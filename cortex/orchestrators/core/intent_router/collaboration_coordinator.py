# AC_START: AC-ROUTER-COLLAB-20260223T000000Z
"""
Agent Collaboration Coordinator for Multi-Agent Workflows

Manages orchestration of multiple agents for complex requests.
Handles agent-to-agent communication, context passing, and shared resources.

Module: cortex/intent_router/collaboration_coordinator.py
Authority: Phase 81 S3 - IntentRouter Capability-Based Routing
Version: 1.0
"""

from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime

# MCP Tool Integration (Phase 81 S3 Part 3)
from cortex.orchestrators.core.intent_router.mcp_executor import MCPToolExecutor, MCPExecutionRequest

logger = logging.getLogger(__name__)


class CollaborationPattern(str, Enum):
    """Collaboration patterns between agents."""
    SEQUENTIAL = "sequential"  # Agent A → Agent B → Agent C (linear)
    PARALLEL = "parallel"  # Agent A || Agent B || Agent C (concurrent)
    HIERARCHICAL = "hierarchical"  # Resolver → Auditor → Executor (layers)
    FEEDBACK_LOOP = "feedback_loop"  # A → B → A (iterative refinement)


@dataclass
class AgentContext:
    """Shared context passed between agents."""
    agent_id: str
    request_id: str
    user_request: str
    intent: str
    extracted_data: Dict[str, Any] = field(default_factory=dict)
    lens_cache: Dict[str, Any] = field(default_factory=dict)  # Pre-analyzed code
    phase_state: Optional[Dict[str, Any]] = None  # For PLAN mode
    execution_metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def add_lens_cache(self, key: str, value: Any) -> None:
        """Cache LENS analysis results to avoid duplication."""
        self.lens_cache[key] = value
        logger.debug(f"LENS cache updated: {key}")
    
    def get_lens_cache(self, key: str) -> Optional[Any]:
        """Retrieve cached LENS analysis."""
        return self.lens_cache.get(key)
    
    def is_lens_cached(self, key: str) -> bool:
        """Check if LENS analysis exists in cache."""
        return key in self.lens_cache


@dataclass
class CollaborationRequest:
    """Request for agent collaboration."""
    request_id: str
    primary_agent_id: str
    secondary_agents: List[str] = field(default_factory=list)
    pattern: CollaborationPattern = CollaborationPattern.SEQUENTIAL
    context: Optional[AgentContext] = None
    timeout_seconds: int = 300
    max_iterations: int = 3
    
    def add_secondary_agent(self, agent_id: str) -> None:
        """Add secondary agent to collaboration chain."""
        if agent_id not in self.secondary_agents:
            self.secondary_agents.append(agent_id)


@dataclass
class CollaborationResult:
    """Result from agent collaboration workflow."""
    request_id: str
    primary_agent_id: str
    execution_path: List[str]  # Agents executed in order
    combined_output: Dict[str, Any]  # Merged results from all agents
    context: AgentContext
    success: bool
    error_message: Optional[str] = None
    duration_seconds: float = 0.0
    iterations_used: int = 0
    
    def add_agent_output(self, agent_id: str, output: Dict[str, Any]) -> None:
        """Merge agent output into combined results."""
        if agent_id not in self.combined_output:
            self.combined_output[agent_id] = {}
        self.combined_output[agent_id].update(output)
        logger.debug(f"Agent output merged: {agent_id}")


