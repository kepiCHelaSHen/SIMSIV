# SIMSIV Results Summary

**Experiment:** 500-Year Paired-Seed Divergence (v2)
**Branch:** `v2-interference` | **Commit:** `71ac785`
**Date:** 2026-03-29
**Script:** `scripts/run_divergence.py`

---

## Experimental Design

| Parameter | Value |
|-----------|-------|
| Scenarios | NO_INSTITUTIONS (law=0) vs STRONG_STATE (law=0.8) |
| Seeds | 101-110 (10 paired seeds) |
| Years | 500 |
| Population | 500 initial, carrying_capacity=800 |
| Design | Paired: same seed runs both scenarios |
| Primary metric | Cumulative trait displacement: R_total = mean_genotype(yr500) - mean_genotype(yr1) |
| Selection metric | Sn = S / sqrt(N_eligible) (population-normalized) |
| Statistical test | Paired t-test (ttest_rel) with Cohen's d effect size |

---

## Primary Findings

### 1. Cognitive Substitution (Confirmed)

Institutional governance relaxes selection on cognitive traits. Without institutions, intelligence and impulse control are displaced significantly more over 500 years.

| Trait | R(A: No Inst) | R(B: State) | Delta R | t | p | Cohen's d |
|-------|--------------|-------------|---------|---|---|-----------|
| intelligence_proxy | +0.133 | +0.099 | **+0.034** | 2.74 | **0.023** | +0.87 |
| mental_illness_risk | +0.010 | -0.004 | **+0.014** | 2.68 | **0.025** | +0.85 |
| impulse_control | +0.140 | +0.117 | **+0.023** | 2.54 | **0.031** | +0.80 |
| pain_tolerance | -0.008 | +0.010 | **-0.018** | -2.39 | **0.041** | -0.75 |

All three cognitive traits (intelligence, impulse control, mental illness risk) show large effect sizes (d > 0.80) in the predicted direction: anarchy selects harder.

### 2. Cooperation Trend (Not Yet Significant)

Cooperation displacement trends in the substitution direction but does not reach significance:

- R(A) = +0.029, R(B) = +0.011, Delta R = +0.017
- t = 1.85, **p = 0.097**, d = 0.59

A 30-seed replication would likely resolve this (power analysis suggests n=25 for d=0.59 at alpha=0.05).

### 3. Selection Sheltering (Novel Finding)

**The state preserves aggressive genotypes by suppressing the violence that would eliminate them.**

Both scenarios select against aggression, but anarchy selects against it faster:
- R_agg(A) = -0.042, R_agg(B) = -0.031
- At year-500 snapshot: Sn_agg significantly more negative in anarchy (p = 0.023, paired)

Mechanism confirmed by mating system data (years 400-500):

| Metric | A: No Inst | B: State | p (paired) |
|--------|-----------|----------|------------|
| Violence rate | 0.021 | 0.008 | < 0.001 |
| Mating inequality | 0.55 | 0.39 | < 0.001 |
| Unmated males | 28% | 9% | < 0.001 |
| Reproductive skew | 0.46 | 0.38 | < 0.001 |

Causal pathway: Higher violence in anarchy (b) removes aggressive agents before reproduction (conflict runs before mating in the tick order), producing faster aggression decline (a) despite higher reproductive skew (c). See Figure F3.

### 4. Population Confound (Acknowledged)

Final populations differ: A = 498 vs B = 770 (paired p = 0.030). This is an inherent treatment effect (violence mortality), not eliminable by carrying capacity adjustment. Mitigated by:
- Population-normalized Sn metric
- Paired-seed design (controls for seed-level variance)
- Squazzoni N-Test confirming scale invariance of cooperation equilibrium

---

## Adversarial Audit Summary

The initial unpaired run (10 seeds, non-paired) showed spurious "substitution" signals at year 500 that failed statistical scrutiny:
- Cooperation: p = 0.164 (not significant)
- Conformity: snapshot noise, no sustained trend
- Most year-500 "SUB" flags were demographic noise inflated by small-population drift

The paired-seed v2 rerun corrected these issues and identified the real signal: **cognitive traits, not prosocial traits**, are the primary targets of institutional substitution.

---

## Squazzoni N-Test (Population Robustness)

| N | Cooperation (200yr mean) | sigma(S) | S positive % | Extinction |
|---|-------------------------|----------|-------------|-----------|
| 250 | 0.498 | 0.011 | 50.8% | 0/10 |
| 500 | 0.511 | 0.011 | 52.8% | 0/10 |
| 1000 | 0.513 | 0.011 | 53.2% | 0/10 |

Cooperation equilibrium converges to ~0.51 regardless of N. Selection noise follows 1/sqrt(N) theoretical scaling. See Figure F8.

---

## Invasion Resistance (V2-INTERFERENCE)

| Predator Type | Infection Rate | Survival at yr 200 | Cooperation Impact |
|---------------|---------------|--------------------|--------------------|
| Silent Predator (agg=1.0) | 1-20% | 0% | -0.10 at 20% |
| Psychopathic Mimic (coop=0.85, psych=0.90) | 10% | 0% | +0.04 (increases) |

Both predator strategies go extinct. Social immune response: institutional punishment, reputation decay, coalition defense, female mate choice against aggression.

---

## Publication Figures

| Figure | File | Description |
|--------|------|-------------|
| F1 | docs/figures/F1_hero_divergence.png | Trait means + Sn time series (dual panel, 95% CI) |
| F2 | docs/figures/F2_forest_plot.png | Forest plot: 35-trait paired displacement, ordered by Cohen's d |
| F3 | docs/figures/F3_selection_sheltering.png | Aggression mechanism: violence rate, skew, genotype decline |
| F8 | docs/figures/F8_squazzoni_fan_plot.png | Squazzoni N-Test: variance scaling + cooperation convergence |

All figures: 300 DPI, serif fonts, Wong (2011) colorblind-safe palette, no top/right spines.

---

## Data Files

| File | Location | Size | Contents |
|------|----------|------|----------|
| selection_matrix_full.csv | outputs/experiments/v2_paired_divergence/ | 16 MB | S + Sn for 35 traits, every tick, every seed |
| metrics_full.csv | outputs/experiments/v2_paired_divergence/ | 25 MB | ~130 metrics per tick |
| trait_displacement.csv | outputs/experiments/v2_paired_divergence/ | 44 KB | R_total per seed per scenario |
| paired_analysis.json | outputs/experiments/v2_paired_divergence/ | 20 KB | Full paired t-test tables + effect sizes |
| critic_validation_bundle.json | outputs/experiments/v2_paired_divergence/ | 44 KB | 5 checkpoint logs (years 100-500) |

---

## Calibration Baseline (AutoSIM Run 3)

9/9 anthropological targets satisfied (score = 1.0, 816 experiments). Held-out validation: 10 seeds x 200yr, mean score 0.934. See docs/validation.md for full report.
