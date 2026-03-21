"""
Tests for ClanSimulation — the v2 multi-band experiment wrapper (Turn 6).

Tests verify:
  - Construction with default and custom band setups
  - Per-band Config isolation (different law_strength values)
  - Simulation runs without crash for short durations
  - Deterministic output with same seed
  - DataFrame export produces valid structure
  - CSV export writes file
  - Band naming and ID mapping
  - Custom distances applied correctly
  - ClanConfig forwarded to engine
  - FREE_COMPETITION vs STRONG_STATE differentiation produces divergent trajectories
"""

import os
import tempfile

import numpy as np
import pytest

from config import Config
from models.clan.clan_config import ClanConfig
from models.clan.clan_simulation import ClanSimulation


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def free_config():
    """FREE_COMPETITION: minimal institutional enforcement."""
    return Config(
        law_strength=0.0,
        property_rights_strength=0.0,
        emergent_institutions_enabled=True,
    )


@pytest.fixture
def state_config():
    """STRONG_STATE: high institutional enforcement."""
    return Config(
        law_strength=0.8,
        property_rights_strength=0.8,
        emergent_institutions_enabled=False,
    )


@pytest.fixture
def two_band_sim(free_config, state_config):
    """ClanSimulation with two bands: FREE vs STATE."""
    return ClanSimulation(
        seed=42,
        n_years=10,
        band_setups=[
            ("Free", free_config),
            ("State", state_config),
        ],
        population_per_band=30,
    )


# ── Construction tests ────────────────────────────────────────────────────────

class TestConstruction:

    def test_default_construction(self):
        """Default constructor creates n_bands bands with default Config."""
        sim = ClanSimulation(seed=42, n_years=5, n_bands=3, population_per_band=20)
        assert len(sim.clan_society.bands) == 3
        assert sim.n_years == 5
        assert sim.seed == 42

    def test_custom_band_setups(self, two_band_sim):
        """Custom band_setups creates named bands."""
        assert len(two_band_sim.clan_society.bands) == 2
        assert "Free" in two_band_sim.band_names
        assert "State" in two_band_sim.band_names

    def test_band_ids_sequential(self, two_band_sim):
        """Band IDs are sequential starting from 1."""
        assert two_band_sim.band_ids == [1, 2]

    def test_per_band_config_isolation(self, two_band_sim):
        """Each band has its own Config with different law_strength."""
        free_cfg = two_band_sim.get_band_config("Free")
        state_cfg = two_band_sim.get_band_config("State")
        assert free_cfg.law_strength == 0.0
        assert state_cfg.law_strength == 0.8
        assert free_cfg is not state_cfg

    def test_population_override(self, two_band_sim):
        """population_per_band overrides Config.population_size for each band."""
        for bid in two_band_sim.band_ids:
            band = two_band_sim.clan_society.bands[bid]
            assert band.society.config.population_size == 30

    def test_custom_distances(self, free_config):
        """Custom distances are applied between named bands."""
        cfg2 = Config()
        sim = ClanSimulation(
            seed=1,
            n_years=1,
            band_setups=[("A", free_config), ("B", cfg2)],
            population_per_band=20,
            distances={("A", "B"): 0.1},
        )
        id_a = sim._band_name_to_id["A"]
        id_b = sim._band_name_to_id["B"]
        assert sim.clan_society.get_distance(id_a, id_b) == pytest.approx(0.1)

    def test_repr(self, two_band_sim):
        """repr shows seed, n_years, band count, and status."""
        r = repr(two_band_sim)
        assert "seed=42" in r
        assert "not run" in r


# ── Run tests ─────────────────────────────────────────────────────────────────

class TestRun:

    def test_run_completes(self, two_band_sim):
        """run() completes without exception."""
        history = two_band_sim.run()
        assert len(history) == 10

    def test_run_returns_yearly_results(self, two_band_sim):
        """Each history entry has the expected keys."""
        history = two_band_sim.run()
        for h in history:
            assert "year" in h
            assert "band_metrics" in h
            assert "clan_metrics" in h
            assert "total_population" in h
            assert h["total_population"] > 0

    def test_year_sequence(self, two_band_sim):
        """Years in history are sequential 1..n_years."""
        history = two_band_sim.run()
        years = [h["year"] for h in history]
        assert years == list(range(1, 11))

    def test_both_bands_survive(self, two_band_sim):
        """Both bands have living agents after 10 ticks."""
        two_band_sim.run()
        for bid in two_band_sim.band_ids:
            band = two_band_sim.clan_society.bands[bid]
            assert band.population_size() > 0

    def test_deterministic_same_seed(self, free_config, state_config):
        """Same seed produces identical total_population trajectory."""
        def run_sim():
            sim = ClanSimulation(
                seed=137,
                n_years=5,
                band_setups=[
                    ("Free", Config(law_strength=0.0)),
                    ("State", Config(law_strength=0.8)),
                ],
                population_per_band=25,
            )
            history = sim.run()
            return [h["total_population"] for h in history]

        run1 = run_sim()
        run2 = run_sim()
        assert run1 == run2

    def test_different_seeds_diverge(self):
        """Different seeds produce different trajectories."""
        pops = []
        for seed in [42, 137]:
            sim = ClanSimulation(
                seed=seed, n_years=10, n_bands=2, population_per_band=30
            )
            history = sim.run()
            pops.append([h["total_population"] for h in history])
        # At least one year should differ
        assert pops[0] != pops[1]

    def test_clan_config_forwarded(self):
        """ClanConfig parameters are used by the engine."""
        clan_cfg = ClanConfig(fission_threshold=9999)
        sim = ClanSimulation(
            seed=42,
            n_years=5,
            n_bands=2,
            population_per_band=30,
            clan_config=clan_cfg,
        )
        # Should run without fission (threshold too high)
        history = sim.run()
        assert len(history) == 5


