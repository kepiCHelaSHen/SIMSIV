# SIMSIV v1 — Provenance Log (Chain of Custody)

**Branch:** `v1-perfect`
**Date:** 2026-03-29
**Purpose:** Trace every coefficient from literature source through design specification to implementation commit. This is the evidence layer for JASSS methodology review.

---

## Provenance Chain Architecture

Every coefficient in SIMSIV v1 enters the codebase through one of three chains:

```
Chain A (GROUNDED):    Literature → DD Doc → Implementation Commit → Code
Chain B (CALIBRATED):  Literature Target → AutoSIM (816 experiments) → best_config.yaml → Code
Chain C (UNGROUNDED):  DD Doc (no literature) → Implementation Commit → Code  [STABILITY-DEPENDENT]
```

**Chain C coefficients have no external justification.** They must survive the Phase 3 Adversarial Critic (±20% perturbation, σ ≤ 0.030) to remain in the model.

---

## Implementation Commit Map

| SHA | Date | Phase | Description |
|-----|------|-------|-------------|
| `1cabb57` | 2026-02 | Initial | Skeleton: 6 engines with DD01-DD03 formulas |
| `c93bd3b` | 2026-02 | DD04 | Evolutionary selection pressure, fertility calibration |
| `24fb953` | 2026-02 | DD14-17 | 26 heritable traits, pathology, developmental biology |
| `5e3fe36` | 2026-03 | DD27 | Trait completion: 35 heritable traits |
| `6f3b943` | 2026-03 | Phase E | Engineering hardening: 13 fixes |
| `f88f107` | 2026-03 | Phase E.1 | Model quality review: 19 fixes across all engines |
| `ee3c2fe` | 2026-03 | Phase F+G | AutoSIM calibration score 1.000, validation 0.934 |
| `ab5b146` | 2026-03-15 | Paper 1 | Finalize — reproducibility statement, freeze for submission |
| `1dfc590` | 2026-03-29 | Phase 1.5 | Snap combat power to DD03 spec |
| `1b63bb9` | 2026-03-29 | Phase 1.5 | Ground death baseline to Keeley (1996) |
| `ff9a8a1` | 2026-03-29 | Phase 1.5 | Add Bowles/Fehr citations to punishment/coalition |

---

## SECTION A: GROUNDED COEFFICIENTS (Chain A)

Literature → DD Doc → Git Commit → Code File:Line

### A1. Conflict & Violence

| Coefficient | Value | Literature | DD Doc | Commit | Code Location |
|-------------|-------|-----------|--------|--------|---------------|
| Violence death fraction target | 0.05–0.15 | Keeley (1996) *War Before Civilization* | validation.md:98 | `ee3c2fe` | autosim/targets |
| Death chance baseline | 0.6 | Keeley (1996) via validation.md | DD03:97-98 | `1b63bb9` | conflict.py:458 |
| Combat power: aggression | 0.25 | DD03 internal spec | DD03:56 | `1dfc590` | conflict.py:351 |
| Combat power: status | 0.20 | DD03 internal spec | DD03:56 | `1dfc590` | conflict.py:352 |
| Combat power: health | 0.25 | DD03 internal spec | DD03:56 | `1dfc590` | conflict.py:353 |
| Combat power: risk_tolerance | 0.15 | DD03 internal spec | DD03:57 | `1dfc590` | conflict.py:354 |
| Combat power: intelligence | 0.05 | DD03 internal spec | DD03:58 | `1dfc590` | conflict.py:356 |
| Male risk mortality age 15-40 | config | Bowles (2008) via DD13 | DD13 | `c93bd3b` | mortality.py:201 |
| Coalition defense | — | Bowles & Gintis (2011) | DD11 | `ff9a8a1` | conflict.py:162 |
| Third-party punishment | — | Bowles (2006); Fehr & Gachter (2002) | DD11 | `ff9a8a1` | conflict.py:563 |
| Violence rate emergence | 0.08 | Bowles & Gintis (2011) | DD05:304 | `1cabb57` | institutions.py:304 |
| Reproductive skew threshold | 3.0 | Bowles (2006) | DD05:336 | `1cabb57` | institutions.py:336 |

### A2. Mating & Reproduction

