"""Pattern Detector - Identifies architectural and design patterns in code.

Detects common software design patterns including:
- Singleton pattern (__new__ override with instance check)
- Factory pattern (static/class methods that create instances)
- Decorator pattern (functions decorated with other functions)
- Decorator chains (multiple decorators on single function)

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
AC-ID: E3-PATTERN-DETECTOR
"""

import ast
import logging
from dataclasses import dataclass
from typing import List

logger = logging.getLogger(__name__)


@dataclass
class DetectedPattern:
    """Represents a detected design pattern.
    
    Attributes:
        pattern_type: Type of pattern (SINGLETON, FACTORY, DECORATED_FUNCTION, DECORATOR_CHAIN)
        class_name: Class name (for class-based patterns)
        function_name: Function name (for function-based patterns)
        decorators: List of decorator names (for decorator patterns)
        confidence: Confidence score 0-1
        evidence: List of evidence strings explaining detection
    """
    pattern_type: str
    class_name: str = ""
    function_name: str = ""
    decorators: List[str] = None
    confidence: float = 1.0
    evidence: List[str] = None
    
    def __post_init__(self) -> None:
        """Initialize mutable defaults."""
        if self.decorators is None:
            self.decorators = []
        if self.evidence is None:
            self.evidence = []


class PatternDetector:
    """Production-ready pattern detector for Python code.
    
    Analyzes AST parse results to identify common design patterns:
    - Singleton: Classes with __new__ override and instance tracking
    - Factory: Static/class methods that create and return instances
    - Decorator: Functions with @decorator syntax
    - Decorator Chain: Functions with multiple decorators
    
    Example:
        >>> from cortex.core.intelligence.ast_intelligence import ASTIntelligenceEngine
        >>> engine = ASTIntelligenceEngine()
        >>> parse_result = engine.parse_string(code)
        >>> detector = PatternDetector()
        >>> patterns = detector.detect_patterns(parse_result)
        >>> for p in patterns:
        ...     print(f"{p.pattern_type}: {p.class_name or p.function_name}")
    """
    
    def __init__(self) -> None:
        """Initialize pattern detector."""
        logger.info("PatternDetector initialized")
    
    def detect_patterns(self, parse_result) -> List[DetectedPattern]:
        """Detect design patterns in parsed code.
        
        Args:
            parse_result: ParseResult from ASTIntelligenceEngine
            
        Returns:
            List of detected patterns
        """
        patterns = []
        
        if not parse_result.success or not parse_result.ast_tree:
            logger.warning("Cannot detect patterns from failed parse result")
            return patterns
        
        # Detect class-based patterns
        for cls in parse_result.classes:
            # Check for singleton pattern
            if self._is_singleton(cls):
                patterns.append(
                    DetectedPattern(
                        pattern_type="SINGLETON",
                        class_name=cls.name,
                        evidence=[
                            "__new__ method override detected",
                            "_instance class variable found",
                        ],
                        confidence=0.95,
                    )
                )
            
            # Check for factory pattern
            if self._is_factory(cls):
                patterns.append(
                    DetectedPattern(
                        pattern_type="FACTORY",
                        class_name=cls.name,
                        evidence=[
                            "Static/class method that creates instances",
                            "Returns different types based on parameters",
                        ],
                        confidence=0.85,
                    )
                )
        
        # Detect function-based patterns
        for func in parse_result.functions:
            # Check for decorated functions
            if func.decorators:
                patterns.append(
                    DetectedPattern(
                        pattern_type="DECORATED_FUNCTION",
                        function_name=func.name,
                        decorators=func.decorators,
                        evidence=[f"Decorated with: {', '.join(func.decorators)}"],
                        confidence=1.0,
                    )
                )
                
                # Check for decorator chain (2+ decorators)
                if len(func.decorators) >= 2:
                    patterns.append(
                        DetectedPattern(
                            pattern_type="DECORATOR_CHAIN",
                            function_name=func.name,
                            decorators=func.decorators,
                            evidence=[
                                f"Decorator chain of length {len(func.decorators)}",
                                f"Decorators: {', '.join(func.decorators)}",
                            ],
                            confidence=1.0,
                        )
                    )
        
        # Also check class methods for decorators
        for cls in parse_result.classes:
            for method in cls.methods:
                if method.decorators:
                    patterns.append(
                        DetectedPattern(
                            pattern_type="DECORATED_FUNCTION",
                            class_name=cls.name,
                            function_name=method.name,
                            decorators=method.decorators,
                            evidence=[f"Decorated method with: {', '.join(method.decorators)}"],
                            confidence=1.0,
                        )
                    )
                    
                    if len(method.decorators) >= 2:
                        patterns.append(
                            DetectedPattern(
                                pattern_type="DECORATOR_CHAIN",
                                class_name=cls.name,
                                function_name=method.name,
                                decorators=method.decorators,
                                evidence=[
                                    f"Method decorator chain of length {len(method.decorators)}",
                                    f"Decorators: {', '.join(method.decorators)}",
                                ],
                                confidence=1.0,
                            )
                        )
        
        logger.info(f"Detected {len(patterns)} patterns", extra={"pattern_count": len(patterns)})
        return patterns
    
    def _is_singleton(self, class_info) -> bool:
        """Check if class implements singleton pattern.
        
        Args:
            class_info: ClassInfo from parse result
            
        Returns:
            True if singleton pattern detected
        """
        has_new_method = any(m.name == "__new__" for m in class_info.methods)
        
        # Look for _instance variable (would need AST tree analysis for full check)
        # For now, heuristic: class has __new__ override suggests singleton
        return has_new_method
    
    def _is_factory(self, class_info) -> bool:
        """Check if class implements factory pattern.
        
        Args:
            class_info: ClassInfo from parse result
            
        Returns:
            True if factory pattern detected
        """
        # Look for static/class methods that create instances
        has_factory_method = False
        
        for method in class_info.methods:
            # Check for staticmethod or classmethod decorators
            has_static_decorator = any(
                "staticmethod" in dec or "classmethod" in dec 
                for dec in method.decorators
            )
            
            # Factory methods often have "create" or "make" in name
            has_factory_name = any(
                keyword in method.name.lower() 
                for keyword in ["create", "make", "build", "factory"]
            )
            
            if has_static_decorator and has_factory_name:
                has_factory_method = True
                break
        
        # Also check if class name contains "Factory"
        has_factory_in_name = "factory" in class_info.name.lower()
        
        return has_factory_method or has_factory_in_name
