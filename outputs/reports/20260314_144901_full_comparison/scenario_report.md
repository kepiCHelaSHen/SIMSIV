# SIMSIV Scenario Comparison Report

*SIMSIV is a stylized model. Results reflect the consequences of the implemented rules, not claims about human societies. All metrics are artifacts of simplification. Do not over-interpret.*

## FREE_COMPETITION

**Population**: 547 -> 873 (+59%), peak 1143, trough 547
**Violence**: stable (early 0.053, late 0.053)
**Resource Gini**: avg 0.134
**Reproductive skew**: 0.525, unmated males: 38.8%
**Child survival**: 76.1%
**Trait evolution**: aggression 0.503->0.483, cooperation 0.503->0.515

## ENFORCED_MONOGAMY

**Population**: 542 -> 968 (+78%), peak 1574, trough 542
**Violence**: stable (early 0.032, late 0.036)
**Resource Gini**: avg 0.136
**Reproductive skew**: 0.484, unmated males: 21.5%
**Child survival**: 74.0%
**Trait evolution**: aggression 0.505->0.509, cooperation 0.502->0.507

## ELITE_POLYGYNY

**Population**: 547 -> 1658 (+203%), peak 1822, trough 547
**Violence**: stable (early 0.055, late 0.060)
**Resource Gini**: avg 0.972
**Reproductive skew**: 0.545, unmated males: 39.6%
**Child survival**: 84.6%
**Trait evolution**: aggression 0.507->0.512, cooperation 0.502->0.538

**Warnings:**
- EXTREME INEQUALITY: resource Gini reached 0.999. May indicate a model artifact (winner-take-all feedback loop).

## HIGH_FEMALE_CHOICE

**Population**: 547 -> 1040 (+90%), peak 1164, trough 547
**Violence**: stable (early 0.055, late 0.054)
**Resource Gini**: avg 0.133
**Reproductive skew**: 0.525, unmated males: 39.9%
**Child survival**: 76.8%
**Trait evolution**: aggression 0.498->0.473, cooperation 0.505->0.518

## RESOURCE_ABUNDANCE

**Population**: 547 -> 1900 (+247%), peak 2385, trough 547
**Violence**: stable (early 0.044, late 0.045)
**Resource Gini**: avg 0.127
**Reproductive skew**: 0.527, unmated males: 37.9%
**Child survival**: 78.9%
**Trait evolution**: aggression 0.505->0.490, cooperation 0.499->0.507

## RESOURCE_SCARCITY

**Population**: 541 -> 29 (-95%), peak 669, trough 20
**Violence**: stable (early 0.073, late 0.066)
**Resource Gini**: avg 0.130
**Reproductive skew**: 0.545, unmated males: 42.6%
**Child survival**: 61.1%
**Trait evolution**: aggression 0.504->0.474, cooperation 0.503->0.485

**Warnings:**
- LOW POPULATION: dropped to 20 — results may reflect extinction dynamics rather than social equilibrium.

## HIGH_VIOLENCE_COST

**Population**: 527 -> 33 (-94%), peak 679, trough 33
**Violence**: stable (early 0.045, late 0.040)
**Resource Gini**: avg 0.126
**Reproductive skew**: 0.549, unmated males: 39.5%
**Child survival**: 84.2%
**Trait evolution**: aggression 0.501->0.469, cooperation 0.511->0.542

**Warnings:**
- LOW POPULATION: dropped to 33 — results may reflect extinction dynamics rather than social equilibrium.

## STRONG_PAIR_BONDING

**Population**: 549 -> 891 (+62%), peak 1188, trough 549
**Violence**: stable (early 0.055, late 0.054)
**Resource Gini**: avg 0.135
**Reproductive skew**: 0.536, unmated males: 35.9%
**Child survival**: 79.3%
**Trait evolution**: aggression 0.506->0.494, cooperation 0.500->0.512

---
## Cross-Scenario Highlights

**Most violent**: RESOURCE_SCARCITY (0.067)
**Least violent**: ENFORCED_MONOGAMY (0.035)
**Highest inequality**: ELITE_POLYGYNY (Gini 0.972)
**Best child survival**: ELITE_POLYGYNY (84.6%)
**Most unmated males**: RESOURCE_SCARCITY (42.6%)

---
*SIMSIV is a stylized model. Results reflect the consequences of the implemented rules, not claims about human societies. All metrics are artifacts of simplification. Do not over-interpret.*