"""Tests for Phase 47 S3: Code Reference Updater."""

import pytest
from pathlib import Path
import tempfile
from cortex.orchestrators.company_separation.code_reference_updater import (
    CodeReference,
    CodeReferenceAnalyzer,
    CodeReferenceUpdater,
    MigrationPlan,
)


class TestCodeReference:
    """Test CodeReference dataclass."""

    def test_create_reference(self):
        """Test creating code reference."""
        ref = CodeReference(
            file_path="/path/to/file.py",
            line_number=42,
            original_code="from company import config",
            suggested_code="from cortex_brain import config",
            reference_type="legacy_import",
            severity="high",
        )

        assert ref.file_path == "/path/to/file.py"
        assert ref.line_number == 42
        assert ref.reference_type == "legacy_import"
        assert ref.severity == "high"


class TestCodeReferenceAnalyzer:
    """Test CodeReferenceAnalyzer class."""

    @pytest.fixture
    def temp_py_file(self):
        """Create temporary Python file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("from company.domains import config\n")
            f.write("config = 'company/config.yaml'\n")
            f.write("path = '_archive/old.py'\n")
            temp_path = f.name

        yield temp_path

        Path(temp_path).unlink()

    def test_initialize_analyzer(self):
        """Test analyzer initialization."""
        analyzer = CodeReferenceAnalyzer()

        assert analyzer.root_dir == "/Users/asifhussain/PROJECTS/CORTEX"
        assert len(analyzer.references) == 0

    def test_analyze_file_with_legacy_imports(self, temp_py_file):
        """Test analyzing file with legacy imports."""
        analyzer = CodeReferenceAnalyzer()
        refs = analyzer.analyze_file(temp_py_file)

        legacy_imports = [r for r in refs if r.reference_type == "legacy_import"]
        assert len(legacy_imports) > 0

    def test_analyze_file_with_legacy_paths(self, temp_py_file):
        """Test analyzing file with legacy path strings."""
        analyzer = CodeReferenceAnalyzer()
        refs = analyzer.analyze_file(temp_py_file)

        legacy_paths = [r for r in refs if r.reference_type == "legacy_path_string"]
        assert len(legacy_paths) > 0

    def test_analyze_file_with_archive_references(self, temp_py_file):
        """Test analyzing file with archive references."""
        analyzer = CodeReferenceAnalyzer()
        refs = analyzer.analyze_file(temp_py_file)

        archive_refs = [r for r in refs if r.reference_type == "archive_reference"]
        assert len(archive_refs) > 0

    def test_analyze_file_nonexistent(self):
        """Test analyzing nonexistent file."""
        analyzer = CodeReferenceAnalyzer()
        refs = analyzer.analyze_file("/nonexistent/file.py")

        assert len(refs) == 0

    def test_analyze_directory(self):
        """Test analyzing directory."""
        analyzer = CodeReferenceAnalyzer()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("from company.domains import config\n")

            refs = analyzer.analyze_directory(tmpdir)
            assert len(refs) > 0

    def test_get_references_by_severity(self, temp_py_file):
        """Test filtering references by severity."""
        analyzer = CodeReferenceAnalyzer()
        analyzer.analyze_file(temp_py_file)

        high_refs = analyzer.get_references_by_severity("high")
        assert len(high_refs) > 0
        assert all(r.severity == "high" for r in high_refs)

    def test_get_references_by_type(self, temp_py_file):
        """Test filtering references by type."""
        analyzer = CodeReferenceAnalyzer()
        analyzer.analyze_file(temp_py_file)

        legacy_refs = analyzer.get_references_by_type("legacy_import")
        assert len(legacy_refs) > 0
        assert all(r.reference_type == "legacy_import" for r in legacy_refs)

    def test_suggest_fix_legacy_import(self, temp_py_file):
        """Test suggesting fix for legacy import."""
        analyzer = CodeReferenceAnalyzer()
        fix = analyzer._suggest_fix("from company.domains import config", "legacy_import")

        assert "from cortex_brain" in fix

    def test_suggest_fix_legacy_path(self, temp_py_file):
        """Test suggesting fix for legacy path."""
        analyzer = CodeReferenceAnalyzer()
        fix = analyzer._suggest_fix("path = 'company/config'", "legacy_path_string")

        assert "company/" not in fix

    def test_classify_severity_high(self):
        """Test severity classification for high priority."""
        analyzer = CodeReferenceAnalyzer()

        high = analyzer._classify_severity("legacy_import")
        assert high == "high"

    def test_classify_severity_medium(self):
        """Test severity classification for medium priority."""
        analyzer = CodeReferenceAnalyzer()

        medium = analyzer._classify_severity("legacy_path_assignment")
        assert medium == "medium"

    def test_get_summary(self, temp_py_file):
        """Test getting analysis summary."""
        analyzer = CodeReferenceAnalyzer()
        analyzer.analyze_file(temp_py_file)

        summary = analyzer.get_summary()

        assert "total_references" in summary
        assert summary["total_references"] > 0
        assert "high_severity" in summary
        assert "by_type" in summary

    def test_multiple_files_analysis(self):
        """Test analyzing multiple files."""
        analyzer = CodeReferenceAnalyzer()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create multiple test files
            for i in range(3):
                test_file = Path(tmpdir) / f"test{i}.py"
                test_file.write_text("from company.domains import config\n")

            refs = analyzer.analyze_directory(tmpdir)
            assert len(refs) >= 3


class TestCodeReferenceUpdater:
    """Test CodeReferenceUpdater class."""

    def test_initialize_updater(self):
        """Test updater initialization."""
        updater = CodeReferenceUpdater()

        assert updater.resolver_path != ""
        assert len(updater.updates) == 0

    def test_apply_update_success(self):
        """Test applying successful update."""
        updater = CodeReferenceUpdater()

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("from company.domains import config\n")
            temp_path = f.name

        success = updater.apply_update(
            temp_path,
            "from company.domains import config",
            "from cortex_brain.domains import config",
        )

        assert success is True
        assert updater.get_update_count() == 1

        Path(temp_path).unlink()

    def test_apply_update_not_found(self):
        """Test applying update when original not found."""
        updater = CodeReferenceUpdater()

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("print('hello')\n")
            temp_path = f.name

        success = updater.apply_update(temp_path, "not found", "replacement")

        assert success is False

        Path(temp_path).unlink()

    def test_get_update_count(self):
        """Test getting update count."""
        updater = CodeReferenceUpdater()

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("test = 'company'\n")
            temp_path = f.name

        updater.apply_update(temp_path, "test = 'company'", "test = 'cortex'")
        assert updater.get_update_count() == 1

        Path(temp_path).unlink()

    def test_get_update_summary(self):
        """Test getting update summary."""
        updater = CodeReferenceUpdater()

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("test = 'company'\n")
            temp_path = f.name

        updater.apply_update(temp_path, "test = 'company'", "test = 'cortex'")
        summary = updater.get_update_summary()

        assert "Applied" in summary
        assert "updates" in summary

        Path(temp_path).unlink()


class TestMigrationPlan:
    """Test MigrationPlan class."""

    def test_initialize_plan(self):
        """Test plan initialization."""
        plan = MigrationPlan()

        assert len(plan.steps) == 0
        assert plan.estimated_effort == 0.0

    def test_add_step(self):
        """Test adding migration step."""
        plan = MigrationPlan()
        plan.add_step(
            1,
            "Update imports",
            ["file1.py", "file2.py"],
            2.5,
            "high",
        )

        assert len(plan.steps) == 1
        assert plan.steps[0]["step"] == 1
        assert plan.estimated_effort == 2.5

    def test_add_multiple_steps(self):
        """Test adding multiple migration steps."""
        plan = MigrationPlan()

        plan.add_step(1, "Step 1", ["file1.py"], 1.0, "high")
        plan.add_step(2, "Step 2", ["file2.py"], 2.0, "medium")
        plan.add_step(3, "Step 3", ["file3.py"], 1.5, "low")

        assert len(plan.steps) == 3
        assert plan.estimated_effort == 4.5

    def test_get_high_priority_steps(self):
        """Test getting high priority steps."""
        plan = MigrationPlan()

        plan.add_step(1, "Step 1", ["file1.py"], 1.0, "high")
        plan.add_step(2, "Step 2", ["file2.py"], 2.0, "medium")
        plan.add_step(3, "Step 3", ["file3.py"], 1.5, "high")

        high_steps = plan.get_high_priority_steps()
        assert len(high_steps) == 2

    def test_get_total_effort(self):
        """Test getting total effort."""
        plan = MigrationPlan()

        plan.add_step(1, "Step 1", ["file1.py"], 1.5, "high")
        plan.add_step(2, "Step 2", ["file2.py"], 2.5, "medium")

        total = plan.get_total_effort()
        assert total == 4.0

    def test_get_affected_files(self):
        """Test getting affected files."""
        plan = MigrationPlan()

        plan.add_step(1, "Step 1", ["file1.py", "file2.py"], 1.0, "high")
        plan.add_step(2, "Step 2", ["file2.py", "file3.py"], 2.0, "medium")

        files = plan.get_affected_files()
        assert len(files) == 3
        assert "file1.py" in files
        assert "file2.py" in files
        assert "file3.py" in files
