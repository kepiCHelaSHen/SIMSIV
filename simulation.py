"""
Core simulation loop — pure library, no IO.
"""

from __future__ import annotations
import logging
import numpy as np

_log = logging.getLogger(__name__)

from config import Config
from models.society import Society
from engines.resources import ResourceEngine
from engines.institutions import InstitutionEngine
from engines.mating import MatingEngine
from engines.reproduction import ReproductionEngine
from engines.conflict import ConflictEngine
from engines.mortality import MortalityEngine
from engines.reputation import ReputationEngine
from engines.pathology import PathologyEngine
from metrics.collectors import MetricsCollector


class Simulation:
    def __init__(self, config: Config):
        self.config = config
        self.rng = np.random.default_rng(config.seed)
        self.society = Society(config, self.rng)
        self.metrics = MetricsCollector()

        # Engines
        self.resource_engine = ResourceEngine()
        self.institution_engine = InstitutionEngine()
        self.mating_engine = MatingEngine()
        self.reproduction_engine = ReproductionEngine()
        self.conflict_engine = ConflictEngine()
        self.mortality_engine = MortalityEngine()
        self.reputation_engine = ReputationEngine()
        self.pathology_engine = PathologyEngine()

        self.year = 0
        self.finished = False

    def tick(self) -> dict:
        """Advance one year. Returns metrics dict for this tick."""
        self.year += 1
        self.society.year = self.year
        self.society.tick_events = []  # reset per-tick events

        pop = self.society.population_size()

        # ── Population safety ────────────────────────────────────────
        if pop < self.config.min_viable_population:
            deficit = self.config.min_viable_population - pop + 10
            self.society.inject_migrants(deficit)

        # ── Engine execution order (steps 1-12) ─────────────────────
        # Conflict runs BEFORE mating/reproduction so that violence
        # has real fitness costs — dead agents can't reproduce.

        # 1. Environment
        env_events = self.society.environment.tick(self.society.population_size())
        for e in env_events:
            self.society.add_event(e)

        # 2. Resources
        res_events = self.resource_engine.run(self.society, self.config, self.rng)
        for e in res_events:
            self.society.add_event(e)

        # 3. Conflict (before mating — violence has reproductive cost)
        conflict_events = self.conflict_engine.run(self.society, self.config, self.rng)
        for e in conflict_events:
            self.society.add_event(e)

        # 4. Mating
        mate_events = self.mating_engine.run(self.society, self.config, self.rng)
        for e in mate_events:
            self.society.add_event(e)

        # 5. Reproduction
        repro_events = self.reproduction_engine.run(self.society, self.config, self.rng)
        for e in repro_events:
            self.society.add_event(e)

        # 6. Aging and mortality
        mort_events = self.mortality_engine.run(self.society, self.config, self.rng)
        for e in mort_events:
            self.society.add_event(e)

        # 7. Migration (after mortality — emigration/immigration)
        if self.config.migration_enabled:
            mig_events = self.society.process_migration(self.config, self.rng)
            for e in mig_events:
                self.society.add_event(e)

        # 8. Pathology (condition activation, trauma — after mortality)
        path_events = self.pathology_engine.run(self.society, self.config, self.rng)
        for e in path_events:
            self.society.add_event(e)

        # 9. Institutions (after mortality — inheritance sees ALL deaths)
        inst_events = self.institution_engine.run(self.society, self.config, self.rng)
        for e in inst_events:
            self.society.add_event(e)

        # 10. Reputation (gossip, trust decay, beliefs, skills — after all interactions)
        rep_events = self.reputation_engine.run(self.society, self.config, self.rng)
        for e in rep_events:
            self.society.add_event(e)

        # 11. Faction detection and neighborhood refresh (periodic — after trust updates)
        if self.config.factions_enabled:
            faction_events = self.society.detect_factions(self.config, self.rng)
            for e in faction_events:
                self.society.add_event(e)

        if self.config.proximity_tiers_enabled:
            self.society.refresh_neighborhoods(self.config, self.rng)

        # 12. Collect metrics
        row = self.metrics.collect(self.society, self.year)

        # Equilibrium check
        if not self.society.equilibrium_flagged:
            if self.metrics.check_equilibrium(self.config):
                self.society.equilibrium_flagged = True
                self.society.equilibrium_year = self.year
                row["equilibrium"] = True

        # Check if simulation is done
        if self.year >= self.config.years:
            self.finished = True
        if self.society.population_size() == 0:
            self.finished = True

        return row

    def run(self, callback=None) -> MetricsCollector:
        """Run full simulation. Optional callback(year, metrics_row) for progress."""
        while not self.finished:
            row = self.tick()
            if callback:
                callback(self.year, row)
        return self.metrics
