"""Challenge Generation System.

AC-ID: REMEDIATION-INTENT-002
Generates challenges (potential issues, risks, edge cases) based on
holistic context analysis. Proactive problem identification.
"""

import ast
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ChallengeCategory(Enum):
    """Challenge categories."""

    BREAKING_CHANGE = "BREAKING_CHANGE"
    TEST_GAP = "TEST_GAP"
    GOVERNANCE_RISK = "GOVERNANCE_RISK"
    HISTORICAL_ISSUE = "HISTORICAL_ISSUE"
    PERFORMANCE_RISK = "PERFORMANCE_RISK"
    SECURITY_RISK = "SECURITY_RISK"


class Severity(Enum):
    """Challenge severity levels."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class Challenge:
    """A challenge/risk identified during analysis."""

    category: str
    severity: str
    description: str
    affected_scope: List[str]
    evidence: List[str]
    mitigation: str
    line_number: Optional[int] = None
    confidence: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation of challenge.
        """
        return {
            "category": self.category,
            "severity": self.severity,
            "description": self.description,
            "affected_scope": self.affected_scope,
            "evidence": self.evidence,
            "mitigation": self.mitigation,
            "line_number": self.line_number,
            "confidence": self.confidence,
        }


# Dangerous patterns that violate governance rules
DANGEROUS_PATTERNS = [
    {
        "pattern": r"\beval\s*\(",
        "description": "Use of dangerous eval() function",
        "severity": "CRITICAL",
        "mitigation": "Replace eval() with ast.literal_eval() or a safer alternative",
    },
    {
        "pattern": r"\bexec\s*\(",
        "description": "Use of dangerous exec() function",
        "severity": "CRITICAL",
        "mitigation": "Avoid exec() and use structured alternatives",
    },
    {
        "pattern": r"open\s*\([^)]+\)\s*\.\s*read\s*\(",
        "description": "File opened without context manager",
        "severity": "HIGH",
        "mitigation": "Use 'with open(...) as f:' context manager for file operations",
    },
    {
        "pattern": r"__import__\s*\(",
        "description": "Dynamic import using __import__",
        "severity": "MEDIUM",
        "mitigation": "Use importlib.import_module() instead",
    },
    {
        "pattern": r"pickle\.load",
        "description": "Unpickling data can be dangerous",
        "severity": "HIGH",
        "mitigation": "Validate pickle source or use safer serialization",
    },
]

# Performance anti-patterns
PERFORMANCE_PATTERNS = [
    {
        "pattern": r"for\s+\w+\s+in\s+\w+\s*:.*\n.*for\s+\w+\s+in\s+\w+\s*:",
        "description": "Nested loops creating potential O(n²) complexity",
        "severity": "MEDIUM",
        "mitigation": "Consider using dict lookups, sets, or optimized algorithms",
        "flags": re.DOTALL,
    },
    {
        "pattern": r"for\s+\w+\s+in\s+\w+\s*:.*\n\s*\w+\s*=\s*\w+\.\w+\(",
        "description": "Database/API call inside loop (potential N+1 query)",
        "severity": "HIGH",
        "mitigation": "Batch the operations or use eager loading",
        "flags": re.DOTALL,
    },
    {
        "pattern": r"\+\s*=\s*['\"]",
        "description": "String concatenation in loop (potential O(n²) memory)",
        "severity": "LOW",
        "mitigation": "Use ''.join() or io.StringIO for string building",
        "flags": 0,
    },
]


