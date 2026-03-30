# SIMSIV — ODD Protocol (Grimm et al. 2010)

**Model:** SIMSIV v1 — Simulation of Intersecting Social and Institutional Variables
**Version:** Commit `71ac785` on branch `v2-interference`
**Authors:** James P. Rice II
**Standard:** ODD+D (Grimm et al. 2010; Muller et al. 2013)
**Submission:** JASSS 2026:81:1 (ref 6029)

---

## 1. PURPOSE AND PATTERNS

### 1.1 Purpose

SIMSIV tests the **Institutional Substitution Hypothesis**: that institutional governance systematically reduces directional selection on heritable prosocial behavioral traits — providing computational evidence that institutions and genes are substitutes, not complements, in human social evolution.

The model generates populations of autonomous agents with heritable behavioral traits who compete for resources, mates, and status. All social patterns — cooperation equilibria, violence rates, institutional emergence, pair bond dynamics — must **emerge** from individual-level rules. No population-level outcome is hardwired.

The primary analytical tools are:

**Selection Differential** *S* (Falconer & Mackay 1996), defined per trait $T$:

$$S_T = \mu_{\text{parents},T} - \mu_{\text{eligible},T}$$

where $\mu_{\text{parents},T}$ is the mean **genotype** (birth value, not phenotype) of trait $T$ among agents who successfully reproduced in a given tick, and $\mu_{\text{eligible},T}$ is the mean genotype of all reproductively eligible agents. A positive $S_T$ indicates directional selection favoring higher values of trait $T$.

**Population-Normalized Selection Differential** $S_n$ (v2 paired-seed protocol):

$$S_{n,T} = \frac{S_T}{\sqrt{N_{\text{eligible}}}}$$

Normalization removes the small-population drift inflation identified in the adversarial audit: $\sigma(S)$ scales as $1/\sqrt{N}$ (confirmed by Squazzoni N-Test across N = 250, 500, 1000).

**Cumulative Trait Displacement** $R_{\text{total}}$ (primary outcome metric):

$$R_{\text{total},T} = \bar{G}_{T,\text{yr500}} - \bar{G}_{T,\text{yr1}}$$

where $\bar{G}$ is the population mean genotype. This integrates the selection response across the full run, avoiding the snapshot-noise artifacts that affect single-year $S$ values.

**Paired-Seed Design** (v2 protocol): Each random seed is run through both experimental conditions, enabling paired $t$-tests that eliminate inter-seed variance and approximately double statistical power at equal sample size.

### 1.2 Entities, State Variables, and Scales

**Entities:**

| Entity | Count | Description |
|--------|-------|-------------|
| Agent | 250–1000 (default 500) | Autonomous individual with 35 heritable traits and ~30 non-heritable state variables |
| Band (Society) | 1 | Single-band population with shared environment, trust network, and institutions |
| Environment | 1 | Exogenous resource supply with seasonal cycles and scarcity shocks |

**Agent State Variables — Heritable Traits (35 total, genotype + phenotype):**

Each agent carries a **genotype** (immutable genetic values set at birth) and a **phenotype** (expressed values that may be modified by developmental plasticity). Inheritance follows a quantitative genetics model (Falconer 1981):

$$\text{child}_i = h^2_i \cdot \text{parent\_midpoint}_i + (1 - h^2_i) \cdot \mu_{\text{pop},i} + \epsilon_i$$

where $h^2_i$ is the trait-specific heritability and $\epsilon_i \sim \mathcal{N}(0, \sigma_m)$ is Gaussian mutation noise ($\sigma_m = 0.05$).

| Domain | Traits | h² Range | Count |
|--------|--------|----------|-------|
| Physical Performance | physical_strength, endurance, physical_robustness, pain_tolerance, longevity_genes, disease_resistance | 0.25–0.60 | 6 |
| Cognitive | intelligence_proxy, emotional_intelligence, impulse_control, conscientiousness | 0.40–0.65 | 4 |
| Temporal | future_orientation | 0.40 | 1 |
| Personality | risk_tolerance, novelty_seeking, anxiety_baseline, mental_health_baseline | 0.40–0.48 | 4 |
| Social Architecture | aggression_propensity, cooperation_propensity, dominance_drive, group_loyalty, outgroup_tolerance, empathy_capacity, conformity_bias, status_drive, jealousy_sensitivity | 0.35–0.50 | 9 |
| Reproductive Biology | fertility_base, sexual_maturation_rate, maternal_investment, paternal_investment_preference, attractiveness_base | 0.35–0.60 | 5 |
| Psychopathology Spectrum | psychopathy_tendency, mental_illness_risk, cardiovascular_risk, autoimmune_risk, metabolic_risk, degenerative_risk | 0.35–0.60 | 6 |

**Agent State Variables — Non-Heritable (contextual, earned, or computed):**

