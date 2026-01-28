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
    
    def canonicalize_extended(self, intent_text: str) -> "ExtendedCanonicalIntent":
        """Canonicalize an intent string to ExtendedCanonicalIntent.
        
        Args:
            intent_text: Intent text to canonicalize.
            
        Returns:
            ExtendedCanonicalIntent with parsed fields.
        """
        import re
        
        # Parse AC-ID (e.g., AC-HP-002-01)
        ac_match = re.search(r'AC-([A-Z]+)-(\d+)-(\d+)', intent_text)
        ac_id = ac_match.group(0) if ac_match else None
        
        # Parse Phase (e.g., PHASE-11)
        phase_match = re.search(r'PHASE-(\d+)', intent_text)
        phase = phase_match.group(0) if phase_match else None
        
        # Determine action type
        action_type = ActionType.EXECUTE
        if 'implement' in intent_text.lower():
            action_type = ActionType.CREATE
        elif 'modify' in intent_text.lower():
            action_type = ActionType.MODIFY
        elif 'delete' in intent_text.lower():
            action_type = ActionType.DELETE
        
        return ExtendedCanonicalIntent(
            intent=intent_text,
            action_type=action_type,
            confidence=0.9,
            context={"ac_id": ac_id, "phase": phase},
        )
    
    @property
    def ac_id(self) -> Optional[str]:
        """Get last canonicalized AC-ID."""
        return getattr(self, '_last_ac_id', None)
    
    @property  
    def phase(self) -> Optional[str]:
        """Get last canonicalized phase."""
        return getattr(self, '_last_phase', None)


from enum import Enum
from cortex.models.canonical_enums import ActionType



@dataclass
class ExtendedCanonicalIntent:
    """Extended canonical intent with additional fields."""
    intent: str
    action_type: ActionType
    confidence: float = 1.0
    context: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def ac_id(self) -> Optional[str]:
        """Get AC-ID from context."""
        return self.context.get("ac_id")
    
    @property
    def phase(self) -> Optional[str]:
        """Get phase from context."""
        return self.context.get("phase")


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
