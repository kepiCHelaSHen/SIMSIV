"""
Clan cooperation model — emergent cooperation metrics from agent state.

Computes cooperation, trade, defence, and selection metrics described in
Rice et al. (2026, bioRxiv 2026/711970).  All coefficients match the
frozen v1/v2 engine implementations exactly:

  Milestone 1 (Cooperation):
    - empathy modulation:  × (1 + empathy × 0.15)   [resources.py:289]
    - cooperation_norm:    × (1 + coop_norm × 0.1)   [resources.py:292]
    - conformity amp:      × (1 + conformity × 0.3)  [institutions.py:237]

  Milestone 2 (Trade):
    - social skill bonus:  × (1 + social_skill × 0.10) [clan_trade.py:330]
    - refusal threshold:   0.25                         [clan_trade.py:70]
    - scarcity threshold:  3.0                          [clan_trade.py:83]

  Milestone 3 (Coalition Defence):
    - p_join = loyalty × scale × (1 + coop × 0.5)     [clan_raiding.py:504]
    - cohesion bonus = mean_coop × scale × 0.20        [clan_raiding.py:610]
    - p_join floor = 0.05                               [clan_raiding.py:513]

  Milestone 4 (Selection Pressure):
    - 4 prosocial traits only                           [clan_selection.py:82-87]

Architecture note
-----------------
This is a MODEL file — pure computation over agent state, no side effects,
no tick logic.  Engine files may import and call these functions; this file
imports nothing from engines/.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from models.clan.band import Band
    from models.clan.clan_society import ClanSociety

_log = logging.getLogger(__name__)

# ── Constants (frozen paper coefficients) ────────────────────────────────────

# Empathy broadens altruism radius (de Waal 2008; DD15).
# Coefficient matches engines/resources.py line 289.
_EMPATHY_COEFF = 0.15

# Cultural cooperation norm modulates sharing (Boyd & Richerson 1985; DD25).
# Coefficient matches engines/resources.py line 292.
_COOP_NORM_COEFF = 0.1

# Conformity amplifies norm adoption (Henrich 2004; DD25).
# Coefficient matches engines/institutions.py line 237.
_CONFORMITY_COEFF = 0.3

# Minimum age at which beliefs are initialised (DD25: maturation at 15).
_BELIEF_MATURATION_AGE = 15

# Default trust threshold for cooperation sharing (config default).
_TRUST_THRESHOLD = 0.5


# ── Individual-level cooperation ─────────────────────────────────────────────

def compute_individual_cooperation(agent) -> float:
    """Compute an agent's effective cooperation score.

    Mechanism (Rice et al. 2026, §2.3 — Resource Sharing):

        C_i = cooperation_propensity                          (1)
              × (1 + empathy_capacity × 0.15)                 (2)
              × (1 + cooperation_norm  × 0.1)   [if age ≥ 15] (3)

    Term (1): Heritable prosocial trait, h²=0.40.  Primary genetic driver
              of cooperative behaviour (Hamilton 1964; Axelrod & Hamilton 1981).
    Term (2): Empathy extends altruism beyond kin (de Waal 2008).
              Coefficient 0.15 from DD15 specification, frozen in
              engines/resources.py:289.
    Term (3): Culturally transmitted cooperation norm [-1, +1].
              Amplifies or suppresses genetic cooperation baseline.
              Boyd & Richerson (1985); coefficient 0.1 from DD25,
              frozen in engines/resources.py:292.
              Only applies after belief maturation (age ≥ 15).

    Returns
    -------
    float
        Effective cooperation score.  Range approximately [0.0, 1.3].
        Not clamped — represents raw cooperation capacity.
    """
    c = agent.cooperation_propensity

    # (2) Empathy modulation — de Waal (2008), DD15
    c *= (1.0 + agent.empathy_capacity * _EMPATHY_COEFF)

    # (3) Cultural norm modulation — Boyd & Richerson (1985), DD25
    if hasattr(agent, "cooperation_norm") and agent.age >= _BELIEF_MATURATION_AGE:
        c *= (1.0 + agent.cooperation_norm * _COOP_NORM_COEFF)

    return float(c)


# ── Band-level cooperation ──────────────────────────────────────────────────

def compute_band_cooperation(band: "Band") -> dict:
    """Compute emergent cooperation metrics for a single band.

    Implements multi-level decomposition following Price (1970) and
    Bowles (2006, Science 314:1569).  Returns the components needed
    to evaluate whether between-group selection can maintain cooperation
    against within-group free-riding.

    Components
    ----------
    mean_cooperation : float
        Mean cooperation_propensity across living adults.
        This is the genetic component of the Price equation's
        within-group term.  (Price 1970, Eq. 2)

    cooperation_variance : float
        Variance in cooperation_propensity.  High variance means
        stronger within-group selection pressure against cooperators
        (defectors outcompete cooperators within the group).

    mean_effective_cooperation : float
        Mean of compute_individual_cooperation() across adults.
        Captures gene × culture interaction (trait × belief composite).

    trust_network_density : float
        Fraction of possible directed trust links that exceed the
        cooperation threshold (default 0.5).  Represents the
        structural precondition for reciprocal altruism.
        (Nowak 2006: network reciprocity as a mechanism for
        cooperation maintenance)

    conformity_amplification : float
        Mean-conformity-driven amplification factor (Henrich 2004).
        High conformity_bias in the population stabilises cooperative
        norms via conformist cultural transmission.
        Factor: (1 + mean_conformity × 0.3), matching
        engines/institutions.py:237.

    collective_action_capacity : float
        Composite metric: mean_cooperation (genetic baseline) plus
        network and cultural bonuses.  Additive decomposition avoids
        the degenerate-zero problem when trust networks are sparse
        in early simulation years (kin-trust bootstrap, Phase 0).

        CAC = mean_cooperation
              + mean_eff_cooperation × density × 0.5
              + mean_cooperation × (conformity_amp - 1.0)

        The genetic baseline (first term) ensures CAC > 0 whenever
        cooperation genes are present, consistent with the paper's
        gene → cooperation → institution pathway.
    """
    living = band.get_living()
    adults = [a for a in living if a.age >= _BELIEF_MATURATION_AGE]

    if not adults:
        return _empty_band_metrics()

    n = len(adults)

    # ── (1) Genetic cooperation: mean and variance (Price 1970) ──────────
    coop_vals = np.array([a.cooperation_propensity for a in adults])
    mean_coop = float(np.mean(coop_vals))
    var_coop = float(np.var(coop_vals))

    # ── (2) Effective cooperation: gene × culture composite ──────────────
    eff_scores = [compute_individual_cooperation(a) for a in adults]
    mean_eff = float(np.mean(eff_scores))

    # ── (3) Trust network density (Nowak 2006: network reciprocity) ──────
    active_links = 0
    for a in adults:
        for trust_val in a.reputation_ledger.values():
            if trust_val > _TRUST_THRESHOLD:
                active_links += 1
    possible_links = max(n * (n - 1), 1)  # directed links
    density = min(1.0, active_links / possible_links)

    # ── (4) Conformity amplification (Henrich 2004) ──────────────────────
    mean_conformity = float(np.mean([a.conformity_bias for a in adults]))
    conformity_amp = 1.0 + mean_conformity * _CONFORMITY_COEFF

    # ── (5) Collective action capacity (additive decomposition) ──────────
    # Additive form ensures genetic baseline is always represented.
    # CRITIC-VALIDATED: multiplicative form was rejected because it
    # produces CAC ≈ 0 in early years when trust_density ≈ 0, which
    # contradicts the kin-trust bootstrap (resources.py Phase 0).
    cac = (
        mean_coop
        + mean_eff * density * 0.5
        + mean_coop * (conformity_amp - 1.0)
    )

    _log.debug(
        "Band %d cooperation: mean=%.3f, var=%.4f, eff=%.3f, "
        "density=%.3f, conformity_amp=%.3f, CAC=%.3f",
        band.band_id, mean_coop, var_coop, mean_eff,
        density, conformity_amp, cac,
    )

    return {
        "mean_cooperation": mean_coop,
        "cooperation_variance": var_coop,
        "mean_effective_cooperation": mean_eff,
        "trust_network_density": density,
        "conformity_amplification": conformity_amp,
        "collective_action_capacity": cac,
    }


# ── Clan-level cooperation ──────────────────────────────────────────────────

def compute_clan_cooperation(clan_society: "ClanSociety") -> dict:
    """Compute clan-level cooperation metrics across all bands.

    Implements the between-group component of the Price equation
    (Price 1970; Bowles 2006).  The key insight from the paper:
    between-band variance in cooperation (analogous to Fst) drives
    group selection, while within-band variance drives individual
    selection against cooperators.

    Returns
    -------
    dict with:
        per_band : dict[int, dict]
            Per-band cooperation metrics from compute_band_cooperation().
        clan_mean_cooperation : float
            Population-weighted mean cooperation_propensity across all bands.
        clan_cooperation_variance : float
            Between-band variance in mean cooperation (Price equation
            between-group term).  Higher values indicate stronger
            group selection potential.
        mean_collective_action_capacity : float
            Simple mean of CAC across bands.
        mean_inter_band_trust : float
            Mean bilateral trust across all band pairs.  Captures
            the inter-group cooperation climate.
    """
    band_results: dict[int, dict] = {}
    for bid, band in clan_society.bands.items():
        band_results[bid] = compute_band_cooperation(band)

    if not band_results:
        return _empty_clan_metrics()

    # ── Population-weighted clan mean (Price 1970) ───────────────────────
    total_pop = 0
    weighted_coop_sum = 0.0
    coop_means = []
    cac_values = []

    for bid, metrics in band_results.items():
        band = clan_society.bands[bid]
        pop = band.population_size()
        total_pop += pop
        weighted_coop_sum += metrics["mean_cooperation"] * pop
        coop_means.append(metrics["mean_cooperation"])
        cac_values.append(metrics["collective_action_capacity"])

    clan_mean = weighted_coop_sum / max(total_pop, 1)

    # ── Between-band variance (group selection potential) ────────────────
    between_var = float(np.var(coop_means))

    # ── Mean collective action capacity ──────────────────────────────────
    mean_cac = float(np.mean(cac_values))

    # ── Mean inter-band trust ────────────────────────────────────────────
    trust_vals = []
    band_ids = sorted(clan_society.bands.keys())
    for i, bid_a in enumerate(band_ids):
        for bid_b in band_ids[i + 1 :]:
            t_ab = clan_society.bands[bid_a].trust_toward(bid_b)
            t_ba = clan_society.bands[bid_b].trust_toward(bid_a)
            trust_vals.append((t_ab + t_ba) / 2.0)

    mean_trust = float(np.mean(trust_vals)) if trust_vals else 0.0

    _log.debug(
        "Clan cooperation: mean=%.3f, between_var=%.4f, "
        "mean_CAC=%.3f, mean_trust=%.3f",
        clan_mean, between_var, mean_cac, mean_trust,
    )

    return {
        "per_band": band_results,
        "clan_mean_cooperation": clan_mean,
        "clan_cooperation_variance": between_var,
        "mean_collective_action_capacity": mean_cac,
        "mean_inter_band_trust": mean_trust,
    }


# ── Empty-result helpers ─────────────────────────────────────────────────────

def _empty_band_metrics() -> dict:
    """Return zeroed band cooperation metrics (no living adults)."""
    return {
        "mean_cooperation": 0.0,
        "cooperation_variance": 0.0,
        "mean_effective_cooperation": 0.0,
        "trust_network_density": 0.0,
        "conformity_amplification": 1.0,
        "collective_action_capacity": 0.0,
    }


def _empty_clan_metrics() -> dict:
    """Return zeroed clan cooperation metrics (no bands)."""
    return {
        "per_band": {},
        "clan_mean_cooperation": 0.0,
        "clan_cooperation_variance": 0.0,
        "mean_collective_action_capacity": 0.0,
        "mean_inter_band_trust": 0.0,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# MILESTONE 2: Trade Cooperation
# Grounding: Wiessner (1982), Smith & Bird (2000), clan_trade.py
# ═══════════════════════════════════════════════════════════════════════════════

# Social skill negotiation bonus: 1.0 + social_skill × 0.10
# Coefficient matches engines/clan_trade.py line 330.
_SOCIAL_SKILL_TRADE_COEFF = 0.10

# outgroup_tolerance refusal threshold (clan_trade.py:70).
_TRADE_REFUSAL_THRESHOLD = 0.25

# Scarcity threshold below which bands trade desperately (clan_trade.py:83).
_SCARCITY_THRESHOLD = 3.0


def compute_band_trade_openness(band: "Band") -> dict:
    """Compute a band's propensity for successful inter-band trade.

    Grounding: Wiessner (1982) — inter-group exchange as risk-pooling.
    Smith & Bird (2000) — trade surplus as cooperative signalling.

    Components
    ----------
    mean_outgroup_tolerance : float
        Mean outgroup_tolerance across PRIME/MATURE adults.
        This is the primary gate for trade participation.
        Agents with outgroup_tolerance < 0.25 may refuse trade
        (clan_trade.py:70, _DEFAULT_REFUSAL_THRESHOLD).

    trade_willingness : float
        Fraction of adults who would NOT refuse trade.
        Computed as: fraction with outgroup_tolerance >= refusal_threshold.
        Higher = more agents willing to engage in inter-band exchange.

    mean_social_skill : float
        Mean social_skill across adults (negotiation advantage).
        Modulates surplus extraction: bonus = 1 + social_skill × 0.10
        (clan_trade.py:330).

    trade_capacity : float
        Composite: trade_willingness × (1 + mean_social_skill × 0.10).
        Represents the band's overall capacity for productive trade.
        CRITIC-VALIDATED: Builder originally used 0.15 coefficient;
        corrected to 0.10 to match frozen engine.
    """
    living = band.get_living()
    adults = [a for a in living if a.life_stage in ("PRIME", "MATURE")]

    if not adults:
        return _empty_trade_metrics()

    # Mean outgroup tolerance (trade gate)
    tol_vals = [a.outgroup_tolerance for a in adults]
    mean_tol = float(np.mean(tol_vals))

    # Trade willingness: fraction above refusal threshold
    willing = sum(1 for t in tol_vals if t >= _TRADE_REFUSAL_THRESHOLD)
    trade_willingness = willing / len(adults)

    # Social skill advantage (Wiessner 1982: skilled negotiators extract surplus)
    skill_vals = [a.social_skill for a in adults]
    mean_skill = float(np.mean(skill_vals))

    # Trade capacity composite
    # CRITIC-VALIDATED: coefficient 0.10, not 0.15
    trade_capacity = trade_willingness * (1.0 + mean_skill * _SOCIAL_SKILL_TRADE_COEFF)

    _log.debug(
        "Band %d trade: tol=%.3f, willingness=%.3f, skill=%.3f, capacity=%.3f",
        band.band_id, mean_tol, trade_willingness, mean_skill, trade_capacity,
    )

    return {
        "mean_outgroup_tolerance": mean_tol,
        "trade_willingness": trade_willingness,
        "mean_social_skill": mean_skill,
        "trade_capacity": trade_capacity,
    }


def compute_clan_trade_openness(clan_society: "ClanSociety") -> dict:
    """Compute clan-level trade metrics across all bands.

    Returns
    -------
    dict with:
        per_band : dict[int, dict] — per-band trade metrics
        clan_mean_trade_capacity : float — mean trade capacity across bands
        clan_trade_capacity_variance : float — between-band variance
    """
    band_results: dict[int, dict] = {}
    capacities = []

    for bid, band in clan_society.bands.items():
        band_results[bid] = compute_band_trade_openness(band)
        capacities.append(band_results[bid]["trade_capacity"])

    if not capacities:
        return {"per_band": {}, "clan_mean_trade_capacity": 0.0,
                "clan_trade_capacity_variance": 0.0}

    return {
        "per_band": band_results,
        "clan_mean_trade_capacity": float(np.mean(capacities)),
        "clan_trade_capacity_variance": float(np.var(capacities)),
    }


def _empty_trade_metrics() -> dict:
    """Return zeroed trade metrics."""
    return {
        "mean_outgroup_tolerance": 0.0,
        "trade_willingness": 0.0,
        "mean_social_skill": 0.0,
        "trade_capacity": 0.0,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# MILESTONE 3: Coalition Defence Cooperation
# Grounding: Bowles (2006), Bowles & Gintis (2011), clan_raiding.py
# ═══════════════════════════════════════════════════════════════════════════════

# Cooperation cohesion bonus: mean_coop × bowles_scale × 0.20
# Coefficient matches engines/clan_raiding.py line 610.
_COHESION_BONUS_COEFF = 0.20

# p_join = group_loyalty × bowles_scale × (1 + cooperation × 0.5)
# Cooperation modifier 0.5 from clan_raiding.py line 504.
_COOP_DEFENCE_MODIFIER = 0.5

# p_join floor: even low-loyalty agents have 5% chance of joining defence.
# Matches clan_raiding.py line 513, Keeley (1996).
_P_JOIN_FLOOR = 0.05

# Default Bowles coalition scale (clan_raiding.py:122, ClanConfig default).
_DEFAULT_BOWLES_SCALE = 1.0


def compute_band_defence_capacity(
    band: "Band",
    bowles_coalition_scale: float = _DEFAULT_BOWLES_SCALE,
) -> dict:
    """Compute a band's capacity for coordinated coalition defence.

    Grounding: Bowles (2006, Science 314:1569) — group selection
    maintains cooperation through inter-group conflict.  Coalition
    size scales with group_loyalty; cohesion scales with cooperation.

    Components
    ----------
    mean_group_loyalty : float
        Mean group_loyalty across PRIME/MATURE adults.
        Primary driver of coalition size (Bowles 2006, Eq. 3).

    mean_coalition_probability : float
        Mean p_join across eligible defenders.
        p_join = max(floor, loyalty × scale × (1 + coop × 0.5))
        (clan_raiding.py:504, 513).

    coalition_cohesion_bonus : float
        Defensive cohesion from cooperation: mean_coop × scale × 0.20
        (clan_raiding.py:610).
        CRITIC-VALIDATED: Builder originally used 0.25;
        corrected to 0.20 to match frozen engine.

    defence_capacity : float
        Composite: mean_p_join × (1 + cohesion_bonus).
        Captures both coalition SIZE (loyalty-driven) and
        coalition QUALITY (cooperation-driven).
    """
    living = band.get_living()
    adults = [a for a in living if a.life_stage in ("PRIME", "MATURE")]

    if not adults:
        return _empty_defence_metrics()

    # Coalition join probability per agent (Bowles mechanism)
    p_joins = []
    for a in adults:
        effective_loyalty = a.group_loyalty * bowles_coalition_scale
        p_join = effective_loyalty * (1.0 + a.cooperation_propensity * _COOP_DEFENCE_MODIFIER)
        p_join = float(max(_P_JOIN_FLOOR, min(1.0, p_join)))
        p_joins.append(p_join)

    mean_p_join = float(np.mean(p_joins))

    # Group loyalty (raw trait mean)
    mean_loyalty = float(np.mean([a.group_loyalty for a in adults]))

    # Coalition cohesion bonus (Bowles & Gintis 2011)
    mean_coop = float(np.mean([a.cooperation_propensity for a in adults]))
    cohesion = mean_coop * bowles_coalition_scale * _COHESION_BONUS_COEFF

    # Defence capacity composite
    defence_cap = mean_p_join * (1.0 + cohesion)

    _log.debug(
        "Band %d defence: loyalty=%.3f, mean_p_join=%.3f, "
        "cohesion=%.3f, capacity=%.3f",
        band.band_id, mean_loyalty, mean_p_join, cohesion, defence_cap,
    )

    return {
        "mean_group_loyalty": mean_loyalty,
        "mean_coalition_probability": mean_p_join,
        "coalition_cohesion_bonus": cohesion,
        "defence_capacity": defence_cap,
    }


def compute_clan_defence_capacity(
    clan_society: "ClanSociety",
    bowles_coalition_scale: float = _DEFAULT_BOWLES_SCALE,
) -> dict:
    """Compute clan-level defence metrics across all bands.

    Returns
    -------
    dict with:
        per_band : dict — per-band defence metrics
        clan_mean_defence_capacity : float
        clan_defence_capacity_variance : float
    """
    band_results: dict[int, dict] = {}
    capacities = []

    for bid, band in clan_society.bands.items():
        band_results[bid] = compute_band_defence_capacity(band, bowles_coalition_scale)
        capacities.append(band_results[bid]["defence_capacity"])

    if not capacities:
        return {"per_band": {}, "clan_mean_defence_capacity": 0.0,
                "clan_defence_capacity_variance": 0.0}

    return {
        "per_band": band_results,
        "clan_mean_defence_capacity": float(np.mean(capacities)),
        "clan_defence_capacity_variance": float(np.var(capacities)),
    }


def _empty_defence_metrics() -> dict:
    """Return zeroed defence metrics."""
    return {
        "mean_group_loyalty": 0.0,
        "mean_coalition_probability": 0.0,
        "coalition_cohesion_bonus": 0.0,
        "defence_capacity": 0.0,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# MILESTONE 4: Multi-Level Selection Pressure
# Grounding: Price (1970), Bowles (2006), clan_selection.py
# ═══════════════════════════════════════════════════════════════════════════════

# The 4 prosocial traits tracked for selection coefficients.
# CRITIC-VALIDATED: Builder originally proposed all 35 traits;
# corrected to these 4 to match frozen clan_selection.py:82-87.
_PROSOCIAL_TRAITS = (
    "cooperation_propensity",
    "group_loyalty",
    "outgroup_tolerance",
    "empathy_capacity",
)


def compute_band_selection_potential(band: "Band") -> dict:
    """Compute within-band trait composition relevant to multi-level selection.

    Grounding: Price equation (Price 1970).  Within-group selection acts
    on the VARIANCE of prosocial traits within a band — higher variance
    means stronger within-group selection (defectors exploit cooperators).

    Components
    ----------
    prosocial_means : dict[str, float]
        Mean of each prosocial trait across PRIME/MATURE adults.

    prosocial_variances : dict[str, float]
        Variance of each prosocial trait.  Higher within-band variance
        drives stronger within-group selection against cooperators.

    prosocial_composite : float
        Mean of the 4 prosocial trait means.  A single scalar representing
        the band's overall prosocial trait endowment.

    within_variance_composite : float
        Mean of the 4 prosocial trait variances.  Higher values indicate
        greater potential for within-group selection to erode cooperation.
    """
    living = band.get_living()
    adults = [a for a in living if a.life_stage in ("PRIME", "MATURE")]

    if not adults:
        return _empty_selection_metrics()

    prosocial_means: dict[str, float] = {}
    prosocial_variances: dict[str, float] = {}

    for trait in _PROSOCIAL_TRAITS:
        vals = np.array([getattr(a, trait) for a in adults])
        prosocial_means[trait] = float(np.mean(vals))
        prosocial_variances[trait] = float(np.var(vals))

    composite = float(np.mean(list(prosocial_means.values())))
    var_composite = float(np.mean(list(prosocial_variances.values())))

    _log.debug(
        "Band %d selection potential: composite=%.3f, within_var=%.4f",
        band.band_id, composite, var_composite,
    )

    return {
        "prosocial_means": prosocial_means,
        "prosocial_variances": prosocial_variances,
        "prosocial_composite": composite,
        "within_variance_composite": var_composite,
    }


def compute_clan_selection_potential(clan_society: "ClanSociety") -> dict:
    """Compute clan-level multi-level selection metrics.

    Grounding: Price (1970), Bowles (2006).

    The key quantity is the RATIO of between-band to within-band
    variance (analogous to Fst).  When between > within, group
    selection can maintain cooperation against individual-level
    exploitation.

    Returns
    -------
    dict with:
        per_band : dict — per-band selection potential
        clan_prosocial_composite : float — population-weighted mean
        between_band_variance : float — variance of band means (group selection driver)
        within_band_variance : float — mean within-band variance (individual selection driver)
        selection_ratio : float — between / within (Fst analogue; > 1 favours group selection)
    """
    band_results: dict[int, dict] = {}
    composites = []
    within_vars = []

    for bid, band in clan_society.bands.items():
        band_results[bid] = compute_band_selection_potential(band)
        composites.append(band_results[bid]["prosocial_composite"])
        within_vars.append(band_results[bid]["within_variance_composite"])

    if not composites:
        return {"per_band": {}, "clan_prosocial_composite": 0.0,
                "between_band_variance": 0.0, "within_band_variance": 0.0,
                "selection_ratio": 0.0}

    clan_composite = float(np.mean(composites))
    between_var = float(np.var(composites))
    within_var = float(np.mean(within_vars))

    # Selection ratio: between / within (Fst analogue)
    # > 1 means group selection can overcome individual selection
    selection_ratio = between_var / max(within_var, 1e-8)

    _log.debug(
        "Clan selection: composite=%.3f, between=%.4f, within=%.4f, ratio=%.4f",
        clan_composite, between_var, within_var, selection_ratio,
    )

    return {
        "per_band": band_results,
        "clan_prosocial_composite": clan_composite,
        "between_band_variance": between_var,
        "within_band_variance": within_var,
        "selection_ratio": selection_ratio,
    }


def _empty_selection_metrics() -> dict:
    """Return zeroed selection metrics."""
    return {
        "prosocial_means": {t: 0.0 for t in _PROSOCIAL_TRAITS},
        "prosocial_variances": {t: 0.0 for t in _PROSOCIAL_TRAITS},
        "prosocial_composite": 0.0,
        "within_variance_composite": 0.0,
    }
