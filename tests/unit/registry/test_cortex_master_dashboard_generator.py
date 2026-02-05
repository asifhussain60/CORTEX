"""
Test suite for cortex-master dashboard generator (auto-sync system).

Tests the automatic dashboard data regeneration triggered by phase completions
and variance detection.
"""

import pytest
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
import json
import yaml


class TestCortexMasterDashboardGenerator:
    """Test cortex-master dashboard auto-sync generator."""
    
    @pytest.fixture
    def mock_registry_path(self, tmp_path):
        """Create mock registry structure."""
        registry = tmp_path / "cortex-registry" / "_cortex-master"
        registry.mkdir(parents=True)
        
        # Create index.yaml
        index_data = {
            "version": "1.0",
            "active_phases": [
                {"id": "phase-21", "number": 21, "name": "JSON-First Rewrite", "status": "in-progress", "progress": 35},
                {"id": "phase-22", "number": 22, "name": "ASK Mode", "status": "in-progress", "progress": 25},
                {"id": "phase-23", "number": 23, "name": "Static Dashboard Generator", "status": "in-progress", "progress": 60}
            ],
            "completed_phases": [
                {"id": "phase-20", "number": 20, "name": "Orchestrator Visibility", "completion_date": "2026-02-03"}
            ],
            "active_enhancements": [
                {"id": "ENH-028", "name": "Response Format Standards", "status": "implemented"}
            ],
            "dashboard": {
                "enabled": True,
                "auto_sync": True,
                "variance_threshold": 10.0,
                "sync_interval_seconds": 300
            }
        }
        
        with open(registry / "index.yaml", "w") as f:
            yaml.dump(index_data, f)
        
        # Create dashboard directory
        dashboard = registry / "dashboard" / "data"
        dashboard.mkdir(parents=True)
        
        return registry
    
    def test_generator_initialization(self, mock_registry_path):
        """Test generator initializes with registry path."""
        from cortex.registry.cortex_master_dashboard_generator import CortexMasterDashboardGenerator
        
        generator = CortexMasterDashboardGenerator(mock_registry_path)
        assert generator.registry_path == mock_registry_path
        assert generator.index_path == mock_registry_path / "index.yaml"
    
    def test_load_registry_data(self, mock_registry_path):
        """Test loading registry index.yaml."""
        from cortex.registry.cortex_master_dashboard_generator import CortexMasterDashboardGenerator
        
        generator = CortexMasterDashboardGenerator(mock_registry_path)
        data = generator.load_registry_data()
        
        assert "active_phases" in data
        assert "completed_phases" in data
        assert len(data["active_phases"]) == 3
        assert data["active_phases"][2]["progress"] == 60
    
    def test_calculate_variance_no_previous_data(self, mock_registry_path):
        """Test variance calculation when no previous data exists."""
        from cortex.registry.cortex_master_dashboard_generator import CortexMasterDashboardGenerator
        
        generator = CortexMasterDashboardGenerator(mock_registry_path)
        variance = generator.calculate_variance(previous_data=None)
        
        assert variance == 0.0  # No previous data = no variance
    
    def test_calculate_variance_with_progress_change(self, mock_registry_path):
        """Test variance calculation with phase progress changes."""
        from cortex.registry.cortex_master_dashboard_generator import CortexMasterDashboardGenerator
        
        generator = CortexMasterDashboardGenerator(mock_registry_path)
        
        previous_data = {
            "active_phases": [
                {"number": 23, "progress": 40}
            ]
        }
        
        # Current data has phase 23 at 60% (was 40%)
        variance = generator.calculate_variance(previous_data)
        
        # Variance should be > 0 (progress changed from 40 to 60)
        assert variance > 0
        assert variance <= 100  # Variance is percentage
    
    def test_calculate_variance_phase_completion(self, mock_registry_path):
        """Test variance when phase moves from active to completed."""
        from cortex.registry.cortex_master_dashboard_generator import CortexMasterDashboardGenerator
        
        generator = CortexMasterDashboardGenerator(mock_registry_path)
        
        previous_data = {
            "active_phases": [
                {"number": 20, "progress": 90},  # Phase 20 was active
                {"number": 21, "progress": 35},
                {"number": 22, "progress": 25},
                {"number": 23, "progress": 60}
            ],
            "completed_phases": []
        }
        
        # Now phase 20 is completed (moved to completed_phases in fixture)
        variance = generator.calculate_variance(previous_data)
        
        # Phase completion should register as high variance (15 points per completion)
        assert variance >= 10.0
    
    def test_generate_dashboard_data(self, mock_registry_path):
        """Test dashboard data generation."""
        from cortex.registry.cortex_master_dashboard_generator import CortexMasterDashboardGenerator
        
        generator = CortexMasterDashboardGenerator(mock_registry_path)
        dashboard_data = generator.generate_dashboard_data()
        
        assert "metadata" in dashboard_data
        assert "statistics" in dashboard_data
        assert "active_phases" in dashboard_data
        assert "completed_phases_2026" in dashboard_data  # Changed from "completed_phases"
        
        # Check metadata
        assert dashboard_data["metadata"]["version"] == "1.0.0"  # Changed from "1.0"
        assert "last_updated" in dashboard_data["metadata"]
        assert "variance_score" in dashboard_data["metadata"]
        
        # Check statistics
        assert dashboard_data["statistics"]["total_phases"] >= 3
        assert dashboard_data["statistics"]["active_phases"] == 3
    
    def test_save_dashboard_data(self, mock_registry_path):
        """Test saving dashboard data to JSON."""
        from cortex.registry.cortex_master_dashboard_generator import CortexMasterDashboardGenerator
        
        generator = CortexMasterDashboardGenerator(mock_registry_path)
        dashboard_data = generator.generate_dashboard_data()
        
        output_path = generator.save_dashboard_data(dashboard_data)
        
        assert output_path.exists()
        assert output_path.name == "plan-summary.json"
        
        # Verify JSON is valid
        with open(output_path) as f:
            loaded = json.load(f)
            assert loaded["metadata"]["version"] == "1.0.0"  # Changed from "1.0"
    
    def test_full_generation_workflow(self, mock_registry_path):
        """Test complete generation workflow."""
        from cortex.registry.cortex_master_dashboard_generator import CortexMasterDashboardGenerator
        
        generator = CortexMasterDashboardGenerator(mock_registry_path)
        result = generator.generate()
        
        assert "output_path" in result
        assert "variance_score" in result
        assert "timestamp" in result
        
        # Verify file was created
        output_path = Path(result["output_path"])
        assert output_path.exists()
    
    def test_error_handling_missing_index(self, tmp_path):
        """Test error handling when index.yaml is missing."""
        from cortex.registry.cortex_master_dashboard_generator import CortexMasterDashboardGenerator
        
        empty_registry = tmp_path / "empty-registry"
        empty_registry.mkdir()
        
        generator = CortexMasterDashboardGenerator(empty_registry)
        
        with pytest.raises(FileNotFoundError):
            generator.load_registry_data()
    
    def test_variance_threshold_detection(self, mock_registry_path):
        """Test variance threshold detection logic."""
        from cortex.registry.cortex_master_dashboard_generator import CortexMasterDashboardGenerator
        
        generator = CortexMasterDashboardGenerator(mock_registry_path)
        
        # Low variance (< 10%)
        assert not generator.should_notify_user(variance=5.2)
        
        # Medium variance (10-20%)
        assert generator.should_notify_user(variance=12.5)
        
        # High variance (> 20%) - silent sync
        assert not generator.should_notify_user(variance=25.0)  # Silent sync, no notification
