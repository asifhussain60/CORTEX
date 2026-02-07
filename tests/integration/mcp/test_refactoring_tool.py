"""
Integration tests for MCP refactoring tool.

AC_START: AC-PHASE24.6-002
Description: MCP tool exposure for RefactoringOrchestrator
Authority: Phase 24.6 - MCP Tool Exposure
Compliance: CORE-008 (TDD), CORE-027 (audit), MCP-FIRST
"""

import tempfile
from pathlib import Path

import pytest

from cortex.mcp.tools.refactoring_tool import (
    cortex_refactor,
    cortex_refactor_available_operations,
    cortex_refactor_supported_languages,
)


class TestCortexRefactorTool:
    """Test cortex_refactor MCP tool."""
    
    def test_refactor_python_rename(self):
        """Test Python rename operation via MCP tool."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
def old_name():
    return 42

result = old_name()
""")
            test_file = Path(f.name)
        
        try:
            result = cortex_refactor(
                operation="rename",
                file_path=str(test_file),
                language="python",
                parameters={"offset": 5, "new_name": "new_name"}
            )
            
            assert result["status"] == "success"
            assert result["operation"] == "rename"
            assert result["language"] == "python"
            assert len(result["modified_files"]) == 1
        finally:
            test_file.unlink()
    
    def test_refactor_typescript_extract_function(self):
        """Test TypeScript extract function via MCP tool."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ts', delete=False) as f:
            f.write("""
function main() {
    const x = 10;
    const y = 20;
    const z = x + y;
    console.log(z);
}
""")
            test_file = Path(f.name)
        
        try:
            result = cortex_refactor(
                operation="extract_function",
                file_path=str(test_file),
                language="typescript",
                parameters={
                    "start_offset": 40,
                    "end_offset": 80,
                    "new_name": "calculateSum"
                }
            )
            
            assert result["status"] == "success"
            assert result["operation"] == "extract_function"
            assert result["language"] == "typescript"
        finally:
            test_file.unlink()
    
    def test_refactor_javascript_organize_imports(self):
        """Test JavaScript organize imports via MCP tool (routes to TypeScript)."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write("""
import { z } from './z';
import { a } from './a';
import React from 'react';
import { b } from './b';

console.log(a, b, z, React);
""")
            test_file = Path(f.name)
        
        try:
            result = cortex_refactor(
                operation="organize_imports",
                file_path=str(test_file),
                language="javascript",
                parameters={}
            )
            
            assert result["status"] == "success"
            assert result["operation"] == "organize_imports"
            assert result["language"] == "javascript"
        finally:
            test_file.unlink()
    
    def test_refactor_invalid_operation(self):
        """Test error handling for invalid operation."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("x = 1")
            test_file = Path(f.name)
        
        try:
            result = cortex_refactor(
                operation="invalid_operation",
                file_path=str(test_file),
                language="python",
                parameters={}
            )
            
            assert result["status"] == "error"
            assert "error" in result
            assert "invalid_operation" in result["error"].lower()
        finally:
            test_file.unlink()
    
    def test_refactor_unsupported_language(self):
        """Test error handling for unsupported language."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.java', delete=False) as f:
            f.write("class Test {}")
            test_file = Path(f.name)
        
        try:
            result = cortex_refactor(
                operation="rename",
                file_path=str(test_file),
                language="java",
                parameters={"offset": 10, "new_name": "NewTest"}
            )
            
            assert result["status"] == "error"
            assert "error" in result
        finally:
            test_file.unlink()
    
    def test_refactor_missing_file(self):
        """Test error handling for missing file."""
        result = cortex_refactor(
            operation="rename",
            file_path="/nonexistent/file.py",
            language="python",
            parameters={"offset": 10, "new_name": "new_name"}
        )
        
        assert result["status"] == "error"
        assert "error" in result


class TestCortexRefactorAvailableOperations:
    """Test cortex_refactor_available_operations MCP tool."""
    
    def test_get_all_operations(self):
        """Test getting all operations."""
        result = cortex_refactor_available_operations()
        
        assert result["status"] == "success"
        assert "operations" in result
        
        # Check Python operations
        assert "python" in result["operations"]
        python_ops = result["operations"]["python"]
        assert "rename" in python_ops
        assert "extract_function" in python_ops
        
        # Check TypeScript operations
        assert "typescript" in result["operations"]
        ts_ops = result["operations"]["typescript"]
        assert "extract_function" in ts_ops
        assert "organize_imports" in ts_ops
    
    def test_get_operations_for_language(self):
        """Test getting operations for specific language."""
        result = cortex_refactor_available_operations(language="python")
        
        assert result["status"] == "success"
        assert "operations" in result
        assert len(result["operations"]) >= 5  # Python has 11+ operations
        assert "rename" in result["operations"]
    
    def test_get_operations_for_invalid_language(self):
        """Test error handling for invalid language."""
        result = cortex_refactor_available_operations(language="invalid")
        
        assert result["status"] == "error"
        assert "error" in result


class TestCortexRefactorSupportedLanguages:
    """Test cortex_refactor_supported_languages MCP tool."""
    
    def test_get_supported_languages(self):
        """Test getting supported languages."""
        result = cortex_refactor_supported_languages()
        
        assert result["status"] == "success"
        assert "supported_languages" in result
        assert "available_languages" in result
        
        # Check supported languages
        assert "python" in result["supported_languages"]
        assert "typescript" in result["supported_languages"]
        
        # Check adapter status
        assert "adapter_status" in result
        assert "python" in result["adapter_status"]
        python_status = result["adapter_status"]["python"]
        assert "available" in python_status
        assert "operations_count" in python_status
    
    def test_get_total_operations(self):
        """Test total operations count."""
        result = cortex_refactor_supported_languages()
        
        assert result["status"] == "success"
        assert "total_operations" in result
        assert result["total_operations"] >= 24  # 11 Python + 8 C# + 5 TypeScript


# AC_COMPLETE: AC-PHASE24.6-002 (tests ready, implementation next)
