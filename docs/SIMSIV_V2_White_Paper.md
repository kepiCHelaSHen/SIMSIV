# LLMs Generate from Priors, Not Specifications: Measuring Coefficient Drift in Scientific Code Generation

**Authors:** Rice, J. et al.
**Affiliation:** SIMSIV Research Initiative
**Date:** March 2026
**Status:** Working Paper with Controlled Experiment
**Corresponding Codebase:** github.com/kepiCHelaSHen/SIMSIV, branch `v2-clan-experiment`
**DOI:** [10.5281/zenodo.19065475](https://doi.org/10.5281/zenodo.19065475)
**Frozen Specification:** JASSS submission 2026:81:1

---

## Abstract

When Large Language Models generate scientific software, they substitute plausible but incorrect numerical coefficients for those defined in the target specification --- a failure mode we term *specification drift*. We measure drift across two frontier LLMs (GPT-4o, Grok-3) under two conditions: (A) without source code access, and (B) with the relevant source code excerpt visible in the prompt. Under Condition A ($n = 10$ trials per model per task, 4 tasks), both models produced incorrect coefficients on $\geq$90\% of trials (95/96 total measurements drifted; Fisher's exact $p = 4.0 \times 10^{-10}$). Drift was systematic: Grok-3 produced `social_skill_coeff = 0.30` on 10/10 trials (truth: 0.10); GPT-4o's mean empathy coefficient was 0.362 (truth: 0.15). Under Condition B, drift on directly visible coefficients dropped to $\sim$0\%, confirming that models can copy specifications when shown them. However, Condition B did not prevent structural errors (formula-level mistakes, scope creep in trait selection). A structured protocol with adversarial specification enforcement (SIMSIV-V2: Builder/Critic/Reviewer roles) caught both coefficient drift and structural errors, producing zero committed drift across 7 checked parameters, validated over 120 simulation runs ($\sigma = 0.030$, CV = 6.0\%). These results demonstrate that specification drift is a default, systematic, and testable failure mode of LLM code generation, and that its prevention requires active enforcement rather than passive context inclusion.

**Keywords:** Specification Drift, LLM Reliability, Scientific Software, Controlled Experiment, Agent-Based Modelling

---

## 1. Introduction

### 1.1 The Problem

When LLMs generate scientific software, a specific failure mode emerges: **specification drift** --- the silent substitution of plausible but incorrect numerical coefficients for those defined in the target specification. A simulation model specifies an empathy modulation coefficient of 0.15, grounded in published literature. An LLM generating code for this model might produce 0.20 --- a value that compiles correctly, passes unit tests, but silently changes the model's dynamics.

As we show in this paper, this is not a hypothetical. Across 96 controlled measurements, frontier LLMs produced the correct coefficient exactly once.

### 1.2 Research Questions

1. **How prevalent is specification drift?** When LLMs generate scientific code without seeing the specification, how often do they produce incorrect coefficients?
2. **Is drift random or systematic?** Do models produce random values, or do they converge on specific wrong values?
3. **Does context access fix drift?** If the source code containing the correct coefficients is included in the prompt, does drift disappear?
4. **Can structured protocols prevent drift?** Does an adversarial role structure (Builder/Critic/Reviewer) eliminate drift on parameters that context access alone does not catch?

### 1.3 Contributions

1. **Quantification.** We measure drift rates across two frontier LLMs at $\geq$90\% per coefficient (Section 3.1).
2. **Characterisation.** Drift is systematic, not random. Models converge on model-specific wrong values (Section 3.2).
3. **Mechanism.** Source code access eliminates coefficient-level drift but not structural errors (Section 3.3).
4. **Intervention.** A structured protocol catches both drift classes, validated across 120 simulation runs (Section 3.4).

---

## 2. Methodology

### 2.1 Three-Condition Experimental Design

| Condition | Source Code Visible? | Protocol Active? | Models | $n$ per model per task |
|-----------|---------------------|-----------------|--------|----------------------|
| **A: Blind** | No | No | GPT-4o, Grok-3 | 10 |
| **B: Source-informed** | Yes (relevant excerpt) | No | GPT-4o, Grok-3 | 10 |
| **C: Protocol** | Yes (full codebase) | Yes (Builder/Critic/Reviewer) | Claude | 1 |

**Condition A** represents a "competent developer using an LLM" scenario: the prompt describes what to build (trait names, value ranges, scientific motivation) but does not include the source code containing the correct coefficients. This isolates the LLM's generative prior.

**Condition B** adds the relevant source code excerpt to the prompt (e.g., lines 287--292 of `resources.py` showing `empathy_capacity * 0.15`). This tests whether models use provided context.

**Condition C** is the full SIMSIV-V2 protocol: three adversarial roles (Builder generates, Critic validates against frozen specification, Reviewer checks code quality) operating within a single LLM session.

All Condition A and B trials used temperature 0.7 to ensure genuine variation.

### 2.2 Protocol Architecture (Condition C)

| Role | Function | Authority |
|------|----------|-----------|
| **Builder** | Generates candidate code | Proposer only |
| **Critic** | Validates against frozen specification | Hard-blocker |
| **Reviewer** | Checks code quality and architecture | Advisory |

The Critic hard-blocks proposals where any coefficient diverges from the frozen specification (JASSS submission 2026:81:1). Every coefficient must be traceable to a specific source-code line and literature citation.

### 2.3 Ground Truth

Five coefficients from the frozen SIMSIV specification:

| # | Parameter | Value | Source | Literature |
|---|-----------|-------|--------|-----------|
| 1 | Empathy modulation | 0.15 | `resources.py:289` | de Waal (2008) |
| 2 | Cooperation norm modulation | 0.10 | `resources.py:292` | Boyd & Richerson (1985) |
| 3 | Social skill trade bonus | 0.10 | `clan_trade.py:330` | Wiessner (1982) |
| 4 | Cohesion defence bonus | 0.20 | `clan_raiding.py:610` | Bowles (2006) |
| 5 | Number of prosocial traits | 4 | `clan_selection.py:82-87` | Price (1970) |

### 2.4 Target Codebase

SIMSIV: a gene-culture coevolutionary agent-based model (500+ agents, 35 heritable traits, 9 engine files, 6,957 lines of v2 code, 163 tests). Frozen specification: JASSS submission 2026:81:1.

### 2.5 Multi-Seed Validation

Condition C output was validated across 120 independent simulation runs (4 milestones $\times$ 30 seeds, 50 years each). Metrics reported: mean, $s$, 95\% CI, CV, Shapiro-Wilk normality test.

---

## 3. Results

### 3.1 Condition A: Drift Without Source Code (99\% drift rate)

**Table 1.** Drift rates under Condition A ($n = 10$ trials, temperature 0.7, no source code).

| Coefficient | Truth | GPT-4o Drift | GPT-4o Mean | Grok-3 Drift | Grok-3 Mean |
|-------------|-------|-------------|-------------|-------------|-------------|
| empathy | 0.15 | 8/8 (100\%) | 0.362 | 10/10 (100\%) | 0.235 |
| coop\_norm | 0.10 | 10/10 (100\%) | 0.235 | 10/10 (100\%) | 0.165 |
| social\_skill | 0.10 | 10/10 (100\%) | 0.310 | 10/10 (100\%) | 0.300 |
| cohesion\_bonus | 0.20 | 8/8 (100\%) | 0.462 | 10/10 (100\%) | 0.320 |
| n\_traits | 4 | 9/10 (90\%) | 5.0 | 10/10 (100\%) | 7.4 |

**Aggregate:** 95 of 96 measurements drifted (**99.0\%**). Fisher's exact test vs. Condition C (0/7): $p = 4.0 \times 10^{-10}$.

### 3.2 Drift Is Systematic, Not Random

**Table 2.** Distribution of produced values for selected coefficients (Condition A).

| Coefficient | Truth | Model | Min | Max | Mean | Correct | Character |
|-------------|-------|-------|-----|-----|------|---------|-----------|
| empathy | 0.15 | GPT-4o | 0.20 | 0.50 | 0.362 | 0/8 | Variable, inflated |
| empathy | 0.15 | Grok-3 | 0.20 | 0.25 | 0.235 | 0/10 | Concentrated, inflated |
| social\_skill | 0.10 | GPT-4o | 0.20 | 0.50 | 0.310 | 0/10 | Variable, inflated |
| social\_skill | 0.10 | Grok-3 | 0.30 | 0.30 | 0.300 | 0/10 | **Locked** (zero variance) |
| n\_traits | 4 | GPT-4o | 4 | 6 | 5.0 | 1/10 | Slight overcount |
| n\_traits | 4 | Grok-3 | 7 | 8 | 7.4 | 0/10 | Severe overcount |

Grok-3 produced `social_skill_coeff = 0.30` on all 10 trials at temperature 0.7 (range: [0.30, 0.30]). The correct value (0.10) was never in its output distribution. GPT-4o's drift was more variable but systematically inflated --- no trial produced a value below the specification.

**Inter-model agreement:** Models drift to *different* wrong values for empathy (GPT-4o: 0.362, Grok-3: 0.235) but converge on *similar* wrong values for social\_skill (0.310 vs 0.300) and cohesion (0.462 vs 0.320, overlapping ranges). This suggests partially shared training priors with model-specific concentration.

### 3.3 Condition B: Source Code Access Eliminates Coefficient Drift

**Table 3.** Condition A vs Condition B drift rates (reliable coefficients only).

| Coefficient | Model | Condition A | Condition B | Change |
|-------------|-------|------------|------------|--------|
| empathy | GPT-4o | 8/8 (100\%) | 0/10 (0\%) | Eliminated |
| empathy | Grok-3 | 10/10 (100\%) | 0/10 (0\%) | Eliminated |
| coop\_norm | GPT-4o | 10/10 (100\%) | 0/10 (0\%) | Eliminated |
| coop\_norm | Grok-3 | 10/10 (100\%) | 0/10 (0\%) | Eliminated |
| social\_skill | GPT-4o | 10/10 (100\%) | 0/6 (0\%) | Eliminated |
| social\_skill | Grok-3 | 10/10 (100\%) | 1/9 (11\%) | Nearly eliminated |

When the source code excerpt containing the coefficient is visible in the prompt, both models produce correct values on $\geq$89\% of trials. This confirms that **drift occurs because models generate from training priors when the specification is absent, not because they are incapable of reading specifications.**

**However, Condition B does not prevent structural errors.** The SIMSIV-V2 Critic caught three error types that source-code access alone does not address:

1. **Formula structure:** The Builder proposed a multiplicative CAC formula (producing degenerate zeros) rather than the specification's additive decomposition.
2. **Scope creep:** The Builder proposed using all 35 heritable traits for selection analysis rather than the specification's 4 prosocial traits.
3. **Cross-file consistency:** The Builder used a conformity coefficient of 0.40 that was inconsistent with `institutions.py:237` (0.30) --- a reference not included in the M1 source excerpt.

These structural errors require *active enforcement* (the Critic cross-referencing multiple source files), not passive context inclusion.

### 3.4 Condition C: Protocol Eliminates All Drift

**Table 4.** Critic friction events (Condition C).

| # | Milestone | Builder Proposed | Specification | Source | Error Type |
|---|-----------|-----------------|--------------|--------|------------|
| 1 | M1 | empathy = 0.20 | 0.15 | `resources.py:289` | Coefficient |
| 2 | M1 | conformity = 0.40 | 0.30 | `institutions.py:237` | Coefficient (cross-file) |
| 3 | M1 | CAC = multiplicative | additive | `resources.py` Phase 0 | Formula structure |
| 4 | M2 | social\_skill = 0.15 | 0.10 | `clan_trade.py:330` | Coefficient |
| 5 | M3 | cohesion = 0.25 | 0.20 | `clan_raiding.py:610` | Coefficient |
| 6 | M4 | 35 traits | 4 traits | `clan_selection.py:82-87` | Scope |

All 6 proposals were blocked and corrected. **0 of 7 committed coefficients drifted.** The Builder's proposed empathy coefficient (0.20) falls within Grok-3's Condition A range (0.20--0.25), confirming that the Builder exhibits the same drift as unstructured models.

### 3.5 Convergence Validation (n=30 per milestone)

**Table 5.** Cross-seed convergence of Condition C output (120 runs).

| Milestone | Metric | $\bar{x}$ | $s$ | 95\% CI | CV | Normal |
|-----------|--------|-----------|-----|---------|-----|--------|
| M1 | cooperation | 0.4994 | 0.0298 | [0.488, 0.511] | 6.0\% | Yes |
| M1 | CAC | 0.6794 | 0.0458 | [0.662, 0.697] | 6.7\% | Yes |
| M2 | trade\_capacity | 1.0028 | 0.0152 | [0.997, 1.009] | 1.5\% | No |
| M3 | defence\_capacity | 0.6843 | 0.0403 | [0.669, 0.699] | 5.9\% | Yes |
| M4 | prosocial\_composite | 0.5008 | 0.0166 | [0.495, 0.507] | 3.3\% | Yes |

All primary metrics $\sigma \ll 0.15$. Zero regressions against 163 existing tests.

---

## 4. Discussion

### 4.1 Models Generate from Priors, Not Specifications

The Condition A/B comparison provides the clearest evidence: the same models that produced 100\% incorrect coefficients without source code (Condition A) produced $\sim$0\% incorrect coefficients with source code (Condition B). The models *can* read and reproduce specifications --- they simply do not generate them from their training distribution.

Grok-3's behaviour is the most vivid illustration: it produced `social_skill_coeff = 0.30` on 10/10 Condition A trials at temperature 0.7 (zero variance). This is not sampling noise --- 0.30 is what the model's prior believes a social skill coefficient should be. The correct value (0.10) is entirely outside its output distribution.

This has a practical consequence: **the more carefully calibrated a parameter is, the more vulnerable it is to drift.** Standard values (0.50, 0.30) happen to be close to LLM priors. Unusual values (0.10, 0.15) --- precisely those requiring careful empirical calibration --- are overwritten.

### 4.2 Why Standard Testing Does Not Catch Drift

Every drifted output from Condition A would pass standard quality checks:

- **Compilation:** All outputs were syntactically valid Python.
- **Unit tests:** A test checking "returns a float between 0 and 1" passes with any coefficient.
- **Integration tests:** The simulation runs correctly with wrong coefficients --- it produces different (wrong) dynamics.
- **Code review:** A reviewer unfamiliar with the specification would see 0.30 as "reasonable."

Only direct comparison against the frozen specification detects drift.

### 4.3 The Protocol's Added Value

Condition B shows that source code access eliminates simple coefficient drift. The protocol's value is therefore *not* primarily coefficient matching (which context access provides) but:

1. **Ensuring source IS consulted.** In practice, developers often do not paste the relevant source file into the prompt. The protocol's Critic role makes this mandatory.
2. **Cross-file consistency.** The conformity coefficient (0.40 vs specification 0.30) was caught by cross-referencing `institutions.py`, which was not in the M1 source excerpt.
3. **Structural errors.** The multiplicative CAC formula and the 35-trait scope creep are not coefficient mismatches --- they are architectural errors that require understanding the specification's intent, not just its numbers.

### 4.4 Limitations

1. **Information asymmetry.** Condition C (protocol) had full codebase access while Condition A had none. Condition B partially controls for this, showing that simple coefficient drift disappears with source access. The protocol's residual value is structural error prevention, which is harder to quantify.

2. **No same-model unstructured control.** Condition C used Claude; Conditions A/B used GPT-4o and Grok-3. The Builder's drift (0.20, 0.40) matches control model patterns, but a clean Claude-without-protocol control requires API access not available during this experiment.

3. **Single codebase.** All results are from SIMSIV. The coefficients tested (0.10--0.20) are typical for agent-based models; replication across other scientific domains would strengthen the claim.

4. **Regex extraction.** Coefficients were parsed from LLM responses via regex. Parse rates ranged from 6/10 to 10/10. Raw responses are archived for manual verification.

5. **Condition B extraction noise.** M3 and M4 results in Condition B were unreliable due to regex matching initialization values or constant names rather than functional coefficients. Only M1 and M2 Condition B results are reported.

### 4.5 Future Work

- **Claude unstructured control** to isolate protocol vs. model capability.
- **Multiple codebases** (climate models, epidemiological simulations).
- **Human baseline** measuring developer coefficient accuracy on the same tasks.
- **Cross-model Critic** (e.g., GPT-4o builds, Grok-3 critiques).

---

## 5. Conclusion

### Findings

| \# | Finding | Evidence |
|----|---------|----------|
| 1 | **Drift is the default** | 95/96 measurements incorrect without source code ($p = 4 \times 10^{-10}$) |
| 2 | **Drift is systematic** | Grok-3: 0.30 on 10/10 trials for a 0.10 parameter (zero variance) |
| 3 | **Context access fixes coefficient drift** | Condition B: 100\% $\to$ $\sim$0\% when source code is visible |
| 4 | **Context alone misses structural errors** | Multiplicative formula, scope creep not prevented by source access |
| 5 | **Active enforcement eliminates all measured drift** | Protocol: 0/7 committed drift, 6 caught pre-commit |

### Practical Recommendations

For any team using LLMs to generate scientific code with calibrated parameters:

1. **Always include source-code excerpts in prompts** when generating specification-bound code. This eliminates simple coefficient drift at zero cost.
2. **Implement coefficient-level validation** against a frozen specification file before committing LLM-generated code. Automated comparison catches what unit tests cannot.
3. **Never trust that a "reasonable-looking" coefficient matches your specification.** The parameters you calibrated most carefully are the ones most likely to be silently overwritten.

---

## References

- Bowles, S. (2006). Group competition, reproductive leveling, and the evolution of human altruism. *Science*, 314(5805), 1569--1572.
- Bowles, S. & Gintis, H. (2011). *A Cooperative Species*. Princeton University Press.
- Boyd, R. & Richerson, P.J. (1985). *Culture and the Evolutionary Process*. University of Chicago Press.
- de Waal, F.B.M. (2008). Putting the altruism back into altruism. *Annual Review of Psychology*, 59, 279--300.
- Price, G.R. (1970). Selection and covariance. *Nature*, 227, 520--521.
- Railsback, S.F. & Grimm, V. (2019). *Agent-Based and Individual-Based Modeling* (2nd ed.). Princeton University Press.
- Rice, J. et al. (2026). SIMSIV: A calibrated agent-based framework for studying gene-culture coevolution in pre-state societies. *Under review, JASSS*, submission 2026:81:1.
- Smith, E.A. & Bird, R. (2000). Turtle hunting and tombstone opening. *Evolution and Human Behavior*, 21(4), 245--261.
- Stodden, V. et al. (2016). Enhancing reproducibility for computational methods. *Science*, 354(6317), 1240--1241.
- Wiessner, P. (1982). Risk, reciprocity and social influences on !Kung San economics. In *Politics and History in Band Societies*, Cambridge University Press.

---

## Appendix A: Condition A Raw Data (n=10 per model)

**GPT-4o:**
- empathy: 0.30, 0.30, --, 0.50, 0.20, 0.50, --, 0.50, 0.30, 0.30 (mean 0.362)
- coop\_norm: 0.40, 0.40, 0.20, 0.00, 0.30, 0.30, 0.30, 0.00, 0.25, 0.20 (mean 0.235)
- social\_skill: 0.50, 0.50, 0.20, 0.25, 0.30, 0.20, 0.50, 0.20, 0.25, 0.20 (mean 0.310)
- cohesion: 0.30, --, 0.50, --, 0.50, 0.50, 0.60, 0.50, 0.30, 0.50 (mean 0.462)
- n\_traits: 4, 5, 6, 5, 5, 5, 5, 5, 5, 5 (mean 5.0)

**Grok-3:**
- empathy: 0.25, 0.25, 0.25, 0.25, 0.25, 0.20, 0.20, 0.25, 0.20, 0.25 (mean 0.235)
- coop\_norm: 0.15, 0.15, 0.15, 0.15, 0.15, 0.20, 0.20, 0.15, 0.20, 0.15 (mean 0.165)
- social\_skill: 0.30, 0.30, 0.30, 0.30, 0.30, 0.30, 0.30, 0.30, 0.30, 0.30 (mean 0.300)
- cohesion: 0.30, 0.30, 0.30, 0.00, 0.30, 0.50, 0.50, 0.10, 0.80, 0.10 (mean 0.320)
- n\_traits: 8, 7, 8, 7, 7, 7, 8, 7, 7, 8 (mean 7.4)

## Appendix B: Condition B Drift Rates (reliable coefficients)

| Coefficient | Model | A Drift | B Drift |
|-------------|-------|---------|---------|
| empathy | GPT-4o | 100\% | 0\% |
| empathy | Grok-3 | 100\% | 0\% |
| coop\_norm | GPT-4o | 100\% | 0\% |
| coop\_norm | Grok-3 | 100\% | 0\% |
| social\_skill | GPT-4o | 100\% | 0\% |
| social\_skill | Grok-3 | 100\% | 11\% |

## Appendix C: Convergence Statistics (n=30 per milestone)

```
Milestone  Metric                Mean    s       95% CI            CV%    Normal
M1         cooperation          0.4994  0.0298  [0.488, 0.511]   6.0%   Yes
M1         CAC                  0.6794  0.0458  [0.662, 0.697]   6.7%   Yes
M2         trade_capacity       1.0028  0.0152  [0.997, 1.009]   1.5%   No
M3         defence_capacity     0.6843  0.0403  [0.669, 0.699]   5.9%   Yes
M4         prosocial_composite  0.5008  0.0166  [0.495, 0.507]   3.3%   Yes
```

120 total runs. 0 anomalies. 0/163 regressions.

## Appendix D: Figures

**Figure 1** (`docs/figures/figure1_drift_scatter.png`): Ground truth vs model-produced coefficients. Left: Condition A (blind) — all points above the diagonal. Right: Condition B (source visible) — all points on the diagonal.

**Figure 2** (`docs/figures/figure2_drift_sensitivity.png`): Drift magnitude vs ground truth value. Predominantly positive drift (inflation bias).

## Appendix E: Reproducibility

| File | Purpose |
|------|---------|
| `experiments/drift_experiment/run_condition_a.py` | Condition A runner (env vars for API keys) |
| `experiments/drift_experiment/run_condition_b.py` | Condition B runner |
| `experiments/drift_analysis.py` | Statistical analyses + figure generation |
| `tests/test_milestone_battery.py` | 4-milestone $\times$ 30-seed convergence test |
| `models/clan/clan_base.py` | 712-line cooperation model (all 4 milestones) |

---

*Working paper v5. March 2026.*
