# SIMSIV — PROMPT: DEEP DIVE 21 — RESOURCE TYPE DIFFERENTIATION
# File: D:\EXPERIMENTS\SIM\prompts\deep_dive_21_resource_types.md
# Use: Send to Claude after DD20 is complete
# Priority: PHASE C, Sprint 14

================================================================================
CONTEXT INJECTION — READ FIRST
================================================================================

You are doing Deep Dive 21 on the SIMSIV resource type model.

Before doing ANYTHING, read:
  1. D:\EXPERIMENTS\SIM\CHAIN_PROMPT.md
  2. D:\EXPERIMENTS\SIM\devlog\DEV_LOG.md
  3. D:\EXPERIMENTS\SIM\engines\resources.py (current 8-phase engine)
  4. D:\EXPERIMENTS\SIM\models\agent.py (current_resources field)
  5. D:\EXPERIMENTS\SIM\config.py
  6. D:\EXPERIMENTS\SIM\STATUS.md

Resources are currently generic — one float representing all wealth. In reality,
different resource types produce fundamentally different social dynamics:
food produces dependency and sharing obligations; tools produce efficiency
multipliers; prestige goods produce status signaling and trade relationships.
This differentiation is what creates specialization, trade networks, and
ultimately the economic foundation of more complex societies. This deep dive
splits the generic resource into three typed pools with distinct mechanics.

================================================================================
DEEP DIVE 21: RESOURCE TYPE DIFFERENTIATION
================================================================================

THREE RESOURCE TYPES:

  SUBSISTENCE (food, water, shelter material):
    Current analog: current_resources (mostly)
    Key property: perishable — high decay rate (0.4 per year vs 0.5 overall)
    Sharing: highest sharing obligation (you share food with kin regardless)
    Conflict trigger: starvation triggers immediate aggression
    Survival: directly maps to health (starvation = health damage)
    Production: intelligence + cooperation + seasonal cycle
    Storage: limited — cannot hoard indefinitely

  TOOLS (weapons, implements, infrastructure):
    New resource type: current_tools
    Key property: durable — low decay rate (0.1 per year)
    Sharing: lower obligation — tools are personal property
    Effect: multiplies subsistence production efficiency (tools → more food)
    Conflict: tool possession affects combat power (armed vs unarmed)
    Production: intelligence + status_drive (ambition drives tool accumulation)
    Trade: primary trade good between agents and eventually between bands
    Inheritance: tools are the most inheritable resource type (durable, valuable)

  PRESTIGE GOODS (ornaments, rare materials, ritual objects):
    New resource type: current_prestige_goods
    Key property: non-perishable but non-productive — purely social value
    Effect: directly boosts prestige_score (social signaling)
    Sharing: given as gifts — generosity display, not obligation
    Conflict: not worth fighting over directly (too abstract)
    Production: trade + ritual + gifting (not extractive labor)
    Mate value: prestige goods boost attractiveness signal beyond raw mate_value
    Inter-band: primary medium of inter-band alliance and trade (v2 prep)

QUESTIONS TO RESOLVE AND IMPLEMENT:

A. SPLITTING CURRENT_RESOURCES
   The cleanest approach: current_resources becomes subsistence_resources.
   Add: current_tools and current_prestige_goods as new float fields on Agent.
   All existing code that references current_resources continues to work
   (it now specifically means subsistence).

   Initial allocation: at population creation, split current endowment:
   - subsistence_resources: 60% of original current_resources
   - current_tools: 30% (weapon/tool equivalent)
   - current_prestige_goods: 10% (rare goods)

B. PRODUCTION MECHANICS
   Each resource type has its own production function in the resource engine:

   Subsistence production:
   - Current Phase 2 logic — intelligence + status + cooperation competitive weights
   - Seasonal cycle affects primarily subsistence (food is most seasonal)
   - Tools multiply subsistence production: subsistence_gain *= (1 + tools * tool_production_multiplier)

   Tool production:
   - Slower than subsistence — tools take time to make
   - Production weight: intelligence * 0.5 + status_drive * 0.3 + age_experience * 0.2
   - Can be traded: high-tool agents can exchange tools for subsistence
   - Upper bound: cap on tools per agent (you can only use so many tools)

   Prestige goods production:
   - Generated through: gifting ceremonies (cooperation events), trade, ritual
   - Not produced directly from labor — they come from social transactions
   - Agent gains prestige goods by giving away subsistence or tools
     (the act of generous giving generates prestige goods as byproduct)
   - This creates the prestige economy: you get social goods by giving material goods

