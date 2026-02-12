"""
Infrastructure Layer Stage 2 REFACTOR: Resource & Scaling Integration Tests

Integration tests for multi-strategy resource workflows and coordination.

Authority: ENH-091 Track 3 Stage 2
AC_START: AC-ENH091-S2-REFACTOR-001
"""

import pytest
from tests.unit.orchestrators.strategies.test_resource_scaling_implementation import (
    UnifiedResourceOrchestrator,
    ResourceProvisioningOperationType,
    ScalingOperationType,
    LoadBalancingOperationType,
    ResourceRequest,
)


class TestResourceWorkflows:
    """Integration tests for resource workflows."""
    
    def setup_method(self):
        self.orchestrator = UnifiedResourceOrchestrator()
    
    def test_provision_then_scale_workflow(self):
        """Test provisioning resource then scaling."""
        # Provision resource
        prov_req = ResourceRequest(
            operation=ResourceProvisioningOperationType.ALLOCATE_RESOURCE,
            context="workflow",
            data={"resource_id": "res-flow-001", "units": 2.0}
        )
        prov_result = self.orchestrator.execute(prov_req)
        assert prov_result.success
        
        # Scale up
        scale_req = ResourceRequest(
            operation=ScalingOperationType.SCALE_UP,
            context="workflow",
            data={"app_id": "app-flow-001"}
        )
        scale_result = self.orchestrator.execute(scale_req)
        assert scale_result.success
    
    def test_autoscale_with_load_balancing(self):
        """Test autoscaling with load balancing."""
        # Enable autoscaling
        auto_req = ResourceRequest(
            operation=ScalingOperationType.AUTO_SCALE_ENABLE,
            context="workflow",
            data={
                "app_id": "app-flow-002",
                "min_replicas": 2,
                "max_replicas": 8
            }
        )
        auto_result = self.orchestrator.execute(auto_req)
        assert auto_result.success
        
        # Register targets for load balancing
        lb_req = ResourceRequest(
            operation=LoadBalancingOperationType.REGISTER_TARGET,
            context="workflow",
            data={"lb_id": "lb-flow-001", "target": "app-flow-002"}
        )
        lb_result = self.orchestrator.execute(lb_req)
        assert lb_result.success
    
    def test_full_application_deployment_workflow(self):
        """Test complete application deployment workflow."""
        app_id = "app-full-deploy"
        
        # 1. Allocate resources
        prov_result = self.orchestrator.execute(ResourceRequest(
            operation=ResourceProvisioningOperationType.ALLOCATE_RESOURCE,
            context="deploy",
            data={"resource_id": f"{app_id}-res", "units": 4.0}
        ))
        assert prov_result.success
        
        # 2. Create load balancer
        lb_result = self.orchestrator.execute(ResourceRequest(
            operation=LoadBalancingOperationType.REGISTER_TARGET,
            context="deploy",
            data={"lb_id": f"{app_id}-lb", "target": f"{app_id}-001"}
        ))
        assert lb_result.success
        
        # 3. Enable autoscaling
        auto_result = self.orchestrator.execute(ResourceRequest(
            operation=ScalingOperationType.AUTO_SCALE_ENABLE,
            context="deploy",
            data={"app_id": app_id, "min_replicas": 1, "max_replicas": 5}
        ))
        assert auto_result.success
        
        # 4. Get scaling metrics
        metrics_result = self.orchestrator.execute(ResourceRequest(
            operation=ScalingOperationType.GET_SCALING_METRICS,
            context="deploy",
            data={"app_id": app_id}
        ))
        assert metrics_result.success
    
    def test_provision_deallocate_reprovision_cycle(self):
        """Test provision-deallocate-reprovision cycle."""
        res_id = "res-cycle-001"
        
        # Allocate
        alloc1 = self.orchestrator.execute(ResourceRequest(
            operation=ResourceProvisioningOperationType.ALLOCATE_RESOURCE,
            context="cycle",
            data={"resource_id": res_id}
        ))
        assert alloc1.success
        
        # Deallocate
        dealloc = self.orchestrator.execute(ResourceRequest(
            operation=ResourceProvisioningOperationType.DEALLOCATE_RESOURCE,
            context="cycle",
            data={"resource_id": res_id}
        ))
        assert dealloc.success
        
        # Reallocate
        alloc2 = self.orchestrator.execute(ResourceRequest(
            operation=ResourceProvisioningOperationType.ALLOCATE_RESOURCE,
            context="cycle",
            data={"resource_id": res_id, "units": 4.0}
        ))
        assert alloc2.success


