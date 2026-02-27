---
title: Frequently Asked Questions
consolidates:
  - 06-faq-general.md
  - 06-faq-orchestration.md
  - 06-faq-governance-tdd.md
  - 06-faq-lens-intelligence.md
  - 06-faq-mcp-integration.md
  - 06-faq-testing-workflow.md
  - 06-faq-business-product.md
last_verified: 2026-02-27
source_of_truth: cortex/ + cortex-registry/ + .github/copilot-instructions.md
audience: [Business Leaders, Product Owners, Software Developers]
---

# Frequently Asked Questions

---

## General and Getting Started

### What is CORTEX?

CORTEX (COgnitive Real-Time EXecution) is a production-grade AI engineering framework. It combines wired orchestrators across four tiers, a growing library of MCP tools exposed via a Pylance-style stdio server, CORE governance rules enforced at pre-commit, CI, and runtime, a parallel code intelligence engine (LENS), and TDD-first execution where CORE-008 mandates RED then GREEN then REFACTOR on every IMPLEMENT and FIX. It works directly inside your IDE via the Model Context Protocol. CORTEX is an LLM-orchestration framework — it delegates AI reasoning to the host LLM (GitHub Copilot or GPT); it does not embed ML models.

### How is CORTEX different from generic AI coding tools?

Generic AI coding tools answer questions and suggest code. CORTEX orchestrates entire workflows end-to-end with mandatory governance (CORE rules enforced automatically), mandatory TDD (blocked if skipped), persistent state (SQLite audit log), full observability (OpenTelemetry, Prometheus, AC markers), and integration across IDE, CI/CD, pre-commit hooks, and work item systems.

### What IDEs does CORTEX support?

Any IDE or AI assistant that supports MCP with stdio transport: VS Code with GitHub Copilot Chat (primary, Pylance-style auto-start), Cursor, Claude Desktop, and any MCP-compatible client.

### How do I verify CORTEX is running?

Call `cortex_verify` in Copilot Chat. If it responds, MCP is live. Alternatively check `.vscode/settings.json` for the cortex MCP server configuration, or run `python3 -m cortex.mcp` in the terminal.

### What Python version is required?

Python 3.9 or higher. Verified by UpgradeOrchestrator.validate_requirements() at session start. To skip preflight in CI/CD set `CORTEX_SKIP_PREFLIGHT=true`.

### How do I install CORTEX?

Clone the repository, run `pip install -r requirements.txt`, and open the workspace in VS Code. The MCP server auto-starts. Verify by calling `cortex_verify` in Copilot Chat.

### Is there a Windows version?

Yes. All make commands have VS Code Task equivalents. Use `python scripts\run_tests.py {mode}` in PowerShell. The MCP setup script auto-detects Windows, macOS, and Linux.

### Where does CORTEX store runtime data?

All runtime data lives in `.cortex-runtime/` (gitignored): `audit.db` for the SQLite WAL audit log, `traces/orchestrator-traces.db` for AC marker traces, and `sweeps/{sweep_id}.db` for per-sweep CORE-064 tracking. No PostgreSQL, MongoDB, or Redis required.

### Does CORTEX require internet access?

No. CORTEX runs entirely locally. LENS analysis, MCP transport (stdio), SQLite audit logs, and the cortex-registry are all local. The only optional network calls are `cortex_fetch_work_items` for ADO or Jira REST API access and production Kubernetes deployments. Air-gapped environments are fully supported.

---

## Orchestration and Architecture

### How many orchestrators does CORTEX have?

Wired orchestrators span four tiers: core, domain, support, and git. The `cortex/orchestrators/` directory contains additional classes (strategy implementations, mixins, sub-components) but the wired orchestrators are the canonical IOrchestrator-compliant entry points.

### What is the universal orchestrator lifecycle?

Every orchestrator satisfies IOrchestrator via OrchestratorProtocolMixin. The five-step lifecycle is: setup, govern, execute, validate, teardown. The execute and run methods auto-log to SQLite WAL. Audit failures are non-blocking.

### How does CORTEX route requests?

IntentRouter classifies every request using LENS analysis and keyword extraction into multiple intent types. Confidence scores at or above 0.7 auto-route, 0.5 to 0.7 may seek clarification, and below 0.5 prompts the user.

### What is MasterOrchestrator?

The executive coordinator at `cortex/orchestrators/core/master_orchestrator.py`. It receives every request from the MCP layer, delegates to IntentRouter for classification, dispatches to the appropriate orchestrator, collects results, and formats them. It also owns the multi-stage audit fix pipeline.

### What are AC markers?

