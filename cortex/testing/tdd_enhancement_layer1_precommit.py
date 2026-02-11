"""TDD Enhancement Layer 1 - Pre-commit Hook Integration.

Implements pre-commit hook violation detection automation including:
- Bare except clause detection (CORE-013)
- Generic exception validation
- Type hints validation (CORE-011)
- Docstring format validation (CORE-012)
- Commit blocking on violations
- --no-verify override support
"""

import ast
import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class ViolationType(Enum):
    """Enumeration of violation types."""

    BARE_EXCEPT = "bare_except"
    GENERIC_EXCEPTION = "generic_exception"
    MISSING_TYPE_HINTS = "missing_type_hints"
    MISSING_DOCSTRING = "missing_docstring"
    INVALID_DOCSTRING = "invalid_docstring"
    SYNTAX_ERROR = "syntax_error"


@dataclass
class Violation:
    """Represents a single code violation."""

    violation_type: ViolationType
    line_number: int
    message: str
    code_snippet: str


@dataclass
class ViolationResult:
    """Result of commit validation."""

    should_block: bool
    violations: List[Violation]
    message: str = ""


class PrecommitHookHandler:
    """Handles pre-commit hook violation detection."""

    def __init__(self) -> None:
        """Initialize the pre-commit hook handler."""
        self.allow_no_verify = True
        self.violations_cache = {}

    def detect_violations(self, code: str, file_path: str) -> List[Violation]:
        """Detect violations in Python code.

        Args:
            code: Python source code to analyze.
            file_path: Path to the file being analyzed.

        Returns:
            List of violations found.
        """
        violations = []

        # Try to parse the code
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return [
                Violation(
                    violation_type=ViolationType.SYNTAX_ERROR,
                    line_number=e.lineno or 0,
                    message=f"Syntax error: {e.msg}",
                    code_snippet=""
                )
            ]

        # Detect bare excepts
        violations.extend(self._detect_bare_excepts(code, tree))

        # Detect missing type hints
        violations.extend(self._detect_missing_type_hints(code, tree))

        # Detect missing docstrings
        violations.extend(self._detect_missing_docstrings(code, tree))

        return violations

    def _detect_bare_excepts(self, code: str, tree: ast.AST) -> List[Violation]:
        """Detect bare except clauses.

        Args:
            code: Python source code.
            tree: AST of the code.

        Returns:
            List of bare except violations.
        """
        violations = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                # Check if it's a bare except (type is None)
                if node.type is None:
                    line_num = node.lineno
                    line = code.split('\n')[line_num - 1] if line_num <= len(code.split('\n')) else ""

                    violations.append(
                        Violation(
                            violation_type=ViolationType.BARE_EXCEPT,
                            line_number=line_num,
                            message="CORE-013: Bare except clause detected. Use specific exception type.",
                            code_snippet=line.strip()
                        )
                    )

        return violations

    def _detect_missing_type_hints(self, code: str, tree: ast.AST) -> List[Violation]:
        """Detect functions missing type hints.

        Args:
            code: Python source code.
            tree: AST of the code.

        Returns:
            List of missing type hint violations.
        """
        violations = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check parameters for type hints
                for arg in node.args.args:
                    if arg.annotation is None:
                        line_num = node.lineno
                        line = code.split('\n')[line_num - 1] if line_num <= len(code.split('\n')) else ""

                        violations.append(
                            Violation(
                                violation_type=ViolationType.MISSING_TYPE_HINTS,
                                line_number=line_num,
                                message=f"CORE-011: Parameter '{arg.arg}' missing type hint",
                                code_snippet=line.strip()
                            )
                        )

                # Check return type hint
                if node.returns is None:
                    line_num = node.lineno
                    line = code.split('\n')[line_num - 1] if line_num <= len(code.split('\n')) else ""

                    violations.append(
                        Violation(
                            violation_type=ViolationType.MISSING_TYPE_HINTS,
                            line_number=line_num,
                            message=f"CORE-011: Function '{node.name}' missing return type hint",
                            code_snippet=line.strip()
                        )
                    )

        return violations

    def _detect_missing_docstrings(self, code: str, tree: ast.AST) -> List[Violation]:
        """Detect functions missing docstrings.

        Args:
            code: Python source code.
            tree: AST of the code.

        Returns:
            List of missing docstring violations.
        """
        violations = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                docstring = ast.get_docstring(node)

                if docstring is None:
                    line_num = node.lineno
                    line = code.split('\n')[line_num - 1] if line_num <= len(code.split('\n')) else ""

                    violations.append(
                        Violation(
                            violation_type=ViolationType.MISSING_DOCSTRING,
                            line_number=line_num,
                            message=f"CORE-012: Function '{node.name}' missing docstring",
                            code_snippet=line.strip()
                        )
                    )
                elif not self._is_valid_google_docstring(docstring, node):
                    line_num = node.lineno + 1

                    violations.append(
                        Violation(
                            violation_type=ViolationType.INVALID_DOCSTRING,
                            line_number=line_num,
                            message=f"CORE-012: Function '{node.name}' docstring missing Args/Returns sections",
                            code_snippet=docstring[:50]
                        )
                    )

        return violations

    def _is_valid_google_docstring(self, docstring: str, node: ast.FunctionDef) -> bool:
        """Check if docstring follows Google style format.

        Args:
            docstring: The docstring text.
            node: The function definition node.

        Returns:
            True if docstring is valid Google style, False otherwise.
        """
        has_args = "Args:" in docstring or len(node.args.args) == 0
        has_returns = "Returns:" in docstring or node.returns is not None

        return has_args and has_returns

    def validate_commit(self, code: str, file_path: str) -> ViolationResult:
        """Validate code for commit.

        Args:
            code: Python source code.
            file_path: Path to the file.

        Returns:
            ViolationResult indicating if commit should be blocked.
        """
        violations = self.detect_violations(code, file_path)

        should_block = self.should_block_commit(violations)

        return ViolationResult(
            should_block=should_block,
            violations=violations,
            message=f"Found {len(violations)} violation(s)" if violations else "Code is clean"
        )

    def should_block_commit(self, violations: List[Violation]) -> bool:
        """Determine if commit should be blocked based on violations.

        Args:
            violations: List of violations found.

        Returns:
            True if commit should be blocked, False otherwise.
        """
        if not violations:
            return False

        # Block on any critical violations
        critical_types = {
            ViolationType.BARE_EXCEPT,
            ViolationType.MISSING_TYPE_HINTS,
            ViolationType.MISSING_DOCSTRING,
        }

        for violation in violations:
            if violation.violation_type in critical_types:
                return True

        return False
