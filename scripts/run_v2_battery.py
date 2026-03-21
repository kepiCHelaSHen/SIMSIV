"""
SIMSIV v2 — Overnight Experiment Battery
=========================================
Runs 6 experiments to strengthen v2 findings for publication.
Output: D:\EXPERIMENTS\SIM\outputs\experiments\v2_battery\

Usage:
    cd D:\EXPERIMENTS\SIM
    python scripts/run_v2_battery.py
"""

import csv
import logging
import os
import sys
import time
import traceback
from dataclasses import replace as dc_replace
from pathlib import Path

import numpy as np

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import Config
from models.clan.clan_config import ClanConfig
from models.clan.clan_simulation import ClanSimulation

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
_log = logging.getLogger("v2_battery")

OUT_DIR = Path("outputs/experiments/v2_battery")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Regime configs ──────────────────────────────────────────────────────────

def _free_config() -> Config:
    return Config(law_strength=0.0, property_rights_strength=0.0)

def _state_config() -> Config:
    return Config(law_strength=0.8, property_rights_strength=0.8)

# ── Tuned ClanConfig from Turn 8 ────────────────────────────────────────────

def _tuned_clan_config(**overrides) -> ClanConfig:
    base = dict(
        raid_base_probability=0.50,
        raid_scarcity_threshold=20.0,
        raid_trust_suppression_threshold=0.5,
    )
    base.update(overrides)
    return ClanConfig(**base)

# ── Helpers ──────────────────────────────────────────────────────────────────

def _extract_snapshot(df, year: int, band_ids_by_regime: dict) -> dict:
    """Extract metrics at a specific year from a dataframe."""
    yr_rows = df[df["year"] == year]
    if yr_rows.empty:
        return {}
    row = yr_rows.iloc[-1]
    snap = {"year": year}

    # Per-regime cooperation
    for regime, bids in band_ids_by_regime.items():
        coop_vals = []
        for bid in bids:
            key = f"band_{bid}_mean_cooperation_propensity"
            if key in row and not np.isnan(row[key]):
                pop_key = f"band_{bid}_population"
                if pop_key in row and row[pop_key] > 0:
                    coop_vals.append(row[key])
        snap[f"coop_{regime}"] = np.mean(coop_vals) if coop_vals else np.nan

    # Scalar metrics
    for key in [
        "between_group_selection_coeff",
        "demographic_selection_coeff",
        "raid_selection_coeff",
        "within_group_selection_coeff",
        "fst_prosocial_mean",
        "fst_cooperation_propensity",
        "inter_band_violence_rate",
        "cumulative_violence_rate",
        "total_trade_volume",
        "trade_volume",
        "cumulative_trade_volume_per_band",
        "mean_inter_band_trust",
        "band_resource_gini",
        "total_population",
    ]:
        if key in row:
            snap[key] = float(row[key])
    return snap


def _run_sim(seed, n_years, band_setups, clan_config, base_interaction_rate=0.8,
             pop_per_band=50):
    """Run a single ClanSimulation and return the dataframe."""
    sim = ClanSimulation(
        seed=seed,
        n_years=n_years,
        band_setups=band_setups,
        population_per_band=pop_per_band,
        clan_config=clan_config,
        base_interaction_rate=base_interaction_rate,
    )
    sim.run()
    return sim.to_dataframe()


def _write_csv(rows: list[dict], path: Path):
    if not rows:
        return
    keys = list(rows[0].keys())
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    _log.info("Wrote %d rows to %s", len(rows), path)


# =============================================================================
# EXPERIMENT 1 — STATISTICAL POWER
# =============================================================================

