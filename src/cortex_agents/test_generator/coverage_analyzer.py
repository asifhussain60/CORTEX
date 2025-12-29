"""
Coverage-Driven Test Prioritization System

This module analyzes code coverage and prioritizes test generation for:
1. Untested code paths (0% coverage)
2. Partially tested code (low coverage)
3. High-risk areas (complex functions, error paths)
4. Critical business logic

Integration: Works with coverage.py to analyze Python code coverage
and generate targeted test recommendations.

Author: Asif Hussain
Date: 2025-11-21
"""

import ast
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from enum import Enum


class RiskLevel(Enum):
    """Risk level for untested code"""
    CRITICAL = "critical"  # High complexity + business logic
    HIGH = "high"          # Complex or business logic
    MEDIUM = "medium"      # Moderate complexity
    LOW = "low"            # Simple utility functions


@dataclass
class UncoveredCode:
    """Represents untested code that needs tests"""
    file_path: str
    function_name: str
    line_start: int
    line_end: int
    coverage_percent: float
    complexity_score: int
    risk_level: RiskLevel
    uncovered_lines: Set[int] = field(default_factory=set)
    reason: str = ""
    priority_score: float = 0.0
    
    def __post_init__(self):
        """Calculate priority score after initialization"""
        self.priority_score = self._calculate_priority()
    
    def _calculate_priority(self) -> float:
        """
        Calculate priority score (0-100) based on:
        - Coverage: 40% weight (0% coverage = max priority)
        - Complexity: 30% weight
        - Risk level: 30% weight
        """
        # Coverage component (inverse: lower coverage = higher priority)
        coverage_score = (100 - self.coverage_percent) * 0.4
        
        # Complexity component (higher complexity = higher priority)
        # Normalize to 0-100 scale (assume max complexity ~20)
        complexity_score = min(self.complexity_score / 20 * 100, 100) * 0.3
        
        # Risk level component
        risk_scores = {
            RiskLevel.CRITICAL: 100,
            RiskLevel.HIGH: 75,
            RiskLevel.MEDIUM: 50,
            RiskLevel.LOW: 25
        }
        risk_score = risk_scores[self.risk_level] * 0.3
        
        return coverage_score + complexity_score + risk_score


@dataclass
class CoverageReport:
    """Coverage analysis results"""
    total_lines: int
    covered_lines: int
    coverage_percent: float
    uncovered_functions: List[UncoveredCode]
    priority_recommendations: List[UncoveredCode]
    
    def get_top_priorities(self, limit: int = 10) -> List[UncoveredCode]:
        """Get top N priority items for test generation"""
        return sorted(
            self.uncovered_functions,
            key=lambda x: x.priority_score,
            reverse=True
        )[:limit]


