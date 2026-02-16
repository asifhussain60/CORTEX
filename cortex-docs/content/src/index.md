# CORTEX Architecture Documentation

---
title: CORTEX Architecture Overview
type: explanation
audience: [Business Leaders, Product Owners, Software Developers]
word_count: 1800
last_verified: 2026-02-15
source_of_truth: cortex/__wiring_contract__.yaml + cortex-registry/
format: diátaxis-explanation
voice: third-person-blended
---

> **Notice:** This documentation represents CORTEX system design and architecture as of February 2026. Capabilities and performance characteristics represent design intentions. Actual results depend on codebase characteristics, development practices, infrastructure configuration, and team expertise. Organizations should conduct proof-of-concept evaluations to assess applicability to their specific context.

---

## Executive Summary

### CORTEX: Intelligent Software Development Acceleration Platform

CORTEX is an intelligent development acceleration platform that processes software development requests through a sophisticated orchestration architecture. Organizations using CORTEX may experience streamlined development workflows through automated test-driven development, code intelligence analysis, and governance enforcement [Business Leaders]. Product teams leverage the platform's orchestrator network to manage feature implementation, refactoring workflows, and architecture validation at scale [Product Owners]. The system provides developers with automated TDD cycles, multi-language code analysis via LENS intelligence, and pre-execution governance gates that enforce 59 CORE rules across 7 enforcement agents [Software Developers].

**Core Architecture Pattern:**

When development requests enter CORTEX, they flow through a multi-stage processing pipeline analogous to modern distributed systems:

1. **MCP Gateway Layer** — Accepts JSON-RPC requests over stdio from IDE clients (VS Code, Cursor, Claude Desktop). The Native Tool Gate validates intent classification and prevents direct file operations for implementation requests, enforcing MCP-first architecture (CORE-049).

2. **Orchestration Layer** — MasterOrchestrator coordinates 20+ specialized orchestrators through hierarchical dispatch. IntentRouter performs LENS-based classification (LANGUAGE→EXAMINATION→NAVIGATION→SYNTHESIS) to route requests: IMPLEMENT/FIX → TDDOrchestrator, ANALYZE → LENSSynthesis, PLAN → PlanOrchestrator, REFACTOR → RefactoringOrchestrator.

3. **Intelligence Layer** — LENS analyzers execute in parallel (8 core analyzers: AST, Git History, Comment, Import, Security, Pattern, Metrics, Domain) to provide unified code intelligence. Context Crystallization Layer (Phase 49) performs async prefetch of rules, LENS state, and infrastructure detection with 245ms average completion.

4. **Governance Layer** — EnforcementOrchestrator coordinates 7 enforcement agents performing pre-execution validation with <150ms latency. Agents check TDD enforcement (CORE-008), type hints (CORE-011), file naming (CORE-028), incremental execution limits (CORE-001), and architecture integrity across 26 automated CORE rules (87% coverage).

5. **CORTEX Brain** — Git-backed registry (cortex-registry/) stores orchestrator specifications, governance rules (59 CORE rules), knowledge base (45+ best practice YAMLs), and phase definitions. Wiring contract (__wiring_contract__.yaml) drives orchestrator discovery with hot-reload support.

CORTEX represents a **cognitive architecture** — an event-driven system that classifies intent, synthesizes context, enforces governance, and executes development workflows autonomously.

### System Architecture Metrics (February 2026)

Organizations deploying CORTEX benefit from understanding the platform's architectural composition and operational characteristics.

**Orchestration Architecture:**

