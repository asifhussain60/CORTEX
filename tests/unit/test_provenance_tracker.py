"""
Tests for Provenance Tracker

AC-EXPLAIN-001: Requirement source tracking (where did this requirement come from?)
AC-EXPLAIN-002: Decision justification capture (why was this decision made?)
AC-EXPLAIN-003: Architecture decision rationale (why this architecture?)
AC-EXPLAIN-004: Test coverage justification (why this test coverage?)
AC-EXPLAIN-005: Evidence bundle provenance (what evidence supports this AC-ID?)

Test scenarios:
- Recording requirement sources
- Recording decision justifications
- Recording architecture rationale
- Recording test coverage justification
- Recording evidence provenance
- Generating provenance reports
- Generating traceability matrix
"""

import pytest
from cortex.core.provenance_tracker import (
    ProvenanceTracker,
    ProvenanceType,
    EvidenceType,
    ProvenanceEntry,
    EvidenceBundle,
)


class TestProvenanceTracker:
    """Test suite for ProvenanceTracker."""
    
    @pytest.fixture
    def tracker(self):
        """Create provenance tracker."""
        return ProvenanceTracker()
    
    def test_record_requirement_source(self, tracker):
        """Test recording requirement source."""
        entry = tracker.record_requirement_source(
            entry_id="source-001",
            ac_id="AC-NFR-003-01",
            source_document="cortex-master.yaml",
            source_section="PHASE-04",
            author="architect",
        )
        
        assert entry.id == "source-001"
        assert entry.ac_id == "AC-NFR-003-01"
        assert entry.provenance_type == ProvenanceType.REQUIREMENT_SOURCE
        assert entry.source_document == "cortex-master.yaml"
        assert entry.author == "architect"
    
    def test_get_requirement_source(self, tracker):
        """Test retrieving requirement source."""
        tracker.record_requirement_source(
            entry_id="source-001",
            ac_id="AC-NFR-003-01",
            source_document="cortex-master.yaml",
        )
        
        provenance = tracker.get_provenance_for_ac_id("AC-NFR-003-01")
        assert len(provenance) == 1
        assert provenance[0].provenance_type == ProvenanceType.REQUIREMENT_SOURCE
    
    def test_get_ac_id_sources(self, tracker):
        """Test getting source documents for AC-ID."""
        tracker.record_requirement_source(
            entry_id="source-001",
            ac_id="AC-NFR-003-01",
            source_document="cortex-master.yaml",
        )
        tracker.record_requirement_source(
            entry_id="source-002",
            ac_id="AC-NFR-003-01",
            source_document="design-doc.md",
        )
        
        sources = tracker.get_ac_id_sources("AC-NFR-003-01")
        assert "cortex-master.yaml" in sources
        assert "design-doc.md" in sources
    
    def test_record_decision_justification(self, tracker):
        """Test recording decision justification."""
        entry = tracker.record_decision_justification(
            entry_id="decision-001",
            ac_id="AC-NFR-003-01",
            justification="Secrets redaction prevents exposure of sensitive data",
            related_ac_ids=["AC-NFR-003-02"],
            author="security-lead",
        )
        
        assert entry.provenance_type == ProvenanceType.DECISION_JUSTIFICATION
        assert entry.justification == "Secrets redaction prevents exposure of sensitive data"
        assert "AC-NFR-003-02" in entry.related_ac_ids
    
    def test_record_architecture_rationale(self, tracker):
        """Test recording architecture rationale."""
        entry = tracker.record_architecture_rationale(
            entry_id="arch-001",
            ac_id="AC-AR-001-01",
            rationale="3-tier governance allows policy inheritance and override at appropriate levels",
            related_ac_ids=["AC-AR-001-02", "AC-AR-001-03"],
            author="architect",
        )
        
        assert entry.provenance_type == ProvenanceType.ARCHITECTURE_RATIONALE
        assert "3-tier governance" in entry.rationale
        assert len(entry.related_ac_ids) == 2
    
    def test_record_test_coverage_justification(self, tracker):
        """Test recording test coverage justification."""
        entry = tracker.record_test_coverage_justification(
            entry_id="test-001",
            ac_id="AC-NFR-003-01",
            justification="21 unit tests provide 95% code coverage",
            test_names=["test_redact_aws_key", "test_redact_password", "test_redact_jwt"],
            coverage_percentage=95.0,
            author="test-engineer",
        )
        
        assert entry.provenance_type == ProvenanceType.TEST_COVERAGE_JUSTIFICATION
        assert entry.metadata['coverage_percentage'] == 95.0
        assert len(entry.metadata['test_names']) == 3
    
    def test_record_evidence_provenance(self, tracker):
        """Test recording evidence provenance."""
        bundle = tracker.record_evidence_provenance(
            entry_id="evidence-001",
            ac_id="AC-NFR-003-01",
            evidence_refs=["test-result-001", "code-review-001"],
            description="All secret redaction tests passing",
            author="ci-system",
        )
        
        assert bundle.bundle_id == "evidence-001"
        assert bundle.ac_id == "AC-NFR-003-01"
        assert bundle.created_by == "ci-system"
    
    def test_get_evidence_for_ac_id(self, tracker):
        """Test retrieving evidence for AC-ID."""
        tracker.record_evidence_provenance(
            entry_id="evidence-001",
            ac_id="AC-NFR-003-01",
            evidence_refs=["test-result-001"],
        )
        
        evidence = tracker.get_evidence_for_ac_id("AC-NFR-003-01")
        assert len(evidence) == 1
        assert evidence[0].bundle_id == "evidence-001"
    
    def test_get_provenance_empty(self, tracker):
        """Test retrieving provenance for non-existent AC-ID."""
        provenance = tracker.get_provenance_for_ac_id("AC-NONEXISTENT-001-01")
        assert len(provenance) == 0
    
    def test_generate_provenance_report(self, tracker):
        """Test generating provenance report."""
        tracker.record_requirement_source(
            entry_id="source-001",
            ac_id="AC-NFR-003-01",
            source_document="cortex-master.yaml",
        )
        tracker.record_decision_justification(
            entry_id="decision-001",
            ac_id="AC-NFR-003-01",
            justification="Secrets redaction is critical",
        )
        tracker.record_evidence_provenance(
            entry_id="evidence-001",
            ac_id="AC-NFR-003-01",
            evidence_refs=["test-result-001"],
        )
        
        report = tracker.generate_provenance_report("AC-NFR-003-01")
        
        assert report['ac_id'] == "AC-NFR-003-01"
        assert report['provenance_entries'] >= 2
        assert report['evidence_bundles'] >= 1
        assert 'cortex-master.yaml' in report['source_documents']
    
    def test_provenance_entry_to_dict(self, tracker):
        """Test provenance entry serialization."""
        entry = tracker.record_requirement_source(
            entry_id="source-001",
            ac_id="AC-NFR-003-01",
            source_document="cortex-master.yaml",
        )
        
        entry_dict = entry.to_dict()
        assert entry_dict['id'] == "source-001"
        assert entry_dict['ac_id'] == "AC-NFR-003-01"
        assert entry_dict['provenance_type'] == "REQUIREMENT_SOURCE"
    
    def test_evidence_bundle_to_dict(self, tracker):
        """Test evidence bundle serialization."""
        bundle = tracker.record_evidence_provenance(
            entry_id="evidence-001",
            ac_id="AC-NFR-003-01",
            evidence_refs=["test-001"],
            description="Test evidence",
        )
        
        bundle_dict = bundle.to_dict()
        assert bundle_dict['bundle_id'] == "evidence-001"
        assert bundle_dict['ac_id'] == "AC-NFR-003-01"
        assert bundle_dict['description'] == "Test evidence"
    
    def test_generate_traceability_matrix(self, tracker):
        """Test generating traceability matrix."""
        ac_ids = ["AC-NFR-003-01", "AC-NFR-003-02"]
        
        # Add provenance for first AC-ID
        tracker.record_requirement_source(
            entry_id="source-001",
            ac_id="AC-NFR-003-01",
            source_document="cortex-master.yaml",
        )
        tracker.record_evidence_provenance(
            entry_id="evidence-001",
            ac_id="AC-NFR-003-01",
            evidence_refs=["test-001"],
        )
        
        # Add provenance for second AC-ID
        tracker.record_requirement_source(
            entry_id="source-002",
            ac_id="AC-NFR-003-02",
            source_document="cortex-master.yaml",
        )
        
        matrix = tracker.generate_traceability_matrix(ac_ids)
        
        assert matrix['total_ac_ids'] == 2
        assert 'AC-NFR-003-01' in matrix['traceability_matrix']
        assert matrix['traceability_matrix']['AC-NFR-003-01']['has_source'] is True
        assert matrix['traceability_matrix']['AC-NFR-003-01']['has_evidence'] is True
    
    def test_multiple_provenance_entries_per_ac_id(self, tracker):
        """Test multiple provenance entries for same AC-ID."""
        tracker.record_requirement_source(
            entry_id="source-001",
            ac_id="AC-NFR-003-01",
            source_document="cortex-master.yaml",
        )
        tracker.record_decision_justification(
            entry_id="decision-001",
            ac_id="AC-NFR-003-01",
            justification="Important for security",
        )
        tracker.record_test_coverage_justification(
            entry_id="test-001",
            ac_id="AC-NFR-003-01",
            justification="95% coverage",
        )
        
        provenance = tracker.get_provenance_for_ac_id("AC-NFR-003-01")
        assert len(provenance) >= 3
        
        types = set(e.provenance_type for e in provenance)
        assert ProvenanceType.REQUIREMENT_SOURCE in types
        assert ProvenanceType.DECISION_JUSTIFICATION in types
        assert ProvenanceType.TEST_COVERAGE_JUSTIFICATION in types
    
    def test_traceability_coverage_calculation(self, tracker):
        """Test traceability coverage percentage calculation."""
        ac_ids = [
            "AC-NFR-003-01",
            "AC-NFR-003-02",
            "AC-NFR-003-03",
        ]
        
        # Fully trace AC-001 and AC-002
        for ac_id in ["AC-NFR-003-01", "AC-NFR-003-02"]:
            tracker.record_requirement_source(
                entry_id=f"source-{ac_id}",
                ac_id=ac_id,
                source_document="cortex-master.yaml",
            )
            tracker.record_evidence_provenance(
                entry_id=f"evidence-{ac_id}",
                ac_id=ac_id,
                evidence_refs=["test-result"],
            )
        
        # Only source for AC-003
        tracker.record_requirement_source(
            entry_id="source-AC-NFR-003-03",
            ac_id="AC-NFR-003-03",
            source_document="cortex-master.yaml",
        )
        
        matrix = tracker.generate_traceability_matrix(ac_ids)
        assert matrix['total_ac_ids'] == 3
        assert matrix['fully_traced'] == 2
        assert matrix['coverage_percentage'] == pytest.approx(66.67, rel=1)
    
    def test_related_ac_ids_tracking(self, tracker):
        """Test tracking related AC-IDs."""
        entry = tracker.record_decision_justification(
            entry_id="decision-001",
            ac_id="AC-NFR-003-01",
            justification="Related to hash verification",
            related_ac_ids=["AC-NFR-003-02", "AC-NFR-003-03"],
        )
        
        assert len(entry.related_ac_ids) == 2
        assert "AC-NFR-003-02" in entry.related_ac_ids
        assert "AC-NFR-003-03" in entry.related_ac_ids
    
    def test_provenance_entry_timestamp(self, tracker):
        """Test that provenance entries have timestamps."""
        entry = tracker.record_requirement_source(
            entry_id="source-001",
            ac_id="AC-NFR-003-01",
            source_document="cortex-master.yaml",
        )
        
        assert entry.timestamp is not None
        assert 'T' in entry.timestamp  # ISO format check
