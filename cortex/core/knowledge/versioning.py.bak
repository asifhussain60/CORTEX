"""
Knowledge Versioning Service for managing knowledge backend versions.

Provides version creation, history tracking, current version retrieval,
and rollback functionality with full audit trail support.

Governance:
  - CORE-008: Tests written before code (TDD)
  - CORE-011: 100% type hints on all parameters and returns
  - CORE-012: Google-style docstrings on public APIs
  - CORE-013: Specific exception handling (no bare except)
  - CORE-026: Git checkpoints before major implementations
  - CORE-027: Audit trail logged (AC_START → AC_EXECUTE → AC_COMPLETE)
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid
import logging
import json


logger = logging.getLogger(__name__)


class VersionStatus(Enum):
    """Status of a knowledge version."""
    
    ACTIVE = "active"
    SUPERSEDED = "superseded"
    ROLLED_BACK = "rolled_back"
    ARCHIVED = "archived"


@dataclass
class KnowledgeVersion:
    """Represents a single version of knowledge in a backend."""
    
    version_id: str
    backend_name: str
    data: Dict[str, Any]
    timestamp: datetime
    author: str = "system"
    comment: Optional[str] = None
    status: VersionStatus = VersionStatus.ACTIVE
    parent_version_id: Optional[str] = None
    change_summary: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert version to dictionary representation."""
        return {
            'version_id': self.version_id,
            'backend_name': self.backend_name,
            'timestamp': self.timestamp.isoformat(),
            'author': self.author,
            'comment': self.comment,
            'status': self.status.value,
            'parent_version_id': self.parent_version_id,
            'change_summary': self.change_summary,
            'data_hash': hash(json.dumps(self.data, sort_keys=True)),
        }


class VersionHistory:
    """Manages version history for a single backend."""
    
    def __init__(self, backend_name: str) -> None:
        """Initialize version history for a backend.
        
        Args:
            backend_name: Name of the backend.
        """
        self.backend_name = backend_name
        self.versions: List[KnowledgeVersion] = []
        self.current_version_index: int = -1
    
    def add_version(self, version: KnowledgeVersion) -> str:
        """Add a new version to history.
        
        Args:
            version: KnowledgeVersion to add.
            
        Returns:
            Version ID.
        """
        self.versions.append(version)
        self.current_version_index = len(self.versions) - 1
        logger.info(f"Version {version.version_id} added to {self.backend_name}")
        return version.version_id
    
    def get_current_version(self) -> Optional[KnowledgeVersion]:
        """Get the current active version.
        
        Returns:
            Current KnowledgeVersion or None.
        """
        if self.current_version_index >= 0 and self.current_version_index < len(self.versions):
            return self.versions[self.current_version_index]
        return None
    
    def get_version(self, version_id: str) -> Optional[KnowledgeVersion]:
        """Get a specific version by ID.
        
        Args:
            version_id: ID of version to retrieve.
            
        Returns:
            KnowledgeVersion if found, None otherwise.
        """
        for version in self.versions:
            if version.version_id == version_id:
                return version
        return None
    
    def get_all_versions(self) -> List[KnowledgeVersion]:
        """Get all versions in history.
        
        Returns:
            List of all KnowledgeVersion objects.
        """
        return self.versions.copy()
    
    def rollback_to(self, version_id: str) -> bool:
        """Rollback to a specific version.
        
        Args:
            version_id: ID of version to rollback to.
            
        Returns:
            True if rollback successful, False otherwise.
        """
        for idx, version in enumerate(self.versions):
            if version.version_id == version_id:
                self.current_version_index = idx
                version.status = VersionStatus.ACTIVE
                logger.info(f"Rolled back to version {version_id} in {self.backend_name}")
                return True
        return False


