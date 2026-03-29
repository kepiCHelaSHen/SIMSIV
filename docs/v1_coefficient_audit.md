# SIMSIV v1 Coefficient Audit — Line-Item Manifest

**Branch:** `v1-perfect` (from tag `v1.0-paper1-submitted`)
**Date:** 2026-03-29
**Scope:** All 9 v1 engine files, cross-referenced against 27 Deep Dive docs + AutoSIM best_config.yaml
**Purpose:** Phase 1 of V1 Perfect Pass — catalog every coefficient for provenance tracing and adversarial perturbation testing

---

## Classification Key

| Label | Meaning | Perturbation Target? |
|-------|---------|---------------------|
| **GROUNDED** | Has specific literature citation (author + year) | No — defended by source |
| **CALIBRATED** | Value from AutoSIM tuning (816 experiments) | **[UNCERTAIN - TARGET FOR PERTURBATION]** |
| **UNGROUNDED** | AI-inferred, no literature or calibration source | **[UNCERTAIN - TARGET FOR PERTURBATION]** |

## Bowles Filter

Coefficients tagged `[BOWLES]` are related to Fst calculation, migration rates, death-in-conflict probability, altruistic cost *c*, or between-group selection dynamics. These require special attention for any future multi-band extension.

---

## Summary Statistics

| Engine File | Total Coefficients | GROUNDED | CALIBRATED | UNGROUNDED | Bowles-Tagged |
|-------------|-------------------|----------|------------|------------|---------------|
| conflict.py | 90 | 0 | 0 | 90 | 6 |
| resources.py | 136 | 10 | 8 | 118 | 22 |
| mating.py | 50 | 0 | 1 | 49 | 5 |
| reproduction.py | 22 | 0 | 3 | 19 | 0 |
| mortality.py | 52 | 4 | 0 | 48 | 1 |
| pathology.py | 63 | 29 | 1 | 33 | 0 |
| institutions.py | 40 | 3 | 12 | 25 | 11 |
| reputation.py | 40 | 8 | 16 | 16 | 11 |
| **TOTAL** | **493** | **54 (11%)** | **41 (8%)** | **398 (81%)** | **56** |

**81% of all coefficients are UNGROUNDED — targets for the Adversarial Critic.**

---

## Critical Findings

### 1. Zero Literature Citations in conflict.py
The entire conflict engine — combat power formula, casualty scaling, coalition defense thresholds, third-party punishment — has **no literature-grounded coefficients**. Every weight (0.20 aggression, 0.15 status, 0.10 risk_tolerance, etc.) is AI-inferred from DD03/DD08/DD11/DD27.

### 2. Combat Power Formula is Fully Ungrounded
```
power = aggression * 0.20 + status * 0.15 + health * 0.20 + risk_tolerance * 0.10
      + intelligence * 0.05 + robustness * 0.10 + dominance_drive * 0.10 + pain_tolerance * 0.05
      + physical_strength * config.weight * (1.4 if male) + allies * 0.03 (cap 3)
```
All weights, the 1.4 male multiplier, and the ally cap are UNGROUNDED.

### 3. AutoSIM Calibration Covers Only 36 Parameters
Of 493 total coefficients, only 36 come from AutoSIM optimization. The remaining 457 hardcoded values were never systematically tested.

### 4. Documentation-Code Discrepancy (institutions.py)
`deep_dive_05_institutions.md` lists `cooperation_institution_boost = 2.0` and `violence_institution_decay = 3.0`, but the code defaults are `0.01` and `0.02` — a **100-150x discrepancy**. Either the doc was aspirational or the code was changed without updating the doc.

### 5. Bowles-Critical Coefficients
56 coefficients are tagged `[BOWLES]` — these are the ones Professor Bowles would scrutinize for any group-selection or institutional-evolution claims.

---

## ENGINE 1: conflict.py (90 coefficients)

### Conflict Initiation Probability

