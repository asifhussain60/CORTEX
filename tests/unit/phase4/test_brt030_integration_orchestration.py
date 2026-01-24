"""
BRT-030: Integration & Orchestration

Enables integration of multiple resilience patterns and orchestration
of complex workflows.

Test Infrastructure (RED phase - Tests Before Implementation per CORE-008)
"""

import pytest
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Set, Callable
from threading import Lock
from enum import Enum
import time


class WorkflowState(Enum):
    """States of a workflow."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class StepState(Enum):
    """States of a workflow step."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRYING = "retrying"


@dataclass
class WorkflowStep:
    """A step in a workflow."""
    step_id: str
    name: str
    action: Callable[[Dict[str, Any]], Dict[str, Any]]
    dependencies: Set[str] = field(default_factory=set)
    state: StepState = StepState.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3


class Workflow(ABC):
    """Base class for workflows."""
    
    @abstractmethod
    def execute(self) -> bool:
        """Execute the workflow."""
        pass
    
    @abstractmethod
    def get_state(self) -> WorkflowState:
        """Get workflow state."""
        pass


class LinearWorkflow(Workflow):
    """Workflow with linear sequential execution."""
    
    def __init__(self, name: str):
        self.name = name
        self._steps: List[WorkflowStep] = []
        self._state = WorkflowState.PENDING
        self._context: Dict[str, Any] = {}
        self._lock = Lock()
    
    def add_step(self, step: WorkflowStep) -> bool:
        """Add a step to workflow."""
        with self._lock:
            if any(s.step_id == step.step_id for s in self._steps):
                return False
            
            self._steps.append(step)
            return True
    
    def execute(self) -> bool:
        """Execute workflow steps sequentially."""
        with self._lock:
            self._state = WorkflowState.RUNNING
        
        try:
            for step in self._steps:
                with self._lock:
                    step.state = StepState.RUNNING
                
                try:
                    result = step.action(self._context)
                    with self._lock:
                        step.result = result
                        step.state = StepState.COMPLETED
                        self._context[step.step_id] = result
                
                except Exception as e:
                    with self._lock:
                        step.error = str(e)
                        step.state = StepState.FAILED
                        self._state = WorkflowState.FAILED
                    return False
            
            with self._lock:
                self._state = WorkflowState.COMPLETED
            return True
        
        except Exception:
            with self._lock:
                self._state = WorkflowState.FAILED
            return False
    
    def get_state(self) -> WorkflowState:
        """Get workflow state."""
        with self._lock:
            return self._state
    
    def get_steps(self) -> List[WorkflowStep]:
        """Get workflow steps."""
        with self._lock:
            return self._steps.copy()


class DAGWorkflow(Workflow):
    """Workflow with DAG (Directed Acyclic Graph) execution."""
    
    def __init__(self, name: str):
        self.name = name
        self._steps: Dict[str, WorkflowStep] = {}
        self._state = WorkflowState.PENDING
        self._context: Dict[str, Any] = {}
        self._lock = Lock()
    
    def add_step(self, step: WorkflowStep) -> bool:
        """Add a step to workflow."""
        with self._lock:
            if step.step_id in self._steps:
                return False
            
            self._steps[step.step_id] = step
            return True
    
    def _get_executable_steps(self) -> List[str]:
        """Get steps ready for execution."""
        executable = []
        
        for step_id, step in self._steps.items():
            if step.state != StepState.PENDING:
                continue
            
            # Check if dependencies are completed
            all_deps_done = all(
                self._steps[dep].state == StepState.COMPLETED
                for dep in step.dependencies
                if dep in self._steps
            )
            
            if all_deps_done:
                executable.append(step_id)
        
        return executable
    
    def execute(self) -> bool:
        """Execute workflow with dependency resolution."""
        with self._lock:
            self._state = WorkflowState.RUNNING
        
        try:
            while True:
                with self._lock:
                    executable = self._get_executable_steps()
                
                if not executable:
                    break
                
                # Execute all executable steps
                for step_id in executable:
                    with self._lock:
                        step = self._steps[step_id]
                        step.state = StepState.RUNNING
                    
                    try:
                        result = step.action(self._context)
                        with self._lock:
                            step.result = result
                            step.state = StepState.COMPLETED
                            self._context[step_id] = result
                    
                    except Exception as e:
                        with self._lock:
                            step.error = str(e)
                            step.state = StepState.FAILED
                            self._state = WorkflowState.FAILED
                        return False
            
            with self._lock:
                self._state = WorkflowState.COMPLETED
            return True
        
        except Exception:
            with self._lock:
                self._state = WorkflowState.FAILED
            return False
    
    def get_state(self) -> WorkflowState:
        """Get workflow state."""
        with self._lock:
            return self._state
    
    def get_steps(self) -> Dict[str, WorkflowStep]:
        """Get workflow steps."""
        with self._lock:
            return {k: v for k, v in self._steps.items()}


