"""Complexity analysis for work planning."""

from typing import Dict, List
from ..base_agent import AgentRequest
from ..utils import extract_file_paths, safe_get


class ComplexityAnalyzer:
    """Analyzes request complexity."""
    
    def __init__(self):
        """Initialize complexity keywords."""
        self.COMPLEXITY_KEYWORDS = {
            "simple": ["add", "create", "simple", "basic", "quick"],
            "medium": ["modify", "update", "refactor", "enhance", "improve"],
            "complex": ["redesign", "migrate", "overhaul", "architecture", "system"]
        }
    
    def analyze(self, request: AgentRequest) -> str:
        """
        Analyze request complexity based on keywords and context.
        
        Returns:
            Complexity level: "simple", "medium", or "complex"
        """
        message_lower = request.user_message.lower()
        
        # Count complexity indicators
        complexity_scores = {
            "simple": 0,
            "medium": 0,
            "complex": 0
        }
        
        for level, keywords in self.COMPLEXITY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in message_lower:
                    complexity_scores[level] += 1
        
        # Check context hints
        context_complexity = safe_get(request.context, "complexity", default="")
        if context_complexity and context_complexity.lower() in complexity_scores:
            complexity_scores[context_complexity.lower()] += 3
        
        # Check for multi-file operations
        if len(extract_file_paths(request.user_message)) > 3:
            complexity_scores["complex"] += 2
        
        # Return highest scoring complexity
        if complexity_scores["complex"] >= complexity_scores["medium"]:
            if complexity_scores["complex"] >= complexity_scores["simple"]:
                return "complex"
        
        if complexity_scores["medium"] >= complexity_scores["simple"]:
            return "medium"
        
        return "simple"