class ChallengeGenerator:
    """Generate challenges based on code analysis."""

    def __init__(self) -> None:
        """Initialize the challenge generator."""
        self._compile_patterns()

    def _compile_patterns(self) -> None:
        """Compile regex patterns for efficiency.

        Pre-compiles all dangerous and performance patterns for faster matching.
        """
        self._dangerous_patterns = [
            {
                **p,
                "compiled": re.compile(p["pattern"], re.MULTILINE),
            }
            for p in DANGEROUS_PATTERNS
        ]

        self._performance_patterns = [
            {
                **p,
                "compiled": re.compile(p["pattern"], p.get("flags", 0)),
            }
            for p in PERFORMANCE_PATTERNS
        ]

    def generate_all(
        self,
        source: str,
        context: Optional[Dict[str, Any]] = None,
        changes: Optional[List[Dict[str, Any]]] = None,
        historical_issues: Optional[List[Dict[str, Any]]] = None,
    ) -> List[Challenge]:
        """Generate all challenges for given source.

        Args:
            source: Python source code.
            context: Additional context (existing tests, etc.)
            changes: Proposed changes to analyze.
            historical_issues: Historical issues from tracking.

        Returns:
            List of challenges sorted by severity (descending).
        """
        challenges: List[Challenge] = []

        # Analyze governance
        challenges.extend(self.analyze_governance(source))

        # Analyze performance
        challenges.extend(self.analyze_performance(source))

        # Analyze test coverage
        if context:
            challenges.extend(self.analyze_coverage(source, context))

        # Analyze changes for breaking changes
        if changes:
            challenges.extend(self.analyze_changes(source, changes))

        # Check historical issues
        if historical_issues and context and context.get("intent"):
            challenges.extend(
                self.check_historical_issues(context["intent"], historical_issues)
            )

        # Sort by severity
        severity_order = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
        challenges.sort(
            key=lambda c: severity_order.get(c.severity, 0), reverse=True
        )

        return challenges

    def analyze_governance(self, source: str) -> List[Challenge]:
        """Analyze source for governance violations.

        Args:
            source: Python source code.

        Returns:
            List of governance challenges.
        """
        challenges: List[Challenge] = []

        # Check dangerous patterns
        for pattern_info in self._dangerous_patterns:
            matches = pattern_info["compiled"].finditer(source)
            for match in matches:
                line_no = source[: match.start()].count("\n") + 1
                challenges.append(
                    Challenge(
                        category="GOVERNANCE_RISK",
                        severity=pattern_info["severity"],
                        description=pattern_info["description"],
                        affected_scope=[f"line {line_no}"],
                        evidence=[match.group(0)[:50]],
                        mitigation=pattern_info["mitigation"],
                        line_number=line_no,
                    )
                )

        # Check for missing docstrings
        try:
            tree = ast.parse(source)
            challenges.extend(self._check_docstrings(tree, source))
        except SyntaxError:
            pass

        return challenges

    def _check_docstrings(
        self, tree: ast.AST, source: str
    ) -> List[Challenge]:
        """Check for missing docstrings.

        Args:
            tree: Parsed AST.
            source: Original source.

        Returns:
            List of docstring challenges.
        """
        challenges: List[Challenge] = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                docstring = ast.get_docstring(node)

                # Skip private methods
                if node.name.startswith("_") and not node.name.startswith("__"):
                    continue

                if not docstring:
                    challenges.append(
                        Challenge(
                            category="GOVERNANCE_RISK",
                            severity="MEDIUM",
                            description=f"Missing docstring for function '{node.name}'",
                            affected_scope=[node.name],
                            evidence=[f"Function at line {node.lineno}"],
                            mitigation=f"Add a docstring describing what '{node.name}' does",
                            line_number=node.lineno,
                        )
                    )

            elif isinstance(node, ast.ClassDef):
                docstring = ast.get_docstring(node)

                if not docstring:
                    challenges.append(
                        Challenge(
                            category="GOVERNANCE_RISK",
                            severity="MEDIUM",
                            description=f"Missing docstring for class '{node.name}'",
                            affected_scope=[node.name],
                            evidence=[f"Class at line {node.lineno}"],
                            mitigation=f"Add a docstring describing the purpose of '{node.name}'",
                            line_number=node.lineno,
                        )
                    )

        return challenges

    def analyze_performance(self, source: str) -> List[Challenge]:
        """Analyze source for performance risks.

        Args:
            source: Python source code.

        Returns:
            List of performance challenges.
        """
        challenges: List[Challenge] = []

        # Check performance patterns
        for pattern_info in self._performance_patterns:
            matches = pattern_info["compiled"].finditer(source)
            for match in matches:
                line_no = source[: match.start()].count("\n") + 1
                challenges.append(
                    Challenge(
                        category="PERFORMANCE_RISK",
                        severity=pattern_info["severity"],
                        description=pattern_info["description"],
                        affected_scope=[f"line {line_no}"],
                        evidence=[match.group(0)[:50]],
                        mitigation=pattern_info["mitigation"],
                        line_number=line_no,
                    )
                )

        return challenges

    def analyze_coverage(
        self, source: str, context: Dict[str, Any]
    ) -> List[Challenge]:
        """Analyze source for test coverage gaps.

        Args:
            source: Python source code.
            context: Context including test information.

        Returns:
            List of test coverage challenges.
        """
        challenges: List[Challenge] = []

        # Analyze functions/classes without tests
        try:
            tree = ast.parse(source)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_name = node.name
                    if not func_name.startswith("_"):
                        # Check if function has tests (simplified check)
                        if context.get("tests"):
                            test_count = len(
                                [
                                    t
                                    for t in context["tests"]
                                    if func_name in str(t)
                                ]
                            )
                            if test_count == 0:
                                challenges.append(
                                    Challenge(
                                        category="TEST_GAP",
                                        severity="MEDIUM",
                                        description=f"No tests found for function '{func_name}'",
                                        affected_scope=[func_name],
                                        evidence=[f"Function at line {node.lineno}"],
                                        mitigation=f"Add unit tests for '{func_name}'",
                                        line_number=node.lineno,
                                    )
                                )
        except SyntaxError:
            pass

        return challenges

    def analyze_changes(
        self, source: str, changes: List[Dict[str, Any]]
    ) -> List[Challenge]:
        """Analyze changes for breaking changes.

        Args:
            source: Original source code.
            changes: List of proposed changes.

        Returns:
            List of breaking change challenges.
        """
        challenges: List[Challenge] = []

        # Analyze each change
        for change in changes:
            if change.get("type") == "REMOVE":
                # Removing public APIs is a breaking change
                if change.get("name") and not change["name"].startswith("_"):
                    challenges.append(
                        Challenge(
                            category="BREAKING_CHANGE",
                            severity="HIGH",
                            description=f"Removal of public API '{change['name']}'",
                            affected_scope=[change["name"]],
                            evidence=[f"Change: {change}"],
                            mitigation="Consider deprecation instead of removal",
                            confidence=0.9,
                        )
                    )
            elif change.get("type") == "RENAME":
                # Renaming public APIs may break code
                if change.get("old") and not change["old"].startswith("_"):
                    challenges.append(
                        Challenge(
                            category="BREAKING_CHANGE",
                            severity="MEDIUM",
                            description=f"Renaming of public API '{change['old']}' to '{change['new']}'",
                            affected_scope=[change["old"]],
                            evidence=[f"Change: {change}"],
                            mitigation="Provide backward compatibility alias",
                            confidence=0.85,
                        )
                    )

        return challenges

    def check_historical_issues(
        self, intent: str, historical_issues: List[Dict[str, Any]]
    ) -> List[Challenge]:
        """Check for historical issues related to intent.

        Args:
            intent: Intent of the change (e.g., FIX, IMPLEMENT, REFACTOR).
            historical_issues: List of historical issues.

        Returns:
            List of historical issue challenges.
        """
        challenges: List[Challenge] = []

        # Match historical issues to intent
        for issue in historical_issues:
            if issue.get("issue_type") == intent or issue.get("intent") == intent:
                challenges.append(
                    Challenge(
                        category="HISTORICAL_ISSUE",
                        severity=issue.get("severity", "MEDIUM"),
                        description=issue.get("description", f"Historical {intent} issue"),
                        affected_scope=issue.get("affected_scope", ["unknown"]),
                        evidence=issue.get("evidence", []),
                        mitigation=issue.get("mitigation", "Review historical context"),
                        confidence=issue.get("confidence", 0.8),
                    )
                )

        return challenges
