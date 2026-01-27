# AC-ID: IR-002-03 - Recommendation Engine
"""
Recommendation Engine for CORTEX Intent Router.

PHASE-07: Holistic Intent Router Intelligence
AC-ID: IR-002-03 - Recommendation Engine

Provides:
- Best practice matching
- Alternative approach finding
- Test strategy suggestion
- Documentation recommendations
- Governance compliance recommendations
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum


class RecommendationType(Enum):
    """Types of recommendations."""
    BEST_PRACTICE = "best_practice"
    ALTERNATIVE = "alternative"
    TEST_STRATEGY = "test_strategy"
    DOCUMENTATION = "documentation"
    GOVERNANCE = "governance"


class Priority(Enum):
    """Recommendation priority levels."""
    HIGH = 1
    MEDIUM = 2
    LOW = 3


@dataclass
class Recommendation:
    """A single recommendation from the engine."""
    
    recommendation_type: RecommendationType
    title: str
    description: str
    rationale: str
    priority: Priority = Priority.MEDIUM
    code_example: Optional[str] = None
    affected_lines: List[int] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert recommendation to dictionary."""
        return {
            "type": self.recommendation_type.value,
            "title": self.title,
            "description": self.description,
            "rationale": self.rationale,
            "priority": self.priority.value,
            "code_example": self.code_example,
            "affected_lines": self.affected_lines,
            "tags": self.tags
        }


@dataclass
class RecommendationResult:
    """Result from recommendation engine analysis."""
    
    recommendations: List[Recommendation] = field(default_factory=list)
    analyzed_code_length: int = 0
    analysis_time_ms: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "recommendations": [r.to_dict() for r in self.recommendations],
            "analyzed_code_length": self.analyzed_code_length,
            "analysis_time_ms": self.analysis_time_ms
        }