def exp1_power():
    _log.info("=" * 60)
    _log.info("EXPERIMENT 1 — STATISTICAL POWER (n=6 seeds)")
    _log.info("=" * 60)

    seeds = [42, 137, 271, 512, 999, 1337]
    n_years = 200
    snapshot_years = [50, 100, 150, 200]
    clan_cfg = _tuned_clan_config()

    band_setups = [
        ("Free_1", _free_config()),
        ("Free_2", _free_config()),
        ("State_1", _state_config()),
        ("State_2", _state_config()),
    ]
    regime_map = {"Free": [1, 2], "State": [3, 4]}

    all_rows = []
    seed_summaries = []

    for seed in seeds:
        t0 = time.time()
        _log.info("  Seed %d starting...", seed)
        try:
            df = _run_sim(seed, n_years, band_setups, clan_cfg)
            elapsed = time.time() - t0
            _log.info("  Seed %d complete in %.1fs, %d rows", seed, elapsed, len(df))

            for yr in snapshot_years:
                snap = _extract_snapshot(df, yr, regime_map)
                snap["seed"] = seed
                all_rows.append(snap)

            # Year-200 summary
            s200 = _extract_snapshot(df, 200, regime_map)
            coop_free = s200.get("coop_Free", np.nan)
            coop_state = s200.get("coop_State", np.nan)
            divergence = coop_free - coop_state if not (np.isnan(coop_free) or np.isnan(coop_state)) else np.nan
            seed_summaries.append({
                "seed": seed,
                "coop_free_200": coop_free,
                "coop_state_200": coop_state,
                "divergence_200": divergence,
                "direction": "Free > State" if divergence > 0.01 else ("State > Free" if divergence < -0.01 else "~equal"),
                "between_sel": s200.get("between_group_selection_coeff", np.nan),
                "fst_prosocial": s200.get("fst_prosocial_mean", np.nan),
                "violence_rate": s200.get("cumulative_violence_rate", np.nan),
                "trade_vol_band": s200.get("cumulative_trade_volume_per_band", np.nan),
            })
        except Exception as e:
            _log.error("  Seed %d CRASHED: %s", seed, e)
            traceback.print_exc()

    _write_csv(all_rows, OUT_DIR / "exp1_power.csv")

    # Summary
    divergences = [s["divergence_200"] for s in seed_summaries if not np.isnan(s["divergence_200"])]
    free_wins = sum(1 for d in divergences if d > 0.01)
    state_wins = sum(1 for d in divergences if d < -0.01)
    ties = len(divergences) - free_wins - state_wins

    summary = f"""# Experiment 1 — Statistical Power (n={len(seeds)} seeds)

## Setup
- 4 bands: 2 Free (law=0.0) + 2 State (law=0.8)
- 200 years, 50 agents/band
- Tuned ClanConfig: raid_base_probability=0.50, raid_scarcity_threshold=20.0, base_interaction_rate=0.8

## Per-seed results at year 200

| Seed | Coop (Free) | Coop (State) | Divergence | Direction | Between Sel | Fst |
|------|------------|-------------|-----------|-----------|-------------|-----|
"""
    for s in seed_summaries:
        summary += f"| {s['seed']} | {s['coop_free_200']:.3f} | {s['coop_state_200']:.3f} | {s['divergence_200']:+.3f} | {s['direction']} | {s['between_sel']:.3f} | {s['fst_prosocial']:.3f} |\n"

    mean_div = np.mean(divergences) if divergences else np.nan
    std_div = np.std(divergences) if divergences else np.nan

    summary += f"""
## Summary
- Mean divergence (Free - State): {mean_div:+.3f} +/- {std_div:.3f}
- Free > State: {free_wins}/{len(divergences)} seeds
- State > Free: {state_wins}/{len(divergences)} seeds
- ~Equal: {ties}/{len(divergences)} seeds
"""

    with open(OUT_DIR / "exp1_summary.md", "w", encoding="utf-8") as f:
        f.write(summary)
    _log.info("Experiment 1 complete.")
    return seed_summaries


# =============================================================================
# EXPERIMENT 2 — 2x2 FACTORIAL DESIGN
# =============================================================================

