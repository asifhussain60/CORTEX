"""
CodeReviewOrchestrator - Tiered code review system with intelligent analysis
Integrates with DependencyCrawler for context-aware review
"""

from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Set
import time
import ast
import re

from src.code_review.dependency_crawler import DependencyCrawler, CrawlStrategy


class AnalysisDepth(Enum):
    """Analysis depth levels for code review"""
    QUICK = "quick"       # Only changed files
    STANDARD = "standard" # Changed files + direct dependencies
    DEEP = "deep"         # Changed files + dependencies + tests + indirect deps


@dataclass
class ReviewIssue:
    """Represents a code review issue"""
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    category: str  # security, performance, maintainability, style, testing
    file_path: str
    line_number: Optional[int]
    message: str
    suggestion: Optional[str]


@dataclass
class CodeReviewReport:
    """Complete code review report"""
    analysis_depth: AnalysisDepth
    total_files_analyzed: int
    total_issues: int
    issues_by_severity: Dict[str, int]
    issues: List[ReviewIssue]
    token_count: int
    execution_time_seconds: float


class CodeAnalyzer:
    """Analyzes code for various issues (security, performance, maintainability)"""
    
    # Security patterns to detect
    SECURITY_PATTERNS = [
        (r"f['\"].*\{.*\}.*['\"]", "SQL injection risk: avoid f-strings with user input in queries", "Use parameterized queries with placeholders"),
        (r"eval\(", "Security risk: eval() can execute arbitrary code", "Avoid eval(), use safe alternatives like ast.literal_eval"),
        (r"exec\(", "Security risk: exec() can execute arbitrary code", "Avoid exec(), refactor to use functions"),
        (r"pickle\.loads?\(", "Security risk: pickle can execute arbitrary code", "Use JSON or other safe serialization"),
        (r"os\.system\(", "Security risk: command injection vulnerability", "Use subprocess with list arguments"),
    ]
    
    # Performance patterns to detect
    PERFORMANCE_PATTERNS = [
        (r"\.append\(", "Performance: inefficient loop with append", "Use list comprehension: [expr for item in iterable]"),
        (r"\+\=.*['\"]", "Performance: string concatenation in loop", "Use ''.join() for string concatenation"),
    ]
    
    # Maintainability patterns to detect
    MAINTAINABILITY_PATTERNS = [
        (r"^\s*[A-Z_]+\s*=\s*\d+\s*$", "Maintainability: magic number without clear name", "Use named constant with descriptive name"),
    ]
    
    def analyze_file(self, file_path: Path) -> List[ReviewIssue]:
        """Analyze a single file for issues"""
        issues = []
        
        if not file_path.exists():
            return issues
        
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # Security analysis
            for line_num, line in enumerate(lines, 1):
                for pattern, message, suggestion in self.SECURITY_PATTERNS:
                    if re.search(pattern, line):
                        issues.append(ReviewIssue(
                            severity="CRITICAL" if "injection" in message else "HIGH",
                            category="security",
                            file_path=str(file_path),
                            line_number=line_num,
                            message=message,
                            suggestion=suggestion
                        ))
            
            # Performance analysis
            for line_num, line in enumerate(lines, 1):
                for pattern, message, suggestion in self.PERFORMANCE_PATTERNS:
                    if re.search(pattern, line):
                        issues.append(ReviewIssue(
                            severity="MEDIUM",
                            category="performance",
                            file_path=str(file_path),
                            line_number=line_num,
                            message=message,
                            suggestion=suggestion
                        ))
            
            # Maintainability analysis
            for line_num, line in enumerate(lines, 1):
                for pattern, message, suggestion in self.MAINTAINABILITY_PATTERNS:
                    if re.search(pattern, line):
                        # Skip common constants like MAX_RETRIES, MIN_VALUE, etc.
                        if not re.search(r"MAX_|MIN_|DEFAULT_", line):
                            continue
                        issues.append(ReviewIssue(
                            severity="LOW",
                            category="maintainability",
                            file_path=str(file_path),
                            line_number=line_num,
                            message=message,
                            suggestion=suggestion
                        ))
            
            # AST-based analysis for Python files
            if file_path.suffix == '.py':
                try:
                    tree = ast.parse(content)
                    ast_issues = self._analyze_ast(tree, file_path)
                    issues.extend(ast_issues)
                except SyntaxError:
                    pass  # Skip files with syntax errors
            
        except Exception as e:
            # Skip files that can't be read
            pass
        
        return issues
    
    def _analyze_ast(self, tree: ast.AST, file_path: Path) -> List[ReviewIssue]:
        """Perform AST-based analysis for deeper insights"""
        issues = []
        
        # Check for missing docstrings
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                if not ast.get_docstring(node):
                    issues.append(ReviewIssue(
                        severity="LOW",
                        category="maintainability",
                        file_path=str(file_path),
                        line_number=node.lineno,
                        message=f"Missing docstring for {node.name}",
                        suggestion="Add docstring to document purpose and parameters"
                    ))
        
        return issues


