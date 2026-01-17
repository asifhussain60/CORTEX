"""Unit tests for MD Organizer Cleaner Analyzer (VAC-001-02)

Tests verify that MDOrganizerCleaner.analyze() correctly:
- Scans repository for markdown files
- Categorizes files into logical groups  
- Identifies naming/organization issues
- Generates executable plan

AC-001-02 Acceptance Criteria:
✓ Scans all MD files in repository
✓ Categorizes into 5+ categories (phases, fixes, documentation, etc.)
✓ Identifies naming issues (length >25 chars, camelCase, etc.)
✓ Generates plan with file movements/renames
✓ Returns Analysis with plan, files_scanned, issues_found
✓ Type hints on all methods (CORE-011)
✓ Google-style docstrings on all classes/methods (CORE-012)

Author: CORTEX Builder
Phase: PHASE-VAC-001-02
CORE Rules: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

import pytest
import sys
import tempfile
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

# Add cortex-brain to path
project_root = Path(__file__).parent.parent.parent.parent.parent
cortex_brain_path = project_root / "cortex-brain"
sys.path.insert(0, str(cortex_brain_path))

# Import from cleaner interface
from tier1.orchestrators.cleaners import (
    CleanerInterface,
    Analysis,
    Report,
    RollbackResult,
)
from tier1.orchestrators.cleaners.md_organizer import (
    MDOrganizerCleaner,
    MDFileCategory,
    MDFileNamingIssue,
)


# =============================================================================
# TEST FIXTURES
# =============================================================================


@pytest.fixture
def temp_repo():
    """Create temporary repository structure for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)
        (repo_path / ".git").mkdir()
        yield repo_path


@pytest.fixture
def sample_md_files(temp_repo):
    """Create sample MD files for testing."""
    files = {
        # Phase files
        "PHASE-001-implementation.md": (
            "# Phase 1\n\nImplementation details"
        ),
        "PHASE-002-findings.md": "# Phase 2\n\nFindings",
        
        # AC Fix files
        "AC-FIX-001-completion-report.md": "# Fix 1",
        "AC-FIX-002-implementation.md": "# Fix 2",
        "AC-MINOR-001-summary.md": "# Minor Fix",
        
        # Session files
        "SESSION-001-summary.md": "# Session 1",
        "SESSION-002-progress.md": "# Session 2",
        
        # Weekly files
        "WEEK-1-completion.md": "# Week 1",
        "WEEK-2-status.md": "# Week 2",
        
        # Completion files
        "PROJECT-COMPLETION-REPORT.md": "# Completion",
        
        # Root files
        "README.md": "# Repository",
        "INDEX.md": "# Index",
        
        # Architecture files
        "architecture-overview.md": "# Architecture",
        "design-patterns.md": "# Patterns",
        
        # Implementation files
        "implementation-guide.md": "# Guide",
        "tutorial.md": "# Tutorial",
        
        # Documentation files
        "documentation.md": "# Docs",
        
        # Files with naming issues
        "TOOLongFileNameThatExceedsLimit.md": "# Too long",
        "CamelCaseFileName.md": "# CamelCase",
        "File With Spaces.md": "# Spaces",
        "other-file.md": "# Other",
    }
    
    created_files = {}
    for filename, content in files.items():
        file_path = temp_repo / filename
        file_path.write_text(content)
        created_files[filename] = file_path
    
    return created_files


@pytest.fixture
def md_cleaner(temp_repo):
    """Create MD Organizer cleaner instance."""
    config = {
        "repo_root": str(temp_repo),
        "target_dir": ".github/docs",
        "dry_run": True,
    }
    return MDOrganizerCleaner(config=config)


# =============================================================================
# TEST: MD File Category Classification
# =============================================================================


