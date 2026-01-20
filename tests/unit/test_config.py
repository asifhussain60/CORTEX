"""
Unit Tests for Configuration Loading

Tests YAML and JSON config loading functionality.
"""

import pytest

from cortex.core.config import load_yaml, load_json, load_config, save_yaml, save_json


class TestLoadYaml:
    """Tests for load_yaml function."""
    
    def test_loads_valid_yaml(self, sample_yaml_file):
        """Should successfully load valid YAML."""
        result = load_yaml(sample_yaml_file)
        
        assert result.is_ok()
        data = result.unwrap()
        assert data["name"] == "test"
        assert data["version"] == "1.0"
        assert data["settings"]["debug"] is True
    
    def test_returns_error_for_missing_file(self, temp_dir):
        """Should return Err for non-existent file."""
        result = load_yaml(temp_dir / "nonexistent.yaml")
        
        assert result.is_err()
        assert "not found" in result.error.lower()
    
    def test_returns_error_for_invalid_yaml(self, temp_dir):
        """Should return Err for invalid YAML syntax."""
        bad_yaml = temp_dir / "bad.yaml"
        bad_yaml.write_text("invalid: yaml: content: [")
        
        result = load_yaml(bad_yaml)
        
        assert result.is_err()
        assert "invalid yaml" in result.error.lower()
    
    def test_handles_empty_file(self, temp_dir):
        """Should return empty dict for empty YAML file."""
        empty_yaml = temp_dir / "empty.yaml"
        empty_yaml.write_text("")
        
        result = load_yaml(empty_yaml)
        
        assert result.is_ok()
        assert result.unwrap() == {}


class TestLoadJson:
    """Tests for load_json function."""
    
    def test_loads_valid_json(self, sample_json_file):
        """Should successfully load valid JSON."""
        result = load_json(sample_json_file)
        
        assert result.is_ok()
        data = result.unwrap()
        assert data["name"] == "test"
    
    def test_returns_error_for_missing_file(self, temp_dir):
        """Should return Err for non-existent file."""
        result = load_json(temp_dir / "nonexistent.json")
        
        assert result.is_err()
        assert "not found" in result.error.lower()
    
    def test_returns_error_for_invalid_json(self, temp_dir):
        """Should return Err for invalid JSON."""
        bad_json = temp_dir / "bad.json"
        bad_json.write_text("{invalid json")
        
        result = load_json(bad_json)
        
        assert result.is_err()
        assert "invalid json" in result.error.lower()


class TestLoadConfig:
    """Tests for load_config function."""
    
    def test_loads_yaml_by_name(self, temp_dir):
        """Should find and load YAML config by name."""
        config_dir = temp_dir / "config"
        config_dir.mkdir()
        (config_dir / "settings.yaml").write_text("key: value")
        
        result = load_config("settings", config_dir=config_dir)
        
        assert result.is_ok()
        assert result.unwrap()["key"] == "value"
    
    def test_loads_json_by_name(self, temp_dir):
        """Should find and load JSON config by name."""
        import json
        
        config_dir = temp_dir / "config"
        config_dir.mkdir()
        (config_dir / "settings.json").write_text(json.dumps({"key": "value"}))
        
        result = load_config("settings", config_dir=config_dir)
        
        assert result.is_ok()
        assert result.unwrap()["key"] == "value"
    
    def test_returns_error_when_not_found(self, temp_dir):
        """Should return Err when config not found."""
        result = load_config("nonexistent", config_dir=temp_dir)
        
        assert result.is_err()
        assert "not found" in result.error.lower()


class TestSaveYaml:
    """Tests for save_yaml function."""
    
    def test_saves_yaml_file(self, temp_dir):
        """Should save data to YAML file."""
        path = temp_dir / "output.yaml"
        data = {"name": "test", "value": 123}
        
        result = save_yaml(path, data)
        
        assert result.is_ok()
        assert path.exists()
        
        # Verify content
        loaded = load_yaml(path)
        assert loaded.unwrap() == data
    
    def test_creates_parent_directories(self, temp_dir):
        """Should create parent directories if needed."""
        path = temp_dir / "deep" / "nested" / "output.yaml"
        
        result = save_yaml(path, {"key": "value"})
        
        assert result.is_ok()
        assert path.exists()


class TestSaveJson:
    """Tests for save_json function."""
    
    def test_saves_json_file(self, temp_dir):
        """Should save data to JSON file."""
        path = temp_dir / "output.json"
        data = {"name": "test", "value": 123}
        
        result = save_json(path, data)
        
        assert result.is_ok()
        assert path.exists()
        
        # Verify content
        loaded = load_json(path)
        assert loaded.unwrap() == data
