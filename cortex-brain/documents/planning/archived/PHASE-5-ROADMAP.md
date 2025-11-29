# Phase 5: Repository Pattern & Unit of Work

**Status:** 📋 PLANNING  
**Date:** 2025-11-23  
**Prerequisites:** Phase 3 (TDD Mastery) ✅ | Phase 4 (Clean Architecture) ✅  
**Estimated Duration:** 3-4 weeks

---

## Executive Summary

Phase 5 completes the **Data Access Layer** of CORTEX Clean Architecture by implementing the Repository Pattern and Unit of Work pattern. This phase builds on Phase 4's validation/specification patterns to provide a clean abstraction over data persistence.

**Architecture Evolution:**
```
Phase 3: TDD Mastery → Test generation, workflows, optimization
Phase 4: Clean Architecture → Validation, specifications, pipeline behaviors
Phase 5: Data Access → Repository, Unit of Work, data abstraction
Phase 6: Infrastructure → External services, API clients, messaging
```

---

## Current State Analysis

### ✅ What We Have (Phases 3-4)

**Phase 3 - TDD Mastery:**
- 5,596 lines of production code
- 120 comprehensive tests (98.1% pass rate)
- TDD workflow orchestration with caching
- Performance optimization (2-5x speedup)

**Phase 4 - Clean Architecture:**
- Validator Framework (56 tests)
- Specification Pattern (54 tests)
- Pipeline Integration (24 tests)
- 134/134 tests passing (100%)

**Current Data Access:**
- Direct SQLite database access
- Conversation repository exists but inconsistent
- No transaction management
- No change tracking
- Hard-coded SQL queries

### ❌ What We Need (Phase 5)

**Repository Pattern:**
- Abstract data access behind interfaces
- Hide database implementation details
- Provide collection-like API for entities
- Support specifications for querying

**Unit of Work:**
- Transaction management
- Change tracking across repositories
- Atomic commit/rollback operations
- Coordinated saves across aggregates

**Benefits:**
- Testable data access (mock repositories)
- Database-agnostic domain layer
- Transaction boundaries explicit
- Consistent query patterns

---

## Phase 5 Milestones

### M5.1: Repository Interfaces & Base Implementation (1 week)

**Goal:** Define repository contracts and create generic base implementation

**Deliverables:**
1. **IRepository<T> Interface** (~50 lines)
   - `get_by_id(id) -> Optional[T]`
   - `get_all() -> List[T]`
   - `find(spec: ISpecification[T]) -> List[T]`
   - `add(entity: T) -> None`
   - `update(entity: T) -> None`
   - `delete(entity: T) -> None`

2. **Repository Base Class** (~150 lines)
   - Generic implementation for common operations
   - Specification-based querying (uses Phase 4 specs)
   - Change tracking integration
   - Transaction participation

3. **IUnitOfWork Interface** (~40 lines)
   - `begin_transaction() -> None`
   - `commit() -> Result[None]`
   - `rollback() -> None`
   - `register_new(entity: T) -> None`
   - `register_dirty(entity: T) -> None`
   - `register_deleted(entity: T) -> None`

4. **Tests** (~200 lines, 15 tests)
   - Repository CRUD operations
   - Specification integration
   - Change tracking
   - Transaction boundaries

**Success Criteria:**
- All repository operations testable with mocks
- Specifications work with repositories
- Change tracking accurate

---

### M5.2: Concrete Repositories (1 week)

**Goal:** Implement repositories for CORTEX domain entities

**Deliverables:**
1. **ConversationRepository** (~200 lines)
   - Find by namespace
   - Find high-quality conversations (spec)
   - Find recent conversations (spec)
   - Tag-based search
   - Entity extraction

2. **PatternRepository** (~180 lines)
   - Find by category
   - Find by confidence threshold
   - Find similar patterns
   - Update confidence scores
   - Pattern linking

3. **SessionRepository** (~150 lines)
   - Find active sessions
   - Find by feature name
   - Session history
   - Metrics aggregation

4. **BrainHealthRepository** (~120 lines)
   - Health metrics
   - Validation results
   - Historical trends
   - Anomaly detection

