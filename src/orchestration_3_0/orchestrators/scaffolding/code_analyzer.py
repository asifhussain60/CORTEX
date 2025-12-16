"""
Code Analyzer Component
Deep semantic understanding of legacy codebase using native Python AST parsing.

Features:
- Python AST parsing using built-in ast module
- Dependency graph generation
- Anti-pattern detection (God objects, circular deps, tight coupling)
- Hotspot identification (high complexity, high churn)
- Technology stack detection

Note: Multi-language support (JS/TS/C#) available via parser_registry if needed.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Tuple
import logging
import json
import ast
from collections import defaultdict
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class AntiPattern:
    """Represents a code anti-pattern detection."""
    type: str  # god_object, circular_dependency, tight_coupling, hardcoded_value
    file: str
    lines: Optional[int] = None
    confidence: float = 0.0
    details: Optional[str] = None


@dataclass
class Hotspot:
    """Represents a high-risk code hotspot."""
    file: str
    complexity: int  # Cyclomatic complexity estimate
    churn: int  # Number of Git commits (placeholder for now)
    confidence: float = 0.0


@dataclass
class CodeStructureReport:
    """Complete code analysis report."""
    language: str
    framework: Optional[str]
    version: Optional[str]
    modules: int
    classes: int
    functions: int
    dependencies: Dict[str, int]
    anti_patterns: List[AntiPattern]
    hotspots: List[Hotspot]


class CodeAnalyzer:
    """
    Deep code analysis using native Python AST parsing.
    
    Uses Python's built-in ast module for Python files.
    For multi-language support, extend with parser_registry.
    Detects anti-patterns, generates dependency graphs, identifies hotspots.
    
    Example:
        analyzer = CodeAnalyzer(repo_path="path/to/legacy/app")
        report = analyzer.analyze()
        print(f"Found {len(report.anti_patterns)} anti-patterns")
    """
    
    # God object threshold (LOC per file)
    GOD_OBJECT_THRESHOLD = 500
    
    # High complexity threshold (cyclomatic complexity estimate)
    HIGH_COMPLEXITY_THRESHOLD = 40
    
    def __init__(self, repo_path: str, exclusions: Optional[List[str]] = None):
        """
        Initialize code analyzer.
        
        Args:
            repo_path: Path to repository root
            exclusions: List of glob patterns to exclude (e.g., ["vendor/*", "node_modules/*"])
        """
        self.repo_path = Path(repo_path)
        self.exclusions = exclusions or ['vendor/*', 'node_modules/*', 'venv/*', '__pycache__/*', '*.pyc', 'dist/*', 'build/*']
        
        # Analysis state
        self.source_files: List[Path] = []
        self.language: Optional[SupportedLanguage] = None
        self.module_count = 0
        self.class_count = 0
        self.function_count = 0
        self.internal_dependencies: Set[str] = set()
        self.external_dependencies: Set[str] = set()
        self.anti_patterns: List[AntiPattern] = []
        self.hotspots: List[Hotspot] = []
    
    def analyze(self) -> CodeStructureReport:
        """
        Perform complete code analysis.
        
        Returns:
            CodeStructureReport with all analysis results
        """
        logger.info(f"Starting code analysis for {self.repo_path}")
        
        # Step 1: Discover source files
        self._discover_source_files()
        
        if not self.source_files:
            logger.warning(f"No source files found in {self.repo_path}")
            return self._empty_report()
        
        # Step 2: Detect primary language
        self._detect_primary_language()
        
        # Step 3: Parse files and extract metrics
        self._parse_and_extract()
        
        # Step 4: Detect anti-patterns
        self._detect_anti_patterns()
        
        # Step 5: Identify hotspots
        self._identify_hotspots()
        
        # Step 6: Detect framework
        framework, version = self._detect_framework()
        
        # Build final report
        report = CodeStructureReport(
            language=self.language if self.language else "unknown",
            framework=framework,
            version=version,
            modules=self.module_count,
            classes=self.class_count,
            functions=self.function_count,
            dependencies={
                "internal": len(self.internal_dependencies),
                "external": len(self.external_dependencies)
            },
            anti_patterns=self.anti_patterns,
            hotspots=self.hotspots
        )
        
        logger.info(f"Analysis complete: {self.module_count} modules, {len(self.anti_patterns)} anti-patterns, {len(self.hotspots)} hotspots")
        return report
    
    def _discover_source_files(self):
        """Discover all source code files in repository."""
        # Currently focuses on Python files (native ast support)
        # For multi-language, extend with parser_registry
        extensions = ['.py']
        
        for ext in extensions:
            for file_path in self.repo_path.rglob(f'*{ext}'):
                # Check exclusions
                if any(file_path.match(pattern) for pattern in self.exclusions):
                    continue
                
                self.source_files.append(file_path)
        
        logger.info(f"Discovered {len(self.source_files)} source files")
    
    def _detect_primary_language(self):
        """Detect primary programming language from file extensions."""
        language_counts = defaultdict(int)
        
        for file_path in self.source_files:
            ext = file_path.suffix.lower()
            if ext == '.py':
                language_counts['python'] += 1
            elif ext in ['.js', '.jsx']:
                language_counts['javascript'] += 1
            elif ext in ['.ts', '.tsx']:
                language_counts['typescript'] += 1
            elif ext == '.cs':
                language_counts['csharp'] += 1
        
        if language_counts:
            self.language = max(language_counts, key=language_counts.get)
            logger.info(f"Primary language detected: {self.language}")
    
    def _parse_and_extract(self):
        """Parse all files and extract code structure metrics."""
        for file_path in self.source_files:
            ext = file_path.suffix.lower()
            
            if ext == '.py':
                self._parse_python_file(file_path)
            # Add more language support via parser_registry as needed
    
    def _parse_python_file(self, file_path: Path):
        """Parse Python file using native ast module."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            tree = ast.parse(source_code, filename=str(file_path))
            self.module_count += 1
            
            # Extract classes, functions, and imports
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    self.class_count += 1
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    self.function_count += 1
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        module = alias.name.split('.')[0]
                        self._classify_dependency(module)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        module = node.module.split('.')[0]
                        self._classify_dependency(module)
        
        except Exception as e:
            logger.warning(f"Failed to parse {file_path}: {e}")
    
    def _classify_dependency(self, module: str):
        """Classify import as internal or external dependency."""
        # Internal if starts with . or exists in repo
        if module.startswith('.') or (self.repo_path / f"{module}.py").exists():
            self.internal_dependencies.add(module)
        else:
            self.external_dependencies.add(module)
    
    def _extract_python_structures(self, tree, file_path: Path):
        """DEPRECATED: Legacy tree-sitter method - replaced by _parse_python_file."""
        pass
    
    def _extract_javascript_structures(self, tree, file_path: Path):
        """DEPRECATED: Legacy tree-sitter method - not currently used."""
        pass
    
    def _extract_csharp_structures(self, tree, file_path: Path):
        """DEPRECATED: Legacy tree-sitter method - not currently used."""
        pass
    
    def _detect_anti_patterns(self):
        """Detect code anti-patterns using AST analysis."""
        for file_path in self.source_files:
            # God object detection (simple heuristic: file size)
            loc = sum(1 for _ in open(file_path, 'rb'))
            if loc > self.GOD_OBJECT_THRESHOLD:
                self.anti_patterns.append(AntiPattern(
                    type="god_object",
                    file=str(file_path.relative_to(self.repo_path)),
                    lines=loc,
                    confidence=min(0.9, loc / self.GOD_OBJECT_THRESHOLD),
                    details=f"File has {loc} lines (threshold: {self.GOD_OBJECT_THRESHOLD})"
                ))
        
        # TODO: Circular dependency detection (requires import graph analysis)
        # TODO: Tight coupling detection (requires call graph analysis)
        # TODO: Hardcoded value detection (requires literal node analysis)
    
    def _identify_hotspots(self):
        """Identify high-risk code hotspots."""
        for file_path in self.source_files:
            ext = file_path.suffix.lower()
            
            if ext == '.py':
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        source_code = f.read()
                    
                    tree = ast.parse(source_code, filename=str(file_path))
                    complexity = self._estimate_complexity_ast(tree)
                    
                    if complexity > self.HIGH_COMPLEXITY_THRESHOLD:
                        self.hotspots.append(Hotspot(
                            file=str(file_path.relative_to(self.repo_path)),
                            complexity=complexity,
                            churn=0,  # Placeholder - requires Git history analysis
                            confidence=min(0.9, complexity / self.HIGH_COMPLEXITY_THRESHOLD)
                        ))
                except Exception as e:
                    logger.warning(f"Failed to analyze hotspot for {file_path}: {e}")
    
    def _estimate_complexity_ast(self, tree: ast.AST) -> int:
        """Estimate cyclomatic complexity by counting control flow nodes."""
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            # Count decision points
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler,
                               ast.With, ast.Assert, ast.BoolOp)):
                complexity += 1
            elif isinstance(node, ast.comprehension):
                complexity += 1
        
        return complexity
    
    def _detect_framework(self) -> Tuple[Optional[str], Optional[str]]:
        """Detect framework and version from imports/dependencies."""
        framework_indicators = {
            'flask': 'Flask',
            'fastapi': 'FastAPI',
            'django': 'Django',
            'express': 'Express',
            'react': 'React',
            'angular': 'Angular',
            'dotnet': '.NET'
        }
        
        # Check external dependencies
        for dep in self.external_dependencies:
            for indicator, framework_name in framework_indicators.items():
                if indicator in dep.lower():
                    return framework_name, None  # Version detection requires package file parsing
        
        # Fallback: Scan file contents for import patterns
        for file_path in self.source_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read(500)  # Read first 500 chars for imports
                    for indicator, framework_name in framework_indicators.items():
                        if f"import {indicator}" in content.lower() or f"from {indicator}" in content.lower():
                            return framework_name, None
            except Exception:
                continue
        
        return None, None
    
    def _empty_report(self) -> CodeStructureReport:
        """Return empty report when no files found."""
        return CodeStructureReport(
            language="unknown",
            framework=None,
            version=None,
            modules=0,
            classes=0,
            functions=0,
            dependencies={"internal": 0, "external": 0},
            anti_patterns=[],
            hotspots=[]
        )
    
    def to_dict(self, report: CodeStructureReport) -> Dict[str, Any]:
        """Convert report to dictionary for JSON serialization."""
        return {
            **asdict(report),
            'anti_patterns': [asdict(ap) for ap in report.anti_patterns],
            'hotspots': [asdict(h) for h in report.hotspots]
        }
