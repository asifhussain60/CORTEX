# Phase 4 Quick Reference

**Validation & Specification Patterns - Quick Reference Card**

---

## 🎯 Validation Framework

### Creating a Validator

```python
from src.application.validation import Validator

class MyCommandValidator(Validator[MyCommand]):
    def __init__(self):
        super().__init__()
        
        # Required field
        self.rule_for(lambda x: x.title).not_empty()
        
        # Length constraints
        self.rule_for(lambda x: x.content).min_length(10).max_length(1000)
        
        # Range validation
        self.rule_for(lambda x: x.score).range(0.0, 1.0)
        
        # Regex pattern
        self.rule_for(lambda x: x.namespace).matches(r'^[a-zA-Z0-9._-]+$')
        
        # Custom predicate
        self.rule_for(lambda x: x.date).must(lambda d: d <= datetime.now())
        
        # Conditional validation
        self.rule_for(lambda x: x.optional_field) \
            .not_empty() \
            .when(lambda x: x.optional_field is not None)
```

### Built-in Validators

| Validator | Method | Example |
|-----------|--------|---------|
| NotEmpty | `.not_empty()` | Required fields |
| MinLength | `.min_length(10)` | Minimum string length |
| MaxLength | `.max_length(500)` | Maximum string length |
| Regex | `.matches(pattern)` | Pattern matching |
| Email | `.email()` | Email format |
| URL | `.url()` | URL format |
| Range | `.range(min, max)` | Numeric range |
| Predicate | `.must(lambda x: ...)` | Custom logic |

### Registering Validators

```python
from src.application.validation import get_validator_registry

registry = get_validator_registry()
registry.register('MyCommand', MyCommandValidator())
```

### Using in Tests

```python
def test_valid_command_passes():
    command = MyCommand(title="Valid", content="Good content")
    validator = MyCommandValidator()
    result = validator.validate(command)
    
    assert result.is_valid
    assert len(result.errors) == 0

def test_invalid_command_fails():
    command = MyCommand(title="", content="")
    validator = MyCommandValidator()
    result = validator.validate(command)
    
    assert not result.is_valid
    assert len(result.errors) > 0
    assert any("Title" in error.error_message for error in result.errors)
```

---

## 🔍 Specification Pattern

### Creating a Specification

```python
from src.domain.specifications import ISpecification

class HighQualitySpec(ISpecification):
    def __init__(self, min_quality: float = 0.70):
        self._min_quality = min_quality
    
    def is_satisfied_by(self, entity) -> bool:
        return entity.quality_score >= self._min_quality
    
    def __str__(self) -> str:
        return f"HighQuality(>={self._min_quality})"
```

### Built-in Specifications

| Specification | Purpose | Example |
|---------------|---------|---------|
| `HighQualityConversationSpec` | Quality threshold | `HighQualityConversationSpec(0.85)` |
| `RecentConversationSpec` | Time-based filter | `RecentConversationSpec(days=7)` |
| `NamespaceMatchSpec` | Namespace matching | `NamespaceMatchSpec("workspace.auth")` |
| `PatternConfidenceSpec` | Confidence threshold | `PatternConfidenceSpec(0.75)` |
| `MinimumParticipantsSpec` | Participant count | `MinimumParticipantsSpec(2)` |
| `EntityCountSpec` | Entity count | `EntityCountSpec(min_entities=5)` |
| `ContextRelevanceSpec` | Relevance threshold | `ContextRelevanceSpec(0.80)` |
| `TierSpec` | Memory tier | `TierSpec(tier=1)` |

### Composing Specifications

```python
# AND composition (both must be satisfied)
spec = high_quality & recent
spec = HighQualityConversationSpec() & RecentConversationSpec()

# OR composition (either must be satisfied)
spec = high_quality | multi_participant
spec = HighQualityConversationSpec() | MinimumParticipantsSpec(3)

# NOT composition (negate specification)
spec = ~high_quality
spec = ~HighQualityConversationSpec()

# Complex composition
spec = (
    (HighQualityConversationSpec(0.85) & RecentConversationSpec(7)) |
    (MinimumParticipantsSpec(3) & EntityCountSpec(10))
)
```

### Expression Specifications

```python
from src.domain.specifications import ExpressionSpecification

# Simple lambda
is_active = ExpressionSpecification(lambda x: x.is_active)

# Complex expression
is_valuable = ExpressionSpecification(
    lambda x: x.quality > 0.8 and x.entities >= 10,
    description="Valuable conversation"
)

# Use with composition
spec = is_active & HighQualityConversationSpec()
```

### Using in Query Handlers

```python
class SearchHandler:
    async def handle(self, query: SearchQuery) -> Result[List[Dto]]:
        # Build specification
        spec = (
            HighQualityConversationSpec(query.min_quality) &
            RecentConversationSpec(days=30)
        )
        
        # Get all entities
        entities = await self._repository.get_all()
        
        # Filter with specification
        filtered = [e for e in entities if spec.is_satisfied_by(e)]
        
        return Result.success([self._to_dto(e) for e in filtered])
```

