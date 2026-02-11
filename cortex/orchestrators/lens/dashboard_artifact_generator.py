"""
AC_START: AC-ENH087-T5-S4-GREEN-001
ENH-087 Track 5 Stage 4: Dashboard Artifacts Generation
GREEN Phase: DashboardArtifactGenerator Implementation

Orchestrator for generating, persisting, and managing dashboard artifacts.
Supports multiple output formats (JSON, YAML, CSV) with full lifecycle management.

Author: CORTEX Architect
Authority: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

import json
import logging
import shutil
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, Any, Optional, List

import yaml

logger = logging.getLogger(__name__)


class ArtifactStatus(Enum):
    """Enumeration of dashboard artifact lifecycle states."""

    PENDING = "PENDING"  # Created, not yet validated
    ACTIVE = "ACTIVE"  # Validated, available for rendering
    ARCHIVED = "ARCHIVED"  # Moved to archive, still accessible
    DELETED = "DELETED"  # Marked for deletion


class OutputFormat(Enum):
    """Supported dashboard artifact output formats."""

    JSON = "json"  # Primary format, full fidelity
    YAML = "yaml"  # Human-readable alternative
    CSV = "csv"  # Simplified tabular export


@dataclass
class DashboardMetadata:
    """Dashboard artifact metadata and tracking information."""

    analysis_id: str  # Unique identifier for analysis
    repository_id: str  # Repository being analyzed
    analysis_type: str  # Type of analysis (LENS, REFACTOR, etc.)
    orchestrator: str  # Orchestrator that generated artifact
    created_at: str  # ISO 8601 UTC timestamp
    updated_at: Optional[str] = None  # ISO 8601 UTC timestamp (optional)
    expires_at: Optional[str] = None  # Optional expiration time

    generation_started_at: Optional[str] = None  # When generation started
    generation_completed_at: Optional[str] = None  # When generation completed
    generation_status: str = "PENDING"  # PENDING, COMPLETED, FAILED, PARTIAL
    generation_errors: List[str] = field(default_factory=list)  # Errors if failed

    version: int = 1  # Incremental version
    previous_version_id: Optional[str] = None  # ID of prior version
    update_reason: Optional[str] = None  # Why artifact was updated

    source_session_id: str = ""  # Session that generated analysis
    source_repo_path: str = ""  # Repository path analyzed
    analysis_version: str = "1.0.0"  # Version of analysis algorithm

    schema_version: str = "1.0.0"  # Schema version for compatibility

    total_items: int = 0  # Count of items analyzed
    analysis_duration_ms: float = 0.0  # Duration in milliseconds
    item_categories: Dict[str, int] = field(default_factory=dict)  # Breakdown by category
    confidence_scores: Dict[str, float] = field(default_factory=dict)  # Quality metrics

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary for serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DashboardMetadata":
        """Create metadata from dictionary (deserialization)."""
        return cls(**data)


@dataclass
class DashboardArtifact:
    """Dashboard artifact with metadata and data payload."""

    artifact_id: str  # Unique artifact identifier
    status: ArtifactStatus  # Current lifecycle state
    metadata: DashboardMetadata  # Artifact metadata
    data: Dict[str, Any]  # Artifact data payload
    format: OutputFormat = OutputFormat.JSON  # Primary format

    def to_dict(self) -> Dict[str, Any]:
        """Convert artifact to dictionary for serialization."""
        return {
            "artifact_id": self.artifact_id,
            "status": self.status.value,
            "metadata": self.metadata.to_dict(),
            "data": self.data,
            "format": self.format.value,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DashboardArtifact":
        """Create artifact from dictionary (deserialization)."""
        return cls(
            artifact_id=data["artifact_id"],
            status=ArtifactStatus(data["status"]),
            metadata=DashboardMetadata.from_dict(data["metadata"]),
            data=data["data"],
            format=OutputFormat(data.get("format", "json")),
        )


class DashboardArtifactGenerator:
    """
    Orchestrator for generating and managing dashboard artifacts.

    Responsibilities:
    - Generate artifacts from LENS analysis results
    - Persist artifacts to physical files (YAML)
    - Support multiple output formats (JSON, YAML, CSV)
    - Manage artifact lifecycle (create, read, update, archive, delete)
    - Validate artifact integrity and schema
    - Track artifact metadata and lineage
    """

    DEFAULT_TTL_DAYS: int = 30
    ARTIFACTS_DIR: str = "dashboards"
    ACTIVE_DIR: str = "active"
    ARCHIVE_DIR: str = "archive"
    STAGING_DIR: str = "staging"

    def __init__(self, cortex_brain_path: Path) -> None:
        """
        Initialize DashboardArtifactGenerator.

        Args:
            cortex_brain_path: Path to cortex_brain root directory
        """
        self.cortex_brain_path = Path(cortex_brain_path)
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Ensure all required artifact directories exist."""
        base_dir = self.cortex_brain_path / self.ARTIFACTS_DIR
        for subdir in [self.ACTIVE_DIR, self.ARCHIVE_DIR, self.STAGING_DIR]:
            (base_dir / subdir).mkdir(parents=True, exist_ok=True)
        logger.debug(f"Dashboard artifact directories ensured at {base_dir}")

    def generate_artifact(
        self,
        artifact_id: str,
        analysis_id: str,
        repository_id: str,
        analysis_type: str,
        orchestrator: str,
        data: Dict[str, Any],
        session_id: str = "",
        repo_path: str = "",
        item_count: int = 0,
        analysis_duration_ms: float = 0.0,
        categories: Optional[Dict[str, int]] = None,
        scores: Optional[Dict[str, float]] = None,
    ) -> DashboardArtifact:
        """
        Generate and persist a new dashboard artifact.

        Args:
            artifact_id: Unique identifier for the artifact
            analysis_id: Analysis that generated this artifact
            repository_id: Repository being analyzed
            analysis_type: Type of analysis (LENS, REFACTOR, etc.)
            orchestrator: Orchestrator responsible for generation
            data: Artifact data payload
            session_id: Session ID that generated analysis
            repo_path: Repository path analyzed
            item_count: Total items analyzed
            analysis_duration_ms: Duration of analysis
            categories: Item breakdown by category
            scores: Confidence scores by category

        Returns:
            DashboardArtifact with PENDING status
        """
        now = datetime.utcnow().isoformat()
        metadata = DashboardMetadata(
            analysis_id=analysis_id,
            repository_id=repository_id,
            analysis_type=analysis_type,
            orchestrator=orchestrator,
            created_at=now,
            generation_started_at=now,
            source_session_id=session_id,
            source_repo_path=repo_path,
            total_items=item_count,
            analysis_duration_ms=analysis_duration_ms,
            item_categories=categories or {},
            confidence_scores=scores or {},
        )

        artifact = DashboardArtifact(
            artifact_id=artifact_id,
            status=ArtifactStatus.PENDING,
            metadata=metadata,
            data=data,
        )

        # Persist to staging directory
        self._write_artifact(artifact, self.STAGING_DIR)

        logger.info(f"Generated artifact {artifact_id} (status: PENDING)")
        return artifact

    def validate_artifact(self, artifact_id: str) -> bool:
        """
        Validate artifact schema and integrity.

        Args:
            artifact_id: ID of artifact to validate

        Returns:
            True if valid, False otherwise
        """
        artifact = self.get_artifact(artifact_id)
        if artifact is None:
            logger.error(f"Artifact {artifact_id} not found for validation")
            return False

        # Validate required metadata fields
        required_fields = [
            "analysis_id",
            "repository_id",
            "analysis_type",
            "orchestrator",
            "created_at",
        ]
        for field_name in required_fields:
            if not getattr(artifact.metadata, field_name):
                logger.error(f"Missing required field: {field_name}")
                return False

        # Validate data is not empty
        if not artifact.data:
            logger.error("Artifact data is empty")
            return False

        logger.info(f"Artifact {artifact_id} validation passed")
        return True

    def activate_artifact(self, artifact_id: str) -> bool:
        """
        Activate artifact (move from STAGING to ACTIVE).

        Args:
            artifact_id: ID of artifact to activate

        Returns:
            True if activated, False otherwise
        """
        if not self.validate_artifact(artifact_id):
            logger.error(f"Artifact {artifact_id} validation failed, cannot activate")
            return False

        artifact = self.get_artifact(artifact_id)
        if artifact is None:
            return False

        # Update status and move to active directory
        artifact.status = ArtifactStatus.ACTIVE
        artifact.metadata.generation_status = "COMPLETED"
        artifact.metadata.generation_completed_at = datetime.utcnow().isoformat()

        self._delete_from_directory(artifact_id, self.STAGING_DIR)
        self._write_artifact(artifact, self.ACTIVE_DIR)

        logger.info(f"Artifact {artifact_id} activated (moved to ACTIVE)")
        return True

    def get_artifact(self, artifact_id: str) -> Optional[DashboardArtifact]:
        """
        Retrieve artifact by ID.

        Args:
            artifact_id: ID of artifact to retrieve

        Returns:
            DashboardArtifact or None if not found
        """
        # Check active directory first
        artifact_path = self._get_artifact_path(artifact_id, self.ACTIVE_DIR)
        if artifact_path.exists():
            return self._read_artifact(artifact_path)

        # Check staging directory
        artifact_path = self._get_artifact_path(artifact_id, self.STAGING_DIR)
        if artifact_path.exists():
            return self._read_artifact(artifact_path)

        # Check archive directory
        artifact_path = self._get_artifact_path(artifact_id, self.ARCHIVE_DIR)
        if artifact_path.exists():
            return self._read_artifact(artifact_path)

        logger.warning(f"Artifact {artifact_id} not found")
        return None

    def update_artifact(
        self, artifact_id: str, updates: Dict[str, Any], reason: str = ""
    ) -> bool:
        """
        Update artifact metadata and data.

        Args:
            artifact_id: ID of artifact to update
            updates: Dictionary of fields to update
            reason: Reason for update

        Returns:
            True if updated, False otherwise
        """
        artifact = self.get_artifact(artifact_id)
        if artifact is None:
            logger.error(f"Artifact {artifact_id} not found for update")
            return False

        # Track previous version
        artifact.metadata.previous_version_id = artifact_id
        artifact.metadata.version += 1
        artifact.metadata.updated_at = datetime.utcnow().isoformat()
        artifact.metadata.update_reason = reason

        # Apply updates
        if "data" in updates:
            artifact.data = updates["data"]
        if "metadata" in updates:
            for key, value in updates["metadata"].items():
                if hasattr(artifact.metadata, key):
                    setattr(artifact.metadata, key, value)

        # Write back to same directory
        status_dir = self.ACTIVE_DIR if artifact.status == ArtifactStatus.ACTIVE else self.STAGING_DIR
        self._write_artifact(artifact, status_dir)

        logger.info(f"Artifact {artifact_id} updated (version {artifact.metadata.version})")
        return True

    def archive_artifact(self, artifact_id: str) -> bool:
        """
        Archive artifact (move from ACTIVE to ARCHIVE).

        Args:
            artifact_id: ID of artifact to archive

        Returns:
            True if archived, False otherwise
        """
        artifact = self.get_artifact(artifact_id)
        if artifact is None:
            logger.error(f"Artifact {artifact_id} not found for archival")
            return False

        # Determine source directory before changing status
        source_dir = (
            self.ACTIVE_DIR
            if artifact.status == ArtifactStatus.ACTIVE
            else self.STAGING_DIR
        )

        # Update status and move to archive
        artifact.status = ArtifactStatus.ARCHIVED
        self._delete_from_directory(artifact_id, source_dir)
        self._write_artifact(artifact, self.ARCHIVE_DIR)

        logger.info(f"Artifact {artifact_id} archived")
        return True

    def delete_artifact(self, artifact_id: str) -> bool:
        """
        Delete artifact permanently.

        Args:
            artifact_id: ID of artifact to delete

        Returns:
            True if deleted, False otherwise
        """
        artifact = self.get_artifact(artifact_id)
        if artifact is None:
            logger.error(f"Artifact {artifact_id} not found for deletion")
            return False

        # Determine which directory it's in
        for subdir in [self.ACTIVE_DIR, self.STAGING_DIR, self.ARCHIVE_DIR]:
            if self._delete_from_directory(artifact_id, subdir):
                logger.info(f"Artifact {artifact_id} deleted from {subdir}")
                return True

        return False

    def list_active_artifacts(self) -> List[DashboardArtifact]:
        """
        List all active artifacts.

        Returns:
            List of active DashboardArtifact objects
        """
        return self._list_artifacts_in_directory(self.ACTIVE_DIR)

    def list_archived_artifacts(self) -> List[DashboardArtifact]:
        """
        List all archived artifacts.

        Returns:
            List of archived DashboardArtifact objects
        """
        return self._list_artifacts_in_directory(self.ARCHIVE_DIR)

    def export_as_json(self, artifact_id: str) -> Optional[str]:
        """
        Export artifact as JSON string.

        Args:
            artifact_id: ID of artifact to export

        Returns:
            JSON string or None if not found
        """
        artifact = self.get_artifact(artifact_id)
        if artifact is None:
            return None

        return json.dumps(artifact.to_dict(), indent=2, default=str)

    def export_as_yaml(self, artifact_id: str) -> Optional[str]:
        """
        Export artifact as YAML string.

        Args:
            artifact_id: ID of artifact to export

        Returns:
            YAML string or None if not found
        """
        artifact = self.get_artifact(artifact_id)
        if artifact is None:
            return None

        return yaml.dump(artifact.to_dict(), default_flow_style=False, sort_keys=False)

    def export_as_csv(self, artifact_id: str) -> Optional[str]:
        """
        Export artifact as CSV (simplified tabular format).

        Args:
            artifact_id: ID of artifact to export

        Returns:
            CSV string or None if not found
        """
        artifact = self.get_artifact(artifact_id)
        if artifact is None:
            return None

        # Simple CSV export of metadata
        lines = [
            "Field,Value",
            f"artifact_id,{artifact.artifact_id}",
            f"analysis_id,{artifact.metadata.analysis_id}",
            f"repository_id,{artifact.metadata.repository_id}",
            f"analysis_type,{artifact.metadata.analysis_type}",
            f"orchestrator,{artifact.metadata.orchestrator}",
            f"created_at,{artifact.metadata.created_at}",
            f"status,{artifact.status.value}",
            f"version,{artifact.metadata.version}",
            f"total_items,{artifact.metadata.total_items}",
            f"analysis_duration_ms,{artifact.metadata.analysis_duration_ms}",
        ]

        return "\n".join(lines)

    def cleanup_expired_artifacts(self, ttl_days: int = DEFAULT_TTL_DAYS) -> int:
        """
        Cleanup expired artifacts (move to archive or delete).

        Args:
            ttl_days: Time-to-live in days (default: 30)

        Returns:
            Count of artifacts cleaned up
        """
        now = datetime.utcnow()
        cutoff_date = now - timedelta(days=ttl_days)
        cleaned_count = 0

        # Check active artifacts
        for artifact in self.list_active_artifacts():
            created = datetime.fromisoformat(artifact.metadata.created_at)
            if created < cutoff_date:
                if self.archive_artifact(artifact.artifact_id):
                    cleaned_count += 1
                    logger.info(f"Archived expired artifact {artifact.artifact_id}")

        return cleaned_count

    def detect_orphaned_artifacts(self) -> List[str]:
        """
        Detect orphaned artifacts (broken references).

        Returns:
            List of orphaned artifact IDs
        """
        orphaned = []

        # Check all artifacts
        for artifact in self.list_active_artifacts() + self.list_archived_artifacts():
            # Verify session exists
            session_path = self.cortex_brain_path / "sessions" / f"{artifact.metadata.source_session_id}.yaml"
            if artifact.metadata.source_session_id and not session_path.exists():
                orphaned.append(artifact.artifact_id)
                logger.warning(f"Orphaned artifact {artifact.artifact_id}: session not found")

            # Verify repo exists
            repo_path = (
                self.cortex_brain_path / "onboarded_repos" / artifact.metadata.repository_id
            )
            if not repo_path.exists():
                if artifact.artifact_id not in orphaned:
                    orphaned.append(artifact.artifact_id)
                logger.warning(f"Orphaned artifact {artifact.artifact_id}: repo not found")

        return orphaned

    # Private methods

    def _get_artifact_path(
        self, artifact_id: str, subdir: str = ACTIVE_DIR
    ) -> Path:
        """Get full path to artifact file."""
        return self.cortex_brain_path / self.ARTIFACTS_DIR / subdir / f"{artifact_id}.yaml"

    def _write_artifact(self, artifact: DashboardArtifact, subdir: str) -> None:
        """Write artifact to YAML file."""
        path = self._get_artifact_path(artifact.artifact_id, subdir)
        with open(path, "w") as f:
            yaml.dump(artifact.to_dict(), f, default_flow_style=False, sort_keys=False)
        logger.debug(f"Wrote artifact {artifact.artifact_id} to {path}")

    def _read_artifact(self, path: Path) -> DashboardArtifact:
        """Read artifact from YAML file."""
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        artifact = DashboardArtifact.from_dict(data)
        logger.debug(f"Read artifact {artifact.artifact_id} from {path}")
        return artifact

    def _delete_from_directory(self, artifact_id: str, subdir: str) -> bool:
        """Delete artifact file from specified directory."""
        path = self._get_artifact_path(artifact_id, subdir)
        if path.exists():
            path.unlink()
            logger.debug(f"Deleted artifact file {path}")
            return True
        return False

    def _list_artifacts_in_directory(self, subdir: str) -> List[DashboardArtifact]:
        """List all artifacts in specified directory."""
        dir_path = self.cortex_brain_path / self.ARTIFACTS_DIR / subdir
        artifacts = []

        if not dir_path.exists():
            return artifacts

        for yaml_file in dir_path.glob("*.yaml"):
            try:
                artifact = self._read_artifact(yaml_file)
                artifacts.append(artifact)
            except Exception as e:
                logger.error(f"Error reading artifact {yaml_file}: {e}")

        return artifacts


# AC_COMPLETE: AC-ENH087-T5-S4-GREEN-001 ✅ DashboardArtifactGenerator orchestrator implemented
