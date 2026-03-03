"""
WorkflowTemplateMixin — Template consumption capability for all orchestrators.

Adds discover/load/get_recommended_template methods to any class that inherits it.
OrchestratorBase inherits this mixin, giving all 22 wired orchestrators the ability
to consume workflow templates from cortex-registry/workflows/templates/.

Override Precedence:
    company/workflows/templates/ > cortex-registry/workflows/templates/

Phase: 23 — Workflow Template Injection
Authority: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings), CORE-035 (single canonical)
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

import yaml

if TYPE_CHECKING:
    from cortex.orchestrators.workflow.template_registry import (  # CORE-035  # interface pattern — registry in L3
        WorkflowTemplateRegistry,
    )


class WorkflowTemplateMixin:
    """
    Mixin that adds workflow template consumption capability to orchestrators.

    Provides methods to discover, load, and resolve workflow templates from
    the cortex-registry and company override directories. All 22 wired
    orchestrators inherit this via OrchestratorBase.

    The mixin does NOT change orchestrator execution logic. Orchestrators
    remain the HOW (execution). Templates remain the WHAT and WHEN (sequencing).
    This mixin is the BRIDGE.

    Usage:
        class MyOrchestrator(OrchestratorBase):
            def get_recommended_template(self) -> Optional[str]:
                return "tdd/tdd-feature-implementation"
    """

    # ══════════════════════════════════════════════════════════════════════════
    # TEMPLATE-ORCHESTRATOR MAPPING — Which templates serve which orchestrators
    # ══════════════════════════════════════════════════════════════════════════
    TEMPLATE_ORCHESTRATOR_MAP: Dict[str, str] = {
        "TDDOrchestrator": "tdd/tdd-workflow",
        "RefactoringOrchestrator": "quality/refactor-workflow",
        "EnforcementOrchestrator": "security/security-compliance-audit",
        "MasterPlanOrchestrator": "lifecycle/master-plan-execution",
        "CortexMasterPlanOrchestrator": "lifecycle/master-plan-execution",
        "MasterOrchestrator": "lifecycle/composite-execution-pipeline",
        "AuditCoordinator": "audit/audit-fix-pipeline",
        "PlanningOrchestrator": "lifecycle/master-plan-execution",
        "EnhancedPlanningOrchestrator": "lifecycle/master-plan-execution",
        "InteractionOrchestrator": "lifecycle/onboarding-workflow",
        "SecurityOrchestrator": "security/security-hardening",
        "DebuggerOrchestrator": "debugging/multi-stack-debug-pipeline",
        # Phase 90 additions — HealthOrchestrator + VacuumOrchestrator
        "HealthOrchestrator": "maintenance/health-check-workflow",
        "VacuumOrchestrator": "maintenance/vacuum-workflow",
    }

    _registry: Optional["WorkflowTemplateRegistry"] = None
    _registry_loaded: bool = False

    def _ensure_registry_loaded(self) -> None:
        """
        Lazily initialize and load the template registry from YAML files.

        Scans cortex-registry/workflows/templates/ for YAML workflow definitions
        and registers them in the WorkflowTemplateRegistry singleton.
        """
        if self._registry_loaded and self._registry is not None:
            return

        from cortex.orchestrators.workflow.template_registry import WorkflowTemplateRegistry  # LAZY: template registry in L3; lazy import breaks L1→L3 DAG violation
        self._registry = WorkflowTemplateRegistry()
        templates_dir = self._find_templates_dir()

        if templates_dir and templates_dir.exists():
            self._load_templates_from_dir(templates_dir, source="cortex")

        # Load company overrides (higher precedence)
        company_dir = self._find_company_templates_dir()
        if company_dir and company_dir.exists():
            self._load_templates_from_dir(company_dir, source="company")

        self._registry_loaded = True

    def _find_templates_dir(self) -> Optional[Path]:
        """
        Locate the cortex-registry/workflows/templates/ directory.

        Returns:
            Path to templates directory, or None if not found.
        """
        # Try relative to CWD first
        candidates = [
            Path("cortex-registry/workflows/templates"),
            Path(__file__).parent.parent.parent / "cortex-registry" / "workflows" / "templates",
        ]

        for candidate in candidates:
            if candidate.exists():
                return candidate

        return None

    def _find_company_templates_dir(self) -> Optional[Path]:
        """
        Locate the company/workflows/ directory for template overrides.

        Returns:
            Path to company workflows directory, or None if not found.
        """
        candidates = [
            Path("cortex-registry/company/workflows"),
            Path(__file__).parent.parent.parent / "cortex-registry" / "company" / "workflows",
        ]

        for candidate in candidates:
            if candidate.exists():
                return candidate

        return None

    def _load_templates_from_dir(self, templates_dir: Path, source: str = "cortex") -> None:
        """
        Recursively load YAML workflow templates from a directory.

        Args:
            templates_dir: Root directory containing template YAML files.
            source: Template source identifier ('cortex' or 'company').
        """
        if self._registry is None:
            return

        for yaml_file in templates_dir.rglob("*.yaml"):
            try:
                with open(yaml_file, "r") as f:
                    data = yaml.safe_load(f)

                if not data:
                    continue

                # Extract workflow definition (may be nested under 'workflow' key)
                workflow_data = data.get("workflow", data)

                # Skip files without required template fields
                if "id" not in workflow_data and "name" not in workflow_data:
                    continue

                # Derive ID from file path if not in YAML
                if "id" not in workflow_data:
                    relative = yaml_file.relative_to(templates_dir)
                    workflow_data["id"] = str(relative.with_suffix("")).replace("\\", "/")

                if "name" not in workflow_data:
                    workflow_data["name"] = workflow_data["id"].replace("/", " ").replace("-", " ").title()

                # Derive category from directory structure
                if "category" not in workflow_data:
                    relative = yaml_file.relative_to(templates_dir)
                    parts = relative.parts
                    workflow_data["category"] = parts[0] if len(parts) > 1 else "general"

                workflow_data["source"] = source

                # Normalize step_id → id in steps for registry compatibility
                steps = workflow_data.get("steps", [])
                for step in steps:
                    if isinstance(step, dict) and "step_id" in step and "id" not in step:
                        step["id"] = step["step_id"]

                # Company templates override existing
                override = source == "company"
                self._registry.register_template(workflow_data, override=override)

            except (yaml.YAMLError, OSError, KeyError):
                continue  # Skip malformed files silently

    def discover_templates(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List available workflow templates, optionally filtered by category.

        Args:
            category: Optional category filter (e.g., 'tdd', 'security', 'lifecycle').

        Returns:
            List of template summary dicts with id, name, category, source keys.
        """
        self._ensure_registry_loaded()
        if self._registry is None:
            return []
        return self._registry.list_templates(category=category)

    def load_template(self, template_id: str) -> Dict[str, Any]:
        """
        Load a specific workflow template by ID with placeholder resolution.

        Args:
            template_id: Template identifier (e.g., 'tdd/tdd-feature-implementation').

        Returns:
            Resolved template dictionary with id, name, category, steps, etc.

        Raises:
            TemplateNotFoundError: If template not found in registry.
        """
        self._ensure_registry_loaded()
        if self._registry is None:
            from cortex.orchestrators.workflow.template_registry import TemplateNotFoundError  # LAZY: exception in L3
            raise TemplateNotFoundError(
                f"Template registry not initialized. Cannot load: {template_id}"
            )
        return self._registry.get_template(template_id)

    def get_recommended_template(self) -> Optional[str]:
        """
        Get the recommended workflow template ID for this orchestrator.

        Base implementation returns None. Subclasses override to return
        their domain-specific template ID.

        Returns:
            Template ID string, or None if no template is recommended.
        """
        return None

    def discover_company_templates(self) -> List[Dict[str, Any]]:
        """
        List workflow templates from the company override directory.

        Company templates in company/workflows/ take precedence over
        cortex-registry/workflows/templates/ templates.

        Returns:
            List of company template summary dicts.
        """
        self._ensure_registry_loaded()
        if self._registry is None:
            return []

        all_templates = self._registry.list_templates()
        return [t for t in all_templates if t.get("source") == "company"]
