# Deep Dive 01: Mating System

## Design Decisions

### Female mate choice model
- Probabilistic weighted selection from available males
- Mate value = f(health, current_status, current_resources, age, attractiveness)
- `female_choice_strength` slider: 0.0 = random pairing, 1.0 = pure best-available
- Age-dependent choosiness: older females slightly less selective (`female_choosiness_age_effect = -0.01/yr` past 30)
- Stronger aggression penalty (0.5) and cooperation bonus (0.4) in female evaluation

### Male competition model
- Probabilistic contest when multiple males target the same female
- Power = status + aggression weighted
- `male_contest_injury_risk = 0.05` — physical cost to competition
- `male_competition_mode = "probabilistic"` (alternatives: tournament, display)

### Pair bond dynamics
- `partner_ids` list + `pair_bond_strengths` dict (replaces single `pair_bond_id`)
- Bond helpers: `is_bonded`, `add_bond`, `remove_bond`, `bond_count`, `primary_partner_id`
- Bond strength grows over time (`pair_bond_growth_rate = 0.02/yr`)
- Dissolution driven by: low resources, health decline, better alternative, jealousy
- Centralized bond cleanup in mating engine (`_clean_stale_bonds`)

### Infidelity and paternity
- Extra-pair copulation (EPC): mate-value-weighted male selection
- `infidelity_base_rate = 0.05`, modulated by female mate value gap
- Paternity uncertainty: males reduce investment when uncertain (`paternity_certainty_threshold = 0.7`)
- `jealousy_detection_rate = 0.4` — probability of detecting EPC

### Widowhood
- `widowhood_mourning_years = 1` — configurable mourning period before re-entry
- Re-pairing probability: function of age, resources, mate value

### Mating system variants (toggleable overlays)
- **Enforced monogamy**: norm violation cost + detection probability, gated by `law_strength`
- **Elite polygyny**: top N% status males exempt from `max_mates` limit
- **Egalitarian**: reduced variance in male competitive success
- Interact with institutional strength parameter

## Config parameters
9 new parameters: `female_choosiness_age_effect`, `male_contest_injury_risk`,
`male_competition_mode`, `pair_bond_growth_rate`, `infidelity_enabled`,
`infidelity_base_rate`, `paternity_certainty_threshold`, `jealousy_detection_rate`,
`widowhood_mourning_years`

## Metrics
6 new metrics: `infidelity_rate`, `epc_detected`, `paternity_uncertainty`,
`avg_bond_strength`, `mating_contests`, `bond_count_distribution`
