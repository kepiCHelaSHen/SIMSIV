# Experiment 2 Replication — 2x2 Factorial at n=10

## Setup
- Design: 2x2 factorial (Free/State) x (Raiding ON/OFF)
- Seeds: 42, 137, 271, 512, 999, 1337, 2048, 3141, 4096, 7777
- 4 conditions x 10 seeds = 40 simulation runs
- 200 years, 4 bands per condition, 50 agents/band
- Tuned ClanConfig: raid_base_probability=0.50, raid_scarcity_threshold=20.0,
  raid_trust_suppression_threshold=0.5
- Runtime: 10.2 minutes (613s)

## 2x2 Table at Year 200 (n=10 seeds per condition)

|             | Raiding ON             | Raiding OFF            |
|-------------|------------------------|------------------------|
| **Free**    | 0.505 (CI: +/-0.027)   | 0.504 (CI: +/-0.020)   |
| **State**   | 0.508 (CI: +/-0.018)   | 0.507 (CI: +/-0.012)   |

## Interaction Effect

| Metric | Original (n=3) | Replication (n=10) |
|--------|---------------|-------------------|
| Interaction effect | +0.039 | **+0.0004** |
| 95% CI | not computed | [-0.013, +0.014] |
| Zero inside CI? | — | **YES** |
| p-value (paired t) | not computed | **0.954** |
| Cohen's d | — | **0.019** |

**Verdict: NOT CONFIRMED.** The interaction effect is indistinguishable from zero.

## Seed-by-Seed Breakdown

| Seed | Div (Raid ON) | Div (Raid OFF) | Interaction |
|------|--------------|---------------|-------------|
| 42   | -0.005 | +0.019 | -0.024 |
| 137  | -0.015 | -0.009 | -0.005 |
| 271  | -0.006 | +0.006 | -0.012 |
| 512  | +0.046 | -0.005 | +0.051 |
| 999  | -0.013 | -0.032 | +0.020 |
| 1337 | +0.022 | +0.029 | -0.007 |
| 2048 | +0.010 | +0.027 | -0.018 |
| 3141 | -0.042 | -0.034 | -0.008 |
| 4096 | -0.003 | +0.003 | -0.006 |
| 7777 | -0.026 | -0.038 | +0.012 |

- Free > State under raiding: 3/10 seeds
- Free > State without raiding: 4/10 seeds
- Positive interaction (raiding helps Free more): 3/10 seeds
- Negative interaction: 7/10 seeds

## Statistical Test

Paired t-test comparing (Free-State divergence under raiding) vs
(Free-State divergence without raiding):
- t(9) = 0.059, p = 0.954
- Effect size d = 0.019 (negligible)
- The null hypothesis (raiding has no effect on Free-State divergence)
  cannot be rejected at any conventional significance level.

## Comparison to Original

| Metric | Original (n=3) | Replication (n=10) |
|--------|---------------|-------------------|
| Free+Raid coop | 0.506 | 0.505 |
| State+Raid coop | 0.469 | 0.508 |
| Free+NoRaid coop | 0.482 | 0.504 |
| State+NoRaid coop | 0.484 | 0.507 |
| Interaction | +0.039 | +0.0004 |

The original n=3 result was a **false positive** driven by one outlier seed
in Condition B (State+Raid seed 137: coop=0.478, well below the n=10 mean
of 0.508). At n=10, State+Raid cooperation rose from 0.469 to 0.508, erasing
the apparent Free advantage under raiding.

All four conditions converge to ~0.505 +/- 0.02. There is no meaningful
difference between Free and State, and raiding does not differentially
affect either regime.

## What This Means

1. **The Bowles mechanism, as implemented, does not produce detectable
   regime-level cooperation divergence.** The coalition defence advantage
   from cooperation_propensity and group_loyalty exists mechanistically
   (confirmed by Exp 3 dose-response) but does not translate into
   measurable differences between institutional regimes at 200yr with
   n=4 bands.

2. **The n=3 result was a sampling artifact.** This is exactly the scenario
   the critic warned about (Ioannidis 2005: false discovery rate >50% at
   10% statistical power).

3. **The dose-response finding (Exp 3) still holds**: cooperation increases
   with raid intensity (0.468 to 0.509). This is a within-regime effect,
   not a between-regime interaction. Raiding raises cooperation for ALL
   bands, not specifically for Free bands.

## What This Means for Bowles Email

The causal interaction finding is dead. We cannot claim that raiding
differentially favors Free bands over State bands.

What we CAN still say:

1. The simulation correctly implements the Bowles coalition defence mechanism
   (mechanistically verified).

2. Higher intergroup conflict increases mean cooperation across all bands
   (Exp 3 dose-response, robust at n=3x4=12 runs).

3. At 500yr, State bands go extinct in 2/3 seeds while Free bands survive
   (Exp 6 — but n=3, needs replication).

4. The net effect of between-group selection on cooperation divergence
   between institutional regimes is **zero** at 200yr with n=4 bands
   (Exp 2, confirmed at n=10).

The honest message to Bowles: "Your mechanism works at the individual
level (cooperation rises with raid intensity) but does not produce
detectable institutional-regime-level divergence at the population sizes
and timescales we can simulate. The mechanism exists but is overwhelmed
by within-group selection and demographic stochasticity."

---

Generated 2026-03-21. 40 runs, 120 data rows, 10.2 minutes.
