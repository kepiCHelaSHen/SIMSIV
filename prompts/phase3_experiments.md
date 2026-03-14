# SIMSIV — PROMPT: PHASE 3 — EXPERIMENT FRAMEWORK AND VISUALIZATION
# File: D:\EXPERIMENTS\SIM\prompts\phase3_experiments.md
# Use: Paste this entire prompt to Claude to execute Phase 3

================================================================================
CONTEXT INJECTION — READ FIRST
================================================================================

You are iterating SIMSIV — a working Python social simulation sandbox.

Before doing ANYTHING, read ALL of the following:
  1. D:\EXPERIMENTS\SIM\CHAIN_PROMPT.md
  2. D:\EXPERIMENTS\SIM\devlog\DEV_LOG.md
  3. D:\EXPERIMENTS\SIM\docs\rules_spec.md
  4. D:\EXPERIMENTS\SIM\docs\assumptions.md
  5. D:\EXPERIMENTS\SIM\main.py
  6. D:\EXPERIMENTS\SIM\config.py
  7. D:\EXPERIMENTS\SIM\metrics\collectors.py
  8. D:\EXPERIMENTS\SIM\visualizations\plots.py

The skeleton is working. Now build the experiment layer on top of it.
Do NOT modify working engine code unless a bug is discovered.

================================================================================
PHASE 3 TASK: EXPERIMENT FRAMEWORK AND VISUALIZATION
================================================================================

--------------------------------------------------------------------------------
A. experiments/scenarios.py
--------------------------------------------------------------------------------

Define at minimum 8 named scenario configs as Python dicts or dataclasses.
Each scenario is a full config override on top of the baseline defaults.

Required scenarios:
  1. FREE_COMPETITION
     Baseline: no norms, unrestricted mating, average resources
     Purpose: null hypothesis — everything else is compared to this

  2. ENFORCED_MONOGAMY
     monogamy_enforced=True, max_mates_per_male=1, law_strength=0.7
     Purpose: test whether monogamy reduces unmated male violence and
              increases child survival

  3. ELITE_POLYGYNY
     polygyny_allowed=True, elite_privilege_multiplier=3.0,
     max_mates_per_male=5 for top quintile of status
     Purpose: test reproductive skew, unmated male effects, instability

  4. HIGH_FEMALE_CHOICE
     female_choice_strength=0.95, male_competition_intensity=0.9
     Purpose: test whether strong female choice drives male status arms race

  5. RESOURCE_ABUNDANCE
     resource_abundance=2.5, resource_volatility=0.1
     Purpose: test how abundance changes mating, cooperation, violence

  6. RESOURCE_SCARCITY
     resource_abundance=0.4, resource_volatility=0.4,
     scarcity_event_probability=0.15
     Purpose: test how scarcity drives inequality and instability

  7. HIGH_VIOLENCE_COST
     violence_cost_multiplier=3.0, mortality_base=0.04
     Purpose: test whether high violence cost selects for cooperation norms

  8. STRONG_PAIR_BONDING
     pair_bond_strength=0.9, pair_bond_dissolution_rate=0.02,
     child_dependency_years=10, paternal_investment_weight=0.8
     Purpose: test whether strong bonds improve child survival and
              reduce conflict

--------------------------------------------------------------------------------
B. experiments/runner.py
--------------------------------------------------------------------------------

ExperimentRunner class:
  - run_scenario(scenario_name, seeds=[42,43,44,45,46]) -> results dict
  - run_all_scenarios(seeds=[42,43,44,45,46]) -> full results dict
  - run_parameter_sweep(param_name, values, seeds=[42,43,44]) -> sweep results
  - compare_to_baseline(results, baseline_results) -> comparison dict
  - All results saved to outputs/reports/[timestamp]/

Parameter sweep targets (v1):
  - female_choice_strength: [0.1, 0.3, 0.5, 0.7, 0.9]
  - violence_cost_multiplier: [0.5, 1.0, 2.0, 4.0]
  - pair_bond_strength: [0.1, 0.3, 0.5, 0.7, 0.9]
  - resource_abundance: [0.3, 0.6, 1.0, 1.5, 2.5]
  - elite_privilege_multiplier: [1.0, 1.5, 2.0, 3.0, 5.0]

