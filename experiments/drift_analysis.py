"""
Statistical analysis + figure generation for the drift experiment.

1. Fisher's exact test on Condition A (95/96 drift) vs Treatment (0/7)
2. Sensitivity analysis: drift magnitude vs ground truth value
3. Inter-model agreement (do GPT-4o and Grok-3 drift to same values?)
4. Scatter plot: ground truth vs produced value (Figure 1)
5. Condition A vs B comparison table
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats as sp_stats
from pathlib import Path

OUT_DIR = Path(__file__).parent.parent / "docs" / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Raw data from Condition A (n=10 per model, blind) ────────────────────────

CONDITION_A = {
    "GPT-4o": {
        "empathy_coeff":       {"truth": 0.15, "values": [0.30, 0.30, None, 0.50, 0.20, 0.50, None, 0.50, 0.30, 0.30]},
        "coop_norm_coeff":     {"truth": 0.10, "values": [0.40, 0.40, 0.20, 0.00, 0.30, 0.30, 0.30, 0.00, 0.25, 0.20]},
        "social_skill_coeff":  {"truth": 0.10, "values": [0.50, 0.50, 0.20, 0.25, 0.30, 0.20, 0.50, 0.20, 0.25, 0.20]},
        "cohesion_bonus_coeff":{"truth": 0.20, "values": [0.30, None, 0.50, None, 0.50, 0.50, 0.60, 0.50, 0.30, 0.50]},
        "n_prosocial_traits":  {"truth": 4,    "values": [4, 5, 6, 5, 5, 5, 5, 5, 5, 5]},
    },
    "Grok-3": {
        "empathy_coeff":       {"truth": 0.15, "values": [0.25, 0.25, 0.25, 0.25, 0.25, 0.20, 0.20, 0.25, 0.20, 0.25]},
        "coop_norm_coeff":     {"truth": 0.10, "values": [0.15, 0.15, 0.15, 0.15, 0.15, 0.20, 0.20, 0.15, 0.20, 0.15]},
        "social_skill_coeff":  {"truth": 0.10, "values": [0.30, 0.30, 0.30, 0.30, 0.30, 0.30, 0.30, 0.30, 0.30, 0.30]},
        "cohesion_bonus_coeff":{"truth": 0.20, "values": [0.30, 0.30, 0.30, 0.00, 0.30, 0.50, 0.50, 0.10, 0.80, 0.10]},
        "n_prosocial_traits":  {"truth": 4,    "values": [8, 7, 8, 7, 7, 7, 8, 7, 7, 8]},
    },
}

# Condition B results (source-code visible, reliable coefficients only)
CONDITION_B = {
    "GPT-4o": {
        "empathy_coeff":      {"truth": 0.15, "values": [0.15]*10},
        "coop_norm_coeff":    {"truth": 0.10, "values": [0.10]*10},
        "social_skill_coeff": {"truth": 0.10, "values": [0.10]*6},  # 6 parseable
    },
    "Grok-3": {
        "empathy_coeff":      {"truth": 0.15, "values": [0.15]*10},
        "coop_norm_coeff":    {"truth": 0.10, "values": [0.10]*10},
        "social_skill_coeff": {"truth": 0.10, "values": [0.10, 0.10, 0.10, 0.10, 0.10, 0.00, 0.10, 0.10, 0.10, 0.10]},
    },
}


def fisher_exact_test():
    """Fisher's exact test: Condition A (95/96 drift) vs Treatment (0/7)."""
    print("=" * 60)
    print("1. FISHER'S EXACT TEST")
    print("=" * 60)

    # Contingency table: [[drift, no-drift], [drift, no-drift]]
    #                     Condition A    Treatment
    table = [[95, 1],    # drift
             [0, 7]]     # no drift
    odds, p = sp_stats.fisher_exact(table, alternative='two-sided')

    print(f"  Condition A: 95 drift, 1 correct (n=96)")
    print(f"  Treatment:   0 drift, 7 correct (n=7)")
    print(f"  Fisher's exact p = {p:.2e}")
    print(f"  Odds ratio = {odds}")
    print(f"  Interpretation: {'Significant' if p < 0.05 else 'Not significant'} (p < 0.001)")
    return p


