"""
TDD Test Suite: Deployment Orchestrator CLI

RED Phase: Tests for unified deployment CLI

Test Coverage:
1. CLI argument parsing (deploy, validate-gates, rollback, status, history, metrics)
2. Deploy command with strategy options (canary, blue-green, direct)
3. Dry-run mode (validation without execution)
4. Gate validation command
5. Rollback command with phase targeting
6. Status command (current deployment state)
7. History command (past deployments)
8. Metrics command (deployment analytics)
9. Admin-only features (skip-gates)
10. Checkpoint resume functionality
11. Error handling and user feedback
12. Integration with deployment orchestrator
"""

import pytest
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock, call
from io import StringIO

from src.deployment.deployment_cli import (
    DeploymentCLI,
    parse_args,
    handle_deploy_command,
    handle_validate_gates_command,
    handle_rollback_command,
    handle_status_command,
    handle_history_command,
    handle_metrics_command,
    main,
)


class TestCLIArgumentParsing:
    """Test CLI argument parsing"""

    def test_parse_deploy_command_basic(self):
        """Should parse basic deploy command"""
        args = parse_args(['deploy'])
        
        assert args.command == 'deploy'
        assert args.strategy is None
        assert args.dry_run is False

    def test_parse_deploy_with_canary_strategy(self):
        """Should parse deploy command with canary strategy"""
        args = parse_args(['deploy', '--strategy', 'canary'])
        
        assert args.command == 'deploy'
        assert args.strategy == 'canary'

    def test_parse_deploy_with_blue_green_strategy(self):
        """Should parse deploy command with blue-green strategy"""
        args = parse_args(['deploy', '--strategy', 'blue-green'])
        
        assert args.command == 'deploy'
        assert args.strategy == 'blue-green'

    def test_parse_deploy_with_dry_run(self):
        """Should parse deploy command with dry-run flag"""
        args = parse_args(['deploy', '--dry-run'])
        
        assert args.command == 'deploy'
        assert args.dry_run is True

    def test_parse_deploy_with_skip_gates(self):
        """Should parse deploy command with skip-gates flag"""
        args = parse_args(['deploy', '--skip-gates'])
        
        assert args.command == 'deploy'
        assert args.skip_gates is True

    def test_parse_validate_gates_command(self):
        """Should parse validate-gates command"""
        args = parse_args(['validate-gates'])
        
        assert args.command == 'validate-gates'

    def test_parse_rollback_command(self):
        """Should parse rollback command"""
        args = parse_args(['rollback'])
        
        assert args.command == 'rollback'
        assert args.phase is None

    def test_parse_rollback_with_phase(self):
        """Should parse rollback command with specific phase"""
        args = parse_args(['rollback', '--phase', 'BUILD'])
        
        assert args.command == 'rollback'
        assert args.phase == 'BUILD'

    def test_parse_status_command(self):
        """Should parse status command"""
        args = parse_args(['status'])
        
        assert args.command == 'status'

    def test_parse_history_command(self):
        """Should parse history command"""
        args = parse_args(['history'])
        
        assert args.command == 'history'
        assert args.limit == 10  # Default limit

    def test_parse_history_with_limit(self):
        """Should parse history command with custom limit"""
        args = parse_args(['history', '--limit', '20'])
        
        assert args.command == 'history'
        assert args.limit == 20

    def test_parse_metrics_command(self):
        """Should parse metrics command"""
        args = parse_args(['metrics'])
        
        assert args.command == 'metrics'
        assert args.days == 7  # Default 7 days


