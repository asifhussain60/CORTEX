"""
Tests for Hash Verifier

AC-NFR-003-02: Hash chain integrity verified on read

Test scenarios:
- Hash computation
- Entry hash verification
- Chain verification
- Tampering detection
- Database verification
- Caching
- Proof generation
"""

import pytest
from datetime import datetime, timezone
from pathlib import Path
from cortex.infrastructure.hash_verifier import HashVerifier, HashChainEntry


class TestHashVerifier:
    """Test suite for HashVerifier."""
    
    @pytest.fixture
    def verifier(self):
        """Create hash verifier."""
        return HashVerifier()
    
    def test_compute_hash(self, verifier):
        """Test SHA-256 hash computation."""
        data = "test data"
        hash1 = verifier.compute_hash(data)
        hash2 = verifier.compute_hash(data)
        
        # Consistent hashing
        assert hash1 == hash2
        
        # Correct length (SHA-256 = 64 hex chars)
        assert len(hash1) == 64
        
        # Different data produces different hash
        assert verifier.compute_hash("different data") != hash1
    
    def test_compute_entry_hash(self, verifier):
        """Test entry hash computation."""
        data_hash = verifier.compute_hash("entry data")
        previous_hash = verifier.compute_hash("previous")
        
        entry_hash = verifier.compute_entry_hash(data_hash, previous_hash)
        
        # Valid hash format
        assert len(entry_hash) == 64
        
        # Deterministic
        entry_hash2 = verifier.compute_entry_hash(data_hash, previous_hash)
        assert entry_hash == entry_hash2
        
        # Different if input changes
        different_hash = verifier.compute_entry_hash(data_hash, "different_previous")
        assert different_hash != entry_hash
    
    def test_create_chain_entry(self, verifier):
        """Test creating a hash chain entry."""
        entry = verifier.create_chain_entry("entry-001", "test data")
        
        assert entry.id == "entry-001"
        assert entry.data_hash == verifier.compute_hash("test data")
        assert len(entry.entry_hash) == 64
        assert len(entry.data_hash) == 64
        assert entry.previous_hash == "0" * 64
    
    def test_create_chain_entry_with_previous(self, verifier):
        """Test creating entry with previous hash."""
        previous_hash = verifier.compute_hash("previous entry")
        entry = verifier.create_chain_entry("entry-002", "test data", previous_hash)
        
        assert entry.previous_hash == previous_hash
        assert entry.entry_hash == verifier.compute_entry_hash(entry.data_hash, previous_hash)
    
    def test_verify_single_entry(self, verifier):
        """Test verification of single entry."""
        entry = verifier.create_chain_entry("entry-001", "data")
        entry_dict = entry.to_dict()
        
        result = verifier.verify_entry(entry_dict)
        assert result.is_ok()
        assert result.unwrap() is True
    
    def test_verify_tampered_entry(self, verifier):
        """Test detection of tampered entry."""
        entry = verifier.create_chain_entry("entry-001", "data")
        entry_dict = entry.to_dict()
        
        # Tamper with data hash
        entry_dict['data_hash'] = "0" * 64
        
        result = verifier.verify_entry(entry_dict)
        assert result.is_ok()
        assert result.unwrap() is False
    
    def test_verify_chain_valid(self, verifier):
        """Test verification of valid chain."""
        # Create chain
        entry1 = verifier.create_chain_entry("entry-001", "data1")
        entry2 = verifier.create_chain_entry("entry-002", "data2", entry1.entry_hash)
        entry3 = verifier.create_chain_entry("entry-003", "data3", entry2.entry_hash)
        
        chain = [entry1.to_dict(), entry2.to_dict(), entry3.to_dict()]
        
        result = verifier.verify_chain(chain)
        assert result.is_ok()
        valid, details = result.unwrap()
        assert valid is True
        assert "verified" in details.lower()
    
    def test_verify_chain_broken_link(self, verifier):
        """Test detection of broken chain link."""
        entry1 = verifier.create_chain_entry("entry-001", "data1")
        entry2 = verifier.create_chain_entry("entry-002", "data2", entry1.entry_hash)
        entry3 = verifier.create_chain_entry("entry-003", "data3", "wrong_hash_1234567890")
        
        chain = [entry1.to_dict(), entry2.to_dict(), entry3.to_dict()]
        
        result = verifier.verify_chain(chain)
        assert result.is_ok()
        valid, details = result.unwrap()
        assert valid is False
        assert "tampering" in details.lower()
    
    def test_verify_chain_empty(self, verifier):
        """Test verification of empty chain."""
        result = verifier.verify_chain([])
        assert result.is_ok()
        valid, details = result.unwrap()
        assert valid is True
    
    def test_verify_entry_missing_fields(self, verifier):
        """Test verification with missing fields."""
        entry = {"entry_hash": "abc123"}  # Missing required fields
        
        result = verifier.verify_entry(entry)
        assert result.is_err()
    
    def test_get_verification_proof(self, verifier):
        """Test generating verification proof."""
        entry = verifier.create_chain_entry("entry-001", "data")
        proof = verifier.get_verification_proof(entry.to_dict())
        
        assert proof['match'] is True
        assert proof['entry_id'] == "entry-001"
        assert proof['computed_hash'] == proof['claimed_hash']
    
    def test_cache_verification(self, verifier):
        """Test verification caching."""
        verifier.cache_verification("entry-001", True)
        
        cached = verifier.get_cached_verification("entry-001")
        assert cached is True
        
        not_cached = verifier.get_cached_verification("entry-999")
        assert not_cached is None
    
    def test_cache_eviction(self):
        """Test cache eviction when full."""
        small_cache_verifier = HashVerifier(cache_size=3)
        
        small_cache_verifier.cache_verification("entry-001", True)
        small_cache_verifier.cache_verification("entry-002", True)
        small_cache_verifier.cache_verification("entry-003", True)
        
        # Cache should be full (3 items)
        assert len(small_cache_verifier._verification_cache) == 3
        
        # Add 4th item - should evict oldest
        small_cache_verifier.cache_verification("entry-004", True)
        assert len(small_cache_verifier._verification_cache) == 3
        
        # Oldest should be gone
        assert small_cache_verifier.get_cached_verification("entry-001") is None
    
    def test_clear_cache(self, verifier):
        """Test cache clearing."""
        verifier.cache_verification("entry-001", True)
        verifier.cache_verification("entry-002", False)
        
        assert len(verifier._verification_cache) == 2
        
        verifier.clear_cache()
        assert len(verifier._verification_cache) == 0
    
    def test_export_chain_to_json(self, verifier):
        """Test exporting chain to JSON."""
        entry1 = verifier.create_chain_entry("entry-001", "data1")
        entry2 = verifier.create_chain_entry("entry-002", "data2", entry1.entry_hash)
        
        chain = [entry1.to_dict(), entry2.to_dict()]
        json_str = verifier.export_chain_to_json(chain)
        
        assert "chain" in json_str
        assert "entry_count" in json_str
        assert "exported_at" in json_str
        assert "entry-001" in json_str
    
    def test_detect_tampering_hash_mismatch(self, verifier):
        """Test tampering detection for hash mismatch."""
        entry = verifier.create_chain_entry("entry-001", "data")
        entry_dict = entry.to_dict()
        
        # Tamper
        entry_dict['data_hash'] = "0" * 64
        
        indicators = verifier.detect_tampering_indicators([entry_dict])
        assert len(indicators) > 0
        assert any(ind['type'] == 'hash_mismatch' for ind in indicators)
    
    def test_detect_tampering_broken_link(self, verifier):
        """Test tampering detection for broken chain link."""
        entry1 = verifier.create_chain_entry("entry-001", "data1")
        entry2 = verifier.create_chain_entry("entry-002", "data2", entry1.entry_hash)
        
        # Break the link
        entry2_dict = entry2.to_dict()
        entry2_dict['previous_hash'] = "wrong_hash_1234567890"
        
        indicators = verifier.detect_tampering_indicators([entry1.to_dict(), entry2_dict])
        assert len(indicators) > 0
        assert any(ind['type'] == 'chain_link_broken' for ind in indicators)
    
    def test_detect_tampering_timestamp_anomaly(self, verifier):
        """Test tampering detection for timestamp anomalies."""
        entry1 = verifier.create_chain_entry("entry-001", "data1")
        entry2 = verifier.create_chain_entry("entry-002", "data2", entry1.entry_hash)
        
        # Make entry2 timestamp earlier
        entry2_dict = entry2.to_dict()
        past_time = (datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)).isoformat()
        entry2_dict['timestamp'] = past_time
        
        indicators = verifier.detect_tampering_indicators([entry1.to_dict(), entry2_dict])
        assert any(ind['type'] == 'timestamp_anomaly' for ind in indicators)
    
    def test_verify_chain_multiple_entries(self, verifier):
        """Test verification of multi-entry chain."""
        entries = []
        prev_hash = "0" * 64
        
        for i in range(10):
            entry = verifier.create_chain_entry(f"entry-{i:03d}", f"data{i}", prev_hash)
            entries.append(entry.to_dict())
            prev_hash = entry.entry_hash
        
        result = verifier.verify_chain(entries)
        assert result.is_ok()
        valid, _ = result.unwrap()
        assert valid is True
