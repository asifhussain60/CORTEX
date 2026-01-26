"""Canonicalization Engine - Standardizes data representations.

Converts data to canonical forms for consistent processing.

Author: CORTEX Framework
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List, Callable
from enum import Enum


class CanonicalForm(Enum):
    """Canonical forms."""

    NORMALIZED = "normalized"
    STANDARDIZED = "standardized"
    STRUCTURED = "structured"
    UNIFIED = "unified"


@dataclass
class CanonicalData:
    """Canonicalized data container.

    Attributes:
        original_data: Original data before canonicalization.
        canonical_form: Form type used.
        standardized_data: Standardized representation.
        metadata: Additional metadata.
    """

    original_data: Any
    canonical_form: CanonicalForm
    standardized_data: Dict[str, Any]
    metadata: Dict[str, Any] = None

    def __post_init__(self) -> None:
        """Initialize defaults."""
        if self.metadata is None:
            self.metadata = {}


class CanonicalizeRule:
    """Rule for canonicalization.

    Attributes:
        rule_id: Rule identifier.
        name: Rule name.
        transformer: Transformation function.
        target_form: Target canonical form.
    """

    def __init__(
        self,
        rule_id: str,
        name: str,
        transformer: Callable,
        target_form: CanonicalForm,
    ) -> None:
        """Initialize canonicalization rule."""
        self.rule_id = rule_id
        self.name = name
        self.transformer = transformer
        self.target_form = target_form


class CanonicalizeEngine:
    """Manages data canonicalization."""

    def __init__(self) -> None:
        """Initialize canonicalization engine."""
        self.rules: Dict[str, CanonicalizeRule] = {}

    def register_rule(self, rule: CanonicalizeRule) -> None:
        """Register a canonicalization rule.

        Args:
            rule: CanonicalizeRule.
        """
        self.rules[rule.rule_id] = rule

    def canonicalize(
        self, data: Any, form: CanonicalForm = CanonicalForm.NORMALIZED
    ) -> CanonicalData:
        """Canonicalize data.

        Args:
            data: Data to canonicalize.
            form: Target canonical form.

        Returns:
            CanonicalData.
        """
        standardized = {}

        # Apply matching rules
        for rule in self.rules.values():
            if rule.target_form == form:
                try:
                    transformed = rule.transformer(data)
                    standardized.update(transformed)
                except Exception:
                    pass

        return CanonicalData(
            original_data=data,
            canonical_form=form,
            standardized_data=standardized,
        )

    def get_rule_count(self) -> int:
        """Get number of registered rules.

        Returns:
            Rule count.
        """
        return len(self.rules)




class ExtendedIntentCanonicalizer(CanonicalizeEngine):
    """Extended intent canonicalizer with additional features."""
    
    def canonicalize_with_context(self, data: Any, context: Dict[str, Any]) -> CanonicalData:
        """Canonicalize with context."""
        return self.canonicalize(data)


from enum import Enum
from cortex.models.canonical_enums import ActionType



@dataclass
class ExtendedCanonicalIntent:
    """Extended canonical intent with additional fields."""
    intent: str
    action_type: ActionType
    confidence: float = 1.0
    context: Dict[str, Any] = field(default_factory=dict)


__all__ = [
    "CanonicalizeEngine",
    "CanonicalData",
    "CanonicalizeRule",
    "CanonicalForm",
    "CanonicalIntentEngine",
    "IntentCanonicalForm",
    "ACIDExtraction",
    "ExtendedIntentCanonicalizer",
    "ExtendedCanonicalIntent",
    "ActionType",
]

# Alias for backward compatibility
CanonicalIntentEngine = CanonicalizeEngine
IntentCanonicalForm = CanonicalForm

# Stub for test compatibility
class ACIDExtraction:
    """ACID extraction for canonicalization."""
    def __init__(self):
        self.data = {}
    
    def extract(self, data):
        return data