class TestDeployCommand:
    """Test deploy command execution"""

    @patch('src.deployment.deployment_cli.DeployOrchestrator')
    def test_deploy_basic_execution(self, mock_orchestrator):
        """Should execute basic deployment"""
        cli = DeploymentCLI()
        
        mock_instance = mock_orchestrator.return_value
        mock_instance.deploy.return_value = {
            'success': True,
            'deployment_id': 'deploy-123',
            'duration': 180
        }
        
        result = cli.deploy()
        
        assert result['success'] is True
        assert 'deployment_id' in result
        mock_instance.deploy.assert_called_once()

    @patch('src.deployment.deployment_cli.DeployOrchestrator')
    def test_deploy_with_canary_strategy(self, mock_orchestrator):
        """Should execute deployment with canary strategy"""
        cli = DeploymentCLI()
        
        mock_instance = mock_orchestrator.return_value
        mock_instance.deploy.return_value = {
            'success': True,
            'strategy': 'canary',
            'stages_completed': 3
        }
        
        result = cli.deploy(strategy='canary')
        
        assert result['success'] is True
        assert result['strategy'] == 'canary'
        mock_instance.deploy.assert_called_once_with(strategy='canary')

    @patch('src.deployment.deployment_cli.DeployOrchestrator')
    def test_deploy_dry_run_mode(self, mock_orchestrator):
        """Should execute dry-run without actual deployment"""
        cli = DeploymentCLI()
        
        mock_instance = mock_orchestrator.return_value
        mock_instance.validate_deployment.return_value = {
            'valid': True,
            'gates_passed': 19,
            'gates_total': 19
        }
        
        result = cli.deploy(dry_run=True)
        
        assert result['valid'] is True
        mock_instance.validate_deployment.assert_called_once()
        mock_instance.deploy.assert_not_called()

    @patch('src.deployment.deployment_cli.DeployOrchestrator')
    def test_deploy_skip_gates_admin_only(self, mock_orchestrator):
        """Should allow skip-gates for admin users"""
        cli = DeploymentCLI(is_admin=True)
        
        mock_instance = mock_orchestrator.return_value
        mock_instance.deploy.return_value = {'success': True}
        
        result = cli.deploy(skip_gates=True)
        
        assert result['success'] is True
        mock_instance.deploy.assert_called_once_with(skip_gates=True)

    def test_deploy_skip_gates_non_admin_denied(self):
        """Should deny skip-gates for non-admin users"""
        cli = DeploymentCLI(is_admin=False)
        
        with pytest.raises(PermissionError, match="Admin privileges required"):
            cli.deploy(skip_gates=True)

    @patch('src.deployment.deployment_cli.DeployOrchestrator')
    def test_deploy_resume_from_checkpoint(self, mock_orchestrator):
        """Should resume deployment from checkpoint"""
        cli = DeploymentCLI()
        
        mock_instance = mock_orchestrator.return_value
        mock_instance.resume_from_checkpoint.return_value = {
            'success': True,
            'resumed_from': 'BUILD'
        }
        
        result = cli.deploy(checkpoint_id='checkpoint-123')
        
        assert result['success'] is True
        assert result['resumed_from'] == 'BUILD'


class TestValidateGatesCommand:
    """Test validate-gates command"""

    @patch('src.deployment.deployment_cli.GateValidator')
    def test_validate_all_gates(self, mock_validator):
        """Should validate all deployment gates"""
        cli = DeploymentCLI()
        
        mock_instance = mock_validator.return_value
        mock_instance.validate_all_gates.return_value = {
            'passed': True,
            'gates_passed': 19,
            'gates_failed': 0,
            'gates_total': 19
        }
        
        result = cli.validate_gates()
        
        assert result['passed'] is True
        assert result['gates_passed'] == 19

    @patch('src.deployment.deployment_cli.GateValidator')
    def test_validate_gates_with_failures(self, mock_validator):
        """Should report gate validation failures"""
        cli = DeploymentCLI()
        
        mock_instance = mock_validator.return_value
        mock_instance.validate_all_gates.return_value = {
            'passed': False,
            'gates_passed': 17,
            'gates_failed': 2,
            'gates_total': 19,
            'failures': [
                {'gate': 'test_coverage', 'reason': 'Coverage below 80%'},
                {'gate': 'brain_schema', 'reason': 'Schema mismatch'}
            ]
        }
        
        result = cli.validate_gates()
        
        assert result['passed'] is False
        assert len(result['failures']) == 2

    @patch('src.deployment.deployment_cli.GateValidator')
    def test_validate_specific_gate_category(self, mock_validator):
        """Should validate specific gate category"""
        cli = DeploymentCLI()
        
        mock_instance = mock_validator.return_value
        mock_instance.validate_category.return_value = {
            'passed': True,
            'category': 'critical',
            'gates_passed': 5
        }
        
        result = cli.validate_gates(category='critical')
        
        assert result['passed'] is True
        assert result['category'] == 'critical'


