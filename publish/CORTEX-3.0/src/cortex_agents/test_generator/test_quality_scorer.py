"""
Test Quality Scoring System

Calculates quality scores for generated tests and provides feedback for
pattern refinement.

Copyright (c) 2024-2025 Asif Hussain. All rights reserved.
"""

import ast
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class QualityMetrics:
    """Test quality metrics"""
    assertion_strength: float  # 0.0-1.0
    edge_case_coverage: float  # 0.0-1.0
    assertion_count: int
    edge_case_count: int
    test_count: int
    has_exception_tests: bool
    has_boundary_tests: bool
    overall_score: float  # 0.0-1.0


@dataclass
class PatternFeedback:
    """Feedback for pattern refinement"""
    pattern_id: int
    effectiveness: float  # 0.0-1.0 (how well pattern performed)
    issues: List[str]  # Problems detected
    suggestions: List[str]  # Improvement suggestions
    should_promote: bool  # Increase confidence
    should_demote: bool  # Decrease confidence


class TestQualityScorer:
    """
    Scores test quality and provides feedback for pattern learning.
    
    Simplified mutation testing alternative that focuses on:
    - Assertion strength (specific vs generic)
    - Edge case coverage
    - Exception handling
    - Boundary testing
    """
    
    def __init__(self):
        """Initialize quality scorer"""
        self.weak_assertions = {
            'assert result',
            'assert not result',
            'assert True',
            'assert False'
        }
        
        self.strong_assertion_patterns = {
            'assertEqual', 'assertEquals', '==',
            'assertIn', 'in',
            'assertRaises', 'raises',
            'assertGreater', 'assertLess', '>', '<',
            'isinstance'
        }
    
    def score_test_code(self, test_code: str) -> QualityMetrics:
        """
        Score generated test code quality.
        
        Args:
            test_code: Generated test code
            
        Returns:
            Quality metrics
        """
        try:
            tree = ast.parse(test_code)
        except SyntaxError:
            return QualityMetrics(
                assertion_strength=0.0,
                edge_case_coverage=0.0,
                assertion_count=0,
                edge_case_count=0,
                test_count=0,
                has_exception_tests=False,
                has_boundary_tests=False,
                overall_score=0.0
            )
        
        # Extract test functions
        test_functions = [
            node for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_')
        ]
        
        if not test_functions:
            return QualityMetrics(
                assertion_strength=0.0,
                edge_case_coverage=0.0,
                assertion_count=0,
                edge_case_count=0,
                test_count=0,
                has_exception_tests=False,
                has_boundary_tests=False,
                overall_score=0.0
            )
        
        # Analyze assertions
        total_assertions = 0
        strong_assertions = 0
        
        for func in test_functions:
            for node in ast.walk(func):
                if isinstance(node, ast.Assert):
                    total_assertions += 1
                    if self._is_strong_assertion(node):
                        strong_assertions += 1
        
        assertion_strength = strong_assertions / total_assertions if total_assertions > 0 else 0.0
        
        # Analyze edge cases
        edge_case_indicators = self._count_edge_case_tests(test_functions)
        edge_case_coverage = min(1.0, edge_case_indicators / (len(test_functions) * 3))  # Expect ~3 edge cases per function
        
        # Check for exception and boundary tests
        has_exception_tests = self._has_exception_tests(test_functions)
        has_boundary_tests = self._has_boundary_tests(test_functions)
        
        # Calculate overall score
        overall_score = (
            assertion_strength * 0.4 +
            edge_case_coverage * 0.3 +
            (1.0 if has_exception_tests else 0.0) * 0.15 +
            (1.0 if has_boundary_tests else 0.0) * 0.15
        )
        
        return QualityMetrics(
            assertion_strength=assertion_strength,
            edge_case_coverage=edge_case_coverage,
            assertion_count=total_assertions,
            edge_case_count=edge_case_indicators,
            test_count=len(test_functions),
            has_exception_tests=has_exception_tests,
            has_boundary_tests=has_boundary_tests,
            overall_score=overall_score
        )
    
    def _is_strong_assertion(self, assert_node: ast.Assert) -> bool:
        """Check if assertion is strong (specific)"""
        # Check assertion content
        code = ast.unparse(assert_node)
        
        # Weak assertions
        for weak in self.weak_assertions:
            if code.strip() == weak:
                return False
        
        # Strong assertion patterns
        for strong in self.strong_assertion_patterns:
            if strong in code:
                return True
        
        # Generic check: has comparison operators
        if any(op in code for op in ['==', '!=', '>', '<', '>=', '<=', 'in', 'isinstance']):
            return True
        
        return False
    
    def _count_edge_case_tests(self, test_functions: List[ast.FunctionDef]) -> int:
        """Count tests that target edge cases"""
        edge_case_keywords = [
            'empty', 'none', 'null', 'zero', 'negative',
            'max', 'min', 'boundary', 'edge', 'invalid',
            'missing', 'large', 'overflow', 'underflow'
        ]
        
        count = 0
        for func in test_functions:
            func_name = func.name.lower()
            if any(keyword in func_name for keyword in edge_case_keywords):
                count += 1
        
        return count
    
    def _has_exception_tests(self, test_functions: List[ast.FunctionDef]) -> bool:
        """Check if tests include exception testing"""
        for func in test_functions:
            for node in ast.walk(func):
                # Check for with pytest.raises or assertRaises
                if isinstance(node, ast.With):
                    for item in node.items:
                        if isinstance(item.context_expr, ast.Call):
                            if 'raises' in ast.unparse(item.context_expr):
                                return True
        return False
    
    def _has_boundary_tests(self, test_functions: List[ast.FunctionDef]) -> bool:
        """Check if tests include boundary testing"""
        boundary_keywords = ['boundary', 'max', 'min', 'zero', 'limit']
        
        for func in test_functions:
            if any(keyword in func.name.lower() for keyword in boundary_keywords):
                return True
        
        return False
    
    def generate_pattern_feedback(
        self,
        pattern_id: int,
        test_code: str,
        quality_metrics: QualityMetrics,
        expected_quality: float = 0.7
    ) -> PatternFeedback:
        """
        Generate feedback for pattern refinement.
        
        Args:
            pattern_id: Pattern that generated the tests
            test_code: Generated test code
            quality_metrics: Measured quality
            expected_quality: Minimum acceptable quality
            
        Returns:
            Feedback for pattern improvement
        """
        effectiveness = quality_metrics.overall_score
        issues = []
        suggestions = []
        
        # Analyze issues
        if quality_metrics.assertion_strength < 0.6:
            issues.append("Weak assertions detected")
            suggestions.append("Use more specific assertions (==, isinstance, in, etc.)")
        
        if quality_metrics.edge_case_coverage < 0.5:
            issues.append("Low edge case coverage")
            suggestions.append("Add tests for empty, null, boundary, and invalid inputs")
        
        if not quality_metrics.has_exception_tests:
            issues.append("No exception testing")
            suggestions.append("Add tests with pytest.raises for error conditions")
        
        if not quality_metrics.has_boundary_tests:
            issues.append("No boundary testing")
            suggestions.append("Add tests for min/max values and limits")
        
        if quality_metrics.assertion_count < quality_metrics.test_count:
            issues.append("Tests missing assertions")
            suggestions.append("Ensure every test has at least one assertion")
        
        # Determine promotion/demotion
        should_promote = effectiveness >= expected_quality and len(issues) == 0
        should_demote = effectiveness < (expected_quality * 0.7)  # Significantly below target
        
        return PatternFeedback(
            pattern_id=pattern_id,
            effectiveness=effectiveness,
            issues=issues,
            suggestions=suggestions,
            should_promote=should_promote,
            should_demote=should_demote
        )
    
    def calculate_quality_improvement(
        self,
        baseline_metrics: QualityMetrics,
        current_metrics: QualityMetrics
    ) -> float:
        """
        Calculate quality improvement ratio.
        
        Args:
            baseline_metrics: Baseline quality
            current_metrics: Current quality
            
        Returns:
            Improvement ratio (e.g., 2.5 = 2.5x improvement)
        """
        if baseline_metrics.overall_score == 0:
            return 1.0
        
        return current_metrics.overall_score / baseline_metrics.overall_score
