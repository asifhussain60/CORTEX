"""
Demo Help System Module

Demonstrates CORTEX help command and explains output.

SOLID Principles:
- Single Responsibility: Only handles help system demonstration
- Open/Closed: Extends BaseOperationModule without modifying it
- Dependency Inversion: Depends on BaseOperationModule abstraction

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from typing import Dict, Any, Tuple, List
from datetime import datetime

from src.operations.base_operation_module import (
    BaseOperationModule,
    OperationModuleMetadata,
    OperationResult,
    OperationStatus,
    OperationPhase
)


class DemoHelpSystemModule(BaseOperationModule):
    """
    Demo module for showing CORTEX help system.
    
    Responsibilities:
    1. Execute help command
    2. Display help output
    3. Explain output format
    4. Show how to discover operations
    """
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Return module metadata."""
        return OperationModuleMetadata(
            module_id="demo_help_system",
            name="Demo Help System",
            description="Execute help command and explain output format",
            phase=OperationPhase.PROCESSING,
            priority=10,
            dependencies=[],
            optional=False,
        )
    
    def validate_prerequisites(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate prerequisites for help system demo.
        
        Checks:
        1. Operations system is available
        """
        issues = []
        
        # Check if we can import help command
        try:
            from src.operations import show_help
        except ImportError as e:
            issues.append(f"Help system not available: {e}")
            return False, issues
        
        return True, []
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Execute help system demonstration.
        
        Steps:
        1. Execute help command
        2. Display help output
        3. Explain format and usage
        4. Show example commands
        """
        start_time = datetime.now()
        
        try:
            # Import help command
            from src.operations import show_help
            
            # Execute help command (table format)
            self.log_info("")
            self.log_info("=" * 70)
            self.log_info("📚 CORTEX HELP SYSTEM")
            self.log_info("=" * 70)
            self.log_info("")
            self.log_info("💡 Discovering Available Commands")
            self.log_info("")
            self.log_info("CORTEX provides a help command to show all available operations.")
            self.log_info("You can use either:")
            self.log_info("  • Natural language: 'help' or 'show commands'")
            self.log_info("  • Slash command: '/CORTEX help' or '/help'")
            self.log_info("")
            
            # Generate and display help
            help_output = show_help('table')
            
            self.log_info("Here's the current list of operations:")
            self.log_info("")
            for line in help_output.split('\n'):
                self.log_info(line)
            self.log_info("")
            
            # Explain the output
            explanation = self._build_explanation()
            for line in explanation.split('\n'):
                if line.strip():
                    self.log_info(line)
            
            self.log_info("=" * 70)
            
            # Store help output in context
            context['demo_help_output'] = help_output
            
            duration_seconds = (datetime.now() - start_time).total_seconds()
            
            return OperationResult(
                success=True,
                status=OperationStatus.SUCCESS,
                message="Help system demonstrated successfully",
                data={
                    'help_output': help_output,
                    'explanation': explanation
                },
                duration_seconds=duration_seconds
            )
            
        except Exception as e:
            self.log_error(f"Help system demo failed: {e}")
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Help system demo failed: {str(e)}",
                errors=[str(e)],
                duration_seconds=(datetime.now() - start_time).total_seconds()
            )
    
    def _build_explanation(self) -> str:
        """
        Build explanation of help output format.
        
        Returns:
            Formatted explanation
        """
        lines = []
        
        lines.append("📖 Understanding the Output:")
        lines.append("")
        lines.append("  Status    Quick Command        Natural Language Example")
        lines.append("  ------    --------------       ------------------------")
        lines.append("  ✅ ready  - Fully implemented and tested")
        lines.append("  🔄 part   - Partially implemented (core works)")
        lines.append("  ⏸️ pend   - Architecture ready, modules pending")
        lines.append("  🎯 plan   - Design phase (CORTEX 2.1+)")
        lines.append("")
        lines.append("💬 How to Use:")
        lines.append("")
        lines.append("  1. Natural Language (Recommended):")
        lines.append("     Just describe what you want:")
        lines.append("       • 'setup environment'")
        lines.append("       • 'cleanup workspace'")
        lines.append("       • 'refresh the story'")
        lines.append("")
        lines.append("  2. Quick Commands (Optional):")
        lines.append("     Use the quick command from the table:")
        lines.append("       • 'setup'")
        lines.append("       • 'cleanup'")
        lines.append("       • 'update story'")
        lines.append("")
        lines.append("  3. Slash Commands (Power Users):")
        lines.append("     Use slash notation for speed:")
        lines.append("       • '/setup'")
        lines.append("       • '/cleanup'")
        lines.append("")
        lines.append("✨ Pro Tip: CORTEX understands context!")
        lines.append("  You can say 'continue where we left off' and CORTEX will")
        lines.append("  remember your last conversation and resume work.")
        lines.append("")
        
        return '\n'.join(lines)
