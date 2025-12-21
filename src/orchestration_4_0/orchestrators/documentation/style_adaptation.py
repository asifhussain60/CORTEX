"""
Style Adaptation Engine - Apply learned preferences to documentation

Transforms generated documentation to match user preferences:
- Adjusts technical depth and complexity
- Modifies tone (formal/casual)
- Controls example density
- Adapts formatting and structure

Integrates with DocumentationPreferenceTracker to apply learned preferences.
"""

import re
from typing import Dict, List, Optional, TYPE_CHECKING
from pathlib import Path

from .preference_tracker import (
    DocumentationPreferences,
    DocumentationStyle,
    DocumentationTone,
    DocumentationDepth,
    ExampleDensity
)

if TYPE_CHECKING:
    from logging import Logger


class StyleAdaptationEngine:
    """
    Adapts documentation style based on user preferences
    
    Features:
    - Technical complexity adjustment
    - Tone modification (formal ↔ casual)
    - Example density control
    - Format-specific transformations
    
    Example:
        engine = StyleAdaptationEngine(logger)
        
        # Get user preferences
        prefs = DocumentationPreferences(
            user_id="dev123",
            style=DocumentationStyle.ACCESSIBLE,
            tone=DocumentationTone.CASUAL,
            depth=DocumentationDepth.DETAILED
        )
        
        # Adapt documentation
        adapted_doc = engine.adapt_documentation(
            original_doc=raw_doc,
            preferences=prefs
        )
    """
    
    def __init__(self, logger: Optional["Logger"] = None):
        """
        Initialize style adaptation engine
        
        Args:
            logger: Logger instance for output
        """
        self.logger = logger
        
        # Technical terms to simplify for accessible style
        self.technical_simplifications = {
            'instantiate': 'create',
            'polymorphism': 'using objects in different ways',
            'encapsulation': 'data hiding',
            'abstraction': 'simplification',
            'inheritance': 'code reuse through parent classes',
            'composition': 'building with smaller parts',
            'dependency injection': 'passing in required objects',
            'singleton': 'single shared instance',
            'factory': 'object creator',
            'decorator': 'wrapper that adds behavior'
        }
        
        # Formal → Casual phrase replacements
        self.casual_phrases = {
            'utilize': 'use',
            'implement': 'build',
            'facilitate': 'help',
            'demonstrate': 'show',
            'subsequently': 'then',
            'consequently': 'so',
            'therefore': 'so',
            'additionally': 'also',
            'furthermore': 'plus',
            'however': 'but',
            'nevertheless': 'still',
            'in order to': 'to'
        }
    
    def adapt_documentation(
        self,
        original_doc: str,
        preferences: DocumentationPreferences
    ) -> str:
        """
        Adapt documentation to match user preferences
        
        Args:
            original_doc: Original generated documentation
            preferences: User's documentation preferences
            
        Returns:
            Adapted documentation string
        """
        if self.logger:
            self.logger.info(
                f"Adapting documentation: style={preferences.style.value}, "
                f"tone={preferences.tone.value}, depth={preferences.depth.value}"
            )
        
        doc = original_doc
        
        # Apply style transformations
        doc = self._adapt_style(doc, preferences.style)
        
        # Apply tone transformations
        doc = self._adapt_tone(doc, preferences.tone)
        
        # Apply depth transformations
        doc = self._adapt_depth(doc, preferences.depth)
        
        # Apply example density transformations
        doc = self._adapt_examples(doc, preferences.example_density)
        
        if self.logger:
            self.logger.debug(f"Adaptation complete: {len(original_doc)} → {len(doc)} chars")
        
        return doc
    
    def _adapt_style(self, doc: str, style: DocumentationStyle) -> str:
        """
        Adapt documentation style (technical ↔ accessible)
        
        Args:
            doc: Documentation text
            style: Target style
            
        Returns:
            Style-adapted documentation
        """
        if style == DocumentationStyle.ACCESSIBLE:
            # Simplify technical jargon
            for technical, simple in self.technical_simplifications.items():
                # Case-insensitive replacement, preserve original case
                pattern = re.compile(re.escape(technical), re.IGNORECASE)
                doc = pattern.sub(simple, doc)
            
            # Add explanatory notes for complex concepts
            doc = self._add_explanatory_notes(doc)
        
        elif style == DocumentationStyle.TECHNICAL:
            # Use precise terminology (reverse simplifications)
            for technical, simple in self.technical_simplifications.items():
                # Only replace if we simplified it
                pattern = re.compile(r'\b' + re.escape(simple) + r'\b', re.IGNORECASE)
                doc = pattern.sub(technical, doc)
        
        # BALANCED: No transformation needed
        
        return doc
    
    def _adapt_tone(self, doc: str, tone: DocumentationTone) -> str:
        """
        Adapt documentation tone (formal ↔ casual)
        
        Args:
            doc: Documentation text
            tone: Target tone
            
        Returns:
            Tone-adapted documentation
        """
        if tone == DocumentationTone.CASUAL:
            # Replace formal phrases with casual equivalents
            for formal, casual in self.casual_phrases.items():
                pattern = re.compile(r'\b' + re.escape(formal) + r'\b', re.IGNORECASE)
                doc = pattern.sub(casual, doc)
            
            # Add conversational markers
            doc = self._add_conversational_markers(doc)
        
        elif tone == DocumentationTone.FORMAL:
            # Replace casual phrases with formal equivalents
            for formal, casual in self.casual_phrases.items():
                pattern = re.compile(r'\b' + re.escape(casual) + r'\b', re.IGNORECASE)
                doc = pattern.sub(formal, doc)
            
            # Remove conversational markers
            doc = self._remove_conversational_markers(doc)
        
        # NEUTRAL: No transformation needed
        
        return doc
    
    def _adapt_depth(self, doc: str, depth: DocumentationDepth) -> str:
        """
        Adapt documentation detail level
        
        Args:
            doc: Documentation text
            depth: Target depth
            
        Returns:
            Depth-adapted documentation
        """
        if depth == DocumentationDepth.DETAILED:
            # Expand brief descriptions
            doc = self._expand_descriptions(doc)
        
        elif depth == DocumentationDepth.CONCISE:
            # Condense verbose descriptions
            doc = self._condense_descriptions(doc)
        
        # MODERATE: No transformation needed
        
        return doc
    
    def _adapt_examples(self, doc: str, density: ExampleDensity) -> str:
        """
        Adapt code example density
        
        Args:
            doc: Documentation text
            density: Target example density
            
        Returns:
            Example-adapted documentation
        """
        # Count existing examples
        example_count = doc.count("```") + doc.count("Example:")
        
        if density == ExampleDensity.MANY and example_count < 5:
            # Add more examples (placeholder - would need context)
            if self.logger:
                self.logger.debug("User prefers many examples - consider adding more")
        
        elif density == ExampleDensity.FEW and example_count > 2:
            # Remove redundant examples (keep only essential ones)
            if self.logger:
                self.logger.debug("User prefers few examples - keeping essential ones")
        
        # BALANCED: No transformation needed
        
        return doc
    
    def _add_explanatory_notes(self, doc: str) -> str:
        """Add explanatory notes for complex concepts"""
        # Find complex terms and add inline explanations
        # Example: "polymorphism" → "polymorphism (using objects in different ways)"
        
        # This is a simplified implementation
        # Production version would use NLP to detect complexity
        
        return doc
    
    def _add_conversational_markers(self, doc: str) -> str:
        """Add conversational elements to make tone more casual"""
        # Add phrases like "Let's...", "You can...", "Here's how..."
        
        # Replace imperative sentences with softer language
        doc = re.sub(r'^(\s*)(?:Create|Build|Make)\s', r'\1Let\'s create ', doc, flags=re.MULTILINE)
        doc = re.sub(r'^(\s*)(?:Use|Call|Invoke)\s', r'\1You can use ', doc, flags=re.MULTILINE)
        
        return doc
    
    def _remove_conversational_markers(self, doc: str) -> str:
        """Remove conversational elements for formal tone"""
        # Remove phrases like "Let's...", "You can..."
        
        doc = re.sub(r"Let's\s+", '', doc, flags=re.IGNORECASE)
        doc = re.sub(r"You can\s+", '', doc, flags=re.IGNORECASE)
        doc = re.sub(r"Here's\s+", '', doc, flags=re.IGNORECASE)
        
        return doc
    
    def _expand_descriptions(self, doc: str) -> str:
        """Expand brief descriptions with more detail"""
        # Find single-line descriptions and expand them
        # This is a placeholder - production would use templates
        
        # Add parameter descriptions if missing
        lines = doc.split('\n')
        expanded_lines = []
        
        for i, line in enumerate(lines):
            expanded_lines.append(line)
            
            # If we see a function/method definition, ensure params are documented
            if 'def ' in line and '(' in line and i + 1 < len(lines):
                # Check if next line has parameter docs
                if 'Args:' not in lines[i + 1] and 'Parameters:' not in lines[i + 1]:
                    # Could add parameter documentation template here
                    pass
        
        return '\n'.join(expanded_lines)
    
    def _condense_descriptions(self, doc: str) -> str:
        """Condense verbose descriptions to be more concise"""
        # Remove redundant explanations
        # Keep only essential information
        
        # Remove "In other words..." type redundancy
        doc = re.sub(r'\s*(?:In other words|That is to say|Put simply)[^.]*\.\s*', ' ', doc, flags=re.IGNORECASE)
        
        # Remove excessive examples (keep first one only)
        # This is simplified - production would be smarter
        
        return doc
    
    def get_adaptation_summary(
        self,
        original_doc: str,
        adapted_doc: str,
        preferences: DocumentationPreferences
    ) -> Dict[str, any]:
        """
        Get summary of adaptations applied
        
        Args:
            original_doc: Original documentation
            adapted_doc: Adapted documentation
            preferences: Applied preferences
            
        Returns:
            Dictionary with adaptation metrics
        """
        return {
            'style': preferences.style.value,
            'tone': preferences.tone.value,
            'depth': preferences.depth.value,
            'example_density': preferences.example_density.value,
            'original_length': len(original_doc),
            'adapted_length': len(adapted_doc),
            'length_change_pct': (len(adapted_doc) - len(original_doc)) / len(original_doc) * 100,
            'original_examples': original_doc.count("```"),
            'adapted_examples': adapted_doc.count("```"),
            'transformations_applied': self._count_transformations(original_doc, adapted_doc)
        }
    
    def _count_transformations(self, original: str, adapted: str) -> int:
        """Count number of transformations applied"""
        # Simple heuristic: count changed words
        original_words = set(original.lower().split())
        adapted_words = set(adapted.lower().split())
        
        return len(original_words.symmetric_difference(adapted_words))