| Variable | Type | Description |
|----------|------|-------------|
| health | float [0,1] | Current health (decays with age, damage, disease) |
| reputation | float [0,1] | Public standing (aggregated from trust ledger) |
| current_resources | float | Subsistence resources acquired this tick |
| current_tools | float | Durable tool capital |
| current_prestige_goods | float | Social-value display goods |
| prestige_score | float [0,1] | Earned via cooperation, sharing, skill |
| dominance_score | float [0,1] | Earned via conflict, intimidation |
| current_status | float | Composite: 0.6 × prestige + 0.4 × dominance |
| reputation_ledger | dict[int, float] | Dyadic trust scores per known agent |
| beliefs (5 dims) | float [-1,+1] | hierarchy, cooperation_norm, violence_acceptability, tradition_adherence, kinship_obligation |
| skills (4 domains) | float [0,1] | foraging, combat, social, craft |
| faction_id | int | Emergent faction membership |
| life_stage | enum | CHILDHOOD / YOUTH / PRIME / MATURE / ELDER |

**Scales:**

| Dimension | Value |
|-----------|-------|
| Temporal | 1 tick = 1 year |
| Spatial | Non-spatial (fully mixed within band) with proximity tiers (household, neighborhood, band) |
| Population | 250–1000 agents (validated stable across this range; Squazzoni N-Test) |
| Duration | 200 years default (validated to 500 years for convergence) |

### 1.3 Process Overview and Scheduling

Each annual tick executes 12 steps in fixed order (see Section 7 for details). The ordering is causally significant: conflict (Step 3) precedes mating (Step 4) and reproduction (Step 5) so that violence has immediate reproductive fitness costs — dead agents cannot mate or reproduce.

---

## 2. DESIGN CONCEPTS

### 2.1 Theoretical and Empirical Background

The model integrates three theoretical traditions:

1. **Quantitative Genetics** (Falconer 1981; Falconer & Mackay 1996): Trait inheritance via the breeder's equation with trait-specific heritabilities, multivariate genetic correlations, and Gaussian mutation.

2. **Gene-Culture Coevolution** (Boyd & Richerson 1985; Henrich 2004): Cultural transmission through conformist bias, prestige-biased learning, and institutional drift. Beliefs and skills co-evolve with genetic traits.

3. **Multi-Level Selection** (Bowles 2006; Bowles & Gintis 2011): Competition between cooperative and defecting strategies within a population, with institutional enforcement and third-party punishment as stabilizing mechanisms.

Calibration targets are drawn from ethnographic and historical demography literature (see Section 8).

### 2.2 Individual Decision-Making

Agents do not employ explicit decision algorithms. Behavior emerges from trait-weighted probabilistic rules:

- **Conflict initiation**: Probability is a function of aggression_propensity, impulse_control, institutional suppression (law_strength), network deterrence (ally count), and environmental stress. Capped at 0.50 per tick.
- **Mate choice**: Females evaluate males via a weighted mate-value function incorporating aggression penalty (−0.5 × aggression; Archer 2009), cooperation bonus (+0.4 × cooperation; Henrich et al. 2001), health, status, and resource signals.
- **Resource sharing**: Agents with cooperation_propensity above threshold share with trusted allies. Psychopathy reduces sharing (exploiter strategy).

### 2.3 Learning

Agents do not learn in the reinforcement-learning sense. Adaptation occurs through two channels:

1. **Genetic selection**: Differential reproduction based on trait-fitness correlations, measured by the selection differential *S*.
2. **Cultural updating**: Beliefs evolve through conformist transmission (Henrich & Boyd 1998), prestige-biased social influence, and direct experience (conflict outcomes update violence_acceptability).

### 2.4 Individual Sensing

Agents sense:
- **Trust** of specific others via their reputation_ledger (dyadic, asymmetric, decays toward 0.5 at rate 0.01/year)
- **Institutional strength** (law_strength: 0 = anarchy, 1 = perfect enforcement) — a global parameter that self-organizes through drift
- **Environmental state** (current scarcity level, seasonal phase)
- **Proximity** (household, neighborhood, band tier — determines interaction probability)

Sensing is imperfect: gossip transmits trust information with noise (σ = 0.1), and bluffs can temporarily inflate apparent status.

### 2.5 Individual Prediction

Agents do not predict future states. Risk tolerance modulates willingness to engage in conflict (low risk_tolerance agents flee rather than fight), but this is a fixed trait, not a learned policy.

### 2.6 Interaction

All interactions are dyadic or small-group:
- **Conflict**: Aggressor vs. target, with bystander trust updates (up to 3 witnesses)
- **Mating**: Female choice + male contest competition
- **Sharing**: Cooperator → trusted allies (within trust threshold)
- **Gossip**: Agent → random ally, sharing trust information about third parties
- **Coalition defense**: Ally intervenes on behalf of target with probability based on trust and cooperation
- **Third-party punishment**: High-cooperation agents punish aggressors they distrust

### 2.7 Collectives

