"""AST Intelligence Engine - Complete code analysis system.

Provides comprehensive Abstract Syntax Tree analysis for Python code including:
- File and string parsing with error handling
- Function/class/import extraction
- Docstring and type hint analysis
- Integration with call graph, pattern detection, and dependency mapping

Author: CORTEX Framework
AC-ID: E3-AST-INTELLIGENCE-ENGINE
"""

import ast
import hashlib
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


@dataclass
class ParameterInfo:
    """Function parameter information.
    
    Attributes:
        name: Parameter name
        type_hint: Type annotation if present
        default: Default value if present
    """
    name: str
    type_hint: Optional[str] = None
    default: Optional[str] = None


@dataclass
class FunctionInfo:
    """Function definition information.
    
    Attributes:
        name: Function name
        parameters: List of parameters
        return_type: Return type annotation
        docstring: Function docstring
        line_number: Line where function is defined
        decorators: List of decorator names
    """
    name: str
    parameters: List[ParameterInfo] = field(default_factory=list)
    return_type: Optional[str] = None
    docstring: Optional[str] = None
    line_number: int = 0
    decorators: List[str] = field(default_factory=list)


@dataclass
class ClassInfo:
    """Class definition information.
    
    Attributes:
        name: Class name
        bases: List of base class names
        methods: List of methods
        docstring: Class docstring
        line_number: Line where class is defined
        decorators: List of decorator names
    """
    name: str
    bases: List[str] = field(default_factory=list)
    methods: List[FunctionInfo] = field(default_factory=list)
    docstring: Optional[str] = None
    line_number: int = 0
    decorators: List[str] = field(default_factory=list)


@dataclass
class ConstantInfo:
    """Module-level constant information.
    
    Attributes:
        name: Constant name
        value: String representation of value
        line_number: Line where defined
    """
    name: str
    value: str
    line_number: int = 0