def sensitivity_analysis():
    """Plot drift magnitude vs ground truth value."""
    print("\n" + "=" * 60)
    print("2. SENSITIVITY: DRIFT MAGNITUDE vs GROUND TRUTH VALUE")
    print("=" * 60)

    # Collect (truth, mean_produced, model) tuples
    points = []
    for model, coeffs in CONDITION_A.items():
        for name, data in coeffs.items():
            if name == "n_prosocial_traits":
                continue  # different scale
            truth = data["truth"]
            vals = [v for v in data["values"] if v is not None]
            if not vals:
                continue
            mean_produced = np.mean(vals)
            mean_delta = mean_produced - truth
            pct_delta = (mean_delta / truth) * 100
            points.append((truth, mean_produced, mean_delta, pct_delta, model, name))
            print(f"  {model} {name}: truth={truth}, mean={mean_produced:.3f}, "
                  f"delta={mean_delta:+.3f} ({pct_delta:+.0f}%)")

    # Observation: smaller truth values drift more (in percentage terms)
    truths = [p[0] for p in points]
    pct_deltas = [p[3] for p in points]
    r, p_val = sp_stats.pearsonr(truths, pct_deltas)
    print(f"\n  Correlation(truth, %drift): r={r:.3f}, p={p_val:.3f}")
    print(f"  {'Confirmed' if r < -0.3 else 'Not confirmed'}: "
          f"smaller coefficients drift proportionally more")

    return points


def inter_model_agreement():
    """Do GPT-4o and Grok-3 drift to the same values?"""
    print("\n" + "=" * 60)
    print("3. INTER-MODEL AGREEMENT")
    print("=" * 60)

    for name in ["empathy_coeff", "coop_norm_coeff", "social_skill_coeff", "cohesion_bonus_coeff"]:
        gpt_vals = [v for v in CONDITION_A["GPT-4o"][name]["values"] if v is not None]
        grok_vals = [v for v in CONDITION_A["Grok-3"][name]["values"] if v is not None]
        truth = CONDITION_A["GPT-4o"][name]["truth"]

        gpt_mean = np.mean(gpt_vals)
        grok_mean = np.mean(grok_vals)
        gpt_std = np.std(gpt_vals)
        grok_std = np.std(grok_vals)

        # Do they converge to the same wrong value?
        overlap = abs(gpt_mean - grok_mean) < max(gpt_std, grok_std)

        print(f"  {name} (truth={truth}):")
        print(f"    GPT-4o: mean={gpt_mean:.3f} ± {gpt_std:.3f}")
        print(f"    Grok-3: mean={grok_mean:.3f} ± {grok_std:.3f}")
        print(f"    Same wrong value? {'Yes (overlapping)' if overlap else 'No (model-specific priors)'}")


def condition_comparison():
    """Compare Condition A vs B drift rates for reliable coefficients."""
    print("\n" + "=" * 60)
    print("4. CONDITION A vs B COMPARISON (reliable coefficients only)")
    print("=" * 60)

    print(f"\n  {'Coefficient':<22s} {'Model':<8s} {'Cond A':>8s} {'Cond B':>8s} {'Change':>10s}")
    print(f"  {'-'*60}")

    for model in ["GPT-4o", "Grok-3"]:
        for name in ["empathy_coeff", "coop_norm_coeff", "social_skill_coeff"]:
            a_vals = [v for v in CONDITION_A[model][name]["values"] if v is not None]
            truth = CONDITION_A[model][name]["truth"]
            a_drift = sum(1 for v in a_vals if abs(v - truth) > 0.001)
            a_rate = f"{a_drift}/{len(a_vals)}"

            if name in CONDITION_B.get(model, {}):
                b_vals = CONDITION_B[model][name]["values"]
                b_drift = sum(1 for v in b_vals if abs(v - truth) > 0.001)
                b_rate = f"{b_drift}/{len(b_vals)}"
            else:
                b_rate = "---"

            print(f"  {name:<22s} {model:<8s} {a_rate:>8s} {b_rate:>8s} {'100%->0%' if '0/' in b_rate else '':>10s}")


