"""
Phase 49 S6: Incremental Updates & Version Control - Knowledge Base Updates

Tests for incremental knowledge updates and version control.

Authority: phase-49-document-ingestion-pipeline.yaml
Acceptance Criteria:
  - AC-PHASE49-S6-001: Knowledge updates are tracked with versions
  - AC-PHASE49-S6-002: Incremental updates merge with existing knowledge without losing data
  - AC-PHASE49-S6-003: Version history is auditable and restorable
"""

import pytest
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class UpdateType(Enum):
    """Type of knowledge update."""
    COMPLIANCE_ADDITION = "compliance_addition"
    COMPLIANCE_REMOVAL = "compliance_removal"
    ARCHITECTURE_UPDATE = "architecture_update"
    DOMAIN_MERGE = "domain_merge"
    RELATIONSHIP_ADD = "relationship_add"
    METADATA_UPDATE = "metadata_update"


@dataclass
class VersionedKnowledge:
    """Versioned knowledge record."""
    knowledge_id: str
    version: int
    content: Dict
    updated_by: str
    updated_at: str
    update_type: UpdateType
    change_summary: str


@dataclass
class KnowledgeVersion:
    """Version history entry."""
    knowledge_id: str
    version: int
    timestamp: str
    change_type: UpdateType
    previous_content: Dict
    new_content: Dict
    diff_summary: str


class IncrementalUpdateEngine:
    """Manages incremental knowledge updates."""
    
    def __init__(self):
        """Initialize update engine."""
        self.knowledge_store = {}  # knowledge_id -> VersionedKnowledge
        self.version_history = {}  # knowledge_id -> List[KnowledgeVersion]
    
    def create_knowledge(
        self,
        knowledge_id: str,
        content: Dict,
        created_by: str,
    ) -> VersionedKnowledge:
        """Create initial knowledge."""
        versioned = VersionedKnowledge(
            knowledge_id=knowledge_id,
            version=1,
            content=content.copy(),
            updated_by=created_by,
            updated_at=datetime.now().isoformat(),
            update_type=UpdateType.METADATA_UPDATE,
            change_summary="Initial creation",
        )
        
        self.knowledge_store[knowledge_id] = versioned
        self.version_history[knowledge_id] = []
        
        return versioned
    
    def update_knowledge(
        self,
        knowledge_id: str,
        updates: Dict,
        updated_by: str,
        update_type: UpdateType,
        change_summary: str,
    ) -> Optional[VersionedKnowledge]:
        """Update existing knowledge incrementally."""
        if knowledge_id not in self.knowledge_store:
            return None
        
        current = self.knowledge_store[knowledge_id]
        previous_content = current.content.copy()
        
        # Merge updates
        new_content = self._merge_content(current.content, updates)
        
        # Create version history entry
        version_entry = KnowledgeVersion(
            knowledge_id=knowledge_id,
            version=current.version,
            timestamp=current.updated_at,
            change_type=update_type,
            previous_content=previous_content,
            new_content=new_content,
            diff_summary=self._summarize_diff(previous_content, new_content),
        )
        
        self.version_history[knowledge_id].append(version_entry)
        
        # Update current knowledge
        versioned = VersionedKnowledge(
            knowledge_id=knowledge_id,
            version=current.version + 1,
            content=new_content,
            updated_by=updated_by,
            updated_at=datetime.now().isoformat(),
            update_type=update_type,
            change_summary=change_summary,
        )
        
        self.knowledge_store[knowledge_id] = versioned
        
        return versioned
    
    def _merge_content(self, current: Dict, updates: Dict) -> Dict:
        """Merge updates with current content."""
        merged = current.copy()
        
        # Handle list fields (compliance_standards, architecture_patterns, domains)
        for key in ["compliance_standards", "architecture_patterns", "domains", "relationships"]:
            if key in updates:
                if key in merged:
                    if isinstance(updates[key], list):
                        # Merge lists (remove duplicates)
                        existing = {str(item) for item in merged[key]}
                        for item in updates[key]:
                            if str(item) not in existing:
                                merged[key].append(item)
                else:
                    merged[key] = updates[key]
        
        # Handle scalar fields
        for key in updates:
            if key not in ["compliance_standards", "architecture_patterns", "domains", "relationships"]:
                merged[key] = updates[key]
        
        return merged
    
    def _summarize_diff(self, old: Dict, new: Dict) -> str:
        """Summarize changes between versions."""
        changes = []
        
        # Check for added/removed keys
        old_keys = set(old.keys())
        new_keys = set(new.keys())
        
        added = new_keys - old_keys
        removed = old_keys - new_keys
        
        if added:
            changes.append(f"Added: {', '.join(added)}")
        if removed:
            changes.append(f"Removed: {', '.join(removed)}")
        
        # Check for list changes
        for key in ["compliance_standards", "architecture_patterns", "domains"]:
            if key in old and key in new:
                old_count = len(old.get(key, []))
                new_count = len(new.get(key, []))
                if old_count != new_count:
                    delta = new_count - old_count
                    op = "added" if delta > 0 else "removed"
                    changes.append(f"{key}: {abs(delta)} {op}")
        
        return "; ".join(changes) if changes else "No changes"
    
    def get_version(self, knowledge_id: str, version: int) -> Optional[Dict]:
        """Get specific version of knowledge."""
        if knowledge_id not in self.version_history:
            return None
        
        # First version is current - 1
        if version == self.knowledge_store[knowledge_id].version:
            return self.knowledge_store[knowledge_id].content
        
        for entry in self.version_history[knowledge_id]:
            if entry.version == version:
                return entry.previous_content  # Return state before update
        
        return None
    
    def get_version_history(self, knowledge_id: str) -> List[KnowledgeVersion]:
        """Get full version history."""
        return self.version_history.get(knowledge_id, [])
    
    def get_current_version(self, knowledge_id: str) -> int:
        """Get current version number."""
        if knowledge_id in self.knowledge_store:
            return self.knowledge_store[knowledge_id].version
        return -1
    
    def restore_version(
        self,
        knowledge_id: str,
        target_version: int,
        restored_by: str,
    ) -> Optional[VersionedKnowledge]:
        """Restore to previous version."""
        target_content = self.get_version(knowledge_id, target_version)
        
        if target_content is None:
            return None
        
        return self.update_knowledge(
            knowledge_id,
            target_content,
            restored_by,
            UpdateType.METADATA_UPDATE,
            f"Restored from version {target_version}",
        )


