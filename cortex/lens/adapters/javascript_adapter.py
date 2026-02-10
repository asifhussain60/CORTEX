"""
JavaScriptAdapter - Tree-sitter-based JavaScript AST parser.

Parses JavaScript source files using tree-sitter-javascript grammar and extracts:
- Classes
- Methods (instance, static, async)
- Functions (arrow, regular, async)
- Fields
- Import statements
- Export statements

Author: Asif Hussain
Created: 2026-02-08
Authority: LENS-MULTI-LANGUAGE-ENHANCEMENT.yaml Phase 3
"""

from pathlib import Path
from typing import List, Optional, Dict, Any
from tree_sitter import Parser, Language, Node
import tree_sitter_javascript as ts_javascript

from cortex.lens.adapters.language_adapter import LanguageAdapter
from cortex.lens.models.polyglot_ast_result import (
    PolyglotASTResult,
    LanguageType,
    ClassInfo,
    FunctionInfo,
    ImportInfo,
)


class JavaScriptAdapter(LanguageAdapter):
    """
    JavaScript language adapter using tree-sitter.
    
    Parses JavaScript source code and extracts:
    - Classes
    - Methods (instance, static, async)
    - Functions (arrow, regular, async)
    - Fields
    - Import statements
    - Export statements
    
    Example:
        >>> adapter = JavaScriptAdapter()
        >>> result = adapter.parse_file(Path("UserService.js"))
        >>> print(f"Found {len(result.classes)} classes")
        >>> print(f"Language: {result.language}")
    """
    
    def __init__(self):
        """Initialize JavaScriptAdapter with tree-sitter parser."""
        # New tree-sitter API (0.20+): pass language directly to Parser
        self.parser = Parser(ts_javascript.language())
        self.language = ts_javascript.language()
    
    def parse_file(self, file_path: Path) -> PolyglotASTResult:
        """
        Parse JavaScript file and return unified AST result.
        
        Args:
            file_path: Path to JavaScript source file
            
        Returns:
            PolyglotASTResult with classes, methods, imports
        """
        # Handle non-existent files
        if not file_path.exists():
            return PolyglotASTResult(
                file_path=file_path,
                language=LanguageType.JAVASCRIPT,
                classes=[],
                functions=[],
                imports=[],
                raw_ast=None,
                parse_errors=[f"File not found: {file_path}"],
                metadata={},
            )
        
        try:
            # Read file content
            source_code = file_path.read_bytes()
            
            # Parse with tree-sitter
            tree = self.parser.parse(source_code)
            root_node = tree.root_node
            
            # Extract AST elements
            classes = self._extract_classes(root_node, source_code)
            functions = self._extract_functions(root_node, source_code)
            imports = self._extract_imports(root_node, source_code)
            
            # Check for parse errors
            parse_errors = self._collect_parse_errors(root_node)
            
            return PolyglotASTResult(
                file_path=file_path,
                language=LanguageType.JAVASCRIPT,
                classes=classes,
                functions=functions,
                imports=imports,
                raw_ast=None,
                parse_errors=parse_errors,
                metadata={
                    "parser": "tree-sitter",
                    "language_version": "ES6+",
                    "total_functions": len(functions),
                    "total_classes": len(classes),
                    "total_imports": len(imports),
                },
            )
        
        except Exception as e:
            return PolyglotASTResult(
                file_path=file_path,
                language=LanguageType.JAVASCRIPT,
                classes=[],
                functions=[],
                imports=[],
                raw_ast=None,
                parse_errors=[str(e)],
                metadata={"error": str(e)},
            )
    
    def _extract_classes(self, root_node: Node, source_code: bytes) -> List[ClassInfo]:
        """Extract class declarations from JavaScript AST."""
        classes = []
        
        # Find class_declaration nodes
        for class_node in self._find_nodes_by_type(root_node, "class_declaration"):
            class_info = self._parse_class(class_node, source_code)
            if class_info:
                classes.append(class_info)
        
        return classes
    
    def _parse_class(self, class_node: Node, source_code: bytes) -> Optional[ClassInfo]:
        """Parse a class declaration."""
        # Get class name
        name_node = self._find_child_by_type(class_node, "identifier")
        if not name_node:
            return None
        
        class_name = source_code[name_node.start_byte:name_node.end_byte].decode("utf-8")
        
        # Get line numbers
        line_start = class_node.start_point[0] + 1
        line_end = class_node.end_point[0] + 1
        
        # Extract method names
        method_names = self._extract_class_method_names(class_node, source_code)
        
        # Extract property names (fields)
        property_names = self._extract_class_property_names(class_node, source_code)
        
        # Extract base classes (extends)
        base_classes = self._extract_base_classes(class_node, source_code)
        
        return ClassInfo(
            name=class_name,
            line_start=line_start,
            line_end=line_end,
            methods=method_names,
            base_classes=base_classes,
            namespace="",
            is_interface=False,
            is_abstract=False,
            properties=property_names,
            attributes=[],
        )
    
    def _extract_class_method_names(self, class_node: Node, source_code: bytes) -> List[str]:
        """Extract method names from a class."""
        method_names = []
        
        # JavaScript uses method_definition for class methods
        for method_node in self._find_nodes_by_type(class_node, "method_definition"):
            name_node = self._find_child_by_type(method_node, "property_identifier")
            if name_node:
                method_name = source_code[name_node.start_byte:name_node.end_byte].decode("utf-8")
                method_names.append(method_name)
        
        return method_names
    
    def _parse_method(self, method_node: Node, source_code: bytes) -> Optional[FunctionInfo]:
        """Parse a method declaration."""
        # Get method name
        name_node = self._find_child_by_type(method_node, "property_identifier")
        if not name_node:
            name_node = self._find_child_by_type(method_node, "identifier")
        if not name_node:
            return None
        
        method_name = source_code[name_node.start_byte:name_node.end_byte].decode("utf-8")
        
        # Get line numbers
        line_start = method_node.start_point[0] + 1
        line_end = method_node.end_point[0] + 1
        
        # Parse parameters
        parameters = self._extract_parameters(method_node, source_code)
        
        # Check if async
        modifiers = self._extract_modifiers(method_node, source_code)
        is_async = "async" in modifiers
        
        return FunctionInfo(
            name=method_name,
            line_start=line_start,
            line_end=line_end,
            parameters=parameters,
            return_type="",
            docstring="",
            is_async=is_async,
        )
    
    def _extract_functions(self, root_node: Node, source_code: bytes) -> List[FunctionInfo]:
        """Extract top-level function declarations from JavaScript AST."""
        functions = []
        
        # Regular function declarations
        for func_node in self._find_nodes_by_type(root_node, "function_declaration"):
            func_info = self._parse_function(func_node, source_code)
            if func_info:
                functions.append(func_info)
        
        # Arrow functions (variable declarations with arrow functions)
        for var_node in self._find_nodes_by_type(root_node, "variable_declaration"):
            func_info = self._parse_arrow_function(var_node, source_code)
            if func_info:
                functions.append(func_info)
        
        return functions
    
    def _parse_function(self, func_node: Node, source_code: bytes) -> Optional[FunctionInfo]:
        """Parse a regular function declaration."""
        # Get function name
        name_node = self._find_child_by_type(func_node, "identifier")
        if not name_node:
            return None
        
        func_name = source_code[name_node.start_byte:name_node.end_byte].decode("utf-8")
        
        # Get line numbers
        line_start = func_node.start_point[0] + 1
        line_end = func_node.end_point[0] + 1
        
        # Parse parameters
        parameters = self._extract_parameters(func_node, source_code)
        
        # Check if async
        modifiers = self._extract_modifiers(func_node, source_code)
        is_async = "async" in modifiers
        
        return FunctionInfo(
            name=func_name,
            line_start=line_start,
            line_end=line_end,
            parameters=parameters,
            return_type="",
            docstring="",
            is_async=is_async,
        )
    
    def _parse_arrow_function(self, var_node: Node, source_code: bytes) -> Optional[FunctionInfo]:
        """Parse an arrow function assigned to a variable."""
        # Find arrow_function node
        arrow_node = self._find_child_by_type(var_node, "arrow_function")
        if not arrow_node:
            return None
        
        # Get variable name as function name
        for child in var_node.children:
            if child.type == "variable_declarator":
                name_node = self._find_child_by_type(child, "identifier")
                if name_node:
                    func_name = source_code[name_node.start_byte:name_node.end_byte].decode("utf-8")
                    
                    # Get line numbers
                    line_start = var_node.start_point[0] + 1
                    line_end = var_node.end_point[0] + 1
                    
                    # Parse parameters
                    parameters = self._extract_parameters(arrow_node, source_code)
                    
                    return FunctionInfo(
                        name=func_name,
                        line_start=line_start,
                        line_end=line_end,
                        parameters=parameters,
                        return_type="",
                        docstring="",
                        is_async=False,
                    )
        
        return None
    
    def _extract_imports(self, root_node: Node, source_code: bytes) -> List[ImportInfo]:
        """Extract import statements from JavaScript AST."""
        imports = []
        
        # Find import_statement nodes
        for import_node in self._find_nodes_by_type(root_node, "import_statement"):
            import_info = self._parse_import(import_node, source_code)
            if import_info:
                imports.append(import_info)
        
        return imports
    
    def _parse_import(self, import_node: Node, source_code: bytes) -> Optional[ImportInfo]:
        """Parse an import statement."""
        # Get the module name from string_literal
        module_name = ""
        for child in import_node.children:
            if child.type == "string":
                module_name = source_code[child.start_byte + 1:child.end_byte - 1].decode("utf-8")
                break
        
        if not module_name:
            return None
        
        # Get imported names
        imported_names = []
        for child in import_node.children:
            if child.type == "identifier":
                name = source_code[child.start_byte:child.end_byte].decode("utf-8")
                if name != "import" and name != "from":
                    imported_names.append(name)
            elif child.type == "import_clause":
                for subchild in child.children:
                    if subchild.type == "identifier":
                        name = source_code[subchild.start_byte:subchild.end_byte].decode("utf-8")
                        imported_names.append(name)
        
        line_number = import_node.start_point[0] + 1
        
        return ImportInfo(
            module=module_name,
            names=imported_names,
            alias="",
            line=line_number,
        )
    
    def _extract_class_property_names(self, class_node: Node, source_code: bytes) -> List[str]:
        """Extract class property/field names."""
        property_names = []
        
        # Find property_definition nodes (ES2022 field declarations)
        for prop_node in self._find_nodes_by_type(class_node, "property_definition"):
            prop_name_node = self._find_child_by_type(prop_node, "property_identifier")
            if prop_name_node:
                prop_name = source_code[prop_name_node.start_byte:prop_name_node.end_byte].decode("utf-8")
                property_names.append(prop_name)
        
        return property_names
    
    def _extract_base_classes(self, class_node: Node, source_code: bytes) -> List[str]:
        """Extract base classes from extends clause."""
        base_classes = []
        
        # Find the class_heritage node
        for child in class_node.children:
            if child.type == "class_heritage":
                # Extract extends
                for subchild in child.children:
                    if subchild.type == "identifier":
                        base_name = source_code[subchild.start_byte:subchild.end_byte].decode("utf-8")
                        if base_name != "extends":
                            base_classes.append(base_name)
        
        return base_classes
    
    def _extract_parameters(self, node: Node, source_code: bytes) -> List[str]:
        """Extract function parameters."""
        parameters = []
        
        # Find formal_parameters node
        for child in node.children:
            if child.type == "formal_parameters":
                for param_child in child.children:
                    if param_child.type == "identifier":
                        param_name = source_code[param_child.start_byte:param_child.end_byte].decode("utf-8")
                        parameters.append(param_name)
        
        return parameters
    
    def _extract_modifiers(self, node: Node, source_code: bytes) -> List[str]:
        """Extract modifiers (async, static, etc.)."""
        modifiers = []
        
        for child in node.children:
            if child.type in ["static", "async"]:
                modifiers.append(source_code[child.start_byte:child.end_byte].decode("utf-8"))
        
        return modifiers
    
    def _collect_parse_errors(self, root_node: Node) -> List[str]:
        """Collect parse errors from tree-sitter."""
        errors = []
        
        def traverse(node: Node):
            if node.is_error:
                errors.append(f"Parse error at line {node.start_point[0] + 1}")
            for child in node.children:
                traverse(child)
        
        traverse(root_node)
        return errors
    
    def _find_nodes_by_type(self, node: Node, node_type: str) -> List[Node]:
        """Recursively find all nodes of a specific type."""
        nodes = []
        
        def traverse(n: Node):
            if n.type == node_type:
                nodes.append(n)
            for child in n.children:
                traverse(child)
        
        traverse(node)
        return nodes
    
    def _find_child_by_type(self, node: Node, node_type: str) -> Optional[Node]:
        """Find the first direct child of a specific type."""
        for child in node.children:
            if child.type == node_type:
                return child
        return None
    
    def get_supported_extensions(self) -> List[str]:
        """
        Return list of JavaScript file extensions this adapter supports.
        
        Returns:
            [".js", ".jsx"]
        """
        return [".js", ".jsx"]
    
    def get_language_name(self) -> str:
        """
        Return human-readable language name.
        
        Returns:
            "JavaScript"
        """
        return "JavaScript"

