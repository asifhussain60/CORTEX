"""Refactoring tool adapter base class and data models (Phase 24).

This module defines the plugin architecture for external refactoring tools,
enabling polyglot semantic refactoring across Python, C#, Java, TypeScript,
and JavaScript codebases.

Architecture:
    - RefactoringToolAdapter: Abstract base class for all adapters
    - RefactoringCapability: Describes what operations a tool supports
    - RefactoringRequest: Encapsulates refactoring operation request
    - RefactoringResult: Encapsulates refactoring operation result
    - RefactoringOperationType: Enum of standardized operation types

Concrete Implementations:
    - RopeAdapter (Python semantic refactoring)
    - RoslynAdapter (C# type-safe refactoring)
    - TypeScriptAdapter (TypeScript/JavaScript LSP-based)
    - JavaAdapter (Java Langtree-based)

Example:
    >>> from cortex.orchestrators.adapters import RefactoringToolAdapter
    >>> class MyAdapter(RefactoringToolAdapter):
    ...     @property
    ...     def tool_name(self) -> str:
    ...         return "my-tool"
    ...     @property
    ...     def languages(self) -> list[str]:
    ...         return ["python"]
    ...     def capabilities(self) -> list[RefactoringCapability]:
    ...         return [RefactoringCapability(...)]
    ...     def is_available(self) -> bool:
    ...         return True
    ...     async def execute_refactoring(self, request: RefactoringRequest) -> RefactoringResult:
    ...         return RefactoringResult(...)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class RefactoringOperationType(str, Enum):
    """Standardized refactoring operation types across all tools.

    Attributes:
        EXTRACT_METHOD: Extract code block into new method/function.
        RENAME_SYMBOL: Rename variable, function, class, or module.
        INLINE: Inline method/variable call or definition.
        ENCAPSULATE_FIELD: Create getter/setter for field access.
        MOVE_METHOD: Move method to different class/module.
        CHANGE_SIGNATURE: Modify method/function signature.
        CONVERT_ANONYMOUS: Convert anonymous function to named.
        INTRODUCE_VARIABLE: Extract expression into variable.
        EXTRACT_INTERFACE: Extract interface from class.
        GENERALIZE_TYPE: Generalize type/variable to parent type.
    """

    EXTRACT_METHOD = "extract_method"
    RENAME_SYMBOL = "rename_symbol"
    INLINE = "inline"
    ENCAPSULATE_FIELD = "encapsulate_field"
    MOVE_METHOD = "move_method"
    CHANGE_SIGNATURE = "change_signature"
    CONVERT_ANONYMOUS = "convert_anonymous"
    INTRODUCE_VARIABLE = "introduce_variable"
    EXTRACT_INTERFACE = "extract_interface"
    GENERALIZE_TYPE = "generalize_type"


@dataclass
class RefactoringCapability:
    """Describes a refactoring operation that a tool supports.

    Attributes:
        name: Operation name (e.g., "extract_method").
        description: Human-readable description of the operation.
        applies_to: Code elements this operation applies to (e.g., ["function", "class"]).
        parameters: Map of parameter names to expected types (e.g., {"new_name": "str"}).
        type_safe: Whether this operation is type-safe (preserves semantics).
        languages: List of languages this operation supports (e.g., ["python", "csharp"]).

    Example:
        >>> cap = RefactoringCapability(
        ...     name="extract_method",
        ...     description="Extract code block into new method",
        ...     applies_to=["function", "method"],
        ...     parameters={"new_name": "str", "extract_docs": "bool"},
        ...     type_safe=True,
        ...     languages=["python", "csharp", "java"]
        ... )
    """

    name: str
    description: str
    applies_to: List[str]
    parameters: Dict[str, str]
    type_safe: bool
    languages: List[str]

    def __post_init__(self) -> None:
        """Validate capability definition."""
        if not self.name:
            raise ValueError("Capability name cannot be empty")
        if not self.description:
            raise ValueError("Capability description cannot be empty")
        if not self.applies_to:
            raise ValueError("Capability must apply to at least one code element")
        if not self.languages:
            raise ValueError("Capability must support at least one language")


@dataclass
class RefactoringRequest:
    """Request to perform a refactoring operation.

    Attributes:
        file_path: Path to file containing code to refactor.
        operation: Type of refactoring operation to perform.
        start_line: Starting line number (1-based, inclusive).
        end_line: Ending line number (1-based, inclusive).
        parameters: Operation-specific parameters (e.g., {"new_name": "my_new_function"}).
        dry_run: If True, return preview without modifying file.

    Invariants:
        - file_path must exist and be readable
        - start_line >= 1
        - end_line >= start_line
        - parameters keys must match capability parameter names

    Example:
        >>> req = RefactoringRequest(
        ...     file_path="src/module.py",
        ...     operation="extract_method",
        ...     start_line=10,
        ...     end_line=15,
        ...     parameters={"new_name": "my_helper"}
        ... )
    """

    file_path: str
    operation: str
    start_line: int
    end_line: int
    parameters: Dict[str, Any] = field(default_factory=dict)
    dry_run: bool = False

    def __post_init__(self) -> None:
        """Validate refactoring request."""
        if not self.file_path:
            raise ValueError("file_path cannot be empty")
        if self.start_line < 1:
            raise ValueError("start_line must be >= 1")
        if self.end_line < self.start_line:
            raise AssertionError(f"end_line ({self.end_line}) must be >= start_line ({self.start_line})")
        if not self.operation:
            raise ValueError("operation cannot be empty")


@dataclass
class RefactoringResult:
    """Result of a refactoring operation.

    Attributes:
        success: Whether refactoring succeeded.
        operation: Type of operation performed.
        file_path: Path to file that was refactored.
        original_content: Original file content (before refactoring).
        refactored_content: Refactored file content (after refactoring).
        changes: List of human-readable change descriptions.
        error_message: Error message if success=False.

    Example:
        >>> result = RefactoringResult(
        ...     success=True,
        ...     operation="extract_method",
        ...     file_path="src/module.py",
        ...     original_content="...",
        ...     refactored_content="...",
        ...     changes=["Extracted 5-line block into 'my_helper' method"],
        ...     error_message=None
        ... )
    """

    success: bool
    operation: str
    file_path: str
    original_content: str
    refactored_content: str
    changes: List[str] = field(default_factory=list)
    error_message: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate refactoring result."""
        if not self.operation:
            raise ValueError("operation cannot be empty")
        if not self.file_path:
            raise ValueError("file_path cannot be empty")
        if self.success and not self.refactored_content:
            raise ValueError("Successful refactoring must have refactored_content")
        if not self.success and not self.error_message:
            raise ValueError("Failed refactoring must have error_message")