| Line | Value | Context | DD | Lit | Class | Bowles |
|------|-------|---------|-----|-----|-------|--------|
| 46 | 0.6 | Impulse control multiplier on aggression | DD15 | — | UNGROUNDED | |
| 46 | 0.3 | Minimum impulse control gate | DD15 | — | UNGROUNDED | |
| 56 | 0.1 | Jealousy conflict post-multiplier | — | — | UNGROUNDED | |
| 59 | 5.0 | Resource stress threshold divisor | — | — | UNGROUNDED | |
| 59 | 0.1 | Resource stress contribution scaling | — | — | UNGROUNDED | |
| 60 | 0.5 | Mental health baseline dampening | DD15 | — | UNGROUNDED | |
| 63 | 0.05 | Status drive conflict contribution | — | — | UNGROUNDED | |
| 71 | 0.2 | Seasonal conflict boost default | DD10 | — | UNGROUNDED | |
| 76 | 0.5 | Law strength base multiplier | — | — | UNGROUNDED | |
| 76 | 0.5 | Punishment strength multiplier | — | — | UNGROUNDED | |
| 77 | 0.8 | Institutional suppression dampening | — | — | UNGROUNDED | |
| 80 | 0.3 | Cooperation dampening on conflict | DD03 | — | UNGROUNDED | |
| 83 | 0.3 | Empathy suppression multiplier | DD15 | — | UNGROUNDED | |
| 83 | 0.5 | Minimum empathy gate | DD15 | — | UNGROUNDED | |
| 88 | 0.5 | Psychopathy suppression of deterrence | DD27 | — | UNGROUNDED | |
| 88 | 0.3 | Minimum network deterrence gate | DD27 | — | UNGROUNDED | |
| 89 | 0.05 | Per-ally conflict reduction | DD03 | — | UNGROUNDED | |
| 103 | 0.5 | Elder conflict probability multiplier | DD22 | — | UNGROUNDED | |
| 106 | 0.4 | Anxiety suppression multiplier | DD27 | — | UNGROUNDED | |
| 106 | 0.3 | Minimum anxiety gate | DD27 | — | UNGROUNDED | |
| 109 | 15 | Violence acceptability belief age gate | DD25 | — | UNGROUNDED | |
| 112 | 0.1 | Violence acceptability boost (positive) | DD25 | — | UNGROUNDED | |
| 114 | 0.15 | Violence acceptability suppression (negative) | DD25 | — | UNGROUNDED | |
| 123 | 0.5 | Upper cap on conflict probability | DD03 | — | UNGROUNDED | |

### Flee Response

| Line | Value | Context | DD | Lit | Class | Bowles |
|------|-------|---------|-----|-----|-------|--------|
| 136 | 0.15 | Pain tolerance contribution to flee | DD15 | — | UNGROUNDED | |
| 140 | 0.15 | Degenerative flee threshold boost | DD17 | — | UNGROUNDED | |
| 144 | 0.5 | Flee chance scaling factor | DD03 | — | UNGROUNDED | |
| 148 | 0.02 | Dominance gain on successful flee | DD03 | — | UNGROUNDED | |
| 150 | 0.02 | Dominance loss on flee | DD03 | — | UNGROUNDED | |

### Coalition Defense (DD11)

| Line | Value | Context | DD | Lit | Class | Bowles |
|------|-------|---------|-----|-----|-------|--------|
| 168 | 0.4 | Min cooperation for coalition defense | DD11 | — | UNGROUNDED | |
| 169 | 0.3 | Min health for coalition defense | DD11 | — | UNGROUNDED | |
| 174 | 0.3 | Group loyalty coalition defense boost | DD27 | — | UNGROUNDED | `[BOWLES]` |
| 178 | 0.03 | Dominance loss for deterred aggressor | DD11 | — | UNGROUNDED | |
| 180 | 0.03 | Prestige gain for coalition defender | DD11 | — | UNGROUNDED | |
| 181 | 0.05 | Trust memory: defender ↔ target | DD11 | — | UNGROUNDED | |
| 183 | -0.1 | Trust memory: aggressor → defender | DD11 | — | UNGROUNDED | |

### Target Selection

| Line | Value | Context | DD | Lit | Class | Bowles |
|------|-------|---------|-----|-----|-------|--------|
| 241 | 4.0 | Household proximity multiplier | DD18 | — | UNGROUNDED | |
| 242 | 2.0 | Neighborhood proximity multiplier | DD18 | — | UNGROUNDED | |
| 248 | 0.3 | Cross-sex targeting weight | DD03 | — | UNGROUNDED | |
| 258 | 1.5 | Trust-based targeting baseline | DD03 | — | UNGROUNDED | |
| 263 | 3.0 | Mate-rival weight boost | DD03 | — | UNGROUNDED | |
| 267 | 0.2 | Status challenge difference threshold | DD08 | — | UNGROUNDED | |
| 268 | 1.5 | Similar-status target boost | DD08 | — | UNGROUNDED | |
| 275 | 1.5 | Resource envy threshold | DD03 | — | UNGROUNDED | |
| 276 | 1.3 | Resource-rich target boost | DD03 | — | UNGROUNDED | |
| 280 | 1.5 | Tool envy threshold | DD21 | — | UNGROUNDED | |
| 281 | 1.4 | Tool-rich target boost | DD21 | — | UNGROUNDED | |
| 290 | 0.4 | Psychopathy strength-seeking mult | DD27 | — | UNGROUNDED | |
| 291 | 0.4 | Risk tolerance coward threshold | DD03 | — | UNGROUNDED | |
| 292 | 1.2 | Health advantage avoidance threshold | DD03 | — | UNGROUNDED | |
| 293 | 0.5 | Cowardly aggressor health penalty | DD03 | — | UNGROUNDED | |
| 295 | 0.5 | Psychopathy prey threshold | DD27 | — | UNGROUNDED | |
| 295 | 0.8 | Psychopathy weak-target threshold | DD27 | — | UNGROUNDED | |
| 326 | 3 | Elder count cap in damping | DD22 | — | UNGROUNDED | |

### Combat Power Formula

