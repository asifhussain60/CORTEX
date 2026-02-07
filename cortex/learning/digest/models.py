"""
Data models for DIGEST Mode.

Pydantic models for structured DIGEST results.

Author: Asif Hussain
Date: 2026-02-07
Phase: 41 Stage 1 (ENH-053)
"""

from datetime import datetime
from typing import Dict, Any
from pydantic import BaseModel, Field


class DigestResult(BaseModel):
    """
    Structured result from DIGEST session analysis.
    
    Attributes:
        file_path: Path to analyzed file
        is_chat_session: Whether file is a Copilot chat session
        chat_score: Confidence score (0-10) for chat detection
        extractions: Dict of extracted insights by category
        timestamp: When analysis was performed
        dry_run: Whether results were saved
    """
    file_path: str
    is_chat_session: bool
    chat_score: int = Field(ge=0, le=10)
    extractions: Dict[str, Any]
    timestamp: datetime
    dry_run: bool = False
    saved: bool = False


class ChatMarker:
    """Chat session detection markers."""
    USER_PROMPT = "User:"
    COPILOT_RESPONSE = "GitHub Copilot:"
    TOOL_CALL = "[Tool call:"
    DRIFT_COMMENT = "# Drift"
    PATTERN_COMMENT = "# Pattern"
    EFFICIENCY_COMMENT = "# Efficiency:"


class ExtractionCategory:
    """Extraction categories for DIGEST."""
    DRIFTS = "drifts"
    PATTERNS = "patterns"
    TOOLS = "tools"
    EFFICIENCY = "efficiency"
    ACCURACY = "accuracy"
    GOVERNANCE_VIOLATIONS = "governance_violations"