| Coefficient | Value | Literature | DD Doc | Commit | Code Location |
|-------------|-------|-----------|--------|--------|---------------|
| Aggression penalty (female choice) | 0.5 | Archer (2009); Chagnon (1988) | DD01:10 | `10965fc` | mating.py:205 |
| Cooperation bonus (female choice) | 0.4 | Henrich et al. (2001) | DD01:10 | `10965fc` | mating.py:209 |
| Dissolution rate target | 0.10–0.30 | Betzig (1989) | validation.md:305 | `ee3c2fe` | autosim/targets |
| Fertility target | 4.0–7.0 | Bentley (1996); Howell (1979); Marlowe (2010) | validation.md:247 | `ee3c2fe` | autosim/targets |

### A3. Demographics & Mortality

| Coefficient | Value | Literature | DD Doc | Commit | Code Location |
|-------------|-------|-----------|--------|--------|---------------|
| Child survival target | 0.50–0.70 | Volk & Atkinson (2013); Hill & Hurtado (1996) | validation.md:205 | `ee3c2fe` | autosim/targets |
| Epidemic child vulnerability age | ≤10 | DD09 (epidemiological standard) | DD09 | `24fb953` | mortality.py:139 |
| Epidemic elder vulnerability age | ≥55 | DD09 (epidemiological standard) | DD09 | `24fb953` | mortality.py:141 |
| Low resources epidemic multiplier | 1.5 | DD09 (malnutrition-infection synergy) | DD09 | `24fb953` | mortality.py:150 |

### A4. Resources & Cooperation

| Coefficient | Value | Literature | DD Doc | Commit | Code Location |
|-------------|-------|-----------|--------|--------|---------------|
| Gini target | 0.30–0.50 | Borgerhoff Mulder et al. (2009) | validation.md:38 | `ee3c2fe` | autosim/targets |
| Cooperation target | 0.25–0.70 | Henrich et al. (2001) | validation.md:349 | `ee3c2fe` | autosim/targets |
| Aggression target | 0.30–0.60 | Archer (2009) | validation.md:383 | `ee3c2fe` | autosim/targets |
| Intelligence competitive weight | 0.25 | DD02/DD08 | DD08 | `1cabb57` | resources.py:167 |
| Status competitive weight | 0.25 | DD08 | DD08 | `1cabb57` | resources.py:168 |
| Experience competitive weight | 0.15 | DD02/DD08 | DD08 | `1cabb57` | resources.py:169 |
| Wealth competitive weight | 0.15 | DD02/DD08 | DD08 | `1cabb57` | resources.py:173 |
| Prestige/dominance pool split | 0.6/0.4 | DD08 | DD08 | `1cabb57` | resources.py:353-354 |
| Competitive weight power | 3 | DD02 | DD02 | `1cabb57` | resources.py:203 |
| Trust gain from sharing | 0.05 | DD02/DD15 | DD02 | `1cabb57` | resources.py:320 |

### A5. Institutions & Beliefs

| Coefficient | Value | Literature | DD Doc | Commit | Code Location |
|-------------|-------|-----------|--------|--------|---------------|
| Conformity amplification | 0.3 | Henrich & Boyd (1998) | DD05:215 | `1cabb57` | institutions.py:215 |
| Conflict winner VA boost | 1.0 × rate | Bowles (2011) | DD25 | `1cabb57` | reputation.py:238 |
| Conflict winner hierarchy | 0.67 × rate | Bowles & Gintis (2011) | DD25 | `1cabb57` | reputation.py:241 |
| Conflict winner coop reduction | 0.67 × rate | Bowles & Gintis (2011) | DD25 | `1cabb57` | reputation.py:243 |
| Punishment VA reduction | 1.33 × rate | Bowles (2006) | DD05 | `1cabb57` | reputation.py:259 |
| Arbitration coop boost | 0.67 × rate | Bowles (2011) | DD20 | `1cabb57` | reputation.py:267 |
| Sharing coop boost | 0.33 × rate | Bowles & Gintis (2011) | DD02 | `1cabb57` | reputation.py:288 |
| Novelty seeking conformity reduction | 0.5 | Henrich & Boyd (1998) | DD25 | `1cabb57` | reputation.py:218 |
| Age learning decline | 0.03/yr | Anthropological data | DD26 | `24fb953` | reputation.py:369 |

