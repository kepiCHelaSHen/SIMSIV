# SIMSIV — PROMPT: DEEP DIVE 05 — INSTITUTIONS
# File: D:\EXPERIMENTS\SIM\prompts\deep_dive_05_institutions.md
# Use: Send to Claude after DD01-DD04 are complete
# Priority: PHASE B, Sprint 5

================================================================================
CONTEXT INJECTION — READ FIRST
================================================================================

You are doing Deep Dive 05 on the SIMSIV institution engine.

Before doing ANYTHING, read:
  1. D:\EXPERIMENTS\SIM\CHAIN_PROMPT.md
  2. D:\EXPERIMENTS\SIM\devlog\DEV_LOG.md
  3. D:\EXPERIMENTS\SIM\engines\institutions.py (current implementation)
  4. D:\EXPERIMENTS\SIM\models\agent.py
  5. D:\EXPERIMENTS\SIM\config.py (all institution-related params)
  6. D:\EXPERIMENTS\SIM\STATUS.md (latest results)

The v1 institution engine is barely functional — it only handles inheritance
distribution and has placeholder stubs for monogamy enforcement and violence
punishment. The real enforcement logic lives scattered across other engines
(mating checks monogamy_enforced, conflict reads violence_punishment_strength).
This deep dive creates a proper institutional layer with emergent institution
formation, strength drift, and cross-engine modulation.

================================================================================
DEEP DIVE 05: INSTITUTIONS
================================================================================

CURRENT STATE:
  - institutions.py is 88 lines, mostly inheritance distribution
  - monogamy_enforced: bool toggle, checked in mating engine
  - law_strength: float 0-1, read by conflict engine for suppression
  - violence_punishment_strength: float 0-1, read by conflict engine
  - inheritance_law_enabled: bool, gates inheritance in institutions engine
  - elite_privilege_multiplier: float, read by resource engine
  - NO institutional drift — strengths are static for entire simulation
  - NO norm enforcement feedback — violations don't weaken institutions
  - NO emergent institution formation — all institutions are config-set

POST-DD02 DATA POINTS:
  - ENFORCED_MONOGAMY (law_strength=0.7, vps=0.5): violence -37%, unmated_m -40%
  - Taxation system (DD02) gated by law_strength — but law_strength doesn't change
  - Status compounding exists but isn't modulated by institutional context

QUESTIONS TO RESOLVE AND IMPLEMENT:

A. INSTITUTIONAL DRIFT MODEL
   The most important missing feature. Institutions should strengthen or erode:
   - How should law_strength drift? What drives it up vs down?
     (high cooperation → stronger institutions? violence → weakens them?)
   - Should institutional strength be derived from agent behavior aggregates?
     (if >60% of agents are cooperative, institutions gain strength)
   - Or should institutions have their own inertia? (harder to change once
     established — path dependency)
   - What is the drift rate? (fast enough to see in 200 years, slow enough
     to feel institutional)

B. NORM ENFORCEMENT
   Currently all enforcement is binary checks in other engines.
   - Should the institution engine actively detect and punish norm violations?
   - Monogamy: detect polygynous bonds, apply reputation/resource penalties
   - Violence: detect conflicts, apply post-hoc punishment (fines, ostracism)
   - Should punishment severity scale with law_strength?
   - Should enforcers be specific agents (chiefs, elders) or abstract?

C. EMERGENT INSTITUTION FORMATION
   Currently institutions are toggle-on at simulation start.
   - Should institutions be able to EMERGE from agent behavior?
   - Example: if violence rate exceeds threshold for N years,
     violence_punishment_strength could spontaneously increase
   - Example: if mating inequality exceeds threshold, monogamy norms could emerge
   - This would make institutions endogenous rather than exogenous
   - What are the thresholds and formation rates?

D. INSTITUTIONAL TYPES EXPANSION
   Current: monogamy, violence punishment, inheritance, elite privilege.
   Consider adding:
   - Property rights: strength of resource theft protection (modulates conflict
     resource transfer — high property rights = less loot in conflict)
   - Kinship norms: strength of kin obligation (modulates cooperation sharing
     radius and parental investment)
   - Bride price / dowry: resource transfer at pair bond formation
     (creates economic incentive for pair bonding)
   - Age hierarchy: elder status bonus (modulates status distribution)
   - Religious/ritual norms: cooperation bonus for in-group, penalty for out-group
     (lays groundwork for v2 multi-tribe dynamics)

E. INHERITANCE SYSTEM EXPANSION
   Current: equal_split or primogeniture, executed on death.
   - Should inheritance be proportional to relationship quality?
     (favored child gets more — driven by parent's trust ledger)
   - Should there be inter-vivos transfers? (gifts while alive — already
     partially covered by DD02 child investment)
   - Should inheritance create status boost for heirs? (prestige inheritance)
   - Should inheritance_law_enabled be default True? (currently False —
     resources just vanish on death when disabled)

F. CROSS-ENGINE MODULATION INTERFACE
   Institutions should modulate behavior across all engines via a clean interface:
   - Resource engine: tax_rate, elite_privilege, property_rights
   - Conflict engine: suppression, punishment, deterrence
   - Mating engine: monogamy, bride price, mate choice norms
   - Reproduction engine: child investment norms, kin support obligations
   - Should the institution engine set "effective config" values each tick
     that other engines read? (clean separation vs current scattered checks)

G. SCENARIO DESIGN
   New institutional scenarios to add:
   - STRONG_STATE: high law, high tax, high punishment
   - WEAK_STATE: low law, no tax, no punishment
   - EMERGENT_INSTITUTIONS: all start at 0, allowed to self-organize
   - THEOCRATIC: high cooperation norm, strong pair bonding, high punishment

================================================================================
DELIVERABLES
================================================================================

1. docs/deep_dive_05_institutions.md — design decisions and drift formulas
2. engines/institutions.py — full replacement implementation
3. config.py additions — all new institutional parameters
4. experiments/scenarios.py — new institutional scenarios
5. metrics/collectors.py additions — institutional metrics
6. DEV_LOG.md entry
7. CHAIN_PROMPT.md update

================================================================================
NEW PARAMETERS TO CONSIDER FOR CONFIG
================================================================================

institutional_drift_rate: float = 0.01        # max change in law_strength per year
institutional_inertia: float = 0.8            # resistance to change (0=fluid, 1=rigid)
norm_violation_decay: float = 0.1             # how much violations weaken institutions
cooperation_institution_boost: float = 0.01   # avg cooperation drives institutional growth
violence_institution_decay: float = 0.02      # violence rate erodes institutions
emergent_institutions_enabled: bool = False    # allow spontaneous institution formation
property_rights_strength: float = 0.0         # modulates conflict resource transfer
bride_price: float = 0.0                      # resource transfer at bond formation
kinship_obligation_strength: float = 0.0      # modulates cooperation sharing
inheritance_law_enabled: bool = True           # change default from False to True
inheritance_prestige_fraction: float = 0.0     # status inherited alongside resources

================================================================================
CONSTRAINTS
================================================================================

- Do not break any other engine
- Institutional changes must be GRADUAL and EMERGENT when drift is enabled
- All new parameters must have defaults that match current behavior (backward compat)
- Institutional drift must be slow enough to be realistic but fast enough to
  observe in 200-year runs
- The cross-engine modulation interface must be clean — avoid spaghetti dependencies
