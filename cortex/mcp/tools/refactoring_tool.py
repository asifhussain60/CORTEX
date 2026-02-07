"""
Refactoring MCP Tools.

Exposes CORTEX RefactoringOrchestrator as MCP tools for SaaS deployment.

AC_START: AC-PHASE24.6-002
Description: MCP tool exposure for RefactoringOrchestrator
Authority: Phase 24.6 - MCP Tool Exposure
Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings), CORE-027 (audit)

MCP Tools:
- cortex_refactor: Execute refactoring operation
- cortex_refactor_available_operations: List operations per language
- cortex_refactor_supported_languages: List supported/available languages

Author: Asif Hussain
ARCH-007: MCP-first architecture enforcement
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from cortex.mcp.decorators import mcp_tool
from cortex.refactoring.models import RefactoringLanguage, RefactoringRequest


@mcp_tool(
    name="cortex_refactor",
    description="Execute semantic refactoring operations (extract, rename, organize, etc.) across Python, C#, TypeScript/JavaScript",
    parameters={
        "operation": "string",
        "file_path": "string",
        "language": "string",
        "parameters": "object",
    }
)
def cortex_refactor(
    operation: str,
    file_path: str,
    language: str,
    parameters: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Execute a refactoring operation on a source file.
    
    Supports 24+ operations across Python, C#, TypeScript/JavaScript:
    - extract_function, extract_method, extract_constant, extract_type
    - rename, inline_variable
    - organize_imports, add_type_hints, convert_to_f_string
    - encapsulate_field, extract_interface
    
    Args:
        operation: Refactoring operation name (e.g., "rename", "extract_function")
        file_path: Path to source file to refactor
        language: Language identifier (python, csharp, typescript, javascript)
        parameters: Operation-specific parameters (offset, new_name, etc.)
        
    Returns:
        Dict with status, modified_files, description, or error
        
    Example:
        >>> cortex_refactor(
        ...     operation="rename",
        ...     file_path="app.py",
        ...     language="python",
        ...     parameters={"offset": 100, "new_name": "new_function_name"}
        ... )
        {
            "status": "success",
            "operation": "rename",
            "language": "python",
            "modified_files": ["app.py"],
            "description": "Renamed symbol at offset 100"
        }
    """
    try:
        from cortex.refactoring.orchestrator import RefactoringOrchestrator
        
        # Initialize orchestrator
        orchestrator = RefactoringOrchestrator()
        
        # Map string language to enum
        language_map = {
            "python": RefactoringLanguage.PYTHON,
            "csharp": RefactoringLanguage.CSHARP,
            "typescript": RefactoringLanguage.TYPESCRIPT,
            "javascript": RefactoringLanguage.JAVASCRIPT,
            "java": RefactoringLanguage.JAVA,
        }
        
        language_enum = language_map.get(language.lower())
        if not language_enum:
            return {
                "status": "error",
                "error": f"Unsupported language: {language}. Supported: {list(language_map.keys())}",
                "operation": operation,
                "file_path": file_path,
            }
        
        # Create refactoring request
        request = RefactoringRequest(
            operation=operation,
            file_path=Path(file_path),
            language=language_enum,
            parameters=parameters or {}
        )
        
        # Execute refactoring
        result = orchestrator.execute_refactoring(request)
        
        # Return result
        if result.is_ok():
            refactoring_result = result.unwrap()
            return {
                "status": "success",
                "operation": operation,
                "language": language,
                "modified_files": [str(f) for f in refactoring_result.modified_files],
                "description": refactoring_result.description,
                "file_path": file_path,
            }
        else:
            error_msg = result.unwrap_err()
            return {
                "status": "error",
                "error": str(error_msg),
                "operation": operation,
                "language": language,
                "file_path": file_path,
            }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Refactoring failed: {str(e)}",
            "operation": operation,
            "language": language,
            "file_path": file_path,
        }


