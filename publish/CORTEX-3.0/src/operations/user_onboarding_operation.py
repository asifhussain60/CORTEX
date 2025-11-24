"""
User Onboarding Operation

Connects the EPM onboarding orchestrator to the CORTEX operations system.
Handles the "onboard me" natural language trigger and executes the guided onboarding flow.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import uuid
from typing import Dict, Any, List
from datetime import datetime
import logging

from .base_operation_module import BaseOperationModule
from ..epm.onboarding_orchestrator import OnboardingOrchestrator, OnboardingProfile, OnboardingSession
from ..epm.step_registry import StepRegistry
from .modules.user_onboarding_steps import register_user_onboarding_steps

logger = logging.getLogger(__name__)


class UserOnboardingOperation(BaseOperationModule):
    """
    User onboarding operation that leverages the EPM framework.
    
    Natural language triggers:
    - "onboard me"
    - "new user setup"
    - "cortex introduction"
    - "getting started"
    - "help me get started"
    """
    
    def __init__(self):
        self.orchestrator = None
        self.step_registry = StepRegistry()
        self.current_session = None
        
        # Register all user onboarding steps
        register_user_onboarding_steps(self.step_registry)
    
    def execute(self, request: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute user onboarding operation.
        
        Args:
            request: Natural language request (e.g., "onboard me")
            context: Additional context including profile preference
            
        Returns:
            Dict with onboarding results and session information
        """
        try:
            # Initialize context if not provided
            if context is None:
                context = {}
            
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
                    "cortex_version": "2.1",
                    "operation_type": "user_onboarding"
                }
            )
            
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
                "onboarding_results": results,
                "session_summary": self._generate_session_summary(session, results),
                "next_steps": self._generate_next_steps(results),
                "graduation_status": self._check_graduation_status(results),
                "metadata": {
                    "operation": "user_onboarding",
                    "execution_time": datetime.now().isoformat(),
                    "epm_integration": True,
                    "step_count": len(results.get("step_results", {}))
                }
            }
            
        except Exception as e:
            logger.error(f"User onboarding operation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": "onboarding_execution_error",
                "recovery_suggestions": [
                    "Check CORTEX installation with 'cortex status'",
                    "Validate brain structure with 'cortex setup'",
                    "Try quick onboarding profile: 'onboard me quick'"
                ],
                "metadata": {
                    "operation": "user_onboarding",
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
        elif "detailed" in request_lower or "thorough" in request_lower:
            return OnboardingProfile.COMPREHENSIVE
        
        # Check context for profile preferences
        if context.get("onboarding_profile"):
            profile_map = {
                "quick": OnboardingProfile.QUICK,
                "standard": OnboardingProfile.STANDARD,
                "comprehensive": OnboardingProfile.COMPREHENSIVE
            }
            return profile_map.get(context["onboarding_profile"], OnboardingProfile.STANDARD)
        
        # Check for time indicators
        if "5 min" in request_lower or "quick start" in request_lower:
            return OnboardingProfile.QUICK
        elif "30 min" in request_lower or "deep dive" in request_lower:
            return OnboardingProfile.COMPREHENSIVE
        
        # Default to standard
        return OnboardingProfile.STANDARD
    
    def _generate_session_summary(self, session: OnboardingSession, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive session summary"""
        
        step_results = results.get("step_results", {})
        total_steps = len(step_results)
        completed_steps = len([r for r in step_results.values() if r.get("status") == "COMPLETED"])
        failed_steps = len([r for r in step_results.values() if r.get("status") == "FAILED"])
        
        return {
            "session_overview": {
                "profile": session.profile.value,
                "duration": self._calculate_session_duration(session),
                "completion_rate": f"{completed_steps}/{total_steps}",
                "success_rate": f"{(completed_steps/total_steps*100):.1f}%" if total_steps > 0 else "0%"
            },
            "step_breakdown": {
                "total_steps": total_steps,
                "completed": completed_steps,
                "failed": failed_steps,
                "skipped": total_steps - completed_steps - failed_steps
            },
            "key_achievements": self._extract_key_achievements(step_results),
            "environment_detected": results.get("environment_info", {}),
            "memory_enabled": self._check_memory_status(step_results),
            "user_ready": completed_steps >= (total_steps * 0.7)  # 70% completion threshold
        }
    
    def _calculate_session_duration(self, session: OnboardingSession) -> str:
        """Calculate human-readable session duration"""
        if session.end_time:
            duration = session.end_time - session.start_time
            total_seconds = duration.total_seconds()
            minutes = int(total_seconds // 60)
            seconds = int(total_seconds % 60)
            return f"{minutes}m {seconds}s"
        return "ongoing"
    
    def _extract_key_achievements(self, step_results: Dict[str, Any]) -> List[str]:
        """Extract key achievements from step results"""
        achievements = []
        
        for step_id, result in step_results.items():
            if result.get("status") == "COMPLETED":
                if step_id == "present_cortex_introduction":
                    achievements.append("✅ Learned about CORTEX cognitive framework")
                elif step_id == "detect_user_environment":
                    achievements.append("✅ Environment detected and validated")
                elif step_id == "validate_cortex_installation":
                    achievements.append("✅ CORTEX installation verified")
                elif step_id == "demonstrate_memory_capabilities":
                    achievements.append("✅ Experienced persistent memory capabilities")
                elif step_id == "guide_first_interaction":
                    achievements.append("✅ Completed first guided CORTEX interaction")
                elif step_id == "setup_conversation_tracking":
                    achievements.append("✅ Conversation memory tracking enabled")
                elif step_id == "present_graduation_summary":
                    achievements.append("🎓 Successfully graduated from CORTEX onboarding")
        
        return achievements
    
    def _check_memory_status(self, step_results: Dict[str, Any]) -> bool:
        """Check if memory/tracking was successfully set up"""
        tracking_result = step_results.get("setup_conversation_tracking", {})
        return tracking_result.get("status") == "COMPLETED"
    
    def _generate_next_steps(self, results: Dict[str, Any]) -> List[str]:
        """Generate personalized next steps based on onboarding results"""
        next_steps = []
        
        # Always include these fundamental next steps
        next_steps.extend([
            "Try: 'help' - See all available CORTEX operations",
            "Try: 'status' - Check system health",
            "Try: 'plan a feature' - Experience interactive planning"
        ])
        
        # Add conditional next steps based on results
        step_results = results.get("step_results", {})
        
        if step_results.get("demonstrate_memory_capabilities", {}).get("status") == "COMPLETED":
            next_steps.append("Try: 'continue our conversation' tomorrow to test memory")
        
        if step_results.get("validate_cortex_installation", {}).get("status") == "FAILED":
            next_steps.append("Run: 'cortex setup' to fix installation issues")
        
        # Add advanced suggestions
        next_steps.extend([
            "Advanced: 'analyze my codebase' - Intelligent project analysis",
            "Advanced: 'onboard this application' - Deploy CORTEX to other projects",
            "Learning: Read the CORTEX story for deeper understanding"
        ])
        
        return next_steps
    
    def _check_graduation_status(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Determine if user successfully graduated from onboarding"""
        step_results = results.get("step_results", {})
        graduation_step = step_results.get("present_graduation_summary", {})
        
        # Graduation criteria
        core_steps_completed = all(
            step_results.get(step_id, {}).get("status") == "COMPLETED"
            for step_id in ["present_cortex_introduction", "detect_user_environment"]
        )
        
        installation_valid = step_results.get("validate_cortex_installation", {}).get("status") == "COMPLETED"
        graduation_presented = graduation_step.get("status") == "COMPLETED"
        
        return {
            "graduated": graduation_presented and core_steps_completed,
            "ready_for_production": graduation_presented and core_steps_completed and installation_valid,
            "graduation_timestamp": graduation_step.get("data", {}).get("graduation_content", {}).get("graduation_timestamp"),
            "certification_level": self._determine_certification_level(step_results),
            "areas_for_improvement": self._identify_improvement_areas(step_results)
        }
    
    def _determine_certification_level(self, step_results: Dict[str, Any]) -> str:
        """Determine user's CORTEX certification level"""
        completed_steps = [step for step, result in step_results.items() if result.get("status") == "COMPLETED"]
        completion_count = len(completed_steps)
        
        if completion_count >= 6:
            return "CORTEX Expert"
        elif completion_count >= 4:
            return "CORTEX Practitioner" 
        elif completion_count >= 2:
            return "CORTEX Novice"
        else:
            return "CORTEX Beginner"
    
    def _identify_improvement_areas(self, step_results: Dict[str, Any]) -> List[str]:
        """Identify areas where user could improve understanding"""
        improvement_areas = []
        
        if step_results.get("demonstrate_memory_capabilities", {}).get("status") != "COMPLETED":
            improvement_areas.append("Experience memory capabilities in real usage")
        
        if step_results.get("guide_first_interaction", {}).get("status") != "COMPLETED":
            improvement_areas.append("Practice natural language interactions")
        
        if step_results.get("setup_conversation_tracking", {}).get("status") != "COMPLETED":
            improvement_areas.append("Enable conversation tracking for full memory benefits")
        
        return improvement_areas


def create_user_onboarding_operation() -> UserOnboardingOperation:
    """Factory function to create user onboarding operation instance"""
    return UserOnboardingOperation()


# Export for use in operations system
__all__ = ["UserOnboardingOperation", "create_user_onboarding_operation"]