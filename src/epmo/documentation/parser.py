"""
Python AST Parser for CORTEX Entry Point Modules

Analyzes Python source code using Abstract Syntax Tree (AST) parsing
to extract classes, functions, imports, and structural information
for documentation generation.

Features:
- Complete AST traversal and analysis
- Class and function extraction with metadata
- Import dependency mapping
- Docstring extraction and analysis
- Type hint processing
- Decorator recognition
"""

import ast
import inspect
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field


@dataclass
class FunctionInfo:
    """Information about a function or method."""
    name: str
    line_number: int
    docstring: Optional[str] = None
    parameters: List[str] = field(default_factory=list)
    return_type: Optional[str] = None
    decorators: List[str] = field(default_factory=list)
    is_method: bool = False
    is_private: bool = False
    complexity: int = 0


@dataclass
class ClassInfo:
    """Information about a class."""
    name: str
    line_number: int
    docstring: Optional[str] = None
    methods: List[FunctionInfo] = field(default_factory=list)
    base_classes: List[str] = field(default_factory=list)
    decorators: List[str] = field(default_factory=list)
    is_private: bool = False


@dataclass
class ImportInfo:
    """Information about an import statement."""
    module: str
    names: List[str] = field(default_factory=list)
    alias: Optional[str] = None
    is_from_import: bool = False
    line_number: int = 0


@dataclass
class EPMAnalysis:
    """Complete analysis results for an Entry Point Module."""
    file_path: Path
    functions: List[FunctionInfo] = field(default_factory=list)
    classes: List[ClassInfo] = field(default_factory=list)
    imports: List[ImportInfo] = field(default_factory=list)
    docstring: Optional[str] = None
    total_lines: int = 0
    complexity_score: int = 0
    has_tests: bool = False


class EPMASTParser:
    """
    Python AST parser for Entry Point Module analysis.
    
    Extracts structural information, dependencies, and metadata
    from Python source files for documentation generation.
    """
    
    def __init__(self):
        self.current_class = None
        self.analysis_cache = {}
    
    def parse_file(self, file_path: Path) -> EPMAnalysis:
        """
        Parse a single Python file and extract all structural information.
        
        Args:
            file_path: Path to the Python file to analyze
            
        Returns:
            EPMAnalysis object containing extracted information
            
        Raises:
            SyntaxError: If the Python file has syntax errors
            FileNotFoundError: If the file doesn't exist
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Check cache first
        cache_key = str(file_path)
        if cache_key in self.analysis_cache:
            return self.analysis_cache[cache_key]
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            # Parse the AST
            tree = ast.parse(source_code)
            
            # Initialize analysis results
            analysis = EPMAnalysis(
                file_path=file_path,
                total_lines=len(source_code.splitlines()),
                docstring=ast.get_docstring(tree)
            )
            
            # Traverse the AST
            self._analyze_node(tree, analysis)
            
            # Calculate complexity
            analysis.complexity_score = self._calculate_complexity(analysis)
            
            # Check for test file
            analysis.has_tests = self._has_test_file(file_path)
            
            # Cache the results
            self.analysis_cache[cache_key] = analysis
            
            return analysis
            
        except SyntaxError as e:
            raise SyntaxError(f"Syntax error in {file_path}: {e}")
    
    def parse_epmo(self, epmo_path: Path) -> List[EPMAnalysis]:
        """
        Parse all Python files in an Entry Point Module directory.
        
        Args:
            epmo_path: Path to the Entry Point Module directory
            
        Returns:
            List of EPMAnalysis objects for each Python file
        """
        if not epmo_path.exists():
            raise FileNotFoundError(f"EPMO directory not found: {epmo_path}")
        
        python_files = list(epmo_path.rglob("*.py"))
        analyses = []
        
        for py_file in python_files:
            try:
                analysis = self.parse_file(py_file)
                analyses.append(analysis)
            except (SyntaxError, Exception) as e:
                print(f"Warning: Could not parse {py_file}: {e}")
                continue
        
        return analyses
    
    def _analyze_node(self, node: ast.AST, analysis: EPMAnalysis) -> None:
        """Recursively analyze AST nodes."""
        for child in ast.walk(node):
            if isinstance(child, ast.FunctionDef):
                self._analyze_function(child, analysis)
            elif isinstance(child, ast.ClassDef):
                self._analyze_class(child, analysis)
            elif isinstance(child, (ast.Import, ast.ImportFrom)):
                self._analyze_import(child, analysis)
    
    def _analyze_function(self, node: ast.FunctionDef, analysis: EPMAnalysis) -> None:
        """Analyze a function definition."""
        func_info = FunctionInfo(
            name=node.name,
            line_number=node.lineno,
            docstring=ast.get_docstring(node),
            parameters=self._extract_parameters(node),
            return_type=self._extract_return_type(node),
            decorators=self._extract_decorators(node),
            is_method=self.current_class is not None,
            is_private=node.name.startswith('_'),
            complexity=self._calculate_function_complexity(node)
        )
        
        if self.current_class:
            self.current_class.methods.append(func_info)
        else:
            analysis.functions.append(func_info)
    
    def _analyze_class(self, node: ast.ClassDef, analysis: EPMAnalysis) -> None:
        """Analyze a class definition."""
        # Store previous class context
        previous_class = self.current_class
        
        class_info = ClassInfo(
            name=node.name,
            line_number=node.lineno,
            docstring=ast.get_docstring(node),
            base_classes=self._extract_base_classes(node),
            decorators=self._extract_decorators(node),
            is_private=node.name.startswith('_')
        )
        
        # Set current class for method analysis
        self.current_class = class_info
        
        # Analyze class methods
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                self._analyze_function(item, analysis)
        
        # Restore previous class context
        self.current_class = previous_class
        
        analysis.classes.append(class_info)
    
    def _analyze_import(self, node: ast.AST, analysis: EPMAnalysis) -> None:
        """Analyze import statements."""
        if isinstance(node, ast.Import):
            for alias in node.names:
                import_info = ImportInfo(
                    module=alias.name,
                    alias=alias.asname,
                    is_from_import=False,
                    line_number=node.lineno
                )
                analysis.imports.append(import_info)
        
        elif isinstance(node, ast.ImportFrom):
            names = [alias.name for alias in node.names]
            import_info = ImportInfo(
                module=node.module or '',
                names=names,
                is_from_import=True,
                line_number=node.lineno
            )
            analysis.imports.append(import_info)
    
    def _extract_parameters(self, node: ast.FunctionDef) -> List[str]:
        """Extract function parameter names."""
        params = []
        for arg in node.args.args:
            params.append(arg.arg)
        return params
    
    def _extract_return_type(self, node: ast.FunctionDef) -> Optional[str]:
        """Extract return type annotation if present."""
        if node.returns:
            return ast.unparse(node.returns)
        return None
    
    def _extract_decorators(self, node: ast.AST) -> List[str]:
        """Extract decorator names."""
        decorators = []
        if hasattr(node, 'decorator_list'):
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Name):
                    decorators.append(decorator.id)
                elif isinstance(decorator, ast.Call):
                    decorators.append(ast.unparse(decorator))
        return decorators
    
    def _extract_base_classes(self, node: ast.ClassDef) -> List[str]:
        """Extract base class names."""
        bases = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
            else:
                bases.append(ast.unparse(base))
        return bases
    
    def _calculate_function_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity for a function."""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.Try, ast.With)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    def _calculate_complexity(self, analysis: EPMAnalysis) -> int:
        """Calculate total complexity score for the analysis."""
        total = 0
        for func in analysis.functions:
            total += func.complexity
        for cls in analysis.classes:
            for method in cls.methods:
                total += method.complexity
        return total
    
    def _has_test_file(self, file_path: Path) -> bool:
        """Check if there's a corresponding test file."""
        test_patterns = [
            f"test_{file_path.stem}.py",
            f"{file_path.stem}_test.py",
            f"test{file_path.stem}.py"
        ]
        
        # Check in same directory and tests/ subdirectory
        search_dirs = [file_path.parent, file_path.parent / "tests"]
        
        for search_dir in search_dirs:
            if search_dir.exists():
                for pattern in test_patterns:
                    if (search_dir / pattern).exists():
                        return True
        
        return False


