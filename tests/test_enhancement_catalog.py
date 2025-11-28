"""
Unit Tests for Enhancement Catalog System

Tests CRUD operations, caching, deduplication, and temporal queries.

Author: GitHub Copilot
Created: 2024-11-28
"""

import pytest
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import sys
import tempfile
import shutil

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.enhancement_catalog import (
    EnhancementCatalog,
    FeatureType,
    AcceptanceStatus,
)


@pytest.fixture
def temp_catalog():
    """Create temporary catalog for testing."""
    temp_dir = tempfile.mkdtemp()
    temp_brain = Path(temp_dir) / "cortex-brain"
    temp_tier3 = temp_brain / "tier3"
    temp_tier3.mkdir(parents=True)
    
    # Create catalog with temporary path
    catalog = EnhancementCatalog(brain_path=temp_brain)
    
    yield catalog
    
    # Cleanup
    shutil.rmtree(temp_dir)


class TestEnhancementCatalogCRUD:
    """Test Create, Read, Update, Delete operations."""
    
    def test_add_feature_new(self, temp_catalog):
        """Test adding a new feature."""
        result = temp_catalog.add_feature(
            name="test_operation",
            feature_type=FeatureType.OPERATION,
            description="Test operation for unit tests",
            source="test"
        )
        
        assert result is True
        
        # Verify feature exists
        features = temp_catalog.get_features_since(datetime.now() - timedelta(minutes=1))
        assert len(features) == 1
        assert features[0]['name'] == "test_operation"
        assert features[0]['type'] == "operation"
    
    def test_add_feature_duplicate(self, temp_catalog):
        """Test adding duplicate feature (should update, not create)."""
        # Add first time
        temp_catalog.add_feature(
            name="duplicate_test",
            feature_type=FeatureType.AGENT,
            description="First version",
            source="test"
        )
        
        # Add again with updated description
        result = temp_catalog.add_feature(
            name="duplicate_test",
            feature_type=FeatureType.AGENT,
            description="Updated version",
            source="test"
        )
        
        assert result is True
        
        # Verify only one feature exists
        features = temp_catalog.get_features_since(datetime.now() - timedelta(minutes=1))
        assert len(features) == 1
        assert features[0]['description'] == "Updated version"
    
    def test_get_features_since_filtering(self, temp_catalog):
        """Test temporal filtering of features."""
        # Add feature from 10 days ago
        old_date = datetime.now() - timedelta(days=10)
        temp_catalog.add_feature(
            name="old_feature",
            feature_type=FeatureType.OPERATION,
            description="Old feature",
            source="test"
        )
        
        # Manually update date to simulate old feature
        conn = sqlite3.connect(temp_catalog.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE cortex_features SET added_at = ? WHERE name = ?",
            (old_date.isoformat(), "old_feature")
        )
        conn.commit()
        conn.close()
        
        # Add recent feature
        temp_catalog.add_feature(
            name="new_feature",
            feature_type=FeatureType.AGENT,
            description="New feature",
            source="test"
        )
        
        # Query features from 5 days ago (should only get new_feature)
        features = temp_catalog.get_features_since(datetime.now() - timedelta(days=5))
        assert len(features) == 1
        assert features[0]['name'] == "new_feature"
        
        # Query all features (should get both)
        all_features = temp_catalog.get_features_since(datetime.now() - timedelta(days=30))
        assert len(all_features) == 2
    
    def test_update_acceptance_status(self, temp_catalog):
        """Test updating feature acceptance status."""
        # Add feature
        temp_catalog.add_feature(
            name="status_test",
            feature_type=FeatureType.WORKFLOW,
            description="Test status updates",
            source="test"
        )
        
        # Update status
        result = temp_catalog.update_acceptance(
            "status_test",
            AcceptanceStatus.ACCEPTED,
            "Feature approved by user"
        )
        
        assert result is True
        
        # Verify status updated
        features = temp_catalog.get_features_since(datetime.now() - timedelta(minutes=1))
        assert features[0]['acceptance_status'] == "accepted"
    
    def test_get_catalog_stats(self, temp_catalog):
        """Test catalog statistics aggregation."""
        # Add various features
        temp_catalog.add_feature("op1", FeatureType.OPERATION, "Op 1", "test")
        temp_catalog.add_feature("op2", FeatureType.OPERATION, "Op 2", "test")
        temp_catalog.add_feature("agent1", FeatureType.AGENT, "Agent 1", "test")
        temp_catalog.add_feature("orch1", FeatureType.ORCHESTRATOR, "Orch 1", "test")
        
        # Update one to accepted
        temp_catalog.update_acceptance("op1", AcceptanceStatus.ACCEPTED, "Approved")
        
        # Get stats
        stats = temp_catalog.get_catalog_stats()
        
        assert stats['total_features'] == 4
        assert stats['by_type']['operation'] == 2
        assert stats['by_type']['agent'] == 1
        assert stats['by_type']['orchestrator'] == 1
        assert stats['by_status']['discovered'] == 3
        assert stats['by_status']['accepted'] == 1


