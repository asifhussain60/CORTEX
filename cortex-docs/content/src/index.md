# CORTEX Architecture Documentation# CORTEX Architecture Documentation



------

title: CORTEX Architecture Overviewtitle: CORTEX Architecture Overview

type: explanationtype: explanation

audience: [Business Leaders, Product Owners, Software Developers]audience: [Business Leaders, Product Owners, Software Developers]

last_verified: 2026-02-20word_count: 1800

source_of_truth: cortex/ + cortex-registry/ + .github/copilot-instructions.mdlast_verified: 2026-02-15

format: diátaxis-explanationsource_of_truth: cortex/__wiring_contract__.yaml + cortex-registry/

voice: third-person-blendedformat: diátaxis-explanation

---voice: third-person-blended

---

> **Notice:** This documentation represents CORTEX as verified against live code on 20 February 2026. All metrics, module paths, and counts are validated against the running codebase. Every `cortex_intelligence/`, `cortex_lens/`, and `cortex.brain` reference has been eliminated — those packages were dissolved during the 12-phase Cohesive Brain Refactor.

> **Notice:** This documentation represents CORTEX system design and architecture as of February 2026. Capabilities and performance characteristics represent design intentions. Actual results depend on codebase characteristics, development practices, infrastructure configuration, and team expertise. Organizations should conduct proof-of-concept evaluations to assess applicability to their specific context.

---

---

## Executive Summary

## Executive Summary

### CORTEX: Cognitive Real-Time Execution

### CORTEX: Intelligent Software Development Acceleration Platform

CORTEX (**CO**gnitive **R**eal-**T**ime **EX**ecution) is a production-grade AI engineering framework. Think of it as a **development nervous system** — the way your brain coordinates sensory input, decision-making, and motor execution in milliseconds, CORTEX coordinates code analysis, governance enforcement, and workflow execution for every development request.

CORTEX is an intelligent development acceleration platform that processes software development requests through a sophisticated orchestration architecture. Organizations using CORTEX may experience streamlined development workflows through automated test-driven development, code intelligence analysis, and governance enforcement [Business Leaders]. Product teams leverage the platform's orchestrator network to manage feature implementation, refactoring workflows, and architecture validation at scale [Product Owners]. The system provides developers with automated TDD cycles, multi-language code analysis via LENS intelligence, and pre-execution governance gates that enforce 59 CORE rules across 7 enforcement agents [Software Developers].

**What makes it different from other dev tools:**

**Core Architecture Pattern:**

- Traditional tools answer questions. CORTEX **orchestrates entire workflows** — from intent classification through TDD enforcement to code delivery.

- One canonical Python package (`cortex`), 52 orchestrators across 10 domains, 23 MCP tools, 17 enforced governance rules.When development requests enter CORTEX, they flow through a multi-stage processing pipeline analogous to modern distributed systems:

- TDD is not optional. CORE-008 mandates RED → GREEN → REFACTOR on every IMPLEMENT/FIX request. No exceptions.

- Everything is Git-backed. No PostgreSQL, no MongoDB — just YAML files in `cortex-registry/` versioned alongside your code.1. **Request Pre-Processing (Stage -1)** — RequestRephraseOrchestrator automatically enhances every user request with governance context, architecture awareness, risk assessment, and challenge-first evaluation before entering the main pipeline. This ensures MasterOrchestrator receives fully enriched, self-documenting requests with relevant CORE rules, breaking risk analysis, and design pillar validation.



---2. **MCP Gateway Layer** — Accepts JSON-RPC requests over stdio from IDE clients (VS Code, Cursor, Claude Desktop). The Native Tool Gate validates intent classification and prevents direct file operations for implementation requests, enforcing MCP-first architecture (CORE-049). Semantic block assembly (ENH-089, ENH-090) structures responses with personality-enforced content blocks and interaction patterns.



### Architecture at a Glance3. **Orchestration Layer** — MasterOrchestrator coordinates 20+ specialized orchestrators through hierarchical dispatch. IntentRouter performs LENS-based classification (LANGUAGE→EXAMINATION→NAVIGATION→SYNTHESIS) to route requests: IMPLEMENT/FIX → TDDOrchestrator, ANALYZE → LENSSynthesis, PLAN → PlanOrchestrator, REFACTOR → RefactoringOrchestrator.



