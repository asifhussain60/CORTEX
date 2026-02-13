# CORTEX Orchestration Overview

**Total Active Orchestrators:** 17 | **Deprecated:** 7 (sunset 2026-03-31) | **Updated:** 2026-02-13  
**Architecture:** Git-Backed Registry | **Wiring:** `__wiring_contract__.yaml` v2.0.0 | **Wave 7 Track 4:** COMPLETE

---

## The Brain's Neural Network

Think of CORTEX's orchestrators as **specialized regions of a living brain**. Just as the human brain doesn't have one monolithic processor but instead distributes cognition across dozens of specialized regions — the visual cortex for sight, Broca's area for language, the hippocampus for memory — CORTEX distributes software intelligence across 17 specialized orchestrators.

Each orchestrator has a **priority number** (lower = more fundamental, like the brain stem vs. the prefrontal cortex) and a specific **cognitive domain**. When a request enters the system, it flows through these regions in a structured cognitive pipeline — from perception, through reasoning, to action.

### The Post-Consolidation Brain (Wave 7 Track 4)

CORTEX recently underwent **neural pruning** — the same process a maturing brain uses to eliminate redundant synaptic connections. Wave 7 Track 4 consolidated 27 orchestrators down to 17, a **37% reduction**, resulting in a faster, leaner cognitive architecture. Four new "unified" orchestrators absorbed the capabilities of 12 predecessors, like brain regions merging to form more powerful association areas.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    🎯 MasterOrchestrator (P10)                       │
│           The Prefrontal Cortex — Executive Decision Center          │
│  • Coordinates all orchestrators   • Manages lifecycle              │
│  • Delegates to IntentRouter       • Circuit breaker patterns       │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
          ┌─────────────────────┼─────────────────────┐
          ▼                     ▼                     ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ 🧠 Core (5)      │  │ 🎨 Domain (5)    │  │ 🔧 Unified       │
│ Brain Stem &     │  │ Specialized      │  │   Support (4)    │
│ Cortex           │  │ Lobes            │  │ Association      │
│                  │  │                  │  │ Areas            │
│ + ⚙️ Infra (3)   │  │                  │  │ + 7 deprecated   │
└──────────────────┘  └──────────────────┘  └──────────────────┘
```

---

## The 17 Active Neural Regions

### 🧠 Core Orchestrators (5) — The Brain Stem & Cortex

These are the non-negotiable foundations — without them, CORTEX cannot think. Like the brain stem controls breathing and heartbeat, these orchestrators control the fundamental cognitive pipeline.

| # | Orchestrator | Priority | Brain Analogy | Role |
|---|-------------|----------|---------------|------|
| 1 | **MasterOrchestrator** | 10 | **Prefrontal cortex** — executive function | Coordinates all thought, routes every request |
| 2 | **IntentRouter** | 20 | **Thalamus** — sensory relay station | Classifies intent signals, routes to specialist regions |
| 3 | **TDDOrchestrator** | 30 | **Primary motor cortex** — disciplined execution | Enforces RED→GREEN→REFACTOR muscle memory |
| 4 | **WorkflowOrchestrator** | 40 | **Basal ganglia** — procedural sequences | Manages multi-step workflow execution |
| 5 | **InteractionOrchestrator** | 50 | **Broca's area** — language production | Handles conversation and user dialogue |

**Deep dives:** [MasterOrchestrator](./master-orchestrator.md) · [IntentRouter](./intent-router.md) · [TDDOrchestrator](./tdd-orchestrator.md)

---

### 🎨 Domain Orchestrators (5) — Specialized Brain Lobes

These are the expert processing centers. Each one handles a specific cognitive domain, the way the angular gyrus processes written language or the fusiform face area recognizes faces.

| # | Orchestrator | Priority | Brain Analogy | Role |
|---|-------------|----------|---------------|------|
| 6 | **RefactoringOrchestrator** | 60 | **Wernicke's area** — code comprehension & restructuring | Understands code structure, improves architecture |
| 7 | **PlanningOrchestrator** | 70 | **Dorsolateral prefrontal** — strategic planning | Decomposes complex tasks, generates execution plans |
| 8 | **DomainOrchestrator** | 80 | **Angular gyrus** — cross-modal integration | Domain expertise, business logic understanding |
| 9 | **ConversationOrchestrator** | 90 | **Superior temporal sulcus** — social cognition | Natural conversation tracking, context maintenance |
| 10 | **SeleniumPlaywrightOrchestrator** | 100 | **Cerebellum** — precision motor control | Fine-grained browser automation |

**Deep dive:** [Domain Orchestrators](./domain-orchestrators.md)

---

### 🔧 Unified Support Orchestrators (4) — Consolidated Association Areas

These are the result of Wave 7's neural pruning. Each one merges multiple predecessor regions into a single, more capable association area — like the brain's temporal-parietal junction integrating input from multiple senses into a unified understanding.

| # | Orchestrator | Priority | Replaces | Brain Analogy | Role |
|---|-------------|----------|----------|---------------|------|
| 11 | **UnifiedOnboardingOrchestrator** | 105 | OnboardingOrch, RepositoryOnboardingOrch, SetupOrch | **Hippocampal formation** — memory encoding | New repository onboarding & environment setup |
| 12 | **UnifiedAnalysisOrchestrator** | 115 | LENSOrchestrator, ToolDiscoveryOrch | **Visual association cortex** — pattern recognition | Code analysis, LENS coordination, tool discovery |
| 13 | **UnifiedQualityAssuranceOrchestrator** | 125 | RecommendationGate, ChallengeEngine, MetaAuditOrch, CodeReviewOrch, SecurityReviewEngine | **Anterior cingulate cortex** — error detection | Quality assurance, challenge generation, code review |
| 14 | **UnifiedDiscoveryOrchestrator** | 135 | EducationalOrch, BusinessLanguageOrch | **Curiosity circuit** — exploration drive | Learning paths, educational content, feature discovery |

**Deep dive:** [Support Orchestrators](./support-orchestrators.md)

---

### ⚙️ Infrastructure Components (3) — The Brain Stem

These keep the brain alive. They don't process user requests directly, but without them, nothing else functions — like the medulla oblongata regulates heartbeat and breathing.

| # | Component | Priority | Brain Analogy | Role |
|---|-----------|----------|---------------|------|
| 15 | **OrchestratorBootstrap** | 1 | **Reticular formation** — arousal & wakefulness | System initialization, boots all regions at startup |
| 16 | **HealthChecker** | 2 | **Autonomic nervous system** — vital signs | Continuous health monitoring across all regions |
| 17 | **DatabaseBackedRegistry** | 5 | **Spinal cord** — central wiring | Connects every region, manages orchestrator catalog |

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
version: "2.0.0"
total_orchestrators: 17
total_active_orchestrators: 17
total_deprecated: 7
wave_7_track_4_status: "CONSOLIDATION COMPLETE"
consolidation_achieved: "37% reduction (27 → 17 orchestrators)"

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

**Last Updated:** 2026-02-13  
**Source:** `__wiring_contract__.yaml` v2.0.0 | Wave 7 Track 4 Complete  
**Active Orchestrators:** 17 | **Deprecated:** 7 | **Infrastructure:** 3