--------------------------------------------------------------------------------
C. experiments/summarizer.py
--------------------------------------------------------------------------------

NarrativeSummarizer class:
  - generate_run_summary(metrics_df, config, events_df) -> str
    Produces a paragraph-level narrative:
      - What happened in broad strokes
      - Key turning points by year range
      - Which variables appeared to drive the main outcomes
      - Any emergent or surprising patterns
      - Explicit warnings if results look like artifacts of simplification

  - generate_scenario_comparison(all_results) -> str
    Produces a comparative narrative across all scenarios

  - flag_instability(metrics_df) -> list of warning strings
    Warns when: population collapses, all male violence, model blows up,
    metrics are suspiciously flat, results are highly seed-sensitive

  - save_summary(text, path)

--------------------------------------------------------------------------------
D. visualizations/dashboard.py
--------------------------------------------------------------------------------

Build multi-panel comparison charts for cross-scenario analysis.

  - plot_scenario_comparison_panel(all_results, output_path)
    8-panel figure: one panel per metric, one line per scenario
    Metrics: population, resource_gini, violence_rate, unmated_male_pct,
             child_survival, reproductive_skew, pair_bond_stability,
             avg_lifespan

  - plot_parameter_sweep_heatmap(sweep_results, param_name, output_path)
    Heatmap: x=param values, y=metrics, color=normalized outcome

  - plot_seed_variance_bands(scenario_results, output_path)
    Shows mean + std dev bands across seeds for each scenario
    Visually shows which results are robust vs seed-sensitive

  - plot_event_timeline(events_df, output_path)
    Timeline of major events: conflict spikes, population drops,
    mating system shifts, scarcity events

--------------------------------------------------------------------------------
E. Composite Indices
--------------------------------------------------------------------------------

Add to metrics/collectors.py:

  civilization_stability_index (CSI):
    = weighted average of:
        (1 - violence_rate) * 0.3
        child_survival_rate * 0.25
        (1 - resource_gini) * 0.2
        pair_bond_stability * 0.15
        population_growth_rate * 0.1
    Range: 0.0 (collapse) to 1.0 (stable)
    Warn in docstring: this is a constructed index, not a real measurement

  mating_inequality_index (MII):
    = gini(offspring_count_per_male)
    Range: 0.0 (perfectly equal) to 1.0 (one male reproduces all)

  social_cohesion_index (SCI):
    = weighted average of:
        avg_social_trust * 0.4
        cooperation_event_rate * 0.35
        (1 - conflict_rate) * 0.25
    Range: 0.0 to 1.0

--------------------------------------------------------------------------------
F. Safeguards Against Overinterpretation
--------------------------------------------------------------------------------

Add to summarizer.py: SimIntegrityChecker class
  - check_population_stability() — warn if < 50 agents survive
  - check_seed_sensitivity() — warn if std_dev > 20% of mean across seeds
  - check_runaway_inequality() — warn if gini > 0.95
  - check_model_collapse() — warn if population hits 0
  - add_boilerplate_disclaimer() — appends standard disclaimer to all reports:
    "SIMSIV is a stylized model. Results reflect the consequences of the
     implemented rules, not claims about human societies. All metrics are
     artifacts of simplification. Do not over-interpret."

================================================================================
OUTPUT REQUIREMENTS
================================================================================

outputs/reports/[timestamp]/
  ├── scenario_comparison.png
  ├── parameter_sweep_[param].png  (one per sweep)
  ├── seed_variance_[scenario].png (one per scenario)
  ├── event_timeline.png
  ├── scenario_report.md           (full narrative comparison)
  ├── scenario_summaries/
  │   ├── FREE_COMPETITION.md
  │   ├── ENFORCED_MONOGAMY.md
  │   └── ... (one per scenario)
  └── integrity_warnings.md        (all model warnings)

================================================================================
AFTER IMPLEMENTATION
================================================================================

Update devlog: D:\EXPERIMENTS\SIM\devlog\DEV_LOG.md
Copy scenario_comparison.png to: D:\EXPERIMENTS\SIM\artifacts\charts\
Copy scenario_report.md to: D:\EXPERIMENTS\SIM\artifacts\design\