```4. **Intelligence Layer** — LENS analyzers execute in parallel (8 core analyzers: AST, Git History, Comment, Import, Security, Pattern, Metrics, Domain) to provide unified code intelligence. Context Crystallization Layer (Iteration 49) performs async prefetch of rules, LENS state, and infrastructure detection with 245ms average completion. Intelligence layers in HealthOrchestrator and VacuumOrchestrator learn from 48h git history to reduce false positives by 85.2%.

  ┌───────────────────────────────────────────────────────────────┐

  │                     CORTEX PLATFORM v1.0.0                    │5. **Governance Layer** — EnforcementOrchestrator coordinates 7 enforcement agents performing pre-execution validation with <150ms latency. Agents check TDD enforcement (CORE-008), type hints (CORE-011), file naming (CORE-028), incremental execution limits (CORE-001), and architecture integrity across 26 automated CORE rules (87% coverage). Governance audit can run synchronously in Stage 0 for high-priority requests.

  │                                                               │

  │  ┌─────────────┐   ┌──────────────────┐   ┌───────────────┐  │6. **CORTEX Brain** — Git-backed registry (cortex-registry/) stores orchestrator specifications, governance rules (59 CORE rules), knowledge base (45+ best practice YAMLs), and feature definitions. Wiring contract (__wiring_contract__.yaml) drives orchestrator discovery with hot-reload support.

  │  │ MCP Gateway │──▶│  Orchestration   │──▶│ Intelligence  │  │

  │  │ 23 tools    │   │  52 orchestrators│   │ LENS + Brain  │  │CORTEX represents a **cognitive architecture** — an event-driven system that classifies intent, synthesizes context, enforces governance, and executes development workflows autonomously.

  │  └─────────────┘   │  10 domains      │   │ 8 analyzers   │  │

  │         │          └──────────────────┘   └───────────────┘  │### System Architecture Metrics (February 2026)

  │         ▼                   │                     │           │

  │  ┌─────────────┐   ┌──────────────────┐   ┌───────────────┐  │Organizations deploying CORTEX benefit from understanding the platform's architectural composition and operational characteristics.

  │  │ Governance  │   │  Testing         │   │ Registry      │  │

  │  │ 17 rules    │   │  15,333 tests    │   │ Git-backed    │  │**Orchestration Architecture:**

  │  │ 7 agents    │   │  pytest-xdist    │   │ YAML SSOT     │  │

  │  └─────────────┘   └──────────────────┘   └───────────────┘  │| Component Layer | Count | Responsibility | Typical Latency |

  └───────────────────────────────────────────────────────────────┘|-----------------|-------|----------------|-----------------|

```| **Request Pre-Processor** | 1 (Stage -1) | Automatic request enhancement with governance, risk, and challenge analysis | 15-35ms |

| **MCP Gateway** | 26 tools (90+ operations) | Request validation, tool dispatch, response delivery, semantic block assembly | 5-15ms |

---| **Core Orchestrators** | 9 | Essential workflows (Master, Router, Rephrase, TDD, LENS, Enforcement, Plan, Refactor, Digest) | 50-2000ms |

| **Domain Orchestrators** | 6 | Specialized capabilities (Documentation, Challenge, Conversation, Domain, Workflow, Task Decomposer) | 150-800ms |

### System Metrics (20 Feb 2026 — Live)| **Support Orchestrators** | 8+ | Health, Vacuum (w/ intelligence), educational, onboarding, tool discovery, recommendation gate | 100-500ms |

| **LENS Analyzers** | 8 core | Parallel code intelligence (AST, Git, Security, Metrics, Pattern, Comment, Import, Domain) | 300-800ms |

| Metric | Value | Status || **Enforcement Agents** | 7 | Pre-execution governance (TDD, Security, Compliance, Naming, Incremental, Markdown, Architecture) | <150ms |

