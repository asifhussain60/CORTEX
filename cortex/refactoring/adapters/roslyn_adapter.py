"""
RoslynAdapter - C# refactoring via Roslyn/OmniSharp.

Implements RefactoringToolAdapter for C# semantic refactoring operations
using .NET Roslyn compiler services.

AC_START: AC-PHASE24.2.1-004
Description: Roslyn adapter for C# refactoring
Authority: Phase 24.2.1 - Roslyn Adapter
Author: Asif Hussain
Created: 2026-02-07
"""

from pathlib import Path
from typing import Any, Dict, List, Union

from cortex.brain.core.result import Err, Ok
from cortex.refactoring.adapters.base import RefactoringToolAdapter
from cortex.refactoring.adapters.roslyn_process import RoslynProcessManager
from cortex.refactoring.models import (
    RefactoringLanguage,
    RefactoringRequest,
    RefactoringResult,
)


class RoslynAdapter(RefactoringToolAdapter):
    """
    C# refactoring adapter using Roslyn compiler services.

    Provides semantic refactoring operations for C# code via Roslyn CLI process:
    - extract_method: Extract code into new method
    - rename: Rename symbols (variables, methods, classes)
    - inline_method: Inline method calls
    - encapsulate_field: Generate getter/setter for field
    - move_to_new_file: Move type to new file
    - introduce_parameter: Convert local variable to parameter
    - extract_interface: Extract interface from class
    - change_signature: Modify method signature

    Example:
        >>> adapter = RoslynAdapter()
        >>> if adapter.is_available():
        ...     request = RefactoringRequest(
        ...         operation="rename",
        ...         file_path=Path("Program.cs"),
        ...         language=RefactoringLanguage.CSHARP,
        ...         parameters={"offset": 150, "new_name": "Calculate"}
        ...     )
        ...     result = adapter.execute_refactoring(request)
    """

    # Supported C# refactoring operations
    SUPPORTED_OPERATIONS = [
        "extract_method",
        "rename",
        "inline_method",
        "encapsulate_field",
        "move_to_new_file",
        "introduce_parameter",
        "extract_interface",
        "change_signature"
    ]

    def __init__(self):
        """Initialize RoslynAdapter with process manager."""
        self._process_manager = RoslynProcessManager()

    def get_supported_operations(self) -> List[str]:
        """
        Get list of supported C# refactoring operations.

        Returns:
            List of operation names supported by this adapter.
        """
        return self.SUPPORTED_OPERATIONS.copy()

    def get_language(self) -> RefactoringLanguage:
        """
        Get programming language handled by this adapter.

        Returns:
            RefactoringLanguage.CSHARP
        """
        return RefactoringLanguage.CSHARP

    def is_available(self) -> bool:
        """
        Check if Roslyn refactoring is available.

        Delegates to RoslynProcessManager to check for .NET SDK and CLI tool.

        Returns:
            True if Roslyn refactoring available, False otherwise.
        """
        return self._process_manager.is_available()

    def validate_request(self, request: RefactoringRequest) -> Union[Ok[None], Err]:
        """
        Validate refactoring request before execution.

        Checks:
        1. Language is C#
        2. Operation is supported
        3. File exists
        4. Required parameters present
        5. Roslyn is available

        Args:
            request: Refactoring request to validate.

        Returns:
            Ok(None) if valid, Err with error message otherwise.
        """
        # Check language
        if request.language != RefactoringLanguage.CSHARP:
            return Err(f"RoslynAdapter only supports C#, got {request.language.value}")

        # Check operation supported
        if request.operation not in self.SUPPORTED_OPERATIONS:
            return Err(
                f"Unsupported operation '{request.operation}'. "
                f"Supported: {', '.join(self.SUPPORTED_OPERATIONS)}"
            )

        # Check file exists
        if not request.file_path.exists():
            return Err(f"File not found: {request.file_path}")

        # Check file is C# source
        if request.file_path.suffix.lower() not in ['.cs', '.csx']:
            return Err(f"File must be C# source (.cs/.csx), got {request.file_path.suffix}")

        # Check Roslyn available
        if not self.is_available():
            return Err(
                "Roslyn refactoring unavailable. Install .NET 8.0+ SDK and build Roslyn CLI tool."
            )

        # Operation-specific validation
        validation_result = self._validate_operation_parameters(request)
        if validation_result.is_err():
            return validation_result

        return Ok(None)

    def _validate_operation_parameters(self, request: RefactoringRequest) -> Union[Ok[None], Err]:
        """
        Validate operation-specific parameters.

        Args:
            request: Refactoring request.

        Returns:
            Ok(None) if parameters valid, Err otherwise.
        """
        params = request.parameters
        op = request.operation

        # Extract method: requires offset range and new name
        if op == "extract_method":
            if "start_offset" not in params or "end_offset" not in params:
                return Err("extract_method requires start_offset and end_offset")
            if "new_name" not in params:
                return Err("extract_method requires new_name")

        # Rename: requires offset and new name
        elif op == "rename":
            if "offset" not in params:
                return Err("rename requires offset (position of symbol)")
            if "new_name" not in params:
                return Err("rename requires new_name")

        # Inline method: requires offset
        elif op == "inline_method":
            if "offset" not in params:
                return Err("inline_method requires offset")

        # Additional operations can be validated here

        return Ok(None)

    def execute_refactoring(self, request: RefactoringRequest) -> Union[Ok[RefactoringResult], Err]:
        """
        Execute C# refactoring operation.

        Args:
            request: Refactoring request.

        Returns:
            Ok with RefactoringResult if successful, Err otherwise.
        """
        # Validate request
        validation = self.validate_request(request)
        if validation.is_err():
            return Err(validation.unwrap_err())

        # Execute via Roslyn process
        return self._execute_via_process(request)

    def _execute_via_process(self, request: RefactoringRequest) -> Union[Ok[RefactoringResult], Err]:
        """
        Execute refactoring via Roslyn CLI process.

        Args:
            request: Refactoring request.

        Returns:
            Ok with RefactoringResult if successful, Err otherwise.
        """
        # Start Roslyn process if not running
        if not self._process_manager.is_running():
            start_result = self._process_manager.start()
            if start_result.is_err():
                return Err(f"Failed to start Roslyn process: {start_result.unwrap_err()}")

        try:
            # Build Roslyn command
            command = {
                "action": "refactor",
                "operation": request.operation,
                "file_path": str(request.file_path.absolute()),
                "parameters": request.parameters
            }

            # Send command to Roslyn process
            response_result = self._process_manager.send_command(command)
            if response_result.is_err():
                return Err(f"Roslyn communication error: {response_result.unwrap_err()}")

            response = response_result.unwrap()

            # Parse response into RefactoringResult
            if response.get("success"):
                return Ok(RefactoringResult(
                    success=True,
                    modified_files=[Path(f) for f in response.get("modified_files", [])],
                    description=response.get("description", "Refactoring applied"),
                    warnings=response.get("warnings", []),
                    errors=[],
                    metadata=response.get("metadata", {})
                ))
            else:
                return Err(f"Roslyn refactoring failed: {response.get('error', 'Unknown error')}")

        except Exception as e:
            return Err(f"Unexpected error during refactoring: {e}")


# AC_COMPLETE: AC-PHASE24.2.1-004 ✅ RoslynAdapter implementation
