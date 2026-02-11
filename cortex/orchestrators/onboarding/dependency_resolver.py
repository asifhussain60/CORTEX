"""Multi-repo dependency resolver.

This module provides the DependencyResolver class that handles
dependency conflict detection and resolution across multiple repos.

PHASE-DEPLOYMENT-002: AC-DEP-002-05
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import yaml


@dataclass
class DependencyConflict:
    """Represents a dependency version conflict.

    Attributes:
        package: Package name.
        versions: Dict of repo name → version spec.
        severity: Conflict severity (minor, major, breaking).
    """
    package: str
    versions: Dict[str, str] = field(default_factory=dict)
    severity: str = "minor"


@dataclass
class ResolutionStrategy:
    """Strategy for resolving a dependency conflict.

    Attributes:
        package: Package name.
        recommendation: Recommended strategy (unified, isolated, upgrade).
        unified_version: Suggested version if using unified strategy.
        notes: Additional notes about the resolution.
    """
    package: str
    recommendation: str  # "unified", "isolated", "upgrade"
    unified_version: str = ""
    notes: str = ""


@dataclass
class ConflictReport:
    """Full conflict resolution report.

    Attributes:
        conflicts: List of detected conflicts.
        recommendations: List of resolution strategies.
        timestamp: When the report was generated.
    """
    conflicts: List[DependencyConflict] = field(default_factory=list)
    recommendations: List[ResolutionStrategy] = field(default_factory=list)
    timestamp: str = ""


class DependencyResolver:
    """Resolves dependency conflicts across multiple repos.

    Scans D:\\PROJECTS\\* for requirements.txt files and detects
    version conflicts between repos.

    Attributes:
        projects_root: Path to the projects root directory.
    """

    # Regex for parsing requirements
    REQUIREMENT_PATTERN = re.compile(
        r'^([a-zA-Z0-9_-]+)\s*((?:[<>=!]+\s*[0-9.]+,?\s*)+)?'
    )

    def __init__(self, projects_root: Path) -> None:
        """Initialize the resolver.

        Args:
            projects_root: Path to the projects root directory.
        """
        self.projects_root = Path(projects_root)

    def _parse_requirements_file(self, file_path: Path) -> Dict[str, str]:
        """Parse a requirements.txt file.

        Args:
            file_path: Path to requirements.txt.

        Returns:
            Dict of package name → version spec.
        """
        requirements: Dict[str, str] = {}

        if not file_path.exists():
            return requirements

        for line in file_path.read_text().strip().split("\n"):
            line = line.strip()

            if not line or line.startswith("#") or line.startswith("-"):
                continue

            match = self.REQUIREMENT_PATTERN.match(line)
            if match:
                name = match.group(1).lower()
                version = (match.group(2) or "").strip()
                requirements[name] = version

        return requirements

    def scan_requirements(self) -> Dict[str, Dict[str, str]]:
        """Scan all repos for requirements.txt files.

        Returns:
            Dict of repo name → package requirements.
        """
        repos: Dict[str, Dict[str, str]] = {}

        if not self.projects_root.exists():
            return repos

        for project_dir in self.projects_root.iterdir():
            if not project_dir.is_dir():
                continue

            requirements_file = project_dir / "requirements.txt"
            if requirements_file.exists():
                repos[project_dir.name] = self._parse_requirements_file(requirements_file)

        return repos

    def build_dependency_graph(self) -> Dict[str, Dict[str, str]]:
        """Build dependency graph showing package → repos and versions.

        Returns:
            Dict of package name → {repo name: version spec}.
        """
        repos = self.scan_requirements()
        graph: Dict[str, Dict[str, str]] = {}

        for repo_name, requirements in repos.items():
            for package, version in requirements.items():
                if package not in graph:
                    graph[package] = {}
                graph[package][repo_name] = version

        return graph

    def _extract_version_tuple(self, spec: str) -> tuple:
        """Extract version tuple from spec.

        Args:
            spec: Version specifier.

        Returns:
            Tuple of (major, minor, patch).
        """
        match = re.search(r'(\d+)\.(\d+)(?:\.(\d+))?', spec)
        if match:
            return (
                int(match.group(1)),
                int(match.group(2)),
                int(match.group(3) or 0),
            )
        return (0, 0, 0)

    def detect_conflicts(self) -> List[DependencyConflict]:
        """Detect version conflicts across repos.

        Returns:
            List of detected conflicts.
        """
        graph = self.build_dependency_graph()
        conflicts: List[DependencyConflict] = []

        for package, versions in graph.items():
            if len(versions) <= 1:
                continue

            # Get unique version specs
            unique_specs = set(v for v in versions.values() if v)

            if len(unique_specs) <= 1:
                continue

            # Determine severity based on major version differences
            major_versions = set()
            for spec in unique_specs:
                major = self._extract_version_tuple(spec)[0]
                major_versions.add(major)

            severity = "major" if len(major_versions) > 1 else "minor"

            conflicts.append(DependencyConflict(
                package=package,
                versions=versions,
                severity=severity,
            ))

        return conflicts

    def suggest_resolutions(self) -> List[ResolutionStrategy]:
        """Suggest resolution strategies for conflicts.

        Returns:
            List of resolution strategies.
        """
        conflicts = self.detect_conflicts()
        strategies: List[ResolutionStrategy] = []

        for conflict in conflicts:
            if conflict.severity == "minor":
                # Minor conflicts: suggest upgrading to highest version
                highest_version = max(
                    (self._extract_version_tuple(v), v)
                    for v in conflict.versions.values() if v
                )[1]

                strategies.append(ResolutionStrategy(
                    package=conflict.package,
                    recommendation="unified",
                    unified_version=highest_version,
                    notes=f"All repos can safely use {highest_version}",
                ))
            else:
                # Major conflicts: may need isolation or upgrade
                strategies.append(ResolutionStrategy(
                    package=conflict.package,
                    recommendation="upgrade",
                    notes="Major version conflict - consider upgrading all repos to latest",
                ))

        return strategies

    def generate_report(self) -> ConflictReport:
        """Generate conflict resolution report.

        Returns:
            ConflictReport with full analysis.
        """
        from datetime import datetime

        report = ConflictReport(
            conflicts=self.detect_conflicts(),
            recommendations=self.suggest_resolutions(),
            timestamp=datetime.now().isoformat(),
        )

        # Write to file
        report_path = self.projects_root / "conflict_resolution_report.yaml"
        report_dict = {
            "timestamp": report.timestamp,
            "conflicts": [
                {
                    "package": c.package,
                    "versions": c.versions,
                    "severity": c.severity,
                }
                for c in report.conflicts
            ],
            "recommendations": [
                {
                    "package": r.package,
                    "recommendation": r.recommendation,
                    "unified_version": r.unified_version or None,
                    "notes": r.notes,
                }
                for r in report.recommendations
            ],
        }
        report_path.write_text(yaml.dump(report_dict, default_flow_style=False))

        return report


def main() -> int:
    """CLI entry point for dependency resolver.

    Returns:
        Exit code.
    """
    import sys

    projects_root = Path.cwd().parent if Path.cwd().name != "PROJECTS" else Path.cwd()

    if "--projects" in sys.argv:
        idx = sys.argv.index("--projects")
        if idx + 1 < len(sys.argv):
            projects_root = Path(sys.argv[idx + 1])

    resolver = DependencyResolver(projects_root)

    if "--scan" in sys.argv:
        repos = resolver.scan_requirements()
        print(f"Found {len(repos)} repos with requirements:")
        for repo_name in repos:
            print(f"  - {repo_name}")
        return 0

    if "--conflicts" in sys.argv:
        conflicts = resolver.detect_conflicts()
        if conflicts:
            print(f"Found {len(conflicts)} conflicts:")
            for conflict in conflicts:
                print(f"  - {conflict.package} ({conflict.severity}): {conflict.versions}")
        else:
            print("No conflicts found")
        return 0

    # Default: generate full report
    report = resolver.generate_report()
    print(f"Generated conflict report at {projects_root / 'conflict_resolution_report.yaml'}")
    print(f"  Conflicts: {len(report.conflicts)}")
    print(f"  Recommendations: {len(report.recommendations)}")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
