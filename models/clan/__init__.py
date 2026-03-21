"""
models.clan — multi-band social simulation layer (SIMSIV v2).

Public exports:
  Band            — a named band that wraps a single Society
  ClanSociety     — registry of multiple Bands + inter-band relationship state
  ClanConfig      — v2 clan-layer configuration parameters (Turn 3)
  ClanSimulation  — high-level wrapper for multi-band experiments (Turn 6)
  compute_individual_cooperation  — per-agent cooperation score (Turn 11)
  compute_band_cooperation        — band-level cooperation metrics (Turn 11)
  compute_clan_cooperation        — clan-level cooperation metrics (Turn 11)
"""

from .band import Band
from .clan_society import ClanSociety
from .clan_config import ClanConfig
from .clan_simulation import ClanSimulation
from .clan_base import (
    compute_individual_cooperation,
    compute_band_cooperation,
    compute_clan_cooperation,
    compute_band_trade_openness,
    compute_clan_trade_openness,
    compute_band_defence_capacity,
    compute_clan_defence_capacity,
    compute_band_selection_potential,
    compute_clan_selection_potential,
)

__all__ = [
    "Band",
    "ClanSociety",
    "ClanConfig",
    "ClanSimulation",
    "compute_individual_cooperation",
    "compute_band_cooperation",
    "compute_clan_cooperation",
    "compute_band_trade_openness",
    "compute_clan_trade_openness",
    "compute_band_defence_capacity",
    "compute_clan_defence_capacity",
    "compute_band_selection_potential",
    "compute_clan_selection_potential",
]
