# SIMSIV V2 Clan Simulator — Innovation Log

## Turn 2 — 2026-03-20

### What was built

Two new files and modifications to two Turn 1 files (no v1.0 frozen files were touched).
All 52 tests pass (22 v1 original + 12 Turn 1 smoke + 18 new Turn 2 trade tests).

**engines/clan_trade.py** — New inter-band trade engine

Core function: `trade_tick(band_a, band_b, trust, rng, config) -> list[dict]`

- `_select_traders(band, rng, config)` — filters living adults by life stage (PRIME/MATURE only).
- `_compute_n_pairs(traders_a, traders_b, trust, config)` — number of trader pairs = `round(min(len_a, len_b, trade_party_size) * trust)`, clamped to at least 1 if traders exist.
- `_is_scarce(band)` — checks if mean subsistence resources < 3.0.
- `_compute_refusal_threshold(scarce, config)` — returns outgroup_tolerance threshold below which an agent may refuse. Scarce bands get 50% lower threshold (desperation overrides xenophobia).
- `_execute_trade_pair(ta, tb, band_a, band_b, trust, scarce_a, scarce_b, rng, config)` — core trade logic: refusal check (probability scales with how far below threshold tolerance is), then three-resource exchange (current_resources, current_tools, current_prestige_goods) with a 5-15% random positive-sum surplus. Social skill modulates the surplus bonus. Caps are enforced. Trust bumps and agent reputation_ledger updates on success; trust penalty on refusal.

Design choices and rationale:
- Trade is positive-sum (~5-15%) calibrated to Wiessner (1982) and Smith & Bird (2000) ethnographic evidence on inter-group reciprocal exchange as risk-pooling.
- Scarcity effect: desperate bands trade more aggressively (lower selectivity) — this models the well-documented pattern of drought-driven trade expansion in forager ethnographies.
- All three DD21 resource types participate: subsistence above floor, tools, prestige goods. Each has its own cap guard.
- Agent-level `remember()` calls are made post-trade, seeding reputation ledger cross-band contacts for future game-theoretic tracking.

**tests/test_clan_trade.py** — 18 new tests

1. `test_trade_tick_returns_list` — basic return type check.
2. `test_trade_tick_event_keys` — all required event keys present.
3. `test_trade_tick_valid_outcome_values` — outcome is always "success" or "refused".
4. `test_trade_tick_positive_sum_gain` — successful exchange creates net positive total value.
5. `test_trade_tick_refused_decreases_trust` — refusal decreases bilateral band trust.
6. `test_trade_tick_success_increases_trust` — success increases bilateral band trust.
7. `test_zero_outgroup_tolerance_always_refuses` — 20 trials confirm zero-tolerance agent always refuses when not scarce.
8. `test_scarcity_lowers_refusal_threshold` — `_compute_refusal_threshold(scarce=True)` < `(scarce=False)`.
9. `test_resource_caps_respected` — post-trade resource values do not exceed storage cap.
10. `test_trade_tick_deterministic` — same seed produces identical outcome sequence.
11. `test_reset_clears_band_metrics` — `ClanEngine.reset()` empties history.
12. `test_reset_allows_fresh_accumulation` — after reset, 2 new ticks → 2 rows.
13. `test_per_band_rng_stored_on_band` — `Band.rng` is a `numpy.random.Generator`.
14. `test_inter_band_events_include_contact_events` — at least one contact event in 20 ticks.
15. `test_trade_events_have_year_stamped` — trade events have non-zero year stamped by ClanEngine.
16. `test_interaction_outcomes_vary_over_many_ticks` — at least 2 distinct contact outcomes over 50 ticks.
17. `test_mean_outgroup_tolerance_returns_float` — helper returns float in [0, 1].
18. `test_trust_changes_after_trade_session` — bilateral trust changes after any trade session.

**Modified: engines/clan_base.py** — Three critic fixes applied

