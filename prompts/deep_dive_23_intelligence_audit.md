# SIMSIV — PROMPT: TARGETED FIX 23 — INTELLIGENCE FEEDBACK LOOP AUDIT
# File: D:\EXPERIMENTS\SIM\prompts\deep_dive_23_intelligence_audit.md
# Use: Send to Claude after DD22 is complete
# Priority: PHASE C, Sprint 16
# Note: This is a targeted fix session, not a full deep dive

================================================================================
CONTEXT INJECTION — READ FIRST
================================================================================

You are doing a targeted audit and fix of the intelligence feedback loop in SIMSIV.

Before doing ANYTHING, read:
  1. D:\EXPERIMENTS\SIM\CHAIN_PROMPT.md
  2. D:\EXPERIMENTS\SIM\devlog\DEV_LOG.md
  3. D:\EXPERIMENTS\SIM\engines\resources.py (intelligence in competitive weights)
  4. D:\EXPERIMENTS\SIM\engines\reputation.py (intelligence in gossip)
  5. D:\EXPERIMENTS\SIM\engines\conflict.py (intelligence in combat)
  6. D:\EXPERIMENTS\SIM\engines\mating.py (intelligence in mate value? check)
  7. D:\EXPERIMENTS\SIM\metrics\collectors.py (track intelligence evolution)
  8. D:\EXPERIMENTS\SIM\STATUS.md (check current intelligence trend data)

Intelligence currently feeds into multiple productivity pathways simultaneously.
If these pathways compound without diminishing returns, intelligence could
become the dominant evolutionary driver — the single trait that matters above
all others, making all other traits relatively insignificant. This would be
both unrealistic and bad for the game (no interesting trade-offs).

================================================================================
AUDIT AND FIX: INTELLIGENCE FEEDBACK LOOP
================================================================================

TASK 1: AUDIT — Map every place intelligence affects outcomes

Go through EVERY engine file and document:
A. WHERE intelligence_proxy affects outcomes:
   List every computation where intelligence_proxy appears as a variable.
   Note the magnitude of the effect and whether it compounds with itself.

B. FEEDBACK LOOP IDENTIFICATION:
   Does intelligence → more resources → better survival → more offspring
   → children with higher intelligence → even more resources → etc?
   Is there any mechanism that LIMITS this compounding?

C. CURRENT INTELLIGENCE TREND:
   Check STATUS.md and metrics for intelligence trait evolution.
   Is it rising faster than other traits? Is it approaching ceiling (1.0)?
   Compare intelligence selection pressure to cooperation and aggression.

TASK 2: DIAGNOSIS — Determine if there IS a problem

Run a targeted experiment:
  - 5 seeds, 500 pop, 200 years
  - Track intelligence_proxy mean and std each 50 years
  - Compare to aggression and cooperation evolution rates
  - If intelligence rises >0.15 over 200 years while other traits rise <0.08,
    there IS a compounding problem that needs fixing

TASK 3: FIX (if needed) — Add diminishing returns

If the audit confirms a compounding problem, implement ONE of these fixes
(choose the most minimal intervention that resolves it):

Option A: Diminishing returns on intelligence in resource competitive weight
  Current: intelligence * 0.25 in competitive weight
  Fix: min(intelligence_proxy ** 0.7, 0.8) * 0.25
  Effect: high intelligence still helps but not proportionally at extremes

Option B: Soft cap on intelligence trait via mutation resistance
  Current: intelligence can rise to 1.0 without resistance
  Fix: when intelligence_proxy > 0.75, mutation sigma effectively increases
  (harder to improve further — maintenance costs of high intelligence)
  Effect: natural ceiling emerges without hard cap

Option C: Intelligence cost — cognitive overhead
  High intelligence agents pay a small resource cost (cognitive maintenance)
  This creates a trade-off: smarter = slightly more resource expensive
  Fix: if agent.intelligence_proxy > 0.7: health_decay *= 1.02
  Effect: very high intelligence is slightly less fit unless resources are abundant

Option D: Social cap — intelligence without social skills is limited
  Intelligence benefits only fully realized in cooperation networks
  Fix: intelligence_effective = intelligence_proxy * (0.6 + cooperation_propensity * 0.4)
  Effect: smart loners less effective than smart cooperators
  (already partially true but strengthen this link)

TASK 4: VALIDATE

After fix (if any):
  - Re-run 5 seed experiment
  - Confirm intelligence still rises (it should — intelligence is adaptive)
    but rises at similar rate to cooperation
  - Confirm other trait evolution signals are not suppressed
  - Log findings in DEV_LOG.md regardless of whether a fix was needed

================================================================================
ALSO CHECK — OTHER POTENTIAL FEEDBACK LOOPS

While auditing, check these other potential runaway loops:

1. COOPERATION FEEDBACK: cooperation → larger networks → more resources
   → better survival → more offspring → higher cooperation in offspring
   Is cooperation also compounding? Compare to intelligence rates.

2. PRESTIGE FEEDBACK: prestige → more resources → display → more prestige
   Prestige decay rate (1%/yr) should prevent this. Verify it does.

3. HEALTH FEEDBACK: health → survive longer → more offspring → higher health genes
   This is INTENDED (health should be selected for) but check it's not too fast.

================================================================================
DELIVERABLES
================================================================================

1. docs/deep_dive_23_intelligence_audit.md — audit findings and fix rationale
2. Target engine file(s) — minimal fix implementation (if needed)
3. config.py — one new parameter if fix requires it (keep minimal)
4. DEV_LOG.md entry — findings even if no fix needed
5. STATUS.md update

================================================================================
CONSTRAINTS
================================================================================

- MINIMAL INTERVENTION: only fix if there IS a demonstrated problem
- Do not reduce the importance of intelligence — it should matter
  We just want it to matter at a similar scale to cooperation
- One fix maximum — don't add multiple intelligence constraints at once
- Rerun validation experiment after any fix to confirm it works
- If no problem found: document that intelligence is not a runaway feedback loop
  and move on. This is a valid and good finding too.
