# Patterns and Knowledge — The Intelligence Behind the Intelligence

---
title: Enterprise Patterns and Knowledge Architecture
type: explanation
audience: [Software Developers, Business Leaders, Product Owners, Curious Learners]
last_verified: 2026-03-02
order: 11
---

> **The central idea:** CORTEX doesn't just enforce rules — it understands architecture. It recognises the structural patterns that distinguish well-designed systems from poorly-designed ones, and it knows why each pattern matters, what problems it solves, and when to recommend it. This architectural awareness is built from a curated knowledge base that grows with every project.

---

## Why Pattern Recognition Changes Everything

Most code quality tools work syntactically — they check formatting, flag missing type hints, or count lines per function. These checks are valuable but shallow. They cannot detect an architectural anti-pattern, identify a system design that will become unmaintainable at scale, or suggest a structural refactoring that would eliminate an entire class of future bugs.

CORTEX works architecturally. Its code intelligence layer recognises the structural patterns underlying any codebase — the same patterns that experienced software architects look for when assessing system quality. When CORTEX detects a pattern, it can evaluate whether the implementation is idiomatic, identify deviations that suggest fragility, and recommend specific improvements.

---

## The Nine Enterprise Patterns

CORTEX's knowledge base includes detailed understanding of nine foundational enterprise software patterns. For each pattern, the knowledge base captures: what problem it solves, what canonical implementation looks like across languages, what deviations indicate poor implementation, and what transformation steps move a poor implementation to a good one.

| Pattern | Core Purpose | Detected When |
|---|---|---|
| **Mediator** | Centralises complex object interactions to reduce coupling | Multiple objects that directly orchestrate each other's behaviour |
| **Strategy** | Encapsulates interchangeable algorithms behind a common interface | Conditional logic selecting between different processing approaches |
| **Observer** | Notifies interested parties of state changes without tight coupling | Objects polling for changes or tightly coupled event notification |
| **Factory** | Centralises object creation logic and abstracts construction complexity | Scattered `new` calls or complex construction logic in consumers |
| **Template Method** | Defines an algorithm skeleton, letting subclasses fill in specific steps | Duplicated algorithm structure with minor variations |
| **Chain of Responsibility** | Passes requests along a chain of handlers until one processes it | Long conditional chains checking object types or request properties |
| **Adapter** | Makes incompatible interfaces work together without modifying either | Translation logic scattered across callers of a component |
| **Repository** | Abstracts data persistence behind a consistent query interface | Business logic directly referencing database constructs |
| **Command** | Encapsulates a request as an object, enabling undo, queuing, and logging | Ad-hoc method calls that cannot be tracked, reversed, or queued |

---

## How Pattern Detection Works

Pattern detection is not keyword matching or simple structural checks. CORTEX analyses the semantic relationships between classes, functions, and modules — identifying the structural signature of each pattern regardless of naming conventions or implementation style.

Detection produces a **confidence score** for each identified pattern instance. High-confidence detections (above 80%) are used directly for recommendations. Medium-confidence detections (50–80%) are flagged for developer review. Low-confidence detections are logged but not surfaced as recommendations.

Importantly, CORTEX detects both **positive patterns** (well-implemented architectural patterns that should be preserved) and **anti-patterns** (common structural mistakes that predict future quality problems). Anti-pattern detection is used to generate targeted recommendations — not just "this is bad" but "here is the specific refactoring that would address it."

---

## Two Knowledge Stores Working Together

CORTEX maintains two complementary knowledge stores that together provide a complete picture of architectural knowledge.

### The Universal Knowledge Base

The universal knowledge base is the canonical source of software engineering principles — the architectural patterns, security best practices, testing approaches, and language-specific idioms that apply to any codebase in any context. This knowledge is curated, version-controlled, and updated as the engineering community's understanding evolves.

The universal knowledge base answers questions like: "What does a well-implemented Repository pattern look like in Python?" or "What are the security implications of this approach to authentication?" The answers come from codified engineering principles, not from statistical inference — so they are reliable, explainable, and consistent.

### The Company Domain Knowledge Base