# ── DataFrame / CSV export tests ──────────────────────────────────────────────

class TestExport:

    def test_to_dataframe_shape(self, two_band_sim):
        """DataFrame has one row per year."""
        two_band_sim.run()
        df = two_band_sim.to_dataframe()
        assert len(df) == 10
        assert "year" in df.columns
        assert "total_population" in df.columns

    def test_to_dataframe_has_clan_metrics(self, two_band_sim):
        """DataFrame contains clan-level metrics columns."""
        two_band_sim.run()
        df = two_band_sim.to_dataframe()
        # These are emitted by ClanMetricsCollector
        expected_cols = ["inter_band_violence_rate", "total_trade_volume"]
        for col in expected_cols:
            assert col in df.columns, f"Missing column: {col}"

    def test_to_dataframe_empty_before_run(self, two_band_sim):
        """DataFrame is empty if run() hasn't been called."""
        df = two_band_sim.to_dataframe()
        assert len(df) == 0

    def test_to_csv(self, two_band_sim):
        """to_csv() writes a valid CSV file."""
        two_band_sim.run()
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            path = f.name
        try:
            two_band_sim.to_csv(path)
            assert os.path.exists(path)
            # Read back and verify
            import pandas as pd
            df = pd.read_csv(path)
            assert len(df) == 10
            assert "year" in df.columns
        finally:
            os.unlink(path)

    def test_get_clan_history(self, two_band_sim):
        """get_clan_history returns flat metric dicts."""
        two_band_sim.run()
        history = two_band_sim.get_clan_history()
        assert len(history) == 10
        assert isinstance(history[0], dict)
        assert "year" in history[0]


# ── Per-band institutional differentiation tests ──────────────────────────────

class TestInstitutionalDifferentiation:

    def test_law_strength_differs_between_bands(self):
        """Bands with different law_strength run under different institutional regimes.

        Note: the v1 institution engine applies institutional drift, so
        law_strength changes slightly each tick.  We verify that the State
        band still has substantially higher law_strength than the Anarchy band
        after running, which confirms per-band Config isolation.
        """
        sim = ClanSimulation(
            seed=42,
            n_years=5,
            band_setups=[
                ("Anarchy", Config(law_strength=0.0, property_rights_strength=0.0)),
                ("State", Config(law_strength=0.9, property_rights_strength=0.9)),
            ],
            population_per_band=30,
        )
        sim.run()
        anarchy_cfg = sim.get_band_config("Anarchy")
        state_cfg = sim.get_band_config("State")
        # State band should still have substantially higher law_strength
        # (drift is small ~0.01/year, so after 5 years gap is still large)
        assert state_cfg.law_strength > anarchy_cfg.law_strength + 0.5, (
            f"Expected State >> Anarchy: state={state_cfg.law_strength:.3f}, "
            f"anarchy={anarchy_cfg.law_strength:.3f}"
        )

    def test_per_band_config_used_in_tick(self):
        """Verify per-band Config actually drives intra-band dynamics.

        Use a detectable signal: set resource_abundance very differently.
        After several ticks, mean resources should diverge between bands.
        """
        sim = ClanSimulation(
            seed=42,
            n_years=10,
            band_setups=[
                ("Poor", Config(resource_abundance=0.3, base_resource_per_agent=2.0)),
                ("Rich", Config(resource_abundance=2.0, base_resource_per_agent=20.0)),
            ],
            population_per_band=30,
        )
        sim.run()

        # Extract mean resources per band at final tick
        poor_band = sim.clan_society.bands[sim._band_name_to_id["Poor"]]
        rich_band = sim.clan_society.bands[sim._band_name_to_id["Rich"]]

        poor_res = np.mean([a.current_resources for a in poor_band.get_living()])
        rich_res = np.mean([a.current_resources for a in rich_band.get_living()])

        # Rich band should have substantially more resources
        assert rich_res > poor_res, (
            f"Expected Rich band to have more resources: poor={poor_res:.2f}, rich={rich_res:.2f}"
        )


# ── Edge case tests ───────────────────────────────────────────────────────────

class TestEdgeCases:

    def test_single_band(self):
        """ClanSimulation works with a single band."""
        sim = ClanSimulation(
            seed=42, n_years=5, n_bands=1, population_per_band=30
        )
        history = sim.run()
        assert len(history) == 5

    def test_many_bands(self):
        """ClanSimulation works with 5 bands (O(N^2) interactions)."""
        sim = ClanSimulation(
            seed=42, n_years=3, n_bands=5, population_per_band=20
        )
        history = sim.run()
        assert len(history) == 3

    def test_one_year(self):
        """Single-year simulation."""
        sim = ClanSimulation(
            seed=42, n_years=1, n_bands=2, population_per_band=30
        )
        history = sim.run()
        assert len(history) == 1
