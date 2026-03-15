# SIMSIV — PROMPT: DEEP DIVE 07 — MEMORY AND REPUTATION
# File: D:\EXPERIMENTS\SIM\prompts\deep_dive_07_reputation.md
# Use: Send to Claude after DD01-DD06 are complete
# Priority: PHASE B, Sprint 7

================================================================================
CONTEXT INJECTION — READ FIRST
================================================================================

You are doing Deep Dive 07 on the SIMSIV memory and reputation system.

Before doing ANYTHING, read:
  1. D:\EXPERIMENTS\SIM\CHAIN_PROMPT.md
  2. D:\EXPERIMENTS\SIM\devlog\DEV_LOG.md
  3. D:\EXPERIMENTS\SIM\models\agent.py (remember(), trust_of(), reputation_ledger,
     reputation field)
  4. D:\EXPERIMENTS\SIM\engines\resources.py (cooperation sharing, kin trust)
  5. D:\EXPERIMENTS\SIM\engines\conflict.py (trust-based targeting, reputation updates)
  6. D:\EXPERIMENTS\SIM\engines\mating.py (trust bonus in female choice)
  7. D:\EXPERIMENTS\SIM\config.py
  8. D:\EXPERIMENTS\SIM\STATUS.md (latest results)

The reputation system is scattered across multiple engines with no unified model.
Each engine independently calls agent.remember() with different deltas, and
the trust_of() function is read in various places. This deep dive unifies the
reputation system, adds gossip/information spread, and creates proper social
network dynamics.

================================================================================
DEEP DIVE 07: MEMORY AND REPUTATION
================================================================================

