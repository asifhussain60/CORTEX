# Code Style Guide

> Auto-generated from cortex-impl-map.yaml on 2026-01-21

**Last Updated:** 2026-01-21  
**Audience:** Contributors, Developers

## Governance Rules

CORTEX enforces style via Tier 0 governance rules:

| Rule | Requirement | Enforcement |
|------|-------------|-------------|
| **CORE-011** | Type hints on all functions | STRICT |
| **CORE-012** | Docstrings (Google format) | STRICT |
| **CORE-013** | No bare except | STRICT |
| **CORE-028** | Kebab-case ≤25 chars (files) | STRICT |

## Type Hints (CORE-011)

All functions MUST have type hints:

```python
# ✅ Correct
def calculate_complexity(
    context: Dict[str, Any],
    weights: List[float]
) -> float:
    """Calculate complexity score."""
    return sum(weights)

# ❌ Incorrect
def calculate_complexity(context, weights):
    return sum(weights)
```

### Common Types

```python
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass

# Optional parameters
def query(name: str, limit: Optional[int] = None) -> List[str]:
    pass

# Union types
def process(data: Union[str, bytes]) -> str:
    pass

# Generic Dict
def get_config() -> Dict[str, Any]:
    pass
```

## Docstrings (CORE-012)

Use Google-style docstrings:

```python
def validate_rule(
    rule_id: str,
    context: Dict[str, Any]
) -> ValidationResult:
    """
    Validate a governance rule against context.
    
    Args:
        rule_id: The rule identifier (e.g., "CORE-001").
        context: Execution context with relevant attributes.
    
    Returns:
        ValidationResult with is_valid flag and any violations.
    
    Raises:
        RuleNotFoundError: If rule_id doesn't exist.
        ValidationError: If context is malformed.
    
    Example:
        >>> result = validate_rule("CORE-001", {"lines": 400})
        >>> result.is_valid
        True
    
    AC-ID: AC-GOV-002
    """
```

### Class Docstrings

```python
@dataclass
class GovernanceRule:
    """
    A governance rule with enforcement configuration.
    
    Attributes:
        id: Unique rule identifier (e.g., "CORE-001").
        description: Human-readable rule description.
        enforcement: Enforcement level (BLOCKED, STRICT, ADVISORY).
        tier: Governance tier (0-3).
    
    Example:
        >>> rule = GovernanceRule(
        ...     id="CORE-001",
        ...     description="Response must be <500 lines",
        ...     enforcement=Enforcement.BLOCKED,
        ...     tier=0
        ... )
    """
    id: str
    description: str
    enforcement: Enforcement
    tier: int
```

## Error Handling (CORE-013)

Never use bare except:

```python
# ✅ Correct
try:
    result = risky_operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    raise
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise OperationError(f"Failed: {e}") from e

# ❌ Incorrect
try:
    result = risky_operation()
except:
    pass  # Never do this
```

## File Naming (CORE-028)

- Kebab-case for files
- Maximum 25 characters
- Descriptive names

```
✅ governance-rule.py
✅ mcp-server.py
✅ intent-router.py

❌ GovernanceRule.py      # PascalCase
❌ governance_rule.py     # snake_case (for new files)
❌ this-is-a-very-long-filename-that-exceeds-limit.py
```

## Import Order

```python
# 1. Standard library
import os
from typing import Dict, List

# 2. Third-party
import pytest
from dataclasses import dataclass

# 3. Local/project
from cortex.core.governance import GovernanceRule
from cortex.orchestrators import BaseOrchestrator
```

## Class Structure

```python
class MyOrchestrator(BaseOrchestrator):
    """Orchestrator description."""
    
    # 1. Class attributes
    MAX_ROUNDS: int = 10
    
    # 2. __init__
    def __init__(self, config: Config) -> None:
        """Initialize orchestrator."""
        super().__init__()
        self.config = config
    
    # 3. Properties
    @property
    def name(self) -> str:
        """Orchestrator name."""
        return self.__class__.__name__
    
    # 4. Public methods
    async def execute(self, context: Context) -> Result:
        """Execute orchestration."""
        pass
    
    # 5. Private methods
    def _validate(self, data: Dict) -> bool:
        """Internal validation."""
        pass
```

## Linting Tools

```powershell
# Ruff (fast Python linter)
ruff check cortex/ --fix

# Black (formatter)
black cortex/

# mypy (type checker)
mypy cortex/ --strict
```

### Pre-commit Config

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
        args: [--fix]
  - repo: https://github.com/psf/black
    rev: 23.0.0
    hooks:
      - id: black
```

## Related

- [Testing Strategy](3-testing-strategy.md)
- [Governance Rules Reference](../05-reference/governance-rules-reference.md)
- [Contributing Guidelines](1-contributing-guidelines.md)
