# V1 Perfect Pass — Design Specification

**Goal:** Make the v1 band simulator bulletproof for JASSS review by fixing known bugs, auditing every coefficient, building a prompt-to-code provenance log, and proving stability via adversarial perturbation sweeps.

**Branch:** `v1-perfect` from tag `v1.0-paper1-submitted`

**Scope:** v1 only (9 engine files, 4 test files, 27 deep dive docs). v2 clan layer is out of scope.

---

## Phase 0: Remediation (Clean Build)

Fix 3 known issues from STATUS.md before any audit work:

1. **getattr false defaults** — `engines/conflict.py` lines 161, 197, 549 use `getattr(config, attr, False)` for config attributes that DO exist (`coalition_defense_enabled`, `leadership_enabled`, `third_party_punishment_enabled`). These are all defined in `config.py` with `bool = True` defaults. The getattr masks potential future breakage. Fix: replace with direct `config.attr` access so missing attributes raise `AttributeError` immediately.

2. **Missing bond_dissolved event** — `engines/conflict.py` lines 500-512 break pair bonds during conflict but emit no event. `engines/mating.py` line 110 emits `{type: "bond_dissolved", ...}` for natural dissolution. Conflict-caused breaks must emit the same event type with `reason: "conflict_break"` and both agent UIDs.

3. **rng.choice on object list** — `engines/conflict.py` line 489 passes a Python list of Agent objects to `rng.choice()`. Numpy converts this to an object array (fragile, version-dependent). Fix: use `rng.choice(len(bystander_pool), ...)` and index into the list.

**Gate:** All 4 existing test files pass (`test_smoke.py`, `test_society.py`, `test_config.py`, `test_id_counter.py`).

---

## Phase 1: Deep Audit

Catalog every hardcoded coefficient across 9 v1 engine files:
- `engines/conflict.py` (590 lines)
- `engines/institutions.py`
- `engines/mating.py`
- `engines/mortality.py`
- `engines/pathology.py`
- `engines/reproduction.py`
- `engines/reputation.py`
- `engines/resources.py`
- `engines/__init__.py`

For each coefficient, record:
- Value, line number, variable name
- Which deep dive doc (DD01-DD27) specified it
- Literature source (author, year, specific claim)
- Classification: **GROUNDED** (literature-backed) / **CALIBRATED** (AutoSIM-tuned) / **UNGROUNDED** (AI-inferred, no external source)

Output: `docs/v1_coefficient_audit.md`

---

## Phase 2: Provenance Log

For each coefficient in the audit catalog, trace the full chain of custody:

```
Literature citation → Deep Dive design doc → Git commit (SHA) → Code file:line
```

Reconstruct from:
- 27 deep dive docs (`docs/deep_dive_*.md`)
- Git commit history on the v1 branch
- `devlog/DEV_LOG.md` session logs
- `CHAIN_PROMPT.md` confirmed design decisions

Output: `docs/v1_provenance_log.md` — novel "chain of custody" artifact for JASSS methodology section.

---

## Phase 3: Adversarial Critic

Automated perturbation sweep script:

For each coefficient from the Phase 1 audit:
1. Run N seeds (suggest N=10) at baseline value
2. Run N seeds at +20% perturbation
3. Run N seeds at -20% perturbation
4. For each of 9 calibration metrics, compute σ across the 3 conditions
5. **Gate: σ ≤ 0.030** — coefficients exceeding this are flagged for architectural review

Output:
- `scripts/v1_stability_sweep.py` — automated sweep runner
- `docs/v1_stability_report.md` — results with pass/fail per coefficient

---

## Success Criteria

- All existing tests pass after Phase 0 fixes
- Every coefficient in 9 engine files is cataloged (Phase 1)
- Every coefficient has a provenance chain or UNGROUNDED flag (Phase 2)
- Every coefficient has a stability score with σ ≤ 0.030 gate applied (Phase 3)
- Failing coefficients are explicitly listed for architectural review
