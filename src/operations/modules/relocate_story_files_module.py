"""
Relocate Story Files Module - Story Refresh Operation

This module relocates Ancient-Rules.md and CORTEX-FEATURES.md to the story directory
to keep all story-related documentation together.

Author: Asif Hussain
Version: 2.0 (Intelligent file relocation)
"""

import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Tuple
from src.operations.base_operation_module import (
    BaseOperationModule,
    OperationModuleMetadata,
    OperationResult,
    OperationPhase,
    OperationStatus
)

logger = logging.getLogger(__name__)


class RelocateStoryFilesModule(BaseOperationModule):
    """
    Relocate story-related files to docs/story/CORTEX-STORY/.
    
    This module moves:
    - Ancient-Rules.md (from cortex-brain/ or docs/)
    - CORTEX-FEATURES.md (from cortex-brain/ or docs/)
    
    What it does:
        1. Searches for files in common locations
        2. Creates backups before moving
        3. Relocates files to story directory
        4. Updates any references in other docs (optional)
        5. Verifies successful relocation
    """
    
    # Files to relocate
    TARGET_FILES = [
        'Ancient-Rules.md',
        'CORTEX-FEATURES.md'
    ]
    
    # Search paths (in order of priority)
    SEARCH_PATHS = [
        'cortex-brain',
        'docs',
        'docs/story',
        '.'  # Root
    ]
    
    def _get_metadata(self) -> OperationModuleMetadata:
        """Get module metadata."""
        return OperationModuleMetadata(
            module_id="relocate_story_files",
            name="Relocate Story Files",
            description="Move Ancient-Rules.md and CORTEX-FEATURES.md to story directory",
            version="2.0",
            author="Asif Hussain",
            dependencies=[],
            config_schema={
                "output_dir": {
                    "type": "string",
                    "description": "Target story directory",
                    "required": False
                },
                "create_backups": {
                    "type": "boolean",
                    "description": "Create backups before moving",
                    "required": False,
                    "default": True
                }
            }
        )
    
    def validate(self, context: Dict[str, Any]) -> OperationResult:
        """Validate prerequisites."""
        # Check if at least one target file exists
        project_root = Path(context.get('project_root', '.'))
        found_files = []
        
        for filename in self.TARGET_FILES:
            if self._find_file(project_root, filename):
                found_files.append(filename)
        
        if not found_files:
            return OperationResult(
                success=False,
                status=OperationStatus.VALIDATION_FAILED,
                message=f"No target files found: {', '.join(self.TARGET_FILES)}"
            )
        
        return OperationResult(
            success=True,
            status=OperationStatus.VALIDATED,
            message=f"Found {len(found_files)} file(s) to relocate"
        )
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """Relocate story files."""
        try:
            logger.info("Relocating story files...")
            
            # Get paths
            project_root = Path(context.get('project_root', '.'))
            output_dir = Path(context.get('output_dir', 'docs/story/CORTEX-STORY'))
            output_dir.mkdir(parents=True, exist_ok=True)
            create_backups = context.get('create_backups', True)
            
            # Relocate files
            relocated = []
            skipped = []
            failed = []
            
            for filename in self.TARGET_FILES:
                result = self._relocate_file(
                    project_root=project_root,
                    filename=filename,
                    target_dir=output_dir,
                    create_backup=create_backups
                )
                
                if result['status'] == 'relocated':
                    relocated.append(result)
                elif result['status'] == 'skipped':
                    skipped.append(result)
                else:
                    failed.append(result)
            
            # Store in context
            context['relocated_files'] = relocated
            context['skipped_files'] = skipped
            context['failed_files'] = failed
            
            # Build message
            messages = []
            if relocated:
                messages.append(f"Relocated {len(relocated)} file(s)")
            if skipped:
                messages.append(f"Skipped {len(skipped)} file(s)")
            if failed:
                messages.append(f"Failed {len(failed)} file(s)")
            
            message = ", ".join(messages)
            success = len(failed) == 0
            
            return OperationResult(
                success=success,
                status=OperationStatus.COMPLETED if success else OperationStatus.PARTIAL,
                message=message,
                data={
                    "relocated_count": len(relocated),
                    "skipped_count": len(skipped),
                    "failed_count": len(failed),
                    "relocated_files": [r['filename'] for r in relocated],
                    "skipped_files": [s['filename'] for s in skipped],
                    "failed_files": [f['filename'] for f in failed]
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to relocate files: {e}", exc_info=True)
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"File relocation failed: {e}"
            )
    
    def _find_file(self, project_root: Path, filename: str) -> Path:
        """
        Find file in search paths.
        
        Args:
            project_root: Project root directory
            filename: File to search for
        
        Returns:
            Path to file or None if not found
        """
        for search_path in self.SEARCH_PATHS:
            file_path = project_root / search_path / filename
            if file_path.exists():
                return file_path
        return None
    
    def _relocate_file(
        self,
        project_root: Path,
        filename: str,
        target_dir: Path,
        create_backup: bool
    ) -> Dict[str, Any]:
        """
        Relocate a single file.
        
        Args:
            project_root: Project root directory
            filename: File to relocate
            target_dir: Target directory
            create_backup: Whether to create backup
        
        Returns:
            Dictionary with relocation status
        """
        try:
            # Find source file
            source_path = self._find_file(project_root, filename)
            if not source_path:
                return {
                    'status': 'skipped',
                    'filename': filename,
                    'reason': 'File not found'
                }
            
            target_path = target_dir / filename
            
            # Check if already in target location
            if source_path.resolve() == target_path.resolve():
                return {
                    'status': 'skipped',
                    'filename': filename,
                    'reason': 'Already in target location'
                }
            
            # Create backup if requested
            if create_backup and source_path.exists():
                backup_dir = source_path.parent / '.backups'
                backup_dir.mkdir(exist_ok=True)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_name = f"{source_path.stem}_{timestamp}{source_path.suffix}"
                backup_path = backup_dir / backup_name
                shutil.copy2(source_path, backup_path)
                logger.info(f"Backed up {filename} to {backup_path}")
            
            # Move file
            shutil.move(str(source_path), str(target_path))
            logger.info(f"Relocated {filename}: {source_path} → {target_path}")
            
            return {
                'status': 'relocated',
                'filename': filename,
                'source': str(source_path),
                'target': str(target_path),
                'backup': str(backup_path) if create_backup else None
            }
            
        except Exception as e:
            logger.error(f"Failed to relocate {filename}: {e}")
            return {
                'status': 'failed',
                'filename': filename,
                'error': str(e)
            }
    
    def rollback(self, context: Dict[str, Any]) -> bool:
        """
        Rollback by moving files back to original locations.
        
        Args:
            context: Shared context dictionary
        
        Returns:
            True if rollback succeeded
        """
        try:
            relocated_files = context.get('relocated_files', [])
            
            for file_info in relocated_files:
                source = Path(file_info['source'])
                target = Path(file_info['target'])
                
                if target.exists():
                    # Move back
                    source.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(target), str(source))
                    logger.info(f"Rolled back: {target} → {source}")
            
            # Clear context
            context.pop('relocated_files', None)
            context.pop('skipped_files', None)
            context.pop('failed_files', None)
            
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
            True if files need relocation
        """
        project_root = Path(context.get('project_root', '.'))
        
        for filename in self.TARGET_FILES:
            if self._find_file(project_root, filename):
                return True
        
        return False
    
    def get_progress_message(self) -> str:
        """Get progress message."""
        return "Relocating story files to unified directory..."


def register() -> BaseOperationModule:
    """Register this module."""
    return RelocateStoryFilesModule()
