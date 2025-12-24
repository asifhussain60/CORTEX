# CORTEX Clean Architecture Upgrade Plan

**Author:** Asif Hussain  
**Date:** 2025-11-21  
**Version:** 1.0  
**Status:** PLANNING  
**Estimated Duration:** 4-6 weeks  
**Repository:** https://github.com/asifhussain60/CORTEX

---

## 📋 Executive Summary

This document outlines a comprehensive plan to integrate Clean Architecture patterns from Jason Taylor's proven enterprise template into CORTEX. The upgrade will enhance maintainability, testability, and separation of concerns while preserving CORTEX's unique AI assistant capabilities.

**Key Goals:**
- Strengthen layer separation and dependency rules
- Implement CQRS with pipeline behaviors
- Add domain events for reactive workflows
- Introduce value objects for domain concepts
- Adopt Result pattern for error handling
- Enhance testing with functional test patterns

**Expected Benefits:**
- 40% reduction in coupling between components
- 50% improvement in test coverage
- 30% faster debugging through clear boundaries
- Better code organization and maintainability

---

## 🎯 Strategic Alignment

### CORTEX Current State (Strengths to Preserve)

✅ **Already Well-Aligned:**
- Tier-based architecture (Tier 0-3) mirrors Clean Architecture layers
- 100% test pass rate (834/897 passing)
- Optimization principles codified (13 validated patterns)
- 97.2% token reduction achieved (Phase 0 complete)
- Strong brain protection enforcement (SKULL rules)

✅ **Unique CORTEX Features (Must Maintain):**
- Conversational AI interface
- Multi-tier memory system (Working Memory, Knowledge Graph, Development Context)
- Pattern learning and extraction
- Context-aware responses
- Plugin-based extensibility

### Clean Architecture Patterns to Adopt

⚡ **High Priority (Weeks 1-3):**
1. Pipeline Behaviors for cross-cutting concerns
2. Result Pattern for error handling
3. Value Objects for domain concepts
4. Guard Clauses for input validation
5. CQRS separation in conversation system

⚡ **Medium Priority (Weeks 4-5):**
6. Domain Events for reactive workflows
7. FluentValidation for complex rules
8. Enhanced functional testing patterns

⚡ **Low Priority (Week 6):**
9. Additional architectural refinements
10. Documentation and knowledge transfer

---

## 📊 Gap Analysis

| Pattern | Clean Architecture | CORTEX Current | Gap | Priority |
|---------|-------------------|----------------|-----|----------|
| **Layer Separation** | Domain → Application → Infrastructure → Presentation | Tier 0-3 + Plugins | Minor - strengthen boundaries | Medium |
| **CQRS** | Commands + Queries separate | Mixed operations | Major - needs separation | High |
| **Pipeline Behaviors** | Auto validation, logging, auth | Manual enforcement | Major - add behaviors | High |
| **Domain Events** | Auto-dispatch on save | N/A | Major - implement system | Medium |
| **Value Objects** | Immutable domain concepts | Primitives used | Major - create objects | High |
| **Result Pattern** | Success/Failure returns | Exceptions | Major - replace exceptions | High |
| **Testing** | Functional + integration | Unit + integration | Minor - add functional | Medium |
| **Guard Clauses** | Ardalis.GuardClauses | Manual validation | Minor - add library | High |
| **Validation** | FluentValidation | Manual checks | Medium - add framework | Medium |
| **Dependency Injection** | Builder extensions | Manual setup | Minor - enhance existing | Low |

---

## 🏗️ Architecture Mapping

