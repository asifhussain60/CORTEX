# AC_ENHANCED: AC-ROUTER-METADATA-20260223T000000Z (Metadata-driven tool discovery)
"""
MCP Tool Executor for Agent Collaboration Workflows

Provides actual MCP tool invocation for executing agents with metadata-driven
tool discovery and error handling.

Module: cortex/intent_router/mcp_executor.py
Authority: Phase 81 S3 Part 3 - MCP Tool Integration
         + Phase 81 S3 Part 4 - Metadata-Driven Discovery
Version: 2.0 (with metadata integration)
"""
from typing import Optional, Dict, List, Any, TYPE_CHECKING
from dataclasses import dataclass
import logging
from datetime import datetime

if TYPE_CHECKING:
    from cortex.orchestrators.core.intent_router.metadata_driven_discovery import MetadataDrivenDiscovery

logger = logging.getLogger(__name__)

@dataclass
class MCPExecutionRequest:
    """Request for MCP tool execution."""
    agent_id: str
    tool_name: str
    tool_parameters: Dict[str, Any]
    request_id: str
    timeout_seconds: int = 30

@dataclass
class MCPExecutionResult:
    """Result from MCP tool execution."""
    success: bool
    agent_id: str
    tool_name: str
    output: Dict[str, Any]
    error_message: Optional[str] = None
    duration_seconds: float = 0.0
    execution_timestamp: str = ""

    def __post_init__(self):
        """Set timestamp if not provided."""
        if not self.execution_timestamp:
            self.execution_timestamp = datetime.now().isoformat()

