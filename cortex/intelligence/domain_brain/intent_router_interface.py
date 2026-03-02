"""Intent Router interface definition."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, List

if TYPE_CHECKING:
    from cortex.intelligence.domain_brain.nlp_handler_router import IntentResult


class IIntentRouter(ABC):
    """Interface for Intent Router implementations."""

    @abstractmethod
    def query_intent(self, query: str) -> "IntentResult":
        """Query and route an intent.

        Args:
            query: Natural language query string

        Returns:
            IntentResult with routing information
        """
        pass

    @abstractmethod
    def get_history(self) -> List[Dict[str, Any]]:
        """Get intent execution history.

        Returns:
            List of recent intent queries (max 100)
        """
        pass
