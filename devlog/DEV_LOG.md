# SIMSIV — DEVELOPMENT LOG
# Simulation of Intersecting Social and Institutional Variables
# Path: D:\EXPERIMENTS\SIM\devlog\DEV_LOG.md

================================================================================
HOW TO USE THIS LOG
================================================================================

Every session, every decision, every change gets logged here.
Format for each entry:

---
DATE: YYYY-MM-DD
SESSION: [number]
AUTHOR: [human / claude / both]
TYPE: [DESIGN / CODE / EXPERIMENT / DEBUG / REFACTOR / DECISION / QUESTION]
SUMMARY: [one line]
DETAILS:
  [full notes]
DECISIONS MADE:
  [bullet list of anything locked in]
FILES CHANGED:
  [list of files touched]
NEXT ACTIONS:
  [what needs to happen next]
---

================================================================================
LOG ENTRIES
================================================================================

---
DATE: 2026-03-13
SESSION: 001
AUTHOR: both
TYPE: DESIGN + SCAFFOLDING
SUMMARY: Project initiated. Directory scaffold built. Design Q&A session begun.
DETAILS:
  - Project SIMSIV formally initialized at D:\EXPERIMENTS\SIM
  - Full project brief reviewed and internalized
  - CHAIN_PROMPT.md created as living master document
  - 45 design questions posed across 9 categories
  - Design Q&A session conducted (see decisions below)
  - Full directory scaffold created
  - DEV_LOG.md initialized (this file)
  - prompts/ directory created for prompt library
  - artifacts/ directory created for design artifacts, charts, exports
  - devlog/ directory created for this log

DECISIONS MADE:
  SCALE:
    - Population: maximize for richness, target 500-1000 agents
    - Generations: maximize, target 100+
    - Time step: annual tick for v1 (revisit in Phase B deep dives)
    - Runtime: kill the compute — no hard ceiling, optimize later

  AGENT MODEL:
    - Traits ARE heritable (parent → offspring blend + Gaussian noise)
    - Heritable traits (v1): aggression, cooperation, attractiveness_base,
      status_drive, risk_tolerance, jealousy_sensitivity, fertility_base,
      intelligence_proxy
    - Non-heritable (earned): social_trust, reputation, pair_bond_status
    - Mutation: YES — Gaussian noise σ=0.05 per heritable trait per generation
    - Decision model: HYBRID — probabilistic weights with utility tiebreakers
    - Agent memory: YES — lightweight reputation ledger per agent pair
      (trust scores updated by cooperation/defection/conflict history)
    - Trait representation: CONTINUOUS (0.0-1.0) — not archetypes
    - Mate value: DYNAMIC — f(health, status, resources, age)

  MATING SYSTEM:
    - Default: UNRESTRICTED COMPETITION (null hypothesis baseline)
    - All variants configurable as experimental overlays
    - Deep dive on mating system = Phase B priority #1

  RESOURCE MODEL:
    - Deep dive in Phase B — v1 uses two-dimensional (survival + status)
    - Architecture must support future expansion

  CONFLICT MODEL:
    - Deep dive in Phase B — v1 implements all standard triggers
    - Architecture must be modular and replaceable

  INSTITUTIONS:
    - Deep dive in Phase B — v1 uses toggle/hybrid approach
    - Designed so institutions can strengthen/erode from agent outcomes

  OUTPUT:
    - CSV + matplotlib charts (PNG) + narrative text summary
    - All runs auto-compared to free-competition baseline
    - Prompts stored in prompts/ directory
    - Artifacts stored in artifacts/ directory

  PHILOSOPHY:
    - Skeleton-first: build working end-to-end sim, then do deep dives
    - Phase A = skeleton with defensible v1 defaults
    - Phase B = deep dive chains per subsystem, in this order:
        1. Mating system
        2. Resource model
        3. Conflict model
        4. Agent trait inheritance + mutation
        5. Institutions
        6. Offspring/household
        7. Memory/reputation

FILES CHANGED:
  - D:\EXPERIMENTS\SIM\CHAIN_PROMPT.md (created, to be updated)
  - D:\EXPERIMENTS\SIM\devlog\DEV_LOG.md (this file, created)
  - All directories created (see scaffold)

NEXT ACTIONS:
  - Update CHAIN_PROMPT.md with all confirmed decisions
  - Write prompts/phase1_design.md
  - Write prompts/phase2_skeleton.md
  - Write prompts/iteration_template.md
  - Write prompts/debug_template.md
  - Write prompts/deep_dive_template.md
  - Begin Phase 1: System Design and Model Specification
---

================================================================================
END OF LOG
================================================================================
