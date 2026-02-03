"""
Next Step Generator for CORTEX ASK Mode.

Generates 3-5 intelligent, context-aware next-step suggestions for users
based on their current learning path, knowledge level, and conversation history.

Features:
- Always provides "deeper dive" as option #1
- 1-2 related concept suggestions
- Practical example option
- Context-dependent advanced/FAQ options
- Adapts to knowledge level (beginner/intermediate/advanced)

Authority: AC-EDUCATIONAL-INTERACTION-001, PHASE-22-ASK-MODE-SYSTEM.yaml
Rules: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Set, Optional
import re


class KnowledgeLevel(Enum):
    """User knowledge level classification."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class StepType(Enum):
    """Type of next-step suggestion."""
    DEEPER_DIVE = "deeper_dive"
    RELATED_CONCEPT = "related_concept"
    PRACTICAL_EXAMPLE = "practical_example"
    ADVANCED_EXTENSION = "advanced_extension"
    FAQ = "faq"
    CUSTOMIZATION = "customization"


@dataclass
class NextStepOption:
    """A single next-step suggestion."""
    number: int
    title: str
    description: str
    step_type: StepType
    estimated_time: str  # e.g., "5 min", "10 min"


@dataclass
class NextStepContext:
    """Context for generating next steps."""
    current_topic: str
    knowledge_level: KnowledgeLevel
    user_query: str
    conversation_history: List[str]


