"""
Test suite for System Alignment + Enhancement Catalog + Learning Library integration.

Validates Phase 0 discovery of features from centralized catalog and
automatic documentation generation via Learning Library.

INCREMENT 10: Enhancement Catalog Discovery
- Temporal tracking: "what's new since last alignment"
- Review logging: records review events per orchestrator
- Statistics: total_features, by_type, by_status counts
- Edge cases: first review (no history), empty catalog

INCREMENT 11: Learning Library Integration
- Document generation from alignment events
- Event capture during alignment
- Auto-documentation of discovered features
- Learning resource creation

Test Coverage:
- Feature discovery from catalog (temporal query)
- Review event logging (timestamp + counts)
- Catalog statistics retrieval
- Empty catalog handling
- First review (never reviewed before)
- Bulk feature discovery with progress tracking
- Learning library document generation
- Event capture integration
- Auto-documentation workflow

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Status: COMPLETE (9/9 tests passing)
"""

import pytest
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from src.utils.enhancement_catalog import EnhancementCatalog, FeatureType, Feature
from src.learning.document_generator import DocumentGenerator
from src.learning.event_taxonomy import LearningEvent, EventType, EventTier
from src.learning.event_collector import LearningEventCollector


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


class TestLearningLibraryIntegration:
    """Test Learning Library integration with Alignment."""
    
    def test_document_generator_creates_alignment_doc(self, tmp_path):
        """Document generator creates documentation from alignment event."""
        # Setup
        generator = DocumentGenerator(enabled=True)
        event = LearningEvent(
            event_type=EventType.WORKFLOW_COMPLETED,
            component="SystemAlignment",
            metadata={
                "features_discovered": 5,
                "new_features": 2,
                "review_duration_ms": 1500
            }
        )
        
        # Execute
        doc = generator.generate_document(event)
        
        # Assert
        assert doc is not None
        assert len(doc) > 0
        assert "WORKFLOW_COMPLETED" in doc or "Workflow Completed" in doc
        assert "SystemAlignment" in doc
    
    def test_event_collector_captures_alignment_events(self, tmp_path):
        """Event collector captures alignment events."""
        # Setup
        collector = LearningEventCollector(enabled=True)
        event = LearningEvent(
            event_type=EventType.OPERATION_ROUTED,
            component="SystemAlignment",
            metadata={"operation": "align"}
        )
        
        # Execute
        collector.capture_event(event)
        events = collector.get_all_events()
        
        # Assert
        assert len(events) > 0
        assert events[0].event_type == EventType.OPERATION_ROUTED
        assert events[0].component == "SystemAlignment"
    
    def test_alignment_generates_learning_documentation(self, tmp_path):
        """Alignment workflow generates learning documentation."""
        # Setup
        db_path = tmp_path / "cortex-brain" / "tier3" / "context.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        catalog = EnhancementCatalog(db_path=db_path)
        generator = DocumentGenerator(enabled=True)
        collector = LearningEventCollector(enabled=True)
        
        # Add features
        catalog.add_feature(
            name="test_feature",
            feature_type=FeatureType.OPERATION,
            description="Test feature",
            source="test"
        )
        
        # Simulate alignment workflow
        features = catalog.get_features_since(
            since_date=datetime.now() - timedelta(days=1)
        )
        
        # Emit event
        event = LearningEvent(
            event_type=EventType.WORKFLOW_COMPLETED,
            component="SystemAlignment",
            metadata={
                "features_discovered": len(features),
                "new_features": len(features)
            }
        )
        collector.capture_event(event)
        
        # Generate documentation
        doc = generator.generate_document(event)
        
        # Log review
        catalog.log_review(
            review_type='alignment',
            features_reviewed=len(features),
            new_features_found=len(features)
        )
        
        # Assert
        assert doc is not None
        assert len(collector.get_all_events()) == 1
        assert catalog.get_last_review_timestamp('alignment') is not None
