# SIMSIV — Paper 1 Revision Prompt
# Executable Chain Prompt for Claude Code CLI
# Run: claude --dangerously-skip-permissions < prompts\revise_paper1.md
# Revises docs/paper1_draft.md based on GPT + Grok pre-submission review
# Also generates figures as PNG files in docs/figures/
# Estimated run time: 20-30 minutes

================================================================================
INSTRUCTIONS FOR CLAUDE CODE
================================================================================

You are revising the SIMSIV Paper 1 draft based on pre-submission peer review
from two AI reviewers (GPT and Grok). Their consensus flagged six issues.
Fix all six. Then generate three publication figures.

READ THESE FILES BEFORE MAKING ANY CHANGES:

  D:\EXPERIMENTS\SIM\docs\paper1_draft.md           ← the paper to revise
  D:\EXPERIMENTS\SIM\outputs\experiments\20260315_194150_NO_INSTITUTIONS_FREE_COMPETITION_STRONG_STATE_s10_y500\comparison.csv
  D:\EXPERIMENTS\SIM\outputs\experiments\20260315_193618_FREE_COMPETITION_STRONG_STATE_EMERGENT_INSTITUTIONS_s10_y500\comparison.csv
  D:\EXPERIMENTS\SIM\outputs\experiments\20260315_195313_all_scenarios_s10_y200\comparison.csv
  D:\EXPERIMENTS\SIM\autosim\best_config.yaml
  D:\EXPERIMENTS\SIM\autosim\targets.yaml

Do NOT change any finding, any number, any table, or any calibration result
unless explicitly instructed below. This is a targeted revision, not a rewrite.

================================================================================
REVISION 1 — SOFTEN SUBSTITUTION CLAIM LANGUAGE (3 locations)
================================================================================

Find and replace these exact phrases throughout the paper:

  FIND:    "provide computational evidence that institutions substitute for,
            rather than complement, heritable prosocial traits"
  REPLACE: "are consistent with the institutional-substitution hypothesis,
            suggesting that institutions may substitute for, rather than
            complement, heritable prosocial traits"

  FIND:    "These findings provide computational evidence that institutions
            substitute for, rather than complement, heritable prosocial traits
            at band-level timescales"
  REPLACE: "These findings are consistent with the institutional-substitution
            hypothesis: institutions appear to substitute for heritable prosocial
            traits in producing cooperative behavioral outcomes at band-level
            timescales, though longer time horizons and multi-group dynamics
            may reveal complementarity"

  FIND (in Conclusions, point 1):
    "This provides computational evidence for the institutional-substitution
     hypothesis at band-level timescales."
  REPLACE:
    "This is consistent with the institutional-substitution hypothesis at
     band-level timescales, though we caution that 500 years (~20 generations)
     may be insufficient to detect weak selection gradients."

================================================================================
REVISION 2 — ADD BOYD & RICHERSON DUAL INHERITANCE CITATION
================================================================================

In Section 1.1, find the paragraph that ends with:
  "The debate therefore remains largely theoretical."

AFTER that paragraph, add this new paragraph:

  "The dual inheritance theory of Boyd and Richerson (1985) provides the
   foundational framework for understanding how genetic and cultural evolution
   interact. Under dual inheritance, cultural transmission constitutes a second
   inheritance system that can evolve independently of, or in interaction with,
   genetic inheritance. Crucially, dual inheritance theory neither predicts
   complementarity nor substitution a priori: the outcome depends on whether
   cultural variants that emerge under institutions increase or decrease the
   fitness gradient on prosocial genes. SIMSIV operationalizes this by
   separating heritable trait values (the genetic channel) from behavioral
   outcomes and belief transmission (the cultural channel), allowing both to
   evolve simultaneously."

Add to the References section (in alphabetical order by author):

  Boyd, R., & Richerson, P. J. (1985). *Culture and the evolutionary process*.
    University of Chicago Press.

================================================================================
REVISION 3 — ADD STANDARD DEVIATIONS TO SCENARIO TABLES
================================================================================

In Section 5.2, find the 500-year results table:

  | Metric | NO_INSTITUTIONS | FREE_COMPETITION | STRONG_STATE |
  |---|---|---|---|
  | Cooperation | 0.523 | 0.524 | 0.523 |
  | Aggression | 0.448 | 0.452 | 0.478 |
  | Intelligence | 0.632 | 0.644 | 0.596 |
  | Law strength | 0.000 | 0.928 | 1.000 |
  | Final population | 569 | 623 | 536 |

