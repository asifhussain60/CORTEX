"""
Golden Tests: Response Template Binding — CORE-066

Phase 64 sub-phase 64-G | Closes: GAP-64-03 (partial)
Authority: CORE-066 (Response Template Binding), CORE-002 (No report files),
           CORE-049 (Silent autonomous execution)

6 Acceptance Criteria (AC-64-G-07 through AC-64-G-12):

  AC-64-G-07  test_implement_mode_response_has_canonical_header
              IMPLEMENT intent produces response with canonical Author + Orchestrator header
  AC-64-G-08  test_audit_mode_response_has_violation_table_schema
              AUDIT intent produces response structure with violations table columns
  AC-64-G-09  test_all_modes_have_progress_bar_definition
              copilot-chat-response-template.yaml progress_bar section exists and has 10-block rule
  AC-64-G-10  test_raw_dict_output_is_p1_violation
              ResponseTemplateValidator.validate_output() rejects raw dict as P1
  AC-64-G-11  test_response_template_yaml_loadable_and_valid
              copilot-chat-response-template.yaml loads cleanly from registry
  AC-64-G-12  test_session_pause_banner_triggered_when_sweep_incomplete
              session_pause_banner section defined and has sweep_id + resume_command fields

AC_START: AC-64-G-RESPONSE-001
Phase: 64 | Stage: G | Priority: P0
"""

from pathlib import Path
from typing import Any, Dict

import pytest
import yaml


# =============================================================================
# Paths
# =============================================================================

REPO_ROOT = Path(__file__).resolve().parents[3]
GOVERNANCE_TEMPLATES = REPO_ROOT / "cortex-registry/workflows/templates/governance"
RESPONSE_TEMPLATE_YAML = GOVERNANCE_TEMPLATES / "copilot-chat-response-template.yaml"
RESPONSE_TEMPLATES_SSOT = REPO_ROOT / ".github/templates/cortex-response-templates.md"


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture(scope="module")
def response_template_doc() -> Dict[str, Any]:
    """Load copilot-chat-response-template.yaml once for the module."""
    assert RESPONSE_TEMPLATE_YAML.exists(), (
        f"copilot-chat-response-template.yaml must exist at {RESPONSE_TEMPLATE_YAML}"
    )
    data = yaml.safe_load(RESPONSE_TEMPLATE_YAML.read_text())
    assert isinstance(data, dict), "Template YAML must parse to a dict"
    return data


# =============================================================================
# AC-64-G-07  IMPLEMENT mode response has canonical header
# =============================================================================

class TestImplementModeResponse:
    """AC-64-G-07: IMPLEMENT intent produces response with canonical Author header."""

    def test_implement_mode_response_has_canonical_header(
        self, response_template_doc: Dict[str, Any]
    ) -> None:
        """Header format must contain Author + Orchestrator canonical fields."""
        header = response_template_doc.get("workflow", {}).get("header", {})
        assert header, "Response template must have a 'header' section under 'workflow'"

        fmt = header.get("format", "")
        assert "{author}" in fmt or "author" in str(header), (
            "Header format must include {author} field for canonical 'Asif Hussain' binding."
        )
        assert "{orchestrator_name}" in fmt or "orchestrator_name" in str(header), (
            "Header format must include {orchestrator_name} for Orchestrator ✅ binding."
        )

    def test_canonical_author_is_asif_hussain(
        self, response_template_doc: Dict[str, Any]
    ) -> None:
        """The canonical author value must be 'Asif Hussain' (SSOT)."""
        header = response_template_doc.get("workflow", {}).get("header", {})
        required_fields = header.get("required_fields", [])
        # required_fields is a list of single-key dicts: [{"author": "Asif Hussain"}, ...]
        author_value = None
        for field_entry in required_fields:
            if isinstance(field_entry, dict) and "author" in field_entry:
                author_value = field_entry["author"]
                break
        assert author_value == "Asif Hussain", (
            f"Canonical author must be 'Asif Hussain' but found: {author_value}"
        )


# =============================================================================
# AC-64-G-08  AUDIT mode has violations table schema
# =============================================================================

