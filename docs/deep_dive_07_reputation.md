# SIMSIV — Deep Dive 07: Memory and Reputation

## Design Decisions

### A. Gossip and Information Spread
**Decision: IMPLEMENTED — sampling-based gossip through allies**
- Each tick, each agent has `gossip_rate` (10%) chance of sharing one trust entry
  with a randomly chosen ally (trust > cooperation_trust_threshold)
- Ally updates their ledger based on the shared opinion, weighted by how much
  they trust the gossiper: weight = (trust_of_gossiper - 0.3) * 0.5
- Gossip noise (`gossip_noise = 0.1`): information degrades with Gaussian noise
  (telephone game effect)
- O(n) per tick — no quadratic cost. Sampling ensures lightweight spread.
- NOT implemented: transitive trust (too complex), event-based gossip (redundant
  with bystander system from DD03)

### B. Reputation Decay and Dynamics
**Decision: IMPLEMENTED — slow decay toward neutral with persistence for extremes**
- `trust_decay_rate = 0.01`: all trust entries drift toward 0.5 each tick
- Extreme values decay slower: effective_decay = rate * (1 - distance_from_0.5 * 0.5)
  - Trust at 0.9: effective decay = 0.008/yr (takes ~50yr to reach 0.5)
  - Trust at 0.6: effective decay = 0.0095/yr (takes ~10yr to reach 0.5)
- This means deep trust/distrust persists while mild opinions fade
- Dead agents cleaned from ledgers to free slots for living connections

### C. Social Network Structure
**Decision: IMPLICIT — tracked via metrics, not explicit graph**
- avg_ledger_size metric tracks social connectivity
- cooperation_network_size already tracks ally count (DD02)
- Formal graph structure (clustering coefficient, path length) deferred —
  would require O(n²) computation for marginal insight
- Dunbar's number analog: ledger cap of 100 provides natural social bandwidth limit

### D. Trust Formation Pathways
**Decision: EXISTING PATHWAYS SUFFICIENT**
- Direct interaction (conflict, cooperation, mating) remains primary
- Kin trust (parent-child, siblings from DD06) bootstraps networks
- Gossip (DD07) enables indirect trust formation
- NOT implemented: homophily (similar traits → faster trust), shared enemies,
  proximity-based trust — these add complexity without clear emergent payoff

### E. Reputation and Mate Value
**Decision: REPUTATION NOW COMPUTED FROM AGGREGATE TRUST**
- `reputation_from_ledger = True`: public reputation = weighted blend of
  how others see you (70%) + existing reputation (30%)
- This replaces the ad-hoc reputation updates scattered across engines
- Existing engine reputation updates still work (they affect individual trust
  entries, which then feed into aggregate reputation)
- Mate value still uses reputation field (10% weight) — no change needed

### F. Social Learning
**Decision: NOT IMPLEMENTED — deferred**
- Agents observing and copying successful strategies would require a strategy
  model and fitness visibility
- Conformity better handled in institutional engine (DD05 territory)
- Gossip provides some social learning indirectly (reputation spreads)

### G. Ledger Management
**Decision: DEAD AGENT CLEANUP + EXISTING EVICTION**
- Dead agent cleanup each tick frees slots for living connections
- Existing eviction (remove entry closest to 0.5) preserved
- Ledger cap configurable but default 100 (Dunbar-adjacent)

## Parameters Added
| Parameter | Default | Description |
|-----------|---------|-------------|
| gossip_enabled | True | Enable gossip/information spread |
| gossip_rate | 0.1 | Probability per agent per tick of gossiping |
| gossip_noise | 0.1 | Gaussian noise on shared trust values |
| trust_decay_rate | 0.01 | Annual decay rate toward neutral (0.5) |
| reputation_from_ledger | True | Compute reputation from aggregate trust |
| dead_agent_ledger_cleanup | True | Remove dead agents from ledgers |
| max_reputation_ledger_size | 100 | Configurable ledger cap |

## Metrics Added
| Metric | Description |
|--------|-------------|
| gossip_events | Count of gossip summary events per tick |
| avg_ledger_size | Mean reputation ledger entries per living agent |
| avg_trust | Mean trust value across all ledger entries |
| distrust_fraction | Fraction of trust entries below 0.4 |
| avg_reputation | Mean public reputation of living agents |

## Files Changed
- `engines/reputation.py` (NEW) — 4-phase reputation engine
- `simulation.py` — added reputation engine as phase 8 (before metrics)
- `config.py` — 7 DD07 parameters
- `metrics/collectors.py` — 5 DD07 metrics

## Validation Results (200 pop, 50yr, seed=42)
- Gossip active: ~1 summary event per tick (10% of pop gossips = ~20 individual shares)
- Avg ledger size: ~5 entries (dead cleanup keeping it lean)
- Avg trust: 0.596 (above neutral — kin trust and cooperation dominate)
- Distrust fraction: ~9% of entries
- Reputation: ~0.60 (now computed from aggregate trust, tracks avg_trust closely)
- Cooperation networks: 2.5 avg allies (slightly lower than pre-DD07 due to trust decay)
