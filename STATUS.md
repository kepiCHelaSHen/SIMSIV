# SIMSIV — Current Status

Phase: SUBMITTED — Paper 1 submitted to bioRxiv (BIORXIV/2026/711970)
Version: v1.0-paper1-submitted (tagged, released on GitHub)

## Publication Status
- bioRxiv: BIORXIV/2026/711970 — Version 1 (submitted 2026-03-16, awaiting screening)
- GitHub: https://github.com/kepiCHelaSHen/SIMSIV (public, released)
- JASSS submission: pending bioRxiv DOI
- arXiv: pending endorsement (code T6DWFA sent to ricejam@outlook.com)

## DO NOT MODIFY v1.0 CODEBASE
The submitted paper was produced by this exact codebase.
All bug fixes wait until v2.0 (society module on kernel).

## Known Issues (fix in v2.0 refactor — NOT before JASSS submission)
Found by simsiv-code-reviewer subagent (2026-03-17):

  [CRITICAL] engines/conflict.py — getattr false defaults
    Lines 161, 197, 549 and throughout. getattr(config, 'X', False)
    silently disables coalition_defense, leadership, third_party_punishment
    if incomplete config passed. Should use direct attribute access.
    NOTE: Did not affect Paper 1 experiments (full config.py always used).

  [CRITICAL] engines/conflict.py line 508-512 — missing bond_dissolved event
    Conflict-caused bond breaks emit no event. Mating/mortality engines
    emit bond_dissolved events that metrics count. Violent scenarios
    undercount bond dissolution.
    NOTE: Bond dissolution not a primary Paper 1 finding. Paper safe.

  [WARNING] engines/conflict.py lines 483-492 — rng.choice on object list
    Passes Agent objects directly to rng.choice. No cross-version
    determinism guarantee. Use index-based sampling like line 333.
    NOTE: All Paper 1 experiments ran same numpy version. Paper safe.

  [WARNING] engines/conflict.py line 559 — misaligned punishment threshold
    punish_p uses 0.4 but entry filter uses willing_thresh (default 0.6).
    If willing_thresh set below 0.4 via YAML, punish_p goes negative.

  [MINOR] engines/conflict.py line 103 — hardcoded elder multiplier (0.5)
    Not config-tunable unlike youth/mature multipliers. Breaks discipline.

  [MINOR] engines/conflict.py lines 168 — hardcoded coalition threshold (0.4)
  [MINOR] engines/conflict.py lines 184, 211, 520, 581 — missing outcome key
  [MINOR] engines/conflict.py line 54 — hardcoded attractiveness threshold (0.6)

## Pending Actions (in order)
  1. Check bioRxiv email — confirm paper is live, get DOI
  2. Add DOI to GitHub README and STATUS.md
  3. JASSS submission — after bioRxiv is live
  4. arXiv endorsement — forward code T6DWFA to Henrich, Bowles, or Marlowe
  5. Update GitHub About description (still says "26 heritable traits")
  6. Add GitHub topics: agent-based-modeling, social-simulation,
     evolutionary-anthropology, gene-culture-coevolution
  7. Fix .claude/ directory still tracked in git: git rm -r --cached .claude/
  8. Run full simsiv-code-reviewer audit across all 9 engines (before v2.0 refactor)

## Next Project: Simulation Kernel
  Vision doc: D:\EXPERIMENTS\VISION.md
  Agentic workflow: D:\EXPERIMENTS\AGENTIC_WORKFLOW.md
  - v2.0 will refactor SIMSIV to run as society module ON the kernel
  - All conflict.py issues above get fixed in that refactor
  - Ecology module is first new module (calibrate to Isle Royale, Hubbard Brook)

## System State (v1.0)
  - 35 heritable traits, 5 belief dims, 4 skill domains — DD01-DD27 complete
  - 9 engines, ~257 config params, ~130 metrics per tick
  - AutoSIM: Run 3 complete (816 exp), best score 1.000
  - Calibration: autosim/best_config.yaml
  - Validation: 0/20 collapses, mean 0.934 on held-out seeds
  - 110 scenario experiment runs (governance, mating, resource ecology)

Updated: 2026-03-17
