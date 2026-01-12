---
agent: agent
---
# CORTEX6: Cortex Search-and-Fix (Day-Zero Brittleness & Risk Review)

You are reviewing the CORTEX6 plan and implementation for production-readiness under real load, partial failure, and ongoing change. Your job is to search across the entire repo/landscape and identify brittleness, breakage points, and material risks—then recommend the simplest robust improvements with minimal impact and no scope creep.

## Scope & Inputs (repo conventions)
- Primary plan/design source: `cortex-brain/cx6-plan/**`
- Execution/update anchor file (must be used to maintain a single evolving plan): `#file:cortex-exec.prompt.md`
- Search across the entire CORTEX6 architecture + infrastructure landscape (code, IaC, CI/CD, runtime configs, docs, ADRs, scripts, manifests, charts, pipelines, and operational artifacts)
- **CORTEX-specific paths:**
  - State files: `cortex-brain/tier1/tracking/progress-tracker.json`, `cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml`
  - Governance: `cortex-brain/tier0/governance/core-rules.yaml` (23 SKULL rules)
  - Database: `cortex-brain/state/planning.db` (SQLite, single-writer)
  - Orchestrators: `src/orchestrators/` (master, planning, TDD, ADO, cleanup, etc.)
  - Tests: `tests/` (pytest-based, evidence source for tracker)
  - Scripts: `scripts/` (sync, validation, consolidation utilities)

## Operating Rules
- **No code snippets or configuration blocks** in the response.
- Focus on **issues that materially impact**: correctness, reliability, security, deployability, scalability, operability.
- Assume production constraints: **partial failures**, latency spikes, retries, deployment rollouts, config drift, dependency upgrades, and noisy neighbors.
- Challenge assumptions and defaults; look for execution-time brittleness and hidden edge cases.
- **Minimal-impact changes only**: do not introduce new subsystems, major rewrites, or architecture expansions. Prefer small, robust fixes.
- Prioritize by real-world impact and likelihood; explain how failures manifest at runtime.

## Repeatable “Tool” Behavior (avoid file bloat)
- Do **NOT** create new files each run.
- Update/extend the existing plan via **one canonical record** inside `#file:cortex-exec.prompt.md`.
- If an entry already exists, update it (status, severity, evidence paths, recommendation, owner, lastReviewed) rather than duplicating.
- Use the structured format below for all updates.

## Required Output Format
1) A concise summary (paragraphs + bullets), broken into sections.
2) A single YAML (preferred) or JSON “update payload” that can be pasted into `#file:cortex-exec.prompt.md` to incrementally maintain the plan.
3) The payload must be **idempotent**: same findings should map to the same stable IDs and update in-place.

---

# Step-by-step Instructions

## 1) Repo-wide discovery
Search for and map:
- Service boundaries, runtime components, and data flows (sync/async paths).
- Deployments, environments, and config sources (env vars, config files, secrets stores).
- External dependencies, contracts, and versioning strategy.
- State stores (DBs, caches, queues), schema/migration mechanisms.
- CI/CD pipelines, release strategy, and rollback mechanisms.
- Observability stack: logging, metrics, tracing, dashboards, alerts.
- Security controls: authN/Z, secrets, key management, RBAC/IAM, network policies.

## 2) Brittleness analysis categories (must cover all)
For each category, identify concrete risks and where they live (file paths / modules / components):
- **Correctness & edge cases** (validation, invariants, fallbacks)
  - YAML encoding corruption (AC-INDEX.yaml, core-rules.yaml with bytes 0x8f, 0x9d)
  - Pattern matching failures (PatternRouter 100% regex, no LLM fallback)
  - Test evidence gaps (marking "implemented" without passing tests)
- **State, concurrency & ordering hazards** (races, dedupe, idempotency)
  - TodoManager in-memory state loss (no persistence to progress-tracker.json)
  - SQLite database single-writer contention (planning.db corruption risk)
  - Progress tracker vs plan viewer sync drift (manual sync required)
- **Integration & contract risks** (APIs/events, backward compatibility)
  - Governance-to-Todo pipeline breaking on rule schema changes
  - AC-INDEX.yaml schema evolution without version migration
  - MasterOrchestrator registry contract changes breaking orchestrators
- **Reliability under partial failure** (timeouts, retries, circuit breaking, backpressure)
  - DoR/DoD validation hard stop with no retry (phase blocking)
  - Governance violation blocking entire plan (single T0 SKULL violation)
  - No rollback on failed phases (partial artifacts left in workspace)
- **Data integrity & lifecycle** (migrations, corruption handling, replay, retention)
  - No database backup before write operations (planning.db)
  - YAML corruption with no repair mechanism
  - Evidence bundle generation without hash validation
