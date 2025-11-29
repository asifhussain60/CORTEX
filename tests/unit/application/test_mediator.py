"""Tests for Mediator pattern implementation"""
import pytest
from src.application.common.mediator import Mediator
from src.application.common.interfaces import (
    ICommand, IQuery, IRequestHandler, IPipelineBehavior, IRequest
)
from src.application.common.result import Result
from dataclasses import dataclass
from typing import Callable, Awaitable, Union


# Test commands and queries
@dataclass
class TestCommand(ICommand):
    """Test command"""
    value: str


@dataclass
class TestQuery(IQuery[str]):
    """Test query"""
    search: str


@dataclass
class FailingCommand(ICommand):
    """Command that should fail"""
    should_fail: bool = True


# Test handlers
class TestCommandHandler(IRequestHandler[TestCommand, Result[str]]):
    """Test command handler"""
    
    def __init__(self):
        self.executed = False
        
    async def handle(self, request: TestCommand) -> Result[str]:
        self.executed = True
        return Result.success(f"Handled: {request.value}")


class TestQueryHandler(IRequestHandler[TestQuery, Result[str]]):
    """Test query handler"""
    
    def __init__(self):
        self.executed = False
        
    async def handle(self, request: TestQuery) -> Result[str]:
        self.executed = True
        return Result.success(f"Found: {request.search}")


class FailingCommandHandler(IRequestHandler[FailingCommand, Result[str]]):
    """Handler that returns failure"""
    
    async def handle(self, request: FailingCommand) -> Result[str]:
        if request.should_fail:
            return Result.failure(["Command failed"])
        return Result.success("Success")


# Test behaviors
class TestBehavior(IPipelineBehavior):
    """Test pipeline behavior"""
    
    def __init__(self, name: str):
        self.name = name
        self.executed = False
        self.execution_order = []
        
    async def handle(
        self,
        request,
        next_handler: Callable[[Union[ICommand, IQuery]], Awaitable[Result]]
    ) -> Result:
        self.executed = True
        self.execution_order.append(f"{self.name}_before")
        result = await next_handler(request)
        self.execution_order.append(f"{self.name}_after")
        return result


class ShortCircuitBehavior(IPipelineBehavior):
    """Behavior that short-circuits the pipeline"""
    
    def __init__(self):
        self.executed = False
        
    async def handle(
        self,
        request,
        next_handler: Callable[[Union[ICommand, IQuery]], Awaitable[Result]]
    ) -> Result:
        self.executed = True
        # Short-circuit - don't call next_handler
        return Result.failure(["Short-circuited"])


class ModifyingBehavior(IPipelineBehavior):
    """Behavior that modifies the result"""
    
    async def handle(
        self,
        request,
        next_handler: Callable[[Union[ICommand, IQuery]], Awaitable[Result]]
    ) -> Result:
        result = await next_handler(request)
        if result.is_success:
            # Modify the result
            return Result.success(f"Modified: {result.value}")
        return result


