# SIMSIV — Post-Autosim Task List
# Created: 2026-03-14
# Updated: 2026-03-15
# Status: DD27 COMPLETE. Autosim 500-experiment run FIRING NOW.

================================================================================
COMPLETED ✓
================================================================================

✓ Autosim Mode A built (autosim/ directory)
✓ Autosim improvements: simulated annealing, --seeds/--years args, expanded tunables
✓ DD27 complete — 35 heritable traits (scientific ceiling)
  - physical_strength, endurance, group_loyalty, outgroup_tolerance
  - future_orientation, conscientiousness, psychopathy_tendency
  - anxiety_baseline, paternal_investment_preference
  - 35×35 correlation matrix PSD-verified
  - All 4 special validation tests passing
✓ README.md updated (35 traits, DD27 complete)
✓ world_architecture.md v3.0 updated (all 35 traits documented)
✓ STATUS.md updated

================================================================================
STEP 1 — AFTER 500-EXPERIMENT AUTOSIM RUN FINISHES
================================================================================

Run command (ALREADY FIRED):
  python -m autosim.runner --experiments 500 --seeds 2 --years 150

When complete:

1. READ RESULTS
   python -c "
   import json
   entries = [json.loads(l) for l in open('autosim/journal.jsonl') if 'experiment_id' in l]
   accepts = [e for e in entries if 'ACCEPT' in e.get('action','')]
   best = max(entries, key=lambda e: e['score'])
   print(f'Total: {len(entries)}, Accepted: {len(accepts)}')
   print(f'Best score: {best[\"score\"]:.4f} (exp {best[\"experiment_id\"]})')
   print('Per-metric scores (best):')
   for k,v in sorted(best['per_metric_scores'].items()):
       print(f'  {k}: {v:.4f}')
   "

2. COMMIT BEST CONFIG
   git add autosim/journal.jsonl autosim/best_config.yaml
   git commit -m "Autosim 500-experiment run complete — best score: X.XXX"
   git push

3. TAG v1.0
   git tag -a v1.0-band-simulator -m "Band simulator complete — DD01-DD27, 35 traits, autosim calibrated"
   git push origin v1.0-band-simulator

================================================================================
STEP 2 — APPLY BEST CONFIG
================================================================================

   claude --dangerously-skip-permissions -p "Read autosim/best_config.yaml and
   config.py. Update the default values in config.py to match the best parameters
   found. Only update the specific fields listed in best_config.yaml. Run smoke
   tests to verify. Git commit -m 'Apply autosim best_config to defaults'."

Then run definitive 500yr validation:
   python main.py --years 500 --population 500 --seed 42
   python main.py --years 500 --population 500 --seed 123
   python main.py --years 500 --population 500 --seed 999

================================================================================
STEP 3 — STALE DOCS CLEANUP
================================================================================

   claude --dangerously-skip-permissions -p "Read CLAUDE.md, docs/AUTOSIM.md,
   CHAIN_PROMPT.md, sandbox/explore.py, models/agent.py.

   1. CLAUDE.md — rewrite: 35 heritable traits (list all), 5 beliefs, 4 skills,
      9 engines with correct tick order, dashboard built, autosim complete with
      simulated annealing.

   2. docs/AUTOSIM.md — update Status to 'COMPLETE — 500 experiments, best score X'.
      Update runtime to ~45 seconds/experiment. Update journal path.

   3. CHAIN_PROMPT.md — update header date, all 35 traits in agent model section,
      add DD27 to deep dive list, update file tree.

   4. sandbox/explore.py — verify agent_df() includes all new DD27 fields:
      physical_strength, endurance, group_loyalty, outgroup_tolerance,
      future_orientation, conscientiousness, psychopathy_tendency,
      anxiety_baseline, paternal_investment_preference.

   Git commit -m 'Docs cleanup — CLAUDE.md, AUTOSIM.md, CHAIN_PROMPT.md updated for DD27'"

================================================================================
STEP 4 — DASHBOARD UPGRADE
================================================================================

   claude --dangerously-skip-permissions -p "Read dashboard/app.py completely.
   Add four improvements:

   1. TRAIT VARIANCE BANDS — Trait Evolution tab: add shaded ±1 std bands
      around mean lines for aggression, cooperation, intelligence, risk_tolerance.

   2. MULTI-RUN RESEARCH MODE — sidebar Research Mode toggle, seeds_count slider
      (3-20). When enabled, run N seeds, show mean + confidence band on all charts.

   3. NETWORK VISUALIZATION TAB — Plotly network graph. Top 150 agents by
      prestige_score as nodes. Color = faction_id. Size = prestige_score.
      Edges = trust > 0.5. Edge width = trust. Within neighborhood tier only.

   4. AGENT BIOGRAPHY TAB — dropdown to select any agent. Display life story
      as readable text: born, parents, bonds, children, medical events, death.
      Pull from events log filtered by agent_id.

   Git commit when done."

================================================================================
STEP 5 — SCIENTIFIC INTEGRITY FIXES
================================================================================

