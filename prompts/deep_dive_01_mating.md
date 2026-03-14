# SIMSIV — PROMPT: DEEP DIVE 01 — MATING SYSTEM
# File: D:\EXPERIMENTS\SIM\prompts\deep_dive_01_mating.md
# Use: Send to Claude after skeleton is working and verified
# Priority: PHASE B, Sprint 1

================================================================================
CONTEXT INJECTION — READ FIRST
================================================================================

You are doing Deep Dive 01 on the SIMSIV mating system engine.

Before doing ANYTHING, read:
  1. D:\EXPERIMENTS\SIM\CHAIN_PROMPT.md
  2. D:\EXPERIMENTS\SIM\devlog\DEV_LOG.md
  3. D:\EXPERIMENTS\SIM\engines\mating.py (current implementation)
  4. D:\EXPERIMENTS\SIM\models\agent.py
  5. D:\EXPERIMENTS\SIM\docs\rules_spec.md sections on mating

The skeleton mating engine is functional. This deep dive replaces it with a
richer, more realistic model without breaking anything else.

================================================================================
DEEP DIVE 01: MATING SYSTEM
================================================================================

This is the single most impactful subsystem for divergent outcomes.
Take the time to get it right.

QUESTIONS TO RESOLVE AND IMPLEMENT:

A. FEMALE MATE CHOICE MODEL
   - Design the precise mate_value scoring function for female choice
   - How are multiple candidate males evaluated? Tournament vs full comparison?
   - What role does pair bond history play in re-pairing decisions?
   - Should there be a "compatibility" dimension beyond raw mate value?
   - How does female_choice_strength slider modulate the function?
     (0.0 = random pairing, 1.0 = pure best-available)
   - Age effects: should older females have lower choosiness? Or the reverse?
   - Should resource-poor females accept lower-quality mates?

B. MALE COMPETITION MODEL
   - How do males compete when multiple target the same female?
   - Contest resolution: pure status, status + aggression, coalitions?
   - Should there be physical contest risk (injury/death) in competition?
   - Should male competition be direct (fight) or indirect (display)?
   - How does male_competition_intensity modulate the function?
   - Should subordinate males accept worse outcomes or fight to the death?

C. PAIR BOND DYNAMICS
   - Dissolution probability formula: what drives dissolution?
     (low resources, health decline, better alternative detected, jealousy)
   - Should pair bond strength GROW over time (investment sunk cost)?
   - How should pair bond quality affect offspring outcomes?
   - Should agents have a memory of past bonds that affects new ones?

D. INFIDELITY AND PATERNITY
   - Should extra-pair copulation (EPC) be modeled?
   - If yes: probability as function of female mate value gap
     (female paired below her potential seeks better genes?)
   - If hidden: how does suspected vs confirmed infidelity differ in effect?
   - Paternity uncertainty: should males' investment drop when uncertain?
   - Should jealousy detection trigger conflict here specifically?

E. MATING SYSTEM VARIANTS AS TOGGLEABLE OVERLAYS
   - Enforced monogamy: add norm violation cost + detection probability
   - Elite polygyny: top N% of status males exempt from max_mates limit
   - Egalitarian: reduce variance in male competitive success
   - How do these overlays interact with institutional strength parameter?

F. WIDOWHOOD AND RE-PAIRING
   - After partner death: mourning period (configurable) before re-entry
   - Re-pairing probability: function of age, resources, mate value
   - Should re-pairing be harder for older agents?

G. HOMOSEXUAL PAIR BONDING (OPTIONAL TOGGLE)
   - If enabled: proportion of agents (configurable, default ~5%)
   - Pair bonding works identically, no reproduction unless adoption modeled
   - Adoption: configurable — homosexual pairs can adopt orphaned offspring
   - Default: disabled (simplification, not value statement)

================================================================================
DELIVERABLES
================================================================================

1. docs/deep_dive_01_mating.md — full design decisions and math
2. engines/mating.py — full replacement implementation
3. config.py additions — all new mating parameters with defaults
4. metrics/collectors.py additions — new mating-relevant metrics
5. DEV_LOG.md entry
6. CHAIN_PROMPT.md update

================================================================================
NEW PARAMETERS TO ADD TO CONFIG
================================================================================

female_choosiness_age_effect: float = -0.01  (choosiness drops per year over 30)
male_contest_injury_risk: float = 0.05
male_competition_mode: str = "probabilistic"  # or "tournament" or "display"
pair_bond_growth_rate: float = 0.02  (strength grows per year together)
infidelity_enabled: bool = True
infidelity_base_rate: float = 0.05
paternity_certainty_threshold: float = 0.7  (below = uncertain = less invest.)
jealousy_detection_rate: float = 0.4
widowhood_mourning_years: int = 1
homosexual_pairing_enabled: bool = False
homosexual_proportion: float = 0.05
adoption_enabled: bool = False
