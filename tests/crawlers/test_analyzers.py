"""
Tests for AC-CRAWLER-002: Language-Specific AST Analyzers
"""
import pytest
import tempfile
from pathlib import Path
from src.crawlers.analyzers import (
    PythonAnalyzer,
    JavaScriptAnalyzer,
    CSharpAnalyzer,
    GenericAnalyzer,
    AnalyzerFactory,
    AnalysisResult,
    Symbol,
)


class TestPythonAnalyzer:
    """AC-CRAWLER-002: Python AST analyzer"""

    def test_python_analyzer_extracts_classes(self):
        """Test Python analyzer finds classes"""
        code = """
class MyClass:
    pass
"""
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
        ) as f:
            f.write(code)
            f.flush()

            analyzer = PythonAnalyzer(f.name)
            result = analyzer.analyze()

            assert len(result.symbols) > 0
            assert any(s.name == "MyClass" and s.type == "class" for s in result.symbols)

        Path(f.name).unlink()

    def test_python_analyzer_extracts_functions(self):
        """Test Python analyzer finds functions"""
        code = """
def my_function():
    pass
"""
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
        ) as f:
            f.write(code)
            f.flush()

            analyzer = PythonAnalyzer(f.name)
            result = analyzer.analyze()

            assert any(
                s.name == "my_function" and s.type == "function"
                for s in result.symbols
            )

        Path(f.name).unlink()

    def test_python_analyzer_extracts_imports(self):
        """Test Python analyzer extracts imports"""
        code = """
import os
from pathlib import Path
"""
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
        ) as f:
            f.write(code)
            f.flush()

            analyzer = PythonAnalyzer(f.name)
            result = analyzer.analyze()

            assert "os" in result.imports
            assert "pathlib" in result.imports

        Path(f.name).unlink()

    def test_python_analyzer_metrics(self):
        """Test Python analyzer calculates metrics"""
        code = """
class A:
    def method1(self): pass
    def method2(self): pass

def func1(): pass
"""
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
        ) as f:
            f.write(code)
            f.flush()

            analyzer = PythonAnalyzer(f.name)
            result = analyzer.analyze()

            assert result.metrics["functions"] == 3
            assert result.metrics["classes"] == 1
            assert result.metrics["lines"] > 0

        Path(f.name).unlink()

    def test_python_analyzer_handles_syntax_error(self):
        """Test Python analyzer handles syntax errors"""
        code = "def invalid syntax"

        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
        ) as f:
            f.write(code)
            f.flush()

            analyzer = PythonAnalyzer(f.name)
            result = analyzer.analyze()

            assert len(result.errors) > 0
            assert "Syntax error" in result.errors[0]

        Path(f.name).unlink()


class TestJavaScriptAnalyzer:
    """AC-CRAWLER-002: JavaScript/TypeScript analyzer"""

    def test_javascript_analyzer_extracts_classes(self):
        """Test JS analyzer finds classes"""
        code = "class MyClass { }"

        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".js",
            delete=False,
        ) as f:
            f.write(code)
            f.flush()

            analyzer = JavaScriptAnalyzer(f.name)
            result = analyzer.analyze()

            assert any(
                s.name == "MyClass" and s.type == "class"
                for s in result.symbols
            )

        Path(f.name).unlink()

    def test_javascript_analyzer_extracts_functions(self):
        """Test JS analyzer finds functions"""
        code = """
const myFunc = () => {};
function anotherFunc() {}
"""
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".js",
            delete=False,
        ) as f:
            f.write(code)
            f.flush()

            analyzer = JavaScriptAnalyzer(f.name)
            result = analyzer.analyze()

            assert len(result.symbols) > 0

        Path(f.name).unlink()

    def test_javascript_analyzer_extracts_imports(self):
        """Test JS analyzer extracts imports"""
        code = """
import React from 'react';
import { Component } from 'react';
"""
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".js",
            delete=False,
        ) as f:
            f.write(code)
            f.flush()

            analyzer = JavaScriptAnalyzer(f.name)
            result = analyzer.analyze()

            assert "react" in result.imports

        Path(f.name).unlink()