@pytest.mark.asyncio
class TestMediator:
    """Test suite for Mediator"""
    
    async def test_mediator_creation(self):
        """Test creating a mediator"""
        mediator = Mediator()
        assert mediator is not None
        assert mediator.get_handler_count() == 0
        assert mediator.get_behavior_count() == 0
    
    async def test_register_handler(self):
        """Test registering a handler"""
        mediator = Mediator()
        handler = TestCommandHandler()
        
        mediator.register_handler(TestCommand, handler)
        
        assert mediator.get_handler_count() == 1
    
    async def test_register_multiple_handlers(self):
        """Test registering multiple handlers"""
        mediator = Mediator()
        command_handler = TestCommandHandler()
        query_handler = TestQueryHandler()
        
        mediator.register_handler(TestCommand, command_handler)
        mediator.register_handler(TestQuery, query_handler)
        
        assert mediator.get_handler_count() == 2
    
    async def test_send_command_without_handler(self):
        """Test sending command without registered handler"""
        mediator = Mediator()
        command = TestCommand(value="test")
        
        result = await mediator.send(command)
        
        assert result.is_failure
        assert "No handler registered" in result.errors[0]
    
    async def test_send_command_with_handler(self):
        """Test sending command with registered handler"""
        mediator = Mediator()
        handler = TestCommandHandler()
        mediator.register_handler(TestCommand, handler)
        
        command = TestCommand(value="test")
        result = await mediator.send(command)
        
        assert result.is_success
        assert result.value == "Handled: test"
        assert handler.executed
    
    async def test_send_query_with_handler(self):
        """Test sending query with registered handler"""
        mediator = Mediator()
        handler = TestQueryHandler()
        mediator.register_handler(TestQuery, handler)
        
        query = TestQuery(search="data")
        result = await mediator.send(query)
        
        assert result.is_success
        assert result.value == "Found: data"
        assert handler.executed
    
    async def test_handler_returns_failure(self):
        """Test handler returning failure"""
        mediator = Mediator()
        handler = FailingCommandHandler()
        mediator.register_handler(FailingCommand, handler)
        
        command = FailingCommand(should_fail=True)
        result = await mediator.send(command)
        
        assert result.is_failure
        assert "Command failed" in result.errors
    
    async def test_register_behavior(self):
        """Test registering a behavior"""
        mediator = Mediator()
        behavior = TestBehavior("test")
        
        mediator.register_behavior(behavior)
        
        assert mediator.get_behavior_count() == 1
    
    async def test_register_multiple_behaviors(self):
        """Test registering multiple behaviors"""
        mediator = Mediator()
        behavior1 = TestBehavior("first")
        behavior2 = TestBehavior("second")
        
        mediator.register_behavior(behavior1)
        mediator.register_behavior(behavior2)
        
        assert mediator.get_behavior_count() == 2
    
    async def test_behavior_execution(self):
        """Test behavior executes before and after handler"""
        mediator = Mediator()
        behavior = TestBehavior("test")
        handler = TestCommandHandler()
        
        mediator.register_behavior(behavior)
        mediator.register_handler(TestCommand, handler)
        
        command = TestCommand(value="test")
        result = await mediator.send(command)
        
        assert result.is_success
        assert behavior.executed
        assert handler.executed
        assert "test_before" in behavior.execution_order
        assert "test_after" in behavior.execution_order
    
    async def test_behavior_execution_order(self):
        """Test behaviors execute in registration order"""
        execution_order = []  # Shared list
        
        class OrderTrackingBehavior(IPipelineBehavior):
            def __init__(self, name):
                self.name = name
                
            async def handle(self, request, next_handler):
                execution_order.append(f"{self.name}_before")
                result = await next_handler(request)
                execution_order.append(f"{self.name}_after")
                return result
        
        mediator = Mediator()
        behavior1 = OrderTrackingBehavior("first")
        behavior2 = OrderTrackingBehavior("second")
        handler = TestCommandHandler()
        
        mediator.register_behavior(behavior1)
        mediator.register_behavior(behavior2)
        mediator.register_handler(TestCommand, handler)
        
        command = TestCommand(value="test")
        result = await mediator.send(command)
        
        assert result.is_success
        # Check execution order: first_before, second_before, handler, second_after, first_after
        assert execution_order == ["first_before", "second_before", "second_after", "first_after"]
    
    async def test_short_circuit_behavior(self):
        """Test behavior can short-circuit pipeline"""
        mediator = Mediator()
        short_circuit = ShortCircuitBehavior()
        handler = TestCommandHandler()
        
        mediator.register_behavior(short_circuit)
        mediator.register_handler(TestCommand, handler)
        
        command = TestCommand(value="test")
        result = await mediator.send(command)
        
        assert result.is_failure
        assert "Short-circuited" in result.errors
        assert short_circuit.executed
        assert not handler.executed  # Handler should not execute
    
    async def test_modifying_behavior(self):
        """Test behavior can modify result"""
        mediator = Mediator()
        modifying = ModifyingBehavior()
        handler = TestCommandHandler()
        
        mediator.register_behavior(modifying)
        mediator.register_handler(TestCommand, handler)
        
        command = TestCommand(value="test")
        result = await mediator.send(command)
        
        assert result.is_success
        assert result.value == "Modified: Handled: test"
        assert handler.executed
    
    async def test_behavior_with_failing_handler(self):
        """Test behavior with handler that fails"""
        mediator = Mediator()
        behavior = TestBehavior("test")
        handler = FailingCommandHandler()
        
        mediator.register_behavior(behavior)
        mediator.register_handler(FailingCommand, handler)
        
        command = FailingCommand(should_fail=True)
        result = await mediator.send(command)
        
        assert result.is_failure
        assert behavior.executed
        # Behavior should still execute after handler
        assert "test_before" in behavior.execution_order
        assert "test_after" in behavior.execution_order
    
    async def test_multiple_commands_same_mediator(self):
        """Test sending multiple commands through same mediator"""
        mediator = Mediator()
        handler = TestCommandHandler()
        mediator.register_handler(TestCommand, handler)
        
        command1 = TestCommand(value="first")
        command2 = TestCommand(value="second")
        
        result1 = await mediator.send(command1)
        result2 = await mediator.send(command2)
        
        assert result1.is_success
        assert result1.value == "Handled: first"
        assert result2.is_success
        assert result2.value == "Handled: second"
    
    async def test_handler_overwrite_warning(self, caplog):
        """Test warning when overwriting handler"""
        import logging
        caplog.set_level(logging.WARNING)
        
        mediator = Mediator()
        handler1 = TestCommandHandler()
        handler2 = TestCommandHandler()
        
        mediator.register_handler(TestCommand, handler1)
        mediator.register_handler(TestCommand, handler2)
        
        # Check warning was logged about overwriting
        assert any("Overwriting" in record.message or "overwriting" in record.message.lower() 
                   for record in caplog.records)
    
    async def test_global_mediator_singleton(self):
        """Test global mediator singleton"""
        from src.application.common.mediator import get_mediator, reset_mediator
        
        # Reset first
        reset_mediator()
        
        mediator1 = get_mediator()
        mediator2 = get_mediator()
        
        assert mediator1 is mediator2
    
    async def test_reset_global_mediator(self):
        """Test resetting global mediator"""
        from src.application.common.mediator import get_mediator, reset_mediator
        
        mediator1 = get_mediator()
        handler = TestCommandHandler()
        mediator1.register_handler(TestCommand, handler)
        
        assert mediator1.get_handler_count() == 1
        
        reset_mediator()
        mediator2 = get_mediator()
        
        assert mediator2 is not mediator1
        assert mediator2.get_handler_count() == 0
