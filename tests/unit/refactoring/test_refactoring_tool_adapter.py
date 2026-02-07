"""
Tests for RefactoringToolAdapter base class and registry.

AC_START: AC-PHASE24.1.1-001
Description: Base adapter interface + registry foundation tests
Authority: Phase 24 - External Refactoring Tools Integration
Compliance: CORE-008 (TDD-first), CORE-011 (type hints), CORE-012 (docstrings)
"""

from __future__ import annotations

import pytest
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from cortex.brain.core.result import Result, Ok, Err


# Test fixtures and mock data
class MockLanguage(Enum):
    """Mock language for testing."""
    PYTHON = "python"
    CSHARP = "csharp"
    TYPESCRIPT = "typescript"
    JAVA = "java"


@dataclass
class MockRefactoringRequest:
    """Mock refactoring request."""
    operation: str
    file_path: Path
    language: MockLanguage
    parameters: Dict[str, Any]


@dataclass
class MockRefactoringResult:
    """Mock refactoring result."""
    success: bool
    modified_files: List[Path]
    description: str
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


class TestRefactoringToolAdapterInterface:
    """Test base adapter interface contract."""
    
    def test_adapter_has_required_abstract_methods(self):
        """Adapter interface must define abstract methods."""
        # RED: Test will fail until we create the interface
        from cortex.refactoring.adapters.base import RefactoringToolAdapter
        
        # Check abstract methods exist
        assert hasattr(RefactoringToolAdapter, 'get_supported_operations')
        assert hasattr(RefactoringToolAdapter, 'get_language')
        assert hasattr(RefactoringToolAdapter, 'is_available')
        assert hasattr(RefactoringToolAdapter, 'execute_refactoring')
        assert hasattr(RefactoringToolAdapter, 'validate_request')
    
    def test_adapter_cannot_be_instantiated_directly(self):
        """Base adapter must be abstract."""
        from cortex.refactoring.adapters.base import RefactoringToolAdapter
        
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            RefactoringToolAdapter()
    
    def test_adapter_requires_language_property(self):
        """Adapter must expose language property."""
        from cortex.refactoring.adapters.base import RefactoringToolAdapter
        from cortex.refactoring.models import RefactoringLanguage
        
        class MockAdapter(RefactoringToolAdapter):
            def get_supported_operations(self) -> List[str]:
                return ["extract_method"]
            
            def get_language(self) -> RefactoringLanguage:
                return RefactoringLanguage.PYTHON
            
            def is_available(self) -> bool:
                return True
            
            def execute_refactoring(self, request) -> Result:
                return Ok({"success": True})
            
            def validate_request(self, request) -> Result:
                return Ok(None)
        
        adapter = MockAdapter()
        assert adapter.get_language() == RefactoringLanguage.PYTHON
    
    def test_adapter_graceful_unavailability_check(self):
        """Adapter must report availability status."""
        from cortex.refactoring.adapters.base import RefactoringToolAdapter
        from cortex.refactoring.models import RefactoringLanguage
        
        class UnavailableAdapter(RefactoringToolAdapter):
            def get_supported_operations(self) -> List[str]:
                return ["extract_method"]
            
            def get_language(self) -> RefactoringLanguage:
                return RefactoringLanguage.PYTHON
            
            def is_available(self) -> bool:
                return False  # Tool not installed
            
            def execute_refactoring(self, request) -> Result:
                return Err("Tool unavailable")
            
            def validate_request(self, request) -> Result:
                return Ok(None)
        
        adapter = UnavailableAdapter()
        assert adapter.is_available() is False


