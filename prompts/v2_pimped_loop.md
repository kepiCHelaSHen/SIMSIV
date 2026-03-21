# SIMSIV — PROMPT: V2 SELF-IMPROVING INNOVATION LOOP
# File: D:\EXPERIMENTS\SIM\prompts\v2_pimped_loop.md
# Purpose: Infinite self-improving build loop for v2 clan simulator
# Run after: v2 5-turn experiment completes
# Uses: simsiv-builder, simsiv-critic, simsiv-code-reviewer subagents + council.py
# Reviewed by: Grok ✅ GPT ✅ Gemini ✅ — all fixes applied
# Loop runs until science is done or genuinely stuck — no arbitrary turn limit
# Architecture: State Machine with Negative Feedback Loops and Metabolic Cycles

================================================================================
CONTEXT INJECTION — READ FIRST (non-negotiable)
================================================================================

Before doing ANYTHING, read ALL of these in order:

  1. D:\EXPERIMENTS\SIM\CHAIN_PROMPT.md
  2. D:\EXPERIMENTS\SIM\CLAUDE.md
  3. D:\EXPERIMENTS\SIM\STATUS.md
  4. D:\EXPERIMENTS\SIM\V2_INNOVATION_LOG.md
  5. D:\EXPERIMENTS\COUNCIL_REVIEW.md
  6. D:\EXPERIMENTS\AGENTIC_WORKFLOW.md
  7. D:\EXPERIMENTS\SIM\outputs\state_vector.md (if it exists — this is your save game)

V2_INNOVATION_LOG.md is your memory.
state_vector.md is your compressed anchor after context resets.
Read both before deciding anything.

================================================================================
FROZEN CODE — ABSOLUTE RULE
================================================================================

The v1.0 codebase produced bioRxiv paper BIORXIV/2026/711970.
DO NOT touch any existing file.
DO NOT fix bugs listed in STATUS.md.
Build ONLY in:
  models/clan/
  engines/clan_*.py
  metrics/clan_collectors.py
  tests/test_clan_*.py

If unsure whether a file is safe to touch — do not touch it.

================================================================================
TWO MODES — CHOOSE AT THE START OF EVERY TURN
================================================================================

VALIDATION MODE (default):
  Full literature grounding required before building.
  Critic is a HARD BLOCKER — must pass before commit.
  Council runs BEFORE build.
  Full multi-seed anomaly detection required.
  Use for: known mechanisms, calibration, fixing issues, post-exploration.

EXPLORATION MODE (when stuck or novelty needed):
  Literature grounding RELAXED — state hypothesis instead of citation.
  Critic is ADVISORY — logs issues but does not block.
  Council runs AFTER build.
  Multi-seed anomaly detection still required.
  REVERSION PROTOCOL ACTIVE (see below).
  Use when: no metric improvement in 5 turns, divergence experiment,
            searching for novel mechanisms, post-Milestone 9.
  Max 3 consecutive Exploration turns. Then return to Validation.
  3 Exploration turns with no improvement → EXIT 2.
  Log at top of turn: "MODE: EXPLORATION — reason: [why]"

================================================================================
REVERSION PROTOCOL — EXPLORATION MODE SAFETY NET
================================================================================

Exploration Mode can introduce changes that break frozen logic 2-3 turns later.
This protocol prevents configuration drift from compounding.

TRIGGER: Any Exploration Mode turn that fails the Multi-Seed Anomaly Check.

EXECUTE:
  1. Do NOT attempt to fix the broken code.
  2. Run: git checkout v2-turn-N-pass
     Where N = the turn number of the last successful Validation Mode tag.
  3. Log in V2_INNOVATION_LOG.md:
     "REVERSION: Turn [current] exploration broke anomaly check.
      Reverted to v2-turn-[N]-pass. Approach added to v2_dead_ends.md."
  4. Append the failed approach to prompts/v2_dead_ends.md with:
     - What was attempted
     - Which seed(s) failed and which bounds were violated
     - Why this approach is now a dead end
  5. Return to Validation Mode. Next turn starts from the reverted state.

This is not failure. This is the system working correctly.
Layering fixes on broken Exploration code is the real failure.

================================================================================
SUBAGENT ROLES — SYNTHETIC DIALECTIC
================================================================================

The Critic and Reviewer have distinct, opposing goals. This tension is deliberate.

