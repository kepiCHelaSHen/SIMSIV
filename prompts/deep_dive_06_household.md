# SIMSIV — PROMPT: DEEP DIVE 06 — OFFSPRING AND HOUSEHOLD
# File: D:\EXPERIMENTS\SIM\prompts\deep_dive_06_household.md
# Use: Send to Claude after DD01-DD05 are complete
# Priority: PHASE B, Sprint 6

================================================================================
CONTEXT INJECTION — READ FIRST
================================================================================

You are doing Deep Dive 06 on the SIMSIV reproduction engine and household model.

Before doing ANYTHING, read:
  1. D:\EXPERIMENTS\SIM\CHAIN_PROMPT.md
  2. D:\EXPERIMENTS\SIM\devlog\DEV_LOG.md
  3. D:\EXPERIMENTS\SIM\engines\reproduction.py (current implementation)
  4. D:\EXPERIMENTS\SIM\engines\resources.py (child investment phase)
  5. D:\EXPERIMENTS\SIM\models\agent.py (breed(), offspring_ids, parent_ids)
  6. D:\EXPERIMENTS\SIM\config.py
  7. D:\EXPERIMENTS\SIM\STATUS.md (latest results)

The current reproduction engine handles conception, EPC-aware paternity, birth,
and infant survival. But there is no ongoing household model — no sibling
relationships, no extended family structure, no lifecycle transitions beyond
the binary fertile/not-fertile check. This deep dive creates a household layer.

================================================================================
DEEP DIVE 06: OFFSPRING AND HOUSEHOLD
================================================================================

CURRENT STATE:
  - reproduction.py: conception chance based on fertility, resources, health,
    pair bond status. EPC-aware paternity from DD01.
  - Child survival: one-shot check at birth based on parental resources,
    bond strength, scarcity, kin network.
  - Child investment: resources.py Phase 3 charges parents per dependent per year
  - Children enter population at age 0, become fertile at age 15
  - No childhood development model between ages 0-15
  - No sibling relationships tracked
  - No grandparent effects
  - offspring_ids grows monotonically — no cleanup of dead offspring references

POST-DD02 DATA POINTS:
  - child_survival_rate fluctuates around 83% (baseline)
  - child_investment_per_year = 0.5 resources per dependent per year
  - child_dependency_years = 5 (short — typical pre-industrial is 10-15)
  - Average offspring count per agent: ~1.0 at year 200
  - Kin trust maintenance: parents + dependent children build trust (+0.02/yr)
  - Reproduction costs female 2.0 resources per birth (one-time)

QUESTIONS TO RESOLVE AND IMPLEMENT:

A. CHILDHOOD DEVELOPMENT MODEL
   Children are currently inert from age 0 to 15 (only consuming resources).
   - Should children develop skills during childhood that affect adult traits?
     (e.g., high-resource childhood → intelligence boost at maturity)
   - Should parental trait values influence childhood outcomes?
     (nurture component on top of nature/genetics)
   - Should childhood quality affect adult health? (stunting from malnutrition)
   - Should dependency period be longer? (5 years is short — 10 is more realistic)

B. CHILD MORTALITY MODEL
   Currently: single survival check at birth, then no further childhood risk.
   - Should there be ongoing childhood mortality risk each year until maturity?
     (pre-industrial: ~30-50% of children died before age 15)
   - Should childhood mortality be resource-dependent each year?
     (poor families lose more children)
   - Should orphan status dramatically increase childhood mortality?
   - Should disease/scarcity events spike childhood deaths?

C. HOUSEHOLD STRUCTURE
   No formal household concept exists.
   - Should agents be grouped into households? (parents + dependent children)
   - Should household size affect resource efficiency? (economies of scale)
   - Should single-parent households have penalties? (lower child survival,
     less resource efficiency)
   - Should blended families (re-pairing with existing children) be modeled?
   - Is a formal household model worth the complexity, or is the implicit
     tracking via partner_ids + offspring_ids sufficient?

D. SIBLING RELATIONSHIPS
   Currently no sibling awareness.
   - Should siblings build mutual trust? (like kin trust in DD02 but sibling-specific)
   - Should siblings cooperate or compete? (resource competition within family
     vs cooperative family units)
   - Should birth order effects exist? (firstborn advantage in primogeniture
     societies, or attention competition in large families)
   - Should sibling count affect child survival? (more siblings = less
     resources per child — the quantity-quality tradeoff)

E. FERTILITY AND BIRTH SPACING
   Current: each fertile female has conception_chance each year, no spacing.
   - Should there be a mandatory birth interval? (2-3 years in pre-industrial
     societies due to lactation)
   - Should fertility decline gradually with maternal age?
     (currently: binary fertile window 15-45)
   - Should maternal health be affected by rapid successive births?
   - Should there be a maximum lifetime births cap based on fertility_base?

F. GRANDPARENT AND EXTENDED KIN EFFECTS
   Currently: only parent-child kin trust is modeled.
   - Should grandparents provide childcare bonuses?
     ("grandmother hypothesis" — post-menopausal women boost grandchild survival)
   - Should extended kin networks reduce conflict probability?
     (large clans deter attacks on members)
   - Should kin group size affect mating success?
     (comes from a "good family" = better mate value)

G. ORPHAN MODEL
   Currently: if both parents die, children have no special handling.
   - Should orphans be adopted by kin? (nearest living relative in trust network)
   - Should orphans have reduced survival rates?
   - Should orphan status create permanent health/status disadvantage?
   - Should the institution engine handle orphan care when law_strength is high?

================================================================================
DELIVERABLES
================================================================================

1. docs/deep_dive_06_household.md — design decisions
2. engines/reproduction.py — updated implementation
3. engines/resources.py — updated child investment if needed
4. models/agent.py updates — if new household/sibling attributes needed
5. config.py additions — household/reproduction parameters
6. metrics/collectors.py additions — household metrics
7. DEV_LOG.md entry
8. CHAIN_PROMPT.md update

================================================================================
NEW PARAMETERS TO CONSIDER FOR CONFIG
================================================================================

birth_interval_years: int = 2             # minimum years between births per female
childhood_mortality_annual: float = 0.02  # annual death risk for children 0-15
orphan_mortality_multiplier: float = 2.0  # mortality multiplier for parentless children
childhood_nutrition_effect: float = 0.1   # resource-quality bonus to adult traits
grandparent_survival_bonus: float = 0.05  # survival bonus if grandparent alive
sibling_trust_growth: float = 0.01        # annual trust growth between siblings
max_lifetime_births: int = 12             # hard cap on births per female
maternal_health_cost: float = 0.03        # health cost per birth to mother
quantity_quality_tradeoff: float = 0.1    # child investment penalty per additional sibling

================================================================================
CONSTRAINTS
================================================================================

- Do not break any other engine
- Household model should be LIGHTWEIGHT — avoid creating a separate data structure
  if existing agent relationships (partner_ids, offspring_ids, parent_ids) suffice
- Population dynamics must remain stable — childhood mortality additions must be
  balanced against birth rates to avoid population collapse
- All new parameters must have defaults that produce current-like behavior
