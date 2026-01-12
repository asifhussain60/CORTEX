---
agent: agent
---

# 🔍 CORTEX Brittleness Review – Day-Zero Risk Analysis

**Purpose:** Analyze CORTEX codebase for brittleness, breakage points, and production risks  
**Version:** 2.1.0 (Plan-Integrated with Regression Prevention)  
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
- ✅ Append to AC-INDEX.yaml
- ✅ Update master-plan.yaml with new AC-IDs
- ✅ Update progress-tracker.json
- ✅ Trigger SyncOrchestrator for dashboard

**Do NOT:**
- ❌ Directly modify AC-INDEX.yaml
- ❌ Directly modify progress-tracker.json
- ❌ Create separate brittleness files
- ❌ Update tracker manually

---

## 🛡️ REGRESSION PREVENTION (Reference Only)

**Reference:** CORTEX.prompt.md maintains unified regression check via MasterOrchestrator.

**This prompt DOES NOT perform direct file access.** All state validation delegated to Python orchestrator.

**Why not embed code?** When MasterOrchestrator is updated, regression check automatically improves for all prompts (DRY principle).

---

## 🛡️ INTELLIGENT CHALLENGE PROTOCOL (CORE-025)

**Purpose:** Validate analysis findings against governance and feasibility.

**Implementation:** Delegated to MasterOrchestrator → RequestValidator.

**Reference:** `.github/prompts/CORTEX-ALIGN.prompt.md § INTELLIGENT CHALLENGE PROTOCOL`

---

## 🔗 PLAN INTEGRATION (CRITICAL)

**This review integrates findings into the cx6-plan:**

| Plan Asset | Integration Role |
|------------|------------------|
| `master-plan.yaml` | Add new AC-IDs to appropriate phase |
| `AC-INDEX.yaml` | Orchestrator APPENDs brittleness AC-IDs |
| `progress-tracker.json` | Orchestrator updates planned_work |
| `plan-viewer-data.json` | Auto-synced via SyncOrchestrator |

**Output Flow:**
```
Findings → AC-IDs → MasterOrchestrator → AC-INDEX.yaml append → master-plan update → tracker update → dashboard sync
```

---

## 📊 Scope & Analysis
- **CORTEX-specific paths:**
  - State files: `cortex-brain/tier1/tracking/progress-tracker.json`, `cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml`
  - Governance: `cortex-brain/tier0/governance/core-rules.yaml` (23 SKULL rules)
  - Database: `cortex-brain/state/planning.db` (SQLite, single-writer)
  - Orchestrators: `src/orchestrators/` (master, planning, TDD, ADO, cleanup, etc.)
  - Tests: `tests/` (pytest-based, evidence source for tracker)
  - Scripts: `scripts/` (sync, validation, consolidation utilities)
  - **CORTEX TOOLKIT:** `src/tools/` (Python tool modules) and `src/mcp/` (MCP tool exposure)

## 🔧 CORTEX TOOLKIT COHERENCE REVIEW (NEW - v2.1.0)

**CRITICAL:** All Python tools in CORTEX TOOLKIT must be neatly organized, efficiently named, and fully exposed via MCP for the MasterOrchestrator to have complete knowledge of available capabilities.

### Toolkit Inventory & Analysis

**Search Scope:**
- `src/tools/*.py` → Core utility tools (non-MCP exposed)
- `src/mcp/*_tools.py` → MCP-exposed tools (decorated with @mcp_tool)
- `scripts/*.py` → Operational scripts (should be refactored into tools or orchestrators)

**Toolkit Assessment Checklist:**

1. **Tool Discovery & Exposure**
   - [ ] All tools in `src/tools/` and `src/mcp/` are cataloged
   - [ ] Each tool is either: (a) exposed via @mcp_tool, (b) internal utility, or (c) candidate for consolidation
   - [ ] MCP discovery in `capability_registry.py` knows about ALL MCP tools
   - [ ] MasterOrchestrator can query complete tool registry without blind spots
   - [ ] No tools hidden in unimported modules or orphaned directories

