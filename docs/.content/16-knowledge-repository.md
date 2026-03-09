# The Knowledge Repository — Best Practices Across Every Facet of the SDLC

---
title: The CORTEX Knowledge Repository — Codified Best Practices for the Entire Software Lifecycle
type: explanation
audience: [Software Developers, Business Leaders, Product Owners, Curious Learners]
last_verified: 2026-03-09
order: 16
source_of_truth: cortex-registry/knowledge/INDEX.yaml
---

> **The central idea:** Most engineering teams reinvent best practices project by project — copying from Stack Overflow, recalling conference talks, or relying on whichever senior engineer happens to be in the room. CORTEX replaces this with a curated, machine-readable knowledge repository spanning 80+ structured YAML files across 14 domains. Every recommendation is versioned, traceable, and automatically surfaced at the moment a developer needs it — not buried in a wiki nobody reads.

---

## Why a Knowledge Repository Matters

Engineering best practices are not scarce. Every company has them somewhere — in onboarding documents, code review comments, architecture decision records, post-mortem reports, and the memories of experienced engineers. The problem is not knowledge creation. The problem is knowledge retrieval at the moment of decision.

When a developer is writing a new API endpoint, they should know your organisation's API versioning standard, the authentication pattern to use, the error handling convention, and the testing expectations — before they write a single line. When a team is planning a migration from WCF to microservices, they should have a proven strangler-fig migration playbook at their fingertips, not a blank whiteboard.

CORTEX's knowledge repository solves this by encoding best practices as structured YAML files that are automatically consulted during every operation. When you implement a feature, the relevant clean code standards, testing strategies, and security patterns are loaded into the intelligence context. When you review code, the code review checklist is applied automatically. When you plan a migration, the migration playbook for your specific technology stack is surfaced. Knowledge stops being passive documentation and becomes active guidance.

---

## Repository Structure — 14 Domains, 80+ Knowledge Files

The knowledge repository is organised into domains that mirror the software development lifecycle. Each domain contains one or more YAML files, and every file is registered in a central index (`cortex-registry/knowledge/INDEX.yaml`) that maps keywords and intent types to the appropriate knowledge source.

| Domain | Files | What It Covers |
|---|---|---|
| **SDLC Intelligence** | 10 | Analysis patterns, test strategy, code review, integration, security-by-design, documentation, stack-specific overrides |
| **Architecture** | 5 | Design patterns, SOLID principles, anti-patterns, refactoring quality standards, architecture best practices |
| **Security** | 6 | OWASP Top 10, secure coding practices, CI/CD hardening, secrets management, API security |
| **Testing & Validation** | 1 | TDD best practices, test strategy matrix, test category definitions |
| **Backend (Python)** | 3 | Clean code, code review, refactoring techniques |
| **Migration** | 12 | Technology-specific migration playbooks covering 12 common transitions |
| **Archetypes** | 13 | Repository classification patterns for automatic technology detection |
| **Domain Profiles** | 7 | Industry-specific governance rules (healthcare, finops, security-ops, auth, legal, ML, devops) |
| **Performance** | 1 | Profiling analysis and optimisation patterns |
| **DevOps & Infrastructure** | 1 | Monitoring and observability standards |
| **AI Practices** | 2 | AI adoption encouragement (150+ verified quotes), AI-augmented development practices |
| **Business Rules** | 1 | Extracted business rule templates |
| **Operational Patterns** | 3 | Proven success patterns, failure anti-patterns, model-tiering execution policy |
| **High-Value Principles** | 1 | 90 curated engineering principles across 10 domains |

The key design principle: **every knowledge file is independent**. No YAML file references another YAML file directly. All cross-domain relationships are managed exclusively by the central INDEX. This eliminates circular dependencies and ensures that adding, removing, or updating a knowledge file never breaks another.

---

## SDLC Intelligence — The Core Lifecycle Knowledge

The SDLC domain is the heart of the knowledge repository. It captures structured best practices for every phase of the software development lifecycle, from initial analysis through to production documentation.

### Analysis and Design Patterns

Before code is written, problems need decomposition. The analysis knowledge covers three systematic techniques: **Context Mapping** for identifying bounded contexts and team relationships, **Event Storming** for domain event discovery, and **LENS Analysis** — CORTEX's own workspace-aware code intelligence that reads the structure of your codebase before making any recommendation.

Architecture decisions are structured as Architecture Decision Records (ADRs) with explicit decision gates: Does this conform to your API standards? Does the infrastructure support this approach? Is this the simplest viable solution? What is the cost of reversing this decision if it proves wrong?

### Test Strategy Selection

