"""
Code Quality Orchestrator.

Provides code review, complexity analysis, and quality scoring.
"""

import ast
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class CodeReviewReport:
    """Code review report."""
    issues: List[Dict[str, Any]] = field(default_factory=list)
    warnings: int = 0
    complexity_warnings: int = 0


@dataclass
class ComplexityReport:
    """Code complexity report."""
    functions: List[Dict[str, Any]] = field(default_factory=list)
    avg_complexity: float = 0.0


@dataclass
class QualityScorecard:
    """Quality scorecard."""
    overall_score: int = 100
    complexity_score: int = 100
    style_score: int = 100
    recommendations: List[str] = field(default_factory=list)


class CodeQualityOrchestrator:
    """Orchestrator for code quality analysis."""
    
    def __init__(self):
        self.metrics = {}
    
    def run_code_review(self, source_code: str) -> CodeReviewReport:
        """Run automated code review."""
        issues = []
        complexity_warnings = 0
        
        try:
            tree = ast.parse(source_code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    complexity = self._calculate_complexity(node)
                    if complexity > 3:  # Lower threshold to catch nested conditions
                        issues.append({
                            'function': node.name,
                            'issue': 'High complexity',
                            'complexity': complexity
                        })
                        complexity_warnings += 1
        except SyntaxError:
            issues.append({'issue': 'Syntax error in code'})
        
        return CodeReviewReport(
            issues=issues,
            warnings=len(issues),
            complexity_warnings=complexity_warnings
        )
    
    def analyze_complexity(self, source_code: str) -> ComplexityReport:
        """Analyze code complexity."""
        functions = []
        
        try:
            tree = ast.parse(source_code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    complexity = self._calculate_complexity(node)
                    functions.append({
                        'name': node.name,
                        'complexity': complexity,
                        'lines': node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0
                    })
        except SyntaxError:
            pass
        
        avg_complexity = sum(f['complexity'] for f in functions) / len(functions) if functions else 0
        
        return ComplexityReport(
            functions=functions,
            avg_complexity=avg_complexity
        )
    
    def generate_scorecard(self, source_code: str) -> QualityScorecard:
        """Generate quality scorecard."""
        complexity_report = self.analyze_complexity(source_code)
        review_report = self.run_code_review(source_code)
        
        complexity_score = max(0, 100 - int(complexity_report.avg_complexity * 10))
        style_score = max(0, 100 - review_report.warnings * 5)
        overall_score = (complexity_score + style_score) // 2
        
        recommendations = []
        if complexity_score < 70:
            recommendations.append("Reduce function complexity")
        if style_score < 70:
            recommendations.append("Address style issues")
        
        return QualityScorecard(
            overall_score=overall_score,
            complexity_score=complexity_score,
            style_score=style_score,
            recommendations=recommendations
        )
    
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity."""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
        return complexity