2. **Naming Consistency & Clarity**
   - [ ] ALL tool filenames follow kebab-case (not snake_case, not PascalCase)
   - [ ] ALL tool filenames ≤ 25 characters (excluding `.py` extension)
   - [ ] NO adjectives in tool names (new, updated, enhanced, old, legacy, etc.)
   - [ ] Tool names are **capability-focused**, not implementation-focused
     - ✅ GOOD: `audit-query.py`, `evidence-generator.py`, `state-manager.py`
     - ❌ BAD: `new-audit-query.py`, `enhanced-evidence-generator.py`, `legacy-state-manager.py`
   - [ ] Tool names describe WHAT the tool does, not HOW or WHEN it was created
   - [ ] Function naming inside tools follows snake_case convention

3. **Duplicate & Redundant Tools**
   - [ ] Search for tools with overlapping functionality
   - [ ] Identify candidates for consolidation (e.g., multiple "audit" tools)
   - [ ] Check git history for orphaned reimplementations of same capability
   - [ ] Flag tools with <20% usage in codebase (candidates for removal)
   - [ ] Consolidation should preserve all unique capabilities (no feature loss)

4. **MCP Exposure & Governance (CORE-024)**
   - [ ] ALL public-facing tools MUST be decorated with `@mcp_tool` (CORE-024 enforcement)
   - [ ] MCP decorator applied consistently: `name`, `description`, `category`, `parameters`, `returns`, `metadata`
   - [ ] Tool categories align with governance intent: `audit`, `governance`, `planning`, `development`, `maintenance`, etc.
   - [ ] Metadata includes: `tags`, `version`, `autonomous` flag, `ac_standard` (if governance-tracked)
   - [ ] Tools without @mcp_tool decorator must have documented reasons (internal utilities only)
   - [ ] Non-MCP tools must NOT be called directly by MasterOrchestrator (routing via MCP only)

5. **Tool Organization & Discoverability**
   - [ ] Tool modules are organized by responsibility (audit, governance, planning, etc.)
   - [ ] No single tool file exceeds 500 lines (split large tools)
   - [ ] Each tool file has clear docstring explaining purpose and examples
   - [ ] Tool dependencies are explicit (imports at top, no circular deps)
   - [ ] Validation helpers and constants are co-located with tools they serve
   - [ ] No orphaned utility functions (all utilities either exported or internal to tool)

6. **Quality & Testing**
   - [ ] Each MCP tool has corresponding test file in `tests/mcp/test_*_tools.py`
   - [ ] Tool tests include: happy path, error handling, parameter validation, integration
   - [ ] Tools validate input parameters strictly (type hints + runtime checks)
   - [ ] Tools fail fast with clear error messages (no silent failures)
   - [ ] Tools return consistent output format (dict with `status`, `data`, `error` keys)
   - [ ] Tools are idempotent where applicable (safe to retry without side effects)

7. **Documentation & Discoverability**
   - [ ] Each tool has clear docstring (description, parameters, returns, examples)
   - [ ] MCP metadata includes human-readable descriptions (not just technical specs)
   - [ ] Tool purpose is understandable to MasterOrchestrator (not magic names)
   - [ ] Related tools are cross-referenced in documentation
   - [ ] Tool catalog or index document exists (human-readable tool directory)

### Implementation Priority for Toolkit Coherence

**Phase 1: Audit & Classification** (Low risk, high visibility)
1. Inventory all tools in `src/tools/` and `src/mcp/`
2. Classify each tool: (a) Core MCP tool, (b) Internal utility, (c) Candidate for consolidation/removal
3. Identify naming violations (adjectives, non-kebab-case, >25 chars)
4. Generate toolkit health report (coverage %, exposure %, quality metrics)

**Phase 2: Consolidation & Renaming** (Medium risk, high impact)
1. Consolidate duplicate tools (preserve all unique capabilities)
2. Rename tools to remove adjectives and enforce kebab-case (<25 chars)
3. Update all imports and references after renaming
4. Add @mcp_tool decorator to all public tools (enforces CORE-024)
5. Verify MCP discovery re-discovers all tools post-rename

**Phase 3: Organization & Optimization** (Medium risk, medium impact)
1. Reorganize tools by responsibility (move orphaned utilities)
2. Split oversized tools (>500 lines) into focused modules
3. Define tool categories consistently (align with governance intents)
4. Update tool documentation and cross-references
5. Ensure no circular dependencies between tools

