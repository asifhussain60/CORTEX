"""
Test suite for ResourceManagementOrchestrator

Tests resource monitoring, allocation policies, and performance optimization:
- CPU usage monitoring and thresholds
- Memory tracking and leak detection
- Disk usage monitoring
- Resource allocation policies for orchestrators
- Performance optimization recommendations
- Alert generation for resource constraints

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0
Feature: Orchestrator Enhancement Plan v2.0 - Feature 16
"""

import pytest
import time
from unittest.mock import patch, MagicMock
from pathlib import Path


class TestCPUMonitoring:
    """Test suite for CPU usage monitoring"""
    
    def test_get_cpu_usage_percentage(self):
        """Test getting current CPU usage percentage"""
        from src.operations.utilities.resource_management_orchestrator import ResourceManagementOrchestrator
        
        manager = ResourceManagementOrchestrator()
        
        cpu_usage = manager.get_cpu_usage()
        
        assert cpu_usage is not None
        assert isinstance(cpu_usage, float)
        assert 0.0 <= cpu_usage <= 100.0
    
    def test_cpu_usage_history_tracking(self):
        """Test tracking CPU usage history over time"""
        from src.operations.utilities.resource_management_orchestrator import ResourceManagementOrchestrator
        
        manager = ResourceManagementOrchestrator()
        
        # Record multiple readings
        for _ in range(3):
            manager.record_cpu_usage()
            time.sleep(0.1)
        
        history = manager.get_cpu_history()
        
        assert history is not None
        assert len(history) >= 3
        assert all(isinstance(reading, dict) for reading in history)
        assert all("timestamp" in reading and "cpu_percent" in reading for reading in history)
    
    def test_cpu_threshold_alert(self):
        """Test CPU threshold alert generation"""
        from src.operations.utilities.resource_management_orchestrator import ResourceManagementOrchestrator
        
        manager = ResourceManagementOrchestrator(cpu_threshold=80.0)
        
        # Mock high CPU usage
        with patch("psutil.cpu_percent", return_value=85.0):
            alert = manager.check_cpu_threshold()
            
            assert alert is not None
            assert alert["resource"] == "cpu"
            assert alert["current_value"] > manager.cpu_threshold
            assert alert["severity"] in ["warning", "critical"]


class TestMemoryTracking:
    """Test suite for memory usage tracking"""
    
    def test_get_memory_usage(self):
        """Test getting current memory usage statistics"""
        from src.operations.utilities.resource_management_orchestrator import ResourceManagementOrchestrator
        
        manager = ResourceManagementOrchestrator()
        
        memory_info = manager.get_memory_usage()
        
        assert memory_info is not None
        assert "total" in memory_info
        assert "available" in memory_info
        assert "percent" in memory_info
        assert "used" in memory_info
        assert 0.0 <= memory_info["percent"] <= 100.0
    
    def test_memory_leak_detection(self):
        """Test detecting potential memory leaks"""
        from src.operations.utilities.resource_management_orchestrator import ResourceManagementOrchestrator
        
        manager = ResourceManagementOrchestrator()
        
        # Simulate increasing memory usage
        mock_readings = [
            {"percent": 50.0, "timestamp": "2025-12-13T10:00:00"},
            {"percent": 55.0, "timestamp": "2025-12-13T10:01:00"},
            {"percent": 60.0, "timestamp": "2025-12-13T10:02:00"},
            {"percent": 65.0, "timestamp": "2025-12-13T10:03:00"},
            {"percent": 70.0, "timestamp": "2025-12-13T10:04:00"}
        ]
        
        leak_detected = manager.detect_memory_leak(mock_readings)
        
        assert isinstance(leak_detected, bool)
        # Should detect increasing trend
        assert leak_detected is True
    
    def test_memory_threshold_alert(self):
        """Test memory threshold alert generation"""
        from src.operations.utilities.resource_management_orchestrator import ResourceManagementOrchestrator
        
        manager = ResourceManagementOrchestrator(memory_threshold=75.0)
        
        # Mock high memory usage
        with patch("psutil.virtual_memory") as mock_mem:
            mock_mem.return_value = MagicMock(percent=80.0, total=16_000_000_000, available=3_200_000_000)
            
            alert = manager.check_memory_threshold()
            
            assert alert is not None
            assert alert["resource"] == "memory"
            assert alert["current_value"] > manager.memory_threshold


