# Experiment 3 -- Raid Intensity Sweep

## Setup
- FREE_COMPETITION only, 4 bands, 200yr, 3 seeds
- Vary raid_base_probability: 0.1, 0.3, 0.5, 0.7

## Results at year 200

| Raid Prob | Mean Coop | Mean Between Sel | Mean Fst | Mean Violence |
|-----------|----------|-----------------|---------|---------------|
| 0.1 | 0.479 | -0.195 | 0.184 | 0.004 |
| 0.3 | 0.473 | +0.344 | 0.191 | 0.014 |
| 0.5 | 0.466 | +0.271 | 0.216 | 0.010 |
| 0.7 | 0.457 | +0.232 | 0.263 | 0.023 |

## Bowles prediction test

Does higher raid intensity increase between_group_sel_coeff?

**Partially confirmed.** The coefficient transitions from negative (-0.195 at raid_p=0.1)
to positive (+0.344 at raid_p=0.3), confirming that moderate intergroup warfare activates
the Bowles group selection mechanism. However, the coefficient decreases slightly at higher
intensities (0.5, 0.7), suggesting diminishing returns -- possibly because high-intensity
raiding causes enough casualties to reduce the variance between groups.

Fst increases monotonically (0.184 -> 0.263) with raid intensity, confirming that raids
create genuine between-group divergence. Mean cooperation declines slightly (0.479 -> 0.457),
indicating that raiding imposes a net cooperation cost (war is expensive).
