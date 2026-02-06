"""
Test suite for RefactoringToolAdapter abstract base class.

Tests cover:
- Abstract interface enforcement
- Concrete adapter implementation
- Dataclass validation (RefactoringCapability, RefactoringRequest, RefactoringResult)
- Enum definition (RefactoringOperationType)

CORTEX Framework Compliance:
- CORE-008: TDD-first (tests written before implementation)
- CORE-011: Type hints mandatory
- CORE-012: Google-style docstrings
"""

from typing import List
import pytest

from cortex.orchestrators.adapters.refactoring_tool_adapter import (
    RefactoringToolAdapter,
    RefactoringCapability,
    RefactoringRequest,
    RefactoringResult,
    RefactoringOperationType,
)


# ============================================================================
# TEST FIXTURES: Concrete Implementations
# ============================================================================

class ConcreteRefactoringAdapter(RefactoringToolAdapter):
    """Concrete implementation for testing abstract interface."""

    @property
    def tool_name(self) -> str:
        """Return the name of this refactoring tool."""
        return "test-tool"

    @property
    def languages(self) -> List[str]:
        """Return list of supported languages."""
        return ["python", "csharp"]

    def capabilities(self) -> List[RefactoringCapability]:
        """Return list of supported refactoring capabilities."""
        return [
            RefactoringCapability(
                name="extract_method",
                description="Extract selected code into a new method",
                applies_to=["function", "method"],
                parameters={"new_name": "str"},
                type_safe=True,
                languages=["python", "csharp"],
            )
        ]

    def is_available(self) -> bool:
        """Return whether the refactoring tool is available."""
        return True

    async def execute_refactoring(self, request: RefactoringRequest) -> RefactoringResult:
        return RefactoringResult(
            success=True,
            operation=request.operation,
            file_path=request.file_path,
            original_content="# original",
            refactored_content="# refactored",
            changes=["Extracted method"],
        )


# ============================================================================
# TEST CLASS: RefactoringToolAdapter Abstract Interface
# ============================================================================

class TestRefactoringToolAdapterAbstractInterface:
    """Test the RefactoringToolAdapter abstract base class interface."""
    
    def test_cannot_instantiate_abstract_class(self):
        """RefactoringToolAdapter is abstract and cannot be instantiated."""
        with pytest.raises(TypeError):
            RefactoringToolAdapter()
    
    def test_concrete_adapter_satisfies_interface(self):
        """Concrete adapter can be instantiated when all methods implemented."""
        adapter = ConcreteRefactoringAdapter()
        assert adapter is not None
        assert isinstance(adapter, RefactoringToolAdapter)
    
    def test_tool_name_property(self):
        """tool_name property returns string."""
        adapter = ConcreteRefactoringAdapter()
        assert adapter.tool_name == "test-tool"
        assert isinstance(adapter.tool_name, str)
    
    def test_languages_property(self):
        """languages property returns list of strings."""
        adapter = ConcreteRefactoringAdapter()
        assert adapter.languages == ["python", "csharp"]
        assert isinstance(adapter.languages, list)
    
    def test_capabilities_method(self):
        """capabilities() returns list of RefactoringCapability."""
        adapter = ConcreteRefactoringAdapter()
        caps = adapter.capabilities()
        assert isinstance(caps, list)
        assert len(caps) > 0
        assert all(isinstance(c, RefactoringCapability) for c in caps)
    
    def test_is_available_method(self):
        """is_available() returns boolean."""
        adapter = ConcreteRefactoringAdapter()
        assert isinstance(adapter.is_available(), bool)
    
    @pytest.mark.asyncio
    async def test_execute_refactoring_method(self):
        """execute_refactoring() is async and returns RefactoringResult."""
        adapter = ConcreteRefactoringAdapter()
        request = RefactoringRequest(
            file_path="test.py",
            operation="extract_method",
            start_line=1,
            end_line=5,
        )
        result = await adapter.execute_refactoring(request)
        assert isinstance(result, RefactoringResult)
        assert result.success is True


# ============================================================================
# TEST CLASS: RefactoringCapability Dataclass
# ============================================================================

