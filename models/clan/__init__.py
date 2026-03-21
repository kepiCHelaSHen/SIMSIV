"""
models.clan — multi-band social simulation layer (SIMSIV v2).

Public exports:
  Band         — a named band that wraps a single Society
  ClanSociety  — registry of multiple Bands + inter-band relationship state
  ClanConfig   — v2 clan-layer configuration parameters (Turn 3)
"""

from .band import Band
from .clan_society import ClanSociety
from .clan_config import ClanConfig

__all__ = ["Band", "ClanSociety", "ClanConfig"]
