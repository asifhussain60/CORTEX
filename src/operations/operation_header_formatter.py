"""
CORTEX Operation Header Formatter

Provides standardized headers and footers for all CORTEX operation orchestrators.
Ensures consistent branding, copyright attribution, and execution context display.

Consolidates functionality from header_formatter.py and header_utils.py

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from datetime import datetime
from typing import Literal, Optional, List


class OperationHeaderFormatter:
    """Format headers and footers for CORTEX operation orchestrators."""
    
    @staticmethod
    def format_minimalist(
        operation_name: str,
        version: str,
        profile: str,
        mode: Literal["LIVE", "DRY RUN"] = "LIVE",
        timestamp: Optional[datetime] = None,
        purpose: Optional[str] = None
    ) -> str:
        """
        Format minimalist header for operations.
        
        Used for: cleanup, optimization, design sync, story refresh, etc.
        
        Args:
            operation_name: Name of the operation (e.g., "Design Sync")
            version: Version string (e.g., "1.0.0")
            profile: Execution profile (e.g., "comprehensive")
            mode: Execution mode ("LIVE" or "DRY RUN")
            timestamp: Execution start time (defaults to now)
            purpose: Optional 1-2 line description of operation purpose
        
        Returns:
            Formatted header string
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        ts_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        
        lines = [
            "",
            "━" * 80,
            f"  CORTEX {operation_name} Orchestrator v{version}",
            "━" * 80,
            "",
            f"Profile: {profile}  │  Mode: {mode}  │  Started: {ts_str}"
        ]
        
        # Add purpose if provided
        if purpose:
            lines.append("")
            lines.append(f"📋 Purpose: {purpose}")
        
        lines.extend([
            "",
            "© 2024-2025 Asif Hussain │ Proprietary │ github.com/asifhussain60/CORTEX",
            "━" * 80,
            ""
        ])
        
        return "\n".join(lines)
    
    @staticmethod
    def format_banner(
        operation_name: str,
        version: str,
        profile: str,
        mode: Literal["LIVE", "DRY RUN"] = "LIVE",
        timestamp: Optional[datetime] = None
    ) -> str:
        """
        Format banner-style header with ASCII art logo.
        
        Used for: help module and other high-visibility entry points.
        
        Args:
            operation_name: Name of the operation (e.g., "Help System")
            version: Version string (e.g., "1.0.0")
            profile: Execution profile (e.g., "standard")
            mode: Execution mode ("LIVE" or "DRY RUN")
            timestamp: Execution start time (defaults to now)
        
        Returns:
            Formatted banner header string
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        ts_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        
        # Pad operation name and version to fit box width
        name_version = f"{operation_name} v{version}"
        padded_name = name_version.ljust(53)
        
        return f"""╔═══════════════════════════════════════════════════════════════════════════╗
║  ██████╗ ██████╗ ██████╗ ████████╗███████╗██╗  ██╗                       ║
║ ██╔════╝██╔═══██╗██╔══██╗╚══██╔══╝██╔════╝╚██╗██╔╝                       ║
║ ██║     ██║   ██║██████╔╝   ██║   █████╗   ╚███╔╝                        ║
║ ██║     ██║   ██║██╔══██╗   ██║   ██╔══╝   ██╔██╗                        ║
║ ╚██████╗╚██████╔╝██║  ██║   ██║   ███████╗██╔╝ ██╗                       ║
║  ╚═════╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝                       ║
║                    {padded_name}║
╠═══════════════════════════════════════════════════════════════════════════╣
║  Profile: {profile:<15} │  Mode: {mode:<6} │  Started: {ts_str}  ║
╠═══════════════════════════════════════════════════════════════════════════╣
║  © 2024-2025 Asif Hussain │ Proprietary │ github.com/asifhussain60/CORTEX ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""
    
    @staticmethod
    def format_completion(
        operation_name: str,
        success: bool,
        duration_seconds: float,
        summary: Optional[str] = None,
        accomplishments: Optional[List[str]] = None
    ) -> str:
        """
        Format completion footer.
        
        Args:
            operation_name: Name of the operation
            success: Whether operation succeeded
            duration_seconds: Total execution time in seconds
            summary: Optional single-line summary message
            accomplishments: Optional list of bullet points showing what was done
        
        Returns:
            Formatted completion footer
        """
        status = "✅ COMPLETED" if success else "❌ FAILED"
        duration = f"{duration_seconds:.2f}s"
        
        lines = [
            "",
            "━" * 80,
            f"  {operation_name} {status} │ Duration: {duration}"
        ]
        
        if summary:
            lines.append(f"  {summary}")
        
        # Show accomplishments if provided and successful
        if accomplishments and success:
            lines.append("")
            lines.append("  Accomplishments:")
            for item in accomplishments:
                lines.append(f"    • {item}")
        
        lines.extend([
            "━" * 80,
            ""
        ])
        
        return "\n".join(lines)
    
    # Convenience methods for printing
    
    @staticmethod
    def print_minimalist(
        operation_name: str,
        version: str,
        profile: str,
        mode: Literal["LIVE", "DRY RUN"] = "LIVE",
        timestamp: Optional[datetime] = None,
        purpose: Optional[str] = None
    ) -> None:
        """Print minimalist header directly to console."""
        header = OperationHeaderFormatter.format_minimalist(
            operation_name, version, profile, mode, timestamp, purpose
        )
        # Use UTF-8 encoding for console output
        try:
            print(header)
        except UnicodeEncodeError:
            # Fallback to ASCII if UTF-8 fails
            print(header.encode('ascii', 'replace').decode('ascii'))
    
    @staticmethod
    def print_banner(
        operation_name: str,
        version: str,
        profile: str,
        mode: Literal["LIVE", "DRY RUN"] = "LIVE",
        timestamp: Optional[datetime] = None
    ) -> None:
        """Print banner header directly to console."""
        header = OperationHeaderFormatter.format_banner(
            operation_name, version, profile, mode, timestamp
        )
        print(header)
    
    @staticmethod
    def print_completion(
        operation_name: str,
        success: bool,
        duration_seconds: float,
        summary: Optional[str] = None,
        accomplishments: Optional[List[str]] = None
    ) -> None:
        """Print completion footer directly to console."""
        footer = OperationHeaderFormatter.format_completion(
            operation_name, success, duration_seconds, summary, accomplishments
        )
        print(footer)


# Backward compatibility aliases
HeaderFormatter = OperationHeaderFormatter
format_minimalist_header = OperationHeaderFormatter.format_minimalist
print_minimalist_header = OperationHeaderFormatter.print_minimalist
print_banner_header = OperationHeaderFormatter.print_banner
format_completion_footer = OperationHeaderFormatter.format_completion
print_completion_footer = OperationHeaderFormatter.print_completion
