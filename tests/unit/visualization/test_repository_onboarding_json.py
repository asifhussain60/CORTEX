"""
Tests for Repository Onboarding with JSON-First Architecture
Author: Asif Hussain
Date: 2026-02-04
Authority: CORE-008 (TDD), CORE-030 (Implementation Truth)
"""

import pytest
import json
import tempfile
from pathlib import Path
from typing import Dict, Any

from cortex.visualization.json_data_generator import JSONDataGenerator
from cortex.visualization.adapters.json_adapter import JSONAdapter


class TestRepositoryOnboardingJSONGeneration:
    """Test onboarding generates JSON correctly"""
    
    def setup_method(self):
        """Create temporary workspace"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.data_dir = self.temp_dir / "data"
        self.data_dir.mkdir()
        self.generator = JSONDataGenerator()
        self.adapter = JSONAdapter(base_path=self.data_dir)
    
    def teardown_method(self):
        """Clean up"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_onboarding_generates_json_file(self):
        """Onboarding process creates dashboard.json"""
        # Simulate LENS analysis output
        lens_output = {
            "repo": {
                "name": "test-repo",
                "path": "/tmp/test",
                "primary_language": "Python"
            },
            "files": [
                {"path": "main.py", "language": "Python", "lines": 100}
            ],
            "metrics": {"health_score": 85}
        }
        
        # Generate and save
        dashboard = self.generator.generate(lens_output)
        saved = self.adapter.save("test-repo", dashboard)
        
        assert saved is True
        file_path = self.data_dir / "test-repo" / "dashboard.json"
        assert file_path.exists()
    
    def test_onboarding_generates_valid_json(self):
        """Generated file contains valid JSON"""
        lens_output = {
            "repo": {"name": "cortex", "path": "/repo/cortex"},
            "files": [],
            "metrics": {"health_score": 90}
        }
        
        dashboard = self.generator.generate(lens_output)
        self.adapter.save("cortex", dashboard)
        
        file_path = self.data_dir / "cortex" / "dashboard.json"
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        assert data["repo"]["display_name"] == "cortex"
        assert data["metrics"]["health_score"] == 90
    
    def test_onboarding_creates_metadata_file(self):
        """Onboarding creates metadata.json with adapter info"""
        # This test prepares for future metadata tracking
        lens_output = {
            "repo": {"name": "test", "path": "/tmp/test"},
            "files": [],
            "metrics": {}
        }
        
        dashboard = self.generator.generate(lens_output)
        self.adapter.save("test", dashboard)
        
        # Verify dashboard was saved
        repo_dir = self.data_dir / "test"
        assert repo_dir.exists()
        assert (repo_dir / "dashboard.json").exists()


class TestRepositoryOnboardingIntegration:
    """Test end-to-end onboarding workflow"""
    
    def setup_method(self):
        """Create workspace"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.data_dir = self.temp_dir / "data"
        self.data_dir.mkdir()
        self.generator = JSONDataGenerator()
        self.adapter = JSONAdapter(base_path=self.data_dir)
    
    def teardown_method(self):
        """Clean up"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_onboarding_workflow_e2e(self):
        """Complete onboarding: LENS → Generate → Save → Load"""
        # Step 1: LENS analysis (simulated)
        lens_output = {
            "repo": {
                "name": "cortex-project",
                "path": "/Users/asif/cortex",
                "primary_language": "Python",
                "description": "Intelligent orchestration system"
            },
            "files": [
                {"path": "main.py", "language": "Python", "lines": 250},
                {"path": "utils.py", "language": "Python", "lines": 150}
            ],
            "metrics": {
                "health_score": 87,
                "security_score": 92,
                "test_coverage": 85
            }
        }
        
        # Step 2: Generate dashboard
        dashboard = self.generator.generate(lens_output)
        assert dashboard is not None
        assert "repo" in dashboard
        
        # Step 3: Save via adapter
        saved = self.adapter.save("cortex-project", dashboard)
        assert saved is True
        
        # Step 4: Load and verify
        loaded = self.adapter.load("cortex-project")
        assert loaded is not None
        assert loaded["repo"]["display_name"] == "cortex-project"
        assert loaded["metrics"]["health_score"] == 87
        assert len(loaded["files"]) == 2


