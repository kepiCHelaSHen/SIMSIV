"""Life Stories tab — Hall of Fame + Agent biographies."""

import streamlit as st
import numpy as np

from models.agent import HERITABLE_TRAITS
from data.names import namer
from dashboard.components.constants import TRAIT_ABBREV, TRAIT_DOMAINS


# ── Domain sets for trait icon mapping ──────────────────────────────
_physical = TRAIT_DOMAINS["physical"]
_cognitive = TRAIT_DOMAINS["cognitive"]
_temporal = TRAIT_DOMAINS["temporal"]
_personality = TRAIT_DOMAINS["personality"]
_social = TRAIT_DOMAINS["social"]
_reproductive = TRAIT_DOMAINS["reproductive"]
_psychopath = TRAIT_DOMAINS["psychopathology"]


# ── Helpers ─────────────────────────────────────────────────────────

def _get_agent_name(agent_id, society, agent=None):
    """Get full name for an agent, caching in session state."""
    cache = st.session_state.setdefault("agent_names", {})
    if agent_id not in cache:
        sex = "male"
        if agent:
            sex = agent.sex.value if hasattr(agent.sex, "value") else str(agent.sex)
        else:
            a = society.get_by_id(agent_id)
            if a:
                sex = a.sex.value if hasattr(a.sex, "value") else str(a.sex)
        cache[agent_id] = namer.get_full_name(agent_id, sex=sex)
    return cache[agent_id]


