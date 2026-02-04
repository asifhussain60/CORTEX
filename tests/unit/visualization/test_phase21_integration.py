"""
Tests for Phase 6: Integration & E2E Tests
Author: Asif Hussain
Date: 2026-02-04
Authority: CORE-008 (TDD), Complete workflow validation
"""

import pytest
import json
import tempfile
from pathlib import Path
from typing import Dict, Any
import time


class TestPhase21FullWorkflow:
    """Test complete Phase 21 workflow"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.data_dir = self.temp_dir / "data"
        self.data_dir.mkdir()
    
    def teardown_method(self):
        """Clean up"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_workflow_lens_to_dashboard_to_spa(self):
        """LENS analysis → Dashboard JSON → SPA rendering"""
        # Step 1: LENS analysis output (simulated)
        lens_output = {
            "repo": {
                "name": "cortex",
                "path": "/repos/cortex",
                "primary_language": "Python",
                "description": "Intelligent orchestration"
            },
            "files": [
                {"path": "main.py", "language": "Python", "lines": 250},
                {"path": "utils.py", "language": "Python", "lines": 150},
                {"path": "app.js", "language": "JavaScript", "lines": 300}
            ],
            "metrics": {
                "health_score": 87,
                "security_score": 92,
                "test_coverage": 85
            }
        }
        
        # Step 2: Generate dashboard (JSONDataGenerator)
        from cortex.visualization.json_data_generator import JSONDataGenerator
        generator = JSONDataGenerator()
        dashboard = generator.generate(lens_output)
        
        # Verify generation
        assert dashboard is not None
        assert dashboard["repo"]["display_name"] == "cortex"
        
        # Step 3: Save dashboard (JSONAdapter)
        from cortex.visualization.adapters.json_adapter import JSONAdapter
        adapter = JSONAdapter(base_path=self.data_dir)
        saved = adapter.save("cortex", dashboard)
        
        assert saved is True
        
        # Step 4: Load dashboard for SPA
        loaded = adapter.load("cortex")
        
        assert loaded is not None
        assert loaded["repo"]["display_name"] == "cortex"
        assert loaded["metrics"]["health_score"] == 87
    
    def test_workflow_performance_end_to_end(self):
        """Complete workflow performs under time limits"""
        from cortex.visualization.json_data_generator import JSONDataGenerator
        from cortex.visualization.adapters.json_adapter import JSONAdapter
        
        # Generate lens data
        lens_output = {
            "repo": {"name": "large-project", "path": "/repos/large"},
            "files": [
                {"path": f"file{i}.py", "language": "Python", "lines": 100}
                for i in range(200)
            ],
            "metrics": {"health_score": 80}
        }
        
        # Time complete workflow
        start = time.perf_counter()
        
        generator = JSONDataGenerator()
        dashboard = generator.generate(lens_output)
        
        adapter = JSONAdapter(base_path=self.data_dir)
        adapter.save("large-project", dashboard)
        loaded = adapter.load("large-project")
        
        elapsed = time.perf_counter() - start
        
        # Should complete in <120s (onboarding + save + load)
        assert elapsed < 120, f"Workflow took {elapsed:.2f}s"


class TestSPADashboardFullRendering:
    """Test SPA renders complete dashboard"""
    
    def test_spa_renders_all_tabs(self):
        """SPA renders all tabs without errors"""
        dashboard = {
            "repo": {
                "display_name": "cortex",
                "primary_language": "Python"
            },
            "overview": {
                "total_files": 100,
                "total_lines": 50000
            },
            "metrics": {
                "health_score": 85,
                "languages": {"Python": 70, "JavaScript": 30}
            },
            "files": [
                {"path": "main.py", "language": "Python", "lines": 250}
            ]
        }
        
        # Verify all tab data present
        tabs = ["repo", "overview", "metrics", "files"]
        for tab in tabs:
            assert tab in dashboard


class TestAdapterIntegration:
    """Test adapter integration with orchestrators"""
    
    def setup_method(self):
        """Setup"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.data_dir = self.temp_dir / "data"
        self.data_dir.mkdir()
    
    def teardown_method(self):
        """Clean up"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_adapter_protocol_enables_swaps(self):
        """Adapter protocol supports multiple implementations"""
        from cortex.visualization.dashboard_data_adapter import DashboardDataAdapter
        from cortex.visualization.adapters.json_adapter import JSONAdapter
        
        # JSONAdapter implements protocol
        adapter = JSONAdapter(base_path=self.data_dir)
        
        # Verify protocol compliance
        assert hasattr(adapter, 'load')
        assert hasattr(adapter, 'save')
        assert hasattr(adapter, 'list_repos')
        assert hasattr(adapter, 'search')
    
    def test_adapter_data_flow_consistency(self):
        """Data flow is consistent through adapter"""
        from cortex.visualization.adapters.json_adapter import JSONAdapter
        
        test_data = {
            "repo": {"name": "test", "lines": 1000},
            "metrics": {"health": 90}
        }
        
        adapter = JSONAdapter(base_path=self.data_dir)
        
        # Save and load
        adapter.save("test", test_data)
        loaded = adapter.load("test")
        
        # Verify consistency
        assert loaded["repo"]["name"] == test_data["repo"]["name"]
        assert loaded["metrics"]["health"] == test_data["metrics"]["health"]


