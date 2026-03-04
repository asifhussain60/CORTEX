"""
MetaAuditorAgent — validates audit results (no false positives).

Authority: Phase 29 S1 | CORE-008, CORE-011, CORE-027
Purpose: Close GAP-08 (Meta-Auditor & Plan-Auditor Agents)
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class AuditValidationResult:  # CORE-035-scoped — domain-specific variant
    """Result of meta-auditor validation."""
    has_false_positives: bool
    false_positive_rules: List[str]
    approved: bool
    corrected_violations: List[Dict[str, Any]]


class MetaAuditorAgent:
    """
    Meta-auditor validates audit results to prevent false positives.

    Validation Strategy:
    1. Re-check violations against actual code
    2. Detect false positives (claimed violation but code compliant)
    3. Provide corrected audit report

    Example:
        agent = MetaAuditorAgent()
        validation = agent.validate_audit_result(audit_result)
        if validation.has_false_positives:
            corrected = agent.re_run_audit_with_fixes(audit_result)
    """

    def __init__(self) -> None:
        """Initialize meta-auditor agent."""
        self.name = "MetaAuditorAgent"
        self.false_positive_detectors = {
            "CORE-008": self._check_tdd_compliance,
            "CORE-011": self._check_type_hints,
            "CORE-028": self._check_file_naming,
        }

    def validate_audit_result(
        self,
        audit_result: Dict[str, Any],
        workspace: Path = None
    ) -> AuditValidationResult:
        """
        Validate audit result (detect false positives).

        Args:
            audit_result: Audit report with violations
            workspace: Workspace path for validation

        Returns:
            AuditValidationResult with false positive detection
        """
        violations = audit_result.get("violations", [])
        false_positive_rules = []
        corrected_violations = []

        for violation in violations:
            rule = violation.get("rule")
            file_path = violation.get("file")

            # Check if violation is false positive
            if rule in self.false_positive_detectors:
                detector = self.false_positive_detectors[rule]
                is_false_positive = detector(file_path, workspace)

                if is_false_positive:
                    false_positive_rules.append(rule)
                else:
                    corrected_violations.append(violation)
            else:
                corrected_violations.append(violation)

        return AuditValidationResult(
            has_false_positives=len(false_positive_rules) > 0,
            false_positive_rules=false_positive_rules,
            approved=len(false_positive_rules) == 0,
            corrected_violations=corrected_violations
        )

    def re_run_audit_with_fixes(self, audit_result: Dict[str, Any]) -> Dict[str, Any]:
        """Re-run audit with false positive fixes applied."""
        validation = self.validate_audit_result(audit_result)

        return {
            "violations": validation.corrected_violations,
            "false_positives_removed": len(validation.false_positive_rules),
            "validated": True
        }

    def _check_tdd_compliance(self, file_path: str, workspace: Path = None) -> bool:
        """Check if CORE-008 violation is a false positive.

        A violation is a false positive when a corresponding test file exists
        for the production file being reported.

        Args:
            file_path: Production file path claimed to lack tests.
            workspace: Repository root (resolved from CWD if None).

        Returns:
            True if the violation is a false positive (test file found),
            False if the violation is genuine (no test file exists).
        """
        # If the reported file is itself a test file → always false positive
        basename = Path(file_path).name
        if basename.startswith("test_") or basename.endswith("_test.py"):
            return True

        # Resolve workspace
        root = workspace if workspace else Path.cwd()

        # Derive expected test-file candidates from the production module name
        stem = Path(file_path).stem  # e.g. "intent_router_impl"
        candidates = [
            root / "tests" / f"test_{stem}.py",
            root / "tests" / "unit" / f"test_{stem}.py",
        ]
        # Also walk up the relative path hierarchy
        rel = Path(file_path)
        for part in rel.parts[:-1]:
            candidates.append(root / "tests" / "unit" / part / f"test_{stem}.py")

        for candidate in candidates:
            if candidate.exists():
                return True  # Test file found → false positive

        # No test file located → genuine CORE-008 violation
        return False

    def _check_type_hints(self, file_path: str, workspace: Path = None) -> bool:
        """Check if CORE-011 violation is a false positive via AST inspection.

        Inspects the actual source file to determine whether *all* public
        function arguments carry type annotations.  If they do, the audit
        result claiming a violation is a false positive.

        Args:
            file_path: Path to the Python file under audit.
            workspace: Repository root (resolved from CWD if None).

        Returns:
            True if the file is fully annotated (violation is false positive),
            False if at least one public function is missing annotations.
        """
        import ast as _ast

        root = workspace if workspace else Path.cwd()
        source_path = root / file_path if not Path(file_path).is_absolute() else Path(file_path)

        if not source_path.exists():
            # Cannot verify → conservatively treat as not a false positive
            return False

        try:
            tree = _ast.parse(source_path.read_text(encoding="utf-8", errors="ignore"))
        except SyntaxError:
            return False

        for node in _ast.walk(tree):
            if isinstance(node, (_ast.FunctionDef, _ast.AsyncFunctionDef)):
                if node.name.startswith("_"):
                    continue  # Private — not subject to CORE-011
                for arg in node.args.args:
                    if arg.arg == "self":
                        continue
                    if arg.annotation is None:
                        return False  # Missing annotation → genuine violation

        # Every inspected public argument is annotated → false positive
        return True

    def _check_file_naming(self, file_path: str, workspace: Path = None) -> bool:
        """Check if CORE-028 violation is false positive."""
        # Check SCREAMING_CASE (true violation)
        filename = file_path.split("/")[-1].replace(".py", "")
        # If entire filename (without extension) is uppercase → true violation
        if filename.isupper() and "_" in filename:
            return False  # True violation: SCREAMING_CASE like BAD_NAME
        return True  # False positive
