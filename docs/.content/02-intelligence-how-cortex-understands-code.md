# How CORTEX Understands Code

---
title: Code Intelligence — LENS, the Brain, and Three Tiers of Reasoning
type: explanation
audience: [Business Leaders, Product Owners, Software Developers, Curious Learners]
last_verified: 2026-03-06
order: 2
---

> **The central idea:** Before CORTEX writes a single line or suggests a single change, it reads — deeply. Nine specialised analysis tools run simultaneously against your codebase and complete in under one second. The results flow through three layers of reasoning before any action is taken.

---

## Why Code Intelligence Matters

Most AI coding tools generate responses from the question alone. CORTEX generates responses from the question *plus a deep understanding of your specific codebase* — its structure, its history, its security posture, its patterns, and its business domain.

This distinction produces qualitatively different outcomes. A generic AI might suggest a pattern that doesn't fit your architecture. CORTEX suggests the pattern already present in your codebase, applied consistently with your naming conventions, tested against your existing test infrastructure, and validated against your governance rules.

---

## LENS — The Sensory System

LENS stands for Language → Examination → Navigation → Synthesis. It is CORTEX's code intelligence engine. Nine specialised analyzers run in parallel against any codebase and produce a unified picture of the code in under one second.

### The Nine Analyzers

All nine run simultaneously. The total time is bounded by the slowest single analyzer — not the sum of all nine.

| Analyzer | What It Reads | What It Produces |
|---|---|---|
| **Structure** | Classes, functions, imports, decorators, type annotations | A complete map of what exists and how it is organised |
| **History** | Commit patterns, change frequency, authorship | Which parts of the codebase change most — and carry the most risk |
| **Documentation** | Docstring coverage, comment quality, gaps | A documentation health score with specific gaps identified |
| **Dependencies** | Import chains, circular references, external libraries | A dependency map showing what connects to what |
| **Security** | Vulnerability patterns, credential exposure, known weaknesses | A prioritised list of security findings with remediation guidance |
| **Patterns** | Framework signatures, architectural patterns, design conventions | Which well-established patterns the codebase uses — and where they are incomplete |
| **Complexity** | Code complexity, coupling, maintainability | Per-function and per-module quality scores |
| **Business Domain** | Industry vertical, regulatory context, domain-specific conventions | What business problem the code is solving |
| **Technology Stack** | Frameworks, runtimes, build tools, dependency versions | A complete picture of the technical environment |

### Languages Supported

LENS provides full analysis for Python, TypeScript, JavaScript, and C#/.NET. Framework-specific support covers Angular, React, and Vue. Language-specific adapters mean CORTEX understands not just the syntax of each language, but the conventions and patterns specific to each ecosystem.

### Caching — Analysis Without Waiting

LENS caches analysis results so that repeat requests against unchanged code return instantly. Results are keyed to the exact content of each file plus the version of each analyzer. When a file changes, only that file's cached entries are invalidated — the rest of the codebase analysis remains instantly available. This makes every subsequent request in a session faster than the first.

---

## Three Intelligence Tiers — Matching Depth to Need

Not every request requires the same depth of analysis. CORTEX automatically selects one of three tiers based on what the request actually needs.

| Tier | Speed | Scope | When Used |
|---|---|---|---|
| **Quick** | Under 200ms | Cached governance rules and framework knowledge | Simple questions — definitions, rule lookups, quick checks |
| **Targeted** | Under 2 seconds | LENS analysis of relevant files plus domain knowledge | Building, fixing, and refactoring — the daily workflow |
| **Full** | Under 10 seconds | Everything in Targeted, plus work item context and deep cross-domain synthesis | Investigations, audits, and complex architectural decisions |

A developer asking "what does CORE-008 mean?" gets a Quick response in milliseconds. A developer asking "implement a payment reset endpoint" gets Targeted analysis of the payment module, the existing service patterns, and relevant security knowledge — all completed before the first test is written.

---

## The Brain — Perception, Reasoning, and Action

After LENS produces its analysis, three cognitive layers process it into a concrete execution plan.

### Perception — Pattern Recognition

The Perception layer maintains a catalogue of known engineering patterns. When CORTEX analyses a repository, it matches observed signals against nine canonical patterns: mediator, strategy, observer, factory, template method, chain of responsibility, adapter, repository, and command. Each match receives a confidence score between 0.0 and 1.0.

The output is a clear picture of what architectural approach the codebase is already using. If your codebase uses the Repository pattern at 0.92 confidence, CORTEX knows to follow that pattern — not introduce an incompatible alternative.

For business leaders, Perception answers: "What patterns is this team actually using?" For product owners: "Does this codebase follow the standards we expect?" For engineers: "What conventions should I follow when adding to this module?"

### Reasoning — Strategy Selection