Audit trail bookmarks emitted by every orchestrator invocation. AC_START opens the session, AC_COMPLETE closes with timing. They write to `.cortex-runtime/traces/orchestrator-traces.db`. Orphaned AC_START without matching AC_COMPLETE is a P0 violation.

### Can I create my own orchestrator?

Yes. Create a file in `cortex/orchestrators/{tier}/` using snake_case naming, inherit from OrchestratorProtocolMixin, implement setup, execute, validate, get_name, and get_mode, add AC markers, write the test first (CORE-008), and register in `cortex-registry/core/specifications/wiring/`.

### How does cross-orchestrator communication work?

Orchestrators never call each other directly. Communication flows through MasterOrchestrator dispatch, SharedAuditTrail for shared context, LENS context passed as a structured object, and WorkflowEngine for multi-step YAML-defined pipelines.

### What happens if an orchestrator fails?

Three layers of resilience: circuit breakers stop calls after threshold breaches, retry handlers manage transient failures with exponential backoff, and graceful degradation returns partial results when non-critical sub-components fail.

---

## Governance and TDD

### How many governance rules exist?

CORE rules plus AC rules are defined in `cortex-registry/core/tier0-skull/skull-rules.yaml`. Tier zero skull rules are immutable — they cannot be overridden, disabled, or bypassed.

### What are the most important rules?

CORE-001 (incremental execution), CORE-002 (markdown suppression — all output inline), CORE-008 (TDD mandatory), CORE-011 (type hints), CORE-012 (docstrings), CORE-028 (snake_case file naming), CORE-035 (single canonical implementation), CORE-048 (holistic validation), CORE-049 (silent execution), CORE-055 (golden test contract), and CORE-064 (sweep completeness).

### Can I disable a CORE rule?

No. Tier zero rules are immutable. If a rule conflicts with your project needs, the correct path is a governance review.

### What is EnforcementOrchestrator?

It coordinates enforcement agents that each check a category of CORE rules. Gate results are PASS, WARNING, or BLOCKED. A BLOCKED result stops the operation immediately with no files modified.

### What is CORE-008 TDD Mandatory?

For every IMPLEMENT or FIX: write a failing test first (RED), write minimum code to pass (GREEN), then refactor while keeping all tests green (REFACTOR). This is not optional. Attempts to skip TDD are BLOCKED by EnforcementOrchestrator.

### What is CORE-064 Sweep Completeness?

Every FIX, REFACTOR, or AUDIT creates a SweepCatalogue entry in SQLite. The catalogue tracks every issue. The operation cannot be marked complete until every item has status CLOSED or an explicit approve-wont-fix decision. The audit fix convergence loop enforces this.

### What is TestQualityGate?

A scoring system (zero to nine) evaluating tests against impact, likelihood, detection, efficiency, and maintenance. Score seven or above means KEEP (golden tier candidate), four to six means REVIEW, and below four means DELETE.

### Does governance slow development?

Gate latency is under one hundred and fifty milliseconds. Most requests pass all gates on first try. The cost of governance is paid once before files change — the cost of not having governance is paid repeatedly through regressions, partial sweeps, and architectural drift.

---

## LENS and Intelligence

### What is LENS?

Language, Examination, Navigation, Synthesis. CORTEX's code intelligence engine — specialised analyzers running in parallel producing structured intelligence for orchestrators.

### What languages does LENS support?

Full support for Python, TypeScript and JavaScript, and C# (.NET). Framework support for Angular, React, and Vue. Partial SQL support for security scanning.

### What is the Brain Tier architecture?

Three layers in `cortex/intelligence/`: Perception (recognises patterns in LENS data), Reasoning (selects strategies based on patterns), and Action (builds step-by-step execution plans).

### How does LENS caching work?

Two-level cache: in-memory LRU for the current session (zero latency on hit) and persistent SQLite cache surviving session restarts. Cache keys derive from file path plus content hash. A file modification invalidates only that file's entries.

### Can I run LENS on an external repository?

Yes. Use `cortex_onboard` in Copilot Chat or RepositoryOnboardingOrchestrator. It runs the full analyzer pass, scores security findings, and stores results for subsequent queries.

---

## MCP Tools and Integration

### How many MCP tools are there?

Registered canonical tools span multiple categories, all registered in `cortex/mcp/mcp_registry.py` and exposed through JSON-RPC 2.0 stdio transport. The library continues to grow as new capabilities are added.

### What is the correct entry point?

For full lifecycle tracking use `cortex_request_lifecycle`. For intent classification only use `cortex_classify`. The deprecated `cortex_process_request` should not be used in new integrations.

### How do I list all tools?

Call `cortex_tools_catalog` from Copilot Chat. It reads directly from the live tool registry.

### What does cortex_onboard return?