class TestRefactoringCapability:
    """Test RefactoringCapability dataclass."""
    
    def test_create_valid_capability(self):
        """Create a valid refactoring capability."""
        cap = RefactoringCapability(
            name="extract_method",
            description="Extract selected code into a new method",
            applies_to=["function", "method"],
            parameters={"method_name": "str", "access_level": "str"},
            type_safe=True,
            languages=["python", "java"],
        )
        assert cap.name == "extract_method"
        assert cap.description == "Extract selected code into a new method"
        assert cap.applies_to == ["function", "method"]
        assert cap.type_safe is True
        assert cap.languages == ["python", "java"]
    
    def test_capability_requires_name(self):
        """RefactoringCapability requires name parameter."""
        with pytest.raises(TypeError):
            RefactoringCapability(
                description="Test",
                applies_to=["function"],
                parameters={},
                type_safe=False,
                languages=["python"],
            )
    
    def test_capability_requires_description(self):
        """RefactoringCapability requires description parameter."""
        with pytest.raises(TypeError):
            RefactoringCapability(
                name="test",
                applies_to=["function"],
                parameters={},
                type_safe=False,
                languages=["python"],
            )
    
    def test_capability_requires_applies_to(self):
        """RefactoringCapability requires applies_to parameter as List[str]."""
        with pytest.raises(TypeError):
            RefactoringCapability(
                name="test",
                description="Test",
                applies_to="function",
                parameters={},
                type_safe=False,
                languages=["python"],
            )
    
    def test_capability_default_parameters(self):
        """RefactoringCapability has default empty parameters dict."""
        cap = RefactoringCapability(
            name="test",
            description="Test",
            applies_to=["function"],
            languages=["python"],
        )
        assert cap.parameters == {}
        assert cap.type_safe is False


# ============================================================================
# TEST CLASS: RefactoringRequest Dataclass
# ============================================================================

class TestRefactoringRequest:
    """Test RefactoringRequest dataclass."""
    
    def test_create_valid_request(self):
        """Create a valid refactoring request."""
        request = RefactoringRequest(
            file_path="/path/to/file.py",
            operation="extract_method",
            start_line=10,
            end_line=20,
        )
        assert request.file_path == "/path/to/file.py"
        assert request.operation == "extract_method"
        assert request.start_line == 10
        assert request.end_line == 20
        assert request.dry_run is False
        assert request.changes == {}
    
    def test_request_requires_file_path(self):
        """RefactoringRequest requires file_path parameter."""
        with pytest.raises(TypeError):
            RefactoringRequest(
                operation="extract_method",
                start_line=1,
                end_line=5,
            )
    
    def test_request_requires_operation(self):
        """RefactoringRequest requires operation parameter."""
        with pytest.raises(TypeError):
            RefactoringRequest(
                file_path="test.py",
                start_line=1,
                end_line=5,
            )
    
    def test_request_start_line_must_be_positive(self):
        """RefactoringRequest.start_line must be >= 1."""
        with pytest.raises(ValueError):
            RefactoringRequest(
                file_path="test.py",
                operation="test",
                start_line=0,
                end_line=5,
            )
    
    def test_request_end_line_greater_than_equal_start_line(self):
        """RefactoringRequest.end_line must be >= start_line."""
        with pytest.raises(ValueError):
            RefactoringRequest(
                file_path="test.py",
                operation="test",
                start_line=10,
                end_line=5,
            )
    
    def test_request_default_parameters(self):
        """RefactoringRequest has proper defaults."""
        request = RefactoringRequest(
            file_path="test.py",
            operation="test",
            start_line=1,
        )
        assert request.end_line == 1
        assert request.dry_run is False
        assert request.changes == {}
    
    def test_request_dry_run_mode(self):
        """RefactoringRequest supports dry_run mode."""
        request = RefactoringRequest(
            file_path="test.py",
            operation="test",
            start_line=1,
            end_line=5,
            dry_run=True,
        )
        assert request.dry_run is True


# ============================================================================
# TEST CLASS: RefactoringResult Dataclass
# ============================================================================

