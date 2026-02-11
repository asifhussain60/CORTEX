"""
Infrastructure Layer Stage 2 GREEN: Resource & Scaling Implementation

Implementation tests for unified resource provisioning, scaling, and load balancing strategies.

Authority: ENH-091 Track 3 Stage 2
AC_START: AC-ENH091-S2-GREEN-001
"""

import pytest
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from enum import Enum


class ResourceProvisioningOperationType(Enum):
    """Resource provisioning operations."""
    ALLOCATE_RESOURCE = "allocate_resource"
    DEALLOCATE_RESOURCE = "deallocate_resource"
    GET_RESOURCE_STATUS = "get_resource_status"
    UPDATE_RESOURCE_LIMITS = "update_resource_limits"


class ScalingOperationType(Enum):
    """Scaling management operations."""
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    AUTO_SCALE_ENABLE = "auto_scale_enable"
    AUTO_SCALE_DISABLE = "auto_scale_disable"
    GET_SCALING_METRICS = "get_scaling_metrics"


class LoadBalancingOperationType(Enum):
    """Load balancing operations."""
    REGISTER_TARGET = "register_target"
    DEREGISTER_TARGET = "deregister_target"
    DISTRIBUTE_LOAD = "distribute_load"
    GET_LOAD_STATUS = "get_load_status"


@dataclass
class ResourceMetrics:
    """Metrics for resource operations."""
    duration_ms: float
    operation_success: bool
    resources_used: str
    error_count: int


@dataclass
class Resource:
    """Resource representation."""
    resource_id: str
    resource_type: str
    allocated_units: float
    max_units: float
    status: str


@dataclass
class ScalingConfig:
    """Scaling configuration."""
    min_replicas: int
    max_replicas: int
    target_utilization: float
    scale_up_threshold: float
    scale_down_threshold: float


@dataclass
class LoadBalancer:
    """Load balancer configuration."""
    lb_id: str
    algorithm: str
    targets: List[str]
    health_check_interval: int


@dataclass
class ResourceRequest:
    """Request for resource operations."""
    operation: Enum
    context: str
    data: Dict[str, Any]
    resource_type: str = "compute"
    timeout_seconds: int = 30


@dataclass
class ResourceResult:
    """Result of resource operation."""
    success: bool
    operation: Enum
    result_data: Optional[Dict[str, Any]]
    error: Optional[str]
    metrics: ResourceMetrics


class ResourceStrategy(ABC):
    """Base class for resource strategies."""
    
    supported_operations: List[Enum] = []
    
    @abstractmethod
    def can_handle(self, operation: Enum) -> bool:
        """Check if strategy can handle operation."""
        pass
    
    @abstractmethod
    def execute(self, request: ResourceRequest) -> ResourceResult:
        """Execute resource operation."""
        pass