| Component Layer | Count | Responsibility | Typical Latency |
|-----------------|-------|----------------|-----------------|
| **MCP Gateway** | 10 core tools | Request validation, tool dispatch, response delivery | 5-15ms |
| **Core Orchestrators** | 8 | Essential workflows (Master, Router, TDD, LENS, Enforcement, Plan, Refactor, Digest) | 50-2000ms |
| **Domain Orchestrators** | 6 | Specialized capabilities (Documentation, Challenge, Conversation, Domain, Workflow, Task Decomposer) | 150-800ms |
| **Support Orchestrators** | 6+ | Educational, onboarding, tool discovery, recommendation gate | 100-500ms |
| **LENS Analyzers** | 8 core | Parallel code intelligence (AST, Git, Security, Metrics, Pattern, Comment, Import, Domain) | 300-800ms |
| **Enforcement Agents** | 7 | Pre-execution governance (TDD, Security, Compliance, Naming, Incremental, Markdown, Architecture) | <150ms |
| **CORE Rules** | 59 automated | Governance standards (87% coverage across 7 agents) | <5ms per rule |

**Git-Backed Registry Structure:**

```
cortex-registry/
├── _cortex-master/          # 46 files: Phase index, dashboard data, enhancements
├── domains/                 # 1 file: Domain-specific configuration
├── governance/              # 2 files: CORE rules, audit checklists
├── interaction/             # 6 files: Response templates, content blocks
├── master/                  # 2 files: Orchestrator master registry
├── planning/                # 7 files: Phase definitions, roadmap
└── manifest.yaml            # Registry metadata
```

**Performance Characteristics (Internal Testing):**

Organizations may observe the following performance patterns based on internal testing with typical repositories (50-100K LOC):

- **Request validation:** P50: 8ms, P95: 15ms, P99: 22ms
- **Pre-flight checks:** P50: 245ms, P95: 320ms, P99: 450ms (includes parallel governance + CCL)
- **Intent classification:** P50: 32ms, P95: 45ms, P99: 62ms (LENS-based routing)
- **TDD cycle (small):** P50: 850ms, P95: 1200ms, P99: 1800ms (RED→GREEN→REFACTOR)
- **TDD cycle (large):** P50: 2100ms, P95: 2600ms, P99: 3500ms (complex implementations)
- **LENS analysis:** P50: 450ms, P95: 750ms, P99: 1200ms (8 analyzers parallel)
- **End-to-end IMPLEMENT:** P50: 1650ms, P95: 2300ms, P99: 3200ms (full workflow)

> **Notice:** Performance measurements reflect internal testing environments. Production results depend on hardware specifications (CPU cores, memory), repository size and complexity, network latency, concurrent operations, and codebase characteristics. Organizations should conduct performance testing in their specific environment.

**Technology Stack:**

- **Runtime:** Python 3.9+ with async/await patterns
- **Transport:** stdio (development), HTTP/JSON-RPC (production Phase 11)
- **Storage:** Git (registry), SQLite (AST cache), File system (workspace)
- **Analysis:** tree-sitter (multi-language parsing), git-python (history), AST (Python native)
- **Integration:** MCP SDK (protocol), JSON-RPC 2.0 (messaging)

**Contract Validation:** A new **ContractValidator** infrastructure component (Priority 3) provides 4-layer validation ensuring all orchestrators maintain their architectural contracts with comprehensive audit logging.

Seven deprecated orchestrators remain active until their **sunset date (2026-03-31)**, after which they'll be fully removed.

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
| **PlanningOrchestrator** | 75 | Strategy planner — roadmap management |
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

### Core Documentation

- **[Index](./index.md)** — This file (architecture overview)
- **[Glossary](./glossary.md)** — Term definitions and concepts
- **[Capabilities Overview](./capabilities/overview.md)** — Feature catalog

### Detailed Documentation

#### Capabilities
- [Core Platform](./capabilities/core-platform.md)
- [AI Intelligence](./capabilities/ai-intelligence.md)
- [Governance & Compliance](./capabilities/governance-compliance.md)
- [Response Formatting](./capabilities/response-formatting.md)
- [Decisioning](./capabilities/decisioning.md)
- [Extensibility](./capabilities/extensibility.md)