SIMSIV-CRITIC — "THE PESSIMIST"
  Goal: Prove the science is wrong and the code is fragile.
  Mindset: Assume the build failed until proven otherwise.
  Specific mission: Actively look for reasons why the implementation
    VIOLATES or MISREPRESENTS the frozen bioRxiv paper.
  Ask: "If I wanted to prove this mechanism is NOT Bowles/Gintis,
        what would I point to?"
  Gates (unchanged):
    Gate 1: Frozen code compliance (must = 1.0 — hard blocker)
    Gate 2: Architecture compliance (must ≥ 0.85)
    Gate 3: Scientific validity — argue against it, then score it (must ≥ 0.85)
    Gate 4: Drift check (must ≥ 0.85)
  In Exploration Mode: advisory only, but pessimism is still required.
  Output: verdict PASS | NEEDS_IMPROVEMENT with blocking/non-blocking split.

SIMSIV-CODE-REVIEWER — "THE LINTER"
  Goal: PEP8, circular imports, file structure, line-level hygiene.
  Mindset: Does not have opinions about science or architecture.
  Specific mission: Find code smells, style violations, hardcoded values,
    determinism bugs, and structural issues. Nothing else.
  Does NOT: evaluate scientific validity, question architecture decisions,
    or suggest features.
  Output: CRITICAL / WARNING / MINOR with exact line citations.

SIMSIV-BUILDER — "THE IMPLEMENTER"
  Goal: Build exactly what is specified. No more. No less.
  Mindset: Reads the constitution before every build.
  Does NOT: make architectural decisions, modify frozen files,
    or add features beyond the turn scope.

================================================================================
SUBAGENT HEALTH CHECK — EVERY TURN
================================================================================

  BUILDER: "Confirm active. State first rule from CLAUDE.md."
    Expected: cites CLAUDE.md content accurately.
    Fail: retry once. Still failing → EXIT 2.

  CRITIC: "Confirm active. You are The Pessimist. What is Gate 1 and threshold?
           What is your specific mission regarding the bioRxiv paper?"
    Expected: "frozen code compliance, must = 1.0" +
              "actively look for violations of the frozen paper"
    Wrong or missing second part: log "critic role drift" and re-invoke
    with full role description before proceeding.

  REVIEWER: "Confirm active. You are The Linter. What do you NOT evaluate?"
    Expected: "not science, not architecture — only code hygiene"
    Wrong answer: log "reviewer role drift" and re-invoke with full role.

  Log health check results every turn in V2_INNOVATION_LOG.md.
  Persistent failure → EXIT 2.

================================================================================
EXIT CONDITIONS
================================================================================

  EXIT 1 — SCIENCE COMPLETE (see detail at bottom)

  EXIT 2 — PERFORMANCE GATE
    No measurable metric improvement across 5 consecutive turns AND
    3 Exploration turns also produced no improvement.
    Metrics tracked (log delta every turn):
      inter_band_violence_rate → target 0.02-0.15
      trade_volume_per_band → target 0.10-0.40
      between_group_sel_coeff → target 0.01-0.10
      cooperation divergence FREE_COMPETITION vs STRONG_STATE
      AutoSIM v2 realism score
    → Write outputs/options.md. Stop. Wait for human.

  EXIT 3 — UNRESOLVABLE ANOMALY
    Multi-seed anomaly on 3 consecutive turns AND reversion protocol failed.
    → git tag v2-stuck-turn-N
    → Write outputs/stuck_report.md. Run council.py. Stop. Wait for human.

  EXIT 4 — FUNDAMENTAL MISALIGNMENT
    Critic: root is broken, patching won't fix it.
    → git tag v2-abandoned-turn-N
    → Write outputs/rebuild_rationale.md. Run council.py. Stop. Wait for human.

  EXIT 5 — HUMAN SAYS STOP
    File D:\EXPERIMENTS\SIM\STOP exists → halt. Write state to log.

================================================================================
EVERY TURN — THE LOOP
================================================================================

BEFORE BUILDING:

  STEP 1 — CHECK EXIT CONDITIONS
    Any met? Execute and stop.
    Performance gate: any metric improved last 5 turns?
    No → switch to Exploration Mode. Log reason.

  STEP 2 — SUBAGENT HEALTH CHECK
    All three. Verify roles explicitly. Log results.

  STEP 3 — CHOOSE MODE. Log it and why.

  STEP 4 — DEAD END CHECK
    Read V2_INNOVATION_LOG.md + prompts/v2_dead_ends.md
    List what failed. Do not repeat it.
    Log: "Dead ends avoided: [list or NONE]"

  STEP 5 — WHAT TO BUILD
    Read last log entry. One clear thing per turn. No scope creep.

  STEP 6 — PROACTIVE COUNCIL (Validation Mode only)
    Summarize plan 3-5 sentences. Run council.py.
    Both flag same risk → redesign before building.
    Skip in Exploration Mode — council runs after.

  STEP 7 — GROUNDING
    Validation: cite Bowles/Gintis mechanism + equation + implementation mapping.
                Cannot cite → do not build. Log gap. Next turn.
    Exploration: state hypothesis. "I expect X because Y. Test: Z."
                 No citation required but hypothesis must be falsifiable.

