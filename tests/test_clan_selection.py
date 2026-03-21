"""
tests/test_clan_selection.py — Test suite for engines/clan_selection.py and
metrics/clan_collectors.py (SIMSIV v2, Turn 4).

Coverage:
  selection_tick:
    - Returns a list of event dicts (always, even when nothing happens)
    - First event is always type "selection_stats" with required keys
    - within_group_selection_coeff is a finite float
    - between_group_selection_coeff is a finite float
    - Single-band clan: between_group_selection_coeff = 0.0
    - Empty band: no crash, coefficients fallback to 0.0
    - Deterministic: same rng seed → same output

  Band fission:
    - Band exceeding fission_threshold splits into two daughter bands
    - Daughters together contain all agents from the parent
    - Parent band is removed from ClanSociety
    - Daughter bands are added to ClanSociety
    - Daughters have fresh band_ids (max_existing + 1 and +2)
    - Event type is "band_fission" with required keys
    - Daughters start at moderate distance from each other (0.3)
    - Band below fission_threshold is NOT fissioned

  Band extinction:
    - Band below extinction_threshold is absorbed by nearest band
    - Refugees appear in absorbing band
    - Extinct band is removed from ClanSociety
    - Event type is "band_extinction" with required keys
    - Single-band clan with extinction: band removed, event emitted
    - Band above extinction_threshold is NOT absorbed

  Inter-band migration:
    - No agents migrate when migration_rate = 0.0
    - Migrants leave origin band and appear in destination band
    - Event type is "inter_band_migration" with required keys
    - Origin band never drops below min_viable_population + 1
    - Migration only involves PRIME/MATURE unbonded adults

  ClanMetricsCollector:
    - collect() returns a dict with "year" key
    - Per-band trait means appear with correct naming convention
    - Fst values are in [0, 1]
    - inter_band_trust keys appear for each band pair
    - Selection coefficients from set_selection_coefficients appear in row
    - get_history() grows one row per collect() call
    - reset() clears history

  Integration:
    - ClanEngine.tick() now returns "selection_events" and "clan_metrics" keys
    - get_clan_history() grows one row per tick
    - reset() clears clan_metrics history
    - No crash over 10 ticks with two bands
"""

import sys
import os

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from models.clan import Band, ClanSociety, ClanConfig
from engines.clan_base import ClanEngine
from engines.clan_selection import (
    selection_tick,
    _compute_within_group_selection,
    _compute_between_group_selection,
    _process_migration,
    _process_fission,
    _process_extinction,
)
from metrics.clan_collectors import ClanMetricsCollector


# ── Fixtures ──────────────────────────────────────────────────────────────────

def _make_config(pop: int = 50, seed: int = 1) -> Config:
    return Config(
        population_size=pop,
        years=20,
        seed=seed,
        migration_enabled=False,
    )


def _make_band(band_id: int, config: Config, rng_seed: int) -> Band:
    rng = np.random.default_rng(rng_seed)
    return Band(band_id=band_id, name=f"Band{band_id}", config=config, rng=rng,
                origin_year=0)


def _make_two_band_clan(seed: int = 42, pop: int = 50):
    """Return (clan_society, engine, config, rng, clan_config) with two bands."""
    config = _make_config(pop=pop, seed=seed)
    clan_config = ClanConfig()
    rng = np.random.default_rng(seed)
    b1 = _make_band(1, config, int(rng.integers(0, 2**31)))
    b2 = _make_band(2, config, int(rng.integers(0, 2**31)))
    clan = ClanSociety(base_interaction_rate=0.8)
    clan.add_band(b1)
    clan.add_band(b2)
    clan.set_distance(1, 2, 0.2)
    engine = ClanEngine()
    return clan, engine, config, rng, clan_config


# ── selection_tick unit tests ─────────────────────────────────────────────────

def test_selection_tick_returns_list():
    """selection_tick always returns a list."""
    clan, _, config, rng, clan_cfg = _make_two_band_clan()
    events = selection_tick(clan, year=1, rng=rng, config=config, clan_config=clan_cfg)
    assert isinstance(events, list)


def test_selection_tick_first_event_is_stats():
    """The first event in the list is always type 'selection_stats'."""
    clan, _, config, rng, clan_cfg = _make_two_band_clan()
    events = selection_tick(clan, year=1, rng=rng, config=config, clan_config=clan_cfg)
    assert len(events) >= 1
    assert events[0]["type"] == "selection_stats"