class TestRollbackCommand:
    """Test rollback command"""

    @patch('src.deployment.deployment_cli.DeploymentRollbackManager')
    def test_rollback_latest_deployment(self, mock_rollback):
        """Should rollback to latest snapshot"""
        cli = DeploymentCLI()
        
        mock_instance = mock_rollback.return_value
        mock_instance.rollback_latest.return_value = {
            'success': True,
            'rolled_back_to': 'deploy-122',
            'rollback_type': 'FULL'
        }
        
        result = cli.rollback()
        
        assert result['success'] is True
        assert 'rolled_back_to' in result

    @patch('src.deployment.deployment_cli.DeploymentRollbackManager')
    def test_rollback_to_specific_phase(self, mock_rollback):
        """Should rollback to specific phase"""
        cli = DeploymentCLI()
        
        mock_instance = mock_rollback.return_value
        mock_instance.rollback_to_phase.return_value = {
            'success': True,
            'phase': 'BUILD',
            'rollback_type': 'CODE_ONLY'
        }
        
        result = cli.rollback(phase='BUILD')
        
        assert result['success'] is True
        assert result['phase'] == 'BUILD'

    @patch('src.deployment.deployment_cli.DeploymentRollbackManager')
    def test_rollback_validation(self, mock_rollback):
        """Should validate system after rollback"""
        cli = DeploymentCLI()
        
        mock_instance = mock_rollback.return_value
        mock_instance.rollback_latest.return_value = {
            'success': True,
            'validation': {
                'git_status': 'clean',
                'tests_passing': True,
                'gates_valid': True
            }
        }
        
        result = cli.rollback()
        
        assert result['validation']['tests_passing'] is True


class TestStatusCommand:
    """Test status command"""

    @patch('src.deployment.deployment_cli.DeployOrchestrator')
    def test_status_active_deployment(self, mock_orchestrator):
        """Should show status of active deployment"""
        cli = DeploymentCLI()
        
        mock_instance = mock_orchestrator.return_value
        mock_instance.get_status.return_value = {
            'active': True,
            'deployment_id': 'deploy-123',
            'current_phase': 'DEPLOY',
            'progress': '60%',
            'started_at': '2025-12-09T18:00:00'
        }
        
        result = cli.status()
        
        assert result['active'] is True
        assert result['current_phase'] == 'DEPLOY'
        assert result['progress'] == '60%'

    @patch('src.deployment.deployment_cli.DeployOrchestrator')
    def test_status_no_active_deployment(self, mock_orchestrator):
        """Should indicate no active deployment"""
        cli = DeploymentCLI()
        
        mock_instance = mock_orchestrator.return_value
        mock_instance.get_status.return_value = {
            'active': False,
            'last_deployment': 'deploy-122',
            'last_status': 'COMPLETED'
        }
        
        result = cli.status()
        
        assert result['active'] is False
        assert 'last_deployment' in result


class TestHistoryCommand:
    """Test history command"""

    @patch('src.deployment.deployment_cli.DeploymentMetricsCollector')
    def test_history_recent_deployments(self, mock_metrics):
        """Should show recent deployment history"""
        cli = DeploymentCLI()
        
        mock_instance = mock_metrics.return_value
        mock_instance.get_deployment_history.return_value = [
            {
                'deployment_id': 'deploy-123',
                'timestamp': '2025-12-09T18:00:00',
                'status': 'COMPLETED',
                'duration': 180
            },
            {
                'deployment_id': 'deploy-122',
                'timestamp': '2025-12-09T17:00:00',
                'status': 'COMPLETED',
                'duration': 165
            }
        ]
        
        result = cli.history(limit=10)
        
        assert len(result) == 2
        assert result[0]['deployment_id'] == 'deploy-123'

    @patch('src.deployment.deployment_cli.DeploymentMetricsCollector')
    def test_history_filter_by_status(self, mock_metrics):
        """Should filter history by deployment status"""
        cli = DeploymentCLI()
        
        mock_instance = mock_metrics.return_value
        mock_instance.get_deployment_history.return_value = [
            {'deployment_id': 'deploy-120', 'status': 'FAILED'},
            {'deployment_id': 'deploy-118', 'status': 'FAILED'}
        ]
        
        result = cli.history(status='FAILED')
        
        assert all(d['status'] == 'FAILED' for d in result)


class TestMetricsCommand:
    """Test metrics command"""

    @patch('src.deployment.deployment_cli.DeploymentMetricsCollector')
    def test_metrics_summary(self, mock_metrics):
        """Should show deployment metrics summary"""
        cli = DeploymentCLI()
        
        mock_instance = mock_metrics.return_value
        mock_instance.generate_report.return_value = {
            'average_duration': 175.5,
            'success_rate': 0.95,
            'total_deployments': 20,
            'rollback_count': 1
        }
        
        result = cli.metrics(days=7)
        
        assert result['success_rate'] == 0.95
        assert result['total_deployments'] == 20

    @patch('src.deployment.deployment_cli.DeploymentMetricsCollector')
    def test_metrics_health_score(self, mock_metrics):
        """Should calculate deployment health score"""
        cli = DeploymentCLI()
        
        mock_instance = mock_metrics.return_value
        mock_instance.calculate_health_score.return_value = 85
        
        score = cli.get_health_score(days=7)
        
        assert score == 85

    @patch('src.deployment.deployment_cli.DeploymentMetricsCollector')
    def test_metrics_with_alerts(self, mock_metrics):
        """Should include alerts in metrics report"""
        cli = DeploymentCLI()
        
        mock_instance = mock_metrics.return_value
        mock_instance.check_health_thresholds.return_value = [
            {
                'level': 'WARNING',
                'message': 'Average deployment duration exceeds 5 minutes'
            }
        ]
        
        alerts = cli.check_metrics_alerts(days=7)
        
        assert len(alerts) == 1
        assert alerts[0]['level'] == 'WARNING'


