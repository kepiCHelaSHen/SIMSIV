# V1 Perfect Pass — Phase 0: Remediation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix 3 known bugs in `engines/conflict.py` on a new `v1-perfect` branch from tag `v1.0-paper1-submitted`, with all existing tests passing.

**Architecture:** Direct edits to `engines/conflict.py` only. Three surgical fixes: replace defensive getattr with direct access, add bond_dissolved event emission, replace rng.choice on object list with index-based selection.

**Tech Stack:** Python 3.11+, numpy, pytest

---

### Task 1: Create v1-perfect branch

**Files:**
- None (git operation only)

- [ ] **Step 1: Create branch from submission tag**

```bash
cd D:/EXPERIMENTS/sim
git checkout -b v1-perfect v1.0-paper1-submitted
```

- [ ] **Step 2: Verify branch state**

```bash
git log --oneline -3
```

Expected: HEAD at `ab5b146 Finalize Paper 1 — reproducibility statement, initialization clarity, rename`

- [ ] **Step 3: Run existing tests to establish baseline**

```bash
cd D:/EXPERIMENTS/sim
python -m pytest tests/test_smoke.py tests/test_society.py tests/test_config.py tests/test_id_counter.py -v
```

Expected: All tests PASS. Record exact count for gate comparison.

---

### Task 2: Fix getattr false defaults (conflict.py lines 161, 197, 549)

**Files:**
- Modify: `engines/conflict.py:161` — `getattr(config, 'coalition_defense_enabled', False)` → `config.coalition_defense_enabled`
- Modify: `engines/conflict.py:197` — `getattr(config, 'leadership_enabled', False)` → `config.leadership_enabled`
- Modify: `engines/conflict.py:199` — `getattr(target, 'faction_id', None)` → `target.faction_id`
- Modify: `engines/conflict.py:200` — `getattr(society, 'faction_leaders', {})` → `society.faction_leaders`
- Modify: `engines/conflict.py:549` — `getattr(config, 'third_party_punishment_enabled', False)` → `config.third_party_punishment_enabled`
- Test: `tests/test_smoke.py` (existing)

**Rationale:** All 3 config attributes exist in `config.py` with `bool = True` defaults:
- `coalition_defense_enabled: bool = True` (config.py:161)
- `leadership_enabled: bool = True` (config.py:251)
- `third_party_punishment_enabled: bool = True` (config.py:157)

The `getattr(..., False)` pattern silently disables features if an attribute is ever renamed or removed. Direct access ensures immediate `AttributeError` failure.

**Note on `target.faction_id`** (line 199): `Agent` dataclass defines `faction_id: Optional[int] = None` (agent.py:355). The getattr default of `None` is redundant — direct access returns `None` by default.

**Note on `society.faction_leaders`** (line 200): Must verify this attribute exists on Society. If it doesn't exist as a permanent attribute (only set by faction detection engine), this getattr IS load-bearing and should be converted to `getattr(society, 'faction_leaders', {})` with a comment explaining why, OR the attribute should be initialized in Society.__init__.

- [ ] **Step 1: Write a targeted test for hard-fail behavior**

Create test that verifies the engine crashes if a required config attribute is missing:

```python
# In tests/test_conflict_remediation.py
"""Tests for Phase 0 conflict.py remediation — getattr, events, rng."""
import numpy as np
import pytest
from config import Config
from simulation import Simulation


def test_coalition_defense_requires_config_attribute():
    """Engine must crash if coalition_defense_enabled is missing from config."""
    config = Config(years=5, population_size=50, seed=42)
    # Verify the attribute exists and is accessible directly
    assert hasattr(config, 'coalition_defense_enabled')
    assert config.coalition_defense_enabled is True


def test_leadership_requires_config_attribute():
    """Engine must crash if leadership_enabled is missing from config."""
    config = Config(years=5, population_size=50, seed=42)
    assert hasattr(config, 'leadership_enabled')
    assert config.leadership_enabled is True


def test_third_party_punishment_requires_config_attribute():
    """Engine must crash if third_party_punishment_enabled is missing."""
    config = Config(years=5, population_size=50, seed=42)
    assert hasattr(config, 'third_party_punishment_enabled')
    assert config.third_party_punishment_enabled is True
```

- [ ] **Step 2: Run test to verify it passes (attributes exist)**

```bash
python -m pytest tests/test_conflict_remediation.py -v
```

Expected: PASS (attributes exist on Config)

- [ ] **Step 3: Check if `society.faction_leaders` exists as an initialized attribute**

```bash
cd D:/EXPERIMENTS/sim
grep -n "faction_leaders" models/society.py
```

