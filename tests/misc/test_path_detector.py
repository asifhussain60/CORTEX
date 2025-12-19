"""
Tests for PathDetector

Tests repository scanning and test directory detection.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from src.setup.modules.path_detector import PathDetector


@pytest.fixture
def temp_repo():
    """Create temporary repository structure for testing."""
    temp_dir = tempfile.mkdtemp()
    repo_path = Path(temp_dir)
    
    # Create test directory with files
    tests_dir = repo_path / "tests"
    tests_dir.mkdir()
    
    # Create test files
    (tests_dir / "test_login.py").write_text("def test_login(): pass")
    (tests_dir / "test_user.py").write_text("def test_user(): pass")
    (tests_dir / "conftest.py").write_text("# pytest config")
    
    # Create pytest.ini
    (repo_path / "pytest.ini").write_text("[pytest]\ntestpaths = tests")
    
    # Create requirements.txt
    (repo_path / "requirements.txt").write_text("pytest>=8.0\nPyYAML>=6.0")
    
    yield repo_path
    
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def temp_repo_multiple_test_dirs():
    """Create repository with multiple test directories."""
    temp_dir = tempfile.mkdtemp()
    repo_path = Path(temp_dir)
    
    # Create multiple test directories
    tests1 = repo_path / "tests"
    tests1.mkdir()
    (tests1 / "test_main.py").write_text("def test_main(): pass")
    (tests1 / "conftest.py").write_text("# pytest")
    
    tests2 = repo_path / "__tests__"
    tests2.mkdir()
    (tests2 / "app.test.js").write_text("test('app', () => {});")
    
    tests3 = repo_path / "src" / "test"
    tests3.mkdir(parents=True)
    (tests3 / "test_utils.py").write_text("def test_utils(): pass")
    
    # Create config files
    (repo_path / "pytest.ini").write_text("[pytest]")
    (repo_path / "package.json").write_text('{"name": "test"}')
    
    yield repo_path
    
    shutil.rmtree(temp_dir)


class TestPathDetectorBasic:
    """Test basic PathDetector functionality."""
    
    def test_init(self, temp_repo):
        """Test detector initialization."""
        detector = PathDetector(str(temp_repo))
        
        assert detector.workspace_root == temp_repo
    
    def test_find_test_directories(self, temp_repo):
        """Test finding test directories."""
        detector = PathDetector(str(temp_repo))
        
        test_dirs = detector.find_test_directories()
        
        assert len(test_dirs) >= 1
        assert any(d["path"] == "tests" for d in test_dirs)
    
    def test_test_directory_has_metadata(self, temp_repo):
        """Test that detected directories have complete metadata."""
        detector = PathDetector(str(temp_repo))
        
        test_dirs = detector.find_test_directories()
        
        assert len(test_dirs) > 0
        
        test_dir = test_dirs[0]
        assert "path" in test_dir
        assert "absolute_path" in test_dir
        assert "test_count" in test_dir
        assert "framework" in test_dir
        assert "confidence" in test_dir
    
    def test_test_count_accuracy(self, temp_repo):
        """Test that test file count is accurate."""
        detector = PathDetector(str(temp_repo))
        
        test_dirs = detector.find_test_directories()
        
        tests_dir = next(d for d in test_dirs if d["path"] == "tests")
        assert tests_dir["test_count"] >= 2  # test_login.py, test_user.py


class TestPathDetectorFrameworkDetection:
    """Test framework detection."""
    
    def test_detect_pytest(self, temp_repo):
        """Test pytest detection."""
        detector = PathDetector(str(temp_repo))
        
        test_dirs = detector.find_test_directories()
        
        tests_dir = next(d for d in test_dirs if d["path"] == "tests")
        assert tests_dir["framework"] == "pytest"
    
    def test_detect_jest(self):
        """Test Jest detection."""
        temp_dir = tempfile.mkdtemp()
        repo_path = Path(temp_dir)
        
        try:
            # Create __tests__ with Jest files
            tests_dir = repo_path / "__tests__"
            tests_dir.mkdir()
            (tests_dir / "app.test.js").write_text("test('app', () => {});")
            
            # Create jest config
            (repo_path / "jest.config.js").write_text("module.exports = {};")
            
            detector = PathDetector(str(repo_path))
            test_dirs = detector.find_test_directories()
            
            jest_dir = next(d for d in test_dirs if "__tests__" in d["path"])
            assert jest_dir["framework"] == "jest"
        
        finally:
            shutil.rmtree(temp_dir)
    
    def test_detect_unittest(self):
        """Test unittest detection."""
        temp_dir = tempfile.mkdtemp()
        repo_path = Path(temp_dir)
        
        try:
            tests_dir = repo_path / "tests"
            tests_dir.mkdir()
            
            # Create test with unittest import
            test_file = tests_dir / "test_sample.py"
            test_file.write_text("import unittest\n\nclass TestSample(unittest.TestCase): pass")
            
            detector = PathDetector(str(repo_path))
            test_dirs = detector.find_test_directories()
            
            if len(test_dirs) > 0:
                assert test_dirs[0]["framework"] in ["unittest", "unknown"]
        
        finally:
            shutil.rmtree(temp_dir)


class TestPathDetectorConfidence:
    """Test confidence scoring."""
    
    def test_high_confidence_directory(self, temp_repo):
        """Test that well-structured test directory has high confidence."""
        detector = PathDetector(str(temp_repo))
        
        test_dirs = detector.find_test_directories()
        
        tests_dir = next(d for d in test_dirs if d["path"] == "tests")
        assert tests_dir["confidence"] >= 0.5
    
    def test_confidence_factors(self, temp_repo):
        """Test confidence calculation factors."""
        detector = PathDetector(str(temp_repo))
        
        # Tests directory with conftest.py and pytest.ini should have high confidence
        test_dirs = detector.find_test_directories()
        
        tests_dir = next(d for d in test_dirs if d["path"] == "tests")
        
        # Should have confidence from:
        # - Directory name match (tests)
        # - conftest.py present
        # - pytest.ini present
        assert tests_dir["confidence"] > 0.5


class TestPathDetectorMultipleDirectories:
    """Test handling multiple test directories."""
    
    def test_find_multiple_directories(self, temp_repo_multiple_test_dirs):
        """Test finding multiple test directories."""
        detector = PathDetector(str(temp_repo_multiple_test_dirs))
        
        test_dirs = detector.find_test_directories()
        
        assert len(test_dirs) >= 2
        
        paths = [d["path"] for d in test_dirs]
        assert "tests" in paths or "__tests__" in paths
    
    def test_sorting_by_confidence(self, temp_repo_multiple_test_dirs):
        """Test that results are sorted by confidence."""
        detector = PathDetector(str(temp_repo_multiple_test_dirs))
        
        test_dirs = detector.find_test_directories()
        
        if len(test_dirs) >= 2:
            # First should have highest confidence
            assert test_dirs[0]["confidence"] >= test_dirs[1]["confidence"]


class TestPathDetectorSuggestions:
    """Test path suggestions."""
    
    def test_suggest_existing_directory(self, temp_repo):
        """Test suggesting existing test directory."""
        detector = PathDetector(str(temp_repo))
        
        suggestion = detector.suggest_test_directory()
        
        assert suggestion == "tests"
    
    def test_suggest_default_for_python(self):
        """Test default suggestion for Python project."""
        temp_dir = tempfile.mkdtemp()
        repo_path = Path(temp_dir)
        
        try:
            # Create Python project markers
            (repo_path / "requirements.txt").write_text("pytest")
            
            detector = PathDetector(str(repo_path))
            suggestion = detector.suggest_test_directory()
            
            assert suggestion == "tests"
        
        finally:
            shutil.rmtree(temp_dir)
    
    def test_suggest_default_for_javascript(self):
        """Test default suggestion for JavaScript project."""
        temp_dir = tempfile.mkdtemp()
        repo_path = Path(temp_dir)
        
        try:
            # Create JavaScript project marker
            (repo_path / "package.json").write_text('{"name": "test"}')
            
            detector = PathDetector(str(repo_path))
            suggestion = detector.suggest_test_directory()
            
            assert suggestion == "__tests__"
        
        finally:
            shutil.rmtree(temp_dir)


class TestPathDetectorDocuments:
    """Test document directory detection."""
    
    def test_find_documents_directories_not_exists(self, temp_repo):
        """Test finding documents when cortex-brain doesn't exist."""
        detector = PathDetector(str(temp_repo))
        
        doc_dirs = detector.find_documents_directories()
        
        assert isinstance(doc_dirs, dict)
        assert all(v is None for v in doc_dirs.values())
    
    def test_find_documents_directories_exists(self):
        """Test finding existing document directories."""
        temp_dir = tempfile.mkdtemp()
        repo_path = Path(temp_dir)
        
        try:
            # Create cortex-brain structure
            brain_path = repo_path / "cortex-brain" / "documents"
            brain_path.mkdir(parents=True)
            
            (brain_path / "reports").mkdir()
            (brain_path / "analysis").mkdir()
            
            detector = PathDetector(str(repo_path))
            doc_dirs = detector.find_documents_directories()
            
            assert "reports" in doc_dirs
            assert doc_dirs["reports"] is not None
            # Normalize path for cross-platform compatibility
            assert "reports" in doc_dirs["reports"].replace("\\", "/")
        
        finally:
            shutil.rmtree(temp_dir)


