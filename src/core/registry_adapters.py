"""
Registry Migration Adapters for CORTEX 4.0 Phase 13.5

Provides backward compatibility layer for existing registries to use UnifiedRegistry.
Allows gradual migration without breaking changes.

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
Version: 1.0.0
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from src.core.unified_registry import (
    UnifiedRegistry,
    RegistryItemType,
    get_unified_registry
)

logger = logging.getLogger(__name__)


class CommandRegistryAdapter:
    """
    Adapter for command_registry.py to use UnifiedRegistry.
    
    Provides backward-compatible interface while delegating to UnifiedRegistry.
    """
    
    def __init__(self, unified_registry: Optional[UnifiedRegistry] = None):
        """
        Initialize adapter.
        
        Args:
            unified_registry: UnifiedRegistry instance (creates if None)
        """
        self.registry = unified_registry or get_unified_registry()
    
    def register_command(self, command_metadata: Any) -> bool:
        """
        Register command (backward compatible with CommandMetadata).
        
        Args:
            command_metadata: CommandMetadata object or dict
        
        Returns:
            True if registered successfully
        """
        # Extract data from CommandMetadata
        if hasattr(command_metadata, '__dict__'):
            metadata = command_metadata.__dict__.copy()
            command = metadata.pop('command')
        else:
            metadata = command_metadata.copy()
            command = metadata.pop('command')
        
        # Convert enum to string if present
        if 'category' in metadata and hasattr(metadata['category'], 'value'):
            metadata['category'] = metadata['category'].value
        
        return self.registry.register(
            item_type=RegistryItemType.COMMAND,
            item_id=command,
            metadata=metadata,
            registered_by=metadata.get('plugin_id')
        )
    
    def expand_command(self, command: str) -> Optional[str]:
        """
        Expand command to natural language equivalent.
        
        Args:
            command: Command string (e.g., "/mac")
        
        Returns:
            Natural language equivalent or None
        """
        item = self.registry.get(RegistryItemType.COMMAND, command)
        if item:
            return item.metadata.get('natural_language_equivalent')
        return None
    
    def is_command(self, user_input: str) -> bool:
        """
        Check if user input is a registered command.
        
        Args:
            user_input: Raw user input
        
        Returns:
            True if registered command
        """
        return self.registry.exists(RegistryItemType.COMMAND, user_input.strip())
    
    def get_command_metadata(self, command: str) -> Optional[Dict]:
        """
        Get command metadata.
        
        Args:
            command: Command string
        
        Returns:
            Metadata dictionary or None
        """
        return self.registry.get_metadata(RegistryItemType.COMMAND, command)
    
    def get_all_commands(self) -> List[str]:
        """
        Get all registered commands.
        
        Returns:
            List of command strings
        """
        return self.registry.list_ids(RegistryItemType.COMMAND)
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get registry statistics.
        
        Returns:
            Statistics dictionary
        """
        stats = self.registry.get_stats()
        return {
            'total_commands': stats['items_by_type'].get('command', 0),
            'total_registrations': stats['total_registrations']
        }


class ToolkitRegistryAdapter:
    """
    Adapter for toolkit_registry.py to use UnifiedRegistry.
    
    Provides backward-compatible interface for tool registration.
    """
    
    def __init__(
        self,
        unified_registry: Optional[UnifiedRegistry] = None,
        toolkit_root: Optional[Path] = None
    ):
        """
        Initialize adapter.
        
        Args:
            unified_registry: UnifiedRegistry instance
            toolkit_root: Path to toolkit root (for compatibility)
        """
        self.registry = unified_registry or get_unified_registry()
        self.toolkit_root = toolkit_root
    
    def register_tool(self, tool_name: str, tool_metadata: Dict) -> bool:
        """
        Register tool.
        
        Args:
            tool_name: Tool identifier
            tool_metadata: Tool metadata from manifest
        
        Returns:
            True if registered successfully
        """
        return self.registry.register(
            item_type=RegistryItemType.TOOL,
            item_id=tool_name,
            metadata=tool_metadata,
            registered_by='toolkit'
        )
    
    def get_tool(self, tool_name: str) -> Optional[Dict]:
        """
        Get tool metadata.
        
        Args:
            tool_name: Tool identifier
        
        Returns:
            Tool metadata or None
        """
        return self.registry.get_metadata(RegistryItemType.TOOL, tool_name)
    
    def list_tools(self, category: Optional[str] = None) -> List[Dict]:
        """
        List tools optionally filtered by category.
        
        Args:
            category: Optional category filter
        
        Returns:
            List of tool metadata dictionaries
        """
        if category:
            items = self.registry.list(
                RegistryItemType.TOOL,
                filter_fn=lambda item: item.metadata.get('category') == category
            )
        else:
            items = self.registry.list(RegistryItemType.TOOL)
        
        return [item.metadata for item in items]
    
    def list_categories(self) -> List[str]:
        """
        List all tool categories.
        
        Returns:
            List of category names
        """
        items = self.registry.list(RegistryItemType.TOOL)
        categories = set(
            item.metadata.get('category')
            for item in items
            if item.metadata.get('category')
        )
        return sorted(categories)


