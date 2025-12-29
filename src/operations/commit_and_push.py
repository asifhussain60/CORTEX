"""
Commit and Push Orchestrator

Handles the complete workflow of staging, committing, pushing, and syncing with remote repository.

Features:
- Stages all untracked and modified files
- Creates meaningful commit with auto-generated or custom message
- Pushes to remote repository
- Syncs with remote to ensure up-to-date
- Provides detailed status reporting

Version: 3.2.1
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List
import logging

# Add CORTEX root to path for imports
cortex_root = Path(__file__).resolve().parents[2]
if str(cortex_root) not in sys.path:
    sys.path.insert(0, str(cortex_root))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CommitAndPushOrchestrator:
    """
    Orchestrates the complete git commit and push workflow.
    """
    
    def __init__(self, repo_path: Optional[Path] = None):
        """
        Initialize orchestrator.
        
        Args:
            repo_path: Path to git repository (defaults to CORTEX root)
        """
        self.repo_path = repo_path or cortex_root
        self.results = {
            "status_check": None,
            "staging": None,
            "commit": None,
            "push": None,
            "sync": None,
            "final_status": None
        }
    
    def execute(self, commit_message: Optional[str] = None) -> Dict:
        """
        Execute the complete commit and push workflow.
        
        Args:
            commit_message: Custom commit message (auto-generated if not provided)
            
        Returns:
            Dictionary with operation results
        """
        print("=" * 70)
        print("🔄 CORTEX Commit and Push Orchestrator")
        print("=" * 70)
        print(f"Repository: {self.repo_path}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        # Step 1: Check git status
        print("\n📊 Step 1: Checking repository status...")
        status_result = self._check_status()
        self.results["status_check"] = status_result
        
        if not status_result["has_changes"]:
            print("✅ No changes to commit")
            return {"success": True, "message": "No changes to commit", "results": self.results}
        
        print(f"   Found {status_result['files_count']} file(s) to commit")
        
        # Step 2: Stage changes
        print("\n📦 Step 2: Staging changes...")
        staging_result = self._stage_changes(status_result["files"])
        self.results["staging"] = staging_result
        
        if not staging_result["success"]:
            print(f"❌ Staging failed: {staging_result['message']}")
            return {"success": False, "message": "Staging failed", "results": self.results}
        
        print(f"✅ Staged {staging_result['staged_count']} file(s)")
        
        # Step 3: Create commit
        print("\n💾 Step 3: Creating commit...")
        if not commit_message:
            commit_message = self._generate_commit_message(status_result["files"])
        
        commit_result = self._create_commit(commit_message)
        self.results["commit"] = commit_result
        
        if not commit_result["success"]:
            print(f"❌ Commit failed: {commit_result['message']}")
            return {"success": False, "message": "Commit failed", "results": self.results}
        
        print(f"✅ Commit created: {commit_result['commit_sha'][:8]}")
        print(f"   Message: {commit_message}")
        
        # Step 4: Push to remote
        print("\n🚀 Step 4: Pushing to remote...")
        push_result = self._push_to_remote()
        self.results["push"] = push_result
        
        if not push_result["success"]:
            print(f"❌ Push failed: {push_result['message']}")
            return {"success": False, "message": "Push failed", "results": self.results}
        
        print(f"✅ Pushed to {push_result['remote']}/{push_result['branch']}")
        
        # Step 5: Sync with remote
        print("\n🔄 Step 5: Syncing with remote...")
        sync_result = self._sync_with_remote()
        self.results["sync"] = sync_result
        
        if not sync_result["success"]:
            print(f"⚠️  Sync warning: {sync_result['message']}")
        else:
            print(f"✅ Synced with remote")
        
        # Step 6: Final status check
        print("\n✨ Step 6: Final status check...")
        final_status = self._check_status()
        self.results["final_status"] = final_status
        
        print("\n" + "=" * 70)
        print("🎉 COMMIT AND PUSH COMPLETE")
        print("=" * 70)
        print(f"Commit: {commit_result['commit_sha'][:8]}")
        print(f"Branch: {push_result['branch']}")
        print(f"Remote: {push_result['remote']}")
        print(f"Status: {'✅ Clean' if not final_status['has_changes'] else '⚠️ Has uncommitted changes'}")
        print("=" * 70)
        
        return {
            "success": True,
            "message": "Commit and push completed successfully",
            "commit_sha": commit_result["commit_sha"],
            "branch": push_result["branch"],
            "remote": push_result["remote"],
            "results": self.results
        }
    
    def _check_status(self) -> Dict:
        """Check git repository status."""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            lines = [line for line in result.stdout.strip().split("\n") if line]
            files = []
            
            for line in lines:
                if len(line) > 3:
                    status = line[:2].strip()
                    filepath = line[3:].strip()
                    files.append({"status": status, "path": filepath})
            
            return {
                "success": True,
                "has_changes": len(files) > 0,
                "files_count": len(files),
                "files": files
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "has_changes": False,
                "files_count": 0,
                "files": [],
                "error": e.stderr
            }
    
    def _stage_changes(self, files: List[Dict]) -> Dict:
        """Stage all changes."""
        try:
            # Add all files
            result = subprocess.run(
                ["git", "add", "-A"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            return {
                "success": True,
                "staged_count": len(files),
                "message": "All changes staged successfully"
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "staged_count": 0,
                "message": f"Staging failed: {e.stderr}"
            }
    
    def _create_commit(self, message: str) -> Dict:
        """Create commit with message."""
        try:
            result = subprocess.run(
                ["git", "commit", "-m", message],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Get commit SHA
            sha_result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            commit_sha = sha_result.stdout.strip()
            
            return {
                "success": True,
                "commit_sha": commit_sha,
                "message": message
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "commit_sha": None,
                "message": f"Commit failed: {e.stderr}"
            }
    
    def _push_to_remote(self) -> Dict:
        """Push commits to remote repository."""
        try:
            # Get current branch
            branch_result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            current_branch = branch_result.stdout.strip()
            
            # Get remote name
            remote_result = subprocess.run(
                ["git", "remote"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            remote = remote_result.stdout.strip().split("\n")[0] or "origin"
            
            # Push to remote
            push_result = subprocess.run(
                ["git", "push", remote, current_branch],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            return {
                "success": True,
                "remote": remote,
                "branch": current_branch,
                "message": "Pushed successfully"
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "remote": None,
                "branch": None,
                "message": f"Push failed: {e.stderr}"
            }
    
    def _sync_with_remote(self) -> Dict:
        """Sync with remote repository (fetch and status check)."""
        try:
            # Fetch from remote
            fetch_result = subprocess.run(
                ["git", "fetch"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Check if we're up to date
            status_result = subprocess.run(
                ["git", "status", "-sb"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            status_line = status_result.stdout.strip().split("\n")[0]
            
            return {
                "success": True,
                "status": status_line,
                "message": "Synced with remote"
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "status": None,
                "message": f"Sync failed: {e.stderr}"
            }
    
    def _generate_commit_message(self, files: List[Dict]) -> str:
        """Generate automatic commit message based on changed files."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Categorize files
        new_files = [f for f in files if f["status"] == "??"]
        modified_files = [f for f in files if f["status"] in ["M", "MM", "AM"]]
        
        parts = []
        
        if new_files:
            parts.append(f"{len(new_files)} new file(s)")
        if modified_files:
            parts.append(f"{len(modified_files)} modified file(s)")
        
        summary = ", ".join(parts) if parts else "changes"
        
        return f"CORTEX: Auto-commit {summary} [{timestamp}]"


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="CORTEX Commit and Push Orchestrator")
    parser.add_argument("-m", "--message", help="Custom commit message")
    parser.add_argument("--repo", help="Repository path (defaults to CORTEX root)")
    
    args = parser.parse_args()
    
    repo_path = Path(args.repo) if args.repo else None
    orchestrator = CommitAndPushOrchestrator(repo_path)
    
    result = orchestrator.execute(commit_message=args.message)
    
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
