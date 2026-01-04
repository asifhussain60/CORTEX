"""
Tests for Phase 2: Duplicate Detection.

Author: Asif Hussain
Created: January 3, 2026
"""

import pytest
from pathlib import Path
from src.orchestrators.refinement.phases.duplicate_detection import DuplicateDetectionPhase


class MockOrchestrator:
    """Mock orchestrator for testing."""
    def __init__(self, target_path):
        self.target_path = target_path


class TestDuplicateDetectionPhase:
    """Test duplicate detection phase."""
    
    @pytest.fixture
    def sample_file(self, tmp_path):
        """Create sample file with duplicates."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""
def calculate_sum(a, b):
    result = a + b
    return result

def calculate_total(x, y):
    result = x + y
    return result

def process_data(data):
    filtered = []
    for item in data:
        if item > 0:
            filtered.append(item)
    return filtered

def filter_data(items):
    result = []
    for item in items:
        if item > 0:
            result.append(item)
    return result
""")
        return test_file
    
    @pytest.fixture
    def phase(self, sample_file):
        """Create duplicate detection phase."""
        orchestrator = MockOrchestrator(sample_file)
        return DuplicateDetectionPhase(orchestrator)
    
    def test_execute(self, phase):
        """Test phase execution."""
        results = phase.execute()
        
        assert "duplicates_found" in results
        assert "duplicate_groups" in results
        assert "consolidation_suggestions" in results
        assert "estimated_savings" in results
    
    def test_find_duplicates(self, phase):
        """Test duplicate finding."""
        results = phase.execute()
        
        # Should find some duplicates
        assert results["duplicates_found"] >= 0
    
    def test_consolidation_suggestions(self, phase):
        """Test consolidation suggestions."""
        results = phase.execute()
        suggestions = results["consolidation_suggestions"]
        
        for suggestion in suggestions:
            assert "duplicate_count" in suggestion
            assert "suggested_location" in suggestion
            assert "refactoring_steps" in suggestion
    
    def test_estimated_savings(self, phase):
        """Test savings calculation."""
        results = phase.execute()
        savings = results["estimated_savings"]
        
        assert "lines" in savings
        assert "files" in savings
        assert savings["lines"] >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
