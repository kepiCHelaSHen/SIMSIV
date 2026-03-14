# SIMSIV — PROMPT: DEBUG TEMPLATE
# File: D:\EXPERIMENTS\SIM\prompts\debug_template.md
# Use: Copy, fill in ERROR DESCRIPTION section, send to Claude

================================================================================
CONTEXT INJECTION — READ FIRST
================================================================================

You are debugging SIMSIV. Read CHAIN_PROMPT.md before diagnosing.

================================================================================
BUG REPORT
================================================================================

ERROR TYPE: [ Exception / Wrong Output / Performance / Logical Error ]

ERROR MESSAGE (paste exact traceback if applicable):
  [ PASTE HERE ]

HOW TO REPRODUCE:
  [ Command that triggers the error ]
  [ e.g.: python main.py --scenario ENFORCED_MONOGAMY --seed 42 ]

EXPECTED BEHAVIOR:
  [ What should happen ]

ACTUAL BEHAVIOR:
  [ What actually happens ]

LAST CHANGE MADE:
  [ What was changed before this error appeared ]

================================================================================
DEBUGGING INSTRUCTIONS
================================================================================

1. Read the traceback carefully — identify the exact line and file
2. Read that file and the surrounding context
3. Identify the root cause (not just where it throws, but WHY)
4. Fix the minimum code needed to resolve it
5. Do not change unrelated code
6. Verify: does python main.py run cleanly after the fix?
7. Update DEV_LOG.md with a DEBUG entry explaining root cause and fix
