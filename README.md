# SIMSIV

### Simulation of Intersecting Social and Institutional Variables

SIMSIV is a calibrated agent-based simulation of band-level human social
evolution, grounded in behavioral genetics, evolutionary anthropology, and
institutional economics. Every agent is a complete simulated person with a
genome, developmental history, medical biography, earned skills, culturally
transmitted beliefs, and a life story from birth to death.

**Band-level simulator v1.0 — 35 heritable traits, 12 engines, calibrated to
score 1.000 against 9 anthropological benchmarks.**

**v2.0 JASSS Resubmission** — Paired-seed 500-year divergence experiment
confirms cognitive substitution (intelligence p=0.023, impulse control p=0.031)
and discovers selection sheltering (the state preserves aggressive genotypes).

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

### v2.0 Paired-Seed Divergence (500yr, 10 paired seeds)

- **Cognitive substitution:** Intelligence (p=0.023, d=0.87) and impulse control
  (p=0.031, d=0.80) are displaced significantly more under anarchy than the state
- **Selection sheltering:** The state *preserves* aggressive genotypes by suppressing
  the lethal violence that would otherwise eliminate them before reproduction
- **Cooperation attractor:** Cooperation converges to ~0.51 regardless of governance
  regime — scale-invariant across N=250-1000 (Squazzoni N-Test)

### v1.0 Scenario Experiments

- Cooperation and intelligence reliably selected for across all scenarios
- Aggression reliably selected against (5 independent fitness cost channels)
- ENFORCED_MONOGAMY reduces violence 37%, unmated males 65%
- STRONG_STATE reduces Gini 40%, violence 49% — without changing cooperation trait
- Law strength self-organizes from 0 → 0.83 in EMERGENT_INSTITUTIONS over 200yr
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
├── engines/              # 12 simulation subsystems
├── metrics/              # ~130 tracked metrics per tick
├── experiments/          # Scenario runner and definitions
├── autosim/              # Calibration engine + results
├── scripts/              # Validation, experiments, divergence scripts
├── results/              # RESULTS_SUMMARY.md (definitive data manifest)
├── dashboard/            # Streamlit visualization
├── tests/                # Test suite
├── docs/                 # ODD Protocol, manuscript, figures, validation
│   └── figures/          # 7 publication figures (F1-F8 + originals)
├── devlog/               # Full development history
└── prompts/              # Executable build prompts
```

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
