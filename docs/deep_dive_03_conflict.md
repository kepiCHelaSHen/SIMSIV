# Deep Dive 03 — Conflict Model: Design Decisions

## Overview

DD03 overhauled the conflict engine to add network deterrence, flee response,
scaled consequences, subordination mechanics, bystander reputation updates,
and proper violence death logging. The goal was to make violence a credible
selection pressure with emergent social dynamics.

## Design Decisions

### A. Conflict Initiation

**Decision**: Keep 5-trigger model (jealousy, resource pressure, status drive,
random baseline, institutional suppression) but add network deterrence and
subordination dampening.

- Agents embedded in dense trust networks (many allies with trust > 0.5)
  are less likely to initiate: `total_p *= 1.0 / (1.0 + own_allies * 0.05)`
- Recent conflict losers enter subordination cooldown (default 2 years),
  reducing initiation probability by 50%: `total_p *= subordination_dampening`
- Cooperation propensity dampens aggression: `total_p *= (1.0 - coop * 0.3)`
- Probability capped at 0.5 to prevent runaway violence

### B. Target Selection

**Decision**: Weighted probabilistic with 5 factors:

1. **Trust-based**: Low trust = more likely target (1.5 - trust)
2. **Rival detection**: Agents sharing a mate partner get 3x weight
3. **Status challenge**: Similar status (|diff| < 0.2) → 1.5x weight
4. **Resource envy**: Targets richer by 1.5x → 1.3x weight (NEW)
5. **Network deterrence**: Well-connected targets are harder to pick:
   `weight *= 1.0 / (1.0 + target_allies * network_deterrence_factor)`
6. **Strength assessment**: Low risk_tolerance aggressors avoid healthier
   targets: `weight *= 0.5` if target health > 1.2x aggressor health (NEW)

Same-sex-only conflict maintained (intra-sex competition).

### C. Flee Response (NEW)

**Decision**: Targets with low risk_tolerance can avoid combat entirely.

- Triggers when `target.risk_tolerance < flee_threshold` (default 0.3)
- Flee chance: `(1.0 - target.risk_tolerance) * 0.5`
- On flee: small status shift (+0.02 aggressor, -0.02 target), no violence
- Creates evolutionary niche for conflict-avoidant strategies
- Flee events logged separately for tracking

### D. Combat Resolution

**Decision**: Power-based probabilistic with resource advantage.

Combat power formula:
```
power = aggression * 0.25 + status * 0.20 + health * 0.25
      + risk_tolerance * 0.15 + resource_edge * combat_resource_factor
      + intelligence * 0.05 + ally_bonus
```

- Resource edge: `min(resources / 20, 1.0)` — wealthy fight better
- Ally bonus: `min(allies, 3) * 0.03` — allies boost confidence
- Win probability: `agg_power / (agg_power + tgt_power + 0.01)`

### E. Scaled Consequences (NEW)

**Decision**: Power differential determines consequence severity.

- `power_diff = |agg_power - tgt_power| / (agg_power + tgt_power + 0.01)`
- `scale_factor = 0.7 + power_diff * 1.6`
  - Close fights (diff ~0): scale 0.7 (reduced consequences)
  - Stomps (diff ~0.5): scale 1.5 (amplified consequences)
- Loser health cost: `violence_cost_health * scale_factor`
- Loser resource loss: `resources * violence_cost_resources * scale_factor`
- Winner takes 50% of loser's resource loss
- Status shift scaled by `(1.0 + power_diff)`
- Winner also suffers minor health cost (0.3x base)

### F. Subordination (NEW)

**Decision**: Losers enter a cooldown period with reduced aggression.

- On loss: `conflict_cooldown = max(current, subordination_cooldown_years)` (default 2)
- Cooldown decays 1/year at start of conflict engine tick
- During cooldown: `total_p *= subordination_dampening` (default 0.5)
- Creates dominance hierarchy dynamics — recent losers are submissive
- 4.5% of living agents are in cooldown at any given time (baseline)

### G. Violence Death (FIX)

**Decision**: Emit proper "death" type events when violence kills.

