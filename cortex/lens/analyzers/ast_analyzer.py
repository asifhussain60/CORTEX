"""
AST Analyzer for CORTEX.

Provides Abstract Syntax Tree analysis capabilities for the LENS intelligence cycle.
Extracts functions, classes, imports, and code structure information.

Includes symtable integration for scope analysis:
- Variable scope resolution (local, global, free, cell)
- Symbol classification (imported, assigned, referenced)
- Nested scope analysis (closures, comprehensions)

Authority: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
Phase 43: AC-PHASE43-017 through AC-PHASE43-020
"""

import ast
import symtable
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict, Any

logger = logging.getLogger(__name__)


@dataclass
class FunctionInfo:
    """
    Information about a function definition.
    
    Attributes:
        name: Function name
        line_number: Line number where function is defined
        parameters: List of parameter names
        return_type: Return type annotation (if any)
        docstring: Function docstring
        decorators: List of decorator names
        is_async: Whether function is async
    """
    name: str
    line_number: int
    parameters: List[str] = field(default_factory=list)
    return_type: str = ""
    docstring: str = ""
    decorators: List[str] = field(default_factory=list)
    is_async: bool = False


@dataclass
class ClassInfo:
    """
    Information about a class definition.
    
    Attributes:
        name: Class name
        line_number: Line number where class is defined
        bases: List of base class names
        methods: List of method names
        docstring: Class docstring
        decorators: List of decorator names
    """
    name: str
    line_number: int
    bases: List[str] = field(default_factory=list)
    methods: List[str] = field(default_factory=list)
    docstring: str = ""
    decorators: List[str] = field(default_factory=list)


@dataclass
class ImportInfo:
    """
    Information about an import statement.
    
    Attributes:
        module: Module name being imported
        names: List of names imported from module
        alias: Alias used (if any)
        line_number: Line number of import
    """
    module: str
    names: List[str]
    alias: str = ""
    line_number: int = 0


