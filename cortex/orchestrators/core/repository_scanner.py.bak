"""
Repository Scanner for CORTEX (AC-PROD-004-01).

Provides system-wide code analysis capabilities including:
- File discovery and classification
- Code structure analysis (classes, functions, imports)
- Pattern detection
- Relationship mapping
- Dependency graph construction

This module is part of the Master Orchestrator Stage 2 (Repository Analysis).
It scans the entire codebase to extract intelligence used in subsequent stages.

Author: CORTEX
Status: Production Ready
Version: 1.0.0
"""

from __future__ import annotations

import ast
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Dict, Optional, Set, Tuple, Any

from cortex.brain.core.result import Result, Ok, Err
from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger


# ============================================================================
# Enums
# ============================================================================

class EntityType(Enum):
    """Types of code entities."""
    FILE = "file"
    CLASS = "class"
    FUNCTION = "function"
    IMPORT = "import"
    PATTERN = "pattern"


class PatternCategory(Enum):
    """Categories of code patterns."""
    DECORATOR = "decorator"
    TYPE_HINT = "type_hint"
    DATACLASS = "dataclass"
    ASYNC = "async"
    CONTEXT_MANAGER = "context_manager"
    PROPERTY = "property"
    CLASSMETHOD = "classmethod"
    STATICMETHOD = "staticmethod"
    ABSTRACT = "abstract"
    PROTOCOL = "protocol"


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class ImportStatement:
    """Represents an import statement."""
    module: str
    names: List[str] = field(default_factory=list)
    is_from_import: bool = False
    line_number: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "module": self.module,
            "names": self.names,
            "is_from_import": self.is_from_import,
            "line_number": self.line_number,
        }


@dataclass
class FunctionEntity:
    """Represents a function or method."""
    name: str
    file_path: str
    line_number: int
    parameters: List[str] = field(default_factory=list)
    return_type: Optional[str] = None
    decorators: List[str] = field(default_factory=list)
    is_async: bool = False
    is_method: bool = False
    docstring: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "parameters": self.parameters,
            "return_type": self.return_type,
            "decorators": self.decorators,
            "is_async": self.is_async,
            "is_method": self.is_method,
            "docstring": self.docstring,
        }


@dataclass
class ClassEntity:
    """Represents a class definition."""
    name: str
    file_path: str
    line_number: int
    base_classes: List[str] = field(default_factory=list)
    methods: List[FunctionEntity] = field(default_factory=list)
    attributes: List[str] = field(default_factory=list)
    decorators: List[str] = field(default_factory=list)
    docstring: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "base_classes": self.base_classes,
            "methods": [m.to_dict() for m in self.methods],
            "attributes": self.attributes,
            "decorators": self.decorators,
            "docstring": self.docstring,
        }


@dataclass
class CodePattern:
    """Represents a detected code pattern."""
    name: str
    category: PatternCategory
    file_path: str
    line_number: int
    context: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "category": self.category.value,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "context": self.context,
        }


@dataclass
class FileEntity:
    """Represents a Python file."""
    path: Path
    relative_path: str
    imports: List[ImportStatement] = field(default_factory=list)
    classes: List[ClassEntity] = field(default_factory=list)
    functions: List[FunctionEntity] = field(default_factory=list)
    patterns: List[CodePattern] = field(default_factory=list)
    lines_of_code: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "path": str(self.path),
            "relative_path": self.relative_path,
            "imports": [i.to_dict() for i in self.imports],
            "classes": [c.to_dict() for c in self.classes],
            "functions": [f.to_dict() for f in self.functions],
            "patterns": [p.to_dict() for p in self.patterns],
            "lines_of_code": self.lines_of_code,
        }


@dataclass
class Relationship:
    """Represents a relationship between entities."""
    source: str  # e.g., "module1.py::ClassName"
    target: str  # e.g., "module2.py::ClassName"
    relationship_type: str  # "imports", "inherits", "uses", etc.
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "source": self.source,
            "target": self.target,
            "relationship_type": self.relationship_type,
        }


@dataclass
class DependencyGraph:
    """Represents the complete dependency graph."""
    files: List[FileEntity] = field(default_factory=list)
    relationships: List[Relationship] = field(default_factory=list)
    circular_dependencies: List[List[str]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "files": [f.to_dict() for f in self.files],
            "relationships": [r.to_dict() for r in self.relationships],
            "circular_dependencies": self.circular_dependencies,
        }