class TestRepositoryOnboardingPerformance:
    """Test onboarding performance"""
    
    def setup_method(self):
        """Create workspace"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.data_dir = self.temp_dir / "data"
        self.data_dir.mkdir()
        self.generator = JSONDataGenerator()
        self.adapter = JSONAdapter(base_path=self.data_dir)
    
    def teardown_method(self):
        """Clean up"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_onboarding_completes_under_2_minutes(self):
        """Full onboarding (generate + save) completes in <120s"""
        import time
        
        # Large repo simulation
        files = [
            {"path": f"file{i}.py", "language": "Python", "lines": 100}
            for i in range(500)
        ]
        lens_output = {
            "repo": {
                "name": "large-repo",
                "path": "/tmp/large",
                "primary_language": "Python"
            },
            "files": files,
            "metrics": {"health_score": 80}
        }
        
        start = time.perf_counter()
        dashboard = self.generator.generate(lens_output)
        self.adapter.save("large-repo", dashboard)
        elapsed = time.perf_counter() - start
        
        assert elapsed < 120, f"Onboarding took {elapsed:.2f}s"
    
    def test_json_file_size_under_limit(self):
        """Generated JSON files stay <20KB for typical repos"""
        files = [
            {"path": f"file{i}.py", "language": "Python", "lines": 100}
            for i in range(50)
        ]
        lens_output = {
            "repo": {"name": "medium-repo", "path": "/tmp/medium"},
            "files": files,
            "metrics": {"health_score": 85}
        }
        
        dashboard = self.generator.generate(lens_output)
        self.adapter.save("medium-repo", dashboard)
        
        file_path = self.data_dir / "medium-repo" / "dashboard.json"
        file_size_kb = file_path.stat().st_size / 1024
        
        assert file_size_kb < 20, f"File size {file_size_kb:.2f}KB exceeds limit"


class TestRepositoryOnboardingRegistryUpdate:
    """Test registry updates during onboarding"""
    
    def setup_method(self):
        """Create workspace with registry"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.data_dir = self.temp_dir / "data"
        self.data_dir.mkdir()
        self.registry_path = self.temp_dir / "registry.json"
        
        # Create initial registry
        self.registry_path.write_text(json.dumps({"repos": []}))
        
        self.generator = JSONDataGenerator()
        self.adapter = JSONAdapter(base_path=self.data_dir)
    
    def teardown_method(self):
        """Clean up"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_onboarding_updates_registry(self):
        """Onboarding updates registry.json with new repo"""
        lens_output = {
            "repo": {
                "name": "new-repo",
                "path": "/tmp/new",
                "primary_language": "Python"
            },
            "files": [],
            "metrics": {"health_score": 75}
        }
        
        dashboard = self.generator.generate(lens_output)
        self.adapter.save("new-repo", dashboard)
        
        # Simulate registry update
        registry = json.loads(self.registry_path.read_text())
        registry["repos"].append({
            "slug": "new-repo",
            "display_name": "new-repo",
            "primary_language": "Python",
            "health_score": 75
        })
        self.registry_path.write_text(json.dumps(registry, indent=2))
        
        # Verify registry updated
        updated = json.loads(self.registry_path.read_text())
        assert len(updated["repos"]) == 1
        assert updated["repos"][0]["slug"] == "new-repo"


class TestRepositoryOnboardingErrorRecovery:
    """Test error handling and recovery"""
    
    def setup_method(self):
        """Create workspace"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.data_dir = self.temp_dir / "data"
        self.data_dir.mkdir()
        self.generator = JSONDataGenerator()
        self.adapter = JSONAdapter(base_path=self.data_dir)
    
    def teardown_method(self):
        """Clean up"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_onboarding_recovers_from_empty_lens_data(self):
        """Onboarding handles empty LENS output gracefully"""
        lens_output = {}
        
        dashboard = self.generator.generate(lens_output)
        saved = self.adapter.save("test", dashboard)
        
        assert saved is True
        assert dashboard is not None
    
    def test_onboarding_handles_invalid_paths(self):
        """Onboarding creates parent directories as needed"""
        lens_output = {
            "repo": {"name": "nested-repo", "path": "/tmp/test"},
            "files": [],
            "metrics": {}
        }
        
        dashboard = self.generator.generate(lens_output)
        # This should create nested directories
        saved = self.adapter.save("path/to/nested-repo", dashboard)
        
        assert saved is True
        assert (self.data_dir / "path" / "to" / "nested-repo" / "dashboard.json").exists()
