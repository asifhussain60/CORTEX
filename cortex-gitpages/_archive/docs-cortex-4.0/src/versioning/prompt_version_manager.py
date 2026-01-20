"""
Prompt Version Management System.

Implements version negotiation, compatibility checking, and backward compatibility
verification for CORTEX prompt releases.

Key components:
- VersionEntry: Dataclass representing a prompt release version
- PromptVersionManager: Singleton managing version lifecycle and negotiation

Enables:
- Versioned prompt releases in cortex-brain/releases/vX.Y.Z/
- Version negotiation between repo and hub
- Compatibility matrix lookup
- Deprecation tracking
- SHA hash verification
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import yaml
import hashlib
import re
from threading import Lock


@dataclass
class VersionEntry:
    """Represents a single prompt release version.
    
    Attributes:
        version: Semantic version string (e.g., "1.0.0")
        release_date: Timestamp when version was released
        sha_hash: SHA256 hash of prompt content for verification
        is_deprecated: Whether this version is deprecated
        metadata: Optional additional metadata (release notes, features, etc.)
    """

    version: str
    release_date: datetime
    sha_hash: str
    is_deprecated: bool = False
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)

    def __post_init__(self):
        """Validate version format after dataclass construction."""
        if not self._is_valid_semantic_version():
            raise ValueError(f"Invalid semantic version format: {self.version}")
        if self.metadata is None:
            self.metadata = {}

    def _is_valid_semantic_version(self) -> bool:
        """Check if version follows semantic versioning (major.minor.patch).
        
        Returns:
            bool: True if version is valid semantic version format
        """
        pattern = r"^\d+\.\d+\.\d+$"
        return bool(re.match(pattern, self.version))

    def get_major_version(self) -> int:
        """Extract major version number.
        
        Returns:
            int: Major version component
        """
        return int(self.version.split(".")[0])

    def get_minor_version(self) -> int:
        """Extract minor version number.
        
        Returns:
            int: Minor version component
        """
        return int(self.version.split(".")[1])

    def get_patch_version(self) -> int:
        """Extract patch version number.
        
        Returns:
            int: Patch version component
        """
        return int(self.version.split(".")[2])


@dataclass
class VersionNegotiationResult:
    """Result of version negotiation between repo and hub.
    
    Attributes:
        version: Negotiated version (or requested if incompatible)
        compatible: Whether requested and available versions are compatible
        error_message: Error description if incompatible
        reason: Detailed reason for compatibility decision
    """

    version: str
    compatible: bool
    error_message: str = ""
    reason: str = ""


class PromptVersionManager:
    """Singleton managing prompt version releases and negotiation.
    
    Handles:
    - Version registration and tracking
    - Version negotiation (repo requests X, hub has Y)
    - Compatibility matrix lookup
    - Deprecation tracking
    - Version history maintenance
    """

    _instance: Optional["PromptVersionManager"] = None
    _lock: Lock = Lock()

    def __new__(cls, *args, **kwargs):
        """Implement singleton pattern with thread safety."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._init_state()
        return cls._instance

    def _init_state(self):
        """Initialize internal state."""
        self.releases_path = Path("cortex_brain") / "releases"
        self.manifest_path = Path("cortex_brain") / "tier0" / "prompt-versions.yaml"
        self.versions: Dict[str, VersionEntry] = {}
        self.current_version: Optional[str] = None
        self.compatibility_matrix: Dict[Tuple[str, str], bool] = {}

    def __init__(
        self,
        releases_path: Optional[Path] = None,
        manifest_path: Optional[Path] = None,
    ):
        """Initialize PromptVersionManager.
        
        Args:
            releases_path: Path to releases directory (default: cortex-brain/releases)
            manifest_path: Path to manifest YAML (default: cortex-brain/tier0/prompt-versions.yaml)
        """
        if releases_path is not None:
            self.releases_path = releases_path
        if manifest_path is not None:
            self.manifest_path = manifest_path

    @property
    def version_count(self) -> int:
        """Get count of registered versions.
        
        Returns:
            int: Number of versions in store
        """
        return len(self.versions)

    @property
    def version_history(self) -> List[VersionEntry]:
        """Get version history in chronological order.
        
        Returns:
            List[VersionEntry]: Versions sorted by release date
        """
        return sorted(
            self.versions.values(),
            key=lambda v: v.release_date,
        )

    def register_version(
        self,
        version: str,
        sha_hash: str,
        is_deprecated: bool = False,
    ) -> VersionEntry:
        """Register a new prompt version release.
        
        Args:
            version: Semantic version string (e.g., "1.0.0")
            sha_hash: SHA256 hash of prompt content
            is_deprecated: Whether this version is deprecated
            
        Returns:
            VersionEntry: The registered version entry
            
        Raises:
            ValueError: If version format is invalid
        """
        if not version:
            raise ValueError("Version string cannot be empty")

        entry = VersionEntry(
            version=version,
            release_date=datetime.now(),
            sha_hash=sha_hash,
            is_deprecated=is_deprecated,
        )

        self.versions[version] = entry
        self.current_version = version

        # Create release directory
        self._create_release_directory(version)

        # Update compatibility matrix
        self._update_compatibility_matrix(version)

        return entry

    def get_version(self, version: str) -> Optional[VersionEntry]:
        """Retrieve version by version string.
        
        Args:
            version: Version string to look up
            
        Returns:
            VersionEntry if found, None otherwise
        """
        return self.versions.get(version)

    def negotiate_version(
        self,
        repo_requested_version: str,
        available_versions: List[str],
    ) -> VersionNegotiationResult:
        """Negotiate version compatibility between repo and hub.
        
        Args:
            repo_requested_version: Version requested by repo
            available_versions: List of versions available at hub
            
        Returns:
            VersionNegotiationResult with compatibility status
        """
        # Check if requested version exists
        if repo_requested_version not in self.versions:
            # Check if it's a future version (valid format but not registered)
            if self._is_future_version(repo_requested_version):
                return VersionNegotiationResult(
                    version=repo_requested_version,
                    compatible=False,
                    error_message="Requested version is a future release not yet available",
                    reason="VERSION_NOT_AVAILABLE",
                )
            else:
                return VersionNegotiationResult(
                    version=repo_requested_version,
                    compatible=False,
                    error_message="Requested version is unknown",
                    reason="VERSION_UNKNOWN",
                )

        # Check if requested version is deprecated
        requested_entry = self.versions[repo_requested_version]
        if requested_entry.is_deprecated:
            return VersionNegotiationResult(
                version=repo_requested_version,
                compatible=False,
                error_message=f"Requested version {repo_requested_version} is deprecated",
                reason="VERSION_DEPRECATED",
            )

        # Try to find compatible version in available_versions
        for available in available_versions:
            if self.is_compatible(repo_requested_version, available):
                return VersionNegotiationResult(
                    version=available,
                    compatible=True,
                    error_message="",
                    reason="VERSION_COMPATIBLE",
                )

        # No compatible version found
        return VersionNegotiationResult(
            version=repo_requested_version,
            compatible=False,
            error_message=f"No compatible version found. Requested: {repo_requested_version}, Available: {available_versions}",
            reason="VERSION_INCOMPATIBLE",
        )

    def is_compatible(self, version1: str, version2: str) -> bool:
        """Check if two versions are compatible.
        
        Compatible means:
        - Same major version
        - version2 >= version1 (forward compatibility)
        
        Args:
            version1: First version string
            version2: Second version string
            
        Returns:
            bool: True if versions are compatible
        """
        key = (version1, version2)
        if key in self.compatibility_matrix:
            return self.compatibility_matrix[key]

        if version1 not in self.versions or version2 not in self.versions:
            return False

        v1_entry = self.versions[version1]
        v2_entry = self.versions[version2]

        # Major versions must match for compatibility
        if v1_entry.get_major_version() != v2_entry.get_major_version():
            return False

        # v2 must be >= v1 (forward compatibility)
        if (
            v2_entry.get_minor_version() < v1_entry.get_minor_version()
            or (
                v2_entry.get_minor_version() == v1_entry.get_minor_version()
                and v2_entry.get_patch_version() < v1_entry.get_patch_version()
            )
        ):
            return False

        return True

    def save_manifest(self) -> None:
        """Save version manifest to YAML file.
        
        Creates cortex-brain/tier0/prompt-versions.yaml with all registered versions.
        """
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)

        manifest_data = {
            "metadata": {
                "description": "CORTEX Prompt Version Manifest",
                "updated_at": datetime.now().isoformat(),
            },
            "current_version": self.current_version,
            "versions": [
                {
                    "version": v.version,
                    "release_date": v.release_date.isoformat(),
                    "sha_hash": v.sha_hash,
                    "is_deprecated": v.is_deprecated,
                    "metadata": v.metadata,
                }
                for v in self.version_history
            ],
        }

        with open(self.manifest_path, "w") as f:
            yaml.dump(manifest_data, f, default_flow_style=False)

    def load_manifest(self) -> None:
        """Load version manifest from YAML file.
        
        Restores all versions from cortex-brain/tier0/prompt-versions.yaml.
        """
        if not self.manifest_path.exists():
            return

        with open(self.manifest_path) as f:
            manifest_data = yaml.safe_load(f)

        if manifest_data is None:
            return

        for v_data in manifest_data.get("versions", []):
            entry = VersionEntry(
                version=v_data["version"],
                release_date=datetime.fromisoformat(
                    v_data["release_date"]
                ),
                sha_hash=v_data["sha_hash"],
                is_deprecated=v_data.get("is_deprecated", False),
                metadata=v_data.get("metadata", {}),
            )
            self.versions[entry.version] = entry
            self._update_compatibility_matrix(entry.version)

        self.current_version = manifest_data.get("current_version")

    def _create_release_directory(self, version: str) -> None:
        """Create release directory for version.
        
        Args:
            version: Version string
        """
        version_dir = self.releases_path / f"v{version}"
        version_dir.mkdir(parents=True, exist_ok=True)

    def _update_compatibility_matrix(self, version: str) -> None:
        """Update compatibility matrix when new version added.
        
        Args:
            version: New version string
        """
        new_entry = self.versions[version]

        for existing_version, existing_entry in self.versions.items():
            if existing_version == version:
                continue

            # Check compatibility both directions
            compatible = (
                new_entry.get_major_version() == existing_entry.get_major_version()
                and (
                    new_entry.get_minor_version() > existing_entry.get_minor_version()
                    or (
                        new_entry.get_minor_version()
                        == existing_entry.get_minor_version()
                        and new_entry.get_patch_version()
                        >= existing_entry.get_patch_version()
                    )
                )
            )

            self.compatibility_matrix[(existing_version, version)] = compatible

    def _is_future_version(self, version: str) -> bool:
        """Check if version string is a valid but future version.
        
        Args:
            version: Version string to check
            
        Returns:
            bool: True if version format is valid but not yet registered
        """
        try:
            entry = VersionEntry(
                version=version,
                release_date=datetime.now(),
                sha_hash="",
                is_deprecated=False,
            )
            # If we can construct a VersionEntry, format is valid
            return True
        except ValueError:
            return False

    @classmethod
    def reset_singleton(cls) -> None:
        """Reset singleton instance for testing.
        
        This method is for testing purposes only and should not be used in production.
        """
        with cls._lock:
            cls._instance = None