C. TRADE MECHANICS (WITHIN BAND)
   First intra-band trade system:
   - Agents with surplus tools can trade with agents who have surplus subsistence
   - Trade probability: f(tool_surplus, subsistence_deficit, bilateral trust)
   - Trade price: 1 tool ≈ N subsistence (configurable exchange rate)
   - Trade generates trust between parties (like cooperation sharing)
   - High intelligence agents get better trade terms
   - This is the precursor to inter-band trade in v2

D. INHERITANCE BY TYPE
   Each resource type inherits differently:
   - Subsistence: largely consumed before death — little inherited
   - Tools: primary inheritance good — durable, valuable, splits per equal_split model
   - Prestige goods: inherited as status symbols — heirs gain prestige_score boost
     (the prestige_goods inheritance is the prestige inheritance from DD05)

E. CONFLICT TARGETING BY RESOURCE
   Conflict target selection now weights by resource type:
   - Subsistence envy: target has excess subsistence → 1.3x targeting
   - Tool envy: target has superior tools → 1.4x targeting (arms race)
   - Prestige goods: NOT a direct conflict trigger (too abstract)
   - Winners loot subsistence primarily (food is most immediately useful)
   - Tool looting: 20% chance winner takes one tool from loser

F. MATE VALUE AND PRESTIGE GOODS
   Female mate choice already weights prestige_score.
   After DD21: prestige_goods also directly contribute to attractiveness signal:
   perceived_attractiveness = attractiveness_base + prestige_goods * prestige_goods_mate_signal
   High prestige goods → visible high mate value → female choice boost
   This is the economic dimension of mate value — wealthy men are more attractive

G. SPECIALIZATION EMERGENCE
   Over time, agents should specialize in what they're good at producing:
   - High intelligence + low aggression → tool specialists
   - High aggression + high risk_tolerance → conflict specialists (raiders)
   - High cooperation + high empathy → prestige goods specialists (traders/priests)
   This specialization is the seed of division of labor at higher levels.

================================================================================
DELIVERABLES
================================================================================

1. docs/deep_dive_21_resource_types.md — design decisions and production formulas
2. models/agent.py — current_tools, current_prestige_goods fields
3. engines/resources.py — three-type production, trade mechanics, seasonal effects
4. engines/conflict.py — resource-type-specific targeting and looting
5. engines/mating.py — prestige goods in mate value signal
6. engines/institutions.py — tool inheritance priority
7. config.py additions — resource type parameters
8. metrics/collectors.py — per-type resource metrics (avg_tools, avg_prestige_goods,
   trade_events, tool_gini, subsistence_gini, prestige_gini_separate)
9. DEV_LOG.md entry
10. CHAIN_PROMPT.md + STATUS.md update

================================================================================
NEW CONFIG PARAMETERS
================================================================================

resource_types_enabled: bool = True
subsistence_decay_rate: float = 0.4          # higher decay than current 0.5
tools_decay_rate: float = 0.1                # very durable
prestige_goods_decay_rate: float = 0.05      # nearly permanent
tool_production_multiplier: float = 0.3      # tools boost subsistence production
tools_per_agent_cap: float = 10.0            # max tools any agent can hold
prestige_goods_per_agent_cap: float = 5.0    # max prestige goods
intraband_trade_probability: float = 0.1     # annual trade attempt probability
tool_subsistence_exchange_rate: float = 3.0  # 1 tool = 3 subsistence
prestige_goods_mate_signal: float = 0.05     # prestige goods → attractiveness boost
tool_conflict_loot_chance: float = 0.2       # chance winner takes a tool

================================================================================
CONSTRAINTS
================================================================================

- current_resources MUST remain functional — it becomes subsistence_resources
  alias for backward compatibility
- Existing code that reads current_resources continues to work unchanged
- Resource splitting must not collapse population dynamics — validate carefully
- Trade must be RARE in early runs — it should emerge as trust networks form
- Backward compatibility: resource_types_enabled=False = current behavior
- Run validation post-implementation: total wealth (all three types) should
  be similar to pre-DD21, just redistributed across types
