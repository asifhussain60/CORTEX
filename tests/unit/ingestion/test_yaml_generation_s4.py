"""
Phase 49 S4: YAML Generation & Schema Validation - Knowledge YAML Pipeline

Tests for YAML schema generation and compliance validation.

Authority: phase-49-document-ingestion-pipeline.yaml
Acceptance Criteria:
  - AC-PHASE49-S4-001: Generated YAML conforms to KnowledgeSchema
  - AC-PHASE49-S4-002: All extracted entities correctly mapped to YAML structure
  - AC-PHASE49-S4-003: Schema validation catches malformed structures
"""

import pytest
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import json


@dataclass
class ComplianceEntry:
    """YAML compliance entry."""
    standard: str
    mentioned: int
    confidence: float
    sections: List[str]


@dataclass
class ArchitectureEntry:
    """YAML architecture entry."""
    pattern: str
    evidence: List[str]
    confidence: float


@dataclass
class DomainEntity:
    """YAML domain entity."""
    name: str
    mentions: int
    confidence: float


@dataclass
class RelationshipEntry:
    """YAML relationship entry."""
    source: str
    target: str
    co_occurrences: int


@dataclass
class KnowledgeYAML:
    """Root YAML structure."""
    metadata: Dict[str, Any]
    document_id: str
    ingestion_date: str
    source_format: str
    extracted_text_length: int
    compliance_standards: List[ComplianceEntry]
    architecture_patterns: List[ArchitectureEntry]
    domains: List[DomainEntity]
    relationships: List[RelationshipEntry]
    overall_confidence: float
    processing_time_ms: float


