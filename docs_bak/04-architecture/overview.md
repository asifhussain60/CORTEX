# Architecture Overview

## System Design

CORTEX is built on a **4-tier governance model** with **specialized orchestrators** for different workflows.

### Tier 0: Immutable Governance
Contains 29 CORE rules that enforce:
- TDD (tests before code)
- Type hints (mandatory)
- Docstring standards (Google style)
- No bare except clauses
- Git checkpoints before major changes
- Audit trails (AC_START → AC_COMPLETE)

### Tier 1: Acceptance Criteria
AC-ID specifications for:
- Phase definitions
- Delivery requirements
- Quality gates
- Approval workflows

### Tier 2: Response Templates & Boundaries
Prevents hallucination by:
- Enforcing response formats
- Limiting scope creep
- Validating outputs
- Boundary enforcement

### Tier 3: Knowledge & Best Practices
Domain-specific intelligence:
- 35+ YAML files
- TDD patterns
- Refactoring guides
- API design principles
- Security best practices

## Core Components

### Orchestrators (23 total)

#### Tier 0: Core Orchestrators
- **MasterOrchestrator** - Main execution hub, coordinates all operations
- **IntentRouter** - Classifies requests using LENS framework
- **TDDOrchestrator** - Test-driven development workflow
- **WorkflowOrchestrator** - Manages complex workflows

#### Tier 1: Domain Orchestrators
- **RefactoringOrchestrator** - Code refactoring automation
- **PlanningOrchestrator** - Project planning
- **DomainOrchestrator** - Domain-specific operations

#### Tier 2: Support Orchestrators
- **OnboardingOrchestrator** - New project setup
- **SetupOrchestrator** - Environment configuration
- **UpgradeOrchestrator** - Version upgrades

### MCP Tools (15 active)

Located in `cortex/mcp/tools/`:
- **governance_tools** - Rule evaluation and policy enforcement
- **deployment_tools** - Canary, rollback, health checks
- **multi_repo_tools** - Cross-repository operations
- **knowledge_tools** - Knowledge graph operations

### Infrastructure

Key components supporting operations:
- **EnhancedAuditLogger** - Immutable audit trail
- **CircuitBreaker** - Fault tolerance
- **StateManager** - Stateful execution
- **GovernanceRegistry** - Rule management
- **KnowledgeRepository** - Best practices database

## Data Flow

```
Request
  ↓
[IntentRouter (LENS)] → Classify intent type
  ↓
[Approval Gate] → Check complexity, get approval if needed
  ↓
[Select Orchestrator] → Route to appropriate handler
  ↓
[Execute] → Run with CORE rules applied
  ↓
[Audit Trail] → Log AC_START → AC_COMPLETE
  ↓
Response
```

## Governance Model

All operations flow through:

1. **Intent Classification** (LENS: Language → Examination → Navigation → Synthesis)
2. **Definition of Ready (DoR)** - Approval gate with complexity assessment
3. **CORE Rules Enforcement** - 29 immutable rules
4. **Audit Trail** - Operation start/complete logging
5. **Result Reporting** - With compliance status

---

Next: [Brain Tier Architecture](brain-tiers.md)
