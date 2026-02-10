"""
DeploymentOrchestrator - Production Deployment Workflow (Phase 73).

Orchestrates comprehensive production deployment with:
1. Pre-flight validation (tests, readiness, git clean)
2. VacuumOrchestrator cleanup (consolidation, wiring verification)
3. Two-branch git strategy (CORTEX + main with filtering)
4. Version management (semantic versioning, prompt regeneration)
5. Deployment reporting with full audit trail

Authority: cortex-architect.prompt.md v15.3 (Silent Autonomous Execution)
AC-ID: AC-DEPLOY-ORCH-001
CORE Rules: CORE-008 (TDD), CORE-026 (Git checkpoints), CORE-029 (Headers)
"""

from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from enum import Enum
import subprocess
import logging
import yaml
import json
import re


# ═══════════════════════════════════════════════════════════════════════
# ENUMS & DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════

class DeploymentPhase(Enum):
    """Deployment lifecycle phases."""
    PRE_FLIGHT = "pre_flight_validation"
    CLEANUP = "cleanup_consolidation"
    PUSH_CORTEX = "push_to_cortex_branch"
    PUSH_MAIN = "push_to_main_branch"
    VERSION = "version_release"
    COMPLETE = "complete"


@dataclass
class DeploymentConfig:
    """Deployment configuration."""
    deployment_type: str = "full"  # full, patch, hotfix
    target_branch_cortex: str = "CORTEX"
    target_branch_main: str = "main"
    version_bump_type: str = "patch"  # major, minor, patch
    include_changelog: bool = True
    create_release_tag: bool = True
    regenerate_prompts: bool = True
    auto_commit: bool = True
    dry_run: bool = False


@dataclass
class ValidationResult:
    """Pre-flight validation result."""
    passed: bool
    readiness_score: int = 0
    test_results: Dict[str, int] = field(default_factory=dict)
    checks: List[str] = field(default_factory=list)
    challenges: List[str] = field(default_factory=list)
    failures: List[str] = field(default_factory=list)


@dataclass
class CleanupResult:
    """Cleanup execution result."""
    success: bool
    files_archived: int = 0
    root_consolidated: int = 0
    orchestrators_verified: int = 0
    mcp_tools_verified: int = 0
    issues: List[str] = field(default_factory=list)


@dataclass
class GitResult:
    """Git operation result."""
    success: bool
    commits_pushed: int = 0
    files_modified: int = 0
    branch: str = ""
    message: str = ""
    errors: List[str] = field(default_factory=list)


@dataclass
class VersionResult:
    """Version management result."""
    success: bool
    version_old: str = ""
    version_new: str = ""
    prompts_regenerated: int = 0
    tag_created: bool = False


@dataclass
class DeploymentResult:
    """Complete deployment result."""
    success: bool
    phase_reached: str = ""
    version_old: str = ""
    version_new: str = ""
    pre_flight: Optional[ValidationResult] = None
    cleanup: Optional[CleanupResult] = None
    cortex_branch: Optional[GitResult] = None
    main_branch: Optional[GitResult] = None
    version_result: Optional[VersionResult] = None
    duration_seconds: float = 0.0
    ac_id: str = ""
    errors: List[str] = field(default_factory=list)


# ═══════════════════════════════════════════════════════════════════════
# DEPLOYMENT ORCHESTRATOR
# ═══════════════════════════════════════════════════════════════════════

