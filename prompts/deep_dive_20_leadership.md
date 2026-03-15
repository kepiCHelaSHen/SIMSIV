# SIMSIV — PROMPT: DEEP DIVE 20 — LEADERSHIP AND COLLECTIVE COORDINATION
# File: D:\EXPERIMENTS\SIM\prompts\deep_dive_20_leadership.md
# Use: Send to Claude after DD19 is complete
# Priority: PHASE C, Sprint 13

================================================================================
CONTEXT INJECTION — READ FIRST
================================================================================

You are doing Deep Dive 20 on the SIMSIV leadership model.

Before doing ANYTHING, read:
  1. D:\EXPERIMENTS\SIM\CHAIN_PROMPT.md
  2. D:\EXPERIMENTS\SIM\devlog\DEV_LOG.md
  3. D:\EXPERIMENTS\SIM\models\agent.py (prestige_score, dominance_score, faction_id)
  4. D:\EXPERIMENTS\SIM\models\society.py (faction detection)
  5. D:\EXPERIMENTS\SIM\engines\institutions.py
  6. D:\EXPERIMENTS\SIM\STATUS.md

Prestige and dominance exist in the model. Factions have emergent leaders
(highest prestige+dominance agent in a faction). But leadership is currently
implicit — the leader has no special behavioral effects on their faction members,
no coordination role, and no influence on collective decisions. In pre-state
societies, leadership is primarily informal (prestige-based) but still has
real effects: leaders coordinate group responses to threats, arbitrate disputes,
represent the group in inter-band interactions, and influence norm adoption.
This deep dive makes leadership explicit and behaviorally consequential.

================================================================================
DEEP DIVE 20: LEADERSHIP AND COLLECTIVE COORDINATION
================================================================================

CORE DESIGN:
  Leadership in pre-state societies is:
  - EARNED not assigned — emerges from prestige + dominance + age
  - INFORMAL not bureaucratic — no formal authority, influence via reputation
  - COSTLY — leaders must demonstrate generosity and competence to maintain
  - UNSTABLE — can be lost through failure, age, or rival emergence
  - CONTEXT-DEPENDENT — different leaders for different domains
    (war leader vs peace chief vs spiritual elder — simplify to 2: war + peace)

TWO LEADERSHIP TYPES:

  WAR LEADER (dominance-based):
    Selected by: highest dominance_score in faction
    Role: coordinates conflict initiation, boosts faction combat effectiveness
    Tenure: maintained while dominance_score remains highest in faction
    Cost: must successfully lead raids/defenses or lose followers

  PEACE CHIEF (prestige-based):
    Selected by: highest prestige_score in faction
    Role: dispute arbitration, resource sharing coordination, norm enforcement
    Tenure: maintained while prestige_score remains highest in faction
    Cost: must demonstrate generosity (resource display) periodically

  Same agent can hold both roles (warrior-chief archetype) if they have
  both high dominance and high prestige. This is historically rare but exists.

QUESTIONS TO RESOLVE AND IMPLEMENT:

A. LEADER SELECTION AND STORAGE
   Leader computed from faction membership each time factions are detected.
   Store on Society, not on Agent:
   - society.faction_leaders: dict[faction_id, dict]
     {'war_leader': agent_id, 'peace_chief': agent_id, 'established_year': int}

   Selection criteria:
   - War leader: highest dominance_score among faction members
   - Peace chief: highest prestige_score among faction members
   - Minimum threshold: must exceed avg_faction_score * 1.2 to be recognized
     (if no one stands out, faction has no recognized leader — common in egalitarian bands)

B. WAR LEADER EFFECTS
   When faction has a recognized war leader:
   - Faction conflict initiation: member aggression boosted 20% when war leader
     has recently won a conflict (leadership inspiration effect)
   - Coalition defense: war leader automatically joins coalition defense of
     any faction member (loyalty obligation)
   - Combat bonus: faction members fighting alongside war leader get +0.05
     to combat power (coordination effect)
   - Deterrence: factions with strong war leaders are targeted less by rivals
     (deterrence multiplier on out-group conflict probability)

