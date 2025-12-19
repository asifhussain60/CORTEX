"""
Integration Tests for Enhancement Discovery Engine

Tests Git scanner, YAML scanner, codebase scanner, and feature deduplication.

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
import yaml

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from discovery.enhancement_discovery import (
    EnhancementDiscoveryEngine,
    DiscoveredFeature,
)


@pytest.fixture
def temp_repo():
    """Create temporary git repository for testing."""
    temp_dir = tempfile.mkdtemp()
    repo_path = Path(temp_dir)
    
    # Initialize git repo
    subprocess.run(['git', 'init'], cwd=repo_path, capture_output=True)
    subprocess.run(['git', 'config', 'user.name', 'Test'], cwd=repo_path, capture_output=True)
    subprocess.run(['git', 'config', 'user.email', 'test@test.com'], cwd=repo_path, capture_output=True)
    
    # Create directory structure
    (repo_path / "src" / "operations").mkdir(parents=True)
    (repo_path / "src" / "cortex_agents").mkdir(parents=True)
    (repo_path / "src" / "orchestrators").mkdir(parents=True)
    (repo_path / "cortex-brain").mkdir(parents=True)
    
    # Create test files
    (repo_path / "src" / "operations" / "test_operation.py").write_text(
        '"""Test Operation"""\nclass TestOperation:\n    pass'
    )
    (repo_path / "src" / "cortex_agents" / "test_agent.py").write_text(
        '"""Test Agent"""\nclass TestAgent:\n    pass'
    )
    (repo_path / "src" / "orchestrators" / "test_orchestrator.py").write_text(
        '"""Test Orchestrator"""\nclass TestOrchestrator:\n    pass'
    )
    
    # Create YAML config
    yaml_content = {
        'operations': {
            'test_op': {'description': 'Test operation from YAML'}
        }
    }
    (repo_path / "cortex-brain" / "capabilities.yaml").write_text(
        yaml.dump(yaml_content)
    )
    
    # Commit files
    subprocess.run(['git', 'add', '.'], cwd=repo_path, capture_output=True)
    subprocess.run(['git', 'commit', '-m', 'Initial commit'], cwd=repo_path, capture_output=True)
    
    yield repo_path
    
    # Cleanup
    shutil.rmtree(temp_dir)


class TestEnhancementDiscoveryEngine:
    """Test discovery engine initialization."""
    
    def test_engine_initialization(self, temp_repo):
        """Test engine initializes with valid repo."""
        engine = EnhancementDiscoveryEngine(temp_repo)
        assert engine.repo_root == temp_repo
    
    def test_discover_all(self, temp_repo):
        """Test full discovery across all sources."""
        engine = EnhancementDiscoveryEngine(temp_repo)
        features = engine.discover_all()
        
        # Should find at least the files we created
        assert len(features) > 0
        
        # Check we found operation
        op_features = [f for f in features if f.type == 'operation']
        assert len(op_features) > 0
        
        # Check we found agent
        agent_features = [f for f in features if f.type == 'agent']
        assert len(agent_features) > 0
        
        # Check we found orchestrator
        orch_features = [f for f in features if f.type == 'orchestrator']
        assert len(orch_features) > 0


class TestGitScanner:
    """Test Git commit history scanning."""
    
    def test_scan_git_commits(self, temp_repo):
        """Test scanning git commit history."""
        engine = EnhancementDiscoveryEngine(temp_repo)
        features = engine.scan_git_commits(days=30)
        
        # Should find features from initial commit
        assert len(features) > 0
        
        # All features should have source='git'
        for feature in features:
            assert feature.source == 'git'
    
    def test_git_scanner_date_filtering(self, temp_repo):
        """Test git scanner respects date filtering."""
        engine = EnhancementDiscoveryEngine(temp_repo)
        
        # Scan only last 0 days (should find nothing)
        features = engine.scan_git_commits(days=0)
        assert len(features) == 0


class TestYAMLScanner:
    """Test YAML configuration scanning."""
    
    def test_scan_yaml_configs(self, temp_repo):
        """Test scanning YAML configuration files."""
        engine = EnhancementDiscoveryEngine(temp_repo)
        features = engine.scan_yaml_configs()
        
        # Should find test_op from capabilities.yaml
        assert len(features) > 0
        
        # Check specific feature
        test_op = next((f for f in features if f.name == 'test_op'), None)
        assert test_op is not None
        assert test_op.description == 'Test operation from YAML'
        assert test_op.source == 'yaml'
    
    def test_yaml_scanner_missing_files(self, temp_repo):
        """Test YAML scanner handles missing files gracefully."""
        # Remove capabilities.yaml
        yaml_file = temp_repo / "cortex-brain" / "capabilities.yaml"
        yaml_file.unlink()
        
        engine = EnhancementDiscoveryEngine(temp_repo)
        features = engine.scan_yaml_configs()
        
        # Should not crash, just return empty or partial results
        assert isinstance(features, list)


class TestCodebaseScanner:
    """Test codebase file system scanning."""
    
    def test_scan_codebase(self, temp_repo):
        """Test scanning codebase for operations/agents/orchestrators."""
        engine = EnhancementDiscoveryEngine(temp_repo)
        features = engine.scan_codebase()
        
        # Should find all three types
        assert len(features) >= 3
        
        types_found = set(f.type for f in features)
        assert 'operation' in types_found
        assert 'agent' in types_found
        assert 'orchestrator' in types_found
        
        # All should have source='codebase'
        for feature in features:
            assert feature.source == 'codebase'
    
    def test_codebase_scanner_extracts_descriptions(self, temp_repo):
        """Test codebase scanner extracts docstring descriptions."""
        engine = EnhancementDiscoveryEngine(temp_repo)
        features = engine.scan_codebase()
        
        # Should extract descriptions from docstrings
        test_op = next((f for f in features if 'test_operation' in f.name.lower()), None)
        assert test_op is not None
        assert test_op.description  # Should have extracted docstring


class TestFeatureDeduplication:
    """Test feature deduplication logic."""
    
    def test_deduplicate_identical_features(self, temp_repo):
        """Test deduplication of identical features."""
        feature1 = DiscoveredFeature(
            name="duplicate",
            type="operation",
            description="Feature 1",
            source="git",
            discovered_at=datetime.now()
        )
        feature2 = DiscoveredFeature(
            name="duplicate",
            type="operation",
            description="Feature 2",
            source="yaml",
            discovered_at=datetime.now()
        )
        
        engine = EnhancementDiscoveryEngine(temp_repo)
        deduplicated = engine._deduplicate_features([feature1, feature2])
        
        # Should only have one feature
        assert len(deduplicated) == 1
        
        # Should keep most recent (feature2)
        assert deduplicated[0].description == "Feature 2"
    
    def test_different_types_not_deduplicated(self, temp_repo):
        """Test features with different types are kept separate."""
        feature1 = DiscoveredFeature(
            name="multi_type",
            type="operation",
            description="Operation",
            source="git",
            discovered_at=datetime.now()
        )
        feature2 = DiscoveredFeature(
            name="multi_type",
            type="agent",
            description="Agent",
            source="yaml",
            discovered_at=datetime.now()
        )
        
        engine = EnhancementDiscoveryEngine(temp_repo)
        deduplicated = engine._deduplicate_features([feature1, feature2])
        
        # Should keep both (different types)
        assert len(deduplicated) == 2


class TestDiscoverSince:
    """Test temporal discovery filtering."""
    
    def test_discover_since_date_filtering(self, temp_repo):
        """Test discover_since filters by date."""
        engine = EnhancementDiscoveryEngine(temp_repo)
        
        # Discover from 30 days ago (should find features)
        features_30d = engine.discover_since(datetime.now() - timedelta(days=30))
        assert len(features_30d) > 0
        
        # Discover from future (should find nothing)
        features_future = engine.discover_since(datetime.now() + timedelta(days=1))
        assert len(features_future) == 0


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_repository(self):
        """Test engine handles empty repository."""
        temp_dir = tempfile.mkdtemp()
        repo_path = Path(temp_dir)
        
        # Initialize git but don't add files
        subprocess.run(['git', 'init'], cwd=repo_path, capture_output=True)
        
        engine = EnhancementDiscoveryEngine(repo_path)
        features = engine.discover_all()
        
        # Should return empty list, not crash
        assert features == []
        
        shutil.rmtree(temp_dir)
    
    def test_non_git_repository(self):
        """Test engine handles non-git directory."""
        temp_dir = tempfile.mkdtemp()
        repo_path = Path(temp_dir)
        
        # Don't initialize git
        engine = EnhancementDiscoveryEngine(repo_path)
        
        # Git scanner should handle gracefully
        features = engine.scan_git_commits()
        assert isinstance(features, list)
        
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