class TestCSharpAnalyzer:
    """AC-CRAWLER-002: C# analyzer"""

    def test_csharp_analyzer_extracts_classes(self):
        """Test C# analyzer finds classes"""
        code = """
public class MyClass
{
}
"""
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".cs",
            delete=False,
        ) as f:
            f.write(code)
            f.flush()

            analyzer = CSharpAnalyzer(f.name)
            result = analyzer.analyze()

            assert any(
                s.name == "MyClass" and s.type == "class"
                for s in result.symbols
            )

        Path(f.name).unlink()

    def test_csharp_analyzer_extracts_methods(self):
        """Test C# analyzer finds methods"""
        code = """
public class MyClass
{
    public void MyMethod() { }
    private int Calculate() { return 0; }
}
"""
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".cs",
            delete=False,
        ) as f:
            f.write(code)
            f.flush()

            analyzer = CSharpAnalyzer(f.name)
            result = analyzer.analyze()

            assert len(result.symbols) > 0

        Path(f.name).unlink()

    def test_csharp_analyzer_extracts_usings(self):
        """Test C# analyzer extracts using statements"""
        code = """
using System;
using System.Collections.Generic;
"""
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".cs",
            delete=False,
        ) as f:
            f.write(code)
            f.flush()

            analyzer = CSharpAnalyzer(f.name)
            result = analyzer.analyze()

            assert "System" in result.imports

        Path(f.name).unlink()


class TestAnalyzerFactory:
    """AC-CRAWLER-002: Analyzer factory"""

    def test_factory_returns_python_analyzer(self):
        """Test factory returns Python analyzer for .py files"""
        with tempfile.NamedTemporaryFile(suffix=".py") as f:
            analyzer = AnalyzerFactory.get_analyzer(f.name)
            assert isinstance(analyzer, PythonAnalyzer)

    def test_factory_returns_javascript_analyzer(self):
        """Test factory returns JS analyzer for .js files"""
        with tempfile.NamedTemporaryFile(suffix=".js") as f:
            analyzer = AnalyzerFactory.get_analyzer(f.name)
            assert isinstance(analyzer, JavaScriptAnalyzer)

    def test_factory_returns_typescript_analyzer(self):
        """Test factory returns JS analyzer for .ts files"""
        with tempfile.NamedTemporaryFile(suffix=".ts") as f:
            analyzer = AnalyzerFactory.get_analyzer(f.name)
            assert isinstance(analyzer, JavaScriptAnalyzer)

    def test_factory_returns_csharp_analyzer(self):
        """Test factory returns C# analyzer for .cs files"""
        with tempfile.NamedTemporaryFile(suffix=".cs") as f:
            analyzer = AnalyzerFactory.get_analyzer(f.name)
            assert isinstance(analyzer, CSharpAnalyzer)

    def test_factory_returns_generic_analyzer(self):
        """Test factory returns generic analyzer for unknown files"""
        with tempfile.NamedTemporaryFile(suffix=".xyz") as f:
            analyzer = AnalyzerFactory.get_analyzer(f.name)
            assert isinstance(analyzer, GenericAnalyzer)

    def test_analysis_result_structure(self):
        """Test AnalysisResult has required fields"""
        result = AnalysisResult(file_path="test.py", language="python")

        assert result.file_path == "test.py"
        assert result.language == "python"
        assert isinstance(result.symbols, list)
        assert isinstance(result.imports, list)
        assert isinstance(result.errors, list)

    def test_symbol_structure(self):
        """Test Symbol has required fields"""
        symbol = Symbol(
            name="test_func",
            type="function",
            line=10,
            column=0,
        )

        assert symbol.name == "test_func"
        assert symbol.type == "function"
        assert symbol.line == 10
        assert symbol.complexity == 1
