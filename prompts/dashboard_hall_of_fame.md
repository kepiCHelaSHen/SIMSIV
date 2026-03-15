# SIMSIV — Dashboard: Hall of Fame Feature
# Prompt for Claude Code CLI
# File to edit: D:\EXPERIMENTS\SIM\dashboard\app.py

================================================================================
CONTEXT
================================================================================

You are working on the SIMSIV social simulation dashboard (Streamlit).
The file is D:\EXPERIMENTS\SIM\dashboard\app.py.

The Life Stories tab (tab_lives) currently shows:
  - A "Featured Lives" section with 3 randomly shuffled agent biography cards
  - A "View Any Agent" dropdown selector
  - Agent biographies are rendered via the existing `_render_biography(agent_id)` function

Your job is to ADD a "Hall of Fame" section to the Life Stories tab. Do not remove
or modify the existing "Featured Lives" or "View Any Agent" sections — just add
the Hall of Fame ABOVE them, separated by a divider.

Do not change any simulation logic, models, engines, or config files.
Only edit dashboard/app.py.

================================================================================
WHAT TO BUILD
================================================================================

Add a "🏆 Hall of Fame" section at the top of tab_lives, above the existing content.

The Hall of Fame surfaces the most extreme and interesting agents across 14 ranked
categories, grouped into 4 sections. Each category shows one agent card (using the
existing _render_biography() function) that is the most extreme example of that
category across ALL agents (living and dead) in society.agents.

Each category card should show:
  - The category name and icon as a header
  - The agent's name, sex, lifespan or current age, generation, faction
  - The specific metric that qualified them (e.g. "Lived 97 years" or "11 offspring")
  - A button "View Full Profile" that expands to show _render_biography() for that agent

================================================================================
THE 14 HALL OF FAME CATEGORIES
================================================================================

Implement a function `_compute_hall_of_fame(society)` that takes the society object
and returns a dict mapping category_key → agent_id (or None if no qualifying agent).

The function must search society.agents (all agents, living and dead) unless noted.

--- SECTION 1: LONGEVITY & SURVIVAL ---

  "oldest_ever"
    Title: "🧓 Oldest Ever"
    Caption: "Lived the longest of anyone in the simulation"
    Selection: agent with highest age (for living) or (year_of_death - birth_year)
               For dead agents: birth_year = year_of_death - age_at_death
               Use: max age among living + max (year_of_death - (year_of_death - age))
               Simpler: just use max(a.age for living) and max(a.age for dead at death)
               Track: "Lived {N} years" or "Currently age {N}"

  "died_youngest_adult"
    Title: "💀 Gone Too Soon"
    Caption: "Shortest adult life — died between age 18 and 40"
    Selection: among dead agents with cause_of_death not in ('childhood_mortality',
               'emigration') and age >= 18 and age <= 40, find minimum age at death
    Track: "Died age {N} from {cause}"

  "survived_most_epidemics"
    Title: "🦠 Epidemic Survivor"
    Caption: "Survived the most epidemic years while remaining alive"
    Selection: search medical_history for events containing 'epidemic', count per agent
               Use: len([e for e in a.medical_history if 'epidemic' in str(e).lower()])
               Pick highest count among all agents (living or dead)
    Track: "Survived {N} epidemic events"

--- SECTION 2: REPRODUCTION & FAMILY ---

  "most_offspring"
    Title: "👶 Most Prolific"
    Caption: "Most total offspring across entire lifetime"
    Selection: max len(a.offspring_ids) across all agents
    Track: "{N} total offspring"

  "zero_offspring_elder"
    Title: "🧘 The Celibate Elder"
    Caption: "Reached elder stage with zero lifetime offspring"
    Selection: among agents with age >= 55 (living) OR age_at_death >= 55 (dead),
               find those with lifetime_births == 0 and len(offspring_ids) == 0
               Pick oldest among qualifying agents
    Track: "Age {N}, no offspring"

  "deepest_lineage"
    Title: "🌳 Dynasty Founder"
    Caption: "Founding agent whose line reaches the deepest generation"
    Selection: for each generation-0 agent, find max generation among all descendants
               (use offspring_ids recursively, cap recursion at 20 levels)
               Pick the gen-0 agent whose descendant line reaches highest generation
    Track: "Line reaches generation {N}"

  "most_partners"
    Title: "💞 Most Bonded"
    Caption: "Formed the most pair bonds across a lifetime"
    Selection: max a.bond_count across living agents, or track via death_partner_ids
               For dead agents: len(a.death_partner_ids) if available, else bond_count
               For living agents: a.bond_count
    Track: "{N} pair bonds formed"

