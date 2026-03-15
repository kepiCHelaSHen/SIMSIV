# SIMSIV — PROMPT: DEEP DIVE 09 — DISEASE AND EPIDEMIC EVENTS
# File: D:\EXPERIMENTS\SIM\prompts\deep_dive_09_disease.md
# Use: Send to Claude after DD08 is complete
# Priority: PHASE C, Sprint 2

================================================================================
CONTEXT INJECTION — READ FIRST
================================================================================

You are doing Deep Dive 09 on the SIMSIV disease and epidemic model.

Before doing ANYTHING, read:
  1. D:\EXPERIMENTS\SIM\CHAIN_PROMPT.md
  2. D:\EXPERIMENTS\SIM\devlog\DEV_LOG.md
  3. D:\EXPERIMENTS\SIM\models\environment.py (current shock model)
  4. D:\EXPERIMENTS\SIM\engines\mortality.py (current death model)
  5. D:\EXPERIMENTS\SIM\models\agent.py
  6. D:\EXPERIMENTS\SIM\config.py
  7. D:\EXPERIMENTS\SIM\STATUS.md (latest results)

The current mortality engine has background death rate (accidents/disease) and
age-based death, but no epidemic mechanics. In pre-industrial societies, disease
was the dominant mortality cause and it struck in sudden spikes — wiping 20-40%
of a population in a single event, then vanishing for decades. The social
consequences are massive and qualitatively different from background mortality:
sudden sex ratio imbalances, orphan surges, inheritance cascades, status
reshuffling as whole lineages die, institutional collapse under stress.
This is one of the biggest missing realism gaps in the model.

================================================================================
DEEP DIVE 09: DISEASE AND EPIDEMIC EVENTS
================================================================================

CURRENT STATE:
  - mortality_base: float = 0.02 — flat background rate, every agent every year
  - scarcity events: environmental shock reducing resources
  - No epidemic events, no disease spread, no immunity, no age-differential
    disease vulnerability, no social consequence of mass death events
  - Calibration target: child survival to 15 = 50-70% (currently ~83% — too high)
    Disease is the primary reason real child survival was lower

CORE DESIGN:
  Epidemics are distinct from background mortality in three ways:
  1. They are SUDDEN (concentrated in 1-3 years, not spread smoothly)
  2. They are LARGE (10-40% population impact vs 2% background)
  3. They have DIFFERENTIAL vulnerability (children, elderly, weakened agents hit hardest)

QUESTIONS TO RESOLVE AND IMPLEMENT:

A. EPIDEMIC TRIGGER MODEL
   - Epidemic probability should be low base rate + modifiers:
     * Overcrowding multiplier (above carrying capacity threshold)
     * Scarcity/malnutrition multiplier (weakens immune response)
     * Time-since-last-epidemic multiplier (susceptible population rebuilds)
   - Should epidemic type vary? (childhood disease vs adult plague vs famine fever)
   - How long does an epidemic last? (1-5 years peak, then fading tail)
   - Should there be immunity? (survivors are partially protected)

B. DIFFERENTIAL VULNERABILITY
   The most important feature — makes epidemics socially interesting:
   - Age: infants (0-5) and elderly (55+) most vulnerable
   - Health: agents below health threshold face multiplied risk
   - Resources: malnourished agents more vulnerable
   - Genetic: fertility_base and intelligence_proxy mildly protective
     (proxy for general physical resilience)
   - Social: agents in dense cooperation networks may have worse exposure
     but better care — net effect configurable

C. SOCIAL CONSEQUENCES
   The interesting part — what happens AFTER the epidemic:
   - Orphan surge: parents die, children face orphan mortality risk
   - Inheritance cascade: mass deaths trigger simultaneous inheritance events
   - Sex ratio disruption: if epidemic is sex-differential, mating market shifts
   - Status reshuffling: entire high-status lineages can be wiped out,
     creating sudden social mobility
   - Institutional response: does law_strength increase during epidemics?
     (collective action, resource pooling) or decrease? (breakdown)
   - Cooperation surge: do agents cooperate more during epidemic?
     (social support networks activate) or defect more? (resource hoarding)

D. IMMUNITY MODEL
   - Should survivors gain partial immunity? (health floor boost for 10-20 years)
   - Should immunity be heritable? (slight boost to fertility_base or health
     for children of survivors — natural selection in action)
   - Should the immune population create herd protection effects?
     (next epidemic hits harder because immune fraction reduced)

E. EPIDEMIC TYPES (OPTIONAL)
   Consider 2-3 distinct epidemic archetypes, each with different parameters:
   - Childhood disease: targets age 0-10, high lethality for infants,
     adults largely immune. Reduces child survival rate. Common.
   - Adult plague: targets 20-50 age range. Destroys the productive/reproductive
     population. Rare but catastrophic.
   - Famine fever: triggered by scarcity, all ages, moderate lethality,
     long duration. Compounds scarcity events.

F. ENVIRONMENT INTEGRATION
   - Epidemic events should appear in environment.tick() alongside scarcity events
   - Should epidemics and scarcity co-occur? (famine → disease → worse famine)
   - Should epidemic events be logged as environment events for metrics?

G. CALIBRATION TARGETS
   After this deep dive, verify against:
   - Child survival to age 15: 50-70% (from ~83% current)
   - Male mortality age 15-35: higher than female (add disease + conflict together)
   - Population variance across seeds: should increase (some runs get epidemics, some don't)
   - Epidemic frequency: roughly 1 major epidemic per 50-100 years per population

================================================================================
DELIVERABLES
================================================================================

1. docs/deep_dive_09_disease.md — design decisions
2. models/environment.py — epidemic event generation
3. engines/mortality.py — epidemic mortality processing with differential vulnerability
4. models/agent.py — immunity field if implemented
5. config.py additions — all epidemic parameters
6. metrics/collectors.py — epidemic metrics (epidemic_active, epidemic_deaths,
   immunity_fraction)
7. DEV_LOG.md entry
8. CHAIN_PROMPT.md update

================================================================================
NEW PARAMETERS TO ADD TO CONFIG
================================================================================

epidemic_base_probability: float = 0.02     # annual chance of epidemic starting
epidemic_lethality_base: float = 0.15       # fraction of vulnerable agents who die
epidemic_duration_years: int = 3            # peak epidemic duration
epidemic_child_vulnerability: float = 3.0   # multiplier for age 0-10
epidemic_elder_vulnerability: float = 2.0   # multiplier for age 55+
epidemic_health_threshold: float = 0.4      # below this health = vulnerable
epidemic_immunity_duration: int = 15        # years of post-epidemic immunity
epidemic_refractory_period: int = 20        # min years between epidemics
epidemic_overcrowding_multiplier: float = 2.0  # above 80% capacity → 2x epidemic risk
immunity_heritability: float = 0.1          # fraction of immunity passed to offspring

================================================================================
CONSTRAINTS
================================================================================

- Epidemics must be SUDDEN and CLUSTERED — not spread smoothly across years
- Differential vulnerability is mandatory — flat epidemic mortality misses
  the most important social consequences
- Do not break background mortality (mortality_base remains active during epidemics)
- Population safety (min_viable_population rescue) must remain functional
- Calibration check required after implementation: run 5 seeds and verify
  child survival drops into 50-70% target range
