"""
Build Story Preview Module - Story Refresh Operation

This module builds an HTML preview of the refreshed CORTEX story using MkDocs.

Author: Asif Hussain
Version: 2.0 (Universal Operations Architecture)
"""

import logging
import subprocess
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


class BuildStoryPreviewModule(BaseOperationModule):
    """
    Build HTML preview of story.
    
    This module uses MkDocs to generate an HTML preview of the CORTEX story
    for immediate viewing.
    
    What it does:
        1. Runs `mkdocs build` to generate HTML
        2. Verifies site/ directory was created
        3. Checks for story HTML file
        4. Provides preview URL
    """
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Return module metadata."""
        return OperationModuleMetadata(
            module_id="build_story_preview",
            name="Build Story Preview",
            description="Generate HTML preview of story",
            phase=OperationPhase.FINALIZATION,
            priority=30,
            dependencies=["save_story_markdown"],
            optional=True,
            version="1.0",
            tags=["story", "preview"]
        )
    
    def validate_prerequisites(self, context: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate that story was saved and project root is available.
        
        Args:
            context: Must contain 'story_file_path' and 'project_root'
        
        Returns:
            (is_valid, issues_list)
        """
        issues = []
        
        if 'story_file_path' not in context:
            issues.append("story_file_path not found in context")
        
        if 'project_root' not in context:
            issues.append("project_root not found in context")
        
        return len(issues) == 0, issues
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Build story preview.
        
        Args:
            context: Shared context dictionary
                - Input: story_file_path (Path), project_root (Path)
                - Output: preview_path (Path), preview_url (str)
        
        Returns:
            OperationResult with build status
        """
        try:
            project_root = Path(context['project_root'])
            
            logger.info("Building story preview with MkDocs...")
            
            # Check if mkdocs is available
            try:
                result = subprocess.run(
                    ['mkdocs', '--version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode != 0:
                    return OperationResult(
                        success=True,
                        status=OperationStatus.SKIPPED,
                        message="MkDocs not available, skipping preview",
                        warnings=["MkDocs not installed or not in PATH"]
                    )
            except (subprocess.TimeoutExpired, FileNotFoundError):
                return OperationResult(
                    success=True,
                    status=OperationStatus.SKIPPED,
                    message="MkDocs not available, skipping preview",
                    warnings=["MkDocs not installed or not in PATH"]
                )
            
            # Run mkdocs build
            result = subprocess.run(
                ['mkdocs', 'build', '--clean'],
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                logger.error(f"MkDocs build failed: {result.stderr}")
                return OperationResult(
                    success=False,
                    status=OperationStatus.FAILED,
                    message="MkDocs build failed",
                    errors=[result.stderr or "Unknown error"],
                    warnings=[result.stdout] if result.stdout else []
                )
            
            # Verify site was built
            site_dir = project_root / "site"
            if not site_dir.exists():
                return OperationResult(
                    success=False,
                    status=OperationStatus.FAILED,
                    message="site/ directory not created",
                    errors=["MkDocs build completed but site/ directory missing"]
                )
            
            # Check for story HTML
            story_html = site_dir / "awakening-of-cortex" / "index.html"
            if not story_html.exists():
                # Try alternative path
                story_html = site_dir / "awakening-of-cortex.html"
            
            if story_html.exists():
                preview_url = f"file://{story_html.as_posix()}"
                logger.info(f"Story preview available at: {preview_url}")
            else:
                preview_url = f"file://{site_dir.as_posix()}/index.html"
                logger.warning(f"Story HTML not found, using site index: {preview_url}")
            
            context['preview_path'] = site_dir
            context['preview_url'] = preview_url
            
            # Get build output statistics
            html_files = list(site_dir.rglob("*.html"))
            
            logger.info(
                f"Story preview built successfully: {len(html_files)} HTML files"
            )
            
            return OperationResult(
                success=True,
                status=OperationStatus.SUCCESS,
                message=f"Story preview built ({len(html_files)} HTML files)",
                data={
                    'site_dir': str(site_dir),
                    'preview_url': preview_url,
                    'html_file_count': len(html_files),
                    'build_output': result.stdout[:500] if result.stdout else None
                }
            )
        
        except subprocess.TimeoutExpired:
            logger.error("MkDocs build timed out")
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message="MkDocs build timed out (60s)",
                errors=["Build took longer than 60 seconds"]
            )
        
        except Exception as e:
            logger.error(f"Failed to build story preview: {e}", exc_info=True)
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Failed to build story preview: {e}",
                errors=[str(e)]
            )
    
    def rollback(self, context: Dict[str, Any]) -> bool:
        """
        Rollback preview build (no-op - site/ can be rebuilt anytime).
        
        Args:
            context: Shared context dictionary
        
        Returns:
            True (always succeeds)
        """
        logger.debug("Rollback story preview build (no-op)")
        
        context.pop('preview_path', None)
        context.pop('preview_url', None)
        
        return True
    
    def should_run(self, context: Dict[str, Any]) -> bool:
        """
        Determine if module should run.
        
        Args:
            context: Shared context dictionary
        
        Returns:
            True only for 'full' profile
        """
        profile = context.get('profile', 'standard')
        return profile == 'full'
    
    def get_progress_message(self) -> str:
        """Get progress message."""
        return "Building story preview with MkDocs..."
