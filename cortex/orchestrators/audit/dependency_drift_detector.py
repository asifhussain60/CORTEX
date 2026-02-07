"""
Dependency Drift Detector - P0-027 AUDIT Check.

Detects drift between requirements.txt and installed packages.

AC_START: AC-ENH053-002
Description: Dependency drift detection implementation
Author: Asif Hussain
Date: 2026-02-07
"""

import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Set, Tuple


@dataclass(frozen=True)
class Package:
    """Represents a Python package with name and version."""

    name: str
    version: str

    def __hash__(self):
        """Hash based on package name only (for set operations)."""
        return hash(self.name.lower())

    def __eq__(self, other):
        """Equality based on package name only (for set operations)."""
        if not isinstance(other, Package):
            return False
        return self.name.lower() == other.name.lower()


@dataclass
class DependencyDriftResult:
    """Result of dependency drift analysis."""

    missing: Set[Package] = field(default_factory=set)
    extra: Set[Package] = field(default_factory=set)
    mismatched: Set[Tuple[str, str, str]] = field(default_factory=set)  # (name, required_version, installed_version)
    severity: str = "P2"

    @property
    def has_drift(self) -> bool:
        """Check if any drift detected."""
        return bool(self.missing or self.extra or self.mismatched)

    def to_dict(self) -> dict:
        """Convert result to dictionary for JSON serialization."""
        return {
            "missing": [{"name": p.name, "version": p.version} for p in self.missing],
            "extra": [{"name": p.name, "version": p.version} for p in self.extra],
            "mismatched": [
                {"name": name, "required": req, "installed": inst}
                for name, req, inst in self.mismatched
            ],
            "severity": self.severity,
            "has_drift": self.has_drift,
        }


class DependencyDriftDetector:
    """
    Detects drift between requirements.txt and installed packages.

    P0-027 AUDIT Check:
    - Compares pip freeze output against requirements.txt
    - Detects missing/extra/version-mismatched packages
    - Generates auto-fix commands
    """

    def __init__(self):
        """Initialize dependency drift detector."""
        self.package_pattern = re.compile(r"^([a-zA-Z0-9_-]+)([>=<~!]=?)(.+)$")

    def analyze(self, repo_path: Path) -> DependencyDriftResult:
        """
        Analyze dependency drift for repository.

        Args:
            repo_path: Path to repository root

        Returns:
            DependencyDriftResult with drift analysis
        """
        required = self._parse_requirements_txt(repo_path)
        installed = self._get_installed_packages()

        missing = self._detect_missing(required, installed)
        extra = self._detect_extra(required, installed)
        mismatched = self._detect_mismatches(required, installed)

        # Determine severity
        severity = "P0" if missing else "P1" if mismatched else "P2"

        return DependencyDriftResult(
            missing=missing,
            extra=extra,
            mismatched=mismatched,
            severity=severity,
        )

    def _parse_requirements_txt(self, repo_path: Path) -> Set[Package]:
        """
        Parse requirements.txt file.

        Args:
            repo_path: Path to repository root

        Returns:
            Set of Package objects
        """
        requirements_file = repo_path / "requirements.txt"
        if not requirements_file.exists():
            return set()

        packages = set()
        content = requirements_file.read_text()

        for line in content.splitlines():
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith("#"):
                continue

            # Parse package specification
            match = self.package_pattern.match(line)
            if match:
                name = match.group(1)
                # operator = match.group(2)
                version = match.group(3).strip()
                packages.add(Package(name, version))

        return packages

    def _get_installed_packages(self) -> Set[Package]:
        """
        Get installed packages via pip freeze.

        Returns:
            Set of Package objects
        """
        try:
            result = subprocess.run(
                ["pip", "freeze"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                return set()

            packages = set()
            for line in result.stdout.splitlines():
                line = line.strip()
                if "==" in line:
                    name, version = line.split("==", 1)
                    packages.add(Package(name, version))

            return packages

        except (subprocess.TimeoutExpired, Exception):
            return set()

    def _detect_missing(self, required: Set[Package], installed: Set[Package]) -> Set[Package]:
        """
        Detect packages in requirements.txt but not installed.

        Args:
            required: Packages from requirements.txt
            installed: Packages from pip freeze

        Returns:
            Set of missing packages
        """
        installed_names = {p.name.lower() for p in installed}
        missing = {p for p in required if p.name.lower() not in installed_names}
        return missing

    def _detect_extra(self, required: Set[Package], installed: Set[Package]) -> Set[Package]:
        """
        Detect packages installed but not in requirements.txt.

        Args:
            required: Packages from requirements.txt
            installed: Packages from pip freeze

        Returns:
            Set of extra packages
        """
        required_names = {p.name.lower() for p in required}
        extra = {p for p in installed if p.name.lower() not in required_names}
        return extra

    def _detect_mismatches(
        self, required: Set[Package], installed: Set[Package]
    ) -> Set[Tuple[str, str, str]]:
        """
        Detect version mismatches between required and installed.

        Args:
            required: Packages from requirements.txt
            installed: Packages from pip freeze

        Returns:
            Set of (name, required_version, installed_version) tuples
        """
        mismatched = set()

        # Create lookup dictionaries
        required_dict = {p.name.lower(): p for p in required}
        installed_dict = {p.name.lower(): p for p in installed}

        # Check for version mismatches
        for name_lower, req_pkg in required_dict.items():
            if name_lower in installed_dict:
                inst_pkg = installed_dict[name_lower]
                if req_pkg.version != inst_pkg.version:
                    mismatched.add((req_pkg.name, req_pkg.version, inst_pkg.version))

        return mismatched

    def generate_fix_commands(self, result: DependencyDriftResult) -> list[str]:
        """
        Generate pip commands to fix drift.

        Args:
            result: DependencyDriftResult

        Returns:
            List of shell commands
        """
        commands = []

        # Install missing packages
        if result.missing:
            packages = " ".join([f"{p.name}=={p.version}" for p in result.missing])
            commands.append(f"pip install {packages}")

        # Fix version mismatches
        if result.mismatched:
            packages = " ".join([f"{name}=={req_ver}" for name, req_ver, _ in result.mismatched])
            commands.append(f"pip install {packages}")

        # Uninstall extra packages
        if result.extra:
            packages = " ".join([p.name for p in result.extra])
            commands.append(f"pip uninstall {packages}")

        return commands


# AC_COMPLETE: AC-ENH053-002 ✅ Implementation complete
