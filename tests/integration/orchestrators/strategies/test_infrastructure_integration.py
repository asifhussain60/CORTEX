"""
Infrastructure Layer Integration Tests (REFACTOR Phase)

Integration tests for UnifiedInfrastructureOrchestrator with multi-strategy workflows,
environment awareness, timeout handling, and error recovery.

Authority: ENH-091 Track 3 Stage 1
AC_START: AC-ENH091-S1-REFACTOR-001
"""

import pytest
from cortex.orchestrators.strategies.infrastructure_strategy_pattern import (
    InfrastructureOperationType,
    InfrastructureRequest,
    UnifiedInfrastructureOrchestrator,
)


class TestInfrastructureWorkflows:
    """Integration tests for infrastructure workflows."""
    
    def setup_method(self):
        self.orchestrator = UnifiedInfrastructureOrchestrator()
    
    def test_session_lifecycle_workflow(self):
        """Test complete session lifecycle: create → retrieve → update → destroy."""
        # Create session
        create_req = InfrastructureRequest(
            operation=InfrastructureOperationType.CREATE_SESSION,
            context="lifecycle",
            data={"session_id": "sess-lifecycle-001"}
        )
        create_result = self.orchestrator.execute(create_req)
        assert create_result.success
        assert create_result.result_data is not None
        session_id = create_result.result_data["session_id"]
        
        # Retrieve session
        retrieve_req = InfrastructureRequest(
            operation=InfrastructureOperationType.RETRIEVE_SESSION,
            context="lifecycle",
            data={"session_id": session_id}
        )
        retrieve_result = self.orchestrator.execute(retrieve_req)
        assert retrieve_result.success
        
        # Update session
        update_req = InfrastructureRequest(
            operation=InfrastructureOperationType.UPDATE_SESSION,
            context="lifecycle",
            data={"session_id": session_id, "updates": {"status": "active"}}
        )
        update_result = self.orchestrator.execute(update_req)
        assert update_result.success
        
        # Destroy session
        destroy_req = InfrastructureRequest(
            operation=InfrastructureOperationType.DESTROY_SESSION,
            context="lifecycle",
            data={"session_id": session_id}
        )
        destroy_result = self.orchestrator.execute(destroy_req)
        assert destroy_result.success
    
    def test_deployment_workflow_success(self):
        """Test deployment workflow: plan → execute → verify."""
        # Plan deployment
        plan_req = InfrastructureRequest(
            operation=InfrastructureOperationType.PLAN_DEPLOYMENT,
            context="deploy",
            data={
                "deployment_id": "deploy-workflow-001",
                "target": "staging",
                "changes": {"version": "2.0.0"}
            }
        )
        plan_result = self.orchestrator.execute(plan_req)
        assert plan_result.success
        
        # Execute deployment
        exec_req = InfrastructureRequest(
            operation=InfrastructureOperationType.EXECUTE_DEPLOYMENT,
            context="deploy",
            data={"deployment_id": "deploy-workflow-001"}
        )
        exec_result = self.orchestrator.execute(exec_req)
        assert exec_result.success
        
        # Verify deployment
        verify_req = InfrastructureRequest(
            operation=InfrastructureOperationType.VERIFY_DEPLOYMENT,
            context="deploy",
            data={"deployment_id": "deploy-workflow-001"}
        )
        verify_result = self.orchestrator.execute(verify_req)
        assert verify_result.success
        assert verify_result.result_data is not None
        assert verify_result.result_data.get("verified") == True
    
    def test_config_load_update_validate_workflow(self):
        """Test config workflow: load → update → validate."""
        config_name = "integration_config"
        
        # Load config
        load_req = InfrastructureRequest(
            operation=InfrastructureOperationType.LOAD_CONFIG,
            context="config",
            data={"config_name": config_name}
        )
        load_result = self.orchestrator.execute(load_req)
        assert load_result.success
        
        # Update config
        update_req = InfrastructureRequest(
            operation=InfrastructureOperationType.UPDATE_CONFIG,
            context="config",
            data={
                "config_name": config_name,
                "updates": {"database": "postgres", "port": 5432}
            }
        )
        update_result = self.orchestrator.execute(update_req)
        assert update_result.success
        
        # Validate config
        validate_req = InfrastructureRequest(
            operation=InfrastructureOperationType.VALIDATE_CONFIG,
            context="config",
            data={
                "config_name": config_name,
                "required_keys": ["database", "port"]
            }
        )
        validate_result = self.orchestrator.execute(validate_req)
        assert validate_result.success
        assert validate_result.result_data is not None
        assert validate_result.result_data.get("valid") == True
    
    def test_monitoring_setup_collect_alert_workflow(self):
        """Test monitoring workflow: setup → collect → generate alerts."""
        monitor_id = "mon-workflow-001"
        
        # Setup monitoring
        setup_req = InfrastructureRequest(
            operation=InfrastructureOperationType.SETUP_MONITORING,
            context="monitor",
            data={
                "monitor_id": monitor_id,
                "targets": ["api-server", "db-server"],
                "thresholds": {"cpu": 80, "memory": 85}
            }
        )
        setup_result = self.orchestrator.execute(setup_req)
        assert setup_result.success
        
        # Collect metrics
        collect_req = InfrastructureRequest(
            operation=InfrastructureOperationType.COLLECT_METRICS,
            context="monitor",
            data={"metric_name": "cpu_usage", "metric_value": 92.0}
        )
        collect_result = self.orchestrator.execute(collect_req)
        assert collect_result.success
        
        # Generate alerts
        alert_req = InfrastructureRequest(
            operation=InfrastructureOperationType.GENERATE_ALERTS,
            context="monitor",
            data={"threshold": 80.0, "severity": "warning"}
        )
        alert_result = self.orchestrator.execute(alert_req)
        assert alert_result.success
        assert alert_result.result_data is not None
        alerts = alert_result.result_data.get("alerts_generated")
        assert alerts is not None
        assert alerts >= 1


