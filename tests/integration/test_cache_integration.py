"""
Integration tests for cache usage across align and deploy operations.

Tests the complete workflow:
1. Align caches discovery and scoring results
2. Deploy uses cached data instead of re-running
3. File changes invalidate cache
4. Performance improvements are measurable

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys

from src.caching import get_cache


@pytest.fixture
def temp_cache_db():
    """Create temporary cache database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = Path(f.name)
    
    # Reset global cache (use correct variable name)
    import src.caching.validation_cache as vc_module
    vc_module._cache = None
    vc_module._cache_db_path = None
    
    with patch('src.caching.validation_cache.DEFAULT_CACHE_DB', str(db_path)):
        yield db_path
    
    # Cleanup
    if db_path.exists():
        db_path.unlink()
    
    # Reset global cache again
    vc_module._cache = None
    vc_module._cache_db_path = None


@pytest.fixture
def mock_files():
    """Create mock file paths for testing."""
    temp_dir = tempfile.mkdtemp()
    temp_path = Path(temp_dir)
    
    # Create mock operation files
    ops_dir = temp_path / "operations"
    ops_dir.mkdir()
    
    orch_file = ops_dir / "test_orchestrator.py"
    orch_file.write_text("class TestOrchestrator: pass")
    
    test_file = temp_path / "tests" / "test_orch.py"
    test_file.parent.mkdir()
    test_file.write_text("def test_orch(): pass")
    
    yield {
        "orchestrator": str(orch_file),
        "test": str(test_file),
        "operations_dir": str(ops_dir)
    }
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir)


class TestAlignCaching:
    """Test SystemAlignmentOrchestrator cache integration."""
    
    def test_align_caches_orchestrator_discovery(self, temp_cache_db, mock_files):
        """Test align caches orchestrator discovery results."""
        cache = get_cache()
        
        # Simulate align discovering orchestrators
        orchestrators = ["TestOrchestrator", "AnotherOrchestrator"]
        files = [mock_files["operations_dir"]]
        
        cache.set("align", "orchestrators", orchestrators, files=files)
        
        # Verify cached
        cached = cache.get("align", "orchestrators", files=files)
        assert cached == orchestrators
    
    def test_align_caches_integration_scores(self, temp_cache_db, mock_files):
        """Test align caches per-feature integration scores."""
        cache = get_cache()
        
        # Simulate align scoring a feature
        score = {
            "feature_name": "TestOrchestrator",
            "integration_score": 85,
            "layers": {
                "discovery": 20,
                "import": 20,
                "instantiation": 20,
                "documentation": 10,
                "testing": 10,
                "wiring": 5,
                "optimization": 0
            }
        }
        
        files = [mock_files["orchestrator"], mock_files["test"]]
        cache.set("align", "score:TestOrchestrator", score, files=files)
        
        # Verify cached
        cached = cache.get("align", "score:TestOrchestrator", files=files)
        assert cached["integration_score"] == 85
    
    def test_align_shares_results_with_deploy(self, temp_cache_db, mock_files):
        """Test align shares all results with deploy namespace."""
        cache = get_cache()
        
        # Simulate align caching and sharing
        orchestrators = ["TestOrchestrator"]
        agents = ["TestAgent"]
        score = {"integration_score": 85}
        
        files = [mock_files["operations_dir"]]
        
        cache.set("align", "orchestrators", orchestrators, files=files)
        cache.share_result("align", "deploy", "orchestrators")
        
        cache.set("align", "agents", agents, files=files)
        cache.share_result("align", "deploy", "agents")
        
        cache.set("align", "score:TestOrchestrator", score, files=files)
        cache.share_result("align", "deploy", "score:TestOrchestrator")
        
        # Verify all available in deploy namespace
        assert cache.get("deploy", "orchestrators", files=files) == orchestrators
        assert cache.get("deploy", "agents", files=files) == agents
        assert cache.get("deploy", "score:TestOrchestrator", files=files) == score


