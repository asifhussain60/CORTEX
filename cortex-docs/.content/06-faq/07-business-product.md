# FAQ — Business & Product

---
title: FAQ — Business & Product
type: reference
audience: [Business Leaders, Product Owners]
last_verified: 2026-02-28
source_of_truth: cortex/ + cortex-registry/ + .github/copilot-instructions.md
order: 7
---

> **Purpose:** Non-technical answers to strategic questions about CORTEX — what it delivers, how it reduces risk, and how to measure its impact. All capability claims verified against live implementation.

---

## What business problem does CORTEX solve?

Engineering teams lose velocity in three ways:

1. **Inconsistent quality** — different developers apply different standards. Bugs reach production because no one checked type hints, docstrings, or TDD compliance automatically.
2. **Governance drift** — architectural standards degrade over time. What starts as "we always write tests first" becomes "we write tests when we have time."
3. **Context loss** — long-running refactors get abandoned mid-sweep. Technical debt compounds because there's no record of what was half-fixed.

CORTEX solves all three:
- **CORE rules** enforced automatically at every commit and every AI-assisted action — no one can bypass governance accidentally.
- **TDD is mandatory** (CORE-008) — the architecture physically prevents implementing without tests.
- **CORE-064 Sweep Completeness Contract** — every refactor sweep is tracked in SQLite; it cannot be marked complete until every item is resolved.

---

## What does the ROI look like?

CORTEX's value is measured in three categories:

| Category | What Changes | How to Measure |
|----------|-------------|----------------|
| **Defect Prevention** | Governance enforcement catches type errors, missing tests, security vulnerabilities before commit | Compare pre/post defect escape rate |
| **Velocity** | LENS analysis + TDD scaffolding reduces time per feature | Track lead time before/after adoption |
| **Technical Debt** | CORE-064 prevents partial sweeps; Vacuum removes sprawl | Track open sweep count + markdown file count over time |

The `cortex_metrics` MCP tool records TDD cycles, debug sessions, and code generation events — use `cortex_metrics_report` to export YAML/JSON for dashboards.

---

## Is CORTEX a replacement for code review?

No — CORTEX is a **complement** to code review, not a replacement. It handles the mechanical checks automatically (type hints, naming conventions, TDD, security patterns), freeing reviewers to focus on business logic, architecture decisions, and domain correctness.

Think of CORTEX as the automated pre-flight checklist. Human reviewers are the pilots who make judgement calls.

---

## How does CORTEX handle sensitive code (credentials, PII)?

**CORE-017** (Security Scan) is enforced by the SecurityScanAgent within EnforcementOrchestrator. It detects:
- Hardcoded credentials and API keys
- SQL injection patterns
- XSS vulnerabilities
- PII exposure in logs

The `secret_redactor.py` module (`cortex/infrastructure/secret_redactor.py`) redacts sensitive values from audit logs before writing to `.cortex-runtime/`. CORTEX never sends source code to external services — all analysis runs locally.

---

## What is the governance compliance trail?

Every CORTEX action produces a compliance trail:

1. **Pre-commit gate result** — which rules were checked, which passed/failed
2. **AC markers** — `AC_START` / `AC_COMPLETE` timestamps in SQLite
3. **Audit hash chain** — each audit entry cryptographically linked to the previous one (`cortex/infrastructure/audit_hash_chain.py`)
4. **Sweep catalogues** — every FIX/REFACTOR/AUDIT sweep itemised in SQLite

This trail is stored in `.cortex-runtime/` (gitignored for security but queryable locally). The `/audit fix` Stage 2 runs a 19-point production scan against this trail.

---

## How do we onboard a new codebase?

One command:

```
Call cortex_onboard with {"path": "/path/to/repo"}
```

CORTEX will:
1. Run LENS (15 parallel analyzer components, 300–800ms)
2. Classify the domain (industry, vertical, regulatory context)
3. Score security findings (P0 critical / P1 high / P2 medium)
4. Identify tech stack (frameworks, languages, versions)
5. Match architecture patterns against the 9-pattern registry
6. Produce a structured assessment with recommended next steps

No configuration files needed. No agents to configure. One call, inline results.

---

## Can multiple teams use CORTEX on the same codebase?

Yes. CORTEX is designed for multi-team environments:

- **Governance is shared** — all teams work under the same CORE rules. No team can lower the bar for others.
- **Sweep tracking is per-team** — each sweep has its own SQLite file; cross-team sweeps use a shared sweep ID.
- **Work item integration** — `cortex_fetch_work_items` maps ADO/Jira work items to CORTEX operations, enabling team-level sprint tracking.
- **Multi-repo support** — `cortex/mcp/tools/multi_repo/` provides cross-repo search, dependency graphs, and shared audit trails.

---

## How does CORTEX fit into our CI/CD pipeline?

CORTEX integrates at three points:

| Integration Point | What It Does |
|------------------|-------------|
| **Pre-commit hook** | `deployment/hooks/` — runs EnforcementOrchestrator locally before `git push` |
| **CI pipeline** | `deployment/` Kubernetes + Docker configs — runs full governance scan on every PR |
| **Post-deploy** | Canary deployment managed by `cortex/mcp/tools/deployment/canary_deployer.py` |

For CI environments, set `CORTEX_SKIP_PREFLIGHT=true` to bypass the package installation preflight and `CORTEX_DISABLE_DB_CLEANUP=true` to preserve the audit DB between runs.

---

## How do we track CORTEX adoption metrics?

The `cortex_metrics` MCP tool captures:

| Metric | What It Measures |
|--------|----------------|
| TDD cycles | RED → GREEN → REFACTOR completions per day |
| Debug sessions | Debugger invocations + resolution time |
| Code generation | Lines generated vs. lines manually written |
| Orchestrator invocations | Which orchestrators are used most |
| Governance gate results | Pass rate per CORE rule over time |

Export via `cortex_metrics_report` (YAML or JSON). Grafana dashboards consume the Prometheus metrics endpoint at `cortex/prometheus_metrics.py`.

---

## What is the CORTEX Master Plan?

`cortex-registry/cortex-master.yaml` is a **thin phase index** (≤ 500 lines) tracking all development phases. The platform is mature and production-ready.

Each phase has a dedicated detail file in `cortex-registry/planning/phases/completed/`. The master plan is a reference index only — never a detail document. This is enforced by the THIN INDEX CONTRACT. Phase status is accessible via `cortex_plan` (MCP) or by reading `cortex-registry/cortex-master.yaml` directly.

---

## What is the difference between `/audit` and `/audit fix`?

| Command | What It Does |
|---------|-------------|
| `/audit` | Scan only — surfaces violations, no auto-fix (Stages 1–6) |
| `/audit fix` | Full 9-stage pipeline — scan + autonomous fix convergence loop |

For a **read-only governance report**, use `/audit`. For **production readiness**, use `/audit fix` — it loops until all P0 and P1 violations are resolved (CORE-064 convergence guarantee).

---

## Does CORTEX require internet access?

**No.** CORTEX runs entirely locally:
- LENS analysis runs against local files
- MCP transport is stdio (process-to-process, no network)
- SQLite audit logs are local `.cortex-runtime/` files
- `cortex-registry/` is local YAML (no cloud sync)

The only optional network calls are:
- `cortex_fetch_work_items` → ADO/Jira REST API (requires `ADO_PAT` or equivalent)
- `deployment/` infrastructure → Kubernetes/Docker deployments (production only)

Air-gapped environments are fully supported for the core CORTEX workflow.

---

*Verified against live codebase*
