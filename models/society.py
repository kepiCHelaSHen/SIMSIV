"""
Society model — holds all agents, environment, and coordinates the simulation tick.
"""

from __future__ import annotations
from typing import Optional

import numpy as np

from .agent import Agent, Sex, create_initial_population
from .environment import Environment
from config import Config


class Society:
    def __init__(self, config: Config, rng: np.random.Generator):
        self.config = config
        self.rng = rng
        self.year = 0
        self.agents: dict[int, Agent] = {}
        self.environment = Environment(config, rng)
        self.events: list[dict] = []  # all events across all years
        self.tick_events: list[dict] = []  # events from current tick only
        self.equilibrium_flagged: bool = False
        self.equilibrium_year: Optional[int] = None

        # Initialize population
        pop = create_initial_population(rng, config, config.population_size)
        for a in pop:
            self.agents[a.id] = a

    def get_living(self) -> list[Agent]:
        return [a for a in self.agents.values() if a.alive]

    def get_living_by_sex(self, sex: Sex) -> list[Agent]:
        return [a for a in self.agents.values() if a.alive and a.sex == sex]

    def get_mating_eligible(self) -> tuple[list[Agent], list[Agent]]:
        """Returns (eligible_females, eligible_males)."""
        females = [a for a in self.agents.values()
                   if a.alive and a.sex == Sex.FEMALE and a.can_mate(self.config)]
        males = [a for a in self.agents.values()
                 if a.alive and a.sex == Sex.MALE and a.can_mate(self.config)]
        return females, males

    def get_by_id(self, agent_id: int) -> Optional[Agent]:
        return self.agents.get(agent_id)

    def add_agent(self, agent: Agent):
        self.agents[agent.id] = agent

    def population_size(self) -> int:
        return len(self.get_living())

    def add_event(self, event: dict):
        if "year" not in event:
            event["year"] = self.year
        self.tick_events.append(event)
        self.events.append(event)

    def inject_migrants(self, count: int):
        """Emergency population injection to prevent extinction."""
        from .agent import Agent, Sex, HERITABLE_TRAITS
        for i in range(count):
            sex = Sex.FEMALE if i < count // 2 else Sex.MALE
            a = Agent(sex=sex, age=int(self.rng.integers(18, 35)), generation=0)
            for trait in HERITABLE_TRAITS:
                setattr(a, trait, float(self.rng.uniform(0.2, 0.8)))
            a.current_resources = float(self.rng.uniform(3, 8))
            a.health = float(self.rng.uniform(0.7, 1.0))
            self.add_agent(a)
        self.add_event({
            "type": "migration",
            "year": self.year,
            "description": f"{count} migrants injected (population rescue)",
        })