The Reasoning layer takes Perception's pattern map and selects the best approach from a ranked set of strategies. Strategies are named approaches such as "test-first incremental", "extract service with refactor", or "security audit before implementation". Each has a historical success rate that updates after every execution.

The system learns which strategies work best for your team over time. If test-first incremental produces consistently successful outcomes on your Django projects, its confidence score rises — and Reasoning recommends it automatically for similar requests.

### Action — Execution Planning

The Action layer converts the chosen strategy into a step-by-step plan. Every step has a mandatory test checkpoint, a defined rollback point if the step fails, and a governance validation check. The plan is built before any code is touched — ensuring that complex, multi-step operations are safe and reversible throughout execution.

---

## Company Domain Synthesis — Your Organisation's Knowledge

Beyond generic engineering patterns, CORTEX can be configured with organisation-specific knowledge stored as structured configuration files. These domain profiles inject:

- Governance rules specific to your industry (PCI-DSS, OWASP, GDPR requirements)
- Expected architecture patterns for your technology platform
- Your team's key technologies and approved frameworks
- Priority signals that change how CORTEX ranks findings

When your team's domain profile is active, CORTEX doesn't just follow generic best practices — it follows *your* best practices. A security finding that is advisory for a generic application might be a blocking violation in a payments context, and CORTEX will enforce that distinction automatically.

---

## Intelligence in Practice — A Worked Example

A developer asks: "Add a password reset feature that sends an email with a time-limited token."

**Structure and History analyzers** reveal existing services: `UserService`, `EmailService`, `TokenService`. History shows `auth_service.py` changes frequently — it's a hot spot that warrants extra care.

**Security analyzer** flags requirements before implementation begins: tokens must be cryptographically secure, hashed before storage, and expire within 30 minutes. These findings are injected into the execution plan as mandatory constraints, not suggestions.

**Pattern analyzer** detects the existing service layer pattern at 0.91 confidence. Reasoning selects "test-first incremental" as the strategy — it has the highest success rate for service-layer additions in this codebase.

**Action layer** produces the plan: write failing tests for all scenarios first (happy path, expired token, invalid token, already-used token, rate limiting), implement minimum code to pass, then improve while keeping tests green.

The developer sees a clear plan before a single character is typed — grounded entirely in their actual codebase, not a generic template.

---

## Session Context Chain — LENS Remembers Every Turn

Most AI tools treat each request as an isolated event. CORTEX treats every request in a session as part of a continuous chain. Before running LENS analysis on your current request, CORTEX reads the last five requests you made in this session — what you asked, how they were classified, and in what order — and injects that history as enriched context into the current turn's analysis.

This means CORTEX understands *what you are building towards*, not just what you asked for right now.

### How It Works

Every request is persisted to a SQLite audit database **before it enters the pipeline** — even if the pipeline subsequently fails or times out. Each request record carries:

- A unique request ID and session-scoped sequence number
- The full text of your request (never truncated)
- A SHA-256 content hash for deduplication
- A parent request ID linking it to the previous request in this session
- Status transitions: `RECEIVED → PROCESSING → COMPLETED` (or `FAILED`)
- Intent classification and orchestrator routing chain

When a new request arrives, the `InteractionOrchestrator` queries this log for the prior five requests in the session, builds a compact context summary, and injects it into the LENS analysis. The LENS run then comprehends your current request *in the context of everything you have been working on*.

### What This Produces

A developer who asks "now add rate limiting" after a session implementing authentication endpoints receives LENS context that already understands the auth module, the service patterns established earlier in the session, and the security constraints that were applied to prior requests. CORTEX does not need to be told what "now" refers to — it already knows.

The chain linkage also creates a complete audit trail. Every request in a session can be reconstructed in sequence, with its outcome, its duration, and its classification — useful for understanding what was built in a session, debugging unexpected outcomes, and satisfying governance review requirements.

### Challenge Decisions — Persisted per Turn

When CORTEX raises a governance challenge against a request (because it detects a risk, an alternative approach, or a governance constraint), the challenge and the decision it produced are also persisted to the audit database — linked to the specific request ID that triggered it. This creates a traceable record of every risk evaluation and every decision made during the session.

---

## The Intelligence Matrix — Wiring Everything Together

The Intelligence Matrix is CORTEX's internal wiring map. It documents which intelligence-providing capabilities (LENS, Brain tiers, knowledge synthesis) are connected to which intelligence-consuming operations (test-driven development, governance enforcement, audit pipelines, debugging). Every cell in the matrix carries a priority — critical, high, medium, or low — ensuring that the most important connections are always established first.

The matrix is not documentation — it is a live contract that governance tools verify on every build. If a required connection is missing, the build fails.

---

*LENS analysis · Brain tier architecture · Session context chain · Intelligence matrix verified against live implementation*
