"""
models.clan — multi-band social simulation layer (SIMSIV v2).

Public exports:
  Band         — a named band that wraps a single Society
  ClanSociety  — registry of multiple Bands + inter-band relationship state
"""

from .band import Band
from .clan_society import ClanSociety

__all__ = ["Band", "ClanSociety"]
