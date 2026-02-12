# Domain Orchestrators

**Purpose:** Documentation of domain-specific orchestrators  
**Audience:** Architects, Domain Experts  
**Last Updated:** 2026-02-10

---

## Table of Contents

- [Overview](#overview)
- [RefactoringOrchestrator](#refactoringorchestrator)
- [PlanningOrchestrator](#planningorchestrator)
- [DomainOrchestrator](#domainorchestrator)
- [ConversationOrchestrator](#conversationorchestrator)
- [DocumentationOrchestrator](#documentationorchestrator)
- [ChallengeEngine](#challengeengine)
- [Cross-Domain Coordination](#cross-domain-coordination)
- [Related Documents](#related-documents)

---

## Overview

Domain orchestrators handle specialized operations within specific problem spaces. Unlike core orchestrators that handle fundamental request processing, domain orchestrators provide deep expertise in particular areas.

| Orchestrator | Priority | Focus Area |
|--------------|----------|------------|
| RefactoringOrchestrator | 50 | Code improvement |
| PlanningOrchestrator | 60 | Phase/roadmap management |
| DomainOrchestrator | 70 | Business logic operations |
| ConversationOrchestrator | 80 | Multi-turn dialogue |
| DocumentationOrchestrator | 90 | Documentation generation |
| ChallengeEngine | 100 | Decision challenges |

---

## RefactoringOrchestrator

### Purpose

Orchestrates code improvement operations while preserving behavior. Ensures refactoring follows best practices and maintains test coverage.

### Capabilities

- **Code Smell Detection** — Identify anti-patterns
- **Safe Transformations** — Behavior-preserving changes
- **Test Preservation** — Ensure tests still pass
- **Quality Metrics** — Track improvement impact

### Refactoring Types

```python
class RefactoringType(Enum):
    """Supported refactoring operations."""
    
    # Structure
    EXTRACT_METHOD = "extract_method"
    EXTRACT_CLASS = "extract_class"
    INLINE_METHOD = "inline_method"
    MOVE_METHOD = "move_method"
    
    # Naming
    RENAME_VARIABLE = "rename_variable"
    RENAME_METHOD = "rename_method"
    RENAME_CLASS = "rename_class"
    
    # Simplification
    SIMPLIFY_CONDITIONAL = "simplify_conditional"
    REMOVE_DEAD_CODE = "remove_dead_code"
    CONSOLIDATE_DUPLICATE = "consolidate_duplicate"
    
    # Design
    EXTRACT_INTERFACE = "extract_interface"
    INTRODUCE_PARAMETER_OBJECT = "introduce_parameter_object"
    REPLACE_CONDITIONAL_WITH_POLYMORPHISM = "replace_conditional_polymorphism"
```

### Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                 REFACTORING WORKFLOW                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. ANALYZE: Identify refactoring opportunities                  │
│     └── Run code smell detectors                                │
│     └── Prioritize by impact                                    │
│                                                                  │
│  2. PLAN: Create refactoring plan                               │
│     └── Order transformations                                   │
│     └── Identify test dependencies                              │
│                                                                  │
│  3. EXECUTE: Apply transformations                              │
│     └── One transformation at a time                            │
│     └── Verify tests after each                                 │
│                                                                  │
│  4. VERIFY: Confirm behavior preserved                          │
│     └── Run full test suite                                     │
│     └── Compare coverage                                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## PlanningOrchestrator

### Purpose

Manages phase lifecycle, roadmap creation, and project planning. Handles PLAN intents and provides phase resolution capabilities.

### Capabilities

- **Phase Management** — Create, update, complete phases
- **Dashboard Sync** — Real-time dashboard updates
- **Resolution** — Intelligent phase status resolution
- **Prioritization** — Phase ordering by impact

### Phase Lifecycle

```python
class PhaseStatus(Enum):
    """Phase lifecycle states."""
    
    PLANNED = "planned"           # Not yet started
    IN_PROGRESS = "in_progress"   # Active development
    BLOCKED = "blocked"           # Waiting on dependency
    COMPLETED = "completed"       # Successfully finished
    CANCELLED = "cancelled"       # Abandoned
```

### MCP Tools

```python
# Phase management tools
PLAN_TOOLS = [
    "cortex_plan_setup",     # Pre-implementation hook
    "cortex_plan_teardown",  # Post-completion hook
    "cortex_plan_resolve",   # Intelligent resolution
    "cortex_plan_sync",      # Dashboard synchronization
]
```

---

## DomainOrchestrator

### Purpose

Bridges CORTEX operations with business domain concepts. Loads and applies domain-specific knowledge from the knowledge base.

### Capabilities

- **Domain Loading** — Load domain YAML definitions
- **Terminology Mapping** — Translate business terms
- **Rule Application** — Apply domain constraints
- **Context Enhancement** — Enrich with domain knowledge

### Domain Structure

```yaml
# Example domain definition
domain: payments
version: "1.0"
terminology:
  transaction: "A financial exchange between parties"
  settlement: "Final transfer of funds"
  authorization: "Approval to proceed with transaction"

constraints:
  - name: "amount_positive"
    rule: "transaction.amount > 0"
  - name: "currency_valid"
    rule: "transaction.currency IN ['USD', 'EUR', 'GBP']"

patterns:
  - name: "idempotency"
    description: "Ensure duplicate requests are handled safely"
  - name: "saga"
    description: "Distributed transaction management"
```

---

## ConversationOrchestrator

### Purpose

Manages multi-turn conversations, maintaining context across dialogue exchanges. Enables natural, flowing interactions.

### Capabilities

- **Context Maintenance** — Track conversation history
- **Intent Continuity** — Link related intents
- **Clarification** — Request missing information
- **Summary** — Synthesize conversation outcomes

### Conversation State

```python
@dataclass
class ConversationState:
    """State maintained across conversation turns."""
    
    conversation_id: str
    turns: List[Turn]
    current_intent: Optional[IntentType]
    pending_clarifications: List[Clarification]
    context: UnifiedIntelligenceContext
    started_at: datetime
    last_activity: datetime
```

### Turn Management

```python
async def process_turn(
    self,
    message: str,
    state: ConversationState
) -> TurnResult:
    """
    Process a conversation turn.
    """
    # Add to history
    turn = Turn(
        role="user",
        content=message,
        timestamp=datetime.utcnow()
    )
    state.turns.append(turn)
    
    # Check for pending clarifications
    if state.pending_clarifications:
        return await self._handle_clarification(
            message,
            state.pending_clarifications.pop(0)
        )
    
    # Classify intent
    intent = self._classify_with_history(message, state.turns)
    
    # Route to appropriate handler
    result = await self._route_intent(intent, state)
    
    # Add response to history
    state.turns.append(Turn(
        role="assistant",
        content=result.response,
        timestamp=datetime.utcnow()
    ))
    
    return result
```

---

## DocumentationOrchestrator

### Purpose

Generates and maintains documentation artifacts. Handles DOCUMENT intents and ensures documentation quality.

### Capabilities

- **Doc Generation** — Create documentation
- **API Docs** — Generate API references
- **README Creation** — Project documentation
- **Diagram Generation** — Visual documentation

### Documentation Types

| Type | Output | Trigger |
|------|--------|---------|
| **API Docs** | OpenAPI spec | `/document api` |
| **Code Docs** | Docstrings | `/document code` |
| **README** | Markdown | `/document readme` |
| **Architecture** | Diagrams | `/document architecture` |

### Quality Checks

```python
def validate_documentation(self, doc: Documentation) -> ValidationResult:
    """
    Validate documentation meets quality standards.
    """
    issues = []
    
    # Check completeness
    if not doc.has_overview:
        issues.append("Missing overview section")
    
    if not doc.has_examples:
        issues.append("Missing examples")
    
    # Check accuracy
    for code_block in doc.code_blocks:
        if not self._validate_code(code_block):
            issues.append(f"Invalid code block: {code_block.id}")
    
    # Check readability
    readability = self._calculate_readability(doc.content)
    if readability < 0.6:
        issues.append(f"Low readability score: {readability}")
    
    return ValidationResult(
        valid=len(issues) == 0,
        issues=issues
    )
```

---

## ChallengeEngine

### Purpose

Generates challenges for decisions requiring verification. Ensures important decisions are validated before execution.

### Capabilities

- **Challenge Generation** — Create decision challenges
- **Disagreement Detection** — Identify conflicting signals
- **Validation** — Verify decision correctness
- **Learning** — Improve from challenge outcomes

### Challenge Types

```python
class ChallengeType(Enum):
    """Types of challenges."""
    
    DESIGN_DECISION = "design_decision"
    ARCHITECTURE_CHOICE = "architecture_choice"
    SECURITY_CONCERN = "security_concern"
    PERFORMANCE_IMPACT = "performance_impact"
    BREAKING_CHANGE = "breaking_change"
    GOVERNANCE_OVERRIDE = "governance_override"
```

### Challenge Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                   CHALLENGE FLOW                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. DETECT: Identify challengeable decision                     │
│     └── Confidence < 0.7                                        │
│     └── Conflicting signals                                     │
│     └── High-impact operation                                   │
│                                                                  │
│  2. GENERATE: Create challenge                                  │
│     └── Formulate question                                      │
│     └── Provide alternatives                                    │
│     └── Present evidence                                        │
│                                                                  │
│  3. PRESENT: Display to user                                    │
│     └── Clear explanation                                       │
│     └── Decision options                                        │
│     └── Recommendation                                          │
│                                                                  │
│  4. RESOLVE: Handle response                                    │
│     └── Accept recommendation                                   │
│     └── Choose alternative                                      │
│     └── Provide clarification                                   │
│                                                                  │
│  5. LEARN: Update models                                        │
│     └── Record outcome                                          │
│     └── Adjust confidence                                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Cross-Domain Coordination

### Inter-Domain Communication

Domain orchestrators coordinate through:

1. **Event Bus** — Async event propagation
2. **Shared Context** — UnifiedIntelligenceContext
3. **Priority Queue** — Ordered execution
4. **Result Aggregation** — Combined outcomes

### Example: Document After Refactor

```python
async def coordinate_refactor_document(
    self,
    target: str,
    context: UnifiedIntelligenceContext
) -> CoordinatedResult:
    """
    Coordinate refactoring followed by documentation.
    """
    # Step 1: Refactor
    refactor_result = await self.refactoring_orchestrator.execute(
        target=target,
        context=context
    )
    
    if not refactor_result.success:
        return CoordinatedResult(
            success=False,
            phase="refactoring",
            error=refactor_result.error
        )
    
    # Step 2: Update documentation
    doc_result = await self.documentation_orchestrator.execute(
        target=target,
        changes=refactor_result.changes,
        context=context
    )
    
    return CoordinatedResult(
        success=doc_result.success,
        refactoring=refactor_result,
        documentation=doc_result
    )
```

---

## Related Documents

- [Orchestration Overview](overview.md) — Architecture
- [MasterOrchestrator](master-orchestrator.md) — Coordination
- [Support Orchestrators](support-orchestrators.md) — Support functions

---

*Part of CORTEX Architecture Documentation*
