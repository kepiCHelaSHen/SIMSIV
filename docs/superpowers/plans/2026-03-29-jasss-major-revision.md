# JASSS Major Revision Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement 4 architectural requirements from JASSS reviewer report: parameter parity, MA trait locking, O(1) event handling, and selection differential logging.

**Architecture:** Four independent changes to config.py, models/agent.py, models/society.py, and metrics/collectors.py. Each is testable in isolation. TDD throughout.

**Tech Stack:** Python 3.11+, numpy, pytest, collections.deque

---

## File Map

| File | Change | Responsibility |
|------|--------|----------------|
| `config.py` | Task 1: Overwrite 34 defaults with AutoSIM Run 3 values | Parameter parity |
| `models/agent.py:626-707` | Task 2: Add MA trait-lock bypass in `breed()` | Trait isolation |
| `models/society.py:26,78-85` | Task 3: Replace list with `deque(maxlen=)` | O(1) event handling |
| `metrics/collectors.py` | Task 4: Add Breeder's Equation metrics to `collect()` | Selection differential |
| `tests/test_jasss_revision.py` | Tasks 1-4: All tests | Regression + correctness |

---

### Task 1: Parameter Parity (config.py)

**Files:**
- Modify: `config.py` — 34 dataclass field defaults
- Test: `tests/test_jasss_revision.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_jasss_revision.py
"""Tests for JASSS Major Revision architectural requirements."""
import numpy as np
import pytest
import yaml
from config import Config


def test_config_defaults_match_autosim_best():
    """Every AutoSIM-calibrated parameter must match best_config.yaml."""
    cfg = Config()
    with open("autosim/best_config.yaml") as f:
        best = yaml.safe_load(f)["parameters"]

    mismatches = []
    for param, best_val in best.items():
        cfg_val = getattr(cfg, param, "MISSING")
        if cfg_val == "MISSING":
            mismatches.append(f"{param}: MISSING from Config")
        elif abs(float(cfg_val) - float(best_val)) > 0.0001:
            mismatches.append(f"{param}: config={cfg_val}, best={best_val}")

    assert not mismatches, (
        f"{len(mismatches)} parameter mismatches:\n" +
        "\n".join(mismatches))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_jasss_revision.py::test_config_defaults_match_autosim_best -v`
Expected: FAIL with 34 mismatches

- [ ] **Step 3: Overwrite config.py defaults**

In `config.py`, update these 34 dataclass fields to their AutoSIM Run 3 calibrated values (maintain type hints and comments):

```python
    resource_equal_floor: float = 0.4
    resource_abundance: float = 0.984895
    aggression_production_penalty: float = 0.6
    cooperation_network_bonus: float = 0.059346
    cooperation_sharing_rate: float = 0.124631
    wealth_diminishing_power: float = 0.736977
    subsistence_floor: float = 1.17297
    scarcity_severity: float = 0.3
    child_investment_per_year: float = 0.349974
    conflict_base_probability: float = 0.15
    violence_cost_health: float = 0.176399
    violence_death_chance: float = 0.115422
    violence_cost_resources: float = 0.14208
    flee_threshold: float = 0.293889
    seasonal_conflict_boost: float = 0.29409
    pair_bond_dissolution_rate: float = 0.02
    pair_bond_strength: float = 0.679299
    base_conception_chance: float = 0.8
    female_choice_strength: float = 0.339674
    infidelity_base_rate: float = 0.034349
    maternal_age_fertility_decline: float = 0.033
    maternal_health_cost: float = 0.027407
    birth_interval_years: int = 2
    age_first_reproduction: int = 14
    age_max_reproduction_female: int = 49
    orphan_mortality_multiplier: float = 1.2
    grandparent_survival_bonus: float = 0.083311
    widowhood_mourning_years: int = 0
    mortality_base: float = 0.006212
    childhood_mortality_annual: float = 0.054119
    health_decay_per_year: float = 0.01025
    epidemic_base_probability: float = 0.029977
    epidemic_lethality_base: float = 0.254318
    male_risk_mortality_multiplier: float = 2.120117
    childbirth_mortality_rate: float = 0.01
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_jasss_revision.py::test_config_defaults_match_autosim_best -v`
Expected: PASS

- [ ] **Step 5: Run full test suite for regression**

