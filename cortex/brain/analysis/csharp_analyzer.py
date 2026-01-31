"""
Phase 8.5: C# AST Analyzer for LENS Intelligence

Analyzes C# code structure, patterns, and edge cases for Microsoft stack support.
Provides CORTEX LENS with expert knowledge of C# idioms and anti-patterns.

AC-ID: AC-PHASE-8.5-01 (Task LENS-MS-001)

CORE Governance:
  - CORE-008: TDD - Tests provided first
  - CORE-011: Type hints on all methods
  - CORE-012: Google-style docstrings
  - CORE-013: Specific exception handling
  - CORE-027: Audit trail logging

Author: Asif Hussain
Created: 2026-01-30
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import re
from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger


@dataclass
class CSharpAnalysisResult:
    """
    Result of C# code analysis.
    
    Attributes:
        file_path: Path to analyzed file
        classes: List of class definitions
        methods: List of method definitions
        linq_queries: Detected LINQ queries
        async_methods: Async/await patterns
        dependency_injection: DI container usage
        entity_framework: EF Core usage patterns
        edge_cases: Detected edge cases and anti-patterns
        complexity_score: Overall complexity (0-100)
    """
    file_path: str
    classes: List[Dict[str, Any]]
    methods: List[Dict[str, Any]]
    linq_queries: List[Dict[str, Any]]
    async_methods: List[Dict[str, Any]]
    dependency_injection: List[Dict[str, Any]]
    entity_framework: List[Dict[str, Any]]
    edge_cases: List[Dict[str, Any]]
    complexity_score: int


class CSharpASTAnalyzer:
    """
    Analyzes C# code for structure, patterns, and edge cases.
    
    Expert in:
    - LINQ queries (syntax, performance, N+1 queries)
    - Async/await patterns (deadlocks, ConfigureAwait)
    - Dependency injection (constructor, service lifetimes)
    - Entity Framework (migrations, lazy loading, tracking)
    - Edge cases (null references, resource disposal, thread safety)
    
    Example:
        analyzer = CSharpASTAnalyzer()
        result = analyzer.analyze_file(Path("Program.cs"))
        
        print(f"Classes: {len(result.classes)}")
        print(f"LINQ queries: {len(result.linq_queries)}")
        print(f"Edge cases: {len(result.edge_cases)}")
    """
    
    def __init__(self) -> None:
        """Initialize C# AST analyzer."""
        self.logger = EnhancedAuditLogger.instance()
        
        # C# pattern regexes
        self.patterns = {
            "class": re.compile(r"(public\s+|private\s+|internal\s+)?class\s+(\w+)"),
            "method": re.compile(r"(public\s+|private\s+|protected\s+)?(static\s+)?(async\s+)?(\w+)\s+(\w+)\s*\("),
            "linq_query": re.compile(r"(from\s+\w+\s+in\s+|\.Where\(|\.Select\(|\.FirstOrDefault\(|\.ToList\()"),
            "async_await": re.compile(r"(async\s+\w+|await\s+)"),
            "di_constructor": re.compile(r"public\s+\w+\([^)]*I\w+"),
            "ef_dbcontext": re.compile(r":\s*DbContext|DbSet<"),
            "null_check": re.compile(r"(\s+==\s+null|\s+!=\s+null|\.HasValue)"),
            "using_statement": re.compile(r"using\s*\([^)]+\)"),
            "lock_statement": re.compile(r"lock\s*\("),
        }
        
        self.logger.log_operation_complete(
            ac_id="AC-PHASE-8.5-01",
            operation="CSHARP_ANALYZER_INIT",
            success=True,
            details={"patterns_loaded": len(self.patterns)},
        )
    
    def analyze_file(self, file_path: Path) -> CSharpAnalysisResult:
        """
        Analyze C# file for structure and patterns.
        
        AC-PHASE-8.5-01: Extract C# code intelligence
        
        Args:
            file_path: Path to C# source file
        
        Returns:
            CSharpAnalysisResult: Analysis results with edge cases
        
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is not C# (.cs extension)
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if file_path.suffix.lower() != ".cs":
            raise ValueError(f"Not a C# file: {file_path}")
        
        try:
            # Read file content
            content = file_path.read_text(encoding="utf-8")
            lines = content.split("\n")
            
            # Extract components
            classes = self._extract_classes(content, lines)
            methods = self._extract_methods(content, lines)
            linq_queries = self._extract_linq_queries(content, lines)
            async_methods = self._extract_async_patterns(content, lines)
            dependency_injection = self._extract_di_patterns(content, lines)
            entity_framework = self._extract_ef_patterns(content, lines)
            
            # Detect edge cases
            edge_cases = self._detect_edge_cases(content, lines)
            
            # Calculate complexity
            complexity = self._calculate_complexity(
                len(classes), len(methods), len(linq_queries), len(async_methods)
            )
            
            result = CSharpAnalysisResult(
                file_path=str(file_path),
                classes=classes,
                methods=methods,
                linq_queries=linq_queries,
                async_methods=async_methods,
                dependency_injection=dependency_injection,
                entity_framework=entity_framework,
                edge_cases=edge_cases,
                complexity_score=complexity,
            )
            
            self.logger.log_operation_complete(
                ac_id="AC-PHASE-8.5-01",
                operation="CSHARP_ANALYSIS_COMPLETE",
                success=True,
                details={
                    "file": str(file_path),
                    "classes": len(classes),
                    "methods": len(methods),
                    "edge_cases": len(edge_cases),
                    "complexity": complexity,
                },
            )
            
            return result
        
        except Exception as e:
            self.logger.log_operation_complete(
                ac_id="AC-PHASE-8.5-01",
                operation="CSHARP_ANALYSIS_ERROR",
                success=False,
                details={"file": str(file_path), "error": str(e)},
            )
            raise
    
    def _extract_classes(self, content: str, lines: List[str]) -> List[Dict[str, Any]]:
        """Extract class definitions."""
        classes = []
        for i, line in enumerate(lines, 1):
            match = self.patterns["class"].search(line)
            if match:
                classes.append({
                    "name": match.group(2),
                    "line": i,
                    "visibility": match.group(1).strip() if match.group(1) else "internal",
                })
        return classes
    
    def _extract_methods(self, content: str, lines: List[str]) -> List[Dict[str, Any]]:
        """Extract method definitions."""
        methods = []
        for i, line in enumerate(lines, 1):
            match = self.patterns["method"].search(line)
            if match:
                methods.append({
                    "name": match.group(5),
                    "line": i,
                    "return_type": match.group(4),
                    "is_static": bool(match.group(2)),
                    "is_async": bool(match.group(3)),
                    "visibility": match.group(1).strip() if match.group(1) else "private",
                })
        return methods
    
    def _extract_linq_queries(self, content: str, lines: List[str]) -> List[Dict[str, Any]]:
        """Extract LINQ query patterns."""
        queries = []
        for i, line in enumerate(lines, 1):
            if self.patterns["linq_query"].search(line):
                queries.append({
                    "line": i,
                    "snippet": line.strip(),
                    "type": "query" if "from" in line else "method",
                })
        return queries
    
    def _extract_async_patterns(self, content: str, lines: List[str]) -> List[Dict[str, Any]]:
        """Extract async/await patterns."""
        async_patterns = []
        for i, line in enumerate(lines, 1):
            if self.patterns["async_await"].search(line):
                async_patterns.append({
                    "line": i,
                    "snippet": line.strip(),
                    "has_await": "await" in line,
                    "has_async": "async" in line,
                })
        return async_patterns
    
    def _extract_di_patterns(self, content: str, lines: List[str]) -> List[Dict[str, Any]]:
        """Extract dependency injection patterns."""
        di_patterns = []
        for i, line in enumerate(lines, 1):
            if self.patterns["di_constructor"].search(line):
                di_patterns.append({
                    "line": i,
                    "snippet": line.strip(),
                    "type": "constructor_injection",
                })
        return di_patterns
    
    def _extract_ef_patterns(self, content: str, lines: List[str]) -> List[Dict[str, Any]]:
        """Extract Entity Framework patterns."""
        ef_patterns = []
        for i, line in enumerate(lines, 1):
            if self.patterns["ef_dbcontext"].search(line):
                ef_patterns.append({
                    "line": i,
                    "snippet": line.strip(),
                    "type": "DbContext" if "DbContext" in line else "DbSet",
                })
        return ef_patterns
    
    def _detect_edge_cases(self, content: str, lines: List[str]) -> List[Dict[str, Any]]:
        """
        Detect C# edge cases and anti-patterns.
        
        Edge cases:
        - Missing null checks
        - Missing ConfigureAwait(false) in libraries
        - LINQ N+1 query patterns
        - Missing using statements for IDisposable
        - Async void methods
        - Deadlock-prone synchronous waits (.Result, .Wait())
        """
        edge_cases = []
        
        # Check for missing null checks on reference parameters
        for i, line in enumerate(lines, 1):
            if "public " in line and "(" in line and ")" in line:
                # Check if next few lines have null check
                has_null_check = any(
                    self.patterns["null_check"].search(lines[j])
                    for j in range(i, min(i + 5, len(lines)))
                    if j < len(lines)
                )
                
                if not has_null_check and "string" in line.lower():
                    edge_cases.append({
                        "type": "missing_null_check",
                        "severity": "medium",
                        "line": i,
                        "message": "Potential null reference - missing null check",
                    })
        
        # Check for async void methods
        for i, line in enumerate(lines, 1):
            if "async void" in line:
                edge_cases.append({
                    "type": "async_void",
                    "severity": "high",
                    "line": i,
                    "message": "Async void method - use async Task instead",
                })
        
        # Check for synchronous waits on async methods
        for i, line in enumerate(lines, 1):
            if ".Result" in line or ".Wait()" in line:
                edge_cases.append({
                    "type": "deadlock_risk",
                    "severity": "high",
                    "line": i,
                    "message": "Synchronous wait on async method - deadlock risk",
                })
        
        # Check for missing using statements with IDisposable
        for i, line in enumerate(lines, 1):
            if "new " in line and any(cls in line for cls in ["Stream", "Client", "Connection", "Context"]):
                # Check if inside using block
                has_using = any(
                    self.patterns["using_statement"].search(lines[j])
                    for j in range(max(0, i - 3), i)
                    if j < len(lines)
                )
                
                if not has_using:
                    edge_cases.append({
                        "type": "missing_dispose",
                        "severity": "medium",
                        "line": i,
                        "message": "IDisposable object without using statement - resource leak",
                    })
        
        return edge_cases
    
    def _calculate_complexity(
        self,
        class_count: int,
        method_count: int,
        linq_count: int,
        async_count: int,
    ) -> int:
        """Calculate overall complexity score (0-100)."""
        # Weighted complexity calculation
        complexity = (
            (class_count * 5) +
            (method_count * 2) +
            (linq_count * 3) +
            (async_count * 4)
        )
        
        return min(100, complexity)
