# SIMSIV — Sensitivity Analysis
# Generated from AutoSIM Run 3 journal (816 experiments)
# This is Table 2 of Paper 1.
# Generated: 2026-03-15 18:13

## Overview

- Total experiments analyzed: 819
- Accepted (improved or annealed): 496
- Parameters analyzed: 34
- Metrics analyzed: 9

Sensitivity measured as Pearson correlation (r) between
parameter value and metric value across all experiments.
|r| ≥ 0.30 = meaningful influence. |r| ≥ 0.50 = strong influence.

## Summary: Strongest Driver per Metric

| Metric | Top Parameter | r | r² | Direction |
|--------|--------------|---|----|-----------|
| Resource Gini | `resource_equal_floor` | -0.885 | 0.783 | ↓ |
| Mating Inequality | `pair_bond_dissolution_rate` | -0.632 | 0.399 | ↓ |
| Violence Death Frac | `violence_death_chance` | +0.577 | 0.333 | ↑ |
| Pop Growth Rate | `scarcity_severity` | -0.243 | 0.059 | ↓ |
| Child Survival | `childhood_mortality_annual` | -0.554 | 0.307 | ↓ |
| Lifetime Births | `male_risk_mortality_multiplier` | +0.486 | 0.237 | ↑ |
| Bond Dissolution | `pair_bond_dissolution_rate` | +0.936 | 0.876 | ↑ |
| Avg Cooperation | `mortality_base` | -0.199 | 0.039 | ↓ |
| Avg Aggression | `mortality_base` | +0.450 | 0.203 | ↑ |

## Full Sensitivity Tables (per metric)

Only showing parameters with |r| ≥ 0.10.

### Resource Gini

| Rank | Parameter | r | r² | p-value | Direction |
|------|-----------|---|----|---------|-----------|
| 1 | `resource_equal_floor` | -0.885 | 0.783 | < 0.0001 | ↓ |
| 2 | `violence_death_chance` | +0.763 | 0.582 | < 0.0001 | ↑ |
| 3 | `epidemic_base_probability` | +0.541 | 0.293 | < 0.0001 | ↑ |
| 4 | `cooperation_network_bonus` | +0.536 | 0.288 | < 0.0001 | ↑ |
| 5 | `maternal_health_cost` | -0.479 | 0.230 | < 0.0001 | ↓ |
| 6 | `wealth_diminishing_power` | -0.461 | 0.212 | < 0.0001 | ↓ |
| 7 | `conflict_base_probability` | +0.378 | 0.143 | < 0.0001 | ↑ |
| 8 | `violence_cost_health` | -0.365 | 0.133 | < 0.0001 | ↓ |
| 9 | `epidemic_lethality_base` | -0.339 | 0.115 | < 0.0001 | ↓ |
| 10 | `female_choice_strength` | -0.314 | 0.099 | < 0.0001 | ↓ |
| 11 | `cooperation_sharing_rate` | -0.311 | 0.097 | < 0.0001 | ↓ |
| 12 | `pair_bond_strength` | +0.280 | 0.079 | < 0.0001 | ↑ |
| 13 | `orphan_mortality_multiplier` | -0.249 | 0.062 | < 0.0001 | ↓ |
| 14 | `health_decay_per_year` | -0.235 | 0.055 | < 0.0001 | ↓ |
| 15 | `child_investment_per_year` | +0.225 | 0.051 | < 0.0001 | ↑ |
| 16 | `aggression_production_penalty` | +0.222 | 0.049 | < 0.0001 | ↑ |
| 17 | `resource_abundance` | +0.211 | 0.045 | < 0.0001 | ↑ |
| 18 | `childhood_mortality_annual` | +0.210 | 0.044 | < 0.0001 | ↑ |
| 19 | `age_first_reproduction` | +0.207 | 0.043 | < 0.0001 | ↑ |
| 20 | `mortality_base` | +0.187 | 0.035 | < 0.0001 | ↑ |
| 21 | `flee_threshold` | -0.171 | 0.029 | < 0.0001 | ↓ |
| 22 | `scarcity_severity` | +0.147 | 0.021 | < 0.0001 | ↑ |
| 23 | `maternal_age_fertility_decline` | -0.136 | 0.018 | < 0.0001 | ↓ |
| 24 | `pair_bond_dissolution_rate` | +0.107 | 0.011 | 0.0021 | ↑ |
| 25 | `subsistence_floor` | -0.103 | 0.011 | 0.0031 | ↓ |

