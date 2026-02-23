"""
TemplateComposer — Dynamic Workflow Composition from Validated Primitives.

Composes new workflow templates by assembling pre-validated primitive building
blocks from cortex-registry/workflows/templates/primitives/. Composed templates
are validated, injected with convergence gates, and persisted to
cortex-registry/workflows/templates/composites/ for future reuse.

Key principle: COMPOSE from validated blocks, never GENERATE arbitrary YAML.
This eliminates hallucination risk while enabling dynamic coverage.

AC_START: AC-PHASE55-S2-001
Phase: 55 | Stage: 2 | Priority: P1
Description: GREEN phase — TemplateComposer implementation
Requirements: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

import hashlib
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# OPERATION → PRIMITIVE CATEGORY MAPPING
# ═══════════════════════════════════════════════════════════════════════════════

# Maps operation types to the ordered sequence of primitive categories needed.
# Every composed workflow follows: analysis → execution → validation.
OPERATION_CATEGORY_MAP: Dict[str, List[str]] = {
    "implement": ["analysis", "execution", "validation"],
    "fix": ["analysis", "execution", "validation"],
    "refactor": ["analysis", "execution", "validation"],
    "migrate": ["analysis", "execution", "validation"],
    "test": ["analysis", "validation"],
    "security": ["analysis", "validation"],
    "analyze": ["analysis"],
    "deploy": ["execution", "validation"],
    "document": ["analysis", "execution"],
}

# Default category sequence for unknown operation types
DEFAULT_CATEGORIES: List[str] = ["analysis", "execution", "validation"]


# ═══════════════════════════════════════════════════════════════════════════════
# PRIMITIVE SCANNER
# ═══════════════════════════════════════════════════════════════════════════════


class PrimitiveScanner:
    """Discovers available primitive templates from the registry directory.

    Scans cortex-registry/workflows/templates/primitives/ recursively for
    YAML files containing primitive workflow definitions. Only active
    primitives (status == 'active') are returned.

    Args:
        primitives_dir: Path to the primitives directory.

    Example:
        >>> scanner = PrimitiveScanner(Path("cortex-registry/workflows/templates/primitives"))
        >>> primitives = scanner.scan()
        >>> len(primitives)
        10
    """

    def __init__(self, primitives_dir: Path) -> None:
        """Initialize PrimitiveScanner.

        Args:
            primitives_dir: Path to the primitives directory to scan.
        """
        self._primitives_dir = primitives_dir

    def scan(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Discover all active primitives, optionally filtered by category.

        Args:
            category: Optional category filter (e.g., 'analysis', 'validation').

        Returns:
            List of primitive dictionaries loaded from YAML files.
        """
        if not self._primitives_dir.exists():
            logger.debug(
                "Primitives directory does not exist: %s", self._primitives_dir
            )
            return []

        primitives: List[Dict[str, Any]] = []

        for yaml_file in sorted(self._primitives_dir.rglob("*.yaml")):
            try:
                data = yaml.safe_load(yaml_file.read_text(encoding="utf-8"))
            except (yaml.YAMLError, OSError) as exc:
                logger.warning("Failed to parse primitive %s: %s", yaml_file, exc)
                continue

            if not isinstance(data, dict):
                continue

            # Skip non-primitive or inactive entries
            if data.get("status") != "active":
                continue

            # Apply category filter
            if category is not None and data.get("category") != category:
                continue

            primitives.append(data)

        logger.debug(
            "PrimitiveScanner discovered %d primitives from %s (filter=%s)",
            len(primitives),
            self._primitives_dir,
            category,
        )
        return primitives


# ═══════════════════════════════════════════════════════════════════════════════
# TEMPLATE COMPOSER
# ═══════════════════════════════════════════════════════════════════════════════


