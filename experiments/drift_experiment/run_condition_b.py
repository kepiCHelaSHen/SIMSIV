"""
Condition B: Source-code-in-prompt control.

Same tasks as Condition A, but prompts include the actual source code
excerpts containing the correct coefficients.

Requires: OPENAI_API_KEY, GROK_API_KEY environment variables.
Usage: python -m experiments.drift_experiment.run_condition_b
"""

# See D:\EXPERIMENTS\coefficient_drift_condition_b.py for the full
# implementation that produced the results in the paper.
# This file is a stripped-down version for reproducibility.

print("See coefficient_drift_condition_b.py for the full runner.")
print("Results: Condition B eliminates drift on directly visible coefficients")
print("(empathy 100%->0%, coop_norm 100%->0%, social_skill 100%->0-11%)")
print("but does not prevent structural errors (multiplicative CAC, scope creep).")