| Line | Value | Context | DD | Lit | Class | Bowles |
|------|-------|---------|-----|-----|-------|--------|
| 343 | 20.0 | Resource edge divisor | DD08 | — | UNGROUNDED | |
| 351 | 0.20 | Aggression weight | DD08 | — | UNGROUNDED | |
| 352 | 0.15 | Status weight | DD08 | — | UNGROUNDED | |
| 353 | 0.20 | Health weight | DD08 | — | UNGROUNDED | |
| 354 | 0.10 | Risk tolerance weight | DD08 | — | UNGROUNDED | |
| 356 | 0.05 | Intelligence weight | DD08 | — | UNGROUNDED | |
| 357 | 0.10 | Physical robustness weight | DD15 | — | UNGROUNDED | |
| 358 | 0.10 | Dominance drive weight | DD15 | — | UNGROUNDED | |
| 359 | 0.05 | Pain tolerance weight | DD15 | — | UNGROUNDED | |
| 374 | 1.4 | Male physical strength multiplier | DD27 | — | UNGROUNDED | |
| 387 | 3 | Ally count cap | DD03 | — | UNGROUNDED | |
| 387 | 0.03 | Per-ally combat bonus | DD03 | — | UNGROUNDED | |

### Combat Resolution & Consequences

| Line | Value | Context | DD | Lit | Class | Bowles |
|------|-------|---------|-----|-----|-------|--------|
| 407 | 0.01 | Numerical stability epsilon | DD08 | — | UNGROUNDED | |
| 416 | 0.7 | Close-fight baseline scale | DD03 | — | UNGROUNDED | |
| 416 | 1.6 | Power differential consequence scaling | DD03 | — | UNGROUNDED | |
| 421 | 0.4 | Robustness damage absorption | DD15 | — | UNGROUNDED | |
| 421 | 0.5 | Min robustness damage reduction | DD15 | — | UNGROUNDED | |
| 428 | 0.5 | Base loot fraction (weak property rights) | DD05 | — | UNGROUNDED | |
| 434 | 0.2 | Tool conflict loot chance | DD21 | — | UNGROUNDED | |
| 438 | 10.0 | Tools per agent cap | DD21 | — | UNGROUNDED | |
| 446 | 0.02 | Prestige loss from violence | DD03 | — | UNGROUNDED | |
| 449 | 0.3 | Winner health cost fraction | DD03 | — | UNGROUNDED | |
| 458 | 0.5 | Death chance baseline multiplier | DD03 | — | UNGROUNDED | `[BOWLES]` |
| 473 | 0.05 | Reputation loss from violence | DD03 | — | UNGROUNDED | |
| 475 | 0.2 | Decisive victory power threshold | DD03 | — | UNGROUNDED | |
| 476 | 0.02 | Decisive victory reputation gain | DD03 | — | UNGROUNDED | |
| 478 | -0.2 | Trust loss: aggressor → target | DD03 | — | UNGROUNDED | |
| 479 | -0.3 | Trust loss: target → aggressor | DD03 | — | UNGROUNDED | |
| 495 | -0.08 | Bystander trust loss toward aggressor | DD03 | — | UNGROUNDED | |
| 497 | 0.6 | Allied bystander trust threshold | DD03 | — | UNGROUNDED | |
| 498 | -0.1 | Allied bystander amplified distrust | DD03 | — | UNGROUNDED | |

### Bond Destabilization

| Line | Value | Context | DD | Lit | Class | Bowles |
|------|-------|---------|-----|-----|-------|--------|
| 506 | 0.1 | Base bond dissolution factor | — | — | UNGROUNDED | |
| 506 | 0.5 | Aggression multiplier on dissolution | — | — | UNGROUNDED | |
| 511 | -0.25 | Trust loss from departing partner | — | — | UNGROUNDED | |

### Institutional Punishment

| Line | Value | Context | DD | Lit | Class | Bowles |
|------|-------|---------|-----|-----|-------|--------|
| 529 | 0.1 | Punishment reputation penalty mult | DD11 | — | UNGROUNDED | |
| 532 | 5 | Resource fine multiplier | DD11 | — | UNGROUNDED | |

### Third-Party Punishment

| Line | Value | Context | DD | Lit | Class | Bowles |
|------|-------|---------|-----|-----|-------|--------|
| 569 | 0.5 | Trust of target threshold | DD11 | — | UNGROUNDED | |
| 570 | 0.5 | Distrust of aggressor threshold | DD11 | — | UNGROUNDED | |
| 572 | 0.4 | Cooperation baseline for punishment | DD11 | — | UNGROUNDED | |
| 572 | 0.3 | Cooperation multiplier for punishment | DD11 | — | UNGROUNDED | `[BOWLES]` |
| 574 | 0.15 | Group loyalty punishment boost | DD27 | — | UNGROUNDED | `[BOWLES]` |
| 577 | 0.3 | Violence acceptability punishment effect | DD25 | — | UNGROUNDED | |
| 577 | 0.5 | Min gate on VA punishment effect | DD25 | — | UNGROUNDED | |
| 589 | -0.15 | Punisher trust toward aggressor | DD11 | — | UNGROUNDED | |
| 590 | -0.1 | Aggressor trust toward punisher | DD11 | — | UNGROUNDED | |
| 593 | 0.02 | Prestige gain from punishment | DD11 | — | UNGROUNDED | `[BOWLES]` |

---

## ENGINE 2: resources.py (136 coefficients)