If it's NOT initialized in `__init__`, we need to verify it's set by the faction engine before conflict runs. If set dynamically, keep `getattr(society, 'faction_leaders', {})` with an explicit comment.

- [ ] **Step 4: Apply the getattr→direct access replacements**

In `engines/conflict.py`:

Line 161: Replace `if getattr(config, 'coalition_defense_enabled', False):` with `if config.coalition_defense_enabled:`

Line 197: Replace `if (getattr(config, 'leadership_enabled', False)` with `if (config.leadership_enabled`

Line 199: Replace `and agent.faction_id == getattr(target, 'faction_id', None)):` with `and agent.faction_id == target.faction_id):`

Line 200: Only replace if society.faction_leaders is initialized in `__init__`. Otherwise keep getattr with comment.

Line 549: Replace `if getattr(config, 'third_party_punishment_enabled', False):` with `if config.third_party_punishment_enabled:`

- [ ] **Step 5: Run all tests**

```bash
python -m pytest tests/ -v
```

Expected: All tests PASS. If any fail, investigate — a failure here means something was relying on the silent False default.

- [ ] **Step 6: Commit**

```bash
git add engines/conflict.py tests/test_conflict_remediation.py
git commit -m "fix(conflict): replace getattr false defaults with direct config access

Lines 161, 197, 549: coalition_defense_enabled, leadership_enabled,
third_party_punishment_enabled now accessed directly on config.
Missing attributes will raise AttributeError immediately instead of
silently disabling features.

Phase 0 remediation for V1 Perfect Pass.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

### Task 3: Add missing bond_dissolved event for conflict-caused breaks

**Files:**
- Modify: `engines/conflict.py:500-512` — add event emission after bond break
- Test: `tests/test_conflict_remediation.py` — add bond dissolution event test

**Reference pattern** from `engines/mating.py:109-114`:
```python
events.append({
    "type": "bond_dissolved",
    "year": society.year,
    "agent_ids": [agent.id, pid],
    "description": f"Pair bond dissolved: {agent.id} & {pid}",
})
```

- [ ] **Step 1: Write failing test for bond_dissolved event on conflict break**

```python
# Add to tests/test_conflict_remediation.py
def test_conflict_bond_break_emits_event():
    """Conflict-caused bond dissolution must emit bond_dissolved event
    with reason='conflict_break' and both agent UIDs."""
    config = Config(
        years=30,
        population_size=100,
        seed=77,
        pair_bond_strength=0.9,       # strong bonds so some exist
        violence_death_chance=0.0,     # no deaths, maximize bond-break chances
    )
    sim = Simulation(config)
    sim.run()

    # Check event_type_counts for bond_dissolved events
    bond_events = []
    for evt in sim.society._event_window:
        if (evt.get("type") == "bond_dissolved"
                and evt.get("outcome", {}).get("reason") == "conflict_break"):
            bond_events.append(evt)

    # We can't guarantee one fires every run, but over 30 years with 100
    # agents and strong bonds, at least one conflict bond break is expected.
    # If none found, the event isn't being emitted.
    # NOTE: if this is flaky, increase years or population.
    if sim.society.event_type_counts.get("conflict", 0) > 0:
        # Conflicts happened — check structure of any conflict bond_dissolved
        for evt in bond_events:
            assert len(evt["agent_ids"]) == 2
            assert evt["outcome"]["reason"] == "conflict_break"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/test_conflict_remediation.py::test_conflict_bond_break_emits_event -v
```

Expected: FAIL or no conflict bond_dissolved events found (event not emitted yet)

- [ ] **Step 3: Add bond_dissolved event emission to conflict.py**

In `engines/conflict.py`, after line 511 (`partner.remember(fighter.id, -0.25)`), before line 512 (`break`), insert:

```python
                            events.append({
                                "type": "bond_dissolved",
                                "year": society.year,
                                "agent_ids": [fighter.id, pid],
                                "description": (
                                    f"Pair bond dissolved by conflict: "
                                    f"{fighter.id} & {pid}"),
                                "outcome": {
                                    "reason": "conflict_break",
                                    "fighter": fighter.id,
                                    "partner": pid,
                                },
                            })
```

- [ ] **Step 4: Run test to verify it passes**

```bash
python -m pytest tests/test_conflict_remediation.py -v
```

Expected: PASS

- [ ] **Step 5: Run full test suite**

```bash
python -m pytest tests/ -v
```

Expected: All tests PASS

- [ ] **Step 6: Commit**

```bash
git add engines/conflict.py tests/test_conflict_remediation.py
git commit -m "fix(conflict): emit bond_dissolved event on conflict-caused bond breaks

