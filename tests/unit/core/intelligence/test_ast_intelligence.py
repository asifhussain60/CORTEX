# © 2025-2026 Asif Hussain. All rights reserved.
# AC-ID: IR-001-01 - AST-Based Code Intelligence Tests
"""
Tests for AST Intelligence Engine.

PHASE-07: Holistic Intent Router Intelligence
AC-ID: IR-001-01 - AST-Based Code Intelligence

Tests cover:
- Python file AST parsing
- Function/class extraction
- Import and dependency identification
- Call graph construction
- Pattern detection
- Graceful degradation on syntax errors
"""

import ast
import tempfile
import textwrap
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from unittest.mock import MagicMock, patch

import pytest


# =============================================================================
# TEST FIXTURES
# =============================================================================


@pytest.fixture
def sample_python_code() -> str:
    """Sample Python code for AST parsing tests."""
    return textwrap.dedent('''
        """Module docstring."""
        
        from typing import List, Optional
        import os
        from pathlib import Path
        
        CONSTANT = "value"
        
        
        def simple_function(x: int, y: int = 10) -> int:
            """Add two numbers.
            
            Args:
                x: First number
                y: Second number
                
            Returns:
                Sum of x and y
            """
            return x + y
        
        
        def function_with_calls(data: List[str]) -> str:
            """Function that calls other functions."""
            result = simple_function(1, 2)
            return str(result)
        
        
        class BaseClass:
            """Base class with some methods."""
            
            def __init__(self, name: str) -> None:
                """Initialize with name."""
                self.name = name
            
            def get_name(self) -> str:
                """Return the name."""
                return self.name
        
        
        class DerivedClass(BaseClass):
            """Derived class that extends BaseClass."""
            
            def __init__(self, name: str, value: int) -> None:
                """Initialize with name and value."""
                super().__init__(name)
                self.value = value
            
            def compute(self) -> int:
                """Compute something."""
                return simple_function(self.value, 10)
    ''')


@pytest.fixture
def syntax_error_code() -> str:
    """Python code with syntax errors."""
    return textwrap.dedent('''
        def broken_function(x:
            return x +
        
        class Incomplete:
            def method(self
    ''')


@pytest.fixture
def singleton_pattern_code() -> str:
    """Python code with singleton pattern."""
    return textwrap.dedent('''
        class Singleton:
            """Singleton pattern implementation."""
            _instance = None
            
            def __new__(cls):
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                return cls._instance
    ''')


@pytest.fixture
def factory_pattern_code() -> str:
    """Python code with factory pattern."""
    return textwrap.dedent('''
        from abc import ABC, abstractmethod
        
        class Product(ABC):
            @abstractmethod
            def operation(self) -> str:
                pass
        
        class ConcreteProductA(Product):
            def operation(self) -> str:
                return "ProductA"
        
        class ConcreteProductB(Product):
            def operation(self) -> str:
                return "ProductB"
        
        class ProductFactory:
            """Factory for creating products."""
            
            @staticmethod
            def create_product(product_type: str) -> Product:
                """Create a product based on type."""
                if product_type == "A":
                    return ConcreteProductA()
                elif product_type == "B":
                    return ConcreteProductB()
                raise ValueError(f"Unknown product type: {product_type}")
    ''')


@pytest.fixture
def decorator_pattern_code() -> str:
    """Python code with decorator pattern."""
    return textwrap.dedent('''
        import functools
        from typing import Callable, Any
        
        def audit_log(func: Callable) -> Callable:
            """Decorator to log function calls."""
            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                print(f"Calling {func.__name__}")
                result = func(*args, **kwargs)
                print(f"Finished {func.__name__}")
                return result
            return wrapper
        
        def governance_check(rule: str) -> Callable:
            """Decorator factory for governance checks."""
            def decorator(func: Callable) -> Callable:
                @functools.wraps(func)
                def wrapper(*args: Any, **kwargs: Any) -> Any:
                    print(f"Checking rule: {rule}")
                    return func(*args, **kwargs)
                return wrapper
            return decorator
        
        @audit_log
        @governance_check("CORE-008")
        def governed_function(x: int) -> int:
            """A function with multiple decorators."""
            return x * 2
    ''')