class TestDiskUsageMonitoring:
    """Test suite for disk usage monitoring"""
    
    def test_get_disk_usage(self):
        """Test getting disk usage for specific path"""
        from src.operations.utilities.resource_management_orchestrator import ResourceManagementOrchestrator
        
        manager = ResourceManagementOrchestrator()
        
        disk_info = manager.get_disk_usage(path="/")
        
        assert disk_info is not None
        assert "total" in disk_info
        assert "used" in disk_info
        assert "free" in disk_info
        assert "percent" in disk_info
        assert 0.0 <= disk_info["percent"] <= 100.0
    
    def test_disk_usage_multiple_paths(self):
        """Test monitoring disk usage for multiple paths"""
        from src.operations.utilities.resource_management_orchestrator import ResourceManagementOrchestrator
        
        manager = ResourceManagementOrchestrator()
        
        paths = ["/", "/tmp"]
        disk_stats = manager.get_disk_usage_multiple(paths)
        
        assert disk_stats is not None
        assert isinstance(disk_stats, dict)
        assert all(path in disk_stats for path in paths if Path(path).exists())
    
    def test_disk_threshold_alert(self):
        """Test disk threshold alert generation"""
        from src.operations.utilities.resource_management_orchestrator import ResourceManagementOrchestrator
        
        manager = ResourceManagementOrchestrator(disk_threshold=85.0)
        
        # Mock high disk usage
        with patch("psutil.disk_usage") as mock_disk:
            mock_disk.return_value = MagicMock(total=1000, used=900, free=100, percent=90.0)
            
            alert = manager.check_disk_threshold(path="/")
            
            assert alert is not None
            assert alert["resource"] == "disk"
            assert alert["current_value"] > manager.disk_threshold


class TestResourceAllocationPolicies:
    """Test suite for resource allocation policies"""
    
    def test_allocate_resources_for_orchestrator(self):
        """Test allocating resources to specific orchestrator"""
        from src.operations.utilities.resource_management_orchestrator import ResourceManagementOrchestrator
        
        manager = ResourceManagementOrchestrator()
        
        allocation = manager.allocate_resources(
            orchestrator_name="PlanningOrchestrator",
            cpu_weight=0.3,
            memory_weight=0.2
        )
        
        assert allocation is not None
        assert "orchestrator_name" in allocation
        assert "cpu_allocation" in allocation
        assert "memory_allocation" in allocation
        assert allocation["orchestrator_name"] == "PlanningOrchestrator"
    
    def test_resource_priority_levels(self):
        """Test resource allocation based on priority levels"""
        from src.operations.utilities.resource_management_orchestrator import ResourceManagementOrchestrator
        
        manager = ResourceManagementOrchestrator()
        
        # High priority orchestrator
        high_priority = manager.allocate_resources(
            orchestrator_name="CriticalOrchestrator",
            priority="high"
        )
        
        # Low priority orchestrator
        low_priority = manager.allocate_resources(
            orchestrator_name="BackgroundOrchestrator",
            priority="low"
        )
        
        assert high_priority["cpu_allocation"] > low_priority["cpu_allocation"]
    
    def test_resource_deallocation(self):
        """Test deallocating resources after orchestrator completion"""
        from src.operations.utilities.resource_management_orchestrator import ResourceManagementOrchestrator
        
        manager = ResourceManagementOrchestrator()
        
        # Allocate resources
        allocation = manager.allocate_resources(
            orchestrator_name="TempOrchestrator",
            cpu_weight=0.2,
            memory_weight=0.1
        )
        
        # Deallocate
        success = manager.deallocate_resources(orchestrator_name="TempOrchestrator")
        
        assert success is True
        
        # Verify deallocation
        allocations = manager.get_active_allocations()
        assert "TempOrchestrator" not in allocations


class TestPerformanceOptimization:
    """Test suite for performance optimization recommendations"""
    
    def test_analyze_resource_bottlenecks(self):
        """Test identifying resource bottlenecks"""
        from src.operations.utilities.resource_management_orchestrator import ResourceManagementOrchestrator
        
        manager = ResourceManagementOrchestrator()
        
        # Mock high CPU, normal memory
        with patch("psutil.cpu_percent", return_value=95.0):
            with patch("psutil.virtual_memory") as mock_mem:
                mock_mem.return_value = MagicMock(percent=45.0)
                
                bottlenecks = manager.analyze_bottlenecks()
                
                assert bottlenecks is not None
                assert isinstance(bottlenecks, list)
                assert any(b["resource"] == "cpu" for b in bottlenecks)
    
    def test_generate_optimization_recommendations(self):
        """Test generating optimization recommendations"""
        from src.operations.utilities.resource_management_orchestrator import ResourceManagementOrchestrator
        
        manager = ResourceManagementOrchestrator()
        
        # Simulate high CPU usage scenario
        bottlenecks = [
            {"resource": "cpu", "current_value": 95.0, "threshold": 80.0}
        ]
        
        recommendations = manager.generate_recommendations(bottlenecks)
        
        assert recommendations is not None
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        assert all("action" in rec for rec in recommendations)
    
    def test_auto_scaling_recommendation(self):
        """Test auto-scaling recommendations based on load"""
        from src.operations.utilities.resource_management_orchestrator import ResourceManagementOrchestrator
        
        manager = ResourceManagementOrchestrator()
        
        # Mock sustained high load
        load_history = [
            {"cpu_percent": 85.0, "memory_percent": 80.0},
            {"cpu_percent": 87.0, "memory_percent": 82.0},
            {"cpu_percent": 90.0, "memory_percent": 85.0}
        ]
        
        should_scale = manager.should_auto_scale(load_history)
        
        assert isinstance(should_scale, bool)
        assert should_scale is True  # High sustained load