@dataclass
class ASTAnalysisResult:
    """
    Result of AST analysis.
    
    Attributes:
        success: Whether analysis succeeded
        functions: List of functions found
        classes: List of classes found
        imports: List of imports found
        error: Error message if analysis failed
        metadata: Additional metadata about the analysis
    """
    success: bool
    functions: List[FunctionInfo] = field(default_factory=list)
    classes: List[ClassInfo] = field(default_factory=list)
    imports: List[ImportInfo] = field(default_factory=list)
    error: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class ASTAnalyzer:
    """
    Analyzes Python code using Abstract Syntax Tree (AST).
    
    Extracts:
    - Function definitions and signatures
    - Class definitions and methods
    - Import statements
    - Code structure and organization
    
    Example:
        ```python
        analyzer = ASTAnalyzer()
        
        # Analyze code string
        result = analyzer.analyze_code(code_string)
        for func in result.functions:
            print(f"Function: {func.name} at line {func.line_number}")
        
        # Analyze file
        result = analyzer.analyze_file(Path("module.py"))
        for cls in result.classes:
            print(f"Class: {cls.name} with methods {cls.methods}")
        ```
    """
    
    def analyze_code(self, code: str) -> ASTAnalysisResult:
        """
        Analyze Python code from a string.
        
        Args:
            code: Python source code to analyze
        
        Returns:
            ASTAnalysisResult with extracted information
        """
        try:
            tree = ast.parse(code)
            
            functions = []
            classes = []
            imports = []
            
            # Visit all nodes in the AST
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                    func_info = self._extract_function_info(node)
                    functions.append(func_info)
                
                elif isinstance(node, ast.ClassDef):
                    class_info = self._extract_class_info(node)
                    classes.append(class_info)
                
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(
                            ImportInfo(
                                module=alias.name,
                                names=[alias.name],
                                alias=alias.asname or "",
                                line_number=node.lineno,
                            )
                        )
                
                elif isinstance(node, ast.ImportFrom):
                    names = [alias.name for alias in node.names]
                    # Get first alias for the import
                    first_alias = node.names[0].asname if node.names and node.names[0].asname else ""
                    imports.append(
                        ImportInfo(
                            module=node.module or "",
                            names=names,
                            alias=first_alias,
                            line_number=node.lineno,
                        )
                    )
            
            # Calculate metadata
            line_count = len(code.splitlines())
            
            # Phase 43: Add symtable integration for scope analysis
            scope_analysis = {}
            try:
                symbols = symtable.symtable(code, "<string>", "exec")
                scope_analysis = self._extract_scope_analysis(symbols)
            except Exception as e:
                logger.debug(f"Symtable scope analysis failed: {e}")
                # Continue without scope analysis - not critical
            
            return ASTAnalysisResult(
                success=True,
                functions=functions,
                classes=classes,
                imports=imports,
                metadata={
                    "line_count": line_count,
                    "function_count": len(functions),
                    "class_count": len(classes),
                    "import_count": len(imports),
                    "scope_analysis": scope_analysis,  # Phase 43 addition
                },
            )
        
        except SyntaxError as e:
            return ASTAnalysisResult(
                success=False,
                error=f"Syntax error: {str(e)}",
            )
        except Exception as e:
            return ASTAnalysisResult(
                success=False,
                error=f"Analysis error: {str(e)}",
            )
    
    def analyze_file(self, file_path: Path) -> ASTAnalysisResult:
        """
        Analyze Python code from a file.
        
        Args:
            file_path: Path to Python file
        
        Returns:
            ASTAnalysisResult with extracted information
        """
        try:
            if not file_path.exists():
                return ASTAnalysisResult(
                    success=False,
                    error=f"File not found: {file_path}",
                )
            
            code = file_path.read_text(encoding="utf-8")
            result = self.analyze_code(code)
            
            # Add file path to metadata
            if result.success:
                result.metadata["file_path"] = str(file_path)
            
            return result
        
        except Exception as e:
            return ASTAnalysisResult(
                success=False,
                error=f"Failed to read file: {str(e)}",
            )
    
    def _extract_function_info(self, node: ast.FunctionDef) -> FunctionInfo:
        """
        Extract information from a function definition node.
        
        Args:
            node: AST FunctionDef or AsyncFunctionDef node
        
        Returns:
            FunctionInfo with extracted data
        """
        # Get parameters
        parameters = [arg.arg for arg in node.args.args]
        
        # Get return type annotation
        return_type = ""
        if node.returns:
            return_type = self._get_type_annotation(node.returns)
        
        # Get docstring
        docstring = ast.get_docstring(node) or ""
        
        # Get decorators
        decorators = []
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                decorators.append(decorator.id)
            elif isinstance(decorator, ast.Attribute):
                decorators.append(decorator.attr)
        
        # Check if async
        is_async = isinstance(node, ast.AsyncFunctionDef)
        
        return FunctionInfo(
            name=node.name,
            line_number=node.lineno,
            parameters=parameters,
            return_type=return_type,
            docstring=docstring,
            decorators=decorators,
            is_async=is_async,
        )
    
    def _extract_class_info(self, node: ast.ClassDef) -> ClassInfo:
        """
        Extract information from a class definition node.
        
        Args:
            node: AST ClassDef node
        
        Returns:
            ClassInfo with extracted data
        """
        # Get base classes
        bases = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
            elif isinstance(base, ast.Attribute):
                bases.append(base.attr)
        
        # Get methods
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef) or isinstance(item, ast.AsyncFunctionDef):
                methods.append(item.name)
        
        # Get docstring
        docstring = ast.get_docstring(node) or ""
        
        # Get decorators
        decorators = []
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                decorators.append(decorator.id)
            elif isinstance(decorator, ast.Attribute):
                decorators.append(decorator.attr)
        
        return ClassInfo(
            name=node.name,
            line_number=node.lineno,
            bases=bases,
            methods=methods,
            docstring=docstring,
            decorators=decorators,
        )
    
    def _get_type_annotation(self, node: ast.AST) -> str:
        """
        Extract type annotation as string.
        
        Args:
            node: AST node representing a type annotation
        
        Returns:
            String representation of the type
        """
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Constant):
            return str(node.value)
        elif isinstance(node, ast.Subscript):
            # Handle generic types like List[str]
            if isinstance(node.value, ast.Name):
                return node.value.id
        return ""
    
    def _extract_scope_analysis(self, symbols: symtable.SymbolTable) -> Dict[str, Any]:
        """Phase 43: Extract scope analysis from symtable.
        
        AC-PHASE43-017: Analyzes variable scopes and symbol types.
        AC-PHASE43-018: Identifies local, global, free, and cell variables.
        AC-PHASE43-019: Distinguishes imported from assigned symbols.
        
        Args:
            symbols: SymbolTable from symtable.symtable()
        
        Returns:
            Dictionary with scope analysis information
        """
        analysis = {
            "scopes": [],
            "symbols_by_type": {
                "local": [],
                "global": [],
                "imported": [],
                "free": [],
                "cell": [],
            }
        }
        
        try:
            # Process each symbol in the table
            for symbol in symbols.get_symbols():
                sym_name = symbol.get_name()
                sym_type = "unknown"
                
                # Classify symbol type
                if symbol.is_imported():
                    sym_type = "imported"
                    analysis["symbols_by_type"]["imported"].append(sym_name)
                elif symbol.is_global():
                    sym_type = "global"
                    analysis["symbols_by_type"]["global"].append(sym_name)
                elif symbol.is_free():
                    sym_type = "free"
                    analysis["symbols_by_type"]["free"].append(sym_name)
                else:
                    sym_type = "local"
                    analysis["symbols_by_type"]["local"].append(sym_name)
            
            # Process nested scopes (functions, classes)
            for child in symbols.get_children():
                child_analysis = {
                    "type": child.get_type(),  # "function", "class", "lambda"
                    "name": child.get_name(),
                    "symbols": len(child.get_symbols()),
                    "is_nested": child.is_nested(),
                }
                analysis["scopes"].append(child_analysis)
        except Exception as e:
            logger.debug(f"Error extracting scope analysis: {e}")
            # Return partial analysis
        
        return analysis