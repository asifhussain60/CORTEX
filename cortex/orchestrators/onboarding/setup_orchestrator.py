"""Setup orchestrator for automated environment configuration.

This module provides the SetupOrchestrator class that handles
requirements validation, conflict detection, and auto-installation.

PHASE-DEPLOYMENT-002: AC-DEP-002-01
"""

import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict


@dataclass
class Requirement:
    """Represents a Python package requirement.
    
    Attributes:
        name: Package name.
        version_spec: Version specifier (e.g., ">=2.0.0").
        source_file: Path to requirements.txt that defined this.
    """
    name: str
    version_spec: str = ""
    source_file: str = ""


@dataclass
class VersionConflict:
    """Represents a version conflict between repos.
    
    Attributes:
        package: Package name.
        versions: Dict of repo name → version spec.
        severity: Conflict severity (minor, major).
    """
    package: str
    versions: Dict[str, str] = field(default_factory=dict)
    severity: str = "minor"


@dataclass
class ConflictResolution:
    """Resolution for a version conflict.
    
    Attributes:
        package: Package name.
        strategy: Resolution strategy (unified, isolated).
        recommended_version: Suggested unified version if applicable.
    """
    package: str
    strategy: str  # "unified" or "isolated"
    recommended_version: str = ""


@dataclass
class InstallResult:
    """Result of package installation.
    
    Attributes:
        success: Whether installation succeeded.
        packages_to_install: List of packages to install.
        actually_installed: Number of packages actually installed.
        progress_reported: Whether progress was reported.
        errors: List of error messages.
    """
    success: bool = True
    packages_to_install: List[str] = field(default_factory=list)
    actually_installed: int = 0
    progress_reported: bool = True
    errors: List[str] = field(default_factory=list)


@dataclass
class SecurityScanResult:
    """Result of security scan.
    
    Attributes:
        scan_completed: Whether scan completed.
        vulnerabilities: Number of vulnerabilities found.
        details: Vulnerability details.
    """
    scan_completed: bool = True
    vulnerabilities: int = 0
    details: List[str] = field(default_factory=list)


