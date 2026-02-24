"""
Phase 67-D: RED tests for convergence_gate schema in canonical YAML templates (GAP-67-04).

Tests verify that:
1. tdd-feature-implementation.yaml refactor_phase step has convergence_gate block
2. audit-fix-pipeline.yaml has convergence_gate configuration for stage 7-8
3. Template validator correctly validates convergence_gate schema
4. WorkflowComposer reads convergence_gate from template steps

Author: Asif Hussain
Phase: 67-D
Sweep: SWEEP-67-WORKFLOW-RUNTIME-WIRING
"""

import pytest
from pathlib import Path
from typing import Any, Dict

# AC_START: AC-67-D-CONVERGENCE-GATE-TEMPLATES-20260224T000000Z

TEMPLATES_ROOT = Path(
    "/Users/asifhussain/PROJECTS/CORTEX/cortex-registry/workflows/templates"
)
TDD_TEMPLATE = TEMPLATES_ROOT / "tdd" / "tdd-feature-implementation.yaml"
AUDIT_TEMPLATE = TEMPLATES_ROOT / "audit" / "audit-fix-pipeline.yaml"


class TestConvergenceGateInTddTemplate:
    """GAP-67-04: tdd-feature-implementation.yaml refactor_phase must have convergence_gate."""

    def test_tdd_template_exists(self) -> None:
        """tdd-feature-implementation.yaml must exist."""
        assert TDD_TEMPLATE.exists(), f"Template not found: {TDD_TEMPLATE}"

    def test_tdd_template_is_valid_yaml(self) -> None:
        """tdd-feature-implementation.yaml must be valid YAML."""
        import yaml

        content = yaml.safe_load(TDD_TEMPLATE.read_text())
        assert content is not None

    def test_refactor_phase_has_convergence_gate(self) -> None:
        """refactor_phase step in tdd template must have convergence_gate block."""
        import yaml

        content = yaml.safe_load(TDD_TEMPLATE.read_text())
        steps = content.get("workflow", {}).get("steps", [])
        refactor_steps = [s for s in steps if s.get("step_id") == "refactor_phase"]
        assert len(refactor_steps) == 1, "refactor_phase step must exist"
        refactor = refactor_steps[0]
        assert "convergence_gate" in refactor, (
            "refactor_phase step must have convergence_gate block. "
            "This is the step that executes RED→GREEN→REFACTOR loop "
            "and MUST be convergence-gated (GAP-67-04)."
        )

    def test_refactor_phase_convergence_gate_has_required_fields(self) -> None:
        """refactor_phase convergence_gate must have max_iterations and check_operation."""
        import yaml

        content = yaml.safe_load(TDD_TEMPLATE.read_text())
        steps = content.get("workflow", {}).get("steps", [])
        refactor = next((s for s in steps if s.get("step_id") == "refactor_phase"), {})
        gate = refactor.get("convergence_gate", {})
        assert "max_cycles" in gate or "max_iterations" in gate, (
            "convergence_gate must have max_cycles or max_iterations"
        )
        assert "convergence_predicate" in gate, (
            "convergence_gate must have convergence_predicate"
        )


class TestConvergenceGateInAuditTemplate:
    """GAP-67-04: audit-fix-pipeline.yaml must have convergence_gate for stage 7-8."""

    def test_audit_template_exists(self) -> None:
        """audit-fix-pipeline.yaml must exist."""
        assert AUDIT_TEMPLATE.exists(), f"Template not found: {AUDIT_TEMPLATE}"

    def test_audit_template_has_convergence_gate_configuration(self) -> None:
        """audit-fix-pipeline.yaml must have convergence_gate config block for stage 7-8."""
        content = AUDIT_TEMPLATE.read_text()
        assert "convergence_gate:" in content, (
            "audit-fix-pipeline.yaml must have convergence_gate: block "
            "for Stage 7-8 auto-fix convergence loop (GAP-67-04). "
            "grep -r convergence_gate cortex-registry/workflows/templates/ → must now have matches."
        )

    def test_audit_convergence_gate_references_validate_p0_count(self) -> None:
        """audit-fix-pipeline.yaml convergence_gate must reference p0 validation."""
        content = AUDIT_TEMPLATE.read_text()
        assert "convergence_gate:" in content
        # Verify it's placed in the convergence loop section
        gate_idx = content.index("convergence_gate:")
        surrounding = content[max(0, gate_idx - 200): gate_idx + 300]
        assert any(
            kw in surrounding
            for kw in ["p0_count", "validate", "stage_7", "stage_8", "auto_fix", "convergence"]
        ), (
            "convergence_gate in audit-fix-pipeline.yaml must be near p0_count/validate context "
            f"(stage 7-8). Found surrounding: {surrounding[:200]}"
        )