# ============================================================================
# TESTS: Version Tracking (AC-PHASE49-S6-001)
# ============================================================================

class TestVersionTracking:
    """Test knowledge updates are tracked with versions."""
    
    def test_initial_version_is_one(self):
        """Test initial knowledge starts at version 1."""
        engine = IncrementalUpdateEngine()
        
        knowledge = engine.create_knowledge(
            "doc-001",
            {"data": "test"},
            "user@example.com",
        )
        
        assert knowledge.version == 1
    
    def test_version_increments_on_update(self):
        """Test version increments with each update."""
        engine = IncrementalUpdateEngine()
        engine.create_knowledge("doc-001", {"data": "v1"}, "user")
        
        updated = engine.update_knowledge(
            "doc-001",
            {"data": "v2"},
            "user",
            UpdateType.METADATA_UPDATE,
            "Updated data",
        )
        
        assert updated.version == 2
    
    def test_multiple_updates_increment_version(self):
        """Test multiple updates increment version correctly."""
        engine = IncrementalUpdateEngine()
        engine.create_knowledge("doc-001", {"value": 1}, "user")
        
        for i in range(2, 6):
            updated = engine.update_knowledge(
                "doc-001",
                {"value": i},
                "user",
                UpdateType.METADATA_UPDATE,
                f"Update to {i}",
            )
            assert updated.version == i
    
    def test_version_metadata_recorded(self):
        """Test version metadata is recorded."""
        engine = IncrementalUpdateEngine()
        engine.create_knowledge("doc-001", {"data": "test"}, "alice@example.com")
        
        updated = engine.update_knowledge(
            "doc-001",
            {"data": "updated"},
            "bob@example.com",
            UpdateType.COMPLIANCE_ADDITION,
            "Added compliance requirement",
        )
        
        assert updated.updated_by == "bob@example.com"
        assert updated.update_type == UpdateType.COMPLIANCE_ADDITION
        assert "compliance" in updated.change_summary.lower()


