"""
Workflow Templates — Phase 45 Stage 3.

Pre-defined workflow templates for common CORTEX operations.

AC_START: AC-PHASE45-S3-003
Phase: 45 | Stage: 3 | Priority: P0
Description: GREEN phase implementation for workflow templates
Requirements: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)

ENH-MCP-WORKFLOW-001 (2026-02-22): WorkflowTemplateManager now dynamically
scans cortex-registry/workflows/templates/**/*.yaml in addition to built-in
templates, resolving GAP-004 discovered during PB-STS-001 execution.
External YAML templates take lower precedence than built-ins; duplicate names
are skipped with a logged warning.
"""

import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

import yaml


logger = logging.getLogger(__name__)

# Canonical registry location for dynamic template discovery (ENH-MCP-WORKFLOW-001)
_REGISTRY_TEMPLATES_ROOT = Path(__file__).resolve().parents[4] / "cortex-registry" / "workflows" / "templates"


# =============================================================================
# TEMPLATE: Phase Execution
# =============================================================================
PHASE_EXECUTION_TEMPLATE = {
    "name": "phase-execution",
    "description": "Execute a CORTEX phase with TDD methodology",
    "variables": {
        "phase_number": "Phase number to execute",
        "phase_name": "Phase name",
        "stage_count": "Number of stages in phase",
    },
    "steps": [
        {
            "name": "Load Phase Specification",
            "action": "read_phase_spec",
            "params": {
                "phase_number": "{{phase_number}}",
            },
        },
        {
            "name": "Initialize Phase Context",
            "action": "init_context",
            "params": {
                "phase_name": "{{phase_name}}",
                "stage_count": "{{stage_count}}",
            },
        },
        {
            "name": "Execute All Stages",
            "action": "execute_stages",
            "params": {
                "stages": "{{stage_count}}",
            },
        },
        {
            "name": "Validate Phase Completion",
            "action": "validate_completion",
            "params": {
                "phase_number": "{{phase_number}}",
            },
        },
        {
            "name": "Update Registry",
            "action": "update_registry",
            "params": {
                "phase_number": "{{phase_number}}",
                "status": "completed",
            },
        },
    ],
}


# =============================================================================
# TEMPLATE: TDD Cycle
# =============================================================================
TDD_CYCLE_TEMPLATE = {
    "name": "tdd-cycle",
    "description": "Execute TDD cycle: RED → GREEN → REFACTOR",
    "variables": {
        "module_name": "Module being developed",
        "test_file": "Test file path",
        "impl_file": "Implementation file path",
    },
    "steps": [
        {
            "name": "RED: Write Failing Tests",
            "action": "write_tests",
            "params": {
                "test_file": "{{test_file}}",
                "module_name": "{{module_name}}",
            },
        },
        {
            "name": "RED: Run Tests (Expect Failures)",
            "action": "run_tests",
            "params": {
                "test_file": "{{test_file}}",
                "expect_failures": True,
            },
        },
        {
            "name": "GREEN: Implement Minimal Solution",
            "action": "implement_solution",
            "params": {
                "impl_file": "{{impl_file}}",
                "module_name": "{{module_name}}",
            },
        },
        {
            "name": "GREEN: Run Tests (Expect Success)",
            "action": "run_tests",
            "params": {
                "test_file": "{{test_file}}",
                "expect_failures": False,
            },
        },
        {
            "name": "REFACTOR: Optimize Implementation",
            "action": "refactor_code",
            "params": {
                "impl_file": "{{impl_file}}",
            },
        },
        {
            "name": "REFACTOR: Verify Tests Still Pass",
            "action": "run_tests",
            "params": {
                "test_file": "{{test_file}}",
                "expect_failures": False,
            },
        },
    ],
}


# =============================================================================
# TEMPLATE: Holistic Refactoring
# =============================================================================
REFACTOR_HOLISTIC_TEMPLATE = {
    "name": "refactor-holistic",
    "description": "Holistic refactoring with semantic analysis",
    "variables": {
        "target_files": "Files to refactor",
        "refactor_operation": "Refactoring operation (extract, rename, etc.)",
    },
    "steps": [
        {
            "name": "Analyze Code Structure",
            "action": "semantic_analyze",
            "params": {
                "target_files": "{{target_files}}",
            },
        },
        {
            "name": "Generate Refactoring Plan",
            "action": "generate_refactor_plan",
            "params": {
                "operation": "{{refactor_operation}}",
                "files": "{{target_files}}",
            },
        },
        {
            "name": "Execute Refactoring",
            "action": "execute_refactor",
            "params": {
                "plan": "{{refactor_plan}}",
            },
        },
        {
            "name": "Run Tests",
            "action": "run_tests",
            "params": {
                "all_tests": True,
            },
        },
        {
            "name": "Validate Semantics Preserved",
            "action": "validate_semantics",
            "params": {
                "original_files": "{{target_files}}",
            },
        },
    ],
}