C. PEACE CHIEF EFFECTS
   When faction has a recognized peace chief:
   - Dispute arbitration: when two faction members initiate conflict with each
     other, peace chief can intervene (probability = prestige_score * 0.4)
     Intervention: reduces conflict probability by 50% (negotiation)
   - Resource coordination: peace chief facilitates cooperation sharing within
     faction (sharing_rate boost +10% for faction members)
   - Norm transmission: peace chief's trait values influence faction members
     via conformity_bias (peer influence effect from DD16)
   - Inheritance facilitation: peace chief witnesses inheritance distribution,
     reducing disputed inheritance events

D. LEADERSHIP COSTS AND TENURE
   Leaders must maintain their position actively:

   War leader cost: must win or participate in defense at least once per N years
   Failure penalty: if war leader loses badly (high power_diff loss), lose
   dominance_score -0.15 (humiliation) and war leader role passes to next highest

   Peace chief cost: must display resources at least once per N years
   (resource_display from DD12 counts)
   Failure: if peace chief fails to display for too long, prestige decays faster
   and role passes to next highest prestige agent

   Both roles: if leader emigrates (DD19), role immediately passes
   Both roles: old age — agents over age 55 with health < 0.5 lose leadership role

E. INTER-FACTION LEADERSHIP DYNAMICS
   When two factions interact:
   - Trade: peace chiefs of both factions get trust bonus from trade event
     (leaders build diplomatic ties)
   - Conflict: war leaders of opposing factions are prioritized targets
     (killing/defeating rival leader = major dominance gain)
   - Merger: when factions merge, leadership contest determines new leaders
     (higher combined prestige/dominance wins)

F. BAND-LEVEL LEADERSHIP (PROTO-CHIEFDOM SIGNAL)
   If a single agent has faction leadership AND has followers across multiple
   factions (trust > 0.6 with agents in other factions), they become a
   band-level "big man" — a proto-chiefdom precursor.
   Track as: band_influencer_id (agent with highest cross-faction trust)
   This is the signal that the band is approaching chiefdom transition.

G. LEADERSHIP AND THE BAND FINGERPRINT
   Leadership quality is an important export to the clan-level simulator.
   Add to band fingerprint:
   - has_war_leader: bool
   - has_peace_chief: bool
   - leadership_quality: float (combined prestige+dominance of leaders / band avg)
   - big_man_present: bool (proto-chiefdom signal)

================================================================================
DELIVERABLES
================================================================================

1. docs/deep_dive_20_leadership.md — design decisions
2. models/society.py — faction_leaders dict, leader selection methods
3. engines/conflict.py — war leader effects (coalition, combat bonus, deterrence)
4. engines/institutions.py — peace chief effects (arbitration, norm transmission)
5. engines/resources.py — peace chief cooperation coordination
6. config.py additions — leadership parameters
7. metrics/collectors.py — leadership metrics (war_leader_count, peace_chief_count,
   leadership_interventions, big_man_present, faction_leader_turnover)
8. DEV_LOG.md entry
9. CHAIN_PROMPT.md + STATUS.md update

================================================================================
NEW CONFIG PARAMETERS
================================================================================

leadership_enabled: bool = True
war_leader_aggression_boost: float = 0.2     # faction member aggression boost when active
war_leader_combat_bonus: float = 0.05        # combat power boost alongside leader
war_leader_deterrence: float = 0.2           # reduction in being targeted by rivals
peace_chief_arbitration_probability: float = 0.4  # chance to intervene in intra-faction conflict
peace_chief_sharing_boost: float = 0.1       # cooperation sharing rate boost
leadership_minimum_threshold: float = 1.2    # must exceed avg * this to be recognized
war_leader_tenure_years: int = 5             # years before must re-demonstrate
peace_chief_tenure_years: int = 5            # years before must re-demonstrate
leadership_age_limit: int = 55              # age above which health-declining leaders step down

================================================================================
CONSTRAINTS
================================================================================

- Leadership must EMERGE from prestige/dominance — never assigned randomly
- Leaders have INFLUENCE not authority — effects are probabilistic boosts
- Leadership must be LOSABLE — failure and age must remove leaders
- Do not create a "leader agent" subclass — use existing agent with Society-level tracking
- Egalitarian bands (no one meets threshold) must be a valid common state
- Backward compatibility: leadership_enabled=False = current behavior
