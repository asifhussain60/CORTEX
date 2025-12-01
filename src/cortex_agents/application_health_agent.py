"""
Application Health Agent

Wrapper agent for Application Health Dashboard orchestrator.
Routes application health and onboarding intents to ApplicationHealthOrchestrator.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from typing import Optional
from pathlib import Path

from .base_agent import BaseAgent, AgentRequest, AgentResponse
from .agent_types import IntentType, AgentType


class ApplicationHealthAgent(BaseAgent):
    """
    Agent for handling application health analysis and onboarding.
    
    Routes requests to ApplicationHealthOrchestrator for:
    - Application health dashboard generation
    - Multi-language code analysis
    - Project onboarding and metrics
    - Architecture graph visualization
    
    Features:
    - Progressive crawling (overview/standard/deep)
    - Multi-threaded analysis for performance
    - Language-specific analyzers (Python, C#, JavaScript, ColdFusion)
    - Dependency graph generation
    - Comprehensive HTML report generation
    
    Example:
        agent = ApplicationHealthAgent("ApplicationHealthAgent", tier1_api, tier2_kg, tier3_context)
        
        # Analyze application health
        request = AgentRequest(
            intent=IntentType.APPLICATION_HEALTH,
            context={"project_path": "/path/to/project", "scan_level": "standard"},
            user_message="show health dashboard"
        )
        response = agent.execute(request)
    """
    
    def __init__(self, name: str, tier1_api=None, tier2_kg=None, tier3_context=None):
        """Initialize Application Health Agent with tier APIs."""
        super().__init__(name, tier1_api, tier2_kg, tier3_context)
        
        # Initialize orchestrator lazily (on first use)
        self._health_orchestrator = None
    
    def _get_health_orchestrator(self):
        """Get or create health orchestrator instance."""
        if self._health_orchestrator is None:
            from src.orchestrators.application_health_orchestrator import ApplicationHealthOrchestrator
            self._health_orchestrator = ApplicationHealthOrchestrator()
            self.logger.info("Initialized ApplicationHealthOrchestrator")
        return self._health_orchestrator
    
    def can_handle(self, request: AgentRequest) -> bool:
        """
        Check if this agent can handle the request.
        
        Args:
            request: The agent request
        
        Returns:
            True if intent is application health related
        """
        health_intents = [
            IntentType.APPLICATION_HEALTH,
            IntentType.ONBOARD_APPLICATION
        ]
        
        try:
            # Check if intent matches health operations
            from .agent_types import IntentType
            if isinstance(request.intent, IntentType):
                return request.intent in health_intents
            
            # String comparison fallback
            intent_str = str(request.intent).lower()
            return any(intent_str == health_intent.value for health_intent in health_intents)
        except:
            return False
    
    def execute(self, request: AgentRequest) -> AgentResponse:
        """
        Execute application health analysis based on intent.
        
        Args:
            request: The agent request
        
        Returns:
            AgentResponse with analysis results and formatted report
        """
        self.log_request(request)
        
        try:
            # Get project path from context or use current directory
            project_path = request.context.get("project_path", str(Path.cwd()))
            scan_level = request.context.get("scan_level", "standard")
            
            # Get orchestrator
            orchestrator = self._get_health_orchestrator()
            
            # Execute analysis
            self.logger.info(f"Analyzing application health for: {project_path}")
            analysis_result = orchestrator.analyze(project_path, scan_level)
            
            # Generate report
            report = orchestrator.generate_report(analysis_result)
            
            # Build response
            response = AgentResponse(
                agent_name=self.name,
                success=True,
                result={
                    "analysis": analysis_result,
                    "report": report,
                    "project_path": project_path,
                    "scan_level": scan_level
                },
                message=f"Application health analysis completed. Analyzed {analysis_result['total_files']} files across {len(analysis_result['languages'])} languages.",
                metadata={
                    "intent": request.intent.value if hasattr(request.intent, 'value') else str(request.intent),
                    "agent_type": AgentType.APPLICATION_HEALTH.name,
                    "scan_duration": analysis_result.get("scan_duration", 0),
                    "timestamp": analysis_result.get("timestamp")
                }
            )
            
            self.log_response(response)
            return response
            
        except Exception as e:
            self.logger.error(f"Application health analysis failed: {str(e)}", exc_info=True)
            
            error_response = AgentResponse(
                agent_name=self.name,
                success=False,
                result={},
                message=f"Application health analysis failed: {str(e)}",
                metadata={
                    "intent": request.intent.value if hasattr(request.intent, 'value') else str(request.intent),
                    "agent_type": AgentType.APPLICATION_HEALTH.name,
                    "error": str(e)
                }
            )
            
            self.log_response(error_response)
            return error_response
