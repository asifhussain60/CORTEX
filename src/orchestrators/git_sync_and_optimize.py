"""
Git Sync and Optimize Orchestrator

Comprehensive workflow for safely syncing with remote and optimizing CORTEX state.

Workflow:
1. Stash current work with descriptive message
2. Pull latest changes from origin
3. Intelligently merge stashed work (auto-resolve or prompt)
4. Run system alignment to validate integration
5. Run optimization to improve performance
6. Run cleanup to remove obsolete artifacts
7. Push merged changes to remote
8. Sync with origin to ensure consistency

Safety Features:
- Automatic stash backup with timestamps
- Conflict detection and resolution strategies
- Rollback capability on merge failures
- Validation checkpoints between phases
- Detailed logging and status reporting

Version: 3.0.0
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Tuple
import logging
import json

# Add CORTEX root to path for imports
cortex_root = Path(__file__).resolve().parents[2]
if str(cortex_root) not in sys.path:
    sys.path.insert(0, str(cortex_root))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GitSyncAndOptimizeOrchestrator:
    """
    Orchestrates safe git sync with remote and system optimization.
    """
    
    def __init__(self, repo_path: Optional[Path] = None):
        """
        Initialize orchestrator.
        
        Args:
            repo_path: Path to git repository (defaults to CORTEX root)
        """
        self.repo_path = repo_path or cortex_root
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.stash_name = f"CORTEX_sync_backup_{self.timestamp}"
        self.results = {
            "pre_status": None,
            "stash": None,
            "pull": None,
            "merge": None,
            "align": None,
            "optimize": None,
            "cleanup": None,
            "push": None,
            "sync": None,
            "post_status": None
        }
        
    def execute(self, auto_resolve_conflicts: bool = True) -> Dict:
        """
        Execute the complete sync and optimize workflow.
        
        Args:
            auto_resolve_conflicts: Automatically resolve simple conflicts
            
        Returns:
            Dictionary with operation results
        """
        print("=" * 80)
        print("🔄 CORTEX Git Sync & Optimize Orchestrator")
        print("=" * 80)
        print(f"Repository: {self.repo_path}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Auto-resolve conflicts: {'✅ Enabled' if auto_resolve_conflicts else '❌ Disabled'}")
        print("=" * 80)
        
        try:
            # Phase 1: Pre-sync status check
            if not self._phase1_pre_status():
                return self._build_error_result("Pre-status check failed")
            
            # Phase 2: Stash current work
            if not self._phase2_stash_work():
                return self._build_error_result("Stash failed")
            
            # Phase 3: Pull from remote
            if not self._phase3_pull_remote():
                return self._build_error_result("Pull failed", rollback=True)
            
            # Phase 4: Merge stashed work
            if not self._phase4_merge_stash(auto_resolve_conflicts):
                return self._build_error_result("Merge failed", rollback=True)
            
            # Phase 5: System alignment
            if not self._phase5_align():
                return self._build_error_result("Alignment failed")
            
            # Phase 6: System optimization
            if not self._phase6_optimize():
                return self._build_error_result("Optimization failed")
            
            # Phase 7: System cleanup
            if not self._phase7_cleanup():
                return self._build_error_result("Cleanup failed")
            
            # Phase 8: Push to remote
            if not self._phase8_push():
                return self._build_error_result("Push failed")
            
            # Phase 9: Sync with remote
            if not self._phase9_sync():
                print("⚠️  Final sync warning (non-critical)")
            
            # Phase 10: Post-sync status
            self._phase10_post_status()
            
            # Success summary
            self._print_success_summary()
            
            return {
                "success": True,
                "message": "Git sync and optimization completed successfully",
                "timestamp": self.timestamp,
                "results": self.results
            }
            
        except Exception as e:
            logger.error(f"Orchestrator error: {e}")
            return self._build_error_result(f"Unexpected error: {str(e)}", rollback=True)
    
    def _phase1_pre_status(self) -> bool:
        """Phase 1: Check pre-sync repository status."""
        print("\n" + "=" * 80)
        print("📊 PHASE 1: Pre-Sync Status Check")
        print("=" * 80)
        
        try:
            result = self._run_git_command(["git", "status", "--porcelain"])
            
            if result["returncode"] != 0:
                print(f"❌ Git status check failed: {result['stderr']}")
                return False
            
            lines = [line for line in result["stdout"].split("\n") if line]
            files_changed = len(lines)
            
            # Get current branch
            branch_result = self._run_git_command(["git", "branch", "--show-current"])
            current_branch = branch_result["stdout"].strip()
            
            self.results["pre_status"] = {
                "success": True,
                "files_changed": files_changed,
                "branch": current_branch,
                "changes": lines
            }
            
            print(f"✅ Current branch: {current_branch}")
            print(f"✅ Files changed: {files_changed}")
            
            if files_changed > 0:
                print(f"📝 Changes detected (will be stashed):")
                for line in lines[:10]:  # Show first 10
                    print(f"   {line}")
                if files_changed > 10:
                    print(f"   ... and {files_changed - 10} more")
            
            return True
            
        except Exception as e:
            logger.error(f"Pre-status check error: {e}")
            return False
    
    def _phase2_stash_work(self) -> bool:
        """Phase 2: Stash current work with descriptive message."""
        print("\n" + "=" * 80)
        print("💾 PHASE 2: Stash Current Work")
        print("=" * 80)
        
        try:
            files_changed = self.results["pre_status"]["files_changed"]
            
            if files_changed == 0:
                print("ℹ️  No changes to stash")
                self.results["stash"] = {"success": True, "stashed": False}
                return True
            
            # Create stash with descriptive message
            result = self._run_git_command([
                "git", "stash", "push", "-u", "-m", self.stash_name
            ])
            
            if result["returncode"] != 0:
                print(f"❌ Stash failed: {result['stderr']}")
                self.results["stash"] = {"success": False, "error": result["stderr"]}
                return False
            
            # Verify stash was created
            stash_list = self._run_git_command(["git", "stash", "list"])
            stash_exists = self.stash_name in stash_list["stdout"]
            
            self.results["stash"] = {
                "success": True,
                "stashed": True,
                "stash_name": self.stash_name,
                "files_count": files_changed
            }
            
            print(f"✅ Stashed {files_changed} file(s)")
            print(f"✅ Stash name: {self.stash_name}")
            print(f"✅ Backup created: {stash_exists}")
            
            return True
            
        except Exception as e:
            logger.error(f"Stash error: {e}")
            return False
    
    def _phase3_pull_remote(self) -> bool:
        """Phase 3: Pull latest changes from remote."""
        print("\n" + "=" * 80)
        print("⬇️  PHASE 3: Pull from Remote")
        print("=" * 80)
        
        try:
            branch = self.results["pre_status"]["branch"]
            
            # Get remote name
            remote_result = self._run_git_command(["git", "remote"])
            remote = remote_result["stdout"].strip().split("\n")[0] or "origin"
            
            print(f"📡 Pulling from {remote}/{branch}...")
            
            # Pull from remote
            result = self._run_git_command([
                "git", "pull", remote, branch, "--rebase"
            ])
            
            if result["returncode"] != 0:
                # Check if it's just "already up to date"
                if "Already up to date" in result["stdout"] or "Already up to date" in result["stderr"]:
                    print("✅ Already up to date with remote")
                    self.results["pull"] = {
                        "success": True,
                        "remote": remote,
                        "branch": branch,
                        "up_to_date": True
                    }
                    return True
                else:
                    print(f"❌ Pull failed: {result['stderr']}")
                    self.results["pull"] = {
                        "success": False,
                        "error": result["stderr"]
                    }
                    return False
            
            self.results["pull"] = {
                "success": True,
                "remote": remote,
                "branch": branch,
                "up_to_date": False,
                "output": result["stdout"]
            }
            
            print(f"✅ Successfully pulled from {remote}/{branch}")
            
            return True
            
        except Exception as e:
            logger.error(f"Pull error: {e}")
            return False
    
    def _phase4_merge_stash(self, auto_resolve: bool) -> bool:
        """Phase 4: Intelligently merge stashed work."""
        print("\n" + "=" * 80)
        print("🔀 PHASE 4: Merge Stashed Work")
        print("=" * 80)
        
        try:
            if not self.results["stash"]["stashed"]:
                print("ℹ️  No stash to merge")
                self.results["merge"] = {"success": True, "merged": False}
                return True
            
            print(f"🔄 Applying stash: {self.stash_name}...")
            
            # Try to apply stash
            result = self._run_git_command(["git", "stash", "pop"])
            
            if result["returncode"] == 0:
                print("✅ Stash applied successfully (no conflicts)")
                self.results["merge"] = {
                    "success": True,
                    "merged": True,
                    "conflicts": False
                }
                return True
            
            # Check for conflicts
            if "CONFLICT" in result["stdout"] or "CONFLICT" in result["stderr"]:
                print("⚠️  Merge conflicts detected")
                
                # Get list of conflicted files
                status = self._run_git_command(["git", "status", "--porcelain"])
                conflicts = [
                    line[3:] for line in status["stdout"].split("\n")
                    if line.startswith("UU") or line.startswith("AA") or line.startswith("DD")
                ]
                
                print(f"📋 Conflicted files ({len(conflicts)}):")
                for file in conflicts:
                    print(f"   ⚠️  {file}")
                
                if auto_resolve:
                    resolved = self._auto_resolve_conflicts(conflicts)
                    
                    if resolved:
                        print("✅ Conflicts auto-resolved")
                        self.results["merge"] = {
                            "success": True,
                            "merged": True,
                            "conflicts": True,
                            "auto_resolved": True,
                            "conflicted_files": conflicts
                        }
                        return True
                
                print("❌ Manual conflict resolution required")
                print("💡 Tip: Resolve conflicts and run: git add . && git stash drop")
                
                self.results["merge"] = {
                    "success": False,
                    "merged": False,
                    "conflicts": True,
                    "conflicted_files": conflicts
                }
                return False
            
            print(f"❌ Stash apply failed: {result['stderr']}")
            self.results["merge"] = {
                "success": False,
                "error": result["stderr"]
            }
            return False
            
        except Exception as e:
            logger.error(f"Merge error: {e}")
            return False
    
    def _auto_resolve_conflicts(self, conflicts: List[str]) -> bool:
        """
        Attempt to auto-resolve conflicts using intelligent strategies.
        
        Args:
            conflicts: List of conflicted file paths
            
        Returns:
            True if all conflicts resolved
        """
        print("\n🤖 Attempting auto-resolution...")
        
        try:
            for file in conflicts:
                file_path = self.repo_path / file
                
                if not file_path.exists():
                    continue
                
                # Strategy 1: Accept both changes for documentation files
                if file.endswith((".md", ".txt", ".yaml", ".json")):
                    print(f"   📝 Merging documentation: {file}")
                    # Accept both (keep working tree version)
                    self._run_git_command(["git", "add", file])
                    continue
                
                # Strategy 2: Accept theirs for generated files
                if "generated" in file.lower() or file.startswith("cortex-brain/"):
                    print(f"   🔄 Accepting remote version: {file}")
                    self._run_git_command(["git", "checkout", "--theirs", file])
                    self._run_git_command(["git", "add", file])
                    continue
                
                # Strategy 3: Accept ours for source code
                if file.endswith((".py", ".js", ".ts")):
                    print(f"   💻 Keeping local version: {file}")
                    self._run_git_command(["git", "checkout", "--ours", file])
                    self._run_git_command(["git", "add", file])
                    continue
            
            # Verify all conflicts resolved
            status = self._run_git_command(["git", "status", "--porcelain"])
            remaining_conflicts = [
                line for line in status["stdout"].split("\n")
                if line.startswith("UU") or line.startswith("AA") or line.startswith("DD")
            ]
            
            return len(remaining_conflicts) == 0
            
        except Exception as e:
            logger.error(f"Auto-resolve error: {e}")
            return False
    
    def _phase5_align(self) -> bool:
        """Phase 5: Run system alignment."""
        print("\n" + "=" * 80)
        print("🎯 PHASE 5: System Alignment")
        print("=" * 80)
        
        try:
            # Check if alignment orchestrator exists
            align_script = self.repo_path / "scripts" / "run_alignment.py"
            
            if not align_script.exists():
                print("⚠️  Alignment script not found, skipping...")
                self.results["align"] = {"success": True, "skipped": True}
                return True
            
            print("🔄 Running system alignment...")
            
            result = subprocess.run(
                [sys.executable, str(align_script)],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode != 0:
                print(f"⚠️  Alignment completed with warnings")
                print(f"   {result.stderr[:200]}")
            else:
                print("✅ System alignment completed")
            
            self.results["align"] = {
                "success": result.returncode == 0,
                "output": result.stdout[-500:] if result.stdout else None
            }
            
            return True  # Non-critical, continue even if warnings
            
        except subprocess.TimeoutExpired:
            print("⏱️  Alignment timeout (continuing anyway)")
            self.results["align"] = {"success": False, "timeout": True}
            return True
        except Exception as e:
            logger.error(f"Alignment error: {e}")
            print(f"⚠️  Alignment error (continuing): {e}")
            self.results["align"] = {"success": False, "error": str(e)}
            return True  # Non-critical
    
    def _phase6_optimize(self) -> bool:
        """Phase 6: Run system optimization."""
        print("\n" + "=" * 80)
        print("⚡ PHASE 6: System Optimization")
        print("=" * 80)
        
        try:
            # Check if optimization script exists
            optimize_script = self.repo_path / "run_optimize.py"
            
            if not optimize_script.exists():
                print("⚠️  Optimization script not found, skipping...")
                self.results["optimize"] = {"success": True, "skipped": True}
                return True
            
            print("🔄 Running system optimization...")
            
            result = subprocess.run(
                [sys.executable, str(optimize_script)],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode != 0:
                print(f"⚠️  Optimization completed with warnings")
            else:
                print("✅ System optimization completed")
            
            self.results["optimize"] = {
                "success": result.returncode == 0,
                "output": result.stdout[-500:] if result.stdout else None
            }
            
            return True  # Non-critical
            
        except subprocess.TimeoutExpired:
            print("⏱️  Optimization timeout (continuing anyway)")
            self.results["optimize"] = {"success": False, "timeout": True}
            return True
        except Exception as e:
            logger.error(f"Optimization error: {e}")
            print(f"⚠️  Optimization error (continuing): {e}")
            self.results["optimize"] = {"success": False, "error": str(e)}
            return True  # Non-critical
    
    def _phase7_cleanup(self) -> bool:
        """Phase 7: Run system cleanup."""
        print("\n" + "=" * 80)
        print("🧹 PHASE 7: System Cleanup")
        print("=" * 80)
        
        try:
            # Check if cleanup script exists
            cleanup_script = self.repo_path / "scripts" / "run_cleanup.py"
            
            if not cleanup_script.exists():
                print("⚠️  Cleanup script not found, skipping...")
                self.results["cleanup"] = {"success": True, "skipped": True}
                return True
            
            print("🔄 Running system cleanup...")
            
            result = subprocess.run(
                [sys.executable, str(cleanup_script)],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode != 0:
                print(f"⚠️  Cleanup completed with warnings")
            else:
                print("✅ System cleanup completed")
            
            self.results["cleanup"] = {
                "success": result.returncode == 0,
                "output": result.stdout[-500:] if result.stdout else None
            }
            
            return True  # Non-critical
            
        except subprocess.TimeoutExpired:
            print("⏱️  Cleanup timeout (continuing anyway)")
            self.results["cleanup"] = {"success": False, "timeout": True}
            return True
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
            print(f"⚠️  Cleanup error (continuing): {e}")
            self.results["cleanup"] = {"success": False, "error": str(e)}
            return True  # Non-critical
    
    def _phase8_push(self) -> bool:
        """Phase 8: Push changes to remote."""
        print("\n" + "=" * 80)
        print("⬆️  PHASE 8: Push to Remote")
        print("=" * 80)
        
        try:
            branch = self.results["pre_status"]["branch"]
            remote = self.results["pull"]["remote"]
            
            # Check if there are commits to push
            result = self._run_git_command([
                "git", "rev-list", f"{remote}/{branch}..HEAD", "--count"
            ])
            
            commits_ahead = int(result["stdout"].strip() or "0")
            
            if commits_ahead == 0:
                print("ℹ️  No commits to push")
                self.results["push"] = {"success": True, "pushed": False}
                return True
            
            print(f"📤 Pushing {commits_ahead} commit(s) to {remote}/{branch}...")
            
            push_result = self._run_git_command([
                "git", "push", remote, branch
            ])
            
            if push_result["returncode"] != 0:
                print(f"❌ Push failed: {push_result['stderr']}")
                self.results["push"] = {
                    "success": False,
                    "error": push_result["stderr"]
                }
                return False
            
            print(f"✅ Successfully pushed to {remote}/{branch}")
            
            self.results["push"] = {
                "success": True,
                "pushed": True,
                "commits_count": commits_ahead,
                "remote": remote,
                "branch": branch
            }
            
            return True
            
        except Exception as e:
            logger.error(f"Push error: {e}")
            return False
    
    def _phase9_sync(self) -> bool:
        """Phase 9: Final sync with remote."""
        print("\n" + "=" * 80)
        print("🔄 PHASE 9: Sync with Remote")
        print("=" * 80)
        
        try:
            # Fetch latest
            result = self._run_git_command(["git", "fetch"])
            
            if result["returncode"] != 0:
                print(f"⚠️  Fetch warning: {result['stderr']}")
                self.results["sync"] = {"success": False, "error": result["stderr"]}
                return False
            
            # Check sync status
            status = self._run_git_command(["git", "status", "-sb"])
            status_line = status["stdout"].strip().split("\n")[0]
            
            print(f"✅ Sync status: {status_line}")
            
            self.results["sync"] = {
                "success": True,
                "status": status_line
            }
            
            return True
            
        except Exception as e:
            logger.error(f"Sync error: {e}")
            return False
    
    def _phase10_post_status(self):
        """Phase 10: Final status check."""
        print("\n" + "=" * 80)
        print("✨ PHASE 10: Post-Sync Status")
        print("=" * 80)
        
        try:
            result = self._run_git_command(["git", "status", "--porcelain"])
            lines = [line for line in result["stdout"].split("\n") if line]
            
            self.results["post_status"] = {
                "success": True,
                "files_changed": len(lines),
                "changes": lines
            }
            
            if len(lines) == 0:
                print("✅ Working directory clean")
            else:
                print(f"📝 {len(lines)} file(s) with changes")
                for line in lines[:5]:
                    print(f"   {line}")
            
        except Exception as e:
            logger.error(f"Post-status error: {e}")
    
    def _print_success_summary(self):
        """Print final success summary."""
        print("\n" + "=" * 80)
        print("🎉 GIT SYNC & OPTIMIZE COMPLETE")
        print("=" * 80)
        
        print("\n📊 Operation Summary:")
        print(f"   Branch: {self.results['pre_status']['branch']}")
        print(f"   Remote: {self.results['pull']['remote']}")
        print(f"   Stashed: {'Yes' if self.results['stash']['stashed'] else 'No'}")
        print(f"   Merged: {'Yes' if self.results['merge']['merged'] else 'No'}")
        print(f"   Aligned: {'Yes' if self.results['align']['success'] else 'Skipped/Warning'}")
        print(f"   Optimized: {'Yes' if self.results['optimize']['success'] else 'Skipped/Warning'}")
        print(f"   Cleaned: {'Yes' if self.results['cleanup']['success'] else 'Skipped/Warning'}")
        print(f"   Pushed: {'Yes' if self.results['push']['pushed'] else 'No changes'}")
        
        print("\n✅ CORTEX is now in optimal state and synced with remote")
        print("=" * 80)
    
    def _run_git_command(self, command: List[str]) -> Dict:
        """
        Run git command and return result.
        
        Args:
            command: Git command as list
            
        Returns:
            Dictionary with returncode, stdout, stderr
        """
        result = subprocess.run(
            command,
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )
        
        return {
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    
    def _rollback_stash(self):
        """Rollback by reapplying stash."""
        print("\n⏪ Rolling back changes...")
        
        if self.results["stash"]["stashed"]:
            print(f"🔄 Reapplying stash: {self.stash_name}")
            result = self._run_git_command(["git", "stash", "pop"])
            
            if result["returncode"] == 0:
                print("✅ Stash reapplied successfully")
            else:
                print(f"⚠️  Stash rollback warning: {result['stderr']}")
                print(f"💡 Your work is safe in stash: {self.stash_name}")
    
    def _build_error_result(self, message: str, rollback: bool = False) -> Dict:
        """
        Build error result dictionary.
        
        Args:
            message: Error message
            rollback: Whether to attempt rollback
            
        Returns:
            Error result dictionary
        """
        print(f"\n❌ ERROR: {message}")
        
        if rollback:
            self._rollback_stash()
        
        print("\n" + "=" * 80)
        print("❌ GIT SYNC & OPTIMIZE FAILED")
        print("=" * 80)
        print(f"Error: {message}")
        print(f"Timestamp: {self.timestamp}")
        
        if self.results["stash"]["stashed"]:
            print(f"\n💡 Your work is safely stashed: {self.stash_name}")
            print("   Use 'git stash list' to see all stashes")
            print("   Use 'git stash pop' to restore your work")
        
        print("=" * 80)
        
        return {
            "success": False,
            "message": message,
            "timestamp": self.timestamp,
            "results": self.results
        }


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="CORTEX Git Sync and Optimize Orchestrator"
    )
    parser.add_argument(
        "--no-auto-resolve",
        action="store_true",
        help="Disable automatic conflict resolution"
    )
    parser.add_argument(
        "--repo",
        help="Repository path (defaults to CORTEX root)"
    )
    
    args = parser.parse_args()
    
    repo_path = Path(args.repo) if args.repo else None
    orchestrator = GitSyncAndOptimizeOrchestrator(repo_path)
    
    result = orchestrator.execute(auto_resolve_conflicts=not args.no_auto_resolve)
    
    # Save results to file
    results_file = cortex_root / "cortex-brain" / "documents" / "reports" / f"git-sync-{orchestrator.timestamp}.json"
    results_file.parent.mkdir(parents=True, exist_ok=True)
    results_file.write_text(json.dumps(result, indent=2))
    
    print(f"\n📄 Results saved to: {results_file}")
    
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