@pytest.fixture
def temp_python_file(sample_python_code: str, tmp_path: Path) -> Path:
    """Create a temporary Python file with sample code."""
    file_path = tmp_path / "sample_module.py"
    file_path.write_text(sample_python_code)
    return file_path


# =============================================================================
# TEST CLASSES: AST PARSING
# =============================================================================


class TestASTParsing:
    """Tests for basic AST parsing functionality."""

    def test_parse_valid_python_file(
        self, temp_python_file: Path
    ) -> None:
        """Test parsing a valid Python file returns AST."""
        from cortex.core.intelligence.ast_intelligence import ASTIntelligenceEngine
        
        engine = ASTIntelligenceEngine()
        result = engine.parse_file(temp_python_file)
        
        assert result is not None
        assert result.success is True
        assert result.ast_tree is not None
        assert isinstance(result.ast_tree, ast.Module)

    def test_parse_returns_module_docstring(
        self, temp_python_file: Path
    ) -> None:
        """Test that module docstring is extracted."""
        from cortex.core.intelligence.ast_intelligence import ASTIntelligenceEngine
        
        engine = ASTIntelligenceEngine()
        result = engine.parse_file(temp_python_file)
        
        assert result.module_docstring == "Module docstring."

    def test_parse_extracts_imports(
        self, temp_python_file: Path
    ) -> None:
        """Test that imports are correctly extracted."""
        from cortex.core.intelligence.ast_intelligence import ASTIntelligenceEngine
        
        engine = ASTIntelligenceEngine()
        result = engine.parse_file(temp_python_file)
        
        assert "typing" in result.imports
        assert "os" in result.imports
        assert "pathlib" in result.imports
        # Check specific from imports
        assert "List" in result.from_imports.get("typing", [])
        assert "Optional" in result.from_imports.get("typing", [])
        assert "Path" in result.from_imports.get("pathlib", [])

    def test_parse_extracts_functions(
        self, temp_python_file: Path
    ) -> None:
        """Test that function definitions are extracted."""
        from cortex.core.intelligence.ast_intelligence import ASTIntelligenceEngine
        
        engine = ASTIntelligenceEngine()
        result = engine.parse_file(temp_python_file)
        
        func_names = [f.name for f in result.functions]
        assert "simple_function" in func_names
        assert "function_with_calls" in func_names

    def test_parse_extracts_function_signatures(
        self, temp_python_file: Path
    ) -> None:
        """Test that function signatures include parameters and return types."""
        from cortex.core.intelligence.ast_intelligence import ASTIntelligenceEngine
        
        engine = ASTIntelligenceEngine()
        result = engine.parse_file(temp_python_file)
        
        simple_func = next(
            f for f in result.functions if f.name == "simple_function"
        )
        
        assert len(simple_func.parameters) == 2
        assert simple_func.parameters[0].name == "x"
        assert simple_func.parameters[0].type_hint == "int"
        assert simple_func.parameters[1].name == "y"
        assert simple_func.parameters[1].default == "10"
        assert simple_func.return_type == "int"

    def test_parse_extracts_function_docstrings(
        self, temp_python_file: Path
    ) -> None:
        """Test that function docstrings are extracted."""
        from cortex.core.intelligence.ast_intelligence import ASTIntelligenceEngine
        
        engine = ASTIntelligenceEngine()
        result = engine.parse_file(temp_python_file)
        
        simple_func = next(
            f for f in result.functions if f.name == "simple_function"
        )
        
        assert simple_func.docstring is not None
        assert "Add two numbers" in simple_func.docstring

    def test_parse_extracts_classes(
        self, temp_python_file: Path
    ) -> None:
        """Test that class definitions are extracted."""
        from cortex.core.intelligence.ast_intelligence import ASTIntelligenceEngine
        
        engine = ASTIntelligenceEngine()
        result = engine.parse_file(temp_python_file)
        
        class_names = [c.name for c in result.classes]
        assert "BaseClass" in class_names
        assert "DerivedClass" in class_names

    def test_parse_extracts_class_hierarchy(
        self, temp_python_file: Path
    ) -> None:
        """Test that class inheritance is identified."""
        from cortex.core.intelligence.ast_intelligence import ASTIntelligenceEngine
        
        engine = ASTIntelligenceEngine()
        result = engine.parse_file(temp_python_file)
        
        derived = next(
            c for c in result.classes if c.name == "DerivedClass"
        )
        
        assert "BaseClass" in derived.bases

    def test_parse_extracts_class_methods(
        self, temp_python_file: Path
    ) -> None:
        """Test that class methods are extracted."""
        from cortex.core.intelligence.ast_intelligence import ASTIntelligenceEngine
        
        engine = ASTIntelligenceEngine()
        result = engine.parse_file(temp_python_file)
        
        base = next(c for c in result.classes if c.name == "BaseClass")
        
        method_names = [m.name for m in base.methods]
        assert "__init__" in method_names
        assert "get_name" in method_names

    def test_parse_extracts_constants(
        self, temp_python_file: Path
    ) -> None:
        """Test that module-level constants are extracted."""
        from cortex.core.intelligence.ast_intelligence import ASTIntelligenceEngine
        
        engine = ASTIntelligenceEngine()
        result = engine.parse_file(temp_python_file)
        
        assert "CONSTANT" in [c.name for c in result.constants]

    def test_parse_from_string(
        self, sample_python_code: str
    ) -> None:
        """Test parsing Python code from string."""
        from cortex.core.intelligence.ast_intelligence import ASTIntelligenceEngine
        
        engine = ASTIntelligenceEngine()
        result = engine.parse_string(sample_python_code)
        
        assert result.success is True
        assert len(result.functions) >= 2
        assert len(result.classes) >= 2