### Mating Inequality

| Rank | Parameter | r | r² | p-value | Direction |
|------|-----------|---|----|---------|-----------|
| 1 | `pair_bond_dissolution_rate` | -0.632 | 0.399 | < 0.0001 | ↓ |
| 2 | `mortality_base` | -0.621 | 0.385 | < 0.0001 | ↓ |
| 3 | `age_first_reproduction` | -0.519 | 0.269 | < 0.0001 | ↓ |
| 4 | `resource_abundance` | -0.511 | 0.261 | < 0.0001 | ↓ |
| 5 | `age_max_reproduction_female` | -0.457 | 0.209 | < 0.0001 | ↓ |
| 6 | `wealth_diminishing_power` | +0.439 | 0.193 | < 0.0001 | ↑ |
| 7 | `maternal_health_cost` | +0.426 | 0.181 | < 0.0001 | ↑ |
| 8 | `orphan_mortality_multiplier` | +0.388 | 0.151 | < 0.0001 | ↑ |
| 9 | `seasonal_conflict_boost` | +0.336 | 0.113 | < 0.0001 | ↑ |
| 10 | `cooperation_sharing_rate` | +0.334 | 0.112 | < 0.0001 | ↑ |
| 11 | `epidemic_base_probability` | -0.334 | 0.112 | < 0.0001 | ↓ |
| 12 | `female_choice_strength` | +0.260 | 0.068 | < 0.0001 | ↑ |
| 13 | `childbirth_mortality_rate` | +0.254 | 0.064 | < 0.0001 | ↑ |
| 14 | `epidemic_lethality_base` | +0.251 | 0.063 | < 0.0001 | ↑ |
| 15 | `violence_death_chance` | -0.249 | 0.062 | < 0.0001 | ↓ |
| 16 | `childhood_mortality_annual` | -0.249 | 0.062 | < 0.0001 | ↓ |
| 17 | `child_investment_per_year` | +0.232 | 0.054 | < 0.0001 | ↑ |
| 18 | `health_decay_per_year` | +0.229 | 0.052 | < 0.0001 | ↑ |
| 19 | `resource_equal_floor` | +0.201 | 0.041 | < 0.0001 | ↑ |
| 20 | `subsistence_floor` | +0.186 | 0.035 | < 0.0001 | ↑ |
| 21 | `conflict_base_probability` | -0.180 | 0.032 | < 0.0001 | ↓ |
| 22 | `violence_cost_health` | +0.173 | 0.030 | < 0.0001 | ↑ |
| 23 | `violence_cost_resources` | +0.163 | 0.026 | < 0.0001 | ↑ |
| 24 | `widowhood_mourning_years` | -0.151 | 0.023 | < 0.0001 | ↓ |
| 25 | `flee_threshold` | +0.126 | 0.016 | 0.0003 | ↑ |
| 26 | `maternal_age_fertility_decline` | +0.117 | 0.014 | 0.0008 | ↑ |
| 27 | `cooperation_network_bonus` | +0.111 | 0.012 | 0.0014 | ↑ |

### Violence Death Frac

