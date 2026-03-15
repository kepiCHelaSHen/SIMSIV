# SIMSIV — Deep Dive 08: Prestige vs Dominance

## Core Design Decision
Split `current_status` into two distinct tracks:
- **prestige_score**: earned through cooperation, intelligence, networks, reputation
- **dominance_score**: earned through conflict victories, aggression, intimidation

`current_status` retained as a backward-compatible computed property:
`current_status = prestige_score * 0.6 + dominance_score * 0.4`

## Design Decisions

### A. Prestige Acquisition
- Cooperation propensity (30%), intelligence (20%), existing prestige (20%),
  network size (4%/ally), reputation (10%)
- Prestige pool = 60% of status resources (cooperation is social capital)
- Prestige decays at 1%/yr (slow — built reputation persists)
- Aggressors lose prestige (-0.02 per conflict initiated)

### B. Dominance Acquisition
- Status drive (30%), aggression (20%), existing dominance (30%), health (10%),
  risk tolerance (10%)
- Dominance pool = 40% of status resources
- Dominance decays at 3%/yr (faster — requires ongoing enforcement)
- Conflict winners gain dominance, losers lose it (scaled by power differential)
- Flee events shift dominance (aggressor gains, target loses)

### C. Interaction Effects
- Both tracks contribute to overall status but in different contexts
- Combat: dominance weighted 70%, prestige 30%
- Mate value: prestige weighted 60%, dominance 40%
- Resource competition: prestige weighted 70%, dominance 30%
- Elite privilege: uses combined score (prestige + dominance)
- High prestige + low dominance = respected elder
- Low prestige + high dominance = feared bully
- Both high = warrior-chief (rare, requires cooperation AND aggression)

### D. Engine Rewiring
- **Conflict**: combat power uses dominance-weighted status; victory shifts
  dominance; aggressor loses prestige; dominance provides fear-based deterrence
- **Resources**: competitive weight uses prestige-weighted status; Phase 5
  distributes prestige and dominance separately with different pools
- **Mating**: mate_value uses prestige-weighted status; contests use dominance;
  high-status polygyny check uses combined score
- **Institutions**: inheritance transfers prestige (not dominance)

### E. What's NOT Implemented
- Dominance instability (losing harder than gaining) — adds complexity
- Prestige display multiplier (witnessed generosity) — would need bystander
  cooperation events
- Institutional boost from prestige-led populations — needs longer-term testing
- Prestige/dominance as heritable traits — they're earned, not genetic

## Parameters Added
| Parameter | Default | Description |
|-----------|---------|-------------|
| prestige_decay_rate | 0.01 | Annual prestige decay |
| dominance_decay_rate | 0.03 | Annual dominance decay (faster) |
| prestige_weight_in_mate_value | 0.6 | Status weight from prestige in mate choice |
| dominance_weight_in_combat | 0.7 | Status weight from dominance in combat |
| dominance_deterrence_factor | 0.3 | High dominance reduces targeting |

## Metrics Added
| Metric | Description |
|--------|-------------|
| avg_prestige | Mean prestige score of living agents |
| avg_dominance | Mean dominance score of living agents |
| prestige_gini | Gini coefficient of prestige distribution |
| dominance_gini | Gini coefficient of dominance distribution |
| prestige_dominance_corr | Correlation between prestige and dominance |

## Files Changed
- `models/agent.py` — prestige_score, dominance_score fields; current_status as computed property
- `engines/conflict.py` — dominance in combat, deterrence, status shifts
- `engines/resources.py` — prestige in competition, dual-track status distribution
- `engines/mating.py` — prestige in mate choice, dominance in contests
- `engines/institutions.py` — prestige inheritance
- `config.py` — 5 DD08 parameters
- `metrics/collectors.py` — 5 DD08 metrics

## Validation Results (200 pop, 30yr, seed=42)
- Avg prestige: 0.757, avg dominance: 0.762
- Prestige Gini: 0.198, Dominance Gini: 0.198
- Prestige-dominance correlation: 0.886 (high in baseline — would diverge
  under specialized scenarios like HIGH_VIOLENCE or STRONG_STATE)
- Population stable at 315 (no regression from status changes)