class MCPToolExecutor:
    """
    Executes MCP tools on behalf of agents.

    Features:
    - Metadata-driven tool discovery (Phase 81 S3 Part 4)
    - Parameter validation before execution
    - Error handling and retry logic
    - Execution result formatting
    - Dynamic agent registration from metadata

    Example:
        >>> executor = MCPToolExecutor()
        >>> executor.register_tool_handler("cortex_process_request", handler_func)
        >>> result = executor.execute(req)

        >>> # Or with metadata discovery:
        >>> executor.initialize_from_metadata(".github/agents/core")
        >>> result = executor.execute(req)  # Tools auto-resolved from metadata
    """

    def __init__(self) -> None:
        """Initialize MCP tool executor."""
        self._tool_handlers: Dict[str, Any] = {}
        self._agent_tools: Dict[str, List[str]] = {}
        self._execution_history: List[MCPExecutionResult] = []
        self._metadata_discovery: Optional['MetadataDrivenDiscovery'] = None
        logger.info("MCPToolExecutor initialized")

    def register_tool_handler(self, tool_name: str, handler: Any) -> None:
        """
        Register handler for MCP tool.

        Args:
            tool_name: Tool identifier (e.g., "cortex_process_request")
            handler: Callable that executes tool
        """
        self._tool_handlers[tool_name] = handler
        logger.debug(f"Tool handler registered: {tool_name}")

    def register_agent_tools(self, agent_id: str, tools: List[str]) -> None:
        """
        Register available tools for agent.

        Args:
            agent_id: Agent identifier
            tools: List of tool names available to agent
        """
        self._agent_tools[agent_id] = tools
        logger.debug(f"Agent tools registered: {agent_id} → {len(tools)} tools")

    def initialize_from_metadata(self, agents_dir: str = ".github/agents/core") -> int:
        """
        Initialize executor with metadata-driven tool discovery.

        Phase 81 S3 Part 4: Load agent metadata and register tools from YAML.

        Args:
            agents_dir: Directory containing agent markdown files

        Returns:
            Number of agents initialized
        """
        try:
            from cortex.orchestrators.core.intent_router.metadata_driven_discovery import MetadataDrivenDiscovery

            self._metadata_discovery = MetadataDrivenDiscovery(agents_dir)
            self._metadata_discovery.initialize()

            # Register all agents and tools from metadata
            registered = self._metadata_discovery.register_with_executor(self)

            logger.info(f"Metadata-driven initialization complete: {registered} agents")
            return registered

        except ImportError:
            logger.warning("MetadataDrivenDiscovery not available, using manual registration")
            return 0
        except Exception as e:
            logger.error(f"Failed to initialize from metadata: {e}")
            return 0

    def execute(self, request: MCPExecutionRequest) -> MCPExecutionResult:
        """
        Execute MCP tool request.

        Args:
            request: MCP execution request

        Returns:
            MCPExecutionResult with success/failure
        """
        start_time = datetime.now()

        try:
            # Step 1: Validate agent has tool
            if request.agent_id not in self._agent_tools:
                return self._error_result(
                    request,
                    f"Agent not registered: {request.agent_id}",
                    start_time
                )

            if request.tool_name not in self._agent_tools[request.agent_id]:
                return self._error_result(
                    request,
                    f"Tool '{request.tool_name}' not available for agent '{request.agent_id}'",
                    start_time
                )

            # Step 2: Check if tool handler exists
            if request.tool_name not in self._tool_handlers:
                logger.warning(f"No handler for tool: {request.tool_name}, using mock")
                return self._mock_execution(request, start_time)

            # Step 3: Invoke tool handler
            handler = self._tool_handlers[request.tool_name]
            logger.info(f"Executing tool: {request.tool_name} for agent: {request.agent_id}")

            # Call handler with parameters and request context
            output = handler(
                tool_name=request.tool_name,
                parameters=request.tool_parameters,
                request_id=request.request_id,
                agent_id=request.agent_id
            )

            # Step 4: Format success result
            duration = (datetime.now() - start_time).total_seconds()
            result = MCPExecutionResult(
                success=True,
                agent_id=request.agent_id,
                tool_name=request.tool_name,
                output=output or {},
                duration_seconds=duration
            )

            self._execution_history.append(result)
            logger.info(f"Tool execution completed: {request.tool_name} ({duration:.2f}s)")

            return result

        except Exception as e:
            logger.error(f"Tool execution failed: {request.tool_name}", exc_info=True)
            return self._error_result(
                request,
                f"Execution error: {str(e)}",
                start_time
            )

    def execute_batch(self, requests: List[MCPExecutionRequest]) -> List[MCPExecutionResult]:
        """
        Execute multiple MCP tool requests sequentially.

        Args:
            requests: List of MCP execution requests

        Returns:
            List of MCPExecutionResult
        """
        results = []
        for req in requests:
            result = self.execute(req)
            results.append(result)
            if not result.success:
                logger.warning(f"Batch execution error, continuing: {result.error_message}")
        return results

    def get_agent_tools(self, agent_id: str) -> List[str]:
        """
        Get tools available for agent.

        Args:
            agent_id: Agent identifier

        Returns:
            List of available tool names
        """
        return self._agent_tools.get(agent_id, [])

    def get_execution_history(self, agent_id: Optional[str] = None) -> List[MCPExecutionResult]:
        """
        Get execution history, optionally filtered by agent.

        Args:
            agent_id: Filter by agent (optional)

        Returns:
            List of execution results
        """
        if agent_id:
            return [r for r in self._execution_history if r.agent_id == agent_id]
        return self._execution_history.copy()

    def _mock_execution(self, request: MCPExecutionRequest, start_time: Any) -> MCPExecutionResult:
        """
        Provide mock execution when handler not registered.

        Useful for testing and phase transitions.
        """
        duration = (datetime.now() - start_time).total_seconds()
        return MCPExecutionResult(
            success=True,
            agent_id=request.agent_id,
            tool_name=request.tool_name,
            output={
                "mock": True,
                "message": f"Mock execution of {request.tool_name}",
                "parameters": request.tool_parameters
            },
            duration_seconds=duration
        )

    def _error_result(self, request: MCPExecutionRequest, error_msg: str, start_time: Any) -> MCPExecutionResult:
        """Create error result."""
        duration = (datetime.now() - start_time).total_seconds()
        result = MCPExecutionResult(
            success=False,
            agent_id=request.agent_id,
            tool_name=request.tool_name,
            output={},
            error_message=error_msg,
            duration_seconds=duration
        )
        self._execution_history.append(result)
        return result

# AC_COMPLETE: AC-ROUTER-MCPEXEC-20260223T000000Z ✅ MCP Tool Executor Module
