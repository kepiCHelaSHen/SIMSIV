# SIMSIV v2 — Session State
# Current state of the v2 clan simulator build.
# Updated each turn by the innovation loop.

---

## Current State (Turn 6 — 2026-03-20)

TURN: 6
MODE: VALIDATION — ClanSimulation wrapper delivered
MILESTONE: 5+6 complete (session memory + ClanSimulation wrapper + per-band Config)
BRANCH: v2-clan-experiment
TAG: v2-turn-6-pass

### What was built this turn
- ClanSimulation wrapper (models/clan/clan_simulation.py) — 257 lines
- Per-band Config in ClanEngine (band.society.config for intra-band ticks)
- Fission config inheritance fix (daughters inherit parent's institutional regime)
- 24 new tests (tests/test_clan_simulation.py)
- Session memory files (Milestone 5)
- Critic blocking issue + linter critical issue both fixed before commit

### Test status
- 165 tests passing (141 existing + 24 new)
- 3-seed anomaly check PASS (coop_std=0.023, agg_std=0.012)
- No frozen v1 files touched

### Metric baseline (first loop turn)
- inter_band_violence_rate: 0.000 (target 0.02-0.15) — BELOW
- trade_volume_per_band: 0.0 (target 0.10-0.40) — BELOW
- between_group_sel_coeff: 0.633 (target 0.01-0.10) — ABOVE (n=2 degeneracy)

### What next turn should do
1. Run FREE_COMPETITION vs STRONG_STATE divergence experiment (Milestone 6)
2. Measure cooperation divergence across institutional regimes
3. Fix population-level → growth-rate fitness proxy (4 turns deferred)
4. Add per-band trait snapshots to DataFrame export
