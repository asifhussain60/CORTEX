"""Contextual Help Provider Implementation."""
from enum import Enum
from typing import Dict, Optional, Any, List
from dataclasses import dataclass

class UserContext(Enum):
    NEW="new"; LEARNING="learning"; INTERMEDIATE="intermediate"; ADVANCED="advanced"

@dataclass
class HelpContent:
    title: str; description: str; steps: List[str]; examples: List[str]

@dataclass
class ErrorRemedy:
    error_type: str; suggested_fix: str; explanation: str

class ContextualHelpProvider:
    """Provides context-aware help and error remediation."""
    def __init__(self):
        self.help_database: Dict[str, HelpContent] = {}
        self.remedies: Dict[str, ErrorRemedy] = {}
    
    def register_help(self, topic: str, content: HelpContent) -> bool:
        if topic in self.help_database: return False
        self.help_database[topic] = content
        return True
    
    def get_help(self, topic: str, context: UserContext) -> Optional[HelpContent]:
        return self.help_database.get(topic)
    
    def register_remedy(self, error_type: str, remedy: ErrorRemedy) -> bool:
        if error_type in self.remedies: return False
        self.remedies[error_type] = remedy
        return True
    
    def suggest_fix(self, error_type: str) -> Optional[ErrorRemedy]:
        return self.remedies.get(error_type)
    
    def detect_context(self, user_activity: Dict[str, Any]) -> UserContext:
        actions = user_activity.get('actions', 0)
        if actions < 3: return UserContext.NEW
        if actions < 10: return UserContext.LEARNING
        if actions < 25: return UserContext.INTERMEDIATE
        return UserContext.ADVANCED
