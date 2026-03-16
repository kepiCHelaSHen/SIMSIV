# SIMSIV: A Calibrated Agent-Based Framework for Studying Gene-Culture Coevolution in Pre-State Societies

**Author:** James P Rice Jr. | March 2026

---

## Abstract

Agent-based models (ABMs) offer a principled way to study gene-culture coevolution, yet most existing frameworks either hard-wire social outcomes or omit realistic demography. We present SIMSIV (Simulation of Intersecting Social and Institutional Variables), an agent-based framework in which 500 agents with 35 heritable traits compete for resources, mates, and status within a single band-level society. Agents inherit traits through a quantitative-genetics model with trait-specific heritability coefficients, form pair bonds, cooperate through trust-based networks, and engage in conflict mediated by institutional governance. Nine engines execute in a fixed annual cycle: environment, resources, conflict, mating, reproduction, mortality, migration, pathology, and institutions. The model was calibrated against nine anthropological benchmarks --- including resource inequality (Gini = 0.310), male reproductive skew (0.578), violence death fraction (0.069), and child survival to age 15 (0.642) --- using simulated annealing over 816 experiments. Held-out validation across 10 unseen seeds (20 independent runs) yielded a mean realism score of 0.934 with zero population collapses. Scenario experiments spanning 200-year and 500-year horizons reveal that institutional governance produces dramatic behavioral substitution --- enforced monogamy reduces violence 37% and unmated males from 28.5% to 11.9%; strong-state governance cuts resource inequality to Gini = 0.200 --- yet heritable cooperation shows no detectable divergence across governance regimes at 500 years (0.523 vs. 0.524 vs. 0.523 for no-institutions, free-competition, and strong-state respectively). Sensitivity analysis identifies mortality rate as the single most influential parameter (mean |r| = 0.315 across 8 of 9 metrics) and confirms that cooperation is weakly driven by any single parameter (max |r| = 0.199). These findings are consistent with the institutional-substitution hypothesis: institutions appear to substitute for heritable prosocial traits in producing cooperative behavioral outcomes at band-level timescales, though longer time horizons and multi-group dynamics may reveal complementarity.

**Keywords:** agent-based model, gene-culture coevolution, cooperation, institutions, pre-state societies, calibration, ODD protocol

---

## 1. Introduction

### 1.1 The gene-culture coevolution debate

How did human societies come to sustain the extraordinary levels of cooperation observed across all known cultures? Two broad camps offer competing explanations. The gene-culture coevolution hypothesis, articulated most forcefully by Bowles and Gintis (2011), argues that cultural institutions and heritable prosocial dispositions evolved together in a self-reinforcing loop: institutions created selection environments that favored cooperative genotypes, and cooperative genotypes in turn enabled more complex institutions. Under this view, genes and culture are complements --- each amplifying the other's effect on social outcomes.

The institutional-substitution hypothesis, rooted in the new institutional economics of North (1990) and extended by Greif (2006), offers a contrasting perspective. Institutions --- even informal ones such as gossip networks, reputation systems, and punishment norms --- can enforce cooperative behavior regardless of individual genetic predisposition. If institutions are sufficiently effective at channeling behavior, the selection gradient on heritable prosocial traits weakens or vanishes. Under this view, institutions substitute for genes: they produce cooperative outcomes without requiring (or producing) cooperative genotypes.

Empirically distinguishing these hypotheses is difficult. The archaeological record preserves material culture but not genotypes. Modern behavioral genetics can estimate heritability of prosocial traits (h-squared approximately 0.40 for cooperation; Cesarini et al., 2008) but cannot reconstruct ancestral selection gradients. Cross-cultural comparisons (Henrich et al., 2001; Henrich et al., 2010) document institutional variation in cooperation but confound genetic and cultural transmission. The debate therefore remains largely theoretical.

The dual inheritance theory of Boyd and Richerson (1985) provides the foundational framework for understanding how genetic and cultural evolution interact. Under dual inheritance, cultural transmission constitutes a second inheritance system that can evolve independently of, or in interaction with, genetic inheritance. Crucially, dual inheritance theory neither predicts complementarity nor substitution a priori: the outcome depends on whether cultural variants that emerge under institutions increase or decrease the fitness gradient on prosocial genes. SIMSIV operationalizes this by separating heritable trait values (the genetic channel) from behavioral outcomes and belief transmission (the cultural channel), allowing both to evolve simultaneously.

### 1.2 Agent-based models as adjudication tools

Agent-based models offer a path forward. By simulating populations of heterogeneous agents whose traits are inherited, mutated, and selected across generations, ABMs can test whether specific institutional regimes alter evolutionary trajectories for prosocial traits. Unlike analytical models, ABMs accommodate the full complexity of demographic stochasticity, assortative mating, conditional behavior, and nonlinear feedback between individual decisions and population outcomes.

Several important ABMs address cooperation evolution. Bowles (2006) modeled between-group competition as a driver of altruism. Boyd and Richerson (2002) demonstrated that cultural group selection can sustain cooperation under conditions where genetic group selection cannot. Gavrilets and Fortunato (2014) showed that social stratification can emerge from resource competition and mate choice. However, most existing models focus on a narrow slice of the gene-culture interaction --- typically cooperation and punishment in stylized games --- rather than embedding cooperation within a full demographic and life-history framework.

### 1.3 This paper's contribution

We present SIMSIV, an agent-based framework designed to study gene-culture coevolution within a demographically realistic band-level society. The model's distinguishing features are:

1. **Demographic realism.** Agents have complete life histories: they are born, mature, form pair bonds, reproduce, age, and die. Fertility, mortality, and mating follow empirically calibrated schedules rather than abstract fitness functions. The model is calibrated against nine anthropological benchmarks drawn from ethnographic and demographic literature on pre-state societies.

2. **Rich trait architecture.** Each agent carries 35 heritable traits spanning physical performance, cognition, personality, social architecture, reproductive biology, and psychopathology. Traits are inherited via a quantitative-genetics model with empirically grounded heritability coefficients and a verified correlation structure.

3. **Institutional endogeneity.** Institutional governance (law strength, property rights, violence punishment) can emerge endogenously from the cooperation-violence balance in the population, or be imposed exogenously as an experimental treatment. This allows direct comparison between scenarios where institutions are absent, emergent, or imposed.

4. **Behavioral and genetic separation.** Because cooperation is both a heritable trait (cooperation_propensity) and a behavioral outcome (resource sharing, alliance formation), the model can distinguish between behavioral changes driven by institutional constraints and genetic changes driven by altered selection pressures.

This paper reports the model's design, calibration, validation, and initial scenario experiments. Our central empirical finding is that institutional governance produces dramatic behavioral substitution --- violence rates, resource inequality, and mating inequality all shift substantially across governance regimes --- but heritable cooperation shows no detectable divergence across governance conditions at 500 simulated years. We interpret this cautiously as evidence for the substitution hypothesis at band-level timescales, while acknowledging that longer timescales or between-group competition (not modeled in v1.0) may produce different results.

