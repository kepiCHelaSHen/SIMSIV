# Deep Dive 23: Intelligence Feedback Loop Audit

## Audit Findings

### Where intelligence_proxy affects outcomes:
1. **Resources**: competitive weight (0.25 factor) — primary income driver
2. **Resources**: tool production (0.5 factor) — DD21 tool generation
3. **Resources**: storage efficiency (DD10) — wealth preservation
4. **Conflict**: combat power (0.05 weight) — minor combat factor
5. **Mating**: indirectly via mate_value (resources → mate attractiveness)
6. **Gossip**: not directly; EI is the gossip trait, not intelligence

### Feedback loop confirmed (mild):
Intelligence → more resources → better survival/mate value → more offspring
→ children with higher intelligence (h²=0.65, highest of all traits)

Key amplifiers: h²=0.65 is the highest heritability, AND intelligence feeds
into resource acquisition which feeds into mate value. Double compounding.

### Experimental results (5 seeds, 200 pop, 100yr):
- Intelligence drift: +0.015 to +0.106 (avg +0.050)
- Cooperation drift: -0.024 to +0.065 (avg +0.010)
- Aggression drift: -0.036 to +0.006 (avg -0.010)

Intelligence rises 5x faster than cooperation on average. Seed 0 shows
+0.106 in 100yr (would extrapolate to ~0.18 over 200yr, exceeding threshold).

### Fix applied: Option A — Diminishing returns
In resource competitive weight:
- Before: `intelligence * 0.25`
- After: `min(intelligence_proxy ** 0.7, 0.8) * 0.25`

Effect: Intelligence still matters significantly, but returns flatten above ~0.7.
An agent with intelligence 0.9 gets the same benefit as one with 0.82.
This prevents the extreme tail from compounding indefinitely.

### Other loops checked:
- **Cooperation**: rises slower than intelligence, self-limiting (sharing costs resources)
- **Prestige**: decay rate (1%/yr) prevents runaway accumulation — confirmed working
- **Health/longevity**: rises very slowly (h²=0.25), not a concern
