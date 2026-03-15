# SIMSIV — Prompt Library

All Claude prompts used to build SIMSIV, copy-paste ready.

## Phase Prompts

| File | Purpose |
|---|---|
| `phase1_design.md` | System design — models, rules, assumptions |
| `phase2_skeleton.md` | Skeleton implementation — working end-to-end |
| `phase3_experiments.md` | Experiment framework — scenarios, runner, output |
| `phase4_roadmap.md` | Roadmap and validation strategy |

## Templates

| File | Purpose |
|---|---|
| `deep_dive_template.md` | Template for any new deep dive |
| `iteration_template.md` | Targeted change or feature iteration |
| `debug_template.md` | Bug diagnosis and fix |

## Deep Dive Prompts (DD01-DD26)

| # | File | Subsystem | Status |
|---|---|---|---|
| 01 | `deep_dive_01_mating.md` | Mating system — female choice, pair bonds, infidelity | COMPLETE |
| 02 | `deep_dive_02_resources.md` | Resource model — 8-phase engine, Gini, cooperation | COMPLETE |
| 03 | `deep_dive_03_conflict.md` | Conflict — deterrence, flee, bystanders, subordination | COMPLETE |
| 04 | `deep_dive_04_genetics.md` | Trait inheritance — mutation variance, stress mutation | COMPLETE |
| 05 | `deep_dive_05_institutions.md` | Institutions — drift, emergence, property rights | COMPLETE |
| 06 | `deep_dive_06_household.md` | Household — birth interval, childhood mortality, orphans | COMPLETE |
| 07 | `deep_dive_07_reputation.md` | Reputation — gossip, trust decay, social memory | COMPLETE |
| 08 | `deep_dive_08_prestige.md` | Prestige/dominance split — dual status hierarchy | COMPLETE |
| 09 | `deep_dive_09_disease.md` | Disease — epidemics, vulnerability, overcrowding | COMPLETE |
| 10 | `deep_dive_10_seasons.md` | Seasonal cycles — resource modulation, storage | COMPLETE |
| 11 | `deep_dive_11_coalitions.md` | Coalitions — defense, third-party punishment, ostracism | COMPLETE |
| 12 | `deep_dive_12_signaling.md` | Status signaling — resource display, dominance bluffing | COMPLETE |
| 13 | `deep_dive_13_demographics.md` | Demographics — sex-differential mortality, fertility curve | COMPLETE |
| 14 | `deep_dive_14_factions.md` | Factions — detection, merge, schism, in-group bias | COMPLETE |
| 15 | `deep_dive_15_genomics.md` | Extended genomics — 21 traits, per-trait h², correlations | COMPLETE |
| 16 | `deep_dive_16_development.md` | Developmental biology — plasticity, orchid/dandelion | COMPLETE |
| 17 | `deep_dive_17_medical.md` | Medical/pathology — 5 condition risks, trauma, remission | COMPLETE |
| 18 | `deep_dive_18_proximity.md` | Proximity tiers — household/neighborhood/band | COMPLETE |
| 19 | `deep_dive_19_migration.md` | Migration — emigration push, immigration pull | COMPLETE |
| 20 | `deep_dive_20_leadership.md` | Leadership — war leader, peace chief per faction | COMPLETE |
| 21 | `deep_dive_21_resource_types.md` | Resource types — subsistence, tools, prestige goods | COMPLETE |
| 22 | `deep_dive_22_life_stages.md` | Life stages — childhood through elder, age behaviors | COMPLETE |
| 23 | `deep_dive_23_intelligence_audit.md` | Intelligence audit — diminishing returns fix | COMPLETE |
| 24 | `deep_dive_24_epigenetics.md` | Epigenetics — transgenerational stress, trauma contagion | COMPLETE |
| 25 | `deep_dive_25_beliefs.md` | Beliefs — 5 cultural dimensions, social influence | COMPLETE |
| 26 | `deep_dive_26_skills.md` | Skills — 4 experiential domains, mentoring, decay | COMPLETE |

## Chain Runner

| File | Purpose |
|---|---|
| `run_remaining_dives.md` | Automated chain runner for DD18-DD26 |