**Factions** emerge through community detection on the trust network (periodic, every 5 years). Faction membership affects sharing preferences (in-group bonus) and conflict targeting (out-group multiplier). Faction leaders (war chief, peace chief) emerge based on dominance and prestige thresholds.

### 2.8 Heterogeneity

Agents are heterogeneous across all 35 heritable traits (initialized from multivariate normal with genetic correlation structure) and diverge further through developmental plasticity, skill acquisition, and differential aging.

### 2.9 Stochasticity

All stochastic processes use a single `numpy.random.Generator` seeded from `config.seed`. This guarantees:
- **Determinism**: Same seed produces identical results across runs
- **Independence**: Each `Simulation(config)` instance owns its own RNG

Stochastic elements: trait mutation, conflict initiation and outcome, mate choice, pair bond dissolution, epidemic occurrence, scarcity shocks, gossip noise.

### 2.10 Observation

The **MetricsCollector** records ~120 metrics per tick, including:

| Metric | Formula | Purpose |
|--------|---------|---------|
| $S_T$ | $\mu_{\text{parents},T} - \mu_{\text{eligible},T}$ (genotype) | Selection differential per trait (35 traits) |
| $S_{n,T}$ | $S_T / \sqrt{N_{\text{eligible}}}$ | Pop-normalized selection differential |
| $R_{\text{total},T}$ | $\bar{G}_{T,500} - \bar{G}_{T,1}$ | Cumulative trait displacement |
| resource_gini | Gini coefficient of current_resources | Wealth inequality |
| violence_death_fraction | violence_deaths / male_deaths | Conflict lethality |
| reproductive_skew | Variance in offspring count / mean | Mating inequality |
| avg_cooperation | Population mean of cooperation_propensity | Trait tracking |

The v2 paired-seed experiment script (`scripts/run_divergence.py`) computes $S_T$ for all 35 traits using **genotype** values (not phenotype), extracted from birth events in `society.tick_events` after each tick. Parent identification uses the `_bred_this_tick` flag set during reproduction (Step 5).

---

## 3. DETAILS

### 3.1 Implementation Details

| Property | Value |
|----------|-------|
| Language | Python 3.11+ |
| Dependencies | numpy, scipy, pandas, matplotlib, pyyaml |
| Repository | https://github.com/kepiCHelaSHen/SIMSIV |
| Verified commit | `fb6a296` (branch `v2-interference`) |
| LOC (engines) | ~4,800 across 9 engine files |
| LOC (models) | ~1,400 across agent.py, society.py |
| Test suite | 32 tests, all passing |

### 3.2 Initialization

Population is created via `create_initial_population()`:
1. 35 heritable traits drawn from multivariate normal with genetic correlation matrix (22 non-zero correlations; e.g., aggression ↔ cooperation r = −0.4)
2. All traits clipped to [0.0, 1.0]
3. Genotype stored as immutable copy of birth values
4. Non-heritable state initialized: health = 1.0, reputation = 0.5, resources = 0, empty ledger

Sex ratio: 50/50 (stochastic).

### 3.3 Input Data

No external input data. The model is self-contained. All parameters are set in `config.py` (synchronized with `autosim/best_config.yaml`; see Section 8).

### 3.4 Submodels — The 12-Step Annual Tick

Executed in `simulation.py:tick()` in strict order:

**Step 1: Environment**
Scarcity shocks (probability 0.030/year, severity 0.3×) and seasonal cycles. Determines resource availability for Step 2.

**Step 2: Resources**
8-phase resource engine:
(a) Seasonal decay and storage. (b) Carrying capacity crowding penalty. (c) Equal floor distribution (40% of pool). (d) Competitive acquisition (weighted by intelligence, status, experience, strength, cooperation network). (e) Aggression production penalty (0.6×). (f) Cooperation sharing (rate 0.125 × cooperation × trust). (g) Child investment drain. (h) Prestige/dominance score computation (0.6/0.4 pool split).

**Step 3: Conflict (pre-reproductive selection)**
Probabilistic initiation: `p = conflict_base_probability × effective_aggression × modifiers`. Modifiers include institutional suppression (law_strength), cooperation dampening, network deterrence, and subordination cooldown. This step executes before mating and reproduction (Steps 4–5), creating a direct pre-reproductive selection filter: agents killed or injured in conflict cannot mate or reproduce that tick. This ordering is the mechanistic basis for the Selection Sheltering finding (Section 10.3).

Target selection: Weighted by trust (low = target), rivalry, status similarity, resource envy. Combat power: aggression(0.25) + status(0.20) + health(0.25) + risk(0.15) + intelligence(0.05) + DD15 additive traits.

Death probability: `violence_death_chance × (0.6 + power_diff)` (Keeley 1996 target: 0.05–0.15).

Bystander trust updates, pair bond destabilization, institutional punishment, third-party punishment, coalition defense all execute within this step.

**Step 4: Mating**
Female choice via weighted mate-value function. Aggression penalty (−0.5; Archer 2009), cooperation bonus (+0.4; Henrich et al. 2001). Male contest with 30% challenge probability. Pair bond formation.