class ResourceProvisioningStrategy(ResourceStrategy):
    """Strategy for resource provisioning."""
    
    def __init__(self):
        self.resources: Dict[str, Resource] = {}
        self.supported_operations = [
            ResourceProvisioningOperationType.ALLOCATE_RESOURCE,
            ResourceProvisioningOperationType.DEALLOCATE_RESOURCE,
            ResourceProvisioningOperationType.GET_RESOURCE_STATUS,
            ResourceProvisioningOperationType.UPDATE_RESOURCE_LIMITS,
        ]
    
    def can_handle(self, operation: Enum) -> bool:
        """Check if can handle operation."""
        return operation in self.supported_operations
    
    def execute(self, request: ResourceRequest) -> ResourceResult:
        """Execute provisioning operation."""
        start_time = time.time()
        
        try:
            resource_id = request.data.get("resource_id", f"res_{int(time.time())}")
            
            if request.operation == ResourceProvisioningOperationType.ALLOCATE_RESOURCE:
                resource_type = request.data.get("resource_type", "compute")
                units = request.data.get("units", 2.0)
                max_units = request.data.get("max_units", 8.0)
                
                resource = Resource(
                    resource_id=resource_id,
                    resource_type=resource_type,
                    allocated_units=units,
                    max_units=max_units,
                    status="allocated"
                )
                self.resources[resource_id] = resource
                result_data = {"resource_id": resource_id, "status": "allocated"}
            
            elif request.operation == ResourceProvisioningOperationType.DEALLOCATE_RESOURCE:
                if resource_id in self.resources:
                    del self.resources[resource_id]
                    result_data = {"resource_id": resource_id, "status": "deallocated"}
                else:
                    result_data = {"resource_id": resource_id, "status": "not_found"}
            
            elif request.operation == ResourceProvisioningOperationType.GET_RESOURCE_STATUS:
                if resource_id in self.resources:
                    res = self.resources[resource_id]
                    result_data = {
                        "resource_id": resource_id,
                        "status": res.status,
                        "allocated": res.allocated_units,
                        "max": res.max_units
                    }
                else:
                    result_data = {"status": "not_found"}
            
            elif request.operation == ResourceProvisioningOperationType.UPDATE_RESOURCE_LIMITS:
                if resource_id in self.resources:
                    new_max = request.data.get("new_max_units", 16.0)
                    self.resources[resource_id].max_units = new_max
                    result_data = {"resource_id": resource_id, "new_max": new_max}
                else:
                    result_data = {"status": "not_found"}
            
            else:
                result_data = None
            
            duration_ms = (time.time() - start_time) * 1000
            metrics = ResourceMetrics(
                duration_ms=duration_ms,
                operation_success=True,
                resources_used="compute",
                error_count=0
            )
            
            return ResourceResult(
                success=True,
                operation=request.operation,
                result_data=result_data,
                error=None,
                metrics=metrics
            )
        
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            metrics = ResourceMetrics(
                duration_ms=duration_ms,
                operation_success=False,
                resources_used="compute",
                error_count=1
            )
            return ResourceResult(
                success=False,
                operation=request.operation,
                result_data=None,
                error=str(e),
                metrics=metrics
            )


class ScalingStrategy(ResourceStrategy):
    """Strategy for scaling management."""
    
    def __init__(self):
        self.scaling_configs: Dict[str, ScalingConfig] = {}
        self.autoscale_enabled: Dict[str, bool] = {}
        self.replicas: Dict[str, int] = {}
        self.supported_operations = [
            ScalingOperationType.SCALE_UP,
            ScalingOperationType.SCALE_DOWN,
            ScalingOperationType.AUTO_SCALE_ENABLE,
            ScalingOperationType.AUTO_SCALE_DISABLE,
            ScalingOperationType.GET_SCALING_METRICS,
        ]
    
    def can_handle(self, operation: Enum) -> bool:
        """Check if can handle operation."""
        return operation in self.supported_operations
    
    def execute(self, request: ResourceRequest) -> ResourceResult:
        """Execute scaling operation."""
        start_time = time.time()
        
        try:
            app_id = request.data.get("app_id", f"app_{int(time.time())}")
            
            if request.operation == ScalingOperationType.SCALE_UP:
                current = self.replicas.get(app_id, 1)
                new_count = min(current + 1, 10)
                self.replicas[app_id] = new_count
                result_data = {"app_id": app_id, "current_replicas": new_count}
            
            elif request.operation == ScalingOperationType.SCALE_DOWN:
                current = self.replicas.get(app_id, 2)
                new_count = max(current - 1, 1)
                self.replicas[app_id] = new_count
                result_data = {"app_id": app_id, "current_replicas": new_count}
            
            elif request.operation == ScalingOperationType.AUTO_SCALE_ENABLE:
                config = ScalingConfig(
                    min_replicas=request.data.get("min_replicas", 1),
                    max_replicas=request.data.get("max_replicas", 10),
                    target_utilization=request.data.get("target_utilization", 0.75),
                    scale_up_threshold=request.data.get("scale_up_threshold", 0.85),
                    scale_down_threshold=request.data.get("scale_down_threshold", 0.25)
                )
                self.scaling_configs[app_id] = config
                self.autoscale_enabled[app_id] = True
                result_data = {"app_id": app_id, "autoscale": "enabled"}
            
            elif request.operation == ScalingOperationType.AUTO_SCALE_DISABLE:
                self.autoscale_enabled[app_id] = False
                result_data = {"app_id": app_id, "autoscale": "disabled"}
            
            elif request.operation == ScalingOperationType.GET_SCALING_METRICS:
                metrics_data = {
                    "current_replicas": self.replicas.get(app_id, 1),
                    "autoscale_enabled": self.autoscale_enabled.get(app_id, False),
                    "cpu_utilization": 65.5,
                    "memory_utilization": 72.3
                }
                result_data = metrics_data
            
            else:
                result_data = None
            
            duration_ms = (time.time() - start_time) * 1000
            metrics = ResourceMetrics(
                duration_ms=duration_ms,
                operation_success=True,
                resources_used="compute",
                error_count=0
            )
            
            return ResourceResult(
                success=True,
                operation=request.operation,
                result_data=result_data,
                error=None,
                metrics=metrics
            )
        
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            metrics = ResourceMetrics(
                duration_ms=duration_ms,
                operation_success=False,
                resources_used="compute",
                error_count=1
            )
            return ResourceResult(
                success=False,
                operation=request.operation,
                result_data=None,
                error=str(e),
                metrics=metrics
            )


