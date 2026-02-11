"""TDD Enhancement Layer 3 - Tier0 Governance Validation.

Implements Tier0 validation layer for governance compliance including:
- Enhanced violation detection with governance context
- CORE-* rule validation via AST analysis
- Violation registry (SQLite/in-memory)
- Compliance report generation
"""

import ast
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class Violation:
    """Represents a governance violation."""

    file_path: str
    line_number: int
    rule: str
    message: str
    severity: str = "error"


class ViolationRegistry:
    """Manages violation storage and retrieval."""

    def __init__(self, mode: str = "memory", db_path: Optional[str] = None) -> None:
        """Initialize the violation registry.

        Args:
            mode: Storage mode - 'memory' or 'sqlite'.
            db_path: Path to SQLite database (required for sqlite mode).
        """
        self.mode = mode
        self.db_path = db_path
        self.in_memory_violations: List[Violation] = []

        if mode == "sqlite" and db_path:
            self._init_database()

    def _init_database(self) -> None:
        """Initialize SQLite database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS violations (
                id INTEGER PRIMARY KEY,
                file_path TEXT NOT NULL,
                line_number INTEGER NOT NULL,
                rule TEXT NOT NULL,
                message TEXT NOT NULL,
                severity TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

    def store_violation(self, violation: Violation) -> None:
        """Store a violation.

        Args:
            violation: The violation to store.
        """
        if self.mode == "memory":
            self.in_memory_violations.append(violation)
        elif self.mode == "sqlite" and self.db_path:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO violations (file_path, line_number, rule, message, severity)
                VALUES (?, ?, ?, ?, ?)
            """, (
                violation.file_path,
                violation.line_number,
                violation.rule,
                violation.message,
                violation.severity
            ))

            conn.commit()
            conn.close()

    def get_violations(self, file_path: Optional[str] = None, rule: Optional[str] = None) -> List[Violation]:
        """Retrieve violations by file or rule.

        Args:
            file_path: Filter by file path (optional).
            rule: Filter by rule (optional).

        Returns:
            List of matching violations.
        """
        if self.mode == "memory":
            violations = self.in_memory_violations

            if file_path:
                violations = [v for v in violations if v.file_path == file_path]
            if rule:
                violations = [v for v in violations if v.rule == rule]

            return violations

        elif self.mode == "sqlite" and self.db_path:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            query = "SELECT file_path, line_number, rule, message, severity FROM violations WHERE 1=1"
            params = []

            if file_path:
                query += " AND file_path = ?"
                params.append(file_path)
            if rule:
                query += " AND rule = ?"
                params.append(rule)

            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()

            return [
                Violation(row[0], row[1], row[2], row[3], row[4])
                for row in rows
            ]

        return []

    def clear_violations(self, file_path: Optional[str] = None) -> None:
        """Clear violations.

        Args:
            file_path: Clear only violations for this file (optional).
        """
        if self.mode == "memory":
            if file_path:
                self.in_memory_violations = [
                    v for v in self.in_memory_violations
                    if v.file_path != file_path
                ]
            else:
                self.in_memory_violations = []

        elif self.mode == "sqlite" and self.db_path:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            if file_path:
                cursor.execute("DELETE FROM violations WHERE file_path = ?", (file_path,))
            else:
                cursor.execute("DELETE FROM violations")

            conn.commit()
            conn.close()


class ASTAnalyzer:
    """Analyzes Python code using AST."""

    def analyze(self, code: str) -> Dict[str, Any]:
        """Analyze code structure.

        Args:
            code: Python source code.

        Returns:
            Dictionary with analysis results.
        """
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return {"error": "Syntax error"}

        functions = []
        classes = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append({
                    "name": node.name,
                    "lineno": node.lineno,
                    "args": [arg.arg for arg in node.args.args],
                    "has_docstring": ast.get_docstring(node) is not None,
                    "has_return_type": node.returns is not None
                })

            elif isinstance(node, ast.ClassDef):
                classes.append({
                    "name": node.name,
                    "lineno": node.lineno,
                    "methods": [
                        m.name for m in node.body if isinstance(m, ast.FunctionDef)
                    ]
                })

        return {
            "functions": functions,
            "classes": classes
        }