| Rank | Parameter | r | r² | p-value | Direction |
|------|-----------|---|----|---------|-----------|
| 1 | `violence_death_chance` | +0.577 | 0.333 | < 0.0001 | ↑ |
| 2 | `resource_equal_floor` | -0.437 | 0.191 | < 0.0001 | ↓ |
| 3 | `maternal_health_cost` | -0.406 | 0.165 | < 0.0001 | ↓ |
| 4 | `epidemic_base_probability` | +0.394 | 0.155 | < 0.0001 | ↑ |
| 5 | `conflict_base_probability` | +0.377 | 0.142 | < 0.0001 | ↑ |
| 6 | `cooperation_network_bonus` | +0.374 | 0.140 | < 0.0001 | ↑ |
| 7 | `wealth_diminishing_power` | -0.358 | 0.128 | < 0.0001 | ↓ |
| 8 | `aggression_production_penalty` | +0.355 | 0.126 | < 0.0001 | ↑ |
| 9 | `orphan_mortality_multiplier` | -0.292 | 0.085 | < 0.0001 | ↓ |
| 10 | `cooperation_sharing_rate` | -0.259 | 0.067 | < 0.0001 | ↓ |
| 11 | `childhood_mortality_annual` | +0.210 | 0.044 | < 0.0001 | ↑ |
| 12 | `female_choice_strength` | -0.178 | 0.032 | < 0.0001 | ↓ |
| 13 | `maternal_age_fertility_decline` | -0.173 | 0.030 | < 0.0001 | ↓ |
| 14 | `age_first_reproduction` | +0.163 | 0.027 | < 0.0001 | ↑ |
| 15 | `widowhood_mourning_years` | +0.128 | 0.016 | 0.0002 | ↑ |
| 16 | `scarcity_severity` | -0.122 | 0.015 | 0.0004 | ↓ |
| 17 | `flee_threshold` | -0.121 | 0.015 | 0.0005 | ↓ |
| 18 | `health_decay_per_year` | -0.106 | 0.011 | 0.0023 | ↓ |
| 19 | `grandparent_survival_bonus` | +0.103 | 0.011 | 0.0030 | ↑ |
| 20 | `age_max_reproduction_female` | +0.103 | 0.011 | 0.0031 | ↑ |

### Pop Growth Rate

| Rank | Parameter | r | r² | p-value | Direction |
|------|-----------|---|----|---------|-----------|
| 1 | `scarcity_severity` | -0.243 | 0.059 | < 0.0001 | ↓ |
| 2 | `pair_bond_strength` | -0.151 | 0.023 | < 0.0001 | ↓ |
| 3 | `infidelity_base_rate` | +0.138 | 0.019 | < 0.0001 | ↑ |
| 4 | `widowhood_mourning_years` | +0.137 | 0.019 | < 0.0001 | ↑ |
| 5 | `mortality_base` | -0.129 | 0.017 | 0.0002 | ↓ |
| 6 | `resource_equal_floor` | +0.126 | 0.016 | 0.0003 | ↑ |
| 7 | `epidemic_lethality_base` | +0.121 | 0.015 | 0.0005 | ↑ |
| 8 | `maternal_age_fertility_decline` | -0.114 | 0.013 | 0.0011 | ↓ |
| 9 | `age_max_reproduction_female` | +0.112 | 0.013 | 0.0013 | ↑ |
| 10 | `violence_cost_health` | +0.111 | 0.012 | 0.0014 | ↑ |
| 11 | `grandparent_survival_bonus` | +0.102 | 0.010 | 0.0037 | ↑ |

### Child Survival

| Rank | Parameter | r | r² | p-value | Direction |
|------|-----------|---|----|---------|-----------|
| 1 | `childhood_mortality_annual` | -0.554 | 0.307 | < 0.0001 | ↓ |
| 2 | `grandparent_survival_bonus` | -0.489 | 0.239 | < 0.0001 | ↓ |
| 3 | `seasonal_conflict_boost` | -0.455 | 0.207 | < 0.0001 | ↓ |
| 4 | `base_conception_chance` | -0.381 | 0.145 | < 0.0001 | ↓ |
| 5 | `aggression_production_penalty` | -0.368 | 0.136 | < 0.0001 | ↓ |
| 6 | `violence_cost_resources` | +0.350 | 0.122 | < 0.0001 | ↑ |
| 7 | `scarcity_severity` | +0.348 | 0.121 | < 0.0001 | ↑ |
| 8 | `conflict_base_probability` | -0.287 | 0.082 | < 0.0001 | ↓ |
| 9 | `childbirth_mortality_rate` | +0.283 | 0.080 | < 0.0001 | ↑ |
| 10 | `cooperation_sharing_rate` | -0.275 | 0.076 | < 0.0001 | ↓ |
| 11 | `male_risk_mortality_multiplier` | -0.247 | 0.061 | < 0.0001 | ↓ |
| 12 | `mortality_base` | +0.238 | 0.057 | < 0.0001 | ↑ |
| 13 | `age_max_reproduction_female` | -0.185 | 0.034 | < 0.0001 | ↓ |
| 14 | `wealth_diminishing_power` | +0.164 | 0.027 | < 0.0001 | ↑ |
| 15 | `infidelity_base_rate` | -0.162 | 0.026 | < 0.0001 | ↓ |
| 16 | `pair_bond_dissolution_rate` | +0.155 | 0.024 | < 0.0001 | ↑ |
| 17 | `pair_bond_strength` | +0.131 | 0.017 | 0.0002 | ↑ |
| 18 | `age_first_reproduction` | -0.131 | 0.017 | 0.0002 | ↓ |
| 19 | `epidemic_lethality_base` | +0.116 | 0.013 | 0.0009 | ↑ |
| 20 | `resource_abundance` | -0.113 | 0.013 | 0.0012 | ↓ |
| 21 | `violence_cost_health` | +0.108 | 0.012 | 0.0020 | ↑ |

