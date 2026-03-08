# The Full Delivery Lifecycle — From Idea to Production

---
title: Delivery Lifecycle — How CORTEX Manages Requirements Through Release
type: explanation
audience: [Business Leaders, Product Owners, Software Developers, Curious Learners]
last_verified: 2026-03-08
order: 9
---

> **The central idea:** Most development tools focus on a single phase of delivery. CORTEX orchestrates the complete lifecycle — from requirements analysis through design, implementation, testing, security review, and release — with structured knowledge injected at each phase and security gates at every transition.

---

## The Problem with Phase Isolation

Traditional software delivery treats each phase as a separate concern handled by different tools. Requirements in a planning tool. Design in a diagramming tool. Implementation in an IDE. Testing in a CI system. Security in a scanner. Release in a deployment pipeline.

Knowledge doesn't flow between these tools. A security requirement captured during requirements analysis is not automatically visible to the developer implementing the feature two weeks later. A design decision is not automatically injected as a constraint when the implementation begins. The result is a team that repeats the same mistakes across phases because each phase starts without full context from the previous ones.

CORTEX treats the entire delivery lifecycle as a single coordinated pipeline where knowledge from each phase flows forward into the next.

---

## Seven Lifecycle Phases — Each with Dedicated Structure

CORTEX codifies seven phases of the software delivery lifecycle as structured workflow templates. Each template defines the steps, the knowledge to inject, the governance gates, and the success criteria for that phase.

### Phase 0 — Change Intelligence (Product Owner Decision Support)

Before a feature even enters the requirements phase, CORTEX helps Product Owners evaluate whether to build it at all. The Change Intelligence Orchestrator discovers how the system works today via LENS analysis, compares current processes against best-practice patterns, produces structured gap analyses with severity scores, evaluates ROI based on actual codebase complexity, and generates system capability inventories.

The output is a Change Recommendation Report: a structured artifact containing current-state documentation, gap analysis, feasibility assessment, ROI projection, and implementation path options — all grounded in real code analysis rather than assumptions. This evidence-based approach replaces subjective "should we build this?" discussions with data-driven decision support.

When the decision is "yes, build it", the Requirements Engineer takes the change intent and decomposes it into structured, testable requirements — business requirements, functional requirements, non-functional requirements, and acceptance criteria — all mapped to the existing architecture discovered during change intelligence.

### Phase 1 — Requirements Analysis

When a developer or product owner asks CORTEX to analyse requirements or scope a feature, the requirements analysis workflow activates. It runs code intelligence analysis to understand the existing system, identifies the threat surface of the proposed change, flags ambiguities that need resolution before design begins, and produces a structured scope document with explicit acceptance criteria.

The output of requirements analysis flows directly into the design phase — the existing system context, identified constraints, and acceptance criteria are all available to the design workflow without manual transfer.

### Phase 2 — Solution Design

The design phase validates proposed approaches against architectural patterns, checks design decisions against security-by-design principles, and flags choices that would violate active governance rules before any implementation begins.

Design decisions are recorded as structured documents that remain linked to the resulting implementation. When a code reviewer later asks "why was this approach chosen?", the design record is available — not lost in a Slack thread from three weeks ago.

### Phase 3 — Implementation

Implementation follows the test-driven cycle for every change. The knowledge from requirements and design is injected as constraints: the acceptance criteria from requirements become the test cases for the red phase; the design decisions become the architectural constraints for the green phase; the security requirements become validation gates for the refactor phase.

An implementation cannot be considered complete without passing tests for every acceptance criterion, satisfying all active governance rules, and clearing the security gate for the specific change type.

### Phase 4 — Code Review

The Code Review Orchestrator runs multi-pass automated reviews across all changed files. Each review pass examines a different dimension: structural analysis (architecture conformance, complexity, coupling), security audit (secrets, PII, vulnerability patterns), governance compliance (active rule adherence), test-coverage gap detection (which behaviours lack tests), and style conformance (naming, formatting, documentation coverage).

Findings are surfaced inline with severity levels (P0 critical through P3 advisory) and include specific fix suggestions. The Code Review Orchestrator integrates with the Quality Analysis Engine, so review comments reference the codebase's overall quality trend — a finding in a declining-quality module receives higher priority than the same finding in an improving module.

Code that passes all review passes receives a governance certificate — a recorded confirmation that all automated checks passed at a specific point in time. This certificate is part of the audit trail.

### Phase 5 — Integration Verification

Integration tests verify that the new capability works correctly in the context of the full system, not just in unit isolation. CORTEX's integration testing approach checks the specific integration seams touched by the change — the connections between the new code and the existing system — rather than running the entire integration suite indiscriminately.

Integration failures are surfaced with full context from the code intelligence layer: which components are involved, how they connect, and what changed most recently in each component. This context dramatically reduces the investigation time for integration failures.

