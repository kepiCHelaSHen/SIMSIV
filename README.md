# SIMSIV
### Simulation of Intersecting Social and Institutional Variables

A Python-based emergent social simulation modeling how human social structures
arise from first-principles interactions among reproduction, resource competition,
status seeking, cooperation, jealousy, violence, pair bonding, and institutional
constraints. Band-level simulator v1.0.

**This is a sandbox for discovery, not an ideological engine.**

---

## Quick Start

```bash
pip install -r requirements.txt
python main.py
python main.py --scenario ENFORCED_MONOGAMY --seed 42 --years 100
```

Interactive dashboard:
```bash
streamlit run experiments/dashboard.py
```

## What's In the Box

- **26 heritable traits** with per-trait heritability coefficients (h²-weighted
  inheritance, Gaussian mutation, stress-amplified variation)
- **5 non-heritable belief dimensions** [-1, +1] — cultural transmission,
  social influence, experience-based updating, ideological tension
- **4 non-heritable skill domains** [0, 1] — experiential learning, decay,
  mentoring, parent transmission
- **9 simulation engines** running in sequence each tick:
  1. **Environment** — carrying capacity, seasonal cycles, epidemics
  2. **Resources** — 8-phase distribution (3 resource types: subsistence, tools, prestige goods)
  3. **Conflict** — jealousy/status/resource triggers, coalition defense, bystander effects
  4. **Mating** — female choice, male competition, pair bonds, infidelity, paternity
  5. **Reproduction** — h²-weighted inheritance, developmental plasticity, epigenetics
  6. **Mortality** — age/health/violence death, childhood mortality, maturation triggers
  7. **Pathology** — 5 condition risks, trauma accumulation, contagion
  8. **Institutions** — norm enforcement, drift, emergence, property rights, inheritance
  9. **Reputation** — gossip, trust decay, beliefs evolution, skill updates, factions
- **Life stages** (childhood → youth → prime → mature → elder) with age-specific behaviors
- **Proximity tiers** (household → neighborhood → band) gating interaction scope
- **Migration** (emigration push / immigration pull between bands)
- **Leadership** (war leader + peace chief per faction)
- **26 deep dive design iterations** completed — see `docs/` for each

## Project Structure

| Directory | Purpose |
|---|---|
| `models/` | Agent, Environment, Society data models |
| `engines/` | 9 simulation engines (mating, resources, conflict, etc.) |
| `metrics/` | Per-tick data collection (~120 metrics) |
| `experiments/` | Scenario definitions and experiment runner |
| `visualizations/` | Chart generation |
| `outputs/` | All run outputs (CSVs, PNGs, JSON) |
| `docs/` | Design documents — one per deep dive |
| `devlog/` | Session-by-session development log |
| `prompts/` | Claude prompt library (26 deep dives + templates) |
| `artifacts/` | Permanent record of significant outputs |
| `sandbox/` | IPython exploration harness |

## Key Design Principles

- **Pure library core**: `simulation.py` has zero IO — `tick()` returns a metrics dict
- **Flat config**: single `Config` dataclass (~250 params), YAML save/load
- **Emergent outcomes**: all social structure arises from rules, never hardwired
- **Reproducible**: every run is seed-controlled and deterministic

## Scenarios

| Scenario | Description |
|---|---|
| `BASELINE` | Unrestricted competition — null hypothesis |
| `ENFORCED_MONOGAMY` | Law-enforced pair bonding |
| `ELITE_POLYGYNY` | Top-status males exempt from mate limits |
| `STRONG_STATE` | High law strength, property rights, taxation |
| `EMERGENT_INSTITUTIONS` | All institutions start at zero, drift enabled |
| `HIGH_VIOLENCE` | Elevated aggression, reduced conflict suppression |
| `RESOURCE_SCARCITY` | Reduced carrying capacity |

## Selected Findings

- Cooperation + intelligence consistently selected for across all scenarios
- Aggression reliably selected against (fitness cost > benefit)
- Institutional strength self-organizes from 0 → 0.48 over 200yr in EMERGENT scenario
- Enforced monogamy reduces violence 37% and unmated males 40% vs baseline
- Elite polygyny drives highest Gini (0.468) but not highest violence
- Trait diversity maintained at σ~0.09 by rare large mutations (5% chance, 3× sigma)

## Documentation

- `CHAIN_PROMPT.md` — master design document (all confirmed decisions)
- `devlog/DEV_LOG.md` — full development history
- `docs/deep_dive_*.md` — design rationale for each subsystem

---

*Not a political project. Not a moral argument. A simulation sandbox.*