class TestRefactoringResult:
    """Test RefactoringResult dataclass."""
    
    def test_create_successful_result(self):
        """Create a successful refactoring result."""
        result = RefactoringResult(
            success=True,
            operation="extract_method",
            file_path="/path/to/file.py",
            original_content="def foo(): pass",
            refactored_content="def bar(): pass",
            changes=["Extracted method"],
        )
        assert result.success is True
        assert result.operation == "extract_method"
        assert result.file_path == "/path/to/file.py"
        assert result.original_content == "def foo(): pass"
        assert result.refactored_content == "def bar(): pass"
        assert result.changes == ["Extracted method"]
        assert result.error is None
    
    def test_create_failed_result(self):
        """Create a failed refactoring result."""
        result = RefactoringResult(
            success=False,
            operation="extract_method",
            file_path="/path/to/file.py",
            error="Syntax error",
        )
        assert result.success is False
        assert result.error == "Syntax error"
        assert result.refactored_content is None
    
    def test_result_success_requires_content(self):
        """Successful result requires refactored_content."""
        with pytest.raises(ValueError):
            RefactoringResult(
                success=True,
                operation="test",
                file_path="test.py",
                original_content="code",
            )
    
    def test_result_failure_requires_error(self):
        """Failed result requires error message."""
        with pytest.raises(ValueError):
            RefactoringResult(
                success=False,
                operation="test",
                file_path="test.py",
                original_content="code",
            )
    
    def test_result_default_changes(self):
        """RefactoringResult has default empty changes."""
        result = RefactoringResult(
            success=True,
            operation="test",
            file_path="test.py",
            original_content="code",
            refactored_content="new code",
        )
        assert result.changes == []


# ============================================================================
# TEST CLASS: RefactoringOperationType Enum
# ============================================================================