class CoverageAnalyzer:
    """
    Analyzes code coverage and prioritizes test generation.
    
    Uses coverage.py data format and AST analysis to identify:
    - Untested code paths
    - High-complexity untested functions
    - Critical business logic without tests
    - Error handling paths without coverage
    """
    
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.coverage_data: Dict = {}
        self.complexity_cache: Dict[str, int] = {}
    
    def load_coverage_data(self, coverage_json_path: Path) -> None:
        """
        Load coverage data from coverage.py JSON report
        
        Expected format:
        {
            "files": {
                "path/to/file.py": {
                    "summary": {"covered_lines": 10, "num_statements": 20},
                    "missing_lines": [5, 6, 7],
                    "excluded_lines": []
                }
            }
        }
        """
        if coverage_json_path.exists():
            with open(coverage_json_path, 'r') as f:
                self.coverage_data = json.load(f)
    
    def analyze_file(self, file_path: Path) -> List[UncoveredCode]:
        """
        Analyze a single file for uncovered code
        
        Returns list of uncovered functions/methods with priority scores
        """
        if not file_path.exists():
            return []
        
        # Get coverage data for this file
        rel_path = str(file_path.relative_to(self.project_root))
        file_coverage = self.coverage_data.get("files", {}).get(rel_path, {})
        
        missing_lines = set(file_coverage.get("missing_lines", []))
        if not missing_lines:
            return []  # Fully covered
        
        # Parse file to find functions/methods
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=str(file_path))
        
        uncovered_items = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                uncovered = self._analyze_function(
                    node, file_path, missing_lines
                )
                if uncovered:
                    uncovered_items.append(uncovered)
        
        return uncovered_items
    
    def _analyze_function(
        self,
        func_node: ast.FunctionDef,
        file_path: Path,
        missing_lines: Set[int]
    ) -> Optional[UncoveredCode]:
        """Analyze a single function for coverage and priority"""
        
        # Get function line range
        func_start = func_node.lineno
        func_end = func_node.end_lineno or func_start
        
        # Find lines in this function that are missing coverage
        func_lines = set(range(func_start, func_end + 1))
        uncovered_lines = func_lines & missing_lines
        
        if not uncovered_lines:
            return None  # Function is fully covered
        
        # Calculate coverage percentage for this function
        coverage_percent = (
            (len(func_lines) - len(uncovered_lines)) / len(func_lines) * 100
        )
        
        # Calculate complexity
        complexity = self._calculate_complexity(func_node)
        
        # Determine risk level
        risk_level = self._determine_risk_level(
            func_node, complexity, coverage_percent
        )
        
        # Generate reason
        reason = self._generate_reason(
            func_node, coverage_percent, complexity, risk_level
        )
        
        return UncoveredCode(
            file_path=str(file_path),
            function_name=func_node.name,
            line_start=func_start,
            line_end=func_end,
            coverage_percent=coverage_percent,
            complexity_score=complexity,
            risk_level=risk_level,
            uncovered_lines=uncovered_lines,
            reason=reason
        )
    
    def _calculate_complexity(self, func_node: ast.FunctionDef) -> int:
        """
        Calculate cyclomatic complexity of a function
        
        Counts decision points:
        - if/elif statements
        - for/while loops
        - try/except blocks
        - boolean operators (and/or)
        - comprehensions
        """
        complexity = 1  # Base complexity
        
        for node in ast.walk(func_node):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
            elif isinstance(node, (ast.ListComp, ast.DictComp, ast.SetComp)):
                complexity += 1
        
        return complexity
    
    def _determine_risk_level(
        self,
        func_node: ast.FunctionDef,
        complexity: int,
        coverage_percent: float
    ) -> RiskLevel:
        """
        Determine risk level based on:
        - Complexity (high = risky)
        - Coverage (low = risky)
        - Function name patterns (validate, authenticate, calculate = critical)
        """
        # Check for critical function patterns
        critical_patterns = [
            'authenticate', 'authorize', 'validate', 'verify',
            'calculate', 'payment', 'billing', 'security'
        ]
        func_name_lower = func_node.name.lower()
        is_critical = any(pattern in func_name_lower for pattern in critical_patterns)
        
        # Check for error handling (try/except blocks)
        has_error_handling = any(
            isinstance(node, ast.Try)
            for node in ast.walk(func_node)
        )
        
        # Risk matrix
        if is_critical and (complexity >= 10 or coverage_percent < 50):
            return RiskLevel.CRITICAL
        elif complexity >= 15 or coverage_percent == 0:
            return RiskLevel.HIGH
        elif complexity >= 10 or coverage_percent < 50:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _generate_reason(
        self,
        func_node: ast.FunctionDef,
        coverage_percent: float,
        complexity: int,
        risk_level: RiskLevel
    ) -> str:
        """Generate human-readable reason for prioritization"""
        reasons = []
        
        if coverage_percent == 0:
            reasons.append("No test coverage")
        elif coverage_percent < 50:
            reasons.append(f"Low coverage ({coverage_percent:.0f}%)")
        
        if complexity >= 15:
            reasons.append(f"High complexity (score: {complexity})")
        elif complexity >= 10:
            reasons.append(f"Moderate complexity (score: {complexity})")
        
        if risk_level == RiskLevel.CRITICAL:
            reasons.append("Critical business logic")
        
        # Check for specific patterns
        func_name_lower = func_node.name.lower()
        if 'validate' in func_name_lower or 'verify' in func_name_lower:
            reasons.append("Input validation function")
        if 'authenticate' in func_name_lower or 'authorize' in func_name_lower:
            reasons.append("Security-critical function")
        
        return "; ".join(reasons) if reasons else "Untested code"
    
    def analyze_project(
        self,
        source_dirs: List[Path],
        exclude_patterns: List[str] = None
    ) -> CoverageReport:
        """
        Analyze entire project for coverage gaps
        
        Args:
            source_dirs: List of directories to analyze
            exclude_patterns: File patterns to exclude (e.g., *test*.py)
        
        Returns:
            CoverageReport with prioritized recommendations
        """
        exclude_patterns = exclude_patterns or ['*test*.py', '*__pycache__*']
        
        all_uncovered: List[UncoveredCode] = []
        total_lines = 0
        covered_lines = 0
        
        for source_dir in source_dirs:
            for py_file in source_dir.rglob('*.py'):
                # Skip excluded files
                if any(py_file.match(pattern) for pattern in exclude_patterns):
                    continue
                
                uncovered = self.analyze_file(py_file)
                all_uncovered.extend(uncovered)
                
                # Update totals from coverage data
                rel_path = str(py_file.relative_to(self.project_root))
                file_coverage = self.coverage_data.get("files", {}).get(rel_path, {})
                summary = file_coverage.get("summary", {})
                total_lines += summary.get("num_statements", 0)
                covered_lines += summary.get("covered_lines", 0)
        
        coverage_percent = (
            (covered_lines / total_lines * 100) if total_lines > 0 else 100.0
        )
        
        # Get top priorities
        priority_recommendations = sorted(
            all_uncovered,
            key=lambda x: x.priority_score,
            reverse=True
        )[:20]  # Top 20 priorities
        
        return CoverageReport(
            total_lines=total_lines,
            covered_lines=covered_lines,
            coverage_percent=coverage_percent,
            uncovered_functions=all_uncovered,
            priority_recommendations=priority_recommendations
        )
    
    def generate_test_plan(
        self,
        coverage_report: CoverageReport,
        target_coverage: float = 85.0
    ) -> Dict:
        """
        Generate actionable test plan to achieve target coverage
        
        Returns:
            {
                "current_coverage": 68.5,
                "target_coverage": 85.0,
                "gap": 16.5,
                "priority_tests": [
                    {
                        "file": "auth.py",
                        "function": "authenticate_user",
                        "priority": 95.0,
                        "reason": "Critical; No coverage; High complexity"
                    }
                ]
            }
        """
        gap = target_coverage - coverage_report.coverage_percent
        
        priority_tests = [
            {
                "file": Path(item.file_path).name,
                "function": item.function_name,
                "line_range": f"{item.line_start}-{item.line_end}",
                "priority": round(item.priority_score, 1),
                "coverage": round(item.coverage_percent, 1),
                "complexity": item.complexity_score,
                "risk": item.risk_level.value,
                "reason": item.reason,
                "uncovered_lines": sorted(list(item.uncovered_lines))
            }
            for item in coverage_report.get_top_priorities(20)
        ]
        
        return {
            "current_coverage": round(coverage_report.coverage_percent, 1),
            "target_coverage": target_coverage,
            "gap": round(gap, 1),
            "lines_to_cover": coverage_report.total_lines - coverage_report.covered_lines,
            "priority_tests": priority_tests,
            "total_untested_functions": len(coverage_report.uncovered_functions)
        }
