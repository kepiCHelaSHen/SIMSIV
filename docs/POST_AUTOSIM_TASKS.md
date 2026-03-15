# SIMSIV — Post-Autosim Task List
# Created: 2026-03-14
# Status: Autosim Mode A running (100 experiments, ~2hr total)
# Purpose: Everything to do after autosim finishes and best_config.yaml is ready

================================================================================
STEP 1 — IMMEDIATELY AFTER AUTOSIM FINISHES
================================================================================

These three things before anything else:

1. READ THE RESULTS
   python -c "
   import json
   with open('autosim/journal.jsonl') as f:
       entries = [json.loads(line) for line in f]
   accepts = [e for e in entries if e['action'] == 'ACCEPT']
   best = max(entries, key=lambda e: e['score'])
   print(f'Total experiments: {len(entries)}')
   print(f'Accepted: {len(accepts)} ({100*len(accepts)//len(entries)}%)')
   print(f'Baseline score: {entries[0][\"score\"]:.4f}')
   print(f'Best score: {best[\"score\"]:.4f} (experiment {best[\"experiment_id\"]})')
   print(f'Best params: {best[\"params\"]}')
   print()
   print('Per-metric scores (best run):')
   for k, v in best['per_metric_scores'].items():
       print(f'  {k}: {v:.4f}')
   "

2. COMMIT THE BEST CONFIG
   git add autosim/journal.jsonl autosim/best_config.yaml
   git commit -m "Autosim Mode A complete — 100 experiments, best score: X.XXX"
   git push

3. TAG v1.0
   git tag -a v1.0-band-simulator -m "Band simulator complete — DD01-DD26, autosim calibrated"
   git push origin v1.0-band-simulator

================================================================================
STEP 2 — APPLY BEST CONFIG
================================================================================

After autosim, update config.py defaults with best_config.yaml values:

   claude --dangerously-skip-permissions -p "Read autosim/best_config.yaml and
   config.py. Update the default values in config.py to match the best parameters
   found by autosim. Only update the specific fields listed in best_config.yaml.
   Do not change any other parameters. Run the smoke tests to verify. Git commit."

Then run a definitive 500yr validation run with the calibrated config:

   python main.py --years 500 --population 500 --seed 42
   python main.py --years 500 --population 500 --seed 123
   python main.py --years 500 --population 500 --seed 999

Compare the 500yr results against the calibration targets.

================================================================================
STEP 3 — STALE DOCS CLEANUP (fire as one CLI session)
================================================================================

Four documents need updating:

   claude --dangerously-skip-permissions -p "Read CLAUDE.md, docs/AUTOSIM.md,
   CHAIN_PROMPT.md, sandbox/explore.py, and models/agent.py. Fix:

   1. CLAUDE.md — rewrite to reflect current state: 26 heritable traits (list all),
      5 beliefs, 4 skills, 9 engines with correct tick order (steps 1-12 including
      6.3 migration and 6.5 pathology), Streamlit dashboard is built and running,
      autosim is complete.

   2. docs/AUTOSIM.md — update Status from 'Not yet implemented' to 'COMPLETE —
      Mode A finished, 100 experiments logged'. Update runtime to '~60-90 seconds
      per experiment'. Update journal path to autosim/journal.jsonl.

   3. CHAIN_PROMPT.md — update header date. Fix Q5 to say 26 traits. Update
      non-heritable fields to include beliefs (5), skills (4), neighborhood_ids,
      migration fields, epigenetic fields.

   4. sandbox/explore.py — fix agent_df(): change a.agent_id to a.id. Add fields:
      life_stage, trauma_score, faction_id, foraging_skill, social_skill,
      hierarchy_belief, cooperation_norm.

   Git commit -m 'Docs cleanup — CLAUDE.md, AUTOSIM.md, CHAIN_PROMPT.md, sandbox fix'
   Git push."

================================================================================
STEP 4 — DASHBOARD UPGRADE
================================================================================

