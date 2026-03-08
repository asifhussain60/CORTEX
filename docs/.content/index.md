# CORTEX Architecture Documentation

---
title: CORTEX Architecture Overview
type: explanation
audience: [Business Leaders, Product Owners, Software Developers, Curious Learners]
last_verified: 2026-03-08
source_of_truth: cortex/ + cortex-registry/cortex-master.yaml + .github/copilot-instructions.md
format: diátaxis-explanation
voice: third-person-blended
---

> **Notice:** This documentation represents CORTEX as verified against live code. All module paths and capabilities are validated against the running codebase. CORTEX is under continuous evolution — specific counts may change as the platform grows.

---

## Executive Summary

### CORTEX: The AI Engineering Partner That Governs, Learns, and Delivers

CORTEX (**CO**gnitive **R**eal-**T**ime **EX**ecution) is a production-grade AI engineering framework that transforms how software teams build, test, and ship code. Think of it as a **development nervous system** — the way your brain coordinates sensory input, decision-making, and motor execution in milliseconds, CORTEX coordinates code analysis, governance enforcement, and workflow execution for every development request.

**The outcomes CORTEX delivers:**

- **Fewer defects reaching production** — governance gates enforce quality standards automatically on every commit, every build, and every release. No exceptions, no human oversight required.
- **Faster time-to-delivery** — automated test generation, structured execution plans, and parallel code intelligence eliminate hours of manual setup per feature.
- **Institutional memory that compounds** — every failure is analysed, every root cause is stored, and every prevention rule fires automatically when a similar situation arises. Knowledge grows with every sprint.
- **Complete audit trails on demand** — every decision, every governance check, and every test result is recorded in a tamper-evident database. Compliance evidence is generated automatically, not assembled manually before audits.
- **Consistent quality at scale** — whether your team is five engineers or fifty, the same governance rules, the same quality gates, and the same architectural standards apply uniformly across every line of code.

**What makes it architecturally different:**

- Traditional tools answer questions. CORTEX **orchestrates entire workflows** — from intent classification through test-driven development enforcement to governed code delivery.
- One canonical Python package, 320+ specialised processing engines across 15 domains, 55+ tools accessible directly in your IDE, and 55+ governance rules enforced at every stage.
- Test-driven development is not optional. Tests are written before implementation on every feature and every bug fix — enforced structurally, not by policy.
- Everything is Git-backed. No external databases, no cloud dependencies for development — just structured configuration files versioned alongside your code.

**Think of it like a human brain:** Your brain doesn't just *hear* a request — it perceives the context, reasons about the best approach, decides on a plan, executes it, and *remembers* what worked for next time. CORTEX works the same way. It perceives your codebase (the sensory system), reasons about the best strategy (the thinking centre), acts on a structured plan (the motor system), and stores lessons learned (long-term memory). Every part works in concert — just like your brain coordinates sight, thought, and action without you consciously managing each step.

---

## Platform Capabilities at a Glance

| Capability | What It Means for Your Team |
|---|---|
| **320+ specialised processing engines** | Every category of engineering work — building, testing, auditing, debugging, security, planning — has a dedicated expert engine |
| **55+ IDE-accessible tools** | All CORTEX capabilities available directly in your coding assistant — no context switching, no separate applications |
| **55+ governance rules** | Quality standards enforced automatically at every commit, build, and deployment — not dependent on code reviewers remembering to check |
| **6 programming languages** | Deep analysis across Python, TypeScript, JavaScript, C#, SQL, and HTML — including framework-specific understanding for Angular, React, and Vue |
| **30+ request types understood** | From "implement this feature" to "debug this failure" to "audit this codebase" — CORTEX classifies and routes every request to the right specialist |
| **4 root cause methodologies** | Failures are analysed structurally, stored permanently, and prevented from recurring — institutional memory that grows with every sprint |
| **9 resilience patterns** | Circuit breakers, bulkheads, graceful degradation — production-grade infrastructure in the framework itself |
| **95+ workflow templates** | Codified best practices across 17 categories — from TDD enforcement to production audits — assembled from reusable building blocks |
| **Interactive dashboards** | On-demand visual reporting of codebase health, quality trends, and architecture maps — generated automatically from live analysis |
| **Repository onboarding** | Any new codebase can be analysed, profiled, and governed within minutes — no manual setup of rules or configurations |
| **Privacy-safe synchronisation** | Code can be synchronised between private and shared repositories with automatic stripping of sensitive metadata |

