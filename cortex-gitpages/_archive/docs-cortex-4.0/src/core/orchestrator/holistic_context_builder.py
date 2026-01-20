"""
Holistic Context Builder - Merges all context dimensions into single YAML structure.

Consolidates intent, code analysis, challenges, recommendations, and git context
into a unified holistic context matching CORTEX.prompt.md format specifications.

Type hints: CORE-011 compliant
Docstrings: Google style, CORE-012 compliant
"""

from typing import Dict, Any, List
import yaml


class HolisticContextBuilder:
    """Merges all context dimensions into unified holistic context.
    
    Responsibilities:
    - Consolidate intent, analysis, challenges, recommendations, git context
    - Produce valid YAML structure
    - Match CORTEX.prompt.md holistic context format
    - Handle edge cases gracefully
    
    Example:
        builder = HolisticContextBuilder()
        result = builder.build_holistic_context({
            "intent": "Add auth",
            "analysis": {...},
            "challenges": [...],
            "recommendations": [...],
            "git_context": {...},
        })
    """
    
    def build_holistic_context(self, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build holistic context from all dimensions.
        
        Merges five primary dimensions:
        1. intent - Canonicalized user request
        2. analysis - Code analysis results (AST, imports, etc)
        3. challenges - Risk/challenge identification
        4. recommendations - Suggested actions
        5. git_context - Version control and relationship data
        
        Args:
            context_data: Dictionary containing context dimensions:
                - intent: str
                - analysis: dict
                - challenges: list
                - recommendations: list
                - git_context: dict
        
        Returns:
            Dictionary with all dimensions merged, ready for YAML serialization.
        """
        result = {
            "intent": context_data.get("intent", ""),
            "analysis": context_data.get("analysis", {}),
            "challenges": context_data.get("challenges", []),
            "recommendations": context_data.get("recommendations", []),
            "git_context": context_data.get("git_context", {}),
        }
        
        return result