class CodeReviewOrchestrator:
    """
    Orchestrates tiered code review with intelligent dependency analysis
    
    Three analysis depths:
    - QUICK: Only changed files (fast, <5 seconds)
    - STANDARD: Changed files + direct dependencies (moderate, <30 seconds)
    - DEEP: Changed files + dependencies + tests + indirect deps (thorough, <60 seconds)
    """
    
    def __init__(self, workspace_path: Path):
        """Initialize orchestrator with workspace path"""
        self.workspace_path = Path(workspace_path)
        self.crawler = DependencyCrawler(self.workspace_path)
        self.analyzer = CodeAnalyzer()
    
    def review_pr(
        self,
        changed_files: List[str],
        depth: AnalysisDepth = AnalysisDepth.STANDARD
    ) -> CodeReviewReport:
        """
        Review PR changes with specified depth
        
        Args:
            changed_files: List of file paths that changed in PR
            depth: Analysis depth (QUICK, STANDARD, or DEEP)
        
        Returns:
            CodeReviewReport with findings
        """
        start_time = time.time()
        
        # Handle empty input
        if not changed_files:
            return CodeReviewReport(
                analysis_depth=depth,
                total_files_analyzed=0,
                total_issues=0,
                issues_by_severity={},
                issues=[],
                token_count=0,
                execution_time_seconds=time.time() - start_time
            )
        
        # Map depth to crawl strategy
        strategy_map = {
            AnalysisDepth.QUICK: CrawlStrategy.LEVEL_1,
            AnalysisDepth.STANDARD: CrawlStrategy.LEVEL_2,
            AnalysisDepth.DEEP: CrawlStrategy.LEVEL_3
        }
        strategy = strategy_map[depth]
        
        # Build dependency graph
        dep_graph = self.crawler.build_dependency_graph(changed_files, strategy)
        
        # Collect all files to analyze
        files_to_analyze: Set[str] = set()
        
        if depth == AnalysisDepth.QUICK:
            # Only changed files
            files_to_analyze.update(dep_graph.changed_files)
        elif depth == AnalysisDepth.STANDARD:
            # Changed files + direct dependencies
            files_to_analyze.update(dep_graph.changed_files)
            files_to_analyze.update(dep_graph.direct_imports)
        else:  # DEEP
            # All files in dependency graph
            files_to_analyze.update(dep_graph.changed_files)
            files_to_analyze.update(dep_graph.direct_imports)
            files_to_analyze.update(dep_graph.test_files)
            files_to_analyze.update(dep_graph.indirect_deps)
        
        # Filter out nonexistent files
        files_to_analyze = {f for f in files_to_analyze if Path(f).exists()}
        
        # Analyze all files
        all_issues: List[ReviewIssue] = []
        for file_path in files_to_analyze:
            issues = self.analyzer.analyze_file(Path(file_path))
            all_issues.extend(issues)
        
        # Calculate severity distribution
        issues_by_severity = {}
        for issue in all_issues:
            issues_by_severity[issue.severity] = issues_by_severity.get(issue.severity, 0) + 1
        
        # Calculate execution time
        execution_time = time.time() - start_time
        
        # Build report
        report = CodeReviewReport(
            analysis_depth=depth,
            total_files_analyzed=len(files_to_analyze),
            total_issues=len(all_issues),
            issues_by_severity=issues_by_severity,
            issues=all_issues,
            token_count=dep_graph.estimate_tokens(),
            execution_time_seconds=execution_time
        )
        
        return report
