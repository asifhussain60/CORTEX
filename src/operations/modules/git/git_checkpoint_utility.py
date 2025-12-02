"""
Git Checkpoint Utility

Fast, lightweight checkpoint management for TDD workflows.
Replaces heavy orchestrator with focused, <2s execution utility.

Features:
- Checkpoint creation with metadata
- List checkpoints with timestamps
- 30-day retention enforcement
- HEAD hash capture for safety

Version: 3.0.0 (Utility Migration)
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import subprocess
import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
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
class CheckpointResult:
    """Result of checkpoint operation."""
    success: bool
    message: str
    checkpoint_id: Optional[str] = None  # Commit SHA
    checkpoint_count: int = 0
    checkpoints: Optional[List[Dict]] = None
    details: Optional[str] = None


def run_checkpoint_utility(
    action: str = "create",
    session_id: Optional[str] = None,
    phase: Optional[str] = None,
    message: Optional[str] = None,
    list_all: bool = False
) -> CheckpointResult:
    """
    Main entry point for git checkpoint utility.
    
    Args:
        action: Operation to perform ("create" or "list")
        session_id: TDD session identifier (for create)
        phase: Current phase (RED, GREEN, REFACTOR)
        message: Optional custom checkpoint message
        list_all: Show all checkpoints including expired
        
    Returns:
        CheckpointResult with operation outcome
    """
    logger.info(f"🔖 Git Checkpoint Utility - Action: {action}")
    
    # Validate git repository
    validation = _validate_git_state()
    if not validation.success:
        return validation
    
    if action == "create":
        return _create_checkpoint(session_id, phase, message)
    elif action == "list":
        return _list_checkpoints(list_all)
    else:
        return CheckpointResult(
            success=False,
            message=f"Unknown action: {action}. Use 'create' or 'list'."
        )


def _validate_git_state() -> CheckpointResult:
    """
    Validate git repository state.
    
    Returns:
        CheckpointResult with validation outcome
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
            return CheckpointResult(
                success=False,
                message="Not a git repository. Run 'git init' first.",
                details=result.stderr.strip()
            )
        
        return CheckpointResult(success=True, message="Git repository validated")
        
    except Exception as e:
        return CheckpointResult(
            success=False,
            message=f"Git validation error: {str(e)}"
        )


def _create_checkpoint(
    session_id: Optional[str],
    phase: Optional[str],
    message: Optional[str]
) -> CheckpointResult:
    """
    Create a new checkpoint with current git state.
    
    Args:
        session_id: TDD session identifier
        phase: Current phase (RED, GREEN, REFACTOR)
        message: Optional custom message
        
    Returns:
        CheckpointResult with checkpoint details
    """
    try:
        # Get current commit SHA (HEAD)
        sha_result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=CORTEX_ROOT,
            capture_output=True,
            text=True,
            check=False
        )
        
        if sha_result.returncode != 0:
            return CheckpointResult(
                success=False,
                message="Failed to get current commit SHA",
                details=sha_result.stderr.strip()
            )
        
        commit_sha = sha_result.stdout.strip()
        
        # Get current branch
        branch_result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=CORTEX_ROOT,
            capture_output=True,
            text=True,
            check=False
        )
        
        current_branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown"
        
        # Check for uncommitted changes
        status_result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=CORTEX_ROOT,
            capture_output=True,
            text=True,
            check=False
        )
        
        has_changes = bool(status_result.stdout.strip())
        
        # Create checkpoint metadata
        checkpoint = {
            "checkpoint_id": commit_sha,
            "session_id": session_id or "manual",
            "phase": phase or "checkpoint",
            "branch": current_branch,
            "timestamp": datetime.now().isoformat(),
            "message": message or f"Checkpoint at {commit_sha[:8]}",
            "has_uncommitted_changes": has_changes
        }
        
        # Load existing checkpoints
        checkpoints_file = CORTEX_ROOT / ".cortex" / "checkpoints.json"
        checkpoints_file.parent.mkdir(parents=True, exist_ok=True)
        
        if checkpoints_file.exists():
            try:
                data = json.loads(checkpoints_file.read_text())
                checkpoints = data.get("checkpoints", [])
            except Exception:
                checkpoints = []
        else:
            checkpoints = []
        
        # Add new checkpoint
        checkpoints.append(checkpoint)
        
        # Enforce 30-day retention
        checkpoints = _enforce_retention(checkpoints)
        
        # Save checkpoints
        checkpoints_file.write_text(
            json.dumps({"checkpoints": checkpoints}, indent=2)
        )
        
        details = f"Branch: {current_branch}\nSHA: {commit_sha[:8]}\nPhase: {phase or 'N/A'}"
        if has_changes:
            details += "\n⚠️ Uncommitted changes detected"
        
        return CheckpointResult(
            success=True,
            message=f"Checkpoint created: {commit_sha[:8]}",
            checkpoint_id=commit_sha,
            checkpoint_count=len(checkpoints),
            details=details
        )
        
    except Exception as e:
        return CheckpointResult(
            success=False,
            message=f"Checkpoint creation failed: {str(e)}"
        )


