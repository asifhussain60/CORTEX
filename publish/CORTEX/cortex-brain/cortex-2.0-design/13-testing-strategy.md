# CORTEX 2.0 Testing Strategy

**Document:** 13-testing-strategy.md  
**Version:** 2.0.0-alpha  
**Date:** 2025-11-07

---

## 🎯 Goals

Establish a pragmatic, automated testing strategy that:
- Guarantees core stability during the 2.0 transition
- Validates new systems (plugins, self-review, maintenance, incremental creation)
- Provides fast feedback locally and in CI
- Detects regressions in performance and rule compliance
- Is easy to extend as new plugins/features are added

---

## 🧪 Test Taxonomy

| Layer | Focus | Examples |
|------|------|---------|
| Unit | Pure logic, small scope | token estimation, chunk splitting, path resolution |
| Component | Single module with I/O | self-review engine, maintenance engine, plugin registry |
| Integration | Subsystem interactions | conversation cycle with retrieval + write guards |
| Contract | External boundaries | plugin hook interface expectations, CLI contracts |
| Migration | Schema/app evolution | idempotent migrations, backfill, rollback checks |
| E2E (Selective) | Critical flows | create doc → validate → index update; nightly ops |
| Performance | Latency and throughput | Tier 1/2 query time, maintenance speedup |

---

## ✅ Coverage Targets

- Unit: 90%+ for core utilities and safety-critical code (path resolver, boundary guard)
- Component: 80%+ across new engines (self-review, maintenance, incremental creation)
- Integration: Must-cover for conversation workflow happy path + 2 edge cases
- Migration: 100% of migration scripts executed in CI dry-run
- Performance: Baseline measurements recorded, fail if >20% regression

---

## 🧩 Frameworks & Tooling

- Python: pytest + pytest-cov
- DB: SQLite in-memory and on-disk temp DBs
- Snapshots: approvals-based tests for health reports and schedules
- CLI: click/argparse simulations (if applicable) or subprocess smoke
- Lint/type: ruff/mypy (optional stage depending on repo config)

---

## 🧱 Test Data & Fixtures

- Tier DB fixtures: minimal schema + seed data for conversations, patterns, archives
- Config fixtures: baseline `cortex.config.json` + variations (Windows/Linux paths)
- Plugin registry stubs: minimal viable plugin set with deterministic outputs
- Large document generator: deterministic 800–1200 line doc content for chunking tests

---

## 🔬 Unit Tests (Examples)

- IncrementalCreationEngine
  - chunk boundaries around headers/code fences
  - resume logic with partial progress
  - validators: markdown/python/json quick checks
- SelfReviewEngine
  - scoring math for category weights
  - recommendations with issue mixes
- DB Maintenance
  - fragmentation calculation from PRAGMA values
  - operation selection under thresholds
- Path Resolver / Boundary Guard
  - relative → absolute mapping across OS
  - allow/deny decisions with rule references

---

## 🧱 Component Tests (Examples)

- Self-review end-to-end (mocked DB metrics):
  - produce HealthReport, group issues, recommendations non-empty
  - auto-fix path only triggers safe categories
- Maintenance end-to-end on temp DB:
  - write 1000 dummy rows, delete half → VACUUM reclaims space
  - ANALYZE updates stats age; REINDEX reduces query time threshold
- Incremental creation end-to-end:
  - write 1000-line markdown in chunks, validate structure, resume after simulated failure

---

## 🔗 Integration Tests (Conversation Workflow)

Scenario: user continues a session that triggers retrieval + document generation.

Asserts:
- Context injected only from allowed tiers/paths
- Boundary guard denies out-of-scope writes (captured event)
- Document generated via incremental engine and validated
- Index updated afterward (status row changes)

Edge cases:
- Tier 1 near capacity → archival plan produced before write
- Length limit exceeded simulation → chunking fallback engages

---

## 🧱 Migration Tests

- Apply all migration SQL against pristine test DBs → success
- Re-apply idempotently → no errors
- Backfill inserts expected seed rows (plugins, baseline health report)
- Rollback simulation: create new rows, restore pre-migration snapshot → DB equals baseline

---

## ⚙️ Performance Tests (Lightweight, CI-Friendly)

- Tier 1 query under 50–100ms on sample DB
- Tier 2 FTS search under 150–200ms on seeded index
- Maintenance speedup: query_time_before / after ≥ 1.2× on synthetic workload
- Incremental creation throughput: ≥ 10 chunks/minute on local CI runner

Fail CI if regression >20% from stored baselines; update baselines via explicit approval.

---

## 🧭 Rule Compliance Tests

- Validate critical rules (e.g., Brain Protector) via explicit violation attempts
- Ensure on_before_write / on_after_write hooks capture and block disallowed writes
- Confirm path resolver never emits absolute hard-coded platform-specific paths in code under test

---

## 🛠️ CI Pipeline Sketch

Stages:
1) Lint / Typecheck (optional)
2) Unit + Component (parallelizable)
3) DB Migration Dry-Run (all scripts)
4) Integration: conversation workflow + incremental doc
5) Performance smoke + baseline compare
6) Artifact publish: coverage XML/HTML + health report snapshot

Cache `.pytest_cache` and fixture DBs for speed.

---

## 🧪 Example Test Snippets

```python
# tests/unit/test_incremental_creation.py
from pathlib import Path
from src.utils.incremental_creation import IncrementalCreationEngine, FileValidator

def test_chunking_and_resume(tmp_path: Path):
    content = "\n".join(["# Title"] + [f"Line {i}" for i in range(1, 1001)])
    file_path = tmp_path / "big.md"
    engine = IncrementalCreationEngine(file_path)

    # First pass: stop mid-way by simulating failure after a few chunks
    ok = engine.create_file_incrementally(content, FileValidator.validate_markdown)
    assert ok is True
    # Simulate resume (no-op because finished) just to ensure idempotency
    assert engine.resume_creation(content) is True
```

```python
# tests/component/test_self_review.py
from src.maintenance.self_review import SelfReviewEngine

def test_self_review_produces_report(mocks):
    engine = SelfReviewEngine(path_resolver=mocks.paths, db_connections=mocks.dbs, config=mocks.cfg)
    report = engine.run_comprehensive_review(auto_fix=False)
    assert 0.0 <= report.overall_score <= 1.0
    text = engine.generate_report(report)
    assert "CORTEX HEALTH REPORT" in text
```

---

## 📈 Reporting & Gates

- Quality Gates (CI):
  - Build: PASS required
  - Lint/Type: PASS or explicitly skipped (visible)
  - Tests: PASS 100%; flaky quarantined with explicit tag
  - Performance: PASS within threshold; otherwise require approval

Artifacts:
- coverage.xml + HTML
- health_report.txt snapshot from component test
- maintenance_metrics.json (optional)

---

## 🔄 Maintenance of Tests

- New plugin → add hook execution test + registry snapshot
- New table → add migration test + schema presence assertion
- New workflow → add integration scenario + metrics check

---

**Next:** 14-configuration-format.md (cortex.config.json v2.0 specification)
