"""
Documentation Preference Tracker - Learn and store user documentation preferences

Tracks user preferences for documentation generation including:
- Style: technical vs accessible
- Tone: formal vs casual
- Depth: detailed vs concise
- Format: markdown vs html vs restructuredtext
- Example density: many vs few examples

Stores preferences in Tier 2 knowledge graph for persistence and learning.

Integration with AgentLearningEngine:
- Tracks which documentation strategies work best for different module types
- Learns patterns from generation success/failure
- Recommends optimal documentation approaches based on context
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, TYPE_CHECKING
import json
import time

if TYPE_CHECKING:
    from logging import Logger
    from ...learning.agent_learning_engine import AgentLearningEngine


class DocumentationStyle(Enum):
    """Documentation writing style preference"""
    TECHNICAL = "technical"  # Dense, precise, assumes expert knowledge
    ACCESSIBLE = "accessible"  # Clear, explanatory, beginner-friendly
    BALANCED = "balanced"  # Mix of both


class DocumentationTone(Enum):
    """Documentation tone preference"""
    FORMAL = "formal"  # Professional, academic
    CASUAL = "casual"  # Conversational, friendly
    NEUTRAL = "neutral"  # Balanced tone


class DocumentationDepth(Enum):
    """Level of detail preference"""
    DETAILED = "detailed"  # Comprehensive, exhaustive
    CONCISE = "concise"  # Brief, to-the-point
    MODERATE = "moderate"  # Balanced detail level


class ExampleDensity(Enum):
    """Preference for code examples"""
    MANY = "many"  # Example for every concept
    FEW = "few"  # Minimal examples
    BALANCED = "balanced"  # Strategic examples


@dataclass
class DocumentationPreferences:
    """User's documentation generation preferences"""
    user_id: str
    project_id: Optional[str] = None
    style: DocumentationStyle = DocumentationStyle.BALANCED
    tone: DocumentationTone = DocumentationTone.NEUTRAL
    depth: DocumentationDepth = DocumentationDepth.MODERATE
    example_density: ExampleDensity = ExampleDensity.BALANCED
    preferred_format: str = "markdown"
    include_diagrams: bool = True
    include_toc: bool = True
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert preferences to dictionary"""
        return {
            'user_id': self.user_id,
            'project_id': self.project_id,
            'style': self.style.value,
            'tone': self.tone.value,
            'depth': self.depth.value,
            'example_density': self.example_density.value,
            'preferred_format': self.preferred_format,
            'include_diagrams': self.include_diagrams,
            'include_toc': self.include_toc,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DocumentationPreferences':
        """Create preferences from dictionary"""
        return cls(
            user_id=data['user_id'],
            project_id=data.get('project_id'),
            style=DocumentationStyle(data.get('style', 'balanced')),
            tone=DocumentationTone(data.get('tone', 'neutral')),
            depth=DocumentationDepth(data.get('depth', 'moderate')),
            example_density=ExampleDensity(data.get('example_density', 'balanced')),
            preferred_format=data.get('preferred_format', 'markdown'),
            include_diagrams=data.get('include_diagrams', True),
            include_toc=data.get('include_toc', True),
            created_at=data.get('created_at', time.time()),
            updated_at=data.get('updated_at', time.time())
        )


@dataclass
class PreferenceUpdate:
    """Record of a preference change with reason"""
    preference_type: str  # "style", "tone", "depth", etc.
    old_value: str
    new_value: str
    reason: str  # "user_edit", "feedback", "auto_learning"
    timestamp: float = field(default_factory=time.time)


class DocumentationPreferenceTracker:
    """
    Tracks and manages user documentation preferences
    
    Features:
    - Per-user and per-project preferences
    - Learning from user feedback and edits
    - Preference history and evolution tracking
    - Integration with Tier 2 knowledge graph
    - AgentLearningEngine integration for strategy recommendations
    
    Example:
        from src.orchestration_4_0.learning.agent_learning_engine import AgentLearningEngine
        
        learning_engine = AgentLearningEngine()
        tracker = DocumentationPreferenceTracker(logger, learning_engine=learning_engine)
        
        # Get or create preferences for user
        prefs = tracker.get_preferences(user_id="dev123")
        print(f"Style: {prefs.style.value}")
        
        # Update based on feedback
        tracker.update_preference(
            user_id="dev123",
            preference_type="style",
            new_value="technical",
            reason="user_feedback"
        )
        
        # Learn from edit patterns
        tracker.learn_from_edits(
            user_id="dev123",
            original_doc="...",
            edited_doc="..."
        )
        
        # Record successful documentation generation for learning
        tracker.record_generation_success(
            user_id="dev123",
            module_type="api_reference",
            context={'complexity': 'high', 'file_count': 10},
            quality_score=8.5
        )
    """
    
    def __init__(
        self,
        logger: Optional["Logger"] = None,
        storage_path: Optional[Path] = None,
        learning_engine: Optional["AgentLearningEngine"] = None
    ):
        """
        Initialize preference tracker
        
        Args:
            logger: Logger instance for output
            storage_path: Path to store preferences (defaults to tier2/)
            learning_engine: Optional AgentLearningEngine for pattern learning
        """
        self.logger = logger
        self.storage_path = storage_path or Path("cortex-brain/tier2/documentation_preferences.json")
        self.learning_engine = learning_engine
        
        # In-memory cache of preferences
        self._preferences_cache: Dict[str, DocumentationPreferences] = {}
        
        # Preference update history
        self._update_history: Dict[str, List[PreferenceUpdate]] = {}
        
        # Load existing preferences
        self._load_preferences()
        
        if self.learning_engine and self.logger:
            self.logger.info("🧠 AgentLearningEngine integration enabled for documentation preferences")
    
    def _load_preferences(self) -> None:
        """Load preferences from storage"""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                
                # Load preferences
                for user_key, pref_data in data.get('preferences', {}).items():
                    self._preferences_cache[user_key] = DocumentationPreferences.from_dict(pref_data)
                
                # Load update history
                for user_key, updates_data in data.get('update_history', {}).items():
                    self._update_history[user_key] = [
                        PreferenceUpdate(**update) for update in updates_data
                    ]
                
                if self.logger:
                    self.logger.info(
                        f"Loaded {len(self._preferences_cache)} preference profiles"
                    )
            
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"Failed to load preferences: {e}")
    
    def _save_preferences(self) -> None:
        """Save preferences to storage"""
        try:
            # Ensure directory exists
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Prepare data
            data = {
                'preferences': {
                    user_key: prefs.to_dict()
                    for user_key, prefs in self._preferences_cache.items()
                },
                'update_history': {
                    user_key: [asdict(update) for update in updates]
                    for user_key, updates in self._update_history.items()
                }
            }
            
            # Write atomically
            temp_path = self.storage_path.with_suffix('.tmp')
            with open(temp_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            temp_path.replace(self.storage_path)
            
            if self.logger:
                self.logger.debug(f"Saved preferences to {self.storage_path}")
        
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to save preferences: {e}")
    
    def get_preferences(
        self,
        user_id: str,
        project_id: Optional[str] = None
    ) -> DocumentationPreferences:
        """
        Get documentation preferences for user/project
        
        Args:
            user_id: User identifier
            project_id: Optional project identifier for project-specific prefs
            
        Returns:
            DocumentationPreferences (creates default if not found)
        """
        # Build cache key
        cache_key = f"{user_id}:{project_id}" if project_id else user_id
        
        # Return cached if exists
        if cache_key in self._preferences_cache:
            return self._preferences_cache[cache_key]
        
        # Create default preferences
        prefs = DocumentationPreferences(
            user_id=user_id,
            project_id=project_id
        )
        
        self._preferences_cache[cache_key] = prefs
        self._save_preferences()
        
        if self.logger:
            self.logger.info(f"Created default preferences for {cache_key}")
        
        return prefs
    
    def update_preference(
        self,
        user_id: str,
        preference_type: str,
        new_value: str,
        reason: str = "user_feedback",
        project_id: Optional[str] = None
    ) -> None:
        """
        Update a specific preference
        
        Args:
            user_id: User identifier
            preference_type: Type of preference (style, tone, depth, etc.)
            new_value: New value for the preference
            reason: Reason for update (user_feedback, auto_learning, etc.)
            project_id: Optional project identifier
        """
        # Get existing preferences
        prefs = self.get_preferences(user_id, project_id)
        cache_key = f"{user_id}:{project_id}" if project_id else user_id
        
        # Record old value
        old_value = getattr(prefs, preference_type, None)
        if old_value and hasattr(old_value, 'value'):
            old_value = old_value.value
        else:
            old_value = str(old_value)
        
        # Update preference
        try:
            if preference_type == 'style':
                prefs.style = DocumentationStyle(new_value)
            elif preference_type == 'tone':
                prefs.tone = DocumentationTone(new_value)
            elif preference_type == 'depth':
                prefs.depth = DocumentationDepth(new_value)
            elif preference_type == 'example_density':
                prefs.example_density = ExampleDensity(new_value)
            elif preference_type == 'preferred_format':
                prefs.preferred_format = new_value
            elif preference_type == 'include_diagrams':
                prefs.include_diagrams = new_value.lower() == 'true'
            elif preference_type == 'include_toc':
                prefs.include_toc = new_value.lower() == 'true'
            else:
                raise ValueError(f"Unknown preference type: {preference_type}")
            
            prefs.updated_at = time.time()
            
            # Record update in history
            if cache_key not in self._update_history:
                self._update_history[cache_key] = []
            
            self._update_history[cache_key].append(PreferenceUpdate(
                preference_type=preference_type,
                old_value=old_value,
                new_value=new_value,
                reason=reason
            ))
            
            # Save to storage
            self._save_preferences()
            
            if self.logger:
                self.logger.info(
                    f"Updated {preference_type} for {cache_key}: {old_value} → {new_value} ({reason})"
                )
        
        except ValueError as e:
            if self.logger:
                self.logger.error(f"Invalid preference value: {e}")
    
    def learn_from_edits(
        self,
        user_id: str,
        original_doc: str,
        edited_doc: str,
        project_id: Optional[str] = None
    ) -> None:
        """
        Learn preferences from user edits to generated documentation
        
        Analyzes the difference between original and edited docs to infer
        preference changes (e.g., user adds more examples → increase example_density)
        
        Args:
            user_id: User identifier
            original_doc: Originally generated documentation
            edited_doc: User-edited documentation
            project_id: Optional project identifier
        """
        if self.logger:
            self.logger.info(f"Learning from edits for user {user_id}")
        
        # Simple heuristics for learning (can be enhanced with NLP)
        
        # Check if user added more examples
        original_examples = original_doc.count("```") + original_doc.count("Example:")
        edited_examples = edited_doc.count("```") + edited_doc.count("Example:")
        
        if edited_examples > original_examples * 1.5:
            # User wants more examples
            prefs = self.get_preferences(user_id, project_id)
            if prefs.example_density != ExampleDensity.MANY:
                self.update_preference(
                    user_id, "example_density", "many",
                    reason="auto_learning", project_id=project_id
                )
        
        # Check if user simplified language (removed technical jargon)
        technical_words = ["instantiate", "polymorphism", "encapsulation", "abstraction"]
        original_tech_count = sum(original_doc.lower().count(word) for word in technical_words)
        edited_tech_count = sum(edited_doc.lower().count(word) for word in technical_words)
        
        if edited_tech_count < original_tech_count * 0.5 and original_tech_count > 0:
            # User prefers accessible style
            prefs = self.get_preferences(user_id, project_id)
            if prefs.style != DocumentationStyle.ACCESSIBLE:
                self.update_preference(
                    user_id, "style", "accessible",
                    reason="auto_learning", project_id=project_id
                )
        
        # Check if user expanded content (wants more detail)
        if len(edited_doc) > len(original_doc) * 1.3:
            prefs = self.get_preferences(user_id, project_id)
            if prefs.depth != DocumentationDepth.DETAILED:
                self.update_preference(
                    user_id, "depth", "detailed",
                    reason="auto_learning", project_id=project_id
                )
        
        # Check if user condensed content (wants conciseness)
        if len(edited_doc) < len(original_doc) * 0.7:
            prefs = self.get_preferences(user_id, project_id)
            if prefs.depth != DocumentationDepth.CONCISE:
                self.update_preference(
                    user_id, "depth", "concise",
                    reason="auto_learning", project_id=project_id
                )
    
    def get_update_history(
        self,
        user_id: str,
        project_id: Optional[str] = None,
        limit: int = 10
    ) -> List[PreferenceUpdate]:
        """
        Get preference update history for user
        
        Args:
            user_id: User identifier
            project_id: Optional project identifier
            limit: Maximum number of updates to return
            
        Returns:
            List of recent PreferenceUpdates (newest first)
        """
        cache_key = f"{user_id}:{project_id}" if project_id else user_id
        
        if cache_key not in self._update_history:
            return []
        
        # Return most recent updates
        return sorted(
            self._update_history[cache_key],
            key=lambda u: u.timestamp,
            reverse=True
        )[:limit]
    
    def save_preferences(self) -> None:
        """Public method to save preferences to storage"""
        self._save_preferences()
    
    def get_preference_summary(
        self,
        user_id: str,
        project_id: Optional[str] = None
    ) -> str:
        """
        Get human-readable summary of user preferences
        
        Args:
            user_id: User identifier
            project_id: Optional project identifier
            
        Returns:
            String summary of preferences
        """
        prefs = self.get_preferences(user_id, project_id)
        
        summary_parts = [
            f"Documentation Preferences for {user_id}",
            f"Style: {prefs.style.value}",
            f"Tone: {prefs.tone.value}",
            f"Depth: {prefs.depth.value}",
            f"Example Density: {prefs.example_density.value}",
            f"Format: {prefs.preferred_format}",
            f"Diagrams: {'Yes' if prefs.include_diagrams else 'No'}",
            f"Table of Contents: {'Yes' if prefs.include_toc else 'No'}"
        ]
        
        if project_id:
            summary_parts.insert(1, f"Project: {project_id}")
        
        return "\n".join(summary_parts)
    
    def record_generation_success(
        self,
        user_id: str,
        module_type: str,
        context: Dict[str, Any],
        quality_score: float,
        execution_time_seconds: float = 0.0,
        project_id: Optional[str] = None
    ) -> None:
        """
        Record successful documentation generation for agent learning.
        
        Integrates with AgentLearningEngine to track which documentation
        strategies work best for different module types and contexts.
        
        Args:
            user_id: User identifier
            module_type: Type of module documented (api_reference, guide, etc.)
            context: Generation context (complexity, file_count, etc.)
            quality_score: Quality score (1.0-10.0)
            execution_time_seconds: Time taken to generate docs
            project_id: Optional project identifier
        """
        if not self.learning_engine:
            if self.logger:
                self.logger.debug("AgentLearningEngine not available - skipping pattern recording")
            return
        
        # Get current user preferences
        prefs = self.get_preferences(user_id, project_id)
        
        # Build strategy context combining preferences and generation context
        strategy_context = {
            'style': prefs.style.value,
            'tone': prefs.tone.value,
            'depth': prefs.depth.value,
            'example_density': prefs.example_density.value,
            'module_type': module_type,
            **context
        }
        
        # Create mock evaluation result (in real usage, would come from evaluator)
        from ...frameworks.agent_evaluator import EvaluationResult, EvaluationCategory
        from ...learning.agent_learning_engine import StrategyType
        
        evaluation = EvaluationResult(
            agent_name="documentation_generator",
            category=EvaluationCategory.CORRECTNESS,
            score=quality_score,
            reasoning=f"Generated documentation with {prefs.style.value} style",
            metrics={'quality_score': quality_score}
        )
        
        # Determine strategy based on preferences
        if prefs.depth == DocumentationDepth.DETAILED:
            strategy = StrategyType.INCREMENTAL
        elif prefs.depth == DocumentationDepth.CONCISE:
            strategy = StrategyType.SKELETON
        else:
            strategy = StrategyType.ADAPTIVE
        
        # Record pattern in learning engine
        try:
            self.learning_engine.learn_from_execution(
                operation_type="documentation",
                strategy=strategy,
                context=strategy_context,
                evaluation=evaluation,
                execution_time_seconds=execution_time_seconds,
                tokens_used=None
            )
            
            if self.logger:
                self.logger.info(
                    f"📚 Recorded documentation pattern: {module_type} "
                    f"(score: {quality_score:.1f}/10, strategy: {strategy.value})"
                )
        
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Failed to record pattern in learning engine: {e}")
    
    def get_recommended_preferences(
        self,
        user_id: str,
        module_type: str,
        context: Dict[str, Any],
        project_id: Optional[str] = None
    ) -> Optional[DocumentationPreferences]:
        """
        Get recommended preferences based on learning engine insights.
        
        Uses AgentLearningEngine to find similar past successful documentation
        generations and recommend optimal preferences.
        
        Args:
            user_id: User identifier
            module_type: Type of module to document
            context: Generation context (complexity, file_count, etc.)
            project_id: Optional project identifier
            
        Returns:
            Recommended DocumentationPreferences or None if no recommendations
        """
        if not self.learning_engine:
            if self.logger:
                self.logger.debug("AgentLearningEngine not available - using default preferences")
            return None
        
        # Build search context
        search_context = {
            'module_type': module_type,
            **context
        }
        
        try:
            # Get recommendations from learning engine
            recommendations = self.learning_engine.get_recommendations(
                operation_type="documentation",
                context=search_context,
                top_k=1
            )
            
            if not recommendations:
                if self.logger:
                    self.logger.info("No learned patterns found - using user's current preferences")
                return None
            
            top_recommendation = recommendations[0]
            
            # Extract preferences from learned patterns
            # This would be enhanced to parse actual learned preference patterns
            current_prefs = self.get_preferences(user_id, project_id)
            
            # For now, adjust based on strategy recommendation
            recommended_prefs = DocumentationPreferences(
                user_id=user_id,
                project_id=project_id,
                style=current_prefs.style,
                tone=current_prefs.tone,
                depth=current_prefs.depth,
                example_density=current_prefs.example_density,
                preferred_format=current_prefs.preferred_format,
                include_diagrams=current_prefs.include_diagrams,
                include_toc=current_prefs.include_toc
            )
            
            # Adjust depth based on recommended strategy
            from ...learning.agent_learning_engine import StrategyType
            if top_recommendation.strategy == StrategyType.INCREMENTAL:
                recommended_prefs.depth = DocumentationDepth.DETAILED
            elif top_recommendation.strategy == StrategyType.SKELETON:
                recommended_prefs.depth = DocumentationDepth.CONCISE
            else:
                recommended_prefs.depth = DocumentationDepth.MODERATE
            
            if self.logger:
                self.logger.info(
                    f"💡 Recommended depth: {recommended_prefs.depth.value} "
                    f"(confidence: {top_recommendation.confidence:.1%}, "
                    f"reasoning: {top_recommendation.reasoning[:50]}...)"
                )
            
            return recommended_prefs
        
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Failed to get recommendations from learning engine: {e}")
            return None
    
    @property
    def preferences(self) -> Dict[str, DocumentationPreferences]:
        """Public read-only access to preferences cache"""
        return self._preferences_cache
    
    @property
    def update_history(self) -> Dict[str, List[PreferenceUpdate]]:
        """Public read-only access to update history"""
        return self._update_history