---

## SECTION B: CALIBRATED COEFFICIENTS (Chain B)

Literature Target → AutoSIM Optimization (816 experiments, commit `ee3c2fe`) → best_config.yaml → Code

**All calibrated values are [UNCERTAIN — TARGET FOR PERTURBATION].**

| Parameter | AutoSIM Value | Literature Target | Target Source | Config Location |
|-----------|--------------|------------------|---------------|-----------------|
| resource_equal_floor | 0.400 | Gini 0.30–0.50 | Borgerhoff Mulder (2009) | config.py:67 |
| resource_abundance | 0.985 | Pop growth 0.001–0.015 | Hassan (1981) | config.py:62 |
| aggression_production_penalty | 0.600 | Aggression 0.30–0.60 | Archer (2009) | config.py:69 |
| cooperation_network_bonus | 0.059 | Cooperation 0.25–0.70 | Henrich et al. (2001) | config.py:74 |
| cooperation_sharing_rate | 0.125 | Cooperation 0.25–0.70 | Henrich et al. (2001) | config.py:75 |
| wealth_diminishing_power | 0.737 | Gini 0.30–0.50 | Borgerhoff Mulder (2009) | config.py:66 |
| subsistence_floor | 1.173 | Pop growth 0.001–0.015 | Hassan (1981) | config.py:68 |
| scarcity_severity | 0.300 | Child survival 0.50–0.70 | Volk & Atkinson (2013) | config.py:63 |
| child_investment_per_year | 0.350 | Fertility 4.0–7.0 | Bentley (1996) | config.py:77 |
| conflict_base_probability | 0.150 | Violence 0.05–0.15 | Keeley (1996) | config.py:86 |
| violence_cost_health | 0.176 | Violence 0.05–0.15 | Keeley (1996) | config.py:89 |
| violence_death_chance | 0.115 | Violence 0.05–0.15 | Keeley (1996) | config.py:91 |
| violence_cost_resources | 0.142 | Violence 0.05–0.15 | Keeley (1996) | config.py:90 |
| flee_threshold | 0.294 | Violence 0.05–0.15 | Keeley (1996) | config.py:95 |
| seasonal_conflict_boost | 0.294 | Violence 0.05–0.15 | Keeley (1996) | config.py:96 |
| pair_bond_dissolution_rate | 0.020 | Dissolution 0.10–0.30 | Betzig (1989) | config.py:78 |
| pair_bond_strength | 0.679 | Dissolution 0.10–0.30 | Betzig (1989) | config.py:79 |
| base_conception_chance | 0.800 | Fertility 4.0–7.0 | Bentley (1996) | config.py:81 |
| female_choice_strength | 0.340 | Mating ineq. 0.40–0.80 | Betzig (2012) | config.py:82 |
| infidelity_base_rate | 0.034 | Mating ineq. 0.40–0.80 | Betzig (2012) | config.py:84 |
| maternal_age_fertility_decline | 0.033 | Fertility 4.0–7.0 | Bentley (1996) | config.py:83 |
| maternal_health_cost | 0.027 | Fertility 4.0–7.0 | Bentley (1996) | config.py:85 |
| birth_interval_years | 2 | Fertility 4.0–7.0 | Bentley (1996) | config.py:80 |
| age_first_reproduction | 14 | Fertility 4.0–7.0 | Howell (1979) | config.py:87 |
| age_max_reproduction_female | 49 | Fertility 4.0–7.0 | Howell (1979) | config.py:88 |
| orphan_mortality_multiplier | 1.200 | Child survival 0.50–0.70 | Hill & Hurtado (1996) | config.py:92 |
| grandparent_survival_bonus | 0.083 | Child survival 0.50–0.70 | Hill & Hurtado (1996) | config.py:93 |
| widowhood_mourning_years | 0 | Dissolution 0.10–0.30 | Betzig (1989) | config.py:94 |
| mortality_base | 0.006 | Pop growth 0.001–0.015 | Hassan (1981) | config.py:97 |
| childhood_mortality_annual | 0.054 | Child survival 0.50–0.70 | Volk & Atkinson (2013) | config.py:98 |
| health_decay_per_year | 0.010 | Pop growth 0.001–0.015 | Hassan (1981) | config.py:99 |
| epidemic_base_probability | 0.030 | Pop growth 0.001–0.015 | Hassan (1981) | config.py:100 |
| epidemic_lethality_base | 0.254 | Pop growth 0.001–0.015 | Hassan (1981) | config.py:101 |
| male_risk_mortality_multiplier | 2.120 | Violence 0.05–0.15 | Keeley (1996) | config.py:102 |
| childbirth_mortality_rate | 0.010 | Pop growth 0.001–0.015 | Hassan (1981) | config.py:103 |

