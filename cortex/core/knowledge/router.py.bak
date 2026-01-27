"""
Intelligent Knowledge Router for smart query routing based on intent analysis.

Analyzes query intent and routes to appropriate backend with confidence
scoring, audit trails, and fallback mechanisms.

Governance:
  - CORE-008: Tests written before code (TDD)
  - CORE-011: 100% type hints on all parameters and returns
  - CORE-012: Google-style docstrings on public APIs
  - CORE-013: Specific exception handling (no bare except)
"""

from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime
import uuid
import logging
import re


logger = logging.getLogger(__name__)


TECHNICAL_KEYWORDS = {
    'python', 'javascript', 'java', 'api', 'database', 'sql', 'nosql',
    'async', 'await', 'microservices', 'docker', 'kubernetes', 'ci/cd',
    'debug', 'memory', 'performance', 'optimization', 'architecture',
    'design patterns', 'framework', 'library', 'module', 'function'
}

BUSINESS_KEYWORDS = {
    'policy', 'benefits', 'budget', 'sales', 'marketing', 'hr',
    'compliance', 'revenue', 'customer', 'strategy', 'roi', 'kpi',
    'company', 'department', 'team', 'process', 'procedure', 'guideline'
}


@dataclass
class QueryIntent:
    """Represents analyzed query intent."""
    
    intent_type: str
    primary_domain: str
    confidence: float
    keywords: List[str] = field(default_factory=list)
    domain_scores: Dict[str, float] = field(default_factory=dict)
    
    def __contains__(self, key: str) -> bool:
        """Support 'in' operator for dict-like access."""
        return hasattr(self, key)
    
    def __getitem__(self, key: str) -> Any:
        """Support dict-like access."""
        if not hasattr(self, key):
            raise KeyError(key)
        return getattr(self, key)


@dataclass
class RoutingAuditEntry:
    """Audit entry for routing decision."""
    
    entry_id: str
    query: str
    selected_backend: str
    confidence: float
    timestamp: datetime = field(default_factory=datetime.now)
    intent_analysis: Optional[QueryIntent] = None
    alternative_backends: List[Tuple[str, float]] = field(default_factory=list)
    routing_factors: Dict[str, Any] = field(default_factory=dict)
    
    def __contains__(self, key: str) -> bool:
        """Support 'in' operator for dict-like access."""
        return hasattr(self, key)
    
    def __getitem__(self, key: str) -> Any:
        """Support dict-like access."""
        if not hasattr(self, key):
            raise KeyError(key)
        return getattr(self, key)


