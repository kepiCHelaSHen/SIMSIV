"""
clan_trade.py — Inter-band resource exchange engine (SIMSIV v2).

Implements trade between two bands as a positive-sum exchange modulated by
bilateral trust and the outgroup_tolerance trait of participating traders.

Public interface
----------------
    trade_tick(band_a, band_b, trust, rng, config) -> list[dict]

Design
------
Trade is positive-sum: each successful exchange produces a ~5-15% net surplus
for both parties combined.  This is calibrated to hunter-gatherer ethnographic
evidence (Wiessner 1982; Smith & Bird 2000) where inter-group exchange acts as
a risk-pooling mechanism that exceeds zero-sum redistribution.

Three resource types are traded (DD21):
    current_resources     — subsistence (perishable, high demand)
    current_tools         — durable, low demand turnover
    current_prestige_goods — social capital, used in signal exchanges

Trust modulation
----------------
Bilateral trust (mean of A→B and B→A) gates:
  - Whether a trade session occurs at all (handled by caller via scheduling)
  - How many trader pairs participate
  - What fraction of surplus is transferred (higher trust → larger exchange)

Outgroup tolerance modulation
------------------------------
Each agent's outgroup_tolerance trait [0,1] governs:
  - Whether they agree to trade (refusal threshold 0.25)
  - Magnitude of their individual contribution to the exchange

Scarcity effect
---------------
Bands under resource stress (mean resources < scarcity_threshold) accept
less favourable trade terms (lower selectivity: they need resources now).

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

# Life stages eligible to act as traders (adults only).
_TRADER_STAGES = frozenset({"PRIME", "MATURE"})

# Default refusal threshold for outgroup_tolerance.
# Agents with outgroup_tolerance < this may refuse to trade.
_DEFAULT_REFUSAL_THRESHOLD: float = 0.25

# Positive-sum surplus range: each successful trade creates 5-15% extra value.
_SURPLUS_MIN: float = 0.05
_SURPLUS_MAX: float = 0.15

# Trust delta for a successful trade (per pair).
_TRUST_GAIN_SUCCESS: float = 0.02

# Trust delta for a refused trade.
_TRUST_LOSS_REFUSED: float = 0.03

# Mean-resource scarcity threshold below which bands trade "desperately".
_SCARCITY_THRESHOLD: float = 3.0

# Fraction of trader's surplus resource they are willing to offer per session.
_OFFER_FRACTION: float = 0.20


# ── Public API ────────────────────────────────────────────────────────────────

def trade_tick(
    band_a: "Band",
    band_b: "Band",
    trust: float,
    rng: np.random.Generator,
    config: "Config",
) -> list[dict]:
    """Run one inter-band trade session between band_a and band_b.

    Parameters
    ----------
    band_a, band_b:
        The two participating bands.  Order does not affect outcomes (symmetric).
    trust:
        Bilateral trust level [0, 1].  Mean of band_a.trust_toward(band_b) and
        band_b.trust_toward(band_a), computed by the caller (ClanEngine).
    rng:
        Seeded numpy.random.Generator.  All randomness goes through this.
    config:
        Shared simulation config.

    Returns
    -------
    list of event dicts, one per trader pair attempted.  Each dict has keys:
        type        : "inter_band_trade"
        year        : int  (populated by ClanEngine — set to 0 here as placeholder)
        agent_ids   : [trader_a_id, trader_b_id]
        description : str
        outcome     : "success" | "refused"
        band_a_id   : int
        band_b_id   : int
    """
    events: list[dict] = []

    # ── Select traders from each band ─────────────────────────────────────────
    traders_a = _select_traders(band_a, rng, config)
    traders_b = _select_traders(band_b, rng, config)

    if not traders_a or not traders_b:
        _log.debug(
            "trade_tick: Band %d or Band %d has no eligible traders — skipping.",
            band_a.band_id,
            band_b.band_id,
        )
        return events

    # ── Determine number of trader pairs ──────────────────────────────────────
    n_pairs = _compute_n_pairs(traders_a, traders_b, trust, config)
    if n_pairs == 0:
        return events

    # ── Scarcity flags ────────────────────────────────────────────────────────
    scarce_a = _is_scarce(band_a)
    scarce_b = _is_scarce(band_b)

    # ── Execute each trader pair ──────────────────────────────────────────────
    for _ in range(n_pairs):
        ta = traders_a[rng.integers(0, len(traders_a))]
        tb = traders_b[rng.integers(0, len(traders_b))]

        event = _execute_trade_pair(
            ta, tb,
            band_a, band_b,
            trust,
            scarce_a, scarce_b,
            rng, config,
        )
        events.append(event)

    _log.debug(
        "trade_tick: Band %d <-> Band %d — %d pairs, trust=%.3f, "
        "successes=%d, refused=%d",
        band_a.band_id,
        band_b.band_id,
        n_pairs,
        trust,
        sum(1 for e in events if e["outcome"] == "success"),
        sum(1 for e in events if e["outcome"] == "refused"),
    )

    return events


# ── Internal helpers ──────────────────────────────────────────────────────────

def _select_traders(band: "Band", rng: np.random.Generator, config: "Config") -> list:
    """Return a list of living PRIME/MATURE adults eligible to trade.

    Filters the band's living population to adults only.  If fewer than
    two adults exist, returns whatever is available (may be empty).
    """
    living = band.get_living()
    adults = [a for a in living if a.life_stage in _TRADER_STAGES]
    if not adults:
        _log.debug("Band %d: no PRIME/MATURE adults available as traders.", band.band_id)
    return adults


def _compute_n_pairs(
    traders_a: list,
    traders_b: list,
    trust: float,
    config: "Config | ClanConfig",
) -> int:
    """Compute the number of trader pairs for this session.

    Formula:
        base = min(len(traders_a), len(traders_b), trade_party_size)
        n    = max(1, round(base * trust))

    trade_party_size is read from config if present (ClanConfig defines it
    explicitly at 3); falls back to module constant 3 for v1 Config objects.
    """
    party_size: int = getattr(config, "trade_party_size", 3)
    base = min(len(traders_a), len(traders_b), party_size)
    n = max(1, round(base * trust))
    return n


def _is_scarce(band: "Band") -> bool:
    """Return True if the band's mean subsistence resources are below threshold."""
    living = band.get_living()
    if not living:
        return True
    mean_res = sum(a.current_resources for a in living) / len(living)
    return mean_res < _SCARCITY_THRESHOLD