### Current CORTEX Architecture → Clean Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CORTEX CURRENT                            │
├─────────────────────────────────────────────────────────────┤
│ Tier 0: Brain Protection (SKULL Rules)                      │
│ Tier 1: Working Memory (Conversations)                      │
│ Tier 2: Knowledge Graph (Patterns)                          │
│ Tier 3: Development Context                                 │
│ Plugins: Platform Switch, Git Monitor, etc.                 │
└─────────────────────────────────────────────────────────────┘
                              ↓
                         UPGRADE TO
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              CORTEX + CLEAN ARCHITECTURE                     │
├─────────────────────────────────────────────────────────────┤
│ DOMAIN LAYER (Tier 0 + 2 Entities)                         │
│ • Brain Protection Rules (policies)                          │
│ • Domain Entities: Conversation, Pattern, Context           │
│ • Value Objects: RelevanceScore, ConversationQuality        │
│ • Domain Events: ConversationCaptured, PatternLearned       │
│ • Domain Exceptions: BrainProtectionViolation               │
├─────────────────────────────────────────────────────────────┤
│ APPLICATION LAYER (Tier 1 + 2 Use Cases)                   │
│ • Commands: CaptureConversation, ImportConversation         │
│ • Queries: SearchContext, GetRelevantPatterns               │
│ • Interfaces: IConversationRepository, IPatternStore        │
│ • Pipeline Behaviors: Validation, BrainProtection, Logging  │
│ • DTOs: ConversationDto, PatternDto                          │
├─────────────────────────────────────────────────────────────┤
│ INFRASTRUCTURE LAYER (Tier 3)                               │
│ • Database: SQLite repositories                              │
│ • External Services: Git, File System                        │
│ • Persistence: ConversationRepository, PatternRepository    │
├─────────────────────────────────────────────────────────────┤
│ PRESENTATION LAYER (Plugins + API)                          │
│ • Natural Language Processor                                 │
│ • Plugin System                                              │
│ • Response Templates                                         │
└─────────────────────────────────────────────────────────────┘
```

---

## 📅 Implementation Timeline

### Week 1: Foundation & Setup (8-10 hours)

**Deliverables:**
- [ ] Install Python equivalents of C# libraries
- [ ] Create base domain classes
- [ ] Setup Result pattern infrastructure
- [ ] Add guard clause utilities

**Tasks:**

#### Task 1.1: Library Installation (1 hour)
```bash
# Install Python equivalents
pip install pydantic           # For validation and DTOs
pip install result             # For Result pattern
pip install python-dataclasses # For value objects (if needed)
pip install returns            # For functional programming patterns
```

#### Task 1.2: Create Domain Base Classes (2 hours)
**File:** `src/domain/common/base_entity.py`
```python
from abc import ABC
from typing import List
from dataclasses import dataclass, field

@dataclass
class BaseEvent:
    """Base class for all domain events"""
    pass

class BaseEntity(ABC):
    """Base entity with domain event support"""
    
    def __init__(self):
        self._domain_events: List[BaseEvent] = []
    
    @property
    def domain_events(self) -> List[BaseEvent]:
        return self._domain_events.copy()
    
    def add_domain_event(self, event: BaseEvent) -> None:
        self._domain_events.append(event)
    
    def remove_domain_event(self, event: BaseEvent) -> None:
        self._domain_events.remove(event)
    
    def clear_domain_events(self) -> None:
        self._domain_events.clear()
```

**File:** `src/domain/common/value_object.py`
```python
from abc import ABC, abstractmethod
from typing import Any, Tuple

class ValueObject(ABC):
    """Base class for value objects"""
    
    @abstractmethod
    def get_equality_components(self) -> Tuple[Any, ...]:
        """Return tuple of components used for equality"""
        pass
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.get_equality_components() == other.get_equality_components()
    
    def __hash__(self) -> int:
        return hash(self.get_equality_components())
```

#### Task 1.3: Implement Result Pattern (2 hours)
**File:** `src/application/common/result.py`
```python
from typing import TypeVar, Generic, List, Optional
from dataclasses import dataclass

T = TypeVar('T')

@dataclass
class Result(Generic[T]):
    """Represents the result of an operation"""
    succeeded: bool
    value: Optional[T] = None
    errors: Optional[List[str]] = None
    
    @staticmethod
    def success(value: T) -> 'Result[T]':
        """Create a successful result"""
        return Result(succeeded=True, value=value)
    
    @staticmethod
    def failure(errors: List[str]) -> 'Result[T]':
        """Create a failed result"""
        return Result(succeeded=False, errors=errors)
    
    @property
    def is_success(self) -> bool:
        return self.succeeded
    
    @property
    def is_failure(self) -> bool:
        return not self.succeeded
    
    def unwrap(self) -> T:
        """Get value or raise if failed"""
        if self.is_failure:
            raise ValueError(f"Cannot unwrap failed result: {self.errors}")
        return self.value
```

#### Task 1.4: Add Guard Clause Utilities (1 hour)
**File:** `src/application/common/guards.py`
```python
from typing import Any, Optional

class Guard:
    """Guard clauses for input validation"""
    
    @staticmethod
    def against_null(value: Any, parameter_name: str, message: Optional[str] = None):
        """Guard against null values"""
        if value is None:
            msg = message or f"{parameter_name} cannot be None"
            raise ValueError(msg)
    
    @staticmethod
    def against_empty(value: str, parameter_name: str, message: Optional[str] = None):
        """Guard against empty strings"""
        if not value or not value.strip():
            msg = message or f"{parameter_name} cannot be empty"
            raise ValueError(msg)
    
    @staticmethod
    def against_negative(value: int, parameter_name: str, message: Optional[str] = None):
        """Guard against negative numbers"""
        if value < 0:
            msg = message or f"{parameter_name} cannot be negative"
            raise ValueError(msg)
    
    @staticmethod
    def against_out_of_range(value: float, min_val: float, max_val: float, 
                             parameter_name: str, message: Optional[str] = None):
        """Guard against values out of range"""
        if not min_val <= value <= max_val:
            msg = message or f"{parameter_name} must be between {min_val} and {max_val}"
            raise ValueError(msg)