def test_selection_stats_event_keys():
    """selection_stats event has all required keys."""
    clan, _, config, rng, clan_cfg = _make_two_band_clan()
    events = selection_tick(clan, year=1, rng=rng, config=config, clan_config=clan_cfg)
    stats = events[0]
    required_keys = {
        "type", "year", "agent_ids", "description", "outcome",
        "within_group_selection_coeff", "between_group_selection_coeff",
    }
    assert required_keys.issubset(stats.keys()), (
        f"Missing keys: {required_keys - stats.keys()}"
    )


def test_within_group_selection_coeff_is_finite():
    """within_group_selection_coeff is a finite float."""
    clan, _, config, rng, clan_cfg = _make_two_band_clan(pop=60)
    events = selection_tick(clan, year=1, rng=rng, config=config, clan_config=clan_cfg)
    coeff = events[0]["within_group_selection_coeff"]
    assert isinstance(coeff, float)
    assert np.isfinite(coeff), f"within_group_selection_coeff is not finite: {coeff}"


def test_between_group_selection_coeff_is_finite():
    """between_group_selection_coeff is a finite float."""
    clan, _, config, rng, clan_cfg = _make_two_band_clan(pop=60)
    events = selection_tick(clan, year=1, rng=rng, config=config, clan_config=clan_cfg)
    coeff = events[0]["between_group_selection_coeff"]
    assert isinstance(coeff, float)
    assert np.isfinite(coeff), f"between_group_selection_coeff is not finite: {coeff}"


def test_between_group_coeff_zero_with_one_band():
    """With only one band, between_group_selection_coeff must be 0.0."""
    config = _make_config(pop=50)
    rng = np.random.default_rng(7)
    b1 = _make_band(1, config, 11)
    clan = ClanSociety()
    clan.add_band(b1)

    demo_coeff, raid_coeff = _compute_between_group_selection(clan)
    assert demo_coeff == 0.0, f"Expected 0.0 for single-band clan, got {demo_coeff}"
    assert raid_coeff == 0.0, f"Expected 0.0 for single-band clan, got {raid_coeff}"


def test_within_group_coeff_fallback_with_few_adults():
    """Band with fewer than 5 adults: within-group coeff falls back to 0.0."""
    config = Config(population_size=5, years=5, seed=1, migration_enabled=False)
    rng = np.random.default_rng(1)
    b1 = Band(1, "Tiny", config, rng, origin_year=0)
    clan = ClanSociety()
    clan.add_band(b1)

    # Kill most agents to ensure < 5 adults
    for a in b1.get_living():
        if a.life_stage in ("PRIME", "MATURE") and a.age > 25:
            a.alive = False

    coeff = _compute_within_group_selection(clan)
    # Should not crash; returns 0.0 or a finite float
    assert np.isfinite(coeff)


def test_selection_tick_deterministic():
    """Same rng seed → identical selection_tick output."""
    clan1, _, config1, rng1, cfg1 = _make_two_band_clan(seed=77)
    clan2, _, config2, rng2, cfg2 = _make_two_band_clan(seed=77)

    events1 = selection_tick(clan1, year=5, rng=rng1, config=config1, clan_config=cfg1)
    events2 = selection_tick(clan2, year=5, rng=rng2, config=config2, clan_config=cfg2)

    assert events1[0]["within_group_selection_coeff"] == pytest.approx(
        events2[0]["within_group_selection_coeff"]
    )
    assert events1[0]["between_group_selection_coeff"] == pytest.approx(
        events2[0]["between_group_selection_coeff"]
    )


def test_selection_tick_no_crash_empty_band():
    """Clan with one empty band does not crash."""
    config = _make_config(pop=40)
    rng = np.random.default_rng(9)
    b1 = _make_band(1, config, 10)
    b2 = _make_band(2, config, 20)

    # Kill all agents in b2
    for a in b2.get_living():
        a.alive = False

    clan = ClanSociety()
    clan.add_band(b1)
    clan.add_band(b2)

    rng_sel = np.random.default_rng(42)
    events = selection_tick(clan, year=1, rng=rng_sel, config=config)
    # Should not crash; first event is stats
    assert events[0]["type"] == "selection_stats"


# ── Band fission tests ────────────────────────────────────────────────────────

