"""
JavaAdapter - Tree-sitter-based Java AST parser.

Parses Java source files using tree-sitter-java grammar and extracts:
- Classes (public, private, abstract, final)
- Interfaces
- Methods (public, private, protected, static, synchronized)
- Fields
- Import statements
- Package declarations
- Annotations (@Override, @Deprecated, etc.)

Author: Asif Hussain
Created: 2026-02-04
Authority: LENS-MULTI-LANGUAGE-ENHANCEMENT.yaml Phase 3
"""

from pathlib import Path
from typing import List, Optional, Dict, Any
from tree_sitter import Parser, Language, Node

from cortex.lens.adapters.language_adapter import LanguageAdapter
from cortex.lens.models.polyglot_ast_result import (
    PolyglotASTResult,
    LanguageType,
    ClassInfo,
    FunctionInfo,
    ImportInfo,
)


class JavaAdapter(LanguageAdapter):
    """
    Java language adapter using tree-sitter.
    
    Parses Java source code and extracts:
    - Classes, interfaces, enums
    - Methods (instance, static, abstract, synchronized)
    - Fields
    - Import statements
    - Package declarations
    - Annotations
    - Access modifiers
    
    Example:
        >>> adapter = JavaAdapter()
        >>> result = adapter.parse_file(Path("UserService.java"))
        >>> print(f"Found {len(result.classes)} classes")
        >>> print(f"Language: {result.language}")
    """
    
    def __init__(self):
        """Initialize JavaAdapter with tree-sitter parser (requires tree-sitter-java)."""
        try:
            import tree_sitter_java as ts_java
            self.language = Language(ts_java.language())
            self.parser = Parser(self.language)
        except ImportError:
            # Fallback if Java not installed
            self.language = None
            self.parser = None
    
    def parse_file(self, file_path: Path) -> PolyglotASTResult:
        """
        Parse Java file and return unified AST result.
        
        Args:
            file_path: Path to Java source file
            
        Returns:
            PolyglotASTResult with classes, methods, imports
        """
        # Handle non-existent files
        if not file_path.exists():
            return PolyglotASTResult(
                file_path=file_path,
                language=LanguageType.JAVA,
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
            package = self._extract_package(root_node, source_code)
            
            # Check for parse errors
            parse_errors = self._collect_parse_errors(root_node)
            
            return PolyglotASTResult(
                file_path=file_path,
                language=LanguageType.JAVA,
                classes=classes,
                functions=functions,
                imports=imports,
                raw_ast=root_node,
                parse_errors=parse_errors,
                metadata={"package": package} if package else {},
            )
        except Exception as e:
            return PolyglotASTResult(
                file_path=file_path,
                language=LanguageType.JAVA,
                classes=[],
                functions=[],
                imports=[],
                raw_ast=None,
                parse_errors=[f"Parse error: {str(e)}"],
                metadata={},
            )
    
    def get_supported_extensions(self) -> List[str]:
        """
        Get Java file extensions.
        
        Returns:
            List of extensions: [".java"]
        """
        return [".java"]
    
    def get_language_name(self) -> str:
        """
        Get human-readable language name.
        
        Returns:
            "java"
        """
        return "java"
    
    def _extract_classes(self, node: Node, source_code: bytes) -> List[ClassInfo]:
        """Extract all class and interface declarations from AST."""
        classes = []
        
        # Find all class_declaration nodes
        for class_node in self._find_nodes_by_type(node, "class_declaration"):
            class_info = self._parse_class(class_node, source_code)
            if class_info:
                classes.append(class_info)
        
        # Find all interface_declaration nodes
        for interface_node in self._find_nodes_by_type(node, "interface_declaration"):
            interface_info = self._parse_interface(interface_node, source_code)
            if interface_info:
                classes.append(interface_info)
        
        # Find all enum_declaration nodes (treat as special classes)
        for enum_node in self._find_nodes_by_type(node, "enum_declaration"):
            enum_info = self._parse_enum(enum_node, source_code)
            if enum_info:
                classes.append(enum_info)
        
        return classes
    
    def _parse_class(self, class_node: Node, source_code: bytes) -> Optional[ClassInfo]:
        """Parse a single class declaration."""
        # Get class name
        name_node = self._find_child_by_type(class_node, "identifier")
        if not name_node:
            return None
        
        class_name = source_code[name_node.start_byte:name_node.end_byte].decode("utf-8")
        
        # Get line numbers
        line_start = class_node.start_point[0] + 1
        line_end = class_node.end_point[0] + 1
        
        # Parse methods
        methods = self._extract_class_methods(class_node, source_code)
        
        # Parse fields
        properties = self._extract_class_fields(class_node, source_code)
        
        # Parse base classes (extends/implements)
        base_classes = self._extract_base_classes(class_node, source_code)
        
        # Check modifiers
        modifiers = self._extract_modifiers(class_node, source_code)
        is_abstract = "abstract" in modifiers
        
        # Extract annotations
        attributes = self._extract_annotations(class_node, source_code)
        
        # Get package from parent
        package = self._get_enclosing_package(class_node, source_code)
        
        return ClassInfo(
            name=class_name,
            line_start=line_start,
            line_end=line_end,
            methods=methods,
            base_classes=base_classes,
            namespace=package,
            is_interface=False,
            is_abstract=is_abstract,
            properties=properties,
            attributes=attributes,
        )
    
    def _parse_interface(self, interface_node: Node, source_code: bytes) -> Optional[ClassInfo]:
        """Parse interface declaration as ClassInfo with is_interface=True."""
        name_node = self._find_child_by_type(interface_node, "identifier")
        if not name_node:
            return None
        
        interface_name = source_code[name_node.start_byte:name_node.end_byte].decode("utf-8")
        
        line_start = interface_node.start_point[0] + 1
        line_end = interface_node.end_point[0] + 1
        
        methods = self._extract_class_methods(interface_node, source_code)
        properties = self._extract_class_fields(interface_node, source_code)
        package = self._get_enclosing_package(interface_node, source_code)
        base_classes = self._extract_base_classes(interface_node, source_code)
        
        return ClassInfo(
            name=interface_name,
            line_start=line_start,
            line_end=line_end,
            methods=methods,
            base_classes=base_classes,
            namespace=package,
            is_interface=True,
            is_abstract=False,
            properties=properties,
            attributes=[],
        )
    
    def _parse_enum(self, enum_node: Node, source_code: bytes) -> Optional[ClassInfo]:
        """Parse enum declaration as ClassInfo."""
        name_node = self._find_child_by_type(enum_node, "identifier")
        if not name_node:
            return None
        
        enum_name = source_code[name_node.start_byte:name_node.end_byte].decode("utf-8")
        
        line_start = enum_node.start_point[0] + 1
        line_end = enum_node.end_point[0] + 1
        
        package = self._get_enclosing_package(enum_node, source_code)
        
        return ClassInfo(
            name=enum_name,
            line_start=line_start,
            line_end=line_end,
            methods=[],
            base_classes=[],
            namespace=package,
            is_interface=False,
            is_abstract=False,
            properties=[],
            attributes=["enum"],
        )
    
    def _extract_class_methods(self, class_node: Node, source_code: bytes) -> List[FunctionInfo]:
        """Extract methods from a class."""
        methods = []
        
        for method_node in self._find_nodes_by_type(class_node, "method_declaration"):
            method_info = self._parse_method(method_node, source_code)
            if method_info:
                methods.append(method_info)
        
        # Also extract constructor_declaration
        for constructor_node in self._find_nodes_by_type(class_node, "constructor_declaration"):
            constructor_info = self._parse_constructor(constructor_node, source_code)
            if constructor_info:
                methods.append(constructor_info)
        
        return methods
    
    def _parse_method(self, method_node: Node, source_code: bytes) -> Optional[FunctionInfo]:
        """Parse a method declaration."""
        # Get method name
        name_node = self._find_child_by_type(method_node, "identifier")
        if not name_node:
            return None
        
        method_name = source_code[name_node.start_byte:name_node.end_byte].decode("utf-8")
        
        # Get line numbers
        line_start = method_node.start_point[0] + 1
        line_end = method_node.end_point[0] + 1
        
        # Parse parameters
        parameters = self._extract_parameters(method_node, source_code)
        
        # Check if synchronized
        modifiers = self._extract_modifiers(method_node, source_code)
        is_async = "synchronized" in modifiers  # Java doesn't have async, use synchronized
        
        # Get return type
        return_type = self._extract_return_type(method_node, source_code)
        
        # Get annotations
        decorators = self._extract_annotations(method_node, source_code)
        
        return FunctionInfo(
            name=method_name,
            line_start=line_start,
            line_end=line_end,
            parameters=[p["name"] for p in parameters],
            is_async=is_async,
            return_type=return_type,
            decorators=decorators,
        )
    
    def _parse_constructor(self, constructor_node: Node, source_code: bytes) -> Optional[FunctionInfo]:
        """Parse constructor as a special method."""
        # Get constructor name (same as class name)
        name_node = self._find_child_by_type(constructor_node, "identifier")
        if not name_node:
            return None
        
        constructor_name = source_code[name_node.start_byte:name_node.end_byte].decode("utf-8")
        
        line_start = constructor_node.start_point[0] + 1
        line_end = constructor_node.end_point[0] + 1
        
        parameters = self._extract_parameters(constructor_node, source_code)
        
        return FunctionInfo(
            name=constructor_name,
            line_start=line_start,
            line_end=line_end,
            parameters=[p["name"] for p in parameters],
            is_async=False,
            return_type=None,  # Constructors don't have return types
            decorators=[],
        )
    
    def _extract_class_fields(self, class_node: Node, source_code: bytes) -> List[dict]:
        """Extract field names from a class."""
        fields = []
        
        # Extract field_declaration
        for field_node in self._find_nodes_by_type(class_node, "field_declaration"):
            # Field declarations can have multiple declarators
            for declarator in self._find_nodes_by_type(field_node, "variable_declarator"):
                name_node = self._find_child_by_type(declarator, "identifier")
                if name_node:
                    field_name = source_code[name_node.start_byte:name_node.end_byte].decode("utf-8")
                    fields.append({"name": field_name, "type": "field"})
        
        return fields
    
    def _extract_functions(self, node: Node, source_code: bytes) -> List[FunctionInfo]:
        """Extract standalone functions (not common in Java)."""
        # Java doesn't have standalone functions outside classes
        return []
    
    def _extract_imports(self, node: Node, source_code: bytes) -> List[ImportInfo]:
        """Extract import statements."""
        imports = []
        
        for import_node in self._find_nodes_by_type(node, "import_declaration"):
            # Get the import path
            # Look for scoped_identifier or identifier
            name_node = None
            for child in import_node.children:
                if child.type in ["scoped_identifier", "identifier"]:
                    name_node = child
                    break
            
            if name_node:
                module_name = source_code[name_node.start_byte:name_node.end_byte].decode("utf-8")
                line = import_node.start_point[0] + 1
                
                imports.append(ImportInfo(
                    module=module_name,
                    names=[],
                    line=line,
                ))
        
        return imports
    
    def _extract_package(self, node: Node, source_code: bytes) -> Optional[str]:
        """Extract package declaration."""
        package_nodes = self._find_nodes_by_type(node, "package_declaration")
        if not package_nodes:
            return None
        
        # Get first package (should only be one)
        package_node = package_nodes[0]
        
        # Find scoped_identifier or identifier
        name_node = None
        for child in package_node.children:
            if child.type in ["scoped_identifier", "identifier"]:
                name_node = child
                break
        
        if name_node:
            return source_code[name_node.start_byte:name_node.end_byte].decode("utf-8")
        
        return None
    
    def _get_enclosing_package(self, node: Node, source_code: bytes) -> Optional[str]:
        """Get package enclosing a node by traversing to root."""
        # In Java, package is at file level, so traverse to root
        root = node
        while root.parent:
            root = root.parent
        
        return self._extract_package(root, source_code)
    
    def _extract_base_classes(self, class_node: Node, source_code: bytes) -> List[str]:
        """Extract base classes from class declaration (extends/implements)."""
        base_classes = []
        
        # Find superclass (extends)
        superclass_node = self._find_child_by_type(class_node, "superclass")
        if superclass_node:
            type_node = self._find_child_by_type(superclass_node, "type_identifier")
            if type_node:
                base_name = source_code[type_node.start_byte:type_node.end_byte].decode("utf-8")
                base_classes.append(base_name)
        
        # Find interfaces (implements/extends for interface)
        interfaces_node = self._find_child_by_type(class_node, "super_interfaces")
        if interfaces_node:
            for type_node in self._find_nodes_by_type(interfaces_node, "type_identifier"):
                interface_name = source_code[type_node.start_byte:type_node.end_byte].decode("utf-8")
                base_classes.append(interface_name)
        
        return base_classes
    
    def _extract_modifiers(self, node: Node, source_code: bytes) -> List[str]:
        """Extract access modifiers and keywords (public, private, static, etc)."""
        modifiers = []
        
        # Find modifiers node
        modifiers_node = self._find_child_by_type(node, "modifiers")
        if modifiers_node:
            for child in modifiers_node.children:
                if child.type in ["public", "private", "protected", "static", 
                                 "final", "abstract", "synchronized", "native",
                                 "strictfp", "transient", "volatile"]:
                    modifier = source_code[child.start_byte:child.end_byte].decode("utf-8")
                    modifiers.append(modifier)
        
        return modifiers
    
    def _extract_annotations(self, node: Node, source_code: bytes) -> List[str]:
        """Extract Java annotations like @Override, @Deprecated."""
        annotations = []
        
        # Look for marker_annotation, annotation nodes
        for anno_node in self._find_nodes_by_type(node, "marker_annotation"):
            name_node = self._find_child_by_type(anno_node, "identifier")
            if name_node:
                anno_name = source_code[name_node.start_byte:name_node.end_byte].decode("utf-8")
                annotations.append(f"@{anno_name}")
        
        for anno_node in self._find_nodes_by_type(node, "annotation"):
            name_node = self._find_child_by_type(anno_node, "identifier")
            if name_node:
                anno_name = source_code[name_node.start_byte:name_node.end_byte].decode("utf-8")
                annotations.append(f"@{anno_name}")
        
        return annotations
    
    def _extract_parameters(self, node: Node, source_code: bytes) -> List[Dict[str, Any]]:
        """Extract method parameters with types."""
        parameters = []
        
        # Find formal_parameters
        param_list = self._find_child_by_type(node, "formal_parameters")
        if not param_list:
            return parameters
        
        # Extract each formal_parameter
        for param_node in self._find_nodes_by_type(param_list, "formal_parameter"):
            # Get parameter name (identifier)
            name_node = self._find_child_by_type(param_node, "identifier")
            if not name_node:
                continue
            
            param_name = source_code[name_node.start_byte:name_node.end_byte].decode("utf-8")
            
            # Get parameter type
            type_node = None
            for child in param_node.children:
                if child.type in ["type_identifier", "integral_type", "floating_point_type",
                                 "boolean_type", "generic_type", "array_type"]:
                    type_node = child
                    break
            
            param_type = None
            if type_node:
                param_type = source_code[type_node.start_byte:type_node.end_byte].decode("utf-8")
            
            parameters.append({
                "name": param_name,
                "type": param_type,
            })
        
        return parameters
    
    def _extract_return_type(self, node: Node, source_code: bytes) -> Optional[str]:
        """Extract return type from method declaration."""
        # Find the type node (various types possible)
        for child in node.children:
            if child.type in ["type_identifier", "integral_type", "floating_point_type",
                             "boolean_type", "void_type", "generic_type", "array_type"]:
                return source_code[child.start_byte:child.end_byte].decode("utf-8")
        
        return None
    
    def _collect_parse_errors(self, node: Node) -> List[str]:
        """Collect any parse errors from tree-sitter."""
        errors = []
        
        if node.has_error:
            errors.append(f"Parse error at line {node.start_point[0] + 1}")
        
        for child in node.children:
            if child.type == "ERROR":
                errors.append(f"Syntax error at line {child.start_point[0] + 1}")
            errors.extend(self._collect_parse_errors(child))
        
        return errors
    
    # Helper methods for tree traversal
    
    def _find_nodes_by_type(self, node: Node, node_type: str) -> List[Node]:
        """Recursively find all nodes of a given type."""
        results = []
        
        if node.type == node_type:
            results.append(node)
        
        for child in node.children:
            results.extend(self._find_nodes_by_type(child, node_type))
        
        return results
    
    def _find_child_by_type(self, node: Node, child_type: str) -> Optional[Node]:
        """Find first direct child of a given type."""
        for child in node.children:
            if child.type == child_type:
                return child
        return None
