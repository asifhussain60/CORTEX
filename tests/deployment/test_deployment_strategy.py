"""
TDD Test Suite: Deployment Strategy System

RED Phase: Tests for progressive deployment strategies (canary, blue-green)

Test Coverage:
1. Strategy configuration loading and validation
2. Canary deployment (staged rollout: 10% → 50% → 100%)
3. Blue-green deployment (zero-downtime switching)
4. Smoke test execution between stages
5. Automatic rollback on smoke test failures
6. Strategy selection and recommendation
7. Deployment phase management
8. Health checks during progressive rollout
9. Traffic routing simulation
10. End-to-end progressive deployment workflows
"""

import pytest
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List
from unittest.mock import Mock, patch, MagicMock
from dataclasses import asdict

from src.deployment.deployment_strategy import (
    DeploymentStrategy,
    StrategyType,
    DeploymentStage,
    StageStatus,
    SmokeTestResult,
    StrategyConfig,
    CanaryConfig,
    BlueGreenConfig,
    DeploymentStrategyManager,
    load_strategy_config,
    recommend_strategy,
)


class TestStrategyConfigurationLoading:
    """Test strategy configuration loading and validation"""

    def test_load_default_config(self, tmp_path):
        """Should load default strategy configuration"""
        config_path = tmp_path / "deployment-strategies.yaml"
        
        manager = DeploymentStrategyManager(str(tmp_path))
        config = manager.get_default_config()
        
        assert config is not None
        assert 'canary' in config
        assert 'blue_green' in config
        assert 'smoke_tests' in config

    def test_validate_canary_config(self):
        """Should validate canary deployment configuration"""
        config = CanaryConfig(
            stages=[10, 50, 100],
            stage_duration_minutes=5,
            health_check_interval_seconds=30,
            smoke_tests_required=True,
            auto_rollback_on_failure=True
        )
        
        assert len(config.stages) == 3
        assert config.stages == [10, 50, 100]
        assert config.stage_duration_minutes == 5

    def test_validate_blue_green_config(self):
        """Should validate blue-green deployment configuration"""
        config = BlueGreenConfig(
            warmup_duration_minutes=2,
            smoke_tests_required=True,
            auto_switch_on_success=True,
            keep_old_environment_hours=24
        )
        
        assert config.warmup_duration_minutes == 2
        assert config.auto_switch_on_success is True
        assert config.keep_old_environment_hours == 24

    def test_invalid_canary_stages(self):
        """Should reject invalid canary stage percentages"""
        with pytest.raises(ValueError, match="stages must end with 100"):
            CanaryConfig(
                stages=[10, 50, 90],  # Missing 100
                stage_duration_minutes=5
            )

    def test_invalid_stage_order(self):
        """Should reject non-ascending stage percentages"""
        with pytest.raises(ValueError, match="stages must be in ascending order"):
            CanaryConfig(
                stages=[50, 10, 100],  # Wrong order
                stage_duration_minutes=5
            )


