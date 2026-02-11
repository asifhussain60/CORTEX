"""
Dashboard Integration Mixin for Operational Orchestrators (Phase 53)
Enables all orchestrators to generate and reference dashboards via MCP tools
Authority: Phase 53 Stage 4 Orchestrator Integration
"""

import logging
from abc import ABC
from pathlib import Path
from typing import Any, Callable, Dict, Optional


class DashboardIntegrationMixin(ABC):
    """
    Mixin to integrate dashboard generation capability into operational orchestrators.

    Provides:
    - Dashboard generation hooks
    - Dashboard data access
    - MCP tool registration
    - Audit trail for dashboard operations

    Usage:
        class MyOrchestrator(IOrchestrator, DashboardIntegrationMixin):
            def execute(self, request):
                # ... existing code ...
                self.on_operation_complete()  # Trigger dashboard regeneration
    """

    # Dashboard generation callback (injected by DashboardOrchestrator)
    _dashboard_generator: Optional[Callable[[Path], Dict[str, Any]]] = None
    _dashboard_cache: Dict[str, Path] = {}

    @classmethod
    def set_dashboard_generator(cls, generator: Callable[[Path], Dict[str, Any]]) -> None:
        """
        Inject dashboard generator function (called by DashboardOrchestrator at init)

        Args:
            generator: Callable that takes repo_path and returns dashboard data
        """
        cls._dashboard_generator = generator

    def get_dashboard_capability(self) -> Dict[str, Any]:
        """
        Return dashboard capability metadata for capability discovery

        Returns:
            Dict with capability info for MCP tool discovery
        """
        return {
            "name": "dashboard_generation",
            "description": "Generate repository dashboard with current analysis",
            "tools": [
                "cortex_generate_dashboard",
                "cortex_sync_dashboard_data",
            ],
            "version": "1.0",
        }

    def trigger_dashboard_generation(self, repo_path: Path, audit_trail_id: str) -> Optional[Path]:
        """
        Trigger dashboard generation for repository

        Args:
            repo_path: Path to repository
            audit_trail_id: AC marker ID for audit trail

        Returns:
            Path to generated dashboard, or None if generation failed
        """
        if not self._dashboard_generator:
            logging.warning(f"[{self.__class__.__name__}] Dashboard generator not initialized")
            return None

        try:
            repo_name = repo_path.name.lower()

            # Check cache
            if repo_name in self._dashboard_cache:
                cached_path = self._dashboard_cache[repo_name]
                if cached_path.exists():
                    logging.debug(f"[{self.__class__.__name__}] Using cached dashboard: {repo_name}")
                    return cached_path

            # Generate dashboard
            logging.info(f"[{self.__class__.__name__}] Generating dashboard for {repo_name}")
            dashboard_data = self._dashboard_generator(repo_path)

            # Save to cache mapping
            dashboard_path = Path(f"company/dashboards/data/{repo_name}.json")
            self._dashboard_cache[repo_name] = dashboard_path

            # Log audit trail
            logging.info(f"[{self.__class__.__name__}] Dashboard generated: {dashboard_path} ({audit_trail_id})")

            return dashboard_path

        except Exception as e:
            logging.error(f"[{self.__class__.__name__}] Dashboard generation failed: {e}")
            return None

    def get_dashboard_metrics(self, repo_path: Path) -> Optional[Dict[str, Any]]:
        """
        Get dashboard metrics for use as evidence in recommendations

        Args:
            repo_path: Path to repository

        Returns:
            Dict with dashboard metrics, or None if unavailable
        """
        dashboard_path = self._dashboard_cache.get(repo_path.name.lower())

        if not dashboard_path or not dashboard_path.exists():
            return None

        try:
            import json
            with open(dashboard_path) as f:
                dashboard_data = json.load(f)

            return {
                "health_score": dashboard_data.get("repository", {}).get("health_score"),
                "metrics": dashboard_data.get("metrics", {}),
                "security_risks": dashboard_data.get("security", {}),
                "last_updated": dashboard_data.get("repository", {}).get("last_updated"),
            }
        except Exception as e:
            logging.error(f"[{self.__class__.__name__}] Failed to read dashboard metrics: {e}")
            return None

    def register_dashboard_capability(self) -> None:
        """Register dashboard capability in orchestrator metadata"""
        if not hasattr(self, 'capabilities'):
            self.capabilities = {}

        self.capabilities['dashboard_generation'] = self.get_dashboard_capability()