Not every change needs the same testing approach. The test strategy knowledge provides a matrix that maps scenarios to testing requirements:

- **New features** require unit tests for every public method, integration tests for API endpoints and database interactions, and security tests for authentication boundaries.
- **Bug fixes** require a failing test that reproduces the exact bug *before* any fix is attempted, plus a regression test to prevent recurrence.
- **Refactoring** requires freezing all existing tests as a contract before the first change is made, then adding property-based tests for boundary conditions.
- **API endpoints** require OpenAPI schema validation, authentication tests (401, 403, 200), all error code coverage, and P99 latency assertions.
- **Database interactions** require transaction isolation, migration testing in both directions, and query plan assertions.

### Code Review Checklist

Code review criteria are classified by severity. P0 blocking checks cover security (no hardcoded secrets, all input sanitised, injection impossible by construction, PCI-DSS compliance) and data integrity (atomic transactions, idempotent mutations, no silent data loss). P1 required checks cover code quality (function length, complexity, type hints, docstrings) and API contracts (versioning, OpenAPI spec updates). P2 recommended checks cover performance (N+1 queries, blocking I/O) and readability.

### Integration Strategy

Integration testing has its own knowledge base covering contract testing (consumer-driven contracts using Pact), service virtualisation (the test double hierarchy from stubs through fakes, mocks, and spies), database test patterns (isolation, seeding with factories, schema migration testing), and performance thresholds (100ms for unit tests, 5 seconds for integration tests, 30 seconds for end-to-end tests).

### Security by Design

Security knowledge is not an afterthought section — it is a design-phase practice. The security-by-design guide provides a complete STRIDE threat modelling framework: data flow diagrams with trust boundaries, per-component threat analysis, DREAD risk scoring (scores of 12+ are P0 blocking; 8–11 are P1 sprint-required), mitigation mapping to OWASP references, and residual risk classification.

### Documentation Strategy

Documentation standards cover API documentation (OpenAPI 3.x, validated by spectral lint in CI), architecture decision records, code documentation (Google-style docstrings, "why not what" inline comments), runbooks (trigger, symptoms, steps, escalation, post-mortem), and README standards.

### Stack-Specific Overrides

Generic SDLC knowledge is further refined by four technology stack overlays:

| Stack | Coverage |
|---|---|
| **Python** | pytest, ruff, mypy, FastAPI, Django patterns |
| **TypeScript/JavaScript** | React, Next.js, Vitest, Jest, Playwright patterns |
| **.NET / C#** | ASP.NET Core, Entity Framework, xUnit, Blazor patterns |
| **HTML/CSS** | WCAG accessibility, Lighthouse performance, pa11y, Tailwind patterns |

When CORTEX analyses a codebase, the resolution order is: stack-specific knowledge overrides generic SDLC knowledge, which overrides domain-level knowledge, which overrides generic best practices. The most specific applicable guidance always wins.

---

## Architecture Knowledge — Patterns, Principles, and Anti-Patterns

### Design Patterns

The architecture domain includes a comprehensive catalogue of engineering design patterns — not as abstract theory, but as practical guidance with explicit "when to use" triggers, key concepts, and anti-patterns to avoid. Patterns include Domain-Driven Design, Microservices Architecture, and the nine enterprise patterns (Mediator, Strategy, Observer, Factory, Template Method, Chain of Responsibility, Adapter, Repository, Command) with detection heuristics.

### SOLID Principles

Each SOLID principle (Single Responsibility, Open-Closed, Liskov Substitution, Interface Segregation, Dependency Inversion) is documented with applicable intent types, so the right principle is surfaced for the right operation — refactoring triggers different SOLID guidance than initial implementation.

### Anti-Patterns

The anti-pattern catalogue serves as a "what not to do" complement to design patterns. Each anti-pattern includes detection signals (so CORTEX can flag them during analysis), consequences (what goes wrong if the anti-pattern persists), and refactoring paths (how to transform the anti-pattern into its healthy counterpart).

### Refactoring Quality Standards

Refactoring is not "clean up the code." The refactoring quality standards define scoring criteria for completeness, traceability, and structural improvement — ensuring that every refactoring operation leaves the codebase measurably better, not just cosmetically different.

---

## Security — Defence in Depth

Security knowledge spans six files covering the full depth of application security:

| File | Purpose |
|---|---|
| **OWASP Top 10** | All ten 2021 web application security risks with severity classification, detection regex patterns, and code-level scanning rules |
| **Secure Coding Practices** | Language-specific secure coding standards applied during implementation |
| **CI/CD Hardening** | Pipeline security — supply chain integrity, dependency scanning, signed artefacts |
| **Secrets Management** | Rotation policies, vault integration patterns, detection patterns for leaked credentials |
| **API Security** | OWASP API Security Top 10 for service-to-service and public API hardening |
| **Security by Design** | STRIDE/DREAD threat modelling integrated into the analysis phase (covered in SDLC above) |

