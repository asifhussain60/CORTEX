"""
Demo Story Refresh Module

Demonstrates CORTEX story refresh operation with narrator voice transformation.

SOLID Principles:
- Single Responsibility: Only handles story refresh demonstration
- Open/Closed: Extends BaseOperationModule without modifying it
- Dependency Inversion: Depends on BaseOperationModule abstraction

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from typing import Dict, Any, Tuple, List
from datetime import datetime
from pathlib import Path

from src.operations.base_operation_module import (
    BaseOperationModule,
    OperationModuleMetadata,
    OperationResult,
    OperationStatus,
    OperationPhase
)
from src.operations import execute_operation


class DemoStoryRefreshModule(BaseOperationModule):
    """
    Demo module for showcasing story refresh operation.
    
    Responsibilities:
    1. Execute story refresh operation
    2. Show narrator voice transformation
    3. Display before/after excerpts
    4. Explain documentation refresh process
    """
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Return module metadata."""
        return OperationModuleMetadata(
            module_id="demo_story_refresh",
            name="Demo Story Refresh",
            description="Execute story refresh and show narrator voice transformation",
            phase=OperationPhase.PROCESSING,
            priority=2,
            dependencies=["demo_help_system"],
            optional=False,
        )
    
    def validate_prerequisites(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate prerequisites for story refresh demo.
        
        Checks:
        1. Story file exists (or operation can create it)
        """
        issues = []
        
        # Check if story file exists (but it's okay if it doesn't - refresh will handle it)
        config = context.get('config', {})
        cortex_root = Path(config.get('cortex_root', Path.cwd()))
        story_path = cortex_root / 'prompts' / 'shared' / 'story.md'
        
        # Just check parent directory is writable
        if not story_path.parent.exists():
            issues.append(f"Story directory not found: {story_path.parent}")
        
        return len(issues) == 0, issues
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Execute story refresh demonstration.
        
        Steps:
        1. Explain story refresh purpose
        2. Execute refresh_cortex_story operation
        3. Show transformation results
        4. Display key excerpts
        """
        start_time = datetime.now()
        
        try:
            self.log_info("")
            self.log_info("=" * 70)
            self.log_info("STORY REFRESH DEMONSTRATION")
            self.log_info("=" * 70)
            
            # Explain story refresh
            self._explain_story_refresh()
            
            # Execute story refresh operation
            self.log_info("")
            self.log_info("🔄 Executing story refresh operation...")
            self.log_info("")
            
            refresh_result = execute_operation('refresh story')
            
            if refresh_result.success:
                self.log_info("✅ Story refresh complete!")
                
                # Show results
                self._show_refresh_results(refresh_result, context)
                
                # Explain what happened
                self._explain_transformation(refresh_result)
                
            else:
                self.log_warning("⚠️  Story refresh encountered issues (demo continues)")
                if refresh_result.errors:
                    for error in refresh_result.errors[:2]:  # Show max 2 errors
                        self.log_warning(f"   - {error}")
            
            self.log_info("")
            self.log_info("=" * 70)
            
            duration_seconds = (datetime.now() - start_time).total_seconds()
            
            return OperationResult(
                success=True,
                status=OperationStatus.SUCCESS,
                message="Story refresh demonstration complete",
                data={
                    'refresh_executed': True,
                    'refresh_success': refresh_result.success,
                    'modules_executed': refresh_result.context.get('modules_executed', 0)
                },
                duration_seconds=duration_seconds
            )
            
        except Exception as e:
            self.log_error(f"Story refresh demo failed: {e}")
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Story refresh demo failed: {str(e)}",
                errors=[str(e)],
                duration_seconds=(datetime.now() - start_time).total_seconds()
            )
    
    def _explain_story_refresh(self):
        """Explain what story refresh does."""
        self.log_info("")
        self.log_info("📖 About Story Refresh:")
        self.log_info("")
        self.log_info("The CORTEX story is the narrative documentation that explains")
        self.log_info("how CORTEX works using the 'Intern with Amnesia' metaphor.")
        self.log_info("")
        self.log_info("Story refresh:")
        self.log_info("  • Loads the raw story template")
        self.log_info("  • Applies narrator voice transformation")
        self.log_info("  • Updates navigation structure")
        self.log_info("  • Validates markdown formatting")
        self.log_info("  • Saves to prompts/shared/story.md")
        self.log_info("")
        self.log_info("This ensures documentation stays fresh, readable, and engaging!")
        self.log_info("")
    
    def _show_refresh_results(self, refresh_result: OperationResult, context: Dict[str, Any]):
        """
        Show story refresh results.
        
        Args:
            refresh_result: Result from refresh operation
            context: Demo context
        """
        self.log_info("")
        self.log_info("📊 Refresh Results:")
        
        modules_executed = refresh_result.context.get('modules_executed', 0)
        self.log_info(f"  • Modules executed: {modules_executed}/6")
        
        duration = refresh_result.total_duration_seconds
        self.log_info(f"  • Duration: {duration:.2f} seconds")
        
        # Show file info if available
        config = context.get('config', {})
        cortex_root = Path(config.get('cortex_root', Path.cwd()))
        story_output = cortex_root / 'prompts' / 'shared' / 'story.md'
        
        if story_output.exists():
            size_kb = story_output.stat().st_size / 1024
            self.log_info(f"  • Output size: {size_kb:.1f} KB")
            self.log_info(f"  • Location: {story_output.name}")
    
    def _explain_transformation(self, refresh_result: OperationResult):
        """
        Explain what the narrator voice transformation does.
        
        Args:
            refresh_result: Result from refresh operation
        """
        self.log_info("")
        self.log_info("✨ Narrator Voice Transformation:")
        self.log_info("")
        self.log_info("CORTEX uses a unique 'narrator voice' to make documentation")
        self.log_info("more engaging and human-centered:")
        self.log_info("")
        self.log_info("  Before: 'The system implements memory persistence.'")
        self.log_info("  After:  'Imagine hiring an intern who forgets everything...")
        self.log_info("          That's GitHub Copilot without CORTEX.'")
        self.log_info("")
        self.log_info("This transformation:")
        self.log_info("  ✓ Makes complex concepts accessible")
        self.log_info("  ✓ Uses metaphors and analogies")
        self.log_info("  ✓ Maintains technical accuracy")
        self.log_info("  ✓ Keeps readers engaged")
        self.log_info("")
        self.log_info("💡 Try reading the story: #file:prompts/shared/story.md")
        self.log_info("")

