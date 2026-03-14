# SIMSIV — Simulation of Intersecting Social and Institutional Variables

Emergent social simulation: 500+ agents with heritable traits compete for resources, mates, and status. Outcomes must EMERGE from rules, never be hardwired.

## Current Status
See `STATUS.md` for what to work on next.

## Key Files
- `CHAIN_PROMPT.md` — Master design doc (all confirmed decisions, authoritative)
- `devlog/DEV_LOG.md` — Session-by-session log (append new entries each session)
- `STATUS.md` — Short "where are we" file (update every session)
- `prompts/phase2_skeleton.md` — Detailed implementation spec for the skeleton

## Architecture Rules
- **Pure library**: Simulation engine has NO UI, NO print statements, NO matplotlib calls. All IO at the edges.
- **Tick returns data**: `sim.tick()` returns pure state — any frontend (CLI, Streamlit, game) consumes it.
- **Engine order per tick**: environment → resources → institutions → mating → reproduction → conflict → age/mortality → metrics
- **Models know nothing about engines** — no circular imports.
- **All randomness** via `numpy.random.Generator` seeded from config. Same seed = identical results.
- **Events are dicts**: `{type, year, agent_ids, description, outcome}`

## Agent Model (8 heritable traits, Gaussian mutation σ=0.05)
aggression_propensity, cooperation_propensity, attractiveness_base, status_drive,
risk_tolerance, jealousy_sensitivity, fertility_base, intelligence_proxy — all float [0.0-1.0]

## Tech Stack
Python 3.11+, numpy, pandas, matplotlib, pyyaml. Streamlit for UI (later). No external APIs.

## Design Improvements to Apply During Build
- Sparse reputation ledger (only store agents actually interacted with, cap at ~100)
- Realistic age pyramid initialization (not all same age)
- Extinction guard (min_viable_population ~20)
- Trait correlation matrix for initial generation (aggression/cooperation negative, etc.)
- Equilibrium detection (flag when metrics stabilize)
