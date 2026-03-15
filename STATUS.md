# SIMSIV — Current Status

Phase: E.1 COMPLETE — Model quality review (25 fixes across all engines)
Previous phase: Phase E engineering hardening
Next step: Re-run autosim calibration with corrected model, then v2 multi-band

## Phase E.1 — Model Quality Review (2026-03-15)

### Critical fixes (4)
- Resource storage intelligence bonuses now apply when resource_types_enabled=True
- Conflict targeting allows cross-sex violence (0.3x weight) — domestic violence pathway
- Mental illness no longer mutates heritable traits — uses trauma_score instead
- Institutional drift enabled by default (drift_rate=0.01, emergent_institutions=True)

### High fixes (6)
- EPC children use social (not genetic) parent_ids — coherent kin networks
- Bond dissolution penalizes both partners' quality, not just male
- Elite privilege ratchet now bidirectional — can decrease when hierarchy_belief drops
- Age increment moved to simulation.py — consistent age across all engines per tick
- current_status setter preserves prestige/dominance ratio (no longer corrupts)
- EPC child survival uses social_father explicitly

### Medium fixes (7)
- Bond strengthening is now symmetric (both partners updated)
- fertility_base range widened [0.4, 1.0] from [0.6, 1.0] — stronger selection
- Bond destabilization uses partner's jealousy, not fighter's aggression
- Cooperation norm boost restricted to agents who actually shared resources
- EPC gap formula uses absolute difference (no division by near-zero)
- Redundant dead-agent ledger cleanup removed (single efficient pass)
- Resource cubing documented (kept — produces realistic Gini)

### Low fixes (2)
- mate_value age curve now peaks at 27, declines after 35 (was flat 15-50)
- Death curve documented as intentionally ad hoc (kept)

## System State
- 35 heritable traits, 5 belief dims, 4 skill domains — DD01-DD27 complete
- 9 engines, ~257 config params, ~130 metrics per tick
- Institutional drift now active by default — law_strength self-organizes
- All known model quality bugs fixed. 22 tests passing.
- AutoSIM calibration should be re-run (model parameters changed)

Updated: 2026-03-15