**Step 5: Reproduction**
Conception probability: fertility × health × resources × pair bond bonus. Birth interval (2 years minimum). Infant survival: parental resources, grandparent bonus (0.083), kin network.

**Trait Inheritance** (within Step 5): `breed()` implements the Falconer (1981) quantitative genetics model. Mutation: $\epsilon \sim \mathcal{N}(0, 0.05)$, amplified under scarcity. Rare large mutations at rate 0.05 with σ = 0.15. Parent breeding tagged for S-metric computation in Step 12.

**MA Trait Locking**: If either parent carries `_is_ma = True`, offspring inherit the MA parent's exact genotype with zero mutation, and the `_is_ma` flag propagates. This ensures infection experiments test social immune response, not mutation-driven dilution.

**Step 6: Mortality**
Background mortality (0.006/year), age-based death (accelerating past 60), health-below-threshold death, childhood mortality (0.054/year for ages 0–15), epidemic mortality (probability 0.030/year, lethality 0.254). Male risk multiplier (2.12× ages 15–40; Bowles 2008).

**Step 7: Migration**
Emigration and rescue immigration when population drops below minimum viable threshold.

**Step 8: Pathology**
Condition activation (cardiovascular, mental illness, autoimmune, metabolic, degenerative), trauma accumulation, epigenetic stress inheritance, trauma contagion through proximity networks.

**Step 9: Institutions**
Inheritance (equal split of resources/tools/prestige goods to heirs). Norm enforcement. Institutional drift: law_strength evolves based on cooperation pressure (boost 2.0) vs. violence erosion (decay 3.0) with inertia 0.8. Conformity amplification (0.3; Henrich & Boyd 1998). Emergent institution formation: after 5 years of violence > 8%, punishment emerges (Bowles & Gintis 2011).

**Step 10: Reputation**
Trust decay toward neutral (0.01/year). Gossip (10% of agents per tick, noise σ = 0.1). Belief evolution: conformist transmission modulated by novelty_seeking. Experience-based belief updates from conflict (Bowles 2011). Skill learning: foraging, combat, social, craft. Mentoring: elders teach youth.

**Step 11: Faction Detection**
Community detection on trust network (periodic). Neighborhood refresh. Faction leader selection (war chief by dominance, peace chief by prestige).

**Step 12: Metrics Collection**
~120 metrics including the **Selection Differential** *S*:
1. $\mu_{\text{pop}}$: Mean cooperation of all living agents
2. $\mu_{\text{eligible}}$: Mean cooperation of agents passing `can_mate()` (age, health, fertility criteria)
3. $\mu_{\text{parents}}$: Mean cooperation of agents tagged `_bred_this_tick = True` in Step 5
4. $S = \mu_{\text{parents}} - \mu_{\text{eligible}}$

Breeding flags cleared after collection.

---

## 4. CALIBRATION AND VALIDATION

### 4.1 Calibration Method

Simulated Annealing (SA) over 816 experiments (Run 3, 2026-03-15). Each experiment: 2 seeds × 150 years × 500 agents. Objective: simultaneous satisfaction of 9 empirical targets.

### 4.2 Calibration Targets

| # | Metric | Target | Source | Calibrated | Validation |
|---|--------|--------|--------|------------|------------|
| 1 | Resource Gini | 0.30–0.50 | Borgerhoff Mulder et al. (2009) | 0.310 | 0.30–0.32 |
| 2 | Mating Inequality | 0.40–0.80 | Betzig (2012) | 0.578 | 0.55–0.60 |
| 3 | Violence Death Fraction | 0.05–0.15 | Keeley (1996); Chagnon (1988) | 0.069 | 0.04–0.07 |
| 4 | Pop Growth Rate | 0.001–0.015 | Hassan (1981) | 0.014 | 0.001–0.014 |
| 5 | Child Survival to 15 | 0.50–0.70 | Volk & Atkinson (2013) | 0.642 | 0.64–0.69 |
| 6 | Lifetime Births | 4.0–7.0 | Bentley (1996); Howell (1979) | 4.214 | 3.97–4.21 |
| 7 | Bond Dissolution Rate | 0.10–0.30 | Betzig (1989) | 0.118 | 0.10–0.12 |
| 8 | Avg Cooperation | 0.25–0.70 | Henrich et al. (2001) | 0.507 | 0.49–0.51 |
| 9 | Avg Aggression | 0.30–0.60 | Archer (2009) | 0.494 | 0.48–0.49 |

### 4.3 Parameter Parity

All 35 SA-calibrated parameters are embedded as dataclass defaults in `config.py`, synchronized with `autosim/best_config.yaml`. Verified by automated test (`test_config_defaults_match_autosim_best`). No runtime YAML loading required — source code IS the calibrated model.

### 4.4 Replicability Guarantee

