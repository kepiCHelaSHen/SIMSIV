# SIMSIV — PHASE E: ENGINEERING HARDENING
# Executable Chain Prompt — Run this in a Claude CLI session
# Root: D:\EXPERIMENTS\SIM
# Authored: 2026-03-15
# Source: Comprehensive code review — 8 priority fixes + 6 moderate issues

================================================================================
INSTRUCTIONS FOR CLAUDE (CLI SESSION)
================================================================================

You are an elite Python engineer working on the SIMSIV simulation project.
Your job in this session is to apply ALL of the engineering fixes listed below
to the codebase at D:\EXPERIMENTS\SIM, then update all project documentation
to reflect the changes.

Read this entire file before writing a single line of code.
Work through the fixes IN ORDER — each block is numbered.
After every block, verify with: python -m pytest tests/ -v
Do NOT change any simulation logic, parameter names, or config defaults.
Do NOT add new simulation features.
Only fix what is listed.

Start by reading these files to load full context:
  - D:\EXPERIMENTS\SIM\CHAIN_PROMPT.md
  - D:\EXPERIMENTS\SIM\config.py
  - D:\EXPERIMENTS\SIM\simulation.py
  - D:\EXPERIMENTS\SIM\models\agent.py
  - D:\EXPERIMENTS\SIM\models\society.py
  - D:\EXPERIMENTS\SIM\engines\reputation.py
  - D:\EXPERIMENTS\SIM\engines\mating.py
  - D:\EXPERIMENTS\SIM\tests\test_smoke.py
  - D:\EXPERIMENTS\SIM\.gitignore
  - D:\EXPERIMENTS\SIM\requirements.txt
  - D:\EXPERIMENTS\SIM\README.md
  - D:\EXPERIMENTS\SIM\STATUS.md
  - D:\EXPERIMENTS\SIM\CLAUDE.md

================================================================================
FIX #1 — P0: REPLACE GLOBAL ID COUNTER WITH PER-SIMULATION IdCounter
================================================================================

PROBLEM:
  models/agent.py has a module-level global:
    _next_id = 0
    def _new_id() -> int:
        global _next_id
        _next_id += 1
        return _next_id
  When autosim runs 500 experiments in one Python process, IDs accumulate
  across runs. The second simulation's agents start at ID 501, not 1.
  Cross-run analysis breaks. Memory grows. This is a correctness bug.

CHANGES REQUIRED:

--- models/agent.py ---

  1. Remove the module-level `_next_id` variable and `_new_id()` function.

  2. Add this class above the Agent dataclass:

      class IdCounter:
          """Monotonically increasing integer ID generator.

          One instance per Simulation. Ensures IDs are unique within a run
          and independent across runs — two Simulation instances both produce
          IDs starting from 1 with no cross-contamination.
          """
          def __init__(self, start: int = 0):
              self._value = start

          def next(self) -> int:
              self._value += 1
              return self._value

          def reset(self):
              self._value = 0

  3. In the Agent dataclass, change:
       id: int = field(default_factory=_new_id)
     to:
       id: int = 0
     (IDs are now assigned by callers via IdCounter, not auto-generated.)

  4. Change `create_initial_population()` signature to:
       def create_initial_population(rng, config, count: int, id_counter: "IdCounter") -> list[Agent]:
     Inside the loop, change Agent construction to:
       a = Agent(id=id_counter.next(), sex=sex, age=int(age), generation=0)

  5. Change `breed()` signature to:
       def breed(parent1, parent2, rng, config, year, id_counter: "IdCounter", scarcity=0.0, pop_trait_means=None) -> Agent:
     Change child creation to:
       child = Agent(id=id_counter.next(), sex=child_sex, age=0, generation=generation, parent_ids=(parent1.id, parent2.id), health=1.0)

  6. Replace `reset_id_counter()` with a no-op stub marked deprecated:
       def reset_id_counter():
           """DEPRECATED: No-op. Use per-Simulation IdCounter instead.
           Retained only for backward compatibility with old scripts.
           """
           pass

--- models/society.py ---

  7. In `Society.__init__()`, add:
       self.id_counter = IdCounter()
     Import IdCounter at the top: from .agent import Agent, Sex, HERITABLE_TRAITS, IdCounter, create_initial_population

  8. Change the `create_initial_population` call to:
       pop = create_initial_population(rng, config, config.population_size, self.id_counter)

  9. In `inject_migrants()`, change Agent construction to:
       a = Agent(id=self.id_counter.next(), sex=sex, age=int(self.rng.integers(18, 35)), generation=0)

  10. In `process_migration()` (immigration branch), change Agent construction to:
        a = Agent(id=self.id_counter.next(), sex=sex, age=age, generation=0)

