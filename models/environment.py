"""
Environment model — resource availability, scarcity shocks, carrying capacity,
epidemic events (DD09).
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
        self.current_scarcity_level = 0.0  # computed once per tick

        # DD09: Epidemic state
        self.in_epidemic = False
        self.epidemic_remaining = 0
        self.years_since_last_epidemic = 999  # start as if long ago

        # DD10: Seasonal cycle state
        self.seasonal_phase = 0.0  # [-1, 1]: -1=trough, 0=transition, 1=peak

    @property
    def carrying_capacity(self) -> int:
        return self.config.carrying_capacity

    def get_scarcity_level(self) -> float:
        """0.0 = no scarcity, 1.0 = maximum scarcity. Computed once per tick."""
        return self.current_scarcity_level

    def get_resource_multiplier(self) -> float:
        """How much resources are available this tick relative to baseline."""
        vol = self.config.resource_volatility
        noise = self.rng.normal(0, vol)
        base = self.abundance_multiplier + noise

        # DD10: Seasonal cycle modulation
        if getattr(self.config, 'seasonal_cycle_enabled', False):
            amplitude = getattr(self.config, 'seasonal_amplitude', 0.3)
            base *= (1.0 + self.seasonal_phase * amplitude)

        if self.in_scarcity:
            base *= getattr(self.config, 'scarcity_severity', 0.6)
        return max(0.1, base)

    def tick(self, population_size: int) -> list[dict]:
        """Advance one year. Returns list of environment events."""
        self.year += 1
        events = []

        # Compute scarcity level once for this tick (all engines read the stored value)
        if self.in_scarcity:
            self.current_scarcity_level = 0.6 + self.rng.uniform(0, 0.3)
        else:
            self.current_scarcity_level = 0.0

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
            base_shock = getattr(self.config, 'scarcity_event_probability', 0.03)
            shock_chance = base_shock + overcrowding * 0.1
            if self.rng.random() < shock_chance:
                self.in_scarcity = True
                self.scarcity_remaining = self.rng.integers(2, 6)
                events.append({
                    "type": "scarcity_start",
                    "year": self.year,
                    "description": f"Scarcity shock — {self.scarcity_remaining} years",
                })

        # ── DD10: Update seasonal cycle phase ─────────────────────────
        if getattr(self.config, 'seasonal_cycle_enabled', False):
            cycle_len = max(1, getattr(self.config, 'seasonal_cycle_length', 3))
            import math
            self.seasonal_phase = math.cos(2 * math.pi * self.year / cycle_len)
        else:
            self.seasonal_phase = 0.0

        # ── DD09: Epidemic event management ──────────────────────────
        self.years_since_last_epidemic += 1

        if self.in_epidemic:
            self.epidemic_remaining -= 1
            if self.epidemic_remaining <= 0:
                self.in_epidemic = False
                events.append({
                    "type": "epidemic_end",
                    "year": self.year,
                    "description": "Epidemic has subsided",
                })
        else:
            refractory = getattr(self.config, 'epidemic_refractory_period', 20)
            if self.years_since_last_epidemic >= refractory:
                base_p = getattr(self.config, 'epidemic_base_probability', 0.02)

                # Overcrowding increases epidemic risk
                capacity_ratio = population_size / max(1, self.carrying_capacity)
                if capacity_ratio > 0.8:
                    overcrowd_mult = getattr(
                        self.config, 'epidemic_overcrowding_multiplier', 2.0)
                    base_p *= 1.0 + (capacity_ratio - 0.8) * overcrowd_mult

                # Scarcity compounds epidemic risk (malnutrition weakens immune response)
                if self.in_scarcity:
                    base_p *= 1.5

                if self.rng.random() < base_p:
                    duration = getattr(self.config, 'epidemic_duration_years', 2)
                    self.in_epidemic = True
                    self.epidemic_remaining = max(1, duration)
                    self.years_since_last_epidemic = 0
                    events.append({
                        "type": "epidemic_start",
                        "year": self.year,
                        "description": (f"Epidemic outbreak — "
                                        f"est. duration {self.epidemic_remaining} years"),
                    })

        return events