--- SECTION 3: STATUS & POWER ---

  "highest_prestige_ever"
    Title: "⭐ Most Prestigious"
    Caption: "Highest prestige score ever recorded"
    Selection: max a.prestige_score across all living agents
               (dead agents don't reliably retain this — living only)
    Track: "Prestige score {N:.3f}"

  "most_conflicts_won"
    Title: "⚔️ Warlord"
    Caption: "Highest dominance score among living agents"
    Selection: max a.dominance_score across living agents
    Track: "Dominance score {N:.3f}"

  "wealthiest_ever"
    Title: "💰 Wealthiest"
    Caption: "Highest combined resource wealth among living agents"
    Selection: max (a.current_resources + a.current_tools * 3 + a.current_prestige_goods * 5)
               among living agents (tools and prestige goods worth more)
    Track: "Total wealth {N:.1f}"

--- SECTION 4: EXTREME TRAITS ---

  "highest_psychopathy_survivor"
    Title: "🎭 The Predator"
    Caption: "Highest psychopathy tendency who survived to MATURE or ELDER stage"
    Selection: among all agents where life_stage in ('MATURE', 'ELDER') for living,
               or age_at_death >= 45 for dead,
               find max psychopathy_tendency
    Track: "Psychopathy {N:.3f}, survived to {life_stage}"

  "most_cooperative_survivor"
    Title: "🤝 The Peacekeeper"
    Caption: "Highest cooperation propensity who survived to old age (55+)"
    Selection: among living agents age >= 55 OR dead agents with age_at_death >= 55,
               find max cooperation_propensity
    Track: "Cooperation {N:.3f}, age {age}"

  "most_aggressive_long_lived"
    Title: "🔥 Aggression Paradox"
    Caption: "Highest aggression propensity who still lived past age 60"
    Selection: among living agents age > 60 OR dead agents age_at_death > 60,
               find max aggression_propensity
    Track: "Aggression {N:.3f}, lived to {age}"

  "most_faction_influence"
    Title: "👑 Faction Leader"
    Caption: "Agent who leads the largest active faction"
    Selection: look at society.faction_leaders dict for active factions
               find the faction with most members, get its war_leader or peace_chief
               Fall back to: agent with highest prestige in a faction if no leaders recorded
    Track: "Leads faction of {N} members"

================================================================================
IMPLEMENTATION RULES
================================================================================

1. Write `_compute_hall_of_fame(society)` as a standalone function near the top
   of the tab_lives section (or with other helper functions). It must be safe to
   call with an empty society (return all Nones).

2. Write `_render_hof_card(category_key, title, caption, agent_id, stat_line, society)`
   that renders a single compact Hall of Fame card using st.container() with a border.
   The card shows:
     - Title (bold, with icon)
     - Caption (st.caption)
     - Agent name + sex icon + key stat in a single line
     - An st.expander("View Full Profile") that calls _render_biography(agent_id)
   If agent_id is None, show st.info("No qualifying agent yet — run a longer simulation.")

3. Layout: display the 14 cards in a 2-column grid (st.columns(2)), grouped by section
   with a section header above each group:
     - "⏳ Longevity & Survival" (3 cards)
     - "👨‍👩‍👧‍👦 Reproduction & Family" (4 cards)
     - "👑 Status & Power" (3 cards)
     - "🧬 Extreme Traits" (4 cards)

4. Add a "🔄 Refresh Hall of Fame" button at the top that forces recomputation
   (use st.session_state to cache the result and invalidate on button press).
   Cache key: "hof_data" — store the result dict in session state so it doesn't
   recompute on every widget interaction.

5. Add a summary ribbon above the cards showing 4 quick stats pulled from the HOF data:
   - Oldest age recorded
   - Most offspring recorded
   - Highest prestige recorded
   - Deepest generation reached
   Use st.columns(4) with st.metric() for each.

6. Handle all edge cases silently:
   - society.agents is empty → all Nones, show info message
   - An agent_id from HOF computation is no longer in society.agents → show info
   - Any category with no qualifying agents → show info per card
   - Dead agents may have age = age at death (not current age) — use correctly

7. Preserve all existing tab_lives content below the Hall of Fame section.
   Insert the Hall of Fame ABOVE the existing st.subheader("Featured Lives") line.

================================================================================
VERIFICATION
================================================================================

After implementing:
1. Run: streamlit run dashboard/app.py
2. Run a simulation (any scenario, 100+ years)
3. Navigate to Life Stories tab
4. Confirm Hall of Fame section appears above Featured Lives
5. Confirm all 14 category cards render (some may show "no qualifying agent")
6. Confirm clicking "View Full Profile" expands the full biography
7. Confirm "Refresh Hall of Fame" button recomputes correctly
8. Confirm the existing Featured Lives and View Any Agent sections still work

================================================================================
END OF PROMPT
================================================================================
