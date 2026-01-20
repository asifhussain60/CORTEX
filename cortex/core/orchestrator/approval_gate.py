"""Approval Gate

STUB IMPLEMENTATION - To be completed in Phase E.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class AlternativeRecommendation:
    """Alternative recommendation for approval."""
    alternative_id: str
    description: str
    rationale: str


__all__ = ["AlternativeRecommendation"]
