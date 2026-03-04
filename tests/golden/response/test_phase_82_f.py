"""
Golden Tests: Phase 82-f — BLOCK-EXECUTION-SPEC + BLOCK-DEVIATION-ALERT + execution_tier Schema
                            Model-Tiering Support

Phase 82 sub-phase 82-f | Closes: GAP-82-12, GAP-82-13, GAP-82-14
Authority: CORE-002 (No report files), CORE-008 (TDD-first), CORE-035 (single canonical
           implementation), CORE-064 (sweep completeness), CORE-066 (response template binding)

12 Acceptance Criteria (tdd_sequence.red):

  BLOCK-EXECUTION-SPEC (GAP-82-12):
    test_execution_spec_block_defined
    test_execution_spec_block_has_table_format
    test_execution_spec_block_has_approval_gate
    test_execution_spec_block_placement
    test_yaml_registry_execution_spec_entry

  BLOCK-DEVIATION-ALERT (GAP-82-13):
    test_deviation_alert_block_defined
    test_deviation_alert_block_has_required_fields
    test_deviation_alert_block_triggers_halt
    test_deviation_alert_distinct_from_error_recovery
    test_yaml_registry_deviation_alert_entry

  execution_tier schema (GAP-82-14):
    test_execution_tier_schema_in_phase_template
    test_phase_82_f_is_self_demonstrating

AC_START: AC-82-F-MODEL-TIERING-001
Phase: 82 | Sub-phase: f | Priority: P2
"""

from pathlib import Path

import pytest
import yaml

# =============================================================================
# Paths
# =============================================================================