def _list_checkpoints(list_all: bool = False) -> CheckpointResult:
    """
    List available checkpoints.
    
    Args:
        list_all: Show all checkpoints including expired
        
    Returns:
        CheckpointResult with checkpoint list
    """
    try:
        checkpoints_file = CORTEX_ROOT / ".cortex" / "checkpoints.json"
        
        if not checkpoints_file.exists():
            return CheckpointResult(
                success=True,
                message="No checkpoints found",
                checkpoint_count=0,
                checkpoints=[]
            )
        
        data = json.loads(checkpoints_file.read_text())
        all_checkpoints = data.get("checkpoints", [])
        
        if not list_all:
            # Filter to only recent checkpoints (30 days)
            cutoff = datetime.now() - timedelta(days=30)
            all_checkpoints = [
                cp for cp in all_checkpoints
                if datetime.fromisoformat(cp["timestamp"]) > cutoff
            ]
        
        # Sort by timestamp (newest first)
        all_checkpoints.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return CheckpointResult(
            success=True,
            message=f"Found {len(all_checkpoints)} checkpoint(s)",
            checkpoint_count=len(all_checkpoints),
            checkpoints=all_checkpoints
        )
        
    except Exception as e:
        return CheckpointResult(
            success=False,
            message=f"Failed to list checkpoints: {str(e)}"
        )


def _enforce_retention(checkpoints: List[Dict]) -> List[Dict]:
    """
    Enforce 30-day retention policy.
    
    Args:
        checkpoints: List of checkpoint dictionaries
        
    Returns:
        Filtered list with only recent checkpoints
    """
    cutoff = datetime.now() - timedelta(days=30)
    
    filtered = []
    for checkpoint in checkpoints:
        try:
            timestamp = datetime.fromisoformat(checkpoint["timestamp"])
            if timestamp > cutoff:
                filtered.append(checkpoint)
            else:
                logger.debug(f"Removing expired checkpoint: {checkpoint['checkpoint_id'][:8]}")
        except Exception as e:
            logger.warning(f"Invalid checkpoint timestamp: {e}")
            # Keep checkpoint if we can't parse timestamp (safer)
            filtered.append(checkpoint)
    
    return filtered


# CLI test execution
if __name__ == "__main__":
    print("=" * 60)
    print("Git Checkpoint Utility - Direct Test")
    print("=" * 60)
    
    # Test 1: Create checkpoint
    print("\n[Test 1] Create checkpoint...")
    result = run_checkpoint_utility(
        action="create",
        session_id="test-001",
        phase="TEST",
        message="Test checkpoint from utility"
    )
    
    print(f"Success: {result.success}")
    print(f"Message: {result.message}")
    if result.checkpoint_id:
        print(f"Checkpoint ID: {result.checkpoint_id[:8]}")
    if result.details:
        print(f"\nDetails:\n{result.details}")
    
    # Test 2: List checkpoints
    print("\n" + "=" * 60)
    print("[Test 2] List checkpoints...")
    list_result = run_checkpoint_utility(action="list")
    
    print(f"Success: {list_result.success}")
    print(f"Message: {list_result.message}")
    print(f"Total: {list_result.checkpoint_count} checkpoint(s)")
    
    if list_result.checkpoints:
        print("\nRecent checkpoints:")
        for i, cp in enumerate(list_result.checkpoints[:5], 1):
            timestamp = datetime.fromisoformat(cp["timestamp"])
            print(f"  {i}. {cp['checkpoint_id'][:8]} - {cp['phase']} - {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n" + "=" * 60)
    print("✅ Utility tests complete")
    print("=" * 60)