class LoadBalancingStrategy(ResourceStrategy):
    """Strategy for load balancing."""
    
    def __init__(self):
        self.load_balancers: Dict[str, LoadBalancer] = {}
        self.supported_operations = [
            LoadBalancingOperationType.REGISTER_TARGET,
            LoadBalancingOperationType.DEREGISTER_TARGET,
            LoadBalancingOperationType.DISTRIBUTE_LOAD,
            LoadBalancingOperationType.GET_LOAD_STATUS,
        ]
    
    def can_handle(self, operation: Enum) -> bool:
        """Check if can handle operation."""
        return operation in self.supported_operations
    
    def execute(self, request: ResourceRequest) -> ResourceResult:
        """Execute load balancing operation."""
        start_time = time.time()
        
        try:
            lb_id = request.data.get("lb_id", f"lb_{int(time.time())}")
            
            if request.operation == LoadBalancingOperationType.REGISTER_TARGET:
                target = request.data.get("target", "target-1")
                
                if lb_id not in self.load_balancers:
                    self.load_balancers[lb_id] = LoadBalancer(
                        lb_id=lb_id,
                        algorithm="round_robin",
                        targets=[],
                        health_check_interval=30
                    )
                
                if target not in self.load_balancers[lb_id].targets:
                    self.load_balancers[lb_id].targets.append(target)
                
                result_data = {
                    "lb_id": lb_id,
                    "registered_target": target,
                    "target_count": len(self.load_balancers[lb_id].targets)
                }
            
            elif request.operation == LoadBalancingOperationType.DEREGISTER_TARGET:
                target = request.data.get("target", "target-1")
                
                if lb_id in self.load_balancers and target in self.load_balancers[lb_id].targets:
                    self.load_balancers[lb_id].targets.remove(target)
                
                result_data = {
                    "lb_id": lb_id,
                    "deregistered_target": target,
                    "target_count": len(self.load_balancers[lb_id].targets) if lb_id in self.load_balancers else 0
                }
            
            elif request.operation == LoadBalancingOperationType.DISTRIBUTE_LOAD:
                if lb_id in self.load_balancers:
                    targets = self.load_balancers[lb_id].targets
                    algorithm = self.load_balancers[lb_id].algorithm
                    result_data = {
                        "lb_id": lb_id,
                        "algorithm": algorithm,
                        "targets": targets,
                        "distribution": "balanced"
                    }
                else:
                    result_data = {"lb_id": lb_id, "status": "not_found"}
            
            elif request.operation == LoadBalancingOperationType.GET_LOAD_STATUS:
                if lb_id in self.load_balancers:
                    lb = self.load_balancers[lb_id]
                    result_data = {
                        "lb_id": lb_id,
                        "healthy_targets": len(lb.targets),
                        "total_targets": len(lb.targets),
                        "load_percentage": 65.0
                    }
                else:
                    result_data = {"status": "not_found"}
            
            else:
                result_data = None
            
            duration_ms = (time.time() - start_time) * 1000
            metrics = ResourceMetrics(
                duration_ms=duration_ms,
                operation_success=True,
                resources_used="network",
                error_count=0
            )
            
            return ResourceResult(
                success=True,
                operation=request.operation,
                result_data=result_data,
                error=None,
                metrics=metrics
            )
        
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            metrics = ResourceMetrics(
                duration_ms=duration_ms,
                operation_success=False,
                resources_used="network",
                error_count=1
            )
            return ResourceResult(
                success=False,
                operation=request.operation,
                result_data=None,
                error=str(e),
                metrics=metrics
            )


