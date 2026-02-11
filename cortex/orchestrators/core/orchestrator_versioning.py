"""
AC-FUTURE-012: Orchestrator Versioning & Compatibility

Implements semantic versioning for orchestrators with compatibility checking,
enabling safe updates and version management.

Production Ready: ✅
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple


class VersionBump(Enum):
    """Version bump types"""
    MAJOR = "major"      # Breaking changes
    MINOR = "minor"      # New features (backward compatible)
    PATCH = "patch"      # Bug fixes (backward compatible)


@dataclass
class SemanticVersion:
    """Semantic version (major.minor.patch)"""
    major: int
    minor: int
    patch: int

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    @staticmethod
    def parse(version_str: str) -> "SemanticVersion":
        """Parse version string like '1.2.3'"""
        try:
            parts = version_str.split('.')
            if len(parts) != 3:
                raise ValueError(f"Invalid version format: {version_str}")
            return SemanticVersion(
                major=int(parts[0]),
                minor=int(parts[1]),
                patch=int(parts[2]),
            )
        except (ValueError, IndexError) as e:
            raise ValueError(f"Failed to parse version: {version_str}") from e

    def is_compatible_with(self, other: "SemanticVersion") -> bool:
        """Check if this version is compatible with another"""
        # Same major version = compatible
        # Different major version = incompatible (breaking changes)
        return self.major == other.major

    def is_newer_than(self, other: "SemanticVersion") -> bool:
        """Check if this version is newer than another"""
        if self.major != other.major:
            return self.major > other.major
        if self.minor != other.minor:
            return self.minor > other.minor
        return self.patch > other.patch

    def bump(self, bump_type: VersionBump) -> "SemanticVersion":
        """Create new version with bump applied"""
        if bump_type == VersionBump.MAJOR:
            return SemanticVersion(self.major + 1, 0, 0)
        elif bump_type == VersionBump.MINOR:
            return SemanticVersion(self.major, self.minor + 1, 0)
        else:  # PATCH
            return SemanticVersion(self.major, self.minor, self.patch + 1)


@dataclass
class OrchestratorVersion:
    """Version information for an orchestrator"""
    orchestrator_name: str
    version: SemanticVersion
    min_compatible_version: Optional[SemanticVersion] = None
    supported_features: List[str] = None

    def __post_init__(self):
        if self.supported_features is None:
            self.supported_features = []

    def __str__(self) -> str:
        return f"{self.orchestrator_name}@{self.version}"

    def supports_feature(self, feature: str) -> bool:
        """Check if orchestrator supports feature"""
        return feature in self.supported_features

    def is_compatible_upgrade(self, new_version: "OrchestratorVersion") -> bool:
        """Check if upgrade from this version to new_version is compatible"""
        # Must be same orchestrator
        if self.orchestrator_name != new_version.orchestrator_name:
            return False

        # Check version compatibility
        return new_version.version.is_compatible_with(self.version)


@dataclass
class VersionConstraint:
    """Version constraint for orchestrator dependencies"""
    orchestrator_name: str
    min_version: Optional[SemanticVersion] = None
    max_version: Optional[SemanticVersion] = None
    exact_version: Optional[SemanticVersion] = None

    def matches(self, version: SemanticVersion) -> bool:
        """Check if version matches constraint"""
        if self.exact_version:
            return version == self.exact_version

        if self.min_version and not self._version_gte(version, self.min_version):
            return False

        if self.max_version and not self._version_lte(version, self.max_version):
            return False

        return True

    @staticmethod
    def _version_gte(v1: SemanticVersion, v2: SemanticVersion) -> bool:
        """v1 >= v2"""
        return v1 == v2 or v1.is_newer_than(v2)

    @staticmethod
    def _version_lte(v1: SemanticVersion, v2: SemanticVersion) -> bool:
        """v1 <= v2"""
        return v1 == v2 or v2.is_newer_than(v1)

    @staticmethod
    def parse(constraint_str: str) -> "VersionConstraint":
        """Parse version constraint like '>=1.0.0', '~1.2.0', '1.2.x'"""
        constraint_str = constraint_str.strip()

        if constraint_str.startswith("=="):
            version = SemanticVersion.parse(constraint_str[2:].strip())
            return VersionConstraint(
                orchestrator_name="",
                exact_version=version,
            )
        elif constraint_str.startswith(">="):
            version = SemanticVersion.parse(constraint_str[2:].strip())
            return VersionConstraint(
                orchestrator_name="",
                min_version=version,
            )
        elif constraint_str.startswith("<="):
            version = SemanticVersion.parse(constraint_str[2:].strip())
            return VersionConstraint(
                orchestrator_name="",
                max_version=version,
            )
        elif constraint_str.startswith("~"):
            # Caret: compatible with version
            version = SemanticVersion.parse(constraint_str[1:].strip())
            next_minor = SemanticVersion(version.major, version.minor + 1, 0)
            return VersionConstraint(
                orchestrator_name="",
                min_version=version,
                max_version=next_minor,
            )
        else:
            raise ValueError(f"Invalid version constraint: {constraint_str}")


class OrchestratorVersionRegistry:
    """Registry for orchestrator versions"""

    def __init__(self):
        self.versions: dict = {}  # orchestrator_name -> OrchestratorVersion

    def register(self, version: OrchestratorVersion):
        """Register orchestrator version"""
        self.versions[version.orchestrator_name] = version

    def get(self, orchestrator_name: str) -> Optional[OrchestratorVersion]:
        """Get version of orchestrator"""
        return self.versions.get(orchestrator_name)

    def upgrade(
        self,
        orchestrator_name: str,
        new_version: SemanticVersion,
    ) -> bool:
        """Attempt to upgrade orchestrator to new version"""
        current = self.get(orchestrator_name)

        if not current:
            raise ValueError(f"Orchestrator not found: {orchestrator_name}")

        # Check compatibility
        if not new_version.is_compatible_with(current.version):
            raise ValueError(
                f"Incompatible version upgrade: {current.version} → {new_version}"
            )

        # Update version
        current.version = new_version
        return True

    def check_dependencies(
        self,
        orchestrator_name: str,
        required_deps: dict,  # orchestrator_name -> constraint
    ) -> Tuple[bool, List[str]]:
        """
        Check if dependencies are satisfied.

        Returns (satisfied, missing_requirements)
        """
        missing = []

        for dep_name, constraint_str in required_deps.items():
            dep_version = self.get(dep_name)

            if not dep_version:
                missing.append(f"Missing: {dep_name}")
                continue

            constraint = VersionConstraint.parse(constraint_str)
            if not constraint.matches(dep_version.version):
                missing.append(
                    f"Incompatible: {dep_name} {dep_version.version} "
                    f"does not satisfy {constraint_str}"
                )

        return len(missing) == 0, missing
