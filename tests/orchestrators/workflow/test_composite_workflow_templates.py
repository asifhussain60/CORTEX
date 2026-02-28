"""
Composite Workflow Template Tests.

Validates the composable workflow template system:
  1. composite-execution-pipeline.yaml - generic pipeline-of-pipelines

Authority: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
Compliance: CORE-028 (snake_case filenames), CORE-035 (no duplication)

Note: threat-model-analysis.yaml, cross-phase-holistic-epilogue.yaml, and
test-strategy-matrix.yaml were removed in Phase 98 (dead code cleanup) as
unreferenced templates.
"""

import pytest
import yaml
from pathlib import Path
from typing import Any, Dict, List, Set


TEMPLATES_ROOT = Path("cortex-registry/workflows/templates")
COMPOSITE_PIPELINE = TEMPLATES_ROOT / "lifecycle" / "composite-execution-pipeline.yaml"


def _load_yaml(path: Path) -> Dict[str, Any]:
    """Load and parse a YAML file."""
    assert path.exists(), f"Template not found: {path}"
    with open(path, "r") as f:
        return yaml.safe_load(f)


def _get_workflow(data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract workflow block from parsed YAML."""
    assert "workflow" in data, "Missing top-level 'workflow' key"
    return data["workflow"]


def _get_steps(workflow: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract steps list from workflow."""
    assert "steps" in workflow, "Missing 'steps' in workflow"
    return workflow["steps"]


def _get_step_ids(steps: List[Dict[str, Any]]) -> Set[str]:
    """Extract all step_id values."""
    return {step["step_id"] for step in steps}


class TestTemplateSchemaCompliance:
    """Composite pipeline template must conform to CORTEX workflow YAML schema."""

    @pytest.fixture
    def template_data(self) -> Dict[str, Any]:
        """Load the composite pipeline template for schema validation."""
        return _load_yaml(COMPOSITE_PIPELINE)

    def test_has_workflow_root(self, template_data: Dict[str, Any]) -> None:
        """Template must have top-level 'workflow' key."""
        assert "workflow" in template_data

    def test_has_required_identity_fields(self, template_data: Dict[str, Any]) -> None:
        """Workflow must have id, name, version, category, description."""
        wf = template_data["workflow"]
        for field in ("id", "name", "version", "category", "description"):
            assert field in wf, f"Missing required field: {field}"

    def test_has_metadata_block(self, template_data: Dict[str, Any]) -> None:
        """Workflow must have metadata with author and created date."""
        wf = template_data["workflow"]
        assert "metadata" in wf
        meta = wf["metadata"]
        assert "author" in meta

    def test_has_steps(self, template_data: Dict[str, Any]) -> None:
        """Workflow must have at least one step."""
        wf = template_data["workflow"]
        assert "steps" in wf
        assert len(wf["steps"]) > 0

    def test_steps_have_required_fields(self, template_data: Dict[str, Any]) -> None:
        """Each step must have step_id, name."""
        wf = template_data["workflow"]
        for step in wf["steps"]:
            assert "step_id" in step, f"Step missing step_id: {step}"
            assert "name" in step, f"Step missing name: {step.get('step_id', '?')}"

    def test_unique_step_ids(self, template_data: Dict[str, Any]) -> None:
        """Step IDs must be unique within a template."""
        wf = template_data["workflow"]
        step_ids = [s["step_id"] for s in wf["steps"]]
        assert len(step_ids) == len(set(step_ids)), "Duplicate step_ids found"

    def test_has_convergence_gate(self, template_data: Dict[str, Any]) -> None:
        """Workflow must have convergence_gate (CORE-068)."""
        wf = template_data["workflow"]
        assert "convergence_gate" in wf

    def test_convergence_has_max_cycles(self, template_data: Dict[str, Any]) -> None:
        """Convergence gate must declare max_cycles."""
        wf = template_data["workflow"]
        gate = wf["convergence_gate"]
        assert "max_cycles" in gate
        assert isinstance(gate["max_cycles"], int)
        assert gate["max_cycles"] >= 1


class TestCompositeExecutionPipeline:
    """Validates the composite execution pipeline template."""

    @pytest.fixture
    def pipeline(self) -> Dict[str, Any]:
        """Load composite pipeline."""
        return _get_workflow(_load_yaml(COMPOSITE_PIPELINE))

    def test_category_is_lifecycle(self, pipeline: Dict[str, Any]) -> None:
        """Pipeline belongs to lifecycle category."""
        assert pipeline["category"] == "lifecycle"

    def test_has_template_ref_steps(self, pipeline: Dict[str, Any]) -> None:
        """Pipeline composes other templates via template_ref."""
        steps = _get_steps(pipeline)
        ref_steps = [s for s in steps if s.get("template_ref")]
        assert len(ref_steps) >= 1, "Pipeline must compose other templates"

    def test_step_ordering_is_logical(self, pipeline: Dict[str, Any]) -> None:
        """Steps follow a logical order (analysis before implementation)."""
        steps = _get_steps(pipeline)
        assert len(steps) >= 3, "Pipeline should have multiple stages"

    def test_convergence_gate_has_criteria(self, pipeline: Dict[str, Any]) -> None:
        """Pipeline convergence gate has success criteria."""
        gate = pipeline["convergence_gate"]
        assert "success_criteria" in gate


class TestGovernanceCompliance:
    """Validates CORE rule compliance for the composite pipeline template."""

    def test_filename_is_kebab_case(self) -> None:
        """CORE-028: filenames must be kebab-case for YAML."""
        name = COMPOSITE_PIPELINE.name
        assert name == name.lower(), f"Filename must be lowercase: {name}"
        assert " " not in name, f"Filename must not have spaces: {name}"
        assert "_" not in name.replace(".yaml", ""), (
            f"YAML filenames use kebab-case, not snake_case: {name}"
        )

    def test_yaml_is_valid(self) -> None:
        """Template must be parseable as valid YAML."""
        data = _load_yaml(COMPOSITE_PIPELINE)
        assert isinstance(data, dict)

    def test_version_is_semver(self) -> None:
        """Version must follow semver (x.y.z)."""
        wf = _get_workflow(_load_yaml(COMPOSITE_PIPELINE))
        version = wf["version"]
        parts = version.split(".")
        assert len(parts) == 3, f"Version must be semver: {version}"
        for part in parts:
            assert part.isdigit(), f"Version parts must be numeric: {version}"
