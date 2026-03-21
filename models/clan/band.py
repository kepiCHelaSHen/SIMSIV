"""
Band model — wraps a Society as a named, identified band.

A Band is the basic multi-group unit: one Society plus metadata that
identifies it within a wider ClanSociety.  Composition (HAS-A) is used
rather than inheritance so that the Band layer never touches engine code
and the underlying Society remains independently valid.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from models.society import Society
    from config import Config

_log = logging.getLogger(__name__)


class Band:
    """A named band that wraps a single Society instance.

    Parameters
    ----------
    band_id:
        Unique integer identifier for this band within the ClanSociety.
    name:
        Human-readable label (e.g. "Northern Band").
    config:
        Config object — passed through to the underlying Society.
    rng:
        Seeded numpy.random.Generator.  Each Band receives its own rng
        so that band order does not affect any band's internal trajectory.
    origin_year:
        Simulation year at which this band was created.  0 for founding bands.
    """

    def __init__(
        self,
        band_id: int,
        name: str,
        config: "Config",
        rng: np.random.Generator,
        origin_year: int = 0,
    ) -> None:
        # Import here to avoid any chance of circular import at module load time.
        # (models.society imports config and models.agent — neither imports Band.)
        from models.society import Society

        self._band_id: int = band_id
        self._name: str = name
        self._origin_year: int = origin_year

        # Each Band owns its own seeded rng.  This rng is used for all intra-band
        # engine calls (_tick_band passes band.rng to each engine step), so that
        # band order in the clan tick does not influence any band's internal
        # trajectory.  The shared clan-level rng is used only for inter-band
        # scheduling and interactions.
        self.rng: np.random.Generator = rng

        # Each Band owns its own isolated Society (and therefore its own IdCounter,
        # event window, agent dict, etc.)
        self.society: Society = Society(config, rng)

        # Trust scores toward other bands: {other_band_id: float [0, 1]}
        # Initialised empty; populated by ClanSociety as bands meet.
        self.inter_band_trust: dict[int, float] = {}

        _log.debug(
            "Band %d ('%s') created at year %d (pop=%d)",
            band_id,
            name,
            origin_year,
            self.society.population_size(),
        )

    # ── Identity properties ─────────────────────────────────────────────────

    @property
    def band_id(self) -> int:
        return self._band_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def origin_year(self) -> int:
        return self._origin_year

    # ── Convenience delegation to the underlying Society ────────────────────

    def get_living(self):
        """Delegate to Society.get_living()."""
        return self.society.get_living()

    def population_size(self) -> int:
        """Delegate to Society.population_size()."""
        return self.society.population_size()

    def get_by_id(self, agent_id: int):
        """Delegate to Society.get_by_id()."""
        return self.society.get_by_id(agent_id)

    # ── Trust helpers ────────────────────────────────────────────────────────

    def trust_toward(self, other_band_id: int) -> float:
        """Return trust score toward another band (default 0.5 if never set)."""
        return self.inter_band_trust.get(other_band_id, 0.5)

    def update_trust(self, other_band_id: int, delta: float) -> None:
        """Apply an additive delta to trust toward another band, clamped [0, 1]."""
        current = self.inter_band_trust.get(other_band_id, 0.5)
        self.inter_band_trust[other_band_id] = float(
            max(0.0, min(1.0, current + delta))
        )
        _log.debug(
            "Band %d trust toward Band %d: %.3f -> %.3f",
            self._band_id,
            other_band_id,
            current,
            self.inter_band_trust[other_band_id],
        )

    # ── Dunder helpers ───────────────────────────────────────────────────────

    def __repr__(self) -> str:
        return (
            f"Band(id={self._band_id}, name='{self._name}', "
            f"pop={self.population_size()}, origin_year={self._origin_year})"
        )
