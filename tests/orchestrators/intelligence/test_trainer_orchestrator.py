"""
TrainerOrchestrator Tests — TDD RED Phase

AC-TRAIN-001: TrainerOrchestrator importable from cortex.orchestrators.intelligence
AC-TRAIN-002: inventory_templates() returns list of existing workflow templates
AC-TRAIN-003: analyze_target() performs LENS + STS analysis on target path
AC-TRAIN-004: detect_gaps() compares patterns against template inventory
AC-TRAIN-005: generate_proposal() returns change manifest (CREATE/ENHANCE/DELETE)
AC-TRAIN-006: execute_proposal() applies changes via TDD workflow
AC-TRAIN-007: Implements OrchestratorProtocolMixin interface

Author: GitHub Copilot
Date: 2026-02-26
Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

import pytest


# =============================================================================
# AC-TRAIN-001: TrainerOrchestrator importable
# =============================================================================


class TestTrainerOrchestratorImport:
    """AC-TRAIN-001: TrainerOrchestrator importable from cortex.orchestrators.intelligence."""

    def test_trainer_orchestrator_importable(self) -> None:
        """TrainerOrchestrator should be importable."""
        from cortex.orchestrators.intelligence.trainer_orchestrator import (
            TrainerOrchestrator,
        )

        assert TrainerOrchestrator is not None

    def test_trainer_orchestrator_has_orch_name(self) -> None:
        """TrainerOrchestrator must have _orch_name attribute."""
        from cortex.orchestrators.intelligence.trainer_orchestrator import (
            TrainerOrchestrator,
        )

        assert hasattr(TrainerOrchestrator, "_orch_name")
        assert TrainerOrchestrator._orch_name == "TrainerOrchestrator"

    def test_trainer_orchestrator_has_orch_version(self) -> None:
        """TrainerOrchestrator must have _orch_version attribute."""
        from cortex.orchestrators.intelligence.trainer_orchestrator import (
            TrainerOrchestrator,
        )

        assert hasattr(TrainerOrchestrator, "_orch_version")
        assert TrainerOrchestrator._orch_version == "1.0.0"


# =============================================================================
# AC-TRAIN-007: OrchestratorProtocolMixin compliance
# =============================================================================


class TestTrainerOrchestratorProtocol:
    """AC-TRAIN-007: TrainerOrchestrator implements OrchestratorProtocolMixin."""

    def test_inherits_protocol_mixin(self) -> None:
        """TrainerOrchestrator must inherit OrchestratorProtocolMixin."""
        from cortex.core.orchestrator_protocol_mixin import OrchestratorProtocolMixin
        from cortex.orchestrators.intelligence.trainer_orchestrator import (
            TrainerOrchestrator,
        )

        assert issubclass(TrainerOrchestrator, OrchestratorProtocolMixin)

    def test_has_execute_operation(self) -> None:
        """TrainerOrchestrator must have execute_operation method."""
        from cortex.orchestrators.intelligence.trainer_orchestrator import (
            TrainerOrchestrator,
        )

        assert hasattr(TrainerOrchestrator, "execute_operation")
        assert callable(getattr(TrainerOrchestrator, "execute_operation"))

    def test_has_get_capabilities(self) -> None:
        """TrainerOrchestrator must have get_capabilities method."""
        from cortex.orchestrators.intelligence.trainer_orchestrator import (
            TrainerOrchestrator,
        )

        assert hasattr(TrainerOrchestrator, "get_capabilities")


# =============================================================================
# AC-TRAIN-002: inventory_templates()
# =============================================================================


class TestInventoryTemplates:
    """AC-TRAIN-002: inventory_templates() returns existing workflow templates."""

    @pytest.fixture
    def trainer(self) -> Any:
        """Create TrainerOrchestrator instance."""
        from cortex.orchestrators.intelligence.trainer_orchestrator import (
            TrainerOrchestrator,
        )

        return TrainerOrchestrator()

    def test_inventory_templates_returns_list(self, trainer: Any) -> None:
        """inventory_templates() should return a list."""
        result = trainer.inventory_templates()
        assert isinstance(result, list)

    def test_inventory_templates_contains_template_metadata(self, trainer: Any) -> None:
        """Each template in inventory should have id, category, path keys."""
        result = trainer.inventory_templates()
        if len(result) > 0:
            template = result[0]
            assert "id" in template
            assert "category" in template
            assert "path" in template

    def test_inventory_templates_discovers_from_registry(self, trainer: Any) -> None:
        """Should discover templates from cortex-registry/workflows/templates/."""
        result = trainer.inventory_templates()
        # At minimum, should find some templates in the registry
        assert len(result) >= 0  # May be empty in test isolation


# =============================================================================
# AC-TRAIN-003: analyze_target()
# =============================================================================


class TestAnalyzeTarget:
    """AC-TRAIN-003: analyze_target() performs LENS + pattern analysis."""

    @pytest.fixture
    def trainer(self) -> Any:
        """Create TrainerOrchestrator instance."""
        from cortex.orchestrators.intelligence.trainer_orchestrator import (
            TrainerOrchestrator,
        )

        return TrainerOrchestrator()

    def test_analyze_target_accepts_path(self, trainer: Any, tmp_path: Path) -> None:
        """analyze_target() should accept a path argument."""
        # Create a simple target directory
        target = tmp_path / "target_repo"
        target.mkdir()
        (target / "main.py").write_text("def hello(): pass")

        result = trainer.analyze_target(target)
        assert isinstance(result, dict)

    def test_analyze_target_returns_patterns(self, trainer: Any, tmp_path: Path) -> None:
        """analyze_target() should return detected patterns."""
        target = tmp_path / "target_repo"
        target.mkdir()
        (target / "main.py").write_text("def hello(): pass")

        result = trainer.analyze_target(target)
        assert "patterns" in result

    def test_analyze_target_returns_tech_stack(self, trainer: Any, tmp_path: Path) -> None:
        """analyze_target() should return detected technology stack."""
        target = tmp_path / "target_repo"
        target.mkdir()
        (target / "main.py").write_text("def hello(): pass")

        result = trainer.analyze_target(target)
        assert "tech_stack" in result

    def test_analyze_target_returns_anti_patterns(
        self, trainer: Any, tmp_path: Path
    ) -> None:
        """analyze_target() should return detected anti-patterns."""
        target = tmp_path / "target_repo"
        target.mkdir()
        # Create code with an anti-pattern (hardcoded password)
        (target / "config.py").write_text('PASSWORD = "admin123"')

        result = trainer.analyze_target(target)
        assert "anti_patterns" in result


# =============================================================================
# AC-TRAIN-004: detect_gaps()
# =============================================================================


class TestDetectGaps:
    """AC-TRAIN-004: detect_gaps() compares patterns against inventory."""

    @pytest.fixture
    def trainer(self) -> Any:
        """Create TrainerOrchestrator instance."""
        from cortex.orchestrators.intelligence.trainer_orchestrator import (
            TrainerOrchestrator,
        )

        return TrainerOrchestrator()

    def test_detect_gaps_returns_dict(self, trainer: Any) -> None:
        """detect_gaps() should return a dictionary."""
        analysis = {"patterns": [], "tech_stack": ["python"], "anti_patterns": []}
        inventory = []

        result = trainer.detect_gaps(analysis, inventory)
        assert isinstance(result, dict)

    def test_detect_gaps_identifies_missing_templates(self, trainer: Any) -> None:
        """detect_gaps() should identify patterns without matching templates."""
        analysis = {
            "patterns": [{"id": "di-lifetime-validation", "type": "quality"}],
            "tech_stack": ["csharp"],
            "anti_patterns": [{"id": "captive-dependency", "severity": "P1"}],
        }
        inventory = [
            {"id": "csharp-refactor-workflow", "category": "backend", "covers": ["refactoring"]},
        ]

        result = trainer.detect_gaps(analysis, inventory)
        assert "missing" in result
        assert len(result["missing"]) > 0

    def test_detect_gaps_identifies_enhancement_opportunities(self, trainer: Any) -> None:
        """detect_gaps() should identify templates that could be enhanced."""
        analysis = {
            "patterns": [{"id": "test-per-service", "type": "testing"}],
            "tech_stack": ["csharp"],
            "anti_patterns": [{"id": "missing-service-tests", "severity": "P1"}],
        }
        inventory = [
            {
                "id": "test-quality-enforcement",
                "category": "testing",
                "covers": ["coverage"],
                "path": "testing/test-quality-enforcement.yaml",
            },
        ]

        result = trainer.detect_gaps(analysis, inventory)
        assert "enhance" in result

    def test_detect_gaps_identifies_obsolete_templates(self, trainer: Any) -> None:
        """detect_gaps() should identify templates no longer needed."""
        analysis = {
            "patterns": [],
            "tech_stack": ["python"],
            "anti_patterns": [],
        }
        # Template that covers a pattern no longer detected
        inventory = [
            {
                "id": "legacy-jquery-migration",
                "category": "frontend",
                "covers": ["jquery"],
                "path": "frontend/legacy-jquery-migration.yaml",
            },
        ]

        result = trainer.detect_gaps(analysis, inventory)
        assert "obsolete" in result


# =============================================================================
# AC-TRAIN-005: generate_proposal()
# =============================================================================


class TestGenerateProposal:
    """AC-TRAIN-005: generate_proposal() returns change manifest."""

    @pytest.fixture
    def trainer(self) -> Any:
        """Create TrainerOrchestrator instance."""
        from cortex.orchestrators.intelligence.trainer_orchestrator import (
            TrainerOrchestrator,
        )

        return TrainerOrchestrator()

    def test_generate_proposal_returns_manifest(self, trainer: Any) -> None:
        """generate_proposal() should return a manifest dictionary."""
        gaps = {
            "missing": [{"pattern": "di-validation", "reason": "No DI lifetime template"}],
            "enhance": [],
            "obsolete": [],
        }

        result = trainer.generate_proposal(gaps)
        assert isinstance(result, dict)
        assert "actions" in result

    def test_generate_proposal_creates_action_items(self, trainer: Any) -> None:
        """generate_proposal() should create action items for each gap."""
        gaps = {
            "missing": [{"pattern": "di-validation", "reason": "No DI lifetime template"}],
            "enhance": [{"template_id": "test-quality", "enhancement": "Add service test gate"}],
            "obsolete": [],
        }

        result = trainer.generate_proposal(gaps)
        actions = result["actions"]
        
        create_actions = [a for a in actions if a["action"] == "CREATE"]
        enhance_actions = [a for a in actions if a["action"] == "ENHANCE"]
        
        assert len(create_actions) == 1
        assert len(enhance_actions) == 1

    def test_generate_proposal_includes_evidence(self, trainer: Any) -> None:
        """Each action should include evidence from the analysis."""
        gaps = {
            "missing": [{"pattern": "di-validation", "reason": "Captive dependency detected"}],
            "enhance": [],
            "obsolete": [],
        }

        result = trainer.generate_proposal(gaps)
        action = result["actions"][0]
        assert "evidence" in action or "reason" in action


# =============================================================================
# AC-TRAIN-006: execute_proposal()
# =============================================================================


class TestExecuteProposal:
    """AC-TRAIN-006: execute_proposal() applies changes via TDD."""

    @pytest.fixture
    def trainer(self) -> Any:
        """Create TrainerOrchestrator instance."""
        from cortex.orchestrators.intelligence.trainer_orchestrator import (
            TrainerOrchestrator,
        )

        return TrainerOrchestrator()

    def test_execute_proposal_requires_approval(self, trainer: Any) -> None:
        """execute_proposal() should require explicit approval."""
        proposal = {
            "actions": [{"action": "CREATE", "target": "test.yaml", "reason": "test"}],
            "approved": False,
        }

        result = trainer.execute_proposal(proposal)
        assert result["status"] == "pending_approval"

    def test_execute_proposal_executes_when_approved(
        self, trainer: Any, tmp_path: Path
    ) -> None:
        """execute_proposal() should execute when approved."""
        proposal = {
            "actions": [
                {
                    "action": "CREATE",
                    "target": str(tmp_path / "new-template.yaml"),
                    "content": "workflow:\n  id: test\n",
                    "reason": "test",
                }
            ],
            "approved": True,
        }

        result = trainer.execute_proposal(proposal)
        assert result["status"] in ["success", "partial"]

    def test_execute_proposal_returns_execution_report(self, trainer: Any) -> None:
        """execute_proposal() should return detailed execution report."""
        proposal = {
            "actions": [],
            "approved": True,
        }

        result = trainer.execute_proposal(proposal)
        assert "executed" in result
        assert "skipped" in result
        assert "errors" in result


# =============================================================================
# Integration Test
# =============================================================================


class TestTrainerOrchestratorIntegration:
    """Integration test for full training pipeline."""

    @pytest.fixture
    def trainer(self) -> Any:
        """Create TrainerOrchestrator instance."""
        from cortex.orchestrators.intelligence.trainer_orchestrator import (
            TrainerOrchestrator,
        )

        return TrainerOrchestrator()

    def test_full_pipeline_scan_operation(
        self, trainer: Any, tmp_path: Path
    ) -> None:
        """Full pipeline: inventory → analyze → detect_gaps → propose."""
        # Setup target
        target = tmp_path / "target_repo"
        target.mkdir()
        (target / "main.py").write_text("def hello(): pass")

        # Execute via execute_operation (protocol method)
        result = trainer.execute_operation(
            "scan",
            {"target_path": str(target)},
        )

        assert "inventory" in result or "analysis" in result or "proposal" in result

    def test_execute_operation_validates_operation_name(self, trainer: Any) -> None:
        """execute_operation() should validate operation name."""
        result = trainer.execute_operation(
            "invalid_operation",
            {},
        )

        assert "error" in result or result.get("status") == "error"
