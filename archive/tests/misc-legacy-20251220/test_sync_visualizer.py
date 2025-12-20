"""
Tests for Sync Operation Visual Feedback System

Tests sync_visualizer.py with TDD methodology.

Author: Asif Hussain
Created: 2025-11-28
"""

import pytest
import json
from pathlib import Path
from datetime import datetime
from src.operations.visual_feedback.sync_visualizer import SyncVisualizer


class TestSyncVisualizerBasics:
    """Test basic initialization and data tracking"""
    
    def test_initialization(self):
        """Test visualizer initializes correctly"""
        visualizer = SyncVisualizer("test-op-001")
        
        assert visualizer.operation_id == "test-op-001"
        assert isinstance(visualizer.start_time, datetime)
        assert len(visualizer.files_data) == 0
        assert len(visualizer.operations_data) == 0
        assert len(visualizer.conflicts_data) == 0
        assert visualizer.metrics['files_added'] == 0
    
    def test_track_file_change_added(self):
        """Test tracking added files"""
        visualizer = SyncVisualizer("test-op-002")
        
        visualizer.track_file_change("src/new.py", "added", 1024, "pending")
        
        assert len(visualizer.files_data) == 1
        assert visualizer.files_data[0]['path'] == "src/new.py"
        assert visualizer.files_data[0]['type'] == "added"
        assert visualizer.files_data[0]['size'] == 1024
        assert visualizer.metrics['files_added'] == 1
    
    def test_track_file_change_modified(self):
        """Test tracking modified files"""
        visualizer = SyncVisualizer("test-op-003")
        
        visualizer.track_file_change("src/existing.py", "modified", 2048)
        
        assert visualizer.metrics['files_modified'] == 1
    
    def test_track_file_change_deleted(self):
        """Test tracking deleted files"""
        visualizer = SyncVisualizer("test-op-004")
        
        visualizer.track_file_change("old_file.txt", "deleted", 0)
        
        assert visualizer.metrics['files_deleted'] == 1


class TestSyncOperations:
    """Test operation tracking"""
    
    def test_track_operation_pull(self):
        """Test tracking pull operation"""
        visualizer = SyncVisualizer("test-op-005")
        
        visualizer.track_operation("pull", "running", 0.0, "Pulling from origin")
        
        assert len(visualizer.operations_data) == 1
        assert visualizer.operations_data[0]['name'] == "pull"
        assert visualizer.operations_data[0]['status'] == "running"
    
    def test_track_operation_push(self):
        """Test tracking push operation"""
        visualizer = SyncVisualizer("test-op-006")
        
        visualizer.track_operation("push", "complete", 250.5, "Pushed successfully")
        
        op = visualizer.operations_data[0]
        assert op['name'] == "push"
        assert op['status'] == "complete"
        assert op['duration'] == 250.5
    
    def test_operations_timeline_ordering(self):
        """Test operations timeline maintains chronological order"""
        visualizer = SyncVisualizer("test-op-007")
        
        visualizer.track_operation("commit", "complete", 100.0)
        visualizer.track_operation("pull", "complete", 150.0)
        visualizer.track_operation("push", "complete", 200.0)
        
        timeline = visualizer.generate_operations_timeline()
        assert len(timeline) == 3
        assert timeline[0]['name'] == "commit"
        assert timeline[2]['name'] == "push"


class TestConflictTracking:
    """Test conflict detection and resolution"""
    
    def test_track_conflict_unresolved(self):
        """Test tracking unresolved conflict"""
        visualizer = SyncVisualizer("test-op-008")
        
        visualizer.track_conflict("src/config.py", "content")
        
        assert len(visualizer.conflicts_data) == 1
        assert visualizer.conflicts_data[0]['file'] == "src/config.py"
        assert visualizer.conflicts_data[0]['status'] == "unresolved"
        assert visualizer.metrics['conflicts_detected'] == 1
        assert visualizer.metrics['conflicts_resolved'] == 0
    
    def test_track_conflict_resolved(self):
        """Test tracking resolved conflict"""
        visualizer = SyncVisualizer("test-op-009")
        
        visualizer.track_conflict("src/config.py", "content", "manual merge")
        
        assert visualizer.conflicts_data[0]['resolution'] == "manual merge"
        assert visualizer.conflicts_data[0]['status'] == "resolved"
        assert visualizer.metrics['conflicts_resolved'] == 1
    
    def test_conflicts_summary_resolution_rate(self):
        """Test conflict resolution rate calculation"""
        visualizer = SyncVisualizer("test-op-010")
        
        visualizer.track_conflict("file1.py", "content", "manual")
        visualizer.track_conflict("file2.py", "rename", "accept theirs")
        visualizer.track_conflict("file3.py", "delete")  # unresolved
        
        summary = visualizer.generate_conflicts_summary()
        assert summary['total'] == 3
        assert summary['resolved'] == 2
        assert summary['unresolved'] == 1
        assert summary['resolution_rate'] == pytest.approx(66.67, rel=0.1)