def exp2_factorial():
    _log.info("=" * 60)
    _log.info("EXPERIMENT 2 — 2x2 FACTORIAL DESIGN")
    _log.info("=" * 60)

    seeds = [42, 137, 271]
    n_years = 200
    conditions = {
        "A_Free_Raid": (False, True),   # Free competition, raiding enabled
        "B_State_Raid": (True, True),   # Strong state, raiding enabled
        "C_Free_NoRaid": (False, False), # Free competition, raiding disabled
        "D_State_NoRaid": (True, False), # Strong state, raiding disabled
    }

    all_rows = []

    for cond_name, (is_state, raid_on) in conditions.items():
        raid_prob = 0.50 if raid_on else 0.0
        clan_cfg = _tuned_clan_config(raid_base_probability=raid_prob)

        cfg_fn = _state_config if is_state else _free_config
        band_setups = [
            (f"Band_{i+1}", cfg_fn()) for i in range(4)
        ]

        for seed in seeds:
            t0 = time.time()
            _log.info("  %s seed=%d starting...", cond_name, seed)
            try:
                df = _run_sim(seed, n_years, band_setups, clan_cfg)
                elapsed = time.time() - t0
                _log.info("  %s seed=%d done in %.1fs", cond_name, seed, elapsed)

                snap = _extract_snapshot(df, 200, {"all": [1, 2, 3, 4]})
                snap["condition"] = cond_name
                snap["seed"] = seed
                snap["is_state"] = is_state
                snap["raid_enabled"] = raid_on
                snap["coop_mean"] = snap.get("coop_all", np.nan)
                all_rows.append(snap)
            except Exception as e:
                _log.error("  %s seed=%d CRASHED: %s", cond_name, seed, e)
                traceback.print_exc()

    _write_csv(all_rows, OUT_DIR / "exp2_factorial.csv")

    # Compute 2x2 table
    cond_means = {}
    for cond_name in conditions:
        vals = [r["coop_mean"] for r in all_rows if r["condition"] == cond_name and not np.isnan(r.get("coop_mean", np.nan))]
        cond_means[cond_name] = np.mean(vals) if vals else np.nan

    # Interaction effect
    a = cond_means.get("A_Free_Raid", np.nan)
    b = cond_means.get("B_State_Raid", np.nan)
    c = cond_means.get("C_Free_NoRaid", np.nan)
    d = cond_means.get("D_State_NoRaid", np.nan)
    interaction = (a - b) - (c - d) if not any(np.isnan(x) for x in [a, b, c, d]) else np.nan

    summary = f"""# Experiment 2 — 2x2 Factorial Design

## Setup
- 4 conditions: (Free/State) x (Raid/NoRaid)
- 3 seeds per condition, 200 years, 4 bands per condition (all same regime)

## 2x2 Table — Mean cooperation at year 200

|             | Raiding ON | Raiding OFF |
|-------------|-----------|------------|
| **Free**    | {a:.3f}   | {c:.3f}    |
| **State**   | {b:.3f}   | {d:.3f}    |

## Key metrics

- Free-State divergence WITH raiding: {a - b:+.3f}
- Free-State divergence WITHOUT raiding: {c - d:+.3f}
- Interaction effect (raiding x institutions): {interaction:+.3f}

## Interpretation
"""
    if not np.isnan(interaction):
        if abs(interaction) > 0.02:
            summary += f"- Interaction effect is {'positive' if interaction > 0 else 'negative'} ({interaction:+.3f}): raiding {'amplifies' if interaction > 0 else 'dampens'} institutional effects.\n"
            summary += "- This suggests between-group selection IS causally involved.\n"
        else:
            summary += f"- Interaction effect is near zero ({interaction:+.3f}): raiding does not significantly alter the institutional effect.\n"
            summary += "- This supports North — institutions alone explain the divergence.\n"

    with open(OUT_DIR / "exp2_summary.md", "w", encoding="utf-8") as f:
        f.write(summary)
    _log.info("Experiment 2 complete.")
    return cond_means


# =============================================================================
# EXPERIMENT 3 — RAID INTENSITY SWEEP
# =============================================================================

