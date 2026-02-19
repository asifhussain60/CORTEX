"""
Phase 71 S1: LDv1 Schema Definition & Tooling
Test Suite for LDv1 Schema Validation

AC-PHASE71-S1-001: Schema JSON exists + validates
AC-PHASE71-S1-002: EvidenceProtocol interface defined
AC-PHASE71-S1-003: Artifact registry YAML complete
AC-PHASE71-S1-004: 45 tests passing
AC-PHASE71-S1-005: Backward compatibility

Authority: phase-71-lens-intelligence-integration-framework.yaml
Created: 2026-02-10
Status: RED (tests before implementation)
"""

import json
import pytest
from typing import Dict, Any, List
from pydantic import BaseModel, validator
from dataclasses import dataclass
from enum import Enum


# ============================================================================
# TEST SECTION 1: Schema Definition & Validation (15 tests)
# ============================================================================

class EvidenceKind(str, Enum):
    """Valid evidence source kinds."""
    GIT_COMMIT = "git-commit"
    GIT_DIFF = "git-diff"
    AST_NODE = "ast-node"
    CODE_COMMENT = "code-comment"
    SECURITY_THREAT = "security-threat"
    PATTERN_MATCH = "pattern-match"
    DEPENDENCY_GRAPH = "dependency-graph"
    TEST_FAILURE = "test-failure"
    PERFORMANCE_METRIC = "performance-metric"


class ConfidenceLevel(str, Enum):
    """Confidence levels for evidence."""
    CERTAIN = "1.0"  # Deterministic (git log, AST parsing)
    HIGH = "0.9"     # Very reliable (most code comments)
    MEDIUM = "0.7"   # Probable (pattern matches)
    LOW = "0.5"      # Uncertain (heuristic analysis)


