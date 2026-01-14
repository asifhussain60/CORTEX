"""
Provenance Tracker - Requirement Source and Decision Tracking

Requirement traceability with:
- Requirement source tracking (where did this requirement come from?)
- Decision justification capture (why was this decision made?)
- Architecture decision rationale (why this architecture?)
- Test coverage justification (why this test coverage?)
- Evidence bundle provenance (what evidence supports this AC-ID?)

Satisfies: AC-EXPLAIN-001 through AC-EXPLAIN-005

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from src.core.result import Err, Ok, Result


class ProvenanceType(str, Enum):
    """Type of provenance information."""
    
    REQUIREMENT_SOURCE = "REQUIREMENT_SOURCE"
    DECISION_JUSTIFICATION = "DECISION_JUSTIFICATION"
    ARCHITECTURE_RATIONALE = "ARCHITECTURE_RATIONALE"
    TEST_COVERAGE_JUSTIFICATION = "TEST_COVERAGE_JUSTIFICATION"
    EVIDENCE_PROVENANCE = "EVIDENCE_PROVENANCE"


class EvidenceType(str, Enum):
    """Type of evidence."""
    
    TEST_RESULT = "TEST_RESULT"
    CODE_REVIEW = "CODE_REVIEW"
    DESIGN_DOCUMENT = "DESIGN_DOCUMENT"
    AUDIT_LOG = "AUDIT_LOG"
    PERFORMANCE_METRIC = "PERFORMANCE_METRIC"
    SECURITY_SCAN = "SECURITY_SCAN"
    MANUAL_VERIFICATION = "MANUAL_VERIFICATION"


@dataclass
class ProvenanceEntry:
    """Single provenance entry."""
    
    id: str
    ac_id: str
    provenance_type: ProvenanceType
    timestamp: str
    source_document: str  # e.g., "cortex-master.yaml", "design-doc.md"
    source_section: Optional[str] = None
    justification: str = ""
    rationale: Optional[str] = None
    related_ac_ids: List[str] = field(default_factory=list)
    evidence_refs: List[str] = field(default_factory=list)
    author: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'ac_id': self.ac_id,
            'provenance_type': self.provenance_type.value,
            'timestamp': self.timestamp,
            'source_document': self.source_document,
            'source_section': self.source_section,
            'justification': self.justification,
            'rationale': self.rationale,
            'related_ac_ids': self.related_ac_ids,
            'evidence_refs': self.evidence_refs,
            'author': self.author,
            'metadata': self.metadata,
        }


@dataclass
class EvidenceBundle:
    """Collection of evidence supporting an AC-ID."""
    
    bundle_id: str
    ac_id: str
    timestamp: str
    evidence_items: List[Dict[str, Any]] = field(default_factory=list)
    created_by: Optional[str] = None
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'bundle_id': self.bundle_id,
            'ac_id': self.ac_id,
            'timestamp': self.timestamp,
            'evidence_items': self.evidence_items,
            'created_by': self.created_by,
            'description': self.description,
        }


class ProvenanceTracker:
    """
    Track and manage provenance information for requirements.
    
    Maintains complete traceability:
    - Where each requirement came from
    - Why each decision was made
    - What evidence supports each AC-ID
    """
    
    def __init__(self):
        """Initialize provenance tracker."""
        self._provenance_entries: Dict[str, List[ProvenanceEntry]] = {}
        self._evidence_bundles: Dict[str, List[EvidenceBundle]] = {}
        self._ac_id_sources: Dict[str, Set[str]] = {}
    
    def record_requirement_source(
        self,
        entry_id: str,
        ac_id: str,
        source_document: str,
        source_section: Optional[str] = None,
        author: Optional[str] = None,
    ) -> ProvenanceEntry:
        """
        Record the source of a requirement.
        
        Args:
            entry_id: Unique entry ID
            ac_id: AC-ID of requirement
            source_document: Document where requirement originated
            source_section: Section within document
            author: Author who defined requirement
            
        Returns:
            ProvenanceEntry instance
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        
        entry = ProvenanceEntry(
            id=entry_id,
            ac_id=ac_id,
            provenance_type=ProvenanceType.REQUIREMENT_SOURCE,
            timestamp=timestamp,
            source_document=source_document,
            source_section=source_section,
            justification=f"Requirement sourced from {source_document}",
            author=author,
        )
        
        if ac_id not in self._provenance_entries:
            self._provenance_entries[ac_id] = []
        self._provenance_entries[ac_id].append(entry)
        
        # Track source document
        if ac_id not in self._ac_id_sources:
            self._ac_id_sources[ac_id] = set()
        self._ac_id_sources[ac_id].add(source_document)
        
        return entry
    
    def record_decision_justification(
        self,
        entry_id: str,
        ac_id: str,
        justification: str,
        related_ac_ids: Optional[List[str]] = None,
        author: Optional[str] = None,
    ) -> ProvenanceEntry:
        """
        Record why a decision was made.
        
        Args:
            entry_id: Unique entry ID
            ac_id: AC-ID of decision
            justification: Why this decision was made
            related_ac_ids: Other AC-IDs this relates to
            author: Decision maker
            
        Returns:
            ProvenanceEntry instance
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        
        entry = ProvenanceEntry(
            id=entry_id,
            ac_id=ac_id,
            provenance_type=ProvenanceType.DECISION_JUSTIFICATION,
            timestamp=timestamp,
            source_document="decision",
            justification=justification,
            related_ac_ids=related_ac_ids or [],
            author=author,
        )
        
        if ac_id not in self._provenance_entries:
            self._provenance_entries[ac_id] = []
        self._provenance_entries[ac_id].append(entry)
        
        return entry
    
    def record_architecture_rationale(
        self,
        entry_id: str,
        ac_id: str,
        rationale: str,
        related_ac_ids: Optional[List[str]] = None,
        author: Optional[str] = None,
    ) -> ProvenanceEntry:
        """
        Record architecture decision rationale.
        
        Args:
            entry_id: Unique entry ID
            ac_id: AC-ID of architecture decision
            rationale: Why this architecture was chosen
            related_ac_ids: Related AC-IDs
            author: Architect
            
        Returns:
            ProvenanceEntry instance
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        
        entry = ProvenanceEntry(
            id=entry_id,
            ac_id=ac_id,
            provenance_type=ProvenanceType.ARCHITECTURE_RATIONALE,
            timestamp=timestamp,
            source_document="architecture",
            rationale=rationale,
            justification=rationale,
            related_ac_ids=related_ac_ids or [],
            author=author,
        )
        
        if ac_id not in self._provenance_entries:
            self._provenance_entries[ac_id] = []
        self._provenance_entries[ac_id].append(entry)
        
        return entry
    
    def record_test_coverage_justification(
        self,
        entry_id: str,
        ac_id: str,
        justification: str,
        test_names: Optional[List[str]] = None,
        coverage_percentage: Optional[float] = None,
        author: Optional[str] = None,
    ) -> ProvenanceEntry:
        """
        Record why specific test coverage was chosen.
        
        Args:
            entry_id: Unique entry ID
            ac_id: AC-ID being tested
            justification: Why this test coverage was chosen
            test_names: Names of tests that cover this AC-ID
            coverage_percentage: Percentage coverage
            author: Test author
            
        Returns:
            ProvenanceEntry instance
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        
        entry = ProvenanceEntry(
            id=entry_id,
            ac_id=ac_id,
            provenance_type=ProvenanceType.TEST_COVERAGE_JUSTIFICATION,
            timestamp=timestamp,
            source_document="test-suite",
            justification=justification,
            author=author,
            metadata={
                'test_names': test_names or [],
                'coverage_percentage': coverage_percentage,
            }
        )
        
        if ac_id not in self._provenance_entries:
            self._provenance_entries[ac_id] = []
        self._provenance_entries[ac_id].append(entry)
        
        return entry
    
    def record_evidence_provenance(
        self,
        entry_id: str,
        ac_id: str,
        evidence_refs: List[str],
        description: str = "",
        author: Optional[str] = None,
    ) -> EvidenceBundle:
        """
        Record what evidence supports an AC-ID.
        
        Args:
            entry_id: Unique entry ID (bundle ID)
            ac_id: AC-ID being supported
            evidence_refs: List of evidence bundle references
            description: Description of evidence
            author: Who captured evidence
            
        Returns:
            EvidenceBundle instance
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        
        bundle = EvidenceBundle(
            bundle_id=entry_id,
            ac_id=ac_id,
            timestamp=timestamp,
            created_by=author,
            description=description,
        )
        
        if ac_id not in self._evidence_bundles:
            self._evidence_bundles[ac_id] = []
        self._evidence_bundles[ac_id].append(bundle)
        
        # Also record as provenance entry
        self.record_requirement_source(
            entry_id=f"prov-{entry_id}",
            ac_id=ac_id,
            source_document="evidence-bundle",
            source_section=entry_id,
            author=author,
        )
        
        return bundle
    
    def get_provenance_for_ac_id(self, ac_id: str) -> List[ProvenanceEntry]:
        """
        Get all provenance entries for an AC-ID.
        
        Args:
            ac_id: AC-ID to look up
            
        Returns:
            List of provenance entries
        """
        return self._provenance_entries.get(ac_id, [])
    
    def get_evidence_for_ac_id(self, ac_id: str) -> List[EvidenceBundle]:
        """
        Get all evidence bundles for an AC-ID.
        
        Args:
            ac_id: AC-ID to look up
            
        Returns:
            List of evidence bundles
        """
        return self._evidence_bundles.get(ac_id, [])
    
    def get_ac_id_sources(self, ac_id: str) -> Set[str]:
        """
        Get source documents for an AC-ID.
        
        Args:
            ac_id: AC-ID to look up
            
        Returns:
            Set of source documents
        """
        return self._ac_id_sources.get(ac_id, set())
    
    def generate_provenance_report(self, ac_id: str) -> Dict[str, Any]:
        """
        Generate comprehensive provenance report for an AC-ID.
        
        Args:
            ac_id: AC-ID to report on
            
        Returns:
            Report dictionary
        """
        provenance = self.get_provenance_for_ac_id(ac_id)
        evidence = self.get_evidence_for_ac_id(ac_id)
        sources = self.get_ac_id_sources(ac_id)
        
        # Organize by type
        by_type = {}
        for entry in provenance:
            ptype = entry.provenance_type.value
            if ptype not in by_type:
                by_type[ptype] = []
            by_type[ptype].append(entry.to_dict())
        
        return {
            'ac_id': ac_id,
            'report_generated': datetime.now(timezone.utc).isoformat(),
            'source_documents': list(sources),
            'provenance_entries': len(provenance),
            'evidence_bundles': len(evidence),
            'by_type': by_type,
            'provenance_details': [e.to_dict() for e in provenance],
            'evidence_details': [e.to_dict() for e in evidence],
        }
    
    def generate_traceability_matrix(
        self,
        ac_ids: List[str],
    ) -> Dict[str, Any]:
        """
        Generate traceability matrix for AC-IDs.
        
        Args:
            ac_ids: List of AC-IDs
            
        Returns:
            Traceability matrix
        """
        matrix = {}
        
        for ac_id in ac_ids:
            provenance = self.get_provenance_for_ac_id(ac_id)
            evidence = self.get_evidence_for_ac_id(ac_id)
            sources = self.get_ac_id_sources(ac_id)
            
            # Check completeness
            has_source = any(e.provenance_type == ProvenanceType.REQUIREMENT_SOURCE for e in provenance)
            has_justification = any(e.provenance_type == ProvenanceType.DECISION_JUSTIFICATION for e in provenance)
            has_architecture = any(e.provenance_type == ProvenanceType.ARCHITECTURE_RATIONALE for e in provenance)
            has_test_coverage = any(e.provenance_type == ProvenanceType.TEST_COVERAGE_JUSTIFICATION for e in provenance)
            has_evidence = len(evidence) > 0
            
            matrix[ac_id] = {
                'has_source': has_source,
                'has_justification': has_justification,
                'has_architecture': has_architecture,
                'has_test_coverage': has_test_coverage,
                'has_evidence': has_evidence,
                'traceability_complete': all([
                    has_source,
                    has_evidence,
                ]),
                'source_documents': list(sources),
            }
        
        return {
            'traceability_matrix': matrix,
            'total_ac_ids': len(ac_ids),
            'fully_traced': sum(1 for v in matrix.values() if v['traceability_complete']),
            'coverage_percentage': (sum(1 for v in matrix.values() if v['traceability_complete']) / len(ac_ids) * 100) if ac_ids else 0,
        }
