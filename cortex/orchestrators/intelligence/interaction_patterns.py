"""
Agent-Orchestrator Interaction Patterns (phase-81 S2).

Defines standardized protocols and patterns for agent↔orchestrator communication.

Authority: cortex-registry/_cortex-master/index.yaml WAVE-L
Created: 2026-02-12
AC-ID: AC-WAVE-L-002
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Protocol
from enum import Enum


class AgentResponseFormat(str, Enum):
    """Standard response formats for agents."""
    STRUCTURED = "structured"  # Dictionary with sections
    NARRATIVE = "narrative"    # Markdown formatted text
    LIST = "list"             # List of items
    TABLE = "table"           # Tabular data


@dataclass
class AgentRequest:
    """
    Standardized request from orchestrator to agent.
    
    Attributes:
        agent_name: Name of the agent to invoke
        operation: Operation to perform (e.g., "validate", "analyze")
        context: Contextual data for the operation
        format: Desired response format
        metadata: Additional metadata for the request
    """
    agent_name: str
    operation: str
    context: Dict[str, Any]
    format: AgentResponseFormat = AgentResponseFormat.STRUCTURED
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Initialize metadata if not provided."""
        if self.metadata is None:
            self.metadata = {}


@dataclass
class AgentResponse:
    """
    Standardized response from agent to orchestrator.
    
    Attributes:
        agent_name: Name of the responding agent
        operation: Operation that was performed
        success: Whether the operation succeeded
        data: Response data (format depends on request format)
        errors: List of errors if operation failed
        warnings: List of warnings
        metadata: Response metadata (execution time, version, etc.)
    """
    agent_name: str
    operation: str
    success: bool
    data: Any
    errors: Optional[List[str]] = None
    warnings: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Initialize lists if not provided."""
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
        if self.metadata is None:
            self.metadata = {}


class AgentProtocol(Protocol):
    """
    Protocol defining the interface all agents must implement.
    
    This is a structural typing protocol - agents don't need to inherit from it,
    they just need to implement the required methods.
    """
    
    def execute(self, request: AgentRequest) -> AgentResponse:
        """
        Execute an agent operation.
        
        Args:
            request: Standardized agent request
        
        Returns:
            Standardized agent response
        """
        raise NotImplementedError("execute not yet implemented")
    
    @property
    def name(self) -> str:
        """Get the agent's name."""
        ...
    
    @property
    def capabilities(self) -> List[str]:
        """Get the agent's capabilities."""
        ...


class AgentToOrchestratorBridge:
    """
    Bridge pattern for orchestrator→agent communication.
    
    Provides a clean abstraction layer between orchestrators and agents,
    handling request formatting, error handling, and response standardization.
    """
    
    def __init__(self) -> None:
        """Initialize the bridge."""
        self._agent_cache: Dict[str, Any] = {}
    
    def invoke_agent(
        self,
        agent_name: str,
        operation: str,
        context: Dict[str, Any],
        format: AgentResponseFormat = AgentResponseFormat.STRUCTURED,
    ) -> AgentResponse:
        """
        Invoke an agent with standardized request/response.
        
        Args:
            agent_name: Name of the agent to invoke
            operation: Operation to perform
            context: Contextual data
            format: Desired response format
        
        Returns:
            Standardized agent response
        
        Example:
            >>> bridge = AgentToOrchestratorBridge()
            >>> response = bridge.invoke_agent(
            ...     "cortex-executor",
            ...     "validate",
            ...     {"code": "print('hello')"}
            ... )
            >>> assert response.success
        """
        # Create standardized request
        request = AgentRequest(
            agent_name=agent_name,
            operation=operation,
            context=context,
            format=format,
        )
        
        # Get or load agent
        agent = self._get_agent(agent_name)
        
        if agent is None:
            return AgentResponse(
                agent_name=agent_name,
                operation=operation,
                success=False,
                data=None,
                errors=[f"Agent '{agent_name}' not found or not loaded"],
            )
        
        try:
            # Invoke agent
            response = agent.execute(request)
            return response
        
        except Exception as e:
            return AgentResponse(
                agent_name=agent_name,
                operation=operation,
                success=False,
                data=None,
                errors=[f"Agent execution failed: {str(e)}"],
            )
    
    def _get_agent(self, agent_name: str) -> Optional[Any]:
        """
        Get or load an agent.
        
        Args:
            agent_name: Name of the agent
        
        Returns:
            Agent instance or None if not found
        """
        # Check cache first
        if agent_name in self._agent_cache:
            return self._agent_cache[agent_name]
        
        # In a real implementation, this would:
        # 1. Use IntentAgentMapper to load agent metadata
        # 2. Instantiate the agent class
        # 3. Cache the instance
        # For now, return None (agents will be loaded externally)
        
        return None
    
    def preload_agent(self, agent_name: str, agent_instance: Any) -> None:
        """
        Preload an agent instance into the cache.
        
        Args:
            agent_name: Name of the agent
            agent_instance: Agent instance
        """
        self._agent_cache[agent_name] = agent_instance
    
    def clear_cache(self) -> None:
        """Clear the agent cache."""
        self._agent_cache.clear()


