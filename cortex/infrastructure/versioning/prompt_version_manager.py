"""
Prompt Version Management System.

Provides version negotiation, compatibility checking, and backward
compatibility verification across prompt releases.

Features:
- Version creation and versioned release directories
- Version negotiation (repo requests version X, hub has version X)
- Incompatible version detection and rejection
- Version history tracking in prompt-versions.yaml
- Backward compatibility matrix
- Deprecated version detection
- Future version rejection
- Major version incompatibility detection

Governance:
- CORE-008: Tests BEFORE code (test-driven development)
- CORE-011: 100% type hints on all parameters and return values
- CORE-012: Google-style docstrings on all public functions and classes
- CORE-013: Specific exception handling (no bare except clauses)

Author: CORTEX Framework
"""

import hashlib
import logging
import re
import threading
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

logger = logging.getLogger(__name__)


@dataclass
class VersionEntry:
    """Version entry for tracking prompt versions.

    Attributes:
        version: Semantic version string (e.g., "1.0.0").
        release_date: Release date of this version.
        sha_hash: SHA hash of the prompt content.
        is_deprecated: Whether this version is deprecated.
        compatible_with: List of compatible versions.
        changelog: Optional changelog notes.
    """

    version: str
    release_date: datetime
    sha_hash: str
    is_deprecated: bool = False
    compatible_with: List[str] = field(default_factory=list)
    changelog: Optional[str] = None

    def parse_version(self) -> Tuple[int, int, int]:
        """Parse version string into major, minor, patch components.

        Returns:
            Tuple of (major, minor, patch) integers.

        Raises:
            ValueError: If version string is invalid.
        """
        match = re.match(r'^(\d+)\.(\d+)\.(\d+)$', self.version)
        if not match:
            raise ValueError(f"Invalid semantic version: {self.version}")
        return int(match.group(1)), int(match.group(2)), int(match.group(3))

    def is_major_compatible(self, other_version: str) -> bool:
        """Check if this version is major-version compatible with another.

        Args:
            other_version: Version string to compare against.

        Returns:
            True if major versions match, False otherwise.
        """
        try:
            self_major, _, _ = self.parse_version()
            match = re.match(r'^(\d+)\.', other_version)
            if match:
                other_major = int(match.group(1))
                return self_major == other_major
        except ValueError:
            pass
        return False


@dataclass
class NegotiationResult:
    """Result of version negotiation.

    Attributes:
        version: Resolved version string (or None if not found).
        compatible: Whether the requested version is compatible.
        error_message: Error message if not compatible.
        entry: The VersionEntry if found.
    """

    version: Optional[str] = None
    compatible: bool = False
    error_message: str = ""
    entry: Optional[VersionEntry] = None


class VersionNegotiationError(Exception):
    """Error during version negotiation."""
    pass


class VersionCompatibilityError(Exception):
    """Error when versions are incompatible."""
    pass


