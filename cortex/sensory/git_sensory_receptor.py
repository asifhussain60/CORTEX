"""Sensory Input Layer - Base classes and receptors.

Phase 11 - CMS-1: Sensory Input Layer + Dependency Synapses

This module implements real-time event ingestion from Git webhooks,
with support for GitHub, GitLab, and Bitbucket webhooks.
"""

from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import hashlib
import hmac
import logging
import json


logger = logging.getLogger(__name__)


class EventType(Enum):
    """Types of sensory events."""
    GIT_PUSH = "git_push"
    GIT_PR = "git_pr"
    GIT_MERGE = "git_merge"
    DEPENDENCY_UPDATE = "dependency_update"
    COMPLIANCE_CHANGE = "compliance_change"


class GitPlatform(Enum):
    """Supported Git platforms."""
    GITHUB = "github"
    GITLAB = "gitlab"
    BITBUCKET = "bitbucket"


class DependencyEcosystem(Enum):
    """Supported dependency ecosystems."""
    PYTHON = "python"
    NODEJS = "nodejs"
    GOLANG = "golang"
    JAVA = "java"
    RUST = "rust"
    DOTNET = "dotnet"


@dataclass
class SensoryEvent:
    """Sensory input event from external sources.
    
    Attributes:
        event_id: Unique event identifier (for deduplication)
        timestamp: When event occurred (ISO 8601 format)
        event_type: Type of sensory input
        source: Source system (GitHub, GitLab, Bitbucket)
        repository: Repository name
        branch: Branch name
        data: Event payload
        metadata: Additional context
    """
    event_id: str
    timestamp: str
    event_type: EventType
    source: GitPlatform
    repository: str
    branch: str
    data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self) -> bool:
        """Validate event structure.
        
        Returns:
            True if valid, raises ValueError if invalid
        """
        if not self.event_id:
            raise ValueError("event_id required for deduplication")
        if not self.timestamp:
            raise ValueError("timestamp required")
        if not self.repository:
            raise ValueError("repository required")
        return True


@dataclass
class DependencyData:
    """Dependency information extracted from file.
    
    Attributes:
        package: Package name
        version: Version specification
        ecosystem: Package ecosystem
        license: Package license (optional)
        source: Package source (PyPI, npm, etc.)
    """
    package: str
    version: str
    ecosystem: DependencyEcosystem
    license: Optional[str] = None
    source: Optional[str] = None
    
    def validate(self) -> bool:
        """Validate dependency data.
        
        Returns:
            True if valid
        """
        if not self.package or not self.version:
            raise ValueError("package and version required")
        return True


