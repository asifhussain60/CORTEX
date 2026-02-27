---
title: Governance and Workflows
consolidates:
  - 01-capabilities-governance-compliance.md
  - 01-capabilities-workflow-templates.md
  - 01-capabilities-workflow-template-tiers.md
  - 01-capabilities-response-formatting.md
last_verified: 2026-02-27
source_of_truth: cortex-registry/core/tier0-skull/skull-rules.yaml + cortex/orchestrators/core/enforcement_orchestrator.py + cortex-registry/workflows/templates/
audience: [Business Leaders, Product Owners, Software Developers]
---

# Governance and Workflows

CORTEX treats governance not as a policy document but as infrastructure — rules enforced automatically at every commit, every CI run, and every runtime operation. Workflow templates codify reusable execution patterns into YAML definitions that the WorkflowEngine executes as typed step graphs.

---

## Governance Architecture

CORTEX enforces governance at three levels:

| Level | When | How |
|-------|------|-----|
| Pre-Commit | Before code enters Git | EnforcementOrchestrator coordinates 10 agents |
| CI Pipeline | During continuous integration | Automated validation stages |
| Runtime | During orchestrator execution | Governance gate in the orchestrator lifecycle |

Thirty-eight CORE rules plus two AC rules are defined in `cortex-registry/core/tier0-skull/skull-rules.yaml`. Tier zero skull rules are immutable — they cannot be overridden, disabled, or bypassed. The file header states explicitly that these rules take precedence over all other tiers.

---

## Critical CORE Rules

| Rule | Name | Enforcement |
|------|------|------------|
| CORE-001 | Incremental Execution | Bounded operations — no unbounded loops |
| CORE-002 | Markdown Suppression | Never create report files; all output inline |
| CORE-005 | Path Portability | No hardcoded paths; use relative or environment-based |
| CORE-008 | TDD Mandatory | Write failing test first, then implement; no exceptions |
| CORE-011 | Type Hints | All functions must have type annotations |
| CORE-012 | Docstrings | All public APIs must have docstrings |
| CORE-013 | Error Handling | Proper exception handling required |
| CORE-028 | File Naming | snake_case only, enforced by FileFactory |
| CORE-035 | Single Canonical | No duplicate implementations anywhere |
| CORE-048 | Holistic Validation | Validation gate before every implementation |
| CORE-049 | Silent Execution | Progress bars only; no verbose chatter |

### Extended Rules

| Rule | Name | Purpose |
|------|------|---------|
| CORE-055 | Golden Test Contract | Golden tests must always pass with zero regressions |
| CORE-058 | SQLite WAL Mode | All SQLite databases must use Write-Ahead Logging |
| CORE-059 | MCP Footprint | MCP tool count validation |
| CORE-060 | SDLC Brain | SDLC governance enforcement |
| CORE-062 | Plan-First | Plan before execution for complex operations |
| CORE-063 | Challenge-First | Challenge gate for high-risk changes |
| CORE-064 | Sweep Completeness Contract | Every operation must exhaust its full issue catalogue; no partial sweeps |

---

## Ten Enforcement Agents

EnforcementOrchestrator at `cortex/orchestrators/core/enforcement_orchestrator.py` coordinates ten agents:

| Agent | Focus | Key Rules |
|-------|-------|-----------|
| GovernanceEnforcementAgent | CORE rule adherence | CORE-002, CORE-028 |
| SecurityCheckpointAgent | Vulnerability detection | CORE-013, credential scan |
| ComplianceValidationAgent | Compliance checks | CORE compliance |
| FileNamingEnforcementAgent | File naming | CORE-028 (snake_case) |
| IncrementalExecutionAgent | Bounded execution | CORE-001, CORE-004 |
| MarkdownSuppressionAgent | Report file prevention | CORE-002 |
| ArchitectureIntegrityAgent | Structural integrity | CORE-017 through CORE-020, CORE-032, CORE-034 |
| DiscoveryEnforcementAgent | Discovery compliance | CORE-030, CORE-035 |
| ResponseContentValidationAgent | Response-level gate | CORE-002 response variant |
| ExtendedGovernanceAgent | Extended rules | CORE-058 through CORE-063 |

Gate results are PASS (operation proceeds), WARNING (operation proceeds with logged advisory), or BLOCKED (operation stops immediately with no files changed).

---

## TestQualityGate

Location: `cortex/testing/quality_gate.py` combined with `cortex-registry/core/test-quality-gate.yaml`.

Every test is scored zero to nine using the formula: Impact (zero to three) plus Likelihood (zero to two) plus Detection (zero to two) plus Efficiency (zero to two) minus Maintenance (zero to two).

| Score Range | Action |
|------------|--------|
| Seven or above | KEEP — high-value test, golden tier candidate |
| Four to six | REVIEW — may need improvement |
| Below four | DELETE — low value, high maintenance cost |

The `TestQualityGate` scoring system applies this rubric from production repositories (no registered MCP tool wrapper; invoked internally by the TDD orchestration pipeline).

---

## SweepCatalogueOrchestrator — CORE-064

`cortex/orchestrators/support/sweep_catalogue_orchestrator.py` implements the Sweep Completeness Contract. When a FIX, REFACTOR, or AUDIT sweep begins, it opens a named catalogue in `.cortex-runtime/sweeps/{sweep_id}.db` using SQLite WAL mode. Every discovered issue is recorded as a catalogue entry with pending or resolved states. The catalogue persists across session boundaries — restarting VS Code does not lose open items. The sweep cannot be closed until every item has status CLOSED or an explicit approve-wont-fix decision. Open sweeps are surfaced via `SweepCatalogueOrchestrator.get_open_issues(sweep_id)` (note: `cortex_sweep_status` MCP tool is not currently registered).