#### Orchestration
- [Overview](./orchestration/overview.md)
- [Master Orchestrator](./orchestration/master-orchestrator.md)
- [Intent Router](./orchestration/intent-router.md)
- [TDD Orchestrator](./orchestration/tdd-orchestrator.md)
- [Domain Orchestrators](./orchestration/domain-orchestrators.md)
- [Support Orchestrators](./orchestration/support-orchestrators.md)
- [Cross-Orchestrator Communication](./orchestration/cross-orchestrator.md)
- [End-to-End Flow](./orchestration/end-to-end-flow.md)

#### LENS (Intelligence)
- [Overview](./lens/overview.md)
- [Architecture](./lens/architecture.md)
- [Analyzers](./lens/analyzers.md)
- [Synthesis](./lens/synthesis.md)
- [Caching](./lens/caching.md)
- [Governance Integration](./lens/governance.md)

#### MCP (API Layer)
- [Overview](./mcp/overview.md)
- [README](./mcp/README.md)
- [Protocol](./mcp/protocol.md)
- [Tools Catalog](./mcp/tools-catalog.md)
- [Integration](./mcp/integration.md)
- [Versioning](./mcp/versioning.md)

#### Infrastructure
- [Overview](./infrastructure/overview.md)
- [Tech Stack](./infrastructure/tech-stack.md)
- [Learning Architecture](./infrastructure/learning-architecture.md)
- [Observability](./infrastructure/observability.md)
- [CI/CD](./infrastructure/ci-cd.md)
- [Deployment](./infrastructure/deployment.md)
- [Scalability](./infrastructure/scalability.md)

#### Diagrams
- [Architecture Overview](./diagrams/architecture-overview.md)
- [Component Relationships](./diagrams/component-relationships.md)
- [Data Flow](./diagrams/data-flow.md)
- [Request Lifecycle](./diagrams/request-lifecycle.md)

#### Toolkit
- [Overview](./toolkit/overview.md)
- [Developer Guide](./toolkit/developer-guide.md)
- [Tool Registry](./toolkit/tool-registry.md)
- [Tool Categories](./toolkit/tool-categories.md)
- [Security Model](./toolkit/security-model.md)

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

**Next Step:** Review [Capabilities Overview](./capabilities/overview.md)

### For Product Owners

**How does CORTEX help?**  
Standardizes development workflows, enforces quality gates, and provides real-time code intelligence across your entire codebase.

**Key Features:**
- Holistic validation before code changes
- Mandatory challenge gate (alternative approaches)
- 10 specialized code analyzers
- Comprehensive audit trails

**Next Step:** Read [Orchestration Overview](./orchestration/overview.md)

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

**Next Step:** Explore [Developer Guide](./toolkit/developer-guide.md) and [TDD Orchestrator](./orchestration/tdd-orchestrator.md)

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

**Traceability:** Every change linked to audit entry in `cortex_brain/governance.db`.

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

## Version History

**Current:** 3.0.0 (2026-02-14)

**Recent Changes:**
- Added 4 super-orchestrators (State, Observability, Intelligence, SOLID)
- Consolidated 12 support orchestrators into 4 unified orchestrators
- MCP tool consolidation (86 → 26 parent tools)
- Holistic validation gate implementation
- Context crystallization layer (async pre-warming)
- Pylance-style MCP architecture
- Cross-platform MCP support
- Single branch policy enforcement

**Breaking Changes:** None (backward compatible)

**Deprecations:** 7 orchestrators (sunset 2026-03-31)

---

## See Also

- **Registry:** `cortex-registry/` — Configuration and governance rules
- **Source Code:** `cortex/` — Python implementation
- **Tests:** `tests/` — Comprehensive test suite
- **MCP Server:** `cortex/mcp/` — API server implementation
- **Wiring:** `cortex/wiring/` — Orchestrator registration

---

*Generated by CORTEX Architecture Team | Updated 2026-02-14*