class TestResourceMonitoringIntegration:
    """Test suite for integrated resource monitoring"""
    
    def test_start_monitoring_session(self):
        """Test starting a resource monitoring session"""
        from src.operations.utilities.resource_management_orchestrator import ResourceManagementOrchestrator
        
        manager = ResourceManagementOrchestrator()
        
        session_id = manager.start_monitoring_session(
            orchestrator_name="TestOrchestrator",
            interval=1.0
        )
        
        assert session_id is not None
        assert isinstance(session_id, str)
    
    def test_stop_monitoring_session(self):
        """Test stopping a monitoring session and getting report"""
        from src.operations.utilities.resource_management_orchestrator import ResourceManagementOrchestrator
        
        manager = ResourceManagementOrchestrator()
        
        session_id = manager.start_monitoring_session(
            orchestrator_name="TestOrchestrator",
            interval=0.5
        )
        
        time.sleep(1.0)  # Let it collect some data
        
        report = manager.stop_monitoring_session(session_id)
        
        assert report is not None
        assert "session_id" in report
        assert "orchestrator_name" in report
        assert "duration_seconds" in report
        assert "cpu_stats" in report
        assert "memory_stats" in report
    
    def test_get_resource_summary(self):
        """Test getting overall resource summary"""
        from src.operations.utilities.resource_management_orchestrator import ResourceManagementOrchestrator
        
        manager = ResourceManagementOrchestrator()
        
        summary = manager.get_resource_summary()
        
        assert summary is not None
        assert "cpu" in summary
        assert "memory" in summary
        assert "disk" in summary
        assert "active_allocations" in summary
        assert "alerts" in summary


class TestAlertGeneration:
    """Test suite for resource alert generation"""
    
    def test_generate_alert_for_threshold_breach(self):
        """Test generating alert when threshold is breached"""
        from src.operations.utilities.resource_management_orchestrator import ResourceManagementOrchestrator
        
        manager = ResourceManagementOrchestrator(
            cpu_threshold=80.0,
            memory_threshold=75.0,
            disk_threshold=85.0
        )
        
        alert = manager.create_alert(
            resource="cpu",
            current_value=90.0,
            threshold=80.0,
            severity="warning"
        )
        
        assert alert is not None
        assert alert["resource"] == "cpu"
        assert alert["current_value"] == 90.0
        assert alert["threshold"] == 80.0
        assert alert["severity"] == "warning"
        assert "timestamp" in alert
        assert "message" in alert
    
    def test_alert_history_tracking(self):
        """Test tracking alert history"""
        from src.operations.utilities.resource_management_orchestrator import ResourceManagementOrchestrator
        
        manager = ResourceManagementOrchestrator()
        
        # Generate multiple alerts
        manager.create_alert("cpu", 85.0, 80.0, "warning")
        manager.create_alert("memory", 80.0, 75.0, "warning")
        manager.create_alert("cpu", 95.0, 80.0, "critical")
        
        history = manager.get_alert_history()
        
        assert history is not None
        assert len(history) >= 3
        assert all("resource" in alert for alert in history)
    
    def test_clear_resolved_alerts(self):
        """Test clearing resolved alerts"""
        from src.operations.utilities.resource_management_orchestrator import ResourceManagementOrchestrator
        
        manager = ResourceManagementOrchestrator()
        
        # Create alert
        alert = manager.create_alert("cpu", 85.0, 80.0, "warning")
        
        # Clear alert
        success = manager.clear_alert(alert["alert_id"])
        
        assert success is True
        
        # Verify cleared
        active_alerts = manager.get_active_alerts()
        assert not any(a["alert_id"] == alert["alert_id"] for a in active_alerts)


class TestResourceManagerConfiguration:
    """Test suite for resource manager configuration"""
    
    def test_configure_thresholds(self):
        """Test configuring resource thresholds"""
        from src.operations.utilities.resource_management_orchestrator import ResourceManagementOrchestrator
        
        manager = ResourceManagementOrchestrator()
        
        manager.configure_thresholds(
            cpu_threshold=85.0,
            memory_threshold=80.0,
            disk_threshold=90.0
        )
        
        assert manager.cpu_threshold == 85.0
        assert manager.memory_threshold == 80.0
        assert manager.disk_threshold == 90.0
    
    def test_configure_monitoring_interval(self):
        """Test configuring monitoring interval"""
        from src.operations.utilities.resource_management_orchestrator import ResourceManagementOrchestrator
        
        manager = ResourceManagementOrchestrator()
        
        manager.configure_monitoring(interval=2.0, enabled=True)
        
        assert manager.monitoring_interval == 2.0
        assert manager.monitoring_enabled is True
    
    def test_export_configuration(self):
        """Test exporting configuration to dict"""
        from src.operations.utilities.resource_management_orchestrator import ResourceManagementOrchestrator
        
        manager = ResourceManagementOrchestrator(
            cpu_threshold=85.0,
            memory_threshold=80.0,
            disk_threshold=90.0
        )
        
        config = manager.export_configuration()
        
        assert config is not None
        assert "cpu_threshold" in config
        assert "memory_threshold" in config
        assert "disk_threshold" in config
        assert config["cpu_threshold"] == 85.0