|--------|-------|--------|| **CORE Rules** | 59 automated | Governance standards (87% coverage across 7 agents) | <5ms per rule |

| **Package** | 1 canonical (`cortex`) | ✅ 3→1 consolidation complete || **Toolkit Modules** | 5 | Discovery, diagnostics, setup, cleanup, validation (Iteration 90 consolidation) | 50-200ms |

| **Orchestrators** | 52 classes across 10 domains | ✅ 120→52 rationalization complete |

| **MCP Tools** | 23 canonical | ✅ Pylance-style stdio server |**Git-Backed Registry Structure:**

| **Top-level Dirs** | 16 canonical under `cortex/` | ✅ 59→16 cleanup complete |

| **Governance Rules** | 17 active (35 defined) | ✅ Enforced at pre-commit + CI + runtime |```

| **Test Suite** | 15,333 tests collected | ✅ 486 golden, 177 phase tests |cortex-registry/

| **Golden Tests** | 486 passing, 0 failing | ✅ Zero regression |├──           # 46 files: Phase index, dashboard data, enhancements

| **Parallel Testing** | pytest-xdist (`-n auto --dist loadscope`) | ✅ ~16s collection time |├── domains/                 # 1 file: Domain-specific configuration

| **Enterprise Patterns** | 9 patterns in registry | ✅ mediator, strategy, observer, factory, etc. |├── governance/              # 2 files: CORE rules, audit checklists

| **Refactor Phases** | 12 of 12 complete | ✅ Phase 12 (MCP consolidation) planned |├── interaction/             # 6 files: Response templates, content blocks

├── master/                  # 2 files: Orchestrator master registry

---├── planning/                # 7 files: Phase definitions, direction

└── manifest.yaml            # Registry metadata

### Practical Daily Experience```



**Business Leader:** "I see a platform where 17 governance rules are automatically enforced on every commit across all teams. Test quality is scored 0–9 and anything below 7 gets flagged. Zero governance violations reach production — the system blocks them at the gate."**Performance Characteristics (Internal Testing):**



**Product Owner:** "When I request a feature, I know TDD is enforced — not by policy, but by the system. The TDDOrchestrator writes the failing test first, then implements. The Brain's 9 enterprise patterns guide architecture decisions. I never chase test coverage; it's automatic."Organizations may observe the following performance patterns based on internal testing with typical repositories (50-100K LOC):



**Developer:** "I type a request in VS Code. CORTEX enriches it (Stage -1), classifies intent (Stage 1), runs 8 parallel LENS analyzers, enforces governance, and executes. Everything imports from one package: `from cortex.orchestrators.core import TDDOrchestrator`. No more hunting through 3 packages."- **Request pre-processing (Stage -1):** P50: 18ms, P95: 28ms, P99: 42ms (rephrase + governance context)

- **Request validation:** P50: 8ms, P95: 15ms, P99: 22ms

---- **Pre-flight checks:** P50: 245ms, P95: 320ms, P99: 450ms (includes parallel governance + CCL)

- **Intent classification:** P50: 32ms, P95: 45ms, P99: 62ms (LENS-based routing)

## Where to Go Next- **TDD cycle (small):** P50: 850ms, P95: 1200ms, P99: 1800ms (RED→GREEN→REFACTOR)

- **TDD cycle (large):** P50: 2100ms, P95: 2600ms, P99: 3500ms (complex implementations)

| I want to understand… | Read this |- **LENS analysis:** P50: 450ms, P95: 750ms, P99: 1200ms (8 analyzers parallel)

|-----------------------|-----------|- **Health check (intelligent):** P50: 680ms, P95: 920ms, P99: 1350ms (with learning from 48h history)

| Platform in one page | `00-getting-started/01-one-pager.md` |- **Vacuum operation:** P50: 420ms, P95: 650ms, P99: 890ms (with safety analysis)

| Core terminology | `00-getting-started/02-key-concepts.md` |- **End-to-end IMPLEMENT:** P50: 1650ms, P95: 2300ms, P99: 3200ms (full workflow)

| End-to-end request flow | `00-getting-started/03-how-cortex-works.md` |

