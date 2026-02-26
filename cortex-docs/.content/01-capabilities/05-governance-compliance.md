# Governance & Compliance

---
title: CORTEX Governance — Automated Rule Enforcement
type: explanation
audience: [Business Leaders, Product Owners, Software Developers]
last_verified: 2026-02-25
source_of_truth: cortex-registry/core/tier0-skull/skull-rules.yaml + cortex/orchestrators/core/enforcement_orchestrator.py
order: 5
---

> **Brain analogy:** Governance is CORTEX's **immune system**. Just as your immune system detects and neutralises threats automatically — without conscious effort — CORTEX's governance layer detects and blocks rule violations before they enter the codebase. You don't think about it; it just works.

---

## Governance Architecture

CORTEX enforces governance at **three levels**:

| Level | When | How |
|-------|------|-----|
| **Pre-Commit** | Before code enters Git | EnforcementOrchestrator + 10 agents |
| **CI Pipeline** | During continuous integration | Automated validation in CI |
| **Runtime** | During orchestrator execution | Governance gate in OrchestratorBase lifecycle |

---

## 22 Active CORE Rules

There are 38 CORE rules defined in `cortex-registry/core/tier0-skull/skull-rules.yaml`. Of these, **22 are actively enforced** via the EnforcementOrchestrator and ExtendedGovernanceAgent.

### Critical Rules (Enforced on Every Operation)

| Rule | Name | Enforcement |
|------|------|------------|
| **CORE-001** | Incremental Execution | Bounded operations — no unbounded loops |
| **CORE-002** | Markdown Suppression | Never create `.md`/`.txt` report files — all output inline |
| **CORE-005** | Path Portability | No hardcoded paths — use relative or environment-based |
| **CORE-008** | TDD Mandatory | Write failing test first, then implement. No exceptions |
| **CORE-011** | Type Hints | All functions must have type annotations |
| **CORE-012** | Docstrings | All public APIs must have docstrings |
| **CORE-013** | Error Handling | Proper exception handling required |
| **CORE-028** | File Naming | snake_case only (enforced by FileFactory) |
| **CORE-035** | Single Canonical | No duplicate implementations (enforced in Phase 05) |
| **CORE-048** | Holistic Validation | Validation gate before IMPLEMENT/FIX/REFACTOR |
| **CORE-049** | Silent Execution | Progress bars only, no verbose chatter |

### Extended Rules (CORE-058 through CORE-064)

Added during Phase 02 (Governance Alignment) through Phase 16 (Sweep Completeness) and wired via ExtendedGovernanceAgent in Phase 11:

| Rule | Name | Purpose |
|------|------|---------|
| **CORE-058** | SQLite WAL Mode | All SQLite databases must use WAL mode |
| **CORE-059** | MCP Footprint | MCP tool count validation |
| **CORE-060** | SDLC Brain | SDLC governance enforcement |
| **CORE-062** | Plan-First | Plan before execution for complex operations |
| **CORE-063** | Challenge-First | Challenge gate for high-risk changes |
| **CORE-064** | Sweep Completeness Contract | Every FIX/REFACTOR/AUDIT must exhaust its full issue catalogue — no partial sweeps. `SweepCatalogueOrchestrator` persists an open catalogue to `.cortex-runtime/sweeps/` so session restarts cannot silently abandon outstanding items. |

---

## 10 Enforcement Agents

**EnforcementOrchestrator** (`cortex/orchestrators/core/enforcement_orchestrator.py`) coordinates 10 agents:

