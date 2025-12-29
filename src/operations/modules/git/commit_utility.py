"""
CommitUtility - Fast commit utility.

Lightweight replacement for CommitOrchestrator.
Design Goals:
- Fast: <3 seconds execution
- Simple: Clear pass/fail
- Safe: Pre-flight checks + checkpoints
- Direct: Minimal dependencies

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import subprocess
import logging
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Any, Optional

from src.config import config

logger = logging.getLogger(__name__)


@dataclass
class CommitResult:
    """Result from commit utility."""
    success: bool
    message: str
    commit_hash: Optional[str] = None
    checkpoint_created: bool = False
    files_committed: int = 0
    details: Optional[Dict[str, Any]] = None


def run_commit_utility(
    auto_add: bool = True,
    create_checkpoint: bool = False
) -> Dict[str, Any]:
    """
    Run commit utility.
    
    Args:
        auto_add: Auto-stage all changes
        create_checkpoint: Create safety checkpoint
    
    Returns:
        Dict with success, message, and commit data
    """
    repo_path = Path(config.root_path)
    
    # Pre-flight validation
    validation = _validate_git_state(repo_path)
    if not validation["success"]:
        return {
            "success": False,
            "message": validation["message"],
            "data": None
        }
    
    # Stage files if requested
    if auto_add:
        stage_result = _stage_files(repo_path)
        if not stage_result["success"]:
            return {
                "success": False,
                "message": stage_result["message"],
                "data": None
            }
    
    # Create checkpoint if requested
    checkpoint_result = {"success": False}
    if create_checkpoint:
        checkpoint_result = _create_checkpoint(repo_path)
    
    # Generate commit message
    message = _generate_commit_message(repo_path)
    
    # Execute commit
    commit_result = _execute_commit(repo_path, message)
    
    if not commit_result["success"]:
        return {
            "success": False,
            "message": commit_result["message"],
            "data": None
        }
    
    # Success
    return {
        "success": True,
        "message": f"Committed {commit_result['files_count']} file(s): {commit_result['commit_hash'][:7]}",
        "data": {
            "commit_hash": commit_result["commit_hash"],
            "files_committed": commit_result["files_count"],
            "checkpoint_created": checkpoint_result["success"],
            "message": message
        }
    }


def _validate_git_state(repo_path: Path) -> Dict[str, Any]:
    """Validate git repository state."""
    try:
        # Check if git repo
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return {
                "success": False,
                "message": "Not a git repository"
            }
        
        # Check for changes
        status_result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        
        if not status_result.stdout.strip():
            return {
                "success": False,
                "message": "No changes to commit"
            }
        
        return {"success": True}
    
    except Exception as e:
        return {
            "success": False,
            "message": f"Validation failed: {e}"
        }


def _stage_files(repo_path: Path) -> Dict[str, Any]:
    """Stage all files."""
    try:
        result = subprocess.run(
            ["git", "add", "-A"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return {
                "success": False,
                "message": f"Failed to stage files: {result.stderr}"
            }
        
        return {"success": True}
    
    except Exception as e:
        return {
            "success": False,
            "message": f"Staging failed: {e}"
        }


def _create_checkpoint(repo_path: Path) -> Dict[str, Any]:
    """Create safety checkpoint."""
    try:
        # Get current commit hash
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return {
                "success": True,
                "checkpoint_hash": result.stdout.strip()
            }
        
        return {"success": False}
    
    except Exception as e:
        logger.warning(f"Checkpoint creation failed: {e}")
        return {"success": False}


def _generate_commit_message(repo_path: Path) -> str:
    """Generate automatic commit message."""
    try:
        # Get changed files
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        
        files = result.stdout.strip().split('\n') if result.stdout.strip() else []
        file_count = len(files)
        
        # Generate message
        if file_count == 0:
            return "chore: update files"
        elif file_count == 1:
            return f"chore: update {files[0]}"
        else:
            return f"chore: update {file_count} files"
    
    except Exception:
        return "chore: automated commit"


def _execute_commit(repo_path: Path, message: str) -> Dict[str, Any]:
    """Execute git commit."""
    try:
        result = subprocess.run(
            ["git", "commit", "-m", message],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return {
                "success": False,
                "message": f"Commit failed: {result.stderr}"
            }
        
        # Get commit hash
        hash_result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        
        # Count files
        count_result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "HEAD~1"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        files_count = len(count_result.stdout.strip().split('\n')) if count_result.stdout.strip() else 0
        
        return {
            "success": True,
            "commit_hash": hash_result.stdout.strip() if hash_result.returncode == 0 else "unknown",
            "files_count": files_count
        }
    
    except Exception as e:
        return {
            "success": False,
            "message": f"Commit execution failed: {e}"
        }


if __name__ == "__main__":
    # Test execution
    result = run_commit_utility()
    print(f"\n{'='*60}")
    print(f"Commit Utility Test")
    print(f"{'='*60}\n")
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    if result.get('data'):
        print(f"\nDetails:")
        for key, value in result['data'].items():
            print(f"  {key}: {value}")