class TestCanaryDeployment:
    """Test canary deployment progressive rollout"""

    def test_canary_initialization(self):
        """Should initialize canary deployment with correct stages"""
        config = CanaryConfig(stages=[10, 50, 100], stage_duration_minutes=5)
        strategy = DeploymentStrategy(
            strategy_type=StrategyType.CANARY,
            deployment_id="deploy-123",
            config=config
        )
        
        assert strategy.strategy_type == StrategyType.CANARY
        assert len(strategy.stages) == 3
        assert strategy.current_stage_index == 0
        assert strategy.status == StageStatus.PENDING

    def test_canary_stage_progression(self):
        """Should progress through canary stages: 10% → 50% → 100%"""
        manager = DeploymentStrategyManager()
        strategy = manager.create_strategy(
            StrategyType.CANARY,
            deployment_id="deploy-123"
        )
        
        # Stage 1: 10%
        stage1 = strategy.get_current_stage()
        assert stage1.percentage == 10
        assert stage1.status == StageStatus.PENDING
        
        # Advance to Stage 2: 50%
        strategy.advance_stage()
        stage2 = strategy.get_current_stage()
        assert stage2.percentage == 50
        
        # Advance to Stage 3: 100%
        strategy.advance_stage()
        stage3 = strategy.get_current_stage()
        assert stage3.percentage == 100

    def test_canary_smoke_tests_between_stages(self):
        """Should run smoke tests before advancing to next stage"""
        manager = DeploymentStrategyManager()
        strategy = manager.create_strategy(
            StrategyType.CANARY,
            deployment_id="deploy-123"
        )
        
        # Run smoke tests for 10% stage
        smoke_result = manager.run_smoke_tests(strategy, stage_index=0)
        
        assert smoke_result is not None
        assert smoke_result.stage_percentage == 10
        assert isinstance(smoke_result.passed, bool)
        assert isinstance(smoke_result.tests_run, int)

    def test_canary_auto_rollback_on_smoke_failure(self):
        """Should automatically rollback if smoke tests fail"""
        manager = DeploymentStrategyManager()
        strategy = manager.create_strategy(
            StrategyType.CANARY,
            deployment_id="deploy-123"
        )
        
        # Simulate smoke test failure at 10% stage
        with patch.object(manager, '_execute_smoke_tests') as mock_smoke:
            mock_smoke.return_value = SmokeTestResult(
                stage_percentage=10,
                passed=False,
                tests_run=5,
                tests_passed=3,
                tests_failed=2,
                failure_reasons=["Health check timeout", "API error rate high"]
            )
            
            result = manager.execute_canary_stage(strategy, stage_index=0)
            
            assert result['rollback_triggered'] is True
            assert result['reason'] == 'smoke_test_failure'

    def test_canary_health_checks_during_stage(self):
        """Should perform health checks during stage duration"""
        manager = DeploymentStrategyManager()
        strategy = manager.create_strategy(
            StrategyType.CANARY,
            deployment_id="deploy-123"
        )
        
        # Monitor health during 10% stage (5 minute duration)
        health_checks = manager.monitor_stage_health(
            strategy,
            stage_index=0,
            duration_minutes=5
        )
        
        assert len(health_checks) > 0
        assert all('timestamp' in check for check in health_checks)
        assert all('healthy' in check for check in health_checks)

    def test_canary_complete_rollout(self):
        """Should complete full canary rollout: 10% → 50% → 100%"""
        manager = DeploymentStrategyManager()
        
        with patch.object(manager, '_execute_smoke_tests') as mock_smoke:
            # All smoke tests pass
            mock_smoke.return_value = SmokeTestResult(
                stage_percentage=100,
                passed=True,
                tests_run=5,
                tests_passed=5,
                tests_failed=0
            )
            
            result = manager.execute_canary_deployment(
                deployment_id="deploy-123"
            )
            
            assert result['success'] is True
            assert result['stages_completed'] == 3
            assert result['final_percentage'] == 100


