"""
Save Story Markdown Module - Story Refresh Operation

This module saves the transformed CORTEX story to the documentation directory.

Author: Asif Hussain
Version: 2.0 (Universal Operations Architecture)
"""

import logging
from pathlib import Path
from typing import Dict, Any, List
import shutil
from datetime import datetime
from src.operations.base_operation_module import (
    BaseOperationModule,
    OperationModuleMetadata,
    OperationResult,
    OperationPhase,
    OperationStatus
)

logger = logging.getLogger(__name__)


class SaveStoryMarkdownModule(BaseOperationModule):
    """
    Save transformed story to file.
    
    This module writes the transformed CORTEX story to docs/awakening-of-cortex.md
    with backup of existing file.
    
    What it does:
        1. Backs up existing story file (if it exists)
        2. Writes transformed story to docs/awakening-of-cortex.md
        3. Verifies file was written correctly
        4. Stores backup path in context for rollback
    """
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Return module metadata."""
        return OperationModuleMetadata(
            module_id="save_story_markdown",
            name="Save Story Markdown",
            description="Write transformed story to file",
            phase=OperationPhase.FINALIZATION,
            priority=10,
            dependencies=["apply_narrator_voice"],
            optional=False,
            version="1.0",
            tags=["story", "required"]
        )
    
    def validate_prerequisites(self, context: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate that transformed story and project root are available.
        
        Args:
            context: Must contain 'transformed_story' and 'project_root'
        
        Returns:
            (is_valid, issues_list)
        """
        issues = []
        
        if 'transformed_story' not in context:
            issues.append("transformed_story not found in context")
        elif not context['transformed_story']:
            issues.append("transformed_story is empty")
        
        if 'project_root' not in context:
            issues.append("project_root not found in context")
        
        return len(issues) == 0, issues
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Save story to file.
        
        Args:
            context: Shared context dictionary
                - Input: transformed_story (str), project_root (Path)
                - Output: story_file_path (Path), backup_path (Path or None)
        
        Returns:
            OperationResult with save status
        """
        try:
            story_content = context['transformed_story']
            project_root = Path(context['project_root'])
            
            # Determine output path
            output_path = project_root / "docs" / "awakening-of-cortex.md"
            
            logger.info(f"Saving story to: {output_path}")
            
            # Create docs directory if it doesn't exist
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Backup existing file
            backup_path = None
            if output_path.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = output_path.parent / f"awakening-of-cortex.backup.{timestamp}.md"
                shutil.copy2(output_path, backup_path)
                logger.info(f"Created backup: {backup_path}")
            
            # Write story to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(story_content)
            
            # Verify file was written
            if not output_path.exists():
                return OperationResult(
                    success=False,
                    status=OperationStatus.FAILED,
                    message="Story file was not created",
                    errors=["File write verification failed"]
                )
            
            # Verify content
            with open(output_path, 'r', encoding='utf-8') as f:
                written_content = f.read()
            
            if written_content != story_content:
                return OperationResult(
                    success=False,
                    status=OperationStatus.FAILED,
                    message="Story file content verification failed",
                    errors=["Written content does not match source"]
                )
            
            # Store paths in context
            context['story_file_path'] = output_path
            context['backup_path'] = backup_path
            
            file_size = output_path.stat().st_size
            lines = story_content.split('\n')
            
            logger.info(
                f"Story saved successfully: {len(lines)} lines, {file_size} bytes"
            )
            
            return OperationResult(
                success=True,
                status=OperationStatus.SUCCESS,
                message=f"Story saved to {output_path.name} ({len(lines)} lines)",
                data={
                    'output_path': str(output_path),
                    'backup_path': str(backup_path) if backup_path else None,
                    'line_count': len(lines),
                    'file_size_bytes': file_size,
                    'backup_created': backup_path is not None
                }
            )
        
        except PermissionError as e:
            logger.error(f"Permission denied writing story file: {e}")
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message="Permission denied writing story file",
                errors=[str(e)]
            )
        
        except Exception as e:
            logger.error(f"Failed to save story: {e}", exc_info=True)
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Failed to save story: {e}",
                errors=[str(e)]
            )
    
    def rollback(self, context: Dict[str, Any]) -> bool:
        """
        Rollback story save by restoring backup.
        
        Args:
            context: Shared context dictionary
        
        Returns:
            True if rollback succeeded
        """
        try:
            logger.info("Rolling back story save...")
            
            story_file_path = context.get('story_file_path')
            backup_path = context.get('backup_path')
            
            if backup_path and Path(backup_path).exists():
                # Restore from backup
                shutil.copy2(backup_path, story_file_path)
                logger.info(f"Restored story from backup: {backup_path}")
                
                # Remove backup
                Path(backup_path).unlink()
                logger.info(f"Removed backup file: {backup_path}")
            elif story_file_path and Path(story_file_path).exists():
                # No backup, just delete the file
                Path(story_file_path).unlink()
                logger.info(f"Removed story file: {story_file_path}")
            
            # Clear context
            context.pop('story_file_path', None)
            context.pop('backup_path', None)
            
            return True
        
        except Exception as e:
            logger.error(f"Rollback failed: {e}", exc_info=True)
            return False
    
    def should_run(self, context: Dict[str, Any]) -> bool:
        """
        Determine if module should run.
        
        Args:
            context: Shared context dictionary
        
        Returns:
            False if dry_run is True
        """
        return not context.get('dry_run', False)
    
    def get_progress_message(self) -> str:
        """Get progress message."""
        return "Saving story to docs/awakening-of-cortex.md..."
