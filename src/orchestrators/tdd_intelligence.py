"""
TDD Intelligence Module - Smart TDD Enforcement

Intelligently determines when TDD is required vs. optional based on code complexity
and business value. Prevents "test bureaucracy" for simple data structures while
enforcing strict TDD discipline for production logic.

Key Features:
- Complexity analysis (methods, logic, dependencies)
- Business value assessment (is this production-critical code?)
- Automatic TDD decision (REQUIRED vs. OPTIONAL)
- Evidence-based rationale (explain why TDD applies/doesn't apply)
- Integration with Brain Protection Rules (TDD_ENFORCEMENT)

Usage:
    from src.orchestrators.tdd_intelligence import TDDIntelligence, CodeType
    
    intelligence = TDDIntelligence()
    
    # Analyze code to determine TDD requirement
    decision = intelligence.analyze_code_for_tdd(
        code_content="public class User { public int Id { get; set; } }",
        file_path="src/Models/User.cs",
        intent="Create user entity"
    )
    
    if decision.tdd_required:
        print(f"TDD MANDATORY: {decision.rationale}")
        # Follow RED→GREEN→REFACTOR
    else:
        print(f"TDD OPTIONAL: {decision.rationale}")
        # Skip TDD, document why

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
Version: 1.0.0 (CORTEX 3.8.2)
"""

import re
import ast
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class CodeType(Enum):
    """Classification of code types for TDD decision."""
    CONTROLLER = "controller"
    SERVICE = "service"
    REPOSITORY = "repository"
    MIDDLEWARE = "middleware"
    ENTITY = "entity"
    DTO = "dto"
    CONFIGURATION = "configuration"
    CONSTANTS = "constants"
    INTERFACE = "interface"
    ORCHESTRATOR = "orchestrator"
    VALIDATOR = "validator"
    UNKNOWN = "unknown"


@dataclass
class TDDDecision:
    """
    TDD enforcement decision with rationale.
    
    Attributes:
        tdd_required: True if TDD is mandatory, False if optional
        code_type: Detected code type (controller, entity, etc.)
        complexity_score: 0-100 (higher = more complex)
        rationale: Human-readable explanation of decision
        evidence: Supporting evidence (methods found, dependencies, etc.)
        exemption_reason: If TDD optional, why (e.g., "Simple POCO, no logic")
    """
    tdd_required: bool
    code_type: CodeType
    complexity_score: int
    rationale: str
    evidence: Dict[str, Any]
    exemption_reason: Optional[str] = None