The company domain knowledge base captures the specific architectural decisions, domain language, business rules, and implementation conventions of your organisation's codebase. This knowledge is extracted automatically by the code intelligence layer and augmented by explicit documentation your team provides.

The company domain knowledge base answers questions like: "How does our team implement the Repository pattern?" or "What is the naming convention for our service layer?" These answers reflect your specific context — meaning recommendations respect your existing architecture rather than imposing generic patterns that conflict with your established conventions.

### Knowledge Resolution Priority

When CORTEX formulates a recommendation, it combines both knowledge stores using a priority hierarchy:

1. **Company-specific overrides** — explicit conventions your team has defined take highest priority
2. **Company-observed patterns** — patterns consistently observed across your codebase
3. **Universal best practices** — the canonical engineering principles from the universal knowledge base
4. **Language defaults** — language-specific idioms and conventions

This hierarchy ensures recommendations feel native to your codebase, not generic and disconnected.

---

## Sharpen the Saw — Learning from Real Migrations

A critical part of CORTEX's pattern knowledge comes from hands-on codebase migrations. The demonstration repositories — informally called "Sharpen the Saw" — provide concrete before-and-after examples of architectural transformation.

### The Transformation Journey

The demonstration begins with a realistic monolithic codebase containing common architectural problems: mixed concerns, direct dependencies, scattered logic, inconsistent patterns, and limited testability. These are the problems CORTEX is designed to detect.

CORTEX analyses the monolith, identifies the structural issues, and generates a prioritised transformation plan. The plan is executed step by step — each step preserving behaviour while improving structure. The completed refactored codebase demonstrates the same functionality with clean pattern implementation, high test coverage, and full governance compliance.

### What Teams Learn From This

The Sharpen the Saw journey is instructive in several ways:

**Pattern recognition in practice** — developers see how CORTEX identifies patterns in ambiguous real-world code, not idealised examples.

**Transformation sequencing** — some refactorings must precede others. The demonstration shows the dependency graph of structural improvements.

**Governance compliance as a target state** — the completed refactoring passes all governance gates. The journey from legacy to compliant codebase is traceable and reproducible.

**Test coverage growth** — the demonstration tracks test coverage at each step, showing how structural improvements unlock test coverage gains that were impossible in the monolithic form.

---

## Pattern-Driven Recommendations in Practice

When a developer requests a code review, a feature implementation, or a quality assessment, the pattern knowledge base directly shapes the output:

A recommendation to **extract an interface** comes with a reference to the specific pattern it implements, the problem it addresses, and the concrete refactoring steps — not just a generic suggestion.

A recommendation to **consolidate conditional logic** comes with the alternative pattern (Strategy or Chain of Responsibility), the rationale for the choice, and a sketch of the transformed structure.

A recommendation to **separate a data access concern** comes with the Repository pattern as context — explaining not just what to do but why the pattern exists and what future flexibility it enables.

---

## Knowledge Updates — Evolving With the Codebase

As your codebase evolves, the company domain knowledge base evolves with it. New conventions observed consistently across the codebase are incorporated. Deprecated patterns are flagged. Architecture decisions documented in code are extracted and formalised.

This continuous knowledge update means that CORTEX's recommendations remain relevant as your team makes decisions, as your architecture matures, and as your codebase grows. Knowledge drift — where a documentation system falls behind the actual state of the codebase — is detected and surfaced for remediation.

---

## For Curious Learners

The patterns and knowledge architecture in CORTEX demonstrates a principle that distinguishes senior engineers from junior ones: the ability to recognise structural patterns in unfamiliar code. When an experienced architect reviews a codebase, they don't read every line — they recognise the shapes. "This is a Repository pattern. This is a Strategy pattern. This mediator is incomplete."

CORTEX codifies that pattern recognition capability. Studying how CORTEX detects, scores, and recommends patterns teaches you to see architecture the way experienced architects see it — not as isolated classes and functions, but as structural signatures that predict quality, maintainability, and extensibility.

---

*Pattern knowledge architecture verified against enterprise patterns registry and knowledge engine implementation*