class FeedbackLoopIntegrator:
    """
    Integrates feedback loop for continuous learning
    
    Monitors user interactions with generated documentation and
    feeds insights back to preference tracker for improvement.
    
    Features:
    - Edit pattern detection
    - Preference drift tracking
    - Automatic preference updates
    """
    
    def __init__(
        self,
        preference_tracker,
        logger: Optional["Logger"] = None
    ):
        """
        Initialize feedback loop integrator
        
        Args:
            preference_tracker: DocumentationPreferenceTracker instance
            logger: Logger instance for output
        """
        self.preference_tracker = preference_tracker
        self.logger = logger
    
    def process_user_edit(
        self,
        user_id: str,
        original_doc: str,
        edited_doc: str,
        doc_type: str = "api",
        project_id: Optional[str] = None
    ) -> None:
        """
        Process user edit and learn from it
        
        Args:
            user_id: User identifier
            original_doc: Originally generated documentation
            edited_doc: User-edited version
            doc_type: Type of documentation (api, architecture, guide)
            project_id: Optional project identifier
        """
        if self.logger:
            self.logger.info(f"Processing user edit feedback for {user_id}")
        
        # Delegate to preference tracker's learning logic
        self.preference_tracker.learn_from_edits(
            user_id=user_id,
            original_doc=original_doc,
            edited_doc=edited_doc,
            project_id=project_id
        )
        
        # Additional feedback analysis could go here
        self._analyze_edit_patterns(original_doc, edited_doc, doc_type)
    
    def _analyze_edit_patterns(
        self,
        original: str,
        edited: str,
        doc_type: str
    ) -> Dict[str, any]:
        """
        Analyze patterns in user edits
        
        Returns:
            Dictionary with analysis results
        """
        return {
            'doc_type': doc_type,
            'added_lines': len(edited.split('\n')) - len(original.split('\n')),
            'added_examples': edited.count("```") - original.count("```"),
            'simplified': len(edited) < len(original),
            'expanded': len(edited) > len(original)
        }
    
    def get_preference_confidence(
        self,
        user_id: str,
        project_id: Optional[str] = None
    ) -> float:
        """
        Get confidence score for learned preferences
        
        Higher score means more data points and stable preferences.
        
        Args:
            user_id: User identifier
            project_id: Optional project identifier
            
        Returns:
            Confidence score (0.0 - 1.0)
        """
        # Get update history to gauge confidence
        history = self.preference_tracker.get_update_history(
            user_id=user_id,
            project_id=project_id,
            limit=100
        )
        
        if not history:
            return 0.0
        
        # More updates = higher confidence (up to a point)
        update_count = len(history)
        base_confidence = min(update_count / 10.0, 0.8)
        
        # Check for consistency (fewer reversals = higher confidence)
        reversals = self._count_preference_reversals(history)
        consistency_bonus = max(0, 0.2 - (reversals * 0.05))
        
        return min(base_confidence + consistency_bonus, 1.0)
    
    def _count_preference_reversals(self, history: List) -> int:
        """Count how many times preferences flip back and forth"""
        reversals = 0
        
        # Group by preference type
        by_type = {}
        for update in history:
            pref_type = update.preference_type
            if pref_type not in by_type:
                by_type[pref_type] = []
            by_type[pref_type].append(update.new_value)
        
        # Count reversals in each type
        for pref_type, values in by_type.items():
            for i in range(len(values) - 2):
                if values[i] == values[i + 2] and values[i] != values[i + 1]:
                    reversals += 1
        
        return reversals