class RecommendationEngine:
    """Engine for generating code recommendations.
    
    Analyzes Python code and generates recommendations for:
    - Design pattern improvements (singleton, factory, etc.)
    - Error handling improvements
    - Code style alternatives (list comprehensions, etc.)
    - Test strategies
    - Documentation needs
    - Governance compliance
    """
    
    def __init__(self) -> None:
        """Initialize recommendation engine."""
        self._patterns = self._load_patterns()
    
    def _load_patterns(self) -> Dict[str, Any]:
        """Load recommendation patterns."""
        return {
            "singleton": {
                "indicators": ["getInstance", "single instance", "only one"],
                "recommendation": "Consider implementing the Singleton pattern"
            },
            "error_handling": {
                "indicators": ["open(", "json.load", "int(", "float("],
                "recommendation": "Add try-except blocks for error handling"
            },
            "context_manager": {
                "indicators": ["open(", "acquire(", "lock("],
                "recommendation": "Use context managers (with statement)"
            }
        }
    
    def analyze(self, code: str, intent: Optional[str] = None) -> RecommendationResult:
        """Analyze code and generate recommendations.
        
        Args:
            code: Python source code to analyze
            intent: Optional intent context for more relevant recommendations
            
        Returns:
            RecommendationResult with list of recommendations
        """
        import time
        start = time.time()
        
        recommendations = []
        
        # Check for singleton pattern opportunities
        if self._needs_singleton(code):
            recommendations.append(Recommendation(
                recommendation_type=RecommendationType.BEST_PRACTICE,
                title="Consider Singleton Pattern",
                description="This class creates new instances each time. Consider using Singleton pattern.",
                rationale="A singleton ensures only one instance exists, reducing resource usage.",
                priority=Priority.MEDIUM,
                tags=["design-pattern", "singleton"]
            ))
        
        # Check for error handling needs
        if self._needs_error_handling(code):
            recommendations.append(Recommendation(
                recommendation_type=RecommendationType.BEST_PRACTICE,
                title="Add Error Handling",
                description="This code performs operations that may fail without error handling.",
                rationale="Proper error handling prevents crashes and improves user experience.",
                priority=Priority.HIGH,
                tags=["error-handling", "robustness"]
            ))
        
        # Check for context manager opportunities
        if self._needs_context_manager(code):
            recommendations.append(Recommendation(
                recommendation_type=RecommendationType.BEST_PRACTICE,
                title="Use Context Manager",
                description="Resource handling could use context managers for automatic cleanup.",
                rationale="Context managers ensure resources are properly released.",
                priority=Priority.MEDIUM,
                tags=["context-manager", "resource-management"]
            ))
        
        # Check for list comprehension opportunities
        if self._can_use_list_comprehension(code):
            recommendations.append(Recommendation(
                recommendation_type=RecommendationType.ALTERNATIVE,
                title="Use List Comprehension",
                description="This loop could be simplified with a list comprehension.",
                rationale="List comprehensions are more Pythonic and often faster.",
                priority=Priority.LOW,
                tags=["pythonic", "list-comprehension"]
            ))
        
        # Check for dict.get() opportunities
        if self._can_use_dict_get(code):
            recommendations.append(Recommendation(
                recommendation_type=RecommendationType.ALTERNATIVE,
                title="Use dict.get()",
                description="Dictionary access could use .get() for safer retrieval.",
                rationale="dict.get() provides a default value and avoids KeyError.",
                priority=Priority.LOW,
                tags=["pythonic", "dict-access"]
            ))
        
        # Check for API test needs
        if self._needs_api_tests(code):
            recommendations.append(Recommendation(
                recommendation_type=RecommendationType.TEST_STRATEGY,
                title="Add API Tests",
                description="This API endpoint needs comprehensive test coverage.",
                rationale="API tests ensure endpoint behavior is correct and documented.",
                priority=Priority.HIGH,
                tags=["testing", "api"]
            ))
        
        # Check for edge case tests
        if self._needs_edge_case_tests(code):
            recommendations.append(Recommendation(
                recommendation_type=RecommendationType.TEST_STRATEGY,
                title="Add Edge Case Tests",
                description="Consider adding tests for edge cases and error conditions.",
                rationale="Edge case tests catch boundary conditions and improve robustness.",
                priority=Priority.MEDIUM,
                tags=["testing", "edge-cases"]
            ))
        
        # Check for documentation needs
        if self._needs_class_docstring(code):
            recommendations.append(Recommendation(
                recommendation_type=RecommendationType.DOCUMENTATION,
                title="Add Class Docstring",
                description="This class is missing a docstring.",
                rationale="Docstrings improve code readability and maintainability.",
                priority=Priority.MEDIUM,
                tags=["documentation", "docstring"]
            ))
        
        # Check for API documentation needs
        if self._needs_api_documentation(code):
            recommendations.append(Recommendation(
                recommendation_type=RecommendationType.DOCUMENTATION,
                title="Add API Documentation",
                description="API endpoints need comprehensive documentation.",
                rationale="API documentation helps consumers understand how to use the API.",
                priority=Priority.HIGH,
                tags=["documentation", "api"]
            ))
        
        # Check for type hints
        if self._needs_type_hints(code):
            recommendations.append(Recommendation(
                recommendation_type=RecommendationType.GOVERNANCE,
                title="Add Type Hints",
                description="Functions are missing type hints.",
                rationale="Type hints improve code quality and enable static analysis.",
                priority=Priority.HIGH,
                tags=["governance", "type-hints", "CORE-011"]
            ))
        
        # Sort by priority
        recommendations.sort(key=lambda r: r.priority.value)
        
        elapsed = (time.time() - start) * 1000
        
        return RecommendationResult(
            recommendations=recommendations,
            analyzed_code_length=len(code),
            analysis_time_ms=elapsed
        )
    
    def _needs_singleton(self, code: str) -> bool:
        """Check if code could benefit from singleton pattern."""
        return ("class " in code and 
                ("Connection" in code or "Manager" in code) and
                "__init__" in code and
                "def get_" in code)
    
    def _needs_error_handling(self, code: str) -> bool:
        """Check if code needs better error handling."""
        risky_patterns = ["open(", "json.load", "int(", "float(", ".read("]
        has_risky = any(p in code for p in risky_patterns)
        has_try = "try:" in code
        return has_risky and not has_try
    
    def _needs_context_manager(self, code: str) -> bool:
        """Check if code could use context managers."""
        return "open(" in code and "with " not in code
    
    def _can_use_list_comprehension(self, code: str) -> bool:
        """Check if loop could be list comprehension."""
        return ("for " in code and 
                "append(" in code and 
                "[" in code)
    
    def _can_use_dict_get(self, code: str) -> bool:
        """Check if dict access could use .get()."""
        # Look for patterns like data['key'] or data[key] without .get()
        import re
        # Match both quoted and variable key access
        dict_access = re.search(r"\w+\[[\w'\"]", code)
        has_get = ".get(" in code
        # Also detect the if key in data: return data[key] pattern
        if_in_pattern = "if " in code and " in " in code and "[" in code
        return (dict_access is not None or if_in_pattern) and not has_get
    
    def _needs_api_tests(self, code: str) -> bool:
        """Check if API endpoints need tests."""
        return ("@app.route" in code or 
                "@router." in code or
                "Flask" in code or
                "FastAPI" in code)
    
    def _needs_edge_case_tests(self, code: str) -> bool:
        """Check if code has edge cases to test."""
        # Detect code that processes input and could have edge cases
        edge_indicators = [
            "if ", "else:", "elif ", "try:", "except",
            "int(", "float(", "json.", ".read(", "open(",
            "data[", "['", "return "
        ]
        # Lower threshold - any code with potential failure points needs edge case tests
        return sum(1 for i in edge_indicators if i in code) >= 2
    
    def _needs_class_docstring(self, code: str) -> bool:
        """Check if class needs docstring."""
        import re
        # Find class without immediate docstring
        class_without_doc = re.search(r'class \w+.*:\s*\n\s*(?!""")', code)
        return class_without_doc is not None
    
    def _needs_api_documentation(self, code: str) -> bool:
        """Check if API needs documentation."""
        # API code (Flask/FastAPI routes) should have comprehensive docs
        is_api = "@app.route" in code or "@router." in code
        if not is_api:
            return False
        # Even if it has some docstrings, recommend more comprehensive API docs
        return True
    
    def _needs_type_hints(self, code: str) -> bool:
        """Check if functions need type hints."""
        import re
        # Find def without -> return type
        def_without_hints = re.search(r'def \w+\([^)]*\):\s*\n', code)
        return def_without_hints is not None