class OrchestratorAgentInvoker:
    """
    Mixin class for orchestrators to easily invoke agents.
    
    Provides convenience methods for common agent invocation patterns.
    Orchestrators can inherit from this to get agent invocation capabilities.
    """
    
    def __init__(self) -> None:
        """Initialize the invoker."""
        self.agent_bridge = AgentToOrchestratorBridge()
    
    def validate_with_agent(
        self,
        agent_name: str,
        validation_target: Any,
        **kwargs
    ) -> AgentResponse:
        """
        Invoke an agent for validation.
        
        Args:
            agent_name: Name of the validation agent
            validation_target: Target to validate
            **kwargs: Additional context
        
        Returns:
            Agent response
        """
        context = {
            "target": validation_target,
            **kwargs
        }
        
        return self.agent_bridge.invoke_agent(
            agent_name=agent_name,
            operation="validate",
            context=context,
        )
    
    def analyze_with_agent(
        self,
        agent_name: str,
        analysis_target: Any,
        **kwargs
    ) -> AgentResponse:
        """
        Invoke an agent for analysis.
        
        Args:
            agent_name: Name of the analysis agent
            analysis_target: Target to analyze
            **kwargs: Additional context
        
        Returns:
            Agent response
        """
        context = {
            "target": analysis_target,
            **kwargs
        }
        
        return self.agent_bridge.invoke_agent(
            agent_name=agent_name,
            operation="analyze",
            context=context,
        )
    
    def execute_with_agent(
        self,
        agent_name: str,
        execution_context: Dict[str, Any],
    ) -> AgentResponse:
        """
        Invoke an agent for execution.
        
        Args:
            agent_name: Name of the execution agent
            execution_context: Execution context
        
        Returns:
            Agent response
        """
        return self.agent_bridge.invoke_agent(
            agent_name=agent_name,
            operation="execute",
            context=execution_context,
        )


def format_agent_response_for_user(response: AgentResponse) -> str:
    """
    Format agent response for user display.
    
    Args:
        response: Agent response to format
    
    Returns:
        Formatted string for display
    
    Example:
        >>> response = AgentResponse(
        ...     agent_name="cortex-executor",
        ...     operation="validate",
        ...     success=True,
        ...     data={"status": "valid"}
        ... )
        >>> formatted = format_agent_response_for_user(response)
        >>> assert "cortex-executor" in formatted
    """
    lines = []
    
    # Header
    status_icon = "✅" if response.success else "❌"
    lines.append(f"{status_icon} **{response.agent_name}** ({response.operation})")
    lines.append("")
    
    # Data
    if response.data:
        if isinstance(response.data, dict):
            for key, value in response.data.items():
                lines.append(f"- **{key}:** {value}")
        elif isinstance(response.data, list):
            for item in response.data:
                lines.append(f"- {item}")
        else:
            lines.append(str(response.data))
        lines.append("")
    
    # Errors
    if response.errors:
        lines.append("**Errors:**")
        for error in response.errors:
            lines.append(f"- ❌ {error}")
        lines.append("")
    
    # Warnings
    if response.warnings:
        lines.append("**Warnings:**")
        for warning in response.warnings:
            lines.append(f"- ⚠️ {warning}")
        lines.append("")
    
    return "\n".join(lines)
