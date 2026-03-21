# SIMSIV v2 — Dead Ends Log
# Approaches that were tried and failed. Do NOT repeat these.
# Updated by the v2 innovation loop.

---

## DEAD END 1 — n=4 bands is insufficient for between-group selection detection

**What was attempted**: Exp 2 factorial (Free/State x Raid/NoRaid) with 4 bands
per condition, 50 agents/band, 200yr. Originally n=3 seeds, then replicated at n=10.

**Result**: n=3 showed interaction effect +0.039 (false positive). n=10 showed
+0.0004 (p=0.954). Zero effect. All four conditions converge to ~0.505.

**Why this is a dead end**: With only 4 bands, stochastic drift overwhelms any
selection signal. Pearson r on 4 data points is inherently noisy (std ~0.2-0.4).
The Bowles mechanism cannot produce detectable regime-level divergence at this
scale. Bowles's (2006) empirical estimates used n=10-30 groups.

**Do NOT repeat**: Any experiment with n<=4 bands expecting to detect
between-group selection effects on cooperation divergence.

---

## DEAD END 2 — 0.6/0.4 blended fitness proxy

**What was attempted**: Blending demographic fitness (60%) with raid win rate (40%)
into a single between_group_selection_coeff.

**Result**: The blended coefficient was not comparable to Bowles (2006) eq. 1.
Critic flagged it as "the most dangerous scientific error in the document."

**Fix applied**: Split into demographic_selection_coeff and raid_selection_coeff
(Turn 11 post-review fixes).

**Do NOT repeat**: Blending fitness components without citation.
