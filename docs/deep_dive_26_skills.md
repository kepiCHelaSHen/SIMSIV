# Deep Dive 26: Skill Acquisition and Cultural Knowledge

## Design Decisions

### Four skill domains (non-heritable, experience-acquired)
Each agent holds 4 skill values [0.0-1.0]:
- **foraging_skill**: resource extraction efficiency, route knowledge
- **combat_skill**: fighting technique, tactical awareness
- **social_skill**: negotiation, alliance building, social reading
- **craft_skill**: tool-making, material processing (only if DD21 resource_types enabled)

### Skill initialization at maturation (age 15)
- Base: `intelligence_proxy * 0.2` (genetic head start)
- Parent transmission: `parent_skill * transmission_fraction * 0.5` per living parent
- `conformity_bias` increases transmission fraction (0.8 + cb * 0.4)

### Skill acquisition mechanics
Skills grow through successful exercise:

**Foraging**: grows when agent's resources > band_average * 1.1
- Rate: `lr * (1 - skill * 0.8)` (diminishing returns)
- Intelligence accelerates: `* (0.7 + intel * 0.6)`

**Combat**: grows from conflict outcomes
- Win: `+0.02 * max(0.1, opponent_skill - own_skill + 0.3)` (learn more from skilled opponents)
- Loss: `+0.005` (learn from defeat, but less)

**Social**: grows from cooperation and relationships
- Active allies > 2: `+lr * 0.5` (emotional_intelligence accelerates)
- Being bonded: `+lr * 0.3`

**Craft**: grows from tool possession/production
- Having tools: `+lr * (1 - skill * 0.8)` (intelligence accelerates)

### Skill decay
- Foraging: 0.02/yr baseline
- Combat: 0.03/yr baseline
- Social: 0.01/yr (nearly permanent)
- Craft: 0.02/yr

### Skill effects on engines

**Resources**: `effective_intelligence = intel * (0.6 + foraging_skill * 0.8)` in competitive weight. Craft skill: `tool_production *= (0.5 + craft_skill * 1.0)`.

**Conflict**: `combat_power += combat_skill * combat_skill_weight (0.15)`.

**Reputation**: Social skill boosts gossip effectiveness: `* (0.9 + social_skill * 0.2)`.

**Mating**: Social skill sharpens female character assessment: `* (1.0 + social_skill * 0.2)`.

### Mentoring within factions
- Mentor (skill > 0.6) → apprentice (skill < 0.4): transfer = mentor_skill * 0.05/yr
- Elder teaching: elders with social_skill > 0.5 transfer +0.03/yr to faction youth
- Age learning decline starts at 45: `max(0.3, 1 - (age-45) * 0.03)`

## Config parameters
11 new parameters controlling skill dynamics.

## Metrics
- `avg_foraging_skill`, `avg_combat_skill`, `avg_social_skill`, `avg_craft_skill`
- `*_skill_gini` (4 domain inequality measures)
- `skill_age_correlation`: correlation between age and social skill
- `mentor_events`: count per tick
- `specialist_count`: agents with any skill > 0.7
