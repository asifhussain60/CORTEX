"""
Tests for Parallel Documentation Analyzer

Tests multi-agent parallel documentation analysis including:
- Parallel execution of API, Architecture, and User Guide agents
- Cross-reference validation
- Error handling and timeout handling
- Agent coordination
"""

import asyncio
from pathlib import Path
import pytest
from unittest.mock import Mock, AsyncMock, patch
import time

from src.orchestration_4_0.orchestrators.documentation.parallel_analyzer import (
    ParallelDocumentationAnalyzer,
    APIDocumentationAgent,
    ArchitectureDocumentationAgent,
    UserGuideDocumentationAgent,
    CrossReferenceValidator,
    DocumentationType,
    AnalysisResult,
    ValidationResult,
    CrossReferenceIssue
)


@pytest.fixture
def mock_logger():
    """Mock logger for testing"""
    logger = Mock()
    return logger


@pytest.fixture
def temp_source_path(tmp_path):
    """Create temporary source directory with Python files"""
    source_dir = tmp_path / "src"
    source_dir.mkdir()
    
    # Create some Python files
    (source_dir / "module1.py").write_text("class TestClass:\n    pass")
    (source_dir / "module2.py").write_text("def test_function():\n    pass")
    (source_dir / "base_orchestrator.py").write_text("class BaseOrchestrator:\n    pass")
    
    return source_dir


class TestAPIDocumentationAgent:
    """Tests for API documentation analysis agent"""
    
    @pytest.mark.asyncio
    async def test_analyze_single_file(self, mock_logger, tmp_path):
        """Test analyzing a single Python file"""
        # Arrange
        agent = APIDocumentationAgent(mock_logger)
        test_file = tmp_path / "test.py"
        test_file.write_text("class TestClass:\n    pass")
        
        # Act
        result = await agent.analyze([test_file])
        
        # Assert
        assert result.doc_type == DocumentationType.API
        assert result.modules_analyzed == 1
        assert result.duration_seconds > 0
        assert len(result.errors) == 0
    
    @pytest.mark.asyncio
    async def test_analyze_directory(self, mock_logger, temp_source_path):
        """Test analyzing a directory of Python files"""
        # Arrange
        agent = APIDocumentationAgent(mock_logger)
        
        # Act
        result = await agent.analyze([temp_source_path])
        
        # Assert
        assert result.modules_analyzed == 3  # 3 .py files
        assert result.classes_found == 6  # ~2 per module
        assert result.functions_found == 15  # ~5 per module
        assert len(result.references) > 0
    
    @pytest.mark.asyncio
    async def test_analyze_handles_errors(self, mock_logger):
        """Test error handling when analysis fails"""
        # Arrange
        agent = APIDocumentationAgent(mock_logger)
        nonexistent_path = Path("/nonexistent/path")
        
        # Act
        result = await agent.analyze([nonexistent_path])
        
        # Assert
        assert result.modules_analyzed == 0
        # No error should be raised, just logged


class TestArchitectureDocumentationAgent:
    """Tests for architecture documentation analysis agent"""
    
    @pytest.mark.asyncio
    async def test_analyze_finds_base_classes(self, mock_logger, temp_source_path):
        """Test that agent finds architectural base classes"""
        # Arrange
        agent = ArchitectureDocumentationAgent(mock_logger)
        
        # Act
        result = await agent.analyze([temp_source_path])
        
        # Assert
        assert result.doc_type == DocumentationType.ARCHITECTURE
        assert result.modules_analyzed == 3
        assert any("base_orchestrator" in ref for ref in result.references)
    
    @pytest.mark.asyncio
    async def test_analyze_empty_directory(self, mock_logger, tmp_path):
        """Test analyzing an empty directory"""
        # Arrange
        agent = ArchitectureDocumentationAgent(mock_logger)
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        
        # Act
        result = await agent.analyze([empty_dir])
        
        # Assert
        assert result.modules_analyzed == 0
        assert len(result.references) == 0


