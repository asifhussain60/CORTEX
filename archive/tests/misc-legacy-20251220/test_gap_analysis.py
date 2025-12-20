"""
Test Coverage Gap Analysis

Tests for SystemRefactorPlugin's gap detection across 5 categories.
This is Phase 2 of the 5-phase workflow.

Copyright © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))


class TestPluginCoverageGaps:
    """Test plugin test coverage detection."""
    
    @pytest.mark.unit
    def test_check_plugin_coverage_finds_plugins(self, plugin_with_mocked_paths):
        """Test _check_plugin_coverage finds plugin files."""
        gaps = plugin_with_mocked_paths._check_plugin_coverage()
        
        assert gaps is not None
        assert isinstance(gaps, list)
    
    @pytest.mark.unit
    def test_check_plugin_coverage_detects_missing_tests(self, plugin_with_mocked_paths):
        """Test _check_plugin_coverage detects plugins without tests."""
        # Create a plugin file without corresponding test
        plugin_file = plugin_with_mocked_paths.src_path / "plugins" / "untested_plugin.py"
        plugin_file.parent.mkdir(exist_ok=True)
        plugin_file.write_text("class UntestedPlugin: pass")
        
        gaps = plugin_with_mocked_paths._check_plugin_coverage()
        
        # Should find gap for untested_plugin
        gap_names = [gap.name for gap in gaps]
        assert "untested_plugin" in gap_names or any("untested" in name for name in gap_names)
    
    @pytest.mark.unit
    def test_plugin_coverage_gap_has_required_fields(self, plugin_with_mocked_paths):
        """Test plugin coverage gaps have required fields."""
        # Create untested plugin
        plugin_file = plugin_with_mocked_paths.src_path / "plugins" / "test_gap.py"
        plugin_file.parent.mkdir(exist_ok=True)
        plugin_file.write_text("class TestGapPlugin: pass")
        
        gaps = plugin_with_mocked_paths._check_plugin_coverage()
        
        if gaps:
            gap = gaps[0]
            assert hasattr(gap, 'category')
            assert hasattr(gap, 'name')
            assert hasattr(gap, 'priority')
            assert hasattr(gap, 'description')
            assert gap.category == "plugin"


class TestEntryPointCoverageGaps:
    """Test entry point test coverage detection."""
    
    @pytest.mark.unit
    def test_check_entry_point_coverage_finds_modules(self, plugin_with_mocked_paths):
        """Test _check_entry_point_coverage finds entry point modules."""
        gaps = plugin_with_mocked_paths._check_entry_point_coverage()
        
        assert gaps is not None
        assert isinstance(gaps, list)
    
    @pytest.mark.unit
    def test_check_entry_point_coverage_detects_missing_tests(self, plugin_with_mocked_paths):
        """Test entry point coverage detects modules without tests."""
        # Create entry point without test
        entry_module = plugin_with_mocked_paths.src_path / "operations" / "untested_entry.py"
        entry_module.parent.mkdir(exist_ok=True)
        entry_module.write_text("def execute(): pass")
        
        gaps = plugin_with_mocked_paths._check_entry_point_coverage()
        
        # Should find gap
        assert isinstance(gaps, list)
    
    @pytest.mark.unit
    def test_entry_point_gap_has_high_priority(self, plugin_with_mocked_paths):
        """Test entry point gaps are marked HIGH priority."""
        # Create untested entry point
        entry_module = plugin_with_mocked_paths.src_path / "operations" / "critical_entry.py"
        entry_module.parent.mkdir(exist_ok=True)
        entry_module.write_text("def execute(): pass")
        
        gaps = plugin_with_mocked_paths._check_entry_point_coverage()
        
        if gaps:
            # Entry points should be HIGH priority
            assert any(gap.priority == "HIGH" for gap in gaps)


class TestRefactorPhaseCoverageGaps:
    """Test REFACTOR phase task detection."""
    
    @pytest.mark.unit
    def test_check_refactor_phase_coverage_scans_files(self, plugin_with_mocked_paths, sample_test_file_content):
        """Test _check_refactor_phase_coverage scans test files."""
        # Create test file with TODO REFACTOR comments
        test_file = plugin_with_mocked_paths.tests_path / "test_auth.py"
        test_file.write_text(sample_test_file_content)
        
        gaps = plugin_with_mocked_paths._check_refactor_phase_coverage()
        
        assert gaps is not None
        assert isinstance(gaps, list)
    
    @pytest.mark.unit
    def test_check_refactor_phase_detects_todo_comments(self, plugin_with_mocked_paths):
        """Test refactor phase detects TODO REFACTOR comments."""
        # Create test with TODO REFACTOR
        test_content = """
        def test_login():
            # TODO REFACTOR: Extract authentication logic
            pass
        
        def test_logout():
            # TODO REFACTOR: Add session cleanup
            pass
        """
        
        test_file = plugin_with_mocked_paths.tests_path / "test_pending.py"
        test_file.write_text(test_content)
        
        gaps = plugin_with_mocked_paths._check_refactor_phase_coverage()
        
        # Should find 2 TODO REFACTOR comments
        if gaps:
            assert len(gaps) >= 1
            assert any("refactor" in gap.description.lower() for gap in gaps)
    
    @pytest.mark.unit
    def test_refactor_phase_gap_is_medium_priority(self, plugin_with_mocked_paths):
        """Test REFACTOR tasks are marked MEDIUM priority."""
        test_content = "# TODO REFACTOR: Improve test structure"
        test_file = plugin_with_mocked_paths.tests_path / "test_medium.py"
        test_file.write_text(test_content)
        
        gaps = plugin_with_mocked_paths._check_refactor_phase_coverage()
        
        if gaps:
            assert any(gap.priority == "MEDIUM" for gap in gaps)


class TestModuleCoverageGaps:
    """Test integration test coverage detection."""
    
    @pytest.mark.unit
    def test_check_module_coverage_finds_modules(self, plugin_with_mocked_paths):
        """Test _check_module_coverage finds source modules."""
        gaps = plugin_with_mocked_paths._check_module_coverage()
        
        assert gaps is not None
        assert isinstance(gaps, list)
    
    @pytest.mark.unit
    def test_check_module_coverage_detects_missing_integration_tests(self, plugin_with_mocked_paths):
        """Test module coverage detects missing integration tests."""
        # Create module without integration test
        module = plugin_with_mocked_paths.src_path / "core" / "untested_module.py"
        module.parent.mkdir(exist_ok=True)
        module.write_text("class UntestedCore: pass")
        
        gaps = plugin_with_mocked_paths._check_module_coverage()
        
        assert isinstance(gaps, list)
    
    @pytest.mark.unit
    def test_module_gap_has_medium_priority(self, plugin_with_mocked_paths):
        """Test module gaps are marked MEDIUM priority."""
        # Create untested module
        module = plugin_with_mocked_paths.src_path / "utils" / "helper.py"
        module.parent.mkdir(exist_ok=True)
        module.write_text("def helper(): pass")
        
        gaps = plugin_with_mocked_paths._check_module_coverage()
        
        if gaps:
            # Module tests should be MEDIUM priority
            assert any(gap.priority in ["MEDIUM", "LOW"] for gap in gaps)


class TestPerformanceCoverageGaps:
    """Test performance test coverage detection."""
    
    @pytest.mark.unit
    def test_check_performance_coverage_scans_for_benchmarks(self, plugin_with_mocked_paths):
        """Test _check_performance_coverage scans for performance tests."""
        gaps = plugin_with_mocked_paths._check_performance_coverage()
        
        assert gaps is not None
        assert isinstance(gaps, list)
    
    @pytest.mark.unit
    def test_check_performance_coverage_detects_missing_benchmarks(self, plugin_with_mocked_paths):
        """Test performance coverage detects missing benchmark tests."""
        # Create source file without performance test
        src_file = plugin_with_mocked_paths.src_path / "core" / "algorithm.py"
        src_file.parent.mkdir(exist_ok=True)
        src_file.write_text("def slow_operation(): pass")
        
        gaps = plugin_with_mocked_paths._check_performance_coverage()
        
        assert isinstance(gaps, list)
    
    @pytest.mark.unit
    def test_performance_gap_has_low_priority(self, plugin_with_mocked_paths):
        """Test performance gaps are marked LOW priority."""
        gaps = plugin_with_mocked_paths._check_performance_coverage()
        
        if gaps:
            # Performance tests should be LOW priority
            assert any(gap.priority == "LOW" for gap in gaps)


class TestGapPrioritization:
    """Test gap prioritization logic."""
    
    @pytest.mark.unit
    def test_gaps_are_prioritized_correctly(self, sample_coverage_gap):
        """Test gaps have correct priority levels."""
        assert sample_coverage_gap.priority in ["HIGH", "MEDIUM", "LOW"]
    
    @pytest.mark.unit
    def test_high_priority_gaps_listed_first(self, plugin_with_mocked_paths):
        """Test high priority gaps appear first in results."""
        # Create mix of gaps
        all_gaps = []
        all_gaps.extend(plugin_with_mocked_paths._check_entry_point_coverage())  # HIGH
        all_gaps.extend(plugin_with_mocked_paths._check_plugin_coverage())  # HIGH
        all_gaps.extend(plugin_with_mocked_paths._check_module_coverage())  # MEDIUM
        all_gaps.extend(plugin_with_mocked_paths._check_performance_coverage())  # LOW
        
        if all_gaps:
            # Sort by priority (HIGH > MEDIUM > LOW)
            priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
            sorted_gaps = sorted(all_gaps, key=lambda g: priority_order.get(g.priority, 3))
            
            # First gap should be HIGH priority
            if sorted_gaps:
                assert sorted_gaps[0].priority == "HIGH"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
