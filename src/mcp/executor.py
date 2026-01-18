"""Tool Execution Framework - Reliable execution with timeout and error handling."""
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import threading
import time

from src.mcp.protocol import MCPTool, MCPResponse, MCPError, ErrorCode, ToolValidator, ToolDefinition

class ExecutionState(Enum):
    """Tool execution states."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"

@dataclass
class ExecutionContext:
    """Execution context for a tool call."""
    execution_id: str
    tool_id: str
    parameters: Dict[str, Any]
    state: ExecutionState = ExecutionState.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[MCPError] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_time_ms: int = 0

class ToolExecutor:
    """Executes MCP tools safely with timeout support."""
    
    def __init__(self, timeout_ms: int = 30000):
        """Initialize executor."""
        self.timeout_ms = timeout_ms
        self.executions: Dict[str, ExecutionContext] = {}
        self.execution_counter = 0
    
    def execute(self, tool: MCPTool, definition: ToolDefinition, params: Dict[str, Any]) -> MCPResponse:
        """Execute tool with validation and timeout."""
        execution_id = f"exec_{self.execution_counter}_{datetime.now().timestamp()}"
        self.execution_counter += 1
        
        context = ExecutionContext(
            execution_id=execution_id,
            tool_id=definition.id,
            parameters=params
        )
        self.executions[execution_id] = context
        
        # Validate parameters
        is_valid, error_msg = ToolValidator.validate_all_params(definition, params)
        if not is_valid:
            error = MCPError(
                code=ErrorCode.INVALID_PARAMS,
                message=error_msg
            )
            return MCPResponse(id=execution_id, error=error)
        
        # Execute with timeout
        context.state = ExecutionState.RUNNING
        context.started_at = datetime.now()
        
        result_holder = {"result": None, "error": None}
        
        def execute_tool():
            try:
                result = tool.execute(**params)
                result_holder["result"] = result
            except Exception as e:
                result_holder["error"] = e
        
        thread = threading.Thread(target=execute_tool, daemon=True)
        thread.start()
        thread.join(timeout=definition.timeout_ms / 1000)
        
        # Check if timed out
        if thread.is_alive():
            context.state = ExecutionState.TIMEOUT
            context.completed_at = datetime.now()
            context.execution_time_ms = int((context.completed_at - context.started_at).total_seconds() * 1000)
            
            error = MCPError(
                code=ErrorCode.TIMEOUT,
                message=f"Tool execution exceeded timeout of {definition.timeout_ms}ms"
            )
            return MCPResponse(id=execution_id, error=error)
        
        # Handle results
        context.completed_at = datetime.now()
        context.execution_time_ms = int((context.completed_at - context.started_at).total_seconds() * 1000)
        
        if result_holder["error"]:
            error = result_holder["error"]
            error_code = tool.get_error_code(error) if hasattr(tool, "get_error_code") else ErrorCode.EXECUTION_ERROR
            
            context.state = ExecutionState.FAILED
            mcp_error = MCPError(
                code=error_code,
                message=str(error)
            )
            context.error = mcp_error
            return MCPResponse(id=execution_id, error=mcp_error)
        
        # Success
        context.state = ExecutionState.COMPLETED
        context.result = result_holder["result"]
        
        return MCPResponse(
            id=execution_id,
            result={
                "data": result_holder["result"],
                "execution_time_ms": context.execution_time_ms
            }
        )
    
    def get_execution_context(self, execution_id: str) -> Optional[ExecutionContext]:
        """Get execution context."""
        return self.executions.get(execution_id)
    
    def get_execution_history(self, tool_id: str, limit: int = 100) -> list:
        """Get execution history for a tool."""
        contexts = [c for c in self.executions.values() if c.tool_id == tool_id]
        return sorted(contexts, key=lambda c: c.started_at or datetime.now(), reverse=True)[:limit]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get executor statistics."""
        total = len(self.executions)
        completed = sum(1 for c in self.executions.values() if c.state == ExecutionState.COMPLETED)
        failed = sum(1 for c in self.executions.values() if c.state == ExecutionState.FAILED)
        timeout = sum(1 for c in self.executions.values() if c.state == ExecutionState.TIMEOUT)
        
        avg_time = 0
        completed_contexts = [c for c in self.executions.values() if c.execution_time_ms > 0]
        if completed_contexts:
            avg_time = sum(c.execution_time_ms for c in completed_contexts) / len(completed_contexts)
        
        return {
            "total_executions": total,
            "completed": completed,
            "failed": failed,
            "timeout": timeout,
            "success_rate": completed / total if total > 0 else 0,
            "avg_execution_time_ms": avg_time
        }