# =============================================================================
# TEST CLASSES: CALL GRAPH CONSTRUCTION
# =============================================================================


class TestCallGraphConstruction:
    """Tests for call graph building functionality."""

    def test_identifies_function_calls(
        self, temp_python_file: Path
    ) -> None:
        """Test that function calls within functions are identified."""
        from cortex.core.intelligence.ast_intelligence import ASTIntelligenceEngine
        from cortex.core.intelligence.call_graph import CallGraphBuilder
        
        engine = ASTIntelligenceEngine()
        parse_result = engine.parse_file(temp_python_file)
        
        builder = CallGraphBuilder()
        call_graph = builder.build(parse_result)
        
        # function_with_calls should call simple_function
        callers_of_simple = call_graph.get_callers("simple_function")
        assert "function_with_calls" in callers_of_simple

    def test_identifies_method_calls(
        self, temp_python_file: Path
    ) -> None:
        """Test that method calls are identified."""
        from cortex.core.intelligence.ast_intelligence import ASTIntelligenceEngine
        from cortex.core.intelligence.call_graph import CallGraphBuilder
        
        engine = ASTIntelligenceEngine()
        parse_result = engine.parse_file(temp_python_file)
        
        builder = CallGraphBuilder()
        call_graph = builder.build(parse_result)
        
        # DerivedClass.compute should call simple_function
        callers_of_simple = call_graph.get_callers("simple_function")
        assert "DerivedClass.compute" in callers_of_simple

    def test_identifies_super_calls(
        self, temp_python_file: Path
    ) -> None:
        """Test that super() calls are identified."""
        from cortex.core.intelligence.ast_intelligence import ASTIntelligenceEngine
        from cortex.core.intelligence.call_graph import CallGraphBuilder
        
        engine = ASTIntelligenceEngine()
        parse_result = engine.parse_file(temp_python_file)
        
        builder = CallGraphBuilder()
        call_graph = builder.build(parse_result)
        
        # DerivedClass.__init__ should call BaseClass.__init__ via super
        assert call_graph.has_super_call(
            "DerivedClass.__init__", "BaseClass.__init__"
        )

    def test_builds_complete_call_graph(
        self, temp_python_file: Path
    ) -> None:
        """Test that a complete call graph is built."""
        from cortex.core.intelligence.ast_intelligence import ASTIntelligenceEngine
        from cortex.core.intelligence.call_graph import CallGraphBuilder
        
        engine = ASTIntelligenceEngine()
        parse_result = engine.parse_file(temp_python_file)
        
        builder = CallGraphBuilder()
        call_graph = builder.build(parse_result)
        
        # Call graph should have nodes for all functions/methods
        assert call_graph.has_node("simple_function")
        assert call_graph.has_node("function_with_calls")
        assert call_graph.has_node("BaseClass.__init__")
        assert call_graph.has_node("DerivedClass.compute")

    def test_call_graph_edge_direction(
        self, temp_python_file: Path
    ) -> None:
        """Test that call graph edges point in correct direction (caller → callee)."""
        from cortex.core.intelligence.ast_intelligence import ASTIntelligenceEngine
        from cortex.core.intelligence.call_graph import CallGraphBuilder
        
        engine = ASTIntelligenceEngine()
        parse_result = engine.parse_file(temp_python_file)
        
        builder = CallGraphBuilder()
        call_graph = builder.build(parse_result)
        
        # Edge: function_with_calls → simple_function
        callees = call_graph.get_callees("function_with_calls")
        assert "simple_function" in callees


