# AC-ID: IR-002-02 - Challenge Generator
"""
Challenge Generation System.

PHASE-07: Holistic Intent Router Intelligence
AC-ID: IR-002-02 - Challenge Generation System

Generates challenges (potential issues, risks, edge cases) based on
holistic context analysis. Proactive problem identification.
"""

import ast
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set


# =============================================================================
# ENUMS
# =============================================================================




class Severity(Enum):
    """Challenge severity levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# =============================================================================
# DATA CLASSES
# =============================================================================


@dataclass
class Challenge:
    """A challenge/risk identified during analysis."""
    category: str  # BREAKING_CHANGE, TEST_GAP, etc.
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    description: str
    affected_scope: List[str]
    evidence: List[str]
    mitigation: str
    line_number: Optional[int] = None
    confidence: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
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


# =============================================================================
# DANGEROUS PATTERNS
# =============================================================================


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


# =============================================================================
# CHALLENGE GENERATOR
# =============================================================================


class ChallengeGenerator:
    """Generate challenges based on code analysis."""
    
    def __init__(self):
        """Initialize the challenge generator."""
        self._compile_patterns()
    
    def _compile_patterns(self) -> None:
        """Compile regex patterns for efficiency."""
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
            List of challenges sorted by severity.
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
        challenges.sort(key=lambda c: severity_order.get(c.severity, 0), reverse=True)
        
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
                line_no = source[:match.start()].count('\n') + 1
                challenges.append(Challenge(
                    category="GOVERNANCE_RISK",
                    severity=pattern_info["severity"],
                    description=pattern_info["description"],
                    affected_scope=[f"line {line_no}"],
                    evidence=[match.group(0)[:50]],
                    mitigation=pattern_info["mitigation"],
                    line_number=line_no,
                ))
        
        # Check for missing docstrings
        try:
            tree = ast.parse(source)
            challenges.extend(self._check_docstrings(tree, source))
        except SyntaxError:
            pass
        
        return challenges
    
    def _check_docstrings(self, tree: ast.AST, source: str) -> List[Challenge]:
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
                if node.name.startswith('_') and not node.name.startswith('__'):
                    continue
                
                if not docstring:
                    challenges.append(Challenge(
                        category="GOVERNANCE_RISK",
                        severity="MEDIUM",
                        description=f"Missing docstring for function '{node.name}'",
                        affected_scope=[node.name],
                        evidence=[f"Function at line {node.lineno}"],
                        mitigation=f"Add a docstring describing what '{node.name}' does",
                        line_number=node.lineno,
                    ))
            
            elif isinstance(node, ast.ClassDef):
                docstring = ast.get_docstring(node)
                
                if not docstring:
                    challenges.append(Challenge(
                        category="GOVERNANCE_RISK",
                        severity="MEDIUM",
                        description=f"Missing docstring for class '{node.name}'",
                        affected_scope=[node.name],
                        evidence=[f"Class at line {node.lineno}"],
                        mitigation=f"Add a docstring describing the purpose of '{node.name}'",
                        line_number=node.lineno,
                    ))
        
        return challenges
    
    def analyze_performance(self, source: str) -> List[Challenge]:
        """Analyze source for performance risks.
        
        Args:
            source: Python source code.
            
        Returns:
            List of performance challenges.
        """
        challenges: List[Challenge] = []
        
        for pattern_info in self._performance_patterns:
            matches = pattern_info["compiled"].finditer(source)
            for match in matches:
                line_no = source[:match.start()].count('\n') + 1
                challenges.append(Challenge(
                    category="PERFORMANCE_RISK",
                    severity=pattern_info["severity"],
                    description=pattern_info["description"],
                    affected_scope=[f"line {line_no}"],
                    evidence=[match.group(0)[:80].replace('\n', '\\n')],
                    mitigation=pattern_info["mitigation"],
                    line_number=line_no,
                ))
        
        return challenges
    
    def analyze_coverage(
        self, source: str, context: Dict[str, Any]
    ) -> List[Challenge]:
        """Analyze test coverage gaps.
        
        Args:
            source: Python source code.
            context: Context with existing test information.
            
        Returns:
            List of coverage challenges.
        """
        challenges: List[Challenge] = []
        
        existing_tests = set(context.get("existing_tests", []))
        
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return challenges
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_name = node.name
                
                # Check if test exists
                test_patterns = [
                    f"test_{func_name}",
                    f"test{func_name.title().replace('_', '')}",
                ]
                
                has_test = any(
                    test in existing_tests or 
                    any(test.startswith(p) for p in test_patterns)
                    for test in existing_tests
                )
                
                if not has_test:
                    # Determine severity based on visibility
                    is_private = func_name.startswith('_')
                    severity = "LOW" if is_private else "MEDIUM"
                    
                    challenges.append(Challenge(
                        category="TEST_GAP",
                        severity=severity,
                        description=f"No tests found for function '{func_name}'",
                        affected_scope=[func_name],
                        evidence=[f"Function defined at line {node.lineno}"],
                        mitigation=f"Add tests for '{func_name}' in test file",
                        line_number=node.lineno,
                    ))
        
        return challenges
    
    def analyze_changes(
        self, source: str, changes: List[Dict[str, Any]]
    ) -> List[Challenge]:
        """Analyze proposed changes for breaking change risks.
        
        Args:
            source: Python source code.
            changes: List of proposed changes.
            
        Returns:
            List of breaking change challenges.
        """
        challenges: List[Challenge] = []
        
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return challenges
        
        # Build function call map
        call_map = self._build_call_map(tree)
        
        for change in changes:
            target = change.get("target", "")
            change_types = change.get("changes", [])
            
            # Check if this function is called by others
            callers = [
                caller for caller, callees in call_map.items()
                if target in callees
            ]
            
            # Assess risk based on change type
            for change_type in change_types:
                if change_type in ["add_parameter", "remove_parameter", "modify_return"]:
                    severity = "HIGH" if callers else "MEDIUM"
                    
                    challenges.append(Challenge(
                        category="BREAKING_CHANGE",
                        severity=severity,
                        description=f"Modifying '{target}' signature may break callers",
                        affected_scope=callers if callers else [target],
                        evidence=[
                            f"Change type: {change_type}",
                            f"Callers: {callers}" if callers else "No direct callers found",
                        ],
                        mitigation="Update all callers or add backwards-compatible defaults",
                    ))
                
                elif change_type == "rename_function":
                    challenges.append(Challenge(
                        category="BREAKING_CHANGE",
                        severity="HIGH",
                        description=f"Renaming public API function '{target}'",
                        affected_scope=callers if callers else [target],
                        evidence=[
                            f"Function '{target}' is part of public API",
                        ],
                        mitigation="Create alias for old name or use deprecation warning",
                    ))
        
        return challenges
    
    def _build_call_map(self, tree: ast.AST) -> Dict[str, List[str]]:
        """Build a map of function calls.
        
        Args:
            tree: Parsed AST.
            
        Returns:
            Dict mapping function names to list of functions they call.
        """
        call_map: Dict[str, List[str]] = {}
        current_func = None
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                current_func = node.name
                call_map[current_func] = []
                
                # Walk the function body
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        if isinstance(child.func, ast.Name):
                            call_map[current_func].append(child.func.id)
                        elif isinstance(child.func, ast.Attribute):
                            call_map[current_func].append(child.func.attr)
        
        return call_map
    
    def check_historical_issues(
        self, intent: Dict[str, Any], historical_issues: List[Dict[str, Any]]
    ) -> List[Challenge]:
        """Check for relevant historical issues.
        
        Args:
            intent: Current intent/change intent.
            historical_issues: List of historical issues.
            
        Returns:
            List of historical issue challenges.
        """
        challenges: List[Challenge] = []
        
        scope = intent.get("scope", {})
        target_file = scope.get("file_path", "")
        
        for issue in historical_issues:
            issue_file = issue.get("file", "")
            
            # Simple matching: same file or related area
            if target_file and issue_file:
                # Check if files are in same module/directory
                if self._files_related(target_file, issue_file):
                    challenges.append(Challenge(
                        category="HISTORICAL_ISSUE",
                        severity="MEDIUM",
                        description=f"Historical {issue.get('issue_type', 'issue')} in related area: {issue.get('description', '')}",
                        affected_scope=[issue_file],
                        evidence=[
                            f"Commit: {issue.get('commit', 'unknown')}",
                            f"Date: {issue.get('date', 'unknown')}",
                        ],
                        mitigation="Review previous fix and ensure new changes don't reintroduce the issue",
                    ))
        
        return challenges
    
    def _files_related(self, file1: str, file2: str) -> bool:
        """Check if two files are related.
        
        Args:
            file1: First file path.
            file2: Second file path.
            
        Returns:
            True if files are related.
        """
        # Same file
        if file1 == file2:
            return True
        
        # Same directory
        import os
from cortex.models.canonical_enums import ChallengeCategory
        dir1 = os.path.dirname(file1)
        dir2 = os.path.dirname(file2)
        
        if dir1 and dir2 and dir1 == dir2:
            return True
        
        # Same module name pattern
        base1 = os.path.basename(file1).replace('.py', '')
        base2 = os.path.basename(file2).replace('.py', '')
        
        if base1 in base2 or base2 in base1:
            return True
        
        return False


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    "ChallengeGenerator",
    "Challenge",
    "ChallengeCategory",
    "Severity",
]