5. **Tests** (~400 lines, 30 tests)
   - Each repository CRUD operations
   - Specification queries
   - Complex queries
   - Edge cases

**Success Criteria:**
- All existing data access migrated to repositories
- Specifications reusable across queries
- No direct SQL in domain/application layers

---

### M5.3: Unit of Work Implementation (1 week)

**Goal:** Coordinate transactions and change tracking across repositories

**Deliverables:**
1. **SQLiteUnitOfWork** (~250 lines)
   - Transaction management
   - Change tracking (new/dirty/deleted)
   - Coordinated saves across repositories
   - Rollback on error
   - Connection pooling

2. **Repository Factory** (~100 lines)
   - Create repositories with shared UoW
   - Inject UoW into repositories
   - Lifecycle management

3. **Integration with CQRS Handlers** (~150 lines)
   - UoW per command handler
   - Automatic transaction boundaries
   - Commit on success, rollback on failure

4. **Tests** (~350 lines, 25 tests)
   - Multi-repository transactions
   - Rollback scenarios
   - Concurrent operations
   - Connection lifecycle

**Success Criteria:**
- Transactions span multiple repositories
- Rollback works correctly
- No database locks or deadlocks
- Performance acceptable (<50ms overhead)

---

### M5.4: Migration & Documentation (3-4 days)

**Goal:** Migrate existing code to use repositories and document patterns

**Deliverables:**
1. **Code Migration** (~500 lines refactored)
   - Update command/query handlers
   - Remove direct database access
   - Use UoW in pipelines
   - Inject repositories

2. **Integration Tests** (~300 lines, 20 tests)
   - End-to-end scenarios with repositories
   - Transaction boundaries validated
   - Specifications in real queries
   - Performance benchmarks

3. **Documentation** (~2,000 lines)
   - Repository pattern guide
   - Unit of Work guide
   - Migration examples
   - Best practices

4. **Performance Validation**
   - Benchmark repository operations
   - Compare with direct SQL
   - Optimize hot paths
   - Target: <10% overhead vs direct SQL

**Success Criteria:**
- All handlers use repositories
- Zero direct database access in domain/application
- Tests green (target: >95% pass rate)
- Documentation complete

---

## Architecture Design

### Repository Pattern Structure

```
src/
├── domain/
│   ├── repositories/                    # Repository interfaces
│   │   ├── __init__.py
│   │   ├── i_repository.py              # Generic IRepository<T>
│   │   ├── i_unit_of_work.py            # IUnitOfWork interface
│   │   ├── i_conversation_repository.py # Domain-specific interface
│   │   ├── i_pattern_repository.py
│   │   ├── i_session_repository.py
│   │   └── i_brain_health_repository.py
│   └── entities/                        # Domain entities (existing)
│       ├── conversation.py
│       ├── pattern.py
│       └── session.py
│
├── infrastructure/
│   ├── persistence/                     # Concrete implementations
│   │   ├── __init__.py
│   │   ├── repository_base.py           # Generic base implementation
│   │   ├── unit_of_work.py              # SQLiteUnitOfWork
│   │   ├── conversation_repository.py   # Concrete repository
│   │   ├── pattern_repository.py
│   │   ├── session_repository.py
│   │   └── brain_health_repository.py
│   └── database/                        # Database utilities (existing)
│       └── sqlite_connection.py
│
└── application/
    └── behaviors/
        └── transaction_behavior.py      # UoW pipeline behavior
```

### Unit of Work Flow

```
Command → ValidationBehavior (Phase 4)
       ↓
       TransactionBehavior (Phase 5)
       ↓
       begin_transaction()
       ↓
       CommandHandler
       ├── repository.add(entity)
       ├── repository.update(entity)
       └── repository.delete(entity)
       ↓
       commit() [on success]
       rollback() [on error]
       ↓
       Result<T>
```

---

## Technical Design

### IRepository<T> Interface