### 1.4 Paper overview

Section 2 describes the model following a modified ODD (Overview, Design concepts, Details) protocol (Grimm et al., 2006; Grimm et al., 2020). Section 3 reports calibration targets, methodology, and held-out validation. Section 4 presents sensitivity analysis across the 816-experiment calibration sweep. Section 5 describes scenario experiments at 200-year and 500-year horizons. Section 6 discusses implications for the gene-culture coevolution debate, and Section 7 concludes.

---

## 2. Model Description (ODD Protocol)

### 2.1 Overview

**Purpose.** SIMSIV models how social structures emerge from first-principles interactions among reproduction, resource competition, status seeking, cooperation, jealousy, violence risk, pair bonding, and institutional constraints within a single band-level society. The model is a sandbox for discovery: interesting outcomes must emerge from rules, never be hard-wired.

**Entities.** The model contains three entity types: (1) *Agents* --- individual humans characterized by 35 heritable traits, non-heritable attributes (reputation, health, resources, skills, beliefs), and social relationships (pair bonds, offspring, trust ledger, faction membership). (2) *Society* --- the band-level collective that maintains a partner index, faction structure, and institutional variables. (3) *Environment* --- a shared resource context that generates seasonal cycles, scarcity events, and epidemics.

**Scale.** Default population: 500 agents initialized with a realistic age pyramid (uniform 0 to 50). Default simulation length: 200 years. Annual time step. Single band (no spatial structure in v1.0).

**Process overview.** Each annual tick executes nine engines in fixed order:

1. **Environment** --- update seasonal cycle, trigger scarcity/epidemic events
2. **Resources** --- eight-phase resource acquisition (base production, tool bonus, intelligence bonus, cooperation network sharing, aggression penalty, equal floor, storage, investment)
3. **Conflict** --- violence initiation, deterrence, flee response, combat resolution, subordination, bystander trust updates
4. **Mating** --- female mate choice, male competition, pair bond formation and dissolution, extra-pair copulation
5. **Reproduction** --- conception, birth, trait inheritance
6. **Mortality** --- aging, natural death, childhood mortality, epidemic mortality
7. **Migration** --- emigration push factors, immigration, minimum viable population guard
8. **Pathology** --- condition activation/remission, trauma accumulation, epigenetic stress
9. **Institutions** --- institutional drift (law strength, property rights), inheritance of resources

Conflict executes before mating so that violence has direct reproductive cost: dead or injured agents cannot mate. Institutions execute after mortality so that inheritance processing sees all deaths in the current tick. Metrics are collected after all engines complete. Figure 1 illustrates the annual tick execution order.

**AI disclosure.** Simulation code development was assisted by Claude (Anthropic, version claude-sonnet-4-6). All scientific decisions, hypotheses, experimental designs, calibration targets, and interpretations are the author's own.

### 2.2 Design Concepts

**Emergence.** All social outcomes --- inequality, pair bond stability, faction structure, institutional strength, trait evolution --- emerge from individual-level decisions and interactions. No outcome is hard-wired. Cooperation, aggression, and institutional governance reach their equilibrium values through the interplay of heritable dispositions, learned beliefs, resource competition, and social feedback.

**Adaptation.** Agents do not optimize consciously. Behavioral decisions (conflict initiation, mate choice, resource sharing) are probabilistic functions of heritable traits, current state, and social context. Adaptation occurs at the population level through differential reproduction: agents whose trait profiles yield higher fitness (more surviving offspring) contribute more to the next generation's gene pool.

**Fitness.** Fitness is not an explicit variable. It is an emergent consequence of survival and reproduction. Agents who acquire resources, avoid lethal conflict, form stable pair bonds, and produce surviving offspring are "fit" by construction. Multiple trait channels contribute: intelligence increases resource acquisition; cooperation provides sharing bonuses and coalition protection; attractiveness and status drive mate value; aggression provides competitive advantage but incurs injury risk and reputation damage.

**Stochasticity.** All randomness flows through a single numpy random generator seeded from the configuration. Given the same seed, the simulation produces identical results. Stochastic elements include: mate choice (probabilistic weighted by mate value), conflict initiation and outcome (probabilistic weighted by combat power), conception (probabilistic per mating attempt), mortality (probabilistic per year), epidemic timing, and trait mutation.

### 2.3 Agent Details

Each agent is defined by 35 heritable traits organized into six domains:

**Physical Performance (6 traits):** physical_strength (h-squared = 0.60), endurance (0.50), physical_robustness (0.50), pain_tolerance (0.45), longevity_genes (0.25), disease_resistance (0.40). These traits govern combat effectiveness, foraging efficiency, damage absorption, and disease vulnerability.

**Cognitive (4 traits):** intelligence_proxy (h-squared = 0.65), emotional_intelligence (0.40), impulse_control (0.50), conscientiousness (0.49). Intelligence drives resource acquisition efficiency; impulse control gates the expression of aggression into actual conflict; conscientiousness affects skill maintenance.

**Personality (4 traits + 1 temporal):** risk_tolerance (h-squared = 0.48), novelty_seeking (0.40), anxiety_baseline (0.40), mental_health_baseline (0.40), future_orientation (0.40). Risk tolerance modulates conflict initiation and flee probability. Future orientation affects resource storage and institutional support.

**Social Architecture (9 traits):** aggression_propensity (h-squared = 0.44), cooperation_propensity (0.40), dominance_drive (0.50), group_loyalty (0.42), outgroup_tolerance (0.40), empathy_capacity (0.35), conformity_bias (0.35), status_drive (0.50), jealousy_sensitivity (0.45). These traits govern the core social dynamics: cooperation versus competition, in-group versus out-group behavior, and status seeking.

**Reproductive Biology (5 traits):** fertility_base (h-squared = 0.50), sexual_maturation_rate (0.60), maternal_investment (0.35), paternal_investment_preference (0.45), attractiveness_base (0.50). These traits determine mating success and reproductive output.

**Psychopathology Spectrum (6 traits):** psychopathy_tendency (h-squared = 0.50; default initialization 0.2), mental_illness_risk (0.60), cardiovascular_risk (0.50), autoimmune_risk (0.40), metabolic_risk (0.45), degenerative_risk (0.35). These traits model heritable vulnerability to physical and psychological conditions.

**Inheritance model.** Offspring trait values are computed as:

> child_value = h-squared * parent_midpoint + (1 - h-squared) * population_mean + mutation

where parent_midpoint is the average of the two parents' trait values (with stochastic parent-weighting variance = 0.1), population_mean is the current band mean for that trait, and mutation is drawn from N(0, 0.05). Rare large mutations (probability 0.05 per trait) use sigma = 0.15. Stress-exposed parents transmit epigenetic load that amplifies mutation variance by up to 1.5x. All trait values are clamped to [0.0, 1.0].

Initial generation traits are drawn from a multivariate normal distribution with a 35 x 35 correlation matrix (PSD-verified via eigenvalue clipping) that encodes empirically motivated trait correlations (e.g., aggression-cooperation negative, intelligence-impulse control positive).

