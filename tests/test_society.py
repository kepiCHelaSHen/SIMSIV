"""Tests for Society model correctness — event window, partner index."""
import numpy as np
import pytest
from config import Config
from models.society import Society


def _make_society(n=30, seed=1):
    cfg = Config(population_size=n, years=1, seed=seed)
    rng = np.random.default_rng(seed)
    return Society(cfg, rng), cfg, rng


def test_event_window_does_not_exceed_cap():
    soc, _, _ = _make_society()
    for i in range(2000):
        soc.add_event({"type": "test", "description": f"e{i}"})
    assert len(soc._event_window) <= soc._event_window_size


def test_event_type_counts_accumulate_without_cap():
    soc, _, _ = _make_society()
    for _ in range(1000):
        soc.add_event({"type": "birth"})
    for _ in range(500):
        soc.add_event({"type": "death"})
    assert soc.event_type_counts["birth"] == 1000
    assert soc.event_type_counts["death"] == 500


def test_event_window_preserves_most_recent():
    soc, _, _ = _make_society()
    soc._event_window_size = 5
    for i in range(10):
        soc.add_event({"type": "test", "n": i})
    ns = [e["n"] for e in soc._event_window]
    assert ns == [5, 6, 7, 8, 9], f"Expected last 5 events, got {ns}"


def test_partner_index_bond_creation():
    soc, _, _ = _make_society()
    living = soc.get_living()
    a, b = living[0], living[1]
    soc._index_bond(a.id, b.id)
    assert b.id in soc.get_partners_of(a.id)
    assert a.id in soc.get_partners_of(b.id)


def test_partner_index_bond_removal():
    soc, _, _ = _make_society()
    living = soc.get_living()
    a, b = living[0], living[1]
    soc._index_bond(a.id, b.id)
    soc._unindex_bond(a.id, b.id)
    assert b.id not in soc.get_partners_of(a.id)
    assert a.id not in soc.get_partners_of(b.id)


def test_partner_index_get_unknown_returns_empty():
    soc, _, _ = _make_society()
    result = soc.get_partners_of(999999)
    assert result == set()


def test_purge_dead_from_ledgers():
    soc, _, _ = _make_society()
    living = soc.get_living()
    # Manually pollute a ledger with a fake dead ID
    living[1].reputation_ledger[99999] = 0.7
    living[2].reputation_ledger[99999] = 0.3
    soc.purge_dead_from_ledgers({99999})
    assert 99999 not in living[1].reputation_ledger
    assert 99999 not in living[2].reputation_ledger