class IntelligentKnowledgeRouter:
    """Router for intelligent query routing to knowledge backends.
    
    Analyzes query intent and routes to appropriate backend based on
    confidence scoring and domain matching.
    """
    
    def __init__(
        self,
        backends: Optional[Dict[str, Any]] = None,
        confidence_threshold: float = 0.5,
    ) -> None:
        """Initialize IntelligentKnowledgeRouter.
        
        Args:
            backends: Dictionary of knowledge backends.
            confidence_threshold: Minimum confidence for routing (0-1).
            
        Raises:
            TypeError: If backends values are not valid backend objects.
            ValueError: If backends dictionary is empty.
        """
        if backends is None:
            backends = {}
        
        # Validate non-empty backends
        if not backends:
            raise ValueError("At least one backend must be provided")
        
        # Validate backends
        for name, backend in backends.items():
            if isinstance(backend, str):
                raise TypeError(f"Backend '{name}' must be an object, not string")
        
        self.backends = backends
        self.confidence_threshold = confidence_threshold
        self.routing_history: List[RoutingAuditEntry] = []
        self.query_count = 0
        self.successful_routes = 0
        self.fallback_count = 0
        
        logger.info(f"IntelligentKnowledgeRouter initialized with {len(self.backends)} backends")
    
    def analyze_query_intent(self, query: str) -> QueryIntent:
        """Analyze query to determine intent and domain.
        
        Args:
            query: The query string to analyze.
            
        Returns:
            QueryIntent object with analysis results.
        """
        query_lower = query.lower()
        keywords = self._extract_keywords(query_lower)
        
        # Score domains
        domain_scores = self._score_domains(keywords)
        
        # Determine primary domain
        primary_domain = max(domain_scores, key=domain_scores.get) if domain_scores else 'general'
        confidence = domain_scores.get(primary_domain, 0.5)
        
        intent = QueryIntent(
            intent_type=self._determine_intent_type(query_lower),
            primary_domain=primary_domain,
            confidence=confidence,
            keywords=keywords,
            domain_scores=domain_scores,
        )
        
        return intent
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract keywords from query.
        
        Args:
            query: Query string.
            
        Returns:
            List of extracted keywords.
        """
        # Split and clean
        words = re.findall(r'\b\w+\b', query)
        keywords = [w.lower() for w in words if len(w) > 2]
        return keywords
    
    def _score_domains(self, keywords: List[str]) -> Dict[str, float]:
        """Score relevant domains based on keywords.
        
        Args:
            keywords: List of keywords.
            
        Returns:
            Dictionary of domain scores.
        """
        scores: Dict[str, float] = {}
        
        technical_matches = sum(1 for k in keywords if k in TECHNICAL_KEYWORDS)
        business_matches = sum(1 for k in keywords if k in BUSINESS_KEYWORDS)
        
        total = max(technical_matches + business_matches, 1)
        
        if technical_matches > 0:
            scores['technical'] = technical_matches / total
        if business_matches > 0:
            scores['business'] = business_matches / total
        
        if not scores:
            scores['general'] = 0.5
        
        return scores
    
    def _determine_intent_type(self, query: str) -> str:
        """Determine type of query intent.
        
        Args:
            query: Query string.
            
        Returns:
            Intent type (question, request, search, etc).
        """
        if '?' in query:
            return 'question'
        elif any(verb in query for verb in ['how to', 'help with', 'need']):
            return 'request'
        else:
            return 'search'
    
    def detect_domain_keywords(self, query: str) -> List[str]:
        """Detect domain-specific keywords in query.
        
        Args:
            query: Query string.
            
        Returns:
            List of detected domain keywords.
        """
        query_lower = query.lower()
        keywords = []
        
        for keyword in TECHNICAL_KEYWORDS:
            if keyword in query_lower:
                keywords.append(keyword)
        
        for keyword in BUSINESS_KEYWORDS:
            if keyword in query_lower:
                keywords.append(keyword)
        
        return keywords
    
    def score_backend_confidence(self, query: str) -> Dict[str, float]:
        """Score confidence for each backend.
        
        Args:
            query: Query to score.
            
        Returns:
            Dictionary of backend names to confidence scores.
        """
        scores = {}
        intent = self.analyze_query_intent(query)
        
        for backend_name, backend in self.backends.items():
            # Get backend domains if available
            backend_domains = getattr(backend, 'domains', None)
            if backend_domains is None or not isinstance(backend_domains, (list, tuple)):
                backend_domains = []
            
            # Match backend name with intent primary domain (for test compatibility)
            name_matches_intent = backend_name.lower() == intent.primary_domain.lower()
            
            # Score based on domain match or name match
            domain_match = any(d in intent.domain_scores for d in backend_domains) if backend_domains else name_matches_intent
            
            # Base score on intent confidence
            if domain_match:
                score = intent.confidence
            elif name_matches_intent:
                score = 0.7  # High confidence for name match
            else:
                score = 0.3
            
            # Normalize to 0-1
            scores[backend_name] = min(max(score, 0.0), 1.0)
        
        return scores
    
    def select_best_backend(self, query: str) -> Optional[str]:
        """Select best backend for query.
        
        Args:
            query: Query string.
            
        Returns:
            Name of selected backend or None.
        """
        if not self.backends:
            return None
        
        scores = self.score_backend_confidence(query)
        
        if not scores:
            return list(self.backends.keys())[0]
        
        best_backend = max(scores, key=scores.get)
        return best_backend
    
    def route_query(
        self,
        query: str,
    ) -> Tuple[Optional[Any], float, RoutingAuditEntry]:
        """Route query to best backend.
        
        Args:
            query: Query to route.
            
        Returns:
            Tuple of (backend_object, confidence, audit_entry).
            
        Raises:
            ValueError: If query is empty.
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        self.query_count += 1
        intent = self.analyze_query_intent(query)
        
        # Check for explicit domain override in query (e.g., "[business] query")
        selected_backend_name = self._check_explicit_domain(query)
        
        if not selected_backend_name:
            selected_backend_name = self.select_best_backend(query)
        
        if not selected_backend_name:
            selected_backend_name = list(self.backends.keys())[0] if self.backends else None
        
        confidence = self.score_backend_confidence(query).get(selected_backend_name, 0.5)
        
        # Get actual backend object
        selected_backend = self.backends.get(selected_backend_name)
        
        # Create audit entry
        audit = RoutingAuditEntry(
            entry_id=str(uuid.uuid4()),
            query=query,
            selected_backend=selected_backend_name or 'none',
            confidence=confidence,
            intent_analysis=intent,
            routing_factors={'query_intent': intent.intent_type},
        )
        
        self.routing_history.append(audit)
        self.successful_routes += 1
        
        logger.info(f"Query routed to {selected_backend_name} (confidence: {confidence:.2f})")
        
        return selected_backend, confidence, audit
    
    def _check_explicit_domain(self, query: str) -> Optional[str]:
        """Check for explicit domain specification in query format [domain].
        
        Args:
            query: Query string to check.
            
        Returns:
            Backend name if found, None otherwise.
        """
        match = re.match(r'\[(\w+)\]\s+', query)
        if match:
            domain = match.group(1).lower()
            if domain in self.backends:
                return domain
        return None
    
    def get_confidence_factors(self, query: str) -> Dict[str, Any]:
        """Get breakdown of confidence scoring factors.
        
        Args:
            query: Query string.
            
        Returns:
            Dictionary of scoring factors.
        """
        intent = self.analyze_query_intent(query)
        scores = self.score_backend_confidence(query)
        
        return {
            'intent_type': intent.intent_type,
            'primary_domain': intent.primary_domain,
            'keywords': intent.keywords,
            'domain_scores': intent.domain_scores,
            'backend_scores': scores,
            'total_keywords': len(intent.keywords),
        }
    
    def get_routing_history(self) -> List[RoutingAuditEntry]:
        """Get routing history.
        
        Returns:
            List of routing audit entries.
        """
        return self.routing_history
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get router performance metrics.
        
        Returns:
            Dictionary with performance metrics.
        """
        success_rate = self.successful_routes / max(self.query_count, 1)
        
        return {
            'queries_routed': self.query_count,
            'successful_routes': self.successful_routes,
            'success_rate': success_rate,
            'total_backends': len(self.backends),
            'avg_confidence': self._calculate_avg_confidence(),
            'fallback_queries': self.fallback_count,
        }
    
    def _calculate_avg_confidence(self) -> float:
        """Calculate average confidence score.
        
        Returns:
            Average confidence from routing history.
        """
        if not self.routing_history:
            return 0.0
        
        total = sum(a.confidence for a in self.routing_history)
        return total / len(self.routing_history)
    
    def route_query_with_fallback(self, query: str) -> Any:
        """Route query with fallback to parallel queries if confidence low.
        
        Args:
            query: Query string.
            
        Returns:
            Results from selected or parallel backends.
        """
        backend_name, confidence, audit = self.route_query(query)
        
        if confidence < self.confidence_threshold and len(self.backends) > 1:
            # Fallback: query multiple backends
            self.fallback_count += 1
            results = {}
            for name, backend in self.backends.items():
                if hasattr(backend, 'query'):
                    try:
                        results[name] = backend.query(query)
                    except Exception as e:
                        logger.error(f"Fallback query failed for {name}: {e}")
            
            return results
        
        # Normal path
        if backend_name and backend_name in self.backends:
            backend = self.backends[backend_name]
            if hasattr(backend, 'query'):
                try:
                    return backend.query(query)
                except Exception as e:
                    logger.error(f"Query failed on {backend_name}: {e}")
        
        return None
    
    def aggregate_parallel_results(self, results: Dict[str, List[Any]]) -> List[Any]:
        """Aggregate results from parallel queries.
        
        Args:
            results: Dictionary of backend results.
            
        Returns:
            Aggregated result list.
        """
        aggregated = []
        
        for backend_name, backend_results in results.items():
            if isinstance(backend_results, list):
                for result in backend_results:
                    aggregated.append(result)
            else:
                aggregated.append(backend_results)
        
        return aggregated


__all__ = [
    "IntelligentKnowledgeRouter",
    "QueryIntent",
    "RoutingAuditEntry",
]
