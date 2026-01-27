"""Intent Classifier for multi-dimensional intent categorization."""

from enum import Enum
from typing import List, Dict, Any, Callable


class IntentCategory(Enum):
    """Intent category types."""

    API = ("api", "data_retrieval", "resource_access")
    DOMAIN = ("domain", "domain_logic", "business_process")
    WORKFLOW = ("workflow", "orchestration", "pipeline")
    CONFIGURATION = ("config", "configuration", "settings")
    DIAGNOSTIC = ("diagnostic", "monitoring", "health_check")


class IntentClassifier:
    """Classifies intents into multiple dimensions."""

    # Category keywords
    API_KEYWORDS = [
        "get", "fetch", "retrieve", "list", "query", "data",
        "record", "user", "account", "database", "api", "call",
        "request", "search", "find"
    ]

    DOMAIN_KEYWORDS = [
        "domain", "business", "execute", "process", "logic",
        "finance", "healthcare", "ecommerce", "industry", "specific"
    ]

    WORKFLOW_KEYWORDS = [
        "workflow", "pipeline", "orchestr", "batch", "start",
        "run", "execute", "process", "sequence", "parallel",
        "fan_out", "saga", "chain"
    ]

    CONFIG_KEYWORDS = [
        "config", "configure", "setting", "set", "parameter",
        "timeout", "retry", "threshold", "limit", "policy"
    ]

    DIAGNOSTIC_KEYWORDS = [
        "monitor", "check", "health", "status", "log", "trace",
        "debug", "diagnose", "error", "alert", "metric",
        "performance", "system"
    ]

    def classify(self, text: str) -> str:
        """Classify intent into category.
        
        Args:
            text: Intent text to classify
            
        Returns:
            Category name: "api", "domain", "workflow", "config", or "diagnostic"
        """
        text_lower = text.lower()
        
        # Count keyword matches for each category
        scores: Dict[str, int] = {
            "api": self._count_keyword_matches(text_lower, self.API_KEYWORDS),
            "domain": self._count_keyword_matches(text_lower, self.DOMAIN_KEYWORDS),
            "workflow": self._count_keyword_matches(text_lower, self.WORKFLOW_KEYWORDS),
            "configuration": self._count_keyword_matches(text_lower, self.CONFIG_KEYWORDS),
            "diagnostic": self._count_keyword_matches(text_lower, self.DIAGNOSTIC_KEYWORDS)
        }
        
        # Return category with highest score
        best_category: str = max(scores, key=lambda k: scores[k])
        return best_category

    def _count_keyword_matches(self, text: str, keywords: List[str]) -> int:
        """Count keyword matches in text.
        
        Args:
            text: Text to search
            keywords: Keywords to match
            
        Returns:
            Number of keyword matches
        """
        count = 0
        for keyword in keywords:
            if keyword in text:
                count += 1
        return count

    def classify_with_confidence(self, text: str) -> Dict[str, Any]:
        """Classify intent with confidence scores for all categories.
        
        Args:
            text: Intent text to classify
            
        Returns:
            Dictionary with category and scores
        """
        text_lower = text.lower()
        
        # Calculate scores and normalize
        scores: Dict[str, int] = {
            "api": self._count_keyword_matches(text_lower, self.API_KEYWORDS),
            "domain": self._count_keyword_matches(text_lower, self.DOMAIN_KEYWORDS),
            "workflow": self._count_keyword_matches(text_lower, self.WORKFLOW_KEYWORDS),
            "configuration": self._count_keyword_matches(text_lower, self.CONFIG_KEYWORDS),
            "diagnostic": self._count_keyword_matches(text_lower, self.DIAGNOSTIC_KEYWORDS)
        }
        
        total = sum(scores.values()) or 1
        normalized_scores: Dict[str, float] = {k: v / total for k, v in scores.items()}
        
        best_category: str = max(scores, key=lambda k: scores[k])
        
        return {
            "category": best_category,
            "confidence": normalized_scores[best_category],
            "scores": normalized_scores
        }