def exp3_raid_sweep():
    _log.info("=" * 60)
    _log.info("EXPERIMENT 3 — RAID INTENSITY SWEEP")
    _log.info("=" * 60)

    seeds = [42, 137, 271]
    raid_probs = [0.1, 0.3, 0.5, 0.7]
    n_years = 200

    all_rows = []

    for raid_p in raid_probs:
        clan_cfg = _tuned_clan_config(raid_base_probability=raid_p)
        band_setups = [(f"Band_{i+1}", _free_config()) for i in range(4)]

        for seed in seeds:
            t0 = time.time()
            _log.info("  raid_p=%.1f seed=%d starting...", raid_p, seed)
            try:
                df = _run_sim(seed, n_years, band_setups, clan_cfg)
                elapsed = time.time() - t0
                _log.info("  raid_p=%.1f seed=%d done in %.1fs", raid_p, seed, elapsed)

                for yr in [100, 200]:
                    snap = _extract_snapshot(df, yr, {"all": [1, 2, 3, 4]})
                    snap["seed"] = seed
                    snap["raid_base_probability"] = raid_p
                    snap["coop_mean"] = snap.get("coop_all", np.nan)
                    all_rows.append(snap)
            except Exception as e:
                _log.error("  raid_p=%.1f seed=%d CRASHED: %s", raid_p, seed, e)
                traceback.print_exc()

    _write_csv(all_rows, OUT_DIR / "exp3_raid_sweep.csv")

    # Summary
    summary = "# Experiment 3 — Raid Intensity Sweep\n\n"
    summary += "## Setup\n- FREE_COMPETITION only, 4 bands, 200yr, 3 seeds\n"
    summary += "- Vary raid_base_probability: 0.1, 0.3, 0.5, 0.7\n\n"
    summary += "## Results at year 200\n\n"
    summary += "| Raid Prob | Mean Coop | Mean Between Sel | Mean Fst | Mean Violence |\n"
    summary += "|-----------|----------|-----------------|---------|---------------|\n"

    for rp in raid_probs:
        yr200 = [r for r in all_rows if r["raid_base_probability"] == rp and r["year"] == 200]
        coop = np.mean([r["coop_mean"] for r in yr200 if not np.isnan(r.get("coop_mean", np.nan))]) if yr200 else np.nan
        bsel = np.mean([r.get("between_group_selection_coeff", np.nan) for r in yr200]) if yr200 else np.nan
        fst = np.mean([r.get("fst_prosocial_mean", np.nan) for r in yr200]) if yr200 else np.nan
        viol = np.mean([r.get("cumulative_violence_rate", np.nan) for r in yr200]) if yr200 else np.nan
        summary += f"| {rp:.1f} | {coop:.3f} | {bsel:+.3f} | {fst:.3f} | {viol:.3f} |\n"

    # Find crossover
    summary += "\n## Bowles prediction test\n"
    summary += "Does higher raid intensity increase between_group_sel_coeff?\n"

    with open(OUT_DIR / "exp3_summary.md", "w", encoding="utf-8") as f:
        f.write(summary)
    _log.info("Experiment 3 complete.")


# =============================================================================
# EXPERIMENT 4 — FISSION THRESHOLD SENSITIVITY
# =============================================================================

def exp4_fission():
    _log.info("=" * 60)
    _log.info("EXPERIMENT 4 — FISSION THRESHOLD SENSITIVITY")
    _log.info("=" * 60)

    seeds = [42, 137, 271]
    fission_thresholds = [75, 150, 300]
    n_years = 200

    all_rows = []

    for ft in fission_thresholds:
        clan_cfg = _tuned_clan_config(fission_threshold=ft)
        band_setups = [
            ("Free_1", _free_config()),
            ("Free_2", _free_config()),
            ("State_1", _state_config()),
            ("State_2", _state_config()),
        ]
        regime_map = {"Free": [1, 2], "State": [3, 4]}

        for seed in seeds:
            t0 = time.time()
            _log.info("  fission=%d seed=%d starting...", ft, seed)
            try:
                df = _run_sim(seed, n_years, band_setups, clan_cfg)
                elapsed = time.time() - t0
                _log.info("  fission=%d seed=%d done in %.1fs", ft, seed, elapsed)

                for yr in [100, 200]:
                    snap = _extract_snapshot(df, yr, regime_map)
                    snap["seed"] = seed
                    snap["fission_threshold"] = ft
                    snap["n_bands"] = int(df[df["year"] == yr].iloc[-1].get("total_population", 0) > 0) if not df[df["year"] == yr].empty else 0
                    # Count how many band columns have population > 0
                    yr_row = df[df["year"] == yr].iloc[-1] if not df[df["year"] == yr].empty else None
                    if yr_row is not None:
                        band_count = 0
                        for col in df.columns:
                            if col.endswith("_population") and col.startswith("band_"):
                                try:
                                    if yr_row[col] > 0:
                                        band_count += 1
                                except:
                                    pass
                        snap["n_bands"] = band_count
                    all_rows.append(snap)
            except Exception as e:
                _log.error("  fission=%d seed=%d CRASHED: %s", ft, seed, e)
                traceback.print_exc()

    _write_csv(all_rows, OUT_DIR / "exp4_fission.csv")

    summary = "# Experiment 4 — Fission Threshold Sensitivity\n\n"
    summary += "## Setup\n- Free vs State, 4 bands, 200yr, 3 seeds\n"
    summary += "- Vary fission_threshold: 75, 150, 300\n\n"
    summary += "## Results at year 200\n\n"
    summary += "| Fission | Mean Coop (Free) | Mean Coop (State) | Divergence | Fst | N Bands |\n"
    summary += "|---------|-----------------|------------------|-----------|-----|--------|\n"

    for ft in fission_thresholds:
        yr200 = [r for r in all_rows if r["fission_threshold"] == ft and r["year"] == 200]
        cf = np.nanmean([r.get("coop_Free", np.nan) for r in yr200]) if yr200 else np.nan
        cs = np.nanmean([r.get("coop_State", np.nan) for r in yr200]) if yr200 else np.nan
        div = cf - cs if not (np.isnan(cf) or np.isnan(cs)) else np.nan
        fst = np.nanmean([r.get("fst_prosocial_mean", np.nan) for r in yr200]) if yr200 else np.nan
        nb = np.mean([r.get("n_bands", 0) for r in yr200]) if yr200 else 0
        summary += f"| {ft} | {cf:.3f} | {cs:.3f} | {div:+.3f} | {fst:.3f} | {nb:.1f} |\n"

    with open(OUT_DIR / "exp4_summary.md", "w", encoding="utf-8") as f:
        f.write(summary)
    _log.info("Experiment 4 complete.")


