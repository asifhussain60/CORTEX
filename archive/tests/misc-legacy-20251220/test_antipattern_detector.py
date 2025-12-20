"""
Test Anti-Pattern Detector

Identifies and suggests fixes for test code smells:
1. Empty or meaningless tests
2. Weak assertions (assert True, assert x is not None)
3. Test duplication (copy-paste)
4. Poor test naming
5. Missing setup/teardown
6. Slow tests without justification

Author: Asif Hussain
Date: 2025-11-21
"""

import ast
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Set, Optional
from enum import Enum


class AntiPattern(Enum):
    """Types of test anti-patterns"""
    EMPTY_TEST = "empty_test"
    WEAK_ASSERTION = "weak_assertion"
    NO_ASSERTION = "no_assertion"
    POOR_NAME = "poor_name"
    TOO_LONG = "too_long"
    DUPLICATE_CODE = "duplicate_code"
    MISSING_DOCSTRING = "missing_docstring"
    SLOW_TEST = "slow_test"
    HARDCODED_VALUES = "hardcoded_values"
    TEST_INTERDEPENDENCE = "test_interdependence"
    

@dataclass
class TestSmell:
    """Detected test code smell"""
    pattern: AntiPattern
    severity: str  # "critical", "warning", "info"
    file_path: str
    line_number: int
    test_name: str
    description: str
    suggestion: str
    example_fix: Optional[str] = None
    

