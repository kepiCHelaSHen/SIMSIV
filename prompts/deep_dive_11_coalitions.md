# SIMSIV — PROMPT: DEEP DIVE 11 — COALITION PUNISHMENT AND DEFECTOR CONTROL
# File: D:\EXPERIMENTS\SIM\prompts\deep_dive_11_coalitions.md
# Use: Send to Claude after DD10 is complete
# Priority: PHASE C, Sprint 4

================================================================================
CONTEXT INJECTION — READ FIRST
================================================================================

You are doing Deep Dive 11 on the SIMSIV coalition and third-party punishment model.

Before doing ANYTHING, read:
  1. D:\EXPERIMENTS\SIM\CHAIN_PROMPT.md
  2. D:\EXPERIMENTS\SIM\devlog\DEV_LOG.md
  3. D:\EXPERIMENTS\SIM\engines\conflict.py (current conflict model)
  4. D:\EXPERIMENTS\SIM\engines\resources.py (cooperation networks)
  5. D:\EXPERIMENTS\SIM\models\agent.py (reputation_ledger, partner_ids)
  6. D:\EXPERIMENTS\SIM\STATUS.md (latest results)

The current cooperation model allows resource sharing among trusted allies.
The current conflict model handles bilateral fights. But one of the most
important mechanisms maintaining cooperation in real societies is third-party
punishment — agents who were NOT directly harmed punish defectors anyway,
at cost to themselves. This is what makes cooperation stable at scale.
Without it, defectors can exploit many bilateral partners before being
caught. This deep dive adds coalition-level social enforcement.

================================================================================
DEEP DIVE 11: COALITION PUNISHMENT AND DEFECTOR CONTROL
================================================================================

CURRENT STATE:
  - Cooperation: bilateral trust-based resource sharing (DD02)
  - Conflict: bilateral fights, winner/loser reputation updates
  - Gossip (DD07): information spread about bad actors
  - No third-party punishment: if A attacks B, only B responds
  - No coalition defense: B's allies don't help B during an attack
  - No ostracism: chronic defectors aren't excluded from networks
  - No altruistic punishment: no agent pays a cost to punish non-partners

CORE CONCEPTS:
  Third-party punishment: agent C punishes agent A for harming agent B,
  even though C wasn't directly harmed. C pays a cost (resources, health risk)
  to impose a cost on A. This is altruistic — C gets no direct benefit.
  Coalition defense: when A attacks B, B's trusted allies have a chance
  to intervene, changing the odds or deterring the attack entirely.
  Ostracism: agents with very low reputation in a community are excluded
  from resource sharing networks, cooperation bonuses, and status gains.

QUESTIONS TO RESOLVE AND IMPLEMENT:

A. THIRD-PARTY PUNISHMENT
   - Who punishes? Only high-cooperation agents? Only agents with trust > threshold?
   - What triggers punishment? Witnessing a conflict? Hearing about it via gossip?
   - What is the punishment action? Resource fine? Health damage? Status loss?
   - What is the cost to the punisher? (small but real — altruistic punishment
     is costly, which is what makes it interesting)
   - How does cooperation_propensity gate punishment willingness?
   - Should there be a "punishment threshold"? (only punish severe violations)

B. COALITION DEFENSE
   - When agent A initiates conflict against agent B, should B's trusted allies
     have a chance to intervene?
   - Intervention probability: function of ally's trust in B, ally's aggression,
     ally's health, and distance from fight (proximity proxy)
   - Intervention effect: reduces A's combat power, or triggers A to flee,
     or adds a second conflict against A
   - Should coalition defense create reputation gains for the defender?
     (prestige reward for protecting allies)
   - Should failed coalition defense damage the ally's reputation?
     (tried to help but lost — social cost?)

C. OSTRACISM MECHANICS
   - Should agents with very low reputation be excluded from cooperation networks?
   - Ostracism threshold: reputation below X → no resource sharing, no ally support
   - Should ostracism be recoverable? (reputation slowly rebuilds if no violations)
   - Should ostracism affect mating? (females avoid ostracized males)
   - Should high-law-strength societies enforce ostracism more strongly?
     (institutional backing for social exclusion)

D. FREE-RIDER DETECTION
   - Currently agents only build distrust through direct negative interactions
   - Should agents be able to detect free-riders? (agents who accept sharing
     but never share themselves)
   - Detection probability: function of intelligence_proxy and network size
   - Consequence: detected free-riders lose trust faster, may be ostracized
   - Should this create arms race between free-rider detection and free-rider
     concealment strategies?

E. PUNISHMENT NORMS AND INSTITUTIONS
   - Should punishment willingness be modulated by law_strength?
     (strong institutions: formal punishment; weak: informal/vigilante)
   - Should punishment be coordinated? (coalitions agree to punish together)
   - Should there be punishment of punishment-avoiders?
     (agents who fail to punish defectors when they should are themselves sanctioned)
   - This is the second-order punishment problem — implement carefully

F. SELECTION EFFECTS
   Expected outcomes after this deep dive:
   - Cooperation becomes more stable (defectors get punished)
   - Aggression declines faster (violent agents face coalition retaliation)
   - Social stratification by reputation becomes sharper
   - High-cooperation agents have larger, more protective networks
   - Low-reputation agents have worse survival even without direct conflict

================================================================================
DELIVERABLES
================================================================================

1. docs/deep_dive_11_coalitions.md — design decisions
2. engines/conflict.py — coalition defense and third-party punishment
3. engines/resources.py — ostracism exclusion from sharing
4. engines/mating.py — ostracism effects on mate choice
5. config.py additions — coalition and punishment parameters
6. metrics/collectors.py — coalition metrics (third_party_punishments,
   coalition_defenses, ostracized_agents)
7. DEV_LOG.md entry
8. CHAIN_PROMPT.md update

================================================================================
NEW PARAMETERS TO ADD TO CONFIG
================================================================================

third_party_punishment_enabled: bool = True
punishment_willingness_threshold: float = 0.6  # cooperation_propensity to punish
punishment_cost_fraction: float = 0.05         # fraction of punisher's resources spent
punishment_severity: float = 0.1              # resource loss imposed on punished agent
coalition_defense_enabled: bool = True
coalition_defense_probability: float = 0.3    # base chance ally intervenes
coalition_defense_trust_threshold: float = 0.65  # trust required to intervene
ostracism_enabled: bool = True
ostracism_reputation_threshold: float = 0.25  # below this = ostracized
ostracism_recovery_rate: float = 0.01         # annual reputation recovery if no violations
free_rider_detection_rate: float = 0.1        # annual chance of detecting non-sharing

================================================================================
CONSTRAINTS
================================================================================

- Third-party punishment must be COSTLY to the punisher — if it's free,
  it's just a reputation update and loses the altruism dynamic
- Coalition defense must not make strong agents untouchable — interventions
  are probabilistic and carry risk for the defender
- Ostracism must be GRADUAL — no instant exclusion, recovery must be possible
- Do not create O(n³) computation — coalition mechanics must use sampling