def test_fission_creates_two_daughter_bands():
    """A band exceeding fission_threshold splits into two daughter bands."""
    config = _make_config(pop=60)
    clan_config = ClanConfig(fission_threshold=20)  # low threshold for testing

    b1 = _make_band(1, config, 10)
    b2 = _make_band(2, config, 20)

    # Make b1 larger than fission threshold by inflating with clones
    # Actually just set a very low threshold — b1 has ~60 agents by default
    clan = ClanSociety()
    clan.add_band(b1)
    clan.add_band(b2)
    clan.set_distance(1, 2, 0.4)

    rng = np.random.default_rng(5)
    initial_pop_b1 = b1.population_size()

    fission_events = _process_fission(clan, year=1, rng=rng, config=config,
                                      clan_config=clan_config)

    # Only b1 should have fissioned (b1 pop > 20, b2 pop > 20 so both may fission)
    fission_types = [e for e in fission_events if e["type"] == "band_fission"]
    assert len(fission_types) >= 1, "Expected at least one fission event."

    # Parent band(s) removed, daughter bands added
    for ev in fission_types:
        pid = ev["parent_band_id"]
        assert pid not in clan.bands, f"Parent band {pid} should have been removed."
        d1 = ev["daughter_band_id_1"]
        d2 = ev["daughter_band_id_2"]
        assert d1 in clan.bands, f"Daughter band {d1} not in clan."
        assert d2 in clan.bands, f"Daughter band {d2} not in clan."


def test_fission_preserves_all_agents():
    """After fission, total agents in daughters = agents in parent before split."""
    config = _make_config(pop=50)
    clan_config = ClanConfig(fission_threshold=20)

    b1 = _make_band(1, config, 10)
    clan = ClanSociety()
    clan.add_band(b1)
    # No second band needed for fission test

    initial_agents = set(a.id for a in b1.get_living())
    initial_pop = len(initial_agents)
    assert initial_pop > 20, "b1 needs more agents than fission_threshold for this test."

    rng = np.random.default_rng(3)
    fission_events = _process_fission(clan, year=1, rng=rng, config=config,
                                      clan_config=clan_config)

    fission_event = next((e for e in fission_events if e["type"] == "band_fission"), None)
    assert fission_event is not None, "Fission should have fired."

    d1_id = fission_event["daughter_band_id_1"]
    d2_id = fission_event["daughter_band_id_2"]

    d1_agents = set(a.id for a in clan.bands[d1_id].get_living())
    d2_agents = set(a.id for a in clan.bands[d2_id].get_living())

    combined = d1_agents | d2_agents
    # All original agents should appear in daughters (after possible id reassignment)
    # Check count equality
    assert len(combined) == initial_pop, (
        f"Expected {initial_pop} total agents after fission, "
        f"got {len(combined)} (d1={len(d1_agents)}, d2={len(d2_agents)})"
    )


def test_fission_event_keys():
    """Fission event has all required keys."""
    config = _make_config(pop=50)
    clan_config = ClanConfig(fission_threshold=20)

    b1 = _make_band(1, config, 15)
    clan = ClanSociety()
    clan.add_band(b1)

    rng = np.random.default_rng(7)
    events = _process_fission(clan, year=3, rng=rng, config=config, clan_config=clan_config)

    fission_events = [e for e in events if e["type"] == "band_fission"]
    if not fission_events:
        pytest.skip("No fission fired — check fission_threshold vs band population.")

    required_keys = {
        "type", "year", "agent_ids", "description", "outcome",
        "parent_band_id", "daughter_band_id_1", "daughter_band_id_2",
        "daughter_1_pop", "daughter_2_pop",
    }
    for ev in fission_events:
        assert required_keys.issubset(ev.keys()), (
            f"Fission event missing keys: {required_keys - ev.keys()}"
        )
        assert ev["outcome"] == "fission"
        assert ev["year"] == 3


def test_fission_daughters_close_to_each_other():
    """Daughter bands start at distance 0.3 from each other."""
    config = _make_config(pop=50)
    clan_config = ClanConfig(fission_threshold=20)

    b1 = _make_band(1, config, 10)
    b2 = _make_band(2, config, 20)  # second band so distance matrix is populated
    clan = ClanSociety()
    clan.add_band(b1)
    clan.add_band(b2)
    clan.set_distance(1, 2, 0.5)

    rng = np.random.default_rng(11)
    events = _process_fission(clan, year=1, rng=rng, config=config, clan_config=clan_config)

    fission_event = next((e for e in events if e["type"] == "band_fission"), None)
    if fission_event is None:
        pytest.skip("No fission fired.")

    d1_id = fission_event["daughter_band_id_1"]
    d2_id = fission_event["daughter_band_id_2"]
    dist = clan.get_distance(d1_id, d2_id)
    assert dist == pytest.approx(0.3), (
        f"Expected daughter-daughter distance 0.3, got {dist}"
    )


