# Deep Dive 18: Proximity Tiers and Social Network Structure

## Design Decisions

### Three-tier proximity model (NOT spatial)
Proximity is purely relational — no x,y coordinates. Three tiers define
interaction probability via soft multipliers:

- **Tier 1 — Household (3-8 agents)**: Partners + dependent children + living
  parents. Dynamically computed each tick. Interaction multiplier: 4x.
- **Tier 2 — Neighborhood (15-40 agents)**: Trusted allies (trust > 0.5) +
  same-faction + siblings. Refreshed every 3 years. Multiplier: 2x.
- **Tier 3 — Band (full population)**: Everyone else. Multiplier: 1x (default).

### Household computation
`household_of(agent)` returns the set of agent IDs in the same household:
- `agent.partner_ids` (symmetric — both directions)
- Dependent children (`offspring_ids` where child age < `child_dependency_years`)
- Living parents (`parent_ids` if alive)

Always current — rebuilds from relationship state each call.

### Neighborhood computation
`refresh_neighborhoods()` runs every `neighborhood_refresh_interval` years (default 3).
Priority order for neighborhood membership:
1. Agents with trust > `neighborhood_trust_threshold` (0.5) in reputation ledger
2. Same-faction members (`faction_id` match)
3. Siblings (shared `parent_ids`)
4. Capped at `neighborhood_size_max` (40), keeping highest-trust agents

Stored as `agent.neighborhood_ids` (list of agent IDs).

### Engine effects

**Resources (cooperation sharing)**:
- Sharing restricted to household + neighborhood
- Only very cooperative agents (cooperation > 0.7) share with band-tier agents
- Cooperation networks become more local and realistic

**Conflict (target selection)**:
- Candidate weights multiplied by tier: 4x household, 2x neighborhood, 1x band
- Most conflicts occur within neighborhood (proximity breeds rivalry)
- Cross-tier conflicts remain possible (reduced probability, not blocked)
- Jealousy-specific targeting unaffected (rival targeting bypasses tier)

**Mating (mate search)**:
- Females evaluate neighborhood males at full weight
- Band-tier males weighted at `band_mate_weight` (0.3) — less visible
- Creates local mate markets and naturally increases endogamy

**Gossip (reputation engine)**:
- Cross-tier gossip (ally not in agent's neighborhood) gets higher noise
- `cross_tier_gossip_noise_multiplier` (2.0x) — information degrades faster

### Backward compatibility
`proximity_tiers_enabled=False` → all engines behave as before DD18.
Neighborhood lists stay empty, no tier weighting applied.

## Config parameters
- `proximity_tiers_enabled: bool = True`
- `household_interaction_multiplier: float = 4.0`
- `neighborhood_interaction_multiplier: float = 2.0`
- `neighborhood_size_max: int = 40`
- `neighborhood_refresh_interval: int = 3`
- `neighborhood_trust_threshold: float = 0.5`
- `band_mate_weight: float = 0.3`
- `cross_tier_gossip_noise_multiplier: float = 2.0`

## Metrics
- `avg_household_size`: mean household size across living agents
- `avg_neighborhood_size`: mean neighborhood size
- `cross_tier_conflict_rate`: fraction of conflicts between non-neighbors
- `local_mate_rate`: fraction of pair bonds formed within neighborhood