- **Security & secrets** (auth boundaries, token handling, rotation, least privilege)
  - Audit logs may expose sensitive data in context fields
  - No secrets redaction in governance evaluation output
  - Planning database readable by all processes (no encryption)
- **Dependency/versioning traps** (pins, transitive risk, breaking upgrades)
  - Python 3.13 encoding behavior differences (cp1252 vs UTF-8 defaults)
  - pytest version assumptions in test discovery
  - YAML library version breaking changes in safe_load
- **Deployability & environment drift** (config parity, feature flags, rollouts)
  - Hardcoded paths in scripts (D:\PROJECTS\CORTEX assumptions)
  - No environment detection (dev vs staging vs prod)
  - Config scattered across YAML files with no central validation
- **Scalability & performance** (hot paths, fan-out, resource limits)
  - Knowledge graph queries without caching (repeated workspace scans)
  - Audit log JSONL files growing unbounded (no rotation)
  - Plan viewer data sync on every AC-ID (no debouncing)
- **Operability & observability blind spots** (SLOs, alerts, runbooks, on-call)
  - No health check endpoints for orchestrators
  - Audit logs not queryable by correlation ID at runtime
  - Phase completion percentage calculated incorrectly (no evidence validation)
  - No smoke tests for critical paths (governance merge, pattern routing)

## 3) Prioritize and explain runtime manifestation
For each issue:
- **Severity**: Critical / High / Medium / Low
- **Impact**: what breaks (data loss, outage, security exposure, silent corruption, etc.)
- **Likelihood**: based on production realities (load, change, partial failure)
- **Manifestation**: what operators/users will observe at runtime
- **Detection gaps**: why it may go unnoticed (missing signals)
- **Minimal robust recommendation**: simplest change within existing architecture
- **Verification**: smallest test/experiment to validate the fix

## 4) Stable finding IDs (idempotency)
Assign each finding a stable ID based on: `<area>-<component>-<risk>-<short-hash>`
- Example: `reliability-planning-phase-blocking-a1b2`
- Use component names from CORTEX: `governance`, `planning`, `tdd`, `ado`, `audit`, `todo`, `master`, `routing`
- Risk categories: `corruption`, `blocking`, `drift`, `race`, `leak`, `exposure`, `timeout`, `retry`
Ensure the same underlying issue maps to the same ID on reruns.

**CORTEX-specific ID patterns:**
- Encoding: `data-yaml-encoding-corruption-{hash}`
- State: `state-tracker-sync-drift-{hash}`
- Governance: `governance-tier0-blocking-{hash}`
- Testing: `testing-evidence-gap-{hash}`
- Orchestration: `orchestration-{orchestrator}-{issue}-{hash}`

---

# Response Requirements (what to produce)

## A) Clear summary with sections (no code/config snippets)
Use these sections:
- **Executive Summary** (2-3 paragraphs: current state, critical risks, recommended actions)
- **Top Risks (Critical/High)** (must-fix before production)
- **Reliability & Failure Modes** (retry, timeout, rollback, circuit breaking)
- **Data & Concurrency Hazards** (corruption, races, sync drift)
- **Security & Secrets** (exposure, least privilege, encryption)
- **Deployability & Environment Drift** (config parity, portability)
- **Scalability & Performance** (hot paths, resource limits)
- **Observability & Operability** (blind spots, debugging, on-call)
- **Testing & Evidence Gaps** (missing tests, false positives, coverage)
- **Quick Wins** (minimal-impact, high leverage, <1 day implementation)
- **Assumptions Challenged** (what defaults seem risky, hidden dependencies)

Each issue should be bullets with: 
- **ID** (stable identifier)
- **Severity** (Critical/High/Medium/Low)
- **What fails** (runtime manifestation)
- **Where** (file paths, components)
- **Impact** (data loss, outage, corruption, exposure)
- **Minimal fix** (smallest change, no architecture expansion)
- **Verification** (test/experiment to validate)

**CORTEX-specific analysis focus:**
- Evidence-based completion tracking (test passing vs metadata claims)
- Governance rule precedence conflicts (T0 vs T1 vs T2 vs T3)
- Orchestrator lifecycle state machine gaps (7 states: PENDING → COMPLETE)
- Progress tracker sync failures (tracker → plan-viewer-data.json → HTML)
- AC-ID validation chain breaks (AC-INDEX → progress-tracker → evidence bundles)

## B) Update payload for `#file:cortex-exec.prompt.md`
Produce a single YAML (or JSON) object with:
- `runMeta`: 
  - `date` (ISO 8601)
  - `reviewer` (agent name or human)
  - `repoRef` (branch/commit hash)
  - `scopePaths` (list of directories searched)
  - `cortexVersion` (e.g., "6.0.0")
  - `phaseContext` (current phase from progress-tracker.json)
