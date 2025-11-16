"""
CORTEX Orchestrator Header Formatter

Provides standardized headers for all CORTEX entry point orchestrators.
Ensures consistent branding, copyright attribution, and execution context display.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from datetime import datetime
from typing import Literal


class HeaderFormatter:
    """Format headers for CORTEX orchestrators."""
    
    @staticmethod
    def format_minimalist(
        operation_name: str,
        version: str,
        profile: str,
        mode: Literal["LIVE", "DRY RUN"],
        timestamp: datetime = None
    ) -> str:
        """
        Format minimalist header (Option C).
        
        Used for: cleanup, optimization, design sync, story refresh, etc.
        
        Args:
            operation_name: Name of the operation (e.g., "Design Sync")
            version: Version string (e.g., "1.0.0")
            profile: Execution profile (e.g., "comprehensive")
            mode: Execution mode ("LIVE" or "DRY RUN")
            timestamp: Execution start time (defaults to now)
        
        Returns:
            Formatted header string
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        ts_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        
        return f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CORTEX {operation_name} Orchestrator v{version}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Profile: {profile}  │  Mode: {mode}  │  Started: {ts_str}

© 2024-2025 Asif Hussain │ Proprietary │ github.com/asifhussain60/CORTEX
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    @staticmethod
    def format_banner(
        operation_name: str,
        version: str,
        profile: str,
        mode: Literal["LIVE", "DRY RUN"],
        timestamp: datetime = None
    ) -> str:
        """
        Format banner-style header (Option D).
        
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
        
        return f"""╔═══════════════════════════════════════════════════════════════════════════╗
║  ██████╗ ██████╗ ██████╗ ████████╗███████╗██╗  ██╗                       ║
║ ██╔════╝██╔═══██╗██╔══██╗╚══██╔══╝██╔════╝╚██╗██╔╝                       ║
║ ██║     ██║   ██║██████╔╝   ██║   █████╗   ╚███╔╝                        ║
║ ██║     ██║   ██║██╔══██╗   ██║   ██╔══╝   ██╔██╗                        ║
║ ╚██████╗╚██████╔╝██║  ██║   ██║   ███████╗██╔╝ ██╗                       ║
║  ╚═════╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝                       ║
║                    {operation_name} v{version:<28}║
╠═══════════════════════════════════════════════════════════════════════════╣
║  Profile: {profile:<15} │  Mode: {mode:<6} │  Started: {ts_str}  ║
╠═══════════════════════════════════════════════════════════════════════════╣
║  © 2024-2025 Asif Hussain │ Proprietary │ github.com/asifhussain60/CORTEX ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""
    
    @staticmethod
    def format_completion(
        success: bool,
        duration_seconds: float,
        summary: str = None
    ) -> str:
        """
        Format completion footer.
        
        Args:
            success: Whether operation succeeded
            duration_seconds: Total execution time
            summary: Optional summary message
        
        Returns:
            Formatted completion footer
        """
        status = "✅ COMPLETED" if success else "❌ FAILED"
        duration = f"{duration_seconds:.2f}s"
        
        footer = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{status} │ Duration: {duration}"""
        
        if summary:
            footer += f"\n{summary}"
        
        footer += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        return footer