---

## SECTION C: STABILITY-DEPENDENT COEFFICIENTS (Chain C)

**These ~398 coefficients have no external literature justification.** They entered the codebase through DD design docs authored by Claude (AI-inferred) and were never validated against empirical data.

**Every coefficient in this section is a primary target for the Phase 3 Adversarial Critic (±20% perturbation, σ ≤ 0.030 gate).**

### C1. conflict.py — 77 STABILITY-DEPENDENT constants

| ID | Line | Value | Context | DD | Bowles |
|----|------|-------|---------|-----|--------|
| C1.01 | 46 | 0.6 | Impulse control multiplier | DD15 | |
| C1.02 | 46 | 0.3 | Impulse control gate floor | DD15 | |
| C1.03 | 56 | 0.1 | Jealousy conflict post-multiplier | — | |
| C1.04 | 59 | 5.0 | Resource stress divisor | — | |
| C1.05 | 59 | 0.1 | Resource stress scaling | — | |
| C1.06 | 60 | 0.5 | Mental health dampening | DD15 | |
| C1.07 | 63 | 0.05 | Status drive contribution | — | |
| C1.08 | 71 | 0.2 | Seasonal conflict boost default | DD10 | |
| C1.09 | 76 | 0.5 | Law strength base multiplier | — | |
| C1.10 | 76 | 0.5 | Punishment strength multiplier | — | |
| C1.11 | 77 | 0.8 | Institutional suppression dampening | — | |
| C1.12 | 80 | 0.3 | Cooperation conflict dampening | DD03 | |
| C1.13 | 83 | 0.3 | Empathy suppression multiplier | DD15 | |
| C1.14 | 83 | 0.5 | Empathy gate floor | DD15 | |
| C1.15 | 88 | 0.5 | Psychopathy deterrence suppression | DD27 | |
| C1.16 | 88 | 0.3 | Network deterrence gate floor | DD27 | |
| C1.17 | 89 | 0.05 | Per-ally conflict reduction | DD03 | |
| C1.18 | 103 | 0.5 | Elder conflict multiplier | DD22 | |
| C1.19 | 106 | 0.4 | Anxiety suppression multiplier | DD27 | |
| C1.20 | 106 | 0.3 | Anxiety gate floor | DD27 | |
| C1.21 | 112 | 0.1 | Violence acceptability boost | DD25 | |
| C1.22 | 114 | 0.15 | Violence acceptability suppress | DD25 | |
| C1.23 | 123 | 0.5 | Conflict probability cap | DD03 | |
| C1.24 | 136 | 0.15 | Pain tolerance flee contribution | DD15 | |
| C1.25 | 140 | 0.15 | Degenerative flee boost | DD17 | |
| C1.26 | 144 | 0.5 | Flee chance scaling | DD03 | |
| C1.27 | 148 | 0.02 | Dominance gain on flee | DD03 | |
| C1.28 | 168 | 0.4 | Coalition defense coop threshold | DD11 | |
| C1.29 | 169 | 0.3 | Coalition defense health threshold | DD11 | |
| C1.30 | 174 | 0.3 | Group loyalty defense boost | DD27 | `[BOWLES]` |
| C1.31 | 178 | 0.03 | Aggressor dominance loss (defense) | DD11 | |
| C1.32 | 180 | 0.03 | Defender prestige gain | DD11 | |
| C1.33 | 181 | 0.05 | Trust memory: defender ↔ target | DD11 | |
| C1.34 | 183 | -0.1 | Trust memory: aggressor → defender | DD11 | |
| C1.35 | 241 | 4.0 | Household proximity multiplier | DD18 | |
| C1.36 | 242 | 2.0 | Neighborhood proximity multiplier | DD18 | |
| C1.37 | 248 | 0.3 | Cross-sex targeting weight | DD03 | |
| C1.38 | 258 | 1.5 | Trust-based targeting baseline | DD03 | |
| C1.39 | 263 | 3.0 | Mate-rival weight boost | DD03 | |
| C1.40 | 267 | 0.2 | Status challenge threshold | DD08 | |
| C1.41 | 268 | 1.5 | Similar-status boost | DD08 | |
| C1.42 | 275 | 1.5 | Resource envy threshold | DD03 | |
| C1.43 | 276 | 1.3 | Resource-rich target boost | DD03 | |
| C1.44 | 343 | 20.0 | Resource edge divisor | DD08 | |
| C1.45 | 357 | 0.05 | Physical robustness (DD15 additive) | DD15 | |
| C1.46 | 358 | 0.05 | Dominance drive (DD15 additive) | DD15 | |
| C1.47 | 359 | 0.03 | Pain tolerance (DD15 additive) | DD15 | |
| C1.48 | 374 | 1.4 | Male physical strength multiplier | DD27 | |
| C1.49 | 387 | 3 | Ally count cap | DD03 | |
| C1.50 | 387 | 0.03 | Per-ally combat bonus | DD03 | |
| C1.51 | 416 | 0.7 | Close-fight baseline scale | DD03 | |
| C1.52 | 416 | 1.6 | Power diff consequence scaling | DD03 | |
| C1.53 | 421 | 0.4 | Robustness damage absorption | DD15 | |
| C1.54 | 421 | 0.5 | Min robustness reduction | DD15 | |
| C1.55 | 428 | 0.5 | Base loot fraction | DD05 | |
| C1.56 | 446 | 0.02 | Prestige loss from violence | DD03 | |
| C1.57 | 449 | 0.3 | Winner health cost fraction | DD03 | |
| C1.58 | 473 | 0.05 | Reputation loss from violence | DD03 | |
| C1.59 | 475 | 0.2 | Decisive victory threshold | DD03 | |
| C1.60 | 476 | 0.02 | Decisive victory reputation gain | DD03 | |
| C1.61 | 478 | -0.2 | Trust loss: aggressor → target | DD03 | |
| C1.62 | 479 | -0.3 | Trust loss: target → aggressor | DD03 | |
| C1.63 | 495 | -0.08 | Bystander distrust of aggressor | DD03 | |
| C1.64 | 497 | 0.6 | Allied bystander threshold | DD03 | |
| C1.65 | 498 | -0.1 | Allied bystander amplified distrust | DD03 | |
| C1.66 | 506 | 0.1 | Bond dissolution base factor | — | |
| C1.67 | 506 | 0.5 | Aggression dissolution multiplier | — | |
| C1.68 | 511 | -0.25 | Departing partner trust loss | — | |
| C1.69 | 529 | 0.1 | Punishment reputation penalty mult | DD11 | |
| C1.70 | 532 | 5 | Resource fine multiplier | DD11 | |
| C1.71 | 572 | 0.3 | Punishment cooperation multiplier | DD11 | `[BOWLES]` |
| C1.72 | 574 | 0.15 | Group loyalty punishment boost | DD27 | `[BOWLES]` |
| C1.73 | 577 | 0.3 | Violence acceptability punishment | DD25 | |
| C1.74 | 589 | -0.15 | Punisher trust toward aggressor | DD11 | |
| C1.75 | 590 | -0.1 | Aggressor trust toward punisher | DD11 | |
| C1.76 | 593 | 0.02 | Prestige gain from punishment | DD11 | `[BOWLES]` |
| C1.77 | 246 | 1.67 | Conflict loser VA reduction | DD25 | `[BOWLES]` |