### Resource Acquisition Weights

| Line | Value | Context | DD | Lit | Class | Bowles |
|------|-------|---------|-----|-----|-------|--------|
| 166 | 0.6, 0.8 | Foraging skill base + multiplier | DD26 | — | UNGROUNDED | |
| 167 | 0.7 | Intelligence diminishing returns power | DD23 | — | UNGROUNDED | |
| 167 | 0.8 | Intelligence ceiling | DD23 | — | UNGROUNDED | |
| 167 | 0.25 | Intelligence competitive weight | DD02, DD08 | — | GROUNDED | |
| 168 | 0.7, 0.3 | Prestige/dominance status split | DD08 | — | GROUNDED | |
| 168 | 0.25 | Status competitive weight | DD08 | — | GROUNDED | |
| 169 | 50 | Experience age cap | DD02 | — | UNGROUNDED | |
| 169 | 0.15 | Experience competitive weight | DD02, DD08 | — | GROUNDED | |
| 173 | 0.15 | Wealth competitive weight | DD02, DD08 | — | GROUNDED | |
| 176 | 5 | Network ally cap | DD02 | — | UNGROUNDED | `[BOWLES]` |
| 179 | 0.08 | Physical strength weight | DD27 | — | UNGROUNDED | |
| 181 | 0.6 | Female strength dampening | DD27 | — | UNGROUNDED | |
| 186 | 0.10 | Future orientation weight | DD27 | — | UNGROUNDED | |
| 195 | config | Aggression production penalty | DD02 | — | CALIBRATED | |
| 203 | 3 | Competitive weight amplification power | DD02 | — | GROUNDED | |
| 203 | 0.01 | Minimum competitive weight floor | DD02 | — | UNGROUNDED | |

### Cooperation Sharing

| Line | Value | Context | DD | Lit | Class | Bowles |
|------|-------|---------|-----|-----|-------|--------|
| 266 | 0.7 | High cooperation threshold for distant sharing | DD18, DD25 | — | UNGROUNDED | |
| 270 | 0.2 | Kinship obligation threshold modifier | DD25 | — | UNGROUNDED | |
| 276 | 0.25 | Minimum sharing trust threshold | DD27 | — | UNGROUNDED | |
| 289 | 0.15 | Empathy sharing boost | DD15 | — | UNGROUNDED | `[BOWLES]` |
| 292 | 0.1 | Cooperation norm sharing boost | DD25 | — | UNGROUNDED | `[BOWLES]` |
| 305 | 0.6 | Group loyalty high threshold | DD27 | — | UNGROUNDED | `[BOWLES]` |
| 306 | 1.2 | Loyal group sharing amplification | DD27 | — | UNGROUNDED | `[BOWLES]` |
| 308 | 0.6 | Psychopathy exploitation threshold | DD27 | — | UNGROUNDED | |
| 320 | 0.05 | Base trust gain from sharing | DD02, DD15 | — | GROUNDED | `[BOWLES]` |
| 320 | 0.3 | EI trust formation multiplier | DD15 | — | UNGROUNDED | |

### Prestige/Dominance Scoring (DD08)

| Line | Value | Context | DD | Lit | Class | Bowles |
|------|-------|---------|-----|-----|-------|--------|
| 338 | 0.30 | Cooperation prestige weight | DD08 | — | UNGROUNDED | `[BOWLES]` |
| 339 | 0.20 | Intelligence prestige weight | DD08 | — | UNGROUNDED | `[BOWLES]` |
| 340 | 0.20 | Existing prestige weight | DD08 | — | UNGROUNDED | `[BOWLES]` |
| 341 | 0.04 | Network prestige weight (per ally, cap 5) | DD08 | — | UNGROUNDED | `[BOWLES]` |
| 342 | 0.10 | Reputation prestige weight | DD08 | — | UNGROUNDED | `[BOWLES]` |
| 343 | 0.20 | Status drive dominance weight | DD08 | — | UNGROUNDED | |
| 344 | 0.15 | Aggression dominance weight | DD08 | — | UNGROUNDED | |
| 345 | 0.25 | Existing dominance weight | DD08 | — | UNGROUNDED | |
| 346 | 0.10 | Health dominance weight | DD08 | — | UNGROUNDED | |
| 347 | 0.10 | Risk tolerance dominance weight | DD08 | — | UNGROUNDED | |
| 348 | 0.20 | Dominance drive weight | DD15 | — | UNGROUNDED | |
| 353 | 0.6 | Prestige pool fraction | DD08 | — | GROUNDED | |
| 354 | 0.4 | Dominance pool fraction | DD08 | — | GROUNDED | |
| 374 | 0.7, 0.3 | Prestige score decay blend | DD08 | — | UNGROUNDED | |
| 376 | 0.7, 0.3 | Dominance score decay blend | DD08 | — | UNGROUNDED | |

### Storage, Decay, Tools, Signaling (abbreviated — 70+ additional coefficients)

All coefficients in storage mechanics (lines 102-131), child investment (lines 222-231), signaling (lines 440-476), and tool production (lines 493-541) are **UNGROUNDED**. Full line-by-line detail available from the audit agents.