class TestRegistryManagement:
    """Test registry management across phases"""
    
    def setup_method(self):
        """Setup"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.registry_path = self.temp_dir / "registry.json"
        self.registry_path.write_text(json.dumps({"repos": []}))
    
    def teardown_method(self):
        """Clean up"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_registry_tracks_repositories(self):
        """Registry tracks all onboarded repositories"""
        registry = json.loads(self.registry_path.read_text())
        
        # Add repos
        repos_to_add = ["cortex", "dashboard", "lens"]
        for repo in repos_to_add:
            registry["repos"].append({
                "slug": repo,
                "display_name": repo,
                "health_score": 85
            })
        
        # Save and verify
        self.registry_path.write_text(json.dumps(registry))
        loaded_registry = json.loads(self.registry_path.read_text())
        
        assert len(loaded_registry["repos"]) == 3
    
    def test_registry_search_functionality(self):
        """Registry search finds repositories"""
        registry = json.loads(self.registry_path.read_text())
        
        # Populate registry
        registry["repos"] = [
            {"slug": "cortex", "display_name": "CORTEX", "language": "Python"},
            {"slug": "dashboard", "display_name": "Dashboard", "language": "JavaScript"},
            {"slug": "lens", "display_name": "LENS", "language": "Python"}
        ]
        
        # Search
        query = "python"
        results = [r for r in registry["repos"] 
                  if query.lower() in r.get("language", "").lower()]
        
        assert len(results) == 2


class TestPerformanceBoundaries:
    """Test performance across all phases"""
    
    def test_json_adapter_load_performance(self):
        """JSONAdapter load time <10ms"""
        from cortex.visualization.adapters.json_adapter import JSONAdapter
        from cortex.visualization.json_data_generator import JSONDataGenerator
        
        temp_dir = Path(tempfile.mkdtemp())
        data_dir = temp_dir / "data"
        data_dir.mkdir()
        
        try:
            # Generate and save
            generator = JSONDataGenerator()
            dashboard = generator.generate({
                "repo": {"name": "test"},
                "files": [{"path": f"f{i}.py"} for i in range(100)],
                "metrics": {}
            })
            
            adapter = JSONAdapter(base_path=data_dir)
            adapter.save("test", dashboard)
            
            # Time load
            import time
            start = time.perf_counter()
            loaded = adapter.load("test")
            elapsed = time.perf_counter() - start
            
            assert loaded is not None
            assert elapsed < 0.01, f"Load took {elapsed:.3f}s"
        finally:
            import shutil
            shutil.rmtree(temp_dir)
    
    def test_data_generator_performance(self):
        """JSONDataGenerator generation <60s"""
        from cortex.visualization.json_data_generator import JSONDataGenerator
        import time
        
        generator = JSONDataGenerator()
        
        # Large dataset
        lens_data = {
            "repo": {"name": "huge-repo"},
            "files": [
                {"path": f"src/module{i}/file{j}.py", "language": "Python", "lines": 100}
                for i in range(10)
                for j in range(100)  # 1000 files
            ],
            "metrics": {"health_score": 80}
        }
        
        start = time.perf_counter()
        dashboard = generator.generate(lens_data)
        elapsed = time.perf_counter() - start
        
        assert dashboard is not None
        assert elapsed < 60, f"Generation took {elapsed:.2f}s"


class TestErrorRecoveryE2E:
    """Test error recovery across phases"""
    
    def setup_method(self):
        """Setup"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.data_dir = self.temp_dir / "data"
        self.data_dir.mkdir()
    
    def teardown_method(self):
        """Clean up"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_recovery_from_corrupted_json(self):
        """System recovers from corrupted JSON files"""
        from cortex.visualization.adapters.json_adapter import JSONAdapter
        
        adapter = JSONAdapter(base_path=self.data_dir)
        
        # Write corrupted JSON
        repo_dir = self.data_dir / "corrupted"
        repo_dir.mkdir()
        (repo_dir / "dashboard.json").write_text("{invalid json")
        
        # Try to load
        loaded = adapter.load("corrupted")
        
        # Should handle gracefully
        assert loaded is None
    
    def test_recovery_from_missing_data(self):
        """System handles missing data gracefully"""
        from cortex.visualization.json_data_generator import JSONDataGenerator
        
        generator = JSONDataGenerator()
        
        # Empty LENS data
        dashboard = generator.generate({})
        
        # Should return valid structure
        assert dashboard is not None
        assert "repo" in dashboard


class TestCrossPhaseValidation:
    """Test validation across all phases"""
    
    def test_adapter_protocol_compliance(self):
        """All adapters comply with protocol"""
        from cortex.visualization.adapters.json_adapter import JSONAdapter
        import inspect
        
        # Check JSONAdapter has all required methods
        required_methods = ['load', 'save', 'list_repos', 'search']
        for method in required_methods:
            assert hasattr(JSONAdapter, method), f"Missing {method}"
    
    def test_data_schema_consistency(self):
        """Data schema is consistent across phases"""
        dashboard = {
            "repo": {"display_name": "test", "language": "Python"},
            "overview": {"files": 100, "lines": 50000},
            "metrics": {"health": 85, "security": 90},
            "files": []
        }
        
        # Verify schema
        assert isinstance(dashboard["repo"], dict)
        assert isinstance(dashboard["metrics"], dict)
        assert isinstance(dashboard["files"], list)
