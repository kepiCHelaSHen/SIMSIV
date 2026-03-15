# SIMSIV — PROMPT: DEEP DIVE 27 — TRAIT COMPLETION (9 NEW HERITABLE TRAITS)
# File: D:\EXPERIMENTS\SIM\prompts\deep_dive_27_trait_completion.md
# Use: Send to Claude after autosim v1.0 is tagged and best_config applied
# Priority: PHASE D, Sprint 1
# Result: 26 → 35 heritable traits (scientific completion of the trait model)

================================================================================
CONTEXT INJECTION — READ FIRST
================================================================================

You are doing Deep Dive 27 on the SIMSIV trait model — adding 9 new heritable
traits that complete the scientific coverage of human individual differences.

Before doing ANYTHING, read:
  1. D:\EXPERIMENTS\SIM\CHAIN_PROMPT.md
  2. D:\EXPERIMENTS\SIM\devlog\DEV_LOG.md
  3. D:\EXPERIMENTS\SIM\models\agent.py (ALL of it — full trait list, HERITABLE_TRAITS,
     TRAIT_HERITABILITY, _build_correlation_matrix, breed(), Agent dataclass)
  4. D:\EXPERIMENTS\SIM\engines\conflict.py
  5. D:\EXPERIMENTS\SIM\engines\resources.py
  6. D:\EXPERIMENTS\SIM\engines\mating.py
  7. D:\EXPERIMENTS\SIM\engines\reproduction.py
  8. D:\EXPERIMENTS\SIM\engines\reputation.py
  9. D:\EXPERIMENTS\SIM\config.py
  10. D:\EXPERIMENTS\SIM\STATUS.md

Current state: 26 heritable traits across 6 domains. This deep dive adds 9 more
to reach 35 total — the scientifically complete ceiling for this model. Every
new trait has a distinct behavioral effect not covered by existing traits, a
documented heritability coefficient from behavioral genetics literature, and
wiring into at least one existing engine.

CRITICAL RULES:
  - Do NOT duplicate existing trait effects. Each new trait must have a
    behavioral effect that cannot be achieved by any combination of existing traits.
  - All new traits default to 0.5 for backward compatibility.
  - All effects must be SMALL MULTIPLIERS on existing behavior — not new systems.
  - Run validation after each group of 3 traits to catch crashes early.
  - NEVER modify the 5 condition risks (traits 21-25) — those are DD17 medical.

================================================================================
DEEP DIVE 27: 9 NEW HERITABLE TRAITS
================================================================================

CURRENT TRAIT COUNT: 26 (indices 0-25)
NEW TRAIT COUNT: 35 (indices 26-34)
TARGET: Scientific completeness — no major heritable human behavioral trait missing

================================================================================
GROUP 1: PHYSICAL PERFORMANCE (traits 26-27)
================================================================================

ADD AFTER sexual_maturation_rate (index 20), BEFORE condition risks (index 21):
Wait — add at end of list after index 25, before any future additions.
Actually add in logical grouping at end: indices 26-34.

TRAIT 26: physical_strength
  Default: 0.5
  Heritability: h² = 0.60 (one of highest heritable physical traits)
  Science: Physical strength is ~60% heritable based on twin studies of grip
           strength, muscle mass, and anaerobic capacity. Distinct from
           physical_robustness (damage absorption) — this is force output.
  Sex differential: males express physical_strength effect at 1.4x females
                    (testosterone-mediated expression difference, not different
                    genetic values — both sexes inherit equally)

  Behavioral effects (wire into existing engines):
    engines/conflict.py — combat power:
      agg_power += agent.physical_strength * config.physical_strength_combat_weight
      (default weight: 0.12 — additive to existing power formula)
      Male sex multiplier: if agent.sex == Sex.MALE: strength_contribution *= 1.4

    engines/resources.py — Phase 2 competitive weight:
      Add physical_strength * 0.08 to competitive weight
      (manual labor productivity — strong agents gather more)
      Inverse sex effect: females get 0.6x physical_strength benefit in
      foraging (endurance-based tasks favor different physiology)

    engines/mating.py — male mate value:
      male mate_value gets +0.05 * physical_strength boost
      (females prefer physically strong mates — well documented)

  Correlation additions to _build_correlation_matrix():
    physical_strength ↔ physical_robustness: +0.45 (muscle/frame correlation)
    physical_strength ↔ pain_tolerance: +0.25 (athletic tolerance)
    physical_strength ↔ endurance: +0.40 (DD27 trait — set below)
    physical_strength ↔ aggression_propensity: +0.15 (slight)
    physical_strength ↔ longevity_genes: -0.10 (slight trade-off)

