"""
ClanSociety — registry of multiple Bands and the inter-band relationship layer.

ClanSociety itself holds no agents directly; all agents live inside their
Band's Society.  ClanSociety manages:
  - Which bands exist (add / remove)
  - Pairwise distances between bands (geographic metaphor)
  - Scheduling of inter-band interaction pairs each year
  - Aggregated trust state (read from individual Band.inter_band_trust)

Models know nothing about engines.  ClanSociety therefore contains no tick
logic — that lives in engines/clan_base.py.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from models.clan.band import Band

_log = logging.getLogger(__name__)


class ClanSociety:
    """Registry of active Bands plus inter-band geography and interaction scheduling.

    Parameters
    ----------
    base_interaction_rate:
        Baseline annual probability that any two bands interact, before
        distance and trust modulation.
    """

    def __init__(self, base_interaction_rate: float = 0.3) -> None:
        self.bands: dict[int, "Band"] = {}

        # Symmetric distance matrix: (min_id, max_id) -> float [0, 1]
        # 0 = adjacent / same territory, 1 = maximum separation.
        # Keys are always stored as (smaller_id, larger_id) for symmetry.
        self.distance_matrix: dict[tuple[int, int], float] = {}

        self.base_interaction_rate: float = base_interaction_rate

        _log.debug("ClanSociety initialised (base_interaction_rate=%.2f)", base_interaction_rate)

    # ── Band registry ────────────────────────────────────────────────────────

    def add_band(self, band: "Band") -> None:
        """Register a Band.  Sets default distance 0.5 to all existing bands."""
        if band.band_id in self.bands:
            _log.warning(
                "add_band: Band %d already registered — ignoring duplicate.", band.band_id
            )
            return
        # Default moderate distance to every existing band
        for existing_id in self.bands:
            key = _dist_key(band.band_id, existing_id)
            self.distance_matrix.setdefault(key, 0.5)
        self.bands[band.band_id] = band
        _log.debug("Band %d ('%s') added to ClanSociety.", band.band_id, band.name)

    def remove_band(self, band_id: int) -> None:
        """Deregister a Band and clean up its distance entries."""
        if band_id not in self.bands:
            _log.warning("remove_band: Band %d not found — ignoring.", band_id)
            return
        del self.bands[band_id]
        # Remove distance entries referencing this band
        keys_to_delete = [k for k in self.distance_matrix if band_id in k]
        for k in keys_to_delete:
            del self.distance_matrix[k]
        _log.debug("Band %d removed from ClanSociety.", band_id)

    # ── Distance helpers ─────────────────────────────────────────────────────

    def set_distance(self, band_id_a: int, band_id_b: int, distance: float) -> None:
        """Set the geographic distance between two bands (float [0, 1])."""
        if band_id_a == band_id_b:
            return
        distance = float(max(0.0, min(1.0, distance)))
        self.distance_matrix[_dist_key(band_id_a, band_id_b)] = distance

    def get_distance(self, band_id_a: int, band_id_b: int) -> float:
        """Return distance between two bands (default 0.5 if not set)."""
        if band_id_a == band_id_b:
            return 0.0
        return self.distance_matrix.get(_dist_key(band_id_a, band_id_b), 0.5)

    # ── Interaction scheduling ────────────────────────────────────────────────

    def schedule_interactions(
        self, year: int, rng: np.random.Generator
    ) -> list[tuple["Band", "Band"]]:
        """Return the list of (band_i, band_j) pairs that will interact this year.

        Interaction probability for a pair (i, j):
            p = base_interaction_rate
              * (1 - distance)          # closer bands meet more often
              * (0.5 + 0.5 * avg_trust) # friendlier bands meet more often

        Each ordered pair is evaluated once (i < j by band_id order).
        Returns a list of unordered Band pairs; order within each tuple is
        (lower_id, higher_id) for determinism.
        """
        band_ids = sorted(self.bands.keys())
        n = len(band_ids)
        pairs: list[tuple["Band", "Band"]] = []

        for i in range(n):
            for j in range(i + 1, n):
                id_a = band_ids[i]
                id_b = band_ids[j]
                band_a = self.bands[id_a]
                band_b = self.bands[id_b]

                distance = self.get_distance(id_a, id_b)
                # Average trust in both directions
                trust_ab = band_a.trust_toward(id_b)
                trust_ba = band_b.trust_toward(id_a)
                avg_trust = (trust_ab + trust_ba) / 2.0

                p = (
                    self.base_interaction_rate
                    * (1.0 - distance)
                    * (0.5 + 0.5 * avg_trust)
                )
                p = float(max(0.0, min(1.0, p)))

                if rng.random() < p:
                    pairs.append((band_a, band_b))
                    _log.debug(
                        "Year %d: interaction scheduled between Band %d and Band %d "
                        "(p=%.3f, dist=%.2f, trust=%.2f)",
                        year, id_a, id_b, p, distance, avg_trust,
                    )

        return pairs

    # ── Aggregate helpers ────────────────────────────────────────────────────

    def total_population(self) -> int:
        """Sum of living agents across all bands."""
        return sum(b.population_size() for b in self.bands.values())

    def living_band_ids(self) -> list[int]:
        """Return IDs of bands that still have at least one living agent."""
        return [bid for bid, b in self.bands.items() if b.population_size() > 0]

    # ── Dunder helpers ───────────────────────────────────────────────────────

    def __repr__(self) -> str:
        band_summary = ", ".join(
            f"Band({bid}, pop={b.population_size()})"
            for bid, b in self.bands.items()
        )
        return f"ClanSociety(bands=[{band_summary}])"


# ── Module-level helper ──────────────────────────────────────────────────────

def _dist_key(a: int, b: int) -> tuple[int, int]:
    """Return canonical (min, max) key for distance_matrix lookup."""
    return (min(a, b), max(a, b))