**Phase 4: Quality & Testing** (Medium risk, high confidence)
1. Add/update test files for all MCP tools
2. Validate input parameters strictly in each tool
3. Implement consistent error handling and output format
4. Verify idempotency where applicable
5. Update tests to verify MCP exposure (CORE-024 compliance)

---

## Operating Rules
- **No code snippets or configuration blocks** in the response.
- Focus on **issues that materially impact**: correctness, reliability, security, deployability, scalability, operability.
- Assume production constraints: **partial failures**, latency spikes, retries, deployment rollouts, config drift, dependency upgrades, and noisy neighbors.
- Challenge assumptions and defaults; look for execution-time brittleness and hidden edge cases.
- **Minimal-impact changes only**: do not introduce new subsystems, major rewrites, or architecture expansions. Prefer small, robust fixes.
- Prioritize by real-world impact and likelihood; explain how failures manifest at runtime.

---

## Repeatable “Tool” Behavior (avoid file bloat)
- Do **NOT** create new files each run.
- Update/extend the existing plan via **one canonical record** inside `AC-INDEX.yaml`.
- If an entry already exists, update it (status, severity, evidence paths, recommendation, owner, lastReviewed) rather than duplicating.
- Use the structured format below for all updates.

## Required Output Format
1) A concise summary (paragraphs + bullets), broken into sections.
2) A single YAML (preferred) or JSON “update payload” that can be pasted into `AC-INDEX.yaml` to incrementally maintain the plan.
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

## 1a) CORTEX Toolkit Inventory & Analysis (CRITICAL)
Perform exhaustive toolkit audit:
1. **List all tool files:**
   - `src/tools/*.py` (list all, note file sizes and naming)
   - `src/mcp/*_tools.py` (identify MCP tool modules)
   - `src/mcp/` non-tools (identify core MCP files vs tools)
   - `scripts/*.py` (candidate tools for refactoring into toolkit)

2. **Classify each tool:**
   - **Exposed via MCP** (has @mcp_tool decorator)
   - **Internal utility** (explicitly marked as internal, no MCP exposure)
   - **Candidate for consolidation** (overlapping functionality)
   - **Candidate for removal** (unused, redundant, orphaned)
   - **Missing MCP exposure** (public tool without @mcp_tool decorator)

3. **Naming audit:**
   - Files with adjectives (new, old, updated, enhanced, legacy, temp, etc.) → Rename
   - Files with non-kebab-case naming → Convert to kebab-case
   - Files with names >25 characters (excluding .py) → Shorten/refactor
   - Examples to flag: `duplicate-detection-toolkit.py` (too long, adjective), `real_implementation_engine.py` (non-kebab, compound), `enhanced-audit-query.py` (adjective)

4. **Duplication detection:**
   - Group tools by purpose (all audit tools together, etc.)
   - Identify overlapping capabilities (e.g., multiple "validate" tools)
   - Check git history for reimplemented features
   - Flag tools with <20% usage in codebase

5. **MCP exposure validation:**
   - For each tool in `src/tools/`, check if it has @mcp_tool decorator
   - For each tool in `src/mcp/*_tools.py`, verify decorator with proper metadata
   - Check `capability_registry.py` `_discover_decorated_tools()` to verify all tools are imported
   - Verify CORE-024 compliance (all public tools must have @mcp_tool)
   - Identify any tools registered manually that should use decorator

6. **Test coverage & organization:**
   - Map each tool to its test file (should exist in `tests/mcp/test_*_tools.py`)
   - Flag tools without tests
   - Check for orphaned test files with no corresponding tool
   - Verify test imports and dependencies are correct

7. **Documentation & discoverability:**
   - Check tool module docstrings (should clearly describe purpose)
   - Verify MCP metadata includes human-readable descriptions
   - Flag missing examples or unclear parameter documentation
   - Check for tool catalog or directory document (if missing, candidate for creation)

8. **Quantified metrics (required output):**
   - Total tools: `N`
   - Tools with @mcp_tool decorator: `M` (percentage: M/N)
   - Tools without tests: `T`
   - Naming violations (adjectives, case, length): `V`
   - Consolidation candidates: `C`
   - Tools not in capability_registry discovery: `U`
   - Overall toolkit health score: `(N-V-U-T+M)/N * 100%`

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
All brittleness and toolkit findings MUST be converted to proper AC-IDs that flow through the governance-to-todo pipeline.