### C2. resources.py — 118 STABILITY-DEPENDENT constants

Key ungrounded clusters (full list in v1_coefficient_audit.md):

| Cluster | Count | Lines | Impact |
|---------|-------|-------|--------|
| Resource acquisition weights | 12 | 166-203 | Drive inequality |
| Cooperation sharing mechanics | 15 | 266-320 | Drive altruism levels |
| Prestige/dominance scoring | 11 | 338-376 | Drive status hierarchy |
| Storage and decay | 14 | 102-131 | Drive wealth accumulation |
| Signaling/bluffing | 12 | 440-476 | Drive honest signaling |
| Tool production | 8 | 493-541 | Drive technology effects |
| Child investment | 5 | 222-231 | Drive parental drain |

### C3. mating.py — 47 STABILITY-DEPENDENT constants

Key ungrounded clusters:

| Cluster | Count | Lines | Impact |
|---------|-------|-------|--------|
| Bond dissolution factors | 8 | 81-101 | Drive pair bond stability |
| Mate value weights | 12 | 197-268 | Drive sexual selection |
| EPC mechanics | 6 | 373-410 | Drive paternity uncertainty |
| Contest mechanics | 4 | 290-298 | Drive male competition |

### C4. reproduction.py — 19 STABILITY-DEPENDENT constants

