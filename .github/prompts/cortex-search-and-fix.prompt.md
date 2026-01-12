---
agent: agent
---

# 🔧 CORTEX Search-and-Fix – Production Brittleness & Risk Review

**Purpose:** Search CORTEX codebase for brittleness, breakage points, and material production risks  
**Version:** 2.0.0  
**Date:** 2026-01-12  
**Governance:** CORE-002 (no root files), CORE-017 (governance enforcement), CORE-009 (plan organization), CORE-025 (intelligent challenge)

---

## 🔗 MASTERORCHESTRATOR DELEGATION

**All findings delegated to unified orchestrator for planning:**

```bash
# Execute via MasterOrchestrator (central control)
python3 -m src.main "{user_intent}" --orchestrator master --format markdown
```

**MasterOrchestrator handles:**
- ✅ Load governance rules (tier0/tier1/tier2/tier3)
- ✅ Validate against SKULL rules
- ✅ Create AC-IDs for brittleness findings
- ✅ Append findings to AC-INDEX.yaml
- ✅ Update master-plan.yaml with new AC-IDs
- ✅ Update progress-tracker.json
- ✅ Trigger SyncOrchestrator

**Do NOT:**
- ❌ Directly modify AC-INDEX.yaml
- ❌ Directly modify progress-tracker.json
- ❌ Create separate brittleness files
- ❌ Update tracker manually

---

## 🛡️ REGRESSION PREVENTION (Reference Only)

**Reference:** CORTEX.prompt.md maintains unified regression check via MasterOrchestrator.

**This prompt DOES NOT perform direct file access.** All findings delegated to Python orchestrator.

**Why not embed code?** When MasterOrchestrator is updated, regression check automatically improves for all prompts (DRY principle).

---

## 🛡️ INTELLIGENT CHALLENGE PROTOCOL (CORE-025)

**Purpose:** Validate findings against governance and feasibility.

**Implementation:** Delegated to MasterOrchestrator → RequestValidator.

**Reference:** `.github/prompts/CORTEX-ALIGN.prompt.md § INTELLIGENT CHALLENGE PROTOCOL`

---

## 📊 Analysis Scope
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
Produce AC-ID entries ready for direct insertion into AC-INDEX.yaml:

- `runMeta`: 
  - `date` (ISO 8601)
  - `reviewer` (agent name or human)
  - `repoRef` (branch/commit hash)
  - `scopePaths` (list of directories searched)
  - `cortexVersion` (e.g., "6.0.0")
  - `phaseContext` (current phase from progress-tracker.json)
  - `nextAvailableIDs`: Map of category → next sequential number (e.g., BRITTLE: 15, RISK: 8)
- `acceptanceCriteria[]`: array of AC-ID objects matching AC-INDEX.yaml schema
- `acceptanceCriteria[].fields`:
  - `id` (AC-<CATEGORY>-<NNN>, e.g., AC-BRITTLE-015)
  - `title` (concise, capability-focused, e.g., "YAML encoding corruption repair")
  - `description` (detailed acceptance criteria - what "done" means)
  - `status` (planned|in_progress|implemented|validated - default: planned)
  - `priority` (critical|high|medium|low)
  - `phase` (1|2|3|4 - which phase implements this)
  - `category` (brittleness|reliability|security|observability|testing)
  - `tests` (list of test file paths that validate this AC)
  - `dependencies` (list of AC-IDs that must complete first)
  - `evidencePaths` (list of repo paths where issue manifests)
  - `riskIfUnfixed` (Critical/High/Medium/Low severity)
  - `implementation` (minimal-impact fix description)
  - `verification` (how to test/validate the fix)
  - `estimatedEffort` (hours or story points)
  - `owner` (component owner if inferable; else TBD)
- `rollup`: 
  - `countByPriority` (critical|high|medium|low counts)
  - `countByCategory` (brittleness|reliability|security|observability counts)
  - `countByPhase` (Phase 1/2/3/4 counts)
  - `topRiskAreas` (list of components with most critical/high AC-IDs)
  - `totalEstimatedEffort` (sum of estimated hours)
- `implementationPlan[]`: ordered list of AC-IDs for day-zero fixes
  - `acID` (the AC-ID to implement)
  - `title` (from AC-ID entry)
  - `priority` (critical|high|medium|low)
  - `estimatedEffort` (hours)
  - `dependencies` (list of AC-IDs that must complete first)
  - `phase` (which phase implements this)
  - `owner` (if inferable)

**Integration with Governance Pipeline:**
1. AC-IDs generated by this prompt append to AC-INDEX.yaml
2. MasterOrchestrator reads AC-INDEX.yaml via GovernanceMerger
3. TodoManager creates tasks for AC-IDs with status=planned
4. TDD-Master enforces test-first implementation (CORE-019)
5. Completion tracked in progress-tracker.json with test evidence
6. Audit trail logged via EnterpriseAuditLogger

The AC-IDs must be appended to AC-INDEX.yaml (no duplicates):
- Query existing AC-IDs in category to get next sequential number
- If AC-ID exists, treat as update (refresh description, status, tests)
- If new, append to acceptanceCriteria array
- Sort by category, then by number within category

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
