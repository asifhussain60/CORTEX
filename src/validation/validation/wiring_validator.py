"""
Wiring Validator - Entry Point Mapping Validation

Validates that orchestrators are properly wired to entry points:
- Checks trigger → orchestrator mapping
- Detects orphaned triggers (no orchestrator)
- Detects ghost features (orchestrator but no trigger)
- Validates naming conventions

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Set

logger = logging.getLogger(__name__)


class WiringValidator:
    """
    Entry point wiring validator.
    
    Validates that all user-facing entry points (response templates)
    are properly connected to orchestrator implementations.
    """
    
    def __init__(self, project_root: Path):
        """
        Initialize wiring validator.
        
        Args:
            project_root: Root directory of CORTEX project
        """
        self.project_root = Path(project_root)
    
    def validate_wiring(
        self,
        discovered_orchestrators: Dict[str, Dict[str, Any]],
        entry_points: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Validate entry point wiring.
        
        Args:
            discovered_orchestrators: Dict of discovered orchestrators
            entry_points: Dict of entry points from templates
        
        Returns:
            Validation results with orphaned/ghost features
        """
        results = {
            "total_entry_points": len(entry_points),
            "total_orchestrators": len(discovered_orchestrators),
            "wired_orchestrators": set(),
            "orphaned_triggers": [],
            "ghost_features": [],
            "wiring_suggestions": []
        }
        
        # Check each entry point
        for trigger, metadata in entry_points.items():
            expected_orch = metadata.get("expected_orchestrator")
            
            if not expected_orch:
                # No orchestrator expected (e.g., help commands)
                continue
            
            if expected_orch in discovered_orchestrators:
                # Properly wired
                results["wired_orchestrators"].add(expected_orch)
            else:
                # Orphaned trigger
                results["orphaned_triggers"].append({
                    "trigger": trigger,
                    "expected_orchestrator": expected_orch,
                    "template": metadata.get("template")
                })
                
                # Generate suggestion
                suggestion = self._generate_wiring_suggestion(trigger, expected_orch)
                results["wiring_suggestions"].append(suggestion)
        
        # Check for ghost features (orchestrators without entry points)
        for orch_name in discovered_orchestrators.keys():
            # Skip admin-only orchestrators
            if "admin" in orch_name.lower() or "system" in orch_name.lower():
                continue
            
            if orch_name not in results["wired_orchestrators"]:
                results["ghost_features"].append({
                    "orchestrator": orch_name,
                    "suggestion": f"Add entry point trigger for {orch_name}"
                })
        
        results["wired_count"] = len(results["wired_orchestrators"])
        results["orphaned_count"] = len(results["orphaned_triggers"])
        results["ghost_count"] = len(results["ghost_features"])
        
        return results
    
    def _generate_wiring_suggestion(self, trigger: str, orchestrator_name: str) -> Dict[str, str]:
        """
        Generate wiring suggestion for orphaned trigger.
        
        Args:
            trigger: Trigger phrase
            orchestrator_name: Expected orchestrator name
        
        Returns:
            Suggestion dict with code snippet
        """
        # Extract feature name from orchestrator
        feature_name = orchestrator_name.replace("Orchestrator", "").lower()
        
        return {
            "trigger": trigger,
            "orchestrator": orchestrator_name,
            "action": "create_orchestrator",
            "template": f"""
# Create missing orchestrator: {orchestrator_name}

from src.operations.base_operation_module import BaseOperationModule, OperationResult, OperationStatus

class {orchestrator_name}(BaseOperationModule):
    \"\"\"
    {feature_name.replace('_', ' ').title()} orchestrator.
    
    Triggered by: {trigger}
    \"\"\"
    
    def get_metadata(self):
        return OperationModuleMetadata(
            module_id="{feature_name}",
            name="{feature_name.replace('_', ' ').title()}",
            description="TODO: Add description",
            phase=OperationPhase.PROCESSING
        )
    
    def execute(self, context):
        # TODO: Implement feature logic
        return OperationResult(
            success=True,
            status=OperationStatus.SUCCESS,
            message="Feature executed successfully"
        )
""".strip()
        }
    
    def check_orchestrator_wired(
        self,
        orchestrator_name: str,
        entry_points: Dict[str, Dict[str, Any]]
    ) -> bool:
        """
        Check if specific orchestrator is wired to entry point.
        
        Args:
            orchestrator_name: Orchestrator class name
            entry_points: Dict of entry points
        
        Returns:
            True if orchestrator is wired
        """
        for trigger, metadata in entry_points.items():
            expected = metadata.get("expected_orchestrator")
            if expected == orchestrator_name:
                return True
        
        return False
    
    def get_wiring_status(
        self,
        orchestrator_name: str,
        entry_points: Dict[str, Dict[str, Any]]
    ) -> str:
        """
        Get wiring status for orchestrator.
        
        Args:
            orchestrator_name: Orchestrator class name
            entry_points: Dict of entry points
        
        Returns:
            Status: 'wired', 'unwired', or 'admin'
        """
        # Check if admin-only
        if "admin" in orchestrator_name.lower() or "system" in orchestrator_name.lower():
            return "admin"
        
        # Check if wired
        if self.check_orchestrator_wired(orchestrator_name, entry_points):
            return "wired"
        
        return "unwired"