---

TRAIT 27: endurance
  Default: 0.5
  Heritability: h² = 0.50
  Science: Aerobic capacity, VO2 max, muscular endurance are ~50% heritable.
           Distinct from physical_strength (force) — this is sustained capacity.
           Distinct from physical_robustness (resisting damage) — this is
           sustained output over time.

  Behavioral effects:
    engines/resources.py — Phase 2 foraging bonus:
      competitive_weight += agent.endurance * config.endurance_foraging_bonus
      (default: 0.06 — sustained foragers gather more over full season)
      Female endurance bonus matches male: no sex differential in endurance
      (supported by physiology — females often outperform on long endurance)

    engines/mortality.py — childbirth survival:
      Current: childbirth_mortality_rate * (3.0 if health < 0.4 else 1.0)
      Add: childbirth_multiplier *= max(0.5, 1.0 - agent.endurance * 0.4)
      (high endurance women survive childbirth better — well documented)

    engines/mortality.py — health damage recovery:
      agents with high endurance lose health slightly slower:
      health_decay *= max(0.7, 1.0 - agent.endurance * 0.15)

  Correlation additions:
    endurance ↔ physical_strength: +0.40 (already set above)
    endurance ↔ physical_robustness: +0.30
    endurance ↔ longevity_genes: +0.25 (aerobic fitness → longevity)
    endurance ↔ disease_resistance: +0.20 (fitness → immunity)

================================================================================
GROUP 2: SOCIAL ARCHITECTURE (traits 28-29)
================================================================================

TRAIT 28: group_loyalty
  Default: 0.5
  Heritability: h² = 0.42
  Science: Willingness to sacrifice personal fitness for group benefit.
           Distinct from cooperation_propensity (which is about exchange —
           I cooperate when I expect return). Group loyalty is kin selection
           coefficient — sacrifice even without expected reciprocation.
           Documented in twin studies of altruistic behavior toward family
           vs strangers. The E.O. Wilson eusociality dimension.

  Behavioral effects:
    engines/conflict.py — coalition defense:
      Current: agents join coalition defense if trust > 0.65
      Add: coalition_join_probability += agent.group_loyalty * 0.3
      AND: high group_loyalty agents join defense of FACTION members
           even with lower trust (group_loyalty gates loyalty extension)

    engines/conflict.py — third-party punishment:
      Current: cooperative agents punish aggressors at personal cost
      Add: punishment_probability += agent.group_loyalty * 0.15
      (loyal agents punish threats to their group even more)

    engines/resources.py — Phase 4 cooperation sharing:
      Current: agents share with trusted allies
      Add: if sharing with same-faction member AND agent.group_loyalty > 0.6:
           share_rate *= 1.2 (loyal agents give more to in-group)
           Also: group_loyalty reduces ostracism resistance — loyal agents
           share even with lower-cooperation faction members

    engines/institutions.py — norm compliance:
      High group_loyalty agents comply with norms even without enforcement:
      norm_compliance_bonus = agent.group_loyalty * 0.1
      (loyal agents follow group rules intrinsically)

  Correlation additions:
    group_loyalty ↔ cooperation_propensity: +0.30 (related but distinct)
    group_loyalty ↔ empathy_capacity: +0.25
    group_loyalty ↔ conformity_bias: +0.20
    group_loyalty ↔ outgroup_tolerance: -0.35 (DD27 trait — inverse relationship)
    group_loyalty ↔ aggression_propensity: +0.15 (loyal fighters)

---

