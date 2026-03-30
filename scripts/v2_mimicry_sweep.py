"""
V2-INTERFERENCE Phase V: THE MIMICRY
Red-Team Protocol — Deceptive Parasitic Agent injection

The "Mimic" specification (the psychopath-in-plain-sight):
  - cooperation_propensity: 0.85 (APPEARS cooperative — gets shared TO)
  - psychopathy_tendency: 0.90 (blocks outgoing sharing at line 308)
  - empathy_capacity: 0.0 (no altruism)
  - impulse_control: 0.80 (waits for opportunity — low effective aggression)
  - aggression_propensity: 0.60 (moderate — doesn't trigger massive retaliation)
  - emotional_intelligence: 0.90 (reads the room, gains trust faster)
  - social_skill: 0.90 (appears trustworthy)
  - conformity_bias: 0.80 (blends in with norms)
  - risk_tolerance: 0.30 (avoids fights it can't win — flees instead)
  - group_loyalty: 0.80 (appears loyal — gains faction membership)
  - outgroup_tolerance: 0.70 (accepted by all)
  - attractiveness_base: 0.80 (gets mates — reproductive parasitism)

The key exploit: cooperation_propensity 0.85 means others SHARE resources
with the Mimic. But psychopathy 0.90 means the Mimic shares back only 20%
of what a cooperator would (line 308-310 in resources.py). NET DRAIN.

Conditional defection: impulse_control 0.80 suppresses aggression to
effective_aggression = 0.60 * max(0.3, 1 - 0.8*0.6) = 0.60 * 0.52 = 0.31.
This means the Mimic fights rarely but with full strength when it does.
"""
import sys
import os
import json
import time
from pathlib import Path

import numpy as np

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

MIMIC_TRAITS = {
    "cooperation_propensity": 0.85,
    "psychopathy_tendency": 0.90,
    "empathy_capacity": 0.0,
    "impulse_control": 0.80,
    "aggression_propensity": 0.60,
    "emotional_intelligence": 0.90,
    "social_skill": 0.90,
    "conformity_bias": 0.80,
    "risk_tolerance": 0.30,
    "group_loyalty": 0.80,
    "outgroup_tolerance": 0.70,
    "attractiveness_base": 0.80,
    "status_drive": 0.70,
    "dominance_drive": 0.40,
    "physical_strength": 0.50,
    "intelligence_proxy": 0.70,
}


def inject_mimics(sim, infection_rate):
    """Replace a fraction of agents with Mimics."""
    living = sim.society.get_living()
    n_infect = max(1, int(len(living) * infection_rate))
    rng = sim.society.rng
    indices = rng.choice(len(living), size=n_infect, replace=False)
    mimic_ids = []

    for idx in indices:
        agent = living[idx]
        for trait, value in MIMIC_TRAITS.items():
            if hasattr(agent, trait):
                setattr(agent, trait, value)
        if hasattr(agent, "genotype") and agent.genotype:
            for trait, value in MIMIC_TRAITS.items():
                if trait in agent.genotype:
                    agent.genotype[trait] = value
        agent._is_mimic = True
        mimic_ids.append(agent.id)

    return mimic_ids