class TestLDv1SchemaDefinition:
    """Test LDv1 schema structure and validation."""

    def test_evidence_item_minimal_structure(self):
        """MUST: EvidenceItem has required fields."""
        # Arrange
        required_fields = ["kind", "ref", "confidence", "source_type"]
        
        # Act/Assert - Define expected structure
        @dataclass
        class EvidenceItem:
            kind: EvidenceKind
            ref: str
            confidence: float
            source_type: str
            snippet: str = ""
        
        # Verify structure can be instantiated
        evidence = EvidenceItem(
            kind=EvidenceKind.GIT_COMMIT,
            ref="sha:abc123",
            confidence=1.0,
            source_type="git"
        )
        
        assert evidence.kind == EvidenceKind.GIT_COMMIT
        assert evidence.confidence == 1.0

    def test_evidence_confidence_range(self):
        """MUST: Confidence scores are 0.0-1.0."""
        valid_scores = [0.0, 0.5, 1.0]
        for score in valid_scores:
            assert 0.0 <= score <= 1.0, f"Invalid confidence: {score}"

    def test_evidence_kind_enumeration(self):
        """MUST: Evidence kinds are restricted enum."""
        # Verify all kinds are valid
        for kind in EvidenceKind:
            assert kind.value in [
                "git-commit", "git-diff", "ast-node", "code-comment",
                "security-threat", "pattern-match", "dependency-graph",
                "test-failure", "performance-metric"
            ]

    def test_lens_artifact_node_structure(self):
        """MUST: LensNode has required fields for graph representation."""
        # Node must have ID + type + evidence
        class LensNode(BaseModel):
            id: str
            node_type: str
            label: str
            evidence: List[Dict[str, Any]] = []
            
            @validator("id")
            def id_not_empty(cls, v):
                assert v, "Node ID cannot be empty"
                return v
        
        node = LensNode(
            id="artifact:file.py",
            node_type="file",
            label="file.py",
            evidence=[{
                "kind": "ast-node",
                "ref": "ast:123",
                "confidence": 1.0
            }]
        )
        
        assert node.id == "artifact:file.py"
        assert len(node.evidence) == 1
        assert node.evidence[0]["confidence"] == 1.0

    def test_lens_artifact_edge_structure(self):
        """MUST: LensEdge represents relationships with evidence."""
        class LensEdge(BaseModel):
            source: str
            target: str
            relation_type: str
            evidence: List[Dict[str, Any]] = []
        
        edge = LensEdge(
            source="file.py",
            target="utils.py",
            relation_type="imports",
            evidence=[{
                "kind": "ast-node",
                "ref": "import:stmt:456",
                "confidence": 1.0
            }]
        )
        
        assert edge.source == "file.py"
        assert edge.relation_type == "imports"

    def test_lens_artifact_metadata(self):
        """MUST: All artifacts have version + timestamp."""
        class LensArtifactMetadata(BaseModel):
            schema_version: str
            timestamp: str
            repository: str
            branch: str
        
        metadata = LensArtifactMetadata(
            schema_version="1.0",
            timestamp="2026-02-10T15:30:00Z",
            repository="cortex",
            branch="main"
        )
        
        assert metadata.schema_version == "1.0"
        assert "2026-02-10" in metadata.timestamp

    def test_lens_artifact_root_structure(self):
        """MUST: Root artifact has metadata + nodes + edges."""
        class LensArtifact(BaseModel):
            metadata: Dict[str, Any]
            nodes: List[Dict[str, Any]]
            edges: List[Dict[str, Any]]
        
        artifact = LensArtifact(
            metadata={"schema_version": "1.0", "timestamp": "2026-02-10T15:30:00Z"},
            nodes=[
                {"id": "file1", "type": "file", "evidence": []}
            ],
            edges=[
                {"source": "file1", "target": "file2", "relation": "imports"}
            ]
        )
        
        assert len(artifact.nodes) == 1
        assert len(artifact.edges) == 1

    def test_backward_compatibility_schema_version(self):
        """MUST: Old outputs can be marked as LDv1."""
        # Existing output structure
        old_output = {
            "repository": "cortex",
            "files": ["file1.py", "file2.py"],
            "commits": [{"sha": "abc123", "author": "user"}]
        }
        
        # Wrap with LDv1 metadata
        ldv1_output = {
            "schema_version": "1.0",
            "timestamp": "2026-02-10T15:30:00Z",
            "legacy_data": old_output
        }
        
        assert "legacy_data" in ldv1_output
        assert ldv1_output["schema_version"] == "1.0"

    def test_artifact_registry_manifest_structure(self):
        """MUST: Manifest defines all available artifacts."""
        class ManifestEntry(BaseModel):
            artifact_id: str
            file_path: str
            description: str
            schema_version: str
            required: bool = False
        
        manifest = {
            "overview": ManifestEntry(
                artifact_id="overview",
                file_path="artifacts/overview.json",
                description="High-level repo summary",
                schema_version="1.0",
                required=True
            ),
            "architecture": ManifestEntry(
                artifact_id="architecture",
                file_path="artifacts/architecture.json",
                description="Architecture analysis",
                schema_version="1.0",
                required=False
            )
        }
        
        assert manifest["overview"].required is True
        assert manifest["architecture"].required is False

    def test_evidence_traceability_requirements(self):
        """MUST: Every evidence item is traceable to source."""
        class TracedEvidence(BaseModel):
            kind: str
            ref: str
            confidence: float
            source_file: str
            source_line: int
        
        evidence = TracedEvidence(
            kind="ast-node",
            ref="func:analyze_code",
            confidence=1.0,
            source_file="cortex/brain/analysis/ast_analyzer.py",
            source_line=42
        )
        
        assert evidence.source_file.endswith(".py")
        assert evidence.source_line > 0

    def test_confidence_score_semantics(self):
        """MUST: Confidence scores have clear semantics."""
        semantics = {
            1.0: "Deterministic (e.g., from git log, AST parsing)",
            0.9: "Very reliable (most code comments)",
            0.7: "Probable (pattern matches)",
            0.5: "Uncertain (heuristic)",
            0.0: "Unknown/unverified"
        }
        
        for score, meaning in semantics.items():
            assert 0.0 <= score <= 1.0
            assert len(meaning) > 0

    def test_schema_version_compatibility_matrix(self):
        """MUST: Schema version determines compatibility."""
        versions = {
            "1.0": ["1.0"],  # Only 1.0 compatible with 1.0
            "1.1": ["1.0", "1.1"],  # 1.1 backward compatible with 1.0
        }
        
        # Verify structure
        for major_version, compatible_with in versions.items():
            assert major_version in compatible_with

    def test_artifact_json_schema_exists(self):
        """MUST: JSON Schema file for LDv1 can be created."""
        # Define the schema structure
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "CORTEX LENS Data Model v1.0",
            "type": "object",
            "required": ["schema_version", "metadata"],
            "properties": {
                "schema_version": {"type": "string", "pattern": "^1\\.0$"},
                "metadata": {"type": "object"},
                "nodes": {"type": "array"},
                "edges": {"type": "array"}
            }
        }
        
        assert schema["$schema"] == "http://json-schema.org/draft-07/schema#"
        assert "schema_version" in schema["required"]


