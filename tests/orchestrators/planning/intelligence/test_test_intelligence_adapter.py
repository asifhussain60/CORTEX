"""
Tests for TestIntelligenceAdapter

Validates test discovery, coverage analysis, gap identification,
and test strategy generation.

Week 9 Day 1: 8 comprehensive tests
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil

from src.orchestrators.planning.intelligence.test_intelligence_adapter import (
    TestIntelligenceAdapter,
    TestFile,
    TestCoverageAnalysis,
    TestGap
)


class TestTestIntelligenceAdapterInit:
    """Test adapter initialization."""
    
    def test_init_with_project_root(self, tmp_path):
        """Test initialization with project root."""
        adapter = TestIntelligenceAdapter(tmp_path)
        
        assert adapter.project_root == tmp_path
        assert adapter._test_file_cache == {}
        assert adapter._coverage_cache is None
    
    def test_init_with_cortex_root(self, tmp_path):
        """Test initialization with CORTEX root."""
        cortex_root = tmp_path / "cortex"
        cortex_root.mkdir()
        
        adapter = TestIntelligenceAdapter(tmp_path, cortex_root=cortex_root)
        
        assert adapter.cortex_root == cortex_root


class TestTestDiscovery:
    """Test discovery functionality."""
    
    def test_discover_test_files(self, tmp_path):
        """Test discovering test files in project."""
        # Create test structure
        test_dir = tmp_path / "tests"
        test_dir.mkdir()
        
        (test_dir / "test_module.py").write_text("""
def test_something():
    assert True

def test_another():
    assert False
""")
        
        (test_dir / "module_test.py").write_text("""
def test_feature():
    pass
""")
        
        adapter = TestIntelligenceAdapter(tmp_path)
        test_files = adapter._discover_test_files()
        
        assert len(test_files) == 2
        assert all(isinstance(f, TestFile) for f in test_files)
    
    def test_analyze_test_file(self, tmp_path):
        """Test analyzing single test file."""
        test_file = tmp_path / "test_sample.py"
        test_file.write_text("""
def test_one():
    assert True

def test_two():
    assert True

def helper_function():
    pass

def test_three():
    assert True
""")
        
        adapter = TestIntelligenceAdapter(tmp_path)
        result = adapter._analyze_test_file(test_file)
        
        assert isinstance(result, TestFile)
        assert result.test_count == 3  # Only test_ functions
        assert result.path == test_file


class TestCoverageAnalysis:
    """Test coverage calculation."""
    
    def test_analyze_project_coverage(self, tmp_path):
        """Test comprehensive project coverage analysis."""
        # Create project structure
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "module1.py").write_text("def func(): pass")
        (src_dir / "module2.py").write_text("def func(): pass")
        
        test_dir = tmp_path / "tests"
        test_dir.mkdir()
        (test_dir / "test_module1.py").write_text("""
def test_func():
    assert True
""")
        
        adapter = TestIntelligenceAdapter(tmp_path)
        analysis = adapter.analyze_project_coverage()
        
        assert isinstance(analysis, TestCoverageAnalysis)
        assert analysis.test_files > 0
        assert analysis.total_files > 0
        assert 0 <= analysis.overall_coverage <= 100
    
    def test_coverage_caching(self, tmp_path):
        """Test that coverage analysis is cached."""
        adapter = TestIntelligenceAdapter(tmp_path)
        
        # First call
        analysis1 = adapter.analyze_project_coverage()
        
        # Second call (should use cache)
        analysis2 = adapter.analyze_project_coverage()
        
        assert analysis1 is analysis2  # Same object (cached)
        
        # Force refresh
        analysis3 = adapter.analyze_project_coverage(force_refresh=True)
        assert analysis1 is not analysis3  # Different object


class TestGapIdentification:
    """Test gap identification."""
    
    def test_identify_critical_gaps(self, tmp_path):
        """Test identifying critical test gaps."""
        # Create structure with gaps
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        
        # Module without tests
        (src_dir / "uncovered.py").write_text("""
class ImportantClass:
    def critical_method(self):
        return True
""")
        
        adapter = TestIntelligenceAdapter(tmp_path)
        gaps = adapter.identify_critical_gaps()
        
        assert isinstance(gaps, list)
        assert all(isinstance(g, TestGap) for g in gaps)
    
    def test_gap_severity_prioritization(self, tmp_path):
        """Test that gaps are sorted by severity."""
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        
        (src_dir / "module.py").write_text("def func(): pass")
        
        adapter = TestIntelligenceAdapter(tmp_path)
        gaps = adapter.identify_critical_gaps([src_dir / "module.py"])
        
        if len(gaps) > 1:
            # Verify severity ordering
            severities = [g.severity for g in gaps]
            severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
            severity_values = [severity_order[s] for s in severities]
            assert severity_values == sorted(severity_values)


class TestStrategyGeneration:
    """Test strategy generation."""
    
    def test_generate_test_strategy_simple(self, tmp_path):
        """Test generating test strategy for simple feature."""
        feature_scope = {
            "files_affected": ["src/models/user.py"],
            "complexity": "low"
        }
        
        adapter = TestIntelligenceAdapter(tmp_path)
        strategy = adapter.generate_test_strategy(feature_scope)
        
        assert "target_coverage" in strategy
        assert "test_types" in strategy
        assert "test_files_to_create" in strategy
        assert "estimated_test_count" in strategy
        assert isinstance(strategy["tdd_recommended"], bool)
    
    def test_generate_test_strategy_complex(self, tmp_path):
        """Test generating test strategy for complex feature."""
        feature_scope = {
            "files_affected": [
                "src/api/endpoint.py",
                "src/models/entity.py",
                "src/services/processor.py"
            ],
            "complexity": "high"
        }
        
        adapter = TestIntelligenceAdapter(tmp_path)
        strategy = adapter.generate_test_strategy(feature_scope, target_coverage=90.0)
        
        assert strategy["target_coverage"] == 90.0
        assert strategy["tdd_recommended"] is True  # Complex feature
        assert len(strategy["reasoning"]) > 0
        assert strategy["estimated_test_count"] > 0


@pytest.fixture
def sample_project(tmp_path):
    """Create a sample project structure for testing."""
    # Source files
    src = tmp_path / "src"
    src.mkdir()
    
    (src / "module1.py").write_text("""
def function1():
    return True

def function2():
    return False
""")
    
    (src / "module2.py").write_text("""
class MyClass:
    def method1(self):
        pass
""")
    
    # Test files
    tests = tmp_path / "tests"
    tests.mkdir()
    
    (tests / "test_module1.py").write_text("""
def test_function1():
    assert True
""")
    
    return tmp_path
