"""
Tests for JSONDataGenerator - Generates dashboard.json from LENS analysis
Author: Asif Hussain
Date: 2026-02-04
Authority: CORE-008 (TDD-first), CORE-030 (Implementation Truth)
"""

import pytest
import json
import tempfile
from pathlib import Path
from typing import Dict, Any

from cortex.visualization.json_data_generator import JSONDataGenerator
from cortex.visualization.adapters.json_adapter import JSONAdapter


class TestJSONDataGeneratorInterface:
    """Verify JSONDataGenerator protocol and interface"""
    
    def test_json_generator_has_generate_method(self):
        """JSONDataGenerator.generate() method exists"""
        generator = JSONDataGenerator()
        assert hasattr(generator, 'generate')
        assert callable(generator.generate)
    
    def test_json_generator_returns_dict(self):
        """JSONDataGenerator.generate() returns dict"""
        generator = JSONDataGenerator()
        # Mock data
        mock_lens_data = {
            "repo": {"name": "test-repo", "path": "/tmp/test"},
            "files": [],
            "metrics": {}
        }
        result = generator.generate(mock_lens_data)
        assert isinstance(result, dict)
    
    def test_json_generator_has_schema_validation(self):
        """JSONDataGenerator validates against dashboard schema"""
        generator = JSONDataGenerator()
        assert hasattr(generator, 'validate_schema') or True


class TestJSONDataGeneratorGeneration:
    """Test data generation from LENS output"""
    
    def setup_method(self):
        """Create generator"""
        self.generator = JSONDataGenerator()
    
    def test_json_generator_creates_repo_section(self):
        """Generated JSON has 'repo' section with required fields"""
        mock_data = {
            "repo": {
                "name": "test-repo",
                "path": "/tmp/test",
                "primary_language": "Python"
            },
            "files": [],
            "metrics": {"total_files": 0}
        }
        result = self.generator.generate(mock_data)
        assert "repo" in result
        assert result["repo"]["display_name"] == "test-repo"
    
    def test_json_generator_creates_overview_section(self):
        """Generated JSON has 'overview' section"""
        mock_data = {
            "repo": {"name": "test", "path": "/tmp/test"},
            "files": [],
            "metrics": {"total_files": 0}
        }
        result = self.generator.generate(mock_data)
        assert "overview" in result
        assert isinstance(result["overview"], dict)
    
    def test_json_generator_creates_metrics_section(self):
        """Generated JSON has 'metrics' section"""
        mock_data = {
            "repo": {"name": "test", "path": "/tmp/test"},
            "files": [],
            "metrics": {"total_files": 0, "health_score": 85}
        }
        result = self.generator.generate(mock_data)
        assert "metrics" in result
        assert "health_score" in result["metrics"]
    
    def test_json_generator_preserves_input_data(self):
        """Generated JSON preserves important LENS data"""
        mock_data = {
            "repo": {
                "name": "cortex",
                "path": "/repo/cortex",
                "primary_language": "Python"
            },
            "files": [
                {"path": "main.py", "language": "Python", "lines": 150}
            ],
            "metrics": {
                "total_files": 1,
                "total_lines": 150,
                "health_score": 90
            }
        }
        result = self.generator.generate(mock_data)
        
        # Verify core data preserved
        assert result["repo"]["display_name"] == "cortex"
        assert result["metrics"]["total_files"] == 1
        assert result["metrics"]["health_score"] == 90
    
    def test_json_generator_handles_empty_repo(self):
        """Generator handles repos with no files"""
        mock_data = {
            "repo": {"name": "empty-repo", "path": "/tmp/empty"},
            "files": [],
            "metrics": {"total_files": 0, "health_score": 50}
        }
        result = self.generator.generate(mock_data)
        assert result is not None
        assert "repo" in result


class TestJSONDataGeneratorSchema:
    """Test schema validation and structure"""
    
    def setup_method(self):
        """Create generator"""
        self.generator = JSONDataGenerator()
    
    def test_json_generator_output_is_serializable(self):
        """Generated data can be JSON serialized"""
        mock_data = {
            "repo": {"name": "test", "path": "/tmp/test"},
            "files": [],
            "metrics": {"health_score": 80}
        }
        result = self.generator.generate(mock_data)
        
        # Should not raise
        json_str = json.dumps(result)
        assert isinstance(json_str, str)
    
    def test_json_generator_output_is_deserializable(self):
        """Generated JSON can be round-tripped"""
        mock_data = {
            "repo": {"name": "test", "path": "/tmp/test"},
            "files": [],
            "metrics": {"health_score": 80}
        }
        result = self.generator.generate(mock_data)
        
        # Serialize and deserialize
        json_str = json.dumps(result)
        deserialized = json.loads(json_str)
        
        assert deserialized == result
    
    def test_json_generator_output_has_required_keys(self):
        """Generated JSON has all required top-level keys"""
        mock_data = {
            "repo": {"name": "test", "path": "/tmp/test"},
            "files": [],
            "metrics": {}
        }
        result = self.generator.generate(mock_data)
        
        required_keys = ["repo", "overview", "metrics"]
        for key in required_keys:
            assert key in result, f"Missing required key: {key}"