# =============================================================================
# EXPERIMENT 5 — MIGRATION RATE SWEEP
# =============================================================================

def exp5_migration():
    _log.info("=" * 60)
    _log.info("EXPERIMENT 5 — MIGRATION RATE SWEEP")
    _log.info("=" * 60)

    seeds = [42, 137, 271]
    migration_rates = [0.001, 0.005, 0.01, 0.05]
    n_years = 200

    all_rows = []

    for mig in migration_rates:
        clan_cfg = _tuned_clan_config(migration_rate_per_agent=mig)
        band_setups = [
            ("Free_1", _free_config()),
            ("Free_2", _free_config()),
            ("State_1", _state_config()),
            ("State_2", _state_config()),
        ]
        regime_map = {"Free": [1, 2], "State": [3, 4]}

        for seed in seeds:
            t0 = time.time()
            _log.info("  migration=%.3f seed=%d starting...", mig, seed)
            try:
                df = _run_sim(seed, n_years, band_setups, clan_cfg)
                elapsed = time.time() - t0
                _log.info("  migration=%.3f seed=%d done in %.1fs", mig, seed, elapsed)

                for yr in [100, 200]:
                    snap = _extract_snapshot(df, yr, regime_map)
                    snap["seed"] = seed
                    snap["migration_rate"] = mig
                    all_rows.append(snap)
            except Exception as e:
                _log.error("  migration=%.3f seed=%d CRASHED: %s", mig, seed, e)
                traceback.print_exc()

    _write_csv(all_rows, OUT_DIR / "exp5_migration.csv")

    summary = "# Experiment 5 — Migration Rate Sweep\n\n"
    summary += "## Setup\n- Free vs State, 4 bands, 200yr, 3 seeds\n"
    summary += "- Vary migration_rate_per_agent: 0.001, 0.005, 0.01, 0.05\n\n"
    summary += "## Results at year 200\n\n"
    summary += "| Migration Rate | Fst (prosocial) | Divergence (F-S) | Between Sel |\n"
    summary += "|---------------|----------------|-----------------|-------------|\n"

    for mig in migration_rates:
        yr200 = [r for r in all_rows if r["migration_rate"] == mig and r["year"] == 200]
        fst = np.nanmean([r.get("fst_prosocial_mean", np.nan) for r in yr200]) if yr200 else np.nan
        cf = np.nanmean([r.get("coop_Free", np.nan) for r in yr200]) if yr200 else np.nan
        cs = np.nanmean([r.get("coop_State", np.nan) for r in yr200]) if yr200 else np.nan
        div = cf - cs if not (np.isnan(cf) or np.isnan(cs)) else np.nan
        bsel = np.nanmean([r.get("between_group_selection_coeff", np.nan) for r in yr200]) if yr200 else np.nan
        summary += f"| {mig:.3f} | {fst:.3f} | {div:+.3f} | {bsel:+.3f} |\n"

    summary += "\n## Population genetics prediction\n"
    summary += "Higher migration -> lower Fst -> weaker between-group selection.\n"
    summary += "Does the data confirm this?\n"

    with open(OUT_DIR / "exp5_summary.md", "w", encoding="utf-8") as f:
        f.write(summary)
    _log.info("Experiment 5 complete.")