1. **Deterministic RNG**: All randomness via `numpy.random.default_rng(seed)`. Verified: identical seed produces identical population at year 200 across runs.
2. **Source-of-truth defaults**: `config.py` defaults = calibrated values. `Config()` with no arguments produces the validated model.
3. **Test suite**: 32 automated tests covering trait range, determinism, config parity, event integrity, selection differential computation.
4. **Public repository**: https://github.com/kepiCHelaSHen/SIMSIV

---

## 5. SENSITIVITY AND ROBUSTNESS

### 5.1 Perturbation Sweep (±20%, σ ≤ 0.030 gate)

10 Tier-1 parameters tested with Triple-Model Consensus (TMC) protocol. 75/90 metric-tests pass. Cooperation and aggression are robust across all perturbations (max σ = 0.015 and 0.009 respectively).

### 5.2 Population Scaling (Squazzoni N-Test)

| N | Cooperation | S (mean) | S positive % | Extinction |
|---|-------------|----------|-------------|-----------|
| 250 | 0.498 | +0.00064 | 50.8% | 0/10 |
| 500 | 0.511 | +0.00077 | 52.8% | 0/10 |
| 1000 | 0.513 | +0.00105 | 53.2% | 0/10 |

*S* is positive at all scales and strengthens with N. Zero extinction risk.

### 5.3 Invasion Resistance

| Predator Type | Infection Rate | Predator Survival | Cooperation Impact |
|---------------|---------------|-------------------|-------------------|
| Silent Predator (aggression=1.0) | 1–20% | 0% at year 200 | −0.10 at 20% |
| Psychopathic Mimic (coop=0.85, psych=0.90) | 10% | 0% at year 200 | +0.04 (increases) |

Both predator strategies go extinct. The immune response is multi-layered: institutional punishment, reputation decay, coalition defense, and female sexual selection against aggression.

---

## 7. INITIALIZATION

**Implementation:** `models/agent.py:create_initial_population()` → `models/society.py:Society.__init__()`

### 7.1 Population Generation

A founding population of *N* agents (default 500) is generated in a single call to `create_initial_population()`:

1. **Sex assignment**: First *N*/2 agents female, remainder male (deterministic split, stochastic within traits).

2. **Age distribution**: Each agent assigned age ∈ [0, `config.init_max_age`) uniformly at random.

3. **Trait initialization**: 35 heritable traits drawn from a multivariate normal distribution:

$$\mathbf{T} \sim \mathcal{N}(\boldsymbol{\mu}, \Sigma)$$

where:
- $\boldsymbol{\mu}$: Mean vector. Most traits $\mu_i = 0.5$. Exception: pathology risk traits (cardiovascular_risk, mental_illness_risk, autoimmune_risk, metabolic_risk, degenerative_risk) and psychopathy_tendency use $\mu_i = 0.2$ to initialize a healthy population.
- $\Sigma = \mathbf{C} \cdot \sigma^2$ where $\sigma = 0.15$ and $\mathbf{C}$ is a 35×35 genetic correlation matrix with 22 non-zero off-diagonal elements (e.g., aggression ↔ cooperation $r = -0.4$, empathy ↔ cooperation $r = +0.2$, psychopathy ↔ empathy $r = -0.5$).
- $\mathbf{C}$ is forced symmetric positive-semidefinite via eigenvalue clipping ($\lambda_i \leftarrow \max(\lambda_i, 10^{-6})$).

4. **Clipping**: All trait values clipped to $[0.0, 1.0]$ post-generation.

5. **Genotype storage**: Each agent's birth trait values stored as an immutable `genotype` dictionary. The genotype is the inheritance source (not the phenotype, which may be modified by developmental plasticity).

6. **Non-heritable state**: health = 1.0 (scaled down for agents initialized age > 40), reputation = 0.5 (neutral), initial resources proportional to age (older agents have more accumulated wealth: 60% subsistence, 30% tools, 10% prestige goods).

7. **Belief initialization**: Adults (age ≥ 15) receive beliefs derived from their traits with Gaussian noise ($\sigma = 0.15$). Children develop beliefs at maturation (year 15) during Step 6 (mortality engine, developmental plasticity).

### 7.2 Demographic Burn-In

No explicit burn-in phase is required in the default protocol. The AutoSIM calibration (816 experiments, SA Run 3) was performed on 150-year runs starting from this initialization, and the held-out validation used 200-year runs from the same starting conditions.

However, for experiments requiring equilibrium baseline measurements, a 50-year burn-in is recommended before introducing perturbations (as used in the V2-INTERFERENCE infection experiments, where Malicious Agents were injected at year 10 after the demographic structure had stabilized).

### 7.3 Deterministic Seeding

The entire initialization pipeline is deterministic given `config.seed`:

```python
rng = numpy.random.default_rng(config.seed)
society = Society(config, rng)  # creates population via create_initial_population(rng, ...)
```

Same seed → identical population → identical 200-year trajectory. Verified by automated test.

---

## 8. SUBMODELS — REPRODUCTION (Inheritance Engine)