class TestRefactoringToolRegistry:
    """Test adapter registry for tool discovery and routing."""
    
    def test_registry_initialization(self):
        """Registry must initialize empty."""
        # RED: Will fail until registry implemented
        from cortex.refactoring.registry import RefactoringToolRegistry
        
        registry = RefactoringToolRegistry()
        assert registry is not None
        assert registry.get_adapter_count() == 0
    
    def test_registry_register_adapter(self):
        """Registry must allow adapter registration."""
        from cortex.refactoring.registry import RefactoringToolRegistry
        from cortex.refactoring.adapters.base import RefactoringToolAdapter
        from cortex.refactoring.models import RefactoringLanguage
        
        class TestAdapter(RefactoringToolAdapter):
            def get_supported_operations(self) -> List[str]:
                return ["extract_method"]
            
            def get_language(self) -> RefactoringLanguage:
                return RefactoringLanguage.PYTHON
            
            def is_available(self) -> bool:
                return True
            
            def execute_refactoring(self, request) -> Result:
                return Ok({"success": True})
            
            def validate_request(self, request) -> Result:
                return Ok(None)
        
        registry = RefactoringToolRegistry()
        adapter = TestAdapter()
        
        result = registry.register(adapter)
        
        assert result.is_ok()
        assert registry.get_adapter_count() == 1
    
    def test_registry_get_adapter_by_language(self):
        """Registry must retrieve adapter by language."""
        from cortex.refactoring.registry import RefactoringToolRegistry
        from cortex.refactoring.adapters.base import RefactoringToolAdapter
        from cortex.refactoring.models import RefactoringLanguage
        
        class PythonAdapter(RefactoringToolAdapter):
            def get_supported_operations(self) -> List[str]:
                return ["extract_method"]
            
            def get_language(self) -> RefactoringLanguage:
                return RefactoringLanguage.PYTHON
            
            def is_available(self) -> bool:
                return True
            
            def execute_refactoring(self, request) -> Result:
                return Ok({"success": True})
            
            def validate_request(self, request) -> Result:
                return Ok(None)
        
        registry = RefactoringToolRegistry()
        adapter = PythonAdapter()
        registry.register(adapter)
        
        result = registry.get_adapter(RefactoringLanguage.PYTHON)
        
        assert result.is_ok()
        retrieved_adapter = result.unwrap()
        assert retrieved_adapter.get_language() == RefactoringLanguage.PYTHON
    
    def test_registry_handles_missing_adapter(self):
        """Registry must handle requests for unregistered languages."""
        from cortex.refactoring.registry import RefactoringToolRegistry
        from cortex.refactoring.models import RefactoringLanguage
        
        registry = RefactoringToolRegistry()
        
        result = registry.get_adapter(RefactoringLanguage.JAVA)
        
        assert result.is_err()
        assert "adapter" in result.unwrap_err().lower()
        assert "java" in result.unwrap_err().lower()
    
    def test_registry_duplicate_language_registration(self):
        """Registry must handle duplicate language registrations."""
        from cortex.refactoring.registry import RefactoringToolRegistry
        from cortex.refactoring.adapters.base import RefactoringToolAdapter
        from cortex.refactoring.models import RefactoringLanguage
        
        class PythonAdapter1(RefactoringToolAdapter):
            def get_supported_operations(self) -> List[str]:
                return ["extract_method"]
            
            def get_language(self) -> RefactoringLanguage:
                return RefactoringLanguage.PYTHON
            
            def is_available(self) -> bool:
                return True
            
            def execute_refactoring(self, request) -> Result:
                return Ok({"success": True})
            
            def validate_request(self, request) -> Result:
                return Ok(None)
        
        class PythonAdapter2(RefactoringToolAdapter):
            def get_supported_operations(self) -> List[str]:
                return ["rename"]
            
            def get_language(self) -> RefactoringLanguage:
                return RefactoringLanguage.PYTHON
            
            def is_available(self) -> bool:
                return True
            
            def execute_refactoring(self, request) -> Result:
                return Ok({"success": True})
            
            def validate_request(self, request) -> Result:
                return Ok(None)
        
        registry = RefactoringToolRegistry()
        adapter1 = PythonAdapter1()
        adapter2 = PythonAdapter2()
        
        result1 = registry.register(adapter1)
        result2 = registry.register(adapter2)
        
        assert result1.is_ok()
        assert result2.is_err()  # Should reject duplicate
        assert "already registered" in result2.unwrap_err().lower()
    
    def test_registry_list_available_languages(self):
        """Registry must list all registered languages."""
        from cortex.refactoring.registry import RefactoringToolRegistry
        from cortex.refactoring.adapters.base import RefactoringToolAdapter
        from cortex.refactoring.models import RefactoringLanguage
        
        class PythonAdapter(RefactoringToolAdapter):
            def get_supported_operations(self) -> List[str]:
                return ["extract_method"]
            
            def get_language(self) -> RefactoringLanguage:
                return RefactoringLanguage.PYTHON
            
            def is_available(self) -> bool:
                return True
            
            def execute_refactoring(self, request) -> Result:
                return Ok({"success": True})
            
            def validate_request(self, request) -> Result:
                return Ok(None)
        
        class CSharpAdapter(RefactoringToolAdapter):
            def get_supported_operations(self) -> List[str]:
                return ["extract_method"]
            
            def get_language(self) -> RefactoringLanguage:
                return RefactoringLanguage.CSHARP
            
            def is_available(self) -> bool:
                return True
            
            def execute_refactoring(self, request) -> Result:
                return Ok({"success": True})
            
            def validate_request(self, request) -> Result:
                return Ok(None)
        
        registry = RefactoringToolRegistry()
        registry.register(PythonAdapter())
        registry.register(CSharpAdapter())
        
        languages = registry.get_supported_languages()
        
        assert len(languages) == 2
        assert RefactoringLanguage.PYTHON in languages
        assert RefactoringLanguage.CSHARP in languages


class TestRefactoringModels:
    """Test data models for refactoring operations."""
    
    def test_refactoring_language_enum(self):
        """RefactoringLanguage enum must define supported languages."""
        from cortex.refactoring.models import RefactoringLanguage
        
        assert RefactoringLanguage.PYTHON
        assert RefactoringLanguage.CSHARP
        assert RefactoringLanguage.TYPESCRIPT
        assert RefactoringLanguage.JAVA
    
    def test_refactoring_request_model(self):
        """RefactoringRequest must capture operation details."""
        from cortex.refactoring.models import RefactoringRequest, RefactoringLanguage
        
        request = RefactoringRequest(
            operation="extract_method",
            file_path=Path("/tmp/test.py"),
            language=RefactoringLanguage.PYTHON,
            parameters={"start_line": 10, "end_line": 20}
        )
        
        assert request.operation == "extract_method"
        assert request.file_path == Path("/tmp/test.py")
        assert request.language == RefactoringLanguage.PYTHON
        assert request.parameters["start_line"] == 10
    
    def test_refactoring_result_model(self):
        """RefactoringResult must capture execution outcome."""
        from cortex.refactoring.models import RefactoringResult
        
        result = RefactoringResult(
            success=True,
            modified_files=[Path("/tmp/test.py")],
            description="Extracted method 'calculate'",
            warnings=["Method name might need adjustment"]
        )
        
        assert result.success is True
        assert len(result.modified_files) == 1
        assert result.description
        assert len(result.warnings) == 1


# AC_COMPLETE: AC-PHASE24.1.1-001 ✅ 12 tests created (RED phase)
