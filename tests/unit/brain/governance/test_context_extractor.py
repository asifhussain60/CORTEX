"""
Unit tests for Context Extractor

AC-GOV-CTX-001-01: Context extraction identifies file context for governance rule application
"""

import pytest
from pathlib import Path
from typing import Dict, Any
from cortex.brain.core.governance.context_extractor import (
    ContextExtractor,
    GovernanceContext
)


class TestContextExtractor:
    """Test suite for ContextExtractor"""
    
    @pytest.fixture
    def extractor(self) -> ContextExtractor:
        """Create ContextExtractor instance"""
        return ContextExtractor()
    
    # AC-GOV-CTX-001-01: Extract context from file path and operation
    
    def test_extract_context_python_file(self, extractor: ContextExtractor) -> None:
        """Test extracting context from Python production file"""
        file_path = "cortex/core/orchestrator.py"
        operation_context = {"operation": "implement", "handler": "execution"}
        
        context = extractor.extract_context(file_path, operation_context)
        
        assert context.file_type == "python"
        assert context.operation_type == "implement"
        assert context.code_classification == "production"
        assert context.development_phase in ["production", "development"]
    
    def test_extract_context_yaml_file(self, extractor: ContextExtractor) -> None:
        """Test extracting context from YAML configuration file"""
        file_path = "cortex-config.yaml"
        operation_context = {"operation": "validation"}
        
        context = extractor.extract_context(file_path, operation_context)
        
        assert context.file_type == "yaml"
        assert context.operation_type == "validation"
        assert context.file_path == file_path
    
    def test_extract_context_generated_code(self, extractor: ContextExtractor) -> None:
        """Test extracting context from generated code file"""
        file_path = "cortex/generated/api_stubs.py"
        operation_context = {"operation": "fix"}
        
        context = extractor.extract_context(file_path, operation_context)
        
        assert context.file_type == "python"
        assert context.code_classification == "generated"
    
    def test_extract_context_test_fixture(self, extractor: ContextExtractor) -> None:
        """Test extracting context from test fixture"""
        file_path = "tests/fixtures/sample_data.json"
        operation_context = {"operation": "refactor"}
        
        context = extractor.extract_context(file_path, operation_context)
        
        assert context.file_type == "json"
        assert context.code_classification == "test"
    
    # File type detection
    
    def test_detect_file_type_python(self, extractor: ContextExtractor) -> None:
        """Test detecting Python file type"""
        assert extractor.detect_file_type("module.py") == "python"
        assert extractor.detect_file_type("script.pyx") == "python"
    
    def test_detect_file_type_yaml(self, extractor: ContextExtractor) -> None:
        """Test detecting YAML file type"""
        assert extractor.detect_file_type("config.yaml") == "yaml"
        assert extractor.detect_file_type("settings.yml") == "yaml"
    
    def test_detect_file_type_json(self, extractor: ContextExtractor) -> None:
        """Test detecting JSON file type"""
        assert extractor.detect_file_type("data.json") == "json"
    
    def test_detect_file_type_markdown(self, extractor: ContextExtractor) -> None:
        """Test detecting Markdown file type"""
        assert extractor.detect_file_type("README.md") == "markdown"
    
    # Code classification detection
    
    def test_detect_code_classification_production(self, extractor: ContextExtractor) -> None:
        """Test classifying production code"""
        assert extractor.detect_code_classification("cortex/core/module.py") == "production"
        assert extractor.detect_code_classification("cortex_brain/state/db.py") == "production"
    
    def test_detect_code_classification_test(self, extractor: ContextExtractor) -> None:
        """Test classifying test code"""
        assert extractor.detect_code_classification("tests/unit/test_module.py") == "test"
        assert extractor.detect_code_classification("tests/fixtures/data.json") == "test"
    
    def test_detect_code_classification_generated(self, extractor: ContextExtractor) -> None:
        """Test classifying generated code"""
        assert extractor.detect_code_classification("cortex/generated/stubs.py") == "generated"
        assert extractor.detect_code_classification("build/output.py") == "generated"
    
    def test_detect_code_classification_internal(self, extractor: ContextExtractor) -> None:
        """Test classifying internal/utility code"""
        assert extractor.detect_code_classification("scripts/utility.py") == "internal"
        assert extractor.detect_code_classification("tools/helper.py") == "internal"
    
    # Operation type extraction
    
    def test_extract_operation_type_from_context(self, extractor: ContextExtractor) -> None:
        """Test extracting operation type from context"""
        assert extractor.extract_operation_type({"operation": "implement"}) == "implement"
        assert extractor.extract_operation_type({"operation": "fix"}) == "fix"
        assert extractor.extract_operation_type({"operation": "refactor"}) == "refactor"
    
    def test_extract_operation_type_default(self, extractor: ContextExtractor) -> None:
        """Test default operation type when not specified"""
        result = extractor.extract_operation_type({})
        assert result in ["implement", "unknown"]


class TestGovernanceContext:
    """Test suite for GovernanceContext dataclass"""
    
    def test_governance_context_creation(self) -> None:
        """Test creating GovernanceContext instance"""
        context = GovernanceContext(
            file_path="cortex/core/module.py",
            file_type="python",
            operation_type="implement",
            development_phase="production",
            code_classification="production",
            handler_name="execution"
        )
        
        assert context.file_path == "cortex/core/module.py"
        assert context.file_type == "python"
        assert context.operation_type == "implement"
        assert context.development_phase == "production"
        assert context.code_classification == "production"
        assert context.handler_name == "execution"