| Cluster | Count | Lines | Impact |
|---------|-------|-------|--------|
| Conception modifiers | 8 | 46-98 | Drive fertility rates |
| Infant survival factors | 11 | 135-214 | Drive child mortality |

### C5. mortality.py — 48 STABILITY-DEPENDENT constants

| Cluster | Count | Lines | Impact |
|---------|-------|-------|--------|
| Health decay mechanics | 8 | 58-76 | Drive lifespan |
| Age-based death formula | 3 | 189-192 | Drive age distribution |
| Childhood mortality modifiers | 5 | 101-113 | Drive child survival |
| Epidemic modifiers | 8 | 146-160 | Drive epidemic impact |
| Developmental plasticity | 12 | 237-290 | Drive trait development |
| Belief initialization weights | 10 | 335-347 | Drive cultural transmission |

### C6. pathology.py — 33 STABILITY-DEPENDENT constants

| Cluster | Count | Lines | Impact |
|---------|-------|-------|--------|
| Condition activation | 12 | 60-96 | Drive disease burden |
| Epigenetic mechanics | 10 | 177-197 | Drive intergenerational stress |
| Trauma contagion | 8 | 205-224 | Drive social pathology |

### C7. institutions.py — 25 STABILITY-DEPENDENT constants

| Cluster | Count | Lines | Impact |
|---------|-------|-------|--------|
| Drift mechanics | 8 | 205-270 | Drive institutional evolution |
| Belief coupling | 5 | 249-262 | Drive belief-institution feedback |
| Emergence thresholds | 4 | 310-346 | Drive institution emergence |
| Inheritance mechanics | 4 | 96-132 | Drive wealth transmission |

### C8. reputation.py — 16 STABILITY-DEPENDENT constants

| Cluster | Count | Lines | Impact |
|---------|-------|-------|--------|
| Gossip mechanics | 6 | 103-130 | Drive information spread |
| Skill learning | 8 | 374-458 | Drive skill development |
| Psychopathy reputation | 2 | 161-163 | Drive exploiter success |

---

## SECTION D: ADVERSARIAL CRITIC TARGET PRIORITIZATION

Coefficients are ranked by **impact on the paper's central claim** (institutions substitute for genes in prosocial trait evolution):

### Priority 1: Claim-Critical (must survive perturbation)
These directly affect the institution-gene substitution finding.

| ID | Coefficient | Value | Why Critical |
|----|-------------|-------|-------------|
| C1.09-11 | Institutional suppression (0.5, 0.5, 0.8) | conflict.py | Directly controls how institutions reduce violence |
| C7.* | Drift mechanics (8 coefficients) | institutions.py | Controls institutional emergence and evolution |
| C1.71-76 | Punishment mechanics (6 coefficients) | conflict.py | Controls altruistic punishment |
| B.* | All 35 AutoSIM calibrated params | config.py | Model achieves targets only at these values |

### Priority 2: Selection-Relevant (affect evolutionary dynamics)
| ID | Coefficient | Why Relevant |
|----|-------------|-------------|
| C1.30 | Group loyalty defense boost (0.3) | Between-group selection mechanism |
| C2 prestige cluster | Prestige scoring (11 coefficients) | Drive status hierarchy → mate access |
| C3 mate value cluster | Mate value weights (12 coefficients) | Drive sexual selection direction |
| C1.48 | Male strength multiplier (1.4) | Sex-differential combat → mating skew |

