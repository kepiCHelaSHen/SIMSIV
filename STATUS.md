# SIMSIV — Current Status

Phase: C — Extended Deep Dives COMPLETE
Last completed: Medical History Deep Dive (DD17) — heritable conditions, trauma, pathology engine
Current blocker: None
Next step: Phase D or v2 planning

## Key results (Session 009, 200 pop x 50yr)

Post-DD06 household mechanics:
- Childhood deaths: 128 total over 50yr (~2-5/yr at 200 pop)
- Orphans: 12 among 245 children (~5%)
- Avg lifetime births: 3.17, max observed 8 (below cap of 12)
- Maternal health: avg 0.427 (visible cumulative cost of reproduction)
- Birth interval working: 2yr minimum between births
- Maternal age decline: gradual fertility reduction past 30
- Grandparent bonus: reduces infant/childhood mortality when grandparent alive
- Sibling trust: co-living siblings build mutual trust (+0.01/yr)
- Population stable at ~440 (no collapse from added mortality)

## Key results (Session 008, 500 pop x 200yr)

Post-DD05 institutional comparison:
- BASELINE: Pop=609, Gini=0.306, Vio=0.054, Law=0.000 (anarchy), inheritance working (5100 events)
- STRONG_STATE: Pop=1177, Gini=0.250, Vio=0.024 (lowest), Law=0.800, PropRights=0.5
- EMERGENT: Pop=941, Gini=0.268, Vio=0.050, Law grows 0->0.484 organically, 24 emergence events
- ENFORCED_MONOGAMY: Pop=740, Gini=0.317, Vio=0.033, Law=0.700 (static)

Emergent institutions: law_strength self-organizes from 0 to 0.48 over 200yr driven by cooperation
Institutions substitute for traits: STRONG_STATE coop=0.527 (lower than BASELINE 0.564 — less selection pressure)
Inheritance now working by default: 5100 events/200yr (was 0 pre-DD05)

## Previous results (Session 007, 500 pop x 200yr)

Post-DD04 trait evolution by scenario:
- BASELINE: agg -0.036, coop +0.058, intel +0.071, fert +0.014, std~0.09
- STRICT_MONOGAMY: agg -0.053, coop +0.074, intel +0.093 (strongest cooperation+intelligence)
- ELITE_POLYGYNY: agg -0.086, coop +0.029, intel +0.080 (strongest anti-aggression)
- HIGH_VIOLENCE: agg -0.069, coop +0.059, intel +0.014 (stress reduces intel selection)

Trait diversity improved: std ~0.09 (was ~0.07 pre-DD04) due to rare mutations
Correlations decay naturally from init values to near-zero by yr200 (correct behavior)
No sex differences emerging (~12 generations insufficient for dimorphism)

## Previous results (Session 006, 500 pop x 100yr)

Post-DD03 four-scenario comparison:
- BASELINE: Pop=623, Gini=0.345, violence=0.056, v-deaths=159, flees=72, cooldown=4.5%
- STRICT_MONOGAMY: Pop=912, Gini=0.286, violence=0.051, v-deaths=118
- ELITE_POLYGYNY: Pop=1248, Gini=0.327, violence=0.053, v-deaths=144
- HIGH_VIOLENCE: Pop=490, Gini=0.367, violence=0.074, v-deaths=275, aggression=0.434

## Previous results (Session 005, 3 seeds x 200 years x 500 pop)

Post-DD02 four-way comparison:
- FREE_COMPETITION: Gini=0.335, violence=0.057, unmated_m=41%, network=3.4
- ENFORCED_MONOGAMY: Gini=0.328, violence -37%, unmated males -40%
- ELITE_POLYGYNY: Gini=0.468, violence=0.064, unmated_m=43%
- RESOURCE_SCARCITY: Gini=0.283, pop=609 (no longer collapses)

Aggression-pays-cost signal:
- High aggression quartile: 2.8 resources, 0.8 offspring, 28% bonded
- Low aggression quartile: 3.4 resources, 1.0 offspring, 32% bonded
- High cooperation: 3.3 resources, 0.885 status, larger networks

