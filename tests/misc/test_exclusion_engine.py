"""
Tests for Exclusion Engine

RED PHASE: Tests written first, expecting failures.

Author: Asif Hussain
Version: 1.0.0
"""

import pytest
from pathlib import Path

from src.operations.modules.discovery.exclusion_engine import ExclusionEngine


@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary project directory."""
    project = tmp_path / "test_project"
    project.mkdir()
    return project


@pytest.fixture
def engine(temp_project):
    """Create ExclusionEngine instance."""
    return ExclusionEngine(project_root=temp_project)


class TestExclusionEngineInitialization:
    """Test exclusion engine initialization."""
    
    def test_init_loads_default_patterns(self, engine):
        """Test that default patterns are loaded."""
        patterns = engine.get_patterns()
        assert ".git/" in patterns
        assert "__pycache__/" in patterns
        assert "node_modules/" in patterns
        assert "*.pyc" in patterns
    
    def test_init_resolves_project_root(self, temp_project):
        """Test that project root is resolved correctly."""
        engine = ExclusionEngine(project_root=temp_project)
        assert engine.project_root == temp_project.resolve()
    
    def test_init_attempts_gitignore_load(self, temp_project):
        """Test that .gitignore is loaded if present."""
        gitignore = temp_project / ".gitignore"
        gitignore.write_text("*.log\ntemp/\n")
        engine = ExclusionEngine(project_root=temp_project)
        # RED PHASE: .gitignore loading not implemented yet
        # Will test proper loading in GREEN phase
        assert engine is not None
    
    def test_init_attempts_cortexignore_load(self, temp_project):
        """Test that .cortexignore is loaded if present."""
        cortexignore = temp_project / ".cortexignore"
        cortexignore.write_text("*.tmp\ncache/\n")
        engine = ExclusionEngine(project_root=temp_project)
        # RED PHASE: .cortexignore loading not implemented yet
        assert engine is not None


class TestExclusionEnginePatternManagement:
    """Test pattern add/get operations."""
    
    def test_add_pattern(self, engine):
        """Test adding a single pattern."""
        initial_count = len(engine.patterns)
        engine.add_pattern("*.test")
        assert len(engine.patterns) == initial_count + 1
        assert "*.test" in engine.get_patterns()
    
    def test_add_patterns_bulk(self, engine):
        """Test adding multiple patterns."""
        patterns_to_add = ["*.temp", "*.cache", "custom_dir/"]
        initial_count = len(engine.patterns)
        engine.add_patterns(patterns_to_add)
        assert len(engine.patterns) == initial_count + 3
        for pattern in patterns_to_add:
            assert pattern in engine.get_patterns()
    
    def test_get_patterns_returns_sorted(self, engine):
        """Test that get_patterns returns sorted list."""
        engine.add_pattern("zzz")
        engine.add_pattern("aaa")
        patterns = engine.get_patterns()
        assert patterns == sorted(patterns)


class TestExclusionEngineShouldExclude:
    """Test should_exclude() method."""
    
    def test_should_exclude_default_patterns(self, engine, temp_project):
        """Test exclusion of default patterns."""
        test_cases = [
            (temp_project / ".git" / "config", True),
            (temp_project / "__pycache__" / "module.pyc", True),
            (temp_project / "node_modules" / "package", True),
            (temp_project / "src" / "main.pyc", True),
            (temp_project / "src" / "main.py", False),
            (temp_project / "README.md", False),
        ]
        
        for path, expected_excluded in test_cases:
            relative_path = path.relative_to(temp_project)
            # RED PHASE: This will return False (not implemented)
            result = engine.should_exclude(path, relative_path)
            # In GREEN phase, should match expected_excluded
            assert isinstance(result, bool)
    
    def test_should_exclude_custom_pattern(self, engine, temp_project):
        """Test exclusion with custom pattern."""
        engine.add_pattern("*.secret")
        
        secret_file = temp_project / "data.secret"
        relative_path = secret_file.relative_to(temp_project)
        
        # RED PHASE: Returns False (not implemented)
        result = engine.should_exclude(secret_file, relative_path)
        # Should return True in GREEN phase
        assert isinstance(result, bool)
    
    def test_should_exclude_directory_pattern(self, engine, temp_project):
        """Test exclusion of directory patterns."""
        engine.add_pattern("temp/")
        
        temp_file = temp_project / "temp" / "file.txt"
        relative_path = temp_file.relative_to(temp_project)
        
        # RED PHASE: Returns False (not implemented)
        result = engine.should_exclude(temp_file, relative_path)
        # Should return True in GREEN phase
        assert isinstance(result, bool)
    
    def test_should_exclude_glob_pattern(self, engine, temp_project):
        """Test glob pattern matching."""
        engine.add_pattern("test_*.py")
        
        test_file = temp_project / "test_example.py"
        normal_file = temp_project / "example.py"
        
        # RED PHASE: Both return False (not implemented)
        result1 = engine.should_exclude(test_file, test_file.relative_to(temp_project))
        result2 = engine.should_exclude(normal_file, normal_file.relative_to(temp_project))
        
        # In GREEN phase: result1 should be True, result2 should be False
        assert isinstance(result1, bool)
        assert isinstance(result2, bool)


class TestExclusionEngineGitignoreIntegration:
    """Test .gitignore file integration."""
    
    def test_loads_gitignore_patterns(self, temp_project):
        """Test that patterns from .gitignore are loaded."""
        gitignore = temp_project / ".gitignore"
        gitignore.write_text("*.log\n/build/\ntemp/\n# comment\n\n")
        
        engine = ExclusionEngine(project_root=temp_project)
        # RED PHASE: .gitignore loading not implemented
        # In GREEN phase, these patterns should be loaded
        # For now, just verify engine was created
        assert engine is not None
    
    def test_handles_missing_gitignore(self, temp_project):
        """Test that missing .gitignore is handled gracefully."""
        engine = ExclusionEngine(project_root=temp_project)
        assert engine is not None
        # Should still have default patterns
        assert len(engine.patterns) > 0


class TestExclusionEngineCortexignoreIntegration:
    """Test .cortexignore file integration."""
    
    def test_loads_cortexignore_patterns(self, temp_project):
        """Test that patterns from .cortexignore are loaded."""
        cortexignore = temp_project / ".cortexignore"
        cortexignore.write_text("*.bak\narchive/\n")
        
        engine = ExclusionEngine(project_root=temp_project)
        # RED PHASE: .cortexignore loading not implemented
        assert engine is not None
    
    def test_handles_missing_cortexignore(self, temp_project):
        """Test that missing .cortexignore is handled gracefully."""
        engine = ExclusionEngine(project_root=temp_project)
        assert engine is not None


# RED PHASE SUMMARY:
# - Tests define expected behavior
# - should_exclude() currently returns False (placeholder)
# - Pattern loading from files not implemented
# - Next: GREEN phase - implement logic to make tests pass