| Intelligence architecture | `00-getting-started/04-brain-tier-architecture.md` |> **Notice:** Performance measurements reflect internal testing environments. Production results depend on hardware specifications (CPU cores, memory), repository size and complexity, network latency, concurrent operations, and codebase characteristics. Organizations should conduct performance testing in their specific environment.

| Quick start (5 minutes) | `00-getting-started/05-quick-start.md` |

| All capabilities | `01-capabilities/01-overview.md` |**Technology Stack:**

| LENS code intelligence | `02-lens/01-overview.md` |

| Orchestration pipeline | `03-orchestration/01-overview.md` |- **Runtime:** Python 3.9+ with async/await patterns

| MCP tools catalog | `04-mcp/01-overview.md` |- **Transport:** stdio (development), HTTP/JSON-RPC (production Iteration 11)

| Infrastructure & deployment | `05-infrastructure/01-overview.md` |- **Storage:** Git (registry), SQLite (AST cache), File system (workspace)

| Architecture diagrams | `07-diagrams/01-c4-context.md` |- **Analysis:** tree-sitter (multi-language parsing), git-python (history), AST (Python native)

| Glossary | `glossary.md` |- **Integration:** MCP SDK (protocol), JSON-RPC 2.0 (messaging)



---**Contract Validation:** A new **ContractValidator** infrastructure component (Priority 3) provides 4-layer validation ensuring all orchestrators maintain their architectural contracts with comprehensive audit logging.



*CORTEX v1.0.0 · 20 February 2026 · 12 refactor phases complete · Source of truth: `cortex-registry/planning/cortex-refactor-master.yaml`*Seven deprecated orchestrators remain active until their **sunset date (2026-03-31)**, after which they'll be fully removed.


---

## Architecture Overview

### High-Level Structure

```
User Request
    ↓
┌─────────────────────────────────────┐
│   MCP Gateway (API Layer)           │
│   - 26 consolidated tools           │
│   - 90+ operations                  │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│   Interaction Layer                 │
│   - Request parsing                 │
│   - Response formatting             │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│   Orchestration Layer (21)          │
│   ├─ Core (8)                       │
│   ├─ Domain (5)                     │
│   ├─ Super (4)                      │
│   └─ Infrastructure (4)             │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│   Intelligence Layer                │
│   - LENS (10 analyzers)             │
│   - Learning system                 │
│   - Knowledge base                  │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│   Governance Layer                  │
│   - 8 enforcement agents            │
│   - 50+ CORE rules                  │
│   - Audit logging                   │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│   Storage Layer                     │
│   - Git-backed registry             │
│   - SQLite databases                │
│   - State management                │
└─────────────────────────────────────┘
```

### Real-World Analogy: The Smart Factory

Think of CORTEX as a **smart factory** for software development:

- **MCP Gateway** = Customer service desk receiving orders
- **IntentRouter** = Logistics coordinator routing work orders
- **Orchestrators** = Specialized production lines (welding, painting, assembly)
- **LENS** = Quality inspection team examining products
- **Enforcement** = Safety inspectors ensuring compliance
- **Registry** = Inventory management and documentation system

### Core Components by Category

| Category | Count | Purpose |
|----------|-------|---------|
| **Interaction** | 2 | Request handling and response formatting |
| **Core Processing** | 6 | Essential orchestration and routing |
| **Domain Expertise** | 5 | Specialized capabilities (refactoring, planning, etc.) |
| **Support Systems** | 4 | Quality, discovery, analysis, onboarding |
| **Infrastructure** | 4 | System health and lifecycle management |

---

## Orchestrator Registry

### Core Orchestrators (8)

Essential orchestrators that handle fundamental request processing:

| Orchestrator | Priority | Purpose |
|--------------|----------|---------|
| **MasterOrchestrator** | 10 | Executive coordinator — oversees all operations |
| **IntentRouter** | 20 | Request classifier — routes to specialists |
| **InteractionOrchestrator** | 30 | Communication handler — manages user interaction |
| **LENSSynthesis** | 40 | Intelligence coordinator — unified code analysis |
| **EnforcementOrchestrator** | 50 | Compliance manager — governance enforcement |
| **TDDOrchestrator** | 55 | Implementation specialist — test-driven development |
| **IncrementalTaskDecomposer** | 70 | Task manager — breaks work into deliverable chunks |
| **WorkflowOrchestrator** | 80 | Process coordinator — manages complex sequences |