class NextStepGenerator:
    """
    Generates intelligent next-step suggestions for educational interaction.
    
    Strategy:
    1. Option #1: Always deeper dive on current topic
    2. Options #2-3: Related concepts (lateral exploration)
    3. Option #4: Practical example or hands-on exercise
    4. Option #5: Context-dependent (advanced extension, FAQ, or customization)
    
    Adapts suggestions based on:
    - User knowledge level
    - Conversation history (avoid repetition)
    - Topic type (orchestrator, MCP tool, architecture, etc.)
    - CORTEX feature availability
    """

    def __init__(self):
        """Initialize NextStepGenerator with topic mappings."""
        # Map topics to related concepts
        self._related_topics: Dict[str, List[str]] = {
            "MasterOrchestrator": ["IntentRouter", "LENSOrchestrator", "EnforcementOrchestrator"],
            "IntentRouter": ["MasterOrchestrator", "Intent Classification", "Routing Logic"],
            "TDDOrchestrator": ["Test-Driven Development", "EnforcementOrchestrator", "Testing Strategy"],
            "LENSOrchestrator": ["Code Analysis", "AST Parsing", "LENS Protocol"],
            "ChallengeEngine": ["InteractionOrchestrator", "Innovation Framework", "Disagreement Detection"],
            "MCP Tools": ["cortex_ask", "cortex_process_request", "MCP Server"],
            "cortex_ask": ["EducationalOrchestrator", "TruthVerificationEngine", "ASK Mode"],
            "Orchestrators": ["MasterOrchestrator", "Wiring Configuration", "IOrchestrator Interface"],
            "Wiring": ["wiring.yaml", "Orchestrator Registration", "GitBackedRegistry"],
            "CORTEX Architecture": ["Orchestrators", "Brain Components", "MCP Gateway"],
        }
        
        # Common beginner topics
        self._beginner_topics: Set[str] = {
            "Getting Started", "Basic Concepts", "Overview", "Introduction"
        }
        
        # Track suggested topics to avoid repetition
        self._suggested_topics: Set[str] = set()

    def generate_next_steps(self, context: NextStepContext) -> List[NextStepOption]:
        """
        Generate 3-5 intelligent next-step suggestions.
        
        Args:
            context: Current conversation context
            
        Returns:
            List of 3-5 NextStepOption objects, numbered 1-5
        """
        options: List[NextStepOption] = []
        
        # Option #1: Always deeper dive on current topic
        options.append(self._generate_deeper_dive(context))
        
        # Options #2-3: Related concepts
        related_options = self._generate_related_concepts(context, count=2)
        options.extend(related_options)
        
        # Option #4: Practical example
        options.append(self._generate_practical_example(context))
        
        # Option #5: Context-dependent (advanced/FAQ/customization)
        final_option = self._generate_context_dependent(context, len(options))
        if final_option:
            options.append(final_option)
        
        # Number the options
        for i, option in enumerate(options, start=1):
            option.number = i
        
        return options[:5]  # Cap at 5 options

    def _generate_deeper_dive(self, context: NextStepContext) -> NextStepOption:
        """Generate deeper dive option on current topic."""
        topic = context.current_topic
        
        if context.knowledge_level == KnowledgeLevel.BEGINNER:
            title = f"Learn more about {topic} basics"
            description = f"Understand the fundamentals of {topic} and how it fits into CORTEX"
            time = "5 min"
        elif context.knowledge_level == KnowledgeLevel.INTERMEDIATE:
            title = f"Explore {topic} implementation details"
            description = f"See how {topic} is implemented, including key methods and interfaces"
            time = "10 min"
        else:  # ADVANCED
            title = f"Deep dive into {topic} architecture"
            description = f"Examine {topic}'s design patterns, extension points, and advanced usage"
            time = "15 min"
        
        return NextStepOption(
            number=1,
            title=title,
            description=description,
            step_type=StepType.DEEPER_DIVE,
            estimated_time=time
        )

    def _generate_related_concepts(
        self, 
        context: NextStepContext, 
        count: int = 2
    ) -> List[NextStepOption]:
        """Generate related concept options."""
        options: List[NextStepOption] = []
        topic = context.current_topic
        
        # Get related topics
        related = self._related_topics.get(topic, [])
        
        # Filter out topics already discussed
        available = [
            t for t in related 
            if t not in context.conversation_history and t not in self._suggested_topics
        ]
        
        # If no specific mappings, infer related topics
        if not available:
            available = self._infer_related_topics(topic, context)
        
        # Generate options for up to 'count' topics
        for i, related_topic in enumerate(available[:count]):
            self._suggested_topics.add(related_topic)
            
            if context.knowledge_level == KnowledgeLevel.BEGINNER:
                title = f"What is {related_topic}?"
                description = f"Learn about {related_topic} and its role in CORTEX"
            else:
                title = f"How {related_topic} integrates with {topic}"
                description = f"Understand the relationship between {topic} and {related_topic}"
            
            options.append(NextStepOption(
                number=0,  # Will be set later
                title=title,
                description=description,
                step_type=StepType.RELATED_CONCEPT,
                estimated_time="7 min"
            ))
        
        # If we don't have enough, add a generic exploration option
        while len(options) < count:
            options.append(NextStepOption(
                number=0,
                title="Explore CORTEX components",
                description="See an overview of key CORTEX components and how they work together",
                step_type=StepType.RELATED_CONCEPT,
                estimated_time="8 min"
            ))
        
        return options[:count]

    def _generate_practical_example(self, context: NextStepContext) -> NextStepOption:
        """Generate practical example option."""
        topic = context.current_topic
        
        # Check if topic is an orchestrator
        if "Orchestrator" in topic:
            title = f"See {topic} in action"
            description = f"Walk through a real-world example of {topic} processing a request"
        elif "cortex_" in topic.lower() or "mcp" in topic.lower():
            title = f"Try using {topic}"
            description = f"Hands-on example of calling {topic} with sample data"
        else:
            title = f"Practical example: {topic}"
            description = f"See {topic} in a real CORTEX workflow with code examples"
        
        return NextStepOption(
            number=0,
            title=title,
            description=description,
            step_type=StepType.PRACTICAL_EXAMPLE,
            estimated_time="10 min"
        )

    def _generate_context_dependent(
        self, 
        context: NextStepContext,
        current_count: int
    ) -> Optional[NextStepOption]:
        """Generate context-dependent final option."""
        topic = context.current_topic
        
        # For beginners, offer FAQ
        if context.knowledge_level == KnowledgeLevel.BEGINNER:
            return NextStepOption(
                number=0,
                title=f"Common questions about {topic}",
                description=f"See frequently asked questions and troubleshooting tips for {topic}",
                step_type=StepType.FAQ,
                estimated_time="5 min"
            )
        
        # For advanced users, offer extension/customization
        elif context.knowledge_level == KnowledgeLevel.ADVANCED:
            if "Orchestrator" in topic:
                return NextStepOption(
                    number=0,
                    title=f"Extending {topic}",
                    description=f"Learn how to customize {topic} behavior or create similar orchestrators",
                    step_type=StepType.CUSTOMIZATION,
                    estimated_time="15 min"
                )
            else:
                return NextStepOption(
                    number=0,
                    title=f"Advanced {topic} patterns",
                    description=f"Explore advanced usage patterns and optimization techniques for {topic}",
                    step_type=StepType.ADVANCED_EXTENSION,
                    estimated_time="12 min"
                )
        
        # For intermediate, context-dependent
        else:
            if len(context.conversation_history) > 3:
                # User has been exploring, offer summary
                return NextStepOption(
                    number=0,
                    title="Review what we've covered",
                    description="Summary of key concepts from our conversation",
                    step_type=StepType.FAQ,
                    estimated_time="5 min"
                )
            else:
                # Offer architecture overview
                return NextStepOption(
                    number=0,
                    title="See how this fits in CORTEX architecture",
                    description=f"Understand where {topic} sits in the overall system design",
                    step_type=StepType.RELATED_CONCEPT,
                    estimated_time="8 min"
                )

    def _infer_related_topics(
        self, 
        topic: str, 
        context: NextStepContext
    ) -> List[str]:
        """Infer related topics when no explicit mapping exists."""
        related = []
        
        # If it's an orchestrator, suggest other orchestrators
        if "Orchestrator" in topic:
            related = ["Wiring Configuration", "IOrchestrator Interface", "MCP Integration"]
        
        # If it's an MCP tool, suggest tool usage
        elif "cortex_" in topic.lower():
            related = ["MCP Server", "Tool Discovery", "Other MCP Tools"]
        
        # If it's architecture, break down into components
        elif "architecture" in topic.lower():
            related = ["Orchestrators", "Brain Components", "LENS Protocol"]
        
        # Generic fallback
        else:
            related = ["CORTEX Overview", "Getting Started Guide", "Common Workflows"]
        
        return related

    def format_options(self, options: List[NextStepOption]) -> str:
        """
        Format options for display to user.
        
        Args:
            options: List of NextStepOption objects
            
        Returns:
            Formatted string with numbered options
        """
        lines = ["**What would you like to explore next?**\n"]
        
        for option in options:
            lines.append(f"{option.number}. **{option.title}** ({option.estimated_time})")
            lines.append(f"   {option.description}\n")
        
        return "\n".join(lines)


# Example usage for testing
if __name__ == "__main__":
    generator = NextStepGenerator()
    
    context = NextStepContext(
        current_topic="MasterOrchestrator",
        knowledge_level=KnowledgeLevel.BEGINNER,
        user_query="What is MasterOrchestrator?",
        conversation_history=[]
    )
    
    options = generator.generate_next_steps(context)
    print(generator.format_options(options))