# =============================================================================
# TEST CLASSES: PATTERN DETECTION
# =============================================================================


class TestPatternDetection:
    """Tests for architectural pattern detection."""

    def test_detects_singleton_pattern(
        self, singleton_pattern_code: str
    ) -> None:
        """Test detection of singleton pattern."""
        from cortex.core.intelligence.ast_intelligence import ASTIntelligenceEngine
        from cortex.core.intelligence.pattern_detector import PatternDetector
        
        engine = ASTIntelligenceEngine()
        parse_result = engine.parse_string(singleton_pattern_code)
        
        detector = PatternDetector()
        patterns = detector.detect_patterns(parse_result)
        
        singleton_patterns = [
            p for p in patterns if p.pattern_type == "SINGLETON"
        ]
        assert len(singleton_patterns) >= 1
        assert singleton_patterns[0].class_name == "Singleton"

    def test_detects_factory_pattern(
        self, factory_pattern_code: str
    ) -> None:
        """Test detection of factory pattern."""
        from cortex.core.intelligence.ast_intelligence import ASTIntelligenceEngine
        from cortex.core.intelligence.pattern_detector import PatternDetector
        
        engine = ASTIntelligenceEngine()
        parse_result = engine.parse_string(factory_pattern_code)
        
        detector = PatternDetector()
        patterns = detector.detect_patterns(parse_result)
        
        factory_patterns = [
            p for p in patterns if p.pattern_type == "FACTORY"
        ]
        assert len(factory_patterns) >= 1
        assert factory_patterns[0].class_name == "ProductFactory"

    def test_detects_decorator_pattern(
        self, decorator_pattern_code: str
    ) -> None:
        """Test detection of decorator usage."""
        from cortex.core.intelligence.ast_intelligence import ASTIntelligenceEngine
        from cortex.core.intelligence.pattern_detector import PatternDetector
        
        engine = ASTIntelligenceEngine()
        parse_result = engine.parse_string(decorator_pattern_code)
        
        detector = PatternDetector()
        patterns = detector.detect_patterns(parse_result)
        
        decorator_patterns = [
            p for p in patterns if p.pattern_type == "DECORATED_FUNCTION"
        ]
        assert len(decorator_patterns) >= 1
        
        # Should identify governed_function with its decorators
        governed = next(
            p for p in decorator_patterns 
            if p.function_name == "governed_function"
        )
        assert "audit_log" in governed.decorators
        assert any("governance_check" in d for d in governed.decorators)

    def test_detects_decorator_chains(
        self, decorator_pattern_code: str
    ) -> None:
        """Test detection of decorator chains."""
        from cortex.core.intelligence.ast_intelligence import ASTIntelligenceEngine
        from cortex.core.intelligence.pattern_detector import PatternDetector
        
        engine = ASTIntelligenceEngine()
        parse_result = engine.parse_string(decorator_pattern_code)
        
        detector = PatternDetector()
        patterns = detector.detect_patterns(parse_result)
        
        # Find decorator chain pattern
        chain_patterns = [
            p for p in patterns if p.pattern_type == "DECORATOR_CHAIN"
        ]
        assert len(chain_patterns) >= 1
        
        # governed_function has 2 decorators = a chain
        chain = chain_patterns[0]
        assert len(chain.decorators) >= 2