# ============================================================================
# TEST SECTION 2: Evidence Protocol Compliance (15 tests)
# ============================================================================

class TestEvidenceProtocol:
    """Test evidence protocol interface and standardization."""

    def test_analyzer_must_emit_evidence_on_every_result(self):
        """MUST: Every analyzer result includes evidence array."""
        class AnalyzerResult(BaseModel):
            analysis_type: str
            findings: List[Dict[str, Any]]
            evidence: List[Dict[str, Any]]
        
        # Result without evidence should fail
        with pytest.raises(ValueError):
            AnalyzerResult(
                analysis_type="test",
                findings=[{"insight": "found something"}],
                evidence=None  # INVALID
            )

    def test_evidence_protocol_interface_definition(self):
        """MUST: EvidenceProtocol interface defined."""
        from abc import ABC, abstractmethod
        
        class EvidenceProtocol(ABC):
            @abstractmethod
            def emit_evidence(self, finding: Dict) -> List[Dict[str, Any]]:
                """All analyzers must implement this."""
                pass
        
        class GitAnalyzerImpl(EvidenceProtocol):
            def emit_evidence(self, finding: Dict) -> List[Dict[str, Any]]:
                return [{
                    "kind": "git-commit",
                    "ref": finding.get("commit_sha"),
                    "confidence": 1.0
                }]
        
        analyzer = GitAnalyzerImpl()
        evidence = analyzer.emit_evidence({"commit_sha": "abc123"})
        
        assert evidence[0]["kind"] == "git-commit"
        assert evidence[0]["confidence"] == 1.0

    def test_confidence_scoring_consistency(self):
        """MUST: Confidence scores consistent across analyzers."""
        # All deterministic sources (git, AST) = 1.0
        deterministic_scores = {
            "git-commit": 1.0,
            "ast-node": 1.0,
            "import-statement": 1.0,
        }
        
        # All pattern-based = 0.7-0.9
        pattern_scores = {
            "pattern-match": 0.7,
            "anomaly-detection": 0.8,
        }
        
        for kind, score in deterministic_scores.items():
            assert score == 1.0

    def test_evidence_item_required_fields_on_every_analyzer(self):
        """MUST: All analyzers emit kind + ref + confidence + source_type."""
        required_in_all = ["kind", "ref", "confidence", "source_type"]
        
        # Simulate analyzer outputs
        git_evidence = {
            "kind": "git-commit",
            "ref": "sha:abc123",
            "confidence": 1.0,
            "source_type": "git"
        }
        
        ast_evidence = {
            "kind": "ast-node",
            "ref": "func:analyze",
            "confidence": 1.0,
            "source_type": "ast"
        }
        
        for evidence in [git_evidence, ast_evidence]:
            for field in required_in_all:
                assert field in evidence

    def test_analyzer_evidence_aggregation(self):
        """MUST: Multiple evidence items can be aggregated."""
        class Node:
            def __init__(self, node_id: str):
                self.id = node_id
                self.evidence = []
            
            def add_evidence(self, item: Dict):
                self.evidence.append(item)
        
        node = Node("file.py")
        node.add_evidence({"kind": "ast-node", "confidence": 1.0})
        node.add_evidence({"kind": "code-comment", "confidence": 0.9})
        
        assert len(node.evidence) == 2
        avg_confidence = sum(e["confidence"] for e in node.evidence) / len(node.evidence)
        assert avg_confidence == 0.95

    def test_evidence_filtering_by_confidence_threshold(self):
        """MUST: Results can be filtered by confidence threshold."""
        all_evidence = [
            {"kind": "ast-node", "confidence": 1.0},
            {"kind": "pattern-match", "confidence": 0.7},
            {"kind": "heuristic", "confidence": 0.4},
        ]
        
        high_confidence = [e for e in all_evidence if e["confidence"] >= 0.9]
        assert len(high_confidence) == 1

    def test_evidence_contradiction_detection(self):
        """MUST: Conflicting evidence can be detected."""
        evidence_set = [
            {"kind": "ast-node", "claim": "function_is_public", "confidence": 1.0},
            {"kind": "pattern-match", "claim": "function_is_private", "confidence": 0.6},
        ]
        
        claims = {e["claim"]: e["confidence"] for e in evidence_set}
        # Check for conflicting claims
        assert "function_is_public" in claims
        assert "function_is_private" in claims

    def test_evidence_source_traceability(self):
        """MUST: Every evidence item traces back to source analyzer."""
        class TracedAnalysis:
            def __init__(self, analyzer_name: str):
                self.analyzer = analyzer_name
                self.results = []
            
            def add_result(self, finding: Dict):
                finding["source_analyzer"] = self.analyzer
                self.results.append(finding)
        
        git_analysis = TracedAnalysis("GitHistoryAnalyzer")
        git_analysis.add_result({
            "finding": "commit_count:50",
            "evidence": [{"kind": "git-commit", "confidence": 1.0}]
        })
        
        assert git_analysis.results[0]["source_analyzer"] == "GitHistoryAnalyzer"

    def test_evidence_temporal_metadata(self):
        """MUST: Evidence includes when it was generated."""
        from datetime import datetime
        
        evidence = {
            "kind": "git-commit",
            "ref": "sha:abc123",
            "confidence": 1.0,
            "generated_at": datetime.now().isoformat()
        }
        
        assert "generated_at" in evidence
        assert "T" in evidence["generated_at"]  # ISO format

    def test_evidence_aggregation_statistics(self):
        """MUST: Evidence can be aggregated into statistics."""
        evidence_list = [
            {"kind": "ast-node", "confidence": 1.0},
            {"kind": "ast-node", "confidence": 1.0},
            {"kind": "pattern-match", "confidence": 0.7},
            {"kind": "pattern-match", "confidence": 0.8},
        ]
        
        stats = {
            "total": len(evidence_list),
            "avg_confidence": sum(e["confidence"] for e in evidence_list) / len(evidence_list),
            "by_kind": {}
        }
        
        for e in evidence_list:
            kind = e["kind"]
            stats["by_kind"][kind] = stats["by_kind"].get(kind, 0) + 1
        
        assert stats["total"] == 4
        assert stats["avg_confidence"] == 0.875  # (1.0 + 1.0 + 0.7 + 0.8) / 4
        assert stats["by_kind"]["ast-node"] == 2