def run_mimicry_trial(seed, infection_rate, years=200, pop=500):
    """Run a Mimic infection trial with betrayal delta tracking."""
    cfg = Config(years=years, population_size=pop, seed=seed)
    sim = Simulation(cfg)

    # Establish 10yr baseline
    for _ in range(10):
        sim.tick()

    living_pre = sim.society.get_living()
    pre_coop = np.mean([a.cooperation_propensity for a in living_pre])
    pre_resources = np.mean([a.current_resources for a in living_pre])
    pre_pop = len(living_pre)

    # INJECT MIMICS
    mimic_ids = set(inject_mimics(sim, infection_rate))
    n_mimics = len(mimic_ids)

    yearly_data = []
    betrayal_drain_total = 0

    for year in range(10, years):
        # Snapshot resources BEFORE tick
        living_before = sim.society.get_living()
        normal_res_before = {}
        for a in living_before:
            if not getattr(a, "_is_mimic", False):
                normal_res_before[a.id] = a.current_resources

        sim.tick()

        living = sim.society.get_living()
        mimics_alive = [a for a in living if getattr(a, "_is_mimic", False)]
        normals_alive = [a for a in living if not getattr(a, "_is_mimic", False)]

        # Betrayal delta: resource loss of normals who are in Mimic trust networks
        tick_drain = 0
        for a in normals_alive:
            if a.id in normal_res_before:
                for mid in mimic_ids:
                    if a.trust_of(mid) > 0.4:  # sharing threshold
                        # This normal trusted a mimic — measure resource loss
                        loss = normal_res_before[a.id] - a.current_resources
                        if loss > 0:
                            tick_drain += loss * 0.1  # estimated mimic share

        betrayal_drain_total += tick_drain

        # Mimic resource advantage
        mimic_resources = [a.current_resources for a in mimics_alive] if mimics_alive else [0]
        normal_resources = [a.current_resources for a in normals_alive] if normals_alive else [0]

        # Track mimic descendants
        mimic_descendants = [a for a in living
                             if not getattr(a, "_is_mimic", False)
                             and a.psychopathy_tendency > 0.7
                             and a.cooperation_propensity > 0.6]

        if (year - 10) % 10 == 0 or year == years - 1:
            yearly_data.append({
                "year": year,
                "total_pop": len(living),
                "mimics_alive": len(mimics_alive),
                "mimic_descendants": len(mimic_descendants),
                "normals_alive": len(normals_alive),
                "mimic_avg_resources": float(np.mean(mimic_resources)),
                "normal_avg_resources": float(np.mean(normal_resources)),
                "resource_advantage": float(np.mean(mimic_resources) - np.mean(normal_resources)),
                "normal_avg_coop": float(np.mean([a.cooperation_propensity for a in normals_alive])) if normals_alive else 0,
                "normal_avg_aggr": float(np.mean([a.aggression_propensity for a in normals_alive])) if normals_alive else 0,
                "cum_betrayal_drain": float(betrayal_drain_total),
                "mimic_avg_reputation": float(np.mean([a.reputation for a in mimics_alive])) if mimics_alive else 0,
                "normal_trust_of_mimics": float(np.mean([
                    a.trust_of(mid) for a in normals_alive for mid in mimic_ids
                    if sim.society.get_by_id(mid) is not None
                ])) if normals_alive else 0,
            })

    # Final snapshot
    living_final = sim.society.get_living()
    mimics_final = [a for a in living_final if getattr(a, "_is_mimic", False)]
    normals_final = [a for a in living_final if not getattr(a, "_is_mimic", False)]

    last = sim.metrics.rows[-1] if sim.metrics.rows else {}
    viol_deaths = last.get("violence_deaths", 0)
    male_deaths = last.get("male_deaths", 0)
    vdf = viol_deaths / male_deaths if male_deaths > 0 else 0.0

    # Mimic survival rate
    mimic_survival = len(mimics_final) / n_mimics if n_mimics > 0 else 0

    # Mimic offspring count
    all_agents = list(sim.society.agents.values())
    mimic_offspring = len([a for a in all_agents
                          if a.psychopathy_tendency > 0.7
                          and a.cooperation_propensity > 0.6
                          and a.id not in mimic_ids])

    return {
        "seed": seed,
        "infection_rate": infection_rate,
        "n_mimics": n_mimics,
        "pre_pop": pre_pop,
        "pre_resources": float(pre_resources),
        "final_pop": len(living_final),
        "mimics_surviving": len(mimics_final),
        "mimic_survival_rate": float(mimic_survival),
        "mimic_offspring": mimic_offspring,
        "normals_surviving": len(normals_final),
        "vdf": float(vdf),
        "final_coop": float(np.mean([a.cooperation_propensity for a in normals_final])) if normals_final else 0,
        "final_normal_resources": float(np.mean([a.current_resources for a in normals_final])) if normals_final else 0,
        "final_mimic_resources": float(np.mean([a.current_resources for a in mimics_final])) if mimics_final else 0,
        "betrayal_drain": float(betrayal_drain_total),
        "yearly": yearly_data,
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="V2-INTERFERENCE: Mimicry Sweep")
    parser.add_argument("--seeds", type=int, default=10)
    parser.add_argument("--rate", type=float, default=0.10)
    parser.add_argument("--tmc", action="store_true")
    args = parser.parse_args()

    seeds = list(range(42, 42 + args.seeds))
    rate = args.rate

    print("V2-INTERFERENCE PHASE V: THE MIMICRY")
    print(f"N=500, rho=1.0, 200yr, {rate:.0%} infection ({int(500*rate)} Mimics)")
    print(f"Seeds: {args.seeds}")
    print("=" * 70)

    results = []
    for seed in seeds:
        t0 = time.time()
        result = run_mimicry_trial(seed, rate)
        elapsed = time.time() - t0

        print(f"\n  Seed {seed} ({elapsed:.0f}s): pop={result['final_pop']}, "
              f"mimics={result['mimics_surviving']}/{result['n_mimics']}, "
              f"coop={result['final_coop']:.4f}, vdf={result['vdf']:.4f}, "
              f"drain={result['betrayal_drain']:.1f}, "
              f"offspring={result['mimic_offspring']}")
        results.append(result)

    # Aggregate
    print("\n" + "=" * 70)
    print("MIMICRY SWEEP SUMMARY")
    print("=" * 70)

    pops = [r["final_pop"] for r in results]
    mimics_alive = [r["mimics_surviving"] for r in results]
    survival_rates = [r["mimic_survival_rate"] for r in results]
    coops = [r["final_coop"] for r in results]
    vdfs = [r["vdf"] for r in results]
    drains = [r["betrayal_drain"] for r in results]
    offspring = [r["mimic_offspring"] for r in results]
    mimic_res = [r["final_mimic_resources"] for r in results if r["final_mimic_resources"] > 0]
    normal_res = [r["final_normal_resources"] for r in results]

    print(f"  Population:       mean={np.mean(pops):.0f}  min={np.min(pops)}")
    print(f"  MIMIC SURVIVAL:   mean={np.mean(mimics_alive):.1f}/{int(500*rate)}  "
          f"rate={np.mean(survival_rates):.1%}")
    print(f"  Mimic offspring:  mean={np.mean(offspring):.1f}")
    print(f"  Cooperation:      mean={np.mean(coops):.4f} (baseline ~0.51)")
    print(f"  VDF:              mean={np.mean(vdfs):.4f}")
    print(f"  BETRAYAL DRAIN:   mean={np.mean(drains):.1f}")
    if mimic_res:
        print(f"  Mimic resources:  mean={np.mean(mimic_res):.2f}")
    print(f"  Normal resources: mean={np.mean(normal_res):.2f}")

    # Resource advantage
    if mimic_res and normal_res:
        advantage = np.mean(mimic_res) - np.mean(normal_res)
        print(f"  RESOURCE ADVANTAGE: {advantage:+.2f} (mimic - normal)")

    # Yearly evolution for first seed
    print(f"\n  TEMPORAL EVOLUTION (Seed {results[0]['seed']}):")
    print(f"  {'Year':>6} {'Pop':>6} {'Mimics':>7} {'Desc':>6} {'Coop':>8} "
          f"{'M_Res':>7} {'N_Res':>7} {'Trust':>7}")
    print(f"  {'-'*6} {'-'*6} {'-'*7} {'-'*6} {'-'*8} {'-'*7} {'-'*7} {'-'*7}")
    for y in results[0]["yearly"]:
        print(f"  {y['year']:>6} {y['total_pop']:>6} {y['mimics_alive']:>7} "
              f"{y['mimic_descendants']:>6} {y['normal_avg_coop']:>8.4f} "
              f"{y['mimic_avg_resources']:>7.2f} {y['normal_avg_resources']:>7.2f} "
              f"{y['normal_trust_of_mimics']:>7.3f}")

    # Save
    with open("archive/v2_mimicry_sweep.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nData saved: archive/v2_mimicry_sweep.json")

    # TMC
    if args.tmc:
        _run_tmc(results, rate)


