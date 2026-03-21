# SIMSIV v2 — COMPREHENSIVE CODE REVIEW AND SCIENTIFIC ANALYSIS
# File: D:\EXPERIMENTS\SIM\prompts\v2_code_review.md
# Purpose: Full independent review of the v2 clan simulator codebase
# Run after: EXIT 1 — science complete
# Uses: simsiv-code-reviewer, simsiv-critic subagents

================================================================================
CONTEXT — READ FIRST
================================================================================

Read these files before doing anything:
  1. D:\EXPERIMENTS\SIM\CHAIN_PROMPT.md       — master design doc
  2. D:\EXPERIMENTS\SIM\CLAUDE.md             — architecture rules
  3. D:\EXPERIMENTS\SIM\docs\v2_findings.md   — scientific findings
  4. D:\EXPERIMENTS\SIM\V2_INNOVATION_LOG.md  — full build history

This is a POST-COMPLETION review. The loop has hit EXIT 1.
You are NOT building anything. You are NOT fixing anything.
You are reading, analyzing, and producing a comprehensive report.

================================================================================
REVIEW SCOPE — V2 FILES ONLY
================================================================================

Review every file in the v2 clan simulator:

  models/clan/band.py
  models/clan/clan_config.py
  models/clan/clan_society.py
  models/clan/clan_simulation.py
  models/clan/__init__.py
  engines/clan_base.py
  engines/clan_trade.py
  engines/clan_raiding.py
  engines/clan_selection.py
  metrics/clan_collectors.py
  tests/test_clan_smoke.py
  tests/test_clan_trade.py
  tests/test_clan_raiding.py
  tests/test_clan_selection.py
  tests/test_clan_integration.py
  tests/test_clan_simulation.py
  docs/v2_findings.md

Do NOT review v1 files. Do NOT suggest fixes to frozen v1 code.

================================================================================
WHAT TO PRODUCE
================================================================================

Write a comprehensive report to:
  D:\EXPERIMENTS\SIM\outputs\reports\v2_review_report.md

The report must cover ALL of the following sections:

---

## SECTION 1 — EXECUTIVE SUMMARY
3-5 paragraphs. High level honest assessment.
- What did the autonomous build loop actually produce?
- Is this publication-quality code?
- What is the overall scientific credibility of the findings?
- What would a senior computational social scientist say when they first read this?

---

## SECTION 2 — CODE QUALITY SCORECARD

Rate each file 1-10 with one sentence of evidence:

  models/clan/band.py              — [score] — [reason]
  models/clan/clan_config.py       — [score] — [reason]
  models/clan/clan_society.py      — [score] — [reason]
  models/clan/clan_simulation.py   — [score] — [reason]
  engines/clan_base.py             — [score] — [reason]
  engines/clan_trade.py            — [score] — [reason]
  engines/clan_raiding.py          — [score] — [reason]
  engines/clan_selection.py        — [score] — [reason]
  metrics/clan_collectors.py       — [score] — [reason]
  tests/ (overall)                 — [score] — [reason]

Overall v2 codebase score: [X/10]

---

## SECTION 3 — ARCHITECTURE ANALYSIS

Answer each question with evidence from the code:

  1. Is the composition pattern (Band HAS-A Society) correctly implemented?
  2. Are circular imports fully absent?
  3. Is all randomness properly seeded and isolated per band?
  4. Are the v1 architecture rules from CLAUDE.md obeyed?
  5. Is the code maintainable — could another engineer extend it?
  6. Are there any performance bottlenecks that would matter at scale?
  7. Is the event system used correctly and consistently?

---

## SECTION 4 — SCIENTIFIC MECHANISMS REVIEW

For each mechanism, assess: is it correctly implemented per the cited literature?

  TRADE ENGINE (clan_trade.py)
  - Is the positive-sum surplus calibrated correctly to Wiessner (1982)?
  - Does outgroup_tolerance correctly gate trade willingness?
  - Is the scarcity-desperation effect scientifically grounded?

  RAIDING ENGINE (clan_raiding.py)
  - Does the Bowles (2006) coalition defense mechanism work correctly?
  - Is group_loyalty driving coalition size as the theory predicts?
  - Is the trust asymmetry (defenders remember more) correctly implemented?
  - Is the casualty system realistic?

  BETWEEN-GROUP SELECTION (clan_selection.py)
  - Is the Fst decomposition mathematically correct?
  - Are within vs between group selection coefficients correctly separated?
  - Is the Malthusian fitness proxy appropriate?
  - Does band fission produce a genuine founder effect?
  - Does migration correctly oppose between-group selection?

  METRICS (clan_collectors.py)
  - Are the inter-band metrics tracking the right things?
  - Is the Fst formula correctly implemented per Wright (1951)?
  - Are cumulative vs per-tick metrics used appropriately?

