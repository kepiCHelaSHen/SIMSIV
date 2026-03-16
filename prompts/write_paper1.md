# SIMSIV — Paper 1 Draft Generator
# Executable Chain Prompt for Claude Code CLI
# Run: claude --dangerously-skip-permissions < prompts\write_paper1.md
# Output: docs/paper1_draft.md (Markdown) + docs/paper1_draft.pdf (if pandoc available)
# Target journal: JASSS (Journal of Artificial Societies and Social Simulation)
# Estimated run time: 15-20 minutes

================================================================================
INSTRUCTIONS FOR CLAUDE CODE
================================================================================

You are writing a complete first draft of a peer-reviewed academic paper
describing the SIMSIV band-level simulator. Read every source file listed
below BEFORE writing a single word of the paper. The paper must be grounded
entirely in the actual data and documented findings — no fabrication, no
rounding up of results, no overclaiming.

READ THESE FILES IN FULL BEFORE WRITING:

  D:\EXPERIMENTS\SIM\docs\validation.md
  D:\EXPERIMENTS\SIM\docs\world_architecture.md
  D:\EXPERIMENTS\SIM\docs\AI_COLLABORATOR_BRIEF.md
  D:\EXPERIMENTS\SIM\docs\sensitivity_analysis.md
  D:\EXPERIMENTS\SIM\autosim\best_config.yaml
  D:\EXPERIMENTS\SIM\autosim\targets.yaml
  D:\EXPERIMENTS\SIM\experiments\scenarios.py
  D:\EXPERIMENTS\SIM\config.py

THEN READ ALL EXPERIMENT OUTPUT FILES:
  D:\EXPERIMENTS\SIM\outputs\experiments\

  Read every comparison.csv and full_report.json you find in every
  subdirectory under outputs/experiments/. List what you find before writing.
  Use the actual numbers — do not estimate or round.

THEN WRITE THE PAPER as described below.

================================================================================
PAPER SPECIFICATION
================================================================================

Title:
  "SIMSIV: A Calibrated Agent-Based Framework for Studying Gene-Culture
   Coevolution in Pre-State Societies"

Target journal: JASSS — Journal of Artificial Societies and Social Simulation
Format: Academic paper, ~6,000-8,000 words, Markdown output
Citation style: Author-year (APA)

Author line:
  Independent Researcher

AI disclosure (place at end of Methods section):
  "Simulation code development was assisted by Claude (Anthropic, version
   claude-sonnet-4-6). All scientific decisions, hypotheses, experimental
   designs, calibration targets, and interpretations of results are the
   author's own."

================================================================================
PAPER STRUCTURE — WRITE EVERY SECTION
================================================================================

--- ABSTRACT (~250 words) ---

Write a structured abstract with these components:
  Background: The gene-culture coevolution debate (Camp A vs Camp B)
  Objective: What SIMSIV is designed to test
  Methods: ABM, 35 traits, 9 engines, simulated annealing calibration
  Results: Key findings — report actual numbers from experiment outputs
  Conclusions: What the results mean for the substitution hypothesis

The abstract's final sentence must be the falsifiable claim:
  "We find that institutional governance reduces directional selection on
   heritable prosocial behavioral traits, providing computational evidence
   that institutions and genes act as partial substitutes in human social
   evolution."

Only use this sentence if the 500yr experiment data supports it.
If cooperation divergence is not clearly present in the data, write a
more cautious conclusion and flag this explicitly in a [NOTE] to the author.

--- 1. INTRODUCTION (~800 words) ---

Structure:
  1.1 The gene-culture coevolution debate
    - State the Camp A vs Camp B positions clearly
    - Bowles & Gintis (2011): co-evolution upward, group selection
    - North (1990): institutions substitute for internal motivation
    - Waring & Wood (2021): culture can bypass genetic adaptation
    - Why this debate is unresolved: lack of controlled experimental tests

  1.2 Agent-based models as adjudication tools
    - Why ABMs are appropriate for this question
    - Brief review of existing ABMs in this space (Axelrod, Epstein & Axtell,
      Bowles 2006 group selection model)
    - What SIMSIV adds that existing models lack: full biological individuality,
      35 heritable traits with empirical h² values, developmental plasticity,
      multi-subsystem calibrated against ethnographic benchmarks

  1.3 This paper's contribution
    - State the three contributions clearly:
      1. A calibrated, validated ABM platform for gene-culture coevolution
      2. Sensitivity analysis showing cooperation is a robust emergent attractor
      3. Scenario experiments testing the institutional substitution hypothesis

  1.4 Paper structure overview (one paragraph)

