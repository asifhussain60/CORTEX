---
name: cortex-rca
description: 'CORTEX Root Cause Analysis skill. Use when: running /rca, investigating failure patterns, querying prevention rules, analyzing recurring bugs, or using cortex_learning MCP tool with op=rca. Covers 4 RCA methodologies (Five-Whys, Fishbone, Fault-Tree, Causal-Chain), prevention rules, and URS learning signals.'
argument-hint: 'rca <failure> | rca query <pattern> | rca list'
---

# CORTEX RCA Memory Engine

**4 root cause analysis methodologies — Phase 87 (121 GREEN tests)**

---

## Commands

```bash
/rca <failure-description>   # Full RCA analysis
/rca query <pattern>          # Query prevention rules for a pattern
/rca list                     # List recent RCA analyses
```

---

## 4 Methodologies

| Methodology | When Auto-Selected | Depth |
|---|---|---|
| **Five-Whys** | TECHNOLOGY category | 5 iterative "why" levels |
| **Fishbone (Ishikawa)** | PROCESS / PEOPLE category | 6 branches: Methods, Machines, Materials, Measurements, Manpower, Environment |
| **Fault-Tree** | Complex multi-factor failures | Boolean logic gates (AND/OR) |
| **Causal-Chain** | DATA category | Event → cause → effect sequence |

**Auto-selection:** Category → methodology mapping:
- TECHNOLOGY → Five-Whys
- PROCESS / PEOPLE → Fishbone
- DATA → Causal-Chain
- Complex / mixed → Fault-Tree

---

## MCP Tool: `cortex_learning`

| Operation | Sub-Action | Purpose |
|---|---|---|
| `op=rca` | `rca_action=analyze` | Run full RCA on a failure |
| `op=rca` | `rca_action=query` | Check prevention rules for a pattern |
| `op=rca` | `rca_action=list` | List recent analyses |
| `op=history` | — | Surface prior failure patterns (confidence ≥0.4) |
| `op=emit` | `signal_type=MILD_REWARD` | Record success signal |
| `op=emit` | `signal_type=MILD_PUNISHMENT` | Record failure signal |

---

## Prevention Rules

Each completed RCA generates a `PreventionRule`:
- Default level: ADVISORY
- Stored in: `.cortex-runtime/rca/rca_store.db`
- Auto-queried before code-modifying operations (PLIP-001)

---

## URS (Unified Reinforcement Signal)

Closed-loop learning across all orchestrators:

| Signal | When |
|---|---|
| `MILD_REWARD` | Code change succeeds, tests pass |
| `MILD_PUNISHMENT` | Code change fails, tests break |
| `decay` | Reduce confidence of stale patterns |
| `promote` | Elevate proven patterns to ENFORCED |
| `quarantine` | Isolate suspicious patterns |

---

## Entry Points

| Component | Location |
|---|---|
| RCA Engine | `cortex/intelligence/learning/rca_engine.py` |
| RCA Store | `cortex/intelligence/learning/rca_store.py` |
| MCP Tool | `cortex/mcp/tools/learning_tool.py` |
