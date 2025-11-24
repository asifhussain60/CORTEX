"""
Application Onboarding Operation

Handles the "onboard this application" natural language trigger.
Deploys CORTEX to target applications with intelligent codebase discovery,
documentation generation, and contextual questioning capabilities.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import uuid
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path
import logging

from .base_operation_module import BaseOperationModule, OperationModuleMetadata, OperationPhase, OperationResult, OperationStatus
from ..epm.onboarding_orchestrator import OnboardingOrchestrator, OnboardingProfile, OnboardingSession
from ..epm.step_registry import StepRegistry
from .modules.application_onboarding_steps import register_application_onboarding_steps

logger = logging.getLogger(__name__)


class ApplicationOnboardingOperation(BaseOperationModule):
    """
    Application onboarding operation that leverages the EPM framework.
    
    Natural language triggers:
    - "onboard this application"
    - "analyze my codebase"
    - "setup cortex for this project"
    - "what can cortex learn about this app"
    - "initialize cortex here"
    - "deploy cortex"
    - "onboard app"
    - "application onboarding"
    """
    
    def __init__(self):
        super().__init__()
        self.orchestrator = None
        self.step_registry = StepRegistry()
        self.current_session = None
        
        # Register all application onboarding steps
        register_application_onboarding_steps(self.step_registry)
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Get operation metadata"""
        return OperationModuleMetadata(
            module_id="application_onboarding",
            name="Application Onboarding",
            description="Deploy CORTEX to applications with intelligent discovery",
            phase=OperationPhase.PROCESSING,
            priority=10,
            version="1.0",
            author="Asif Hussain"
        )
    
    def execute(self, request: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute application onboarding operation.
        
        Args:
            request: Natural language request (e.g., "onboard this application")
            context: Additional context including profile preference and project root
            
        Returns:
            Dict with onboarding results and session information
        """
        try:
            # Initialize context if not provided
            if context is None:
                context = {}
            
            # Get project root from context or use current directory
            project_root = context.get('project_root', Path.cwd())
            context['project_root'] = project_root
            
            # Detect onboarding profile from request or default to standard
            profile = self._detect_onboarding_profile(request, context)
            
            # Create onboarding session
            session_id = str(uuid.uuid4())
            session = OnboardingSession(
                session_id=session_id,
                profile=profile,
                start_time=datetime.now(),
                context=context.copy(),
                metadata={
                    "request": request,
                    "auto_detected_profile": profile.value,
                    "cortex_version": "3.0",
                    "operation_type": "application_onboarding",
                    "project_root": str(project_root)
                }
            )
            
            self.current_session = session
            
            # Initialize orchestrator
            self.orchestrator = OnboardingOrchestrator(
                step_registry=self.step_registry,
                session=session
            )
            
            # Execute onboarding flow
            results = self.orchestrator.execute_onboarding_flow(profile)
            
            # Compile final results
            return {
                "success": results.get("success", False),
                "session_id": session_id,
                "profile": profile.value,
                "project_root": str(project_root),
                "onboarding_results": results,
                "session_summary": self._generate_session_summary(session, results),
                "next_steps": self._generate_next_steps(results),
                "discovery_reports": self._extract_discovery_reports(results),
                "metadata": {
                    "operation": "application_onboarding",
                    "execution_time": datetime.now().isoformat(),
                    "epm_integration": True,
                    "step_count": len(results.get("step_results", {})),
                    "crawlers_executed": self._count_crawlers_executed(results)
                }
            }
            
        except Exception as e:
            logger.error(f"Application onboarding operation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": "application_onboarding_execution_error",
                "recovery_suggestions": [
                    "Check project directory permissions",
                    "Verify CORTEX installation with 'cortex status'",
                    "Try quick onboarding profile: 'onboard this app quick'",
                    "Ensure project has valid structure (source files, git repo, etc.)"
                ],
                "metadata": {
                    "operation": "application_onboarding",
                    "execution_time": datetime.now().isoformat(),
                    "error_captured": True
                }
            }
    
    def _detect_onboarding_profile(self, request: str, context: Dict[str, Any]) -> OnboardingProfile:
        """
        Detect appropriate onboarding profile from request and context.
        
        Returns:
            OnboardingProfile enum value
        """
        request_lower = request.lower()
        
        # Check for explicit profile requests
        if "quick" in request_lower or "fast" in request_lower or "minimal" in request_lower:
            return OnboardingProfile.QUICK
        elif "comprehensive" in request_lower or "complete" in request_lower or "full" in request_lower:
            return OnboardingProfile.COMPREHENSIVE
        elif "detailed" in request_lower or "thorough" in request_lower or "deep" in request_lower:
            return OnboardingProfile.COMPREHENSIVE
        
        # Check context for profile preferences
        if context.get("onboarding_profile"):
            profile_map = {
                "quick": OnboardingProfile.QUICK,
                "standard": OnboardingProfile.STANDARD,
                "comprehensive": OnboardingProfile.COMPREHENSIVE
            }
            return profile_map.get(context["onboarding_profile"], OnboardingProfile.STANDARD)
        
        # Default to standard
        return OnboardingProfile.STANDARD
    
    def _generate_session_summary(self, session: OnboardingSession, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive session summary"""
        step_results = results.get("step_results", {})
        
        return {
            "session_id": session.session_id,
            "profile": session.profile.value,
            "duration": self._calculate_session_duration(session),
            "total_steps": len(step_results),
            "successful_steps": sum(1 for r in step_results.values() if r.get("success")),
            "failed_steps": sum(1 for r in step_results.values() if not r.get("success")),
            "key_achievements": self._extract_key_achievements(step_results),
            "crawlers_run": self._extract_crawlers_run(step_results),
            "documentation_generated": self._extract_documentation_generated(step_results),
            "completion_timestamp": datetime.now().isoformat()
        }
    
    def _calculate_session_duration(self, session: OnboardingSession) -> str:
        """Calculate human-readable session duration"""
        duration = datetime.now() - session.start_time
        minutes = int(duration.total_seconds() / 60)
        seconds = int(duration.total_seconds() % 60)
        return f"{minutes}m {seconds}s"
    
    def _extract_key_achievements(self, step_results: Dict[str, Any]) -> List[str]:
        """Extract key achievements from step results"""
        achievements = []
        
        for step_id, result in step_results.items():
            if result.get("success"):
                # Extract achievements from result data
                data = result.get("data", {})
                if "achievement" in data:
                    achievements.append(data["achievement"])
                elif "summary" in data:
                    achievements.append(data["summary"])
        
        return achievements
    
    def _extract_crawlers_run(self, step_results: Dict[str, Any]) -> List[str]:
        """Extract list of crawlers that were executed"""
        crawlers = []
        
        # Look for the crawl_application step
        if "crawl_application" in step_results:
            crawler_data = step_results["crawl_application"].get("data", {})
            crawlers = crawler_data.get("crawlers_executed", [])
        
        return crawlers
    
    def _extract_documentation_generated(self, step_results: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extract list of generated documentation files"""
        docs = []
        
        # Look for documentation generation steps
        for step_id, result in step_results.items():
            if "generate" in step_id or "document" in step_id:
                data = result.get("data", {})
                if "documentation_files" in data:
                    docs.extend(data["documentation_files"])
        
        return docs
    
    def _generate_next_steps(self, results: Dict[str, Any]) -> List[str]:
        """Generate contextual next steps based on results"""
        next_steps = [
            "Review generated documentation in cortex-brain/discovery-reports/",
            "Explore the application analysis and tech stack insights",
            "Ask CORTEX questions about your codebase: 'What patterns did you find?'"
        ]
        
        # Add context-specific suggestions
        if results.get("success"):
            next_steps.append("Use 'plan a feature' to leverage CORTEX's understanding of your app")
            next_steps.append("Try 'help' to see all available CORTEX operations")
        
        return next_steps
    
    def _extract_discovery_reports(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract discovery report information"""
        reports = []
        
        step_results = results.get("step_results", {})
        if "crawl_application" in step_results:
            crawler_data = step_results["crawl_application"].get("data", {})
            reports = crawler_data.get("discovery_reports", [])
        
        return reports
    
    def _count_crawlers_executed(self, results: Dict[str, Any]) -> int:
        """Count number of crawlers successfully executed"""
        step_results = results.get("step_results", {})
        if "crawl_application" in step_results:
            crawler_data = step_results["crawl_application"].get("data", {})
            return len(crawler_data.get("crawlers_executed", []))
        return 0


def create_application_onboarding_operation() -> ApplicationOnboardingOperation:
    """Factory function to create application onboarding operation instance"""
    return ApplicationOnboardingOperation()


# Export for use in operations system
__all__ = ["ApplicationOnboardingOperation", "create_application_onboarding_operation"]
