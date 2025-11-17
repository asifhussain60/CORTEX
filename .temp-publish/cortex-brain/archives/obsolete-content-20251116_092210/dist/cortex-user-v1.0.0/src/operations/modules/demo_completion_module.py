"""
Demo Completion Module

Summarizes demo learnings and suggests next steps.

SOLID Principles:
- Single Responsibility: Only handles demo completion and summary
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


class DemoCompletionModule(BaseOperationModule):
    """
    Demo module for completing the interactive demo.
    
    Responsibilities:
    1. Summarize what was learned
    2. Highlight key capabilities
    3. Suggest next steps
    4. Provide command reminders
    """
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Return module metadata."""
        return OperationModuleMetadata(
            module_id="demo_completion",
            name="Demo Completion",
            description="Summarize demo learnings and suggest next steps",
            phase=OperationPhase.FINALIZATION,
            priority=4,
            dependencies=["demo_conversation"],
            optional=False,
        )
    
    def validate_prerequisites(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate prerequisites for demo completion.
        
        No strict requirements - always runs.
        """
        return True, []
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Execute demo completion.
        
        Steps:
        1. Summarize demo experience
        2. Highlight key learnings
        3. Suggest next steps
        4. Provide command reference
        """
        start_time = datetime.now()
        
        try:
            profile = context.get('demo_profile', 'standard')
            demo_start_time_str = context.get('demo_start_time')
            
            # Calculate total demo time
            if demo_start_time_str:
                demo_start = datetime.fromisoformat(demo_start_time_str)
                total_duration = (datetime.now() - demo_start).total_seconds()
            else:
                total_duration = None
            
            self.log_info("")
            self.log_info("=" * 70)
            self.log_info("DEMO COMPLETION")
            self.log_info("=" * 70)
            
            # Summary
            self._show_summary(profile, total_duration)
            
            # Key learnings
            self._show_key_learnings(profile)
            
            # Next steps
            self._show_next_steps()
            
            # Command reference
            self._show_command_reference()
            
            # Closing message
            self._show_closing_message()
            
            self.log_info("=" * 70)
            
            duration_seconds = (datetime.now() - start_time).total_seconds()
            
            return OperationResult(
                success=True,
                status=OperationStatus.SUCCESS,
                message="Demo completed successfully!",
                data={
                    'profile': profile,
                    'total_demo_duration': total_duration,
                    'demo_completed': True
                },
                duration_seconds=duration_seconds
            )
            
        except Exception as e:
            self.log_error(f"Demo completion failed: {e}")
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Demo completion failed: {str(e)}",
                errors=[str(e)],
                duration_seconds=(datetime.now() - start_time).total_seconds()
            )
    
    def _show_summary(self, profile: str, total_duration: float = None):
        """
        Show demo summary.
        
        Args:
            profile: Demo profile used
            total_duration: Total demo duration in seconds
        """
        self.log_info("")
        self.log_info("🎉 Congratulations! You've completed the CORTEX demo!")
        self.log_info("")
        
        if total_duration:
            minutes = int(total_duration // 60)
            seconds = int(total_duration % 60)
            self.log_info(f"📊 Demo Duration: {minutes}m {seconds}s ({profile} profile)")
        else:
            self.log_info(f"📊 Profile: {profile}")
        
        self.log_info("")
    
    def _show_key_learnings(self, profile: str):
        """
        Show key learnings from demo.
        
        Args:
            profile: Demo profile used
        """
        self.log_info("✨ What You Learned:")
        self.log_info("")
        
        # Common learnings across all profiles
        learnings = [
            "✓ How to get help with /help command",
            "✓ Natural language vs slash commands",
            "✓ Story refresh and narrator voice transformation"
        ]
        
        # Add profile-specific learnings
        if profile in ['standard', 'comprehensive']:
            learnings.append("✓ Workspace cleanup and optimization")
        
        if profile == 'comprehensive':
            learnings.append("✓ Conversation tracking and /resume workflow")
            learnings.append("✓ CORTEX 4-tier memory architecture")
        
        for learning in learnings:
            self.log_info(f"  {learning}")
        
        self.log_info("")
    
    def _show_next_steps(self):
        """Show suggested next steps."""
        self.log_info("🚀 Suggested Next Steps:")
        self.log_info("")
        self.log_info("1. Try a real task:")
        self.log_info("   'Add a new feature to my project'")
        self.log_info("   'Refactor this code to use dependency injection'")
        self.log_info("")
        self.log_info("2. Explore documentation:")
        self.log_info("   Read the story: #file:prompts/shared/story.md")
        self.log_info("   Technical reference: #file:prompts/shared/technical-reference.md")
        self.log_info("")
        self.log_info("3. Setup conversation tracking:")
        self.log_info("   See: #file:prompts/shared/tracking-guide.md")
        self.log_info("   This enables /resume and persistent memory!")
        self.log_info("")
        self.log_info("4. Check project health:")
        self.log_info("   Try: /status")
        self.log_info("   Shows: test coverage, git status, brain health")
        self.log_info("")
    
    def _show_command_reference(self):
        """Show quick command reference."""
        self.log_info("📋 Quick Command Reference:")
        self.log_info("")
        self.log_info("Essential Commands:")
        self.log_info("  /help         - Show all available commands")
        self.log_info("  /status       - Check system health")
        self.log_info("  /resume       - Continue from last session")
        self.log_info("  /setup        - Reconfigure environment")
        self.log_info("")
        self.log_info("Natural Language Works Too:")
        self.log_info("  'cleanup workspace'")
        self.log_info("  'refresh documentation'")
        self.log_info("  'show me what I was working on'")
        self.log_info("")
        self.log_info("💡 Use '/help' anytime to see full command list!")
        self.log_info("")
    
    def _show_closing_message(self):
        """Show closing message."""
        self.log_info("🧠 Remember:")
        self.log_info("")
        self.log_info("CORTEX transforms GitHub Copilot from an amnesiac intern")
        self.log_info("into a continuously improving development partner.")
        self.log_info("")
        self.log_info("  • It remembers your conversations")
        self.log_info("  • It learns from your patterns")
        self.log_info("  • It understands your project context")
        self.log_info("  • It coordinates specialized agents")
        self.log_info("")
        self.log_info("Now go build something amazing! 🚀")
        self.log_info("")

