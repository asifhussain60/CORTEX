"""
Shared types for Response Templates v4.0

This module contains shared types to avoid circular imports.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional


class ResponseTier(Enum):
    """Response complexity tiers"""
    INSTANT = "tier1_instant"          # <50 tokens
    FOCUSED = "tier2_focused"          # 50-200 tokens
    STRUCTURED = "tier3_structured"    # 200-600 tokens
    COMPREHENSIVE = "tier4_comprehensive"  # 600+ tokens


@dataclass
class TemplateContext:
    """Context information for template generation"""
    operation: str
    request: str
    has_modifications: bool = False
    has_architecture: bool = False
    has_technical_depth: bool = False
    has_risks: bool = False
    estimated_tokens: int = 0
    is_factual_query: bool = False
    is_single_concept: bool = False
    requires_multiple_aspects: bool = False
    requires_explanation: bool = False
    all_work_complete: bool = False
    no_errors: bool = True
    no_user_action_required: bool = False
