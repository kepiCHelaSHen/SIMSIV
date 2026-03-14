# SIMSIV — PROMPT: DEEP DIVE TEMPLATE
# File: D:\EXPERIMENTS\SIM\prompts\deep_dive_template.md
# Use: Copy this file, fill in SUBSYSTEM NAME and QUESTIONS, then send to Claude

================================================================================
CONTEXT INJECTION — READ FIRST
================================================================================

You are doing a DEEP DIVE on a specific SIMSIV subsystem.

Before doing ANYTHING, read:
  1. D:\EXPERIMENTS\SIM\CHAIN_PROMPT.md
  2. D:\EXPERIMENTS\SIM\devlog\DEV_LOG.md
  3. The relevant engine file (listed below)
  4. D:\EXPERIMENTS\SIM\docs\rules_spec.md (relevant sections)

================================================================================
DEEP DIVE TARGET: [SUBSYSTEM NAME]
================================================================================

Current implementation file: engines/[ENGINE].py
Current status: working v1 skeleton

================================================================================
DEEP DIVE QUESTIONS FOR THIS SUBSYSTEM
================================================================================

[ PASTE SPECIFIC QUESTIONS HERE ]

Examples for mating system deep dive:
  - What is the most realistic model for female mate choice given the agent
    attributes we have? Design the scoring function precisely.
  - How should pair bond dissolution probability be calculated? What factors
    should affect it?
  - How should infidelity work mechanically? Hidden vs discovered?
  - How should male competition contests resolve? What determines winner?
  - Should courtship have multiple rounds or be resolved in one tick?
  - How should widowhood be handled in the simulation loop?

================================================================================
DELIVERABLES
================================================================================

1. A design memo for this subsystem (docs/deep_dive_[subsystem].md)
   - New design decisions
   - Implementation specification (pseudocode level)
   - Parameter additions to config.py
   - Known tradeoffs and limitations

2. Updated engine file with full implementation
   - Replace or extend the skeleton implementation
   - All new parameters pulled from config
   - All new events properly logged
   - All new metrics added to collectors.py

3. Updated CHAIN_PROMPT.md CONFIRMED DECISIONS section

4. DEV_LOG.md entry for this session

================================================================================
CONSTRAINTS
================================================================================

- Do not break any other engine
- Do not change model/agent.py attributes without documenting in DEV_LOG
- Do not change the simulation loop order without explicit permission
- All new parameters must have defaults that produce sane behavior
- New behavior must produce emergent output — no hardcoded outcomes
