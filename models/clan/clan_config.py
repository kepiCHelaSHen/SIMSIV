"""
ClanConfig — v2 clan-simulator configuration parameters.

This dataclass holds parameters that are specific to the multi-band (clan)
layer of SIMSIV v2.  It is deliberately separate from the v1 Config dataclass,
which is frozen (paper submitted).

Usage::

    from models.clan.clan_config import ClanConfig
    clan_cfg = ClanConfig()  # all defaults
    clan_cfg = ClanConfig(trade_party_size=5, raid_loot_fraction=0.35)

Architecture note
-----------------
ClanConfig is a pure data container — it imports nothing from engines or
simulation.  Engines import it freely without circular-import risk.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ClanConfig:
    """All tunable parameters for the v2 inter-band (clan) simulation layer.

    Parameters are grouped by subsystem.  Defaults are calibrated to produce
    plausible inter-band dynamics for band-level forager societies (~25-50 agents
    per band) based on Bowles (2006), Wiessner (1982), and Keeley (1996).
    """

    # ── Trade parameters ───────────────────────────────────────────────────────
    # Maximum number of trader pairs per inter-band trade session.
    # Actual count = min(n_adults_a, n_adults_b, trade_party_size) * trust.
    trade_party_size: int = 3

    # outgroup_tolerance threshold below which an agent may refuse to trade.
    # Agents exactly at threshold refuse with p=0; agents at 0 always refuse.
    trade_refusal_threshold: float = 0.25

    # ── Raiding parameters ─────────────────────────────────────────────────────
    # Baseline annual probability a band even considers raiding a neighbour.
    # Multiplied by scarcity pressure and mean aggression to get final p_raid.
    raid_base_probability: float = 0.10

    # scarcity threshold (mean resources per agent) below which raids become
    # much more likely.  Values match clan_trade._SCARCITY_THRESHOLD = 3.0.
    raid_scarcity_threshold: float = 3.0

    # Maximum fraction of defenders' resources that can be looted per raid.
    # Actual loot scales with victory margin: loot = loot_fraction * margin.
    raid_loot_fraction: float = 0.30

    # Fraction of raiding party members that can be killed in combat (upper
    # bound — actual casualties are probabilistic).
    raid_attacker_casualty_rate: float = 0.15

    # Fraction of defending coalition members that can be killed per raid.
    raid_defender_casualty_rate: float = 0.20

    # Maximum proportion of band population that join the raiding party.
    raid_party_max_fraction: float = 0.35

    # Maximum proportion of band population that join the defensive coalition.
    raid_defense_max_fraction: float = 0.50

    # Trust penalty applied to both bands after a raid (attacker's side).
    # Raids are much more trust-destructive than hostile contact events.
    raid_trust_loss_attacker: float = 0.15

    # Trust penalty applied to the defender's record of the attacker.
    # Asymmetric: victims remember raids more strongly than aggressors.
    raid_trust_loss_defender: float = 0.25

    # Minimum bilateral trust below which raiding risk is elevated.
    # When trust >= this value, raid probability is suppressed.
    raid_trust_suppression_threshold: float = 0.4

    # Scale factor for the Bowles coalition-defence benefit.
    # Higher → larger defensive coalitions → bigger defensive bonus.
    # Applied directly to group_loyalty in p_join computation so that
    # bowles_coalition_scale > 1 amplifies the loyalty → coalition size link.
    # Ref: Bowles (2006) Science 314(5805), Eq. 3.
    bowles_coalition_scale: float = 1.0

    # Floor probability for any eligible agent joining the defensive coalition.
    # Ethnographic evidence (Keeley 1996) indicates that even low-loyalty members
    # participate in group defence when their band is physically threatened.
    # The floor prevents a degenerate all-zero coalition in low-loyalty bands.
    # Set to 0.05 (5%) — low enough to preserve selection signal, high enough
    # to avoid behavioural implausibility.  Make 0.0 to disable the floor.
    p_join_floor: float = 0.05

    # ── Between-group selection parameters (Turn 4) ─────────────────────────

    # Band population above which fission (splitting) is triggered.
    # Default 150: Dunbar (1992) cognitive limit for stable social relationships
    # in human hunter-gatherer groups.
    fission_threshold: int = 150

    # Band population below which extinction (absorption by nearest band) occurs.
    # Default 10: minimum viable population for a forager band to maintain
    # reproductive and defensive viability (Hill et al. 2011).
    extinction_threshold: int = 10

    # Annual per-agent probability of inter-band migration (gene flow).
    # Low values (~0.005) oppose between-group selection by reducing Fst.
    # Empirical estimate: ~0.5-2% annual inter-band migration in foragers
    # (Wiessner 1982; Hill et al. 2011).
    migration_rate_per_agent: float = 0.005