BUILD using simsiv-builder subagent.

AFTER BUILDING:

  STEP 8 — SELF CRITIQUE
    Frozen file touched? Circular imports? Randomness seeded? Tests pass?
    Does this implement the grounding/hypothesis from Step 7?

  STEP 9 — CRITIC REVIEW (The Pessimist)
    Validation: hard blocker. Max 3 rounds. Blocked → log + move on.
    Exploration: advisory. Log all issues. Do not block commit.
    Both modes: critic must argue against the science before scoring it.

  STEP 10 — CODE REVIEWER (The Linter)
    Every new file. Fix CRITICAL. Log WARNING/MINOR as non-blocking.
    Linter does not evaluate science. Ignore any science comments from it.

  STEP 11 — COUNCIL
    Validation: skip unless critic flagged issues. Then run council.py.
    Exploration: run NOW. Run council.py. Fix consensus flags. Log fixes.

  STEP 12 — MULTI-SEED ANOMALY DETECTION
    Run 3 seeds minimum:
      python main.py --seed 42 --years 50 --population 100
      python main.py --seed 137 --years 50 --population 100
      python main.py --seed 271 --years 50 --population 100

    BOUND CHECK (all 3 seeds must pass):
      cooperation > 0.25
      aggression < 0.70
      population not zero

    VARIANCE CHECK (across 3 seeds):
      cooperation std < 0.15
      aggression std < 0.15
      If σ > 0.10 on any metric within target range:
        Flag: STOCHASTIC_INSTABILITY
        Force 1 Validation Mode turn to tighten the mechanism before continuing.

    TREND CHECK (across last 3 turns):
      No metric monotonically worsening across 3 consecutive turns.
      Flag: TREND_DEGRADATION if detected.

    2+ seeds fail bound check → ANOMALY
    Three consecutive ANOMALY → EXIT 3
    STOCHASTIC_INSTABILITY → force Validation turn (not an exit, a correction)

    EXPLORATION MODE: if anomaly check fails → REVERSION PROTOCOL (see above)

  STEP 13 — METRIC IMPROVEMENT TRACKING
    Record all 5 performance gate metrics. Compare to last turn.
    Log delta for each: "[metric] [last] → [current] ([+/-change])"
    This feeds EXIT 2. Track streak of turns with no improvement.

  STEP 14 — COMMIT AND LOG
    If Exploration and anomaly passed: commit. Git tag: v2-turn-N-pass
    If Exploration and anomaly failed: REVERSION PROTOCOL. Do not commit.
    Validation: commit only if critic passed. Git tag: v2-turn-N-pass

    Append to V2_INNOVATION_LOG.md:
      Turn number and mode
      What was built
      Dead ends avoided
      Grounding or hypothesis
      Health check results (roles confirmed?)
      Critic verdict + gate scores
      Linter: CRITICAL issues found/fixed
      3-seed anomaly results + variance + trend
      STOCHASTIC_INSTABILITY flag if triggered
      Metric deltas (all 5)
      Council flags and fixes
      Reversion executed? (yes/no + reason)
      What next turn should focus on

  STEP 15 — SESSION MEMORY
    Update prompts/v2_session_state.md — current state, mode, why.
    Failures → prompts/v2_dead_ends.md

  STEP 16 — PROMPT LOG
    Append to prompts/v2_turn_prompts.md:
      ## Turn N — [date]
      ### Builder prompt:
      [exact prompt sent to simsiv-builder this turn]
      ### Critic prompt:
      [exact prompt sent to simsiv-critic this turn]
      ### Council plan summary:
      [the 3-5 sentence plan summary sent to council.py]
      ---
    This creates a full reproducible record of every build decision.
    Future sessions and researchers can replay any turn exactly.

  LOOP TO STEP 1.

================================================================================
SYNTHESIS SCHEDULE
================================================================================

LIGHTWEIGHT — every 3 turns after Milestone 7:
  Read last 3 log entries.
  Track? Science grounded? Metrics improving? Any STOCHASTIC_INSTABILITY flags?
  NO to any → run council.py immediately.
  Log MINI-SYNTHESIS. Adjust priority. Continue.

