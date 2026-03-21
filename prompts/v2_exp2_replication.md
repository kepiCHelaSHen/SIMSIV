# SIMSIV v2 — EXPERIMENT 2 REPLICATION AT N=10
# File: D:\EXPERIMENTS\SIM\prompts\v2_exp2_replication.md
# Purpose: Replicate the 2x2 factorial at n=10 seeds to make the causal
#          finding publishable. This is the one experiment standing between
#          the current findings and a defensible email to Samuel Bowles.
# Runtime estimate: ~25-35 minutes
# Output: D:\EXPERIMENTS\SIM\outputs\experiments\v2_battery\exp2_replication\

================================================================================
CONTEXT
================================================================================

Read before doing anything:
  D:\EXPERIMENTS\SIM\outputs\experiments\v2_battery\BATTERY_REPORT.md
  D:\EXPERIMENTS\SIM\outputs\experiments\v2_battery\exp2_factorial.csv
  D:\EXPERIMENTS\SIM\docs\v2_findings.md
  D:\EXPERIMENTS\SIM\models\clan\clan_simulation.py

The current Experiment 2 (2x2 factorial) used n=3 seeds per condition.
It found an interaction effect of +0.039 (raiding x institutions).
This is the key causal finding — Bowles mechanism is operative.

But n=3 is underpowered. This replication runs n=10 seeds per condition.
40 total simulation runs. If the +0.039 interaction survives at n=10
with a narrow confidence interval — the finding is publishable.

DO NOT build anything. DO NOT modify any code.
Run simulations. Collect data. Write the report.

================================================================================
THE EXPERIMENT
================================================================================

DESIGN: 2x2 factorial
  Factor 1: Institutions (FREE_COMPETITION vs STRONG_STATE)
  Factor 2: Raiding (ENABLED vs DISABLED)

4 conditions x 10 seeds = 40 simulation runs.

CONDITIONS:

  CONDITION A — Free + Raiding ON:
    law_strength = 0.0 (emergent drift active)
    property_rights_strength = 0.0
    raid_base_probability = 0.50
    Use tuned ClanConfig from Turn 8

  CONDITION B — State + Raiding ON:
    law_strength = 0.8
    property_rights_strength = 0.8
    raid_base_probability = 0.50
    Use tuned ClanConfig from Turn 8

  CONDITION C — Free + Raiding OFF:
    law_strength = 0.0
    property_rights_strength = 0.0
    raid_base_probability = 0.0 (raiding disabled)

  CONDITION D — State + Raiding OFF:
    law_strength = 0.8
    property_rights_strength = 0.8
    raid_base_probability = 0.0 (raiding disabled)

SEEDS: 42, 137, 271, 512, 999, 1337, 2048, 3141, 4096, 7777
YEARS: 200
BANDS: 4 (2 per regime, same as original Exp 2)
AGENTS PER BAND: 50

COLLECT AT YEARS 100, 150, 200:
  - mean cooperation_propensity per regime (Free bands average, State bands average)
  - between_group_selection_coeff
  - fst_prosocial_mean
  - inter_band_violence_rate
  - trade_volume_per_band
  - band count (to detect extinctions)

================================================================================
OUTPUT
================================================================================

Create directory: D:\EXPERIMENTS\SIM\outputs\experiments\v2_battery\exp2_replication\

Write after every 10 runs (do not wait until the end):
  exp2_replication_partial.csv — running results so far

After all 40 runs complete write:
  exp2_replication_full.csv — all 40 runs

Then write:
  exp2_replication_report.md — full analysis

The report must contain:

  ## 2x2 TABLE AT YEAR 200 (n=10 seeds per condition)
  Mean cooperation per condition with 95% CI:
    |             | Raiding ON        | Raiding OFF       |
    |-------------|-------------------|-------------------|
    | Free        | X.XXX (CI: ±0.XX) | X.XXX (CI: ±0.XX) |
    | State       | X.XXX (CI: ±0.XX) | X.XXX (CI: ±0.XX) |

  ## INTERACTION EFFECT
  Original (n=3): +0.039
  Replication (n=10): [value] (95% CI: [low, high])
  Does zero fall inside the CI? [YES/NO]
  Verdict: [CONFIRMED / NOT CONFIRMED / INCONCLUSIVE]

  ## SEED-BY-SEED BREAKDOWN
  For each of the 10 seeds, report cooperation divergence (Free - State)
  under Raiding ON vs Raiding OFF.
  How many seeds show Free > State under raiding? [X/10]
  How many seeds show Free > State without raiding? [X/10]

  ## STATISTICAL TEST
  Run a simple t-test or Mann-Whitney U comparing:
    (Free_RaidON - State_RaidON) vs (Free_RaidOFF - State_RaidOFF)
  Report: test statistic, p-value, effect size (Cohen's d)
  p < 0.05 with consistent direction = publishable finding

  ## COMPARISON TO ORIGINAL
  How does n=10 compare to n=3?
  Did the effect size change? Did the direction change?
  Is the finding more or less convincing at n=10?

  ## VERDICT FOR BOWLES EMAIL
  One paragraph. No hedging.
  Can we defensibly claim the Bowles mechanism is causally operative?
  What is the exact sentence we should use in the email?

================================================================================
AFTER THE REPORT
================================================================================

Update D:\EXPERIMENTS\SIM\docs\v2_findings.md:
  Replace the Experiment 2 section with the n=10 results.
  Update the "strongest defensible claims" section accordingly.
  Update the "what to tell Bowles" section with the n=10 finding.

Commit everything:
  git add outputs/experiments/v2_battery/exp2_replication/
  git add docs/v2_findings.md
  git commit -m "Exp 2 replication n=10: causal finding [CONFIRMED/NOT CONFIRMED]"
  git tag v2-exp2-n10-final

================================================================================
IF THE FINDING DOES NOT REPLICATE
================================================================================

If the interaction effect at n=10 is NOT statistically significant
or reverses direction:

  1. Do NOT update docs/v2_findings.md with a false positive
  2. Write exp2_replication_report.md honestly — the finding did not replicate
  3. Write a section: "What this means for Bowles email"
     - The mechanism is suggestive but not statistically robust at n=10
     - What additional experiments would be needed
     - Whether the other findings (Exp 3 dose-response, Exp 6 extinction) are
       sufficient to warrant contact with Bowles anyway

  4. Commit with message: "Exp 2 n=10 replication: finding NOT confirmed"

Science that doesn't replicate is still science.
Report it honestly. Do not hide it.

================================================================================
DONE
================================================================================

When complete print a one-line summary:

"Exp 2 n=10 complete: interaction effect = [value] (p=[value]).
 Finding [CONFIRMED/NOT CONFIRMED]. See exp2_replication_report.md."
