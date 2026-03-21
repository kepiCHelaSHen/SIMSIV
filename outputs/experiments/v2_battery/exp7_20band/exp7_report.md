# Experiment 7 — 20-Band Mixed Simulation (Turn 11)

## Setup
- 20 bands: 10 FREE_COMPETITION (law=0.0) + 10 STRONG_STATE (law=0.8)
- All bands in the SAME simulation, competing against each other
- 200yr, 30 agents/band (600 total initial), 6 seeds
- Tuned ClanConfig: raid_base_probability=0.50, raid_scarcity_threshold=20.0,
  raid_trust_suppression_threshold=0.5
- base_interaction_rate=0.5 (190 band pairs)
- Runtime: 9.2 minutes (552s)

## Results at Year 200

| Seed | Coop (Free) | Coop (State) | Divergence | Free Bands | State Bands | Total Pop |
|------|------------|-------------|-----------|------------|-------------|-----------|
| 42   | 0.405      | 0.482       | -0.077    | 2          | 20          | 1175      |
| 137  | 0.413      | 0.506       | -0.094    | 3          | 19          | 1059      |
| 271  | 0.398      | 0.500       | -0.103    | 3          | 17          | 1108      |
| 512  | 0.425      | 0.528       | -0.102    | 3          | 18          | 1385      |
| 999  | 0.411      | 0.537       | -0.125    | 2          | 22          | 1620      |
| 1337 | 0.413      | 0.500       | -0.087    | 2          | 20          | 1270      |

## Statistical Summary

- **Mean divergence (Free - State): -0.098 +/- 0.016**
- **One-sample t-test vs 0: t(5) = -14.62, p < 0.0001**
- **Cohen's d = -5.97** (massive effect size)
- **State > Free in 6/6 seeds** (perfectly consistent)

## Demographic Dynamics

The result is driven by demographic dominance:
- Free bands start with 10 but only 2-3 survive to year 200
- State bands start with 10 and grow to 17-22 (via fission)
- This IS between-group selection — but selecting FOR institutional governance

### Mechanism

1. **State bands maintain cooperation** via law enforcement and property rights.
   Higher cooperation → better resource sharing → healthier population.

2. **Healthier populations grow** → exceed fission threshold (150) → split
   into daughter bands. Daughters inherit the State Config.

3. **Free bands lack enforcement** → cooperation drifts lower (0.40-0.43 vs
   0.48-0.54). Lower cooperation → less resource sharing → slower growth
   → fewer fission events → gradual demographic decline.

4. **Free bands that raid State bands** face larger, better-coordinated
   defensive coalitions (State bands have higher cooperation → cohesion bonus).
   Raid casualties compound the demographic disadvantage.

5. **Net result**: institutional governance is the fitter strategy. State
   bands outcompete Free bands through demographic dominance, not because
   State bands are "better at war" but because they are better at
   maintaining the population base that warfare requires.

## Interpretation

**This is unambiguous support for North (1990) over Bowles/Gintis (2006).**

The Bowles mechanism (coalition defence → cooperation) IS present — Exp 3
confirmed that cooperation increases with raid intensity. But when Free and
State bands compete directly at adequate scale (n=20), institutional
governance provides a larger fitness advantage than the coalition defence
benefit. Institutions don't just substitute for prosocial traits — they
outcompete the trait-selection mechanism by maintaining the demographic base
that between-group selection requires.

The irony: between-group selection IS operating, but it selects for the
institutional regime that maintains cooperation (State), not for the
regime where cooperation must be sustained by group selection alone (Free).
Institutions co-opt between-group selection rather than being replaced by it.

## What to Tell Bowles

Your mechanism is real but insufficient. When we scale our multi-band
simulation to 20 groups (10 Free + 10 State) competing over 200 years,
Free bands develop cooperation of ~0.41 while State bands reach ~0.51
(p < 0.0001, d = -5.97, 6/6 seeds). The institutional regime dominates
demographically: State bands fission and proliferate (17-22 bands) while
Free bands dwindle to 2-3 survivors.

The coalition defence mechanism you described does raise cooperation with
conflict intensity (confirmed in our dose-response experiment). But at
the population level, institutional governance maintains cooperation more
effectively than between-group selection alone. The mechanism that wins is
not trait selection — it is institutional-regime selection: between-group
competition selects for the GOVERNANCE SYSTEM that best maintains
cooperation, not for the TRAITS that produce cooperation without governance.

This is consistent with your 2006 conclusion that "the group-level advantage
of altruism rarely compensates for its individual-level cost without
additional mechanisms" — except that the additional mechanism turns out
to be North's institutions, not warfare.
