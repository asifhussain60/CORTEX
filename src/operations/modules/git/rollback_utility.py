"""
Rollback Utility

Fast, lightweight rollback management for TDD workflows.
Replaces heavy orchestrator with focused, <3s execution utility.

Features:
- Checkpoint validation before rollback
- Git reset to checkpoint with safety checks
- Uncommitted changes detection
- Dry-run mode for preview
- User confirmation prompts

Version: 3.0.0 (Utility Migration)
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import subprocess
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import CORTEX config
try:
    from src.config import config
    CORTEX_ROOT = Path(config.root_path)
except ImportError:
    # Fallback if config not available
    CORTEX_ROOT = Path(__file__).resolve().parents[4]


@dataclass
class RollbackResult:
    """Result of rollback operation."""
    success: bool
    message: str
    checkpoint_id: Optional[str] = None
    executed: bool = False
    safe: bool = True
    warning: Optional[str] = None
    details: Optional[str] = None


def run_rollback_utility(
    checkpoint_id: str,
    dry_run: bool = False,
    force: bool = False,
    skip_confirmation: bool = False
) -> RollbackResult:
    """
    Main entry point for rollback utility.
    
    Args:
        checkpoint_id: Checkpoint SHA to rollback to
        dry_run: If True, preview changes without executing
        force: If True, bypass safety checks (dangerous!)
        skip_confirmation: If True, skip user confirmation prompt
        
    Returns:
        RollbackResult with operation outcome
    """
    logger.info(f"🔙 Rollback Utility - Checkpoint: {checkpoint_id[:8]}")
    
    # Validate git repository
    validation = _validate_git_state()
    if not validation.success:
        return validation
    
    # Validate checkpoint exists
    checkpoint_validation = _validate_checkpoint(checkpoint_id)
    if not checkpoint_validation.success:
        return checkpoint_validation
    
    # Dry-run mode: show preview only
    if dry_run:
        return _preview_rollback(checkpoint_id)
    
    # Force mode: skip safety checks (dangerous!)
    if force:
        logger.warning("⚠️ FORCED ROLLBACK - Bypassing safety checks")
        return _execute_rollback(checkpoint_id, forced=True)
    
    # Normal mode: perform safety checks
    safety_check = _check_safety(checkpoint_id)
    if not safety_check.success:
        return safety_check
    
    # User confirmation
    if not skip_confirmation:
        confirmation = _confirm_rollback(checkpoint_id)
        if not confirmation:
            return RollbackResult(
                success=False,
                message="Rollback cancelled by user",
                checkpoint_id=checkpoint_id,
                executed=False
            )
    
    # Execute rollback
    return _execute_rollback(checkpoint_id, forced=False)


def _validate_git_state() -> RollbackResult:
    """
    Validate git repository state.
    
    Returns:
        RollbackResult with validation outcome
    """
    try:
        # Check if we're in a git repository
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            cwd=CORTEX_ROOT,
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode != 0:
            return RollbackResult(
                success=False,
                message="Not a git repository. Run 'git init' first.",
                details=result.stderr.strip()
            )
        
        return RollbackResult(success=True, message="Git repository validated")
        
    except Exception as e:
        return RollbackResult(
            success=False,
            message=f"Git validation error: {str(e)}"
        )


def _validate_checkpoint(checkpoint_id: str) -> RollbackResult:
    """
    Validate that checkpoint exists in git history.
    
    Args:
        checkpoint_id: Checkpoint SHA to validate
        
    Returns:
        RollbackResult with validation outcome
    """
    try:
        # Check if checkpoint exists in git
        result = subprocess.run(
            ["git", "cat-file", "-t", checkpoint_id],
            cwd=CORTEX_ROOT,
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode != 0:
            return RollbackResult(
                success=False,
                message=f"Invalid checkpoint: {checkpoint_id[:8]} not found in git history",
                checkpoint_id=checkpoint_id
            )
        
        # Verify it's a commit object
        obj_type = result.stdout.strip()
        if obj_type != "commit":
            return RollbackResult(
                success=False,
                message=f"Invalid checkpoint: {checkpoint_id[:8]} is not a commit (type: {obj_type})",
                checkpoint_id=checkpoint_id
            )
        
        return RollbackResult(
            success=True,
            message=f"Checkpoint {checkpoint_id[:8]} validated",
            checkpoint_id=checkpoint_id
        )
        
    except Exception as e:
        return RollbackResult(
            success=False,
            message=f"Checkpoint validation error: {str(e)}",
            checkpoint_id=checkpoint_id
        )


def _check_safety(checkpoint_id: str) -> RollbackResult:
    """
    Perform safety checks before rollback.
    
    Args:
        checkpoint_id: Checkpoint to rollback to
        
    Returns:
        RollbackResult with safety check outcome
    """
    try:
        # Check for uncommitted changes
        status_result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=CORTEX_ROOT,
            capture_output=True,
            text=True,
            check=False
        )
        
        if status_result.stdout.strip():
            uncommitted = []
            for line in status_result.stdout.strip().split('\n'):
                if line.strip():
                    filename = line[3:].strip()
                    uncommitted.append(filename)
            
            files_list = '\n'.join(f"  - {f}" for f in uncommitted[:10])
            if len(uncommitted) > 10:
                files_list += f"\n  ... and {len(uncommitted) - 10} more file(s)"
            
            return RollbackResult(
                success=False,
                message="Uncommitted changes detected",
                checkpoint_id=checkpoint_id,
                safe=False,
                warning="Uncommitted changes must be committed or stashed",
                details=f"The following files have uncommitted changes:\n{files_list}\n\n"
                       f"Commit or stash changes before rollback, or use --force to override (⚠️ will lose changes!)"
            )
        
        # Check for merge in progress
        merge_head = CORTEX_ROOT / ".git" / "MERGE_HEAD"
        if merge_head.exists():
            return RollbackResult(
                success=False,
                message="Merge in progress",
                checkpoint_id=checkpoint_id,
                safe=False,
                warning="Cannot rollback during merge",
                details="Complete or abort the merge before attempting rollback:\n"
                       "  git merge --abort  (to cancel merge)\n"
                       "  git commit         (to complete merge)"
            )
        
        # All checks passed
        return RollbackResult(
            success=True,
            message="Safety checks passed",
            checkpoint_id=checkpoint_id,
            safe=True
        )
        
    except Exception as e:
        return RollbackResult(
            success=False,
            message=f"Safety check error: {str(e)}",
            checkpoint_id=checkpoint_id,
            safe=False
        )


def _preview_rollback(checkpoint_id: str) -> RollbackResult:
    """
    Preview rollback changes (dry-run mode).
    
    Args:
        checkpoint_id: Checkpoint to preview
        
    Returns:
        RollbackResult with preview details
    """
    try:
        # Get diff between HEAD and checkpoint
        diff_result = subprocess.run(
            ["git", "diff", "HEAD", checkpoint_id, "--stat"],
            cwd=CORTEX_ROOT,
            capture_output=True,
            text=True,
            check=False
        )
        
        if diff_result.returncode != 0:
            return RollbackResult(
                success=False,
                message="Failed to generate rollback preview",
                checkpoint_id=checkpoint_id,
                details=diff_result.stderr.strip()
            )
        
        preview = diff_result.stdout.strip()
        if not preview:
            preview = "No changes (already at checkpoint)"
        
        # Get commit message for checkpoint
        commit_msg_result = subprocess.run(
            ["git", "log", "-1", "--pretty=format:%s", checkpoint_id],
            cwd=CORTEX_ROOT,
            capture_output=True,
            text=True,
            check=False
        )
        
        commit_msg = commit_msg_result.stdout.strip() if commit_msg_result.returncode == 0 else "Unknown"
        
        details = f"Checkpoint: {checkpoint_id[:8]}\nMessage: {commit_msg}\n\nChanges:\n{preview}"
        
        return RollbackResult(
            success=True,
            message=f"Dry-run: Would rollback to {checkpoint_id[:8]}",
            checkpoint_id=checkpoint_id,
            executed=False,
            details=details
        )
        
    except Exception as e:
        return RollbackResult(
            success=False,
            message=f"Preview error: {str(e)}",
            checkpoint_id=checkpoint_id
        )


def _confirm_rollback(checkpoint_id: str) -> bool:
    """
    Prompt user for rollback confirmation.
    
    Args:
        checkpoint_id: Checkpoint to rollback to
        
    Returns:
        True if user confirms, False otherwise
    """
    print("\n" + "=" * 60)
    print("⚠️  ROLLBACK CONFIRMATION REQUIRED")
    print("=" * 60)
    print(f"\nYou are about to rollback to checkpoint: {checkpoint_id[:8]}")
    print("\n⚠️  WARNING: This will discard all changes after this checkpoint!")
    print("This operation cannot be easily undone.")
    print("\n" + "=" * 60)
    
    response = input("\nType 'yes' to confirm rollback: ").strip().lower()
    
    return response == 'yes'


def _execute_rollback(checkpoint_id: str, forced: bool = False) -> RollbackResult:
    """
    Execute git reset to checkpoint.
    
    Args:
        checkpoint_id: Checkpoint to rollback to
        forced: Whether this is a forced rollback
        
    Returns:
        RollbackResult with execution outcome
    """
    try:
        # Execute git reset --hard
        reset_result = subprocess.run(
            ["git", "reset", "--hard", checkpoint_id],
            cwd=CORTEX_ROOT,
            capture_output=True,
            text=True,
            check=False
        )
        
        if reset_result.returncode != 0:
            return RollbackResult(
                success=False,
                message=f"Git reset failed: {reset_result.stderr.strip()}",
                checkpoint_id=checkpoint_id,
                executed=False
            )
        
        # Get current branch
        branch_result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=CORTEX_ROOT,
            capture_output=True,
            text=True,
            check=False
        )
        
        current_branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown"
        
        mode_str = "FORCED" if forced else "standard"
        details = f"Branch: {current_branch}\nCheckpoint: {checkpoint_id[:8]}\nMode: {mode_str}"
        
        return RollbackResult(
            success=True,
            message=f"✅ Rollback to {checkpoint_id[:8]} completed successfully",
            checkpoint_id=checkpoint_id,
            executed=True,
            details=details
        )
        
    except Exception as e:
        return RollbackResult(
            success=False,
            message=f"Rollback execution error: {str(e)}",
            checkpoint_id=checkpoint_id,
            executed=False
        )


# CLI test execution
if __name__ == "__main__":
    print("=" * 60)
    print("Rollback Utility - Direct Test")
    print("=" * 60)
    
    # Get current HEAD for safe testing
    head_result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=CORTEX_ROOT,
        capture_output=True,
        text=True,
        check=False
    )
    
    if head_result.returncode != 0:
        print("❌ Not in a git repository")
        exit(1)
    
    current_head = head_result.stdout.strip()
    
    # Test 1: Dry-run mode (safe - no changes)
    print(f"\n[Test 1] Dry-run rollback to HEAD ({current_head[:8]})...")
    result = run_rollback_utility(
        checkpoint_id=current_head,
        dry_run=True,
        skip_confirmation=True
    )
    
    print(f"Success: {result.success}")
    print(f"Message: {result.message}")
    print(f"Executed: {result.executed}")
    if result.details:
        print(f"\nDetails:\n{result.details}")
    
    # Test 2: Validate checkpoint
    print("\n" + "=" * 60)
    print("[Test 2] Validate current HEAD as checkpoint...")
    validation = _validate_checkpoint(current_head)
    
    print(f"Success: {validation.success}")
    print(f"Message: {validation.message}")
    
    # Test 3: Safety checks
    print("\n" + "=" * 60)
    print("[Test 3] Run safety checks...")
    safety = _check_safety(current_head)
    
    print(f"Success: {safety.success}")
    print(f"Message: {safety.message}")
    print(f"Safe: {safety.safe}")
    if safety.warning:
        print(f"Warning: {safety.warning}")
    if safety.details:
        print(f"Details:\n{safety.details}")
    
    print("\n" + "=" * 60)
    print("✅ Utility tests complete (no actual rollback performed)")
    print("=" * 60)
