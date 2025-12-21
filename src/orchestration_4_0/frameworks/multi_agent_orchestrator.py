"""
Multi-Agent Collaboration Orchestrator

Phase 5 Task 5.6: Multi-Agent Framework
Supports sequential chat, group chat, and nested chat patterns.

Author: CORTEX Development Team
Version: 1.0.0
Created: 2025-12-21
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from enum import Enum

from src.orchestration_4_0.base.agent_interface import Agent, AgentContext, ManagerAgent, CoordinatorAgent

logger = logging.getLogger(__name__)


class CollaborationPattern(Enum):
    """Multi-agent collaboration patterns"""
    SEQUENTIAL = "sequential"  # Agent1 → Agent2 → Agent3
    GROUP = "group"           # Parallel agents → Manager synthesis
    NESTED = "nested"         # Hierarchical teams → Coordinator


class MultiAgentOrchestrator:
    """
    Orchestrates multi-agent collaboration with various patterns.
    
    Patterns:
    - Sequential: Pipeline where each agent processes output of previous
    - Group: Multiple agents execute in parallel, manager synthesizes results
    - Nested: Hierarchical teams with coordinator integration
    """
    
    def __init__(self):
        self.pattern = CollaborationPattern.SEQUENTIAL
        self.agents: List[Agent] = []
        self.timeout_seconds = 300
    
    async def execute_sequential(
        self,
        agents: List[Agent],
        initial_context: AgentContext
    ) -> AgentContext:
        """
        Execute agents sequentially: Agent1 → Agent2 → Agent3
        
        Args:
            agents: List of agents to execute in order
            initial_context: Initial context to pass to first agent
            
        Returns:
            Final context after all agents executed
        """
        logger.info(f"🎭 Sequential chat: {len(agents)} agents")
        
        context = initial_context
        
        for agent in agents:
            try:
                logger.info(f"  → {agent.get_name()}")
                context.add_to_history(agent.get_name())
                context = await agent.execute(context)
                
                if context.has_errors():
                    logger.warning(f"  ⚠️ {agent.get_name()} reported errors: {context.errors}")
                    
            except Exception as e:
                error_msg = f"Agent {agent.get_name()} failed: {str(e)}"
                logger.error(f"  ❌ {error_msg}")
                context.add_error(error_msg)
                # Continue to next agent rather than failing entirely
        
        logger.info(f"✅ Sequential chat complete: {len(context.history)} agents executed")
        return context
    
    async def execute_group(
        self,
        agents: List[Agent],
        manager: ManagerAgent,
        initial_context: AgentContext
    ) -> AgentContext:
        """
        Execute agents in parallel, manager synthesizes results.
        
        Args:
            agents: List of agents to execute in parallel
            manager: Manager agent to synthesize results
            initial_context: Initial context to pass to all agents
            
        Returns:
            Synthesized context from manager
        """
        logger.info(f"🎭 Group chat: {len(agents)} parallel agents + manager")
        
        # Execute all agents in parallel
        tasks = []
        for agent in agents:
            # Clone context for each agent (avoid shared state)
            agent_context = AgentContext(
                data=initial_context.data.copy(),
                metadata=initial_context.metadata.copy()
            )
            agent_context.add_to_history(agent.get_name())
            tasks.append(agent.execute(agent_context))
        
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results, handle exceptions
            valid_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"  ❌ {agents[i].get_name()} failed: {str(result)}")
                    error_context = AgentContext()
                    error_context.add_error(f"Agent {agents[i].get_name()} failed: {str(result)}")
                    valid_results.append(error_context)
                else:
                    logger.info(f"  ✅ {agents[i].get_name()} completed")
                    valid_results.append(result)
            
            # Manager synthesizes results
            logger.info(f"  → Manager: {manager.get_name()}")
            final_context = await manager.synthesize(valid_results)
            final_context.add_to_history(manager.get_name())
            
            logger.info(f"✅ Group chat complete: {len(agents)} agents → manager")
            return final_context
            
        except Exception as e:
            logger.error(f"❌ Group chat failed: {str(e)}")
            error_context = AgentContext()
            error_context.add_error(f"Group chat failed: {str(e)}")
            return error_context
    
    async def execute_nested(
        self,
        teams: Dict[str, List[Agent]],
        coordinator: CoordinatorAgent,
        initial_context: AgentContext
    ) -> AgentContext:
        """
        Execute hierarchical teams, coordinator integrates results.
        
        Args:
            teams: Dictionary mapping team_name -> list of agents
            coordinator: Coordinator agent to integrate team results
            initial_context: Initial context to pass to all teams
            
        Returns:
            Coordinated context from coordinator
        """
        logger.info(f"🎭 Nested chat: {len(teams)} teams + coordinator")
        
        # Execute each team sequentially (teams contain sequential agents)
        team_tasks = []
        for team_name, team_agents in teams.items():
            logger.info(f"  Team: {team_name} ({len(team_agents)} agents)")
            team_context = AgentContext(
                data=initial_context.data.copy(),
                metadata=initial_context.metadata.copy()
            )
            team_tasks.append(
                self.execute_sequential(team_agents, team_context)
            )
        
        try:
            team_results_list = await asyncio.gather(*team_tasks, return_exceptions=True)
            
            # Build team results dictionary
            team_results = {}
            for i, (team_name, team_result) in enumerate(zip(teams.keys(), team_results_list)):
                if isinstance(team_result, Exception):
                    logger.error(f"  ❌ Team {team_name} failed: {str(team_result)}")
                    error_context = AgentContext()
                    error_context.add_error(f"Team {team_name} failed: {str(team_result)}")
                    team_results[team_name] = error_context
                else:
                    logger.info(f"  ✅ Team {team_name} completed")
                    team_results[team_name] = team_result
            
            # Coordinator integrates team results
            logger.info(f"  → Coordinator: {coordinator.get_name()}")
            final_context = await coordinator.coordinate(team_results)
            final_context.add_to_history(coordinator.get_name())
            
            logger.info(f"✅ Nested chat complete: {len(teams)} teams → coordinator")
            return final_context
            
        except Exception as e:
            logger.error(f"❌ Nested chat failed: {str(e)}")
            error_context = AgentContext()
            error_context.add_error(f"Nested chat failed: {str(e)}")
            return error_context
