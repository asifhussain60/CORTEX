"""
Sub-phase 129-e tests — distill-workflow.yaml exists and is valid YAML.

TDD contract (CORE-008): these fail before the workflow file is created.
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml


WORKFLOW_PATH = Path(__file__).parents[3] / (
    "cortex-registry/workflows/templates/lifecycle/distill-workflow.yaml"
)


class TestDistillWorkflowYaml:
    """distill-workflow.yaml structural validation."""

    def test_workflow_file_exists(self):
        assert WORKFLOW_PATH.exists(), (
            f"distill-workflow.yaml not found at {WORKFLOW_PATH}"
        )

    def test_workflow_file_is_valid_yaml(self):
        content = WORKFLOW_PATH.read_text(encoding="utf-8")
        doc = yaml.safe_load(content)
        assert doc is not None, "distill-workflow.yaml parsed as empty/null"

    def test_workflow_has_id(self):
        doc = yaml.safe_load(WORKFLOW_PATH.read_text())
        assert doc.get("id") == "lifecycle/distill-workflow"

    def test_workflow_has_correct_mode(self):
        doc = yaml.safe_load(WORKFLOW_PATH.read_text())
        modes = doc["workflow"]["metadata"]["modes_served"]
        assert "DISTILL" in modes

    def test_workflow_has_five_stages(self):
        doc = yaml.safe_load(WORKFLOW_PATH.read_text())
        steps = doc["workflow"]["steps"]
        # Steps: ac_start + 5 stages + ac_complete = 7
        stage_ids = [s["id"] for s in steps if s["id"].startswith("stage_")]
        assert len(stage_ids) == 5, (
            f"Expected 5 stage steps, found {len(stage_ids)}: {stage_ids}"
        )

    def test_workflow_has_distilled_prompt_output(self):
        doc = yaml.safe_load(WORKFLOW_PATH.read_text())
        outputs = doc["workflow"].get("outputs", {})
        assert "distilled_prompt" in outputs

    def test_workflow_composer_spec_lists_distill(self):
        spec_path = Path(__file__).parents[3] / (
            "cortex-registry/workflows/workflow-composer-spec.yaml"
        )
        spec = yaml.safe_load(spec_path.read_text())
        intent_routing = spec.get("intent_routing", {})
        assert "DISTILL" in intent_routing, (
            "DISTILL missing from intent_routing in workflow-composer-spec.yaml"
        )
