"""
V1 Stability Sweep — Phase 3 Adversarial Critic
Triple-Model Consensus (TMC) Protocol

Worker (Claude/native): Runs ±20% perturbation simulations
Auditor (GPT-4o): Reviews stability, calculates selection coefficient
Critic (Grok-3): Red-teams for model fractures

Gate: σ ≤ 0.030 per metric across conditions
"""
import os
import sys
import json
import time
import logging
from pathlib import Path
from dataclasses import dataclass, field

import numpy as np

# Load API keys from context-hacking
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

logging.basicConfig(level=logging.WARNING)
_log = logging.getLogger("stability_sweep")

# ── Tier-1 Claim-Critical Coefficients ────────────────────────────────────────

TIER1_COEFFICIENTS = {
    # Institutional suppression (conflict.py) — uses absolute perturbation since default=0
    "law_strength_base_mult": {
        "file": "engines/conflict.py", "line": 76,
        "param": "law_strength", "default": 0.0,
        "absolute_perturb": [0.0, 0.1, 0.2],  # test 0, 0.1, 0.2 law strength
        "note": "Institutional suppression — directly controls institution-gene claim",
    },
    # Institutional micro-gradient (hard floor detection)
    "law_strength_micro": {
        "file": "engines/institutions.py", "line": 114,
        "param": "law_strength", "default": 0.0,
        "absolute_perturb": [0.0, 0.01, 0.02],
        "note": "Micro-sweep: detect hard floor in violence suppression at low law_strength",
    },
    # Violence death chance (AutoSIM calibrated)
    "violence_death_chance": {
        "file": "config.py", "line": 91,
        "param": "violence_death_chance", "default": 0.115422,
        "note": "Keeley (1996) target 0.05-0.15; AutoSIM calibrated",
    },
    # Conflict base probability (AutoSIM calibrated)
    "conflict_base_probability": {
        "file": "config.py", "line": 86,
        "param": "conflict_base_probability", "default": 0.15,
        "note": "Drive overall violence rate",
    },
    # Pair bond dissolution (AutoSIM calibrated)
    "pair_bond_dissolution_rate": {
        "file": "config.py", "line": 78,
        "param": "pair_bond_dissolution_rate", "default": 0.02,
        "note": "Betzig (1989) target 0.10-0.30",
    },
    # Female choice strength (AutoSIM calibrated)
    "female_choice_strength": {
        "file": "config.py", "line": 82,
        "param": "female_choice_strength", "default": 0.339674,
        "note": "Betzig (2012) mating inequality target",
    },
    # Mortality base (AutoSIM calibrated)
    "mortality_base": {
        "file": "config.py", "line": 97,
        "param": "mortality_base", "default": 0.006212,
        "note": "Hassan (1981) pop growth target",
    },
    # Childhood mortality (AutoSIM calibrated)
    "childhood_mortality_annual": {
        "file": "config.py", "line": 98,
        "param": "childhood_mortality_annual", "default": 0.054119,
        "note": "Volk & Atkinson (2013) child survival target",
    },
    # Cooperation network bonus (AutoSIM calibrated)
    "cooperation_network_bonus": {
        "file": "config.py", "line": 74,
        "param": "cooperation_network_bonus", "default": 0.059346,
        "note": "Henrich et al. (2001) cooperation target",
    },
    # Aggression production penalty (AutoSIM calibrated)
    "aggression_production_penalty": {
        "file": "config.py", "line": 69,
        "param": "aggression_production_penalty", "default": 0.6,
        "note": "Archer (2009) aggression target",
    },
    # Epidemic lethality (AutoSIM calibrated)
    "epidemic_lethality_base": {
        "file": "config.py", "line": 101,
        "param": "epidemic_lethality_base", "default": 0.254318,
        "note": "Hassan (1981) pop growth target",
    },
}

# ── Calibration Metrics ───────────────────────────────────────────────────────

METRICS = [
    "resource_gini",
    "mating_inequality",
    "violence_death_fraction",
    "pop_growth_rate",
    "child_survival_rate",
    "avg_lifetime_births",
    "violence_rate",
    "avg_cooperation",
    "avg_aggression",
]