def _render_biography(agent_id, society, sim_events):
    """Render a rich biography card for an agent using Streamlit components."""
    a = society.get_by_id(agent_id)
    if not a:
        st.warning(f"Agent {agent_id} not found.")
        return

    name = _get_agent_name(agent_id, society, a)
    sex_str = a.sex.value.capitalize()
    sex_icon = "\u2640" if a.sex.value == "female" else "\u2642"

    if a.alive:
        birth_year = max(1, society.year - a.age)
        status_line = f"Born Year {birth_year} \u00b7 Age {a.age} \u00b7 Still Alive"
        status_icon = "\U0001f7e2"
    else:
        birth_year = (a.year_of_death - a.age) if a.year_of_death else "?"
        cause = a.cause_of_death or "unknown"
        status_line = f"Born Year {birth_year} \u00b7 Died Year {a.year_of_death} \u00b7 {cause}"
        status_icon = "\U0001f480"

    p1, p2 = a.parent_ids
    p1_name = _get_agent_name(p1, society) if p1 is not None else "Unknown"
    p2_name = _get_agent_name(p2, society) if p2 is not None else "Unknown"
    parents_str = f"{p1_name} \u00d7 {p2_name}" if (p1 is not None or p2 is not None) else "Unknown (Founder)"

    child_names = []
    for cid in list(a.offspring_ids)[:5]:
        child = society.get_by_id(cid)
        if child:
            child_names.append(_get_agent_name(cid, society, child))
    children_str = ", ".join(child_names) if child_names else "None"
    if len(a.offspring_ids) > 5:
        children_str += f" (+{len(a.offspring_ids) - 5} more)"

    trait_vals = [(t, getattr(a, t, 0.5)) for t in HERITABLE_TRAITS]
    trait_vals.sort(key=lambda x: x[1], reverse=True)
    top5 = trait_vals[:5]
    bottom3 = trait_vals[-3:]

    blocks = "\u2581\u2582\u2583\u2584\u2585\u2586\u2587\u2588"

    def _bar(val):
        idx = min(int(val * len(blocks)), len(blocks) - 1)
        return blocks[idx]

    agent_events = [e for e in sim_events if agent_id in e.get("agent_ids", [])]
    agent_events.sort(key=lambda e: e.get("year", 0))

    event_icons = {
        "birth": "\U0001f476", "death": "\U0001f480", "pair_bond_formed": "\U0001f491",
        "bond_dissolved": "\U0001f494", "conflict": "\u2694\ufe0f",
        "epc_occurred": "\U0001f48b", "epc_detected": "\U0001f440",
        "mating_contest": "\U0001f94a", "flee": "\U0001f3c3",
        "punishment": "\u2696\ufe0f", "inheritance": "\U0001f4b0",
        "institution_emerged": "\U0001f3db\ufe0f", "maturation": "\U0001f331",
        "childhood_death": "\U0001f622", "infant_death": "\U0001f622",
    }

    def _format_event(e):
        etype = e.get("type", "")
        yr = e.get("year", "?")
        desc = e.get("description", "")
        icon = event_icons.get(etype, "\u00b7")
        if desc:
            return f"**Yr {yr}** {icon} {desc}"
        return f"**Yr {yr}** {icon} {etype.replace('_', ' ').title()}"

    partner_names = []
    for pid in a.partner_ids:
        partner = society.get_by_id(pid)
        if partner:
            partner_names.append(_get_agent_name(pid, society, partner))

    faction_str = f"Faction {a.faction_id}" if a.faction_id is not None else "No faction"
    conditions_str = ", ".join(a.active_conditions) if a.active_conditions else "None"
    life_stage = getattr(a, "life_stage", "Unknown")

    with st.container(border=True):
        st.markdown(f"## {sex_icon} {name}")
        st.markdown(f"{status_icon} {status_line}")
        st.markdown(f"*{sex_str} \u00b7 Generation {a.generation} \u00b7 {life_stage} \u00b7 {faction_str}*")
        st.markdown("---")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**\U0001f9ec Lineage**")
            st.markdown(f"Parents: {parents_str}")
            st.markdown(f"Children ({len(a.offspring_ids)}): {children_str}")
            if partner_names:
                st.markdown(f"Partner(s): {', '.join(partner_names)}")
            st.markdown("")
            st.markdown("**\U0001f4ca Status**")
            st.markdown(f"Reputation: {a.reputation:.2f} \u00b7 Health: {a.health:.2f}")
            st.markdown(f"Resources: {a.current_resources:.1f} \u00b7 Trauma: {a.trauma_score:.2f}")
            if conditions_str != "None":
                st.markdown(f"\u2695\ufe0f Conditions: {conditions_str}")

        with col2:
            st.markdown("**\U0001f4aa Dominant Traits**")
            for t, v in top5:
                bar = _bar(v)
                d_icon = "\u26aa"
                if t in _physical:
                    d_icon = "\U0001f7e0"
                elif t in _cognitive:
                    d_icon = "\U0001f535"
                elif t in _temporal:
                    d_icon = "\U0001f7e1"
                elif t in _personality:
                    d_icon = "\U0001f7e3"
                elif t in _social:
                    d_icon = "\U0001f7e2"
                elif t in _reproductive:
                    d_icon = "\U0001fa77"
                elif t in _psychopath:
                    d_icon = "\U0001f534"
                st.markdown(f"{d_icon} {TRAIT_ABBREV.get(t, t)}: **{v:.2f}** {bar}")
            st.markdown("")
            st.markdown("**\U0001f4c9 Weakest Traits**")
            for t, v in bottom3:
                st.markdown(f"\u00b7 {TRAIT_ABBREV.get(t, t)}: {v:.2f} {_bar(v)}")

        st.markdown("---")
        st.markdown("**\U0001f4d6 Life Events**")
        if agent_events:
            sig_events = [e for e in agent_events
                          if e.get("type", "") not in ("resource_transfers",)]
            display_events = sig_events[:20] if len(sig_events) > 5 else agent_events[:20]
            for e in display_events:
                st.markdown(_format_event(e))
            if len(agent_events) > 20:
                st.caption(f"... and {len(agent_events) - 20} more events")
        else:
            st.markdown("*No recorded events*")

        st.markdown("---")
        st.markdown("**\U0001f6e0 Skills**")
        sk1, sk2, sk3, sk4 = st.columns(4)
        sk1.metric("Foraging", f"{getattr(a, 'foraging_skill', 0):.2f}")
        sk2.metric("Combat", f"{getattr(a, 'combat_skill', 0):.2f}")
        sk3.metric("Social", f"{getattr(a, 'social_skill', 0):.2f}")
        sk4.metric("Craft", f"{getattr(a, 'craft_skill', 0):.2f}")


