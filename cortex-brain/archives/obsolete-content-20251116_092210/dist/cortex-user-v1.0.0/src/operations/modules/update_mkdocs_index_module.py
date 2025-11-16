"""
Update MkDocs Index Module - Story Refresh Operation

This module updates the MkDocs navigation to include the refreshed story.

Author: Asif Hussain
Version: 2.0 (Universal Operations Architecture)
"""

import logging
from pathlib import Path
from typing import Dict, Any, List
import yaml
from src.operations.base_operation_module import (
    BaseOperationModule,
    OperationModuleMetadata,
    OperationResult,
    OperationPhase,
    OperationStatus
)

logger = logging.getLogger(__name__)


class UpdateMkDocsIndexModule(BaseOperationModule):
    """
    Update MkDocs navigation with story.
    
    This module ensures the CORTEX story is properly linked in the
    MkDocs navigation structure.
    
    What it does:
        1. Reads mkdocs.yml configuration
        2. Checks if story is in navigation
        3. Updates navigation if needed
        4. Writes back to mkdocs.yml
    """
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Return module metadata."""
        return OperationModuleMetadata(
            module_id="update_mkdocs_index",
            name="Update MkDocs Index",
            description="Update MkDocs navigation with story",
            phase=OperationPhase.FINALIZATION,
            priority=20,
            dependencies=["save_story_markdown"],
            optional=True,
            version="1.0",
            tags=["story", "documentation"]
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
        Update MkDocs navigation.
        
        Args:
            context: Shared context dictionary
                - Input: story_file_path (Path), project_root (Path)
                - Output: mkdocs_updated (bool), navigation_entry (str)
        
        Returns:
            OperationResult with update status
        """
        try:
            project_root = Path(context['project_root'])
            mkdocs_path = project_root / "mkdocs.yml"
            
            if not mkdocs_path.exists():
                logger.warning(f"mkdocs.yml not found at {mkdocs_path}")
                return OperationResult(
                    success=True,
                    status=OperationStatus.SKIPPED,
                    message="mkdocs.yml not found, skipping navigation update",
                    warnings=["MkDocs configuration not found"]
                )
            
            logger.info(f"Updating MkDocs navigation: {mkdocs_path}")
            
            # Read mkdocs.yml
            # Note: MkDocs YAML may contain Python object tags that yaml.safe_load can't handle
            # We'll read as text and check for story entry
            with open(mkdocs_path, 'r', encoding='utf-8') as f:
                mkdocs_content = f.read()
            
            # Simple text-based check for story entry
            if 'awakening-of-cortex' in mkdocs_content.lower():
                logger.info("Story already found in MkDocs navigation (text search)")
                context['mkdocs_updated'] = False
                context['navigation_entry'] = "Already exists"
                
                return OperationResult(
                    success=True,
                    status=OperationStatus.SUCCESS,
                    message="Story already in MkDocs navigation",
                    data={
                        'mkdocs_path': str(mkdocs_path),
                        'navigation_updated': False,
                        'detection_method': 'text_search'
                    }
                )
            
            # Try to parse YAML (may fail with MkDocs custom tags)
            try:
                with open(mkdocs_path, 'r', encoding='utf-8') as f:
                    mkdocs_config = yaml.safe_load(f)
            except yaml.YAMLError as e:
                # If YAML parsing fails but story isn't found, warn and skip
                logger.warning(f"Could not parse mkdocs.yml (MkDocs custom tags): {e}")
                logger.warning("Story not found in navigation, but cannot update due to YAML format")
                
                context['mkdocs_updated'] = False
                context['navigation_entry'] = None
                
                return OperationResult(
                    success=True,
                    status=OperationStatus.SKIPPED,
                    message="Cannot update MkDocs navigation (YAML format incompatible)",
                    warnings=[
                        "mkdocs.yml contains custom tags that prevent automatic updates",
                        "Story may need to be manually added to navigation"
                    ]
                )
            
            if not mkdocs_config:
                return OperationResult(
                    success=False,
                    status=OperationStatus.FAILED,
                    message="mkdocs.yml is empty or invalid",
                    errors=["Could not parse MkDocs configuration"]
                )
            
            # Check if story is in navigation
            nav = mkdocs_config.get('nav', [])
            story_entry_name = "The Awakening (Complete)"
            story_path = "awakening-of-cortex.md"
            
            story_exists = False
            for item in nav:
                if isinstance(item, dict):
                    for key, value in item.items():
                        if value == story_path or 'awakening' in str(value).lower():
                            story_exists = True
                            logger.info(f"Story already in navigation: {key}")
                            break
            
            if story_exists:
                context['mkdocs_updated'] = False
                context['navigation_entry'] = "Already exists"
                
                return OperationResult(
                    success=True,
                    status=OperationStatus.SUCCESS,
                    message="Story already in MkDocs navigation",
                    data={
                        'mkdocs_path': str(mkdocs_path),
                        'navigation_updated': False,
                        'story_entry': story_entry_name
                    }
                )
            
            # Add story to navigation (at the top of the nav list)
            nav.insert(0, {story_entry_name: story_path})
            mkdocs_config['nav'] = nav
            
            # Write back to mkdocs.yml
            with open(mkdocs_path, 'w', encoding='utf-8') as f:
                yaml.dump(mkdocs_config, f, default_flow_style=False, sort_keys=False)
            
            context['mkdocs_updated'] = True
            context['navigation_entry'] = story_entry_name
            
            logger.info(f"Added story to MkDocs navigation: {story_entry_name}")
            
            return OperationResult(
                success=True,
                status=OperationStatus.SUCCESS,
                message=f"Story added to MkDocs navigation: {story_entry_name}",
                data={
                    'mkdocs_path': str(mkdocs_path),
                    'navigation_updated': True,
                    'story_entry': story_entry_name,
                    'story_path': story_path
                }
            )
        
        except yaml.YAMLError as e:
            logger.error(f"YAML parsing error: {e}")
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Failed to parse mkdocs.yml: {e}",
                errors=[str(e)]
            )
        
        except Exception as e:
            logger.error(f"Failed to update MkDocs navigation: {e}", exc_info=True)
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Failed to update MkDocs navigation: {e}",
                errors=[str(e)]
            )
    
    def rollback(self, context: Dict[str, Any]) -> bool:
        """
        Rollback MkDocs navigation update.
        
        Note: This is a simplified rollback that doesn't restore the exact
        previous state. For production, consider backing up mkdocs.yml.
        
        Args:
            context: Shared context dictionary
        
        Returns:
            True if rollback succeeded
        """
        try:
            if not context.get('mkdocs_updated', False):
                logger.debug("MkDocs navigation was not updated, no rollback needed")
                return True
            
            logger.info("Rolling back MkDocs navigation update...")
            
            project_root = Path(context['project_root'])
            mkdocs_path = project_root / "mkdocs.yml"
            
            if not mkdocs_path.exists():
                logger.warning("mkdocs.yml not found, cannot rollback")
                return False
            
            # Read current config (use FullLoader to handle MkDocs custom tags)
            with open(mkdocs_path, 'r', encoding='utf-8') as f:
                try:
                    mkdocs_config = yaml.load(f, Loader=yaml.FullLoader)
                except AttributeError:
                    # Fallback for older PyYAML versions
                    mkdocs_config = yaml.load(f)
            
            # Remove story entry
            nav = mkdocs_config.get('nav', [])
            story_entry_name = context.get('navigation_entry', "The Awakening (Complete)")
            
            nav_filtered = []
            for item in nav:
                if isinstance(item, dict):
                    # Remove if it's the story entry
                    if story_entry_name not in item:
                        nav_filtered.append(item)
                else:
                    nav_filtered.append(item)
            
            mkdocs_config['nav'] = nav_filtered
            
            # Write back
            with open(mkdocs_path, 'w', encoding='utf-8') as f:
                yaml.dump(mkdocs_config, f, default_flow_style=False, sort_keys=False)
            
            logger.info("MkDocs navigation rollback complete")
            
            context.pop('mkdocs_updated', None)
            context.pop('navigation_entry', None)
            
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
            True if not in quick profile and not dry_run
        """
        profile = context.get('profile', 'standard')
        dry_run = context.get('dry_run', False)
        return profile != 'quick' and not dry_run
    
    def get_progress_message(self) -> str:
        """Get progress message."""
        return "Updating MkDocs navigation..."


def register():
    """Register the module."""
    return UpdateMkDocsIndexModule()
