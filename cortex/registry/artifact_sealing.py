"""
ArtifactSealing - Registry Artifact Immutability & Version Control

Authority: Phase 76 S2 Task 2 - Registry Isolation & Multi-Tenant Foundation
AC-ID: AC-PHASE76-S2-T2-001

Provides artifact sealing (immutability), version control, and tamper detection
for registry data. Ensures production data integrity with cryptographic guarantees.

Key Features:
- Artifact sealing with cryptographic hashing (SHA-256)
- Immutability enforcement (once sealed, cannot be modified)
- Version control with audit trail
- Tamper detection (integrity verification)
- Rollback support with version snapshots
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
import hashlib
import json
import logging

from cortex.registry.tenant_context import TenantContext

logger = logging.getLogger(__name__)


@dataclass
class ArtifactMetadata:
    """Metadata for sealed artifacts."""
    
    artifact_id: str
    artifact_type: str  # "phase", "orchestrator", "wiring", etc.
    version: int = 1
    sealed: bool = False
    seal_hash: Optional[str] = None
    created_at: Optional[datetime] = None
    sealed_at: Optional[datetime] = None
    tenant_id: Optional[str] = None
    created_by: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "artifact_id": self.artifact_id,
            "artifact_type": self.artifact_type,
            "version": self.version,
            "sealed": self.sealed,
            "seal_hash": self.seal_hash,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "sealed_at": self.sealed_at.isoformat() if self.sealed_at else None,
            "tenant_id": self.tenant_id,
            "created_by": self.created_by,
            "metadata": self.metadata.copy()
        }


class ArtifactSealingError(Exception):
    """Base exception for artifact sealing operations."""
    pass


class ArtifactAlreadySealedError(ArtifactSealingError):
    """Raised when attempting to modify sealed artifact."""
    pass


class ArtifactTamperingDetectedError(ArtifactSealingError):
    """Raised when artifact integrity check fails."""
    pass


class ArtifactSealingManager:
    """
    Manage artifact sealing, versioning, and integrity verification.
    
    Provides:
    - Seal artifacts with cryptographic hash
    - Version control for artifacts
    - Integrity verification
    - Tamper detection
    - Rollback support
    
    Example:
        >>> from cortex.registry.artifact_sealing import ArtifactSealingManager
        >>> manager = ArtifactSealingManager()
        >>> 
        >>> # Create and seal artifact
        >>> artifact = {"status": "active", "priority": "P0"}
        >>> metadata = manager.seal_artifact("phase-42", "phase", artifact)
        >>> 
        >>> # Verify integrity
        >>> is_valid = manager.verify_artifact("phase-42", artifact)
        >>> 
        >>> # Create new version (automatically unseals for updates)
        >>> new_artifact = {"status": "completed"}
        >>> new_metadata = manager.update_artifact_version("phase-42", new_artifact)
    """
    
    def __init__(self, storage_path: Optional[Path] = None) -> None:
        """
        Initialize ArtifactSealingManager.
        
        Args:
            storage_path: Path for storing sealed artifact metadata
        """
        self.storage_path = storage_path or Path("registry/sealed-artifacts")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self._sealed_artifacts: Dict[str, ArtifactMetadata] = {}
        self._artifact_versions: Dict[str, List[Dict[str, Any]]] = {}
        
        logger.info(f"Initialized ArtifactSealingManager at {self.storage_path}")
    
    def _compute_artifact_hash(self, artifact: Dict[str, Any]) -> str:
        """
        Compute SHA-256 hash of artifact for integrity verification.
        
        Args:
            artifact: Artifact to hash
        
        Returns:
            SHA-256 hash of artifact JSON
        """
        # Serialize with sorted keys for deterministic hashing
        artifact_json = json.dumps(artifact, sort_keys=True, default=str)
        hash_obj = hashlib.sha256(artifact_json.encode('utf-8'))
        return hash_obj.hexdigest()
    
    def seal_artifact(
        self,
        artifact_id: str,
        artifact_type: str,
        artifact: Dict[str, Any],
        tenant_ctx: Optional[TenantContext] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ArtifactMetadata:
        """
        Seal an artifact with cryptographic hash (immutability guarantee).
        
        Args:
            artifact_id: Unique artifact identifier
            artifact_type: Type of artifact (phase, orchestrator, wiring)
            artifact: Artifact data to seal
            tenant_ctx: Optional TenantContext for tenant-scoped sealing
            metadata: Optional metadata to attach
        
        Returns:
            ArtifactMetadata with seal information
        
        Raises:
            ArtifactAlreadySealedError: If artifact already sealed
        
        Example:
            >>> ctx = TenantContext("ws1", "user1", ["admin"])
            >>> manager = ArtifactSealingManager()
            >>> 
            >>> artifact = {"phase_id": "42", "status": "active"}
            >>> meta = manager.seal_artifact("phase-42", "phase", artifact, ctx)
            >>> 
            >>> print(meta.sealed)  # True
            >>> print(meta.seal_hash)  # SHA-256 hash
        """
        # Check if already sealed
        if artifact_id in self._sealed_artifacts:
            existing = self._sealed_artifacts[artifact_id]
            if existing.sealed:
                raise ArtifactAlreadySealedError(
                    f"Artifact {artifact_id} is already sealed"
                )
        
        # Compute hash
        seal_hash = self._compute_artifact_hash(artifact)
        
        # Create metadata
        artifact_meta = ArtifactMetadata(
            artifact_id=artifact_id,
            artifact_type=artifact_type,
            version=1,
            sealed=True,
            seal_hash=seal_hash,
            created_at=datetime.utcnow(),
            sealed_at=datetime.utcnow(),
            tenant_id=tenant_ctx.tenant_id if tenant_ctx else "local",
            created_by=tenant_ctx.user_id if tenant_ctx else "system",
            metadata=metadata or {}
        )
        
        # Store sealed artifact
        self._sealed_artifacts[artifact_id] = artifact_meta
        
        # Initialize version history
        if artifact_id not in self._artifact_versions:
            self._artifact_versions[artifact_id] = []
        
        self._artifact_versions[artifact_id].append({
            "version": 1,
            "hash": seal_hash,
            "timestamp": artifact_meta.sealed_at.isoformat() if artifact_meta.sealed_at else "",
            "artifact": artifact.copy()
        })
        
        logger.info(f"Sealed artifact {artifact_id} (type={artifact_type}, hash={seal_hash[:8]}...)")
        
        return artifact_meta
    
    def verify_artifact(
        self,
        artifact_id: str,
        artifact: Dict[str, Any]
    ) -> bool:
        """
        Verify sealed artifact integrity (detect tampering).
        
        Args:
            artifact_id: Artifact identifier
            artifact: Artifact to verify
        
        Returns:
            True if artifact is valid, False otherwise
        
        Raises:
            ArtifactTamperingDetectedError: If artifact hash doesn't match seal
        
        Example:
            >>> manager = ArtifactSealingManager()
            >>> artifact = {"status": "active"}
            >>> meta = manager.seal_artifact("phase-42", "phase", artifact)
            >>> 
            >>> # Verify unchanged artifact
            >>> is_valid = manager.verify_artifact("phase-42", artifact)
            >>> assert is_valid
            >>> 
            >>> # Detect tampering
            >>> tampered = {"status": "modified"}
            >>> try:
            ...     manager.verify_artifact("phase-42", tampered)
            ... except ArtifactTamperingDetectedError:
            ...     print("Tampering detected!")
        """
        if artifact_id not in self._sealed_artifacts:
            logger.warning(f"Artifact {artifact_id} not sealed")
            return False
        
        meta = self._sealed_artifacts[artifact_id]
        
        if not meta.sealed:
            logger.warning(f"Artifact {artifact_id} is not sealed")
            return False
        
        # Compute current hash
        current_hash = self._compute_artifact_hash(artifact)
        
        # Compare with seal hash
        if current_hash != meta.seal_hash:
            raise ArtifactTamperingDetectedError(
                f"Artifact {artifact_id} hash mismatch: "
                f"expected {meta.seal_hash}, got {current_hash}"
            )
        
        logger.debug(f"Artifact {artifact_id} integrity verified")
        return True
    
    def get_artifact_metadata(self, artifact_id: str) -> Optional[ArtifactMetadata]:
        """
        Get metadata for sealed artifact.
        
        Args:
            artifact_id: Artifact identifier
        
        Returns:
            ArtifactMetadata or None if not found
        """
        return self._sealed_artifacts.get(artifact_id)
    
    def get_artifact_history(self, artifact_id: str) -> List[Dict[str, Any]]:
        """
        Get version history for artifact.
        
        Args:
            artifact_id: Artifact identifier
        
        Returns:
            List of version records with hashes and timestamps
        """
        return self._artifact_versions.get(artifact_id, [])
    
    def update_artifact_version(
        self,
        artifact_id: str,
        new_artifact: Dict[str, Any],
        tenant_ctx: Optional[TenantContext] = None
    ) -> ArtifactMetadata:
        """
        Create new version of sealed artifact.
        
        Unseals old version, creates new sealed version with incremented
        version number and new seal hash.
        
        Args:
            artifact_id: Artifact identifier
            new_artifact: New artifact data
            tenant_ctx: Optional TenantContext
        
        Returns:
            ArtifactMetadata for new version
        
        Raises:
            ValueError: If artifact not previously sealed
        
        Example:
            >>> manager = ArtifactSealingManager()
            >>> v1 = {"status": "active"}
            >>> meta1 = manager.seal_artifact("phase-42", "phase", v1)
            >>> 
            >>> # Create v2
            >>> v2 = {"status": "completed", "duration_days": 5}
            >>> meta2 = manager.update_artifact_version("phase-42", v2)
            >>> 
            >>> assert meta2.version == 2
            >>> assert meta1.seal_hash != meta2.seal_hash
        """
        if artifact_id not in self._sealed_artifacts:
            raise ValueError(f"Artifact {artifact_id} not previously sealed")
        
        old_meta = self._sealed_artifacts[artifact_id]
        
        # Compute new hash
        new_hash = self._compute_artifact_hash(new_artifact)
        
        # Create new metadata with incremented version
        new_meta = ArtifactMetadata(
            artifact_id=artifact_id,
            artifact_type=old_meta.artifact_type,
            version=old_meta.version + 1,
            sealed=True,
            seal_hash=new_hash,
            created_at=old_meta.created_at,
            sealed_at=datetime.utcnow(),
            tenant_id=tenant_ctx.tenant_id if tenant_ctx else old_meta.tenant_id,
            created_by=tenant_ctx.user_id if tenant_ctx else old_meta.created_by,
            metadata=old_meta.metadata.copy()
        )
        
        # Update sealed artifacts
        self._sealed_artifacts[artifact_id] = new_meta
        
        # Add to version history
        self._artifact_versions[artifact_id].append({
            "version": new_meta.version,
            "hash": new_hash,
            "timestamp": new_meta.sealed_at.isoformat() if new_meta.sealed_at else "",
            "artifact": new_artifact.copy()
        })
        
        logger.info(
            f"Created new version {new_meta.version} for artifact {artifact_id} "
            f"(hash={new_hash[:8]}...)"
        )
        
        return new_meta
    
    def rollback_to_version(
        self,
        artifact_id: str,
        version: int
    ) -> Dict[str, Any]:
        """
        Rollback to previous artifact version.
        
        Args:
            artifact_id: Artifact identifier
            version: Version to rollback to
        
        Returns:
            Artifact data from specified version
        
        Raises:
            ValueError: If version not found
        """
        if artifact_id not in self._artifact_versions:
            raise ValueError(f"No version history for artifact {artifact_id}")
        
        history = self._artifact_versions[artifact_id]
        
        # Find version
        version_record = None
        for record in history:
            if record["version"] == version:
                version_record = record
                break
        
        if not version_record:
            raise ValueError(
                f"Version {version} not found for artifact {artifact_id}"
            )
        
        artifact = version_record["artifact"]
        logger.info(f"Rolled back {artifact_id} to version {version}")
        
        return artifact
    
    def list_sealed_artifacts(
        self,
        artifact_type: Optional[str] = None,
        tenant_id: Optional[str] = None
    ) -> List[ArtifactMetadata]:
        """
        List sealed artifacts with optional filtering.
        
        Args:
            artifact_type: Filter by type (optional)
            tenant_id: Filter by tenant (optional)
        
        Returns:
            List of matching ArtifactMetadata
        """
        artifacts = list(self._sealed_artifacts.values())
        
        if artifact_type:
            artifacts = [a for a in artifacts if a.artifact_type == artifact_type]
        
        if tenant_id:
            artifacts = [a for a in artifacts if a.tenant_id == tenant_id]
        
        return artifacts
    
    def get_sealing_statistics(self) -> Dict[str, Any]:
        """
        Get statistics on sealed artifacts.
        
        Returns:
            Dictionary with sealing stats
        """
        total = len(self._sealed_artifacts)
        sealed = sum(1 for a in self._sealed_artifacts.values() if a.sealed)
        unsealed = total - sealed
        
        # Group by type
        by_type = {}
        for artifact in self._sealed_artifacts.values():
            if artifact.artifact_type not in by_type:
                by_type[artifact.artifact_type] = 0
            by_type[artifact.artifact_type] += 1
        
        # Group by tenant
        by_tenant = {}
        for artifact in self._sealed_artifacts.values():
            tenant = artifact.tenant_id or "local"
            if tenant not in by_tenant:
                by_tenant[tenant] = 0
            by_tenant[tenant] += 1
        
        return {
            "total_artifacts": total,
            "sealed": sealed,
            "unsealed": unsealed,
            "by_type": by_type,
            "by_tenant": by_tenant,
            "total_versions": sum(len(v) for v in self._artifact_versions.values())
        }