@dataclass
class SynapticNode:
    """Graph node representing a concept.
    
    Attributes:
        node_id: Unique node identifier
        node_type: Type of node (package, version, cve, etc.)
        label: Human-readable label
        properties: Node properties
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    node_id: str
    node_type: str
    label: str
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class SynapticConnection:
    """Connection between two graph nodes.
    
    Attributes:
        connection_id: Unique connection identifier
        source_node_id: Source node ID
        target_node_id: Target node ID
        relationship_type: Type of relationship
        properties: Connection properties
        created_at: Creation timestamp
    """
    connection_id: str
    source_node_id: str
    target_node_id: str
    relationship_type: str
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class GitWebhookValidator:
    """Validates Git webhook signatures.
    
    Supports:
    - GitHub: SHA256 HMAC
    - GitLab: SHA256 HMAC
    - Bitbucket: SHA256 HMAC
    """
    
    @staticmethod
    def validate_github_signature(payload: str, signature: str, secret: str) -> bool:
        """Validate GitHub webhook signature.
        
        Args:
            payload: Raw request body
            signature: X-Hub-Signature-256 header value
            secret: Webhook secret
            
        Returns:
            True if signature valid
        """
        expected_hash = hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        expected_signature = f"sha256={expected_hash}"
        return hmac.compare_digest(signature, expected_signature)
    
    @staticmethod
    def validate_gitlab_signature(payload: str, signature: str, secret: str) -> bool:
        """Validate GitLab webhook signature.
        
        Args:
            payload: Raw request body
            signature: X-Gitlab-Token header value
            secret: Webhook token
            
        Returns:
            True if signature valid
        """
        return hmac.compare_digest(signature, secret)
    
    @staticmethod
    def validate_bitbucket_signature(payload: str, signature: str, secret: str) -> bool:
        """Validate Bitbucket webhook signature.
        
        Args:
            payload: Raw request body
            signature: X-Hub-Signature header value
            secret: Webhook secret
            
        Returns:
            True if signature valid
        """
        expected_hash = hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(signature, expected_hash)


class GitWebhookParser:
    """Parses Git webhook payloads into SensoryEvent objects."""
    
    @staticmethod
    def parse_github_push(payload: Dict[str, Any]) -> SensoryEvent:
        """Parse GitHub push webhook.
        
        Args:
            payload: GitHub webhook JSON payload
            
        Returns:
            SensoryEvent object
        """
        repo_name = payload["repository"]["name"]
        ref = payload["ref"]  # refs/heads/main
        branch = ref.split("/")[-1]
        
        event_id = f"gh_{repo_name}_{payload['after'][:8]}_{int(datetime.utcnow().timestamp())}"
        
        return SensoryEvent(
            event_id=event_id,
            timestamp=datetime.utcnow().isoformat(),
            event_type=EventType.GIT_PUSH,
            source=GitPlatform.GITHUB,
            repository=repo_name,
            branch=branch,
            data=payload,
            metadata={
                "commits": len(payload.get("commits", [])),
                "pusher": payload.get("pusher", {}).get("name"),
                "commit_sha": payload.get("after"),
            }
        )
    
    @staticmethod
    def parse_gitlab_push(payload: Dict[str, Any]) -> SensoryEvent:
        """Parse GitLab push webhook.
        
        Args:
            payload: GitLab webhook JSON payload
            
        Returns:
            SensoryEvent object
        """
        repo_name = payload["project"]["name"]
        ref = payload["ref"]  # refs/heads/main
        branch = ref.split("/")[-1]
        
        event_id = f"gl_{repo_name}_{payload['after'][:8]}_{int(datetime.utcnow().timestamp())}"
        
        return SensoryEvent(
            event_id=event_id,
            timestamp=datetime.utcnow().isoformat(),
            event_type=EventType.GIT_PUSH,
            source=GitPlatform.GITLAB,
            repository=repo_name,
            branch=branch,
            data=payload,
            metadata={
                "commits": len(payload.get("commits", [])),
                "user_name": payload.get("user_name"),
                "commit_sha": payload.get("after"),
            }
        )
    
    @staticmethod
    def parse_bitbucket_push(payload: Dict[str, Any]) -> SensoryEvent:
        """Parse Bitbucket push webhook.
        
        Args:
            payload: Bitbucket webhook JSON payload
            
        Returns:
            SensoryEvent object
        """
        repo_name = payload["repository"]["name"]
        
        # Bitbucket push has push.changes array
        changes = payload.get("push", {}).get("changes", [])
        new_ref = changes[0].get("new", {}) if changes else {}
        branch = new_ref.get("name", "main")
        commit_sha = new_ref.get("target", {}).get("hash", "unknown")
        
        event_id = f"bb_{repo_name}_{commit_sha[:8]}_{int(datetime.utcnow().timestamp())}"
        
        return SensoryEvent(
            event_id=event_id,
            timestamp=datetime.utcnow().isoformat(),
            event_type=EventType.GIT_PUSH,
            source=GitPlatform.BITBUCKET,
            repository=repo_name,
            branch=branch,
            data=payload,
            metadata={
                "commits": len(changes),
                "commit_sha": commit_sha,
            }
        )


class DependencyFileDetector:
    """Detects and identifies dependency files."""
    
    DEPENDENCY_FILES = {
        # Python
        "requirements.txt": DependencyEcosystem.PYTHON,
        "poetry.lock": DependencyEcosystem.PYTHON,
        "pyproject.toml": DependencyEcosystem.PYTHON,
        "setup.py": DependencyEcosystem.PYTHON,
        "setup.cfg": DependencyEcosystem.PYTHON,
        "Pipfile": DependencyEcosystem.PYTHON,
        "Pipfile.lock": DependencyEcosystem.PYTHON,
        
        # Node.js
        "package.json": DependencyEcosystem.NODEJS,
        "package-lock.json": DependencyEcosystem.NODEJS,
        "yarn.lock": DependencyEcosystem.NODEJS,
        "pnpm-lock.yaml": DependencyEcosystem.NODEJS,
        "npm-shrinkwrap.json": DependencyEcosystem.NODEJS,
        
        # Go
        "go.mod": DependencyEcosystem.GOLANG,
        "go.sum": DependencyEcosystem.GOLANG,
        
        # Java
        "pom.xml": DependencyEcosystem.JAVA,
        "build.gradle": DependencyEcosystem.JAVA,
        "build.gradle.kts": DependencyEcosystem.JAVA,
        
        # Rust
        "Cargo.toml": DependencyEcosystem.RUST,
        "Cargo.lock": DependencyEcosystem.RUST,
        
        # .NET
        "packages.config": DependencyEcosystem.DOTNET,
        ".csproj": DependencyEcosystem.DOTNET,
    }
    
    @staticmethod
    def is_dependency_file(filename: str) -> bool:
        """Check if file is a dependency file.
        
        Args:
            filename: Filename to check
            
        Returns:
            True if dependency file
        """
        for dep_file in DependencyFileDetector.DEPENDENCY_FILES:
            if filename.endswith(dep_file) or filename == dep_file:
                return True
        return False
    
    @staticmethod
    def get_ecosystem(filename: str) -> Optional[DependencyEcosystem]:
        """Get ecosystem for dependency file.
        
        Args:
            filename: Filename
            
        Returns:
            DependencyEcosystem if recognized, None otherwise
        """
        for dep_file, ecosystem in DependencyFileDetector.DEPENDENCY_FILES.items():
            if filename.endswith(dep_file) or filename == dep_file:
                return ecosystem
        return None


if __name__ == "__main__":
    logger.info("Sensory Input Layer - Git Webhook Infrastructure")