## What was built in DD17
- Pathology engine (NEW): condition activation, remission, trauma tracking, medical history
- 5 heritable condition risks: cardiovascular, mental_illness, autoimmune, metabolic, degenerative
- All condition risks added to HERITABLE_TRAITS (26 total), initial mean 0.2 (low)
- Condition activation: probability-based with trigger multipliers (age, stress, trauma, scarcity)
- Condition remission: annual probability if resources adequate, harder for high-risk agents
- Accumulated trauma: builds from conflict losses, kin deaths, chronic deprivation; slow recovery with kin support
- Condition effects: cardiovascular→health decay, mental_illness→erratic behavior, autoimmune→epidemic vulnerability, metabolic→resource penalty, degenerative→flee threshold
- Mate choice: active conditions reduce attractiveness signal (emotional_intelligence detects)
- Trauma behavioral effects: >0.4 increases mental illness activation, >0.8 behavioral instability
- Medical history: bounded list of events per agent (max 50)
- Tick order: pathology runs at step 6.5 (between mortality and institutions)
- 12 new config params, 7 new metrics

## What was built in DD16
- Genotype/phenotype distinction: genotype stored at birth, breed() reads genotype from parents
- Developmental plasticity: childhood environment modifies trait expression at maturation (age 15)
- Childhood resource quality: tracked as running average of parental resources ages 0-5
- Childhood trauma: flagged when parent dies before agent reaches age 10
- Parental modeling: parents' aggression/cooperation influence child's trait expression
- Orchid/dandelion: mental_health_baseline moderates environmental sensitivity (low = orchid)
- Orphan effect: no living parent at maturation → aggression boost, reputation penalty
- Peer group effects: conformity_bias gates how much peers influence traits (30% of parental)
- Birth order: firstborn +intelligence/impulse_control, later-born +risk/novelty
- All modifications capped at ±0.10 per trait (enough to matter, not override genetics)
- 7 new config params, 3 new metrics (maturation_events, childhood_trauma_rate, avg_childhood_resource_quality)

## What was built in DD15
- Expanded heritable traits from 8 to 21 with per-trait heritability coefficients (h²)
- Heritability model: child_val = h² * parent_midpoint + (1-h²) * pop_mean + mutation
- 21x21 correlation matrix built programmatically (preserves original 8x8 block)
- longevity_genes: shifts death age up to +10yr, reduces health decay 40% after 50
- disease_resistance: reduces epidemic vulnerability up to 50%
- physical_robustness: absorbs combat damage (40% reduction), combat power component
- pain_tolerance: raises effective risk_tolerance for flee check, combat power
- mental_health_baseline: moderates stress→aggression response (50% reduction)
- emotional_intelligence: amplifies trust formation, gossip, mate assessment, bluff detection (30% each)
- impulse_control: gates aggression→conflict translation (60% reduction)
- novelty_seeking: correlated with risk_tolerance, anti-correlated with conformity
- empathy_capacity: extends sharing radius (+15%), reduces conflict initiation (-30%)
- conformity_bias: accelerates institutional adoption (+30%)
- dominance_drive: independent dominance_score contribution (+20% weight)
- maternal_investment: quality-quantity tradeoff (-20% conception, +15% survival)
- sexual_maturation_rate: modifies age_first_reproduction ±3 years
- 1 new config param (heritability_by_trait dict), 13 new metrics

## What was built in DD14
- Faction detection: connected-component analysis on mutual trust graph (every 5yr)
- Faction formation: 45 factions at peak in 500-pop run, consolidating over time
- Leader-based merge: faction leaders with mutual trust > 0.8 trigger faction merger
- Schism: oversized factions (>50) probabilistically split (0.01/yr pressure)
- In-group sharing: lower trust threshold (-0.1) + sharing rate boost (+20%) for faction allies
- Out-group conflict: 1.5x targeting weight for inter-faction conflict
- Endogamy: mild same-faction mate value bonus (+10%)
- Faction effects: avg trust +0.096, cooperation networks +1.5, violence -0.020 vs factions-off
- 11 new config params, 6 new metrics (faction_count, largest_faction_size, faction_size_gini, faction_stability, inter_faction_conflict_rate, factionless_fraction)

## What was built in DD13
- Sex-differential mortality: males 15-40 face 1.8x background mortality rate
- Childbirth mortality: 2% per-birth risk, 3x multiplier for unhealthy mothers (health < 0.4)
- Age-specific fertility curve: adolescent subfertility (60% age 15-19), peak 20-28, decline post-30
- 4 new config params, 4 new metrics (male_deaths, female_deaths, childbirth_deaths, sex_ratio_reproductive)