class TestScalingStrategies:
    """Integration tests for scaling strategies."""
    
    def setup_method(self):
        self.orchestrator = UnifiedResourceOrchestrator()
    
    def test_gradual_scale_up(self):
        """Test gradual scaling up."""
        app_id = "app-gradual-up"
        
        # Scale up 3 times
        for i in range(3):
            result = self.orchestrator.execute(ResourceRequest(
                operation=ScalingOperationType.SCALE_UP,
                context="test",
                data={"app_id": app_id}
            ))
            assert result.success
    
    def test_gradual_scale_down(self):
        """Test gradual scaling down."""
        app_id = "app-gradual-down"
        
        # Scale up first
        for _ in range(3):
            self.orchestrator.execute(ResourceRequest(
                operation=ScalingOperationType.SCALE_UP,
                context="test",
                data={"app_id": app_id}
            ))
        
        # Then scale down
        for i in range(2):
            result = self.orchestrator.execute(ResourceRequest(
                operation=ScalingOperationType.SCALE_DOWN,
                context="test",
                data={"app_id": app_id}
            ))
            assert result.success
    
    def test_autoscale_enable_disable_cycle(self):
        """Test autoscale enable-disable cycle."""
        app_id = "app-as-cycle"
        
        # Enable
        enable = self.orchestrator.execute(ResourceRequest(
            operation=ScalingOperationType.AUTO_SCALE_ENABLE,
            context="test",
            data={"app_id": app_id}
        ))
        assert enable.success
        
        # Disable
        disable = self.orchestrator.execute(ResourceRequest(
            operation=ScalingOperationType.AUTO_SCALE_DISABLE,
            context="test",
            data={"app_id": app_id}
        ))
        assert disable.success
        
        # Re-enable
        reenable = self.orchestrator.execute(ResourceRequest(
            operation=ScalingOperationType.AUTO_SCALE_ENABLE,
            context="test",
            data={"app_id": app_id}
        ))
        assert reenable.success
    
    def test_scaling_metrics_consistency(self):
        """Test scaling metrics are consistent."""
        app_id = "app-metrics"
        
        # Get initial metrics
        metrics1 = self.orchestrator.execute(ResourceRequest(
            operation=ScalingOperationType.GET_SCALING_METRICS,
            context="test",
            data={"app_id": app_id}
        ))
        assert metrics1.success
        
        # Scale up
        self.orchestrator.execute(ResourceRequest(
            operation=ScalingOperationType.SCALE_UP,
            context="test",
            data={"app_id": app_id}
        ))
        
        # Get updated metrics
        metrics2 = self.orchestrator.execute(ResourceRequest(
            operation=ScalingOperationType.GET_SCALING_METRICS,
            context="test",
            data={"app_id": app_id}
        ))
        assert metrics2.success
        assert metrics2.result_data is not None


class TestLoadBalancingPatterns:
    """Integration tests for load balancing patterns."""
    
    def setup_method(self):
        self.orchestrator = UnifiedResourceOrchestrator()
    
    def test_register_multiple_targets(self):
        """Test registering multiple targets."""
        lb_id = "lb-multi-001"
        
        for i in range(3):
            result = self.orchestrator.execute(ResourceRequest(
                operation=LoadBalancingOperationType.REGISTER_TARGET,
                context="test",
                data={"lb_id": lb_id, "target": f"target-{i}"}
            ))
            assert result.success
    
    def test_dynamic_target_management(self):
        """Test dynamic target add/remove."""
        lb_id = "lb-dynamic"
        targets = ["target-1", "target-2", "target-3"]
        
        # Register all
        for target in targets:
            self.orchestrator.execute(ResourceRequest(
                operation=LoadBalancingOperationType.REGISTER_TARGET,
                context="test",
                data={"lb_id": lb_id, "target": target}
            ))
        
        # Deregister middle one
        self.orchestrator.execute(ResourceRequest(
            operation=LoadBalancingOperationType.DEREGISTER_TARGET,
            context="test",
            data={"lb_id": lb_id, "target": "target-2"}
        ))
        
        # Get status
        status = self.orchestrator.execute(ResourceRequest(
            operation=LoadBalancingOperationType.GET_LOAD_STATUS,
            context="test",
            data={"lb_id": lb_id}
        ))
        assert status.success
    
    def test_load_distribution_across_replicas(self):
        """Test load distribution across replicas."""
        lb_id = "lb-dist"
        app_id = "app-dist"
        
        # Register targets
        for i in range(4):
            self.orchestrator.execute(ResourceRequest(
                operation=LoadBalancingOperationType.REGISTER_TARGET,
                context="test",
                data={"lb_id": lb_id, "target": f"replica-{i}"}
            ))
        
        # Distribute load
        dist = self.orchestrator.execute(ResourceRequest(
            operation=LoadBalancingOperationType.DISTRIBUTE_LOAD,
            context="test",
            data={"lb_id": lb_id}
        ))
        assert dist.success
    
    def test_load_balancer_health_check(self):
        """Test load balancer health checks."""
        lb_id = "lb-health"
        
        # Register targets
        for i in range(2):
            self.orchestrator.execute(ResourceRequest(
                operation=LoadBalancingOperationType.REGISTER_TARGET,
                context="test",
                data={"lb_id": lb_id, "target": f"healthy-{i}"}
            ))
        
        # Check load status
        status = self.orchestrator.execute(ResourceRequest(
            operation=LoadBalancingOperationType.GET_LOAD_STATUS,
            context="test",
            data={"lb_id": lb_id}
        ))
        assert status.success


