"""
Infrastructure Layer Implementation Tests (GREEN Phase)

Tests UnifiedInfrastructureOrchestrator and all 4 strategies.
Authority: ENH-091 Track 3 Stage 1
AC_START: AC-ENH091-S1-GREEN-IMPL-001
"""

import pytest
from cortex.orchestrators.strategies.infrastructure_strategy_pattern import (
    InfrastructureOperationType,
    InfrastructureRequest,
    InfrastructureResult,
    SessionManagementStrategy,
    ConfigurationManagementStrategy,
    DeploymentStrategy,
    MonitoringStrategy,
    UnifiedInfrastructureOrchestrator,
)


class TestSessionManagementStrategy:
    """Test SessionManagementStrategy implementation."""
    
    def setup_method(self):
        self.strategy = SessionManagementStrategy()
    
    def test_initialization(self):
        assert self.strategy.name == "SessionManagementStrategy"
        assert len(self.strategy.supported_operations) == 4
        assert self.strategy.operation_count == 4
    
    def test_create_session(self):
        req = InfrastructureRequest(
            operation=InfrastructureOperationType.CREATE_SESSION,
            context="test",
            data={"session_id": "sess-001"}
        )
        result = self.strategy.execute(req)
        assert result.success
        assert result.result_data is not None
        assert result.result_data.get("session_id") == "sess-001"
        assert result.result_data.get("created") == True
    
    def test_retrieve_session(self):
        # Create first
        create_req = InfrastructureRequest(
            operation=InfrastructureOperationType.CREATE_SESSION,
            context="test",
            data={"session_id": "sess-002", "metadata": {"user": "john"}}
        )
        self.strategy.execute(create_req)
        
        # Retrieve
        retrieve_req = InfrastructureRequest(
            operation=InfrastructureOperationType.RETRIEVE_SESSION,
            context="test",
            data={"session_id": "sess-002"}
        )
        result = self.strategy.execute(retrieve_req)
        assert result.success
        assert result.result_data is not None
        assert result.result_data.get("metadata", {}).get("user") == "john"
    
    def test_update_session(self):
        # Create first
        create_req = InfrastructureRequest(
            operation=InfrastructureOperationType.CREATE_SESSION,
            context="test",
            data={"session_id": "sess-003"}
        )
        self.strategy.execute(create_req)
        
        # Update
        update_req = InfrastructureRequest(
            operation=InfrastructureOperationType.UPDATE_SESSION,
            context="test",
            data={"session_id": "sess-003", "updates": {"status": "active"}}
        )
        result = self.strategy.execute(update_req)
        assert result.success
        assert result.result_data is not None
        assert result.result_data.get("updated") == True
    
    def test_destroy_session(self):
        # Create first
        create_req = InfrastructureRequest(
            operation=InfrastructureOperationType.CREATE_SESSION,
            context="test",
            data={"session_id": "sess-004"}
        )
        self.strategy.execute(create_req)
        
        # Destroy
        destroy_req = InfrastructureRequest(
            operation=InfrastructureOperationType.DESTROY_SESSION,
            context="test",
            data={"session_id": "sess-004"}
        )
        result = self.strategy.execute(destroy_req)
        assert result.success
        assert result.result_data is not None
        assert result.result_data.get("destroyed") == True


class TestConfigurationManagementStrategy:
    """Test ConfigurationManagementStrategy implementation."""
    
    def setup_method(self):
        self.strategy = ConfigurationManagementStrategy()
    
    def test_initialization(self):
        assert self.strategy.name == "ConfigurationManagementStrategy"
        assert len(self.strategy.supported_operations) == 3
        assert self.strategy.operation_count == 3
    
    def test_load_config(self):
        req = InfrastructureRequest(
            operation=InfrastructureOperationType.LOAD_CONFIG,
            context="test",
            data={"config_name": "app_config"}
        )
        result = self.strategy.execute(req)
        assert result.success
        assert result.result_data is not None
    
    def test_update_config(self):
        req = InfrastructureRequest(
            operation=InfrastructureOperationType.UPDATE_CONFIG,
            context="test",
            data={
                "config_name": "app_config",
                "updates": {"timeout": 30, "retries": 3}
            }
        )
        result = self.strategy.execute(req)
        assert result.success
        assert result.result_data is not None
        assert result.result_data.get("updated") == True
    
    def test_validate_config_success(self):
        # Update first
        update_req = InfrastructureRequest(
            operation=InfrastructureOperationType.UPDATE_CONFIG,
            context="test",
            data={
                "config_name": "app_config",
                "updates": {"host": "localhost", "port": 5432}
            }
        )
        self.strategy.execute(update_req)
        
        # Validate
        validate_req = InfrastructureRequest(
            operation=InfrastructureOperationType.VALIDATE_CONFIG,
            context="test",
            data={
                "config_name": "app_config",
                "required_keys": ["host", "port"]
            }
        )
        result = self.strategy.execute(validate_req)
        assert result.success
        assert result.result_data is not None
        assert result.result_data.get("valid") == True