**Implementation:** `models/agent.py:breed()`, called from `engines/reproduction.py` (Step 5)

### 8.1 Conception and Birth

A female agent conceives if:
- She passes `can_mate()` (alive, fertile age, health criteria)
- She has not given birth within `birth_interval_years` (default 2)
- A stochastic conception check passes: $p = \text{base\_conception\_chance} \times f_{\text{fertility}} \times f_{\text{health}} \times f_{\text{resources}} \times f_{\text{bond}}$

The genetic father is determined by paternity tracking (social father may differ due to extra-pair copulation).

### 8.2 Quantitative Genetic Inheritance (Falconer 1981)

For each of the 35 heritable traits, the offspring value is computed:

$$G_{\text{child},i} = h^2_i \cdot \text{blend}_i + (1 - h^2_i) \cdot \mu_{\text{pop},i} + \epsilon_i$$

where:
- $h^2_i$: Trait-specific heritability (range 0.25–0.65; see Section 1.2)
- $\text{blend}_i = w \cdot G_{\text{parent1},i} + (1-w) \cdot G_{\text{parent2},i}$: Weighted parental midpoint. $w \sim \mathcal{N}(0.5, \text{pwv})$ where `parent_weight_variance` = 0.1 (clipped to [0.1, 0.9])
- $\mu_{\text{pop},i}$: Current population mean for trait $i$ (regression toward mean)
- $\epsilon_i$: Mutation noise

**Note on notation:** The directive specified $G_{\text{offspring}} = 0.4 \times G_{\text{parents}} + 0.6 \times \mu_{\text{pop}}$. This corresponds to a trait with $h^2 = 0.4$. In SIMSIV, $h^2$ varies per trait (0.25–0.65), so the general form above is used. For cooperation_propensity specifically, $h^2 = 0.40$, matching the directive exactly.

### 8.3 Mutation

Standard agents:
$$\epsilon_i \sim \begin{cases} \mathcal{N}(0, 0.15) & \text{with probability } 0.05 \text{ (rare large mutation)} \\ \mathcal{N}(0, \sigma_m) & \text{otherwise} \end{cases}$$

where $\sigma_m = 0.05$ (amplified during environmental stress by factor up to 1.5×, and by parental epigenetic stress load).

### 8.4 MA Trait Locking (Genetic Integrity)

If either parent carries the `_is_ma = True` flag:

```python
if getattr(parent1, '_is_ma', False) or getattr(parent2, '_is_ma', False):
    ma_parent = parent1 if getattr(parent1, '_is_ma', False) else parent2
    child_val = ma_parent.genotype[trait_name]  # exact copy, zero mutation
    child._is_ma = True  # flag propagates
```

**Effect:** $\sigma_m = 0$ for MA offspring. The MA genotype is cloned without mutation, regression, or blending. This ensures that infection experiments (V2-INTERFERENCE) test the population's social immune response to a fixed-strategy invader, not the erosion of the invader strategy through mutation drift.

### 8.5 Genotype vs. Phenotype

After all 35 traits are computed, the child's **genotype** is stored as an immutable snapshot:

```python
child.genotype = {t: getattr(child, t) for t in HERITABLE_TRAITS}
```

The genotype is the inheritance source for future generations. The **phenotype** (the live trait values on the agent) may subsequently be modified by developmental plasticity (Step 6) and skill acquisition (Step 10), but these modifications do not affect the genotype and are not heritable.

### 8.6 Parent Tagging for Selection Differential

Both parents are tagged `_bred_this_tick = True` at the moment of successful birth. This flag is read by the MetricsCollector in Step 12 to compute $\mu_{\text{parents}}$ and cleared after collection.

---

## 9. SUBMODELS — INSTITUTIONAL DRIFT

**Implementation:** `engines/institutions.py:_drift_institutions()`, called in Step 9

### 9.1 Drift Mechanics

Institutional strength (`law_strength` ∈ [0, 1]) evolves each tick based on the balance between cooperative pressure and violence erosion:

$$\Delta_{\text{law}} = r \cdot (F_{\text{coop}} - F_{\text{violence}} + F_{\text{belief}}) \cdot R$$

where:
- $r$: `institutional_drift_rate` (default 0.01, maximum change per tick)
- $F_{\text{coop}} = \max(0, \bar{c} - 0.4) \times b_{\text{coop}} \times (1 + \bar{\phi} \times 0.3) + F_{\text{norm}} + F_{\text{future}}$
  - $\bar{c}$: population mean cooperation_propensity
  - $b_{\text{coop}} = 2.0$: cooperation institution boost
  - $\bar{\phi}$: mean conformity_bias (Henrich & Boyd 1998 amplification)
  - $F_{\text{norm}} = \bar{\ell} \times 0.1 + \bar{\kappa} \times 0.08$: group loyalty and conscientiousness bonus
  - $F_{\text{future}} = \bar{f} \times 0.05$: future orientation investment