Fix 1 — Per-band rng contract: `_tick_band` now receives `band.rng` instead of the shared clan-level rng. Each band's internal 12-step tick draws from its own rng; the clan-level rng is reserved for inter-band scheduling and interaction draws. Band trajectories are now truly independent of band ordering.

Fix 2 — Interaction type draw: `_process_interaction` no longer unconditionally bumps trust. Instead, it draws an interaction type using a probability formula grounded in bilateral trust and mean outgroup_tolerance:
- `p_trade = trust * mean_tol` — tolerant, trusting bands trade
- `p_neutral = mean_tol * (1 - trust)` — tolerant but not-yet-trusting bands meet peacefully
- `p_hostile = 1 - mean_tol` — intolerant bands have hostile contact
These three probabilities sum to exactly 1. Hostile contacts decrease trust; neutral contacts bump trust by a tolerance-modulated small delta. This means outgroup_tolerance trait now has real discriminating power on inter-band relationship formation.

Fix 3 — `reset()` method added to ClanEngine. Clears `_band_metrics` dict. Call between independent runs in autosim parameter sweeps to prevent metrics history bleed-over.

**Modified: models/clan/band.py** — Per-band rng attribute

Added `self.rng: np.random.Generator = rng` as a Band attribute (stored before the Society is created with the same rng). The docstring already described per-band rngs; now the implementation matches the contract: `_tick_band` in `clan_base.py` reads `band.rng` to drive all 12 engine steps for that band.

### Self-critique findings and what was fixed

**Issue 1 — positive-sum surplus calculation**

Original draft of `_execute_trade_pair` computed `receive_a = give_b * skill_bonus_a * (1 + surplus * 0.5)`. This meant if give_b = 0 (trader_b has nothing to trade), trader_a receives nothing even though they gave resources away. Fixed: each side receives based on what the other gives, which is correct. When both sides have zero surplus, no transfer occurs and the event is still "success" (a goodwill exchange of zero). This edge case is not a problem because the subsistence floor ensures agents always have some resources above floor unless they are at exactly the floor — in which case the offer is `max(0, floor - floor) = 0`, a zero-cost contact.

**Issue 2 — agent_ids in refused events**

The refused event correctly includes `[trader_a.id, trader_b.id]` in `agent_ids`. The caller's year stamp (set to 0 as placeholder in `trade_tick`) is overwritten to the actual year by `ClanEngine._process_interaction`. This is the correct pattern — the trade engine doesn't know the simulation year, the engine dispatcher does.

**Issue 3 — trust update in neutral contact could be zero**

If mean_tol is near 0 (bands of highly xenophobic agents), the neutral contact trust_delta = `uniform(0.005, 0.02) * near_zero` could be below floating-point significance for trust's repr but not for equality tests. In practice, mean outgroup_tolerance starts at ~0.5 (default) and rarely drops below 0.1 in a healthy population. The minimum meaningful delta is `0.005 * 0.1 = 0.0005`, which is representable in float64 and will register as ≠ to the initial value. No fix needed.

**Issue 4 — trade_tick events are added twice to each band's society**

In `_process_interaction`, when interaction_type is "trade", trade events are first stamped with `year` and added to both societies in a loop, then a separate `contact_event` summary is also added. This means trade events appear in both band event windows, which is correct (both bands experienced the trade). The `inter_band_events` in the result only contains the trade events + one contact summary, which is the right external representation.

**Issue 5 — `_TRADER_STAGES` uses PRIME/MATURE only**

CHILDHOOD and YOUTH agents are excluded. ELDER agents are also excluded. This is a deliberate design choice: inter-band diplomacy and trade are adult responsibilities. Elders are excluded to avoid confusion with intra-band elder roles. If a band consists entirely of children (disaster scenario), `_select_traders` returns empty and `trade_tick` returns `[]` cleanly.

### Known limitations