REPLACE with (pull exact SDs from the CSV files read above):

  | Metric | NO_INSTITUTIONS | FREE_COMPETITION | STRONG_STATE |
  |---|---|---|---|
  | Cooperation | 0.523 ± 0.024 | 0.524 ± 0.020 | 0.523 ± 0.028 |
  | Aggression | 0.448 ± 0.029 | 0.452 ± 0.020 | 0.478 ± 0.019 |
  | Intelligence | 0.632 ± 0.020 | 0.644 ± 0.019 | 0.596 ± 0.023 |
  | Law strength | 0.000 ± 0.000 | 0.928 ± 0.043 | 1.000 ± 0.000 |
  | Final population | 569 ± 259 | 623 ± 300 | 536 ± 231 |

VERIFY each SD value against the CSV before writing.
The columns in the CSV are: avg_cooperation_std, avg_aggression_std,
avg_intelligence_std, law_strength_std, final_population_std.

Also add SDs to the 200-year table in Section 5.2. Pull values from the
all_scenarios_s10_y200 comparison.csv for the three governance scenarios.

================================================================================
REVISION 4 — EXPAND COOPERATION ATTRACTOR SECTION
================================================================================

In Section 5.5, find the paragraph beginning:
  "The cooperation attractor. Across all scenarios and time horizons..."

REPLACE the entire paragraph with these two paragraphs:

  "**The cooperation attractor.** Across all scenarios and time horizons,
   heritable cooperation propensity converges to a narrow band of approximately
   0.51--0.53 (with the exception of the population-collapse scenario at 0.489
   and the high-female-choice scenario at 0.549). This stability is not a
   ceiling or floor effect: cooperation starts at 0.5 by initialization and
   has full range [0.0, 1.0] to diverge. It is not a parameter artifact:
   sensitivity analysis confirms that no single parameter strongly drives
   cooperation (max |r| = 0.199). And it is not a consequence of weak selection:
   the model clearly selects on cooperation through resource sharing, reputation,
   coalition protection, and reduced conflict targeting. Rather, the attractor
   reflects an evolutionary balance between cooperation's multi-channel fitness
   benefits and its costs: cooperators who share too freely are exploited by
   defectors; defectors who cooperate too little lose network benefits and
   reputation.

   This finding is theoretically significant for two reasons. First, it suggests
   that band-level societies may exhibit a universal cooperation equilibrium that
   is robust to both ecological conditions (scarcity and abundance produce similar
   cooperation levels) and institutional conditions (all governance regimes
   converge near the same value). The principal exceptions --- high female choice
   (0.549) and population collapse under scarcity (0.489) --- reveal the two
   mechanisms that can escape the attractor: sexual selection directly rewarding
   cooperative genotypes, and demographic collapse disrupting selection entirely.
   Second, if this attractor is real rather than a model artifact, it predicts
   that cross-cultural variation in cooperation norms should be driven primarily
   by cultural transmission and institutional enforcement rather than by heritable
   trait variation --- a prediction that is testable with comparative behavioral
   genetics data across small-scale societies."

================================================================================
REVISION 5 — ADD FORWARD-LOOKING V2 SENTENCE IN CONCLUSIONS
================================================================================

Find the final sentence of the paper before the references:
  "The model code, calibration data, and scenario configurations are available
   at https://github.com/kepiCHelaSHen/SIMSIV"

BEFORE that sentence, add:

  "We invite independent replications, parameter explorations, and theoretical
   extensions using the open repository. The model is designed as a platform:
   the scenario system, calibration pipeline, and experimental runner can support
   research questions beyond those addressed here."

================================================================================
REVISION 6 — ADD FIGURE REFERENCES IN TEXT
================================================================================

In Section 2.1, after the process overview numbered list, add:

  "Figure 1 illustrates the annual tick execution order."

In Section 3.3, after the calibrated performance table, add:

  "Figure 2 shows the calibrated values relative to their target ranges."

In Section 5.2, after the 500-year results table, add:

  "Figure 3 plots mean cooperation propensity across all 500 simulated years
   for the three governance scenarios, confirming the absence of divergence
   at all time points, not just the final year."

