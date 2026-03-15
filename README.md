# SIMSIV
### Simulation of Intersecting Social and Institutional Variables

An agent-based social simulation grounded in behavioral genetics, evolutionary
anthropology, and institutional economics. Models how human social structures
emerge from first-principles interactions — reproduction, resource competition,
status seeking, cooperation, jealousy, violence, pair bonding, and institutional
constraints — with no hardwired outcomes.

**Band-level simulator v1.0. All findings are emergent. Nothing is scripted.**

---

## Scientific Foundation

Every mechanism is grounded in documented science:

- **35 heritable traits** — per-trait h² values from behavioral genetics
  literature. Covers all major domains: physical performance, cognitive,
  personality, social, reproductive, temporal, psychopathology spectrum
- **35×35 correlation matrix** — empirically grounded cross-trait correlations
  (aggression/cooperation −0.4, psychopathy/empathy −0.5, etc.)
- **Developmental plasticity** — genotype/phenotype distinction; childhood
  environment modifies trait expression (orchid/dandelion model via
  mental_health_baseline)
- **Demographic calibration** — calibrated against ethnographic benchmarks:
  violence rate 0.018 matches !Kung San (≈0.02), Gini 0.33-0.47 matches
  pre-industrial societies
- **Institutional economics** — law strength drift, property rights,
  norm emergence, prestige vs dominance dual-track status
- **Cultural evolution** — belief transmission via prestige bias,
  conformity, and experience-based updating (5 belief dimensions)

---

## Quick Start

```bash
pip install -r requirements.txt
python main.py
python main.py --seed 42 --years 200 --population 500
streamlit run dashboard/app.py
```

---

## What's Simulated

**Every agent is a complete individual with:**
- **35 heritable traits** with real h² coefficients — physical strength,
  endurance, group loyalty, outgroup tolerance, future orientation,
  conscientiousness, psychopathy tendency, anxiety baseline, paternal
  investment preference, plus 26 from DD01-DD26
- Genotype separate from phenotype (developmental plasticity at age 15)
- 5 cultural belief dimensions (non-heritable, socially transmitted)
- 4 skill domains (experiential learning, decay, mentoring)
- Medical history and 5 heritable condition risks
- Complete life biography (birth to death, all events logged)
- Bilateral trust ledger (reputation memory, gossip-mediated)
- Faction membership (emergent from trust network topology)
- Life stage role (youth / prime / mature / elder with distinct behaviors)
- Proximity tier (household → neighborhood → band)

**9 simulation engines per annual tick:**

| Step | Engine | Core Function |
|------|---------|---------------|
| 1 | Environment | Seasonal cycles, scarcity shocks, epidemic events |
| 2 | Resources | 8-phase distribution — subsistence, tools, prestige goods |
| 3 | Conflict | Violence triggers, deterrence, coalition defense, third-party punishment |
| 4 | Mating | Female choice, male competition, pair bonds, EPC, paternity uncertainty |
| 5 | Reproduction | h²-weighted inheritance, developmental plasticity, birth spacing |
| 6 | Mortality | Age decay, health death, sex-differential mortality, childbirth risk |
| 7 | Pathology | Condition activation, trauma accumulation, epigenetic load |
| 8 | Institutions | Inheritance, norm enforcement, institutional drift and emergence |
| 9 | Reputation | Gossip, trust decay, belief updates, skill learning, faction detection |

---

## The 35 Heritable Traits

| Domain | Traits |
|--------|--------|
| **Physical** | physical_strength, endurance, physical_robustness, pain_tolerance, longevity_genes, disease_resistance |
| **Cognitive** | intelligence_proxy, emotional_intelligence, impulse_control, conscientiousness |
| **Temporal** | future_orientation |
| **Personality** | risk_tolerance, novelty_seeking, anxiety_baseline, mental_health_baseline |
| **Social** | aggression_propensity, cooperation_propensity, dominance_drive, group_loyalty, outgroup_tolerance, empathy_capacity, conformity_bias, status_drive, jealousy_sensitivity |
| **Reproductive** | fertility_base, sexual_maturation_rate, maternal_investment, paternal_investment_preference, attractiveness_base |
| **Psychopathology** | psychopathy_tendency, mental_illness_risk, cardiovascular_risk, autoimmune_risk, metabolic_risk, degenerative_risk |

---

## Key Empirical Findings

These patterns emerge from rules — no outcome is hardwired:

