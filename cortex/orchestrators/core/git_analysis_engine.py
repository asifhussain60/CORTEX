"""
Git Analysis Engine - Scope D Implementation

AC-ID: AC-PLANNING-REFINE-QB-001 - Git Analysis (Scope D: All Scopes)
CORE-008: TDD (tests before implementation)

Git analysis integrates four scopes:
1. Current branch/commit state (what state are we in?)
2. Affected files (what will change?)
3. Dependencies (what imports will be affected?)
4. Risk assessment (how risky is this?)

Tests: test_planning_refinement_orchestrator.py
- test_refinement_git_analysis_scope_d_integrated
- test_planning_audit_trail_e2e.py
- test_git_analysis_engine.py (pending)
"""

from __future__ import annotations

import subprocess
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from enum import Enum


class RiskLevel(Enum):
    """Risk levels for changes."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class BranchInfo:
    """Current branch information."""
    branch_name: str
    commit_hash: str
    commit_message: str
    commits_ahead_of_main: int = 0
    uncommitted_changes: bool = False


@dataclass
class FileAnalysis:
    """Analysis of a single file."""
    file_path: str
    change_type: str  # "create", "modify", "delete"
    lines_affected: int
    is_test_file: bool
    is_critical: bool = False


@dataclass
class DependencyAnalysis:
    """Analysis of dependencies/imports."""
    source_file: str
    imports_external: List[str] = field(default_factory=list)
    imports_internal: List[str] = field(default_factory=list)
    imported_by: List[str] = field(default_factory=list)


@dataclass
class RiskAssessment:
    """Complete risk assessment."""
    risk_level: RiskLevel
    risk_score: float  # 0.0 - 1.0
    factors: List[str]
    mitigations: List[str]
    affected_systems: List[str]


@dataclass
class GitAnalysisResult:
    """Complete git analysis result."""
    branch_info: BranchInfo
    affected_files: List[FileAnalysis]
    dependency_analysis: Dict[str, DependencyAnalysis]
    risk_assessment: RiskAssessment
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class GitAnalysisEngine:
    """Analyzes git state and impact of planned changes."""
    
    def __init__(self, repo_path: str = ".") -> None:
        """Initialize git analysis engine.
        
        Args:
            repo_path: Path to git repository (default: current directory)
        
        AC-PLANNING-REFINE-QB-001: Git analysis initialization
        """
        self.repo_path = Path(repo_path)
        if not (self.repo_path / ".git").exists():
            raise ValueError(f"No git repository found at {repo_path}")
    
    def _run_git_command(self, *args: str) -> str:
        """Execute git command safely.
        
        Args:
            *args: Git command arguments
        
        Returns:
            Command output
        """
        try:
            result = subprocess.run(
                ["git", "-C", str(self.repo_path), *args],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                raise RuntimeError(f"Git command failed: {result.stderr}")
            return result.stdout.strip()
        except subprocess.TimeoutExpired:
            raise RuntimeError("Git command timed out")
    
    def get_branch_info(self) -> BranchInfo:
        """
        Scope D Part 1: Current branch/commit state.
        
        Returns:
            Information about current branch
        
        AC-PLANNING-REFINE-QB-001-A: Branch analysis
        """
        try:
            # Get current branch
            branch = self._run_git_command("rev-parse", "--abbrev-ref", "HEAD")
            
            # Get current commit hash
            commit_hash = self._run_git_command("rev-parse", "HEAD")[:8]
            
            # Get current commit message
            commit_message = self._run_git_command("log", "-1", "--pretty=%B")
            
            # Get commits ahead of main (if exists)
            try:
                ahead = self._run_git_command("rev-list", "--count", "main..HEAD")
                commits_ahead = int(ahead) if ahead else 0
            except (ValueError, TypeError, Exception):
                commits_ahead = 0
            
            # Check for uncommitted changes
            status = self._run_git_command("status", "--porcelain")
            uncommitted = bool(status.strip())
            
            return BranchInfo(
                branch_name=branch,
                commit_hash=commit_hash,
                commit_message=commit_message[:80],  # First 80 chars
                commits_ahead_of_main=commits_ahead,
                uncommitted_changes=uncommitted
            )
        except Exception as e:
            # Fallback if git commands fail
            return BranchInfo(
                branch_name="unknown",
                commit_hash="unknown",
                commit_message="(unable to determine)",
                commits_ahead_of_main=0,
                uncommitted_changes=False
            )
    
    def get_affected_files(self, plan_files: Optional[List[str]] = None) -> List[FileAnalysis]:
        """
        Scope D Part 2: Affected files analysis.
        
        Args:
            plan_files: List of files planned to be changed
                       If None, analyzes current uncommitted changes
        
        Returns:
            List of affected files with analysis
        
        AC-PLANNING-REFINE-QB-001-B: Affected files analysis
        """
        if plan_files is None:
            # Analyze current git status
            try:
                status_output = self._run_git_command("status", "--porcelain")
                affected_files = []
                
                for line in status_output.split("\n"):
                    if not line.strip():
                        continue
                    
                    change_type_code = line[:2]
                    file_path = line[3:]
                    
                    # Map git status codes to change types
                    if "A" in change_type_code:
                        change_type = "create"
                    elif "D" in change_type_code:
                        change_type = "delete"
                    else:
                        change_type = "modify"
                    
                    analysis = FileAnalysis(
                        file_path=file_path,
                        change_type=change_type,
                        lines_affected=0,  # Would need diff to calculate
                        is_test_file="test" in file_path.lower()
                    )
                    affected_files.append(analysis)
                
                return affected_files
            except Exception:
                return []
        else:
            # Analyze provided file list
            affected_files = []
            for file_path in plan_files:
                analysis = FileAnalysis(
                    file_path=file_path,
                    change_type="modify",
                    lines_affected=0,
                    is_test_file="test" in file_path.lower(),
                    is_critical="orchestrator" in file_path.lower() or "master" in file_path.lower()
                )
                affected_files.append(analysis)
            
            return affected_files
    
    def get_dependency_analysis(self, affected_files: List[FileAnalysis]) -> Dict[str, DependencyAnalysis]:
        """
        Scope D Part 3: Dependency/import analysis.
        
        Args:
            affected_files: Files to analyze for dependencies
        
        Returns:
            Dependency analysis for each file
        
        AC-PLANNING-REFINE-QB-001-C: Dependency analysis
        """
        analysis_map = {}
        
        for file_obj in affected_files:
            file_path = self.repo_path / file_obj.file_path
            
            if not file_path.exists() or not file_path.suffix == ".py":
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract imports (simple regex-based)
                external_imports = set()
                internal_imports = set()
                
                for line in content.split("\n"):
                    line = line.strip()
                    if line.startswith("from ") or line.startswith("import "):
                        # Extract module name
                        if "from " in line:
                            module = line.split("from ")[1].split(" import ")[0]
                        else:
                            module = line.split("import ")[1].split(" as ")[0]
                        
                        module = module.strip().split(".")[0]
                        
                        # Classify as internal/external
                        if module.startswith("cortex"):
                            internal_imports.add(module)
                        else:
                            external_imports.add(module)
                
                analysis_map[file_obj.file_path] = DependencyAnalysis(
                    source_file=file_obj.file_path,
                    imports_external=sorted(list(external_imports)),
                    imports_internal=sorted(list(internal_imports)),
                    imported_by=[]  # Would need reverse analysis
                )
            except Exception:
                pass
        
        return analysis_map
    
    def assess_risk(
        self,
        branch_info: BranchInfo,
        affected_files: List[FileAnalysis],
        dependencies: Dict[str, DependencyAnalysis]
    ) -> RiskAssessment:
        """
        Scope D Part 4: Risk assessment.
        
        Args:
            branch_info: Current branch state
            affected_files: Files affected by changes
            dependencies: Dependency analysis
        
        Returns:
            Complete risk assessment
        
        AC-PLANNING-REFINE-QB-001-D: Risk assessment
        """
        risk_score = 0.0
        factors = []
        mitigations = []
        affected_systems = set()
        
        # Factor 1: Number of affected files
        file_count = len(affected_files)
        if file_count > 10:
            risk_score += 0.2
            factors.append("Many files affected (>10)")
            mitigations.append("Consider breaking into smaller PRs")
        elif file_count > 5:
            risk_score += 0.1
            factors.append("Multiple files affected")
        
        # Factor 2: Deletion of files
        deletions = [f for f in affected_files if f.change_type == "delete"]
        if deletions:
            risk_score += 0.15
            factors.append("Files will be deleted")
            mitigations.append("Ensure deletion is intentional")
        
        # Factor 3: Critical system changes
        critical_files = [f for f in affected_files if f.is_critical]
        if critical_files:
            risk_score += 0.25
            factors.append("Critical system changes (orchestrators/master)")
            mitigations.append("Require extra review")
            affected_systems.add("ORCHESTRATION_SYSTEM")
        
        # Factor 4: Test coverage
        test_files = [f for f in affected_files if f.is_test_file]
        test_ratio = len(test_files) / max(len(affected_files), 1)
        if test_ratio < 0.25:
            risk_score += 0.1
            factors.append("Low test coverage for changes")
            mitigations.append("Add comprehensive tests")
        
        # Factor 5: External dependencies
        external_dep_count = sum(len(d.imports_external) for d in dependencies.values())
        if external_dep_count > 5:
            risk_score += 0.1
            factors.append("Multiple external dependencies")
            mitigations.append("Verify dependency compatibility")
        
        # Factor 6: Uncommitted changes
        if branch_info.uncommitted_changes:
            risk_score += 0.05
            factors.append("Uncommitted changes exist")
            mitigations.append("Clean up workspace before proceeding")
        
        # Factor 7: Commits ahead of main
        if branch_info.commits_ahead_of_main > 5:
            risk_score += 0.05
            factors.append(f"Branch {branch_info.commits_ahead_of_main} commits ahead of main")
            mitigations.append("Consider rebasing")
        
        # Determine risk level
        risk_score = min(1.0, risk_score)
        if risk_score >= 0.6:
            risk_level = RiskLevel.HIGH
        elif risk_score >= 0.4:
            risk_level = RiskLevel.MEDIUM
        elif risk_score >= 0.2:
            risk_level = RiskLevel.LOW
        else:
            risk_level = RiskLevel.LOW
        
        return RiskAssessment(
            risk_level=risk_level,
            risk_score=risk_score,
            factors=factors,
            mitigations=mitigations,
            affected_systems=sorted(list(affected_systems))
        )
    
    def analyze(self, plan_files: Optional[List[str]] = None) -> GitAnalysisResult:
        """
        Perform complete git analysis (all scopes D).
        
        Combines:
        1. Current branch/commit state
        2. Affected files
        3. Dependencies
        4. Risk assessment
        
        Args:
            plan_files: Optional list of files to analyze
        
        Returns:
            Complete analysis result
        
        AC-PLANNING-REFINE-QB-001: Complete analysis
        """
        # Scope 1: Branch info
        branch_info = self.get_branch_info()
        
        # Scope 2: Affected files
        affected_files = self.get_affected_files(plan_files)
        
        # Scope 3: Dependency analysis
        dependencies = self.get_dependency_analysis(affected_files)
        
        # Scope 4: Risk assessment
        risk = self.assess_risk(branch_info, affected_files, dependencies)
        
        return GitAnalysisResult(
            branch_info=branch_info,
            affected_files=affected_files,
            dependency_analysis=dependencies,
            risk_assessment=risk
        )


# Convenience singleton
_git_analysis_engine_instance: Optional[GitAnalysisEngine] = None


def get_git_analysis_engine(repo_path: str = ".") -> GitAnalysisEngine:
    """Get or create git analysis engine singleton.
    
    Args:
        repo_path: Path to git repository
    
    Returns:
        GitAnalysisEngine instance
    """
    global _git_analysis_engine_instance
    if _git_analysis_engine_instance is None:
        _git_analysis_engine_instance = GitAnalysisEngine(repo_path=repo_path)
    return _git_analysis_engine_instance