**AC-ID Format:** `AC-<CATEGORY>-<NNN>`
- Examples: `AC-BRITTLE-001`, `AC-RISK-005`, `AC-DEBT-012`, `AC-TOOLKIT-008`
- Categories: 
  - `BRITTLE` (brittleness/fragility issues)
  - `RISK` (runtime failure risks)
  - `DEBT` (technical debt)
  - `SEC` (security issues)
  - `TOOLKIT` (CORTEX toolkit organization, naming, exposure, consolidation)
- Sequential numbering: Query AC-INDEX.yaml to find highest existing number in category, increment by 1

**Category Mapping (issue type → AC category):**
- Encoding/corruption/data integrity → `AC-BRITTLE-*`
- Concurrency/race conditions/state loss → `AC-RISK-*`
- Missing tests/validation gaps/observability → `AC-DEBT-*`
- Security/secrets/exposure → `AC-SEC-*`
- Governance/blocking/hardcoded assumptions → `AC-RISK-*`
- **NEW: Tool naming violations (adjectives, non-kebab-case, >25 chars) → `AC-TOOLKIT-*`**
- **NEW: Tool duplication/consolidation opportunities → `AC-TOOLKIT-*`**
- **NEW: Tool MCP exposure gaps (missing @mcp_tool decorator) → `AC-TOOLKIT-*`**
- **NEW: Tool organization/discoverability issues → `AC-TOOLKIT-*`**
- **NEW: Tool test coverage gaps → `AC-TOOLKIT-*`**

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
- **CORTEX Toolkit Coherence** (organization, naming, exposure gaps, consolidation opportunities)
- **Reliability & Failure Modes** (retry, timeout, rollback, circuit breaking)
- **Data & Concurrency Hazards** (corruption, races, sync drift)
- **Security & Secrets** (exposure, least privilege, encryption)
- **Deployability & Environment Drift** (config parity, portability)
- **Scalability & Performance** (hot paths, resource limits)
- **Observability & Operability** (blind spots, debugging, on-call)
- **Testing & Evidence Gaps** (missing tests, false positives, coverage)
- **Quick Wins** (minimal-impact, high leverage, <1 day implementation)
- **Assumptions Challenged** (what defaults seem risky, hidden dependencies)

### CORTEX Toolkit Coherence Section Details

**Toolkit Health Report** (quantified metrics):
- Total tools inventoried: `N` (src/tools/ + src/mcp/ modules)
- Tools exposed via MCP: `M` (with @mcp_tool decorator)
- Naming violations: `K` (adjectives, non-kebab-case, >25 chars)
- Duplicate/redundant tools: `D` (candidates for consolidation)
- Tools without tests: `T` (missing test coverage)
- Tools not in capability_registry: `U` (discovery blind spots)

**Specific Findings** (per toolkit concern):
- **AC-TOOLKIT-NNN: [Naming issue]** (e.g., "Rename enhanced-audit-query.py to audit-query.py per CORE-022")
- **AC-TOOLKIT-MMM: [Consolidation opportunity]** (e.g., "Merge duplicate-detection-toolkit.py with gap-detector.py")
- **AC-TOOLKIT-LLL: [MCP exposure gap]** (e.g., "Add @mcp_tool decorator to validate-prompt-integrity.py")
- **AC-TOOLKIT-KKK: [Organization issue]** (e.g., "Move orphaned validators/ utilities into audit-tools.py")
- **AC-TOOLKIT-JJJ: [Test coverage gap]** (e.g., "Add test_orchestrator-scaffolder.py for CORE-024 validation")

Each toolkit issue should include:
- **AC-ID** (e.g., AC-TOOLKIT-001)
- **Tool(s) affected** (specific file names)
- **Type** (naming|consolidation|exposure|organization|testing)
- **Current state** (what's wrong)
- **Desired state** (how it should be)
- **Impact** (why this matters for MasterOrchestrator)
- **Effort** (minimal|low|medium)

Each issue (brittleness or toolkit) should be bullets with: 
- **AC-ID** (generated identifier, e.g., AC-BRITTLE-015, AC-TOOLKIT-008)
- **Title** (capability-focused, e.g., "YAML encoding repair mechanism", "Consolidate audit tool family")
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