def _compute_refusal_threshold(scarce: bool, config: "Config | ClanConfig") -> float:
    """Return outgroup_tolerance threshold below which an agent may refuse.

    Scarce bands are desperate: they lower their selectivity so that even
    low-outgroup-tolerance agents participate (survival need overrides xenophobia).

    trade_refusal_threshold is read from config if present (ClanConfig defines
    it explicitly at 0.25); falls back to _DEFAULT_REFUSAL_THRESHOLD for v1
    Config objects.
    """
    threshold: float = getattr(config, "trade_refusal_threshold", _DEFAULT_REFUSAL_THRESHOLD)
    if scarce:
        # Desperation lowers the bar — agents trade even if not particularly
        # tolerant of strangers.
        threshold *= 0.5
    return threshold


def _execute_trade_pair(
    trader_a,
    trader_b,
    band_a: "Band",
    band_b: "Band",
    trust: float,
    scarce_a: bool,
    scarce_b: bool,
    rng: np.random.Generator,
    config: "Config",
) -> dict:
    """Attempt one trade between trader_a (from band_a) and trader_b (from band_b).

    Returns a single event dict.

    Refusal logic
    -------------
    An agent refuses if their outgroup_tolerance is below the refusal threshold
    AND a uniform[0,1] draw confirms non-cooperation.  The probability of refusal
    given low tolerance is:
        p_refuse = max(0, threshold - outgroup_tolerance) / threshold

    This means agents at exactly the threshold refuse with probability 0, and
    agents at 0 tolerance always refuse (unless scarce band adjustments apply).

    Exchange logic (success)
    ------------------------
    Each trader offers a fraction of their surplus in each resource type.
    "Surplus" is resources above the subsistence floor.  The exchange rate is
    approximately 1-for-1 by value, but a positive-sum bonus (5-15%) is added
    to both parties' total receipts.

    Both agents' social_skill is used to moderate the exchange: more socially
    skilled traders negotiate better terms (slightly higher bonus).
    """
    refusal_thresh_a = _compute_refusal_threshold(scarce_a, config)
    refusal_thresh_b = _compute_refusal_threshold(scarce_b, config)

    # ── Refusal check for trader_a ────────────────────────────────────────────
    refused = False
    refusing_agent_id: int | None = None

    if trader_a.outgroup_tolerance < refusal_thresh_a:
        # Probability of refusal decreases as tolerance increases
        p_refuse_a = (refusal_thresh_a - trader_a.outgroup_tolerance) / max(refusal_thresh_a, 1e-6)
        if rng.random() < p_refuse_a:
            refused = True
            refusing_agent_id = trader_a.id

    if not refused and trader_b.outgroup_tolerance < refusal_thresh_b:
        p_refuse_b = (refusal_thresh_b - trader_b.outgroup_tolerance) / max(refusal_thresh_b, 1e-6)
        if rng.random() < p_refuse_b:
            refused = True
            refusing_agent_id = trader_b.id

    if refused:
        # Refusal: trust decreases for both bands
        band_a.update_trust(band_b.band_id, -_TRUST_LOSS_REFUSED)
        band_b.update_trust(band_a.band_id, -_TRUST_LOSS_REFUSED)

        _log.debug(
            "Trade refused: agent %d (Band %d) refused trade with agent %d (Band %d)",
            trader_a.id, band_a.band_id,
            trader_b.id, band_b.band_id,
        )
        return {
            "type": "inter_band_trade",
            "year": 0,  # filled in by caller
            "agent_ids": [trader_a.id, trader_b.id],
            "description": (
                f"Agent {refusing_agent_id} refused inter-band trade "
                f"(Band {band_a.band_id} <-> Band {band_b.band_id})"
            ),
            "outcome": "refused",
            "band_a_id": band_a.band_id,
            "band_b_id": band_b.band_id,
        }

    # ── Successful trade ──────────────────────────────────────────────────────
    floor = float(getattr(config, "subsistence_floor", 1.0))
    offer_fraction = _OFFER_FRACTION * trust  # higher trust → more generous exchange

    # Compute what each trader offers (from their surplus above subsistence floor)
    # Each resource type is traded independently.
    transferred_a_to_b: dict[str, float] = {}
    transferred_b_to_a: dict[str, float] = {}

    resource_fields = ("current_resources", "current_tools", "current_prestige_goods")

    # Social skill bonus: more skilled negotiators secure a better surplus.
    # Range: [1.00, 1.10] for social_skill in [0, 1].
    # NOTE: _SURPLUS_MIN must NOT appear here — it is baked into the rng.uniform
    # draw below.  Adding it here was a double-inflation bug (Turn 2 critique #1).
    skill_bonus_a = 1.0 + (trader_a.social_skill * 0.10)
    skill_bonus_b = 1.0 + (trader_b.social_skill * 0.10)

    # Positive-sum surplus fraction drawn uniformly per pair.
    surplus_frac = float(rng.uniform(_SURPLUS_MIN, _SURPLUS_MAX))

    for field in resource_fields:
        val_a = float(getattr(trader_a, field, 0.0))
        val_b = float(getattr(trader_b, field, 0.0))

        # Only the subsistence resource uses the hard floor; tools and prestige
        # goods have no floor — any positive amount is tradeable.
        if field == "current_resources":
            surplus_a = max(0.0, val_a - floor)
            surplus_b = max(0.0, val_b - floor)
        else:
            surplus_a = max(0.0, val_a)
            surplus_b = max(0.0, val_b)

        offer_a = surplus_a * offer_fraction
        offer_b = surplus_b * offer_fraction

        # Asymmetric-loss guard (Turn 2 critique #2): skip this resource type
        # if one side has nothing to offer.  A trade requires both parties to
        # give something — a one-sided transfer is not exchange; it is looting.
        if offer_a <= 0.0 or offer_b <= 0.0:
            transferred_a_to_b[field] = 0.0
            transferred_b_to_a[field] = 0.0
            continue

        transferred_a_to_b[field] = offer_a
        transferred_b_to_a[field] = offer_b

    # ── Apply transfers with positive-sum surplus ──────────────────────────────
    for field in resource_fields:
        give_a = transferred_a_to_b[field]
        give_b = transferred_b_to_a[field]

        # What each trader receives = what the other gives, × their skill bonus
        receive_a = give_b * skill_bonus_a * (1.0 + surplus_frac * 0.5)
        receive_b = give_a * skill_bonus_b * (1.0 + surplus_frac * 0.5)

        # Deduct what was given
        current_a = float(getattr(trader_a, field, 0.0))
        current_b = float(getattr(trader_b, field, 0.0))

        new_a = current_a - give_a + receive_a
        new_b = current_b - give_b + receive_b

        # Clamp to caps to prevent runaway accumulation.
        if field == "current_resources":
            cap = float(getattr(config, "resource_storage_cap", 20.0))
        elif field == "current_tools":
            cap = float(getattr(config, "tools_per_agent_cap", 10.0))
        else:
            cap = float(getattr(config, "prestige_goods_per_agent_cap", 5.0))

        setattr(trader_a, field, float(max(0.0, min(cap, new_a))))
        setattr(trader_b, field, float(max(0.0, min(cap, new_b))))

    # ── Update bilateral band trust ───────────────────────────────────────────
    band_a.update_trust(band_b.band_id, _TRUST_GAIN_SUCCESS)
    band_b.update_trust(band_a.band_id, _TRUST_GAIN_SUCCESS)

    # ── Update agent-level reputation ledger ──────────────────────────────────
    # Agents who trade successfully remember each other with a trust bump.
    trust_bump = 0.04 * (1.0 + trader_a.emotional_intelligence * 0.3)
    trader_a.remember(trader_b.id, trust_bump)
    trader_b.remember(trader_a.id, trust_bump)

    total_transferred = sum(transferred_a_to_b.values()) + sum(transferred_b_to_a.values())

    _log.debug(
        "Trade success: agent %d (Band %d) <-> agent %d (Band %d), "
        "total_volume=%.2f, surplus=%.1f%%",
        trader_a.id, band_a.band_id,
        trader_b.id, band_b.band_id,
        total_transferred,
        surplus_frac * 100,
    )

    return {
        "type": "inter_band_trade",
        "year": 0,  # filled in by caller
        "agent_ids": [trader_a.id, trader_b.id],
        "description": (
            f"Inter-band trade: agent {trader_a.id} (Band {band_a.band_id}) "
            f"<-> agent {trader_b.id} (Band {band_b.band_id}), "
            f"volume={total_transferred:.2f}, surplus={surplus_frac*100:.1f}%"
        ),
        "outcome": "success",
        "band_a_id": band_a.band_id,
        "band_b_id": band_b.band_id,
    }
