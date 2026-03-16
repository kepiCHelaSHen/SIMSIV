"""Figure 1: SIMSIV Annual Tick Architecture."""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

fig, ax = plt.subplots(figsize=(7, 10))
ax.set_xlim(0, 10)
ax.set_ylim(0, 12)
ax.axis('off')

engines = [
    ("1. Environment",    "Seasonal cycles, scarcity shocks, epidemics",      "#4A90D9"),
    ("2. Resources",      "8-phase acquisition across 3 resource types",       "#5BA85B"),
    ("3. Conflict",       "Violence, deterrence, coalition defense",            "#D94A4A"),
    ("4. Mating",         "Female choice, pair bonding, EPC",                  "#D97A4A"),
    ("5. Reproduction",   "h\u00b2-weighted inheritance, developmental plasticity", "#A84AB8"),
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
                    arrowprops=dict(arrowstyle="->", color="#cccccc", lw=1.5))

ax.text(5, 11.7, "SIMSIV \u2014 Annual Simulation Tick",
        ha='center', va='center', fontsize=12, fontweight='bold', color='#333333')
ax.text(5, 0.25, "\u2191 Metrics collected after all engines complete \u2192 next year",
        ha='center', va='center', fontsize=8, color='#666666', style='italic')

plt.tight_layout()
plt.savefig("docs/figures/fig1_tick_architecture.png",
            dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print("Figure 1 saved.")