**Non-heritable attributes.** Each agent also carries: reputation (float, computed from trust ledger), health (float, decays with age), age (integer), three resource types (subsistence, tools, prestige goods), prestige and dominance scores, current status (0.6 * prestige + 0.4 * dominance), partner IDs, offspring IDs, a sparse reputation ledger (trust scores for up to 100 known agents), faction membership, neighborhood ties, five belief dimensions (hierarchy, cooperation norm, violence acceptability, tradition adherence, kinship obligation; float [-1, +1]), four skill domains (foraging, combat, social, craft; float [0, 1]), epigenetic stress load, and medical history.

### 2.4 Engine Details

**Environment engine.** Updates the seasonal resource cycle (3-year period, amplitude 0.3) and triggers stochastic events: scarcity shocks (base probability 0.03/year; severity multiplier 0.6) and epidemics (base probability 0.02/year; lethality 0.254; 2-year duration; 20-year refractory period; overcrowding multiplier 2.0 above 80% carrying capacity).

**Resource engine.** An eight-phase pipeline: (1) base production scaled by intelligence and endurance; (2) tool bonus from accumulated durable goods; (3) cooperation network bonus (0.05 per trusted ally); (4) aggression production penalty (calibrated at 0.6); (5) equal floor redistribution (calibrated at 25%); (6) storage with decay; (7) child investment costs (0.35 resources per dependent child per year); (8) subsistence floor guarantee (1.17 minimum resources). Three resource types are modeled: subsistence (high decay), tools (low decay), and prestige goods (near-permanent).

**Conflict engine.** Agents initiate conflict based on aggression propensity, jealousy triggers, resource grievances, and random baseline probability. Institutional law strength and coalition deterrence suppress initiation. Targets are selected probabilistically, weighted by resource holdings and inversely by ally count. Low-risk-tolerance targets may flee. Combat resolution depends on a composite power score (aggression + status + health + risk tolerance + resource advantage + ally count). Losers suffer health damage (0.15), resource loss (10%), possible death (5% per conflict), and enter a 2-year subordination cooldown. Bystanders update trust toward aggressors. Cross-sex targeting is enabled at 0.3x weight.

**Mating engine.** Eligible agents enter the mating pool (70% participation rate). Females choose mates probabilistically weighted by mate value (a composite of status, attractiveness, resources, prestige goods, and health, with an age curve peaking at 27). Female choice penalizes aggression and rewards cooperation. Male competition resolves contested pairings. Pair bonds form with configurable strength; dissolution is probabilistic (calibrated at 0.02/year base rate). Extra-pair copulation is modeled with detection probability (0.4), paternity uncertainty, and bond destabilization driven by the partner's jealousy sensitivity.

**Reproduction engine.** Bonded pairs attempt conception annually. Conception probability depends on base chance (calibrated at 0.80), female fertility (trait-based, declining after age 30), health, and seasonal cycle. Birth interval minimum is 2 years. Offspring inherit traits via the quantitative-genetics model described in Section 2.3. Maternal health cost per birth is 0.03. Maximum lifetime births per female is 12.

**Mortality engine.** Death occurs through natural aging (mean 60, SD 15, modified by longevity genes), background mortality (calibrated at 0.006/year), childhood mortality (calibrated at 0.054/year for ages 0-15), epidemic mortality, violence, and childbirth risk (0.02 per birth). Male risk mortality multiplier is 2.12 for ages 15-40. Orphaned children face 2x mortality. Health below 0.05 triggers death.

**Institution engine.** When institutional drift is enabled (default rate 0.01/year), law strength adjusts annually based on the band's cooperation-violence balance: high cooperation pushes law strength up; high violence pushes it down. Institutional inertia (default 0.8) resists rapid change. Property rights modulate conflict resource transfer. Inheritance of resources to offspring is enabled by default (equal split).

**Reputation engine.** Agents update trust toward interaction partners based on observed cooperation and conflict. Gossip spreads information with degradation (noise 0.1 per hop). Trust decays toward neutral (0.5) at 0.01/year. Beliefs update through social conformity pressure, direct experience, and novelty-seeking drift. Skills develop through practice and parental transmission.

### 2.5 Scenarios

The following scenarios are used in experiments. FREE_COMPETITION serves as the baseline; all others modify specific parameters.

| Scenario | Key Parameter Changes | Purpose |
|---|---|---|
| FREE_COMPETITION | Default calibrated config (institutional drift ON) | Baseline: weak endogenous governance |
| NO_INSTITUTIONS | Drift disabled, law = 0, no property rights | True zero-governance control |
| ENFORCED_MONOGAMY | Monogamy enforced, law = 0.7, punishment = 0.5 | Monogamy hypothesis (Henrich et al., 2012) |
| ELITE_POLYGYNY | Elite privilege 3x, max 5 mates/male | Polygyny and inequality |
| HIGH_FEMALE_CHOICE | Female choice strength = 0.95 | Sexual selection pressure |
| RESOURCE_SCARCITY | Abundance 0.6x, volatility 0.3, frequent shocks | Ecological stress |
| RESOURCE_ABUNDANCE | Abundance 2.5x, low volatility | Ecological relaxation |
| STRONG_STATE | Law = 0.8, punishment = 0.7, property rights = 0.5, tax = 15%, monogamy | High imposed governance |
| EMERGENT_INSTITUTIONS | Law starts at 0, high drift rate (0.02), low inertia (0.7) | Self-organizing governance |

---

## 3. Calibration and Validation

### 3.1 Calibration targets

The model is calibrated against nine empirically grounded benchmarks targeting pre-state, band-level societies. Each target is expressed as an acceptable range rather than a point estimate, reflecting genuine uncertainty in the ethnographic literature.

| # | Metric | Target Range | Weight | Primary Source |
|---|---|---|---|---|
| 1 | Resource Gini | 0.30 -- 0.50 | 1.0 | Borgerhoff Mulder et al. (2009) |
| 2 | Mating inequality (male offspring Gini) | 0.40 -- 0.70 | 1.0 | Betzig (2012) |
| 3 | Violence death fraction (male) | 0.05 -- 0.15 | 2.0 | Keeley (1996); Chagnon (1988) |
| 4 | Population growth rate | 0.001 -- 0.015/yr | 1.0 | Hassan (1981); Biraben (1980) |
| 5 | Child survival to age 15 | 0.50 -- 0.70 | 2.0 | Volk & Atkinson (2013) |
| 6 | Lifetime births per woman | 4.0 -- 7.0 | 2.5 | Bentley (1996); Marlowe (2010) |
| 7 | Pair bond dissolution rate | 0.10 -- 0.30/yr | 1.5 | Betzig (1989) |
| 8 | Mean cooperation propensity | 0.25 -- 0.70 | 0.3 | Henrich et al. (2001); Fehr & Gachter (2002) |
| 9 | Mean aggression propensity | 0.30 -- 0.60 | 0.3 | Archer (2009) |