================================================================================
GENERATE FIGURE 1 — ANNUAL TICK ARCHITECTURE DIAGRAM
================================================================================

Create D:\EXPERIMENTS\SIM\docs\figures\fig1_tick_architecture.py

This Python script generates a clean flowchart of the 9-engine annual tick.
Run it to produce fig1_tick_architecture.png.

```python
"""Figure 1: SIMSIV Annual Tick Architecture."""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch

fig, ax = plt.subplots(figsize=(7, 10))
ax.set_xlim(0, 10)
ax.set_ylim(0, 12)
ax.axis('off')

engines = [
    ("1. Environment",    "Seasonal cycles, scarcity shocks, epidemics",      "#4A90D9"),
    ("2. Resources",      "8-phase acquisition across 3 resource types",       "#5BA85B"),
    ("3. Conflict",       "Violence, deterrence, coalition defense",            "#D94A4A"),
    ("4. Mating",         "Female choice, pair bonding, EPC",                  "#D97A4A"),
    ("5. Reproduction",   "h²-weighted inheritance, developmental plasticity", "#A84AB8"),
    ("6. Mortality",      "Aging, sex-differential death, epidemics",          "#8B6914"),
    ("7. Migration",      "Emigration push, immigration pull",                 "#2A9D8F"),
    ("8. Pathology",      "Conditions, trauma, epigenetic stress",             "#E76F51"),
    ("9. Institutions",   "Drift, norm enforcement, inheritance",              "#264653"),
]

box_h = 0.85
gap   = 0.15
start = 11.2

for i, (title, subtitle, color) in enumerate(engines):
    y = start - i * (box_h + gap)
    rect = mpatches.FancyBboxPatch(
        (0.5, y - box_h), 9, box_h,
        boxstyle="round,pad=0.05",
        facecolor=color, edgecolor='white', linewidth=1.5, alpha=0.92
    )
    ax.add_patch(rect)
    ax.text(5, y - box_h/2 + 0.18, title,
            ha='center', va='center', fontsize=10,
            fontweight='bold', color='white')
    ax.text(5, y - box_h/2 - 0.18, subtitle,
            ha='center', va='center', fontsize=7.5,
            color='white', alpha=0.9)
    if i < len(engines) - 1:
        arrow_y = y - box_h - 0.02
        ax.annotate("", xy=(5, arrow_y - gap + 0.05),
                    xytext=(5, arrow_y),
                    arrowprops=dict(arrowstyle="->", color="#cccccc",
                                   lw=1.5))

ax.text(5, 11.7, "SIMSIV — Annual Simulation Tick",
        ha='center', va='center', fontsize=12, fontweight='bold', color='#333333')
ax.text(5, 0.25, "↑ Metrics collected after all engines complete → next year",
        ha='center', va='center', fontsize=8, color='#666666', style='italic')

plt.tight_layout()
plt.savefig("docs/figures/fig1_tick_architecture.png",
            dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print("Figure 1 saved.")
```

================================================================================
GENERATE FIGURE 2 — CALIBRATION TARGETS VS ACHIEVED VALUES
================================================================================

Create D:\EXPERIMENTS\SIM\docs\figures\fig2_calibration.py

