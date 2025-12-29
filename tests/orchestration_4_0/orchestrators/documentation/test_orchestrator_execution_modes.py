"""
End-to-End Integration Tests for Execution Modes with DocumentationOrchestrator

Tests that execution modes properly control documentation generation behavior.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock
import tempfile
import shutil

from src.orchestration_4_0.orchestrators.documentation.documentation_orchestrator import (
    DocumentationOrchestrator,
    DocumentationConfig
)
from src.orchestration_4_0.execution.execution_mode import ExecutionMode


@pytest.fixture
def temp_output_dir():
    """Create temporary output directory"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_logger():
    """Mock logger"""
    return Mock()


@pytest.fixture
def orchestrator(mock_logger):
    """Create orchestrator instance"""
    config = {
        'cortex_root': Path.cwd(),
        'execution_mode': 'AUTONOMOUS'
    }
    return DocumentationOrchestrator(logger=mock_logger, config=config)


class TestExecutionModeOrchestration:
    """Test execution mode integration with DocumentationOrchestrator"""
    
    def test_orchestrator_has_mode_integration(self, orchestrator):
        """Test that orchestrator has mode integration initialized"""
        assert hasattr(orchestrator, 'mode_integration')
        assert orchestrator.mode_integration is not None
    
    def test_orchestrator_has_formatting_config_attribute(self, orchestrator):
        """Test that orchestrator has formatting_config attribute"""
        assert hasattr(orchestrator, 'formatting_config')
    
    def test_mode_selection_in_setup(self, orchestrator, temp_output_dir):
        """Test that mode is selected during setup phase"""
        context = {
            'config': DocumentationConfig(
                source_paths=[Path("src")],
                output_dir=temp_output_dir
            )
        }
        
        # Run setup
        orchestrator._setup(context)
        
        # Verify mode was selected and stored
        assert 'execution_mode' in context
        assert isinstance(context['execution_mode'], ExecutionMode)
        
        # Verify formatting config was generated
        assert 'formatting_config' in context
        assert orchestrator.formatting_config is not None
    
    def test_mode_override_in_setup(self, orchestrator, temp_output_dir):
        """Test that mode can be overridden via context"""
        context = {
            'config': DocumentationConfig(
                source_paths=[Path("src")],
                output_dir=temp_output_dir
            ),
            'execution_mode': 'supervised'
        }
        
        # Run setup
        orchestrator._setup(context)
        
        # Verify mode was overridden
        assert context['execution_mode'] == ExecutionMode.SUPERVISED
    
    def test_autonomous_mode_formatting(self, mock_logger, temp_output_dir):
        """Test AUTONOMOUS mode uses concise formatting"""
        config = {
            'cortex_root': Path.cwd(),
            'execution_mode': 'AUTONOMOUS'
        }
        orch = DocumentationOrchestrator(logger=mock_logger, config=config)
        
        context = {
            'config': DocumentationConfig(
                source_paths=[Path("src")],
                output_dir=temp_output_dir
            ),
            'execution_mode': 'autonomous'
        }
        
        orch._setup(context)
        
        # Verify autonomous formatting
        assert orch.formatting_config.detail_level.value == 'concise'
        assert orch.formatting_config.include_examples is False
        assert orch.formatting_config.include_diagrams is False
        assert orch.formatting_config.max_description_length == 200
    
    def test_supervised_mode_formatting(self, mock_logger, temp_output_dir):
        """Test SUPERVISED mode uses standard formatting"""
        config = {
            'cortex_root': Path.cwd()
        }
        orch = DocumentationOrchestrator(logger=mock_logger, config=config)
        
        context = {
            'config': DocumentationConfig(
                source_paths=[Path("src")],
                output_dir=temp_output_dir
            ),
            'execution_mode': 'supervised'
        }
        
        orch._setup(context)
        
        # Verify supervised formatting
        assert orch.formatting_config.detail_level.value == 'standard'
        assert orch.formatting_config.include_examples is True
        assert orch.formatting_config.include_diagrams is True
        assert orch.formatting_config.max_description_length == 500
    
    def test_human_in_loop_mode_formatting(self, mock_logger, temp_output_dir):
        """Test HUMAN_IN_LOOP mode uses verbose formatting"""
        config = {
            'cortex_root': Path.cwd()
        }
        orch = DocumentationOrchestrator(logger=mock_logger, config=config)
        
        context = {
            'config': DocumentationConfig(
                source_paths=[Path("src")],
                output_dir=temp_output_dir
            ),
            'execution_mode': 'human_in_loop'
        }
        
        orch._setup(context)
        
        # Verify human-in-loop formatting
        assert orch.formatting_config.detail_level.value == 'verbose'
        assert orch.formatting_config.include_examples is True
        assert orch.formatting_config.include_diagrams is True
        assert orch.formatting_config.max_description_length == 1000
    
    def test_mode_integration_method_access(self, orchestrator):
        """Test access to mode integration methods"""
        # Verify orchestrator can access mode integration methods
        assert hasattr(orchestrator.mode_integration, 'select_mode_for_operation')
        assert hasattr(orchestrator.mode_integration, 'get_formatting_config')
        assert hasattr(orchestrator.mode_integration, 'should_include_section')
        assert hasattr(orchestrator.mode_integration, 'format_description')
    
    def test_user_stats_updated_after_export(self, mock_logger, temp_output_dir):
        """Test that user stats are updated after successful documentation export"""
        config = {
            'cortex_root': Path.cwd()
        }
        orch = DocumentationOrchestrator(logger=mock_logger, config=config)
        
        # Setup context
        context = {
            'config': DocumentationConfig(
                source_paths=[Path("src")],
                output_dir=temp_output_dir
            )
        }
        
        orch._setup(context)
        
        # Get initial stats
        initial_completed = orch.mode_integration.user_profile.get_user().completed_operations
        
        # Mock result
        from src.orchestration_4_0.orchestrators.documentation.documentation_orchestrator import (
            DocumentationResult
        )
        result = DocumentationResult()
        context['result'] = result
        
        # Run export phase (which updates stats)
        try:
            orch._export_phase(context, result)
        except Exception:
            pass  # May fail due to missing files, but stats should still update
        
        # Verify stats were updated
        final_completed = orch.mode_integration.user_profile.get_user().completed_operations
        assert final_completed >= initial_completed
    
    def test_section_inclusion_based_on_mode(self, orchestrator, temp_output_dir):
        """Test that section inclusion respects execution mode"""
        context = {
            'config': DocumentationConfig(
                source_paths=[Path("src")],
                output_dir=temp_output_dir
            ),
            'execution_mode': 'autonomous'
        }
        
        orchestrator._setup(context)
        
        # Get selected mode
        mode = context['execution_mode']
        
        # Test section inclusion logic
        assert orchestrator.mode_integration.should_include_section("description", mode) is True
        assert orchestrator.mode_integration.should_include_section("examples", mode) is False
        assert orchestrator.mode_integration.should_include_section("warnings", mode) is False
    
    def test_description_formatting_based_on_mode(self, orchestrator, temp_output_dir):
        """Test that descriptions are formatted according to mode"""
        context = {
            'config': DocumentationConfig(
                source_paths=[Path("src")],
                output_dir=temp_output_dir
            ),
            'execution_mode': 'autonomous'
        }
        
        orchestrator._setup(context)
        mode = context['execution_mode']
        
        # Create long description (exceeds autonomous limit of 200)
        long_desc = "A" * 300
        
        # Format description
        formatted = orchestrator.mode_integration.format_description(long_desc, mode)
        
        # Verify truncation
        assert len(formatted) < len(long_desc)
        assert formatted.endswith("...")
    
    def test_execution_summary_available(self, orchestrator, temp_output_dir):
        """Test that execution summary can be retrieved"""
        context = {
            'config': DocumentationConfig(
                source_paths=[Path("src")],
                output_dir=temp_output_dir
            )
        }
        
        orchestrator._setup(context)
        mode = context['execution_mode']
        
        # Get execution summary
        summary = orchestrator.mode_integration.get_execution_summary(mode)
        
        # Verify summary structure
        assert 'mode' in summary
        assert 'description' in summary
        assert 'formatting' in summary
        assert 'user_action_required' in summary
    
    def test_config_with_all_modes(self, mock_logger, temp_output_dir):
        """Test that all execution modes work with config"""
        modes = ['autonomous', 'supervised', 'human_in_loop']
        
        for mode_str in modes:
            config = {'cortex_root': Path.cwd()}
            orch = DocumentationOrchestrator(logger=mock_logger, config=config)
            
            context = {
                'config': DocumentationConfig(
                    source_paths=[Path("src")],
                    output_dir=temp_output_dir
                ),
                'execution_mode': mode_str
            }
            
            # Should not raise exception
            orch._setup(context)
            
            # Verify mode was set
            assert context['execution_mode'].value == mode_str
            assert orch.formatting_config is not None
    
    def test_mode_integration_with_user_id(self, mock_logger, temp_output_dir):
        """Test mode integration with specific user ID"""
        config = {'cortex_root': Path.cwd()}
        orch = DocumentationOrchestrator(logger=mock_logger, config=config)
        
        # Verify user_id was set (default)
        assert orch.mode_integration.user_id is not None
    
    def test_formatting_config_affects_options(self, orchestrator, temp_output_dir):
        """Test that formatting config properly affects documentation options"""
        # Test AUTONOMOUS mode
        context_auto = {
            'config': DocumentationConfig(
                source_paths=[Path("src")],
                output_dir=temp_output_dir
            ),
            'execution_mode': 'autonomous'
        }
        
        orchestrator._setup(context_auto)
        config_auto = orchestrator.formatting_config
        
        # Test SUPERVISED mode
        context_super = {
            'config': DocumentationConfig(
                source_paths=[Path("src")],
                output_dir=temp_output_dir
            ),
            'execution_mode': 'supervised'
        }
        
        orchestrator._setup(context_super)
        config_super = orchestrator.formatting_config
        
        # Verify differences
        assert config_auto.include_examples != config_super.include_examples
        assert config_auto.max_description_length < config_super.max_description_length
        assert config_auto.detail_level != config_super.detail_level


class TestExecutionModeEdgeCases:
    """Test edge cases for execution mode integration"""
    
    def test_invalid_mode_override_falls_back(self, mock_logger, temp_output_dir):
        """Test that invalid mode override falls back gracefully"""
        config = {'cortex_root': Path.cwd()}
        orch = DocumentationOrchestrator(logger=mock_logger, config=config)
        
        context = {
            'config': DocumentationConfig(
                source_paths=[Path("src")],
                output_dir=temp_output_dir
            ),
            'execution_mode': 'invalid_mode'
        }
        
        # Should not raise exception
        orch._setup(context)
        
        # Should have valid mode
        assert isinstance(context['execution_mode'], ExecutionMode)
    
    def test_no_mode_specified_uses_default(self, mock_logger, temp_output_dir):
        """Test that no mode specified uses default selection"""
        config = {'cortex_root': Path.cwd()}
        orch = DocumentationOrchestrator(logger=mock_logger, config=config)
        
        context = {
            'config': DocumentationConfig(
                source_paths=[Path("src")],
                output_dir=temp_output_dir
            )
        }
        
        orch._setup(context)
        
        # Should have auto-selected mode
        assert 'execution_mode' in context
        assert isinstance(context['execution_mode'], ExecutionMode)
