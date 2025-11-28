"""
Test suite for System Alignment + Enhancement Catalog integration.

Validates Phase 0 discovery of features from centralized catalog.
"""

import pytest
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from src.utils.enhancement_catalog import EnhancementCatalog, FeatureType, Feature


class TestAlignmentCatalogIntegration:
    """Test System Alignment catalog discovery."""
    
    def test_catalog_features_discovered(self, tmp_path):
        """Catalog returns features since last review."""
        # Setup
        db_path = tmp_path / "cortex-brain" / "tier3" / "context.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        catalog = EnhancementCatalog(db_path=db_path)
        catalog.add_feature(
            name="test_feature",
            feature_type=FeatureType.OPERATION,
            description="Test feature",
            source="test"
        )
        
        # Execute
        last_review = catalog.get_last_review_timestamp('alignment')
        features = catalog.get_features_since(
            since_date=datetime.now() - timedelta(days=1) if not last_review else last_review
        )
        
        # Assert
        assert len(features) > 0
        assert any(f.name == 'test_feature' for f in features)
    
    def test_catalog_review_logged(self, tmp_path):
        """Catalog logs review event."""
        # Setup
        db_path = tmp_path / "cortex-brain" / "tier3" / "context.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        catalog = EnhancementCatalog(db_path=db_path)
        
        # Execute
        catalog.log_review(
            review_type='alignment',
            features_reviewed=5,
            new_features_found=2,
            notes="Test review"
        )
        
        # Assert
        last_review = catalog.get_last_review_timestamp('alignment')
        assert last_review is not None
    
    def test_catalog_returns_stats(self, tmp_path):
        """Catalog provides statistics."""
        # Setup
        db_path = tmp_path / "cortex-brain" / "tier3" / "context.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        catalog = EnhancementCatalog(db_path=db_path)
        catalog.add_feature(
            name="feature1",
            feature_type=FeatureType.AGENT,
            description="Agent feature",
            source="test"
        )
        catalog.add_feature(
            name="feature2",
            feature_type=FeatureType.OPERATION,
            description="Operation feature",
            source="test"
        )
        
        # Execute
        stats = catalog.get_catalog_stats()
        
        # Assert
        assert stats['total_features'] >= 2
        assert 'by_type' in stats
        assert 'by_status' in stats
    
    def test_catalog_handles_no_features(self, tmp_path):
        """Catalog handles empty catalog gracefully."""
        # Setup
        db_path = tmp_path / "cortex-brain" / "tier3" / "context.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        catalog = EnhancementCatalog(db_path=db_path)
        
        # Execute
        features = catalog.get_features_since(since_date=datetime.now() - timedelta(days=1))
        stats = catalog.get_catalog_stats()
        
        # Assert
        assert features == []
        assert stats['total_features'] == 0
    
    def test_catalog_since_never_reviewed(self, tmp_path):
        """Catalog handles first review correctly."""
        # Setup
        db_path = tmp_path / "cortex-brain" / "tier3" / "context.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        catalog = EnhancementCatalog(db_path=db_path)
        catalog.add_feature(
            name="old_feature",
            feature_type=FeatureType.WORKFLOW,
            description="Old feature",
            source="test"
        )
        
        # Execute
        last_review = catalog.get_last_review_timestamp('alignment')
        
        # Assert - never reviewed returns None
        assert last_review is None
    
    def test_catalog_discovery_with_progress(self, tmp_path):
        """Catalog discovery integrates with progress monitoring."""
        # Setup
        db_path = tmp_path / "cortex-brain" / "tier3" / "context.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        catalog = EnhancementCatalog(db_path=db_path)
        for i in range(5):
            catalog.add_feature(
                name=f"feature_{i}",
                feature_type=FeatureType.OPERATION,
                description=f"Feature {i}",
                source="test"
            )
        
        # Execute - simulate discovery
        features = catalog.get_features_since(since_date=datetime.now() - timedelta(days=7))
        
        # Assert
        assert len(features) == 5
        
        # Verify discovery metadata
        for feature in features:
            assert isinstance(feature, Feature)
            assert feature.name is not None
            assert feature.feature_type is not None
            assert feature.description is not None