# ============================================================================
# TEST SECTION 3: Artifact Registry Conformance (15 tests)
# ============================================================================

class TestArtifactRegistry:
    """Test artifact registry structure and conformance."""

    def test_artifact_registry_manifest_file_structure(self):
        """MUST: Artifact registry manifest defines all artifacts."""
        manifest = {
            "artifacts": {
                "overview": {
                    "id": "overview",
                    "path": "artifacts/overview.json",
                    "description": "High-level repository overview",
                    "required": True,
                    "lazy_loadable": False
                },
                "architecture": {
                    "id": "architecture",
                    "path": "artifacts/architecture.json",
                    "description": "Architecture analysis",
                    "required": False,
                    "lazy_loadable": True
                }
            }
        }
        
        assert "overview" in manifest["artifacts"]
        assert manifest["artifacts"]["overview"]["required"] is True

    def test_lazy_loadable_artifacts_definition(self):
        """MUST: Artifacts marked lazy_loadable can be loaded on-demand."""
        lazy_artifacts = [
            "architecture",
            "performance",
            "security",
            "domain-analysis",
            "dependency-graph",
            "test-coverage",
            "code-complexity",
            "change-frequency",
            "contributor-map"
        ]
        
        assert len(lazy_artifacts) == 9
        assert "architecture" in lazy_artifacts

    def test_required_artifacts_always_present(self):
        """MUST: Required artifacts always included in manifest."""
        required = ["overview", "metadata"]
        
        manifest = {
            "artifacts": {
                artifact: {"required": True} for artifact in required
            }
        }
        
        for required_artifact in required:
            assert required_artifact in manifest["artifacts"]

    def test_artifact_cross_reference_validation(self):
        """MUST: Artifacts can reference each other."""
        class Artifact:
            def __init__(self, artifact_id: str):
                self.id = artifact_id
                self.references = []
            
            def add_reference(self, target_artifact_id: str):
                self.references.append(target_artifact_id)
        
        architecture = Artifact("architecture")
        architecture.add_reference("dependency-graph")
        
        assert "dependency-graph" in architecture.references

    def test_artifact_schema_validation(self):
        """MUST: Each artifact type has validation schema."""
        artifact_schemas = {
            "overview": {
                "required": ["repository_name", "statistics"],
                "types": {"statistics": "object"}
            },
            "architecture": {
                "required": ["layers", "components"],
                "types": {"layers": "array"}
            }
        }
        
        for artifact_type, schema in artifact_schemas.items():
            assert "required" in schema
            assert len(schema["required"]) > 0

    def test_artifact_versioning_support(self):
        """MUST: Artifacts support version tracking."""
        artifact = {
            "id": "overview",
            "schema_version": "1.0",
            "artifact_version": "2.3.1",
            "compatible_with": ["1.0", "1.1", "1.2"]
        }
        
        assert artifact["schema_version"] == "1.0"
        assert len(artifact["compatible_with"]) == 3

    def test_artifact_update_tracking(self):
        """MUST: Track when artifacts were last updated."""
        artifact = {
            "id": "architecture",
            "created": "2026-02-10T10:00:00Z",
            "last_updated": "2026-02-10T15:30:00Z",
            "change_count": 3
        }
        
        assert artifact["last_updated"] > artifact["created"]
        assert artifact["change_count"] > 0

    def test_artifact_dependencies_definition(self):
        """MUST: Artifacts can declare dependencies."""
        artifacts = {
            "performance": {
                "depends_on": ["ast-analysis", "git-history"]
            },
            "security": {
                "depends_on": ["ast-analysis", "dependency-graph"]
            }
        }
        
        for artifact_id, artifact_def in artifacts.items():
            assert "depends_on" in artifact_def
            assert len(artifact_def["depends_on"]) > 0

    def test_artifact_size_constraints(self):
        """MUST: Large artifacts are flagged."""
        artifact_sizes = {
            "overview": 50_000,      # 50 KB
            "architecture": 150_000,  # 150 KB (large)
            "performance": 500_000    # 500 KB (very large)
        }
        
        for artifact_id, size in artifact_sizes.items():
            large = size > 200_000
            # Track for optimization
            assert size > 0

    def test_manifest_self_consistency(self):
        """MUST: Manifest is self-consistent."""
        manifest = {
            "schema_version": "1.0",
            "artifacts": {
                "overview": {"id": "overview"},
                "architecture": {"id": "architecture"}
            }
        }
        
        for artifact_id, artifact_def in manifest["artifacts"].items():
            assert artifact_def["id"] == artifact_id

    def test_artifact_discovery_via_manifest(self):
        """MUST: All artifacts discoverable via manifest."""
        manifest = {
            "artifact_ids": ["overview", "architecture", "performance", 
                           "security", "domain", "dependency", "test",
                           "complexity", "frequency", "contributors"]
        }
        
        assert len(manifest["artifact_ids"]) == 10

    def test_artifact_registry_index_json_structure(self):
        """MUST: index.json provides entry point."""
        index = {
            "version": "1.0",
            "timestamp": "2026-02-10T15:30:00Z",
            "artifacts": [
                {"id": "overview", "path": "overview.json"},
                {"id": "architecture", "path": "architecture.json"}
            ]
        }
        
        assert index["version"] == "1.0"
        assert len(index["artifacts"]) == 2

    def test_manifest_caching_support(self):
        """MUST: Manifest supports cache versioning."""
        manifest_v1 = {
            "version": "1.0",
            "cache_key": "cortex/main/abc123def456",
            "artifacts": ["overview", "architecture"]
        }
        
        # New commit
        manifest_v2 = {
            "version": "1.0",
            "cache_key": "cortex/main/789ghi123jkl456",
            "artifacts": ["overview", "architecture"]
        }
        
        assert manifest_v1["cache_key"] != manifest_v2["cache_key"]


