"""Figure 2: Calibration targets vs achieved values."""
import matplotlib.pyplot as plt
import numpy as np

metrics = [
    "Resource\nGini", "Mating\nInequality", "Violence\nDeath Frac",
    "Pop Growth\nRate", "Child\nSurvival", "Lifetime\nBirths",
    "Bond\nDissolution", "Mean\nCooperation", "Mean\nAggression",
]

targets = [
    (0.30, 0.50), (0.40, 0.70), (0.05, 0.15), (0.001, 0.015),
    (0.50, 0.70), (4.0, 7.0), (0.10, 0.30), (0.25, 0.70), (0.30, 0.60),
]

achieved = [0.310, 0.578, 0.069, 0.0137, 0.642, 4.21, 0.118, 0.507, 0.494]

fig, axes = plt.subplots(1, 9, figsize=(14, 4))
fig.suptitle("Figure 2: Calibrated Values vs. Anthropological Target Ranges",
             fontsize=11, fontweight='bold', y=1.02)

colors_in  = "#4CAF50"
colors_out = "#F44336"

for i, (ax, metric, (lo, hi), val) in enumerate(
        zip(axes, metrics, targets, achieved)):
    in_range = lo <= val <= hi
    color = colors_in if in_range else colors_out

    ax.barh(0, hi - lo, left=lo, height=0.5,
            color='#E8E8E8', edgecolor='#AAAAAA', linewidth=0.8)
    ax.axvline(val, color=color, linewidth=2.5)

    ax.set_xlim(lo - (hi-lo)*0.3, hi + (hi-lo)*0.3)
    ax.set_ylim(-0.5, 0.8)
    ax.set_xlabel(f"{val:.3f}", fontsize=8, labelpad=2)
    ax.set_title(metric, fontsize=7.5, pad=3)
    ax.set_yticks([])
    ax.tick_params(axis='x', labelsize=7)
    ax.spines[['top','left','right']].set_visible(False)

    status = "\u2713" if in_range else "\u2717"
    ax.text(0.5, 0.75, status, transform=ax.transAxes,
            ha='center', fontsize=12, color=color)

plt.tight_layout()
plt.savefig("docs/figures/fig2_calibration.png",
            dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print("Figure 2 saved.")
