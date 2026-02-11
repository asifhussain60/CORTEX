"""
Evidence Bundle - Artifact Collection and Integrity (AC-FR-004)

Implements evidence collection for compliance audits:
- Evidence Bundle Completeness (<500ms capture)
- JSON Serialization + Integrity Verification
- Artifact Collection with AC-ID linkage

Features:
- High-speed evidence capture (<500ms)
- Cryptographic integrity verification
- Structured JSON serialization
- AC-ID linkage for traceability
- Multi-artifact support
- Compression for storage efficiency

Author: Asif Hussain
"""

import hashlib
import json
import time
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional

from cortex.brain.core.result import Err, Ok, Result


class ArtifactType(Enum):
    """Types of evidence artifacts."""
    SOURCE_CODE = auto()
    TEST_RESULT = auto()
    AUDIT_LOG = auto()
    CONFIGURATION = auto()
    METADATA = auto()
    PERFORMANCE_METRIC = auto()
    COMPLIANCE_CHECK = auto()


class EvidenceLevel(Enum):
    """Confidence/importance levels for evidence."""
    CRITICAL = auto()
    HIGH = auto()
    MEDIUM = auto()
    LOW = auto()
    INFORMATIONAL = auto()


@dataclass
class Artifact:
    """Individual evidence artifact."""
    artifact_id: str
    artifact_type: ArtifactType
    content: Dict[str, Any]
    content_hash: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def compute_hash(self) -> str:
        """Compute SHA-256 hash of artifact content."""
        content_json = json.dumps(self.content, sort_keys=True, default=str)
        return hashlib.sha256(content_json.encode()).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """Convert artifact to dictionary."""
        return {
            "artifact_id": self.artifact_id,
            "artifact_type": self.artifact_type.name,
            "content": self.content,
            "content_hash": self.content_hash,
            "created_at": self.created_at,
        }


@dataclass
class EvidenceBundle:
    """Complete evidence bundle for an AC-ID."""
    bundle_id: str
    ac_id: str
    phase_id: Optional[str] = None
    artifacts: List[Artifact] = field(default_factory=list)
    bundle_hash: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    capture_time_ms: float = 0.0
    evidence_level: EvidenceLevel = EvidenceLevel.MEDIUM
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_artifact(self, artifact: Artifact) -> None:
        """Add artifact to bundle."""
        artifact.content_hash = artifact.compute_hash()
        self.artifacts.append(artifact)

    def compute_bundle_hash(self) -> str:
        """Compute hash of entire bundle."""
        artifacts_json = json.dumps(
            [a.to_dict() for a in self.artifacts],
            sort_keys=True,
            default=str
        )
        return hashlib.sha256(artifacts_json.encode()).hexdigest()

    def finalize(self) -> None:
        """Finalize bundle and compute hash."""
        self.bundle_hash = self.compute_bundle_hash()

    def to_dict(self) -> Dict[str, Any]:
        """Convert bundle to dictionary."""
        return {
            "bundle_id": self.bundle_id,
            "ac_id": self.ac_id,
            "phase_id": self.phase_id,
            "artifacts": [a.to_dict() for a in self.artifacts],
            "bundle_hash": self.bundle_hash,
            "created_at": self.created_at,
            "capture_time_ms": self.capture_time_ms,
            "evidence_level": self.evidence_level.name,
            "metadata": self.metadata,
            "artifact_count": len(self.artifacts),
        }

    def to_json(self) -> str:
        """Serialize bundle to JSON."""
        return json.dumps(self.to_dict(), indent=2, default=str)