Three improvements identified from GPT/Grok feedback and dashboard review:

   claude --dangerously-skip-permissions -p "Read dashboard/app.py completely.
   Add three improvements:

   1. TRAIT VARIANCE BANDS — in the Trait Evolution tab, add shaded ±1 std
      deviation bands around the mean lines for aggression, cooperation,
      intelligence, and risk_tolerance using the _std metrics already in the
      data. Use semi-transparent Plotly fill_between.

   2. MULTI-RUN RESEARCH MODE — add a 'Research Mode' toggle in the sidebar
      with a seeds_count slider (3-20). When enabled and Run is clicked, run N
      simulations with different seeds, compute mean and std per year across all
      seeds, display mean line + shaded confidence band on all charts. Single
      run remains the default.

   3. NETWORK VISUALIZATION TAB — add a Social Network tab using Plotly network
      graph. Show top 150 agents by prestige_score as nodes. Node color =
      faction_id (categorical colors). Node size = prestige_score. Edges =
      reputation_ledger entries with trust > 0.5. Edge width = trust value.
      Only show edges within neighborhood_ids (proximity tier). Renders after
      simulation completes from final agent state.

   4. AGENT BIOGRAPHY TAB — add a Biography tab. After a run completes, show a
      dropdown to select any agent by ID. Display their full life story as
      readable text: born year X, parents Y and Z, bonded at age A, children B
      and C, medical events, faction history, cause of death. Pull from the
      events log filtered by agent_id.

   Keep all existing functionality. Git commit when done."

================================================================================
STEP 5 — SCIENTIFIC INTEGRITY FIXES (from external feedback)
================================================================================

These address the substantive research concerns raised in the architecture review:

--- 5A. DEVELOPMENTAL PLASTICITY AUDIT ---
Concern: ±0.10 trait modification may be too large relative to genetic variance
         (population σ~0.09), effectively overriding genetic selection.

Check: after calibrated runs, examine heritability_realized metric from DD16.
Target: adult phenotype/genotype correlation should be 0.6-0.8.

If heritability_realized < 0.5, run this fix:
   claude --dangerously-skip-permissions -p "Read engines/reproduction.py and
   engines/mortality.py (maturation section). The developmental plasticity
   modifications (±0.10 per trait) may be too large relative to genetic variance.
   Change the modification cap from a fixed 0.10 to a dynamic cap of
   0.5 * population_trait_std for each trait. This scales plasticity to
   the actual genetic variance in the population. Test that heritability_realized
   metric improves toward 0.6-0.8 range. Git commit."

--- 5B. FACTION FORMATION: TOPOLOGY + IDEOLOGY ---
Concern: factions form from trust-network topology only. Two ideologically
         opposed agents can be in the same faction if their trust networks connect.

Fix:
   claude --dangerously-skip-permissions -p "Read models/society.py (detect_factions
   method) and models/agent.py (belief fields). Modify faction detection to use
   a combined score: faction_affinity = trust * (1 - belief_distance * 0.3)
   where belief_distance = mean(abs(a.belief - b.belief) for each belief dimension).
   This means ideologically distant agents need higher trust to be in the same
   faction. belief_distance weight 0.3 is configurable (belief_faction_weight).
   Add 1 config param, test that ideologically divergent bands develop distinct
   factions. Git commit."

--- 5C. AGGRESSION VIABILITY IN HOSTILE ENVIRONMENTS ---
Concern: five simultaneous penalties may prevent warrior-dominant societies
         from emerging even when historically appropriate.

Action (experiment, not code change):
   Run dedicated experiment — HOSTILE_ENVIRONMENT scenario:
   - HIGH resource scarcity (resource_abundance=0.4)
   - HIGH violence_acceptability initial belief (start at +0.5)
   - LOW institutional strength (law=0.0)
   - 500 years

   Expected: aggression should stabilize or rise above 0.5 in this scenario.
   If aggression still declines to <0.35 even in this extreme scenario,
   the selection pressure is overdetermined and needs recalibration.

   Add HOSTILE_ENVIRONMENT to experiments/scenarios.py.

--- 5D. INSTITUTIONAL COLLAPSE CYCLES ---
Concern: strong self-reinforcing institutional loop (cooperation → institutions
         → reduced violence → stronger cooperation) may prevent collapse.

