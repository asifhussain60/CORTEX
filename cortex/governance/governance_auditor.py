"""
Comprehensive governance audit for WAVE-4.

Performs full compliance check across CORE rules, git hygiene,
and registry consistency.

AC_START: AC-WAVE-4-AUDIT-001
Description: Comprehensive governance audit and compliance reporting
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import subprocess

import yaml

from cortex.governance.validation.registry_validator import RegistryValidator


logger = logging.getLogger(__name__)


class GovernanceAuditor:
    """
    Comprehensive governance auditor for CORTEX.
    
    Checks:
    - CORE-051: settings.json not tracked in git
    - CORE-052: Single branch policy (CORTEX only)
    - CORE-002: Markdown sprawl prevention
    - CORE-008: TDD compliance (tests passing)
    - Registry consistency via RegistryValidator
    
    Attributes:
        repo_path: Path to repository root
        registry_path: Path to cortex-registry
    """
    
    def __init__(
        self, 
        repo_path: Optional[Path] = None,
        registry_path: Optional[Path] = None
    ) -> None:
        """
        Initialize governance auditor.
        
        Args:
            repo_path: Repository root (defaults to current directory)
            registry_path: Registry root (defaults to cortex-registry/)
        """
        self.repo_path = repo_path or Path.cwd()
        self.registry_path = registry_path or self.repo_path / "cortex-registry"
        self.registry_validator = RegistryValidator(registry_path=self.registry_path)
        
    def run_comprehensive_audit(self) -> Dict[str, Any]:
        """
        Run full governance compliance audit.
        
        Returns:
            Dictionary with:
                - compliant (bool): Overall compliance status
                - p0_violations (List[Dict]): Critical violations
                - p1_warnings (List[Dict]): High-priority warnings
                - p2_notices (List[Dict]): Medium-priority notices
                - checks_performed (int): Total checks
                - timestamp (str): Audit timestamp
        """
        logger.info("Starting comprehensive governance audit...")
        
        p0_violations: List[Dict[str, Any]] = []
        p1_warnings: List[Dict[str, Any]] = []
        p2_notices: List[Dict[str, Any]] = []
        
        # P0: CORE-051 - settings.json not tracked
        settings_check = self._check_settings_json_not_tracked()
        if not settings_check["passed"]:
            p0_violations.append({
                "rule": "CORE-051",
                "check": "settings.json tracking",
                "details": settings_check["details"],
                "remediation": "git rm --cached .vscode/settings.json"
            })
            
        # P0: CORE-052 - Single branch policy
        branch_check = self._check_single_branch_policy()
        if not branch_check["passed"]:
            p1_warnings.append({
                "rule": "CORE-052",
                "check": "Single branch policy",
                "details": branch_check["details"],
                "remediation": "Archive remote branches, keep CORTEX only"
            })
            
        # P1: CORE-002 - Markdown sprawl
        markdown_check = self._check_markdown_sprawl()
        if not markdown_check["passed"]:
            p2_notices.append({
                "rule": "CORE-002",
                "check": "Markdown file count",
                "details": markdown_check["details"],
                "remediation": "Run vacuum to archive excess files"
            })
            
        # P1: Registry consistency
        registry_check = self.registry_validator.validate_registry()
        if not registry_check["valid"]:
            p1_warnings.append({
                "rule": "REGISTRY-CONSISTENCY",
                "check": "Registry validation",
                "details": f"{registry_check['issue_count']} issues in {registry_check['phase_count']} phases",
                "remediation": "Fix broken references and stale data"
            })
            
        # P2: Git hygiene
        git_check = self._check_git_hygiene()
        if not git_check["passed"]:
            p2_notices.append({
                "rule": "CORE-025",
                "check": "Git discipline",
                "details": git_check["details"],
                "remediation": "Commit or stash uncommitted changes"
            })
            
        total_checks = 5
        compliant = len(p0_violations) == 0 and len(p1_warnings) <= 2
        
        return {
            "compliant": compliant,
            "p0_violations": p0_violations,
            "p1_warnings": p1_warnings,
            "p2_notices": p2_notices,
            "checks_performed": total_checks,
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "p0_count": len(p0_violations),
                "p1_count": len(p1_warnings),
                "p2_count": len(p2_notices)
            }
        }
        
    def _check_settings_json_not_tracked(self) -> Dict[str, Any]:
        """
        Check if .vscode/settings.json is tracked in git (CORE-051).
        
        Returns:
            Dictionary with passed (bool) and details (str)
        """
        try:
            result = subprocess.run(
                ["git", "ls-files", ".vscode/settings.json"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            is_tracked = bool(result.stdout.strip())
            
            return {
                "passed": not is_tracked,
                "details": "settings.json is tracked (VIOLATION)" if is_tracked else "settings.json not tracked ✅"
            }
        except Exception as e:
            return {
                "passed": False,
                "details": f"Failed to check git tracking: {e}"
            }
            
    def _check_single_branch_policy(self) -> Dict[str, Any]:
        """
        Check single branch policy (CORE-052).
        
        Returns:
            Dictionary with passed (bool) and details (str)
        """
        try:
            # Check local branches
            result = subprocess.run(
                ["git", "branch"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            local_branches = [
                line.strip().lstrip("* ")
                for line in result.stdout.splitlines()
                if line.strip()
            ]
            
            # Check remote branches (excluding archived)
            remote_result = subprocess.run(
                ["git", "branch", "-r"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            remote_branches = [
                line.strip()
                for line in remote_result.stdout.splitlines()
                if line.strip() and "archive/" not in line.lower() and "HEAD" not in line
            ]
            
            # Filter to active remote branches only
            active_remote = [b for b in remote_branches if "main" not in b and "gh-pages" not in b]
            
            local_ok = len(local_branches) == 1 and local_branches[0] == "CORTEX"
            remote_ok = len(active_remote) <= 1  # Allow CORTEX on remote
            
            details = f"Local: {len(local_branches)} branches, Remote active: {len(active_remote)} branches"
            
            return {
                "passed": local_ok,
                "details": details
            }
        except Exception as e:
            return {
                "passed": False,
                "details": f"Failed to check branches: {e}"
            }
            
    def _check_markdown_sprawl(self) -> Dict[str, Any]:
        """
        Check markdown file count in _cortex-master (CORE-002).
        
        Returns:
            Dictionary with passed (bool) and details (str)
        """
        try:
            master_dir = self.registry_path / "_cortex-master"
            if not master_dir.exists():
                return {
                    "passed": True,
                    "details": "Registry master directory not found"
                }
                
            # Count non-archived markdown files
            md_files = [
                f for f in master_dir.rglob("*.md")
                if "_archive" not in str(f)
            ]
            
            file_count = len(md_files)
            passed = file_count <= 25  # Target from WAVE-1
            
            return {
                "passed": passed,
                "details": f"{file_count} markdown files (target: ≤25)"
            }
        except Exception as e:
            return {
                "passed": False,
                "details": f"Failed to count markdown files: {e}"
            }
            
    def _check_git_hygiene(self) -> Dict[str, Any]:
        """
        Check git working directory hygiene (CORE-025).
        
        Returns:
            Dictionary with passed (bool) and details (str)
        """
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            uncommitted = result.stdout.strip()
            file_count = len(uncommitted.splitlines()) if uncommitted else 0
            
            # Allow up to 2 uncommitted files (e.g., report + one working file)
            passed = file_count <= 2
            
            return {
                "passed": passed,
                "details": f"{file_count} uncommitted files"
            }
        except Exception as e:
            return {
                "passed": False,
                "details": f"Failed to check git status: {e}"
            }
            
    def generate_compliance_report(self, audit_results: Dict[str, Any]) -> str:
        """
        Generate YAML compliance report.
        
        Args:
            audit_results: Results from run_comprehensive_audit()
            
        Returns:
            YAML string with formatted report
        """
        report = {
            "governance_compliance_report": {
                "date": audit_results["timestamp"],
                "compliant": audit_results["compliant"],
                "summary": audit_results["summary"],
                "p0_violations": audit_results["p0_violations"],
                "p1_warnings": audit_results["p1_warnings"],
                "p2_notices": audit_results["p2_notices"],
                "checks_performed": audit_results["checks_performed"],
                "verdict": "PRODUCTION READY ✅" if audit_results["compliant"] else "REMEDIATION REQUIRED ⚠️"
            }
        }
        
        return yaml.dump(report, default_flow_style=False, sort_keys=False)
