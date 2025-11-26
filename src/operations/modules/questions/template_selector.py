"""
CORTEX 3.0 Phase 2 - Template Selector
=====================================

Dynamic template selection based on namespace detection from Question Router.
Integrates Feature 2 (Question Router) with Response Template System.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

Phase: Phase 2 - Advanced Response Handling (Task 1)
Integration: Question Router → Response Template System
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import time
import logging

# Import from Feature 2 (Phase 1)
try:
    from src.agents.namespace_detector import NamespaceDetector, NamespaceType, NamespaceDetectionResult
except ImportError:
    logging.warning("NamespaceDetector not available - using fallback")
    NamespaceDetector = None
    NamespaceType = None


@dataclass
class TemplateSelectionResult:
    """Result of template selection process."""
    template_name: str
    template_content: Dict[str, Any]
    confidence: float
    reasoning: str
    parameters: Dict[str, Any]
    namespace: str
    selection_time_ms: float


class TemplateCategory(Enum):
    """Template categories for different types of responses."""
    CORTEX_FRAMEWORK = "cortex"
    WORKSPACE_CODE = "workspace"
    GENERAL_HELP = "help"
    STATUS_CHECK = "status"
    ERROR_HANDLING = "error"
    PLANNING = "planning"
    EXECUTION = "execution"
    VALIDATION = "validation"


class TemplateSelector:
    """
    Dynamic template selector that integrates with Question Router.
    
    Selects appropriate response templates based on:
    - Namespace detection (CORTEX vs workspace)
    - Question intent and context
    - User preferences and history
    """
    
    def __init__(self, brain_path: str = None):
        """
        Initialize template selector.
        
        Args:
            brain_path: Path to CORTEX brain directory
        """
        self.brain_path = Path(brain_path) if brain_path else Path(__file__).parent.parent.parent.parent / "cortex-brain"
        self.templates_path = self.brain_path / "response-templates"
        
        # Initialize namespace detector from Phase 1
        self.namespace_detector = None
        if NamespaceDetector:
            try:
                self.namespace_detector = NamespaceDetector()
            except Exception as e:
                logging.warning(f"Failed to initialize NamespaceDetector: {e}")
        
        # Load templates
        self.templates = self._load_templates()
        
        # Template selection cache for performance
        self._selection_cache = {}
        self._cache_max_size = 1000
    
    def _load_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load response templates from brain directory."""
        templates = {}
        
        try:
            # Load main templates file
            main_templates_file = self.templates_path / "response-templates.yaml"
            if main_templates_file.exists():
                with open(main_templates_file, 'r', encoding='utf-8') as f:
                    main_templates = yaml.safe_load(f)
                    if main_templates and 'templates' in main_templates:
                        templates.update(main_templates['templates'])
            
            # Load additional template files
            for template_file in self.templates_path.glob("*.yaml"):
                if template_file.name != "response-templates.yaml":
                    try:
                        with open(template_file, 'r', encoding='utf-8') as f:
                            file_templates = yaml.safe_load(f)
                            if file_templates:
                                templates.update(file_templates)
                    except Exception as e:
                        logging.warning(f"Failed to load template file {template_file}: {e}")
            
            logging.info(f"Loaded {len(templates)} response templates")
            
        except Exception as e:
            logging.error(f"Failed to load templates: {e}")
            # Fallback templates
            templates = self._get_fallback_templates()
        
        return templates
    
    def _get_fallback_templates(self) -> Dict[str, Dict[str, Any]]:
        """Fallback templates if loading fails."""
        return {
            "cortex_status": {
                "name": "CORTEX Status",
                "trigger": ["status", "health", "how is cortex"],
                "response_type": "structured",
                "namespace": "cortex",
                "content": "## CORTEX Status\n\nSystem operational. All brain tiers functional."
            },
            "workspace_help": {
                "name": "Workspace Help",
                "trigger": ["help", "how to", "workspace"],
                "response_type": "narrative",
                "namespace": "workspace", 
                "content": "I'll help you with your workspace. What specific task do you need assistance with?"
            },
            "general_response": {
                "name": "General Response",
                "trigger": ["*"],
                "response_type": "narrative",
                "namespace": "general",
                "content": "I understand you need assistance. Could you provide more details about what you're trying to achieve?"
            }
        }
    
    def select_template(self, question: str, context: Dict[str, Any] = None) -> TemplateSelectionResult:
        """
        Select appropriate template for given question and context.
        
        Args:
            question: User's question or request
            context: Additional context (current file, project state, etc.)
            
        Returns:
            TemplateSelectionResult with selected template and metadata
        """
        start_time = time.time()
        context = context or {}
        
        # Check cache first
        cache_key = self._get_cache_key(question, context)
        if cache_key in self._selection_cache:
            cached_result = self._selection_cache[cache_key]
            cached_result.selection_time_ms = (time.time() - start_time) * 1000
            return cached_result
        
        # Step 1: Namespace detection using Phase 1 Question Router
        namespace_result = self._detect_namespace(question, context)
        
        # Step 2: Intent analysis
        intent = self._analyze_intent(question, context)
        
        # Step 3: Template matching
        candidate_templates = self._find_candidate_templates(question, namespace_result, intent)
        
        # Step 4: Scoring and selection
        best_template = self._score_and_select(candidate_templates, question, namespace_result, intent, context)
        
        # Step 5: Parameter extraction
        parameters = self._extract_parameters(question, context, best_template)
        
        selection_time_ms = (time.time() - start_time) * 1000
        
        result = TemplateSelectionResult(
            template_name=best_template['name'],
            template_content=best_template['template'],
            confidence=best_template['score'],
            reasoning=best_template['reasoning'],
            parameters=parameters,
            namespace=namespace_result.primary_namespace.name if namespace_result else "UNKNOWN",
            selection_time_ms=selection_time_ms
        )
        
        # Cache result
        self._cache_result(cache_key, result)
        
        return result
    
    def _detect_namespace(self, question: str, context: Dict[str, Any]) -> Optional[NamespaceDetectionResult]:
        """Detect question namespace using Phase 1 Question Router."""
        if not self.namespace_detector:
            return None
            
        try:
            return self.namespace_detector.detect_namespace(question)
        except Exception as e:
            logging.warning(f"Namespace detection failed: {e}")
            return None
    
    def _analyze_intent(self, question: str, context: Dict[str, Any]) -> str:
        """Analyze user intent from question."""
        question_lower = question.lower()
        
        # Status/health questions
        if any(word in question_lower for word in ['status', 'health', 'how is', 'show me']):
            return 'STATUS'
        
        # Help questions
        if any(word in question_lower for word in ['help', 'how to', 'what is', 'explain']):
            return 'HELP'
        
        # Planning questions
        if any(word in question_lower for word in ['plan', 'design', 'architecture', 'strategy']):
            return 'PLAN'
        
        # Execution questions
        if any(word in question_lower for word in ['create', 'add', 'implement', 'build', 'make']):
            return 'EXECUTE'
        
        # Testing/validation
        if any(word in question_lower for word in ['test', 'validate', 'check', 'verify']):
            return 'TEST'
        
        # Error/debugging
        if any(word in question_lower for word in ['error', 'bug', 'broken', 'fix', 'debug']):
            return 'FIX'
        
        return 'GENERAL'
    
    def _find_candidate_templates(self, question: str, namespace_result: Optional[NamespaceDetectionResult], intent: str) -> List[Dict[str, Any]]:
        """Find candidate templates based on namespace and intent."""
        candidates = []
        question_lower = question.lower()
        
        for template_id, template in self.templates.items():
            candidate = {
                'id': template_id,
                'template': template,
                'score': 0.0,
                'reasoning': []
            }
            
            # Namespace matching
            template_namespace = template.get('namespace', 'general')
            if namespace_result:
                if namespace_result.primary_namespace == NamespaceType.CORTEX_FRAMEWORK and template_namespace == 'cortex':
                    candidate['score'] += 0.4
                    candidate['reasoning'].append("Namespace match: CORTEX framework")
                elif namespace_result.primary_namespace == NamespaceType.WORKSPACE_CODE and template_namespace == 'workspace':
                    candidate['score'] += 0.4
                    candidate['reasoning'].append("Namespace match: Workspace code")
                elif namespace_result.primary_namespace == NamespaceType.GENERAL and template_namespace == 'general':
                    candidate['score'] += 0.3
                    candidate['reasoning'].append("Namespace match: General question")
            
            # Trigger word matching
            triggers = template.get('trigger', [])
            if isinstance(triggers, str):
                triggers = [triggers]
            
            for trigger in triggers:
                if trigger.lower() in question_lower:
                    candidate['score'] += 0.3
                    candidate['reasoning'].append(f"Trigger match: '{trigger}'")
            
            # Intent matching
            template_intent = template.get('response_type', 'narrative')
            if intent == 'STATUS' and 'status' in template.get('name', '').lower():
                candidate['score'] += 0.2
                candidate['reasoning'].append("Intent match: Status")
            elif intent == 'HELP' and template_intent in ['detailed', 'table']:
                candidate['score'] += 0.2
                candidate['reasoning'].append("Intent match: Help")
            
            # Add candidate if it has any score
            if candidate['score'] > 0:
                candidates.append(candidate)
        
        # Sort by score
        candidates.sort(key=lambda x: x['score'], reverse=True)
        return candidates[:10]  # Top 10 candidates
    
    def _score_and_select(self, candidates: List[Dict[str, Any]], question: str, namespace_result: Optional[NamespaceDetectionResult], intent: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Score candidates and select the best template."""
        if not candidates:
            # Fallback to general template
            return {
                'name': 'General Fallback',
                'template': self.templates.get('general_response', self._get_fallback_templates()['general_response']),
                'score': 0.1,
                'reasoning': 'Fallback: No suitable templates found'
            }
        
        best = candidates[0]
        
        # Additional scoring based on context
        if context.get('current_file'):
            if namespace_result and namespace_result.primary_namespace == NamespaceType.WORKSPACE_CODE:
                best['score'] += 0.1
                best['reasoning'].append("Context: Working on workspace file")
        
        # Confidence-based adjustments
        if namespace_result and namespace_result.confidence > 0.8:
            best['score'] += 0.1
            best['reasoning'].append(f"High namespace confidence: {namespace_result.confidence:.2f}")
        
        best['reasoning'] = " | ".join(best['reasoning'])
        return best
    
    def _extract_parameters(self, question: str, context: Dict[str, Any], template: Dict[str, Any]) -> Dict[str, Any]:
        """Extract parameters for template rendering."""
        parameters = {
            'question': question,
            'context': context,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Extract common parameters
        if context.get('current_file'):
            parameters['current_file'] = context['current_file']
        
        if context.get('project_name'):
            parameters['project_name'] = context['project_name']
        
        # Template-specific parameter extraction
        template_content = template['template']
        if isinstance(template_content, dict):
            # Extract variables from template content
            content_str = str(template_content.get('content', ''))
            # Simple variable extraction ({{variable}})
            import re
            variables = re.findall(r'\{\{(\w+)\}\}', content_str)
            for var in variables:
                if var not in parameters:
                    parameters[var] = context.get(var, f"[{var}]")
        
        return parameters
    
    def _get_cache_key(self, question: str, context: Dict[str, Any]) -> str:
        """Generate cache key for question and context."""
        # Simple cache key based on question and key context elements
        context_key = str(sorted([(k, v) for k, v in context.items() if k in ['current_file', 'project_name']]))
        return f"{hash(question)}:{hash(context_key)}"
    
    def _cache_result(self, cache_key: str, result: TemplateSelectionResult):
        """Cache selection result."""
        if len(self._selection_cache) >= self._cache_max_size:
            # Remove oldest entry (simple FIFO)
            oldest_key = next(iter(self._selection_cache))
            del self._selection_cache[oldest_key]
        
        self._selection_cache[cache_key] = result
    
    def get_template_stats(self) -> Dict[str, Any]:
        """Get template selection statistics."""
        return {
            'total_templates': len(self.templates),
            'cache_size': len(self._selection_cache),
            'cache_max_size': self._cache_max_size,
            'namespace_detector_available': self.namespace_detector is not None
        }


# Convenience function for easy integration
def select_template_for_question(question: str, context: Dict[str, Any] = None, brain_path: str = None) -> TemplateSelectionResult:
    """
    Convenience function to select template for a question.
    
    Args:
        question: User's question
        context: Optional context
        brain_path: Optional brain path
        
    Returns:
        TemplateSelectionResult
    """
    selector = TemplateSelector(brain_path)
    return selector.select_template(question, context)


if __name__ == "__main__":
    # Test the template selector
    import sys
    import json
    
    # Test questions
    test_questions = [
        "Show me CORTEX brain health status",
        "How do I debug my application code?",
        "What is the best authentication approach?",
        "Help me plan a new feature",
        "Add a purple button to the dashboard"
    ]
    
    selector = TemplateSelector()
    
    print("🧠 CORTEX 3.0 Phase 2 - Template Selector Test")
    print("=" * 60)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{i}. Question: {question}")
        
        try:
            result = selector.select_template(question)
            
            print(f"   Template: {result.template_name}")
            print(f"   Namespace: {result.namespace}")
            print(f"   Confidence: {result.confidence:.2f}")
            print(f"   Reasoning: {result.reasoning}")
            print(f"   Selection Time: {result.selection_time_ms:.1f}ms")
            
        except Exception as e:
            print(f"   ERROR: {e}")
    
    print(f"\n📊 Template Stats:")
    stats = selector.get_template_stats()
    print(json.dumps(stats, indent=2))