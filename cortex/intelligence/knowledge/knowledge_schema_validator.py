"""KnowledgeSchemaValidator — enforces a 5-rule schema on knowledge YAML content.

Validates synthesized or hand-authored knowledge YAML strings before they are
persisted to ``cortex-registry/knowledge/``.

Five validation rules:
  1. Content must be parseable YAML (no syntax errors).
  2. Top-level ``title`` key must be present and non-empty.
  3. Top-level ``domain`` key must be present and non-empty.
  4. ``best_practices`` must be a list.
  5. ``best_practices`` must contain at least 3 items.

Phase: 135-b (GAP-135-03)
CORE: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings),
      CORE-035 (single canonical implementation)
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import yaml

logger = logging.getLogger(__name__)


@dataclass
class SchemaValidationResult:
    """Result of a knowledge YAML schema validation pass.

    Attributes:
        is_valid: True when all 5 rules pass.
        errors: Human-readable error messages for failed rules.
        parsed: The parsed YAML dict (``None`` when YAML is unparseable).
    """

    is_valid: bool
    errors: List[str] = field(default_factory=list)
    parsed: Optional[Dict[str, Any]] = None


class KnowledgeSchemaValidator:
    """Enforces the 5-rule CORTEX knowledge YAML schema.

    Usage::

        validator = KnowledgeSchemaValidator()
        result = validator.validate(yaml_string)
        if not result.is_valid:
            for error in result.errors:
                logger.warning("Schema violation: %s", error)
    """

    _MIN_BEST_PRACTICES: int = 3

    def validate(self, yaml_content: str) -> SchemaValidationResult:
        """Validate *yaml_content* against the 5-rule knowledge schema.

        Args:
            yaml_content: Raw YAML string (output of ``KnowledgeTemplateSynthesizer``
                or hand-authored knowledge file).

        Returns:
            :class:`SchemaValidationResult` with ``is_valid``, ``errors``, and ``parsed``.
        """
        errors: List[str] = []

        # Rule 1: parseable YAML
        try:
            parsed: Any = yaml.safe_load(yaml_content)
        except yaml.YAMLError as exc:
            return SchemaValidationResult(
                is_valid=False,
                errors=[f"Rule 1 — YAML syntax error: {exc}"],
                parsed=None,
            )

        if not isinstance(parsed, dict):
            return SchemaValidationResult(
                is_valid=False,
                errors=["Rule 1 — Top-level structure must be a YAML mapping (dict)"],
                parsed=None,
            )

        # Rule 2: title present and non-empty
        title = parsed.get("title", "")
        if not title or not str(title).strip():
            errors.append("Rule 2 — title required: 'title' key must be present and non-empty")

        # Rule 3: domain present and non-empty
        domain = parsed.get("domain", "")
        if not domain or not str(domain).strip():
            errors.append("Rule 3 — domain required: 'domain' key must be present and non-empty")

        # Rule 4: best_practices must be a list
        bp = parsed.get("best_practices")
        if not isinstance(bp, list):
            errors.append(
                "Rule 4 — best_practices must be a list, "
                f"got {type(bp).__name__ if bp is not None else 'missing'}"
            )
        else:
            # Rule 5: best_practices must have >= 3 items
            if len(bp) < self._MIN_BEST_PRACTICES:
                errors.append(
                    f"Rule 5 — best_practices must have at least {self._MIN_BEST_PRACTICES} items, "
                    f"got {len(bp)}"
                )

        return SchemaValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            parsed=parsed if len(errors) == 0 else None,
        )
