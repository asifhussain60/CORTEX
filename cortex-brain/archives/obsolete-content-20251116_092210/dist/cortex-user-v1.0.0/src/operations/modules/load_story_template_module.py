"""
Load Story Template Module - Story Refresh Operation

This module loads the CORTEX story template from prompts/shared/story.md
as the first step in the story refresh operation.

Author: Asif Hussain
Version: 2.0 (Universal Operations Architecture)
"""

import logging
from pathlib import Path
from typing import Dict, Any, List
from src.operations.base_operation_module import (
    BaseOperationModule,
    OperationModuleMetadata,
    OperationResult,
    OperationPhase,
    OperationStatus
)

logger = logging.getLogger(__name__)


class LoadStoryTemplateModule(BaseOperationModule):
    """
    Load the CORTEX story template file.
    
    This module is part of the refresh_cortex_story operation and demonstrates
    how the universal operations architecture works for non-setup commands.
    
    What it does:
        1. Validates story file exists at prompts/shared/story.md
        2. Loads story content
        3. Validates basic Markdown structure
        4. Stores story content in context for downstream modules
    
    Example Usage:
        # Via operation
        result = execute_operation("refresh_cortex_story")
        
        # Direct
        module = LoadStoryTemplateModule()
        context = {'project_root': Path('/path/to/cortex')}
        result = module.execute(context)
        story_content = context['story_content']
    """
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Return module metadata."""
        return OperationModuleMetadata(
            module_id="load_story_template",
            name="Load Story Template",
            description="Load CORTEX story from prompts/shared/story.md",
            phase=OperationPhase.PREPARATION,
            priority=10,
            dependencies=[],
            optional=False,
            version="1.0",
            tags=["story", "required", "preparation"]
        )
    
    def validate_prerequisites(self, context: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate that story file exists.
        
        Args:
            context: Must contain 'project_root'
        
        Returns:
            (is_valid, issues_list)
        """
        issues = []
        
        # Check project root
        if 'project_root' not in context:
            issues.append("project_root not set in context")
            return False, issues
        
        project_root = Path(context['project_root'])
        if not project_root.exists():
            issues.append(f"Project root does not exist: {project_root}")
        
        # Check story file exists
        story_path = project_root / "prompts" / "shared" / "story.md"
        if not story_path.exists():
            issues.append(f"Story file not found: {story_path}")
        
        return len(issues) == 0, issues
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Load story template file.
        
        Args:
            context: Shared context dictionary
                - Input: project_root (Path)
                - Output: story_content (str), story_path (Path), story_line_count (int)
        
        Returns:
            OperationResult with story loading status
        """
        try:
            project_root = Path(context['project_root'])
            story_path = project_root / "prompts" / "shared" / "story.md"
            
            logger.info(f"Loading story template from: {story_path}")
            
            # Read story file
            with open(story_path, 'r', encoding='utf-8') as f:
                story_content = f.read()
            
            # Validate basic structure
            if not story_content.strip():
                return OperationResult(
                    success=False,
                    status=OperationStatus.FAILED,
                    message="Story file is empty",
                    errors=["Story file contains no content"]
                )
            
            # Count lines and check for markdown
            lines = story_content.split('\n')
            has_markdown = any(line.startswith('#') for line in lines)
            
            if not has_markdown:
                logger.warning("Story file does not appear to contain Markdown headers")
            
            # Store in context for downstream modules
            context['story_content'] = story_content
            context['story_path'] = story_path
            context['story_line_count'] = len(lines)
            context['story_has_markdown'] = has_markdown
            
            logger.info(f"Story loaded successfully: {len(lines)} lines, {len(story_content)} characters")
            
            return OperationResult(
                success=True,
                status=OperationStatus.SUCCESS,
                message=f"Story template loaded ({len(lines)} lines)",
                data={
                    'story_path': str(story_path),
                    'line_count': len(lines),
                    'character_count': len(story_content),
                    'has_markdown': has_markdown,
                    'file_size_bytes': story_path.stat().st_size
                }
            )
        
        except FileNotFoundError as e:
            logger.error(f"Story file not found: {e}")
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message="Story file not found",
                errors=[str(e)]
            )
        
        except PermissionError as e:
            logger.error(f"Permission denied reading story file: {e}")
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message="Permission denied reading story file",
                errors=[str(e)]
            )
        
        except Exception as e:
            logger.error(f"Unexpected error loading story: {e}", exc_info=True)
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Failed to load story template: {e}",
                errors=[str(e)]
            )
    
    def rollback(self, context: Dict[str, Any]) -> bool:
        """
        Rollback story loading (no-op for read operation).
        
        Args:
            context: Shared context dictionary
        
        Returns:
            True (always succeeds for read-only operations)
        """
        # Read-only operation - no rollback needed
        logger.debug("Rollback called for read-only operation (no-op)")
        
        # Clear story data from context if present
        context.pop('story_content', None)
        context.pop('story_path', None)
        context.pop('story_line_count', None)
        context.pop('story_has_markdown', None)
        
        return True
    
    def should_run(self, context: Dict[str, Any]) -> bool:
        """
        Determine if module should run.
        
        Args:
            context: Shared context dictionary
        
        Returns:
            True (always run for story refresh)
        """
        # Always load story for refresh operation
        return True
    
    def get_progress_message(self) -> str:
        """Get progress message."""
        return "Loading CORTEX story template..."
