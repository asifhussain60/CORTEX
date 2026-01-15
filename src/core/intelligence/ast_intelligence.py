# © 2025-2026 Asif Hussain. All rights reserved.
# AC-ID: IR-001-01 - AST-Based Code Intelligence
"""
AST Intelligence Engine for CORTEX LENS.

PHASE-07: Holistic Intent Router Intelligence
AC-ID: IR-001-01 - AST-Based Code Intelligence

This module provides AST-based code analysis capabilities including:
- Python file parsing into AST representation
- Function/class definition extraction with signatures
- Import and dependency identification
- Graceful degradation on syntax errors

Part of CORTEX LENS context intelligence system.
"""

from __future__ import annotations

import ast
import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union


# =============================================================================
# DATA CLASSES
# =============================================================================


@dataclass
class Parameter:
    """Represents a function parameter.
    
    Attributes:
        name: Parameter name
        type_hint: Type annotation if present
        default: Default value if present
        is_args: True if *args
        is_kwargs: True if **kwargs
    """
    name: str
    type_hint: Optional[str] = None
    default: Optional[str] = None
    is_args: bool = False
    is_kwargs: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "type_hint": self.type_hint,
            "default": self.default,
            "is_args": self.is_args,
            "is_kwargs": self.is_kwargs,
        }


@dataclass
class FunctionInfo:
    """Information about a function definition.
    
    Attributes:
        name: Function name
        parameters: List of parameters
        return_type: Return type annotation
        docstring: Function docstring
        decorators: List of decorator names
        line_number: Line where function is defined
        is_async: True if async function
        is_method: True if method in a class
        class_name: Parent class name if method
    """
    name: str
    parameters: List[Parameter] = field(default_factory=list)
    return_type: Optional[str] = None
    docstring: Optional[str] = None
    decorators: List[str] = field(default_factory=list)
    line_number: int = 0
    is_async: bool = False
    is_method: bool = False
    class_name: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "parameters": [p.to_dict() for p in self.parameters],
            "return_type": self.return_type,
            "docstring": self.docstring,
            "decorators": self.decorators,
            "line_number": self.line_number,
            "is_async": self.is_async,
            "is_method": self.is_method,
            "class_name": self.class_name,
        }
    
    def __eq__(self, other: object) -> bool:
        """Compare two FunctionInfo objects by name and parameters."""
        if not isinstance(other, FunctionInfo):
            return False
        return (
            self.name == other.name
            and len(self.parameters) == len(other.parameters)
            and self.class_name == other.class_name
        )


@dataclass
class ClassInfo:
    """Information about a class definition.
    
    Attributes:
        name: Class name
        bases: List of base class names
        methods: List of method definitions
        docstring: Class docstring
        decorators: List of decorator names
        line_number: Line where class is defined
        class_variables: Class-level variable names
    """
    name: str
    bases: List[str] = field(default_factory=list)
    methods: List[FunctionInfo] = field(default_factory=list)
    docstring: Optional[str] = None
    decorators: List[str] = field(default_factory=list)
    line_number: int = 0
    class_variables: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "bases": self.bases,
            "methods": [m.to_dict() for m in self.methods],
            "docstring": self.docstring,
            "decorators": self.decorators,
            "line_number": self.line_number,
            "class_variables": self.class_variables,
        }


@dataclass
class ConstantInfo:
    """Information about a module-level constant.
    
    Attributes:
        name: Constant name
        value: String representation of value
        line_number: Line where constant is defined
    """
    name: str
    value: Optional[str] = None
    line_number: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "value": self.value,
            "line_number": self.line_number,
        }


@dataclass
class ParseResult:
    """Result of parsing a Python file or string.
    
    Attributes:
        success: True if parsing succeeded
        ast_tree: The AST tree if successful
        functions: List of function definitions
        classes: List of class definitions
        imports: Set of imported module names
        from_imports: Dict mapping module to imported names
        constants: List of module-level constants
        module_docstring: Module-level docstring
        error: Error message if parsing failed
        error_line: Line number of error
        error_column: Column number of error
        file_path: Path to parsed file (if from file)
    """
    success: bool = True
    ast_tree: Optional[ast.Module] = None
    functions: List[FunctionInfo] = field(default_factory=list)
    classes: List[ClassInfo] = field(default_factory=list)
    imports: Set[str] = field(default_factory=set)
    from_imports: Dict[str, List[str]] = field(default_factory=dict)
    constants: List[ConstantInfo] = field(default_factory=list)
    module_docstring: Optional[str] = None
    error: Optional[str] = None
    error_line: Optional[int] = None
    error_column: Optional[int] = None
    file_path: Optional[Path] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "success": self.success,
            "functions": [f.to_dict() for f in self.functions],
            "classes": [c.to_dict() for c in self.classes],
            "imports": list(self.imports),
            "from_imports": self.from_imports,
            "constants": [c.to_dict() for c in self.constants],
            "module_docstring": self.module_docstring,
            "error": self.error,
            "error_line": self.error_line,
            "error_column": self.error_column,
            "file_path": str(self.file_path) if self.file_path else None,
        }


