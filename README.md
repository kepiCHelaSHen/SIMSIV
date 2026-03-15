# SIMSIV

### Simulation of Intersecting Social and Institutional Variables

SIMSIV is an agent-based social simulation grounded in behavioral genetics, evolutionary anthropology, and institutional economics. It models how human social structures emerge from first-principles interactions — reproduction, resource competition, status seeking, cooperation, jealousy, violence, pair bonding, and institutional constraints — with no hardwired outcomes.

**Band-level simulator v1.0. All findings are emergent. Nothing is scripted.**

The goal is not to recreate history. The goal is to explore how individual-level traits and incentives can generate large-scale social patterns.

---

## Scientific Foundation

Core mechanisms are informed by findings from behavioral genetics, evolutionary anthropology, and institutional economics.

**35 heritable traits**
Each trait has a literature-informed heritability coefficient (h²). Traits cover major behavioral domains including physical performance, cognition, personality, social behavior, reproductive strategy, and psychopathology risk.

**35×35 trait correlation matrix**
Traits interact through a correlation matrix capturing documented relationships such as aggression/cooperation tradeoffs and empathy/psychopathy opposition.

**Developmental plasticity**
Genotype and phenotype are separated. Early-life environment modifies trait expression (modeled through developmental baseline parameters).

**Demographic calibration**
Model parameters are calibrated toward ethnographic benchmarks such as violence rates, inequality levels, and fertility patterns observed in small-scale societies.

**Institutional economics**
Institutions emerge and evolve through norm enforcement, property rights, taxation, and prestige vs dominance status dynamics.

**Cultural evolution**
Beliefs spread through prestige bias, conformity pressure, and experience-based updating across five belief dimensions.

---

## Quick Start

Install dependencies:

```bash
pip install -r requirements.txt
```

Run a simulation:

```bash
python main.py
```

Custom parameters:

```bash
python main.py --seed 42 --years 200 --population 500
```

Launch the dashboard:

```bash
streamlit run dashboard/app.py
```

---

## What the Simulation Models

Each agent represents a full individual with biological, social, and cultural attributes.

Agents include:

- 35 heritable traits
- genotype / phenotype separation
- developmental plasticity
- 5 cultural belief dimensions
- 4 learnable skill domains
- medical history and genetic risk factors
- complete life biography logging
- bilateral trust ledger (reputation memory)
- emergent faction membership
- life stage roles (youth → elder)
- spatial proximity tiers (household → neighborhood → band)

Agents interact through cooperation, competition, coalition formation, mating dynamics, and institutional enforcement.

---

## The 9 Simulation Engines

Each simulation year runs through nine interacting subsystems.

| Step | Engine | Function |
|------|--------|----------|
| 1 | Environment | Seasonal cycles, scarcity shocks, epidemic events |
| 2 | Resources | Multi-phase resource distribution and inequality formation |
| 3 | Conflict | Violence triggers, coalition defense, punishment systems |
| 4 | Mating | Female choice, male competition, pair bonding, extra-pair mating |
| 5 | Reproduction | Heritable trait inheritance with mutation and birth spacing |
| 6 | Mortality | Aging, health risks, childbirth mortality |
| 7 | Pathology | Disease activation, trauma accumulation |
| 8 | Institutions | Norm enforcement, property rights, governance emergence |
| 9 | Reputation | Gossip networks, trust updates, faction detection |

All dynamics emerge from these mechanisms — nothing is scripted.

---

## The 35 Heritable Traits

Traits span several behavioral domains.

**Physical**
physical_strength, endurance, physical_robustness, pain_tolerance, longevity_genes, disease_resistance

**Cognitive**
intelligence_proxy, emotional_intelligence, impulse_control, conscientiousness

**Temporal**
future_orientation

**Personality**
risk_tolerance, novelty_seeking, anxiety_baseline, mental_health_baseline

**Social**
aggression_propensity, cooperation_propensity, dominance_drive, group_loyalty, outgroup_tolerance, empathy_capacity, conformity_bias, status_drive, jealousy_sensitivity

