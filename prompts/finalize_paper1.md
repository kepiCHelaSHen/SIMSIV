# SIMSIV — Paper 1 Final Polish + Rename
# Executable Chain Prompt for Claude Code CLI
# Run: claude --dangerously-skip-permissions < prompts\finalize_paper1.md
# Applies 3 last-mile fixes from GPT final review + renames paper file
# Estimated run time: 5 minutes

================================================================================
INSTRUCTIONS FOR CLAUDE CODE
================================================================================

Apply three small targeted edits to the paper. Then rename the file.
Do NOT change anything else. No rewrites, no new content beyond what is
specified here.

READ THIS FILE FIRST:
  D:\EXPERIMENTS\SIM\docs\paper1_draft.md

================================================================================
FIX 1 — ADD REPRODUCIBILITY STATEMENT
================================================================================

In Section 3 (Calibration and Validation), find the final sentence of
Section 3.5 Known Limitations. It ends with something like:
  "...rather than precise benchmarks."

AFTER that sentence, at the end of Section 3.5, add this paragraph:

  "**Reproducibility.** All experiments reported in this paper can be
   reproduced exactly using the scripts in the repository's experiments/
   directory. Scenario configurations, the calibration pipeline, and the
   AutoSIM optimizer are included in full. The calibrated parameter file
   (autosim/best_config.yaml) and the full 816-experiment calibration journal
   (autosim/journal.jsonl) are committed to the repository. Given the same
   seed, the simulation produces identical results. Code and data are available
   at https://github.com/kepiCHelaSHen/SIMSIV"

================================================================================
FIX 2 — CLARIFY COOPERATION TRAIT INITIALIZATION
================================================================================

In Section 5.5 (Additional findings), in the expanded cooperation attractor
section, find this sentence:
  "cooperation starts at 0.5 by initialization"

REPLACE with:
  "cooperation is initialized from the multivariate normal distribution
   described in Section 2.3, with population mean 0.5 and variance 0.1
   prior to correlation transformation"

================================================================================
FIX 3 — CHANGE "UNIVERSAL" TO "ROBUST"
================================================================================

In Section 5.5, in the cooperation attractor section, find:
  "suggests that band-level societies may exhibit a universal cooperation
   equilibrium"

REPLACE with:
  "suggests that band-level societies may exhibit a robust cooperation
   equilibrium"

================================================================================
RENAME THE FILE
================================================================================

After applying all three fixes, save the revised content to:
  D:\EXPERIMENTS\SIM\docs\simsiv_calibrated_abm_gene_culture_coevolution.md

Then DELETE the old file:
  D:\EXPERIMENTS\SIM\docs\paper1_draft.md

Also update any internal references in other docs that mention paper1_draft.md:
  D:\EXPERIMENTS\SIM\docs\paper1_submission_notes.md
  D:\EXPERIMENTS\SIM\STATUS.md
  D:\EXPERIMENTS\SIM\CHAIN_PROMPT.md

In each of those files, find any occurrence of "paper1_draft.md" and replace
with "simsiv_calibrated_abm_gene_culture_coevolution.md"

================================================================================
VERIFICATION
================================================================================

Before finishing, confirm:
  [ ] Fix 1 applied — reproducibility paragraph present in Section 3.5
  [ ] Fix 2 applied — initialization sentence updated
  [ ] Fix 3 applied — "universal" → "robust"
  [ ] New file exists: docs/simsiv_calibrated_abm_gene_culture_coevolution.md
  [ ] Old file deleted: docs/paper1_draft.md
  [ ] References updated in submission notes, STATUS.md, CHAIN_PROMPT.md
  [ ] Word count unchanged (should still be ~8,300 words, ±50 for the additions)

Print a summary of what was changed.

================================================================================
END OF FINALIZATION PROMPT
================================================================================
