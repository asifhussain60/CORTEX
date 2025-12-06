"""
Code Explanation Generator (No-Bloat Educational System)

Generates contextual explanations for generated code WITHOUT adding inline comments.
All educational content lives in response messages, keeping code clean for all users.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from typing import Dict, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass


@dataclass
class CodeExplanation:
    """Structured explanation for generated code."""
    
    # Core explanation
    what_it_does: str  # High-level purpose
    why_this_approach: str  # Design decisions
    
    # Pattern identification
    patterns_used: List[str]  # ["Dependency Injection", "Factory Pattern"]
    solid_principles: List[str]  # ["SRP", "DIP"]
    
    # Educational resources
    learning_paths: List[Tuple[str, str]]  # [(title, file_path)]
    key_concepts: List[Tuple[str, str]]  # [(concept, explanation)]
    
    # Security/best practices
    considerations: List[str]  # ["Token expiration in production", "Hash passwords"]


class CodeExplanationGenerator:
    """
    Generates contextual explanations for code WITHOUT inline comments.
    
    Design Philosophy:
    - Code remains clean and comment-free (expert-level quality)
    - Explanations live in response messages only
    - Junior/mid users get educational content separate from code
    - Expert users see clean code, juniors see code + explanation section
    
    Usage:
        generator = CodeExplanationGenerator()
        
        code = '''
        class JWTAuthService:
            def __init__(self, secret_key: str, token_expiry: int = 3600):
                self.secret_key = secret_key
                self.token_expiry = token_expiry
        '''
        
        explanation = generator.generate_explanation(
            code=code,
            context={
                "operation": "authentication_service",
                "patterns": ["dependency_injection", "single_responsibility"]
            },
            experience_level="junior"
        )
        
        # Response includes:
        # - Clean code (no comments)
        # - Separate explanation section
        # - Links to learning paths
        # - Pattern breakdown
    """
    
    def __init__(self, learning_paths_base: str = "cortex-brain/documents/learning-paths"):
        """
        Initialize generator.
        
        Args:
            learning_paths_base: Base path to learning path documents
        """
        self.learning_paths_base = learning_paths_base
        
        # Pattern recognition templates
        self.pattern_explainers = {
            "dependency_injection": self._explain_dependency_injection,
            "single_responsibility": self._explain_single_responsibility,
            "factory_pattern": self._explain_factory_pattern,
            "repository_pattern": self._explain_repository_pattern,
            "strategy_pattern": self._explain_strategy_pattern,
        }
        
        # Learning path mappings
        self.learning_paths = {
            "solid": ("SOLID Principles", "solid-principles.md"),
            "dependency_injection": ("Dependency Injection", "dependency-injection.md"),
            "tdd": ("TDD Workflow", "tdd-workflow.md"),
            "async": ("Async Patterns", "async-patterns.md"),
            "testing": ("Testing Strategies", "testing-strategies.md"),
        }
    
    def generate_explanation(
        self,
        code: str,
        context: Dict,
        experience_level: str = "junior"
    ) -> Optional[CodeExplanation]:
        """
        Generate explanation for code based on context and experience level.
        
        Args:
            code: The generated code (clean, no comments)
            context: Dict with operation type, patterns used, etc.
            experience_level: "junior", "mid", "senior", "expert"
            
        Returns:
            CodeExplanation if user is junior/mid, None for senior/expert
        """
        # Expert users don't need explanations
        if experience_level in ["senior", "expert"]:
            return None
        
        operation = context.get("operation", "unknown")
        patterns = context.get("patterns", [])
        
        # Detect patterns from code if not provided
        if not patterns:
            patterns = self._detect_patterns(code)
        
        # Build explanation
        what_it_does = self._explain_purpose(operation, code, context)
        why_this_approach = self._explain_design_decisions(patterns, context)
        
        patterns_used = [p.replace("_", " ").title() for p in patterns]
        solid_principles = self._identify_solid_principles(patterns)
        
        learning_paths = self._get_relevant_learning_paths(patterns)
        key_concepts = self._extract_key_concepts(patterns, operation)
        
        considerations = self._get_best_practices(operation, patterns)
        
        return CodeExplanation(
            what_it_does=what_it_does,
            why_this_approach=why_this_approach,
            patterns_used=patterns_used,
            solid_principles=solid_principles,
            learning_paths=learning_paths,
            key_concepts=key_concepts,
            considerations=considerations
        )
    
    def format_explanation_section(self, explanation: CodeExplanation) -> str:
        """
        Format explanation as markdown section for response message.
        
        Args:
            explanation: CodeExplanation object
            
        Returns:
            Formatted markdown section
        """
        sections = []
        
        # What it does
        sections.append(f"**🎯 What This Code Does:**\n{explanation.what_it_does}\n")
        
        # Design decisions
        sections.append(f"**⚡ Why This Approach:**\n{explanation.why_this_approach}\n")
        
        # Patterns used
        if explanation.patterns_used:
            patterns_list = "\n".join([f"- {p}" for p in explanation.patterns_used])
            sections.append(f"**🏗️ Patterns Applied:**\n{patterns_list}\n")
        
        # SOLID principles
        if explanation.solid_principles:
            solid_list = "\n".join([f"- **{p}**: {self._get_solid_description(p)}" 
                                   for p in explanation.solid_principles])
            sections.append(f"**🔷 SOLID Principles:**\n{solid_list}\n")
        
        # Key concepts
        if explanation.key_concepts:
            concepts_list = "\n".join([f"- **{concept}**: {desc}" 
                                      for concept, desc in explanation.key_concepts])
            sections.append(f"**💡 Key Concepts:**\n{concepts_list}\n")
        
        # Best practices
        if explanation.considerations:
            considerations_list = "\n".join([f"- {c}" for c in explanation.considerations])
            sections.append(f"**⚠️ Important Considerations:**\n{considerations_list}\n")
        
        # Learning paths
        if explanation.learning_paths:
            paths_list = "\n".join([f"- [{title}](file:///{self.learning_paths_base}/{path}) - Deep dive guide" 
                                   for title, path in explanation.learning_paths])
            sections.append(f"**📚 Learn More:**\n{paths_list}\n")
        
        return "\n".join(sections)
    
    # ========== Pattern Explainers ==========
    
    def _explain_dependency_injection(self, context: Dict) -> str:
        """Explain DI pattern in context."""
        return (
            "Dependencies passed through constructor instead of created internally. "
            "Makes code testable (can inject mocks) and flexible (swap implementations)."
        )
    
    def _explain_single_responsibility(self, context: Dict) -> str:
        """Explain SRP in context."""
        return (
            "This class has ONE clear job. Changes to other features won't require "
            "modifying this code. Easier to understand, test, and maintain."
        )
    
    def _explain_factory_pattern(self, context: Dict) -> str:
        """Explain Factory pattern in context."""
        return (
            "Object creation logic centralized in factory method. Client code doesn't "
            "need to know implementation details. Makes adding new types easier."
        )
    
    def _explain_repository_pattern(self, context: Dict) -> str:
        """Explain Repository pattern in context."""
        return (
            "Data access logic isolated from business logic. Can swap data sources "
            "(SQLite → PostgreSQL) without changing business code."
        )
    
    def _explain_strategy_pattern(self, context: Dict) -> str:
        """Explain Strategy pattern in context."""
        return (
            "Different algorithms/behaviors encapsulated as separate strategies. "
            "Client can switch strategies at runtime without code changes."
        )
    
    # ========== Helper Methods ==========
    
    def _detect_patterns(self, code: str) -> List[str]:
        """Detect patterns from code structure."""
        patterns = []
        
        if "__init__" in code and "self." in code:
            # Check for constructor injection
            if ":" in code.split("__init__")[1].split(")")[0]:
                patterns.append("dependency_injection")
        
        if "class " in code:
            # Single class = likely SRP
            class_count = code.count("class ")
            if class_count == 1:
                patterns.append("single_responsibility")
        
        if "create_" in code.lower() or "factory" in code.lower():
            patterns.append("factory_pattern")
        
        if "repository" in code.lower() or ("get_" in code and "save_" in code):
            patterns.append("repository_pattern")
        
        return patterns
    
    def _explain_purpose(self, operation: str, code: str, context: Dict) -> str:
        """Generate high-level purpose explanation."""
        operation_purposes = {
            "authentication_service": "Handles user authentication using JWT tokens. Creates tokens on login, validates tokens on requests.",
            "database_repository": "Manages data persistence with clean separation from business logic.",
            "api_client": "Communicates with external API. Handles requests, error handling, and response parsing.",
            "configuration_manager": "Centralizes application configuration. Loads from files/env vars with validation.",
        }
        
        return operation_purposes.get(operation, 
            f"Implements {operation.replace('_', ' ')} with clean architecture patterns.")
    
    def _explain_design_decisions(self, patterns: List[str], context: Dict) -> str:
        """Explain why these patterns were chosen."""
        if not patterns:
            return "Standard implementation following CORTEX best practices."
        
        reasons = []
        
        if "dependency_injection" in patterns:
            reasons.append("**Dependency Injection** for testability and flexibility")
        
        if "single_responsibility" in patterns:
            reasons.append("**Single Responsibility** to keep code focused and maintainable")
        
        if "factory_pattern" in patterns:
            reasons.append("**Factory Pattern** to centralize object creation logic")
        
        if "repository_pattern" in patterns:
            reasons.append("**Repository Pattern** to isolate data access from business logic")
        
        return "This approach chosen for: " + ", ".join(reasons)
    
    def _identify_solid_principles(self, patterns: List[str]) -> List[str]:
        """Map patterns to SOLID principles."""
        solid = []
        
        if "single_responsibility" in patterns:
            solid.append("SRP")
        
        if "dependency_injection" in patterns:
            solid.append("DIP")
        
        # OCP applies to most extensible patterns
        if any(p in patterns for p in ["factory_pattern", "strategy_pattern"]):
            solid.append("OCP")
        
        return solid
    
    def _get_solid_description(self, principle: str) -> str:
        """Get brief description of SOLID principle."""
        descriptions = {
            "SRP": "Single Responsibility - One class, one job",
            "OCP": "Open/Closed - Open for extension, closed for modification",
            "LSP": "Liskov Substitution - Subtypes must be substitutable",
            "ISP": "Interface Segregation - Many specific interfaces > one general",
            "DIP": "Dependency Inversion - Depend on abstractions, not implementations"
        }
        return descriptions.get(principle, principle)
    
    def _get_relevant_learning_paths(self, patterns: List[str]) -> List[Tuple[str, str]]:
        """Get learning paths relevant to these patterns."""
        paths = []
        
        # Always include SOLID for pattern work
        if patterns:
            paths.append(self.learning_paths["solid"])
        
        if "dependency_injection" in patterns:
            paths.append(self.learning_paths["dependency_injection"])
        
        # TDD is relevant for all code
        paths.append(self.learning_paths["tdd"])
        
        return paths
    
    def _extract_key_concepts(self, patterns: List[str], operation: str) -> List[Tuple[str, str]]:
        """Extract key concepts to highlight."""
        concepts = []
        
        if "dependency_injection" in patterns:
            concepts.append(("Constructor Injection", 
                           "Dependencies passed via __init__ parameters"))
        
        if "authentication" in operation:
            concepts.append(("Token Expiration", 
                           "Security: Tokens expire after set time (3600 sec = 1 hour)"))
            concepts.append(("Secret Key", 
                           "Used to sign/verify tokens. Must be kept secure in production."))
        
        if "repository" in operation:
            concepts.append(("Data Access Layer", 
                           "Separates how data is stored from how it's used"))
        
        return concepts
    
    def _get_best_practices(self, operation: str, patterns: List[str]) -> List[str]:
        """Get best practices and considerations."""
        practices = []
        
        if "authentication" in operation:
            practices.append("🔒 Use environment variables for secret keys in production")
            practices.append("⏰ Implement token refresh for better UX")
            practices.append("🔐 Always hash passwords before storing (never plain text)")
        
        if "database" in operation or "repository" in operation:
            practices.append("💾 Use connection pooling for production")
            practices.append("🔄 Implement migrations for schema changes")
            practices.append("⚡ Add indexes for frequently queried columns")
        
        if "dependency_injection" in patterns:
            practices.append("🧪 Makes unit testing easier (inject mock dependencies)")
            practices.append("🔧 Can swap implementations without changing client code")
        
        return practices