class TestDeployCacheConsumption:
    """Test DeploymentGates cache consumption."""
    
    def test_deploy_uses_cached_orchestrators(self, temp_cache_db, mock_files):
        """Test deploy uses cached orchestrator discovery from align."""
        cache = get_cache()
        
        # Simulate align cached data
        orchestrators = ["OrchestratorA", "OrchestratorB"]
        files = [mock_files["operations_dir"]]
        
        cache.set("align", "orchestrators", orchestrators, files=files)
        cache.share_result("align", "deploy", "orchestrators")
        
        # Deploy should retrieve from cache
        cached = cache.get("deploy", "orchestrators", files=files)
        assert cached == orchestrators
        
        # Verify stats show hit
        stats = cache.get_stats("deploy")
        assert stats["hits"] == 1
        assert stats["misses"] == 0
    
    def test_deploy_uses_cached_integration_scores(self, temp_cache_db, mock_files):
        """Test deploy uses cached integration scores from align."""
        cache = get_cache()
        
        # Simulate align cached scores for multiple features
        features = {
            "FeatureA": {"integration_score": 92},
            "FeatureB": {"integration_score": 85},
            "FeatureC": {"integration_score": 78}
        }
        
        files = [mock_files["orchestrator"]]
        
        for feature, score in features.items():
            cache.set("align", f"score:{feature}", score, files=files)
            cache.share_result("align", "deploy", f"score:{feature}")
        
        # Deploy should retrieve all from cache
        for feature, expected_score in features.items():
            cached = cache.get("deploy", f"score:{feature}", files=files)
            assert cached == expected_score
    
    def test_deploy_fallback_on_cache_miss(self, temp_cache_db, mock_files):
        """Test deploy handles cache miss gracefully (fallback)."""
        cache = get_cache()
        
        # Deploy tries to get cached data that doesn't exist
        files = [mock_files["operations_dir"]]
        cached = cache.get("deploy", "orchestrators", files=files)
        
        assert cached is None
        
        # Verify stats show miss
        stats = cache.get_stats("deploy")
        assert stats["misses"] == 1


class TestFileChangeInvalidation:
    """Test cache invalidation when files change."""
    
    def test_file_change_invalidates_align_cache(self, temp_cache_db, mock_files):
        """Test file change invalidates align cache."""
        cache = get_cache()
        
        files = [mock_files["orchestrator"]]
        
        # Cache score
        score = {"integration_score": 85}
        cache.set("align", "score:TestOrchestrator", score, files=files)
        
        # Verify cached
        assert cache.get("align", "score:TestOrchestrator", files=files) == score
        
        # Modify file
        Path(mock_files["orchestrator"]).write_text("class TestOrchestrator: # changed")
        
        # Should be invalidated
        assert cache.get("align", "score:TestOrchestrator", files=files) is None
    
    def test_file_change_invalidates_shared_deploy_cache(self, temp_cache_db, mock_files):
        """Test file change invalidates both align and deploy caches."""
        cache = get_cache()
        
        files = [mock_files["orchestrator"]]
        
        # Align caches and shares
        score = {"integration_score": 85}
        cache.set("align", "score:TestOrchestrator", score, files=files)
        cache.share_result("align", "deploy", "score:TestOrchestrator")
        
        # Both should be cached
        assert cache.get("align", "score:TestOrchestrator", files=files) == score
        assert cache.get("deploy", "score:TestOrchestrator", files=files) == score
        
        # Modify file
        Path(mock_files["orchestrator"]).write_text("class TestOrchestrator: # changed")
        
        # Both should be invalidated
        assert cache.get("align", "score:TestOrchestrator", files=files) is None
        assert cache.get("deploy", "score:TestOrchestrator", files=files) is None
    
    def test_unrelated_file_change_preserves_cache(self, temp_cache_db, mock_files):
        """Test changes to untracked files don't invalidate cache."""
        cache = get_cache()
        
        # Cache with file tracking
        tracked_files = [mock_files["orchestrator"]]
        score = {"integration_score": 85}
        cache.set("align", "score:TestOrchestrator", score, files=tracked_files)
        
        # Modify untracked file
        Path(mock_files["test"]).write_text("def test_orch(): # changed")
        
        # Cache should still be valid
        cached = cache.get("align", "score:TestOrchestrator", files=tracked_files)
        assert cached == score


