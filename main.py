"""
SIMSIV — CLI entry point.
Run: python main.py [--seed N] [--years N] [--population N] [--config path.yaml]
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from config import Config
from simulation import Simulation


def print_progress(year: int, row: dict):
    pop = row.get("population", 0)
    births = row.get("births", 0)
    deaths = row.get("deaths", 0)
    conflicts = row.get("conflicts", 0)
    gini = row.get("resource_gini", 0)
    violence = row.get("violence_rate", 0)
    eq = " [EQUILIBRIUM]" if row.get("equilibrium") else ""

    print(f"  Year {year:4d} | Pop {pop:5d} | "
          f"B/D {births:3d}/{deaths:3d} | "
          f"Conflicts {conflicts:3d} | "
          f"Gini {gini:.3f} | "
          f"Violence {violence:.3f}{eq}")


def save_outputs(sim: Simulation, output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)

    # Metrics CSV
    sim.metrics.save_csv(output_dir / "metrics.csv")

    # Events CSV
    import pandas as pd
    events_df = pd.DataFrame(sim.society.events)
    events_df.to_csv(output_dir / "events.csv", index=False)

    # Final agents
    living = sim.society.get_living()
    agents_data = []
    for a in living:
        agents_data.append({
            "id": a.id, "sex": a.sex.value, "age": a.age,
            "generation": a.generation, "health": round(a.health, 3),
            "resources": round(a.current_resources, 2),
            "status": round(a.current_status, 3),
            "aggression": round(a.aggression_propensity, 3),
            "cooperation": round(a.cooperation_propensity, 3),
            "attractiveness": round(a.attractiveness_base, 3),
            "intelligence": round(a.intelligence_proxy, 3),
            "offspring_count": len(a.offspring_ids),
            "pair_bonded": a.pair_bond_id is not None,
        })
    pd.DataFrame(agents_data).to_csv(output_dir / "final_agents.csv", index=False)

    # Summary JSON
    df = sim.metrics.to_dataframe()
    summary = {
        "seed": sim.config.seed,
        "years": sim.config.years,
        "population_size_initial": sim.config.population_size,
        "population_size_final": len(living),
        "total_births": int(df["births"].sum()),
        "total_deaths": int(df["deaths"].sum()),
        "total_conflicts": int(df["conflicts"].sum()),
        "avg_resource_gini": round(float(df["resource_gini"].mean()), 4),
        "avg_violence_rate": round(float(df["violence_rate"].mean()), 4),
        "avg_reproductive_skew": round(float(df["reproductive_skew"].mean()), 4),
        "equilibrium_reached": sim.society.equilibrium_flagged,
        "equilibrium_year": sim.society.equilibrium_year,
        "timestamp": datetime.now().isoformat(),
    }
    with open(output_dir / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    # Charts
    try:
        from visualizations.plots import plot_dashboard
        charts_dir = output_dir / "charts"
        charts_dir.mkdir(exist_ok=True)
        plot_dashboard(df, charts_dir)
    except Exception as e:
        print(f"  Warning: chart generation failed: {e}")


def main():
    parser = argparse.ArgumentParser(description="SIMSIV — Social Simulation")
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--years", type=int, default=None)
    parser.add_argument("--population", type=int, default=None)
    parser.add_argument("--config", type=str, default=None, help="YAML config file")
    parser.add_argument("--output-dir", type=str, default=None)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    # Load config
    if args.config:
        config = Config.load(Path(args.config))
    else:
        config = Config()

    if args.seed is not None:
        config.seed = args.seed
    if args.years is not None:
        config.years = args.years
    if args.population is not None:
        config.population_size = args.population

    # Output directory
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path("outputs/runs") / f"{ts}_seed{config.seed}"

    print("=" * 60)
    print(f"  SIMSIV | Pop={config.population_size} | Years={config.years} | Seed={config.seed}")
    print(f"  Mating: {config.mating_system} | Law: {config.law_strength}")
    print(f"  Output: {output_dir}")
    print("=" * 60)

    # Run
    sim = Simulation(config)
    callback = None if args.quiet else print_progress
    sim.run(callback=callback)

    # Save
    save_outputs(sim, output_dir)

    print("=" * 60)
    print(f"  DONE | Final pop: {sim.society.population_size()}")
    if sim.society.equilibrium_flagged:
        print(f"  Equilibrium reached at year {sim.society.equilibrium_year}")
    print(f"  Output saved to: {output_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()