---

### Architecture at a Glance

CORTEX is structured around three interconnected pillars working in concert — like the major regions of a human brain that cooperate on every thought and action.

The **MCP Gateway** is the sensory interface — like your eyes and ears. It exposes 55+ tools directly in your coding assistant, providing the doorway through which every request enters the system. Just as your senses receive signals from the outside world, the gateway receives requests from your IDE.

The **Orchestration Layer** is the motor cortex — the part of the brain that coordinates action. It routes requests through 320+ specialised processing engines across 15 domains — from core coordination through domain specialists to operational support. Like the motor cortex coordinating thousands of muscle fibres to pick up a cup, the orchestration layer coordinates dozens of specialist engines to deliver a complete result.

The **Intelligence Layer** is the thinking centre — combining code analysis (LENS), three tiers of reasoning (Perception, Reasoning, Action), and a continuous learning system that improves with every interaction. Like the prefrontal cortex that weighs options, considers history, and makes decisions, this layer turns raw data into intelligent action.

Underpinning all three pillars are the **Governance Registry** (55+ rules enforced at every stage), the **Testing Infrastructure** (19,000+ tests in a comprehensive parallel test suite), and the **Git-Backed Configuration Store** (all rules, templates, and knowledge versioned as YAML alongside your code).

---

### What Each Role Experiences

**Business Leader:** "I see a platform where governance rules are automatically enforced on every commit across all teams. Test quality is scored, and anything below the threshold is flagged before it reaches production. Compliance evidence is generated continuously — not assembled in a panic before the next audit. I can quantify the reduction in rework, the improvement in delivery cadence, and the elimination of recurring failures."

**Product Owner:** "When I request a feature, I know tests are written before implementation — not by policy, but by the system itself. Acceptance criteria become test cases automatically. Work items from our tracking system are pulled directly into the developer's context, so nothing is lost between the planning board and the code. I never chase test coverage or governance compliance — it's structural."

**Software Engineer:** "I type a request in my IDE. CORTEX classifies my intent, runs parallel code analysis, enforces governance, and executes the right workflow — all within seconds. Every operation teaches the system what works for our codebase. When something fails, root cause analysis stores the lesson permanently. Everything imports from one package, everything is testable, and every action has a rollback point."

**Curious Learner:** "I see a living reference for how professional engineering teams actually operate. Every capability demonstrates a principle I'm learning — test-driven development, clean architecture, security by design, root cause analysis. I can follow structured learning paths from beginner to advanced, all grounded in real governance rules and real code patterns."

---

*CORTEX · Cognitive Real-Time Execution · Source of truth: `cortex-registry/cortex-master.yaml`*

## Where to Go Next

| I want to understand… | Read this |
|-----------------------|-----------|
| What CORTEX is — one page | `01-platform-what-is-cortex.md` |
| How CORTEX analyses code | `02-intelligence-how-cortex-understands-code.md` |
| Governance and quality enforcement | `03-governance-quality-that-enforces-itself.md` |
| Test-driven development | `04-tdd-quality-flywheel.md` |
| Orchestration architecture | `05-orchestration-the-engine-room.md` |
| IDE tools (MCP gateway) | `06-mcp-tools-in-your-ide.md` |
| Security | `07-security-built-in-not-bolted-on.md` |
| Learning and institutional memory | `08-learning-institutional-memory.md` |
| Full delivery lifecycle | `09-lifecycle-from-idea-to-production.md` |
| Infrastructure and resilience | `10-infrastructure-built-to-last.md` |
| Enterprise patterns and knowledge | `11-patterns-knowledge-architecture.md` |
| AI efficiency and context management | `12-ai-efficiency-context-management.md` |
| Getting started (5 minutes) | `13-getting-started.md` |
| Frequently asked questions | `14-faq.md` |
| Glossary | `glossary.md` |

---

*CORTEX · Cognitive Real-Time Execution · Comprehensive orchestration, governance, and intelligence · Source of truth: `cortex-registry/cortex-master.yaml`*

