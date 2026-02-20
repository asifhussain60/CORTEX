"""Contextual Help & Error Remediation tests and implementation."""
import pytest
from enum import Enum
from typing import Dict, List, Optional, Any
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
    def __init__(self):
        self.help_database: Dict[str, HelpContent] = {}
        self.remedies: Dict[str, ErrorRemedy] = {}
        self.context_history = []
    
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

class TestContextualHelp:
    def setup_method(self):
        self.provider = ContextualHelpProvider()
    
    def test_register_help(self):
        content = HelpContent("Topic", "Desc", ["Step 1"], ["Example"])
        assert self.provider.register_help("test", content) is True
    
    def test_get_help(self):
        content = HelpContent("Topic", "Desc", ["Step 1"], ["Example"])
        self.provider.register_help("test", content)
        result = self.provider.get_help("test", UserContext.NEW)
        assert result is not None
        assert result.title == "Topic"
    
    def test_register_remedy(self):
        remedy = ErrorRemedy("TypeError", "Check types", "Explanation")
        assert self.provider.register_remedy("TypeError", remedy) is True
    
    def test_suggest_fix(self):
        remedy = ErrorRemedy("TypeError", "Check types", "Explanation")
        self.provider.register_remedy("TypeError", remedy)
        result = self.provider.suggest_fix("TypeError")
        assert result is not None
        assert result.suggested_fix == "Check types"
    
    def test_detect_context_new(self):
        context = self.provider.detect_context({'actions': 1})
        assert context == UserContext.NEW
    
    def test_detect_context_learning(self):
        context = self.provider.detect_context({'actions': 5})
        assert context == UserContext.LEARNING
    
    def test_detect_context_intermediate(self):
        context = self.provider.detect_context({'actions': 15})
        assert context == UserContext.INTERMEDIATE
    
    def test_detect_context_advanced(self):
        context = self.provider.detect_context({'actions': 30})
        assert context == UserContext.ADVANCED