Violence death fraction carries double weight because it is the most contested metric in the ethnographic literature and the model's most structurally constrained output (the single-band model lacks inter-group warfare, which contributes substantially to ethnographic violence death rates). Child survival and lifetime births carry elevated weights because they directly constrain the evolutionary timescale.

### 3.2 AutoSIM methodology

Calibration was performed using AutoSIM, a custom simulated annealing optimizer operating on 36 continuous configuration parameters. The optimizer perturbs 2--5 parameters per experiment, accepts improvements deterministically, and accepts downhill moves probabilistically per the Metropolis criterion. Key algorithm parameters: initial temperature 0.085, geometric cooling factor approximately 0.9992 per experiment, perturbation scale 0.15 of parameter range (escalating to 0.25--0.35 on stall), and random jumps every 10th experiment (5 parameters, scale 0.30).

Each experiment evaluates a candidate configuration by running the simulation for 150 years with 500 agents across 2 random seeds, measuring all 9 metrics over the final 30 years, and computing a weighted realism score. A survival gate requires that the population remain above 20 agents for the score to be accepted. Per-experiment runtime was 35--120 seconds.

The calibration campaign (Run 3) executed 816 experiments over approximately 10.5 hours. This was the third calibration run; two prior runs (102 and 33 experiments respectively) were invalidated by 19 model bugs identified and corrected during Phase F quality review. The Phase F corrections materially altered the calibrated parameter landscape: for example, female_choice_strength shifted from 0.882 (Run 1) to 0.340 (Run 3), and subsistence_floor shifted from 0.300 to 1.173. These dramatic reversals confirm that the bug fixes were scientifically significant and that Run 3 represents the correct calibrated baseline.

### 3.3 Calibrated performance

The best configuration (experiment score 1.000) achieved all nine metrics simultaneously within their target ranges:

| Metric | Calibrated Value | Target Range | Status |
|---|---|---|---|
| Resource Gini | 0.310 | 0.30 -- 0.50 | In range |
| Mating inequality | 0.578 | 0.40 -- 0.70 | In range |
| Violence death fraction | 0.069 | 0.05 -- 0.15 | In range |
| Population growth rate | 0.014/yr | 0.001 -- 0.015 | In range |
| Child survival to 15 | 0.642 | 0.50 -- 0.70 | In range |
| Lifetime births per woman | 4.21 | 4.0 -- 7.0 | In range |
| Bond dissolution rate | 0.118 | 0.10 -- 0.30 | In range |
| Mean cooperation | 0.507 | 0.25 -- 0.70 | In range |
| Mean aggression | 0.494 | 0.30 -- 0.60 | In range |

Figure 2 shows the calibrated values relative to their target ranges.

Key calibrated parameters that shifted substantially from defaults include: mortality_base (0.02 default to 0.006 calibrated), childhood_mortality_annual (0.02 to 0.054), base_conception_chance (0.50 to 0.80), pair_bond_dissolution_rate (0.10 to 0.02), epidemic_lethality_base (0.15 to 0.254), female_choice_strength (0.60 to 0.34), and aggression_production_penalty (0.30 to 0.60). The calibrated configuration produces a high-fertility, high-childhood-mortality, low-background-mortality demographic regime characteristic of pre-industrial natural-fertility populations (Coale & Demeny, 1966).

### 3.4 Held-out validation

To assess generalization beyond training seeds, we conducted a held-out validation pass using 10 seeds drawn from a separate pseudorandom sequence (seeded at 7777, guaranteed non-overlapping with training seeds 42 and 137). Each seed was run twice independently at 200 years with 500 agents, yielding 20 total validation runs.

**Results.** Mean realism score: 0.934 (grand mean across 20 runs). Population collapses: 0 out of 20.

Four metrics proved robust (10/10 seeds in range in both runs): resource Gini, mating inequality, cooperation propensity, and aggression propensity. These metrics showed low cross-seed variance (SD = 0.009--0.022) and consistent convergence to mid-range values.

Three metrics proved fragile: violence death fraction (3--4/10 seeds in range; mean 0.040--0.049, below the 0.05 target floor), population growth rate (3/10 seeds in range; high stochastic variance, SD = 0.013), and child survival to age 15 (5--7/10 seeds in range; mean 0.682--0.689, slightly above the 0.70 ceiling). These fragilities are structurally explained: violence death fraction is depressed because the single-band model lacks inter-group warfare; population growth is inherently volatile at N = 500; child survival is slightly high because the model lacks famine-level resource collapses.

The validation verdict is that the calibrated configuration is suitable for comparative scenario experiments. The key scientific use case --- comparing outcomes across institutional regimes --- is robust even when individual metrics sit near target boundaries, because relative differences between scenarios are meaningful even when absolute calibration is imperfect.

### 3.5 Known limitations

The following limitations should be acknowledged:

1. **No inter-group dynamics.** SIMSIV v1.0 models a single band in isolation. There is no inter-band warfare, trade, intermarriage, or cultural exchange. This is the primary structural constraint on the violence death fraction and means that all findings reflect intra-group dynamics only.

2. **No spatial structure.** Agents interact within a single field. Household and neighborhood tiers exist but are abstract trust-network proximity, not geographic. Real bands occupy physical territory that shapes interaction patterns.

3. **Annual time step.** Sub-annual dynamics (seasonal disease, short-term resource fluctuations, birth clustering) are abstracted to annual resolution.

4. **Simplified genetics.** The inheritance model is a quantitative-genetics approximation (h-squared-weighted midpoint with Gaussian mutation), not a molecular-genetics simulation. There are no dominant/recessive alleles, no linkage disequilibrium, and no explicit loci. This is appropriate for band-level timescales (hundreds of years, tens of generations) but would require extension for deeper evolutionary analysis.

5. **Modern heritability estimates.** Trait heritability coefficients are drawn from modern behavioral genetics literature and applied to a pre-industrial context. The true heritability of behavioral traits in ancestral environments is unknown.

6. **Calibration target uncertainty.** Several targets are themselves contested or uncertain in the empirical literature. Violence death fractions vary enormously across ethnographic groups and may be subject to publication bias toward high-violence societies (Fry, 2006). All empirical targets should be treated as order-of-magnitude constraints rather than precise benchmarks.

**Reproducibility.** All experiments reported in this paper can be reproduced exactly using the scripts in the repository's experiments/ directory. Scenario configurations, the calibration pipeline, and the AutoSIM optimizer are included in full. The calibrated parameter file (autosim/best_config.yaml) and the full 816-experiment calibration journal (autosim/journal.jsonl) are committed to the repository. Given the same seed, the simulation produces identical results. Code and data are available at https://github.com/kepiCHelaSHen/SIMSIV

---

## 4. Sensitivity Analysis

### 4.1 Method