--- 5A. DEVELOPMENTAL PLASTICITY AUDIT ---
After calibrated 500yr runs, check heritability_realized metric from DD16.
Target: 0.6-0.8. If < 0.5, scale developmental cap by population trait std.

--- 5B. FACTION IDEOLOGY FIX ---
   claude --dangerously-skip-permissions -p "Read models/society.py
   detect_factions method and models/agent.py belief fields. Modify faction
   detection: faction_affinity = trust * (1 - belief_distance * 0.3) where
   belief_distance = mean(abs differences across 5 belief dimensions).
   Add config param belief_faction_weight=0.3. Git commit."

--- 5C. AGGRESSION VIABILITY TEST ---
Add HOSTILE_ENVIRONMENT scenario to experiments/scenarios.py:
  resource_abundance=0.4, initial violence_acceptability=+0.5, law=0.0
Run 500yr, 5 seeds. Aggression should stabilize > 0.5 in this scenario.

--- 5D. INSTITUTIONAL COLLAPSE TEST ---
Run 500yr EMERGENT_INSTITUTIONS, watch for law_strength collapse events.
If monotonically increasing, add institutional corruption mechanism.

================================================================================
STEP 6 — PERFORMANCE AUDIT
================================================================================

Profile O(N²) bottlenecks before v2 work:

   claude --dangerously-skip-permissions -p "Add cProfile timing to main.py
   for a 500-agent 200-year run. Report top 5 slowest operations. Vectorize
   engines/resources.py Phase 2 competitive weight calculation using NumPy
   arrays instead of for-loops. Benchmark before/after. Git commit."

Target: 500 agents / 200 years < 60 seconds.

================================================================================
STEP 7 — RESEARCH EXPERIMENTS QUEUE
================================================================================

With calibrated 35-trait model, run these 500yr experiments for YouTube
video and documentation. Each 10 seeds = ~2 hours per scenario.

Priority:
1. DEFINITIVE_BASELINE — FREE_COMPETITION, 500yr, 10 seeds
2. MONOGAMY_VS_POLYGYNY — 500yr, 10 seeds each, head-to-head
3. EMERGENT_INSTITUTIONS_LONG — 500yr, 5 seeds (watch for collapse)
4. HOSTILE_ENVIRONMENT — 500yr, 5 seeds (aggression viability test)
5. STRONG_STATE_LONG — 500yr, 5 seeds (trait substitution over full timescale)

Watch specifically for new DD27 trait dynamics:
- Does psychopathy_tendency stay low (0.2-0.35) as expected?
- Does future_orientation rise in STRONG_STATE (institutions select for patience)?
- Does group_loyalty diverge between cooperative vs aggressive scenarios?
- Does paternal_investment_preference show sex-differential patterns?

================================================================================
STEP 8 — VALIDATION DOCUMENTATION
================================================================================

Write docs/validation.md:
- Calibration methodology (autosim Mode A, 500 experiments, simulated annealing)
- Per-metric before/after scores
- Ethnographic comparisons
- Known deviations and reasons
- Limitations section
- Suggested citations for all h² values and demographic targets

================================================================================
STEP 9 — FOLLOW-UP AUTOSIM (HIGH FIDELITY)
================================================================================

After applying best_config from 500-experiment screening run:

   python -m autosim.runner --experiments 200 --seeds 5 --years 300

This is the definitive calibration — 200 experiments at full fidelity
starting from the best parameters the screening run found.

================================================================================
STEP 10 — V2 PLANNING
================================================================================

Write docs/v2_clan_simulator.md covering:
- Temporal scale: how to bridge 1yr band ticks → 10yr clan ticks
- Band fingerprint adequacy (consider adding variance metrics)
- Inter-band mechanics: trade, raid, intermarriage, migration
- Band → clan transition thresholds (specific numeric criteria)
- Cultural distance metric (belief vector comparison)
- outgroup_tolerance trait integration into inter-band dynamics (new in DD27)
- Player interaction design
- Performance target: 1000 bands in under 5 minutes

================================================================================
PRIORITY SUMMARY
================================================================================

  RUNNING NOW:
  → Autosim 500-experiment run (--seeds 2 --years 150, ~6 hours)

  IMMEDIATELY WHEN AUTOSIM FINISHES:
  □ Read results + commit best config
  □ Tag v1.0-band-simulator
  □ Apply best_config to config.py defaults

  THIS WEEK:
  □ Stale docs cleanup (CLAUDE.md, AUTOSIM.md, CHAIN_PROMPT.md) — Step 3
  □ Dashboard upgrade (4 improvements) — Step 4
  □ Faction ideology fix — Step 5B
  □ Performance audit + vectorization — Step 6

  BEFORE V2:
  □ Developmental plasticity audit — Step 5A
  □ 500yr research experiments — Step 7
  □ Write validation.md — Step 8
  □ High fidelity autosim (200 exp × 5 seeds × 300yr) — Step 9
  □ Write v2_clan_simulator.md — Step 10

================================================================================
END OF DOCUMENT
================================================================================