- `findings[]`: array of finding objects keyed by `id`
- `findings[].fields`:
  - `title` (concise, actionable)
  - `category` (from brittleness analysis categories)
  - `severity` (Critical/High/Medium/Low)
  - `impact` (data loss/outage/corruption/exposure/degradation)
  - `likelihood` (High/Medium/Low based on production realities)
  - `evidencePaths` (list of repo paths where issue manifests)
  - `manifestation` (what operators/users observe at runtime)
  - `detectionGap` (why it may go unnoticed)
  - `recommendation` (minimal-impact fix, no architecture expansion)
  - `verification` (smallest test/experiment to validate fix)
  - `owner` (component owner if inferable; else `TBD`)
  - `status` (`open|in_progress|mitigated|accepted_risk|wont_fix`)
  - `lastReviewed` (ISO 8601 date)
  - `relatedACIDs` (list of AC-IDs impacted, if applicable)
  - `regressionRisk` (None/Low/Medium/High - risk of fix breaking existing behavior)
- `rollup`: 
  - `countBySeverity` (Critical/High/Medium/Low counts)
  - `countByCategory` (category name → count)
  - `countByStatus` (status → count)
  - `topRiskAreas` (list of components with most Critical/High findings)
- `nextActions[]`: ordered list of day-zero implementation tasks
  - `action` (description)
  - `priority` (P0/P1/P2/P3)
  - `estimatedEffort` (hours or days)
  - `blockedBy` (list of finding IDs that must be resolved first)
  - `owner` (if inferable)

**CORTEX-specific payload fields:**
- `phaseImpact`: Which phases are blocked by this finding (Phase 1/2/3/4)
- `governanceTier`: Which governance tier is affected (T0/T1/T2/T3)
- `testEvidence`: Whether finding has test reproduction (true/false)
- `automationPotential`: Can fix be automated via script (true/false)

The payload must be designed so it can be merged into the existing record without creating duplicates:
- If `id` exists, treat this as an update (refresh fields, add to history if status changed)
- If new, append to findings array
- Sort findings by severity (Critical → High → Medium → Low) and then by category

Do not include any code/config blocks; only descriptive text.

---

# CORTEX-Specific Review Checklist

Before completing the analysis, verify these CORTEX 6-specific patterns:

## Evidence-Based Tracking
- [ ] Check if completion percentages match actual test pass rates
- [ ] Verify AC-INDEX.yaml entries have corresponding test files
- [ ] Validate progress-tracker.json claims backed by test evidence
- [ ] Confirm plan-viewer-data.json synced from tracker (not hardcoded)

## Governance Integrity
- [ ] All 23 SKULL rules (CORE-001 to CORE-023) load without encoding errors
- [ ] Tier precedence enforced (T0 > T1 > T2 > T3) in GovernanceMerger
- [ ] Governance violations block execution with clear diagnostic messages
- [ ] Rule conflicts logged to audit trail with resolution strategy

## Orchestrator Lifecycle
- [ ] All orchestrators implement 7-state lifecycle (PENDING → IN_PROGRESS → COMPLETE/FAILED/BLOCKED)
- [ ] TodoManager tasks persist across orchestrator restarts
- [ ] Phase DoR/DoD validation blocks execution correctly
- [ ] Failed phases trigger rollback or leave clean partial state

## State Management
- [ ] progress-tracker.json is single source of truth for completion
- [ ] No dual-write patterns (tracker and plan-viewer-data.json)
- [ ] SQLite databases use WAL mode for concurrency
- [ ] State files have backup/recovery mechanisms

## Pattern Routing
- [ ] PatternRouter regex patterns cover 90%+ of intents
- [ ] Unmatched patterns logged for pattern expansion
- [ ] LLM fallback enabled when confidence < threshold
- [ ] Intent classification failures don't crash MasterOrchestrator

## Test Infrastructure
- [ ] pytest discovery finds all test_*.py files
- [ ] Test evidence validator runs without false positives
- [ ] Coverage reports accurately reflect implemented code
- [ ] Smoke tests validate critical paths (governance, routing, execution)

## Audit Trail
- [ ] All operations log with correlation IDs
- [ ] Audit logs queryable by AC-ID, phase, orchestrator
- [ ] Hash chain integrity validated on startup
- [ ] JSONL files rotate before exceeding size limits

## Data Sync Pipeline
- [ ] sync_plan_viewer_data.py runs after every tracker update
- [ ] plan-viewer.html loads data from plan-viewer-data.json only
- [ ] No hardcoded status values in HTML templates
- [ ] Dashboard refresh detects stale data automatically

---

# Begin the analysis now
Search across `cortex-brain/cx6-plan/**` and the corresponding implementation and infrastructure. Produce the summary and the idempotent update payload.