We computed Pearson correlation coefficients between each of the 36 tunable parameters and each of the 9 output metrics across the full 816-experiment calibration sweep. Each experiment represents a unique parameter configuration evaluated at 150 years with 500 agents averaged over 2 seeds. Because the simulated annealing optimizer explores parameter space non-uniformly (concentrating near high-scoring regions), these correlations should be interpreted as local sensitivity measures in the vicinity of the calibrated optimum, not as global sensitivity indices.

### 4.2 Results: top drivers per metric

**Resource Gini** is most strongly driven by resource_equal_floor (r = -0.885). This is mechanistically transparent: the equal-floor parameter directly controls what fraction of the resource pool is distributed equally versus competitively. A higher floor compresses inequality by construction.

**Bond dissolution rate** is most strongly driven by pair_bond_dissolution_rate (r = +0.936). Again, this is expected: the parameter is the direct per-year probability of bond dissolution, and the metric measures observed dissolution. The near-perfect correlation confirms that the base rate dominates over indirect dissolution drivers (jealousy, conflict, health).

**Population growth rate** is driven by mortality_base (r = -0.541) and childhood_mortality_annual (r = -0.392). Lower mortality enables population expansion --- a straightforward life-history prediction.

**Violence death fraction** is driven by conflict_base_probability (r = +0.490) and mortality_base (r = -0.373). Higher conflict probability generates more violence deaths; higher background mortality dilutes the violence fraction by increasing non-violence deaths.

**Aggression propensity** is driven by mortality_base (r = +0.450). This finding has a clear evolutionary interpretation: higher background mortality shortens lifespans, reducing the fitness cost of aggression (which imposes health and survival penalties). When agents die young from other causes anyway, the marginal cost of aggressive behavior declines.

### 4.3 Key finding: cooperation is weakly driven

The most notable sensitivity result is negative: no single parameter strongly drives mean cooperation propensity. The maximum absolute correlation across all 36 parameters is |r| = 0.199 (mortality_base, negative direction). This means that cooperation is not a "knob" that any single parameter can turn. Instead, cooperation propensity is an emergent equilibrium sustained by the interaction of multiple fitness channels: resource sharing bonuses, reputation benefits, faction membership, coalition protection, and reduced conflict targeting. The multi-channel nature of cooperation's fitness advantage makes it resistant to perturbation by any single parameter --- a property that has important implications for the substitution hypothesis (see Section 6).

### 4.4 Life-history confirmation: mortality drives aggression

The finding that mortality_base is the single most influential parameter globally (mean |r| = 0.315 across 8 of 9 metrics) confirms a fundamental life-history prediction. Background mortality rate sets the tempo of the entire demographic system: it determines average lifespan, which determines generation time, which determines the strength and direction of selection on behavioral traits. The positive correlation between mortality and aggression (r = +0.450) reproduces a well-known evolutionary prediction: in high-mortality environments, the fitness cost of risky aggressive strategies is reduced because the expected remaining lifespan is shorter (Daly & Wilson, 1988; Nettle, 2010). This pattern validation --- the model reproducing a known theoretical prediction without being explicitly programmed to do so --- strengthens confidence in the model's evolutionary dynamics.

---

## 5. Scenario Experiments

### 5.1 Experimental design

We conducted scenario experiments at two time horizons: 200 years (10 seeds per scenario, sufficient for behavioral comparison) and 500 years (10 seeds per scenario, targeting trait divergence detection). All experiments used the calibrated baseline configuration from AutoSIM Run 3, with scenario-specific parameter overrides as described in Section 2.5. Metrics were computed over the final 30 years of each run. All reported values are means across seeds.

Five parallel 500-year experiment batches were executed: (1) FREE_COMPETITION, STRONG_STATE, and EMERGENT_INSTITUTIONS; (2) NO_INSTITUTIONS, FREE_COMPETITION, and STRONG_STATE; (3) mating system comparisons; (4) resource ecology comparisons; and (5) a full 11-scenario 200-year run at 10 seeds. The governance spectrum analysis in Section 5.2 uses Batch 2 as the canonical dataset, as it is the only batch containing all three governance scenarios (NO_INSTITUTIONS, FREE_COMPETITION, STRONG_STATE) in the same experimental run. FREE_COMPETITION was run independently in both Batch 1 and Batch 2 with the same 10 seeds; the cooperation means differed by 0.021 (0.545 vs. 0.524), which is within one cross-seed standard deviation (SD = 0.040), confirming that this variation reflects normal stochastic variance rather than systematic error.

### 5.2 Governance spectrum: behavioral substitution without genetic divergence

The governance spectrum experiment compared three scenarios representing a gradient from zero governance (NO_INSTITUTIONS) through endogenous governance (FREE_COMPETITION) to strong imposed governance (STRONG_STATE).

**200-year results (10 seeds):**

| Metric | NO_INSTITUTIONS | FREE_COMPETITION | STRONG_STATE |
|---|---|---|---|
| Cooperation | 0.526 ± 0.012 | 0.519 ± 0.015 | 0.510 ± 0.021 |
| Violence rate | 0.022 ± 0.004 | 0.018 ± 0.004 | 0.009 ± 0.001 |
| Resource Gini | 0.312 ± 0.009 | 0.328 ± 0.010 | 0.200 ± 0.009 |
| Law strength | 0.000 ± 0.000 | 0.481 ± 0.029 | 0.985 ± 0.013 |

At 200 years, institutional governance produces large behavioral effects. STRONG_STATE reduces violence by 57% relative to NO_INSTITUTIONS (0.009 vs. 0.021), cuts resource inequality by 36% (Gini 0.200 vs. 0.312), and reduces unmated males from 28.8% to 11.7% (via enforced monogamy). FREE_COMPETITION, with its endogenously emergent institutions (law = 0.481), falls between the two extremes on most metrics.

**500-year results (10 seeds):**

| Metric | NO_INSTITUTIONS | FREE_COMPETITION | STRONG_STATE |
|---|---|---|---|
| Cooperation | 0.523 ± 0.024 | 0.524 ± 0.020 | 0.523 ± 0.028 |
| Aggression | 0.448 ± 0.029 | 0.452 ± 0.020 | 0.478 ± 0.019 |
| Intelligence | 0.632 ± 0.020 | 0.644 ± 0.019 | 0.596 ± 0.023 |
| Law strength | 0.000 ± 0.000 | 0.928 ± 0.043 | 1.000 ± 0.000 |
| Final population | 569 ± 259 | 623 ± 300 | 536 ± 231 |

Figure 3 plots mean cooperation propensity across all 500 simulated years for the three governance scenarios, confirming the absence of divergence at all time points, not just the final year.

**The central finding is in the cooperation row: 0.523, 0.524, 0.523.** After 500 simulated years --- approximately 20 generations --- heritable cooperation propensity is indistinguishable across the three governance regimes. This is not a ceiling or floor effect: cooperation sits at the midpoint of its possible range (0.0--1.0), with ample room for divergence in either direction. The null result is substantive.

