"""
CORTEX Response Formatter

Automatically formats operation results with appropriate copyright headers
based on execution context. This ensures consistent branding and legal
attribution without requiring user intervention.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path


class ResponseFormatter:
    """
    Intelligent response formatter that adapts headers based on context.
    
    Header Strategy:
    - First operation in session: Full header
    - Help/documentation: Banner header (ASCII art)
    - Regular operations: Minimal footer
    - Error situations: No header (focus on problem)
    """
    
    # Track if this is first operation in session (per-instance)
    _first_operation_shown = False
    
    @staticmethod
    def format_operation_result(
        operation_name: str,
        result: Any,
        context: Dict[str, Any],
        is_help: bool = False
    ) -> str:
        """
        Format operation result with appropriate header.
        
        Args:
            operation_name: Name of the operation (e.g., "Design Sync")
            result: OperationResult object
            context: Execution context
            is_help: Whether this is a help command
            
        Returns:
            Formatted markdown string for Copilot Chat display
        """
        # Determine header style
        if is_help:
            header = ResponseFormatter._format_banner_header(operation_name, context)
        elif not ResponseFormatter._first_operation_shown:
            header = ResponseFormatter._format_full_header(operation_name, context)
            ResponseFormatter._first_operation_shown = True
        else:
            header = ""  # No header for subsequent operations
        
        # Format main content
        content = ResponseFormatter._format_content(operation_name, result, context)
        
        # Add minimal footer (always present for copyright)
        footer = ResponseFormatter._format_minimal_footer(operation_name, result)
        
        return f"{header}\n{content}\n{footer}".strip()
    
    @staticmethod
    def _format_banner_header(operation_name: str, context: Dict[str, Any]) -> str:
        """Format banner-style header (Option D) for help commands."""
        profile = context.get('profile', 'standard')
        mode = "LIVE" if not context.get('dry_run', False) else "DRY RUN"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        version = context.get('version', '1.0.0')
        
        return f"""
╔═══════════════════════════════════════════════════════════════════════════╗
║  ██████╗ ██████╗ ██████╗ ████████╗███████╗██╗  ██╗                       ║
║ ██╔════╝██╔═══██╗██╔══██╗╚══██╔══╝██╔════╝╚██╗██╔╝                       ║
║ ██║     ██║   ██║██████╔╝   ██║   █████╗   ╚███╔╝                        ║
║ ██║     ██║   ██║██╔══██╗   ██║   ██╔══╝   ██╔██╗                        ║
║ ╚██████╗╚██████╔╝██║  ██║   ██║   ███████╗██╔╝ ██╗                       ║
║  ╚═════╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝                       ║
║                    {operation_name} v{version:<39} ║
╠═══════════════════════════════════════════════════════════════════════════╣
║  Profile: {profile:<15} │  Mode: {mode:<6} │  Started: {timestamp}  ║
╠═══════════════════════════════════════════════════════════════════════════╣
║  © 2024-2025 Asif Hussain │ Proprietary │ github.com/asifhussain60/CORTEX ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""
    
    @staticmethod
    def _format_full_header(operation_name: str, context: Dict[str, Any]) -> str:
        """Format full header (Option C) for first operation."""
        profile = context.get('profile', 'standard')
        mode = "DRY RUN (Preview Only)" if context.get('dry_run', False) else "LIVE EXECUTION"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        version = context.get('version', '1.0.0')
        
        return f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CORTEX {operation_name} Orchestrator v{version}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Profile: {profile}  │  Mode: {mode}  │  Started: {timestamp}