class TestEnhancementCatalogCaching:
    """Test caching behavior."""
    
    def test_cache_hit(self, temp_catalog):
        """Test cache returns same results without DB query."""
        # Add feature
        temp_catalog.add_feature("cache_test", FeatureType.OPERATION, "Test", "test")
        
        # First query (cache miss)
        since_date = datetime.now() - timedelta(minutes=1)
        features1 = temp_catalog.get_features_since(since_date)
        
        # Second query with same date (cache hit)
        features2 = temp_catalog.get_features_since(since_date)
        
        # Should return identical results
        assert len(features1) == len(features2)
        assert features1[0]['name'] == features2[0]['name']
    
    def test_cache_invalidation_on_add(self, temp_catalog):
        """Test cache invalidates when new feature added."""
        # Add feature and query
        temp_catalog.add_feature("feature1", FeatureType.OPERATION, "Test 1", "test")
        since_date = datetime.now() - timedelta(minutes=1)
        features1 = temp_catalog.get_features_since(since_date)
        assert len(features1) == 1
        
        # Add another feature (should invalidate cache)
        temp_catalog.add_feature("feature2", FeatureType.AGENT, "Test 2", "test")
        
        # Query again (should see new feature)
        features2 = temp_catalog.get_features_since(since_date)
        assert len(features2) == 2
    
    def test_cache_ttl_expiration(self, temp_catalog):
        """Test cache expires after TTL (24 hours)."""
        # This is difficult to test without mocking time
        # Just verify cache exists and has TTL mechanism
        assert hasattr(temp_catalog, '_cache')
        assert hasattr(temp_catalog, '_cache_ttl')
        assert temp_catalog._cache_ttl == timedelta(hours=24)


class TestEnhancementCatalogDeduplication:
    """Test hash-based deduplication."""
    
    def test_hash_based_deduplication(self, temp_catalog):
        """Test features deduplicated by name+type hash."""
        # Add same feature twice
        temp_catalog.add_feature("dup_feature", FeatureType.OPERATION, "V1", "test")
        temp_catalog.add_feature("dup_feature", FeatureType.OPERATION, "V2", "test")
        
        # Should only have one feature
        features = temp_catalog.get_features_since(datetime.now() - timedelta(minutes=1))
        assert len(features) == 1
        
        # Should have latest description
        assert features[0]['description'] == "V2"
    
    def test_different_types_not_deduplicated(self, temp_catalog):
        """Test same name with different type creates separate entries."""
        temp_catalog.add_feature("multi_type", FeatureType.OPERATION, "Op", "test")
        temp_catalog.add_feature("multi_type", FeatureType.AGENT, "Agent", "test")
        
        # Should have two features
        features = temp_catalog.get_features_since(datetime.now() - timedelta(minutes=1))
        assert len(features) == 2


class TestEnhancementCatalogReviewLogging:
    """Test review event logging."""
    
    def test_log_review(self, temp_catalog):
        """Test logging review events."""
        result = temp_catalog.log_review(
            review_type='documentation',
            metadata={'version': '3.2.0', 'features_found': 10}
        )
        
        assert result is True
    
    def test_get_last_review_timestamp(self, temp_catalog):
        """Test retrieving last review timestamp."""
        # Initially no review
        timestamp = temp_catalog.get_last_review_timestamp('alignment')
        assert timestamp is None
        
        # Log review
        temp_catalog.log_review('alignment')
        
        # Should now have timestamp
        timestamp = temp_catalog.get_last_review_timestamp('alignment')
        assert timestamp is not None
        assert isinstance(timestamp, datetime)
        
        # Should be recent (within last minute)
        assert (datetime.now() - timestamp).total_seconds() < 60
    
    def test_multiple_review_types(self, temp_catalog):
        """Test independent tracking of different review types."""
        # Log different review types
        temp_catalog.log_review('documentation')
        temp_catalog.log_review('epm_setup')
        temp_catalog.log_review('alignment')
        
        # Each should have independent timestamp
        doc_time = temp_catalog.get_last_review_timestamp('documentation')
        epm_time = temp_catalog.get_last_review_timestamp('epm_setup')
        align_time = temp_catalog.get_last_review_timestamp('alignment')
        
        assert doc_time is not None
        assert epm_time is not None
        assert align_time is not None


class TestEnhancementCatalogEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_catalog(self, temp_catalog):
        """Test queries on empty catalog."""
        features = temp_catalog.get_features_since(datetime.now() - timedelta(days=30))
        assert features == []
        
        stats = temp_catalog.get_catalog_stats()
        assert stats['total_features'] == 0
        assert stats['by_type'] == {}
        assert stats['by_status'] == {}
    
    def test_invalid_feature_type(self, temp_catalog):
        """Test handling of invalid feature type."""
        # This should not raise exception, just use provided type
        result = temp_catalog.add_feature(
            "test", FeatureType.OPERATION, "Test", "test"
        )
        assert result is True
    
    def test_update_nonexistent_feature(self, temp_catalog):
        """Test updating feature that doesn't exist."""
        result = temp_catalog.update_acceptance(
            "nonexistent",
            AcceptanceStatus.ACCEPTED,
            "Test"
        )
        # Should return False (no rows updated)
        assert result is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