class TestRefactoringOperationType:
    """Test RefactoringOperationType enum."""
    
    def test_all_operation_types_defined(self):
        """All expected operation types are defined in enum."""
        expected_operations = {
            "extract_method",
            "rename",
            "inline",
            "move",
            "convert_to_property",
            "encapsulate_field",
            "pull_up_method",
            "push_down_method",
            "extract_interface",
            "change_method_signature",
        }
        
        enum_operations = {member.value for member in RefactoringOperationType}
        
        # Check that at least the expected operations are present
        assert expected_operations.issubset(enum_operations)
    
    def test_enum_members_are_strings(self):
        """All enum members should be strings."""
        for member in RefactoringOperationType:
            assert isinstance(member.value, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

        class IncompleteAdapter(RefactoringToolAdapter):
            tool_name = "test"
            
            def capabilities(self) -> List[RefactoringCapability]:
                return []
            
            def is_available(self) -> bool:
                return False
            
            async def execute_refactoring(
                self,
                request: RefactoringRequest
            ) -> RefactoringResult:
                pass
        
        with pytest.raises(TypeError):
            IncompleteAdapter()
    
    def test_requires_capabilities_method(self):
        """Concrete adapters must implement capabilities() method."""
        from cortex.orchestrators.adapters.refactoring_tool_adapter import RefactoringToolAdapter
        
        class IncompleteAdapter(RefactoringToolAdapter):
            tool_name = "test"
            languages = ["python"]
            
            def is_available(self) -> bool:
                return False
            
            async def execute_refactoring(
                self,
                request: RefactoringRequest
            ) -> RefactoringResult:
                pass
        
        with pytest.raises(TypeError):
            IncompleteAdapter()
    
    def test_requires_is_available_method(self):
        """Concrete adapters must implement is_available() method."""
        from cortex.orchestrators.adapters.refactoring_tool_adapter import RefactoringToolAdapter
        
        class IncompleteAdapter(RefactoringToolAdapter):
            tool_name = "test"
            languages = ["python"]
            
            def capabilities(self) -> List[RefactoringCapability]:
                return []
            
            async def execute_refactoring(
                self,
                request: RefactoringRequest
            ) -> RefactoringResult:
                pass
        
        with pytest.raises(TypeError):
            IncompleteAdapter()
    
    def test_requires_execute_refactoring_method(self):
        """Concrete adapters must implement execute_refactoring() async method."""
        from cortex.orchestrators.adapters.refactoring_tool_adapter import RefactoringToolAdapter
        
        class IncompleteAdapter(RefactoringToolAdapter):
            tool_name = "test"
            languages = ["python"]
            
            def capabilities(self) -> List[RefactoringCapability]:
                return []
            
            def is_available(self) -> bool:
                return False
        
        with pytest.raises(TypeError):
            IncompleteAdapter()


class TestRefactoringCapability:
    """Test RefactoringCapability dataclass."""
    
    def test_create_valid_capability(self):
        """Create a valid refactoring capability."""
        cap = RefactoringCapability(
            name="extract_method",
            description="Extract selected code into a new method",
            applies_to="function",
            parameters={
                "method_name": "str",
                "access_level": "str"
            },
            type_safe=True,
            languages=["python", "java"]
        )
        
        assert cap.name == "extract_method"
        assert cap.type_safe is True
        assert "python" in cap.languages
    
    def test_capability_requires_name(self):
        """Capability requires non-empty name."""
        with pytest.raises(AssertionError):
            RefactoringCapability(
                name="",
                description="Extract selected code into a new method",
                applies_to="function",
                parameters={"method_name": "str"},
                type_safe=True,
                languages=["python"]
            )
    
    def test_capability_requires_languages_list(self):
        """Capability requires non-empty languages list."""
        with pytest.raises(AssertionError):
            RefactoringCapability(
                name="extract_method",
                description="Extract selected code into a new method",
                applies_to="function",
                parameters={"method_name": "str"},
                type_safe=True,
                languages=[]
            )
    
    def test_capability_type_safe_must_be_bool(self):
        """Type_safe field must be boolean."""
        with pytest.raises(AssertionError):
            RefactoringCapability(
                name="extract_method",
                description="Extract selected code into a new method",
                applies_to="function",
                parameters={"method_name": "str"},
                type_safe="yes",  # Should be bool
                languages=["python"]
            )


class TestRefactoringRequest:
    """Test RefactoringRequest dataclass."""
    
    def test_create_valid_request(self):
        """Create a valid refactoring request."""
        request = RefactoringRequest(
            file_path="src/module.py",
            operation="extract_method",
            start_line=10,
            end_line=25,
            parameters={
                "method_name": "helper_function",
                "access_level": "private"
            },
            dry_run=True
        )
        
        assert request.file_path == "src/module.py"
        assert request.operation == "extract_method"
        assert request.dry_run is True
    
    def test_request_requires_file_path(self):
        """Request requires non-empty file path."""
        with pytest.raises(AssertionError):
            RefactoringRequest(
                file_path="",
                operation="extract_method",
                start_line=10,
                end_line=25,
                parameters={}
            )
    
    def test_request_requires_operation(self):
        """Request requires operation name."""
        with pytest.raises(AssertionError):
            RefactoringRequest(
                file_path="src/module.py",
                operation="",
                start_line=10,
                end_line=25,
                parameters={}
            )
    
    def test_request_start_line_must_be_positive(self):
        """Start line must be positive."""
        with pytest.raises(AssertionError):
            RefactoringRequest(
                file_path="src/module.py",
                operation="extract_method",
                start_line=0,
                end_line=25,
                parameters={}
            )
    
    def test_request_end_line_greater_than_equal_start_line(self):
        """End line must be >= start line."""
        with pytest.raises(AssertionError):
            RefactoringRequest(
                file_path="src/module.py",
                operation="extract_method",
                start_line=25,
                end_line=10,
                parameters={}
            )


class TestRefactoringResult:
    """Test RefactoringResult dataclass."""
    
    def test_create_successful_result(self):
        """Create a successful refactoring result."""
        result = RefactoringResult(
            success=True,
            operation="extract_method",
            file_path="src/module.py",
            original_content="def original(): pass",
            refactored_content="def helper(): pass\ndef original(): helper()",
            changes=[
                "Extracted lines 10-15 to new method 'helper'",
                "Updated call site in original function"
            ]
        )
        
        assert result.success is True
        assert len(result.changes) == 2
    
    def test_create_failed_result_requires_error_message(self):
        """Failed result requires error message."""
        with pytest.raises(AssertionError):
            RefactoringResult(
                success=False,
                operation="extract_method",
                file_path="src/module.py",
                original_content="def original(): pass",
                refactored_content="",
                changes=[],
                error_message=None
            )
    
    def test_failed_result_with_error_message(self):
        """Create failed result with error message."""
        result = RefactoringResult(
            success=False,
            operation="extract_method",
            file_path="src/module.py",
            original_content="def original(): pass",
            refactored_content="",
            changes=[],
            error_message="Selected code spans multiple functions"
        )
        
        assert result.success is False
        assert "multiple functions" in result.error_message


class TestRefactoringOperationType:
    """Test RefactoringOperationType enum."""
    
    def test_enum_values(self):
        """Verify all refactoring operation types are defined."""
        operations = [
            RefactoringOperationType.EXTRACT_METHOD,
            RefactoringOperationType.RENAME_SYMBOL,
            RefactoringOperationType.INLINE,
            RefactoringOperationType.ENCAPSULATE,
            RefactoringOperationType.MOVE,
            RefactoringOperationType.CHANGE_SIGNATURE,
            RefactoringOperationType.PULL_UP,
            RefactoringOperationType.PUSH_DOWN,
            RefactoringOperationType.EXTRACT_VARIABLE,
            RefactoringOperationType.EXTRACT_CONSTANT
        ]
        
        assert len(operations) == 10
        assert RefactoringOperationType.EXTRACT_METHOD.value == "extract_method"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