Run: `python -m pytest tests/ -v`
Expected: All tests pass (some numeric outputs may shift due to new defaults — update any hardcoded expected values)

- [ ] **Step 6: Commit**

```bash
git add config.py tests/test_jasss_revision.py
git commit -m "fix(config): snap 34 defaults to AutoSIM Run 3 calibrated values

JASSS Requirement 1: Parameter Parity. All dataclass defaults now
match autosim/best_config.yaml. Source code reflects the calibrated
'Perfect' model state. Type hints and validation preserved."
```

---

### Task 2: MA Trait Locking in breed() (models/agent.py)

**Files:**
- Modify: `models/agent.py:696-704` — add `_is_ma` check before mutation
- Test: `tests/test_jasss_revision.py`

- [ ] **Step 1: Write the failing test**

```python
# Add to tests/test_jasss_revision.py
from models.agent import Agent, Sex, breed, create_initial_population, IdCounter, HERITABLE_TRAITS


def test_ma_offspring_inherit_exact_genotype():
    """MA parents must pass exact genotype — no mutation drift."""
    rng = np.random.default_rng(42)
    config = Config(years=1, population_size=50, seed=42)
    idc = IdCounter()
    pop = create_initial_population(rng, config, 50, idc)
    pop_means = {t: float(np.mean([getattr(a, t) for a in pop]))
                 for t in HERITABLE_TRAITS}

    # Create MA parent
    parent1 = pop[0]
    parent1._is_ma = True
    parent1.aggression_propensity = 1.0
    parent1.cooperation_propensity = 0.0
    parent1.genotype = {t: getattr(parent1, t) for t in HERITABLE_TRAITS}

    parent2 = pop[25]  # normal parent

    # Breed 20 offspring — all should have EXACT parent1 genotype for MA traits
    for _ in range(20):
        child = breed(parent1, parent2, rng, config, year=1,
                      id_counter=idc, pop_trait_means=pop_means)
        # MA genotype must be copied exactly — no mutation
        assert child.aggression_propensity == parent1.aggression_propensity, (
            f"MA aggression mutated: {child.aggression_propensity} != {parent1.aggression_propensity}")
        assert child.cooperation_propensity == parent1.cooperation_propensity, (
            f"MA cooperation mutated: {child.cooperation_propensity} != {parent1.cooperation_propensity}")


def test_normal_offspring_still_mutate():
    """Normal parents must still produce mutated offspring."""
    rng = np.random.default_rng(42)
    config = Config(years=1, population_size=50, seed=42)
    idc = IdCounter()
    pop = create_initial_population(rng, config, 50, idc)
    pop_means = {t: float(np.mean([getattr(a, t) for a in pop]))
                 for t in HERITABLE_TRAITS}

    parent1 = pop[0]
    parent2 = pop[25]
    # Ensure neither is MA
    parent1._is_ma = False
    parent2._is_ma = False

    # Breed 20 offspring — at least some traits should differ from midpoint
    children_agg = []
    for _ in range(20):
        child = breed(parent1, parent2, rng, config, year=1,
                      id_counter=idc, pop_trait_means=pop_means)
        children_agg.append(child.aggression_propensity)

    # With mutation, we expect variance
    assert np.std(children_agg) > 0.01, "No mutation detected in normal offspring"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_jasss_revision.py::test_ma_offspring_inherit_exact_genotype -v`
Expected: FAIL (MA offspring currently get mutated)

- [ ] **Step 3: Add MA trait-lock bypass to breed()**

In `models/agent.py`, at line 696 (just before the mutation block), add:

```python
        # JASSS Req 2: MA trait locking — malicious agents pass exact genotype
        if getattr(parent1, '_is_ma', False) or getattr(parent2, '_is_ma', False):
            # Use the MA parent's genotype directly, no mutation
            ma_parent = parent1 if getattr(parent1, '_is_ma', False) else parent2
            child_val = ma_parent.genotype.get(trait_name, genetic_val)
            setattr(child, trait_name, float(np.clip(child_val, 0.0, 1.0)))
            continue
```

Insert this block right BEFORE line 697 (`# Mutation: rare large jumps or normal noise`), after line 695 (`genetic_val = h2 * blend + (1.0 - h2) * pop_mean`). The `continue` skips the mutation and goes to the next trait.