### Phase 6 — Security Assessment

A dedicated security assessment phase runs the complete security analysis for the change: static application security testing, CVE checks for any new or updated dependencies, OWASP Top 10 validation for the specific feature type, and a **Threat Model Engine** review that applies STRIDE classification to entry points, data flows, and trust boundaries. The engine produces a ranked threat catalogue with risk scores and recommended mitigations — particularly when the change touches authentication, authorisation, or data handling.

Security assessment findings are prioritised by severity. Critical and high findings block release. Medium findings require acknowledgment. Low findings are documented and tracked.

### Phase 7 — Release Readiness

The release readiness phase confirms that all preceding phases completed successfully, all security findings have been addressed, the deployment configuration is correct, secrets have been rotated as required, and the release documentation is in place.

Only when all seven phases have passed does CORTEX consider a feature genuinely ready for production.

---

## Knowledge Injection — The Right Information at the Right Phase

Each phase declares the knowledge it needs, and CORTEX injects that knowledge automatically. This is not documentation lookup — it is structured context that becomes part of the execution plan.

The knowledge resolution follows a priority order that ensures the most specific, most relevant guidance always wins:

- **Stack-specific knowledge** wins when a Python-specific or TypeScript-specific rule conflicts with a generic rule
- **SDLC-phase knowledge** provides phase-specific guidance that overrides generic engineering advice
- **Domain knowledge** adds business-vertical context — a payments feature gets payments-specific security rules
- **Generic knowledge** provides the baseline that applies when nothing more specific is available

The resolution happens silently before execution begins. The developer sees the result — a plan grounded in the right guidance for their specific context — without needing to manually locate and apply the relevant knowledge.

---

## Planning — Structured Decomposition

For complex features or significant architectural changes, CORTEX includes structured planning tools that decompose high-level goals into specific, executable tasks.

The planning engine produces decomposed work items with explicit acceptance criteria, estimated effort, risk assessment, and dependencies between items. For very large initiatives, wave-based delivery planning produces a sequence of increments each independently deliverable and valuable.

Each planned item includes a readiness check — a set of conditions that must be true before work on that item can begin. This prevents the common failure mode of starting an item only to discover a dependency that wasn't ready, resulting in wasted partial work.

Planning output integrates with work item management systems. Items created by CORTEX's planning tools appear in the team's tracking system automatically, with all relevant context attached. The `cortex_ado` MCP tool connects directly to Azure DevOps boards, pulling user stories, bugs, and tasks, enriching them with LENS context, and injecting sprint-aware acceptance criteria into the intelligence pipeline. The provider-agnostic `WorkItemProvider` protocol supports Jira, GitHub Issues, and custom internal trackers with the same interface.

---

## The Production Readiness Audit

CORTEX includes a comprehensive production readiness audit that can be triggered at any time and runs automatically before major releases. The audit covers nine sequential stages:

**Environment check** — Validates that all required dependencies are present and at the correct versions.

**Governance pre-flight** — Runs the full governance specification validation against the current codebase.

**19-point production scan** — A comprehensive checklist covering code quality, test coverage, security, documentation, architecture integrity, and operational readiness.

**Architecture validation** — Checks the wiring between all components against the specification, at three levels of detail: component connections, interface contracts, and runtime behaviour.

**Orchestrator health** — Verifies that all active orchestrators are healthy, responsive, and correctly configured.

**Cleanup** — Removes accumulated documentation sprawl, stale files, and orphaned artifacts. The Vacuum Recency Guard protects files modified within the last 7 days from deletion, ensuring work-in-progress artefacts are never swept up by aggressive cleanup heuristics.

**Meta-audit** — 23 checks against the framework's own internal consistency — ensuring the intelligence layer, prompt system, and configuration files are all in agreement.

**Auto-fix convergence** — The detect→fix→rescan loop runs until all critical and high-priority violations are resolved. This stage does not complete until the codebase is genuinely clean.

**Final verification** — The full test suite runs in parallel, and the audit trail is validated for completeness.

---

## Debugging — Structured Diagnosis Across All Stacks

When something goes wrong, CORTEX's debugging pipeline provides structured diagnosis across multiple technology stacks. Eight debugging strategies cover the full range of modern development contexts, each following a consistent five-phase methodology.

### The Five-Phase Debug Lifecycle

Every debugging session follows the same disciplined process, regardless of the technology stack involved:

**Inject** — CORTEX places precisely targeted diagnostic markers into the relevant code. These markers capture execution state, variable values, timing information, and control flow — without modifying application behaviour. Each technology stack has a dedicated injection strategy that understands the conventions of that ecosystem.

**Capture** — The application runs with markers active, and CORTEX collects the diagnostic output. For frontend applications, this includes console traces and DOM event flows. For APIs, it includes request/response pairs with headers and timing. For databases, it includes query execution plans and parameter values.

