"""Tests for Config loading and validation."""
import warnings
import tempfile
from pathlib import Path
import yaml
import pytest
from config import Config


def test_unknown_key_emits_warning():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump({'populaton_size': 200, 'years': 50}, f)
        path = Path(f.name)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        cfg = Config.load(path)
    assert any('populaton_size' in str(warning.message) for warning in w), \
        "Expected UserWarning for unknown key 'populaton_size'"
    assert cfg.population_size == 500  # default, not the typo'd value


def test_valid_keys_load_correctly():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump({'population_size': 200, 'years': 50, 'seed': 99}, f)
        path = Path(f.name)
    cfg = Config.load(path)
    assert cfg.population_size == 200
    assert cfg.years == 50
    assert cfg.seed == 99


def test_mating_system_monogamy_wires_all_flags():
    cfg = Config(mating_system="monogamy")
    assert cfg.monogamy_enforced is True
    assert cfg.max_mates_per_male == 1
    assert cfg.max_mates_per_female == 1


def test_mating_system_unrestricted_wires_flags():
    cfg = Config(mating_system="unrestricted")
    assert cfg.monogamy_enforced is False
    assert cfg.max_mates_per_male == 999


def test_mating_system_invalid_warns_and_defaults():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        cfg = Config(mating_system="communism")
    assert any('Unknown mating_system' in str(warning.message) for warning in w)
    assert cfg.mating_system == "unrestricted"


def test_config_yaml_round_trip():
    cfg = Config(population_size=123, years=77, seed=555, mating_system="monogamy")
    with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as f:
        path = Path(f.name)
    cfg.save(path)
    cfg2 = Config.load(path)
    assert cfg2.population_size == 123
    assert cfg2.seed == 555
    assert cfg2.mating_system == "monogamy"
