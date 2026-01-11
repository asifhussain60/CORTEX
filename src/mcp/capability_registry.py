"""
MCP Capability Registry - Exposes CORTEX Orchestrator Capabilities

Provides a registry of capabilities that can be discovered and invoked through
Model Context Protocol (MCP). Maps orchestrator functionality to MCP tools.

Author: Asif Hussain
Version: 1.0.0
Created: 2026-01-08
Correlation ID: FEAT06-P1-T1.2
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict
from pathlib import Path
import yaml


logger = logging.getLogger("cortex.mcp.capability_registry")


@dataclass
class Capability:
    """
    Capability definition for an orchestrator function.
    
    Maps to MCP tool format with JSON Schema parameter definitions.
    """
    name: str
    description: str
    parameters: Dict[str, Any]
    returns: Dict[str, Any]
    orchestrator_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    def to_mcp_tool(self) -> Dict[str, Any]:
        """
        Convert to MCP tool definition format.
        
        Returns:
            MCP tool definition with JSON Schema
        """
        # Build JSON Schema for parameters
        properties = {}
        required = []
        
        for param_name, param_def in self.parameters.items():
            properties[param_name] = {
                "type": param_def.get("type", "string"),
                "description": param_def.get("description", "")
            }
            if param_def.get("required", False):
                required.append(param_name)
        
        tool_def = {
            "name": self.name,
            "description": self.description,
            "inputSchema": {
                "type": "object",
                "properties": properties
            }
        }
        
        if required:
            tool_def["inputSchema"]["required"] = required
        
        return tool_def
    
    def validate_parameters(self, params: Dict[str, Any]) -> bool:
        """
        Validate parameters against definition.
        
        Args:
            params: Parameters to validate
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If required parameter is missing
            TypeError: If parameter type is wrong
        """
        for param_name, param_def in self.parameters.items():
            # Check required parameters
            if param_def.get("required", False) and param_name not in params:
                raise ValueError(f"Required parameter '{param_name}' is missing")
            
            # Check types (basic validation)
            if param_name in params:
                expected_type = param_def.get("type", "string")
                value = params[param_name]
                
                if expected_type == "string" and not isinstance(value, str):
                    raise TypeError(f"Parameter '{param_name}' must be string, got {type(value).__name__}")
                elif expected_type == "integer" and not isinstance(value, int):
                    raise TypeError(f"Parameter '{param_name}' must be integer, got {type(value).__name__}")
                elif expected_type == "boolean" and not isinstance(value, bool):
                    raise TypeError(f"Parameter '{param_name}' must be boolean, got {type(value).__name__}")
        
        return True


class CapabilityRegistry:
    """
    Registry of available orchestrator capabilities.
    
    Manages capability definitions and provides discovery/search functionality.
    """
    
    def __init__(self):
        self.capabilities: Dict[str, Capability] = {}
        logger.info("CapabilityRegistry initialized")
    
    def register(self, capability: Capability):
        """
        Register a capability.
        
        Args:
            capability: Capability to register
        """
        self.capabilities[capability.name] = capability
        logger.debug(f"Registered capability: {capability.name}")
    
    def unregister(self, name: str):
        """
        Unregister a capability.
        
        Args:
            name: Capability name
        """
        if name in self.capabilities:
            del self.capabilities[name]
            logger.debug(f"Unregistered capability: {name}")
    
    def get(self, name: str) -> Optional[Capability]:
        """
        Get capability by name.
        
        Args:
            name: Capability name
            
        Returns:
            Capability or None if not found
        """
        return self.capabilities.get(name)
    
    def list_all(self) -> List[Capability]:
        """
        List all registered capabilities.
        
        Returns:
            List of all capabilities
        """
        return list(self.capabilities.values())
    
    def search_by_tag(self, tag: str) -> List[Capability]:
        """
        Search capabilities by metadata tag.
        
        Args:
            tag: Tag to search for
            
        Returns:
            List of capabilities with matching tag
        """
        results = []
        for cap in self.capabilities.values():
            tags = cap.metadata.get("tags", [])
            if tag in tags:
                results.append(cap)
        return results
    
    def get_metadata(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get capability metadata.
        
        Args:
            name: Capability name
            
        Returns:
            Metadata dict or None if not found
        """
        cap = self.get(name)
        return cap.metadata if cap else None
    
    def group_by_category(self) -> Dict[str, List[Capability]]:
        """
        Group capabilities by category.
        
        Returns:
            Dict mapping category to list of capabilities
        """
        grouped: Dict[str, List[Capability]] = {}
        
        for cap in self.capabilities.values():
            category = cap.metadata.get("category", "other")
            if category not in grouped:
                grouped[category] = []
            grouped[category].append(cap)
        
        return grouped
    
    def load_from_orchestrator_registry(self, orchestrator_registry):
        """
        Load capabilities from orchestrator registry.
        
        Args:
            orchestrator_registry: OrchestratorRegistry instance
        """
        # Get all registered orchestrators
        orchestrators = orchestrator_registry.list_all()
        
        # Handle both list and dict returns
        if isinstance(orchestrators, dict):
            items = orchestrators.items()
        else:
            # If list, create temporary dict mapping
            items = [(orch.get("id", f"orch_{i}"), orch) for i, orch in enumerate(orchestrators)]
        
        for orch_id, orch_info in items:
            # Load manifest if available
            manifest_path = orch_info.get("manifest_path") if isinstance(orch_info, dict) else None
            if manifest_path and Path(manifest_path).exists():
                try:
                    with open(manifest_path, 'r') as f:
                        manifest = yaml.safe_load(f)
                    self.load_from_manifest(orch_id, manifest)
                except Exception as e:
                    logger.warning(f"Failed to load manifest for {orch_id}: {e}")
        
        logger.info(f"Loaded {len(self.capabilities)} capabilities from orchestrator registry")
    
    def load_from_manifest(self, orchestrator_id: str, manifest: Dict[str, Any]):
        """
        Load capabilities from orchestrator manifest.
        
        Args:
            orchestrator_id: Orchestrator ID
            manifest: Manifest data
        """
        capabilities_def = manifest.get("capabilities", {})
        
        for cap_name, cap_def in capabilities_def.items():
            capability = Capability(
                name=cap_name,
                description=cap_def.get("description", ""),
                parameters=cap_def.get("parameters", {}),
                returns=cap_def.get("returns", {}),
                orchestrator_id=orchestrator_id,
                metadata=cap_def.get("metadata", {})
            )
            self.register(capability)
    
    def discover_all(self):
        """
        Discover all capabilities from known orchestrators and decorated tools.
        
        Loads capability definitions from:
        1. Common orchestrator patterns (manual definitions)
        2. @mcp_tool decorated functions (automatic discovery)
        """
        # Define common CORTEX capabilities (manually defined orchestrators)
        common_capabilities = [
            Capability(
                name="plan",
                description="Create a structured plan with phases and tasks",
                parameters={
                    "request": {
                        "type": "string",
                        "description": "Planning request description",
                        "required": True
                    }
                },
                returns={"type": "object", "description": "Plan with YAML structure"},
                orchestrator_id="planning_v5",
                metadata={
                    "category": "planning",
                    "tags": ["planning", "strategy"],
                    "version": "5.0",
                    "autonomous": True
                }
            ),
            Capability(
                name="tdd",
                description="Execute test-driven development cycle (RED→GREEN→REFACTOR)",
                parameters={
                    "request": {
                        "type": "string",
                        "description": "TDD request (feature to implement)",
                        "required": True
                    }
                },
                returns={"type": "object", "description": "TDD execution results"},
                orchestrator_id="tdd_orchestrator",
                metadata={
                    "category": "development",
                    "tags": ["testing", "development", "quality"],
                    "version": "2.0",
                    "autonomous": False
                }
            ),
            Capability(
                name="investigate",
                description="Perform root cause analysis and investigation",
                parameters={
                    "issue": {
                        "type": "string",
                        "description": "Issue or problem to investigate",
                        "required": True
                    }
                },
                returns={"type": "object", "description": "Investigation report"},
                orchestrator_id="investigation_orchestrator",
                metadata={
                    "category": "analysis",
                    "tags": ["investigation", "debugging", "analysis"],
                    "version": "2.0",
                    "autonomous": True
                }
            ),
            Capability(
                name="refactor",
                description="Refactor and improve code quality",
                parameters={
                    "target": {
                        "type": "string",
                        "description": "Code or component to refactor",
                        "required": True
                    }
                },
                returns={"type": "object", "description": "Refactoring results"},
                orchestrator_id="refactor_orchestrator",
                metadata={
                    "category": "development",
                    "tags": ["refactoring", "code-quality", "improvement"],
                    "version": "2.0",
                    "autonomous": True
                }
            ),
            Capability(
                name="vacuum",
                description="Deep clean workspace and remove unnecessary files",
                parameters={
                    "scope": {
                        "type": "string",
                        "description": "Scope of cleanup (cache, logs, all)",
                        "required": False
                    }
                },
                returns={"type": "object", "description": "Cleanup report"},
                orchestrator_id="vacuum_orchestrator",
                metadata={
                    "category": "maintenance",
                    "tags": ["cleanup", "maintenance", "optimization"],
                    "version": "2.0",
                    "autonomous": True
                }
            ),
            Capability(
                name="cortex_align_plan_sync",
                description="Holistic plan synchronization - creates or revises plan for snowball alignment",
                parameters={
                    "ac_file": {
                        "type": "string",
                        "description": "Path to AC YAML file (supports glob patterns)",
                        "required": True
                    },
                    "remediation_file": {
                        "type": "string",
                        "description": "Path to remediation-plan.yaml",
                        "required": True
                    },
                    "snowball_file": {
                        "type": "string",
                        "description": "Path to snowball-strategy.yaml",
                        "required": True
                    },
                    "plan_path": {
                        "type": "string",
                        "description": "Path to plan directory",
                        "required": True
                    },
                    "mode": {
                        "type": "string",
                        "description": "Mode: auto (detect), create (new plan), revise (update existing)",
                        "required": False
                    }
                },
                returns={"type": "object", "description": "Sync results with action, counts, alignment status"},
                orchestrator_id="align_orchestrator",
                metadata={
                    "category": "alignment",
                    "tags": ["planning", "alignment", "synchronization", "snowball"],
                    "version": "1.0",
                    "autonomous": True,
                    "phase": 7,
                    "ac_standard": "AC-ALIGN-001"
                }
            ),
            Capability(
                name="cortex_search_references",
                description="Search for file/text references across workspace",
                parameters={
                    "workspace_root": {
                        "type": "string",
                        "description": "Root directory to search",
                        "required": True
                    },
                    "pattern": {
                        "type": "string",
                        "description": "Text or regex pattern to find",
                        "required": True
                    },
                    "file_extensions": {
                        "type": "array",
                        "description": "File types to search (e.g., ['.md', '.yaml'])",
                        "required": False
                    },
                    "exclude_dirs": {
                        "type": "array",
                        "description": "Directories to exclude from search",
                        "required": False
                    },
                    "use_regex": {
                        "type": "boolean",
                        "description": "Treat pattern as regex",
                        "required": False
                    }
                },
                returns={"type": "object", "description": "Search results with file matches"},
                orchestrator_id="reference_updater",
                metadata={
                    "category": "refactoring",
                    "tags": ["search", "references", "refactoring"],
                    "version": "1.0",
                    "autonomous": True
                }
            ),
            Capability(
                name="cortex_update_references",
                description="Search and replace file/text references across workspace",
                parameters={
                    "workspace_root": {
                        "type": "string",
                        "description": "Root directory to search",
                        "required": True
                    },
                    "old_pattern": {
                        "type": "string",
                        "description": "Pattern to find",
                        "required": True
                    },
                    "new_pattern": {
                        "type": "string",
                        "description": "Replacement text",
                        "required": True
                    },
                    "file_extensions": {
                        "type": "array",
                        "description": "File types to search (e.g., ['.md', '.yaml'])",
                        "required": False
                    },
                    "exclude_dirs": {
                        "type": "array",
                        "description": "Directories to exclude from search",
                        "required": False
                    },
                    "use_regex": {
                        "type": "boolean",
                        "description": "Treat patterns as regex",
                        "required": False
                    },
                    "dry_run": {
                        "type": "boolean",
                        "description": "Preview changes without applying (default: true)",
                        "required": False
                    },
                    "backup": {
                        "type": "boolean",
                        "description": "Create .bak files before modifying (default: true)",
                        "required": False
                    }
                },
                returns={"type": "object", "description": "Update results with file changes"},
                orchestrator_id="reference_updater",
                metadata={
                    "category": "refactoring",
                    "tags": ["refactoring", "rename", "references", "automation"],
                    "version": "1.0",
                    "autonomous": True
                }
            ),
        ]
        
        for cap in common_capabilities:
            self.register(cap)
        
        # Auto-discover decorated tools by importing tool modules
        self._discover_decorated_tools()
        
        logger.info(f"Discovered {len(self.capabilities)} total capabilities ({len(common_capabilities)} manual + decorated)")
    
    def _discover_decorated_tools(self):
        """
        Discover and register @mcp_tool decorated functions.
        
        Imports all *_tools.py modules to trigger decorator registration,
        then converts decorated tool metadata to Capability objects.
        """
        try:
            # Import mcp_decorator to access decorated tools
            from src.mcp.mcp_decorator import get_decorated_tools
            
            # Import all tool modules to trigger decoration
            tool_modules = [
                'src.mcp.audit_tools',
                'src.mcp.governance_tools',
                'src.mcp.housekeeping_tools',
                'src.mcp.planning_tools',
                'src.mcp.tdd_tools',
                'src.mcp.todo_tools',
                'src.mcp.traceability_tools',
            ]
            
            for module_name in tool_modules:
                try:
                    __import__(module_name)
                    logger.debug(f"Imported {module_name} for tool discovery")
                except Exception as e:
                    logger.warning(f"Failed to import {module_name}: {e}")
            
            # Get all decorated tools
            decorated_tools = get_decorated_tools()
            
            # Convert to Capability objects and register
            for tool_meta in decorated_tools:
                capability = Capability(
                    name=tool_meta["name"],
                    description=tool_meta["description"],
                    parameters=tool_meta["parameters"],
                    returns=tool_meta["returns"],
                    orchestrator_id=tool_meta.get("orchestrator_id"),
                    metadata=tool_meta.get("metadata", {})
                )
                self.register(capability)
            
            logger.info(f"Auto-registered {len(decorated_tools)} decorated tools")
            
        except Exception as e:
            logger.error(f"Failed to discover decorated tools: {e}")


# Global registry instance
_global_registry: Optional[CapabilityRegistry] = None


def get_capability_registry() -> CapabilityRegistry:
    """
    Get global capability registry (singleton).
    
    Returns:
        Global CapabilityRegistry instance
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = CapabilityRegistry()
        _global_registry.discover_all()
    return _global_registry
