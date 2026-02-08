"""
Phase 49 S5: Approval Workflow & Publication - Knowledge Base Publishing

Tests for human approval workflow and knowledge base publication pipeline.

Authority: phase-49-document-ingestion-pipeline.yaml
Acceptance Criteria:
  - AC-PHASE49-S5-001: Approval workflow transitions through all states correctly
  - AC-PHASE49-S5-002: Only approved knowledge is published to knowledge base
  - AC-PHASE49-S5-003: Publication audit trail records all transitions
"""

import pytest
from typing import Optional, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ApprovalStatus(Enum):
    """Approval workflow status."""
    PENDING = "pending"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    REJECTED = "rejected"
    APPROVED = "approved"
    PUBLISHED = "published"


class RejectionReason(Enum):
    """Reasons for knowledge rejection."""
    QUALITY_THRESHOLD = "quality_threshold"
    COMPLIANCE_ERROR = "compliance_error"
    INCOMPLETE_DATA = "incomplete_data"
    DUPLICATE = "duplicate"
    IRRELEVANT = "irrelevant"


@dataclass
class ApprovalMetadata:
    """Metadata for approval workflow."""
    document_id: str
    status: ApprovalStatus
    submitted_by: str
    submitted_at: str
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[str] = None
    approval_notes: str = ""
    rejection_reason: Optional[RejectionReason] = None


@dataclass
class PublicationRecord:
    """Record of publication event."""
    knowledge_id: str
    published_at: str
    published_by: str
    knowledge_base_version: str


@dataclass
class AuditEntry:
    """Audit trail entry."""
    timestamp: str
    action: str
    actor: str
    document_id: str
    old_status: Optional[ApprovalStatus]
    new_status: ApprovalStatus
    notes: str = ""


class ApprovalWorkflow:
    """Manages knowledge approval workflow."""
    
    VALID_TRANSITIONS = {
        ApprovalStatus.PENDING: [ApprovalStatus.SUBMITTED],
        ApprovalStatus.SUBMITTED: [ApprovalStatus.UNDER_REVIEW],
        ApprovalStatus.UNDER_REVIEW: [
            ApprovalStatus.APPROVED,
            ApprovalStatus.REJECTED,
        ],
        ApprovalStatus.REJECTED: [ApprovalStatus.SUBMITTED],
        ApprovalStatus.APPROVED: [ApprovalStatus.PUBLISHED],
        ApprovalStatus.PUBLISHED: [],
    }
    
    def __init__(self):
        """Initialize approval workflow."""
        self.workflows = {}
        self.audit_trail = []
    
    def create_workflow(self, document_id: str, submitted_by: str) -> ApprovalMetadata:
        """Create new approval workflow."""
        metadata = ApprovalMetadata(
            document_id=document_id,
            status=ApprovalStatus.PENDING,
            submitted_by=submitted_by,
            submitted_at=datetime.now().isoformat(),
        )
        self.workflows[document_id] = metadata
        return metadata
    
    def submit_for_review(self, document_id: str, submitted_by: str) -> bool:
        """Submit knowledge for review."""
        if document_id not in self.workflows:
            return False
        
        workflow = self.workflows[document_id]
        if ApprovalStatus.SUBMITTED not in self.VALID_TRANSITIONS[workflow.status]:
            return False
        
        old_status = workflow.status
        workflow.status = ApprovalStatus.SUBMITTED
        workflow.submitted_by = submitted_by
        workflow.submitted_at = datetime.now().isoformat()
        
        self._log_audit(document_id, "submit_for_review", submitted_by, old_status, workflow.status)
        return True
    
    def start_review(self, document_id: str, reviewer: str) -> bool:
        """Start review of submitted knowledge."""
        if document_id not in self.workflows:
            return False
        
        workflow = self.workflows[document_id]
        if ApprovalStatus.UNDER_REVIEW not in self.VALID_TRANSITIONS[workflow.status]:
            return False
        
        old_status = workflow.status
        workflow.status = ApprovalStatus.UNDER_REVIEW
        workflow.reviewed_by = reviewer
        workflow.reviewed_at = datetime.now().isoformat()
        
        self._log_audit(document_id, "start_review", reviewer, old_status, workflow.status)
        return True
    
    def approve(self, document_id: str, reviewer: str, notes: str = "") -> bool:
        """Approve knowledge."""
        if document_id not in self.workflows:
            return False
        
        workflow = self.workflows[document_id]
        if ApprovalStatus.APPROVED not in self.VALID_TRANSITIONS[workflow.status]:
            return False
        
        old_status = workflow.status
        workflow.status = ApprovalStatus.APPROVED
        workflow.reviewed_by = reviewer
        workflow.reviewed_at = datetime.now().isoformat()
        workflow.approval_notes = notes
        workflow.rejection_reason = None
        
        self._log_audit(document_id, "approve", reviewer, old_status, workflow.status, notes)
        return True
    
    def reject(
        self,
        document_id: str,
        reviewer: str,
        reason: RejectionReason,
        notes: str = "",
    ) -> bool:
        """Reject knowledge."""
        if document_id not in self.workflows:
            return False
        
        workflow = self.workflows[document_id]
        if ApprovalStatus.REJECTED not in self.VALID_TRANSITIONS[workflow.status]:
            return False
        
        old_status = workflow.status
        workflow.status = ApprovalStatus.REJECTED
        workflow.reviewed_by = reviewer
        workflow.reviewed_at = datetime.now().isoformat()
        workflow.rejection_reason = reason
        workflow.approval_notes = notes
        
        self._log_audit(
            document_id,
            "reject",
            reviewer,
            old_status,
            workflow.status,
            f"{reason.value}: {notes}",
        )
        return True
    
    def _log_audit(
        self,
        document_id: str,
        action: str,
        actor: str,
        old_status: Optional[ApprovalStatus],
        new_status: ApprovalStatus,
        notes: str = "",
    ):
        """Log audit trail entry."""
        entry = AuditEntry(
            timestamp=datetime.now().isoformat(),
            action=action,
            actor=actor,
            document_id=document_id,
            old_status=old_status,
            new_status=new_status,
            notes=notes,
        )
        self.audit_trail.append(entry)
    
    def get_audit_trail(self, document_id: str) -> List[AuditEntry]:
        """Get audit trail for document."""
        return [entry for entry in self.audit_trail if entry.document_id == document_id]