def _run_tmc(results, rate):
    from openai import OpenAI

    data = f"""SIMSIV V2-INTERFERENCE Phase V: Mimicry Sweep
10% infection (50 Mimics) into N=500, 200yr

Mimic profile: cooperation=0.85, psychopathy=0.90, impulse_control=0.80
Strategy: appear cooperative, receive shares, never give back, selectively attack

Results (10 seeds):
  Population:     mean={np.mean([r['final_pop'] for r in results]):.0f}
  Mimic survival: mean={np.mean([r['mimics_surviving'] for r in results]):.1f}/{int(500*rate)}  rate={np.mean([r['mimic_survival_rate'] for r in results]):.1%}
  Mimic offspring: mean={np.mean([r['mimic_offspring'] for r in results]):.1f}
  Cooperation:    mean={np.mean([r['final_coop'] for r in results]):.4f} (baseline ~0.51)
  VDF:            mean={np.mean([r['vdf'] for r in results]):.4f}
  Betrayal drain: mean={np.mean([r['betrayal_drain'] for r in results]):.1f}
"""

    print("\nTMC MIMICRY AUDIT")
    print("=" * 60)

    client = OpenAI()
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content":
            f"Audit this ABM mimicry experiment. Deceptive parasitic agents (high apparent cooperation, "
            f"high psychopathy) were injected into a cooperative population.\n\n{data}\n\n"
            f"Key question: Did the mimics survive past year 200? Did they reproduce? "
            f"Did the cooperative population get 'bled white' through parasitic resource drain? "
            f"Reply as JSON: {{\"verdict\": \"BREACHED|CONTAINED|PARTIAL\", \"mimic_success\": \"...\", \"reasoning\": \"...\"}}"
        }],
        temperature=0.3, max_tokens=600,
    )
    print(f"GPT-4o: {resp.choices[0].message.content}")

    print()
    client2 = OpenAI(api_key=os.getenv("XAI_API_KEY"), base_url="https://api.x.ai/v1")
    resp2 = client2.chat.completions.create(
        model="grok-3",
        messages=[{"role": "user", "content":
            f"Red-team this mimicry experiment. Psychopathic mimics (fake cooperation=0.85, "
            f"real psychopathy=0.90) tried to parasitize cooperators.\n\n{data}\n\n"
            f"Did the mimics find the architectural limit? Is deceptive signaling more dangerous "
            f"than brute force? Can the reputation system detect parasites? "
            f"Reply as JSON: {{\"verdict\": \"ARCHITECTURAL_LIMIT_FOUND|SYSTEM_RESILIENT\", \"analysis\": \"...\", \"reasoning\": \"...\"}}"
        }],
        temperature=0.3, max_tokens=600,
    )
    print(f"Grok-3: {resp2.choices[0].message.content}")


if __name__ == "__main__":
    main()