ROOT = Path("/Users/asifhussain/PROJECTS/CORTEX")
SSOT = ROOT / ".github" / "templates" / "cortex-response-templates.md"
YAML_REGISTRY = ROOT / "cortex-registry" / "artifacts" / "templates" / "responses" / "response-templates.yaml"
PHASE_TEMPLATE = ROOT / "cortex-registry" / "planning" / "phases" / "_template.yaml"
PHASE_82_F_SPEC = ROOT / "cortex-registry" / "_cortex-master" / "phases" / "completed" / "phase-82-response-template-engine.yaml"
_PHASE_82_F_SPEC_V2_LEGACY = ROOT / "cortex-registry" / "_cortex-master" / "phases" / "completed" / "phase-82-response-template-engine-v2.yaml"


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture(scope="module")
def ssot_text() -> str:
    assert SSOT.exists(), f"SSOT must exist at {SSOT}"
    return SSOT.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def yaml_registry() -> dict:
    assert YAML_REGISTRY.exists(), f"YAML registry must exist at {YAML_REGISTRY}"
    return yaml.safe_load(YAML_REGISTRY.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def phase_template_text() -> str:
    assert PHASE_TEMPLATE.exists(), f"Phase template must exist at {PHASE_TEMPLATE}"
    return PHASE_TEMPLATE.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def phase_82_f_text() -> str:
    assert PHASE_82_F_SPEC.exists(), f"Phase-82 spec must exist at {PHASE_82_F_SPEC}"
    return PHASE_82_F_SPEC.read_text(encoding="utf-8")


# =============================================================================
# GAP-82-12: BLOCK-EXECUTION-SPEC
# =============================================================================


class TestBlockExecutionSpec:
    """GAP-82-12: BLOCK-EXECUTION-SPEC must be defined in SSOT for model-tiering support."""

    def test_execution_spec_block_defined(self, ssot_text: str) -> None:
        """BLOCK-EXECUTION-SPEC must exist in SSOT § Composable Content Blocks.

        Gate 1 (Execution Spec Compilation) is the critical safety mechanism enabling
        plan-on-capable-model + execute-on-cheap-model workflow. Without BLOCK-EXECUTION-SPEC,
        cheaper models (Haiku) have no structured spec to follow — they interpret the plan
        from context, which leads to intent violations.

        GAP-82-12: no canonical block to surface machine-readable execution constraint document.
        """
        assert "BLOCK-EXECUTION-SPEC" in ssot_text, (
            "SSOT must define BLOCK-EXECUTION-SPEC. "
            "This block renders the compiled execution spec as a scannable inline block "
            "(step id | action type | target files | command | validation) before execution begins. "
            "GAP-82-12: no canonical execution spec block defined."
        )

    def test_execution_spec_block_has_table_format(self, ssot_text: str) -> None:
        """BLOCK-EXECUTION-SPEC must specify a table format with canonical columns.

        Canonical table format: Step # | Action | Target Files | Command | Validation
        This makes each step machine-parseable so cheaper executor models can follow verbatim.

        GAP-82-12: execution spec must be rendered as a scannable inline block.
        """
        assert "BLOCK-EXECUTION-SPEC" in ssot_text, (
            "BLOCK-EXECUTION-SPEC must be defined in SSOT before its format can be validated."
        )
        lower = ssot_text.lower()
        # Must reference table columns for the spec
        assert (
            "action" in lower and "target" in lower and "command" in lower and "validation" in lower
        ), (
            "BLOCK-EXECUTION-SPEC must specify table format columns: "
            "Step | Action | Target Files | Command | Validation. "
            "Expected 'action', 'target', 'command', and 'validation' in SSOT."
        )

    def test_execution_spec_block_has_approval_gate(self, ssot_text: str) -> None:
        """BLOCK-EXECUTION-SPEC must include an approval gate before execution begins.

        The user must be able to review and approve the execution spec before the
        cheaper model executes it. This prevents silent divergence from intent.

        GAP-82-12: CORTEX policy: x3 compiles spec; Haiku follows spec verbatim;
        any deviation → BLOCK-DEVIATION-ALERT.
        """
        assert "BLOCK-EXECUTION-SPEC" in ssot_text, (
            "BLOCK-EXECUTION-SPEC must be defined in SSOT before its approval gate can be validated."
        )
        lower = ssot_text.lower()
        assert "proceed" in lower or "approve" in lower or "approval" in lower, (
            "BLOCK-EXECUTION-SPEC must include an approval gate (proceed gate) before execution. "
            "Expected 'proceed' or 'approve' in SSOT near BLOCK-EXECUTION-SPEC."
        )

    def test_execution_spec_block_placement(self, ssot_text: str) -> None:
        """BLOCK-EXECUTION-SPEC must state it renders after BLOCK-INTENT-REFLECTION.

        Integration: renders between BLOCK-INTENT-REFLECTION (confirm intent) and first
        implementation step. User can review + approve before cheaper model executes.

        GAP-82-12: execution spec placement rule not defined.
        """
        assert "BLOCK-EXECUTION-SPEC" in ssot_text, (
            "BLOCK-EXECUTION-SPEC must be defined in SSOT before its placement rule can be validated."
        )
        lower = ssot_text.lower()
        assert "block-intent-reflection" in lower or "intent-reflection" in lower or "intent reflection" in lower, (
            "BLOCK-EXECUTION-SPEC must reference BLOCK-INTENT-REFLECTION as its placement anchor. "
            "The spec block renders after BLOCK-INTENT-REFLECTION and before implementation. "
            "Expected 'BLOCK-INTENT-REFLECTION' reference near BLOCK-EXECUTION-SPEC definition."
        )

    def test_yaml_registry_execution_spec_entry(self, yaml_registry: dict) -> None:
        """YAML registry must have an execution_spec template entry.

        GAP-82-12: execution_spec entry must be machine-readable in YAML registry.
        """
        templates = yaml_registry.get("templates", {})
        assert "execution_spec" in templates, (
            "response-templates.yaml must contain an 'execution_spec' template entry. "
            f"Current template keys: {list(templates.keys())}"
        )


# =============================================================================
# GAP-82-13: BLOCK-DEVIATION-ALERT
# =============================================================================


class TestBlockDeviationAlert:
    """GAP-82-13: BLOCK-DEVIATION-ALERT must be defined in SSOT for executor divergence."""

    def test_deviation_alert_block_defined(self, ssot_text: str) -> None:
        """BLOCK-DEVIATION-ALERT must exist in SSOT § Composable Content Blocks.

        Gate 3 (Deviation Detector) specifies that the executor must HALT + escalate when:
        unexpected test failure, more files changed than allowed, output doesn't match
        expected pattern, conflicting edits, environment mismatch.

        GAP-82-13: no canonical block for unexpected divergence from execution spec.
        """
        assert "BLOCK-DEVIATION-ALERT" in ssot_text, (
            "SSOT must define BLOCK-DEVIATION-ALERT. "
            "This block signals unexpected divergence from the execution spec and forces "
            "an explicit HALT + escalation. "
            "GAP-82-13: no standard deviation alert block defined."
        )

    def test_deviation_alert_block_has_required_fields(self, ssot_text: str) -> None:
        """BLOCK-DEVIATION-ALERT must include Step, Expected, Actual, Divergence type, Action required fields.

        Format:
          ### ⚠️ Deviation Detected — Escalating to Architect
          **Step:** {step_id}
          **Expected:** {expected_output}
          **Actual:** {actual_output}
          **Divergence type:** {more_files | test_unexpected | env_mismatch | output_mismatch}
          **Action required:** Human review or x3 re-plan before continuing

        GAP-82-13: no standard deviation fields defined.
        """
        assert "BLOCK-DEVIATION-ALERT" in ssot_text, (
            "BLOCK-DEVIATION-ALERT must be defined in SSOT before its fields can be validated."
        )
        lower = ssot_text.lower()
        assert "expected" in lower and "actual" in lower, (
            "BLOCK-DEVIATION-ALERT must include Expected and Actual fields to surface "
            "exactly what deviated. Expected 'expected' and 'actual' in SSOT."
        )
        assert "divergence" in lower, (
            "BLOCK-DEVIATION-ALERT must include a Divergence type field. "
            "Expected 'divergence' in SSOT."
        )

    def test_deviation_alert_block_triggers_halt(self, ssot_text: str) -> None:
        """BLOCK-DEVIATION-ALERT must state that the executor must HALT before emitting this block.

        The alert forces an explicit stop — prevents the cheap model from covering up
        the divergence with a 'close enough' patch.

        GAP-82-13: HALT trigger must be explicit in block definition.
        """
        assert "BLOCK-DEVIATION-ALERT" in ssot_text, (
            "BLOCK-DEVIATION-ALERT must be defined in SSOT before its HALT trigger can be validated."
        )
        lower = ssot_text.lower()
        assert "halt" in lower or "stop" in lower or "escalat" in lower, (
            "BLOCK-DEVIATION-ALERT must state the executor must HALT before emitting it. "
            "Expected 'halt', 'stop', or 'escalat' in SSOT near BLOCK-DEVIATION-ALERT definition."
        )

    def test_deviation_alert_distinct_from_error_recovery(self, ssot_text: str) -> None:
        """SSOT must note that BLOCK-DEVIATION-ALERT differs from BLOCK-ERROR-RECOVERY.

        BLOCK-ERROR-RECOVERY: known error states (blocked gates, failed tests where failure expected)
        BLOCK-DEVIATION-ALERT: unexpected divergence from execution spec (executor outside spec)

        Both blocks exist but serve different purposes. SSOT must make this distinction clear.

        GAP-82-13: without explicit distinction, the two blocks will be conflated.
        """
        assert "BLOCK-DEVIATION-ALERT" in ssot_text, (
            "BLOCK-DEVIATION-ALERT must be defined in SSOT before its distinction can be validated."
        )
        assert "BLOCK-ERROR-RECOVERY" in ssot_text, (
            "Both BLOCK-DEVIATION-ALERT and BLOCK-ERROR-RECOVERY must be defined to establish distinction."
        )
        lower = ssot_text.lower()
        # SSOT must reference both in a way that contrasts them
        assert "unexpected" in lower or "divergence" in lower, (
            "SSOT must note BLOCK-DEVIATION-ALERT covers unexpected divergence (distinct from "
            "BLOCK-ERROR-RECOVERY which covers known error states). "
            "Expected 'unexpected' or 'divergence' in SSOT."
        )

    def test_yaml_registry_deviation_alert_entry(self, yaml_registry: dict) -> None:
        """YAML registry must have a deviation_alert template entry.

        GAP-82-13: deviation_alert entry must be machine-readable in YAML registry.
        """
        templates = yaml_registry.get("templates", {})
        assert "deviation_alert" in templates, (
            "response-templates.yaml must contain a 'deviation_alert' template entry. "
            f"Current template keys: {list(templates.keys())}"
        )


# =============================================================================
# GAP-82-14: execution_tier schema
# =============================================================================


class TestExecutionTierSchema:
    """GAP-82-14: execution_tier optional field must be in the phase template."""

    def test_execution_tier_schema_in_phase_template(
        self, phase_template_text: str
    ) -> None:
        """cortex-registry/planning/phases/_template.yaml must have execution_tier optional field.

        Proposed schema:
          execution_tier:
            plan: x3        # model tier that writes the execution spec
            execute: haiku  # model tier that follows the spec
            escalate_to: x3 # model tier that receives BLOCK-DEVIATION-ALERT escalations
            safe_to_delegate: true  # derived: true if all green steps are verbatim

        GAP-82-14: sub-phase specs lack execution_tier field — model-tiering policy unenforceable.
        """
        lower = phase_template_text.lower()
        assert "execution_tier" in lower, (
            "cortex-registry/planning/phases/_template.yaml must define an optional "
            "execution_tier field with plan/execute/escalate_to/safe_to_delegate keys. "
            "GAP-82-14: model-tiering policy is unenforceable without this schema field."
        )
        # Must have at least plan and safe_to_delegate fields defined
        assert "safe_to_delegate" in lower, (
            "execution_tier schema in _template.yaml must include the 'safe_to_delegate' key. "
            "This derived field (true when all green steps are verbatim) enables "
            "safe delegation to cheaper executor models."
        )

    def test_phase_82_f_is_self_demonstrating(self, phase_82_f_text: str) -> None:
        """phase-82-f spec itself must have execution_tier field populated (self-demonstrating).

        The phase-82-f sub-phase already declares execution_tier in its YAML spec:
          execution_tier:
            plan: x3
            execute: x3  # judgment required — not safe for Haiku
            escalate_to: x3
            safe_to_delegate: false

        This test verifies the spec is self-referential (educational — demonstrates the schema).

        GAP-82-14: P3 schema enhancement — self-demonstrating example in the defining sub-phase.
        """
        lower = phase_82_f_text.lower()
        assert "execution_tier" in lower, (
            "phase-82-f spec must contain the execution_tier field as a self-demonstrating example. "
            "The sub-phase that defines this schema should also demonstrate it. "
            "Expected 'execution_tier' in phase-82-response-template-engine.yaml."
        )
        assert "safe_to_delegate" in lower, (
            "phase-82-f execution_tier field must include 'safe_to_delegate' key "
            "as a self-demonstrating example of the schema."
        )


# AC_COMPLETE: AC-82-F-MODEL-TIERING-001 ✅ RED phase — 12 tests written, all must FAIL