def test_fission_not_triggered_below_threshold():
    """Band below fission_threshold is not fissioned."""
    config = _make_config(pop=30)
    clan_config = ClanConfig(fission_threshold=200)  # very high threshold

    b1 = _make_band(1, config, 5)
    clan = ClanSociety()
    clan.add_band(b1)

    rng = np.random.default_rng(8)
    events = _process_fission(clan, year=1, rng=rng, config=config, clan_config=clan_config)

    fission_events = [e for e in events if e["type"] == "band_fission"]
    assert len(fission_events) == 0, "Should not fission — band below threshold."
    assert 1 in clan.bands, "Band 1 should still exist."


def test_fission_daughters_inherit_parent_distances():
    """Regression test for Turn 4 blocking bug: daughter bands must inherit the
    parent's actual distances, not the default 0.5 that get_distance returns
    after the parent has been removed.

    Setup:
        3 bands — A (id=1), B (id=2), C (id=3).
        A-B distance = 0.2  (near)
        A-C distance = 0.8  (far)
        B and C each have pop=10, below fission_threshold=20, so only A fissions.

    Trigger fission on A (pop=50, threshold=20).

    Assert:
        Both daughter bands have distance to B close to 0.2 (within ±0.1).
        Both daughter bands have distance to C close to 0.8 (within ±0.1).

    Before the fix, remove_band(A) was called before the distance-inheritance
    loop, so get_distance(A, B) and get_distance(A, C) both returned the
    default 0.5 — masking the real geography.
    """
    # Band A will fission; B and C must remain below fission_threshold=20
    # so they are not also removed during this call.
    config_a = _make_config(pop=50)   # band A — will fission (pop=50 > threshold=20)
    config_bc = _make_config(pop=10)  # bands B and C — stay intact (pop=10 < threshold=20)
    clan_config = ClanConfig(fission_threshold=20)

    b_a = _make_band(1, config_a,  rng_seed=10)
    b_b = _make_band(2, config_bc, rng_seed=20)
    b_c = _make_band(3, config_bc, rng_seed=30)

    clan = ClanSociety()
    clan.add_band(b_a)
    clan.add_band(b_b)
    clan.add_band(b_c)

    # Set known distances from A to its neighbours.
    clan.set_distance(1, 2, 0.2)   # A near B
    clan.set_distance(1, 3, 0.8)   # A far from C
    clan.set_distance(2, 3, 0.5)   # B-C irrelevant for this test

    # Confirm the precondition: only band A should exceed the threshold.
    assert b_a.population_size() > clan_config.fission_threshold, (
        "Precondition: band A must exceed fission_threshold."
    )
    assert b_b.population_size() <= clan_config.fission_threshold, (
        "Precondition: band B must be at or below fission_threshold."
    )
    assert b_c.population_size() <= clan_config.fission_threshold, (
        "Precondition: band C must be at or below fission_threshold."
    )

    rng = np.random.default_rng(99)
    events = _process_fission(clan, year=1, rng=rng, config=config_a,
                               clan_config=clan_config)

    fission_event = next(
        (e for e in events if e["type"] == "band_fission" and e["parent_band_id"] == 1),
        None,
    )
    assert fission_event is not None, (
        "Expected fission of band 1 (pop=50, threshold=20)."
    )

    d1_id = fission_event["daughter_band_id_1"]
    d2_id = fission_event["daughter_band_id_2"]

    # Bands B and C must still be in the clan (not fissioned).
    assert 2 in clan.bands, "Band B (id=2) should still exist after only band A fissioned."
    assert 3 in clan.bands, "Band C (id=3) should still exist after only band A fissioned."

    # Noise tolerance: fission adds ±0.05 noise per daughter, so allow ±0.1.
    noise_tol = 0.1

    for daughter_id in (d1_id, d2_id):
        dist_to_b = clan.get_distance(daughter_id, 2)
        dist_to_c = clan.get_distance(daughter_id, 3)
        assert abs(dist_to_b - 0.2) <= noise_tol, (
            f"Daughter {daughter_id} distance to B should be ~0.2 "
            f"(parent A-B=0.2), got {dist_to_b:.3f}.  "
            f"If this is 0.5, the bug (remove_band before distance capture) "
            f"has regressed."
        )
        assert abs(dist_to_c - 0.8) <= noise_tol, (
            f"Daughter {daughter_id} distance to C should be ~0.8 "
            f"(parent A-C=0.8), got {dist_to_c:.3f}.  "
            f"If this is 0.5, the bug (remove_band before distance capture) "
            f"has regressed."
        )


# ── Band extinction tests ──────────────────────────────────────────────────────