**Reproductive**
fertility_base, sexual_maturation_rate, maternal_investment, paternal_investment_preference, attractiveness_base

**Health / Psychopathology Risk**
psychopathy_tendency, mental_illness_risk, cardiovascular_risk, autoimmune_risk, metabolic_risk, degenerative_risk

---

## Emergent Patterns Observed

These patterns arise from the interaction rules rather than explicit programming.

- Cooperation and intelligence tend to increase over time
- Aggression often declines due to fitness costs
- Institutions can substitute for cooperative traits
- Monogamy reduces violence and unmated male populations
- Institutional strength can self-organize from low initial conditions
- Factions emerge naturally from trust network clustering
- Elite polygyny increases inequality without necessarily increasing violence
- Trait diversity stabilizes through mutation-selection balance

These outcomes vary across seeds and scenarios.

---

## Scenarios

SIMSIV includes multiple experimental scenarios.

| Scenario | Parameters | Purpose |
|----------|-----------|---------|
| `FREE_COMPETITION` | baseline | control scenario |
| `ENFORCED_MONOGAMY` | strong law + monogamy | mating system effects |
| `ELITE_POLYGYNY` | elite reproductive privilege | inequality dynamics |
| `HIGH_FEMALE_CHOICE` | stronger female selection | sexual selection |
| `RESOURCE_ABUNDANCE` | surplus resources | cooperation effects |
| `RESOURCE_SCARCITY` | resource shocks | institutional stress |
| `HIGH_VIOLENCE_COST` | lethal violence | aggression selection |
| `STRONG_STATE` | strong institutions | governance effects |
| `EMERGENT_INSTITUTIONS` | zero starting governance | norm emergence |
| `STRONG_PAIR_BONDING` | stable marriages | family stability |

---

## Project Structure

```
SIMSIV/
├── models/        agent and environment definitions
├── engines/       nine simulation subsystems
├── metrics/       ~130 tracked metrics
├── experiments/   scenario runner
├── autosim/       automated parameter calibration
├── dashboard/     Streamlit visualization
├── sandbox/       exploratory notebooks
├── tests/         smoke tests
├── docs/          design deep-dives
├── devlog/        development history
├── prompts/       build prompts
└── outputs/       run outputs
```

Key files:

- `config.py` — ~257 tunable parameters
- `simulation.py` — core simulation loop
- `targets.yaml` — calibration benchmarks

---

## Autosim Calibration

SIMSIV includes an automated calibration system.

It uses simulated annealing to search parameter space and match ethnographic targets including:

- inequality
- reproductive skew
- violence mortality
- child survival
- lifetime births
- bond dissolution
- cooperation levels
- aggression levels
- population growth

Run calibration:

```bash
python -m autosim.runner --experiments 500 --seeds 2 --years 150
```

---

## Architecture Guarantees

**Deterministic** — Same seed → identical run.

**Pure library** — Simulation logic is separate from visualization.

**Modular** — Engines interact through shared society state.

**Reproducible** — All configs are serializable and logged.

**Isolated instances** — Per-simulation `IdCounter`; running N simulations in sequence produces independent, non-colliding agent ID spaces.

**Bounded memory** — Event list capped to a rolling window (500 events); full event-type counts tracked as running totals; no OOM on long runs.

**Typed** — All Agent fields declared in dataclass; no dynamic attribute injection.

**Validated config** — `Config.load()` warns on unrecognized YAML keys.

**Tested** — pytest suite covering IdCounter isolation, Config validation, Society event windowing, partner index correctness, breed(), gini(), 10-tick run, population counting (22 test cases, 4 test files).

---

## Limitations

SIMSIV currently models band-level societies only.

Calibration improves plausibility but does not prove correctness. Results should be interpreted as hypotheses generated by a mechanistic simulation rather than definitive claims about human societies.

Higher-level social structures are planned but not yet implemented.

---

## Roadmap

**v1** — Band-level simulation (current)

**v2** — Clan and tribe models using band-level aggregates

**v3** — Chiefdom and early state formation

**Future** — A strategy game layer where civilizations emerge dynamically from the simulation.
