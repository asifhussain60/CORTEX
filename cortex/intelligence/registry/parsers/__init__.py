"""
Parser registry — maps schema types to dedicated parser classes.

Uses a decorator-based registration pattern:

    @register_parser("governance-rule")
    class GovernanceRuleParser:
        def parse(self, data: dict, source_file: str) -> GovernanceRuleModel:
            ...

Unrecognized types fall back to GenericParser automatically via
``get_parser_for_type()``.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional, Type

# Global parser registry: schema_type → parser_class
PARSER_REGISTRY: Dict[str, Type[Any]] = {}


def register_parser(schema_type: str) -> Callable:
    """Decorator that registers a parser class for a given schema type.

    Args:
        schema_type: The YAML schema type string (e.g. ``"governance-rule"``).

    Returns:
        A class decorator that adds the parser to ``PARSER_REGISTRY``.

    Raises:
        ValueError: If ``schema_type`` is already registered.

    Example::

        @register_parser("governance-rule")
        class GovernanceRuleParser:
            def parse(self, data, source_file):
                ...
    """

    def decorator(cls: Type[Any]) -> Type[Any]:
        if schema_type in PARSER_REGISTRY:
            raise ValueError(
                f"Parser for schema type '{schema_type}' is already registered "
                f"(existing: {PARSER_REGISTRY[schema_type].__name__}, "
                f"new: {cls.__name__})"
            )
        PARSER_REGISTRY[schema_type] = cls
        return cls

    return decorator


def get_parser_for_type(schema_type: str) -> Type[Any]:
    """Look up the parser class for a schema type, falling back to GenericParser.

    Args:
        schema_type: The YAML schema type to look up.

    Returns:
        The registered parser class, or ``GenericParser`` class
        if no dedicated parser is registered.
    """
    if schema_type in PARSER_REGISTRY:
        return PARSER_REGISTRY[schema_type]

    # Lazy import to avoid circular dependency
    from cortex.intelligence.registry.parsers.generic_parser import GenericParser

    return GenericParser


# --- Auto-register built-in parsers on import ---
# Import each parser module so its @register_parser decorator fires.
from cortex.intelligence.registry.parsers.generic_parser import GenericParser as _GenericParser  # noqa: E402, F811
from cortex.intelligence.registry.parsers.governance_parser import GovernanceRuleParser as _GovernanceRuleParser  # noqa: E402, F811
from cortex.intelligence.registry.parsers.workflow_parser import WorkflowTemplateParser as _WorkflowTemplateParser  # noqa: E402, F811
from cortex.intelligence.registry.parsers.pattern_parser import PatternParser as _PatternParser  # noqa: E402, F811
from cortex.intelligence.registry.parsers.plan_parser import PlanParser as _PlanParser  # noqa: E402, F811
from cortex.intelligence.registry.parsers.config_parser import ConfigParser as _ConfigParser  # noqa: E402, F811
from cortex.intelligence.registry.parsers.knowledge_parser import KnowledgeParser as _KnowledgeParser  # noqa: E402, F811
from cortex.intelligence.registry.parsers.template_parser import TemplateParser as _TemplateParser  # noqa: E402, F811
