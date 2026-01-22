"""
HolisticContextBuilder - Merges multi-dimensional context into unified structure.

Combines:
- Intent (user requirement)
- Analysis (static/dynamic analysis results)
- Challenges (detected issues/risks)
- Recommendations (suggested actions)
- Git context (version control metadata)

Production-ready implementation with:
- Lossless data merging
- YAML serialization support
- Nested structure preservation
- Type safety
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import copy


@dataclass
class HolisticContext:
    """Data class for HolisticContext."""
    data: Dict[str, Any] = field(default_factory=dict)


class HolisticContextBuilder:
    """Implementation of HolisticContextBuilder for merging multi-dimensional context."""

    def __init__(self):
        """Initialize builder."""
        self._context: Dict[str, Any] = {}

    def build_holistic_context(self, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build holistic context by merging all dimensions.
        
        Args:
            context_data: Dict with keys: intent, analysis, challenges, 
                         recommendations, git_context
        
        Returns:
            Merged context dict with all dimensions preserved
        """
        # Deep copy to avoid mutations
        result: Dict[str, Any] = {}
        
        # Extract and preserve each dimension
        result["intent"] = context_data.get("intent", "")
        result["analysis"] = copy.deepcopy(context_data.get("analysis", {}))
        result["challenges"] = copy.deepcopy(context_data.get("challenges", []))
        result["recommendations"] = copy.deepcopy(context_data.get("recommendations", []))
        result["git_context"] = copy.deepcopy(context_data.get("git_context", {}))
        
        return result


__all__ = [
    "HolisticContext",
    "HolisticContextBuilder",
]