--- engines/reproduction.py ---

  11. Find every call to `breed(...)` in the reproduction engine.
      Add `id_counter=society.id_counter` as a keyword argument to each call.

VERIFICATION:
  python -m pytest tests/ -v
  Then run this in a Python shell:
    from config import Config
    from simulation import Simulation
    s1 = Simulation(Config(population_size=20, years=1, seed=1))
    s2 = Simulation(Config(population_size=20, years=1, seed=2))
    print(min(s1.society.agents.keys()), min(s2.society.agents.keys()))
    # Both should print 1 — independent sequences

================================================================================
FIX #2 — P0: CAP society.events TO PREVENT MEMORY GROWTH
================================================================================

PROBLEM:
  society.events accumulates EVERY event from EVERY year into one unbounded list.
  At N=500, 100 years: ~500K dicts (~200MB). At N=1000, 500 years: OOM crash.
  autosim runs hundreds of these in sequence.

CHANGES REQUIRED:

--- models/society.py ---

  1. In `Society.__init__()`, REMOVE:
       self.events: list[dict] = []
     ADD these three lines instead:
       self._event_window: list[dict] = []       # rolling buffer, last N events
       self._event_window_size: int = 500        # configurable cap
       self.event_type_counts: dict[str, int] = {}  # running totals by type, never trimmed

  2. Rewrite `add_event()` to:
       def add_event(self, event: dict):
           if "year" not in event:
               event["year"] = self.year
           self.tick_events.append(event)
           # Rolling window — trim from front when over cap
           self._event_window.append(event)
           if len(self._event_window) > self._event_window_size:
               self._event_window.pop(0)
           # Accumulate type counts (never trimmed — cheap summary)
           etype = event.get("type", "unknown")
           self.event_type_counts[etype] = self.event_type_counts.get(etype, 0) + 1

--- main.py ---

  3. In `save_outputs()`, change:
       events_df = pd.DataFrame(sim.society.events)
     to:
       events_df = pd.DataFrame(sim.society._event_window)
     Add a comment: # Recent events only (last 500). Full counts in event_type_counts.

--- Any other file referencing society.events ---

  4. Search the entire codebase for `.events` references:
       grep -r "society\.events" D:\EXPERIMENTS\SIM --include="*.py"
     Replace every `society.events` with `society._event_window`.
     This includes: experiments/summarizer.py, dashboard/app.py, autosim/runner.py
     (wherever applicable — read each file before editing).

VERIFICATION:
  python -m pytest tests/ -v
  Run: python main.py --seed 42 --years 200 --population 500 --quiet
  After run, check: len(sim.society._event_window) <= 500  # should be True

================================================================================
FIX #3 — P1: DECLARE _parent_* BELIEF FIELDS IN AGENT DATACLASS
================================================================================

PROBLEM:
  In breed(), the code does:
    setattr(child, f'_parent_{bfield}', p_avg)
  for 5 belief fields. These attributes are NOT declared in the Agent dataclass.
  dataclasses.asdict() silently omits them. Type checkers can't see them.
  Engines reading them via getattr(a, '_parent_hierarchy_belief', 0.0) get
  silent fallback 0.0 for manually-constructed agents. Fragile.

CHANGES REQUIRED:

--- models/agent.py ---

  1. In the Agent dataclass, find the beliefs section (hierarchy_belief, etc.).
     Directly AFTER the kinship_obligation line, add these 5 fields:

       # ── DD25: Parental belief staging (set at birth, consumed at maturation) ──
       # Stores parent-averaged belief values until the child matures (age 15).
       # MortalityEngine/ReputationEngine reads these at maturation to initialize
       # the child's own beliefs, then should clear them (set to None).
       _parent_hierarchy_belief: Optional[float] = None
       _parent_cooperation_norm: Optional[float] = None
       _parent_violence_acceptability: Optional[float] = None
       _parent_tradition_adherence: Optional[float] = None
       _parent_kinship_obligation: Optional[float] = None

  2. In `breed()`, find the block:
       for bfield in ('hierarchy_belief', ...):
           setattr(child, f'_parent_{bfield}', p_avg)
     Replace the entire block with direct assignments:

       if getattr(config, 'beliefs_enabled', False):
           child._parent_hierarchy_belief = (parent1.hierarchy_belief + parent2.hierarchy_belief) / 2.0
           child._parent_cooperation_norm = (parent1.cooperation_norm + parent2.cooperation_norm) / 2.0
           child._parent_violence_acceptability = (parent1.violence_acceptability + parent2.violence_acceptability) / 2.0
           child._parent_tradition_adherence = (parent1.tradition_adherence + parent2.tradition_adherence) / 2.0
           child._parent_kinship_obligation = (parent1.kinship_obligation + parent2.kinship_obligation) / 2.0

  3. Search for any engine that reads these via getattr:
       grep -r "_parent_hierarchy_belief\|_parent_cooperation_norm" D:\EXPERIMENTS\SIM --include="*.py"
     Replace any `getattr(a, '_parent_hierarchy_belief', 0.0)` with
     `(a._parent_hierarchy_belief if a._parent_hierarchy_belief is not None else 0.0)`
     or simply `a._parent_hierarchy_belief or 0.0`.