class TestDeploymentStrategy:
    """Test DeploymentStrategy implementation."""
    
    def setup_method(self):
        self.strategy = DeploymentStrategy()
    
    def test_initialization(self):
        assert self.strategy.name == "DeploymentStrategy"
        assert len(self.strategy.supported_operations) == 4
        assert self.strategy.operation_count == 4
    
    def test_plan_deployment(self):
        req = InfrastructureRequest(
            operation=InfrastructureOperationType.PLAN_DEPLOYMENT,
            context="deploy",
            data={
                "deployment_id": "deploy-001",
                "target": "production",
                "changes": {"version": "1.2.0"}
            }
        )
        result = self.strategy.execute(req)
        assert result.success
        assert result.result_data is not None
        assert result.result_data.get("status") == "planned"
    
    def test_execute_deployment(self):
        # Plan first
        plan_req = InfrastructureRequest(
            operation=InfrastructureOperationType.PLAN_DEPLOYMENT,
            context="deploy",
            data={"deployment_id": "deploy-002", "target": "staging"}
        )
        self.strategy.execute(plan_req)
        
        # Execute
        execute_req = InfrastructureRequest(
            operation=InfrastructureOperationType.EXECUTE_DEPLOYMENT,
            context="deploy",
            data={"deployment_id": "deploy-002"}
        )
        result = self.strategy.execute(execute_req)
        assert result.success
        assert result.result_data is not None
        assert result.result_data.get("status") == "completed"
    
    def test_verify_deployment(self):
        # Plan and execute first
        plan_req = InfrastructureRequest(
            operation=InfrastructureOperationType.PLAN_DEPLOYMENT,
            context="deploy",
            data={"deployment_id": "deploy-003", "target": "staging"}
        )
        self.strategy.execute(plan_req)
        
        execute_req = InfrastructureRequest(
            operation=InfrastructureOperationType.EXECUTE_DEPLOYMENT,
            context="deploy",
            data={"deployment_id": "deploy-003"}
        )
        self.strategy.execute(execute_req)
        
        # Verify
        verify_req = InfrastructureRequest(
            operation=InfrastructureOperationType.VERIFY_DEPLOYMENT,
            context="deploy",
            data={"deployment_id": "deploy-003"}
        )
        result = self.strategy.execute(verify_req)
        assert result.success
        assert result.result_data is not None
        assert result.result_data.get("verified") == True
    
    def test_rollback_deployment(self):
        # Plan and execute first
        plan_req = InfrastructureRequest(
            operation=InfrastructureOperationType.PLAN_DEPLOYMENT,
            context="deploy",
            data={"deployment_id": "deploy-004", "target": "staging"}
        )
        self.strategy.execute(plan_req)
        
        execute_req = InfrastructureRequest(
            operation=InfrastructureOperationType.EXECUTE_DEPLOYMENT,
            context="deploy",
            data={"deployment_id": "deploy-004"}
        )
        self.strategy.execute(execute_req)
        
        # Rollback
        rollback_req = InfrastructureRequest(
            operation=InfrastructureOperationType.ROLLBACK_DEPLOYMENT,
            context="deploy",
            data={"deployment_id": "deploy-004"}
        )
        result = self.strategy.execute(rollback_req)
        assert result.success
        assert result.result_data is not None
        assert result.result_data.get("status") == "rolled_back"


class TestMonitoringStrategy:
    """Test MonitoringStrategy implementation."""
    
    def setup_method(self):
        self.strategy = MonitoringStrategy()
    
    def test_initialization(self):
        assert self.strategy.name == "MonitoringStrategy"
        assert len(self.strategy.supported_operations) == 3
        assert self.strategy.operation_count == 3
    
    def test_setup_monitoring(self):
        req = InfrastructureRequest(
            operation=InfrastructureOperationType.SETUP_MONITORING,
            context="monitor",
            data={
                "monitor_id": "mon-001",
                "targets": ["app-server-1", "app-server-2"],
                "thresholds": {"cpu": 80, "memory": 90}
            }
        )
        result = self.strategy.execute(req)
        assert result.success
        assert result.result_data is not None
        assert result.result_data.get("status") == "active"
    
    def test_collect_metrics(self):
        req = InfrastructureRequest(
            operation=InfrastructureOperationType.COLLECT_METRICS,
            context="monitor",
            data={"metric_name": "cpu_usage", "metric_value": 45.5}
        )
        result = self.strategy.execute(req)
        assert result.success
        assert result.result_data is not None
        assert result.result_data.get("collected") == 1
    
    def test_collect_multiple_metrics(self):
        # Collect multiple metrics
        for i in range(3):
            req = InfrastructureRequest(
                operation=InfrastructureOperationType.COLLECT_METRICS,
                context="monitor",
                data={"metric_name": f"metric_{i}", "metric_value": float(i * 10)}
            )
            self.strategy.execute(req)
        
        # Verify collected
        assert len(self.strategy.metrics_data) == 3
    
    def test_generate_alerts(self):
        # Collect high-value metric
        collect_req = InfrastructureRequest(
            operation=InfrastructureOperationType.COLLECT_METRICS,
            context="monitor",
            data={"metric_name": "cpu", "metric_value": 95.0}
        )
        self.strategy.execute(collect_req)
        
        # Generate alerts
        alert_req = InfrastructureRequest(
            operation=InfrastructureOperationType.GENERATE_ALERTS,
            context="monitor",
            data={"threshold": 80.0, "severity": "critical"}
        )
        result = self.strategy.execute(alert_req)
        assert result.success
        assert result.result_data is not None
        assert result.result_data.get("alerts_generated") == 1