Notable CALIBRATED values from AutoSIM:
- `resource_equal_floor` (0.4)
- `cooperation_network_bonus` (0.059)
- `cooperation_sharing_rate` (0.125)
- `wealth_diminishing_power` (0.737)
- `subsistence_floor` (1.173)
- `child_investment_per_year` (0.350)
- `aggression_production_penalty` (0.6)

All marked **[UNCERTAIN - TARGET FOR PERTURBATION]**.

---

## ENGINE 3: mating.py (50 coefficients)

### Bond Dissolution

| Line | Value | Context | DD | Lit | Class | Bowles |
|------|-------|---------|-----|-----|-------|--------|
| 81 | 0.5 | Bond strength resistance factor | DD01 | — | UNGROUNDED | |
| 85 | 10.0 | Resource stress threshold | — | — | UNGROUNDED | |
| 88 | 0.15 | Low mate value dissolution impact | — | — | UNGROUNDED | |
| 91 | 0.5 | Environmental stress amplification | — | — | UNGROUNDED | |
| 94 | 0.3 | Future orientation dissolution damping | DD27 | — | UNGROUNDED | |
| 96 | 0.5 | Psychopathy dissolution boost | DD27 | — | UNGROUNDED | |
| 100 | 0.2 | Paternal investment dissolution resist | DD27 | — | UNGROUNDED | |
| 101 | 0.5 | Max annual dissolution rate | — | — | UNGROUNDED | |

### Female Choice / Mate Value

| Line | Value | Context | DD | Lit | Class | Bowles |
|------|-------|---------|-----|-----|-------|--------|
| 180 | 1.15 | Youth choosiness boost | DD22 | — | UNGROUNDED | |
| 186 | 0.15 | Anxiety choosiness boost | DD27 | — | UNGROUNDED | |
| 189 | 3.0 | Resource desperation threshold | — | — | UNGROUNDED | |
| 197 | 0.3 | EI trust amplification in mate eval | DD15 | — | UNGROUNDED | |
| 201 | 0.2 | Social skill character assessment | DD26 | — | UNGROUNDED | |
| 205 | 0.5 | Aggression penalty in female choice | DD01 | — | UNGROUNDED | `[BOWLES]` |
| 209 | 0.4 | Cooperation bonus in female choice | DD01 | — | UNGROUNDED | |
| 254 | 0.4, 0.3, 0.2, 0.1 | Invest signal weights | DD27 | — | UNGROUNDED | |
| 258 | 0.3, 0.25, 0.15, 0.15, 0.15 | Genetic signal weights | DD27 | — | UNGROUNDED | |
| 267 | 0.3, 0.8, 0.4 | Psychopathy charm effect | DD27 | — | UNGROUNDED | |

### Male Contest

| Line | Value | Context | DD | Lit | Class | Bowles |
|------|-------|---------|-----|-----|-------|--------|
| 290 | 0.3 | Contest challenge probability | DD01 | — | UNGROUNDED | `[BOWLES]` |
| 292 | 0.4 | Dominance weight in contest | DD08 | — | UNGROUNDED | `[BOWLES]` |
| 293 | 0.3 | Health weight in contest | — | — | UNGROUNDED | |
| 294 | 0.3 | Aggression weight in contest | — | — | UNGROUNDED | `[BOWLES]` |

### EPC & Bond Dynamics

| Line | Value | Context | DD | Lit | Class | Bowles |
|------|-------|---------|-----|-----|-------|--------|
| 316 | 0.5-1.0 | Initial bond strength range | DD01 | — | CALIBRATED | |
| 373 | 0.5 | EPC bond dampening | DD01 | — | UNGROUNDED | |
| 375 | 1.5 | PIP EPC accelerant | DD27 | — | UNGROUNDED | |
| 404 | -0.3 | Paternity confidence loss | DD01 | — | UNGROUNDED | |
| 410 | 0.2 | Bond damage base from infidelity | — | — | UNGROUNDED | |
| 445 | 0.05, 0.8 | Bond growth + diminishing return | DD01 | — | UNGROUNDED | |

---

## ENGINE 4: reproduction.py (22 coefficients)

### Conception

| Line | Value | Context | DD | Lit | Class | Bowles |
|------|-------|---------|-----|-----|-------|--------|
| 46 | 0.6, 0.4 | Fertility base weight + floor | — | — | UNGROUNDED | |
| 47 | 0.5, 16.0 | Resource modifier floor + threshold | — | — | UNGROUNDED | |
| 53 | 20 | Adolescent subfertility age | DD13 | — | UNGROUNDED | |
| 56 | 28 | Peak fertility plateau | DD13 | — | UNGROUNDED | |
| 61 | 0.05 | Minimum fertility floor | — | — | UNGROUNDED | |
| 64 | 0.2 | Maternal investment tradeoff | DD15 | — | UNGROUNDED | |
| 85 | 1.3 | Pair bond conception bonus | — | — | UNGROUNDED | |

### Infant Survival