@dataclass
class ParseResult:
    """Result of AST parsing operation.
    
    Attributes:
        success: Whether parsing succeeded
        ast_tree: Parsed AST module (if successful)
        module_docstring: Module-level docstring
        imports: Set of imported module names
        from_imports: Dict mapping module to list of imported names
        functions: List of function definitions
        classes: List of class definitions
        constants: List of module-level constants
        error: Error message (if failed)
        error_line: Line number where error occurred
        error_column: Column number where error occurred
        source_path: Path to source file (if parsed from file)
    """
    success: bool
    ast_tree: Optional[ast.Module] = None
    module_docstring: Optional[str] = None
    imports: Set[str] = field(default_factory=set)
    from_imports: Dict[str, List[str]] = field(default_factory=dict)
    functions: List[FunctionInfo] = field(default_factory=list)
    classes: List[ClassInfo] = field(default_factory=list)
    constants: List[ConstantInfo] = field(default_factory=list)
    error: Optional[str] = None
    error_line: Optional[int] = None
    error_column: Optional[int] = None
    source_path: Optional[Path] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize parse result to dictionary.
        
        Returns:
            Dictionary representation of parse result
        """
        return {
            "success": self.success,
            "module_docstring": self.module_docstring,
            "imports": list(self.imports),
            "from_imports": self.from_imports,
            "functions": [
                {
                    "name": f.name,
                    "parameters": [
                        {"name": p.name, "type_hint": p.type_hint, "default": p.default}
                        for p in f.parameters
                    ],
                    "return_type": f.return_type,
                    "docstring": f.docstring,
                    "line_number": f.line_number,
                    "decorators": f.decorators,
                }
                for f in self.functions
            ],
            "classes": [
                {
                    "name": c.name,
                    "bases": c.bases,
                    "methods": [
                        {
                            "name": m.name,
                            "parameters": [
                                {"name": p.name, "type_hint": p.type_hint, "default": p.default}
                                for p in m.parameters
                            ],
                            "return_type": m.return_type,
                            "docstring": m.docstring,
                            "line_number": m.line_number,
                            "decorators": m.decorators,
                        }
                        for m in c.methods
                    ],
                    "docstring": c.docstring,
                    "line_number": c.line_number,
                    "decorators": c.decorators,
                }
                for c in self.classes
            ],
            "constants": [
                {"name": c.name, "value": c.value, "line_number": c.line_number}
                for c in self.constants
            ],
            "error": self.error,
            "error_line": self.error_line,
            "error_column": self.error_column,
        }


class ASTIntelligenceEngine:
    """Production-ready AST analysis engine for Python code.
    
    Provides comprehensive code intelligence through AST parsing:
    - Robust error handling for syntax errors and file I/O
    - Complete extraction of functions, classes, imports
    - Type hint and docstring preservation
    - Optional caching for performance
    - Structured results for downstream analysis
    
    Example:
        >>> engine = ASTIntelligenceEngine()
        >>> result = engine.parse_file(Path("module.py"))
        >>> if result.success:
        ...     for func in result.functions:
        ...         print(f"{func.name}: {func.docstring}")
    """
    
    def __init__(self, enable_cache: bool = False) -> None:
        """Initialize AST intelligence engine.
        
        Args:
            enable_cache: Enable result caching for repeated analyses
        """
        self.enable_cache = enable_cache
        self._cache: Dict[str, ParseResult] = {}
        logger.info(
            "ASTIntelligenceEngine initialized",
            extra={"cache_enabled": enable_cache}
        )
    
    def parse_file(self, file_path: Path) -> ParseResult:
        """Parse Python file and extract AST information.
        
        Args:
            file_path: Path to Python source file
            
        Returns:
            ParseResult with extracted information or error details
        """
        # Check cache
        if self.enable_cache:
            cache_key = f"file:{file_path}"
            if cache_key in self._cache:
                logger.debug(f"Cache hit for {file_path}")
                return self._cache[cache_key]
        
        # Validate file existence
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return ParseResult(
                success=False,
                error=f"File not found: {file_path}",
                source_path=file_path,
            )
        
        # Read file content
        try:
            source_code = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError as e:
            logger.error(f"Binary or non-UTF8 file: {file_path}", exc_info=True)
            return ParseResult(
                success=False,
                error=f"Cannot decode file (binary or non-UTF8): {e}",
                source_path=file_path,
            )
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}", exc_info=True)
            return ParseResult(
                success=False,
                error=f"Error reading file: {e}",
                source_path=file_path,
            )
        
        # Parse the source code
        result = self.parse_string(source_code)
        result.source_path = file_path
        
        # Cache result
        if self.enable_cache:
            cache_key = f"file:{file_path}"
            self._cache[cache_key] = result
        
        return result
    
    def parse_string(self, source_code: str) -> ParseResult:
        """Parse Python source code string and extract AST information.
        
        Args:
            source_code: Python source code as string
            
        Returns:
            ParseResult with extracted information or error details
        """
        # Parse AST
        try:
            tree = ast.parse(source_code)
        except SyntaxError as e:
            logger.warning(f"Syntax error in source code: {e}", exc_info=True)
            return ParseResult(
                success=False,
                error=f"Syntax error: {e.msg}",
                error_line=e.lineno,
                error_column=e.offset,
            )
        except Exception as e:
            logger.error(f"Unexpected error parsing source: {e}", exc_info=True)
            return ParseResult(
                success=False,
                error=f"Parse error: {e}",
            )
        
        # Extract information
        result = ParseResult(
            success=True,
            ast_tree=tree,
            module_docstring=ast.get_docstring(tree),
        )
        
        # Extract top-level elements
        for node in tree.body:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    result.imports.add(alias.name)
            
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    result.imports.add(node.module)
                    imported_names = [alias.name for alias in node.names]
                    result.from_imports[node.module] = imported_names
            
            elif isinstance(node, ast.FunctionDef):
                func_info = self._extract_function_info(node)
                result.functions.append(func_info)
            
            elif isinstance(node, ast.ClassDef):
                class_info = self._extract_class_info(node)
                result.classes.append(class_info)
            
            elif isinstance(node, ast.Assign):
                # Extract module-level constants (uppercase names)
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id.isupper():
                        constant = ConstantInfo(
                            name=target.id,
                            value=ast.unparse(node.value) if hasattr(ast, 'unparse') else str(node.value),
                            line_number=node.lineno,
                        )
                        result.constants.append(constant)
        
        logger.info(
            "Successfully parsed source",
            extra={
                "functions": len(result.functions),
                "classes": len(result.classes),
                "imports": len(result.imports),
            }
        )
        
        return result
    
    def _extract_function_info(self, node: ast.FunctionDef) -> FunctionInfo:
        """Extract function information from AST node.
        
        Args:
            node: FunctionDef AST node
            
        Returns:
            FunctionInfo with extracted details
        """
        # Extract parameters
        parameters = []
        for arg in node.args.args:
            param = ParameterInfo(
                name=arg.arg,
                type_hint=ast.unparse(arg.annotation) if arg.annotation else None,
            )
            parameters.append(param)
        
        # Add defaults to parameters
        defaults = node.args.defaults
        if defaults:
            # Defaults align to the last N parameters
            num_defaults = len(defaults)
            for i, default in enumerate(defaults):
                param_index = len(parameters) - num_defaults + i
                if param_index >= 0:
                    parameters[param_index].default = ast.unparse(default) if hasattr(ast, 'unparse') else str(default)
        
        # Extract decorators
        decorators = []
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                decorators.append(decorator.id)
            elif isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Name):
                    decorators.append(f"{decorator.func.id}(...)")
                else:
                    decorators.append(ast.unparse(decorator) if hasattr(ast, 'unparse') else "decorator")
            else:
                decorators.append(ast.unparse(decorator) if hasattr(ast, 'unparse') else "decorator")
        
        return FunctionInfo(
            name=node.name,
            parameters=parameters,
            return_type=ast.unparse(node.returns) if node.returns else None,
            docstring=ast.get_docstring(node),
            line_number=node.lineno,
            decorators=decorators,
        )
    
    def _extract_class_info(self, node: ast.ClassDef) -> ClassInfo:
        """Extract class information from AST node.
        
        Args:
            node: ClassDef AST node
            
        Returns:
            ClassInfo with extracted details
        """
        # Extract base classes
        bases = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
            else:
                bases.append(ast.unparse(base) if hasattr(ast, 'unparse') else "Base")
        
        # Extract methods
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_info = self._extract_function_info(item)
                methods.append(method_info)
        
        # Extract decorators
        decorators = []
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                decorators.append(decorator.id)
            elif isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Name):
                    decorators.append(f"{decorator.func.id}(...)")
                else:
                    decorators.append(ast.unparse(decorator) if hasattr(ast, 'unparse') else "decorator")
            else:
                decorators.append(ast.unparse(decorator) if hasattr(ast, 'unparse') else "decorator")
        
        return ClassInfo(
            name=node.name,
            bases=bases,
            methods=methods,
            docstring=ast.get_docstring(node),
            line_number=node.lineno,
            decorators=decorators,
        )

