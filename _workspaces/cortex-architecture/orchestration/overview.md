# CORTEX Orchestration Overview

**Total Active Orchestrators:** 21 | **Deprecated:** 7 (sunset 2026-03-31) | **Updated:** 2026-02-14  
**Architecture:** Git-Backed Registry | **Wiring:** `__wiring_contract__.yaml` v2.1.0 | **Status:** COMPLETE

---

## The Coordinated System

Think of CORTEX's orchestrators as **specialized processing centers working together**. Just as a modern data center distributes workloads across specialized servers — some for database queries, others for authentication, others for analytics — CORTEX distributes software intelligence across 17 specialized orchestrators.

Each orchestrator has a **priority number** (lower = more fundamental, like core infrastructure vs. advanced features) and a specific **processing domain**. When a request enters the system, it flows through these centers in a structured pipeline — from perception, through reasoning, to action.

### The Consolidated Architecture

CORTEX underwent **system consolidation** — reducing redundancy and improving efficiency. The architecture consolidated 27 orchestrators down to 17, a **37% reduction**, and added 4 super-orchestrators for advanced capabilities. The total system now comprises 21 orchestrators (14 active + 4 super-orchestrators + 7 deprecated) plus 4 infrastructure components.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    🎯 MasterOrchestrator (P10)                       │
│              The Air Traffic Control Tower — Central Coordination     │
│  • Coordinates all orchestrators   • Manages lifecycle              │
│  • Delegates to IntentRouter       • Circuit breaker patterns       │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
          ┌─────────────────────┼─────────────────────┐
          ▼                     ▼                     ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ 🧠 Core (5)      │  │ 🎨 Domain (5)    │  │ 🔧 Unified       │
