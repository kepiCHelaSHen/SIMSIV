# Experiment 5 -- Migration Rate Sweep

## Setup
- Free vs State, 4 bands, 200yr, 3 seeds
- Vary migration_rate_per_agent: 0.001, 0.005, 0.01, 0.05

## Results at year 200

| Migration Rate | Fst (prosocial) | Divergence (F-S) | Between Sel |
|---------------|----------------|-----------------|-------------|
| 0.001 | 0.219 | -0.005 | +0.056 |
| 0.005 | 0.229 | -0.003 | +0.050 |
| 0.010 | 0.218 | -0.001 | +0.127 |
| 0.050 | 0.325 | -0.052 | +0.093 |

## Population genetics prediction

Higher migration -> lower Fst -> weaker between-group selection.

**NOT CONFIRMED.** Fst INCREASES with migration rate (0.219 -> 0.325), contrary to the
standard Wright island-model prediction. The divergence also increases in magnitude
(-0.005 -> -0.052), driven by the highest migration rate.

Possible explanations:
1. High migration destabilizes band demographics (emigration shrinks bands), amplifying
   stochastic drift and increasing Fst
2. 200 years is insufficient for the homogenizing effect of gene flow to overcome
   founder-effect-driven divergence in bands this small
3. The per-agent migration rate of 0.05 (5% annual) is extreme -- approximately 10x the
   ethnographic estimate (Wiessner 1982) -- and may push bands below viable size
4. With only 4 bands, Fst sampling noise exceeds the signal

**This anomaly requires investigation before publication.**