def analyze_epmo_structure(epmo_path: Path) -> Dict[str, Any]:
    """
    Convenience function to analyze an EPMO and return structured data.
    
    Args:
        epmo_path: Path to the Entry Point Module directory
        
    Returns:
        Dictionary containing analysis results in JSON-serializable format
    """
    parser = EPMASTParser()
    analyses = parser.parse_epmo(epmo_path)
    
    # Convert to serializable format
    result = {
        'epmo_path': str(epmo_path),
        'total_files': len(analyses),
        'total_functions': sum(len(a.functions) for a in analyses),
        'total_classes': sum(len(a.classes) for a in analyses),
        'total_imports': sum(len(a.imports) for a in analyses),
        'total_lines': sum(a.total_lines for a in analyses),
        'average_complexity': sum(a.complexity_score for a in analyses) / len(analyses) if analyses else 0,
        'files': []
    }
    
    for analysis in analyses:
        file_data = {
            'path': str(analysis.file_path),
            'docstring': analysis.docstring,
            'total_lines': analysis.total_lines,
            'complexity_score': analysis.complexity_score,
            'has_tests': analysis.has_tests,
            'functions': [
                {
                    'name': f.name,
                    'line_number': f.line_number,
                    'docstring': f.docstring,
                    'parameters': f.parameters,
                    'return_type': f.return_type,
                    'decorators': f.decorators,
                    'is_method': f.is_method,
                    'is_private': f.is_private,
                    'complexity': f.complexity
                }
                for f in analysis.functions
            ],
            'classes': [
                {
                    'name': c.name,
                    'line_number': c.line_number,
                    'docstring': c.docstring,
                    'base_classes': c.base_classes,
                    'decorators': c.decorators,
                    'is_private': c.is_private,
                    'methods': [
                        {
                            'name': m.name,
                            'line_number': m.line_number,
                            'docstring': m.docstring,
                            'parameters': m.parameters,
                            'return_type': m.return_type,
                            'decorators': m.decorators,
                            'is_private': m.is_private,
                            'complexity': m.complexity
                        }
                        for m in c.methods
                    ]
                }
                for c in analysis.classes
            ],
            'imports': [
                {
                    'module': i.module,
                    'names': i.names,
                    'alias': i.alias,
                    'is_from_import': i.is_from_import,
                    'line_number': i.line_number
                }
                for i in analysis.imports
            ]
        }
        result['files'].append(file_data)
    
    return result