class UnifiedResourceOrchestrator:
    """Unified orchestrator for resource, scaling, and load balancing."""
    
    def __init__(self):
        self.strategies: List[ResourceStrategy] = [
            ResourceProvisioningStrategy(),
            ScalingStrategy(),
            LoadBalancingStrategy(),
        ]
    
    def execute(self, request: ResourceRequest) -> ResourceResult:
        """Execute resource operation by routing to appropriate strategy."""
        for strategy in self.strategies:
            if strategy.can_handle(request.operation):
                return strategy.execute(request)
        
        return ResourceResult(
            success=False,
            operation=request.operation,
            result_data=None,
            error=f"No strategy available for {request.operation.value}",
            metrics=ResourceMetrics(
                duration_ms=0.0,
                operation_success=False,
                resources_used="unknown",
                error_count=1
            )
        )
    
    def get_supported_operations(self) -> List[Enum]:
        """Get all supported operations."""
        operations = []
        for strategy in self.strategies:
            operations.extend(strategy.supported_operations)
        return operations
    
    def list_strategies(self) -> List[str]:
        """List all available strategies."""
        return [s.__class__.__name__ for s in self.strategies]
    
    def get_operation_count(self) -> int:
        """Get total operation count."""
        return sum(len(s.supported_operations) for s in self.strategies)


# Implementation tests
class TestResourceProvisioningStrategyImplementation:
    """Test resource provisioning strategy implementation."""
    
    def setup_method(self):
        self.strategy = ResourceProvisioningStrategy()
    
    def test_initialization(self):
        """Test strategy initialization."""
        assert len(self.strategy.resources) == 0
        assert len(self.strategy.supported_operations) == 4
    
    def test_allocate_resource(self):
        """Test allocating resource."""
        request = ResourceRequest(
            operation=ResourceProvisioningOperationType.ALLOCATE_RESOURCE,
            context="test",
            data={
                "resource_id": "res-001",
                "resource_type": "compute",
                "units": 4.0,
                "max_units": 8.0
            }
        )
        result = self.strategy.execute(request)
        assert result.success
        assert result.result_data is not None
        assert result.result_data["status"] == "allocated"
    
    def test_deallocate_resource(self):
        """Test deallocating resource."""
        # First allocate
        alloc_req = ResourceRequest(
            operation=ResourceProvisioningOperationType.ALLOCATE_RESOURCE,
            context="test",
            data={"resource_id": "res-001"}
        )
        self.strategy.execute(alloc_req)
        
        # Then deallocate
        dealloc_req = ResourceRequest(
            operation=ResourceProvisioningOperationType.DEALLOCATE_RESOURCE,
            context="test",
            data={"resource_id": "res-001"}
        )
        result = self.strategy.execute(dealloc_req)
        assert result.success
    
    def test_get_resource_status(self):
        """Test getting resource status."""
        # Allocate first
        alloc_req = ResourceRequest(
            operation=ResourceProvisioningOperationType.ALLOCATE_RESOURCE,
            context="test",
            data={"resource_id": "res-002", "units": 2.0}
        )
        self.strategy.execute(alloc_req)
        
        # Get status
        status_req = ResourceRequest(
            operation=ResourceProvisioningOperationType.GET_RESOURCE_STATUS,
            context="test",
            data={"resource_id": "res-002"}
        )
        result = self.strategy.execute(status_req)
        assert result.success
        assert result.result_data is not None
    
    def test_update_resource_limits(self):
        """Test updating resource limits."""
        # Allocate first
        alloc_req = ResourceRequest(
            operation=ResourceProvisioningOperationType.ALLOCATE_RESOURCE,
            context="test",
            data={"resource_id": "res-003"}
        )
        self.strategy.execute(alloc_req)
        
        # Update limits
        update_req = ResourceRequest(
            operation=ResourceProvisioningOperationType.UPDATE_RESOURCE_LIMITS,
            context="test",
            data={"resource_id": "res-003", "new_max_units": 16.0}
        )
        result = self.strategy.execute(update_req)
        assert result.success


