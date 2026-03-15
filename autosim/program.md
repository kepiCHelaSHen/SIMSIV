# AutoSIM Program — Mode A Parameter Optimization

## What This Does

AutoSIM is an autonomous simulation improvement loop. Mode A optimizes
`config.py` parameter values against anthropological calibration targets.
It never modifies engine logic or model files.

## Architecture

```
autosim/
  program.md         # This file — design and instructions
  targets.yaml       # Calibration targets + tunable parameter ranges
  realism_score.py   # Scoring function (0.0 = terrible, 1.0 = perfect)
  runner.py          # Orchestrator: perturb → run → score → keep/discard
  journal.jsonl      # Experiment log (append-only)
  best_config.yaml   # Current best parameters
```

## How It Works

1. **Baseline**: score the default Config against 9 calibration targets
2. **Perturb**: randomly modify 2-4 parameters within allowed ranges
3. **Run**: execute 200yr simulation × 3 seeds (for robustness)
4. **Score**: compute weighted realism score against targets
5. **Keep/Discard**: if score improves, accept new parameters; else reject
6. **Log**: every experiment written to journal.jsonl with full metrics
7. **Repeat**: until experiment budget exhausted

## Calibration Targets

| Metric | Target | Source |
|--------|--------|--------|
| Resource Gini | 0.30–0.50 | Pre-industrial societies |
| Male reproductive skew | 0.40–0.70 | Polygynous hunter-gatherers |
| Violence death fraction | 5–15% of male deaths | Ethnographic data |
| Population growth | 0.1–1.5%/yr | Pre-industrial average |
| Child survival to 15 | 50–70% | Pre-industrial average |
| Children per woman | 4–7 | Natural fertility populations |
| Bond dissolution | 10–30% | Cross-cultural average |
| Cooperation trait | >0.25 | Cooperation exists IRL |
| Aggression trait | 0.30–0.60 | Moderate, not eliminated |

## Optimizer Strategy

Hill-climbing with adaptive perturbation:
- **Normal**: perturb 2 params, step_scale=0.15
- **Stalled (10+ rejections)**: widen to 3 params, step_scale=0.25
- **Long stall (20+)**: 4 params, step_scale=0.35
- **Every 10th experiment**: random jump (5 params, step_scale=0.30)

## Safety Rails

- **Sacred files**: models/agent.py, models/society.py never modified
- **Mode A only**: config parameters only, no engine logic changes
- **Survival gate**: population must survive 200yr (>20 at end)
- **Parameter bounds**: all values clamped to allowed ranges in targets.yaml
- **Journal**: every experiment logged with full reproducibility info

## Usage

```bash
# Smoke test (3 experiments)
python -m autosim.runner --smoke-test

# Full run (100 experiments)
python -m autosim.runner --experiments 100

# Analyze results
python -c "
import json
with open('autosim/journal.jsonl') as f:
    entries = [json.loads(line) for line in f]
accepts = [e for e in entries if e['action'] == 'ACCEPT']
print(f'Accepted: {len(accepts)} / {len(entries)}')
print(f'Best score: {max(e[\"score\"] for e in entries):.4f}')
"
```
