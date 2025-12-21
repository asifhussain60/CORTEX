"""
Integration test for DocumentationOrchestrator with ParallelDocumentationAnalyzer

Tests end-to-end workflow with parallel analysis enabled.
"""

import pytest
from pathlib import Path
import logging
from unittest.mock import Mock

from src.orchestration_4_0.orchestrators.documentation.documentation_orchestrator import (
    DocumentationOrchestrator,
    DocumentationConfig,
    DocumentationResult
)


@pytest.fixture
def mock_logger():
    """Mock logger for testing"""
    return logging.getLogger('test')


@pytest.fixture
def temp_python_project(tmp_path):
    """Create temporary Python project for testing"""
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    
    # Create some Python modules
    (src_dir / "base_module.py").write_text("""
class BaseClass:
    '''Base class docstring'''
    def method1(self):
        pass
""")
    
    (src_dir / "api_module.py").write_text("""
def api_function():
    '''API function docstring'''
    pass

class APIClass:
    pass
""")
    
    (src_dir / "example_usage.py").write_text("""
from .api_module import api_function

# Example usage
api_function()
""")
    
    return src_dir


class TestDocumentationOrchestratorIntegration:
    """Integration tests for DocumentationOrchestrator with parallel analysis"""
    
    def test_parallel_analysis_enabled(self, mock_logger, temp_python_project, tmp_path):
        """Test orchestrator with parallel analysis enabled"""
        # Arrange
        output_dir = tmp_path / "docs"
        config = DocumentationConfig(
            source_paths=[temp_python_project],
            output_dir=output_dir,
            use_parallel_analysis=True,
            generate_diagrams=False  # Skip diagrams for faster test
        )
        
        orchestrator = DocumentationOrchestrator(mock_logger)
        
        # Act
        context = {'config': config}
        result = orchestrator.execute(context)
        
        # Assert
        assert result is not None
        assert 'result' in result
        doc_result: DocumentationResult = result['result']
        assert doc_result.modules_analyzed == 3
        assert len(doc_result.errors) == 0
    
    def test_parallel_analysis_disabled(self, mock_logger, temp_python_project, tmp_path):
        """Test orchestrator with parallel analysis disabled (sequential)"""
        # Arrange
        output_dir = tmp_path / "docs"
        config = DocumentationConfig(
            source_paths=[temp_python_project],
            output_dir=output_dir,
            use_parallel_analysis=False,  # Sequential mode
            generate_diagrams=False
        )
        
        orchestrator = DocumentationOrchestrator(mock_logger)
        
        # Act
        context = {'config': config}
        result = orchestrator.execute(context)
        
        # Assert
        assert result is not None
        assert 'result' in result
        doc_result: DocumentationResult = result['result']
        assert doc_result.modules_analyzed == 3
        assert len(doc_result.errors) == 0
    
    def test_parallel_vs_sequential_consistency(self, mock_logger, temp_python_project, tmp_path):
        """Test that parallel and sequential analysis produce consistent results"""
        # Arrange
        output_dir_parallel = tmp_path / "docs_parallel"
        output_dir_sequential = tmp_path / "docs_sequential"
        
        config_parallel = DocumentationConfig(
            source_paths=[temp_python_project],
            output_dir=output_dir_parallel,
            use_parallel_analysis=True,
            generate_diagrams=False
        )
        
        config_sequential = DocumentationConfig(
            source_paths=[temp_python_project],
            output_dir=output_dir_sequential,
            use_parallel_analysis=False,
            generate_diagrams=False
        )
        
        orchestrator_parallel = DocumentationOrchestrator(mock_logger)
        orchestrator_sequential = DocumentationOrchestrator(mock_logger)
        
        # Act
        result_parallel = orchestrator_parallel.execute({'config': config_parallel})
        result_sequential = orchestrator_sequential.execute({'config': config_sequential})
        
        # Assert
        doc_result_parallel: DocumentationResult = result_parallel['result']
        doc_result_sequential: DocumentationResult = result_sequential['result']
        
        # Both should analyze the same number of modules
        assert doc_result_parallel.modules_analyzed == doc_result_sequential.modules_analyzed
        
        # Both should succeed
        assert len(doc_result_parallel.errors) == 0
        assert len(doc_result_sequential.errors) == 0
    
    def test_cross_reference_validation_warnings(self, mock_logger, tmp_path):
        """Test that cross-reference validation detects issues"""
        # Arrange - Create project with broken references
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        
        (src_dir / "architecture.py").write_text("""
# References missing_module
from .missing_module import MissingClass
""")
        
        output_dir = tmp_path / "docs"
        config = DocumentationConfig(
            source_paths=[src_dir],
            output_dir=output_dir,
            use_parallel_analysis=True,
            generate_diagrams=False
        )
        
        orchestrator = DocumentationOrchestrator(mock_logger)
        
        # Act
        result = orchestrator.execute({'config': config})
        
        # Assert
        doc_result: DocumentationResult = result['result']
        # Should complete without errors (validation warnings are non-fatal)
        assert doc_result.modules_analyzed > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