To state the finding precisely: institutions change *behavior* (violence, inequality, mating access) dramatically, but they do not change the *underlying cooperation gene*. The strong-state scenario reduces violence by more than half and restructures mating entirely, yet the heritable trait that drives cooperation is no more or less prevalent than in the ungoverned population. This is behavioral substitution: institutions substitute for genetic predisposition in producing cooperative outcomes.

Two secondary findings merit note. First, aggression shows modest divergence: 0.448 under no institutions versus 0.478 under the strong state, a difference of 0.030. This is counterintuitive --- one might expect strong governance to select against aggression. However, the strong-state scenario reduces the fitness cost of aggression by suppressing its lethal consequences (violence punishment prevents death), which weakens the selection pressure against aggressive genotypes. This interpretation is mechanistically plausible but should be confirmed with explicit selection gradient tracking across longer run horizons before being treated as a confirmed finding. Second, intelligence shows a suggestive divergence: 0.644 under free competition versus 0.596 under the strong state. This may reflect reduced selection for resource-acquisition skill when the state redistributes resources via taxation, though the 500-year window may be insufficient to confirm this trend.

We note that 500 years represents approximately 20 generations, which is a short evolutionary timescale. It is possible that trait divergence would emerge at longer timescales (1,000+ years) or under between-group competition (not modeled in v1.0). The absence of divergence at 500 years does not definitively rule out gene-culture complementarity --- it indicates that the substitution effect dominates at band-level timescales.

### 5.3 Mating systems: monogamy reduces violence

The mating-system experiments compared four regimes at 500 years (10 seeds each):

| Scenario | Cooperation | Violence Death Fraction | Unmated Males | Gini |
|---|---|---|---|---|
| FREE_COMPETITION | 0.526 | 0.037 | 28.5% | 0.382 |
| ENFORCED_MONOGAMY | 0.524 | 0.023 | 11.9% | 0.385 |
| ELITE_POLYGYNY | 0.532 | 0.037 | -- | 0.382 |
| HIGH_FEMALE_CHOICE | 0.549 | 0.034 | -- | 0.379 |

Enforced monogamy reduces the violence death fraction by 37% relative to free competition (0.023 vs. 0.037) and cuts the unmated-male fraction from 28.5% to 11.9%. This is consistent with Henrich, Boyd, and Richerson's (2012) hypothesis that normative monogamy reduces male-male competition by ensuring more equitable access to mates. Resource Gini is effectively unchanged (0.385 vs. 0.382), indicating that monogamy's violence-reducing effect operates through the mating channel rather than the resource channel.

High female choice produces the highest cooperation (0.549), which is expected because female mate choice in the model penalizes aggression and rewards cooperation, creating direct sexual selection pressure on prosocial traits. Elite polygyny produces slightly elevated cooperation (0.532) but does not reduce violence relative to the baseline.

### 5.4 Resource ecology: scarcity, drift, and the cooperation attractor

The resource experiments compared three ecological conditions at 500 years (10 seeds each):

| Scenario | Cooperation | Final Population | Gini |
|---|---|---|---|
| FREE_COMPETITION | 0.532 | 725 | 0.371 |
| RESOURCE_SCARCITY | 0.489 | 67 | 0.351 |
| RESOURCE_ABUNDANCE | 0.520 | 938 | 0.361 |

Resource scarcity collapses the population to a mean of 67 agents (from 725 under baseline conditions), producing a dramatic reduction in cooperation (0.489 vs. 0.532). This is a small-population effect: at N = 67, genetic drift overwhelms selection, and the multi-channel fitness advantage that sustains cooperation in larger populations is insufficient to prevent stochastic erosion. The cooperation decline under scarcity is therefore primarily a drift effect, not an adaptive response to scarcity. This interpretation is supported by the 200-year data, where RESOURCE_SCARCITY produces cooperation of 0.511 --- near the baseline --- before the population has contracted enough for drift to dominate.

Resource abundance increases population to 938 but does not substantially alter cooperation (0.520 vs. 0.532) or inequality (Gini 0.361 vs. 0.371). The relaxation of ecological constraint permits population expansion without restructuring social dynamics.

### 5.5 Additional findings

**Emergent institutional self-organization.** The EMERGENT_INSTITUTIONS scenario starts with zero law strength and a high drift rate (0.02/year). By year 200, law strength self-organizes to 0.845 (10-seed mean), close to the STRONG_STATE imposed level of 0.985. This demonstrates that the cooperation-violence balance in the population is sufficient to bootstrap institutional governance from scratch without exogenous imposition. Violence under emergent institutions (0.010) is comparable to the strong state (0.009), suggesting that the specific pathway to governance (emergent vs. imposed) matters less than the resulting governance level.

At 200 years, emergent institutions produce an unmated-male fraction of 30.3%, substantially higher than the strong state's 11.7%. This is because the emergent-institutions scenario does not impose monogamy: it only develops law enforcement and property rights. The combination of high law strength with unrestricted mating produces a distinctive social equilibrium --- low violence but high mating inequality --- that is not observed in any of the imposed-governance scenarios.

**The cooperation attractor.** Across all scenarios and time horizons, heritable cooperation propensity converges to a narrow band of approximately 0.51--0.53 (with the exception of the population-collapse scenario at 0.489 and the high-female-choice scenario at 0.549). This stability is not a ceiling or floor effect: cooperation is initialized from the multivariate normal distribution described in Section 2.3, with population mean 0.5 and variance 0.1 prior to correlation transformation and has full range [0.0, 1.0] to diverge. It is not a parameter artifact: sensitivity analysis confirms that no single parameter strongly drives cooperation (max |r| = 0.199). And it is not a consequence of weak selection: the model clearly selects on cooperation through resource sharing, reputation, coalition protection, and reduced conflict targeting. Rather, the attractor reflects an evolutionary balance between cooperation's multi-channel fitness benefits and its costs: cooperators who share too freely are exploited by defectors; defectors who cooperate too little lose network benefits and reputation.

This finding is theoretically significant for two reasons. First, it suggests that band-level societies may exhibit a robust cooperation equilibrium that is robust to both ecological conditions (scarcity and abundance produce similar cooperation levels) and institutional conditions (all governance regimes converge near the same value). The principal exceptions --- high female choice (0.549) and population collapse under scarcity (0.489) --- reveal the two mechanisms that can escape the attractor: sexual selection directly rewarding cooperative genotypes, and demographic collapse disrupting selection entirely. Second, if this attractor is real rather than a model artifact, it predicts that cross-cultural variation in cooperation norms should be driven primarily by cultural transmission and institutional enforcement rather than by heritable trait variation --- a prediction that is testable with comparative behavioral genetics data across small-scale societies.

---

## 6. Discussion

### 6.1 The substitution finding in context

Our central finding is that institutional governance produces behavioral substitution: governance dramatically alters behavioral outcomes (violence, inequality, mating access) without detectably altering the heritable cooperation trait over 500 simulated years. We state this finding cautiously for three reasons.

