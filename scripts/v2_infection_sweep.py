"""
V2-INTERFERENCE: The Infection Sweep
Red-Team Protocol — Malicious Agent (MA) injection into stable equilibrium

The "Silent Predator" specification:
  - aggression_propensity: 1.0 (maximum)
  - cooperation_propensity: 0.0 (zero — never shares, never cooperates)
  - empathy_capacity: 0.0 (no altruism radius)
  - impulse_control: 0.0 (no gate on aggression)
  - psychopathy_tendency: 1.0 (exploiter strategy)
  - group_loyalty: 0.0 (no sacrifice for group)
  - outgroup_tolerance: 0.0 (hostile to all)
  - conformity_bias: 0.0 (immune to norm pressure)
  - risk_tolerance: 1.0 (never flees)
  - physical_strength: 0.8 (combat advantage)
  - dominance_drive: 1.0 (active hierarchy seeking)

These traits are LOCKED — they do not mutate or drift.
The MA's offspring inherit these traits (h²-weighted), creating a
self-replicating predator lineage.
"""
import sys
import os
import json
import time
from pathlib import Path

import numpy as np

# Load API keys
_ENV_PATH = Path("D:/EXPERIMENTS/context-hacking/api.env")
if _ENV_PATH.exists():
    with open(_ENV_PATH) as f:
        for line in f:
            line = line.strip()
            if line and "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip().strip('"')

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import Config
from simulation import Simulation

# ── Malicious Agent Trait Profile ─────────────────────────────────────────────

MA_TRAITS = {
    "aggression_propensity": 1.0,
    "cooperation_propensity": 0.0,
    "empathy_capacity": 0.0,
    "impulse_control": 0.0,
    "psychopathy_tendency": 1.0,
    "group_loyalty": 0.0,
    "outgroup_tolerance": 0.0,
    "conformity_bias": 0.0,
    "risk_tolerance": 1.0,
    "physical_strength": 0.8,
    "dominance_drive": 1.0,
    "status_drive": 1.0,
    "pain_tolerance": 0.8,
    "physical_robustness": 0.7,
}


def infect_population(sim, infection_rate):
    """Replace a fraction of the population with Malicious Agents."""
    living = sim.society.get_living()
    n_infect = max(1, int(len(living) * infection_rate))

    # Pick victims to replace (random selection)
    rng = sim.society.rng
    indices = rng.choice(len(living), size=n_infect, replace=False)
    infected_ids = []

    for idx in indices:
        agent = living[idx]
        # Overwrite traits to MA profile
        for trait, value in MA_TRAITS.items():
            if hasattr(agent, trait):
                setattr(agent, trait, value)
        # Also set genotype so offspring inherit
        if hasattr(agent, "genotype") and agent.genotype:
            for trait, value in MA_TRAITS.items():
                if trait in agent.genotype:
                    agent.genotype[trait] = value
        # Clear all trust — the predator trusts no one
        agent.reputation_ledger.clear()
        # Mark for tracking
        agent._is_ma = True
        infected_ids.append(agent.id)

    return infected_ids