@dataclass
class ScanContext:
    """Context for repository scanning."""
    workspace_root: Path
    target_paths: List[Path]
    exclude_patterns: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "workspace_root": str(self.workspace_root),
            "target_paths": [str(p) for p in self.target_paths],
            "exclude_patterns": self.exclude_patterns,
        }


@dataclass
class ScanOutput:
    """Output of repository scan."""
    workspace_root: Path
    files: List[FileEntity] = field(default_factory=list)
    entities: DependencyGraph = field(default_factory=DependencyGraph)
    file_count: int = 0
    class_count: int = 0
    function_count: int = 0
    import_count: int = 0
    pattern_count: int = 0
    total_lines_of_code: int = 0
    timestamp: Optional[datetime] = None
    scan_duration: float = 0.0
    scanner_version: str = "1.0.0"
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "workspace_root": str(self.workspace_root),
            "files": [f.to_dict() for f in self.files],
            "entities": self.entities.to_dict(),
            "file_count": self.file_count,
            "class_count": self.class_count,
            "function_count": self.function_count,
            "import_count": self.import_count,
            "pattern_count": self.pattern_count,
            "total_lines_of_code": self.total_lines_of_code,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "scan_duration": self.scan_duration,
            "scanner_version": self.scanner_version,
            "errors": self.errors,
        }


# ============================================================================
# Repository Scanner
# ============================================================================

