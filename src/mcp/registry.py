"""
Orchestrator Registry for MCP Server.

Maps orchestrator names to Python classes and configuration files.
Provides discovery, validation, and hot-reload capabilities.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass
from importlib import import_module


logger = logging.getLogger(__name__)


@dataclass
class OrchestratorDefinition:
    """Definition of a registered orchestrator."""
    name: str
    class_name: str
    module_path: str
    config_path: str
    type: str  # "autonomous" or "guided"
    description: Optional[str] = None
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate orchestrator definition.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate type
        if self.type not in ["autonomous", "guided"]:
            return False, f"Invalid type '{self.type}' (must be 'autonomous' or 'guided')"
        
        # Validate config exists
        if not Path(self.config_path).exists():
            return False, f"Config file not found: {self.config_path}"
        
        return True, None


class OrchestratorRegistry:
    """
    Registry for orchestrator discovery and management.
    
    Loads orchestrator definitions from YAML config and provides
    lookup, validation, and instantiation capabilities.
    """
    
    def __init__(self, config_path: str):
        """
        Initialize registry from config file.
        
        Args:
            config_path: Path to mcp-server.yaml config
        """
        self.config_path = config_path
        self.orchestrators: Dict[str, OrchestratorDefinition] = {}
        self._load_config()
    
    def _load_config(self) -> None:
        """Load orchestrator definitions from config file."""
        if not Path(self.config_path).exists():
            logger.warning(f"Config file not found: {self.config_path}")
            return
        
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            if not config or 'orchestrators' not in config:
                logger.warning(f"No orchestrators defined in {self.config_path}")
                return
            
            for name, definition in config['orchestrators'].items():
                try:
                    orch_def = OrchestratorDefinition(
                        name=name,
                        class_name=definition['class'],
                        module_path=definition['module'],
                        config_path=definition['config'],
                        type=definition['type'],
                        description=definition.get('description')
                    )
                    
                    # Validate definition
                    is_valid, error = orch_def.validate()
                    if not is_valid:
                        logger.error(f"Invalid orchestrator '{name}': {error}")
                        continue
                    
                    self.orchestrators[name] = orch_def
                    logger.info(f"Registered orchestrator: {name} ({orch_def.type})")
                    
                except KeyError as e:
                    logger.error(f"Missing required field in orchestrator '{name}': {e}")
                except Exception as e:
                    logger.error(f"Error loading orchestrator '{name}': {e}")
        
        except Exception as e:
            logger.error(f"Error loading config {self.config_path}: {e}")
    
    def get(self, name: str) -> Optional[OrchestratorDefinition]:
        """
        Get orchestrator definition by name.
        
        Args:
            name: Orchestrator name
            
        Returns:
            OrchestratorDefinition or None if not found
        """
        return self.orchestrators.get(name)
    
    def list_orchestrators(self) -> list[str]:
        """
        Get list of registered orchestrator names.
        
        Returns:
            List of orchestrator names
        """
        return list(self.orchestrators.keys())
    
    def list_by_type(self, orch_type: str) -> list[str]:
        """
        Get orchestrators by type.
        
        Args:
            orch_type: "autonomous" or "guided"
            
        Returns:
            List of orchestrator names matching type
        """
        return [
            name for name, definition in self.orchestrators.items()
            if definition.type == orch_type
        ]
    
    def exists(self, name: str) -> bool:
        """
        Check if orchestrator is registered.
        
        Args:
            name: Orchestrator name
            
        Returns:
            True if registered
        """
        return name in self.orchestrators
    
    def instantiate(self, name: str) -> Optional[Any]:
        """
        Instantiate an orchestrator by name.
        
        Args:
            name: Orchestrator name
            
        Returns:
            Orchestrator instance or None if failed
        """
        definition = self.get(name)
        if not definition:
            logger.error(f"Orchestrator '{name}' not registered")
            return None
        
        try:
            # Import module
            module = import_module(definition.module_path)
            
            # Get class
            orchestrator_class = getattr(module, definition.class_name)
            
            # Instantiate with config
            instance = orchestrator_class(config_path=definition.config_path)
            
            logger.info(f"Instantiated orchestrator: {name}")
            return instance
            
        except ImportError as e:
            logger.error(f"Cannot import module '{definition.module_path}': {e}")
            return None
        except AttributeError as e:
            logger.error(
                f"Class '{definition.class_name}' not found in module "
                f"'{definition.module_path}': {e}"
            )
            return None
        except Exception as e:
            logger.error(f"Error instantiating orchestrator '{name}': {e}")
            return None
    
    def reload(self) -> None:
        """Reload registry from config file (hot-reload)."""
        logger.info("Reloading orchestrator registry...")
        self.orchestrators.clear()
        self._load_config()
        logger.info(f"Registry reloaded: {len(self.orchestrators)} orchestrators")
    
    def validate_all(self) -> Dict[str, tuple[bool, Optional[str]]]:
        """
        Validate all registered orchestrators.
        
        Returns:
            Dictionary mapping orchestrator names to (is_valid, error_message)
        """
        results = {}
        for name, definition in self.orchestrators.items():
            results[name] = definition.validate()
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get registry statistics.
        
        Returns:
            Dictionary with counts and breakdown
        """
        autonomous = self.list_by_type("autonomous")
        guided = self.list_by_type("guided")
        
        return {
            "total": len(self.orchestrators),
            "autonomous": len(autonomous),
            "guided": len(guided),
            "orchestrators": {
                "autonomous": autonomous,
                "guided": guided
            }
        }