---

## SECTION 5 — FINDINGS CREDIBILITY ASSESSMENT

Read docs/v2_findings.md carefully. For each finding:

  FINDING 1 — Cooperation divergence is seed-dependent
  - Is this finding robust or an artifact of n=3?
  - What would change with n=10 seeds?

  FINDING 2 — Seed 271 shows clear Bowles/Gintis dynamics
  - Is the Fst growth from 0.06 to 0.36 meaningful?
  - Is the cooperation increase from 0.483 to 0.515 statistically significant?
  - Or is this within normal stochastic variance?

  FINDING 3 — Between-group selection is weak and variable (-0.147 ± 0.235)
  - Is this consistent with the theoretical literature?
  - Is the negative mean coefficient a problem or a finding?

  FINDING 4 — Institutional drift creates a hybrid pathway
  - This is the most novel finding. Is it real or an artifact?
  - Is the drift from 0.0 to 0.15 in Free bands meaningful?
  - What mechanism drives it? Is that mechanism correctly implemented?

  FINDING 5 — Inter-band metrics in target ranges
  - Violence 0.023 ± 0.011 vs target 0.02-0.15
  - Trade 0.226 ± 0.196 vs target 0.10-0.40
  - Are these ranges ethnographically realistic?

---

## SECTION 6 — WHAT BOWLES WILL FIND INTERESTING

You are writing this section for a non-academic audience.
Samuel Bowles is the author of the 2006 Science paper on group selection.
He is 82 years old and has spent 30 years on this question.

Answer these questions directly:

  1. What in this codebase will immediately catch his attention?
  2. What will he question or push back on?
  3. What will he find novel that he has not seen before?
  4. What experiments will he suggest running next?
  5. What would make him take this seriously as a research contribution?
  6. Is the hybrid pathway finding (seed 271 + institutional drift) the right
     thing to lead with in an email to him?

---

## SECTION 7 — WHAT COULD BE BETTER

Honest list of improvements. Do NOT suggest fixing v1 issues.
Focus only on v2 scientific and code quality improvements:

  SCIENTIFIC IMPROVEMENTS (would strengthen the paper):
  - [list each with explanation]

  CODE QUALITY IMPROVEMENTS (would make it more maintainable):
  - [list each with explanation]

  EXPERIMENT IMPROVEMENTS (would make findings more robust):
  - [list each with explanation]

---

## SECTION 8 — TEST SUITE ASSESSMENT

  - How many tests exist? Are they the right tests?
  - Are edge cases covered?
  - Are the integration tests testing the right scientific outcomes?
  - What tests are missing that would catch scientific errors?
  - Run the full test suite and report results:
    python -m pytest tests/ -v

---

## SECTION 9 — OVERALL VERDICT

One paragraph. No hedging. What is this?

Is this:
  A) Toy code that happens to produce interesting numbers
  B) Solid research infrastructure that could support peer-reviewed findings
  C) Publication-quality work that stands on its own
  D) Something genuinely novel in the computational social science space

Give your honest verdict and defend it with evidence from the code and findings.

---

## SECTION 10 — THREE THINGS TO DO BEFORE EMAILING BOWLES

Specific, actionable, in priority order.
Not "run more experiments" — be specific about exactly what and why.

================================================================================
HOW TO RUN THIS REVIEW
================================================================================

STEP 1 — Read all context files listed above.

STEP 2 — Invoke simsiv-code-reviewer on every v2 file.
  Read each file carefully. Do not skim.

STEP 3 — Invoke simsiv-critic on docs/v2_findings.md.
  Apply The Pessimist lens — argue against every finding before assessing it.

STEP 4 — Run the test suite:
  python -m pytest tests/ -v 2>&1

STEP 5 — Write the full report to outputs/reports/v2_review_report.md

STEP 6 — Run council.py for external GPT-4o and Grok perspective:
  python D:\EXPERIMENTS\council.py
  Incorporate their feedback into the report.

STEP 7 — Done. Do not build anything. Do not fix anything.
  Report only.
================================================================================