```python
"""Figure 2: Calibration targets vs achieved values."""
import matplotlib.pyplot as plt
import numpy as np

metrics = [
    "Resource\nGini",
    "Mating\nInequality",
    "Violence\nDeath Frac",
    "Pop Growth\nRate",
    "Child\nSurvival",
    "Lifetime\nBirths",
    "Bond\nDissolution",
    "Mean\nCooperation",
    "Mean\nAggression",
]

# Target ranges [low, high]
targets = [
    (0.30, 0.50),
    (0.40, 0.70),
    (0.05, 0.15),
    (0.001, 0.015),
    (0.50, 0.70),
    (4.0,  7.0),
    (0.10, 0.30),
    (0.25, 0.70),
    (0.30, 0.60),
]

# Calibrated values (from best_config.yaml autosim_key_metrics)
achieved = [0.310, 0.578, 0.069, 0.0137, 0.642, 4.21, 0.118, 0.507, 0.494]

# Normalize each to [0,1] within its target range for display
fig, axes = plt.subplots(1, 9, figsize=(14, 4))
fig.suptitle("Figure 2: Calibrated Values vs. Anthropological Target Ranges",
             fontsize=11, fontweight='bold', y=1.02)

colors_in  = "#4CAF50"
colors_out = "#F44336"

for i, (ax, metric, (lo, hi), val) in enumerate(
        zip(axes, metrics, targets, achieved)):
    in_range = lo <= val <= hi
    color = colors_in if in_range else colors_out

    # Draw target range as background
    ax.barh(0, hi - lo, left=lo, height=0.5,
            color='#E8E8E8', edgecolor='#AAAAAA', linewidth=0.8)
    # Draw achieved value
    ax.barh(0, 0.001, left=val, height=0.5, color=color, linewidth=0)
    ax.axvline(val, color=color, linewidth=2.5)

    ax.set_xlim(lo - (hi-lo)*0.3, hi + (hi-lo)*0.3)
    ax.set_ylim(-0.5, 0.8)
    ax.set_xlabel(f"{val:.3f}", fontsize=8, labelpad=2)
    ax.set_title(metric, fontsize=7.5, pad=3)
    ax.set_yticks([])
    ax.tick_params(axis='x', labelsize=7)
    ax.spines[['top','left','right']].set_visible(False)

    status = "✓" if in_range else "✗"
    ax.text(0.5, 0.75, status, transform=ax.transAxes,
            ha='center', fontsize=12, color=color)

plt.tight_layout()
plt.savefig("docs/figures/fig2_calibration.png",
            dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print("Figure 2 saved.")
```

================================================================================
GENERATE FIGURE 3 — COOPERATION TRAJECTORY OVER 500 YEARS
================================================================================

Create D:\EXPERIMENTS\SIM\docs\figures\fig3_cooperation_trajectory.py

This script reads the per-seed metrics CSV files to get year-by-year
cooperation data for the three governance scenarios.

```python
"""Figure 3: Cooperation trajectory 0-500yr across governance regimes."""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path("outputs/experiments")

# Locate the three scenario directories from Batch 2
# (NO_INSTITUTIONS_FREE_COMPETITION_STRONG_STATE_s10_y500)
batch2 = next(ROOT.glob("*NO_INSTITUTIONS_FREE_COMPETITION_STRONG_STATE*"))

scenarios = {
    "NO_INSTITUTIONS":  {"color": "#E53935", "label": "No Institutions (law=0)"},
    "FREE_COMPETITION": {"color": "#FB8C00", "label": "Free Competition (endogenous governance)"},
    "STRONG_STATE":     {"color": "#1E88E5", "label": "Strong State (law=0.8)"},
}

fig, ax = plt.subplots(figsize=(10, 5))

for scenario, props in scenarios.items():
    path = batch2 / scenario / "per_seed.json"
    if not path.exists():
        print(f"WARNING: {path} not found — skipping")
        continue

    import json
    with open(path) as f:
        per_seed = json.load(f)

    # per_seed is a list of per-seed summary dicts (final values only)
    # We need year-by-year data from metrics.csv
    metrics_path = batch2 / scenario / "metrics.csv"
    if not metrics_path.exists():
        print(f"WARNING: {metrics_path} not found — using final values only")
        continue

    df = pd.read_csv(metrics_path)

    if "avg_cooperation" not in df.columns or "year" not in df.columns:
        print(f"WARNING: expected columns missing in {metrics_path}")
        continue

    # Average across seeds by year
    mean_by_year = df.groupby("year")["avg_cooperation"].mean()
    std_by_year  = df.groupby("year")["avg_cooperation"].std()
    years        = mean_by_year.index

    ax.plot(years, mean_by_year, color=props["color"],
            linewidth=2.0, label=props["label"], zorder=3)
    ax.fill_between(years,
                    mean_by_year - std_by_year,
                    mean_by_year + std_by_year,
                    color=props["color"], alpha=0.12, zorder=2)

ax.axhline(0.5, color='gray', linestyle='--', linewidth=0.8,
           alpha=0.5, label='Initialization mean (0.5)')
ax.set_xlabel("Simulated Year", fontsize=11)
ax.set_ylabel("Mean Cooperation Propensity", fontsize=11)
ax.set_title(
    "Figure 3: Heritable Cooperation Propensity Over 500 Years\n"
    "by Governance Regime (mean ± 1 SD, 10 seeds each)",
    fontsize=11, fontweight='bold'
)
ax.set_ylim(0.35, 0.75)
ax.legend(fontsize=9, loc='upper left')
ax.spines[['top','right']].set_visible(False)
ax.grid(axis='y', alpha=0.3)

note = ("Shaded bands = ±1 SD across seeds. "
        "Convergence of all three lines confirms behavioral substitution "
        "without genetic divergence.")
ax.text(0.5, -0.14, note, transform=ax.transAxes,
        ha='center', fontsize=8, color='#555555', style='italic')

plt.tight_layout()
plt.savefig("docs/figures/fig3_cooperation_trajectory.png",
            dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print("Figure 3 saved.")
```