| Line | Value | Context | DD | Lit | Class | Bowles |
|------|-------|---------|-----|-----|-------|--------|
| 135 | 0.02 | Base childbirth mortality | — | — | CALIBRATED | |
| 137 | 3.0 | Unhealthy mother multiplier | DD13 | — | UNGROUNDED | |
| 139 | 0.4 | Endurance childbirth protection | DD27 | — | UNGROUNDED | |
| 163 | 12.0 | Resource factor denominator | — | — | UNGROUNDED | |
| 164 | 0.6, 0.4 | Survival floor + ceiling from resources | — | — | UNGROUNDED | |
| 168 | 0.2 | Pair bond survival boost | — | — | UNGROUNDED | |
| 177 | 0.02, 0.1 | Kin bonus per sibling + cap | — | — | UNGROUNDED | |
| 181 | 0.15 | Maternal investment survival boost | DD15 | — | UNGROUNDED | |
| 183 | 0.8, 0.4 | Conscientiousness floor + range | DD27 | — | UNGROUNDED | |
| 190 | config | Grandparent survival bonus | DD06 | — | CALIBRATED | |
| 193 | 0.1, 0.98 | Survival probability bounds | — | — | UNGROUNDED | |
| 214 | 2.0 | Resources lost per birth | — | — | UNGROUNDED | |

---

## ENGINE 5: mortality.py (52 coefficients)

### Health Decay

| Line | Value | Context | DD | Lit | Class | Bowles |
|------|-------|---------|-----|-----|-------|--------|
| 58 | 30 | Age threshold for accelerating decay | — | — | UNGROUNDED | |
| 58 | 0.002 | Per-year acceleration rate | — | — | UNGROUNDED | |
| 62 | 0.5, 0.4 | Longevity genes: floor + reduction | DD15 | — | UNGROUNDED | |
| 64 | 0.7, 0.15 | Endurance: floor + reduction | DD27 | — | UNGROUNDED | |
| 66 | 0.75, 0.12 | Conscientiousness: floor + reduction | DD27 | — | UNGROUNDED | |
| 72 | 0.03 | Scarcity health penalty | — | — | UNGROUNDED | |
| 75 | 2.0 | Low resources health penalty threshold | — | — | UNGROUNDED | |
| 76 | 0.02 | Low resources health penalty | — | — | UNGROUNDED | |

### Age-Based Death

| Line | Value | Context | DD | Lit | Class | Bowles |
|------|-------|---------|-----|-----|-------|--------|
| 189 | 10 | Max longevity gene age shift | DD15 | — | UNGROUNDED | |
| 192 | 0.01 | Age-based death probability base | — | — | UNGROUNDED | |
| 192 | 1.5 | Age-based death exponent | — | — | UNGROUNDED | |
| 201 | 15, 40 | Male risk mortality age range | DD13 | Bowles 2008 | GROUNDED | `[BOWLES]` |

### Childhood Mortality

| Line | Value | Context | DD | Lit | Class | Bowles |
|------|-------|---------|-----|-----|-------|--------|
| 101 | 0.5, 1.5 | Resource factor bounds | DD06 | — | UNGROUNDED | |
| 101 | 10.0 | Parental resources divisor | DD06 | — | UNGROUNDED | |
| 109 | 0.3 | Min child death reduction from grandparent | DD06 | — | UNGROUNDED | |
| 113 | 0.5 | Scarcity childhood mortality boost | DD06 | — | UNGROUNDED | |

### Epidemic

| Line | Value | Context | DD | Lit | Class | Bowles |
|------|-------|---------|-----|-----|-------|--------|
| 139 | 10 | Child epidemic vulnerability age | DD09 | — | GROUNDED | |
| 141 | 55 | Elder epidemic vulnerability age | DD09 | — | GROUNDED | |
| 146 | 2.0 | Low health epidemic multiplier | DD09 | — | UNGROUNDED | |
| 150 | 1.5 | Low resources epidemic multiplier | DD09 | — | GROUNDED | |
| 153 | 0.7, 0.3 | Intelligence epidemic resilience | DD09 | — | UNGROUNDED | |
| 156 | 0.4, 0.5 | Disease resistance epidemic floor + reduction | DD15 | — | UNGROUNDED | |

### Developmental Plasticity + Beliefs + Skills

52 additional coefficients in maturation (lines 237-290), belief initialization (lines 335-347), and skill initialization (lines 352-375). All **UNGROUNDED** — trait-to-belief weight formulas (0.6/0.4/0.3/0.8/0.2 etc.) and skill transmission fractions (0.5) are AI-inferred from DD16/DD25/DD26.

---

## ENGINE 6: pathology.py (63 coefficients)

Most pathology coefficients reference DD17 (Medical) and DD24 (Epigenetics) and are documented in those design docs, but **none cite external literature**. Key values:

| Line | Value | Context | DD | Lit | Class | Bowles |
|------|-------|---------|-----|-----|-------|--------|
| 60 | 0.2 | Default condition risk | DD17 | — | UNGROUNDED | |
| 65 | 3.0 | Chronic resource stress threshold | DD17 | — | UNGROUNDED | |
| 73 | 40, 0.05 | Age acceleration threshold + rate | DD17 | — | UNGROUNDED | |
| 96 | 0.3 | Max annual activation probability | DD17 | — | UNGROUNDED | |
| 123 | 2.0, 0.02 | Trauma accumulation threshold + rate | DD17 | — | UNGROUNDED | |
| 177 | 15, 45 | Epigenetic age range | DD24 | — | UNGROUNDED | |
| 205 | 0.6 | Trauma contagion threshold | DD24 | — | UNGROUNDED | |