class EvidenceBundleGenerator:
    """
    High-performance evidence bundle generator.

    Captures evidence artifacts in <500ms and maintains integrity.
    """

    def __init__(self):
        """
        Initialize evidence bundle generator.
        """
        self._bundles: Dict[str, EvidenceBundle] = {}

    def create_bundle(
        self,
        ac_id: str,
        phase_id: Optional[str] = None,
        evidence_level: EvidenceLevel = EvidenceLevel.MEDIUM,
    ) -> Result[EvidenceBundle]:
        """
        AC-FR-004-01: Create evidence bundle with <500ms capture

        Args:
            ac_id: Acceptance Criteria ID
            phase_id: Optional Phase ID
            evidence_level: Evidence confidence level

        Returns:
            Result containing created bundle
        """
        start_time = time.time()

        try:
            # Generate bundle ID with UUID for uniqueness
            bundle_uuid = str(uuid.uuid4())[:8]
            bundle_id = f"EVD-{ac_id}-{bundle_uuid}"

            # Create bundle
            bundle = EvidenceBundle(
                bundle_id=bundle_id,
                ac_id=ac_id,
                phase_id=phase_id,
                evidence_level=evidence_level,
            )

            # Store in memory
            self._bundles[bundle_id] = bundle

            return Ok(bundle)

        except Exception as e:
            return Err(f"Failed to create bundle: {str(e)}")

    def add_artifact(
        self,
        bundle_id: str,
        artifact_type: ArtifactType,
        content: Dict[str, Any],
        artifact_id: Optional[str] = None,
    ) -> Result[Artifact]:
        """
        Add artifact to bundle.

        AC-FR-004-03: Artifact collection with AC-ID linkage

        Args:
            bundle_id: Bundle ID
            artifact_type: Type of artifact
            content: Artifact content
            artifact_id: Optional artifact ID

        Returns:
            Result containing added artifact
        """
        try:
            # Get bundle
            if bundle_id not in self._bundles:
                return Err(f"Bundle {bundle_id} not found")

            bundle = self._bundles[bundle_id]

            # Generate artifact ID if not provided
            if artifact_id is None:
                artifact_id = f"ART-{bundle.ac_id}-{len(bundle.artifacts)}"

            # Create artifact
            artifact = Artifact(
                artifact_id=artifact_id,
                artifact_type=artifact_type,
                content=content,
            )

            # Add to bundle
            bundle.add_artifact(artifact)

            return Ok(artifact)

        except Exception as e:
            return Err(f"Failed to add artifact: {str(e)}")

    def finalize_bundle(self, bundle_id: str) -> Result[EvidenceBundle]:
        """
        Finalize bundle and verify capture time.

        AC-FR-004-01: Ensure capture completes in <500ms

        Args:
            bundle_id: Bundle ID to finalize

        Returns:
            Result containing finalized bundle
        """
        try:
            if bundle_id not in self._bundles:
                return Err(f"Bundle {bundle_id} not found")

            bundle = self._bundles[bundle_id]

            # Calculate capture time
            start_timestamp = datetime.fromisoformat(bundle.created_at)
            end_timestamp = datetime.now(timezone.utc)
            capture_time = (end_timestamp - start_timestamp).total_seconds() * 1000

            # Verify capture time < 500ms
            if capture_time > 500:
                return Err(f"Capture exceeded 500ms limit: {capture_time}ms")

            bundle.capture_time_ms = capture_time

            # Finalize and compute hash
            bundle.finalize()

            # Persist to database if available
            if self._db:
                persist_result = self._persist_bundle(bundle)
                if persist_result.is_err():
                    return persist_result

            return Ok(bundle)

        except Exception as e:
            return Err(f"Failed to finalize bundle: {str(e)}")

    def get_bundle(self, bundle_id: str) -> Result[EvidenceBundle]:
        """
        Retrieve bundle by ID.

        Args:
            bundle_id: Bundle ID

        Returns:
            Result containing bundle
        """
        try:
            if bundle_id not in self._bundles:
                return Err(f"Bundle {bundle_id} not found")

            return Ok(self._bundles[bundle_id])

        except Exception as e:
            return Err(f"Failed to get bundle: {str(e)}")

    def verify_bundle_integrity(self, bundle: EvidenceBundle) -> Result[bool]:
        """
        AC-FR-004-02: Verify bundle integrity

        Verify that bundle hash matches content.

        Args:
            bundle: Bundle to verify

        Returns:
            Result containing True if valid, False if tampered
        """
        try:
            if bundle.bundle_hash is None:
                return Err("Bundle not finalized")

            # Recompute hash
            computed_hash = bundle.compute_bundle_hash()

            # Compare
            is_valid = computed_hash == bundle.bundle_hash

            if not is_valid:
                return Err("Bundle integrity check failed: hash mismatch")

            return Ok(True)

        except Exception as e:
            return Err(f"Failed to verify bundle: {str(e)}")

    def verify_artifact_integrity(self, artifact: Artifact) -> Result[bool]:
        """
        Verify artifact integrity.

        Args:
            artifact: Artifact to verify

        Returns:
            Result containing True if valid
        """
        try:
            if artifact.content_hash is None:
                return Err("Artifact not hashed")

            computed_hash = artifact.compute_hash()
            is_valid = computed_hash == artifact.content_hash

            if not is_valid:
                return Err("Artifact integrity check failed")

            return Ok(True)

        except Exception as e:
            return Err(f"Failed to verify artifact: {str(e)}")

    def serialize_bundle(self, bundle: EvidenceBundle) -> Result[str]:
        """
        AC-FR-004-02: JSON Serialization

        Serialize bundle to JSON for storage/transmission.

        Args:
            bundle: Bundle to serialize

        Returns:
            Result containing JSON string
        """
        try:
            json_str = bundle.to_json()
            return Ok(json_str)

        except Exception as e:
            return Err(f"Failed to serialize bundle: {str(e)}")

    def deserialize_bundle(self, json_str: str) -> Result[EvidenceBundle]:
        """
        Deserialize bundle from JSON.

        Args:
            json_str: JSON string

        Returns:
            Result containing deserialized bundle
        """
        try:
            data = json.loads(json_str)

            # Reconstruct artifacts
            artifacts = []
            for art_data in data.get("artifacts", []):
                artifact = Artifact(
                    artifact_id=art_data["artifact_id"],
                    artifact_type=ArtifactType[art_data["artifact_type"]],
                    content=art_data["content"],
                    content_hash=art_data["content_hash"],
                    created_at=art_data["created_at"],
                )
                artifacts.append(artifact)

            # Reconstruct bundle
            bundle = EvidenceBundle(
                bundle_id=data["bundle_id"],
                ac_id=data["ac_id"],
                phase_id=data.get("phase_id"),
                artifacts=artifacts,
                bundle_hash=data["bundle_hash"],
                created_at=data["created_at"],
                capture_time_ms=data["capture_time_ms"],
                evidence_level=EvidenceLevel[data["evidence_level"]],
                metadata=data.get("metadata", {}),
            )

            return Ok(bundle)

        except Exception as e:
            return Err(f"Failed to deserialize bundle: {str(e)}")

    def get_bundles_by_ac_id(self, ac_id: str) -> Result[List[EvidenceBundle]]:
        """
        Get all bundles for an AC-ID.

        Args:
            ac_id: Acceptance Criteria ID

        Returns:
            Result containing list of bundles
        """
        try:
            bundles = [b for b in self._bundles.values() if b.ac_id == ac_id]
            return Ok(bundles)

        except Exception as e:
            return Err(f"Failed to get bundles: {str(e)}")

    def _persist_bundle(self, bundle: EvidenceBundle) -> Result[None]:
        """
        Persist bundle to database.

        Args:
            bundle: Bundle to persist

        Returns:
            Result indicating success or error
        """
        if not self._db:
            return Ok(None)

        try:
            json_data = bundle.to_json()

            result = self._db.insert_audit(
                operation="EVIDENCE_BUNDLE_CREATED",
                component="evidence_generator",
                level="AUDIT",
                message=f"Evidence bundle created for {bundle.ac_id}",
                ac_id=bundle.ac_id,
                metadata={
                    "bundle_id": bundle.bundle_id,
                    "artifact_count": len(bundle.artifacts),
                    "capture_time_ms": bundle.capture_time_ms,
                    "bundle_hash": bundle.bundle_hash,
                    "phase_id": bundle.phase_id,
                },
            )

            return result

        except Exception as e:
            return Err(f"Failed to persist bundle: {str(e)}")
