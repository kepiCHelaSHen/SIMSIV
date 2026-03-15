"""
SIMSIV Name System
==================
Assigns persistent human-readable names to agents based on agent ID.
Names are deterministic — same agent ID always gets the same name.
Supports Earth (human) and alien planet modes.

Usage:
    from data.names import namer
    name = namer.get_name(agent_id, sex="female")
    full_name = namer.get_full_name(agent_id, sex="male")
    dynasty = namer.get_dynasty_name(founding_agent_id, sex="male")
"""

from __future__ import annotations
from pathlib import Path
from functools import lru_cache

_DATA_DIR = Path(__file__).parent


def _load(filename: str) -> list[str]:
    """Load a name file, stripping comments and blank lines."""
    path = _DATA_DIR / filename
    if not path.exists():
        return []
    lines = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            lines.append(line)
    return lines


# Load all name lists at module import (cached)
_FEMALE_NAMES: list[str] = []
_MALE_NAMES: list[str] = []
_SURNAMES: list[str] = []
_ALIEN_NAMES: list[str] = []


def _ensure_loaded():
    global _FEMALE_NAMES, _MALE_NAMES, _SURNAMES, _ALIEN_NAMES
    if not _FEMALE_NAMES:
        _FEMALE_NAMES = _load("female.txt")
    if not _MALE_NAMES:
        _MALE_NAMES = _load("male.txt")
    if not _SURNAMES:
        _SURNAMES = _load("surnames.txt")
    if not _ALIEN_NAMES:
        _ALIEN_NAMES = _load("alien.txt")


def get_name(agent_id: int, sex: str = "male", alien: bool = False) -> str:
    """Get a given name for an agent. Deterministic from agent_id."""
    _ensure_loaded()
    if alien:
        pool = _ALIEN_NAMES or [f"E-{agent_id}"]
        return pool[agent_id % len(pool)]
    if sex == "female" or sex == "FEMALE":
        pool = _FEMALE_NAMES or [f"F-{agent_id}"]
    else:
        pool = _MALE_NAMES or [f"M-{agent_id}"]
    return pool[agent_id % len(pool)]


def get_surname(agent_id: int) -> str:
    """Get a family/surname for an agent. Deterministic from agent_id."""
    _ensure_loaded()
    pool = _SURNAMES or [f"Clan-{agent_id}"]
    # Use a different hash to decorrelate from given name
    idx = (agent_id * 2654435761) % max(1, len(pool))
    return pool[idx]


def get_full_name(agent_id: int, sex: str = "male", alien: bool = False) -> str:
    """Get full name: [Given] [Surname]"""
    given = get_name(agent_id, sex=sex, alien=alien)
    if alien:
        return given  # aliens may not have surnames
    surname = get_surname(agent_id)
    return f"{given} {surname}"


def get_dynasty_name(founding_agent_id: int, sex: str = "male") -> str:
    """Get a dynasty display name: 'the [Surname] line'"""
    surname = get_surname(founding_agent_id)
    return f"the {surname} line"


def name_population(agents: list, alien: bool = False) -> dict[int, str]:
    """
    Assign names to a list of agents. Returns {agent_id: full_name}.
    Efficient batch assignment.
    """
    _ensure_loaded()
    result = {}
    for agent in agents:
        sex = agent.sex.value if hasattr(agent.sex, 'value') else str(agent.sex)
        result[agent.id] = get_full_name(agent.id, sex=sex, alien=alien)
    return result


# Convenience singleton
class _Namer:
    def get_name(self, agent_id, sex="male", alien=False):
        return get_name(agent_id, sex=sex, alien=alien)

    def get_surname(self, agent_id):
        return get_surname(agent_id)

    def get_full_name(self, agent_id, sex="male", alien=False):
        return get_full_name(agent_id, sex=sex, alien=alien)

    def get_dynasty_name(self, founding_agent_id, sex="male"):
        return get_dynasty_name(founding_agent_id, sex=sex)

    def name_population(self, agents, alien=False):
        return name_population(agents, alien=alien)


namer = _Namer()