# =============================================================================
# TEST CLASSES: DEPENDENCY MAPPING
# =============================================================================


class TestDependencyMapping:
    """Tests for import dependency mapping."""

    def test_maps_standard_library_imports(
        self, temp_python_file: Path
    ) -> None:
        """Test mapping of standard library imports."""
        from cortex.core.intelligence.ast_intelligence import ASTIntelligenceEngine
        from cortex.core.intelligence.dependency_mapper import DependencyMapper
        
        engine = ASTIntelligenceEngine()
        parse_result = engine.parse_file(temp_python_file)
        
        mapper = DependencyMapper()
        deps = mapper.map_dependencies(parse_result)
        
        stdlib_deps = deps.get_standard_library()
        assert "os" in stdlib_deps
        assert "typing" in stdlib_deps
        assert "pathlib" in stdlib_deps

    def test_classifies_import_types(
        self, temp_python_file: Path
    ) -> None:
        """Test classification of import types (standard, third-party, local)."""
        from cortex.core.intelligence.ast_intelligence import ASTIntelligenceEngine
        from cortex.core.intelligence.dependency_mapper import DependencyMapper
        
        engine = ASTIntelligenceEngine()
        parse_result = engine.parse_file(temp_python_file)
        
        mapper = DependencyMapper()
        deps = mapper.map_dependencies(parse_result)
        
        # All imports in sample code are standard library
        assert deps.third_party == []
        assert deps.local == []

    def test_builds_import_graph(
        self, tmp_path: Path
    ) -> None:
        """Test building import graph from multiple files."""
        from cortex.core.intelligence.ast_intelligence import ASTIntelligenceEngine
        from cortex.core.intelligence.dependency_mapper import DependencyMapper
        
        # Create module_a.py
        module_a = tmp_path / "module_a.py"
        module_a.write_text(textwrap.dedent('''
            """Module A."""
            def func_a() -> str:
                return "a"
        '''))
        
        # Create module_b.py that imports module_a
        module_b = tmp_path / "module_b.py"
        module_b.write_text(textwrap.dedent('''
            """Module B imports Module A."""
            from module_a import func_a
            
            def func_b() -> str:
                return func_a() + "b"
        '''))
        
        engine = ASTIntelligenceEngine()
        # Explicitly mark module_a as local since it's in the same directory
        mapper = DependencyMapper(local_packages={"module_a"})
        
        # Parse both files
        result_a = engine.parse_file(module_a)
        result_b = engine.parse_file(module_b)
        
        # Map dependencies
        deps_b = mapper.map_dependencies(result_b)
        
        assert "module_a" in [d.module for d in deps_b.local]


# =============================================================================
# TEST CLASSES: GRACEFUL DEGRADATION
# =============================================================================


