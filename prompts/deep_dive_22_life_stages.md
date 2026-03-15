# SIMSIV — PROMPT: DEEP DIVE 22 — LIFE STAGE SOCIAL ROLES
# File: D:\EXPERIMENTS\SIM\prompts\deep_dive_22_life_stages.md
# Use: Send to Claude after DD21 is complete
# Priority: PHASE C, Sprint 15

================================================================================
CONTEXT INJECTION — READ FIRST
================================================================================

You are doing Deep Dive 22 on the SIMSIV life stage model.

Before doing ANYTHING, read:
  1. D:\EXPERIMENTS\SIM\CHAIN_PROMPT.md
  2. D:\EXPERIMENTS\SIM\devlog\DEV_LOG.md
  3. D:\EXPERIMENTS\SIM\models\agent.py
  4. D:\EXPERIMENTS\SIM\engines\mortality.py (age-based mechanics)
  5. D:\EXPERIMENTS\SIM\engines\reproduction.py (fertility windows)
  6. D:\EXPERIMENTS\SIM\STATUS.md

Current model: biological life stages exist (fertility windows, age decay,
childhood mortality). But social life stages are absent. In all human societies,
life is structured into recognized social phases with associated roles,
obligations, and behavioral expectations — not just biological age brackets.
A young male entering adulthood doesn't just become fertile; he enters a
period of status competition, risk-taking, and coalition building. An elder
doesn't just decay; they become an advisor, norm transmitter, and repository
of social memory. These social roles shape behavior independently of biology.

================================================================================
DEEP DIVE 22: LIFE STAGE SOCIAL ROLES
================================================================================

FIVE LIFE STAGES:

  CHILDHOOD (age 0 to age_first_reproduction):
    Already partially modeled (DD06/DD13)
    Social role: learning, trust building with family, developing traits
    DD22 additions: peer group formation, learning rate (conformity boost in childhood)

  YOUNG ADULT / INITIATION PHASE (age_first_reproduction to age_first_reproduction+10):
    Currently: just became fertile, enters mating pool, nothing special
    Real pattern: most intense period of status competition, risk-taking, coalition formation
    Social role: proving ground — establish position in hierarchy
    DD22 additions: elevated risk-taking, higher conflict initiation, intense alliance building
    This is the "young male effect" — documented cross-culturally

  PRIME ADULT / ESTABLISHED PHASE (age 25-45 approx):
    Currently: main reproductive and productive years
    Social role: pair bonding, parenting, resource accumulation, faction leadership
    DD22 additions: reduced risk-taking vs youth, parenting investment peak,
    eligibility for faction leadership (DD20) requires being in this stage

  MATURE ADULT / SENIOR PHASE (age 45-60 approx):
    Currently: fertility ends for females, gradual health decay
    Social role: reduced direct competition, increased advisory role
    DD22 additions: social memory repository — high-reputation senior agents
    have norm transmission effect on younger faction members
    Post-reproductive females become grandmothers (DD06 already partially covers this)
    Male elders become wisdom keepers — prestige from experience, not strength

  ELDER / DECLINE PHASE (age 60+):
    Currently: high death probability, continued health decay
    Social role: ritual role, dispute memory, lineage keeper
    DD22 additions: elder agents anchor norm stability (slow institutional decay)
    Very old agents (age 70+) with high reputation = living cultural memory

QUESTIONS TO RESOLVE AND IMPLEMENT:

A. LIFE STAGE COMPUTATION
   Each agent has a computed life_stage property:
   - CHILDHOOD: age < config.age_first_reproduction
   - YOUTH: config.age_first_reproduction <= age < age_first_reproduction + 10
   - PRIME: age_first_reproduction + 10 <= age < 45
   - MATURE: 45 <= age < 60
   - ELDER: age >= 60
   These are computed from age — not stored (always current).

B. YOUTH PHASE EFFECTS
   Young adults (initiation phase) are biologically primed for competition:
   - Conflict initiation: +25% probability multiplier
   - Risk tolerance expression: youth_risk_multiplier * risk_tolerance
     (genetically risk-tolerant youth are dramatically more risk-tolerant)
   - Alliance formation: +50% rate of trust building with same-cohort peers
     (bonding with peers who entered adulthood together — cohort effect)
   - Status hunger: status_drive expression multiplied in youth phase
   - Lower patience: shorter conflict cooldown recovery time
   Female youth: parallel pattern but expressed through mate evaluation
   (highly choosy in youth, accepting configurable female_choosiness_age_effect)