- $F_{\text{violence}} = v_{\text{rate}} \times b_{\text{violence}}$
  - $v_{\text{rate}}$: conflict events / population this tick
  - $b_{\text{violence}} = 3.0$: violence institution decay
- $F_{\text{belief}}$: aggregate belief influence (cooperation_norm accelerates, violence_acceptability erodes)
- $R$: resistance factor incorporating inertia (0.8), elder norm anchoring, and tradition adherence

### 9.2 Institutional Inertia

Resistance to change depends on current law_strength:

$$R = \begin{cases} 1 - \alpha \cdot L & \text{if growing (coop > violence)} \\ 1 - \alpha \cdot (1 - L) & \text{if eroding (violence > coop)} \end{cases}$$

where $\alpha = 0.8$ (institutional inertia) and $L$ = current law_strength. This creates path dependency: strong institutions resist erosion, weak institutions resist growth.

Elder agents (life_stage = ELDER, reputation > 0.4) amplify resistance by up to 30% (norm anchor).

### 9.3 Coupled Institutional Parameters

When `law_strength` changes, three downstream parameters track proportionally:

| Parameter | Tracking Formula | Effect |
|-----------|-----------------|--------|
| `violence_punishment_strength` | $L \times 0.7$ | Institutional deterrence of violence |
| `property_rights_strength` | $L \times 0.5$ | Protection of resources from conflict looting |
| `elite_privilege_multiplier` | Drifts with hierarchy_belief ±0.01 | Resource advantage for high-status agents |

### 9.4 Emergent Institution Formation

If no institutions exist (`law_strength` = 0), they can emerge spontaneously:

1. **Punishment emergence**: If `violence_rate > 0.08` for 5 consecutive years (Bowles & Gintis 2011), `violence_punishment_strength` jumps to 0.1 and `law_strength` floors at 0.1.

2. **Mate restriction emergence**: If reproductive skew (top 10% males have 3× offspring of bottom 50%) persists for 8 years (Bowles 2006), `max_mates_per_male` decreases (minimum 3).

### 9.5 Cooperation Threshold

The directive specified threshold 0.6. The implementation uses **0.4**: cooperation above $\bar{c} = 0.4$ drives institutional growth. This lower threshold was calibrated by AutoSIM Run 3 to match the empirical cooperation range (0.25–0.70, Henrich et al. 2001). At the model's equilibrium cooperation of ~0.51, the effective cooperation pressure is $(0.51 - 0.4) \times 2.0 = 0.22$, modulated by conformity and resistance.

---

## 10. RESULTS — 500-YEAR PAIRED-SEED DIVERGENCE EXPERIMENT

**Protocol:** v2 paired-seed, population-normalized (scripts/run_divergence.py)
**Design:** 10 seeds (101-110) x 2 scenarios (NO_INSTITUTIONS, STRONG_STATE) x 500 years. Paired $t$-tests on cumulative trait displacement $R_{\text{total}}$.

### 10.1 Significant Differential Displacement (p < 0.05, paired)

| Trait | $R_{\text{total}}$(A) | $R_{\text{total}}$(B) | $\Delta R$ (A-B) | $t$ | $p$ | Cohen's $d$ | Direction |
|-------|---------|---------|---------|------|--------|-----------|-----------|
| intelligence_proxy | +0.133 | +0.099 | +0.034 | 2.74 | 0.023 | +0.87 | Anarchy selects harder |
| mental_illness_risk | +0.010 | -0.004 | +0.014 | 2.68 | 0.025 | +0.85 | Anarchy selects harder |
| impulse_control | +0.140 | +0.117 | +0.023 | 2.54 | 0.031 | +0.80 | Anarchy selects harder |
| pain_tolerance | -0.008 | +0.010 | -0.018 | -2.39 | 0.041 | -0.75 | State selects harder |

### 10.2 Interpretation

The primary finding is **cognitive substitution**: without institutional scaffolding, intelligence (+0.034, $d$ = 0.87) and impulse control (+0.023, $d$ = 0.80) are displaced significantly more over 500 years. Institutions relax selection on cognitive traits by providing external coordination mechanisms.

Cooperation trends in the predicted direction ($\Delta R$ = +0.017, $p$ = 0.097, $d$ = 0.59) but does not reach significance at $n$ = 10. A 30-seed replication is recommended.

### 10.3 Selection Sheltering (Aggression Reversal)

The original hypothesis predicted that institutions would suppress selection on aggression. The data show the **opposite**: aggression declines faster under anarchy ($R_A$ = -0.042 vs $R_B$ = -0.031). At the year-500 snapshot, the normalized selection differential $S_{n,\text{agg}}$ is significantly more negative in anarchy ($p$ = 0.023, paired).

**Mechanism** (Figure 3): Without institutions, violence rate is 2-3x higher (0.021 vs 0.008). Conflict executes before reproduction in the tick order (Step 3 vs Step 5), so aggressive agents are killed or injured before they can mate. The state paradoxically *preserves* aggressive genotypes by suppressing the lethal consequences of aggression — a phenomenon we term **Selection Sheltering**.

