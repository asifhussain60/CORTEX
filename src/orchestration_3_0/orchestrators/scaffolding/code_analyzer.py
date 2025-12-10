"""
Code Analyzer Component
Deep semantic understanding of legacy codebase using Tree-sitter AST parsing.

Features:
- Multi-language AST parsing (Python/JS/TS/C#)
- Dependency graph generation
- Anti-pattern detection (God objects, circular deps, tight coupling)
- Hotspot identification (high complexity, high churn)
- Technology stack detection
"""

from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Tuple
import logging
import json
from collections import defaultdict
from dataclasses import dataclass, asdict

from src.intelligence.tree_sitter_parser import TreeSitterParser, SupportedLanguage, TREE_SITTER_AVAILABLE

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
    Deep code analysis using Tree-sitter AST parsing.
    
    Reuses TreeSitterParser from intelligence module for multi-language support.
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
        if not TREE_SITTER_AVAILABLE:
            raise ImportError("Tree-sitter not available. Install with: pip install tree-sitter tree-sitter-python tree-sitter-javascript tree-sitter-c-sharp")
        
        self.repo_path = Path(repo_path)
        self.exclusions = exclusions or ['vendor/*', 'node_modules/*', 'venv/*', '__pycache__/*', '*.pyc', 'dist/*', 'build/*']
        self.parser = TreeSitterParser()
        
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
            language=self.language.value if self.language else "unknown",
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
        extensions = ['.py', '.js', '.jsx', '.ts', '.tsx', '.cs']
        
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
            lang = self.parser.detect_language(str(file_path))
            if lang:
                language_counts[lang] += 1
        
        if language_counts:
            self.language = max(language_counts, key=language_counts.get)
            logger.info(f"Primary language detected: {self.language.value}")
    
    def _parse_and_extract(self):
        """Parse all files and extract code structure metrics."""
        for file_path in self.source_files:
            lang = self.parser.detect_language(str(file_path))
            if not lang:
                continue
            
            tree = self.parser.parse_file(str(file_path), lang)
            if not tree:
                logger.warning(f"Failed to parse {file_path}")
                continue
            
            self.module_count += 1
            
            # Extract classes and functions using Tree-sitter queries
            if lang == SupportedLanguage.PYTHON:
                self._extract_python_structures(tree, file_path)
            elif lang in [SupportedLanguage.JAVASCRIPT, SupportedLanguage.TYPESCRIPT]:
                self._extract_javascript_structures(tree, file_path)
            elif lang == SupportedLanguage.CSHARP:
                self._extract_csharp_structures(tree, file_path)
    
    def _extract_python_structures(self, tree, file_path: Path):
        """Extract Python classes, functions, and imports."""
        # Query for class definitions
        class_query = "(class_definition name: (identifier) @class_name)"
        class_captures = self.parser.query_nodes(tree, class_query, SupportedLanguage.PYTHON)
        self.class_count += len(class_captures)
        
        # Query for function definitions
        func_query = "(function_definition name: (identifier) @func_name)"
        func_captures = self.parser.query_nodes(tree, func_query, SupportedLanguage.PYTHON)
        self.function_count += len(func_captures)
        
        # Query for imports
        import_query = "(import_statement) @import"
        import_captures = self.parser.query_nodes(tree, import_query, SupportedLanguage.PYTHON)
        
        # Extract import module names (simplified - assumes "import X" or "from X import Y")
        with open(file_path, 'rb') as f:
            source_code = f.read()
        
        for node, _ in import_captures:
            import_text = self.parser.get_node_text(node, source_code)
            if import_text.startswith('from'):
                module = import_text.split()[1].split('.')[0]
            else:
                module = import_text.split()[1].split('.')[0]
            
            # Classify as internal or external
            if module.startswith('.') or (self.repo_path / f"{module}.py").exists():
                self.internal_dependencies.add(module)
            else:
                self.external_dependencies.add(module)
    
    def _extract_javascript_structures(self, tree, file_path: Path):
        """Extract JavaScript/TypeScript classes, functions, and imports."""
        # Query for class declarations
        class_query = "(class_declaration name: (identifier) @class_name)"
        class_captures = self.parser.query_nodes(tree, class_query, SupportedLanguage.JAVASCRIPT)
        self.class_count += len(class_captures)
        
        # Query for function declarations
        func_query = "(function_declaration name: (identifier) @func_name)"
        func_captures = self.parser.query_nodes(tree, func_query, SupportedLanguage.JAVASCRIPT)
        self.function_count += len(func_captures)
        
        # Arrow functions
        arrow_query = "(arrow_function) @arrow"
        arrow_captures = self.parser.query_nodes(tree, arrow_query, SupportedLanguage.JAVASCRIPT)
        self.function_count += len(arrow_captures)
    
    def _extract_csharp_structures(self, tree, file_path: Path):
        """Extract C# classes, methods, and using statements."""
        # Query for class declarations
        class_query = "(class_declaration name: (identifier) @class_name)"
        class_captures = self.parser.query_nodes(tree, class_query, SupportedLanguage.CSHARP)
        self.class_count += len(class_captures)
        
        # Query for method declarations
        method_query = "(method_declaration name: (identifier) @method_name)"
        method_captures = self.parser.query_nodes(tree, method_query, SupportedLanguage.CSHARP)
        self.function_count += len(method_captures)
    
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
            lang = self.parser.detect_language(str(file_path))
            if not lang:
                continue
            
            tree = self.parser.parse_file(str(file_path), lang)
            if not tree:
                continue
            
            # Estimate cyclomatic complexity (simplified: count control flow nodes)
            complexity = self._estimate_complexity(tree, lang)
            
            if complexity > self.HIGH_COMPLEXITY_THRESHOLD:
                self.hotspots.append(Hotspot(
                    file=str(file_path.relative_to(self.repo_path)),
                    complexity=complexity,
                    churn=0,  # Placeholder - requires Git history analysis
                    confidence=min(0.9, complexity / self.HIGH_COMPLEXITY_THRESHOLD)
                ))
    
    def _estimate_complexity(self, tree, language: SupportedLanguage) -> int:
        """Estimate cyclomatic complexity by counting control flow nodes."""
        control_flow_types = ['if_statement', 'while_statement', 'for_statement', 'try_statement', 
                              'case_statement', 'switch_statement', 'conditional_expression']
        
        complexity = 1  # Base complexity
        nodes = self.parser.traverse_tree(tree.root_node)
        
        for node_info in nodes:
            if node_info['type'] in control_flow_types:
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
        
        for dep in self.external_dependencies:
            for indicator, framework_name in framework_indicators.items():
                if indicator in dep.lower():
                    return framework_name, None  # Version detection requires package file parsing
        
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
