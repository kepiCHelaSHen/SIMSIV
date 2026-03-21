"""
models.clan — multi-band social simulation layer (SIMSIV v2).

Public exports:
  Band            — a named band that wraps a single Society
  ClanSociety     — registry of multiple Bands + inter-band relationship state
  ClanConfig      — v2 clan-layer configuration parameters (Turn 3)
  ClanSimulation  — high-level wrapper for multi-band experiments (Turn 6)
"""

from .band import Band
from .clan_society import ClanSociety
from .clan_config import ClanConfig
from .clan_simulation import ClanSimulation

__all__ = ["Band", "ClanSociety", "ClanConfig", "ClanSimulation"]