class TemplateComposer:
    """Assembles new workflow templates from validated primitive building blocks.

    When no pre-authored template matches the user's operation, TemplateComposer
    selects appropriate primitives based on operation type, assembles them into
    a sequenced workflow with convergence gates, and optionally persists the
    result to the composites directory for future reuse.

    Design invariants:
        - Only composes from existing, validated primitives (never generates YAML)
        - Every composed template includes a convergence gate
        - Analysis primitives always come first, validation primitives always last
        - Composed templates are persisted as standard YAML consumable by
          WorkflowTemplateRegistry

    Args:
        primitives_dir: Path to primitives directory.
        composites_dir: Optional path to composites output directory.

    Example:
        >>> composer = TemplateComposer(
        ...     primitives_dir=Path("cortex-registry/workflows/templates/primitives"),
        ...     composites_dir=Path("cortex-registry/workflows/templates/composites"),
        ... )
        >>> template = composer.compose(operation_type="refactor", description="Refactor auth")
        >>> template["id"]
        'composed/refactor-a1b2c3d4'
    """

    def __init__(
        self,
        primitives_dir: Path,
        composites_dir: Optional[Path] = None,
    ) -> None:
        """Initialize TemplateComposer.

        Args:
            primitives_dir: Path to the primitives directory.
            composites_dir: Optional path for persisting composed templates.
        """
        self._scanner = PrimitiveScanner(primitives_dir)
        self._composites_dir = composites_dir

    def compose(
        self,
        operation_type: str,
        description: str,
    ) -> Optional[Dict[str, Any]]:
        """Compose a workflow template from primitives for the given operation.

        Selects primitives matching the required categories for the operation
        type, assembles them into a sequenced workflow, and injects a
        convergence gate.

        Args:
            operation_type: Operation type (e.g., 'refactor', 'fix', 'implement').
            description: Human-readable description of the operation.

        Returns:
            Composed template dictionary, or None if no primitives available.
        """
        # Determine required categories for this operation
        categories = OPERATION_CATEGORY_MAP.get(
            operation_type.lower(), DEFAULT_CATEGORIES
        )

        # Scan for matching primitives
        all_primitives = self._scanner.scan()

        if not all_primitives:
            logger.info(
                "No primitives available for composition (operation=%s)",
                operation_type,
            )
            return None

        # Select best primitive for each required category
        steps: List[Dict[str, Any]] = []
        for cat in categories:
            cat_primitives = [p for p in all_primitives if p.get("category") == cat]
            if cat_primitives:
                # Select best-fit primitive for this category and operation type
                selected = self._select_best_primitive(cat_primitives, operation_type)
                # Primitives store steps under execution.steps (canonical schema).
                # Fall back to root-level steps for composed/test primitives.
                prim_steps = (
                    selected.get("execution", {}).get("steps", None)
                    or selected.get("steps", [])
                )
                for step in prim_steps:
                    enriched_step = dict(step)
                    enriched_step["source_category"] = cat
                    enriched_step["source_primitive"] = selected.get(
                        "template_id", "unknown"
                    )
                    steps.append(enriched_step)

        if not steps:
            logger.info(
                "No matching primitives for categories %s (operation=%s)",
                categories,
                operation_type,
            )
            return None

        # Generate unique ID from operation + description
        template_id = self._generate_id(operation_type, description)

        # Assemble composed template
        template: Dict[str, Any] = {
            "id": template_id,
            "template_id": template_id,
            "name": f"Composed: {operation_type} — {description[:60]}",
            "category": "composed",
            "tier": "composed",
            "status": "active",
            "source": "composer",
            "steps": steps,
            "convergence_gate": {
                "max_cycles": 5,
                "success_predicate": "all_steps_passed and validation_clean",
                "backoff_strategy": "linear",
            },
            "metadata": {
                "operation_type": operation_type,
                "description": description,
                "primitive_categories": categories,
                "composed": True,
            },
        }

        logger.info(
            "Composed template '%s' from %d primitives (%d steps)",
            template_id,
            len(categories),
            len(steps),
        )

        return template

    def persist(self, template: Dict[str, Any]) -> Optional[Path]:
        """Persist a composed template to the composites directory as YAML.

        Will not overwrite existing files with the same name.

        Args:
            template: Composed template dictionary to persist.

        Returns:
            Path to the persisted YAML file, or None if composites_dir not set
            or file already exists.
        """
        if self._composites_dir is None:
            logger.debug("No composites_dir set — skipping persistence")
            return None

        # Ensure directory exists
        self._composites_dir.mkdir(parents=True, exist_ok=True)

        # Derive filename from template ID
        template_id = template.get("id", "unknown")
        safe_name = template_id.replace("/", "-").replace(" ", "-")
        file_path = self._composites_dir / f"{safe_name}.yaml"

        # Do not overwrite existing
        if file_path.exists():
            logger.debug(
                "Composed template already exists at %s — skipping", file_path
            )
            return None

        # Write YAML
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(template, f, default_flow_style=False, sort_keys=False)

        logger.info("Persisted composed template to %s", file_path)
        return file_path

    def _select_best_primitive(
        self,
        candidates: List[Dict[str, Any]],
        operation_type: str,
    ) -> Dict[str, Any]:
        """Select the most relevant primitive from a list of category matches.

        Scoring heuristic (higher = better fit):
        - +2  primitive name or template_id contains the operation type keyword
        - +1  primitive tags contain the operation type keyword
        - +1  primitive tags contain an op-aligned keyword synonym
              (e.g., tag "refactoring" scores for op "refactor")
        - -1  primitive name contains a keyword from an unrelated domain
              (e.g., "css" or "dom" when operation is "refactor")
        - -1  primitive tags contain a keyword from an unrelated domain

        Falls back to the first candidate when all scores are equal.

        Args:
            candidates: Non-empty list of primitive dicts for the same category.
            operation_type: The current operation type (e.g., 'refactor').

        Returns:
            The best-fit primitive dictionary.
        """
        # Keywords that indicate a primitive is unrelated to this operation type.
        _UNRELATED_KEYWORDS: Dict[str, List[str]] = {
            "refactor": ["css", "dom", "html", "css-selector", "zero-inline"],
            "fix": ["css", "dom", "css-selector", "zero-inline"],
            "implement": ["css", "dom", "css-selector"],
            "security": ["ast"],
            "test": [],
            "analyze": ["css", "dom"],
        }
        # Tag synonyms that align with an operation type even if the op word
        # is not literally present in the tag string.
        _OP_SYNONYMS: Dict[str, List[str]] = {
            "refactor": ["refactoring", "restructure", "reorganise", "reorganize"],
            "fix": ["bugfix", "repair", "remediation"],
            "implement": ["implementation", "build", "create"],
            "test": ["testing", "regression", "validation"],
            "security": ["vulnerability", "threat", "audit"],
            "analyze": ["analysis", "inspection", "scan"],
            "deploy": ["deployment", "release", "publish"],
        }

        op = operation_type.lower()
        noise = _UNRELATED_KEYWORDS.get(op, [])
        synonyms = _OP_SYNONYMS.get(op, [])

        def _score(primitive: Dict[str, Any]) -> int:
            name = (primitive.get("name") or primitive.get("template_id") or "").lower()
            tags: List[str] = [t.lower() for t in primitive.get("metadata", {}).get("tags", [])]
            score = 0
            # Name match
            if op in name:
                score += 2
            # Tag exact match
            if any(op in tag for tag in tags):
                score += 1
            # Tag synonym match
            if any(syn in tag for syn in synonyms for tag in tags):
                score += 1
            # Name noise penalty
            for kw in noise:
                if kw in name:
                    score -= 1
            # Tag noise penalty
            for kw in noise:
                if any(kw in tag for tag in tags):
                    score -= 1
            return score

        return max(candidates, key=_score)

    def _generate_id(self, operation_type: str, description: str) -> str:
        """Generate a unique template ID from operation type and description.

        Args:
            operation_type: Operation type string.
            description: Description string.

        Returns:
            Unique template ID string in format 'composed/{op}-{hash}'.
        """
        content = f"{operation_type}:{description}"
        short_hash = hashlib.sha256(content.encode()).hexdigest()[:8]
        return f"composed/{operation_type.lower()}-{short_hash}"


# AC_COMPLETE: AC-PHASE55-S2-001 ✅ TemplateComposer implemented (GREEN phase)