--- 2. MODEL DESCRIPTION (~1,500 words) ---

Follow the ODD protocol (Overview, Design concepts, Details) — this is
standard for ABM papers and reviewers at JASSS expect it.

  2.1 Overview
    - Purpose: test gene-culture coevolution hypotheses
    - Entities: agents (full biological individuals), society, environment
    - Scale: 50-500 agents, annual tick, 200-500 year runs
    - Process overview: 9-engine annual tick (list all 9 in order)

  2.2 Design Concepts
    - Emergence: list what emerges (factions, institutions, trait evolution)
      and confirm none of it is scripted
    - Adaptation: agents don't optimize — they follow probabilistic rules
      based on traits and state
    - Fitness: implicit — reproductive success drives trait evolution
      through h²-weighted inheritance
    - Interaction: agents interact through trust networks, conflict,
      mating, and resource competition
    - Stochasticity: all processes probabilistic, seeded RNG for reproducibility
    - Observation: ~130 metrics per tick including all trait means

  2.3 Agent Details
    - The 35 heritable traits: list all, organized by domain
    - Heritability model: child_val = h² × parent_midpoint + (1-h²) × pop_mean + mutation
    - Genotype/phenotype separation: developmental plasticity at age 15
    - 35×35 correlation matrix: PSD-verified, 100+ empirically grounded correlations
    - Cultural beliefs (5 dimensions) and skills (4 domains): non-heritable
    - Life stages: CHILDHOOD / YOUTH / PRIME / MATURE / ELDER

  2.4 Engine Details
    Describe each engine briefly (2-3 sentences each):
      Environment, Resources (8-phase), Conflict (cross-sex enabled),
      Mating (EPC, female choice, symmetric dissolution),
      Reproduction (h²-weighted, developmental plasticity),
      Mortality (sex-differential), Migration, Pathology, Institutions
      (drift ENABLED by default), Reputation (gossip, BFS factions)

  2.5 Scenarios
    Table: all 11 scenarios with key overrides and scientific purpose
    Note the distinction between FREE_COMPETITION (weak endogenous governance)
    and NO_INSTITUTIONS (true zero-governance null) — explain why both are needed

--- 3. CALIBRATION AND VALIDATION (~1,000 words) ---

  3.1 Calibration targets
    Table: all 9 targets with empirical range, source citation, and rationale
    Be explicit about the weighting (violence_death_fraction weight=2.0, etc.)

  3.2 AutoSIM calibration methodology
    - Simulated annealing algorithm: temperature schedule, perturbation
    - 816 experiments, ~10.5 hours, Run 3 (post-Phase F bug fixes)
    - Why Run 3 supersedes Runs 1 and 2: 19 model fixes changed dynamics
    - Best score: 1.000

  3.3 Calibrated parameter values
    Table: key calibrated parameters vs defaults, noting dramatic reversals
    (female_choice_strength 0.88→0.34, subsistence_floor 0.30→1.17)
    Interpret the reversals as evidence the fixes were scientifically material

  3.4 Held-out validation
    - Design: 10 seeds × 200yr × 500pop × 2 independent runs
    - Seeds not used in calibration training
    - Results table: all 9 metrics, mean, std, in-range count
    - Verdict: MOSTLY ROBUST, 0/20 collapses, mean score 0.934

  3.5 Known limitations of calibration
    - Violence death fraction fragility: intra-band only, no inter-group raiding
    - Lifetime births near floor: structural constraint on bonded fraction
    - Bond dissolution near floor: calibrated to minimum

