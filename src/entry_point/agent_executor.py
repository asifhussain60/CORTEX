"""
Agent Executor - Executes specific agents based on routing decisions

This module handles the actual execution of specialist agents after
the IntentRouter has determined which agents should handle a request.

Addresses CORTEX-BRAIN-001 incident by ensuring architectural analysis
requests are properly routed to and executed by the ArchitectAgent.
"""

from typing import Dict, Any, Optional
import logging
from datetime import datetime

from src.cortex_agents.base_agent import BaseAgent, AgentRequest, AgentResponse
from src.cortex_agents.agent_types import AgentType
from src.cortex_agents.strategic.architect import ArchitectAgent
from src.cortex_agents.work_planner.agent import WorkPlanner
from src.cortex_agents.health_validator.agent import HealthValidator
from src.cortex_agents.tactical.code_executor import CodeExecutor
from src.agents.feedback_agent import FeedbackAgent
from src.cortex_agents.ado_agent import ADOAgent


class AgentExecutor:
    """
    Executes specific agents based on routing decisions.
    
    This class takes routing decisions from IntentRouter and actually
    instantiates and executes the appropriate specialist agents.
    """
    
    def __init__(self, tier1_api=None, tier2_kg=None, tier3_context=None):
        """Initialize AgentExecutor with tier APIs."""
        self.tier1 = tier1_api
        self.tier2 = tier2_kg
        self.tier3 = tier3_context
        
        self.logger = logging.getLogger(__name__)
        
        # Agent instances cache
        self._agent_cache = {}
        
    def execute_routing_decision(self, routing_decision: Dict[str, Any], request: AgentRequest) -> AgentResponse:
        """
        Execute agents based on routing decision.
        
        Args:
            routing_decision: Decision from IntentRouter
            request: Original user request
            
        Returns:
            AgentResponse from executed agent(s)
        """
        try:
            primary_agent_type = routing_decision['primary_agent']
            secondary_agents = routing_decision.get('secondary_agents', [])
            
            # Execute primary agent
            primary_response = self._execute_agent(primary_agent_type, request)
            
            # Execute secondary agents if any
            secondary_responses = []
            for agent_type in secondary_agents:
                try:
                    secondary_response = self._execute_agent(agent_type, request)
                    secondary_responses.append(secondary_response)
                except Exception as e:
                    self.logger.warning(f"Secondary agent {agent_type} failed: {str(e)}")
            
            # Combine responses if multiple agents executed
            if secondary_responses:
                combined_response = self._combine_responses(primary_response, secondary_responses)
            else:
                combined_response = primary_response
                
            return combined_response
            
        except Exception as e:
            self.logger.error(f"Agent execution failed: {str(e)}")
            return AgentResponse(
                success=False,
                result={},
                message=f"Agent execution failed: {str(e)}",
                agent_name="AgentExecutor",
                error=str(e)
            )
    
    def _execute_agent(self, agent_type: AgentType, request: AgentRequest) -> AgentResponse:
        """
        Execute a specific agent type.
        
        Args:
            agent_type: Type of agent to execute
            request: Agent request
            
        Returns:
            AgentResponse from the agent
        """
        # Get or create agent instance
        agent = self._get_agent_instance(agent_type)
        
        if not agent:
            raise ValueError(f"No agent available for type: {agent_type}")
            
        # Check if agent can handle this request
        if not agent.can_handle(request):
            raise ValueError(f"Agent {agent_type} cannot handle request: {request.user_message}")
        
        # Execute the agent
        self.logger.info(f"Executing agent: {agent_type.name}")
        response = agent.execute(request)
        
        return response
    
    def _get_agent_instance(self, agent_type: AgentType) -> Optional[BaseAgent]:
        """
        Get or create agent instance.
        
        Args:
            agent_type: Type of agent needed
            
        Returns:
            Agent instance or None if not available
        """
        # Check cache first
        if agent_type in self._agent_cache:
            return self._agent_cache[agent_type]
        
        # Create new instance based on type
        agent = None
        
        if agent_type == AgentType.ARCHITECT:
            agent = ArchitectAgent(
                name="Architect",
                tier1_api=self.tier1,
                tier2_kg=self.tier2,
                tier3_context=self.tier3
            )
        elif agent_type == AgentType.EXECUTOR:
            agent = CodeExecutor(
                name="CodeExecutor",
                tier1_api=self.tier1,
                tier2_kg=self.tier2,
                tier3_context=self.tier3
            )
        elif agent_type == AgentType.PLANNER:
            agent = WorkPlanner(
                name="WorkPlanner",
                tier1_api=self.tier1,
                tier2_kg=self.tier2,
                tier3_context=self.tier3
            )
        elif agent_type == AgentType.VALIDATOR:
            agent = HealthValidator(
                name="HealthValidator",
                tier1_api=self.tier1,
                tier2_kg=self.tier2,
                tier3_context=self.tier3
            )
        elif agent_type == AgentType.FEEDBACK:
            agent = FeedbackAgent(
                name="FeedbackAgent"
            )
        elif agent_type == AgentType.ADO_ORCHESTRATOR:
            agent = ADOAgent(
                name="ADOAgent",
                tier1_api=self.tier1,
                tier2_kg=self.tier2,
                tier3_context=self.tier3
            )
        # Add other agents as needed
        else:
            self.logger.warning(f"Agent type {agent_type} not implemented yet")
            
        # Cache the instance
        if agent:
            self._agent_cache[agent_type] = agent
            
        return agent
    
    def _combine_responses(self, primary_response: AgentResponse, 
                          secondary_responses: list[AgentResponse]) -> AgentResponse:
        """
        Combine responses from multiple agents.
        
        Args:
            primary_response: Response from primary agent
            secondary_responses: Responses from secondary agents
            
        Returns:
            Combined AgentResponse
        """
        # Start with primary response
        combined_message = primary_response.message
        combined_result = primary_response.result if primary_response.result else {}
        
        # Add secondary responses
        for i, response in enumerate(secondary_responses):
            combined_message += f"\n\n## Secondary Agent {i+1} Results:\n{response.message}"
            
            # Merge results
            if response.result:
                combined_result[f'secondary_agent_{i+1}'] = response.result
        
        # Create combined response
        return AgentResponse(
            success=primary_response.success and all(r.success for r in secondary_responses),
            result=combined_result,
            message=combined_message,
            agent_name="AgentExecutor (Multi-Agent)",
            metadata={
                'primary_agent': primary_response.agent_name,
                'secondary_agents': [r.agent_name for r in secondary_responses],
                'total_agents': 1 + len(secondary_responses)
            }
        )


__all__ = ["AgentExecutor"]