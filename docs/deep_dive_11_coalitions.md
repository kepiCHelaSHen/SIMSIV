# SIMSIV — Deep Dive 11: Coalition Punishment and Defector Control

## Design Decisions

### A. Third-Party Punishment
- Cooperative agents (cooperation >= 0.6) who trust the target and distrust
  the aggressor may punish after a conflict
- Punisher pays cost: 5% of own resources
- Aggressor penalty: 0.5 resources + 0.1 prestige loss
- Punisher gains 0.02 prestige (altruistic punishment is socially valued)
- One punisher per conflict (prevents pile-on)
- Result: ~2-5 punishments per 50yr (rare but impactful)

### B. Coalition Defense
- When A attacks B, B's allies (trust > 0.65, cooperation > 0.4, health > 0.3)
  may intervene before combat
- Defense probability: base 0.3 * trust_of_target * cooperation_propensity
- Successful defense: aggressor loses 0.03 dominance, defender gains 0.03 prestige
- Trust strengthened between defender and target
- Conflict averted entirely (no combat damage)
- Result: ~2-4 defenses per year (~95 over 50yr)

### C. Ostracism
- Agents with reputation below 0.25 excluded from cooperation sharing
- Result: nearly no agents ostracized in baseline (reputation stays above
  threshold due to DD07 aggregate computation)
- Would activate more in high-violence or low-cooperation scenarios

### D. What's NOT Implemented
- Free-rider detection (adds complexity, existing gossip handles detection)
- Second-order punishment (punishing non-punishers — too complex for v1)
- Coordinated coalition punishment (would need coalition formation model)
- Ostracism effects on mating (reputation already affects mate_value)

## Parameters Added
| Parameter | Default | Description |
|-----------|---------|-------------|
| third_party_punishment_enabled | True | Enable altruistic punishment |
| punishment_willingness_threshold | 0.6 | Min cooperation to punish |
| punishment_cost_fraction | 0.05 | Punisher's resource cost |
| punishment_severity | 0.1 | Resource/prestige loss on punished |
| coalition_defense_enabled | True | Enable ally intervention |
| coalition_defense_probability | 0.3 | Base chance ally intervenes |
| coalition_defense_trust_threshold | 0.65 | Trust required to intervene |
| ostracism_enabled | True | Exclude low-reputation from sharing |
| ostracism_reputation_threshold | 0.25 | Below this = ostracized |

## Metrics Added
| Metric | Description |
|--------|-------------|
| coalition_defenses | Count of ally interventions per tick |
| third_party_punishments | Count of altruistic punishments per tick |
| ostracized_count | Agents below ostracism reputation threshold |

## Files Changed
- `engines/conflict.py` — coalition defense + third-party punishment
- `engines/resources.py` — ostracism exclusion from sharing
- `config.py` — 9 DD11 parameters
- `metrics/collectors.py` — 3 DD11 metrics
