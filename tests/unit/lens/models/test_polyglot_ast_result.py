"""
Unit tests for PolyglotASTResult data model.

Tests the unified AST result structure that works across Python, C#, Java, TypeScript, JavaScript.

Author: Asif Hussain
Created: 2026-02-04
Authority: LENS-MULTI-LANGUAGE-ENHANCEMENT.yaml Phase 0
"""

import pytest
from pathlib import Path
from typing import List, Dict, Any

# Direct import to avoid circular dependency in cortex.lens.__init__.py
# Use importlib to load the module directly without triggering package imports
import importlib.util

# Calculate path: tests/unit/lens/models → cortex/lens/models/polyglot_ast_result.py
test_file = Path(__file__)  # tests/unit/lens/models/test_polyglot_ast_result.py
tests_dir = test_file.parent.parent.parent.parent  # tests/
project_root = tests_dir.parent  # CORTEX/
model_file = project_root / "cortex" / "lens" / "models" / "polyglot_ast_result.py"

spec = importlib.util.spec_from_file_location("polyglot_ast_result", model_file)
polyglot_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(polyglot_module)

PolyglotASTResult = polyglot_module.PolyglotASTResult
ClassInfo = polyglot_module.ClassInfo
FunctionInfo = polyglot_module.FunctionInfo
ImportInfo = polyglot_module.ImportInfo
LanguageType = polyglot_module.LanguageType


class TestPolyglotASTResult:
    """Test suite for PolyglotASTResult model."""

    def test_create_empty_result(self):
        """Test creating an empty AST result."""
        result = PolyglotASTResult(
            file_path=Path("/test/file.py"),
            language=LanguageType.PYTHON,
            classes=[],
            functions=[],
            imports=[],
        )
        
        assert result.file_path == Path("/test/file.py")
        assert result.language == LanguageType.PYTHON
        assert len(result.classes) == 0
        assert len(result.functions) == 0
        assert len(result.imports) == 0

    def test_create_python_result_with_classes(self):
        """Test creating AST result with Python classes."""
        classes = [
            ClassInfo(
                name="OrderService",
                line_start=10,
                line_end=50,
                methods=["create_order", "update_order"],
                base_classes=["BaseService"],
                docstring="Handles order management",
            )
        ]
        
        result = PolyglotASTResult(
            file_path=Path("/src/services/order_service.py"),
            language=LanguageType.PYTHON,
            classes=classes,
            functions=[],
            imports=[],
        )
        
        assert len(result.classes) == 1
        assert result.classes[0].name == "OrderService"
        assert result.classes[0].line_start == 10
        assert result.classes[0].line_end == 50
        assert "create_order" in result.classes[0].methods

    def test_create_csharp_result_with_namespaces(self):
        """Test creating AST result with C# namespaces."""
        classes = [
            ClassInfo(
                name="CustomerRepository",
                line_start=15,
                line_end=100,
                methods=["GetById", "Save", "Delete"],
                base_classes=["IRepository<Customer>"],
                docstring="Repository for customer data access",
                namespace="MyApp.Data.Repositories",
            )
        ]
        
        result = PolyglotASTResult(
            file_path=Path("/src/Data/Repositories/CustomerRepository.cs"),
            language=LanguageType.CSHARP,
            classes=classes,
            functions=[],
            imports=[],
        )
        
        assert result.language == LanguageType.CSHARP
        assert result.classes[0].namespace == "MyApp.Data.Repositories"

    def test_create_javascript_result_with_functions(self):
        """Test creating AST result with standalone JavaScript functions."""
        functions = [
            FunctionInfo(
                name="fetchOrders",
                line_start=5,
                line_end=15,
                parameters=["customerId", "options"],
                is_async=True,
                docstring="Fetches orders for a customer",
            )
        ]
        
        result = PolyglotASTResult(
            file_path=Path("/src/api/orders.js"),
            language=LanguageType.JAVASCRIPT,
            classes=[],
            functions=functions,
            imports=[],
        )
        
        assert len(result.functions) == 1
        assert result.functions[0].name == "fetchOrders"
        assert result.functions[0].is_async is True

    def test_create_typescript_result_with_interfaces(self):
        """Test creating AST result with TypeScript interfaces."""
        classes = [
            ClassInfo(
                name="OrderDTO",
                line_start=8,
                line_end=20,
                methods=[],
                base_classes=["IOrder"],
                docstring="Data transfer object for orders",
                is_interface=True,
            )
        ]
        
        result = PolyglotASTResult(
            file_path=Path("/src/types/order.ts"),
            language=LanguageType.TYPESCRIPT,
            classes=classes,
            functions=[],
            imports=[],
        )
        
        assert result.classes[0].is_interface is True

    def test_imports_parsing(self):
        """Test import statement parsing."""
        imports = [
            ImportInfo(
                module="typing",
                names=["List", "Dict", "Optional"],
                line=1,
            ),
            ImportInfo(
                module="pathlib",
                names=["Path"],
                line=2,
            ),
        ]
        
        result = PolyglotASTResult(
            file_path=Path("/src/models.py"),
            language=LanguageType.PYTHON,
            classes=[],
            functions=[],
            imports=imports,
        )
        
        assert len(result.imports) == 2
        assert result.imports[0].module == "typing"
        assert "Optional" in result.imports[0].names


