# AC_START: AC-WAVE7-TRACK2-PART2A-TESTS
# Description: Tests for Extended Refactoring Strategy with Adapter Integration

"""
Test Suite for Extended Refactoring Domain Strategy

Coverage:
- Python adapter (Rope): 8 tests
- TypeScript adapter: 6 tests
- Language routing: 4 tests
- Extended strategy integration: 5 tests
- Total: 23 tests

Pattern: TDD RED phase (comprehensive feature parity testing)
"""

import pytest
from pathlib import Path
from typing import Dict, List

from cortex.orchestrators.unified_refactoring_strategy_extended import (
    RefactoringLanguage,
    RefactoringRequest,
    RefactoringResult,
    PythonRefactoringAdapter,
    TypeScriptRefactoringAdapter,
    ExtendedRefactoringDomainStrategy,
)


# ============================================================================
# PYTHON REFACTORING ADAPTER TESTS
# ============================================================================

class TestPythonRefactoringAdapter:
    """Test suite for Python refactoring adapter."""
    
    def test_adapter_initialization(self):
        """Test Python adapter can be initialized."""
        adapter = PythonRefactoringAdapter()
        assert adapter is not None
        assert adapter.language == RefactoringLanguage.PYTHON
    
    def test_supports_python_language(self):
        """Test adapter supports Python language."""
        adapter = PythonRefactoringAdapter()
        assert adapter.supports_language(RefactoringLanguage.PYTHON)
    
    def test_does_not_support_other_languages(self):
        """Test adapter doesn't claim to support other languages."""
        adapter = PythonRefactoringAdapter()
        assert not adapter.supports_language(RefactoringLanguage.TYPESCRIPT)
        assert not adapter.supports_language(RefactoringLanguage.CSHARP)
    
    def test_get_supported_operations(self):
        """Test get supported operations for Python."""
        adapter = PythonRefactoringAdapter()
        operations = adapter.get_supported_operations()
        
        assert len(operations) == 11
        assert "rename" in operations
        assert "extract_method" in operations
        assert "extract_variable" in operations
        assert "inline" in operations
        assert "organize_imports" in operations
    
    def test_execute_rename_operation(self):
        """Test execute rename operation."""
        adapter = PythonRefactoringAdapter()
        request = RefactoringRequest(
            operation="rename",
            file_path=Path("module.py"),
            language=RefactoringLanguage.PYTHON,
            parameters={"offset": 100, "new_name": "process_data"},
        )
        
        result = adapter.execute_refactoring(request)
        
        assert result.status == "success"
        assert result.operation == "rename"
        assert result.file_path == Path("module.py")
        assert len(result.modified_files) > 0
    
    def test_execute_extract_method_operation(self):
        """Test execute extract method operation."""
        adapter = PythonRefactoringAdapter()
        request = RefactoringRequest(
            operation="extract_method",
            file_path=Path("module.py"),
            language=RefactoringLanguage.PYTHON,
            parameters={"start_offset": 100, "end_offset": 200, "new_name": "helper"},
        )
        
        result = adapter.execute_refactoring(request)
        
        assert result.status == "success"
        assert result.operation == "extract_method"
        assert "methods_created" in result.changes_summary
    
    def test_execute_unsupported_operation(self):
        """Test execute unsupported operation returns error."""
        adapter = PythonRefactoringAdapter()
        request = RefactoringRequest(
            operation="unsupported_op",
            file_path=Path("module.py"),
            language=RefactoringLanguage.PYTHON,
            parameters={},
        )
        
        result = adapter.execute_refactoring(request)
        
        assert result.status == "failed"
        assert "not supported" in result.description


# ============================================================================
# TYPESCRIPT REFACTORING ADAPTER TESTS
# ============================================================================

class TestTypeScriptRefactoringAdapter:
    """Test suite for TypeScript refactoring adapter."""
    
    def test_adapter_initialization(self):
        """Test TypeScript adapter can be initialized."""
        adapter = TypeScriptRefactoringAdapter()
        assert adapter is not None
    
    def test_supports_typescript_language(self):
        """Test adapter supports TypeScript language."""
        adapter = TypeScriptRefactoringAdapter()
        assert adapter.supports_language(RefactoringLanguage.TYPESCRIPT)
    
    def test_supports_javascript_language(self):
        """Test adapter supports JavaScript language."""
        adapter = TypeScriptRefactoringAdapter()
        assert adapter.supports_language(RefactoringLanguage.JAVASCRIPT)
    
    def test_get_supported_operations(self):
        """Test get supported operations for TypeScript."""
        adapter = TypeScriptRefactoringAdapter()
        operations = adapter.get_supported_operations()
        
        assert len(operations) == 5
        assert "rename" in operations
        assert "extract_function" in operations
        assert "extract_const" in operations
        assert "organize_imports" in operations
        assert "convert_arrow_function" in operations
    
    def test_execute_rename_operation(self):
        """Test execute rename operation."""
        adapter = TypeScriptRefactoringAdapter()
        request = RefactoringRequest(
            operation="rename",
            file_path=Path("app.ts"),
            language=RefactoringLanguage.TYPESCRIPT,
            parameters={"offset": 100, "new_name": "processData"},
        )
        
        result = adapter.execute_refactoring(request)
        
        assert result.status == "success"
        assert result.operation == "rename"
        assert result.file_path == Path("app.ts")
    
    def test_execute_extract_function_operation(self):
        """Test execute extract function operation."""
        adapter = TypeScriptRefactoringAdapter()
        request = RefactoringRequest(
            operation="extract_function",
            file_path=Path("app.ts"),
            language=RefactoringLanguage.TYPESCRIPT,
            parameters={"start_offset": 100, "end_offset": 200},
        )
        
        result = adapter.execute_refactoring(request)
        
        assert result.status == "success"
        assert result.operation == "extract_function"
        assert "functions_created" in result.changes_summary


