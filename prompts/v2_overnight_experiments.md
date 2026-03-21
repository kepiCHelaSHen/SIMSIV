# SIMSIV v2 — OVERNIGHT EXPERIMENT BATTERY
# File: D:\EXPERIMENTS\SIM\prompts\v2_overnight_experiments.md
# Purpose: Run all experiments needed to make v2 findings publication quality
# Run after: EXIT 1 — science complete
# Output: D:\EXPERIMENTS\SIM\outputs\experiments\v2_battery\

================================================================================
CONTEXT — READ FIRST
================================================================================

Read these files before doing anything:
  1. D:\EXPERIMENTS\SIM\CHAIN_PROMPT.md
  2. D:\EXPERIMENTS\SIM\docs\v2_findings.md     — current findings to strengthen
  3. D:\EXPERIMENTS\SIM\models\clan\clan_simulation.py — the runner to use
  4. D:\EXPERIMENTS\SIM\prompts\v2_session_state.md

You are NOT building anything new.
You are running experiments using the existing ClanSimulation wrapper.
All output goes to: D:\EXPERIMENTS\SIM\outputs\experiments\v2_battery\
Create that directory if it does not exist.

================================================================================
THE CORE QUESTION THESE EXPERIMENTS ANSWER
================================================================================

Does between-group selection produce cooperation divergence across
institutional regimes? Is the hybrid pathway in seed 271 real or noise?

The current findings (n=3 seeds, 200yr) are underpowered.
These experiments increase statistical power and test robustness.

================================================================================
EXPERIMENT BATTERY — RUN ALL IN SEQUENCE
================================================================================

EXPERIMENT 1 — STATISTICAL POWER (most important)
  Goal: Increase from n=3 to n=6 seeds to test robustness of findings.
  Runtime estimate: ~15 minutes

  Run: FREE_COMPETITION vs STRONG_STATE
  Seeds: 42, 137, 271, 512, 999, 1337
  Years: 200
  Bands: 4 (2 Free + 2 State)
  Agents per band: 50
  Config: Use tuned ClanConfig from Turn 8
    raid_base_probability=0.50
    raid_scarcity_threshold=20.0
    base_interaction_rate=0.8

  Collect per seed at years 50, 100, 150, 200:
    - mean cooperation per regime (Free vs State)
    - between_group_selection_coeff
    - fst_prosocial_mean
    - inter_band_violence_rate
    - trade_volume_per_band

  Output: outputs/experiments/v2_battery/exp1_power.csv
  Also write: outputs/experiments/v2_battery/exp1_summary.md
    - Mean and std of cooperation divergence (Free - State) at year 200
    - How many seeds show Free > State vs State > Free
    - Is the hybrid pathway (emergent drift) visible in multiple seeds?

---

EXPERIMENT 2 — 2x2 FACTORIAL DESIGN (isolates the mechanism)
  Goal: Separate the effect of institutions from between-group selection.
  This is what Bowles will ask for first.
  Runtime estimate: ~20 minutes

  Four conditions:
    A: FREE_COMPETITION + raiding ENABLED   (current baseline)
    B: STRONG_STATE   + raiding ENABLED     (current baseline)
    C: FREE_COMPETITION + raiding DISABLED  (raid_base_probability=0.0)
    D: STRONG_STATE   + raiding DISABLED    (raid_base_probability=0.0)

  Seeds: 42, 137, 271 (3 seeds per condition = 12 total runs)
  Years: 200

  Key question: Does cooperation diverge MORE when raiding is enabled?
  If yes → between-group selection is causally driving the divergence.
  If no → institutions alone explain everything (supports North).

  Output: outputs/experiments/v2_battery/exp2_factorial.csv
  Also write: outputs/experiments/v2_battery/exp2_summary.md
    - 2x2 table: mean cooperation divergence per condition
    - Interaction effect: does raiding amplify or dampen institutional effects?

---

EXPERIMENT 3 — RAID INTENSITY SWEEP
  Goal: Test whether stronger between-group conflict shifts balance to Bowles.
  Runtime estimate: ~25 minutes

  Vary raid_base_probability: 0.1, 0.3, 0.5, 0.7
  Seeds: 42, 137, 271
  Years: 200
  Regime: FREE_COMPETITION only (4 bands, no institutional variation)

  Key question: Does higher raid intensity increase between_group_sel_coeff?
  Bowles (2006) predicts yes — more warfare = stronger group selection.

  Output: outputs/experiments/v2_battery/exp3_raid_sweep.csv
  Also write: outputs/experiments/v2_battery/exp3_summary.md
    - Plot cooperation divergence vs raid intensity
    - At what raid_base_probability does between_group_sel_coeff turn positive?