Also mark child as MA:
After line 707 (`child.genotype = {t: getattr(child, t) for t in HERITABLE_TRAITS}`), add:
```python
    # Propagate MA flag to offspring
    if getattr(parent1, '_is_ma', False) or getattr(parent2, '_is_ma', False):
        child._is_ma = True
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_jasss_revision.py -v`
Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add models/agent.py tests/test_jasss_revision.py
git commit -m "feat(agent): MA trait locking — exact genotype inheritance

JASSS Requirement 2: Malicious Agent offspring inherit exact parent
genotype with zero mutation. Ensures infection sweep tests social
immune response, not mutation-driven dilution. Normal breeding
unaffected. _is_ma flag propagates to all descendants."
```

---

### Task 3: O(1) Event Handling (models/society.py)

**Files:**
- Modify: `models/society.py:1,26,78-85` — replace list with deque
- Test: `tests/test_jasss_revision.py`

- [ ] **Step 1: Write the failing test**

```python
# Add to tests/test_jasss_revision.py
from collections import deque
from models.society import Society


def test_event_window_is_deque():
    """Event window must be a collections.deque for O(1) append/evict."""
    cfg = Config(population_size=30, years=1, seed=1)
    rng = np.random.default_rng(1)
    soc = Society(cfg, rng)
    assert isinstance(soc._event_window, deque), (
        f"Expected deque, got {type(soc._event_window)}")
    assert soc._event_window.maxlen == 500


def test_event_window_auto_evicts():
    """Deque must auto-evict oldest events when full — no manual pop(0)."""
    cfg = Config(population_size=30, years=1, seed=1)
    rng = np.random.default_rng(1)
    soc = Society(cfg, rng)
    for i in range(1000):
        soc.add_event({"type": "test", "description": f"e{i}"})
    assert len(soc._event_window) == 500
    # Most recent event should be last
    assert soc._event_window[-1]["description"] == "e999"
    # Oldest should be e500 (first 500 evicted)
    assert soc._event_window[0]["description"] == "e500"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_jasss_revision.py::test_event_window_is_deque -v`
Expected: FAIL (currently a list)

- [ ] **Step 3: Replace list with deque**

In `models/society.py`:

Add import at top (line 1 area):
```python
from collections import deque
```

Replace line 26:
```python
        self._event_window: list[dict] = []        # rolling buffer, last N events
```
with:
```python
        self._event_window: deque[dict] = deque(maxlen=500)  # O(1) circular buffer
```

Replace lines 82-85 in `add_event()`:
```python
        # Rolling window — trim from front when over cap
        self._event_window.append(event)
        if len(self._event_window) > self._event_window_size:
            self._event_window.pop(0)
```
with:
```python
        # O(1) circular buffer — deque handles eviction automatically
        self._event_window.append(event)
```

Remove `self._event_window_size` from line 27 (no longer needed, maxlen on deque).

- [ ] **Step 3b: Update existing society tests for deque**

In `tests/test_society.py`, update `test_event_window_does_not_exceed_cap`:

Replace `assert len(soc._event_window) <= soc._event_window_size` with:
```python
    assert len(soc._event_window) <= soc._event_window.maxlen
```

Update `test_event_window_preserves_most_recent` — it sets `soc._event_window_size = 5` which no longer works (deque maxlen is immutable). Replace by adding 600 events to the default 500-maxlen deque:
```python
def test_event_window_preserves_most_recent():
    soc, _, _ = _make_society()
    for i in range(600):
        soc.add_event({"type": "test", "description": f"e{i}"})
    assert len(soc._event_window) == 500
    assert soc._event_window[-1]["description"] == "e599"
    assert soc._event_window[0]["description"] == "e100"
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/ -v`
Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add models/society.py tests/test_jasss_revision.py
git commit -m "perf(society): O(1) event window via collections.deque

JASSS Requirement 3: Replace O(N) list.pop(0) with O(1) deque(maxlen=500).
Eliminates non-linear slowdown in 500-year divergence runs.
Existing event_window_size tests still pass."
```

---

### Task 4: Selection Differential (Breeder's Equation) Metrics

**Files:**
- Modify: `metrics/collectors.py` — add 4 new metrics to `collect()`
- Modify: `engines/reproduction.py` — tag parents who bred this tick
- Test: `tests/test_jasss_revision.py`

- [ ] **Step 1: Write the failing test**