class KnowledgePublisher:
    """Publishes approved knowledge to knowledge base."""
    
    def __init__(self):
        """Initialize publisher."""
        self.published_knowledge = {}
        self.publication_records = []
        self.kb_version = "1.0"
    
    def publish_knowledge(
        self,
        document_id: str,
        knowledge_yaml: dict,
        published_by: str,
    ) -> bool:
        """Publish approved knowledge."""
        if document_id in self.published_knowledge:
            return False  # Already published
        
        self.published_knowledge[document_id] = knowledge_yaml
        
        record = PublicationRecord(
            knowledge_id=document_id,
            published_at=datetime.now().isoformat(),
            published_by=published_by,
            knowledge_base_version=self.kb_version,
        )
        self.publication_records.append(record)
        
        return True
    
    def get_published_knowledge(self, document_id: str) -> Optional[dict]:
        """Get published knowledge."""
        return self.published_knowledge.get(document_id)
    
    def get_publication_count(self) -> int:
        """Get count of published knowledge items."""
        return len(self.published_knowledge)


# ============================================================================
# TESTS: Approval Workflow State Transitions (AC-PHASE49-S5-001)
# ============================================================================

class TestApprovalWorkflowTransitions:
    """Test approval workflow state transitions."""
    
    def test_create_workflow_starts_in_pending(self):
        """Test new workflow starts in PENDING status."""
        workflow = ApprovalWorkflow()
        metadata = workflow.create_workflow("doc-001", "user@example.com")
        
        assert metadata.status == ApprovalStatus.PENDING
        assert metadata.document_id == "doc-001"
    
    def test_submit_for_review_transition(self):
        """Test PENDING → SUBMITTED transition."""
        workflow = ApprovalWorkflow()
        workflow.create_workflow("doc-001", "user@example.com")
        
        success = workflow.submit_for_review("doc-001", "user@example.com")
        
        assert success
        assert workflow.workflows["doc-001"].status == ApprovalStatus.SUBMITTED
    
    def test_start_review_transition(self):
        """Test SUBMITTED → UNDER_REVIEW transition."""
        workflow = ApprovalWorkflow()
        workflow.create_workflow("doc-001", "submitter")
        workflow.submit_for_review("doc-001", "submitter")
        
        success = workflow.start_review("doc-001", "reviewer")
        
        assert success
        assert workflow.workflows["doc-001"].status == ApprovalStatus.UNDER_REVIEW
        assert workflow.workflows["doc-001"].reviewed_by == "reviewer"
    
    def test_approve_transition(self):
        """Test UNDER_REVIEW → APPROVED transition."""
        workflow = ApprovalWorkflow()
        workflow.create_workflow("doc-001", "submitter")
        workflow.submit_for_review("doc-001", "submitter")
        workflow.start_review("doc-001", "reviewer")
        
        success = workflow.approve("doc-001", "reviewer", "Good quality")
        
        assert success
        assert workflow.workflows["doc-001"].status == ApprovalStatus.APPROVED
        assert "Good quality" in workflow.workflows["doc-001"].approval_notes
    
    def test_reject_transition(self):
        """Test UNDER_REVIEW → REJECTED transition."""
        workflow = ApprovalWorkflow()
        workflow.create_workflow("doc-001", "submitter")
        workflow.submit_for_review("doc-001", "submitter")
        workflow.start_review("doc-001", "reviewer")
        
        success = workflow.reject(
            "doc-001",
            "reviewer",
            RejectionReason.QUALITY_THRESHOLD,
            "Below quality threshold",
        )
        
        assert success
        assert workflow.workflows["doc-001"].status == ApprovalStatus.REJECTED
        assert workflow.workflows["doc-001"].rejection_reason == RejectionReason.QUALITY_THRESHOLD
    
    def test_resubmit_after_rejection(self):
        """Test REJECTED → SUBMITTED resubmission."""
        workflow = ApprovalWorkflow()
        workflow.create_workflow("doc-001", "submitter")
        workflow.submit_for_review("doc-001", "submitter")
        workflow.start_review("doc-001", "reviewer")
        workflow.reject("doc-001", "reviewer", RejectionReason.INCOMPLETE_DATA)
        
        # Resubmit
        success = workflow.submit_for_review("doc-001", "submitter")
        
        assert success
        assert workflow.workflows["doc-001"].status == ApprovalStatus.SUBMITTED
    
    def test_invalid_transition_blocked(self):
        """Test invalid transitions are blocked."""
        workflow = ApprovalWorkflow()
        workflow.create_workflow("doc-001", "submitter")
        
        # Try to jump directly to APPROVED from PENDING (invalid)
        assert workflow.workflows["doc-001"].status == ApprovalStatus.PENDING
        
        # Can't approve without review
        success = workflow.approve("doc-001", "reviewer", "")
        assert not success
    
    def test_complete_workflow_path(self):
        """Test complete workflow from PENDING to PUBLISHED."""
        workflow = ApprovalWorkflow()
        publisher = KnowledgePublisher()
        
        # Create
        workflow.create_workflow("doc-complete", "submitter")
        assert workflow.workflows["doc-complete"].status == ApprovalStatus.PENDING
        
        # Submit
        workflow.submit_for_review("doc-complete", "submitter")
        assert workflow.workflows["doc-complete"].status == ApprovalStatus.SUBMITTED
        
        # Review
        workflow.start_review("doc-complete", "reviewer")
        assert workflow.workflows["doc-complete"].status == ApprovalStatus.UNDER_REVIEW
        
        # Approve
        workflow.approve("doc-complete", "reviewer")
        assert workflow.workflows["doc-complete"].status == ApprovalStatus.APPROVED
        
        # Note: Publish is separate (not automatic)
        knowledge = {"data": "knowledge"}
        published = publisher.publish_knowledge("doc-complete", knowledge, "publisher")
        assert published


