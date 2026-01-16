"""
Test suite for Auto-Indexing System (KN-001-02)
================================================
PHASE-12: Knowledge Ecosystem Expansion
AC: KN-001-02 - Auto-Indexing System

Validates:
1. Index built on commit
2. AC-ID → domain mapping maintained
3. Index searchable via API

Specification:
- Automatically index all knowledge entries
- Build AC-ID to domain mapping
- Provide searchable index API
- Maintain index on entry changes
- Support domain-based queries
"""

import os
import json
import pytest
import sqlite3
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict


def get_knowledge_dir() -> Path:
    """Get knowledge directory using portable path resolution (CORE-028)."""
    return Path(__file__).parent.parent.parent.parent / "cortex-brain" / "tier3" / "knowledge"


@dataclass
class IndexEntry:
    """Represents an indexed knowledge entry."""
    entry_id: str
    domain: str
    title: str
    ac_ids: List[str]
    created_at: datetime
    quality_score: Optional[float] = None
    file_path: Optional[str] = None


@pytest.fixture(scope="module")
def indexer():
    """Create indexer instance for tests."""
    from cortex_brain.tier3.knowledge.knowledge_indexer import KnowledgeIndexer
    return KnowledgeIndexer()


class TestIndexStructure:
    """Tests for index data structure and schema."""
    
    def test_index_file_exists(self):
        """Verify knowledge index file exists."""
        from cortex_brain.tier3.knowledge.knowledge_indexer import KnowledgeIndexer
        indexer = KnowledgeIndexer()
        
        knowledge_dir = get_knowledge_dir()
        index_file = knowledge_dir / ".knowledge-index.json"
        assert index_file.exists(), "Knowledge index file not found"
    
    def test_index_file_contains_valid_json(self, indexer):
        """Verify index file contains valid JSON."""
        knowledge_dir = get_knowledge_dir()
        index_file = knowledge_dir / ".knowledge-index.json"
        with open(index_file, 'r') as f:
            data = json.load(f)
        assert data is not None, "Index JSON is empty or invalid"
    
    def test_index_contains_metadata_section(self, indexer):
        """Verify index contains metadata about the index itself."""
        knowledge_dir = get_knowledge_dir()
        index_file = knowledge_dir / ".knowledge-index.json"
        with open(index_file, 'r') as f:
            data = json.load(f)
        
        assert "metadata" in data, "Index missing metadata section"
        metadata = data["metadata"]
        assert "version" in metadata, "Metadata missing version"
        assert "created_at" in metadata, "Metadata missing created_at"
        assert "entry_count" in metadata, "Metadata missing entry_count"
    
    def test_index_contains_entries_section(self, indexer):
        """Verify index contains entries section."""
        knowledge_dir = get_knowledge_dir()
        index_file = knowledge_dir / ".knowledge-index.json"
        with open(index_file, 'r') as f:
            data = json.load(f)
        
        assert "entries" in data, "Index missing entries section"
        assert isinstance(data["entries"], list), "Entries should be a list"
    
    def test_index_contains_ac_id_mapping_section(self, indexer):
        """Verify index contains AC-ID to domain mapping."""
        knowledge_dir = get_knowledge_dir()
        index_file = knowledge_dir / ".knowledge-index.json"
        with open(index_file, 'r') as f:
            data = json.load(f)
        
        assert "ac_id_mapping" in data, "Index missing ac_id_mapping section"
        assert isinstance(data["ac_id_mapping"], dict), "ac_id_mapping should be a dict"
    
    def test_index_contains_domain_index_section(self, indexer):
        """Verify index contains per-domain index."""
        knowledge_dir = get_knowledge_dir()
        index_file = knowledge_dir / ".knowledge-index.json"
        with open(index_file, 'r') as f:
            data = json.load(f)
        
        assert "by_domain" in data, "Index missing by_domain section"
        assert isinstance(data["by_domain"], dict), "by_domain should be a dict"


