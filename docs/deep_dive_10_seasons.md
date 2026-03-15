# SIMSIV — Deep Dive 10: Seasonal Resource Cycles

## Design Decisions

### A. Seasonal Effect Model
**Decision: Cosine-wave resource cycle with annual tick approximation**
- Since ticks are annual, seasons modulate the resource multiplier via a
  cosine wave: `phase = cos(2π * year / cycle_length)`
- `seasonal_amplitude = 0.3`: resource multiplier varies ±30% around baseline
- `seasonal_cycle_length = 3`: 3-year cycle (peak → lean → lean → peak)
- Phase 1.0 = peak abundance, -0.5 = trough (lean period)
- This creates predictable scarcity that agents can implicitly adapt to
  (through trait selection over generations)

### B. Resource Storage
**Decision: Intelligence-mediated storage efficiency + storage cap**
- Storage cap: 20.0 max resources per agent (prevents runaway accumulation)
- Intelligence bonus on decay rate: smarter agents retain up to 20% more
  resources year-to-year (effective_decay = base_decay + intel * bonus)
- Max retention capped at 90% (can't perfectly preserve everything)
- Creates emergent wealth inequality: intelligent savers accumulate more

### C. Birth Timing
**Decision: Conception modulated by cycle phase**
- `birth_timing_sensitivity = 0.2`: conception chance ±20% based on phase
- Peak years → more births, lean years → fewer births
- Creates natural birth clustering in abundance periods

### D. Seasonal Conflict
**Decision: Lean-phase conflict boost**
- `seasonal_conflict_boost = 0.2`: conflict probability increases up to 20%
  during lean phases (phase < 0)
- Stronger lean phases → stronger conflict boost
- Creates conflict cycles correlated with resource scarcity

### E. What's NOT Implemented
- Environmental memory / carrying capacity depletion (too complex for current model)
- Anticipatory behavior (would need agent-level strategy model)
- Seasonal cooperation boost (existing cooperation sharing already activates
  when agents have resources to share — lean years naturally suppress sharing)
- Multi-year drought cycles beyond configurable cycle_length

## Parameters Added
| Parameter | Default | Description |
|-----------|---------|-------------|
| seasonal_cycle_enabled | True | Enable predictable resource cycles |
| seasonal_amplitude | 0.3 | Peak-to-trough resource variation |
| seasonal_cycle_length | 3 | Years per full cycle |
| resource_storage_cap | 20.0 | Max resources per agent |
| storage_intelligence_bonus | 0.2 | Intelligence reduces storage decay |
| seasonal_conflict_boost | 0.2 | Conflict boost during lean phase |
| birth_timing_sensitivity | 0.2 | Cycle effect on conception |

## Metrics Added
| Metric | Description |
|--------|-------------|
| seasonal_phase | Current cycle phase [-1, 1] |

## Files Changed
- `models/environment.py` — seasonal_phase computation, cycle modulation of resources
- `engines/resources.py` — intelligence-mediated storage, storage cap
- `engines/reproduction.py` — birth timing sensitivity to cycle
- `engines/conflict.py` — lean-phase conflict boost
- `config.py` — 7 DD10 parameters
- `metrics/collectors.py` — 1 DD10 metric