```python
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Optional
from domain.specifications import ISpecification

T = TypeVar('T')

class IRepository(ABC, Generic[T]):
    """Generic repository interface for entity persistence."""
    
    @abstractmethod
    def get_by_id(self, entity_id: int) -> Optional[T]:
        """Get entity by ID."""
        pass
    
    @abstractmethod
    def get_all(self) -> List[T]:
        """Get all entities."""
        pass
    
    @abstractmethod
    def find(self, spec: ISpecification[T]) -> List[T]:
        """Find entities matching specification."""
        pass
    
    @abstractmethod
    def add(self, entity: T) -> None:
        """Add new entity."""
        pass
    
    @abstractmethod
    def update(self, entity: T) -> None:
        """Update existing entity."""
        pass
    
    @abstractmethod
    def delete(self, entity: T) -> None:
        """Delete entity."""
        pass
    
    @abstractmethod
    def count(self, spec: Optional[ISpecification[T]] = None) -> int:
        """Count entities matching specification."""
        pass
```

### IUnitOfWork Interface

```python
from abc import ABC, abstractmethod
from typing import TypeVar
from application.common.result import Result

T = TypeVar('T')

class IUnitOfWork(ABC):
    """Unit of Work pattern for transaction management."""
    
    @abstractmethod
    def begin_transaction(self) -> None:
        """Start transaction."""
        pass
    
    @abstractmethod
    def commit(self) -> Result[None]:
        """Commit all changes."""
        pass
    
    @abstractmethod
    def rollback(self) -> None:
        """Rollback all changes."""
        pass
    
    @abstractmethod
    def register_new(self, entity: T) -> None:
        """Track new entity for insertion."""
        pass
    
    @abstractmethod
    def register_dirty(self, entity: T) -> None:
        """Track modified entity for update."""
        pass
    
    @abstractmethod
    def register_deleted(self, entity: T) -> None:
        """Track entity for deletion."""
        pass
    
    @property
    @abstractmethod
    def conversations(self) -> 'IConversationRepository':
        """Get conversation repository."""
        pass
    
    @property
    @abstractmethod
    def patterns(self) -> 'IPatternRepository':
        """Get pattern repository."""
        pass
    
    @property
    @abstractmethod
    def sessions(self) -> 'ISessionRepository':
        """Get session repository."""
        pass
```

### Usage Example

```python
# In command handler
class CaptureConversationHandler:
    def __init__(self, uow: IUnitOfWork):
        self._uow = uow
    
    async def handle(self, command: CaptureConversationCommand) -> Result[int]:
        # Specification for duplicate check (Phase 4)
        duplicate_spec = TitleMatchSpec(command.title) & \
                        ContentSimilaritySpec(command.content, threshold=0.95)
        
        # Check for duplicates using specification
        duplicates = self._uow.conversations.find(duplicate_spec)
        if duplicates:
            return Result.failure("Duplicate conversation detected")
        
        # Create entity
        conversation = Conversation(
            title=command.title,
            content=command.content,
            namespace=command.namespace
        )
        
        # Add to repository (tracked by UoW)
        self._uow.conversations.add(conversation)
        
        # Commit handled by TransactionBehavior
        return Result.success(conversation.id)
```

---

## Integration with Existing Phases

### Phase 4 Specifications → Phase 5 Repositories

**Specifications (Phase 4)** define business rules for filtering:
```python
high_quality = HighQualityConversationSpec(min_quality=0.85)
recent = RecentConversationSpec(days=30)
rich = EntityCountSpec(min_entities=10)

learning_candidates = high_quality & recent & rich
```

**Repositories (Phase 5)** use specifications for queries:
```python
candidates = await uow.conversations.find(learning_candidates)
```

### CQRS Handlers → Repositories

**Before Phase 5:**
```python
# Direct database access
cursor.execute("SELECT * FROM conversations WHERE quality_score >= 0.85")
conversations = cursor.fetchall()
```

**After Phase 5:**
```python
# Repository with specification
spec = HighQualityConversationSpec(0.85)
conversations = await uow.conversations.find(spec)
```

---

## Performance Targets

| Operation | Target | Notes |
|-----------|--------|-------|
| Repository CRUD | <10ms overhead | vs direct SQL |
| Specification query | <50ms | Simple spec |
| Complex specification | <200ms | Composite spec with 3+ conditions |
| Transaction commit | <100ms | 5 entities across 2 repositories |
| Change tracking | <5ms | Per entity |