Each OWASP risk includes machine-readable regex patterns that CORTEX uses during code analysis. For example, the Injection risk (A03) includes patterns for SQL string concatenation, dynamic shell execution, and `eval()` with dynamic input — these are checked automatically during every code review and audit operation.

---

## Migration Playbooks — 12 Proven Transition Guides

One of the most valuable sections of the knowledge repository for enterprise teams is the migration library. Each migration guide covers a common technology transition with a structured approach:

| Migration | Complexity | Strategy |
|---|---|---|
| **Selenium → Playwright** | Medium | Side-by-side execution, page-object migration |
| **WCF → REST API / Microservice** | High | Strangler fig + anti-corruption layer |
| **AngularJS → Angular** | High | ngUpgrade hybrid mode, module-by-module |
| **ASP.NET → ASP.NET Core** | High | Project-by-project re-platforming |
| **Entity Framework → EF Core** | Medium | Context migration, query translation |
| **jQuery → Modern Framework** | Medium | Component-by-component replacement |
| **Monolith → Microservices** | Very High | Domain decomposition, strangler fig |
| **SOAP → REST** | Medium | Contract mapping, parallel deployment |
| **On-Premises → Cloud** | High | Lift-and-shift → re-platform → re-architect |
| **SQL → NoSQL** | High | Data model transformation, dual-write |
| **JavaScript → TypeScript** | Medium | Incremental strictness, `.d.ts` stubs |
| **.NET Framework → .NET 8+** | High | Project SDK conversion, API compatibility |

Each guide includes an overview (source, target, typical duration, risk level), a phased migration strategy (discovery, architecture decision, implementation, cutover), contract mapping tables (how constructs in the old technology map to the new), and specific anti-patterns to avoid during the transition.

For example, the WCF-to-microservice guide maps `[ServiceContract]` interfaces to `[ApiController]` classes, `[OperationContract]` methods to HTTP verb attributes, and WCF data contracts to DTOs — with explicit guidance on handling duplex/callback contracts (WebSocket or SignalR), security model migration (Windows Auth to OAuth 2.0/JWT), and traffic cutover strategy (10% → 25% → 50% → 100% with rollback capability).

---

## Archetype Detection — Automatic Repository Classification

When CORTEX onboards a new repository, it does not ask the user what kind of project it is. It detects it automatically using weighted signal scoring defined in the archetype knowledge base.

Thirteen archetype profiles cover the most common software architectures:

| Archetype | Detection Signals |
|---|---|
| **.NET Monolith** | `.sln`, `.csproj`, `Global.asax`, `web.config` |
| **Microservices Mesh** | `docker-compose.yaml`, `k8s/`, `helm/`, Istio/Envoy references |
| **SPA Frontend** | `package.json` with React/Angular/Vue, `src/components/` |
| **Serverless** | `serverless.yml`, Lambda handler patterns, CDK/SAM templates |
| **Data Platform** | Jupyter notebooks, `requirements.txt` with pandas/spark |
| **ML Platform** | Model training scripts, MLflow, model registry references |
| **Event-Driven** | Kafka/RabbitMQ configuration, event handler patterns |
| **SaaS Multi-Tenant** | Tenant isolation patterns, subscription management |
| **Mobile Native** | Xcode/Android project files, platform-specific directories |
| **Legacy Batch** | Scheduled job configuration, batch processing scripts |
| **Embedded Systems** | Makefiles, cross-compilation configuration, hardware interfaces |
| **CLI Tooling** | Argument parsing, command registration patterns |

Each signal has a numeric weight. CORTEX sums the weights of matched signals and classifies the repository as the highest-scoring archetype. The classification then determines which knowledge files, governance rules, and analysis strategies are most relevant — a .NET monolith gets different guidance than a serverless application.

---

## Domain Profiles — Industry-Specific Governance

Seven domain profiles add industry-specific rules on top of the universal knowledge base:

| Profile | Key Standards |
|---|---|
| **Healthcare** | HIPAA compliance, PHI encryption (AES-256), access logging, data minimisation, de-identification |
| **FinOps** | Cloud cost governance, budget thresholds, resource tagging, cost anomaly detection |
| **Security Operations** | SOC procedures, incident response, threat detection, security monitoring |
| **Authentication** | SSO integration, identity management, token lifecycle, session security |
| **Legal** | Regulatory compliance, contract management, data retention policies |
| **Machine Learning** | Model governance, training data lineage, inference monitoring, bias detection |
| **DevOps** | CI/CD standards, infrastructure as code, deployment strategies, SLA/SLO management |