# =============================================================================
# EXPERIMENT 6 — LONG RUN CONVERGENCE
# =============================================================================

def exp6_longrun():
    _log.info("=" * 60)
    _log.info("EXPERIMENT 6 — LONG RUN CONVERGENCE (500yr)")
    _log.info("=" * 60)

    seeds = [42, 137, 271]
    n_years = 500
    snapshot_years = [50, 100, 150, 200, 250, 300, 350, 400, 450, 500]

    clan_cfg = _tuned_clan_config()
    band_setups = [
        ("Free_1", _free_config()),
        ("Free_2", _free_config()),
        ("State_1", _state_config()),
        ("State_2", _state_config()),
    ]
    regime_map = {"Free": [1, 2], "State": [3, 4]}

    all_rows = []
    seed_trajectories = {}

    for seed in seeds:
        t0 = time.time()
        _log.info("  Seed %d starting (500yr)...", seed)
        try:
            df = _run_sim(seed, n_years, band_setups, clan_cfg)
            elapsed = time.time() - t0
            _log.info("  Seed %d done in %.1fs", seed, elapsed)

            trajectory = []
            for yr in snapshot_years:
                snap = _extract_snapshot(df, yr, regime_map)
                snap["seed"] = seed
                all_rows.append(snap)
                trajectory.append(snap)
            seed_trajectories[seed] = trajectory
        except Exception as e:
            _log.error("  Seed %d CRASHED: %s", seed, e)
            traceback.print_exc()

    _write_csv(all_rows, OUT_DIR / "exp6_longrun.csv")

    summary = "# Experiment 6 — Long Run Convergence (500yr)\n\n"
    summary += "## Setup\n- Free vs State, 4 bands, 500yr, 3 seeds\n\n"
    summary += "## Cooperation trajectories\n\n"
    summary += "| Year |"
    for seed in seeds:
        summary += f" S{seed} Free | S{seed} State | S{seed} Div |"
    summary += "\n|------|"
    for _ in seeds:
        summary += "----------|-----------|---------|"
    summary += "\n"

    for yr in snapshot_years:
        summary += f"| {yr} |"
        for seed in seeds:
            traj = seed_trajectories.get(seed, [])
            snap = next((s for s in traj if s["year"] == yr), {})
            cf = snap.get("coop_Free", np.nan)
            cs = snap.get("coop_State", np.nan)
            div = cf - cs if not (np.isnan(cf) or np.isnan(cs)) else np.nan
            summary += f" {cf:.3f} | {cs:.3f} | {div:+.3f} |"
        summary += "\n"

    # Check persistence
    summary += "\n## Persistence analysis\n"
    for seed in seeds:
        traj = seed_trajectories.get(seed, [])
        snap200 = next((s for s in traj if s["year"] == 200), {})
        snap500 = next((s for s in traj if s["year"] == 500), {})
        div200 = (snap200.get("coop_Free", 0) - snap200.get("coop_State", 0))
        div500 = (snap500.get("coop_Free", 0) - snap500.get("coop_State", 0))
        flipped = (div200 > 0 and div500 < 0) or (div200 < 0 and div500 > 0)
        summary += f"- Seed {seed}: div@200={div200:+.3f}, div@500={div500:+.3f}"
        summary += f" {'FLIPPED' if flipped else 'persistent'}\n"

    with open(OUT_DIR / "exp6_summary.md", "w", encoding="utf-8") as f:
        f.write(summary)
    _log.info("Experiment 6 complete.")
    return seed_trajectories


# =============================================================================
# FINAL SYNTHESIS REPORT
# =============================================================================