TRAIT 29: outgroup_tolerance
  Default: 0.5
  Heritability: h² = 0.40
  Science: Constitutional openness to strangers/out-group members.
           Distinct from kinship_obligation BELIEF (DD25) — that's culturally
           transmitted. This is temperament — some individuals are heritably
           more open to strangers regardless of cultural context.
           Documented in xenophobia research, personality genetics,
           inter-group contact studies. Correlates with Openness (Big Five).

  Behavioral effects:
    engines/mating.py — cross-faction/cross-group mate search:
      Current: band-level males available at 0.3x weight (DD18)
      Add: effective_band_weight = 0.3 + agent.outgroup_tolerance * 0.3
      (tolerant females evaluate out-of-neighborhood males more seriously)

    engines/resources.py — cooperation sharing:
      Current: sharing requires trust > 0.5
      Add: tolerant agents lower their sharing trust threshold:
      effective_threshold = 0.5 - agent.outgroup_tolerance * 0.15
      (minimum threshold floor: 0.25)

    engines/reputation.py — migrant integration:
      Immigrant agents integrate faster when host agents have high outgroup_tolerance:
      In trust-building phase: host.remember(immigrant.id, outgroup_tolerance * 0.02)
      (tolerant agents extend initial trust to newcomers faster)

    models/society.py — migration acceptance:
      Band-level average outgroup_tolerance modulates immigration pull factor:
      pull_multiplier *= (0.7 + avg_outgroup_tolerance * 0.6)

  Correlation additions:
    outgroup_tolerance ↔ group_loyalty: -0.35 (already set above)
    outgroup_tolerance ↔ conformity_bias: -0.25 (open minds resist conformity)
    outgroup_tolerance ↔ novelty_seeking: +0.30 (curious = open)
    outgroup_tolerance ↔ empathy_capacity: +0.25
    outgroup_tolerance ↔ jealousy_sensitivity: -0.20

================================================================================
GROUP 3: TEMPORAL AND COGNITIVE (traits 30-31)
================================================================================

TRAIT 30: future_discounting
  Default: 0.5
  Heritability: h² = 0.40
  Science: Time preference — how strongly an agent discounts future rewards
           relative to immediate ones. HIGH future_discounting = impulsive,
           spend now, short-term thinking. LOW future_discounting = patient,
           save, invest, plan. One of the most studied heritable behavioral
           traits (Mischel marshmallow task, twin studies of delay of
           gratification). Distinct from impulse_control (which is about
           restraining actions) — future_discounting is about time horizon
           in decision-making. High impulse control but still present-focused
           is a different phenotype from patient planners.

  NOTE: high future_discounting = SHORT time horizon (counterintuitive name).
        Consider inverting to future_orientation [0=present, 1=future focused]
        for clarity. Implement as future_orientation where 1.0 = low discounting
        (patient, future-focused) and 0.0 = high discounting (impulsive, now).

  Behavioral effects:
    engines/resources.py — Phase 1 storage:
      Current: storage bonus = intelligence * intel_storage_bonus
      Add: storage_multiplier *= (0.6 + agent.future_orientation * 0.8)
      (future-oriented agents save more resources year-to-year)

    engines/resources.py — Phase 2 competitive weight:
      Add: future_orientation * 0.10 to competitive weight
      (patient agents use resources more efficiently over time)

    engines/reproduction.py — birth spacing:
      Future-oriented agents are less likely to conceive immediately when
      resources are below threshold:
      if resources < threshold AND agent.future_orientation > 0.6:
          conception_chance *= 0.7 (they wait for better conditions)

    engines/institutions.py — institutional adoption:
      Institutions are future investments. Future-oriented agents adopt
      norms faster and drift institutional strength upward:
      institutional drift boost += avg_future_orientation * 0.05
      (patient populations build better institutions)

    engines/mating.py — bond dissolution:
      Future-oriented agents are less likely to dissolve bonds opportunistically:
      dissolution_chance *= max(0.5, 1.0 - agent.future_orientation * 0.3)

  Correlation additions:
    future_orientation ↔ intelligence_proxy: +0.30 (smart agents plan ahead)
    future_orientation ↔ impulse_control: +0.35 (related but distinct)
    future_orientation ↔ conscientiousness: +0.40 (DD27 trait)
    future_orientation ↔ risk_tolerance: -0.25 (patient = risk averse)
    future_orientation ↔ novelty_seeking: -0.20