FULL — every 5 turns:
  Read full V2_INNOVATION_LOG.md.
  Write SYNTHESIS:
    What built, what working, what drifting
    Metric trajectory across last 5 turns
    Count of reversions (exploration failures)
    STOCHASTIC_INSTABILITY flags resolved?
    Validation vs Exploration balance — is it right?
    Next 5 turn priorities
  Run council.py.
  Write outputs/options.md — 2-3 choices with mode specified.
  Pick best by metric trajectory.
  No option with positive trajectory → EXIT 2.
  Log chosen direction. Continue.

================================================================================
CONTEXT RESET — TURN 15, THEN EVERY 5 TURNS
================================================================================

STEP A — GENERATE STATE VECTOR SUMMARY
  Before compacting, write outputs/state_vector.md:
  This is the save game. It must be exactly 10-15 lines. No more.

  Required fields:
    TURN: [current turn number]
    MILESTONE: [current milestone and status]
    MODE: [current mode and why]
    LAST_3_FAILURES: [brief description of last 3 dead ends]
    WINNING_PARAMETERS: [any config/parameter values found to work]
    METRIC_STATUS: [current value vs target for all 5 metrics]
    OPEN_FLAGS: [any ANOMALY / INSTABILITY / TREND_DEGRADATION not resolved]
    LAST_VALIDATION_TAG: [git tag of last successful Validation commit]
    NEXT_TURN_FOCUS: [one sentence]
    SCIENCE_GROUNDING: [one sentence — are we still on Bowles/Gintis?]

STEP B — COMPACT
  Run /compact in Claude Code.

STEP C — RE-ANCHOR
  Re-read CHAIN_PROMPT.md and CLAUDE.md fresh. Do not rely on memory.
  Read outputs/state_vector.md — this is your new anchor.
  Re-run subagent health checks with role verification.
  Log: "CONTEXT RESET — Turn N. State vector loaded. Health checks passed."

If subagent fails health check after reset → EXIT 2.
If output feels generic or detached from science → compact immediately
  and generate state vector even if not at turn 15.

================================================================================
MILESTONE SEQUENCE
================================================================================

  1. FOUNDATION (Validation) — scaffold, clan_base.py, smoke test
  2. TRADE (Validation) — clan_trade.py, trust, outgroup_tolerance
  3. RAIDING (Validation) — clan_raiding.py, aggression+scarcity, coalitions
  4. BETWEEN-GROUP SELECTION (Validation) — clan_selection.py, Bowles/Gintis,
     within + between coefficients tracked separately
  5. SESSION MEMORY (Validation) — v2_dead_ends.md, v2_session_state.md
  6. DIVERGENCE EXPERIMENT (Exploration — explicit) — Branch A vs B,
     3 seeds each, critic advisory, reversion protocol active, merge winner
  7. AUTOSIM V2 (Validation) ← LIGHTWEIGHT SYNTHESIS EVERY 3 TURNS STARTS HERE
     Multi-band calibration, 50+ experiments:
       inter_band_violence_rate: [0.02, 0.15]
       trade_volume_per_band: [0.10, 0.40]
       between_group_sel_coeff: [0.01, 0.10]
  8. METRICS (Validation) — clan_collectors.py, all inter-band metrics
  9. FULL CLAN RUN (Validation) — 200yr, 3 bands, 3 seeds minimum,
     FREE_COMPETITION vs STRONG_STATE, measure cooperation divergence
  10. CONTINUOUS IMPROVEMENT (alternating modes) — loop until EXIT 1

================================================================================
EXIT 1 — SCIENCE DONE — FULL CRITERIA
================================================================================

docs/v2_findings.md must contain ALL of these:

  1. Cooperation divergence across governance scenarios
     Evidenced by data across 3+ seeds. Not just code. Actual numbers.

  2. FREE_COMPETITION vs STRONG_STATE at 200yr
     Report mean AND std per scenario across 3 seeds.
     Is the difference statistically meaningful?

  3. AutoSIM v2 realism score ≥ 0.85 against inter-band targets.

  4. One paragraph: what this means for Bowles/Gintis vs North.
     Cite the mechanism. Cite the data. One paragraph only.

  5. Experiment list for Paper 2 to make the claim publishable.

  6. No open STOCHASTIC_INSTABILITY flags on any primary metric.

All 6 present and evidenced → EXIT 1. Write COMPLETION REPORT. Stop.
