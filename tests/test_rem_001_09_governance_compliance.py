"""
AC-REM-001-09: Core Governance Violations Remediation
Validators for CORE-008, 011, 012, 013 compliance
"""

import unittest
from typing import List, Dict
from dataclasses import dataclass


@dataclass
class ComplianceViolation:
    """Represents a governance compliance violation"""
    core_rule: str  # CORE-008, CORE-011, CORE-012, CORE-013
    file_path: str
    line_number: int
    violation_type: str
    message: str
    suggested_fix: str


class CORE008Validator:
    """CORE-008: Test-Driven Development validator"""

    @staticmethod
    def validate_tdd_pattern(file_path: str, code_content: str) -> List[ComplianceViolation]:
        """Validate TDD patterns in code"""
        violations = []
        
        # Check if test file has assertions
        if "test_" in file_path or file_path.endswith("_test.py"):
            if "assert " not in code_content and "self.assert" not in code_content:
                violations.append(ComplianceViolation(
                    core_rule="CORE-008",
                    file_path=file_path,
                    line_number=1,
                    violation_type="missing_assertions",
                    message="Test file contains no assertions",
                    suggested_fix="Add at least one assertion to verify test behavior"
                ))
        
        return violations


class CORE011Validator:
    """CORE-011: Type Hints Required validator"""

    @staticmethod
    def validate_type_hints(file_path: str, ast_tree) -> List[ComplianceViolation]:
        """Validate type hints in code"""
        violations = []
        
        # In a real implementation, this would parse AST
        # For now, we'll use a simple regex-based check
        import re
        import ast
        
        try:
            # Parse the AST
            for node in ast.walk(ast_tree):
                if isinstance(node, ast.FunctionDef):
                    # Check return type annotation
                    if node.returns is None and not node.name.startswith("_"):
                        violations.append(ComplianceViolation(
                            core_rule="CORE-011",
                            file_path=file_path,
                            line_number=node.lineno,
                            violation_type="missing_return_type",
                            message=f"Function '{node.name}' missing return type hint",
                            suggested_fix="Add return type annotation: def func() -> ReturnType:"
                        ))
                    
                    # Check parameter type annotations
                    for arg in node.args.args:
                        if arg.annotation is None and arg.arg != "self" and arg.arg != "cls":
                            violations.append(ComplianceViolation(
                                core_rule="CORE-011",
                                file_path=file_path,
                                line_number=node.lineno,
                                violation_type="missing_param_type",
                                message=f"Parameter '{arg.arg}' in function '{node.name}' missing type hint",
                                suggested_fix="Add parameter type annotation: def func(param: ParamType):"
                            ))
        except SyntaxError:
            pass
        
        return violations


class CORE012Validator:
    """CORE-012: Docstrings Required validator"""

    @staticmethod
    def validate_docstrings(file_path: str, ast_tree) -> List[ComplianceViolation]:
        """Validate docstrings in code"""
        violations = []
        
        import ast
        
        try:
            for node in ast.walk(ast_tree):
                # Check class docstrings
                if isinstance(node, ast.ClassDef):
                    docstring = ast.get_docstring(node)
                    if not docstring and not node.name.startswith("_"):
                        violations.append(ComplianceViolation(
                            core_rule="CORE-012",
                            file_path=file_path,
                            line_number=node.lineno,
                            violation_type="missing_class_docstring",
                            message=f"Class '{node.name}' missing docstring",
                            suggested_fix='Add docstring: class Foo:\n    """Class description."""'
                        ))
                
                # Check function docstrings (non-private)
                elif isinstance(node, ast.FunctionDef):
                    docstring = ast.get_docstring(node)
                    if not docstring and not node.name.startswith("_"):
                        violations.append(ComplianceViolation(
                            core_rule="CORE-012",
                            file_path=file_path,
                            line_number=node.lineno,
                            violation_type="missing_function_docstring",
                            message=f"Function '{node.name}' missing docstring",
                            suggested_fix='Add docstring: def func():\n    """Function description."""'
                        ))
        except SyntaxError:
            pass
        
        return violations


class CORE013Validator:
    """CORE-013: Specific Exception Handling validator"""

    @staticmethod
    def validate_exception_handling(file_path: str, ast_tree) -> List[ComplianceViolation]:
        """Validate exception handling patterns"""
        violations = []
        
        import ast
        
        try:
            for node in ast.walk(ast_tree):
                if isinstance(node, ast.Try):
                    for handler in node.handlers:
                        # Detect bare except
                        if handler.type is None:
                            violations.append(ComplianceViolation(
                                core_rule="CORE-013",
                                file_path=file_path,
                                line_number=handler.lineno,
                                violation_type="bare_except",
                                message="Bare except clause violates CORE-013",
                                suggested_fix="Replace 'except:' with specific exception: except SpecificError as e:"
                            ))
                        
                        # Detect generic Exception without logging
                        elif isinstance(handler.type, ast.Name) and handler.type.id == "Exception":
                            has_logging = CORE013Validator._has_logging_in_handler(handler)
                            if not has_logging:
                                violations.append(ComplianceViolation(
                                    core_rule="CORE-013",
                                    file_path=file_path,
                                    line_number=handler.lineno,
                                    violation_type="generic_exception_no_logging",
                                    message="Generic Exception handler missing logging",
                                    suggested_fix="Add logging call: logging.error('...', exc_info=True)"
                                ))
        except SyntaxError:
            pass
        
        return violations

    @staticmethod
    def _has_logging_in_handler(handler) -> bool:
        """Check if handler contains logging call"""
        import ast
        for stmt in handler.body:
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                if isinstance(stmt.value.func, ast.Attribute):
                    if stmt.value.func.attr in ("error", "warning", "info", "debug", "critical"):
                        return True
        return False


