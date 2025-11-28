"""
Entry Point Scanner - Convention-Based Discovery

Discovers all entry points from response-templates.yaml:
- Parses YAML for all template triggers
- Maps triggers to orchestrators (naming convention)
- Detects orphaned triggers (no orchestrator)
- Detects ghost features (orchestrator but no trigger)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import logging
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class EntryPointScanner:
    """
    Convention-based entry point discovery.
    
    Parses response-templates.yaml to find all user-facing triggers
    and validates they map to actual orchestrators.
    """
    
    def __init__(self, project_root: Path):
        """
        Initialize entry point scanner.
        
        Args:
            project_root: Root directory of CORTEX project
        """
        self.project_root = Path(project_root)
        self.templates_path = self.project_root / "cortex-brain" / "response-templates.yaml"
    
    def discover(self) -> Dict[str, Dict[str, Any]]:
        """
        Discover all entry points from response templates.
        
        Returns:
            Dict mapping trigger to metadata:
            {
                "start tdd": {
                    "template": "tdd_workflow_start",
                    "triggers": ["start tdd", "tdd workflow"],
                    "response_type": "detailed",
                    "expected_orchestrator": "TDDWorkflowOrchestrator",
                    "status": "wired"  # or "orphaned"
                }
            }
        """
        if not self.templates_path.exists():
            logger.warning(f"Templates file not found: {self.templates_path}")
            return {}
        
        try:
            with open(self.templates_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            
            templates = data.get("templates", {})
            entry_points = {}
            
            for template_name, template_data in templates.items():
                triggers = template_data.get("triggers", [])
                # Use explicit expected_orchestrator from YAML if available, otherwise infer
                yaml_orchestrator = template_data.get("expected_orchestrator")
                
                for trigger in triggers:
                    # Prefer explicit YAML mapping over inference
                    if yaml_orchestrator:
                        expected_orchestrator = yaml_orchestrator
                    else:
                        # Fall back to inference for backward compatibility
                        expected_orchestrator = self._infer_orchestrator(trigger, template_name)
                    
                    entry_points[trigger] = {
                        "template": template_name,
                        "triggers": triggers,
                        "response_type": template_data.get("response_type", "detailed"),
                        "expected_orchestrator": expected_orchestrator,
                        "status": "unknown"  # Will be validated later
                    }
            
            logger.info(f"Discovered {len(entry_points)} entry point triggers")
            return entry_points
        
        except Exception as e:
            logger.error(f"Failed to parse templates: {e}")
            return {}
    
    def _infer_orchestrator(self, trigger: str, template_name: str) -> Optional[str]:
        """
        Infer expected orchestrator from trigger/template name.
        
        Args:
            trigger: Trigger phrase (e.g., "start tdd")
            template_name: Template name (e.g., "tdd_workflow_start")
        
        Returns:
            Expected orchestrator class name or None
        """
        # Naming conventions
        mappings = {
            "start tdd": "TDDWorkflowOrchestrator",
            "tdd workflow": "TDDWorkflowOrchestrator",
            "begin tdd": "TDDWorkflowOrchestrator",
            "tdd session": "TDDWorkflowOrchestrator",
            "tdd": "TDDWorkflowOrchestrator",
            "git checkpoint": "GitCheckpointOrchestrator",
            "create checkpoint": "GitCheckpointOrchestrator",
            "save checkpoint": "GitCheckpointOrchestrator",
            "lint validation": "LintValidationOrchestrator",
            "validate lint": "LintValidationOrchestrator",
            "check code quality": "LintValidationOrchestrator",
            "run linter": "LintValidationOrchestrator",
            "session completion": "SessionCompletionOrchestrator",
            "complete session": "SessionCompletionOrchestrator",
            "finish session": "SessionCompletionOrchestrator",
            "session report": "SessionCompletionOrchestrator",
            "end session": "SessionCompletionOrchestrator",
            "upgrade": "UpgradeOrchestrator",
            "upgrade cortex": "UpgradeOrchestrator",
            "cortex version": "UpgradeOrchestrator",
            "check version": "UpgradeOrchestrator",
            "optimize": "OptimizeCortexOrchestrator",
            "optimize cortex": "OptimizeCortexOrchestrator",
            "cleanup": "HolisticCleanupOrchestrator",
            "clean up": "HolisticCleanupOrchestrator",
            "cleanup cortex": "HolisticCleanupOrchestrator",
            "clean cortex": "HolisticCleanupOrchestrator",
            "holistic cleanup": "HolisticCleanupOrchestrator",
            "setup": "SetupOrchestrator",
            "setup copilot instructions": "SetupEPMOrchestrator",
            "setup instructions": "SetupEPMOrchestrator",
            "generate copilot instructions": "SetupEPMOrchestrator",
            "create copilot instructions": "SetupEPMOrchestrator",
            "setup epm": "SetupEPMOrchestrator",
            "copilot instructions": "SetupEPMOrchestrator",
            "plan ado": "ADOWorkItemOrchestrator",
            "create work item": "ADOWorkItemOrchestrator",
            "ado work item": "ADOWorkItemOrchestrator",
            "create story": "ADOWorkItemOrchestrator",
            "create feature": "ADOWorkItemOrchestrator",
            "create bug": "ADOWorkItemOrchestrator",
            "ado planning": "ADOWorkItemOrchestrator",
            "demo": "DemoOrchestrator",
            "cortex demo": "DemoOrchestrator",
            "show demo": "DemoOrchestrator",
            "run demo": "DemoOrchestrator",
            "demo cortex": "DemoOrchestrator",
            "live demo": "DemoOrchestrator",
            "unified entry": "UnifiedEntryPointOrchestrator",
            "entry point": "UnifiedEntryPointOrchestrator",
            "cortex entry": "UnifiedEntryPointOrchestrator",
            "unified interface": "UnifiedEntryPointOrchestrator",
            "feedback": "FeedbackOrchestrator",
            "align": "SystemAlignmentOrchestrator",
            "healthcheck": "HealthCheckOrchestrator",
            "design sync": "DesignSyncOrchestrator",
            "design": "DesignSyncOrchestrator",
            "sync": "DesignSyncOrchestrator",
            "publish": "PublishBranchOrchestrator",
            "workflow": "WorkflowOrchestrator",
            "architect": "ArchitectAgent",
            "analyze architecture": "ArchitectAgent",
            "architecture analysis": "ArchitectAgent",
            "crawl shell": "ArchitectAgent",
            "feedback": "FeedbackAgent",
            "report issue": "FeedbackAgent",
            "report bug": "FeedbackAgent",
            "ingest to brain": "BrainIngestionAgent",
            "save to brain": "BrainIngestionAgent",
            "brain ingest": "BrainIngestionAgent",
            "learn this": "BrainIngestionAgent",
            "brain ingestion adapter": "BrainIngestionAdapterAgent",
            "start brain ingestion adapter": "BrainIngestionAdapterAgent",
            "run ingestion adapter": "BrainIngestionAdapterAgent",
            "adapter brain ingestion": "BrainIngestionAdapterAgent",
            "plan": "InteractivePlannerAgent",
            "planning": "PlanningOrchestrator",
            "plan a feature": "InteractivePlannerAgent",
            "feature planning": "InteractivePlannerAgent",
            "hands on tutorial": "HandsOnTutorialOrchestrator",
            "start hands on tutorial": "HandsOnTutorialOrchestrator",
            "run on tutorial": "HandsOnTutorialOrchestrator",
            "publish branch": "PublishBranchOrchestrator",
            "start publish branch": "PublishBranchOrchestrator",
            "run branch": "PublishBranchOrchestrator",
            "optimize system": "OptimizeSystemOrchestrator",
            "start optimize system": "OptimizeSystemOrchestrator",
            "run system": "OptimizeSystemOrchestrator",
            "view discovery": "ViewDiscoveryAgent",
            "start view discovery": "ViewDiscoveryAgent",
            "run discovery": "ViewDiscoveryAgent",
            "learning capture": "LearningCaptureAgent",
            "start learning capture": "LearningCaptureAgent",
            "run capture": "LearningCaptureAgent",
            "code review": "CodeReviewOrchestrator",
            "review pr": "CodeReviewOrchestrator",
            "pr review": "CodeReviewOrchestrator",
            "review pull request": "CodeReviewOrchestrator",
            "pull request review": "CodeReviewOrchestrator",
            "ado pr review": "CodeReviewOrchestrator"
        }
        
        # Check trigger keywords
        trigger_lower = trigger.lower()
        template_lower = template_name.lower()
        
        # First pass: exact matches (prioritize)
        for keyword, orchestrator in mappings.items():
            if keyword == trigger_lower or keyword == template_lower:
                return orchestrator
        
        # Second pass: substring matches
        for keyword, orchestrator in mappings.items():
            if keyword in trigger_lower or keyword in template_lower:
                return orchestrator
        
        return None
    
    def validate_wiring(
        self,
        discovered_orchestrators: Dict[str, Dict[str, Any]]
    ) -> tuple[List[str], List[str]]:
        """
        Validate entry point wiring.
        
        Args:
            discovered_orchestrators: Dict of discovered orchestrators
        
        Returns:
            Tuple of (orphaned_triggers, ghost_features)
            - orphaned_triggers: Triggers with no orchestrator
            - ghost_features: Orchestrators with no trigger
        """
        entry_points = self.discover()
        
        orphaned_triggers = []
        wired_orchestrators = set()
        
        # Check for orphaned triggers
        for trigger, metadata in entry_points.items():
            expected = metadata["expected_orchestrator"]
            if expected and expected not in discovered_orchestrators:
                orphaned_triggers.append(trigger)
            elif expected:
                wired_orchestrators.add(expected)
        
        # Check for ghost features (orchestrators with no entry point)
        ghost_features = []
        for orchestrator_name in discovered_orchestrators.keys():
            if orchestrator_name not in wired_orchestrators:
                # Skip admin-only features
                if "admin" not in orchestrator_name.lower():
                    ghost_features.append(orchestrator_name)
        
        return orphaned_triggers, ghost_features
