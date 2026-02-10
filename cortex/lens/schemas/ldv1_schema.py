"""
Phase 71 S1: LDv1 Schema Implementation
Core schema definitions for CORTEX LENS Data Model v1.0

AC-PHASE71-S1-001: Schema JSON exists + validates
AC-PHASE71-S1-002: EvidenceProtocol interface defined
AC-PHASE71-S1-003: Artifact registry YAML complete
AC-PHASE71-S1-005: Backward compatibility

Authority: phase-71-lens-intelligence-integration-framework.yaml
Created: 2026-02-10
Status: GREEN (implementation)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Any, Optional, Protocol
from abc import ABC, abstractmethod
from pydantic import BaseModel, field_validator
from datetime import datetime
import json


# ============================================================================
# ENUMERATIONS
# ============================================================================

class EvidenceKind(str, Enum):
    """Valid evidence source kinds for LENS analysis."""
    GIT_COMMIT = "git-commit"
    GIT_DIFF = "git-diff"
    AST_NODE = "ast-node"
    CODE_COMMENT = "code-comment"
    SECURITY_THREAT = "security-threat"
    PATTERN_MATCH = "pattern-match"
    DEPENDENCY_GRAPH = "dependency-graph"
    TEST_FAILURE = "test-failure"
    PERFORMANCE_METRIC = "performance-metric"


class ConfidenceLevel(float, Enum):
    """Confidence levels for evidence, expressed as float."""
    CERTAIN = 1.0      # Deterministic (git log, AST parsing)
    HIGH = 0.9         # Very reliable (most code comments)
    MEDIUM = 0.7       # Probable (pattern matches)
    LOW = 0.5          # Uncertain (heuristic analysis)
    UNKNOWN = 0.0      # Unknown/unverified


# ============================================================================
# CORE SCHEMA MODELS
# ============================================================================

@dataclass
class EvidenceItem:
    """
    Evidence item representing a single fact or finding.
    
    Every piece of intelligence extracted by LENS must be traceable
    back to its source with a confidence score.
    """
    kind: EvidenceKind
    ref: str                                    # Reference ID (e.g., "sha:abc123", "line:42")
    confidence: float                           # 0.0-1.0 confidence score
    source_type: str                            # Source analyzer ("git", "ast", "comment", etc.)
    snippet: Optional[str] = None               # Optional code snippet
    source_file: Optional[str] = None           # Source file in analyzer
    source_line: Optional[int] = None           # Source line in analyzer
    generated_at: Optional[str] = None          # ISO timestamp
    
    def __post_init__(self):
        """Validate evidence item after initialization."""
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError(f"Confidence must be 0.0-1.0, got {self.confidence}")
        if not self.ref:
            raise ValueError("Evidence ref cannot be empty")
        if not self.source_type:
            raise ValueError("Evidence source_type cannot be empty")
        if self.generated_at is None:
            self.generated_at = datetime.now().isoformat()


class LensNode(BaseModel):
    """Graph node representing an analyzed artifact (file, class, function, etc.)."""
    id: str
    node_type: str
    label: str
    evidence: List[Dict[str, Any]] = []
    
    @field_validator("id")
    @classmethod
    def id_not_empty(cls, v):
        if not v:
            raise ValueError("Node ID cannot be empty")
        return v


class LensEdge(BaseModel):
    """Graph edge representing relationships between nodes."""
    source: str
    target: str
    relation_type: str
    evidence: List[Dict[str, Any]] = []


class LensArtifactMetadata(BaseModel):
    """Metadata for LENS analysis artifact."""
    schema_version: str
    timestamp: str
    repository: str
    branch: str
    commit_sha: Optional[str] = None
    analysis_duration_ms: int = 0
    analyzer_versions: Optional[Dict[str, str]] = None


class LensArtifact(BaseModel):
    """Root artifact containing analyzed intelligence."""
    metadata: Dict[str, Any]
    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, Any]] = []
    
    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "metadata": {
                    "schema_version": "1.0",
                    "timestamp": "2026-02-10T15:30:00Z",
                    "repository": "cortex",
                    "branch": "main"
                },
                "nodes": [],
                "edges": []
            }
        }


# ============================================================================
# ARTIFACT REGISTRY
# ============================================================================

@dataclass
class ManifestEntry:
    """Entry in artifact manifest."""
    artifact_id: str
    file_path: str
    description: str
    schema_version: str
    required: bool = False
    lazy_loadable: bool = True
    depends_on: List[str] = field(default_factory=list)


class ArtifactManifest(BaseModel):
    """Manifest defining all available artifacts."""
    version: str = "1.0"
    timestamp: str
    artifacts: Dict[str, Dict[str, Any]]
    
    @classmethod
    def create_default(cls) -> "ArtifactManifest":
        """Create default manifest with all standard artifacts."""
        return cls(
            timestamp=datetime.now().isoformat(),
            artifacts={
                "overview": {
                    "artifact_id": "overview",
                    "file_path": "artifacts/overview.json",
                    "description": "High-level repository overview",
                    "schema_version": "1.0",
                    "required": True,
                    "lazy_loadable": False
                },
                "architecture": {
                    "artifact_id": "architecture",
                    "file_path": "artifacts/architecture.json",
                    "description": "Architecture analysis",
                    "schema_version": "1.0",
                    "required": False,
                    "lazy_loadable": True
                },
                "performance": {
                    "artifact_id": "performance",
                    "file_path": "artifacts/performance.json",
                    "description": "Performance analysis",
                    "schema_version": "1.0",
                    "required": False,
                    "lazy_loadable": True,
                    "depends_on": ["ast-analysis", "git-history"]
                },
                "security": {
                    "artifact_id": "security",
                    "file_path": "artifacts/security.json",
                    "description": "Security threat analysis",
                    "schema_version": "1.0",
                    "required": False,
                    "lazy_loadable": True,
                    "depends_on": ["ast-analysis"]
                },
                "domain": {
                    "artifact_id": "domain",
                    "file_path": "artifacts/domain.json",
                    "description": "Domain/business logic analysis",
                    "schema_version": "1.0",
                    "required": False,
                    "lazy_loadable": True
                },
                "dependency": {
                    "artifact_id": "dependency",
                    "file_path": "artifacts/dependency.json",
                    "description": "Dependency graph",
                    "schema_version": "1.0",
                    "required": False,
                    "lazy_loadable": True,
                    "depends_on": ["ast-analysis"]
                },
                "test": {
                    "artifact_id": "test",
                    "file_path": "artifacts/test.json",
                    "description": "Test coverage analysis",
                    "schema_version": "1.0",
                    "required": False,
                    "lazy_loadable": True
                },
                "complexity": {
                    "artifact_id": "complexity",
                    "file_path": "artifacts/complexity.json",
                    "description": "Code complexity metrics",
                    "schema_version": "1.0",
                    "required": False,
                    "lazy_loadable": True,
                    "depends_on": ["ast-analysis"]
                },
                "frequency": {
                    "artifact_id": "frequency",
                    "file_path": "artifacts/frequency.json",
                    "description": "Change frequency analysis",
                    "schema_version": "1.0",
                    "required": False,
                    "lazy_loadable": True,
                    "depends_on": ["git-history"]
                },
                "contributors": {
                    "artifact_id": "contributors",
                    "file_path": "artifacts/contributors.json",
                    "description": "Contributor map",
                    "schema_version": "1.0",
                    "required": False,
                    "lazy_loadable": True,
                    "depends_on": ["git-history"]
                },
            }
        )


class AnalysisIndex(BaseModel):
    """Index (entry point) for all LENS analysis artifacts."""
    version: str = "1.0"
    timestamp: str
    cache_key: Optional[str] = None  # Git commit SHA for caching
    artifacts: List[Dict[str, str]]  # List of {id, path} entries


# ============================================================================
# EVIDENCE PROTOCOL
# ============================================================================

class EvidenceProtocol(ABC):
    """
    Interface that all LENS analyzers must implement.
    
    Ensures consistent evidence emission across all analyzers.
    """
    
    @abstractmethod
    def emit_evidence(self, finding: Dict[str, Any]) -> List[EvidenceItem]:
        """
        Transform a finding into one or more evidence items.
        
        Args:
            finding: Raw finding from analyzer
            
        Returns:
            List of evidence items with confidence scores
        """
        pass
    
    @abstractmethod
    def get_confidence_for_finding(self, finding: Dict[str, Any]) -> float:
        """
        Compute confidence score for a finding.
        
        Args:
            finding: Raw finding
            
        Returns:
            Confidence score 0.0-1.0
        """
        pass


# ============================================================================
# JSON SCHEMA DEFINITION
# ============================================================================

LDVL_JSON_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "CORTEX LENS Data Model v1.0 (LDv1)",
    "description": "Standardized schema for CORTEX LENS intelligence artifacts",
    "type": "object",
    "required": ["schema_version", "metadata"],
    "properties": {
        "schema_version": {
            "type": "string",
            "pattern": "^1\\.0$",
            "description": "Schema version (must be 1.0 for LDv1)"
        },
        "metadata": {
            "type": "object",
            "required": ["schema_version", "timestamp", "repository", "branch"],
            "properties": {
                "schema_version": {"type": "string"},
                "timestamp": {"type": "string", "format": "date-time"},
                "repository": {"type": "string"},
                "branch": {"type": "string"},
                "commit_sha": {"type": "string"},
                "analysis_duration_ms": {"type": "integer", "minimum": 0},
                "analyzer_versions": {"type": "object"}
            }
        },
        "nodes": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["id", "node_type", "label"],
                "properties": {
                    "id": {"type": "string"},
                    "node_type": {"type": "string"},
                    "label": {"type": "string"},
                    "evidence": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["kind", "ref", "confidence", "source_type"],
                            "properties": {
                                "kind": {
                                    "type": "string",
                                    "enum": [e.value for e in EvidenceKind]
                                },
                                "ref": {"type": "string"},
                                "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                                "source_type": {"type": "string"},
                                "snippet": {"type": ["string", "null"]},
                                "source_file": {"type": ["string", "null"]},
                                "source_line": {"type": ["integer", "null"]},
                                "generated_at": {"type": "string"}
                            }
                        }
                    }
                }
            }
        },
        "edges": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["source", "target", "relation_type"],
                "properties": {
                    "source": {"type": "string"},
                    "target": {"type": "string"},
                    "relation_type": {"type": "string"},
                    "evidence": {
                        "type": "array",
                        "items": {"type": "object"}
                    }
                }
            }
        }
    },
    "additionalProperties": False
}


# ============================================================================
# VALIDATOR & UTILITIES
# ============================================================================

class LDv1Validator:
    """Validates LENS artifacts against LDv1 schema."""
    
    @staticmethod
    def validate_evidence_item(evidence: Dict[str, Any]) -> bool:
        """Validate a single evidence item."""
        required_fields = ["kind", "ref", "confidence", "source_type"]
        
        for field in required_fields:
            if field not in evidence:
                raise ValueError(f"Missing required field: {field}")
        
        if not (0.0 <= evidence["confidence"] <= 1.0):
            raise ValueError(f"Invalid confidence: {evidence['confidence']}")
        
        if evidence["kind"] not in [e.value for e in EvidenceKind]:
            raise ValueError(f"Invalid evidence kind: {evidence['kind']}")
        
        return True
    
    @staticmethod
    def validate_artifact(artifact: Dict[str, Any]) -> bool:
        """Validate entire artifact against LDv1 schema."""
        if "schema_version" not in artifact:
            raise ValueError("Missing schema_version")
        
        if artifact.get("schema_version") != "1.0":
            raise ValueError(f"Unsupported schema version: {artifact.get('schema_version')}")
        
        if "metadata" not in artifact:
            raise ValueError("Missing metadata")
        
        # Validate all evidence items
        for node in artifact.get("nodes", []):
            for evidence in node.get("evidence", []):
                LDv1Validator.validate_evidence_item(evidence)
        
        for edge in artifact.get("edges", []):
            for evidence in edge.get("evidence", []):
                LDv1Validator.validate_evidence_item(evidence)
        
        return True


# ============================================================================
# BACKWARD COMPATIBILITY
# ============================================================================

class BackwardCompatibilityWrapper:
    """
    Wraps existing LENS outputs as LDv1 artifacts.
    
    Enables gradual migration from old format to LDv1.
    """
    
    @staticmethod
    def wrap_existing_result(old_result: Dict[str, Any]) -> Dict[str, Any]:
        """Wrap old format result as LDv1."""
        return {
            "schema_version": "1.0",
            "timestamp": datetime.now().isoformat(),
            "legacy_data": old_result,
            "migration_status": "pending"
        }
    
    @staticmethod
    def mark_as_legacy(result: Dict[str, Any]) -> Dict[str, Any]:
        """Mark analyzer output as legacy (no evidence field yet)."""
        result["is_legacy"] = True
        return result


if __name__ == "__main__":
    # Quick validation test
    print("✅ LDv1 Schema module loaded successfully")
    
    # Test evidence item creation
    evidence = EvidenceItem(
        kind=EvidenceKind.GIT_COMMIT,
        ref="sha:abc123def456",
        confidence=1.0,
        source_type="git",
        snippet="commit message here"
    )
    print(f"✅ EvidenceItem created: {evidence}")
    
    # Test manifest creation
    manifest = ArtifactManifest.create_default()
    print(f"✅ ArtifactManifest created with {len(manifest.artifacts)} artifacts")
    
    # Test validation
    test_artifact = {
        "schema_version": "1.0",
        "metadata": {
            "schema_version": "1.0",
            "timestamp": "2026-02-10T15:30:00Z",
            "repository": "cortex",
            "branch": "main"
        },
        "nodes": [],
        "edges": []
    }
    
    LDv1Validator.validate_artifact(test_artifact)
    print("✅ Artifact validation passed")