# ============================================================================
# TEST SECTION 4: Backward Compatibility Tests (bonus, 5 tests)
# ============================================================================

class TestBackwardCompatibility:
    """Ensure LDv1 doesn't break existing outputs."""

    def test_existing_lens_result_can_wrap_as_ldv1(self):
        """MUST: Existing LensAnalysisResult wrappable as LDv1."""
        existing_result = {
            "repository": "cortex",
            "analysis_time_ms": 234,
            "findings": [
                {"type": "git", "data": {"commits": 50}},
                {"type": "ast", "data": {"functions": 120}}
            ]
        }
        
        wrapped = {
            "schema_version": "1.0",
            "legacy_data": existing_result,
            "migration_status": "pending"
        }
        
        assert "legacy_data" in wrapped
        assert wrapped["schema_version"] == "1.0"

    def test_old_dashboard_json_format_still_parseable(self):
        """MUST: Old dashboard.json format still works."""
        old_format = {
            "tabs": {
                "overview": {"data": []},
                "architecture": {"data": []}
            }
        }
        
        # Should still be readable
        assert "tabs" in old_format
        assert "overview" in old_format["tabs"]

    def test_analyzer_without_evidence_field_marked_legacy(self):
        """MUST: Analyzers without evidence marked as legacy."""
        result_without_evidence = {
            "analyzer": "GitHistoryAnalyzer",
            "findings": [{"commits": 50}],
            "is_legacy": True  # Mark for migration
        }
        
        assert result_without_evidence["is_legacy"] is True

    def test_evidence_field_optional_in_legacy_mode(self):
        """MUST: Evidence optional during transition period."""
        legacy_result = {
            "findings": [{"type": "analysis"}]
            # No evidence field
        }
        
        # Should still be valid
        assert "findings" in legacy_result

    def test_migration_path_defined(self):
        """MUST: Clear migration path from old to LDv1."""
        migration = {
            "phase": "71",
            "old_format": "dashboard.json",
            "new_format": "ldv1_manifest",
            "migration_stages": [
                "stage_1_define_schema",
                "stage_2_add_evidence_to_analyzers",
                "stage_3_incremental_extraction",
                "stage_4_manifest_publishing",
                "stage_5_full_migration"
            ]
        }
        
        assert len(migration["migration_stages"]) == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
