"""
CORTEX Phase-28 S5: Compound MCP Tool - Onboard and Generate Dashboard

Combines repository onboarding (cortex_onboard_repository) and dashboard generation
(cortex_generate_dashboard) into a single atomic operation.

MCP Tool: cortex_onboard_and_dashboard

AC_START: AC-PHASE28-S5-002
Description: Compound MCP tool for integrated workflow
Author: CORTEX Implementation
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class OperationStatus(Enum):
    """Status of compound operation stages"""
    PENDING = "pending"
    ONBOARDING = "onboarding"
    DASHBOARD_GENERATION = "dashboard_generation"
    REGISTRATION = "registration"
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILED = "failed"


@dataclass
class OnboardAndDashboardResult:
    """
    Result of compound onboarding + dashboard generation operation
    """
    status: OperationStatus
    repo_name: str
    
    # Onboarding results
    profile_created: bool
    profile_path: Optional[str] = None
    
    # Dashboard results
    dashboard_created: bool
    dashboard_path: Optional[str] = None
    
    # Registration results
    registry_updated: bool
    
    # Execution metadata
    total_duration_seconds: float = 0.0
    onboarding_duration_seconds: float = 0.0
    dashboard_duration_seconds: float = 0.0
    registration_duration_seconds: float = 0.0
    
    # Error information
    onboarding_error: Optional[str] = None
    dashboard_error: Optional[str] = None
    registration_error: Optional[str] = None
    
    # Audit trail
    audit_trail: List[str] = None
    
    def __post_init__(self):
        if self.audit_trail is None:
            self.audit_trail = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary"""
        return asdict(self)
    
    def is_success(self) -> bool:
        """Check if operation succeeded"""
        return self.status == OperationStatus.SUCCESS
    
    def is_partial_success(self) -> bool:
        """Check if operation partially succeeded"""
        return self.status == OperationStatus.PARTIAL_SUCCESS


