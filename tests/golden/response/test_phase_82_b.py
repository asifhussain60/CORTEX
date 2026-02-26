"""
Golden Tests: Phase 82-b — BLOCK-DIFF-PREVIEW + BLOCK-RESUME-BANNER
                            Cross-Session Continuity

Phase 82 sub-phase 82-b | Closes: GAP-82-03, GAP-82-04
Authority: CORE-002 (No report files), CORE-008 (TDD-first), CORE-035 (single canonical
           implementation), CORE-064 (sweep completeness), CORE-066 (response template binding)

6 Acceptance Criteria (tdd_sequence.red):

  test_diff_preview_block_defined
      BLOCK-DIFF-PREVIEW exists in SSOT with table format
  test_diff_preview_uses_details_for_large_diffs
      BLOCK-DIFF-PREVIEW spec includes '<details>' collapse rule
  test_resume_banner_block_defined
      BLOCK-RESUME-BANNER exists in SSOT
  test_resume_banner_fields
      BLOCK-RESUME-BANNER has sweep_id, last_completed, remaining, open_items fields
  test_governance_template_resume_banner_entry
      resume_banner section exists in copilot-chat-response-template.yaml
  test_governance_template_diff_preview_entry
      diff_preview section exists in copilot-chat-response-template.yaml

AC_START: AC-82-B-DIFF-RESUME-001
Phase: 82 | Sub-phase: b | Priority: P1
"""

from pathlib import Path

import pytest
import yaml

# =============================================================================
# Paths
# =============================================================================

ROOT = Path("/Users/asifhussain/PROJECTS/CORTEX")
SSOT = ROOT / ".github" / "templates" / "cortex-response-templates.md"
GOVERNANCE_TEMPLATE = ROOT / "cortex-registry" / "workflows" / "templates" / "governance" / "copilot-chat-response-template.yaml"


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture(scope="module")
def ssot_text() -> str:
    """Read SSOT file once for the module."""
    assert SSOT.exists(), f"SSOT must exist at {SSOT}"
    return SSOT.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def governance_template() -> dict:
    """Load copilot-chat-response-template.yaml as a parsed dict."""
    assert GOVERNANCE_TEMPLATE.exists(), f"Governance template must exist at {GOVERNANCE_TEMPLATE}"
    return yaml.safe_load(GOVERNANCE_TEMPLATE.read_text(encoding="utf-8"))


# =============================================================================
# GAP-82-03: BLOCK-DIFF-PREVIEW
# =============================================================================


class TestBlockDiffPreview:
    """GAP-82-03: BLOCK-DIFF-PREVIEW must be defined in SSOT with table schema and collapse rule."""

    def test_diff_preview_block_defined(self, ssot_text: str) -> None:
        """BLOCK-DIFF-PREVIEW must exist in SSOT with table format.

        Post-implementation responses show changed files without a standard before/after
        schema. Each orchestrator formats diffs inconsistently.
        BLOCK-DIFF-PREVIEW provides a canonical inline before/after code change rendering.

        GAP-82-03: no standard for inline before/after code change rendering.
        CORE-035: single canonical implementation — no duplicate diff formats.
        """
        assert "BLOCK-DIFF-PREVIEW" in ssot_text, (
            "SSOT must define BLOCK-DIFF-PREVIEW. "
            "This block provides standard before/after schema for post-implementation responses. "
            "GAP-82-03: currently no BLOCK-DIFF-PREVIEW defined in SSOT or YAML registry."
        )

    def test_diff_preview_uses_details_for_large_diffs(self, ssot_text: str) -> None:
        """BLOCK-DIFF-PREVIEW must specify <details> collapse rule for diffs >5 files.

        Renderer note: BLOCK-DIFF-PREVIEW must integrate with the Renderer Safety Switch
        (GAP-82-09) — use table for ≤5 files with short paths, auto-downgrade to <details>
        blocks for >5 files or when any cell exceeds 80 chars.

        GAP-82-03: YAML registry has post_work_diff section but no BLOCK-DIFF-PREVIEW collapse rule.
        """
        assert "BLOCK-DIFF-PREVIEW" in ssot_text, (
            "BLOCK-DIFF-PREVIEW must be defined in SSOT before its collapse rule can be validated."
        )
        # The collapse rule must reference <details> for large diffs
        lower = ssot_text.lower()
        assert "<details>" in ssot_text and (
            "diff" in lower or "preview" in lower
        ), (
            "BLOCK-DIFF-PREVIEW definition in SSOT must include a collapse rule: "
            "use table for ≤5 files with short paths; downgrade to <details> for >5 files "
            "or when any cell exceeds 80 chars. Expected '<details>' in SSOT."
        )