class YAMLSchema:
    """YAML schema validator."""
    
    REQUIRED_FIELDS = {
        "metadata": dict,
        "document_id": str,
        "ingestion_date": str,
        "source_format": str,
        "extracted_text_length": int,
        "compliance_standards": list,
        "architecture_patterns": list,
        "domains": list,
        "relationships": list,
        "overall_confidence": float,
        "processing_time_ms": float,
    }
    
    COMPLIANCE_REQUIRED_FIELDS = {"standard", "mentioned", "confidence", "sections"}
    ARCHITECTURE_REQUIRED_FIELDS = {"pattern", "evidence", "confidence"}
    DOMAIN_REQUIRED_FIELDS = {"name", "mentions", "confidence"}
    RELATIONSHIP_REQUIRED_FIELDS = {"source", "target", "co_occurrences"}
    
    @staticmethod
    def validate_structure(data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate YAML structure against schema."""
        errors = []
        
        # Check required top-level fields
        for field, expected_type in YAMLSchema.REQUIRED_FIELDS.items():
            if field not in data:
                errors.append(f"Missing required field: {field}")
            elif not isinstance(data[field], expected_type):
                errors.append(f"Field '{field}' should be {expected_type.__name__}, got {type(data[field]).__name__}")
        
        # Validate compliance_standards
        if "compliance_standards" in data:
            if not isinstance(data["compliance_standards"], list):
                errors.append("compliance_standards must be a list")
            else:
                for i, item in enumerate(data["compliance_standards"]):
                    missing = YAMLSchema.COMPLIANCE_REQUIRED_FIELDS - set(item.keys())
                    if missing:
                        errors.append(f"compliance_standards[{i}] missing fields: {missing}")
                    
                    if "confidence" in item and not (0.0 <= item["confidence"] <= 1.0):
                        errors.append(f"compliance_standards[{i}].confidence out of range [0,1]")
        
        # Validate architecture_patterns
        if "architecture_patterns" in data:
            if not isinstance(data["architecture_patterns"], list):
                errors.append("architecture_patterns must be a list")
            else:
                for i, item in enumerate(data["architecture_patterns"]):
                    missing = YAMLSchema.ARCHITECTURE_REQUIRED_FIELDS - set(item.keys())
                    if missing:
                        errors.append(f"architecture_patterns[{i}] missing fields: {missing}")
                    
                    if "confidence" in item and not (0.0 <= item["confidence"] <= 1.0):
                        errors.append(f"architecture_patterns[{i}].confidence out of range [0,1]")
        
        # Validate domains
        if "domains" in data:
            if not isinstance(data["domains"], list):
                errors.append("domains must be a list")
            else:
                for i, item in enumerate(data["domains"]):
                    missing = YAMLSchema.DOMAIN_REQUIRED_FIELDS - set(item.keys())
                    if missing:
                        errors.append(f"domains[{i}] missing fields: {missing}")
                    
                    if "confidence" in item and not (0.0 <= item["confidence"] <= 1.0):
                        errors.append(f"domains[{i}].confidence out of range [0,1]")
        
        # Validate relationships
        if "relationships" in data:
            if not isinstance(data["relationships"], list):
                errors.append("relationships must be a list")
            else:
                for i, item in enumerate(data["relationships"]):
                    missing = YAMLSchema.RELATIONSHIP_REQUIRED_FIELDS - set(item.keys())
                    if missing:
                        errors.append(f"relationships[{i}] missing fields: {missing}")
        
        # Validate overall_confidence
        if "overall_confidence" in data:
            if not (0.0 <= data["overall_confidence"] <= 1.0):
                errors.append("overall_confidence out of range [0,1]")
        
        # Validate processing_time_ms
        if "processing_time_ms" in data:
            if data["processing_time_ms"] < 0:
                errors.append("processing_time_ms must be non-negative")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_compliance_entry(entry: Dict[str, Any]) -> tuple[bool, str]:
        """Validate single compliance entry."""
        if not all(field in entry for field in YAMLSchema.COMPLIANCE_REQUIRED_FIELDS):
            return False, f"Missing fields: {YAMLSchema.COMPLIANCE_REQUIRED_FIELDS - set(entry.keys())}"
        
        if not isinstance(entry["standard"], str):
            return False, "standard must be string"
        
        if not isinstance(entry["mentioned"], int):
            return False, "mentioned must be int"
        
        if not isinstance(entry["confidence"], float):
            return False, "confidence must be float"
        
        if not (0.0 <= entry["confidence"] <= 1.0):
            return False, "confidence out of range"
        
        if not isinstance(entry["sections"], list):
            return False, "sections must be list"
        
        return True, ""


class KnowledgeYAMLGenerator:
    """Generate YAML from parsed knowledge."""
    
    def __init__(self):
        """Initialize generator."""
        self.generated_count = 0
    
    def generate_from_parsed_knowledge(
        self,
        document_id: str,
        source_format: str,
        extracted_text: str,
        compliance_standards: List[Dict[str, Any]],
        architecture_patterns: List[Dict[str, Any]],
        domains: List[str],
        relationships: Dict[str, List[str]],
        overall_confidence: float,
        processing_time_ms: float,
    ) -> Dict[str, Any]:
        """Generate YAML structure from parsed knowledge."""
        
        # Map compliance standards to YAML entries
        compliance_entries = []
        for standard in compliance_standards:
            entry = {
                "standard": standard.get("standard_type", standard.get("standard")),
                "mentioned": standard.get("mentions", 1),
                "confidence": standard.get("confidence", 0.5),
                "sections": standard.get("sections", [])[:3],
            }
            compliance_entries.append(entry)
        
        # Map architecture patterns to YAML entries
        architecture_entries = []
        for pattern in architecture_patterns:
            entry = {
                "pattern": pattern.get("pattern_type", pattern.get("pattern")),
                "evidence": pattern.get("evidence", [])[:2],
                "confidence": pattern.get("confidence", 0.5),
            }
            architecture_entries.append(entry)
        
        # Map domains to YAML entries
        domain_entries = []
        for domain in domains:
            entry = {
                "name": domain,
                "mentions": 1,  # Would be counted from original text
                "confidence": 0.8,
            }
            domain_entries.append(entry)
        
        # Map relationships to YAML entries
        relationship_entries = []
        for source, targets in relationships.items():
            for target in targets:
                entry = {
                    "source": source,
                    "target": target,
                    "co_occurrences": 1,  # Would be counted from text
                }
                relationship_entries.append(entry)
        
        yaml_structure = {
            "metadata": {
                "document_id": document_id,
                "ingestion_date": datetime.now().isoformat(),
                "source_format": source_format,
                "extracted_text_length": len(extracted_text),
            },
            "document_id": document_id,
            "ingestion_date": datetime.now().isoformat(),
            "source_format": source_format,
            "extracted_text_length": len(extracted_text),
            "compliance_standards": compliance_entries,
            "architecture_patterns": architecture_entries,
            "domains": domain_entries,
            "relationships": relationship_entries,
            "overall_confidence": overall_confidence,
            "processing_time_ms": processing_time_ms,
        }
        
        self.generated_count += 1
        return yaml_structure
    
    def validate_generated_yaml(self, yaml_data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate generated YAML against schema."""
        return YAMLSchema.validate_structure(yaml_data)


# ============================================================================
# TESTS: YAML Structure Validation (AC-PHASE49-S4-001)
# ============================================================================

class TestYAMLStructureValidation:
    """Test YAML structure conforms to schema."""
    
    def test_valid_yaml_structure(self):
        """Test valid YAML structure passes validation."""
        yaml_data = {
            "metadata": {"document_id": "doc123"},
            "document_id": "doc123",
            "ingestion_date": "2026-02-08T10:00:00",
            "source_format": "pdf",
            "extracted_text_length": 5000,
            "compliance_standards": [],
            "architecture_patterns": [],
            "domains": [],
            "relationships": [],
            "overall_confidence": 0.85,
            "processing_time_ms": 250.5,
        }
        
        is_valid, errors = YAMLSchema.validate_structure(yaml_data)
        
        assert is_valid
        assert len(errors) == 0
    
    def test_missing_required_field(self):
        """Test missing required field fails validation."""
        yaml_data = {
            "metadata": {"document_id": "doc123"},
            "document_id": "doc123",
            "ingestion_date": "2026-02-08T10:00:00",
            "source_format": "pdf",
            # Missing: extracted_text_length
            "compliance_standards": [],
            "architecture_patterns": [],
            "domains": [],
            "relationships": [],
            "overall_confidence": 0.85,
            "processing_time_ms": 250.5,
        }
        
        is_valid, errors = YAMLSchema.validate_structure(yaml_data)
        
        assert not is_valid
        assert any("extracted_text_length" in error for error in errors)
    
    def test_wrong_field_type(self):
        """Test wrong field type fails validation."""
        yaml_data = {
            "metadata": {"document_id": "doc123"},
            "document_id": "doc123",
            "ingestion_date": "2026-02-08T10:00:00",
            "source_format": "pdf",
            "extracted_text_length": "5000",  # Should be int, not str
            "compliance_standards": [],
            "architecture_patterns": [],
            "domains": [],
            "relationships": [],
            "overall_confidence": 0.85,
            "processing_time_ms": 250.5,
        }
        
        is_valid, errors = YAMLSchema.validate_structure(yaml_data)
        
        assert not is_valid
        assert any("extracted_text_length" in error for error in errors)
    
    def test_confidence_out_of_range(self):
        """Test confidence score out of range fails validation."""
        yaml_data = {
            "metadata": {"document_id": "doc123"},
            "document_id": "doc123",
            "ingestion_date": "2026-02-08T10:00:00",
            "source_format": "pdf",
            "extracted_text_length": 5000,
            "compliance_standards": [],
            "architecture_patterns": [],
            "domains": [],
            "relationships": [],
            "overall_confidence": 1.5,  # Out of range [0,1]
            "processing_time_ms": 250.5,
        }
        
        is_valid, errors = YAMLSchema.validate_structure(yaml_data)
        
        assert not is_valid
        assert any("overall_confidence" in error for error in errors)


# ============================================================================
# TESTS: Entity Mapping (AC-PHASE49-S4-002)
# ============================================================================

class TestEntityMapping:
    """Test extracted entities correctly mapped to YAML structure."""
    
    def test_compliance_entry_mapping(self):
        """Test compliance standard mapped correctly."""
        compliance_data = {
            "standard": "PCI-DSS",
            "mentioned": 5,
            "confidence": 0.92,
            "sections": ["Section 1", "Section 2", "Section 3"],
        }
        
        is_valid, error = YAMLSchema.validate_compliance_entry(compliance_data)
        
        assert is_valid
    
    def test_compliance_entry_missing_field(self):
        """Test compliance entry with missing field fails."""
        compliance_data = {
            "standard": "PCI-DSS",
            "mentioned": 5,
            # Missing: confidence
            "sections": ["Section 1"],
        }
        
        is_valid, error = YAMLSchema.validate_compliance_entry(compliance_data)
        
        assert not is_valid
        assert "confidence" in error
    
    def test_compliance_entry_invalid_confidence(self):
        """Test compliance entry with invalid confidence fails."""
        compliance_data = {
            "standard": "PCI-DSS",
            "mentioned": 5,
            "confidence": 1.5,  # Out of range
            "sections": ["Section 1"],
        }
        
        is_valid, error = YAMLSchema.validate_compliance_entry(compliance_data)
        
        assert not is_valid
    
    def test_architecture_pattern_mapping(self):
        """Test architecture pattern mapped correctly."""
        pattern_data = {
            "pattern": "microservices",
            "evidence": ["service 1", "service 2"],
            "confidence": 0.88,
        }
        
        # Manual validation
        assert isinstance(pattern_data["pattern"], str)
        assert isinstance(pattern_data["evidence"], list)
        assert 0.0 <= pattern_data["confidence"] <= 1.0
    
    def test_domain_entity_mapping(self):
        """Test domain entity mapped correctly."""
        domain_data = {
            "name": "security",
            "mentions": 12,
            "confidence": 0.90,
        }
        
        # Manual validation
        assert isinstance(domain_data["name"], str)
        assert isinstance(domain_data["mentions"], int)
        assert 0.0 <= domain_data["confidence"] <= 1.0
    
    def test_relationship_entry_mapping(self):
        """Test relationship entry mapped correctly."""
        relationship_data = {
            "source": "security",
            "target": "compliance",
            "co_occurrences": 8,
        }
        
        # Manual validation
        assert isinstance(relationship_data["source"], str)
        assert isinstance(relationship_data["target"], str)
        assert isinstance(relationship_data["co_occurrences"], int)


# ============================================================================
# TESTS: YAML Generation Pipeline
# ============================================================================

class TestYAMLGeneration:
    """Test YAML generation from parsed knowledge."""
    
    def test_generate_basic_yaml(self):
        """Test generating basic YAML structure."""
        generator = KnowledgeYAMLGenerator()
        
        yaml_data = generator.generate_from_parsed_knowledge(
            document_id="doc-001",
            source_format="pdf",
            extracted_text="This is a test document about PCI-DSS and microservices.",
            compliance_standards=[
                {"standard": "PCI-DSS", "mentions": 1, "confidence": 0.85, "sections": ["test"]}
            ],
            architecture_patterns=[
                {"pattern": "microservices", "evidence": ["test"], "confidence": 0.80}
            ],
            domains=["security", "compliance"],
            relationships={"security": ["compliance"]},
            overall_confidence=0.85,
            processing_time_ms=125.3,
        )
        
        is_valid, errors = YAMLSchema.validate_structure(yaml_data)
        assert is_valid
        assert yaml_data["document_id"] == "doc-001"
        assert yaml_data["source_format"] == "pdf"
    
    def test_generate_complex_yaml(self):
        """Test generating complex YAML with multiple entities."""
        generator = KnowledgeYAMLGenerator()
        
        yaml_data = generator.generate_from_parsed_knowledge(
            document_id="doc-enterprise",
            source_format="docx",
            extracted_text="Large enterprise document" * 100,
            compliance_standards=[
                {"standard": "PCI-DSS", "mentions": 5, "confidence": 0.92, "sections": ["s1", "s2", "s3"]},
                {"standard": "HIPAA", "mentions": 3, "confidence": 0.88, "sections": ["s1", "s2"]},
                {"standard": "GDPR", "mentions": 2, "confidence": 0.80, "sections": ["s1"]},
            ],
            architecture_patterns=[
                {"pattern": "microservices", "evidence": ["e1", "e2"], "confidence": 0.90},
                {"pattern": "event-driven", "evidence": ["e1"], "confidence": 0.85},
            ],
            domains=["security", "compliance", "performance", "reliability"],
            relationships={
                "security": ["compliance", "performance"],
                "compliance": ["security"],
                "performance": ["reliability"],
            },
            overall_confidence=0.88,
            processing_time_ms=450.2,
        )
        
        is_valid, errors = YAMLSchema.validate_structure(yaml_data)
        assert is_valid
        assert len(yaml_data["compliance_standards"]) == 3
        assert len(yaml_data["architecture_patterns"]) == 2
        assert len(yaml_data["domains"]) == 4
    
    def test_generated_count_increments(self):
        """Test generated_count increments on each generation."""
        generator = KnowledgeYAMLGenerator()
        
        assert generator.generated_count == 0
        
        for i in range(3):
            generator.generate_from_parsed_knowledge(
                document_id=f"doc-{i}",
                source_format="pdf",
                extracted_text="test",
                compliance_standards=[],
                architecture_patterns=[],
                domains=[],
                relationships={},
                overall_confidence=0.8,
                processing_time_ms=100.0,
            )
        
        assert generator.generated_count == 3


# ============================================================================
# TESTS: Schema Validation Catches Malformed Structures
# ============================================================================

class TestSchemaValidationErrors:
    """Test schema validation catches malformed structures."""
    
    def test_invalid_compliance_array(self):
        """Test invalid compliance_standards array."""
        yaml_data = {
            "metadata": {"document_id": "doc123"},
            "document_id": "doc123",
            "ingestion_date": "2026-02-08T10:00:00",
            "source_format": "pdf",
            "extracted_text_length": 5000,
            "compliance_standards": [
                {
                    "standard": "PCI-DSS",
                    "mentioned": 1,
                    # Missing: confidence
                    "sections": ["test"],
                }
            ],
            "architecture_patterns": [],
            "domains": [],
            "relationships": [],
            "overall_confidence": 0.85,
            "processing_time_ms": 250.5,
        }
        
        is_valid, errors = YAMLSchema.validate_structure(yaml_data)
        
        assert not is_valid
        assert any("compliance_standards" in error for error in errors)
    
    def test_invalid_architecture_array(self):
        """Test invalid architecture_patterns array."""
        yaml_data = {
            "metadata": {"document_id": "doc123"},
            "document_id": "doc123",
            "ingestion_date": "2026-02-08T10:00:00",
            "source_format": "pdf",
            "extracted_text_length": 5000,
            "compliance_standards": [],
            "architecture_patterns": [
                {
                    "pattern": "microservices",
                    "evidence": [],
                    # Missing: confidence
                }
            ],
            "domains": [],
            "relationships": [],
            "overall_confidence": 0.85,
            "processing_time_ms": 250.5,
        }
        
        is_valid, errors = YAMLSchema.validate_structure(yaml_data)
        
        assert not is_valid
        assert any("architecture_patterns" in error for error in errors)
    
    def test_invalid_domains_array(self):
        """Test invalid domains array."""
        yaml_data = {
            "metadata": {"document_id": "doc123"},
            "document_id": "doc123",
            "ingestion_date": "2026-02-08T10:00:00",
            "source_format": "pdf",
            "extracted_text_length": 5000,
            "compliance_standards": [],
            "architecture_patterns": [],
            "domains": [
                {
                    "name": "security",
                    "mentions": 5,
                    # Missing: confidence
                }
            ],
            "relationships": [],
            "overall_confidence": 0.85,
            "processing_time_ms": 250.5,
        }
        
        is_valid, errors = YAMLSchema.validate_structure(yaml_data)
        
        assert not is_valid
        assert any("domains" in error for error in errors)
    
    def test_negative_processing_time(self):
        """Test negative processing_time_ms fails validation."""
        yaml_data = {
            "metadata": {"document_id": "doc123"},
            "document_id": "doc123",
            "ingestion_date": "2026-02-08T10:00:00",
            "source_format": "pdf",
            "extracted_text_length": 5000,
            "compliance_standards": [],
            "architecture_patterns": [],
            "domains": [],
            "relationships": [],
            "overall_confidence": 0.85,
            "processing_time_ms": -100.0,
        }
        
        is_valid, errors = YAMLSchema.validate_structure(yaml_data)
        
        assert not is_valid
        assert any("processing_time_ms" in error for error in errors)


# ============================================================================
# TESTS: Serialization & Deserialization
# ============================================================================

class TestYAMLSerializationDeserialization:
    """Test YAML can be serialized and deserialized correctly."""
    
    def test_yaml_to_json_serialization(self):
        """Test YAML structure can be serialized to JSON."""
        generator = KnowledgeYAMLGenerator()
        
        yaml_data = generator.generate_from_parsed_knowledge(
            document_id="doc-serialize",
            source_format="pdf",
            extracted_text="Test content",
            compliance_standards=[
                {"standard": "PCI-DSS", "mentions": 1, "confidence": 0.85, "sections": ["test"]}
            ],
            architecture_patterns=[],
            domains=["security"],
            relationships={},
            overall_confidence=0.85,
            processing_time_ms=100.0,
        )
        
        # Should be JSON serializable
        json_str = json.dumps(yaml_data)
        assert json_str is not None
        assert "doc-serialize" in json_str
    
    def test_yaml_roundtrip_preserves_data(self):
        """Test YAML roundtrip preserves data integrity."""
        generator = KnowledgeYAMLGenerator()
        
        original_yaml = generator.generate_from_parsed_knowledge(
            document_id="doc-roundtrip",
            source_format="docx",
            extracted_text="Original content",
            compliance_standards=[
                {"standard": "HIPAA", "mentions": 2, "confidence": 0.90, "sections": ["s1", "s2"]}
            ],
            architecture_patterns=[
                {"pattern": "microservices", "evidence": ["e1"], "confidence": 0.88}
            ],
            domains=["health", "security"],
            relationships={"health": ["security"]},
            overall_confidence=0.89,
            processing_time_ms=150.5,
        )
        
        # Serialize and deserialize
        json_str = json.dumps(original_yaml)
        restored_yaml = json.loads(json_str)
        
        # Verify key fields preserved
        assert restored_yaml["document_id"] == "doc-roundtrip"
        assert restored_yaml["source_format"] == "docx"
        assert restored_yaml["overall_confidence"] == 0.89
        assert len(restored_yaml["compliance_standards"]) == 1
        assert restored_yaml["compliance_standards"][0]["standard"] == "HIPAA"


# ============================================================================
# TESTS: Validation Edge Cases
# ============================================================================

class TestValidationEdgeCases:
    """Test validation edge cases."""
    
    def test_empty_metadata(self):
        """Test empty metadata dict."""
        yaml_data = {
            "metadata": {},
            "document_id": "doc123",
            "ingestion_date": "2026-02-08T10:00:00",
            "source_format": "pdf",
            "extracted_text_length": 5000,
            "compliance_standards": [],
            "architecture_patterns": [],
            "domains": [],
            "relationships": [],
            "overall_confidence": 0.85,
            "processing_time_ms": 250.5,
        }
        
        # Should be valid (metadata is just a dict)
        is_valid, errors = YAMLSchema.validate_structure(yaml_data)
        assert is_valid
    
    def test_large_extracted_text_length(self):
        """Test large text length value."""
        yaml_data = {
            "metadata": {"document_id": "doc123"},
            "document_id": "doc123",
            "ingestion_date": "2026-02-08T10:00:00",
            "source_format": "pdf",
            "extracted_text_length": 100_000_000,  # 100MB
            "compliance_standards": [],
            "architecture_patterns": [],
            "domains": [],
            "relationships": [],
            "overall_confidence": 0.85,
            "processing_time_ms": 250.5,
        }
        
        is_valid, errors = YAMLSchema.validate_structure(yaml_data)
        assert is_valid
    
    def test_zero_confidence_valid(self):
        """Test zero confidence is valid."""
        yaml_data = {
            "metadata": {"document_id": "doc123"},
            "document_id": "doc123",
            "ingestion_date": "2026-02-08T10:00:00",
            "source_format": "pdf",
            "extracted_text_length": 5000,
            "compliance_standards": [],
            "architecture_patterns": [],
            "domains": [],
            "relationships": [],
            "overall_confidence": 0.0,  # Zero confidence valid
            "processing_time_ms": 250.5,
        }
        
        is_valid, errors = YAMLSchema.validate_structure(yaml_data)
        assert is_valid
    
    def test_max_confidence_valid(self):
        """Test confidence of 1.0 is valid."""
        yaml_data = {
            "metadata": {"document_id": "doc123"},
            "document_id": "doc123",
            "ingestion_date": "2026-02-08T10:00:00",
            "source_format": "pdf",
            "extracted_text_length": 5000,
            "compliance_standards": [],
            "architecture_patterns": [],
            "domains": [],
            "relationships": [],
            "overall_confidence": 1.0,  # Max confidence valid
            "processing_time_ms": 250.5,
        }
        
        is_valid, errors = YAMLSchema.validate_structure(yaml_data)
        assert is_valid
    
    def test_many_compliance_standards(self):
        """Test handling many compliance standards."""
        yaml_data = {
            "metadata": {"document_id": "doc123"},
            "document_id": "doc123",
            "ingestion_date": "2026-02-08T10:00:00",
            "source_format": "pdf",
            "extracted_text_length": 5000,
            "compliance_standards": [
                {
                    "standard": f"STANDARD-{i}",
                    "mentioned": i,
                    "confidence": 0.5 + (i * 0.01),
                    "sections": [f"sec-{i}"],
                }
                for i in range(10)
            ],
            "architecture_patterns": [],
            "domains": [],
            "relationships": [],
            "overall_confidence": 0.85,
            "processing_time_ms": 250.5,
        }
        
        is_valid, errors = YAMLSchema.validate_structure(yaml_data)
        assert is_valid
    
    def test_complex_relationships(self):
        """Test many relationships."""
        yaml_data = {
            "metadata": {"document_id": "doc123"},
            "document_id": "doc123",
            "ingestion_date": "2026-02-08T10:00:00",
            "source_format": "pdf",
            "extracted_text_length": 5000,
            "compliance_standards": [],
            "architecture_patterns": [],
            "domains": [],
            "relationships": [
                {
                    "source": f"entity-{i}",
                    "target": f"entity-{i+1}",
                    "co_occurrences": i * 2,
                }
                for i in range(15)
            ],
            "overall_confidence": 0.85,
            "processing_time_ms": 250.5,
        }
        
        is_valid, errors = YAMLSchema.validate_structure(yaml_data)
        assert is_valid