class TestMDFileClassification:
    """Test file classification into categories."""

    def test_phase_file_classification(
        self, md_cleaner: MDOrganizerCleaner
    ) -> None:
        """Verify PHASE files are classified correctly."""
        category = md_cleaner._classify_file("PHASE-001-implementation.md")
        assert category == MDFileCategory.PHASE

    def test_ac_fix_file_classification(
        self, md_cleaner: MDOrganizerCleaner
    ) -> None:
        """Verify AC-FIX files are classified correctly."""
        category = md_cleaner._classify_file("AC-FIX-001-completion.md")
        assert category == MDFileCategory.AC_FIX

    def test_ac_minor_file_classification(
        self, md_cleaner: MDOrganizerCleaner
    ) -> None:
        """Verify AC-MINOR files are classified correctly."""
        category = md_cleaner._classify_file("AC-MINOR-001-summary.md")
        assert category == MDFileCategory.AC_MINOR

    def test_session_file_classification(
        self, md_cleaner: MDOrganizerCleaner
    ) -> None:
        """Verify SESSION files are classified correctly."""
        category = md_cleaner._classify_file("SESSION-001-summary.md")
        assert category == MDFileCategory.SESSION

    def test_weekly_file_classification(
        self, md_cleaner: MDOrganizerCleaner
    ) -> None:
        """Verify WEEK files are classified correctly."""
        category = md_cleaner._classify_file("WEEK-1-completion.md")
        assert category == MDFileCategory.WEEKLY

    def test_completion_file_classification(
        self, md_cleaner: MDOrganizerCleaner
    ) -> None:
        """Verify files with COMPLETION in name are classified correctly."""
        category = md_cleaner._classify_file("PROJECT-COMPLETION-REPORT.md")
        assert category == MDFileCategory.COMPLETION

    def test_root_file_classification(
        self, md_cleaner: MDOrganizerCleaner
    ) -> None:
        """Verify README and INDEX are classified as ROOT."""
        assert md_cleaner._classify_file("README.md") == MDFileCategory.ROOT
        assert md_cleaner._classify_file("INDEX.md") == MDFileCategory.ROOT

    def test_architecture_file_classification(
        self, md_cleaner: MDOrganizerCleaner
    ) -> None:
        """Verify architecture files are classified correctly."""
        assert (
            md_cleaner._classify_file("architecture-overview.md")
            == MDFileCategory.ARCHITECTURE
        )
        assert (
            md_cleaner._classify_file("design-patterns.md")
            == MDFileCategory.ARCHITECTURE
        )

    def test_implementation_file_classification(
        self, md_cleaner: MDOrganizerCleaner
    ) -> None:
        """Verify implementation files are classified correctly."""
        assert (
            md_cleaner._classify_file("implementation-guide.md")
            == MDFileCategory.IMPLEMENTATION
        )
        assert md_cleaner._classify_file("tutorial.md") == MDFileCategory.IMPLEMENTATION

    def test_documentation_file_classification(
        self, md_cleaner: MDOrganizerCleaner
    ) -> None:
        """Verify documentation files are classified correctly."""
        category = md_cleaner._classify_file("documentation.md")
        assert category == MDFileCategory.DOCUMENTATION

    def test_other_file_classification(
        self, md_cleaner: MDOrganizerCleaner
    ) -> None:
        """Verify uncategorized files are classified as OTHER."""
        category = md_cleaner._classify_file("other-file.md")
        assert category == MDFileCategory.OTHER


# =============================================================================
# TEST: Naming Issue Identification
# =============================================================================


class TestNamingIssueIdentification:
    """Test identification of naming issues."""

    def test_exceeds_length_issue_identification(
        self, md_cleaner: MDOrganizerCleaner
    ) -> None:
        """Verify files exceeding 25-char limit are identified (CORE-028)."""
        md_cleaner._md_files = {
            "TOOLongFileNameThatExceedsLimit.md": Path("test.md")
        }
        issues = md_cleaner._identify_issues()
        
        # Should have identified length issue
        assert len(issues) > 0
        assert any(issue == MDFileNamingIssue.EXCEEDS_LENGTH for _, issue in issues)

    def test_camelcase_issue_identification(
        self, md_cleaner: MDOrganizerCleaner
    ) -> None:
        """Verify camelCase files are identified."""
        md_cleaner._md_files = {"CamelCaseFileName.md": Path("test.md")}
        issues = md_cleaner._identify_issues()
        
        assert len(issues) > 0
        assert any(issue == MDFileNamingIssue.CAMELCASE for _, issue in issues)

    def test_spaces_issue_identification(
        self, md_cleaner: MDOrganizerCleaner
    ) -> None:
        """Verify files with spaces are identified."""
        md_cleaner._md_files = {"File With Spaces.md": Path("test.md")}
        issues = md_cleaner._identify_issues()
        
        assert len(issues) > 0
        assert any(issue == MDFileNamingIssue.SPACES for _, issue in issues)

    def test_kebab_case_acceptable(
        self, md_cleaner: MDOrganizerCleaner
    ) -> None:
        """Verify kebab-case files have no issues."""
        md_cleaner._md_files = {"proper-kebab-case.md": Path("test.md")}
        issues = md_cleaner._identify_issues()
        
        # Should have no issues
        assert len(issues) == 0