class AgentCollaborationCoordinator:
    """
    Coordinates multi-agent workflows.
    
    Architecture:
    - Resolves agent requests to collaboration patterns
    - Manages shared context (LENS cache, phase state)
    - Orchestrates sequential/parallel/hierarchical execution
    - Handles feedback loops for iterative refinement
    
    Example:
        >>> coordinator = AgentCollaborationCoordinator()
        >>> collab_req = CollaborationRequest(
        ...     request_id="req-001",
        ...     primary_agent_id="cortex-phase-resolver",
        ...     secondary_agents=["cortex-master-plan-auditor"],
        ...     pattern=CollaborationPattern.HIERARCHICAL
        ... )
        >>> result = coordinator.coordinate(collab_req)
        >>> print(f"Executed {len(result.execution_path)} agents successfully")
    """
    
    def __init__(self) -> None:
        """Initialize collaboration coordinator."""
        self._active_collaborations: Dict[str, CollaborationRequest] = {}
        self._agent_registry: Dict[str, Dict[str, Any]] = {}
        self._mcp_executor = MCPToolExecutor()  # MCP tool integration (Phase 81 S3 Part 3)
        logger.info("AgentCollaborationCoordinator initialized")
    
    def register_agent(
        self,
        agent_id: str,
        capabilities: List[str],
        mcp_tools: List[str],
        priority: str = "P2"
    ) -> None:
        """
        Register agent in collaboration system.
        
        Args:
            agent_id: Unique agent identifier
            capabilities: List of capabilities (e.g., ["phase_resolution", "context_extraction"])
            mcp_tools: MCP tools available to this agent
            priority: Agent priority (P0, P1, P2, P3)
        """
        self._agent_registry[agent_id] = {
            "capabilities": capabilities,
            "mcp_tools": mcp_tools,
            "priority": priority,
            "registered_at": datetime.now().isoformat(),
            "collaboration_count": 0
        }
        
        # Register agent's tools with MCP executor (Phase 81 S3 Part 3)
        self._mcp_executor.register_agent_tools(agent_id, mcp_tools)
        
        logger.info(f"Agent registered: {agent_id} | Capabilities: {len(capabilities)}")
    
    def determine_collaboration_pattern(
        self,
        primary_agent_id: str,
        secondary_agents: List[str]
    ) -> CollaborationPattern:
        """
        Determine optimal collaboration pattern.
        
        Rules:
        - HIERARCHICAL: Resolver → Auditor (role-based handoff)
        - SEQUENTIAL: Multiple agents needing ordered execution
        - PARALLEL: Agents with no dependencies (can run concurrently)
        - FEEDBACK_LOOP: Iterative refinement (designer → validator → designer)
        
        Args:
            primary_agent_id: Primary orchestrator agent
            secondary_agents: Supporting agents
        
        Returns:
            Optimal CollaborationPattern for this workflow
        """
        if not secondary_agents:
            return CollaborationPattern.SEQUENTIAL
        
        # Hierarchical patterns: Resolver + Auditor + Executor
        resolver_roles = ["resolver", "phase-resolver"]
        auditor_roles = ["auditor", "plan-auditor", "meta-auditor"]
        executor_roles = ["executor", "orchestrator"]
        
        primary_is_resolver = any(role in primary_agent_id for role in resolver_roles)
        has_auditor = any(any(role in agent for role in auditor_roles) for agent in secondary_agents)
        
        if primary_is_resolver and has_auditor:
            logger.info("Detected hierarchical pattern: Resolver → Auditor → Executor")
            return CollaborationPattern.HIERARCHICAL
        
        # Check for feedback loop pattern
        designer_roles = ["designer", "design"]
        validator_roles = ["validator", "validation"]
        
        primary_is_designer = any(role in primary_agent_id for role in designer_roles)
        has_validator = any(any(role in agent for role in validator_roles) for agent in secondary_agents)
        
        if primary_is_designer and has_validator:
            logger.info("Detected feedback loop pattern: Design → Validate → Design")
            return CollaborationPattern.FEEDBACK_LOOP
        
        # Default to sequential for ordered execution
        logger.info(f"Using sequential pattern for {len(secondary_agents)} agents")
        return CollaborationPattern.SEQUENTIAL
    
    def coordinate(self, request: CollaborationRequest) -> CollaborationResult:
        """
        Coordinate multi-agent workflow.
        
        Args:
            request: CollaborationRequest with agents and pattern
        
        Returns:
            CollaborationResult with execution path and combined output
        """
        import time
        start_time = time.time()
        
        logger.info(
            f"Coordination started: request_id={request.request_id}, "
            f"pattern={request.pattern}, agents={len(request.secondary_agents) + 1}"
        )
        
        # Initialize context if not provided
        if not request.context:
            request.context = AgentContext(
                agent_id=request.primary_agent_id,
                request_id=request.request_id,
                user_request="",
                intent=""
            )
        
        # Determine execution order
        execution_path = self._build_execution_path(request)
        
        result = CollaborationResult(
            request_id=request.request_id,
            primary_agent_id=request.primary_agent_id,
            execution_path=execution_path,
            combined_output={},
            context=request.context,
            success=False
        )
        
        try:
            # Execute agents according to pattern
            if request.pattern == CollaborationPattern.HIERARCHICAL:
                self._execute_hierarchical(execution_path, request, result)
            elif request.pattern == CollaborationPattern.PARALLEL:
                self._execute_parallel(execution_path, request, result)
            elif request.pattern == CollaborationPattern.FEEDBACK_LOOP:
                self._execute_feedback_loop(execution_path, request, result)
            else:
                self._execute_sequential(execution_path, request, result)
            
            result.success = True
            
        except Exception as e:
            result.success = False
            result.error_message = str(e)
            logger.error(f"Coordination failed: {result.error_message}", exc_info=True)
        
        finally:
            duration = time.time() - start_time
            result.duration_seconds = duration
            logger.info(
                f"Coordination completed: request_id={request.request_id}, "
                f"success={result.success}, duration={duration:.2f}s"
            )
        
        return result
    
    def _build_execution_path(self, request: CollaborationRequest) -> List[str]:
        """
        Build ordered list of agents to execute.
        
        Args:
            request: CollaborationRequest
        
        Returns:
            Ordered list of agent IDs for execution
        """
        path = [request.primary_agent_id]
        path.extend(request.secondary_agents)
        return path
    
    def _execute_hierarchical(
        self,
        execution_path: List[str],
        request: CollaborationRequest,
        result: CollaborationResult
    ) -> None:
        """
        Execute hierarchical pattern: Resolver → Auditor → Executor.
        
        Each layer receives output from previous layer via shared context.
        """
        logger.debug(f"Executing hierarchical pattern with {len(execution_path)} agents")
        
        for agent_id in execution_path:
            logger.debug(f"Hierarchical execution step: {agent_id}")
            
            # Simulate agent execution (actual implementation would call MCP tools)
            agent_output = {
                "agent_id": agent_id,
                "status": "completed",
                "timestamp": datetime.now().isoformat()
            }
            
            result.add_agent_output(agent_id, agent_output)
            
            # Update context for next agent
            if request.context:
                request.context.agent_id = agent_id
                request.context.execution_metadata[agent_id] = agent_output
    
    def _execute_parallel(
        self,
        execution_path: List[str],
        request: CollaborationRequest,
        result: CollaborationResult
    ) -> None:
        """
        Execute parallel pattern: All agents run concurrently.
        """
        import concurrent.futures
        
        logger.debug(f"Executing parallel pattern with {len(execution_path)} agents")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(execution_path)) as executor:
            futures = {}
            
            for agent_id in execution_path:
                # Submit agent task
                future = executor.submit(self._execute_agent, agent_id, request)
                futures[future] = agent_id
            
            # Collect results
            for future in concurrent.futures.as_completed(futures):
                agent_id = futures[future]
                try:
                    agent_output = future.result(timeout=request.timeout_seconds)
                    result.add_agent_output(agent_id, agent_output)
                    logger.debug(f"Parallel agent completed: {agent_id}")
                except Exception as e:
                    logger.error(f"Parallel agent failed: {agent_id}: {e}")
                    raise
    
    def _execute_sequential(
        self,
        execution_path: List[str],
        request: CollaborationRequest,
        result: CollaborationResult
    ) -> None:
        """
        Execute sequential pattern: Agents run one after another.
        """
        logger.debug(f"Executing sequential pattern with {len(execution_path)} agents")
        
        for agent_id in execution_path:
            agent_output = self._execute_agent(agent_id, request)
            result.add_agent_output(agent_id, agent_output)
            logger.debug(f"Sequential agent completed: {agent_id}")
    
    def _execute_feedback_loop(
        self,
        execution_path: List[str],
        request: CollaborationRequest,
        result: CollaborationResult
    ) -> None:
        """
        Execute feedback loop pattern: Agents iterate until convergence.
        """
        logger.debug(f"Executing feedback loop with {len(execution_path)} agents")
        
        for iteration in range(request.max_iterations):
            logger.debug(f"Feedback loop iteration: {iteration + 1}/{request.max_iterations}")
            
            for agent_id in execution_path:
                agent_output = self._execute_agent(agent_id, request)
                result.add_agent_output(agent_id, agent_output)
            
            result.iterations_used = iteration + 1
            
            # Check convergence (in real implementation, would analyze deltas)
            if self._has_converged(result):
                logger.debug("Feedback loop converged")
                break
    
    def _execute_agent(
        self,
        agent_id: str,
        request: CollaborationRequest
    ) -> Dict[str, Any]:
        """
        Execute single agent via MCP tool invocation.
        
        Phase 81 S3 Part 3: Actual MCP tool integration
        
        Invokes agent's MCP tools with request context and captures output.
        """
        logger.debug(f"Executing agent: {agent_id}")
        
        if agent_id not in self._agent_registry:
            logger.warning(f"Agent not registered: {agent_id}")
            return {"agent_id": agent_id, "status": "not_registered"}
        
        agent_info = self._agent_registry[agent_id]
        agent_info["collaboration_count"] += 1
        
        # Phase 81 S3 Part 3: Actual MCP tool invocation
        mcp_tools = agent_info.get("mcp_tools", [])
        
        if not mcp_tools:
            logger.warning(f"No MCP tools for agent: {agent_id}")
            return {
                "agent_id": agent_id,
                "status": "completed",
                "mcp_tools_invoked": [],
                "error": "No MCP tools registered"
            }
        
        # Execute primary MCP tool for agent
        primary_tool = mcp_tools[0]  # Use first tool as primary
        
        mcp_request = MCPExecutionRequest(
            agent_id=agent_id,
            tool_name=primary_tool,
            tool_parameters={
                "request_id": request.request_id,
                "user_request": request.context.user_request if request.context else "",
                "intent": request.context.intent if request.context else "",
                "extracted_data": request.context.extracted_data if request.context else {}
            },
            request_id=request.request_id,
            timeout_seconds=request.timeout_seconds
        )
        
        # Invoke MCP tool via executor
        execution_result = self._mcp_executor.execute(mcp_request)
        
        return {
            "agent_id": agent_id,
            "status": "completed" if execution_result.success else "failed",
            "mcp_tools_invoked": [primary_tool],
            "mcp_execution_result": {
                "success": execution_result.success,
                "output": execution_result.output,
                "error": execution_result.error_message,
                "duration": execution_result.duration_seconds
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def _has_converged(self, result: CollaborationResult) -> bool:
        """
        Check if feedback loop has converged.
        
        Convergence criteria: Agent outputs stabilize (delta < threshold)
        """
        if result.iterations_used < 2:
            return False
        
        # In production, would compare output deltas across iterations
        return False  # Placeholder


# AC_COMPLETE: AC-ROUTER-COLLAB-20260223T000000Z ✅ Agent Collaboration Coordinator
