"""
CORTEX Context Injection Helper

Simplified interface for injecting Tier 1 context at CORTEX entry points.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from typing import Dict, Optional
import logging
from src.context_injector import ContextInjector

logger = logging.getLogger(__name__)

# Global context injector instance (lazy initialization)
_context_injector = None


def get_context_injector() -> ContextInjector:
    """Get or create global context injector instance"""
    global _context_injector
    if _context_injector is None:
        _context_injector = ContextInjector()
        logger.info("Context injector initialized")
    return _context_injector


def inject_tier1_context(user_request: str, 
                         conversation_id: Optional[str] = None) -> Dict:
    """
    Inject Tier 1 context with automatic pronoun resolution
    
    This is the simplified interface for CORTEX entry points.
    Use this at the start of request processing to:
    - Load recent conversations
    - Extract active entities
    - Resolve pronouns ("it" → actual entity)
    - Get formatted context summary
    
    Args:
        user_request: User's request text
        conversation_id: Optional conversation UUID
    
    Returns:
        {
            'resolved_request': str,  # Request with pronouns resolved
            'formatted_summary': str,  # Token-efficient context (<500 tokens)
            'active_entities': {...},  # Files, classes, methods, UI components
            'context_display': str,  # User-friendly summary for display
            'injection_time_ms': float  # Performance metric
        }
    
    Example:
        >>> context = inject_tier1_context("Make it purple")
        >>> print(context['resolved_request'])
        "Make the FAB button purple"
        
        >>> print(context['context_display'])
        🧠 **Context Loaded**
        
        📚 **Recent Work:**
           • Added purple FAB button to dashboard
        
        📄 **Active Files:**
           • Dashboard.tsx
           • styles.css
    """
    injector = get_context_injector()
    
    # Inject Tier 1 only (fast, focused context)
    full_context = injector.inject_context(
        user_request=user_request,
        conversation_id=conversation_id,
        include_tiers={'tier1': True, 'tier2': False, 'tier3': False}
    )
    
    # Extract Tier 1 results
    tier1 = full_context.get('tier1', {})
    
    return {
        'resolved_request': tier1.get('resolved_request', user_request),
        'formatted_summary': tier1.get('formatted_summary', ''),
        'active_entities': tier1.get('active_entities', {}),
        'context_display': tier1.get('context_display', ''),
        'injection_time_ms': full_context.get('injection_time_ms', 0),
        'raw_conversations': tier1.get('recent_conversations', [])  # For advanced use
    }


def inject_full_context(user_request: str,
                       conversation_id: Optional[str] = None,
                       current_file: Optional[str] = None) -> Dict:
    """
    Inject context from all tiers (1, 2, 3)
    
    Use this for complex operations that benefit from:
    - Tier 1: Recent conversations + entities
    - Tier 2: Pattern matching from knowledge graph
    - Tier 3: Development metrics and git analysis
    
    Args:
        user_request: User's request text
        conversation_id: Optional conversation UUID
        current_file: Optional current file path (for namespace detection)
    
    Returns:
        Complete context from all tiers with performance metrics
    """
    injector = get_context_injector()
    
    return injector.inject_context(
        user_request=user_request,
        conversation_id=conversation_id,
        current_file=current_file,
        include_tiers={'tier1': True, 'tier2': True, 'tier3': True}
    )


def resolve_pronoun_only(user_request: str) -> str:
    """
    Quick pronoun resolution without full context injection
    
    Use when you only need pronoun resolution (e.g., in message preprocessing)
    
    Args:
        user_request: User's request text
    
    Returns:
        Request with pronouns resolved
    
    Example:
        >>> resolve_pronoun_only("Make it bigger")
        "Make the FAB button bigger"
    """
    context = inject_tier1_context(user_request)
    return context['resolved_request']


def get_context_display(user_request: str) -> str:
    """
    Get formatted context display for showing to user
    
    Use this to display what CORTEX "remembers" from recent work
    
    Args:
        user_request: User's request text
    
    Returns:
        Formatted context summary with emojis (ready for display)
    
    Example:
        >>> print(get_context_display("Continue work"))
        🧠 **Context Loaded**
        
        📚 **Recent Work:**
           • Added authentication system
        
        📄 **Active Files:**
           • AuthService.cs
    """
    context = inject_tier1_context(user_request)
    return context['context_display']


# Performance monitoring helpers

def get_last_injection_time() -> float:
    """Get the time taken for last context injection (in ms)"""
    injector = get_context_injector()
    return injector._last_injection_time_ms


def is_injection_performance_ok() -> bool:
    """Check if last injection was within performance target (<200ms)"""
    return get_last_injection_time() < 200.0