### Lifetime Births

| Rank | Parameter | r | r² | p-value | Direction |
|------|-----------|---|----|---------|-----------|
| 1 | `male_risk_mortality_multiplier` | +0.486 | 0.237 | < 0.0001 | ↑ |
| 2 | `cooperation_sharing_rate` | +0.385 | 0.148 | < 0.0001 | ↑ |
| 3 | `seasonal_conflict_boost` | +0.379 | 0.144 | < 0.0001 | ↑ |
| 4 | `widowhood_mourning_years` | -0.356 | 0.127 | < 0.0001 | ↓ |
| 5 | `resource_equal_floor` | -0.338 | 0.114 | < 0.0001 | ↓ |
| 6 | `base_conception_chance` | +0.332 | 0.110 | < 0.0001 | ↑ |
| 7 | `violence_cost_health` | -0.319 | 0.102 | < 0.0001 | ↓ |
| 8 | `violence_death_chance` | +0.291 | 0.085 | < 0.0001 | ↑ |
| 9 | `pair_bond_dissolution_rate` | -0.263 | 0.069 | < 0.0001 | ↓ |
| 10 | `child_investment_per_year` | +0.258 | 0.067 | < 0.0001 | ↑ |
| 11 | `grandparent_survival_bonus` | +0.244 | 0.059 | < 0.0001 | ↑ |
| 12 | `epidemic_base_probability` | +0.240 | 0.058 | < 0.0001 | ↑ |
| 13 | `pair_bond_strength` | +0.238 | 0.057 | < 0.0001 | ↑ |
| 14 | `health_decay_per_year` | -0.236 | 0.056 | < 0.0001 | ↓ |
| 15 | `infidelity_base_rate` | -0.228 | 0.052 | < 0.0001 | ↓ |
| 16 | `epidemic_lethality_base` | -0.227 | 0.051 | < 0.0001 | ↓ |
| 17 | `age_first_reproduction` | -0.226 | 0.051 | < 0.0001 | ↓ |
| 18 | `mortality_base` | -0.222 | 0.049 | < 0.0001 | ↓ |
| 19 | `childhood_mortality_annual` | +0.215 | 0.046 | < 0.0001 | ↑ |
| 20 | `childbirth_mortality_rate` | -0.198 | 0.039 | < 0.0001 | ↓ |
| 21 | `maternal_age_fertility_decline` | +0.198 | 0.039 | < 0.0001 | ↑ |
| 22 | `female_choice_strength` | -0.181 | 0.033 | < 0.0001 | ↓ |
| 23 | `conflict_base_probability` | +0.161 | 0.026 | < 0.0001 | ↑ |
| 24 | `aggression_production_penalty` | +0.117 | 0.014 | 0.0008 | ↑ |
| 25 | `cooperation_network_bonus` | +0.116 | 0.013 | 0.0009 | ↑ |
| 26 | `age_max_reproduction_female` | -0.101 | 0.010 | 0.0039 | ↓ |

### Bond Dissolution