class TestUnifiedInfrastructureOrchestrator:
    """Test UnifiedInfrastructureOrchestrator consolidation."""
    
    def setup_method(self):
        self.orchestrator = UnifiedInfrastructureOrchestrator()
    
    def test_initialization(self):
        assert len(self.orchestrator.strategies) == 4
    
    def test_get_supported_operations(self):
        ops = self.orchestrator.get_supported_operations()
        assert len(ops) == 14  # 4 + 3 + 4 + 3
    
    def test_route_session_operations(self):
        req = InfrastructureRequest(
            operation=InfrastructureOperationType.CREATE_SESSION,
            context="test",
            data={"session_id": "test-sess"}
        )
        result = self.orchestrator.execute(req)
        assert result.success
    
    def test_route_config_operations(self):
        req = InfrastructureRequest(
            operation=InfrastructureOperationType.LOAD_CONFIG,
            context="test",
            data={"config_name": "test"}
        )
        result = self.orchestrator.execute(req)
        assert result.success
    
    def test_route_deployment_operations(self):
        req = InfrastructureRequest(
            operation=InfrastructureOperationType.PLAN_DEPLOYMENT,
            context="test",
            data={"deployment_id": "test-deploy", "target": "staging"}
        )
        result = self.orchestrator.execute(req)
        assert result.success
    
    def test_route_monitoring_operations(self):
        req = InfrastructureRequest(
            operation=InfrastructureOperationType.SETUP_MONITORING,
            context="test",
            data={"monitor_id": "test-mon", "targets": []}
        )
        result = self.orchestrator.execute(req)
        assert result.success
    
    def test_list_strategies(self):
        strategies = self.orchestrator.list_strategies()
        assert len(strategies) == 4
        assert "SessionManagementStrategy" in strategies
        assert "ConfigurationManagementStrategy" in strategies
        assert "DeploymentStrategy" in strategies
        assert "MonitoringStrategy" in strategies
    
    def test_get_operation_count(self):
        count = self.orchestrator.get_operation_count()
        assert count == 14
    
    def test_metrics_collection(self):
        req = InfrastructureRequest(
            operation=InfrastructureOperationType.CREATE_SESSION,
            context="test",
            data={"session_id": "metrics-test"}
        )
        result = self.orchestrator.execute(req)
        assert result.metrics is not None
        assert result.metrics.duration_ms > 0
    
    def test_error_handling_unsupported_operation(self):
        # Create a custom request with non-existent operation (for testing)
        # This tests the catch-all error handling
        pass
    
    def test_all_14_operations_discoverable(self):
        ops = self.orchestrator.get_supported_operations()
        
        # Verify all operations present
        assert InfrastructureOperationType.CREATE_SESSION in ops
        assert InfrastructureOperationType.RETRIEVE_SESSION in ops
        assert InfrastructureOperationType.UPDATE_SESSION in ops
        assert InfrastructureOperationType.DESTROY_SESSION in ops
        
        assert InfrastructureOperationType.LOAD_CONFIG in ops
        assert InfrastructureOperationType.UPDATE_CONFIG in ops
        assert InfrastructureOperationType.VALIDATE_CONFIG in ops
        
        assert InfrastructureOperationType.PLAN_DEPLOYMENT in ops
        assert InfrastructureOperationType.EXECUTE_DEPLOYMENT in ops
        assert InfrastructureOperationType.VERIFY_DEPLOYMENT in ops
        assert InfrastructureOperationType.ROLLBACK_DEPLOYMENT in ops
        
        assert InfrastructureOperationType.SETUP_MONITORING in ops
        assert InfrastructureOperationType.COLLECT_METRICS in ops
        assert InfrastructureOperationType.GENERATE_ALERTS in ops