© 2024-2025 Asif Hussain │ Proprietary │ github.com/asifhussain60/CORTEX
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    @staticmethod
    def _format_minimal_footer(operation_name: str, result: Any) -> str:
        """Format minimal footer (always present for copyright)."""
        if not result:
            return "\n---\n*© 2024-2025 Asif Hussain | CORTEX 2.0*"
        
        success = getattr(result, 'success', False)
        duration = getattr(result, 'total_duration_seconds', None)
        
        status_icon = "✅" if success else "❌"
        status_text = "COMPLETED" if success else "FAILED"
        
        duration_text = f" ({duration:.1f}s)" if duration else ""
        
        return f"""
---
*{status_icon} {operation_name} {status_text}{duration_text} | © 2024-2025 Asif Hussain | CORTEX 2.0*
"""
    
    @staticmethod
    def _format_content(operation_name: str, result: Any, context: Dict[str, Any]) -> str:
        """Format the main content based on operation type."""
        if not result:
            return "No result data available."
        
        # Extract key information
        success = getattr(result, 'success', False)
        message = getattr(result, 'message', 'Operation completed')
        data = getattr(result, 'data', {})
        
        content_parts = [f"# {operation_name} Results\n"]
        
        # Add status
        status_icon = "✅" if success else "❌"
        content_parts.append(f"{status_icon} **Status:** {message}\n")
        
        # Format data based on operation type
        if operation_name == "Design Sync":
            content_parts.append(ResponseFormatter._format_design_sync_data(data))
        elif operation_name == "Cleanup":
            content_parts.append(ResponseFormatter._format_cleanup_data(data))
        elif operation_name == "Setup":
            content_parts.append(ResponseFormatter._format_setup_data(data))
        else:
            # Generic formatting
            content_parts.append(ResponseFormatter._format_generic_data(data))
        
        return "\n".join(content_parts)
    
    @staticmethod
    def _format_design_sync_data(data: Dict[str, Any]) -> str:
        """Format Design Sync specific data."""
        if not data:
            return ""
        
        metrics = data.get('metrics', {})
        impl_state = data.get('implementation_state', {})
        
        parts = []
        
        # Implementation discovery
        if impl_state:
            total = impl_state.get('total_modules', 0)
            implemented = impl_state.get('implemented_modules', 0)
            percentage = impl_state.get('completion_percentage', 0)
            tests = impl_state.get('tests', {})
            test_count = sum(tests.values()) if isinstance(tests, dict) else 0
            plugins = len(impl_state.get('plugins', []))
            
            parts.append(f"""
## 📊 Implementation Discovery

- **Modules:** {implemented}/{total} ({percentage:.1f}% complete)
- **Tests:** {test_count:,}
- **Plugins:** {plugins}
""")
        
        # Gap analysis
        if metrics:
            gaps = metrics.get('gaps_analyzed', 0)
            optimizations = metrics.get('optimizations_integrated', 0)
            conversions = metrics.get('md_to_yaml_converted', 0)
            consolidations = metrics.get('status_files_consolidated', 0)
            
            parts.append(f"""
## 🔍 Analysis & Improvements

- **Gaps Identified:** {gaps}
- **Status Files Consolidated:** {consolidations}
- **MD → YAML Conversions:** {conversions}
- **Optimizations Integrated:** {optimizations}
""")
        
        return "\n".join(parts)
    
    @staticmethod
    def _format_cleanup_data(data: Dict[str, Any]) -> str:
        """Format Cleanup specific data."""
        if not data:
            return ""
        
        metrics = data.get('metrics', {})
        if not metrics:
            return ""
        
        backups = metrics.get('backups_deleted', 0)
        files_reorganized = metrics.get('files_reorganized', 0)
        space_freed_mb = metrics.get('space_freed_mb', 0)
        
        return f"""
## 🧹 Cleanup Results

- **Backups Removed:** {backups}
- **Files Reorganized:** {files_reorganized}
- **Space Freed:** {space_freed_mb:.2f} MB
"""
    
    @staticmethod
    def _format_setup_data(data: Dict[str, Any]) -> str:
        """Format Setup specific data."""
        if not data:
            return ""
        
        return """
## ⚙️ Setup Complete

Environment configured successfully.
"""
    
    @staticmethod
    def _format_generic_data(data: Dict[str, Any]) -> str:
        """Generic data formatting."""
        if not data:
            return ""
        
        return f"""
## 📋 Details

```json
{data}
```
"""
    
    @staticmethod
    def reset_session():
        """Reset session state (for testing or explicit session start)."""
        ResponseFormatter._first_operation_shown = False


def format_for_copilot(operation_name: str, result: Any, context: Dict[str, Any] = None) -> str:
    """
    Convenience function to format operation results for Copilot Chat display.
    
    Args:
        operation_name: Name of the operation
        result: OperationResult object
        context: Optional execution context
        
    Returns:
        Formatted markdown string
    """
    if context is None:
        context = {}
    
    # Detect if this is a help operation
    is_help = 'help' in operation_name.lower()
    
    return ResponseFormatter.format_operation_result(
        operation_name=operation_name,
        result=result,
        context=context,
        is_help=is_help
    )
