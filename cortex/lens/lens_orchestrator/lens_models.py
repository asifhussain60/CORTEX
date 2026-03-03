"""
LENS data models — LENSContext dataclass.

Extracted from lens_orchestrator.py (Phase 103-d, GAP-103-04).
Authority: CORE-008, CORE-011, CORE-012, LENS-003
"""
# CORE-035 — LENSContext here is the analyzer-result context (git/ast/comment fields);
# distinct from cortex/lens/models/context.py which is the Phase 65 operation context.
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any, Dict

__all__ = ["LENSContext"]


@dataclass
class LENSContext:
    """
    Unified LENS intelligence context.

    Compatible with IntentRouter's lens_context parameter (LENS-002).

    Attributes:
        git_analysis: Git commit history and patterns
        ast_analysis: AST structure and complexity
        comment_analysis: Comments, TODOs, and docstrings
        vision_analysis: Vision API analysis for images (URLs, elements, issues)
        tech_stack: Technology stack detected (Phase 90)
        metadata: Analysis metadata (timing, cache hits, etc.)
        analysis_id: Unique analysis identifier for URS correlation (Phase 83-e)
    """

    git_analysis: Dict[str, Any] = field(default_factory=dict)
    ast_analysis: Dict[str, Any] = field(default_factory=dict)
    comment_analysis: Dict[str, Any] = field(default_factory=dict)
    vision_analysis: Dict[str, Any] = field(default_factory=dict)
    tech_stack: Dict[str, Any] = field(default_factory=dict)  # Phase 90 S1
    metadata: Dict[str, Any] = field(default_factory=dict)
    analysis_id: str = field(default_factory=lambda: str(uuid.uuid4()))  # Phase 83-e: URS

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for IntentRouter compatibility."""
        result = {
            "git_analysis": self.git_analysis,
            "ast_analysis": self.ast_analysis,
            "comment_analysis": self.comment_analysis,
            "tech_stack": self.tech_stack,  # Phase 90 S1
            "_metadata": self.metadata,
        }
        # Only include vision_analysis if present
        if self.vision_analysis:
            result["vision_analysis"] = self.vision_analysis
        return result