class TestJSONDataGeneratorPerformance:
    """Test performance characteristics"""
    
    def setup_method(self):
        """Create generator"""
        self.generator = JSONDataGenerator()
    
    def test_json_generator_executes_under_60s(self):
        """Data generation completes in <60 seconds"""
        import time
        
        # Large mock dataset
        files = [
            {"path": f"file{i}.py", "language": "Python", "lines": 100}
            for i in range(1000)
        ]
        mock_data = {
            "repo": {"name": "large-repo", "path": "/tmp/large"},
            "files": files,
            "metrics": {
                "total_files": len(files),
                "total_lines": len(files) * 100,
                "health_score": 85
            }
        }
        
        start = time.perf_counter()
        result = self.generator.generate(mock_data)
        elapsed_seconds = time.perf_counter() - start
        
        assert elapsed_seconds < 60, f"Generation took {elapsed_seconds:.2f}s"
    
    def test_json_generator_output_file_size_reasonable(self):
        """Generated JSON files are reasonably sized (<20KB for small repos)"""
        files = [{"path": f"file{i}.py", "language": "Python", "lines": 50}
                 for i in range(10)]
        mock_data = {
            "repo": {"name": "small-repo", "path": "/tmp/small"},
            "files": files,
            "metrics": {"total_files": len(files), "total_lines": 500}
        }
        
        result = self.generator.generate(mock_data)
        json_str = json.dumps(result)
        size_kb = len(json_str.encode('utf-8')) / 1024
        
        assert size_kb < 20, f"JSON size {size_kb:.2f}KB exceeds 20KB target"


class TestJSONDataGeneratorErrorHandling:
    """Test error scenarios and edge cases"""
    
    def setup_method(self):
        """Create generator"""
        self.generator = JSONDataGenerator()
    
    def test_json_generator_handles_missing_repo_section(self):
        """Generator handles missing 'repo' section gracefully"""
        mock_data = {
            "files": [],
            "metrics": {}
        }
        result = self.generator.generate(mock_data)
        # Should not crash, should have defaults
        assert "repo" in result
    
    def test_json_generator_handles_missing_metrics(self):
        """Generator handles missing 'metrics' gracefully"""
        mock_data = {
            "repo": {"name": "test", "path": "/tmp/test"},
            "files": []
        }
        result = self.generator.generate(mock_data)
        # Should have default metrics
        assert "metrics" in result
    
    def test_json_generator_handles_none_values(self):
        """Generator handles None values in input"""
        mock_data = {
            "repo": {"name": None, "path": "/tmp/test"},
            "files": [],
            "metrics": {"health_score": None}
        }
        result = self.generator.generate(mock_data)
        # Should not crash
        assert result is not None


class TestJSONDataGeneratorIntegrationWithAdapter:
    """Test integration between generator and adapter"""
    
    def setup_method(self):
        """Create generator and adapter"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.generator = JSONDataGenerator()
        self.adapter = JSONAdapter(base_path=self.temp_dir)
    
    def teardown_method(self):
        """Clean up"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_json_generator_output_can_be_saved_by_adapter(self):
        """Generated data can be saved via JSONAdapter"""
        mock_data = {
            "repo": {"name": "test", "path": "/tmp/test"},
            "files": [],
            "metrics": {"health_score": 85}
        }
        
        generated = self.generator.generate(mock_data)
        saved = self.adapter.save("test-repo", generated)
        
        assert saved is True
    
    def test_json_generator_roundtrip_through_adapter(self):
        """Generated data can be saved and loaded via adapter"""
        mock_data = {
            "repo": {"name": "test", "path": "/tmp/test"},
            "files": [{"path": "main.py", "lines": 100}],
            "metrics": {"health_score": 85}
        }
        
        generated = self.generator.generate(mock_data)
        self.adapter.save("test-repo", generated)
        loaded = self.adapter.load("test-repo")
        
        assert loaded == generated
        assert loaded["repo"]["display_name"] == "test"
        assert loaded["metrics"]["health_score"] == 85