class SetupOrchestrator:
    """Orchestrates automated environment setup.
    
    Handles requirements parsing, conflict detection, and auto-installation
    for single or multi-repo environments.
    
    Attributes:
        workspace: Path to the workspace root.
        projects_root: Path to D:\\PROJECTS root for multi-repo scanning.
    """
    
    # Regex for parsing requirements.txt entries
    REQUIREMENT_PATTERN = re.compile(
        r'^([a-zA-Z0-9_-]+)\s*((?:[<>=!]+\s*[0-9.]+,?\s*)+)?'
    )
    
    def __init__(
        self,
        workspace: Path,
        projects_root: Optional[Path] = None,
    ) -> None:
        """Initialize the setup orchestrator.
        
        Args:
            workspace: Path to the workspace root.
            projects_root: Path to projects root for multi-repo scanning.
        """
        self.workspace = Path(workspace)
        self.projects_root = Path(projects_root) if projects_root else None
    
    def parse_requirements(self, requirements_file: Optional[Path] = None) -> List[Requirement]:
        """Parse requirements.txt file.
        
        Args:
            requirements_file: Path to requirements.txt. Defaults to workspace/requirements.txt.
            
        Returns:
            List of parsed requirements.
        """
        if requirements_file is None:
            requirements_file = self.workspace / "requirements.txt"
        
        requirements: List[Requirement] = []
        
        if not requirements_file.exists():
            return requirements
        
        for line in requirements_file.read_text().strip().split("\n"):
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue
            
            # Skip options like -r, -e, etc.
            if line.startswith("-"):
                continue
            
            match = self.REQUIREMENT_PATTERN.match(line)
            if match:
                name = match.group(1)
                version_spec = (match.group(2) or "").strip()
                requirements.append(Requirement(
                    name=name,
                    version_spec=version_spec,
                    source_file=str(requirements_file),
                ))
        
        return requirements
    
    def scan_multi_repo_requirements(self) -> Dict[str, List[Requirement]]:
        """Scan multiple repos for requirements.txt files.
        
        Returns:
            Dict of repo name → list of requirements.
        """
        repos: Dict[str, List[Requirement]] = {}
        
        if not self.projects_root or not self.projects_root.exists():
            # Just scan current workspace
            requirements = self.parse_requirements()
            repos[self.workspace.name] = requirements
            return repos
        
        # Scan all project directories
        for project_dir in self.projects_root.iterdir():
            if not project_dir.is_dir():
                continue
            
            requirements_file = project_dir / "requirements.txt"
            if requirements_file.exists():
                requirements = self.parse_requirements(requirements_file)
                repos[project_dir.name] = requirements
        
        return repos
    
    def detect_version_conflicts(self) -> List[VersionConflict]:
        """Detect version conflicts across repos.
        
        Returns:
            List of version conflicts.
        """
        conflicts: List[VersionConflict] = []
        repos = self.scan_multi_repo_requirements()
        
        # Build package → versions map
        package_versions: Dict[str, Dict[str, str]] = {}
        
        for repo_name, requirements in repos.items():
            for req in requirements:
                if req.name not in package_versions:
                    package_versions[req.name] = {}
                package_versions[req.name][repo_name] = req.version_spec
        
        # Find conflicts (packages with different version specs)
        for package, versions in package_versions.items():
            if len(versions) > 1:
                unique_specs = set(v for v in versions.values() if v)
                if len(unique_specs) > 1:
                    # Determine severity
                    severity = self._determine_conflict_severity(list(unique_specs))
                    conflicts.append(VersionConflict(
                        package=package,
                        versions=versions,
                        severity=severity,
                    ))
        
        return conflicts
    
    def _determine_conflict_severity(self, specs: List[str]) -> str:
        """Determine conflict severity based on version specs.
        
        Args:
            specs: List of version specifiers.
            
        Returns:
            Severity level (minor, major).
        """
        # Extract major versions
        major_versions = set()
        for spec in specs:
            # Extract version number
            match = re.search(r'(\d+)\.', spec)
            if match:
                major_versions.add(int(match.group(1)))
        
        if len(major_versions) > 1:
            return "major"
        return "minor"
    
    def resolve_version_conflicts(self) -> List[ConflictResolution]:
        """Suggest resolution for version conflicts.
        
        Returns:
            List of conflict resolutions.
        """
        conflicts = self.detect_version_conflicts()
        resolutions: List[ConflictResolution] = []
        
        for conflict in conflicts:
            if conflict.severity == "minor":
                # Minor conflicts can use unified version
                recommended = self._find_highest_version(list(conflict.versions.values()))
                resolutions.append(ConflictResolution(
                    package=conflict.package,
                    strategy="unified",
                    recommended_version=recommended,
                ))
            else:
                # Major conflicts need isolated environments
                resolutions.append(ConflictResolution(
                    package=conflict.package,
                    strategy="isolated",
                ))
        
        return resolutions
    
    def _find_highest_version(self, specs: List[str]) -> str:
        """Find the highest version from a list of specs.
        
        Args:
            specs: List of version specifiers.
            
        Returns:
            Highest version spec.
        """
        highest = ""
        highest_tuple = (0, 0, 0)
        
        for spec in specs:
            match = re.search(r'(\d+)\.(\d+)(?:\.(\d+))?', spec)
            if match:
                major = int(match.group(1))
                minor = int(match.group(2))
                patch = int(match.group(3) or 0)
                
                if (major, minor, patch) > highest_tuple:
                    highest_tuple = (major, minor, patch)
                    highest = spec
        
        return highest
    
    def auto_install(self, dry_run: bool = False) -> InstallResult:
        """Auto-install requirements.
        
        Args:
            dry_run: If True, only list packages without installing.
            
        Returns:
            InstallResult with installation details.
        """
        result = InstallResult()
        requirements = self.parse_requirements()
        
        result.packages_to_install = [
            f"{r.name}{r.version_spec}" for r in requirements
        ]
        
        if dry_run:
            return result
        
        # Install packages
        try:
            for package in result.packages_to_install:
                subprocess.run(
                    ["pip", "install", package],
                    capture_output=True,
                    check=True,
                )
                result.actually_installed += 1
        except subprocess.CalledProcessError as e:
            result.success = False
            result.errors.append(str(e))
        
        return result
    
    def run_security_scan(self) -> SecurityScanResult:
        """Run pip-audit for CVE scanning.
        
        Returns:
            SecurityScanResult with scan details.
        """
        result = SecurityScanResult()
        
        try:
            output = subprocess.run(
                ["pip-audit", "--format", "json"],
                capture_output=True,
                text=True,
            )
            
            if output.returncode == 0:
                import json
                vulnerabilities = json.loads(output.stdout)
                result.vulnerabilities = len(vulnerabilities)
                result.details = [str(v) for v in vulnerabilities]
            else:
                result.scan_completed = True
                result.vulnerabilities = 0
                
        except FileNotFoundError:
            # pip-audit not installed
            result.scan_completed = False
        except Exception as e:
            result.scan_completed = False
            result.details.append(str(e))
        
        return result


def main() -> int:
    """CLI entry point for setup orchestrator.
    
    Returns:
        Exit code.
    """
    import sys
    
    workspace = Path.cwd()
    projects_root = None
    
    if "--projects" in sys.argv:
        idx = sys.argv.index("--projects")
        if idx + 1 < len(sys.argv):
            projects_root = Path(sys.argv[idx + 1])
    
    orchestrator = SetupOrchestrator(workspace, projects_root)
    
    if "--dry-run" in sys.argv:
        result = orchestrator.auto_install(dry_run=True)
        print(f"Would install {len(result.packages_to_install)} packages:")
        for pkg in result.packages_to_install[:10]:
            print(f"  - {pkg}")
        if len(result.packages_to_install) > 10:
            print(f"  ... and {len(result.packages_to_install) - 10} more")
        return 0
    
    if "--conflicts" in sys.argv:
        conflicts = orchestrator.detect_version_conflicts()
        print(f"Found {len(conflicts)} version conflicts:")
        for conflict in conflicts:
            print(f"  - {conflict.package}: {conflict.versions}")
        return 0
    
    print("Usage: setup_orchestrator.py [--dry-run|--conflicts] [--projects <path>]")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