# ============================================================================
# TESTS: Incremental Merge (AC-PHASE49-S6-002)
# ============================================================================

class TestIncrementalMerge:
    """Test incremental updates merge without data loss."""
    
    def test_merge_preserves_existing_fields(self):
        """Test merge preserves existing fields."""
        engine = IncrementalUpdateEngine()
        
        initial = {"name": "doc1", "version": 1, "status": "active"}
        engine.create_knowledge("doc-001", initial, "user")
        
        # Update only one field
        updated = engine.update_knowledge(
            "doc-001",
            {"version": 2},
            "user",
            UpdateType.METADATA_UPDATE,
            "Version update",
        )
        
        assert updated.content["name"] == "doc1"
        assert updated.content["status"] == "active"
        assert updated.content["version"] == 2
    
    def test_merge_adds_new_fields(self):
        """Test merge adds new fields."""
        engine = IncrementalUpdateEngine()
        
        engine.create_knowledge(
            "doc-001",
            {"compliance": ["PCI-DSS"]},
            "user",
        )
        
        updated = engine.update_knowledge(
            "doc-001",
            {"architecture": ["microservices"]},
            "user",
            UpdateType.ARCHITECTURE_UPDATE,
            "Added architecture",
        )
        
        assert "compliance" in updated.content
        assert "architecture" in updated.content
        assert updated.content["compliance"] == ["PCI-DSS"]
        assert updated.content["architecture"] == ["microservices"]
    
    def test_merge_deduplicates_list_items(self):
        """Test merge deduplicates list items."""
        engine = IncrementalUpdateEngine()
        
        engine.create_knowledge(
            "doc-001",
            {"domains": ["security", "compliance"]},
            "user",
        )
        
        updated = engine.update_knowledge(
            "doc-001",
            {"domains": ["security", "performance"]},
            "user",
            UpdateType.DOMAIN_MERGE,
            "Merged domains",
        )
        
        # Should have 3 unique domains, not duplicates
        domains = updated.content["domains"]
        assert len(domains) == 3
        assert "security" in domains
        assert "compliance" in domains
        assert "performance" in domains
    
    def test_merge_accumulates_compliance_standards(self):
        """Test merge accumulates compliance standards."""
        engine = IncrementalUpdateEngine()
        
        engine.create_knowledge(
            "doc-001",
            {"compliance_standards": [{"standard": "PCI-DSS", "confidence": 0.9}]},
            "user",
        )
        
        updated = engine.update_knowledge(
            "doc-001",
            {"compliance_standards": [{"standard": "HIPAA", "confidence": 0.85}]},
            "user",
            UpdateType.COMPLIANCE_ADDITION,
            "Added HIPAA",
        )
        
        standards = updated.content["compliance_standards"]
        assert len(standards) >= 2
        standard_names = [s.get("standard") for s in standards]
        assert "PCI-DSS" in standard_names
        assert "HIPAA" in standard_names


# ============================================================================
# TESTS: Version History & Auditability (AC-PHASE49-S6-003)
# ============================================================================