---

TRAIT 31: conscientiousness
  Default: 0.5
  Heritability: h² = 0.49
  Science: Big Five conscientiousness — organized, disciplined, reliable,
           hardworking, follows through on commitments. One of the most
           robustly documented heritable personality dimensions (~49% heritable).
           Distinct from impulse_control (restraining bad behavior) and
           future_orientation (time horizon) — conscientiousness is about
           execution quality and follow-through on intentions.

  Behavioral effects:
    engines/reputation.py — skill decay:
      Current: skills decay annually by skill_X_decay rate
      Add: effective_decay = skill_X_decay * max(0.4, 1.0 - agent.conscientiousness * 0.5)
      (conscientious agents maintain skills better — they practice consistently)

    engines/reproduction.py — child investment consistency:
      Current: child investment = child_investment_per_year
      Add: investment *= (0.8 + agent.conscientiousness * 0.4)
      (conscientious parents invest more consistently)

    engines/institutions.py — norm compliance:
      Conscientious agents follow institutional norms more reliably:
      combine with group_loyalty: both contribute to institutional compliance
      norm_compliance_bonus += agent.conscientiousness * 0.08

    engines/mortality.py — health maintenance:
      Conscientious agents maintain health through consistent behavior:
      health_decay *= max(0.75, 1.0 - agent.conscientiousness * 0.12)

  Correlation additions:
    conscientiousness ↔ future_orientation: +0.40 (already set)
    conscientiousness ↔ impulse_control: +0.35
    conscientiousness ↔ intelligence_proxy: +0.20
    conscientiousness ↔ risk_tolerance: -0.15 (careful ≈ risk averse)
    conscientiousness ↔ novelty_seeking: -0.25 (structured vs exploratory)

================================================================================
GROUP 4: PSYCHOPATHOLOGY SPECTRUM (traits 32-33)
================================================================================

