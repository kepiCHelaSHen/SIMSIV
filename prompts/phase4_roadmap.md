# SIMSIV — PROMPT: PHASE 4 — ROADMAP AND VALIDATION
# File: D:\EXPERIMENTS\SIM\prompts\phase4_roadmap.md
# Use: Paste this entire prompt to Claude to execute Phase 4

================================================================================
CONTEXT INJECTION — READ FIRST
================================================================================

You are planning the future of SIMSIV. Read ALL prior files before producing
any output. This phase is documentation and planning, not implementation.

Read:
  1. D:\EXPERIMENTS\SIM\CHAIN_PROMPT.md
  2. D:\EXPERIMENTS\SIM\devlog\DEV_LOG.md
  3. D:\EXPERIMENTS\SIM\docs\ (all files)
  4. Skim all .py files for architecture understanding

================================================================================
PHASE 4 TASK: ROADMAP, VALIDATION, AND EXPANSION
================================================================================

Produce the following documents in D:\EXPERIMENTS\SIM\docs\

A. roadmap_v2_v3.md
   - Concrete v2 feature list with implementation complexity estimates
   - Concrete v3 feature list
   - Prioritization rationale
   - Dependencies between features
   Candidate v2 features (evaluate and prioritize):
     - Matrilineal inheritance system
     - Patrilineal vs matrilineal as configurable variable
     - Recreational pair bonding as social stability mechanism
     - Multi-group / multi-tribe dynamics (migration, inter-group war)
     - Religion / moral code as abstracted norm enforcement mechanism
     - Elite succession crises and inheritance disputes
     - Reputation economy (public vs private reputation)
     - Kin coalition and alliance formation
     - Cultural norm transmission and drift
     - Trade networks between agents

B. validation_strategy.md
   - Explicit framework for "is this model behaving sanely"
   - Sanity checks tied to known anthropological patterns:
       * Does elite polygyny increase reproductive skew? (expected: yes)
       * Does monogamy reduce unmated male %, violence? (expected: yes)
       * Does resource scarcity increase inequality? (expected: yes)
       * Does pair bonding improve child survival? (expected: yes)
       * Does strong female choice intensify male status competition? (yes)
   - Calibration vs validation distinction (be honest about limits)
   - Literature references to anchor sanity checks
   - What counts as "this model is broken"
   - What counts as "this model is producing interesting emergent behavior"

C. architecture_expansion.md
   - How to add new engines without breaking existing code
   - How to add new agent attributes
   - How to add new institution types
   - How to add spatial / landscape component
   - How to add multi-group dynamics
   - Interface contracts between modules
   - What should NEVER change (stable interfaces)
   - What is designed to be replaced (swappable subsystems)

D. sprint_next.md
   - Concrete next 3 sprints after skeleton is working
   - Each sprint: goal, files to create/modify, acceptance criteria
   - Sprint 1: First deep dive (mating system)
   - Sprint 2: Second deep dive (resource model)
   - Sprint 3: Experiment runner + first real results

E. agent_design_notes.md
   - Deep notes on agent trait design decisions
   - Mutation model mathematics
   - Inheritance blend formula
   - Mate value function specification
   - Reputation ledger update rules
   - Decision weight calculation details
   - Known limitations of the current agent model
   - Proposed v2 agent extensions

================================================================================
AFTER IMPLEMENTATION
================================================================================

Update devlog: D:\EXPERIMENTS\SIM\devlog\DEV_LOG.md
Copy roadmap_v2_v3.md to: D:\EXPERIMENTS\SIM\artifacts\design\