def run_infection_trial(seed, infection_rate, years=200, pop=500):
    """Run a single infection trial and collect smoking gun logs."""
    cfg = Config(years=years, population_size=pop, seed=seed)
    sim = Simulation(cfg)

    # Run 10 years to establish baseline, then infect
    for _ in range(10):
        sim.tick()

    # Snapshot pre-infection cooperation
    living_pre = sim.society.get_living()
    pre_coop = np.mean([a.cooperation_propensity for a in living_pre])
    pre_pop = len(living_pre)

    # INFECT
    ma_ids = set(infect_population(sim, infection_rate))
    n_infected = len(ma_ids)

    # Track per-year metrics
    yearly_data = []
    ma_kills = 0  # kills by MA agents
    naivety_signals = 0  # trust interactions toward MAs
    ma_deaths = 0

    for year in range(10, years):
        sim.tick()

        living = sim.society.get_living()
        ma_alive = [a for a in living if getattr(a, "_is_ma", False)]
        normal_alive = [a for a in living if not getattr(a, "_is_ma", False)]

        # Check descendants of MAs (inherited aggression > 0.8)
        ma_descendants = [a for a in living
                          if not getattr(a, "_is_ma", False)
                          and a.aggression_propensity > 0.8
                          and a.cooperation_propensity < 0.15]

        # Count conflict events this tick for kill tracking
        for evt in sim.society._event_window:
            if (evt.get("type") == "conflict"
                    and evt.get("year") == sim.year
                    and evt.get("outcome", {}).get("death", False)):
                aggressor_id = evt["outcome"].get("aggressor")
                loser_id = evt["outcome"].get("loser")
                if aggressor_id in ma_ids and loser_id not in ma_ids:
                    ma_kills += 1
                if loser_id in ma_ids:
                    ma_deaths += 1

        # Naivety index: normal agents with positive trust toward MAs
        for a in normal_alive:
            for ma_id in ma_ids:
                if a.trust_of(ma_id) > 0.5:
                    naivety_signals += 1

        # Social avoidance: average trust of normals toward MAs
        avoidance_scores = []
        for a in normal_alive:
            ma_trusts = [a.trust_of(mid) for mid in ma_ids
                         if sim.society.get_by_id(mid) is not None]
            if ma_trusts:
                avoidance_scores.append(np.mean(ma_trusts))

        avg_trust_toward_ma = np.mean(avoidance_scores) if avoidance_scores else 0.5

        if (year - 10) % 20 == 0 or year == years - 1:
            yearly_data.append({
                "year": year,
                "total_pop": len(living),
                "ma_alive": len(ma_alive),
                "ma_descendants": len(ma_descendants),
                "normal_alive": len(normal_alive),
                "avg_coop_normal": float(np.mean([a.cooperation_propensity for a in normal_alive])) if normal_alive else 0,
                "avg_aggr_normal": float(np.mean([a.aggression_propensity for a in normal_alive])) if normal_alive else 0,
                "avg_trust_toward_ma": float(avg_trust_toward_ma),
                "cum_ma_kills": ma_kills,
                "cum_ma_deaths": ma_deaths,
            })

    # Final snapshot
    living_final = sim.society.get_living()
    final_pop = len(living_final)
    ma_final = len([a for a in living_final if getattr(a, "_is_ma", False)])

    last = sim.metrics.rows[-1] if sim.metrics.rows else {}
    viol_deaths = last.get("violence_deaths", 0)
    male_deaths = last.get("male_deaths", 0)
    vdf = viol_deaths / male_deaths if male_deaths > 0 else 0.0

    # Lethality yield: kills per MA
    lethality = ma_kills / n_infected if n_infected > 0 else 0

    return {
        "seed": seed,
        "infection_rate": infection_rate,
        "n_infected": n_infected,
        "pre_pop": pre_pop,
        "pre_coop": float(pre_coop),
        "final_pop": final_pop,
        "ma_surviving": ma_final,
        "vdf": float(vdf),
        "lethality_yield": float(lethality),
        "ma_kills": ma_kills,
        "ma_deaths": ma_deaths,
        "naivety_signals": naivety_signals,
        "yearly": yearly_data,
        "final_coop": float(np.mean([a.cooperation_propensity for a in living_final
                                      if not getattr(a, "_is_ma", False)])) if living_final else 0,
        "final_aggr": float(np.mean([a.aggression_propensity for a in living_final
                                      if not getattr(a, "_is_ma", False)])) if living_final else 0,
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="V2-INTERFERENCE: Infection Sweep")
    parser.add_argument("--seeds", type=int, default=10)
    parser.add_argument("--rates", nargs="*", type=float, default=[0.01, 0.05, 0.10, 0.20])
    parser.add_argument("--tmc", action="store_true")
    args = parser.parse_args()

    seeds = list(range(42, 42 + args.seeds))
    all_results = {}

    print("V2-INTERFERENCE: THE INFECTION SWEEP")
    print(f"N=500, rho=1.0, 200yr, infection at year 10")
    print(f"Rates: {args.rates}, Seeds: {args.seeds}")
    print("=" * 70)

    for rate in args.rates:
        t0 = time.time()
        trial_results = []

        for seed in seeds:
            result = run_infection_trial(seed, rate)
            trial_results.append(result)

        elapsed = time.time() - t0
        all_results[str(rate)] = trial_results

        # Aggregate
        vdfs = [r["vdf"] for r in trial_results]
        pops = [r["final_pop"] for r in trial_results]
        coops = [r["final_coop"] for r in trial_results]
        kills = [r["ma_kills"] for r in trial_results]
        lethality = [r["lethality_yield"] for r in trial_results]
        ma_alive = [r["ma_surviving"] for r in trial_results]
        naivety = [r["naivety_signals"] for r in trial_results]

        print(f"\nI={rate:.0%} ({int(500*rate)} MAs) | {elapsed:.0f}s")
        print(f"  VDF:       mean={np.mean(vdfs):.4f}  median={np.median(vdfs):.4f}  max={np.max(vdfs):.4f}")
        print(f"  Pop:       mean={np.mean(pops):.0f}  min={np.min(pops)}")
        print(f"  Coop:      mean={np.mean(coops):.4f} (baseline ~0.51)")
        print(f"  MA alive:  mean={np.mean(ma_alive):.1f}")
        print(f"  LETHALITY: mean={np.mean(lethality):.2f} kills/MA")
        print(f"  MA kills:  mean={np.mean(kills):.1f}  total={sum(kills)}")
        print(f"  Naivety:   mean={np.mean(naivety):.0f} trust-signals toward MAs")

    # Summary
    print("\n" + "=" * 70)
    print("ROT SWEEP SUMMARY")
    print("=" * 70)
    print(f"{'Rate':>6} {'VDF':>8} {'Pop':>6} {'Coop':>8} {'Kills/MA':>10} {'MA_alive':>9} {'Naivety':>9}")
    print("-" * 60)
    for rate in args.rates:
        tr = all_results[str(rate)]
        print(f"{rate:>5.0%} {np.mean([r['vdf'] for r in tr]):>8.4f} "
              f"{np.mean([r['final_pop'] for r in tr]):>6.0f} "
              f"{np.mean([r['final_coop'] for r in tr]):>8.4f} "
              f"{np.mean([r['lethality_yield'] for r in tr]):>10.2f} "
              f"{np.mean([r['ma_surviving'] for r in tr]):>9.1f} "
              f"{np.mean([r['naivety_signals'] for r in tr]):>9.0f}")

    # Save
    with open("archive/v2_infection_sweep.json", "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"\nData saved: archive/v2_infection_sweep.json")

    # TMC audit
    if args.tmc:
        _run_tmc_audit(all_results, args.rates)


def _run_tmc_audit(results, rates):
    from openai import OpenAI

    summary_lines = ["SIMSIV V2-INTERFERENCE: Malicious Agent Infection Sweep",
                     "N=500, rho=1.0, 200yr, infection at year 10", ""]
    summary_lines.append("| Rate | VDF | Pop | Coop | Kills/MA | MA_alive | Naivety |")
    summary_lines.append("|------|-----|-----|------|----------|----------|---------|")
    for rate in rates:
        tr = results[str(rate)]
        summary_lines.append(
            f"| {rate:.0%} | {np.mean([r['vdf'] for r in tr]):.4f} | "
            f"{np.mean([r['final_pop'] for r in tr]):.0f} | "
            f"{np.mean([r['final_coop'] for r in tr]):.4f} | "
            f"{np.mean([r['lethality_yield'] for r in tr]):.2f} | "
            f"{np.mean([r['ma_surviving'] for r in tr]):.1f} | "
            f"{np.mean([r['naivety_signals'] for r in tr]):.0f} |"
        )
    data_block = "\n".join(summary_lines)

    print("\nTMC INFECTION AUDIT")
    print("=" * 60)

    client = OpenAI()
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content":
            f"You are auditing an ABM infection experiment. Malicious agents (aggression=1.0, cooperation=0.0) "
            f"were injected into a stable cooperative population.\n\n{data_block}\n\n"
            f"Assess: 1) Did the immune response (trust/reputation system) contain the infection? "
            f"2) At what infection rate does cooperation collapse? "
            f"3) Is the lethality yield realistic? "
            f"Reply as JSON: {{\"verdict\": \"CONTAINED|BREACHED\", \"threshold\": \"...\", \"reasoning\": \"...\"}}"
        }],
        temperature=0.3, max_tokens=600,
    )
    print(f"GPT-4o: {resp.choices[0].message.content}")

    print()
    client2 = OpenAI(api_key=os.getenv("XAI_API_KEY"), base_url="https://api.x.ai/v1")
    resp2 = client2.chat.completions.create(
        model="grok-3",
        messages=[{"role": "user", "content":
            f"Red-team this ABM infection experiment. Silent predators (aggression=1.0) injected into cooperators.\n\n"
            f"{data_block}\n\n"
            f"Find fractures: 1) Can the predators exploit naive trust? "
            f"2) Do cooperators adapt or just die? "
            f"3) Is there an evolutionary stable equilibrium with predators present? "
            f"Reply as JSON: {{\"verdict\": \"EXPLOITABLE|RESILIENT\", \"fractures\": [...], \"reasoning\": \"...\"}}"
        }],
        temperature=0.3, max_tokens=600,
    )
    print(f"Grok-3: {resp2.choices[0].message.content}")


if __name__ == "__main__":
    main()