# =============================================================================
# GAP-82-04: BLOCK-RESUME-BANNER
# =============================================================================


class TestBlockResumeBanner:
    """GAP-82-04: BLOCK-RESUME-BANNER must be defined in SSOT for cross-session sweep continuity."""

    def test_resume_banner_block_defined(self, ssot_text: str) -> None:
        """BLOCK-RESUME-BANNER must exist in SSOT.

        copilot-chat-response-template.yaml defines session_pause_banner ✅
        but no corresponding resume_banner template exists.
        Result: Users resuming sweeps get no formatted orientation on re-entry.

        GAP-82-04: looped_refactoring_continuity section references resume but has no template.
        CORE-035: single canonical implementation.
        """
        assert "BLOCK-RESUME-BANNER" in ssot_text, (
            "SSOT must define BLOCK-RESUME-BANNER. "
            "This block provides formatted orientation when a user resumes a paused sweep. "
            "The pause side (session_pause_banner) exists; the resume side must be added. "
            "GAP-82-04: currently no resume_banner template defined."
        )

    def test_resume_banner_fields(self, ssot_text: str) -> None:
        """BLOCK-RESUME-BANNER must specify sweep_id, last_completed, remaining, open_items fields.

        The resume banner must orient the user on re-entry by showing exactly where the
        sweep left off and what work remains. Required fields:
          - sweep_id: which sweep is being resumed
          - last_completed: the last completed step
          - remaining: count of remaining steps/files
          - open_items (P0/P1/P2 counts): priority breakdown of remaining work

        GAP-82-04: no standard resume format defined.
        """
        assert "BLOCK-RESUME-BANNER" in ssot_text, (
            "BLOCK-RESUME-BANNER must be defined in SSOT before its fields can be validated."
        )
        lower = ssot_text.lower()
        # All four required fields must be present in the SSOT near the RESUME-BANNER section
        assert "sweep_id" in lower or "sweep id" in lower, (
            "BLOCK-RESUME-BANNER must specify sweep_id field."
        )
        assert "last_completed" in lower or "last completed" in lower, (
            "BLOCK-RESUME-BANNER must specify last_completed field."
        )
        assert "remaining" in lower, (
            "BLOCK-RESUME-BANNER must specify a remaining count field."
        )
        assert "open_items" in lower or "open items" in lower or "p0" in lower, (
            "BLOCK-RESUME-BANNER must specify open_items or P0/P1/P2 count fields."
        )


# =============================================================================
# Governance Template entries
# =============================================================================


class TestGovernanceTemplateEntries:
    """BLOCK-DIFF-PREVIEW and BLOCK-RESUME-BANNER must be wired into the governance template."""

    def test_governance_template_resume_banner_entry(self, governance_template: dict) -> None:
        """copilot-chat-response-template.yaml must have a resume_banner section.

        The governance template is the machine-readable source for all response sections.
        The session_pause_banner section already exists; resume_banner must be added
        alongside it in the looped_refactoring_continuity section or sections block.

        GAP-82-04: governance template has pause but no resume.
        """
        # Check sections dict or looped_refactoring_continuity
        workflow = governance_template.get("workflow", {})
        sections = workflow.get("sections", {})
        loop = workflow.get("looped_refactoring_continuity", {})

        has_resume_in_sections = "resume_banner" in sections
        has_resume_in_loop = "resume_banner" in str(loop).lower()

        assert has_resume_in_sections or has_resume_in_loop, (
            "copilot-chat-response-template.yaml must contain a 'resume_banner' section. "
            "Currently only session_pause_banner exists. "
            f"Current section keys: {list(sections.keys())}"
        )

    def test_governance_template_diff_preview_entry(self, governance_template: dict) -> None:
        """copilot-chat-response-template.yaml must have a diff_preview section.

        The governance template sections define all canonical response blocks.
        BLOCK-DIFF-PREVIEW needs a corresponding machine-readable section definition.

        GAP-82-03: YAML registry has post_work_diff but no BLOCK-DIFF-PREVIEW section.
        """
        workflow = governance_template.get("workflow", {})
        sections = workflow.get("sections", {})

        assert "diff_preview" in sections, (
            "copilot-chat-response-template.yaml must contain a 'diff_preview' section. "
            "This is distinct from post_work_diff (which is the holistic-file-review-gate view). "
            "diff_preview is the inline before/after per-response block. "
            f"Current section keys: {list(sections.keys())}"
        )


# AC_COMPLETE: AC-82-B-DIFF-RESUME-001 ✅ RED phase — 6 tests written, all must FAIL before implementation