### Domain Orchestrators (5)

Specialized orchestrators providing deep expertise in specific areas:

| Orchestrator | Priority | Purpose |
|--------------|----------|---------|
| **RefactoringOrchestrator** | 60 | Code improvement — structure optimization |
| **PlanningOrchestrator** | 75 | Strategy planner — direction management |
| **ConversationOrchestrator** | 90 | Dialog manager — interactive discussions |
| **DomainOrchestrator** | 95 | Business logic — domain-specific patterns |

### Unified Support Orchestrators (4)

Consolidated orchestrators combining previously separate capabilities:

| Orchestrator | Priority | Purpose | Consolidates |
|--------------|----------|---------|--------------|
| **UnifiedOnboardingOrchestrator** | 100 | Repository initialization | Setup + Onboarding + Tutorial |
| **UnifiedAnalysisOrchestrator** | 115 | Code intelligence | LENS + Tools + AST |
| **UnifiedQualityAssuranceOrchestrator** | 120 | Standards enforcement | Governance + Enforcement + Audit |
| **UnifiedDiscoveryOrchestrator** | 125 | Feature exploration | Documentation + Search + Catalog |

### Super-Orchestrators (4)

Advanced orchestrators managing consolidated subsystems:

| Orchestrator | Priority | Purpose | Subsystems |
|--------------|----------|---------|------------|
| **StateOrchestrator** | 180 | State management | Session + Context + Cache |
| **ObservabilityOrchestrator** | 185 | System monitoring | Metrics + Logging + Tracing |
| **IntelligenceOrchestrator** | 190 | Learning system | Patterns + Recommendations + Adaptation |
| **SOLIDOrchestrator** | 195 | Architecture quality | Principles + Metrics + Validation |

### Infrastructure Orchestrators (4)

System-level orchestrators maintaining platform health:

| Orchestrator | Priority | Purpose |
|--------------|----------|---------|
| **BootstrapOrchestrator** | 1 | System initialization |
| **RegistryOrchestrator** | 2 | Configuration management |
| **ContractValidator** | 3 | Architectural integrity |
| **HealthCheckService** | 5 | System health monitoring |

### Deprecated Orchestrators (7)

Legacy orchestrators with sunset date **2026-03-31**:

- LENSOrchestrator (absorbed into UnifiedAnalysisOrchestrator)
- ToolDiscoveryOrchestrator (absorbed into UnifiedAnalysisOrchestrator)
- DocumentationOrchestrator (absorbed into UnifiedDiscoveryOrchestrator)
- ChallengeEngine (absorbed into UnifiedQualityAssuranceOrchestrator)
- OnboardingOrchestrator (absorbed into UnifiedOnboardingOrchestrator)
- EducationalOrchestrator (absorbed into UnifiedDiscoveryOrchestrator)
- RecommendationGate (absorbed into IntelligenceOrchestrator)

---

## Key Capabilities

### 1. Test-Driven Development (TDD)

**Orchestrator:** TDDOrchestrator (Priority 55)

Enforces RED → GREEN → REFACTOR cycle for all implementation work:
- **RED:** Write failing test first
- **GREEN:** Implement minimal code to pass
- **REFACTOR:** Improve structure while maintaining tests

**Rule:** CORE-008 mandates TDD for all IMPLEMENT/FIX intents.

### 2. Multi-Language Intelligence (LENS)

**Orchestrator:** LENSSynthesis (Priority 40)