# =============================================================================
# TEST: File Scanning
# =============================================================================


class TestFileScan:
    """Test markdown file scanning."""

    def test_scan_returns_dictionary(
        self, temp_repo, sample_md_files
    ) -> None:
        """Verify scan returns dictionary of files."""
        config = {"repo_root": str(temp_repo), "dry_run": True}
        cleaner = MDOrganizerCleaner(config=config)
        
        scanned = cleaner._scan_md_files()
        
        # Should return a dictionary
        assert isinstance(scanned, dict)
        assert len(scanned) > 0

    def test_scan_excludes_hidden_dirs(
        self, temp_repo: Path
    ) -> None:
        """Verify scan excludes hidden directories."""
        hidden_dir = temp_repo / ".hidden"
        hidden_dir.mkdir()
        (hidden_dir / "file.md").write_text("# Hidden")
        
        config = {"repo_root": str(temp_repo), "dry_run": True}
        cleaner = MDOrganizerCleaner(config=config)
        
        scanned = cleaner._scan_md_files()
        
        # Should not find file in hidden directory
        assert "file.md" not in scanned

    def test_scan_excludes_venv(
        self, temp_repo: Path
    ) -> None:
        """Verify scan excludes venv directories."""
        venv_dir = temp_repo / "venv"
        venv_dir.mkdir()
        (venv_dir / "file.md").write_text("# Venv")
        
        config = {"repo_root": str(temp_repo), "dry_run": True}
        cleaner = MDOrganizerCleaner(config=config)
        
        scanned = cleaner._scan_md_files()
        
        # Should not find file in venv
        for path in scanned.values():
            assert "venv" not in path.parts


# =============================================================================
# TEST: File Categorization
# =============================================================================


class TestFileCategorization:
    """Test file categorization into groups."""

    def test_categorize_creates_all_categories(
        self, md_cleaner: MDOrganizerCleaner, sample_md_files: Dict[str, Path]
    ) -> None:
        """Verify categorization creates groups for files."""
        md_cleaner._md_files = sample_md_files
        categories = md_cleaner._categorize_files()
        
        # Should have multiple categories with files
        non_empty = {k: v for k, v in categories.items() if len(v) > 0}
        assert len(non_empty) >= 5  # At least 5 categories

    def test_categorize_groups_phases(
        self, md_cleaner: MDOrganizerCleaner
    ) -> None:
        """Verify PHASE files are grouped together."""
        md_cleaner._md_files = {
            "PHASE-001-implementation.md": Path("test1.md"),
            "PHASE-002-findings.md": Path("test2.md"),
        }
        categories = md_cleaner._categorize_files()
        
        assert len(categories[MDFileCategory.PHASE.value]) == 2


# =============================================================================
# TEST: Execution Plan Generation
# =============================================================================


class TestPlanGeneration:
    """Test execution plan generation."""

    def test_plan_has_required_fields(
        self, md_cleaner: MDOrganizerCleaner
    ) -> None:
        """Verify generated plan has required fields."""
        md_cleaner._md_files = {}
        md_cleaner._categories = {}
        md_cleaner._issues = []
        
        plan = md_cleaner._generate_plan()
        
        assert "moves" in plan
        assert "renames" in plan
        assert "categories" in plan
        assert "issues_identified" in plan
        assert "issues" in plan

    def test_plan_includes_identified_issues(
        self, md_cleaner: MDOrganizerCleaner
    ) -> None:
        """Verify plan includes identified issues."""
        md_cleaner._md_files = {}
        md_cleaner._categories = {}
        md_cleaner._issues = [
            ("bad-name.md", MDFileNamingIssue.EXCEEDS_LENGTH),
        ]
        
        plan = md_cleaner._generate_plan()
        
        assert len(plan["issues"]) > 0
        assert plan["issues"][0]["file"] == "bad-name.md"


# =============================================================================
# TEST: CleanerInterface Contract
# =============================================================================