A structured assessment including security findings with severity, complexity hotspots, tech stack detected, architecture patterns matched, and recommended next steps.

### How does cortex_refactor handle renaming?

It performs semantic refactoring across Python, C#, and TypeScript. C# symbol rename uses Roslyn by-name rename — you provide the symbol name, not a byte offset. CORTEX finds all usages across the solution.

### How do work items integrate?

`cortex_fetch_work_items` provides provider-agnostic work item access via the WorkItemProvider Protocol. ADO is the default provider. Adding Jira or a custom system requires implementing the protocol and registering it in the provider factory. The MCP tool surface remains unchanged.

---

## Testing and Development Workflow

### How do I run the test suite?

Always use the canonical runner: `make test-batch` for full batch run, `make test-smoke` for quick validation (under sixty seconds), `make test-fast` for unit tests only, or `python3 scripts/run_tests.py {mode}` for cross-platform. Never use raw pytest commands that bypass the batch reporter or xdist parallelism.

### How many tests exist?

The test suite is comprehensive — spanning golden, phase, unit, and integration tests. Exact counts evolve as the framework grows. Use `make test-batch` for the full run.

### What is the TDD workflow?

RED: write a failing test in `tests/` that specifies the behaviour. GREEN: write minimum code in `cortex/` to make it pass. REFACTOR: clean up while keeping all tests green. Tests mirror the cortex source structure under `tests/`.

### What is a golden test?

Golden tests validate immutable contracts — behaviours that must never change. They run serially for deterministic results. All golden tests must always pass (CORE-055). A golden test failure is a P0 blocker.

### How do I debug a failing test?

Use the Debug task (verbose, no xdist): `python3 -m pytest tests/path/to/test.py -p no:xdist --tb=long -v -s`. This disables parallelism, shows full tracebacks, and captures stdout.

### What is validate_orchestrator_context?

All MCP tool functions that call validate_orchestrator_context must guard it: `if orchestrator_context is not None: validate_orchestrator_context(orchestrator_context)`. This allows direct test invocation without MasterOrchestrator context while enforcing routing in production.

---

## Business and Product

### What business problem does CORTEX solve?

Inconsistent quality (different developers apply different standards), governance drift (architectural standards degrade over time), and context loss (long-running refactors get abandoned). CORTEX solves all three through automatic rule enforcement, mandatory TDD, and the sweep completeness contract.

### Is CORTEX a replacement for code review?

No. CORTEX handles mechanical checks (type hints, naming, TDD, security patterns) automatically, freeing reviewers to focus on business logic, architecture decisions, and domain correctness.

### How does CORTEX handle sensitive code?

CORE-017 is enforced by SecurityScanAgent detecting hardcoded credentials, SQL injection, XSS, and PII exposure. The secret_redactor module redacts sensitive values from audit logs. CORTEX never sends source code to external services — all analysis runs locally.

### How do we onboard a new codebase?

One command: call `cortex_onboard` with the repository path. CORTEX runs LENS, classifies the domain, scores security findings, identifies the tech stack, matches architecture patterns, and produces a structured assessment. No configuration files needed.

### Can multiple teams use CORTEX on the same codebase?

Yes. Governance is shared (all teams under the same rules), sweep tracking is per-team or shared, work item integration maps to team-level sprint tracking, and multi-repo support provides cross-repo search and dependency graphs.

### How do we track adoption metrics?

The `cortex_metrics` MCP tool captures TDD cycles, debug sessions, code generation, orchestrator invocations, and governance gate results. Export via `cortex_metrics_report` in YAML or JSON format. Grafana dashboards consume the Prometheus metrics endpoint.

---

*All answers verified against live codebase*

---

## Upcoming Capabilities

### What capabilities are planned next?

CORTEX is actively evolving. Planned capabilities include:

- **Unified Response Templates** — standardising progress display across all orchestrators with engagement visibility blocks showing which orchestrators ran, timing, and multi-phase progress.
- **Multi-Stack Debug Pipeline** — extending debugging from Python-only to multi-stack (JavaScript/TypeScript, HTML/Vision API, REST/GraphQL/gRPC, SQL, and C#/.NET) with automatic strategy selection based on detected stack.
- **RCA Memory Engine** — structured root cause analysis with multiple methodologies, a Prevention Gate that escalates on repeated P0 root causes, and a Recurrence Signature Engine detecting the same root cause class across sessions.

### Do upcoming capabilities add new orchestrators or MCP tools?

No. Planned capabilities are additive extensions to existing infrastructure — new strategies within existing pattern engines, new methods on existing mixins, and new operations on existing MCP tools. Zero new orchestrators. Zero new MCP tools. All changes are backward-compatible.
