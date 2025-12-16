"""
Code Review Suggester - Feature 8 Implementation
CORTEX Orchestrator Enhancement Plan v1.0

Automatic code review suggestions after phase completion.
Integrates with response template system and Brain Tier 1.

Author: Asif Hussain
Created: December 13, 2025
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import re
from src.utils.resource_resolver import get_root_path


class CodeReviewSuggester:
    """
    Manages code review suggestions based on phase completion.
    
    Features:
    - Trigger-based suggestions (phase-4, phase-5, before-deployment)
    - User interaction handling (accept/decline)
    - Skip tracking in Brain Tier 1
    - Deployment reminders for skipped reviews
    """
    
    # Trigger rules mapping
    TRIGGER_RULES = {
        'phase-4': {
            'suggest_after': True,
            'name': 'Controllers Implementation',
            'message': (
                "✅ Phase 4 Complete! Controllers implemented.\n\n"
                "🔍 Recommended: Run code review analysis?\n"
                "- Compare legacy vs modern\n"
                "- Validate SOLID principles\n"
                "- Check security compliance\n\n"
                "Say 'review code' or 'skip review'"
            )
        },
        'phase-5': {
            'suggest_after': True,
            'name': 'Legacy Migration',
            'message': (
                "✅ Phase 5 Complete! Legacy code migrated.\n\n"
                "🔍 Recommended: Run comprehensive review?\n"
                "- Functionality parity check\n"
                "- Performance comparison\n"
                "- Test coverage validation\n\n"
                "Say 'review code' or 'skip review'"
            )
        },
        'before-deployment': {
            'suggest': True,
            'name': 'Deployment Preparation',
            'message': (
                "⚠️ Preparing for deployment.\n\n"
                "🔍 Required: Code review before deployment?\n"
                "- Security audit\n"
                "- Performance validation\n"
                "- Compliance check\n\n"
                "Say 'review code' to proceed"
            )
        }
    }
    
    def __init__(self, brain_path: Optional[Path] = None):
        """
        Initialize suggester with Brain Tier 1 path.
        
        Args:
            brain_path: Path to cortex-brain/tier1/ directory
        """
        if brain_path is None:
            # Default to project root
            project_root = get_root_path().parent
            self.brain_path = project_root / "cortex-brain" / "tier1"
        else:
            self.brain_path = brain_path
        
        self.skip_history_file = self.brain_path / "code-review-skip-history.json"
    
    def check_should_suggest(self, context: Dict[str, Any]) -> bool:
        """
        Check if code review should be suggested based on context.
        
        Args:
            context: Phase or event information
        
        Returns:
            True if suggestion should be shown
        """
        # Check phase-based triggers
        if 'phase' in context:
            phase = context['phase']
            if phase in self.TRIGGER_RULES:
                rule = self.TRIGGER_RULES[phase]
                return rule.get('suggest_after', False)
        
        # Check event-based triggers
        if 'event' in context:
            event = context['event']
            if event in self.TRIGGER_RULES:
                rule = self.TRIGGER_RULES[event]
                return rule.get('suggest', False)
        
        return False
    
    def format_suggestion_message(self, context: Dict[str, Any]) -> str:
        """
        Format suggestion message based on context.
        
        Args:
            context: Phase or event information
        
        Returns:
            Formatted suggestion message
        """
        # Get trigger key
        trigger_key = context.get('phase') or context.get('event')
        
        if trigger_key and trigger_key in self.TRIGGER_RULES:
            return self.TRIGGER_RULES[trigger_key]['message']
        
        # Fallback message
        return (
            "🔍 Code review recommended.\n\n"
            "Say 'review code' to start or 'skip review' to continue."
        )
    
    def parse_user_response(self, response: str) -> str:
        """
        Parse user response to determine action.
        
        Args:
            response: User's response string
        
        Returns:
            'accept', 'decline', or 'unknown'
        """
        response_lower = response.lower().strip()
        
        # Accept patterns
        accept_patterns = [
            r'\breview\s+code\b',
            r'\brun\s+review\b',
            r'\bstart\s+review\b',
            r'\byes\b',
            r'\baccept\b'
        ]
        
        for pattern in accept_patterns:
            if re.search(pattern, response_lower):
                return 'accept'
        
        # Decline patterns
        decline_patterns = [
            r'\bskip\s+review\b',
            r'\bno\s+review\b',
            r'\bdecline\b',
            r'\bno\b',
            r'\blater\b'
        ]
        
        for pattern in decline_patterns:
            if re.search(pattern, response_lower):
                return 'decline'
        
        return 'unknown'
    
    def track_skip_decision(self, context: Dict[str, Any], reason: str) -> bool:
        """
        Track skip decision in Brain Tier 1.
        
        Args:
            context: Phase or event information
            reason: Reason for skipping
        
        Returns:
            True if successfully tracked
        """
        try:
            # Ensure brain directory exists
            self.brain_path.mkdir(parents=True, exist_ok=True)
            
            # Load existing skip history
            if self.skip_history_file.exists():
                with open(self.skip_history_file, 'r', encoding='utf-8') as f:
                    skip_data = json.load(f)
            else:
                skip_data = {'skipped_reviews': []}
            
            # Add new skip entry
            skip_entry = {
                'phase': context.get('phase', 'unknown'),
                'event': context.get('event', None),
                'name': context.get('name', 'Unknown'),
                'reason': reason,
                'timestamp': context.get('timestamp', datetime.now().isoformat()),
                'status': context.get('status', 'unknown')
            }
            
            skip_data['skipped_reviews'].append(skip_entry)
            
            # Save updated history
            with open(self.skip_history_file, 'w', encoding='utf-8') as f:
                json.dump(skip_data, f, indent=2)
            
            return True
        
        except Exception as e:
            print(f"Error tracking skip decision: {e}")
            return False
    
    def get_deployment_reminder(self, context: Dict[str, Any]) -> Optional[str]:
        """
        Get deployment reminder if reviews were skipped.
        
        Args:
            context: Deployment event information
        
        Returns:
            Reminder message or None
        """
        if not self.skip_history_file.exists():
            return None
        
        try:
            with open(self.skip_history_file, 'r', encoding='utf-8') as f:
                skip_data = json.load(f)
            
            skipped_reviews = skip_data.get('skipped_reviews', [])
            
            if not skipped_reviews:
                return None
            
            # Format reminder with skipped phases
            phases = [entry['phase'] for entry in skipped_reviews if entry.get('phase')]
            
            reminder = (
                f"⚠️ Reminder: You skipped code reviews for the following phases:\n"
            )
            
            for entry in skipped_reviews:
                phase = entry.get('phase', 'unknown')
                name = entry.get('name', 'Unknown')
                reminder += f"  • {phase}: {name}\n"
            
            reminder += "\nRecommend running code review before deployment."
            
            return reminder
        
        except Exception as e:
            print(f"Error getting deployment reminder: {e}")
            return None
    
    def get_trigger_rules(self) -> Dict[str, Any]:
        """
        Get all trigger rules for documentation/debugging.
        
        Returns:
            Dictionary of trigger rules
        """
        return self.TRIGGER_RULES


# Convenience function for easy integration
def suggest_code_review(context: Dict[str, Any], brain_path: Optional[Path] = None) -> Optional[str]:
    """
    Convenience function to check and get code review suggestion.
    
    Args:
        context: Phase or event information
        brain_path: Optional Brain Tier 1 path
    
    Returns:
        Suggestion message or None
    """
    suggester = CodeReviewSuggester(brain_path=brain_path)
    
    if suggester.check_should_suggest(context):
        return suggester.format_suggestion_message(context)
    
    return None