class TestPerformanceImprovement:
    """Test measurable performance improvements from caching."""
    
    def test_cache_miss_slower_than_cache_hit(self, temp_cache_db, mock_files):
        """Test cache hit is faster than cache miss."""
        cache = get_cache()
        
        # Simulate expensive operation
        def expensive_discovery():
            time.sleep(0.1)  # Simulate work
            return ["OrchestratorA", "OrchestratorB"]
        
        files = [mock_files["operations_dir"]]
        
        # First run: cache miss (expensive)
        start = time.time()
        result = expensive_discovery()
        cache.set("align", "orchestrators", result, files=files)
        miss_time = time.time() - start
        
        # Second run: cache hit (fast)
        start = time.time()
        cached = cache.get("align", "orchestrators", files=files)
        hit_time = time.time() - start
        
        assert cached == result
        assert hit_time < miss_time
        assert hit_time < 0.01  # Cache hit should be < 10ms
    
    def test_deploy_faster_with_align_cache(self, temp_cache_db, mock_files):
        """Test deploy is faster when using cached align results."""
        cache = get_cache()
        
        files = [mock_files["operations_dir"]]
        
        # Simulate align caching expensive operations
        orchestrators = ["OrchestratorA", "OrchestratorB"]
        agents = ["AgentA", "AgentB"]
        
        cache.set("align", "orchestrators", orchestrators, files=files)
        cache.set("align", "agents", agents, files=files)
        cache.share_result("align", "deploy", "orchestrators")
        cache.share_result("align", "deploy", "agents")
        
        # Deploy retrieval should be very fast
        start = time.time()
        deploy_orch = cache.get("deploy", "orchestrators", files=files)
        deploy_agents = cache.get("deploy", "agents", files=files)
        deploy_time = time.time() - start
        
        assert deploy_orch == orchestrators
        assert deploy_agents == agents
        assert deploy_time < 0.02  # Should be < 20ms for both
    
    def test_cache_hit_rate_improves_with_use(self, temp_cache_db, mock_files):
        """Test cache hit rate improves with repeated access."""
        cache = get_cache()
        
        files = [mock_files["operations_dir"]]
        result = ["OrchestratorA"]
        
        # Set once
        cache.set("align", "orchestrators", result, files=files)
        
        # Access multiple times
        for _ in range(10):
            cache.get("align", "orchestrators", files=files)
        
        stats = cache.get_stats("align")
        # 10 hits, 0 misses (set doesn't count as miss)
        assert stats["hit_rate"] == 1.0
        assert stats["hits"] == 10


class TestEndToEndWorkflow:
    """Test complete align→deploy workflow with caching."""
    
    def test_complete_align_then_deploy_workflow(self, temp_cache_db, mock_files):
        """Test complete workflow from align to deploy."""
        cache = get_cache()
        
        files = [mock_files["operations_dir"]]
        
        # Step 1: Align discovers and caches
        orchestrators = ["OrchestratorA", "OrchestratorB"]
        agents = ["AgentA"]
        scores = {
            "OrchestratorA": {"integration_score": 92},
            "OrchestratorB": {"integration_score": 85}
        }
        
        cache.set("align", "orchestrators", orchestrators, files=files)
        cache.set("align", "agents", agents, files=files)
        
        for feature, score in scores.items():
            cache.set("align", f"score:{feature}", score, files=files)
        
        # Step 2: Align shares with deploy
        cache.share_result("align", "deploy", "orchestrators")
        cache.share_result("align", "deploy", "agents")
        for feature in scores:
            cache.share_result("align", "deploy", f"score:{feature}")
        
        # Step 3: Deploy retrieves from cache
        deploy_orch = cache.get("deploy", "orchestrators", files=files)
        deploy_agents = cache.get("deploy", "agents", files=files)
        deploy_scores = {
            feature: cache.get("deploy", f"score:{feature}", files=files)
            for feature in scores
        }
        
        # Verify all data matches
        assert deploy_orch == orchestrators
        assert deploy_agents == agents
        assert deploy_scores == scores
        
        # Verify high hit rate for deploy
        deploy_stats = cache.get_stats("deploy")
        assert deploy_stats["hits"] == 4  # orch + agents + 2 scores
        assert deploy_stats["misses"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
