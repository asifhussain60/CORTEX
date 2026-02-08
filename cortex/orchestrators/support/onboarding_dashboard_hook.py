"""
CORTEX Phase-28 S5: Dashboard Auto-Generation Hook

Post-onboarding trigger to automatically generate dashboard for newly onboarded repositories.
Closes the integration gap between repository profiling (Phase-28) and dashboard generation (Phase-53).

AC_START: AC-PHASE28-S5-001
Description: Dashboard auto-generation hook infrastructure
Author: CORTEX Implementation
"""

from typing import Optional, Callable, Any, Dict
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class HookEventType(Enum):
    """Event types that trigger dashboard generation"""
    PROFILE_CREATED = "profile_created"
    PROFILE_UPDATED = "profile_updated"
    ONBOARDING_COMPLETE = "onboarding_complete"


@dataclass
class ProfileCreatedEvent:
    """Event fired when repository profile is successfully created"""
    repo_name: str
    profile_path: str
    timestamp: datetime
    profile_data: Dict[str, Any]
    
    def __post_init__(self):
        """Validate event data"""
        if not self.repo_name:
            raise ValueError("repo_name is required")
        if not self.profile_path:
            raise ValueError("profile_path is required")
        if not self.profile_data:
            raise ValueError("profile_data is required")


