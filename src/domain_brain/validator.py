"""Consistency validator for Domain Brain.

Validates domain schemas, referential integrity, circular dependencies, and conflicts.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass

from src.domain_brain.models import Domain, Entity, Conflict, ConflictResolution


@dataclass
class ValidationResult:
    """Result of validation operation.

    Attributes:
        is_valid: Whether validation passed
        errors: List of validation errors
        warnings: List of validation warnings
        conflicts_detected: List of conflicts found
    """

    is_valid: bool
    errors: List[str] = None
    warnings: List[str] = None
    conflicts_detected: List[str] = None

    def __post_init__(self) -> None:
        """Initialize default lists."""
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
        if self.conflicts_detected is None:
            self.conflicts_detected = []


class ConsistencyValidator:
    """Validates domain consistency across multiple dimensions.

    Performs:
    - JSON Schema validation against domain-schema.json
    - Referential integrity checks (all referenced entities exist)
    - Circular dependency detection (A -> B -> A is invalid)
    - Conflict detection (multiple sources disagree on same attribute)
    """

    def __init__(self, schema_path: Optional[Path] = None) -> None:
        """Initialize validator.

        Args:
            schema_path: Path to JSON schema file. If None, uses default schema.
        """
        self.schema_path = schema_path
        self.schema: Dict[str, Any] = {}
        if schema_path and schema_path.exists():
            with open(schema_path) as f:
                self.schema = json.load(f)

    def validate_domain(self, domain: Domain) -> ValidationResult:
        """Validate entire domain.

        Args:
            domain: Domain to validate

        Returns:
            ValidationResult with all validation checks
        """
        result = ValidationResult(is_valid=True)

        # Check referential integrity
        integrity_errors = self._validate_referential_integrity(domain)
        result.errors.extend(integrity_errors)

        # Check for circular dependencies
        circular_errors = self._detect_circular_dependencies(domain)
        result.errors.extend(circular_errors)

        # Detect conflicts
        conflicts = self._detect_conflicts(domain)
        result.conflicts_detected.extend(conflicts)

        # Schema validation if schema is loaded
        if self.schema:
            schema_errors = self._validate_schema(domain)
            result.errors.extend(schema_errors)

        result.is_valid = len(result.errors) == 0

        return result

    def _validate_referential_integrity(self, domain: Domain) -> List[str]:
        """Validate that all entity references exist.

        Args:
            domain: Domain to check

        Returns:
            List of referential integrity errors
        """
        errors = []
        entity_ids: Set[str] = set(domain.entities.keys())

        for entity_id, entity in domain.entities.items():
            # Check for referenced entities in metadata
            refs = entity.metadata.get("references", [])
            if isinstance(refs, list):
                for ref in refs:
                    if ref not in entity_ids:
                        errors.append(
                            f"Entity {entity_id} references non-existent entity {ref}"
                        )

            # Check for dependencies
            deps = entity.metadata.get("depends_on", [])
            if isinstance(deps, list):
                for dep in deps:
                    if dep not in entity_ids:
                        errors.append(
                            f"Entity {entity_id} depends on non-existent entity {dep}"
                        )

        return errors

    def _detect_circular_dependencies(self, domain: Domain) -> List[str]:
        """Detect circular dependencies in domain entities.

        Args:
            domain: Domain to check

        Returns:
            List of circular dependency errors
        """
        errors = []
        visited: Set[str] = set()
        rec_stack: Set[str] = set()

        def has_cycle(entity_id: str) -> bool:
            """Check if entity has circular dependency."""
            visited.add(entity_id)
            rec_stack.add(entity_id)

            entity = domain.entities.get(entity_id)
            if not entity:
                return False

            # Check dependencies
            deps = entity.metadata.get("depends_on", [])
            if isinstance(deps, list):
                for dep in deps:
                    if dep not in visited:
                        if has_cycle(dep):
                            return True
                    elif dep in rec_stack:
                        errors.append(
                            f"Circular dependency detected: {entity_id} -> {dep} -> ... -> {entity_id}"
                        )
                        return True

            rec_stack.remove(entity_id)
            return False

        for entity_id in domain.entities:
            if entity_id not in visited:
                has_cycle(entity_id)

        return errors

    def _detect_conflicts(self, domain: Domain) -> List[str]:
        """Detect conflicts between different sources on same attribute.

        Args:
            domain: Domain to check

        Returns:
            List of conflict descriptions
        """
        conflicts = []

        # Check for entity conflicts (same entity from different sources)
        source_entities: Dict[str, List[Entity]] = {}
        for entity in domain.entities.values():
            if entity.source not in source_entities:
                source_entities[entity.source] = []
            source_entities[entity.source].append(entity)

        # Find conflicts: multiple sources claiming same entity
        for entity in domain.entities.values():
            same_name_from_other_sources = [
                e for e in domain.entities.values()
                if e.name == entity.name and e.source != entity.source
            ]
            if same_name_from_other_sources:
                sources = [e.source for e in [entity] + same_name_from_other_sources]
                conflict_msg = f"Conflict: Entity '{entity.name}' exists in sources: {sources}"
                if conflict_msg not in conflicts:
                    conflicts.append(conflict_msg)

        return conflicts

    def _validate_schema(self, domain: Domain) -> List[str]:
        """Validate domain against JSON schema.

        Args:
            domain: Domain to validate

        Returns:
            List of schema validation errors
        """
        errors = []

        if not self.schema:
            return errors

        # Basic schema validation (simplified for now)
        required_fields = self.schema.get("required", [])
        domain_dict = domain.to_dict()

        for field in required_fields:
            if field not in domain_dict or domain_dict[field] is None:
                errors.append(f"Required field missing: {field}")

        return errors

    def validate_entity(self, entity: Entity, domain: Domain) -> ValidationResult:
        """Validate a single entity within domain context.

        Args:
            entity: Entity to validate
            domain: Parent domain for reference checking

        Returns:
            ValidationResult for the entity
        """
        result = ValidationResult(is_valid=True)
        entity_ids = set(domain.entities.keys())

        # Check references
        refs = entity.metadata.get("references", [])
        if isinstance(refs, list):
            for ref in refs:
                if ref not in entity_ids:
                    result.errors.append(
                        f"Entity references non-existent entity: {ref}"
                    )

        # Check dependencies
        deps = entity.metadata.get("depends_on", [])
        if isinstance(deps, list):
            for dep in deps:
                if dep not in entity_ids:
                    result.errors.append(
                        f"Entity depends on non-existent entity: {dep}"
                    )

        result.is_valid = len(result.errors) == 0
        return result
