"""
Router Agent - Orchestrator Operations Handler

Routes orchestrator-level operations (system maintenance, comprehensive workflows)
to appropriate operation modules.

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
Version: 3.8.1
"""

from typing import Dict, Any, Optional
import logging

from src.cortex_agents.base_agent import BaseAgent, AgentRequest, AgentResponse
from src.cortex_agents.agent_types import AgentType, IntentType

logger = logging.getLogger(__name__)


class RouterAgent(BaseAgent):
    """
    Router agent for orchestrator-level operations.
    
    Handles comprehensive workflows like system maintenance that
    coordinate multiple operations (healthcheck → align → optimize).
    """
    
    def __init__(self, name: str = "RouterAgent", tier1_api=None, tier2_kg=None, tier3_context=None):
        """Initialize router agent."""
        super().__init__(
            name=name,
            tier1_api=tier1_api,
            tier2_kg=tier2_kg,
            tier3_context=tier3_context
        )
        self.agent_type = AgentType.ROUTER
        self.orchestrators = {}
    
    def can_handle(self, request: AgentRequest) -> bool:
        """
        Check if router can handle this request.
        
        Args:
            request: Agent request
            
        Returns:
            True if request is for orchestrator operation
        """
        orchestrator_triggers = [
            'system maintenance',
            'full maintenance',
            'maintain system',
            'run maintenance',
            'comprehensive maintenance'
        ]
        
        message_lower = request.user_message.lower()
        return any(trigger in message_lower for trigger in orchestrator_triggers)
    
    def execute(self, request: AgentRequest) -> AgentResponse:
        """
        Execute orchestrator operation.
        
        Args:
            request: Agent request
            
        Returns:
            AgentResponse with orchestrator results
        """
        message_lower = request.user_message.lower()
        
        try:
            # Route to appropriate orchestrator
            if any(trigger in message_lower for trigger in ['system maintenance', 'full maintenance', 'maintain system']):
                return self._execute_system_maintenance(request)
            else:
                return AgentResponse(
                    success=False,
                    result={},
                    message="Unknown orchestrator operation",
                    agent_name=self.name,
                    error="No matching orchestrator found"
                )
                
        except Exception as e:
            logger.error(f"Router agent execution failed: {e}", exc_info=True)
            return AgentResponse(
                success=False,
                result={},
                message=f"Orchestrator execution failed: {str(e)}",
                agent_name=self.name,
                error=str(e)
            )
    
    def _execute_system_maintenance(self, request: AgentRequest) -> AgentResponse:
        """
        Execute system maintenance orchestrator.
        
        Args:
            request: Agent request
            
        Returns:
            AgentResponse with maintenance results
        """
        try:
            from src.operations.modules.orchestration.system_maintenance_orchestrator import SystemMaintenanceOrchestrator
            
            logger.info("🔧 Executing system maintenance orchestrator")
            
            orchestrator = SystemMaintenanceOrchestrator()
            result = orchestrator.execute({})
            
            # Format response message
            if result.success:
                message = f"✅ {result.message}\n\n"
                message += f"**Phases Completed:** {result.data.get('phases_completed', 0)}/4\n\n"
                
                if result.data.get('improvements'):
                    message += "**Improvements:**\n"
                    for imp in result.data['improvements']:
                        message += f"- {imp}\n"
                    message += "\n"
                
                if result.warnings:
                    message += "**Warnings:**\n"
                    for warn in result.warnings:
                        message += f"- {warn}\n"
                    message += "\n"
                
                if result.data.get('report_path'):
                    message += f"**Report:** `{result.data['report_path']}`"
            else:
                message = f"❌ {result.message}\n\n"
                if result.errors:
                    message += "**Errors:**\n"
                    for err in result.errors:
                        message += f"- {err}\n"
            
            return AgentResponse(
                success=result.success,
                result=result.data,
                message=message,
                agent_name=self.name,
                metadata={
                    'orchestrator': 'system_maintenance',
                    'phases_completed': result.data.get('phases_completed', 0),
                    'duration': result.duration_seconds
                }
            )
            
        except Exception as e:
            logger.error(f"System maintenance execution failed: {e}", exc_info=True)
            return AgentResponse(
                success=False,
                result={},
                message=f"System maintenance failed: {str(e)}",
                agent_name=self.name,
                error=str(e)
            )


__all__ = ["RouterAgent"]