Action (experiment):
   Run 500yr EMERGENT_INSTITUTIONS and watch for:
   - law_strength collapse events (drops >0.2 in 10yr)
   - faction_count spikes (institutional crisis → fragmentation)
   - institutions_emerged metric cycling up and down

   If law_strength monotonically increases and never falls, add an
   'institutional corruption' mechanism: law_strength decays faster when
   dominant faction has very high dominance (authoritarian capture).

================================================================================
STEP 6 — PERFORMANCE AUDIT
================================================================================

Before v2 work begins, profile the O(N²) bottlenecks:

   claude --dangerously-skip-permissions -p "Add cProfile timing to main.py for
   a standard 500-agent 200-year run. Profile which engine takes the most time
   per tick. Report the top 5 slowest operations. Then implement the single
   most impactful vectorization: in engines/resources.py Phase 2, replace the
   for-loop competitive weight calculation with NumPy array operations.
   Benchmark before and after. Git commit with timing results in commit message."

Target: 500 agents / 200 years should run in under 60 seconds after optimization.
This is the threshold for comfortable autosim experiments and multi-seed research runs.

================================================================================
STEP 7 — RESEARCH EXPERIMENTS QUEUE
================================================================================

Run these experiments with the calibrated 500yr config. Each generates a
named output in outputs/runs/ for the YouTube video and future documentation.

Priority order:

1. DEFINITIVE_BASELINE — 500yr, 10 seeds, FREE_COMPETITION
   Purpose: establish the null hypothesis with full statistical rigor

2. MONOGAMY_VS_POLYGYNY — 500yr, 10 seeds each, ENFORCED_MONOGAMY vs ELITE_POLYGYNY
   Purpose: the headline finding with proper variance bands

3. EMERGENT_INSTITUTIONS_LONG — 500yr, 5 seeds, EMERGENT_INSTITUTIONS
   Purpose: watch for institutional collapse cycles

4. HOSTILE_ENVIRONMENT — 500yr, 5 seeds, new scenario (see 5C above)
   Purpose: test whether warrior societies can emerge

5. STRONG_STATE_LONG — 500yr, 5 seeds, STRONG_STATE
   Purpose: watch trait substitution over full genetic timescale

Run all experiments with:
   python experiments/runner.py --scenario X --years 500 --seeds 10

================================================================================
STEP 8 — VALIDATION DOCUMENTATION
================================================================================

Write a proper calibration and validation document for the research notes:

File: docs/validation.md

Contents:
- Calibration methodology (autosim Mode A, 100 experiments, hill-climbing)
- Per-metric calibration results (before/after autosim scores)
- Ethnographic comparisons (!Kung violence, pre-industrial Gini, TFR targets)
- Known deviations from targets and reasons
- Limitations section (model-dependent, scenario-dependent findings)
- Suggested citations for h² values, demographic targets

This document makes the scientific claims in README.md defensible.

================================================================================
STEP 9 — V2 PLANNING
================================================================================

When all above is done, write the clan simulator design document:

File: docs/v2_clan_simulator.md

Cover:
- Temporal scale: band ticks at 1yr, clan ticks at 10yr — how to bridge
- Band fingerprint adequacy: does 15 values capture enough state?
- Inter-band interaction mechanics: trade, raid, intermarriage, migration
- Band → clan transition thresholds (specific numeric criteria)
- Cultural distance metric for belief vector comparison
- Clan simulator performance target: 1000 bands running in under 5 minutes
- Player interaction design: what does the player control at clan level?

================================================================================
PRIORITY SUMMARY
================================================================================

  IMMEDIATE (today/tonight):
  ✓ Read autosim results
  ✓ Commit best config
  ✓ Tag v1.0
  ✓ Fix stale docs (CLAUDE.md, AUTOSIM.md, CHAIN_PROMPT.md, sandbox)

  THIS WEEK:
  □ Apply best config to config.py defaults
  □ Dashboard upgrade (variance bands + multi-run + network viz + biography)
  □ Faction formation ideology fix (5B)
  □ Performance audit and vectorization

  BEFORE V2:
  □ Developmental plasticity audit (5A)
  □ Run 500yr research experiments (Step 7)
  □ Write validation.md (Step 8)
  □ Run hostile environment test (5C)
  □ Run institutional collapse test (5D)
  □ Write v2 clan simulator design doc (Step 9)

================================================================================
END OF DOCUMENT
================================================================================
