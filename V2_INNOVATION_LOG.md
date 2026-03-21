# SIMSIV V2 Clan Simulator — Innovation Log

## Turn 1 — 2026-03-20

### What was built

Five new files on branch `v2-clan-experiment`. No existing files were modified.
The frozen v1.0 codebase (paper submitted to bioRxiv) is untouched.

**models/clan/__init__.py**
Public exports: `Band`, `ClanSociety`.

**models/clan/band.py** — `Band` class
- Composition pattern (HAS-A Society, not inherits-from Society).
- Properties: `band_id: int`, `name: str`, `origin_year: int`.
- `inter_band_trust: dict[int, float]` — trust toward other bands, default 0.5.
- `trust_toward(other_band_id)` — returns trust (0.5 if unseen).
- `update_trust(other_band_id, delta)` — additive update clamped [0, 1].
- Delegates `get_living()`, `population_size()`, `get_by_id()` to the underlying Society.
- Defers Society import to `__init__` body to guard against any future circular import risk.

**models/clan/clan_society.py** — `ClanSociety` class
- `bands: dict[int, Band]` registry.
- `distance_matrix: dict[tuple[int,int], float]` — symmetric, keyed (min_id, max_id).
- `add_band(band)` — registers a band, sets default distance 0.5 to all existing bands.
- `remove_band(band_id)` — deregisters and cleans up all distance entries.
- `set_distance(a, b, d)` / `get_distance(a, b)` — geographic separation helpers.
- `schedule_interactions(year, rng)` — evaluates every ordered pair (i < j), computes
  interaction probability as `base_rate * (1 - distance) * (0.5 + 0.5 * avg_trust)`,
  returns list of `(Band, Band)` tuples.
- `total_population()`, `living_band_ids()` aggregate helpers.

**engines/clan_base.py** — `ClanEngine` class
- Single set of v1 engine singletons shared across all bands (engines are stateless).
- `tick(clan_society, year, rng, config)` — iterates bands in band_id order, runs
  the full 12-step v1 tick on each band's Society, then schedules inter-band
  interactions and processes each pair.
- `_tick_band(band, year, rng, config)` — mirrors `simulation.Simulation.tick`
  exactly: year advance, population rescue, age all agents, then steps 1-12.
- `_process_interaction(band_a, band_b, year, rng, config)` — stub: applies a small
  positive trust delta (rng.uniform(0.01, 0.05)) and records `inter_band_contact`
  events on both societies.
- `get_band_history(band_id)` — returns the full per-tick metrics row list.
- Uses `logging.getLogger(__name__)` throughout. No print statements.
- All randomness via the passed `rng` parameter.

**tests/test_clan_smoke.py** — 12 pytest smoke tests
1. `test_band_construction` — Band creates, properties correct.
2. `test_clan_society_add_remove` — registry and distance cleanup.
3. `test_clan_engine_5_ticks_no_crash` — ClanEngine runs without exception.
4. `test_both_bands_have_agents_after_5_ticks` — no extinction in 5 ticks.
5. `test_year_counter_advances_in_both_bands` — society.year == current year.
6. `test_tick_returns_per_band_metrics` — result has `band_metrics[band_id]` with `population`.
7. `test_tick_returns_total_population` — `total_population` sum is correct.
8. `test_inter_band_interactions_scheduled` — at least one interaction over 10 ticks.
9. `test_trust_updated_after_interaction` — trust changes post-interaction.
10. `test_band_isolation` — agent objects are distinct Python objects across bands.
11. `test_band_metrics_history_accumulates` — 5 ticks = 5 history rows per band.
12. `test_schedule_interactions_deterministic` — same seed = same schedule.

### Self-critique findings and what was fixed

**Issue 1 — Circular import risk in Band constructor**
`Band.__init__` originally planned a top-level import of `Society`. Deferred the import
to inside `__init__` body as `from models.society import Society` to eliminate any
potential circular import at module load time if the import graph ever changes.
Verified: `models/clan/` files have zero imports from `engines/` or `simulation`.