class OnboardingDashboardHook:
    """
    Post-profile hook that triggers dashboard generation immediately after 
    repository profile is created.
    
    Provides:
    - Event-driven architecture for dashboard generation
    - Error isolation (profile retained even if dashboard fails)
    - Configurable enable/disable
    - Audit trail via AC markers
    - Graceful degradation on generation failure
    """
    
    def __init__(
        self,
        dashboard_orchestrator: Optional[Any] = None,
        enabled: bool = True,
        auto_retry_on_failure: bool = True,
        max_retries: int = 3
    ):
        """
        Initialize dashboard hook.
        
        Args:
            dashboard_orchestrator: DashboardOrchestrator instance (lazy-loaded if None)
            enabled: Whether to trigger dashboard generation (default: True)
            auto_retry_on_failure: Whether to retry on transient failures
            max_retries: Maximum retry attempts
        """
        self.dashboard_orchestrator = dashboard_orchestrator
        self.enabled = enabled
        self.auto_retry_on_failure = auto_retry_on_failure
        self.max_retries = max_retries
        self._event_handlers: Dict[HookEventType, list] = {
            HookEventType.PROFILE_CREATED: [],
            HookEventType.PROFILE_UPDATED: [],
            HookEventType.ONBOARDING_COMPLETE: []
        }
    
    def register_handler(
        self,
        event_type: HookEventType,
        handler: Callable[[ProfileCreatedEvent], None]
    ) -> None:
        """Register a custom event handler for dashboard generation events"""
        self._event_handlers[event_type].append(handler)
        logger.debug(f"Registered handler for {event_type.value}")
    
    def on_profile_created(self, event: ProfileCreatedEvent) -> Dict[str, Any]:
        """
        Called when repository profile is successfully created.
        
        Triggers dashboard generation via configured orchestrator.
        
        Args:
            event: ProfileCreatedEvent with repo metadata
            
        Returns:
            Dict with generation status and result
            {
                "status": "success" | "failed" | "skipped",
                "dashboard_path": "/path/to/dashboard.json" if success,
                "error": "Error message" if failed,
                "audit_trail": ["AC markers"]
            }
        """
        audit_trail = []
        
        try:
            # Log start
            audit_trail.append(f"AC_START: AC-PHASE28-S5-HK001-{event.repo_name}")
            logger.info(f"Dashboard hook triggered for {event.repo_name}")
            
            # Check if enabled
            if not self.enabled:
                logger.info(f"Dashboard hook disabled, skipping dashboard generation")
                audit_trail.append(f"Dashboard generation skipped (hook disabled)")
                return {
                    "status": "skipped",
                    "reason": "hook_disabled",
                    "audit_trail": audit_trail
                }
            
            # Fire event handlers
            for handler in self._event_handlers[HookEventType.PROFILE_CREATED]:
                try:
                    handler(event)
                except Exception as e:
                    logger.warning(f"Event handler failed: {e}")
                    audit_trail.append(f"Warning: Handler failed - {str(e)}")
            
            # Generate dashboard via orchestrator
            dashboard_result = self._generate_dashboard(event, audit_trail)
            
            if dashboard_result["status"] == "success":
                logger.info(
                    f"Dashboard generated successfully: "
                    f"{dashboard_result['dashboard_path']}"
                )
                audit_trail.append(
                    f"AC_COMPLETE: AC-PHASE28-S5-HK001-{event.repo_name} ✅"
                )
                return {
                    "status": "success",
                    "dashboard_path": dashboard_result["dashboard_path"],
                    "audit_trail": audit_trail
                }
            else:
                # Generation failed but profile is safe
                logger.warning(
                    f"Dashboard generation failed: {dashboard_result.get('error')}"
                )
                audit_trail.append(
                    f"Dashboard generation failed: {dashboard_result.get('error')}"
                )
                audit_trail.append(
                    f"Profile retained (deletion safe): {event.profile_path}"
                )
                return {
                    "status": "failed",
                    "error": dashboard_result.get("error"),
                    "profile_retained": True,
                    "audit_trail": audit_trail
                }
        
        except Exception as e:
            logger.error(f"Hook error: {e}", exc_info=True)
            audit_trail.append(f"Hook error: {str(e)}")
            return {
                "status": "failed",
                "error": str(e),
                "profile_retained": True,
                "audit_trail": audit_trail
            }
    
    def _generate_dashboard(
        self,
        event: ProfileCreatedEvent,
        audit_trail: list
    ) -> Dict[str, Any]:
        """
        Internal: Generate dashboard via orchestrator with retry logic.
        
        Args:
            event: Profile created event
            audit_trail: Running audit trail
            
        Returns:
            Generation result
        """
        if self.dashboard_orchestrator is None:
            return {
                "status": "failed",
                "error": "Dashboard orchestrator not configured"
            }
        
        retry_count = 0
        last_error = None
        
        while retry_count <= self.max_retries:
            try:
                # Call dashboard orchestrator
                result = self.dashboard_orchestrator.generate_from_profile(
                    repo_name=event.repo_name,
                    profile_data=event.profile_data,
                    profile_path=event.profile_path
                )
                
                if result.get("status") == "success":
                    audit_trail.append(
                        f"Dashboard generated: {result.get('dashboard_path')}"
                    )
                    return result
                else:
                    last_error = result.get("error", "Unknown error")
                    if not self.auto_retry_on_failure or retry_count >= self.max_retries:
                        return result
                    
                    retry_count += 1
                    logger.warning(
                        f"Dashboard generation retry {retry_count}/{self.max_retries}: "
                        f"{last_error}"
                    )
                    audit_trail.append(
                        f"Retry {retry_count}: {last_error}"
                    )
            
            except Exception as e:
                last_error = str(e)
                if not self.auto_retry_on_failure or retry_count >= self.max_retries:
                    return {
                        "status": "failed",
                        "error": last_error
                    }
                
                retry_count += 1
                logger.warning(
                    f"Dashboard generation exception retry {retry_count}/{self.max_retries}: "
                    f"{last_error}"
                )
                audit_trail.append(f"Exception retry {retry_count}: {last_error}")
        
        # All retries exhausted
        return {
            "status": "failed",
            "error": f"Dashboard generation failed after {self.max_retries} retries: {last_error}"
        }
    
    def disable(self) -> None:
        """Disable dashboard auto-generation hook"""
        self.enabled = False
        logger.info("Dashboard hook disabled")
    
    def enable(self) -> None:
        """Enable dashboard auto-generation hook"""
        self.enabled = True
        logger.info("Dashboard hook enabled")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current hook status"""
        return {
            "enabled": self.enabled,
            "auto_retry": self.auto_retry_on_failure,
            "max_retries": self.max_retries,
            "handlers_registered": sum(
                len(handlers) for handlers in self._event_handlers.values()
            )
        }


# AC_COMPLETE: AC-PHASE28-S5-001 ✅
# Dashboard auto-generation hook infrastructure complete
# - OnboardingDashboardHook class implemented
# - Event-driven architecture with handler registration
# - Retry logic with error isolation
# - Audit trail integration
# Ready for integration into RepositoryOnboardingOrchestrator