--- 4. SENSITIVITY ANALYSIS (~600 words) ---

  4.1 Method
    Pearson r across 816 calibration experiments
    Note limitation: linear correlations, nonlinear interactions require Sobol

  4.2 Results
    Table: top 3-5 drivers per metric with r values
    Pull directly from docs/sensitivity_analysis.md — use exact numbers

  4.3 Key finding: cooperation is weakly driven
    Report: max |r| for avg_cooperation = 0.199
    Interpret: cooperation is a robust emergent attractor, not parameter-forced
    This is a direct answer to the reviewer concern "did you hard-code cooperation"

  4.4 Other notable sensitivities
    - resource_equal_floor dominates Gini (r=-0.885): redistribution norm
    - pair_bond_dissolution_rate dominates bond dissolution (r=+0.936)
    - mortality_base drives both cooperation (down) and aggression (up):
      life history theory prediction confirmed

--- 5. SCENARIO EXPERIMENTS (~1,500 words) ---

  5.1 Experimental design
    - Baseline: best_config.yaml calibrated parameters
    - 10 seeds per scenario (seed pool: 1001-9009, 1337)
    - 200yr runs: all 11 scenarios
    - 500yr runs: governance spectrum + mating systems + resource ecology
    - Statistical comparison: means across seeds, report ranges

  5.2 The governance spectrum (primary finding)
    Three-way comparison: NO_INSTITUTIONS vs FREE_COMPETITION vs STRONG_STATE

    Table with these columns for 200yr AND 500yr:
      Scenario | Coop trait | Aggression | Violence | Gini | Law strength

    Report the cooperation divergence at 500yr explicitly:
      FREE_COMPETITION: [number from data]
      NO_INSTITUTIONS:  [number from data]
      STRONG_STATE:     [number from data]

    Interpret: cooperation trait rose in FREE_COMPETITION, stayed flat in
    STRONG_STATE. This is the substitution finding. State it clearly.
    Be appropriately cautious about effect size.

    If Mann-Whitney U p-values are available from the data, report them.
    If not, note that formal statistical testing is ongoing and report
    the means and cross-seed distributions.

  5.3 Mating system effects
    Table: FREE_COMPETITION vs ENFORCED_MONOGAMY vs ELITE_POLYGYNY
      at both 200yr and 500yr

    Key findings to report with actual numbers:
      - Monogamy violence reduction (% change)
      - Monogamy unmated males reduction (% change)
      - Elite polygyny demographic paradox (lifespan vs pop growth)
      - Whether monogamy cooperation at 500yr is higher or lower than baseline
        (tests whether monogamy also substitutes for cooperation like STRONG_STATE)

  5.4 Resource ecology effects
    Table: FREE_COMPETITION vs RESOURCE_SCARCITY vs RESOURCE_ABUNDANCE
      at 200yr and 500yr

    Key findings:
      - Scarcity cooperation at 200yr (higher than baseline — stress effect)
      - Scarcity cooperation at 500yr (what happened? does it hold or reverse?)
      - Population collapse under scarcity (report final populations)
      - Abundance effect on cooperation and inequality

  5.5 Additional findings from 200yr full run
    Briefly report EMERGENT_INSTITUTIONS law self-organization result
    Report HIGH_FEMALE_CHOICE effect on cooperation trait
    Report STRONG_PAIR_BONDING violence and Gini effects