CURRENT STATE:
  - reputation_ledger: dict[int, float] — sparse, max 100 entries
  - remember(other_id, delta): updates or creates trust entry
    New entry: 0.5 + delta. Existing: old + delta. Clipped to [0.0-1.0].
    Eviction: if at cap, evict entry closest to neutral (0.5).
  - trust_of(other_id): returns ledger value or 0.5 (neutral default)
  - reputation: float [0.0-1.0] — "public standing score", updated in:
    * conflict.py: aggressor -0.05, institutional punishment -penalty
    * mating.py (EPC): female -0.05 on detection
  - Trust updated by:
    * conflict.py: aggressor→target -0.2, target→aggressor -0.3
    * mating.py: pair bond +0.1, EPC detected: partner→female -0.2, partner→epc_male -0.3
    * resources.py: cooperation sharing +0.05 mutual, kin trust +0.02 mutual

  PROBLEMS:
  - reputation (public) and reputation_ledger (private) are disconnected
  - No gossip: agent A attacks agent B, agent C (B's friend) doesn't learn
  - No reputation decay: trust/distrust is permanent once set
  - No social network structure: connections are implicit via ledger entries
  - Cooperation networks (DD02) work but are small (avg 3.3) because trust
    only builds through direct interaction or kin
  - 100-entry ledger cap means older relationships get evicted

POST-DD02 DATA POINTS:
  - Cooperation network size: avg 3.3 allies (trust > 0.5)
  - Kin trust maintenance: +0.02/yr builds to meaningful trust in ~5 years
  - cooperation_trust_threshold = 0.5 (allies need trust above this)
  - Trust is read in: resource competitive weight, cooperation sharing,
    conflict target selection, female mate choice

QUESTIONS TO RESOLVE AND IMPLEMENT:

A. GOSSIP AND INFORMATION SPREAD
   The most impactful missing feature. Currently trust is purely pairwise.
   - Should agents share information about third parties?
     (A trusts B, B distrusts C → A should learn to distrust C)
   - How to model gossip? Options:
     1. Transitive trust: A's trust of C influenced by B's trust of C,
        weighted by A's trust of B
     2. Event-based gossip: when conflict occurs, nearby agents (in trust
        network) hear about it
     3. Periodic gossip: each tick, agents share a random trust entry
        with a trusted ally
   - How fast should gossip spread? (too fast → homogeneous opinions,
     too slow → no social learning)
   - Should gossip be noisy? (information degrades as it passes through
     multiple agents — telephone game effect)

B. REPUTATION DECAY AND DYNAMICS
   Current: trust never decays — once set, stays forever.
   - Should trust decay toward neutral (0.5) over time?
     (forgetting — old grudges fade, old friendships lose relevance)
   - Should extreme trust values decay slower? (deep trust/distrust persists
     longer than mild opinions)
   - Should there be a "relevance" weight? (trust for living vs dead agents,
     recent vs distant interactions)
   - Should the reputation (public) field be computed from aggregate trust?
     (reputation = average of how others see you, not a separate stat)

C. SOCIAL NETWORK STRUCTURE
   Currently implicit. Should it be explicit?
   - Should the model track network metrics? (clustering coefficient,
     average path length, degree distribution)
   - Should high-degree agents (many connections) have social advantages?
     (information access, cooperation opportunities, deterrence)
   - Should there be a maximum "social bandwidth"? (Dunbar's number ~150)
     Current ledger cap of 100 is in this range.
   - Should network position affect status? (central agents gain status,
     peripheral agents lose it — social capital)

D. TRUST FORMATION PATHWAYS
   Current: only direct interaction or kin trust.
   - Should proximity-based trust exist? (agents in same household,
     same extended family, same status bracket)
   - Should shared enemies create trust? ("enemy of my enemy is my friend")
   - Should cooperative actions be visible to bystanders?
     (witnessing cooperation increases trust in the cooperator)
   - Should trust build faster between similar agents? (homophily —
     similar trait values → faster trust growth)

E. REPUTATION AND MATE VALUE
   Currently reputation is 10% of mate_value.
   - Should reputation weight be context-dependent?
     (in high-institution societies, reputation matters more)
   - Should female choice use reputation_ledger directly rather than
     the abstract reputation field? (A chooses B based on A's trust of B,
     not B's global reputation)
   - DD01 already includes trust bonus in female choice. Is this sufficient?

F. SOCIAL LEARNING AND NORM INTERNALIZATION
   Currently agents don't learn from others' experiences.
   - Should agents observe outcomes of others' strategies and adjust?
     (if high-cooperation agents are visibly richer, observing agents
     increase cooperation — Pavlovian social learning)
   - Should this be a separate heritable trait (social_learning_rate)?
   - Or should conformity be built into the institutional engine?
     (DD05 territory — but the reputation system needs to support it)

G. LEDGER MANAGEMENT
   Current: evict entry closest to neutral (0.5) when at cap.
   - Is the eviction strategy correct? (it preserves strong opinions)
   - Should dead agents be cleaned from ledgers periodically?
     (they consume slots but can never interact)
   - Should ledger size be configurable?
   - Should there be separate friend/enemy lists with different caps?

================================================================================
DELIVERABLES
================================================================================

1. docs/deep_dive_07_reputation.md — design decisions
2. models/agent.py updates — reputation system changes
3. engines/resources.py — updated cooperation network logic if needed
4. engines/conflict.py — gossip/bystander updates
5. config.py additions — reputation parameters
6. metrics/collectors.py additions — social network metrics
7. DEV_LOG.md entry
8. CHAIN_PROMPT.md update

================================================================================
NEW PARAMETERS TO CONSIDER FOR CONFIG
================================================================================

gossip_enabled: bool = True               # enable gossip/information spread
gossip_rate: float = 0.1                  # fraction of trust entries shared per tick
gossip_noise: float = 0.1                 # information degradation per hop
trust_decay_rate: float = 0.01            # annual decay toward neutral
trust_decay_threshold: float = 0.1        # don't decay if |trust - 0.5| > this
reputation_from_ledger: bool = False       # compute reputation from aggregate trust
bystander_trust_update: bool = False       # witnesses update trust ledgers
shared_enemy_trust_bonus: float = 0.0     # "enemy of my enemy" trust boost
homophily_trust_bonus: float = 0.0        # similar traits → faster trust growth
max_reputation_ledger_size: int = 100     # configurable ledger cap
dead_agent_ledger_cleanup: bool = True    # periodically clean dead agents from ledgers

================================================================================
CONSTRAINTS
================================================================================

- Do not break any other engine
- Gossip must not create O(n²) per-tick cost — use sampling/probability
- Trust decay must be slow enough that meaningful relationships persist
- Social network metrics should be computed in collectors.py, not in the engine
- All new parameters must have defaults that match current behavior
- The unified reputation model must be backward-compatible with existing
  engine reads of reputation and trust_of()
