"""
RED phase tests — service-decomposition-workflow.yaml structure validation (Phase 14 / CORE-008).

Validates the workflow YAML conforms to WorkflowEngine schema and CORTEX conventions.
Implementation target: cortex-registry/workflows/templates/lifecycle/service-decomposition-workflow.yaml
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest
import yaml


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

WORKFLOW_PATH = Path(
    "cortex-registry/workflows/templates/lifecycle/service-decomposition-workflow.yaml"
)


@pytest.fixture
def workflow_data() -> dict:
    """Load and parse the service-decomposition workflow YAML."""
    assert WORKFLOW_PATH.exists(), f"Workflow file not found: {WORKFLOW_PATH}"
    with WORKFLOW_PATH.open() as fh:
        return yaml.safe_load(fh)


# ---------------------------------------------------------------------------
# Structure tests
# ---------------------------------------------------------------------------

class TestWorkflowStructure:
    """Validate top-level YAML structure."""

    def test_file_exists(self):
        """Workflow template file must exist on disk."""
        assert WORKFLOW_PATH.exists()

    def test_top_level_workflow_key(self, workflow_data):
        """Top-level key must be 'workflow'."""
        assert "workflow" in workflow_data

    def test_workflow_has_id(self, workflow_data):
        """workflow.id must be present and follow lifecycle/ prefix convention."""
        wf = workflow_data["workflow"]
        assert "id" in wf
        assert wf["id"].startswith("lifecycle/")

    def test_workflow_id_no_monolith(self, workflow_data):
        """workflow.id must not contain the word 'monolith'."""
        wf_id = workflow_data["workflow"]["id"].lower()
        assert "monolith" not in wf_id

    def test_workflow_name_no_monolith(self, workflow_data):
        """workflow.name must not contain the word 'monolith'."""
        name = workflow_data["workflow"].get("name", "").lower()
        assert "monolith" not in name

    def test_workflow_has_steps(self, workflow_data):
        """workflow.steps must be a non-empty list."""
        steps = workflow_data["workflow"].get("steps", [])
        assert isinstance(steps, list)
        assert len(steps) > 0

    def test_workflow_has_metadata(self, workflow_data):
        """workflow.metadata must be present."""
        assert "metadata" in workflow_data["workflow"]

    def test_workflow_has_success_criteria(self, workflow_data):
        """workflow.success_criteria must be present."""
        assert "success_criteria" in workflow_data["workflow"]


# ---------------------------------------------------------------------------
# Step sequence tests
# ---------------------------------------------------------------------------

class TestWorkflowStepSequence:
    """Validate the 8-step strangler-fig progression."""

    EXPECTED_STEPS = [
        "lens_baseline",
        "security_gate",
        "layer_data_access",
        "layer_api",
        "layer_frontend",
        "layer_tests",
        "holistic_sweep",
        "lens_verification",
    ]

    def _step_ids(self, workflow_data: dict) -> list[str]:
        return [s["step_id"] for s in workflow_data["workflow"]["steps"]]

    def test_all_expected_steps_present(self, workflow_data):
        """All 8 required step IDs must be present."""
        step_ids = self._step_ids(workflow_data)
        for expected in self.EXPECTED_STEPS:
            assert expected in step_ids, f"Missing step: {expected}"

    def test_security_gate_is_blocking(self, workflow_data):
        """security_gate step must have blocking: true."""
        steps = {s["step_id"]: s for s in workflow_data["workflow"]["steps"]}
        assert steps["security_gate"].get("blocking") is True

    def test_security_gate_before_layer_data_access(self, workflow_data):
        """security_gate must appear before layer_data_access in steps list."""
        step_ids = self._step_ids(workflow_data)
        assert step_ids.index("security_gate") < step_ids.index("layer_data_access")

    def test_lens_verification_is_last(self, workflow_data):
        """lens_verification must be the final step."""
        step_ids = self._step_ids(workflow_data)
        assert step_ids[-1] == "lens_verification"

    def test_lens_baseline_is_first(self, workflow_data):
        """lens_baseline must be the first step."""
        step_ids = self._step_ids(workflow_data)
        assert step_ids[0] == "lens_baseline"


# ---------------------------------------------------------------------------
# Convergence gate tests
# ---------------------------------------------------------------------------

class TestConvergenceGates:
    """Each step must define a convergence_gate with max_cycles."""

    def test_all_steps_have_convergence_gate(self, workflow_data):
        """Every step must declare a convergence_gate."""
        for step in workflow_data["workflow"]["steps"]:
            assert "convergence_gate" in step, (
                f"Step '{step['step_id']}' missing convergence_gate"
            )

    def test_all_convergence_gates_have_max_cycles(self, workflow_data):
        """Every convergence_gate must define max_cycles > 0."""
        for step in workflow_data["workflow"]["steps"]:
            gate = step.get("convergence_gate", {})
            assert "max_cycles" in gate, (
                f"Step '{step['step_id']}' convergence_gate missing max_cycles"
            )
            assert gate["max_cycles"] > 0

    def test_security_gate_max_cycles_gte_5(self, workflow_data):
        """security_gate convergence max_cycles must be >= 5 (retries matter)."""
        steps = {s["step_id"]: s for s in workflow_data["workflow"]["steps"]}
        assert steps["security_gate"]["convergence_gate"]["max_cycles"] >= 5


# ---------------------------------------------------------------------------
# CORE-028 FileFactory name compliance
# ---------------------------------------------------------------------------

class TestFileFactoryCompliance:
    """CORE-028 — YAML files must use hyphens, not underscores."""

    def test_filename_uses_hyphens(self):
        """Filename must contain only hyphens as word separators (no underscores)."""
        filename = WORKFLOW_PATH.name
        assert "_" not in filename, f"Filename uses underscores: {filename}"

    def test_filename_extension_is_yaml(self):
        """File must have .yaml extension."""
        assert WORKFLOW_PATH.suffix == ".yaml"

    def test_filename_no_monolith(self):
        """Filename must not contain 'monolith'."""
        assert "monolith" not in WORKFLOW_PATH.name.lower()
