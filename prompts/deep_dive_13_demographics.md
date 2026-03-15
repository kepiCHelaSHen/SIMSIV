# SIMSIV — PROMPT: DEEP DIVE 13 — SEX-DIFFERENTIAL MORTALITY AND DEMOGRAPHICS
# File: D:\EXPERIMENTS\SIM\prompts\deep_dive_13_demographics.md
# Use: Send to Claude after DD12 is complete
# Priority: PHASE C, Sprint 6

================================================================================
CONTEXT INJECTION — READ FIRST
================================================================================

You are doing Deep Dive 13 on the SIMSIV demographic model.

Before doing ANYTHING, read:
  1. D:\EXPERIMENTS\SIM\CHAIN_PROMPT.md
  2. D:\EXPERIMENTS\SIM\devlog\DEV_LOG.md
  3. D:\EXPERIMENTS\SIM\engines\mortality.py (current death model)
  4. D:\EXPERIMENTS\SIM\engines\reproduction.py (current fertility model)
  5. D:\EXPERIMENTS\SIM\models\agent.py
  6. D:\EXPERIMENTS\SIM\config.py
  7. D:\EXPERIMENTS\SIM\STATUS.md (latest results)

The current model applies identical mortality rates to males and females and
uses a simple binary fertile/not-fertile window. In pre-industrial societies,
male mortality was significantly higher than female (especially ages 15-40)
due to conflict, risk-taking behavior, and hazardous work. Female mortality
was elevated during reproductive years due to childbirth. Birth spacing,
age-specific fertility curves, and sex ratio dynamics all affect social
structure in ways the current model misses. This deep dive adds demographic
realism.

================================================================================
DEEP DIVE 13: SEX-DIFFERENTIAL MORTALITY AND DEMOGRAPHICS
================================================================================

