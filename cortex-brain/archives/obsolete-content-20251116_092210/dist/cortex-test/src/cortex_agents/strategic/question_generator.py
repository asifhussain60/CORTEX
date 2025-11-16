"""
Question Generator Utility (CORTEX 2.1)

Generates high-quality clarifying questions for interactive planning.
Prioritizes questions by importance and adapts to user expertise level.

Part of CORTEX 2.1 Interactive Planning enhancement.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import re
import logging


# Re-export types from interactive_planner for convenience
from src.cortex_agents.strategic.interactive_planner import (
    Question,
    QuestionType
)


class QuestionPriority:
    """Question priority levels (1-5)."""
    CRITICAL = 5      # Must answer (blocking decisions)
    HIGH = 4          # Important (affects architecture)
    MEDIUM = 3        # Helpful (improves plan quality)
    LOW = 2           # Optional (nice-to-have details)
    TRIVIAL = 1       # Skip if time limited


class QuestionCategory:
    """Categories of questions."""
    TECHNICAL_CHOICE = "technical_choice"    # Which tech/approach
    SAFETY = "safety"                         # Risk mitigation
    COMPATIBILITY = "compatibility"           # Backwards compatibility
    TESTING = "testing"                       # Test requirements
    DEPLOYMENT = "deployment"                 # Deployment strategy
    SECURITY = "security"                     # Security concerns
    PERFORMANCE = "performance"               # Performance requirements
    UX = "user_experience"                    # User experience
    SCOPE = "scope"                           # Feature scope


class QuestionTemplate:
    """
    Template for generating context-aware questions.
    
    Templates adapt to detected keywords and context to generate
    relevant, specific questions for the user's request.
    """
    
    def __init__(
        self,
        template_id: str,
        triggers: List[str],
        question_text: str,
        question_type: QuestionType,
        options: List[str],
        default: str,
        priority: int,
        category: str,
        dependencies: Optional[List[str]] = None
    ):
        """
        Initialize question template.
        
        Args:
            template_id: Unique template identifier
            triggers: Keywords that activate this template
            question_text: Question text (may include {placeholders})
            question_type: Type of question
            options: Available options for multiple choice
            default: Default answer
            priority: Question priority (1-5)
            category: Question category
            dependencies: IDs of questions this depends on
        """
        self.template_id = template_id
        self.triggers = [t.lower() for t in triggers]
        self.question_text = question_text
        self.question_type = question_type
        self.options = options
        self.default = default
        self.priority = priority
        self.category = category
        self.dependencies = dependencies or []
    
    def matches(self, request: str) -> bool:
        """Check if request triggers this template."""
        request_lower = request.lower()
        return any(trigger in request_lower for trigger in self.triggers)
    
    def generate(self, context: Dict[str, Any]) -> Question:
        """Generate question from template."""
        # Format question text with context
        question_text = self.question_text.format(**context) if context else self.question_text
        
        return Question(
            text=question_text,
            type=self.question_type,
            options=self.options,
            default=self.default,
            priority=self.priority,
            context={
                "category": self.category,
                "template_id": self.template_id,
                "dependencies": self.dependencies
            },
            id=self.template_id
        )


class QuestionGenerator:
    """
    Generates clarifying questions for interactive planning.
    
    Features:
    - Template-based question generation
    - Context-aware question adaptation
    - Priority-based question ordering
    - Dependency-aware question filtering
    - User expertise level adaptation
    
    Example:
        generator = QuestionGenerator()
        questions = generator.generate(
            request="Refactor authentication",
            context={"expertise": "intermediate"},
            max_questions=5
        )
    """
    
    def __init__(self):
        """Initialize Question Generator with templates."""
        self.logger = logging.getLogger(__name__)
        self.templates = self._build_templates()
    
    def generate(
        self,
        request: str,
        context: Dict[str, Any],
        max_questions: int = 5
    ) -> List[Question]:
        """
        Generate clarifying questions for a request.
        
        Args:
            request: User's request text
            context: Additional context (expertise, preferences, etc.)
            max_questions: Maximum number of questions to generate
        
        Returns:
            List of Question objects, prioritized and filtered
        """
        # Find matching templates
        matching_templates = [
            template for template in self.templates
            if template.matches(request)
        ]
        
        self.logger.info(f"Found {len(matching_templates)} matching templates for request")
        
        # Generate questions from templates
        questions = [
            template.generate(context)
            for template in matching_templates
        ]
        
        # Filter by dependencies
        questions = self._filter_by_dependencies(questions, context)
        
        # Adapt to user expertise
        questions = self._adapt_to_expertise(questions, context.get("expertise", "beginner"))
        
        # Sort by priority (highest first)
        questions.sort(key=lambda q: q.priority, reverse=True)
        
        # Limit to max_questions
        return questions[:max_questions]
    
    def _build_templates(self) -> List[QuestionTemplate]:
        """Build library of question templates."""
        return [
            # Authentication questions
            QuestionTemplate(
                template_id="auth_strategy",
                triggers=["auth", "authentication", "login", "signin"],
                question_text="What authentication strategy should I use?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["OAuth 2.0", "JWT tokens", "Session-based", "Other"],
                default="JWT tokens",
                priority=QuestionPriority.CRITICAL,
                category=QuestionCategory.TECHNICAL_CHOICE
            ),
            
            QuestionTemplate(
                template_id="refresh_tokens",
                triggers=["auth", "authentication", "jwt", "token"],
                question_text="Should I add refresh token support?",
                question_type=QuestionType.YES_NO,
                options=["Yes", "No"],
                default="Yes",
                priority=QuestionPriority.HIGH,
                category=QuestionCategory.TECHNICAL_CHOICE,
                dependencies=["auth_strategy"]
            ),
            
            QuestionTemplate(
                template_id="social_login",
                triggers=["auth", "authentication", "login", "oauth"],
                question_text="Should I support social login (OAuth providers)?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["Yes (Google, GitHub, Facebook)", "Yes (custom providers)", "No"],
                default="No",
                priority=QuestionPriority.MEDIUM,
                category=QuestionCategory.TECHNICAL_CHOICE,
                dependencies=["auth_strategy"]
            ),
            
            # Refactoring questions
            QuestionTemplate(
                template_id="preserve_schema",
                triggers=["refactor", "redesign", "change", "modify"],
                question_text="Should I preserve the existing data schema?",
                question_type=QuestionType.YES_NO,
                options=["Yes (safer)", "No (redesign)"],
                default="Yes (safer)",
                priority=QuestionPriority.HIGH,
                category=QuestionCategory.SAFETY
            ),
            
            QuestionTemplate(
                template_id="backward_compat",
                triggers=["refactor", "update", "change", "modify", "upgrade"],
                question_text="Do you need backward compatibility with existing code?",
                question_type=QuestionType.YES_NO,
                options=["Yes", "No"],
                default="Yes",
                priority=QuestionPriority.HIGH,
                category=QuestionCategory.COMPATIBILITY
            ),
            
            # Testing questions
            QuestionTemplate(
                template_id="test_coverage",
                triggers=["test", "testing", "tdd", "implement", "create", "add"],
                question_text="What level of test coverage do you need?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=[
                    "Comprehensive (unit + integration + e2e)",
                    "Standard (unit + integration)",
                    "Basic (unit tests only)",
                    "None"
                ],
                default="Standard (unit + integration)",
                priority=QuestionPriority.MEDIUM,
                category=QuestionCategory.TESTING
            ),
            
            # Deployment questions
            QuestionTemplate(
                template_id="deployment_strategy",
                triggers=["deploy", "release", "rollout", "implement", "production"],
                question_text="How should this be deployed?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=[
                    "Gradual rollout (safest)",
                    "Feature flag",
                    "All at once",
                    "Not sure"
                ],
                default="Gradual rollout (safest)",
                priority=QuestionPriority.MEDIUM,
                category=QuestionCategory.DEPLOYMENT
            ),
            
            # Security questions
            QuestionTemplate(
                template_id="security_review",
                triggers=["auth", "authentication", "security", "api", "endpoint"],
                question_text="Should I include security review/audit steps?",
                question_type=QuestionType.YES_NO,
                options=["Yes", "No"],
                default="Yes",
                priority=QuestionPriority.HIGH,
                category=QuestionCategory.SECURITY
            ),
            
            # Performance questions
            QuestionTemplate(
                template_id="performance_requirements",
                triggers=["performance", "speed", "optimize", "scale", "load"],
                question_text="What are your performance requirements?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=[
                    "High performance critical",
                    "Standard performance acceptable",
                    "Performance not critical",
                    "Not sure"
                ],
                default="Standard performance acceptable",
                priority=QuestionPriority.MEDIUM,
                category=QuestionCategory.PERFORMANCE
            ),
            
            # Database questions
            QuestionTemplate(
                template_id="database_migration",
                triggers=["database", "db", "schema", "migration", "refactor"],
                question_text="Should I create database migration scripts?",
                question_type=QuestionType.YES_NO,
                options=["Yes", "No"],
                default="Yes",
                priority=QuestionPriority.HIGH,
                category=QuestionCategory.SAFETY
            ),
            
            # API questions
            QuestionTemplate(
                template_id="api_versioning",
                triggers=["api", "endpoint", "rest", "graphql"],
                question_text="Do you need API versioning?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=[
                    "Yes (v1, v2, etc.)",
                    "Yes (via headers)",
                    "No",
                    "Not sure"
                ],
                default="Yes (v1, v2, etc.)",
                priority=QuestionPriority.MEDIUM,
                category=QuestionCategory.COMPATIBILITY
            ),
            
            # Documentation questions
            QuestionTemplate(
                template_id="documentation",
                triggers=["implement", "create", "add", "build"],
                question_text="Should I generate documentation?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=[
                    "Yes (API docs + user guide)",
                    "Yes (API docs only)",
                    "Yes (inline comments only)",
                    "No"
                ],
                default="Yes (API docs + user guide)",
                priority=QuestionPriority.LOW,
                category=QuestionCategory.TECHNICAL_CHOICE
            ),
        ]
    
    def _filter_by_dependencies(
        self,
        questions: List[Question],
        context: Dict[str, Any]
    ) -> List[Question]:
        """
        Filter questions based on dependencies.
        
        If a question depends on another that hasn't been answered,
        it may be skipped or deferred.
        
        Args:
            questions: List of questions to filter
            context: Context with answered questions
        
        Returns:
            Filtered list of questions
        """
        answered_ids = set(context.get("answered_question_ids", []))
        
        filtered = []
        for question in questions:
            dependencies = question.context.get("dependencies", [])
            
            # If no dependencies, include
            if not dependencies:
                filtered.append(question)
                continue
            
            # If dependencies answered, include
            if all(dep in answered_ids for dep in dependencies):
                filtered.append(question)
                continue
            
            # If dependencies not answered, skip for now
            self.logger.debug(
                f"Skipping question '{question.id}' - dependencies not met: {dependencies}"
            )
        
        return filtered
    
    def _adapt_to_expertise(
        self,
        questions: List[Question],
        expertise: str
    ) -> List[Question]:
        """
        Adapt questions to user's expertise level.
        
        Args:
            questions: List of questions to adapt
            expertise: User expertise ("beginner", "intermediate", "expert")
        
        Returns:
            Adapted list of questions
        """
        # Beginners: Ask more safety/compatibility questions
        if expertise == "beginner":
            for question in questions:
                if question.context.get("category") in [
                    QuestionCategory.SAFETY,
                    QuestionCategory.COMPATIBILITY
                ]:
                    question.priority = min(5, question.priority + 1)
        
        # Experts: Skip trivial questions, focus on technical choices
        elif expertise == "expert":
            # Remove trivial questions
            questions = [q for q in questions if q.priority > QuestionPriority.TRIVIAL]
            
            # Boost technical choice questions
            for question in questions:
                if question.context.get("category") == QuestionCategory.TECHNICAL_CHOICE:
                    question.priority = min(5, question.priority + 1)
        
        return questions


# Helper function for standalone use
def generate_questions(
    request: str,
    context: Optional[Dict[str, Any]] = None,
    max_questions: int = 5
) -> List[Question]:
    """
    Convenience function to generate questions.
    
    Args:
        request: User's request text
        context: Additional context
        max_questions: Maximum questions to generate
    
    Returns:
        List of Question objects
    """
    generator = QuestionGenerator()
    return generator.generate(
        request=request,
        context=context or {},
        max_questions=max_questions
    )