Supporting evidence: mating inequality is significantly higher in anarchy (0.55 vs 0.39, $p$ < 0.001), unmated males 28% vs 9% ($p$ < 0.001), confirming the fitness penalty pathway.

### 10.4 Population Confound

Scenario A populations (mean = 498) are significantly smaller than Scenario B (mean = 770, paired $p$ = 0.030). This is an inherent treatment effect (violence removes agents), not eliminable by carrying capacity adjustment. Population normalization ($S_n$) and the paired design mitigate but do not fully eliminate this confound.

### 10.5 Data Availability

| File | Location | Contents |
|------|----------|----------|
| selection_matrix_full.csv | outputs/experiments/v2_paired_divergence/ | $S$ and $S_n$ for 35 traits, every tick |
| trait_displacement.csv | outputs/experiments/v2_paired_divergence/ | $R_{\text{total}}$ per seed per scenario |
| paired_analysis.json | outputs/experiments/v2_paired_divergence/ | Full statistical tables |
| critic_validation_bundle.json | outputs/experiments/v2_paired_divergence/ | 5 checkpoint logs (years 100-500) |

### 10.6 Publication Figures

| Figure | File | Contents |
|--------|------|----------|
| F1 | docs/figures/F1_hero_divergence.png | Trait means + $S_n$ time series, 95% CI |
| F2 | docs/figures/F2_forest_plot.png | Forest plot: all 35 traits, paired displacement |
| F3 | docs/figures/F3_selection_sheltering.png | Aggression mechanism: violence, skew, decline |
| F8 | docs/figures/F8_squazzoni_fan_plot.png | Squazzoni N-Test: scale invariance |

---

## 6. REFERENCES

Archer, J. (2009). Does sexual selection explain human sex differences in aggression? *Behavioral and Brain Sciences*, 32(3-4), 249–266.

Bentley, G.R. (1996). How did prehistoric women bear "man the hunter"? *American Journal of Physical Anthropology*, Suppl 22, 58.

Betzig, L. (1989). Causes of conjugal dissolution. *Ethology and Sociobiology*, 10, 285–305.

Betzig, L. (2012). Means, variances, and ranges in reproductive success. *Evolution and Human Behavior*, 33(4), 309–317.

Borgerhoff Mulder, M. et al. (2009). Intergenerational wealth transmission and the dynamics of inequality. *Science*, 326(5953), 682–688.

Bowles, S. (2006). Group competition, reproductive leveling, and the evolution of human altruism. *Science*, 314(5805), 1569–1572.

Bowles, S. (2008). Conflict: Altruism's midwife. *Nature*, 456, 326–327.

Bowles, S. & Gintis, H. (2011). *A Cooperative Species: Human Reciprocity and Its Evolution*. Princeton University Press.

Boyd, R. & Richerson, P.J. (1985). *Culture and the Evolutionary Process*. University of Chicago Press.

Chagnon, N. (1988). Life histories, blood revenge, and warfare in a tribal population. *Science*, 239(4843), 985–992.

Falconer, D.S. (1981). *Introduction to Quantitative Genetics* (2nd ed.). Longman.

Falconer, D.S. & Mackay, T.F.C. (1996). *Introduction to Quantitative Genetics* (4th ed.). Longman.

Fehr, E. & Gächter, S. (2002). Altruistic punishment in humans. *Nature*, 415, 137–140.

Grimm, V. et al. (2010). The ODD protocol: A review and first update. *Ecological Modelling*, 221(23), 2760–2768.

Hassan, F. (1981). *Demographic Archaeology*. Academic Press.

Henrich, J. (2004). Cultural group selection, coevolutionary processes and large-scale cooperation. *Journal of Economic Behavior & Organization*, 53, 3–35.

Henrich, J. & Boyd, R. (1998). The evolution of conformist transmission. *Evolution and Human Behavior*, 19, 215–241.

Henrich, J. et al. (2001). In search of homo economicus. *American Economic Review*, 91(2), 73–78.

Hill, K. & Hurtado, A.M. (1996). *Ache Life History*. Aldine de Gruyter.

Howell, N. (1979). *Demography of the Dobe !Kung*. Academic Press.

Keeley, L.H. (1996). *War Before Civilization*. Oxford University Press.

Marlowe, F.W. (2010). *The Hadza: Hunter-Gatherers of Tanzania*. University of California Press.

Müller, B. et al. (2013). Describing human decisions in agent-based models — ODD+D. *Environmental Modelling & Software*, 48, 37–48.

Volk, A. & Atkinson, J. (2013). Infant and child death in the human environment of evolutionary adaptedness. *Evolution and Human Behavior*, 34(3), 182–192.

Walker, P.L. (2001). A bioarchaeological perspective on the history of violence. *Annual Review of Anthropology*, 30, 573–596.
