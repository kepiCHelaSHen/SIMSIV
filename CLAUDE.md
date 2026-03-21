# SIMSIV — Simulation of Intersecting Social and Institutional Variables

Emergent social simulation: 500+ agents with 35 heritable traits compete for resources, mates, and status. All social patterns EMERGE from rules — never hardwired. DD01-DD27 complete.

## Current Status
- **Paper 1:** Under review at JASSS (submission 2026:81:1, ref 6029)
- **v2 clan simulator:** Complete (6,957 lines, 187 tests, 120 convergence runs)
- **Drift working paper:** Draft v5 (`docs/SIMSIV_V2_White_Paper.md`)
- See `STATUS.md` for full details.

## Key Files
- `CHAIN_PROMPT.md` — Master design doc (all confirmed decisions, authoritative)
- `STATUS.md` — Short "where are we" file
- `devlog/DEV_LOG.md` — Session-by-session log
- `autosim/` — Autonomous improvement loop (runner, journal, targets, best config)
- `dashboard/app.py` — Streamlit dashboard (run: `python -m streamlit run dashboard/app.py`)

### v2 Clan Layer
- `models/clan/clan_base.py` — Cooperation, trade, defence, selection metrics (712 lines)
- `models/clan/band.py` — Band model (wraps Society, composition pattern)
- `models/clan/clan_society.py` — Multi-band registry + interaction scheduling
- `models/clan/clan_config.py` — v2 tunable parameters
- `models/clan/clan_simulation.py` — High-level experiment wrapper
- `engines/clan_base.py` — ClanEngine: per-band v1 tick + inter-band dispatch
- `engines/clan_trade.py` — Positive-sum trade (Wiessner 1982)
- `engines/clan_raiding.py` — Bowles raiding + coalition defence
- `engines/clan_selection.py` — Between-group selection, fission, extinction, Fst

### Drift Experiment
- `experiments/drift_experiment/` — Controlled experiment scripts (Conditions A/B)
- `experiments/drift_analysis.py` — Fisher's exact, sensitivity, inter-model agreement, figures
- `docs/SIMSIV_V2_White_Paper.md` — Working paper
- `docs/figures/figure1_drift_scatter.png` — Hero figure
- `tests/test_milestone_battery.py` — 4-milestone × 30-seed convergence gate

## Architecture Rules
- **Pure library**: Simulation engine has NO UI, NO print statements. All IO at the edges.
- **Tick returns data**: `sim.tick()` returns pure state dict — any frontend consumes it.
- **Models know nothing about engines** — no circular imports.
- **All randomness** via `numpy.random.Generator` seeded from config. Same seed = identical results.
- **Events are dicts**: `{type, year, agent_ids, description, outcome}`
- **Isolated simulation instances**: Use `Simulation(config)` freely in loops. Each instance owns its own `IdCounter` at `society.id_counter`. Agent IDs are unique within a run.
- **Bounded events**: `society._event_window` holds last 500 events (rolling). `society.event_type_counts` holds running totals per event type. Do NOT use `society.events`.
- **Structured logging**: All engines use `logging.getLogger(__name__)`. Pass `--verbose` for debug output. No bare `print()` inside engines.
- **Config validation**: `Config.load()` warns on unrecognized YAML keys.

## v1 Engine Tick Order (12 steps, runs per-band in v2)
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

## v2 Clan Tick (wraps v1, adds inter-band)
1. Run v1 12-step tick on each band independently (per-band rng)
2. Schedule inter-band interactions (distance × trust)
3. Classify + dispatch: trade / neutral / hostile(raid)
4. Between-group selection: coefficients, migration, fission, extinction
5. Collect clan-level metrics (Fst, trust, trade volume, selection coefficients)

## Agent Model — 35 Heritable Traits (h²-weighted, mutation σ=0.05)
**Original 8**: aggression_propensity, cooperation_propensity, attractiveness_base, status_drive, risk_tolerance, jealousy_sensitivity, fertility_base, intelligence_proxy
**DD15 Biological**: longevity_genes, disease_resistance, physical_robustness, pain_tolerance
**DD15 Psychological**: mental_health_baseline, emotional_intelligence, impulse_control, novelty_seeking
**DD15 Social**: empathy_capacity, conformity_bias, dominance_drive
**DD15 Reproductive**: maternal_investment, sexual_maturation_rate
**DD17 Condition Risks**: cardiovascular_risk, mental_illness_risk, autoimmune_risk, metabolic_risk, degenerative_risk
**DD27 Trait Completion**: physical_strength, endurance, conscientiousness, future_orientation, group_loyalty, outgroup_tolerance, psychopathy_tendency, social_skill

All float [0.0-1.0].

## Frozen Paper Coefficients (Critic enforces these)
| Parameter | Value | Source |
|-----------|-------|--------|
| empathy_coeff | 0.15 | resources.py:289 |
| coop_norm_coeff | 0.10 | resources.py:292 |
| conformity_coeff | 0.30 | institutions.py:237 |
| social_skill_coeff | 0.10 | clan_trade.py:330 |
| cohesion_bonus_coeff | 0.20 | clan_raiding.py:610 |

## 9 v1 Engine Files + 4 v2 Engine Files
`engines/`: conflict, institutions, mating, mortality, pathology, reproduction, reputation, resources + `__init__.py`
`engines/`: clan_base, clan_trade, clan_raiding, clan_selection (v2)

## Tech Stack
Python 3.11+, numpy, pandas, scipy, matplotlib, pyyaml, plotly, streamlit. No external APIs.
