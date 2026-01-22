# © 2025-2026 Asif Hussain. All rights reserved.
"""Challenge Generation System for Intent Router.

This module provides automated challenge generation to identify potential
issues in code changes, test coverage gaps, governance risks, and performance
problems before they reach production.

PHASE-07: Holistic Intent Router Intelligence
AC-ID: IR-002-02 - Challenge Generation System
"""

import ast
import re
from dataclasses import dataclass, field
from enum import Enum
from functools import total_ordering
from typing import Any, Dict, List, Optional, Set


class ChallengeCategory(str, Enum):
    """Categories of challenges that can be detected."""
    
    BREAKING_CHANGE = "BREAKING_CHANGE"
    TEST_GAP = "TEST_GAP"
    GOVERNANCE_RISK = "GOVERNANCE_RISK"
    HISTORICAL_ISSUE = "HISTORICAL_ISSUE"
    PERFORMANCE_RISK = "PERFORMANCE_RISK"


@total_ordering
class Severity:
    """Comparable severity level that acts like a string."""
    
    _ORDER = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
    
    def __init__(self, value: str) -> None:
        """Create severity instance."""
        self.value = value
    
    def __str__(self) -> str:
        """Get string representation."""
        return self.value
    
    def __repr__(self) -> str:
        """Get representation."""
        return f"Severity('{self.value}')"
    
    def __lt__(self, other: object) -> bool:
        """Compare severity levels."""
        if isinstance(other, Severity):
            return self._ORDER.get(self.value, 0) < self._ORDER.get(other.value, 0)
        elif isinstance(other, str):
            return self._ORDER.get(self.value, 0) < self._ORDER.get(other, 0)
        return NotImplemented
    
    def __eq__(self, other: object) -> bool:
        """Check equality."""
        if isinstance(other, Severity):
            return self.value == other.value
        elif isinstance(other, str):
            return self.value == other
        return False
    
    def __hash__(self) -> int:
        """Get hash."""
        return hash(self.value)


class ChallengeSeverity:
    """Severity level constants."""
    
    CRITICAL: Severity = Severity("CRITICAL")
    HIGH: Severity = Severity("HIGH")
    MEDIUM: Severity = Severity("MEDIUM")
    LOW: Severity = Severity("LOW")