class TestAuditModeViolationsTable:
    """AC-64-G-08: AUDIT intent produces response with violations table columns."""

    def test_audit_mode_response_has_violation_table_schema(
        self, response_template_doc: Dict[str, Any]
    ) -> None:
        """violations_table section must exist with P0/P1/P2 Severity column."""
        sections = (
            response_template_doc.get("workflow", {})
            .get("sections", {})
        )
        assert "violations_table" in sections, (
            "Response template must have a 'violations_table' section for AUDIT mode."
        )
        violations = sections["violations_table"]
        table = violations.get("table", {})
        columns = table.get("columns", [])
        column_names = [c.get("name", "") if isinstance(c, dict) else str(c) for c in columns]

        assert "Severity" in column_names, (
            f"violations_table must have 'Severity' column. Found: {column_names}"
        )
        assert "Rule" in column_names, (
            f"violations_table must have 'Rule' column. Found: {column_names}"
        )

    def test_violations_table_has_p0_p1_p2_severity_values(
        self, response_template_doc: Dict[str, Any]
    ) -> None:
        """Severity column must list P0, P1, P2 as valid values."""
        sections = response_template_doc.get("workflow", {}).get("sections", {})
        violations = sections.get("violations_table", {})
        columns = violations.get("table", {}).get("columns", [])
        severity_col = next(
            (c for c in columns if isinstance(c, dict) and c.get("name") == "Severity"),
            None,
        )
        assert severity_col is not None, "Severity column must be present"
        values = severity_col.get("values", [])
        severity_text = " ".join(str(v) for v in values)
        assert "P0" in severity_text, "Severity values must include P0"
        assert "P1" in severity_text, "Severity values must include P1"
        assert "P2" in severity_text, "Severity values must include P2"


# =============================================================================
# AC-64-G-09  All modes have progress bar definition
# =============================================================================

class TestProgressBarDefinition:
    """AC-64-G-09: progress_bar section exists with 10-block rule."""

    def test_all_modes_have_progress_bar_definition(
        self, response_template_doc: Dict[str, Any]
    ) -> None:
        """Progress bar section must be present under workflow."""
        wf = response_template_doc.get("workflow", {})
        assert "progress_bar" in wf, (
            "Response template must have a 'progress_bar' section."
        )

    def test_progress_bar_requires_exactly_10_blocks(
        self, response_template_doc: Dict[str, Any]
    ) -> None:
        """Progress bar rules must specify exactly 10 blocks."""
        progress_bar = response_template_doc.get("workflow", {}).get("progress_bar", {})
        rules = progress_bar.get("rules", [])
        rules_text = " ".join(str(r) for r in rules)
        assert "10" in rules_text, (
            "Progress bar rules must specify 'Exactly 10 blocks'. "
            f"Current rules: {rules}"
        )

    def test_progress_bar_not_in_code_block(
        self, response_template_doc: Dict[str, Any]
    ) -> None:
        """Progress bar rules must forbid fencing in code blocks."""
        progress_bar = response_template_doc.get("workflow", {}).get("progress_bar", {})
        rules = progress_bar.get("rules", [])
        rules_text = " ".join(str(r) for r in rules).lower()
        # Rule says "Never fenced in a code block"
        assert "fenced" in rules_text or "code block" in rules_text, (
            "Progress bar rules must explicitly forbid code-block fencing."
        )


# =============================================================================
# AC-64-G-10  Raw dict output is a P1 violation
# =============================================================================

class TestRawDictOutputIsP1Violation:
    """AC-64-G-10: ResponseTemplateValidator.validate_output() rejects raw dict as P1."""

    def test_raw_dict_output_is_p1_violation(self) -> None:
        """Raw dict (no header, no author) must be flagged as P1 CORE-066 violation."""
        from cortex.governance.response_template_validator import (  # noqa: PLC0415
            ResponseTemplateValidator,
        )
        validator = ResponseTemplateValidator()
        raw_output = {"status": "ok", "files_changed": 3, "violations": []}
        result = validator.validate_output(raw_output)

        assert result["valid"] is False, (
            "ResponseTemplateValidator must reject raw dict output (CORE-066)."
        )
        assert result["severity"] in ("P0", "P1"), (
            f"Raw dict is a P0/P1 violation, got severity={result['severity']}"
        )
        assert "core_066" in result.get("rule", "").lower() or "CORE-066" in str(result), (
            "Violation must reference CORE-066."
        )

    def test_validator_accepts_canonical_string_response(self) -> None:
        """ResponseTemplateValidator must accept a properly formatted string response."""
        from cortex.governance.response_template_validator import (  # noqa: PLC0415
            ResponseTemplateValidator,
        )
        validator = ResponseTemplateValidator()
        canonical = (
            "## 🔎 CORTEX Architect AUDIT\n"
            "**Author:** Asif Hussain | **Orchestrator:** AuditCoordinator ✅\n\n"
            "---\n\n"
            "## 📋 Summary\nAudit complete..."
        )
        result = validator.validate_output(canonical)
        assert result["valid"] is True, (
            f"Canonical response must pass ResponseTemplateValidator: {result}"
        )


# =============================================================================
# AC-64-G-11  Response template YAML loadable and valid
# =============================================================================