def _compute_hall_of_fame(society):
    """Compute the 14 Hall of Fame categories. Returns dict of category_key -> (agent_id, stat_line)."""
    agents = society.agents
    if not agents:
        return {k: (None, "") for k in [
            "oldest_ever", "died_youngest_adult", "survived_most_epidemics",
            "most_offspring", "zero_offspring_elder", "deepest_lineage", "most_partners",
            "highest_prestige_ever", "most_conflicts_won", "wealthiest_ever",
            "highest_psychopathy_survivor", "most_cooperative_survivor",
            "most_aggressive_long_lived", "most_faction_influence",
        ]}

    all_agents = list(agents.values())
    living = [a for a in all_agents if a.alive]
    dead = [a for a in all_agents if not a.alive]
    result = {}

    # Oldest ever
    best_id, best_age = None, 0
    for a in all_agents:
        age = a.age
        if age > best_age:
            best_age, best_id = age, a.id
    stat = f"Currently age {best_age}" if (agents.get(best_id) and agents[best_id].alive) else f"Lived {best_age} years"
    result["oldest_ever"] = (best_id, stat)

    # Gone Too Soon
    best_id, best_age = None, 999
    for a in dead:
        if a.cause_of_death in ("childhood_mortality", "emigration"):
            continue
        if 18 <= a.age <= 40 and a.age < best_age:
            best_age, best_id = a.age, a.id
    result["died_youngest_adult"] = (best_id, f"Died age {best_age} from {agents[best_id].cause_of_death}" if best_id else "")

    # Epidemic Survivor
    best_id, best_count = None, 0
    for a in all_agents:
        count = len([e for e in a.medical_history if "epidemic" in str(e).lower()])
        if count > best_count:
            best_count, best_id = count, a.id
    result["survived_most_epidemics"] = (best_id if best_count > 0 else None,
                                          f"Survived {best_count} epidemic events" if best_count > 0 else "")

    # Most Prolific
    best_id, best_n = None, 0
    for a in all_agents:
        n = len(a.offspring_ids)
        if n > best_n:
            best_n, best_id = n, a.id
    result["most_offspring"] = (best_id, f"{best_n} total offspring")

    # Celibate Elder
    best_id, best_age = None, 0
    for a in all_agents:
        age = a.age
        if age >= 55 and a.lifetime_births == 0 and len(a.offspring_ids) == 0:
            if age > best_age:
                best_age, best_id = age, a.id
    result["zero_offspring_elder"] = (best_id, f"Age {best_age}, no offspring" if best_id else "")

    # Deepest Lineage
    def _max_gen(aid, depth=0):
        if depth > 20:
            return 0
        a = agents.get(aid)
        if not a or not a.offspring_ids:
            return a.generation if a else 0
        return max((_max_gen(oid, depth + 1) for oid in a.offspring_ids), default=0)

    founders = [a for a in all_agents if a.generation == 0 and a.offspring_ids]
    best_id, best_gen = None, 0
    for f in founders:
        mg = _max_gen(f.id)
        if mg > best_gen:
            best_gen, best_id = mg, f.id
    result["deepest_lineage"] = (best_id, f"Line reaches generation {best_gen}" if best_id else "")

    # Most Partners
    best_id, best_n = None, 0
    for a in all_agents:
        n = a.bond_count if a.alive else len(a.death_partner_ids)
        if n > best_n:
            best_n, best_id = n, a.id
    result["most_partners"] = (best_id, f"{best_n} pair bonds" if best_n > 0 else "")

    # Highest Prestige
    best_id, best_v = None, 0
    for a in living:
        if a.prestige_score > best_v:
            best_v, best_id = a.prestige_score, a.id
    result["highest_prestige_ever"] = (best_id, f"Prestige score {best_v:.3f}" if best_id else "")

    # Warlord (dominance)
    best_id, best_v = None, 0
    for a in living:
        if a.dominance_score > best_v:
            best_v, best_id = a.dominance_score, a.id
    result["most_conflicts_won"] = (best_id, f"Dominance score {best_v:.3f}" if best_id else "")

    # Wealthiest
    best_id, best_v = None, 0
    for a in living:
        wealth = a.current_resources + a.current_tools * 3 + a.current_prestige_goods * 5
        if wealth > best_v:
            best_v, best_id = wealth, a.id
    result["wealthiest_ever"] = (best_id, f"Total wealth {best_v:.1f}" if best_id else "")

    # The Predator (psychopathy survivor)
    best_id, best_v = None, 0
    best_stage = ""
    for a in all_agents:
        eligible = (a.alive and a.life_stage in ("MATURE", "ELDER")) or (not a.alive and a.age >= 45)
        if eligible and a.psychopathy_tendency > best_v:
            best_v, best_id = a.psychopathy_tendency, a.id
            best_stage = a.life_stage if a.alive else f"died age {a.age}"
    result["highest_psychopathy_survivor"] = (best_id,
        f"Psychopathy {best_v:.3f}, {best_stage}" if best_id else "")

    # The Peacekeeper
    best_id, best_v = None, 0
    for a in all_agents:
        eligible = (a.alive and a.age >= 55) or (not a.alive and a.age >= 55)
        if eligible and a.cooperation_propensity > best_v:
            best_v, best_id = a.cooperation_propensity, a.id
    result["most_cooperative_survivor"] = (best_id,
        f"Cooperation {best_v:.3f}, age {agents[best_id].age}" if best_id else "")

    # Aggression Paradox
    best_id, best_v = None, 0
    for a in all_agents:
        eligible = (a.alive and a.age > 60) or (not a.alive and a.age > 60)
        if eligible and a.aggression_propensity > best_v:
            best_v, best_id = a.aggression_propensity, a.id
    result["most_aggressive_long_lived"] = (best_id,
        f"Aggression {best_v:.3f}, lived to {agents[best_id].age}" if best_id else "")

    # Faction Leader
    best_id, best_n = None, 0
    faction_sizes = {}
    for a in living:
        if a.faction_id is not None:
            faction_sizes[a.faction_id] = faction_sizes.get(a.faction_id, 0) + 1
    if faction_sizes:
        largest_fid = max(faction_sizes, key=faction_sizes.get)
        largest_n = faction_sizes[largest_fid]
        # Try faction_leaders
        leaders = getattr(society, "faction_leaders", {}).get(largest_fid, {})
        leader_id = leaders.get("war_leader") or leaders.get("peace_chief")
        if leader_id and agents.get(leader_id):
            best_id, best_n = leader_id, largest_n
        else:
            # Fallback: highest prestige in faction
            faction_agents = [a for a in living if a.faction_id == largest_fid]
            if faction_agents:
                top = max(faction_agents, key=lambda a: a.prestige_score)
                best_id, best_n = top.id, largest_n
    result["most_faction_influence"] = (best_id, f"Leads faction of {best_n} members" if best_id else "")

    return result


