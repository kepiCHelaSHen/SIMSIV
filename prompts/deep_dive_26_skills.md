# SIMSIV — PROMPT: DEEP DIVE 26 — SKILL ACQUISITION AND CULTURAL KNOWLEDGE
# File: D:\EXPERIMENTS\SIM\prompts\deep_dive_26_skills.md
# Use: Send to Claude after DD25 is complete
# Priority: PHASE C, Sprint 19

================================================================================
CONTEXT INJECTION — READ FIRST
================================================================================

You are doing Deep Dive 26 on the SIMSIV skill acquisition and cultural knowledge model.

Before doing ANYTHING, read:
  1. D:\EXPERIMENTS\SIM\CHAIN_PROMPT.md
  2. D:\EXPERIMENTS\SIM\devlog\DEV_LOG.md
  3. D:\EXPERIMENTS\SIM\models\agent.py (intelligence_proxy, emotional_intelligence from DD15)
  4. D:\EXPERIMENTS\SIM\engines\resources.py (production mechanics)
  5. D:\EXPERIMENTS\SIM\engines\conflict.py (combat resolution)
  6. D:\EXPERIMENTS\SIM\engines\reproduction.py (parental investment)
  7. D:\EXPERIMENTS\SIM\STATUS.md

The current model treats agent capabilities as purely genetic — your intelligence
trait determines your resource acquisition, your aggression determines your combat
effectiveness. But in reality, humans accumulate skills through practice and
experience that partially decouple capabilities from genetics. A low-intelligence
agent who has spent 20 years foraging is more effective than a high-intelligence
youth who just entered adulthood. This accumulated experiential knowledge:
  - Reduces genetic determinism (nurture complements nature)
  - Creates age-based advantages separate from health decline
  - Enables cultural knowledge transmission between generations
  - Seeds the division of labor that eventually produces chiefdoms and states

================================================================================
DEEP DIVE 26: SKILL ACQUISITION AND CULTURAL KNOWLEDGE
================================================================================

FOUR SKILL DOMAINS:

  FORAGING_SKILL: float [0.0-1.0]
    Represents: resource extraction efficiency, route knowledge, seasonal patterns
    Grows through: successful resource acquisition phases (above-average yields)
    Decays: slowly without use (0.02/yr), faster if resources consistently scarce
    Effect: multiplies subsistence resource gain in Phase 2 of resource engine
    Peak age: 30-45 (experience peak)
    Transmission: can be taught to offspring (social learning)

  COMBAT_SKILL: float [0.0-1.0]
    Represents: fighting technique, tactical awareness, weapon handling
    Grows through: conflict wins (especially against skilled opponents)
    Decays: slowly without use (0.03/yr), faster after injury
    Effect: adds to combat power in conflict resolution
    Interacts with: physical_robustness (DD15) and health — skilled but injured agent
    Peak age: 20-35 (physical prime)
    Transmission: can be taught within faction (mentor-apprentice)

  SOCIAL_SKILL: float [0.0-1.0]
    Represents: negotiation, alliance building, reading social situations
    Grows through: successful cooperation events, gossip accuracy, mating success
    Decays: very slowly (0.01/yr) — social knowledge persists
    Effect: boosts trust-building rate and gossip effectiveness
    Interacts with: emotional_intelligence (DD15) — synergistic effect
    Peak age: 35-55 (social prime — elders are most socially skilled)
    Transmission: primarily through observation and experience

  CRAFT_SKILL: float [0.0-1.0]  [only active if DD21 resource_types is enabled]
    Represents: tool-making, construction, material processing efficiency
    Grows through: tool production phases in resource engine
    Decays: slowly (0.02/yr)
    Effect: multiplies tool production rate, improves tool quality multiplier
    Interacts with: intelligence_proxy — smart crafters improve faster
    Peak age: 25-50 (steady prime)
    Transmission: strongest transmission (craft knowledge is explicit and teachable)

QUESTIONS TO RESOLVE AND IMPLEMENT:

A. SKILL INITIALIZATION
   All agents start with low skills at maturation (age 15):
   - Base skill = intelligence_proxy * 0.2 (genetic head start, not starting from zero)
   - Youth agents have low skills regardless of genetics
   - This creates a realistic age-advantage separate from health

B. SKILL ACQUISITION MECHANICS
   Skills grow through successful exercise:

   Foraging skill:
   - If agent's resource gain this tick > band_average * 1.1:
     foraging_skill += 0.01 * (1 - foraging_skill * 0.8)  # diminishing returns
   - intelligence_proxy accelerates learning: learning_rate *= (0.7 + intel * 0.6)

   Combat skill:
   - On conflict WIN: combat_skill += 0.02 * (opponent_skill - own_skill + 0.3)
     (learn more from beating skilled opponents)
   - On conflict LOSS: combat_skill += 0.005 (learn from defeat too, but less)
   - Capped by physical_robustness: very frail agents can't fully utilize skill

   Social skill:
   - Per successful cooperation event: +0.005
   - Per new bond formed: +0.01
   - Per gossip event where agent's trust assessment proved accurate: +0.005
   - emotional_intelligence (DD15) accelerates: learning_rate *= (0.8 + ei * 0.4)

   Craft skill (if DD21 active):
   - Per tool produced: +0.01 * (1 - craft_skill * 0.8)
   - Per tool traded: +0.005 (trade refines craftsmanship understanding)