class TDDIntelligence:
    """
    Intelligent TDD enforcement engine.
    
    Analyzes code complexity and business value to determine when TDD
    should be enforced vs. when it's optional/wasteful.
    """
    
    # TDD is REQUIRED if complexity score >= threshold
    TDD_COMPLEXITY_THRESHOLD = 30
    
    # Code types that always require TDD (production-critical)
    TDD_MANDATORY_TYPES = {
        CodeType.CONTROLLER,
        CodeType.SERVICE,
        CodeType.REPOSITORY,
        CodeType.MIDDLEWARE,
        CodeType.ORCHESTRATOR,
        CodeType.VALIDATOR
    }
    
    # Code types that are usually simple (TDD optional by default)
    TDD_OPTIONAL_TYPES = {
        CodeType.ENTITY,
        CodeType.DTO,
        CodeType.CONFIGURATION,
        CodeType.CONSTANTS,
        CodeType.INTERFACE
    }
    
    def __init__(self):
        """Initialize TDD intelligence engine."""
        self.logger = logging.getLogger(__name__)
    
    def analyze_code_for_tdd(
        self,
        code_content: str,
        file_path: str,
        intent: Optional[str] = None
    ) -> TDDDecision:
        """
        Analyze code to determine if TDD is required.
        
        Args:
            code_content: Source code content to analyze
            file_path: Path to file (used for type detection)
            intent: User's stated intent (e.g., "Create user entity")
        
        Returns:
            TDDDecision with enforcement decision and rationale
        """
        # Detect code type from file path and content
        code_type = self._detect_code_type(file_path, code_content, intent)
        
        # Calculate complexity score
        complexity = self._calculate_complexity(code_content, code_type)
        
        # Gather evidence
        evidence = {
            "file_path": file_path,
            "intent": intent,
            "has_methods": complexity["method_count"] > 0,
            "has_logic": complexity["has_conditionals"] or complexity["has_loops"],
            "has_dependencies": complexity["dependency_count"] > 0,
            "method_count": complexity["method_count"],
            "dependency_count": complexity["dependency_count"],
            "line_count": complexity["line_count"]
        }
        
        # Make TDD decision
        complexity_score = complexity["score"]
        
        # Decision logic
        if code_type in self.TDD_MANDATORY_TYPES:
            # Production-critical code always requires TDD
            return TDDDecision(
                tdd_required=True,
                code_type=code_type,
                complexity_score=complexity_score,
                rationale=f"{code_type.value.capitalize()} is production-critical code with {complexity['method_count']} method(s). TDD mandatory for quality assurance.",
                evidence=evidence,
                exemption_reason=None
            )
        
        elif code_type in self.TDD_OPTIONAL_TYPES and complexity_score < self.TDD_COMPLEXITY_THRESHOLD:
            # Simple data structure, TDD optional
            return TDDDecision(
                tdd_required=False,
                code_type=code_type,
                complexity_score=complexity_score,
                rationale=f"{code_type.value.capitalize()} is a simple data structure (complexity {complexity_score}/100). TDD optional - no logic to test.",
                evidence=evidence,
                exemption_reason=f"Simple {code_type.value} with {complexity['property_count']} properties, no business logic"
            )
        
        elif complexity_score >= self.TDD_COMPLEXITY_THRESHOLD:
            # High complexity always requires TDD
            return TDDDecision(
                tdd_required=True,
                code_type=code_type,
                complexity_score=complexity_score,
                rationale=f"High complexity detected (score {complexity_score}/100). TDD mandatory for {complexity['method_count']} method(s) with logic.",
                evidence=evidence,
                exemption_reason=None
            )
        
        else:
            # Edge case: unknown type or medium complexity
            # Default to TDD required for safety
            return TDDDecision(
                tdd_required=True,
                code_type=code_type,
                complexity_score=complexity_score,
                rationale=f"Moderate complexity (score {complexity_score}/100). TDD recommended as best practice.",
                evidence=evidence,
                exemption_reason=None
            )
    
    def _detect_code_type(self, file_path: str, code_content: str, intent: Optional[str]) -> CodeType:
        """
        Detect code type from file path, content, and intent.
        
        Args:
            file_path: Path to file
            code_content: Source code content
            intent: User's stated intent
        
        Returns:
            CodeType enum value
        """
        file_path_lower = file_path.lower()
        code_lower = code_content.lower()
        intent_lower = (intent or "").lower()
        
        # Check file path patterns
        if "controller" in file_path_lower or "controllers/" in file_path_lower:
            return CodeType.CONTROLLER
        if "service" in file_path_lower or "services/" in file_path_lower:
            return CodeType.SERVICE
        if "repository" in file_path_lower or "repositories/" in file_path_lower:
            return CodeType.REPOSITORY
        if "middleware" in file_path_lower:
            return CodeType.MIDDLEWARE
        if "orchestrator" in file_path_lower:
            return CodeType.ORCHESTRATOR
        if "validator" in file_path_lower or "validation" in file_path_lower:
            return CodeType.VALIDATOR
        if "entity" in file_path_lower or "entities/" in file_path_lower or "models/" in file_path_lower:
            return CodeType.ENTITY
        if "dto" in file_path_lower or "request" in file_path_lower or "response" in file_path_lower:
            return CodeType.DTO
        if "config" in file_path_lower or "settings" in file_path_lower:
            return CodeType.CONFIGURATION
        if "constants" in file_path_lower or "enums" in file_path_lower:
            return CodeType.CONSTANTS
        if "interface" in file_path_lower or code_content.strip().startswith("interface "):
            return CodeType.INTERFACE
        
        # Check code content patterns
        if re.search(r'class\s+\w+Controller', code_content):
            return CodeType.CONTROLLER
        if re.search(r'class\s+\w+Service', code_content):
            return CodeType.SERVICE
        if re.search(r'class\s+\w+Repository', code_content):
            return CodeType.REPOSITORY
        if re.search(r'class\s+\w+Middleware', code_content):
            return CodeType.MIDDLEWARE
        if re.search(r'class\s+\w+Orchestrator', code_content):
            return CodeType.ORCHESTRATOR
        
        # Check intent patterns
        if "entity" in intent_lower or "model" in intent_lower:
            return CodeType.ENTITY
        if "dto" in intent_lower or "request" in intent_lower or "response" in intent_lower:
            return CodeType.DTO
        if "config" in intent_lower or "settings" in intent_lower:
            return CodeType.CONFIGURATION
        
        return CodeType.UNKNOWN
    
    def _calculate_complexity(self, code_content: str, code_type: CodeType) -> Dict[str, Any]:
        """
        Calculate code complexity score (0-100).
        
        Factors:
        - Method count (more methods = higher complexity)
        - Property count (for data structures)
        - Conditional logic (if/switch)
        - Loops (for/while)
        - Dependencies (external calls)
        - Line count
        
        Args:
            code_content: Source code to analyze
            code_type: Detected code type
        
        Returns:
            Dict with complexity metrics and score
        """
        # Count methods (functions/methods with bodies)
        method_pattern = r'(public|private|protected|internal|static)?\s*(async\s+)?\w+\s+\w+\s*\([^)]*\)\s*\{'
        methods = re.findall(method_pattern, code_content)
        method_count = len(methods)
        
        # Count properties (auto-properties and regular properties)
        property_pattern = r'(public|private|protected|internal)?\s*\w+\s+\w+\s*\{\s*(get|set)'
        properties = re.findall(property_pattern, code_content)
        property_count = len(properties)
        
        # Check for logic
        has_conditionals = bool(re.search(r'\b(if|switch|case|else)\b', code_content))
        has_loops = bool(re.search(r'\b(for|while|foreach|do)\b', code_content))
        
        # Count dependencies (references to external services/classes)
        dependency_pattern = r'(I\w+Repository|I\w+Service|DbContext|\w+Client)'
        dependencies = re.findall(dependency_pattern, code_content)
        dependency_count = len(set(dependencies))
        
        # Line count
        line_count = len(code_content.splitlines())
        
        # Calculate score
        score = 0
        
        # Method count contributes most to complexity
        score += min(method_count * 15, 50)  # Max 50 points
        
        # Logic complexity
        if has_conditionals:
            score += 15
        if has_loops:
            score += 15
        
        # Dependencies indicate integration complexity
        score += min(dependency_count * 10, 20)  # Max 20 points
        
        # For entities/DTOs, having methods is unusual (increases complexity)
        if code_type in [CodeType.ENTITY, CodeType.DTO] and method_count > 0:
            score += 20  # Entities with methods require TDD
        
        # Cap at 100
        score = min(score, 100)
        
        return {
            "score": score,
            "method_count": method_count,
            "property_count": property_count,
            "has_conditionals": has_conditionals,
            "has_loops": has_loops,
            "dependency_count": dependency_count,
            "line_count": line_count
        }
    
    def should_enforce_tdd(
        self,
        code_type: CodeType,
        has_methods: bool,
        has_logic: bool,
        has_dependencies: bool
    ) -> bool:
        """
        Simple boolean check: should TDD be enforced?
        
        Args:
            code_type: Type of code being created
            has_methods: Does code have methods (not just properties)?
            has_logic: Does code have conditionals/loops?
            has_dependencies: Does code call external services?
        
        Returns:
            True if TDD should be enforced, False otherwise
        """
        # Always enforce for production-critical types
        if code_type in self.TDD_MANDATORY_TYPES:
            return True
        
        # Always skip for interfaces (no implementation to test)
        if code_type == CodeType.INTERFACE:
            return False
        
        # Enforce if code has logic (even if it's an entity)
        if has_methods and (has_logic or has_dependencies):
            return True
        
        # Otherwise, TDD optional
        return False
    
    def get_tdd_guidance(self, decision: TDDDecision) -> str:
        """
        Generate human-readable TDD guidance based on decision.
        
        Args:
            decision: TDD decision from analyze_code_for_tdd
        
        Returns:
            Formatted guidance string for user
        """
        if decision.tdd_required:
            return f"""
🔴 TDD MANDATORY

Code Type: {decision.code_type.value.capitalize()}
Complexity: {decision.complexity_score}/100

{decision.rationale}

Required Workflow:
1. RED Phase: Write failing test (verify it fails)
2. GREEN Phase: Write minimal implementation (make test pass)
3. REFACTOR Phase: Clean up code (maintain passing tests)

Evidence:
- Methods: {decision.evidence.get('method_count', 0)}
- Dependencies: {decision.evidence.get('dependency_count', 0)}
- Has Logic: {decision.evidence.get('has_logic', False)}
"""
        else:
            return f"""
⏭️  TDD OPTIONAL

Code Type: {decision.code_type.value.capitalize()}
Complexity: {decision.complexity_score}/100

{decision.rationale}

Exemption Reason: {decision.exemption_reason}

You may create this code without TDD workflow. However, if you add
methods with logic later, TDD will become mandatory.

Evidence:
- Methods: {decision.evidence.get('method_count', 0)}
- Properties: {decision.evidence.get('property_count', 0)}
- Has Logic: {decision.evidence.get('has_logic', False)}
"""


# Singleton instance for global access
_tdd_intelligence_instance: Optional[TDDIntelligence] = None


def get_tdd_intelligence() -> TDDIntelligence:
    """Get singleton TDD intelligence instance."""
    global _tdd_intelligence_instance
    if _tdd_intelligence_instance is None:
        _tdd_intelligence_instance = TDDIntelligence()
    return _tdd_intelligence_instance
