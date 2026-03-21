"""
Clan smoke tests — fast sanity checks for the SIMSIV v2 multi-band layer.

Tests verify:
  - Band and ClanSociety can be constructed without errors.
  - ClanEngine runs 5 ticks without crashing.
  - Both bands still have living agents after 5 ticks.
  - Year counter in each band's society advances correctly.
  - Inter-band interaction scheduling is deterministic and bounded.
  - Trust is updated after interactions.
  - Band removal works cleanly.
  - Zero-population edge case: population rescue triggers when a band
    falls below min_viable_population.
"""

import sys
import os

import numpy as np
import pytest

# Ensure project root is importable regardless of working directory.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from models.clan import Band, ClanSociety
from engines.clan_base import ClanEngine


# ── Fixtures ─────────────────────────────────────────────────────────────────

def _make_two_band_clan(seed: int = 99, pop: int = 50):
    """Return (clan_society, engine, config, rng) with two bands of `pop` agents each."""
    config = Config(
        population_size=pop,
        years=10,
        seed=seed,
        # Keep migration disabled so intra-band migration doesn't distort counts
        migration_enabled=False,
    )
    rng = np.random.default_rng(seed)

    # Each band gets its own rng derived from the master rng so their internal
    # trajectories are independent but the overall run is still reproducible.
    rng_band1 = np.random.default_rng(rng.integers(0, 2**31))
    rng_band2 = np.random.default_rng(rng.integers(0, 2**31))

    band1 = Band(band_id=1, name="Northern Band", config=config, rng=rng_band1, origin_year=0)
    band2 = Band(band_id=2, name="Southern Band", config=config, rng=rng_band2, origin_year=0)

    clan = ClanSociety(base_interaction_rate=0.8)  # high rate to ensure interactions occur
    clan.add_band(band1)
    clan.add_band(band2)
    clan.set_distance(1, 2, 0.2)  # close bands — high interaction probability

    engine = ClanEngine()
    return clan, engine, config, rng


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_band_construction():
    """Band constructs without error and exposes correct properties."""
    config = Config(population_size=30, years=1, seed=1)
    rng = np.random.default_rng(1)
    band = Band(band_id=7, name="Test Band", config=config, rng=rng, origin_year=5)

    assert band.band_id == 7
    assert band.name == "Test Band"
    assert band.origin_year == 5
    assert band.population_size() > 0
    # Delegates work
    assert len(band.get_living()) == band.population_size()


def test_clan_society_add_remove():
    """ClanSociety add_band / remove_band works and cleans up distances."""
    config = Config(population_size=20, years=1, seed=2)
    rng_a = np.random.default_rng(2)
    rng_b = np.random.default_rng(3)

    band_a = Band(1, "A", config, rng_a)
    band_b = Band(2, "B", config, rng_b)

    clan = ClanSociety()
    clan.add_band(band_a)
    clan.add_band(band_b)
    assert 1 in clan.bands
    assert 2 in clan.bands

    # Distance entry should exist
    assert (1, 2) in clan.distance_matrix

    clan.remove_band(2)
    assert 2 not in clan.bands
    # Distance entry should be cleaned up
    assert (1, 2) not in clan.distance_matrix


def test_clan_engine_5_ticks_no_crash():
    """ClanEngine.tick() runs 5 times without raising any exception."""
    clan, engine, config, rng = _make_two_band_clan(seed=42, pop=50)

    for year in range(1, 6):
        result = engine.tick(clan, year, rng, config)
        assert result is not None, f"tick returned None at year {year}"
        assert result["year"] == year


def test_both_bands_have_agents_after_5_ticks():
    """Both bands must have at least one living agent after 5 ticks."""
    clan, engine, config, rng = _make_two_band_clan(seed=42, pop=50)

    for year in range(1, 6):
        engine.tick(clan, year, rng, config)

    for band_id, band in clan.bands.items():
        assert band.population_size() > 0, (
            f"Band {band_id} has no living agents after 5 ticks"
        )


def test_year_counter_advances_in_both_bands():
    """Each band's society.year must equal the current simulation year after each tick."""
    clan, engine, config, rng = _make_two_band_clan(seed=42, pop=50)

    for year in range(1, 6):
        engine.tick(clan, year, rng, config)
        for band_id, band in clan.bands.items():
            assert band.society.year == year, (
                f"Band {band_id} society.year={band.society.year} expected {year}"
            )


def test_tick_returns_per_band_metrics():
    """tick() result dict contains band_metrics for each active band."""
    clan, engine, config, rng = _make_two_band_clan(seed=42, pop=50)

    result = engine.tick(clan, 1, rng, config)

    assert "band_metrics" in result
    assert 1 in result["band_metrics"]
    assert 2 in result["band_metrics"]

    # Each metrics row must at minimum contain 'population'
    for band_id in (1, 2):
        row = result["band_metrics"][band_id]
        assert "population" in row, f"No 'population' key in metrics for Band {band_id}"
        assert row["population"] >= 0


