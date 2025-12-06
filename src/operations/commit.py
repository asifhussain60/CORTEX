"""
<<<<<<< Updated upstream
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
    run_commit()
logger = logging.getLogger(__name__)


def run_commit(
    project_root: Path = None,
    auto_add_untracked: bool = False,
    rebase: bool = False,
    commit_message: str = None
) -> Dict[str, Any]:
    """
    Execute git commit and sync workflow.
    
    Performs intelligent git synchronization with stash-pull-merge-push pattern:
    1. Pre-flight validation (branch check, untracked files)
    2. Handle untracked files (interactive or auto-add)
    3. Stash local changes (preserves uncommitted work)
    4. Pull from origin (merge or rebase)
    5. Apply stash (intelligent conflict resolution for split-machine work)
    6. Create safety checkpoint (rollback capability)
    7. Push to origin (sync complete)
    
    Args:
        project_root: Project root directory (default: current working directory)
        auto_add_untracked: Automatically add untracked files (default: False)
        rebase: Use rebase instead of merge when pulling (default: False)
        commit_message: Commit message for uncommitted changes (optional)
    
    Returns:
        Dict with:
            - success (bool): True if workflow completed successfully
            - message (str): Summary message
            - checkpoint_created (bool): Whether safety checkpoint was created
            - checkpoint_id (str): Checkpoint ID for rollback
            - steps_completed (List[str]): List of completed workflow steps
            - duration_seconds (float): Total workflow duration
            - stash_applied (bool): Whether stash was applied
            - conflicts_resolved (int): Number of conflicts auto-resolved
    
    Examples:
        # Standard sync (interactive untracked file handling)
        result = run_commit()
        
        # Auto-add untracked files
        result = run_commit(auto_add_untracked=True)
        
        # Use rebase instead of merge
        result = run_commit(rebase=True)
        
        # Custom commit message
        result = run_commit(commit_message="feat: Add commit CLI wrapper")
    """
    from src.orchestrators.commit_orchestrator import CommitOrchestrator
    
    # Use current directory if no project root specified
    if project_root is None:
        project_root = Path.cwd()
    
    try:
        # Initialize orchestrator
        orchestrator = CommitOrchestrator(project_root)
        
        # Execute commit workflow
        result = orchestrator.execute(
            auto_add_untracked=auto_add_untracked,
            rebase=rebase,
            commit_message=commit_message
        )
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Commit workflow failed: {str(e)}")
        return {
            'success': False,
            'message': f"Commit workflow failed: {str(e)}",
            'checkpoint_created': False,
            'checkpoint_id': None,
            'steps_completed': [],
            'duration_seconds': 0.0,
            'stash_applied': False,
            'conflicts_resolved': 0
        }


def main():
    """CLI entry point for direct execution."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='CORTEX Commit and Sync Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Standard commit/sync workflow (interactive)
  python -m src.operations.commit
  
  # Auto-add untracked files
  python -m src.operations.commit --auto-add
  
  # Use rebase instead of merge
  python -m src.operations.commit --rebase
  
  # Custom commit message
  python -m src.operations.commit --message "feat: Add new feature"
  
  # Combined options
  python -m src.operations.commit --auto-add --rebase --message "fix: Bug fix"

Workflow Steps:
  1. Pre-flight check (branch, untracked files, uncommitted changes)
  2. Handle untracked files (interactive or auto-add)
  3. Stash local changes (preserve uncommitted work)
  4. Pull from origin (merge or rebase)
  5. Apply stash (intelligent conflict resolution)
  6. Create safety checkpoint (git tag for rollback)
  7. Push to origin

Safety Features:
  - Automatic stash before pull (preserves local work)
  - Intelligent conflict resolution for split-machine scenarios
  - Safety checkpoint after merge (rollback capability)
  - Untracked file validation (prevents accidental commits)
  - Merge conflict detection
  - Zero data loss guarantee (stash + checkpoints + validation)

Split-Machine Work:
  CORTEX intelligently merges code when work is split across machines:
  - Stashes local changes before pull
  - Pulls remote changes
  - Applies stash on top of pulled code
  - Auto-resolves conflicts (preserves both local and remote)
  - Python files: Keeps both changes (functional merge)
  - Other files: Prefers local version (safer default)

Rollback:
  If sync fails, use: git reset --hard <checkpoint-id>
  Checkpoint IDs displayed in output: commit-YYYYMMDD-HHMMSS
"""
    )
    
    parser.add_argument(
        '--project-root',
        type=Path,
        default=Path.cwd(),
        help='Project root directory (default: current directory)'
    )
    
    parser.add_argument(
        '--auto-add',
        action='store_true',
        help='Automatically add untracked files (default: interactive prompt)'
    )
    
    parser.add_argument(
        '--rebase',
        action='store_true',
        help='Use rebase instead of merge when pulling (default: merge)'
    )
    
    parser.add_argument(
        '--message',
        type=str,
        help='Commit message for uncommitted changes (optional)'
    )
    
    args = parser.parse_args()
    
    # Execute commit workflow
    result = run_commit(
        project_root=args.project_root,
        auto_add_untracked=args.auto_add,
        rebase=args.rebase,
        commit_message=args.message
    )
    
    # Display result summary
    print(f"\n{'='*60}")
    print(f"Result: {'✅ SUCCESS' if result['success'] else '❌ FAILED'}")
    print(f"Message: {result['message']}")
    print(f"Steps completed: {', '.join(result['steps_completed'])}")
    
    if result.get('stash_applied'):
        print(f"Stash: Applied successfully")
    
    if result.get('conflicts_resolved', 0) > 0:
        print(f"Conflicts resolved: {result['conflicts_resolved']} (split-machine work)")
    
    if result['checkpoint_created']:
        print(f"Checkpoint: {result['checkpoint_id'][:8]}... (use for rollback)")
    
    print(f"Duration: {result['duration_seconds']:.1f}s")
    print(f"{'='*60}\n")
    
    # Exit with appropriate code
    sys.exit(0 if result['success'] else 1)


if __name__ == "__main__":
    main()
