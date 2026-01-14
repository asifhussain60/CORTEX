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
        
        # Health Check v1 (CORTEX Architecture Validation - AC-CORTEX-001)
        self.registry.register(
            id="health_check_v1",
            name="Health Check Orchestrator v1",
            version="1.0.0",
            type=OrchestratorType.AUTONOMOUS,
            category=OrchestratorCategory.VALIDATION,
            class_name="HealthCheckOrchestratorV1",
            module_path="src.orchestrators.health.health_check_orchestrator_v1",
            manifest_path="cortex-brain/manifests/orchestrators/health-check-orchestrator-v1.yaml",
            patterns=[r"^(health check|repair cortex|wiring|diagnose cortex|architecture health).*$"],
            capabilities=["architecture_validation", "database_integrity_check", "registry_validation", "auto_repair", "health_reporting"]
        )
        
        # Epic Review
        self.registry.register(
            id="epic_review",
            name="Epic Review Orchestrator",
            version="1.0.0",
            type=OrchestratorType.AUTONOMOUS,
            category=OrchestratorCategory.VALIDATION,
            class_name="EpicReviewOrchestrator",
            module_path="src.orchestrators.epic_review_orchestrator",
            manifest_path="cortex-brain/manifests/orchestrators/epic-review-orchestrator.yaml",
            patterns=[r"^(epic review|review epic|progress report|cortex status|epic status).*$"],
            capabilities=["health_monitoring", "progress_analysis", "gap_detection", "epic_updates"]
        )
        
        # Planning v5
        self.registry.register(
            id="planning_v5",
            name="Planning System v5",
            version="5.0.0",
            type=OrchestratorType.AUTONOMOUS,
            category=OrchestratorCategory.PLANNING,
            class_name="PlanningOrchestratorV5",
            module_path="src.orchestrators.planning.planning_orchestrator",
            manifest_path="cortex-brain/manifests/orchestrators/planning-system-5.0-manifest.yaml",
            patterns=[r"^(plan|create a plan|make a plan).*$"],
            capabilities=["planning", "context_discovery", "state_tracking"]
        )
        
        # Vacuum v2
        self.registry.register(
            id="vacuum",
            name="Vacuum Orchestrator v2",
            version="2.0.0",
            type=OrchestratorType.AUTONOMOUS,
            category=OrchestratorCategory.MAINTENANCE,
            class_name="VacuumOrchestrator",
            module_path="src.orchestrators.vacuum.vacuum_orchestrator",
            manifest_path="cortex-brain/manifests/orchestrators/vacuum-orchestrator-v2.yaml",
            patterns=[r"^(vacuum|deep clean|organize files).*$"],
            capabilities=["cleanup", "duplicate_detection", "file_organization"]
        )
        
        # Maintenance v2
        self.registry.register(
            id="maintenance_v2",
            name="Maintenance Orchestrator v2",
            version="2.0.0",
            type=OrchestratorType.AUTONOMOUS,
            category=OrchestratorCategory.MAINTENANCE,
            class_name="MaintenanceOrchestratorV2",
            module_path="src.orchestrators.maintenance.maintenance_orchestrator",
            manifest_path="cortex-brain/manifests/orchestrators/maintenance-orchestrator-v2.yaml",
            patterns=[r"^(maintenance|system maintenance|run maintenance).*$"],
            capabilities=["health_monitoring", "dependency_updates", "security_scan", "performance_optimization"]
        )
        
        # ADO v2
        self.registry.register(
            id="ado_v2",
            name="ADO Orchestrator v2",
            version="2.0.0",
            type=OrchestratorType.AUTONOMOUS,
            category=OrchestratorCategory.INTEGRATION,
            class_name="ADOOrchestratorV2",
            module_path="src.orchestrators.ado.ado_orchestrator",
            manifest_path="cortex-brain/manifests/orchestrators/ado-orchestrator-v2.yaml",
            patterns=[r"^(ado|ado story|ado feature|create ado|azure devops).*$"],
            capabilities=["work_item_creation", "user_story_generation", "feature_creation", "epic_linking"]
        )
        
        # Investigation v2
        self.registry.register(
            id="investigation_v2",
            name="Investigation Orchestrator v2",
            version="2.0.0",
            type=OrchestratorType.AUTONOMOUS,
            category=OrchestratorCategory.ANALYSIS,
            class_name="InvestigationOrchestratorV2",
            module_path="src.orchestrators.investigation.investigation_orchestrator",
            manifest_path="cortex-brain/manifests/orchestrators/investigation-orchestrator-v2.yaml",
            patterns=[r"^(investigate|investigation|find root cause|analyze error|debug issue).*$"],
            capabilities=["log_analysis", "error_detection", "dependency_analysis", "root_cause_analysis"]
        )
        
        # Sanitization v2
        self.registry.register(
            id="sanitization_v2",
            name="Sanitization Orchestrator v2",
            version="2.0.0",
            type=OrchestratorType.AUTONOMOUS,
            category=OrchestratorCategory.SECURITY,
            class_name="SanitizationOrchestratorV2",
            module_path="src.orchestrators.sanitization.sanitization_orchestrator",
            manifest_path="cortex-brain/manifests/orchestrators/sanitization-orchestrator-v2.yaml",
            patterns=[r"^(sanitize|sanitization|remove pii|remove secrets|anonymize).*$"],
            capabilities=["pii_removal", "secret_detection", "data_anonymization", "compliance_validation"]
        )
        
        # TODO Orchestrator (DAG-based task management)
        self.registry.register(
            id="todo_orchestrator",
            name="TODO Orchestrator",
            version="6.0.0",
            type=OrchestratorType.AUTONOMOUS,
            category=OrchestratorCategory.WORKFLOW,
            class_name="TodoOrchestrator",
            module_path="src.orchestrators.core.todo_orchestrator",
            manifest_path="cortex-brain/manifests/orchestrators/todo-orchestrator.yaml",
            patterns=[r"^(todo|manage todos|task management|dag|dependencies).*$"],
            capabilities=["dag_management", "dependency_tracking", "task_parallelization", "checkpoint_recovery"]
        )
        
        # TDD-Master Orchestrator (Planning → TDD coordination)
        self.registry.register(
            id="tdd_master",
            name="TDD-Master Orchestrator",
            version="1.0.0",
            type=OrchestratorType.AUTONOMOUS,
            category=OrchestratorCategory.WORKFLOW,
            class_name="TDDMasterOrchestrator",
            module_path="src.orchestrators.tdd_master.tdd_master_orchestrator",
            manifest_path="cortex-brain/manifests/orchestrators/tdd-master-orchestrator-manifest.yaml",
            patterns=[r"^(tdd-master|implement|build|create|fix|refactor|add feature).*$"],
            capabilities=["plan_detection", "context_transformation", "tdd_invocation", "ac_validation", "governance_enforcement", "dashboard_updates", "completion_reports"]
        )
        
        # Gap-Fix Orchestrator (14-phase gap detection and remediation)
        self.registry.register(
            id="gap_fix",
            name="Gap-Fix Orchestrator",
            version="1.0.0",
            type=OrchestratorType.AUTONOMOUS,
            category=OrchestratorCategory.ANALYSIS,
            class_name="GapFixOrchestrator",
            module_path="src.orchestrators.gap_fix.gap_fix_orchestrator",
            manifest_path="cortex-brain/manifests/orchestrators/gap-fix-orchestrator-manifest.yaml",
            patterns=[r"^(gap-fix|gap fix|find gaps|detect gaps|fix gaps|gap detection|gap analysis).*$"],
            capabilities=["gap_detection", "snowball_analysis", "mcp_validation", "plan_alignment", "remediation_planning", "phase_orchestration"]
        )
        
        # Autonomous AC Implementor (Direct AC-ID implementation from progress tracker)
        self.registry.register(
            id="autonomous_ac_implementor",
            name="Autonomous AC Implementor",
            version="1.0.0",
            type=OrchestratorType.AUTONOMOUS,
            category=OrchestratorCategory.WORKFLOW,
            class_name="AutonomousACImplementor",
            module_path="src.orchestrators.autonomous.autonomous_ac_implementor",
            manifest_path="cortex-brain/manifests/orchestrators/autonomous-ac-implementor-manifest.yaml",
            patterns=[r"^(autonomous|implement phase|continue autonomous|carry out|implement plan autonomous).*$"],
            capabilities=["direct_ac_implementation", "progress_tracking", "sequential_execution", "evidence_generation", "blocker_detection", "phase_completion"]
        )
        
        self.logger.info("Registered core orchestrators")