| Rank | Parameter | r | r² | p-value | Direction |
|------|-----------|---|----|---------|-----------|
| 1 | `pair_bond_dissolution_rate` | +0.936 | 0.876 | < 0.0001 | ↑ |
| 2 | `mortality_base` | +0.720 | 0.519 | < 0.0001 | ↑ |
| 3 | `age_first_reproduction` | +0.493 | 0.243 | < 0.0001 | ↑ |
| 4 | `seasonal_conflict_boost` | -0.461 | 0.213 | < 0.0001 | ↓ |
| 5 | `resource_abundance` | +0.447 | 0.200 | < 0.0001 | ↑ |
| 6 | `subsistence_floor` | -0.396 | 0.157 | < 0.0001 | ↓ |
| 7 | `cooperation_sharing_rate` | -0.378 | 0.143 | < 0.0001 | ↓ |
| 8 | `health_decay_per_year` | -0.363 | 0.132 | < 0.0001 | ↓ |
| 9 | `age_max_reproduction_female` | +0.344 | 0.118 | < 0.0001 | ↑ |
| 10 | `epidemic_lethality_base` | -0.286 | 0.082 | < 0.0001 | ↓ |
| 11 | `wealth_diminishing_power` | -0.277 | 0.077 | < 0.0001 | ↓ |
| 12 | `epidemic_base_probability` | +0.276 | 0.076 | < 0.0001 | ↑ |
| 13 | `maternal_health_cost` | -0.260 | 0.068 | < 0.0001 | ↓ |
| 14 | `scarcity_severity` | +0.256 | 0.066 | < 0.0001 | ↑ |
| 15 | `aggression_production_penalty` | -0.222 | 0.049 | < 0.0001 | ↓ |
| 16 | `cooperation_network_bonus` | -0.202 | 0.041 | < 0.0001 | ↓ |
| 17 | `grandparent_survival_bonus` | -0.194 | 0.038 | < 0.0001 | ↓ |
| 18 | `orphan_mortality_multiplier` | -0.188 | 0.035 | < 0.0001 | ↓ |
| 19 | `widowhood_mourning_years` | +0.172 | 0.030 | < 0.0001 | ↑ |
| 20 | `violence_cost_resources` | -0.159 | 0.025 | < 0.0001 | ↓ |
| 21 | `childbirth_mortality_rate` | -0.154 | 0.024 | < 0.0001 | ↓ |
| 22 | `violence_cost_health` | -0.136 | 0.019 | < 0.0001 | ↓ |
| 23 | `child_investment_per_year` | -0.130 | 0.017 | 0.0002 | ↓ |
| 24 | `resource_equal_floor` | -0.122 | 0.015 | 0.0005 | ↓ |
| 25 | `violence_death_chance` | +0.116 | 0.013 | 0.0008 | ↑ |

### Avg Cooperation

| Rank | Parameter | r | r² | p-value | Direction |
|------|-----------|---|----|---------|-----------|
| 1 | `mortality_base` | -0.199 | 0.039 | < 0.0001 | ↓ |
| 2 | `epidemic_lethality_base` | +0.193 | 0.037 | < 0.0001 | ↑ |
| 3 | `violence_cost_health` | +0.161 | 0.026 | < 0.0001 | ↑ |
| 4 | `age_max_reproduction_female` | -0.119 | 0.014 | 0.0006 | ↓ |
| 5 | `pair_bond_dissolution_rate` | -0.115 | 0.013 | 0.0010 | ↓ |
| 6 | `female_choice_strength` | +0.108 | 0.012 | 0.0020 | ↑ |
| 7 | `resource_abundance` | -0.107 | 0.011 | 0.0021 | ↓ |
| 8 | `pair_bond_strength` | -0.106 | 0.011 | 0.0023 | ↓ |

### Avg Aggression

