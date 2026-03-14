# SIMSIV — PROMPT: DEEP DIVE 02 — RESOURCE MODEL
# File: D:\EXPERIMENTS\SIM\prompts\deep_dive_02_resources.md
# Use: Send to Claude after skeleton is working and DD01 mating is complete
# Priority: PHASE B, Sprint 2

================================================================================
CONTEXT INJECTION — READ FIRST
================================================================================

Read before starting:
  1. D:\EXPERIMENTS\SIM\CHAIN_PROMPT.md
  2. D:\EXPERIMENTS\SIM\devlog\DEV_LOG.md
  3. D:\EXPERIMENTS\SIM\engines\resources.py
  4. D:\EXPERIMENTS\SIM\models\agent.py
  5. D:\EXPERIMENTS\SIM\docs\rules_spec.md resource sections

================================================================================
DEEP DIVE 02: RESOURCE MODEL
================================================================================

QUESTIONS TO RESOLVE AND IMPLEMENT:

A. RESOURCE DIMENSIONALITY
   Current v1: two-dimensional (survival_resources + status_resources)
   Decide precisely:
   - Should survival resources be zero-sumish (finite pool per tick)?
   - Should status resources accumulate without hard cap?
   - Should the two dimensions interact? (status amplifies survival acquisition)
   - Is there a conversion rate between them?

B. ACQUISITION FUNCTION
   Design the precise formula for per-agent resource acquisition:
   - Base rate per agent per tick
   - Intelligence_proxy multiplier
   - Status multiplier
   - Environmental abundance multiplier
   - Diminishing returns at high resource levels?
   - Should cooperation between agents boost mutual acquisition?

C. INHERITANCE MODEL
   v1 uses equal_split. Design full configurable inheritance:
   - equal_split: divide estate among all surviving offspring
   - primogeniture: all to eldest son
   - matrilineal: all to sister's children (via mother's brother)
   - configurable_split: parameter controls % to eldest vs rest
   - Should inheritance be delayed (estate held until children come of age)?

D. REDISTRIBUTION / TAXATION
   - Should there be a society-level resource pool?
   - Configurable tax rate: % taken from top earners, redistributed to all
   - Institutional strength gates redistribution enforcement
   - Should redistribution increase social cohesion score?

E. RESOURCE SHOCKS AND SCARCITY EVENTS
   - Precise shock model: how often, how severe, how localized?
   - Should shocks target specific agents or all agents equally?
   - Recovery rate after a shock
   - Should shocks trigger migration (v2) or just competition (v1)?

F. RESOURCE AND MATE VALUE INTERACTION
   - At what threshold do resources meaningfully boost mate value?
   - Should resource display be a male strategy specifically?
   - Should female mate choice weight resources differently by context
     (scarcity = weight resources more, abundance = weight other traits)?

G. WEALTH CEILING
   - Should there be a hard cap? Soft cap (diminishing returns)?
   - Rationale: without cap, elite accumulation accelerates until 1 agent
     owns everything, which may be interesting or may be a model artifact

================================================================================
DELIVERABLES
================================================================================

1. docs/deep_dive_02_resources.md — design decisions and formulas
2. engines/resources.py — full replacement
3. config.py additions
4. models/agent.py updates (if new resource attributes needed)
5. metrics/collectors.py additions
6. DEV_LOG.md entry
7. CHAIN_PROMPT.md update
