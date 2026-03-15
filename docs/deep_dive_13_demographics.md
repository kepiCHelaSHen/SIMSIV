# SIMSIV — Deep Dive 13: Sex-Differential Mortality and Demographics

## Design Decisions

### A. Sex-Differential Mortality
- Males age 15-40: 1.8x background mortality rate (risk-taking + hazardous behavior)
- Existing conflict mortality already sex-differential (same-sex targeting)
- Combined effect: male deaths exceed female deaths by ~5-10%

### B. Childbirth Mortality
- 2% per-birth maternal mortality risk
- 3x multiplier for unhealthy mothers (health < 0.4)
- ~11 childbirth deaths per 50yr at 200 pop (realistic pre-industrial)
- ~10-14% lifetime risk for women with 5-7 births (historically plausible)

### C. Age-Specific Fertility
- Adolescent (15-19): 60% of peak fertility (subfecundity)
- Peak (20-28): 100% fertility
- Early decline (29-30): still full fertility
- Post-30 decline: DD06's 3%/yr decline (gradual)
- Combined with DD06 birth interval (2yr) and lifetime cap (12)

### D. What's NOT Implemented
- Grandmother survival bonus per grandchild (already in DD06)
- Male dominance delay age (mate_value age penalty already handles this)
- TFR metric (would need cumulative tracking across lifetimes)
- Sex-differential elderly mortality (small effect, adds complexity)

## Parameters Added
| Parameter | Default | Description |
|-----------|---------|-------------|
| male_risk_mortality_multiplier | 1.8 | Extra male mortality age 15-40 |
| childbirth_mortality_rate | 0.02 | Per-birth maternal death risk |
| adolescent_fertility_fraction | 0.6 | Fertility multiplier age 15-19 |
| fertility_peak_age | 24 | Age of peak fertility |

## Metrics Added
| Metric | Description |
|--------|-------------|
| male_deaths | Male deaths per tick |
| female_deaths | Female deaths per tick |
| childbirth_deaths | Maternal deaths per tick |
| sex_ratio_reproductive | Females per 100 males (age 20-40) |

## Files Changed
- `engines/mortality.py` — sex-differential background mortality
- `engines/reproduction.py` — childbirth mortality, age-specific fertility
- `config.py` — 4 DD13 parameters
- `metrics/collectors.py` — 4 DD13 metrics
