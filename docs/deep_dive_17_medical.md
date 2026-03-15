# Deep Dive 17: Medical History and Pathology

## Summary
Added individual medical histories with heritable condition risks, condition
activation/remission cycles, accumulated trauma, and a dedicated pathology engine.
Creates individual-level health variation where lineages develop recognizable
health profiles over generations.

## Heritable Condition Risks (5 new traits)
| Trait | Default | h² | Effect |
|-------|---------|-----|--------|
| cardiovascular_risk | 0.2 | 0.50 | Extra health decay after 40, reduced stamina |
| mental_illness_risk | 0.2 | 0.60 | Erratic behavior (random cooperation/aggression spikes) |
| autoimmune_risk | 0.2 | 0.40 | Increased epidemic vulnerability despite average disease_resistance |
| metabolic_risk | 0.2 | 0.45 | Reduced resource acquisition efficiency |
| degenerative_risk | 0.2 | 0.35 | Accelerated health decay after 50, increased flee threshold |

Initial population mean set to 0.2 (low) so baseline is mostly healthy.

## Condition Activation Model
```
activation_p = condition_activation_base * base_risk * trigger_multipliers
```

Trigger multipliers:
- Chronic resource stress (resources < 3.0): x2.0
- Childhood trauma: x1.5
- Age past 40: x(1 + years_past_40 * 0.05)
- Recent conflict injury: x1.3
- Scarcity event: x1.4
- Metabolic paradox (resources > 8.0, metabolic only): x1.5
- High trauma (mental_illness only): x(1 + trauma_score)

Annual remission probability = 0.15 * (1 - base_risk), if resources adequate.

## Accumulated Trauma
`trauma_score: float [0.0-1.0]` — accumulates from:
- Conflict loss: +0.05
- Partner/offspring death: +0.04
- Chronic resource deprivation: +0.02/year

Recovery: -0.01/year when resources adequate, accelerated by kin support.

Effects:
- trauma > 0.4: mental illness activation more likely
- trauma > 0.8: behavioral instability (20% chance of random aggression spikes)

## Medical History
`medical_history: list[dict]` — bounded to 50 entries.
Events: condition_activated, condition_remitted.
Format: `{year: int, event: str, severity: float}`

## Engine Wiring
- **engines/pathology.py** (NEW): Condition activation, remission, effects, trauma
- **engines/mortality.py**: Autoimmune condition → epidemic vulnerability x2.0
- **engines/conflict.py**: Degenerative → increased flee threshold (+0.15)
- **engines/resources.py**: Metabolic → resource acquisition -15%
- **engines/mating.py**: Active conditions reduce attractiveness signal (EI detects)
- **simulation.py**: Pathology engine at step 6.5 (between mortality and institutions)

## Mate Choice and Health Signals
- Active conditions reduce attractiveness expression (not heritable value)
- High emotional_intelligence enables better detection of hidden conditions
- Creates selection pressure against heritable condition risks

## Config Parameters (12 new)
| Parameter | Default | Description |
|-----------|---------|-------------|
| pathology_enabled | True | Enable pathology system |
| condition_activation_base | 0.02 | Annual base activation probability |
| condition_remission_rate | 0.15 | Annual remission probability |
| trauma_decay_rate | 0.01 | Annual trauma recovery rate |
| trauma_conflict_increment | 0.05 | Trauma per conflict loss |
| trauma_grief_increment | 0.04 | Trauma per kin death |
| cardiovascular_health_decay_boost | 0.005 | Extra health decay when active |
| mental_illness_decision_noise | 0.15 | Random trait spike magnitude |
| autoimmune_epidemic_vulnerability | 2.0 | Epidemic multiplier |
| metabolic_resource_penalty | 0.15 | Resource acquisition reduction |
| degenerative_flee_threshold_boost | 0.15 | Flee threshold increase |
| health_signal_visibility | 0.5 | Condition visibility to mates |

## Metrics Added (7)
- active_conditions_count: total active conditions across population
- avg_trauma_score: mean trauma score
- cardiovascular_prevalence: fraction with active cardiovascular
- mental_illness_prevalence: fraction with active mental illness
- autoimmune_prevalence: fraction with active autoimmune
- metabolic_prevalence: fraction with active metabolic
- degenerative_prevalence: fraction with active degenerative

## Constraints Met
- Condition prevalence LOW in healthy populations (base_risk 0.2, activation_base 0.02)
- Pathology engine lightweight (simple probability checks per agent)
- Medical history bounded to 50 entries
- Condition effects modest (not catastrophic)
- pathology_enabled=False reproduces pre-DD17 behavior
