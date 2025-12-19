"""
Tests for File Discovery Engine

RED PHASE: Tests written first, expecting failures.

Author: Asif Hussain
Version: 1.0.0
"""

import pytest
from pathlib import Path
from unittest.mock import Mock

from src.operations.modules.discovery.file_discovery_engine import FileDiscoveryEngine
from src.operations.modules.discovery.language_detector import LanguageDetector
from src.operations.modules.discovery.exclusion_engine import ExclusionEngine
from src.operations.modules.discovery.models import DiscoveryScope, FileInventory


@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary project with files."""
    project = tmp_path / "test_project"
    project.mkdir()
    
    # Create Python files
    (project / "main.py").write_text("print('hello')\nprint('world')")
    (project / "utils.py").write_text("def helper(): pass")
    
    # Create subdirectory with files
    src_dir = project / "src"
    src_dir.mkdir()
    (src_dir / "app.py").write_text("# Application\nclass App: pass")
    (src_dir / "config.py").write_text("CONFIG = {}")
    
    # Create test directory
    test_dir = project / "tests"
    test_dir.mkdir()
    (test_dir / "test_main.py").write_text("def test_main(): assert True")
    
    # Create other file types
    (project / "README.md").write_text("# Project")
    (project / "data.json").write_text('{"key": "value"}')
    
    # Create files to be excluded
    (project / "temp.log").write_text("log content")
    cache_dir = project / "__pycache__"
    cache_dir.mkdir()
    (cache_dir / "main.pyc").write_text("compiled")
    
    return project


@pytest.fixture
def exclusion_engine(temp_project):
    """Create exclusion engine."""
    return ExclusionEngine(project_root=temp_project)


@pytest.fixture
def discovery_engine(exclusion_engine):
    """Create file discovery engine."""
    return FileDiscoveryEngine(exclusion_engine=exclusion_engine)


class TestFileDiscoveryEngineInitialization:
    """Test engine initialization."""
    
    def test_init_creates_components(self, discovery_engine):
        """Test that initialization creates required components."""
        assert discovery_engine.exclusion_engine is not None
        assert discovery_engine.language_detector is not None
        assert isinstance(discovery_engine.language_detector, LanguageDetector)


class TestFileDiscoveryEngineDiscover:
    """Test main discover() method."""
    
    def test_discover_empty_directory(self, discovery_engine, tmp_path):
        """Test discovery in empty directory."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        scope = DiscoveryScope(root_path=empty_dir)
        
        inventory = discovery_engine.discover(scope)
        
        assert isinstance(inventory, FileInventory)
        assert inventory.total_files == 0
        assert inventory.total_size == 0
        assert inventory.total_lines == 0
    
    def test_discover_with_files(self, discovery_engine, temp_project):
        """Test discovery with actual files."""
        scope = DiscoveryScope(root_path=temp_project)
        
        inventory = discovery_engine.discover(scope)
        
        assert isinstance(inventory, FileInventory)
        assert inventory.total_files > 0
        assert inventory.total_size > 0
        assert len(inventory.languages) > 0
    
    def test_discover_excludes_patterns(self, discovery_engine, temp_project):
        """Test that exclusion patterns are applied."""
        scope = DiscoveryScope(root_path=temp_project)
        
        inventory = discovery_engine.discover(scope)
        
        # Check that .pyc and .log files are excluded
        file_names = [f.path.name for f in inventory.files]
        assert "main.pyc" not in file_names
        assert "temp.log" not in file_names
    
    def test_discover_collects_statistics(self, discovery_engine, temp_project):
        """Test that statistics are collected correctly."""
        scope = DiscoveryScope(root_path=temp_project)
        
        inventory = discovery_engine.discover(scope)
        
        assert inventory.total_files == len(inventory.files)
        assert inventory.discovery_time > 0
        assert "python" in inventory.languages


