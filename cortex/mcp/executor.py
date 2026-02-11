"""MCP Executor

Author: CORTEX Framework
"""

import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from cortex.mcp.protocol import ErrorCode


class ExecutionState(Enum):
    """Tool execution states."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class ExecutionError:
    """Execution error details."""
    code: ErrorCode
    message: str


@dataclass
class ExecutionResponse:
    """Response from tool execution."""
    id: str
    result: Optional[Any] = None
    error: Optional[ExecutionError] = None
    execution_time_ms: float = 0.0


@dataclass
class ExecutionContext:
    """Context for a tool execution."""
    execution_id: str
    tool_id: str
    state: ExecutionState = ExecutionState.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    execution_time_ms: float = 0.0
    params: Dict[str, Any] = field(default_factory=dict)
    result: Optional[Any] = None
    error: Optional[ExecutionError] = None


class ToolExecutor:
    """Execute MCP tools with timeout, context tracking, and statistics.

    Provides comprehensive execution management including:
    - Timeout handling
    - Execution history
    - Statistics tracking
    - Context management
    """

    def __init__(self, timeout_ms: int = 30000):
        """Initialize executor.

        Args:
            timeout_ms: Default timeout in milliseconds.
        """
        self.timeout_ms = timeout_ms
        self._contexts: Dict[str, ExecutionContext] = {}
        self._history: Dict[str, List[ExecutionContext]] = {}  # tool_id -> executions
        self.execution_counter = 0
        self._total_execution_time = 0.0
        self._success_count = 0
        self._failure_count = 0

    def execute(self, tool, definition, params: Dict[str, Any]) -> ExecutionResponse:
        """Execute a tool.

        Args:
            tool: MCPTool instance to execute.
            definition: Tool definition.
            params: Parameters for execution.

        Returns:
            ExecutionResponse with result or error.
        """
        execution_id = str(uuid.uuid4())
        tool_id = definition.id

        # Create context
        context = ExecutionContext(
            execution_id=execution_id,
            tool_id=tool_id,
            state=ExecutionState.PENDING,
            params=params
        )
        self._contexts[execution_id] = context

        # Add to history
        if tool_id not in self._history:
            self._history[tool_id] = []
        self._history[tool_id].append(context)

        self.execution_counter += 1

        # Validate parameters using definition
        if hasattr(definition, 'validate_params'):
            is_valid, error_msg = definition.validate_params(params)
            if not is_valid:
                context.state = ExecutionState.FAILED
                context.error = ExecutionError(
                    code=ErrorCode.INVALID_PARAMS,
                    message=error_msg or "Invalid parameters"
                )
                self._failure_count += 1
                return ExecutionResponse(
                    id=execution_id,
                    error=context.error
                )
        else:
            # Basic validation: check required params
            for param_def in definition.parameters:
                if hasattr(param_def, 'required') and param_def.required:
                    if param_def.name not in params:
                        context.state = ExecutionState.FAILED
                        context.error = ExecutionError(
                            code=ErrorCode.INVALID_PARAMS,
                            message=f"Missing required parameter: {param_def.name}"
                        )
                        self._failure_count += 1
                        return ExecutionResponse(
                            id=execution_id,
                            error=context.error
                        )

        # Execute with timing
        context.state = ExecutionState.RUNNING
        context.start_time = datetime.now()

        # Get timeout (tool-specific or default)
        timeout_ms = getattr(definition, 'timeout_ms', None) or self.timeout_ms
        timeout_s = timeout_ms / 1000.0

        try:
            start_time = time.time()
            result = tool.execute(**params)
            elapsed = (time.time() - start_time) * 1000  # Convert to ms

            # Check timeout after execution (simple approach)
            if elapsed > timeout_ms:
                context.state = ExecutionState.TIMEOUT
                context.error = ExecutionError(
                    code=ErrorCode.TIMEOUT,
                    message=f"Execution timed out after {elapsed:.0f}ms (limit: {timeout_ms}ms)"
                )
                context.end_time = datetime.now()
                context.execution_time_ms = elapsed
                self._failure_count += 1
                return ExecutionResponse(
                    id=execution_id,
                    error=context.error,
                    execution_time_ms=elapsed
                )

            context.state = ExecutionState.COMPLETED
            context.result = result
            context.end_time = datetime.now()
            context.execution_time_ms = elapsed
            self._total_execution_time += elapsed
            self._success_count += 1

            return ExecutionResponse(
                id=execution_id,
                result=result,
                execution_time_ms=elapsed
            )

        except Exception as e:
            elapsed = (time.time() - start_time) * 1000 if 'start_time' in locals() else 0
            context.state = ExecutionState.FAILED
            context.end_time = datetime.now()
            context.execution_time_ms = elapsed

            # Get error code from tool if available
            error_code = ErrorCode.EXECUTION_ERROR
            if hasattr(tool, 'get_error_code'):
                try:
                    error_code = tool.get_error_code()
                except Exception:
                    pass

            context.error = ExecutionError(
                code=error_code,
                message=str(e)
            )
            self._failure_count += 1

            return ExecutionResponse(
                id=execution_id,
                error=context.error,
                execution_time_ms=elapsed
            )

    def get_execution_context(self, execution_id: str) -> Optional[ExecutionContext]:
        """Get execution context by ID.

        Args:
            execution_id: Execution identifier.

        Returns:
            ExecutionContext or None if not found.
        """
        return self._contexts.get(execution_id)

    def get_execution_history(self, tool_id: str, limit: Optional[int] = None) -> List[ExecutionContext]:
        """Get execution history for a tool.

        Args:
            tool_id: Tool identifier.
            limit: Maximum number of entries to return.

        Returns:
            List of execution contexts.
        """
        history = self._history.get(tool_id, [])
        if limit is not None:
            return history[-limit:]
        return history

    def get_stats(self) -> Dict[str, Any]:
        """Get executor statistics.

        Returns:
            Statistics dictionary.
        """
        total = self._success_count + self._failure_count
        success_rate = self._success_count / total if total > 0 else 0.0
        avg_time = self._total_execution_time / self._success_count if self._success_count > 0 else 0.0

        return {
            "total_executions": total,
            "completed": self._success_count,
            "failed": self._failure_count,
            "success_rate": success_rate,
            "avg_execution_time_ms": avg_time,
            "total_execution_time_ms": self._total_execution_time,
        }


class ToolExecutionEngine:
    """Enhanced tool execution."""

    def __init__(self, timeout_ms: int = 30000):
        """Initialize execution engine.

        Args:
            timeout_ms: Default timeout in milliseconds.
        """
        self.executor = ToolExecutor(timeout_ms=timeout_ms)

    def run(self, tool, definition, params: Dict[str, Any]) -> ExecutionResponse:
        """Run tool.

        Args:
            tool: Tool to execute.
            definition: Tool definition.
            params: Execution parameters.

        Returns:
            ExecutionResponse.
        """
        return self.executor.execute(tool, definition, params)

__all__ = ["ExecutionState", "ErrorCode", "ExecutionError", "ExecutionResponse", "ExecutionContext", "ToolExecutor", "ToolExecutionEngine"]
