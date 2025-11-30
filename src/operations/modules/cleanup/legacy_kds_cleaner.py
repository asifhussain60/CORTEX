"""
Legacy Cleanup Handlers for CORTEX

Handles cleanup of legacy KDS (Key Data Streams) files and directories
from pre-CORTEX 2.0 era.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
"""

from pathlib import Path
from typing import List, Callable
import shutil
import logging

logger = logging.getLogger(__name__)


class LegacyKDSCleaner:
    """
    Cleans up legacy KDS prompt files and directories.
    
    Removes old Key Data Streams (KDS) prompts and folders that are no longer
    needed after CORTEX 2.0 deployment. Only keeps CORTEX.prompt.md and
    copilot-instructions.md in .github/prompts/.
    """
    
    def __init__(self, project_root: Path, log_action_callback: Callable, metrics):
        self.project_root = project_root
        self._log_action = log_action_callback
        self.metrics = metrics
    
    def cleanup(self, dry_run: bool) -> int:
        """
        Clean up legacy KDS files and directories.
        
        Legacy files removed:
        - Old prompt files: ask.prompt.md, continue.prompt.md, task.prompt.md, etc.
        - Old subdirectories: comm/, knowledge/, ops/, quality/, shared/, util/
        - Old root directories: _Portable, instructions, key-data-streams, learning, prompts.keys
        
        Args:
            dry_run: If True, only simulate cleanup without actual deletions
        
        Returns:
            int: Number of legacy files/directories removed
        """
        logger.info("Scanning for legacy KDS files...")
        
        cleaned_count = 0
        github_dir = self.project_root / '.github'
        
        if not github_dir.exists():
            logger.info("  No .github directory found - skipping")
            return 0
        
        # Define legacy prompt files to remove (keep only CORTEX.prompt.md and copilot-instructions.md)
        legacy_prompt_files = [
            'ask.prompt.md',
            'continue.prompt.md',
            'create-plan.prompt.md',
            'handoff.prompt.md',
            'healthcheck.prompt.md',
            'port-instructions.prompt.md',
            'stash.prompt.md',
            'task.prompt.md',
            'test-generation.prompt.md',
            'question.prompt.md',
            'analyze-learning.prompt.md',
            'data-streams.prompt.md',
            'total-recall.prompt.md',
            'commit.prompt.md',
            'sync.prompt.md',
            'cohesion-review.prompt.md',
            'refactor.prompt.md',
            'cleanup.prompt.md'
        ]
        
        # Define legacy directories to remove
        legacy_directories = [
            '.github/_Portable',
            '.github/instructions',
            '.github/key-data-streams',
            '.github/learning',
            '.github/prompts.keys',
            '.github/prompts/comm',
            '.github/prompts/knowledge',
            '.github/prompts/ops',
            '.github/prompts/quality',
            '.github/prompts/shared',
            '.github/prompts/util',
            '.github/prompts/prompts.keys',
            '.github/prompts/internal'
        ]
        
        # Remove legacy prompt files
        prompts_dir = github_dir / 'prompts'
        if prompts_dir.exists():
            for prompt_file in legacy_prompt_files:
                prompt_path = prompts_dir / prompt_file
                if prompt_path.exists():
                    if not dry_run:
                        try:
                            prompt_path.unlink()
                            logger.info(f"  Removed: {prompt_path.relative_to(self.project_root)}")
                            cleaned_count += 1
                            self._log_action('legacy_removed', prompt_path, "Legacy KDS prompt file")
                        except Exception as e:
                            self.metrics.errors.append(f"Failed to remove {prompt_path}: {e}")
                            logger.error(f"  ❌ Failed to remove {prompt_file}: {e}")
                    else:
                        logger.info(f"  [DRY RUN] Would remove: {prompt_path.relative_to(self.project_root)}")
                        cleaned_count += 1
        
        # Remove legacy directories
        for legacy_dir_str in legacy_directories:
            legacy_dir = self.project_root / legacy_dir_str
            if legacy_dir.exists() and legacy_dir.is_dir():
                if not dry_run:
                    try:
                        shutil.rmtree(legacy_dir)
                        logger.info(f"  Removed directory: {legacy_dir.relative_to(self.project_root)}")
                        cleaned_count += 1
                        self._log_action('legacy_removed', legacy_dir, "Legacy KDS directory")
                    except Exception as e:
                        self.metrics.errors.append(f"Failed to remove {legacy_dir}: {e}")
                        logger.error(f"  ❌ Failed to remove directory {legacy_dir.name}: {e}")
                else:
                    logger.info(f"  [DRY RUN] Would remove directory: {legacy_dir.relative_to(self.project_root)}")
                    cleaned_count += 1
        
        # Remove old .github.zip if it exists
        github_zip = github_dir / '.github.zip'
        if github_zip.exists():
            if not dry_run:
                try:
                    github_zip.unlink()
                    logger.info(f"  Removed: {github_zip.relative_to(self.project_root)}")
                    cleaned_count += 1
                    self._log_action('legacy_removed', github_zip, "Legacy archive file")
                except Exception as e:
                    self.metrics.errors.append(f"Failed to remove {github_zip}: {e}")
            else:
                logger.info(f"  [DRY RUN] Would remove: {github_zip.relative_to(self.project_root)}")
                cleaned_count += 1
        
        if cleaned_count == 0:
            logger.info("  ✓ No legacy KDS files found")
        else:
            logger.info(f"  ✓ Cleaned {cleaned_count} legacy items")
        
        return cleaned_count
