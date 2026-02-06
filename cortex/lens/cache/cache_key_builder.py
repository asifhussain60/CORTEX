"""Cache key generation from request context.

Generates deterministic cache keys using:
- User request content hash
- Git HEAD commit SHA
- File modification times
- LENS version for invalidation

Enables cache invalidation on:
- Code changes (git HEAD changes)
- File modifications (new mtime)
- LENS version upgrades (version changes)
"""

import hashlib
import subprocess
from pathlib import Path
from typing import Optional, Tuple
import os


def build_cache_key(
    user_request: str,
    repo_path: str,
    lens_version: str = "2.0"
) -> str:
    """Generate unique cache key from request context.
    
    Key is deterministic: same inputs always produce same key.
    Enables cache hits for repeated requests on unchanged code.
    
    Args:
        user_request: User's request string (analysis target)
        repo_path: Repository root path
        lens_version: LENS version for cache invalidation
        
    Returns:
        SHA256 hash (64 hex characters) as cache key
        
    Example:
        >>> key1 = build_cache_key("analyze file.py", "/repo", "2.0")
        >>> key2 = build_cache_key("analyze file.py", "/repo", "2.0")
        >>> key1 == key2  # Same inputs → same key (deterministic)
        True
    """
    try:
        repo_state_hash = get_repo_state_hash(repo_path)
    except Exception:
        # Fallback: use path hash if git unavailable
        repo_state_hash = hashlib.sha256(repo_path.encode()).hexdigest()[:16]
    
    # Combine: request + state + version for uniqueness
    combined = f"{user_request}:{repo_state_hash}:{lens_version}"
    full_hash = hashlib.sha256(combined.encode()).hexdigest()
    
    return full_hash


def get_repo_state_hash(repo_path: str) -> str:
    """Generate hash of repo state (git HEAD + file mtimes).
    
    Captures current repository state via:
    - Git HEAD commit SHA (detects code changes)
    - Python source file count (detects file additions/deletions)
    - Newest file mtime (detects recent modifications)
    
    Cache invalidates when any of these change.
    
    Args:
        repo_path: Repository root path
        
    Returns:
        SHA256 hash prefix (32 hex characters) representing current repo state
        
    Raises:
        ValueError: If repo_path doesn't exist or is not a git repo
    """
    repo_path_obj = Path(repo_path)
    
    if not repo_path_obj.exists():
        raise ValueError(f"Repository path does not exist: {repo_path}")
    
    # Get git HEAD SHA (detects code changes)
    git_head = _get_git_head(repo_path_obj)
    
    # Get file stats (detects modifications)
    file_mtime = _get_latest_mtime(repo_path_obj)
    file_count = _count_source_files(repo_path_obj)
    
    # Combine all state indicators
    state_string = f"{git_head}:{file_mtime}:{file_count}"
    state_hash = hashlib.sha256(state_string.encode()).hexdigest()
    
    # Return first 32 chars (128-bit hash) for readability
    return state_hash[:32]


def _get_git_head(repo_path: Path) -> str:
    """Get current git HEAD commit SHA.
    
    Args:
        repo_path: Repository root path
        
    Returns:
        Git commit SHA (first 8 chars) or 'unknown' if not a git repo
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(repo_path),
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0:
            return result.stdout.strip()[:8]
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    # Fallback: hash of repo path
    return hashlib.sha256(str(repo_path).encode()).hexdigest()[:8]


def _get_latest_mtime(repo_path: Path) -> str:
    """Get most recent file modification time in repo.
    
    Args:
        repo_path: Repository root path
        
    Returns:
        ISO format timestamp or '0' if no files found
    """
    try:
        latest_mtime = 0.0
        for py_file in repo_path.rglob("*.py"):
            if ".git" not in str(py_file):  # Skip .git directory
                mtime = py_file.stat().st_mtime
                if mtime > latest_mtime:
                    latest_mtime = mtime
        
        return str(int(latest_mtime))
    except Exception:
        return "0"


def _count_source_files(repo_path: Path) -> str:
    """Count Python source files in repository.
    
    Args:
        repo_path: Repository root path
        
    Returns:
        Count as string (for hashing)
    """
    try:
        count = len(list(repo_path.rglob("*.py")))
        return str(count)
    except Exception:
        return "0"


def detect_changes(old_hash: str, new_hash: str) -> bool:
    """Detect if repo state has changed.
    
    Simple comparison: if hashes differ, state changed.
    Used for cache invalidation decisions.
    
    Args:
        old_hash: Previous repo state hash
        new_hash: Current repo state hash
        
    Returns:
        True if changes detected (hash mismatch), False if unchanged
        
    Example:
        >>> changed = detect_changes("abc123", "abc123")
        >>> changed  # Same hash → no changes
        False
        >>> changed = detect_changes("abc123", "def456")
        >>> changed  # Different hash → changes detected
        True
    """
    return old_hash != new_hash


__all__ = ["build_cache_key", "get_repo_state_hash", "detect_changes"]