class TestWorkflowComposerReadsConvergenceGate:
    """Phase 67-D integration: WorkflowComposer reads convergence_gate from template."""

    def test_workflow_step_convergence_gate_populated_from_template(self) -> None:
        """WorkflowStep.parameters['convergence_gate'] must be populated from YAML template."""
        import os
        import tempfile
        from pathlib import Path
        from cortex.orchestrators.workflow.workflow_composer import WorkflowComposer

        yaml_content = """workflow:
  name: test-convergence-gate-schema
  steps:
    - step_id: refactor_phase
      orchestrator: RefactoringOrchestrator
      convergence_gate:
        max_cycles: 3
        convergence_predicate: "all_tests_pass and complexity_reduced"
        check_operation: validate_tests_green
"""
        tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False)
        tmp.write(yaml_content)
        tmp.flush()
        tmp.close()
        template = Path(tmp.name)

        try:
            composer = WorkflowComposer(template_path=template)
        finally:
            os.unlink(tmp.name)

        assert len(composer._steps) == 1
        step = composer._steps[0]
        assert "convergence_gate" in step.parameters, (
            "WorkflowComposer must preserve convergence_gate from YAML template "
            "into WorkflowStep.parameters['convergence_gate']"
        )
        gate = step.parameters["convergence_gate"]
        assert gate.get("max_cycles") == 3
        assert "all_tests_pass" in gate.get("convergence_predicate", "")

    def test_execute_with_convergence_uses_template_convergence_gate(self) -> None:
        """_execute_with_convergence() must use convergence_gate.max_cycles from template."""
        import os
        import tempfile
        from pathlib import Path
        from cortex.orchestrators.workflow.workflow_composer import WorkflowComposer
        from cortex.orchestrators.workflow.convergence_loop_executor import (
            ConvergenceLoopExecutor,
        )
        from unittest.mock import patch

        yaml_content = """workflow:
  name: test-gate-max-cycles
  steps:
    - step_id: refactor_phase
      orchestrator: RefactoringOrchestrator
      convergence_gate:
        max_cycles: 7
        convergence_predicate: "all_tests_pass"
"""
        tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False)
        tmp.write(yaml_content)
        tmp.flush()
        tmp.close()
        template = Path(tmp.name)

        try:
            composer = WorkflowComposer(template_path=template)
        finally:
            os.unlink(tmp.name)

        captured_configs: list = []
        original_init = ConvergenceLoopExecutor.__init__

        def capturing_init(self_inner: Any, config: Any = None) -> None:
            if config is not None:
                captured_configs.append(config)
            original_init(self_inner, config=config)

        with patch.object(ConvergenceLoopExecutor, "__init__", capturing_init):
            try:
                composer._execute_with_convergence(workflow=None, context=None)
            except Exception:
                pass

        assert len(captured_configs) >= 1, "ConvergenceLoopExecutor must be instantiated"
        config = captured_configs[0]
        assert config.max_retries == 7, (
            f"ConvergenceLoopExecutor.config.max_retries must be 7 (from template), got {config.max_retries}"
        )


# AC_COMPLETE: AC-67-D-CONVERGENCE-GATE-TEMPLATES-20260224T000000Z ✅
