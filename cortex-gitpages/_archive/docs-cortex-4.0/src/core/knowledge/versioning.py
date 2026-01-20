"""Knowledge versioning, history tracking, and rollback."""
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime

@dataclass
class KnowledgeVersion:
    """Knowledge version with metadata."""
    version_id: str
    timestamp: datetime
    data: Dict[str, Any]
    author: str = "system"
    comment: str = ""
    changes: Dict[str, Any] = field(default_factory=dict)

class VersioningService:
    """Manages knowledge versioning and history."""

    def __init__(self, backends: Dict[str, Any]):
        """Initialize VersioningService."""
        self.backends = backends
        self.versions: Dict[str, List[KnowledgeVersion]] = {b: [] for b in backends}
        self.current_versions: Dict[str, str] = {}

    def create_version(self, backend: str, data: Dict[str, Any], author: str = "system", comment: str = "") -> str:
        """Create a new version."""
        version_id = f"v_{len(self.versions.get(backend, []))}_{datetime.now().timestamp()}"
        version = KnowledgeVersion(
            version_id=version_id,
            timestamp=datetime.now(),
            data=data,
            author=author,
            comment=comment
        )
        if backend not in self.versions:
            self.versions[backend] = []
        self.versions[backend].append(version)
        self.current_versions[backend] = version_id
        return version_id

    def rollback_to_version(self, backend: str, version_id: str) -> bool:
        """Rollback to previous version."""
        for version in self.versions.get(backend, []):
            if version.version_id == version_id:
                self.current_versions[backend] = version_id
                return True
        return False

    def get_version_history(self, backend: str) -> List[KnowledgeVersion]:
        """Get version history for backend."""
        return self.versions.get(backend, [])

    def get_current_version(self, backend: str) -> Optional[KnowledgeVersion]:
        """Get current version."""
        version_id = self.current_versions.get(backend)
        if version_id:
            for v in self.versions.get(backend, []):
                if v.version_id == version_id:
                    return v
        return None