class TestGracefulDegradation:
    """Tests for graceful handling of syntax errors."""

    def test_handles_syntax_errors(
        self, syntax_error_code: str
    ) -> None:
        """Test that syntax errors are handled gracefully."""
        from cortex.core.intelligence.ast_intelligence import ASTIntelligenceEngine
        
        engine = ASTIntelligenceEngine()
        result = engine.parse_string(syntax_error_code)
        
        assert result.success is False
        assert result.error is not None
        assert "syntax" in result.error.lower() or "parse" in result.error.lower()

    def test_syntax_error_includes_location(
        self, syntax_error_code: str
    ) -> None:
        """Test that syntax errors include line/column information."""
        from cortex.core.intelligence.ast_intelligence import ASTIntelligenceEngine
        
        engine = ASTIntelligenceEngine()
        result = engine.parse_string(syntax_error_code)
        
        assert result.error_line is not None
        assert result.error_column is not None

    def test_handles_nonexistent_file(self) -> None:
        """Test handling of nonexistent file."""
        from cortex.core.intelligence.ast_intelligence import ASTIntelligenceEngine
        
        engine = ASTIntelligenceEngine()
        result = engine.parse_file(Path("/nonexistent/path/file.py"))
        
        assert result.success is False
        assert "not found" in result.error.lower() or "exist" in result.error.lower()

    def test_handles_empty_file(
        self, tmp_path: Path
    ) -> None:
        """Test handling of empty Python file."""
        from cortex.core.intelligence.ast_intelligence import ASTIntelligenceEngine
        
        empty_file = tmp_path / "empty.py"
        empty_file.write_text("")
        
        engine = ASTIntelligenceEngine()
        result = engine.parse_file(empty_file)
        
        assert result.success is True
        assert len(result.functions) == 0
        assert len(result.classes) == 0

    def test_handles_binary_file(
        self, tmp_path: Path
    ) -> None:
        """Test handling of non-Python (binary) file."""
        from cortex.core.intelligence.ast_intelligence import ASTIntelligenceEngine
        
        binary_file = tmp_path / "binary.py"
        binary_file.write_bytes(b'\x00\x01\x02\x03')
        
        engine = ASTIntelligenceEngine()
        result = engine.parse_file(binary_file)
        
        assert result.success is False
        assert result.error is not None


# =============================================================================
# TEST CLASSES: INTEGRATION
# =============================================================================


class TestASTIntelligenceIntegration:
    """Integration tests for AST intelligence engine."""

    def test_full_analysis_pipeline(
        self, temp_python_file: Path
    ) -> None:
        """Test complete analysis pipeline from file to insights."""
        from cortex.core.intelligence.ast_intelligence import ASTIntelligenceEngine
        from cortex.core.intelligence.call_graph import CallGraphBuilder
        from cortex.core.intelligence.dependency_mapper import DependencyMapper
        
        engine = ASTIntelligenceEngine()
        result = engine.parse_file(temp_python_file)
        
        assert result.success is True
        
        # Build call graph
        call_builder = CallGraphBuilder()
        call_graph = call_builder.build(result)
        
        assert call_graph is not None
        assert call_graph.node_count > 0
        
        # Map dependencies
        dep_mapper = DependencyMapper()
        deps = dep_mapper.map_dependencies(result)
        
        assert deps is not None
        assert len(deps.get_standard_library()) > 0

    def test_analysis_result_serialization(
        self, temp_python_file: Path
    ) -> None:
        """Test that analysis results can be serialized to dict."""
        from cortex.core.intelligence.ast_intelligence import ASTIntelligenceEngine
        
        engine = ASTIntelligenceEngine()
        result = engine.parse_file(temp_python_file)
        
        serialized = result.to_dict()
        
        assert isinstance(serialized, dict)
        assert "functions" in serialized
        assert "classes" in serialized
        assert "imports" in serialized
        assert "success" in serialized

    def test_analysis_caching(
        self, temp_python_file: Path
    ) -> None:
        """Test that repeated analysis uses cache."""
        from cortex.core.intelligence.ast_intelligence import ASTIntelligenceEngine
        
        engine = ASTIntelligenceEngine(enable_cache=True)
        
        # First parse
        result1 = engine.parse_file(temp_python_file)
        
        # Second parse should use cache
        result2 = engine.parse_file(temp_python_file)
        
        assert result1.success is True
        assert result2.success is True
        # Cache hit should return same data
        assert result1.functions == result2.functions
