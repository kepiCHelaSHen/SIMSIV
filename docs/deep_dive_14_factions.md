# SIMSIV — Deep Dive 14: In-Group Identity and Social Factions

## Design Decisions

### A. Faction Detection Algorithm
- Connected-component analysis on the **mutual** trust graph
- Edge exists when both agents trust each other above `faction_min_trust_threshold` (0.65)
- Components < `faction_min_size` (3) are factionless (faction_id = None)
- Detection runs every `faction_detection_interval` years (default 5) — not every tick
- BFS traversal: O(n + e) where e = number of trust edges above threshold
- Factions persist across detection cycles via majority-overlap matching (>30%)

### B. Leader-Based Merge (Political Alliance)
- After computing connected components, check existing faction leaders
- If two leaders from different components have mutual trust > `faction_merge_trust` (0.8),
  their components are merged before faction assignment
- Represents political alliance bringing separate groups together
- Natural connected-component merging also occurs when general trust links grow

### C. Faction Schism
- Components exceeding `faction_max_size` (50) face probabilistic schism
- Effective probability: 1 - (1 - schism_pressure)^interval per detection cycle
- Split algorithm: pick two seed agents (highest prestige, and most "distant" from seed1)
- Members assigned to whichever seed they trust more
- Sub-groups below min_size become factionless

### D. In-Group Preference Mechanics
All faction mechanics are SOFT modifiers, not absolute barriers:

1. **Resource sharing** (resources.py Phase 4):
   - Trust threshold reduced by `in_group_trust_threshold_reduction` (0.1) for same-faction
   - Sharing rate boosted by `in_group_sharing_bonus` (0.2) proportional to in-group allies
   - Result: faction members share more easily and more generously

2. **Conflict targeting** (conflict.py _select_target):
   - Out-group agents weighted `out_group_conflict_multiplier` (1.5x) in targeting
   - Result: violence directed outward toward other factions

3. **Mate preference** (mating.py _form_pairs):
   - Same-faction males get `endogamy_preference` (0.1) bonus in female choice
   - Result: mild in-group mating preference without preventing cross-faction pairing

### E. Faction Formation Drivers
Factions emerge naturally from existing trust mechanics:
- **Kinship** (DD02): parent-child trust bootstraps the core clusters
- **Sibling bonds** (DD06): co-living siblings build mutual trust
- **Cooperation networks** (DD02/DD04): sharing strengthens trust (amplifying loop)
- **Gossip** (DD07): trust information spreads through existing clusters
- **Coalition defense** (DD11): defending each other builds deep in-group trust
- No explicit "faction assignment" — detection only observes emergent clusters

### F. Faction Lifecycle
- **Formation**: year 6-10 in typical runs (kin clusters reach threshold density)
- **Growth**: successful factions attract more trust links over time
- **Consolidation**: factions merge as inter-faction trust grows (natural or leader-mediated)
- **Schism**: large factions probabilistically split (prevents mega-factions)
- **Dissolution**: factions with members dying/dispersing below min_size are dissolved

### G. What's NOT Implemented
- Territory (v2 feature — factions are within-population only)
- Faction leadership effects (leader doesn't confer special benefits to members)
- Elite capture (highest-status member getting institutional advantages)
- Faction-level inheritance or prestige
- Faction-specific norms or enforcement
- Inter-faction raiding or warfare (v2)

### H. V2 Preparation
The faction system is designed as foundation for multi-tribe dynamics:
- `faction_id` on agents generalizes to tribal membership
- Faction detection algorithm generalizes to territory-based assignment
- Out-group conflict mechanics generalize to inter-tribe raiding
- Faction leadership generalizes to political authority
- In-group sharing generalizes to tribal economy

## Parameters Added
| Parameter | Default | Description |
|-----------|---------|-------------|
| factions_enabled | True | Enable faction detection and mechanics |
| faction_detection_interval | 5 | Years between faction recomputation |
| faction_min_trust_threshold | 0.65 | Mutual trust required for same faction |
| faction_min_size | 3 | Minimum viable faction size |
| faction_max_size | 50 | Schism pressure above this (Dunbar-inspired) |
| in_group_sharing_bonus | 0.2 | Sharing rate boost for in-group allies |
| in_group_trust_threshold_reduction | 0.1 | Lower trust needed for in-group sharing |
| out_group_conflict_multiplier | 1.5 | Inter-faction conflict targeting boost |
| endogamy_preference | 0.1 | Same-faction mate value boost |
| faction_schism_pressure | 0.01 | Annual schism probability above max_size |
| faction_merge_trust | 0.8 | Inter-leader trust required for faction merge |

## Metrics Added
| Metric | Description |
|--------|-------------|
| faction_count | Number of active factions (from living agent faction_ids) |
| largest_faction_size | Biggest faction's living member count |
| faction_size_gini | Inequality between faction sizes |
| faction_stability | Average age of active factions (years since formation) |
| inter_faction_conflict_rate | Fraction of conflicts between different factions |
| factionless_fraction | Fraction of population not in any faction |

## Files Changed
- `models/agent.py` — faction_id field
- `models/society.py` — detect_factions method, faction tracking state
- `simulation.py` — wired faction detection (phase 8.5)
- `engines/resources.py` — in-group sharing bonus + lower trust threshold
- `engines/conflict.py` — out-group targeting preference
- `engines/mating.py` — endogamy preference
- `config.py` — 11 DD14 parameters
- `metrics/collectors.py` — 6 DD14 metrics
