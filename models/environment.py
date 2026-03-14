"""
Environment model — resource availability, scarcity shocks, carrying capacity.
"""

from __future__ import annotations
import numpy as np


class Environment:
    def __init__(self, config, rng: np.random.Generator):
        self.config = config
        self.rng = rng
        self.year = 0
        self.abundance_multiplier = config.resource_abundance
        self.in_scarcity = False
        self.scarcity_remaining = 0

    @property
    def carrying_capacity(self) -> int:
        return self.config.carrying_capacity

    def get_scarcity_level(self) -> float:
        """0.0 = no scarcity, 1.0 = maximum scarcity."""
        if self.in_scarcity:
            return 0.6 + self.rng.uniform(0, 0.3)
        return 0.0

    def get_resource_multiplier(self) -> float:
        """How much resources are available this tick relative to baseline."""
        vol = self.config.resource_volatility
        noise = self.rng.normal(0, vol)
        base = self.abundance_multiplier + noise
        if self.in_scarcity:
            base *= 0.4  # scarcity cuts resources by 60%
        return max(0.1, base)

    def tick(self, population_size: int) -> list[dict]:
        """Advance one year. Returns list of environment events."""
        self.year += 1
        events = []

        # Scarcity shock management
        if self.in_scarcity:
            self.scarcity_remaining -= 1
            if self.scarcity_remaining <= 0:
                self.in_scarcity = False
                events.append({
                    "type": "scarcity_end",
                    "year": self.year,
                    "description": "Scarcity period ended",
                })
        else:
            # Random scarcity shock — more likely when overcrowded
            overcrowding = max(0, population_size / self.carrying_capacity - 0.8)
            shock_chance = 0.03 + overcrowding * 0.1
            if self.rng.random() < shock_chance:
                self.in_scarcity = True
                self.scarcity_remaining = self.rng.integers(2, 6)
                events.append({
                    "type": "scarcity_start",
                    "year": self.year,
                    "description": f"Scarcity shock — {self.scarcity_remaining} years",
                })

        return events
