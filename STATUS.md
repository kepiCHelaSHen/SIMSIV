# SIMSIV — Current Status

Phase: V2 ACTIVE — Paper 1 under review at JASSS, v2 clan simulator complete, drift working paper in progress
Version: v2-working-paper-alpha (tagged)

## Publication Status

### Paper 1 (v1 band simulator)
- JASSS submission: **2026:81:1** (ref 6029) — under editorial review
  - Title: "SIMSIV: A Calibrated Agent-Based Framework for Studying Gene-Culture Coevolution in Pre-State Societies"
  - Tracking: https://www.epress.ac.uk/JASSS/webforms/submission.php?id=7800&article=6029
  - Editor: Flaminio Squazzoni
- bioRxiv: REJECTED (screening stage)
- Zenodo: DOI 10.5281/zenodo.19065475
- GitHub: https://github.com/kepiCHelaSHen/SIMSIV (public)

### Working Paper (v2 drift experiment)
- Title: "LLMs Generate from Priors, Not Specifications: Measuring Coefficient Drift in Scientific Code Generation"
- Status: Draft v5 complete, targeting EMNLP/ICML workshop or arxiv preprint
- Location: `docs/SIMSIV_V2_White_Paper.md`

## v2 Clan Simulator — COMPLETE
- 6,957 lines of v2-specific code across 14 files
- 4 milestones: cooperation, trade, coalition defence, multi-level selection
- 187 tests total (141 v2 + 22 v1 + 24 drift/convergence)
- 120 convergence runs (4 milestones × 30 seeds), all σ < 0.05
- Drift experiment: 3 conditions (A: blind, B: source-informed, C: protocol)

## v2 Key Files
- `models/clan/clan_base.py` — 712-line cooperation model (4 milestones)
- `models/clan/` — Band, ClanSociety, ClanConfig, ClanSimulation
- `engines/clan_base.py` — ClanEngine tick driver
- `engines/clan_trade.py` — Inter-band trade (Wiessner 1982)
- `engines/clan_raiding.py` — Bowles raiding + coalition defence
- `engines/clan_selection.py` — Between-group selection + Fst
- `experiments/drift_experiment/` — Controlled drift experiment scripts
- `experiments/drift_analysis.py` — Statistical analyses + figures
- `tests/test_milestone_battery.py` — 4-milestone × 30-seed convergence gate
- `docs/SIMSIV_V2_White_Paper.md` — Drift working paper
- `docs/figures/figure1_drift_scatter.png` — Hero figure

## Known v1 Issues (deferred — do NOT fix before JASSS review completes)
- engines/conflict.py getattr false defaults (lines 161, 197, 549)
- Missing bond_dissolved event on conflict-caused breaks
- rng.choice on object list (line 508-512)
- Hardcoded elder multiplier, coalition threshold

## Frozen Paper Coefficients (v2 specification)
These are the ground-truth values the Critic enforces:

| Parameter | Value | Source | Literature |
|-----------|-------|--------|-----------|
| empathy_coeff | 0.15 | resources.py:289 | de Waal (2008) |
| coop_norm_coeff | 0.10 | resources.py:292 | Boyd & Richerson (1985) |
| conformity_coeff | 0.30 | institutions.py:237 | Henrich (2004) |
| social_skill_coeff | 0.10 | clan_trade.py:330 | Wiessner (1982) |
| cohesion_bonus_coeff | 0.20 | clan_raiding.py:610 | Bowles (2006) |

Updated: 2026-03-21