VERIFICATION:
  from dataclasses import asdict
  from models.agent import Agent
  a = Agent()
  d = asdict(a)
  assert '_parent_hierarchy_belief' in d  # must be True now

================================================================================
FIX #4 — P1: WARN ON UNKNOWN KEYS IN Config.load()
================================================================================

PROBLEM:
  Config.load() silently drops unrecognized YAML keys:
    return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
  A typo like `populaton_size: 200` is silently ignored. The simulation runs
  at the default value with no indication anything went wrong.

CHANGES REQUIRED:

--- config.py ---

  Replace the `load()` classmethod with this:

    @classmethod
    def load(cls, path: Path) -> "Config":
        import warnings
        with open(path) as f:
            data = yaml.safe_load(f)
        if not data:
            return cls()
        known = set(cls.__dataclass_fields__.keys())
        unknown = [k for k in data if k not in known]
        if unknown:
            warnings.warn(
                f"Config.load('{path}'): Unrecognized key(s) will be IGNORED: {unknown}\n"
                f"  Check for typos. Run Config() to see all valid parameter names.",
                UserWarning,
                stacklevel=2,
            )
        return cls(**{k: v for k, v in data.items() if k in known})

  Also add validation to `__post_init__` — replace the existing method with:

    def __post_init__(self):
        import warnings
        VALID_MATING_SYSTEMS = ("unrestricted", "monogamy", "elite_polygyny")

        if self.mating_system not in VALID_MATING_SYSTEMS:
            warnings.warn(
                f"Unknown mating_system '{self.mating_system}'. "
                f"Valid: {VALID_MATING_SYSTEMS}. Defaulting to 'unrestricted'.",
                UserWarning,
                stacklevel=2,
            )
            self.mating_system = "unrestricted"

        if self.mating_system == "monogamy":
            self.monogamy_enforced = True
            self.max_mates_per_male = 1
            self.max_mates_per_female = 1

        elif self.mating_system == "elite_polygyny":
            self.monogamy_enforced = False
            # max_mates_per_male left at caller's value (default 999 = unlimited)

        elif self.mating_system == "unrestricted":
            self.monogamy_enforced = False
            self.max_mates_per_male = 999

VERIFICATION:
  python -m pytest tests/ -v
  Quick shell check:
    import warnings, tempfile, yaml
    from pathlib import Path
    from config import Config
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump({'populaton_size': 200}, f); path = Path(f.name)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        cfg = Config.load(path)
        assert any('populaton_size' in str(x.message) for x in w), "No warning raised!"
    print("Fix #4 verified")

================================================================================
FIX #5 — P2: ADD REVERSE PARTNERSHIP INDEX TO Society
================================================================================

PROBLEM:
  household_of() and any engine needing "who is bonded to agent X" does:
    for a in self.agents.values():          # O(N) full scan
        if a.alive and agent.id in a.partner_ids:
  With N=500 agents each calling this multiple times per tick = O(N²) per tick.

CHANGES REQUIRED:

--- models/society.py ---

  1. In `Society.__init__()`, add after `self.faction_leaders`:
       self._partner_index: dict[int, set[int]] = {}

  2. Add these three methods to Society (good place: after `add_agent()`):

       def _index_bond(self, a_id: int, b_id: int):
           """Record a bond in the reverse index (both directions)."""
           self._partner_index.setdefault(a_id, set()).add(b_id)
           self._partner_index.setdefault(b_id, set()).add(a_id)

       def _unindex_bond(self, a_id: int, b_id: int):
           """Remove a bond from the reverse index (both directions)."""
           self._partner_index.get(a_id, set()).discard(b_id)
           self._partner_index.get(b_id, set()).discard(a_id)

       def get_partners_of(self, agent_id: int) -> set[int]:
           """O(1) lookup: all agent IDs that have agent_id as a partner."""
           return self._partner_index.get(agent_id, set())

  3. In `household_of()`, replace this block:
       for a in self.agents.values():
           if a.alive and agent.id in a.partner_ids:
               hh.add(a.id)
     With:
       for pid in self.get_partners_of(agent.id):
           p = self.get_by_id(pid)
           if p and p.alive:
               hh.add(pid)

  4. Bootstrap the index in `__init__()` after population creation (handles
     any pre-bonded agents in edge cases):
       for a in self.agents.values():
           for pid in a.partner_ids:
               self._index_bond(a.id, pid)

