"""
Code Analyzer - Extract metadata and structure from Python code

Uses AST (Abstract Syntax Tree) to analyze Python files and extract:
- Classes and their methods
- Function signatures and docstrings
- Type hints and annotations
- Inheritance hierarchies
- Module structure
"""

import ast
import inspect
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


@dataclass
class MethodInfo:
    """Information about a class method"""
    name: str
    signature: str
    docstring: Optional[str]
    return_type: Optional[str]
    parameters: List[Dict[str, Any]]
    is_abstract: bool
    is_property: bool
    decorators: List[str]
    line_number: int


@dataclass
class ClassInfo:
    """Information about a class"""
    name: str
    docstring: Optional[str]
    base_classes: List[str]
    methods: List[MethodInfo]
    attributes: List[Dict[str, Any]]
    is_abstract: bool
    decorators: List[str]
    line_number: int


@dataclass
class FunctionInfo:
    """Information about a standalone function"""
    name: str
    signature: str
    docstring: Optional[str]
    return_type: Optional[str]
    parameters: List[Dict[str, Any]]
    decorators: List[str]
    line_number: int


@dataclass
class ModuleInfo:
    """Information about a Python module"""
    name: str
    path: Path
    docstring: Optional[str]
    classes: List[ClassInfo] = field(default_factory=list)
    functions: List[FunctionInfo] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    dependencies: Set[str] = field(default_factory=set)


class CodeAnalyzer:
    """
    Analyzes Python code using AST to extract structural information
    
    Example:
        analyzer = CodeAnalyzer()
        module_info = analyzer.analyze_file(Path("my_module.py"))
        
        # Access extracted information
        for cls in module_info.classes:
            print(f"Class: {cls.name}")
            for method in cls.methods:
                print(f"  Method: {method.name} - {method.signature}")
    """
    
    def __init__(self):
        self.logger = None  # Will be injected by orchestrator
    
    def analyze_file(self, file_path: Path) -> ModuleInfo:
        """
        Analyze a Python file and extract all metadata
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            ModuleInfo containing all extracted information
            
        Raises:
            SyntaxError: If the file contains invalid Python syntax
            FileNotFoundError: If the file doesn't exist
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        try:
            tree = ast.parse(source)
        except SyntaxError as e:
            raise SyntaxError(f"Invalid Python syntax in {file_path}: {e}")
        
        module_info = ModuleInfo(
            name=file_path.stem,
            path=file_path,
            docstring=ast.get_docstring(tree)
        )
        
        # Extract imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_info.imports.append(alias.name)
                    module_info.dependencies.add(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    module_info.imports.append(node.module)
                    module_info.dependencies.add(node.module.split('.')[0])
        
        # Extract top-level definitions
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                module_info.classes.append(self._extract_class_info(node))
            elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                module_info.functions.append(self._extract_function_info(node))
        
        return module_info
    
    def _extract_class_info(self, node: ast.ClassDef) -> ClassInfo:
        """Extract information from a class definition"""
        base_classes = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                base_classes.append(base.id)
            elif isinstance(base, ast.Attribute):
                base_classes.append(self._get_full_name(base))
        
        decorators = [self._get_decorator_name(dec) for dec in node.decorator_list]
        is_abstract = 'abstractmethod' in decorators or 'ABC' in base_classes
        
        methods = []
        attributes = []
        
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                methods.append(self._extract_method_info(item))
            elif isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                # Class attribute with type annotation
                attributes.append({
                    'name': item.target.id,
                    'type': self._get_annotation(item.annotation),
                    'line_number': item.lineno
                })
        
        return ClassInfo(
            name=node.name,
            docstring=ast.get_docstring(node),
            base_classes=base_classes,
            methods=methods,
            attributes=attributes,
            is_abstract=is_abstract,
            decorators=decorators,
            line_number=node.lineno
        )
    
    def _extract_method_info(self, node: ast.FunctionDef) -> MethodInfo:
        """Extract information from a method definition"""
        decorators = [self._get_decorator_name(dec) for dec in node.decorator_list]
        is_abstract = 'abstractmethod' in decorators
        is_property = 'property' in decorators
        
        parameters = self._extract_parameters(node)
        return_type = self._get_annotation(node.returns) if node.returns else None
        
        # Build signature
        params_str = ', '.join([
            f"{p['name']}: {p['type']}" if p['type'] else p['name']
            for p in parameters
        ])
        signature = f"{node.name}({params_str})"
        if return_type:
            signature += f" -> {return_type}"
        
        return MethodInfo(
            name=node.name,
            signature=signature,
            docstring=ast.get_docstring(node),
            return_type=return_type,
            parameters=parameters,
            is_abstract=is_abstract,
            is_property=is_property,
            decorators=decorators,
            line_number=node.lineno
        )
    
    def _extract_function_info(self, node: ast.FunctionDef) -> FunctionInfo:
        """Extract information from a function definition"""
        decorators = [self._get_decorator_name(dec) for dec in node.decorator_list]
        parameters = self._extract_parameters(node)
        return_type = self._get_annotation(node.returns) if node.returns else None
        
        # Build signature
        params_str = ', '.join([
            f"{p['name']}: {p['type']}" if p['type'] else p['name']
            for p in parameters
        ])
        signature = f"{node.name}({params_str})"
        if return_type:
            signature += f" -> {return_type}"
        
        return FunctionInfo(
            name=node.name,
            signature=signature,
            docstring=ast.get_docstring(node),
            return_type=return_type,
            parameters=parameters,
            decorators=decorators,
            line_number=node.lineno
        )
    
    def _extract_parameters(self, node: ast.FunctionDef) -> List[Dict[str, Any]]:
        """Extract parameter information from a function"""
        parameters = []
        args = node.args
        
        # Regular arguments
        for arg in args.args:
            parameters.append({
                'name': arg.arg,
                'type': self._get_annotation(arg.annotation) if arg.annotation else None,
                'default': None,
                'kind': 'positional'
            })
        
        # Handle defaults (align with args from the right)
        if args.defaults:
            default_offset = len(args.args) - len(args.defaults)
            for i, default in enumerate(args.defaults):
                parameters[default_offset + i]['default'] = ast.unparse(default)
        
        # *args
        if args.vararg:
            parameters.append({
                'name': f"*{args.vararg.arg}",
                'type': self._get_annotation(args.vararg.annotation) if args.vararg.annotation else None,
                'default': None,
                'kind': 'var_positional'
            })
        
        # **kwargs
        if args.kwarg:
            parameters.append({
                'name': f"**{args.kwarg.arg}",
                'type': self._get_annotation(args.kwarg.annotation) if args.kwarg.annotation else None,
                'default': None,
                'kind': 'var_keyword'
            })
        
        return parameters
    
    def _get_annotation(self, annotation: Optional[ast.expr]) -> Optional[str]:
        """Convert an annotation AST node to a string"""
        if annotation is None:
            return None
        try:
            return ast.unparse(annotation)
        except Exception:
            return str(annotation)
    
    def _get_decorator_name(self, decorator: ast.expr) -> str:
        """Extract decorator name from AST node"""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return self._get_full_name(decorator)
        elif isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Name):
                return decorator.func.id
            elif isinstance(decorator.func, ast.Attribute):
                return self._get_full_name(decorator.func)
        return "unknown"
    
    def _get_full_name(self, node: ast.Attribute) -> str:
        """Get the full dotted name from an Attribute node"""
        parts = []
        current = node
        while isinstance(current, ast.Attribute):
            parts.insert(0, current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.insert(0, current.id)
        return '.'.join(parts)