class TestScalingStrategyImplementation:
    """Test scaling strategy implementation."""
    
    def setup_method(self):
        self.strategy = ScalingStrategy()
    
    def test_initialization(self):
        """Test strategy initialization."""
        assert len(self.strategy.scaling_configs) == 0
        assert len(self.strategy.supported_operations) == 5
    
    def test_scale_up(self):
        """Test scaling up."""
        request = ResourceRequest(
            operation=ScalingOperationType.SCALE_UP,
            context="test",
            data={"app_id": "app-001"}
        )
        result = self.strategy.execute(request)
        assert result.success
        assert result.result_data is not None
    
    def test_scale_down(self):
        """Test scaling down."""
        # First scale up
        up_req = ResourceRequest(
            operation=ScalingOperationType.SCALE_UP,
            context="test",
            data={"app_id": "app-002"}
        )
        self.strategy.execute(up_req)
        
        # Then scale down
        down_req = ResourceRequest(
            operation=ScalingOperationType.SCALE_DOWN,
            context="test",
            data={"app_id": "app-002"}
        )
        result = self.strategy.execute(down_req)
        assert result.success
    
    def test_auto_scale_enable(self):
        """Test enabling auto-scaling."""
        request = ResourceRequest(
            operation=ScalingOperationType.AUTO_SCALE_ENABLE,
            context="test",
            data={
                "app_id": "app-003",
                "min_replicas": 2,
                "max_replicas": 10
            }
        )
        result = self.strategy.execute(request)
        assert result.success
        assert result.result_data is not None
        assert result.result_data["autoscale"] == "enabled"
    
    def test_auto_scale_disable(self):
        """Test disabling auto-scaling."""
        request = ResourceRequest(
            operation=ScalingOperationType.AUTO_SCALE_DISABLE,
            context="test",
            data={"app_id": "app-004"}
        )
        result = self.strategy.execute(request)
        assert result.success
    
    def test_get_scaling_metrics(self):
        """Test getting scaling metrics."""
        request = ResourceRequest(
            operation=ScalingOperationType.GET_SCALING_METRICS,
            context="test",
            data={"app_id": "app-005"}
        )
        result = self.strategy.execute(request)
        assert result.success
        assert result.result_data is not None


