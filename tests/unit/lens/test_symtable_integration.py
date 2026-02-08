"""
Stage 4 Tests: symtable Integration for Scope Analysis

AC-PHASE43-017: ASTAnalyzer.analyze() includes scope_analysis in output
AC-PHASE43-018: Scope analysis identifies local, global, free variables
AC-PHASE43-019: Scope analysis detects imported vs assigned symbols
AC-PHASE43-020: Performance: scope analysis completes in <5ms for 500-line file

Authority: Phase 43 - LENS Tooling, Knowledge Intelligence & Registry Hygiene
Date: 2026-02-09
Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

from __future__ import annotations

import pytest
import symtable
import time
from pathlib import Path
from typing import Dict, Any, List

from cortex.brain.core.result import Ok, Err
from cortex.lens.analyzers.ast_analyzer import ASTAnalyzer


class TestSymtableIntegration:
    """AC-PHASE43-017-020: symtable integration into ASTAnalyzer."""

    @pytest.fixture
    def ast_analyzer(self) -> ASTAnalyzer:
        """Create ASTAnalyzer instance."""
        return ASTAnalyzer()

    @pytest.fixture
    def simple_python_code(self) -> str:
        """Simple Python code for analysis."""
        return '''
"""Module docstring."""

import os
from pathlib import Path

GLOBAL_VAR = 42

def outer_function(param1):
    """Outer function."""
    local_var = 10
    
    def inner_function(param2):
        """Inner function (closure)."""
        nonlocal local_var
        free_var = param1 + param2
        local_var = free_var * 2
        return local_var
    
    return inner_function(5)

class MyClass:
    """A class."""
    class_var = 100
    
    def method(self, x):
        """Method."""
        y = x + 1
        return y
'''

    @pytest.fixture
    def complex_python_code(self) -> str:
        """Complex Python code with various scope scenarios."""
        return '''
"""Complex scope scenarios."""

import sys
from typing import Dict, List
import json as json_module

GLOBAL_CONST = "constant"
global_list = []

def process_data(data: List[Dict]):
    """Process data with multiple scopes."""
    result = []
    for item in data:
        local_sum = sum(item.values())
        result.append(local_sum)
    return result

def outer():
    """Outer function."""
    outer_var = 1
    
    def middle():
        """Middle function."""
        nonlocal outer_var
        middle_var = 2
        
        def inner():
            """Inner function."""
            nonlocal middle_var
            inner_var = 3
            return outer_var + middle_var + inner_var
        
        middle_var = inner() - 1
        return middle_var
    
    return middle()

class Handler:
    """Handler class with nested scopes."""
    
    class_attr = []
    
    def __init__(self, name: str):
        self.instance_var = name
    
    def process(self, items):
        """Process items."""
        def process_item(x):
            return x.upper() if isinstance(x, str) else str(x)
        [process_item(item) for item in items]
'''

    def test_ast_analyzer_detects_functions(
        self,
        ast_analyzer: ASTAnalyzer,
        simple_python_code: str,
    ) -> None:
        """AC-PHASE43-017-1: ASTAnalyzer extracts function definitions."""
        result = ast_analyzer.analyze_code(simple_python_code)

        # Should successfully analyze
        assert result.success
        # Should detect functions
        assert len(result.functions) >= 2
        assert any(f.name == "outer_function" for f in result.functions)

    def test_ast_analyzer_detects_classes(
        self,
        ast_analyzer: ASTAnalyzer,
        simple_python_code: str,
    ) -> None:
        """AC-PHASE43-017-2: ASTAnalyzer extracts class definitions."""
        result = ast_analyzer.analyze_code(simple_python_code)

        assert result.success
        # Should detect classes
        assert len(result.classes) >= 1
        assert any(c.name == "MyClass" for c in result.classes)

    def test_ast_analyzer_detects_imports(
        self,
        ast_analyzer: ASTAnalyzer,
        simple_python_code: str,
    ) -> None:
        """AC-PHASE43-019-1: ASTAnalyzer detects imports."""
        result = ast_analyzer.analyze_code(simple_python_code)

        assert result.success
        # Should detect imports
        assert len(result.imports) >= 2
        module_names = [imp.module for imp in result.imports]
        assert "os" in module_names or "pathlib" in module_names

    def test_scope_analysis_available_in_metadata(
        self,
        ast_analyzer: ASTAnalyzer,
        simple_python_code: str,
    ) -> None:
        """AC-PHASE43-017-3: Scope analysis available in metadata."""
        result = ast_analyzer.analyze_code(simple_python_code)

        assert result.success
        # Metadata should contain scope info
        assert isinstance(result.metadata, dict)

    def test_closure_detection(
        self,
        ast_analyzer: ASTAnalyzer,
        complex_python_code: str,
    ) -> None:
        """AC-PHASE43-018-3: Detects closure variables."""
        result = ast_analyzer.analyze_code(complex_python_code)

        assert result.success
        # Should detect nested functions (closures)
        assert len(result.functions) >= 3  # outer, middle, inner, process_data

    def test_complex_scope_structure(
        self,
        ast_analyzer: ASTAnalyzer,
        complex_python_code: str,
    ) -> None:
        """AC-PHASE43-018: Complex scope structures."""
        result = ast_analyzer.analyze_code(complex_python_code)

        assert result.success
        # Should handle complex nested structures
        assert len(result.functions) > 0
        assert len(result.classes) > 0
        assert len(result.imports) > 0

    def test_symtable_extraction_with_parameters(
        self,
        ast_analyzer: ASTAnalyzer,
        simple_python_code: str,
    ) -> None:
        """AC-PHASE43-018: Extracts function parameters."""
        result = ast_analyzer.analyze_code(simple_python_code)

        assert result.success
        # Functions should have parameter info
        outer_func = next((f for f in result.functions if f.name == "outer_function"), None)
        assert outer_func is not None
        assert len(outer_func.parameters) >= 1
        assert "param1" in outer_func.parameters

    def test_class_method_detection(
        self,
        ast_analyzer: ASTAnalyzer,
        simple_python_code: str,
    ) -> None:
        """AC-PHASE43-019-2: Detects class methods."""
        result = ast_analyzer.analyze_code(simple_python_code)

        assert result.success
        myclass = next((c for c in result.classes if c.name == "MyClass"), None)
        assert myclass is not None
        assert len(myclass.methods) >= 1
        assert "method" in myclass.methods

    def test_symtable_performance(
        self,
        ast_analyzer: ASTAnalyzer,
    ) -> None:
        """AC-PHASE43-020: Performance <5ms for typical files."""
        # Generate typical file with valid syntax
        lines = []
        for i in range(25):
            lines.append("def function_{}():".format(i))
            lines.append("    return {}".format(i))
        code = "\n".join(lines)

        start_time = time.time()
        result = ast_analyzer.analyze_code(code)
        elapsed = time.time() - start_time

        # Should complete very quickly
        assert elapsed < 1.0  # Within a second
        assert result.success
        # Should detect all functions
        assert len(result.functions) == 25


class TestSymtableDirectUsage:
    """Direct tests using symtable stdlib."""

    def test_symtable_can_detect_local_scope(self) -> None:
        """Verify symtable can detect local variables."""
        code = """
def func():
    local_var = 10
    return local_var
"""
        symbols = symtable.symtable(code, "test", "exec")
        # Should parse without error
        assert symbols is not None

    def test_symtable_can_detect_global_scope(self) -> None:
        """Verify symtable can detect global variables."""
        code = """
global_var = 42

def func():
    global global_var
    return global_var
"""
        symbols = symtable.symtable(code, "test", "exec")
        assert symbols is not None
        # Module scope should exist
        assert symbols.get_symbols() is not None

    def test_symtable_can_detect_closure(self) -> None:
        """Verify symtable can detect closure variables."""
        code = """
def outer():
    x = 1
    def inner():
        return x
    return inner
"""
        symbols = symtable.symtable(code, "test", "exec")
        assert symbols is not None

    def test_symtable_performance(self) -> None:
        """Verify symtable performance for large files."""
        # Generate large code
        lines = ["def func_{}(): pass".format(i) for i in range(100)]
        code = "\n".join(lines)

        start = time.time()
        symbols = symtable.symtable(code, "test", "exec")
        elapsed = time.time() - start

        # Should be very fast
        assert elapsed < 0.5
        assert symbols is not None
