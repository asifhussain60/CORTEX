"""
CORTEX Brain Transfer Plugin

Registers brain export/import commands with CORTEX plugin system.
Enables natural language access: "export brain", "import brain"

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from typing import Dict, Any, List
from pathlib import Path
import logging

# Import plugin base if available
try:
    from src.plugins.base_plugin import BasePlugin
    from src.plugins.command_registry import CommandMetadata, CommandCategory
except ImportError:
    # Fallback for standalone usage
    BasePlugin = object
    CommandMetadata = None
    CommandCategory = None

from .cli import handle_export_brain_request, handle_import_brain_request

logger = logging.getLogger(__name__)


class BrainTransferPlugin(BasePlugin if BasePlugin != object else object):
    """
    Brain Transfer Plugin for CORTEX.
    
    Provides:
    - Export brain patterns to YAML
    - Import brain patterns from YAML
    - Intelligent conflict resolution
    - Namespace-aware merging
    """
    
    def __init__(self):
        """Initialize brain transfer plugin."""
        if BasePlugin != object:
            super().__init__()
    
    def _get_metadata(self):
        """Return plugin metadata."""
        if BasePlugin == object:
            return None
        
        from src.plugins.base_plugin import PluginMetadata, PluginCategory, PluginPriority, HookPoint
        
        return PluginMetadata(
            plugin_id="brain_transfer",
            name="Brain Transfer",
            version="1.0.0",
            category=PluginCategory.MAINTENANCE,
            priority=PluginPriority.MEDIUM,
            description="Export and import brain patterns across CORTEX instances",
            author="Asif Hussain",
            dependencies=[],
            hooks=[HookPoint.ON_BRAIN_UPDATE.value],
            config_schema={},
            natural_language_patterns=self.get_natural_language_patterns()
        )
    
    def initialize(self) -> bool:
        """Initialize plugin resources."""
        # Validate cortex-brain directory exists
        try:
            current = Path(__file__).resolve()
            for parent in current.parents:
                brain_path = parent / "cortex-brain"
                if brain_path.exists():
                    return True
            logger.warning("cortex-brain directory not found")
            return False
        except Exception as e:
            logger.error(f"Brain transfer initialization failed: {e}")
            return False
    
    def get_natural_language_patterns(self) -> List[str]:
        """
        Natural language patterns this plugin handles.
        
        Returns:
            List of trigger patterns
        """
        return [
            "export brain",
            "share my knowledge",
            "export patterns",
            "export learned knowledge",
            "save brain state",
            "import brain",
            "load knowledge",
            "import patterns",
            "merge brain",
            "sync brain"
        ]
    
    def register_commands(self) -> List[Any]:
        """
        Register slash commands with command registry.
        
        Returns:
            List of CommandMetadata objects
        """
        if CommandMetadata is None:
            return []
        
        # Export brain command
        export_cmd = CommandMetadata(
            command="/export-brain",
            natural_language_equivalent="export brain",
            plugin_id="brain_transfer",
            description="Export learned patterns to YAML for sharing",
            category=CommandCategory.MAINTENANCE,
            aliases=["/export", "/share-brain"],
            examples=[
                "/export-brain",
                "/export-brain workspace",
                "/export-brain all"
            ],
            requires_online=False
        )
        
        # Import brain command
        import_cmd = CommandMetadata(
            command="/import-brain",
            natural_language_equivalent="import brain",
            plugin_id="brain_transfer",
            description="Import patterns from YAML with intelligent merging",
            category=CommandCategory.MAINTENANCE,
            aliases=["/import", "/load-brain"],
            examples=[
                "/import-brain brain-export-20251117.yaml",
                "/import-brain"
            ],
            requires_online=False
        )
        
        return [export_cmd, import_cmd]
    
    def execute(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute brain transfer operation.
        
        Args:
            request: Natural language request
            context: Execution context
        
        Returns:
            Operation result
        """
        request_lower = request.lower()
        
        # Determine operation type
        if any(word in request_lower for word in ["export", "share", "save"]):
            return handle_export_brain_request(request, context)
        
        elif any(word in request_lower for word in ["import", "load", "merge", "sync"]):
            return handle_import_brain_request(request, context)
        
        else:
            return {
                "success": False,
                "error": "Unknown brain transfer operation",
                "message": "❌ Please specify 'export brain' or 'import brain'"
            }
    
    def validate(self, context: Dict[str, Any]) -> bool:
        """
        Validate brain transfer can execute.
        
        Args:
            context: Execution context
        
        Returns:
            True if valid, False otherwise
        """
        # Check if cortex-brain directory exists
        try:
            current = Path(__file__).resolve()
            for parent in current.parents:
                brain_path = parent / "cortex-brain"
                if brain_path.exists():
                    return True
            return False
        except Exception as e:
            logger.error(f"Brain transfer validation failed: {e}")
            return False
    
    def cleanup(self):
        """Cleanup after execution (no-op for brain transfer)."""
        pass


# Plugin instance for registration
plugin = BrainTransferPlugin()


def register_plugin(registry=None):
    """
    Register brain transfer plugin with CORTEX.
    
    Args:
        registry: Optional command registry
    
    Returns:
        Plugin instance
    """
    if registry:
        plugin.register_commands(registry)
    return plugin
