"""
Condition A: Blind control — no source code in prompt.

Queries GPT-4o and Grok-3 with plain coding prompts (no spec, no source code).
Measures coefficient drift rates across 10 trials per model per task.

Requires environment variables:
  OPENAI_API_KEY
  GROK_API_KEY

Usage: python -m experiments.drift_experiment.run_condition_a
"""

import json
import os
import re
import time
import requests
from datetime import datetime
from collections import defaultdict

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
GROK_API_KEY = os.environ.get("GROK_API_KEY", "")

N_TRIALS = 10
TEMPERATURE = 0.7

GROUND_TRUTH = {
    "empathy_coeff": 0.15,
    "coop_norm_coeff": 0.10,
    "social_skill_coeff": 0.10,
    "cohesion_bonus_coeff": 0.20,
    "n_prosocial_traits": 4,
}

CODEBASE_CONTEXT = """You are writing code for SIMSIV, an agent-based simulation of human social evolution.

Key agent traits (all float 0-1, heritable):
- cooperation_propensity (h²=0.40): prosocial behaviour
- empathy_capacity (h²=0.35): extends altruism beyond kin
- conformity_bias (h²=0.35): adoption of group norms
- group_loyalty (h²=0.42): coalition participation
- outgroup_tolerance (h²=0.40): inter-group openness
- social_skill (0-1): negotiation ability
- aggression_propensity, risk_tolerance, etc. (35 traits total)

Non-heritable state:
- cooperation_norm: float [-1, +1], culturally transmitted belief
- reputation_ledger: dict[agent_id -> trust float]
- life_stage: CHILDHOOD/YOUTH/PRIME/MATURE/ELDER
- age: int (beliefs initialised at age 15)

The simulation has bands (groups of ~30-50 agents) that interact via trade and raiding.
"""

PROMPTS = {
    "M1": "Write a Python function `compute_individual_cooperation(agent)` that computes an agent's effective cooperation score. Combine: 1. cooperation_propensity (primary genetic driver) 2. An empathy modulation factor 3. A cultural cooperation norm modulation (if adult, age >= 15). Return a float. Include specific numerical coefficients. Write ONLY the function with comments.",
    "M2": "Write a Python function `compute_band_trade_openness(band)` for inter-band trade capacity. Consider outgroup_tolerance as the primary gate and social_skill as a negotiation bonus. Return a dict with trade_willingness, mean_social_skill, trade_capacity. Include specific numerical coefficients. Write ONLY the function.",
    "M3": "Write a Python function `compute_band_defence_capacity(band)` for coalition defence (Bowles 2006). group_loyalty drives join probability, cooperation_propensity provides cohesion bonus. Return a dict with mean_group_loyalty, mean_coalition_probability, coalition_cohesion_bonus, defence_capacity. Include specific coefficients. Write ONLY the function.",
    "M4": "Write a Python function `compute_band_selection_potential(band)` for multi-level selection (Price equation). Identify which of the 35 heritable traits are relevant to prosocial selection, compute mean and variance. Return prosocial_composite and within_variance_composite. Explain your trait choice. Write ONLY the function.",
}


def extract_coefficients(text, milestone):
    """Extract numerical coefficients via regex. See drift_analysis.py for details."""
    result = {}
    if milestone == "M1":
        for pat in [r'empathy[_\w]*\s*[\*\xd7]\s*(0\.\d+)', r'(0\.\d+)\s*[\*\xd7]\s*(?:agent\.)?empathy', r'empathy.*?=\s*(0\.\d+)', r'(0\.\d+).*empathy']:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                result["empathy_coeff"] = float(m.group(1))
                break
        for pat in [r'(?:cooperation_norm|coop.*norm|norm)[_\w]*\s*[\*\xd7]\s*(0\.\d+)', r'(0\.\d+)\s*[\*\xd7]\s*(?:agent\.)?cooperation_norm', r'(?:norm|cultural).*?=?\s*(0\.\d+)', r'(0\.\d+).*(?:norm|cultural)']:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                result["coop_norm_coeff"] = float(m.group(1))
                break
    elif milestone == "M2":
        for pat in [r'social_skill[_\w]*\s*[\*\xd7]\s*(0\.\d+)', r'(0\.\d+)\s*[\*\xd7]\s*(?:agent\.)?social_skill', r'(?:skill|SKILL).*?(?:COEFF|bonus|weight).*?=\s*(0\.\d+)', r'(0\.\d+).*social.?skill']:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                result["social_skill_coeff"] = float(m.group(1))
                break
    elif milestone == "M3":
        for pat in [r'(?:cohesion|COHESION).*?(?:COEFF|bonus|weight).*?=\s*(0\.\d+)', r'cohesion.*?(0\.\d+)', r'(0\.\d+).*cohesion']:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                result["cohesion_bonus_coeff"] = float(m.group(1))
                break
    elif milestone == "M4":
        trait_names = ["cooperation_propensity", "group_loyalty", "outgroup_tolerance", "empathy_capacity", "conformity_bias", "social_skill", "aggression_propensity", "risk_tolerance", "status_drive", "dominance_drive", "novelty_seeking", "impulse_control", "conscientiousness", "future_orientation", "emotional_intelligence", "maternal_investment", "physical_strength", "physical_robustness"]
        found = [t for t in trait_names if t in text]
        result["n_prosocial_traits"] = len(found)
    return result


def query_model(api_url, api_key, model_id, prompt):
    try:
        r = requests.post(api_url, headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}, json={"model": model_id, "messages": [{"role": "user", "content": CODEBASE_CONTEXT + "\n\n" + prompt}], "max_tokens": 1200, "temperature": TEMPERATURE}, timeout=60)
        data = r.json()
        return data["choices"][0]["message"]["content"] if "choices" in data else f"ERROR: {json.dumps(data)[:200]}"
    except Exception as e:
        return f"ERROR: {e}"


def main():
    if not OPENAI_API_KEY or not GROK_API_KEY:
        print("Set OPENAI_API_KEY and GROK_API_KEY environment variables.")
        return

    models = [
        ("GPT-4o", "https://api.openai.com/v1/chat/completions", OPENAI_API_KEY, "gpt-4o"),
        ("Grok-3", "https://api.x.ai/v1/chat/completions", GROK_API_KEY, "grok-3"),
    ]

    for model_name, api_url, api_key, model_id in models:
        print(f"\n--- {model_name} ---")
        for milestone, prompt in PROMPTS.items():
            for trial in range(1, N_TRIALS + 1):
                print(f"  {milestone} t{trial}...", end=" ", flush=True)
                response = query_model(api_url, api_key, model_id, prompt)
                if response.startswith("ERROR"):
                    print("FAILED")
                    continue
                coeffs = extract_coefficients(response, milestone)
                print(coeffs)
                time.sleep(1.0)


if __name__ == "__main__":
    main()
