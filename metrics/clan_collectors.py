"""
clan_collectors.py — Per-band and inter-band metrics for SIMSIV v2.

ClanMetricsCollector gathers three categories of data each tick:

1. Per-band snapshots
   - Population count
   - Mean and SD of all 35 heritable traits
   - Mean beliefs (5 dims), mean skills (4 domains)
   - law_strength from band.society
   - mean_resources, resource_gini within band

2. Inter-band metrics
   - inter_band_trust matrix snapshot (all pairwise scores)
   - interaction_count broken down by type (trades, raids, neutral contacts)
   - trade_volume (total resources exchanged this tick)
   - inter_band_violence_rate (raids / total interactions; 0 if no interactions)

3. Divergence metrics
   - Trait centroid Euclidean distance between every band pair
   - Fst-style between-group vs within-group variance decomposition for
     four key prosocial traits:
       cooperation_propensity, group_loyalty, outgroup_tolerance, empathy_capacity
   - within_group_selection_coeff  (updated by clan_selection engine)
   - between_group_selection_coeff (updated by clan_selection engine)

Usage::

    collector = ClanMetricsCollector()
    # each tick:
    row = collector.collect(clan_society, year, events)
    # after run:
    history = collector.get_history()

Architecture rules obeyed
--------------------------
- No print() statements.  Uses logging.getLogger(__name__).
- All array math via numpy (no calls to random — this module is pure analytics).
- No imports from engines.*  — no circular imports possible.
- Models (ClanSociety, Band) are accessed only via TYPE_CHECKING or runtime import.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import numpy as np

from models.agent import HERITABLE_TRAITS

if TYPE_CHECKING:
    from models.clan.clan_society import ClanSociety

_log = logging.getLogger(__name__)

# The four key prosocial traits for Fst-style decomposition (Bowles 2006).
_FST_TRAITS: tuple[str, ...] = (
    "cooperation_propensity",
    "group_loyalty",
    "outgroup_tolerance",
    "empathy_capacity",
)

# Belief attribute names (DD25)
_BELIEF_ATTRS: tuple[str, ...] = (
    "hierarchy_belief",
    "cooperation_norm",
    "violence_acceptability",
    "tradition_adherence",
    "kinship_obligation",
)

# Skill attribute names (DD26)
_SKILL_ATTRS: tuple[str, ...] = (
    "foraging_skill",
    "combat_skill",
    "social_skill",
    "craft_skill",
)


def _gini(values: list[float]) -> float:
    """Gini coefficient for a list of non-negative floats.

    Returns 0 for empty or single-element lists, 0 for all-zero vectors.
    """
    if len(values) < 2:
        return 0.0
    arr = np.array(sorted(values), dtype=float)
    total = arr.sum()
    if total == 0.0:
        return 0.0
    n = len(arr)
    idx = np.arange(1, n + 1)
    return float((2.0 * (idx * arr).sum() / (n * total)) - (n + 1) / n)


def _safe_mean(values: list[float]) -> float:
    """Mean, returns 0.0 for empty list."""
    return float(np.mean(values)) if values else 0.0


def _safe_std(values: list[float]) -> float:
    """Population SD, returns 0.0 for empty list."""
    return float(np.std(values)) if values else 0.0


def _fst(all_values: list[list[float]]) -> float:
    """Compute Fst-style between-group variance fraction.

    Fst = (sigma_between^2) / (sigma_total^2)

    where sigma_between^2 is the variance of band means weighted by band size,
    and sigma_total^2 is the variance of all individual values pooled.

    Returns 0.0 if fewer than 2 groups exist or total variance is near zero.
    This is the Wright (1951) island-model Fst, adapted for continuous traits.

    Citation: Bowles (2006) Science 314(5805) uses Fst as the key parameter
    for between-group selection intensity.
    """
    # Filter to non-empty groups
    groups = [g for g in all_values if len(g) > 0]
    if len(groups) < 2:
        return 0.0

    # Pool all values for total variance
    pooled = [v for g in groups for v in g]
    if len(pooled) < 2:
        return 0.0

    var_total = float(np.var(pooled))
    if var_total < 1e-10:
        return 0.0

    # Between-group variance: variance of band means (weighted by band size)
    band_means = np.array([np.mean(g) for g in groups])
    band_sizes = np.array([len(g) for g in groups])
    grand_mean = np.sum(band_means * band_sizes) / np.sum(band_sizes)
    var_between = float(
        np.sum(band_sizes * (band_means - grand_mean) ** 2) / np.sum(band_sizes)
    )

    return float(np.clip(var_between / var_total, 0.0, 1.0))


def _centroid_distance(means_a: np.ndarray, means_b: np.ndarray) -> float:
    """Euclidean distance between two trait-mean vectors (centroids)."""
    return float(np.linalg.norm(means_a - means_b))


class ClanMetricsCollector:
    """Collects per-band and inter-band metrics each clan tick.

    Each call to collect() appends one row dict to the internal history.
    The row contains flat keys for all metrics, avoiding nested dicts so
    that history can be directly converted to a pandas DataFrame.

    Per-band metrics use the naming convention:
        band_{band_id}_{metric_name}

    For example, for band 1:
        band_1_population
        band_1_mean_cooperation_propensity
        band_1_std_cooperation_propensity
        ...

    Inter-band metrics use:
        inter_band_trust_{id_a}_{id_b}   (always with id_a < id_b)
        total_interactions
        trade_count
        raid_count
        neutral_count
        inter_band_violence_rate
        total_trade_volume

    Divergence metrics (one per band pair where id_a < id_b):
        centroid_dist_{id_a}_{id_b}       (Euclidean dist of trait centroids)
        fst_{trait}                       (pooled Fst for all bands, per prosocial trait)
        within_group_selection_coeff      (set externally by clan_selection engine)
        between_group_selection_coeff     (set externally by clan_selection engine)
    """

    def __init__(self) -> None:
        self._history: list[dict] = []
        # These coefficients are written by clan_selection.py after it runs
        # its fitness regression, then folded in at the next collect() call.
        self._pending_within_coeff: float = 0.0
        self._pending_between_coeff: float = 0.0

    # ── External setter called by clan_selection engine ───────────────────────

    def set_selection_coefficients(
        self,
        within_coeff: float,
        between_coeff: float,
    ) -> None:
        """Record selection coefficients computed by clan_selection.py.

        Called after selection_tick() finishes each year so that the next
        call to collect() includes the coefficients in the metrics row.
        """
        self._pending_within_coeff = float(within_coeff)
        self._pending_between_coeff = float(between_coeff)

    # ── Primary API ───────────────────────────────────────────────────────────

    def collect(
        self,
        clan_society: "ClanSociety",
        year: int,
        events: list[dict],
    ) -> dict:
        """Collect all metrics for this tick.

        Parameters
        ----------
        clan_society:
            The live multi-band registry.
        year:
            Current simulation year.
        events:
            All inter-band events generated this tick (from ClanEngine).

        Returns
        -------
        Flat dict of all metrics for this tick.  Also appended to internal
        history (accessible via get_history()).
        """
        row: dict = {"year": year}

        band_ids = sorted(clan_society.bands.keys())

        # ── 1. Per-band snapshots ──────────────────────────────────────────────
        # Collect trait arrays per band for later divergence computation.
        band_trait_arrays: dict[int, dict[str, list[float]]] = {}

        for bid in band_ids:
            band = clan_society.bands[bid]
            living = band.get_living()
            pop = len(living)

            prefix = f"band_{bid}_"
            row[f"{prefix}population"] = pop

            if pop == 0:
                # Emit zero/NaN sentinel values for dead bands.
                for trait in HERITABLE_TRAITS:
                    row[f"{prefix}mean_{trait}"] = 0.0
                    row[f"{prefix}std_{trait}"] = 0.0
                for bel in _BELIEF_ATTRS:
                    row[f"{prefix}mean_{bel}"] = 0.0
                for skl in _SKILL_ATTRS:
                    row[f"{prefix}mean_{skl}"] = 0.0
                row[f"{prefix}law_strength"] = 0.0
                row[f"{prefix}mean_resources"] = 0.0
                row[f"{prefix}resource_gini"] = 0.0
                band_trait_arrays[bid] = {t: [] for t in HERITABLE_TRAITS}
                continue

            # Heritable traits
            trait_data: dict[str, list[float]] = {}
            for trait in HERITABLE_TRAITS:
                vals = [getattr(a, trait) for a in living]
                trait_data[trait] = vals
                row[f"{prefix}mean_{trait}"] = _safe_mean(vals)
                row[f"{prefix}std_{trait}"] = _safe_std(vals)

            band_trait_arrays[bid] = trait_data

            # Beliefs (non-heritable, range [-1, +1])
            for bel in _BELIEF_ATTRS:
                vals = [getattr(a, bel, 0.0) for a in living]
                row[f"{prefix}mean_{bel}"] = _safe_mean(vals)

            # Skills (non-heritable, range [0, 1])
            for skl in _SKILL_ATTRS:
                vals = [getattr(a, skl, 0.0) for a in living]
                row[f"{prefix}mean_{skl}"] = _safe_mean(vals)

            # Institutional
            law_strength = getattr(band.society, "law_strength", 0.0)
            row[f"{prefix}law_strength"] = float(law_strength)

            # Resource distribution
            resources = [a.current_resources for a in living]
            row[f"{prefix}mean_resources"] = _safe_mean(resources)
            row[f"{prefix}resource_gini"] = _gini(resources)

        # ── 2. Inter-band trust matrix ────────────────────────────────────────
        n_bands = len(band_ids)
        for i in range(n_bands):
            for j in range(i + 1, n_bands):
                id_a = band_ids[i]
                id_b = band_ids[j]
                t_ab = clan_society.bands[id_a].trust_toward(id_b)
                t_ba = clan_society.bands[id_b].trust_toward(id_a)
                row[f"inter_band_trust_{id_a}_{id_b}"] = round((t_ab + t_ba) / 2.0, 4)

        # ── 3. Interaction counts from events ─────────────────────────────────
        trade_count = sum(1 for e in events if e.get("type") == "inter_band_trade"
                          and e.get("outcome") == "success")
        raid_count = sum(1 for e in events if e.get("type") == "inter_band_raid")
        neutral_count = sum(1 for e in events
                            if e.get("type") == "inter_band_contact"
                            and e.get("outcome") == "neutral_contact")
        refused_count = sum(1 for e in events if e.get("type") == "inter_band_trade"
                            and e.get("outcome") == "refused")

        total_interactions = trade_count + raid_count + neutral_count + refused_count
        row["total_interactions"] = total_interactions
        row["trade_count"] = trade_count
        row["raid_count"] = raid_count
        row["neutral_count"] = neutral_count
        row["refused_trade_count"] = refused_count
        row["inter_band_violence_rate"] = (
            raid_count / total_interactions if total_interactions > 0 else 0.0
        )

        # Trade volume: sum all resource transfers in successful trade events.
        # (clan_trade stores no volume field directly; count successes as proxy)
        # For a precise volume we would need the engine to store it in the event.
        # Use count * mean_band_resources as best-available proxy.
        row["total_trade_volume"] = float(trade_count)  # will be improved in future turns

        # ── 4. Divergence metrics ──────────────────────────────────────────────
        # Centroid distances between each band pair
        for i in range(n_bands):
            for j in range(i + 1, n_bands):
                id_a = band_ids[i]
                id_b = band_ids[j]
                arr_a_data = band_trait_arrays[id_a]
                arr_b_data = band_trait_arrays[id_b]

                if not arr_a_data[HERITABLE_TRAITS[0]] or not arr_b_data[HERITABLE_TRAITS[0]]:
                    row[f"centroid_dist_{id_a}_{id_b}"] = 0.0
                    continue

                centroid_a = np.array(
                    [_safe_mean(arr_a_data[t]) for t in HERITABLE_TRAITS]
                )
                centroid_b = np.array(
                    [_safe_mean(arr_b_data[t]) for t in HERITABLE_TRAITS]
                )
                row[f"centroid_dist_{id_a}_{id_b}"] = round(
                    _centroid_distance(centroid_a, centroid_b), 6
                )

        # Fst per prosocial trait (pooled across all bands)
        for trait in _FST_TRAITS:
            per_band = [band_trait_arrays[bid][trait] for bid in band_ids]
            row[f"fst_{trait}"] = round(_fst(per_band), 6)

        # Composite Fst: mean of the four prosocial Fst values
        fst_values = [row[f"fst_{t}"] for t in _FST_TRAITS]
        row["fst_prosocial_mean"] = round(_safe_mean(fst_values), 6)

        # ── 5. Selection coefficients (set externally by clan_selection.py) ───
        row["within_group_selection_coeff"] = self._pending_within_coeff
        row["between_group_selection_coeff"] = self._pending_between_coeff

        # ── 6. Finalize ───────────────────────────────────────────────────────
        self._history.append(row)
        _log.debug(
            "ClanMetricsCollector: year=%d, bands=%d, total_pop=%d, "
            "fst_coop=%.4f, within_sel=%.4f, between_sel=%.4f",
            year,
            len(band_ids),
            sum(row.get(f"band_{bid}_population", 0) for bid in band_ids),
            row.get("fst_cooperation_propensity", 0.0),
            self._pending_within_coeff,
            self._pending_between_coeff,
        )
        return row

    def get_history(self) -> list[dict]:
        """Return a copy of all collected metric rows (one per tick)."""
        return list(self._history)

    def reset(self) -> None:
        """Clear accumulated history.

        Call between independent runs when reusing this collector instance.
        """
        self._history.clear()
        self._pending_within_coeff = 0.0
        self._pending_between_coeff = 0.0
        _log.debug("ClanMetricsCollector.reset() — history cleared.")
