# SIMSIV — Deep Dive 12: Status Signaling

## Design Decisions

### Honest Signal: Resource Display
- Agents with resources > 5.0 and cooperation > 0.3 invest in display
- Cost: 5% of resources per year (real cost = honest signal)
- Benefit: prestige gain proportional to display cost
- Creates selection for: resource efficiency + cooperation

### Dishonest Signal: Dominance Bluff
- Low-dominance, risk-tolerant, aggressive agents attempt bluffs (5%/yr)
- Detection: intelligence-gated, 30% base rate * observer intelligence
  * existing distrust
- Caught: major reputation loss (0.15) + prestige loss (0.05)
- Success: temporary dominance boost (+0.05)
- Creates selection pressure: intelligence (detection) vs risk_tolerance (bluffing)

### What's NOT Implemented
- Generosity display (already captured by cooperation sharing + prestige)
- Perceived mate_value layer (too complex — signals affect prestige/dominance
  which already feed into mate_value)
- Institutional signal verification (low payoff)
- Costly handicap principle (interesting but complex for v1)

## Parameters Added
| Parameter | Default | Description |
|-----------|---------|-------------|
| signaling_enabled | True | Enable signaling mechanics |
| resource_display_fraction | 0.05 | Resources spent on display |
| resource_display_prestige_boost | 0.03 | Prestige per display unit |
| bluff_base_probability | 0.05 | Annual bluff attempt rate |
| bluff_detection_base | 0.3 | Base detection probability |
| bluff_caught_reputation_loss | 0.15 | Reputation hit when caught |

## Metrics: bluff_attempts, bluff_detections

## Files Changed
- `engines/resources.py` — signaling phase (display + bluff)
- `config.py` — 6 DD12 parameters
- `metrics/collectors.py` — 2 DD12 metrics
