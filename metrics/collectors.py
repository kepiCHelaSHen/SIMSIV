"""
Metrics collector — records per-tick stats for analysis and visualization.
"""

from __future__ import annotations
import numpy as np
import pandas as pd
from models.agent import Agent, Sex, HERITABLE_TRAITS


def _gini(values: list[float]) -> float:
    """Compute Gini coefficient. 0 = perfect equality, 1 = perfect inequality."""
    if not values or len(values) < 2:
        return 0.0
    arr = np.array(sorted(values), dtype=float)
    if arr.sum() == 0:
        return 0.0
    n = len(arr)
    index = np.arange(1, n + 1)
    return float((2 * (index * arr).sum() / (n * arr.sum())) - (n + 1) / n)


class MetricsCollector:
    def __init__(self):
        self.rows: list[dict] = []

    def collect(self, society, year: int) -> dict:
        living = society.get_living()
        pop = len(living)

        if pop == 0:
            row = {"year": year, "population": 0}
            self.rows.append(row)
            return row

        males = [a for a in living if a.sex == Sex.MALE]
        females = [a for a in living if a.sex == Sex.FEMALE]

        # Count tick events
        births = sum(1 for e in society.tick_events if e.get("type") == "birth")
        deaths = sum(1 for e in society.tick_events if e.get("type") == "death")
        infant_deaths = sum(1 for e in society.tick_events if e.get("type") == "infant_death")
        conflicts = sum(1 for e in society.tick_events if e.get("type") == "conflict")
        bonds_formed = sum(1 for e in society.tick_events if e.get("type") == "pair_bond_formed")
        bonds_dissolved = sum(1 for e in society.tick_events if e.get("type") == "bond_dissolved")

        # Avg lifespan: mean age at death for agents who died this tick
        deaths_this_tick = [e for e in society.tick_events if e.get("type") == "death"]
        lifespan_this_tick = []
        for e in deaths_this_tick:
            for aid in e.get("agent_ids", []):
                a = society.get_by_id(aid)
                if a and a.year_of_death == year:
                    lifespan_this_tick.append(a.age)
        avg_lifespan_this_tick = float(np.mean(lifespan_this_tick)) if lifespan_this_tick else 0.0

        # Resources
        resources = [a.current_resources for a in living]
        statuses = [a.current_status for a in living]

        # Reproductive skew — gini of offspring count among adults
        offspring_counts = [len(a.offspring_ids) for a in living if a.age >= 15]

        # Unmated percentages
        unmated_males = sum(1 for m in males if not m.is_bonded and m.age >= 15)
        unmated_females = sum(1 for f in females if not f.is_bonded and f.age >= 15)
        adult_males = max(1, sum(1 for m in males if m.age >= 15))
        adult_females = max(1, sum(1 for f in females if f.age >= 15))

        # Elite reproductive advantage (top 10% vs bottom 10%)
        if offspring_counts and len(offspring_counts) >= 10:
            sorted_oc = sorted(offspring_counts)
            n = len(sorted_oc)
            bottom_10 = sorted_oc[:max(1, n // 10)]
            top_10 = sorted_oc[-max(1, n // 10):]
            avg_bottom = np.mean(bottom_10) or 0.01
            avg_top = np.mean(top_10)
            elite_advantage = float(avg_top / avg_bottom) if avg_bottom > 0 else 0.0
        else:
            elite_advantage = 1.0

        # Child survival rate
        child_survival = 0.0
        if births + infant_deaths > 0:
            child_survival = births / (births + infant_deaths)

        # Pair bond stability
        bonded = sum(1 for a in living if a.is_bonded)
        bonded_pct = bonded / pop if pop > 0 else 0

        # Average health and age
        avg_health = float(np.mean([a.health for a in living]))
        avg_age = float(np.mean([a.age for a in living]))

        # Average traits
        avg_aggression = float(np.mean([a.aggression_propensity for a in living]))
        avg_cooperation = float(np.mean([a.cooperation_propensity for a in living]))

        # Derived rates
        violence_rate = conflicts / pop if pop > 0 else 0

        # ── Infidelity / bond metrics ──────────────────────────────
        epc_events = sum(1 for e in society.tick_events if e.get("type") == "epc_occurred")
        epc_detected = sum(1 for e in society.tick_events if e.get("type") == "epc_detected")
        bonded_females_count = sum(1 for f in females if f.is_bonded and f.age >= 15)
        infidelity_rate = epc_events / max(1, bonded_females_count)

        bonded_males_list = [m for m in males if m.is_bonded]
        paternity_uncertainty_avg = (
            1.0 - float(np.mean([m.paternity_confidence for m in bonded_males_list]))
            if bonded_males_list else 0.0
        )

        all_strengths = []
        for a in living:
            all_strengths.extend(a.pair_bond_strengths.values())
        avg_bond_strength = float(np.mean(all_strengths)) if all_strengths else 0.0

        mating_contests = sum(1 for e in society.tick_events if e.get("type") == "mating_contest")

        # ── DD02: Resource distribution metrics ───────────────────────
        total_resources = sum(a.current_resources for a in living)
        if total_resources > 0 and pop >= 10:
            sorted_res = sorted([a.current_resources for a in living], reverse=True)
            top_10_n = max(1, pop // 10)
            resource_top10_share = sum(sorted_res[:top_10_n]) / total_resources
        else:
            resource_top10_share = 0.0

        # Cooperation network size: avg trusted allies per agent
        network_sizes = []
        for a in living:
            count = sum(1 for trust in a.reputation_ledger.values() if trust > 0.5)
            network_sizes.append(count)
        cooperation_network_size = float(np.mean(network_sizes)) if network_sizes else 0.0

        resource_transfer_events = sum(
            1 for e in society.tick_events if e.get("type") == "resource_transfers")

        # ── DD03: Conflict deep dive metrics ─────────────────────────
        flee_events = sum(1 for e in society.tick_events if e.get("type") == "flee")
        violence_deaths = sum(
            1 for e in society.tick_events
            if e.get("type") == "death" and "violence" in e.get("description", ""))
        punishment_events = sum(
            1 for e in society.tick_events if e.get("type") == "punishment")
        agents_in_cooldown = sum(1 for a in living if a.conflict_cooldown > 0)

        # ── DD04: Per-trait evolution tracking ─────────────────────────
        trait_means = {}
        trait_stds = {}
        for trait in HERITABLE_TRAITS:
            vals = [getattr(a, trait) for a in living]
            trait_means[trait] = float(np.mean(vals))
            trait_stds[trait] = float(np.std(vals))

        # Max generation in living population
        max_generation = max((a.generation for a in living), default=0)

        # ── DD06: Household metrics ──────────────────────────────────
        childhood_deaths = sum(
            1 for e in society.tick_events if e.get("type") == "childhood_death")
        orphan_deaths = sum(
            1 for e in society.tick_events
            if e.get("type") == "childhood_death" and "orphan=True" in e.get("description", ""))

        children = [a for a in living if a.age <= 15]
        children_count = len(children)
        orphan_count = 0
        for child in children:
            has_parent = False
            for pid in child.parent_ids:
                if pid is not None:
                    p = society.get_by_id(pid)
                    if p and p.alive:
                        has_parent = True
                        break
            if not has_parent:
                orphan_count += 1

        fertile_females = [f for f in females if f.age >= 15 and f.age <= 45]
        avg_lifetime_births = (
            float(np.mean([f.lifetime_births for f in fertile_females]))
            if fertile_females else 0.0)

        avg_maternal_health = (
            float(np.mean([f.health for f in females if f.lifetime_births > 0]))
            if any(f.lifetime_births > 0 for f in females) else 0.0)

        # ── DD05: Institutional metrics ──────────────────────────────
        current_law_strength = getattr(society.config, 'law_strength', 0.0)
        current_vps = getattr(society.config, 'violence_punishment_strength', 0.0)
        current_property_rights = getattr(society.config, 'property_rights_strength', 0.0)
        inheritance_events = sum(
            1 for e in society.tick_events if e.get("type") == "inheritance")
        norm_violations = sum(
            1 for e in society.tick_events if e.get("type") == "norm_violation")
        institutions_emerged = sum(
            1 for e in society.tick_events if e.get("type") == "institution_emerged")

        # ── DD13: Demographic metrics ────────────────────────────────
        male_deaths = sum(1 for e in society.tick_events
                          if e.get("type") == "death"
                          and any((a := society.get_by_id(aid)) and a and a.sex == Sex.MALE
                                  for aid in e.get("agent_ids", [])))
        female_deaths = sum(1 for e in society.tick_events
                            if e.get("type") == "death"
                            and any((a := society.get_by_id(aid)) and a and a.sex == Sex.FEMALE
                                    for aid in e.get("agent_ids", [])))
        childbirth_deaths = sum(1 for e in society.tick_events
                                if e.get("type") == "childbirth_death")
        # Sex ratio in reproductive age
        repro_males = sum(1 for m in males if 20 <= m.age <= 40)
        repro_females = sum(1 for f in females if 20 <= f.age <= 40)
        sex_ratio_reproductive = (
            repro_females / max(1, repro_males) * 100 if repro_males > 0 else 0.0)

        # ── DD12: Signaling metrics ──────────────────────────────────
        signal_events = [e for e in society.tick_events
                         if e.get("type") == "signaling_summary"]
        bluff_attempts = 0
        bluff_detections = 0
        for e in signal_events:
            desc = e.get("description", "")
            # Parse "X bluffs, Y detected" from description
            import re
            m = re.search(r'(\d+) bluffs', desc)
            if m:
                bluff_attempts += int(m.group(1))
            m = re.search(r'(\d+) detected', desc)
            if m:
                bluff_detections += int(m.group(1))

        # ── DD11: Coalition metrics ──────────────────────────────────
        coalition_defenses = sum(
            1 for e in society.tick_events if e.get("type") == "coalition_defense")
        third_party_punishments = sum(
            1 for e in society.tick_events if e.get("type") == "third_party_punishment")
        ostracism_thresh = getattr(society.config, 'ostracism_reputation_threshold', 0.25)
        ostracized_count = sum(1 for a in living if a.reputation < ostracism_thresh)

        # ── DD10: Seasonal metrics ───────────────────────────────────
        seasonal_phase = society.environment.seasonal_phase

        # ── DD09: Epidemic metrics ───────────────────────────────────
        epidemic_active = 1 if society.environment.in_epidemic else 0
        epidemic_deaths = sum(
            1 for e in society.tick_events if e.get("type") == "epidemic_death")

        # ── DD08: Prestige vs Dominance metrics ─────────────────────
        prestige_vals = [a.prestige_score for a in living]
        dominance_vals = [a.dominance_score for a in living]
        avg_prestige = float(np.mean(prestige_vals))
        avg_dominance = float(np.mean(dominance_vals))
        prestige_gini = _gini(prestige_vals)
        dominance_gini = _gini(dominance_vals)
        # Correlation between prestige and dominance
        if pop >= 10:
            prestige_dominance_corr = float(np.corrcoef(prestige_vals, dominance_vals)[0, 1])
        else:
            prestige_dominance_corr = 0.0

        # ── DD07: Reputation/social network metrics ────────────────
        gossip_events = sum(
            1 for e in society.tick_events if e.get("type") == "gossip_summary")

        # Average ledger size (social connections)
        ledger_sizes = [len(a.reputation_ledger) for a in living]
        avg_ledger_size = float(np.mean(ledger_sizes)) if ledger_sizes else 0.0

        # Trust distribution: avg trust, distrust fraction
        all_trust_vals = []
        for a in living:
            all_trust_vals.extend(a.reputation_ledger.values())
        avg_trust = float(np.mean(all_trust_vals)) if all_trust_vals else 0.5
        distrust_fraction = (
            sum(1 for v in all_trust_vals if v < 0.4) / len(all_trust_vals)
            if all_trust_vals else 0.0)

        avg_reputation = float(np.mean([a.reputation for a in living]))

        # ── DD14: Faction metrics ──────────────────────────────────
        # Count factions from living agents' faction_ids (always current)
        faction_member_counts = {}
        for a in living:
            if a.faction_id is not None:
                faction_member_counts[a.faction_id] = (
                    faction_member_counts.get(a.faction_id, 0) + 1)
        faction_count = len(faction_member_counts)
        largest_faction_size = (
            max(faction_member_counts.values()) if faction_member_counts else 0)
        faction_sizes = [float(c) for c in faction_member_counts.values()]
        faction_size_gini = _gini(faction_sizes) if len(faction_sizes) >= 2 else 0.0

        # Faction stability: average age of active factions
        factions = getattr(society, 'factions', {})
        active_factions = {fid: f for fid, f in factions.items()
                          if fid in faction_member_counts}
        faction_stability = (
            float(np.mean([year - f['formed_year']
                           for f in active_factions.values()]))
            if active_factions else 0.0)

        # Inter-faction conflict rate
        inter_faction = 0
        for e in society.tick_events:
            if e.get("type") != "conflict":
                continue
            outcome = e.get("outcome", {})
            agg = society.get_by_id(outcome.get("aggressor", -1))
            tgt = society.get_by_id(outcome.get("target", -1))
            if (agg and tgt
                    and agg.faction_id is not None
                    and tgt.faction_id is not None
                    and agg.faction_id != tgt.faction_id):
                inter_faction += 1
        inter_faction_conflict_rate = (
            inter_faction / max(1, conflicts) if conflicts > 0 else 0.0)

        factionless_count = sum(1 for a in living if a.faction_id is None)
        factionless_fraction = factionless_count / pop if pop > 0 else 1.0

        # ── Composite indices ──────────────────────────────────────
        # Mating inequality index: Gini of offspring count among adult males
        male_offspring = [len(m.offspring_ids) for m in males if m.age >= 15]
        mating_inequality = _gini(male_offspring) if male_offspring else 0.0

        # Population growth rate (from previous tick)
        if self.rows:
            prev_pop = self.rows[-1].get("population", pop)
            pop_growth_rate = (pop - prev_pop) / max(1, prev_pop)
        else:
            pop_growth_rate = 0.0

        # Civilization Stability Index (CSI): 0=collapse, 1=stable
        # WARNING: constructed index, not a real measurement
        csi = ((1 - min(1.0, violence_rate * 5)) * 0.3
               + child_survival * 0.25
               + (1 - _gini(resources)) * 0.2
               + bonded_pct * 0.15
               + max(0.0, min(1.0, 0.5 + pop_growth_rate * 10)) * 0.1)

        # Social Cohesion Index (SCI): cooperation + bonds + peace
        sci = (avg_cooperation * 0.4
               + bonded_pct * 0.35
               + (1 - min(1.0, violence_rate * 5)) * 0.25)

        row = {
            "year": year,
            "population": pop,
            "males": len(males),
            "females": len(females),
            "births": births,
            "deaths": deaths,
            "infant_deaths": infant_deaths,
            "conflicts": conflicts,
            "bonds_formed": bonds_formed,
            "bonds_dissolved": bonds_dissolved,
            "resource_gini": _gini(resources),
            "status_gini": _gini(statuses),
            "reproductive_skew": _gini(offspring_counts) if offspring_counts else 0.0,
            "mating_inequality": mating_inequality,
            "unmated_male_pct": unmated_males / adult_males,
            "unmated_female_pct": unmated_females / adult_females,
            "elite_repro_advantage": elite_advantage,
            "child_survival_rate": child_survival,
            "pair_bonded_pct": bonded_pct,
            "violence_rate": violence_rate,
            "pop_growth_rate": pop_growth_rate,
            "avg_resources": float(np.mean(resources)),
            "avg_status": float(np.mean(statuses)),
            "avg_health": avg_health,
            "avg_age": avg_age,
            "avg_aggression": avg_aggression,
            "avg_cooperation": avg_cooperation,
            "avg_lifespan": avg_lifespan_this_tick,
            "infidelity_rate": infidelity_rate,
            "epc_detected": epc_detected,
            "paternity_uncertainty": paternity_uncertainty_avg,
            "avg_bond_strength": avg_bond_strength,
            "mating_contests": mating_contests,
            "resource_top10_share": resource_top10_share,
            "cooperation_network_size": cooperation_network_size,
            "resource_transfers": resource_transfer_events,
            "flee_events": flee_events,
            "violence_deaths": violence_deaths,
            "punishment_events": punishment_events,
            "agents_in_cooldown": agents_in_cooldown,
            "scarcity": society.environment.get_scarcity_level(),
            "civilization_stability": csi,
            "social_cohesion": sci,
            "max_generation": max_generation,
            "avg_attractiveness": trait_means.get("attractiveness_base", 0.5),
            "avg_status_drive": trait_means.get("status_drive", 0.5),
            "avg_risk_tolerance": trait_means.get("risk_tolerance", 0.5),
            "avg_jealousy": trait_means.get("jealousy_sensitivity", 0.5),
            "avg_fertility": trait_means.get("fertility_base", 0.5),
            "avg_intelligence": trait_means.get("intelligence_proxy", 0.5),
            "trait_std_aggression": trait_stds.get("aggression_propensity", 0.0),
            "trait_std_cooperation": trait_stds.get("cooperation_propensity", 0.0),
            "law_strength": current_law_strength,
            "violence_punishment": current_vps,
            "property_rights": current_property_rights,
            "inheritance_events": inheritance_events,
            "norm_violations": norm_violations,
            "institutions_emerged": institutions_emerged,
            "childhood_deaths": childhood_deaths,
            "orphan_deaths": orphan_deaths,
            "children_count": children_count,
            "orphan_count": orphan_count,
            "avg_lifetime_births": avg_lifetime_births,
            "avg_maternal_health": avg_maternal_health,
            "gossip_events": gossip_events,
            "avg_ledger_size": avg_ledger_size,
            "avg_trust": avg_trust,
            "distrust_fraction": distrust_fraction,
            "avg_reputation": avg_reputation,
            "avg_prestige": avg_prestige,
            "avg_dominance": avg_dominance,
            "prestige_gini": prestige_gini,
            "dominance_gini": dominance_gini,
            "prestige_dominance_corr": prestige_dominance_corr,
            "epidemic_active": epidemic_active,
            "epidemic_deaths": epidemic_deaths,
            "seasonal_phase": seasonal_phase,
            "coalition_defenses": coalition_defenses,
            "third_party_punishments": third_party_punishments,
            "ostracized_count": ostracized_count,
            "bluff_attempts": bluff_attempts,
            "bluff_detections": bluff_detections,
            "male_deaths": male_deaths,
            "female_deaths": female_deaths,
            "childbirth_deaths": childbirth_deaths,
            "sex_ratio_reproductive": sex_ratio_reproductive,
            "faction_count": faction_count,
            "largest_faction_size": largest_faction_size,
            "faction_size_gini": faction_size_gini,
            "faction_stability": faction_stability,
            "inter_faction_conflict_rate": inter_faction_conflict_rate,
            "factionless_fraction": factionless_fraction,
            # DD17: Medical/pathology metrics
            "active_conditions_count": sum(
                len(a.active_conditions) for a in living),
            "avg_trauma_score": float(np.mean(
                [a.trauma_score for a in living])) if living else 0.0,
            "cardiovascular_prevalence": sum(
                1 for a in living if "cardiovascular" in a.active_conditions) / max(1, pop),
            "mental_illness_prevalence": sum(
                1 for a in living if "mental_illness" in a.active_conditions) / max(1, pop),
            "autoimmune_prevalence": sum(
                1 for a in living if "autoimmune" in a.active_conditions) / max(1, pop),
            "metabolic_prevalence": sum(
                1 for a in living if "metabolic" in a.active_conditions) / max(1, pop),
            "degenerative_prevalence": sum(
                1 for a in living if "degenerative" in a.active_conditions) / max(1, pop),
            # DD16: Developmental biology metrics
            "maturation_events": sum(
                1 for e in society.tick_events if e.get("type") == "maturation"),
            "childhood_trauma_rate": (
                sum(1 for a in children if a.childhood_trauma) / max(1, children_count)
                if children_count > 0 else 0.0),
            "avg_childhood_resource_quality": (
                float(np.mean([a.childhood_resource_quality for a in children]))
                if children else 0.5),
            # DD15: Extended genomics trait means
            "avg_longevity_genes": trait_means.get("longevity_genes", 0.5),
            "avg_disease_resistance": trait_means.get("disease_resistance", 0.5),
            "avg_physical_robustness": trait_means.get("physical_robustness", 0.5),
            "avg_pain_tolerance": trait_means.get("pain_tolerance", 0.5),
            "avg_mental_health": trait_means.get("mental_health_baseline", 0.5),
            "avg_emotional_intelligence": trait_means.get("emotional_intelligence", 0.5),
            "avg_impulse_control": trait_means.get("impulse_control", 0.5),
            "avg_novelty_seeking": trait_means.get("novelty_seeking", 0.5),
            "avg_empathy": trait_means.get("empathy_capacity", 0.5),
            "avg_conformity": trait_means.get("conformity_bias", 0.5),
            "avg_dominance_drive": trait_means.get("dominance_drive", 0.5),
            "avg_maternal_investment": trait_means.get("maternal_investment", 0.5),
            "avg_sexual_maturation": trait_means.get("sexual_maturation_rate", 0.5),
        }
        self.rows.append(row)
        return row

    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(self.rows)

    def save_csv(self, path):
        self.to_dataframe().to_csv(path, index=False)

    def check_equilibrium(self, config) -> bool:
        """Check if key metrics have stabilized."""
        w = config.equilibrium_window
        if len(self.rows) < w + 1:
            return False

        recent = self.rows[-w:]
        keys = ["population", "resource_gini", "violence_rate", "reproductive_skew"]

        for key in keys:
            values = [r.get(key, 0) for r in recent]
            if not values or values[0] == 0:
                continue
            max_change = max(abs(v - values[0]) / (abs(values[0]) + 0.01) for v in values[1:])
            if max_change > config.equilibrium_threshold:
                return False
        return True