class OrchestrationManager:
    """Manages workflow orchestration."""
    
    def __init__(self):
        self._workflows: Dict[str, Workflow] = {}
        self._execution_history: List[Dict[str, Any]] = []
        self._lock = Lock()
    
    def register_workflow(self, workflow_id: str, workflow: Workflow) -> bool:
        """Register a workflow."""
        with self._lock:
            if workflow_id in self._workflows:
                return False
            
            self._workflows[workflow_id] = workflow
            return True
    
    def execute_workflow(self, workflow_id: str) -> bool:
        """Execute a registered workflow."""
        with self._lock:
            workflow = self._workflows.get(workflow_id)
            if not workflow:
                return False
        
        start_time = time.time()
        success = workflow.execute()
        end_time = time.time()
        
        with self._lock:
            self._execution_history.append({
                "workflow_id": workflow_id,
                "success": success,
                "start_time": start_time,
                "end_time": end_time,
                "duration_ms": (end_time - start_time) * 1000
            })
        
        return success
    
    def get_workflow_state(self, workflow_id: str) -> Optional[WorkflowState]:
        """Get state of a workflow."""
        with self._lock:
            workflow = self._workflows.get(workflow_id)
            if not workflow:
                return None
            
            return workflow.get_state()
    
    def get_execution_history(self) -> List[Dict[str, Any]]:
        """Get execution history."""
        with self._lock:
            return self._execution_history.copy()


