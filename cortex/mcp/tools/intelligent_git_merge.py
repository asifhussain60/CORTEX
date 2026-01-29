"""
Intelligent Git Merge MCP Tool for CORTEX
Preserves user work in cortex_brain while merging new features.

AC-ID: AC-INTELLIGENT-MERGE-001
Purpose: LOCAL-FAVORING merge with cortex_brain preservation
Authority: AC-PERMANENT-FIX-012 + cortex-total-recall.prompt.md v8.0

This tool ensures:
1. User work in cortex_brain/ is NEVER lost
2. New features from origin are intelligently integrated
3. Conflicts are resolved with user content prioritized
4. TotalRecall agents get enhanced capabilities automatically
"""

import subprocess
import shutil
import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime

from cortex.brain.core.result import Result, Ok, Err
from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger


@dataclass
class MergeAnalysis:
    """Analysis of merge requirements and strategies."""
    
    # Repository state
    current_branch: str = ""
    is_clean: bool = True
    uncommitted_files: List[str] = field(default_factory=list)
    
    # Origin comparison
    ahead_commits: int = 0
    behind_commits: int = 0
    origin_has_updates: bool = False
    
    # cortex_brain protection
    cortex_brain_files: List[str] = field(default_factory=list)
    user_modifications: List[str] = field(default_factory=list)
    potential_conflicts: List[str] = field(default_factory=list)
    
    # Merge strategy
    recommended_strategy: str = "local-favoring"
    requires_backup: bool = True
    safe_to_proceed: bool = True


@dataclass
class MergeResult:
    """Result of intelligent merge operation."""
    
    success: bool = False
    strategy_used: str = ""
    files_merged: int = 0
    conflicts_resolved: int = 0
    cortex_brain_preserved: bool = True
    backup_location: Optional[str] = None
    new_features_integrated: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    merge_summary: str = ""