# =============================================================================
# TEMPLATE MANAGER
# =============================================================================
class WorkflowTemplateManager:
    """Manages workflow templates.

    Provides access to pre-defined workflow templates for common operations.
    On first construction, scans ``cortex-registry/workflows/templates/**/*.yaml``
    to discover externally-authored templates (ENH-MCP-WORKFLOW-001 / GAP-004).
    Built-in templates always take precedence over registry YAML files.

    Example:
        >>> manager = WorkflowTemplateManager()
        >>> template = manager.get_template("tdd-cycle")
        >>> print(template["name"])
        tdd-cycle
        >>> # Dynamic templates discovered from the registry:
        >>> "security-hardening" in manager.list_templates()
        True
    """

    def __init__(self, registry_root: Optional[Path] = None) -> None:
        """Initialize template manager with built-ins and registry discovery.

        Args:
            registry_root: Override path for dynamic template discovery.
                           Defaults to ``cortex-registry/workflows/templates/``.
        """
        self._templates: Dict[str, Dict[str, Any]] = {
            "phase-execution": PHASE_EXECUTION_TEMPLATE,
            "tdd-cycle": TDD_CYCLE_TEMPLATE,
            "refactor-holistic": REFACTOR_HOLISTIC_TEMPLATE,
        }
        # Discover external templates from the registry (ENH-MCP-WORKFLOW-001)
        root = registry_root if registry_root is not None else _REGISTRY_TEMPLATES_ROOT
        self._load_registry_templates(root)

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _load_registry_templates(self, root: Path) -> None:
        """Scan ``root/**/*.yaml`` and register templates not already present.

        Built-in templates (defined as module-level constants) always win.
        External YAML files that fail to parse are skipped with a warning.

        Args:
            root: Directory root to scan recursively.
        """
        if not root.is_dir():
            logger.debug(
                "Workflow registry root does not exist — skipping dynamic discovery: %s", root
            )
            return

        discovered = 0
        skipped_builtin = 0
        skipped_invalid = 0

        for yaml_file in sorted(root.rglob("*.yaml")):
            try:
                raw = yaml_file.read_text(encoding="utf-8")
                data: Any = yaml.safe_load(raw)
            except Exception as exc:
                logger.warning("Failed to parse workflow template %s: %s", yaml_file, exc)
                skipped_invalid += 1
                continue

            if not isinstance(data, dict):
                logger.debug("Skipping non-dict YAML template: %s", yaml_file)
                skipped_invalid += 1
                continue

            # Support both top-level template dict and nested {template: {...}}
            template_data: Dict[str, Any] = data.get("template", data)
            name: Any = template_data.get("name") or yaml_file.stem

            if not isinstance(name, str):
                logger.warning("Template %s has invalid 'name' field — skipping", yaml_file)
                skipped_invalid += 1
                continue

            if name in self._templates:
                logger.debug(
                    "Registry template '%s' shadowed by built-in — skipping %s", name, yaml_file
                )
                skipped_builtin += 1
                continue

            self._templates[name] = template_data
            discovered += 1
            logger.debug("Discovered workflow template '%s' from %s", name, yaml_file)

        logger.info(
            "Workflow template discovery complete: %d discovered, %d skipped (built-in), "
            "%d skipped (invalid) from %s",
            discovered, skipped_builtin, skipped_invalid, root,
        )

    # ── Public API ────────────────────────────────────────────────────────────

    def get_template(self, name: str) -> Dict[str, Any]:
        """Get workflow template by name.

        Args:
            name: Template name.

        Returns:
            Template dictionary.

        Raises:
            KeyError: If template does not exist.
        """
        if name not in self._templates:
            available = sorted(self._templates.keys())
            raise KeyError(
                f"Template not found: '{name}'. Available templates: {available}"
            )

        logger.debug("Retrieved template: %s", name)
        return self._templates[name]

    def list_templates(self) -> List[str]:
        """List all available template names (built-in + discovered).

        Returns:
            Sorted list of template names.
        """
        return sorted(self._templates.keys())

    def register_template(self, name: str, template: Dict[str, Any]) -> None:
        """Register a custom workflow template at runtime.

        Args:
            name: Template name.
            template: Template dictionary.
        """
        self._templates[name] = template
        logger.info("Registered custom template: %s", name)


# =============================================================================
# AC_COMPLETE: AC-PHASE45-S3-003 (GREEN phase implementation)
# =============================================================================