def _render_hof_card(title, caption, agent_id, stat_line, society, sim_events):
    """Render a single compact Hall of Fame card."""
    with st.container(border=True):
        st.markdown(f"**{title}**")
        st.caption(caption)
        if agent_id is None:
            st.info("No qualifying agent yet \u2014 run a longer simulation.")
            return
        a = society.get_by_id(agent_id)
        if not a:
            st.info("Agent no longer in simulation data.")
            return
        name = _get_agent_name(agent_id, society, a)
        sex_icon = "\u2640" if a.sex.value == "female" else "\u2642"
        st.markdown(f"{sex_icon} **{name}** \u2014 {stat_line}")
        with st.expander("View Full Profile"):
            _render_biography(agent_id, society, sim_events)


# ── Main render ─────────────────────────────────────────────────────

def render(df, df_std, living, society, config, sim_events, is_multi_run, seeds_count=1, **kwargs):
    """Render the Life Stories tab."""
    if df is None or len(df) == 0:
        st.info("Run a simulation first.")
        return

    # -- Hall of Fame --
    st.header("\U0001f3c6 Hall of Fame")

    col_hof_title, col_hof_btn = st.columns([4, 1])
    with col_hof_btn:
        if st.button("\U0001f504 Refresh", key="refresh_hof"):
            st.session_state.pop("hof_data", None)

    if "hof_data" not in st.session_state:
        st.session_state["hof_data"] = _compute_hall_of_fame(society)
    hof = st.session_state["hof_data"]

    # Summary ribbon
    c1, c2, c3, c4 = st.columns(4)
    oldest = hof.get("oldest_ever", (None, ""))
    most_off = hof.get("most_offspring", (None, ""))
    prestige = hof.get("highest_prestige_ever", (None, ""))
    lineage = hof.get("deepest_lineage", (None, ""))
    c1.metric("Oldest Age", oldest[1].split()[-1] if oldest[0] else "\u2014")
    c2.metric("Most Offspring", most_off[1].split()[0] if most_off[0] else "\u2014")
    c3.metric("Top Prestige", prestige[1].split()[-1] if prestige[0] else "\u2014")
    c4.metric("Deepest Gen", lineage[1].split()[-1] if lineage[0] else "\u2014")

    # Category definitions
    HOF_CATEGORIES = [
        ("\u23f3 Longevity & Survival", [
            ("oldest_ever", "\U0001f9d3 Oldest Ever", "Lived the longest of anyone in the simulation"),
            ("died_youngest_adult", "\U0001f480 Gone Too Soon", "Shortest adult life \u2014 died between age 18 and 40"),
            ("survived_most_epidemics", "\U0001f9a0 Epidemic Survivor", "Survived the most epidemic years"),
        ]),
        ("\U0001f468\u200d\U0001f469\u200d\U0001f467\u200d\U0001f466 Reproduction & Family", [
            ("most_offspring", "\U0001f476 Most Prolific", "Most total offspring across entire lifetime"),
            ("zero_offspring_elder", "\U0001f9d8 The Celibate Elder", "Reached elder stage with zero offspring"),
            ("deepest_lineage", "\U0001f333 Dynasty Founder", "Founding agent whose line reaches the deepest generation"),
            ("most_partners", "\U0001f49e Most Bonded", "Formed the most pair bonds across a lifetime"),
        ]),
        ("\U0001f451 Status & Power", [
            ("highest_prestige_ever", "\u2b50 Most Prestigious", "Highest prestige score ever recorded"),
            ("most_conflicts_won", "\u2694\ufe0f Warlord", "Highest dominance score among living agents"),
            ("wealthiest_ever", "\U0001f4b0 Wealthiest", "Highest combined resource wealth"),
        ]),
        ("\U0001f9ec Extreme Traits", [
            ("highest_psychopathy_survivor", "\U0001f3ad The Predator", "Highest psychopathy who survived to maturity"),
            ("most_cooperative_survivor", "\U0001f91d The Peacekeeper", "Highest cooperation who survived to old age"),
            ("most_aggressive_long_lived", "\U0001f525 Aggression Paradox", "Highest aggression who still lived past 60"),
            ("most_faction_influence", "\U0001f451 Faction Leader", "Agent who leads the largest active faction"),
        ]),
    ]

    for section_title, categories in HOF_CATEGORIES:
        st.subheader(section_title)
        cols = st.columns(2)
        for i, (key, title, caption) in enumerate(categories):
            aid, stat = hof.get(key, (None, ""))
            with cols[i % 2]:
                _render_hof_card(title, caption, aid, stat, society, sim_events)

    st.markdown("---")

    # -- Featured Lives --
    st.subheader("Featured Lives")

    all_agents = list(society.agents.values())
    all_ids = [a.id for a in all_agents]

    # Shuffle button updates the seed for featured agents
    col_title, col_shuffle = st.columns([4, 1])
    with col_shuffle:
        if st.button("Shuffle", key="shuffle_featured"):
            st.session_state["featured_seed"] = st.session_state.get("featured_seed", 42) + 1

    feat_seed = st.session_state.get("featured_seed", 42)
    rng_feat = np.random.default_rng(feat_seed)
    featured_ids = list(rng_feat.choice(all_ids, size=min(3, len(all_ids)), replace=False))

    cols = st.columns(3)
    for i, aid in enumerate(featured_ids):
        with cols[i]:
            _render_biography(int(aid), society, sim_events)

    st.markdown("---")
    st.subheader("View Any Agent")

    col_sel, col_btn = st.columns([3, 1])
    with col_sel:
        selected_id = st.selectbox(
            "Select agent ID",
            sorted(all_ids),
            format_func=lambda x: f"{x} \u2014 {_get_agent_name(x, society)}",
            key="life_story_select",
        )
    with col_btn:
        if st.button("Random Agent", key="random_agent_btn"):
            selected_id = int(np.random.default_rng().choice(all_ids))

    if selected_id:
        _render_biography(int(selected_id), society, sim_events)