class RefactoringToolAdapter(ABC):
    """Abstract base class for external refactoring tool adapters (Phase 24).

    Subclasses must implement:
        - tool_name: Name of the tool
        - languages: Languages supported
        - capabilities(): List of refactoring operations
        - is_available(): Check if tool is installed/available
        - execute_refactoring(): Execute a refactoring operation

    Plugin Architecture:
        Each adapter encapsulates a specific refactoring tool (Rope, Roslyn, etc.)
        and provides a unified interface for the RefactoringOrchestrator to use.
        The orchestrator selects adapters based on language and operation type.

    Type Safety:
        Adapters can declare type_safe=True if they perform semantic refactoring
        that guarantees program semantics are preserved (e.g., type-aware renames).

    Concurrency:
        execute_refactoring() is async to support parallel execution of multiple
        refactoring operations across different files.

    Example:
        >>> class RopeAdapter(RefactoringToolAdapter):
        ...     @property
        ...     def tool_name(self) -> str:
        ...         return "rope"
        ...     @property
        ...     def languages(self) -> List[str]:
        ...         return ["python"]
        ...     def capabilities(self) -> List[RefactoringCapability]:
        ...         return [RefactoringCapability(...)]
        ...     def is_available(self) -> bool:
        ...         try:
        ...             import rope.base.project
        ...             return True
        ...         except ImportError:
        ...             return False
        ...     async def execute_refactoring(self, req: RefactoringRequest) -> RefactoringResult:
        ...         # Implementation
        ...         pass
    """

    @property
    @abstractmethod
    def tool_name(self) -> str:
        """Name of the refactoring tool.

        Returns:
            Tool identifier (e.g., "rope", "roslyn", "typescript-lsp").
        """
        pass

    @property
    @abstractmethod
    def languages(self) -> List[str]:
        """Programming languages this adapter supports.

        Returns:
            List of language identifiers (e.g., ["python", "csharp"]).
        """
        pass

    @abstractmethod
    def capabilities(self) -> List[RefactoringCapability]:
        """Refactoring operations this tool can perform.

        Returns:
            List of RefactoringCapability objects describing supported operations.

        Note:
            This method should be cached in production to avoid repeated computation.
            The RefactoringOrchestrator may call this multiple times per session.
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the refactoring tool is installed and available.

        Returns:
            True if tool can be used, False if tool is not installed/configured.

        Note:
            This is checked before attempting refactoring. Should return False
            immediately if required dependencies are missing.
        """
        pass

    @abstractmethod
    async def execute_refactoring(self, request: RefactoringRequest) -> RefactoringResult:
        """Execute a refactoring operation.

        Args:
            request: RefactoringRequest with operation details.

        Returns:
            RefactoringResult with outcome and modified content.

        Raises:
            ValueError: If operation is not supported or parameters are invalid.
            IOError: If file cannot be read or written.
            Exception: Tool-specific errors from the refactoring engine.

        Implementation Notes:
            - Should validate request.operation matches a supported capability
            - Should validate request.parameters match capability parameter spec
            - Should respect request.dry_run (return preview without writing)
            - Should handle errors gracefully (return RefactoringResult with success=False)
            - Should preserve original content in result (for diff/review)
            - Should include human-readable changes list in result
        """
        pass
