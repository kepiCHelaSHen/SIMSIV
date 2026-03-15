# SIMSIV — PROMPT: DEEP DIVE 12 — STATUS SIGNALING
# File: D:\EXPERIMENTS\SIM\prompts\deep_dive_12_signaling.md
# Use: Send to Claude after DD11 is complete
# Priority: PHASE C, Sprint 5

================================================================================
CONTEXT INJECTION — READ FIRST
================================================================================

You are doing Deep Dive 12 on the SIMSIV status signaling model.

Before doing ANYTHING, read:
  1. D:\EXPERIMENTS\SIM\CHAIN_PROMPT.md
  2. D:\EXPERIMENTS\SIM\devlog\DEV_LOG.md
  3. D:\EXPERIMENTS\SIM\models\agent.py (mate_value, prestige_score, dominance_score)
  4. D:\EXPERIMENTS\SIM\engines\mating.py (female choice model)
  5. D:\EXPERIMENTS\SIM\engines\conflict.py (dominance display)
  6. D:\EXPERIMENTS\SIM\STATUS.md (latest results)

Currently agents compete for status based on actual trait values and earned
scores. But real social competition involves SIGNALS — behaviors that
communicate underlying quality, some honest (resource display, skill
demonstration) and some dishonest (bluffing quality you don't have).
An arms race between signalers and detectors produces social dynamics
— deception, reputation inflation, costly honest signals — that are
missing from the current model. This deep dive adds a signaling layer.

================================================================================
DEEP DIVE 12: STATUS SIGNALING
================================================================================

CURRENT STATE:
  - mate_value: computed directly from actual health, status, resources,
    attractiveness, reputation — no signaling layer
  - Female choice: reads mate_value directly — no deception possible
  - Status competition: actual scores determine outcomes — no bluffing
  - No concept of signal reliability or signal cost
  - Agents have perfect information about observable traits

CORE CONCEPTS:
  Honest signals: costly to fake — resource display, offspring count,
  scar patterns (conflict history), long-term pair bond stability.
  Quality is real; signal is verifiable.

  Dishonest signals: cheap to produce — aggression display without real
  fighting, exaggerated resource holding behavior, reputation manipulation.
  Quality may not match signal.

  Arms race: as dishonest signaling spreads, detection ability evolves.
  As detection improves, honest signaling becomes more valuable.
  This produces cyclical dynamics and trait evolution pressure.

QUESTIONS TO RESOLVE AND IMPLEMENT:

A. SIGNAL TYPES TO MODEL
   Keep it tractable — implement 2-3 distinct signal types:

   Resource display (honest):
   - Agent "displays" a fraction of resources as a signal
   - Costs: resources spent on display are unavailable for other uses
   - Effect: boosts perceived mate value and prestige beyond actual values
   - Detectable: females can verify resource level (honest signal)

   Dominance display (partially dishonest):
   - Agent signals fighting ability without actual fighting
   - Cost: time and energy (minor health cost)
   - Effect: may deter conflict attempts (targets think twice)
   - Deceptive: actual fighting ability may not match display
   - Detection: counter-signals, challenges, actual fights reveal truth

   Generosity display (honest):
   - Agent makes public resource transfers (visible to bystanders)
   - Cost: real resources transferred
   - Effect: prestige gain beyond private sharing
   - Honest by definition: costs are real

B. SIGNAL DETECTION AND VERIFICATION
   - How do agents assess signal reliability?
   - Should intelligence_proxy gate detection ability?
     (smarter agents see through bluffs more often)
   - Should past interaction history improve detection?
     (if you've fought X before and he lost, his dominance display means less)
   - Should gossip (DD07) transmit signal reliability information?
     ("don't be fooled by agent 47 — I've seen him flee from weak opponents")

C. DECEPTION MECHANICS
   - Should there be a "bluff" action available to low-quality agents?
   - Bluff probability: function of risk_tolerance
   - Bluff detection probability: function of target's intelligence_proxy
     and existing trust/reputation data
   - Caught bluffing: major reputation loss, reduced mate value for several years
   - Successful bluff: temporary mate value / status boost
   - This creates selection pressure: risk-tolerant low-quality agents bluff;
     intelligent females detect bluffs; honest signalers gain reliability premium

D. COSTLY HONEST SIGNAL — THE HANDICAP PRINCIPLE
   - Should some signals be so costly that only high-quality agents can afford them?
   - Example: prolonged resource display reduces agent's competitive ability
     for that year — only agents with surplus can maintain it
   - Example: fighting multiple consecutive conflicts without fleeing
     signals real dominance — but kills low-quality agents who try
   - This produces reliable honest signaling WITHOUT verification

E. MATE VALUE REVISION
   - Currently mate_value is computed from actual values
   - After this deep dive, mate_value should include a signaling component:
     perceived_mate_value = actual_mate_value + signal_bonus - deception_penalty
   - Female choice reads perceived_mate_value, not actual
   - Over time, deceptive signals that are detected create reputation penalty
     that reduces perceived beyond actual

F. SIGNALING AND INSTITUTIONAL CONTEXT
   - Should strong institutions suppress dishonest signaling?
     (reputation verification systems, property rights reduce resource bluffing)
   - Should high-cooperation societies value honest signals more?
     (gossip networks spread signal reliability information)

================================================================================
DELIVERABLES
================================================================================

1. docs/deep_dive_12_signaling.md — design decisions and signal economics
2. models/agent.py — signal state fields (current_signal_investment,
   bluff_active, signal_reputation_bonus)
3. engines/resources.py — display costs and prestige gains
4. engines/mating.py — perceived_mate_value incorporating signals
5. engines/conflict.py — dominance display as deterrent
6. config.py additions — signaling parameters
7. metrics/collectors.py — signaling metrics (bluff_attempts, bluff_detections,
   avg_signal_investment, honest_signal_premium)
8. DEV_LOG.md entry
9. CHAIN_PROMPT.md update

================================================================================
NEW PARAMETERS TO ADD TO CONFIG
================================================================================

signaling_enabled: bool = True
resource_display_fraction: float = 0.05      # fraction of resources spent on display
resource_display_mate_value_boost: float = 0.1  # perceived MV boost per display unit
dominance_display_health_cost: float = 0.01  # health cost of display per year
dominance_display_deterrence: float = 0.2    # reduction in being targeted
bluffing_enabled: bool = True
bluff_base_probability: float = 0.05         # base annual bluff attempt rate
bluff_detection_base: float = 0.3            # base detection probability
bluff_caught_reputation_loss: float = 0.3   # major reputation hit if caught
bluff_success_mv_boost: float = 0.15         # temporary MV boost from successful bluff
generosity_display_prestige_multiplier: float = 1.5  # public vs private sharing

================================================================================
CONSTRAINTS
================================================================================

- Signaling must be COSTLY — free signals produce no interesting dynamics
- Bluffing must be DETECTABLE — otherwise all agents bluff and signals lose meaning
- Do not create perfect information — some deception should always be possible
- Signal effects must be TEMPORARY — reputation recovers, bluff effects fade
- Backward compatibility: signaling_enabled=False reproduces current behavior