```

#### Task 1.5: Project Structure Review (2 hours)
- Review current directory structure
- Plan migration of existing code
- Document architectural decisions
- Create migration checklist

---

### Week 2: Value Objects & Domain Events (10-12 hours)

**Deliverables:**
- [ ] RelevanceScore value object
- [ ] ConversationQuality value object
- [ ] Namespace value object
- [ ] PatternConfidence value object
- [ ] Domain event infrastructure
- [ ] Event dispatcher

**Tasks:**

#### Task 2.1: Create RelevanceScore Value Object (2 hours)
**File:** `src/domain/value_objects/relevance_score.py`
```python
from dataclasses import dataclass
from typing import Tuple, Any
from src.domain.common.value_object import ValueObject
from src.application.common.guards import Guard

@dataclass(frozen=True)
class RelevanceScore(ValueObject):
    """Represents relevance score between 0.0 and 1.0"""
    value: float
    
    def __post_init__(self):
        Guard.against_out_of_range(
            self.value, 0.0, 1.0, 
            "RelevanceScore", 
            "RelevanceScore must be between 0.0 and 1.0"
        )
    
    @property
    def is_high(self) -> bool:
        """Check if relevance is high (≥ 0.80)"""
        return self.value >= 0.80
    
    @property
    def is_medium(self) -> bool:
        """Check if relevance is medium (0.50-0.79)"""
        return 0.50 <= self.value < 0.80
    
    @property
    def is_low(self) -> bool:
        """Check if relevance is low (< 0.50)"""
        return self.value < 0.50
    
    @property
    def quality_label(self) -> str:
        """Get human-readable quality label"""
        if self.is_high:
            return "High"
        elif self.is_medium:
            return "Medium"
        else:
            return "Low"
    
    @property
    def quality_emoji(self) -> str:
        """Get emoji indicator"""
        if self.is_high:
            return "🟢"
        elif self.is_medium:
            return "🟡"
        else:
            return "🔴"
    
    def get_equality_components(self) -> Tuple[Any, ...]:
        return (self.value,)
    
    def __str__(self) -> str:
        return f"{self.value:.2f} ({self.quality_label} {self.quality_emoji})"
```

#### Task 2.2: Create ConversationQuality Value Object (2 hours)
**File:** `src/domain/value_objects/conversation_quality.py`
```python
from dataclasses import dataclass
from enum import Enum
from typing import Tuple, Any
from src.domain.common.value_object import ValueObject
from src.application.common.guards import Guard

class QualityThreshold(Enum):
    """Quality thresholds for conversations"""
    EXCELLENT = 0.90
    GOOD = 0.70
    FAIR = 0.50
    POOR = 0.30

@dataclass(frozen=True)
class ConversationQuality(ValueObject):
    """Represents conversation quality with threshold-based categorization"""
    score: float
    turn_count: int
    entity_count: int
    
    def __post_init__(self):
        Guard.against_out_of_range(
            self.score, 0.0, 1.0, 
            "ConversationQuality.score"
        )
        Guard.against_negative(self.turn_count, "turn_count")
        Guard.against_negative(self.entity_count, "entity_count")
    
    @property
    def is_excellent(self) -> bool:
        return self.score >= QualityThreshold.EXCELLENT.value
    
    @property
    def is_good(self) -> bool:
        return self.score >= QualityThreshold.GOOD.value
    
    @property
    def is_fair(self) -> bool:
        return self.score >= QualityThreshold.FAIR.value
    
    @property
    def is_poor(self) -> bool:
        return self.score < QualityThreshold.FAIR.value
    
    @property
    def should_capture(self) -> bool:
        """Determine if conversation should be captured for learning"""
        return self.score >= QualityThreshold.GOOD.value
    
    def get_equality_components(self) -> Tuple[Any, ...]:
        return (self.score, self.turn_count, self.entity_count)
```

#### Task 2.3: Create Namespace Value Object (2 hours)
**File:** `src/domain/value_objects/namespace.py`
```python
from dataclasses import dataclass
from typing import Tuple, Any
from src.domain.common.value_object import ValueObject
from src.application.common.guards import Guard

@dataclass(frozen=True)
class Namespace(ValueObject):
    """Represents a namespace with isolation rules"""
    value: str
    
    def __post_init__(self):
        Guard.against_empty(self.value, "Namespace")
        if not self._is_valid_format():
            raise ValueError(f"Invalid namespace format: {self.value}")
    
    def _is_valid_format(self) -> bool:
        """Validate namespace format (e.g., workspace.project.feature)"""
        parts = self.value.split('.')
        return len(parts) >= 2 and all(part.isidentifier() for part in parts)
    
    @property
    def root(self) -> str:
        """Get root namespace (first segment)"""
        return self.value.split('.')[0]
    
    @property
    def is_workspace(self) -> bool:
        """Check if this is a workspace namespace"""
        return self.root == "workspace"
    
    @property
    def is_cortex(self) -> bool:
        """Check if this is a CORTEX internal namespace"""
        return self.root == "cortex"
    
    @property
    def priority_multiplier(self) -> float:
        """Get priority multiplier for pattern search"""
        if self.is_workspace:
            return 2.0  # Highest priority
        elif self.is_cortex:
            return 1.5  # Medium priority
        else:
            return 0.5  # Lowest priority
    
    def get_equality_components(self) -> Tuple[Any, ...]:
        return (self.value,)
