"""Health Orchestrator - Coordinates Health Agents

Main orchestrator that coordinates specialized health agents to detect
and report repository health issues. Provides integration with CI/CD,
pre-commit hooks, and MCP tools.

Author: CORTEX Framework
Phase: PHASE-92
CORE Rules: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from .agents.base_agent import BaseHealthAgent, HealthCheckResult
from .reports.health_report import HealthReport, HealthMetrics


class HealthOrchestrator:
    """Main orchestrator for repository health management.
    
    Coordinates multiple health agents to scan the repository for issues,
    generates comprehensive reports, and provides actionable recommendations.
    
    Attributes:
        workspace_root: Root path of workspace to check
        agents: List of registered health agents
        config: Orchestrator configuration
        enabled: Whether orchestrator is enabled
    
    Usage:
        ```python
        orchestrator = HealthOrchestrator(Path("/path/to/repo"))
        
        # Register agents
        orchestrator.register_agent(DuplicateDetectionAgent())
        orchestrator.register_agent(StubDetectionAgent())
        
        # Run health check
        report = orchestrator.run_health_check()
        
        # Get recommendations
        recommendations = report.generate_recommendations()
        ```
    """
    
    def __init__(
        self,
        workspace_root: Path,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize Health Orchestrator.
        
        Args:
            workspace_root: Root path of workspace to check
            config: Optional configuration dictionary
        """
        self.workspace_root = Path(workspace_root)
        self.agents: List[BaseHealthAgent] = []
        self.config = config or {}
        self.enabled = True
        
        if not self.workspace_root.exists():
            raise ValueError(f"Workspace root does not exist: {self.workspace_root}")
    
    def register_agent(self, agent: BaseHealthAgent) -> None:
        """Register a health agent.
        
        Args:
            agent: Health agent instance to register
        """
        self.agents.append(agent)
    
    def unregister_agent(self, agent_name: str) -> bool:
        """Unregister a health agent by name.
        
        Args:
            agent_name: Name of agent to unregister
        
        Returns:
            True if agent was found and removed, False otherwise
        """
        for i, agent in enumerate(self.agents):
            if agent.name == agent_name:
                self.agents.pop(i)
                return True
        return False
    
    def get_agent(self, agent_name: str) -> Optional[BaseHealthAgent]:
        """Get agent by name.
        
        Args:
            agent_name: Name of agent to find
        
        Returns:
            Agent instance or None if not found
        """
        for agent in self.agents:
            if agent.name == agent_name:
                return agent
        return None
    
    def list_agents(self) -> List[str]:
        """List all registered agent names.
        
        Returns:
            List of agent names
        """
        return [agent.name for agent in self.agents]
    
    def run_health_check(
        self,
        agent_names: Optional[List[str]] = None,
    ) -> HealthReport:
        """Run health check with registered agents.
        
        Args:
            agent_names: Optional list of specific agents to run.
                        If None, runs all enabled agents.
        
        Returns:
            HealthReport with aggregated results
        """
        start_time = time.time()
        report = HealthReport(workspace_root=self.workspace_root)
        
        # Determine which agents to run
        agents_to_run = self.agents
        if agent_names:
            agents_to_run = [
                agent for agent in self.agents
                if agent.name in agent_names
            ]
        
        # Run each agent
        for agent in agents_to_run:
            if not agent.is_enabled():
                continue
            
            try:
                result = agent.check(self.workspace_root)
                report.add_agent_result(result)
            except Exception as e:
                # Log error but continue with other agents
                print(f"Error running {agent.name}: {str(e)}")
                # Create error result
                error_result = HealthCheckResult(
                    agent_name=agent.name,
                    issues=[],
                    files_scanned=0,
                    duration_seconds=0.0,
                    metadata={"error": str(e)},
                )
                report.add_agent_result(error_result)
        
        # Generate recommendations
        report.generate_recommendations()
        
        # Update total duration
        report.metadata["total_duration_seconds"] = time.time() - start_time
        
        return report
    
    def run_agent(self, agent_name: str) -> Optional[HealthCheckResult]:
        """Run a specific agent by name.
        
        Args:
            agent_name: Name of agent to run
        
        Returns:
            HealthCheckResult or None if agent not found
        """
        agent = self.get_agent(agent_name)
        if not agent:
            return None
        
        if not agent.is_enabled():
            return None
        
        return agent.check(self.workspace_root)
    
    def enable_agent(self, agent_name: str) -> bool:
        """Enable a specific agent.
        
        Args:
            agent_name: Name of agent to enable
        
        Returns:
            True if agent was found, False otherwise
        """
        agent = self.get_agent(agent_name)
        if agent:
            agent.enable()
            return True
        return False
    
    def disable_agent(self, agent_name: str) -> bool:
        """Disable a specific agent.
        
        Args:
            agent_name: Name of agent to disable
        
        Returns:
            True if agent was found, False otherwise
        """
        agent = self.get_agent(agent_name)
        if agent:
            agent.disable()
            return True
        return False
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of orchestrator state.
        
        Returns:
            Dictionary with orchestrator summary
        """
        return {
            "workspace_root": str(self.workspace_root),
            "agents_registered": len(self.agents),
            "agents_enabled": sum(1 for agent in self.agents if agent.is_enabled()),
            "agent_names": self.list_agents(),
            "enabled": self.enabled,
        }


__all__ = ["HealthOrchestrator"]
