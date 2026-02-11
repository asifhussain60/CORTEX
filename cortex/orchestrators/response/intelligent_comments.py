"""
Intelligent code comment generation system.
Generates 5 types of comments: COMPLEXITY, SECURITY, BUSINESS, PERFORMANCE, CONTRACT.

Module: cortex.orchestrators.response.intelligent_comments
Author: Asif Hussain
Created: 2026-02-07
Version: 1.0
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set

# ============================================================================
# ENUMERATIONS
# ============================================================================


class CommentType(str, Enum):
    """Type of intelligent comment."""

    COMPLEXITY = "complexity"
    """Code complexity and structure issues"""

    SECURITY = "security"
    """Security vulnerabilities and best practices"""

    BUSINESS = "business"
    """Business logic and domain meaning"""

    PERFORMANCE = "performance"
    """Performance anti-patterns and optimizations"""

    CONTRACT = "contract"
    """API contract, preconditions, postconditions"""


class CommentSeverity(str, Enum):
    """Severity level of comment."""

    INFO = "info"
    """Informational comment"""

    WARNING = "warning"
    """Warning - should address"""

    CRITICAL = "critical"
    """Critical issue - must address"""


# ============================================================================
# DATA CLASSES
# ============================================================================


@dataclass
class CodeComment:
    """A generated code comment."""

    type: CommentType
    severity: CommentSeverity
    message: str
    line_number: Optional[int] = None
    suggestion: Optional[str] = None

    def render_inline(self) -> str:
        """Render comment as inline code comment."""
        icon_map = {
            CommentSeverity.INFO: "ℹ️",
            CommentSeverity.WARNING: "⚠️",
            CommentSeverity.CRITICAL: "🚨",
        }
        icon = icon_map.get(self.severity, "💬")

        result = f"{icon} [{self.type.value.upper()}] {self.message}"

        if self.suggestion:
            result += f"\n   → Suggestion: {self.suggestion}"

        return result


@dataclass
class CommentContext:
    """Context for comment generation."""

    code_snippet: str
    language: str = "python"
    file_path: Optional[str] = None
    function_name: Optional[str] = None
    cyclomatic_complexity: Optional[int] = None
    lines_of_code: Optional[int] = None
    has_type_hints: bool = False
    has_docstring: bool = False
    dependencies: List[str] = field(default_factory=list)


# ============================================================================
# COMMENT GENERATORS (BY TYPE)
# ============================================================================


class ComplexityCommentGenerator:
    """Generates COMPLEXITY comments."""

    @staticmethod
    def generate(context: CommentContext) -> List[CodeComment]:
        """Generate complexity comments."""
        comments = []

        # Check cyclomatic complexity
        if context.cyclomatic_complexity and context.cyclomatic_complexity > 5:
            comments.append(CodeComment(
                type=CommentType.COMPLEXITY,
                severity=CommentSeverity.WARNING if context.cyclomatic_complexity <= 10 else CommentSeverity.CRITICAL,
                message=f"Cyclomatic complexity is {context.cyclomatic_complexity} (threshold: 5)",
                suggestion="Consider breaking function into smaller, single-responsibility functions"
            ))

        # Check lines of code
        if context.lines_of_code and context.lines_of_code >= 50:
            comments.append(CodeComment(
                type=CommentType.COMPLEXITY,
                severity=CommentSeverity.WARNING,
                message=f"Function is {context.lines_of_code} lines long (threshold: 50)",
                suggestion="Extract logical sections into separate functions"
            ))

        # Check for deeply nested structures
        max_indent = ComplexityCommentGenerator._get_max_indent(context.code_snippet)
        if max_indent > 4:
            comments.append(CodeComment(
                type=CommentType.COMPLEXITY,
                severity=CommentSeverity.WARNING,
                message=f"Nesting depth is {max_indent} levels (threshold: 4)",
                suggestion="Refactor nested conditionals using early returns or helper functions"
            ))

        return comments

    @staticmethod
    def _get_max_indent(code: str) -> int:
        """Get maximum indentation level."""
        max_indent = 0
        for line in code.split('\n'):
            if line.strip():
                indent = len(line) - len(line.lstrip())
                max_indent = max(max_indent, indent // 4)
        return max_indent


class SecurityCommentGenerator:
    """Generates SECURITY comments."""

    PATTERNS = {
        r"eval\s*\(": ("Code Injection (eval)", "Use ast.literal_eval() or JSON parsing instead"),
        r"exec\s*\(": ("Code Injection (exec)", "Avoid executing user-provided code"),
        r"SELECT.*\{.*\}|f['\"].*SELECT": ("SQL Injection", "Use parameterized queries with placeholders"),
        r"os\.system\s*\(": ("OS Command Injection", "Use subprocess with shell=False"),
        r"md5\s*\(": ("Weak Hash Algorithm", "Use bcrypt, scrypt, or PBKDF2 for passwords"),
        r"pickle\.load": ("Deserialization Vulnerability", "Use JSON or MessagePack instead of pickle"),
    }

    @staticmethod
    def generate(context: CommentContext) -> List[CodeComment]:
        """Generate security comments."""
        comments = []

        for pattern, (issue, suggestion) in SecurityCommentGenerator.PATTERNS.items():
            if re.search(pattern, context.code_snippet, re.IGNORECASE):
                comments.append(CodeComment(
                    type=CommentType.SECURITY,
                    severity=CommentSeverity.CRITICAL,
                    message=issue,
                    suggestion=suggestion
                ))

        return comments


class BusinessCommentGenerator:
    """Generates BUSINESS comments."""

    KEYWORDS = {
        "price": "monetary value calculation",
        "discount": "pricing reduction",
        "revenue": "income generation",
        "cost": "expense tracking",
        "subscription": "recurring payment",
        "payment": "transaction processing",
        "invoice": "billing document",
        "customer": "client entity",
        "order": "purchase request",
        "inventory": "stock management",
    }

    @staticmethod
    def generate(context: CommentContext) -> List[CodeComment]:
        """Generate business comments."""
        comments = []
        code_lower = context.code_snippet.lower()

        for keyword, meaning in BusinessCommentGenerator.KEYWORDS.items():
            if keyword in code_lower:
                comments.append(CodeComment(
                    type=CommentType.BUSINESS,
                    severity=CommentSeverity.INFO,
                    message=f"This code handles {meaning}",
                    suggestion="Ensure PM/stakeholders review logic changes here"
                ))
                break  # Only one business comment per context

        return comments


class PerformanceCommentGenerator:
    """Generates PERFORMANCE comments."""

    @staticmethod
    def generate(context: CommentContext) -> List[CodeComment]:
        """Generate performance comments."""
        comments = []

        # Check for nested loops
        if PerformanceCommentGenerator._has_nested_loops(context.code_snippet):
            comments.append(CodeComment(
                type=CommentType.PERFORMANCE,
                severity=CommentSeverity.WARNING,
                message="O(n²) nested loop detected - quadratic time complexity",
                suggestion="Consider using set/dict lookups or sorting before iteration (O(n log n))"
            ))

        # Check for repeated list operations
        if re.search(r"\.append\s*\(", context.code_snippet) and \
           PerformanceCommentGenerator._has_nested_loops(context.code_snippet):
            comments.append(CodeComment(
                type=CommentType.PERFORMANCE,
                severity=CommentSeverity.WARNING,
                message="List append in loop may cause allocation overhead",
                suggestion="Pre-allocate list or use list comprehension instead"
            ))

        return comments

    @staticmethod
    def _has_nested_loops(code: str) -> bool:
        """Check for nested loops."""
        for_count = 0
        in_loop = False
        for line in code.split('\n'):
            stripped = line.strip()
            if stripped.startswith('for '):
                if in_loop:
                    return True
                for_count += 1
                in_loop = True
            elif for_count > 0 and (stripped.startswith('if ') or stripped.startswith('while ')):
                in_loop = True
            elif stripped and not stripped.startswith(' ') and not stripped.startswith('\t'):
                in_loop = False
                for_count = 0

        return False


class ContractCommentGenerator:
    """Generates CONTRACT (API contract) comments."""

    @staticmethod
    def generate(context: CommentContext) -> List[CodeComment]:
        """Generate contract comments."""
        comments = []

        # Check for missing docstring
        if not context.has_docstring and context.function_name:
            comments.append(CodeComment(
                type=CommentType.CONTRACT,
                severity=CommentSeverity.INFO,
                message=f"Function '{context.function_name}' lacks documentation",
                suggestion="Add docstring with: description, args, return type, raises"
            ))

        # Check for missing type hints
        if not context.has_type_hints and context.language == "python":
            comments.append(CodeComment(
                type=CommentType.CONTRACT,
                severity=CommentSeverity.INFO,
                message="Function lacks type hints",
                suggestion="Add type annotations to parameters and return value (PEP 484)"
            ))

        return comments


# ============================================================================
# INTELLIGENT COMMENT GENERATOR (ORCHESTRATOR)
# ============================================================================


class IntelligentCommentGenerator:
    """Orchestrator for intelligent comment generation."""

    GENERATORS = {
        CommentType.COMPLEXITY: ComplexityCommentGenerator.generate,
        CommentType.SECURITY: SecurityCommentGenerator.generate,
        CommentType.BUSINESS: BusinessCommentGenerator.generate,
        CommentType.PERFORMANCE: PerformanceCommentGenerator.generate,
        CommentType.CONTRACT: ContractCommentGenerator.generate,
    }

    def generate(
        self,
        context: CommentContext,
        types: List[CommentType],
        min_severity: Optional[CommentSeverity] = None
    ) -> List[CodeComment]:
        """
        Generate comments for code context.

        Args:
            context: Code context for analysis
            types: List of comment types to generate
            min_severity: Minimum severity to include (filters out lower severity)

        Returns:
            List of CodeComment objects
        """
        comments = []

        for comment_type in types:
            if comment_type in self.GENERATORS:
                generated = self.GENERATORS[comment_type](context)
                comments.extend(generated)

        # Filter by minimum severity
        if min_severity:
            severity_order = {
                CommentSeverity.INFO: 1,
                CommentSeverity.WARNING: 2,
                CommentSeverity.CRITICAL: 3,
            }
            min_level = severity_order.get(min_severity, 0)
            comments = [
                c for c in comments
                if severity_order.get(c.severity, 0) >= min_level
            ]

        return comments


# ============================================================================
# COMMENT REGISTRY (CACHING)
# ============================================================================


class CommentRegistry:
    """Registry for generated comments (cache by function)."""

    def __init__(self):
        """Initialize registry."""
        self._comments: Dict[str, List[CodeComment]] = {}

    def register(self, comment: CodeComment, function_id: str) -> None:
        """
        Register a comment for a function.

        Args:
            comment: Comment to register
            function_id: Function identifier (name or path)
        """
        if function_id not in self._comments:
            self._comments[function_id] = []
        self._comments[function_id].append(comment)

    def get(self, function_id: str) -> List[CodeComment]:
        """
        Get comments for a function.

        Args:
            function_id: Function identifier

        Returns:
            List of comments for function
        """
        return self._comments.get(function_id, [])

    def get_by_type(self, function_id: str, comment_type: CommentType) -> List[CodeComment]:
        """
        Get comments of specific type for function.

        Args:
            function_id: Function identifier
            comment_type: Comment type to filter

        Returns:
            List of comments matching type
        """
        all_comments = self.get(function_id)
        return [c for c in all_comments if c.type == comment_type]

    def clear(self, function_id: Optional[str] = None) -> None:
        """
        Clear comments.

        Args:
            function_id: Clear specific function, or None to clear all
        """
        if function_id:
            self._comments.pop(function_id, None)
        else:
            self._comments.clear()


# ============================================================================
# MODULE EXPORTS
# ============================================================================


__all__ = [
    "CommentType",
    "CommentSeverity",
    "CodeComment",
    "CommentContext",
    "IntelligentCommentGenerator",
    "CommentRegistry",
]
