"""
Tests for AC-REM-001-07: Violation Detection Automation
Pre-commit hook violation detector tests
"""

import unittest
import tempfile
import os
from pathlib import Path
from cortex.testing.violation_detector import ViolationDetector, PreCommitViolationDetector, Violation


class TestViolationDetectorBasic(unittest.TestCase):
    """Test basic violation detection"""

    def test_detector_initialization(self):
        """Test ViolationDetector can be initialized"""
        content = "def test(): pass"
        detector = ViolationDetector("test.py", content)
        self.assertEqual(detector.file_path, "test.py")
        self.assertIsNotNone(detector.violations)

    def test_bare_except_detection(self):
        """Test detection of bare except clauses"""
        content = """
try:
    operation()
except:
    pass
"""
        detector = ViolationDetector("test.py", content)
        import ast
        tree = ast.parse(content)
        detector.visit(tree)
        
        self.assertGreater(len(detector.violations), 0)
        violation = detector.violations[0]
        self.assertIn("bare except", violation.rule_name.lower())
        self.assertEqual(violation.severity, "CRITICAL")

    def test_generic_exception_without_logging(self):
        """Test detection of generic Exception without logging"""
        content = """
try:
    operation()
except Exception as e:
    pass
"""
        detector = ViolationDetector("test.py", content)
        import ast
        tree = ast.parse(content)
        detector.visit(tree)
        
        # Should find at least one violation (generic Exception without logging)
        self.assertGreater(len(detector.violations), 0)
        violation = detector.violations[0]
        self.assertEqual(violation.severity, "HIGH")

    def test_exception_with_logging(self):
        """Test no violation when exception is logged"""
        content = """
import logging
try:
    operation()
except Exception as e:
    logging.error(f"Operation failed: {e}")
"""
        detector = ViolationDetector("test.py", content)
        import ast
        tree = ast.parse(content)
        detector.visit(tree)
        
        # Should have no generic Exception violation (logging present)
        logging_violations = [v for v in detector.violations if "generic" in v.message.lower()]
        self.assertEqual(len(logging_violations), 0)

    def test_missing_return_type_hint(self):
        """Test detection of missing return type hints"""
        content = """
def calculate(x, y):
    return x + y
"""
        detector = ViolationDetector("test.py", content)
        import ast
        tree = ast.parse(content)
        detector.visit(tree)
        
        type_hint_violations = [v for v in detector.violations if "type hint" in v.rule_name.lower()]
        self.assertGreater(len(type_hint_violations), 0)

    def test_missing_docstring(self):
        """Test detection of missing docstrings"""
        content = """
def process_data(data):
    return data
"""
        detector = ViolationDetector("test.py", content)
        import ast
        tree = ast.parse(content)
        detector.visit(tree)
        
        docstring_violations = [v for v in detector.violations if "docstring" in v.rule_name.lower()]
        self.assertGreater(len(docstring_violations), 0)

    def test_function_with_docstring(self):
        """Test no violation when function has docstring"""
        content = '''
def process_data(data) -> dict:
    """Process the input data and return result."""
    return {"result": data}
'''
        detector = ViolationDetector("test.py", content)
        import ast
        tree = ast.parse(content)
        detector.visit(tree)
        
        docstring_violations = [v for v in detector.violations if "docstring" in v.rule_name.lower()]
        self.assertEqual(len(docstring_violations), 0)


class TestPreCommitDetector(unittest.TestCase):
    """Test pre-commit detector integration"""

    def test_precommit_detector_initialization(self):
        """Test PreCommitViolationDetector initialization"""
        detector = PreCommitViolationDetector(["test.py"])
        self.assertIsNotNone(detector)
        self.assertEqual(len(detector.files_to_check), 1)

    def test_precommit_detector_with_multiple_files(self):
        """Test detector with multiple files"""
        files = ["test1.py", "test2.py", "test3.py"]
        detector = PreCommitViolationDetector(files)
        self.assertEqual(len(detector.files_to_check), 3)

    def test_precommit_detector_violation_reporting(self):
        """Test violation reporting from pre-commit detector"""
        detector = PreCommitViolationDetector([])
        detector.all_violations = {
            "test.py": [
                Violation(
                    violation_id="CORE-013-001",
                    file_path="test.py",
                    line_number=5,
                    rule_name="CORE-013: Bare except",
                    severity="CRITICAL",
                    message="Bare except clause",
                    code_snippet="except:"
                )
            ]
        }
        
        # Report with HIGH threshold should include CRITICAL
        success = detector.report_violations(severity_threshold="HIGH")
        self.assertFalse(success, "Should report violations")

    def test_precommit_detector_severity_filtering(self):
        """Test severity-based filtering in reporting"""
        detector = PreCommitViolationDetector([])
        detector.all_violations = {
            "test.py": [
                Violation(
                    violation_id="CORE-012-001",
                    file_path="test.py",
                    line_number=5,
                    rule_name="CORE-012: Missing docstring",
                    severity="LOW",
                    message="Missing docstring",
                    code_snippet="def func():"
                )
            ]
        }
        
        # Report with CRITICAL threshold should filter out LOW severity
        # (severity_levels: CRITICAL=0, HIGH=1, MEDIUM=2, LOW=3)
        # threshold CRITICAL (level 0) should not report LOW (level 3)
        success = detector.report_violations(severity_threshold="CRITICAL")
        self.assertTrue(success, "Should not report LOW severity when threshold is CRITICAL")


class TestViolationDetectorRegex(unittest.TestCase):
    """Test regex-based violation detection"""

    def test_tdd_violation_detection(self):
        """Test CORE-008 TDD violation detection"""
        content = """
def test_something():
    '''Test function without assertions'''
    result = calculate(5)
"""
        detector = ViolationDetector("test_example.py", content)
        PreCommitViolationDetector._detect_tdd_violations("test_example.py", content, detector)
        
        tdd_violations = [v for v in detector.violations if "CORE-008" in v.violation_id]
        self.assertGreater(len(tdd_violations), 0)

    def test_no_tdd_violation_with_assertions(self):
        """Test no CORE-008 violation when assertions present"""
        content = """
def test_something():
    '''Test function with assertions'''
    result = calculate(5)
    assert result == 25
"""
        detector = ViolationDetector("test_example.py", content)
        PreCommitViolationDetector._detect_tdd_violations("test_example.py", content, detector)
        
        tdd_violations = [v for v in detector.violations if "CORE-008" in v.violation_id]
        self.assertEqual(len(tdd_violations), 0)


class TestViolationObject(unittest.TestCase):
    """Test Violation data class"""

    def test_violation_creation(self):
        """Test Violation object creation"""
        violation = Violation(
            violation_id="CORE-013-001",
            file_path="test.py",
            line_number=5,
            rule_name="CORE-013: Bare except",
            severity="CRITICAL",
            message="Bare except clause"
        )
        
        self.assertEqual(violation.violation_id, "CORE-013-001")
        self.assertEqual(violation.file_path, "test.py")
        self.assertEqual(violation.line_number, 5)
        self.assertEqual(violation.severity, "CRITICAL")

    def test_violation_with_code_snippet(self):
        """Test Violation with code snippet"""
        violation = Violation(
            violation_id="CORE-013-001",
            file_path="test.py",
            line_number=5,
            rule_name="CORE-013: Bare except",
            severity="CRITICAL",
            message="Bare except clause",
            code_snippet="except: pass"
        )
        
        self.assertEqual(violation.code_snippet, "except: pass")


if __name__ == "__main__":
    unittest.main()
