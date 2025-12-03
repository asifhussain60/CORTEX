# Mac Continuation Guide - Orchestrator Migration

**Date:** December 2, 2025  
**Branch:** CORTEX-3.0  
**Status:** Ready to continue Sprint 1

---

## Quick Start (Mac)

```bash
# 1. Navigate to CORTEX
cd ~/PROJECTS/CORTEX

# 2. Pull latest changes
git pull origin CORTEX-3.0

# Expected output:
# remote: Enumerating objects: 13, done.
# remote: Counting objects: 100% (13/13), done.
# Updating dbcabb07..0e237397
# Fast-forward
#  2 files changed, 1900 insertions(+)
#  create mode 100644 cortex-brain/documents/implementation-guides/orchestrator-migration-implementation-plan.md

# 3. Verify implementation plan exists
ls -la cortex-brain/documents/implementation-guides/orchestrator-migration-implementation-plan.md

# 4. Read the plan
cat cortex-brain/documents/implementation-guides/orchestrator-migration-implementation-plan.md | less
# Or open in editor:
code cortex-brain/documents/implementation-guides/orchestrator-migration-implementation-plan.md
```

---

## Environment Verification

```bash
# Check Python version (need 3.8+)
python3 --version

# Check CORTEX config
python3 -c "from src.config import config; print(f'Root: {config.root_path}')"
python3 -c "from src.config import config; print(f'Brain: {config.brain_path}')"

# Run system alignment (should pass)
python3 -m src.operations.align

# Expected output:
# ✅ [OK] Brain tier structure: All 4 tiers present
# ✅ [OK] Protection rules: brain-protection-rules.yaml valid
# ✅ [OK] Response templates: 62 templates loaded
# ...
# ✅ System Alignment: HEALTHY (9/9 checks passed)
```

---

## Sprint 1: Start Here

### Task 1: Migrate commit_orchestrator → commit_utility

**Estimated Time:** 2-3 hours

#### Step 1: Create Utility Module

```bash
# Create git utilities directory if not exists
mkdir -p src/operations/modules/git

# Create commit utility file
touch src/operations/modules/git/commit_utility.py
code src/operations/modules/git/commit_utility.py
```

**Copy this template:**

```python
"""
Commit Utility - Fast & Reliable

Lightweight replacement for CommitOrchestrator focusing on essential git operations.

Design Goals:
    - Execute in <3 seconds
    - Clear pass/fail reporting
    - No complex dependencies
    - Actionable error messages

Features:
    - Pre-flight validation (dirty state, untracked files)
    - Stash management
    - Commit with metadata
    - Safety checkpoint creation
    - Branch preservation

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0
Status: PRODUCTION
"""

import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

from src.config import config

logger = logging.getLogger(__name__)


@dataclass
class CommitResult:
    """Result of commit operation."""
    success: bool
    message: str
    commit_hash: Optional[str] = None
    checkpoint_created: bool = False
    files_committed: int = 0
    details: Dict[str, Any] = None


def run_commit_utility(
    message: Optional[str] = None,
    auto_add: bool = False,
    create_checkpoint: bool = True,
    **kwargs
) -> Dict[str, Any]:
    """
    Execute git commit operation with safety checks.
    
    Args:
        message: Commit message (auto-generated if None)
        auto_add: Automatically stage untracked files
        create_checkpoint: Create safety checkpoint before commit
        **kwargs: Additional parameters
    
    Returns:
        Dict with success, message, and commit details
    """
    try:
        repo_path = Path.cwd()
        
        # Pre-flight validation
        validation = _validate_git_state(repo_path)
        if not validation["success"]:
            return validation
        
        # Handle untracked files
        if not auto_add and validation.get("untracked_files"):
            return {
                "success": False,
                "message": f"Untracked files found: {len(validation['untracked_files'])}. Use --auto-add or stage manually.",
                "data": {"untracked_files": validation["untracked_files"]}
            }
        
        # Stage files if auto-add
        if auto_add:
            stage_result = _stage_files(repo_path)
            if not stage_result["success"]:
                return stage_result
        
        # Create checkpoint if requested
        checkpoint_hash = None
        if create_checkpoint:
            checkpoint_result = _create_checkpoint(repo_path)
            if checkpoint_result["success"]:
                checkpoint_hash = checkpoint_result.get("checkpoint_hash")
        
        # Generate commit message if not provided
        if not message:
            message = _generate_commit_message(repo_path)
        
        # Execute commit
        commit_result = _execute_commit(repo_path, message)
        if not commit_result["success"]:
            return commit_result
        
        # Return success
        result = CommitResult(
            success=True,
            message="Commit completed successfully",
            commit_hash=commit_result["commit_hash"],
            checkpoint_created=checkpoint_hash is not None,
            files_committed=commit_result.get("files_count", 0),
            details={
                "checkpoint": checkpoint_hash,
                "commit_message": message,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        return {
            "success": result.success,
            "message": result.message,
            "data": {
                "commit_hash": result.commit_hash,
                "checkpoint_created": result.checkpoint_created,
                "files_committed": result.files_committed,
                **result.details
            }
        }
    
    except Exception as e:
        logger.error(f"Commit utility failed: {e}")
        return {
            "success": False,
            "message": f"Commit failed: {e}",
            "data": None
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
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        
        if not result.stdout.strip():
            return {
                "success": False,
                "message": "No changes to commit"
            }
        
        # Parse untracked files
        untracked = [
            line[3:] for line in result.stdout.split('\n')
            if line.startswith('??')
        ]
        
        return {
            "success": True,
            "untracked_files": untracked
        }
    
    except Exception as e:
        return {
            "success": False,
            "message": f"Git validation failed: {e}"
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
            "message": f"Stage failed: {e}"
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
```

