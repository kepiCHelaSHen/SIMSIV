# SIMSIV — CHAIN RUNNER: DD15 through DD23
# Execute all remaining deep dives in sequence.
# Do NOT stop between dives. Do NOT ask for confirmation. NEVER STOP.

================================================================================
INSTRUCTIONS
================================================================================

You are executing the remaining deep dives for SIMSIV in sequence.
Complete each one fully before moving to the next.

For EACH deep dive:
  1. Read the prompt file listed below
  2. Read CHAIN_PROMPT.md, STATUS.md, DEV_LOG.md for current context
  3. Execute the deep dive completely — all deliverables
  4. Update DEV_LOG.md, STATUS.md, CHAIN_PROMPT.md
  5. Run a quick validation:
     python main.py --years 20 --population 100 --seed 42
     to confirm no crashes before proceeding to the next dive
  6. Immediately proceed to the next dive without stopping

================================================================================
EXECUTION ORDER
================================================================================

DIVE 1:  prompts/deep_dive_15_genomics.md
DIVE 2:  prompts/deep_dive_16_development.md
DIVE 3:  prompts/deep_dive_17_medical.md
DIVE 4:  prompts/deep_dive_18_proximity.md
DIVE 5:  prompts/deep_dive_19_migration.md
DIVE 6:  prompts/deep_dive_20_leadership.md
DIVE 7:  prompts/deep_dive_21_resource_types.md
DIVE 8:  prompts/deep_dive_22_life_stages.md
DIVE 9:  prompts/deep_dive_23_intelligence_audit.md

================================================================================
NEVER STOP RULE
================================================================================

Do NOT pause between dives.
Do NOT ask the user if you should continue.
Do NOT wait for confirmation.
If a dive produces a minor issue, fix it and continue.
If a dive produces a crash that cannot be fixed in 3 attempts, log the issue
in DEV_LOG.md, skip that dive, and continue to the next one.

Complete all dives. Log everything. Then report a final summary of all
completed dives, key findings from each, and any dives that were skipped.