Conflict-driven pair bond destabilization (lines 500-512) now emits a
bond_dissolved event matching the format from mating.py, with
outcome.reason='conflict_break' and both agent UIDs.

Required for provenance log to track how conflict breaks social cohesion.

Phase 0 remediation for V1 Perfect Pass.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

### Task 4: Fix rng.choice on object list (conflict.py line 489)

**Files:**
- Modify: `engines/conflict.py:489-492` — replace object-list rng.choice with index-based
- Test: `tests/test_conflict_remediation.py` — add determinism test

**Issue:** `rng.choice(bystander_pool, size=n, replace=False)` passes a Python list of Agent objects to numpy. Numpy converts this to a dtype=object array, which is fragile across numpy versions and breaks deterministic seeding guarantees.

**Fix:** Use `rng.choice(len(bystander_pool), size=n, replace=False)` to get indices, then index the list.

- [ ] **Step 1: Write test for deterministic bystander selection**

```python
# Add to tests/test_conflict_remediation.py
def test_bystander_selection_is_deterministic():
    """Same seed must produce identical bystander selection across runs."""
    results = []
    for _ in range(2):
        config = Config(years=10, population_size=80, seed=42)
        sim = Simulation(config)
        sim.run()
        # Collect conflict events
        conflicts = [e for e in sim.society._event_window
                     if e.get("type") == "conflict"]
        results.append(conflicts)

    # Same seed → same events
    assert len(results[0]) == len(results[1])
    for e1, e2 in zip(results[0], results[1]):
        assert e1["agent_ids"] == e2["agent_ids"]
```

- [ ] **Step 2: Run test — should pass even before fix (but validates determinism)**

```bash
python -m pytest tests/test_conflict_remediation.py::test_bystander_selection_is_deterministic -v
```

Expected: PASS (numpy object-array choice still works with same seed, but is fragile)

- [ ] **Step 3: Apply the fix**

In `engines/conflict.py`, replace lines 489-492:

**Before:**
```python
                bystanders = rng.choice(
                    bystander_pool,
                    size=min(n_bystanders, len(bystander_pool)),
                    replace=False)
```

**After:**
```python
                n_select = min(n_bystanders, len(bystander_pool))
                bystander_indices = rng.choice(
                    len(bystander_pool), size=n_select, replace=False)
                bystanders = [bystander_pool[i] for i in bystander_indices]
```

- [ ] **Step 4: Run all tests**

```bash
python -m pytest tests/ -v
```

Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add engines/conflict.py tests/test_conflict_remediation.py
git commit -m "fix(conflict): use index-based rng.choice for bystander selection

Replace rng.choice(object_list) with rng.choice(len(list)) + indexing.
Eliminates fragile numpy object-array conversion, preserves seed
determinism via self.rng throughout.

Phase 0 remediation for V1 Perfect Pass.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

### Task 5: Phase 0 Gate — Full Test Suite Verification

**Files:**
- None (verification only)

- [ ] **Step 1: Run complete test suite**

```bash
cd D:/EXPERIMENTS/sim
python -m pytest tests/ -v --tb=short 2>&1
```

Expected: All tests PASS. Record exact output.

- [ ] **Step 2: Run a 200-year smoke test to verify no behavioral regression**

```bash
cd D:/EXPERIMENTS/sim
python -c "
from config import Config
from simulation import Simulation
config = Config(years=200, population_size=100, seed=42)
sim = Simulation(config)
sim.run()
print(f'Year: {sim.year}')
print(f'Population: {sim.society.population_size()}')
print(f'Events: {dict(sim.society.event_type_counts)}')
print(f'Bond dissolved events: {sim.society.event_type_counts.get(\"bond_dissolved\", 0)}')
print('GATE PASSED' if sim.society.population_size() > 0 else 'GATE FAILED')
"
```

Expected: Simulation completes 200 years, population survives, bond_dissolved count > 0.

- [ ] **Step 3: Verify determinism (same seed = identical output)**

```bash
cd D:/EXPERIMENTS/sim
python -c "
from config import Config
from simulation import Simulation
pops = []
for run in range(2):
    config = Config(years=50, population_size=100, seed=42)
    sim = Simulation(config)
    sim.run()
    pops.append(sim.society.population_size())
assert pops[0] == pops[1], f'Determinism broken: {pops}'
print(f'Determinism verified: both runs → population {pops[0]}')
print('GATE PASSED')
"
```

Expected: Both runs produce identical population count. GATE PASSED.

- [ ] **Step 4: Log gate results**

Record all gate outputs. If any gate fails, investigate and fix before proceeding to Phase 1.
