# Experiment 1 — Statistical Power (n=6 seeds)

## Setup
- 4 bands: 2 Free (law=0.0) + 2 State (law=0.8)
- 200 years, 50 agents/band
- Tuned ClanConfig: raid_base_probability=0.50, raid_scarcity_threshold=20.0, base_interaction_rate=0.8

## Per-seed results at year 200

| Seed | Coop (Free) | Coop (State) | Divergence | Direction | Between Sel | Fst |
|------|------------|-------------|-----------|-----------|-------------|-----|
| 42 | 0.493 | 0.493 | +0.001 | ~equal | 0.152 | 0.383 |
| 137 | 0.538 | 0.524 | +0.014 | Free > State | 0.031 | 0.127 |
| 271 | 0.400 | 0.454 | -0.054 | State > Free | 0.009 | 0.189 |
| 512 | 0.521 | 0.534 | -0.013 | State > Free | -0.167 | 0.380 |
| 999 | 0.515 | 0.490 | +0.025 | Free > State | 0.203 | 0.205 |
| 1337 | 0.544 | 0.590 | -0.045 | State > Free | -0.139 | 0.531 |

## Summary
- Mean divergence (Free - State): -0.012 +/- 0.029
- Free > State: 2/6 seeds
- State > Free: 3/6 seeds
- ~Equal: 1/6 seeds