---

EXPERIMENT 4 — FISSION THRESHOLD SENSITIVITY
  Goal: Test whether founder effects drive the seed 271 hybrid pathway.
  Runtime estimate: ~20 minutes

  Vary fission_threshold: 75, 150, 300
  Seeds: 42, 137, 271
  Years: 200
  Regime: FREE_COMPETITION vs STRONG_STATE

  Key question: Does lower fission threshold (more fission = more founder
  effects) increase cooperation divergence in Free bands?
  If yes → founder effects are the primary driver of the hybrid pathway.

  Output: outputs/experiments/v2_battery/exp4_fission.csv
  Also write: outputs/experiments/v2_battery/exp4_summary.md
    - Does Fst increase faster with lower fission threshold?
    - Does emergent institutional drift appear more often with more fission?

---

EXPERIMENT 5 — MIGRATION RATE SWEEP
  Goal: Test the Fst erosion prediction from evolutionary theory.
  Runtime estimate: ~20 minutes

  Vary migration_rate_per_agent: 0.001, 0.005, 0.01, 0.05
  Seeds: 42, 137, 271
  Years: 200
  Regime: FREE_COMPETITION vs STRONG_STATE

  Key question: Does higher migration reduce between-group selection?
  Standard population genetics predicts: more gene flow = lower Fst =
  weaker between-group selection. Does our simulation reproduce this?

  Output: outputs/experiments/v2_battery/exp5_migration.csv
  Also write: outputs/experiments/v2_battery/exp5_summary.md
    - Fst at year 200 vs migration rate
    - Does cooperation divergence decrease with higher migration?

---

EXPERIMENT 6 — LONG RUN CONVERGENCE
  Goal: Is the cooperation divergence in seed 271 transient or persistent?
  Runtime estimate: ~20 minutes

  Run: FREE_COMPETITION vs STRONG_STATE
  Seeds: 42, 137, 271
  Years: 500
  Bands: 4 (2 Free + 2 State)

  Key question: Does Free > State cooperation persist at year 500
  or does it converge back? Transient = noise. Persistent = real signal.

  Output: outputs/experiments/v2_battery/exp6_longrun.csv
  Also write: outputs/experiments/v2_battery/exp6_summary.md
    - Cooperation trajectory from year 0 to 500
    - Is seed 271 divergence still present at year 500?
    - Does any seed flip direction between 200 and 500?

================================================================================
FINAL SYNTHESIS REPORT
================================================================================

After all 6 experiments complete, write:
  outputs/experiments/v2_battery/BATTERY_REPORT.md

This report must answer:

1. STATISTICAL POWER
   With n=6 seeds, is cooperation divergence consistent?
   What is the mean and std across all seeds?

2. CAUSAL MECHANISM
   From the 2x2 factorial: is between-group selection (raiding)
   the causal driver of cooperation divergence, or is it institutions alone?

3. PARAMETER ROBUSTNESS
   Are the findings robust across raid intensity and fission threshold?
   Or are they sensitive to specific parameter values?

4. THEORETICAL PREDICTION TESTS
   Does migration reduce Fst as population genetics predicts?
   Does raid intensity shift the balance toward Bowles/Gintis?

5. THE HYBRID PATHWAY
   Is the emergent institutional drift in Free bands (seed 271) robust?
   Does it appear in other seeds or parameter settings?
   What conditions produce it?

6. PAPER 2 READINESS
   Based on all experiments, what is the strongest defensible claim?
   What is the minimum set of findings that could be published?
   What experiments are still needed?

7. WHAT TO TELL BOWLES
   One paragraph. What is the single most interesting finding
   from this entire battery? Frame it for a scientist who has spent
   30 years on this question.

================================================================================
EXECUTION NOTES
================================================================================

- Use ClanSimulation from models.clan.clan_simulation
- Use the best_config.yaml from autosim/ as the base v1 Config
- Use the tuned ClanConfig from Turn 8 as the base clan config
- Write CSV output after each experiment — do not batch
- If any experiment crashes — log the error, skip, continue with next
- Total estimated runtime: 2-2.5 hours
- This is a read/run/report task — do not modify any code
================================================================================
