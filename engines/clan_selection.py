"""
clan_selection.py — Between-group (Bowles/Gintis) selection engine (SIMSIV v2, Turn 4).

This engine implements the core Bowles & Gintis (2004, 2011) between-group
selection mechanism: competition between bands (via raiding and differential
growth) can select for heritable prosocial traits (cooperation_propensity,
group_loyalty) even when those traits are individually costly.

Public interface
----------------
    selection_tick(clan_society, year, rng, config, clan_config) -> list[dict]

Three coupled mechanisms
------------------------

1. Within-group selection coefficient
   For each band, estimate the selection coefficient on prosocial traits:
   positive when high-cooperation agents have MORE offspring/survive better
   than band mean; negative when cooperators are exploited (defectors prosper).
   Computed as Pearson r(trait, fitness_proxy) across living adults.
   Output key: within_group_selection_coeff (mean across all bands)

2. Between-group selection coefficient
   Across bands, do bands with higher mean prosocial traits grow faster
   (positive delta-population) or win more raids?  Computed as Pearson
   r(band_mean_prosocial, band_fitness_proxy) across all active bands.
   Output key: between_group_selection_coeff

3. Demographic events (fission, extinction, migration)

   a) Band fission:
      When a band exceeds fission_threshold (default 150 agents, Dunbar 1992),
      it splits into two daughter bands.  Agents are randomly split but the
      rng introduces a founder effect: each daughter band inherits a random
      subsample of agents.  The two daughters get IDs = max_existing_id + 1
      and max_existing_id + 2.

   b) Band extinction:
      When a band drops below extinction_threshold (default 10 agents),
      it is absorbed by the nearest band (lowest distance in distance_matrix).
      Refugees join the absorbing band, carrying their traits, increasing
      gene flow (reducing Fst between absorbing and extinct band).

   c) Inter-band migration (gene flow):
      Each tick, a small number of agents (controlled by
      migration_rate_per_agent) migrate from one band to another.
      Migrants carry all their heritable traits.  This force opposes
      between-group selection by reducing Fst.  Migration probability is
      inversely proportional to distance and proportional to trust.

Architecture rules obeyed
--------------------------
- No print() statements.  Uses logging.getLogger(__name__).
- All randomness via the seeded rng parameter.  No np.random calls.
- No imports from models.society or simulation.
- Models know nothing about this engine.
- No circular imports.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from models.clan.clan_society import ClanSociety
    from config import Config
    from models.clan.clan_config import ClanConfig

_log = logging.getLogger(__name__)

# ── Module-level constants (defaults for when ClanConfig doesn't have the key) ─

_DEFAULT_FISSION_THRESHOLD: int = 150
_DEFAULT_EXTINCTION_THRESHOLD: int = 10
_DEFAULT_MIGRATION_RATE_PER_AGENT: float = 0.005  # ~0.5% annual migration
_DEFAULT_FISSION_FOUNDER_NOISE: float = 0.02       # sd of noise on founder trait means

# Prosocial traits used for selection coefficient computation
_PROSOCIAL_TRAITS: tuple[str, ...] = (
    "cooperation_propensity",
    "group_loyalty",
    "outgroup_tolerance",
    "empathy_capacity",
)

# Fitness proxies used for within-group selection coefficient
# offspring_ids count + survival weight (not dying this year)
_MIN_BAND_COUNT_FOR_BETWEEN: int = 2  # need at least 2 bands for between-group stats


# ── Public API ────────────────────────────────────────────────────────────────

def selection_tick(
    clan_society: "ClanSociety",
    year: int,
    rng: np.random.Generator,
    config: "Config",
    clan_config: "ClanConfig | None" = None,
    prev_populations: dict[int, int] | None = None,
) -> list[dict]:
    """Run one year of between-group and within-group selection.

    Parameters
    ----------
    clan_society:
        The multi-band registry.  This function may add and remove bands.
    year:
        Current simulation year.
    rng:
        Seeded numpy.random.Generator.  All randomness goes through this.
    config:
        Shared v1 simulation config.
    clan_config:
        Optional v2 ClanConfig.  Provides fission_threshold, etc.
        Falls back to module-level defaults when None or attribute absent.
    prev_populations:
        Optional dict {band_id: population_count} from the previous tick.
        When provided, _compute_between_group_selection uses population
        growth rate as the fitness proxy (Bowles 2006, Price equation).
        When None, falls back to population level (less accurate but
        backward compatible).

    Returns
    -------
    list of event dicts describing demographic events (fission, extinction,
    migration).  Also returns within and between selection coefficients as
    metadata in a synthetic "selection_stats" event at index 0.
    """
    events: list[dict] = []

    # ── Step 1: Compute within-group selection coefficients ───────────────────
    within_coeff = _compute_within_group_selection(clan_society)

    # ── Step 2: Compute between-group selection coefficients ─────────────────
    # Returns two separate coefficients: demographic (Price equation) and raid.
    demographic_coeff, raid_coeff = _compute_between_group_selection(
        clan_society, prev_populations
    )
    # Legacy key: mean of the two for backward compatibility with tests that
    # read "between_group_selection_coeff".  New code should use the split keys.
    between_coeff = (demographic_coeff + raid_coeff) / 2.0

    # Emit a stats event so callers can extract the coefficients without
    # re-running the computation.
    stats_event: dict = {
        "type": "selection_stats",
        "year": year,
        "agent_ids": [],
        "description": (
            f"Year {year} selection: within={within_coeff:.4f}, "
            f"demo={demographic_coeff:.4f}, raid={raid_coeff:.4f}"
        ),
        "outcome": "computed",
        "within_group_selection_coeff": within_coeff,
        "between_group_selection_coeff": between_coeff,
        "demographic_selection_coeff": demographic_coeff,
        "raid_selection_coeff": raid_coeff,
    }
    events.append(stats_event)

    _log.debug(
        "selection_tick year=%d: within=%.4f, demo=%.4f, raid=%.4f",
        year, within_coeff, demographic_coeff, raid_coeff,
    )

    # ── Step 3: Inter-band migration (gene flow) ───────────────────────────────
    migration_events = _process_migration(clan_society, year, rng, config, clan_config)
    events.extend(migration_events)

    # ── Step 4: Band fission (oversized bands split) ───────────────────────────
    fission_events = _process_fission(clan_society, year, rng, config, clan_config)
    events.extend(fission_events)

    # ── Step 5: Band extinction (tiny bands absorbed) ─────────────────────────
    # Run after fission so that a band that fissions doesn't immediately become
    # an extinction candidate.
    extinction_events = _process_extinction(clan_society, year, rng, config, clan_config)
    events.extend(extinction_events)

    return events


# ── Within-group selection ─────────────────────────────────────────────────────

def _compute_within_group_selection(clan_society: "ClanSociety") -> float:
    """Estimate mean within-group selection coefficient across all bands.

    Within-group selection coefficient for a trait = Pearson r between the
    trait value and a fitness proxy, computed across living adults in each band.
    A positive coefficient means high-trait agents reproduce/survive better.

    Fitness proxy per agent:
        fitness_proxy = 0.5 * (offspring_count / max_offspring_in_band)
                      + 0.5 * (health / 1.0)

    The two components are weighted equally:
    - offspring_count captures realized reproductive success.
    - health captures survival prospects (higher health → survive longer).

    Returns the mean coefficient across all bands and all prosocial traits.
    Returns 0.0 if no band has enough adults to compute a correlation.
    """
    coefficients: list[float] = []

    for bid, band in clan_society.bands.items():
        living = band.get_living()
        # Filter to PRIME and MATURE only — ELDERs are post-reproductive and
        # their inclusion dilutes the within-group selection signal.
        # (Turn 4 critic warning; fixed Turn 5 following Grok council review.)
        adults = [
            a for a in living
            if a.life_stage in ("PRIME", "MATURE") and a.age >= 15
        ]
        if len(adults) < 5:
            continue

        # Build fitness proxy vector
        offspring_counts = np.array(
            [float(len(a.offspring_ids)) for a in adults], dtype=float
        )
        max_off = max(offspring_counts.max(), 1.0)
        health_vals = np.array([a.health for a in adults], dtype=float)
        fitness_proxy = 0.5 * (offspring_counts / max_off) + 0.5 * health_vals

        fp_std = fitness_proxy.std()
        if fp_std < 1e-8:
            continue  # no fitness variance — skip

        for trait in _PROSOCIAL_TRAITS:
            trait_vals = np.array([getattr(a, trait) for a in adults], dtype=float)
            t_std = trait_vals.std()
            if t_std < 1e-8:
                continue  # no trait variance in this band — skip
            r = float(np.corrcoef(trait_vals, fitness_proxy)[0, 1])
            if np.isfinite(r):
                coefficients.append(r)

    if not coefficients:
        return 0.0

    return float(np.mean(coefficients))


# ── Between-group selection ────────────────────────────────────────────────────

def _compute_between_group_selection(
    clan_society: "ClanSociety",
    prev_populations: dict[int, int] | None = None,
) -> tuple[float, float]:
    """Estimate between-group selection coefficients (demographic + raid).

    Returns TWO separate coefficients rather than a blended composite:

    1. demographic_selection_coeff: Pearson r between band mean prosocial
       trait and Malthusian growth rate r = ln(N_t / N_{t-1}).
       This IS the Price equation fitness measure (Price 1970; Bowles 2006
       eq. 1). Positive = prosocial bands grow faster.

    2. raid_selection_coeff: Pearson r between band mean prosocial trait
       and raid win rate (wins / total raids in recent event window).
       Positive = prosocial bands win more raids (Bowles coalition defence).

    Previously these were blended 0.6/0.4 into a single coefficient.
    That blend was uncited and not comparable to the Bowles (2006) empirical
    estimates. Splitting them makes each coefficient independently
    interpretable against the literature.

    Returns (0.0, 0.0) if fewer than _MIN_BAND_COUNT_FOR_BETWEEN bands exist.
    """
    active_bands = [
        (bid, band) for bid, band in clan_society.bands.items()
        if band.population_size() > 0
    ]
    if len(active_bands) < _MIN_BAND_COUNT_FOR_BETWEEN:
        return 0.0, 0.0

    band_ids = [x[0] for x in active_bands]
    bands = [x[1] for x in active_bands]

    pop_sizes = np.array([b.population_size() for b in bands], dtype=float)

    # ── Demographic fitness: Malthusian parameter r = ln(N_t / N_{t-1}) ──
    # This is the natural measure of fitness in the Price equation
    # (Price 1970; Bowles 2006, Science 314:1569, eq. 1).
    if prev_populations is not None:
        prev_pops = np.array(
            [float(prev_populations.get(bid, int(pop_sizes[i])))
             for i, bid in enumerate(band_ids)],
            dtype=float,
        )
        prev_pops = np.maximum(prev_pops, 1.0)
        # Suppress log(0) warning for extinct bands — sigmoid maps -inf to 0.
        with np.errstate(divide="ignore"):
            malthusian_r = np.log(pop_sizes / prev_pops)
        demographic_fitness = 1.0 / (1.0 + np.exp(-5.0 * malthusian_r))
    else:
        max_pop = max(pop_sizes.max(), 1.0)
        demographic_fitness = pop_sizes / max_pop

    # ── Raid fitness: win rate from recent event window ──
    raid_wins = np.zeros(len(bands), dtype=float)
    raid_totals = np.zeros(len(bands), dtype=float)
    for i, band in enumerate(bands):
        event_window = getattr(band.society, "_event_window", [])
        for ev in event_window:
            if ev.get("type") != "inter_band_raid":
                continue
            outcome = ev.get("outcome", "")
            att_id = ev.get("attacker_band_id")
            def_id = ev.get("defender_band_id")
            bid = band_ids[i]
            if att_id == bid:
                raid_totals[i] += 1
                if outcome == "attacker_wins":
                    raid_wins[i] += 1
            elif def_id == bid:
                raid_totals[i] += 1
                if outcome == "defender_wins":
                    raid_wins[i] += 1

    with np.errstate(divide="ignore", invalid="ignore"):
        raid_win_rate = np.where(raid_totals > 0, raid_wins / raid_totals, 0.5)

    # ── Compute Pearson r for each fitness component separately ──
    def _mean_r_vs_fitness(fitness_vec: np.ndarray) -> float:
        """Pearson r between prosocial trait means and a fitness vector."""
        if fitness_vec.std() < 1e-8:
            return 0.0
        coefficients: list[float] = []
        for trait in _PROSOCIAL_TRAITS:
            trait_means = np.array(
                [float(np.mean([getattr(a, trait) for a in b.get_living()])
                       if b.get_living() else 0.0)
                 for b in bands],
                dtype=float,
            )
            if trait_means.std() < 1e-8:
                continue
            r = float(np.corrcoef(trait_means, fitness_vec)[0, 1])
            if np.isfinite(r):
                coefficients.append(r)
        return float(np.mean(coefficients)) if coefficients else 0.0

    demographic_coeff = _mean_r_vs_fitness(demographic_fitness)
    raid_coeff = _mean_r_vs_fitness(raid_win_rate)

    return demographic_coeff, raid_coeff


# ── Inter-band migration ───────────────────────────────────────────────────────

def _process_migration(
    clan_society: "ClanSociety",
    year: int,
    rng: np.random.Generator,
    config: "Config",
    clan_config: "ClanConfig | None",
) -> list[dict]:
    """Move a small fraction of agents between bands (gene flow).

    Migration probability per agent is:
        p_migrate = migration_rate_per_agent * trust * (1 - distance)

    A migrating agent is physically moved: removed from their origin band's
    Society and added to the destination band's Society.  They carry all their
    heritable traits, beliefs, skills, and non-heritable state.

    This is the primary mechanism opposing between-group selection:
    migrants reduce Fst between the two bands they connect.

    Returns a list of "inter_band_migration" event dicts.
    """
    migration_rate = _cfg(
        clan_config, "migration_rate_per_agent", _DEFAULT_MIGRATION_RATE_PER_AGENT
    )
    if migration_rate <= 0.0:
        return []

    band_ids = sorted(clan_society.bands.keys())
    n = len(band_ids)
    if n < 2:
        return []

    events: list[dict] = []

    # Evaluate all directed pairs: agent in band_i may migrate to band_j
    for i in range(n):
        id_origin = band_ids[i]
        band_origin = clan_society.bands[id_origin]
        living = band_origin.get_living()

        # Never deplete a band below min_viable_population + 1
        min_vp = _cfg(config, "min_viable_population", 10.0)
        if len(living) <= int(min_vp) + 1:
            continue

        # Pick a random destination band (not itself)
        other_ids = [bid for bid in band_ids if bid != id_origin]
        if not other_ids:
            continue

        id_dest = int(rng.choice(other_ids))
        band_dest = clan_society.bands[id_dest]

        distance = clan_society.get_distance(id_origin, id_dest)
        trust = (
            band_origin.trust_toward(id_dest) + band_dest.trust_toward(id_origin)
        ) / 2.0

        # Per-agent migration probability
        p_migrate = migration_rate * trust * (1.0 - distance)
        p_migrate = float(max(0.0, min(1.0, p_migrate)))

        # Sample migrants from living agents (adults only to avoid
        # separating dependent children from parents)
        adult_migrants = [
            a for a in living
            if a.life_stage in ("PRIME", "MATURE") and not a.partner_ids
        ]
        if not adult_migrants:
            continue

        migrated: list = []
        for agent in adult_migrants:
            # Guard again: stop if origin band would fall below minimum
            if len(band_origin.get_living()) <= int(min_vp) + 1:
                break
            if rng.random() < p_migrate:
                migrated.append(agent)

        for agent in migrated:
            # Move agent: mark them dead in origin society, add to destination.
            # We cannot use agent.die() (that's a permanent death).  Instead
            # we move the agent object directly between the two Society registries.
            _move_agent(agent, band_origin, band_dest)
            events.append({
                "type": "inter_band_migration",
                "year": year,
                "agent_ids": [agent.id],
                "description": (
                    f"Agent {agent.id} migrated from Band {id_origin} "
                    f"to Band {id_dest} (trust={trust:.2f}, dist={distance:.2f})"
                ),
                "outcome": "migrated",
                "origin_band_id": id_origin,
                "destination_band_id": id_dest,
            })

        if migrated:
            _log.debug(
                "Migration: %d agents moved Band %d → Band %d (year %d)",
                len(migrated), id_origin, id_dest, year,
            )

    return events


def _move_agent(agent, band_origin, band_dest) -> None:
    """Transfer an agent from one band's Society to another.

    The agent object is removed from origin's _agents dict and inserted into
    destination's _agents dict.  We reuse the same Python object — no copying —
    so all heritable and non-heritable attributes are preserved exactly.

    The agent's numeric id may collide with an existing id in the destination
    band (because each Band's IdCounter starts from 1 independently).  The
    destination Society's _agents dict uses the id as key; if the key already
    exists, we store the immigrant under a new unique id derived from the
    destination Society's counter.
    """
    origin_society = band_origin.society
    dest_society = band_dest.society

    # Remove from origin
    origin_society.agents.pop(agent.id, None)

    # Reassign id if collision: Agent uses a plain dataclass field `id`,
    # so we assign directly.  The new id is unique within the destination society.
    if agent.id in dest_society.agents:
        new_id = dest_society.id_counter.next()
        # Agent.id is a plain dataclass field — direct assignment is safe.
        agent.id = new_id  # type: ignore[misc]

    # Insert into destination
    dest_society.agents[agent.id] = agent

    _log.debug(
        "Moved agent id=%d to Band %d (dest_pop=%d)",
        agent.id, band_dest.band_id, len(dest_society.agents),
    )


# ── Band fission ──────────────────────────────────────────────────────────────

def _process_fission(
    clan_society: "ClanSociety",
    year: int,
    rng: np.random.Generator,
    config: "Config",
    clan_config: "ClanConfig | None",
) -> list[dict]:
    """Split any band that exceeds the fission threshold.

    Fission threshold default = 150 (Dunbar 1992 — the cognitive limit
    for maintaining stable social relationships in human groups).

    Mechanism:
      - Living agents are randomly split into two daughter bands.
      - rng.shuffle ensures random assignment, implementing a founder effect.
      - Each daughter band receives a randomly sampled ~50% of the parent pop
        (with ±10% stochastic variation so daughters are not always equal size).
      - The two daughters get fresh IDs = max_existing_id + 1 and + 2.
      - The parent band is removed from ClanSociety after split.
      - Each daughter band is placed at the parent's centroid with a small
        random distance offset.
      - Daughter bands inherit the parent's trust scores.
      - Daughter bands begin at moderate distance from each other (0.3) since
        they share origin territory.

    Returns a list of "band_fission" event dicts.
    """
    fission_threshold = _cfg(
        clan_config, "fission_threshold", _DEFAULT_FISSION_THRESHOLD
    )

    events: list[dict] = []

    # Snapshot of band ids — collect candidates first to avoid modifying dict
    # during iteration.
    candidate_ids = [
        bid for bid, band in clan_society.bands.items()
        if band.population_size() > fission_threshold
    ]

    for bid in candidate_ids:
        if bid not in clan_society.bands:
            continue  # already removed (shouldn't happen, guard anyway)
        band = clan_society.bands[bid]
        living = band.get_living()
        if len(living) <= fission_threshold:
            continue

        _log.info(
            "Band fission: Band %d (pop=%d) exceeds threshold %d at year %d",
            bid, len(living), int(fission_threshold), year,
        )

        # ── Create two daughter bands ─────────────────────────────────────────
        max_id = max(clan_society.bands.keys()) if clan_society.bands else 0
        daughter_id_1 = max_id + 1
        daughter_id_2 = max_id + 2

        # Shuffle agents for random founder effect
        agents_list = list(living)
        rng.shuffle(agents_list)

        # Stochastic split: ~50% ± 10%
        split_frac = float(rng.uniform(0.40, 0.60))
        split_idx = max(1, int(len(agents_list) * split_frac))
        group1 = agents_list[:split_idx]
        group2 = agents_list[split_idx:]

        # Derive daughter rngs from the clan rng (deterministic, not random)
        seed1 = int(rng.integers(0, 2**31))
        seed2 = int(rng.integers(0, 2**31))

        # Import here to avoid circular import at module level
        from models.clan.band import Band

        # Daughters inherit the parent band's Config — not the shared default.
        # This preserves institutional regime across fission events: a
        # STRONG_STATE band that fissions produces STRONG_STATE daughters.
        # Uses dataclasses.replace to create independent copies so that
        # institutional drift in one daughter does not affect the other.
        from dataclasses import replace as dc_replace
        parent_config = band.society.config
        daughter1 = Band(
            band_id=daughter_id_1,
            name=f"Band{daughter_id_1}(fission of {bid})",
            config=dc_replace(parent_config),
            rng=np.random.default_rng(seed1),
            origin_year=year,
        )
        daughter2 = Band(
            band_id=daughter_id_2,
            name=f"Band{daughter_id_2}(fission of {bid})",
            config=dc_replace(parent_config),
            rng=np.random.default_rng(seed2),
            origin_year=year,
        )

        # Clear the freshly initialised agents (they're placeholders from
        # the Band constructor's Society init) and replace with the actual
        # agents from the parent band.
        daughter1.society.agents.clear()
        daughter2.society.agents.clear()

        for agent in group1:
            daughter1.society.agents[agent.id] = agent
        for agent in group2:
            daughter2.society.agents[agent.id] = agent

        # Inherit parent's trust scores toward all other bands
        for other_id, trust_val in band.inter_band_trust.items():
            if other_id != bid:
                daughter1.inter_band_trust[other_id] = trust_val
                daughter2.inter_band_trust[other_id] = trust_val

        # Daughters start with moderate trust toward each other
        daughter1.inter_band_trust[daughter_id_2] = 0.7
        daughter2.inter_band_trust[daughter_id_1] = 0.7

        # Capture parent distances BEFORE removing the parent band.
        # After remove_band(bid), any call to get_distance(bid, x) returns the
        # default 0.5 because the distance_matrix entries are cleaned up as part
        # of remove_band.  Capturing here ensures daughters inherit the correct
        # geographic proximity to every existing band.
        parent_distances: dict[int, float] = {
            oid: clan_society.get_distance(bid, oid)
            for oid in clan_society.bands
            if oid != bid
        }

        # ── Register daughters, remove parent ─────────────────────────────────
        clan_society.remove_band(bid)
        clan_society.add_band(daughter1)
        clan_society.add_band(daughter2)

        # Distance: daughters share parent's distances to other bands.
        # Use the pre-captured parent_distances dict — do NOT call
        # clan_society.get_distance(bid, ...) here; bid has been removed.
        for other_id in clan_society.bands:
            if other_id in (daughter_id_1, daughter_id_2):
                continue
            parent_dist = parent_distances.get(other_id, 0.5)
            # Small noise ±0.05 so daughters occupy slightly different territory
            noise = float(rng.uniform(-0.05, 0.05))
            clan_society.set_distance(daughter_id_1, other_id,
                                       float(np.clip(parent_dist + noise, 0.0, 1.0)))
            clan_society.set_distance(daughter_id_2, other_id,
                                       float(np.clip(parent_dist - noise, 0.0, 1.0)))

        # Daughters are close to each other (shared origin territory)
        clan_society.set_distance(daughter_id_1, daughter_id_2, 0.3)

        events.append({
            "type": "band_fission",
            "year": year,
            "agent_ids": [a.id for a in agents_list],
            "description": (
                f"Band {bid} (pop={len(agents_list)}) split into "
                f"Band {daughter_id_1} (n={len(group1)}) "
                f"and Band {daughter_id_2} (n={len(group2)}) at year {year}"
            ),
            "outcome": "fission",
            "parent_band_id": bid,
            "daughter_band_id_1": daughter_id_1,
            "daughter_band_id_2": daughter_id_2,
            "daughter_1_pop": len(group1),
            "daughter_2_pop": len(group2),
        })

        _log.info(
            "Band %d fissioned → Band %d (n=%d) + Band %d (n=%d)",
            bid, daughter_id_1, len(group1), daughter_id_2, len(group2),
        )

    return events


# ── Band extinction ───────────────────────────────────────────────────────────

def _process_extinction(
    clan_society: "ClanSociety",
    year: int,
    rng: np.random.Generator,
    config: "Config",
    clan_config: "ClanConfig | None",
) -> list[dict]:
    """Absorb any band that has fallen below the extinction threshold.

    When a band's living population drops below extinction_threshold (default 10),
    its surviving members join the nearest band (minimum distance).  They carry
    all their heritable traits, increasing gene flow and reducing Fst.

    If no neighbour band exists, the band is simply removed (everyone dies;
    this is an edge case for 1-band scenarios and should not normally occur).

    Returns a list of "band_extinction" event dicts.
    """
    extinction_threshold = _cfg(
        clan_config, "extinction_threshold", _DEFAULT_EXTINCTION_THRESHOLD
    )

    events: list[dict] = []

    candidate_ids = [
        bid for bid, band in clan_society.bands.items()
        if 0 < band.population_size() < extinction_threshold
    ]

    for bid in candidate_ids:
        if bid not in clan_society.bands:
            continue

        band = clan_society.bands[bid]
        living = band.get_living()
        if len(living) >= extinction_threshold:
            continue

        # Find nearest absorbing band
        other_ids = [oid for oid in clan_society.bands if oid != bid]
        if not other_ids:
            # No neighbours — remove the band but emit the event
            clan_society.remove_band(bid)
            events.append({
                "type": "band_extinction",
                "year": year,
                "agent_ids": [a.id for a in living],
                "description": (
                    f"Band {bid} (pop={len(living)}) went extinct at year {year} "
                    f"with no absorbing band available"
                ),
                "outcome": "extinction_no_absorber",
                "extinct_band_id": bid,
                "absorbing_band_id": None,
            })
            _log.warning(
                "Band %d extinct at year %d — no absorbing band available.",
                bid, year,
            )
            continue

        # Select closest band by distance
        distances = {
            oid: clan_society.get_distance(bid, oid)
            for oid in other_ids
        }
        absorbing_id = min(distances, key=lambda k: distances[k])
        absorbing_band = clan_society.bands[absorbing_id]

        # Move all refugees
        refugee_ids = []
        for agent in living:
            _move_agent(agent, band, absorbing_band)
            refugee_ids.append(agent.id)

        # Update trust: absorbing band gets a boost (they welcomed refugees)
        absorbing_band.update_trust(bid, 0.0)  # no-op — band about to be removed
        # The absorbing band's trust toward other bands stays the same.
        # Refugees' representation in the absorbing band increases gene flow.

        clan_society.remove_band(bid)

        events.append({
            "type": "band_extinction",
            "year": year,
            "agent_ids": refugee_ids,
            "description": (
                f"Band {bid} (pop={len(refugee_ids)}) went extinct — "
                f"refugees absorbed by Band {absorbing_id} at year {year}"
            ),
            "outcome": "absorbed",
            "extinct_band_id": bid,
            "absorbing_band_id": absorbing_id,
        })

        _log.info(
            "Band %d extinct at year %d — %d refugees → Band %d",
            bid, year, len(refugee_ids), absorbing_id,
        )

    return events


# ── Helpers ───────────────────────────────────────────────────────────────────

def _cfg(obj: "ClanConfig | None", key: str, default: float) -> float:
    """Safe attribute accessor with fallback default."""
    if obj is None:
        return float(default)
    return float(getattr(obj, key, default))