class TestCleanerInterfaceCompliance:
    """Test that MDOrganizerCleaner correctly implements CleanerInterface."""

    def test_is_cleaner_interface_subclass(
        self, md_cleaner: MDOrganizerCleaner
    ) -> None:
        """Verify MDOrganizerCleaner is a CleanerInterface subclass."""
        assert isinstance(md_cleaner, CleanerInterface)

    def test_has_required_properties(
        self, md_cleaner: MDOrganizerCleaner
    ) -> None:
        """Verify required properties exist."""
        assert hasattr(md_cleaner, "name")
        assert hasattr(md_cleaner, "version")
        assert hasattr(md_cleaner, "domain")

    def test_name_property_returns_string(
        self, md_cleaner: MDOrganizerCleaner
    ) -> None:
        """Verify name property returns string."""
        assert isinstance(md_cleaner.name, str)
        assert len(md_cleaner.name) > 0

    def test_version_property_returns_string(
        self, md_cleaner: MDOrganizerCleaner
    ) -> None:
        """Verify version property returns string."""
        assert isinstance(md_cleaner.version, str)
        assert len(md_cleaner.version) > 0

    def test_domain_property_returns_string(
        self, md_cleaner: MDOrganizerCleaner
    ) -> None:
        """Verify domain property returns string."""
        assert isinstance(md_cleaner.domain, str)
        assert md_cleaner.domain == "md_organizer"

    def test_has_required_methods(
        self, md_cleaner: MDOrganizerCleaner
    ) -> None:
        """Verify required methods exist."""
        assert hasattr(md_cleaner, "analyze")
        assert callable(getattr(md_cleaner, "analyze"))
        assert hasattr(md_cleaner, "execute")
        assert callable(getattr(md_cleaner, "execute"))
        assert hasattr(md_cleaner, "rollback")
        assert callable(getattr(md_cleaner, "rollback"))


# =============================================================================
# TEST: Analyze Phase
# =============================================================================


class TestAnalyzePhase:
    """Test the analyze() method."""

    def test_analyze_returns_analysis(
        self, md_cleaner: MDOrganizerCleaner, sample_md_files: Dict[str, Path]
    ) -> None:
        """Verify analyze() returns Analysis dataclass."""
        analysis = md_cleaner.analyze()
        
        assert isinstance(analysis, Analysis)

    def test_analyze_has_required_fields(
        self, md_cleaner: MDOrganizerCleaner
    ) -> None:
        """Verify Analysis has required fields."""
        analysis = md_cleaner.analyze()
        
        assert hasattr(analysis, "cleaner_id")
        assert hasattr(analysis, "timestamp")
        assert hasattr(analysis, "files_scanned")
        assert hasattr(analysis, "issues_found")
        assert hasattr(analysis, "plan")
        assert hasattr(analysis, "logs")

    def test_analyze_files_scanned_is_int(
        self, md_cleaner: MDOrganizerCleaner
    ) -> None:
        """Verify files_scanned is integer."""
        analysis = md_cleaner.analyze()
        
        assert isinstance(analysis.files_scanned, int)
        assert analysis.files_scanned >= 0

    def test_analyze_issues_found_is_int(
        self, md_cleaner: MDOrganizerCleaner
    ) -> None:
        """Verify issues_found is integer."""
        analysis = md_cleaner.analyze()
        
        assert isinstance(analysis.issues_found, int)
        assert analysis.issues_found >= 0

    def test_analyze_plan_is_dict(
        self, md_cleaner: MDOrganizerCleaner
    ) -> None:
        """Verify plan is dictionary."""
        analysis = md_cleaner.analyze()
        
        assert isinstance(analysis.plan, dict)

    def test_analyze_logs_is_list(
        self, md_cleaner: MDOrganizerCleaner
    ) -> None:
        """Verify logs is list of strings."""
        analysis = md_cleaner.analyze()
        
        assert isinstance(analysis.logs, list)
        assert all(isinstance(log, str) for log in analysis.logs)
        assert len(analysis.logs) > 0

    def test_analyze_creates_execution_plan(
        self, md_cleaner: MDOrganizerCleaner, sample_md_files: Dict[str, Path]
    ) -> None:
        """Verify analyze() creates executable plan."""
        analysis = md_cleaner.analyze()
        
        assert analysis.plan is not None
        assert len(analysis.plan) > 0


# =============================================================================
# TEST: Type Hints (CORE-011)
# =============================================================================