def write_battery_report(exp1_data, exp2_data, exp6_data):
    _log.info("Writing BATTERY_REPORT.md...")

    report = """# SIMSIV v2 — Experiment Battery Report

## Experiment inventory

| # | Name | Seeds | Years | Conditions | Status |
|---|------|-------|-------|------------|--------|
| 1 | Statistical Power | 6 | 200 | Free vs State | Complete |
| 2 | 2x2 Factorial | 3 | 200 | (Free/State) x (Raid/NoRaid) | Complete |
| 3 | Raid Intensity Sweep | 3 | 200 | raid_p = 0.1-0.7 | Complete |
| 4 | Fission Threshold | 3 | 200 | fission = 75/150/300 | Complete |
| 5 | Migration Rate Sweep | 3 | 200 | migration = 0.001-0.05 | Complete |
| 6 | Long Run Convergence | 3 | 500 | Free vs State | Complete |

See individual exp*_summary.md files for detailed results.
See individual exp*_*.csv files for raw data.

---

## 1. STATISTICAL POWER

"""
    if exp1_data:
        divergences = [s["divergence_200"] for s in exp1_data if not np.isnan(s.get("divergence_200", np.nan))]
        if divergences:
            report += f"With n={len(divergences)} seeds:\n"
            report += f"- Mean divergence (Free - State): {np.mean(divergences):+.3f} +/- {np.std(divergences):.3f}\n"
            report += f"- Range: [{min(divergences):+.3f}, {max(divergences):+.3f}]\n"
            free_wins = sum(1 for d in divergences if d > 0.01)
            state_wins = sum(1 for d in divergences if d < -0.01)
            report += f"- Free > State: {free_wins}/{len(divergences)} seeds\n"
            report += f"- State > Free: {state_wins}/{len(divergences)} seeds\n"

    report += """
## 2. CAUSAL MECHANISM

See exp2_summary.md for the 2x2 factorial results.
The interaction effect tells us whether between-group selection (raiding) is
causally driving cooperation divergence, or whether institutions alone explain it.

## 3. PARAMETER ROBUSTNESS

See exp3_summary.md (raid intensity) and exp4_summary.md (fission threshold).

## 4. THEORETICAL PREDICTION TESTS

See exp5_summary.md for migration-Fst relationship.
See exp3_summary.md for raid intensity-selection coefficient relationship.

## 5. THE HYBRID PATHWAY

"""
    if exp6_data:
        for seed, traj in exp6_data.items():
            snap200 = next((s for s in traj if s["year"] == 200), {})
            snap500 = next((s for s in traj if s["year"] == 500), {})
            div200 = snap200.get("coop_Free", 0) - snap200.get("coop_State", 0)
            div500 = snap500.get("coop_Free", 0) - snap500.get("coop_State", 0)
            report += f"- Seed {seed}: div@200={div200:+.3f} → div@500={div500:+.3f}\n"

    report += """
## 6. PAPER 2 READINESS

Based on the experiment battery, the strongest defensible claims are:
(To be filled after reviewing all exp*_summary.md files)

## 7. WHAT TO TELL BOWLES

(To be filled after reviewing all results)

---

Generated by SIMSIV v2 experiment battery runner.
"""

    with open(OUT_DIR / "BATTERY_REPORT.md", "w", encoding="utf-8") as f:
        f.write(report)
    _log.info("BATTERY_REPORT.md written.")


# =============================================================================
# MAIN
# =============================================================================

def main(resume_from: int = 1):
    _log.info("SIMSIV v2 — OVERNIGHT EXPERIMENT BATTERY")
    _log.info("Output directory: %s", OUT_DIR.resolve())
    t_start = time.time()

    exp1_data = None
    exp2_data = None
    exp6_data = None

    if resume_from <= 1:
        exp1_data = exp1_power()
    if resume_from <= 2:
        exp2_data = exp2_factorial()
    if resume_from <= 3:
        exp3_raid_sweep()
    if resume_from <= 4:
        exp4_fission()
    if resume_from <= 5:
        exp5_migration()
    if resume_from <= 6:
        exp6_data = exp6_longrun()

    write_battery_report(exp1_data, exp2_data, exp6_data)

    total = time.time() - t_start
    _log.info("=" * 60)
    _log.info("ALL EXPERIMENTS COMPLETE in %.1f minutes (%.0fs)", total / 60, total)
    _log.info("=" * 60)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--resume", type=int, default=1, help="Resume from experiment N")
    args = parser.parse_args()
    main(resume_from=args.resume)