### Testing Specifications

```python
def test_high_quality_satisfied():
    spec = HighQualityConversationSpec(min_quality=0.70)
    conversation = create_conversation(quality_score=0.85)
    
    assert spec.is_satisfied_by(conversation)

def test_composition():
    spec = HighQualityConversationSpec() & RecentConversationSpec(days=7)
    
    good_recent = create_conversation(quality=0.85, days_old=3)
    good_old = create_conversation(quality=0.85, days_old=30)
    
    assert spec.is_satisfied_by(good_recent)
    assert not spec.is_satisfied_by(good_old)
```

---

## 🔄 Pipeline Integration

### Automatic Validation

Validators are automatically executed by `ValidationBehavior` in the pipeline:

```python
# Send command through mediator
result = await mediator.send(command)

# Pipeline flow:
# 1. ValidationBehavior finds validator in registry
# 2. Validator executes all rules
# 3. If validation fails, Result.failure returned
# 4. If validation passes, command reaches handler
```

### Validator Registry

All validators are pre-registered on startup:

```python
# Registered validators:
- CaptureConversationCommand
- LearnPatternCommand
- UpdateContextRelevanceCommand
- UpdatePatternConfidenceCommand
- SearchContextQuery
- GetConversationQualityQuery
- FindSimilarPatternsQuery
```

---

## 📁 File Locations

### Validation Framework
```
src/application/validation/
├── validator.py                    # Base Validator<T> class
├── validation_result.py            # ValidationResult/Error
├── common_validators.py            # 8 built-in validators
├── conversation_validators.py      # Command validators
├── conversation_query_validators.py # Query validators
└── validator_registry.py           # Validator registry
```

### Specification Pattern
```
src/domain/specifications/
├── specification.py                # ISpecification<T> interface
├── composite_specification.py      # And/Or/Not composition
├── expression_specification.py     # Lambda-based specs
└── common_specifications.py        # 8 domain specifications
```

### Tests
```
tests/unit/application/validation/  # 56 validator tests
tests/unit/domain/specifications/   # 54 specification tests
tests/integration/application/      # 24 integration tests
```

---

## 📚 Documentation

- **Full Guide:** `docs/validation-guide.md`
- **Specification Guide:** `docs/specification-guide.md`
- **Phase Summary:** `docs/PHASE-4-COMPLETE.md`

---

## ⚡ Common Patterns

### Pattern 1: Command with Validation

```python
# 1. Create command
@dataclass
class MyCommand(ICommand):
    title: str
    content: str

# 2. Create validator
class MyCommandValidator(Validator[MyCommand]):
    def __init__(self):
        super().__init__()
        self.rule_for(lambda x: x.title).not_empty()
        self.rule_for(lambda x: x.content).min_length(10)

# 3. Register validator
registry.register('MyCommand', MyCommandValidator())

# 4. Use in pipeline (automatic!)
result = await mediator.send(command)
```

### Pattern 2: Query with Specifications

```python
# 1. Define specifications
high_quality = HighQualityConversationSpec(0.85)
recent = RecentConversationSpec(days=30)

# 2. Compose specifications
filter_spec = high_quality & recent

# 3. Use in query handler
entities = await repository.get_all()
filtered = [e for e in entities if filter_spec.is_satisfied_by(e)]
```

### Pattern 3: Custom Business Rule

```python
# 1. Create specification
class CustomRuleSpec(ISpecification):
    def is_satisfied_by(self, entity) -> bool:
        return (
            entity.property1 > threshold and
            entity.property2.startswith('prefix') and
            len(entity.collection) >= min_count
        )

# 2. Use in queries
custom_filter = CustomRuleSpec()
results = [e for e in entities if custom_filter.is_satisfied_by(e)]

# 3. Compose with others
complex = custom_filter & HighQualityConversationSpec()
```

---

## 🎯 Best Practices

### Validation
1. ✅ One validator per command/query
2. ✅ Validate required fields first
3. ✅ Use specific error messages
4. ✅ Use `.when()` for optional fields
5. ✅ Test both valid and invalid cases

### Specifications
1. ✅ Name by business rules, not implementation
2. ✅ Keep specifications small and focused
3. ✅ Compose rather than extend
4. ✅ Make specifications immutable
5. ✅ Provide meaningful `__str__()` representations

---

## 📊 Test Coverage

```
Phase 4A: 56/56 tests (Validators)
Phase 4B: 54/54 tests (Specifications)  
Phase 4C: 24/24 tests (Integration)
─────────────────────────────────────
Total:    134/134 tests passing ✅
```

---

**Phase 4 Complete!** 🎉

For detailed information, see the full guides in `docs/`.
