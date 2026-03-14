# SIMSIV — PROMPT: ITERATION TEMPLATE
# File: D:\EXPERIMENTS\SIM\prompts\iteration_template.md
# Use: Copy, fill in the CHANGE REQUEST section, send to Claude

================================================================================
CONTEXT INJECTION — READ FIRST
================================================================================

You are iterating SIMSIV. Read CHAIN_PROMPT.md and all existing code before
making any changes. Do not refactor unless explicitly asked.

================================================================================
CHANGE REQUEST
================================================================================

TYPE: [ BUG FIX / NEW FEATURE / ENHANCEMENT / REFACTOR / PARAMETER TUNING ]

DESCRIPTION:
  [ Describe exactly what needs to change and why ]

FILES LIKELY AFFECTED:
  [ List files you think need to change ]

ACCEPTANCE CRITERIA:
  [ How do we know this is done correctly? ]

DO NOT CHANGE:
  [ List anything that must not be touched ]

================================================================================
INSTRUCTIONS
================================================================================

1. Make targeted, minimal changes only
2. Explain what you changed and why
3. If a bug: show the root cause before fixing
4. If a new feature: confirm it matches rules_spec.md before implementing
5. Update DEV_LOG.md with a new entry
6. Update CHAIN_PROMPT.md CONFIRMED DECISIONS if any design changed
7. Run a quick sanity check: does python main.py still work after your change?
