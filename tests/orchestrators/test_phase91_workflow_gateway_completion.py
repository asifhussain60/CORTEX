"""
Phase 91 — Workflow Composer Mandatory Gateway Completion
TDD RED → GREEN → REFACTOR

Covers all 5 gaps identified in the Phase 91 landscape audit:
  GAP-1: TrainerOrchestrator and MasterOrchestrator gateway not enabled
  GAP-2: INVESTIGATE mode has no dedicated workflow template
  GAP-3: train-workflow and totalrecall-workflow missing review-and-cleanup
  GAP-4: workflow-composer-spec missing convergence ref for TRAIN/TOTALRECALL
  GAP-5: audit fix Stage 9 pattern_detection not reading workflow_runs table
  GAP-6: activity-log-query primitive does not exist
  GAP-7: investigate-workflow.yaml does not exist

Governance:
  CORE-008: TDD mandatory — these tests written before implementation
  CORE-011: Type hints on all functions
  CORE-012: Docstrings on all public APIs
  CORE-064: Sweep completeness contract
"""

from __future__ import annotations

import sqlite3
import tempfile
from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest
import yaml


# ============================================================================
# CONSTANTS
# ============================================================================
TEMPLATES_ROOT = Path(__file__).parents[2] / "cortex-registry" / "workflows" / "templates"
SPEC_PATH = Path(__file__).parents[2] / "cortex-registry" / "workflows" / "workflow-composer-spec.yaml"


# ============================================================================
# GAP-1: TrainerOrchestrator gateway enablement
# ============================================================================
class TestTrainerOrchestratorGateway:
    """GAP-1: TrainerOrchestrator code-touching (Step 6: apply_proposals) must route via gateway."""

    def test_trainer_orchestrator_has_gateway_enabled(self) -> None:
        """TrainerOrchestrator.PHASE90_GATEWAY_ENABLED must be True (Phase 91)."""
        from cortex.orchestrators.intelligence.trainer_orchestrator import TrainerOrchestrator

        assert TrainerOrchestrator.PHASE90_GATEWAY_ENABLED is True, (
            "TrainerOrchestrator touches code in apply_proposals() — must route via WorkflowGateway. "
            "Set PHASE90_GATEWAY_ENABLED = True."
        )

    def test_trainer_orchestrator_inherits_enforcement_mixin(self) -> None:
        """TrainerOrchestrator must inherit WorkflowEnforcementMixin."""
        from cortex.core.workflow_enforcement_mixin import WorkflowEnforcementMixin
        from cortex.orchestrators.intelligence.trainer_orchestrator import TrainerOrchestrator

        assert issubclass(TrainerOrchestrator, WorkflowEnforcementMixin)

    def test_trainer_orchestrator_resolves_train_template(self) -> None:
        """WorkflowGateway must resolve 'lifecycle/train-workflow' for mode TRAIN."""
        from cortex.orchestrators.workflow.workflow_gateway import WorkflowGateway

        gateway = WorkflowGateway()
        template_id = gateway.resolve_template("TRAIN", {})
        assert template_id == "lifecycle/train-workflow", (
            f"Expected 'lifecycle/train-workflow', got '{template_id}'"
        )


# ============================================================================
# GAP-1b: MasterOrchestrator gateway registration
# ============================================================================
class TestMasterOrchestratorGatewayRegistration:
    """GAP-1b: WorkflowGateway MODE_TEMPLATE_MAP must map TOTALRECALL + SYNC."""

    def test_workflow_gateway_maps_totalrecall(self) -> None:
        """WorkflowGateway must have TOTALRECALL → lifecycle/totalrecall-workflow."""
        from cortex.orchestrators.workflow.workflow_gateway import WorkflowGateway

        gateway = WorkflowGateway()
        template_id = gateway.resolve_template("TOTALRECALL", {})
        assert template_id == "lifecycle/totalrecall-workflow"

    def test_workflow_gateway_maps_sync(self) -> None:
        """WorkflowGateway must have SYNC → lifecycle/sync-workflow."""
        from cortex.orchestrators.workflow.workflow_gateway import WorkflowGateway

        gateway = WorkflowGateway()
        template_id = gateway.resolve_template("SYNC", {})
        assert template_id == "lifecycle/sync-workflow"

    def test_workflow_gateway_maps_train(self) -> None:
        """WorkflowGateway must have TRAIN → lifecycle/train-workflow."""
        from cortex.orchestrators.workflow.workflow_gateway import WorkflowGateway

        gateway = WorkflowGateway()
        template_id = gateway.resolve_template("TRAIN", {})
        assert template_id == "lifecycle/train-workflow"