class IntegrationBridge:
    """Bridges different resilience pattern implementations."""
    
    def __init__(self):
        self._adapters: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {}
        self._lock = Lock()
    
    def register_adapter(
        self,
        pattern_type: str,
        adapter: Callable[[Dict[str, Any]], Dict[str, Any]]
    ) -> bool:
        """Register an adapter for a pattern."""
        with self._lock:
            if pattern_type in self._adapters:
                return False
            
            self._adapters[pattern_type] = adapter
            return True
    
    def adapt_pattern(
        self,
        pattern_type: str,
        context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Adapt pattern context."""
        with self._lock:
            adapter = self._adapters.get(pattern_type)
            if not adapter:
                return None
            
            try:
                return adapter(context)
            except Exception:
                return None


class DependencyResolver:
    """Resolves dependencies between workflow steps."""
    
    def __init__(self):
        self._dependencies: Dict[str, Set[str]] = {}
        self._lock = Lock()
    
    def add_dependency(self, step_id: str, depends_on: str) -> bool:
        """Add a dependency."""
        with self._lock:
            if step_id not in self._dependencies:
                self._dependencies[step_id] = set()
            
            self._dependencies[step_id].add(depends_on)
            return True
    
    def get_execution_order(self, steps: List[str]) -> List[str]:
        """Get execution order for steps."""
        with self._lock:
            # Topological sort
            visited = set()
            order = []
            
            def visit(step_id):
                if step_id in visited:
                    return
                
                visited.add(step_id)
                
                for dep in self._dependencies.get(step_id, set()):
                    if dep in steps:
                        visit(dep)
                
                order.append(step_id)
            
            for step_id in steps:
                visit(step_id)
            
            return order
    
    def has_circular_dependency(self) -> bool:
        """Check for circular dependencies."""
        with self._lock:
            visited = set()
            rec_stack = set()
            
            def has_cycle(node):
                visited.add(node)
                rec_stack.add(node)
                
                for dep in self._dependencies.get(node, set()):
                    if dep not in visited:
                        if has_cycle(dep):
                            return True
                    elif dep in rec_stack:
                        return True
                
                rec_stack.remove(node)
                return False
            
            for node in self._dependencies:
                if node not in visited:
                    if has_cycle(node):
                        return True
            
            return False


# ============================================================================
# TEST SUITE
# ============================================================================

class TestLinearWorkflow:
    """Test LinearWorkflow functionality."""
    
    def test_add_step(self):
        """Test adding step to workflow."""
        workflow = LinearWorkflow("test-workflow")
        step = WorkflowStep(
            "step1",
            "Test Step",
            lambda ctx: {"status": "ok"}
        )
        
        assert workflow.add_step(step)
    
    def test_execute_single_step(self):
        """Test executing workflow with single step."""
        workflow = LinearWorkflow("test-workflow")
        step = WorkflowStep(
            "step1",
            "Test Step",
            lambda ctx: {"status": "ok"}
        )
        workflow.add_step(step)
        
        assert workflow.execute()
        assert workflow.get_state() == WorkflowState.COMPLETED
    
    def test_execute_multiple_steps(self):
        """Test executing workflow with multiple steps."""
        workflow = LinearWorkflow("test-workflow")
        
        step1 = WorkflowStep(
            "step1",
            "Step 1",
            lambda ctx: {"value": 1}
        )
        step2 = WorkflowStep(
            "step2",
            "Step 2",
            lambda ctx: {"value": ctx.get("step1", {}).get("value", 0) + 1}
        )
        
        workflow.add_step(step1)
        workflow.add_step(step2)
        
        assert workflow.execute()
        assert workflow.get_state() == WorkflowState.COMPLETED
    
    def test_execute_failed_step(self):
        """Test workflow fails on step error."""
        workflow = LinearWorkflow("test-workflow")
        
        def failing_action(ctx):
            raise Exception("Step failed")
        
        step = WorkflowStep("step1", "Test Step", failing_action)
        workflow.add_step(step)
        
        assert not workflow.execute()
        assert workflow.get_state() == WorkflowState.FAILED


class TestDAGWorkflow:
    """Test DAGWorkflow functionality."""
    
    def test_add_step_with_dependency(self):
        """Test adding step with dependencies."""
        workflow = DAGWorkflow("test-dag")
        
        step1 = WorkflowStep("step1", "Step 1", lambda ctx: {"v": 1})
        step2 = WorkflowStep(
            "step2",
            "Step 2",
            lambda ctx: {"v": 2},
            dependencies={"step1"}
        )
        
        assert workflow.add_step(step1)
        assert workflow.add_step(step2)
    
    def test_execute_dag_with_dependencies(self):
        """Test executing DAG with dependencies."""
        workflow = DAGWorkflow("test-dag")
        
        step1 = WorkflowStep("step1", "Step 1", lambda ctx: {"v": 1})
        step2 = WorkflowStep(
            "step2",
            "Step 2",
            lambda ctx: {"v": 2},
            dependencies={"step1"}
        )
        step3 = WorkflowStep(
            "step3",
            "Step 3",
            lambda ctx: {"v": 3},
            dependencies={"step2"}
        )
        
        workflow.add_step(step1)
        workflow.add_step(step2)
        workflow.add_step(step3)
        
        assert workflow.execute()
        assert workflow.get_state() == WorkflowState.COMPLETED


class TestOrchestrationManager:
    """Test OrchestrationManager functionality."""
    
    def test_register_workflow(self):
        """Test registering workflow."""
        manager = OrchestrationManager()
        workflow = LinearWorkflow("test")
        
        assert manager.register_workflow("wf1", workflow)
    
    def test_execute_workflow(self):
        """Test executing workflow."""
        manager = OrchestrationManager()
        workflow = LinearWorkflow("test")
        
        step = WorkflowStep("step1", "Step 1", lambda ctx: {"ok": True})
        workflow.add_step(step)
        
        manager.register_workflow("wf1", workflow)
        assert manager.execute_workflow("wf1")
    
    def test_get_workflow_state(self):
        """Test getting workflow state."""
        manager = OrchestrationManager()
        workflow = LinearWorkflow("test")
        
        manager.register_workflow("wf1", workflow)
        state = manager.get_workflow_state("wf1")
        
        assert state == WorkflowState.PENDING
    
    def test_get_execution_history(self):
        """Test getting execution history."""
        manager = OrchestrationManager()
        workflow = LinearWorkflow("test")
        
        step = WorkflowStep("step1", "Step 1", lambda ctx: {"ok": True})
        workflow.add_step(step)
        
        manager.register_workflow("wf1", workflow)
        manager.execute_workflow("wf1")
        
        history = manager.get_execution_history()
        assert len(history) == 1
        assert history[0]["success"]


class TestIntegrationBridge:
    """Test IntegrationBridge functionality."""
    
    def test_register_adapter(self):
        """Test registering adapter."""
        bridge = IntegrationBridge()
        adapter = lambda ctx: {"adapted": True}
        
        assert bridge.register_adapter("pattern1", adapter)
    
    def test_adapt_pattern(self):
        """Test adapting pattern."""
        bridge = IntegrationBridge()
        adapter = lambda ctx: {"adapted": True, "original": ctx}
        bridge.register_adapter("pattern1", adapter)
        
        result = bridge.adapt_pattern("pattern1", {"input": "data"})
        assert result["adapted"] is True


class TestDependencyResolver:
    """Test DependencyResolver functionality."""
    
    def test_add_dependency(self):
        """Test adding dependency."""
        resolver = DependencyResolver()
        assert resolver.add_dependency("step2", "step1")
    
    def test_get_execution_order(self):
        """Test getting execution order."""
        resolver = DependencyResolver()
        
        resolver.add_dependency("step2", "step1")
        resolver.add_dependency("step3", "step2")
        
        order = resolver.get_execution_order(["step1", "step2", "step3"])
        assert order.index("step1") < order.index("step2")
        assert order.index("step2") < order.index("step3")
    
    def test_has_no_circular_dependency(self):
        """Test checking for no circular dependencies."""
        resolver = DependencyResolver()
        
        resolver.add_dependency("step2", "step1")
        resolver.add_dependency("step3", "step2")
        
        assert not resolver.has_circular_dependency()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
