# AutoSIM — Autonomous Simulation Improvement Loop

Inspired by Karpathy's autoresearch pattern: AI agent modifies code → runs experiment → checks metric → keeps/discard → repeats. No human in the loop.

## Why SIMSIV Is a Good Fit

- Simulation runs are fast (~60-90 seconds per experiment: 3 seeds x 200yr x 500pop)
- Metrics are interpretable (Gini, violence rate, trait evolution) vs opaque loss curves
- Real-world anthropological targets exist to calibrate against

## Architecture

```
autoresearch mapping:
  program.md          →  CLAUDE.md + calibration_targets.md
  train.py            →  any engine file (conflict.py, reproduction.py, etc.)
  val_bpb metric      →  composite "realism score"
  5-min experiment    →  200-year simulation run (~60-90 seconds, 3 seeds)
```

## Calibration Targets

Real-world anthropological/demographic benchmarks:

| Metric | Target Range | Source |
|--------|-------------|--------|
| Resource Gini | 0.30–0.50 | Pre-industrial societies |
| Reproductive skew (male) | 0.40–0.70 | Polygynous hunter-gatherers |
| Violence death rate | 5–15% of male deaths | Ethnographic data |
| Population growth rate | 0.5–1.5%/yr at equilibrium | Pre-industrial avg |
| Child survival to 15 | 50–70% | Pre-industrial avg |
| Avg children per woman | 4–7 | Natural fertility societies |
| Pair bond dissolution | 10–30%/lifetime | Cross-cultural avg |
| Cooperation trait stability | No extinction (>0.2 avg) | Cooperation exists IRL |
| Aggression trait | Moderate decline or stable | Not eliminated IRL either |

## Composite Realism Score

```python
def realism_score(metrics: dict, targets: dict) -> float:
    """0.0 = terrible, 1.0 = perfect match to all targets."""
    scores = []
    for metric_name, (low, high) in targets.items():
        value = metrics[metric_name]
        if low <= value <= high:
            scores.append(1.0)
        else:
            dist = min(abs(value - low), abs(value - high))
            range_size = high - low
            scores.append(max(0, 1.0 - dist / (range_size + 0.01)))
    return sum(scores) / len(scores)
```

## Experiment Loop — Two Modes

### Mode A — Parameter Sweep (start here)

- AI agent modifies `config.py` values only
- Runs 200-year sim, checks realism score
- Keeps parameters that improve score
- Basically hyperparameter optimization with an LLM as the search algorithm

### Mode B — Engine Logic Modification (the real prize)

- AI agent modifies engine files (reproduction.py, conflict.py, etc.)
- Same loop: modify → run → score → keep/discard
- Agent might discover kin-based alliances, age-dependent aggression, etc.
- Constraint: changes must pass smoke tests

## Safety Rails

- **Git checkpoint** before each experiment
- **Smoke test gate**: sim must complete 200 years, population must survive
- **Bounded changes**: agent can only modify `engines/` and `config.py`, never `models/agent.py` (trait structure is sacred). Sacred files: `models/agent.py`, `models/society.py`, `models/environment.py`, `simulation.py`, `metrics/collectors.py`, all 8 engine files (`engines/conflict.py`, `engines/institutions.py`, `engines/mating.py`, `engines/mortality.py`, `engines/pathology.py`, `engines/reproduction.py`, `engines/reputation.py`, `engines/resources.py`)
- **Budget cap**: max 30 seconds compute per experiment
- **Journal**: every experiment logged to `autosim/journal.jsonl` with diff, metrics, score

## File Structure

```
autosim/
  program.md          # Instructions for the AI agent
  targets.yaml        # Calibration targets
  runner.py           # Orchestrator: modify → run → score → keep/discard
  journal.jsonl       # Experiment log
  best_config.yaml    # Current best parameters
```

## Agent Instructions (program.md concept)

> You are optimizing a social simulation. Your goal is to maximize the realism
> score by modifying engine logic and parameters. The simulation models agents
> with heritable traits competing for resources and mates. Current weak spots:
> Resource Gini too low (0.09–0.15, target 0.30–0.50), violence rate may be
> unrealistic. Do NOT hardwire outcomes. All social patterns must emerge from
> agent-level rules.

## What This Could Discover

- Non-linear resource sharing curves that produce realistic Gini
- Age-dependent mating strategies (young males aggressive, older males cooperative)
- Kinship loyalty mechanics from reputation + shared parents
- Seasonal resource cycles creating realistic boom-bust demographics
- Status inheritance effects (children of high-status parents start with advantages)

## Prerequisites Before Building

1. **Calibration targets file** — 10–15 metrics with real-world ranges
2. **Fast benchmark harness** — `score_run(config, seed_count=3)` averaging 3 seeds in <30 seconds

## Status

**RUNNING — Mode A complete, 100+ experiments logged.** Parameter sweeps optimizing realism score via `autosim/runner.py`. Journal at `autosim/journal.jsonl`. Best config at `autosim/best_config.yaml`. Mode B (engine logic modification) not yet attempted.
