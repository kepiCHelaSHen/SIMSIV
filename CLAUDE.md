# SIMSIV — Simulation of Intersecting Social and Institutional Variables

Emergent social simulation: 500+ agents with 26 heritable traits compete for resources, mates, and status. All social patterns EMERGE from rules — never hardwired. Phase C complete (DD01-DD26).

## Current Status
Phase E complete (Engineering hardening: IdCounter, event window, partner index, logging, test suite). Ready for v2 multi-band or autosim scale-up.
See `STATUS.md` for what to work on next.

## Key Files
- `CHAIN_PROMPT.md` — Master design doc (all confirmed decisions, authoritative)
- `STATUS.md` — Short "where are we" file
- `devlog/DEV_LOG.md` — Session-by-session log
- `autosim/` — Autonomous improvement loop (runner, journal, targets, best config)
- `dashboard/app.py` — Streamlit dashboard (run: `python -m streamlit run dashboard/app.py`)

## Architecture Rules
- **Pure library**: Simulation engine has NO UI, NO print statements. All IO at the edges.
- **Tick returns data**: `sim.tick()` returns pure state dict — any frontend consumes it.
- **Models know nothing about engines** — no circular imports.
- **All randomness** via `numpy.random.Generator` seeded from config. Same seed = identical results.
- **Events are dicts**: `{type, year, agent_ids, description, outcome}`
- **Isolated simulation instances**: Use `Simulation(config)` freely in loops. Each instance owns its own `IdCounter` at `society.id_counter`. Agent IDs are unique within a run. Two simultaneous simulations both start from ID 1.
- **Bounded events**: `society._event_window` holds last 500 events (rolling). `society.event_type_counts` holds running totals per event type. Do NOT use `society.events` — that attribute no longer exists.
- **Structured logging**: All engines use `logging.getLogger(__name__)`. Pass `--verbose` for debug output. No bare `print()` inside engines.
- **Config validation**: `Config.load()` warns on unrecognized YAML keys. `Config.__post_init__` validates `mating_system` and wires enforcement flags.

## Engine Tick Order (12 steps)
1. Environment (scarcity shocks, seasons)
2. Resources (8-phase distribution, cooperation sharing, taxation)
3. Conflict (before mating — violence has reproductive cost)
4. Mating (female choice, pair bonds, EPC, contests)
5. Reproduction (conception, birth, infant survival)
6. Mortality (aging, health decay, childhood mortality)
7. Migration (emigration/immigration, if enabled)
8. Pathology (conditions, trauma, epigenetics)
9. Institutions (inheritance, norm enforcement, drift, emergence)
10. Reputation (gossip, trust decay, beliefs, skills, factions)
11. Faction detection + neighborhood refresh (periodic)
12. Metrics collection (~120 metrics per tick)

## Agent Model — 26 Heritable Traits (h²-weighted, mutation σ=0.05)
**Original 8**: aggression_propensity, cooperation_propensity, attractiveness_base, status_drive, risk_tolerance, jealousy_sensitivity, fertility_base, intelligence_proxy
**DD15 Biological**: longevity_genes, disease_resistance, physical_robustness, pain_tolerance
**DD15 Psychological**: mental_health_baseline, emotional_intelligence, impulse_control, novelty_seeking
**DD15 Social**: empathy_capacity, conformity_bias, dominance_drive
**DD15 Reproductive**: maternal_investment, sexual_maturation_rate
**DD17 Condition Risks**: cardiovascular_risk, mental_illness_risk, autoimmune_risk, metabolic_risk, degenerative_risk

All float [0.0-1.0].

## Non-Heritable State
- health, reputation, current_resources, current_tools, current_prestige_goods
- prestige_score, dominance_score (DD08: dual status tracks)
- **Beliefs** (DD25, 5 dims): hierarchy_belief, cooperation_norm, violence_acceptability, tradition_adherence, kinship_obligation — float [-1, +1]
- **Skills** (DD26, 4 domains): foraging_skill, combat_skill, social_skill, craft_skill — float [0, 1]
- faction_id, neighborhood_ids, reputation_ledger
- trauma_score, epigenetic_stress_load, active_conditions
- life_stage (computed: CHILDHOOD/YOUTH/PRIME/MATURE/ELDER)

## 9 Engine Files
`engines/`: conflict, institutions, mating, mortality, pathology, reproduction, reputation, resources + `__init__.py`

## Tech Stack
Python 3.11+, numpy, pandas, matplotlib, pyyaml, plotly, streamlit. No external APIs.
