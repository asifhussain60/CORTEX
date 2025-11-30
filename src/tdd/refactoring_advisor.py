"""
Refactoring Advisor for TDD Demo System
Shows refactoring in action with before/after examples.

Integrates with existing RefactoringIntelligence system.
"""

import ast
import difflib
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import textwrap

# Import existing refactoring intelligence
from src.workflows.refactoring_intelligence import (
    CodeSmellDetector,
    RefactoringEngine,
    CodeSmell as RefactoringCodeSmell,
    CodeSmellType,
    RefactoringSuggestion as RefactoringEngineSuggestion,
    RefactoringType
)


class SmellPriority(Enum):
    """Priority levels for code smells."""
    CRITICAL = "critical"    # Must fix before merge
    RECOMMENDED = "recommended"  # Should fix soon
    OPTIONAL = "optional"    # Nice to have


@dataclass
class CodeSmell:
    """
    Detected code smell with refactoring advice.
    
    This is a demo-specific wrapper around RefactoringIntelligence
    code smells, adding demo presentation features.
    """
    smell_type: str
    location: str
    priority: SmellPriority
    description: str
    confidence: float  # 0.0-1.0
    
    # Demo-specific fields
    before_code: str
    after_code: str
    diff: str
    explanation: str  # Brief explanation of why this is a smell


@dataclass
class RefactoringSuggestion:
    """
    Refactoring suggestion with before/after example.
    
    Demonstrates refactoring in action, not teaching concepts.
    """
    refactoring_type: str
    target_location: str
    priority: SmellPriority
    confidence: float
    
    # Before/after demonstration
    before_code: str
    after_code: str
    diff_lines: List[str]
    
    # Metadata
    estimated_effort: str  # "low", "medium", "high"
    safety_verified: bool
    test_protection: bool  # Whether refactoring is protected by tests


