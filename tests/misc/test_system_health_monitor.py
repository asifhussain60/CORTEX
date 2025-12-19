"""
Tests for system health monitoring with scoring
Aggregates validation, diagnostics, and repair results into health score

TDD Phase: RED - Tests written first, expected to fail
"""

import pytest
from pathlib import Path
import tempfile
import shutil
from unittest.mock import MagicMock

from src.monitoring.system_health_monitor import (
    SystemHealthMonitor,
    HealthScore,
    HealthStatus
)


class TestSystemHealthMonitor:
    """Test system health monitoring"""
    
    @pytest.fixture
    def temp_cortex_dir(self):
        """Create temporary CORTEX directory"""
        temp_dir = tempfile.mkdtemp()
        cortex_dir = Path(temp_dir) / "CORTEX"
        cortex_dir.mkdir()
        
        yield cortex_dir
        
        shutil.rmtree(temp_dir)
    
    def test_monitor_initialization(self, temp_cortex_dir):
        """Test SystemHealthMonitor can be initialized"""
        monitor = SystemHealthMonitor(root_path=temp_cortex_dir)
        
        assert monitor is not None
        assert monitor.root_path == temp_cortex_dir
    
    def test_calculate_health_score(self, temp_cortex_dir):
        """Test health score calculation"""
        monitor = SystemHealthMonitor(root_path=temp_cortex_dir)
        score = monitor.calculate_health_score()
        
        assert isinstance(score, HealthScore)
        assert 0 <= score.overall_score <= 100
        assert score.status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED, HealthStatus.CRITICAL]
    
    def test_health_score_components(self, temp_cortex_dir):
        """Test health score includes all components"""
        monitor = SystemHealthMonitor(root_path=temp_cortex_dir)
        score = monitor.calculate_health_score()
        
        assert hasattr(score, 'validation_score')
        assert hasattr(score, 'diagnostic_score')
        assert hasattr(score, 'overall_score')
    
    def test_health_status_enum(self):
        """Test HealthStatus enum values"""
        assert HealthStatus.HEALTHY.value == "healthy"
        assert HealthStatus.DEGRADED.value == "degraded"
        assert HealthStatus.CRITICAL.value == "critical"
    
    def test_generate_health_report(self, temp_cortex_dir):
        """Test health report generation"""
        monitor = SystemHealthMonitor(root_path=temp_cortex_dir)
        score = monitor.calculate_health_score()
        report = monitor.generate_report(score)
        
        assert isinstance(report, str)
        assert "HEALTH" in report.upper()
        assert str(score.overall_score) in report