class TestClassInfo:
    """Test suite for ClassInfo model."""

    def test_create_basic_class(self):
        """Test creating a basic class info."""
        cls = ClassInfo(
            name="User",
            line_start=10,
            line_end=30,
            methods=["get_name", "set_name"],
            base_classes=[],
            docstring="User model",
        )
        
        assert cls.name == "User"
        assert len(cls.methods) == 2

    def test_class_with_namespace(self):
        """Test class with namespace (C#/Java)."""
        cls = ClassInfo(
            name="OrderService",
            line_start=5,
            line_end=50,
            methods=["ProcessOrder"],
            base_classes=["BaseService"],
            docstring="",
            namespace="MyApp.Services",
        )
        
        assert cls.namespace == "MyApp.Services"

    def test_interface_flag(self):
        """Test interface detection (TypeScript/Java)."""
        interface = ClassInfo(
            name="IRepository",
            line_start=1,
            line_end=10,
            methods=["GetById", "Save"],
            base_classes=[],
            docstring="",
            is_interface=True,
        )
        
        assert interface.is_interface is True


class TestFunctionInfo:
    """Test suite for FunctionInfo model."""

    def test_create_basic_function(self):
        """Test creating a basic function info."""
        func = FunctionInfo(
            name="calculate_total",
            line_start=15,
            line_end=25,
            parameters=["items", "tax_rate"],
            is_async=False,
            docstring="Calculates order total",
        )
        
        assert func.name == "calculate_total"
        assert len(func.parameters) == 2

    def test_async_function(self):
        """Test async function detection."""
        func = FunctionInfo(
            name="fetch_data",
            line_start=10,
            line_end=20,
            parameters=["url"],
            is_async=True,
            docstring="",
        )
        
        assert func.is_async is True


class TestLanguageType:
    """Test suite for LanguageType enum."""

    def test_all_supported_languages(self):
        """Test all supported language types."""
        assert LanguageType.PYTHON.value == "python"
        assert LanguageType.CSHARP.value == "csharp"
        assert LanguageType.JAVA.value == "java"
        assert LanguageType.TYPESCRIPT.value == "typescript"
        assert LanguageType.JAVASCRIPT.value == "javascript"

    def test_language_from_extension(self):
        """Test deriving language from file extension."""
        assert LanguageType.from_extension(".py") == LanguageType.PYTHON
        assert LanguageType.from_extension(".cs") == LanguageType.CSHARP
        assert LanguageType.from_extension(".java") == LanguageType.JAVA
        assert LanguageType.from_extension(".ts") == LanguageType.TYPESCRIPT
        assert LanguageType.from_extension(".js") == LanguageType.JAVASCRIPT


class TestImportInfo:
    """Test suite for ImportInfo model."""

    def test_create_import(self):
        """Test creating an import info."""
        imp = ImportInfo(
            module="os.path",
            names=["join", "exists"],
            line=3,
        )
        
        assert imp.module == "os.path"
        assert "join" in imp.names
        assert imp.line == 3