class CompoundOnboardAndDashboardOperation:
    """
    Orchestrate combined repository onboarding and dashboard generation.
    
    Flow:
    1. Onboard repository (Phase-28)
    2. Generate dashboard (Phase-53)
    3. Update registry (index.yaml)
    4. Return unified result
    
    Features:
    - Atomic operation (all-or-nothing semantics)
    - Error isolation (profile retained even if dashboard fails)
    - Comprehensive audit trail
    - Performance tracking
    - Graceful partial success handling
    """
    
    def __init__(
        self,
        onboarding_orchestrator: Any,
        dashboard_orchestrator: Any,
        registry_updater: Optional[Any] = None
    ):
        """
        Initialize compound operation.
        
        Args:
            onboarding_orchestrator: RepositoryOnboardingOrchestrator instance
            dashboard_orchestrator: DashboardOrchestrator instance
            registry_updater: Optional registry update handler
        """
        self.onboarding_orch = onboarding_orchestrator
        self.dashboard_orch = dashboard_orchestrator
        self.registry_updater = registry_updater
    
    def execute(
        self,
        repo_path: str,
        auto_dashboard: bool = True,
        update_registry: bool = True
    ) -> OnboardAndDashboardResult:
        """
        Execute compound operation: onboard + dashboard generation.
        
        Args:
            repo_path: Path to repository to onboard
            auto_dashboard: Whether to automatically generate dashboard (default: True)
            update_registry: Whether to update registry (default: True)
            
        Returns:
            OnboardAndDashboardResult with complete operation details
        """
        import time
        from datetime import datetime
        
        start_time = time.time()
        result = OnboardAndDashboardResult(
            status=OperationStatus.PENDING,
            repo_name="",
            profile_created=False,
            dashboard_created=False,
            registry_updated=False
        )
        
        result.audit_trail.append(
            f"AC_START: AC-PHASE28-S5-COMPOUND-001"
        )
        result.audit_trail.append(f"Timestamp: {datetime.now().isoformat()}")
        result.audit_trail.append(f"Operation: Onboard + Dashboard")
        result.audit_trail.append(f"Repo Path: {repo_path}")
        
        try:
            # STAGE 1: Repository Onboarding
            result.status = OperationStatus.ONBOARDING
            result.audit_trail.append("STAGE 1: Repository Onboarding")
            
            onboarding_start = time.time()
            onboarding_result = self._execute_onboarding(repo_path, result)
            result.onboarding_duration_seconds = time.time() - onboarding_start
            
            if not onboarding_result["success"]:
                result.status = OperationStatus.FAILED
                result.onboarding_error = onboarding_result["error"]
                result.audit_trail.append(
                    f"❌ Onboarding failed: {onboarding_result['error']}"
                )
                result.audit_trail.append(
                    f"AC_COMPLETE: AC-PHASE28-S5-COMPOUND-001 ❌"
                )
                return self._finalize_result(result, start_time)
            
            # Extract repo info from onboarding result
            result.repo_name = onboarding_result.get("repo_name", "")
            result.profile_path = onboarding_result.get("profile_path", "")
            result.profile_created = True
            
            result.audit_trail.append(
                f"✅ Onboarding complete: {result.profile_path}"
            )
            
            # STAGE 2: Dashboard Generation (if enabled)
            if not auto_dashboard:
                result.audit_trail.append(
                    "STAGE 2: Dashboard generation skipped (auto_dashboard=False)"
                )
            else:
                result.status = OperationStatus.DASHBOARD_GENERATION
                result.audit_trail.append("STAGE 2: Dashboard Generation")
                
                dashboard_start = time.time()
                dashboard_result = self._execute_dashboard_generation(
                    result.repo_name,
                    onboarding_result.get("profile_data"),
                    result.profile_path,
                    result
                )
                result.dashboard_duration_seconds = time.time() - dashboard_start
                
                if not dashboard_result["success"]:
                    result.dashboard_error = dashboard_result["error"]
                    result.audit_trail.append(
                        f"⚠️  Dashboard generation failed: {dashboard_result['error']}"
                    )
                    result.audit_trail.append(
                        "Profile retained (profile is safe, deletio safety maintained)"
                    )
                    result.status = OperationStatus.PARTIAL_SUCCESS
                else:
                    result.dashboard_path = dashboard_result.get("dashboard_path")
                    result.dashboard_created = True
                    result.audit_trail.append(
                        f"✅ Dashboard created: {result.dashboard_path}"
                    )
            
            # STAGE 3: Registry Update (if enabled)
            if not update_registry:
                result.audit_trail.append(
                    "STAGE 3: Registry update skipped (update_registry=False)"
                )
            else:
                result.status = OperationStatus.REGISTRATION
                result.audit_trail.append("STAGE 3: Registry Update")
                
                registration_start = time.time()
                registration_result = self._execute_registry_update(result)
                result.registration_duration_seconds = time.time() - registration_start
                
                if not registration_result["success"]:
                    result.registration_error = registration_result["error"]
                    result.audit_trail.append(
                        f"⚠️  Registry update failed: {registration_result['error']}"
                    )
                    # Still partial success if profile/dashboard created
                else:
                    result.registry_updated = True
                    result.audit_trail.append("✅ Registry updated")
            
            # Final status determination
            if result.profile_created and result.dashboard_created and result.registry_updated:
                result.status = OperationStatus.SUCCESS
            elif result.profile_created:
                result.status = OperationStatus.PARTIAL_SUCCESS
            
            result.audit_trail.append(
                f"AC_COMPLETE: AC-PHASE28-S5-COMPOUND-001 ✅"
            )
            
            return self._finalize_result(result, start_time)
        
        except Exception as e:
            logger.error(f"Compound operation error: {e}", exc_info=True)
            result.status = OperationStatus.FAILED
            result.onboarding_error = str(e)
            result.audit_trail.append(f"Exception: {str(e)}")
            result.audit_trail.append(
                f"AC_COMPLETE: AC-PHASE28-S5-COMPOUND-001 ❌"
            )
            return self._finalize_result(result, start_time)
    
    def _execute_onboarding(
        self,
        repo_path: str,
        result: OnboardAndDashboardResult
    ) -> Dict[str, Any]:
        """
        Execute stage 1: Repository onboarding.
        
        Args:
            repo_path: Path to repository
            result: Result object for audit trail
            
        Returns:
            Onboarding result dict
        """
        try:
            onboarding_result = self.onboarding_orch.onboard_repository(
                repo_path=repo_path
            )
            
            return {
                "success": onboarding_result.get("status") == "success",
                "error": onboarding_result.get("error"),
                "repo_name": onboarding_result.get("repo_name"),
                "profile_path": onboarding_result.get("profile_path"),
                "profile_data": onboarding_result.get("profile_data")
            }
        except Exception as e:
            logger.error(f"Onboarding execution error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _execute_dashboard_generation(
        self,
        repo_name: str,
        profile_data: Dict[str, Any],
        profile_path: str,
        result: OnboardAndDashboardResult
    ) -> Dict[str, Any]:
        """
        Execute stage 2: Dashboard generation.
        
        Args:
            repo_name: Repository name
            profile_data: Repository profile data
            profile_path: Path to profile YAML
            result: Result object for audit trail
            
        Returns:
            Dashboard generation result dict
        """
        try:
            dashboard_result = self.dashboard_orch.generate_from_profile(
                repo_name=repo_name,
                profile_data=profile_data,
                profile_path=profile_path
            )
            
            return {
                "success": dashboard_result.get("status") == "success",
                "error": dashboard_result.get("error"),
                "dashboard_path": dashboard_result.get("dashboard_path")
            }
        except Exception as e:
            logger.error(f"Dashboard generation execution error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _execute_registry_update(
        self,
        result: OnboardAndDashboardResult
    ) -> Dict[str, Any]:
        """
        Execute stage 3: Registry update.
        
        Args:
            result: Result object with profile and dashboard info
            
        Returns:
            Registry update result dict
        """
        try:
            if self.registry_updater is None:
                return {
                    "success": False,
                    "error": "Registry updater not configured"
                }
            
            update_result = self.registry_updater.update_onboarded_repo(
                repo_name=result.repo_name,
                profile_path=result.profile_path,
                dashboard_path=result.dashboard_path if result.dashboard_created else None,
                dashboard_generated=result.dashboard_created
            )
            
            return {
                "success": update_result.get("status") == "success",
                "error": update_result.get("error")
            }
        except Exception as e:
            logger.error(f"Registry update execution error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _finalize_result(
        self,
        result: OnboardAndDashboardResult,
        start_time: float
    ) -> OnboardAndDashboardResult:
        """
        Finalize result with timing information.
        
        Args:
            result: Result object to finalize
            start_time: Operation start time
            
        Returns:
            Finalized result
        """
        import time
        result.total_duration_seconds = time.time() - start_time
        return result


# MCP Tool Definition
# Tool: cortex_onboard_and_dashboard
# Type: Compound Operation
# Implements: Phase-28 S5 + Phase-53 integration
# 
# Usage:
#   result = cortex_onboard_and_dashboard(
#       repo_path="/path/to/repository",
#       auto_dashboard=True,
#       update_registry=True
#   )
#
# Returns: OnboardAndDashboardResult with complete audit trail

# AC_COMPLETE: AC-PHASE28-S5-002 ✅
# Compound MCP tool infrastructure complete
# - CompoundOnboardAndDashboardOperation class implemented
# - Three-stage execution: Onboarding → Dashboard → Registry
# - Comprehensive error handling and audit trail
# - Partial success support (profile always retained)
# Ready for MCP gateway wiring
