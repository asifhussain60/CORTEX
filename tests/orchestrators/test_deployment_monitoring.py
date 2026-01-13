"""
Tests for AC-ROLLOUT-SIMPLE-003: Deployment Monitoring
Track deployment health and trigger rollbacks on failures.
"""
import pytest
from src.orchestrators.rollout_gates import RolloutGateManager, RolloutStage
from src.orchestrators.deployment_monitoring import DeploymentMonitor, HealthStatus


@pytest.mark.ac_id("AC-ROLLOUT-SIMPLE-003")
class TestDeploymentMonitoring:
    """Test deployment health monitoring."""
    
    @pytest.mark.ac_id("AC-ROLLOUT-SIMPLE-003")
    def test_monitor_initialization(self):
        """AC-ROLLOUT-SIMPLE-003: Can initialize deployment monitor."""
        gate_manager = RolloutGateManager()
        monitor = DeploymentMonitor(gate_manager)
        
        assert monitor.gate_manager == gate_manager
    
    @pytest.mark.ac_id("AC-ROLLOUT-SIMPLE-003")
    def test_record_deployment_metrics(self):
        """AC-ROLLOUT-SIMPLE-003: Can record deployment metrics."""
        gate_manager = RolloutGateManager()
        monitor = DeploymentMonitor(gate_manager)
        
        gate_manager.register_feature("monitored-feature", RolloutStage.CANARY)
        
        # Record metrics
        monitor.record_metric("monitored-feature", success=True)
        monitor.record_metric("monitored-feature", success=True)
        monitor.record_metric("monitored-feature", success=False)
        
        metrics = monitor.get_metrics("monitored-feature")
        assert metrics['total'] == 3
        assert metrics['failures'] == 1
    
    @pytest.mark.ac_id("AC-ROLLOUT-SIMPLE-003")
    def test_health_status_calculation(self):
        """AC-ROLLOUT-SIMPLE-003: Calculate health status from metrics."""
        gate_manager = RolloutGateManager()
        monitor = DeploymentMonitor(gate_manager)
        
        gate_manager.register_feature("healthy-feature", RolloutStage.CANARY)
        
        # 95% success rate = HEALTHY
        for _ in range(95):
            monitor.record_metric("healthy-feature", success=True)
        for _ in range(5):
            monitor.record_metric("healthy-feature", success=False)
        
        health = monitor.get_health_status("healthy-feature")
        assert health == HealthStatus.HEALTHY
    
    @pytest.mark.ac_id("AC-ROLLOUT-SIMPLE-003")
    def test_degraded_health_detection(self):
        """AC-ROLLOUT-SIMPLE-003: Detect degraded health (80-95% success)."""
        gate_manager = RolloutGateManager()
        monitor = DeploymentMonitor(gate_manager)
        
        gate_manager.register_feature("degraded-feature", RolloutStage.CANARY)
        
        # 85% success rate = DEGRADED
        for _ in range(85):
            monitor.record_metric("degraded-feature", success=True)
        for _ in range(15):
            monitor.record_metric("degraded-feature", success=False)
        
        health = monitor.get_health_status("degraded-feature")
        assert health == HealthStatus.DEGRADED
    
    @pytest.mark.ac_id("AC-ROLLOUT-SIMPLE-003")
    def test_unhealthy_triggers_alert(self):
        """AC-ROLLOUT-SIMPLE-003: Unhealthy status (<80% success) triggers alert."""
        gate_manager = RolloutGateManager()
        monitor = DeploymentMonitor(gate_manager)
        
        gate_manager.register_feature("failing-feature", RolloutStage.CANARY)
        
        # 70% success rate = UNHEALTHY
        for _ in range(70):
            monitor.record_metric("failing-feature", success=True)
        for _ in range(30):
            monitor.record_metric("failing-feature", success=False)
        
        health = monitor.get_health_status("failing-feature")
        assert health == HealthStatus.UNHEALTHY
        assert monitor.should_trigger_alert("failing-feature")
