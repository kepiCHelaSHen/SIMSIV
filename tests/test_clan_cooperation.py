"""
3-seed stress test for clan cooperation foundation (Milestone 1).

SIMSIV-V2 Turn 11 — VALIDATION MODE.
Seeds: 42, 137, 271.
Anomaly threshold: σ > 0.15 triggers anomaly detection.
"""

from __future__ import annotations

import sys
import numpy as np

from config import Config
from models.clan.clan_simulation import ClanSimulation
from models.clan.clan_base import (
    compute_individual_cooperation,
    compute_band_cooperation,
    compute_clan_cooperation,
)


def run_seed(seed: int, n_years: int = 50, n_bands: int = 3,
             pop_per_band: int = 30) -> dict:
    """Run a ClanSimulation and compute cooperation metrics at final year."""
    sim = ClanSimulation(
        seed=seed,
        n_years=n_years,
        n_bands=n_bands,
        population_per_band=pop_per_band,
    )
    sim.run()
    clan_coop = compute_clan_cooperation(sim.clan_society)

    # Also compute per-band details
    band_details = {}
    for bid, band in sim.clan_society.bands.items():
        band_coop = compute_band_cooperation(band)
        band_details[bid] = band_coop

    return {
        "seed": seed,
        "clan_mean_cooperation": clan_coop["clan_mean_cooperation"],
        "clan_cooperation_variance": clan_coop["clan_cooperation_variance"],
        "mean_collective_action_capacity": clan_coop["mean_collective_action_capacity"],
        "mean_inter_band_trust": clan_coop["mean_inter_band_trust"],
        "per_band": clan_coop["per_band"],
        "total_population": sim.clan_society.total_population(),
    }


def main():
    seeds = [42, 137, 271]
    results = []

    print("=" * 70)
    print("SIMSIV-V2 Milestone 1 — Cooperation Foundation Stress Test")
    print("=" * 70)
    print(f"Seeds: {seeds}")
    print(f"Simulation: 50 years, 3 bands, 30 agents/band")
    print()

    for seed in seeds:
        print(f"--- Seed {seed} ---")
        r = run_seed(seed)
        results.append(r)
        print(f"  clan_mean_cooperation:          {r['clan_mean_cooperation']:.4f}")
        print(f"  clan_cooperation_variance:      {r['clan_cooperation_variance']:.6f}")
        print(f"  mean_collective_action_capacity: {r['mean_collective_action_capacity']:.4f}")
        print(f"  mean_inter_band_trust:          {r['mean_inter_band_trust']:.4f}")
        print(f"  total_population:               {r['total_population']}")
        for bid, bm in r["per_band"].items():
            print(f"    Band {bid}: mean_coop={bm['mean_cooperation']:.3f}, "
                  f"var={bm['cooperation_variance']:.4f}, "
                  f"density={bm['trust_network_density']:.3f}, "
                  f"CAC={bm['collective_action_capacity']:.3f}")
        print()

    # ── Variance check (σ across seeds) ──────────────────────────────────
    clan_means = [r["clan_mean_cooperation"] for r in results]
    cac_values = [r["mean_collective_action_capacity"] for r in results]

    sigma_coop = float(np.std(clan_means))
    sigma_cac = float(np.std(cac_values))

    print("=" * 70)
    print("CROSS-SEED VARIANCE ANALYSIS")
    print("=" * 70)
    print(f"clan_mean_cooperation per seed: {[f'{v:.4f}' for v in clan_means]}")
    print(f"  mean = {np.mean(clan_means):.4f}")
    print(f"  σ    = {sigma_coop:.4f}")
    print()
    print(f"mean_CAC per seed:              {[f'{v:.4f}' for v in cac_values]}")
    print(f"  mean = {np.mean(cac_values):.4f}")
    print(f"  σ    = {sigma_cac:.4f}")
    print()

    # ── Anomaly detection (Step 12) ──────────────────────────────────────
    anomaly = False
    if sigma_coop > 0.15:
        anomaly = True
        print("*** ANOMALY DETECTED (Step 12) ***")
        print(f"  cooperation σ = {sigma_coop:.4f} > 0.15 threshold")
        print("  Foundation is UNSTABLE across seeds.")
        print("  Diagnosis: High cross-seed variance indicates that cooperation")
        print("  outcomes are sensitive to initial random state, suggesting")
        print("  insufficient convergence mechanisms or unstable equilibria.")
    else:
        print("STABLE: cooperation σ = {:.4f} ≤ 0.15 threshold".format(sigma_coop))

    if sigma_cac > 0.15:
        anomaly = True
        print(f"*** ANOMALY DETECTED: CAC σ = {sigma_cac:.4f} > 0.15 ***")
    else:
        print(f"STABLE: CAC σ = {sigma_cac:.4f} ≤ 0.15 threshold")

    print()
    if not anomaly:
        print("RESULT: FOUNDATION STABLE — Milestone 1 PASSED")
    else:
        print("RESULT: FOUNDATION UNSTABLE — requires investigation")

    return 0 if not anomaly else 1


if __name__ == "__main__":
    sys.exit(main())
