"""
CORTEX 2.0 Plugin Schema Definitions
Machine-readable plugin system using YAML with strict validation
"""

from typing import Dict, List, Any, Optional, Union, Literal
from dataclasses import dataclass, field
from enum import Enum
import yaml


class PluginType(str, Enum):
    """Plugin categories"""
    WORKFLOW = "workflow"
    AGENT = "agent"
    CONSTRAINT = "constraint"
    VALIDATOR = "validator"


class StepType(str, Enum):
    """Workflow step types"""
    ANALYZE = "analyze"
    EXECUTE = "execute"
    VALIDATE = "validate"
    QUERY = "query"
    TRANSFORM = "transform"
    NOTIFY = "notify"


@dataclass
class Target:
    """Target file or resource for plugin operations"""
    path: str
    type: str
    constraints: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowStep:
    """Single step in a workflow"""
    step: str
    action: StepType
    params: Dict[str, Any] = field(default_factory=dict)
    condition: Optional[str] = None
    on_error: str = "abort"  # abort, continue, retry


@dataclass
class ValidationRule:
    """Validation check definition"""
    check: str
    scope: str
    required: bool = False
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Parameter:
    """Plugin parameter definition"""
    name: str
    type: str  # string, int, bool, date, enum, list
    default: Any = None
    required: bool = False
    values: Optional[List[str]] = None  # For enum type
    description: str = ""


@dataclass
class PluginConfig:
    """Complete plugin configuration"""
    version: str
    type: PluginType
    name: str
    description: str = ""
    
    # Optional sections depending on plugin type
    targets: List[Target] = field(default_factory=list)
    workflow: List[WorkflowStep] = field(default_factory=list)
    validation: List[ValidationRule] = field(default_factory=list)
    parameters: List[Parameter] = field(default_factory=list)
    
    # Agent-specific
    agent_class: Optional[str] = None
    requires: List[str] = field(default_factory=list)
    
    # Metadata
    author: str = "CORTEX"
    created: Optional[str] = None
    updated: Optional[str] = None


# JSON Schema for YAML validation
PLUGIN_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["version", "type", "name"],
    "properties": {
        "version": {
            "type": "string",
            "pattern": "^\\d+\\.\\d+(\\.\\d+)?$"
        },
        "type": {
            "type": "string",
            "enum": ["workflow", "agent", "constraint", "validator"]
        },
        "name": {"type": "string"},
        "description": {"type": "string"},
        
        "targets": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["path", "type"],
                "properties": {
                    "path": {"type": "string"},
                    "type": {"type": "string"},
                    "constraints": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "metadata": {"type": "object"}
                }
            }
        },
        
        "workflow": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["step", "action"],
                "properties": {
                    "step": {"type": "string"},
                    "action": {
                        "type": "string",
                        "enum": ["analyze", "execute", "validate", "query", "transform", "notify"]
                    },
                    "params": {"type": "object"},
                    "condition": {"type": "string"},
                    "on_error": {
                        "type": "string",
                        "enum": ["abort", "continue", "retry"]
                    }
                }
            }
        },
        
        "validation": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["check", "scope"],
                "properties": {
                    "check": {"type": "string"},
                    "scope": {"type": "string"},
                    "required": {"type": "boolean"},
                    "params": {"type": "object"}
                }
            }
        },
        
        "parameters": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "type"],
                "properties": {
                    "name": {"type": "string"},
                    "type": {
                        "type": "string",
                        "enum": ["string", "int", "bool", "date", "enum", "list"]
                    },
                    "default": {},
                    "required": {"type": "boolean"},
                    "values": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "description": {"type": "string"}
                }
            }
        },
        
        "agent_class": {"type": "string"},
        "requires": {
            "type": "array",
            "items": {"type": "string"}
        },
        
        "author": {"type": "string"},
        "created": {"type": "string"},
        "updated": {"type": "string"}
    }
}


def validate_plugin_schema(config: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Validate plugin configuration against schema
    
    Returns:
        (is_valid, error_message)
    """
    try:
        # Check required fields
        if "version" not in config:
            return False, "Missing required field: version"
        if "type" not in config:
            return False, "Missing required field: type"
        if "name" not in config:
            return False, "Missing required field: name"
        
        # Validate plugin type
        valid_types = ["workflow", "agent", "constraint", "validator"]
        if config["type"] not in valid_types:
            return False, f"Invalid plugin type: {config['type']}. Must be one of: {valid_types}"
        
        # Validate workflow steps if present
        if "workflow" in config:
            valid_actions = ["analyze", "execute", "validate", "query", "transform", "notify"]
            for i, step in enumerate(config["workflow"]):
                if "step" not in step:
                    return False, f"Workflow step {i} missing 'step' field"
                if "action" not in step:
                    return False, f"Workflow step {i} missing 'action' field"
                if step["action"] not in valid_actions:
                    return False, f"Invalid action '{step['action']}' in step {i}"
        
        # Validate parameters if present
        if "parameters" in config:
            valid_param_types = ["string", "int", "bool", "date", "enum", "list"]
            for param in config["parameters"]:
                if "name" not in param:
                    return False, "Parameter missing 'name' field"
                if "type" not in param:
                    return False, f"Parameter '{param.get('name')}' missing 'type' field"
                if param["type"] not in valid_param_types:
                    return False, f"Invalid parameter type: {param['type']}"
                
                # Enum must have values
                if param["type"] == "enum" and not param.get("values"):
                    return False, f"Enum parameter '{param['name']}' must have 'values'"
        
        return True, None
        
    except Exception as e:
        return False, f"Schema validation error: {str(e)}"