# ============================================================================
# EXTENDED REFACTORING STRATEGY TESTS
# ============================================================================

class TestExtendedRefactoringStrategy:
    """Test suite for extended refactoring strategy."""
    
    def test_strategy_initialization(self):
        """Test strategy can be initialized."""
        strategy = ExtendedRefactoringDomainStrategy()
        assert strategy is not None
    
    def test_has_python_adapter(self):
        """Test strategy has Python adapter."""
        strategy = ExtendedRefactoringDomainStrategy()
        assert RefactoringLanguage.PYTHON in strategy.adapters
    
    def test_has_typescript_adapter(self):
        """Test strategy has TypeScript adapter."""
        strategy = ExtendedRefactoringDomainStrategy()
        assert RefactoringLanguage.TYPESCRIPT in strategy.adapters
    
    def test_get_supported_languages(self):
        """Test get supported languages."""
        strategy = ExtendedRefactoringDomainStrategy()
        languages = strategy.get_supported_languages()
        
        assert RefactoringLanguage.PYTHON in languages
        assert RefactoringLanguage.TYPESCRIPT in languages
        assert RefactoringLanguage.JAVASCRIPT in languages
    
    def test_get_all_operations(self):
        """Test get all operations by language."""
        strategy = ExtendedRefactoringDomainStrategy()
        operations = strategy.get_all_operations()
        
        assert RefactoringLanguage.PYTHON in operations
        assert RefactoringLanguage.TYPESCRIPT in operations
        assert len(operations[RefactoringLanguage.PYTHON]) == 11
        assert len(operations[RefactoringLanguage.TYPESCRIPT]) == 5
    
    def test_execute_python_refactoring(self):
        """Test execute Python refactoring via strategy."""
        strategy = ExtendedRefactoringDomainStrategy()
        request = RefactoringRequest(
            operation="rename",
            file_path=Path("module.py"),
            language=RefactoringLanguage.PYTHON,
            parameters={"offset": 100, "new_name": "new_name"},
        )
        
        result = strategy.execute_refactoring(request)
        
        assert result.status == "success"
        assert result.operation == "rename"
        assert result.file_path == Path("module.py")
    
    def test_execute_typescript_refactoring(self):
        """Test execute TypeScript refactoring via strategy."""
        strategy = ExtendedRefactoringDomainStrategy()
        request = RefactoringRequest(
            operation="extract_function",
            file_path=Path("app.ts"),
            language=RefactoringLanguage.TYPESCRIPT,
            parameters={},
        )
        
        result = strategy.execute_refactoring(request)
        
        assert result.status == "success"
        assert result.operation == "extract_function"
    
    def test_execute_javascript_refactoring(self):
        """Test execute JavaScript refactoring via strategy."""
        strategy = ExtendedRefactoringDomainStrategy()
        request = RefactoringRequest(
            operation="rename",
            file_path=Path("app.js"),
            language=RefactoringLanguage.JAVASCRIPT,
            parameters={},
        )
        
        result = strategy.execute_refactoring(request)
        
        assert result.status == "success"
    
    def test_unsupported_language_returns_error(self):
        """Test unsupported language returns error."""
        strategy = ExtendedRefactoringDomainStrategy()
        request = RefactoringRequest(
            operation="rename",
            file_path=Path("file.cs"),
            language=RefactoringLanguage.CSHARP,
            parameters={},
        )
        
        result = strategy.execute_refactoring(request)
        
        assert result.status == "failed"
        assert "not supported" in result.description


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestRefactoringStrategyIntegration:
    """Integration tests for refactoring strategy."""
    
    def test_all_python_operations_supported(self):
        """Test all Python operations can be executed."""
        strategy = ExtendedRefactoringDomainStrategy()
        adapter = strategy.adapters[RefactoringLanguage.PYTHON]
        operations = adapter.get_supported_operations()
        
        for operation in operations:
            request = RefactoringRequest(
                operation=operation,
                file_path=Path("module.py"),
                language=RefactoringLanguage.PYTHON,
                parameters={},
            )
            
            result = adapter.execute_refactoring(request)
            assert result.status == "success", f"Operation {operation} failed"
    
    def test_all_typescript_operations_supported(self):
        """Test all TypeScript operations can be executed."""
        strategy = ExtendedRefactoringDomainStrategy()
        adapter = strategy.adapters[RefactoringLanguage.TYPESCRIPT]
        operations = adapter.get_supported_operations()
        
        for operation in operations:
            request = RefactoringRequest(
                operation=operation,
                file_path=Path("app.ts"),
                language=RefactoringLanguage.TYPESCRIPT,
                parameters={},
            )
            
            result = adapter.execute_refactoring(request)
            assert result.status == "success", f"Operation {operation} failed"
    
    def test_refactoring_result_contains_metadata(self):
        """Test refactoring result contains expected metadata."""
        strategy = ExtendedRefactoringDomainStrategy()
        request = RefactoringRequest(
            operation="rename",
            file_path=Path("module.py"),
            language=RefactoringLanguage.PYTHON,
            parameters={},
        )
        
        result = strategy.execute_refactoring(request)
        
        assert result.status is not None
        assert result.operation is not None
        assert result.file_path is not None
        assert result.description is not None
        assert isinstance(result.changes_summary, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

# AC_COMPLETE: AC-WAVE7-TRACK2-PART2A-TESTS ✅
# 23 test cases for extended refactoring strategy
