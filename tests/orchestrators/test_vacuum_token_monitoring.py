"""
Test token monitoring integration in VacuumOrchestratorV2.

Validates:
- Token usage checked after each phase
- User warnings generated at threshold
- Continuation prompt integration
- Message formatting with warnings

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from src.orchestrators.vacuum.vacuum_orchestrator_v2 import VacuumOrchestratorV2
from src.orchestrators.base.base_orchestrator_v4_1 import PhaseStatus


class TestVacuumTokenMonitoring:
    """Test token monitoring in VacuumOrchestratorV2."""
    
    @pytest.fixture
    def mock_config(self, tmp_path):
        """Create mock configuration."""
        config = {
            'orchestrator_name': 'vacuum_v2',
            'orchestrator_version': '2.0',
            'execution': {
                'token_warning_threshold': 5000  # Low threshold for testing
            },
            'cleanup_categories': {
                'temp_files': {
                    'patterns': ['*.tmp', '*.temp'],
                    'risk_level': 'SAFE'
                }
            },
            'safety': {
                'size_threshold_mb': 10
            },
            'exclusions': ['.git', 'node_modules']
        }
        
        config_path = tmp_path / "vacuum-config.yaml"
        return config, str(config_path)
    
    @pytest.fixture
    def orchestrator(self, mock_config, tmp_path):
        """Create VacuumOrchestratorV2 instance."""
        config, config_path = mock_config
        
        with patch('src.orchestrators.base.base_orchestrator_v4_1.load_yaml_config') as mock_load:
            mock_load.return_value = config
            
            orchestrator = VacuumOrchestratorV2(
                config_path=config_path
            )
            
            return orchestrator
    
    def test_token_check_called_after_phases(self, orchestrator, tmp_path):
        """Test check_token_usage() called after each phase."""
        target_path = tmp_path / "test_project"
        target_path.mkdir()
        
        # Create test file
        (target_path / "test.tmp").write_text("test")
        
        with patch.object(orchestrator, 'check_token_usage') as mock_check:
            mock_check.return_value = {
                'estimated_tokens': 1000,
                'threshold': 5000,
                'should_warn': False,
                'percentage': 20.0,
                'user_message': None
            }
            
            # Mock phase methods to avoid full execution
            with patch.object(orchestrator, '_phase_discovery') as mock_discovery, \
                 patch.object(orchestrator, '_phase_analysis') as mock_analysis, \
                 patch.object(orchestrator, '_phase_planning') as mock_planning, \
                 patch.object(orchestrator, '_phase_approval_dry_run') as mock_approval:
                
                # Set up mock return values
                mock_result = Mock()
                mock_result.status = PhaseStatus.COMPLETED
                mock_result.artifacts = []
                mock_result.errors = []
                
                mock_discovery.return_value = mock_result
                mock_analysis.return_value = mock_result
                mock_planning.return_value = mock_result
                mock_approval.return_value = mock_result
                
                # Execute dry-run
                result = orchestrator.execute(
                    user_request="vacuum test",
                    target_path=target_path,
                    dry_run=True
                )
                
                # Verify check_token_usage called 4 times:
                # After Discovery, Analysis, Planning, and dry-run completion
                assert mock_check.call_count == 4
    
    def test_warning_message_appended_to_response(self, orchestrator, tmp_path):
        """Test token warning message appended to completion message."""
        target_path = tmp_path / "test_project"
        target_path.mkdir()
        
        # Create test file
        (target_path / "test.tmp").write_text("test")
        
        warning_message = (
            "\n\n⚠️ **TOKEN WARNING**: Estimated 5,000 tokens "
            "(100.0% of 5,000 threshold).\n\n"
            "📋 **Continuation prompt updated**: `tracking/CONTINUATION-PROMPT.md`\n"
            "💡 **Recommendation**: Consider copying the continuation prompt "
            "for session handoff to maintain context across chat sessions."
        )
        
        with patch.object(orchestrator, 'check_token_usage') as mock_check:
            # First 3 calls: no warning
            # Last call (dry-run completion): warning
            mock_check.side_effect = [
                {'estimated_tokens': 1000, 'threshold': 5000, 'should_warn': False, 'percentage': 20.0, 'user_message': None},
                {'estimated_tokens': 2000, 'threshold': 5000, 'should_warn': False, 'percentage': 40.0, 'user_message': None},
                {'estimated_tokens': 3000, 'threshold': 5000, 'should_warn': False, 'percentage': 60.0, 'user_message': None},
                {'estimated_tokens': 5000, 'threshold': 5000, 'should_warn': True, 'percentage': 100.0, 'user_message': warning_message}
            ]
            
            # Mock phase methods
            with patch.object(orchestrator, '_phase_discovery') as mock_discovery, \
                 patch.object(orchestrator, '_phase_analysis') as mock_analysis, \
                 patch.object(orchestrator, '_phase_planning') as mock_planning, \
                 patch.object(orchestrator, '_phase_approval_dry_run') as mock_approval:
                
                mock_result = Mock()
                mock_result.status = PhaseStatus.COMPLETED
                mock_result.artifacts = []
                mock_result.errors = []
                
                mock_discovery.return_value = mock_result
                mock_analysis.return_value = mock_result
                mock_planning.return_value = mock_result
                mock_approval.return_value = mock_result
                
                # Execute
                result = orchestrator.execute(
                    user_request="vacuum test",
                    target_path=target_path,
                    dry_run=True
                )
                
                # Verify warning message appended
                assert warning_message in result.message
                assert "Dry-run completed successfully" in result.message
    
    def test_warning_logged_when_triggered(self, orchestrator, tmp_path, caplog):
        """Test token warning logged for debugging."""
        target_path = tmp_path / "test_project"
        target_path.mkdir()
        
        with patch.object(orchestrator, 'check_token_usage') as mock_check:
            mock_check.return_value = {
                'estimated_tokens': 5000,
                'threshold': 5000,
                'should_warn': True,
                'percentage': 100.0,
                'user_message': "⚠️ TOKEN WARNING"
            }
            
            with patch.object(orchestrator, '_phase_discovery') as mock_discovery, \
                 patch.object(orchestrator, '_phase_analysis') as mock_analysis, \
                 patch.object(orchestrator, '_phase_planning') as mock_planning, \
                 patch.object(orchestrator, '_phase_approval_dry_run') as mock_approval:
                
                mock_result = Mock()
                mock_result.status = PhaseStatus.COMPLETED
                mock_result.artifacts = []
                mock_result.errors = []
                
                mock_discovery.return_value = mock_result
                mock_analysis.return_value = mock_result
                mock_planning.return_value = mock_result
                mock_approval.return_value = mock_result
                
                orchestrator.execute(
                    user_request="vacuum test",
                    target_path=target_path,
                    dry_run=True
                )
                
                # Verify warning logged
                assert any("Token warning triggered" in record.message for record in caplog.records)
    
    def test_no_warning_below_threshold(self, orchestrator, tmp_path):
        """Test no warning when below threshold."""
        target_path = tmp_path / "test_project"
        target_path.mkdir()
        
        with patch.object(orchestrator, 'check_token_usage') as mock_check:
            mock_check.return_value = {
                'estimated_tokens': 1000,
                'threshold': 5000,
                'should_warn': False,
                'percentage': 20.0,
                'user_message': None
            }
            
            with patch.object(orchestrator, '_phase_discovery') as mock_discovery, \
                 patch.object(orchestrator, '_phase_analysis') as mock_analysis, \
                 patch.object(orchestrator, '_phase_planning') as mock_planning, \
                 patch.object(orchestrator, '_phase_approval_dry_run') as mock_approval:
                
                mock_result = Mock()
                mock_result.status = PhaseStatus.COMPLETED
                mock_result.artifacts = []
                mock_result.errors = []
                
                mock_discovery.return_value = mock_result
                mock_analysis.return_value = mock_result
                mock_planning.return_value = mock_result
                mock_approval.return_value = mock_result
                
                result = orchestrator.execute(
                    user_request="vacuum test",
                    target_path=target_path,
                    dry_run=True
                )
                
                # Verify no warning in message
                assert "TOKEN WARNING" not in result.message
                assert "CONTINUATION-PROMPT" not in result.message
