"""
Generate publication-quality figures for all 6 v2 battery experiments.
Reads CSV data from outputs/experiments/v2_battery/ and saves PNGs.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path

DATA_DIR = Path("outputs/experiments/v2_battery")
OUT_DIR = DATA_DIR / "figures"
OUT_DIR.mkdir(exist_ok=True)

COLORS = {"Free": "#2196F3", "State": "#F44336", "Emergent": "#4CAF50"}


def fig1_statistical_power():
    """Exp 1: Cooperation by seed, Free vs State."""
    df = pd.read_csv(DATA_DIR / "exp1_power.csv")
    # CSV has wide format: year, coop_Free, coop_State, ..., seed
    # Get last year (200) per seed
    last = df.groupby("seed").last().reset_index()

    fig, ax = plt.subplots(figsize=(8, 5))
    seeds = sorted(last["seed"].unique())
    x = np.arange(len(seeds))
    w = 0.35

    free_vals = [last[last["seed"] == s]["coop_Free"].values[0] for s in seeds]
    state_vals = [last[last["seed"] == s]["coop_State"].values[0] for s in seeds]

    ax.bar(x - w/2, free_vals, w, label="Free Competition", color=COLORS["Free"], alpha=0.8)
    ax.bar(x + w/2, state_vals, w, label="Strong State", color=COLORS["State"], alpha=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels([str(s) for s in seeds])
    ax.set_xlabel("Seed", fontsize=11)
    ax.set_ylabel("Mean Cooperation (year 200)", fontsize=11)
    ax.set_title("Exp 1: Statistical Power — Cooperation by Seed & Regime", fontsize=13, fontweight='bold')
    ax.legend(fontsize=10)
    ax.set_ylim(0.3, 0.65)
    ax.axhline(y=np.mean(free_vals + state_vals), color='gray', linestyle='--', alpha=0.3)
    ax.grid(axis='y', alpha=0.2)
    plt.tight_layout()
    fig.savefig(OUT_DIR / "exp1_power.png", dpi=200, bbox_inches='tight')
    print(f"  Saved exp1_power.png")
    plt.close()


def fig2_factorial():
    """Exp 2: 2x2 Factorial — Raiding x Institutions."""
    # Data from report
    data = {
        ("Free", "Raiding ON"): 0.506,
        ("Free", "Raiding OFF"): 0.482,
        ("State", "Raiding ON"): 0.469,
        ("State", "Raiding OFF"): 0.484,
    }

    fig, ax = plt.subplots(figsize=(7, 5))
    x = [0, 1]
    free_y = [data[("Free", "Raiding OFF")], data[("Free", "Raiding ON")]]
    state_y = [data[("State", "Raiding OFF")], data[("State", "Raiding ON")]]

    ax.plot(x, free_y, 'o-', color=COLORS["Free"], linewidth=2.5, markersize=10,
            label="Free Competition")
    ax.plot(x, state_y, 's-', color=COLORS["State"], linewidth=2.5, markersize=10,
            label="Strong State")

    ax.set_xticks(x)
    ax.set_xticklabels(["Raiding OFF", "Raiding ON"], fontsize=11)
    ax.set_ylabel("Mean Cooperation (year 200)", fontsize=11)
    ax.set_title("Exp 2: Causal Mechanism — 2x2 Factorial\n(Raiding x Institutions)",
                 fontsize=13, fontweight='bold')
    ax.legend(fontsize=10)
    ax.set_ylim(0.45, 0.52)
    ax.grid(alpha=0.2)

    # Annotate interaction
    ax.annotate("Interaction: +0.039",
                xy=(0.5, 0.495), fontsize=10, ha='center',
                bbox=dict(boxstyle="round,pad=0.3", facecolor="wheat", alpha=0.7))
    plt.tight_layout()
    fig.savefig(OUT_DIR / "exp2_factorial.png", dpi=200, bbox_inches='tight')
    print(f"  Saved exp2_factorial.png")
    plt.close()


def fig3_raid_sweep():
    """Exp 3: Raid intensity vs cooperation."""
    raid_probs = [0.1, 0.3, 0.5, 0.7]
    coop = [0.468, 0.492, 0.506, 0.509]
    violence = [0.006, 0.013, 0.023, 0.033]
    fst = [0.248, 0.226, 0.302, 0.230]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Left: cooperation vs raid intensity
    ax1.plot(raid_probs, coop, 'o-', color=COLORS["Free"], linewidth=2.5, markersize=10)
    ax1.set_xlabel("Raid Base Probability", fontsize=11)
    ax1.set_ylabel("Mean Cooperation", fontsize=11)
    ax1.set_title("Cooperation Increases with Raiding\n(Bowles 2006 prediction confirmed)",
                  fontsize=12, fontweight='bold')
    ax1.grid(alpha=0.2)
    ax1.set_ylim(0.45, 0.52)

    # Right: Fst and violence
    ax2r = ax2.twinx()
    l1, = ax2.plot(raid_probs, fst, 'D-', color="#9C27B0", linewidth=2, markersize=8, label="Fst")
    l2, = ax2r.plot(raid_probs, violence, 's-', color="#FF9800", linewidth=2, markersize=8, label="Violence rate")
    ax2.set_xlabel("Raid Base Probability", fontsize=11)
    ax2.set_ylabel("Fst (prosocial traits)", fontsize=11, color="#9C27B0")
    ax2r.set_ylabel("Violence Rate", fontsize=11, color="#FF9800")
    ax2.set_title("Divergence & Violence vs Raid Intensity", fontsize=12, fontweight='bold')
    ax2.legend(handles=[l1, l2], fontsize=9, loc='upper left')
    ax2.grid(alpha=0.2)

    plt.tight_layout()
    fig.savefig(OUT_DIR / "exp3_raid_sweep.png", dpi=200, bbox_inches='tight')
    print(f"  Saved exp3_raid_sweep.png")
    plt.close()


def fig4_fission():
    """Exp 4: Fission threshold effects."""
    thresholds = [75, 150, 300]
    coop_free = [0.411, 0.477, 0.477]
    coop_state = [0.493, 0.490, 0.490]
    fst = [0.341, 0.233, 0.233]
    n_bands = [8.0, 4.0, 4.0]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Left: cooperation by regime
    x = np.arange(len(thresholds))
    w = 0.3
    ax1.bar(x - w/2, coop_free, w, label="Free", color=COLORS["Free"], alpha=0.8)
    ax1.bar(x + w/2, coop_state, w, label="State", color=COLORS["State"], alpha=0.8)
    ax1.set_xticks(x)
    ax1.set_xticklabels([str(t) for t in thresholds])
    ax1.set_xlabel("Fission Threshold (agents)", fontsize=11)
    ax1.set_ylabel("Mean Cooperation", fontsize=11)
    ax1.set_title("Cooperation by Fission Threshold", fontsize=12, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.set_ylim(0.35, 0.55)
    ax1.grid(axis='y', alpha=0.2)

    # Right: Fst and band count
    ax2r = ax2.twinx()
    l1, = ax2.plot(thresholds, fst, 'D-', color="#9C27B0", linewidth=2, markersize=10, label="Fst")
    l2, = ax2r.plot(thresholds, n_bands, 's-', color="#4CAF50", linewidth=2, markersize=10, label="N bands")
    ax2.set_xlabel("Fission Threshold", fontsize=11)
    ax2.set_ylabel("Fst", fontsize=11, color="#9C27B0")
    ax2r.set_ylabel("Number of Bands", fontsize=11, color="#4CAF50")
    ax2.set_title("Founder Effects: Lower Threshold = More Bands + Higher Fst",
                  fontsize=11, fontweight='bold')
    ax2.legend(handles=[l1, l2], fontsize=9)
    ax2.grid(alpha=0.2)

    plt.tight_layout()
    fig.savefig(OUT_DIR / "exp4_fission.png", dpi=200, bbox_inches='tight')
    print(f"  Saved exp4_fission.png")
    plt.close()


def fig5_migration():
    """Exp 5: Migration rate vs Fst."""
    rates = [0.001, 0.005, 0.010, 0.050]
    fst = [0.314, 0.233, 0.219, 0.333]
    between_sel = [0.110, 0.064, -0.042, -0.180]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    ax1.plot(rates, fst, 'o-', color="#9C27B0", linewidth=2.5, markersize=10)
    ax1.set_xlabel("Migration Rate (per agent per year)", fontsize=11)
    ax1.set_ylabel("Fst (prosocial traits)", fontsize=11)
    ax1.set_title("Migration Reduces Fst\n(Wright Island Model confirmed for m<0.01)",
                  fontsize=12, fontweight='bold')
    ax1.set_xscale('log')
    ax1.grid(alpha=0.2)

    # Annotate the anomaly
    ax1.annotate("Transient regime\n(200yr < equilibrium)",
                 xy=(0.050, 0.333), xytext=(0.025, 0.28),
                 arrowprops=dict(arrowstyle="->", color='red'),
                 fontsize=9, color='red')

    ax2.bar(range(len(rates)), between_sel,
            color=[COLORS["Free"] if v > 0 else COLORS["State"] for v in between_sel],
            alpha=0.8)
    ax2.set_xticks(range(len(rates)))
    ax2.set_xticklabels([str(r) for r in rates])
    ax2.set_xlabel("Migration Rate", fontsize=11)
    ax2.set_ylabel("Between-Group Selection Coefficient", fontsize=11)
    ax2.set_title("Migration Opposes Between-Group Selection",
                  fontsize=12, fontweight='bold')
    ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    ax2.grid(axis='y', alpha=0.2)

    plt.tight_layout()
    fig.savefig(OUT_DIR / "exp5_migration.png", dpi=200, bbox_inches='tight')
    print(f"  Saved exp5_migration.png")
    plt.close()


def fig6_longrun():
    """Exp 6: Long-run dynamics (500yr)."""
    seeds = [42, 137, 271]
    free_200 = [0.493, 0.538, 0.400]
    state_200 = [0.493, 0.524, 0.454]
    free_500 = [0.674, 0.627, 0.323]
    state_500 = [None, None, 0.531]  # NaN = extinct

    fig, ax = plt.subplots(figsize=(10, 6))

    for i, seed in enumerate(seeds):
        # Free trajectory
        ax.plot([200, 500], [free_200[i], free_500[i]], 'o-',
                color=COLORS["Free"], linewidth=2, markersize=8,
                label="Free" if i == 0 else None, alpha=0.7)
        ax.annotate(f"s{seed}", xy=(200, free_200[i]), fontsize=8, ha='right')

        # State trajectory
        if state_500[i] is not None:
            ax.plot([200, 500], [state_200[i], state_500[i]], 's-',
                    color=COLORS["State"], linewidth=2, markersize=8,
                    label="State" if i == 0 else None, alpha=0.7)
        else:
            ax.plot([200], [state_200[i]], 's',
                    color=COLORS["State"], markersize=8,
                    label="State" if i == 0 else None, alpha=0.7)
            ax.annotate(f"EXTINCT", xy=(350, state_200[i]),
                       fontsize=9, color='red', fontweight='bold',
                       ha='center')
            ax.plot([200, 350], [state_200[i], state_200[i]], '--',
                    color=COLORS["State"], alpha=0.3)

    ax.set_xlabel("Year", fontsize=12)
    ax.set_ylabel("Mean Cooperation", fontsize=12)
    ax.set_title("Exp 6: Long-Run Dynamics (500yr)\n2/3 Seeds: State Bands Go Extinct",
                 fontsize=13, fontweight='bold')
    ax.legend(fontsize=11)
    ax.set_xlim(180, 520)
    ax.set_ylim(0.25, 0.75)
    ax.grid(alpha=0.2)

    plt.tight_layout()
    fig.savefig(OUT_DIR / "exp6_longrun.png", dpi=200, bbox_inches='tight')
    print(f"  Saved exp6_longrun.png")
    plt.close()


def main():
    print("Generating v2 battery experiment figures...")
    print(f"Output: {OUT_DIR.resolve()}\n")

    fig1_statistical_power()
    fig2_factorial()
    fig3_raid_sweep()
    fig4_fission()
    fig5_migration()
    fig6_longrun()

    print(f"\nDone. 6 figures saved to {OUT_DIR}/")


if __name__ == "__main__":
    main()