# ============================================================================
# GAP-2: INVESTIGATE mode workflow template
# ============================================================================
class TestInvestigateWorkflowTemplate:
    """GAP-2: INVESTIGATE mode must have a dedicated workflow template."""

    def test_investigate_workflow_file_exists(self) -> None:
        """lifecycle/investigate-workflow.yaml must exist."""
        template_path = TEMPLATES_ROOT / "lifecycle" / "investigate-workflow.yaml"
        assert template_path.exists(), (
            "lifecycle/investigate-workflow.yaml is missing. "
            "Create it as a read-only LENS scan template with SQLite trace (Phase 91)."
        )

    def test_investigate_workflow_has_required_fields(self) -> None:
        """investigate-workflow.yaml must declare required template fields."""
        template_path = TEMPLATES_ROOT / "lifecycle" / "investigate-workflow.yaml"
        if not template_path.exists():
            pytest.skip("investigate-workflow.yaml not yet created")
        with open(template_path) as f:
            data = yaml.safe_load(f)
        workflow = data.get("workflow", {})
        assert workflow.get("id") == "lifecycle/investigate-workflow"
        assert "steps" in workflow
        assert workflow.get("status") == "active"

    def test_investigate_workflow_references_ac_marker(self) -> None:
        """investigate-workflow.yaml must include ac-marker-emit steps."""
        template_path = TEMPLATES_ROOT / "lifecycle" / "investigate-workflow.yaml"
        if not template_path.exists():
            pytest.skip("investigate-workflow.yaml not yet created")
        content = template_path.read_text()
        assert "ac-marker-emit" in content, "Must reference primitives/execution/ac-marker-emit"

    def test_workflow_gateway_maps_investigate(self) -> None:
        """WorkflowGateway must map INVESTIGATE → lifecycle/investigate-workflow."""
        from cortex.orchestrators.workflow.workflow_gateway import WorkflowGateway

        gateway = WorkflowGateway()
        template_id = gateway.resolve_template("INVESTIGATE", {})
        assert template_id == "lifecycle/investigate-workflow", (
            f"Expected 'lifecycle/investigate-workflow', got '{template_id}'"
        )


# ============================================================================
# GAP-3: review-and-cleanup in train-workflow + totalrecall-workflow
# ============================================================================
class TestReviewAndCleanupEpilogue:
    """GAP-3: All code-touching mode workflows must end with review-and-cleanup primitive."""

    def _load_template(self, relative_path: str) -> str:
        """Load template YAML content as string."""
        return (TEMPLATES_ROOT / relative_path).read_text()

    @pytest.mark.parametrize("template_path", [
        "lifecycle/train-workflow.yaml",
        "lifecycle/totalrecall-workflow.yaml",
        "sdlc/implement-workflow.yaml",
        "sdlc/fix-workflow.yaml",
        "quality/refactor-workflow.yaml",
        "debugging/multi-stack-debug-pipeline.yaml",
        "maintenance/health-check-workflow.yaml",
        "maintenance/vacuum-workflow.yaml",
    ])
    def test_template_contains_review_and_cleanup(self, template_path: str) -> None:
        """All code-touching workflows must reference primitives/execution/review-and-cleanup."""
        full_path = TEMPLATES_ROOT / template_path
        if not full_path.exists():
            pytest.skip(f"{template_path} not yet created")
        content = full_path.read_text()
        assert "review-and-cleanup" in content, (
            f"{template_path} is missing 'review-and-cleanup' primitive reference. "
            "Every code-touching workflow must end with the universal epilogue."
        )


# ============================================================================
# GAP-4: workflow-composer-spec convergence refs for TRAIN/TOTALRECALL
# ============================================================================
class TestWorkflowComposerSpecConvergence:
    """GAP-4: TRAIN and TOTALRECALL must declare convergence in workflow-composer-spec.yaml."""

    def _load_spec(self) -> Dict[str, Any]:
        with open(SPEC_PATH) as f:
            return yaml.safe_load(f)

    def test_train_has_convergence_ref_in_spec(self) -> None:
        """TRAIN entry in workflow-composer-spec must declare convergence."""
        spec = self._load_spec()
        routing = spec.get("intent_routing", {})
        train = routing.get("TRAIN", {})
        assert "convergence" in train, (
            "workflow-composer-spec.yaml TRAIN entry missing 'convergence' field. "
            "Code-touching modes require detect-fix-rescan-loop (CORE-068)."
        )
        assert "detect-fix-rescan-loop" in train["convergence"]

    def test_totalrecall_has_convergence_ref_in_spec(self) -> None:
        """TOTALRECALL entry in workflow-composer-spec must declare convergence."""
        spec = self._load_spec()
        routing = spec.get("intent_routing", {})
        totalrecall = routing.get("TOTALRECALL", {})
        assert "convergence" in totalrecall, (
            "workflow-composer-spec.yaml TOTALRECALL entry missing 'convergence' field."
        )
        assert "detect-fix-rescan-loop" in totalrecall["convergence"]

    def test_investigate_has_workflow_ref_in_spec(self) -> None:
        """INVESTIGATE entry must declare a workflow_ref (not null) after Phase 91."""
        spec = self._load_spec()
        routing = spec.get("intent_routing", {})
        investigate = routing.get("INVESTIGATE", {})
        wf_ref = investigate.get("workflow_ref")
        assert wf_ref is not None and wf_ref != "", (
            "INVESTIGATE workflow_ref is null. Phase 91 requires lifecycle/investigate-workflow."
        )
        assert wf_ref == "lifecycle/investigate-workflow"


