# Experiment 1 — Statistical Power (n=6 seeds)

## Setup
- 4 bands: 2 Free (law=0.0) + 2 State (law=0.8)
- 200 years, 50 agents/band
- Tuned ClanConfig: raid_base_probability=0.50, raid_scarcity_threshold=20.0, base_interaction_rate=0.8

## Per-seed results at year 200

| Seed | Coop (Free) | Coop (State) | Divergence | Direction | Between Sel | Fst |
|------|------------|-------------|-----------|-----------|-------------|-----|
| 42 | 0.450 | 0.499 | -0.049 | State > Free | 0.003 | 0.134 |
| 137 | 0.510 | 0.510 | +0.000 | ~equal | 0.164 | 0.192 |
| 271 | 0.374 | 0.441 | -0.066 | State > Free | -0.017 | 0.269 |
| 512 | 0.500 | 0.519 | -0.019 | State > Free | -0.309 | 0.331 |
| 999 | 0.593 | 0.510 | +0.083 | Free > State | -0.435 | 0.304 |
| 1337 | 0.561 | nan | +nan | ~equal | -0.069 | 0.315 |

## Summary
- Mean divergence (Free - State): -0.010 +/- 0.052
- Free > State: 1/5 seeds
- State > Free: 3/5 seeds
- ~Equal: 1/5 seeds