# =============================================================================
# AST INTELLIGENCE ENGINE
# =============================================================================


class ASTIntelligenceEngine:
    """AST-based code intelligence engine for Python files.
    
    Parses Python source code and extracts structured information about
    functions, classes, imports, and other code elements.
    
    Attributes:
        enable_cache: Whether to cache parse results
        
    Example:
        >>> engine = ASTIntelligenceEngine()
        >>> result = engine.parse_file(Path("my_module.py"))
        >>> for func in result.functions:
        ...     print(f"{func.name}: {func.return_type}")
    """
    
    def __init__(self, enable_cache: bool = False) -> None:
        """Initialize the AST intelligence engine.
        
        Args:
            enable_cache: If True, cache parse results by file content hash
        """
        self.enable_cache = enable_cache
        self._cache: Dict[str, ParseResult] = {}
    
    def parse_file(self, file_path: Path) -> ParseResult:
        """Parse a Python file and extract code intelligence.
        
        Args:
            file_path: Path to the Python file to parse
            
        Returns:
            ParseResult containing extracted information or error details
        """
        if not file_path.exists():
            return ParseResult(
                success=False,
                error=f"File not found: {file_path}",
                file_path=file_path,
            )
        
        try:
            content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError as e:
            return ParseResult(
                success=False,
                error=f"Failed to read file (encoding error): {e}",
                file_path=file_path,
            )
        except Exception as e:
            return ParseResult(
                success=False,
                error=f"Failed to read file: {e}",
                file_path=file_path,
            )
        
        # Check cache if enabled
        if self.enable_cache:
            cache_key = self._compute_cache_key(content)
            if cache_key in self._cache:
                cached = self._cache[cache_key]
                # Update file path in cached result
                result = ParseResult(
                    success=cached.success,
                    ast_tree=cached.ast_tree,
                    functions=cached.functions,
                    classes=cached.classes,
                    imports=cached.imports,
                    from_imports=cached.from_imports,
                    constants=cached.constants,
                    module_docstring=cached.module_docstring,
                    error=cached.error,
                    error_line=cached.error_line,
                    error_column=cached.error_column,
                    file_path=file_path,
                )
                return result
        
        result = self.parse_string(content)
        result.file_path = file_path
        
        # Store in cache if enabled
        if self.enable_cache and result.success:
            cache_key = self._compute_cache_key(content)
            self._cache[cache_key] = result
        
        return result
    
    def parse_string(self, source: str) -> ParseResult:
        """Parse Python source code from a string.
        
        Args:
            source: Python source code string
            
        Returns:
            ParseResult containing extracted information or error details
        """
        # Handle empty source
        if not source.strip():
            return ParseResult(
                success=True,
                ast_tree=ast.Module(body=[], type_ignores=[]),
                functions=[],
                classes=[],
                imports=set(),
                from_imports={},
                constants=[],
                module_docstring=None,
            )
        
        try:
            tree = ast.parse(source)
        except SyntaxError as e:
            return ParseResult(
                success=False,
                error=f"Syntax error: {e.msg}",
                error_line=e.lineno,
                error_column=e.offset,
            )
        except Exception as e:
            return ParseResult(
                success=False,
                error=f"Parse error: {str(e)}",
            )
        
        # Extract information from AST
        extractor = _ASTExtractor()
        extractor.visit(tree)
        
        return ParseResult(
            success=True,
            ast_tree=tree,
            functions=extractor.functions,
            classes=extractor.classes,
            imports=extractor.imports,
            from_imports=extractor.from_imports,
            constants=extractor.constants,
            module_docstring=extractor.module_docstring,
        )
    
    def _compute_cache_key(self, content: str) -> str:
        """Compute cache key from file content."""
        return hashlib.sha256(content.encode()).hexdigest()


