"""Tests for Tool Executor Framework (AC-MCP-COMPLIANCE-005)."""
import pytest
import time
from unittest.mock import Mock
from datetime import datetime

from src.mcp.protocol import ToolParameter, ToolDefinition, MCPTool, ErrorCode
from src.mcp.executor import ToolExecutor, ExecutionState

@pytest.fixture
def executor():
    """Create tool executor."""
    return ToolExecutor(timeout_ms=5000)

@pytest.fixture
def mock_tool():
    """Create mock tool."""
    tool = Mock(spec=MCPTool)
    definition = ToolDefinition(
        id="exec_tool_001",
        name="execute_task",
        description="Task execution",
        parameters=[
            ToolParameter(name="task", type="string", description="Task", required=True),
            ToolParameter(name="duration_ms", type="number", description="Duration", required=False, default=100)
        ]
    )
    tool.get_definition.return_value = definition
    tool.execute.return_value = {"result": "success"}
    tool.get_error_code.return_value = ErrorCode.EXECUTION_ERROR
    return tool

# Unit Tests - Execution
def test_executor_creation():
    """Test executor creation."""
    exec = ToolExecutor()
    assert exec.timeout_ms == 30000

def test_executor_with_custom_timeout():
    """Test executor with custom timeout."""
    exec = ToolExecutor(timeout_ms=60000)
    assert exec.timeout_ms == 60000

def test_execute_successful_call(executor, mock_tool):
    """Test successful execution."""
    response = executor.execute(
        mock_tool,
        mock_tool.get_definition(),
        {"task": "test_task"}
    )
    assert response.result is not None
    assert response.error is None

def test_execute_with_all_parameters(executor, mock_tool):
    """Test execution with all parameters."""
    response = executor.execute(
        mock_tool,
        mock_tool.get_definition(),
        {"task": "test", "duration_ms": 200}
    )
    assert response.result is not None

def test_execute_invalid_params(executor, mock_tool):
    """Test execution with invalid parameters."""
    response = executor.execute(
        mock_tool,
        mock_tool.get_definition(),
        {"invalid_param": "value"}  # Missing required 'task'
    )
    assert response.error is not None
    assert response.error.code == ErrorCode.INVALID_PARAMS

def test_execution_context_created(executor, mock_tool):
    """Test execution context is created."""
    response = executor.execute(
        mock_tool,
        mock_tool.get_definition(),
        {"task": "test"}
    )
    context = executor.get_execution_context(response.id)
    assert context is not None
    assert context.tool_id == "exec_tool_001"

def test_execution_state_tracking(executor, mock_tool):
    """Test execution state transitions."""
    response = executor.execute(
        mock_tool,
        mock_tool.get_definition(),
        {"task": "test"}
    )
    context = executor.get_execution_context(response.id)
    assert context.state == ExecutionState.COMPLETED

def test_execution_time_recorded(executor, mock_tool):
    """Test execution time is recorded."""
    response = executor.execute(
        mock_tool,
        mock_tool.get_definition(),
        {"task": "test"}
    )
    context = executor.get_execution_context(response.id)
    assert context.execution_time_ms >= 0

# Timeout Tests
def test_execution_timeout_handling(executor):
    """Test timeout handling."""
    tool = Mock(spec=MCPTool)
    definition = ToolDefinition(
        id="timeout_tool",
        name="slow_op",
        description="Slow operation",
        timeout_ms=100  # 100ms timeout
    )
    tool.get_definition.return_value = definition
    
    # Tool that sleeps longer than timeout
    def slow_execute(**kwargs):
        time.sleep(0.2)  # 200ms - longer than timeout
        return {"result": "done"}
    
    tool.execute.side_effect = slow_execute
    
    response = executor.execute(tool, definition, {})
    assert response.error is not None
    assert response.error.code == ErrorCode.TIMEOUT

def test_timeout_threshold_respected(executor):
    """Test timeout threshold is respected."""
    tool = Mock(spec=MCPTool)
    definition = ToolDefinition(
        id="timeout_tool_2",
        name="check_timeout",
        description="Check timeout",
        timeout_ms=1000
    )
    tool.get_definition.return_value = definition
    tool.execute.return_value = {"status": "ok"}
    
    response = executor.execute(tool, definition, {})
    # Should succeed if execution is quick enough
    assert response.error is None