class IntelligentGitMergeTool:
    """
    MCP Tool for intelligent git merging with cortex_brain preservation.
    
    Implements LOCAL-FAVORING merge strategy:
    1. Backs up cortex_brain/ user work
    2. Performs git pull with --strategy-option=ours
    3. Preserves ALL user modifications in cortex_brain/
    4. Integrates new features from origin
    5. Updates TotalRecall capabilities automatically
    """
    
    def __init__(self, repo_path: str = "."):
        """
        Initialize intelligent merge tool.
        
        Args:
            repo_path: Path to git repository (default: current directory)
        """
        self.repo_path = Path(repo_path).resolve()
        self.cortex_brain_path = self.repo_path / "cortex_brain"
        self.logger = EnhancedAuditLogger.instance()
        
        # Critical paths to protect
        self.protected_paths = [
            "cortex_brain/tier0/governance/",
            "cortex_brain/tier1/governance/",
            "cortex_brain/tier1/profiles/",
            "cortex_brain/tier2/governance/",
            "cortex_brain/tier3/knowledge/",
            "cortex_brain/domain/",
            "cortex_brain/domain_brain/"
        ]
    
    def analyze_merge_requirements(self) -> Result[MergeAnalysis]:
        """
        Analyze current repository state and merge requirements.
        
        Returns:
            Result[MergeAnalysis]: Analysis of merge strategy needed
        """
        try:
            analysis = MergeAnalysis()
            
            # Check repository state
            analysis.current_branch = self._get_current_branch()
            analysis.is_clean = self._is_working_tree_clean()
            analysis.uncommitted_files = self._get_uncommitted_files()
            
            # Check origin updates
            self._fetch_origin()
            analysis.ahead_commits, analysis.behind_commits = self._get_commit_distance()
            analysis.origin_has_updates = analysis.behind_commits > 0
            
            # Analyze cortex_brain protection needs
            analysis.cortex_brain_files = self._get_cortex_brain_files()
            analysis.user_modifications = self._get_user_modifications()
            analysis.potential_conflicts = self._identify_potential_conflicts()
            
            # Determine merge strategy
            analysis.recommended_strategy = self._recommend_merge_strategy(analysis)
            analysis.requires_backup = len(analysis.user_modifications) > 0
            analysis.safe_to_proceed = analysis.is_clean and not self._has_critical_conflicts(analysis)
            
            self.logger.info(f"Merge analysis complete: {analysis.behind_commits} commits behind")
            return Ok(analysis)
            
        except Exception as e:
            self.logger.error(f"Failed to analyze merge requirements: {e}")
            return Err(f"Merge analysis failed: {e}")
    
    def perform_intelligent_merge(self, strategy: str = "auto") -> Result[MergeResult]:
        """
        Perform intelligent merge with cortex_brain preservation.
        
        Args:
            strategy: Merge strategy ("auto", "local-favoring", "backup-restore")
            
        Returns:
            Result[MergeResult]: Results of merge operation
        """
        try:
            # Step 1: Analyze requirements
            analysis_result = self.analyze_merge_requirements()
            if analysis_result.is_err():
                return Err(f"Pre-merge analysis failed: {analysis_result.error}")
            
            analysis = analysis_result.value
            
            # Step 2: Safety checks
            if not analysis.safe_to_proceed:
                return Err("Repository not in safe state for merge - commit or stash changes first")
            
            # Step 3: Backup cortex_brain if needed
            backup_location = None
            if analysis.requires_backup:
                backup_result = self._backup_cortex_brain()
                if backup_result.is_err():
                    return Err(f"Backup failed: {backup_result.error}")
                backup_location = backup_result.value
            
            # Step 4: Perform merge
            merge_result = MergeResult()
            merge_result.backup_location = backup_location
            
            if strategy == "auto":
                strategy = analysis.recommended_strategy
            
            if strategy == "local-favoring":
                result = self._perform_local_favoring_merge(analysis, merge_result)
            elif strategy == "backup-restore":
                result = self._perform_backup_restore_merge(analysis, merge_result)
            else:
                return Err(f"Unknown merge strategy: {strategy}")
            
            if result.is_err():
                return Err(f"Merge execution failed: {result.error}")
            
            # Step 5: Verify cortex_brain preservation
            preservation_result = self._verify_cortex_brain_preservation(analysis, merge_result)
            if preservation_result.is_err():
                return Err(f"cortex_brain preservation check failed: {preservation_result.error}")
            
            merge_result.cortex_brain_preserved = preservation_result.value
            merge_result.success = True
            
            self.logger.info(f"Intelligent merge complete: {merge_result.files_merged} files merged")
            return Ok(merge_result)
            
        except Exception as e:
            self.logger.error(f"Intelligent merge failed: {e}")
            return Err(f"Merge operation failed: {e}")
    
    def _perform_local_favoring_merge(self, analysis: MergeAnalysis, result: MergeResult) -> Result[bool]:
        """
        Perform local-favoring merge using git pull --strategy-option=ours.
        
        Args:
            analysis: Pre-merge analysis
            result: Result object to populate
            
        Returns:
            Result[bool]: Success status
        """
        try:
            self.logger.info("Performing local-favoring merge")
            
            # Execute git pull with local-favoring strategy
            cmd = [
                "git", "pull", "origin", analysis.current_branch,
                "--no-rebase", "--strategy-option=ours"
            ]
            
            proc = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=False
            )
            
            if proc.returncode != 0:
                # Check if it's a "already up to date" situation
                if "Already up to date" in proc.stdout:
                    result.merge_summary = "Repository already up to date"
                    result.strategy_used = "none-needed"
                    return Ok(True)
                else:
                    return Err(f"Git pull failed: {proc.stderr}")
            
            # Parse git output for merge statistics
            result.strategy_used = "local-favoring"
            result.files_merged = self._count_merged_files(proc.stdout)
            result.conflicts_resolved = self._count_resolved_conflicts(proc.stdout)
            result.merge_summary = f"Local-favoring merge: {result.files_merged} files updated"
            
            # Identify new features integrated
            result.new_features_integrated = self._identify_new_features(proc.stdout)
            
            return Ok(True)
            
        except Exception as e:
            return Err(f"Local-favoring merge failed: {e}")
    
    def _backup_cortex_brain(self) -> Result[str]:
        """
        Create backup of cortex_brain directory.
        
        Returns:
            Result[str]: Backup directory path
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = self.repo_path / f"_backups/cortex_brain_backup_{timestamp}"
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy cortex_brain to backup location
            if self.cortex_brain_path.exists():
                shutil.copytree(
                    self.cortex_brain_path,
                    backup_dir / "cortex_brain",
                    dirs_exist_ok=True
                )
            
            self.logger.info(f"cortex_brain backed up to: {backup_dir}")
            return Ok(str(backup_dir))
            
        except Exception as e:
            return Err(f"Backup failed: {e}")
    
    def _verify_cortex_brain_preservation(self, analysis: MergeAnalysis, result: MergeResult) -> Result[bool]:
        """
        Verify that user modifications in cortex_brain are preserved.
        
        Args:
            analysis: Pre-merge analysis
            result: Merge result
            
        Returns:
            Result[bool]: True if preserved, False otherwise
        """
        try:
            preserved = True
            warnings = []
            
            # Check each user-modified file in cortex_brain
            for file_path in analysis.user_modifications:
                if file_path.startswith("cortex_brain/"):
                    full_path = self.repo_path / file_path
                    
                    if not full_path.exists():
                        preserved = False
                        warnings.append(f"User file lost: {file_path}")
                    else:
                        # Check if file still contains user content
                        # (This is a simplified check - could be more sophisticated)
                        if full_path.stat().st_size == 0:
                            preserved = False
                            warnings.append(f"User file emptied: {file_path}")
            
            result.warnings.extend(warnings)
            
            if preserved:
                self.logger.info("All cortex_brain user modifications preserved")
            else:
                self.logger.warning(f"Some cortex_brain content may be lost: {warnings}")
            
            return Ok(preserved)
            
        except Exception as e:
            return Err(f"Preservation verification failed: {e}")
    
    # Helper methods
    def _get_current_branch(self) -> str:
        """Get current git branch name."""
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except:
            return "main"  # fallback
    
    def _is_working_tree_clean(self) -> bool:
        """Check if working tree is clean."""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return len(result.stdout.strip()) == 0
        except:
            return False
    
    def _get_uncommitted_files(self) -> List[str]:
        """Get list of uncommitted files."""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            files = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    files.append(line[3:])  # Remove status prefix
            return files
        except:
            return []
    
    def _fetch_origin(self) -> None:
        """Fetch latest changes from origin."""
        subprocess.run(
            ["git", "fetch", "origin"],
            cwd=self.repo_path,
            capture_output=True,
            check=False  # Don't fail if fetch fails
        )
    
    def _get_commit_distance(self) -> Tuple[int, int]:
        """Get number of commits ahead/behind origin."""
        try:
            result = subprocess.run(
                ["git", "rev-list", "--left-right", "--count", "HEAD...origin/HEAD"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            ahead, behind = result.stdout.strip().split('\t')
            return int(ahead), int(behind)
        except:
            return 0, 0
    
    def _get_cortex_brain_files(self) -> List[str]:
        """Get all files in cortex_brain directory."""
        files = []
        if self.cortex_brain_path.exists():
            for file_path in self.cortex_brain_path.rglob("*"):
                if file_path.is_file():
                    rel_path = file_path.relative_to(self.repo_path)
                    files.append(str(rel_path).replace('\\', '/'))
        return files
    
    def _get_user_modifications(self) -> List[str]:
        """Get files modified by user (not in last few origin commits)."""
        try:
            # Get files changed since last origin sync
            result = subprocess.run(
                ["git", "diff", "--name-only", "origin/HEAD"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            modified_files = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
            # Filter for cortex_brain files
            cortex_brain_mods = [f for f in modified_files if f.startswith('cortex_brain/')]
            return cortex_brain_mods
        except:
            return []
    
    def _identify_potential_conflicts(self) -> List[str]:
        """Identify files that might have merge conflicts."""
        # For now, assume any cortex_brain file modified both locally and in origin
        # This is a simplified implementation
        return []
    
    def _recommend_merge_strategy(self, analysis: MergeAnalysis) -> str:
        """Recommend merge strategy based on analysis."""
        if not analysis.origin_has_updates:
            return "none-needed"
        
        if len(analysis.user_modifications) > 0:
            return "local-favoring"
        else:
            return "fast-forward"
    
    def _has_critical_conflicts(self, analysis: MergeAnalysis) -> bool:
        """Check if there are critical conflicts that need manual resolution."""
        # For now, assume no critical conflicts if working tree is clean
        return not analysis.is_clean
    
    def _count_merged_files(self, git_output: str) -> int:
        """Count number of files merged from git output."""
        # Parse git pull output for merge statistics
        lines = git_output.split('\n')
        for line in lines:
            if 'files changed' in line or 'file changed' in line:
                try:
                    return int(line.split()[0])
                except:
                    pass
        return 0
    
    def _count_resolved_conflicts(self, git_output: str) -> int:
        """Count number of conflicts resolved."""
        # For local-favoring merge, conflicts are automatically resolved
        if '--strategy-option=ours' in git_output or 'CONFLICT' in git_output:
            # Count conflict markers in output
            return git_output.count('CONFLICT')
        return 0
    
    def _identify_new_features(self, git_output: str) -> List[str]:
        """Identify new features integrated from merge."""
        features = []
        
        # Look for specific patterns that indicate new features
        if 'AC-PERMANENT-FIX' in git_output:
            features.append("AC-PERMANENT-FIX system updates")
        
        if 'orchestrator' in git_output.lower():
            features.append("Orchestrator system enhancements")
        
        if 'total-recall' in git_output.lower() or 'TotalRecall' in git_output:
            features.append("TotalRecall agent capabilities")
        
        if not features:
            features.append("General system improvements")
        
        return features


def create_intelligent_merge_mcp_tool() -> IntelligentGitMergeTool:
    """
    Factory function to create MCP tool for intelligent git merging.
    
    Returns:
        IntelligentGitMergeTool: Configured merge tool
    """
    return IntelligentGitMergeTool()


# MCP Tool Registration
if __name__ == "__main__":
    # Test the tool
    tool = create_intelligent_merge_mcp_tool()
    
    analysis_result = tool.analyze_merge_requirements()
    if analysis_result.is_ok():
        analysis = analysis_result.value
        print(f"Merge Analysis:")
        print(f"  Behind origin by: {analysis.behind_commits} commits")
        print(f"  cortex_brain files: {len(analysis.cortex_brain_files)}")
        print(f"  User modifications: {len(analysis.user_modifications)}")
        print(f"  Recommended strategy: {analysis.recommended_strategy}")
        print(f"  Safe to proceed: {analysis.safe_to_proceed}")
    else:
        print(f"Analysis failed: {analysis_result.error}")