C. PRIME ADULT EFFECTS
   Established adults are the productive core:
   - Parenting investment peak: highest child_investment_per_year expression
   - Leadership eligibility: must be in PRIME phase to be elected war leader
     (peace chief can be PRIME or MATURE)
   - Risk moderation: risk expression returns toward genetic baseline
   - Resource accumulation peak: experience bonus maxes out

D. MATURE ADULT EFFECTS
   Post-prime adults shift from competition to maintenance:
   - Conflict initiation: -20% multiplier (wisdom reduces aggression)
   - Advisory role: mature agents in same faction as youth agents have
     conformity_bias-weighted influence on youth behavior
     (elders moderating youth violence — documented in many cultures)
   - Social memory: mature agents retain more ledger entries (cap raised to 150)
   - Grandmother effect: already in DD06 — grandparent survival bonus

E. ELDER EFFECTS
   Very old agents serve special social functions:
   - Norm anchor: elder agents with high reputation slow institutional drift
     (institutional inertia boost proportional to count of respected elders)
   - Dispute memory: elders remember past conflicts and can testify
     (reduces conflict probability between agents who have shared elder memory)
   - Lineage keeper: elder's death triggers a "cultural memory loss" event
     if they were the last link to founding generation
   - Peaceful presence: high-reputation elders in a faction reduce
     out-group conflict probability (wisdom/diplomacy effect)

F. COHORT EFFECTS
   Agents born in same year-range (±3yr) form implicit cohorts:
   - Youth in same cohort build trust faster (+50% rate with same-cohort peers)
   - Cohort solidarity: agents who fought together in youth maintain
     strong trust bonds into adulthood (shared history effect)
   - Cohort competition: same-cohort males also compete hardest against each other
     (both strongest allies AND strongest rivals from same cohort)

G. INITIATION EVENTS
   When an agent crosses from CHILDHOOD to YOUTH (age 15):
   - Log "maturation" event (already exists from DD16)
   - Apply developmental modifications (DD16)
   - Agent enters mating pool
   - Social: youth agents from same faction recognize each other as cohort-mates
     (automatic trust boost with same-faction cohort members)

H. METRICS
   - youth_conflict_rate: violence rate among youth agents specifically
   - elder_count: number of living elders
   - cohort_cohesion: average trust within same-generation cohort groups
   - life_stage_distribution: fraction of population in each stage

================================================================================
DELIVERABLES
================================================================================

1. docs/deep_dive_22_life_stages.md — design decisions and stage definitions
2. models/agent.py — life_stage computed property, cohort_year field
3. engines/conflict.py — life stage conflict modifiers
4. engines/resources.py — elder norm anchor effect on institutional drift
5. engines/institutions.py — elder stability effect on law_strength decay
6. engines/mating.py — life stage effects on choosiness and mate search
7. config.py additions — life stage parameters
8. metrics/collectors.py — 4 new life stage metrics
9. DEV_LOG.md entry
10. CHAIN_PROMPT.md + STATUS.md update

================================================================================
NEW CONFIG PARAMETERS
================================================================================

life_stages_enabled: bool = True
youth_conflict_multiplier: float = 1.25      # elevated conflict initiation for youth
youth_risk_multiplier: float = 1.4           # amplified risk tolerance expression
youth_trust_building_multiplier: float = 1.5 # faster trust with same-cohort peers
prime_parenting_multiplier: float = 1.2      # peak parenting investment expression
mature_conflict_dampening: float = 0.8       # reduced conflict initiation for mature adults
mature_ledger_cap: int = 150                 # expanded social memory for mature+
elder_norm_anchor_strength: float = 0.3      # elder effect on institutional inertia
elder_conflict_damping: float = 0.15         # elder presence reduces out-group conflict
cohort_range_years: int = 3                  # age range defining a cohort

================================================================================
CONSTRAINTS
================================================================================

- Life stages must be COMPUTED from age — never stored (avoids sync issues)
- Stage effects must be SOFT MULTIPLIERS — not absolute behavioral overrides
- Youth violence increase must be MODERATE — not enough to destabilize populations
- Elder effects must be SMALL individually but significant in aggregate
- Backward compatibility: life_stages_enabled=False = current behavior
- Run validation: youth agents should show measurably higher conflict rates
  elder presence should correlate with lower institutional drift rate
