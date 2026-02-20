"""
Tests for Change Coherence Engine.

AC_START: AC-ENH-101-003
Description: TDD tests for ChangeCoherenceEngine
Authority: ENH-101 Stage S1 - Foundation
Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)

Test Strategy: Golden Path Truth Tests with audit log verification
- No mocks for core logic
- Real file operations
- Audit trail assertions
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from cortex.orchestrators.validation.coherence_models import (
    Change,
    ChangeType,
    CoherenceReport,
    CoherenceStatus,
    FileStructure,
    PreEditContext,
    Section,
    SectionType,
    ValidationResult,
    VersionMarker,
)

if TYPE_CHECKING:
    from cortex.orchestrators.validation.change_coherence_engine import (
        ChangeCoherenceEngine,
    )


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def temp_markdown_file() -> Path:
    """Create a temporary markdown file for testing."""
    content = """# Test Document

**Version:** 1.0 | **Updated:** 2026-02-13

## Section One

This is section one content.

## Section Two

This is section two content.

## Section Three

This is section three content.

---

*v1.0 - Test document footer*
"""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", delete=False
    ) as f:
        f.write(content)
        return Path(f.name)


@pytest.fixture
def temp_markdown_with_duplicates() -> Path:
    """Create a markdown file with duplicate sections."""
    content = """# Document with Duplicates

## Important Rules

Rule 1: Do this
Rule 2: Do that

## Other Content

Some content here.

## Important Rules

Rule 1: Do this
Rule 2: Do that

## Footer

End of document.
"""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", delete=False
    ) as f:
        f.write(content)
        return Path(f.name)


@pytest.fixture
def temp_markdown_version_mismatch() -> Path:
    """Create a markdown file with version mismatch."""
    content = """# Document

**Version:** 2.0 | **Updated:** 2026-02-13

## Content

Some content.

---