--- 6. DISCUSSION (~900 words) ---

  6.1 The substitution finding in theoretical context
    - Connect to Camp A vs Camp B debate explicitly
    - Interpret: behavioral effects are immediate, genetic effects take centuries
    - This means institutions are "fast-moving cultural regulators" and
      trait evolution is "slow-moving genetic selection" — quote Waring & Wood
    - The finding is consistent with North's substitution thesis but does not
      confirm the strong version: governance raises behavior WITHOUT raising
      the underlying cooperation gene

  6.2 The cooperation attractor finding
    - Cooperation stabilizes near 0.51 regardless of parameters
    - Multiple fitness channels sustain it: resource sharing, reputation,
      faction protection, coalition defense
    - This is the "ecological baseline" of cooperation in band societies
    - Institutions don't push it above the attractor — they just do the
      behavioral work without it

  6.3 Mating systems and social order
    - Monogamy violence reduction: consistent with Henrich et al. (2012)
    - Unmated male reduction: consistent with Scheidel (2017) on violence
    - Note: monogamy also has high law_strength override, so effect is
      partially institutional, partially mating-structural — discuss

  6.4 Stress-induced cooperation
    - Scarcity produces highest cooperation at 200yr
    - Reversal at 500yr due to population collapse: drift dominates selection
      at very small N
    - Implication: stress-cooperation is a short-run phenomenon dependent
      on population viability

  6.5 Limitations
    Must include these (do not soften):
    L1: Single-band model — no inter-group competition. Cannot distinguish
        group selection from within-group mechanisms. v2 addresses this.
    L2: No spatial structure
    L3: Annual time step
    L4: Quantitative genetics approximation (no loci, no LD)
    L5: Modern h² values applied to pre-industrial populations
    L6: Calibration target uncertainty (violence data includes inter-group)

--- 7. CONCLUSIONS (~300 words) ---

  Three paragraphs:
  1. What was built: calibrated ABM, 35 traits, 9 engines, score 1.000
  2. What was found: cooperation is an emergent attractor, institutions
     substitute for genetic prosociality in the short run, behavioral
     effects precede genetic effects by centuries
  3. What comes next: clan simulator (v2), group selection test, longer runs

--- REFERENCES ---

Include ALL of these — pull exact citations from docs/validation.md Section 8
and docs/validation_literature_addendum.md:

Required citations:
  Archer (2009), Bentley (1996), Betzig (1989, 2012),
  Biraben (1980), Borgerhoff Mulder et al. (2009),
  Bowles (2006), Bowles & Gintis (2011),
  Choi & Bowles (2007),
  Fehr & Gächter (2002), Fry (2006),
  Greif (2006), Hassan (1981),
  Henrich & Boyd (1998), Henrich et al. (2012),
  Hill & Hurtado (1996), Howell (1979),
  Keeley (1996), Marlowe (2010),
  North (1990), Ostrom (1990),
  Smith (2016), Tabellini (2008),
  Volk & Atkinson (2013), Walker (2001),
  Waring & Wood (2021)

Format: APA author-year

================================================================================
OUTPUT INSTRUCTIONS
================================================================================

Write the complete paper to:
  D:\EXPERIMENTS\SIM\docs\paper1_draft.md

Use proper Markdown:
  # for paper title
  ## for section numbers (1. Introduction, etc.)
  ### for subsections
  Tables using | pipe | format
  Bold for key findings
  Italics for emphasis

After writing the Markdown, attempt to convert to PDF:
  pip install pandoc --break-system-packages (if not installed)
  pandoc docs/paper1_draft.md -o docs/paper1_draft.pdf --pdf-engine=xelatex

If pandoc fails, note it and provide the Markdown only.
The Markdown is sufficient for review purposes.

Then write a SHORT cover file at:
  D:\EXPERIMENTS\SIM\docs\paper1_submission_notes.md

Containing:
  - Target journal: JASSS
  - Suggested reviewers (3 names from the cited literature)
  - Cover letter text (3 paragraphs: what the paper does, why JASSS,
    what the key contribution is)
  - arXiv category: cs.MA (Multi-Agent Systems) + q-bio.PE (Populations and Evolution)

================================================================================
QUALITY CHECKS BEFORE FINISHING
================================================================================

Before saving, verify:
  [ ] Every number cited in the paper matches the actual experiment output files
  [ ] No metric is described as "significantly" different without statistical support
      (if no p-values computed, say "mean difference of X across 10 seeds")
  [ ] Limitations section is honest and complete — do not soften L1
  [ ] The substitution finding is stated at appropriate confidence level
      (preliminary if effect is small, strong if divergence is large and consistent)
  [ ] AI disclosure is present in Methods section
  [ ] All 25+ required references are included
  [ ] Abstract is ≤250 words
  [ ] Total word count is between 6,000-8,000 words

================================================================================
END OF PAPER GENERATION PROMPT
================================================================================