@dataclass
class Challenge:
    """Represents a detected challenge requiring attention.
    
    Attributes:
        category: Type of challenge (breaking change, test gap, etc.)
        severity: How critical the challenge is
        description: Human-readable description of the issue
        mitigation: Suggested action to address the challenge
        affected_scope: List of code elements affected by this challenge
        metadata: Additional context-specific data
    """
    
    category: str
    severity: Severity
    description: str
    mitigation: str
    affected_scope: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        """Convert severity to Severity type if needed."""
        if isinstance(self.severity, str):
            self.severity = Severity(self.severity)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert challenge to dictionary format.
        
        Returns:
            Dictionary representation of the challenge
        """
        return {
            "category": self.category,
            "severity": str(self.severity),
            "description": self.description,
            "mitigation": self.mitigation,
            "affected_scope": self.affected_scope,
            "metadata": self.metadata,
        }


class ChallengeGenerator:
    """Generates automated challenges for code analysis.
    
    This class analyzes code, changes, and context to identify potential
    issues that should be reviewed before proceeding with implementation.
    
    Methods:
        analyze_changes: Detect breaking changes in code modifications
        analyze_coverage: Identify test coverage gaps
        analyze_governance: Find governance and code quality risks
        analyze_historical: Match against historical issue patterns
        analyze_performance: Detect performance anti-patterns
        generate_all: Run all analysis types and return prioritized challenges
    """
    
    def __init__(self) -> None:
        """Initialize the challenge generator."""
        self._severity_order = {
            "CRITICAL": 4,
            "HIGH": 3,
            "MEDIUM": 2,
            "LOW": 1,
        }
    
    def analyze_changes(
        self,
        code: str,
        changes: List[Dict[str, Any]],
    ) -> List[Challenge]:
        """Analyze code changes for breaking change risks.
        
        Args:
            code: Source code to analyze
            changes: List of change descriptions with type, target, and changes fields
            
        Returns:
            List of challenges related to breaking changes
        """
        challenges: List[Challenge] = []
        
        # Parse code to build call graph
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return challenges
        
        # Build function call relationships
        call_graph = self._build_call_graph(tree)
        
        for change in changes:
            target = change.get("target", "")
            change_type = change.get("type", "")
            change_details = change.get("changes", [])
            
            # Check for signature changes
            if "add_parameter" in change_details or "modify_return" in change_details:
                affected = self._find_callers(target, call_graph)
                challenges.append(Challenge(
                    category=ChallengeCategory.BREAKING_CHANGE.value,
                    severity=ChallengeSeverity.HIGH,
                    description=f"Function '{target}' signature change may break {len(affected)} caller(s)",
                    mitigation=f"Review and update all callers: {', '.join(affected[:3])}",
                    affected_scope=affected,
                ))
            
            # Check for public API changes
            if "rename_function" in change_details:
                is_public = not target.startswith("_")
                if is_public:
                    challenges.append(Challenge(
                        category=ChallengeCategory.BREAKING_CHANGE.value,
                        severity=ChallengeSeverity.CRITICAL,
                        description=f"Public API function '{target}' rename is a breaking change",
                        mitigation="Consider deprecation period or version bump (major)",
                        affected_scope=[target],
                    ))
        
        return challenges
    
    def analyze_coverage(
        self,
        code: str,
        context: Dict[str, Any],
    ) -> List[Challenge]:
        """Identify test coverage gaps in code.
        
        Args:
            code: Source code to analyze
            context: Context dict with 'existing_tests' list
            
        Returns:
            List of challenges related to test gaps
        """
        challenges: List[Challenge] = []
        existing_tests = set(context.get("existing_tests", []))
        
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return challenges
        
        # Find all functions
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(node.name)
        
        # Check each function for test coverage
        for func_name in functions:
            test_name = f"test_{func_name}"
            is_private = func_name.startswith("_")
            
            if test_name not in existing_tests:
                severity = (
                    ChallengeSeverity.MEDIUM if is_private
                    else ChallengeSeverity.HIGH
                )
                challenges.append(Challenge(
                    category=ChallengeCategory.TEST_GAP.value,
                    severity=severity,
                    description=(
                        f"Function '{func_name}' ({'private' if is_private else 'public'}) "
                        "has no corresponding test"
                    ),
                    mitigation=f"Create test: {test_name}",
                    affected_scope=[func_name],
                ))
        
        return challenges
    
    def analyze_governance(
        self,
        code: str,
    ) -> List[Challenge]:
        """Find governance and code quality risks.
        
        Args:
            code: Source code to analyze
            
        Returns:
            List of challenges related to governance violations
        """
        challenges: List[Challenge] = []
        
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return challenges
        
        # Check for missing docstrings
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not ast.get_docstring(node):
                    is_public = not node.name.startswith("_")
                    if is_public:
                        challenges.append(Challenge(
                            category=ChallengeCategory.GOVERNANCE_RISK.value,
                            severity=ChallengeSeverity.MEDIUM,
                            description=f"Public function '{node.name}' missing docstring",
                            mitigation="Add Google-style docstring with Args, Returns, Raises",
                            affected_scope=[node.name],
                        ))
        
        # Check for dangerous patterns
        code_lines = code.split("\n")
        for i, line in enumerate(code_lines, 1):
            # Detect eval() usage
            if "eval(" in line and not line.strip().startswith("#"):
                challenges.append(Challenge(
                    category=ChallengeCategory.GOVERNANCE_RISK.value,
                    severity=ChallengeSeverity.CRITICAL,
                    description=f"Dangerous eval() usage on line {i}",
                    mitigation="Replace eval() with ast.literal_eval() or safer alternative",
                    affected_scope=[f"line_{i}"],
                ))
            
            # Detect exec() usage
            if "exec(" in line and not line.strip().startswith("#"):
                challenges.append(Challenge(
                    category=ChallengeCategory.GOVERNANCE_RISK.value,
                    severity=ChallengeSeverity.CRITICAL,
                    description=f"Unsafe exec() on line {i}",
                    mitigation="Refactor to avoid dynamic code execution",
                    affected_scope=[f"line_{i}"],
                ))
            
            # Detect bare except clauses
            if re.search(r"except\s*:", line):
                challenges.append(Challenge(
                    category=ChallengeCategory.GOVERNANCE_RISK.value,
                    severity=ChallengeSeverity.HIGH,
                    description=f"Bare except clause on line {i} (CORE-013 violation)",
                    mitigation="Specify exception types explicitly",
                    affected_scope=[f"line_{i}"],
                ))
        
        return challenges
    
    def analyze_historical(
        self,
        code: str,
        context: Dict[str, Any],
    ) -> List[Challenge]:
        """Match code against historical issue patterns.
        
        Args:
            code: Source code to analyze
            context: Context dict with 'historical_issues' list
            
        Returns:
            List of challenges based on historical patterns
        """
        challenges: List[Challenge] = []
        historical_issues = context.get("historical_issues", [])
        
        for issue in historical_issues:
            pattern = issue.get("pattern", "")
            if pattern and re.search(pattern, code, re.IGNORECASE):
                is_security = "security" in issue.get("tags", [])
                severity = (
                    ChallengeSeverity.CRITICAL if is_security
                    else ChallengeSeverity.MEDIUM
                )
                
                challenges.append(Challenge(
                    category=ChallengeCategory.HISTORICAL_ISSUE.value,
                    severity=severity,
                    description=issue.get("description", "Historical pattern detected"),
                    mitigation=issue.get("resolution", "Review historical fixes"),
                    affected_scope=[],
                    metadata={"issue_id": issue.get("id")},
                ))
        
        return challenges
    
    def check_historical_issues(
        self,
        intent: Any,
        historical_issues: List[Dict[str, Any]],
    ) -> List[Challenge]:
        """Check intent against historical issues (alias for analyze_historical).
        
        Args:
            intent: Intent dict or code to analyze
            historical_issues: List of historical issue patterns
            
        Returns:
            List of challenges based on historical patterns
        """
        # If intent is a dict with file_path, match by file
        if isinstance(intent, dict):
            file_path = intent.get("scope", {}).get("file_path", "")
            challenges = []
            
            for issue in historical_issues:
                issue_file = issue.get("file", "")
                # Match if files are the same
                if issue_file and file_path and issue_file == file_path:
                    tags = issue.get("tags", [issue.get("issue_type", "").lower()])
                    is_security = "security" in tags or issue.get("issue_type") == "SECURITY"
                    severity = (
                        ChallengeSeverity.CRITICAL if is_security
                        else ChallengeSeverity.MEDIUM
                    )
                    
                    challenges.append(Challenge(
                        category=ChallengeCategory.HISTORICAL_ISSUE.value,
                        severity=severity,
                        description=issue.get("description", "Historical issue in this file"),
                        mitigation=f"Review commit {issue.get('commit', 'N/A')} from {issue.get('date', 'N/A')}",
                        affected_scope=[file_path],
                        metadata={"issue": issue},
                    ))
            
            return challenges
        else:
            # Treat as code string
            return self.analyze_historical(str(intent), {"historical_issues": historical_issues})
    
    def analyze_performance(
        self,
        code: str,
    ) -> List[Challenge]:
        """Detect performance anti-patterns in code.
        
        Args:
            code: Source code to analyze
            
        Returns:
            List of challenges related to performance risks
        """
        challenges: List[Challenge] = []
        
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return challenges
        
        # Detect nested loops (O(n²) complexity)
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                # Check if this loop contains another loop
                nested_loops = [
                    n for n in ast.walk(node)
                    if isinstance(n, ast.For) and n is not node
                ]
                if nested_loops:
                    challenges.append(Challenge(
                        category=ChallengeCategory.PERFORMANCE_RISK.value,
                        severity=ChallengeSeverity.MEDIUM,
                        description="Nested loop detected - potential O(n²) complexity",
                        mitigation="Consider using set lookups or dict-based optimization",
                        affected_scope=[],
                    ))
        
        # Detect N+1 query patterns (database call in loop)
        code_lines = code.split("\n")
        in_loop = False
        for i, line in enumerate(code_lines):
            if "for " in line and " in " in line:
                in_loop = True
            elif line.strip() and not line.strip().startswith(" "):
                in_loop = False
            
            if in_loop and any(
                pattern in line.lower()
                for pattern in ["get_connection", "execute", "query", "fetch"]
            ):
                challenges.append(Challenge(
                    category=ChallengeCategory.PERFORMANCE_RISK.value,
                    severity=ChallengeSeverity.HIGH,
                    description=f"Potential N+1 query pattern near line {i + 1}",
                    mitigation="Use batch queries or prefetch data before loop",
                    affected_scope=[f"line_{i + 1}"],
                ))
                break  # Only report first occurrence
        
        return challenges
    
    def generate_all(
        self,
        code: str,
        context: Optional[Dict[str, Any]] = None,
        changes: Optional[List[Dict[str, Any]]] = None,
    ) -> List[Challenge]:
        """Run all analysis types and return prioritized challenges.
        
        Args:
            code: Source code to analyze
            context: Optional context with test/historical data
            changes: Optional list of change descriptions
            
        Returns:
            List of all challenges, sorted by severity (highest first)
        """
        if context is None:
            context = {}
        if changes is None:
            changes = []
        
        all_challenges: List[Challenge] = []
        
        # Run all analysis types
        if changes:
            all_challenges.extend(self.analyze_changes(code, changes))
        all_challenges.extend(self.analyze_coverage(code, context))
        all_challenges.extend(self.analyze_governance(code))
        all_challenges.extend(self.analyze_historical(code, context))
        all_challenges.extend(self.analyze_performance(code))
        
        # Sort by severity (highest first)
        all_challenges.sort(
            key=lambda c: self._severity_order.get(c.severity, 0),
            reverse=True,
        )
        
        return all_challenges
    
    # Helper methods
    
    def _build_call_graph(self, tree: ast.AST) -> Dict[str, List[str]]:
        """Build a call graph from AST.
        
        Args:
            tree: Parsed AST
            
        Returns:
            Dict mapping function names to functions they call
        """
        call_graph: Dict[str, List[str]] = {}
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_name = node.name
                calls: List[str] = []
                
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        if isinstance(child.func, ast.Name):
                            calls.append(child.func.id)
                        elif isinstance(child.func, ast.Attribute):
                            calls.append(child.func.attr)
                
                call_graph[func_name] = calls
        
        return call_graph
    
    def _find_callers(
        self,
        target: str,
        call_graph: Dict[str, List[str]],
    ) -> List[str]:
        """Find all functions that call a target function.
        
        Args:
            target: Function name to search for
            call_graph: Call graph dictionary
            
        Returns:
            List of function names that call the target
        """
        callers: List[str] = []
        
        for func_name, calls in call_graph.items():
            if target in calls:
                callers.append(func_name)
        
        return callers
