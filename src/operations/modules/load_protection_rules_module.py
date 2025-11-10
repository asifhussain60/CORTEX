"""
Load protection rules module for brain protection validation.

Part of the Brain Protection operation - loads brain-protection-rules.yaml.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any

from src.operations.base_operation_module import (
    BaseOperationModule,
    OperationModuleMetadata,
    OperationResult,
    OperationPhase,
    OperationStatus
)


class LoadProtectionRulesModule(BaseOperationModule):
    """
    Load brain protection rules from YAML configuration.
    
    Loads and validates the brain-protection-rules.yaml file that defines
    SKULL protection rules and tier protection policies.
    """
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Get module metadata."""
        return OperationModuleMetadata(
            module_id="load_protection_rules",
            name="Load Protection Rules",
            description="Load brain-protection-rules.yaml",
            phase=OperationPhase.PREPARATION,
            priority=10
        )
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Execute protection rules loading.
        
        Args:
            context: Operation context
            
        Returns:
            OperationResult with loaded rules
        """
        try:
            project_root = Path(context.get("project_root", os.getcwd()))
            brain_root = project_root / "cortex-brain"
            rules_file = brain_root / "brain-protection-rules.yaml"
            
            if not rules_file.exists():
                return OperationResult(
                    success=False,
                    status=OperationStatus.FAILED,
                    message="brain-protection-rules.yaml not found",
                    error=f"Protection rules file not found at {rules_file}"
                )
            
            self.log_info(f"Loading protection rules from {rules_file}")
            
            # Load YAML
            with open(rules_file, 'r', encoding='utf-8') as f:
                rules = yaml.safe_load(f)
            
            if not rules:
                return OperationResult(
                    success=False,
                    status=OperationStatus.FAILED,
                    message="Protection rules file is empty",
                    error="YAML file contains no rules"
                )
            
            # Validate structure
            validation = self._validate_rules_structure(rules)
            if not validation["valid"]:
                return OperationResult(
                    success=False,
                    status=OperationStatus.FAILED,
                    message="Invalid protection rules structure",
                    error=validation["error"]
                )
            
            # Count rules
            skull_rules_count = len(rules.get("skull_rules", {}))
            tier_protections = len([k for k in rules.keys() if k.startswith("tier")])
            
            self.log_info(
                f"Loaded {skull_rules_count} SKULL rules and "
                f"{tier_protections} tier protections"
            )
            
            return OperationResult(
                success=True,
                status=OperationStatus.SUCCESS,
                message=f"Loaded protection rules: {skull_rules_count} SKULL rules",
                data={
                    "protection_rules": rules,
                    "skull_rules_count": skull_rules_count,
                    "tier_protections_count": tier_protections
                }
            )
            
        except yaml.YAMLError as e:
            self.log_error(f"YAML parsing error: {e}")
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message="Failed to parse protection rules YAML",
                errors=[str(e)]
            )
        except Exception as e:
            self.log_error(f"Failed to load protection rules: {e}")
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message="Protection rules loading failed",
                errors=[str(e)]
            )
    
    def _validate_rules_structure(self, rules: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate protection rules structure.
        
        Args:
            rules: Loaded rules dictionary
            
        Returns:
            Validation result
        """
        # Check for required sections
        if "skull_rules" not in rules:
            return {
                "valid": False,
                "error": "Missing required 'skull_rules' section"
            }
        
        # Validate SKULL rules
        skull_rules = rules["skull_rules"]
        for rule_id, rule_def in skull_rules.items():
            if "name" not in rule_def:
                return {
                    "valid": False,
                    "error": f"SKULL rule {rule_id} missing 'name'"
                }
            
            if "severity" not in rule_def:
                return {
                    "valid": False,
                    "error": f"SKULL rule {rule_id} missing 'severity'"
                }
            
            if rule_def["severity"] not in ["BLOCKING", "WARNING"]:
                return {
                    "valid": False,
                    "error": f"SKULL rule {rule_id} has invalid severity: {rule_def['severity']}"
                }
        
        return {"valid": True}


def register() -> BaseOperationModule:
    """Register module for discovery."""
    return LoadProtectionRulesModule()
