"""
Integration test for Task 1.1: DependencyGraph Integration

Verifies end-to-end workflow:
1. ApplicationHealthOrchestrator builds architecture graph
2. Graph data is included in analysis results
3. DashboardDataAdapter saves architecture.json

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
import json
from pathlib import Path
from src.orchestrators.application_health_orchestrator import ApplicationHealthOrchestrator
from src.operations.dashboard_data_adapter import DashboardDataAdapter


class TestTask1_1Integration:
    """Integration tests for Task 1.1 DependencyGraph integration."""
    
    @pytest.fixture
    def sample_repo(self):
        """Create a sample repository with Python files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            
            # Create Python files with imports
            (repo / "main.py").write_text("""
import utils
from data import process_data

def main():
    utils.helper()
    process_data()
""")
            
            (repo / "utils.py").write_text("""
def helper():
    return "helper"
""")
            
            (repo / "data.py").write_text("""
def process_data():
    return []
""")
            
            yield repo
    
    def test_orchestrator_includes_architecture_graph(self, sample_repo):
        """Test that ApplicationHealthOrchestrator includes architecture graph in results."""
        orchestrator = ApplicationHealthOrchestrator()
        
        # Analyze repository
        result = orchestrator.analyze(str(sample_repo), scan_level='standard')
        
        # Verify architecture_graph key exists
        assert 'architecture_graph' in result, "architecture_graph missing from analysis results"
        
        # Verify graph structure
        graph = result['architecture_graph']
        assert 'nodes' in graph
        assert 'edges' in graph
        assert 'metadata' in graph
        
        # Should have 3 nodes (main.py, utils.py, data.py)
        assert len(graph['nodes']) == 3, f"Expected 3 nodes, got {len(graph['nodes'])}"
        
        # Verify nodes have required fields
        for node in graph['nodes']:
            assert 'id' in node
            assert 'label' in node
            assert 'type' in node
            assert 'loc' in node
            assert 'language' in node
        
        # Should have edges (main.py imports utils.py and data.py)
        assert len(graph['edges']) >= 2, f"Expected at least 2 edges, got {len(graph['edges'])}"
        
        # Verify edges have required fields
        for edge in graph['edges']:
            assert 'source' in edge
            assert 'target' in edge
            assert 'weight' in edge
    
    def test_dashboard_adapter_saves_architecture_json(self, sample_repo):
        """Test that DashboardDataAdapter saves architecture.json."""
        # Create cortex-brain directory in sample repo
        brain_dir = sample_repo / "cortex-brain"
        brain_dir.mkdir()
        
        adapter = DashboardDataAdapter(sample_repo)
        
        # Generate orchestrator analysis
        orchestrator = ApplicationHealthOrchestrator()
        result = orchestrator.analyze(str(sample_repo))
        
        # Save dashboard data with architecture graph
        metadata = {"project_name": "test", "version": "1.0"}
        quality = {"score": 85, "issues": []}
        security = {"compliance": 95, "vulnerabilities": []}
        performance = {"averageLatency": 100, "metrics": []}
        architecture = result['architecture_graph']
        
        adapter.save_dashboard_data(metadata, quality, security, performance, architecture)
        
        # Verify architecture.json was created
        arch_file = adapter.dashboard_dir / "data" / "architecture.json"
        assert arch_file.exists(), f"architecture.json not found at {arch_file}"
        
        # Verify JSON is valid
        with open(arch_file, 'r') as f:
            arch_data = json.load(f)
        
        assert 'nodes' in arch_data
        assert 'edges' in arch_data
        assert len(arch_data['nodes']) == 3
    
    def test_import_accuracy_threshold(self, sample_repo):
        """Test that import detection meets 90% accuracy threshold."""
        orchestrator = ApplicationHealthOrchestrator()
        result = orchestrator.analyze(str(sample_repo))
        
        graph = result['architecture_graph']
        edges = graph['edges']
        
        # Expected imports:
        # main.py -> utils.py (1)
        # main.py -> data.py (1)
        expected_edges = {
            ('main.py', 'utils.py'),
            ('main.py', 'data.py')
        }
        
        # Check edges
        found_edges = set()
        for edge in edges:
            source = edge['source']
            target = edge['target']
            found_edges.add((source, target))
        
        # Calculate accuracy (found / expected)
        matches = len(found_edges.intersection(expected_edges))
        accuracy = (matches / len(expected_edges)) * 100
        
        assert accuracy >= 90, f"Import accuracy {accuracy}% < 90% threshold"
    
    def test_performance_target(self, sample_repo):
        """Test that graph building completes within performance target."""
        import time
        
        orchestrator = ApplicationHealthOrchestrator()
        
        # Measure analysis time
        start = time.time()
        result = orchestrator.analyze(str(sample_repo))
        duration = time.time() - start
        
        # Performance target: <1s for small repos (3 files)
        # Should be well under 1s for this tiny test
        assert duration < 1.0, f"Analysis took {duration}s, expected <1s"
        
        # Verify graph was built
        assert 'architecture_graph' in result
        assert len(result['architecture_graph']['nodes']) > 0
    
    def test_graceful_degradation_on_error(self):
        """Test that analysis continues even if graph building fails."""
        orchestrator = ApplicationHealthOrchestrator()
        
        # Analyze nonexistent path
        result = orchestrator.analyze("/nonexistent/path/xyz")
        
        # Should still have architecture_graph key (may be empty or have error)
        assert 'architecture_graph' in result
        
        # Graph should have structure even if empty
        graph = result['architecture_graph']
        assert 'nodes' in graph
        assert 'edges' in graph