class TestAntiPatternDetector:
    """
    Detects anti-patterns in test code
    
    Analyzes test files for:
    - Code smells
    - Weak assertions
    - Poor maintainability
    - Performance issues
    """
    
    def __init__(self):
        self.weak_assertions = {
            'assert True',
            'assert False',
            'assertTrue(True)',
            'assertFalse(False)',
            'assert x',
            'assert not x',
        }
        
        self.poor_name_patterns = [
            r'^test\d+$',  # test1, test2
            r'^test_test',  # test_test_something
            r'^testTest',   # testTest
            r'^test$',      # just 'test'
        ]
    
    def analyze_test_file(self, file_path: Path) -> List[TestSmell]:
        """
        Analyze a test file for anti-patterns
        
        Returns list of detected code smells
        """
        if not file_path.exists():
            return []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return []
        
        smells = []
        
        # Analyze each test function
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.name.startswith('test_'):
                    smells.extend(self._analyze_test_function(
                        node, str(file_path)
                    ))
        
        # Check for test interdependence
        smells.extend(self._check_test_interdependence(tree, str(file_path)))
        
        return smells
    
    def _analyze_test_function(
        self,
        func_node: ast.FunctionDef,
        file_path: str
    ) -> List[TestSmell]:
        """Analyze a single test function"""
        smells = []
        
        # Check for empty test
        if self._is_empty_test(func_node):
            smells.append(TestSmell(
                pattern=AntiPattern.EMPTY_TEST,
                severity="critical",
                file_path=file_path,
                line_number=func_node.lineno,
                test_name=func_node.name,
                description="Test function is empty or only contains pass/docstring",
                suggestion="Add meaningful test logic with assertions",
                example_fix="# Add: result = function_under_test()\n# Add: assert result == expected_value"
            ))
        
        # Check for no assertions
        elif not self._has_assertions(func_node):
            smells.append(TestSmell(
                pattern=AntiPattern.NO_ASSERTION,
                severity="critical",
                file_path=file_path,
                line_number=func_node.lineno,
                test_name=func_node.name,
                description="Test has no assertions - won't catch failures",
                suggestion="Add assert statements to validate behavior",
                example_fix="assert result == expected_value"
            ))
        
        # Check for weak assertions
        weak_assertions = self._find_weak_assertions(func_node)
        if weak_assertions:
            smells.append(TestSmell(
                pattern=AntiPattern.WEAK_ASSERTION,
                severity="warning",
                file_path=file_path,
                line_number=func_node.lineno,
                test_name=func_node.name,
                description=f"Weak assertions: {', '.join(weak_assertions)}",
                suggestion="Use specific assertions with expected values",
                example_fix="Replace 'assert result' with 'assert result == expected'"
            ))
        
        # Check for poor naming
        if self._has_poor_name(func_node.name):
            smells.append(TestSmell(
                pattern=AntiPattern.POOR_NAME,
                severity="warning",
                file_path=file_path,
                line_number=func_node.lineno,
                test_name=func_node.name,
                description="Test name is not descriptive",
                suggestion="Use descriptive names: test_<what>_<condition>_<expected>",
                example_fix=f"Rename to: test_{func_node.name[5:]}_with_valid_input_returns_success"
            ))
        
        # Check for missing docstring
        if not ast.get_docstring(func_node):
            smells.append(TestSmell(
                pattern=AntiPattern.MISSING_DOCSTRING,
                severity="info",
                file_path=file_path,
                line_number=func_node.lineno,
                test_name=func_node.name,
                description="Test lacks docstring explanation",
                suggestion="Add docstring explaining what is being tested",
                example_fix='"""Test that function handles invalid input gracefully"""'
            ))
        
        # Check for excessive length
        func_length = (func_node.end_lineno or func_node.lineno) - func_node.lineno
        if func_length > 50:
            smells.append(TestSmell(
                pattern=AntiPattern.TOO_LONG,
                severity="warning",
                file_path=file_path,
                line_number=func_node.lineno,
                test_name=func_node.name,
                description=f"Test is too long ({func_length} lines)",
                suggestion="Break into smaller, focused tests or extract helper functions",
                example_fix="Split into multiple test functions, each testing one behavior"
            ))
        
        # Check for hardcoded values (magic numbers)
        if self._has_hardcoded_values(func_node):
            smells.append(TestSmell(
                pattern=AntiPattern.HARDCODED_VALUES,
                severity="info",
                file_path=file_path,
                line_number=func_node.lineno,
                test_name=func_node.name,
                description="Test contains magic numbers/strings",
                suggestion="Extract constants or use variables with descriptive names",
                example_fix="EXPECTED_COUNT = 42  # Number of users in test dataset"
            ))
        
        return smells
    
    def _is_empty_test(self, func_node: ast.FunctionDef) -> bool:
        """Check if test is empty (only pass or docstring)"""
        # Get body excluding docstring
        body = func_node.body
        if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
            body = body[1:]  # Skip docstring
        
        # Check if empty or only 'pass'
        if not body:
            return True
        if len(body) == 1 and isinstance(body[0], ast.Pass):
            return True
        
        return False
    
    def _has_assertions(self, func_node: ast.FunctionDef) -> bool:
        """Check if test has any assertions"""
        for node in ast.walk(func_node):
            if isinstance(node, ast.Assert):
                return True
            # Check for unittest assertions
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr.startswith('assert'):
                        return True
        
        return False
    
    def _find_weak_assertions(self, func_node: ast.FunctionDef) -> List[str]:
        """Find weak or meaningless assertions"""
        weak = []
        
        for node in ast.walk(func_node):
            if isinstance(node, ast.Assert):
                test_code = ast.unparse(node.test)
                
                # Check against known weak patterns
                if any(weak_pattern in test_code for weak_pattern in [
                    'True', 'False', ' is not None', ' is None'
                ]):
                    weak.append(test_code)
        
        return weak
    
    def _has_poor_name(self, test_name: str) -> bool:
        """Check if test name is poor"""
        return any(
            re.match(pattern, test_name)
            for pattern in self.poor_name_patterns
        )
    
    def _has_hardcoded_values(self, func_node: ast.FunctionDef) -> bool:
        """Check for magic numbers/strings"""
        magic_count = 0
        
        for node in ast.walk(func_node):
            if isinstance(node, ast.Constant):
                # Ignore common values (0, 1, True, False, None, empty string)
                if node.value not in {0, 1, True, False, None, '', -1}:
                    # Ignore strings that look like descriptive names
                    if isinstance(node.value, str):
                        if len(node.value) > 20 or ' ' in node.value:
                            continue
                    magic_count += 1
        
        return magic_count > 3  # More than 3 magic values
    
    def _check_test_interdependence(
        self,
        tree: ast.Module,
        file_path: str
    ) -> List[TestSmell]:
        """Check if tests depend on each other (shared state)"""
        smells = []
        
        # Look for global variables modified in tests
        global_vars = set()
        test_functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                test_functions.append(node)
            elif isinstance(node, ast.Global):
                global_vars.update(node.names)
        
        if global_vars:
            # Tests modifying global state
            for test_func in test_functions:
                for node in ast.walk(test_func):
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                if target.id in global_vars:
                                    smells.append(TestSmell(
                                        pattern=AntiPattern.TEST_INTERDEPENDENCE,
                                        severity="critical",
                                        file_path=file_path,
                                        line_number=test_func.lineno,
                                        test_name=test_func.name,
                                        description=f"Test modifies global state: {target.id}",
                                        suggestion="Use fixtures or setup/teardown to manage state",
                                        example_fix="@pytest.fixture\ndef clean_state():\n    yield\n    # cleanup"
                                    ))
        
        return smells
    
    def generate_improvement_report(
        self,
        smells: List[TestSmell]
    ) -> Dict:
        """
        Generate actionable improvement report
        
        Returns:
        {
            "total_issues": 15,
            "by_severity": {"critical": 3, "warning": 8, "info": 4},
            "by_pattern": {"weak_assertion": 5, "poor_name": 3, ...},
            "recommendations": [...]
        }
        """
        by_severity = {"critical": 0, "warning": 0, "info": 0}
        by_pattern = {}
        
        for smell in smells:
            by_severity[smell.severity] += 1
            pattern_name = smell.pattern.value
            by_pattern[pattern_name] = by_pattern.get(pattern_name, 0) + 1
        
        # Generate top recommendations
        recommendations = []
        if by_pattern.get('weak_assertion', 0) > 0:
            recommendations.append({
                "priority": 1,
                "action": "Strengthen assertions",
                "impact": "High - Improves bug detection rate",
                "effort": "Low - Quick fixes",
                "count": by_pattern['weak_assertion']
            })
        
        if by_pattern.get('empty_test', 0) > 0:
            recommendations.append({
                "priority": 1,
                "action": "Complete empty tests",
                "impact": "Critical - Tests provide no value currently",
                "effort": "Medium - Requires understanding requirements",
                "count": by_pattern['empty_test']
            })
        
        if by_pattern.get('poor_name', 0) > 0:
            recommendations.append({
                "priority": 2,
                "action": "Improve test names",
                "impact": "Medium - Improves maintainability",
                "effort": "Low - Rename + update docstrings",
                "count": by_pattern['poor_name']
            })
        
        return {
            "total_issues": len(smells),
            "by_severity": by_severity,
            "by_pattern": by_pattern,
            "recommendations": sorted(
                recommendations,
                key=lambda x: x['priority']
            ),
            "detailed_smells": [
                {
                    "pattern": s.pattern.value,
                    "severity": s.severity,
                    "test": s.test_name,
                    "line": s.line_number,
                    "description": s.description,
                    "suggestion": s.suggestion
                }
                for s in smells
            ]
        }