**Issue 2 — Zero-population edge case**
If a band's population collapses to zero, `_tick_band` must not crash. Verified that
the population rescue path (`society.inject_migrants(deficit)`) fires when
`pop < config.min_viable_population`. Tested manually: a band zeroed out recovered
to 31 agents after one tick. Added no extra guard — the existing v1 mechanism works.

**Issue 3 — Distance matrix key ordering**
Symmetric pair lookup must be consistent regardless of which band_id is passed
first to `get_distance()`. Introduced `_dist_key(a, b)` which always returns
`(min(a, b), max(a, b))`. Applied consistently in `set_distance`, `get_distance`,
`add_band` (default insertion), and `remove_band` (cleanup).

**Issue 4 — Shared rng consumption order across bands**
When multiple bands share one rng, the consumption order determines reproducibility.
Fixed: bands are always ticked in sorted `band_id` order so results are reproducible
given the same starting rng state and the same set of active bands.

**Issue 5 — Engine statefulness check**
Confirmed v1 engines carry no mutable per-run state between calls — they are effectively
stateless function objects. Safe to share a single engine instance across bands.
Each band's Society carries all state. Verified by inspection of all 8 engine files.

**Issue 6 — False positive in print() check**
Regex scan of new files flagged "print" inside a docstring comment in clan_base.py.
Confirmed no actual `print()` calls exist in any new file.

### Known limitations

- Inter-band mechanics are a stub: only a small trust bump on contact. No trade,
  raiding, marriage exchange, or gene flow between bands yet.
- The shared `rng` across all bands means that adding or removing a band mid-run
  changes the rng consumption sequence for all subsequent bands. The Turn 2 design
  should consider per-band rngs forked from a master rng at construction time.
- `schedule_interactions` evaluates all O(N^2) band pairs every tick. With many
  bands this scales poorly. Acceptable for now (2-10 bands expected in v2).
- `MetricsCollector` is shared via `_band_metrics` dict in the engine. If the same
  `ClanEngine` instance is reused across multiple independent runs (e.g. in autosim),
  history will accumulate across runs. Turn 2 should add a `reset()` method or
  create a fresh `ClanEngine` per run.
- `inter_band_contact` events are emitted but not yet read by any metrics collector.
  The `metrics/clan_collectors.py` planned in the task description is not yet built.

### Council review (2026-03-20)

GPT-4o errored (API issue — no response). Grok reviewed successfully.

**Grok findings:**
- DRIFT: None flagged — work aligns with gene-culture coevolution research question.
- Architecture: No circular imports, clean model/engine separation, rng management correct.
- Risk: Shared rng across bands is the primary reproducibility risk. O(N^2) scheduling
  could be a performance issue if band count grows beyond expected 2-10 range.
- Both risks were already documented in Known Limitations above.

**Consensus fixes required (both models flagged):**
- None possible — GPT-4o errored. No consensus.

**Single-model flags (Grok only — applied by judgment):**
- Shared rng risk: Already documented. Will be addressed in Turn 2 with per-band rng
  forking as described in "What the next turn should do" below.

Since no DRIFT was flagged and no consensus fix was required, proceeding as planned.

### What the next turn should do

1. Build `metrics/clan_collectors.py` — collect per-band and cross-band metrics:
   total_population per band, inter_band_trust matrix snapshot, interaction count,
   population divergence index (how much band trait distributions have diverged).

2. Design and implement real inter-band mechanics:
   - Trade (resource transfer proportional to trust and surplus/deficit).
   - Marriage exchange (agent transfer between bands — gene flow vector).
   - Raiding (conflict where loser loses resources, trust drops).
   Use the existing v1 conflict/resource engine primitives where possible.

3. Per-band rng design: fork band rngs from master rng at `Band` construction so
   inter-band mechanics can use a separate rng without disrupting intra-band ticks.

4. Add a `reset()` method to `ClanEngine` (or make MetricsCollectors external to the
   engine) so the engine can be reused across autosim parameter sweeps.

5. Consider a `BandFingerprint` dataclass that captures the heritable trait
   distribution of a band (mean, sd per trait) — the primary output variable for
   testing the gene-culture coevolution claim across multiple bands.
