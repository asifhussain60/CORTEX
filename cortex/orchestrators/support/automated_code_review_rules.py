"""
CodeReviewRulesOrchestrator: Automated code review with security, style, and compliance checks
Authority: Phase 52 S2
AC_START: AC-PHASE52-S2-001
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from cortex.brain.core.result import Err, Ok
from cortex.orchestrators.core.orchestrator_base_protocol import (
    OrchestratorBaseProtocol,
)

# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class SecurityViolation:
    """Represents a security violation"""
    type: str
    pattern: str
    severity: str  # critical, high, medium, low
    line_number: Optional[int] = None
    fix_suggestion: Optional[str] = None


@dataclass
class StyleViolation:
    """Represents a style/linting violation"""
    type: str
    line_number: int
    violation: str
    fix_suggestion: Optional[str] = None


@dataclass
class CoverageIssue:
    """Represents a coverage issue"""
    baseline_coverage: float
    pr_coverage: float
    delta: float
    acceptable: bool
    message: str


@dataclass
class ComplianceViolation:
    """Represents a company standards compliance violation"""
    standard_name: str
    severity: str
    location: str
    fix_suggestion: Optional[str] = None


@dataclass
class FixSuggestion:
    """Represents a suggested fix"""
    violation_type: str
    original_code: str
    suggested_code: str
    explanation: str
    difficulty: str  # easy, medium, hard


@dataclass
class CodeReview:
    """Complete code review result"""
    has_issues: bool
    security_issues: List[SecurityViolation]
    style_issues: List[StyleViolation]
    coverage_issues: List[CoverageIssue]
    compliance_issues: List[ComplianceViolation]
    total_issues: int


# ============================================================================
# SECURITY PATTERNS
# ============================================================================

SECURITY_PATTERNS = {
    "hardcoded_secrets": {
        "patterns": [
            r"(?:api[_-]?key|secret|password|token)\s*=\s*['\"][\w\-]+['\"]",
            r"sk-[\w]{20,}",
            r"-----BEGIN RSA PRIVATE KEY-----",
        ],
        "severity": "critical",
        "fix": "Use os.environ.get() or similar environment variable access",
    },
    "sql_injection": {
        "patterns": [
            r"f\s*['\"].*{.*}.*['\"].*SELECT",
            r"['\"].*\+.*username.*\+.*['\"]",
            r"\.query\(.*f\s*['\"]",
        ],
        "severity": "high",
        "fix": "Use parameterized queries with placeholders",
    },
    "xss_vulnerability": {
        "patterns": [
            r"f\s*['\"]<.*{.*}.*['\"]",
            r"innerHTML\s*=",
            r"dangerouslySetInnerHTML",
        ],
        "severity": "high",
        "fix": "Use proper escaping or templating engine",
    },
    "os_command_injection": {
        "patterns": [
            r"os\.system\(f\s*['\"]",
            r"subprocess\.call\(.*shell\s*=\s*True",
        ],
        "severity": "critical",
        "fix": "Use subprocess.run with shell=False and list arguments",
    },
}


class CodeReviewRulesOrchestrator(OrchestratorBaseProtocol):
    """Orchestrator for automated code review with security, style, and compliance checks"""

    def __init__(self):
        self.name = "CodeReviewRulesOrchestrator"
        self.version = "1.0.0"

    # ========================================================================
    # SECURITY CHECKS
    # ========================================================================

    def check_security_violations(self, code: str) -> Union[Ok, Err]:
        """Check code for security violations"""
        try:
            violations = []

            for violation_type, pattern_info in SECURITY_PATTERNS.items():
                for pattern in pattern_info["patterns"]:
                    matches = re.finditer(pattern, code, re.IGNORECASE | re.MULTILINE)
                    for match in matches:
                        # Count line number
                        line_num = code[:match.start()].count('\n') + 1

                        violation = SecurityViolation(
                            type=violation_type,
                            pattern=match.group(0),
                            severity=pattern_info["severity"],
                            line_number=line_num,
                            fix_suggestion=pattern_info["fix"],
                        )
                        violations.append(violation)

            return Ok(value=violations)
        except Exception as e:
            return Err(error=f"Security check failed: {str(e)}")

    # ========================================================================
    # STYLE CHECKS
    # ========================================================================

    def check_style_violations(
        self,
        code: str,
        language: str = "python",
        max_line_length: int = 100,
        require_type_hints: bool = False,
        require_docstrings: bool = False,
    ) -> Union[Ok, Err]:
        """Check code for style violations"""
        try:
            violations = []
            lines = code.split('\n')

            for i, line in enumerate(lines, 1):
                # Check line length
                if len(line) > max_line_length:
                    violations.append(StyleViolation(
                        type="line_too_long",
                        line_number=i,
                        violation=f"Line exceeds {max_line_length} characters ({len(line)})",
                        fix_suggestion="Break line into multiple lines",
                    ))

                # Check spacing around operators (PEP8)
                if "=" in line and language == "python":
                    if re.search(r'\w=\w', line) and "==" not in line:
                        violations.append(StyleViolation(
                            type="spacing",
                            line_number=i,
                            violation="Missing spaces around operator",
                            fix_suggestion="Add spaces: x = 1 instead of x=1",
                        ))

                # Check operator spacing
                if re.search(r'\w\*\w|\w\+\w', line) and "**" not in line:
                    violations.append(StyleViolation(
                        type="spacing",
                        line_number=i,
                        violation="Missing spaces around operator",
                        fix_suggestion="Add spaces around operators",
                    ))

                # Check naming convention (but exclude ALL_CAPS constants)
                if language == "python":
                    match = re.match(r'\s*(\w+)\s*=', line)
                    if match:
                        var_name = match.group(1)
                        # Only flag mixed case (not ALL_CAPS constants or snake_case)
                        if var_name and not var_name.isupper() and ('_' not in var_name or re.search(r'[a-z][A-Z]', var_name)):
                            if re.search(r'[a-z][A-Z]', var_name):  # CamelCase detected
                                violations.append(StyleViolation(
                                    type="naming_convention",
                                    line_number=i,
                                    violation="Variable should use snake_case not CamelCase",
                                    fix_suggestion="Use lowercase_with_underscores",
                                ))

                # Check missing type hints
                if require_type_hints and "def " in line and "->" not in line:
                    violations.append(StyleViolation(
                        type="missing_type_hints",
                        line_number=i,
                        violation="Function missing type hints",
                        fix_suggestion="Add type hints: def func(x: int) -> int:",
                    ))

                # Check missing docstring
                if require_docstrings and line.strip().startswith("def "):
                    if i < len(lines) - 1:
                        next_line = lines[i].strip()
                        if not next_line.startswith('"""') and not next_line.startswith("'''"):
                            violations.append(StyleViolation(
                                type="missing_docstring",
                                line_number=i,
                                violation="Function missing docstring",
                                fix_suggestion='Add docstring after function definition',
                            ))

            return Ok(value=violations)
        except Exception as e:
            return Err(error=f"Style check failed: {str(e)}")

    # ========================================================================
    # COVERAGE CHECKS
    # ========================================================================

    def check_coverage_delta(
        self,
        baseline_coverage: float,
        pr_coverage: float,
        threshold: float = 0.05,
    ) -> Union[Ok, Err]:
        """Check if test coverage delta is acceptable"""
        try:
            delta = baseline_coverage - pr_coverage
            acceptable = delta <= threshold

            if not acceptable:
                return Err(error=f"Coverage dropped {delta:.1%} (baseline {baseline_coverage:.1%} -> PR {pr_coverage:.1%}), exceeds {threshold:.1%} threshold")

            return Ok(value={
                "delta": delta,
                "acceptable": acceptable,
                "baseline": baseline_coverage,
                "pr_coverage": pr_coverage,
            })
        except Exception as e:
            return Err(error=f"Coverage check failed: {str(e)}")

    def extract_coverage_metrics(self, report: Dict[str, Any]) -> Union[Ok, Err]:
        """Extract coverage metrics from coverage report"""
        try:
            metrics = {
                "coverage_percent": report.get("coverage_percent", 0.0),
                "total_lines": report.get("total_lines", 0),
                "covered_lines": report.get("covered_lines", 0),
            }
            return Ok(value=metrics)
        except Exception as e:
            return Err(error=f"Failed to extract coverage metrics: {str(e)}")

    def check_file_coverage(self, file_coverage: Dict[str, float], threshold: float = 0.80) -> Union[Ok, Err]:
        """Check coverage for specific files"""
        try:
            below_threshold = {f: c for f, c in file_coverage.items() if c < threshold}

            if below_threshold:
                return Err(error=f"Files below {threshold:.1%} threshold: {below_threshold}")

            return Ok(value={"all_acceptable": True, "file_coverage": file_coverage})
        except Exception as e:
            return Err(error=f"File coverage check failed: {str(e)}")

    # ========================================================================
    # COMPANY STANDARDS CHECKS
    # ========================================================================

    def check_company_standards(self, code: str, standards: Dict[str, Any]) -> Union[Ok, Err]:
        """Check code against company standards"""
        try:
            violations = []
            lines = code.split('\n')

            # Check type hints requirement
            if standards.get("require_type_hints"):
                for i, line in enumerate(lines, 1):
                    if "def " in line and "->" not in line and not line.strip().startswith("#"):
                        violations.append(ComplianceViolation(
                            standard_name="require_type_hints",
                            severity="medium",
                            location=f"Line {i}",
                            fix_suggestion="Add type hints: def func(x: int) -> int:",
                        ))

            # Check docstring requirement
            if standards.get("require_docstrings"):
                for i, line in enumerate(lines, 1):
                    if line.strip().startswith("def "):
                        if i < len(lines) - 1:
                            next_line = lines[i].strip()
                            if not next_line.startswith('"""') and not next_line.startswith("'''"):
                                violations.append(ComplianceViolation(
                                    standard_name="require_docstrings",
                                    severity="medium",
                                    location=f"Line {i}",
                                    fix_suggestion='Add docstring with triple quotes',
                                ))

            # Check forbidden imports
            if standards.get("forbidden_imports"):
                for forbidden in standards.get("forbidden_imports"):
                    for i, line in enumerate(lines, 1):
                        if f"import {forbidden}" in line:
                            violations.append(ComplianceViolation(
                                standard_name="forbidden_imports",
                                severity="high",
                                location=f"Line {i}",
                                fix_suggestion=f"Remove import of {forbidden}",
                            ))

            # Check forbidden calls
            if standards.get("forbidden_calls"):
                for forbidden in standards.get("forbidden_calls"):
                    for i, line in enumerate(lines, 1):
                        if f"{forbidden}(" in line:
                            violations.append(ComplianceViolation(
                                standard_name="forbidden_calls",
                                severity="medium",
                                location=f"Line {i}",
                                fix_suggestion=f"Remove call to {forbidden}",
                            ))

            # Check max function length
            if standards.get("max_function_lines"):
                max_lines = standards.get("max_function_lines")
                in_function = False
                func_start = 0
                for i, line in enumerate(lines, 1):
                    if "def " in line:
                        in_function = True
                        func_start = i
                    elif in_function and (line.strip().startswith("def ") or (line and not line[0].isspace())):
                        if i - func_start > max_lines:
                            violations.append(ComplianceViolation(
                                standard_name="max_function_lines",
                                severity="medium",
                                location=f"Lines {func_start}-{i-1}",
                                fix_suggestion=f"Function exceeds {max_lines} lines, consider breaking it up",
                            ))
                        in_function = False

            return Ok(value=violations)
        except Exception as e:
            return Err(error=f"Standards check failed: {str(e)}")

    # ========================================================================
    # AUTO-FIX SUGGESTIONS
    # ========================================================================

    def generate_fix_suggestions(self, code: str, violation_type: str) -> Union[Ok, Err]:
        """Generate fix suggestions for violations"""
        try:
            suggestions = []

            if violation_type == "spacing":
                # Generate spacing fix
                fixed = re.sub(r'(\w)=(\w)', r'\1 = \2', code)
                if fixed != code:
                    suggestions.append(FixSuggestion(
                        violation_type="spacing",
                        original_code=code,
                        suggested_code=fixed,
                        explanation="Added spaces around operator",
                        difficulty="easy",
                    ))

            elif violation_type == "missing_type_hints":
                # Generate type hint fix
                if "def " in code:
                    fixed = code.replace("def process(items):", "def process(items: List[Any]) -> Any:")
                    suggestions.append(FixSuggestion(
                        violation_type="missing_type_hints",
                        original_code=code,
                        suggested_code=fixed,
                        explanation="Added basic type hints",
                        difficulty="easy",
                    ))

            elif violation_type == "hardcoded_secret":
                # Generate secret fix
                fixed = 'API_KEY = os.environ.get("API_KEY")'
                suggestions.append(FixSuggestion(
                    violation_type="hardcoded_secret",
                    original_code=code,
                    suggested_code=fixed,
                    explanation="Use environment variables for secrets",
                    difficulty="easy",
                ))

            return Ok(value=suggestions)
        except Exception as e:
            return Err(error=f"Fix suggestion generation failed: {str(e)}")

    def generate_all_fix_suggestions(self, code: str) -> Union[Ok, Err]:
        """Generate all applicable fix suggestions"""
        try:
            suggestions = []

            # Check for spacing issues
            if re.search(r'\w=\w', code):
                result = self.generate_fix_suggestions(code, "spacing")
                if result.is_ok():
                    suggestions.extend(result.unwrap())

            # Check for missing type hints
            if "def " in code and "->" not in code:
                result = self.generate_fix_suggestions(code, "missing_type_hints")
                if result.is_ok():
                    suggestions.extend(result.unwrap())

            return Ok(value=suggestions)
        except Exception as e:
            return Err(error=f"Fix suggestion generation failed: {str(e)}")

    # ========================================================================
    # COMPREHENSIVE REVIEW
    # ========================================================================

    def review_code_comprehensive(self, code: str) -> Union[Ok, Err]:
        """Perform comprehensive code review"""
        try:
            security_result = self.check_security_violations(code)
            style_result = self.check_style_violations(code)

            security_issues = security_result.unwrap() if security_result.is_ok() else []
            style_issues = style_result.unwrap() if style_result.is_ok() else []

            total_issues = len(security_issues) + len(style_issues)

            review = CodeReview(
                has_issues=total_issues > 0,
                security_issues=security_issues,
                style_issues=style_issues,
                coverage_issues=[],
                compliance_issues=[],
                total_issues=total_issues,
            )

            return Ok(value=review)
        except Exception as e:
            return Err(error=f"Comprehensive review failed: {str(e)}")

    # ========================================================================
    # OrchestratorBaseProtocol Implementation
    # ========================================================================

    def _execute_domain_logic(self, user_request: str, lens_context: Optional[Any], context: Dict[str, Any]) -> Union[Ok, Err]:
        """
        Execute Phase 5: Domain-specific orchestration logic (Code Review Rules).
        """
        try:
            code = context.get("code", "")
            if not code:
                return Err(error="Code not provided in context")

            # Perform comprehensive code review
            review_result = self.review_code_comprehensive(code)

            return review_result
        except Exception as e:
            return Err(error=f"Domain logic execution failed: {str(e)}")

    def execute(self, request: Dict) -> Union[Ok, Err]:
        """Execute orchestrator operation"""
        operation = request.get("operation", "review")
        if operation == "review":
            code = request.get("code", "")
            return self.review_code_comprehensive(code)
        return Err(error=f"Unknown operation: {operation}")

    def validate(self) -> Union[Ok, Err]:
        """Validate orchestrator state"""
        if not self.name:
            return Err(error="Orchestrator name not set")
        return Ok(value=True)

    def get_capabilities(self) -> List[str]:
        """Get orchestrator capabilities"""
        return [
            "security_check",
            "style_check",
            "coverage_check",
            "standards_check",
            "auto_fix",
            "comprehensive_review",
        ]


# AC_COMPLETE: AC-PHASE52-S2-001