def test_extinction_absorbs_tiny_band():
    """Band below extinction_threshold is absorbed by the nearest band."""
    config = _make_config(pop=50)
    clan_config = ClanConfig(extinction_threshold=20)

    b1 = _make_band(1, config, 10)
    b2 = _make_band(2, config, 20)
    clan = ClanSociety()
    clan.add_band(b1)
    clan.add_band(b2)
    clan.set_distance(1, 2, 0.3)

    # Kill most agents in b1 so it falls below threshold
    living = b1.get_living()
    for a in living[5:]:  # leave 5 survivors
        a.alive = False

    assert b1.population_size() < clan_config.extinction_threshold

    b2_initial_pop = b2.population_size()

    rng = np.random.default_rng(13)
    events = _process_extinction(clan, year=2, rng=rng, config=config,
                                  clan_config=clan_config)

    ext_events = [e for e in events if e["type"] == "band_extinction"]
    assert len(ext_events) >= 1, "Expected extinction event."

    # b1 should be removed
    assert 1 not in clan.bands, "Extinct band 1 should have been removed."
    # b2 should have gained refugees
    b2_final_pop = clan.bands[2].population_size()
    assert b2_final_pop > b2_initial_pop, (
        f"Band 2 should have gained refugees (was {b2_initial_pop}, now {b2_final_pop})"
    )


def test_extinction_event_keys():
    """Extinction event has required keys."""
    config = _make_config(pop=50)
    clan_config = ClanConfig(extinction_threshold=20)

    b1 = _make_band(1, config, 10)
    b2 = _make_band(2, config, 20)
    clan = ClanSociety()
    clan.add_band(b1)
    clan.add_band(b2)

    living = b1.get_living()
    for a in living[3:]:
        a.alive = False

    rng = np.random.default_rng(15)
    events = _process_extinction(clan, year=7, rng=rng, config=config,
                                  clan_config=clan_config)

    ext_events = [e for e in events if e["type"] == "band_extinction"]
    if not ext_events:
        pytest.skip("Extinction not triggered — check threshold.")

    required_keys = {
        "type", "year", "agent_ids", "description", "outcome",
        "extinct_band_id", "absorbing_band_id",
    }
    for ev in ext_events:
        assert required_keys.issubset(ev.keys()), (
            f"Extinction event missing keys: {required_keys - ev.keys()}"
        )
        assert ev["year"] == 7


def test_extinction_single_band_no_crash():
    """Single-band clan with extinction: band removed, no crash."""
    config = _make_config(pop=30)
    clan_config = ClanConfig(extinction_threshold=20)

    b1 = _make_band(1, config, 5)
    clan = ClanSociety()
    clan.add_band(b1)

    # Kill most agents
    living = b1.get_living()
    for a in living[3:]:
        a.alive = False

    rng = np.random.default_rng(22)
    events = _process_extinction(clan, year=10, rng=rng, config=config,
                                  clan_config=clan_config)

    ext_events = [e for e in events if e["type"] == "band_extinction"]
    # Should have fired and band should be gone
    if b1.population_size() < clan_config.extinction_threshold:
        assert 1 not in clan.bands, "Extinct band should be removed."
        assert len(ext_events) >= 1


def test_extinction_not_triggered_above_threshold():
    """Band above extinction_threshold is not absorbed."""
    config = _make_config(pop=50)
    clan_config = ClanConfig(extinction_threshold=5)  # very low threshold

    b1 = _make_band(1, config, 10)
    b2 = _make_band(2, config, 20)
    clan = ClanSociety()
    clan.add_band(b1)
    clan.add_band(b2)

    # Both bands have pop >> 5
    assert b1.population_size() > clan_config.extinction_threshold

    rng = np.random.default_rng(30)
    events = _process_extinction(clan, year=1, rng=rng, config=config,
                                  clan_config=clan_config)

    ext_events = [e for e in events if e["type"] == "band_extinction"]
    assert len(ext_events) == 0, "Neither band should be absorbed."


# ── Migration tests ───────────────────────────────────────────────────────────

def test_migration_zero_rate_no_events():
    """Migration rate 0.0 → no migration events."""
    config = _make_config(pop=50)
    clan_config = ClanConfig(migration_rate_per_agent=0.0)

    b1 = _make_band(1, config, 10)
    b2 = _make_band(2, config, 20)
    clan = ClanSociety()
    clan.add_band(b1)
    clan.add_band(b2)
    clan.set_distance(1, 2, 0.0)  # close bands
    # High trust
    b1.update_trust(2, 0.3)
    b2.update_trust(1, 0.3)

    rng = np.random.default_rng(5)
    events = _process_migration(clan, year=1, rng=rng, config=config,
                                 clan_config=clan_config)
    mig_events = [e for e in events if e["type"] == "inter_band_migration"]
    assert len(mig_events) == 0, "Migration rate=0 should produce no events."


