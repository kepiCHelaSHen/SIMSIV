# SIMSIV — Current Status

Phase: G — Dashboard overhaul (in progress)
Last completed: Phase F model quality fixes (19 fixes, 22 tests passing)
Active: 10-seed × 500yr scenario experiment (FREE_COMPETITION vs STRONG_STATE vs EMERGENT_INSTITUTIONS)

## What Is Running Right Now
- Scenario experiment: 3 scenarios × 10 seeds × 500 years
  Testing the central publication claim: do cooperation traits diverge
  between governed vs ungoverned societies at long timescales?

## Phase Summary

### Phase G — Dashboard Overhaul (in progress, 2026-03-15)
  - prompts/dashboard_overhaul.md written (20-block executable prompt)
  - Refactors 111KB app.py into tabs/ + components/ modules
  - Adds: Beliefs tab, Scenario Comparison, Lorenz curve, survivorship
    curve, inter-faction violence matrix, bond duration histogram,
    phase portrait, epidemic bands, export panel, KPI deltas

### Publication Plan (locked, 2026-03-15)
  Central claim: "Institutional governance systematically reduces directional
    selection on heritable prosocial behavioral traits — providing computational
    evidence that institutions and genes are substitutes, not complements,
    in human social evolution."
  Paper 1: Methods paper → JASSS / PLOS ONE
  Paper 2: Findings paper → Evolutionary Human Sciences
  Paper 3: Coevolution claim → Evolution and Human Behavior
  arXiv preprint: after scenario experiments + sensitivity analysis

### Scenario Experiments Run 1 (complete, 2026-03-15)
  5 seeds × 200yr × 10 scenarios. Key findings:
  - ENFORCED_MONOGAMY: violence ▼37%, unmated males ▼65%
  - STRONG_STATE: Gini ▼40%, violence ▼49%, law=0.981
  - EMERGENT_INSTITUTIONS: law self-organizes 0→0.829
  - Cooperation trait IDENTICAL at 200yr across all scenarios (~0.511)
    → 500yr run needed to detect trait divergence
  - RESOURCE_SCARCITY highest cooperation (0.536) — stress-induced
  - ELITE_POLYGYNY near-zero pop growth despite highest lifespan

### Validation (complete, 2026-03-15)
  10 held-out seeds × 200yr × 2 independent runs
  Mean score: 0.934, 0/20 collapses
  Robust: Gini, Mating Inequality, Cooperation, Aggression (10/10 in range)
  Fragile: Violence Death Fraction, Lifetime Births, Pop Growth, Bond Dissolution
  Verdict: MOSTLY ROBUST — suitable for scenario experiments
  Full report: docs/validation.md

### AutoSIM Run 3 (complete, 2026-03-15)
  816 experiments × 150yr × 500pop × 2 seeds (~10.5 hours)
  Best score: 1.000 (first perfect calibration in project history)
  Key parameter shifts from Run 1 (pre-Phase F):
    female_choice_strength: 0.882 → 0.340 (dramatic reversal)
    subsistence_floor: 0.300 → 1.173 (dramatic reversal)
    child_investment_per_year: 0.993 → 0.350 (dramatic reversal)
  Reversals confirm Phase F bug fixes were scientifically material.

### Phase F — Model Quality Fixes (complete, 2026-03-15)
  19 fixes across all engines. 22 tests passing.
  Critical: storage bonuses active, cross-sex conflict enabled,
    mental illness no longer mutates heritable traits,
    institutional drift enabled by default (drift_rate=0.01)
  High: EPC kin networks, bond dissolution symmetry, elite privilege
    bidirectional, age consistency, status setter, EPC survival
  Medium: symmetric bond strengthening, wider fertility range,
    partner-driven destabilization, cooperation norm restriction

### Phase E — Engineering Hardening (complete, 2026-03-15)
  14 fixes. Per-simulation IdCounter, event window, partner index,
  logging module, Config validation, test suite (4 files, 22 cases),
  dashboard split, .gitignore, .python-version

## System State
  - 35 heritable traits, 5 belief dims, 4 skill domains — DD01-DD27 complete
  - 9 engines, ~257 config params, ~130 metrics per tick
  - 27 deep dives complete — docs/deep_dive_*.md
  - AutoSIM: Run 3 complete (816 exp), best score 1.000
  - Calibration: autosim/best_config.yaml
  - Validation: 0/20 collapses, mean 0.934 on held-out seeds

## Next Steps (in order)
  1. Wait for 10-seed × 500yr run to complete — analyze trait divergence
  2. Complete Phase G dashboard overhaul
  3. Write docs/sensitivity_analysis.md (from autosim journal data)
  4. Apply best_config defaults to config.py
  5. Tag v1.0-band-simulator on git, create Zenodo archive
  6. Draft Paper 1 (methods paper)

Updated: 2026-03-15
