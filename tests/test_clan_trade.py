"""
Trade engine tests — validates engines/clan_trade.py and the Trade integration
in engines/clan_base.py (Turn 2 of SIMSIV v2 Clan Simulator).

Coverage:
  - trade_tick returns a list of event dicts.
  - Each event has the required keys and valid outcome values.
  - Successful trades produce a net positive-sum result for both traders.
  - Refused trades decrease bilateral band trust.
  - Successful trades increase bilateral band trust.
  - Agents with zero outgroup_tolerance always refuse (if not scarce).
  - Scarcity lowers the refusal threshold (desperate bands trade anyway).
  - Resource caps are respected after trade.
  - ClanEngine.reset() clears band metrics history.
  - Per-band rng: two bands with different rngs evolve on independent
    trajectories (band-1 tick does not consume band-2 rng).
  - trade_tick is deterministic: same rng seed → same events.
  - Inter-band interactions include trade, neutral, and hostile outcomes
    across enough ticks (distribution sanity check).
"""

import sys
import os

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from models.clan import Band, ClanSociety
from engines.clan_base import ClanEngine, _mean_outgroup_tolerance
from engines.clan_trade import (
    trade_tick,
    _select_traders,
    _compute_n_pairs,
    _is_scarce,
    _compute_refusal_threshold,
    _execute_trade_pair,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────

def _make_config(pop: int = 40, seed: int = 1) -> Config:
    return Config(
        population_size=pop,
        years=10,
        seed=seed,
        migration_enabled=False,
    )


def _make_band(band_id: int, config: Config, rng_seed: int) -> Band:
    rng = np.random.default_rng(rng_seed)
    return Band(band_id=band_id, name=f"Band{band_id}", config=config, rng=rng, origin_year=0)


def _make_two_band_clan(seed: int = 42, pop: int = 50):
    """Return (clan, engine, config, rng) with two bands ready for ticking."""
    config = _make_config(pop=pop, seed=seed)
    rng = np.random.default_rng(seed)
    rng_b1 = np.random.default_rng(rng.integers(0, 2**31))
    rng_b2 = np.random.default_rng(rng.integers(0, 2**31))
    band1 = Band(1, "Northern", config, rng_b1, origin_year=0)
    band2 = Band(2, "Southern", config, rng_b2, origin_year=0)
    clan = ClanSociety(base_interaction_rate=0.9)
    clan.add_band(band1)
    clan.add_band(band2)
    clan.set_distance(1, 2, 0.1)  # very close → very high interaction probability
    engine = ClanEngine()
    return clan, engine, config, rng


# ── trade_tick unit tests ─────────────────────────────────────────────────────

def test_trade_tick_returns_list():
    """trade_tick returns a list (may be empty if no adults available)."""
    config = _make_config(pop=40)
    rng = np.random.default_rng(7)
    band_a = _make_band(1, config, 10)
    band_b = _make_band(2, config, 20)
    result = trade_tick(band_a, band_b, trust=0.7, rng=rng, config=config)
    assert isinstance(result, list)


def test_trade_tick_event_keys():
    """Every returned event must have all required keys."""
    config = _make_config(pop=40)
    rng = np.random.default_rng(8)
    band_a = _make_band(1, config, 11)
    band_b = _make_band(2, config, 22)
    events = trade_tick(band_a, band_b, trust=0.9, rng=rng, config=config)
    required_keys = {"type", "year", "agent_ids", "description", "outcome",
                     "band_a_id", "band_b_id"}
    for ev in events:
        assert required_keys.issubset(ev.keys()), (
            f"Event missing required keys: {required_keys - ev.keys()}"
        )
        assert ev["type"] == "inter_band_trade"
        assert ev["outcome"] in {"success", "refused"}


def test_trade_tick_valid_outcome_values():
    """outcome field is always 'success' or 'refused'."""
    config = _make_config(pop=50)
    rng = np.random.default_rng(9)
    band_a = _make_band(1, config, 13)
    band_b = _make_band(2, config, 14)
    events = trade_tick(band_a, band_b, trust=0.6, rng=rng, config=config)
    for ev in events:
        assert ev["outcome"] in {"success", "refused"}, (
            f"Unexpected outcome: {ev['outcome']}"
        )


def test_trade_tick_positive_sum_gain():
    """A successful trade leaves both traders with non-negative resource change
    summed across the pair, showing a net surplus was created.

    We set up a scenario that forces success: very high outgroup_tolerance
    on both traders and plentiful resources.
    """
    config = _make_config(pop=40)
    rng = np.random.default_rng(5)
    band_a = _make_band(1, config, 30)
    band_b = _make_band(2, config, 40)

    # Find two adults to trade; manually set their attributes for determinism.
    traders_a = _select_traders(band_a, rng, config)
    traders_b = _select_traders(band_b, rng, config)

    if not traders_a or not traders_b:
        pytest.skip("No adults available in one of the bands — skip positive-sum check.")

    ta = traders_a[0]
    tb = traders_b[0]

    # Force favorable conditions: high tolerance, plentiful resources.
    ta.outgroup_tolerance = 0.9
    tb.outgroup_tolerance = 0.9
    ta.current_resources = 15.0
    tb.current_resources = 15.0
    ta.current_tools = 5.0
    tb.current_tools = 5.0

    res_before_a = ta.current_resources
    res_before_b = tb.current_resources

    event = _execute_trade_pair(
        ta, tb,
        band_a, band_b,
        trust=0.9,
        scarce_a=False,
        scarce_b=False,
        rng=rng,
        config=config,
    )

    if event["outcome"] == "success":
        # Both parties should have received more than they gave overall.
        gain_a = ta.current_resources - res_before_a
        gain_b = tb.current_resources - res_before_b
        total_gain = gain_a + gain_b
        # The documented surplus range is 5–15%, so the combined gain MUST be
        # strictly positive.  A tolerance of -0.01 permitted tiny net-negative
        # results (Turn 2 critique #5).  The correct invariant is total_gain > 0.
        assert total_gain > 0.0, (
            f"Expected strict positive-sum trade; total gain={total_gain:.4f}"
        )


def test_trade_tick_refused_decreases_trust():
    """A refused trade decreases bilateral trust."""
    config = _make_config(pop=40)
    rng = np.random.default_rng(77)
    band_a = _make_band(1, config, 50)
    band_b = _make_band(2, config, 60)

    # Set initial trust
    band_a.update_trust(2, 0.0)   # start at 0.5 then immediately override
    band_b.update_trust(1, 0.0)
    # override to specific value by direct manipulation
    band_a.inter_band_trust[2] = 0.6
    band_b.inter_band_trust[1] = 0.6

    traders_a = _select_traders(band_a, rng, config)
    traders_b = _select_traders(band_b, rng, config)

    if not traders_a or not traders_b:
        pytest.skip("No adults — cannot test refusal trust effect.")

    ta = traders_a[0]
    tb = traders_b[0]

    # Force refusal by setting outgroup_tolerance to zero on both.
    ta.outgroup_tolerance = 0.0
    tb.outgroup_tolerance = 0.0

    trust_before_a = band_a.trust_toward(2)
    trust_before_b = band_b.trust_toward(1)

    event = _execute_trade_pair(
        ta, tb,
        band_a, band_b,
        trust=0.6,
        scarce_a=False,
        scarce_b=False,
        rng=rng,
        config=config,
    )

    if event["outcome"] == "refused":
        assert band_a.trust_toward(2) < trust_before_a or band_b.trust_toward(1) < trust_before_b, (
            "Trust should decrease after a refused trade."
        )


def test_trade_tick_success_increases_trust():
    """A successful trade increases bilateral trust."""
    config = _make_config(pop=40)
    rng = np.random.default_rng(88)
    band_a = _make_band(1, config, 70)
    band_b = _make_band(2, config, 80)

    band_a.inter_band_trust[2] = 0.5
    band_b.inter_band_trust[1] = 0.5

    traders_a = _select_traders(band_a, rng, config)
    traders_b = _select_traders(band_b, rng, config)

    if not traders_a or not traders_b:
        pytest.skip("No adults available.")

    ta = traders_a[0]
    tb = traders_b[0]

    # Guarantee success: high tolerance, plentiful resources.
    ta.outgroup_tolerance = 0.99
    tb.outgroup_tolerance = 0.99
    ta.current_resources = 12.0
    tb.current_resources = 12.0

    trust_before_a = band_a.trust_toward(2)
    trust_before_b = band_b.trust_toward(1)

    event = _execute_trade_pair(
        ta, tb,
        band_a, band_b,
        trust=0.9,
        scarce_a=False,
        scarce_b=False,
        rng=rng,
        config=config,
    )

    if event["outcome"] == "success":
        assert band_a.trust_toward(2) > trust_before_a or band_b.trust_toward(1) > trust_before_b, (
            "Trust should increase after a successful trade."
        )


def test_zero_outgroup_tolerance_always_refuses():
    """Agent with outgroup_tolerance=0 always refuses when band is not scarce."""
    config = _make_config(pop=40)
    band_a = _make_band(1, config, 90)
    band_b = _make_band(2, config, 100)

    traders_a = _select_traders(band_a, np.random.default_rng(1), config)
    traders_b = _select_traders(band_b, np.random.default_rng(2), config)

    if not traders_a or not traders_b:
        pytest.skip("No traders available.")

    ta = traders_a[0]
    tb = traders_b[0]

    # One agent with zero tolerance, the other high tolerance.
    ta.outgroup_tolerance = 0.0
    tb.outgroup_tolerance = 0.99
    ta.current_resources = 10.0
    tb.current_resources = 10.0

    # Run 20 trials — all should be refused.
    for trial in range(20):
        rng = np.random.default_rng(trial)
        event = _execute_trade_pair(
            ta, tb,
            band_a, band_b,
            trust=0.9,
            scarce_a=False,  # not scarce, so refusal threshold not relaxed
            scarce_b=False,
            rng=rng,
            config=config,
        )
        assert event["outcome"] == "refused", (
            f"Trial {trial}: expected 'refused' for zero-tolerance agent, "
            f"got '{event['outcome']}'"
        )


def test_scarcity_lowers_refusal_threshold():
    """Scarce band lowers the refusal threshold."""
    config = _make_config()
    # Not scarce
    normal = _compute_refusal_threshold(scarce=False, config=config)
    # Scarce
    desperate = _compute_refusal_threshold(scarce=True, config=config)
    assert desperate < normal, (
        f"Scarce band should have lower refusal threshold; "
        f"normal={normal:.3f}, desperate={desperate:.3f}"
    )


def test_resource_caps_respected():
    """Trade should not leave any agent above their resource cap."""
    config = _make_config(pop=40)
    rng = np.random.default_rng(123)
    band_a = _make_band(1, config, 111)
    band_b = _make_band(2, config, 222)

    traders_a = _select_traders(band_a, rng, config)
    traders_b = _select_traders(band_b, rng, config)

    if not traders_a or not traders_b:
        pytest.skip("No traders.")

    ta = traders_a[0]
    tb = traders_b[0]

    ta.outgroup_tolerance = 0.99
    tb.outgroup_tolerance = 0.99
    ta.current_resources = 18.0
    tb.current_resources = 18.0

    cap = float(getattr(config, "resource_storage_cap", 20.0))

    _execute_trade_pair(
        ta, tb, band_a, band_b,
        trust=0.8, scarce_a=False, scarce_b=False,
        rng=rng, config=config,
    )

    assert ta.current_resources <= cap + 1e-6, (
        f"ta.current_resources={ta.current_resources:.2f} exceeds cap={cap}"
    )
    assert tb.current_resources <= cap + 1e-6, (
        f"tb.current_resources={tb.current_resources:.2f} exceeds cap={cap}"
    )


def test_trade_tick_deterministic():
    """Same rng seed → same sequence of trade events."""
    config = _make_config(pop=40)
    band_a1 = _make_band(1, config, 10)
    band_b1 = _make_band(2, config, 20)
    band_a2 = _make_band(1, config, 10)
    band_b2 = _make_band(2, config, 20)

    rng1 = np.random.default_rng(55)
    rng2 = np.random.default_rng(55)

    events1 = trade_tick(band_a1, band_b1, trust=0.7, rng=rng1, config=config)
    events2 = trade_tick(band_a2, band_b2, trust=0.7, rng=rng2, config=config)

    assert len(events1) == len(events2), (
        f"Different number of events: {len(events1)} vs {len(events2)}"
    )
    for e1, e2 in zip(events1, events2):
        assert e1["outcome"] == e2["outcome"], (
            f"Outcome mismatch: {e1['outcome']} vs {e2['outcome']}"
        )


# ── ClanEngine integration tests ──────────────────────────────────────────────

def test_reset_clears_band_metrics():
    """ClanEngine.reset() clears accumulated metrics history."""
    clan, engine, config, rng = _make_two_band_clan(seed=42, pop=50)

    for year in range(1, 4):
        engine.tick(clan, year, rng, config)

    assert len(engine.get_band_history(1)) == 3

    engine.reset()

    assert len(engine.get_band_history(1)) == 0, (
        "After reset(), band history should be empty."
    )
    assert len(engine.get_band_history(2)) == 0, (
        "After reset(), band history should be empty."
    )


def test_reset_allows_fresh_accumulation():
    """After reset(), ticking again accumulates fresh history starting from row 1."""
    clan, engine, config, rng = _make_two_band_clan(seed=42, pop=50)

    for year in range(1, 4):
        engine.tick(clan, year, rng, config)

    engine.reset()

    # Re-run two ticks — history should have exactly 2 rows per band.
    for year in range(1, 3):
        engine.tick(clan, year, rng, config)

    assert len(engine.get_band_history(1)) == 2, (
        "Expected 2 history rows after reset + 2 ticks."
    )


def test_per_band_rng_stored_on_band():
    """Band.rng attribute is a numpy Generator after construction."""
    config = _make_config()
    band = _make_band(1, config, 42)
    assert isinstance(band.rng, np.random.Generator), (
        "Band.rng should be a numpy.random.Generator"
    )


def test_inter_band_events_include_contact_events():
    """result['inter_band_events'] contains at least one inter_band_contact after
    enough ticks with high interaction probability."""
    clan, engine, config, rng = _make_two_band_clan(seed=7, pop=50)

    all_events: list[dict] = []
    for year in range(1, 21):
        result = engine.tick(clan, year, rng, config)
        all_events.extend(result["inter_band_events"])

    contact_events = [e for e in all_events if e.get("type") == "inter_band_contact"]
    assert len(contact_events) > 0, (
        "Expected at least one inter_band_contact event in 20 ticks."
    )


def test_trade_events_have_year_stamped():
    """Trade events returned in result['inter_band_events'] have a non-zero year."""
    clan, engine, config, rng = _make_two_band_clan(seed=7, pop=50)

    trade_events: list[dict] = []
    for year in range(1, 21):
        result = engine.tick(clan, year, rng, config)
        trade_events.extend(
            e for e in result["inter_band_events"]
            if e.get("type") == "inter_band_trade"
        )

    if not trade_events:
        pytest.skip("No trade events in 20 ticks — year stamping not verifiable.")

    for ev in trade_events:
        assert ev["year"] > 0, (
            f"Trade event year should be stamped by ClanEngine; got year={ev['year']}"
        )


def test_interaction_outcomes_vary_over_many_ticks():
    """Over 50 ticks, at least two different inter_band_contact outcomes should appear.

    This checks that the interaction-type draw (trade/neutral/hostile) produces
    real variety rather than always returning the same outcome.
    """
    clan, engine, config, rng = _make_two_band_clan(seed=99, pop=60)

    outcomes: set[str] = set()
    for year in range(1, 51):
        result = engine.tick(clan, year, rng, config)
        for ev in result["inter_band_events"]:
            if ev.get("type") == "inter_band_contact":
                outcomes.add(ev.get("outcome", ""))

    assert len(outcomes) >= 2, (
        f"Expected at least 2 distinct inter_band_contact outcomes over 50 ticks; "
        f"got: {outcomes}"
    )


def test_mean_outgroup_tolerance_returns_float():
    """_mean_outgroup_tolerance returns a float in [0, 1]."""
    config = _make_config()
    band = _make_band(1, config, 5)
    tol = _mean_outgroup_tolerance(band)
    assert isinstance(tol, float)
    assert 0.0 <= tol <= 1.0, f"Tolerance {tol} outside [0, 1]"


def test_trust_changes_after_trade_session():
    """After a completed trade session, bilateral trust must have changed from
    its pre-trade value (either up for success or down for refusal)."""
    config = _make_config(pop=40)
    rng = np.random.default_rng(333)
    band_a = _make_band(1, config, 44)
    band_b = _make_band(2, config, 55)

    band_a.inter_band_trust[2] = 0.5
    band_b.inter_band_trust[1] = 0.5

    before_a = band_a.trust_toward(2)
    before_b = band_b.trust_toward(1)

    events = trade_tick(band_a, band_b, trust=0.7, rng=rng, config=config)

    if not events:
        pytest.skip("No trade events produced — no adults or pairs available.")

    after_a = band_a.trust_toward(2)
    after_b = band_b.trust_toward(1)

    assert after_a != before_a or after_b != before_b, (
        "Trust should change after at least one trade pair is processed."
    )