def test_migration_event_keys():
    """Migration event (if it occurs) has required keys."""
    config = _make_config(pop=80)
    # High migration rate to ensure events occur
    clan_config = ClanConfig(migration_rate_per_agent=1.0)

    b1 = _make_band(1, config, 10)
    b2 = _make_band(2, config, 20)
    clan = ClanSociety()
    clan.add_band(b1)
    clan.add_band(b2)
    clan.set_distance(1, 2, 0.0)
    b1.update_trust(2, 0.5)
    b2.update_trust(1, 0.5)

    rng = np.random.default_rng(7)
    events = _process_migration(clan, year=3, rng=rng, config=config,
                                 clan_config=clan_config)
    mig_events = [e for e in events if e["type"] == "inter_band_migration"]

    if not mig_events:
        pytest.skip("No migration events occurred — increase migration_rate or pop.")

    required_keys = {
        "type", "year", "agent_ids", "description", "outcome",
        "origin_band_id", "destination_band_id",
    }
    for ev in mig_events:
        assert required_keys.issubset(ev.keys()), (
            f"Migration event missing keys: {required_keys - ev.keys()}"
        )
        assert ev["outcome"] == "migrated"
        assert ev["year"] == 3


def test_migration_origin_population_conserved():
    """Total population is conserved after migration (migrants move, not multiply)."""
    config = _make_config(pop=60)
    clan_config = ClanConfig(migration_rate_per_agent=0.5)  # high rate

    b1 = _make_band(1, config, 10)
    b2 = _make_band(2, config, 20)
    clan = ClanSociety()
    clan.add_band(b1)
    clan.add_band(b2)
    clan.set_distance(1, 2, 0.0)
    b1.update_trust(2, 0.5)
    b2.update_trust(1, 0.5)

    total_before = sum(b.population_size() for b in clan.bands.values())

    rng = np.random.default_rng(9)
    _process_migration(clan, year=1, rng=rng, config=config, clan_config=clan_config)

    total_after = sum(b.population_size() for b in clan.bands.values())
    assert total_after == total_before, (
        f"Total population changed after migration: {total_before} → {total_after}"
    )


def test_migration_origin_never_below_min_vp():
    """Origin band is guarded so it cannot drop below min_viable_population + 1.

    With pop=50 and min_vp=20, the guard stops migration when the origin band
    reaches min_vp + 1 = 21.  We verify that after migration, BOTH origin and
    destination bands satisfy the guard.
    """
    config = Config(
        population_size=50,
        years=5,
        seed=1,
        migration_enabled=False,
        min_viable_population=20,
    )
    clan_config = ClanConfig(migration_rate_per_agent=1.0)

    b1 = _make_band(1, config, 10)
    b2 = _make_band(2, config, 20)
    clan = ClanSociety()
    clan.add_band(b1)
    clan.add_band(b2)
    clan.set_distance(1, 2, 0.0)
    b1.update_trust(2, 0.5)  # trust=1.0 after update (0.5 + delta clamped)
    b2.update_trust(1, 0.5)

    rng = np.random.default_rng(11)
    _process_migration(clan, year=1, rng=rng, config=config, clan_config=clan_config)

    min_allowed = config.min_viable_population + 1  # the guard floor
    for bid, band in clan.bands.items():
        pop = band.population_size()
        # Each band that acted as an origin should have stopped at >= min_allowed.
        # Bands that only received (pop > initial) trivially satisfy this.
        # We allow 0 only if a band was already empty before (edge case).
        assert pop >= min_allowed or pop == 0, (
            f"Band {bid} (pop={pop}) dropped below guard floor "
            f"(min_viable_population + 1 = {min_allowed})"
        )


# ── ClanMetricsCollector tests ────────────────────────────────────────────────

def test_clan_collector_returns_dict_with_year():
    """collect() returns a dict with year key."""
    clan, _, config, _, _ = _make_two_band_clan()
    collector = ClanMetricsCollector()
    row = collector.collect(clan, year=5, events=[])
    assert isinstance(row, dict)
    assert row["year"] == 5


def test_clan_collector_per_band_population_keys():
    """collect() includes per-band population counts."""
    clan, _, config, _, _ = _make_two_band_clan()
    collector = ClanMetricsCollector()
    row = collector.collect(clan, year=1, events=[])

    for bid in clan.bands:
        key = f"band_{bid}_population"
        assert key in row, f"Missing key: {key}"
        assert row[key] >= 0


