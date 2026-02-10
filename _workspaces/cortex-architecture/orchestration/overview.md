# Orchestration Overview

**Purpose:** Introduction to CORTEX orchestration concepts and patterns  
**Audience:** All Technical Stakeholders  
**Last Updated:** 2026-02-10

---

## Table of Contents

- [What is Orchestration?](#what-is-orchestration)
- [Orchestrator Categories](#orchestrator-categories)
- [Orchestrator Hierarchy](#orchestrator-hierarchy)
- [Request Lifecycle](#request-lifecycle)
- [Coordination Patterns](#coordination-patterns)
- [Related Documents](#related-documents)

---

## What is Orchestration?

Orchestration in CORTEX refers to the coordination of multiple specialized components to accomplish complex development tasks. Unlike simple command-response systems, CORTEX orchestrators:

- **Understand Context** — Analyze code, history, and domain knowledge
- **Make Decisions** — Route requests to appropriate handlers
- **Coordinate Actions** — Manage multi-step workflows
- **Enforce Governance** — Apply quality and security rules
- **Learn and Adapt** — Improve based on outcomes

---

## Orchestrator Categories

CORTEX organizes 23 orchestrators into four categories:

### Core Orchestrators (8)

Central coordination and fundamental operations.

| Orchestrator | Priority | Purpose |
|--------------|----------|---------|
| **MasterOrchestrator** | 10 | Central coordinator for all operations |
| **IntentRouter** | 20 | Intent classification and routing |
| **TDDOrchestrator** | 30 | Test-driven development workflow |
| **WorkflowOrchestrator** | 40 | Multi-step workflow management |
| **InteractionOrchestrator** | 50 | User interaction handling |
| **WrappedTDDOrchestrator** | 170 | TDD with additional wrappers |
| **DatabaseBackedRegistry** | 5 | Wiring and registry management |
| **HealthChecker** | 2 | System health monitoring |

### Domain Orchestrators (6)

Domain-specific logic and specialized operations.

| Orchestrator | Priority | Purpose |
|--------------|----------|---------|
| **RefactoringOrchestrator** | 60 | Code improvement and restructuring |
| **PlanningOrchestrator** | 70 | Development planning and phases |
| **DomainOrchestrator** | 80 | Business domain logic |
| **ConversationOrchestrator** | 90 | Dialogue and conversation |
| **SeleniumPlaywrightOrchestrator** | 100 | Browser automation |
| **DocumentationOrchestrator** | — | Documentation generation |

### Support Orchestrators (9)

Auxiliary functions and operational support.

| Orchestrator | Priority | Purpose |
|--------------|----------|---------|
| **OnboardingOrchestrator** | 110 | Repository onboarding |
| **ToolDiscoveryOrchestrator** | 120 | Tool and feature discovery |
| **UpgradeOrchestrator** | 130 | Version upgrades |
| **RollbackOrchestrator** | 140 | Rollback and recovery |
| **SetupOrchestrator** | 150 | Initial setup and configuration |
| **ComposedOrchestrator** | 160 | Composite operations |
| **KnowledgeOrchestrator** | — | Knowledge retrieval |
| **ValidationOrchestrator** | — | Validation operations |
| **MigrationOrchestrator** | — | Migration operations |

### Infrastructure Orchestrators (3)

System-level operations and management.

| Orchestrator | Priority | Purpose |
|--------------|----------|---------|
| **OrchestratorBootstrap** | 1 | System initialization |
| **DatabaseBackedRegistry** | 5 | Wiring registry |
| **HealthChecker** | 2 | Health monitoring |

---

## Orchestrator Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│                     ORCHESTRATOR HIERARCHY                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│                    ┌─────────────────────┐                      │
│                    │  MasterOrchestrator │                      │
│                    │    (Coordinator)    │                      │
│                    └─────────┬───────────┘                      │
│                              │                                   │
│              ┌───────────────┼───────────────┐                  │
│              ▼               ▼               ▼                   │
│      ┌──────────────┐ ┌──────────────┐ ┌──────────────┐        │
│      │ IntentRouter │ │    LENS      │ │  Governance  │        │
│      │  (Routing)   │ │(Intelligence)│ │ (Enforcement)│        │
│      └──────┬───────┘ └──────────────┘ └──────────────┘        │
│             │                                                    │
│    ┌────────┼────────┬────────┬────────┐                       │
│    ▼        ▼        ▼        ▼        ▼                        │
│ ┌──────┐┌──────┐┌──────┐┌──────┐┌──────┐                       │
│ │ TDD  ││Refac-││Plan- ││Onboa-││ ...  │                       │
│ │Orch. ││toring││ning  ││rding ││      │                       │
│ └──────┘└──────┘└──────┘└──────┘└──────┘                       │
│                                                                  │
│              Domain & Support Orchestrators                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Priority System

Priority determines orchestrator initialization order and resolution precedence:

| Priority Range | Category | Initialization |
|----------------|----------|----------------|
| 1-10 | Infrastructure | First |
| 10-50 | Core | Second |
| 60-100 | Domain | Third |
| 110-200 | Support | Last |

Lower priority = earlier initialization = higher precedence.

---

## Request Lifecycle

### Complete Request Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                      REQUEST LIFECYCLE                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. RECEIVE                                                      │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  Client → MCP Gateway → JSON-RPC validation              │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  2. AUTHENTICATE                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  API Key validation → Rate limiting → Session context     │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  3. CLASSIFY                                                     │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  IntentRouter → Keyword analysis → Confidence scoring     │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  4. ENRICH                                                       │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  LENS → Git + AST + Comments → Context synthesis          │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  5. ROUTE                                                        │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  MasterOrchestrator → Target orchestrator selection       │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  6. VALIDATE                                                     │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  EnforcementOrchestrator → Pre-execution governance       │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  7. EXECUTE                                                      │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  Target Orchestrator → Operation execution                │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  8. AUDIT                                                        │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  EnhancedAuditLogger → AC markers → Metrics emission      │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  9. RESPOND                                                      │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  Format response → Header injection → JSON-RPC response   │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Timing Breakdown

| Stage | Target | Typical |
|-------|--------|---------|
| Receive + Auth | < 10ms | 5ms |
| Classify | < 25ms | 15ms |
| Enrich (cached) | < 50ms | 30ms |
| Enrich (uncached) | < 500ms | 200ms |
| Route | < 10ms | 5ms |
| Validate | < 150ms | 100ms |
| Execute | Varies | — |
| Audit + Respond | < 20ms | 10ms |

---

## Coordination Patterns

### Pattern 1: Sequential Orchestration

Single orchestrator handles the entire request.

```
Request → IntentRouter → TDDOrchestrator → Response
```

**Use Case:** Simple IMPLEMENT or FIX requests.

### Pattern 2: Composite Orchestration

Multiple orchestrators work in sequence.

```
Request → IntentRouter → TDD → Refactoring → Documentation → Response
```

**Use Case:** "Implement AND document" composite intents.

### Pattern 3: Parallel Orchestration

Multiple orchestrators work simultaneously.

```
Request → IntentRouter ─┬→ LENS (context)
                        ├→ Knowledge (rules)
                        └→ Governance (validation)
                        │
                        ▼
                    Aggregation → Response
```

**Use Case:** Context gathering for complex operations.

### Pattern 4: Challenge-Response

Orchestrator generates challenge for user confirmation.

```
Request → IntentRouter → TDD → Challenge → User → Proceed/Modify → Execute
```

**Use Case:** High-risk or ambiguous operations.

### Pattern 5: Fallback Orchestration

Primary fails, fallback takes over.

```
Request → TDDOrchestrator (timeout) → WorkflowOrchestrator → Response
```

**Use Case:** Resilience and availability.

---

## Orchestrator Interface

All orchestrators implement `IOrchestrator`:

```python
from abc import ABC, abstractmethod
from typing import Dict, Any
from cortex.core.result import Result

class IOrchestrator(ABC):
    """Base interface for all CORTEX orchestrators."""
    
    name: str
    category: str
    priority: int
    capabilities: list
    
    @abstractmethod
    def can_handle(self, operation: str) -> bool:
        """Check if orchestrator can handle operation."""
        pass
    
    @abstractmethod
    def execute_operation(
        self,
        operation_name: str,
        parameters: Dict[str, Any],
        mode: OperationMode = OperationMode.STANDARD
    ) -> Result[Dict[str, Any], str]:
        """Execute the operation."""
        pass
```

---

## Related Documents

- [MasterOrchestrator](master-orchestrator.md) — Central coordination
- [IntentRouter](intent-router.md) — Intent classification
- [TDDOrchestrator](tdd-orchestrator.md) — TDD workflow
- [End-to-End Flow](end-to-end-flow.md) — Detailed lifecycle

---

*Part of CORTEX Architecture Documentation*