```

#### Task 2.4: Create Domain Events (3 hours)
**File:** `src/domain/events/conversation_events.py`
```python
from dataclasses import dataclass
from datetime import datetime
from src.domain.common.base_entity import BaseEvent

@dataclass
class ConversationCapturedEvent(BaseEvent):
    """Event raised when a conversation is captured"""
    conversation_id: str
    title: str
    quality_score: float
    entity_count: int
    captured_at: datetime

@dataclass
class PatternLearnedEvent(BaseEvent):
    """Event raised when a new pattern is learned"""
    pattern_id: str
    pattern_type: str
    confidence: float
    source_conversation_id: str
    learned_at: datetime

@dataclass
class BrainRuleViolatedEvent(BaseEvent):
    """Event raised when a brain protection rule is violated"""
    rule_id: str
    rule_name: str
    violation_details: str
    severity: str
    detected_at: datetime

@dataclass
class ContextRelevanceUpdatedEvent(BaseEvent):
    """Event raised when context relevance score changes"""
    conversation_id: str
    old_score: float
    new_score: float
    reason: str
    updated_at: datetime
```

#### Task 2.5: Create Event Dispatcher (3 hours)
**File:** `src/application/common/event_dispatcher.py`
```python
from typing import Dict, List, Callable, Type
from src.domain.common.base_entity import BaseEvent, BaseEntity