class TestPathDetectorComprehensiveScan:
    """Test comprehensive repository scan."""
    
    def test_scan_repository(self, temp_repo):
        """Test complete repository scan."""
        detector = PathDetector(str(temp_repo))
        
        results = detector.scan_repository()
        
        assert "workspace_root" in results
        assert "test_directories" in results
        assert "suggested_test_directory" in results
        assert "document_directories" in results
        assert "recommendations" in results
    
    def test_scan_recommendations(self, temp_repo):
        """Test that scan generates recommendations."""
        detector = PathDetector(str(temp_repo))
        
        results = detector.scan_repository()
        
        assert isinstance(results["recommendations"], list)
        assert len(results["recommendations"]) > 0
    
    def test_scan_with_multiple_directories(self, temp_repo_multiple_test_dirs):
        """Test scan with multiple test directories."""
        detector = PathDetector(str(temp_repo_multiple_test_dirs))
        
        results = detector.scan_repository()
        
        assert len(results["test_directories"]) >= 2
        assert len(results["recommendations"]) > 0


class TestPathDetectorEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_repository(self):
        """Test scanning empty repository."""
        temp_dir = tempfile.mkdtemp()
        
        try:
            detector = PathDetector(temp_dir)
            test_dirs = detector.find_test_directories()
            
            assert isinstance(test_dirs, list)
            assert len(test_dirs) == 0
        
        finally:
            shutil.rmtree(temp_dir)
    
    def test_max_depth_limit(self, temp_repo):
        """Test that max_depth parameter limits search."""
        # Create deeply nested test directory
        deep_dir = temp_repo / "a" / "b" / "c" / "d" / "tests"
        deep_dir.mkdir(parents=True)
        (deep_dir / "test_deep.py").write_text("def test_deep(): pass")
        
        detector = PathDetector(str(temp_repo))
        
        # With max_depth=3, should not find deeply nested test
        test_dirs = detector.find_test_directories(max_depth=3)
        
        deep_paths = [d["path"] for d in test_dirs if "a/b/c/d/tests" in d["path"]]
        assert len(deep_paths) == 0
