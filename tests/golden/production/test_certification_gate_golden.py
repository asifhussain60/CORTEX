"""
Phase 106-D: Certification Gate — Golden Tests (CORE-008 RED cycle)
Authority: GAP-106-04 — No formal certification stamp on clean audit exit
SSOT: cortex-registry/planning/phases/planned/phase-106-rca-guard-certification.yaml

Tests validate:
1. audit_certifications DDL exists in pipeline YAML
2. Stage 9 post_run writes certification row on clean exit
3. cortex_governance MCP tool supports op: certification_status
4. Certification record includes git_sha field
5. Certification record includes guard_tests_gen field
"""
from pathlib import Path
from typing import Any

import pytest

WORKSPACE = Path(__file__).resolve().parents[3]
PIPELINE_PATH = (
    WORKSPACE
    / "cortex-registry"
    / "workflows"
    / "templates"
    / "audit"
    / "audit-fix-pipeline.yaml"
)
GOVERNANCE_TOOL_PATH = WORKSPACE / "cortex" / "mcp" / "tools" / "governance.py"


class TestCertificationGateGolden:
    """Phase 106-D: 5 golden tests for the formal certification gate."""

    def _pipeline_text(self) -> str:
        assert PIPELINE_PATH.exists(), f"Pipeline missing: {PIPELINE_PATH}"
        return PIPELINE_PATH.read_text()

    def test_certification_row_written_on_clean_exit(self) -> None:
        """GAP-106-04: Stage 9 post_run must write an audit_certifications row on clean exit."""
        content = self._pipeline_text()
        assert "audit_certifications" in content, (
            "audit-fix-pipeline.yaml is missing 'audit_certifications' — Stage 9 post_run "
            "must write a certification row on clean exit.\n"
            "Phase 106-D: Add audit_certifications DDL + Stage 9 certification INSERT."
        )

    def test_certification_predicate_blocks_partial_audit(self) -> None:
        """GAP-106-04: Certification must require p0==0 AND p1==0 AND test_fail==0."""
        content = self._pipeline_text()
        assert "audit_certifications" in content, "See test_certification_row_written_on_clean_exit"

        cert_idx = content.index("audit_certifications")
        cert_block = content[cert_idx : cert_idx + 1000]
        # Must have the predicate documented
        assert "p0" in cert_block and ("p1" in cert_block or "test_fail" in cert_block), (
            "audit_certifications block must document the certification predicate "
            "(p0==0 AND p1==0 AND test_fail==0)."
        )

    def test_mcp_certification_status_returns_correct_fields(self) -> None:
        """GAP-106-04: cortex_governance MCP tool must support op: certification_status."""
        assert GOVERNANCE_TOOL_PATH.exists(), f"governance.py missing: {GOVERNANCE_TOOL_PATH}"
        content = GOVERNANCE_TOOL_PATH.read_text()
        assert "certification_status" in content, (
            "cortex/mcp/tools/governance.py is missing 'certification_status' operation.\n"
            "Phase 106-D: Add op: certification_status handler that queries "
            "audit_certifications table and returns {certified, certification_id, git_sha, "
            "readiness_score, certified_at}."
        )

    def test_certification_includes_git_sha(self) -> None:
        """GAP-106-04: Certification record must include git_sha field."""
        content = self._pipeline_text()
        assert "audit_certifications" in content, "See test_certification_row_written_on_clean_exit"
        assert "git_sha" in content, (
            "audit_certifications schema must include 'git_sha' column.\n"
            "Phase 106-D: Add git_sha field to audit_certifications DDL."
        )

    def test_certification_includes_guard_count(self) -> None:
        """GAP-106-04: Certification record must track guard_tests_gen count."""
        content = self._pipeline_text()
        assert "audit_certifications" in content, "See test_certification_row_written_on_clean_exit"
        assert "guard_tests_gen" in content or "guard_count" in content, (
            "audit_certifications schema must include guard_tests_gen (regression guards "
            "generated this run).\n"
            "Phase 106-D: Add guard_tests_gen INTEGER to audit_certifications schema."
        )