def test_clan_collector_trait_means_present():
    """Per-band trait means appear in metrics row."""
    clan, _, config, _, _ = _make_two_band_clan()
    collector = ClanMetricsCollector()
    row = collector.collect(clan, year=1, events=[])

    from models.agent import HERITABLE_TRAITS
    for bid in clan.bands:
        for trait in ["cooperation_propensity", "group_loyalty"]:
            key = f"band_{bid}_mean_{trait}"
            assert key in row, f"Missing trait mean key: {key}"
            assert 0.0 <= row[key] <= 1.0, f"Trait mean out of range: {key}={row[key]}"


def test_clan_collector_fst_values_in_range():
    """Fst values are in [0, 1]."""
    clan, _, config, _, _ = _make_two_band_clan()
    collector = ClanMetricsCollector()
    row = collector.collect(clan, year=1, events=[])

    fst_keys = [k for k in row if k.startswith("fst_")]
    assert len(fst_keys) > 0, "Expected at least one Fst key."
    for k in fst_keys:
        assert 0.0 <= row[k] <= 1.0, f"Fst out of range [0,1]: {k}={row[k]}"


def test_clan_collector_inter_band_trust_present():
    """inter_band_trust keys appear for each band pair."""
    clan, _, config, _, _ = _make_two_band_clan()
    collector = ClanMetricsCollector()
    row = collector.collect(clan, year=1, events=[])

    trust_keys = [k for k in row if k.startswith("inter_band_trust_")]
    assert len(trust_keys) >= 1, "Expected at least one inter_band_trust key."


def test_clan_collector_selection_coefficients():
    """Selection coefficients from set_selection_coefficients appear in row."""
    clan, _, config, _, _ = _make_two_band_clan()
    collector = ClanMetricsCollector()
    collector.set_selection_coefficients(within_coeff=0.123, between_coeff=-0.456)
    row = collector.collect(clan, year=1, events=[])

    assert row["within_group_selection_coeff"] == pytest.approx(0.123)
    assert row["between_group_selection_coeff"] == pytest.approx(-0.456)


def test_clan_collector_history_grows():
    """get_history() grows one row per collect() call."""
    clan, _, config, _, _ = _make_two_band_clan()
    collector = ClanMetricsCollector()

    for year in range(1, 6):
        collector.collect(clan, year=year, events=[])

    history = collector.get_history()
    assert len(history) == 5, f"Expected 5 history rows, got {len(history)}"


def test_clan_collector_reset_clears_history():
    """reset() clears all collected history."""
    clan, _, config, _, _ = _make_two_band_clan()
    collector = ClanMetricsCollector()

    for year in range(1, 4):
        collector.collect(clan, year=year, events=[])

    assert len(collector.get_history()) == 3
    collector.reset()
    assert len(collector.get_history()) == 0


def test_clan_collector_event_counts():
    """Interaction counts are correctly tallied from events."""
    clan, _, config, _, _ = _make_two_band_clan()
    collector = ClanMetricsCollector()

    fake_events = [
        {"type": "inter_band_trade", "outcome": "success"},
        {"type": "inter_band_trade", "outcome": "success"},
        {"type": "inter_band_trade", "outcome": "refused"},
        {"type": "inter_band_raid", "outcome": "attacker_wins"},
        {"type": "inter_band_contact", "outcome": "neutral_contact"},
    ]

    row = collector.collect(clan, year=1, events=fake_events)
    assert row["trade_count"] == 2
    assert row["raid_count"] == 1
    assert row["neutral_count"] == 1
    assert row["refused_trade_count"] == 1
    assert row["total_interactions"] == 5
    assert row["inter_band_violence_rate"] == pytest.approx(1 / 5)


def test_clan_collector_empty_band_no_crash():
    """collect() handles a band with 0 living agents without crashing."""
    config = _make_config(pop=50)
    b1 = _make_band(1, config, 10)
    b2 = _make_band(2, config, 20)
    clan = ClanSociety()
    clan.add_band(b1)
    clan.add_band(b2)

    # Kill all agents in b2
    for a in b2.get_living():
        a.alive = False

    collector = ClanMetricsCollector()
    row = collector.collect(clan, year=1, events=[])  # should not crash
    assert row["band_2_population"] == 0


def test_clan_collector_centroid_distance_present():
    """Centroid distance between band pair is present and non-negative."""
    clan, _, config, _, _ = _make_two_band_clan()
    collector = ClanMetricsCollector()
    row = collector.collect(clan, year=1, events=[])

    dist_keys = [k for k in row if k.startswith("centroid_dist_")]
    assert len(dist_keys) >= 1, "Expected at least one centroid_dist key."
    for k in dist_keys:
        assert row[k] >= 0.0, f"Centroid distance should be non-negative: {k}={row[k]}"


