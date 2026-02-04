"""
Tests for PolyglotAnalyzer - Multi-Language AST Analysis.

Test Coverage:
- Language detection (.py, .cs, .csx, .java, .ts, .js)
- Python file analysis (via ASTAnalyzer)
- C# file analysis (via CSharpAdapter)
- Unsupported file types
- Result format conversion
- Error handling

Authority: ENH-017 Phase 2
"""

import pytest
from pathlib import Path
from cortex.lens.analyzers.polyglot_analyzer import PolyglotAnalyzer, PolyglotAnalysisResult


@pytest.fixture
def analyzer():
    """Create PolyglotAnalyzer instance."""
    return PolyglotAnalyzer()


@pytest.fixture
def temp_python_file(tmp_path):
    """Create temporary Python file."""
    file_path = tmp_path / "test_module.py"
    file_path.write_text('''
def hello(name: str) -> str:
    """Greet someone."""
    return f"Hello, {name}!"

class Person:
    """A person."""
    def __init__(self, name: str):
        self.name = name
''')
    return file_path


@pytest.fixture
def temp_csharp_file(tmp_path):
    """Create temporary C# file."""
    file_path = tmp_path / "UserService.cs"
    file_path.write_text('''
using System;

namespace MyApp.Services
{
    public class UserService
    {
        public string Name { get; set; }
        
        public void SaveUser(string name)
        {
            Name = name;
        }
    }
}
''')
    return file_path


def test_language_detection_python(analyzer):
    """Should detect Python from .py extension."""
    assert analyzer._detect_language(Path("module.py")) == "python"


def test_language_detection_csharp(analyzer):
    """Should detect C# from .cs extension."""
    assert analyzer._detect_language(Path("UserService.cs")) == "csharp"


def test_language_detection_csharp_script(analyzer):
    """Should detect C# from .csx extension."""
    assert analyzer._detect_language(Path("script.csx")) == "csharp"


def test_language_detection_unknown(analyzer):
    """Should return unknown for unsupported extensions."""
    assert analyzer._detect_language(Path("file.rb")) == "unknown"


def test_supported_extensions(analyzer):
    """Should list all supported extensions."""
    extensions = analyzer.get_supported_extensions()
    assert ".py" in extensions
    assert ".cs" in extensions
    assert ".csx" in extensions
    assert len(extensions) >= 3


def test_is_supported_python(analyzer):
    """Should recognize Python files as supported."""
    assert analyzer.is_supported(Path("module.py")) is True


def test_is_supported_csharp(analyzer):
    """Should recognize C# files as supported."""
    assert analyzer.is_supported(Path("Service.cs")) is True


def test_is_supported_unsupported(analyzer):
    """Should recognize unsupported files."""
    assert analyzer.is_supported(Path("file.rb")) is False


def test_analyze_python_file(analyzer, temp_python_file):
    """Should analyze Python file and return unified format."""
    result = analyzer.analyze_file(temp_python_file)
    
    assert result.success is True
    assert result.language == "Python"
    # Python ASTAnalyzer extracts methods as top-level functions too
    assert len(result.functions) == 2  # hello + __init__
    assert result.functions[0]["name"] == "hello"
    assert result.functions[0]["parameters"] == ["name"]
    assert len(result.classes) == 1
    assert result.classes[0]["name"] == "Person"
    assert result.error == ""


def test_analyze_csharp_file(analyzer, temp_csharp_file):
    """Should analyze C# file and return unified format."""
    result = analyzer.analyze_file(temp_csharp_file)
    
    assert result.success is True
    assert result.language == "C#"
    assert len(result.classes) == 1
    assert result.classes[0]["name"] == "UserService"
    assert result.classes[0]["namespace"] == "MyApp.Services"
    assert "SaveUser" in result.classes[0]["methods"]
    assert len(result.classes[0]["properties"]) == 1
    assert result.classes[0]["properties"][0]["name"] == "Name"
    assert len(result.imports) == 1
    assert result.imports[0]["module"] == "System"
    assert result.error == ""


def test_analyze_unsupported_file(analyzer, tmp_path):
    """Should handle unsupported file types gracefully."""
    ruby_file = tmp_path / "script.rb"
    ruby_file.write_text('puts "Hello"')
    
    result = analyzer.analyze_file(ruby_file)
    
    assert result.success is False
    assert result.language == "unknown"
    assert "Unsupported language" in result.error
    assert len(result.functions) == 0
    assert len(result.classes) == 0