class TestIndexEntry:
    """Tests for individual index entries."""
    
    def test_index_entry_has_required_fields(self, indexer):
        """Verify each index entry has required fields."""
        knowledge_dir = get_knowledge_dir()
        index_file = knowledge_dir / ".knowledge-index.json"
        with open(index_file, 'r') as f:
            data = json.load(f)
        
        required_fields = ["entry_id", "domain", "title", "ac_ids", "created_at"]
        
        for entry in data["entries"]:
            for field in required_fields:
                assert field in entry, f"Index entry missing required field: {field}"
                assert entry[field] is not None, f"Index entry field is None: {field}"
    
    def test_index_entry_id_format_valid(self, indexer):
        """Verify index entry IDs follow correct format."""
        knowledge_dir = get_knowledge_dir()
        index_file = knowledge_dir / ".knowledge-index.json"
        with open(index_file, 'r') as f:
            data = json.load(f)
        
        for entry in data["entries"]:
            entry_id = entry["entry_id"]
            # Should start with KE-
            assert entry_id.startswith("KE-"), f"Invalid entry ID format: {entry_id}"
    
    def test_index_entry_domain_valid(self, indexer):
        """Verify index entry domains are from valid domain list."""
        knowledge_dir = get_knowledge_dir()
        index_file = knowledge_dir / ".knowledge-index.json"
        with open(index_file, 'r') as f:
            data = json.load(f)
        
        valid_domains = [
            "GOVERNANCE", "INTENT-ROUTING", "HALLUCINATION-PREVENTION",
            "EXECUTION-ORCHESTRATION", "DATA-MANAGEMENT", "OBSERVABILITY",
            "SECURITY", "API-DESIGN", "ML-MODELS", "KNOWLEDGE-CURATION",
            "TESTING-VALIDATION", "DEPLOYMENT", "DOCUMENTATION",
            "PERFORMANCE", "ARCHITECTURE", "ERROR-HANDLING"
        ]
        
        for entry in data["entries"]:
            assert entry["domain"] in valid_domains, f"Invalid domain: {entry['domain']}"
    
    def test_index_entry_ac_ids_is_list(self, indexer):
        """Verify ac_ids field is a list."""
        knowledge_dir = get_knowledge_dir()
        index_file = knowledge_dir / ".knowledge-index.json"
        with open(index_file, 'r') as f:
            data = json.load(f)
        
        for entry in data["entries"]:
            assert isinstance(entry["ac_ids"], list), f"ac_ids should be a list for {entry['entry_id']}"


class TestACIDMapping:
    """Tests for AC-ID to domain mapping."""
    
    def test_ac_id_mapping_exists_for_all_entries(self, indexer):
        """Verify AC-ID mapping exists for all indexed entries."""
        knowledge_dir = get_knowledge_dir()
        index_file = knowledge_dir / ".knowledge-index.json"
        with open(index_file, 'r') as f:
            data = json.load(f)
        
        ac_id_mapping = data["ac_id_mapping"]
        
        # Every entry with AC-IDs should have mapping entries
        for entry in data["entries"]:
            for ac_id in entry["ac_ids"]:
                assert ac_id in ac_id_mapping, f"Missing AC-ID mapping for {ac_id}"
    
    def test_ac_id_mapping_points_to_correct_domain(self, indexer):
        """Verify AC-ID mappings point to correct domains."""
        knowledge_dir = get_knowledge_dir()
        index_file = knowledge_dir / ".knowledge-index.json"
        with open(index_file, 'r') as f:
            data = json.load(f)
        
        ac_id_mapping = data["ac_id_mapping"]
        entries_by_id = {e["entry_id"]: e for e in data["entries"]}
        
        for ac_id, mapped_data in ac_id_mapping.items():
            # Find which entry contains this AC-ID
            for entry in data["entries"]:
                if ac_id in entry["ac_ids"]:
                    assert mapped_data["domain"] == entry["domain"], \
                        f"AC-ID {ac_id} mapped to wrong domain"
                    break
    
    def test_ac_id_mapping_has_reference_info(self, indexer):
        """Verify AC-ID mapping contains reference information."""
        knowledge_dir = get_knowledge_dir()
        index_file = knowledge_dir / ".knowledge-index.json"
        with open(index_file, 'r') as f:
            data = json.load(f)
        
        ac_id_mapping = data["ac_id_mapping"]
        
        for ac_id, mapping in ac_id_mapping.items():
            assert "entry_id" in mapping, f"Mapping missing entry_id for {ac_id}"
            assert "domain" in mapping, f"Mapping missing domain for {ac_id}"