*v1.5 - Outdated footer version*
"""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", delete=False
    ) as f:
        f.write(content)
        return Path(f.name)


@pytest.fixture
def cce() -> "ChangeCoherenceEngine":
    """Create a ChangeCoherenceEngine instance."""
    from cortex.orchestrators.validation.change_coherence_engine import (
        ChangeCoherenceEngine,
    )
    return ChangeCoherenceEngine()


# ============================================================================
# TEST: ENGINE INITIALIZATION
# ============================================================================


class TestChangeCoherenceEngineInit:
    """Tests for ChangeCoherenceEngine initialization."""
    
    def test_engine_can_be_instantiated(self, cce: "ChangeCoherenceEngine") -> None:
        """Engine can be instantiated without errors."""
        assert cce is not None
        assert hasattr(cce, "pre_edit")
        assert hasattr(cce, "post_edit")
        assert hasattr(cce, "validate_coherence")
    
    def test_engine_has_audit_logger(self, cce: "ChangeCoherenceEngine") -> None:
        """Engine has audit logging capability."""
        assert hasattr(cce, "audit_log")
        assert callable(getattr(cce, "audit_log", None))


# ============================================================================
# TEST: PRE-EDIT PHASE
# ============================================================================


class TestPreEditPhase:
    """Tests for pre-edit context gathering."""
    
    def test_pre_edit_loads_full_file_content(
        self, cce: "ChangeCoherenceEngine", temp_markdown_file: Path
    ) -> None:
        """Pre-edit loads entire file content into context."""
        context = cce.pre_edit(temp_markdown_file)
        
        assert isinstance(context, PreEditContext)
        assert context.file_path == temp_markdown_file
        assert len(context.original_content) > 0
        assert "Section One" in context.original_content
        assert "Section Three" in context.original_content
    
    def test_pre_edit_detects_file_structure(
        self, cce: "ChangeCoherenceEngine", temp_markdown_file: Path
    ) -> None:
        """Pre-edit analyzes and detects file structure."""
        context = cce.pre_edit(temp_markdown_file)
        
        assert isinstance(context.structure, FileStructure)
        assert context.structure.file_type == "markdown"
        assert len(context.structure.sections) >= 3  # At least 3 H2 sections
    
    def test_pre_edit_detects_version_markers(
        self, cce: "ChangeCoherenceEngine", temp_markdown_file: Path
    ) -> None:
        """Pre-edit finds version markers in header and footer."""
        context = cce.pre_edit(temp_markdown_file)
        
        assert len(context.structure.version_markers) >= 1
        versions = [vm.version for vm in context.structure.version_markers]
        assert "1.0" in versions
    
    def test_pre_edit_detects_existing_duplicates(
        self, cce: "ChangeCoherenceEngine", temp_markdown_with_duplicates: Path
    ) -> None:
        """Pre-edit identifies already-existing duplicate sections."""
        context = cce.pre_edit(temp_markdown_with_duplicates)
        
        # Should detect "Important Rules" appears twice
        assert len(context.existing_duplicates) >= 1
        
        dup_names = [d.original_section.name for d in context.existing_duplicates]
        assert any("Important Rules" in name for name in dup_names)
    
    def test_pre_edit_logs_audit_entry(
        self, cce: "ChangeCoherenceEngine", temp_markdown_file: Path
    ) -> None:
        """Pre-edit creates audit log entry for traceability."""
        context = cce.pre_edit(temp_markdown_file)
        
        # Verify audit entry was created
        audit_entries = cce.get_audit_entries()
        assert len(audit_entries) >= 1
        
        latest = audit_entries[-1]
        assert latest["operation"] == "pre_edit"
        assert latest["file_path"] == str(temp_markdown_file)
        assert "timestamp" in latest


# ============================================================================
# TEST: POST-EDIT PHASE
# ============================================================================


class TestPostEditPhase:
    """Tests for post-edit coherence validation."""
    
    def test_post_edit_returns_coherence_report(
        self, cce: "ChangeCoherenceEngine", temp_markdown_file: Path
    ) -> None:
        """Post-edit returns a coherence report."""
        # Pre-edit first
        cce.pre_edit(temp_markdown_file)
        
        # No changes - should pass
        report = cce.post_edit(temp_markdown_file)
        
        assert isinstance(report, CoherenceReport)
        assert report.file_path == temp_markdown_file
    
    def test_post_edit_detects_new_duplicates(
        self, cce: "ChangeCoherenceEngine", temp_markdown_file: Path
    ) -> None:
        """Post-edit detects when edit introduces new duplicates."""
        # Pre-edit
        cce.pre_edit(temp_markdown_file)
        
        # Simulate adding duplicate content
        with open(temp_markdown_file, "a") as f:
            f.write("\n\n## Section One\n\nDuplicate of section one.\n")
        
        # Post-edit should detect the new duplicate
        report = cce.post_edit(temp_markdown_file)
        
        assert len(report.duplicates_found) >= 1
        assert report.status in [CoherenceStatus.WARNING, CoherenceStatus.FAILED]
    
    def test_post_edit_detects_version_inconsistency(
        self, cce: "ChangeCoherenceEngine", temp_markdown_version_mismatch: Path
    ) -> None:
        """Post-edit detects version mismatch between header and footer."""
        cce.pre_edit(temp_markdown_version_mismatch)
        
        report = cce.post_edit(temp_markdown_version_mismatch)
        
        assert report.version_consistent is False
        assert report.status in [CoherenceStatus.WARNING, CoherenceStatus.FAILED]
    
    def test_post_edit_logs_audit_entry(
        self, cce: "ChangeCoherenceEngine", temp_markdown_file: Path
    ) -> None:
        """Post-edit creates audit log entry."""
        cce.pre_edit(temp_markdown_file)
        cce.post_edit(temp_markdown_file)
        
        audit_entries = cce.get_audit_entries()
        post_edit_entries = [e for e in audit_entries if e["operation"] == "post_edit"]
        
        assert len(post_edit_entries) >= 1
        assert "coherence_status" in post_edit_entries[-1]


# ============================================================================
# TEST: COHERENCE VALIDATION
# ============================================================================


class TestCoherenceValidation:
    """Tests for validate_coherence method."""
    
    def test_validate_coherence_on_clean_file(
        self, cce: "ChangeCoherenceEngine", temp_markdown_file: Path
    ) -> None:
        """Clean file passes coherence validation."""
        with open(temp_markdown_file) as f:
            content = f.read()
        
        result = cce.validate_coherence(content, file_type="markdown")
        
        assert isinstance(result, CoherenceReport)
        assert result.status == CoherenceStatus.PASSED
    
    def test_validate_coherence_detects_duplicate_sections(
        self, cce: "ChangeCoherenceEngine", temp_markdown_with_duplicates: Path
    ) -> None:
        """Validation detects duplicate sections."""
        with open(temp_markdown_with_duplicates) as f:
            content = f.read()
        
        result = cce.validate_coherence(content, file_type="markdown")
        
        assert len(result.duplicates_found) >= 1
    
    def test_validate_coherence_returns_recommendations(
        self, cce: "ChangeCoherenceEngine", temp_markdown_with_duplicates: Path
    ) -> None:
        """Validation provides recommendations for issues found."""
        with open(temp_markdown_with_duplicates) as f:
            content = f.read()
        
        result = cce.validate_coherence(content, file_type="markdown")
        
        # Should recommend consolidating duplicates
        assert len(result.recommendations) >= 1


# ============================================================================
# TEST: CHANGE TRACKING
# ============================================================================


class TestChangeTracking:
    """Tests for tracking proposed changes."""
    
    def test_propose_change_checks_for_conflicts(
        self, cce: "ChangeCoherenceEngine", temp_markdown_file: Path
    ) -> None:
        """Proposing a change checks for conflicts with existing content."""
        context = cce.pre_edit(temp_markdown_file)
        
        # Propose adding a section that already exists
        change = Change(
            change_type=ChangeType.INSERT,
            target_line=20,
            new_content="## Section One\n\nNew content",
            description="Add new section",
        )
        
        conflict_check = cce.check_change_conflicts(context, change)
        
        assert conflict_check.has_conflict is True
        assert "Section One" in conflict_check.conflict_reason
    
    def test_propose_change_allows_non_conflicting(
        self, cce: "ChangeCoherenceEngine", temp_markdown_file: Path
    ) -> None:
        """Non-conflicting changes are allowed."""
        context = cce.pre_edit(temp_markdown_file)
        
        # Propose adding a new unique section
        change = Change(
            change_type=ChangeType.INSERT,
            target_line=20,
            new_content="## New Unique Section\n\nUnique content",
            description="Add new section",
        )
        
        conflict_check = cce.check_change_conflicts(context, change)
        
        assert conflict_check.has_conflict is False


# ============================================================================
# TEST: AUDIT TRAIL (WAVE-10 TRUTH TEST PATTERN)
# ============================================================================


class TestAuditTrail:
    """Tests verifying audit trail for traceability.
    
    Following WAVE-10 Test Quality guidelines:
    - Verify against audit logs for hard evidence
    - No mocks - real operations only
    """
    
    def test_full_workflow_creates_audit_trail(
        self, cce: "ChangeCoherenceEngine", temp_markdown_file: Path
    ) -> None:
        """Full pre_edit → post_edit workflow creates complete audit trail."""
        # Clear any previous audit entries
        cce.clear_audit_log()
        
        # Execute full workflow
        cce.pre_edit(temp_markdown_file)
        cce.post_edit(temp_markdown_file)
        
        # Verify audit trail
        entries = cce.get_audit_entries()
        
        assert len(entries) == 2
        assert entries[0]["operation"] == "pre_edit"
        assert entries[1]["operation"] == "post_edit"
        
        # Verify timestamps are in order
        assert entries[0]["timestamp"] <= entries[1]["timestamp"]
    
    def test_audit_entries_contain_file_path(
        self, cce: "ChangeCoherenceEngine", temp_markdown_file: Path
    ) -> None:
        """Audit entries include file path for traceability."""
        cce.clear_audit_log()
        cce.pre_edit(temp_markdown_file)
        
        entries = cce.get_audit_entries()
        assert entries[0]["file_path"] == str(temp_markdown_file)
    
    def test_audit_entries_contain_structure_summary(
        self, cce: "ChangeCoherenceEngine", temp_markdown_file: Path
    ) -> None:
        """Audit entries include structure summary for analysis."""
        cce.clear_audit_log()
        cce.pre_edit(temp_markdown_file)
        
        entries = cce.get_audit_entries()
        assert "sections_count" in entries[0]
        assert "version_markers_count" in entries[0]


# AC_COMPLETE: AC-ENH-101-003 ✅ TDD tests for ChangeCoherenceEngine