---

## Audit Trail

Every CORTEX action is recorded in CortexAuditDB (SQLite WAL mode at `.cortex-runtime/`):

- Orchestrator decisions
- Governance gate results (PASS, WARNING, BLOCKED)
- Test execution results
- Strategy selection reasoning
- AC markers (AC_START and AC_COMPLETE timestamps)

The trail uses hash-chain integrity via `cortex/infrastructure/audit_hash_chain.py`. Each audit entry includes a cryptographic hash of the previous entry, creating a tamper-evident chain.

---

## Response Formatting Standards

CORTEX responses follow strict formatting standards loaded from `cortex-registry/`:

- Inline delivery — CORE-002 mandates all output inline, never as report files
- Structured output — tables, code blocks, and hierarchical sections
- Role-aware detail levels — different depths for business leaders, product owners, and developers
- Silent execution — CORE-049 mandates progress bars only, no verbose chatter

Every response begins with a plain-language reflection of what CORTEX understood from the request, giving the user ten seconds to confirm or correct before execution begins.

---

## Workflow Template Architecture

Workflow templates are YAML files stored in `cortex-registry/workflows/templates/` and executed by the WorkflowEngine at `cortex/core/workflow_engine.py`. They are organised in a three-tier hierarchy: Primitive, then Composite, then Workflow.

### Tier 1 — Primitives

Location: `cortex-registry/workflows/templates/primitives/`

Atomic, reusable building blocks with a single responsibility. Primitives are referenced (never duplicated) by higher tiers.

| Category | Examples |
|----------|---------|
| analysis | `lens-ast-scan.yaml`, `lens-vision-scan.yaml` |
| execution | `audit-trace.yaml`, `file-extraction.yaml`, `semantic-edit.yaml` |
| governance | `sweep-catalogue-open.yaml`, `sweep-catalogue-close.yaml` |
| intelligence | `intelligence-injection.yaml` |
| validation | `detect-fix-rescan-loop.yaml`, `regression-test.yaml`, `duplicate-detection.yaml` |

The `audit-trace.yaml` primitive is consumed by all workflow templates that need AC marker trace chain wiring, ensuring every orchestrator invocation produces a paired AC_START and AC_COMPLETE entry in the trace database.

### Tier 2 — Composites

Location: `cortex-registry/workflows/templates/composites/`

Composed of multiple primitives. Represent a reusable workflow pattern for a domain. Must not duplicate a top-level workflow file per CORE-035.

### Tier 3 — Workflows

Location: `cortex-registry/workflows/templates/<domain>/`

Full, intent-specific execution workflows. Each maps to an intent type.

| Domain | Workflow Examples |
|--------|-------------------|
| tdd | `tdd-feature-implementation.yaml`, `tdd-api-service.yaml` |
| security | `security-compliance-audit.yaml`, `threat-model-analysis.yaml` |
| lifecycle | `onboarding-workflow.yaml`, `migration-modernize.yaml` |
| backend | `csharp-refactor-workflow.yaml`, `csharp-security-workflow.yaml` |
| audit | Audit pipeline templates |
| governance | `master-plan-phase-lifecycle.yaml`, `golden-test-promotion.yaml` |

### How Templates Execute

The WorkflowEngine reads a YAML template, parses its phases and dependencies, and executes phases sequentially. For each phase it runs setup, then the governance gate, then execution (following the RED then GREEN then REFACTOR pattern where applicable), then validation against acceptance criteria, and finally teardown with audit trail recording. A validation loop retries if needed, and on completion the registry status is updated.

---

*All rule identifiers and agent names verified against live governance registry — 27 February 2026*

---

## RCA as a Governance Signal (Phase 87 PLANNED)

The RCA Memory Engine integrates with the governance layer to turn historical failure patterns into proactive enforcement signals. This closes the loop between the "what happened" (OPJ), the "why it happened" (RCA Engine), and "don't let it happen again" (Prevention Gate + URS).

### RCA Prevention Gate Governance Levels

| Recurrence Count | Severity | Action |
|-----------------|----------|--------|
| 1 | Advisory | Log RCA match, surface to developer as info |
| 2 | Warning | Surface in governance gate response, include fix reference |
| 3+ P0 | Blocking | Halt operation, require structured review before proceeding |

### RCA Workflow Template (Phase 87 PLANNED)

A new workflow template `cortex-registry/workflows/templates/rca/rca-analysis-workflow.yaml` orchestrates the full RCA pipeline:

1. **Trigger** — OPJMixin detects a new failure with `rca: True` flag
2. **Methodology Selection** — RCAEngine selects appropriate methodology (Five Whys, Fishbone, Fault Tree, Causal Chain) based on failure category
3. **Analysis** — Structured analysis generates the `RCAAnalysis` dataclass
4. **Signature** — RecurrenceSignatureEngine generates and stores canonical fingerprint
5. **Prevention Rule** — `generate_prevention_rule()` creates a blocking or advisory rule
6. **URS Signal** — Reinforcement signal emitted based on recurrence count and severity
7. **cortex-docs Sync** — Documentation updated inline (CORE-002 — no report files)
