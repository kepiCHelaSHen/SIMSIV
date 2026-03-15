# Deep Dive 21: Resource Type Differentiation

## Design Decisions

### Three resource types
- **Subsistence** (`current_resources`): Food/water/shelter. Perishable (40% retention).
  Primary sharing good. Directly maps to health/survival. Backward compatible.
- **Tools** (`current_tools`): Weapons/implements. Durable (10% decay/yr). Multiply
  subsistence production. Primary inheritance and trade good. Combat advantage.
- **Prestige Goods** (`current_prestige_goods`): Ornaments/ritual objects. Nearly
  permanent (5% decay). Pure social value — boost prestige and mate attractiveness.

### Production
- Subsistence: existing competitive weight system, multiplied by tools
- Tools: intelligence * 0.5 + status_drive * 0.3 + experience * 0.2 (slower gain)
- Prestige goods: generated from generous sharing (cooperation > 0.5)

### Trade
- Intra-band only (annual probability 0.1)
- Tool-subsistence exchange at configurable rate (1 tool = 3 subsistence)
- Requires trust > 0.4 between parties and proximity (neighborhood)
- Trade generates trust (+0.03 bilateral)

### Conflict targeting
- Subsistence envy: 1.3x (existing)
- Tool envy: 1.4x (superior tools are tempting targets)
- Tool looting: 20% chance winner takes one tool from loser

### Inheritance
- Subsistence: largely consumed before death — little inherited
- Tools: primary inheritance good — splits equally to heirs
- Prestige goods: inherited, heirs gain small prestige_score boost

### Mate value
- Prestige goods boost attractiveness signal: `prestige_goods_mate_signal` (0.05)

## Config parameters
11 new parameters controlling decay rates, caps, production, trade, and signaling.

## Metrics
- `avg_tools`, `avg_prestige_goods`: per-type averages
- `tool_gini`, `prestige_goods_gini`: inequality measures
- `trade_events`: annual trade activity