class VersioningService:
    """Service for managing knowledge backend versions.
    
    Provides complete version lifecycle management including creation,
    history tracking, current version retrieval, and rollback with
    full audit trail support.
    """
    
    def __init__(self, backends: Optional[Dict[str, Any]] = None) -> None:
        """Initialize VersioningService.
        
        Args:
            backends: Dictionary of knowledge backends to version.
        """
        self.backends = backends or {}
        self.histories: Dict[str, VersionHistory] = {}
        
        # Initialize history for each backend
        for backend_name in self.backends:
            self.histories[backend_name] = VersionHistory(backend_name)
        
        logger.info(f"VersioningService initialized for {len(self.backends)} backends")
    
    def create_version(
        self,
        backend_name: str,
        data: Dict[str, Any],
        author: str = "system",
        comment: Optional[str] = None,
    ) -> str:
        """Create a new version of knowledge in a backend.
        
        Args:
            backend_name: Name of the backend.
            data: Knowledge data to version.
            author: Author of the version (default: "system").
            comment: Optional comment describing the version.
            
        Returns:
            Version ID of created version.
            
        Raises:
            ValueError: If backend not found.
        """
        if backend_name not in self.backends:
            raise ValueError(f"Backend {backend_name} not found")
        
        history = self.histories[backend_name]
        current = history.get_current_version()
        
        version_id = f"v_{uuid.uuid4().hex[:12]}"
        timestamp = datetime.now()
        
        version = KnowledgeVersion(
            version_id=version_id,
            backend_name=backend_name,
            data=data,
            timestamp=timestamp,
            author=author,
            comment=comment,
            status=VersionStatus.ACTIVE,
            parent_version_id=current.version_id if current else None,
            change_summary=self._generate_change_summary(current, data) if current else "Initial version",
        )
        
        history.add_version(version)
        logger.info(f"Created version {version_id} for {backend_name}")
        return version_id
    
    def get_current_version(self, backend_name: str) -> Optional[KnowledgeVersion]:
        """Get the current active version for a backend.
        
        Args:
            backend_name: Name of the backend.
            
        Returns:
            Current KnowledgeVersion or None.
            
        Raises:
            ValueError: If backend not found.
        """
        if backend_name not in self.backends:
            raise ValueError(f"Backend {backend_name} not found")
        
        history = self.histories[backend_name]
        return history.get_current_version()
    
    def get_version_history(self, backend_name: str) -> List[KnowledgeVersion]:
        """Get complete version history for a backend.
        
        Args:
            backend_name: Name of the backend.
            
        Returns:
            List of KnowledgeVersion objects in order.
            
        Raises:
            ValueError: If backend not found.
        """
        if backend_name not in self.backends:
            raise ValueError(f"Backend {backend_name} not found")
        
        history = self.histories[backend_name]
        return history.get_all_versions()
    
    def get_version(self, backend_name: str, version_id: str) -> Optional[KnowledgeVersion]:
        """Get a specific version by ID.
        
        Args:
            backend_name: Name of the backend.
            version_id: ID of version to retrieve.
            
        Returns:
            KnowledgeVersion if found, None otherwise.
            
        Raises:
            ValueError: If backend not found.
        """
        if backend_name not in self.backends:
            raise ValueError(f"Backend {backend_name} not found")
        
        history = self.histories[backend_name]
        return history.get_version(version_id)
    
    def rollback_to_version(self, backend_name: str, version_id: str) -> bool:
        """Rollback a backend to a specific version.
        
        Args:
            backend_name: Name of the backend.
            version_id: ID of version to rollback to.
            
        Returns:
            True if rollback successful, False otherwise.
        """
        if backend_name not in self.backends:
            logger.error(f"Backend {backend_name} not found")
            return False
        
        history = self.histories[backend_name]
        success = history.rollback_to(version_id)
        
        if success:
            logger.warning(f"Backend {backend_name} rolled back to {version_id}")
            self._log_rollback_audit(backend_name, version_id)
        else:
            logger.error(f"Rollback to {version_id} failed for {backend_name}")
        
        return success
    
    def get_version_diff(
        self,
        backend_name: str,
        version_id_1: str,
        version_id_2: str,
    ) -> Dict[str, Any]:
        """Get differences between two versions.
        
        Args:
            backend_name: Name of the backend.
            version_id_1: First version ID.
            version_id_2: Second version ID.
            
        Returns:
            Dictionary with diff information.
        """
        version1 = self.get_version(backend_name, version_id_1)
        version2 = self.get_version(backend_name, version_id_2)
        
        if not version1 or not version2:
            return {}
        
        return {
            'version_1': version_id_1,
            'version_2': version_id_2,
            'timestamp_1': version1.timestamp,
            'timestamp_2': version2.timestamp,
            'author_1': version1.author,
            'author_2': version2.author,
            'change_summary': version2.change_summary,
        }
    
    def list_versions(self, backend_name: str) -> List[Dict[str, Any]]:
        """List all versions for a backend in human-readable format.
        
        Args:
            backend_name: Name of the backend.
            
        Returns:
            List of version dictionaries.
        """
        if backend_name not in self.backends:
            return []
        
        history = self.histories[backend_name]
        return [v.to_dict() for v in history.get_all_versions()]
    
    def get_version_count(self, backend_name: str) -> int:
        """Get total number of versions for a backend.
        
        Args:
            backend_name: Name of the backend.
            
        Returns:
            Count of versions.
        """
        if backend_name not in self.backends:
            return 0
        
        history = self.histories[backend_name]
        return len(history.get_all_versions())
    
    def prune_old_versions(self, backend_name: str, keep_count: int = 10) -> int:
        """Remove old versions, keeping only the most recent.
        
        Args:
            backend_name: Name of the backend.
            keep_count: Number of recent versions to keep.
            
        Returns:
            Number of versions pruned.
        """
        if backend_name not in self.backends:
            return 0
        
        history = self.histories[backend_name]
        current_count = len(history.versions)
        
        if current_count <= keep_count:
            return 0
        
        removed_count = current_count - keep_count
        history.versions = history.versions[-keep_count:]
        history.current_version_index = len(history.versions) - 1
        
        logger.info(f"Pruned {removed_count} old versions from {backend_name}")
        return removed_count
    
    def _generate_change_summary(
        self,
        previous_version: Optional[KnowledgeVersion],
        new_data: Dict[str, Any],
    ) -> str:
        """Generate a summary of changes between versions.
        
        Args:
            previous_version: Previous KnowledgeVersion or None.
            new_data: New knowledge data.
            
        Returns:
            Summary string describing changes.
        """
        if not previous_version:
            return "Initial version"
        
        prev_keys = set(previous_version.data.keys())
        new_keys = set(new_data.keys())
        
        added_keys = new_keys - prev_keys
        removed_keys = prev_keys - new_keys
        modified_keys = [k for k in prev_keys & new_keys if previous_version.data[k] != new_data[k]]
        
        changes = []
        if added_keys:
            changes.append(f"Added: {len(added_keys)} fields")
        if removed_keys:
            changes.append(f"Removed: {len(removed_keys)} fields")
        if modified_keys:
            changes.append(f"Modified: {len(modified_keys)} fields")
        
        return "; ".join(changes) if changes else "No structural changes"
    
    def _log_rollback_audit(self, backend_name: str, version_id: str) -> None:
        """Log rollback action to audit trail.
        
        Args:
            backend_name: Name of the backend.
            version_id: Version ID of rollback target.
        """
        audit_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': 'rollback',
            'backend': backend_name,
            'target_version': version_id,
            'user': 'system',
        }
        logger.warning(f"Audit: {json.dumps(audit_entry)}")


__all__ = ["KnowledgeVersion", "VersioningService", "VersionStatus", "VersionHistory"]