When a healthcare application is detected (or specified), the healthcare profile's rules are layered on top of the universal governance rules — PHI encryption becomes a P0 blocking check, access logging becomes mandatory, and data minimisation is enforced by construction.

---

## AI Development Practices — The Modern Engineering Companion

Two knowledge files address the intersection of AI and software development:

### AI-Augmented Development Practices

This file captures cross-repository AI coding standards extracted from onboarded projects. It catalogues supported AI vendors (GitHub Copilot, Cursor, Anthropic Claude, Aider, Amazon Q, Windsurf) with their detection files and instruction formats, enabling CORTEX to recognise and respect existing AI configuration in any repository it analyses.

### AI Adoption Sparks

A curated library of 150+ verified quotes and insights from software industry leaders and AI researchers — Jensen Huang, Sal Khan, Satya Nadella, and many others. These are not decoration. They are automatically injected into CORTEX responses when encouraging teams to adopt AI practices, providing real-world evidence that AI is a career amplifier, not a replacement.

---

## Operational Patterns — Lessons from Production

Three knowledge files capture operational wisdom distilled from real CORTEX production operations:

**Success Patterns** document strategies that consistently produce good outcomes: batch-verified deletion (delete in small batches with smoke gates between each), import chain verification before any deletion, compatibility shim migration (update all callers before removing the shim), index-driven knowledge resolution, and SRP decomposition by stage for monolithic files.

**Failure Patterns** document the inverse — common mistakes and their consequences, each with a corresponding prevention strategy. These feed directly into the Unified Reinforcement Signal (URS) system, where they are surfaced automatically when a developer is about to repeat a known mistake.

**Model-Tiering Execution Policy** addresses a specific architectural question: when is it safe to plan on a capable model and execute on a cheaper model? The answer is nuanced — safe only when execution is fully constrained by machine-readable specs with per-step validation and deviation-triggered escalation.

---

## High-Value Principles — The Engineering Conscience

The principles library contains 90 curated engineering principles across 10 domains: TDD, architecture, security, code quality, design, observability, performance, governance, collaboration, and universal. Each principle has a title, a concise body (200 characters maximum), domain tags, applicable intent types, and a relevance weight.

These principles are not reference documentation — they are automatically injected into analytical responses. When you ask CORTEX to investigate an architectural decision, a relevant architecture principle is surfaced. When you design a testing strategy, a TDD principle appears. One principle per response, always relevant, never repeated in consecutive responses. They function as an engineering conscience — a brief, authoritative reminder of the standard to hold before making a decision.

---

## How Knowledge Is Consumed

The knowledge repository is not a static reference that developers browse. It is a live intelligence layer consumed by CORTEX's orchestrators during every operation.

**Intent-based loading** — When a request is classified (implement, fix, refactor, audit, design, review), the central INDEX maps the intent to relevant knowledge domains. Only the applicable knowledge is loaded — an implementation request pulls clean code, TDD, and security; a migration request pulls the relevant migration playbook.

**Stack-aware resolution** — Knowledge is layered with increasing specificity. Generic SDLC principles form the base. Stack-specific overrides (Python, TypeScript, .NET, HTML/CSS) add language-specific guidance. Domain profiles add industry-specific rules. The most specific applicable guidance always takes priority.

**Automatic surfacing** — Developers do not need to search for knowledge. When writing code, the relevant clean code standards are already in the intelligence context. When reviewing, the code review checklist is already active. When auditing, the security patterns are already loaded. Knowledge appears at the moment of decision, not in a separate documentation portal.

**Keyword matching** — Every knowledge file is tagged with keywords in the central INDEX. The intelligence engine matches request context against these keywords to select the most relevant guidance, even when the intent classification is broad.

---

## Growing the Knowledge Base

The knowledge repository is designed to grow. New knowledge files follow a simple protocol:

1. Create a YAML file in the appropriate domain directory under `cortex-registry/knowledge/`
2. Register it in `cortex-registry/knowledge/INDEX.yaml` with title, path, and keywords
3. The file is immediately available to all orchestrators on the next operation

No code changes required. No deployment. No configuration update. The INDEX-driven architecture means that adding knowledge is a documentation task, not an engineering task — any team member who can write a YAML file can contribute to the organisation's collective intelligence.

This is the compounding advantage: every migration completed, every security incident analysed, every architecture decision evaluated adds to the knowledge base. The hundredth project benefits from every lesson learned across the first ninety-nine.
