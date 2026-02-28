"""
Phase 59-h (GAP-59-12): Stale AC Marker Reformatting Tests
===========================================================
Verifies that the primary stale AC markers in key orchestrator files
have been converted from AC-PHASE{N}-{SEQ} to AC-{DOMAIN}-{ISO} format.

The standard: AC-{DOMAIN}-{ISO-TIMESTAMP}  (e.g. AC-REFACTOR-20260223T000000Z)
Phase-numbered markers are kept only in inline doc comments for audit trail;
file-level AC_START / AC_COMPLETE comments must use the new format.

TDD: RED → GREEN → REFACTOR (CORE-008)
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parents[2]


def _file_content(rel_path: str) -> str:
    return (REPO_ROOT / rel_path).read_text()


def _ac_markers(content: str) -> list[str]:
    """Extract all AC_START / AC_COMPLETE marker IDs from file-level comments."""
    pattern = re.compile(r"#\s*AC_(?:START|COMPLETE|ENHANCED|UPDATE):\s*(AC-[A-Z0-9_.\-]+)", re.MULTILINE)
    return pattern.findall(content)


PHASE_PATTERN = re.compile(r"AC-PHASE\d")


class TestRefactoringOrchestratorACMarkers:
    """refactoring_orchestrator.py file-level AC markers use domain format (GAP-59-12)."""

    def test_no_phase_numbered_file_level_ac_start(self):
        content = _file_content("cortex/orchestrators/domain/refactoring_orchestrator.py")
        markers = _ac_markers(content)
        bad = [m for m in markers if PHASE_PATTERN.search(m)]
        assert not bad, f"Phase-numbered file-level AC markers remain: {bad}"

    def test_ac_refactor_marker_present(self):
        content = _file_content("cortex/orchestrators/domain/refactoring_orchestrator.py")
        markers = _ac_markers(content)
        assert any("AC-REFACTOR-" in m for m in markers), (
            f"Expected AC-REFACTOR-* domain marker; got: {markers}"
        )


class TestIntentRouterACMarkers:
    """intent_router/ file-level AC markers use domain format."""

    @pytest.mark.parametrize("rel_path,expected_prefix", [
        ("cortex/orchestrators/core/intent_router/capability_matcher.py", "AC-ROUTER-CAPABILITY-"),
        ("cortex/orchestrators/core/intent_router/collaboration_coordinator.py", "AC-ROUTER-COLLAB-"),
        ("cortex/orchestrators/core/intent_router/metadata_driven_discovery.py", "AC-ROUTER-METADATA-"),
        # intent_router_enhanced.py was deleted — removed from parametrize (Check #9 vacuum)
    ])
    def test_no_phase_numbered_marker(self, rel_path, expected_prefix):
        content = _file_content(rel_path)
        markers = _ac_markers(content)
        bad = [m for m in markers if PHASE_PATTERN.search(m)]
        assert not bad, (
            f"{rel_path}: phase-numbered file-level AC markers remain: {bad}"
        )

    @pytest.mark.parametrize("rel_path,expected_prefix", [
        ("cortex/orchestrators/core/intent_router/capability_matcher.py", "AC-ROUTER-CAPABILITY-"),
        ("cortex/orchestrators/core/intent_router/collaboration_coordinator.py", "AC-ROUTER-COLLAB-"),
    ])
    def test_domain_marker_present(self, rel_path, expected_prefix):
        content = _file_content(rel_path)
        markers = _ac_markers(content)
        assert any(m.startswith(expected_prefix) for m in markers), (
            f"{rel_path}: expected domain marker with prefix '{expected_prefix}'; got {markers}"
        )


class TestWorkflowACMarkers:
    """Workflow orchestrators file-level AC markers use domain format."""

    @pytest.mark.parametrize("rel_path", [
        "cortex/orchestrators/workflow/autonomous_workflow_executor.py",
        "cortex/orchestrators/workflow/workflow_gateway.py",
        "cortex/orchestrators/workflow/workflow_composer.py",
    ])
    def test_no_phase_numbered_file_level_markers(self, rel_path):
        content = _file_content(rel_path)
        markers = _ac_markers(content)
        bad = [m for m in markers if PHASE_PATTERN.search(m)]
        assert not bad, (
            f"{rel_path}: stale phase-numbered file-level AC markers remain: {bad}"
        )


class TestIntelligenceACMarkers:
    """Intelligence orchestrators file-level AC markers use domain format."""

    @pytest.mark.parametrize("rel_path", [
        "cortex/orchestrators/intelligence/metadata_parser.py",
        "cortex/orchestrators/intelligence/agent_rules_interpreter.py",
    ])
    def test_no_phase_numbered_file_level_markers(self, rel_path):
        content = _file_content(rel_path)
        markers = _ac_markers(content)
        bad = [m for m in markers if PHASE_PATTERN.search(m)]
        assert not bad, (
            f"{rel_path}: stale phase-numbered file-level AC markers remain: {bad}"
        )


class TestACMarkerFormatStandard:
    """Verify the AC marker format standard is documented (CORE-012)."""

    def test_copilot_instructions_documents_ac_standard(self):
        content = _file_content(".github/copilot-instructions.md")
        # Standard should specify {DOMAIN} and {TIMESTAMP} format
        assert "AC-{DOMAIN}" in content or "AC_{DOMAIN}" in content or "AC-{" in content, (
            "copilot-instructions.md should document the AC marker format standard"
        )