def run_simulation(seed: int, **overrides) -> dict:
    """Run a single simulation and return final metrics."""
    cfg = Config(years=100, population_size=200, seed=seed, **overrides)
    sim = Simulation(cfg)
    sim.run()

    rows = sim.metrics.rows
    if not rows:
        return {m: float("nan") for m in METRICS}

    last = rows[-1]
    result = {}
    for m in METRICS:
        if m == "violence_death_fraction":
            # Compute from raw counts
            vd = last.get("violence_deaths", 0)
            md = last.get("male_deaths", 0)
            result[m] = vd / md if md > 0 else 0.0
        else:
            result[m] = last.get(m, float("nan"))
    return result


def perturbation_sweep(
    param_name: str,
    default_value: float,
    n_seeds: int = 10,
    perturbation: float = 0.20,
    tier1_key: str = "",
) -> dict:
    """Run baseline, +20%, -20% conditions and compute cross-condition σ."""
    # Check for absolute perturbation override (for zero-default params)
    # Look up by tier1 dict key, not config param name
    spec = TIER1_COEFFICIENTS.get(tier1_key, {})
    if "absolute_perturb" in spec:
        vals = spec["absolute_perturb"]
        conditions = {"baseline": vals[0], "mid": vals[1], "high": vals[2]}
    else:
        conditions = {
            "baseline": default_value,
            "plus_20pct": default_value * (1.0 + perturbation),
            "minus_20pct": default_value * (1.0 - perturbation),
        }

    seeds = list(range(42, 42 + n_seeds))
    results = {}

    for cond_name, value in conditions.items():
        cond_results = []
        for seed in seeds:
            overrides = {param_name: value}
            metrics = run_simulation(seed, **overrides)
            cond_results.append(metrics)
        results[cond_name] = cond_results

    # Compute cross-condition σ for each metric
    stability = {}
    for m in METRICS:
        # Mean of each condition across seeds
        cond_means = []
        for cond_name in conditions:
            values = [r[m] for r in results[cond_name] if not np.isnan(r[m])]
            cond_means.append(np.mean(values) if values else float("nan"))

        # σ across the 3 condition means
        valid = [v for v in cond_means if not np.isnan(v)]
        sigma = float(np.std(valid)) if len(valid) >= 2 else float("nan")
        gate = "PASS" if sigma <= 0.030 else "FAIL"

        stability[m] = {
            "baseline_mean": round(cond_means[0], 6),
            "plus20_mean": round(cond_means[1], 6),
            "minus20_mean": round(cond_means[2], 6),
            "sigma": round(sigma, 6),
            "gate": gate,
        }

    return {
        "param": param_name,
        "default": default_value,
        "conditions": {k: round(v, 6) for k, v in conditions.items()},
        "n_seeds": n_seeds,
        "stability": stability,
    }


# ── TMC: External Model Audit ────────────────────────────────────────────────

def _call_openai(prompt: str, model: str = "gpt-4o") -> str:
    """Call OpenAI API (GPT-4o auditor)."""
    try:
        from openai import OpenAI
        client = OpenAI()  # uses OPENAI_API_KEY from env
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=600,
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"[OPENAI ERROR: {e}]"


def _call_xai(prompt: str, model: str = "grok-3") -> str:
    """Call xAI API (Grok-3 critic) via OpenAI-compatible endpoint."""
    try:
        from openai import OpenAI
        client = OpenAI(
            api_key=os.getenv("XAI_API_KEY"),
            base_url="https://api.x.ai/v1",
        )
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=600,
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"[XAI ERROR: {e}]"