# =============================================================================
# AST VISITOR FOR EXTRACTION
# =============================================================================


class _ASTExtractor(ast.NodeVisitor):
    """AST visitor that extracts code intelligence.
    
    Walks the AST and collects information about functions, classes,
    imports, and other code elements.
    """
    
    def __init__(self) -> None:
        """Initialize the extractor."""
        self.functions: List[FunctionInfo] = []
        self.classes: List[ClassInfo] = []
        self.imports: Set[str] = set()
        self.from_imports: Dict[str, List[str]] = {}
        self.constants: List[ConstantInfo] = []
        self.module_docstring: Optional[str] = None
        self._current_class: Optional[str] = None
        self._processed_module_docstring = False
    
    def visit_Module(self, node: ast.Module) -> None:
        """Visit module node to extract docstring."""
        if node.body and isinstance(node.body[0], ast.Expr):
            if isinstance(node.body[0].value, ast.Constant):
                value = node.body[0].value.value
                if isinstance(value, str):
                    self.module_docstring = value
                    self._processed_module_docstring = True
        self.generic_visit(node)
    
    def visit_Import(self, node: ast.Import) -> None:
        """Visit import statement."""
        for alias in node.names:
            self.imports.add(alias.name.split(".")[0])
    
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Visit from...import statement."""
        if node.module:
            module_name = node.module.split(".")[0]
            self.imports.add(module_name)
            
            if node.module not in self.from_imports:
                self.from_imports[node.module] = []
            
            for alias in node.names:
                if alias.name != "*":
                    self.from_imports[node.module].append(alias.name)
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definition."""
        self._extract_function(node, is_async=False)
        self.generic_visit(node)
    
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Visit async function definition."""
        self._extract_function(node, is_async=True)
        self.generic_visit(node)
    
    def _extract_function(
        self,
        node: Union[ast.FunctionDef, ast.AsyncFunctionDef],
        is_async: bool,
    ) -> FunctionInfo:
        """Extract function information from AST node."""
        # Extract parameters
        parameters = self._extract_parameters(node.args)
        
        # Extract return type
        return_type = None
        if node.returns:
            return_type = self._annotation_to_string(node.returns)
        
        # Extract docstring
        docstring = ast.get_docstring(node)
        
        # Extract decorators
        decorators = []
        for decorator in node.decorator_list:
            decorators.append(self._decorator_to_string(decorator))
        
        func_info = FunctionInfo(
            name=node.name,
            parameters=parameters,
            return_type=return_type,
            docstring=docstring,
            decorators=decorators,
            line_number=node.lineno,
            is_async=is_async,
            is_method=self._current_class is not None,
            class_name=self._current_class,
        )
        
        # Add to appropriate list
        if self._current_class is not None:
            # Method will be added by ClassDef handler
            return func_info
        else:
            self.functions.append(func_info)
            return func_info
    
    def _extract_parameters(self, args: ast.arguments) -> List[Parameter]:
        """Extract parameter information from function arguments."""
        parameters = []
        
        # Calculate defaults offset
        num_args = len(args.args)
        num_defaults = len(args.defaults)
        defaults_offset = num_args - num_defaults
        
        # Regular arguments
        for i, arg in enumerate(args.args):
            type_hint = None
            if arg.annotation:
                type_hint = self._annotation_to_string(arg.annotation)
            
            default = None
            default_index = i - defaults_offset
            if default_index >= 0 and default_index < len(args.defaults):
                default = self._value_to_string(args.defaults[default_index])
            
            parameters.append(Parameter(
                name=arg.arg,
                type_hint=type_hint,
                default=default,
            ))
        
        # *args
        if args.vararg:
            type_hint = None
            if args.vararg.annotation:
                type_hint = self._annotation_to_string(args.vararg.annotation)
            parameters.append(Parameter(
                name=args.vararg.arg,
                type_hint=type_hint,
                is_args=True,
            ))
        
        # Keyword-only arguments
        num_kwonly = len(args.kwonlyargs)
        num_kw_defaults = len(args.kw_defaults)
        
        for i, arg in enumerate(args.kwonlyargs):
            type_hint = None
            if arg.annotation:
                type_hint = self._annotation_to_string(arg.annotation)
            
            default = None
            if i < num_kw_defaults and args.kw_defaults[i] is not None:
                default = self._value_to_string(args.kw_defaults[i])
            
            parameters.append(Parameter(
                name=arg.arg,
                type_hint=type_hint,
                default=default,
            ))
        
        # **kwargs
        if args.kwarg:
            type_hint = None
            if args.kwarg.annotation:
                type_hint = self._annotation_to_string(args.kwarg.annotation)
            parameters.append(Parameter(
                name=args.kwarg.arg,
                type_hint=type_hint,
                is_kwargs=True,
            ))
        
        return parameters
    
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definition."""
        # Extract base classes
        bases = []
        for base in node.bases:
            bases.append(self._annotation_to_string(base))
        
        # Extract docstring
        docstring = ast.get_docstring(node)
        
        # Extract decorators
        decorators = []
        for decorator in node.decorator_list:
            decorators.append(self._decorator_to_string(decorator))
        
        # Extract class variables
        class_variables = []
        for item in node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        class_variables.append(target.id)
            elif isinstance(item, ast.AnnAssign):
                if isinstance(item.target, ast.Name):
                    class_variables.append(item.target.id)
        
        # Extract methods
        old_class = self._current_class
        self._current_class = node.name
        
        methods = []
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method_info = self._extract_function(
                    item,
                    is_async=isinstance(item, ast.AsyncFunctionDef),
                )
                methods.append(method_info)
        
        self._current_class = old_class
        
        class_info = ClassInfo(
            name=node.name,
            bases=bases,
            methods=methods,
            docstring=docstring,
            decorators=decorators,
            line_number=node.lineno,
            class_variables=class_variables,
        )
        
        self.classes.append(class_info)
    
    def visit_Assign(self, node: ast.Assign) -> None:
        """Visit assignment to detect module-level constants."""
        # Only process module-level assignments (not inside functions/classes)
        if self._current_class is None:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    # Check if it looks like a constant (UPPER_CASE)
                    if target.id.isupper() or target.id[0].isupper():
                        value = self._value_to_string(node.value)
                        self.constants.append(ConstantInfo(
                            name=target.id,
                            value=value,
                            line_number=node.lineno,
                        ))
    
    def _annotation_to_string(self, node: ast.expr) -> str:
        """Convert annotation AST node to string."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Constant):
            return repr(node.value)
        elif isinstance(node, ast.Attribute):
            value = self._annotation_to_string(node.value)
            return f"{value}.{node.attr}"
        elif isinstance(node, ast.Subscript):
            value = self._annotation_to_string(node.value)
            slice_val = self._annotation_to_string(node.slice)
            return f"{value}[{slice_val}]"
        elif isinstance(node, ast.Tuple):
            elements = ", ".join(
                self._annotation_to_string(e) for e in node.elts
            )
            return elements
        elif isinstance(node, ast.List):
            elements = ", ".join(
                self._annotation_to_string(e) for e in node.elts
            )
            return f"[{elements}]"
        elif isinstance(node, ast.BinOp):
            # Handle Union type syntax (X | Y)
            left = self._annotation_to_string(node.left)
            right = self._annotation_to_string(node.right)
            return f"{left} | {right}"
        else:
            return ast.unparse(node)
    
    def _value_to_string(self, node: ast.expr) -> str:
        """Convert value AST node to string."""
        if isinstance(node, ast.Constant):
            return repr(node.value)
        elif isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.List):
            elements = ", ".join(
                self._value_to_string(e) for e in node.elts
            )
            return f"[{elements}]"
        elif isinstance(node, ast.Dict):
            pairs = []
            for k, v in zip(node.keys, node.values):
                if k is not None:
                    key_str = self._value_to_string(k)
                    val_str = self._value_to_string(v)
                    pairs.append(f"{key_str}: {val_str}")
            return "{" + ", ".join(pairs) + "}"
        else:
            try:
                return ast.unparse(node)
            except Exception:
                return "<complex>"
    
    def _decorator_to_string(self, node: ast.expr) -> str:
        """Convert decorator AST node to string."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Call):
            func = self._decorator_to_string(node.func)
            args = ", ".join(self._value_to_string(a) for a in node.args)
            return f"{func}({args})"
        elif isinstance(node, ast.Attribute):
            value = self._decorator_to_string(node.value)
            return f"{value}.{node.attr}"
        else:
            try:
                return ast.unparse(node)
            except Exception:
                return "<decorator>"


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    "ASTIntelligenceEngine",
    "ParseResult",
    "FunctionInfo",
    "ClassInfo",
    "ConstantInfo",
    "Parameter",
]