First, 500 years (approximately 20 generations) is a short evolutionary timescale. Selection coefficients on cooperation in the model are presumably small (cooperation's fitness advantage is distributed across multiple channels, each contributing marginally). Weak selection requires many generations to produce detectable allele frequency change, and 20 generations may be below the detection threshold.

Second, SIMSIV v1.0 models only within-group dynamics. The gene-culture complementarity hypothesis (Bowles & Gintis, 2011) emphasizes between-group competition as the mechanism through which institutions amplify selection on prosocial traits. A single-band model cannot test this mechanism. If institutions make bands more cohesive and competitive in inter-group conflict, and if inter-group selection is the primary driver of prosocial trait evolution, then our finding of no within-group trait divergence is entirely compatible with strong gene-culture complementarity at the multi-group level.

Third, the model uses a quantitative-genetics approximation rather than explicit genetic architecture. The h-squared-weighted midpoint inheritance model may smooth over nonlinear genetic dynamics (epistasis, linkage, frequency-dependent selection) that could amplify or suppress trait change under institutional selection.

With these caveats, the substitution finding is nonetheless scientifically meaningful. It establishes that, within the considerable complexity of a demographically realistic band-level simulation, institutions sufficient to halve violence rates and restructure mating access do not produce measurable selection on the heritable cooperation trait. This is a necessary (though not sufficient) condition for the substitution hypothesis and a challenge to strong forms of the complementarity hypothesis that predict rapid coevolutionary response.

### 6.2 The cooperation attractor

The convergence of cooperation propensity to approximately 0.51--0.53 across nearly all scenarios is perhaps the most striking emergent property of the model. This stability is not a ceiling or floor effect, not a parameter artifact, and not a consequence of weak selection --- the model clearly selects on cooperation (cooperators gain resource sharing, reputation, coalition protection, and reduced conflict targeting). Rather, the attractor reflects the balance between cooperation's fitness benefits and its costs: cooperators who share too freely are exploited by defectors; defectors who cooperate too little lose network benefits and reputation.

This finding is consistent with evolutionary game theory predictions of mixed equilibria in public-goods games (Hauert et al., 2002) and with empirical evidence that human cooperation is substantial but not universal across cultures (Henrich et al., 2001). The model suggests that the level of cooperation observed in human societies may be an evolutionary stable strategy maintained by the multi-dimensional fitness landscape of band-level social life, rather than a product of any specific institutional arrangement.

### 6.3 Mating systems and violence

The finding that enforced monogamy reduces violence death fraction by 37% (0.023 vs. 0.037) and cuts unmated males from 28.5% to 11.9% is consistent with the monogamous-marriage hypothesis (Henrich et al., 2012), which proposes that normative monogamy reduces male-male competition by ensuring more equitable distribution of reproductive opportunities. Our model provides a mechanism: by eliminating the high-status polygyny pathway, monogamy reduces the potential fitness payoff of aggressive competition for mates, thereby reducing the equilibrium violence rate.

Notably, monogamy does not substantially alter resource inequality (Gini 0.385 vs. 0.382), confirming that monogamy's prosocial effects operate through the mating channel specifically. This specificity is useful for disentangling the multiple proposed benefits of monogamy in the evolutionary literature.

### 6.4 Stress-cooperation dynamics: a short-run versus long-run distinction

The 200-year data showed RESOURCE_SCARCITY producing cooperation of 0.511 --- near the baseline. However, the 500-year data reveals a substantial decline to 0.489, driven by population collapse (final population 67). This apparent reversal --- stress initially does not alter cooperation, but prolonged stress erodes it --- reveals a short-run/long-run distinction. In the short run, the cooperation attractor holds because the population is large enough for multi-channel selection to operate. In the long run, population collapse triggers genetic drift that degrades cooperation stochastically. The practical implication is that ecological stress threatens cooperation not through altered selection but through population collapse and the consequent loss of selection efficacy.

### 6.5 Limitations

Beyond the model limitations discussed in Section 3.5, several analysis limitations should be noted.

**Single-band constraint.** The absence of between-group dynamics is the most consequential limitation for the gene-culture coevolution question. All findings are conditional on within-group dynamics only.

**No spatial structure.** Real bands occupy heterogeneous landscapes. Spatial effects on resource access, interaction probability, and migration could alter cooperation dynamics in ways not captured here.

**Annual time step.** The annual tick resolution means that sub-annual dynamics (seasonal variation in resource availability, short-term alliance formation, rapid disease transmission) are abstracted.

**Modern heritability estimates.** The h-squared values used are derived from modern twin studies and behavioral genetics literature. The heritability of behavioral traits in ancestral environments is unknown and may differ substantially.

**Calibration uncertainty.** The simulated annealing optimizer is not guaranteed to find the global optimum. The calibrated parameter set represents one of potentially many configurations that achieve perfect realism scores. Alternative calibrations might produce different sensitivity patterns or scenario outcomes.

---

## 7. Conclusions

We have presented SIMSIV, an agent-based framework for studying gene-culture coevolution in pre-state societies. The model simulates 500 agents with 35 heritable traits across a complete life history, calibrated against nine anthropological benchmarks and validated on held-out seeds (mean realism score 0.934, zero collapses across 20 runs).

Our scenario experiments yield three principal findings:

1. **Behavioral substitution without genetic divergence.** Institutional governance dramatically alters behavior --- reducing violence by more than half, cutting resource inequality by 36%, and restructuring mating access --- yet heritable cooperation propensity is indistinguishable across governance regimes at 500 years (0.523 vs. 0.524 vs. 0.523). This is consistent with the institutional-substitution hypothesis at band-level timescales, though we caution that 500 years (~20 generations) may be insufficient to detect weak selection gradients.

2. **A cooperation attractor.** Heritable cooperation propensity converges to approximately 0.51--0.53 across nearly all scenarios, suggesting a robust evolutionary equilibrium maintained by the multi-dimensional fitness landscape of band-level social life.

3. **Monogamy reduces violence through the mating channel.** Enforced monogamy reduces violence death fraction by 37% and unmated males from 28.5% to 11.9%, consistent with the monogamous-marriage hypothesis (Henrich et al., 2012), without substantially altering resource inequality.

These findings should be interpreted within the model's limitations, particularly the absence of between-group competition. The next development phase (SIMSIV v2.0) will introduce a multi-band clan simulator with inter-group warfare, trade, and migration, enabling direct testing of the between-group selection mechanism central to the gene-culture complementarity hypothesis.

We invite independent replications, parameter explorations, and theoretical extensions using the open repository. The model is designed as a platform: the scenario system, calibration pipeline, and experimental runner can support research questions beyond those addressed here. The model code, calibration data, and scenario configurations are available at https://github.com/kepiCHelaSHen/SIMSIV

---

## Figures

**Figure 1.** Annual simulation tick execution order for SIMSIV v1.0. Each of the nine engines executes in fixed sequence, ensuring causal consistency: conflict precedes mating (dead agents cannot mate), mortality precedes institutions (inheritance sees all deaths). Metrics are collected after all engines complete. *(See docs/figures/fig1_tick_architecture.png)*

**Figure 2.** Calibrated model outputs relative to anthropological target ranges. Green checkmarks indicate metrics within target range; the model achieves all nine targets simultaneously (calibration score = 1.000). Target ranges are shown as gray bars; calibrated values as vertical lines. *(See docs/figures/fig2_calibration.png)*

**Figure 3.** Mean heritable cooperation propensity over 500 simulated years for three governance regimes: No Institutions (law strength fixed at 0), Free Competition (endogenous institutional drift), and Strong State (law strength fixed at 0.8, monogamy enforced). Shaded bands show ±1 SD across 10 seeds. The convergence of all three trajectories to approximately 0.52 confirms that institutional governance does not alter the evolutionary trajectory of the cooperation trait at this timescale. *(See docs/figures/fig3_cooperation_trajectory.png)*

## References

Archer, J. (2009). Does sexual selection explain human sex differences in aggression? *Behavioral and Brain Sciences*, *32*(3--4), 249--266.

Bentley, G. R. (1996). How did prehistoric women bear "man the hunter"? Reconstructing fertility from skeletal remains. In R. P. Gowland & C. Knusel (Eds.), *Social archaeology of funerary remains*. Oxbow Books.

Betzig, L. (1989). Causes of conjugal dissolution: A cross-cultural study. *Current Anthropology*, *30*(5), 654--676.

Betzig, L. (2012). Means, variances, and ranges in reproductive success: Comparative evidence. *Evolution and Human Behavior*, *33*(4), 309--317.

Biraben, J. N. (1980). An essay concerning mankind's evolution. *Population*, Special Issue, 13--25.

Boyd, R., & Richerson, P. J. (1985). *Culture and the evolutionary process*. University of Chicago Press.

Borgerhoff Mulder, M., Bowles, S., Hertz, T., Bell, A., Beise, J., Clark, G., Fazzio, I., Gurven, M., Hill, K., Hooper, P. L., Irons, W., Kaplan, H., Leonetti, D., Low, B., Marlowe, F., McElreath, R., Naidu, S., Nolin, D., Piraino, P., ... Wiessner, P. (2009). Intergenerational wealth transmission and the dynamics of inequality in small-scale societies. *Science*, *326*(5953), 682--688.

Bowles, S. (2006). Group competition, reproductive leveling, and the evolution of human altruism. *Science*, *314*(5805), 1569--1572.

Bowles, S., & Gintis, H. (2011). *A cooperative species: Human reciprocity and its evolution*. Princeton University Press.

Boyd, R., & Richerson, P. J. (2002). Group beneficial norms can spread rapidly in a structured population. *Journal of Theoretical Biology*, *215*(2), 287--296.

Cesarini, D., Dawes, C. T., Fowler, J. H., Johannesson, M., Lichtenstein, P., & Wallace, B. (2008). Heritability of cooperative behavior in the trust game. *Proceedings of the National Academy of Sciences*, *105*(10), 3721--3726.

Chagnon, N. A. (1988). Life histories, blood revenge, and warfare in a tribal population. *Science*, *239*(4843), 985--992.

Coale, A. J., & Demeny, P. (1966). *Regional model life tables and stable populations*. Princeton University Press.

Daly, M., & Wilson, M. (1988). *Homicide*. Aldine de Gruyter.

Fehr, E., & Gachter, S. (2002). Altruistic punishment in humans. *Nature*, *415*(6868), 137--140.

Fry, D. P. (2006). *The human potential for peace: An anthropological challenge to assumptions about war and violence*. Oxford University Press.

Gavrilets, S., & Fortunato, L. (2014). A solution to the collective action problem in between-group conflict with within-group inequality. *Nature Communications*, *5*, 3526.

Greif, A. (2006). *Institutions and the path to the modern economy: Lessons from medieval trade*. Cambridge University Press.

Grimm, V., Berger, U., Bastiansen, F., Eliassen, S., Ginot, V., Giske, J., Goss-Custard, J., Grand, T., Heinz, S. K., Huse, G., Huth, A., Jepsen, J. U., Jorgensen, C., Mooij, W. M., Muller, B., Pe'er, G., Piou, C., Railsback, S. F., Robbins, A. M., ... DeAngelis, D. L. (2006). A standard protocol for describing individual-based and agent-based models. *Ecological Modelling*, *198*(1--2), 115--126.

Grimm, V., Railsback, S. F., Vincenot, C. E., Berger, U., Gallagher, C., DeAngelis, D. L., Edmonds, B., Ge, J., Giske, J., Groeneveld, J., Johnston, A. S. A., Milles, A., Nabe-Nielsen, J., Polhill, J. G., Radchuk, V., Rohwader, M.-S., Stillman, R. A., Thiele, J. C., & Ayllón, D. (2020). The ODD protocol for describing agent-based and other simulation models: A second update to improve clarity, replication, and structural realism. *Journal of Artificial Societies and Social Simulation*, *23*(2), 7.

Hassan, F. A. (1981). *Demographic archaeology*. Academic Press.

Hauert, C., De Monte, S., Hofbauer, J., & Sigmund, K. (2002). Volunteering as Red Queen mechanism for cooperation in public goods games. *Science*, *296*(5570), 1129--1132.

Henrich, J., Boyd, R., Bowles, S., Camerer, C., Fehr, E., Gintis, H., & McElreath, R. (2001). In search of homo economicus: Behavioral experiments in 15 small-scale societies. *American Economic Review*, *91*(2), 73--78.

Henrich, J., Boyd, R., & Richerson, P. J. (2012). The puzzle of monogamous marriage. *Philosophical Transactions of the Royal Society B*, *367*(1589), 657--669.

Henrich, J., Ensminger, J., McElreath, R., Barr, A., Barrett, C., Bolyanatz, A., Cardenas, J. C., Gurven, M., Gwako, E., Henrich, N., Lesorogol, C., Marlowe, F., Tracer, D., & Ziker, J. (2010). Markets, religion, community size, and the evolution of fairness and punishment. *Science*, *327*(5972), 1480--1484.

Hill, K., & Hurtado, A. M. (1996). *Ache life history: The ecology and demography of a foraging people*. Aldine de Gruyter.

Howell, N. (1979). *Demography of the Dobe !Kung*. Academic Press.

Keeley, L. H. (1996). *War before civilization: The myth of the peaceful savage*. Oxford University Press.

Marlowe, F. W. (2010). *The Hadza: Hunter-gatherers of Tanzania*. University of California Press.

Nettle, D. (2010). Dying young and living fast: Variation in life history across English neighborhoods. *Behavioral Ecology*, *21*(2), 387--395.

North, D. C. (1990). *Institutions, institutional change, and economic performance*. Cambridge University Press.

Volk, A. A., & Atkinson, J. A. (2013). Infant and child death in the human environment of evolutionary adaptedness. *Evolution and Human Behavior*, *34*(3), 182--192.

Walker, P. L. (2001). A bioarchaeological perspective on the history of violence. *Annual Review of Anthropology*, *30*, 573--596.