class TestFileDiscoveryEngineTraversal:
    """Test directory traversal."""
    
    def test_traverse_single_level(self, discovery_engine, tmp_path):
        """Test traversal of single directory level."""
        test_dir = tmp_path / "single"
        test_dir.mkdir()
        (test_dir / "file1.py").write_text("code")
        (test_dir / "file2.py").write_text("code")
        
        scope = DiscoveryScope(root_path=test_dir)
        
        files = list(discovery_engine._traverse_directory(scope))
        assert len(files) == 2
    
    def test_traverse_nested_directories(self, discovery_engine, tmp_path):
        """Test traversal of nested directories."""
        root = tmp_path / "nested"
        root.mkdir()
        (root / "level1").mkdir()
        (root / "level1" / "level2").mkdir()
        (root / "level1" / "level2" / "file.py").write_text("code")
        
        scope = DiscoveryScope(root_path=root)
        
        files = list(discovery_engine._traverse_directory(scope))
        assert len(files) == 1
        assert files[0].name == "file.py"
    
    def test_traverse_respects_max_depth(self, discovery_engine, tmp_path):
        """Test that max_depth is respected."""
        root = tmp_path / "depth_test"
        root.mkdir()
        (root / "level1").mkdir()
        (root / "file1.py").write_text("code")
        (root / "level1" / "level2").mkdir()
        (root / "level1" / "file2.py").write_text("code")
        (root / "level1" / "level2" / "level3").mkdir()
        (root / "level1" / "level2" / "file3.py").write_text("code")
        (root / "level1" / "level2" / "level3" / "file4.py").write_text("code")
        
        scope = DiscoveryScope(root_path=root, max_depth=1)
        
        files = list(discovery_engine._traverse_directory(scope))
        # Should get file1.py and file2.py, but not file3.py or file4.py
        assert len(files) == 2


class TestFileDiscoveryEngineMetadata:
    """Test metadata collection."""
    
    def test_collect_metadata_file_info(self, discovery_engine, tmp_path):
        """Test metadata collection for a file."""
        test_file = tmp_path / "test.py"
        test_file.write_text("line1\nline2\nline3")
        
        file_info = discovery_engine._collect_metadata(test_file, tmp_path)
        
        assert file_info.path == test_file
        assert file_info.language == "python"
        assert file_info.size_bytes > 0
    
    def test_collect_metadata_calculates_hash(self, discovery_engine, tmp_path):
        """Test that file hash is calculated."""
        test_file = tmp_path / "test.py"
        test_file.write_text("content")
        
        file_info = discovery_engine._collect_metadata(test_file, tmp_path)
        
        assert file_info.hash != ""
        assert file_info.hash != "error"
        assert len(file_info.hash) == 16  # Truncated SHA256
    
    def test_collect_metadata_counts_lines(self, discovery_engine, tmp_path):
        """Test that lines are counted correctly."""
        test_file = tmp_path / "test.py"
        test_file.write_text("line1\nline2\nline3\n")
        
        file_info = discovery_engine._collect_metadata(test_file, tmp_path)
        
        assert file_info.line_count == 3


class TestLanguageDetector:
    """Test language detector."""
    
    def test_detect_python(self):
        """Test Python detection."""
        detector = LanguageDetector()
        lang = detector.detect(Path("test.py"))
        assert lang == "python"
    
    def test_detect_csharp(self):
        """Test C# detection."""
        detector = LanguageDetector()
        lang = detector.detect(Path("test.cs"))
        assert lang == "csharp"
    
    def test_detect_javascript(self):
        """Test JavaScript detection."""
        detector = LanguageDetector()
        lang = detector.detect(Path("test.js"))
        assert lang == "javascript"
    
    def test_detect_unknown_extension(self):
        """Test detection of unknown extension."""
        detector = LanguageDetector()
        lang = detector.detect(Path("test.xyz"))
        assert lang == "unknown"


# RED PHASE SUMMARY:
# - 21 tests created defining expected behavior
# - All tests expect NotImplementedError
# - Tests cover: initialization, discovery, traversal, metadata, language detection
# - Next: GREEN phase - implement to make tests pass