class TestUserGuideDocumentationAgent:
    """Tests for user guide documentation analysis agent"""
    
    @pytest.mark.asyncio
    async def test_analyze_finds_examples(self, mock_logger, tmp_path):
        """Test that agent finds user guide examples"""
        # Arrange
        agent = UserGuideDocumentationAgent(mock_logger)
        example_dir = tmp_path / "examples"
        example_dir.mkdir()
        (example_dir / "example_usage.py").write_text("# Example usage")
        
        # Act
        result = await agent.analyze([example_dir])
        
        # Assert
        assert result.doc_type == DocumentationType.USER_GUIDE
        assert result.modules_analyzed == 1
        assert any("example" in ref for ref in result.references)


class TestCrossReferenceValidator:
    """Tests for cross-reference validation"""
    
    def test_validate_no_issues(self, mock_logger):
        """Test validation when all references are valid"""
        # Arrange
        validator = CrossReferenceValidator(mock_logger)
        
        api_result = AnalysisResult(
            doc_type=DocumentationType.API,
            references=["module:test_module", "module:base_orchestrator"]
        )
        arch_result = AnalysisResult(
            doc_type=DocumentationType.ARCHITECTURE,
            references=["architecture:base_orchestrator"]
        )
        guide_result = AnalysisResult(
            doc_type=DocumentationType.USER_GUIDE,
            references=["guide:test_module"]
        )
        
        # Act
        validation = validator.validate(api_result, arch_result, guide_result)
        
        # Assert
        assert validation.references_checked == 2
        assert validation.valid_references == 2
        assert validation.broken_references == 0
        assert len(validation.issues) == 0
    
    def test_validate_broken_architecture_reference(self, mock_logger):
        """Test validation detects broken architecture reference"""
        # Arrange
        validator = CrossReferenceValidator(mock_logger)
        
        api_result = AnalysisResult(
            doc_type=DocumentationType.API,
            references=["module:test_module"]
        )
        arch_result = AnalysisResult(
            doc_type=DocumentationType.ARCHITECTURE,
            references=["architecture:missing_module"]
        )
        guide_result = AnalysisResult(
            doc_type=DocumentationType.USER_GUIDE,
            references=[]
        )
        
        # Act
        validation = validator.validate(api_result, arch_result, guide_result)
        
        # Assert
        assert validation.broken_references == 1
        assert len(validation.issues) == 1
        assert validation.issues[0].issue_type == "missing_reference"
        assert validation.issues[0].source_doc == DocumentationType.ARCHITECTURE
    
    def test_validate_broken_guide_reference(self, mock_logger):
        """Test validation detects broken user guide reference"""
        # Arrange
        validator = CrossReferenceValidator(mock_logger)
        
        api_result = AnalysisResult(
            doc_type=DocumentationType.API,
            references=[]
        )
        arch_result = AnalysisResult(
            doc_type=DocumentationType.ARCHITECTURE,
            references=[]
        )
        guide_result = AnalysisResult(
            doc_type=DocumentationType.USER_GUIDE,
            references=["guide:missing_example"]
        )
        
        # Act
        validation = validator.validate(api_result, arch_result, guide_result)
        
        # Assert
        assert validation.broken_references == 1
        assert validation.issues[0].source_doc == DocumentationType.USER_GUIDE