class TestResponseTemplateYamlValid:
    """AC-64-G-11: copilot-chat-response-template.yaml loads cleanly."""

    def test_response_template_yaml_loadable_and_valid(self) -> None:
        """YAML file must exist, parse without error, and have required top-level keys."""
        assert RESPONSE_TEMPLATE_YAML.exists(), (
            f"copilot-chat-response-template.yaml must exist at {RESPONSE_TEMPLATE_YAML}"
        )
        data = yaml.safe_load(RESPONSE_TEMPLATE_YAML.read_text())
        assert isinstance(data, dict), "YAML must parse to a dict"
        assert "workflow" in data, "Must have 'workflow' top-level key"
        wf = data["workflow"]
        assert wf.get("id") == "governance/copilot-chat-response-template", (
            f"Workflow id must be 'governance/copilot-chat-response-template', got: {wf.get('id')}"
        )
        assert "header" in wf, "Must have 'header' section"
        assert "progress_bar" in wf, "Must have 'progress_bar' section"
        assert "sections" in wf, "Must have 'sections' section"

    def test_holistic_file_review_gate_yaml_loadable(self) -> None:
        """holistic-file-review-gate.yaml must also load cleanly."""
        gate_yaml = GOVERNANCE_TEMPLATES / "holistic-file-review-gate.yaml"
        assert gate_yaml.exists(), f"holistic-file-review-gate.yaml must exist at {gate_yaml}"
        data = yaml.safe_load(gate_yaml.read_text())
        assert isinstance(data, dict)
        assert "workflow" in data
        assert data["workflow"].get("id") == "governance/holistic-file-review-gate"

    def test_holistic_gate_has_5_gates_defined(self) -> None:
        """holistic-file-review-gate.yaml step_4 must define GATE-1 through GATE-5."""
        gate_yaml = GOVERNANCE_TEMPLATES / "holistic-file-review-gate.yaml"
        data = yaml.safe_load(gate_yaml.read_text())
        steps = data.get("workflow", {}).get("steps", [])
        step4 = next(
            (s for s in steps if s.get("id") == "step_4_post_work_verification"), None
        )
        assert step4 is not None, "step_4_post_work_verification must exist in template"
        gates = step4.get("gates", {})
        for gate_id in ["GATE-1", "GATE-2", "GATE-3", "GATE-4", "GATE-5"]:
            assert gate_id in gates, (
                f"holistic-file-review-gate must define {gate_id} in step_4"
            )


# =============================================================================
# AC-64-G-12  Session pause banner triggered when sweep incomplete
# =============================================================================

class TestSessionPauseBanner:
    """AC-64-G-12: session_pause_banner section defined with sweep_id + resume_command."""

    def test_session_pause_banner_triggered_when_sweep_incomplete(
        self, response_template_doc: Dict[str, Any]
    ) -> None:
        """session_pause_banner must exist and include sweep_id + resume_command fields."""
        sections = response_template_doc.get("workflow", {}).get("sections", {})
        assert "session_pause_banner" in sections, (
            "Response template must have a 'session_pause_banner' section (CORE-066)."
        )
        banner = sections["session_pause_banner"]
        fmt = str(banner.get("format", ""))
        assert "{sweep_id}" in fmt, (
            "session_pause_banner format must include {sweep_id} field."
        )
        assert "resume" in fmt.lower(), (
            "session_pause_banner format must include a resume command or trigger."
        )

    def test_session_pause_banner_has_enforcement_rule(
        self, response_template_doc: Dict[str, Any]
    ) -> None:
        """session_pause_banner enforcement section must reference CORE-066."""
        sections = response_template_doc.get("workflow", {}).get("sections", {})
        banner = sections.get("session_pause_banner", {})
        enforcement = str(banner.get("enforcement", ""))
        assert "CORE-066" in enforcement, (
            "session_pause_banner enforcement must reference CORE-066."
        )

    def test_mode_section_matrix_covers_all_expected_modes(
        self, response_template_doc: Dict[str, Any]
    ) -> None:
        """mode_section_matrix must cover key execution modes including GOLDEN_TEST."""
        matrix_section = response_template_doc.get("workflow", {}).get(
            "mode_section_matrix", {}
        )
        matrix = matrix_section.get("matrix", {})
        expected_modes = ["IMPLEMENT", "FIX", "REFACTOR", "AUDIT", "GOLDEN_TEST"]
        for mode in expected_modes:
            assert mode in matrix, (
                f"mode_section_matrix must cover mode '{mode}'. "
                f"Current modes: {list(matrix.keys())}"
            )


# AC_COMPLETE: AC-64-G-RESPONSE-001 ✅ RED phase — response template golden tests written