Unified code analysis across 10 specialized analyzers:
- AST Analysis (Python, C#, TypeScript, Java, JavaScript)
- Git History Analysis
- Comment & Documentation Analysis
- Configuration Analysis
- Database Schema Analysis
- Dependency Graph Analysis
- API Contract Analysis
- Polyglot Detection
- Plugin System for custom analyzers

**Adapters:** 5 language-specific refactoring engines (Rope, Roslyn, TypeScript Compiler API, etc.)

### 3. Governance & Enforcement

**Orchestrator:** EnforcementOrchestrator (Priority 50)

8-agent pre-execution validation system:
1. **GovernanceEnforcementAgent** — TDD, type hints, docstrings
2. **SecurityCheckpointAgent** — Git discipline, audit trails
3. **ComplianceValidationAgent** — Domain-specific compliance
4. **FileNamingEnforcementAgent** — Naming conventions
5. **IncrementalExecutionAgent** — Deliverable chunk sizing
6. **MarkdownSuppressionAgent** — Documentation standards
7. **ArchitectureIntegrityAgent** — Pattern consistency
8. **EnvironmentIntegrityAgent** — MCP availability

**Coverage:** 26/30 CORE rules automated (87%)

### 4. MCP-First Architecture

**Gateway:** Model Context Protocol Server

All CORTEX functionality exposed through 26 consolidated MCP tools:
- `cortex_process_request` — Main implementation workflow
- `cortex_lens_analyze` — Code intelligence
- `cortex_challenge` — Design review
- `cortex_onboard_repository` — Repository setup
- `cortex_audit` — Health scans
- `cortex_refactor` — Code improvement
- ... and 20 more

**Architecture:** Auto-starting server (Pylance-style) — zero manual setup.

### 5. Holistic Validation

**Feature:** Pre-implementation validation gate

Every IMPLEMENT/FIX/REFACTOR request undergoes 7-step validation:
1. Registry consistency check
2. Context pre-warming (async)
3. Dependency graph analysis
4. Regression risk scoring (0.0-1.0)
5. Architecture drift detection
6. **Mandatory Challenge Gate** (alternative approaches)
7. CORTEX self-analysis (for CORTEX repo only)

**Verdict:** PASS (<0.4), WARN (0.4-0.7), BLOCK (>0.7)

### 6. Silent Autonomous Execution

**Rule:** CORE-049

Default execution mode — proceed without narration:
- ✅ Show ASCII progress bars only
- ✅ Report completion with metrics
- ❌ No "shall I proceed?" prompts
- ❌ No mid-execution narration
- ❌ No step-by-step descriptions

**Trigger words:** "proceed", "implement", "continue", "yes"

---

## Documentation Structure

> Files are numbered within each section for progressive reading — start at 01 and work forward.

### Getting Started (read first)
- [01 — One Pager](./00-getting-started/01-one-pager.md) — What CORTEX is in 2 minutes
- [02 — Key Concepts](./00-getting-started/02-key-concepts.md) — Terminology reference
- [03 — How CORTEX Works](./00-getting-started/03-how-cortex-works.md) — End-to-end mental model
- [04 — Brain Tier Architecture](./00-getting-started/04-brain-tier-architecture.md) — 3-layer intelligence
- [05 — Quick Start](./00-getting-started/05-quick-start.md) — First request in 5 minutes

### Reference
- **[Glossary](./glossary.md)** — 58 terms defined
- **[Index](./index.md)** — This file

### 01 — Capabilities
- [01 Overview](./01-capabilities/01-overview.md) — Full capability inventory
- [02 Core Platform](./01-capabilities/02-core-platform.md) — Foundation infrastructure
- [03 AI Intelligence](./01-capabilities/03-ai-intelligence.md) — Multi-layer intelligence architecture
- [04 Intelligence Layer](./01-capabilities/04-intelligence-layer.md) — Learning-enhanced orchestrators (Iteration 96)
- [05 Decisioning](./01-capabilities/05-decisioning.md) — Intent classification and routing
- [06 Conversational Gateway](./01-capabilities/06-conversational-gateway.md) — Natural language interface
- [07 Governance & Compliance](./01-capabilities/07-governance-compliance.md) — CORE rules enforcement
- [08 Response Formatting](./01-capabilities/08-response-formatting.md) — Intent-adaptive output
- [09 Semantic Blocks](./01-capabilities/09-semantic-blocks.md) — Structured response assembly
- [10 Workflow Templates](./01-capabilities/10-workflow-templates.md) — Convergence-gated workflows
- [11 Extensibility](./01-capabilities/11-extensibility.md) — Plugin architecture

### 02 — LENS (Code Intelligence)
- [01 Overview](./02-lens/01-overview.md) — What LENS is and why it exists
- [02 Architecture](./02-lens/02-architecture.md) — Layer architecture and wiring
- [03 Analyzers](./02-lens/03-analyzers.md) — 8 parallel code intelligence streams
- [04 Synthesis](./02-lens/04-synthesis.md) — Merging streams into unified context
- [05 Caching](./02-lens/05-caching.md) — 3-tier performance optimisation
- [06 Governance Integration](./02-lens/06-governance-integration.md) — LENS + enforcement

### 03 — Orchestration
- [01 Overview](./03-orchestration/01-overview.md) — Full orchestrator registry and priority table
- [02 Master Orchestrator](./03-orchestration/02-master-orchestrator.md) — Executive coordinator
- [03 Intent Router](./03-orchestration/03-intent-router.md) — Request classification engine
- [04 TDD Orchestrator](./03-orchestration/04-tdd-orchestrator.md) — RED → GREEN → REFACTOR engine
- [05 Domain Orchestrators](./03-orchestration/05-domain-orchestrators.md) — Specialist capability engines
- [06 Cross-Orchestrator Communication](./03-orchestration/06-cross-orchestrator.md) — Messaging and state sharing
- [07 Request Rephrase](./03-orchestration/07-request-rephrase.md) — Stage -1 pre-processor
- [08 End-to-End Flow](./03-orchestration/08-end-to-end-flow.md) — Complete request trace

### 04 — MCP (API Layer)
- [01 Overview](./04-mcp/01-overview.md) — MCP gateway architecture
- [02 Protocol](./04-mcp/02-protocol.md) — JSON-RPC 2.0 specification
- [03 Tools Catalog](./04-mcp/03-tools-catalog.md) — All 26 tools reference
- [04 Integration](./04-mcp/04-integration.md) — Connecting clients to CORTEX
- [05 Versioning](./04-mcp/05-versioning.md) — Semantic version management

### 05 — Infrastructure
- [01 Overview](./05-infrastructure/01-overview.md) — Infrastructure and deployment architecture
- [02 Tech Stack](./05-infrastructure/02-tech-stack.md) — Technology reference
- [03 Deployment](./05-infrastructure/03-deployment.md) — Local to production guide
- [04 CI/CD](./05-infrastructure/04-ci-cd.md) — Automated quality gates
- [05 Observability](./05-infrastructure/05-observability.md) — Metrics, logs, traces
- [06 Scalability](./05-infrastructure/06-scalability.md) — Horizontal and vertical scaling
- [07 Learning Architecture](./05-infrastructure/07-learning-architecture.md) — Universal learning loop

### 06 — Toolkit
- [01 Overview](./06-toolkit/01-overview.md) — MCP tool catalog
- [02 Tool Categories](./06-toolkit/02-tool-categories.md) — Functional classification
- [03 Tool Registry](./06-toolkit/03-tool-registry.md) — Central catalog and lifecycle
- [04 Developer Guide](./06-toolkit/04-developer-guide.md) — Creating custom MCP tools
- [05 Security Model](./06-toolkit/05-security-model.md) — Defence-in-depth architecture

### 07 — Diagrams
- [01 C4 Context](./07-diagrams/01-c4-context.md) — System context (who uses CORTEX)
- [02 C4 Container](./07-diagrams/02-c4-container.md) — Runtime components
- [03 Architecture Overview](./07-diagrams/03-architecture-overview.md) — System-level ASCII diagram
- [04 Component Relationships](./07-diagrams/04-component-relationships.md) — Dependency graph
- [05 Data Flow](./07-diagrams/05-data-flow.md) — End-to-end processing
- [06 Request Lifecycle](./07-diagrams/06-request-lifecycle.md) — Request pipeline sequence
- [07 Governance Gate Flow](./07-diagrams/07-governance-gate-flow.md) — Pre-execution validation
- [08 TDD Cycle](./07-diagrams/08-tdd-cycle.md) — RED → GREEN → REFACTOR visual
- [09 LENS Analyzer Pipeline](./07-diagrams/09-lens-analyzer-pipeline.md) — 8-stream parallel pipeline

### 08 — Learning System
- [01 Overview](./08-learning/01-overview.md) — Adaptive intelligence architecture
- [02 Pattern Capture](./08-learning/02-pattern-capture.md) — What is captured and how it improves CORTEX

---

## Getting Started

### For Business Leaders

**What is CORTEX?**  
An intelligent software development platform that automates code analysis, implementation, and quality control while enforcing best practices.

**Key Benefits:**
- 87% governance automation (26/30 rules)
- Zero-setup MCP architecture
- Test-driven development enforcement
- Multi-language support (5 languages)

**Next Step:** Review [Capabilities Overview](./01-capabilities/01-overview.md)

### For Product Owners

**How does CORTEX help?**  
Standardizes development workflows, enforces quality gates, and provides real-time code intelligence across your entire codebase.

**Key Features:**
- Holistic validation before code changes
- Mandatory challenge gate (alternative approaches)
- 10 specialized code analyzers
- Comprehensive audit trails

**Next Step:** Read [Orchestration Overview](./03-orchestration/01-overview.md)

### For Software Developers

**Where do I start?**  
CORTEX operates through MCP tools in VS Code. Every request routes through specialized orchestrators using TDD methodology.

**Development Flow:**
1. Make request ("implement login feature")
2. IntentRouter classifies → routes to TDDOrchestrator
3. Holistic validation gate (pre-execution)
4. TDD cycle: RED → GREEN → REFACTOR
5. Governance validation (8 agents)
6. Commit with audit markers

**Next Step:** Explore [Quick Start](./00-getting-started/05-quick-start.md) and [TDD Orchestrator](./03-orchestration/04-tdd-orchestrator.md)

---

## Quality & Governance

### CORE Rules

50+ governance rules enforced across all operations:

**Tier 0 (Immutable):**
- CORE-002: No markdown file generation in chat
- CORE-008: TDD mandatory (tests before code)
- CORE-035: Single canonical implementation
- CORE-047: No file paths in instructions
- CORE-048: Holistic validation gate
- CORE-049: Silent autonomous execution
- CORE-050: MCP circuit breaker
- CORE-051: Cross-platform MCP
- CORE-052: Single branch policy

**Enforcement:** Pre-execution gate blocks violations before code generation.

### Audit Trail

All governance-gated work marked with AC (Audit Commit) markers:
```python
# AC_START: AC-ENHANCEMENT-001
# Description: Implement user authentication
# ... code ...
# AC_COMPLETE: AC-ENHANCEMENT-001 ✅ 42/42 tests passing
```

**Traceability:** Every change linked to audit entry in `.cortex-runtime/governance.db`.

---

## Performance Metrics

### Request Processing

| Stage | Latency | Description |
|-------|---------|-------------|
| MCP Gateway | <5ms | Request parsing |
| Intent Classification | 10-20ms | IntentRouter analysis |
| Context Gathering | 50-200ms | LENS analysis |
| Holistic Validation | 150ms | Pre-execution gate |
| Governance Check | 50-150ms | 8-agent validation |
| Orchestrator Execution | 100-5000ms | Depends on operation |
| Response Formatting | 5-10ms | Output generation |

**Total:** 365ms - 5.5s (depends on complexity)

### System Health

- **Uptime Target:** 99.9%
- **Registry Sync:** <200ms
- **LENS Cache Hit:** 70% target
- **Test Coverage:** 90%+ requirement
- **Orchestrator Availability:** 100% (21/21 active)

---

---

## See Also

- **Registry:** `cortex-registry/` — Configuration and governance rules
- **Source Code:** `cortex/` — Python implementation
- **Tests:** `tests/` — Comprehensive test suite
- **MCP Server:** `cortex/04-mcp/` — API server implementation
- **Wiring:** `cortex/wiring/` — Orchestrator registration

---

*Generated by CORTEX Architecture Team | Updated 2026-02-14*
