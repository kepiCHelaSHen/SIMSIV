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

Every mechanism is traceable to documented science:

- **Heritability coefficients** — per-trait h² values from behavioral genetics
  literature (intelligence ~0.65, aggression ~0.44, cooperation ~0.40, etc.)
- **Trait correlation matrix** — empirically grounded cross-trait correlations
  (aggression/cooperation −0.4, status_drive/risk_tolerance +0.3, etc.)
- **Developmental plasticity** — genotype/phenotype distinction; childhood
  environment modifies trait expression (orchid/dandelion model)
- **Demographic calibration** — validated against ethnographic data:
  violence rate 0.018 matches !Kung San (≈0.02), Gini 0.33-0.47 matches
  pre-industrial societies, TFR 4-7 matches natural fertility populations
- **Institutional economics** — law strength drift, property rights,
  norm emergence, prestige vs dominance dual-track status
- **Cultural evolution** — belief transmission via prestige bias,
  conformity, and experience-based updating

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
- 26 heritable traits (genetic, h²-weighted inheritance with mutation)
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
7. **Elite polygyny maximizes inequality (Gini 0.468)** but not violence — the
   resource privilege effect dominates the mating competition effect
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
├── models/          Agent, Environment, Society data models
├── engines/         9 simulation engines
├── metrics/         Per-tick data collection (~120 metrics)
├── experiments/     Scenario runner, multi-seed experiments, summarizer
├── dashboard/       Streamlit visual dashboard
├── sandbox/         IPython exploration harness
├── docs/            Design documents — one per deep dive (DD01-DD26)
├── devlog/          Complete development history
├── prompts/         26 deep dive implementation prompts
└── outputs/         Run outputs (CSV, PNG, JSON)
```

**Key files:**
- `config.py` — all ~250 tunable parameters in one dataclass
- `simulation.py` — tick orchestrator (pure library, zero IO)
- `docs/world_architecture.md` — complete model specification and v2 hierarchy design
- `CHAIN_PROMPT.md` — master design document

---

## Architecture Guarantees

- **Deterministic** — same seed produces identical results (scarcity computed
  once per tick, no per-call RNG consumption)
- **Pure library** — `sim.tick()` returns a metrics dict; any frontend consumes it
- **Modular** — engines share no state except via Society; no circular imports
- **Reproducible** — all configs YAML-serializable; runs fully logged

---

## Roadmap

**Current:** Band-level simulator (v1.0) — 500 agents, full individual simulation

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