#### Step 2: Create CLI Wrapper

```bash
# Create CLI wrapper
touch src/operations/commit.py
code src/operations/commit.py
```

**Copy this template:**

```python
"""
Commit Entry Point

Simple CLI wrapper for fast CommitUtility.
Follows standard CORTEX operations pattern.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from operations.modules.git.commit_utility import run_commit_utility


def run_commit(**kwargs):
    """
    Run commit operation using fast utility.
    
    Returns:
        Dict with success, message, and commit results
    """
    result = run_commit_utility(**kwargs)
    
    return {
        "success": result["success"],
        "message": result["message"],
        "data": result.get("data"),
    }


def main():
    """CLI entry point."""
    result = run_commit()
    
    print(f"\n{'='*60}")
    print(f"Commit Operation")
    print(f"{'='*60}\n")
    print(result["message"])
    
    if result.get("data"):
        print(f"\nCommit Details:")
        for key, value in result["data"].items():
            print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
```

#### Step 3: Test the Utility

```bash
# Test utility directly
python3 -m src.operations.modules.git.commit_utility

# Test CLI wrapper
python3 -m src.operations.commit

# Test performance
time python3 -m src.operations.commit
# Should be <3 seconds
```

#### Step 4: Move Old Orchestrator

```bash
# Create backup
mv src/orchestrators/commit_orchestrator.py src/orchestrators/commit_orchestrator.py.bak

# Verify it's gone
ls src/orchestrators/commit_orchestrator.py
# Should show: No such file or directory
```

#### Step 5: Run Validation

```bash
# System alignment check
python3 -m src.operations.align

# Should pass all checks
```

#### Step 6: Commit Changes

```bash
# Stage files
git add src/operations/modules/git/commit_utility.py
git add src/operations/commit.py
git add src/orchestrators/commit_orchestrator.py.bak

# Commit
git commit -m "feat: migrate commit orchestrator to utility

- Create commit_utility.py with <3s execution
- Add CLI wrapper in src/operations/commit.py
- Remove old commit_orchestrator.py (keep .bak)
- Pre-flight validation, stash management, safety checkpoints
- Performance: <3s (tested)

DoD: ✅ Utility functional, ✅ Align verified"

# Push to remote
git push origin CORTEX-3.0
```

---

## Continue with Task 2 & 3

After commit utility is complete, proceed with:

1. **git_checkpoint_utility** (same pattern, 1-2 hours)
2. **rollback_utility** (same pattern, 1-2 hours)

Total Sprint 1: 5-7 hours

---

## Troubleshooting

### Import Errors

```bash
# If you get import errors, add CORTEX to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:${PWD}"

# Or add to ~/.zshrc or ~/.bashrc
echo 'export PYTHONPATH="${PYTHONPATH}:~/PROJECTS/CORTEX"' >> ~/.zshrc
source ~/.zshrc
```

### Config Issues

```bash
# Check config for Mac hostname
hostname

# Update cortex.config.json if needed
code cortex.config.json

# Add Mac section:
{
  "machines": {
    "YOUR-MAC-HOSTNAME": {
      "rootPath": "/Users/yourusername/PROJECTS/CORTEX",
      "brainPath": "/Users/yourusername/PROJECTS/CORTEX/cortex-brain"
    }
  }
}
```

### Git Issues

```bash
# If git commands fail, check repo
git status

# Should show you're on CORTEX-3.0 branch
git branch

# Pull latest if behind
git pull origin CORTEX-3.0
```

---

## Quick Reference

```bash
# Environment check
python3 --version && python3 -m src.operations.align

# Create utility
mkdir -p src/operations/modules/[category] && touch src/operations/modules/[category]/[name]_utility.py

# Create CLI wrapper
touch src/operations/[name].py

# Test
python3 -m src.operations.[name]

# Measure performance
time python3 -m src.operations.[name]

# Move old orchestrator
mv src/orchestrators/[name]_orchestrator.py src/orchestrators/[name]_orchestrator.py.bak

# Commit
git add -A && git commit -m "feat: migrate [name] orchestrator..." && git push origin CORTEX-3.0
```

---

**Ready to Start:** Yes  
**First Task:** migrate commit_orchestrator → commit_utility  
**Estimated Time:** 2-3 hours  
**Full Plan:** See `cortex-brain/documents/implementation-guides/orchestrator-migration-implementation-plan.md`