---

## ENGINE 7: institutions.py (40 coefficients)

### Institutional Drift

| Line | Value | Context | DD | Lit | Class | Bowles |
|------|-------|---------|-----|-----|-------|--------|
| 189 | 0.8 | Institutional inertia | DD05 | — | CALIBRATED | |
| 190 | 0.01 | Cooperation institution boost default | DD05 | — | CALIBRATED | |
| 191 | 0.02 | Violence institution decay default | DD05 | — | CALIBRATED | |
| 214 | 0.4 | Cooperation threshold for growth | DD05 | — | CALIBRATED | |
| 215 | 0.3 | Conformity amplification factor | DD05 | Henrich & Boyd 1998 | GROUNDED | |
| 205 | 0.1 | Group loyalty institutional boost | DD27 | — | UNGROUNDED | |
| 206 | 0.08 | Conscientiousness institutional boost | DD27 | — | UNGROUNDED | |
| 210 | 0.05 | Future orientation boost | DD27 | — | UNGROUNDED | |
| 273 | 0.7 | Violence punishment tracking | DD05 | — | CALIBRATED | |
| 277 | 0.5 | Property rights tracking | DD05 | — | CALIBRATED | |

### Institutional Emergence

| Line | Value | Context | DD | Lit | Class | Bowles |
|------|-------|---------|-----|-----|-------|--------|
| 304 | 0.08 | Violence rate emergence threshold | DD05 | Bowles & Gintis 2011 | GROUNDED | `[BOWLES]` |
| 310 | 5 | Violence streak threshold (years) | DD05 | — | CALIBRATED | `[BOWLES]` |
| 312 | 0.1 | Punishment emergence strength | DD05 | — | CALIBRATED | `[BOWLES]` |
| 336 | 3.0 | Reproductive skew threshold | DD05 | Bowles 2006 | GROUNDED | `[BOWLES]` |
| 343 | 8 | Inequality streak threshold (years) | DD05 | — | CALIBRATED | `[BOWLES]` |
| 344 | 3 | Minimum mate limit floor | — | — | UNGROUNDED | `[BOWLES]` |

### Belief-Institutional Coupling (DD25)

| Line | Value | Context | DD | Lit | Class | Bowles |
|------|-------|---------|-----|-----|-------|--------|
| 242 | 0.3 | Belief institutional influence default | DD25 | — | CALIBRATED | |
| 249 | 0.3 | Cooperation norm belief influence | DD25 | — | UNGROUNDED | |
| 251 | 0.2 | Violence acceptability belief drain | DD25 | — | UNGROUNDED | |
| 254 | 0.5 | Tradition adherence inertia amplification | DD25 | — | UNGROUNDED | |
| 259 | 0.01 | Hierarchy belief elite_privilege adjustment | DD25 | — | UNGROUNDED | |

---

## ENGINE 8: reputation.py (40 coefficients)

### Trust Mechanics

| Line | Value | Context | DD | Lit | Class | Bowles |
|------|-------|---------|-----|-----|-------|--------|
| 43 | 0.01 | Trust decay rate default | DD07 | — | CALIBRATED | |
| 50 | 0.5 | Extreme value decay dampening | DD07 | — | CALIBRATED | |
| 62 | 0.1 | Gossip rate default | DD07 | — | CALIBRATED | |
| 63 | 0.1 | Gossip noise default | DD07 | — | CALIBRATED | |
| 108 | 0.5 | Gossip weight base scaling | DD07 | — | CALIBRATED | |
| 108 | 0.3 | Gossip weight trust offset | DD07 | — | CALIBRATED | |
| 159 | 0.7, 0.3 | Reputation blend (aggregate/stability) | DD07 | — | CALIBRATED | |

### Belief Experience Updates (Bowles-critical)

| Line | Value | Context | DD | Lit | Class | Bowles |
|------|-------|---------|-----|-----|-------|--------|
| 218 | 0.5 | Novelty seeking conformity reduction | DD25 | Henrich & Boyd 1998 | GROUNDED | |
| 238 | 1.0 | Conflict winner violence acceptability | DD25 | Bowles 2011 | GROUNDED | `[BOWLES]` |
| 241 | 0.67 | Conflict winner hierarchy belief | DD25 | Bowles & Gintis 2011 | GROUNDED | `[BOWLES]` |
| 243 | 0.67 | Conflict winner cooperation reduction | DD25 | Bowles & Gintis 2011 | GROUNDED | `[BOWLES]` |
| 246 | 1.67 | Conflict loser violence reduction | DD25 | — | UNGROUNDED | `[BOWLES]` |
| 259 | 1.33 | Punishment violence reduction | DD05 | Bowles 2006 | GROUNDED | `[BOWLES]` |
| 267 | 0.67 | Arbitration cooperation boost | DD20 | Bowles 2011 | GROUNDED | |
| 288 | 0.33 | Direct sharing cooperation boost | DD02 | Bowles & Gintis 2011 | GROUNDED | |