--- engines/mating.py ---

  5. In `_form_pairs()`, after the symmetric `add_bond()` calls, add:
       society._index_bond(agent.id, partner_id)

  6. In `_clean_stale_bonds()`, after `agent.remove_bond(pid)`, add:
       society._unindex_bond(agent.id, pid)

  7. In `_dissolve_bonds()`, after each bond removal pair, add:
       society._unindex_bond(agent.id, pid)

VERIFICATION:
  python -m pytest tests/ -v
  Shell check:
    from config import Config
    from simulation import Simulation
    import numpy as np
    cfg = Config(population_size=50, years=10, seed=42)
    sim = Simulation(cfg)
    sim.run()
    # Spot-check: every bond in partner_ids should be reflected in the index
    for a in sim.society.get_living():
        for pid in a.partner_ids:
            assert pid in sim.society.get_partners_of(a.id), f"Index missing bond {a.id}→{pid}"
    print("Fix #5 verified")

================================================================================
FIX #6 — P2: REPLACE ALL print() IN ENGINES WITH logging
================================================================================

PROBLEM:
  Engines use bare print() for warnings and debug output. When autosim runs
  500 experiments, stdout is flooded. There is no way to silence or redirect it.

CHANGES REQUIRED:

--- Every file in engines/ and models/ ---

  For EACH file in engines/ (conflict.py, institutions.py, mating.py,
  mortality.py, pathology.py, reproduction.py, reputation.py, resources.py)
  and models/society.py and models/agent.py:

  1. Add at the top of the file (after other imports):
       import logging
       _log = logging.getLogger(__name__)

  2. Replace every internal print() call:
       print(f"Warning: ...")    →  _log.warning("...")
       print(f"  Warning: ...")  →  _log.warning("...")
       print(f"Debug: ...")      →  _log.debug("...")
       print(f"Error: ...")      →  _log.error("...")

  Use your judgment on level: missing data / unexpected state = warning,
  normal flow trace = debug, unrecoverable issue = error.

--- simulation.py ---

  3. Add at top:
       import logging
       _log = logging.getLogger(__name__)

  4. In the chart generation try/except in run():
       except Exception as e:
           print(f"  Warning: chart generation failed: {e}")
     Change to:
       except Exception as e:
           _log.warning("Chart generation failed: %s", e)

--- main.py ---

  5. Add to the top of `main()`, before any other code:
       import logging
       logging.basicConfig(
           level=logging.WARNING,
           format="%(levelname)s [%(name)s] %(message)s"
       )

  6. Add `--verbose` flag to argparse:
       parser.add_argument("--verbose", action="store_true",
                           help="Enable debug logging from all engines")

  7. After parsing args, add:
       if args.verbose:
           logging.getLogger().setLevel(logging.DEBUG)

  DO NOT convert these print() calls — they are intentional user-facing output:
    - print_progress() in main.py
    - The "===" divider lines in main.py
    - Any print in sandbox/explore.py

VERIFICATION:
  python main.py --seed 42 --years 10 --population 50 --quiet
  # Should produce ZERO output except the final summary lines
  python main.py --seed 42 --years 10 --population 50 --verbose
  # Should produce engine-level debug messages

================================================================================
FIX #7 — P2: COMPLETE mating_system WIRING IN Config.__post_init__
================================================================================

NOTE: This fix is already included in Fix #4 above (the rewritten __post_init__).
If you applied Fix #4, this fix is already done.

Confirm by checking that __post_init__ now handles all three cases:
  "monogamy"       → monogamy_enforced=True, max_mates_per_male=1, max_mates_per_female=1
  "elite_polygyny" → monogamy_enforced=False
  "unrestricted"   → monogamy_enforced=False, max_mates_per_male=999
  anything else    → UserWarning, fall back to "unrestricted"

================================================================================
FIX #8 — P2: MAKE DEAD LEDGER CLEANUP RELIABLE
================================================================================

PROBLEM:
  Dead agent IDs persist in living agents' reputation_ledger dicts even after
  config.dead_agent_ledger_cleanup = True. The cleanup only happens opportunistically
  inside the reputation engine via a full scan. The ledger cap (100 entries) only
  fires at insertion — dead entries fill slots and crowd out live ones.

CHANGES REQUIRED:

--- models/society.py ---

  1. Add this public method to Society:

       def purge_dead_from_ledgers(self, dead_ids: set[int]):
           """Remove dead agent IDs from all living agents' reputation ledgers.

           Call this after any batch of deaths in a tick.
           O(living * |dead_ids|) — only call when dead_ids is non-empty.
           Also cleans dead IDs from the partner index.
           """
           if not dead_ids:
               return
           for agent in self.get_living():
               for did in dead_ids:
                   agent.reputation_ledger.pop(did, None)
           # Clean partner index
           for did in dead_ids:
               self._partner_index.pop(did, None)
           for partners in self._partner_index.values():
               partners -= dead_ids