- Pre-DD03 bug: conflict engine called `loser.die("violence")` but only
  emitted "conflict" events. Metrics collector counted deaths by type=="death".
- Result: 0 violence deaths in metrics despite violence being a death cause.
- Fix: on lethal outcome, emit both a "death" event and a "conflict" event.
- Death chance now scales with power differential:
  `effective_death_chance = violence_death_chance * (0.5 + power_diff)`

### H. Bystander Trust Updates (NEW)

**Decision**: Witnesses to violence adjust their trust of the aggressor.

- Up to `bystander_count` (default 3) nearby agents witness each conflict
- Each bystander: `remember(aggressor, -0.08)` (distrust the aggressor)
- Allied bystanders (trust of target > 0.6): additional `remember(aggressor, -0.1)`
- Creates social cost of violence beyond the direct combatants
- Bystander trust is configurable via `bystander_trust_update` flag

### I. Pair Bond Destabilization

**Decision**: Retained from v1, no changes needed.

- Both fighters' pair bonds have a dissolution chance: `aggression * 0.15`
- Partners who leave remember the fighter negatively (-0.25)

### J. Institutional Punishment

**Decision**: Retained from v1, activated when `violence_punishment_strength > 0`.

- Reputation penalty: `punishment_strength * 0.1`
- Resource fine: `punishment_strength * 0.5`
- Creates institutional deterrence layer on top of social deterrence

## Results

### Baseline (500 pop, 100yr)

| Metric | Pre-DD03 | Post-DD03 |
|--------|----------|-----------|
| Violence rate | 0.057 | 0.056 |
| Violence deaths | 0 (bug) | 159 |
| Flee events | 0 (n/a) | 72 |
| Agents in cooldown | 0 (n/a) | 4.5% |
| Avg aggression | 0.47 | 0.47 |
| Avg cooperation | 0.56 | 0.56 |

### Scenario Comparison

| Scenario | Pop | V-deaths | Conflicts | Flees | Cooldown | Aggression |
|----------|-----|----------|-----------|-------|----------|------------|
| BASELINE | 623 | 159 | 6078 | 72 | 28 | 0.472 |
| STRICT_MONOGAMY | 912 | 118 | 4647 | 31 | 80 | 0.483 |
| ELITE_POLYGYNY | 1248 | 144 | 5182 | 32 | 122 | 0.467 |
| HIGH_VIOLENCE | 490 | 275 | 4578 | 54 | 48 | 0.434 |

### Key Findings

1. **Violence death logging fixed**: 159 violence deaths now properly tracked
   (was 0 due to event type bug)
2. **HIGH_VIOLENCE shows selection against aggression**: 0.434 vs 0.472 baseline,
   confirming violence creates real evolutionary pressure when costs are high
3. **HIGH_VIOLENCE population stable at 490**: no longer collapses (was 71 pre-DD02)
4. **Flee mechanic active**: 72 baseline flee events, creating a niche for
   risk-averse agents
5. **Subordination working**: 4.5% in cooldown, creating temporary dominance
   hierarchies

## New Config Parameters (9)

| Parameter | Default | Description |
|-----------|---------|-------------|
| flee_threshold | 0.3 | risk_tolerance below which flee is possible |
| network_deterrence_factor | 0.1 | per-ally reduction in targeting weight |
| bystander_trust_update | True | witnesses update trust ledgers |
| bystander_count | 3 | max witnesses per conflict |
| subordination_cooldown_years | 2 | years of reduced aggression after loss |
| subordination_dampening | 0.5 | conflict prob multiplier during cooldown |
| combat_resource_factor | 0.1 | resource advantage weight in combat |
| winner_status_scale | 0.05 | base status gain for winner |
| loser_status_scale | 0.05 | base status loss for loser |

## New Metrics (4)

| Metric | Description |
|--------|-------------|
| flee_events | Number of flee events per tick |
| violence_deaths | Violence-caused deaths per tick |
| punishment_events | Institutional punishment events per tick |
| agents_in_cooldown | Agents in subordination cooldown |
