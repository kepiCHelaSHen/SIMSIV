# SIMSIV v2 — Session State
# Updated: Turn 7 (2026-03-21)

TURN: 7
MILESTONE: 6 complete (Divergence Experiment)
MODE: EXPLORATION (returning to VALIDATION next turn)
BRANCH: v2-clan-experiment
TAG: v2-turn-7-pass

### Key findings from Turn 7
- Growth-rate fitness proxy DELIVERED (4-turn deferral resolved)
- Divergence experiment: INCONCLUSIVE at n=2 bands, 50yr
  - Seed 42: Free band went extinct
  - Seeds 137, 271: Free cooperation ~0.04 higher (directional Bowles/Gintis)
- Violence rate and trade volume still zero — interactions too rare
- Institutional drift works: Free bands drift law_strength from 0.0 to ~0.15

### Metric status
- inter_band_violence_rate: 0.000 (target 0.02-0.15) — BELOW TARGET
- trade_volume_per_band: 0.0 (target 0.10-0.40) — BELOW TARGET
- between_group_sel_coeff: 0.500 (target 0.01-0.10) — DEGENERATE (n=2)

### What next turn should do
1. VALIDATION MODE — increase to n=4 bands (2 Free + 2 State)
2. Investigate why inter-band interactions produce zero trade/violence metrics
3. Consider increasing base_interaction_rate or reducing distance
4. Run 200yr experiment with 4 bands for non-degenerate selection coefficients
