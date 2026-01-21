"""
AC-REM-001-07: Violation Detection Automation
Pre-commit hook for detecting CORE governance violations
"""

import ast
import re
import logging
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Violation:
    """Represents a code violation"""
    violation_id: str
    file_path: str
    line_number: int
    rule_name: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    message: str
    code_snippet: str = ""


class ViolationDetector(ast.NodeVisitor):
    """AST-based detector for CORE governance violations"""

    def __init__(self, file_path: str, file_content: str):
        self.file_path = file_path
        self.file_content = file_content
        self.lines = file_content.split('\n')
        self.violations: List[Violation] = []
        self.current_function = None

    def visit_Try(self, node):
        """Detect bare except and bare except with pass violations"""
        for handler in node.handlers:
            if handler.type is None:  # bare except:
                line_num = handler.lineno
                code_line = self.lines[line_num - 1] if line_num <= len(self.lines) else ""
                
                # Check if except body is only 'pass'
                if len(handler.body) == 1 and isinstance(handler.body[0], ast.Pass):
                    self.violations.append(Violation(
                        violation_id="CORE-013-001",
                        file_path=self.file_path,
                        line_number=line_num,
                        rule_name="CORE-013: Bare except with pass",
                        severity="CRITICAL",
                        message="Bare except clause with pass suppresses all exceptions",
                        code_snippet=code_line.strip()
                    ))
                else:
                    # Bare except without pass but no specific exception type
                    self.violations.append(Violation(
                        violation_id="CORE-013-002",
                        file_path=self.file_path,
                        line_number=line_num,
                        rule_name="CORE-013: Bare except",
                        severity="HIGH",
                        message="Bare except catches all exceptions including SystemExit, KeyboardInterrupt",
                        code_snippet=code_line.strip()
                    ))
            else:
                # Check for generic Exception handling without logging
                exception_type = self._get_exception_name(handler.type)
                if exception_type in ("Exception", "BaseException"):
                    # Check if body contains logging
                    if not self._has_logging_call(handler.body):
                        line_num = handler.lineno
                        code_line = self.lines[line_num - 1] if line_num <= len(self.lines) else ""
                        self.violations.append(Violation(
                            violation_id="CORE-013-003",
                            file_path=self.file_path,
                            line_number=line_num,
                            rule_name="CORE-013: Generic exception without logging",
                            severity="HIGH",
                            message=f"Catching {exception_type} without logging the error",
                            code_snippet=code_line.strip()
                        ))
        
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        """Detect functions without type hints and docstrings"""
        # Check for return type annotation (CORE-011)
        if node.returns is None:
            line_num = node.lineno
            code_line = self.lines[line_num - 1] if line_num <= len(self.lines) else ""
            self.violations.append(Violation(
                violation_id="CORE-011-001",
                file_path=self.file_path,
                line_number=line_num,
                rule_name="CORE-011: Missing return type hint",
                severity="MEDIUM",
                message=f"Function '{node.name}' missing return type hint",
                code_snippet=code_line.strip()
            ))
        
        # Check for docstring (CORE-012)
        docstring = ast.get_docstring(node)
        if not docstring:
            line_num = node.lineno
            code_line = self.lines[line_num - 1] if line_num <= len(self.lines) else ""
            self.violations.append(Violation(
                violation_id="CORE-012-001",
                file_path=self.file_path,
                line_number=line_num,
                rule_name="CORE-012: Missing docstring",
                severity="MEDIUM",
                message=f"Function '{node.name}' missing docstring",
                code_snippet=code_line.strip()
            ))
        
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        """Detect classes without docstrings"""
        # Check for docstring (CORE-012)
        docstring = ast.get_docstring(node)
        if not docstring:
            line_num = node.lineno
            code_line = self.lines[line_num - 1] if line_num <= len(self.lines) else ""
            self.violations.append(Violation(
                violation_id="CORE-012-002",
                file_path=self.file_path,
                line_number=line_num,
                rule_name="CORE-012: Missing class docstring",
                severity="LOW",
                message=f"Class '{node.name}' missing docstring",
                code_snippet=code_line.strip()
            ))
        
        self.generic_visit(node)

    @staticmethod
    def _get_exception_name(node) -> str:
        """Extract exception name from AST node"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Tuple):
            return "Tuple"
        return str(node)

    @staticmethod
    def _has_logging_call(body: List[ast.stmt]) -> bool:
        """Check if body contains logging call"""
        for stmt in body:
            if isinstance(stmt, ast.Expr):
                if isinstance(stmt.value, ast.Call):
                    if isinstance(stmt.value.func, ast.Attribute):
                        if stmt.value.func.attr in ("error", "warning", "info", "debug", "critical"):
                            return True
            elif isinstance(stmt, ast.Assign):
                continue
        return False


class PreCommitViolationDetector:
    """Pre-commit hook detector for all CORE violations"""

    def __init__(self, files_to_check: List[str]):
        self.files_to_check = files_to_check
        self.all_violations: Dict[str, List[Violation]] = {}

    def detect_violations(self) -> Dict[str, List[Violation]]:
        """Detect all violations in specified files"""
        for file_path in self.files_to_check:
            if not file_path.endswith('.py') or '__pycache__' in file_path:
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Parse and detect violations
                tree = ast.parse(content, filename=file_path)
                detector = ViolationDetector(file_path, content)
                detector.visit(tree)
                
                # Also detect regex-based violations (CORE-008: TDD)
                self._detect_tdd_violations(file_path, content, detector)
                
                if detector.violations:
                    self.all_violations[file_path] = detector.violations
            except SyntaxError as e:
                logger.warning(f"Syntax error in {file_path}: {e}")
            except Exception as e:
                logger.warning(f"Error analyzing {file_path}: {e}")
        
        return self.all_violations

    @staticmethod
    def _detect_tdd_violations(file_path: str, content: str, detector: ViolationDetector):
        """Detect CORE-008 violations (TDD patterns)"""
        # Check if test file has assertions
        if 'test_' in file_path or file_path.endswith('_test.py'):
            # If it's a test, check for assertions
            if 'assert ' not in content and 'self.assert' not in content:
                detector.violations.append(Violation(
                    violation_id="CORE-008-001",
                    file_path=file_path,
                    line_number=1,
                    rule_name="CORE-008: Missing assertions in test",
                    severity="CRITICAL",
                    message="Test file without any assertions",
                    code_snippet=""
                ))

    def report_violations(self, severity_threshold: str = "MEDIUM") -> bool:
        """Report violations and return False if violations found"""
        severity_levels = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        threshold_level = severity_levels.get(severity_threshold, 2)

        violations_found = False
        for file_path, violations in self.all_violations.items():
            for violation in violations:
                violation_level = severity_levels.get(violation.severity, 3)
                if violation_level <= threshold_level:
                    violations_found = True
                    logger.error(
                        f"{file_path}:{violation.line_number} [{violation.rule_name}] "
                        f"{violation.message}"
                    )
                    if violation.code_snippet:
                        logger.error(f"  > {violation.code_snippet}")

        if violations_found:
            logger.error(f"\nTotal violations found: {sum(len(v) for v in self.all_violations.values())}")
            return False
        return True


def main():
    """Main entry point for pre-commit hook"""
    import sys
    
    files = sys.argv[1:] if len(sys.argv) > 1 else []
    if not files:
        logger.info("No files to check")
        return 0
    
    detector = PreCommitViolationDetector(files)
    detector.detect_violations()
    success = detector.report_violations(severity_threshold="HIGH")
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