class TestDomainIndex:
    """Tests for per-domain index."""
    
    def test_domain_index_has_all_domains(self, indexer):
        """Verify domain index contains all 16 domains."""
        knowledge_dir = get_knowledge_dir()
        index_file = knowledge_dir / ".knowledge-index.json"
        with open(index_file, 'r') as f:
            data = json.load(f)
        
        by_domain = data["by_domain"]
        expected_domains = [
            "GOVERNANCE", "INTENT-ROUTING", "HALLUCINATION-PREVENTION",
            "EXECUTION-ORCHESTRATION", "DATA-MANAGEMENT", "OBSERVABILITY",
            "SECURITY", "API-DESIGN", "ML-MODELS", "KNOWLEDGE-CURATION",
            "TESTING-VALIDATION", "DEPLOYMENT", "DOCUMENTATION",
            "PERFORMANCE", "ARCHITECTURE", "ERROR-HANDLING"
        ]
        
        for domain in expected_domains:
            assert domain in by_domain, f"Domain index missing {domain}"
    
    def test_domain_index_entries_format(self, indexer):
        """Verify domain index entries are properly formatted."""
        knowledge_dir = get_knowledge_dir()
        index_file = knowledge_dir / ".knowledge-index.json"
        with open(index_file, 'r') as f:
            data = json.load(f)
        
        by_domain = data["by_domain"]
        
        for domain, entries in by_domain.items():
            assert isinstance(entries, list), f"Domain {domain} entries should be a list"
            # Each entry in domain index should be an entry_id
            for entry_id in entries:
                assert isinstance(entry_id, str), f"Domain index entry should be string"


class TestIndexAPI:
    """Tests for index search and retrieval API."""
    
    def test_find_entries_by_domain_method_exists(self, indexer):
        """Verify API has method to find entries by domain."""
        assert hasattr(indexer, 'find_entries_by_domain'), \
            "KnowledgeIndexer missing find_entries_by_domain method"
    
    def test_find_entries_by_ac_id_method_exists(self, indexer):
        """Verify API has method to find entries by AC-ID."""
        assert hasattr(indexer, 'find_entries_by_ac_id'), \
            "KnowledgeIndexer missing find_entries_by_ac_id method"
    
    def test_find_domain_for_ac_id_method_exists(self, indexer):
        """Verify API has method to find domain for AC-ID."""
        assert hasattr(indexer, 'find_domain_for_ac_id'), \
            "KnowledgeIndexer missing find_domain_for_ac_id method"
    
    def test_search_by_title_method_exists(self, indexer):
        """Verify API has method to search by title."""
        assert hasattr(indexer, 'search_by_title'), \
            "KnowledgeIndexer missing search_by_title method"
    
    def test_get_index_stats_method_exists(self, indexer):
        """Verify API has method to get index statistics."""
        assert hasattr(indexer, 'get_index_stats'), \
            "KnowledgeIndexer missing get_index_stats method"


class TestIndexingOnCommit:
    """Tests for index rebuilding on knowledge entry commits."""
    
    def test_index_rebuild_method_exists(self, indexer):
        """Verify indexer has method to rebuild index."""
        assert hasattr(indexer, 'rebuild_index'), \
            "KnowledgeIndexer missing rebuild_index method"
    
    def test_index_rebuild_returns_success(self, indexer):
        """Verify index rebuild returns success status."""
        result = indexer.rebuild_index()
        assert result is True or isinstance(result, dict), \
            "rebuild_index should return bool or dict with result"
    
    def test_index_update_method_exists(self, indexer):
        """Verify indexer has method to update single entry."""
        assert hasattr(indexer, 'update_entry'), \
            "KnowledgeIndexer missing update_entry method"