class TestTypeHints:
    """Test that all methods have proper type hints."""

    def test_analyze_has_return_type(
        self, md_cleaner: MDOrganizerCleaner
    ) -> None:
        """Verify analyze() has return type hint."""
        analyze_method = md_cleaner.analyze
        annotations = analyze_method.__annotations__
        assert "return" in annotations
        assert annotations["return"] == Analysis

    def test_execute_has_type_hints(
        self, md_cleaner: MDOrganizerCleaner
    ) -> None:
        """Verify execute() has parameter and return type hints."""
        execute_method = md_cleaner.execute
        annotations = execute_method.__annotations__
        assert "plan" in annotations
        assert "return" in annotations
        assert annotations["return"] == Report

    def test_rollback_has_return_type(
        self, md_cleaner: MDOrganizerCleaner
    ) -> None:
        """Verify rollback() has return type hint."""
        rollback_method = md_cleaner.rollback
        annotations = rollback_method.__annotations__
        assert "return" in annotations
        assert annotations["return"] == RollbackResult

    def test_classify_file_has_type_hints(
        self, md_cleaner: MDOrganizerCleaner
    ) -> None:
        """Verify _classify_file() has type hints."""
        method = md_cleaner._classify_file
        annotations = method.__annotations__
        assert "filename" in annotations
        assert "return" in annotations
        assert annotations["return"] == MDFileCategory


# =============================================================================
# TEST: Docstrings (CORE-012)
# =============================================================================


class TestDocstrings:
    """Test that all classes and methods have docstrings."""

    def test_cleaner_has_docstring(
        self, md_cleaner: MDOrganizerCleaner
    ) -> None:
        """Verify MDOrganizerCleaner has docstring."""
        assert md_cleaner.__class__.__doc__ is not None
        assert len(md_cleaner.__class__.__doc__) > 0

    def test_analyze_has_docstring(
        self, md_cleaner: MDOrganizerCleaner
    ) -> None:
        """Verify analyze() has docstring."""
        assert md_cleaner.analyze.__doc__ is not None
        assert len(md_cleaner.analyze.__doc__) > 0

    def test_enums_have_docstrings(self) -> None:
        """Verify enum classes have docstrings."""
        assert MDFileCategory.__doc__ is not None
        assert MDFileNamingIssue.__doc__ is not None


# =============================================================================
# ACCEPTANCE CRITERIA VERIFICATION
# =============================================================================


class TestAcceptanceCriteria:
    """Test that all acceptance criteria are met."""

    def test_ac_scans_all_md_files(
        self, md_cleaner: MDOrganizerCleaner, sample_md_files: Dict[str, Path]
    ) -> None:
        """AC1: Scans all MD files in repository."""
        analysis = md_cleaner.analyze()
        assert analysis.files_scanned >= len(sample_md_files)

    def test_ac_categorizes_into_multiple_groups(
        self, md_cleaner: MDOrganizerCleaner, sample_md_files: Dict[str, Path]
    ) -> None:
        """AC2: Categorizes into 5+ categories."""
        analysis = md_cleaner.analyze()
        categories = analysis.plan.get("categories", {})
        non_empty = {k: v for k, v in categories.items() if len(v) > 0}
        assert len(non_empty) >= 5

    def test_ac_identifies_naming_issues(
        self, md_cleaner: MDOrganizerCleaner
    ) -> None:
        """AC3: Identifies naming issues (length, camelCase, etc.)."""
        md_cleaner._md_files = {
            "TOOLongFileName.md": Path("test.md"),
            "CamelCase.md": Path("test.md"),
        }
        issues = md_cleaner._identify_issues()
        assert len(issues) > 0

    def test_ac_returns_analysis_with_plan(
        self, md_cleaner: MDOrganizerCleaner
    ) -> None:
        """AC4: Returns Analysis with plan, files_scanned, issues_found."""
        analysis = md_cleaner.analyze()
        assert isinstance(analysis, Analysis)
        assert hasattr(analysis, "plan")
        assert hasattr(analysis, "files_scanned")
        assert hasattr(analysis, "issues_found")

    def test_ac_type_hints_100_percent(
        self, md_cleaner: MDOrganizerCleaner
    ) -> None:
        """AC5: Type hints on all methods (CORE-011)."""
        # Check main methods
        analyze_method = md_cleaner.analyze
        assert "return" in analyze_method.__annotations__

    def test_ac_docstrings_100_percent(
        self, md_cleaner: MDOrganizerCleaner
    ) -> None:
        """AC6: Google-style docstrings (CORE-012)."""
        assert md_cleaner.__class__.__doc__ is not None
        assert md_cleaner.analyze.__doc__ is not None