class PromptVersionManager:
    """Singleton manager for prompt version control.

    Manages version registration, negotiation, and compatibility checking
    for prompt releases.

    Attributes:
        versions_file: Path to the prompt-versions.yaml file.
    """

    _instance: Optional["PromptVersionManager"] = None
    _lock: threading.Lock = threading.Lock()

    def __init__(
        self,
        versions_file: Optional[Path] = None,
        manifest_path: Optional[Path] = None,
        releases_path: Optional[Path] = None,
    ) -> None:
        """Initialize version manager.

        Args:
            versions_file: Path to versions YAML file. If None, uses default.
            manifest_path: Alternative path for manifest (alias for versions_file).
            releases_path: Path to releases directory.
        """
        self._versions: Dict[str, VersionEntry] = {}
        self._versions_file = manifest_path or versions_file or Path("prompt-versions.yaml")
        self._releases_path = releases_path
        self._initialized = False
        self._local_lock = threading.Lock()
        self._version_history: List[VersionEntry] = []

    @classmethod
    def get_instance(cls) -> "PromptVersionManager":
        """Get singleton instance.

        Returns:
            The singleton PromptVersionManager instance.
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_singleton(cls) -> None:
        """Reset singleton instance for testing."""
        with cls._lock:
            cls._instance = None

    @property
    def version_count(self) -> int:
        """Get the count of registered versions.

        Returns:
            Number of registered versions.
        """
        return len(self._versions)

    @property
    def current_version(self) -> Optional[str]:
        """Get the current (latest non-deprecated) version.

        Returns:
            Latest version string, or None if no versions registered.
        """
        latest = self.get_latest_version()
        return latest.version if latest else None

    @property
    def version_history(self) -> List[VersionEntry]:
        """Get version history in registration order.

        Returns:
            List of VersionEntry objects in registration order.
        """
        return self._version_history.copy()

    def register_version(
        self,
        version: str,
        sha_hash: str,
        is_deprecated: bool = False,
        release_date: Optional[datetime] = None,
        compatible_with: Optional[List[str]] = None,
        changelog: Optional[str] = None,
    ) -> VersionEntry:
        """Register a new version.

        Args:
            version: Semantic version string.
            sha_hash: SHA hash of prompt content.
            is_deprecated: Whether version is deprecated.
            release_date: Release date. Defaults to now.
            compatible_with: List of compatible versions.
            changelog: Optional changelog notes.

        Returns:
            Created VersionEntry.

        Raises:
            ValueError: If version format is invalid.
        """
        # Validate version format
        if not version or not re.match(r'^\d+\.\d+\.\d+$', version):
            raise ValueError(f"Invalid semantic version: {version}")

        # Validate sha_hash
        if not sha_hash or len(sha_hash) < 3:
            raise ValueError("Invalid SHA hash: must be at least 3 characters")

        entry = VersionEntry(
            version=version,
            release_date=release_date or datetime.now(),
            sha_hash=sha_hash,
            is_deprecated=is_deprecated,
            compatible_with=compatible_with or [],
            changelog=changelog,
        )

        with self._local_lock:
            self._versions[version] = entry
            self._version_history.append(entry)

        # Create release directory if releases_path is set
        if self._releases_path:
            version_dir = self._releases_path / f"v{version}"
            version_dir.mkdir(parents=True, exist_ok=True)

        return entry

    def get_version(self, version: str) -> Optional[VersionEntry]:
        """Get version entry by version string.

        Args:
            version: Version string to look up.

        Returns:
            VersionEntry if found, None otherwise.
        """
        return self._versions.get(version)

    def get_latest_version(self) -> Optional[VersionEntry]:
        """Get the latest non-deprecated version.

        Returns:
            Latest VersionEntry, or None if no versions registered.
        """
        if not self._versions:
            return None

        latest: Optional[VersionEntry] = None
        latest_parsed: Optional[Tuple[int, int, int]] = None

        for entry in self._versions.values():
            if entry.is_deprecated:
                continue
            try:
                parsed = entry.parse_version()
                if latest_parsed is None or parsed > latest_parsed:
                    latest = entry
                    latest_parsed = parsed
            except ValueError:
                continue

        return latest

    def negotiate_version(
        self,
        repo_requested_version: Optional[str] = None,
        requested: Optional[str] = None,
        available_versions: Optional[List[str]] = None,
        available: Optional[List[str]] = None,
    ) -> NegotiationResult:
        """Negotiate a compatible version.

        Args:
            repo_requested_version: Requested version string (preferred param name).
            requested: Requested version string (alternative param name).
            available_versions: List of available versions (preferred param name).
            available: List of available versions (alternative param name).

        Returns:
            NegotiationResult with compatibility info.
        """
        req_version = repo_requested_version or requested or ""
        avail_versions = available_versions or available or list(self._versions.keys())

        # Check if requested version exists
        if req_version in self._versions:
            entry = self._versions[req_version]

            # Check if deprecated
            if entry.is_deprecated:
                return NegotiationResult(
                    version=req_version,
                    compatible=False,
                    error_message=f"Version {req_version} is deprecated",
                    entry=entry,
                )

            # Check if available
            if req_version in avail_versions:
                return NegotiationResult(
                    version=req_version,
                    compatible=True,
                    error_message="",
                    entry=entry,
                )

        # Check if requesting future version
        try:
            req_match = re.match(r'^(\d+)\.(\d+)\.(\d+)$', req_version)
            if req_match:
                req_major = int(req_match.group(1))
                req_minor = int(req_match.group(2))
                req_patch = int(req_match.group(3))

                max_version: Optional[Tuple[int, int, int]] = None
                for v in avail_versions:
                    if v in self._versions:
                        entry = self._versions[v]
                        try:
                            parsed = entry.parse_version()
                            if max_version is None or parsed > max_version:
                                max_version = parsed
                        except ValueError:
                            pass

                if max_version:
                    req_tuple = (req_major, req_minor, req_patch)
                    if req_tuple > max_version:
                        return NegotiationResult(
                            version=req_version,
                            compatible=False,
                            error_message=f"Version {req_version} is not yet available (future version)",
                            entry=None,
                        )
        except ValueError:
            pass

        # Try major version match
        try:
            match = re.match(r'^(\d+)\.', req_version)
            if match:
                req_major = int(match.group(1))

                best_match: Optional[VersionEntry] = None
                best_parsed: Optional[Tuple[int, int, int]] = None

                for version in avail_versions:
                    if version not in self._versions:
                        continue
                    entry = self._versions[version]
                    if entry.is_deprecated:
                        continue

                    try:
                        parsed = entry.parse_version()
                        major, _, _ = parsed

                        if major == req_major:
                            if best_parsed is None or parsed > best_parsed:
                                best_match = entry
                                best_parsed = parsed
                    except ValueError:
                        continue

                if best_match:
                    return NegotiationResult(
                        version=best_match.version,
                        compatible=True,
                        error_message="",
                        entry=best_match,
                    )

                # Major version not available
                return NegotiationResult(
                    version=req_version,
                    compatible=False,
                    error_message=f"No compatible version found for major version {req_major}",
                    entry=None,
                )
        except ValueError:
            pass

        return NegotiationResult(
            version=req_version,
            compatible=False,
            error_message=f"Version {req_version} not available",
            entry=None,
        )

    def is_compatible(
        self,
        version_a: str,
        version_b: str,
    ) -> bool:
        """Check if two versions are compatible.

        Args:
            version_a: First version string.
            version_b: Second version string.

        Returns:
            True if versions are compatible, False otherwise.
        """
        if version_a == version_b:
            return True

        entry_a = self._versions.get(version_a)
        entry_b = self._versions.get(version_b)

        if entry_a and version_b in entry_a.compatible_with:
            return True
        if entry_b and version_a in entry_b.compatible_with:
            return True

        # Check major version compatibility
        try:
            match_a = re.match(r'^(\d+)\.(\d+)\.(\d+)$', version_a)
            match_b = re.match(r'^(\d+)\.(\d+)\.(\d+)$', version_b)

            if match_a and match_b:
                major_a = int(match_a.group(1))
                major_b = int(match_b.group(1))

                # Same major version: compatible
                if major_a == major_b:
                    return True

                return False
        except ValueError:
            pass

        return False

    def check_compatibility(
        self,
        version_a: str,
        version_b: str,
    ) -> bool:
        """Alias for is_compatible.

        Args:
            version_a: First version string.
            version_b: Second version string.

        Returns:
            True if versions are compatible, False otherwise.
        """
        return self.is_compatible(version_a, version_b)

    def is_version_deprecated(self, version: str) -> bool:
        """Check if a version is deprecated.

        Args:
            version: Version string to check.

        Returns:
            True if deprecated, False otherwise.
        """
        entry = self._versions.get(version)
        return entry.is_deprecated if entry else False

    def list_versions(
        self,
        include_deprecated: bool = False,
    ) -> List[VersionEntry]:
        """List all registered versions.

        Args:
            include_deprecated: Whether to include deprecated versions.

        Returns:
            List of VersionEntry objects.
        """
        versions = list(self._versions.values())
        if not include_deprecated:
            versions = [v for v in versions if not v.is_deprecated]
        return sorted(versions, key=lambda v: v.version)

    def save_manifest(self, path: Optional[Path] = None) -> None:
        """Save versions to YAML file (alias for save_to_file).

        Args:
            path: Path to save to. Uses default if None.
        """
        self.save_to_file(path)

    def load_manifest(self, path: Optional[Path] = None) -> None:
        """Load versions from YAML file (alias for load_from_file).

        Args:
            path: Path to load from. Uses default if None.
        """
        self.load_from_file(path)

    def save_to_file(self, path: Optional[Path] = None) -> None:
        """Save versions to YAML file.

        Args:
            path: Path to save to. Uses default if None.
        """
        target = path or self._versions_file

        data = {
            "versions": [
                {
                    "version": v.version,
                    "release_date": v.release_date.isoformat(),
                    "sha_hash": v.sha_hash,
                    "is_deprecated": v.is_deprecated,
                    "compatible_with": v.compatible_with,
                    "changelog": v.changelog,
                }
                for v in self._versions.values()
            ]
        }

        with open(target, "w") as f:
            yaml.safe_dump(data, f, default_flow_style=False)

    def load_from_file(self, path: Optional[Path] = None) -> None:
        """Load versions from YAML file.

        Args:
            path: Path to load from. Uses default if None.
        """
        target = path or self._versions_file

        if not target.exists():
            return

        with open(target) as f:
            data = yaml.safe_load(f)

        if not data or "versions" not in data:
            return

        for v in data["versions"]:
            release_date = v.get("release_date")
            if isinstance(release_date, str):
                release_date = datetime.fromisoformat(release_date)

            entry = VersionEntry(
                version=v["version"],
                release_date=release_date or datetime.now(),
                sha_hash=v.get("sha_hash", ""),
                is_deprecated=v.get("is_deprecated", False),
                compatible_with=v.get("compatible_with", []),
                changelog=v.get("changelog"),
            )
            self._versions[entry.version] = entry
            self._version_history.append(entry)


__all__ = [
    "PromptVersionManager",
    "VersionEntry",
    "NegotiationResult",
    "VersionNegotiationError",
    "VersionCompatibilityError",
]