class TestBlueGreenDeployment:
    """Test blue-green deployment zero-downtime switching"""

    def test_blue_green_initialization(self):
        """Should initialize blue-green deployment with two environments"""
        config = BlueGreenConfig(
            warmup_duration_minutes=2,
            smoke_tests_required=True
        )
        strategy = DeploymentStrategy(
            strategy_type=StrategyType.BLUE_GREEN,
            deployment_id="deploy-123",
            config=config
        )
        
        assert strategy.strategy_type == StrategyType.BLUE_GREEN
        assert 'blue_environment' in strategy.metadata
        assert 'green_environment' in strategy.metadata

    def test_deploy_to_inactive_environment(self):
        """Should deploy new version to inactive (green) environment"""
        manager = DeploymentStrategyManager()
        strategy = manager.create_strategy(
            StrategyType.BLUE_GREEN,
            deployment_id="deploy-123"
        )
        
        # Current active: blue, deploy to: green
        result = manager.deploy_to_green_environment(strategy)
        
        assert result['success'] is True
        assert result['target_environment'] == 'green'
        assert result['active_environment'] == 'blue'  # Still blue

    def test_warmup_green_environment(self):
        """Should warm up green environment before switching"""
        manager = DeploymentStrategyManager()
        strategy = manager.create_strategy(
            StrategyType.BLUE_GREEN,
            deployment_id="deploy-123"
        )
        
        warmup_result = manager.warmup_environment(
            strategy,
            environment='green',
            duration_minutes=2
        )
        
        assert warmup_result['warmed_up'] is True
        assert warmup_result['duration_minutes'] == 2

    def test_smoke_tests_on_green_environment(self):
        """Should run smoke tests on green environment before switch"""
        manager = DeploymentStrategyManager()
        strategy = manager.create_strategy(
            StrategyType.BLUE_GREEN,
            deployment_id="deploy-123"
        )
        
        with patch.object(manager, '_execute_smoke_tests') as mock_smoke:
            mock_smoke.return_value = SmokeTestResult(
                stage_percentage=100,
                passed=True,
                tests_run=10,
                tests_passed=10,
                tests_failed=0
            )
            
            smoke_result = manager.run_smoke_tests_on_environment(
                strategy,
                environment='green'
            )
            
            assert smoke_result.passed is True

    def test_switch_traffic_to_green(self):
        """Should switch traffic from blue to green environment"""
        manager = DeploymentStrategyManager()
        strategy = manager.create_strategy(
            StrategyType.BLUE_GREEN,
            deployment_id="deploy-123"
        )
        
        switch_result = manager.switch_active_environment(
            strategy,
            from_env='blue',
            to_env='green'
        )
        
        assert switch_result['success'] is True
        assert switch_result['old_active'] == 'blue'
        assert switch_result['new_active'] == 'green'
        assert switch_result['switch_time'] is not None

    def test_rollback_switch_on_failure(self):
        """Should rollback to blue if green environment fails"""
        manager = DeploymentStrategyManager()
        strategy = manager.create_strategy(
            StrategyType.BLUE_GREEN,
            deployment_id="deploy-123"
        )
        
        # Simulate failure after switch
        with patch.object(manager, 'monitor_environment_health') as mock_health:
            mock_health.return_value = {'healthy': False, 'errors': ['high_error_rate']}
            
            rollback_result = manager.rollback_to_blue(strategy)
            
            assert rollback_result['success'] is True
            assert rollback_result['active_environment'] == 'blue'

    def test_cleanup_old_environment(self):
        """Should cleanup blue environment after successful green deployment"""
        manager = DeploymentStrategyManager()
        strategy = manager.create_strategy(
            StrategyType.BLUE_GREEN,
            deployment_id="deploy-123"
        )
        
        cleanup_result = manager.cleanup_old_environment(
            strategy,
            environment='blue',
            keep_hours=24
        )
        
        assert cleanup_result['scheduled'] is True
        assert cleanup_result['cleanup_after_hours'] == 24

    def test_complete_blue_green_deployment(self):
        """Should complete full blue-green deployment workflow"""
        manager = DeploymentStrategyManager()
        
        with patch.object(manager, '_execute_smoke_tests') as mock_smoke:
            mock_smoke.return_value = SmokeTestResult(
                stage_percentage=100,
                passed=True,
                tests_run=10,
                tests_passed=10,
                tests_failed=0
            )
            
            result = manager.execute_blue_green_deployment(
                deployment_id="deploy-123"
            )
            
            assert result['success'] is True
            assert result['switched_to'] == 'green'
            assert result['old_environment_cleanup_scheduled'] is True


class TestStrategyRecommendation:
    """Test strategy selection and recommendation logic"""

    def test_recommend_canary_for_high_risk(self):
        """Should recommend canary for high-risk deployments"""
        recommendation = recommend_strategy(
            deployment_size='large',
            risk_level='high',
            criticality='production'
        )
        
        assert recommendation['strategy'] == StrategyType.CANARY
        assert 'reason' in recommendation

    def test_recommend_blue_green_for_zero_downtime(self):
        """Should recommend blue-green for zero-downtime requirement"""
        recommendation = recommend_strategy(
            deployment_size='medium',
            risk_level='medium',
            criticality='production',
            requires_zero_downtime=True
        )
        
        assert recommendation['strategy'] == StrategyType.BLUE_GREEN
        assert 'zero_downtime' in recommendation['reason']

    def test_recommend_direct_for_low_risk(self):
        """Should recommend direct deployment for low-risk changes"""
        recommendation = recommend_strategy(
            deployment_size='small',
            risk_level='low',
            criticality='development'
        )
        
        assert recommendation['strategy'] == StrategyType.DIRECT


class TestSmokeTestExecution:
    """Test smoke test execution framework"""

    def test_execute_smoke_tests(self):
        """Should execute smoke tests and return results"""
        manager = DeploymentStrategyManager()
        
        smoke_result = manager.execute_smoke_tests(
            deployment_id="deploy-123",
            test_suite="standard"
        )
        
        assert isinstance(smoke_result, SmokeTestResult)
        assert smoke_result.tests_run > 0

    def test_smoke_test_categories(self):
        """Should support different smoke test categories"""
        manager = DeploymentStrategyManager()
        
        categories = ['health_check', 'api_validation', 'database_connectivity', 'critical_features']
        
        for category in categories:
            result = manager.execute_smoke_tests(
                deployment_id="deploy-123",
                test_suite=category
            )
            assert result is not None


