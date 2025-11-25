"""
CORTEX Help Command - Display Available Operations

Provides concise, user-friendly display of all CORTEX operations with:
    - Quick command reference
    - Natural language examples
    - Implementation status
    - Underlying orchestration modules

Author: Asif Hussain
Version: 1.0
"""

import logging
from typing import Dict, List, Tuple, Any
from pathlib import Path
from src.operations.operation_factory import OperationFactory

logger = logging.getLogger(__name__)


class HelpCommand:
    """
    Generate help text for CORTEX operations.
    
    Displays:
        - Quick commands (shortest natural language phrase)
        - Natural language example (most common usage)
        - Orchestration module (operation_id)
        - Status (✅ ready, ⏸️ pending, 🎯 planned)
    """
    
    def __init__(self, factory: OperationFactory = None):
        """
        Initialize help command.
        
        Args:
            factory: Operation factory (auto-created if None)
        """
        self.factory = factory or OperationFactory()
    
    def generate_help(self, format: str = 'table') -> str:
        """
        Generate help text for all CORTEX operations.
        
        Args:
            format: Output format ('table', 'list', 'detailed')
        
        Returns:
            Formatted help text
        """
        operations = self._gather_operation_data()
        
        if format == 'table':
            return self._format_as_table(operations)
        elif format == 'list':
            return self._format_as_list(operations)
        elif format == 'detailed':
            return self._format_detailed(operations)
        else:
            return self._format_as_table(operations)
    
    def _gather_operation_data(self) -> List[Dict[str, Any]]:
        """
        Gather data for all operations.
        
        Returns:
            List of operation data dictionaries
        """
        operations_data = []
        
        for op_id in self.factory.get_available_operations():
            op_info = self.factory.get_operation_info(op_id)
            if not op_info:
                continue
            
            # Extract shortest natural language phrase as "quick command"
            natural_lang = op_info.get('natural_language', [])
            quick_cmd = min(natural_lang, key=len) if natural_lang else op_id
            
            # Get example natural language phrase (longest or most descriptive)
            example = max(natural_lang, key=len) if natural_lang else quick_cmd
            
            # Determine status
            status = self._determine_status(op_id, op_info)
            
            # Get module count
            modules = op_info.get('modules', [])
            module_count = len(modules)
            
            operations_data.append({
                'quick_cmd': quick_cmd,
                'example': example,
                'operation_id': op_id,
                'operation_name': op_info.get('name', op_id),
                'status': status,
                'status_icon': self._get_status_icon(status),
                'module_count': module_count,
                'category': op_info.get('category', 'other'),
                'slash_command': op_info.get('slash_command', ''),
            })
        
        # Sort alphabetically by quick command
        operations_data.sort(key=lambda x: x['quick_cmd'].lower())
        
        return operations_data
    
    def _determine_status(self, op_id: str, op_info: Dict[str, Any]) -> str:
        """
        Determine operation implementation status.
        
        Args:
            op_id: Operation identifier
            op_info: Operation configuration
        
        Returns:
            Status string: 'ready', 'pending', 'planned'
        """
        # Check explicit status field
        explicit_status = op_info.get('status', '').lower()
        if explicit_status == 'pending':
            return 'planned'
        
        # Check module implementation status
        modules = op_info.get('modules', [])
        if not modules:
            return 'pending'
        
        # Get module definitions from config
        all_modules = self.factory.config.get('modules', {})
        
        implemented_count = 0
        for module_id in modules:
            module_def = all_modules.get(module_id, {})
            if module_def.get('status') == 'implemented':
                implemented_count += 1
        
        # Determine overall status
        if implemented_count == len(modules):
            return 'ready'
        elif implemented_count > 0:
            return 'partial'
        else:
            return 'pending'
    
    def _get_status_icon(self, status: str) -> str:
        """Get visual icon for status."""
        icons = {
            'ready': '✅',
            'partial': '🔄',
            'pending': '⏸️',
            'planned': '🎯'
        }
        return icons.get(status, '❓')
    
    def _format_as_table(self, operations: List[Dict[str, Any]]) -> str:
        """
        Format operations as a table.
        
        Args:
            operations: List of operation data
        
        Returns:
            Formatted table string
        """
        lines = []
        lines.append("")
        lines.append("=" * 90)
        lines.append("CORTEX COMMANDS")
        lines.append("=" * 90)
        lines.append("")
        
        # Table header
        lines.append(f"{'Status':<8} {'Quick Command':<20} {'Natural Language Example':<35} {'Module':<20}")
        lines.append("-" * 90)
        
        # Table rows
        for op in operations:
            status = f"{op['status_icon']} {op['status'][:4]}"
            quick = op['quick_cmd'][:18]
            example = op['example'][:33]
            module = op['operation_id'][:18]
            
            lines.append(f"{status:<8} {quick:<20} {example:<35} {module:<20}")
        
        lines.append("-" * 90)
        lines.append("")
        lines.append("Legend:")
        lines.append("  ✅ ready    - Fully implemented and tested")
        lines.append("  🔄 partial  - Partially implemented (some modules ready)")
        lines.append("  ⏸️ pending  - Architecture ready, implementation pending")
        lines.append("  🎯 planned  - Design phase, CORTEX 2.1+")
        lines.append("")
        lines.append("Usage:")
        lines.append("  Natural language:  'setup environment' or 'refresh story'")
        lines.append("  Slash commands:    /setup or /CORTEX, refresh cortex story")
        lines.append("  Programmatic:      execute_operation('environment_setup')")
        lines.append("")
        lines.append("=" * 90)
        
        return "\n".join(lines)
    
    def _format_as_list(self, operations: List[Dict[str, Any]]) -> str:
        """Format operations as a bulleted list."""
        lines = []
        lines.append("\nCORTEX COMMANDS:\n")
        
        for op in operations:
            lines.append(f"{op['status_icon']} {op['quick_cmd']}")
            lines.append(f"   Example: {op['example']}")
            lines.append(f"   Module: {op['operation_id']} ({op['module_count']} modules)")
            lines.append("")
        
        return "\n".join(lines)
    
    def _format_detailed(self, operations: List[Dict[str, Any]]) -> str:
        """Format operations with detailed information."""
        lines = []
        lines.append("\n" + "=" * 90)
        lines.append("CORTEX COMMANDS - DETAILED")
        lines.append("=" * 90 + "\n")
        
        # Group by category
        by_category: Dict[str, List[Dict[str, Any]]] = {}
        for op in operations:
            category = op['category']
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(op)
        
        for category, ops in sorted(by_category.items()):
            lines.append(f"\n{category.upper()}:")
            lines.append("-" * 90)
            
            for op in ops:
                lines.append(f"\n{op['status_icon']} {op['operation_name']}")
                lines.append(f"   Quick:      {op['quick_cmd']}")
                lines.append(f"   Example:    {op['example']}")
                lines.append(f"   Module:     {op['operation_id']}")
                lines.append(f"   Status:     {op['status']}")
                lines.append(f"   Modules:    {op['module_count']} modules")
                if op['slash_command']:
                    lines.append(f"   Command:    {op['slash_command']}")
        
        lines.append("\n" + "=" * 90 + "\n")
        
        return "\n".join(lines)
    
    def get_operation_by_command(self, command: str) -> Dict[str, Any]:
        """
        Find operation by quick command.
        
        Args:
            command: Quick command string
        
        Returns:
            Operation data dictionary
        """
        operations = self._gather_operation_data()
        
        command_lower = command.lower().strip()
        for op in operations:
            if op['quick_cmd'].lower() == command_lower:
                return op
        
        return {}


def show_help(format: str = 'table') -> str:
    """
    Convenience function to display CORTEX help.
    
    Args:
        format: Output format ('table', 'list', 'detailed')
    
    Returns:
        Formatted help text
    
    Example:
        print(show_help())
        print(show_help('detailed'))
    """
    help_cmd = HelpCommand()
    return help_cmd.generate_help(format)


def find_command(command: str) -> Dict[str, Any]:
    """
    Find operation by command.
    
    Args:
        command: Command string to search for
    
    Returns:
        Operation data dictionary
    
    Example:
        op = find_command('setup')
        print(f"Operation: {op['operation_id']}")
    """
    help_cmd = HelpCommand()
    return help_cmd.get_operation_by_command(command)


# Allow direct execution for testing
if __name__ == "__main__":
    print(show_help('table'))