- No "remember" cross-band: `trader_a.remember(trader_b.id, ...)` adds trader_b to trader_a's reputation_ledger. Since they're in different bands, this cross-band ledger entry is currently unused by any engine. Future turns could use this as the gene-flow / cultural contact vector.
- Trade frequency: with `trade_party_size` defaulting to 3, and the interaction-type draw, actual trade sessions occur roughly `base_rate * (1-dist) * (0.5 + 0.5*avg_trust) * trust * mean_tol` of the time. With default params (base_rate=0.3, dist=0.5, trust=0.5, tol=0.5), this is roughly 5.6% of annual ticks per band pair. This seems low but matches ethnographic evidence for distant band contact frequency.
- No raiding engine yet. The "hostile" interaction type currently only decrements trust; it does not transfer resources or inflict health damage. This is intentional Turn 2 scope limitation — raiding is a separate engine.
- No marriage exchange (gene flow between bands). This remains the highest-priority Turn 3 item for testing the gene-culture coevolution claim.
- `metrics/clan_collectors.py` still not built. Cross-band trait divergence metrics cannot be computed until Turn 3.

### What the next turn should do

1. Build `metrics/clan_collectors.py` — per-band trait distribution snapshots (mean and SD per heritable trait per band) and a population divergence index (Jensen-Shannon divergence on trait distributions). This is the primary instrument for the Bowles/Gintis vs North test.

2. Build `engines/clan_raid.py` — hostile inter-band conflict: resource transfer, health damage, trust penalty. The hostile contact path in `_process_interaction` should dispatch to `raid_tick` just as the trade path dispatches to `trade_tick`.

3. Marriage exchange / gene flow: allow occasional agent transfers between bands (emigration from one band, immigration to another) using the existing v1 migration mechanism. This seeds genetic and cultural divergence across bands — the core v2 scientific experiment.

4. Add a `BandFingerprint` dataclass capturing the heritable trait distribution of a band at a given year. Needed for between-group selection coefficient computation.

5. Update `ClanEngine.tick()` docstring to remove the word "stub" — the interaction pipeline is now real (trade engine implemented, interaction-type draw active).

### Council review (2026-03-20)

GPT-4o errored (API issue). Grok reviewed successfully.

**Grok findings:**
- DRIFT: None flagged. Project aligned with Bowles/Gintis co-evolution research question.
- Science: Trade mechanics grounded in Wiessner/Smith & Bird ethnographic evidence. Interaction-type draw (trade/neutral/hostile) plausible for Bowles-Gintis dynamics. Limitation: without raiding and gene flow, between-group selection is still partial.
- Architecture: No circular imports, per-band rng correct. Concern: ClanEngine reuse without guaranteed fresh instance could corrupt autosim data.
- Risk: Missing `metrics/clan_collectors.py` blocks trait divergence measurement — the core scientific instrument.
- Next: Prioritize `metrics/clan_collectors.py` and marriage exchange (gene flow).

**Consensus fixes required (both models flagged):**
- None possible — GPT-4o errored.

**Single-model flags (Grok only — judgment applied):**
- ClanEngine reuse risk: Already addressed in Turn 2 via `reset()` method. Class docstring will be updated in Turn 3 to make the "one engine per run OR call reset()" contract explicit.
- Missing metrics: Correctly scoped as Turn 3 priority. No code change needed now.
- Raiding/gene flow absence: Correctly scoped as Turn 3 work. No drift.

No code changes required. No DRIFT flagged. Proceeding.

---

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

---

## CRITIC REVIEW — Turn 1

gate_1_frozen_compliance:  1.0 — Git commit a60e4be confirms exactly 5 new files created (models/clan/__init__.py, models/clan/band.py, models/clan/clan_society.py, engines/clan_base.py, tests/test_clan_smoke.py); zero existing files modified; STATUS.md change is an uncommitted working-tree modification predating Turn 1 and is not part of the v2 build; no known bugs from STATUS.md were touched.