def tmc_audit(sweep_result: dict) -> dict:
    """Run Triple-Model Consensus audit on a sweep result."""
    param = sweep_result["param"]
    stability = sweep_result["stability"]

    # Build audit prompt
    table_lines = [f"Parameter: {param} (default: {sweep_result['default']})"]
    table_lines.append(f"Perturbation: ±20% ({sweep_result['conditions']})")
    table_lines.append("")
    table_lines.append("| Metric | Baseline | +20% | -20% | σ | Gate |")
    table_lines.append("|--------|----------|------|------|---|------|")
    for m, s in stability.items():
        table_lines.append(
            f"| {m} | {s['baseline_mean']:.4f} | {s['plus20_mean']:.4f} | "
            f"{s['minus20_mean']:.4f} | {s['sigma']:.4f} | {s['gate']} |"
        )
    data_block = "\n".join(table_lines)

    auditor_prompt = (
        "You are a statistical auditor for an agent-based model of pre-state "
        "societies (SIMSIV). Review this perturbation sweep result.\n\n"
        f"{data_block}\n\n"
        "For each FAIL metric, assess:\n"
        "1. Is the sensitivity expected given the parameter's role?\n"
        "2. Does the direction of change make biological/social sense?\n"
        "3. Rate overall stability: STABLE / SENSITIVE / FRAGILE\n\n"
        "Reply with a JSON object: {\"verdict\": \"STABLE|SENSITIVE|FRAGILE\", "
        "\"failures\": [...], \"reasoning\": \"...\"}"
    )

    critic_prompt = (
        "You are an evolutionary biology red-team critic reviewing an ABM "
        "stability test. Your job: find model fractures.\n\n"
        f"{data_block}\n\n"
        "Check for:\n"
        "1. Population collapse risk (does ±20% cause extinction?)\n"
        "2. Non-linear responses (σ >> parameter change magnitude)\n"
        "3. Violated evolutionary constraints (cooperation going to 0 or 1)\n\n"
        "Reply with a JSON object: {\"verdict\": \"STABLE|FRACTURE_DETECTED\", "
        "\"fractures\": [...], \"reasoning\": \"...\"}"
    )

    # Dispatch to external models
    _log.info(f"TMC audit for {param}: calling GPT-4o...")
    auditor_response = _call_openai(auditor_prompt)
    _log.info(f"TMC audit for {param}: calling Grok-3...")
    critic_response = _call_xai(critic_prompt)

    # Claude (worker) verdict: pure σ gate
    failures = [m for m, s in stability.items() if s["gate"] == "FAIL"]
    claude_verdict = "STABLE" if len(failures) == 0 else "SENSITIVE"

    return {
        "param": param,
        "claude_worker": {"verdict": claude_verdict, "failures": failures},
        "gpt4o_auditor": auditor_response,
        "grok3_critic": critic_response,
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description="V1 Stability Sweep — Phase 3")
    parser.add_argument("--seeds", type=int, default=10, help="Seeds per condition")
    parser.add_argument("--tmc", action="store_true", help="Enable TMC external audit")
    parser.add_argument("--params", nargs="*", help="Specific params to test")
    args = parser.parse_args()

    params = args.params or list(TIER1_COEFFICIENTS.keys())
    results = []

    for name in params:
        if name not in TIER1_COEFFICIENTS:
            print(f"Unknown parameter: {name}")
            continue

        spec = TIER1_COEFFICIENTS[name]
        print(f"\n{'='*60}")
        print(f"SWEEPING: {name} (default={spec['default']})")
        print(f"  Note: {spec['note']}")
        print(f"  Seeds: {args.seeds} per condition")
        print(f"{'='*60}")

        t0 = time.time()
        result = perturbation_sweep(
            param_name=spec["param"],
            default_value=spec["default"],
            tier1_key=name,
            n_seeds=args.seeds,
        )
        elapsed = time.time() - t0

        # Print stability table
        print(f"\n  Completed in {elapsed:.1f}s")
        print(f"  {'Metric':<30} {'Baseline':>8} {'  +20%':>8} {'  -20%':>8} {'    σ':>8} {'Gate':>6}")
        print(f"  {'-'*30} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*6}")
        for m, s in result["stability"].items():
            print(
                f"  {m:<30} {s['baseline_mean']:>8.4f} {s['plus20_mean']:>8.4f} "
                f"{s['minus20_mean']:>8.4f} {s['sigma']:>8.4f} {s['gate']:>6}"
            )

        # TMC audit if enabled
        if args.tmc:
            print(f"\n  Dispatching TMC audit...")
            tmc = tmc_audit(result)
            result["tmc"] = tmc
            print(f"  Claude: {tmc['claude_worker']['verdict']}")
            print(f"  GPT-4o: {tmc['gpt4o_auditor'][:100]}...")
            print(f"  Grok-3: {tmc['grok3_critic'][:100]}...")

        results.append(result)

    # Write results
    out_path = Path("docs/v1_stability_report.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to {out_path}")

    # Summary
    total_tests = sum(len(r["stability"]) for r in results)
    total_fail = sum(
        1 for r in results for s in r["stability"].values() if s["gate"] == "FAIL"
    )
    print(f"\n{'='*60}")
    print(f"PHASE 3 SUMMARY: {total_tests - total_fail}/{total_tests} passed (σ ≤ 0.030)")
    print(f"Failures: {total_fail}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
