"""
Golden Tests — Phase 90: HealthOrchestrator + VacuumOrchestrator Gateway Wiring

GHV-001 .. GHV-016: Regression guard confirming both orchestrators are correctly
wired to the Phase 90 WorkflowGateway infrastructure.

Coverage clusters:
  A: Inheritance — both orchestrators carry WorkflowEnforcementMixin + WorkflowTemplateMixin (GHV-001..GHV-004)
  B: TEMPLATE_ORCHESTRATOR_MAP entries (GHV-005..GHV-008)
  C: get_recommended_template() returns correct IDs (GHV-009..GHV-010)
  D: WorkflowGateway._MODE_TEMPLATE_MAP consistency with orchestrator IDs (GHV-011..GHV-012)
  E: Template YAML files exist on disk (GHV-013..GHV-014)
  F: Opt-in gateway routing integration (GHV-015..GHV-016)

Phase: 90 | Priority: P0
Authority: CORE-008, CORE-055 (golden test tier), CORE-064
AC_START: AC-P90-GOLDEN-HV-001
"""
# ruff: noqa: S101
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Type

import pytest

ROOT = Path(__file__).parents[4]
TEMPLATES_ROOT = ROOT / "cortex-registry" / "workflows" / "templates"


# ─────────────────────────────────────────────────────────────────────────────
# Cluster A: Inheritance contract
# ─────────────────────────────────────────────────────────────────────────────

class TestHealthOrchestratorInheritance:
    """GHV-001..GHV-002: HealthOrchestrator carries both Phase 90 mixins."""

    @pytest.fixture
    def health_class(self) -> Type:
        from cortex.orchestrators.health.health_orchestrator import HealthOrchestrator
        return HealthOrchestrator

    def test_health_orchestrator_inherits_enforcement_mixin(self, health_class: Type) -> None:
        """GHV-001: HealthOrchestrator is a WorkflowEnforcementMixin subclass."""
        from cortex.core.workflow_enforcement_mixin import WorkflowEnforcementMixin
        assert issubclass(health_class, WorkflowEnforcementMixin), (
            "HealthOrchestrator must inherit WorkflowEnforcementMixin (Phase 90 wiring)"
        )

    def test_health_orchestrator_inherits_template_mixin(self, health_class: Type) -> None:
        """GHV-002: HealthOrchestrator is a WorkflowTemplateMixin subclass."""
        from cortex.core.workflow_template_mixin import WorkflowTemplateMixin
        assert issubclass(health_class, WorkflowTemplateMixin), (
            "HealthOrchestrator must inherit WorkflowTemplateMixin (Phase 90 wiring)"
        )