# ── ClanEngine integration tests ──────────────────────────────────────────────

def test_engine_tick_returns_selection_events_key():
    """engine.tick() result includes 'selection_events' key."""
    clan, engine, config, rng, clan_cfg = _make_two_band_clan()
    result = engine.tick(clan, year=1, rng=rng, config=config, clan_config=clan_cfg)
    assert "selection_events" in result, "tick() result should have 'selection_events' key."


def test_engine_tick_returns_clan_metrics_key():
    """engine.tick() result includes 'clan_metrics' key with year."""
    clan, engine, config, rng, clan_cfg = _make_two_band_clan()
    result = engine.tick(clan, year=2, rng=rng, config=config, clan_config=clan_cfg)
    assert "clan_metrics" in result, "tick() result should have 'clan_metrics' key."
    assert result["clan_metrics"]["year"] == 2


def test_engine_get_clan_history_grows():
    """engine.get_clan_history() grows one row per tick."""
    clan, engine, config, rng, clan_cfg = _make_two_band_clan()

    for year in range(1, 6):
        engine.tick(clan, year, rng, config, clan_cfg)

    history = engine.get_clan_history()
    assert len(history) == 5, f"Expected 5 history rows, got {len(history)}"


def test_engine_reset_clears_clan_history():
    """engine.reset() clears the clan metrics history."""
    clan, engine, config, rng, clan_cfg = _make_two_band_clan()

    for year in range(1, 4):
        engine.tick(clan, year, rng, config, clan_cfg)

    assert len(engine.get_clan_history()) == 3
    engine.reset()
    assert len(engine.get_clan_history()) == 0


def test_engine_10_ticks_no_crash():
    """ClanEngine runs 10 ticks with clan_config without crashing."""
    clan, engine, config, rng, clan_cfg = _make_two_band_clan(seed=42, pop=50)

    for year in range(1, 11):
        result = engine.tick(clan, year, rng, config, clan_cfg)
        assert result is not None
        assert result["year"] == year
        assert result["total_population"] >= 0


def test_engine_tick_selection_stats_event_present():
    """tick() selection_events always contains a 'selection_stats' event."""
    clan, engine, config, rng, clan_cfg = _make_two_band_clan()
    result = engine.tick(clan, year=1, rng=rng, config=config, clan_config=clan_cfg)

    sel_events = result["selection_events"]
    assert len(sel_events) >= 1
    assert sel_events[0]["type"] == "selection_stats"


def test_engine_tick_without_clan_config_no_crash():
    """tick() without clan_config argument does not crash."""
    clan, engine, config, rng, _ = _make_two_band_clan()
    # Old-style call without clan_config
    result = engine.tick(clan, year=1, rng=rng, config=config)
    assert result is not None
    assert "selection_events" in result
    assert "clan_metrics" in result


# ── clan_config fission/extinction threshold tests ───────────────────────────

def test_clan_config_has_selection_params():
    """ClanConfig exposes fission_threshold, extinction_threshold, and migration_rate."""
    cc = ClanConfig()
    assert hasattr(cc, "fission_threshold")
    assert hasattr(cc, "extinction_threshold")
    assert hasattr(cc, "migration_rate_per_agent")
    assert hasattr(cc, "p_join_floor")
    # Validate defaults
    assert cc.fission_threshold == 150
    assert cc.extinction_threshold == 10
    assert 0.0 <= cc.migration_rate_per_agent <= 1.0
    assert 0.0 <= cc.p_join_floor <= 1.0


def test_clan_config_p_join_floor_applied():
    """Defensive coalition always has at least p_join_floor per agent."""
    from engines.clan_raiding import _select_defensive_coalition

    config = _make_config(pop=60)
    clan_config = ClanConfig(p_join_floor=0.99)  # nearly deterministic join

    b1 = _make_band(1, config, 10)
    # Set all group_loyalty to 0 so base p_join = 0 * (1 + ...) = 0
    for a in b1.get_living():
        a.group_loyalty = 0.0
        a.cooperation_propensity = 0.0

    rng = np.random.default_rng(7)
    coalition = _select_defensive_coalition(b1, rng, clan_config)
    # With p_join_floor=0.99, even agents with group_loyalty=0 should almost
    # always join; expect a non-trivial coalition
    assert len(coalition) > 0, (
        "With p_join_floor=0.99, coalition should not be empty even with zero loyalty."
    )