class TestIndexConsistency:
    """Tests for index consistency and integrity."""
    
    def test_index_entry_count_matches_metadata(self, indexer):
        """Verify index entry count in metadata matches actual entries."""
        knowledge_dir = get_knowledge_dir()
        index_file = knowledge_dir / ".knowledge-index.json"
        with open(index_file, 'r') as f:
            data = json.load(f)
        
        metadata_count = data["metadata"]["entry_count"]
        actual_count = len(data["entries"])
        assert metadata_count == actual_count, \
            f"Metadata entry_count ({metadata_count}) doesn't match actual ({actual_count})"
    
    def test_domain_index_count_matches_entries(self, indexer):
        """Verify per-domain index counts match actual domain entries."""
        knowledge_dir = get_knowledge_dir()
        index_file = knowledge_dir / ".knowledge-index.json"
        with open(index_file, 'r') as f:
            data = json.load(f)
        
        # Count entries by domain
        domain_counts = {}
        for entry in data["entries"]:
            domain = entry["domain"]
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
        
        # Verify index by_domain counts match
        for domain, count in domain_counts.items():
            actual_in_index = len(data["by_domain"][domain])
            assert count == actual_in_index, \
                f"Domain {domain} count mismatch: {count} vs {actual_in_index}"
    
    def test_no_duplicate_entries_in_index(self, indexer):
        """Verify no duplicate entries in index."""
        knowledge_dir = get_knowledge_dir()
        index_file = knowledge_dir / ".knowledge-index.json"
        with open(index_file, 'r') as f:
            data = json.load(f)
        
        entry_ids = [e["entry_id"] for e in data["entries"]]
        assert len(entry_ids) == len(set(entry_ids)), "Duplicate entries found in index"


class TestIndexVersion:
    """Tests for index versioning and metadata."""
    
    def test_index_metadata_has_version(self, indexer):
        """Verify index has version information."""
        knowledge_dir = get_knowledge_dir()
        index_file = knowledge_dir / ".knowledge-index.json"
        with open(index_file, 'r') as f:
            data = json.load(f)
        
        assert "version" in data["metadata"], "Index metadata missing version"
        assert data["metadata"]["version"] is not None, "Index version is None"
    
    def test_index_metadata_has_created_at(self, indexer):
        """Verify index has creation timestamp."""
        knowledge_dir = get_knowledge_dir()
        index_file = knowledge_dir / ".knowledge-index.json"
        with open(index_file, 'r') as f:
            data = json.load(f)
        
        assert "created_at" in data["metadata"], "Index metadata missing created_at"
        assert data["metadata"]["created_at"] is not None, "Index created_at is None"
    
    def test_index_metadata_has_updated_at(self, indexer):
        """Verify index has last updated timestamp."""
        knowledge_dir = get_knowledge_dir()
        index_file = knowledge_dir / ".knowledge-index.json"
        with open(index_file, 'r') as f:
            data = json.load(f)
        
        assert "updated_at" in data["metadata"], "Index metadata missing updated_at"


class TestIndexQueryPerformance:
    """Tests for index query performance."""
    
    def test_index_loads_under_100ms(self, indexer):
        """Verify index loads in under 100ms."""
        import time
        knowledge_dir = get_knowledge_dir()
        index_file = knowledge_dir / ".knowledge-index.json"
        
        start = time.time()
        with open(index_file, 'r') as f:
            data = json.load(f)
        elapsed = (time.time() - start) * 1000  # Convert to ms
        
        assert elapsed < 100, f"Index load took {elapsed:.2f}ms (should be < 100ms)"
    
    def test_domain_lookup_is_constant_time(self, indexer):
        """Verify domain lookup is O(1) operation."""
        knowledge_dir = get_knowledge_dir()
        index_file = knowledge_dir / ".knowledge-index.json"
        with open(index_file, 'r') as f:
            data = json.load(f)
        
        # Domain lookup should use dict, not list scan
        assert isinstance(data["by_domain"], dict), "by_domain should use dict for O(1) lookup"


class TestIndexGoveranceIntegration:
    """Tests for integration with governance system."""
    
    def test_index_tracks_indexing_ac_id(self, indexer):
        """Verify index references correct AC-ID."""
        knowledge_dir = get_knowledge_dir()
        index_file = knowledge_dir / ".knowledge-index.json"
        with open(index_file, 'r') as f:
            data = json.load(f)
        
        assert "metadata" in data, "Index missing metadata"
        assert "ac_id" in data["metadata"], "Index metadata missing ac_id reference"
        assert data["metadata"]["ac_id"] == "KN-001-02", "Index should reference KN-001-02"
    
    def test_index_includes_governance_db_reference(self, indexer):
        """Verify index can be integrated with governance.db."""
        # Should contain reference to governance database
        knowledge_dir = get_knowledge_dir()
        index_file = knowledge_dir / ".knowledge-index.json"
        with open(index_file, 'r') as f:
            data = json.load(f)
        
        # Index should include AC-ID mappings for audit trail
        assert "ac_id_mapping" in data, "Index missing ac_id_mapping for governance"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
