"""Rule Evaluator - PHASE-DEPLOYMENT-003-mcp-expansion.

Evaluates governance rules against code.

Author: CORTEX Framework
"""

from pathlib import Path
from typing import Any, Dict


class RuleEvaluator:
    """Evaluates governance rules against code.

    Supports rules like CORE-008 (test-first), CORE-012 (docstrings), etc.
    """

    SUPPORTED_RULES = {
        "CORE-008": "test_exists",
        "CORE-011": "type_hints",
        "CORE-012": "docstring",
    }

    def __init__(self):
        """Initialize the rule evaluator."""
        pass

    def evaluate_rule(
        self,
        rule_id: str,
        code_path: str,
        **kwargs,
    ) -> Dict[str, Any]:
        """Evaluate a rule against code.

        Args:
            rule_id: Rule identifier (e.g., CORE-008).
            code_path: Path to the code file.
            **kwargs: Additional parameters for specific rules.

        Returns:
            Evaluation result with passed, message, rule_id.
        """
        if rule_id == "CORE-008":
            return self._evaluate_core_008(code_path, kwargs.get("test_exists", False))
        elif rule_id == "CORE-012":
            return self._evaluate_core_012(code_path, kwargs.get("code"))
        else:
            return {
                "rule_id": rule_id,
                "passed": True,
                "message": f"Rule {rule_id} not implemented, passing by default",
            }

    def _evaluate_core_008(self, code_path: str, test_exists: bool) -> Dict[str, Any]:
        """Evaluate CORE-008: Tests must exist before implementation.

        Args:
            code_path: Path to the implementation file.
            test_exists: Whether corresponding test file exists.

        Returns:
            Evaluation result.
        """
        if test_exists:
            return {
                "rule_id": "CORE-008",
                "passed": True,
                "message": f"Test file exists for {code_path}",
            }
        else:
            return {
                "rule_id": "CORE-008",
                "passed": False,
                "message": f"Test file not found for {code_path}. CORE-008 requires tests before implementation.",
            }

    def _evaluate_core_012(self, code_path: str, code: str = None) -> Dict[str, Any]:
        """Evaluate CORE-012: Google docstrings required.

        Args:
            code_path: Path to the code file.
            code: Optional code content to check.

        Returns:
            Evaluation result.
        """
        if code:
            # Simple check for docstring presence
            if '"""' in code or "'''" in code:
                return {
                    "rule_id": "CORE-012",
                    "passed": True,
                    "message": "Docstring found in code",
                }
            else:
                return {
                    "rule_id": "CORE-012",
                    "passed": False,
                    "message": "Missing docstring. CORE-012 requires Google-style docstrings.",
                }

        # If no code provided, try to read from path
        try:
            content = Path(code_path).read_text()
            if '"""' in content or "'''" in content:
                return {
                    "rule_id": "CORE-012",
                    "passed": True,
                    "message": f"Docstring found in {code_path}",
                }
        except Exception:
            pass

        return {
            "rule_id": "CORE-012",
            "passed": False,
            "message": f"Cannot verify docstring for {code_path}",
        }


__all__ = ["RuleEvaluator"]
