# SIMSIV — DEVELOPMENT LOG (Phase E onwards)
# Started: 2026-03-15
# Previous history: devlog/archive/DEV_LOG_phase_a_to_d.md
#                   (recover with: git show HEAD~1:devlog/DEV_LOG.md)

================================================================================
DATE: 2026-03-15
SESSION: phase_e_prep
AUTHOR: both
TYPE: ANALYSIS + PREP
SUMMARY: AutoSIM Run 1 complete (102 experiments). Code review done. Learnings
         captured. Phase E chain prompt written. Clean restart planned.
================================================================================

AUTOSIM RUN 1 — FINAL NUMBERS:
  Experiments:   102 (IDs 0–101)
  Runtime:       ~5 hours  (2026-03-14 22:53 → 2026-03-15 03:53)
  Start score:   0.7027  (experiment 0, default config)
  Best score:    0.9852  (experiment 98)
  Improvement:   +40.2%
  Weak metric:   avg_lifetime_births = 3.82 (target floor 4.0, gap = 0.18)

CALIBRATED PARAMETER SHIFTS (default → best_config.yaml):
  wealth_diminishing_power:    0.70 → 0.838   ← biggest single-step gain (exp 1)
  pair_bond_dissolution_rate:  0.10 → 0.020   ← primary fertility lever
  female_choice_strength:      0.60 → 0.882   ← shapes selection dynamics globally
  child_investment_per_year:   0.50 → 0.993   ← coupled to childhood survival
  mortality_base:              0.02 → 0.005   ← lower background, higher episodic
  childhood_mortality_annual:  0.02 → 0.047   ← more child death, less adult death
  epidemic_lethality_base:     0.15 → 0.246   ← more lethal when they hit
  subsistence_floor:           1.00 → 0.300   ← was hiding resource stress
  base_conception_chance:      0.50 → 0.673   ← direct fertility
  resource_abundance:          1.00 → 1.370   ← stability required more resources

TOP 9 SCIENTIFIC FINDINGS (full detail: docs/autosim_learnings_pre_phase_e.md):
  1. Default config over-protected agents — realistic mortality was needed
  2. Pair bond STABILITY is the primary fertility regulator, not conception rate
  3. Female choice must be very high (~0.88) for realistic selection dynamics
  4. Mortality structure (who dies, when) matters more than total death rate
  5. Adult background mortality should be LOW; childhood + epidemics HIGH
  6. Subsistence floor was insulating agents from the scarcity being studied
  7. Violence: more frequent, quickly resolved, moderately lethal
  8. avg_lifetime_births gap likely from low bonded-female fraction (~28%)
  9. Scarcity_severity and epidemic_lethality hitting tuning range ceilings

TARGETS.YAML TUNING RANGE UPDATES RECOMMENDED:
  scarcity_severity:          ceiling 0.80 → 0.95
  epidemic_lethality_base:    ceiling 0.30 → 0.35
  pair_bond_dissolution_rate: floor   0.02 → 0.01
  Remove from tunable (insensitive): grandparent_survival_bonus,
                                     cooperation_network_bonus

14 ENGINEERING BUGS IDENTIFIED (Phase E fixes):
  P0  ID counter bleeds across autosim runs — IDs not isolated per simulation
  P0  society.events unbounded — OOM risk on long/large runs
  P1  _parent_* belief attrs injected dynamically, not declared in Agent
  P1  Config.load() silently drops unknown YAML keys
  P2  household_of() O(N) partner scan — needs reverse index
  P2  Engine print() pollutes autosim batch output — needs logging
  P2  mating_system __post_init__ wiring incomplete
  P2  Dead ledger cleanup unreliable
  P3  dashboard/app.py 111KB god file
  P3  journal.jsonl committed to git
  P3  No .python-version; plotly missing from requirements.txt
  P3  Only 1 smoke test file

FILES CREATED:
  docs/autosim_learnings_pre_phase_e.md    ← full 102-experiment analysis
  prompts/phase_e_engineering_hardening.md ← executable fix prompt
  devlog/archive/DEV_LOG_phase_a_to_d.md  ← phase history archive

NEXT STEPS:
  [ ] git show HEAD~1:devlog/DEV_LOG.md > devlog/archive/DEV_LOG_phase_a_to_d_recovered.md
  [ ] copy autosim\journal.jsonl autosim\journal_pre_phase_e.jsonl
  [ ] Stop autosim
  [ ] claude --dangerously-skip-permissions < prompts/phase_e_engineering_hardening.md
  [ ] python -m pytest tests/ -v  (all green)
  [ ] Clear autosim/journal.jsonl
  [ ] Restart autosim from best_config.yaml
  [ ] Update targets.yaml with tuning range recommendations above
  [ ] Primary target: close avg_lifetime_births gap (3.82 → 4.0+)

================================================================================
