# Specification Drift Experiment

Controlled experiment measuring coefficient drift across frontier LLMs.

## Conditions

| Condition | Source Code Visible? | Critic Role? | n per model |
|-----------|---------------------|-------------|-------------|
| A (blind) | No | No | 10 |
| B (source-informed) | Yes | No | 10 |
| Treatment (protocol) | Yes (full codebase) | Yes | 1 |

## Results Summary

| Condition | GPT-4o | Grok-3 | Claude+Critic |
|-----------|--------|--------|---------------|
| A (blind) | 97.8% drift | 100% drift | — |
| B (source) | ~0% drift (M1/M2) | ~0% drift (M1/M2) | — |
| Treatment | — | — | 0% drift |

## Files

- `run_condition_a.py` — Blind control runner
- `run_condition_b.py` — Source-informed control runner
- `../drift_analysis.py` — Statistical analysis + figure generation

## Requirements

Set environment variables before running:
```
export OPENAI_API_KEY=sk-...
export GROK_API_KEY=xai-...
```