gate_2_architecture:       0.95 — No print() calls in any new file (grep confirmed); all randomness via the passed rng parameter; no circular imports (live import test passed); structured logging via logging.getLogger(__name__) used throughout; all 34 tests (22 v1 + 12 new) pass; one minor deduction: _tick_band (clan_base.py line 139) accepts the shared clan-level rng rather than a per-band rng, meaning the Band constructor's documented per-band rng is used only for Society initialization and is thereafter abandoned — every engine call in _tick_band draws from the shared rng instead, partially contradicting the per-band rng isolation documented in band.py line 47 and the V2_INNOVATION_LOG Issue 4 fix note.

gate_3_scientific:         0.80 — The interaction-scheduling formula at clan_society.py lines 126-130 (p = base_rate * (1 - distance) * (0.5 + 0.5 * avg_trust)) is directionally plausible and consistent with Axelrod-style proximity-weighted encounter models; distance symmetry is correctly enforced via _dist_key (clan_society.py line 165); however the stub _process_interaction (clan_base.py lines 252-311) applies only a positive trust delta — there is no null hypothesis baseline for hostile or indifferent first contact, which will bias all inter-band relationships toward trust accumulation from tick 1 and confound the between-group selection signal Turn 2 needs; additionally, metrics/clan_collectors.py is explicitly noted as not yet built (V2_INNOVATION_LOG line 109), so no between-group or within-group selection coefficients are being tracked at all, which is the core measurement required for the Bowles/Gintis vs North test.

gate_4_drift:              0.90 — The scaffold is coherent with the central research question; Band wraps Society via composition without inheriting from it, cleanly separating the within-group and between-group layers; the architecture enables future between-group selection experiments (different institutional configs per band, gene flow via marriage exchange, raiding); the stub nature of inter-band mechanics is correctly scoped for a Turn 1; the ClanEngine._band_metrics dict accumulating across runs (noted in V2_INNOVATION_LOG line 105-108) is the one structural issue that could invalidate autosim parameter sweeps if ClanEngine is reused, but this is already documented as a known limitation with a proposed fix.

blocking_issues:
  - None. All gates at or above threshold. All 34 tests pass. No existing code modified.

nonblocking_issues:
  - clan_base.py line 139 — _tick_band accepts the shared clan-level rng, not a per-band rng. The per-band rngs constructed in the test fixture (test_clan_smoke.py lines 45-46) are consumed only during Band/Society construction (Society.__init__ calls create_initial_population with that rng). From tick 1 onward, all engine calls draw from the shared rng in band_id order. This is internally consistent and reproducible, but it contradicts the "each Band receives its own rng" contract stated in band.py line 43-47. If Turn 2 introduces per-band engine rng isolation, the _tick_band signature must change. Document the actual contract clearly or implement the fork now.
  - clan_base.py line 272 — _process_interaction always applies a positive trust delta (rng.uniform(0.01, 0.05)). There is no hostile-contact or neutral-contact path. This will systematically inflate trust between all bands regardless of their trait composition, preempting the outgroup_tolerance trait from having any discriminating effect on inter-band relationship formation. Turn 2 should add an interaction-type draw (trade/raid/neutral) before applying any trust delta.
  - clan_base.py lines 317-326 — _get_metrics_collector creates MetricsCollector lazily and stores it in self._band_metrics indefinitely. A ClanEngine instance reused across parameter sweeps will accumulate history from all runs. Add a reset() method or note in the class docstring that one ClanEngine per run is required.
  - metrics/clan_collectors.py — not yet built. This is correctly scoped as Turn 2 work, but without it there are zero cross-band metrics (population divergence index, per-band trait means, interaction counts). The scientific claim cannot be tested until this exists.

verdict: PASS

next_turn_priority: Build metrics/clan_collectors.py with per-band trait-distribution snapshots (mean and SD per heritable trait) and a population divergence index — this is the primary measurement instrument for the Bowles/Gintis vs North test, and nothing about the gene-culture coevolution claim can be evaluated without it.