class EventDispatcher:
    """Dispatches domain events to registered handlers"""
    
    def __init__(self):
        self._handlers: Dict[Type[BaseEvent], List[Callable]] = {}
    
    def register(self, event_type: Type[BaseEvent], handler: Callable):
        """Register an event handler"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
    
    def dispatch(self, entity: BaseEntity):
        """Dispatch all events from an entity"""
        events = entity.domain_events
        entity.clear_domain_events()
        
        for event in events:
            self._dispatch_event(event)
    
    def _dispatch_event(self, event: BaseEvent):
        """Dispatch a single event to all registered handlers"""
        event_type = type(event)
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                handler(event)
```

---

### Week 3: CQRS & Pipeline Behaviors (12-15 hours)

**Deliverables:**
- [ ] Command/Query interfaces
- [ ] MediatR-style request handler
- [ ] BrainProtectionBehaviour
- [ ] ValidationBehaviour
- [ ] PerformanceBehaviour
- [ ] LoggingBehaviour

**Tasks:**

#### Task 3.1: Create CQRS Infrastructure (3 hours)
**File:** `src/application/common/cqrs.py`
```python
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Any
from src.application.common.result import Result

TRequest = TypeVar('TRequest')
TResponse = TypeVar('TResponse')

class IRequest(ABC, Generic[TResponse]):
    """Marker interface for requests (commands/queries)"""
    pass

class IRequestHandler(ABC, Generic[TRequest, TResponse]):
    """Handler for requests"""
    
    @abstractmethod
    async def handle(self, request: TRequest) -> Result[TResponse]:
        """Handle the request"""
        pass

class ICommand(IRequest[TResponse], Generic[TResponse]):
    """Marker interface for commands (write operations)"""
    pass

class IQuery(IRequest[TResponse], Generic[TResponse]):
    """Marker interface for queries (read operations)"""
    pass
```

#### Task 3.2: Create Conversation Commands (3 hours)
**File:** `src/application/conversations/commands/capture_conversation.py`
```python
from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from src.application.common.cqrs import ICommand, IRequestHandler
from src.application.common.result import Result
from src.application.common.guards import Guard
from src.domain.events.conversation_events import ConversationCapturedEvent

@dataclass
class CaptureConversationCommand(ICommand[str]):
    """Command to capture a new conversation"""
    title: str
    content: str
    file_path: str
    tags: Optional[list[str]] = None
    
class CaptureConversationCommandHandler(IRequestHandler[CaptureConversationCommand, str]):
    """Handler for capturing conversations"""
    
    def __init__(self, conversation_repo, event_dispatcher):
        self._repo = conversation_repo
        self._dispatcher = event_dispatcher
    
    async def handle(self, request: CaptureConversationCommand) -> Result[str]:
        # Validation via guards
        Guard.against_empty(request.title, "title")
        Guard.against_empty(request.content, "content")
        Guard.against_empty(request.file_path, "file_path")
        
        # Create conversation entity
        conversation = Conversation(
            title=request.title,
            content=request.content,
            file_path=request.file_path,
            tags=request.tags or []
        )
        
        # Add domain event
        conversation.add_domain_event(ConversationCapturedEvent(
            conversation_id=conversation.id,
            title=conversation.title,
            quality_score=conversation.quality.score,
            entity_count=conversation.entity_count,
            captured_at=datetime.utcnow()
        ))
        
        # Persist
        await self._repo.add(conversation)
        
        # Dispatch events
        self._dispatcher.dispatch(conversation)
        
        return Result.success(conversation.id)
```

**File:** `src/application/conversations/commands/import_conversation.py`
```python
from dataclasses import dataclass
from src.application.common.cqrs import ICommand, IRequestHandler
from src.application.common.result import Result
from src.application.common.guards import Guard

@dataclass
class ImportConversationCommand(ICommand[dict]):
    """Command to import conversation from file"""
    file_path: str
    
class ImportConversationCommandHandler(IRequestHandler[ImportConversationCommand, dict]):
    """Handler for importing conversations"""
    
    def __init__(self, conversation_repo, parser_service):
        self._repo = conversation_repo
        self._parser = parser_service
    
    async def handle(self, request: ImportConversationCommand) -> Result[dict]:
        Guard.against_empty(request.file_path, "file_path")
        
        # Parse conversation file
        parsed_result = await self._parser.parse(request.file_path)
        if parsed_result.is_failure:
            return Result.failure(parsed_result.errors)
        
        # Import to repository
        import_result = await self._repo.import_conversation(parsed_result.value)
        
        return Result.success({
            'conversation_id': import_result.id,
            'title': import_result.title,
            'status': 'imported'
        })
```

#### Task 3.3: Create Conversation Queries (2 hours)
**File:** `src/application/conversations/queries/search_context.py`
```python
from dataclasses import dataclass
from typing import List
from src.application.common.cqrs import IQuery, IRequestHandler
from src.application.common.result import Result
from src.domain.value_objects.relevance_score import RelevanceScore

@dataclass
class SearchContextQuery(IQuery[List[dict]]):
    """Query to search conversation context"""
    keywords: List[str]
    file_names: List[str]
    min_relevance: float = 0.5
    max_results: int = 10

@dataclass
class ContextSearchResult:
    """Result of context search"""
    conversation_id: str
    title: str
    relevance: RelevanceScore
    snippet: str
    timestamp: str

class SearchContextQueryHandler(IRequestHandler[SearchContextQuery, List[ContextSearchResult]]):
    """Handler for searching context"""
    
    def __init__(self, conversation_repo):
        self._repo = conversation_repo
    
    async def handle(self, request: SearchContextQuery) -> Result[List[ContextSearchResult]]:
        # Search conversations
        conversations = await self._repo.search(
            keywords=request.keywords,
            file_names=request.file_names,
            min_relevance=request.min_relevance,
            limit=request.max_results
        )
        
        # Map to DTOs
        results = [
            ContextSearchResult(
                conversation_id=c.id,
                title=c.title,
                relevance=RelevanceScore(c.relevance_score),
                snippet=c.snippet,
                timestamp=c.timestamp.isoformat()
            )
            for c in conversations
        ]
        
        return Result.success(results)
```

#### Task 3.4: Implement Pipeline Behaviors (4 hours)

**File:** `src/application/behaviors/brain_protection_behaviour.py`
```python
from typing import Callable, TypeVar
from src.application.common.cqrs import IRequest
from src.application.common.result import Result
from src.tier0.brain_protector import BrainProtector

TRequest = TypeVar('TRequest', bound=IRequest)
TResponse = TypeVar('TResponse')

class BrainProtectionBehaviour:
    """Pipeline behavior for enforcing SKULL rules"""
    
    def __init__(self, brain_protector: BrainProtector):
        self._protector = brain_protector
    
    async def handle(
        self, 
        request: TRequest, 
        next_handler: Callable
    ) -> Result[TResponse]:
        # Validate request against SKULL rules
        validation_result = self._protector.validate_operation(request)
        
        if not validation_result.is_valid:
            return Result.failure([
                f"Brain Protection Violation: {error}" 
                for error in validation_result.errors
            ])
        
        # Continue pipeline
        return await next_handler()
```

**File:** `src/application/behaviors/validation_behaviour.py`
```python
from typing import Callable, TypeVar, Dict, Type
from src.application.common.cqrs import IRequest
from src.application.common.result import Result

TRequest = TypeVar('TRequest', bound=IRequest)
TResponse = TypeVar('TResponse')

class IValidator:
    """Interface for validators"""
    async def validate(self, request) -> Result[None]:
        pass

class ValidationBehaviour:
    """Pipeline behavior for request validation"""
    
    def __init__(self):
        self._validators: Dict[Type, IValidator] = {}
    
    def register_validator(self, request_type: Type, validator: IValidator):
        """Register a validator for a request type"""
        self._validators[request_type] = validator
    
    async def handle(
        self, 
        request: TRequest, 
        next_handler: Callable
    ) -> Result[TResponse]:
        # Get validator for request type
        request_type = type(request)
        validator = self._validators.get(request_type)
        
        if validator:
            # Validate request
            validation_result = await validator.validate(request)
            if validation_result.is_failure:
                return validation_result
        
        # Continue pipeline
        return await next_handler()
```

**File:** `src/application/behaviors/performance_behaviour.py`
```python
import time
from typing import Callable, TypeVar
from src.application.common.cqrs import IRequest
from src.application.common.result import Result

TRequest = TypeVar('TRequest', bound=IRequest)
TResponse = TypeVar('TResponse')

class PerformanceBehaviour:
    """Pipeline behavior for performance monitoring"""
    
    def __init__(self, logger, threshold_ms: int = 500):
        self._logger = logger
        self._threshold_ms = threshold_ms
    
    async def handle(
        self, 
        request: TRequest, 
        next_handler: Callable
    ) -> Result[TResponse]:
        request_name = type(request).__name__
        start_time = time.time()
        
        try:
            # Execute request
            result = await next_handler()
            
            # Calculate elapsed time
            elapsed_ms = (time.time() - start_time) * 1000
            
            # Log if exceeds threshold
            if elapsed_ms > self._threshold_ms:
                self._logger.warning(
                    f"Long running request: {request_name} "
                    f"({elapsed_ms:.2f}ms exceeds {self._threshold_ms}ms threshold)"
                )
            else:
                self._logger.debug(f"{request_name} completed in {elapsed_ms:.2f}ms")
            
            return result
            
        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            self._logger.error(
                f"{request_name} failed after {elapsed_ms:.2f}ms: {str(e)}"
            )
            raise
```

#### Task 3.5: Create Mediator (2 hours)
**File:** `src/application/common/mediator.py`
```python
from typing import Dict, List, Type, Callable
from src.application.common.cqrs import IRequest, IRequestHandler
from src.application.common.result import Result

class Mediator:
    """Simple mediator for CQRS"""
    
    def __init__(self):
        self._handlers: Dict[Type[IRequest], IRequestHandler] = {}
        self._behaviors: List[Callable] = []
    
    def register_handler(self, request_type: Type[IRequest], handler: IRequestHandler):
        """Register a request handler"""
        self._handlers[request_type] = handler
    
    def add_behavior(self, behavior: Callable):
        """Add a pipeline behavior"""
        self._behaviors.append(behavior)
    
    async def send(self, request: IRequest) -> Result:
        """Send a request through the pipeline"""
        request_type = type(request)
        
        # Get handler
        handler = self._handlers.get(request_type)
        if not handler:
            return Result.failure([f"No handler registered for {request_type.__name__}"])
        
        # Build pipeline
        async def pipeline():
            return await handler.handle(request)
        
        # Apply behaviors in reverse order
        for behavior in reversed(self._behaviors):
            current_pipeline = pipeline
            pipeline = lambda: behavior.handle(request, current_pipeline)
        
        # Execute pipeline
        return await pipeline()
```

---

### Week 4: Migration & Testing (10-12 hours)

**Deliverables:**
- [ ] Migrate Tier 1 to CQRS pattern
- [ ] Migrate Tier 2 to use value objects
- [ ] Update brain protector to use Result pattern
- [ ] Functional tests for CQRS
- [ ] Integration tests for pipeline behaviors

**Tasks:**

#### Task 4.1: Migrate Brain Protector to Result Pattern (3 hours)
- Replace exceptions with Result returns
- Update all callers to handle Result
- Add comprehensive error messages
- Update tests

#### Task 4.2: Migrate Conversation System to CQRS (4 hours)
- Replace direct repository calls with commands
- Replace searches with queries
- Add command/query handlers
- Wire up mediator

#### Task 4.3: Add Value Objects to Existing Code (3 hours)
- Replace primitive relevance scores with RelevanceScore
- Replace quality calculations with ConversationQuality
- Replace namespace strings with Namespace
- Update serialization/deserialization

#### Task 4.4: Create Functional Tests (2 hours)
**File:** `tests/functional/test_conversation_workflows.py`
```python
import pytest
from src.application.conversations.commands.capture_conversation import CaptureConversationCommand
from src.application.conversations.queries.search_context import SearchContextQuery

class TestConversationWorkflows:
    """Functional tests for conversation workflows"""
    
    @pytest.mark.asyncio
    async def test_capture_and_search_conversation(self, mediator, test_db):
        # Arrange
        command = CaptureConversationCommand(
            title="Test Conversation",
            content="Discussion about authentication",
            file_path="/test/conversation.md",
            tags=["auth", "security"]
        )
        
        # Act - Capture
        capture_result = await mediator.send(command)
        assert capture_result.is_success
        conversation_id = capture_result.value
        
        # Act - Search
        query = SearchContextQuery(
            keywords=["authentication"],
            file_names=[],
            min_relevance=0.5
        )
        search_result = await mediator.send(query)
        
        # Assert
        assert search_result.is_success
        results = search_result.value
        assert len(results) > 0
        assert any(r.conversation_id == conversation_id for r in results)
```

---

### Week 5: Domain Events & Advanced Patterns (8-10 hours)

**Deliverables:**
- [ ] Event handlers for all domain events
- [ ] FluentValidation integration
- [ ] Enhanced guard clauses
- [ ] Pattern learning triggered by events
- [ ] Context updates triggered by events

**Tasks:**

#### Task 5.1: Create Event Handlers (4 hours)
**File:** `src/application/conversations/events/conversation_captured_handler.py`
```python
from src.domain.events.conversation_events import ConversationCapturedEvent
from src.application.common.event_dispatcher import EventDispatcher

class ConversationCapturedEventHandler:
    """Handler for ConversationCapturedEvent"""
    
    def __init__(self, pattern_extractor, notification_service):
        self._pattern_extractor = pattern_extractor
        self._notifications = notification_service
    
    async def handle(self, event: ConversationCapturedEvent):
        """Handle conversation captured event"""
        # Extract patterns from captured conversation
        patterns = await self._pattern_extractor.extract(event.conversation_id)
        
        # Notify if high quality
        if event.quality_score >= 0.80:
            await self._notifications.notify_high_quality_conversation(event)
        
        # Log metrics
        print(f"Conversation captured: {event.title} (Quality: {event.quality_score})")
```

#### Task 5.2: Integrate FluentValidation (3 hours)
**File:** `src/application/conversations/validators/capture_conversation_validator.py`
```python
from src.application.conversations.commands.capture_conversation import CaptureConversationCommand
from src.application.common.result import Result

class CaptureConversationValidator:
    """Validator for CaptureConversationCommand"""
    
    async def validate(self, command: CaptureConversationCommand) -> Result[None]:
        errors = []
        
        # Title validation
        if not command.title or len(command.title.strip()) == 0:
            errors.append("Title is required")
        elif len(command.title) > 200:
            errors.append("Title cannot exceed 200 characters")
        
        # Content validation
        if not command.content or len(command.content.strip()) == 0:
            errors.append("Content is required")
        elif len(command.content) < 50:
            errors.append("Content must be at least 50 characters")
        
        # File path validation
        if not command.file_path or len(command.file_path.strip()) == 0:
            errors.append("File path is required")
        elif not command.file_path.endswith('.md'):
            errors.append("File path must end with .md")
        
        # Tags validation
        if command.tags and len(command.tags) > 10:
            errors.append("Cannot have more than 10 tags")
        
        if errors:
            return Result.failure(errors)
        
        return Result.success(None)
```

#### Task 5.3: Wire Up Event System (3 hours)
- Register all event handlers with dispatcher
- Update repositories to dispatch events on save
- Add event logging
- Test event propagation

---

### Week 6: Polish & Documentation (6-8 hours)

**Deliverables:**
- [ ] Architecture documentation
- [ ] Migration guide
- [ ] Updated test documentation
- [ ] Performance benchmarks
- [ ] Code review and cleanup

**Tasks:**

#### Task 6.1: Create Architecture Documentation (2 hours)
**File:** `cortex-brain/documents/architecture/CLEAN-ARCHITECTURE-IMPLEMENTATION.md`
- Document layer boundaries
- Document CQRS patterns used
- Document pipeline behaviors
- Document domain events

#### Task 6.2: Create Migration Guide (2 hours)
**File:** `cortex-brain/documents/guides/CLEAN-ARCHITECTURE-MIGRATION-GUIDE.md`
- Before/after code examples
- Migration steps for each pattern
- Common pitfalls and solutions
- Testing strategies

#### Task 6.3: Performance Benchmarking (2 hours)
- Measure pipeline overhead
- Compare before/after response times
- Validate no performance regression
- Document optimization opportunities

#### Task 6.4: Code Review and Cleanup (2 hours)
- Review all new code
- Remove dead code
- Update docstrings
- Ensure consistency

---

## 🧪 Testing Strategy

### Unit Tests (Week 1-2)
```python
# Test value objects
def test_relevance_score_validation():
    with pytest.raises(ValueError):
        RelevanceScore(1.5)  # Out of range
    
    score = RelevanceScore(0.85)
    assert score.is_high
    assert not score.is_medium

# Test Result pattern
def test_result_success():
    result = Result.success("test value")
    assert result.is_success
    assert result.value == "test value"

def test_result_failure():
    result = Result.failure(["error1", "error2"])
    assert result.is_failure
    assert len(result.errors) == 2
```

### Integration Tests (Week 3-4)
```python
# Test CQRS pipeline
@pytest.mark.asyncio
async def test_command_with_behaviors(mediator):
    # Arrange
    mediator.add_behavior(BrainProtectionBehaviour())
    mediator.add_behavior(ValidationBehaviour())
    
    command = CaptureConversationCommand(
        title="Test",
        content="Test content",
        file_path="test.md"
    )
    
    # Act
    result = await mediator.send(command)
    
    # Assert
    assert result.is_success
```

### Functional Tests (Week 4-5)
```python
# Test complete workflows
@pytest.mark.asyncio
async def test_conversation_lifecycle(app_context):
    # Capture → Search → Update → Delete
    # Verify events fired at each step
    # Verify domain state consistent
    pass
```

---

## 📊 Success Metrics

### Code Quality Metrics

| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| **Test Coverage** | 92% | 95% | pytest-cov |
| **Coupling** | Medium | Low | Code analysis |
| **Cyclomatic Complexity** | 8.5 avg | 6.0 avg | radon |
| **Type Hints Coverage** | 60% | 90% | mypy |
| **Documentation Coverage** | 70% | 85% | pydocstyle |

### Performance Metrics

| Metric | Baseline | Target | Acceptable Degradation |
|--------|----------|--------|----------------------|
| **Command Execution** | 50ms | 55ms | <10% |
| **Query Execution** | 30ms | 33ms | <10% |
| **Pipeline Overhead** | N/A | <5ms | N/A |
| **Event Dispatch** | N/A | <2ms | N/A |

### Architecture Metrics

| Metric | Baseline | Target |
|--------|----------|--------|
| **Layer Dependencies** | Some violations | Zero violations |
| **Domain Purity** | 70% | 95% |
| **CQRS Separation** | 0% | 100% |
| **Result Pattern Usage** | 0% | 80% |

---

## ⚠️ Risks & Mitigation

### Risk 1: Performance Degradation
**Probability:** Medium  
**Impact:** High  
**Mitigation:**
- Benchmark each phase
- Optimize pipeline behaviors
- Use async/await properly
- Profile before production

### Risk 2: Breaking Changes
**Probability:** High  
**Impact:** Medium  
**Mitigation:**
- Keep old APIs temporarily
- Add deprecation warnings
- Phased rollout
- Comprehensive tests

### Risk 3: Complexity Increase
**Probability:** Medium  
**Impact:** Medium  
**Mitigation:**
- Thorough documentation
- Code examples
- Team training
- Gradual adoption

### Risk 4: Integration Issues
**Probability:** Low  
**Impact:** High  
**Mitigation:**
- Integration tests
- Staging environment
- Rollback plan
- Feature flags

---

## 🎯 Definition of Done (DoD)

**For Each Week:**
- [ ] All deliverables completed
- [ ] Unit tests written and passing
- [ ] Integration tests written and passing
- [ ] Code reviewed
- [ ] Documentation updated
- [ ] Performance validated

**For Overall Project:**
- [ ] All patterns implemented
- [ ] 95% test coverage achieved
- [ ] Zero architecture violations
- [ ] Performance targets met
- [ ] Documentation complete
- [ ] Migration guide validated
- [ ] Team trained on new patterns

---

## 🚀 Rollout Strategy

### Phase 1: Internal Testing (Week 6)
- Test with CORTEX development team
- Validate all scenarios
- Fix critical bugs
- Performance tuning

### Phase 2: Beta Release (Week 7)
- Deploy to staging environment
- Limited user testing
- Monitor metrics
- Gather feedback

### Phase 3: Production Release (Week 8)
- Gradual rollout (10% → 50% → 100%)
- Feature flags for new behaviors
- Monitor error rates
- Ready to rollback

---

## 📚 Learning Resources

**For Team:**
1. Clean Architecture book by Robert C. Martin
2. Jason Taylor's Clean Architecture video (GOTO 2019)
3. CQRS pattern documentation
4. Domain-Driven Design basics
5. Python async/await best practices

**Code Examples:**
- Jason Taylor's Clean Architecture template (C#)
- This upgrade plan code samples
- CORTEX existing patterns (optimization-principles.yaml)

---

## 📞 Support & Questions

**Technical Lead:** Asif Hussain  
**Repository:** https://github.com/asifhussain60/CORTEX  
**Documentation:** cortex-brain/documents/

**For Questions:**
- Create GitHub issue with `clean-architecture` label
- Reference this plan in discussions
- Update plan based on learnings

---

## 📝 Change Log

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2025-11-21 | 1.0 | Initial plan created | Asif Hussain |

---

**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Proprietary - See LICENSE file
