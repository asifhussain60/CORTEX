"""
CORTEX Orchestrator Header Utilities

Provides standardized copyright headers for all CORTEX entry point orchestrators.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from datetime import datetime
from typing import Optional


def format_minimalist_header(
    operation_name: str,
    version: str,
    profile: str,
    mode: str,
    purpose: Optional[str] = None
) -> str:
    """
    Format minimalist header (Option C) for orchestrators.
    
    Returns the header as a string instead of printing.
    
    Args:
        operation_name: Name of the operation (e.g., "Design Sync")
        version: Version number (e.g., "1.0.0")
        profile: Execution profile (e.g., "comprehensive")
        mode: Execution mode description (always "LIVE EXECUTION")
        purpose: Optional 1-2 line description of what will be accomplished
    
    Returns:
        Formatted header string
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    lines = [
        "",
        "━" * 80,
        f"  CORTEX {operation_name} Orchestrator v{version}",
        "━" * 80,
        "",
        f"Profile: {profile}  │  Mode: {mode}  │  Started: {timestamp}"
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


def print_minimalist_header(
    operation_name: str,
    version: str,
    profile: str,
    mode: str,
    purpose: Optional[str] = None
) -> None:
    """
    Print minimalist header (Option C) for orchestrators.
    
    Args:
        operation_name: Name of the operation (e.g., "Design Sync")
        version: Version number (e.g., "1.0.0")
        profile: Execution profile (e.g., "comprehensive")
        mode: Execution mode description (always "LIVE EXECUTION")
        purpose: Optional 1-2 line description of what will be accomplished
    """
    header = format_minimalist_header(
        operation_name, version, profile, mode, purpose
    )
    print(header)


def print_banner_header(
    operation_name: str,
    version: str,
    profile: str
) -> None:
    """
    Print banner-style header (Option D) for help module.
    
    Args:
        operation_name: Name of the operation (e.g., "Help System")
        version: Version number (e.g., "1.0.0")
        profile: Execution profile
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print("\n╔═══════════════════════════════════════════════════════════════════════════╗")
    print("║  ██████╗ ██████╗ ██████╗ ████████╗███████╗██╗  ██╗                       ║")
    print("║ ██╔════╝██╔═══██╗██╔══██╗╚══██╔══╝██╔════╝╚██╗██╔╝                       ║")
    print("║ ██║     ██║   ██║██████╔╝   ██║   █████╗   ╚███╔╝                        ║")
    print("║ ██║     ██║   ██║██╔══██╗   ██║   ██╔══╝   ██╔██╗                        ║")
    print("║ ╚██████╗╚██████╔╝██║  ██║   ██║   ███████╗██╔╝ ██╗                       ║")
    print("║  ╚═════╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝                       ║")
    print(f"║                    {operation_name} v{version:<39} ║")
    print("╠═══════════════════════════════════════════════════════════════════════════╣")
    print(f"║  Profile: {profile:<15} │  Mode: LIVE    │  Started: {timestamp}  ║")
    print("╠═══════════════════════════════════════════════════════════════════════════╣")
    print("║  © 2024-2025 Asif Hussain │ Proprietary │ github.com/asifhussain60/CORTEX ║")
    print("╚═══════════════════════════════════════════════════════════════════════════╝")
    print()


def format_completion_footer(
    operation_name: str,
    success: bool,
    duration_seconds: float,
    summary: Optional[str] = None,
    accomplishments: Optional[list] = None
) -> str:
    """
    Format completion footer for orchestrators.
    
    Returns the footer as a string instead of printing.
    
    Args:
        operation_name: Name of the operation
        success: Whether operation succeeded
        duration_seconds: Execution duration
        summary: Optional summary message (single line)
        accomplishments: Optional list of bullet points showing what was done
    
    Returns:
        Formatted footer string
    """
    status = "✅ COMPLETED" if success else "❌ FAILED"
    
    lines = [
        "",
        "━" * 80,
        f"  {operation_name} {status} in {duration_seconds:.1f}s"
    ]
    
    if summary:
        lines.append(f"  {summary}")
    
    # Show accomplishments if provided
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


def print_completion_footer(
    operation_name: str,
    success: bool,
    duration_seconds: float,
    summary: Optional[str] = None,
    accomplishments: Optional[list] = None
) -> None:
    """
    Print completion footer for orchestrators.
    
    Args:
        operation_name: Name of the operation
        success: Whether operation succeeded
        duration_seconds: Execution duration
        summary: Optional summary message (single line)
        accomplishments: Optional list of bullet points showing what was done
    """
    footer = format_completion_footer(
        operation_name, success, duration_seconds, summary, accomplishments
    )
    print(footer)