## What was built in DD12
- Resource display: honest signal costing 5% resources, builds prestige
- Dominance bluffing: low-dominance agents attempt bluffs (5%/yr), intelligence-gated detection
- Detection rate: ~55% (intelligence_proxy * distrust increases detection)
- Caught bluffing: -0.15 reputation, -0.05 prestige (major social cost)
- 6 new config params, 2 new metrics (bluff_attempts, bluff_detections)

## What was built in DD11
- Coalition defense: allies intervene before combat (trust > 0.65, ~2-4/yr)
- Third-party punishment: cooperative agents punish aggressors at personal cost (~2-5/50yr)
- Ostracism: low-reputation agents excluded from cooperation sharing
- Defender gains prestige; aggressor loses dominance on failed attack
- 9 new config params, 3 new metrics (coalition_defenses, third_party_punishments, ostracized_count)

## What was built in DD10
- Seasonal resource cycles: cosine wave modulation of resource multiplier (3-year default)
- Intelligence-mediated storage: smarter agents retain up to 20% more resources year-to-year
- Storage cap: 20.0 max resources per agent (prevents runaway accumulation)
- Birth timing: conception ±20% based on cycle phase (more births in peak years)
- Seasonal conflict: lean-phase conflict probability boosted up to 20%
- 7 new config params, 1 new metric (seasonal_phase)

## What was built in DD09
- Epidemic events: 2%/yr base probability, 2yr duration, 20yr refractory period
- Differential vulnerability: children 3x, elderly 2x, low health 2x, low resources 1.5x
- Overcrowding multiplier: epidemic risk scales above 80% carrying capacity
- Scarcity compounds: 1.5x epidemic risk during active scarcity
- Social consequences: handled by existing orphan (DD06) + inheritance (DD05) systems
- Cross-seed validation: 3/5 seeds get epidemics, pop variance 77-669 (vs pre-DD09 ~similar)
- 8 new config params, 2 new metrics (epidemic_active, epidemic_deaths)

## What was built in DD08
- Prestige/dominance split: current_status → prestige_score + dominance_score (backward-compatible property)
- Prestige: cooperation, intelligence, networks, reputation → 60% of status pool, 1%/yr decay
- Dominance: aggression, status_drive, conflict victories → 40% of status pool, 3%/yr decay
- Combat: dominance weighted 70%, prestige 30%; victories shift dominance
- Mate value: prestige weighted 60%, dominance 40%
- Resource competition: prestige weighted 70%, dominance 30%
- Dominance deterrence: high-dominance agents harder to target in conflict
- Aggressor prestige penalty: violence costs social standing
- 5 new config params, 5 new metrics (avg_prestige, avg_dominance, prestige_gini, dominance_gini, prestige_dominance_corr)

## What was built in DD07
- Reputation engine (NEW): 4-phase engine (trust decay → dead cleanup → gossip → reputation update)
- Gossip: sampling-based trust sharing through allies (10% chance/tick, noise=0.1)
- Trust decay: slow annual drift toward neutral (0.01/yr), extreme values persist longer
- Dead agent cleanup: removes dead agents from ledgers to free slots
- Aggregate reputation: public reputation computed from how others see you (70% aggregate + 30% existing)
- 7 new config params, 5 new metrics (gossip_events, avg_ledger_size, avg_trust, distrust_fraction, avg_reputation)

## What was built in DD06
- Birth interval: 2yr minimum between births (lactational amenorrhea analog)
- Maternal age fertility decline: 3% per year past 30 (gradual, not binary)
- Lifetime birth cap: max 12 per female (configurable)
- Maternal health cost: 0.03 per birth (cumulative)
- Annual childhood mortality: 0.02 base rate, resource-dependent, scarcity-amplified
- Orphan mortality multiplier: 2x base rate for parentless children
- Grandparent survival bonus: 0.05 reduction in infant/childhood mortality
- Sibling trust growth: co-living siblings build trust +0.01/yr
- 8 new config params, 6 new metrics (childhood_deaths, orphan_deaths, children_count, orphan_count, avg_lifetime_births, avg_maternal_health)