# ============================================================================
# GAP-6: activity-log-query primitive
# ============================================================================
class TestActivityLogQueryPrimitive:
    """GAP-6: primitives/intelligence/activity-log-query.yaml must exist and be valid."""

    def test_activity_log_query_primitive_exists(self) -> None:
        """primitives/intelligence/activity-log-query.yaml must exist."""
        primitive_path = TEMPLATES_ROOT / "primitives" / "intelligence" / "activity-log-query.yaml"
        assert primitive_path.exists(), (
            "primitives/intelligence/activity-log-query.yaml is missing. "
            "Create it as a reusable primitive for reading workflow_runs from SQLite."
        )

    def test_activity_log_query_primitive_structure(self) -> None:
        """activity-log-query.yaml must have tier=primitive and required fields."""
        primitive_path = TEMPLATES_ROOT / "primitives" / "intelligence" / "activity-log-query.yaml"
        if not primitive_path.exists():
            pytest.skip("activity-log-query.yaml not yet created")
        with open(primitive_path) as f:
            data = yaml.safe_load(f)
        assert data.get("tier") == "primitive"
        assert data.get("template_id") == "primitives/intelligence/activity-log-query"
        assert "steps" in data

    def test_activity_log_query_reads_workflow_runs(self) -> None:
        """activity-log-query.yaml must reference the workflow_runs SQLite table."""
        primitive_path = TEMPLATES_ROOT / "primitives" / "intelligence" / "activity-log-query.yaml"
        if not primitive_path.exists():
            pytest.skip("activity-log-query.yaml not yet created")
        content = primitive_path.read_text()
        assert "workflow_runs" in content, (
            "activity-log-query primitive must query the workflow_runs table."
        )


# ============================================================================
# GAP-5: audit-fix-pipeline Stage 9 reads workflow_runs for intelligent decisions
# ============================================================================
class TestAuditFixActivityLogIntegration:
    """GAP-5: Stage 9 in audit-fix-pipeline must reference activity-log-query primitive."""

    def test_audit_fix_pipeline_stage9_references_activity_log_query(self) -> None:
        """audit-fix-pipeline.yaml Stage 9 must include activity-log-query step."""
        pipeline_path = TEMPLATES_ROOT / "audit" / "audit-fix-pipeline.yaml"
        content = pipeline_path.read_text()
        assert "activity-log-query" in content, (
            "audit-fix-pipeline.yaml Stage 9 must reference 'activity-log-query' primitive. "
            "This enables intelligent upgrade decisions from historical workflow_runs data."
        )


# ============================================================================
# INTEGRATION: WorkflowGateway SQLite logging for all newly enabled modes
# ============================================================================
class TestWorkflowGatewaySQLiteLogging:
    """All gateway-enabled modes must produce a workflow_runs row in SQLite."""

    def test_execute_gated_logs_train_mode_to_sqlite(self) -> None:
        """WorkflowGateway.execute_gated for TRAIN must write a workflow_runs row."""
        from cortex.orchestrators.workflow.workflow_gateway import WorkflowGateway

        with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
            db_path = Path(tmp.name)
            gateway = WorkflowGateway(db_path=db_path)

            mock_composer = MagicMock()
            mock_composer.execute_from_template.return_value = {
                "status": "complete",
                "steps_completed": 6,
            }
            gateway._composer = mock_composer

            result = gateway.execute_gated(
                orchestrator_name="TrainerOrchestrator",
                mode="TRAIN",
                context={"target_repo_path": "/tmp/test-repo"},
            )

            assert result["status"] == "complete"
            assert result["template_id"] == "lifecycle/train-workflow"

            with sqlite3.connect(str(db_path)) as conn:
                rows = conn.execute(
                    "SELECT mode, template_id, status FROM workflow_runs WHERE mode = 'TRAIN'"
                ).fetchall()
            assert len(rows) == 1
            assert rows[0][1] == "lifecycle/train-workflow"
            assert rows[0][2] == "complete"

    def test_execute_gated_logs_investigate_mode_to_sqlite(self) -> None:
        """WorkflowGateway.execute_gated for INVESTIGATE must write a workflow_runs row."""
        from cortex.orchestrators.workflow.workflow_gateway import WorkflowGateway

        with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
            db_path = Path(tmp.name)
            gateway = WorkflowGateway(db_path=db_path)

            mock_composer = MagicMock()
            mock_composer.execute_from_template.return_value = {
                "status": "complete",
                "steps_completed": 4,
            }
            gateway._composer = mock_composer

            result = gateway.execute_gated(
                orchestrator_name="InvestigationOrchestrator",
                mode="INVESTIGATE",
                context={"query": "why did deployment fail?"},
            )

            assert result["status"] == "complete"
            assert result["template_id"] == "lifecycle/investigate-workflow"

            with sqlite3.connect(str(db_path)) as conn:
                rows = conn.execute(
                    "SELECT mode, template_id FROM workflow_runs WHERE mode = 'INVESTIGATE'"
                ).fetchall()
            assert len(rows) == 1
            assert rows[0][1] == "lifecycle/investigate-workflow"