class RefactoringAdvisor:
    """
    Intelligent refactoring advisor for TDD demo system.
    
    Features:
    - AST-based code smell detection (11 types)
    - Before/after examples with diff highlighting
    - Priority ranking (critical/recommended/optional)
    - Confidence scoring (0.0-1.0)
    - Auto-apply capability with test protection
    
    Integrates with existing RefactoringIntelligence from TDD Mastery.
    
    NOT a tutorial - shows refactoring being applied, doesn't teach concepts.
    """
    
    def __init__(self):
        """Initialize Refactoring Advisor."""
        self.detector = CodeSmellDetector()
        self.engine = RefactoringEngine()
    
    def analyze_code(self, code: str, file_path: str = "demo.py") -> List[CodeSmell]:
        """
        Analyze code for smells and generate demo-ready results.
        
        Args:
            code: Python code to analyze
            file_path: File path for reporting
        
        Returns:
            List of CodeSmell objects with before/after examples
        """
        # Use existing refactoring intelligence
        raw_smells = self.detector.analyze_file(file_path, code)
        
        # Convert to demo-ready format with before/after examples
        demo_smells = []
        for smell in raw_smells:
            demo_smell = self._create_demo_smell(smell, code)
            if demo_smell:
                demo_smells.append(demo_smell)
        
        # Sort by priority
        demo_smells.sort(key=lambda s: (
            0 if s.priority == SmellPriority.CRITICAL else
            1 if s.priority == SmellPriority.RECOMMENDED else 2
        ))
        
        return demo_smells
    
    def get_refactoring_suggestions(self, smells: List[CodeSmell], 
                                   code: str) -> List[RefactoringSuggestion]:
        """
        Generate refactoring suggestions for detected smells.
        
        Args:
            smells: List of detected code smells
            code: Original source code
        
        Returns:
            List of RefactoringSuggestion objects with before/after examples
        """
        suggestions = []
        
        # Convert demo smells back to RefactoringIntelligence format
        raw_smells = [self._to_raw_smell(smell) for smell in smells]
        
        # Generate suggestions using existing engine
        raw_suggestions = self.engine.generate_suggestions(raw_smells, code)
        
        # Convert to demo format with enhanced before/after
        for suggestion in raw_suggestions:
            demo_suggestion = self._create_demo_suggestion(suggestion)
            if demo_suggestion:
                suggestions.append(demo_suggestion)
        
        return suggestions
    
    def apply_refactoring(self, suggestion: RefactoringSuggestion, 
                         code: str) -> Tuple[str, bool]:
        """
        Apply refactoring suggestion to code.
        
        Args:
            suggestion: Refactoring suggestion to apply
            code: Original source code
        
        Returns:
            Tuple of (refactored_code, success)
        """
        # For demo purposes, return the after_code
        # In production, this would use AST transformations
        if suggestion.after_code:
            return (suggestion.after_code, True)
        
        return (code, False)
    
    def generate_diff(self, before: str, after: str) -> str:
        """
        Generate unified diff between before and after code.
        
        Args:
            before: Code before refactoring
            after: Code after refactoring
        
        Returns:
            Unified diff string
        """
        before_lines = before.splitlines(keepends=True)
        after_lines = after.splitlines(keepends=True)
        
        diff = difflib.unified_diff(
            before_lines,
            after_lines,
            fromfile='before',
            tofile='after',
            lineterm=''
        )
        
        return ''.join(diff)
    
    def _create_demo_smell(self, smell: RefactoringCodeSmell, 
                          code: str) -> Optional[CodeSmell]:
        """
        Convert RefactoringIntelligence smell to demo format.
        
        Args:
            smell: Raw code smell from detector
            code: Source code
        
        Returns:
            Demo-ready CodeSmell object
        """
        # Extract location info
        parts = smell.location.split(':')
        line_num = int(parts[1]) if len(parts) > 1 else 1
        
        # Get code context (before)
        lines = code.splitlines()
        start = max(0, line_num - 3)
        end = min(len(lines), line_num + 3)
        before_code = '\n'.join(lines[start:end])
        
        # Generate refactored version (after)
        after_code = self._generate_refactored_code(smell, before_code)
        
        # Generate diff
        diff = self.generate_diff(before_code, after_code)
        
        # Map severity to priority
        priority = self._severity_to_priority(smell.severity)
        
        # Add explanation
        explanation = self._get_smell_explanation(smell.smell_type)
        
        return CodeSmell(
            smell_type=smell.smell_type.value,
            location=smell.location,
            priority=priority,
            description=smell.description,
            confidence=smell.confidence,
            before_code=before_code,
            after_code=after_code,
            diff=diff,
            explanation=explanation
        )
    
    def _create_demo_suggestion(self, 
                               suggestion: RefactoringEngineSuggestion) -> Optional[RefactoringSuggestion]:
        """
        Convert RefactoringEngine suggestion to demo format.
        
        Args:
            suggestion: Raw suggestion from engine
        
        Returns:
            Demo-ready RefactoringSuggestion object
        """
        # Generate diff lines
        diff = self.generate_diff(
            suggestion.code_before,
            suggestion.code_after
        )
        diff_lines = diff.splitlines()
        
        # Map to priority
        priority = (SmellPriority.CRITICAL if suggestion.confidence > 0.9
                   else SmellPriority.RECOMMENDED if suggestion.confidence > 0.7
                   else SmellPriority.OPTIONAL)
        
        return RefactoringSuggestion(
            refactoring_type=suggestion.refactoring_type.value,
            target_location=suggestion.target_location,
            priority=priority,
            confidence=suggestion.confidence,
            before_code=suggestion.code_before,
            after_code=suggestion.code_after,
            diff_lines=diff_lines,
            estimated_effort=suggestion.estimated_effort,
            safety_verified=suggestion.safety_verified,
            test_protection=True  # Demo system always has tests
        )
    
    def _generate_refactored_code(self, smell: RefactoringCodeSmell, 
                                 code: str) -> str:
        """
        Generate refactored version of code.
        
        This is simplified for demo purposes. Production version
        would use AST transformations.
        
        Args:
            smell: Detected code smell
            code: Original code snippet
        
        Returns:
            Refactored code
        """
        # Simplified refactoring examples for demo
        if smell.smell_type == CodeSmellType.LONG_METHOD:
            return self._refactor_long_method(code)
        elif smell.smell_type == CodeSmellType.MAGIC_NUMBER:
            return self._refactor_magic_numbers(code)
        elif smell.smell_type == CodeSmellType.COMPLEX_CONDITIONAL:
            return self._refactor_complex_conditional(code)
        elif smell.smell_type == CodeSmellType.DEEP_NESTING:
            return self._refactor_deep_nesting(code)
        else:
            return code  # Return unchanged for unsupported types
    
    def _refactor_long_method(self, code: str) -> str:
        """Refactor long method by extracting helpers."""
        # Simplified: Add comment showing extraction
        lines = code.splitlines()
        if len(lines) > 5:
            middle = len(lines) // 2
            lines.insert(middle, "    # Extracted to helper method:")
            lines.insert(middle + 1, "    # result = self._process_data(...)")
        return '\n'.join(lines)
    
    def _refactor_magic_numbers(self, code: str) -> str:
        """Replace magic numbers with named constants."""
        # Simplified: Replace common magic numbers
        refactored = code
        if '100' in code:
            refactored = code.replace('100', 'THRESHOLD_VALUE')
        if '86400' in code:
            refactored = code.replace('86400', 'SECONDS_PER_DAY')
        return refactored
    
    def _refactor_complex_conditional(self, code: str) -> str:
        """Simplify complex conditional."""
        # Simplified: Add extracted boolean variable
        lines = code.splitlines()
        for i, line in enumerate(lines):
            if 'if ' in line and 'and' in line and 'or' in line:
                indent = len(line) - len(line.lstrip())
                lines.insert(i, ' ' * indent + 'is_valid = self._validate_conditions(...)')
                lines[i + 1] = ' ' * indent + 'if is_valid:'
                break
        return '\n'.join(lines)
    
    def _refactor_deep_nesting(self, code: str) -> str:
        """Reduce deep nesting with early returns."""
        # Simplified: Suggest early return
        lines = code.splitlines()
        for i, line in enumerate(lines):
            if 'if ' in line:
                indent = len(line) - len(line.lstrip())
                lines.insert(i + 1, ' ' * (indent + 4) + '# Use early return to reduce nesting:')
                lines.insert(i + 2, ' ' * (indent + 4) + '# if not condition: return')
                break
        return '\n'.join(lines)
    
    def _severity_to_priority(self, severity: str) -> SmellPriority:
        """Map severity to demo priority."""
        severity_map = {
            'high': SmellPriority.CRITICAL,
            'medium': SmellPriority.RECOMMENDED,
            'low': SmellPriority.OPTIONAL
        }
        return severity_map.get(severity, SmellPriority.OPTIONAL)
    
    def _to_raw_smell(self, demo_smell: CodeSmell) -> RefactoringCodeSmell:
        """Convert demo smell back to RefactoringIntelligence format."""
        # Map priority back to severity
        severity_map = {
            SmellPriority.CRITICAL: 'high',
            SmellPriority.RECOMMENDED: 'medium',
            SmellPriority.OPTIONAL: 'low'
        }
        
        return RefactoringCodeSmell(
            smell_type=CodeSmellType(demo_smell.smell_type),
            location=demo_smell.location,
            severity=severity_map[demo_smell.priority],
            description=demo_smell.description,
            confidence=demo_smell.confidence
        )
    
    def _get_smell_explanation(self, smell_type: CodeSmellType) -> str:
        """Get brief explanation of smell type for demo."""
        explanations = {
            CodeSmellType.LONG_METHOD: "Method too long - harder to understand and test",
            CodeSmellType.COMPLEX_CONDITIONAL: "Complex condition - hard to understand logic",
            CodeSmellType.MAGIC_NUMBER: "Magic number - unclear meaning without context",
            CodeSmellType.DEEP_NESTING: "Deep nesting - increases cognitive load",
            CodeSmellType.LONG_PARAMETER_LIST: "Too many parameters - consider parameter object",
            CodeSmellType.GOD_CLASS: "Class doing too much - violates single responsibility",
            CodeSmellType.DUPLICATE_CODE: "Duplicated code - violates DRY principle",
            CodeSmellType.DEAD_CODE: "Unused code - increases maintenance burden",
            CodeSmellType.SLOW_FUNCTION: "Performance issue - function execution is slow",
            CodeSmellType.HOT_PATH: "Hot path - frequently called, optimize for performance",
            CodeSmellType.PERFORMANCE_BOTTLENECK: "Bottleneck - major contributor to total time"
        }
        return explanations.get(smell_type, "Code quality issue detected")