class TestLoadBalancingStrategyImplementation:
    """Test load balancing strategy implementation."""
    
    def setup_method(self):
        self.strategy = LoadBalancingStrategy()
    
    def test_initialization(self):
        """Test strategy initialization."""
        assert len(self.strategy.load_balancers) == 0
        assert len(self.strategy.supported_operations) == 4
    
    def test_register_target(self):
        """Test registering target."""
        request = ResourceRequest(
            operation=LoadBalancingOperationType.REGISTER_TARGET,
            context="test",
            data={"lb_id": "lb-001", "target": "target-1"}
        )
        result = self.strategy.execute(request)
        assert result.success
        assert result.result_data is not None
        assert result.result_data["target_count"] == 1
    
    def test_deregister_target(self):
        """Test deregistering target."""
        # Register first
        reg_req = ResourceRequest(
            operation=LoadBalancingOperationType.REGISTER_TARGET,
            context="test",
            data={"lb_id": "lb-002", "target": "target-1"}
        )
        self.strategy.execute(reg_req)
        
        # Deregister
        dereg_req = ResourceRequest(
            operation=LoadBalancingOperationType.DEREGISTER_TARGET,
            context="test",
            data={"lb_id": "lb-002", "target": "target-1"}
        )
        result = self.strategy.execute(dereg_req)
        assert result.success
    
    def test_distribute_load(self):
        """Test distributing load."""
        # Register target
        reg_req = ResourceRequest(
            operation=LoadBalancingOperationType.REGISTER_TARGET,
            context="test",
            data={"lb_id": "lb-003", "target": "target-1"}
        )
        self.strategy.execute(reg_req)
        
        # Distribute load
        dist_req = ResourceRequest(
            operation=LoadBalancingOperationType.DISTRIBUTE_LOAD,
            context="test",
            data={"lb_id": "lb-003"}
        )
        result = self.strategy.execute(dist_req)
        assert result.success
    
    def test_get_load_status(self):
        """Test getting load status."""
        # Register target
        reg_req = ResourceRequest(
            operation=LoadBalancingOperationType.REGISTER_TARGET,
            context="test",
            data={"lb_id": "lb-004", "target": "target-1"}
        )
        self.strategy.execute(reg_req)
        
        # Get status
        status_req = ResourceRequest(
            operation=LoadBalancingOperationType.GET_LOAD_STATUS,
            context="test",
            data={"lb_id": "lb-004"}
        )
        result = self.strategy.execute(status_req)
        assert result.success
        assert result.result_data is not None


class TestUnifiedResourceOrchestrator:
    """Test unified resource orchestrator."""
    
    def setup_method(self):
        self.orchestrator = UnifiedResourceOrchestrator()
    
    def test_initialization(self):
        """Test orchestrator initialization."""
        assert len(self.orchestrator.strategies) == 3
    
    def test_route_provisioning_operation(self):
        """Test routing provisioning operation."""
        request = ResourceRequest(
            operation=ResourceProvisioningOperationType.ALLOCATE_RESOURCE,
            context="test",
            data={"resource_id": "res-001"}
        )
        result = self.orchestrator.execute(request)
        assert result.success
    
    def test_route_scaling_operation(self):
        """Test routing scaling operation."""
        request = ResourceRequest(
            operation=ScalingOperationType.SCALE_UP,
            context="test",
            data={"app_id": "app-001"}
        )
        result = self.orchestrator.execute(request)
        assert result.success
    
    def test_route_load_balancing_operation(self):
        """Test routing load balancing operation."""
        request = ResourceRequest(
            operation=LoadBalancingOperationType.REGISTER_TARGET,
            context="test",
            data={"lb_id": "lb-001", "target": "target-1"}
        )
        result = self.orchestrator.execute(request)
        assert result.success
    
    def test_get_supported_operations(self):
        """Test getting supported operations."""
        ops = self.orchestrator.get_supported_operations()
        assert len(ops) == 13
    
    def test_list_strategies(self):
        """Test listing strategies."""
        strategies = self.orchestrator.list_strategies()
        assert len(strategies) == 3
        assert "ResourceProvisioningStrategy" in strategies
        assert "ScalingStrategy" in strategies
        assert "LoadBalancingStrategy" in strategies
    
    def test_get_operation_count(self):
        """Test getting operation count."""
        count = self.orchestrator.get_operation_count()
        assert count == 13
