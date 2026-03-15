# Deep Dive 20: Leadership and Collective Coordination

## Design Decisions

### Two leadership types
- **War Leader**: Selected by highest dominance_score in faction. Must exceed
  faction avg * 1.2. Boosts faction combat effectiveness, deters rival targeting.
- **Peace Chief**: Selected by highest prestige_score in faction. Mediates
  intra-faction disputes, boosts cooperation sharing rate.

Same agent can hold both roles if they lead in both dimensions.

### Leader selection
- Computed whenever factions are re-detected (every faction_detection_interval years)
- Stored on `society.faction_leaders` dict, not on agents
- Agents over age 55 with health < 0.5 are ineligible
- Egalitarian bands (no one exceeds threshold) have no recognized leader

### War leader effects
- Faction members get `war_leader_aggression_boost` (20%) to conflict initiation
- Members fighting alongside war leader get `war_leader_combat_bonus` (+0.05 power)
- Factions with war leaders are targeted less (`war_leader_deterrence` = 0.2)

### Peace chief effects
- Intra-faction conflict mediation: `peace_chief_arbitration_probability` * prestige
- Faction sharing rate boosted by `peace_chief_sharing_boost` (10%)
- Chief gains +0.02 prestige from successful mediations

### Backward compatibility
`leadership_enabled=False` → no leader effects applied.

## Config parameters
9 new parameters (war_leader_*, peace_chief_*, leadership_*)

## Metrics
- `war_leader_count`, `peace_chief_count`: active leaders across all factions
- `leadership_arbitrations`: peace chief mediation events per tick