│ Foundation &     │  │ Specialized      │  │   Support (4)    │
│ Core System      │  │ Teams            │  │ Helper           │
│                  │  │                  │  │ Services         │
│ + ⚙️ Infra (3)   │  │                  │  │ + 7 deprecated   │
└──────────────────┘  └──────────────────┘  └──────────────────┘
```

---

## The 21 Orchestrators (14 Active + 4 Super + 7 Deprecated)

### 🧠 Core Orchestrators (6) — The Foundation Layer

These are the non-negotiable foundations — without them, CORTEX cannot function. Like essential infrastructure (power, networking, authentication), these orchestrators control the fundamental request pipeline.

| # | Orchestrator | Priority | System Analogy | Role |
|---|-------------|----------|---------------|------|
| 1 | **MasterOrchestrator** | 10 | **Air traffic control** — central coordination | Coordinates all operations, routes every request |
| 2 | **IntentRouter** | 20 | **Security checkpoint** — classification hub | Classifies intent, routes to specialist teams |
| 3 | **TDDOrchestrator** | 30 | **Construction crew** — disciplined execution | Enforces RED→GREEN→REFACTOR workflow |
| 4 | **WorkflowOrchestrator** | 40 | **Assembly line** — procedural sequences | Manages multi-step workflow execution |
| 5 | **InteractionOrchestrator** | 50 | **Customer service** — communication | Handles conversation and user dialogue |
| 6 | **WrappedTDDOrchestrator** | 170 | **Deprecated wrapper** — removed soon | DEPRECATED (sunset 2026-03-31, use TDDOrchestrator directly) |

**Deep dives:** [MasterOrchestrator](./master-orchestrator.md) · [IntentRouter](./intent-router.md) · [TDDOrchestrator](./tdd-orchestrator.md)

---

### 🎨 Domain Orchestrators (5) — Specialized Teams

These are the expert processing centers. Each one handles a specific domain, like specialized departments in a company (legal, finance, HR, marketing, R&D).

| # | Orchestrator | Priority | System Analogy | Role |
|---|-------------|----------|---------------|------|
| 6 | **RefactoringOrchestrator** | 60 | **Renovation team** — code restructuring | Understands code structure, improves architecture |
| 7 | **PlanningOrchestrator** | 70 | **Project management** — strategic planning | Decomposes complex tasks, generates execution plans |
| 8 | **DomainOrchestrator** | 80 | **Business analyst** — domain expertise | Domain knowledge, business logic understanding |
| 9 | **ConversationOrchestrator** | 90 | **Account manager** — relationship building | Natural conversation tracking, context maintenance |
| 10 | **SeleniumPlaywrightOrchestrator** | 100 | **QA automation** — precision testing | Fine-grained browser automation |

**Deep dive:** [Domain Orchestrators](./domain-orchestrators.md)

---

### 🔧 Support Orchestrators (10) — Assistant Regions

Organizations benefit from specialized assistance across development workflows. These orchestrators provide capabilities from repository onboarding to quality assurance [Business Leaders]. Product teams use these assistants for comprehensive code analysis, educational content, and planning support [Product Owners]. Support orchestrators integrate with core processing to enhance development capabilities [Software Developers].

| # | Orchestrator | Priority | System Analogy | Role |
|---|-------------|----------|----------------|------|
| 11 | **UnifiedOnboardingOrchestrator** | 105 | **Memory system** — initial encoding | Repository onboarding & environment setup |
| 12 | **UnifiedAnalysisOrchestrator** | 115 | **Pattern recognition** — analysis engine | Code analysis & LENS coordination |
| 13 | **UnifiedQualityAssuranceOrchestrator** | 125 | **Quality control** — error detection | Quality assurance & code review |
| 14 | **UnifiedDiscoveryOrchestrator** | 135 | **Exploration system** — discovery engine | Learning paths & feature discovery |
| 15 | **RollbackOrchestrator** | 140 | DEPRECATED — use WorkflowOrchestrator | Rollback operations (sunset 2026-03-31) |
| 16 | **SetupOrchestrator** | 150 | DEPRECATED — use UnifiedOnboardingOrch | Setup operations (sunset 2026-03-31) |
| 17 | **ComposedOrchestrator** | 160 | DEPRECATED — use MasterOrchestrator | Composition patterns (sunset 2026-03-31) |
| 18-20 | **3 Other DEPRECATED** | Various | See below | Onboarding, ToolDiscovery, Upgrade |

**Deep dive:** [Support Orchestrators](./support-orchestrators.md)

---

### ⚙️ Infrastructure Components (4) — Core Foundation

These keep the system running. Organizations depend on these foundational systems for orchestrator lifecycle and validation [Business Leaders]. Infrastructure components ensure system reliability through continuous health monitoring and contract enforcement [Product Owners]. These components provide the wiring backbone that connects all orchestrators with 4-layer validation [Software Developers].

| # | Component | Priority | System Analogy | Role |
|---|-----------|----------|----------------|------|
| 1 | **OrchestratorBootstrap** | 1 | **System initialization** — startup process | System initialization, boots all regions at startup |
| 2 | **HealthChecker** | 2 | **Health monitoring** — vital signs tracker | Continuous health monitoring across all regions |
| 3 | **ContractValidator** | 3 | **Quality control gateway** — architectural integrity | 4-layer validation (signature, return type, audit, cross-layer) |
| 4 | **DatabaseBackedRegistry** | 5 | **Central registry** — component catalog | Connects every region, manages orchestrator catalog |

---

### 🌟 Super-Orchestrators (4) — Advanced Coordination Centers

**NEW:** Organizations gain advanced capabilities through these multi-subsystem coordinators that consolidate 18 specialized components [Business Leaders]. Product teams benefit from unified state management, comprehensive observability, enhanced intelligence analysis, and architectural quality validation [Product Owners]. Each super-orchestrator provides audit logging and consolidates 3-6 specialized subsystems into coordinated processing centers [Software Developers].

| # | Super-Orchestrator | Priority | Consolidates | System Analogy | Capabilities |
|---|-------------------|----------|--------------|----------------|-------------|
| 18 | **StateOrchestrator** | 180 | 3 state managers | **Memory & state storage** — consolidation | State management, checkpoints, conversation state, brain state |
| 19 | **ObservabilityOrchestrator** | 185 | 4 monitoring systems | **System awareness** — visibility platform | Metrics, tracing, alerts, comprehensive observability |
| 20 | **IntelligenceOrchestrator** | 190 | 5 intelligence engines | **Pattern recognition** — intelligence synthesis | AST parsing, comment analysis, intelligence routing, code comprehension |
| 21 | **SOLIDOrchestrator** | 195 | 6 quality analyzers | **Quality control** — architectural integrity | SOLID analysis (SRP, OCP, LSP, ISP, DIP), DRY validation |

**Architecture Pattern:** Each super-orchestrator:
- Consolidates multiple specialized subsystems (3-6 components each)
- Provides unified API for coordinated operations
- Implements comprehensive audit logging
- Reduces integration complexity through single coordination point

**Consolidated Components:**
```
StateOrchestrator ← BrainStateManager, CheckpointManager, ConversationStateManager
ObservabilityOrch ← PrometheusMetrics, Tracer, AlertManager, MetricsCollector
IntelligenceOrch  ← ASTEngine, CommentAnalyzer, ComprehensionLoop, RoutingEngine, DomainInference
SOLIDOrchestrator ← SRPAnalyzer, OCPAnalyzer, LSPAnalyzer, ISPAnalyzer, DIPAnalyzer, DRYAnalyzer
```

> **Notice:** Super-orchestrator capabilities represent system design intentions. Actual 
> performance characteristics depend on codebase complexity, infrastructure configuration, 
> and operational context. Organizations should evaluate effectiveness through pilot testing.

---

### ⚠️ Deprecated Orchestrators (7) — Vestigial Structures

These are evolutionary remnants being phased out by 2026-03-31. They still function but are superseded by unified orchestrators:

| Orchestrator | Priority | Replaced By | Sunset |
|-------------|----------|-------------|--------|
| OnboardingOrchestrator | 110 | UnifiedOnboardingOrchestrator | 2026-03-31 |
| ToolDiscoveryOrchestrator | 120 | UnifiedAnalysisOrchestrator | 2026-03-31 |
| UpgradeOrchestrator | 130 | UnifiedOnboardingOrchestrator | 2026-03-31 |
| RollbackOrchestrator | 140 | WorkflowOrchestrator | 2026-03-31 |
| SetupOrchestrator | 150 | UnifiedOnboardingOrchestrator | 2026-03-31 |
| ComposedOrchestrator | 160 | MasterOrchestrator | 2026-03-31 |
| WrappedTDDOrchestrator | 170 | TDDOrchestrator | 2026-03-31 |

---

## Orchestrator Request Flow

### The Cognitive Pipeline

When a request enters CORTEX, it follows the same path a thought takes through the brain — from sensory input to motor output:

```
1. 👂 Sensory Input — User request arrives
   ↓