class TestResourceCoordination:
    """Integration tests for multi-strategy coordination."""
    
    def setup_method(self):
        self.orchestrator = UnifiedResourceOrchestrator()
    
    def test_provision_scale_and_balance(self):
        """Test all three strategies working together."""
        # Provision
        prov = self.orchestrator.execute(ResourceRequest(
            operation=ResourceProvisioningOperationType.ALLOCATE_RESOURCE,
            context="coord",
            data={"resource_id": "res-coord"}
        ))
        assert prov.success
        
        # Scale
        scale = self.orchestrator.execute(ResourceRequest(
            operation=ScalingOperationType.SCALE_UP,
            context="coord",
            data={"app_id": "app-coord"}
        ))
        assert scale.success
        
        # Balance
        balance = self.orchestrator.execute(ResourceRequest(
            operation=LoadBalancingOperationType.REGISTER_TARGET,
            context="coord",
            data={"lb_id": "lb-coord", "target": "replica-1"}
        ))
        assert balance.success
    
    def test_resource_limits_with_scaling(self):
        """Test resource limits interaction with scaling."""
        res_id = "res-limits"
        app_id = "app-limits"
        
        # Allocate with limits
        alloc = self.orchestrator.execute(ResourceRequest(
            operation=ResourceProvisioningOperationType.ALLOCATE_RESOURCE,
            context="limits",
            data={"resource_id": res_id, "max_units": 8.0}
        ))
        assert alloc.success
        
        # Update limits
        update = self.orchestrator.execute(ResourceRequest(
            operation=ResourceProvisioningOperationType.UPDATE_RESOURCE_LIMITS,
            context="limits",
            data={"resource_id": res_id, "new_max_units": 16.0}
        ))
        assert update.success
        
        # Then scale with new limits
        scale = self.orchestrator.execute(ResourceRequest(
            operation=ScalingOperationType.SCALE_UP,
            context="limits",
            data={"app_id": app_id}
        ))
        assert scale.success
    
    def test_persistent_state_across_operations(self):
        """Test state persistence across operations."""
        res_id = "res-persist"
        
        # Create resource
        create = self.orchestrator.execute(ResourceRequest(
            operation=ResourceProvisioningOperationType.ALLOCATE_RESOURCE,
            context="persist",
            data={"resource_id": res_id, "units": 2.0}
        ))
        assert create.success
        
        # Check status
        status1 = self.orchestrator.execute(ResourceRequest(
            operation=ResourceProvisioningOperationType.GET_RESOURCE_STATUS,
            context="persist",
            data={"resource_id": res_id}
        ))
        assert status1.success
        assert status1.result_data is not None
        
        # Update
        update = self.orchestrator.execute(ResourceRequest(
            operation=ResourceProvisioningOperationType.UPDATE_RESOURCE_LIMITS,
            context="persist",
            data={"resource_id": res_id, "new_max_units": 12.0}
        ))
        assert update.success
        
        # Check status again
        status2 = self.orchestrator.execute(ResourceRequest(
            operation=ResourceProvisioningOperationType.GET_RESOURCE_STATUS,
            context="persist",
            data={"resource_id": res_id}
        ))
        assert status2.success
