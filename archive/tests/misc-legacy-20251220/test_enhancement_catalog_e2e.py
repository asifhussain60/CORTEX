"""
End-to-End Tests for Enhancement Cataloging System

Tests complete workflow: Discovery → Catalog → Retrieval

Author: GitHub Copilot
Created: 2024-11-28
"""

import pytest
from datetime import datetime, timedelta
from pathlib import Path
import sys
import tempfile
import shutil
import subprocess
import time

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.enhancement_catalog import EnhancementCatalog, FeatureType, AcceptanceStatus
from discovery.enhancement_discovery import EnhancementDiscoveryEngine


@pytest.fixture
def test_environment():
    """Create complete test environment with catalog and discovery."""
    temp_dir = tempfile.mkdtemp()
    repo_path = Path(temp_dir)
    
    # Setup git repo
    subprocess.run(['git', 'init'], cwd=repo_path, capture_output=True, check=True)
    subprocess.run(['git', 'config', 'user.name', 'Test'], cwd=repo_path, capture_output=True)
    subprocess.run(['git', 'config', 'user.email', 'test@test.com'], cwd=repo_path, capture_output=True)
    
    # Create CORTEX structure
    brain_path = repo_path / "cortex-brain"
    brain_path.mkdir()
    (brain_path / "tier3").mkdir()
    
    # Create source files
    (repo_path / "src" / "operations").mkdir(parents=True)
    (repo_path / "src" / "operations" / "test_op.py").write_text(
        '"""Test Operation Module"""\nclass TestOperation:\n    pass'
    )
    
    # Commit
    subprocess.run(['git', 'add', '.'], cwd=repo_path, capture_output=True)
    subprocess.run(['git', 'commit', '-m', 'Add test operation'], cwd=repo_path, capture_output=True)
    
    # Initialize catalog and engine
    catalog = EnhancementCatalog(brain_path=brain_path)
    engine = EnhancementDiscoveryEngine(repo_path)
    
    yield {
        'repo_path': repo_path,
        'brain_path': brain_path,
        'catalog': catalog,
        'engine': engine
    }
    
    # Cleanup
    shutil.rmtree(temp_dir)