C. SKILL EFFECTS ON ENGINES
   Each skill modifies its domain's outcomes:

   Foraging skill → Resources engine Phase 2:
   effective_intelligence = intelligence_proxy * (0.6 + foraging_skill * 0.8)
   (skill multiplies but doesn't replace intelligence — synergistic)

   Combat skill → Conflict engine combat power:
   agg_power += combat_skill * combat_skill_weight  # default 0.15
   (skilled fighters are more dangerous regardless of raw aggression)

   Social skill → Reputation engine:
   - Trust building rate: * (0.8 + social_skill * 0.4)
   - Gossip spread efficiency: * (0.9 + social_skill * 0.2)
   - Mating trust bonus: female's trust assessment of male is sharper
     when female has high social skill (better judge of character)

   Craft skill → Resources engine tool production:
   tools_produced *= (0.5 + craft_skill * 1.0)
   (master craftsman produces 1.5x tools vs novice)

D. SKILL DECAY AND AGING
   Skills have different decay profiles:
   - Foraging: 0.02/yr baseline, 0.05/yr if agent is not foraging
     (sedentary agents lose foraging knowledge)
   - Combat: 0.03/yr baseline, 0.08/yr post-injury (injury disrupts practice)
   - Social: 0.01/yr (nearly permanent — social knowledge persists)
   - Craft: 0.02/yr baseline (craft knowledge durable but needs practice)

   Age effects:
   - Learning rate slows after age 45: * max(0.3, 1 - (age-45)*0.03)
   - Skills do NOT automatically decline with age — only decay from disuse
   - This creates the elder advantage: old agents have high social skill
     despite declining health — compensates for physical decline

E. SKILL TRANSMISSION (CULTURAL KNOWLEDGE)
   Skills can be transferred between agents — this is cultural knowledge:

   Parent → child transmission (social learning at maturation):
   - At age 15, child gains: parent_skill * social_learning_fraction
   - Default fraction: 0.3 (child starts at 30% of parent's skill level)
   - conformity_bias (DD15) increases transmission fraction
   - This creates skill dynasties: families of skilled foragers, fighters, crafters

   Mentor → apprentice (within faction):
   - High-skilled agents in same faction can mentor low-skilled same-age-range agents
   - Mentor must have skill > 0.6 AND apprentice must have skill < 0.4
   - Annual transfer: apprentice_skill += mentor_skill * 0.05
   - Mentor's skill unchanged (teaching doesn't cost knowledge)
   - This is the cultural knowledge transmission mechanism

   Elder teaching:
   - Social skill transfers most effectively from elders (age 55+, social_skill > 0.5)
   - Elder mentoring: +0.03 social skill per year to young faction members
   - Models the "wisdom transmission" role of elders from DD22

F. SKILL INEQUALITY AND EMERGENT SPECIALISTS
   Over time, skill distribution should diverge:
   - Some agents specialize through feedback loops:
     good forager → more resources → more time to forage → better forager
   - skill_gini will emerge for each domain
   - In STRONG_STATE: craft skills should concentrate (specialization with
     institutional support)
   - In FREE_COMPETITION: combat skill should concentrate among survivors

   Specialists in the band fingerprint:
   - top_forager_skill, top_combat_skill, top_social_skill
   - specialist_fraction: agents with any skill > 0.7 (measures specialization)
   These export to clan level (skilled bands are more valuable allies/dangerous enemies)

G. METRICS
   - avg_foraging_skill, avg_combat_skill, avg_social_skill, avg_craft_skill
   - skill_gini (per domain): inequality in skill distribution
   - skill_age_correlation: correlation between age and social skill
     (should be positive — validates elder advantage)
   - mentor_events: count of skill transmission events per year
   - specialist_count: agents with any skill > 0.7

================================================================================
DELIVERABLES
================================================================================

1. docs/deep_dive_26_skills.md — design decisions and skill formulas
2. models/agent.py — 4 skill fields (foraging_skill, combat_skill, social_skill,
   craft_skill — all float [0.0-1.0])
3. engines/resources.py — foraging skill in competitive weight, craft skill in tools
4. engines/conflict.py — combat skill in power calculation
5. engines/reputation.py — social skill in trust building and gossip
6. engines/mating.py — social skill in female assessment accuracy
7. engines/reproduction.py — skill transmission at maturation (age 15)
8. config.py additions — skill parameters
9. metrics/collectors.py — 12 new skill metrics
10. DEV_LOG.md entry
11. CHAIN_PROMPT.md + STATUS.md update

================================================================================
NEW CONFIG PARAMETERS
================================================================================

skills_enabled: bool = True
skill_learning_rate_base: float = 0.01      # base annual skill gain rate
skill_foraging_decay: float = 0.02          # annual foraging skill decay
skill_combat_decay: float = 0.03            # annual combat skill decay
skill_social_decay: float = 0.01            # annual social skill decay
skill_craft_decay: float = 0.02             # annual craft skill decay
skill_parent_transmission: float = 0.30     # fraction of parent skill to child at maturation
skill_mentor_transfer_rate: float = 0.05    # annual transfer from mentor to apprentice
skill_age_learning_decline_start: int = 45  # age at which learning slows
combat_skill_weight: float = 0.15           # combat skill contribution to power
skill_learning_intelligence_multiplier: float = 0.6  # how much intel boosts learning

================================================================================
CONSTRAINTS
================================================================================

- Skills are NON-HERITABLE — transmitted via social learning, not breed()
  (only the genetic potential to learn quickly is heritable — intelligence)
- Skill effects must COMPLEMENT not REPLACE trait effects
  (high combat skill + low aggression is a defensive skilled fighter, not an aggressor)
- craft_skill only active if DD21 resource_types is also enabled
- Skill decay must be slow enough for elders to maintain social advantage
- Backward compatibility: skills_enabled=False = current behavior
- Run validation: after 200yr, expect positive skill_age_correlation for social skill
  and skill_gini > 0.2 for combat skill (natural specialization)