class WorkspaceRegistryAdapter:
    """
    Adapter for workspace_registry.py to use UnifiedRegistry.
    
    Note: WorkspaceRegistry has more complex functionality (persistence, UUID generation).
    This adapter provides core registration features while preserving specialized logic.
    """
    
    def __init__(self, unified_registry: Optional[UnifiedRegistry] = None):
        """
        Initialize adapter.
        
        Args:
            unified_registry: UnifiedRegistry instance
        """
        self.registry = unified_registry or get_unified_registry()
    
    def register_workspace(
        self,
        workspace_id: str,
        workspace_info: Dict
    ) -> bool:
        """
        Register workspace.
        
        Args:
            workspace_id: Workspace UUID
            workspace_info: Workspace metadata
        
        Returns:
            True if registered successfully
        """
        return self.registry.register(
            item_type=RegistryItemType.WORKSPACE,
            item_id=workspace_id,
            metadata=workspace_info,
            registered_by='workspace_detector'
        )
    
    def get_workspace(self, workspace_id: str) -> Optional[Dict]:
        """
        Get workspace by ID.
        
        Args:
            workspace_id: Workspace UUID
        
        Returns:
            Workspace metadata or None
        """
        return self.registry.get_metadata(RegistryItemType.WORKSPACE, workspace_id)
    
    def get_workspace_by_path(self, path: str) -> Optional[Dict]:
        """
        Get workspace by path.
        
        Args:
            path: Workspace path
        
        Returns:
            Workspace metadata or None
        """
        items = self.registry.list(
            RegistryItemType.WORKSPACE,
            filter_fn=lambda item: item.metadata.get('path') == path
        )
        return items[0].metadata if items else None
    
    def list_workspaces(self, status: Optional[str] = None) -> List[Dict]:
        """
        List workspaces optionally filtered by status.
        
        Args:
            status: Optional status filter
        
        Returns:
            List of workspace metadata
        """
        if status:
            items = self.registry.list(
                RegistryItemType.WORKSPACE,
                filter_fn=lambda item: item.metadata.get('status') == status
            )
        else:
            items = self.registry.list(RegistryItemType.WORKSPACE)
        
        return [item.metadata for item in items]


def migrate_command_registry_to_unified(
    command_registry: Any,
    unified_registry: UnifiedRegistry
) -> int:
    """
    Migrate existing CommandRegistry to UnifiedRegistry.
    
    Args:
        command_registry: Existing PluginCommandRegistry instance
        unified_registry: Target UnifiedRegistry
    
    Returns:
        Number of commands migrated
    """
    migrated = 0
    
    # Access internal _commands dict
    if hasattr(command_registry, '_commands'):
        for command, metadata in command_registry._commands.items():
            try:
                adapter = CommandRegistryAdapter(unified_registry)
                adapter.register_command(metadata)
                migrated += 1
            except Exception as e:
                logger.error(f"Failed to migrate command {command}: {e}")
    
    logger.info(f"Migrated {migrated} commands to UnifiedRegistry")
    return migrated


def migrate_toolkit_registry_to_unified(
    toolkit_manifest: Dict,
    unified_registry: UnifiedRegistry
) -> int:
    """
    Migrate toolkit manifest to UnifiedRegistry.
    
    Args:
        toolkit_manifest: Toolkit manifest dictionary
        unified_registry: Target UnifiedRegistry
    
    Returns:
        Number of tools migrated
    """
    migrated = 0
    
    if 'categories' in toolkit_manifest:
        for category_data in toolkit_manifest['categories']:
            if 'tools' in category_data:
                for tool in category_data['tools']:
                    try:
                        tool_name = tool['name']
                        # Add category to metadata
                        tool['category'] = category_data['name']
                        
                        adapter = ToolkitRegistryAdapter(unified_registry)
                        adapter.register_tool(tool_name, tool)
                        migrated += 1
                    except Exception as e:
                        logger.error(f"Failed to migrate tool {tool.get('name')}: {e}")
    
    logger.info(f"Migrated {migrated} tools to UnifiedRegistry")
    return migrated


def create_migration_report(unified_registry: UnifiedRegistry) -> Dict[str, Any]:
    """
    Create migration report showing current registry state.
    
    Args:
        unified_registry: UnifiedRegistry instance
    
    Returns:
        Report dictionary
    """
    stats = unified_registry.get_stats()
    
    report = {
        'migration_version': '1.0.0',
        'total_items': stats['total_items'],
        'items_by_type': stats['items_by_type'],
        'statistics': {
            'total_registrations': stats['total_registrations'],
            'total_unregistrations': stats['total_unregistrations'],
            'conflict_detections': stats['conflict_detections'],
            'validation_failures': stats['validation_failures']
        },
        'compatibility': {
            'command_registry_compatible': True,
            'toolkit_registry_compatible': True,
            'workspace_registry_compatible': True
        }
    }
    
    return report
