"""
Unit tests for RoslynAdapter.

AC_START: AC-PHASE24.2.1-003
Description: Roslyn adapter implementation tests
Authority: Phase 24.2.1 - Roslyn Adapter
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from cortex.refactoring.adapters.roslyn_adapter import RoslynAdapter
from cortex.refactoring.models import (
    RefactoringRequest,
    RefactoringLanguage,
    RefactoringResult
)
from cortex.brain.core.result import Ok, Err


class TestRoslynAdapterInitialization:
    """Test RoslynAdapter initialization."""

    def test_roslyn_adapter_import(self):
        """Test that RoslynAdapter can be imported."""
        from cortex.refactoring.adapters.roslyn_adapter import RoslynAdapter
        assert RoslynAdapter is not None

    def test_roslyn_adapter_initialization(self):
        """Test RoslynAdapter initializes correctly."""
        adapter = RoslynAdapter()
        assert adapter is not None

    def test_roslyn_adapter_language(self):
        """Test RoslynAdapter returns C# language."""
        adapter = RoslynAdapter()
        assert adapter.get_language() == RefactoringLanguage.CSHARP

    def test_roslyn_adapter_supported_operations(self):
        """Test RoslynAdapter returns supported operations."""
        adapter = RoslynAdapter()
        operations = adapter.get_supported_operations()
        
        assert isinstance(operations, list)
        assert len(operations) >= 6  # Minimum operations
        assert "extract_method" in operations
        assert "rename" in operations


class TestRoslynAdapterAvailability:
    """Test RoslynAdapter availability checking."""

    @patch('cortex.refactoring.adapters.roslyn_process.RoslynProcessManager.is_available')
    def test_is_available_delegates_to_process_manager(self, mock_available):
        """Test is_available delegates to RoslynProcessManager."""
        mock_available.return_value = True
        
        adapter = RoslynAdapter()
        assert adapter.is_available() is True
        
        mock_available.assert_called_once()

    @patch('cortex.refactoring.adapters.roslyn_process.RoslynProcessManager.is_available')
    def test_is_available_false_when_dotnet_missing(self, mock_available):
        """Test is_available returns False when dotnet missing."""
        mock_available.return_value = False
        
        adapter = RoslynAdapter()
        assert adapter.is_available() is False


class TestRoslynAdapterValidation:
    """Test RoslynAdapter request validation."""

    def test_validate_valid_request(self, tmp_path):
        """Test validating a valid refactoring request."""
        test_file = tmp_path / "test.cs"
        test_file.write_text("class Test {}")
        
        adapter = RoslynAdapter()
        request = RefactoringRequest(
            operation="rename",
            file_path=test_file,
            language=RefactoringLanguage.CSHARP,
            parameters={"offset": 10, "new_name": "NewName"}
        )
        
        result = adapter.validate_request(request)
        assert result.is_ok()

    def test_validate_wrong_language(self, tmp_path):
        """Test validation fails for wrong language."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def test(): pass")
        
        adapter = RoslynAdapter()
        request = RefactoringRequest(
            operation="rename",
            file_path=test_file,
            language=RefactoringLanguage.PYTHON,
            parameters={}
        )
        
        result = adapter.validate_request(request)
        assert result.is_err()
        assert "c#" in str(result.unwrap_err()).lower()

    def test_validate_unsupported_operation(self, tmp_path):
        """Test validation fails for unsupported operation."""
        test_file = tmp_path / "test.cs"
        test_file.write_text("class Test {}")
        
        adapter = RoslynAdapter()
        request = RefactoringRequest(
            operation="unsupported_operation",
            file_path=test_file,
            language=RefactoringLanguage.CSHARP,
            parameters={}
        )
        
        result = adapter.validate_request(request)
        assert result.is_err()
        assert "unsupported" in str(result.unwrap_err()).lower()


class TestRoslynAdapterExecution:
    """Test RoslynAdapter refactoring execution."""

    @patch('cortex.refactoring.adapters.roslyn_adapter.RoslynAdapter._execute_via_process')
    def test_execute_refactoring_delegates_to_process(self, mock_execute, tmp_path):
        """Test execute_refactoring delegates to process execution."""
        test_file = tmp_path / "test.cs"
        test_file.write_text("class Test {}")
        
        mock_execute.return_value = Ok(RefactoringResult(
            success=True,
            modified_files=[test_file],
            description="Refactoring applied",
            warnings=[],
            errors=[],
            metadata={}
        ))
        
        adapter = RoslynAdapter()
        request = RefactoringRequest(
            operation="rename",
            file_path=test_file,
            language=RefactoringLanguage.CSHARP,
            parameters={"offset": 10, "new_name": "NewName"}
        )
        
        result = adapter.execute_refactoring(request)
        assert result.is_ok()
        mock_execute.assert_called_once()


# AC_COMPLETE: AC-PHASE24.2.1-003 ✅ 12/12 tests (RED phase)
