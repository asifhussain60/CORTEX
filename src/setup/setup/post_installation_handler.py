"""
Post-Installation Handler

Handles user choices after successful CORTEX setup:
1. Demo - Show CORTEX capabilities
2. Analyze - Onboard and analyze current repository
3. Skip - Start working immediately

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class PostInstallationHandler:
    """
    Handles post-installation user choices and routes to appropriate orchestrator.
    """
    
    def __init__(self, context: Dict[str, Any]):
        """
        Initialize handler with setup context.
        
        Args:
            context: Setup context from completion module
        """
        self.context = context
        self.project_root = Path(context.get('project_root', Path.cwd()))
        self.user_project_root = Path(context.get('user_project_root', self.project_root.parent))
        
    def detect_user_choice(self, user_input: str) -> str:
        """
        Detect what user wants to do from their input.
        
        Args:
            user_input: User's response
            
        Returns:
            Choice identifier: 'demo', 'analyze', or 'skip'
        """
        user_lower = user_input.lower()
        
        # Demo triggers
        demo_triggers = [
            'demo', 'show me', 'demonstrate', 'tour', 'capabilities',
            'what can you do', 'features', 'show features', 'see demo'
        ]
        
        if any(trigger in user_lower for trigger in demo_triggers):
            return 'demo'
        
        # Analyze/onboard triggers
        analyze_triggers = [
            'analyze', 'onboard', 'analyze repo', 'analyze repository',
            'analyze this', 'scan', 'review', 'inspect', 'check repo'
        ]
        
        if any(trigger in user_lower for trigger in analyze_triggers):
            return 'analyze'
        
        # Skip/start working triggers
        skip_triggers = [
            'skip', 'no', 'later', 'start working', 'get started',
            'jump in', 'begin', 'help'
        ]
        
        if any(trigger in user_lower for trigger in skip_triggers):
            return 'skip'
        
        # Default to demo if unclear
        return 'demo'
    
    def handle_demo_choice(self) -> Dict[str, Any]:
        """
        Handle user choosing to see a demo.
        
        Returns:
            Response dictionary with template routing
        """
        logger.info("User selected: Demo")
        
        # Route to Demo Orchestrator
        return {
            'action': 'demo',
            'orchestrator': 'demo',
            'template_id': 'introduction_discovery',
            'context': {
                'post_installation': True,
                'user_request': 'show me CORTEX capabilities',
                'source': 'post_installation_handler'
            }
        }
    
    def handle_analyze_choice(self) -> Dict[str, Any]:
        """
        Handle user choosing to analyze their repository.
        
        Returns:
            Response dictionary with onboarding routing
        """
        logger.info("User selected: Analyze Repository")
        
        # Route to Onboarding Module
        return {
            'action': 'analyze',
            'orchestrator': 'onboarding',
            'module': 'onboarding_module',
            'context': {
                'post_installation': True,
                'user_project_root': str(self.user_project_root),
                'project_root': str(self.project_root),
                'brain_initialized': self.context.get('brain_initialized', False),
                'source': 'post_installation_handler'
            }
        }
    
    def handle_skip_choice(self) -> Dict[str, Any]:
        """
        Handle user choosing to skip and start working.
        
        Returns:
            Response dictionary with help information
        """
        logger.info("User selected: Skip / Start Working")
        
        return {
            'action': 'skip',
            'template_id': 'general_help',
            'context': {
                'post_installation': True,
                'message': 'Ready to start! Say "help" to see available commands.',
                'source': 'post_installation_handler'
            }
        }
    
    def process_user_choice(self, user_input: str) -> Dict[str, Any]:
        """
        Process user's choice and route to appropriate handler.
        
        Args:
            user_input: User's response to post-installation prompt
            
        Returns:
            Response dictionary with routing information
        """
        choice = self.detect_user_choice(user_input)
        
        handlers = {
            'demo': self.handle_demo_choice,
            'analyze': self.handle_analyze_choice,
            'skip': self.handle_skip_choice
        }
        
        handler = handlers.get(choice, self.handle_demo_choice)
        return handler()


def handle_post_installation_choice(context: Dict[str, Any], user_input: str) -> Dict[str, Any]:
    """
    Convenience function for handling post-installation choices.
    
    Args:
        context: Setup context
        user_input: User's response
        
    Returns:
        Routing dictionary
    """
    handler = PostInstallationHandler(context)
    return handler.process_user_choice(user_input)