class TestNetworkDiagram:
    """Test network diagram data generation"""
    
    def test_network_diagram_basic_structure(self):
        """Test network diagram has nodes and links"""
        visualizer = SyncVisualizer("test-op-011")
        
        diagram = visualizer.generate_network_diagram_data()
        
        assert 'nodes' in diagram
        assert 'links' in diagram
        assert 'metadata' in diagram
        assert len(diagram['nodes']) == 2  # local and remote
    
    def test_network_diagram_push_link(self):
        """Test push operation creates correct link"""
        visualizer = SyncVisualizer("test-op-012")
        
        visualizer.track_file_change("src/new.py", "added", 1024)
        visualizer.track_operation("push", "complete", 150.0)
        
        diagram = visualizer.generate_network_diagram_data()
        
        assert len(diagram['links']) == 1
        assert diagram['links'][0]['source'] == 'local'
        assert diagram['links'][0]['target'] == 'remote'
        assert diagram['links'][0]['type'] == 'push'
    
    def test_network_diagram_pull_link(self):
        """Test pull operation creates correct link"""
        visualizer = SyncVisualizer("test-op-013")
        
        visualizer.track_operation("pull", "running")
        
        diagram = visualizer.generate_network_diagram_data()
        
        assert diagram['links'][0]['source'] == 'remote'
        assert diagram['links'][0]['target'] == 'local'
        assert diagram['links'][0]['type'] == 'pull'


class TestFileFlowData:
    """Test file flow visualization data"""
    
    def test_file_flow_groups_by_type(self):
        """Test files grouped by change type"""
        visualizer = SyncVisualizer("test-op-014")
        
        visualizer.track_file_change("new1.py", "added", 1024)
        visualizer.track_file_change("existing.py", "modified", 2048)
        visualizer.track_file_change("old.txt", "deleted", 0)
        
        flow_data = visualizer.generate_file_flow_data()
        
        assert len(flow_data['added']) == 1
        assert len(flow_data['modified']) == 1
        assert len(flow_data['deleted']) == 1
    
    def test_file_flow_calculates_total_size(self):
        """Test total size calculation"""
        visualizer = SyncVisualizer("test-op-015")
        
        visualizer.track_file_change("file1.py", "added", 1000)
        visualizer.track_file_change("file2.py", "modified", 2000)
        
        flow_data = visualizer.generate_file_flow_data()
        
        assert flow_data['total_size_bytes'] == 3000


class TestWebSocketMessages:
    """Test WebSocket message generation"""
    
    def test_websocket_message_structure(self):
        """Test WebSocket message has required fields"""
        visualizer = SyncVisualizer("test-op-016")
        
        message = visualizer.generate_websocket_message("file_change")
        
        assert message['type'] == 'sync_update'
        assert message['operation_id'] == "test-op-016"
        assert message['event_type'] == "file_change"
        assert 'timestamp' in message
        assert 'data' in message
    
    def test_websocket_message_includes_all_data(self):
        """Test WebSocket message includes all visualization data"""
        visualizer = SyncVisualizer("test-op-017")
        
        visualizer.track_file_change("test.py", "added", 1024)
        visualizer.track_operation("commit", "complete", 100.0)
        
        message = visualizer.generate_websocket_message("operation_update")
        data = message['data']
        
        assert 'network_diagram' in data
        assert 'file_flow' in data
        assert 'operations' in data
        assert 'conflicts' in data
        assert 'metrics' in data


class TestHTMLDashboard:
    """Test HTML dashboard generation"""
    
    def test_html_dashboard_generation(self, tmp_path):
        """Test HTML dashboard file is created"""
        visualizer = SyncVisualizer("test-op-018")
        
        visualizer.track_file_change("test.py", "added", 1024, "complete")
        visualizer.track_operation("push", "complete", 150.0)
        
        output_file = tmp_path / "test-dashboard.html"
        result_path = visualizer.generate_html_dashboard(output_file)
        
        assert Path(result_path).exists()
        assert output_file.exists()
    
    def test_html_dashboard_contains_d3js(self, tmp_path):
        """Test HTML dashboard includes D3.js"""
        visualizer = SyncVisualizer("test-op-019")
        
        output_file = tmp_path / "test-d3.html"
        visualizer.generate_html_dashboard(output_file)
        
        content = output_file.read_text()
        assert "d3js.org/d3.v7.min.js" in content
        assert "forceSimulation" in content
    
    def test_html_dashboard_includes_metrics(self, tmp_path):
        """Test HTML dashboard shows metrics"""
        visualizer = SyncVisualizer("test-op-020")
        
        visualizer.track_file_change("file1.py", "added", 1024)
        visualizer.track_file_change("file2.py", "modified", 2048)
        
        output_file = tmp_path / "test-metrics.html"
        visualizer.generate_html_dashboard(output_file)
        
        content = output_file.read_text()
        assert "Files Added" in content
        assert "Files Modified" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