class TestEnvironmentAwareness:
    """Test environment-aware orchestrator operations."""
    
    def setup_method(self):
        self.orchestrator = UnifiedInfrastructureOrchestrator()
    
    def test_environment_default(self):
        """Test default environment 'default'."""
        req = InfrastructureRequest(
            operation=InfrastructureOperationType.CREATE_SESSION,
            context="env_test",
            data={"session_id": "env-default"}
        )
        assert req.environment == "default"
    
    def test_environment_production(self):
        """Test production environment context."""
        req = InfrastructureRequest(
            operation=InfrastructureOperationType.PLAN_DEPLOYMENT,
            context="deploy",
            data={"deployment_id": "deploy-prod"},
            environment="production"
        )
        assert req.environment == "production"
        result = self.orchestrator.execute(req)
        assert result.success
    
    def test_environment_staging(self):
        """Test staging environment context."""
        req = InfrastructureRequest(
            operation=InfrastructureOperationType.PLAN_DEPLOYMENT,
            context="deploy",
            data={"deployment_id": "deploy-staging"},
            environment="staging"
        )
        assert req.environment == "staging"
        result = self.orchestrator.execute(req)
        assert result.success
    
    def test_environment_development(self):
        """Test development environment context."""
        req = InfrastructureRequest(
            operation=InfrastructureOperationType.SETUP_MONITORING,
            context="monitor",
            data={"monitor_id": "mon-dev", "targets": []},
            environment="development"
        )
        assert req.environment == "development"
        result = self.orchestrator.execute(req)
        assert result.success


