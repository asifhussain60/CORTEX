"""
CORTEX Entry Point - Main request processor and dispatcher.

Handles user requests and routes to appropriate orchestrators.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path

from src.orchestrators.master_orchestrator import MasterOrchestrator
from src.mcp.registry import OrchestratorRegistry
from src.database.planning_state_db import PlanningStateDB


class CortexEntry:
    """
    Main entry point for CORTEX requests.
    
    Coordinates between fast command handling and orchestrator routing.
    """
    
    def __init__(
        self,
        brain_path: Optional[str] = None,
        enable_logging: bool = False,
        project_root: Optional[Path] = None,
        registry_path: Optional[str] = None
    ):
        """
        Initialize CORTEX entry point.
        
        Args:
            brain_path: Path to cortex-brain directory
            enable_logging: Enable verbose logging
            project_root: Project root directory
            registry_path: Path to orchestrator registry JSON
        """
        # Configure logging
        if enable_logging:
            logging.basicConfig(
                level=logging.DEBUG,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        self.logger = logging.getLogger("cortex.entry_point")
        self.project_root = project_root or Path.cwd()
        self.brain_path = Path(brain_path) if brain_path else self.project_root / "cortex-brain"
        
        # Initialize registry
        if not registry_path:
            registry_path = str(self.brain_path / "registry" / "orchestrators.json")
        self.registry = OrchestratorRegistry(registry_path=registry_path)
        
        # Register core orchestrators if registry is empty
        if len(self.registry.list_all(enabled_only=False)) == 0:
            self._register_core_orchestrators()
        
        # Initialize state database
        db_path = str(self.brain_path / "state" / "planning.db")
        self.state_db = PlanningStateDB(db_path=db_path)
        
        # Initialize master orchestrator
        master_config = str(self.brain_path / "config" / "master-orchestrator.yaml")
        self.master_orchestrator = MasterOrchestrator(
            config_path=master_config,
            registry=self.registry,
            state_db=self.state_db
        )
        
        self.logger.info("CortexEntry initialized")
    
    def cleanup(self):
        """Cleanup resources."""
        pass
    
    def setup(self, repo_path: Optional[str] = None, verbose: bool = False) -> Dict[str, Any]:
        """Run setup wizard."""
        return {"success": True, "message": "Setup complete (stub)"}
    
    def process(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None,
        resume_session: bool = False,
        format_type: str = "markdown"
    ) -> str:
        """
        Process user request.
        
        Args:
            user_input: User's request string
            context: Additional context
            resume_session: Whether to resume previous session
            format_type: Output format
        
        Returns:
            Formatted response string
        """
        try:
            # Route and execute via master orchestrator
            result = self.master_orchestrator.handle_request(
                user_input=user_input,
                context=context or {}
            )
            
            return result.message
        
        except Exception as e:
            self.logger.error(f"Error processing request: {e}", exc_info=True)
            return f"[ERROR] {str(e)}"
    
    def _register_core_orchestrators(self):
        """Register core CORTEX orchestrators in registry."""
        from src.mcp.metadata import OrchestratorType, OrchestratorCategory
        
        # Planning v5
        self.registry.register(
            id="planning_v5",
            name="Planning System v5",
            version="5.0.0",
            type=OrchestratorType.AUTONOMOUS,
            category=OrchestratorCategory.PLANNING,
            class_name="PlanningOrchestratorV5",
            module_path="src.orchestrators.planning.planning_orchestrator_v5",
            manifest_path="cortex-brain/manifests/orchestrators/planning-system-5.0-manifest.yaml",
            patterns=[r"^(plan|create a plan|make a plan).*$"],
            capabilities=["planning", "context_discovery", "state_tracking"]
        )
        
        self.logger.info("Registered core orchestrators")
