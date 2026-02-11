"""BaseInquiryHandler - Abstract base for all inquiry handlers.

AC-ID: INQUIRY-007-NEW
Purpose: Define common interface for inquiry handlers
Author: Asif Hussain
Date: 2026-01-27
"""

from abc import ABC, abstractmethod
from typing import Any, Dict

from cortex.models.inquiry_models import AssembledContext


class BaseInquiryHandler(ABC):
    """Abstract base class for inquiry handlers.

    All handlers must implement handle() method to process
    assembled context and return formatted responses.
    """

    @abstractmethod
    def handle(self, context: AssembledContext) -> Dict[str, Any]:
        """Handle inquiry using assembled context.

        Args:
            context: Assembled context with evidence, category, confidence

        Returns:
            Response dictionary with:
                - answer: str (40-60 words)
                - evidence: List[Dict] (file:line references)
                - confidence: float (0.0-1.0)
                - disclaimer: str (optional, for user repos)
        """
        pass