class TestTimeoutHandling:
    """Test timeout configuration and handling."""
    
    def setup_method(self):
        self.orchestrator = UnifiedInfrastructureOrchestrator()
    
    def test_default_timeout_30_seconds(self):
        """Test default timeout is 30 seconds."""
        req = InfrastructureRequest(
            operation=InfrastructureOperationType.CREATE_SESSION,
            context="timeout",
            data={"session_id": "timeout-default"}
        )
        assert req.timeout_seconds == 30
    
    def test_custom_timeout_60_seconds(self):
        """Test custom timeout configuration."""
        req = InfrastructureRequest(
            operation=InfrastructureOperationType.EXECUTE_DEPLOYMENT,
            context="deploy",
            data={"deployment_id": "deploy-long"},
            timeout_seconds=60
        )
        assert req.timeout_seconds == 60
        result = self.orchestrator.execute(req)
        assert result.success
    
    def test_custom_timeout_5_seconds(self):
        """Test short timeout configuration."""
        req = InfrastructureRequest(
            operation=InfrastructureOperationType.LOAD_CONFIG,
            context="config",
            data={"config_name": "fast"},
            timeout_seconds=5
        )
        assert req.timeout_seconds == 5
        result = self.orchestrator.execute(req)
        assert result.success
    
    def test_custom_timeout_300_seconds(self):
        """Test extended timeout configuration."""
        req = InfrastructureRequest(
            operation=InfrastructureOperationType.COLLECT_METRICS,
            context="monitor",
            data={"metric_name": "long_run", "metric_value": 50.0},
            timeout_seconds=300
        )
        assert req.timeout_seconds == 300
        result = self.orchestrator.execute(req)
        assert result.success


class TestErrorRecovery:
    """Test error handling and recovery."""
    
    def setup_method(self):
        self.orchestrator = UnifiedInfrastructureOrchestrator()
    
    def test_retrieve_nonexistent_session(self):
        """Test error when retrieving non-existent session."""
        req = InfrastructureRequest(
            operation=InfrastructureOperationType.RETRIEVE_SESSION,
            context="error",
            data={"session_id": "nonexistent-session-xyz"}
        )
        result = self.orchestrator.execute(req)
        assert not result.success
        assert result.error is not None
    
    def test_destroy_nonexistent_session(self):
        """Test error when destroying non-existent session."""
        req = InfrastructureRequest(
            operation=InfrastructureOperationType.DESTROY_SESSION,
            context="error",
            data={"session_id": "nonexistent-destroy-xyz"}
        )
        result = self.orchestrator.execute(req)
        assert not result.success
        assert result.error is not None
    
    def test_rollback_nonexistent_deployment(self):
        """Test error when rolling back non-existent deployment."""
        req = InfrastructureRequest(
            operation=InfrastructureOperationType.ROLLBACK_DEPLOYMENT,
            context="error",
            data={"deployment_id": "nonexistent-deploy-xyz"}
        )
        result = self.orchestrator.execute(req)
        assert not result.success
        assert result.error is not None
    
    def test_validate_missing_required_config_keys(self):
        """Test validation fails when required keys missing."""
        config_name = "incomplete_config"
        
        # Update config without required keys
        update_req = InfrastructureRequest(
            operation=InfrastructureOperationType.UPDATE_CONFIG,
            context="config",
            data={
                "config_name": config_name,
                "updates": {"other_key": "value"}
            }
        )
        self.orchestrator.execute(update_req)
        
        # Validate expecting required keys
        validate_req = InfrastructureRequest(
            operation=InfrastructureOperationType.VALIDATE_CONFIG,
            context="config",
            data={
                "config_name": config_name,
                "required_keys": ["database", "port"]
            }
        )
        result = self.orchestrator.execute(validate_req)
        assert not result.success
        assert result.error is not None