--- engines/reputation.py ---

  2. At the very START of the `run()` method in ReputationEngine, BEFORE any
     gossip or decay logic, add this block:

       # ── Dead ledger cleanup (efficient: diff from this tick's deaths) ──
       if config.dead_agent_ledger_cleanup:
           dead_ids_this_tick: set[int] = set()
           for e in society.tick_events:
               if e.get("type") in ("death", "emigration", "violence_death",
                                     "childhood_death", "natural_death"):
                   if e.get("agent_ids"):
                       dead_ids_this_tick.add(e["agent_ids"][0])
           if dead_ids_this_tick:
               society.purge_dead_from_ledgers(dead_ids_this_tick)

  NOTE: This is O(living × deaths_per_tick). On a typical tick with <5 deaths
  in a 500-agent run, this is ~2,500 dict.pop() calls — negligible. It only
  runs when there are actual deaths this tick.

VERIFICATION:
  Run a 100-year simulation at N=200.
  After the run, sample 10 living agents. For each, check:
    for agent in random.sample(sim.society.get_living(), 10):
        dead_ids = {id for id, a in sim.society.agents.items() if not a.alive}
        overlap = set(agent.reputation_ledger.keys()) & dead_ids
        assert len(overlap) == 0, f"Agent {agent.id} ledger has {len(overlap)} dead entries"
  print("Fix #8 verified")

================================================================================
FIX #9 — P3: SPLIT dashboard/app.py INTO SUB-MODULES
================================================================================

PROBLEM:
  dashboard/app.py is a 111KB monolithic Streamlit file. Hard to navigate,
  impossible to unit-test, impossible to reuse chart functions.

CHANGES REQUIRED:

  1. Read dashboard/app.py in full.

  2. Create this directory structure:
       dashboard/
         __init__.py          (empty)
         app.py               (slim router, ~80 lines)
         tabs/
           __init__.py        (empty)
           overview.py        (population/demographics tab)
           resources.py       (resource/inequality tab)
           conflict.py        (violence/conflict tab)
           mating.py          (mating/reproduction tab)
           traits.py          (trait evolution tab)
           agents.py          (agent explorer tab)
           factions.py        (factions/social structure tab — if present)
         components/
           __init__.py        (empty)
           charts.py          (shared chart helper functions)
           data_loaders.py    (all pd.read_csv, json.load, @st.cache_data)
           sidebar.py         (sidebar widgets and config panel)
           metrics_cards.py   (st.metric summary card helpers)

  3. RULES for extraction:
     - Each tab module exports exactly one function: render(df, agents_df, summary, events_df)
     - components/data_loaders.py owns ALL file I/O decorated with @st.cache_data
     - components/charts.py owns ALL plotly/matplotlib figure-creation functions
       (functions that return fig objects — no st.plotly_chart() calls inside)
     - components/metrics_cards.py owns st.metric() groupings
     - NO Streamlit calls inside components/charts.py or components/data_loaders.py
       (except metrics_cards.py and sidebar.py which are inherently Streamlit widgets)
     - app.py only contains: st.set_page_config(), st.sidebar, tab routing,
       calls to tab render() functions

  4. Rewrite app.py as the slim entry point that imports and routes to each tab.

  5. Verify: streamlit run dashboard/app.py
     Behavior must be 100% identical to before the split.

================================================================================
FIX #10 — P3: UPDATE .gitignore
================================================================================

Read D:\EXPERIMENTS\SIM\.gitignore then add any of these lines that are missing:

  # Runtime data — never commit
  autosim/journal.jsonl
  outputs/
  data/

  # Large runtime files
  *.jsonl
  *.parquet

  # Testing
  .coverage
  htmlcov/
  .pytest_cache/

  # OS artifacts
  .DS_Store
  Thumbs.db
  desktop.ini

  # Python cache
  __pycache__/
  *.py[cod]
  *.pyo

Do NOT add autosim/best_config.yaml — that's a tracked reference artifact.

================================================================================
FIX #11 — P3: ADD .python-version AND UPDATE requirements.txt
================================================================================

--- CREATE .python-version at D:\EXPERIMENTS\SIM\.python-version ---

  Content (exactly one line):
    3.11