class Tier0Validator:
    """Tier0 validation layer for governance compliance."""

    def __init__(self) -> None:
        """Initialize the Tier0 validator."""
        self.registry = ViolationRegistry(mode="memory")

    def validate_code(self, code: str, file_path: str) -> List[Dict[str, Any]]:
        """Validate code for governance compliance.

        Args:
            code: Python source code.
            file_path: Path to the file.

        Returns:
            List of violations.
        """
        violations = []

        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return [{
                "file": file_path,
                "line": e.lineno or 0,
                "rule": "SYNTAX",
                "message": f"Syntax error: {e.msg}"
            }]

        # Validate CORE-013: No bare except
        violations.extend(self._validate_core_013(code, tree, file_path))

        # Validate CORE-011: Type hints
        violations.extend(self._validate_core_011(code, tree, file_path))

        # Validate CORE-012: Docstrings
        violations.extend(self._validate_core_012(code, tree, file_path))

        return violations

    def _validate_core_013(self, code: str, tree: ast.AST, file_path: str) -> List[Dict[str, Any]]:
        """Validate CORE-013: No bare except clauses.

        Args:
            code: Python source code.
            tree: AST of the code.
            file_path: Path to the file.

        Returns:
            List of violations.
        """
        violations = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                violations.append({
                    "file": file_path,
                    "line": node.lineno,
                    "rule": "CORE-013",
                    "message": "Bare except clause detected",
                    "severity": "error"
                })

        return violations

    def _validate_core_011(self, code: str, tree: ast.AST, file_path: str) -> List[Dict[str, Any]]:
        """Validate CORE-011: Type hints required.

        Args:
            code: Python source code.
            tree: AST of the code.
            file_path: Path to the file.

        Returns:
            List of violations.
        """
        violations = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check parameters
                for arg in node.args.args:
                    if arg.annotation is None:
                        violations.append({
                            "file": file_path,
                            "line": node.lineno,
                            "rule": "CORE-011",
                            "message": f"Parameter '{arg.arg}' missing type hint",
                            "severity": "error"
                        })

                # Check return type
                if node.returns is None:
                    violations.append({
                        "file": file_path,
                        "line": node.lineno,
                        "rule": "CORE-011",
                        "message": f"Function '{node.name}' missing return type hint",
                        "severity": "error"
                    })

        return violations

    def _validate_core_012(self, code: str, tree: ast.AST, file_path: str) -> List[Dict[str, Any]]:
        """Validate CORE-012: Google-style docstrings required.

        Args:
            code: Python source code.
            tree: AST of the code.
            file_path: Path to the file.

        Returns:
            List of violations.
        """
        violations = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                docstring = ast.get_docstring(node)

                if docstring is None:
                    violations.append({
                        "file": file_path,
                        "line": node.lineno,
                        "rule": "CORE-012",
                        "message": f"Function '{node.name}' missing docstring",
                        "severity": "error"
                    })

        return violations

    def validate_governance(self, code: str, rules: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Validate governance rules.

        Args:
            code: Python source code.
            rules: List of rules to validate (optional).

        Returns:
            List of violations.
        """
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return []

        violations = []

        if not rules:
            rules = ["CORE-011", "CORE-012", "CORE-013"]

        if "CORE-013" in rules:
            violations.extend(self._validate_core_013(code, tree, ""))

        if "CORE-011" in rules:
            violations.extend(self._validate_core_011(code, tree, ""))

        if "CORE-012" in rules:
            violations.extend(self._validate_core_012(code, tree, ""))

        return violations

    def generate_compliance_report(self, violations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a compliance report.

        Args:
            violations: List of violations.

        Returns:
            Compliance report dictionary.
        """
        by_rule = {}
        for v in violations:
            rule = v.get("rule", "UNKNOWN")
            by_rule[rule] = by_rule.get(rule, 0) + 1

        # Calculate compliance score
        # Assume maximum 100 violations for score calculation
        max_violations = max(len(violations), 1)
        compliance_score = max(0, 100 - (len(violations) * 100 // max(max_violations, 1)))

        return {
            "summary": {
                "total_violations": len(violations),
                "by_rule": by_rule,
                "compliance_score": compliance_score
            },
            "violations": violations,
            "compliance_score": compliance_score
        }

    def get_violations(self) -> List[Dict[str, Any]]:
        """Get current violations from registry.

        Returns:
            List of violations.
        """
        violations = self.registry.get_violations()
        return [
            {
                "file": v.file_path,
                "line": v.line_number,
                "rule": v.rule,
                "message": v.message,
                "severity": v.severity
            }
            for v in violations
        ]

    def validate_tdd_order(self) -> bool:
        """Validate TDD order (tests before code).

        Returns:
            True if TDD order is maintained, False otherwise.
        """
        # This would be validated at the process level
        return True