================================================================================
RUN THE FIGURE SCRIPTS
================================================================================

After creating the three figure scripts, run them:

  cd D:\EXPERIMENTS\SIM
  pip install matplotlib pandas numpy --break-system-packages --quiet
  python docs/figures/fig1_tick_architecture.py
  python docs/figures/fig2_calibration.py
  python docs/figures/fig3_cooperation_trajectory.py

Verify all three PNG files exist:
  docs/figures/fig1_tick_architecture.png
  docs/figures/fig2_calibration.png
  docs/figures/fig3_cooperation_trajectory.png

If any figure script fails, diagnose the error, fix the script, and re-run.
Do NOT skip figures — they are required for submission.

================================================================================
ADD FIGURE CAPTIONS TO THE PAPER
================================================================================

After all text revisions are complete, add a new section at the end of the
paper, just before References:

---

## Figures

**Figure 1.** Annual simulation tick execution order for SIMSIV v1.0. Each of
the nine engines executes in fixed sequence, ensuring causal consistency:
conflict precedes mating (dead agents cannot mate), mortality precedes
institutions (inheritance sees all deaths). Metrics are collected after all
engines complete. *(See docs/figures/fig1_tick_architecture.png)*

**Figure 2.** Calibrated model outputs relative to anthropological target
ranges. Green checkmarks (✓) indicate metrics within target range; the model
achieves all nine targets simultaneously (calibration score = 1.000). Target
ranges are shown as gray bars; calibrated values as vertical lines. Source
data: autosim/best_config.yaml. *(See docs/figures/fig2_calibration.png)*

**Figure 3.** Mean heritable cooperation propensity (cooperation_propensity
trait) over 500 simulated years for three governance regimes: No Institutions
(law strength fixed at 0), Free Competition (endogenous institutional drift),
and Strong State (law strength fixed at 0.8, monogamy enforced). Shaded bands
show ±1 SD across 10 seeds. The convergence of all three trajectories to
approximately 0.52 confirms that institutional governance does not alter the
evolutionary trajectory of the cooperation trait at this timescale. Source
data: outputs/experiments/20260315_194150_NO_INSTITUTIONS_FREE_COMPETITION_STRONG_STATE_s10_y500/
*(See docs/figures/fig3_cooperation_trajectory.png)*

---

================================================================================
FINAL VERIFICATION CHECKLIST
================================================================================

Before saving the revised paper, verify:

  [ ] Substitution claim is softened in 3 locations (abstract, results, conclusions)
  [ ] Boyd & Richerson (1985) added to Section 1.1 and References
  [ ] SDs added to 500-year governance table in Section 5.2
  [ ] SDs added to 200-year governance table in Section 5.2
  [ ] Cooperation attractor expanded to two paragraphs in Section 5.5
  [ ] Platform invitation sentence added before repo URL in Conclusions
  [ ] Figure 1, 2, 3 references added in Sections 2.1, 3.3, 5.2
  [ ] Figures section added before References
  [ ] All three PNG files exist in docs/figures/
  [ ] No new factual claims introduced (only softening and expanding existing ones)
  [ ] Word count is still between 6,000-8,500 words

Save the revised paper to:
  D:\EXPERIMENTS\SIM\docs\paper1_draft.md   (overwrite — git tracks history)

Also save the three figure scripts to:
  D:\EXPERIMENTS\SIM\docs\figures\fig1_tick_architecture.py
  D:\EXPERIMENTS\SIM\docs\figures\fig2_calibration.py
  D:\EXPERIMENTS\SIM\docs\figures\fig3_cooperation_trajectory.py

================================================================================
END OF REVISION PROMPT
================================================================================