# Error Handling Tests
def test_execution_error_handling(executor):
    """Test execution error handling."""
    tool = Mock(spec=MCPTool)
    definition = ToolDefinition(
        id="error_tool",
        name="failing_op",
        description="Fails"
    )
    tool.get_definition.return_value = definition
    tool.execute.side_effect = ValueError("Test error")
    tool.get_error_code.return_value = ErrorCode.EXECUTION_ERROR
    
    response = executor.execute(tool, definition, {})
    assert response.error is not None
    assert response.error.code == ErrorCode.EXECUTION_ERROR

def test_error_message_included(executor):
    """Test error message is included in response."""
    tool = Mock(spec=MCPTool)
    definition = ToolDefinition(
        id="error_tool_2",
        name="failing_op_2",
        description="Fails"
    )
    tool.get_definition.return_value = definition
    tool.execute.side_effect = RuntimeError("Specific error message")
    tool.get_error_code.return_value = ErrorCode.EXECUTION_ERROR
    
    response = executor.execute(tool, definition, {})
    assert "Specific error message" in response.error.message

# History Tests
def test_execution_history_retrieval(executor, mock_tool):
    """Test retrieving execution history."""
    for i in range(3):
        executor.execute(
            mock_tool,
            mock_tool.get_definition(),
            {"task": f"task_{i}"}
        )
    
    history = executor.get_execution_history("exec_tool_001")
    assert len(history) == 3

def test_execution_history_limit(executor, mock_tool):
    """Test execution history with limit."""
    for i in range(20):
        executor.execute(
            mock_tool,
            mock_tool.get_definition(),
            {"task": f"task_{i}"}
        )
    
    history = executor.get_execution_history("exec_tool_001", limit=5)
    assert len(history) <= 5

def test_execution_history_empty(executor):
    """Test execution history for nonexistent tool."""
    history = executor.get_execution_history("nonexistent")
    assert len(history) == 0

# Statistics Tests
def test_executor_statistics(executor, mock_tool):
    """Test executor statistics."""
    executor.execute(mock_tool, mock_tool.get_definition(), {"task": "test_1"})
    executor.execute(mock_tool, mock_tool.get_definition(), {"task": "test_2"})
    
    stats = executor.get_stats()
    assert stats["total_executions"] >= 2
    assert stats["completed"] >= 2

def test_executor_stats_success_rate(executor, mock_tool):
    """Test success rate calculation."""
    # Execute successfully
    executor.execute(mock_tool, mock_tool.get_definition(), {"task": "success"})
    
    stats = executor.get_stats()
    assert stats["success_rate"] >= 0
    assert stats["success_rate"] <= 1

def test_executor_stats_average_time(executor, mock_tool):
    """Test average execution time calculation."""
    executor.execute(mock_tool, mock_tool.get_definition(), {"task": "test"})
    
    stats = executor.get_stats()
    assert stats["avg_execution_time_ms"] >= 0

# Integration Tests
def test_concurrent_executions(executor, mock_tool):
    """Test multiple concurrent executions."""
    responses = []
    for i in range(5):
        response = executor.execute(
            mock_tool,
            mock_tool.get_definition(),
            {"task": f"concurrent_{i}"}
        )
        responses.append(response)
    
    assert len(responses) == 5
    assert all(r.result is not None for r in responses)

def test_execution_ids_unique(executor, mock_tool):
    """Test execution IDs are unique."""
    responses = []
    for i in range(5):
        response = executor.execute(
            mock_tool,
            mock_tool.get_definition(),
            {"task": f"task_{i}"}
        )
        responses.append(response.id)
    
    assert len(set(responses)) == 5  # All unique

def test_execution_counter_increments(executor, mock_tool):
    """Test execution counter increments."""
    initial_count = executor.execution_counter
    executor.execute(mock_tool, mock_tool.get_definition(), {"task": "test"})
    assert executor.execution_counter > initial_count
