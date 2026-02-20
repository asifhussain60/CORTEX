# Learning System — Pattern Capture & Feedback Loop

---
title: Learning System Pattern Capture — How CORTEX Gets Smarter Over Time
type: explanation
audience: [Software Developers, Product Owners]
last_verified: 2026-02-18
source_of_truth: cortex/learning/ + cortex_intelligence/memory/ + cortex/orchestrators/health/intelligence.py
format: diátaxis-explanation
voice: third-person-blended
feature: Production (Iteration 71 + Iteration 96)
order: 2
---

> **Purpose:** Explains exactly what the learning system captures, how it stores patterns, and how those patterns improve future CORTEX behaviour — without requiring manual configuration.

---

## What Is Captured?

The learning system captures **operational patterns** — not user data or business logic. Every observation is derived from git history and orchestrator telemetry:

| Pattern Type | Source | Retention |
|---|---|---|
| File change frequency | Git commit history (48h window) | 7 days |
| Test failure patterns | pytest output telemetry | 30 days |
| Orchestrator routing decisions | Audit log | 90 days |
| LENS analysis results | SQLite cache | 48h TTL |
| Governance violation types | `governance.db` | 365 days |
| Performance timings | OpenTelemetry spans | 30 days |

---

## The 48-Hour Learning Window

The primary learning window is the most recent **48 hours** of git activity. This gives the system:

- **Recency bias** — recent changes matter more than old ones
- **Bounded memory** — no unbounded growth in pattern storage
- **Fast adaptation** — new patterns emerge within 2 commit cycles

```
Now
  │
  │◄── 48h window ───────────────────────────────────────────────►│
  │
  ▼ (most influential)                          (least influential)
Recent commits                               Commits 47-48h ago
  │                                                 │
  ▼                                                 ▼
Pattern weight: 1.0                     Pattern weight: 0.02
```

---

## Pattern Learner Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     PATTERN LEARNER                              │
│                                                                  │
│  Input: Git commits + Orchestrator telemetry                     │
│                                                                  │
│  ┌────────────────┐    ┌─────────────────┐    ┌──────────────┐  │
│  │ Git History    │    │ Frequency        │    │  Confidence  │  │
│  │ Extractor      │───►│ Scorer          │───►│  Calculator  │  │
│  └────────────────┘    └─────────────────┘    └──────┬───────┘  │
│                                                       │          │
│                                                       ▼          │
│                                              ┌────────────────┐  │
│                                              │ Pattern Store  │  │
│                                              │ (SQLite cache) │  │
│                                              └────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Impact: Before vs After Learning

### Health Check False Positives (Iteration 96)

The HealthOrchestrator learned to distinguish genuine problems from noisy false positives by observing 48h of activity:

| Metric | Before Learning | After Learning |
|--------|----------------|----------------|
| False positive rate | 85.2% | <5% |
| Unnecessary alerts | ~17 per hour | <1 per hour |
| Developer interruptions | High | Near-zero |

**How it works:** The learner detects files that change frequently (hot paths). Health warnings about "uncommitted changes" in hot-path files during active development are suppressed — they are expected, not problems.

### Vacuum Safety (Iteration 96)

The VacuumOrchestrator learned which files are "critically active" before proposing deletion:

- Files with commits in the last 48h → never suggested for deletion
- Files unchanged for 90+ days with no cross-references → safe deletion candidates
- Files unchanged for 90+ days but imported elsewhere → flagged, not auto-deleted

This eliminated all accidental deletion incidents (previously ~2 per month during vacuum runs).

---

## Smart Caching

The learning system maintains a file-based cache that reduces redundant analysis:

```
First analysis (cold):
  File hash → compute LENS analysis → store in cache (SQLite)
  Time: ~450ms

Subsequent analyses (warm):
  File hash → cache hit → return stored result
  Time: ~12ms (73% reduction)

Cache invalidation:
  File changes → hash changes → cache miss → recompute
  Stale entries → TTL expiry → automatic cleanup
```

---

## Knowledge Base Tier Precedence

Learned patterns feed into the knowledge base, which applies a three-tier precedence hierarchy:

```
┌─────────────────────────────────────────────┐
│  Tier 0: Universal Best Practices            │  (lowest precedence)
│  45+ YAML files in cortex-registry/          │
│  e.g., "always add type hints"               │
└─────────────────────────────────────────────┘
                    overridden by
┌─────────────────────────────────────────────┐
│  Tier 1: Domain Patterns                     │
│  Framework-specific rules                    │
│  e.g., "Django views use class-based pattern"│
└─────────────────────────────────────────────┘
                    overridden by
┌─────────────────────────────────────────────┐
│  Company Patterns (highest precedence)       │
│  Repository-specific learned patterns        │
│  e.g., "this team uses dataclasses, not dicts│
└─────────────────────────────────────────────┘
```

Higher-precedence patterns override lower-precedence ones. This means CORTEX adapts to how **your specific team** works, not just generic best practice.

---

## What the Learning System Does NOT Do

- ❌ It does not store user requests or conversation history beyond the active session
- ❌ It does not learn from production data (development environment only)
- ❌ It does not modify CORE governance rules (immutable — CORE-035)
- ❌ It does not self-modify orchestrator logic
- ❌ It does not share patterns between separate CORTEX installations

---

## Related Documents

- **[Learning Overview](./01-overview.md)** — Architecture and lifecycle
- **[Intelligence Layer](../01-capabilities/04-intelligence-layer.md)** — Iteration 96 learning-enhanced orchestrators
- **[LENS Caching](../02-lens/05-caching.md)** — Cache layer detail
- **[Infrastructure Overview](../05-infrastructure/01-overview.md)** — Storage backends

---

*Last verified: 2026-02-18 | Feature: 71 + 96 | Source: cortex/learning/ + cortex_intelligence/memory/*
