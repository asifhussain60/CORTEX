"""
CORTEX Orchestrator Header Utilities

Provides standardized copyright headers for all CORTEX entry point orchestrators.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from datetime import datetime
from typing import Optional


def print_minimalist_header(
    operation_name: str,
    version: str,
    profile: str,
    mode: str,
    dry_run: bool = False
) -> None:
    """
    Print minimalist header (Option C) for orchestrators.
    
    Args:
        operation_name: Name of the operation (e.g., "Design Sync")
        version: Version number (e.g., "1.0.0")
        profile: Execution profile (e.g., "comprehensive")
        mode: Execution mode description
        dry_run: Whether in dry-run mode
    """
    mode_str = "DRY RUN (Preview Only)" if dry_run else mode
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print("\n" + "━" * 80)
    print(f"  CORTEX {operation_name} Orchestrator v{version}")
    print("━" * 80)
    print()
    print(f"Profile: {profile}  │  Mode: {mode_str}  │  Started: {timestamp}")
    print()
    print("© 2024-2025 Asif Hussain │ Proprietary │ github.com/asifhussain60/CORTEX")
    print("━" * 80)
    print()


def print_banner_header(
    operation_name: str,
    version: str,
    profile: str,
    mode: str,
    dry_run: bool = False
) -> None:
    """
    Print banner-style header (Option D) for help module.
    
    Args:
        operation_name: Name of the operation (e.g., "Help System")
        version: Version number (e.g., "1.0.0")
        profile: Execution profile
        mode: Execution mode description
        dry_run: Whether in dry-run mode
    """
    mode_str = "DRY RUN" if dry_run else "LIVE"
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
    print(f"║  Profile: {profile:<15} │  Mode: {mode_str:<6} │  Started: {timestamp}  ║")
    print("╠═══════════════════════════════════════════════════════════════════════════╣")
    print("║  © 2024-2025 Asif Hussain │ Proprietary │ github.com/asifhussain60/CORTEX ║")
    print("╚═══════════════════════════════════════════════════════════════════════════╝")
    print()


def print_completion_footer(
    operation_name: str,
    success: bool,
    duration_seconds: float,
    summary: Optional[str] = None
) -> None:
    """
    Print completion footer for orchestrators.
    
    Args:
        operation_name: Name of the operation
        success: Whether operation succeeded
        duration_seconds: Execution duration
        summary: Optional summary message
    """
    status = "✅ COMPLETED" if success else "❌ FAILED"
    
    print()
    print("━" * 80)
    print(f"  {operation_name} {status} in {duration_seconds:.1f}s")
    if summary:
        print(f"  {summary}")
    print("━" * 80)
    print()
