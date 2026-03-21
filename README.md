# SIMSIV

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19065475.svg)](https://doi.org/10.5281/zenodo.19065475)

### Simulation of Intersecting Social and Institutional Variables

SIMSIV is a calibrated agent-based simulation of band-level human social
evolution, grounded in behavioral genetics, evolutionary anthropology, and
institutional economics. Every agent is a complete simulated person with a
genome, developmental history, medical biography, earned skills, culturally
transmitted beliefs, and a life story from birth to death.

**v1.0 band simulator (under review at JASSS) + v2.0 multi-band clan simulator with drift experiment.**
35 heritable traits, 13 engines, 187 tests, calibrated to score 1.000 against 9 anthropological benchmarks.

All findings are emergent. Nothing is scripted.

---

## The Central Research Question

> *Does institutional governance systematically reduce directional selection on
> heritable prosocial behavioral traits — providing computational evidence that
> institutions and genes are substitutes, not complements, in human social
> evolution?*

This engages the debate between Camp A (Bowles/Gintis: traits and institutions
co-evolve upward together) and Camp B (North: institutions substitute for
internal motivation).

---

## Quick Start

```bash
pip install -r requirements.txt
python main.py --seed 42 --years 200 --population 500
streamlit run dashboard/app.py
```

Run scenario experiments:

```bash
python scripts/run_experiments.py --scenarios FREE_COMPETITION STRONG_STATE --seeds 5 --years 200
python scripts/run_experiments.py --list   # show all scenarios
```

Validate calibration:

```bash
python scripts/validate_best_config.py --seeds 10 --years 200
```

---

## The 9 Simulation Engines

Each annual tick runs through nine interacting subsystems in order:

| Step | Engine | Function |
|------|--------|----------|
| 1 | Environment | Seasonal cycles, scarcity shocks, epidemic events |
| 2 | Resources | 8-phase distribution across 3 resource types |
| 3 | Conflict | Violence, deterrence, coalitions, cross-sex dynamics |
| 4 | Mating | Female choice, male competition, pair bonding, EPC |
| 5 | Reproduction | h²-weighted trait inheritance, developmental plasticity |
| 6 | Mortality | Aging, sex-differential mortality, epidemic vulnerability |
| 6.3 | Migration | Voluntary emigration and immigration |
| 6.5 | Pathology | Disease activation, trauma, epigenetic stress |
| 7 | Institutions | Norm enforcement, property rights, institutional drift |
| 8 | Reputation | Gossip networks, trust, beliefs, skills, faction detection |

---

## The 35 Heritable Traits

**Physical:** physical_strength, endurance, physical_robustness, pain_tolerance,
longevity_genes, disease_resistance

**Cognitive:** intelligence_proxy (h²=0.65), emotional_intelligence,
impulse_control, conscientiousness

**Temporal:** future_orientation

**Personality:** risk_tolerance, novelty_seeking, anxiety_baseline,
mental_health_baseline

**Social:** aggression_propensity, cooperation_propensity, dominance_drive,
group_loyalty, outgroup_tolerance, empathy_capacity, conformity_bias,
status_drive, jealousy_sensitivity

**Reproductive:** fertility_base, sexual_maturation_rate, maternal_investment,
paternal_investment_preference, attractiveness_base

**Psychopathology risk:** psychopathy_tendency, mental_illness_risk,
cardiovascular_risk, autoimmune_risk, metabolic_risk, degenerative_risk

---

## Key Emergent Findings

These arise from interaction rules — not scripted outcomes:

- Cooperation and intelligence reliably selected for across all scenarios
- Aggression reliably selected against (5 independent fitness cost channels)
- ENFORCED_MONOGAMY reduces violence 37%, unmated males 65%
- STRONG_STATE reduces Gini 40%, violence 49% — without changing cooperation trait
- Law strength self-organizes from 0 → 0.83 in EMERGENT_INSTITUTIONS over 200yr
- Resource scarcity produces the highest cooperation (stress-interdependence)
- Elite polygyny paradox: highest lifespan, near-zero population growth
- Cooperation trait is a robust emergent attractor (max sensitivity r = 0.20)

---

## Scenarios

| Scenario | Purpose |
|----------|---------|
| `FREE_COMPETITION` | Null hypothesis — weak endogenous governance |
| `NO_INSTITUTIONS` | True zero-governance control |
| `ENFORCED_MONOGAMY` | Mating system effects |
| `ELITE_POLYGYNY` | Reproductive inequality |
| `HIGH_FEMALE_CHOICE` | Sexual selection |
| `RESOURCE_ABUNDANCE` | Ecological effects on cooperation |
| `RESOURCE_SCARCITY` | Stress-induced cooperation |
| `HIGH_VIOLENCE_COST` | Aggression selection pressure |
| `STRONG_PAIR_BONDING` | Family stability effects |
| `STRONG_STATE` | Strong fixed governance |
| `EMERGENT_INSTITUTIONS` | Institutional self-organization |

---

## Calibration

AutoSIM uses simulated annealing to fit 36 parameters against 9 targets drawn
from ethnographic and historical demography literature. See `autosim/targets.yaml`
for sources and `docs/validation.md` for the full calibration report.

Best config: `autosim/best_config.yaml` — score 1.000, Run 3, 816 experiments.
Held-out validation: 10 seeds × 200yr, mean score 0.934, zero collapses.

---

## Project Structure

```
SIMSIV/
├── config.py              # ~257 tunable parameters
├── simulation.py          # Annual tick orchestrator
├── models/               # Agent, Society, Environment
├── engines/              # 9 simulation subsystems
├── metrics/              # ~130 tracked metrics per tick
├── experiments/          # Scenario runner and definitions
├── autosim/              # Calibration engine + results
├── scripts/              # Validation, experiments, sensitivity analysis
├── dashboard/            # Streamlit visualization
├── tests/                # 187 tests (22 v1 + 141 v2 clan + 24 drift/convergence)
├── docs/                 # Architecture, validation, calibration docs
├── devlog/               # Full development history
└── prompts/              # Executable build prompts
```

---

## Specification Drift — Working Paper

**"LLMs Generate from Priors, Not Specifications"** — we ran a controlled experiment measuring coefficient drift across GPT-4o, Grok-3, and Claude on SIMSIV implementation tasks.

**Key finding:** Without source code in the prompt, frontier LLMs produced incorrect coefficients on 99% of measurements (95/96, Fisher's exact p = 4×10⁻¹⁰). With the SIMSIV-V2 Builder/Critic/Reviewer protocol, drift dropped to 0%.

- **Paper:** [`docs/SIMSIV_V2_White_Paper.md`](docs/SIMSIV_V2_White_Paper.md)
- **Figure 1 — Drift scatter plot:** [`docs/figures/figure1_drift_scatter.png`](docs/figures/figure1_drift_scatter.png)
- **Figure 2 — Drift sensitivity:** [`docs/figures/figure2_drift_sensitivity.png`](docs/figures/figure2_drift_sensitivity.png)
- **Experiment code:** [`experiments/drift_experiment/`](experiments/drift_experiment/)
- **Convergence battery:** [`tests/test_milestone_battery.py`](tests/test_milestone_battery.py) (4 milestones × 30 seeds)
- **Tag:** `v2-working-paper-alpha`

## Development Protocol — Anti-Drift Framework

SIMSIV v2 uses a **Builder/Critic/Reviewer** protocol to prevent specification drift in LLM-generated scientific code.

**σ-Gated Commits:** No code is merged unless variance across n=30 seeds is < 0.15 on all primary metrics.

**Critic-Led Friction:** The Critic enforces 100% compliance with the frozen JASSS specification (submission 2026:81:1). Every coefficient must trace to a source-code line and a literature citation.

**Automated Kill-Switches:** Five exit conditions halt the loop: science complete, performance gate, anomaly, misalignment, or human stop.

---

## Development Methodology

Built over 27 deep-dive design sessions (DD01-DD27), each adding a
scientifically grounded subsystem. Full history in `CHAIN_PROMPT.md`,
`devlog/`, and `prompts/`.

**AI disclosure:** Code development was assisted by Claude (Anthropic). All
scientific decisions, hypotheses, experimental designs, and interpretations
are the author's own.

This repository is fully transparent — every design decision, calibration run,
validation result, and experiment output is committed to git.

---

## Known Limitations

- **Single-band only:** Between-group selection (Bowles & Gintis, Choi & Bowles)
  is absent. All findings reflect within-group dynamics. Addressed in v2.
- **No spatial structure:** Proximity tiers are abstract, not geographic.
- **Annual time step:** Sub-annual dynamics are abstracted.

Full limitations: `docs/validation.md` Section 4.

---

## Roadmap

**v1 — Band simulator** (current): Single band, 35 traits, calibrated.

**v2 — Clan simulator** (planned): Multiple bands interacting via trade,
raiding, intermarriage. Adds inter-group competition.

**v3 — Tribe/Chiefdom** (planned): Territorial dynamics, hereditary leadership.

**Game layer** (planned): Strategy game built on the simulation engine.

---

## License

See LICENSE file.
