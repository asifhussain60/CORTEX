# AC-ID: IR-001-01 - AST-Based Code Intelligence - Pattern Detector
"""
Pattern Detector for CORTEX LENS.

PHASE-07: Holistic Intent Router Intelligence
AC-ID: IR-001-01 - AST-Based Code Intelligence

This module detects architectural patterns in Python code including:
- Singleton pattern
- Factory pattern
- Decorator pattern and decorator chains

Part of CORTEX LENS context intelligence system.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, TYPE_CHECKING

if TYPE_CHECKING:
    from cortex.brain.core.intelligence.ast_intelligence import ParseResult, ClassInfo


# =============================================================================
# DATA CLASSES
# =============================================================================


@dataclass
class DetectedPattern:
    """Represents a detected design pattern.
    
    Attributes:
        pattern_type: Type of pattern (SINGLETON, FACTORY, etc.)
        class_name: Name of class implementing pattern (if applicable)
        function_name: Name of function (if applicable)
        decorators: List of decorator names (for decorated functions)
        confidence: Confidence score for detection (0.0 - 1.0)
        evidence: List of evidence for the detection
        line_number: Line number where pattern is detected
    """
    pattern_type: str
    class_name: Optional[str] = None
    function_name: Optional[str] = None
    decorators: List[str] = field(default_factory=list)
    confidence: float = 1.0
    evidence: List[str] = field(default_factory=list)
    line_number: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "pattern_type": self.pattern_type,
            "class_name": self.class_name,
            "function_name": self.function_name,
            "decorators": self.decorators,
            "confidence": self.confidence,
            "evidence": self.evidence,
            "line_number": self.line_number,
        }


# =============================================================================
# PATTERN DETECTOR
# =============================================================================


class PatternDetector:
    """Detects architectural patterns in parsed code.
    
    Analyzes parsed AST information to identify common design patterns
    like singleton, factory, and decorator patterns.
    
    Example:
        >>> from cortex.brain.core.intelligence.ast_intelligence import ASTIntelligenceEngine
        >>> engine = ASTIntelligenceEngine()
        >>> result = engine.parse_file(Path("module.py"))
        >>> detector = PatternDetector()
        >>> patterns = detector.detect_patterns(result)
    """
    
    def detect_patterns(self, parse_result: "ParseResult") -> List[DetectedPattern]:
        """Detect all patterns in parsed result.
        
        Args:
            parse_result: Result from ASTIntelligenceEngine
            
        Returns:
            List of detected patterns
        """
        patterns: List[DetectedPattern] = []
        
        if not parse_result.success or parse_result.ast_tree is None:
            return patterns
        
        # Detect class-based patterns
        for cls in parse_result.classes:
            patterns.extend(self._detect_class_patterns(cls, parse_result))
        
        # Detect function-based patterns
        for func in parse_result.functions:
            patterns.extend(self._detect_function_patterns(func))
        
        # Detect decorator chains
        patterns.extend(self._detect_decorator_chains(parse_result))
        
        return patterns
    
    def _detect_class_patterns(
        self,
        cls: "ClassInfo",
        parse_result: "ParseResult",
    ) -> List[DetectedPattern]:
        """Detect patterns in a class definition.
        
        Args:
            cls: Class information
            parse_result: Full parse result for context
            
        Returns:
            List of detected patterns
        """
        patterns: List[DetectedPattern] = []
        
        # Check for singleton pattern
        singleton = self._detect_singleton(cls)
        if singleton:
            patterns.append(singleton)
        
        # Check for factory pattern
        factory = self._detect_factory(cls, parse_result)
        if factory:
            patterns.append(factory)
        
        return patterns
    
    def _detect_singleton(self, cls: "ClassInfo") -> Optional[DetectedPattern]:
        """Detect singleton pattern in a class.
        
        Singleton indicators:
        - Has _instance class variable
        - __new__ method that checks/sets _instance
        
        Args:
            cls: Class information
            
        Returns:
            DetectedPattern if singleton, None otherwise
        """
        evidence: List[str] = []
        
        # Check for _instance class variable
        has_instance_var = any(
            var in ("_instance", "__instance", "instance")
            for var in cls.class_variables
        )
        if has_instance_var:
            evidence.append("Has _instance class variable")
        
        # Check for __new__ method
        new_method = next(
            (m for m in cls.methods if m.name == "__new__"),
            None
        )
        if new_method:
            evidence.append("Has __new__ method")
        
        # Singleton requires both indicators
        if has_instance_var and new_method:
            return DetectedPattern(
                pattern_type="SINGLETON",
                class_name=cls.name,
                confidence=0.9,
                evidence=evidence,
                line_number=cls.line_number,
            )
        
        return None
    
    def _detect_factory(
        self,
        cls: "ClassInfo",
        parse_result: "ParseResult",
    ) -> Optional[DetectedPattern]:
        """Detect factory pattern in a class.
        
        Factory indicators:
        - Has method with "create" in name
        - Method returns instance of another class
        - Static method that creates objects
        
        Args:
            cls: Class information
            parse_result: Full parse result for context
            
        Returns:
            DetectedPattern if factory, None otherwise
        """
        evidence: List[str] = []
        
        # Look for create methods
        create_methods = [
            m for m in cls.methods
            if "create" in m.name.lower() or "make" in m.name.lower()
        ]
        
        if create_methods:
            evidence.append(f"Has create method: {create_methods[0].name}")
        
        # Check for staticmethod decorator on create methods
        for method in create_methods:
            if "staticmethod" in method.decorators:
                evidence.append("Create method is static")
        
        # Check if class name suggests factory
        if "factory" in cls.name.lower():
            evidence.append("Class name contains 'factory'")
        
        # Factory requires at least create method
        if create_methods:
            return DetectedPattern(
                pattern_type="FACTORY",
                class_name=cls.name,
                confidence=0.8 if len(evidence) >= 2 else 0.6,
                evidence=evidence,
                line_number=cls.line_number,
            )
        
        return None
    
    def _detect_function_patterns(self, func: Any) -> List[DetectedPattern]:
        """Detect patterns in a function definition.
        
        Args:
            func: Function information
            
        Returns:
            List of detected patterns
        """
        patterns: List[DetectedPattern] = []
        
        # Check for decorated functions
        if func.decorators:
            patterns.append(DetectedPattern(
                pattern_type="DECORATED_FUNCTION",
                function_name=func.name,
                decorators=func.decorators,
                confidence=1.0,
                evidence=[f"Has decorators: {', '.join(func.decorators)}"],
                line_number=func.line_number,
            ))
        
        return patterns
    
    def _detect_decorator_chains(
        self,
        parse_result: "ParseResult",
    ) -> List[DetectedPattern]:
        """Detect decorator chains (functions with multiple decorators).
        
        Args:
            parse_result: Full parse result
            
        Returns:
            List of detected decorator chain patterns
        """
        patterns: List[DetectedPattern] = []
        
        # Check functions
        for func in parse_result.functions:
            if len(func.decorators) >= 2:
                patterns.append(DetectedPattern(
                    pattern_type="DECORATOR_CHAIN",
                    function_name=func.name,
                    decorators=func.decorators,
                    confidence=1.0,
                    evidence=[
                        f"Function has {len(func.decorators)} decorators",
                        f"Decorators: {', '.join(func.decorators)}",
                    ],
                    line_number=func.line_number,
                ))
        
        # Check class methods
        for cls in parse_result.classes:
            for method in cls.methods:
                if len(method.decorators) >= 2:
                    patterns.append(DetectedPattern(
                        pattern_type="DECORATOR_CHAIN",
                        class_name=cls.name,
                        function_name=method.name,
                        decorators=method.decorators,
                        confidence=1.0,
                        evidence=[
                            f"Method has {len(method.decorators)} decorators",
                            f"Decorators: {', '.join(method.decorators)}",
                        ],
                        line_number=method.line_number,
                    ))
        
        return patterns


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    "PatternDetector",
    "DetectedPattern",
]
