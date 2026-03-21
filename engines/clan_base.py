"""
ClanEngine — multi-band tick driver (SIMSIV v2).

Responsibilities per tick:
  1. Run the full v1 12-step simulation tick on every band's Society
     (using the existing engine singletons, each band isolated).
  2. Schedule inter-band interactions via ClanSociety.schedule_interactions().
  3. Classify each scheduled interaction as trade, neutral, or hostile, then
     dispatch to the appropriate inter-band engine:
       - trade   → clan_trade.trade_tick()
       - hostile → clan_raiding.raid_tick()  [Turn 3: Bowles raiding engine]
       - neutral → small trust bump, no exchange
  4. Return a structured result dict with per-band metrics and inter-band events.

Architecture rules obeyed:
  - No print() statements.  Uses logging.getLogger(__name__).
  - All randomness via the seeded rng parameter.
  - Models (Band, ClanSociety) know nothing about this engine.
  - No circular imports: engines import from models and config only.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import numpy as np

from config import Config
from engines.resources import ResourceEngine
from engines.institutions import InstitutionEngine
from engines.mating import MatingEngine
from engines.reproduction import ReproductionEngine
from engines.conflict import ConflictEngine
from engines.mortality import MortalityEngine
from engines.reputation import ReputationEngine
from engines.pathology import PathologyEngine
from engines.clan_trade import trade_tick
from engines.clan_raiding import raid_tick
from engines.clan_selection import selection_tick
from metrics.collectors import MetricsCollector
from metrics.clan_collectors import ClanMetricsCollector

if TYPE_CHECKING:
    from models.clan.clan_society import ClanSociety
    from models.clan.band import Band
    from models.clan.clan_config import ClanConfig

_log = logging.getLogger(__name__)


class ClanEngine:
    """Drives a multi-band ClanSociety forward one year at a time.

    A single set of engine instances is shared across all bands.  Each
    engine is stateless (no mutable instance state used between calls) so
    sharing is safe and avoids N×9 engine object allocations.

    Usage::

        engine = ClanEngine()
        for year in range(1, 101):
            result = engine.tick(clan_society, year, rng, config)
    """

    def __init__(self) -> None:
        # Stateless v1 engines — shared across all bands each tick.
        self._resource_engine = ResourceEngine()
        self._institution_engine = InstitutionEngine()
        self._mating_engine = MatingEngine()
        self._reproduction_engine = ReproductionEngine()
        self._conflict_engine = ConflictEngine()
        self._mortality_engine = MortalityEngine()
        self._reputation_engine = ReputationEngine()
        self._pathology_engine = PathologyEngine()

        # Per-band MetricsCollector (v1 per-band metrics) keyed by band_id
        self._band_metrics: dict[int, MetricsCollector] = {}

        # Clan-level metrics collector (Turn 4: inter-band + divergence metrics)
        self._clan_metrics: ClanMetricsCollector = ClanMetricsCollector()

    # ── Public API ───────────────────────────────────────────────────────────

    def tick(
        self,
        clan_society: "ClanSociety",
        year: int,
        rng: np.random.Generator,
        config: Config,
        clan_config: "ClanConfig | None" = None,
    ) -> dict:
        """Advance all bands by one year.

        Parameters
        ----------
        clan_society:
            The multi-band registry.
        year:
            Current simulation year (caller is responsible for advancing).
        rng:
            Seeded numpy.random.Generator shared across the clan tick.
            Each band call consumes from this generator in band_id order so
            that results are reproducible given the same rng state.
        config:
            Shared configuration applied to all bands.
        clan_config:
            Optional v2 ClanConfig controlling inter-band parameters
            (fission threshold, extinction threshold, migration rate, etc.).
            When None, clan_selection defaults are used.

        Returns
        -------
        dict with:
            year              : int
            band_metrics      : {band_id: metrics_row_dict}
            inter_band_events : list[event_dict]
            selection_events  : list[event_dict]
            clan_metrics      : dict (clan-level snapshot from ClanMetricsCollector)
            total_population  : int
        """
        _log.debug("ClanEngine tick year=%d, bands=%d", year, len(clan_society.bands))

        band_metrics: dict[int, dict] = {}
        all_inter_band_events: list[dict] = []

        # ── Step 1: Tick each band independently ─────────────────────────────
        # Each band is ticked with its own per-band rng (band.rng) so that the
        # internal trajectory of a band is independent of band count and band
        # ordering in the clan.  The shared clan-level rng is reserved for
        # inter-band scheduling and interactions only.
        #
        # Per-band Config: each band uses band.society.config (set at Band
        # construction) for its intra-band dynamics.  This enables institutional
        # differentiation — e.g. Band A runs FREE_COMPETITION while Band B
        # runs STRONG_STATE — which is the core Bowles/Gintis vs North
        # experimental manipulation.
        for band_id in sorted(clan_society.bands.keys()):
            band = clan_society.bands[band_id]
            band_config = band.society.config
            metrics_row = self._tick_band(band, year, band.rng, band_config)
            band_metrics[band_id] = metrics_row

        # ── Step 2: Schedule inter-band interactions ──────────────────────────
        interaction_pairs = clan_society.schedule_interactions(year, rng)

        # ── Step 3: Process each inter-band interaction ────────────────────────
        for band_a, band_b in interaction_pairs:
            events = self._process_interaction(band_a, band_b, year, rng, config,
                                               clan_config)
            all_inter_band_events.extend(events)

        # ── Step 4: Between-group selection (Turn 4) ──────────────────────────
        # Runs after trade/raid so it can observe this tick's fitness outcomes.
        # A dedicated sub-rng is derived from the shared rng (consuming exactly
        # one integer from rng) so that selection_tick's internal randomness does
        # NOT change the shared rng state for subsequent inter-band scheduling.
        # This preserves the RNG contract for existing tests.
        sel_rng = np.random.default_rng(int(rng.integers(0, 2**31)))
        sel_events = selection_tick(clan_society, year, sel_rng, config, clan_config)
        # Extract selection coefficients from the stats event (index 0)
        within_coeff = 0.0
        between_coeff = 0.0
        if sel_events:
            stats = sel_events[0]
            if stats.get("type") == "selection_stats":
                within_coeff = float(stats.get("within_group_selection_coeff", 0.0))
                between_coeff = float(stats.get("between_group_selection_coeff", 0.0))

        # Pass coefficients to clan metrics collector so they appear in the row
        self._clan_metrics.set_selection_coefficients(within_coeff, between_coeff)

        # ── Step 5: Collect clan-level metrics ────────────────────────────────
        clan_metrics_row = self._clan_metrics.collect(
            clan_society, year, all_inter_band_events
        )

        _log.debug(
            "ClanEngine tick year=%d complete: %d inter-band interactions, "
            "%d selection events, total_pop=%d",
            year,
            len(interaction_pairs),
            len(sel_events),
            clan_society.total_population(),
        )

        return {
            "year": year,
            "band_metrics": band_metrics,
            "inter_band_events": all_inter_band_events,
            "selection_events": sel_events,
            "clan_metrics": clan_metrics_row,
            "total_population": clan_society.total_population(),
        }

    # ── Per-band tick (mirrors simulation.Simulation.tick exactly) ───────────

    def _tick_band(
        self,
        band: "Band",
        year: int,
        rng: np.random.Generator,
        config: Config,
    ) -> dict:
        """Run the full 12-step v1 tick on a single band's Society.

        Mirrors the logic in simulation.Simulation.tick so that each band
        evolves identically to a standalone v1 run.

        Returns the metrics row dict for this band this tick.
        """
        society = band.society

        # ── Advance year on the society ──────────────────────────────────────
        society.year = year
        society.tick_events = []

        pop = society.population_size()

        # ── Population safety ────────────────────────────────────────────────
        if pop < config.min_viable_population:
            deficit = config.min_viable_population - pop + 10
            society.inject_migrants(deficit)
            _log.debug(
                "Band %d: population rescue — injected %d migrants at year %d",
                band.band_id,
                deficit,
                year,
            )

        # ── Age all agents ───────────────────────────────────────────────────
        for a in society.get_living():
            a.age += 1

        # ── Steps 1–11: engine execution ─────────────────────────────────────

        # 1. Environment
        env_events = society.environment.tick(society.population_size())
        for e in env_events:
            society.add_event(e)

        # 2. Resources
        res_events = self._resource_engine.run(society, config, rng)
        for e in res_events:
            society.add_event(e)

        # 3. Conflict (before mating — violence has reproductive cost)
        conflict_events = self._conflict_engine.run(society, config, rng)
        for e in conflict_events:
            society.add_event(e)

        # 4. Mating
        mate_events = self._mating_engine.run(society, config, rng)
        for e in mate_events:
            society.add_event(e)

        # 5. Reproduction
        repro_events = self._reproduction_engine.run(society, config, rng)
        for e in repro_events:
            society.add_event(e)

        # 6. Mortality
        mort_events = self._mortality_engine.run(society, config, rng)
        for e in mort_events:
            society.add_event(e)

        # 7. Migration (intra-band — only if enabled in config)
        if config.migration_enabled:
            mig_events = society.process_migration(config, rng)
            for e in mig_events:
                society.add_event(e)

        # 8. Pathology
        path_events = self._pathology_engine.run(society, config, rng)
        for e in path_events:
            society.add_event(e)

        # 9. Institutions
        inst_events = self._institution_engine.run(society, config, rng)
        for e in inst_events:
            society.add_event(e)

        # 10. Reputation
        rep_events = self._reputation_engine.run(society, config, rng)
        for e in rep_events:
            society.add_event(e)

        # 11. Factions + neighborhood refresh (periodic)
        if config.factions_enabled:
            faction_events = society.detect_factions(config, rng)
            for e in faction_events:
                society.add_event(e)

        if config.proximity_tiers_enabled:
            society.refresh_neighborhoods(config, rng)

        # 12. Collect metrics
        metrics_collector = self._get_metrics_collector(band.band_id)
        row = metrics_collector.collect(society, year)

        _log.debug(
            "Band %d tick year=%d: pop=%d",
            band.band_id,
            year,
            society.population_size(),
        )
        return row

    # ── Inter-band interaction stub ──────────────────────────────────────────

    def _process_interaction(
        self,
        band_a: "Band",
        band_b: "Band",
        year: int,
        rng: np.random.Generator,
        config: Config,
        clan_config: "ClanConfig | None" = None,
    ) -> list[dict]:
        """Process one inter-band interaction: contact record + trade session.

        Interaction type is determined first by an interaction-type draw:
          - "trade"   (probability proportional to bilateral trust)
          - "neutral" (bands meet but do not exchange goods)
          - "hostile" (low-tolerance contact; slight trust decrease)

        For "trade" contacts, trade_tick() is called and its events appended.

        Trust updates are modulated by the mean outgroup_tolerance of the
        living adults in each band, so that trait composition affects the
        inter-band relationship trajectory.

        Returns a list of event dicts describing what happened.
        """
        events: list[dict] = []

        # ── Compute mean outgroup_tolerance across each band's adults ─────────
        tol_a = _mean_outgroup_tolerance(band_a)
        tol_b = _mean_outgroup_tolerance(band_b)
        mean_tol = (tol_a + tol_b) / 2.0

        # Bilateral trust (symmetric mean)
        trust = (band_a.trust_toward(band_b.band_id) + band_b.trust_toward(band_a.band_id)) / 2.0

        # ── Interaction-type draw ─────────────────────────────────────────────
        # p_trade     = trust * mean_outgroup_tolerance
        # p_neutral   = mean_outgroup_tolerance * (1 - trust)
        # p_hostile   = 1 - mean_outgroup_tolerance
        # (Probabilities sum to one because: trust*tol + tol*(1-trust) + (1-tol) = 1)
        p_trade = trust * mean_tol
        p_neutral = mean_tol * (1.0 - trust)
        # p_hostile fills the remainder: 1 - p_trade - p_neutral = 1 - mean_tol

        draw = float(rng.random())

        if draw < p_trade:
            interaction_type = "trade"
        elif draw < p_trade + p_neutral:
            interaction_type = "neutral"
        else:
            interaction_type = "hostile"

        _log.debug(
            "Inter-band interaction: Band %d <-> Band %d at year %d "
            "type=%s (trust=%.2f, mean_tol=%.2f)",
            band_a.band_id, band_b.band_id, year,
            interaction_type, trust, mean_tol,
        )

        # ── Dispatch on interaction type ──────────────────────────────────────
        if interaction_type == "trade":
            # Delegate to trade engine; stamp year on returned events.
            trade_events = trade_tick(band_a, band_b, trust, rng, config)
            for ev in trade_events:
                ev["year"] = year
                band_a.society.add_event(ev)
                band_b.society.add_event(ev)
            events.extend(trade_events)

            # Record a summary contact event.
            contact_event: dict = {
                "type": "inter_band_contact",
                "year": year,
                "agent_ids": [],
                "description": (
                    f"Band {band_a.band_id} traded with Band {band_b.band_id} "
                    f"({len(trade_events)} exchange(s))"
                ),
                "outcome": "trade",
                "other_band_id": band_b.band_id,
            }

        elif interaction_type == "neutral":
            # Neutral contact: small trust bump, no exchange.
            # Delta is modulated by outgroup tolerance: tolerant bands gain more.
            trust_delta = float(rng.uniform(0.005, 0.02)) * mean_tol
            band_a.update_trust(band_b.band_id, trust_delta)
            band_b.update_trust(band_a.band_id, trust_delta)

            contact_event = {
                "type": "inter_band_contact",
                "year": year,
                "agent_ids": [],
                "description": (
                    f"Band {band_a.band_id} neutral contact with Band {band_b.band_id} "
                    f"(trust +{trust_delta:.3f})"
                ),
                "outcome": "neutral_contact",
                "other_band_id": band_b.band_id,
            }

        else:  # hostile — attempt a raid (Bowles raiding engine)
            # Determine which band is the attacker (higher scarcity + aggression
            # drives raid motivation; lower mean resources → more likely attacker).
            mean_res_a = _mean_resources(band_a)
            mean_res_b = _mean_resources(band_b)

            if mean_res_a <= mean_res_b:
                # band_a is more resource-stressed — more likely to be the attacker
                att, dfn = band_a, band_b
            else:
                att, dfn = band_b, band_a

            raid_events = raid_tick(att, dfn, trust, rng, clan_config or config)
            for ev in raid_events:
                ev["year"] = year
                band_a.society.add_event(ev)
                band_b.society.add_event(ev)
            events.extend(raid_events)

            # Build a summary contact_event for this hostile interaction.
            if not raid_events:
                # Raid probability check failed — plain hostile contact.
                trust_loss = float(rng.uniform(0.01, 0.04)) * (1.0 - mean_tol)
                band_a.update_trust(band_b.band_id, -trust_loss)
                band_b.update_trust(band_a.band_id, -trust_loss)
                contact_event = {
                    "type": "inter_band_contact",
                    "year": year,
                    "agent_ids": [],
                    "description": (
                        f"Band {band_a.band_id} hostile contact with Band {band_b.band_id} "
                        f"(trust -{trust_loss:.3f}; no raid triggered)"
                    ),
                    "outcome": "hostile_contact",
                    "other_band_id": band_b.band_id,
                }
            else:
                contact_event = {
                    "type": "inter_band_contact",
                    "year": year,
                    "agent_ids": [],
                    "description": (
                        f"Band {att.band_id} raided Band {dfn.band_id} "
                        f"({len(raid_events)} raid event(s))"
                    ),
                    "outcome": "raid",
                    "other_band_id": band_b.band_id,
                }

            # The hostile path adds its own contact_event inline (unlike the
            # trade/neutral paths which fall through to the shared block below).
            band_a.society.add_event(contact_event)
            band_b.society.add_event(contact_event)
            events.append(contact_event)
            return events  # early return for hostile — avoids duplicate add

        # ── Shared finalisation for trade and neutral paths ───────────────────
        band_a.society.add_event(contact_event)
        band_b.society.add_event(contact_event)
        events.append(contact_event)

        return events

    # ── Helpers ──────────────────────────────────────────────────────────────

    def reset(self) -> None:
        """Clear accumulated per-band and clan-level metrics history.

        Call this between independent runs when reusing a ClanEngine instance
        (e.g. in autosim parameter sweeps).  Without this call, get_band_history()
        and get_clan_history() would return rows from previous runs mixed with
        the current run.

        Note: this does NOT reset band Society state — that lives in the Band
        objects themselves and must be reset by recreating the ClanSociety and
        its Bands.
        """
        self._band_metrics.clear()
        self._clan_metrics.reset()
        _log.debug("ClanEngine.reset() called — per-band and clan metrics history cleared.")

    def _get_metrics_collector(self, band_id: int) -> MetricsCollector:
        """Return (creating if needed) the MetricsCollector for a band."""
        if band_id not in self._band_metrics:
            self._band_metrics[band_id] = MetricsCollector()
        return self._band_metrics[band_id]

    def get_band_history(self, band_id: int) -> list[dict]:
        """Return the full per-tick metrics history for a band (list of row dicts)."""
        collector = self._band_metrics.get(band_id)
        if collector is None:
            return []
        return collector.rows

    def get_clan_history(self) -> list[dict]:
        """Return the full per-tick clan-level metrics history.

        Each row is a flat dict from ClanMetricsCollector.collect(), containing
        per-band snapshots, inter-band trust matrix, interaction counts,
        divergence metrics (Fst, centroid distances), and selection coefficients.
        """
        return self._clan_metrics.get_history()


# ── Module-level helper ───────────────────────────────────────────────────────

def _mean_outgroup_tolerance(band: "Band") -> float:
    """Return mean outgroup_tolerance across all living adults in the band.

    Falls back to 0.5 (neutral) if no living agents exist.
    """
    living = band.get_living()
    if not living:
        return 0.5
    return float(sum(a.outgroup_tolerance for a in living) / len(living))


def _mean_resources(band: "Band") -> float:
    """Return mean current_resources across all living agents in the band.

    Falls back to 0.0 if no living agents exist (maximally resource-stressed,
    triggering the highest raid motivation in _process_interaction).
    """
    living = band.get_living()
    if not living:
        return 0.0
    return float(sum(a.current_resources for a in living) / len(living))