class TestVacuumOrchestratorInheritance:
    """GHV-003..GHV-004: VacuumOrchestrator carries both Phase 90 mixins."""

    @pytest.fixture
    def vacuum_class(self) -> Type:
        from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator
        return VacuumOrchestrator

    def test_vacuum_orchestrator_inherits_enforcement_mixin(self, vacuum_class: Type) -> None:
        """GHV-003: VacuumOrchestrator is a WorkflowEnforcementMixin subclass."""
        from cortex.core.workflow_enforcement_mixin import WorkflowEnforcementMixin
        assert issubclass(vacuum_class, WorkflowEnforcementMixin), (
            "VacuumOrchestrator must inherit WorkflowEnforcementMixin (Phase 90 wiring)"
        )

    def test_vacuum_orchestrator_inherits_template_mixin(self, vacuum_class: Type) -> None:
        """GHV-004: VacuumOrchestrator is a WorkflowTemplateMixin subclass."""
        from cortex.core.workflow_template_mixin import WorkflowTemplateMixin
        assert issubclass(vacuum_class, WorkflowTemplateMixin), (
            "VacuumOrchestrator must inherit WorkflowTemplateMixin (Phase 90 wiring)"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Cluster B: TEMPLATE_ORCHESTRATOR_MAP entries
# ─────────────────────────────────────────────────────────────────────────────

class TestTemplateOrchestratorMapEntries:
    """GHV-005..GHV-008: TEMPLATE_ORCHESTRATOR_MAP contains correct entries for both orchestrators."""

    @pytest.fixture
    def template_map(self) -> Dict[str, str]:
        from cortex.core.workflow_template_mixin import WorkflowTemplateMixin
        return WorkflowTemplateMixin.TEMPLATE_ORCHESTRATOR_MAP

    def test_health_orchestrator_in_map(self, template_map: Dict) -> None:
        """GHV-005: TEMPLATE_ORCHESTRATOR_MAP contains 'HealthOrchestrator' key."""
        assert "HealthOrchestrator" in template_map, (
            "HealthOrchestrator not in TEMPLATE_ORCHESTRATOR_MAP — Phase 90 wiring incomplete"
        )

    def test_vacuum_orchestrator_in_map(self, template_map: Dict) -> None:
        """GHV-006: TEMPLATE_ORCHESTRATOR_MAP contains 'VacuumOrchestrator' key."""
        assert "VacuumOrchestrator" in template_map, (
            "VacuumOrchestrator not in TEMPLATE_ORCHESTRATOR_MAP — Phase 90 wiring incomplete"
        )

    def test_health_orchestrator_maps_to_correct_template(self, template_map: Dict) -> None:
        """GHV-007: HealthOrchestrator → 'maintenance/health-check-workflow'."""
        actual = template_map.get("HealthOrchestrator", "")
        assert actual == "maintenance/health-check-workflow", (
            f"HealthOrchestrator maps to {actual!r}, expected 'maintenance/health-check-workflow'"
        )

    def test_vacuum_orchestrator_maps_to_correct_template(self, template_map: Dict) -> None:
        """GHV-008: VacuumOrchestrator → 'maintenance/vacuum-workflow'."""
        actual = template_map.get("VacuumOrchestrator", "")
        assert actual == "maintenance/vacuum-workflow", (
            f"VacuumOrchestrator maps to {actual!r}, expected 'maintenance/vacuum-workflow'"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Cluster C: get_recommended_template() contract
# ─────────────────────────────────────────────────────────────────────────────

class TestGetRecommendedTemplate:
    """GHV-009..GHV-010: get_recommended_template() returns exact canonical template IDs."""

    def test_health_orchestrator_recommended_template(self, tmp_path: Path) -> None:
        """GHV-009: HealthOrchestrator.get_recommended_template() == 'maintenance/health-check-workflow'."""
        from cortex.orchestrators.health.health_orchestrator import HealthOrchestrator
        orch = HealthOrchestrator(tmp_path)
        result = orch.get_recommended_template()
        assert result == "maintenance/health-check-workflow", (
            f"HealthOrchestrator.get_recommended_template() returned {result!r}"
        )

    def test_vacuum_orchestrator_recommended_template(self, tmp_path: Path) -> None:
        """GHV-010: VacuumOrchestrator.get_recommended_template() == 'maintenance/vacuum-workflow'."""
        from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator
        orch = VacuumOrchestrator(tmp_path)
        result = orch.get_recommended_template()
        assert result == "maintenance/vacuum-workflow", (
            f"VacuumOrchestrator.get_recommended_template() returned {result!r}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Cluster D: WorkflowGateway._MODE_TEMPLATE_MAP consistency
# ─────────────────────────────────────────────────────────────────────────────

class TestGatewayModeMapConsistency:
    """GHV-011..GHV-012: _MODE_TEMPLATE_MAP agrees with get_recommended_template()."""

    def test_gateway_health_mode_matches_orchestrator_template(self, tmp_path: Path) -> None:
        """GHV-011: Gateway HEALTH template ID matches HealthOrchestrator.get_recommended_template()."""
        from cortex.orchestrators.health.health_orchestrator import HealthOrchestrator
        from cortex.orchestrators.workflow.workflow_gateway import _MODE_TEMPLATE_MAP

        orch = HealthOrchestrator(tmp_path)
        gateway_template = _MODE_TEMPLATE_MAP["HEALTH"]
        orchestrator_template = orch.get_recommended_template()
        assert gateway_template == orchestrator_template, (
            f"Gateway HEALTH={gateway_template!r} != "
            f"HealthOrchestrator.get_recommended_template()={orchestrator_template!r}"
        )

    def test_gateway_vacuum_mode_matches_orchestrator_template(self, tmp_path: Path) -> None:
        """GHV-012: Gateway VACUUM template ID matches VacuumOrchestrator.get_recommended_template()."""
        from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator
        from cortex.orchestrators.workflow.workflow_gateway import _MODE_TEMPLATE_MAP

        orch = VacuumOrchestrator(tmp_path)
        gateway_template = _MODE_TEMPLATE_MAP["VACUUM"]
        orchestrator_template = orch.get_recommended_template()
        assert gateway_template == orchestrator_template, (
            f"Gateway VACUUM={gateway_template!r} != "
            f"VacuumOrchestrator.get_recommended_template()={orchestrator_template!r}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Cluster E: Template YAML files exist on disk
# ─────────────────────────────────────────────────────────────────────────────

class TestMaintenanceTemplatesExist:
    """GHV-013..GHV-014: Template YAML files referenced by both orchestrators exist."""

    def test_health_check_workflow_yaml_exists(self) -> None:
        """GHV-013: maintenance/health-check-workflow.yaml exists on disk."""
        path = TEMPLATES_ROOT / "maintenance" / "health-check-workflow.yaml"
        assert path.exists(), (
            "maintenance/health-check-workflow.yaml not found — "
            "HealthOrchestrator has no executable template"
        )

    def test_vacuum_workflow_yaml_exists(self) -> None:
        """GHV-014: maintenance/vacuum-workflow.yaml exists on disk."""
        path = TEMPLATES_ROOT / "maintenance" / "vacuum-workflow.yaml"
        assert path.exists(), (
            "maintenance/vacuum-workflow.yaml not found — "
            "VacuumOrchestrator has no executable template"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Cluster F: Opt-in gateway routing integration
# ─────────────────────────────────────────────────────────────────────────────

class TestHealthVacuumGatewayIntegration:
    """GHV-015..GHV-016: Both orchestrators can opt-in to gateway routing."""

    def test_health_orchestrator_gateway_enabled_is_true(self, tmp_path: Path) -> None:
        """GHV-015: HealthOrchestrator.PHASE90_GATEWAY_ENABLED is True (opted-in)."""
        from cortex.orchestrators.health.health_orchestrator import HealthOrchestrator
        assert HealthOrchestrator.PHASE90_GATEWAY_ENABLED is True, (
            "HealthOrchestrator.PHASE90_GATEWAY_ENABLED must be True — "
            "this orchestrator is the Phase 90 gateway opt-in pilot"
        )

    def test_vacuum_orchestrator_gateway_enabled_is_true(self, tmp_path: Path) -> None:
        """GHV-016: VacuumOrchestrator.PHASE90_GATEWAY_ENABLED is True (opted-in)."""
        from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator
        assert VacuumOrchestrator.PHASE90_GATEWAY_ENABLED is True, (
            "VacuumOrchestrator.PHASE90_GATEWAY_ENABLED must be True — "
            "this orchestrator is the Phase 90 gateway opt-in pilot"
        )


# AC_COMPLETE: AC-P90-GOLDEN-HV-001 ✅ Health + Vacuum Phase 90 golden tests