| Agent | Focus | Key Rules |
|-------|-------|-----------|
| **GovernanceEnforcementAgent** | CORE rule adherence | CORE-002, CORE-028 |
| **SecurityCheckpointAgent** | Vulnerability detection | CORE-013, credential scan |
| **ComplianceValidationAgent** | Compliance checks | CORE compliance |
| **FileNamingEnforcementAgent** | File naming | CORE-028 (snake_case) |
| **IncrementalExecutionAgent** | Bounded execution | CORE-001, CORE-004 |
| **MarkdownSuppressionAgent** | Report file prevention | CORE-002 |
| **ArchitectureIntegrityAgent** | Structural integrity | CORE-017 through CORE-020, CORE-032, CORE-034 |
| **DiscoveryEnforcementAgent** | Discovery compliance | CORE-030, CORE-035 |
| **ResponseContentValidationAgent** | Response-level gate | CORE-002 response variant |
| **ExtendedGovernanceAgent** | New rules | CORE-058 through CORE-063 |

**Gate results:**
- **PASS** — operation proceeds
- **WARNING** — operation proceeds with logged advisory
- **BLOCKED** — operation stops immediately; no files changed

---

## TestQualityGate

**Location:** `cortex/testing/quality_gate.py` + `cortex-registry/core/test-quality-gate.yaml`

Every test is scored 0–9 using the formula:

```
Score = Impact(0-3) + Likelihood(0-2) + Detection(0-2) + Efficiency(0-2) − Maintenance(0-2)
```

| Score Range | Action |
|------------|--------|
| **≥ 7** | KEEP — high-value test |
| **4–6** | REVIEW — may need improvement |
| **< 4** | DELETE — low value, high maintenance |

**TestQualityGate** — invoked internally by the TDD orchestration pipeline (not exposed as a registered MCP tool).

**Business Leader:** "Test quality is quantified, not subjective. Every test has a score. We maintain 15,739 signal-dense tests, not 18,000 mixed-quality ones."

**Product Owner:** "During the refactor, TestQualityGate identified 3,360 low-value tests (scoring <4). We archived them and kept the signal. 696 golden tests all score ≥7."

**Developer:** "I commit a new test. If it scores below 7, TDDOrchestrator blocks the commit and tells me why — usually low detection coverage or high maintenance cost."

---

## Audit Trail

Every CORTEX action is recorded in CortexAuditDB (SQLite WAL mode, `.cortex-runtime/`):

- Orchestrator decisions
- Governance gate results (PASS/WARNING/BLOCKED)
- Test execution results
- Strategy selection reasoning
- AC markers (AC_START / AC_COMPLETE)

The trail is immutable and Git-versioned where applicable.

---

## Practical Examples

**Business Leader:** "Our compliance team asks 'how do you enforce code quality?' I point them to 38 CORE rules enforced automatically on every commit, 10 enforcement agents, and TestQualityGate scoring. It's not policy — it's infrastructure."

**Product Owner:** "Last week a developer tried to commit a utility function without tests. CORE-008 blocked the commit automatically. The developer wrote the test, it passed, and the commit went through — all in 10 minutes."

**Developer:** "I added a new endpoint. EnforcementOrchestrator flagged: (1) CORE-011 — missing type hint on the handler, (2) CORE-012 — no docstring on the public method. I fixed both, re-committed, and the gate passed. Total overhead: 2 minutes."

---

## SweepCatalogueOrchestrator (CORE-064)

`cortex/orchestrators/support/sweep_catalogue_orchestrator.py` implements the Sweep Completeness Contract. When a FIX/REFACTOR/AUDIT sweep begins, it:

1. **Opens** a named catalogue in `.cortex-runtime/sweeps/{sweep_id}.db`
2. **Records** every issue found as a catalogue entry (pending/resolved states)
3. **Persists** across session boundaries — restarting VS Code does not lose open items
4. **Asserts** completion before the sweep can be closed — zero pending items required
5. **Guards** `VacuumOrchestrator` from deleting open `.db` catalogue files

**Sweep status** is accessible via `SweepCatalogueOrchestrator` directly or by querying `.cortex-runtime/sweeps/{sweep_id}.db`.

---

*All rule IDs and agent names verified against live governance registry · 21 February 2026*