class TestMultiStrategyCoordination:
    """Test coordination across multiple strategies."""
    
    def setup_method(self):
        self.orchestrator = UnifiedInfrastructureOrchestrator()
    
    def test_session_and_config_coordination(self):
        """Test session creation and config loading in sequence."""
        # Create session
        session_req = InfrastructureRequest(
            operation=InfrastructureOperationType.CREATE_SESSION,
            context="multi",
            data={"session_id": "multi-001"}
        )
        session_result = self.orchestrator.execute(session_req)
        assert session_result.success
        
        # Load config in same context
        config_req = InfrastructureRequest(
            operation=InfrastructureOperationType.LOAD_CONFIG,
            context="multi",
            data={"config_name": "multi-config"}
        )
        config_result = self.orchestrator.execute(config_req)
        assert config_result.success
    
    def test_deployment_and_monitoring_coordination(self):
        """Test deployment and monitoring in coordinated workflow."""
        deploy_id = "multi-deploy-001"
        monitor_id = "multi-mon-001"
        
        # Setup monitoring first
        monitor_req = InfrastructureRequest(
            operation=InfrastructureOperationType.SETUP_MONITORING,
            context="multi",
            data={"monitor_id": monitor_id, "targets": [deploy_id]}
        )
        monitor_result = self.orchestrator.execute(monitor_req)
        assert monitor_result.success
        
        # Plan deployment
        deploy_req = InfrastructureRequest(
            operation=InfrastructureOperationType.PLAN_DEPLOYMENT,
            context="multi",
            data={"deployment_id": deploy_id, "target": "staging"}
        )
        deploy_result = self.orchestrator.execute(deploy_req)
        assert deploy_result.success
    
    def test_all_four_strategies_in_sequence(self):
        """Test all 4 strategies executed in coordinated workflow."""
        # Session: Create
        sess_result = self.orchestrator.execute(InfrastructureRequest(
            operation=InfrastructureOperationType.CREATE_SESSION,
            context="all4",
            data={"session_id": "all4-sess"}
        ))
        assert sess_result.success
        
        # Config: Load
        config_result = self.orchestrator.execute(InfrastructureRequest(
            operation=InfrastructureOperationType.LOAD_CONFIG,
            context="all4",
            data={"config_name": "all4-cfg"}
        ))
        assert config_result.success
        
        # Deployment: Plan
        deploy_result = self.orchestrator.execute(InfrastructureRequest(
            operation=InfrastructureOperationType.PLAN_DEPLOYMENT,
            context="all4",
            data={"deployment_id": "all4-deploy", "target": "staging"}
        ))
        assert deploy_result.success
        
        # Monitoring: Setup
        monitor_result = self.orchestrator.execute(InfrastructureRequest(
            operation=InfrastructureOperationType.SETUP_MONITORING,
            context="all4",
            data={"monitor_id": "all4-mon", "targets": ["all4-deploy"]}
        ))
        assert monitor_result.success


class TestOperationDiscovery:
    """Test operation discovery and capability listing."""
    
    def setup_method(self):
        self.orchestrator = UnifiedInfrastructureOrchestrator()
    
    def test_get_supported_operations_count(self):
        """Test getting all supported operations."""
        ops = self.orchestrator.get_supported_operations()
        assert len(ops) == 14
    
    def test_all_operations_discoverable(self):
        """Test all 14 operations are discoverable."""
        ops = self.orchestrator.get_supported_operations()
        op_values = [op.value for op in ops]
        
        expected = [
            "create_session", "retrieve_session", "update_session", "destroy_session",
            "load_config", "update_config", "validate_config",
            "plan_deployment", "execute_deployment", "verify_deployment", "rollback_deployment",
            "setup_monitoring", "collect_metrics", "generate_alerts"
        ]
        
        for exp in expected:
            assert exp in op_values
    
    def test_list_strategies(self):
        """Test listing all available strategies."""
        strategies = self.orchestrator.list_strategies()
        assert len(strategies) == 4
        assert "SessionManagementStrategy" in strategies
        assert "ConfigurationManagementStrategy" in strategies
        assert "DeploymentStrategy" in strategies
        assert "MonitoringStrategy" in strategies
    
    def test_get_operation_count(self):
        """Test getting total operation count."""
        count = self.orchestrator.get_operation_count()
        assert count == 14
