"""Constraint validator for Knowledge Graph schema compliance.

Validates that entities and relationships conform to the defined schema
constraints, including node type definitions, relationship cardinality,
and property requirements.

Enables schema enforcement across all adapter implementations.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Set

# Schema definitions
VALID_ENTITY_TYPES: Set[str] = {"Entity", "Rule", "Service", "API", "Domain"}
VALID_RELATIONSHIP_TYPES: Set[str] = {
    "CALLS",
    "DEPENDS_ON",
    "IMPLEMENTS",
    "HAS_RULE",
    "BELONGS_TO",
}

# Cardinality constraints (not enforced in this phase, documented for future)
CARDINALITY_CONSTRAINTS = {
    "Rule": {
        "HAS_RULE": "many-to-many",  # Rules can have multiple rules, entities can have multiple rules
    },
    "Service": {
        "CALLS": "many-to-many",  # Services can call multiple services
        "DEPENDS_ON": "many-to-many",  # Services can depend on multiple services
    },
}


@dataclass
class ConstraintViolation:
    """Represents a schema constraint violation.

    Attributes:
        field: Field or constraint that was violated
        value: Value that violated the constraint
        reason: Human-readable explanation of the violation
    """

    field: str
    value: Any
    reason: str


class ConstraintValidator:
    """Validates Knowledge Graph entities and relationships against schema.

    Enforces:
      - Valid entity types (from VALID_ENTITY_TYPES)
      - Valid relationship types (from VALID_RELATIONSHIP_TYPES)
      - Relationship cardinality constraints
      - Property requirements
    """

    @staticmethod
    def validate_entity_type(entity_type: str) -> None:
        """Validate entity type is in allowed set.

        Args:
            entity_type: Entity type to validate

        Raises:
            ValueError: If entity_type not in VALID_ENTITY_TYPES
        """
        if entity_type not in VALID_ENTITY_TYPES:
            raise ValueError(
                f"Invalid entity type '{entity_type}'. "
                f"Must be one of: {', '.join(sorted(VALID_ENTITY_TYPES))}"
            )

    @staticmethod
    def validate_relationship_type(rel_type: str) -> None:
        """Validate relationship type is in allowed set.

        Args:
            rel_type: Relationship type to validate

        Raises:
            ValueError: If rel_type not in VALID_RELATIONSHIP_TYPES
        """
        if rel_type not in VALID_RELATIONSHIP_TYPES:
            raise ValueError(
                f"Invalid relationship type '{rel_type}'. "
                f"Must be one of: {', '.join(sorted(VALID_RELATIONSHIP_TYPES))}"
            )

    @staticmethod
    def validate_entity(
        entity_id: str,
        entity_type: str,
        properties: Dict[str, Any],
    ) -> List[ConstraintViolation]:
        """Validate an entity against all constraints.

        Args:
            entity_id: Entity identifier
            entity_type: Entity type
            properties: Entity properties

        Returns:
            List[ConstraintViolation]: Any violations found (empty if valid)
        """
        violations: List[ConstraintViolation] = []

        # Validate entity type
        try:
            ConstraintValidator.validate_entity_type(entity_type)
        except ValueError as e:
            violations.append(
                ConstraintViolation(field="type", value=entity_type, reason=str(e))
            )

        # Validate entity ID is non-empty
        if not entity_id or not isinstance(entity_id, str):
            violations.append(
                ConstraintViolation(
                    field="id",
                    value=entity_id,
                    reason="Entity ID must be non-empty string",
                )
            )

        return violations

    @staticmethod
    def validate_relationship(
        source_id: str,
        source_type: str,
        rel_type: str,
        target_id: str,
        target_type: str,
    ) -> List[ConstraintViolation]:
        """Validate a relationship against all constraints.

        Args:
            source_id: Source entity ID
            source_type: Source entity type
            rel_type: Relationship type
            target_id: Target entity ID
            target_type: Target entity type

        Returns:
            List[ConstraintViolation]: Any violations found
        """
        violations: List[ConstraintViolation] = []

        # Validate relationship type
        try:
            ConstraintValidator.validate_relationship_type(rel_type)
        except ValueError as e:
            violations.append(
                ConstraintViolation(field="rel_type", value=rel_type, reason=str(e))
            )

        # Validate entity IDs are non-empty
        if not source_id or not isinstance(source_id, str):
            violations.append(
                ConstraintViolation(
                    field="source_id",
                    value=source_id,
                    reason="Source ID must be non-empty string",
                )
            )

        if not target_id or not isinstance(target_id, str):
            violations.append(
                ConstraintViolation(
                    field="target_id",
                    value=target_id,
                    reason="Target ID must be non-empty string",
                )
            )

        return violations

    @staticmethod
    def get_valid_entity_types() -> List[str]:
        """Get list of valid entity types.

        Returns:
            List[str]: Valid entity types sorted
        """
        return sorted(list(VALID_ENTITY_TYPES))

    @staticmethod
    def get_valid_relationship_types() -> List[str]:
        """Get list of valid relationship types.

        Returns:
            List[str]: Valid relationship types sorted
        """
        return sorted(list(VALID_RELATIONSHIP_TYPES))