---

## Testing Strategy

### Unit Tests (~60 tests)
- Repository interfaces
- Base repository implementation
- Unit of Work transaction logic
- Change tracking
- Specification integration

### Integration Tests (~25 tests)
- End-to-end with real database
- Multi-repository transactions
- Rollback scenarios
- Concurrent access
- Performance benchmarks

### Test Data Builders
```python
class ConversationBuilder:
    def with_high_quality(self, score=0.90):
        self._quality_score = score
        return self
    
    def recent(self, days_ago=7):
        self._captured_at = datetime.now() - timedelta(days=days_ago)
        return self
    
    def build(self) -> Conversation:
        return Conversation(...)
```

---

## Migration Plan

### Phase 1: Create Interfaces (Day 1-2)
- Define repository interfaces
- Define Unit of Work interface
- Create base implementations
- Write unit tests

### Phase 2: Concrete Repositories (Day 3-7)
- Implement ConversationRepository
- Implement PatternRepository
- Implement SessionRepository
- Implement BrainHealthRepository
- Write integration tests

### Phase 3: Unit of Work (Day 8-12)
- Implement SQLiteUnitOfWork
- Integrate with repositories
- Add transaction behavior to pipeline
- Write transaction tests

### Phase 4: Migration (Day 13-15)
- Refactor command handlers
- Refactor query handlers
- Remove direct SQL access
- Update tests

### Phase 5: Validation & Documentation (Day 16-20)
- Performance benchmarks
- Integration test suite
- Documentation
- Code review
- Production readiness checklist

---

## Success Metrics

### Code Quality
- ✅ Zero direct SQL in domain/application layers
- ✅ All handlers use repositories
- ✅ Specifications used for all queries
- ✅ Transaction boundaries explicit

### Test Coverage
- ✅ >95% test pass rate
- ✅ 60+ unit tests
- ✅ 25+ integration tests
- ✅ Performance benchmarks green

### Performance
- ✅ <10% overhead vs direct SQL
- ✅ <100ms transaction commit
- ✅ No database locks or deadlocks
- ✅ Connection pooling working

### Documentation
- ✅ Repository pattern guide complete
- ✅ Unit of Work guide complete
- ✅ Migration examples provided
- ✅ Best practices documented

---

## Risks & Mitigations

### Risk 1: Performance Overhead
**Mitigation:** Benchmark early, optimize hot paths, use connection pooling

### Risk 2: Complex Migration
**Mitigation:** Incremental migration, feature flags, parallel implementation

### Risk 3: Transaction Deadlocks
**Mitigation:** Explicit transaction boundaries, timeout policies, retry logic

### Risk 4: Specification Complexity
**Mitigation:** Expression tree optimization, query plan caching, SQL generation hints

---

## Dependencies

### External
- sqlite3 (built-in)
- pytest for testing
- pytest-asyncio for async tests

### Internal
- Phase 4 Specification Pattern
- Phase 4 Validation Framework
- Phase 3 CQRS/Mediator
- Domain entities (Conversation, Pattern, Session)

---

## Deliverables Summary

**Code:**
- ~1,200 lines of production code
- ~850 lines of test code
- 85+ comprehensive tests

**Documentation:**
- Repository pattern guide (~800 lines)
- Unit of Work guide (~600 lines)
- Migration examples (~600 lines)

**Total Estimated Time:** 3-4 weeks

---

## Next Steps

**Immediate Actions:**
1. Review and approve Phase 5 roadmap
2. Create milestone branches
3. Set up project tracking
4. Begin M5.1 implementation

**Approval Checklist:**
- [ ] Architecture design reviewed
- [ ] Success metrics agreed
- [ ] Timeline approved
- [ ] Resources allocated
- [ ] Dependencies validated

**Ready to begin Phase 5 implementation?**

---

**Author:** Asif Hussain  
**Date:** 2025-11-23  
**Status:** 📋 PLANNING → Awaiting Approval  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Proprietary