@mcp_tool(
    name="cortex_refactor_available_operations",
    description="List available refactoring operations for a language or all languages",
    parameters={
        "language": "string",
    }
)
def cortex_refactor_available_operations(
    language: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get available refactoring operations for a language or all languages.
    
    Args:
        language: Language identifier (optional). If omitted, returns operations for all languages.
        
    Returns:
        Dict with status and operations map (language -> operations list)
        
    Example:
        >>> cortex_refactor_available_operations()
        {
            "status": "success",
            "operations": {
                "python": ["rename", "extract_function", ...],
                "typescript": ["extract_function", "organize_imports", ...]
            }
        }
        
        >>> cortex_refactor_available_operations(language="python")
        {
            "status": "success",
            "operations": ["rename", "extract_function", "organize_imports", ...]
        }
    """
    try:
        from cortex.refactoring.orchestrator import RefactoringOrchestrator
        
        orchestrator = RefactoringOrchestrator()
        
        if language:
            # Get operations for specific language
            language_map = {
                "python": RefactoringLanguage.PYTHON,
                "csharp": RefactoringLanguage.CSHARP,
                "typescript": RefactoringLanguage.TYPESCRIPT,
                "javascript": RefactoringLanguage.JAVASCRIPT,
                "java": RefactoringLanguage.JAVA,
            }
            
            language_enum = language_map.get(language.lower())
            if not language_enum:
                return {
                    "status": "error",
                    "error": f"Unknown language: {language}. Supported: {list(language_map.keys())}",
                }
            
            operations_result = orchestrator.registry.get_operations_for_language(language_enum)
            
            if operations_result.is_ok():
                operations = operations_result.unwrap()
                return {
                    "status": "success",
                    "language": language,
                    "operations": operations,
                }
            else:
                return {
                    "status": "error",
                    "error": operations_result.unwrap_err(),
                    "language": language,
                }
        else:
            # Get all operations
            all_operations = orchestrator.get_all_operations()
            
            # Convert enum keys to strings
            operations_map = {
                lang.value: ops for lang, ops in all_operations.items()
            }
            
            return {
                "status": "success",
                "operations": operations_map,
            }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Failed to get operations: {str(e)}",
        }


@mcp_tool(
    name="cortex_refactor_supported_languages",
    description="List supported languages and adapter availability status",
    parameters={}
)
def cortex_refactor_supported_languages() -> Dict[str, Any]:
    """
    Get supported languages and adapter availability status.
    
    Returns supported languages (registered adapters), available languages
    (adapters with tools installed), and detailed adapter status.
    
    Returns:
        Dict with status, supported_languages, available_languages, adapter_status
        
    Example:
        >>> cortex_refactor_supported_languages()
        {
            "status": "success",
            "supported_languages": ["python", "csharp", "typescript"],
            "available_languages": ["python", "typescript"],
            "adapter_status": {
                "python": {"available": True, "operation_count": 11},
                "csharp": {"available": False, "operation_count": 8},
                "typescript": {"available": True, "operation_count": 5}
            },
            "total_operations": 24
        }
    """
    try:
        from cortex.refactoring.orchestrator import RefactoringOrchestrator
        
        orchestrator = RefactoringOrchestrator()
        
        # Get supported and available languages
        supported = orchestrator.get_supported_languages()
        available = orchestrator.get_available_languages()
        
        # Get adapter status
        adapter_status = orchestrator.get_adapter_status()
        
        # Get total operations count
        total_operations = orchestrator.get_total_operations_count()
        
        # Convert enums to strings
        supported_languages = [lang.value for lang in supported]
        available_languages = [lang.value for lang in available]
        adapter_status_map = {
            lang.value: status for lang, status in adapter_status.items()
        }
        
        return {
            "status": "success",
            "supported_languages": supported_languages,
            "available_languages": available_languages,
            "adapter_status": adapter_status_map,
            "total_operations": total_operations,
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Failed to get language support: {str(e)}",
        }


# AC_COMPLETE: AC-PHASE24.6-002 ✅ MCP tools implemented