### Priority 3: Demographic (affect population dynamics)
| ID | Coefficient | Why Relevant |
|----|-------------|-------------|
| C4.* | Conception modifiers (8) | Drive fertility → population growth |
| C5 health cluster | Health decay (8) | Drive lifespan → generational turnover |
| C5 childhood cluster | Childhood mortality (5) | Drive child survival → fitness |

### Priority 4: Social Fabric (affect cooperation/trust)
| ID | Coefficient | Why Relevant |
|----|-------------|-------------|
| C2 sharing cluster | Cooperation sharing (15) | Drive cooperative equilibrium |
| C8 gossip cluster | Gossip mechanics (6) | Drive information/reputation spread |
| C1.61-65 | Trust memory updates (5) | Drive social network structure |

---

## SECTION E: LITERATURE BIBLIOGRAPHY

All external sources cited in the provenance chain:

| Author(s) | Year | Title | Journal | Used For |
|-----------|------|-------|---------|----------|
| Archer, J. | 2009 | Does sexual selection explain human sex differences in aggression? | Behavioral and Brain Sciences, 32(3-4) | Aggression target 0.30-0.60; female choice grounding |
| Bentley, G.R. | 1996 | How did prehistoric women bear "man the hunter"? | American Journal of Physical Anthropology | Fertility target 4.0-7.0 |
| Betzig, L. | 1989 | Causes of conjugal dissolution | Ethology and Sociobiology, 10 | Dissolution target 0.10-0.30 |
| Betzig, L. | 2012 | Means, variances, and ranges in reproductive success | Evolution and Human Behavior, 33(4) | Mating inequality target 0.40-0.80 |
| Borgerhoff Mulder, M. et al. | 2009 | Intergenerational wealth transmission | Science, 326(5953) | Gini target 0.30-0.50 |
| Bowles, S. | 2006 | Group competition, reproductive leveling | Science, 314(5805) | Group selection framework; punishment grounding |
| Bowles, S. | 2008 | Conflict: Altruism's midwife | Nature, 456 | Male risk mortality |
| Bowles, S. & Gintis, H. | 2011 | A Cooperative Species | Princeton University Press | Coalition defense; belief experience updates |
| Chagnon, N. | 1988 | Life histories, blood revenge | Science, 239(4843) | Violence death data; aggression-fitness link |
| Fehr, E. & Gachter, S. | 2002 | Altruistic punishment in humans | Nature, 415 | Third-party punishment grounding |
| Hassan, F. | 1981 | Demographic Archaeology | Academic Press | Pop growth target 0.001-0.015 |
| Henrich, J. & Boyd, R. | 1998 | The evolution of conformist transmission | Evolution and Human Behavior, 19 | Conformity amplification |
| Henrich, J. et al. | 2001 | In search of homo economicus | American Economic Review, 91(2) | Cooperation target 0.25-0.70 |
| Hill, K. & Hurtado, A.M. | 1996 | Ache Life History | Aldine de Gruyter | Child survival data; orphan effects |
| Howell, N. | 1979 | Demography of the Dobe !Kung | Academic Press | Fertility and mortality data |
| Keeley, L.H. | 1996 | War Before Civilization | Oxford University Press | Violence death target 0.05-0.15 |
| Marlowe, F.W. | 2010 | The Hadza | University of California Press | Fertility supplementary data |
| Volk, A. & Atkinson, J. | 2013 | Infant and child death in the human environment | Evolution and Human Behavior, 34(3) | Child survival target 0.50-0.70 |
| Walker, P.L. | 2001 | A bioarchaeological perspective on violence | Annual Review of Anthropology, 30 | !Kung violence data |

---

*Generated 2026-03-29. This document is the evidence layer for JASSS submission 2026:81:1 (ref 6029). It proves the chain of custody from anthropological literature to code for all grounded/calibrated coefficients, and explicitly flags all AI-inferred constants as stability-dependent targets for Phase 3 adversarial perturbation testing.*