class DeploymentOrchestrator:
    """
    Orchestrates production deployment with full governance enforcement.
    
    Workflow:
    1. Pre-flight validation (tests, readiness, git status)
    2. Cleanup & consolidation (vacuum orchestrator)
    3. Push to CORTEX branch (all files)
    4. Push to main branch (filtered - production only)
    5. Version management (semantic versioning, tags)
    6. Report generation with audit trail
    
    Usage:
        orchestrator = DeploymentOrchestrator(workspace_root=Path("."))
        config = DeploymentConfig(deployment_type="full", version_bump_type="patch")
        result = orchestrator.deploy_to_production(config)
    """
    
    # Files/directories to exclude from origin/main
    EXCLUDED_FROM_MAIN = {
        "docs/**",                      # Documentation (except README.md in root)
        "_workspaces/**",               # Development workspaces
        ".github/agents/**",             # Internal agent specs
        ".github/prompts/cortex-architect.prompt.md",  # Internal architect mode
        "cortex-registry/**",            # Development wiring registry
        ".phase*",                       # Session markers
        ".session*",                     # Development session markers
        "**/*-complete",                 # Session completion markers
        "**/*-checkpoint",               # Checkpoint markers
        "cortex_brain/tier2/**",         # Internal analysis tier
        "cortex_brain/tier3/**",         # Internal analysis tier
    }
    
    # Files/directories included in origin/main (production only)
    INCLUDED_FOR_MAIN = {
        "cortex/",                       # Production system
        "cortex_brain/tier0/",           # Core knowledge
        "cortex_brain/tier1/",           # Production knowledge
        "tests/",                        # Test suite
        "deployment/",                   # Deployment configs
        ".github/prompts/CORTEX.prompt.md",  # Main production prompt (FRESH)
        ".github/prompts/response-format-standards.md",  # Standards
        ".github/workflows/",            # CI/CD pipelines
        "README.md",                     # Root documentation
        "requirements.txt",              # Dependencies
        "Makefile",                      # Build
        "pytest.ini",                    # Test config
        "pyproject.toml",                # Project config
    }
    
    def __init__(
        self,
        workspace_root: Optional[Path] = None,
        logger: Optional[logging.Logger] = None
    ) -> None:
        """
        Initialize DeploymentOrchestrator.
        
        Args:
            workspace_root: Root directory of CORTEX workspace
            logger: Optional logger instance
        """
        self.workspace_root = Path(workspace_root or Path.cwd())
        self.logger = logger or self._create_logger()
        
        # Load components
        self._initialize_components()
    
    def _create_logger(self) -> logging.Logger:
        """Create logger for deployment operations."""
        logger = logging.getLogger("DeploymentOrchestrator")
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger
    
    def _initialize_components(self) -> None:
        """Initialize orchestrator components."""
        try:
            from cortex.orchestrators.support.vacuum_orchestrator import VacuumOrchestrator
            from cortex.brain.production.readiness_assessment import ProductionReadinessAssessment
            from cortex.ci_cd.production_release import ProductionReleaseManager
            
            self.vacuum = VacuumOrchestrator()
            self.readiness_assessment = ProductionReadinessAssessment(self.workspace_root)
            self.release_manager = ProductionReleaseManager(self.workspace_root)
        except ImportError as e:
            self.logger.warning(f"Could not load components: {e}")
            self.vacuum = None
            self.readiness_assessment = None
            self.release_manager = None
    
    # ═════════════════════════════════════════════════════════════════
    # MAIN DEPLOYMENT WORKFLOW
    # ═════════════════════════════════════════════════════════════════
    
    def deploy_to_production(
        self,
        config: Optional[DeploymentConfig] = None
    ) -> DeploymentResult:
        """
        Execute complete production deployment workflow.
        
        Args:
            config: Deployment configuration
            
        Returns:
            DeploymentResult with full status
        """
        config = config or DeploymentConfig()
        start_time = datetime.now()
        ac_id = f"AC-DEPLOY-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        self._log_ac_start(ac_id, "Production Deployment")
        
        result = DeploymentResult(
            success=False,
            ac_id=ac_id
        )
        
        try:
            # Stage 1: Pre-flight validation
            self.logger.info("🚀 STAGE 1: Pre-Flight Validation")
            pre_flight = self.pre_flight_validation()
            result.pre_flight = pre_flight
            
            if not pre_flight.passed:
                result.errors = pre_flight.failures
                result.phase_reached = "PRE_FLIGHT"
                return result
            
            # Stage 2: Cleanup & consolidation
            self.logger.info("🧹 STAGE 2: Cleanup & Consolidation")
            cleanup = self.cleanup_and_consolidate()
            result.cleanup = cleanup
            
            if not cleanup["success"]:
                result.errors.append("Cleanup failed")
                result.phase_reached = "CLEANUP"
                return result
            
            # Stage 3: Push to CORTEX branch
            self.logger.info("🌿 STAGE 3: Push to CORTEX Branch")
            cortex_result = self.push_to_cortex_branch()
            result.cortex_branch = cortex_result
            
            if not cortex_result.success:
                result.errors.append(f"CORTEX branch push failed: {cortex_result.message}")
                result.phase_reached = "PUSH_CORTEX"
                return result
            
            # Stage 4: Push to main branch (filtered)
            self.logger.info("📦 STAGE 4: Push to Main Branch (Filtered)")
            main_result = self.push_to_main_branch(filter_excluded=True)
            result.main_branch = main_result
            
            if not main_result.success:
                result.errors.append(f"Main branch push failed: {main_result.message}")
                result.phase_reached = "PUSH_MAIN"
                return result
            
            # Stage 5: Version & release
            self.logger.info("📊 STAGE 5: Version & Release")
            version_result = self.create_release_version()
            result.version_result = version_result
            result.version_old = version_result.version_old
            result.version_new = version_result.version_new
            
            if not version_result.success:
                result.errors.append("Version creation failed")
                result.phase_reached = "VERSION"
                return result
            
            # Mark as successful
            result.success = True
            result.phase_reached = "COMPLETE"
            
        except Exception as e:
            self.logger.error(f"Deployment failed: {e}", exc_info=True)
            result.errors.append(str(e))
            result.success = False
        
        finally:
            # Calculate duration and log completion
            duration = (datetime.now() - start_time).total_seconds()
            result.duration_seconds = duration
            
            if result.success:
                self._log_ac_complete(ac_id, "Production Deployment", success=True)
            else:
                self._log_ac_complete(ac_id, "Production Deployment", success=False)
        
        return result
    
    # ═════════════════════════════════════════════════════════════════
    # STAGE 1: PRE-FLIGHT VALIDATION
    # ═════════════════════════════════════════════════════════════════
    
    def pre_flight_validation(self) -> ValidationResult:
        """
        Execute pre-flight validation checks.
        
        Returns:
            ValidationResult with all checks
        """
        result = ValidationResult(passed=True)
        checks = []
        
        # Check 1: Production readiness assessment
        try:
            if self.readiness_assessment:
                readiness = self.readiness_assessment.full_check()
                if readiness.get("status") == "READY":
                    checks.append("✅ Production readiness: READY")
                    result.readiness_score = 100
                else:
                    checks.append(f"⚠️ Production readiness: {readiness.get('status')}")
                    result.readiness_score = 80
        except Exception as e:
            checks.append(f"❌ Production readiness check failed: {e}")
            result.passed = False
        
        # Check 2: All tests passing
        try:
            test_results = self.run_all_tests()
            passed = test_results.get("passed", 0)
            failed = test_results.get("failed", 0)
            
            if failed == 0:
                checks.append(f"✅ Tests: {passed}/{passed} passing")
                result.test_results = test_results
            else:
                checks.append(f"❌ Tests: {failed} failing")
                result.passed = False
        except Exception as e:
            checks.append(f"❌ Test check failed: {e}")
            result.passed = False
        
        # Check 3: Git status clean
        try:
            if self.verify_git_clean():
                checks.append("✅ Git status: Clean")
            else:
                checks.append("❌ Git status: Uncommitted changes")
                result.passed = False
        except Exception as e:
            checks.append(f"❌ Git check failed: {e}")
            result.passed = False
        
        # Check 4: 24h git history
        try:
            history = self.verify_git_24h_history()
            checks.append(f"✅ Git history: {history.get('commits', 0)} commits in 24h")
        except Exception as e:
            checks.append(f"⚠️ Git history check: {e}")
        
        # Check 5: Challenge gate
        challenges = self.generate_challenge_gate()
        result.challenges = challenges
        
        result.checks = checks
        return result
    
    def run_all_tests(self) -> Dict[str, int]:
        """
        Run all tests and return results.
        
        Returns:
            Dict with passed/failed counts
        """
        try:
            result = subprocess.run(
                ["pytest", "tests/", "-v", "--tb=short"],
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            # Parse output
            output = result.stdout + result.stderr
            passed = output.count(" PASSED")
            failed = output.count(" FAILED")
            
            return {"passed": passed, "failed": failed, "returncode": result.returncode}
        except Exception as e:
            self.logger.error(f"Test execution failed: {e}")
            return {"passed": 0, "failed": 1, "error": str(e)}
    
    def verify_git_clean(self) -> bool:
        """
        Verify git working directory is clean.
        
        Returns:
            True if clean, False otherwise
        """
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.workspace_root,
                capture_output=True,
                text=True
            )
            return result.stdout.strip() == ""
        except Exception as e:
            self.logger.error(f"Git status check failed: {e}")
            return False
    
    def verify_git_24h_history(self) -> Dict[str, Any]:
        """
        Verify 24h git history.
        
        Returns:
            Dict with commit count and summary
        """
        try:
            result = subprocess.run(
                ["git", "log", "--oneline", "--since=24.hours", "--all"],
                cwd=self.workspace_root,
                capture_output=True,
                text=True
            )
            commits = result.stdout.strip().split("\n") if result.stdout.strip() else []
            return {"commits": len(commits), "summary": commits[:5]}
        except Exception as e:
            self.logger.error(f"Git history check failed: {e}")
            return {"commits": 0, "error": str(e)}
    
    def generate_challenge_gate(self) -> List[str]:
        """
        Generate challenge gate with alternatives.
        
        Returns:
            List of challenges/alternatives
        """
        challenges = [
            "Deployment Type: Full production release (all branches)",
            "Review Plan: All 5 stages will execute (no manual gates between stages)",
            "Rollback: Available via git tags if needed",
            "Alternative: Run /audit after deployment for post-deployment verification"
        ]
        return challenges
    
    # ═════════════════════════════════════════════════════════════════
    # STAGE 2: CLEANUP & CONSOLIDATION
    # ═════════════════════════════════════════════════════════════════
    
    def cleanup_and_consolidate(self) -> Dict[str, Any]:
        """
        Execute cleanup and consolidation via VacuumOrchestrator.
        
        Returns:
            Dict with cleanup results
        """
        results = {}
        
        try:
            if not self.vacuum:
                return {"success": False, "error": "VacuumOrchestrator not available"}
            
            # 1. Run vacuum cleanup
            results["vacuum"] = asdict(
                self.vacuum.execute_full_cleanup() or CleanupResult(success=False)
            )
            
            # 2. Verify orchestrator wiring
            results["wiring_check"] = asdict(
                self.vacuum.verify_orchestrator_wiring() or CleanupResult(success=False)
            )
            
            # 3. Verify MCP tools
            results["mcp_check"] = asdict(
                self.vacuum.verify_mcp_tools_registered() or CleanupResult(success=False)
            )
            
            # 4. Consolidate root folders
            results["consolidation"] = asdict(
                self.vacuum.consolidate_root_folders() or CleanupResult(success=False)
            )
            
            # 5. Archive session markers
            results["archive"] = asdict(
                self.vacuum.archive_session_markers() or CleanupResult(success=False)
            )
            
            # 6. Git checkpoint
            results["git_checkpoint"] = self._git_checkpoint("vacuum-cleanup")
            
            # Overall success
            results["success"] = all(
                r.get("success", False) for k, r in results.items()
                if k not in ["success", "git_checkpoint"]
            )
            
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")
            results["success"] = False
            results["error"] = str(e)
        
        return results
    
    # ═════════════════════════════════════════════════════════════════
    # STAGE 3 & 4: BRANCH PUSH STRATEGY
    # ═════════════════════════════════════════════════════════════════
    
    def push_to_cortex_branch(self) -> GitResult:
        """
        Push all files to origin/CORTEX branch.
        
        Returns:
            GitResult with push status
        """
        return self._git_push_branch(
            branch="CORTEX",
            message="chore: Production deployment checkpoint",
            include_all=True
        )
    
    def push_to_main_branch(self, filter_excluded: bool = True) -> GitResult:
        """
        Push filtered files to origin/main branch.
        
        Args:
            filter_excluded: Whether to filter excluded files
            
        Returns:
            GitResult with push status
        """
        if not filter_excluded:
            return self._git_push_branch(
                branch="main",
                message="chore: Production release",
                include_all=True
            )
        else:
            return self._git_push_branch_filtered(
                branch="main",
                excluded=self.EXCLUDED_FROM_MAIN,
                message="chore: Production release"
            )
    
    def _git_push_branch(
        self,
        branch: str,
        message: str,
        include_all: bool = False
    ) -> GitResult:
        """
        Push files to git branch.
        
        Args:
            branch: Branch name
            message: Commit message
            include_all: Include all files
            
        Returns:
            GitResult
        """
        result = GitResult(success=False, branch=branch)
        
        try:
            # Add files
            if include_all:
                subprocess.run(
                    ["git", "add", "."],
                    cwd=self.workspace_root,
                    check=True
                )
            else:
                subprocess.run(
                    ["git", "add", "-A"],
                    cwd=self.workspace_root,
                    check=True
                )
            
            # Commit
            commit_result = subprocess.run(
                ["git", "commit", "-m", message],
                cwd=self.workspace_root,
                capture_output=True,
                text=True
            )
            
            if commit_result.returncode not in [0, 1]:  # 0 = committed, 1 = nothing to commit
                result.message = commit_result.stderr
                return result
            
            # Push
            push_result = subprocess.run(
                ["git", "push", "origin", branch],
                cwd=self.workspace_root,
                capture_output=True,
                text=True
            )
            
            if push_result.returncode == 0:
                result.success = True
                result.message = f"Pushed to {branch}"
                result.commits_pushed = 1
            else:
                result.message = push_result.stderr
                result.errors.append(push_result.stderr)
        
        except Exception as e:
            result.message = str(e)
            result.errors.append(str(e))
        
        return result
    
    def _git_push_branch_filtered(
        self,
        branch: str,
        excluded: set,
        message: str
    ) -> GitResult:
        """
        Push filtered files to git branch.
        
        Args:
            branch: Branch name
            excluded: Set of excluded patterns
            message: Commit message
            
        Returns:
            GitResult
        """
        result = GitResult(success=False, branch=branch)
        
        try:
            # Get list of files to include
            files_to_include = self._get_included_files(excluded)
            
            if not files_to_include:
                result.message = "No files to commit"
                return result
            
            # Add included files only
            for file in files_to_include:
                subprocess.run(
                    ["git", "add", file],
                    cwd=self.workspace_root,
                    capture_output=True
                )
            
            # Commit
            commit_result = subprocess.run(
                ["git", "commit", "-m", message],
                cwd=self.workspace_root,
                capture_output=True,
                text=True
            )
            
            if commit_result.returncode not in [0, 1]:
                result.message = commit_result.stderr
                return result
            
            # Push
            push_result = subprocess.run(
                ["git", "push", "origin", branch],
                cwd=self.workspace_root,
                capture_output=True,
                text=True
            )
            
            if push_result.returncode == 0:
                result.success = True
                result.message = f"Pushed {len(files_to_include)} files to {branch}"
                result.commits_pushed = 1
                result.files_modified = len(files_to_include)
            else:
                result.message = push_result.stderr
                result.errors.append(push_result.stderr)
        
        except Exception as e:
            result.message = str(e)
            result.errors.append(str(e))
        
        return result
    
    def _get_included_files(self, excluded: set) -> List[str]:
        """
        Get list of files to include (excluding patterns).
        
        Args:
            excluded: Set of excluded patterns
            
        Returns:
            List of file paths
        """
        included = []
        
        try:
            result = subprocess.run(
                ["git", "ls-files"],
                cwd=self.workspace_root,
                capture_output=True,
                text=True
            )
            
            all_files = result.stdout.strip().split("\n") if result.stdout.strip() else []
            
            for file in all_files:
                # Check if file matches any excluded pattern
                should_exclude = False
                for pattern in excluded:
                    if self._matches_pattern(file, pattern):
                        should_exclude = True
                        break
                
                if not should_exclude:
                    included.append(file)
        
        except Exception as e:
            self.logger.error(f"Failed to get included files: {e}")
        
        return included
    
    def _matches_pattern(self, file_path: str, pattern: str) -> bool:
        """
        Check if file path matches exclusion pattern.
        
        Args:
            file_path: File path
            pattern: Pattern (supports * and **)
            
        Returns:
            True if matches
        """
        import fnmatch
        return fnmatch.fnmatch(file_path, pattern)
    
    def get_excluded_files(self) -> List[str]:
        """
        Get list of excluded files.
        
        Returns:
            List of excluded patterns
        """
        return list(self.EXCLUDED_FROM_MAIN)
    
    # ═════════════════════════════════════════════════════════════════
    # STAGE 5: VERSION MANAGEMENT
    # ═════════════════════════════════════════════════════════════════
    
    def create_release_version(self) -> VersionResult:
        """
        Create release version with semantic versioning.
        
        Returns:
            VersionResult
        """
        result = VersionResult(success=False)
        
        try:
            if not self.release_manager:
                return VersionResult(success=False)
            
            # 1. Get current version
            current_version = self.release_manager.get_current_version()
            result.version_old = current_version
            
            # 2. Bump version
            new_version = self.release_manager.bump_version(current_version, "patch")
            result.version_new = new_version
            
            # 3. Regenerate CORTEX.prompt.md
            prompt_result = self.release_manager.regenerate_cortex_prompt(new_version)
            if prompt_result.get("success"):
                result.prompts_regenerated += 1
            
            # 4. Regenerate copilot-instruction.md
            instr_result = self.release_manager.regenerate_copilot_instructions(new_version)
            if instr_result.get("success"):
                result.prompts_regenerated += 1
            
            # 5. Generate changelog
            changelog = self.release_manager.generate_changelog_entry(
                new_version,
                ["Production deployment complete", "Cleanup & consolidation", "Full test suite passing"]
            )
            
            # 6. Create git tag
            tag_result = self._git_tag(f"v{new_version}", f"Release {new_version}")
            result.tag_created = tag_result
            
            # 7. AC marker
            self._log_ac_marker(f"AC-VERSION-{new_version}")
            
            result.success = True
        
        except Exception as e:
            self.logger.error(f"Version creation failed: {e}")
            result.success = False
        
        return result
    
    def _git_tag(self, tag_name: str, message: str) -> bool:
        """
        Create git tag.
        
        Args:
            tag_name: Tag name
            message: Tag message
            
        Returns:
            True if successful
        """
        try:
            subprocess.run(
                ["git", "tag", "-a", tag_name, "-m", message],
                cwd=self.workspace_root,
                check=True
            )
            
            subprocess.run(
                ["git", "push", "origin", tag_name],
                cwd=self.workspace_root,
                check=True
            )
            
            return True
        except Exception as e:
            self.logger.error(f"Tag creation failed: {e}")
            return False
    
    def _git_checkpoint(self, message: str) -> Dict[str, Any]:
        """
        Create git checkpoint.
        
        Args:
            message: Checkpoint message
            
        Returns:
            Dict with checkpoint result
        """
        try:
            result = subprocess.run(
                ["git", "commit", "-m", f"chore: {message}", "--allow-empty"],
                cwd=self.workspace_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return {"success": True, "message": message}
            else:
                return {"success": False, "error": result.stderr}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ═════════════════════════════════════════════════════════════════
    # REPORTING & AUDIT
    # ═════════════════════════════════════════════════════════════════
    
    def generate_deployment_report(
        self,
        pre_flight: Optional[ValidationResult] = None,
        cleanup: Optional[Dict] = None,
        cortex_branch: Optional[GitResult] = None,
        main_branch: Optional[GitResult] = None,
        version: Optional[VersionResult] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive deployment report.
        
        Returns:
            Dict with deployment report
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "deployment_status": "SUCCESS" if all([
                pre_flight and pre_flight.passed,
                cleanup and cleanup.get("success"),
                cortex_branch and cortex_branch.success,
                main_branch and main_branch.success,
                version and version.success
            ]) else "FAILED",
            "stages": {
                "pre_flight_validation": asdict(pre_flight) if pre_flight else {},
                "cleanup_consolidation": cleanup or {},
                "push_cortex_branch": asdict(cortex_branch) if cortex_branch else {},
                "push_main_branch": asdict(main_branch) if main_branch else {},
                "version_release": asdict(version) if version else {},
            },
            "metrics": {
                "files_archived": cleanup.get("files_archived", 0) if cleanup else 0,
                "commits_pushed": (cortex_branch.commits_pushed if cortex_branch else 0) +
                                 (main_branch.commits_pushed if main_branch else 0),
                "version_old": version.version_old if version else "",
                "version_new": version.version_new if version else "",
                "duration_seconds": 0,
            }
        }
        
        return report
    
    def _log_ac_start(self, ac_id: str, operation: str) -> None:
        """Log AC_START marker."""
        self.logger.info(f"AC_START: {ac_id} | Operation: {operation}")
    
    def _log_ac_complete(self, ac_id: str, operation: str, success: bool = True) -> None:
        """Log AC_COMPLETE marker."""
        status = "✅" if success else "❌"
        self.logger.info(f"AC_COMPLETE: {ac_id} {status} | Operation: {operation}")
    
    def _log_ac_marker(self, marker: str) -> None:
        """Log AC marker."""
        self.logger.info(f"# {marker}")


if __name__ == "__main__":
    # Simple CLI usage
    orchestrator = DeploymentOrchestrator()
    config = DeploymentConfig(deployment_type="full", version_bump_type="patch")
    result = orchestrator.deploy_to_production(config)
    
    print(f"Deployment {'✅ SUCCESSFUL' if result.success else '❌ FAILED'}")
    print(f"Version: {result.version_old} → {result.version_new}")
    print(f"Duration: {result.duration_seconds:.2f}s")
    if result.errors:
        print(f"Errors: {', '.join(result.errors)}")