**Analyse** — The captured data flows through CORTEX's intelligence layer, which correlates the diagnostic output with the code structure, the change history, and any relevant root cause analyses from previous sessions. The analysis identifies not just what went wrong, but why — and whether this failure pattern has been seen before.

**Fix Plan** — CORTEX generates a prioritised remediation plan with specific steps, each with a defined test to verify the fix. High-confidence fixes can be applied automatically; lower-confidence fixes are presented for developer review.

**Cleanup** — All diagnostic markers are removed automatically when the session ends. This is not optional — the cleanup manager verifies that zero diagnostic artifacts remain in the codebase. Debugging infrastructure never ships to production.

### Eight Technology-Specific Strategies

For **Python applications**, three strategies cover the most common failure categories: test failures (why did this specific test break?), refactoring regressions (what changed during the refactor that introduced a failure?), and governance violations (why is this code failing a governance gate?).

For **frontend applications** (JavaScript, TypeScript, React, Angular, Vue), a dedicated strategy injects console tracing and DOM event monitoring. The strategy understands framework-specific patterns — component lifecycle in React, change detection in Angular, reactivity in Vue — and targets diagnostic markers accordingly.

For **visual layout issues**, a screenshot analysis strategy uses Vision API to capture the rendered page, map visual elements to CSS selectors and HTML structure, and identify discrepancies between expected and actual layout. This bridges the gap between what a developer sees in the browser and what exists in the code.

For **API integrations** (REST, GraphQL, gRPC), a trace strategy captures complete request/response cycles including headers, payload structure, timing, and error codes. This surfaces authentication failures, serialisation mismatches, timeout issues, and contract violations that are invisible from either the client or server alone.

For **database operations** (SQL Server, Oracle, PostgreSQL), a query trace strategy captures execution plans, parameter bindings, transaction boundaries, and locking behaviour. This reveals performance bottlenecks, missing indexes, and concurrency issues that only manifest under load.

For **C# and .NET applications**, a dedicated strategy traces method entry and exit, dependency injection resolution, middleware pipeline execution, and async/await continuation paths. This covers the full .NET request lifecycle from HTTP arrival through controller execution to database access.

---

## Repository Onboarding — Bringing a New Codebase Under Governance

When a team adopts CORTEX for an existing codebase, the onboarding process produces a complete intelligence profile within minutes — no manual configuration of rules, patterns, or governance settings required.

The onboarding engine runs the full code intelligence analysis against the new repository, identifying the technology stack, the architectural patterns in use, the security posture, the test coverage baseline, and the domain context. The results feed into a structured onboarding report that includes a prioritised list of governance gaps, a recommended remediation sequence, and a generated interactive dashboard showing the current state of the codebase.

For business leaders, onboarding provides an immediate, data-driven assessment of a codebase's quality and risk profile — valuable for acquisition due diligence, vendor code assessment, or baseline measurement before a modernisation initiative. For product owners, it surfaces the technical debt and governance gaps that affect delivery velocity. For engineers, it provides the complete architectural map they need to contribute effectively from their first day on the project.

---

## Dashboard Generation — Visual Reporting on Demand

CORTEX generates interactive HTML dashboards that visualise codebase health, quality trends, architecture maps, and governance compliance. Dashboards are produced from live analysis — not manually assembled slides or spreadsheets.

A single command produces a complete dashboard suite: a landing page that summarises the portfolio view across all repositories, plus detailed per-repository dashboards with quality scores, dependency maps, pattern detection results, and trend analysis over time. Dashboards are static HTML files that can be hosted anywhere, shared with stakeholders, or embedded in internal portals — no runtime server required.

For business leaders, dashboards provide the engineering health visibility that is typically invisible: which codebases are improving, which are accumulating technical debt, and where governance compliance is strongest or weakest. For product owners, dashboards connect code quality to delivery confidence — a repository with rising quality scores and declining violation trends is a repository that will deliver features predictably.

---

## Privacy-Safe Synchronisation — Sharing Code Without Sharing Secrets

For organisations that maintain both private development repositories and shared or public-facing repositories, CORTEX provides a structured synchronisation pipeline that ensures sensitive metadata never crosses the boundary.

The synchronisation follows a four-gate process: pull the latest state from both repositories, compute the differences, sanitise the outgoing changes by stripping CORTEX-internal metadata, governance traces, runtime databases, and any detected secrets or personally identifiable information, then merge the sanitised changes into the target repository.

This is particularly valuable for organisations that contribute to open source from private codebases, share code between internal teams with different security clearance levels, or maintain separate development and deployment repositories. The sanitisation is automated and verified — there is no reliance on developers remembering to remove sensitive content before pushing.

---

*Lifecycle phases verified against template registry · Planning, debugging, onboarding, dashboard, and sync capabilities verified against live implementation*