2. 🌐 MCP Gateway — cortex_process_request (peripheral nerve)
   ↓
3. 🧠 MasterOrchestrator — Prefrontal cortex validates & delegates
   ↓
4. 🧭 IntentRouter — Thalamus classifies the signal
   │   IMPLEMENT → TDDOrchestrator (motor cortex)
   │   REFACTOR  → RefactoringOrchestrator (Wernicke's area)
   │   ANALYZE   → UnifiedAnalysisOrchestrator (visual association)
   ↓
5. 🎯 Specialist Orchestrator — Processes in its cognitive domain
   ↓
6. 🛡️ Quality Gate — UnifiedQualityAssuranceOrchestrator (anterior cingulate)
   ↓
7. 📤 Motor Output — Validated response delivered via MCP
```

### Example: IMPLEMENT Flow

```python
# User: "Implement user authentication"

# Step 1: MCP Entry (sensory nerve fires)
cortex_process_request(
    request="Implement user authentication",
    enable_challenge=True
)

# Step 2: MasterOrchestrator delegates (prefrontal cortex)
intent = IntentRouter.classify(request)  # Thalamus routes
# Result: IntentType.IMPLEMENT → TDDOrchestrator

# Step 3: TDD Cycle (motor cortex executes)
orchestrator.execute_tdd_cycle(
    phase='RED',      # Write failing tests (intention)
    phase='GREEN',    # Implement minimal code (action)
    phase='REFACTOR'  # Apply best practices (refinement)
)

# Step 4: Quality Gate (anterior cingulate checks for errors)
UnifiedQualityAssuranceOrchestrator.validate([
    'CORE-008',  # Tests before code
    'CORE-011',  # Type hints
    'CORE-012',  # Docstrings
])

# Step 5: Audit Trail — AC_START → AC_COMPLETE markers
# Result: ✅ Implementation complete with governance compliance
```

---

## Orchestrator Wiring

### The Connectome: `__wiring_contract__.yaml`

Just as neuroscientists map the brain's "connectome" — the complete wiring diagram of neural connections — CORTEX maps its orchestrator connections in `__wiring_contract__.yaml`:

```yaml
version: "2.1.0"
total_orchestrators: 21
total_active_orchestrators: 21
total_deprecated: 7
phase_23_megab_s3_status: "SUPER-ORCHESTRATORS REGISTERED"
consolidation_achieved: "37% reduction (27 → 21 orchestrators including 4 super-orchestrators)"

orchestrators:
  - name: "MasterOrchestrator"
    category: "core"
    priority: 10
    capabilities: ["orchestration", "routing", "delegation"]
    dependencies: []
    is_optional: false
```

### Dynamic Loading — Synaptic Activation

Orchestrators are loaded **on-demand**, like neurons that only fire when stimulated. This keeps the brain's resting metabolic cost low:

```python
from cortex.wiring import GitBackedRegistry

# Initialize registry (brain wakes up)
registry = GitBackedRegistry()
registry.load()

# Get orchestrator (neuron activates on demand)
tdd_orch = registry.get('TDDOrchestrator')

# First access triggers instantiation (synaptic connection forms)
tdd_orch.execute_tdd_cycle(...)
```

---

## Key Design Patterns (Cognitive Architecture Principles)

| Pattern | Brain Analogy | Description |
|---------|---------------|-------------|
| **Strategy** | Specialized brain regions | Different orchestrators for different intents |
| **Chain of Responsibility** | Neural signal cascade | Master → Router → Specialist → Quality Gate |
| **Lazy Loading** | Synaptic pruning | Orchestrators instantiated only when needed |
| **Dependency Injection** | Axonal connections | Dependencies declared in YAML, wired at runtime |
| **Event-Driven** | Neurotransmitter signaling | Orchestrators communicate via events, not direct calls |

---

## Performance Metrics

| Metric | Target | Actual | Brain Analogy |
|--------|--------|--------|---------------|
| **Orchestrator Load** | <100ms | ~80ms | Neuron activation time |
| **Routing Decision** | <50ms | ~35ms | Thalamic relay speed |
| **TDD Cycle (small)** | <5s | ~3.2s | Motor planning + execution |
| **Quality Validation** | <200ms | ~150ms | Error detection latency |
| **Memory per Orchestrator** | <10MB | ~7MB | Neural metabolic cost |

---

**Last Updated:** 2026-02-14  
**Source:** `__wiring_contract__.yaml` v2.1.0 | Phase 23 MEGA-B S3 Complete  
**Active Orchestrators:** 14 + 4 super | **Deprecated:** 7 | **Infrastructure:** 4
---

## See Also

**Orchestration Deep Dives:**
- [Master Orchestrator](./master-orchestrator.md) — Executive coordination and lifecycle management
- [Intent Router](./intent-router.md) — Request classification and routing
- [TDD Orchestrator](./tdd-orchestrator.md) — Test-driven development workflow
- [Domain Orchestrators](./domain-orchestrators.md) — Specialized domain handlers
- [Support Orchestrators](./support-orchestrators.md) — Unified support layer

**Related Architecture:**
- [End-to-End Flow](./end-to-end-flow.md) — Complete request lifecycle
- [Cross-Orchestrator Communication](./cross-orchestrator.md) — Event-driven patterns
- [MCP Integration](../mcp/overview.md) — How orchestrators expose tools
- [Governance Compliance](../capabilities/governance-compliance.md) — Enforcement agents

**Reference:**
- [CORTEX Glossary](../glossary.md) — Term definitions
- [Architecture Index](../index.md) — Full documentation map