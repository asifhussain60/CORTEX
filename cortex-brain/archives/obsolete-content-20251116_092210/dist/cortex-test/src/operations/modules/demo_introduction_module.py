"""
Demo Introduction Module

Welcomes users to CORTEX interactive demo.

SOLID Principles:
- Single Responsibility: Only handles demo introduction
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


class DemoIntroductionModule(BaseOperationModule):
    """
    Demo module for welcoming users to CORTEX.
    
    Responsibilities:
    1. Display welcome message
    2. Explain demo flow
    3. Set user expectations
    4. Provide overview of capabilities
    """
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Return module metadata."""
        return OperationModuleMetadata(
            module_id="demo_introduction",
            name="Demo Introduction",
            description="Welcome message and demo flow explanation",
            phase=OperationPhase.PREPARATION,
            priority=1,
            dependencies=[],
            optional=False,
        )
    
    def validate_prerequisites(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate prerequisites for demo introduction.
        
        No strict requirements - always runs.
        """
        return True, []
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Execute demo introduction.
        
        Steps:
        1. Display welcome banner
        2. Explain demo purpose
        3. Describe what will be shown
        4. Set expectations
        """
        start_time = datetime.now()
        
        try:
            # Get profile from context (quick, standard, comprehensive)
            profile = context.get('demo_profile', 'standard')
            
            # Build introduction message
            intro_message = self._build_introduction(profile)
            
            # Log introduction
            self.log_info("=" * 70)
            self.log_info("CORTEX INTERACTIVE DEMO")
            self.log_info("=" * 70)
            for line in intro_message.split('\n'):
                if line.strip():
                    self.log_info(line)
            self.log_info("=" * 70)
            
            # Store demo start time in context
            context['demo_start_time'] = start_time.isoformat()
            context['demo_profile'] = profile
            
            duration_seconds = (datetime.now() - start_time).total_seconds()
            
            return OperationResult(
                success=True,
                status=OperationStatus.SUCCESS,
                message=f"Welcome to CORTEX! ({profile} profile)",
                data={
                    'profile': profile,
                    'intro_message': intro_message
                },
                duration_seconds=duration_seconds
            )
            
        except Exception as e:
            self.log_error(f"Demo introduction failed: {e}")
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Demo introduction failed: {str(e)}",
                errors=[str(e)],
                duration_seconds=(datetime.now() - start_time).total_seconds()
            )
    
    def _build_introduction(self, profile: str) -> str:
        """
        Build introduction message based on profile.
        
        Args:
            profile: Demo profile (quick, standard, comprehensive)
        
        Returns:
            Formatted introduction message
        """
        lines = []
        
        # Welcome message
        lines.append("")
        lines.append("🧠 Welcome to CORTEX Interactive Demo!")
        lines.append("")
        lines.append("CORTEX transforms GitHub Copilot from an amnesiac intern into")
        lines.append("a continuously improving development partner through:")
        lines.append("")
        lines.append("  • Memory - Last 20 conversations preserved across sessions")
        lines.append("  • Learning - Accumulates patterns from every interaction")
        lines.append("  • Intelligence - 4-tier brain architecture")
        lines.append("  • Coordination - 10 specialist agents working together")
        lines.append("")
        
        # Profile-specific content
        if profile == 'quick':
            lines.append("📋 Quick Demo (2 minutes)")
            lines.append("  ✓ Essential commands")
            lines.append("  ✓ Help system")
            lines.append("  ✓ Story refresh")
        elif profile == 'standard':
            lines.append("📋 Standard Demo (3-4 minutes)")
            lines.append("  ✓ Essential commands")
            lines.append("  ✓ Help system")
            lines.append("  ✓ Story refresh")
            lines.append("  ✓ Workspace cleanup")
        else:  # comprehensive
            lines.append("📋 Comprehensive Demo (5-6 minutes)")
            lines.append("  ✓ Essential commands")
            lines.append("  ✓ Help system")
            lines.append("  ✓ Story refresh")
            lines.append("  ✓ Workspace cleanup")
            lines.append("  ✓ Conversation memory")
        
        lines.append("")
        lines.append("💡 What You'll Learn:")
        lines.append("  • How to interact with CORTEX using natural language")
        lines.append("  • Key commands and operations available")
        lines.append("  • How CORTEX maintains context and memory")
        lines.append("  • Real working examples you can use right away")
        lines.append("")
        lines.append("🚀 Let's begin!")
        lines.append("")
        
        return '\n'.join(lines)
