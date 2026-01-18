"""
IntelligentKnowledgeRouter Implementation (AC-IKP-002-01).

Smart query router that analyzes query intent and routes to appropriate backend
with confidence scoring and audit trail support.

Governance:
  - CORE-008: TDD methodology
  - CORE-011: Type hints mandatory
  - CORE-012: Google-style docstrings
  - CORE-013: Specific exception handling
"""

from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import re
from collections import defaultdict


@dataclass
class RoutingDecision:
    """Represents a routing decision with metadata."""
    
    backend_name: str
    confidence: float
    intent_type: str
    detected_domains: List[str]
    factors: Dict[str, float]
    timestamp: datetime = field(default_factory=datetime.now)


class IntelligentKnowledgeRouter:
    """
    Smart router for knowledge queries.
    
    Analyzes query intent and routes to appropriate backend with confidence scoring.
    Provides fallback to parallel queries for ambiguous queries.
    """

    # Domain keywords for detection
    DOMAIN_KEYWORDS = {
        'technical': [
            'python', 'java', 'javascript', 'database', 'sql', 'api', 'rest',
            'microservice', 'architecture', 'docker', 'kubernetes', 'deploy',
            'bug', 'debug', 'optimize', 'performance', 'memory', 'latency'
        ],
        'business': [
            'budget', 'revenue', 'sales', 'marketing', 'roi', 'strategy',
            'goal', 'objective', 'metric', 'kpi', 'forecast', 'plan',
            'deadline', 'resource', 'team', 'organization'
        ],
        'policy': [
            'policy', 'rule', 'regulation', 'compliance', 'legal', 'hr',
            'benefits', 'leave', 'vacation', 'conduct', 'ethics',
            'procedure', 'guideline', 'requirement', 'approval'
        ],
    }

    def __init__(
        self,
        backends: Dict[str, Any],
        confidence_threshold: float = 0.5
    ):
        """
        Initialize router with backends.
        
        Args:
            backends: Dictionary mapping backend names to backend objects.
            confidence_threshold: Minimum confidence for direct routing.
            
        Raises:
            ValueError: If backends is empty or contains invalid types.
            TypeError: If backends values are not callable or have required methods.
        """
        if not backends:
            raise ValueError("At least one backend must be provided")
        
        # Validate backend types
        for backend_name, backend_obj in backends.items():
            if isinstance(backend_obj, str):
                raise TypeError(
                    f"Backend '{backend_name}' must be an object, not a string"
                )
            if backend_obj is None:
                raise ValueError(
                    f"Backend '{backend_name}' cannot be None"
                )
        
        self.backends = backends
        self.confidence_threshold = confidence_threshold
        self.routing_history: List[RoutingDecision] = []
        self.query_count = 0
        self.fallback_count = 0

    def analyze_query_intent(self, query: str) -> Dict[str, Any]:
        """
        Analyze query to determine intent type.
        
        Args:
            query: Query text to analyze.
            
        Returns:
            Dict with intent_type and analysis details.
            
        Raises:
            ValueError: If query is empty.
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        query_lower = query.lower()
        
        # Determine intent from question type
        if query_lower.startswith('how'):
            intent_type = 'how_to'
        elif query_lower.startswith('what'):
            intent_type = 'definition'
        elif query_lower.startswith('why'):
            intent_type = 'rationale'
        elif query_lower.startswith('when'):
            intent_type = 'timing'
        else:
            intent_type = 'general'
        
        return {
            'intent_type': intent_type,
            'query_length': len(query),
            'has_question_mark': '?' in query,
        }

    def detect_domain_keywords(self, query: str) -> List[str]:
        """
        Detect domain keywords in query.
        
        Args:
            query: Query text to analyze.
            
        Returns:
            List of detected domain names.
        """
        query_lower = query.lower()
        detected = []
        
        # Check for explicit domain hint like "[domain]"
        domain_hint_match = re.match(r'^\[(\w+)\]', query_lower)
        if domain_hint_match:
            hint = domain_hint_match.group(1)
            if hint in self.DOMAIN_KEYWORDS:
                return [hint]
        
        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            for keyword in keywords:
                if keyword in query_lower:
                    detected.append(domain)
                    break
        
        return list(set(detected))  # Remove duplicates

    def score_backend_confidence(self, query: str) -> Dict[str, float]:
        """
        Score confidence for each backend.
        
        Args:
            query: Query text to score.
            
        Returns:
            Dict mapping backend names to confidence scores (0-1).
        """
        scores = {}
        detected_domains = self.detect_domain_keywords(query)
        
        for backend_name in self.backends.keys():
            score = 0.0
            
            # Match detected domains with backend specialization
            if detected_domains:
                if any(domain in backend_name.lower() for domain in detected_domains):
                    score += 0.7
                else:
                    score += 0.3
            else:
                # Default score for ambiguous queries
                score = 0.5
            
            # Adjust based on query length (very short or very long are less clear)
            if len(query) < 10:
                score *= 0.8
            elif len(query) > 500:
                score *= 0.9
            
            scores[backend_name] = min(1.0, score)
        
        return scores

    def select_best_backend(self, query: str) -> Tuple[str, float]:
        """
        Select best backend for query.
        
        Args:
            query: Query to route.
            
        Returns:
            Tuple of (backend_name, confidence).
        """
        scores = self.score_backend_confidence(query)
        best_backend = max(scores, key=scores.get)
        confidence = scores[best_backend]
        
        return best_backend, confidence

    def route_query(self, query: str) -> Tuple[Any, float, Dict[str, Any]]:
        """
        Route query to appropriate backend.
        
        Args:
            query: Query text to route.
            
        Returns:
            Tuple of (backend_object, confidence_score, audit_entry).
            
        Raises:
            ValueError: If query is empty.
            RuntimeError: If no backends available.
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        if not self.backends:
            raise RuntimeError("No backends available for routing")
        
        self.query_count += 1
        
        # Analyze query
        intent = self.analyze_query_intent(query)
        domains = self.detect_domain_keywords(query)
        
        # Score backends
        scores = self.score_backend_confidence(query)
        
        # Select best backend
        best_backend_name = max(scores, key=scores.get)
        confidence = scores[best_backend_name]
        
        backend = self.backends[best_backend_name]
        
        # Create audit entry
        audit = {
            'query': query[:100],  # Truncate long queries
            'confidence': confidence,
            'selected_backend': best_backend_name,
            'intent_type': intent['intent_type'],
            'detected_domains': domains,
            'timestamp': datetime.now().isoformat(),
            'confidence_scores': scores,
        }
        
        # Record decision
        decision = RoutingDecision(
            backend_name=best_backend_name,
            confidence=confidence,
            intent_type=intent['intent_type'],
            detected_domains=domains,
            factors=scores,
        )
        self.routing_history.append(decision)
        
        return backend, confidence, audit

    def route_query_with_fallback(self, query: str) -> List[Dict[str, Any]]:
        """
        Route query with fallback to parallel queries if confidence low.
        
        Args:
            query: Query text to route.
            
        Returns:
            List of results from applicable backends.
        """
        backend, confidence, audit = self.route_query(query)
        
        if confidence < self.confidence_threshold:
            # Use parallel query fallback
            self.fallback_count += 1
            results = []
            
            for backend_name, backend_obj in self.backends.items():
                if hasattr(backend_obj, 'query') and callable(backend_obj.query):
                    try:
                        result = backend_obj.query(query)
                        results.extend(result if isinstance(result, list) else [result])
                    except Exception:
                        pass
            
            return results
        else:
            # Use selected backend
            if hasattr(backend, 'query') and callable(backend.query):
                return backend.query(query)
            return []

    def get_routing_history(self) -> List[RoutingDecision]:
        """
        Get routing history.
        
        Returns:
            List of routing decisions made.
        """
        return self.routing_history

    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics.
        
        Returns:
            Dict with performance statistics.
        """
        return {
            'queries_routed': self.query_count,
            'fallback_queries': self.fallback_count,
            'avg_confidence': (
                sum(d.confidence for d in self.routing_history) / len(self.routing_history)
                if self.routing_history else 0.0
            ),
            'backend_usage': self._calculate_backend_usage(),
        }

    def _calculate_backend_usage(self) -> Dict[str, int]:
        """
        Calculate which backends were used most.
        
        Returns:
            Dict mapping backend names to usage count.
        """
        usage = defaultdict(int)
        for decision in self.routing_history:
            usage[decision.backend_name] += 1
        return dict(usage)

    def get_confidence_factors(self, query: str) -> Dict[str, Any]:
        """
        Get breakdown of confidence factors for query.
        
        Args:
            query: Query to analyze.
            
        Returns:
            Dict with factor details.
        """
        scores = self.score_backend_confidence(query)
        domains = self.detect_domain_keywords(query)
        intent = self.analyze_query_intent(query)
        
        return {
            'backend_scores': scores,
            'detected_domains': domains,
            'intent': intent,
            'best_backend': max(scores, key=scores.get),
            'best_confidence': max(scores.values()),
        }

    def aggregate_parallel_results(
        self,
        results: Dict[str, List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """
        Aggregate results from multiple backends.
        
        Args:
            results: Dict mapping backend names to result lists.
            
        Returns:
            Aggregated and deduplicated result list.
        """
        aggregated = []
        seen = set()
        
        for backend_name in sorted(results.keys()):
            for result in results.get(backend_name, []):
                # Simple deduplication based on string representation
                result_str = str(result)
                if result_str not in seen:
                    seen.add(result_str)
                    result_copy = dict(result) if isinstance(result, dict) else result
                    if isinstance(result_copy, dict):
                        result_copy['_source_backend'] = backend_name
                    aggregated.append(result_copy)
        
        return aggregated


__all__ = ['IntelligentKnowledgeRouter', 'RoutingDecision']
