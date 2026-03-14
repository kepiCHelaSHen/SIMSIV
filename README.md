# SIMSIV
### Simulation of Intersecting Social and Institutional Variables

A Python-based emergent social simulation sandbox exploring how human social
structures may arise from first-principles interactions among reproduction,
resource competition, status seeking, cooperation, jealousy, violence, pair
bonding, and institutional constraints.

**This is a sandbox for discovery, not an ideological engine.**

---

## Quick Start

```bash
pip install -r requirements.txt
python main.py
python main.py --scenario ENFORCED_MONOGAMY --seed 42 --years 100
```

## Project Structure

| Directory | Purpose |
|---|---|
| `models/` | Agent, Environment, Society data models |
| `engines/` | Simulation logic — mating, resources, conflict, etc. |
| `metrics/` | Per-tick data collection |
| `experiments/` | Scenario definitions and experiment runner |
| `visualizations/` | Chart generation |
| `outputs/` | All run outputs (CSVs, PNGs, JSON) |
| `docs/` | Design documents and specs |
| `devlog/` | Session-by-session development log |
| `prompts/` | Claude prompt library for iterative development |
| `artifacts/` | Permanent record of significant outputs |

## Master Design Document

See `CHAIN_PROMPT.md` for all design decisions, confirmed parameters,
prompt library, and development strategy.

## Development Log

See `devlog/DEV_LOG.md` for full session-by-session history.

## Status

Pre-skeleton — design phase complete. Implementation not yet started.
See `CHAIN_PROMPT.md → NEXT SESSION OBJECTIVE` for current priority.

---

*Not a political project. Not a moral argument. A simulation sandbox.*