class RepositoryScanner:
    """
    Scans a repository to extract code intelligence.
    
    Responsibilities:
    - Discover Python files
    - Analyze code structure (classes, functions, imports)
    - Detect patterns
    - Build dependency graphs
    - Generate scan reports
    
    Usage:
        scanner = RepositoryScanner(workspace_root=Path("/project"))
        context = ScanContext(
            workspace_root=Path("/project"),
            target_paths=[Path("/project/src")],
            exclude_patterns=["*.pyc", "__pycache__"],
        )
        result = scanner.scan(context)
    """
    
    def __init__(self, workspace_root: Path) -> None:
        """
        Initialize repository scanner.
        
        Args:
            workspace_root: Root directory of workspace
        """
        self.workspace_root = workspace_root
        self.logger = EnhancedAuditLogger()
    
    def scan(self, context: ScanContext) -> ScanOutput:
        """
        Perform repository scan.
        
        Args:
            context: Scan context with paths and patterns
            
        Returns:
            ScanOutput with analysis results
        """
        ac_id = "AC-PROD-004-01"
        
        self.logger.log_operation_start(
            ac_id=ac_id,
            operation="Repository Scan",
            details={
                "workspace": str(context.workspace_root),
                "target_count": len(context.target_paths),
            },
        )
        
        start_time = time.time()
        try:
            output = ScanOutput(
                workspace_root=context.workspace_root,
                timestamp=datetime.now(),
            )
            
            # Discover files
            files = self.discover_files(context)
            
            # Analyze each file
            for file_entity in files:
                output.files.append(file_entity)
                output.file_count += 1
                output.total_lines_of_code += file_entity.lines_of_code
                output.class_count += len(file_entity.classes)
                output.function_count += len(file_entity.functions)
                output.import_count += len(file_entity.imports)
                output.pattern_count += len(file_entity.patterns)
            
            # Build dependency graph
            output.entities = self.build_dependency_graph(context, output.files)
            
            # Calculate duration
            output.scan_duration = time.time() - start_time
            
            self.logger.log_operation_complete(
                ac_id=ac_id,
                operation="Repository Scan",
                success=True,
                details={
                    "files_scanned": output.file_count,
                    "classes_found": output.class_count,
                    "functions_found": output.function_count,
                    "duration": f"{output.scan_duration:.2f}s",
                },
            )
            
            return output
            
        except Exception as e:
            self.logger.log_operation_complete(
                ac_id=ac_id,
                operation="Repository Scan",
                success=False,
                details={"error": str(e)},
            )
            raise
    
    def discover_files(self, context: ScanContext) -> List[FileEntity]:
        """
        Discover Python files in target paths.
        
        Args:
            context: Scan context
            
        Returns:
            List of discovered FileEntity objects
        """
        files = []
        
        for target_path in context.target_paths:
            if not target_path.exists():
                continue
            
            # Find all Python files
            pattern = "**/*.py"
            for py_file in target_path.glob(pattern):
                # Check exclusion patterns
                if self._should_exclude(py_file, context.exclude_patterns):
                    continue
                
                # Analyze file
                try:
                    file_entity = self.analyze_file_path(
                        py_file,
                        context.workspace_root,
                    )
                    if file_entity:
                        files.append(file_entity)
                except Exception as e:
                    # Log error but continue
                    pass
        
        return files
    
    def analyze_file_path(
        self,
        file_path: Path,
        workspace_root: Path,
    ) -> Optional[FileEntity]:
        """
        Analyze a Python file.
        
        Args:
            file_path: Path to Python file
            workspace_root: Workspace root for relative paths
            
        Returns:
            FileEntity or None if error
        """
        try:
            content = file_path.read_text(encoding='utf-8')
            return self.analyze_file(str(file_path), content, workspace_root)
        except Exception:
            return None
    
    def analyze_file(
        self,
        file_path: str,
        content: str,
        workspace_root: Optional[Path] = None,
    ) -> Optional[FileEntity]:
        """
        Analyze file content.
        
        Args:
            file_path: Path to file
            content: File content
            workspace_root: Workspace root (optional)
            
        Returns:
            FileEntity or None
        """
        try:
            # Parse AST
            tree = ast.parse(content)
            
            # Determine relative path
            if workspace_root:
                full_path = Path(file_path)
                try:
                    relative_path = str(full_path.relative_to(workspace_root))
                except ValueError:
                    relative_path = file_path
            else:
                relative_path = file_path
            
            # Create file entity
            file_entity = FileEntity(
                path=Path(file_path),
                relative_path=relative_path,
                lines_of_code=len(content.split('\n')),
            )
            
            # Extract imports
            file_entity.imports = self.extract_imports(content)
            
            # Identify classes and functions
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_entity = self._extract_class(node, file_path, content)
                    file_entity.classes.append(class_entity)
                elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                    # Only top-level functions (not methods)
                    if isinstance(node, ast.FunctionDef) and not self._is_nested(node, tree):
                        func_entity = self._extract_function(node, file_path, content)
                        file_entity.functions.append(func_entity)
            
            # Detect patterns
            file_entity.patterns = self.detect_patterns(content, file_path)
            
            return file_entity
            
        except Exception:
            return None
    
    def extract_imports(self, content: str) -> List[ImportStatement]:
        """
        Extract import statements from code.
        
        Args:
            content: Python code content
            
        Returns:
            List of ImportStatement objects
        """
        imports = []
        try:
            tree = ast.parse(content)
            
            for i, node in enumerate(ast.walk(tree)):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(ImportStatement(
                            module=alias.name,
                            is_from_import=False,
                            line_number=node.lineno,
                        ))
                elif isinstance(node, ast.ImportFrom):
                    names = [alias.name for alias in node.names]
                    imports.append(ImportStatement(
                        module=node.module or ".",
                        names=names,
                        is_from_import=True,
                        line_number=node.lineno,
                    ))
        except Exception:
            pass
        
        return imports
    
    def identify_classes(self, content: str) -> List[ClassEntity]:
        """
        Identify class definitions in code.
        
        Args:
            content: Python code content
            
        Returns:
            List of ClassEntity objects
        """
        classes = []
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_entity = self._extract_class(node, "<input>", content)
                    classes.append(class_entity)
        except Exception:
            pass
        
        return classes
    
    def identify_functions(self, content: str) -> List[FunctionEntity]:
        """
        Identify function definitions in code.
        
        Args:
            content: Python code content
            
        Returns:
            List of FunctionEntity objects
        """
        functions = []
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if not self._is_nested(node, tree):
                        func_entity = self._extract_function(node, "<input>", content)
                        functions.append(func_entity)
        except Exception:
            pass
        
        return functions
    
    def detect_patterns(
        self,
        content: str,
        file_path: str = "<input>",
    ) -> List[CodePattern]:
        """
        Detect code patterns in content.
        
        Args:
            content: Python code content
            file_path: File path for reference
            
        Returns:
            List of CodePattern objects
        """
        patterns = []
        try:
            tree = ast.parse(content)
            lines = content.split('\n')
            
            for node in ast.walk(tree):
                # Detect decorators
                if hasattr(node, 'decorator_list'):
                    for decorator in node.decorator_list:
                        decorator_name = self._get_node_name(decorator)
                        if decorator_name:
                            patterns.append(CodePattern(
                                name=decorator_name,
                                category=PatternCategory.DECORATOR,
                                file_path=file_path,
                                line_number=node.lineno,
                            ))
                
                # Detect dataclass
                if isinstance(node, ast.ClassDef):
                    for dec in node.decorator_list:
                        if isinstance(dec, ast.Name) and dec.id == "dataclass":
                            patterns.append(CodePattern(
                                name="dataclass",
                                category=PatternCategory.DATACLASS,
                                file_path=file_path,
                                line_number=node.lineno,
                            ))
                
                # Detect type hints
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if node.returns:
                        patterns.append(CodePattern(
                            name="type_hint",
                            category=PatternCategory.TYPE_HINT,
                            file_path=file_path,
                            line_number=node.lineno,
                        ))
        
        except Exception:
            pass
        
        return patterns
    
    def build_dependency_graph(
        self,
        context: Optional[ScanContext] = None,
        files: Optional[List[FileEntity]] = None,
    ) -> DependencyGraph:
        """
        Build dependency graph from files.
        
        Args:
            context: Scan context (optional)
            files: List of FileEntity objects (optional)
            
        Returns:
            DependencyGraph object
        """
        graph = DependencyGraph()
        
        if files:
            graph.files = files
            
            # Build relationships from imports
            for file_entity in files:
                for import_stmt in file_entity.imports:
                    # Create relationship
                    source = file_entity.relative_path
                    target = import_stmt.module
                    
                    rel = Relationship(
                        source=source,
                        target=target,
                        relationship_type="imports",
                    )
                    graph.relationships.append(rel)
        
        return graph
    
    def generate_summary(self, output: ScanOutput) -> str:
        """
        Generate text summary of scan results.
        
        Args:
            output: ScanOutput object
            
        Returns:
            Text summary
        """
        summary = f"""
Repository Scan Summary
======================
Workspace: {output.workspace_root}
Scan Time: {output.timestamp}
Duration: {output.scan_duration:.2f}s

Statistics:
- Files: {output.file_count}
- Classes: {output.class_count}
- Functions: {output.function_count}
- Imports: {output.import_count}
- Patterns: {output.pattern_count}
- Lines of Code: {output.total_lines_of_code}

Errors: {len(output.errors)}
"""
        return summary.strip()
    
    # ========================================================================
    # Private Helper Methods
    # ========================================================================
    
    def _should_exclude(self, file_path: Path, exclude_patterns: List[str]) -> bool:
        """Check if file should be excluded."""
        for pattern in exclude_patterns:
            if file_path.match(pattern):
                return True
        return False
    
    def _extract_class(
        self,
        node: ast.ClassDef,
        file_path: str,
        content: str,
    ) -> ClassEntity:
        """Extract class information from AST node."""
        base_classes = [self._get_node_name(base) for base in node.bases]
        base_classes = [b for b in base_classes if b]
        
        decorators = [self._get_node_name(d) for d in node.decorator_list]
        decorators = [d for d in decorators if d]
        
        methods = []
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method = self._extract_function(item, file_path, content, is_method=True)
                methods.append(method)
        
        return ClassEntity(
            name=node.name,
            file_path=file_path,
            line_number=node.lineno,
            base_classes=base_classes,
            methods=methods,
            decorators=decorators,
            docstring=ast.get_docstring(node),
        )
    
    def _extract_function(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        file_path: str,
        content: str,
        is_method: bool = False,
    ) -> FunctionEntity:
        """Extract function information from AST node."""
        args = node.args
        parameters = [arg.arg for arg in args.args]
        
        decorators = [self._get_node_name(d) for d in node.decorator_list]
        decorators = [d for d in decorators if d]
        
        return_type = None
        if node.returns:
            return_type = self._get_node_name(node.returns)
        
        return FunctionEntity(
            name=node.name,
            file_path=file_path,
            line_number=node.lineno,
            parameters=parameters,
            return_type=return_type,
            decorators=decorators,
            is_async=isinstance(node, ast.AsyncFunctionDef),
            is_method=is_method,
            docstring=ast.get_docstring(node),
        )
    
    def _is_nested(self, node: ast.AST, tree: ast.Module) -> bool:
        """Check if node is nested inside a class."""
        for top_level in tree.body:
            if isinstance(top_level, ast.ClassDef):
                for item in top_level.body:
                    if item == node:
                        return True
        return False
    
    def _get_node_name(self, node: ast.expr) -> Optional[str]:
        """Extract name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            value = self._get_node_name(node.value)
            if value:
                return f"{value}.{node.attr}"
            return node.attr
        elif isinstance(node, ast.Subscript):
            return self._get_node_name(node.value)
        return None
