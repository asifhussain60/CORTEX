"""
Test Critical Review Functionality

Tests for SystemRefactorPlugin's test suite analysis and health assessment.
This is Phase 1 of the 5-phase workflow.

Copyright © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))


class TestTestSuiteAnalysis:
    """Test analyzing test suite with pytest."""
    
    @pytest.mark.unit
    def test_analyze_test_suite_collects_tests(self, refactor_plugin, mock_pytest_collect):
        """Test _analyze_test_suite collects test count."""
        with patch('subprocess.run', return_value=mock_pytest_collect):
            result = refactor_plugin._analyze_test_suite()
            
            assert result is not None
            assert 'total_tests' in result
            assert result['total_tests'] == 5
    
    @pytest.mark.unit
    def test_analyze_test_suite_runs_tests(self, refactor_plugin, mock_pytest_execution):
        """Test _analyze_test_suite runs tests and captures results."""
        with patch('subprocess.run', side_effect=[mock_pytest_execution, mock_pytest_execution]):
            result = refactor_plugin._analyze_test_suite()
            
            assert result is not None
            assert 'passed' in result
            assert 'failed' in result
            assert result['passed'] == 4
            assert result['failed'] == 1
    
    @pytest.mark.unit
    def test_analyze_test_suite_calculates_pass_rate(self, refactor_plugin, mock_pytest_execution):
        """Test _analyze_test_suite calculates pass rate percentage."""
        with patch('subprocess.run', side_effect=[mock_pytest_execution, mock_pytest_execution]):
            result = refactor_plugin._analyze_test_suite()
            
            assert 'pass_rate' in result
            # 4 passed / 5 total = 80%
            assert result['pass_rate'] == 80.0
    
    @pytest.mark.unit
    def test_analyze_test_suite_handles_errors(self, refactor_plugin):
        """Test _analyze_test_suite handles subprocess errors gracefully."""
        mock_error = MagicMock()
        mock_error.returncode = 1
        mock_error.stdout = "Error running pytest"
        
        with patch('subprocess.run', side_effect=Exception("pytest failed")):
            result = refactor_plugin._analyze_test_suite()
            
            # Should return empty/default result on error
            assert result is not None


class TestHealthAssessment:
    """Test system health assessment logic."""
    
    @pytest.mark.unit
    def test_assess_health_excellent(self, refactor_plugin, excellent_metrics):
        """Test health assessment returns EXCELLENT for high coverage."""
        health = refactor_plugin._assess_system_health(excellent_metrics)
        
        assert health == "EXCELLENT"
    
    @pytest.mark.unit
    def test_assess_health_good(self, refactor_plugin, good_metrics):
        """Test health assessment returns GOOD for above-average coverage."""
        health = refactor_plugin._assess_system_health(good_metrics)
        
        assert health == "GOOD"
    
    @pytest.mark.unit
    def test_assess_health_needs_attention(self, refactor_plugin, needs_attention_metrics):
        """Test health assessment returns NEEDS_ATTENTION for moderate coverage."""
        health = refactor_plugin._assess_system_health(needs_attention_metrics)
        
        assert health == "NEEDS_ATTENTION"
    
    @pytest.mark.unit
    def test_assess_health_critical(self, refactor_plugin, critical_metrics):
        """Test health assessment returns CRITICAL for low coverage."""
        health = refactor_plugin._assess_system_health(critical_metrics)
        
        assert health == "CRITICAL"
    
    @pytest.mark.unit
    def test_health_assessment_thresholds(self, refactor_plugin):
        """Test health assessment uses correct thresholds."""
        # EXCELLENT: ≥98% pass rate AND ≥400 tests
        excellent = {
            'total_tests': 400,
            'passed': 392,
            'failed': 8,
            'pass_rate': 98.0
        }
        assert refactor_plugin._assess_system_health(excellent) == "EXCELLENT"
        
        # GOOD: ≥95% pass rate AND ≥300 tests
        good = {
            'total_tests': 300,
            'passed': 285,
            'failed': 15,
            'pass_rate': 95.0
        }
        assert refactor_plugin._assess_system_health(good) == "GOOD"
        
        # NEEDS_ATTENTION: ≥90% pass rate AND ≥200 tests
        needs_attention = {
            'total_tests': 200,
            'passed': 180,
            'failed': 20,
            'pass_rate': 90.0
        }
        assert refactor_plugin._assess_system_health(needs_attention) == "NEEDS_ATTENTION"
        
        # CRITICAL: Below thresholds
        critical = {
            'total_tests': 100,
            'passed': 70,
            'failed': 30,
            'pass_rate': 70.0
        }
        assert refactor_plugin._assess_system_health(critical) == "CRITICAL"


class TestTestCategoryAnalysis:
    """Test analyzing test categories by directory."""
    
    @pytest.mark.unit
    def test_analyze_test_categories_scans_directories(self, plugin_with_mocked_paths):
        """Test _analyze_test_categories scans test directories."""
        result = plugin_with_mocked_paths._analyze_test_categories()
        
        assert result is not None
        assert isinstance(result, dict)
    
    @pytest.mark.unit
    def test_analyze_test_categories_includes_expected_dirs(self, plugin_with_mocked_paths):
        """Test category analysis includes expected test directories."""
        result = plugin_with_mocked_paths._analyze_test_categories()
        
        # Should analyze major test directories
        expected_categories = [
            'tier0', 'tier1', 'tier2', 'tier3',
            'integration', 'plugins', 'edge_cases',
            'orchestrators', 'agents'
        ]
        
        # At least some categories should be present
        assert any(cat in result for cat in expected_categories)
    
    @pytest.mark.unit
    def test_analyze_test_categories_counts_files(self, plugin_with_mocked_paths):
        """Test category analysis counts test files per directory."""
        result = plugin_with_mocked_paths._analyze_test_categories()
        
        # Each category should have a count
        for category, count in result.items():
            assert isinstance(count, int)
            assert count >= 0
    
    @pytest.mark.integration
    def test_analyze_test_categories_with_real_tests(self, refactor_plugin):
        """Test category analysis on real test directory (if exists)."""
        if refactor_plugin.tests_path.exists():
            result = refactor_plugin._analyze_test_categories()
            
            assert result is not None
            assert len(result) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
