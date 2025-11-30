"""
Base Agent Module

Provides the base class for all CORTEX agents with common functionality.
"""

import asyncio
import logging
import time
from datetime import datetime
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class AgentMetrics:
    """Metrics for agent performance tracking"""
    execution_count: int = 0
    total_execution_time: float = 0.0
    last_execution_time: Optional[datetime] = None
    success_count: int = 0
    error_count: int = 0
    errors: list = field(default_factory=list)
    
    @property
    def average_execution_time(self) -> float:
        """Calculate average execution time"""
        if self.execution_count == 0:
            return 0.0
        return self.total_execution_time / self.execution_count
    
    @property 
    def success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.execution_count == 0:
            return 0.0
        return (self.success_count / self.execution_count) * 100

class BaseAgent(ABC):
    """
    Base class for all CORTEX agents.
    
    Provides common functionality including:
    - Logging configuration
    - Metrics tracking  
    - Error handling
    - Execution timing
    - Health monitoring
    """
    
    def __init__(self, agent_name: str = None):
        """
        Initialize base agent.
        
        Args:
            agent_name: Name of the agent (defaults to class name)
        """
        self.agent_name = agent_name or self.__class__.__name__
        self.logger = logging.getLogger(f"cortex.agents.{self.agent_name}")
        
        # Initialize metrics
        self.metrics = AgentMetrics()
        
        # Execution tracking
        self.execution_start = None
        self.is_executing = False
        
        self.logger.info(f"Initialized {self.agent_name}")
    
    def _start_execution(self):
        """Mark start of execution for timing"""
        self.execution_start = datetime.now()
        self.is_executing = True
        self.metrics.execution_count += 1
        
    def _end_execution(self, success: bool = True, error: str = None):
        """Mark end of execution and update metrics"""
        if self.execution_start:
            duration = (datetime.now() - self.execution_start).total_seconds()
            self.metrics.total_execution_time += duration
            self.metrics.last_execution_time = datetime.now()
        
        if success:
            self.metrics.success_count += 1
        else:
            self.metrics.error_count += 1
            if error:
                self.metrics.errors.append({
                    "timestamp": datetime.now(),
                    "error": error
                })
        
        self.is_executing = False
    
    async def execute_with_metrics(self, operation_name: str, operation_func, *args, **kwargs):
        """
        Execute an operation with automatic metrics tracking.
        
        Args:
            operation_name: Name of the operation for logging
            operation_func: Function to execute
            *args, **kwargs: Arguments to pass to function
            
        Returns:
            Result of operation function
        """
        self.logger.info(f"Starting {operation_name}")
        self._start_execution()
        
        try:
            if asyncio.iscoroutinefunction(operation_func):
                result = await operation_func(*args, **kwargs)
            else:
                result = operation_func(*args, **kwargs)
            
            self._end_execution(success=True)
            self.logger.info(f"Completed {operation_name} successfully")
            return result
            
        except Exception as e:
            error_msg = f"{operation_name} failed: {str(e)}"
            self.logger.error(error_msg)
            self._end_execution(success=False, error=error_msg)
            raise
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get agent health status.
        
        Returns:
            Dictionary with health information
        """
        return {
            "agent_name": self.agent_name,
            "is_executing": self.is_executing,
            "metrics": {
                "execution_count": self.metrics.execution_count,
                "success_rate": self.metrics.success_rate,
                "average_execution_time": self.metrics.average_execution_time,
                "error_count": self.metrics.error_count,
                "last_execution": self.metrics.last_execution_time.isoformat() if self.metrics.last_execution_time else None
            },
            "status": self._get_agent_status()
        }
    
    def _get_agent_status(self) -> str:
        """Get agent status based on metrics"""
        if self.metrics.execution_count == 0:
            return "ready"
        elif self.is_executing:
            return "executing"
        elif self.metrics.success_rate >= 90:
            return "healthy"
        elif self.metrics.success_rate >= 70:
            return "warning"
        else:
            return "error"
    
    @abstractmethod
    async def process(self, *args, **kwargs):
        """
        Main processing method to be implemented by subclasses.
        
        This is the primary entry point for agent operations.
        """
        pass
    
    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.agent_name})"

class MetricsCollector:
    """Collects and aggregates metrics from multiple agents"""
    
    def __init__(self):
        self.agents = {}
        
    def register_agent(self, agent: BaseAgent):
        """Register an agent for metrics collection"""
        self.agents[agent.agent_name] = agent
        
    def get_aggregate_metrics(self) -> Dict[str, Any]:
        """Get aggregated metrics from all registered agents"""
        total_executions = 0
        total_errors = 0
        total_time = 0.0
        
        agent_statuses = {}
        
        for name, agent in self.agents.items():
            metrics = agent.metrics
            total_executions += metrics.execution_count
            total_errors += metrics.error_count  
            total_time += metrics.total_execution_time
            
            agent_statuses[name] = {
                "status": agent._get_agent_status(),
                "success_rate": metrics.success_rate,
                "execution_count": metrics.execution_count
            }
        
        overall_success_rate = 0.0
        if total_executions > 0:
            overall_success_rate = ((total_executions - total_errors) / total_executions) * 100
        
        return {
            "total_agents": len(self.agents),
            "total_executions": total_executions,
            "total_errors": total_errors,
            "overall_success_rate": overall_success_rate,
            "total_execution_time": total_time,
            "agent_statuses": agent_statuses
        }