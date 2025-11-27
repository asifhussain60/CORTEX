"""
Test Plugin Integration and End-to-End Workflow

Tests for SystemRefactorPlugin's full 5-phase workflow and CORTEX framework integration.
This validates the complete plugin lifecycle from initialization through reporting.

Copyright © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))


class TestPluginExecution:
    """Test full plugin execution workflow."""
    
    @pytest.mark.integration
    def test_full_workflow_executes_all_phases(
        self,
        plugin_with_mocked_paths,
        mock_pytest_collect,
        mock_pytest_execution
    ):
        """Test complete 5-phase workflow execution."""
        with patch('subprocess.run', side_effect=[mock_pytest_collect, mock_pytest_execution]):
            # Execute full workflow
            result = plugin_with_mocked_paths.execute({
                'request': 'review system tests'
            })
            
            assert result is not None
            assert result.get('success') is True
            
            # Should have report
            assert 'report' in result or 'file_path' in result
    
    @pytest.mark.integration
    def test_workflow_handles_subprocess_errors(self, plugin_with_mocked_paths):
        """Test workflow handles subprocess failures gracefully."""
        # Mock subprocess to raise error
        mock_error = MagicMock()
        mock_error.side_effect = Exception("Subprocess failed")
        
        with patch('subprocess.run', mock_error):
            result = plugin_with_mocked_paths.execute({
                'request': 'review system tests'
            })
            
            # Should handle error gracefully
            assert result is not None
            
            # May return partial results or error info
            if result.get('success') is False:
                assert 'error' in result or 'message' in result
    
    @pytest.mark.integration
    def test_workflow_creates_output_files(
        self,
        plugin_with_mocked_paths,
        mock_pytest_collect,
        mock_pytest_execution
    ):
        """Test workflow creates expected output files."""
        with patch('subprocess.run', side_effect=[mock_pytest_collect, mock_pytest_execution]):
            result = plugin_with_mocked_paths.execute({
                'request': 'review system tests'
            })
            
            # Should create markdown report
            reports_dir = plugin_with_mocked_paths.brain_path / "documents" / "reports"
            if reports_dir.exists():
                report_files = list(reports_dir.glob("*.md"))
                assert len(report_files) > 0
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_workflow_with_real_test_directory(self, plugin_with_mocked_paths):
        """Test workflow with actual test directory (if available)."""
        # Check if real tests directory exists
        if not plugin_with_mocked_paths.tests_path.exists():
            pytest.skip("Real tests directory not available")
        
        # Execute with real directory
        result = plugin_with_mocked_paths.execute({
            'request': 'analyze test coverage'
        })
        
        assert result is not None


class TestPhaseIntegration:
    """Test integration between workflow phases."""
    
    @pytest.mark.integration
    def test_critical_review_feeds_gap_analysis(
        self,
        plugin_with_mocked_paths,
        mock_pytest_collect,
        mock_pytest_execution
    ):
        """Test Phase 1 output flows to Phase 2."""
        with patch('subprocess.run', side_effect=[mock_pytest_collect, mock_pytest_execution]):
            # Run Phase 1
            metrics = plugin_with_mocked_paths._analyze_test_suite()
            health = plugin_with_mocked_paths._assess_system_health(metrics)
            
            # Phase 2 should use Phase 1 results
            plugin_gaps = plugin_with_mocked_paths._check_plugin_coverage()
            
            # Both phases should complete
            assert metrics is not None
            assert health in ["EXCELLENT", "GOOD", "NEEDS_ATTENTION", "CRITICAL"]
            assert isinstance(plugin_gaps, list)
    
    @pytest.mark.integration
    def test_gap_analysis_feeds_recommendations(self, plugin_with_mocked_paths):
        """Test Phase 2 output flows to Phase 4."""
        # Create gaps
        gaps = plugin_with_mocked_paths._check_plugin_coverage()
        
        # Create mock report with gaps
        from plugins.system_refactor_plugin import ReviewReport
        report = ReviewReport(
            overall_health="GOOD",
            test_metrics={'total_tests': 300, 'passed': 285, 'failed': 15, 'pass_rate': 95.0},
            test_categories={},
            coverage_gaps=gaps,
            refactor_tasks=[],
            recommendations=[]
        )
        
        # Generate recommendations
        recommendations = plugin_with_mocked_paths._generate_recommendations(report)
        
        # Recommendations should reference gaps
        if len(gaps) > 0:
            recommendations_text = " ".join(recommendations)
            assert any(keyword in recommendations_text.lower() for keyword in ["gap", "coverage", "test"])
    
    @pytest.mark.integration
    def test_refactor_phase_feeds_recommendations(self, plugin_with_mocked_paths):
        """Test Phase 3 output flows to Phase 4."""
        # Execute refactor phase
        tasks = plugin_with_mocked_paths._execute_refactor_phase()
        
        # Create mock report with tasks
        from plugins.system_refactor_plugin import ReviewReport
        report = ReviewReport(
            overall_health="GOOD",
            test_metrics={'total_tests': 300, 'passed': 285, 'failed': 15, 'pass_rate': 95.0},
            test_categories={},
            coverage_gaps=[],
            refactor_tasks=tasks,
            recommendations=[]
        )
        
        # Generate recommendations
        recommendations = plugin_with_mocked_paths._generate_recommendations(report)
        
        # Recommendations should reference tasks if present
        if len(tasks) > 0:
            recommendations_text = " ".join(recommendations)
            assert any(keyword in recommendations_text.lower() for keyword in ["refactor", "task", "todo"])


class TestPluginCleanup:
    """Test plugin cleanup and resource management."""
    
    @pytest.mark.unit
    def test_cleanup_releases_resources(self, refactor_plugin):
        """Test cleanup() releases any held resources."""
        # Execute some operations first
        refactor_plugin.initialize()
        
        # Cleanup should succeed
        result = refactor_plugin.cleanup()
        
        assert result is True
    
    @pytest.mark.unit
    def test_cleanup_is_idempotent(self, refactor_plugin):
        """Test cleanup() can be called multiple times safely."""
        result1 = refactor_plugin.cleanup()
        result2 = refactor_plugin.cleanup()
        result3 = refactor_plugin.cleanup()
        
        # All calls should succeed
        assert result1 is True
        assert result2 is True
        assert result3 is True
    
    @pytest.mark.unit
    def test_cleanup_after_error(self, refactor_plugin):
        """Test cleanup() works even after errors."""
        # Simulate error during execution
        try:
            refactor_plugin._analyze_test_suite()  # May fail if no tests
        except Exception:
            pass
        
        # Cleanup should still work
        result = refactor_plugin.cleanup()
        assert result is True


class TestPluginRegistration:
    """Test plugin registration with CORTEX framework."""
    
    @pytest.mark.unit
    def test_register_function_exists(self):
        """Test plugin has register() function."""
        from plugins.system_refactor_plugin import register
        
        assert callable(register)
    
    @pytest.mark.unit
    def test_register_returns_plugin_instance(self):
        """Test register() returns SystemRefactorPlugin instance."""
        from plugins.system_refactor_plugin import register, SystemRefactorPlugin
        
        plugin = register()
        
        assert plugin is not None
        assert isinstance(plugin, SystemRefactorPlugin)
    
    @pytest.mark.unit
    def test_plugin_has_required_metadata(self, refactor_plugin):
        """Test plugin instance has required metadata."""
        assert hasattr(refactor_plugin, 'metadata')
        
        metadata = refactor_plugin.metadata
        assert 'plugin_id' in metadata
        assert 'name' in metadata
        assert 'version' in metadata
        assert 'category' in metadata


class TestPluginDiscovery:
    """Test CORTEX plugin discovery mechanism."""
    
    @pytest.mark.integration
    def test_plugin_discoverable_by_cortex(self):
        """Test CORTEX can discover the plugin."""
        # Check plugin file exists in expected location
        plugin_file = Path(__file__).parent.parent.parent.parent / "src" / "plugins" / "system_refactor_plugin.py"
        
        assert plugin_file.exists(), "Plugin file should exist in src/plugins/"
    
    @pytest.mark.integration
    def test_plugin_module_importable(self):
        """Test plugin module can be imported."""
        try:
            from plugins import system_refactor_plugin
            assert system_refactor_plugin is not None
        except ImportError:
            pytest.fail("Plugin module should be importable")


class TestCommandMetadata:
    """Test plugin command metadata."""
    
    @pytest.mark.unit
    def test_command_metadata_structure(self, refactor_plugin):
        """Test command metadata has correct structure."""
        commands = refactor_plugin.get_commands()
        
        assert len(commands) > 0
        
        for cmd in commands:
            assert 'command' in cmd
            assert 'plugin_id' in cmd
            assert 'description' in cmd
            assert 'usage' in cmd
    
    @pytest.mark.unit
    def test_command_metadata_matches_plugin_id(self, refactor_plugin):
        """Test command metadata plugin_id matches plugin."""
        commands = refactor_plugin.get_commands()
        plugin_id = refactor_plugin.metadata['plugin_id']
        
        for cmd in commands:
            assert cmd['plugin_id'] == plugin_id
    
    @pytest.mark.unit
    def test_command_has_usage_examples(self, refactor_plugin):
        """Test command metadata includes usage examples."""
        commands = refactor_plugin.get_commands()
        
        for cmd in commands:
            usage = cmd.get('usage', '')
            assert len(usage) > 0, "Usage should provide examples"


class TestErrorHandling:
    """Test plugin error handling."""
    
    @pytest.mark.unit
    def test_handles_missing_test_directory(self, tmp_path):
        """Test plugin handles missing test directory."""
        from plugins.system_refactor_plugin import SystemRefactorPlugin
        
        # Create plugin with non-existent tests directory
        plugin = SystemRefactorPlugin()
        plugin.project_root = tmp_path
        plugin.tests_path = tmp_path / "nonexistent_tests"
        
        # Should handle gracefully
        result = plugin.execute({'request': 'review tests'})
        
        # Should not crash
        assert result is not None
    
    @pytest.mark.unit
    def test_handles_empty_test_directory(self, plugin_with_mocked_paths):
        """Test plugin handles empty test directory."""
        # Ensure tests directory is empty
        tests_path = plugin_with_mocked_paths.tests_path
        for item in tests_path.iterdir():
            if item.is_file():
                item.unlink()
        
        # Should handle gracefully
        result = plugin_with_mocked_paths._execute_refactor_phase()
        
        # Should return empty list, not crash
        assert isinstance(result, list)
        assert len(result) == 0
    
    @pytest.mark.unit
    def test_handles_malformed_test_files(self, plugin_with_mocked_paths, mock_test_file):
        """Test plugin handles malformed test files."""
        # Create test file with syntax error
        malformed_content = """
        def test_something(
            # Missing closing parenthesis
            assert True
        """
        
        test_file = mock_test_file(
            plugin_with_mocked_paths.tests_path,
            "test_malformed.py",
            malformed_content
        )
        
        # Should handle gracefully
        result = plugin_with_mocked_paths._execute_refactor_phase()
        
        # Should not crash
        assert isinstance(result, list)


class TestPerformance:
    """Test plugin performance characteristics."""
    
    @pytest.mark.slow
    def test_workflow_completes_in_reasonable_time(
        self,
        plugin_with_mocked_paths,
        mock_pytest_collect,
        mock_pytest_execution
    ):
        """Test full workflow completes within timeout."""
        import time
        
        start_time = time.time()
        
        with patch('subprocess.run', side_effect=[mock_pytest_collect, mock_pytest_execution]):
            plugin_with_mocked_paths.execute({
                'request': 'review system tests'
            })
        
        elapsed_time = time.time() - start_time
        
        # Should complete within 60 seconds (generous for mocked operations)
        assert elapsed_time < 60.0, f"Workflow took {elapsed_time:.2f}s, should be < 60s"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