class TestStrategyPersistence:
    """Test strategy state persistence"""

    def test_save_strategy_state(self, tmp_path):
        """Should save strategy state to disk"""
        manager = DeploymentStrategyManager(str(tmp_path))
        strategy = manager.create_strategy(
            StrategyType.CANARY,
            deployment_id="deploy-123"
        )
        
        save_path = manager.save_strategy_state(strategy)
        
        assert Path(save_path).exists()

    def test_load_strategy_state(self, tmp_path):
        """Should load strategy state from disk"""
        manager = DeploymentStrategyManager(str(tmp_path))
        strategy = manager.create_strategy(
            StrategyType.CANARY,
            deployment_id="deploy-123"
        )
        
        save_path = manager.save_strategy_state(strategy)
        loaded_strategy = manager.load_strategy_state("deploy-123")
        
        assert loaded_strategy.deployment_id == strategy.deployment_id
        assert loaded_strategy.strategy_type == strategy.strategy_type

    def test_resume_canary_deployment(self, tmp_path):
        """Should resume canary deployment from saved state"""
        manager = DeploymentStrategyManager(str(tmp_path))
        strategy = manager.create_strategy(
            StrategyType.CANARY,
            deployment_id="deploy-123"
        )
        
        # Advance to 50% stage
        strategy.advance_stage()
        manager.save_strategy_state(strategy)
        
        # Resume from checkpoint
        resumed = manager.load_strategy_state("deploy-123")
        current_stage = resumed.get_current_stage()
        
        assert current_stage.percentage == 50


class TestEndToEndStrategyWorkflows:
    """Test complete end-to-end strategy workflows"""

    def test_full_canary_workflow_with_validation(self):
        """Should execute complete canary workflow with all validations"""
        manager = DeploymentStrategyManager()
        
        with patch.object(manager, '_execute_smoke_tests') as mock_smoke:
            mock_smoke.return_value = SmokeTestResult(
                stage_percentage=100,
                passed=True,
                tests_run=15,
                tests_passed=15,
                tests_failed=0
            )
            
            # Execute full canary deployment
            result = manager.execute_strategy(
                strategy_type=StrategyType.CANARY,
                deployment_id="deploy-123",
                validate_each_stage=True
            )
            
            assert result['success'] is True
            assert result['strategy_type'] == 'canary'
            assert result['stages_completed'] == 3
            assert result['total_duration_minutes'] > 0

    def test_full_blue_green_workflow_with_validation(self):
        """Should execute complete blue-green workflow with all validations"""
        manager = DeploymentStrategyManager()
        
        with patch.object(manager, '_execute_smoke_tests') as mock_smoke:
            mock_smoke.return_value = SmokeTestResult(
                stage_percentage=100,
                passed=True,
                tests_run=20,
                tests_passed=20,
                tests_failed=0
            )
            
            # Execute full blue-green deployment
            result = manager.execute_strategy(
                strategy_type=StrategyType.BLUE_GREEN,
                deployment_id="deploy-123",
                validate_switch=True
            )
            
            assert result['success'] is True
            assert result['strategy_type'] == 'blue_green'
            assert result['environment_switched'] is True

    def test_canary_with_rollback_at_stage_2(self):
        """Should rollback canary deployment if stage 2 (50%) fails"""
        manager = DeploymentStrategyManager()
        
        call_count = [0]
        
        def smoke_side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 2:  # Fail at 50% stage
                return SmokeTestResult(
                    stage_percentage=50,
                    passed=False,
                    tests_run=10,
                    tests_passed=7,
                    tests_failed=3,
                    failure_reasons=["API timeout", "Database connection error"]
                )
            return SmokeTestResult(
                stage_percentage=10,
                passed=True,
                tests_run=10,
                tests_passed=10,
                tests_failed=0
            )
        
        with patch.object(manager, '_execute_smoke_tests', side_effect=smoke_side_effect):
            result = manager.execute_strategy(
                strategy_type=StrategyType.CANARY,
                deployment_id="deploy-123",
                validate_each_stage=True
            )
            
            assert result['success'] is False
            assert result['rollback_triggered'] is True
            assert result['failed_at_stage'] == 50
