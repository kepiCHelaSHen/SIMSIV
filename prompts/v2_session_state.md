# SIMSIV v2 — Session State
# Current state of the v2 clan simulator build.
# Updated each turn by the innovation loop.

---

## Current State (Turn 6 — 2026-03-20)

TURN: 6
MODE: VALIDATION — building ClanSimulation wrapper (known infrastructure)
MILESTONE: 6 (ClanSimulation wrapper + per-band Config) — in progress
BRANCH: v2-clan-experiment

### What was built this turn
- ClanSimulation wrapper (models/clan/clan_simulation.py)
- Per-band Config support in ClanEngine (band.society.config used for intra-band ticks)
- 24 new tests (tests/test_clan_simulation.py)
- Session memory files (this file + v2_dead_ends.md) — Milestone 5

### Test status
- 165 tests passing (141 existing + 24 new)
- No frozen v1 files touched

### Per-band Config approach
- Each Band is constructed with its own Config object
- ClanEngine.tick() reads band.society.config for intra-band dynamics
- Enables FREE_COMPETITION (law_strength=0.0) vs STRONG_STATE (law_strength=0.8)
- Verified: resource_abundance and law_strength diverge between bands

### What next turn should do
1. Run first FREE_COMPETITION vs STRONG_STATE experiment (50yr, 3 seeds)
2. Measure cooperation divergence between bands under different institutional regimes
3. Add per-band trait snapshots to DataFrame export (mean cooperation per band)
4. Consider fitness proxy fix (growth rate vs population size)

### Council consensus (from Turn 5)
- Both GPT + Grok flagged: ClanSimulation wrapper needed (✅ done)
- Both flagged: per-band institutional differentiation needed (✅ done)
- Population size fitness proxy concern (deferred — not blocking)
