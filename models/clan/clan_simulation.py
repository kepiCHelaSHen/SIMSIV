"""
ClanSimulation — high-level wrapper for multi-band v2 experiments.

Orchestrates ClanEngine, ClanSociety, and Band objects into a complete
simulation run.  Supports per-band Config objects for institutional
differentiation (the core Bowles/Gintis vs North experimental manipulation).

Usage::

    from models.clan.clan_simulation import ClanSimulation
    from config import Config

    sim = ClanSimulation(
        seed=42,
        n_years=200,
        band_setups=[
            ("Free", Config(law_strength=0.0, property_rights_strength=0.0)),
            ("State", Config(law_strength=0.8, property_rights_strength=0.8)),
        ],
    )
    history = sim.run()
    df = sim.to_dataframe()
    df.to_csv("experiment_results.csv", index=False)

Architecture rules obeyed
--------------------------
- No print() statements.  Uses logging.getLogger(__name__).
- All randomness via seeded numpy.random.Generator.
- Models know nothing about engines — ClanSimulation lives in models/clan/
  but imports engines at method-call time only.
- No circular imports.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import numpy as np

from config import Config
from models.clan.band import Band
from models.clan.clan_config import ClanConfig
from models.clan.clan_society import ClanSociety

if TYPE_CHECKING:
    import pandas as pd

_log = logging.getLogger(__name__)


class ClanSimulation:
    """Run a complete multi-band clan experiment.

    Parameters
    ----------
    seed:
        Random seed for full reproducibility.
    n_years:
        Number of annual ticks to simulate.
    band_setups:
        List of (name, Config) tuples — one per band.  Each band gets its
        own Config object, enabling per-band institutional differentiation.
        If None, creates ``n_bands`` bands with the default Config.
    n_bands:
        Number of bands when ``band_setups`` is None.  Ignored when
        ``band_setups`` is provided.
    population_per_band:
        Initial population per band (overrides Config.population_size for
        band construction).
    clan_config:
        ClanConfig controlling inter-band parameters (fission threshold,
        raid parameters, etc.).  None uses defaults.
    base_interaction_rate:
        Baseline annual probability of any two bands interacting.
    distances:
        Optional dict mapping (band_name_a, band_name_b) to float distance.
        Names must match those in band_setups.  Unspecified pairs default to 0.5.
    """

    def __init__(
        self,
        seed: int = 42,
        n_years: int = 200,
        band_setups: list[tuple[str, Config]] | None = None,
        n_bands: int = 3,
        population_per_band: int = 50,
        clan_config: ClanConfig | None = None,
        base_interaction_rate: float = 0.3,
        distances: dict[tuple[str, str], float] | None = None,
    ) -> None:
        self.seed = seed
        self.n_years = n_years
        self.clan_config = clan_config or ClanConfig()
        self._history: list[dict] = []
        self._ran = False

        # Master rng — used only for deriving per-band rngs and the shared
        # clan-level rng.  Never passed directly to any engine.
        master_rng = np.random.default_rng(seed)

        # Shared clan-level rng for inter-band scheduling and interactions.
        self._rng = np.random.default_rng(int(master_rng.integers(0, 2**31)))

        from dataclasses import replace as dc_replace

        # Build band setups if not provided
        if band_setups is None:
            default_config = Config()
            band_setups = [
                (f"Band_{i+1}", dc_replace(default_config))
                for i in range(n_bands)
            ]

        # Create ClanSociety
        self.clan_society = ClanSociety(base_interaction_rate=base_interaction_rate)

        # Create bands — each with its own Config and per-band rng.
        # We use dataclasses.replace to avoid mutating caller-provided Configs.
        self._band_name_to_id: dict[str, int] = {}
        for band_id, (name, band_config) in enumerate(band_setups, start=1):
            band_config = dc_replace(band_config, population_size=population_per_band)
            band_rng = np.random.default_rng(int(master_rng.integers(0, 2**31)))
            band = Band(
                band_id=band_id,
                name=name,
                config=band_config,
                rng=band_rng,
                origin_year=0,
            )
            self.clan_society.add_band(band)
            self._band_name_to_id[name] = band_id

        # Apply custom distances if provided
        if distances:
            for (name_a, name_b), dist in distances.items():
                id_a = self._band_name_to_id[name_a]
                id_b = self._band_name_to_id[name_b]
                self.clan_society.set_distance(id_a, id_b, dist)

        _log.info(
            "ClanSimulation created: seed=%d, n_years=%d, %d bands, pop/band=%d",
            seed, n_years, len(band_setups), population_per_band,
        )

    def run(self) -> list[dict]:
        """Run the full simulation and return tick-level history.

        Returns a list of result dicts (one per year), each containing:
        year, band_metrics, inter_band_events, selection_events,
        clan_metrics, total_population.

        ClanEngine is imported here (not at module level) to avoid a
        circular import: models/clan/ must not import from engines/ at
        module load time.
        """
        if self._ran:
            raise RuntimeError(
                "ClanSimulation.run() has already been called. Create a new "
                "ClanSimulation instance for a fresh run (re-running advances "
                "the rng state and produces different results)."
            )

        # Deferred import — engines import from models.clan via TYPE_CHECKING,
        # so models.clan must not import engines at module level.
        from engines.clan_base import ClanEngine

        engine = ClanEngine()
        self._history = []

        # A default Config() is used for inter-band operations (the `config`
        # param passed to ClanEngine.tick).  This is intentional: inter-band
        # engines (clan_trade, clan_raiding) read raid/trade parameters from
        # ClanConfig, not from Config.  The per-band institutional params
        # (law_strength, property_rights_strength) drive intra-band dynamics
        # via band.society.config in _tick_band, not inter-band dispatch.
        default_config = Config()

        for year in range(1, self.n_years + 1):
            result = engine.tick(
                self.clan_society,
                year,
                self._rng,
                default_config,
                self.clan_config,
            )
            self._history.append(result)

            if year % 50 == 0:
                _log.info(
                    "Year %d/%d: total_pop=%d, bands=%d",
                    year, self.n_years,
                    result["total_population"],
                    len(self.clan_society.bands),
                )

        self._ran = True
        _log.info(
            "ClanSimulation complete: %d years, final_pop=%d",
            self.n_years,
            self.clan_society.total_population(),
        )

        return self._history

    def get_clan_history(self) -> list[dict]:
        """Return the clan-level metrics rows (one per year).

        Each row is the flat dict from ClanMetricsCollector.collect().
        """
        return [h["clan_metrics"] for h in self._history]

    def to_dataframe(self) -> "pd.DataFrame":
        """Convert clan-level history to a pandas DataFrame.

        Columns include: year, total_population, inter_band_violence_rate,
        trade_volume, within_group_selection_coeff, between_group_selection_coeff,
        Fst per prosocial trait, and per-band population/cooperation/aggression.

        Raises ImportError if pandas is not installed.
        """
        import pandas as pd

        if not self._history:
            return pd.DataFrame()

        rows = []
        for h in self._history:
            clan = h["clan_metrics"]
            row = {
                "year": h["year"],
                "total_population": h["total_population"],
            }
            # Flatten clan metrics into the row
            for key, val in clan.items():
                if isinstance(val, (int, float, np.integer, np.floating)):
                    row[key] = float(val)

            # Per-band trait snapshots from clan_metrics (emitted by
            # ClanMetricsCollector as band_{bid}_{metric} keys).
            # These are already in clan dict — they get flattened above.
            # Additionally, extract per-band law_strength from the band's
            # Config so institutional regime is tracked in the time series.
            for bid in sorted(h["band_metrics"].keys()):
                band = self.clan_society.bands.get(bid)
                if band is not None:
                    row[f"band_{bid}_law_strength"] = float(
                        band.society.config.law_strength
                    )

            rows.append(row)

        return pd.DataFrame(rows)

    def to_csv(self, path: str) -> None:
        """Export clan-level history to CSV."""
        df = self.to_dataframe()
        df.to_csv(path, index=False)
        _log.info("Exported %d rows to %s", len(df), path)

    @property
    def band_names(self) -> list[str]:
        """Return the names of all bands in creation order."""
        return list(self._band_name_to_id.keys())

    @property
    def band_ids(self) -> list[int]:
        """Return the IDs of all bands in creation order."""
        return list(self._band_name_to_id.values())

    def get_band_config(self, band_name: str) -> Config:
        """Return the Config object for a named band."""
        bid = self._band_name_to_id[band_name]
        return self.clan_society.bands[bid].society.config

    def __repr__(self) -> str:
        status = "ran" if self._ran else "not run"
        return (
            f"ClanSimulation(seed={self.seed}, n_years={self.n_years}, "
            f"bands={len(self.clan_society.bands)}, {status})"
        )