def create_scatter_plot():
    """Figure 1: Ground truth vs model-produced coefficient values."""
    print("\n" + "=" * 60)
    print("5. GENERATING SCATTER PLOT (Figure 1)")
    print("=" * 60)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    colors = {"GPT-4o": "#1f77b4", "Grok-3": "#ff7f0e", "Protocol": "#2ca02c"}

    # ── Left panel: Condition A (blind) ──────────────────────────────────
    ax = ax1
    ax.set_title("Condition A: No Source Code (Blind)", fontsize=13, fontweight='bold')

    for model, coeffs in CONDITION_A.items():
        for name, data in coeffs.items():
            if name == "n_prosocial_traits":
                continue
            truth = data["truth"]
            vals = [v for v in data["values"] if v is not None]
            # Add jitter on x-axis to separate overlapping points
            jitter = np.random.default_rng(42).normal(0, 0.003, len(vals))
            ax.scatter([truth + j for j in jitter], vals,
                      color=colors[model], alpha=0.5, s=40, label=model,
                      edgecolors='white', linewidths=0.5)

    # Protocol points
    protocol_truths = [0.15, 0.10, 0.10, 0.20]
    ax.scatter(protocol_truths, protocol_truths,
              color=colors["Protocol"], marker='D', s=80, label="Protocol",
              edgecolors='black', linewidths=1, zorder=5)

    # Diagonal (perfect compliance)
    ax.plot([0, 0.55], [0, 0.55], 'k--', alpha=0.3, linewidth=1, label="Perfect compliance")
    ax.set_xlabel("Ground Truth Coefficient", fontsize=11)
    ax.set_ylabel("Model-Produced Coefficient", fontsize=11)
    ax.set_xlim(0.05, 0.25)
    ax.set_ylim(-0.05, 0.85)

    # De-duplicate legend
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), loc='upper left', fontsize=9)
    ax.grid(True, alpha=0.2)

    # ── Right panel: Condition B (source code visible) ───────────────────
    ax = ax2
    ax.set_title("Condition B: Source Code Visible", fontsize=13, fontweight='bold')

    for model, coeffs in CONDITION_B.items():
        for name, data in coeffs.items():
            truth = data["truth"]
            vals = data["values"]
            jitter = np.random.default_rng(43).normal(0, 0.003, len(vals))
            ax.scatter([truth + j for j in jitter], vals,
                      color=colors[model], alpha=0.5, s=40, label=model,
                      edgecolors='white', linewidths=0.5)

    ax.scatter(protocol_truths, protocol_truths,
              color=colors["Protocol"], marker='D', s=80, label="Protocol",
              edgecolors='black', linewidths=1, zorder=5)

    ax.plot([0, 0.55], [0, 0.55], 'k--', alpha=0.3, linewidth=1, label="Perfect compliance")
    ax.set_xlabel("Ground Truth Coefficient", fontsize=11)
    ax.set_ylabel("Model-Produced Coefficient", fontsize=11)
    ax.set_xlim(0.05, 0.25)
    ax.set_ylim(-0.05, 0.85)

    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), loc='upper left', fontsize=9)
    ax.grid(True, alpha=0.2)

    fig.suptitle("Specification Drift: Model-Produced vs Ground Truth Coefficients",
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()

    out_path = OUT_DIR / "figure1_drift_scatter.png"
    fig.savefig(out_path, dpi=200, bbox_inches='tight')
    print(f"  Saved to {out_path}")

    # ── Also generate the sensitivity figure ─────────────────────────────
    fig2, ax = plt.subplots(figsize=(8, 5))
    ax.set_title("Drift Magnitude vs Ground Truth Value", fontsize=13, fontweight='bold')

    for model, coeffs in CONDITION_A.items():
        xs, ys = [], []
        for name, data in coeffs.items():
            if name == "n_prosocial_traits":
                continue
            truth = data["truth"]
            vals = [v for v in data["values"] if v is not None]
            for v in vals:
                xs.append(truth)
                ys.append(v - truth)  # absolute drift
        ax.scatter(xs, ys, color=colors[model], alpha=0.4, s=30, label=model)

    ax.axhline(y=0, color='black', linestyle='--', alpha=0.3, label="No drift")
    ax.set_xlabel("Ground Truth Coefficient", fontsize=11)
    ax.set_ylabel("Drift (produced - truth)", fontsize=11)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.2)
    plt.tight_layout()

    out_path2 = OUT_DIR / "figure2_drift_sensitivity.png"
    fig2.savefig(out_path2, dpi=200, bbox_inches='tight')
    print(f"  Saved to {out_path2}")


def main():
    p = fisher_exact_test()
    points = sensitivity_analysis()
    inter_model_agreement()
    condition_comparison()
    create_scatter_plot()

    print("\n" + "=" * 60)
    print("SUMMARY FOR PAPER")
    print("=" * 60)
    print(f"  Fisher's exact test: p = {p:.2e}")
    print(f"  Condition A (blind): 95/96 = 99% drift")
    print(f"  Condition B (source visible): ~0% drift on M1/M2 coefficients")
    print(f"  Treatment (protocol): 0/7 = 0% drift")
    print(f"  Conclusion: Source code access eliminates simple coefficient drift.")
    print(f"  Protocol's added value: ensures source IS consulted + catches")
    print(f"  structural errors (multiplicative CAC, scope creep) that")
    print(f"  source-pasting alone does not prevent.")


if __name__ == "__main__":
    main()
