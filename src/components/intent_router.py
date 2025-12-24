"""
CORTEX Intent Router
Purpose: Detect user intent and route to appropriate component (Planning or Development)
Version: 1.0
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import re
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import json


class IntentRouter:
    """Routes user requests to Planning Orchestrator or Development Executor"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the Intent Router
        
        Args:
            config_path: Path to entry-point-router.yaml (optional)
        """
        if config_path is None:
            # Default to cortex-brain/components/intent-router/entry-point-router.yaml
            config_path = Path(__file__).parent.parent.parent / "cortex-brain" / "components" / "intent-router" / "entry-point-router.yaml"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.planning_triggers = self.config['planning_triggers']['keywords']
        self.development_triggers = self.config['development_triggers']['keywords']
        self.ambiguous_triggers = self.config['ambiguous_triggers']['keywords']
        self.needs_planning_signals = self.config['context_signals']['needs_planning']
        self.ready_for_impl_signals = self.config['context_signals']['ready_for_implementation']
        
        self.metrics_path = Path(__file__).parent.parent.parent / "cortex-brain" / "metrics" / "routing-decisions.jsonl"
        self.metrics_path.parent.mkdir(parents=True, exist_ok=True)
    
    def route(self, user_message: str) -> Dict:
        """
        Route user message to appropriate component
        
        Args:
            user_message: The user's natural language request
        
        Returns:
            Dict with keys: 
                - action: 'planning', 'development', or 'clarification'
                - confidence: float 0.0 to 1.0
                - keywords_matched: List of matched keywords
                - context_signals: List of detected context signals
                - pipeline: 'sequential', 'standalone_planning', 'standalone_development', or 'clarification'
                - response_template: Suggested response to user
        """
        user_message_lower = user_message.lower()
        
        # Step 1: Check for explicit planning triggers (Rule 1 - Highest Priority)
        planning_matches = self._match_keywords(user_message_lower, self.planning_triggers)
        if planning_matches['count'] > 0:
            confidence = min(0.95, 0.7 + (planning_matches['count'] * 0.1))
            return self._create_routing_decision(
                action='planning',
                confidence=confidence,
                keywords_matched=planning_matches['keywords'],
                context_signals=[],
                pipeline='sequential_planning_to_development',
                user_message=user_message
            )
        
        # Step 2: Check for explicit development triggers (Rule 2)
        development_matches = self._match_keywords(user_message_lower, self.development_triggers)
        if development_matches['count'] > 0:
            confidence = min(0.95, 0.7 + (development_matches['count'] * 0.1))
            return self._create_routing_decision(
                action='development',
                confidence=confidence,
                keywords_matched=development_matches['keywords'],
                context_signals=[],
                pipeline='standalone_development',
                user_message=user_message
            )
        
        # Step 3: Check for ambiguous triggers with context signals (Rules 3 & 4)
        ambiguous_matches = self._match_keywords(user_message_lower, self.ambiguous_triggers)
        if ambiguous_matches['count'] > 0:
            # Detect context signals
            planning_signals = self._match_keywords(user_message_lower, self.needs_planning_signals)
            impl_signals = self._match_keywords(user_message_lower, self.ready_for_impl_signals)
            
            if planning_signals['count'] > impl_signals['count']:
                # Rule 3: Ambiguous + planning context → route to planning
                confidence = 0.65 + (planning_signals['count'] * 0.05)
                return self._create_routing_decision(
                    action='planning',
                    confidence=confidence,
                    keywords_matched=ambiguous_matches['keywords'],
                    context_signals=planning_signals['keywords'],
                    pipeline='sequential_planning_to_development',
                    user_message=user_message
                )
            elif impl_signals['count'] > planning_signals['count']:
                # Rule 4: Ambiguous + implementation context → route to development
                confidence = 0.65 + (impl_signals['count'] * 0.05)
                return self._create_routing_decision(
                    action='development',
                    confidence=confidence,
                    keywords_matched=ambiguous_matches['keywords'],
                    context_signals=impl_signals['keywords'],
                    pipeline='standalone_development',
                    user_message=user_message
                )
            else:
                # Equal signals or no signals → ask clarification
                return self._create_clarification_request(
                    feature=ambiguous_matches['keywords'][0] if ambiguous_matches['keywords'] else 'this feature',
                    user_message=user_message
                )
        
        # Step 4: No clear match (Rule 5 - Fallback)
        return self._create_clarification_request(
            feature='this',
            user_message=user_message
        )
    
    def _match_keywords(self, text: str, keywords: List[str]) -> Dict:
        """
        Match keywords in text (case-insensitive)
        
        Returns:
            Dict with 'count' and 'keywords' (list of matched keywords)
        """
        matched = []
        for keyword in keywords:
            # Use word boundary matching to avoid partial matches
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            if re.search(pattern, text):
                matched.append(keyword)
        
        return {
            'count': len(matched),
            'keywords': matched
        }
    
    def _create_routing_decision(self, action: str, confidence: float, keywords_matched: List[str], 
                                  context_signals: List[str], pipeline: str, user_message: str) -> Dict:
        """Create a routing decision dictionary"""
        decision = {
            'action': action,
            'confidence': confidence,
            'keywords_matched': keywords_matched,
            'context_signals': context_signals,
            'pipeline': pipeline,
            'response_template': self._get_response_template(action, pipeline),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        
        # Log metrics
        self._log_routing_decision(user_message, decision)
        
        return decision
    
    def _create_clarification_request(self, feature: str, user_message: str) -> Dict:
        """Create a clarification request"""
        clarification_prompt = self.config['ambiguous_triggers']['clarification_prompt'].format(feature=feature)
        
        decision = {
            'action': 'clarification',
            'confidence': 0.0,
            'keywords_matched': [],
            'context_signals': [],
            'pipeline': 'clarification',
            'response_template': clarification_prompt,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        
        # Log metrics
        self._log_routing_decision(user_message, decision)
        
        return decision
    
    def _get_response_template(self, action: str, pipeline: str) -> str:
        """Get appropriate response template based on action and pipeline"""
        templates = self.config['ux_patterns']
        
        if action == 'planning':
            return templates['pattern_1_planning_first']['cortex_response']
        elif action == 'development':
            return templates['pattern_2_implement_directly']['cortex_response']
        else:
            return templates['pattern_3_ambiguous_needs_clarification']['cortex_response']
    
    def _log_routing_decision(self, user_message: str, decision: Dict):
        """Log routing decision to metrics file"""
        if not self.config['config']['store_routing_decisions']:
            return
        
        log_entry = {
            'timestamp': decision['timestamp'],
            'user_message': user_message[:100],  # Truncate for privacy
            'routing_decision': decision['action'],
            'confidence_score': decision['confidence'],
            'keywords_matched': decision['keywords_matched'],
            'context_signals': decision['context_signals'],
            'pipeline': decision['pipeline'],
            'clarification_needed': decision['action'] == 'clarification'
        }
        
        # Append to JSONL file
        with open(self.metrics_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def get_pipeline_config(self, pipeline_name: str) -> Dict:
        """Get pipeline configuration by name"""
        return self.config['pipelines'].get(pipeline_name, {})


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

if __name__ == "__main__":
    # Example usage
    router = IntentRouter()
    
    # Test cases
    test_cases = [
        "plan authentication system",
        "add login button",
        "authentication",
        "implement payment processing",
        "what's the best way to handle user sessions?",
        "just add a simple config file",
    ]
    
    print("🧠 CORTEX Intent Router - Test Cases\n")
    print("=" * 80)
    
    for test_message in test_cases:
        result = router.route(test_message)
        print(f"\n📝 User: \"{test_message}\"")
        print(f"🎯 Action: {result['action'].upper()}")
        print(f"📊 Confidence: {result['confidence']:.2f}")
        print(f"🔑 Keywords: {', '.join(result['keywords_matched']) if result['keywords_matched'] else 'None'}")
        print(f"📋 Pipeline: {result['pipeline']}")
        print("-" * 80)