def test_analyze_nonexistent_file(analyzer):
    """Should handle missing files gracefully."""
    result = analyzer.analyze_file(Path("/nonexistent/file.py"))
    
    assert result.success is False
    assert result.error != ""


def test_python_result_format(analyzer, temp_python_file):
    """Should convert Python results to unified format correctly."""
    result = analyzer.analyze_file(temp_python_file)
    
    # Check function format
    func = result.functions[0]
    assert "name" in func
    assert "line_number" in func
    assert "parameters" in func
    assert "is_async" in func
    assert "return_type" in func
    assert "docstring" in func
    
    # Check class format
    cls = result.classes[0]
    assert "name" in cls
    assert "line_number" in cls
    assert "methods" in cls
    assert "bases" in cls
    assert "docstring" in cls


def test_csharp_result_format(analyzer, temp_csharp_file):
    """Should convert C# results to unified format correctly."""
    result = analyzer.analyze_file(temp_csharp_file)
    
    # Check class format
    cls = result.classes[0]
    assert "name" in cls
    assert "line_number" in cls
    assert "methods" in cls
    assert "bases" in cls
    assert "namespace" in cls
    assert "is_interface" in cls
    assert "is_abstract" in cls
    assert "properties" in cls
    
    # Check import format
    imp = result.imports[0]
    assert "module" in imp
    assert "names" in imp
    assert "alias" in imp
    assert "line_number" in imp


def test_metadata_includes_analyzer(analyzer, temp_python_file):
    """Should include analyzer name in metadata."""
    result = analyzer.analyze_file(temp_python_file)
    assert "analyzer" in result.metadata
    assert result.metadata["analyzer"] == "ASTAnalyzer"


def test_metadata_includes_analyzer_csharp(analyzer, temp_csharp_file):
    """Should include analyzer name in metadata for C#."""
    result = analyzer.analyze_file(temp_csharp_file)
    assert "analyzer" in result.metadata
    assert result.metadata["analyzer"] == "CSharpAdapter"


@pytest.fixture
def temp_java_file(tmp_path):
    """Create temporary Java file."""
    file_path = tmp_path / "UserService.java"
    file_path.write_text('''
package com.example.service;

import java.util.List;
import java.util.ArrayList;

public class UserService {
    private List<String> users;
    
    public UserService() {
        this.users = new ArrayList<>();
    }
    
    public void addUser(String name) {
        users.add(name);
    }
    
    public List<String> getUsers() {
        return users;
    }
}
''')
    return file_path


def test_analyze_java_file(analyzer, temp_java_file):
    """Should analyze Java file using JavaAdapter."""
    result = analyzer.analyze_file(temp_java_file)
    
    assert result.success
    assert result.language == "Java"
    assert len(result.classes) == 1
    assert result.classes[0]["name"] == "UserService"


def test_java_methods_extraction(analyzer, temp_java_file):
    """Should extract methods from Java class."""
    result = analyzer.analyze_file(temp_java_file)
    
    user_service = result.classes[0]
    method_names = user_service["methods"]
    
    assert "UserService" in method_names  # Constructor
    assert "addUser" in method_names
    assert "getUsers" in method_names


def test_java_fields_extraction(analyzer, temp_java_file):
    """Should extract fields from Java class."""
    result = analyzer.analyze_file(temp_java_file)
    
    user_service = result.classes[0]
    properties = user_service["properties"]
    
    assert len(properties) == 1
    field_names = [p["name"] for p in properties]
    assert "users" in field_names


def test_java_imports_extraction(analyzer, temp_java_file):
    """Should extract imports from Java file."""
    result = analyzer.analyze_file(temp_java_file)
    
    assert len(result.imports) == 2
    import_modules = [imp["module"] for imp in result.imports]
    assert "java.util.List" in import_modules
    assert "java.util.ArrayList" in import_modules


def test_metadata_includes_analyzer_java(analyzer, temp_java_file):
    """Should include analyzer name in metadata for Java."""
    result = analyzer.analyze_file(temp_java_file)
    assert "analyzer" in result.metadata
    assert result.metadata["analyzer"] == "JavaAdapter"


def test_supported_extensions_includes_java(analyzer):
    """Should include .java in supported extensions."""
    extensions = analyzer.get_supported_extensions()
    assert ".java" in extensions


def test_is_supported_java(analyzer, temp_java_file):
    """Should recognize Java files as supported."""
    assert analyzer.is_supported(temp_java_file) is True

