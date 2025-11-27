"""
CORTEX 2.0 - Git Event Capture Helper

Purpose: Called by git hooks to capture git operations.
Usage: python capture_git_event.py <hook_type>

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

SECURITY: This script is called by git hooks. All inputs must be validated.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Set

# Add src to path
CORTEX_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(CORTEX_ROOT))

# SECURITY: Whitelist of allowed hook types
ALLOWED_HOOKS: Set[str] = {"post-commit", "post-merge", "post-checkout"}


def capture_git_event(hook_type: str):
    """Capture git event to Tier 1 with security validation."""
    
    # SECURITY: Validate hook type against whitelist
    if hook_type not in ALLOWED_HOOKS:
        # Silently fail - don't break git operations or expose errors
        return
    
    try:
        from src.tier1.working_memory import WorkingMemory
        
        # Get brain path
        brain_path = os.environ.get("CORTEX_BRAIN_PATH", str(CORTEX_ROOT / "cortex-brain"))
        db_path = Path(brain_path) / "tier1" / "conversations.db"
        
        # SECURITY: Validate database path
        db_path = db_path.resolve(strict=True)
        
        if not db_path.exists():
            return
        
        # Get git details based on hook type (with validation)
        if hook_type == "post-commit":
            context = _get_commit_context()
        elif hook_type == "post-merge":
            context = _get_merge_context()
        else:
            context = {"type": f"git_{hook_type}"}
            
        context["timestamp"] = datetime.now().isoformat()
        
        # Store to Tier 1
        wm = WorkingMemory(str(db_path))
        
        # Get today's ambient session
        session_id = _get_ambient_session(wm)
        
        # Store event
        wm.store_message(
            conversation_id=session_id,
            message={
                "role": "system",
                "content": f"[Git Event] {json.dumps(context)}",
                "timestamp": context["timestamp"]
            }
        )
        
    except Exception as e:
        # SECURITY: Silently fail - don't break git operations
        pass


def _get_commit_context() -> dict:
    """Get commit context with security validation."""
    try:
        # SECURITY: Use list args to prevent command injection
        result = subprocess.run(
            ["git", "log", "-1", "--pretty=format:%H%n%s%n%b"],
            capture_output=True,
            text=True,
            timeout=5  # SECURITY: Prevent hanging
        )
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n', 2)
            return {
                "type": "git_commit",
                "commit_hash": lines[0][:40] if len(lines) > 0 else "",  # Limit hash length
                "commit_message": lines[1][:200] if len(lines) > 1 else "",  # Limit message length
                "commit_body": lines[2][:500] if len(lines) > 2 else ""  # Limit body length
            }
    except (subprocess.TimeoutExpired, Exception):
        pass
        
    return {"type": "git_commit"}


def _get_merge_context() -> dict:
    """Get merge context with security validation."""
    try:
        # SECURITY: Use list args to prevent command injection
        result = subprocess.run(
            ["git", "log", "-1", "--pretty=format:%H%n%s"],
            capture_output=True,
            text=True,
            timeout=5  # SECURITY: Prevent hanging
        )
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n', 1)
            return {
                "type": "git_merge",
                "commit_hash": lines[0][:40] if len(lines) > 0 else "",  # Limit hash length
                "merge_message": lines[1][:200] if len(lines) > 1 else ""  # Limit message length
            }
    except (subprocess.TimeoutExpired, Exception):
        pass
        
    return {"type": "git_merge"}


def _get_ambient_session(wm) -> str:
    """Get or create ambient capture session."""
    from datetime import date
    today = date.today().isoformat()
    
    # Create new ambient session for today
    session_id = wm.start_conversation(
        user_id="ambient_daemon",
        metadata={
            "type": "ambient",
            "date": today,
            "description": "Automatic background context capture"
        }
    )
    
    return session_id


if __name__ == "__main__":
    if len(sys.argv) < 2:
        # Silently exit - called incorrectly
        sys.exit(1)
        
    hook_type = sys.argv[1]
    
    # SECURITY: Additional validation of hook type argument
    if not isinstance(hook_type, str) or len(hook_type) > 50:
        sys.exit(1)
    
    capture_git_event(hook_type)