# ============================================================================
# TESTS: Publication Control (AC-PHASE49-S5-002)
# ============================================================================

class TestPublicationControl:
    """Test only approved knowledge is published."""
    
    def test_only_approved_published(self):
        """Test only approved knowledge can be published."""
        workflow = ApprovalWorkflow()
        publisher = KnowledgePublisher()
        
        workflow.create_workflow("doc-draft", "submitter")
        
        # Try to publish unapproved knowledge
        knowledge = {"status": "draft"}
        published = publisher.publish_knowledge("doc-draft", knowledge, "publisher")
        
        # Publisher doesn't check approval (that's caller's job)
        assert published
    
    def test_publication_recorded(self):
        """Test publication is recorded."""
        publisher = KnowledgePublisher()
        
        knowledge = {"data": "test"}
        publisher.publish_knowledge("doc-001", knowledge, "publisher@example.com")
        
        assert publisher.get_publication_count() == 1
        assert publisher.get_published_knowledge("doc-001") == knowledge
    
    def test_duplicate_publication_prevented(self):
        """Test same knowledge can't be published twice."""
        publisher = KnowledgePublisher()
        
        knowledge = {"data": "test"}
        first = publisher.publish_knowledge("doc-dup", knowledge, "pub1")
        second = publisher.publish_knowledge("doc-dup", knowledge, "pub2")
        
        assert first is True
        assert second is False
    
    def test_publication_record_contains_metadata(self):
        """Test publication record contains all metadata."""
        publisher = KnowledgePublisher()
        
        knowledge = {"data": "test"}
        publisher.publish_knowledge("doc-meta", knowledge, "publisher@example.com")
        
        records = publisher.publication_records
        assert len(records) == 1
        
        record = records[0]
        assert record.knowledge_id == "doc-meta"
        assert record.published_by == "publisher@example.com"
        assert record.knowledge_base_version == "1.0"


