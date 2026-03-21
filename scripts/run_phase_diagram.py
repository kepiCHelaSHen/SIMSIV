"""
SIMSIV v2 — Phase Diagram: Institutional Strength x War Intensity
=================================================================
Maps the boundary between North and Bowles in parameter space.

20 bands (10 Free + 10 State) per run, 500yr, 3 seeds per condition.
Vary: law_strength of State bands (institutional strength)
Vary: raid_casualty_rate (war intensity / lethality)

Output: outputs/experiments/v2_battery/exp8_phase_diagram/
"""

import csv, time, sys
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import Config
from models.clan.clan_config import ClanConfig
from models.clan.clan_simulation import ClanSimulation

OUT = Path("outputs/experiments/v2_battery/exp8_phase_diagram")
OUT.mkdir(parents=True, exist_ok=True)

# ── Parameter grid ──────────────────────────────────────────────────────────
LAW_STRENGTHS = [0.0, 0.2, 0.4, 0.6, 0.8]       # institutional strength
CASUALTY_RATES = [0.10, 0.20, 0.35, 0.50]         # war lethality
SEEDS = [42, 137, 271]
N_YEARS = 500
SNAPSHOT_YEARS = [100, 200, 300, 500]

total_runs = len(LAW_STRENGTHS) * len(CASUALTY_RATES) * len(SEEDS)
print(f"Phase diagram: {len(LAW_STRENGTHS)} x {len(CASUALTY_RATES)} x {len(SEEDS)} seeds = {total_runs} runs")
print(f"Each run: 20 bands, {N_YEARS}yr, ~150s")
print(f"Estimated runtime: ~{total_runs * 150 / 3600:.1f} hours")
print()

all_rows = []
run_count = 0
t_start = time.time()

for law in LAW_STRENGTHS:
    for cas in CASUALTY_RATES:
        for seed in SEEDS:
            run_count += 1
            t0 = time.time()

            clan_cfg = ClanConfig(
                raid_base_probability=0.50,
                raid_scarcity_threshold=20.0,
                raid_trust_suppression_threshold=0.5,
                raid_attacker_casualty_rate=cas,
                raid_defender_casualty_rate=cas * 1.33,  # defenders take 33% more
            )

            # 10 Free + 10 State (State uses the current law_strength)
            band_setups = []
            for i in range(10):
                band_setups.append((f"Free_{i+1}", Config(law_strength=0.0, property_rights_strength=0.0)))
            for i in range(10):
                band_setups.append((f"State_{i+1}", Config(law_strength=law, property_rights_strength=law)))

            sim = ClanSimulation(
                seed=seed, n_years=N_YEARS, band_setups=band_setups,
                population_per_band=30, clan_config=clan_cfg,
                base_interaction_rate=0.5,
            )
            history = sim.run()
            elapsed = time.time() - t0

            for yr in SNAPSHOT_YEARS:
                if yr > len(history):
                    continue
                h = history[yr - 1]
                clan = h["clan_metrics"]

                free_coops, state_coops = [], []
                free_alive, state_alive = 0, 0

                for bid in sim.clan_society.bands:
                    band = sim.clan_society.bands[bid]
                    living = band.get_living()
                    if not living:
                        continue
                    coop = float(np.mean([a.cooperation_propensity for a in living]))
                    # Classify by ORIGINAL band name, not current law_strength
                    # (institutional drift moves law_strength, corrupting the classifier)
                    name = band.name
                    is_free = name.startswith("Free") or "(fission of" in name and any(
                        f"fission of {fid}" in name for fid in range(1, 11)
                    )
                    # Simpler: original Free bands have IDs 1-10, State 11-20.
                    # Fission daughters inherit parent Config. Check the CONFIG
                    # value at construction time, not the drifted value.
                    # Since we can't recover original ID reliably after fission,
                    # use a threshold relative to the STATE law_strength for this run.
                    # If law > 0: Free started at 0, State at law.
                    # Midpoint = law/2. Below midpoint = Free regime.
                    midpoint = law / 2.0 if law > 0 else -1  # law=0: all same regime
                    band_law = band.society.config.law_strength
                    if law == 0.0:
                        # Both regimes identical — classify by original ID
                        # IDs 1-10 were Free, 11-20 were State
                        if bid <= 10:
                            free_coops.append(coop)
                            free_alive += 1
                        else:
                            state_coops.append(coop)
                            state_alive += 1
                    elif band_law < midpoint:
                        free_coops.append(coop)
                        free_alive += 1
                    else:
                        state_coops.append(coop)
                        state_alive += 1

                free_mean = float(np.mean(free_coops)) if free_coops else float("nan")
                state_mean = float(np.mean(state_coops)) if state_coops else float("nan")
                div = free_mean - state_mean if not (np.isnan(free_mean) or np.isnan(state_mean)) else float("nan")

                # Who is winning? (regime with more surviving bands)
                if free_alive > state_alive:
                    winner = "Free"
                elif state_alive > free_alive:
                    winner = "State"
                else:
                    winner = "Tie"

                all_rows.append({
                    "law_strength": law, "casualty_rate": cas, "seed": seed, "year": yr,
                    "coop_free": free_mean, "coop_state": state_mean, "divergence": div,
                    "free_bands": free_alive, "state_bands": state_alive,
                    "total_bands": len(sim.clan_society.bands),
                    "total_pop": h["total_population"],
                    "fst_coop": clan.get("fst_cooperation_propensity", 0),
                    "demographic_sel": clan.get("demographic_selection_coeff", 0),
                    "winner": winner,
                })

            # Print progress
            r500 = [r for r in all_rows if r["seed"] == seed and r["year"] == 500
                     and r["law_strength"] == law and r["casualty_rate"] == cas]
            if r500:
                r = r500[0]
                print(f"[{run_count}/{total_runs}] law={law:.1f} cas={cas:.2f} seed={seed}: "
                      f"Free={r['coop_free']:.3f}({r['free_bands']}b) "
                      f"State={r['coop_state']:.3f}({r['state_bands']}b) "
                      f"winner={r['winner']} ({elapsed:.0f}s)")

            # Save partial results every 15 runs
            if run_count % 15 == 0:
                keys = list(all_rows[0].keys())
                with open(OUT / "phase_partial.csv", "w", newline="") as f:
                    w = csv.DictWriter(f, fieldnames=keys)
                    w.writeheader()
                    w.writerows(all_rows)
                print(f"  -> Partial saved ({len(all_rows)} rows)")