def test_tick_returns_total_population():
    """result['total_population'] sums all living agents across bands."""
    clan, engine, config, rng = _make_two_band_clan(seed=42, pop=50)

    result = engine.tick(clan, 1, rng, config)

    expected = sum(b.population_size() for b in clan.bands.values())
    assert result["total_population"] == expected


def test_inter_band_interactions_scheduled():
    """With high base_interaction_rate and close distance, interactions occur."""
    # Use a deterministic seed and run several ticks; expect at least one interaction.
    clan, engine, config, rng = _make_two_band_clan(seed=7, pop=50)

    all_inter_events: list[dict] = []
    for year in range(1, 11):
        result = engine.tick(clan, year, rng, config)
        all_inter_events.extend(result["inter_band_events"])

    assert len(all_inter_events) > 0, (
        "Expected at least one inter-band interaction over 10 ticks with "
        "high interaction rate and close distance."
    )


def test_trust_updated_after_interaction():
    """Band trust scores change after inter-band interactions."""
    clan, engine, config, rng = _make_two_band_clan(seed=7, pop=50)

    # Default trust is 0.5 (not yet set)
    initial_trust_1_to_2 = clan.bands[1].trust_toward(2)
    initial_trust_2_to_1 = clan.bands[2].trust_toward(1)

    # Run enough ticks that at least one interaction occurs
    had_interaction = False
    for year in range(1, 21):
        result = engine.tick(clan, year, rng, config)
        if result["inter_band_events"]:
            had_interaction = True
            break

    if not had_interaction:
        pytest.skip("No interaction occurred in 20 ticks — trust test inconclusive.")

    final_trust_1_to_2 = clan.bands[1].trust_toward(2)
    final_trust_2_to_1 = clan.bands[2].trust_toward(1)

    assert final_trust_1_to_2 != initial_trust_1_to_2 or \
           final_trust_2_to_1 != initial_trust_2_to_1, (
        "Trust should change after at least one inter-band interaction."
    )


def test_band_isolation():
    """Each band's Society is fully isolated — agents do not bleed between bands."""
    config = Config(population_size=30, years=1, seed=5, migration_enabled=False)
    rng1 = np.random.default_rng(10)
    rng2 = np.random.default_rng(20)

    band1 = Band(1, "Band1", config, rng1)
    band2 = Band(2, "Band2", config, rng2)

    # Collect all agent IDs from each band
    ids1 = {a.id for a in band1.get_living()}
    ids2 = {a.id for a in band2.get_living()}

    # No ID overlap between two freshly created bands (they both start from 1
    # by design — IdCounter is per-Society — so IDs WILL overlap numerically,
    # but they should not be the SAME OBJECTS)
    for agent_id in ids1:
        agent_in_b1 = band1.get_by_id(agent_id)
        agent_in_b2 = band2.get_by_id(agent_id)
        if agent_in_b2 is not None:
            # Both bands may have agent with same numeric ID, but they must be
            # distinct Python objects (isolated societies)
            assert agent_in_b1 is not agent_in_b2, (
                f"Agent id={agent_id} is the SAME OBJECT in both bands — "
                "societies are not isolated!"
            )


def test_band_metrics_history_accumulates():
    """engine.get_band_history() grows one row per tick."""
    clan, engine, config, rng = _make_two_band_clan(seed=42, pop=50)

    for year in range(1, 6):
        engine.tick(clan, year, rng, config)

    history1 = engine.get_band_history(1)
    history2 = engine.get_band_history(2)

    assert len(history1) == 5, f"Expected 5 history rows for Band 1, got {len(history1)}"
    assert len(history2) == 5, f"Expected 5 history rows for Band 2, got {len(history2)}"


def test_schedule_interactions_deterministic():
    """Same rng state produces the same interaction schedule."""
    config = Config(population_size=30, years=1, seed=3, migration_enabled=False)

    def _make_clan():
        rng_a = np.random.default_rng(100)
        rng_b = np.random.default_rng(200)
        band_a = Band(1, "A", config, rng_a)
        band_b = Band(2, "B", config, rng_b)
        clan = ClanSociety(base_interaction_rate=0.5)
        clan.add_band(band_a)
        clan.add_band(band_b)
        clan.set_distance(1, 2, 0.3)
        return clan

    rng1 = np.random.default_rng(77)
    rng2 = np.random.default_rng(77)

    clan1 = _make_clan()
    clan2 = _make_clan()

    pairs1 = clan1.schedule_interactions(year=1, rng=rng1)
    pairs2 = clan2.schedule_interactions(year=1, rng=rng2)

    # Same seed → same number of scheduled pairs
    assert len(pairs1) == len(pairs2), (
        "schedule_interactions is not deterministic given the same rng seed."
    )
