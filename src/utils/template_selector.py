"""
Template Selector
Version: 3.3.0
Purpose: Intent detection and template selection with backward compatibility
Part of: Response Template System Refactor (Phase 5.4)
"""

import yaml
import re
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass

from src.utils.template_composer import TemplateComposer, UserProfile, ComposedResponse


@dataclass
class SelectionResult:
    """Result of template selection"""
    template_id: str
    confidence: float  # 0.0 to 1.0
    matched_intent: str
    matched_keywords: List[str]
    orchestrator: Optional[str] = None


class TemplateSelector:
    """
    Selects appropriate template based on user input with intent detection.
    
    Features:
    - Keyword-based intent detection
    - Priority-based template matching
    - Context validation (tech_stack, dor_complete, etc.)
    - Backward compatibility with legacy system
    - Integration with TemplateComposer
    """
    
    def __init__(self, brain_path: str = None):
        """
        Initialize TemplateSelector.
        
        Args:
            brain_path: Path to cortex-brain directory
        """
        if brain_path is None:
            current_dir = Path(__file__).parent
            brain_path = current_dir.parent.parent / "cortex-brain"
        
        self.brain_path = Path(brain_path)
        self.routing_path = self.brain_path / "response-routing-rules.yaml"
        self.legacy_path = self.brain_path / "response-templates.yaml"
        
        # Lazy-loaded routing rules
        self._routing: Optional[Dict] = None
        
        # TemplateComposer integration
        self.composer = TemplateComposer(brain_path=str(brain_path))
    
    @property
    def routing(self) -> Dict:
        """Lazy-load routing rules"""
        if self._routing is None:
            if self.routing_path.exists():
                with open(self.routing_path, 'r', encoding='utf-8') as f:
                    self._routing = yaml.safe_load(f)
            else:
                self._routing = {}
        return self._routing
    
    def select_template(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None
    ) -> SelectionResult:
        """
        Select appropriate template based on user input and context.
        
        Args:
            user_input: User's natural language input
            context: Additional context (tech_stack, dor_complete, etc.)
        
        Returns:
            SelectionResult with template_id and metadata
        """
        context = context or {}
        
        # Extract keywords from user input
        keywords = self._extract_keywords(user_input)
        
        # Match against priority groups
        intent_detection = self.routing.get('intent_detection', {})
        
        # Try each priority level in order
        for priority_key in sorted(intent_detection.keys()):
            if priority_key == 'fallback':
                continue  # Handle fallback last
            
            intents = intent_detection[priority_key]
            
            for intent_def in intents:
                match_result = self._match_intent(keywords, intent_def, context)
                
                if match_result:
                    return match_result
        
        # Fallback if no match
        fallback = intent_detection.get('fallback', {})
        return SelectionResult(
            template_id=fallback.get('template', 'template_fallback'),
            confidence=0.5,
            matched_intent='fallback',
            matched_keywords=[],
            orchestrator=None
        )
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extract keywords from text using simple tokenization.
        
        Args:
            text: Input text
        
        Returns:
            List of lowercase keywords
        """
        # Lowercase and remove punctuation
        text = text.lower()
        text = re.sub(r'[^\w\s-]', ' ', text)
        
        # Tokenize
        tokens = text.split()
        
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        keywords = [t for t in tokens if t not in stop_words]
        
        return keywords
    
    def _match_intent(
        self,
        keywords: List[str],
        intent_def: Dict,
        context: Dict[str, Any]
    ) -> Optional[SelectionResult]:
        """
        Check if keywords match an intent definition.
        
        Args:
            keywords: Extracted keywords from user input
            intent_def: Intent definition from routing rules
            context: Additional context for validation
        
        Returns:
            SelectionResult if match found, None otherwise
        """
        intent_keywords = intent_def.get('keywords', [])
        
        # Check for keyword matches
        matched_keywords = []
        for intent_kw in intent_keywords:
            intent_kw_lower = intent_kw.lower()
            
            # Support multi-word keywords (e.g., "plan ado")
            if ' ' in intent_kw_lower:
                # Check if phrase appears in original keyword list (reconstruct from keywords)
                keyword_text = ' '.join(keywords)
                if intent_kw_lower in keyword_text:
                    matched_keywords.append(intent_kw)
            else:
                # Single word match
                if intent_kw_lower in keywords:
                    matched_keywords.append(intent_kw)
        
        # Require at least one keyword match
        if not matched_keywords:
            return None
        
        # Validate context requirements
        context_required = intent_def.get('context_required')
        if context_required:
            if not self._validate_context(context_required, context):
                return None
        
        # Calculate confidence based on match quality
        confidence = len(matched_keywords) / len(intent_keywords)
        confidence = min(confidence, 1.0)
        
        return SelectionResult(
            template_id=intent_def['template'],
            confidence=confidence,
            matched_intent=intent_def['intent'],
            matched_keywords=matched_keywords,
            orchestrator=intent_def.get('orchestrator')
        )
    
    def _validate_context(self, requirement: str, context: Dict[str, Any]) -> bool:
        """
        Validate context requirement.
        
        Args:
            requirement: Context requirement (e.g., 'has_tech_stack')
            context: Context dict to validate
        
        Returns:
            True if requirement met, False otherwise
        """
        if requirement == 'has_tech_stack':
            return context.get('tech_stack') is not None
        
        if requirement == 'dor_complete':
            return context.get('dor_complete', False)
        
        # Add more validation rules as needed
        return True
    
    def compose_response(
        self,
        user_input: str,
        profile: UserProfile,
        context: Optional[Dict[str, Any]] = None,
        content_vars: Optional[Dict[str, str]] = None
    ) -> Tuple[SelectionResult, ComposedResponse]:
        """
        Complete workflow: Select template + Compose response.
        
        Args:
            user_input: User's natural language input
            profile: User profile (interaction mode, experience, detail)
            context: Additional context
            content_vars: Variables for template substitution
        
        Returns:
            Tuple of (SelectionResult, ComposedResponse)
        """
        # Select template
        selection = self.select_template(user_input, context)
        
        # Compose response
        composed = self.composer.compose_response(
            template_id=selection.template_id,
            profile=profile,
            content_vars=content_vars
        )
        
        return selection, composed
    
    def is_legacy_mode(self) -> bool:
        """
        Check if system should use legacy template system.
        
        Returns:
            True if legacy mode enabled, False otherwise
        """
        # Check for feature flag in config
        # For now, default to new system
        return False
    
    def get_template_list(self) -> List[Dict[str, str]]:
        """
        Get list of all available templates.
        
        Returns:
            List of dicts with template_id, name, description
        """
        templates = self.composer.definitions.get('templates', {})
        
        result = []
        for name, template in templates.items():
            result.append({
                'template_id': template.get('id'),
                'name': template.get('name'),
                'description': template.get('description', ''),
                'response_type': template.get('response_type', '')
            })
        
        return result
    
    def get_intents_for_template(self, template_id: str) -> List[str]:
        """
        Get list of intents that map to a template.
        
        Args:
            template_id: Template ID to lookup
        
        Returns:
            List of intent names
        """
        intent_detection = self.routing.get('intent_detection', {})
        intents = []
        
        for priority_key, intent_list in intent_detection.items():
            if priority_key == 'fallback':
                continue
            
            for intent_def in intent_list:
                if intent_def.get('template') == template_id:
                    intents.append(intent_def.get('intent'))
        
        return intents