class ComplianceValidator:
    """Unified compliance validator for all CORE rules"""

    def __init__(self, file_path: str, code_content: str):
        self.file_path = file_path
        self.code_content = code_content
        self.violations: List[ComplianceViolation] = []
        self.ast_tree = None
        self._parse_ast()

    def _parse_ast(self):
        """Parse AST from code content"""
        import ast
        try:
            self.ast_tree = ast.parse(self.code_content)
        except SyntaxError:
            self.ast_tree = None

    def validate_all_core_rules(self) -> List[ComplianceViolation]:
        """Validate all CORE rules"""
        if not self.ast_tree:
            return []
        
        # Validate each CORE rule
        violations = []
        violations.extend(CORE008Validator.validate_tdd_pattern(self.file_path, self.code_content))
        violations.extend(CORE011Validator.validate_type_hints(self.file_path, self.ast_tree))
        violations.extend(CORE012Validator.validate_docstrings(self.file_path, self.ast_tree))
        violations.extend(CORE013Validator.validate_exception_handling(self.file_path, self.ast_tree))
        
        self.violations = violations
        return violations

    def get_violations_by_rule(self, core_rule: str) -> List[ComplianceViolation]:
        """Get violations for specific CORE rule"""
        return [v for v in self.violations if v.core_rule == core_rule]

    def get_critical_violations(self) -> List[ComplianceViolation]:
        """Get only critical violations (CORE-013)"""
        return [v for v in self.violations if v.core_rule == "CORE-013"]


class TestCORE008Validator(unittest.TestCase):
    """Test CORE-008 TDD validator"""

    def test_test_file_without_assertions(self):
        """Test detection of test file without assertions"""
        violations = CORE008Validator.validate_tdd_pattern(
            "test_example.py",
            "def test_something(): pass"
        )
        self.assertGreater(len(violations), 0)
        self.assertEqual(violations[0].core_rule, "CORE-008")

    def test_test_file_with_assertions(self):
        """Test no violation when assertions present"""
        violations = CORE008Validator.validate_tdd_pattern(
            "test_example.py",
            "def test_something():\n    assert True"
        )
        self.assertEqual(len(violations), 0)


class TestCORE011Validator(unittest.TestCase):
    """Test CORE-011 type hints validator"""

    def test_function_without_return_type(self):
        """Test detection of missing return type"""
        import ast
        code = "def func(x):\n    return x"
        tree = ast.parse(code)
        
        violations = CORE011Validator.validate_type_hints("test.py", tree)
        self.assertGreater(len(violations), 0)

    def test_function_with_return_type(self):
        """Test no violation with return type"""
        import ast
        code = "def func(x: int) -> int:\n    return x"
        tree = ast.parse(code)
        
        violations = CORE011Validator.validate_type_hints("test.py", tree)
        self.assertEqual(len(violations), 0)


class TestCORE012Validator(unittest.TestCase):
    """Test CORE-012 docstring validator"""

    def test_function_without_docstring(self):
        """Test detection of missing docstring"""
        import ast
        code = "def func():\n    pass"
        tree = ast.parse(code)
        
        violations = CORE012Validator.validate_docstrings("test.py", tree)
        self.assertGreater(len(violations), 0)

    def test_function_with_docstring(self):
        """Test no violation with docstring"""
        import ast
        code = 'def func():\n    """Function description."""\n    pass'
        tree = ast.parse(code)
        
        violations = CORE012Validator.validate_docstrings("test.py", tree)
        self.assertEqual(len(violations), 0)


class TestCORE013Validator(unittest.TestCase):
    """Test CORE-013 exception handling validator"""

    def test_bare_except_detection(self):
        """Test detection of bare except"""
        import ast
        code = "try:\n    pass\nexcept:\n    pass"
        tree = ast.parse(code)
        
        violations = CORE013Validator.validate_exception_handling("test.py", tree)
        self.assertGreater(len(violations), 0)
        self.assertEqual(violations[0].violation_type, "bare_except")

    def test_generic_exception_without_logging(self):
        """Test detection of generic Exception without logging"""
        import ast
        code = "try:\n    pass\nexcept Exception:\n    pass"
        tree = ast.parse(code)
        
        violations = CORE013Validator.validate_exception_handling("test.py", tree)
        self.assertGreater(len(violations), 0)


class TestComplianceValidator(unittest.TestCase):
    """Test unified compliance validator"""

    def test_validator_initialization(self):
        """Test validator initialization"""
        validator = ComplianceValidator("test.py", "def func(): pass")
        self.assertIsNotNone(validator)

    def test_validate_all_core_rules(self):
        """Test validating all CORE rules"""
        code = "try:\n    pass\nexcept:\n    pass"
        validator = ComplianceValidator("test.py", code)
        violations = validator.validate_all_core_rules()
        
        self.assertGreater(len(violations), 0)

    def test_get_violations_by_rule(self):
        """Test getting violations for specific rule"""
        code = "try:\n    pass\nexcept:\n    pass"
        validator = ComplianceValidator("test.py", code)
        validator.validate_all_core_rules()
        
        core_013_violations = validator.get_violations_by_rule("CORE-013")
        self.assertGreater(len(core_013_violations), 0)

    def test_get_critical_violations(self):
        """Test getting critical violations"""
        code = "try:\n    pass\nexcept:\n    pass"
        validator = ComplianceValidator("test.py", code)
        validator.validate_all_core_rules()
        
        critical = validator.get_critical_violations()
        self.assertGreater(len(critical), 0)


if __name__ == "__main__":
    unittest.main()