CURRENT STATE:
  - mortality_base: identical for both sexes (0.02/year)
  - Conflict mortality: males only fight males (same-sex targeting) — de facto
    higher male mortality from conflict, but not tracked separately
  - Fertility: binary window (15-45F, 15-65M), flat conception chance within window
  - No childbirth mortality for females
  - No birth spacing — females can conceive every year
  - No age-specific fertility curves (fertility doesn't decline gradually)
  - Sex ratio stays near 50/50 throughout (not realistic)

CALIBRATION TARGETS:
  - Male mortality age 15-40: ~2x female (conflict + risk-taking)
  - Female mortality during reproduction: ~1.5x baseline (childbirth risk)
  - Sex ratio at birth: 50/50 (fine)
  - Sex ratio age 20-40: ~105F per 100M (males die faster)
  - Birth spacing: 2-3 years average between live births (lactation, recovery)
  - Age-specific fertility: peaks 20-28, declines gradually, ends 45
  - Child survival: 50-70% to age 15 (currently ~83% — too high)
    Note: DD09 epidemic will help; this dive adds childbirth + spacing effects

QUESTIONS TO RESOLVE AND IMPLEMENT:

A. SEX-DIFFERENTIAL MORTALITY
   - Males age 15-40: elevated mortality multiplier
     Sources: conflict (already partially modeled), risk-taking behavior
     (risk_tolerance trait should gate this), hazardous resource acquisition
   - Females during reproduction: childbirth mortality risk per birth
     Should scale with: maternal health, resource level, birth frequency
   - Elderly: females slightly more robust than males past age 60
     (historical pattern — implement as differential age-decay rate)

B. AGE-SPECIFIC FERTILITY CURVE
   Current: flat within window. Real fertility:
   - 15-19: subfertile (adolescent subfecundity) — 60% of peak
   - 20-28: peak fertility — 100%
   - 29-35: gradual decline — 90% to 75%
   - 36-42: accelerating decline — 60% to 30%
   - 43-45: minimal — 10-15%
   Implement as a piecewise function applied to base_conception_chance.
   Should use fertility_base trait as the multiplier on this curve.

C. BIRTH SPACING AND LACTATIONAL SUPPRESSION
   Currently: females can conceive every year. Reality: 2-3 year average interval
   - Add last_birth_year field to agent
   - Conception chance severely reduced for 1-2 years post-birth
   - Space modulated by: infant survival (longer spacing if infant survives),
     resource level (well-fed mothers cycle faster), and fertility_base trait
   - This reduces total fertility from effectively 15+ to a realistic 5-8 lifetime

D. SEX RATIO DYNAMICS
   If male mortality is higher, sex ratio shifts female-heavy in reproductive ages.
   This affects the mating market:
   - More females than males in the 20-40 age bracket
   - Males become relatively scarce → females compete more for males?
   - Or: males have more mate choice options? (challenge assumption)
   - Should male_competition_intensity scale with sex ratio?
   - Should female_choice_strength decline when males are scarce?
     (fewer options = less choosiness)

E. GRANDPARENT EFFECT (FEMALE LONGEVITY)
   Post-menopausal females currently stop reproducing but otherwise behave
   identically. In reality they provide substantial childcare:
   - Grandmothers with living grandchildren should boost grandchild survival
   - Should there be a "grandmother_survival_bonus" applied to grandchildren?
   - This creates selection pressure for female longevity past menopause
   - Links to DD06 household model

F. MALE DEVELOPMENTAL TRAJECTORY
   Males in real societies enter competition later and peak later than females:
   - Male mate value peaks later (25-35 for males vs 18-25 for females)
   - Male status and resource accumulation takes longer
   - Should male fertility window start effectively later? (15 is legal but
     real reproductive success starts 18-25 for males)
   - Should young males (15-20) have a "subordinate" period where they
     can't effectively compete with established older males?

G. DEMOGRAPHIC METRICS
   After this deep dive:
   - Track male vs female mortality rates separately
   - Track age-specific fertility rates (children per woman per age bracket)
   - Track sex ratio by age cohort
   - Track total fertility rate (TFR) — calibration target: 4-7 for natural fertility
   - Track average generation length (not same as avg age at death)

================================================================================
DELIVERABLES
================================================================================

1. docs/deep_dive_13_demographics.md — design decisions and demographic formulas
2. engines/mortality.py — sex-differential mortality, childbirth mortality
3. engines/reproduction.py — age-specific fertility curve, birth spacing
4. models/agent.py — last_birth_year field, birth_count field
5. config.py additions — demographic parameters
6. metrics/collectors.py — demographic metrics (male_mortality_rate,
   female_mortality_rate, tfr, sex_ratio_reproductive, avg_birth_interval)
7. DEV_LOG.md entry
8. CHAIN_PROMPT.md update

================================================================================
NEW PARAMETERS TO ADD TO CONFIG
================================================================================

male_risk_mortality_multiplier: float = 1.8  # extra male mortality age 15-40
childbirth_mortality_rate: float = 0.02      # per-birth female mortality risk
childbirth_mortality_health_threshold: float = 0.4  # below this health = 3x risk
birth_spacing_years: int = 2                 # min years between births (lactation)
birth_spacing_fertility_suppression: float = 0.8  # conception chance reduction during spacing
fertility_peak_age: int = 24                 # age of peak fertility
fertility_decline_start: int = 32            # age fertility starts declining
adolescent_fertility_fraction: float = 0.6  # fertility multiplier age 15-19
grandmother_survival_bonus: float = 0.05    # grandchild survival boost per grandmother
male_dominance_delay_age: int = 22          # age males enter full competition

================================================================================
CONSTRAINTS
================================================================================

- Birth spacing must not collapse population — verify TFR stays 4-7 after implementation
- Sex-differential mortality must be MODERATE — don't create extreme sex ratios
- Childbirth mortality should be significant but not catastrophic (2% per birth
  means ~10-14% lifetime risk for a woman with 5-7 births — historically plausible)
- All changes must keep total fertility rate in calibration target range
- Calibration check required: run 5 seeds post-implementation, verify TFR 4-7,
  child survival 50-70%, sex ratio 100-110F per 100M in age 20-40
