"""
Refactoring Operations MCP Tools

Exposes RefactoringToolAdapter capabilities via MCP for polyglot refactoring.
Provides Python (Rope), C# (Roslyn), TypeScript, and Java refactoring operations.

AC_START: AC-PHASE24.1.4-001
Description: MCP tools for external refactoring operations
Authority: Phase 24 - External Refactoring Tools Integration
Compliance: CORE-011 (type hints), CORE-012 (docstrings), MCP-FIRST
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

from cortex.mcp.decorators import mcp_tool

logger = logging.getLogger(__name__)


@mcp_tool(
    name="cortex_refactor_python",
    description="Execute Python refactoring operations via Rope library (extract_method, rename, inline, encapsulate_field, move_method, change_signature)",
    category="refactoring"
)
def cortex_refactor_python(
    operation: str,
    file_path: str,
    parameters: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Execute Python semantic refactoring operation.
    
    Supported operations:
        - extract_method: Extract code block into new method
        - rename: Rename variables, functions, classes
        - inline: Inline variable or method
        - encapsulate_field: Create getter/setter for field
        - move_method: Move method to another class
        - change_signature: Modify method signature
    
    Args:
        operation: Refactoring operation name
        file_path: Path to Python file to refactor
        parameters: Operation-specific parameters:
            - extract_method: {start_offset: int, end_offset: int, new_name: str}
            - rename: {offset: int, new_name: str}
            - inline: {offset: int}
            - encapsulate_field: {offset: int}
            - move_method: {offset: int, target_class: str}
            - change_signature: {offset: int, new_parameters: list}
    
    Returns:
        Refactoring result with success status, modified files, and description
        
    Examples:
        cortex_refactor_python("rename", "/app/main.py", {"offset": 150, "new_name": "process_data"})
        cortex_refactor_python("extract_method", "/app/utils.py", {"start_offset": 100, "end_offset": 200, "new_name": "helper"})
    """
    try:
        from cortex.refactoring.adapters.rope_adapter import RopeAdapter
        from cortex.refactoring.models import RefactoringRequest, RefactoringLanguage
        
        # Initialize adapter
        adapter = RopeAdapter()
        
        # Check availability
        if not adapter.is_available():
            return {
                "status": "error",
                "error": "Rope library not available. Install with: pip install rope",
                "operation": operation,
                "file_path": file_path
            }
        
        # Create refactoring request
        request = RefactoringRequest(
            operation=operation,
            file_path=Path(file_path),
            language=RefactoringLanguage.PYTHON,
            parameters=parameters
        )
        
        # Execute refactoring
        result = adapter.execute_refactoring(request)
        
        if result.is_ok():
            refactoring_result = result.unwrap()
            return {
                "status": "success",
                "success": refactoring_result.success,
                "operation": operation,
                "file_path": file_path,
                "modified_files": [str(f) for f in refactoring_result.modified_files],
                "description": refactoring_result.description,
                "warnings": refactoring_result.warnings,
                "metadata": refactoring_result.metadata
            }
        else:
            error = result.unwrap_err()
            return {
                "status": "error",
                "error": error,
                "operation": operation,
                "file_path": file_path
            }
    
    except Exception as e:
        logger.error(f"Python refactoring failed: {e}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "operation": operation,
            "file_path": file_path
        }


@mcp_tool(
    name="cortex_refactoring_list_operations",
    description="List available refactoring operations for all supported languages",
    category="refactoring"
)
def cortex_refactoring_list_operations(
    language: Optional[str] = None
) -> Dict[str, Any]:
    """
    List available refactoring operations.
    
    Args:
        language: Optional language filter (python, csharp, typescript, java)
        
    Returns:
        Dictionary with supported languages and their operations
    """
    try:
        from cortex.refactoring.registry import RefactoringToolRegistry
        from cortex.refactoring.adapters.rope_adapter import RopeAdapter
        from cortex.refactoring.models import RefactoringLanguage
        
        # Initialize registry with available adapters
        registry = RefactoringToolRegistry()
        
        # Register Python adapter
        try:
            rope_adapter = RopeAdapter()
            registry.register(rope_adapter)
        except Exception as e:
            logger.warning(f"Failed to register Rope adapter: {e}")
        
        # Get operations by language
        operations_by_language = {}
        
        for lang in registry.get_supported_languages():
            ops_result = registry.get_operations_for_language(lang)
            if ops_result.is_ok():
                operations_by_language[lang.value] = {
                    "operations": ops_result.unwrap(),
                    "available": lang in registry.get_available_languages()
                }
        
        # Filter by language if specified
        if language:
            lang_lower = language.lower()
            if lang_lower in operations_by_language:
                return {
                    "status": "success",
                    "language": lang_lower,
                    "operations": operations_by_language[lang_lower]["operations"],
                    "available": operations_by_language[lang_lower]["available"]
                }
            else:
                return {
                    "status": "error",
                    "error": f"Language '{language}' not supported",
                    "supported_languages": list(operations_by_language.keys())
                }
        
        # Return all languages
        return {
            "status": "success",
            "languages": operations_by_language,
            "total_languages": len(operations_by_language)
        }
    
    except Exception as e:
        logger.error(f"Failed to list refactoring operations: {e}", exc_info=True)
        return {
            "status": "error",
            "error": str(e)
        }


@mcp_tool(
    name="cortex_refactoring_validate",
    description="Validate a refactoring request before execution",
    category="refactoring"
)
def cortex_refactoring_validate(
    operation: str,
    file_path: str,
    language: str,
    parameters: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Validate refactoring request without executing.
    
    Args:
        operation: Refactoring operation name
        file_path: Path to file to refactor
        language: Programming language (python, csharp, typescript, java)
        parameters: Operation-specific parameters
        
    Returns:
        Validation result with success status and any errors
    """
    try:
        from cortex.refactoring.registry import RefactoringToolRegistry
        from cortex.refactoring.adapters.rope_adapter import RopeAdapter
        from cortex.refactoring.models import (
            RefactoringRequest,
            RefactoringLanguage
        )
        
        # Initialize registry
        registry = RefactoringToolRegistry()
        
        # Register adapters
        if language.lower() == "python":
            adapter = RopeAdapter()
            registry.register(adapter)
        
        # Get language enum
        try:
            lang_enum = RefactoringLanguage[language.upper()]
        except KeyError:
            return {
                "status": "error",
                "error": f"Unsupported language: {language}",
                "supported": [l.value for l in RefactoringLanguage]
            }
        
        # Get adapter
        adapter_result = registry.get_adapter(lang_enum)
        if adapter_result.is_err():
            return {
                "status": "error",
                "error": adapter_result.unwrap_err(),
                "language": language
            }
        
        adapter = adapter_result.unwrap()
        
        # Create request
        request = RefactoringRequest(
            operation=operation,
            file_path=Path(file_path),
            language=lang_enum,
            parameters=parameters
        )
        
        # Validate
        validation_result = adapter.validate_request(request)
        
        if validation_result.is_ok():
            return {
                "status": "success",
                "valid": True,
                "operation": operation,
                "file_path": file_path,
                "language": language
            }
        else:
            return {
                "status": "success",
                "valid": False,
                "operation": operation,
                "file_path": file_path,
                "language": language,
                "error": validation_result.unwrap_err()
            }
    
    except Exception as e:
        logger.error(f"Validation failed: {e}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "operation": operation,
            "file_path": file_path,
            "language": language
        }


# AC_COMPLETE: AC-PHASE24.1.4-001 ✅ 3 MCP tools created
