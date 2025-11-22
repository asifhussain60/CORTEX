# Specification Pattern Guide

**CORTEX Clean Architecture - Phase 4**

This guide explains how to use the Specification Pattern in CORTEX for composable business rules and complex domain queries.

---

## Table of Contents

1. [Overview](#overview)
2. [Core Concepts](#core-concepts)
3. [Creating Specifications](#creating-specifications)
4. [Built-in Specifications](#built-in-specifications)
5. [Composing Specifications](#composing-specifications)
6. [Expression Specifications](#expression-specifications)
7. [Using in Query Handlers](#using-in-query-handlers)
8. [Testing Specifications](#testing-specifications)
9. [Best Practices](#best-practices)

---

## Overview

The Specification Pattern encapsulates business rules in reusable, composable objects. It's perfect for complex filtering, validation, and business logic that needs to be reused across different contexts.

### Key Benefits

✅ **Composable** - Combine specifications with AND, OR, NOT  
✅ **Reusable** - Share business rules across queries and commands  
✅ **Testable** - Test business logic in isolation  
✅ **Readable** - Express complex rules in clear, domain language  
✅ **Type-Safe** - Full generic type support  
✅ **Operator Overloading** - Use `&`, `|`, `~` for natural composition  

---

## Core Concepts

### ISpecification<T>

Base interface for all specifications. Generic type `T` is the entity being evaluated.

```python
from src.domain.specifications import ISpecification

class MySpecification(ISpecification[MyEntity]):
    def is_satisfied_by(self, entity: MyEntity) -> bool:
        # Business rule logic here
        return entity.property == expected_value
```

### Three Ways to Create Specifications

1. **Class-based** - Reusable specifications with state
2. **Expression-based** - Lambda functions for simple rules
3. **Composite** - Combine existing specifications with AND/OR/NOT

---

## Creating Specifications

### Class-Based Specification

Best for complex, reusable business rules:

```python
from src.domain.specifications import ISpecification

class HighQualityConversationSpec(ISpecification):
    """Specification for high-quality conversations"""
    
    def __init__(self, min_quality: float = 0.70):
        self._min_quality = min_quality
    
    def is_satisfied_by(self, conversation) -> bool:
        """Check if conversation meets quality threshold"""
        return conversation.quality_score >= self._min_quality
    
    def __str__(self) -> str:
        return f"HighQualityConversation(>={self._min_quality})"
```

### Using the Specification

```python
# Create specification
spec = HighQualityConversationSpec(min_quality=0.80)

# Test against entity
conversation = get_conversation("conv-123")
if spec.is_satisfied_by(conversation):
    print("✅ High quality conversation")
else:
    print("❌ Does not meet quality threshold")

# Filter collection
high_quality_convos = [c for c in conversations 
                       if spec.is_satisfied_by(c)]
```

---

## Built-in Specifications

CORTEX includes 8 domain-specific specifications:

### 1. HighQualityConversationSpec

Filters conversations by quality score threshold.

```python
from src.domain.specifications import HighQualityConversationSpec

# Default threshold: 0.70
spec = HighQualityConversationSpec()

# Custom threshold
spec = HighQualityConversationSpec(min_quality=0.85)

# Use it
if spec.is_satisfied_by(conversation):
    print("High quality conversation!")
```

### 2. RecentConversationSpec

Filters conversations by recency (last N days).

```python
from src.domain.specifications import RecentConversationSpec

# Last 7 days (default)
spec = RecentConversationSpec()

# Custom timeframe
spec = RecentConversationSpec(days=30)

if spec.is_satisfied_by(conversation):
    print("Recent conversation")
```

### 3. NamespaceMatchSpec

Filters by namespace (case-insensitive).

```python
from src.domain.specifications import NamespaceMatchSpec

spec = NamespaceMatchSpec("workspace.backend")

if spec.is_satisfied_by(pattern):
    print("Pattern matches namespace")
```

### 4. PatternConfidenceSpec

Filters patterns by confidence score threshold.

```python
from src.domain.specifications import PatternConfidenceSpec

# High confidence patterns (>= 0.75)
spec = PatternConfidenceSpec(min_confidence=0.75)

if spec.is_satisfied_by(pattern):
    print("High confidence pattern")
```

### 5. MinimumParticipantsSpec

Filters conversations by participant count.

```python
from src.domain.specifications import MinimumParticipantsSpec

# At least 2 participants
spec = MinimumParticipantsSpec(min_participants=2)

if spec.is_satisfied_by(conversation):
    print("Multi-participant conversation")
```

### 6. EntityCountSpec

Filters conversations by entity count.

```python
from src.domain.specifications import EntityCountSpec

# At least 5 entities
spec = EntityCountSpec(min_entities=5)

if spec.is_satisfied_by(conversation):
    print("Rich conversation with many entities")
```

### 7. ContextRelevanceSpec

Filters context by relevance score threshold.

```python
from src.domain.specifications import ContextRelevanceSpec

# Highly relevant context (>= 0.80)
spec = ContextRelevanceSpec(min_relevance=0.80)

if spec.is_satisfied_by(context):
    print("Highly relevant context")
```

### 8. TierSpec

Filters by memory tier (Tier 1, 2, or 3).

```python
from src.domain.specifications import TierSpec

# Working memory only (Tier 1)
spec = TierSpec(tier=1)

# Knowledge graph only (Tier 2)
spec = TierSpec(tier=2)

# Development context only (Tier 3)
spec = TierSpec(tier=3)

if spec.is_satisfied_by(entity):
    print(f"Entity is in Tier {spec._tier}")
```

---

## Composing Specifications

The power of specifications comes from composition:

### AND Composition

Both specifications must be satisfied:

```python
from src.domain.specifications import (
    HighQualityConversationSpec,
    RecentConversationSpec,
    AndSpecification
)

# Method 1: Using AndSpecification
high_quality = HighQualityConversationSpec()
recent = RecentConversationSpec(days=7)
spec = AndSpecification(high_quality, recent)

# Method 2: Using & operator
spec = high_quality & recent

# Use it
if spec.is_satisfied_by(conversation):
    print("High quality AND recent conversation!")
```

### OR Composition

At least one specification must be satisfied:

```python
from src.domain.specifications import (
    HighQualityConversationSpec,
    MinimumParticipantsSpec,
    OrSpecification
)

# Method 1: Using OrSpecification
high_quality = HighQualityConversationSpec()
multi_participant = MinimumParticipantsSpec(min_participants=3)
spec = OrSpecification(high_quality, multi_participant)

# Method 2: Using | operator
spec = high_quality | multi_participant

# Use it
if spec.is_satisfied_by(conversation):
    print("Either high quality OR multi-participant!")
```

### NOT Composition

Negates a specification:

```python
from src.domain.specifications import (
    HighQualityConversationSpec,
    NotSpecification
)

# Method 1: Using NotSpecification
high_quality = HighQualityConversationSpec()
spec = NotSpecification(high_quality)

# Method 2: Using ~ operator
spec = ~high_quality

# Use it
if spec.is_satisfied_by(conversation):
    print("Low quality conversation")
```

### Complex Composition

Combine multiple specifications with parentheses:

```python
# (High quality AND recent) OR (Multi-participant AND relevant)
spec = (
    (HighQualityConversationSpec() & RecentConversationSpec(days=7)) |
    (MinimumParticipantsSpec(3) & EntityCountSpec(min_entities=5))
)

# Filter collection
interesting_conversations = [
    c for c in conversations 
    if spec.is_satisfied_by(c)
]
```

### Real-World Example

```python
# Find conversations for learning:
# - High quality (>= 0.85)
# - Recent (last 30 days)
# - Rich with entities (>= 10)
# - In the correct namespace
learning_spec = (
    HighQualityConversationSpec(min_quality=0.85) &
    RecentConversationSpec(days=30) &
    EntityCountSpec(min_entities=10) &
    NamespaceMatchSpec("workspace.backend")
)

# Apply to query
candidates = [
    conv for conv in all_conversations
    if learning_spec.is_satisfied_by(conv)
]
```

---

## Expression Specifications

For simple, one-off rules, use expression specifications:

### Basic Expression

```python
from src.domain.specifications import ExpressionSpecification

# Lambda-based specification
is_published = ExpressionSpecification(
    lambda post: post.is_published,
    description="Published posts"
)

# Use it
if is_published.is_satisfied_by(post):
    print("Post is published")
```

### Complex Expression

```python
# Multiple conditions in lambda
is_active_user = ExpressionSpecification(
    lambda user: user.is_active and user.last_login_days <= 30,
    description="Active users (logged in last 30 days)"
)

active_users = [u for u in users if is_active_user.is_satisfied_by(u)]
```

### Composing with Expressions

```python
# Mix expression specs with class-based specs
is_public = ExpressionSpecification(lambda x: x.is_public)
high_quality = HighQualityConversationSpec()

# Public AND high quality
spec = is_public & high_quality

public_high_quality = [
    c for c in conversations
    if spec.is_satisfied_by(c)
]
```

---

## Using in Query Handlers

Specifications shine in query handlers for filtering:

### Basic Filtering

```python
from src.application.queries import SearchContextQuery
from src.domain.specifications import (
    HighQualityConversationSpec,
    RecentConversationSpec,
    NamespaceMatchSpec
)

class SearchContextHandler:
    """Handler for searching conversations"""
    
    async def handle(self, query: SearchContextQuery) -> Result[List[ConversationDto]]:
        # Build specification from query parameters
        spec = self._build_specification(query)
        
        # Get all conversations
        all_conversations = await self._repository.get_all()
        
        # Filter using specification
        filtered = [
            conv for conv in all_conversations
            if spec.is_satisfied_by(conv)
        ]
        
        # Map to DTOs
        return Result.success([self._to_dto(c) for c in filtered])
    
    def _build_specification(self, query: SearchContextQuery):
        """Build specification from query parameters"""
        specs = []
        
        # Quality filter
        if query.min_quality:
            specs.append(HighQualityConversationSpec(query.min_quality))
        
        # Recency filter
        if query.recent_only:
            specs.append(RecentConversationSpec(days=7))
        
        # Namespace filter
        if query.namespace:
            specs.append(NamespaceMatchSpec(query.namespace))
        
        # Combine all specs with AND
        if len(specs) == 0:
            return ExpressionSpecification(lambda x: True)  # Match all
        elif len(specs) == 1:
            return specs[0]
        else:
            # Combine with AND
            result = specs[0]
            for spec in specs[1:]:
                result = result & spec
            return result
```

### Advanced Filtering

```python
class FindSimilarPatternsHandler:
    """Find patterns similar to current context"""
    
    async def handle(self, query: FindSimilarPatternsQuery) -> Result[List[PatternDto]]:
        # Build complex specification
        spec = (
            # Must match namespace
            NamespaceMatchSpec(query.namespace) &
            # Must have high confidence
            PatternConfidenceSpec(min_confidence=0.75) &
            # Must match type if specified
            (ExpressionSpecification(lambda p: p.pattern_type == query.pattern_type)
             if query.pattern_type else
             ExpressionSpecification(lambda p: True))
        )
        
        # Get all patterns
        all_patterns = await self._repository.get_all()
        
        # Filter and sort
        matching = [p for p in all_patterns if spec.is_satisfied_by(p)]
        sorted_patterns = sorted(matching, 
                                key=lambda p: p.confidence_score, 
                                reverse=True)
        
        # Return top N
        return Result.success([
            self._to_dto(p) 
            for p in sorted_patterns[:query.max_results]
        ])
```

---

## Testing Specifications

### Unit Testing

Test specifications in isolation:

```python
import pytest
from datetime import datetime, timedelta

class TestHighQualityConversationSpec:
    
    def test_high_quality_satisfied(self):
        """High quality conversation should satisfy spec"""
        spec = HighQualityConversationSpec(min_quality=0.70)
        
        conversation = create_conversation(quality_score=0.85)
        
        assert spec.is_satisfied_by(conversation)
    
    def test_low_quality_not_satisfied(self):
        """Low quality conversation should not satisfy spec"""
        spec = HighQualityConversationSpec(min_quality=0.70)
        
        conversation = create_conversation(quality_score=0.50)
        
        assert not spec.is_satisfied_by(conversation)
    
    def test_boundary_satisfied(self):
        """Boundary value should satisfy spec"""
        spec = HighQualityConversationSpec(min_quality=0.70)
        
        conversation = create_conversation(quality_score=0.70)
        
        assert spec.is_satisfied_by(conversation)
    
    def test_custom_threshold(self):
        """Custom threshold should work"""
        spec = HighQualityConversationSpec(min_quality=0.90)
        
        good = create_conversation(quality_score=0.95)
        not_good = create_conversation(quality_score=0.85)
        
        assert spec.is_satisfied_by(good)
        assert not spec.is_satisfied_by(not_good)
```

### Testing Composition

```python
class TestSpecificationComposition:
    
    def test_and_composition(self):
        """AND composition should require both specs"""
        high_quality = HighQualityConversationSpec(min_quality=0.70)
        recent = RecentConversationSpec(days=7)
        
        spec = high_quality & recent
        
        # Both conditions met
        good_recent = create_conversation(
            quality_score=0.85,
            captured_at=datetime.now() - timedelta(days=3)
        )
        assert spec.is_satisfied_by(good_recent)
        
        # Only one condition met
        good_old = create_conversation(
            quality_score=0.85,
            captured_at=datetime.now() - timedelta(days=30)
        )
        assert not spec.is_satisfied_by(good_old)
    
    def test_or_composition(self):
        """OR composition should accept either spec"""
        high_quality = HighQualityConversationSpec(min_quality=0.70)
        multi_participant = MinimumParticipantsSpec(min_participants=3)
        
        spec = high_quality | multi_participant
        
        # High quality but single participant
        high_single = create_conversation(
            quality_score=0.85,
            participant_count=1
        )
        assert spec.is_satisfied_by(high_single)
        
        # Low quality but multi-participant
        low_multi = create_conversation(
            quality_score=0.50,
            participant_count=4
        )
        assert spec.is_satisfied_by(low_multi)
        
        # Neither condition
        low_single = create_conversation(
            quality_score=0.50,
            participant_count=1
        )
        assert not spec.is_satisfied_by(low_single)
    
    def test_not_composition(self):
        """NOT composition should negate spec"""
        high_quality = HighQualityConversationSpec(min_quality=0.70)
        
        spec = ~high_quality
        
        low = create_conversation(quality_score=0.50)
        high = create_conversation(quality_score=0.85)
        
        assert spec.is_satisfied_by(low)
        assert not spec.is_satisfied_by(high)
```

---

## Best Practices

### 1. Name Specifications by Business Rules

Use domain language that non-technical stakeholders understand:

```python
# ✅ Good - Clear business meaning
class HighQualityConversationSpec(ISpecification):
    pass

# ❌ Bad - Technical implementation detail
class QualityScoreGreaterThanSeventySpec(ISpecification):
    pass
```

### 2. Keep Specifications Small and Focused

Each specification should encapsulate ONE business rule:

```python
# ✅ Good - Single responsibility
class HighQualityConversationSpec(ISpecification):
    def is_satisfied_by(self, conversation) -> bool:
        return conversation.quality_score >= self._min_quality

# ❌ Bad - Multiple concerns
class ComplexConversationSpec(ISpecification):
    def is_satisfied_by(self, conversation) -> bool:
        return (conversation.quality_score >= 0.70 and
                conversation.participant_count >= 2 and
                conversation.entity_count >= 5)
```

### 3. Compose Rather Than Extend

Build complex rules by composing simple specifications:

```python
# ✅ Good - Composition
high_quality = HighQualityConversationSpec()
multi_participant = MinimumParticipantsSpec(2)
many_entities = EntityCountSpec(5)

complex_spec = high_quality & multi_participant & many_entities

# ❌ Bad - Complex inheritance
class ComplexConversationSpec(HighQualityConversationSpec, 
                              MinimumParticipantsSpec):
    pass
```

### 4. Make Specifications Immutable

Specifications should not change after creation:

```python
# ✅ Good - Immutable state
class HighQualityConversationSpec(ISpecification):
    def __init__(self, min_quality: float = 0.70):
        self._min_quality = min_quality  # Read-only

# ❌ Bad - Mutable state
class HighQualityConversationSpec(ISpecification):
    def set_threshold(self, value: float):
        self._min_quality = value
```

### 5. Provide Meaningful String Representations

Override `__str__` for debugging:

```python
class HighQualityConversationSpec(ISpecification):
    def __str__(self) -> str:
        return f"HighQualityConversation(>={self._min_quality})"

# Useful for debugging
spec = high_quality & recent
print(spec)  # "(HighQualityConversation(>=0.70) AND RecentConversation(<=7 days))"
```

### 6. Use Expression Specs for Simple, One-Off Rules

Don't create a class if a lambda suffices:

```python
# ✅ Good - Expression for simple rule
is_active = ExpressionSpecification(lambda x: x.is_active)

# ❌ Bad - Class for simple rule
class IsActiveSpec(ISpecification):
    def is_satisfied_by(self, entity) -> bool:
        return entity.is_active
```

### 7. Test Boundary Conditions

Always test boundary values:

```python
def test_boundary_conditions(self):
    spec = HighQualityConversationSpec(min_quality=0.70)
    
    # Exactly at boundary
    assert spec.is_satisfied_by(create_conversation(quality_score=0.70))
    
    # Just below boundary
    assert not spec.is_satisfied_by(create_conversation(quality_score=0.69))
    
    # Just above boundary
    assert spec.is_satisfied_by(create_conversation(quality_score=0.71))
```

---

## Example: Complete Specification

Here's a complete, production-ready specification:

```python
"""Specification for finding valuable conversations for learning"""
from datetime import datetime, timedelta
from src.domain.specifications import ISpecification


class LearningCandidateSpec(ISpecification):
    """Identifies conversations that are good candidates for learning
    
    A conversation is a learning candidate if it:
    - Has high quality (>= 0.85)
    - Is recent (last 30 days)
    - Has many entities (>= 10)
    - Has multiple participants (>= 2)
    - Is in the correct namespace
    """
    
    def __init__(
        self,
        namespace: str,
        min_quality: float = 0.85,
        max_age_days: int = 30,
        min_entities: int = 10,
        min_participants: int = 2
    ):
        """Initialize learning candidate specification
        
        Args:
            namespace: Required namespace to match
            min_quality: Minimum quality score (default: 0.85)
            max_age_days: Maximum age in days (default: 30)
            min_entities: Minimum entity count (default: 10)
            min_participants: Minimum participants (default: 2)
        """
        self._namespace = namespace.lower()
        self._min_quality = min_quality
        self._max_age_days = max_age_days
        self._min_entities = min_entities
        self._min_participants = min_participants
        self._cutoff_date = datetime.now() - timedelta(days=max_age_days)
    
    def is_satisfied_by(self, conversation) -> bool:
        """Check if conversation is a learning candidate
        
        Args:
            conversation: Conversation to evaluate
            
        Returns:
            True if conversation meets all criteria, False otherwise
        """
        return (
            # Quality threshold
            conversation.quality_score >= self._min_quality and
            
            # Recency threshold
            conversation.captured_at >= self._cutoff_date and
            
            # Entity richness
            conversation.entity_count >= self._min_entities and
            
            # Multi-participant conversation
            conversation.participant_count >= self._min_participants and
            
            # Namespace match (case-insensitive)
            conversation.namespace.lower() == self._namespace
        )
    
    def __str__(self) -> str:
        """String representation for debugging"""
        return (
            f"LearningCandidate("
            f"namespace={self._namespace}, "
            f"quality>={self._min_quality}, "
            f"age<={self._max_age_days}d, "
            f"entities>={self._min_entities}, "
            f"participants>={self._min_participants})"
        )


# Usage
spec = LearningCandidateSpec(
    namespace="workspace.backend",
    min_quality=0.90,
    max_age_days=14
)

candidates = [
    conv for conv in all_conversations
    if spec.is_satisfied_by(conv)
]
```

---

## Summary

The Specification Pattern provides a powerful way to express business rules in CORTEX:

- **Composable** - Combine simple rules into complex ones with `&`, `|`, `~`
- **Reusable** - Share business logic across queries and commands
- **Testable** - Test rules in isolation from infrastructure
- **Readable** - Express domain concepts in clear, business language

For more information, see:
- [Validation Framework Guide](validation-guide.md)
- [Clean Architecture Overview](../README.md)
- API Reference (coming soon)

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Proprietary