1. **Cooperation and intelligence are reliably selected for** across all scenarios
2. **Aggression is reliably selected against** — fitness cost exceeds benefit
3. **Institutions substitute for traits** — strong governance reduces selection
   pressure for cooperative genes (STRONG_STATE cooperation trait lower than BASELINE)
4. **Monogamy reduces violence 37% and unmated males 40%** vs free competition
5. **Institutional strength self-organizes** from 0 → 0.48 law strength over 200yr
   in EMERGENT_INSTITUTIONS scenario — driven purely by cooperation/violence balance
6. **Factions emerge naturally** from kin trust clusters via connected-component
   detection — not assigned, not scripted
7. **Elite polygyny maximizes inequality (Gini 0.468)** but not violence
8. **Trait diversity maintained** at σ~0.09 by rare large mutations (5% chance,
   3× sigma) even under strong directional selection

---

## Scenarios

| Scenario | Key Parameters | Tests |
|----------|---------------|-------|
| `FREE_COMPETITION` | Baseline defaults | Null hypothesis |
| `ENFORCED_MONOGAMY` | law=0.7, mating="monogamy" | Monogamy → violence/inequality |
| `ELITE_POLYGYNY` | elite_privilege=3.0, max_mates=5 | Status inequality → social structure |
| `HIGH_FEMALE_CHOICE` | female_choice_strength=0.95 | Sexual selection → trait evolution |
| `RESOURCE_ABUNDANCE` | resource_abundance=2.5 | Surplus → cooperation/violence |
| `RESOURCE_SCARCITY` | resource_abundance=0.4, scarcity_prob=0.15 | Stress → institutions |
| `HIGH_VIOLENCE_COST` | violence_cost_health=0.45 | Lethality → aggression selection |
| `STRONG_STATE` | law=0.8, tax=0.15, property_rights=0.5 | Governance → trait substitution |
| `EMERGENT_INSTITUTIONS` | all institutions start at 0 | Self-organization of norms |
| `STRONG_PAIR_BONDING` | bond_strength=0.9, dissolution=0.02 | Stability → child outcomes |

---

## Project Structure

```
SIMSIV/
├── models/          Agent (35 traits), Environment, Society
├── engines/         9 simulation engines
├── metrics/         Per-tick data collection (~130 metrics)
├── experiments/     Scenario runner, multi-seed experiments, summarizer
├── autosim/         Autonomous calibration — Mode A parameter optimization
├── dashboard/       Streamlit visual dashboard
├── sandbox/         IPython exploration harness
├── tests/           5 smoke tests (pytest)
├── docs/            Design documents — DD01-DD27 + world architecture
├── devlog/          Complete development history
├── prompts/         27 deep dive implementation prompts
└── outputs/         Run outputs (CSV, PNG, JSON)
```

**Key files:**
- `config.py` — ~257 tunable parameters in one dataclass
- `simulation.py` — tick orchestrator (pure library, zero IO)
- `docs/world_architecture.md` — complete model specification and v2 hierarchy design
- `CHAIN_PROMPT.md` — master design document
- `autosim/targets.yaml` — calibration targets with anthropological sources

---

## Architecture Guarantees

- **Deterministic** — same seed produces identical results
- **Pure library** — `sim.tick()` returns a metrics dict; any frontend consumes it
- **Modular** — engines share no state except via Society; no circular imports
- **Reproducible** — all configs YAML-serializable; runs fully logged
- **Tested** — 5 pytest smoke tests covering breed(), gini(), config round-trip,
  10-tick run, population counting

---

## Autosim Calibration

Mode A parameter optimization with simulated annealing, calibrated against
9 anthropological targets (resource Gini, reproductive skew, violence death
fraction, child survival, lifetime births, bond dissolution, cooperation,
aggression, population growth).

```bash
python -m autosim.runner --experiments 500 --seeds 2 --years 150
```

---

## Roadmap

**Current:** Band-level simulator (v1.0) — 35 traits, 500 agents, DD01-DD27 complete

**v2:** Clan and tribe simulators — bands export aggregate fingerprints upward;
clan-level dynamics (trade, raiding, intermarriage, cultural drift) operate on
band fingerprints without simulating individuals

**v3:** Chiefdom and state simulators — full five-level hierarchy
(band → clan → tribe → chiefdom → state)

**Game layer:** Civilization-style game where social structures emerge from the
simulation — no scripted history, no hardwired outcomes

See `docs/world_architecture.md` for the complete hierarchical design.

---

*Not a political project. Not a moral argument.*
*A scientific instrument that happens to generate compelling emergent stories.*
