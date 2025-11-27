"""
CORTEX 2.0 YAML Plugin Processor
Loads, validates, and executes machine-readable YAML plugins
"""

import yaml
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import asdict

from .plugin_schema import (
    PluginConfig, Target, WorkflowStep, ValidationRule, Parameter,
    validate_plugin_schema
)


class PluginProcessor:
    """Process and execute YAML-based plugins"""
    
    def __init__(self, cortex_root: Path):
        self.cortex_root = cortex_root
        self.plugin_cache = {}
        
    def load_plugin(self, plugin_path: str) -> tuple[Optional[PluginConfig], Optional[str]]:
        """
        Load and validate a YAML plugin
        
        Args:
            plugin_path: Path to .yaml plugin file (relative or absolute)
            
        Returns:
            (plugin_config, error_message)
        """
        try:
            # Resolve path
            if not os.path.isabs(plugin_path):
                plugin_path = self.cortex_root / plugin_path
            
            # Check cache
            cache_key = str(plugin_path)
            if cache_key in self.plugin_cache:
                return self.plugin_cache[cache_key], None
            
            # Load YAML
            with open(plugin_path, 'r', encoding='utf-8') as f:
                config_dict = yaml.safe_load(f)
            
            # Validate schema
            is_valid, error = validate_plugin_schema(config_dict)
            if not is_valid:
                return None, f"Schema validation failed: {error}"
            
            # Convert to PluginConfig
            plugin = self._dict_to_plugin(config_dict)
            
            # Cache
            self.plugin_cache[cache_key] = plugin
            
            return plugin, None
            
        except FileNotFoundError:
            return None, f"Plugin file not found: {plugin_path}"
        except yaml.YAMLError as e:
            return None, f"YAML parsing error: {str(e)}"
        except Exception as e:
            return None, f"Error loading plugin: {str(e)}"
    
    def _dict_to_plugin(self, config_dict: Dict[str, Any]) -> PluginConfig:
        """Convert dictionary to PluginConfig dataclass"""
        
        # Parse targets
        targets = []
        for t in config_dict.get("targets", []):
            targets.append(Target(
                path=t["path"],
                type=t["type"],
                constraints=t.get("constraints", []),
                metadata=t.get("metadata", {})
            ))
        
        # Parse workflow
        workflow = []
        for s in config_dict.get("workflow", []):
            workflow.append(WorkflowStep(
                step=s["step"],
                action=s["action"],
                params=s.get("params", {}),
                condition=s.get("condition"),
                on_error=s.get("on_error", "abort")
            ))
        
        # Parse validation
        validation = []
        for v in config_dict.get("validation", []):
            validation.append(ValidationRule(
                check=v["check"],
                scope=v["scope"],
                required=v.get("required", False),
                params=v.get("params", {})
            ))
        
        # Parse parameters
        parameters = []
        for p in config_dict.get("parameters", []):
            parameters.append(Parameter(
                name=p["name"],
                type=p["type"],
                default=p.get("default"),
                required=p.get("required", False),
                values=p.get("values"),
                description=p.get("description", "")
            ))
        
        return PluginConfig(
            version=config_dict["version"],
            type=config_dict["type"],
            name=config_dict["name"],
            description=config_dict.get("description", ""),
            targets=targets,
            workflow=workflow,
            validation=validation,
            parameters=parameters,
            agent_class=config_dict.get("agent_class"),
            requires=config_dict.get("requires", []),
            author=config_dict.get("author", "CORTEX"),
            created=config_dict.get("created"),
            updated=config_dict.get("updated")
        )
    
    def execute_workflow(
        self, 
        plugin: PluginConfig, 
        user_params: Dict[str, Any] = None
    ) -> tuple[bool, Optional[str], Dict[str, Any]]:
        """
        Execute a workflow plugin
        
        Args:
            plugin: Loaded plugin configuration
            user_params: User-provided parameters
            
        Returns:
            (success, error_message, result_data)
        """
        if plugin.type != "workflow":
            return False, f"Cannot execute non-workflow plugin: {plugin.type}", {}
        
        user_params = user_params or {}
        results = {}
        
        try:
            # Merge parameters with defaults
            params = self._merge_parameters(plugin.parameters, user_params)
            
            # Execute each workflow step
            for step in plugin.workflow:
                # Check condition
                if step.condition and not self._eval_condition(step.condition, params, results):
                    continue
                
                # Execute step
                step_result = self._execute_step(step, params, plugin.targets)
                results[step.step] = step_result
                
                # Handle errors
                if step_result.get("error"):
                    if step.on_error == "abort":
                        return False, f"Step '{step.step}' failed: {step_result['error']}", results
                    elif step.on_error == "retry":
                        # Simple retry logic (could be enhanced)
                        step_result = self._execute_step(step, params, plugin.targets)
                        results[step.step] = step_result
                        if step_result.get("error"):
                            return False, f"Step '{step.step}' failed after retry", results
            
            # Run validation
            validation_passed, validation_error = self._validate_results(plugin.validation, results)
            if not validation_passed:
                return False, f"Validation failed: {validation_error}", results
            
            return True, None, results
            
        except Exception as e:
            return False, f"Workflow execution error: {str(e)}", results
    
    def _merge_parameters(
        self, 
        param_defs: List[Parameter], 
        user_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge user parameters with defaults"""
        merged = {}
        
        for param_def in param_defs:
            if param_def.name in user_params:
                merged[param_def.name] = user_params[param_def.name]
            elif param_def.default is not None:
                merged[param_def.name] = param_def.default
            elif param_def.required:
                raise ValueError(f"Required parameter missing: {param_def.name}")
        
        return merged
    
    def _eval_condition(
        self, 
        condition: str, 
        params: Dict[str, Any], 
        results: Dict[str, Any]
    ) -> bool:
        """Evaluate a condition string"""
        # Simple condition evaluation
        # Could be enhanced with safe expression parser
        try:
            # Replace parameter references
            for key, value in params.items():
                condition = condition.replace(f"${key}", str(value))
            
            # Check for simple conditions
            if condition == "auto_deploy_flag":
                return params.get("deploy", False)
            if condition == "new_technical_features":
                return results.get("identify_gaps", {}).get("technical_missing", [])
            
            return True  # Default to true if condition not recognized
            
        except Exception:
            return False
    
    def _execute_step(
        self, 
        step: WorkflowStep, 
        params: Dict[str, Any], 
        targets: List[Target]
    ) -> Dict[str, Any]:
        """Execute a single workflow step"""
        # This is a placeholder - actual implementation would call
        # appropriate CORTEX modules based on step.action
        
        result = {
            "step": step.step,
            "action": step.action,
            "success": True,
            "error": None,
            "data": {}
        }
        
        # Dispatch based on action type
        if step.action == "analyze":
            result["data"] = self._analyze_action(step, params)
        elif step.action == "execute":
            result["data"] = self._execute_action(step, params, targets)
        elif step.action == "validate":
            result["data"] = self._validate_action(step, params, targets)
        elif step.action == "query":
            result["data"] = self._query_action(step, params)
        elif step.action == "transform":
            result["data"] = self._transform_action(step, params, targets)
        elif step.action == "notify":
            result["data"] = self._notify_action(step, params)
        
        return result
    
    def _analyze_action(self, step: WorkflowStep, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute analyze action"""
        # Placeholder for actual git analysis, file scanning, etc.
        return {"analyzed": True, "params": step.params}
    
    def _execute_action(self, step: WorkflowStep, params: Dict[str, Any], targets: List[Target]) -> Dict[str, Any]:
        """Execute execute action"""
        # Placeholder for actual code execution, file updates, etc.
        return {"executed": True, "targets": len(targets)}
    
    def _validate_action(self, step: WorkflowStep, params: Dict[str, Any], targets: List[Target]) -> Dict[str, Any]:
        """Execute validate action"""
        # Placeholder for actual validation logic
        return {"validated": True, "checks_passed": True}
    
    def _query_action(self, step: WorkflowStep, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute query action"""
        # Placeholder for database/knowledge graph queries
        return {"query_results": []}
    
    def _transform_action(self, step: WorkflowStep, params: Dict[str, Any], targets: List[Target]) -> Dict[str, Any]:
        """Execute transform action"""
        # Placeholder for data transformation
        return {"transformed": True}
    
    def _notify_action(self, step: WorkflowStep, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute notify action"""
        # Placeholder for notifications
        return {"notified": True}
    
    def _validate_results(
        self, 
        validation_rules: List[ValidationRule], 
        results: Dict[str, Any]
    ) -> tuple[bool, Optional[str]]:
        """Run validation checks on results"""
        for rule in validation_rules:
            # Placeholder for actual validation
            # Would check specific conditions based on rule.check
            pass
        
        return True, None
    
    def get_plugin_info(self, plugin: PluginConfig) -> Dict[str, Any]:
        """Get plugin metadata and structure"""
        return {
            "name": plugin.name,
            "version": plugin.version,
            "type": plugin.type,
            "description": plugin.description,
            "targets_count": len(plugin.targets),
            "workflow_steps": len(plugin.workflow),
            "validation_rules": len(plugin.validation),
            "parameters": [
                {
                    "name": p.name,
                    "type": p.type,
                    "required": p.required,
                    "default": p.default
                }
                for p in plugin.parameters
            ]
        }
