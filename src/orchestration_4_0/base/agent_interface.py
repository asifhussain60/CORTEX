"""
Agent Interface for Multi-Agent Collaboration

Provides abstract agent interface and context for multi-agent patterns.
Part of Phase 5 Package 6: Multi-Agent Collaboration Framework
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class AgentContext:
    """
    Context passed between agents in multi-agent collaboration.
    
    Attributes:
        data: Main data payload exchanged between agents
        metadata: Additional metadata (timestamps, agent history, etc.)
        history: Execution history (agent names in order)
        errors: List of errors encountered during execution
    """
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    history: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    def add_to_history(self, agent_name: str) -> None:
        """Add agent to execution history"""
        self.history.append(agent_name)
        self.metadata[f"{agent_name}_timestamp"] = datetime.now().isoformat()
    
    def add_error(self, error: str) -> None:
        """Add error to context"""
        self.errors.append(error)
    
    def has_errors(self) -> bool:
        """Check if context contains errors"""
        return len(self.errors) > 0
    
    def get_last_agent(self) -> Optional[str]:
        """Get name of last executed agent"""
        return self.history[-1] if self.history else None


class Agent(ABC):
    """
    Abstract agent interface for multi-agent collaboration.
    
    All agents participating in sequential chat, group chat, or nested chat
    must implement this interface.
    """
    
    def __init__(self, name: str):
        """
        Initialize agent.
        
        Args:
            name: Agent name for tracking and debugging
        """
        self.name = name
    
    @abstractmethod
    async def execute(self, context: AgentContext) -> AgentContext:
        """
        Execute agent logic and return updated context.
        
        Args:
            context: Input context from previous agent or initial context
            
        Returns:
            Updated context with agent's contributions
            
        Raises:
            Exception: If agent execution fails
        """
        pass
    
    def get_name(self) -> str:
        """Return agent name for tracking"""
        return self.name


class ManagerAgent(Agent):
    """
    Special agent type for group chat pattern.
    
    Receives results from multiple parallel agents and synthesizes them.
    """
    
    @abstractmethod
    async def synthesize(self, results: List[AgentContext]) -> AgentContext:
        """
        Synthesize results from multiple agents.
        
        Args:
            results: List of contexts from parallel agents
            
        Returns:
            Synthesized context combining all agent results
        """
        pass
    
    async def execute(self, context: AgentContext) -> AgentContext:
        """
        Default execute delegates to synthesize for single context.
        
        Managers typically receive results via synthesize(), but this
        provides fallback for sequential usage.
        """
        return await self.synthesize([context])


class CoordinatorAgent(Agent):
    """
    Special agent type for nested chat pattern.
    
    Receives results from multiple teams and coordinates integration.
    """
    
    @abstractmethod
    async def coordinate(self, team_results: Dict[str, AgentContext]) -> AgentContext:
        """
        Coordinate results from multiple teams.
        
        Args:
            team_results: Dictionary mapping team_name -> team_context
            
        Returns:
            Coordinated context integrating all team results
        """
        pass
    
    async def execute(self, context: AgentContext) -> AgentContext:
        """
        Default execute delegates to coordinate for single context.
        
        Coordinators typically receive results via coordinate(), but this
        provides fallback for sequential usage.
        """
        return await self.coordinate({"default": context})