class TestCLIOutput:
    """Test CLI output formatting"""

    def test_format_deploy_success_output(self):
        """Should format successful deployment output"""
        cli = DeploymentCLI()
        
        result = {
            'success': True,
            'deployment_id': 'deploy-123',
            'duration': 180,
            'gates_passed': 19
        }
        
        output = cli.format_output(result, command='deploy')
        
        assert 'SUCCESS' in output
        assert 'deploy-123' in output
        assert '180' in output

    def test_format_validation_failure_output(self):
        """Should format validation failure output with remediation"""
        cli = DeploymentCLI()
        
        result = {
            'passed': False,
            'failures': [
                {
                    'gate': 'test_coverage',
                    'reason': 'Coverage below 80%',
                    'remediation': 'Run: pytest --cov=src tests/'
                }
            ]
        }
        
        output = cli.format_output(result, command='validate-gates')
        
        assert 'FAILED' in output
        assert 'test_coverage' in output
        assert 'pytest' in output

    def test_format_metrics_table(self):
        """Should format metrics as table"""
        cli = DeploymentCLI()
        
        metrics = {
            'average_duration': 175.5,
            'success_rate': 0.95,
            'total_deployments': 20
        }
        
        output = cli.format_metrics_table(metrics)
        
        assert 'Average Duration' in output
        assert '175.5' in output
        assert '95%' in output


class TestCLIIntegration:
    """Test CLI integration with deployment system"""

    @patch('src.deployment.deployment_cli.DeployOrchestrator')
    @patch('src.deployment.deployment_cli.DeploymentStrategyManager')
    def test_full_deployment_workflow(self, mock_strategy, mock_orchestrator):
        """Should execute full deployment workflow through CLI"""
        mock_orch_instance = mock_orchestrator.return_value
        mock_orch_instance.deploy.return_value = {
            'success': True,
            'deployment_id': 'deploy-123'
        }
        
        # Simulate CLI invocation: deploy --strategy canary --dry-run
        sys.argv = ['deployment_cli.py', 'deploy', '--strategy', 'canary', '--dry-run']
        
        with patch('sys.exit'):
            main()

    @patch('src.deployment.deployment_cli.GateValidator')
    def test_validate_before_deploy_workflow(self, mock_validator):
        """Should validate gates before deployment"""
        cli = DeploymentCLI()
        
        mock_instance = mock_validator.return_value
        mock_instance.validate_all_gates.return_value = {
            'passed': True,
            'gates_passed': 19
        }
        
        # Validate first
        validation = cli.validate_gates()
        assert validation['passed'] is True
        
        # Then deploy if validation passed
        if validation['passed']:
            with patch('src.deployment.deployment_cli.DeployOrchestrator') as mock_deploy:
                mock_deploy.return_value.deploy.return_value = {'success': True}
                result = cli.deploy()
                assert result['success'] is True


class TestErrorHandling:
    """Test CLI error handling"""

    def test_handle_deployment_failure(self):
        """Should handle deployment failure gracefully"""
        cli = DeploymentCLI()
        
        with patch('src.deployment.deployment_cli.DeployOrchestrator') as mock_orch:
            mock_orch.return_value.deploy.side_effect = Exception("Deployment failed")
            
            result = cli.deploy()
            
            assert result['success'] is False
            assert 'error' in result

    def test_handle_invalid_strategy(self):
        """Should reject invalid deployment strategy"""
        with pytest.raises(ValueError, match="Invalid strategy"):
            parse_args(['deploy', '--strategy', 'invalid'])

    def test_handle_missing_checkpoint(self):
        """Should handle missing checkpoint gracefully"""
        cli = DeploymentCLI()
        
        with patch('src.deployment.deployment_cli.DeployOrchestrator') as mock_orch:
            mock_orch.return_value.resume_from_checkpoint.return_value = {
                'success': False,
                'reason': 'checkpoint_not_found'
            }
            
            result = cli.deploy(checkpoint_id='missing-123')
            
            assert result['success'] is False
            assert 'checkpoint_not_found' in result['reason']
