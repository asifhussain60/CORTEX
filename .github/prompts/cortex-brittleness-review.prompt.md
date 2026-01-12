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

## 4) Generate AC-IDs (not finding IDs)
All brittleness findings MUST be converted to proper AC-IDs that flow through the governance-to-todo pipeline.

**AC-ID Format:** `AC-<CATEGORY>-<NNN>`
- Examples: `AC-BRITTLE-001`, `AC-RISK-005`, `AC-DEBT-012`
- Categories: `BRITTLE` (brittleness/fragility), `RISK` (runtime failure risks), `DEBT` (technical debt), `SEC` (security issues)
- Sequential numbering: Query AC-INDEX.yaml to find highest existing number in category, increment by 1

**Category Mapping (brittleness type → AC category):**
- Encoding/corruption/data integrity → `AC-BRITTLE-*`
- Concurrency/race conditions/state loss → `AC-RISK-*`
- Missing tests/validation gaps/observability → `AC-DEBT-*`
- Security/secrets/exposure → `AC-SEC-*`
- Governance/blocking/hardcoded assumptions → `AC-RISK-*`

**Why AC-IDs (not finding IDs)?**
- Single tracking system (no parallel workflows outside governance)
- Flows through MasterOrchestrator → TodoManager → progress-tracker.json
- Test evidence required (CORE-019 TDD enforcement)
- Audit trail via EnterpriseAuditLogger
- Phase assignment and prioritization automatic

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
- **AC-ID** (generated identifier, e.g., AC-BRITTLE-015)
- **Title** (capability-focused, e.g., "YAML encoding repair mechanism")
- **Priority** (critical|high|medium|low)
- **What fails** (runtime manifestation)
- **Where** (file paths, components)
- **Risk if unfixed** (data loss, outage, corruption, exposure)
- **Implementation** (minimal-impact fix, no architecture expansion)
- **Verification** (test strategy to validate fix)
- **Phase** (which phase implements this: 1/2/3/4)

**CORTEX-specific analysis focus:**
- Evidence-based completion tracking (test passing vs metadata claims)
- Governance rule precedence conflicts (T0 vs T1 vs T2 vs T3)
- Orchestrator lifecycle state machine gaps (7 states: PENDING → COMPLETE)
- Progress tracker sync failures (tracker → plan-viewer-data.json → HTML)
- AC-ID validation chain integrity (AC-INDEX → TodoManager → progress-tracker → evidence)

## B) AC-ID entries for `cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml`

**CRITICAL INTEGRATION REQUIREMENT:**

All AC-IDs generated by this review MUST be **appended directly to AC-INDEX.yaml's `acceptanceCriteria[]` array** — NOT as a separate file under a new root key like `brittleness_acs:`.

The SINGLE SOURCE OF TRUTH is: `cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml`

### Integration Steps (MANDATORY):

1. **Query AC-INDEX.yaml** for existing AC-ID counts per category:
   ```bash
   grep "^    - id: AC-BRITTLE-" cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml | tail -1
   grep "^    - id: AC-RISK-" cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml | tail -1
   ```
   Extract the highest number in each category to determine next sequential ID.

2. **Append to `acceptanceCriteria[]` array** (NOT a separate nested YAML file):
   - Insert new AC-ID objects at the END of the `acceptanceCriteria[]` array
   - DO NOT create new root-level keys like `brittleness_acs:` or `report_acs:`
   - DO NOT create separate YAML files (e.g., AC-IDS-BRITTLENESS-2026-01-12.yaml) as the canonical storage

3. **Update AC-INDEX.yaml metadata**:
   - `total_ac_count`: Increment from current (e.g., 102 → 131 if adding 29)
   - `last_updated`: Set to ISO 8601 timestamp of this review
   - `categories.{BRITTLE,RISK,etc}.prefix`: Auto-populate if new category

4. **AC-ID Format** (each entry in `acceptanceCriteria[]`):
   - `id`: AC-<CATEGORY>-<NNN> (e.g., AC-BRITTLE-001)
   - `title`: Concise, capability-focused (e.g., "YAML encoding corruption repair")
   - `description`: Detailed acceptance criteria (what "done" means)
   - `status`: planned|in_progress|implemented|validated (default: planned)
   - `priority`: critical|high|medium|low
   - `phase`: 1|2|3|4 (which phase implements this)
   - `category`: brittleness|reliability|security|observability|testing
   - `tests`: List of test file paths (may be empty for planned AC-IDs)
   - `dependencies`: List of AC-IDs that must complete first
   - `evidencePaths`: List of repo paths where issue manifests
   - `riskIfUnfixed`: Critical/High/Medium/Low severity
   - `implementation`: Minimal-impact fix description (if known)
   - `verification`: How to test/validate the fix
   - `estimatedEffort`: Hours or story points
   - `owner`: Component owner (TBD if unknown)

5. **Flow through Governance Pipeline**:
   - MasterOrchestrator reads updated AC-INDEX.yaml via GovernanceMerger
   - TodoManager creates tasks for new AC-IDs with status=planned
   - TDD-Master enforces test-first implementation (CORE-019)
   - Completion tracked in progress-tracker.json with test evidence
   - Audit trail logged via EnterpriseAuditLogger

### DO NOT:

❌ Create separate YAML/JSON files in `cortex-brain/documents/reports/` as the canonical source  
❌ Nest AC-IDs under new root keys like `brittleness_acs:` or `report_acs:`  
❌ Split AC-ID definitions across multiple files  
❌ Update progress-tracker.json with new AC-IDs before integrating into AC-INDEX.yaml  

**Why?** MasterOrchestrator reads ONLY AC-INDEX.yaml. Separate files are invisible to the governance pipeline and won't flow through TodoManager → TDD-Master → Evidence Validation.

### Duplicate Handling:

- If AC-ID already exists in AC-INDEX.yaml, update in-place (refresh description, status, tests)
- If AC-ID is new, append to `acceptanceCriteria[]` array
- No duplicate AC-IDs allowed; each ID must be unique within the registry

Do not include any code/config blocks in the summary; only descriptive text.

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

---

# AC-ID Generation Workflow

When producing brittleness review output:

1. **Query AC-INDEX.yaml** for highest existing AC-ID number in each category:
   - `grep "^  - id: AC-BRITTLE-" cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml | tail -1`
   - Extract number, increment by 1 for next AC-ID

2. **Generate AC-ID entries** matching AC-INDEX.yaml schema:
   - Required fields: id, title, description, status, priority, phase, category, tests
   - Optional fields: dependencies, evidencePaths, estimatedEffort, owner

3. **Append to AC-INDEX.yaml** (do not modify existing entries):
   - Insert new AC-IDs at end of acceptanceCriteria array
   - Update schema metadata: total_ac_count, last_updated

4. **Update progress-tracker.json** to reference new AC-IDs:
   - Add AC-IDs to appropriate phase's planned_work array
   - Set initial status to "not_started"

5. **Flow through governance pipeline:**
   - MasterOrchestrator reads AC-INDEX.yaml via GovernanceMerger
   - TodoManager creates tasks for new AC-IDs
   - TDD-Master enforces test-first implementation
   - Evidence tracked in progress-tracker.json

**Critical Rules:**
- NEVER create finding IDs or parallel tracking systems
- ALL brittleness issues MUST become AC-IDs
- AC-IDs MUST flow through TodoManager (no shortcuts)
- Test evidence REQUIRED before marking implemented (CORE-019)

---

# Begin the analysis now
Search across `cortex-brain/cx6-plan/**` and the corresponding implementation and infrastructure. Produce the summary and AC-ID entries ready for AC-INDEX.yaml append.
