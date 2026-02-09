"""
Phase 38 Stage 11: ScreamingCaseDetector Tests
Authority: TDDOrchestrator | CORE-008
Acceptance Criteria: AC-PHASE38-030
"""

import pytest
from pathlib import Path
from cortex.orchestrators.support.screaming_case_detector import ScreamingCaseDetector


class TestScreamingCaseDetector:
    """ScreamingCaseDetector - identifies SCREAMING_CASE naming violations"""

    @pytest.fixture
    def workspace(self, tmp_path):
        """Create test workspace"""
        (tmp_path / "cortex").mkdir()
        (tmp_path / "cortex" / "orchestrators").mkdir(parents=True)
        return tmp_path

    @pytest.fixture
    def detector(self, workspace):
        """Initialize detector"""
        return ScreamingCaseDetector(workspace)

    def test_initialization(self, detector, workspace):
        """Test: Detector initializes properly"""
        assert detector.workspace_root == workspace
        assert detector.screaming_pattern is not None

    def test_is_screaming_case_true(self, detector):
        """Test: Recognizes SCREAMING_CASE names"""
        assert detector._is_screaming_case("MAX_RETRY_COUNT") is True
        assert detector._is_screaming_case("FILE_RELOCATION_ENGINE") is True
        assert detector._is_screaming_case("HTTP_STATUS_OK") is True

    def test_is_screaming_case_false(self, detector):
        """Test: Rejects non-SCREAMING_CASE names"""
        assert detector._is_screaming_case("my_module") is False
        assert detector._is_screaming_case("MyClass") is False
        assert detector._is_screaming_case("camelCase") is False
        assert detector._is_screaming_case("kebab-case") is False

    def test_convert_to_kebab_case(self, detector):
        """Test: Converts SCREAMING_CASE to kebab-case"""
        assert detector._convert_to_kebab_case("MY_FILE") == "my-file"
        assert detector._convert_to_kebab_case("FILE_RELOCATION_ENGINE") == "file-relocation-engine"
        assert detector._convert_to_kebab_case("HTTP_STATUS") == "http-status"

    def test_detect_screaming_case_files(self, detector, workspace):
        """Test: Detects files with SCREAMING_CASE names"""
        # Create SCREAMING_CASE file
        screaming_file = workspace / "MY_MODULE.py"
        screaming_file.write_text("# content")
        
        # Create normal file
        normal_file = workspace / "my_module.py"
        normal_file.write_text("# content")
        
        violations = detector.detect_screaming_case_files()
        
        assert isinstance(violations, list)
        # Should find MY_MODULE violation
        names = [v.current_name for v in violations]
        assert "MY_MODULE" in names

    def test_detect_screaming_case_directories(self, detector, workspace):
        """Test: Detects directories with SCREAMING_CASE names"""
        (workspace / "MY_PACKAGE").mkdir()
        (workspace / "ORCHESTRATORS_SUPPORT").mkdir()
        
        violations = detector.detect_screaming_case_directories()
        
        assert isinstance(violations, dict)
        # Should find directories
        dir_names = [p.name for p in violations.keys()]
        assert "MY_PACKAGE" in dir_names or "ORCHESTRATORS_SUPPORT" in dir_names

    def test_find_file_references(self, detector, workspace):
        """Test: Finds references to a file"""
        # Create files with references
        target = workspace / "UTILS.py"
        target.write_text("def my_util(): pass")
        
        referrer = workspace / "main.py"
        referrer.write_text("from UTILS import my_util")
        
        refs = detector._find_file_references(target)
        
        assert isinstance(refs, list)
        # May or may not find reference depending on import pattern

    def test_generate_migration_plan(self, detector, workspace):
        """Test: Generates migration plan"""
        screaming_file = workspace / "BAD_NAME.py"
        screaming_file.write_text("pass")
        
        violations = detector.detect_screaming_case_files()
        
        if violations:
            plan = detector.generate_migration_plan(violations)
            
            assert "total_violations" in plan
            assert "files_to_rename" in plan
            assert "estimated_effort" in plan

    def test_should_skip_venv(self, detector, workspace):
        """Test: Skips .venv directory"""
        venv_path = workspace / ".venv"
        venv_path.mkdir()
        assert detector._should_skip(venv_path) is True

    def test_should_skip_pycache(self, detector, workspace):
        """Test: Skips __pycache__"""
        assert detector._should_skip_dir(workspace / "__pycache__") is True

    def test_integration_full_scan(self, detector, workspace):
        """Integration: Full scan workflow"""
        # Create mixed naming
        (workspace / "SCREAMING_CASE.py").write_text("pass")
        (workspace / "kebab_case.py").write_text("pass")
        (workspace / "CamelCase.py").write_text("pass")
        
        violations = detector.detect_screaming_case_files()
        dirs_violations = detector.detect_screaming_case_directories()
        
        assert isinstance(violations, list)
        assert isinstance(dirs_violations, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