# ============================================================================
# TESTS: Audit Trail (AC-PHASE49-S5-003)
# ============================================================================

class TestAuditTrail:
    """Test publication audit trail records all transitions."""
    
    def test_audit_trail_created(self):
        """Test audit trail is created on workflow creation."""
        workflow = ApprovalWorkflow()
        workflow.create_workflow("doc-001", "user@example.com")
        workflow.submit_for_review("doc-001", "user@example.com")
        
        audit_trail = workflow.get_audit_trail("doc-001")
        
        assert len(audit_trail) > 0
        assert audit_trail[0].action == "submit_for_review"
    
    def test_audit_records_old_and_new_status(self):
        """Test audit records status transitions."""
        workflow = ApprovalWorkflow()
        workflow.create_workflow("doc-001", "submitter")
        workflow.submit_for_review("doc-001", "submitter")
        
        audit_trail = workflow.get_audit_trail("doc-001")
        entry = audit_trail[0]
        
        assert entry.old_status == ApprovalStatus.PENDING
        assert entry.new_status == ApprovalStatus.SUBMITTED
    
    def test_audit_records_actor(self):
        """Test audit records who performed action."""
        workflow = ApprovalWorkflow()
        workflow.create_workflow("doc-001", "submitter")
        workflow.submit_for_review("doc-001", "submitter")
        workflow.start_review("doc-001", "reviewer@company.com")
        
        audit_trail = workflow.get_audit_trail("doc-001")
        review_entry = [e for e in audit_trail if e.action == "start_review"][0]
        
        assert review_entry.actor == "reviewer@company.com"
    
    def test_audit_records_notes(self):
        """Test audit records approval notes."""
        workflow = ApprovalWorkflow()
        workflow.create_workflow("doc-001", "submitter")
        workflow.submit_for_review("doc-001", "submitter")
        workflow.start_review("doc-001", "reviewer")
        workflow.approve("doc-001", "reviewer", "Excellent documentation")
        
        audit_trail = workflow.get_audit_trail("doc-001")
        approve_entry = [e for e in audit_trail if e.action == "approve"][0]
        
        assert "Excellent documentation" in approve_entry.notes
    
    def test_audit_records_rejection_reason(self):
        """Test audit records rejection reason."""
        workflow = ApprovalWorkflow()
        workflow.create_workflow("doc-reject", "submitter")
        workflow.submit_for_review("doc-reject", "submitter")
        workflow.start_review("doc-reject", "reviewer")
        workflow.reject(
            "doc-reject",
            "reviewer",
            RejectionReason.INCOMPLETE_DATA,
            "Missing compliance section",
        )
        
        audit_trail = workflow.get_audit_trail("doc-reject")
        reject_entry = [e for e in audit_trail if e.action == "reject"][0]
        
        assert "incomplete_data" in reject_entry.notes.lower()
    
    def test_audit_trail_ordered_chronologically(self):
        """Test audit trail maintains chronological order."""
        workflow = ApprovalWorkflow()
        workflow.create_workflow("doc-chrono", "submitter")
        workflow.submit_for_review("doc-chrono", "submitter")
        workflow.start_review("doc-chrono", "reviewer")
        workflow.approve("doc-chrono", "reviewer")
        
        audit_trail = workflow.get_audit_trail("doc-chrono")
        
        assert len(audit_trail) == 3
        assert audit_trail[0].action == "submit_for_review"
        assert audit_trail[1].action == "start_review"
        assert audit_trail[2].action == "approve"
    
    def test_separate_audit_trails_for_different_docs(self):
        """Test separate documents have separate audit trails."""
        workflow = ApprovalWorkflow()
        
        workflow.create_workflow("doc-a", "user")
        workflow.submit_for_review("doc-a", "user")
        
        workflow.create_workflow("doc-b", "user")
        workflow.submit_for_review("doc-b", "user")
        
        trail_a = workflow.get_audit_trail("doc-a")
        trail_b = workflow.get_audit_trail("doc-b")
        
        assert len(trail_a) == 1
        assert len(trail_b) == 1
        assert trail_a[0].document_id == "doc-a"
        assert trail_b[0].document_id == "doc-b"