--- UPDATE requirements.txt ---

  Replace the entire file with:

    # Core simulation
    numpy>=1.24,<2.0
    pandas>=2.0,<3.0
    pyyaml>=6.0,<7.0
    scipy>=1.10,<2.0

    # Visualization
    matplotlib>=3.7,<4.0
    plotly>=5.18,<6.0

    # Dashboard
    streamlit>=1.28,<2.0

    # Development / testing
    pytest>=7.4
    pytest-cov>=4.1

  NOTE: plotly was a missing dependency (dashboard uses it, wasn't listed).

================================================================================
FIX #12 — P3: EXPAND THE TEST SUITE
================================================================================

--- CREATE tests/test_id_counter.py ---

  """Tests for per-simulation IdCounter isolation."""
  import pytest
  from models.agent import IdCounter
  from config import Config
  from simulation import Simulation


  def test_counter_starts_at_one():
      c = IdCounter()
      assert c.next() == 1


  def test_counter_monotonic():
      c = IdCounter()
      ids = [c.next() for _ in range(100)]
      assert ids == list(range(1, 101))


  def test_counter_reset():
      c = IdCounter()
      c.next(); c.next()
      c.reset()
      assert c.next() == 1


  def test_two_simulations_have_independent_counters():
      """Running two Simulation instances should not share ID state."""
      s1 = Simulation(Config(population_size=20, years=1, seed=1))
      s2 = Simulation(Config(population_size=20, years=1, seed=2))
      # IDs within each simulation are unique
      ids1 = list(s1.society.agents.keys())
      ids2 = list(s2.society.agents.keys())
      assert len(ids1) == len(set(ids1)), "Duplicate IDs in simulation 1"
      assert len(ids2) == len(set(ids2)), "Duplicate IDs in simulation 2"
      # Counters are independent (both start from 1)
      assert min(ids1) == 1
      assert min(ids2) == 1


--- CREATE tests/test_config.py ---

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


--- CREATE tests/test_society.py ---

  """Tests for Society model correctness — event window, partner index."""
  import numpy as np
  import pytest
  from config import Config
  from models.society import Society


  def _make_society(n=30, seed=1):
      cfg = Config(population_size=n, years=1, seed=seed)
      rng = np.random.default_rng(seed)
      return Society(cfg, rng), cfg, rng


  def test_event_window_does_not_exceed_cap():
      soc, _, _ = _make_society()
      for i in range(2000):
          soc.add_event({"type": "test", "description": f"e{i}"})
      assert len(soc._event_window) <= soc._event_window_size


  def test_event_type_counts_accumulate_without_cap():
      soc, _, _ = _make_society()
      for _ in range(1000):
          soc.add_event({"type": "birth"})
      for _ in range(500):
          soc.add_event({"type": "death"})
      assert soc.event_type_counts["birth"] == 1000
      assert soc.event_type_counts["death"] == 500


  def test_event_window_preserves_most_recent():
      soc, _, _ = _make_society()
      soc._event_window_size = 5
      for i in range(10):
          soc.add_event({"type": "test", "n": i})
      ns = [e["n"] for e in soc._event_window]
      assert ns == [5, 6, 7, 8, 9], f"Expected last 5 events, got {ns}"


  def test_partner_index_bond_creation():
      soc, _, _ = _make_society()
      living = soc.get_living()
      a, b = living[0], living[1]
      soc._index_bond(a.id, b.id)
      assert b.id in soc.get_partners_of(a.id)
      assert a.id in soc.get_partners_of(b.id)


  def test_partner_index_bond_removal():
      soc, _, _ = _make_society()
      living = soc.get_living()
      a, b = living[0], living[1]
      soc._index_bond(a.id, b.id)
      soc._unindex_bond(a.id, b.id)
      assert b.id not in soc.get_partners_of(a.id)
      assert a.id not in soc.get_partners_of(b.id)


  def test_partner_index_get_unknown_returns_empty():
      soc, _, _ = _make_society()
      result = soc.get_partners_of(999999)
      assert result == set()


  def test_purge_dead_from_ledgers():
      soc, _, _ = _make_society()
      living = soc.get_living()
      target = living[0]
      # Manually pollute a ledger with a fake dead ID
      living[1].reputation_ledger[99999] = 0.7
      living[2].reputation_ledger[99999] = 0.3
      soc.purge_dead_from_ledgers({99999})
      assert 99999 not in living[1].reputation_ledger
      assert 99999 not in living[2].reputation_ledger

================================================================================
FIX #13 — DOCUMENTATION UPDATES
================================================================================

After ALL code fixes are verified, update these documentation files:

--- UPDATE D:\EXPERIMENTS\SIM\CHAIN_PROMPT.md ---

  1. Change the header comment line 4 to:
       # Last Updated: 2026-03-15 | Phase E — Engineering hardening complete

  2. Change the Status line in PROJECT IDENTITY to:
       Status:     PHASE E COMPLETE — Engineering hardening done (14 fixes applied)

  3. In DEVELOPMENT STRATEGY, add a new section AFTER the Phase D entry:

       PHASE E — ENGINEERING HARDENING (COMPLETE):
         Goal: Fix all code review findings before scaling to v2 multi-band
         14 fixes applied. Zero known correctness bugs. Ready for v2 or scale-up.
         Full details: prompts/phase_e_engineering_hardening.md

  4. In CHANGE LOG, add a new entry AT THE TOP (most recent first):

       2026-03-15 | Phase E | ENGINEERING HARDENING (14 FIXES)
         Fix #1  [P0] Global ID counter → per-Simulation IdCounter class
                      Two Simulation instances now have fully independent ID sequences
         Fix #2  [P0] society.events → capped _event_window (500) + event_type_counts
                      Prevents OOM on long/large runs; autosim multi-run stable
         Fix #3  [P1] _parent_* belief attrs declared as Agent dataclass fields
                      dataclasses.asdict() now serializes them; no dynamic injection
         Fix #4  [P1] Config.load() emits UserWarning on unrecognized YAML keys
                      Typos in YAML configs are now caught, not silently dropped
         Fix #5  [P2] Reverse partnership index (_partner_index) added to Society
                      household_of() is now O(1) lookup, not O(N) scan
         Fix #6  [P2] All engine print() replaced with logging module
                      --quiet flag fully silences; --verbose flag exposes debug logs
         Fix #7  [P2] mating_system __post_init__ covers all 3 valid systems + invalid
                      "monogamy" wires max_mates_per_male=1; invalid warns + defaults
         Fix #8  [P2] Dead ledger cleanup driven by tick_events diff (reliable + fast)
                      purge_dead_from_ledgers() added to Society; called each tick
         Fix #9  [P3] dashboard/app.py split into tabs/ and components/ sub-modules
         Fix #10 [P3] .gitignore updated (journal.jsonl, outputs/, *.jsonl, OS files)
         Fix #11 [P3] .python-version added (3.11); requirements.txt adds plotly+pytest
         Fix #12 [P3] Test suite expanded: test_id_counter.py, test_config.py, test_society.py
                      ~25 test cases covering IdCounter, Config validation, event window,
                      partner index, ledger cleanup

  5. Change NEXT SESSION OBJECTIVE to:
       NEXT SESSION OBJECTIVE:
         v2 multi-band architecture, OR scale-up autosim experiments with DD01-DD27
         full feature set. All Phase E blockers cleared.

  6. In the FILE TREE section, update the prompts/ listing to include:
       ├── phase_e_engineering_hardening.md

  7. In the FILE TREE section, update the tests/ listing to:
       ├── tests\
       │   ├── __init__.py
       │   ├── test_smoke.py
       │   ├── test_id_counter.py    ← NEW Phase E
       │   ├── test_config.py        ← NEW Phase E
       │   └── test_society.py       ← NEW Phase E

  8. In the FILE TREE section, update the dashboard/ listing to:
       ├── dashboard\
       │   ├── __init__.py
       │   ├── app.py                ← slim router (Phase E split)
       │   ├── tabs\                 ← NEW Phase E
       │   │   ├── overview.py
       │   │   ├── resources.py
       │   │   ├── conflict.py
       │   │   ├── mating.py
       │   │   ├── traits.py
       │   │   └── agents.py
       │   └── components\           ← NEW Phase E
       │       ├── charts.py
       │       ├── data_loaders.py
       │       ├── sidebar.py
       │       └── metrics_cards.py

--- UPDATE D:\EXPERIMENTS\SIM\README.md ---

  In the "Architecture Guarantees" section, REPLACE the existing bullet list with:

    - **Deterministic** — same seed produces identical results
    - **Pure library** — `sim.tick()` returns a metrics dict; any frontend consumes it
    - **Modular** — engines share no state except via Society; no circular imports
    - **Reproducible** — all configs YAML-serializable; runs fully logged
    - **Isolated instances** — per-simulation `IdCounter`; running N simulations in
      sequence produces independent, non-colliding agent ID spaces
    - **Bounded memory** — event list capped to a rolling window (500 events);
      full event-type counts tracked as running totals; no OOM on long runs
    - **Typed** — all Agent fields declared in dataclass; no dynamic attribute injection
    - **Validated config** — `Config.load()` warns on unrecognized YAML keys
    - **Tested** — pytest suite covering IdCounter isolation, Config validation,
      Society event windowing, partner index correctness, breed(), gini(),
      10-tick run, population counting (~25 test cases, 4 test files)

--- UPDATE D:\EXPERIMENTS\SIM\STATUS.md ---

  Rewrite the entire file to:

    # SIMSIV — Current Status

    Phase: E COMPLETE — Engineering hardening (14 fixes)
    Previous phase: DD27 Trait completion (35 heritable traits)
    Next step: v2 multi-band architecture OR autosim scale-up experiments

    ## Phase E Summary (2026-03-15)
    - [P0] Per-simulation IdCounter — no ID bleed across autosim runs
    - [P0] Bounded event list — no OOM on long/large runs
    - [P1] Agent dataclass clean — no dynamic attribute injection
    - [P1] Config load validates — unknown YAML keys emit warnings
    - [P2] O(1) partner index — household_of() no longer O(N)
    - [P2] Structured logging — engines use logging module, --verbose flag added
    - [P2] Mating system wiring — all 3 systems + invalid case handled
    - [P2] Reliable ledger cleanup — dead IDs purged via tick_events diff
    - [P3] dashboard/ split into tabs/ + components/ sub-modules
    - [P3] .gitignore, .python-version, requirements.txt (added plotly + pytest)
    - [P3] 3 new test files: test_id_counter, test_config, test_society (~25 cases)

    ## System State
    - 35 heritable traits, 5 belief dims, 4 skill domains — DD01-DD27 complete
    - 9 engines, ~257 config params, ~130 metrics per tick
    - 27 deep dives complete — see docs/deep_dive_*.md
    - AutoSIM: Mode A parameter optimization, simulated annealing
    - All known correctness bugs fixed. Ready for v2.

    Updated: 2026-03-15

--- UPDATE D:\EXPERIMENTS\SIM\CLAUDE.md ---

  1. Change the "Current Status" line to:
       Phase E complete (Engineering hardening: IdCounter, event window, partner
       index, logging, test suite). Ready for v2 multi-band or autosim scale-up.

  2. In the Architecture Rules section, ADD these rules:

       - **Isolated simulation instances**: Use `Simulation(config)` freely in loops.
         Each instance owns its own `IdCounter` at `society.id_counter`. Agent IDs
         are unique within a run. Two simultaneous simulations both start from ID 1.
       - **Bounded events**: `society._event_window` holds last 500 events (rolling).
         `society.event_type_counts` holds running totals per event type. Do NOT use
         `society.events` — that attribute no longer exists (removed Phase E).
       - **Structured logging**: All engines use `logging.getLogger(__name__)`.
         Pass `--verbose` for debug output. No bare `print()` inside engines.
       - **Config validation**: `Config.load()` warns on unrecognized YAML keys.
         `Config.__post_init__` validates `mating_system` and wires enforcement flags.

================================================================================
FINAL VERIFICATION CHECKLIST
================================================================================

Run these after ALL fixes and doc updates are complete:

  [ ] python -m pytest tests/ -v
      → All tests green. Report exact count.

  [ ] python main.py --seed 42 --years 50 --population 100 --quiet
      → Runs clean. Zero extraneous output.

  [ ] python main.py --seed 42 --years 50 --population 100 --verbose
      → Debug log lines appear from named engine modules.

  [ ] python main.py --seed 42 --years 50 --population 100
      → Normal progress output works as before.

  [ ] streamlit run dashboard/app.py
      → Dashboard loads. All tabs render correctly.

  [ ] python -c "
      from config import Config
      from simulation import Simulation
      s1 = Simulation(Config(population_size=20, years=2, seed=1))
      s2 = Simulation(Config(population_size=20, years=2, seed=2))
      assert min(s1.society.agents) == 1
      assert min(s2.society.agents) == 1
      print('IdCounter isolation: PASS')
      "

  [ ] python -c "
      from config import Config
      from simulation import Simulation
      sim = Simulation(Config(population_size=100, years=150, seed=42))
      sim.run()
      assert len(sim.society._event_window) <= 500
      print(f'Event window cap: PASS ({len(sim.society._event_window)} events in window)')
      print(f'Event type counts: {sim.society.event_type_counts}')
      "

  [ ] python -c "
      import dataclasses
      from models.agent import Agent
      a = Agent()
      d = dataclasses.asdict(a)
      assert '_parent_hierarchy_belief' in d
      print('Dataclass field declared: PASS')
      "

  [ ] Confirm CHAIN_PROMPT.md changelog updated
  [ ] Confirm README.md Architecture Guarantees updated
  [ ] Confirm STATUS.md rewritten
  [ ] Confirm CLAUDE.md Architecture Rules updated

================================================================================
WHAT NOT TO CHANGE
================================================================================

  - NO simulation logic changes (engines, agent math, mating math, etc.)
  - NO new simulation features
  - NO Config parameter name or default value changes (breaks YAML compat)
  - NO metrics column name changes (breaks existing output files)
  - NO tick order changes in simulation.py
  - NO changes to docs/deep_dive_*.md (those are the locked design rationale)
  - NO changes to autosim/targets.yaml or autosim/best_config.yaml

================================================================================
END OF PHASE E CHAIN PROMPT
================================================================================