```python
# Add to tests/test_jasss_revision.py
from simulation import Simulation


def test_selection_differential_metrics_exist():
    """Metrics must include mu_pop, mu_eligible, mu_parents, S."""
    config = Config(years=20, population_size=100, seed=42)
    sim = Simulation(config)
    sim.run()

    last = sim.metrics.rows[-1]
    for key in ["mu_pop_cooperation", "mu_eligible_cooperation",
                "mu_parents_cooperation", "selection_differential_S"]:
        assert key in last, f"Missing metric: {key}"

    # S = mu_parents - mu_eligible
    if last["mu_parents_cooperation"] is not None and last["mu_eligible_cooperation"] is not None:
        expected_S = last["mu_parents_cooperation"] - last["mu_eligible_cooperation"]
        assert abs(last["selection_differential_S"] - expected_S) < 0.001, (
            f"S mismatch: {last['selection_differential_S']} != {expected_S}")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_jasss_revision.py::test_selection_differential_metrics_exist -v`
Expected: FAIL (metrics don't exist yet)

- [ ] **Step 3a: Tag parents in reproduction engine**

In `engines/reproduction.py`, after a successful birth event, tag both parents:

Find the block where the child is created (after `breed()` call) and add:
```python
                    # Tag parents for Breeder's Equation metrics
                    mother._bred_this_tick = True
                    father._bred_this_tick = True
```

- [ ] **Step 3b: Add selection differential to metrics collector**

In `metrics/collectors.py`, inside the `collect()` method, after the existing cooperation metrics, add:

```python
        # JASSS Req 4: Breeder's Equation — Selection Differential
        coop_all = [a.cooperation_propensity for a in living]
        mu_pop = float(np.mean(coop_all)) if coop_all else None

        females_elig, males_elig = society.get_mating_eligible()
        eligible = females_elig + males_elig
        coop_eligible = [a.cooperation_propensity for a in eligible]
        mu_eligible = float(np.mean(coop_eligible)) if coop_eligible else None

        parents = [a for a in living if getattr(a, '_bred_this_tick', False)]
        coop_parents = [a.cooperation_propensity for a in parents]
        mu_parents = float(np.mean(coop_parents)) if coop_parents else None

        S = (mu_parents - mu_eligible) if (mu_parents is not None and mu_eligible is not None) else None

        row["mu_pop_cooperation"] = mu_pop
        row["mu_eligible_cooperation"] = mu_eligible
        row["mu_parents_cooperation"] = mu_parents
        row["selection_differential_S"] = S

        # Clear breeding flags for next tick
        for a in living:
            a._bred_this_tick = False
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/ -v`
Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add engines/reproduction.py metrics/collectors.py tests/test_jasss_revision.py
git commit -m "feat(metrics): Breeder's Equation selection differential per tick

JASSS Requirement 4: Log mu_pop, mu_eligible, mu_parents, and S
(selection differential) every tick. Parents tagged in reproduction
engine, metrics computed in collector. S = mu_parents - mu_eligible
measures directional selection pressure on cooperation."
```

---

### Task 5: Gate — Full Regression + 200yr Smoke Test

**Files:**
- None (verification only)

- [ ] **Step 1: Run full test suite**

Run: `python -m pytest tests/ -v`
Expected: All tests PASS

- [ ] **Step 2: 200yr determinism check**

```bash
python -c "
from config import Config
from simulation import Simulation
pops = []
for _ in range(2):
    sim = Simulation(Config(years=200, population_size=200, seed=42))
    sim.run()
    pops.append(sim.society.population_size())
assert pops[0] == pops[1], f'Determinism broken: {pops}'
last = sim.metrics.rows[-1]
print(f'Pop: {pops[0]}')
print(f'S: {last[\"selection_differential_S\"]:.6f}')
print(f'mu_parents: {last[\"mu_parents_cooperation\"]}')
print(f'mu_eligible: {last[\"mu_eligible_cooperation\"]}')
print('GATE PASSED')
"
```

- [ ] **Step 3: Commit gate results**

```bash
git commit --allow-empty -m "gate: JASSS revision requirements 1-4 verified

All 4 architectural requirements implemented and tested:
1. Parameter parity: 34/35 defaults match AutoSIM Run 3
2. MA trait locking: exact genotype inheritance, zero mutation
3. O(1) event handling: deque(maxlen=500)
4. Selection differential: S = mu_parents - mu_eligible per tick"
```
