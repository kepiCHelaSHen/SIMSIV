"""
clan_raiding.py — Inter-band conflict (raiding) engine (SIMSIV v2, Turn 3).

Implements lethal inter-group raiding between two bands, following the Bowles
(2006) "group selection in humans" framework where warfare is a key force in
the evolution of prosocial traits.

Public interface
----------------
    raid_tick(attacker_band, defender_band, trust, rng, config) -> list[dict]

Design
------
Raiding is scarcity-driven: bands raid when their mean resource level is low
AND their mean aggression_propensity is high.  The probability of a raid
attempt is:

    p_raid = raid_base * scarcity_pressure * aggression_pressure * xenophobia * trust_deficit

where:
  scarcity_pressure = max(0, 1 - mean_resources / raid_scarcity_threshold)
  aggression_pressure = mean aggression_propensity of attacker adults
  xenophobia = 1 - mean outgroup_tolerance (attacker adults)
  trust_deficit = max(0, 1 - trust / raid_trust_suppression_threshold)

Raiding party (attackers)
-------------------------
PRIME/MATURE males with above-median aggression_propensity + risk_tolerance
are selected.  Party size ∝ band population (capped at raid_party_max_fraction).

Coalition defence (Bowles mechanism)
-------------------------------------
Defenders mobilise proportional to group_loyalty mean.  Higher group_loyalty →
larger defensive coalition → higher combined defensive power.  cooperation_propensity
provides a cohesion bonus (coordinated defence is stronger than individual
defence).

Combat resolution
-----------------
Adapted from the v1 conflict.py formula:
  power = physical_strength * 1.4 (males) + aggression * 0.20 + health * 0.20
        + risk_tolerance * 0.10 + physical_robustness * 0.10 + combat_skill * 0.10
        + endurance * 0.05 + pain_tolerance * 0.05

Collective attacker power vs collective defender power.  Victory margin is the
normalised power difference.  Probabilistic outcome to prevent determinism.

Consequences
------------
Attacker wins:
  - Loots current_resources, current_tools, current_prestige_goods proportional
    to victory margin (capped at raid_loot_fraction).
  - Loot is distributed equally among surviving attacker members.
  - Defenders take casualties (some killed, removed from their band's society).
  - Attackers take smaller casualties.

Defender wins:
  - No loot.
  - Attackers take heavier casualties than in a draw.
  - Defenders take light casualties (pyrrhic defence is realistic).

Both outcomes:
  - Bilateral trust decreases.  Defenders lose more trust toward attackers
    (asymmetric memory of victimhood — Bowles & Gintis 2011).
  - Survivors' trauma_score increases.
  - Both sides' agents update reputation ledgers negatively toward each other.

Trait modulation (summary)
--------------------------
  aggression_propensity  : raid initiation, attacker selection
  group_loyalty          : defensive coalition size (Bowles mechanism)
  outgroup_tolerance     : inversely drives raid probability
  risk_tolerance         : attacker selection + combat power
  cooperation_propensity : defender coalition cohesion bonus
  physical_strength      : individual combat power (sex-differentiated)
  endurance              : combat power (sustained engagement)
  physical_robustness    : damage absorption (reduces casualty chance)
  pain_tolerance         : combat power contribution
  combat_skill           : if skills_enabled (config)

Architecture rules
------------------
- No print() statements.  Uses logging.getLogger(__name__).
- All randomness via the seeded rng parameter.
- No imports from models.society, engines.*, or simulation.
- Models know nothing about this engine.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from models.clan.band import Band
    from config import Config
    from models.clan.clan_config import ClanConfig

_log = logging.getLogger(__name__)

# ── Module-level constants ────────────────────────────────────────────────────

# Life stages eligible to join raiding party or defensive coalition.
_COMBATANT_STAGES = frozenset({"PRIME", "MATURE"})

# Minimum raiding party size — raids require at least this many fighters.
_MIN_RAID_PARTY_SIZE: int = 2

# Default config parameters used when config attribute is absent (v1 Config).
_DEFAULT_RAID_BASE_PROBABILITY: float = 0.10
_DEFAULT_RAID_SCARCITY_THRESHOLD: float = 3.0
_DEFAULT_RAID_LOOT_FRACTION: float = 0.30
_DEFAULT_RAID_ATTACKER_CASUALTY_RATE: float = 0.15
_DEFAULT_RAID_DEFENDER_CASUALTY_RATE: float = 0.20
_DEFAULT_RAID_PARTY_MAX_FRACTION: float = 0.35
_DEFAULT_RAID_DEFENSE_MAX_FRACTION: float = 0.50
_DEFAULT_RAID_TRUST_LOSS_ATTACKER: float = 0.15
_DEFAULT_RAID_TRUST_LOSS_DEFENDER: float = 0.25
_DEFAULT_RAID_TRUST_SUPPRESSION_THRESHOLD: float = 0.4
_DEFAULT_BOWLES_COALITION_SCALE: float = 1.0

# Trauma increment applied to raid survivors.
_RAID_TRAUMA_INCREMENT: float = 0.08

# Reputation ledger penalty: agents on opposing sides distrust each other.
_RAID_REPUTATION_PENALTY: float = -0.20


# ── Public API ────────────────────────────────────────────────────────────────

def raid_tick(
    attacker_band: "Band",
    defender_band: "Band",
    trust: float,
    rng: np.random.Generator,
    config: "Config | ClanConfig",
) -> list[dict]:
    """Attempt an inter-band raid by attacker_band against defender_band.

    Parameters
    ----------
    attacker_band:
        The aggressor band.  Raid motivation is computed from this band's
        resource stress and trait composition.
    defender_band:
        The band being raided.
    trust:
        Bilateral trust level [0, 1].  Mean of both directional trust scores,
        computed by the caller (ClanEngine._process_interaction).
    rng:
        Seeded numpy.random.Generator.  All randomness goes through this.
    config:
        Shared simulation config (v1 Config or v2 ClanConfig).

    Returns
    -------
    list of event dicts.  Each dict has keys:
        type        : "inter_band_raid"
        year        : int  (populated by ClanEngine — set to 0 here)
        agent_ids   : list of int (raiding party + casualties)
        description : str
        outcome     : "attacker_wins" | "defender_wins" | "draw"
        attacker_band_id : int
        defender_band_id : int

    An empty list is returned if:
      - The probability check fails (no raid this tick).
      - The attacker band cannot form a valid raiding party (too few adults).
    """
    events: list[dict] = []

    # ── 1. Check whether the attacker band initiates a raid this tick ─────────
    if not _raid_triggered(attacker_band, defender_band, trust, rng, config):
        _log.debug(
            "raid_tick: Band %d → Band %d: raid not triggered (trust=%.2f).",
            attacker_band.band_id, defender_band.band_id, trust,
        )
        return events

    # ── 2. Form the raiding party ─────────────────────────────────────────────
    raiding_party = _select_raiding_party(attacker_band, rng, config)
    if len(raiding_party) < _MIN_RAID_PARTY_SIZE:
        _log.debug(
            "raid_tick: Band %d cannot form raiding party (party_size=%d < min=%d).",
            attacker_band.band_id, len(raiding_party), _MIN_RAID_PARTY_SIZE,
        )
        return events

    # ── 3. Mobilise the defensive coalition ───────────────────────────────────
    defensive_coalition = _select_defensive_coalition(defender_band, rng, config)

    _log.debug(
        "raid_tick: Band %d (n=%d) raids Band %d (defenders=%d), trust=%.2f",
        attacker_band.band_id, len(raiding_party),
        defender_band.band_id, len(defensive_coalition),
        trust,
    )

    # ── 4. Compute collective combat power ────────────────────────────────────
    attacker_power = _collective_power(raiding_party, config)
    defender_power = _collective_power(defensive_coalition, config)

    # Bowles coalition cohesion bonus: cooperative defenders coordinate better.
    cohesion_bonus = _coalition_cohesion_bonus(defensive_coalition, config)
    defender_power *= (1.0 + cohesion_bonus)

    # ── 5. Probabilistic combat resolution ───────────────────────────────────
    total_power = attacker_power + defender_power + 1e-6
    attacker_win_prob = attacker_power / total_power

    # Power margin: 0 = evenly matched, 1 = complete dominance.
    power_margin = abs(attacker_power - defender_power) / total_power

    combat_roll = float(rng.random())
    if combat_roll < attacker_win_prob:
        outcome = "attacker_wins"
    elif combat_roll < attacker_win_prob + (1.0 - attacker_win_prob) * 0.15:
        # ~15% of the remaining probability is a tactical draw
        outcome = "draw"
    else:
        outcome = "defender_wins"

    _log.debug(
        "raid_tick: att_power=%.2f, def_power=%.2f, cohesion_bonus=%.3f, "
        "outcome=%s (margin=%.3f)",
        attacker_power, defender_power, cohesion_bonus, outcome, power_margin,
    )

    # ── 6. Apply loot (attacker wins only) ────────────────────────────────────
    looted: dict[str, float] = {"current_resources": 0.0,
                                "current_tools": 0.0,
                                "current_prestige_goods": 0.0}

    if outcome == "attacker_wins" and defensive_coalition:
        loot_fraction = float(getattr(config, "raid_loot_fraction", _DEFAULT_RAID_LOOT_FRACTION))
        # Scale loot by power margin (decisive victories loot more)
        effective_loot = loot_fraction * (0.5 + power_margin * 0.5)
        looted = _apply_loot(
            raiding_party, defensive_coalition, defender_band, effective_loot, rng, config
        )

    # ── 7. Apply casualties ───────────────────────────────────────────────────
    attacker_deaths, defender_deaths = _apply_casualties(
        raiding_party, defensive_coalition,
        outcome, power_margin, rng, config,
    )

    # ── 8. Update trauma scores for survivors ────────────────────────────────
    for fighter in raiding_party + defensive_coalition:
        if fighter.alive:
            fighter.trauma_score = min(
                1.0, fighter.trauma_score + _RAID_TRAUMA_INCREMENT
            )

    # ── 9. Update bilateral trust ─────────────────────────────────────────────
    trust_loss_attacker = float(
        getattr(config, "raid_trust_loss_attacker", _DEFAULT_RAID_TRUST_LOSS_ATTACKER)
    )
    trust_loss_defender = float(
        getattr(config, "raid_trust_loss_defender", _DEFAULT_RAID_TRUST_LOSS_DEFENDER)
    )

    # Attacker's trust toward defender decreases (they acted on hostility)
    attacker_band.update_trust(defender_band.band_id, -trust_loss_attacker)
    # Defender's trust toward attacker decreases more (victims remember raids)
    defender_band.update_trust(attacker_band.band_id, -trust_loss_defender)

    # ── 10. Reputation ledger updates ─────────────────────────────────────────
    # Surviving raiders and defenders remember each other negatively.
    surviving_raiders = [a for a in raiding_party if a.alive]
    surviving_defenders = [a for a in defensive_coalition if a.alive]
    _update_reputation_ledgers(surviving_raiders, surviving_defenders)

    # ── 11. Build and return event ────────────────────────────────────────────
    all_agent_ids = (
        [a.id for a in raiding_party]
        + [a.id for a in defensive_coalition]
    )

    total_looted = sum(looted.values())
    description = (
        f"Raid: Band {attacker_band.band_id} "
        f"(party={len(raiding_party)}, deaths={attacker_deaths}) "
        f"→ Band {defender_band.band_id} "
        f"(defenders={len(defensive_coalition)}, deaths={defender_deaths}) "
        f"— {outcome}, loot={total_looted:.1f}"
    )

    _log.info(
        "raid_tick: %s", description,
    )

    events.append({
        "type": "inter_band_raid",
        "year": 0,  # stamped by caller (ClanEngine)
        "agent_ids": all_agent_ids,
        "description": description,
        "outcome": outcome,
        "attacker_band_id": attacker_band.band_id,
        "defender_band_id": defender_band.band_id,
        "attacker_deaths": attacker_deaths,
        "defender_deaths": defender_deaths,
        "loot": dict(looted),
        "power_margin": round(power_margin, 3),
    })

    return events


# ── Internal helpers ──────────────────────────────────────────────────────────

def _cfg(config: "Config | ClanConfig", key: str, default: float) -> float:
    """Safe config accessor: return config.key if present, else default."""
    return float(getattr(config, key, default))


def _raid_triggered(
    attacker_band: "Band",
    defender_band: "Band",
    trust: float,
    rng: np.random.Generator,
    config: "Config | ClanConfig",
) -> bool:
    """Return True if the attacker band initiates a raid this tick.

    Probability formula (all factors multiplicative):
        p = base * scarcity * aggression * xenophobia * trust_deficit

    Factors
    -------
    scarcity:
        Increases as mean resources drop below raid_scarcity_threshold.
        0 when resources are abundant; 1 when resources are completely depleted.
    aggression:
        Mean aggression_propensity of eligible combatants in the attacker band.
        Higher aggression → more likely to raid.
    xenophobia:
        1 - mean outgroup_tolerance.  More xenophobic bands raid more often.
    trust_deficit:
        How far below the trust suppression threshold the current trust is.
        When trust >= threshold, this factor → 0 (raids suppressed).
        When trust = 0, this factor → 1.

    Edge cases
    ----------
    - Empty attacker band: returns False.
    - If all factors stack to 0, p = 0 → never raid.
    """
    living_attackers = attacker_band.get_living()
    if not living_attackers:
        return False

    # Adults only for trait reads
    adults = [a for a in living_attackers if a.life_stage in _COMBATANT_STAGES]
    if not adults:
        return False

    base = _cfg(config, "raid_base_probability", _DEFAULT_RAID_BASE_PROBABILITY)
    scarcity_threshold = _cfg(
        config, "raid_scarcity_threshold", _DEFAULT_RAID_SCARCITY_THRESHOLD
    )
    trust_suppression = _cfg(
        config, "raid_trust_suppression_threshold", _DEFAULT_RAID_TRUST_SUPPRESSION_THRESHOLD
    )

    # Scarcity pressure: mean attacker resources vs threshold
    mean_res = sum(a.current_resources for a in living_attackers) / len(living_attackers)
    scarcity = max(0.0, 1.0 - mean_res / max(scarcity_threshold, 1e-6))

    # Aggression pressure: mean trait of eligible combatants
    aggression = sum(a.aggression_propensity for a in adults) / len(adults)

    # Xenophobia: low outgroup_tolerance → high raid tendency
    mean_tolerance = sum(a.outgroup_tolerance for a in adults) / len(adults)
    xenophobia = 1.0 - mean_tolerance

    # Trust deficit: raids suppressed when trust is high
    trust_deficit = max(0.0, 1.0 - trust / max(trust_suppression, 1e-6))

    p_raid = base * scarcity * aggression * xenophobia * trust_deficit
    p_raid = float(min(1.0, max(0.0, p_raid)))

    _log.debug(
        "raid_trigger: Band %d → Band %d: p=%.4f "
        "(base=%.2f, scarcity=%.2f, agg=%.2f, xeno=%.2f, trust_deficit=%.2f)",
        attacker_band.band_id, defender_band.band_id, p_raid,
        base, scarcity, aggression, xenophobia, trust_deficit,
    )

    return bool(rng.random() < p_raid)


def _select_raiding_party(
    band: "Band",
    rng: np.random.Generator,
    config: "Config | ClanConfig",
) -> list:
    """Select the raiding party from the attacker band.

    Selection criteria:
      - Must be PRIME or MATURE life stage (active adults)
      - Must be male (raiding is male-biased per ethnographic record; Keeley 1996)
      - Must have aggression_propensity above median for the eligible pool
      - Must have risk_tolerance above median for the eligible pool
      - Party size capped at raid_party_max_fraction of band population

    If the eligible pool is empty, returns an empty list (raid cannot proceed).
    """
    living = band.get_living()
    max_frac = _cfg(config, "raid_party_max_fraction", _DEFAULT_RAID_PARTY_MAX_FRACTION)
    max_size = max(1, int(len(living) * max_frac))

    # Filter: PRIME/MATURE males only
    try:
        from models.agent import Sex
        eligible = [
            a for a in living
            if a.life_stage in _COMBATANT_STAGES and a.sex == Sex.MALE
        ]
    except ImportError:
        # Fallback: no sex filter if Sex enum unavailable (should not happen)
        eligible = [a for a in living if a.life_stage in _COMBATANT_STAGES]

    if not eligible:
        return []

    # Compute score = aggression_propensity * risk_tolerance
    # (high on both → strong raid candidate)
    scores = np.array(
        [a.aggression_propensity * a.risk_tolerance for a in eligible],
        dtype=float,
    )

    # Only agents above median raid-candidate score are considered
    median_score = float(np.median(scores))
    above_median = [a for a, s in zip(eligible, scores) if s >= median_score]
    if not above_median:
        above_median = eligible  # fallback if all tied at median

    # Sample up to max_size without replacement
    n = min(len(above_median), max_size)
    if n == 0:
        return []

    idx = rng.choice(len(above_median), size=n, replace=False)
    party = [above_median[i] for i in idx]

    _log.debug(
        "Band %d raiding party: %d fighters (from %d eligible, max_size=%d)",
        band.band_id, len(party), len(eligible), max_size,
    )
    return party


def _select_defensive_coalition(
    band: "Band",
    rng: np.random.Generator,
    config: "Config | ClanConfig",
) -> list:
    """Select the defensive coalition from the defender band.

    Bowles mechanism: coalition size scales with mean group_loyalty trait.
    Higher group_loyalty → more defenders mobilise.

    Selection:
      - All PRIME/MATURE adults are eligible (both sexes defend their band)
      - Each eligible agent joins the coalition with probability:
          p_join = group_loyalty * (1 + cooperation_propensity * 0.5)
        clamped to [0.1, 1.0] (even low-loyalty agents have 10% chance to join)
      - Coalition size capped at raid_defense_max_fraction of band population

    If the band is empty, returns an empty list (no defence possible).
    """
    living = band.get_living()
    if not living:
        return []

    max_frac = _cfg(config, "raid_defense_max_fraction", _DEFAULT_RAID_DEFENSE_MAX_FRACTION)
    max_size = max(1, int(len(living) * max_frac))

    eligible = [a for a in living if a.life_stage in _COMBATANT_STAGES]
    if not eligible:
        # If no PRIME/MATURE adults, any living agent can defend (desperation)
        eligible = list(living)

    # bowles_coalition_scale (ClanConfig) amplifies group_loyalty's effect on
    # p_join.  scale=1.0 is the baseline (Bowles 2006).  Values > 1 make the
    # Bowles mechanism stronger (higher loyalty → proportionally larger coalition);
    # values < 1 weaken it (useful for parameter sensitivity analysis).
    # Configurable via ClanConfig.bowles_coalition_scale (default 1.0).
    bowles_scale = _cfg(config, "bowles_coalition_scale", _DEFAULT_BOWLES_COALITION_SCALE)

    coalition: list = []
    for agent in eligible:
        # p_join base: group_loyalty scaled by bowles_coalition_scale,
        # with a cooperation cohesion modifier.
        # bowles_scale multiplies the effective loyalty signal so that
        # higher bowles_coalition_scale produces proportionally larger coalitions.
        # Formula derived from Bowles (2006) Eq. 3: r_C ∝ loyalty × scale.
        effective_loyalty = agent.group_loyalty * bowles_scale
        p_join = effective_loyalty * (1.0 + agent.cooperation_propensity * 0.5)
        # Floor 0.05 (configurable via ClanConfig.p_join_floor, default 0.05):
        # Ethnographic evidence (Keeley 1996; Bowles 2006) shows that even
        # low-loyalty group members have a non-trivial probability of joining
        # defence when the group is physically threatened.  A strictly zero floor
        # would create bands where some agents never defend under any circumstance,
        # which is inconsistent with observed forager behaviour.  The floor is kept
        # low (5%) to avoid biasing the selection mechanism while preserving
        # minimal social pressure to participate.
        p_join_floor = _cfg(config, "p_join_floor", 0.05)
        p_join = float(max(p_join_floor, min(1.0, p_join)))
        if rng.random() < p_join:
            coalition.append(agent)

    # Trim to maximum allowed size (random subset if over cap)
    if len(coalition) > max_size:
        idx = rng.choice(len(coalition), size=max_size, replace=False)
        coalition = [coalition[i] for i in idx]

    _log.debug(
        "Band %d defensive coalition: %d defenders (from %d eligible, "
        "max_size=%d, bowles_scale=%.2f, p_join_floor=%.2f)",
        band.band_id, len(coalition), len(eligible), max_size,
        bowles_scale, _cfg(config, "p_join_floor", 0.05),
    )
    return coalition


def _individual_combat_power(agent, config: "Config | ClanConfig") -> float:
    """Compute individual combat power for one fighter.

    Adapted from v1 conflict.py _resolve_conflict formula.  Physical traits
    dominate inter-group raiding (unlike intra-group dominance contests where
    status and social skill matter more).

    Formula:
        power = phys_strength_contrib   (0.30 weight, male 1.4× multiplier)
              + aggression_propensity   (0.20)
              + health                  (0.20)
              + risk_tolerance          (0.10)
              + physical_robustness     (0.10)
              + endurance               (0.05)
              + pain_tolerance          (0.05)
              + combat_skill            (if skills_enabled)
    """
    try:
        from models.agent import Sex
        is_male = agent.sex == Sex.MALE
    except ImportError:
        is_male = True  # assume male if unavailable

    # Physical strength with sex differential
    str_weight = 0.30
    str_contrib = agent.physical_strength * str_weight
    if is_male:
        str_contrib *= 1.4

    power = (
        str_contrib
        + agent.aggression_propensity * 0.20
        + agent.health * 0.20
        + agent.risk_tolerance * 0.10
        + agent.physical_robustness * 0.10
        + agent.endurance * 0.05
        + agent.pain_tolerance * 0.05
    )

    # Combat skill (if skills subsystem is active)
    if getattr(config, "skills_enabled", False):
        csw = float(getattr(config, "combat_skill_weight", 0.10))
        power += agent.combat_skill * csw

    return max(0.01, power)


def _collective_power(fighters: list, config: "Config | ClanConfig") -> float:
    """Sum individual combat power across a group of fighters.

    Returns 0.01 minimum to avoid division by zero in probability calculations
    when the group is empty.
    """
    if not fighters:
        return 0.01
    return sum(_individual_combat_power(a, config) for a in fighters)


def _coalition_cohesion_bonus(
    defenders: list,
    config: "Config | ClanConfig",
) -> float:
    """Compute defensive cohesion bonus from cooperation_propensity.

    Coordinated defence (high cooperation_propensity) is stronger than an equal
    number of independent defenders.  This is the Bowles & Gintis mechanism:
    group selection favours cooperation specifically because it improves inter-
    group conflict outcomes.

    Formula:
        bonus = mean_cooperation * bowles_coalition_scale * 0.20

    Range: approximately [0, 0.20] for cooperation in [0, 1] and default scale.
    """
    if not defenders:
        return 0.0
    mean_coop = sum(a.cooperation_propensity for a in defenders) / len(defenders)
    scale = _cfg(config, "bowles_coalition_scale", _DEFAULT_BOWLES_COALITION_SCALE)
    return mean_coop * scale * 0.20


def _apply_loot(
    raiding_party: list,
    defenders: list,
    defender_band: "Band",
    effective_loot_fraction: float,
    rng: np.random.Generator,
    config: "Config | ClanConfig",
) -> dict[str, float]:
    """Transfer resources from individual defenders to individual raiders.

    Each defender loses a fraction of each resource type; loot is pooled and
    distributed equally among surviving raiders.

    Only steals from defenders that have positive amounts — no floor needed
    because loot already has natural floor of 0 for each defender.

    Returns a dict of {resource_field: total_looted} for event logging.
    """
    resource_fields = ("current_resources", "current_tools", "current_prestige_goods")
    total_looted: dict[str, float] = {f: 0.0 for f in resource_fields}

    surviving_raiders = [a for a in raiding_party if a.alive]
    if not surviving_raiders:
        return total_looted  # no raiders left to carry loot

    # Loot from each defender proportionally
    for defender in defenders:
        if not defender.alive:
            continue
        for field in resource_fields:
            amount = float(getattr(defender, field, 0.0))
            if amount <= 0.0:
                continue
            stolen = amount * effective_loot_fraction
            # Clamp stolen to what the defender actually has
            stolen = min(stolen, amount)
            setattr(defender, field, amount - stolen)
            total_looted[field] += stolen

    if not surviving_raiders:
        return total_looted

    # Distribute loot equally among surviving raiders
    n_survivors = len(surviving_raiders)
    for field in resource_fields:
        share = total_looted[field] / n_survivors
        if share <= 0.0:
            continue
        # Apply resource caps to prevent runaway accumulation
        if field == "current_resources":
            cap = float(getattr(config, "resource_storage_cap", 20.0))
        elif field == "current_tools":
            cap = float(getattr(config, "tools_per_agent_cap", 10.0))
        else:
            cap = float(getattr(config, "prestige_goods_per_agent_cap", 5.0))

        for raider in surviving_raiders:
            current = float(getattr(raider, field, 0.0))
            setattr(raider, field, float(min(cap, current + share)))

    _log.debug(
        "Loot: resources=%.2f, tools=%.2f, prestige=%.2f "
        "(distributed to %d raiders)",
        total_looted["current_resources"],
        total_looted["current_tools"],
        total_looted["current_prestige_goods"],
        n_survivors,
    )
    return total_looted


def _apply_casualties(
    raiding_party: list,
    defensive_coalition: list,
    outcome: str,
    power_margin: float,
    rng: np.random.Generator,
    config: "Config | ClanConfig",
) -> tuple[int, int]:
    """Kill some fighters and remove them from their band's society.

    Casualty rates are set per outcome:
      - attacker_wins: attackers take light casualties; defenders take heavy.
      - defender_wins: attackers take heavy casualties; defenders take light.
      - draw:          both sides take moderate casualties.

    Individual casualty probability is modulated by physical_robustness
    (higher robustness → less likely to die) and power_margin (more decisive
    victory → more casualties on the losing side).

    Returns (n_attacker_deaths, n_defender_deaths).
    """
    base_att_rate = _cfg(
        config, "raid_attacker_casualty_rate", _DEFAULT_RAID_ATTACKER_CASUALTY_RATE
    )
    base_def_rate = _cfg(
        config, "raid_defender_casualty_rate", _DEFAULT_RAID_DEFENDER_CASUALTY_RATE
    )

    if outcome == "attacker_wins":
        att_rate = base_att_rate * (0.5 + power_margin * 0.5)
        def_rate = base_def_rate * (0.5 + power_margin * 1.5)
    elif outcome == "defender_wins":
        att_rate = base_att_rate * (0.5 + power_margin * 1.5)
        def_rate = base_def_rate * (0.5 + power_margin * 0.5)
    else:  # draw
        att_rate = base_att_rate * 0.75
        def_rate = base_def_rate * 0.75

    attacker_deaths = _kill_fighters(raiding_party, att_rate, rng)
    defender_deaths = _kill_fighters(defensive_coalition, def_rate, rng)

    _log.debug(
        "Casualties: attackers=%d/%d, defenders=%d/%d (outcome=%s, margin=%.3f)",
        attacker_deaths, len(raiding_party),
        defender_deaths, len(defensive_coalition),
        outcome, power_margin,
    )
    return attacker_deaths, defender_deaths


def _kill_fighters(fighters: list, base_rate: float, rng: np.random.Generator) -> int:
    """For each fighter, roll a death check and kill them if it fires.

    Individual death probability:
        p_die = base_rate * (1 - physical_robustness * 0.5)

    physical_robustness reduces death probability (tough fighters survive more).
    Killed agents have .die() called, which marks them dead in their Society.

    Returns the count of agents killed.
    """
    deaths = 0
    for fighter in fighters:
        if not fighter.alive:
            continue
        # Robustness reduces p_die: max 50% reduction at robustness=1.0
        p_die = base_rate * max(0.1, 1.0 - fighter.physical_robustness * 0.5)
        p_die = float(min(1.0, max(0.0, p_die)))
        if rng.random() < p_die:
            fighter.die("raid", 0)  # year = 0, will be overwritten by event year
            deaths += 1
    return deaths


def _update_reputation_ledgers(raiders: list, defenders: list) -> None:
    """Cross-update reputation ledgers between raiders and defenders.

    Survivors on each side remember the opposing side negatively.
    This creates lasting inter-band hostility in the social memory.
    """
    for raider in raiders:
        for defender in defenders:
            if defender.alive:
                raider.remember(defender.id, _RAID_REPUTATION_PENALTY)
    for defender in defenders:
        for raider in raiders:
            if raider.alive:
                # Defenders remember attackers more negatively (victim memory)
                defender.remember(raider.id, _RAID_REPUTATION_PENALTY * 1.5)
