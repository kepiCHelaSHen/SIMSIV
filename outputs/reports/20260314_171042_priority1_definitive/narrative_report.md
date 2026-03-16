# SIMSIV Scenario Comparison Report

*SIMSIV is a stylized model. Results reflect the consequences of the implemented rules, not claims about human societies. All metrics are artifacts of simplification. Do not over-interpret.*

## FREE_COMPETITION

**Population**: 548 -> 979 (+79%), peak 1198, trough 548
**Violence**: stable (early 0.061, late 0.056)
**Resource Gini**: avg 0.236
**Reproductive skew**: 0.539, unmated males: 40.4%
**Child survival**: 80.8%
**Trait evolution**: aggression 0.500->0.493, cooperation 0.501->0.523

## ENFORCED_MONOGAMY

**Population**: 543 -> 994 (+83%), peak 1218, trough 543
**Violence**: stable (early 0.037, late 0.036)
**Resource Gini**: avg 0.237
**Reproductive skew**: 0.491, unmated males: 23.3%
**Child survival**: 76.7%
**Trait evolution**: aggression 0.501->0.500, cooperation 0.503->0.514

## ELITE_POLYGYNY

**Population**: 548 -> 867 (+58%), peak 1337, trough 548
**Violence**: stable (early 0.062, late 0.060)
**Resource Gini**: avg 0.412
**Reproductive skew**: 0.554, unmated males: 41.1%
**Child survival**: 85.8%
**Trait evolution**: aggression 0.500->0.500, cooperation 0.502->0.545

---
## Cross-Scenario Highlights

**Most violent**: ELITE_POLYGYNY (0.061)
**Least violent**: ENFORCED_MONOGAMY (0.037)
**Highest inequality**: ELITE_POLYGYNY (Gini 0.412)
**Best child survival**: ELITE_POLYGYNY (85.8%)
**Most unmated males**: ELITE_POLYGYNY (41.1%)

## Integrity Warnings

- SEED SENSITIVE: ELITE_POLYGYNY.final_population has high variance (mean=867.800, std=306.529, cv=35.3%). Results may not be robust — use more seeds.

---
*SIMSIV is a stylized model. Results reflect the consequences of the implemented rules, not claims about human societies. All metrics are artifacts of simplification. Do not over-interpret.*