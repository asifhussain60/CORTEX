# CORTEX 2.0 Monitoring Dashboard

**Document:** 17-monitoring-dashboard.md  
**Version:** 2.0.0-alpha  
**Date:** 2025-11-07

---

## 🎯 Purpose

Provide a real-time, actionable view of CORTEX health and activity so issues are detected early, decisions are data-driven, and remediation is fast and safe.

Outcomes:
- Single snapshot of overall health with drill-downs
- Trends over time for key metrics (7-day, 30-day)
- Alerting on thresholds with clear next steps
- Zero manual scraping of logs or databases

---

## ❌ Pain Points in 1.0

- No single source of truth for health; info scattered across tests, logs, and databases
- Manual validation; problems discovered reactively
- No thresholds or alerts; hard to know what “normal” looks like
- Siloed metrics (performance vs rules vs knowledge growth)

---

## ✅ 2.0 Solution Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                         Dashboard System                         │
├──────────────────────────────────────────────────────────────────┤
│ Snapshot Generator (CLI/Plugin)                                  │
│  • Aggregates metrics from tiers, self-review, tests, git        │
│  • Produces JSON snapshot + Markdown summary                     │
│  • Writes to corpus-callosum (history + latest)                  │
├───────────────────┬───────────────────────────┬──────────────────┤
│ Collectors        │ Metrics Store             │ Presentation      │
│ • SelfReview      │ • JSONL history           │ • MkDocs page     │
│ • Dev Context     │ • Latest snapshot JSON    │ • CLI summary     │
│ • Event Stream    │ • Rolling windows (7/30d) │ • (Future) Web UI │
└───────────────────┴───────────────────────────┴──────────────────┘
```

Key design choices:
- Files-first storage (JSON/JSONL) in `cortex-brain/corpus-callosum/`
- Leverage Self-Review Engine (07) as a primary signal
- Start with MkDocs + CLI; optional web UI later
- Strict thresholds with clear severities and actions

---

## 📦 Data Sources

- Self-Review Engine (07): overall and category scores, issues, recommendations
- Tier 1 (conversation): counts, freshness, FIFO proximity
- Tier 2 (knowledge graph): growth, confidence distribution, decay
- Tier 3 (development context): churn, hotspots, velocity trends
- Event Stream (Tier 4): backlog size, processing cadence
- Tests/CI: pass/fail, flaky rate, coverage
- Git: commit velocity, change size, co-modification hotspots

---

## 🧮 Metrics Taxonomy

Categories and example metrics (each with target, warn, critical):

1) Overall Health
- overall_score (0–1 from Self-Review)
- overall_status (excellent/good/fair/poor/critical)

2) Performance
- tier1_query_ms (target ≤ 50ms, warn > 50ms, critical > 100ms)
- tier2_fts_ms (target ≤ 150ms, warn > 150ms, critical > 300ms)
- agent_latency_ms (p95 for key agents)

3) Tests & Quality
- tests_total, tests_passing, tests_failing (critical if > 0 failing)
- coverage (target 100%, warn < 90%)
- flaky_tests_rate (warn > 5%)

4) Storage & Maintenance
- db_fragmentation_pct (warn > 20%, critical > 30%)
- event_backlog (warn > 50, critical > 100)
- tier1_conversation_count (info at ≥ 18/20)

5) Knowledge & Governance
- patterns_total, low_confidence_patterns
- rule_compliance_passed / total_rules (critical if Tier 0 fails)
- protector_challenges_last_7d

6) Development Context
- commit_velocity_7d, avg_commit_size
- hotspots_top5 (file churn list)

---

## 🧩 Widgets & Views

- Health Header: traffic light + overall score + last updated
- Category Cards: Database, Performance, Tests, Storage, Rules
- Trends: sparklines for tier1/tier2 times, coverage, backlog
- Alerts Feed: threshold violations with severity and action
- Hotspots: top N risky files/components with guidance
- Knowledge Growth: patterns added/decayed, confidence histogram

---

## 🚨 Alerts & Thresholds

Severity model and default thresholds (configurable in `cortex.config.json`):

- Critical
  - tests_failing > 0
  - rule_violation where rule.critical = true
  - tier2_fts_ms > 300
  - db_fragmentation_pct > 30

- High
  - tier1_query_ms > 100
  - tier2_fts_ms > 150
  - event_backlog > 100

- Medium
  - coverage < 90%
  - old_logs > 50 (90d)
  - low_confidence_patterns > threshold

- Info
  - tier1_conversation_count ≥ 18
  - protector_challenges_last_7d = 0 (consider review cadence)

Actions tie back to Self-Review auto-fix hooks (VACUUM, ANALYZE, rebuild FTS, archive logs).

---

## 🔌 Plugin Integration

Hook points (aligned with 02-plugin-system):
- metrics_collect: plugins can contribute domain metrics
- dashboard_snapshot: finalize/augment snapshot before publish
- dashboard_publish: push snapshot to destinations (MkDocs page, file, webhook)

Plugins must emit schema-compliant JSON fragments; core merges and validates.

---

## 🗃️ Storage Layout

- `cortex-brain/corpus-callosum/dashboard-snapshot.json` (latest)
- `cortex-brain/corpus-callosum/metrics-history.jsonl` (append-only history)
- `cortex-brain/corpus-callosum/efficiency-history.jsonl` (existing perf history)

Snapshot shape (abridged):
```json
{
  "generated_at": "2025-11-07T12:34:56Z",
  "overall": { "status": "good", "score": 0.87 },
  "categories": {
    "database": 0.92,
    "performance": 0.82,
    "rules": 1.0,
    "tests": 1.0,
    "storage": 0.95
  },
  "metrics": { "tier1_query_ms": 25, "tier2_fts_ms": 95, "event_backlog": 23 },
  "issues": [ { "severity": "medium", "title": "Stale statistics" } ],
  "alerts": [ { "severity": "high", "metric": "tier2_fts_ms", "value": 190 } ],
  "recommendations": [ "Rebuild FTS5 index" ]
}
```

---

## 🧰 CLI & Automation

Commands (initial design):
- `python scripts/cortex-dashboard.py --snapshot` → writes latest snapshot JSON + Markdown
- `python scripts/cortex-dashboard.py --history --days 7` → appends metrics to history
- `python scripts/cortex-dashboard.py --open` → opens MkDocs dashboard page

Scheduling:
- Daily snapshot at 02:00 with auto-fix allowed via Self-Review (07)
- Weekly deep trend report (adds 30-day visuals)

---

## 🔒 Security & Privacy

- No secrets or PII in metrics; redact paths/content where needed
- File-level ACLs inherit repo permissions; no external calls by default
- Plugin payloads validated; unknown fields ignored, unsafe fields blocked

---

## ⚡ Performance Budget

- Snapshot generation ≤ 2s on typical repo
- Metrics collection overhead ≤ 500ms during normal operation
- History write is append-only and O(1) per run

---

## 🚀 Implementation Phases

Phase 1: Minimal Snapshot (MVP)
- Use Self-Review Engine outputs to generate `dashboard-snapshot.json`
- Render MkDocs page with health header, category cards, alerts list

Phase 2: History & Trends
- Append metrics to `metrics-history.jsonl`
- Add 7/30-day sparklines and deltas

Phase 3: Alerts & Actions
- Threshold config in `cortex.config.json`
- Alert classification + recommended fixes
- Optional notifications (stdout, file webhook)

Phase 4: Optional Web UI
- Lightweight local web view reusing snapshot JSON
- Live auto-refresh (file watcher)

---

## ✅ Acceptance Criteria

- Snapshot file generated with overall score and 5 category scores
- MkDocs page shows health, alerts, and at least 3 trends
- Zero failing tests is enforced as critical; dashboard reflects this
- Thresholds configurable; changing them affects alert classification
- History grows with daily runs; trends reflect last 7/30 days

---

## 🔗 Related

- 07-self-review-system.md (primary signal source)
- 10-agent-workflows.md (metrics producers/consumers)
- 18-performance-optimization.md (follow-up tuning work)
- 14-configuration-format.md (thresholds, scheduling)
