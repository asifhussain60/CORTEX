"""
CSharpAdapter - Tree-sitter-based C# AST parser.

Parses C# source files using tree-sitter-c-sharp grammar and extracts:
- Classes (public, internal, abstract, sealed, partial)
- Methods (public, private, protected, async, static)
- Properties and fields
- Using statements (imports)
- Namespaces
- Attributes/decorators
- Interfaces

Author: Asif Hussain
Created: 2026-02-04
Authority: LENS-MULTI-LANGUAGE-ENHANCEMENT.yaml Phase 1
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

import tree_sitter_c_sharp as ts_csharp
from tree_sitter import Language, Node, Parser

from cortex.lens.adapters.language_adapter import LanguageAdapter
from cortex.lens.models.polyglot_ast_result import (
    ClassInfo,
    FunctionInfo,
    ImportInfo,
    LanguageType,
    PolyglotASTResult,
)


class CSharpAdapter(LanguageAdapter):
    """
    C# language adapter using tree-sitter.

    Parses C# source code and extracts:
    - Classes, interfaces, structs, enums
    - Methods (instance, static, async, abstract)
    - Properties and fields
    - Using directives
    - Namespaces
    - Attributes (decorators)
    - Access modifiers

    Example:
        >>> adapter = CSharpAdapter()
        >>> result = adapter.parse_file(Path("UserService.cs"))
        >>> print(f"Found {len(result.classes)} classes")
        >>> print(f"Language: {result.language}")
    """

    def __init__(self):
        """Initialize CSharpAdapter with tree-sitter parser.
        
        Handles both tree-sitter 0.20 (PyCapsule) and 0.21+ (Language) APIs.
        """
        try:
            # Get language from tree-sitter-c-sharp
            lang_obj = ts_csharp.language()
            
            # Check if it's already a Language object (0.21+ API)
            if isinstance(lang_obj, Language):
                self.language = lang_obj
            else:
                # It's a PyCapsule (0.20 API) - wrap it
                # tree-sitter 0.20 expects Language to be constructed differently
                # Workaround: Use language_library approach
                from tree_sitter import Language as TSLanguage
                try:
                    # Try loading from shared library if available
                    self.language = TSLanguage(ts_csharp.language_library(), 'c_sharp')
                except (AttributeError, TypeError):
                    # Fallback: Create mock Language for compatibility
                    # This will allow initialization but log warning
                    print("⚠️ CSharpAdapter: tree-sitter version mismatch detected")
                    print("   tree-sitter: 0.20.x | tree-sitter-c-sharp: 0.23.x")
                    print("   Recommend: pip install --upgrade tree-sitter>=0.21.0")
                    print("   Fallback: Using pattern-based analysis for C#")
                    self.language = None
            
            self.parser = Parser()
            if self.language:
                self.parser.set_language(self.language)
            
        except Exception as e:
            print(f"⚠️ CSharpAdapter initialization failed: {e}")
            print("   Falling back to pattern-based analysis")
            self.language = None
            self.parser = None

    def parse_file(self, file_path: Path) -> PolyglotASTResult:
        """
        Parse C# file and return unified AST result.

        Args:
            file_path: Path to C# source file

        Returns:
            PolyglotASTResult with classes, methods, imports

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Read file content
        source_code = file_path.read_bytes()

        # If parser not available (version mismatch), use pattern-based fallback
        if not self.parser or not self.language:
            return self._pattern_based_parse(file_path, source_code)

        # Parse with tree-sitter
        try:
            tree = self.parser.parse(source_code)
            root_node = tree.root_node

            # Extract AST elements
            classes = self._extract_classes(root_node, source_code)
            functions = self._extract_functions(root_node, source_code)
            imports = self._extract_imports(root_node, source_code)
            namespace = self._extract_namespace(root_node, source_code)

            # Check for parse errors
            parse_errors = self._collect_parse_errors(root_node)

            return PolyglotASTResult(
                file_path=file_path,
                language=LanguageType.CSHARP,
                classes=classes,
                functions=functions,
                imports=imports,
                raw_ast=root_node,
                parse_errors=parse_errors,
                metadata={"namespace": namespace} if namespace else {},
            )
        except Exception as e:
            # Fallback to pattern-based parsing
            print(f"⚠️ AST parsing failed for {file_path.name}: {e}")
            print("   Using pattern-based fallback")
            return self._pattern_based_parse(file_path, source_code)

    def get_supported_extensions(self) -> List[str]:
        """
        Get C# file extensions.

        Returns:
            List of extensions: [".cs", ".csx"]
        """
        return [".cs", ".csx"]

    def get_language_name(self) -> str:
        """
        Get human-readable language name.

        Returns:
            "C#"
        """
        return "C#"

    def _extract_classes(self, node: Node, source_code: bytes) -> List[ClassInfo]:
        """Extract all class declarations from AST."""
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

        # Parse properties/fields
        properties = self._extract_class_properties(class_node, source_code)

        # Parse base classes
        base_classes = self._extract_base_classes(class_node, source_code)

        # Check modifiers
        modifiers = self._extract_modifiers(class_node, source_code)
        is_abstract = "abstract" in modifiers
        is_sealed = "sealed" in modifiers

        # Extract attributes
        attributes = self._extract_attributes(class_node, source_code)

        # Get namespace from parent
        namespace = self._get_enclosing_namespace(class_node, source_code)

        return ClassInfo(
            name=class_name,
            line_start=line_start,
            line_end=line_end,
            methods=methods,  # Keep as FunctionInfo objects, not just names
            base_classes=base_classes,
            namespace=namespace,
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
        properties = self._extract_class_properties(interface_node, source_code)
        namespace = self._get_enclosing_namespace(interface_node, source_code)

        return ClassInfo(
            name=interface_name,
            line_start=line_start,
            line_end=line_end,
            methods=methods,  # Store FunctionInfo objects, not just names
            base_classes=[],
            namespace=namespace,
            is_interface=True,
            is_abstract=False,
            properties=properties,
            attributes=[],
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
        # Get method name - in tree-sitter C#, we need to skip the return type identifier
        # and get the method name identifier. The structure is:
        # method_declaration: [modifiers] return_type identifier(name) parameter_list body
        identifiers = [c for c in method_node.children if c.type == "identifier"]

        if not identifiers:
            return None

        # If there are multiple identifiers, the last one before parameter_list is the method name
        # Find parameter_list position
        param_list_idx = -1
        for i, child in enumerate(method_node.children):
            if child.type == "parameter_list":
                param_list_idx = i
                break

        # Get the identifier just before parameter_list
        method_name = None
        if param_list_idx > 0:
            for i in range(param_list_idx - 1, -1, -1):
                if method_node.children[i].type == "identifier":
                    method_name = source_code[
                        method_node.children[i].start_byte:method_node.children[i].end_byte
                    ].decode("utf-8")
                    break

        if not method_name and identifiers:
            # Fallback: use last identifier
            method_name = source_code[identifiers[-1].start_byte:identifiers[-1].end_byte].decode("utf-8")

        if not method_name:
            return None

        # Get line numbers
        line_start = method_node.start_point[0] + 1
        line_end = method_node.end_point[0] + 1

        # Parse parameters
        parameters = self._extract_parameters(method_node, source_code)

        # Check if async
        modifiers = self._extract_modifiers(method_node, source_code)
        is_async = "async" in modifiers

        # Get return type
        return_type = self._extract_return_type(method_node, source_code)

        # Get attributes
        decorators = self._extract_attributes(method_node, source_code)

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

    def _extract_class_properties(self, class_node: Node, source_code: bytes) -> List[dict]:
        """Extract property and field names from a class."""
        properties = []

        # Extract property_declaration
        for prop_node in self._find_nodes_by_type(class_node, "property_declaration"):
            name_node = self._find_child_by_type(prop_node, "identifier")
            if name_node:
                prop_name = source_code[name_node.start_byte:name_node.end_byte].decode("utf-8")
                properties.append({"name": prop_name, "type": "property"})

        # Extract field_declaration
        for field_node in self._find_nodes_by_type(class_node, "field_declaration"):
            # Field declarations can have multiple declarators
            for declarator in self._find_nodes_by_type(field_node, "variable_declarator"):
                name_node = self._find_child_by_type(declarator, "identifier")
                if name_node:
                    field_name = source_code[name_node.start_byte:name_node.end_byte].decode("utf-8")
                    properties.append({"name": field_name, "type": "field"})

        return properties

    def _extract_functions(self, node: Node, source_code: bytes) -> List[FunctionInfo]:
        """Extract standalone functions (not common in C#, but possible)."""
        # C# typically doesn't have standalone functions outside classes
        # But we can handle local functions if needed
        return []

    def _extract_imports(self, node: Node, source_code: bytes) -> List[ImportInfo]:
        """Extract using directives."""
        imports = []

        for using_node in self._find_nodes_by_type(node, "using_directive"):
            # Get the namespace being imported
            name_node = self._find_child_by_type(using_node, "qualified_name")
            if not name_node:
                name_node = self._find_child_by_type(using_node, "identifier")

            if name_node:
                module_name = source_code[name_node.start_byte:name_node.end_byte].decode("utf-8")
                line = using_node.start_point[0] + 1

                imports.append(ImportInfo(
                    module=module_name,
                    names=[],
                    line=line,
                ))

        return imports

    def _extract_namespace(self, node: Node, source_code: bytes) -> Optional[str]:
        """Extract namespace declaration."""
        namespace_nodes = self._find_nodes_by_type(node, "namespace_declaration")
        if not namespace_nodes:
            return None

        # Get first namespace (most common case)
        namespace_node = namespace_nodes[0]
        name_node = self._find_child_by_type(namespace_node, "qualified_name")
        if not name_node:
            name_node = self._find_child_by_type(namespace_node, "identifier")

        if name_node:
            return source_code[name_node.start_byte:name_node.end_byte].decode("utf-8")

        return None

    def _get_enclosing_namespace(self, node: Node, source_code: bytes) -> Optional[str]:
        """Get namespace enclosing a node."""
        current = node.parent
        while current:
            if current.type == "namespace_declaration":
                name_node = self._find_child_by_type(current, "qualified_name")
                if not name_node:
                    name_node = self._find_child_by_type(current, "identifier")
                if name_node:
                    return source_code[name_node.start_byte:name_node.end_byte].decode("utf-8")
            current = current.parent
        return None

    def _extract_base_classes(self, class_node: Node, source_code: bytes) -> List[str]:
        """Extract base classes from class declaration."""
        base_classes = []

        # Find base_list node
        base_list = self._find_child_by_type(class_node, "base_list")
        if not base_list:
            return base_classes

        # Extract all type identifiers from base list
        for type_node in base_list.children:
            if type_node.type in ["simple_name", "qualified_name", "identifier"]:
                base_name = source_code[type_node.start_byte:type_node.end_byte].decode("utf-8")
                base_classes.append(base_name)

        return base_classes

    def _extract_modifiers(self, node: Node, source_code: bytes) -> List[str]:
        """Extract access modifiers and other keywords (public, private, async, static, etc)."""
        modifiers = []

        # Find modifier keywords in children
        for child in node.children:
            if child.type in ["public", "private", "protected", "internal",
                             "static", "async", "abstract", "sealed", "virtual",
                             "override", "readonly"]:
                modifier = source_code[child.start_byte:child.end_byte].decode("utf-8")
                modifiers.append(modifier)

        return modifiers

    def _extract_attributes(self, node: Node, source_code: bytes) -> List[str]:
        """Extract C# attributes (decorators) like [Serializable], [HttpGet]."""
        attributes = []

        # Look for attribute_list nodes
        for attr_list in self._find_nodes_by_type(node, "attribute_list"):
            for attr_node in attr_list.children:
                if attr_node.type == "attribute":
                    # Get attribute name
                    name_node = self._find_child_by_type(attr_node, "identifier")
                    if not name_node:
                        name_node = self._find_child_by_type(attr_node, "qualified_name")
                    if name_node:
                        attr_name = source_code[name_node.start_byte:name_node.end_byte].decode("utf-8")
                        attributes.append(attr_name)

        return attributes

    def _extract_parameters(self, node: Node, source_code: bytes) -> List[Dict[str, Any]]:
        """Extract method parameters with types."""
        parameters = []

        # Find parameter_list
        param_list = self._find_child_by_type(node, "parameter_list")
        if not param_list:
            return parameters

        # Extract each parameter
        for param_node in self._find_nodes_by_type(param_list, "parameter"):
            # Get parameter name
            name_node = self._find_child_by_type(param_node, "identifier")
            if not name_node:
                continue

            param_name = source_code[name_node.start_byte:name_node.end_byte].decode("utf-8")

            # Get parameter type
            type_node = self._find_child_by_type(param_node, "type")
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
        # Find the return type node (usually the first type child)
        for child in node.children:
            if child.type in ["predefined_type", "identifier", "qualified_name", "generic_name"]:
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

    def _pattern_based_parse(self, file_path: Path, source_code: bytes) -> PolyglotASTResult:
        """
        Fallback pattern-based C# parser for tree-sitter version mismatch.
        
        Uses regex patterns to extract basic structure when AST parsing unavailable.
        
        Args:
            file_path: Path to C# file
            source_code: File content as bytes
            
        Returns:
            PolyglotASTResult with pattern-extracted elements
        """
        import re
        
        text = source_code.decode('utf-8', errors='ignore')
        
        # Extract classes using regex
        classes = []
        class_pattern = r'(?:public|internal|private|protected)?\s+(?:abstract|sealed|partial)?\s*class\s+(\w+)'
        for match in re.finditer(class_pattern, text):
            class_name = match.group(1)
            line_num = text[:match.start()].count('\n') + 1
            
            classes.append(ClassInfo(
                name=class_name,
                line_start=line_num,
                line_end=line_num,  # Approximate
                methods=[],
                base_classes=[],
                docstring="",
                is_abstract='abstract' in match.group(0),
                attributes=[],
            ))
        
        # Extract methods using regex
        functions = []
        # Match method declarations with return types (including Task<T>, List<T>, etc.)
        method_pattern = r'(?:public|private|protected|internal)?\s+(?:static|async|virtual|override)?\s*(?:\w+(?:<[^>]+>)?)\s+(\w+)\s*\('
        
        # Also get all class names to filter out constructors
        class_names = {c.name for c in classes}
        
        for match in re.finditer(method_pattern, text):
            method_name = match.group(1)
            # Skip property getters/setters and constructors (same name as class)
            if method_name in ['get', 'set'] or method_name in class_names:
                continue
            
            line_num = text[:match.start()].count('\n') + 1
            
            functions.append(FunctionInfo(
                name=method_name,
                line_start=line_num,
                line_end=line_num,  # Approximate
                parameters=[],
                return_type='unknown',
                decorators=[],
                is_async='async' in match.group(0),
            ))
        
        # Extract using statements
        imports = []
        using_pattern = r'using\s+([\w.]+)\s*;'
        for match in re.finditer(using_pattern, text):
            import_name = match.group(1)
            line_num = text[:match.start()].count('\n') + 1
            
            imports.append(ImportInfo(
                module=import_name,
                names=[],  # C# using statements don't have specific names
                line=line_num,
                alias=None,
            ))
        
        # Extract namespace
        namespace_match = re.search(r'namespace\s+([\w.]+)', text)
        namespace = namespace_match.group(1) if namespace_match else None
        
        return PolyglotASTResult(
            file_path=file_path,
            language=LanguageType.CSHARP,
            classes=classes,
            functions=functions,
            imports=imports,
            raw_ast=None,  # No AST available
            parse_errors=[],
            metadata={
                "namespace": namespace,
                "fallback_mode": True,
                "reason": "tree-sitter version mismatch (0.20 vs 0.21+)"
            },
        )
