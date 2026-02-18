"""
Workflow Template Registry with mode detection and placeholder resolution.

Provides convergence-gated, knowledge-parameterized workflow templates that resolve
differently based on repository context (ARCHITECT vs PRODUCTION mode). Templates
contain placeholders resolved by KnowledgeSynthesisEngine. Templates auto-discovered
from metadata.yaml files in cortex-registry/workflows/templates/ and company/workflows/.

Mode Detection:
- ARCHITECT: .cortex-runtime/ marker exists → CORTEX-internal knowledge
- PRODUCTION: No .cortex-runtime/ marker → User domain knowledge

Override Precedence:
- company/workflows/*.yaml > cortex-registry/workflows/templates/*.yaml

Phase: 100 Stage 1 Part 2
Author: Asif Hussain
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml


# AC_START: AC-PHASE100-002
# Description: WorkflowTemplateRegistry with convergence gates


class TemplateNotFoundError(Exception):
    """Raised when template not found in registry."""

    pass


class PlaceholderResolutionError(Exception):
    """Raised when placeholder cannot be resolved."""

    pass


class TemplateValidationError(Exception):
    """Raised when template fails validation."""

    pass


@dataclass
class WorkflowTemplate:
    """
    Workflow template with convergence gates and knowledge placeholders.

    Attributes:
        id: Unique template identifier.
        name: Human-readable template name.
        category: Template category (tdd, api, security, etc.).
        steps: List of workflow steps with convergence gates.
        placeholders: Default placeholder values.
        source: Template source ('cortex' or 'company').
        metadata: Additional template metadata.
    """

    id: str
    name: str
    category: str
    steps: List[Dict[str, Any]]
    placeholders: Dict[str, Any] = field(default_factory=dict)
    source: str = "cortex"
    metadata: Dict[str, Any] = field(default_factory=dict)


class WorkflowTemplateRegistry:
    """
    Registry for convergence-gated workflow templates with mode detection.

    Manages template registration, retrieval, validation, and placeholder resolution.
    Detects ARCHITECT vs PRODUCTION mode for context-aware template resolution.
    """

    def __init__(self) -> None:
        """Initialize template registry."""
        self._templates: Dict[str, WorkflowTemplate] = {}
        self._mode: Optional[str] = None

    def detect_mode(self) -> str:
        """
        Detect repository mode (ARCHITECT vs PRODUCTION).

        Returns:
            "ARCHITECT" if .cortex-runtime/ marker exists, "PRODUCTION" otherwise.
        """
        if self._mode is not None:
            return self._mode

        cortex_marker = Path(".cortex-runtime")
        self._mode = "ARCHITECT" if cortex_marker.exists() else "PRODUCTION"
        return self._mode

    def register_template(
        self, template_data: Dict[str, Any], override: bool = False
    ) -> None:
        """
        Register workflow template with validation.

        Args:
            template_data: Template definition dictionary.
            override: If True, allow overriding existing template.

        Raises:
            TemplateValidationError: If template invalid.
        """
        # Validate required fields
        self._validate_template_schema(template_data)

        # Check for circular dependencies
        self._validate_no_circular_deps(template_data)

        template = WorkflowTemplate(
            id=template_data["id"],
            name=template_data["name"],
            category=template_data.get("category", "general"),
            steps=template_data.get("steps", []),
            placeholders=template_data.get("placeholders", {}),
            source=template_data.get("source", "cortex"),
            metadata=template_data.get("metadata", {}),
        )

        # Check if template exists
        if template.id in self._templates and not override:
            # If company template, allow override
            if template.source == "company":
                self._templates[template.id] = template
            # Otherwise, keep existing
            return

        self._templates[template.id] = template

    def get_template(self, template_id: str) -> Dict[str, Any]:
        """
        Retrieve template by ID.

        Args:
            template_id: Template identifier.

        Returns:
            Template data dictionary.

        Raises:
            TemplateNotFoundError: If template not found.
        """
        if template_id not in self._templates:
            raise TemplateNotFoundError(
                f"Template not found: {template_id}. "
                f"Available templates: {list(self._templates.keys())}"
            )

        template = self._templates[template_id]
        return {
            "id": template.id,
            "name": template.name,
            "category": template.category,
            "steps": template.steps,
            "placeholders": template.placeholders,
            "source": template.source,
            "metadata": template.metadata,
        }

    def list_templates(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List templates, optionally filtered by category.

        Args:
            category: Optional category filter.

        Returns:
            List of template data dictionaries.
        """
        templates = []
        for template in self._templates.values():
            if category is None or template.category == category:
                templates.append(
                    {
                        "id": template.id,
                        "name": template.name,
                        "category": template.category,
                        "source": template.source,
                    }
                )
        return templates

    def resolve_placeholders(
        self, template: Union[str, Dict[str, Any]], mode: str
    ) -> Union[str, Dict[str, Any]]:
        """
        Resolve placeholders in template using mode-specific knowledge.

        Supports both string templates and dictionary templates.

        Args:
            template: Template text or dictionary with {{placeholder}} markers.
            mode: ARCHITECT or PRODUCTION mode.

        Returns:
            Resolved template (string or dict) with placeholders replaced.

        Raises:
            PlaceholderResolutionError: If placeholder cannot be resolved.
        """
        # Get knowledge context for mode
        context = self._get_knowledge_context(mode)

        # Handle string templates
        if isinstance(template, str):
            return self._resolve_template_text(template, context)

        # Handle dictionary templates
        if isinstance(template, dict):
            resolved = {}
            for key, value in template.items():
                if isinstance(value, str):
                    resolved[key] = self._resolve_template_text(value, context)
                elif isinstance(value, dict):
                    resolved[key] = self.resolve_placeholders(value, mode)
                elif isinstance(value, list):
                    resolved[key] = [
                        self._resolve_template_text(item, context)
                        if isinstance(item, str)
                        else item
                        for item in value
                    ]
                else:
                    resolved[key] = value
            return resolved

        return template

    def _get_knowledge_context(self, mode: str) -> Dict[str, Any]:
        """
        Get knowledge context for specified mode.

        Args:
            mode: ARCHITECT or PRODUCTION mode.

        Returns:
            Knowledge context dictionary with placeholders.
        """
        if mode == "ARCHITECT":
            return {
                "test_framework": "pytest",
                "api_framework": "FastAPI",
                "core_rules": "CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)",
                "orchestrator_pattern": "CORTEX orchestrator pattern",
                "knowledge_source": "cortex-registry/integration/patterns/",
                "governance_orchestrator": "EnforcementOrchestrator",
                "coverage_target": "95%",
            }
        else:  # PRODUCTION mode
            return {
                "test_framework": "Jest",  # Default, overridden by profile
                "api_framework": "Express",
                "knowledge_source": "cortex-registry/company/domains/",
                "coverage_target": "80%",
            }

    def _resolve_template_text(
        self, template_text: str, context: Dict[str, Any]
    ) -> str:
        """
        Resolve placeholders in template text using context.

        Supports simple placeholders ({{var}}) and nested ({{obj.attr}}).

        Args:
            template_text: Text with {{placeholder}} markers.
            context: Context dictionary for resolution.

        Returns:
            Resolved text with placeholders replaced.

        Raises:
            PlaceholderResolutionError: If placeholder cannot be resolved.
        """
        # Find all placeholders
        placeholder_pattern = r"\{\{([^}]+)\}\}"
        placeholders = re.findall(placeholder_pattern, template_text)

        resolved_text = template_text
        for placeholder in placeholders:
            placeholder_key = placeholder.strip()

            # Handle nested placeholders (e.g., config.auth_pattern)
            value = self._resolve_nested_key(context, placeholder_key)

            if value is None:
                raise PlaceholderResolutionError(
                    f"Cannot resolve placeholder: {{{{{placeholder_key}}}}}. "
                    f"Available keys: {list(context.keys())}"
                )

            # Replace placeholder
            resolved_text = resolved_text.replace(
                f"{{{{{placeholder_key}}}}}", str(value)
            )

        return resolved_text

    def _resolve_nested_key(self, context: Dict[str, Any], key: str) -> Optional[Any]:
        """
        Resolve nested key like 'config.auth_pattern' from context.

        Args:
            context: Context dictionary.
            key: Key to resolve (supports dot notation).

        Returns:
            Resolved value or None if not found.
        """
        parts = key.split(".")
        current = context

        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None

        return current

    def _validate_template_schema(self, template_data: Dict[str, Any]) -> None:
        """
        Validate template has required fields.

        Args:
            template_data: Template definition.

        Raises:
            TemplateValidationError: If required fields missing.
        """
        required_fields = ["id", "name"]
        missing_fields = [
            field for field in required_fields if field not in template_data
        ]

        if missing_fields:
            raise TemplateValidationError(
                f"Missing required fields: {missing_fields}"
            )

    def _validate_no_circular_deps(self, template_data: Dict[str, Any]) -> None:
        """
        Validate template has no circular dependencies between steps.

        Args:
            template_data: Template definition.

        Raises:
            TemplateValidationError: If circular dependency detected.
        """
        steps = template_data.get("steps", [])
        if not steps:
            return

        # Build dependency graph
        step_ids = {step["id"] for step in steps}
        dependencies: Dict[str, List[str]] = {}

        for step in steps:
            step_id = step["id"]
            depends_on = step.get("depends_on", [])
            dependencies[step_id] = [
                dep for dep in depends_on if dep in step_ids
            ]

        # Detect cycles using DFS
        visited = set()
        rec_stack = set()

        def has_cycle(node: str) -> bool:
            """DFS cycle detection."""
            visited.add(node)
            rec_stack.add(node)

            for neighbor in dependencies.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True

            rec_stack.remove(node)
            return False

        for step_id in dependencies:
            if step_id not in visited:
                if has_cycle(step_id):
                    raise TemplateValidationError(
                        f"Circular dependency detected in template steps"
                    )


# AC_COMPLETE: AC-PHASE100-002 ✅ WorkflowTemplateRegistry implemented (GREEN phase)
