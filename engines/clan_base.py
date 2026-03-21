"""
ClanEngine — multi-band tick driver (SIMSIV v2).

Responsibilities per tick:
  1. Run the full v1 12-step simulation tick on every band's Society
     (using the existing engine singletons, each band isolated).
  2. Schedule inter-band interactions via ClanSociety.schedule_interactions().
  3. Apply stub inter-band events (trade, conflict, migration stubs).
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
from metrics.collectors import MetricsCollector

if TYPE_CHECKING:
    from models.clan.clan_society import ClanSociety
    from models.clan.band import Band

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

        # Per-band MetricsCollector keyed by band_id
        self._band_metrics: dict[int, MetricsCollector] = {}

    # ── Public API ───────────────────────────────────────────────────────────

    def tick(
        self,
        clan_society: "ClanSociety",
        year: int,
        rng: np.random.Generator,
        config: Config,
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

        Returns
        -------
        dict with:
            year            : int
            band_metrics    : {band_id: metrics_row_dict}
            inter_band_events: list[event_dict]
            total_population: int
        """
        _log.debug("ClanEngine tick year=%d, bands=%d", year, len(clan_society.bands))

        band_metrics: dict[int, dict] = {}
        all_inter_band_events: list[dict] = []

        # ── Step 1: Tick each band independently ─────────────────────────────
        for band_id in sorted(clan_society.bands.keys()):
            band = clan_society.bands[band_id]
            metrics_row = self._tick_band(band, year, rng, config)
            band_metrics[band_id] = metrics_row

        # ── Step 2: Schedule inter-band interactions ──────────────────────────
        interaction_pairs = clan_society.schedule_interactions(year, rng)

        # ── Step 3: Process each inter-band interaction (stub) ─────────────────
        for band_a, band_b in interaction_pairs:
            events = self._process_interaction(band_a, band_b, year, rng, config)
            all_inter_band_events.extend(events)

        _log.debug(
            "ClanEngine tick year=%d complete: %d inter-band interactions, "
            "total_pop=%d",
            year,
            len(interaction_pairs),
            clan_society.total_population(),
        )

        return {
            "year": year,
            "band_metrics": band_metrics,
            "inter_band_events": all_inter_band_events,
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
    ) -> list[dict]:
        """Stub: record inter-band contact and nudge trust.

        Full inter-band mechanics (trade, marriage exchange, raiding,
        gene flow) are planned for subsequent turns.  For now:
          - Record an inter_band_contact event on both societies.
          - Slightly increase mutual trust (positive-contact default).

        Returns a list of event dicts describing what happened.
        """
        events: list[dict] = []

        # Small trust bump from peaceful contact
        trust_delta = float(rng.uniform(0.01, 0.05))
        band_a.update_trust(band_b.band_id, trust_delta)
        band_b.update_trust(band_a.band_id, trust_delta)

        contact_event_a: dict = {
            "type": "inter_band_contact",
            "year": year,
            "agent_ids": [],
            "description": (
                f"Band {band_a.band_id} contacted Band {band_b.band_id} "
                f"(trust delta +{trust_delta:.3f})"
            ),
            "outcome": "peaceful_contact",
            "other_band_id": band_b.band_id,
        }
        contact_event_b: dict = {
            "type": "inter_band_contact",
            "year": year,
            "agent_ids": [],
            "description": (
                f"Band {band_b.band_id} contacted Band {band_a.band_id} "
                f"(trust delta +{trust_delta:.3f})"
            ),
            "outcome": "peaceful_contact",
            "other_band_id": band_a.band_id,
        }

        band_a.society.add_event(contact_event_a)
        band_b.society.add_event(contact_event_b)

        events.append(contact_event_a)

        _log.debug(
            "Inter-band contact: Band %d <-> Band %d at year %d (trust delta=%.3f)",
            band_a.band_id,
            band_b.band_id,
            year,
            trust_delta,
        )
        return events

    # ── Helpers ──────────────────────────────────────────────────────────────

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