| Rank | Parameter | r | r² | p-value | Direction |
|------|-----------|---|----|---------|-----------|
| 1 | `mortality_base` | +0.450 | 0.203 | < 0.0001 | ↑ |
| 2 | `pair_bond_dissolution_rate` | +0.307 | 0.094 | < 0.0001 | ↑ |
| 3 | `seasonal_conflict_boost` | -0.262 | 0.069 | < 0.0001 | ↓ |
| 4 | `scarcity_severity` | +0.259 | 0.067 | < 0.0001 | ↑ |
| 5 | `child_investment_per_year` | -0.242 | 0.058 | < 0.0001 | ↓ |
| 6 | `cooperation_network_bonus` | -0.234 | 0.055 | < 0.0001 | ↓ |
| 7 | `resource_abundance` | +0.218 | 0.048 | < 0.0001 | ↑ |
| 8 | `age_first_reproduction` | +0.205 | 0.042 | < 0.0001 | ↑ |
| 9 | `epidemic_lethality_base` | -0.168 | 0.028 | < 0.0001 | ↓ |
| 10 | `grandparent_survival_bonus` | -0.157 | 0.025 | < 0.0001 | ↓ |
| 11 | `orphan_mortality_multiplier` | -0.144 | 0.021 | < 0.0001 | ↓ |
| 12 | `aggression_production_penalty` | -0.134 | 0.018 | 0.0001 | ↓ |
| 13 | `age_max_reproduction_female` | +0.127 | 0.016 | 0.0003 | ↑ |
| 14 | `female_choice_strength` | -0.120 | 0.015 | 0.0006 | ↓ |
| 15 | `maternal_health_cost` | -0.118 | 0.014 | 0.0007 | ↓ |
| 16 | `cooperation_sharing_rate` | -0.115 | 0.013 | 0.0010 | ↓ |
| 17 | `violence_cost_health` | -0.104 | 0.011 | 0.0028 | ↓ |

## Global Parameter Importance
(Mean |r| across all metrics — measures overall influence)

| Rank | Parameter | Mean |r| | Max |r| | Metrics Influenced |
|------|-----------|---------|---------|-------------------|
| 1 | `mortality_base` | 0.315 | 0.720 | 8 |
| 2 | `pair_bond_dissolution_rate` | 0.286 | 0.936 | 7 |
| 3 | `resource_equal_floor` | 0.246 | 0.885 | 6 |
| 4 | `violence_death_chance` | 0.238 | 0.763 | 5 |
| 5 | `cooperation_sharing_rate` | 0.235 | 0.385 | 7 |
| 6 | `age_first_reproduction` | 0.230 | 0.519 | 7 |
| 7 | `epidemic_base_probability` | 0.220 | 0.541 | 5 |
| 8 | `seasonal_conflict_boost` | 0.219 | 0.461 | 5 |
| 9 | `wealth_diminishing_power` | 0.207 | 0.461 | 5 |
| 10 | `maternal_health_cost` | 0.203 | 0.479 | 5 |
| 11 | `resource_abundance` | 0.199 | 0.511 | 6 |
| 12 | `epidemic_lethality_base` | 0.192 | 0.339 | 8 |
| 13 | `cooperation_network_bonus` | 0.192 | 0.536 | 6 |
| 14 | `childhood_mortality_annual` | 0.190 | 0.554 | 5 |
| 15 | `age_max_reproduction_female` | 0.178 | 0.457 | 8 |
| 16 | `aggression_production_penalty` | 0.178 | 0.368 | 6 |
| 17 | `conflict_base_probability` | 0.177 | 0.378 | 5 |
| 18 | `violence_cost_health` | 0.172 | 0.365 | 8 |
| 19 | `orphan_mortality_multiplier` | 0.167 | 0.388 | 5 |
| 20 | `scarcity_severity` | 0.166 | 0.348 | 6 |
| 21 | `grandparent_survival_bonus` | 0.154 | 0.489 | 6 |
| 22 | `health_decay_per_year` | 0.152 | 0.363 | 5 |
| 23 | `female_choice_strength` | 0.148 | 0.314 | 6 |
| 24 | `child_investment_per_year` | 0.141 | 0.258 | 5 |
| 25 | `pair_bond_strength` | 0.138 | 0.280 | 5 |

## Notes for Paper

- This analysis uses Pearson r (linear correlation).
  Some parameters may have nonlinear effects not captured here.
- The optimizer's annealing accepts worse solutions, so the
  parameter space explored is broader than pure gradient descent.
- Parameters with very narrow ranges (< 0.05 spread) may show
  artificially low r due to range restriction.
- For publication, consider supplementing with OAT
  (one-at-a-time) sweeps on the top 5 parameters per metric.

## Calibration Context

These sensitivities are derived from the calibration search
trajectory, not from a designed sensitivity experiment.
They show which parameters the optimizer had to move to
achieve calibration — a pragmatic but imperfect proxy for
true global sensitivity.
