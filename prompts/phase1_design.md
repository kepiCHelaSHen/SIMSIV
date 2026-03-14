# SIMSIV — PROMPT: PHASE 1 — SYSTEM DESIGN AND MODEL SPECIFICATION
# File: D:\EXPERIMENTS\SIM\prompts\phase1_design.md
# Use: Paste this entire prompt to Claude to execute Phase 1

================================================================================
CONTEXT INJECTION — READ FIRST
================================================================================

You are implementing SIMSIV — Simulation of Intersecting Social and
Institutional Variables. This is a Python-based emergent social simulation
sandbox modeling how human social structures emerge from first-principles.

Before doing ANYTHING, read the following files in full:
  1. D:\EXPERIMENTS\SIM\CHAIN_PROMPT.md   ← master design document
  2. D:\EXPERIMENTS\SIM\devlog\DEV_LOG.md ← all decisions made so far

These files contain all confirmed design decisions. Do not contradict them.
Do not re-ask questions that have already been answered.

================================================================================
PHASE 1 TASK: SYSTEM DESIGN AND MODEL SPECIFICATION
================================================================================

Produce the following documents. Save each to D:\EXPERIMENTS\SIM\docs\

A. design_memo.md
   - Purpose of the simulation
   - What is being modeled
   - What is intentionally simplified in v1
   - What is intentionally excluded in v1
   - Core design philosophy (discovery over dogma, emergence over scripting)

B. rules_spec.md
   - Full entity definitions (Agent, Household, Children, Society, Environment,
     Institutions) with ALL attributes, types, ranges, and defaults
   - Full environmental parameter list with min/max/default values
   - Institution toggle definitions (v1 set)
   - Main simulation loop specification (pseudocode for each loop)
   - Agent lifecycle specification (birth → growth → mate → reproduce → age → die)
   - Mating engine specification (unrestricted competition default)
   - Resource engine specification
   - Conflict engine specification
   - Offspring/household engine specification
   - Metrics collection specification

C. assumptions.md
   - Complete list of v1 assumptions
   - What each assumption simplifies and why
   - Which assumptions are most likely to matter for results
   - Which assumptions are targets for Phase B deep dives

D. feature_split.md
   - Definitive v1 feature list (what gets built in the skeleton)
   - Definitive v2 feature list (first deep dive expansion)
   - Definitive v3 feature list (advanced features)
   - Clear rationale for each placement

================================================================================
CONFIRMED DESIGN DECISIONS TO RESPECT
================================================================================

SCALE:
  - Population: 500-1000 agents
  - Generations: 100+
  - Time step: annual tick
  - Runtime: no hard ceiling, maximize richness

AGENT TRAITS (heritable, Gaussian mutation σ=0.05):
  aggression_propensity, cooperation_propensity, attractiveness_base,
  status_drive, risk_tolerance, jealousy_sensitivity, fertility_base,
  intelligence_proxy

AGENT TRAITS (non-heritable, earned):
  social_trust, reputation, pair_bond_status, current_resources,
  current_status, health, age

MATE VALUE: dynamic = f(health, status, resources, age)

DECISION MODEL: hybrid probabilistic + utility tiebreaker

MEMORY: reputation ledger per agent pair, updated by interaction history

DEFAULT MATING SYSTEM: unrestricted competition

RESOURCES: two-dimensional (survival_resources + status_resources)

OUTPUT: CSV + PNG charts + narrative text summary

================================================================================
QUALITY BAR
================================================================================

- Be specific. Vague spec is useless.
- Every attribute must have: name, type, range, default, description
- Every parameter must have: name, type, min, max, default, effect
- The simulation loop must be specified at pseudocode level
- Assumptions must be honest about what they mean for interpretation
- Feature split must be principled, not arbitrary

================================================================================
OUTPUT
================================================================================

Save files to: D:\EXPERIMENTS\SIM\docs\
Log completion in: D:\EXPERIMENTS\SIM\devlog\DEV_LOG.md