total_time = time.time() - t_start
print(f"\nAll {total_runs} runs complete in {total_time:.0f}s ({total_time/60:.1f} min, {total_time/3600:.1f} hr)")

# Write full CSV
keys = list(all_rows[0].keys())
with open(OUT / "phase_diagram.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=keys)
    w.writeheader()
    w.writerows(all_rows)
print(f"Full results: {OUT}/phase_diagram.csv ({len(all_rows)} rows)")

# ── Summary: phase diagram at year 500 ──────────────────────────────────────
print("\n=== PHASE DIAGRAM AT YEAR 500 ===")
print(f"{'law':>5} {'cas':>5} | {'Free coop':>10} {'State coop':>11} {'Div':>8} | {'Free bands':>11} {'State bands':>12} | Winner")
print("-" * 85)

for law in LAW_STRENGTHS:
    for cas in CASUALTY_RATES:
        cond_rows = [r for r in all_rows if r["law_strength"] == law
                     and r["casualty_rate"] == cas and r["year"] == 500]
        if not cond_rows:
            continue
        fc = np.nanmean([r["coop_free"] for r in cond_rows])
        sc = np.nanmean([r["coop_state"] for r in cond_rows])
        div = np.nanmean([r["divergence"] for r in cond_rows])
        fb = np.mean([r["free_bands"] for r in cond_rows])
        sb = np.mean([r["state_bands"] for r in cond_rows])
        # Winner by demographic dominance (more bands on average)
        w = "FREE" if fb > sb else ("STATE" if sb > fb else "TIE")
        print(f"{law:5.1f} {cas:5.2f} | {fc:10.3f} {sc:11.3f} {div:+8.3f} | {fb:11.1f} {sb:12.1f} | {w}")

print(f"\nPhase diagram complete. Data: {OUT}/phase_diagram.csv")
