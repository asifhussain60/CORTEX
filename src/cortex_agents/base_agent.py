"""
Base Agent Class and Core Data Structures

Provides abstract base class for all CORTEX specialist agents
and standard request/response formats.

PROGRESS MONITORING:
All agents can report progress during long-running operations using the
report_progress() method. Progress monitoring automatically activates if
the operation takes >5 seconds.

Example with Progress Monitoring:
    from src.utils.progress_decorator import with_progress
    
    class MyAgent(BaseAgent):
        def can_handle(self, request: AgentRequest) -> bool:
            return request.intent == "process_files"
        
        @with_progress(operation_name="File Processing")
        def execute(self, request: AgentRequest) -> AgentResponse:
            files = request.context.get('files', [])
            
            for i, file in enumerate(files, 1):
                self.report_progress(i, len(files), f"Processing {file}")
                result = self._process_file(file)
            
            return AgentResponse(success=True, result={"processed": len(files)})
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
import sys

# Import progress monitoring
from src.utils.progress_decorator import with_progress, yield_progress


@dataclass
class AgentRequest:
    """
    Standard request format for all agents.
    
    Attributes:
        intent: The classified user intent (e.g., "plan", "code", "test")
        context: Additional context information (files, settings, etc.)
        user_message: Original user message text
        conversation_id: Optional ID linking to Tier 1 conversation
        priority: Request priority level (default: NORMAL)
        metadata: Additional metadata for the request
    
    Example:
        request = AgentRequest(
            intent="plan",
            context={"feature": "authentication"},
            user_message="Add user authentication"
        )
    """
    intent: str
    context: Dict[str, Any]
    user_message: str
    conversation_id: Optional[str] = None
    priority: int = 3  # NORMAL priority
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class AgentResponse:
    """
    Standard response format for all agents.
    
    Attributes:
        success: Whether the agent executed successfully
        result: The main result/output from the agent
        message: Human-readable message describing the outcome
        metadata: Additional metadata about the execution
        agent_name: Name of the agent that generated this response
        duration_ms: Execution time in milliseconds
        next_actions: Suggested follow-up actions
        error: Optional error message if execution failed
    
    Example:
        response = AgentResponse(
            success=True,
            result={"tasks": ["Create auth model", "Add login route"]},
            message="Feature broken down into 2 tasks",
            agent_name="WorkPlanner"
        )
    """
    success: bool
    result: Any
    message: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    agent_name: str = ""
    duration_ms: float = 0.0
    next_actions: List[str] = field(default_factory=list)
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class AgentMessage:
    """
    Message format for agent-to-agent communication in workflows.
    
    Used for orchestrating multi-agent workflows like TDD cycle.
    
    Attributes:
        from_agent: Name of the sending agent
        to_agent: Name of the receiving agent
        command: Command/action to perform
        payload: Data payload for the command
        correlation_id: Optional ID to correlate related messages
    
    Example:
        message = AgentMessage(
            from_agent="workflow-orchestrator",
            to_agent="test-generator",
            command="create_test",
            payload={"task": "auth", "expect_failure": True}
        )
    """
    from_agent: str
    to_agent: str
    command: str
    payload: Dict[str, Any]
    correlation_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


class BaseAgent(ABC):
    """
    Abstract base class for all CORTEX specialist agents.
    
    All agents must implement:
    - can_handle(): Check if agent can process a request
    - execute(): Perform the agent's primary function
    
    Agents automatically receive:
    - Tier 1 API (conversation/working memory)
    - Tier 2 Knowledge Graph (patterns/learning)
    - Tier 3 Context Intelligence (git/metrics)
    - Logging infrastructure
    
    Example:
        class MyAgent(BaseAgent):
            def can_handle(self, request: AgentRequest) -> bool:
                return request.intent == "my_intent"
            
            def execute(self, request: AgentRequest) -> AgentResponse:
                # Do work
                return AgentResponse(
                    success=True,
                    result=result,
                    message="Work completed"
                )
    """
    
    def __init__(
        self,
        name: str,
        tier1_api=None,
        tier2_kg=None,
        tier3_context=None
    ):
        """
        Initialize the agent.
        
        Args:
            name: Agent name (e.g., "IntentRouter", "WorkPlanner")
            tier1_api: Tier 1 API instance (working memory)
            tier2_kg: Tier 2 Knowledge Graph instance
            tier3_context: Tier 3 Context Intelligence instance
        """
        self.name = name
        self.tier1 = tier1_api
        self.tier2 = tier2_kg
        self.tier3 = tier3_context
        self.logger = self._setup_logging()
    
    def _setup_logging(self) -> logging.Logger:
        """
        Configure agent-specific logging.
        
        Returns:
            Logger instance configured for this agent
        """
        logger = logging.getLogger(f"cortex.agents.{self.name}")
        
        # Only configure if not already configured
        if not logger.handlers:
            logger.setLevel(logging.INFO)
            
            # Console handler
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(logging.INFO)
            
            # Format: [AGENT_NAME] LEVEL: Message
            formatter = logging.Formatter(
                f'[{self.name}] %(levelname)s: %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    @abstractmethod
    def can_handle(self, request: AgentRequest) -> bool:
        """
        Check if this agent can handle the given request.
        
        Args:
            request: The agent request to evaluate
        
        Returns:
            True if agent can handle this request, False otherwise
        
        Example:
            def can_handle(self, request: AgentRequest) -> bool:
                return request.intent in ["plan", "feature"]
        """
        pass
    
    @abstractmethod
    def execute(self, request: AgentRequest) -> AgentResponse:
        """
        Execute the agent's primary function.
        
        Args:
            request: The agent request to process
        
        Returns:
            AgentResponse with results and status
        
        Example:
            def execute(self, request: AgentRequest) -> AgentResponse:
                result = self._do_work(request)
                return AgentResponse(
                    success=True,
                    result=result,
                    message="Work completed successfully"
                )
        """
        pass
    
    def log_request(self, request: AgentRequest):
        """Log incoming request (for debugging/auditing)"""
        self.logger.info(
            f"Received request - Intent: {request.intent}, "
            f"ConversationID: {request.conversation_id}"
        )
    
    def log_response(self, response: AgentResponse):
        """Log outgoing response (for debugging/auditing)"""
        status = "SUCCESS" if response.success else "FAILURE"
        self.logger.info(
            f"Response {status} - Duration: {response.duration_ms:.2f}ms, "
            f"Message: {response.message}"
        )
    
    def _measure_execution(self, func, *args, **kwargs):
        """
        Measure execution time of a function.
        
        Args:
            func: Function to measure
            *args, **kwargs: Arguments to pass to function
        
        Returns:
            Tuple of (result, duration_ms)
        """
        start = datetime.now()
        result = func(*args, **kwargs)
        duration_ms = (datetime.now() - start).total_seconds() * 1000
        return result, duration_ms
    
    def report_progress(self, current: int, total: int, step: str):
        """
        Report progress from within agent execution.
        
        Use this method to provide progress updates during long-running operations.
        Progress monitoring will automatically activate if operation takes >5 seconds.
        
        Args:
            current: Current item index (1-based)
            total: Total items to process
            step: Description of current step
        
        Example:
            def execute(self, request: AgentRequest) -> AgentResponse:
                items = self._get_items(request)
                for i, item in enumerate(items, 1):
                    self.report_progress(i, len(items), f"Processing {item.name}")
                    self._process_item(item)
                return AgentResponse(success=True, result={})
        
        Note:
            Only works when agent's execute() method is decorated with @with_progress.
            If not decorated, this method safely does nothing.
        """
        yield_progress(current, total, step)
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}')>"
