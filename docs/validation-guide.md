# Validation Framework Guide

**CORTEX Clean Architecture - Phase 4**

This guide explains how to use the FluentValidation-style validator framework in CORTEX for validating commands and queries.

---

## Table of Contents

1. [Overview](#overview)
2. [Core Concepts](#core-concepts)
3. [Creating Validators](#creating-validators)
4. [Built-in Validators](#built-in-validators)
5. [Fluent API](#fluent-api)
6. [Conditional Validation](#conditional-validation)
7. [Custom Error Messages](#custom-error-messages)
8. [Integration with Pipeline](#integration-with-pipeline)
9. [Testing Validators](#testing-validators)
10. [Best Practices](#best-practices)

---

## Overview

The validation framework provides a fluent, type-safe way to validate commands and queries before they reach handlers. It integrates seamlessly with the CQRS/Mediator pipeline from Phase 3.

### Key Benefits

✅ **Fluent API** - Chainable validation rules that read like English  
✅ **Type-Safe** - Full generic type support with Python type hints  
✅ **Automatic Discovery** - Validators automatically found via registry  
✅ **Detailed Errors** - Property-specific error messages  
✅ **Reusable** - Common validators shared across commands/queries  
✅ **Testable** - Easy to unit test validators in isolation  

---

## Core Concepts

### Validator<T>

Base class for all validators. Generic type `T` is the command or query being validated.

```python
from src.application.validation import Validator

class MyCommandValidator(Validator[MyCommand]):
    def __init__(self):
        super().__init__()
        # Define validation rules here
```

### ValidationResult

Result of validation containing errors if validation failed.

```python
result = validator.validate(command)

if result.is_valid:
    # Proceed with command
    pass
else:
    # Handle errors
    for error in result.errors:
        print(f"{error.property_name}: {error.error_message}")
```

### ValidationError

Represents a single validation error for a property.

```python
@dataclass(frozen=True)
class ValidationError:
    property_name: str        # e.g., "title"
    error_message: str        # e.g., "Title is required"
    attempted_value: object   # The value that failed validation
    error_code: str          # Optional error code
```

---

## Creating Validators

### Basic Validator

```python
from src.application.validation import Validator
from src.application.commands import CaptureConversationCommand

class CaptureConversationValidator(Validator[CaptureConversationCommand]):
    """Validator for CaptureConversationCommand"""
    
    def __init__(self):
        super().__init__()
        
        # Required fields
        self.rule_for(lambda x: x.conversation_id).not_empty() \
            .with_message("Conversation ID is required")
        
        self.rule_for(lambda x: x.title).not_empty() \
            .with_message("Title is required") \
            .max_length(500) \
            .with_message("Title cannot exceed 500 characters")
        
        self.rule_for(lambda x: x.content).not_empty() \
            .min_length(10) \
            .with_message("Content must be at least 10 characters")
```

### Using the Validator

```python
# Create command
command = CaptureConversationCommand(
    conversation_id="conv-123",
    title="Test Conversation",
    content="Valid content here",
    file_path="/path/to/file.py"
)

# Validate
validator = CaptureConversationValidator()
result = validator.validate(command)

# Check result
if result.is_valid:
    print("✅ Validation passed!")
else:
    print("❌ Validation failed:")
    for error in result.errors:
        print(f"  - {error}")
```

---

## Built-in Validators

The framework includes 8 built-in validators for common scenarios:

### 1. NotEmptyValidator

Validates that a value is not None, empty string, or empty collection.

```python
self.rule_for(lambda x: x.name).not_empty()
```

### 2. MinLengthValidator

Validates minimum string length.

```python
self.rule_for(lambda x: x.content).min_length(10)
```

### 3. MaxLengthValidator

Validates maximum string length.

```python
self.rule_for(lambda x: x.title).max_length(500)
```

### 4. RegexValidator

Validates string matches a regular expression.

```python
self.rule_for(lambda x: x.namespace).matches(r'^[a-zA-Z0-9._-]+$')
```

### 5. EmailValidator

Validates email format.

```python
self.rule_for(lambda x: x.email).email()
```

### 6. UrlValidator

Validates URL format.

```python
self.rule_for(lambda x: x.website).url()
```

### 7. RangeValidator

Validates numeric value is within range.

```python
self.rule_for(lambda x: x.quality_score).range(0.0, 1.0)
```

### 8. PredicateValidator

Validates using a custom predicate function.

```python
self.rule_for(lambda x: x.captured_at) \
    .must(lambda dt: dt <= datetime.now()) \
    .with_message("Date cannot be in the future")
```

---

## Fluent API

Validation rules can be chained together for readability:

### Chaining Multiple Rules

```python
self.rule_for(lambda x: x.title) \
    .not_empty() \
    .min_length(3) \
    .max_length(500) \
    .with_message("Title must be 3-500 characters")
```

### Multiple Properties

```python
# Validate multiple properties
self.rule_for(lambda x: x.title).not_empty()
self.rule_for(lambda x: x.content).not_empty().min_length(10)
self.rule_for(lambda x: x.quality_score).range(0.0, 1.0)
```

---

## Conditional Validation

Use `.when()` to apply validation rules conditionally:

### Basic Conditional

```python
self.rule_for(lambda x: x.quality_score) \
    .range(0.0, 1.0) \
    .when(lambda x: x.quality_score is not None)
```

### Complex Conditional

```python
self.rule_for(lambda x: x.entity_count) \
    .must(lambda count: count >= 0) \
    .with_message("Entity count cannot be negative") \
    .when(lambda x: x.entity_count is not None and x.include_entities)
```

### Multiple Conditions

```python
self.rule_for(lambda x: x.tags) \
    .must(lambda tags: all(isinstance(t, str) and t.strip() for t in tags)) \
    .with_message("All tags must be non-empty strings") \
    .when(lambda x: x.tags is not None and len(x.tags) > 0)
```

---

## Custom Error Messages

Customize error messages to be more user-friendly:

### Per-Rule Messages

```python
self.rule_for(lambda x: x.title).not_empty() \
    .with_message("Please provide a conversation title")

self.rule_for(lambda x: x.content).min_length(10) \
    .with_message("Conversation content is too short (minimum 10 characters)")
```

### Message Interpolation

Use property names in messages:

```python
self.rule_for(lambda x: x.max_results) \
    .must(lambda n: 1 <= n <= 100) \
    .with_message("Maximum results must be between 1 and 100")
```

---

## Integration with Pipeline

Validators are automatically discovered and executed by `ValidationBehavior` in the pipeline.

### Registering Validators

Add validators to the registry:

```python
from src.application.validation import get_validator_registry

# Get global registry
registry = get_validator_registry()

# Register validator
registry.register('MyCommand', MyCommandValidator())
```

### Automatic Registration

Built-in validators are automatically registered on startup:

```python
# In validator_registry.py
def _register_default_validators(self):
    self.register('CaptureConversationCommand', CaptureConversationValidator())
    self.register('LearnPatternCommand', LearnPatternValidator())
    # ... more registrations
```

### Pipeline Execution

When a command is sent through the mediator:

```python
# 1. Command enters pipeline
command = CaptureConversationCommand(...)

# 2. ValidationBehavior runs
result = await mediator.send(command)

# 3. If validation fails, Result.failure returned
# 4. If validation passes, command reaches handler
```

---

## Testing Validators

### Unit Testing

Test validators in isolation:

```python
import pytest
from datetime import datetime

class TestCaptureConversationValidator:
    
    def test_valid_command_passes(self):
        """Valid command should pass validation"""
        command = CaptureConversationCommand(
            conversation_id="conv-123",
            title="Test",
            content="Valid content here",
            file_path="/path"
        )
        
        validator = CaptureConversationValidator()
        result = validator.validate(command)
        
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_missing_title_fails(self):
        """Missing title should fail validation"""
        command = CaptureConversationCommand(
            conversation_id="conv-123",
            title="",  # Invalid!
            content="Valid content",
            file_path="/path"
        )
        
        validator = CaptureConversationValidator()
        result = validator.validate(command)
        
        assert not result.is_valid
        assert any("Title is required" in error.error_message 
                   for error in result.errors)
```

### Integration Testing

Test validators in pipeline context:

```python
@pytest.mark.asyncio
async def test_validation_blocks_invalid_command(self):
    """Invalid command should not reach handler"""
    command = CaptureConversationCommand(
        conversation_id="",  # Invalid!
        title="Test",
        content="Valid content",
        file_path="/path"
    )
    
    handler_called = False
    async def mock_handler(request):
        nonlocal handler_called
        handler_called = True
        return Result.success("OK")
    
    behavior = ValidationBehavior()
    result = await behavior.handle(command, mock_handler)
    
    assert not result.is_success
    assert not handler_called  # Handler was not reached
```

---

## Best Practices

### 1. One Validator Per Command/Query

Create a dedicated validator for each command or query:

```python
# ✅ Good - Dedicated validator
class CaptureConversationValidator(Validator[CaptureConversationCommand]):
    pass

# ❌ Bad - Reusing validator for multiple commands
class GenericValidator(Validator):
    pass
```

### 2. Validate Required Fields First

Check required fields before optional constraints:

```python
# ✅ Good - Required first, then constraints
self.rule_for(lambda x: x.title).not_empty()
self.rule_for(lambda x: x.title).max_length(500)

# ❌ Bad - Constraints before required check
self.rule_for(lambda x: x.title).max_length(500)
self.rule_for(lambda x: x.title).not_empty()
```

### 3. Use Specific Error Messages

Provide clear, actionable error messages:

```python
# ✅ Good - Specific and actionable
.with_message("Title must be 3-500 characters")

# ❌ Bad - Generic error
.with_message("Invalid title")
```

### 4. Use Conditional Validation for Optional Fields

Don't validate optional fields if they're None:

```python
# ✅ Good - Validate only if present
self.rule_for(lambda x: x.quality_score) \
    .range(0.0, 1.0) \
    .when(lambda x: x.quality_score is not None)

# ❌ Bad - Fails if None
self.rule_for(lambda x: x.quality_score).range(0.0, 1.0)
```

### 5. Group Related Rules

Keep related validation rules together:

```python
# ✅ Good - Grouped by property
# Title validation
self.rule_for(lambda x: x.title).not_empty()
self.rule_for(lambda x: x.title).max_length(500)

# Content validation
self.rule_for(lambda x: x.content).not_empty()
self.rule_for(lambda x: x.content).min_length(10)
```

### 6. Test Both Valid and Invalid Cases

Write tests for all validation scenarios:

```python
def test_valid_command_passes():
    """Test valid command passes"""
    pass

def test_missing_required_field_fails():
    """Test missing required field fails"""
    pass

def test_field_too_long_fails():
    """Test field exceeding max length fails"""
    pass
```

### 7. Use Type Hints

Always use proper type hints:

```python
# ✅ Good - Type hints present
class MyValidator(Validator[MyCommand]):
    def __init__(self):
        super().__init__()

# ❌ Bad - No type hints
class MyValidator(Validator):
    pass
```

---

## Example: Complete Validator

Here's a complete, production-ready validator:

```python
"""Validator for LearnPatternCommand"""
from datetime import datetime
from src.application.validation import Validator
from src.application.commands import LearnPatternCommand


class LearnPatternValidator(Validator[LearnPatternCommand]):
    """Validates pattern learning commands
    
    Ensures:
    - All required fields are present
    - Pattern type is valid
    - Namespace follows naming conventions
    - Confidence score is in valid range
    - Optional fields meet constraints when provided
    """
    
    VALID_PATTERN_TYPES = [
        'code_structure',
        'architecture',
        'best_practice',
        'anti_pattern',
        'optimization',
        'bug_fix',
        'design_pattern',
        'decision_pattern'
    ]
    
    def __init__(self):
        super().__init__()
        
        # Required: Pattern ID
        self.rule_for(lambda x: x.pattern_id).not_empty() \
            .with_message("Pattern ID is required")
        
        # Required: Pattern name with length constraints
        self.rule_for(lambda x: x.pattern_name).not_empty() \
            .with_message("Pattern name is required") \
            .max_length(200) \
            .with_message("Pattern name cannot exceed 200 characters")
        
        # Required: Pattern type from valid set
        self.rule_for(lambda x: x.pattern_type).not_empty() \
            .with_message("Pattern type is required") \
            .must(lambda pt: pt in self.VALID_PATTERN_TYPES) \
            .with_message(
                f"Pattern type must be one of: {', '.join(self.VALID_PATTERN_TYPES)}"
            )
        
        # Required: Pattern content
        self.rule_for(lambda x: x.pattern_content).not_empty() \
            .with_message("Pattern content is required")
        
        # Required: Source conversation ID
        self.rule_for(lambda x: x.source_conversation_id).not_empty() \
            .with_message("Source conversation ID is required")
        
        # Required: Namespace with format validation
        self.rule_for(lambda x: x.namespace).not_empty() \
            .with_message("Namespace is required") \
            .matches(r'^[a-zA-Z0-9._-]+$') \
            .with_message(
                "Namespace must contain only letters, numbers, dots, hyphens, and underscores"
            )
        
        # Required: Confidence score in range
        self.rule_for(lambda x: x.confidence_score) \
            .must(lambda score: 0.0 <= score <= 1.0) \
            .with_message("Confidence score must be between 0.0 and 1.0")
        
        # Optional: Tags validation when provided
        self.rule_for(lambda x: x.tags) \
            .must(lambda tags: all(isinstance(t, str) and t.strip() for t in tags)) \
            .with_message("All tags must be non-empty strings") \
            .when(lambda x: x.tags is not None)
        
        # Optional: Learned date validation when provided
        self.rule_for(lambda x: x.learned_at) \
            .must(lambda dt: dt <= datetime.now()) \
            .with_message("Learned date cannot be in the future") \
            .when(lambda x: x.learned_at is not None)
```

---

## Summary

The validation framework provides a powerful, fluent way to validate commands and queries in CORTEX:

- **Fluent API** for readable validation rules
- **8 built-in validators** for common scenarios
- **Automatic pipeline integration** via registry
- **Type-safe** with full generic support
- **Testable** with clear separation of concerns

For more information, see:
- [Specification Pattern Guide](specification-guide.md)
- [Clean Architecture Overview](../README.md)
- API Reference (coming soon)

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Proprietary