TRAIT 32: psychopathy_tendency
  Default: 0.2  (baseline low — most people have low psychopathy)
  Heritability: h² = 0.50
  Science: Psychopathic traits — reduced empathy, reduced fear response,
           callousness, strategic manipulation — are ~50% heritable.
           Present in all human populations at low frequency (~1-4%).
           At moderate levels (not clinical): produces strategic, fearless,
           charming agents who exploit cooperation norms without reciprocating.
           Critical for modeling exploiter phenotypes that real populations have.
           Distinct from aggression_propensity (which is reactive/emotional)
           — psychopathy is cold, strategic, calculated.

  NOTE: Default should be 0.2 not 0.5 — most people are not psychopathic.
        Use low default to reflect realistic population distribution.

  Behavioral effects:
    engines/resources.py — cooperation sharing:
      High psychopathy agents accept cooperation shares but share less:
      if agent.psychopathy_tendency > 0.6:
          share_rate *= max(0.2, 1.0 - agent.psychopathy_tendency * 0.6)
      (they take but don't give — exploiter strategy)

    engines/conflict.py — conflict probability and targeting:
      High psychopathy agents have reduced fear-based conflict suppression:
      network_deterrence_factor *= max(0.3, 1.0 - agent.psychopathy_tendency * 0.5)
      (they're less deterred by allies — fearless)
      BUT: they are more strategic in target selection (prey on weak):
      strength_assessment_weight *= (1.0 + agent.psychopathy_tendency * 0.4)

    engines/mating.py — bond formation and dissolution:
      High psychopathy agents form bonds more easily (charm) but dissolve faster:
      bond_formation_weight *= (0.8 + agent.psychopathy_tendency * 0.4)
      dissolution_chance *= (1.0 + agent.psychopathy_tendency * 0.5)
      (they bond quickly but don't stay)

    engines/reputation.py — gossip and trust:
      High psychopathy agents are better at appearing trustworthy initially:
      initial_reputation_bonus = agent.psychopathy_tendency * 0.1
      BUT: when caught in exploitative behavior, reputation collapses faster:
      reputation_damage_multiplier = 1.0 + agent.psychopathy_tendency * 0.5

  Correlation additions:
    psychopathy_tendency ↔ empathy_capacity: -0.50 (strong inverse)
    psychopathy_tendency ↔ cooperation_propensity: -0.35
    psychopathy_tendency ↔ conscientiousness: -0.30
    psychopathy_tendency ↔ risk_tolerance: +0.25 (fearless)
    psychopathy_tendency ↔ dominance_drive: +0.20

---

TRAIT 33: anxiety_baseline
  Default: 0.5
  Heritability: h² = 0.40
  Science: Baseline threat sensitivity and anxiety disposition.
           Distinct from mental_health_baseline (which is resilience/stability
           under stress) — anxiety_baseline is the sensitivity of the threat
           detection system itself. High anxiety = detect threats early, avoid
           risks, cautious. Low anxiety = miss threats, take risks, bold.
           Well documented in behavioral genetics (neuroticism component).
           Interacts with environment: high anxiety is adaptive in dangerous
           environments, maladaptive in safe ones.

  Behavioral effects:
    engines/conflict.py — flee behavior:
      Current: flee threshold based on risk_tolerance
      Add: effective_flee_threshold = flee_threshold
           + agent.anxiety_baseline * config.anxiety_flee_boost
           (anxious agents flee more readily — survival advantage or cowardice)

    engines/mating.py — mate search caution:
      High anxiety females are more cautious in mate evaluation:
      choosiness_boost = agent.anxiety_baseline * 0.15
      (anxious agents are more risk-averse in mate choice)

    engines/resources.py — storage:
      Anxious agents hoard more as a safety buffer:
      storage_bonus += agent.anxiety_baseline * 0.10

    engines/conflict.py — conflict initiation:
      High anxiety dramatically reduces aggression expression:
      total_p *= max(0.3, 1.0 - agent.anxiety_baseline * 0.4)
      (anxious agents don't start fights even if genetically aggressive)

    engines/pathology.py — condition activation:
      High anxiety baseline increases mental_illness activation probability:
      condition_risk_multiplier['mental_illness'] *= (0.7 + agent.anxiety_baseline * 0.6)

  Correlation additions:
    anxiety_baseline ↔ mental_health_baseline: -0.45 (anxious ≠ resilient)
    anxiety_baseline ↔ risk_tolerance: -0.45 (anxious = risk averse)
    anxiety_baseline ↔ impulse_control: +0.15 (slightly more inhibited)
    anxiety_baseline ↔ novelty_seeking: -0.30 (anxious avoid novelty)
    anxiety_baseline ↔ mental_illness_risk: +0.30 (anxiety elevates risk)

================================================================================
GROUP 5: EVOLUTIONARY PSYCHOLOGY (trait 34)
================================================================================

TRAIT 34: paternal_investment_preference
  Default: 0.5
  Heritability: h² = 0.45
  Science: Female heritable preference for high-investment vs high-genetic-quality
           males. This is the "good genes vs good dad" trade-off — one of the
           most studied topics in evolutionary psychology (Gangestad & Simpson).
           HIGH value: female prefers high-investment partner (resources,
           pair bond stability, paternity confidence, parenting)
           LOW value: female prefers high genetic quality (physical strength,
           dominance, attractiveness, health) even at cost of less investment.
           Males inherit this gene too but it primarily expresses in female
           mate choice behavior. Male expression: willingness to invest vs
           preference for multiple low-investment matings.

  Behavioral effects (primarily female expression):
    engines/mating.py — female mate choice weights:
      Current: weights mate_value uniformly
      Add: if female:
        investment_weight = agent.paternal_investment_preference
        genetic_weight = 1.0 - investment_weight
        # Reweight mate_value components:
        # Investment signals: resources, bond_strength_history, parenting_history
        # Genetic signals: physical_strength, health, attractiveness, dominance
        adjusted_mate_value = (
            genetic_weight * (health*0.3 + attractiveness*0.25 + dominance*0.15
                             + physical_strength*0.15 + status*0.15)
            + investment_weight * (resources_norm*0.4 + reputation*0.3
                                  + cooperation*0.2 + bond_stability*0.1)
        )

    engines/mating.py — EPC behavior:
      Females with LOW paternal_investment_preference more likely to EPC:
      epc_chance *= (1.5 - agent.paternal_investment_preference)
      (low-investment-preference females seek genetic quality affairs)

    engines/mating.py — male expression:
      Males with HIGH paternal_investment_preference invest more in existing
      bonds vs seeking new mates:
      if male:
        bond_dissolution_resistance += agent.paternal_investment_preference * 0.2
        new_mate_seeking_probability *= (1.0 - agent.paternal_investment_preference * 0.3)

  Correlation additions:
    paternal_investment_preference ↔ maternal_investment: +0.30 (investment orientation)
    paternal_investment_preference ↔ jealousy_sensitivity: +0.20 (invest = monitor)
    paternal_investment_preference ↔ conscientiousness: +0.25 (planners prefer investment)
    paternal_investment_preference ↔ future_orientation: +0.20
    paternal_investment_preference ↔ risk_tolerance: -0.15

================================================================================
IMPLEMENTATION ORDER
================================================================================

Implement in 5 groups matching the sections above. After each group, run:
  python main.py --years 20 --population 100 --seed 42
Confirm no crashes before proceeding to next group.

Group 1: physical_strength + endurance (indices 26-27)
Group 2: group_loyalty + outgroup_tolerance (indices 28-29)
Group 3: future_orientation + conscientiousness (indices 30-31)
Group 4: psychopathy_tendency + anxiety_baseline (indices 32-33)
Group 5: paternal_investment_preference (index 34)

================================================================================
WHAT TO MODIFY IN EACH FILE
================================================================================

models/agent.py:
  1. Add 9 new entries to HERITABLE_TRAITS list (indices 26-34)
  2. Add 9 new h² entries to TRAIT_HERITABILITY dict
  3. Expand _build_correlation_matrix() with all new correlation entries
     (listed per-trait above — approximately 35 new correlation pairs)
  4. Add 9 new float fields to Agent dataclass
     NOTE: psychopathy_tendency default=0.2, all others default=0.5
  5. Rename future_discounting → future_orientation for clarity
     (1.0 = future-focused/patient, 0.0 = present-focused/impulsive)

engines/conflict.py:
  - physical_strength: combat power additive
  - group_loyalty: coalition defense + punishment probability
  - outgroup_tolerance: no direct conflict effect
  - psychopathy_tendency: reduced deterrence, stronger prey selection
  - anxiety_baseline: flee boost, conflict initiation suppression

engines/resources.py:
  - physical_strength: foraging competitive weight + sex differential
  - endurance: foraging bonus
  - group_loyalty: in-faction sharing boost
  - outgroup_tolerance: lower sharing trust threshold
  - future_orientation: storage multiplier + competitive weight
  - psychopathy_tendency: accept shares but don't give

engines/mating.py:
  - physical_strength: male mate value boost
  - outgroup_tolerance: out-of-neighborhood mate search weight
  - future_orientation: bond dissolution resistance
  - psychopathy_tendency: easy bond formation, fast dissolution
  - paternal_investment_preference: female mate choice reweighting + EPC + male investment

engines/reproduction.py:
  - future_orientation: birth spacing under resource stress
  - conscientiousness: child investment consistency

engines/mortality.py:
  - endurance: childbirth survival + health decay
  - conscientiousness: health maintenance

engines/reputation.py:
  - conscientiousness: skill decay modulator
  - outgroup_tolerance: migrant trust extension
  - psychopathy_tendency: initial reputation + damage multiplier
  - group_loyalty: faction sharing boost

engines/institutions.py:
  - group_loyalty: norm compliance
  - conscientiousness: norm compliance
  - future_orientation: institutional drift boost

engines/pathology.py:
  - anxiety_baseline: mental_illness activation multiplier

models/society.py:
  - outgroup_tolerance: immigration pull factor

config.py:
  Add these new parameters:
  physical_strength_combat_weight: float = 0.12
  endurance_foraging_bonus: float = 0.06
  anxiety_flee_boost: float = 0.10
  psychopathy_sharing_penalty: float = 0.6
  outgroup_tolerance_sharing_threshold: float = 0.15
  future_orientation_storage_multiplier: float = 0.8
  conscientiousness_skill_decay_modifier: float = 0.5

metrics/collectors.py:
  Add to trait means section:
  avg_physical_strength, avg_endurance, avg_group_loyalty,
  avg_outgroup_tolerance, avg_future_orientation, avg_conscientiousness,
  avg_psychopathy_tendency, avg_anxiety_baseline,
  avg_paternal_investment_preference
  Also: psychopathy_std (psychopathy variance matters — expect right-skewed distribution)

================================================================================
SPECIAL VALIDATION TESTS
================================================================================

After full implementation, run these targeted validations:

1. PSYCHOPATHY TEST:
   Run 200yr FREE_COMPETITION with 5 seeds.
   Expect: psychopathy_tendency mean stays LOW (0.2-0.35)
   because exploiter strategy should be selected against in stable groups.
   If psychopathy rises above 0.4, the penalty mechanisms need strengthening.

2. PHYSICAL STRENGTH SEX DIFFERENTIAL TEST:
   Check final_agents.csv — male mean physical_strength should produce
   higher combat_power than female of equal genetic strength value.
   Verify sex multiplier is applying correctly.

3. FUTURE ORIENTATION INSTITUTIONAL TEST:
   Run EMERGENT_INSTITUTIONS with 5 seeds.
   Expect: law_strength should emerge faster and reach higher values than
   pre-DD27 because future-oriented agents drive institutional development.

4. PATERNAL INVESTMENT PREFERENCE TEST:
   Run HIGH_FEMALE_CHOICE with 5 seeds.
   Compare: do females with low paternal_investment_preference have higher
   EPC rates than high-preference females? This should be observable in
   infidelity_rate segmented by paternal_investment_preference quartile.

================================================================================
DELIVERABLES
================================================================================

1. docs/deep_dive_27_trait_completion.md — design decisions, all 9 traits,
   heritability values, behavioral effect formulas, correlation additions
2. models/agent.py — 9 new trait fields, expanded HERITABLE_TRAITS,
   TRAIT_HERITABILITY, _build_correlation_matrix
3. All engine files with targeted modifications (listed above)
4. config.py — 7 new parameters
5. metrics/collectors.py — 9 new trait mean metrics + psychopathy_std
6. DEV_LOG.md entry
7. CHAIN_PROMPT.md + STATUS.md update

================================================================================
BACKWARD COMPATIBILITY REQUIREMENTS
================================================================================

- All 26 existing traits unchanged — no modifications to existing trait fields,
  heritability values, or engine effects
- All 9 new traits default to their specified values (0.5 except psychopathy_tendency=0.2)
- Existing scenarios must still run without modification
- Existing metrics must still be computed identically
- Run validation: post-DD27 baseline Gini, violence, cooperation should be
  within 15% of pre-DD27 values (some drift expected from new trait interactions)

================================================================================
SCIENTIFIC NOTES
================================================================================

After DD27, the trait model covers:
  PHYSICAL: strength, robustness, endurance, pain_tolerance, longevity, disease_resistance
  COGNITIVE: intelligence, emotional_intelligence, impulse_control, conscientiousness
  TEMPORAL: future_orientation
  PERSONALITY: risk_tolerance, novelty_seeking, anxiety_baseline, mental_health_baseline
  SOCIAL: aggression, cooperation, dominance_drive, group_loyalty, outgroup_tolerance,
          empathy_capacity, conformity_bias, status_drive, jealousy_sensitivity
  REPRODUCTIVE: fertility, sexual_maturation_rate, maternal_investment,
                paternal_investment_preference, attractiveness_base
  PSYCHOPATHOLOGY: psychopathy_tendency, mental_illness_risk, cardiovascular_risk,
                   autoimmune_risk, metabolic_risk, degenerative_risk

This covers all major domains of heritable human individual differences that
have documented behavioral effects in anthropological and behavioral genetics
literature. No major scientifically validated heritable trait domain is absent
after DD27.

FINAL TRAIT COUNT: 35 (the scientifically complete ceiling for this model)