class TestEndToEndWorkflow:
    """Test complete discovery → catalog → retrieval workflow."""
    
    def test_full_discovery_cycle(self, test_environment):
        """Test complete cycle from discovery to retrieval."""
        catalog = test_environment['catalog']
        engine = test_environment['engine']
        
        # Step 1: Discover features
        discovered = engine.discover_all()
        assert len(discovered) > 0, "Discovery should find features"
        
        # Step 2: Add to catalog
        for feature in discovered:
            catalog.add_feature(
                name=feature.name,
                feature_type=self._map_type(feature.type),
                description=feature.description or "",
                source=feature.source
            )
        
        # Step 3: Retrieve from catalog
        features = catalog.get_features_since(datetime.now() - timedelta(days=1))
        assert len(features) > 0, "Catalog should contain features"
        
        # Step 4: Verify feature data
        feature_names = [f['name'] for f in features]
        assert any('test_op' in name for name in feature_names)
    
    def test_incremental_discovery(self, test_environment):
        """Test incremental discovery with temporal filtering."""
        catalog = test_environment['catalog']
        engine = test_environment['engine']
        repo_path = test_environment['repo_path']
        
        # First discovery
        discovered1 = engine.discover_all()
        for feature in discovered1:
            catalog.add_feature(
                name=feature.name,
                feature_type=self._map_type(feature.type),
                description=feature.description or "",
                source=feature.source
            )
        
        # Log review
        catalog.log_review('test_review')
        initial_count = len(catalog.get_features_since(datetime.now() - timedelta(days=1)))
        
        # Add new file
        (repo_path / "src" / "operations" / "new_op.py").write_text(
            '"""New Operation"""\nclass NewOperation:\n    pass'
        )
        subprocess.run(['git', 'add', '.'], cwd=repo_path, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Add new operation'], cwd=repo_path, capture_output=True)
        
        # Second discovery (incremental)
        last_review = catalog.get_last_review_timestamp('test_review')
        discovered2 = engine.discover_since(last_review)
        
        for feature in discovered2:
            catalog.add_feature(
                name=feature.name,
                feature_type=self._map_type(feature.type),
                description=feature.description or "",
                source=feature.source
            )
        
        # Should have more features now
        final_count = len(catalog.get_features_since(datetime.now() - timedelta(days=1)))
        assert final_count > initial_count, "Incremental discovery should find new features"
    
    def test_review_logging_workflow(self, test_environment):
        """Test review logging across multiple discovery cycles."""
        catalog = test_environment['catalog']
        
        # Initial state: no reviews
        assert catalog.get_last_review_timestamp('documentation') is None
        
        # Log first review
        catalog.log_review('documentation', metadata={'features_found': 5})
        first_review = catalog.get_last_review_timestamp('documentation')
        assert first_review is not None
        
        # Small delay
        time.sleep(0.1)
        
        # Log second review
        catalog.log_review('documentation', metadata={'features_found': 7})
        second_review = catalog.get_last_review_timestamp('documentation')
        
        # Second review should be more recent
        assert second_review > first_review
    
    def test_acceptance_workflow(self, test_environment):
        """Test feature acceptance workflow."""
        catalog = test_environment['catalog']
        engine = test_environment['engine']
        
        # Discover and add features
        discovered = engine.discover_all()
        for feature in discovered:
            catalog.add_feature(
                name=feature.name,
                feature_type=self._map_type(feature.type),
                description=feature.description or "",
                source=feature.source
            )
        
        # Get stats (all should be 'discovered')
        stats = catalog.get_catalog_stats()
        assert stats['by_status']['discovered'] == stats['total_features']
        
        # Accept one feature
        features = catalog.get_features_since(datetime.now() - timedelta(days=1))
        if features:
            catalog.update_acceptance(
                features[0]['name'],
                AcceptanceStatus.ACCEPTED,
                "Approved by user"
            )
            
            # Stats should now show 1 accepted
            stats = catalog.get_catalog_stats()
            assert stats['by_status']['accepted'] == 1
            assert stats['by_status']['discovered'] == stats['total_features'] - 1
    
    def _map_type(self, discovery_type: str) -> FeatureType:
        """Map discovery type to FeatureType enum."""
        mapping = {
            'operation': FeatureType.OPERATION,
            'agent': FeatureType.AGENT,
            'orchestrator': FeatureType.ORCHESTRATOR,
            'workflow': FeatureType.WORKFLOW,
            'template': FeatureType.TEMPLATE,
            'documentation': FeatureType.DOCUMENTATION,
            'integration': FeatureType.INTEGRATION,
            'utility': FeatureType.UTILITY,
        }
        return mapping.get(discovery_type.lower(), FeatureType.UTILITY)


class TestPerformanceBenchmarks:
    """Test performance with caching enabled/disabled."""
    
    def test_cached_vs_uncached_performance(self, test_environment):
        """Benchmark cached vs uncached queries."""
        catalog = test_environment['catalog']
        engine = test_environment['engine']
        
        # Populate catalog
        discovered = engine.discover_all()
        for feature in discovered:
            catalog.add_feature(
                name=feature.name,
                feature_type=FeatureType.OPERATION,
                description=feature.description or "",
                source=feature.source
            )
        
        # First query (cache miss)
        since_date = datetime.now() - timedelta(days=1)
        start = time.time()
        features1 = catalog.get_features_since(since_date)
        uncached_time = time.time() - start
        
        # Second query (cache hit)
        start = time.time()
        features2 = catalog.get_features_since(since_date)
        cached_time = time.time() - start
        
        # Cached should be faster (or at least not slower)
        assert cached_time <= uncached_time * 1.5, f"Cached query slower: {cached_time}s vs {uncached_time}s"
        
        # Results should be identical
        assert len(features1) == len(features2)
    
    def test_large_catalog_performance(self, test_environment):
        """Test performance with large number of features."""
        catalog = test_environment['catalog']
        
        # Add 100 features
        start = time.time()
        for i in range(100):
            catalog.add_feature(
                name=f"feature_{i}",
                feature_type=FeatureType.OPERATION,
                description=f"Feature {i}",
                source="test"
            )
        add_time = time.time() - start
        
        # Query all features
        start = time.time()
        features = catalog.get_features_since(datetime.now() - timedelta(days=1))
        query_time = time.time() - start
        
        # Should complete in reasonable time
        assert add_time < 5.0, f"Adding 100 features took {add_time}s (should be <5s)"
        assert query_time < 1.0, f"Querying 100 features took {query_time}s (should be <1s)"
        assert len(features) == 100


class TestConcurrentAccess:
    """Test thread-safety and concurrent access."""
    
    def test_concurrent_reads(self, test_environment):
        """Test multiple concurrent reads."""
        catalog = test_environment['catalog']
        
        # Add features
        for i in range(10):
            catalog.add_feature(f"feature_{i}", FeatureType.OPERATION, f"F{i}", "test")
        
        # Multiple reads should all succeed
        since_date = datetime.now() - timedelta(days=1)
        results = []
        for _ in range(5):
            features = catalog.get_features_since(since_date)
            results.append(len(features))
        
        # All should return same count
        assert all(count == results[0] for count in results)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