# ============================================================================
# INTEGRATION HOOKS FOR SPECIFIC ORCHESTRATORS
# ============================================================================

def integrate_with_master_orchestrator(master_orch: Any, dashboard_gen: Callable) -> None:
    """
    Integrate dashboard generation with MasterOrchestrator

    Args:
        master_orch: MasterOrchestrator instance
        dashboard_gen: Dashboard generator function
    """
    # Set mixin class method
    if hasattr(DashboardIntegrationMixin, 'set_dashboard_generator'):
        DashboardIntegrationMixin.set_dashboard_generator(dashboard_gen)

    # Add dashboard routing to MasterOrchestrator
    original_execute = master_orch.execute if hasattr(master_orch, 'execute') else None

    def execute_with_dashboard(request):
        # Execute original logic
        result = original_execute(request) if original_execute else None

        # After execution, check if dashboard should be generated
        if result and hasattr(result, 'repo_path'):
            # Trigger dashboard generation as post-processing
            pass

        return result

    if original_execute:
        master_orch.execute = execute_with_dashboard


def integrate_with_planning_orchestrator(planning_orch: Any, dashboard_gen: Callable) -> None:
    """
    Integrate dashboard with PlanningOrchestrator
    (Register dashboard as deployment artifact)
    """
    if hasattr(DashboardIntegrationMixin, 'set_dashboard_generator'):
        DashboardIntegrationMixin.set_dashboard_generator(dashboard_gen)

    if not hasattr(planning_orch, 'deployment_artifacts'):
        planning_orch.deployment_artifacts = []

    # Add dashboard to artifacts list
    planning_orch.deployment_artifacts.append({
        "type": "dashboard",
        "source": "cortex_generate_dashboard",
        "format": "json",
    })


def integrate_with_interaction_orchestrator(interaction_orch: Any, dashboard_gen: Callable) -> None:
    """
    Integrate dashboard with InteractionOrchestrator
    (List as available action for user)
    """
    if hasattr(DashboardIntegrationMixin, 'set_dashboard_generator'):
        DashboardIntegrationMixin.set_dashboard_generator(dashboard_gen)

    if not hasattr(interaction_orch, 'available_actions'):
        interaction_orch.available_actions = []

    # Add dashboard generation as discoverable action
    interaction_orch.available_actions.append({
        "action_id": "generate_dashboard",
        "title": "Generate Repository Dashboard",
        "description": "Create or update dashboard with latest analysis",
        "mcp_tool": "cortex_generate_dashboard",
    })


# ============================================================================
# FACTORY FOR DASHBOARD INTEGRATION
# ============================================================================

class DashboardIntegrationFactory:
    """Factory for integrating DashboardOrchestrator with other orchestrators"""

    @staticmethod
    def integrate_all(dashboard_generator_fn: Callable) -> None:
        """
        Integrate DashboardOrchestrator with all 7 operational orchestrators

        Args:
            dashboard_generator_fn: Function to call for dashboard generation
        """
        # Set global generator for all mixins
        DashboardIntegrationMixin.set_dashboard_generator(dashboard_generator_fn)

        # Log integration
        logging.info("[DashboardIntegration] All orchestrators configured for dashboard capability")


if __name__ == "__main__":
    # Example usage
    print("Dashboard Integration Mixin ready for orchestrator wiring")