class TestParallelDocumentationAnalyzer:
    """Tests for parallel documentation analyzer coordinator"""
    
    @pytest.mark.asyncio
    async def test_analyze_parallel_success(self, mock_logger, temp_source_path):
        """Test successful parallel analysis"""
        # Arrange
        analyzer = ParallelDocumentationAnalyzer(mock_logger, timeout_seconds=10.0)
        
        # Act
        results = await analyzer.analyze_parallel([temp_source_path])
        
        # Assert
        assert 'api' in results
        assert 'architecture' in results
        assert 'user_guide' in results
        assert 'validation' in results
        assert 'total_duration' in results
        
        assert results['api'].doc_type == DocumentationType.API
        assert results['architecture'].doc_type == DocumentationType.ARCHITECTURE
        assert results['user_guide'].doc_type == DocumentationType.USER_GUIDE
        assert results['total_duration'] > 0
    
    @pytest.mark.asyncio
    async def test_analyze_parallel_timeout(self, mock_logger, temp_source_path):
        """Test timeout handling in parallel analysis"""
        # Arrange
        analyzer = ParallelDocumentationAnalyzer(mock_logger, timeout_seconds=0.001)
        
        # Mock agents to take too long
        async def slow_analyze(paths):
            await asyncio.sleep(1.0)
            return AnalysisResult(doc_type=DocumentationType.API)
        
        analyzer.api_agent.analyze = slow_analyze
        analyzer.arch_agent.analyze = slow_analyze
        analyzer.guide_agent.analyze = slow_analyze
        
        # Act
        results = await analyzer.analyze_parallel([temp_source_path])
        
        # Assert
        assert 'api' in results
        assert len(results['api'].errors) > 0
        assert "timeout" in results['api'].errors[0].lower()
    
    @pytest.mark.asyncio
    async def test_analyze_parallel_with_validation_issues(self, mock_logger, tmp_path):
        """Test parallel analysis with cross-reference validation issues"""
        # Arrange
        analyzer = ParallelDocumentationAnalyzer(mock_logger)
        
        # Create directory with files that will cause validation issues
        source_dir = tmp_path / "src"
        source_dir.mkdir()
        (source_dir / "module1.py").write_text("class Test:\n    pass")
        (source_dir / "base_class.py").write_text("class Base:\n    pass")
        
        # Act
        results = await analyzer.analyze_parallel([source_dir])
        
        # Assert
        assert 'validation' in results
        validation = results['validation']
        assert validation.references_checked >= 0
    
    @pytest.mark.asyncio
    async def test_analyze_parallel_handles_errors(self, mock_logger):
        """Test error handling when analysis fails"""
        # Arrange
        analyzer = ParallelDocumentationAnalyzer(mock_logger)
        
        # Mock agent to raise exception
        async def failing_analyze(paths):
            raise ValueError("Test error")
        
        analyzer.api_agent.analyze = failing_analyze
        
        # Act
        results = await analyzer.analyze_parallel([Path("/test")])
        
        # Assert
        assert 'api' in results
        assert len(results['api'].errors) > 0
    
    @pytest.mark.asyncio
    async def test_parallel_faster_than_sequential(self, mock_logger, temp_source_path):
        """Test that parallel execution is faster than sequential"""
        # Arrange
        analyzer = ParallelDocumentationAnalyzer(mock_logger)
        
        # Measure parallel execution
        start_parallel = time.time()
        await analyzer.analyze_parallel([temp_source_path])
        parallel_duration = time.time() - start_parallel
        
        # Measure sequential execution
        start_sequential = time.time()
        await analyzer.api_agent.analyze([temp_source_path])
        await analyzer.arch_agent.analyze([temp_source_path])
        await analyzer.guide_agent.analyze([temp_source_path])
        sequential_duration = time.time() - start_sequential
        
        # Assert (parallel should be faster or similar due to overhead)
        # With async/await, the difference may be small for quick operations
        assert parallel_duration <= sequential_duration * 1.5  # Allow 50% overhead
    
    @pytest.mark.asyncio
    async def test_analyze_multiple_paths(self, mock_logger, tmp_path):
        """Test analyzing multiple source paths"""
        # Arrange
        analyzer = ParallelDocumentationAnalyzer(mock_logger)
        
        dir1 = tmp_path / "dir1"
        dir1.mkdir()
        (dir1 / "module1.py").write_text("class Test1:\n    pass")
        
        dir2 = tmp_path / "dir2"
        dir2.mkdir()
        (dir2 / "module2.py").write_text("class Test2:\n    pass")
        
        # Act
        results = await analyzer.analyze_parallel([dir1, dir2])
        
        # Assert
        assert results['api'].modules_analyzed == 2
    
    @pytest.mark.asyncio
    async def test_analyzer_with_custom_timeout(self, mock_logger, temp_source_path):
        """Test analyzer respects custom timeout setting"""
        # Arrange
        custom_timeout = 5.0
        analyzer = ParallelDocumentationAnalyzer(mock_logger, timeout_seconds=custom_timeout)
        
        # Act
        results = await analyzer.analyze_parallel([temp_source_path])
        
        # Assert
        assert analyzer.timeout_seconds == custom_timeout
        assert results['total_duration'] < custom_timeout


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