### Skill Learning

| Line | Value | Context | DD | Lit | Class | Bowles |
|------|-------|---------|-----|-----|-------|--------|
| 369 | 0.03 | Age learning rate decline | DD26 | anthropological data | GROUNDED | |
| 374 | 1.1, 0.8 | Foraging growth threshold + saturation | DD26 | — | UNGROUNDED | |
| 383 | 0.5, 0.8 | Social skill rate + saturation | DD26 | — | UNGROUNDED | |
| 422 | 0.02 | Combat skill gain multiplier | DD26 | — | UNGROUNDED | `[BOWLES]` |
| 425 | 0.005 | Combat skill loser gain | DD26 | — | UNGROUNDED | `[BOWLES]` |

---

## BOWLES FILTER: Complete List (56 coefficients)

These are the coefficients most relevant to Fst, migration, death-in-conflict, altruistic cost *c*, and between-group selection:

### Death-in-Conflict Related
- conflict.py:458 — Death chance baseline multiplier (0.5) **UNGROUNDED**
- conflict.py:572 — Cooperation multiplier for punishment (0.3) **UNGROUNDED**
- conflict.py:574 — Group loyalty punishment boost (0.15) **UNGROUNDED**
- conflict.py:593 — Prestige gain from punishment (0.02) **UNGROUNDED**
- conflict.py:174 — Group loyalty coalition defense boost (0.3) **UNGROUNDED**
- mortality.py:201 — Male risk mortality age range 15-40 **GROUNDED** (Bowles 2008)
- reputation.py:238 — Conflict winner VA boost (1.0) **GROUNDED** (Bowles 2011)
- reputation.py:241 — Conflict winner hierarchy (0.67) **GROUNDED** (Bowles & Gintis 2011)
- reputation.py:243 — Conflict winner cooperation reduction (0.67) **GROUNDED** (Bowles & Gintis 2011)
- reputation.py:246 — Conflict loser VA reduction (1.67) **UNGROUNDED**
- reputation.py:259 — Punishment VA reduction (1.33) **GROUNDED** (Bowles 2006)
- reputation.py:422 — Combat skill gain (0.02) **UNGROUNDED**
- reputation.py:425 — Combat skill loser gain (0.005) **UNGROUNDED**

### Altruistic Cost / Cooperation
- resources.py:289 — Empathy sharing boost (0.15) **UNGROUNDED**
- resources.py:292 — Cooperation norm sharing boost (0.1) **UNGROUNDED**
- resources.py:305 — Group loyalty high threshold (0.6) **UNGROUNDED**
- resources.py:306 — Group loyalty sharing amplification (1.2) **UNGROUNDED**
- resources.py:320 — Trust gain from sharing (0.05) **GROUNDED**
- resources.py:338-342 — Prestige scoring weights (0.30/0.20/0.20/0.04/0.10) **UNGROUNDED**

### Institutional Selection
- institutions.py:304 — Violence rate emergence (0.08) **GROUNDED** (Bowles & Gintis 2011)
- institutions.py:310 — Violence streak threshold (5yr) **CALIBRATED**
- institutions.py:312 — Punishment emergence (0.1) **CALIBRATED**
- institutions.py:336 — Reproductive skew (3.0) **GROUNDED** (Bowles 2006)
- institutions.py:343 — Inequality streak (8yr) **CALIBRATED**
- institutions.py:344 — Mate limit floor (3) **UNGROUNDED**

### Mating Competition
- mating.py:205 — Aggression penalty in female choice (0.5) **UNGROUNDED**
- mating.py:290 — Contest challenge probability (0.3) **UNGROUNDED**
- mating.py:292 — Dominance weight in contest (0.4) **UNGROUNDED**
- mating.py:294 — Aggression weight in contest (0.3) **UNGROUNDED**

---

## PERTURBATION TARGET LIST

**All 439 CALIBRATED + UNGROUNDED coefficients are targets for the Phase 3 Adversarial Critic.**

The most critical subset (highest impact on model claims):

1. **Combat power weights** (conflict.py:351-359) — 8 coefficients, all UNGROUNDED
2. **Death chance formula** (conflict.py:458) — UNGROUNDED, directly determines violence mortality
3. **Prestige/dominance scoring** (resources.py:338-348) — 11 coefficients, all UNGROUNDED
4. **Female choice weights** (mating.py:205,209,254,258) — all UNGROUNDED, drive sexual selection
5. **Institutional emergence thresholds** (institutions.py:304,310,336,343) — mix of GROUNDED and CALIBRATED
6. **Belief experience multipliers** (reputation.py:238-267) — mix, but loser VA reduction (1.67) is UNGROUNDED
7. **AutoSIM-calibrated params** (36 total) — all marked [UNCERTAIN - TARGET FOR PERTURBATION]

---

*Generated by Phase 1 audit. Input to Phase 2 (Provenance Log) and Phase 3 (Adversarial Critic ±20% perturbation sweep, σ ≤ 0.030 gate).*