## Known minor issues
- One-tick mourning delay: partners of agents dying in mortality engine don't get mourning state until next tick's _clean_stale_bonds. Functionally harmless.

## What was built in DD05
- Institutional drift: law_strength evolves from cooperation/violence balance (drift_rate * net_pressure * inertia_resistance)
- Norm enforcement: active polygyny detection with reputation + resource penalties scaled by law_strength
- Emergent institution formation: violence punishment after 5yr high-violence streak, mate limit reduction after 8yr inequality streak
- Property rights: modulates conflict resource looting (loot_fraction = 0.5 * (1 - property_rights))
- Enhanced inheritance: default ON (was OFF), trust-weighted model option, prestige inheritance (status to heirs)
- STRONG_STATE scenario: law=0.8, vps=0.7, property_rights=0.5, tax=0.15, monogamy
- EMERGENT_INSTITUTIONS scenario: all start at 0, drift_rate=0.02, inertia=0.7, emergence enabled
- 7 new config params (+ changed inheritance_law_enabled default True), 6 new metrics

## What was built in DD04
- Parent weight variance: random blend (N(0.5, 0.1)) instead of exact 50/50 inheritance
- Rare large mutations: 5% chance per trait of 3x sigma jump (maintains diversity)
- Stress-induced mutation: scarcity amplifies sigma by up to 1.5x (faster adaptation under pressure)
- Population-derived migrant traits: rescue migrants match evolved trait distribution
- Per-trait evolution tracking: all 8 traits tracked in metrics (was only aggression+cooperation)
- Trait diversity metrics: std of aggression and cooperation tracked per tick
- Max generation tracking: generational depth in metrics
- 5 new config params, 9 new metrics

## What was built in DD03
- Network deterrence: agents with allies are less likely to initiate AND harder to target
- Flee response: low risk_tolerance agents can avoid combat (flee_threshold=0.3)
- Scaled consequences: power differential affects cost magnitude (0.7x close fights, 1.5x stomps)
- Subordination: losers enter cooldown (2yr default), reducing future aggression by 50%
- Bystander trust: witnesses distrust the aggressor (-0.08, allied witnesses -0.1 extra)
- Resource advantage in combat (combat_resource_factor=0.1)
- Violence death logging fix: proper "death" type events now emitted
- Strength assessment: cowardly aggressors avoid healthier targets
- Resource envy: richer targets are more tempting to pick
- 9 new config params, 4 new metrics (flee_events, violence_deaths, punishment_events, agents_in_cooldown)

## What was built in DD02
- 8-phase resource engine: decay → distribute → child investment → cooperation sharing → status → elite privilege → taxation → subsistence floor
- Kin trust maintenance: parents + dependent children build mutual trust (+0.02/yr), bootstraps cooperation networks from 0.5 → 3.3 allies
- Aggression production penalty (0.3): fighters get 18% fewer resources
- Cooperation network competitive bonus (0.05/ally, max 5): cooperative clusters dominate
- Cubed competitive weights (was squared): pushes Gini from 0.24 → 0.33
- Equal floor reduced 40% → 25%: more competition, more spread
- Child investment costs (0.5/child/yr): links mating structure to resource inequality
- Configurable taxation/redistribution: gated by law_strength
- Subsistence floor (1.0): prevents death spirals
- Wealth diminishing returns (power 0.7): soft ceiling on accumulation
- Configurable scarcity severity (0.6): softer than v1's hardcoded 0.4
- 12 new config params, 3 new metrics (resource_top10_share, cooperation_network_size, resource_transfers)

## What was built in DD01
- partner_ids list + pair_bond_strengths dict (replaces single pair_bond_id)
- Bond helpers: is_bonded, add_bond, remove_bond, bond_count, primary_partner_id, etc.
- Extra-pair copulation (EPC) with mate-value-weighted male selection
- Paternity uncertainty + reduced male investment when suspicious
- Male mating contests with injury risk
- Widowhood mourning period
- Age-dependent female choosiness
- Stronger aggression penalty (0.5) and cooperation bonus (0.4) in mate choice
- Centralized bond cleanup in mating engine (_clean_stale_bonds)
- 6 new metrics: infidelity_rate, epc_detected, paternity_uncertainty, avg_bond_strength, mating_contests
- 9 new config params

Updated: 2026-03-14
