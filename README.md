# SIMSIV

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19065475.svg)](https://doi.org/10.5281/zenodo.19065475)

### Simulation of Intersecting Social and Institutional Variables

SIMSIV is a calibrated agent-based simulation of band-level human social
evolution, grounded in behavioral genetics, evolutionary anthropology, and
institutional economics. Every agent is a complete simulated person with a
genome, developmental history, medical biography, earned skills, culturally
transmitted beliefs, and a life story from birth to death.

**v1.0 band simulator (under review at JASSS) + v2.0 multi-band clan simulator with drift experiment.**
35 heritable traits, 13 engines, 187 tests, calibrated to score 1.000 against 9 anthropological benchmarks.

**v2.0 JASSS Resubmission** — Paired-seed 500-year divergence experiment
confirms cognitive substitution (intelligence p=0.023, impulse control p=0.031)
and discovers selection sheltering (the state preserves aggressive genotypes).

All findings are emergent. Nothing is scripted.

---

## The Central Research Question

> *Does institutional governance systematically reduce directional selection on
> heritable prosocial behavioral traits — providing computational evidence that
> institutions and genes are substitutes, not complements, in human social
> evolution?*

This engages the debate between Camp A (Bowles/Gintis: traits and institutions
co-evolve upward together) and Camp B (North: institutions substitute for
internal motivation).

---

## Quick Start

```bash
pip install -r requirements.txt
python main.py --seed 42 --years 200 --population 500
streamlit run dashboard/app.py
```

Run scenario experiments:

```bash
python scripts/run_experiments.py --scenarios FREE_COMPETITION STRONG_STATE --seeds 5 --years 200
python scripts/run_experiments.py --list   # show all scenarios
```

Validate calibration:

```bash
python scripts/validate_best_config.py --seeds 10 --years 200
```

---

## The 9 Simulation Engines

Each annual tick runs through nine interacting subsystems in order:

| Step | Engine | Function |
|------|--------|----------|
| 1 | Environment | Seasonal cycles, scarcity shocks, epidemic events |
| 2 | Resources | 8-phase distribution across 3 resource types |
| 3 | Conflict | Violence, deterrence, coalitions, cross-sex dynamics |
| 4 | Mating | Female choice, male competition, pair bonding, EPC |
| 5 | Reproduction | h²-weighted trait inheritance, developmental plasticity |
| 6 | Mortality | Aging, sex-differential mortality, epidemic vulnerability |
| 6.3 | Migration | Voluntary emigration and immigration |
| 6.5 | Pathology | Disease activation, trauma, epigenetic stress |
| 7 | Institutions | Norm enforcement, property rights, institutional drift |
| 8 | Reputation | Gossip networks, trust, beliefs, skills, faction detection |

---

## The 35 Heritable Traits

**Physical:** physical_strength, endurance, physical_robustness, pain_tolerance,
longevity_genes, disease_resistance

**Cognitive:** intelligence_proxy (h²=0.65), emotional_intelligence,
impulse_control, conscientiousness

**Temporal:** future_orientation

**Personality:** risk_tolerance, novelty_seeking, anxiety_baseline,
mental_health_baseline

**Social:** aggression_propensity, cooperation_propensity, dominance_drive,
group_loyalty, outgroup_tolerance, empathy_capacity, conformity_bias,
status_drive, jealousy_sensitivity

**Reproductive:** fertility_base, sexual_maturation_rate, maternal_investment,
paternal_investment_preference, attractiveness_base

**Psychopathology risk:** psychopathy_tendency, mental_illness_risk,
cardiovascular_risk, autoimmune_risk, metabolic_risk, degenerative_risk

---

## Key Emergent Findings

These arise from interaction rules — not scripted outcomes:

### v2.0 Paired-Seed Divergence (500yr, 10 paired seeds)

- **Cognitive substitution:** Intelligence (p=0.023, d=0.87) and impulse control
  (p=0.031, d=0.80) are displaced significantly more under anarchy than the state
- **Selection sheltering:** The state *preserves* aggressive genotypes by suppressing
  the lethal violence that would otherwise eliminate them before reproduction
- **Cooperation attractor:** Cooperation converges to ~0.51 regardless of governance
  regime — scale-invariant across N=250-1000 (Squazzoni N-Test)

### v1.0 Scenario Experiments

- Cooperation and intelligence reliably selected for across all scenarios
- Aggression reliably selected against (5 independent fitness cost channels)
- ENFORCED_MONOGAMY reduces violence 37%, unmated males 65%
- STRONG_STATE reduces Gini 40%, violence 49% — without changing cooperation trait
- Law strength self-organizes from 0 → 0.83 in EMERGENT_INSTITUTIONS over 200yr
- Cooperation trait is a robust emergent attractor (max sensitivity r = 0.20)

---

## Scenarios

| Scenario | Purpose |
|----------|---------|
| `FREE_COMPETITION` | Null hypothesis — weak endogenous governance |
| `NO_INSTITUTIONS` | True zero-governance control |
| `ENFORCED_MONOGAMY` | Mating system effects |
| `ELITE_POLYGYNY` | Reproductive inequality |
| `HIGH_FEMALE_CHOICE` | Sexual selection |
| `RESOURCE_ABUNDANCE` | Ecological effects on cooperation |
| `RESOURCE_SCARCITY` | Stress-induced cooperation |
| `HIGH_VIOLENCE_COST` | Aggression selection pressure |
| `STRONG_PAIR_BONDING` | Family stability effects |
| `STRONG_STATE` | Strong fixed governance |
| `EMERGENT_INSTITUTIONS` | Institutional self-organization |

---

## Calibration

AutoSIM uses simulated annealing to fit 36 parameters against 9 targets drawn
from ethnographic and historical demography literature. See `autosim/targets.yaml`
for sources and `docs/validation.md` for the full calibration report.

Best config: `autosim/best_config.yaml` — score 1.000, Run 3, 816 experiments.
Held-out validation: 10 seeds × 200yr, mean score 0.934, zero collapses.

---

## Project Structure

```
SIMSIV/
├── config.py              # ~257 tunable parameters
├── simulation.py          # Annual tick orchestrator
├── models/               # Agent, Society, Environment
├── engines/              # 12 simulation subsystems
├── metrics/              # ~130 tracked metrics per tick
├── experiments/          # Scenario runner and definitions
├── autosim/              # Calibration engine + results
├── scripts/              # Validation, experiments, divergence scripts
├── results/              # RESULTS_SUMMARY.md (definitive data manifest)
├── dashboard/            # Streamlit visualization
├── tests/                # 187 tests (22 v1 + 141 v2 clan + 24 drift/convergence)
├── docs/                 # ODD Protocol, manuscript, figures, validation
│   └── figures/          # 7 publication figures (F1-F8 + originals)
├── devlog/               # Full development history
└── prompts/              # Executable build prompts
```

---

## Specification Drift — Working Paper

**"LLMs Generate from Priors, Not Specifications"** — we ran a controlled experiment measuring coefficient drift across GPT-4o, Grok-3, and Claude on SIMSIV implementation tasks.

**Key finding:** Without source code in the prompt, frontier LLMs produced incorrect coefficients on 99% of measurements (95/96, Fisher's exact p = 4×10⁻¹⁰). With the SIMSIV-V2 Builder/Critic/Reviewer protocol, drift dropped to 0%.

- **Paper:** [`docs/SIMSIV_V2_White_Paper.md`](docs/SIMSIV_V2_White_Paper.md)
- **Figure 1 — Drift scatter plot:** [`docs/figures/figure1_drift_scatter.png`](docs/figures/figure1_drift_scatter.png)
- **Figure 2 — Drift sensitivity:** [`docs/figures/figure2_drift_sensitivity.png`](docs/figures/figure2_drift_sensitivity.png)
- **Experiment code:** [`experiments/drift_experiment/`](experiments/drift_experiment/)
- **Convergence battery:** [`tests/test_milestone_battery.py`](tests/test_milestone_battery.py) (4 milestones × 30 seeds)
- **Tag:** `v2-working-paper-alpha`

## Context Hacking — Turning LLM Weaknesses into Strengths

The drift experiment revealed something deeper than a bug: **LLMs generate from training priors, not from your specification.** Every frontier model we tested (GPT-4o, Grok-3, Claude) confidently produced wrong coefficients when the source code wasn't in context — because it was generating from what it "remembered" about similar models, not from what you asked it to build.

The standard response is to treat this as a flaw to suppress. We went the other direction: **build systems that exploit it.**

### Layer 1: Prior-as-Detector

The Critic subagent ("The Pessimist") reads from frozen source code before every review. When the Builder drifts from spec, the Critic catches it precisely BECAUSE it knows what the "textbook answer" looks like vs the grounded answer. The model's tendency to hallucinate becomes a tripwire — if the output matches the prior instead of the source, it's flagged.

This is why the Critic's prompt says "argue AGAINST the science before scoring it." An LLM that tries to disprove its own output is more rigorous than one that tries to confirm it. The prior-generation tendency makes the Critic naturally suspicious of anything that looks "too standard" — exactly the pattern that indicates drift.

### Layer 2: Synthetic Dialectic (Opposing Subagent Goals)

Three subagents with deliberately opposing objectives:

| Subagent | Goal | Mindset |
|----------|------|---------|
| **Builder** | Implement exactly what's specified | "Read the constitution before every build" |
| **Critic** | Prove the science is wrong | "Assume the build failed until proven otherwise" |
| **Reviewer** | Find code smells, nothing else | "No opinions about science or architecture" |

The tension is deliberate. The Builder optimizes for completion. The Critic optimizes for failure. The Reviewer ignores both and checks hygiene. No single agent can satisfy all three — the system only converges when the code is actually correct. This is Generator-Critic-Refiner (Google ADK 2025) adapted for scientific rigor.

### Layer 3: Frozen Code as Forcing Function

The v1 codebase produced a submitted paper (BIORXIV/2026/711970). It is immutable — no agent can modify it, fix its bugs, or "improve" it. This creates a hard constraint: all generation must ground against actual source lines, not the model's prior beliefs about what the code should look like.

Every coefficient must trace to a file and line number. The Critic verifies this with `git diff` — if a frozen file was touched, the build is blocked with a hard gate (Gate 1 = 1.0 required). This forces the Builder to compose WITH the existing code rather than rewriting it from priors.

### Layer 4: Multi-Model Disagreement as Signal

The external council runs GPT-4o and Grok-3 against the same innovation log after every build. Different models have different training priors — they've seen different papers, different codebases, different implementations of the same concepts.

When GPT-4o and Grok agree on a problem, it's likely real. When they disagree, it signals an area where priors diverge — exactly where specification drift is most dangerous. The protocol: fix anything BOTH models flag (consensus = must fix). Consider anything ONE model flags (use judgment). If both flag DRIFT — stop everything and re-read the master design doc.

### Layer 5: Context Window as a Managed Resource

Each subagent runs in its own isolated 200K-token context. The parent orchestrator gets signal only — not the full noise of every file read and every test run. This prevents the core failure mode of long AI sessions: context window collapse, where the model loses track of its own decisions as the conversation grows.

Key mechanisms:
- **State vector compression**: Every 5 turns, the system writes a 10-15 line "save game" (`outputs/state_vector.md`) capturing turn number, milestone, mode, last 3 failures, winning parameters, metric status, and next focus. After context reset, this is the anchor.
- **Innovation log as external memory**: `V2_INNOVATION_LOG.md` is the persistent record that survives context resets. Every turn appends: what was built, what failed, critic scores, anomaly results, metric deltas, and what next turn should do.
- **Dead end tracking**: Failed approaches go to `v2_dead_ends.md` with what was tried, why it failed, and why it's a dead end. The system reads this BEFORE choosing what to build — it cannot repeat logged failures.

### Layer 6: σ-Gated Statistical Verification

No code merges on vibes. Every build runs a 3-seed anomaly check:

| Check | Threshold | Purpose |
|-------|-----------|---------|
| Cooperation | > 0.25 per seed | Population hasn't collapsed to defectors |
| Aggression | < 0.70 per seed | No runaway violence |
| Population | > 0 per seed | No extinction |
| Cooperation std | < 0.15 across seeds | Not stochastically unstable |
| Aggression std | < 0.15 across seeds | Not stochastically unstable |

If any seed fails bounds: ANOMALY. Two consecutive anomalies trigger investigation. Three trigger EXIT 3 (stop and wait for human). In Exploration Mode, anomaly triggers the Reversion Protocol — `git checkout` to the last passing tag, log the failure, return to Validation Mode. No patching broken exploration code.

The convergence battery (`tests/test_milestone_battery.py`) extends this: 4 milestones × 30 seeds, all primary metrics must have σ < 0.15. This is the gate that separates "works on one seed" from "works reliably."

### Layer 7: Two Modes with Negative Feedback

The loop operates in two modes with automatic switching:

**Validation Mode** (default): Full literature grounding required. Critic is a hard blocker. Council runs before build. Every claim needs a citation. Use for: known mechanisms, calibration, fixing issues.

**Exploration Mode** (when stuck): Literature grounding relaxed — state a falsifiable hypothesis instead. Critic is advisory only. Council runs after build. Reversion Protocol active. Max 3 consecutive Exploration turns, then forced return to Validation.

The switching creates a negative feedback loop:
- No metric improvement for 5 turns → switch to Exploration (try something new)
- Exploration fails anomaly check → Reversion Protocol → back to Validation
- 3 Exploration turns with no improvement → EXIT 2 (stop, wait for human)

This prevents both stagnation (forced exploration) and chaos (forced reversion). The system oscillates between rigor and creativity with automatic damping.

### Layer 8: Token-Efficient Architecture

Running multi-agent scientific workflows burns tokens fast (4-7x vs single session). Every design choice optimizes for token efficiency:

- **Subagents get targeted prompts**: The Builder gets "build X" not "here's the whole project." The Critic gets the specific files to review, not the full codebase.
- **Health checks are 3 lines**: "Confirm active. State first rule from CLAUDE.md." If the answer is wrong, re-invoke with full role description. If right, proceed. No wasted tokens on role re-establishment.
- **Partial results save every N runs**: Long experiments write CSVs incrementally so a crash doesn't lose everything. The system can resume from partial data.
- **CHAIN_PROMPT.md is the single source of truth**: One file, read once, contains all confirmed design decisions. No searching through conversation history. If it's not in CHAIN_PROMPT.md, it's not decided.

### Layer 9: The Self-Correcting Loop

The most important property: **the system catches its own mistakes.**

The Exp 2 false positive is the proof. At n=3 seeds, the factorial showed an interaction effect of +0.039 (suggesting the Bowles mechanism causally drives cooperation). The system logged this as a finding. The critic flagged n=3 as underpowered (Ioannidis 2005: false discovery rate >50% at 10% statistical power). The replication at n=10 killed it: +0.0004, p=0.954.

A human scientist might have published the n=3 result. The loop didn't — because the critic's adversarial stance forced the replication, and the replication was honest. The dead end was logged. The system scaled up to n=20 bands and found the real result (p<0.0001, d=-5.97).

**The false positive wasn't a failure of the system. It was the system working correctly.** Error → detection → correction → stronger result. That sequence, fully documented in the git log, is the core contribution.

### The Result

99% drift without grounding → 0% drift with the protocol. The weakness didn't go away — it was architecturally contained and repurposed as a detection mechanism.

**Don't fight what LLMs are bad at. Build systems that use it.**

## Development Protocol — Anti-Drift Framework

SIMSIV v2 uses a **Builder/Critic/Reviewer** protocol to prevent specification drift in LLM-generated scientific code.

**σ-Gated Commits:** No code is merged unless variance across n=30 seeds is < 0.15 on all primary metrics.

**Critic-Led Friction:** The Critic enforces 100% compliance with the frozen JASSS specification (submission 2026:81:1). Every coefficient must trace to a source-code line and a literature citation.

**Automated Kill-Switches:** Five exit conditions halt the loop: science complete, performance gate, anomaly, misalignment, or human stop.

**Self-Correcting Science:** The loop caught its own false positive (Exp 2 interaction effect +0.039 at n=3, collapsed to +0.0004 at n=10), logged the dead end, scaled up the experiment, and found the real result at n=20 bands. The entire error-correction sequence is in the git log.

---

## Development Methodology

Built over 27 deep-dive design sessions (DD01-DD27), each adding a
scientifically grounded subsystem. Full history in `CHAIN_PROMPT.md`,
`devlog/`, and `prompts/`.

**AI disclosure:** Code development was assisted by Claude (Anthropic). All
scientific decisions, hypotheses, experimental designs, and interpretations
are the author's own.

This repository is fully transparent — every design decision, calibration run,
validation result, and experiment output is committed to git.

---

## v2 Clan Simulator — Between-Group Selection Results

v2 extends the band simulator with inter-band trade, raiding, migration, fission/extinction, and per-band institutional differentiation. 7,663 lines, 165 tests. Built autonomously by the loop in 11 turns.

**The definitive experiment** (Exp 7): 20 bands (10 FREE_COMPETITION + 10 STRONG_STATE) competing directly for 200-500 years.

| Result | Value |
|--------|-------|
| Cooperation divergence (Free - State) | **-0.098 ± 0.016** |
| Statistical significance | **p < 0.0001, d = -5.97** |
| Direction | **State > Free in 6/6 seeds** |
| Free band survival | 2-3 out of 10 |
| State band proliferation | 17-22 (via fission) |

**Interpretation:** Institutional governance wins. Between-group selection is real (cooperation increases with raid intensity, Exp 3) but is co-opted by institutional regimes — evolution selects for the governance system that maintains cooperation, not for the traits that produce cooperation without governance.

Full results: [`docs/v2_findings.md`](docs/v2_findings.md) | Battery report: [`outputs/experiments/v2_battery/BATTERY_REPORT.md`](outputs/experiments/v2_battery/BATTERY_REPORT.md)

---

## Known Limitations

- **Band count sensitivity:** Between-group selection is undetectable at n=4 bands (noise) but clear at n=20 (p<0.0001). Results are scale-dependent.
- **No spatial structure:** Proximity tiers are abstract, not geographic.
- **Annual time step:** Sub-annual dynamics are abstracted.
- **Parameter sensitivity:** Phase diagram (institutional strength x war intensity) in progress. Current results hold at one parameterization.

Full limitations: `docs/validation.md` Section 4.

---

## Roadmap

**v1 — Band simulator** (complete): Single band, 35 traits, calibrated. Under review at JASSS.

**v2 — Clan simulator** (complete): Multiple bands, trade, raiding, between-group selection. North vs Bowles tested.

**v2.1 — Phase diagram** (in progress): Map the boundary between North and Bowles across institutional strength x war intensity parameter space.

**v3 — Tribe/Chiefdom** (planned): Territorial dynamics, hereditary leadership.

**Game layer** (planned): Strategy game built on the simulation engine.

---

## License

See LICENSE file.