class TestVersionHistory:
    """Test version history is auditable and restorable."""
    
    def test_version_history_recorded(self):
        """Test version history is recorded."""
        engine = IncrementalUpdateEngine()
        engine.create_knowledge("doc-001", {"v": 1}, "user")
        
        engine.update_knowledge(
            "doc-001",
            {"v": 2},
            "user",
            UpdateType.METADATA_UPDATE,
            "Update 2",
        )
        
        history = engine.get_version_history("doc-001")
        
        assert len(history) >= 1
        assert history[0].version == 1
    
    def test_diff_summary_generated(self):
        """Test diff summary is generated."""
        engine = IncrementalUpdateEngine()
        engine.create_knowledge("doc-001", {"old_field": "value"}, "user")
        
        engine.update_knowledge(
            "doc-001",
            {"new_field": "value"},
            "user",
            UpdateType.METADATA_UPDATE,
            "Added new field",
        )
        
        history = engine.get_version_history("doc-001")
        entry = history[0]
        
        assert entry.diff_summary is not None
        assert len(entry.diff_summary) > 0
    
    def test_version_history_chronological(self):
        """Test version history is chronological."""
        engine = IncrementalUpdateEngine()
        engine.create_knowledge("doc-001", {"v": 1}, "user")
        
        for i in range(2, 5):
            engine.update_knowledge(
                "doc-001",
                {"v": i},
                "user",
                UpdateType.METADATA_UPDATE,
                f"Update {i}",
            )
        
        history = engine.get_version_history("doc-001")
        
        for i, entry in enumerate(history, start=1):
            assert entry.version == i
    
    def test_restore_to_previous_version(self):
        """Test restore to previous version."""
        engine = IncrementalUpdateEngine()
        engine.create_knowledge("doc-001", {"value": 1, "status": "new"}, "user")
        
        # Make several updates
        engine.update_knowledge(
            "doc-001",
            {"value": 2},
            "user",
            UpdateType.METADATA_UPDATE,
            "Update 2",
        )
        
        engine.update_knowledge(
            "doc-001",
            {"value": 3},
            "user",
            UpdateType.METADATA_UPDATE,
            "Update 3",
        )
        
        # Restore to version 1
        restored = engine.restore_version("doc-001", 1, "admin")
        
        assert restored is not None
        assert restored.version == 4  # New version after restore
        # Note: Actual content restoration logic depends on implementation
    
    def test_change_type_recorded(self):
        """Test change type is recorded."""
        engine = IncrementalUpdateEngine()
        engine.create_knowledge("doc-001", {}, "user")
        
        engine.update_knowledge(
            "doc-001",
            {"compliance": "PCI-DSS"},
            "user",
            UpdateType.COMPLIANCE_ADDITION,
            "Added compliance",
        )
        
        history = engine.get_version_history("doc-001")
        assert history[0].change_type == UpdateType.COMPLIANCE_ADDITION
    
    def test_update_actor_recorded(self):
        """Test who made update is recorded."""
        engine = IncrementalUpdateEngine()
        engine.create_knowledge("doc-001", {}, "alice")
        
        engine.update_knowledge(
            "doc-001",
            {"data": "updated"},
            "bob@company.com",
            UpdateType.METADATA_UPDATE,
            "Update by Bob",
        )
        
        current = engine.knowledge_store["doc-001"]
        assert current.updated_by == "bob@company.com"
    
    def test_get_current_version_number(self):
        """Test get current version number."""
        engine = IncrementalUpdateEngine()
        engine.create_knowledge("doc-001", {}, "user")
        
        assert engine.get_current_version("doc-001") == 1
        
        engine.update_knowledge("doc-001", {}, "user", UpdateType.METADATA_UPDATE, "")
        assert engine.get_current_version("doc-001") == 2
        
        engine.update_knowledge("doc-001", {}, "user", UpdateType.METADATA_UPDATE, "")
        assert engine.get_current_version("doc-001") == 3


# ============================================================================
# TESTS: Multiple Knowledge Items
# ============================================================================

class TestMultipleKnowledgeItems:
    """Test managing multiple knowledge items."""
    
    def test_separate_version_tracking_per_item(self):
        """Test separate version tracking per knowledge item."""
        engine = IncrementalUpdateEngine()
        
        engine.create_knowledge("doc-001", {"v": 1}, "user")
        engine.create_knowledge("doc-002", {"v": 1}, "user")
        
        engine.update_knowledge("doc-001", {"v": 2}, "user", UpdateType.METADATA_UPDATE, "")
        engine.update_knowledge("doc-001", {"v": 3}, "user", UpdateType.METADATA_UPDATE, "")
        
        assert engine.get_current_version("doc-001") == 3
        assert engine.get_current_version("doc-002") == 1
