"""
Unit tests for LanguageAdapter abstract base class (Phase 0).

Tests the contract that all language-specific adapters must implement.

Author: Asif Hussain
Created: 2026-02-04
Authority: LENS-MULTI-LANGUAGE-ENHANCEMENT.yaml Phase 0
"""

import pytest
from pathlib import Path
from abc import ABC
from typing import List

# Direct import to avoid circular dependency
import importlib.util

test_file = Path(__file__)
tests_dir = test_file.parent.parent.parent.parent
project_root = tests_dir.parent
adapter_file = project_root / "cortex" / "lens" / "adapters" / "language_adapter.py"

spec = importlib.util.spec_from_file_location("language_adapter", adapter_file)
adapter_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter_module)

LanguageAdapter = adapter_module.LanguageAdapter

# Import PolyglotASTResult for type checking
model_file = project_root / "cortex" / "lens" / "models" / "polyglot_ast_result.py"
spec2 = importlib.util.spec_from_file_location("polyglot_ast_result", model_file)
model_module = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(model_module)

PolyglotASTResult = model_module.PolyglotASTResult
LanguageType = model_module.LanguageType


class ConcreteAdapter(LanguageAdapter):
    """Concrete implementation for testing abstract methods."""
    
    def parse_file(self, file_path: Path) -> PolyglotASTResult:
        """Test implementation."""
        return PolyglotASTResult(
            language=LanguageType.PYTHON,
            file_path=file_path,
            classes=[],
            functions=[],
            imports=[]
        )
    
    def get_supported_extensions(self) -> List[str]:
        """Test implementation."""
        return [".py", ".pyi"]
    
    def get_language_name(self) -> str:
        """Test implementation."""
        return "Python"


class TestLanguageAdapter:
    """Test LanguageAdapter abstract base class."""
    
    def test_is_abstract_base_class(self):
        """Test that LanguageAdapter is an ABC."""
        assert issubclass(LanguageAdapter, ABC)
    
    def test_cannot_instantiate_directly(self):
        """Test that LanguageAdapter cannot be instantiated."""
        with pytest.raises(TypeError) as exc_info:
            LanguageAdapter()
        
        assert "abstract" in str(exc_info.value).lower()
    
    def test_concrete_adapter_can_be_instantiated(self):
        """Test that concrete implementation can be instantiated."""
        adapter = ConcreteAdapter()
        assert isinstance(adapter, LanguageAdapter)
    
    def test_parse_file_abstract_method(self):
        """Test that parse_file is an abstract method."""
        # This is tested by trying to instantiate without implementing it
        class IncompleteAdapter(LanguageAdapter):
            def get_supported_extensions(self):
                return [".txt"]
            def get_language_name(self):
                return "Test"
        
        with pytest.raises(TypeError):
            IncompleteAdapter()
    
    def test_get_supported_extensions_abstract_method(self):
        """Test that get_supported_extensions is an abstract method."""
        class IncompleteAdapter(LanguageAdapter):
            def parse_file(self, file_path):
                return None
            def get_language_name(self):
                return "Test"
        
        with pytest.raises(TypeError):
            IncompleteAdapter()
    
    def test_get_language_name_abstract_method(self):
        """Test that get_language_name is an abstract method."""
        class IncompleteAdapter(LanguageAdapter):
            def parse_file(self, file_path):
                return None
            def get_supported_extensions(self):
                return []
        
        with pytest.raises(TypeError):
            IncompleteAdapter()
    
    def test_concrete_adapter_parse_file(self):
        """Test that concrete adapter can parse files."""
        adapter = ConcreteAdapter()
        result = adapter.parse_file(Path("/test/file.py"))
        
        assert isinstance(result, PolyglotASTResult)
        assert result.language == LanguageType.PYTHON
        assert result.file_path == Path("/test/file.py")
    
    def test_concrete_adapter_supported_extensions(self):
        """Test that concrete adapter returns supported extensions."""
        adapter = ConcreteAdapter()
        extensions = adapter.get_supported_extensions()
        
        assert isinstance(extensions, list)
        assert ".py" in extensions
        assert ".pyi" in extensions
    
    def test_concrete_adapter_language_name(self):
        """Test that concrete adapter returns language name."""
        adapter = ConcreteAdapter()
        name = adapter.get_language_name()
        
        assert isinstance(name, str)
        assert name == "Python"
    
    def test_supports_file_method(self):
        """Test the supports_file helper method."""
        adapter = ConcreteAdapter()
        
        assert adapter.supports_file(Path("/test/file.py"))
        assert adapter.supports_file(Path("/test/file.pyi"))
        assert not adapter.supports_file(Path("/test/file.java"))
        assert not adapter.supports_file(Path("/test/file.cs"))
    
    def test_supports_file_case_insensitive(self):
        """Test that supports_file is case-insensitive."""
        adapter = ConcreteAdapter()
        
        assert adapter.supports_file(Path("/test/FILE.PY"))
        assert adapter.supports_file(Path("/test/File.Py"))
        assert adapter.supports_file(Path("/test/file.PYI"))


class TestLanguageAdapterContract:
    """Test the contract that all adapters must follow."""
    
    def test_parse_file_returns_polyglot_result(self):
        """Test that parse_file returns PolyglotASTResult."""
        adapter = ConcreteAdapter()
        result = adapter.parse_file(Path("/test.py"))
        
        assert isinstance(result, PolyglotASTResult)
    
    def test_get_supported_extensions_returns_list_of_strings(self):
        """Test that get_supported_extensions returns list of strings."""
        adapter = ConcreteAdapter()
        extensions = adapter.get_supported_extensions()
        
        assert isinstance(extensions, list)
        assert all(isinstance(ext, str) for ext in extensions)
        assert all(ext.startswith(".") for ext in extensions)
    
    def test_get_language_name_returns_string(self):
        """Test that get_language_name returns a string."""
        adapter = ConcreteAdapter()
        name = adapter.get_language_name()
        
        assert isinstance(name, str)
        assert len(name) > 0
    
    def test_multiple_concrete_adapters(self):
        """Test that multiple adapters can coexist."""
        class PythonAdapter(LanguageAdapter):
            def parse_file(self, fp):
                return PolyglotASTResult(LanguageType.PYTHON, fp, [], [], [])
            def get_supported_extensions(self):
                return [".py"]
            def get_language_name(self):
                return "Python"
        
        class JavaAdapter(LanguageAdapter):
            def parse_file(self, fp):
                return PolyglotASTResult(LanguageType.JAVA, fp, [], [], [])
            def get_supported_extensions(self):
                return [".java"]
            def get_language_name(self):
                return "Java"
        
        py_adapter = PythonAdapter()
        java_adapter = JavaAdapter()
        
        assert py_adapter.get_language_name() == "Python"
        assert java_adapter.get_language_name() == "Java"
        assert py_adapter.supports_file(Path("test.py"))
        assert java_adapter.supports_file(Path("test.java"))
        assert not py_adapter.supports_file(Path("test.java"))
        assert not java_adapter.supports_file(Path("test.py"))
