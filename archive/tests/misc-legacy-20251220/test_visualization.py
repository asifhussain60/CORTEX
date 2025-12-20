"""Tests for visualization modules."""

import pytest
from unittest.mock import MagicMock
from src.operations.modules.visualization import (
    DependencyGraphGenerator,
    DependencyNode,
    ArchitectureDiagramGenerator,
    ProgressVisualizer
)


class TestDependencyGraphGenerator:
    """Test suite for DependencyGraphGenerator."""
    
    @pytest.fixture
    def mock_ast_engine(self):
        """Create mock AST engine."""
        engine = MagicMock()
        engine.get_architecture_insights.return_value = {
            'dependencies': [
                {'from': 'module_a.py', 'to': 'module_b.py'},
                {'from': 'module_b.py', 'to': 'module_c.py'}
            ],
            'circular_dependencies': [
                ['module_x.py', 'module_y.py', 'module_x.py']
            ]
        }
        return engine
        
    @pytest.fixture
    def generator(self, mock_ast_engine):
        """Create generator instance."""
        return DependencyGraphGenerator(mock_ast_engine)
        
    def test_initialization(self, generator, mock_ast_engine):
        """Test generator initialization."""
        assert generator.ast_engine == mock_ast_engine
        
    def test_generate_mermaid_graph(self, generator):
        """Test Mermaid graph generation."""
        graph = generator.generate_module_graph(format="mermaid")
        
        assert "graph TD" in graph
        assert "module_a_py" in graph
        assert "module_b_py" in graph
        assert "fill:#e1f5ff" in graph  # Styling present
        
    def test_generate_dot_graph(self, generator):
        """Test DOT graph generation."""
        graph = generator.generate_module_graph(format="dot")
        
        assert "digraph Dependencies" in graph
        assert "rankdir=LR" in graph
        assert '"module_a.py" -> "module_b.py"' in graph
        
    def test_generate_json_graph(self, generator):
        """Test JSON graph generation."""
        graph = generator.generate_module_graph(format="json")
        
        assert '"from": "module_a.py"' in graph
        assert '"to": "module_b.py"' in graph
        
    def test_unsupported_format_raises_error(self, generator):
        """Test that unsupported format raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported format"):
            generator.generate_module_graph(format="invalid")
            
    def test_detect_circular_dependencies(self, generator):
        """Test circular dependency detection."""
        graph = generator.detect_circular_dependencies()
        
        assert "graph TD" in graph
        assert "CIRCULAR" in graph
        assert "stroke:red" in graph
        
    def test_detect_circular_dependencies_none(self, generator, mock_ast_engine):
        """Test circular dependency detection when none exist."""
        mock_ast_engine.get_architecture_insights.return_value = {
            'dependencies': [],
            'circular_dependencies': []
        }
        
        graph = generator.detect_circular_dependencies()
        
        assert "No Circular Dependencies Detected" in graph


class TestArchitectureDiagramGenerator:
    """Test suite for ArchitectureDiagramGenerator."""
    
    @pytest.fixture
    def mock_ast_engine(self):
        """Create mock AST engine."""
        return MagicMock()
        
    @pytest.fixture
    def generator(self, mock_ast_engine):
        """Create generator instance."""
        return ArchitectureDiagramGenerator(mock_ast_engine)
        
    def test_initialization(self, generator):
        """Test generator initialization."""
        assert 'presentation' in generator.layers
        assert 'orchestration' in generator.layers
        assert 'intelligence' in generator.layers
        assert 'infrastructure' in generator.layers
        
    def test_generate_layer_diagram(self, generator):
        """Test layered architecture diagram generation."""
        diagram = generator.generate_layer_diagram()
        
        assert "graph TB" in diagram
        assert "subgraph Presentation" in diagram
        assert "subgraph Orchestration" in diagram
        assert "CLI[CLI Interface]" in diagram
        assert "PLAN[Planning Orchestrator]" in diagram
        
    def test_generate_component_diagram_planning(self, generator):
        """Test component diagram for planning orchestrator."""
        diagram = generator.generate_component_diagram("planning_orchestrator")
        
        assert "graph TD" in diagram
        assert "CLASSIFY[Classify Tier]" in diagram
        assert "TIER1[Tier 1: Instant]" in diagram
        assert "REFACTOR[Refactor Cycle]" in diagram
        assert "classDef" in diagram
        
    def test_generate_component_diagram_unknown(self, generator):
        """Test component diagram for unknown component."""
        diagram = generator.generate_component_diagram("unknown_component")
        
        assert "graph TD" in diagram
        assert "unknown_component" in diagram.lower()
        assert "INPUT[Input]" in diagram


class TestProgressVisualizer:
    """Test suite for ProgressVisualizer."""
    
    @pytest.fixture
    def visualizer(self):
        """Create visualizer instance."""
        return ProgressVisualizer()
        
    def test_generate_progress_bar_50_percent(self, visualizer):
        """Test progress bar at 50%."""
        bar = visualizer.generate_progress_bar(5, 10, width=20)
        
        assert "[" in bar
        assert "]" in bar
        assert "50%" in bar
        assert "(5/10)" in bar
        assert "█" in bar
        assert "░" in bar
        
    def test_generate_progress_bar_zero_total(self, visualizer):
        """Test progress bar with zero total."""
        bar = visualizer.generate_progress_bar(0, 0, width=20)
        
        assert "0%" in bar
        assert "(0/0)" in bar
        
    def test_generate_progress_bar_full(self, visualizer):
        """Test progress bar at 100%."""
        bar = visualizer.generate_progress_bar(10, 10, width=20)
        
        assert "100%" in bar
        assert "(10/10)" in bar
        
    def test_generate_phase_timeline(self, visualizer):
        """Test phase timeline generation."""
        phases = [
            {'name': 'Phase 1', 'id': '1', 'status': 'complete', 'start': '08:00', 'end': '09:00'},
            {'name': 'Phase 2', 'id': '2', 'status': 'in_progress', 'start': '09:00', 'end': '10:00'},
            {'name': 'Phase 3', 'id': '3', 'status': 'pending', 'start': 'N/A', 'end': 'N/A'}
        ]
        
        timeline = visualizer.generate_phase_timeline(phases)
        
        assert "gantt" in timeline
        assert "title CORTEX Evolution" in timeline
        assert "Phase 1:done" in timeline
        assert "Phase 2:active" in timeline
        assert "Phase 3" in timeline
        
    def test_generate_metrics_chart(self, visualizer):
        """Test metrics chart generation."""
        metrics = {
            'tests_passed': 100,
            'tests_failed': 5,
            'coverage': 95
        }
        
        chart = visualizer.generate_metrics_chart(metrics)
        
        assert "Metrics Summary" in chart
        assert "tests_passed" in chart
        assert "100" in chart
        assert "█" in chart
        
    def test_generate_metrics_chart_empty(self, visualizer):
        """Test metrics chart with no numeric values."""
        metrics = {
            'status': 'complete',
            'name': 'test'
        }
        
        chart = visualizer.generate_metrics_chart(metrics)
        
        assert "No numeric metrics available" in chart
        
    def test_generate_completion_summary(self, visualizer):
        """Test completion summary generation."""
        summary = visualizer.generate_completion_summary(
            total_phases=10,
            completed_phases=7,
            in_progress_phases=1,
            pending_phases=2
        )
        
        assert "Phase Completion Summary" in summary
        assert "70%" in summary
        assert "(7/10)" in summary
        assert "Completed:" in summary and "7 phases" in summary
        assert "In Progress:" in summary and "1 phases" in summary
        assert "Pending:" in summary and "2 phases" in summary


class TestDependencyNode:
    """Test suite for DependencyNode dataclass."""
    
    def test_dependency_node_creation(self):
        """Test DependencyNode creation."""
        node = DependencyNode(
            name="test_module",
            type="module",
            file_path="/path/to/module.py",
            dependencies=["dep1", "dep2"]
        )
        
        assert node.name == "test_module"
        assert node.type == "module"
        assert node.file_path == "/path/to/module.py"
        assert len(node.dependencies) == 2
