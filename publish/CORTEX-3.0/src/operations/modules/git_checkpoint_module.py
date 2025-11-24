"""
Git Checkpoint Module

Creates and validates git checkpoints before development work.
Implements GIT_CHECKPOINT_ENFORCEMENT Tier 0 instinct.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file

This module:
1. Creates git checkpoints (commits or tags) before development
2. Validates checkpoint existence and quality
3. Provides rollback capability
4. Enforces Tier 0 checkpoint governance rule
"""

from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import subprocess
import logging

from src.operations.base_operation_module import (
    BaseOperationModule,
    OperationResult,
    OperationModuleMetadata,
    OperationPhase
)

logger = logging.getLogger(__name__)


class CheckpointType:
    """Supported checkpoint types."""
    COMMIT = "commit"
    TAG = "tag"
    STASH = "stash"


class CheckpointViolation(Exception):
    """Raised when checkpoint enforcement is violated."""
    pass


class GitCheckpointModule(BaseOperationModule):
    """
    Creates and validates git checkpoints for development safety.
    
    Features:
    - Create commit checkpoints with standardized messages
    - Create tag checkpoints with timestamps
    - Create stash checkpoints for temporary saves
    - Validate checkpoint existence before development
    - Check for uncommitted changes
    - Provide checkpoint history and rollback info
    
    Example:
        module = GitCheckpointModule()
        
        # Create checkpoint before feature development
        result = module.execute({
            'operation': 'create',
            'message': 'before authentication implementation',
            'checkpoint_type': 'commit'
        })
        
        # Validate checkpoint exists
        result = module.execute({
            'operation': 'validate',
            'required_for': 'authentication feature'
        })
        
        # List recent checkpoints
        result = module.execute({
            'operation': 'list',
            'limit': 10
        })
    """
    
    def __init__(self):
        """Initialize Git Checkpoint Module."""
        super().__init__()
        self.repo_path = self._find_git_root()
    
    def get_metadata(self) -> OperationModuleMetadata:
        """
        Return metadata describing this module.
        
        Returns:
            OperationModuleMetadata with module information
        """
        return OperationModuleMetadata(
            module_id="git_checkpoint",
            name="Git Checkpoint",
            description="Creates and validates git checkpoints before development work",
            version="1.0.0",
            phase=OperationPhase.PRE_VALIDATION,
            dependencies=[],
            optional=False
        )
    
    def _find_git_root(self) -> Optional[Path]:
        """
        Find the git repository root.
        
        Returns:
            Path to .git directory or None if not in a git repo
        """
        current = Path.cwd()
        while current != current.parent:
            git_dir = current / ".git"
            if git_dir.exists():
                return current
            current = current.parent
        return None
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Execute git checkpoint operation.
        
        Args:
            context: Operation context with:
                - operation: 'create', 'validate', 'list', or 'rollback'
                - message: Checkpoint message (for create)
                - checkpoint_type: 'commit', 'tag', or 'stash' (for create)
                - required_for: Feature name (for validate)
                - checkpoint_id: Checkpoint to rollback to (for rollback)
                - limit: Number of checkpoints to list (for list)
        
        Returns:
            OperationResult with checkpoint information
        """
        if not self.repo_path:
            return OperationResult(
                success=False,
                message="Not in a git repository",
                data={"error": "No .git directory found"}
            )
        
        operation = context.get('operation', 'create')
        
        try:
            if operation == 'create':
                return self._create_checkpoint(context)
            elif operation == 'validate':
                return self._validate_checkpoint(context)
            elif operation == 'list':
                return self._list_checkpoints(context)
            elif operation == 'rollback':
                return self._rollback_to_checkpoint(context)
            else:
                return OperationResult(
                    success=False,
                    message=f"Unknown operation: {operation}",
                    data={"valid_operations": ["create", "validate", "list", "rollback"]}
                )
        
        except CheckpointViolation as e:
            return OperationResult(
                success=False,
                message=str(e),
                data={"violation": True, "alternatives": self._get_alternatives()}
            )
        except Exception as e:
            logger.error(f"Git checkpoint operation failed: {e}", exc_info=True)
            return OperationResult(
                success=False,
                message=f"Checkpoint operation failed: {str(e)}",
                data={"error": str(e)}
            )
    
    def _create_checkpoint(self, context: Dict[str, Any]) -> OperationResult:
        """
        Create a git checkpoint.
        
        Args:
            context: Must contain 'message' and optional 'checkpoint_type'
        
        Returns:
            OperationResult with checkpoint details
        """
        message = context.get('message', 'development checkpoint')
        checkpoint_type = context.get('checkpoint_type', CheckpointType.COMMIT)
        
        # First, check for uncommitted changes
        status_check = self._check_git_status()
        
        if checkpoint_type == CheckpointType.COMMIT:
            # If there are uncommitted changes, commit them
            if status_check['has_changes']:
                result = self._create_commit_checkpoint(message)
            else:
                # If no changes, create empty checkpoint commit
                result = self._create_empty_checkpoint(message)
        
        elif checkpoint_type == CheckpointType.TAG:
            # Tags don't require changes
            result = self._create_tag_checkpoint(message)
        
        elif checkpoint_type == CheckpointType.STASH:
            # Stash requires uncommitted changes
            if not status_check['has_changes']:
                return OperationResult(
                    success=False,
                    message="No changes to stash",
                    data=status_check
                )
            result = self._create_stash_checkpoint(message)
        
        else:
            return OperationResult(
                success=False,
                message=f"Unknown checkpoint type: {checkpoint_type}",
                data={"valid_types": [CheckpointType.COMMIT, CheckpointType.TAG, CheckpointType.STASH]}
            )
        
        return result
    
    def _check_git_status(self) -> Dict[str, Any]:
        """
        Check git status for uncommitted changes.
        
        Returns:
            Dictionary with status information
        """
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            output = result.stdout.strip()
            has_changes = bool(output)
            
            # Parse changes
            modified = []
            added = []
            deleted = []
            untracked = []
            
            for line in output.split('\n'):
                if not line:
                    continue
                status = line[:2]
                filepath = line[3:]
                
                if 'M' in status:
                    modified.append(filepath)
                elif 'A' in status:
                    added.append(filepath)
                elif 'D' in status:
                    deleted.append(filepath)
                elif '?' in status:
                    untracked.append(filepath)
            
            return {
                'has_changes': has_changes,
                'modified': modified,
                'added': added,
                'deleted': deleted,
                'untracked': untracked,
                'total_changes': len(modified) + len(added) + len(deleted)
            }
        
        except subprocess.CalledProcessError as e:
            logger.error(f"Git status check failed: {e}")
            return {
                'has_changes': False,
                'error': str(e)
            }
    
    def _create_commit_checkpoint(self, message: str) -> OperationResult:
        """
        Create a commit checkpoint with staged or all changes.
        
        Args:
            message: Checkpoint message
        
        Returns:
            OperationResult with commit details
        """
        try:
            # Add all changes
            subprocess.run(
                ['git', 'add', '-A'],
                cwd=self.repo_path,
                check=True,
                capture_output=True
            )
            
            # Create commit
            commit_message = f"checkpoint: {message}"
            subprocess.run(
                ['git', 'commit', '-m', commit_message],
                cwd=self.repo_path,
                check=True,
                capture_output=True,
                text=True
            )
            
            # Get commit hash
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            commit_hash = result.stdout.strip()
            
            return OperationResult(
                success=True,
                message=f"Checkpoint commit created: {commit_hash[:8]}",
                data={
                    'checkpoint_type': 'commit',
                    'commit_hash': commit_hash,
                    'commit_message': commit_message,
                    'short_hash': commit_hash[:8]
                }
            )
        
        except subprocess.CalledProcessError as e:
            return OperationResult(
                success=False,
                message=f"Failed to create commit checkpoint: {e}",
                data={'error': str(e)}
            )
    
    def _create_empty_checkpoint(self, message: str) -> OperationResult:
        """
        Create an empty checkpoint commit (no changes).
        
        Args:
            message: Checkpoint message
        
        Returns:
            OperationResult with commit details
        """
        try:
            commit_message = f"checkpoint: {message}"
            subprocess.run(
                ['git', 'commit', '--allow-empty', '-m', commit_message],
                cwd=self.repo_path,
                check=True,
                capture_output=True,
                text=True
            )
            
            # Get commit hash
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            commit_hash = result.stdout.strip()
            
            return OperationResult(
                success=True,
                message=f"Empty checkpoint commit created: {commit_hash[:8]}",
                data={
                    'checkpoint_type': 'commit',
                    'commit_hash': commit_hash,
                    'commit_message': commit_message,
                    'short_hash': commit_hash[:8],
                    'empty': True
                }
            )
        
        except subprocess.CalledProcessError as e:
            return OperationResult(
                success=False,
                message=f"Failed to create empty checkpoint: {e}",
                data={'error': str(e)}
            )
    
    def _create_tag_checkpoint(self, message: str) -> OperationResult:
        """
        Create a tag checkpoint at current HEAD.
        
        Args:
            message: Checkpoint message
        
        Returns:
            OperationResult with tag details
        """
        try:
            # Generate tag name with timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            tag_name = f"checkpoint-{timestamp}"
            
            # Create annotated tag
            subprocess.run(
                ['git', 'tag', '-a', tag_name, '-m', f"Checkpoint: {message}"],
                cwd=self.repo_path,
                check=True,
                capture_output=True
            )
            
            # Get current commit
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            commit_hash = result.stdout.strip()
            
            return OperationResult(
                success=True,
                message=f"Checkpoint tag created: {tag_name}",
                data={
                    'checkpoint_type': 'tag',
                    'tag_name': tag_name,
                    'commit_hash': commit_hash,
                    'short_hash': commit_hash[:8],
                    'timestamp': timestamp
                }
            )
        
        except subprocess.CalledProcessError as e:
            return OperationResult(
                success=False,
                message=f"Failed to create tag checkpoint: {e}",
                data={'error': str(e)}
            )
    
    def _create_stash_checkpoint(self, message: str) -> OperationResult:
        """
        Create a stash checkpoint (temporary save).
        
        Args:
            message: Checkpoint message
        
        Returns:
            OperationResult with stash details
        """
        try:
            stash_message = f"WIP: checkpoint {message}"
            
            subprocess.run(
                ['git', 'stash', 'save', stash_message],
                cwd=self.repo_path,
                check=True,
                capture_output=True,
                text=True
            )
            
            # Get stash list
            result = subprocess.run(
                ['git', 'stash', 'list', '-1'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            stash_info = result.stdout.strip()
            
            return OperationResult(
                success=True,
                message=f"Checkpoint stash created",
                data={
                    'checkpoint_type': 'stash',
                    'stash_message': stash_message,
                    'stash_info': stash_info
                }
            )
        
        except subprocess.CalledProcessError as e:
            return OperationResult(
                success=False,
                message=f"Failed to create stash checkpoint: {e}",
                data={'error': str(e)}
            )
    
    def _validate_checkpoint(self, context: Dict[str, Any]) -> OperationResult:
        """
        Validate that a checkpoint exists before development.
        
        Args:
            context: Must contain 'required_for' (feature name)
        
        Returns:
            OperationResult indicating if checkpoint is valid
        """
        required_for = context.get('required_for', 'development work')
        
        # Check git status
        status = self._check_git_status()
        
        if status['has_changes']:
            raise CheckpointViolation(
                f"Uncommitted changes detected before starting '{required_for}'. "
                f"Create checkpoint first:\n"
                f"  Modified: {len(status['modified'])} files\n"
                f"  Added: {len(status['added'])} files\n"
                f"  Deleted: {len(status['deleted'])} files\n"
                f"  Untracked: {len(status['untracked'])} files"
            )
        
        # Check if recent checkpoint exists
        try:
            result = subprocess.run(
                ['git', 'log', '-1', '--oneline'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            last_commit = result.stdout.strip()
            
            return OperationResult(
                success=True,
                message=f"Checkpoint validation passed for '{required_for}'",
                data={
                    'valid': True,
                    'clean_working_tree': True,
                    'last_commit': last_commit
                }
            )
        
        except subprocess.CalledProcessError as e:
            return OperationResult(
                success=False,
                message=f"Checkpoint validation failed: {e}",
                data={'error': str(e)}
            )
    
    def _list_checkpoints(self, context: Dict[str, Any]) -> OperationResult:
        """
        List recent checkpoints.
        
        Args:
            context: Optional 'limit' for number of checkpoints
        
        Returns:
            OperationResult with checkpoint list
        """
        limit = context.get('limit', 10)
        
        try:
            # Get commit checkpoints
            result = subprocess.run(
                ['git', 'log', f'-{limit}', '--oneline', '--grep=checkpoint:'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            commit_checkpoints = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split(' ', 1)
                    commit_checkpoints.append({
                        'type': 'commit',
                        'hash': parts[0],
                        'message': parts[1] if len(parts) > 1 else ''
                    })
            
            # Get tag checkpoints
            result = subprocess.run(
                ['git', 'tag', '-l', 'checkpoint-*'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            tag_checkpoints = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    tag_checkpoints.append({
                        'type': 'tag',
                        'name': line
                    })
            
            return OperationResult(
                success=True,
                message=f"Found {len(commit_checkpoints)} commit checkpoints and {len(tag_checkpoints)} tag checkpoints",
                data={
                    'commit_checkpoints': commit_checkpoints,
                    'tag_checkpoints': tag_checkpoints,
                    'total': len(commit_checkpoints) + len(tag_checkpoints)
                }
            )
        
        except subprocess.CalledProcessError as e:
            return OperationResult(
                success=False,
                message=f"Failed to list checkpoints: {e}",
                data={'error': str(e)}
            )
    
    def _rollback_to_checkpoint(self, context: Dict[str, Any]) -> OperationResult:
        """
        Rollback to a specific checkpoint.
        
        Args:
            context: Must contain 'checkpoint_id' (commit hash or tag name)
        
        Returns:
            OperationResult with rollback information
        """
        checkpoint_id = context.get('checkpoint_id')
        
        if not checkpoint_id:
            return OperationResult(
                success=False,
                message="Checkpoint ID required for rollback",
                data={'error': 'Missing checkpoint_id'}
            )
        
        try:
            # Verify checkpoint exists
            subprocess.run(
                ['git', 'rev-parse', checkpoint_id],
                cwd=self.repo_path,
                check=True,
                capture_output=True
            )
            
            # Create safety tag before rollback
            safety_tag = f"before-rollback-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}"
            subprocess.run(
                ['git', 'tag', safety_tag],
                cwd=self.repo_path,
                check=True,
                capture_output=True
            )
            
            # Perform rollback
            subprocess.run(
                ['git', 'reset', '--hard', checkpoint_id],
                cwd=self.repo_path,
                check=True,
                capture_output=True
            )
            
            return OperationResult(
                success=True,
                message=f"Rolled back to checkpoint: {checkpoint_id}",
                data={
                    'checkpoint_id': checkpoint_id,
                    'safety_tag': safety_tag,
                    'recovery_command': f"git reset --hard {safety_tag}"
                }
            )
        
        except subprocess.CalledProcessError as e:
            return OperationResult(
                success=False,
                message=f"Rollback failed: {e}",
                data={'error': str(e)}
            )
    
    def _get_alternatives(self) -> List[str]:
        """
        Get alternative actions when checkpoint is missing.
        
        Returns:
            List of alternative suggestions
        """
        return [
            "Create commit checkpoint: git commit -m 'checkpoint: before [feature] development'",
            "Create tag checkpoint: git tag -a checkpoint-[timestamp] -m 'Checkpoint before [feature]'",
            "Stash changes: git stash save 'WIP: checkpoint before [feature]'",
            "Use automated module: GitCheckpointModule().execute({'operation': 'create', 'message': '[feature]'})"
        ]


# Module registration for CORTEX operations
def get_module():
    """Factory function for module registration."""
    return GitCheckpointModule()
