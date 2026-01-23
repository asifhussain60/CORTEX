"""
Cross-Domain Knowledge Synthesis Engine - Tier 3.

Synthesizes insights from multiple knowledge domains using graph-based analysis,
pattern detection, and relationship mapping.

AC: KN-004-01 - Cross-Domain Knowledge Synthesis
AC: DB-005 - Knowledge Synthesis Engine Implementation

Production-Ready Features:
- Multi-domain cross-domain querying with relevance scoring
- Pattern detection and analysis across domains
- Relationship graph traversal and strength calculation
- Source attribution with traceability
- Synthesis caching with TTL
- Thread-safe singleton pattern
"""

from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
import yaml
import threading
from collections import defaultdict
import logging


logger = logging.getLogger(__name__)


@dataclass
class SynthesisResult:
    """Result of knowledge synthesis."""
    synthesis_id: str
    source_domains: List[str]
    synthesized_knowledge: str
    supporting_entries: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    confidence: float
    pattern_matches: List[str]
    created_at: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class SynthesisEngine:
    """Cross-domain knowledge synthesis engine with production-grade features."""
    
    _instance: Optional['SynthesisEngine'] = None
    _lock: threading.Lock = threading.Lock()
    
    def __new__(cls) -> 'SynthesisEngine':
        """Singleton pattern with thread safety."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        """Initialize synthesis engine with production-grade features."""
        if hasattr(self, '_initialized'):
            return
        
        self._domain_relationships: Dict[str, List[Tuple[str, float]]] = defaultdict(list)
        self._synthesis_cache: Dict[str, Tuple[SynthesisResult, float]] = {}
        self._synthesis_history: List[SynthesisResult] = []
        self._pattern_db: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self._config: Dict[str, Any] = {}
        self._cache_ttl: timedelta = timedelta(hours=24)
        self.ac_id: str = "KN-004-01"  # Governance reference
        self.governance_manager = None  # Will be injected by governance layer
        self.curator = None  # Knowledge curator reference
        self.indexer = None  # Search index reference
        self._load_config()
        self._initialized = True
        logger.info("SynthesisEngine initialized")
    
    def _load_config(self) -> None:
        """Load synthesis configuration from YAML."""
        config_file = Path(__file__).parent / "synthesis-config.yaml"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    self._config = data or {}
                    self._domain_relationships = self._build_relationship_graph(
                        data.get("domain_relationships", {})
                    )
                    self._load_patterns(data.get("patterns", {}))
                logger.info(f"Configuration loaded from {config_file}")
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                self._initialize_default_config()
        else:
            logger.warning(f"Config file not found: {config_file}")
            self._initialize_default_config()
    
    def _initialize_default_config(self) -> None:
        """Initialize with sensible defaults."""
        default_domains = [
            "GOVERNANCE", "INTENT-ROUTING", "HALLUCINATION-PREVENTION",
            "EXECUTION-ORCHESTRATION", "DATA-MANAGEMENT", "OBSERVABILITY",
            "SECURITY", "API-DESIGN", "ML-MODELS", "KNOWLEDGE-CURATION",
            "TESTING-VALIDATION", "DEPLOYMENT", "DOCUMENTATION",
            "PERFORMANCE", "ARCHITECTURE", "ERROR-HANDLING"
        ]
        
        # Create simple adjacency for all domains
        for domain in default_domains:
            for other_domain in default_domains:
                if domain != other_domain:
                    # All domains are connected with default strength 0.5
                    self._domain_relationships[domain].append((other_domain, 0.5))
    
    def _build_relationship_graph(self, rels: Dict[str, Any]) -> Dict[str, List[Tuple[str, float]]]:
        """Build relationship graph with strength weights."""
        graph: Dict[str, List[Tuple[str, float]]] = defaultdict(list)
        for source, targets in rels.items():
            if isinstance(targets, list):
                for target in targets:
                    if isinstance(target, dict):
                        strength = target.get("strength", 0.5)
                        target_name = target.get("domain", str(target))
                        graph[source].append((target_name, strength))
                    elif isinstance(target, str):
                        graph[source].append((target, 0.5))
        return graph
    
    def _load_patterns(self, patterns: Dict[str, Any]) -> None:
        """Load domain patterns for analysis."""
        for domain, pattern_list in patterns.items():
            if isinstance(pattern_list, list):
                self._pattern_db[domain] = pattern_list
    
    def query_across_domains(
        self, query: str, domains: List[str], max_results: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Query knowledge across multiple domains with relevance scoring.
        
        Args:
            query: Search query string
            domains: List of domains to search
            max_results: Maximum results to return
            
        Returns:
            List of matching entries sorted by relevance
            
        Raises:
            ValueError: If domains list is empty
        """
        if not domains:
            raise ValueError("At least one domain must be specified")
        
        results: List[Dict[str, Any]] = []
        query_lower = query.lower()
        query_tokens = set(query_lower.split())
        
        for domain in domains:
            # Query patterns for this domain
            patterns = self._pattern_db.get(domain, [])
            for idx, pattern in enumerate(patterns):
                relevance = self._calculate_relevance(query_tokens, pattern)
                if relevance > 0:
                    # Handle both dict and string patterns in result building
                    if isinstance(pattern, dict):
                        results.append({
                            "entry_id": pattern.get("id", f"{domain}-{idx}"),
                            "domain": domain,
                            "title": pattern.get("title", f"{domain} Entry"),
                            "content": pattern.get("content", ""),
                            "relevance": relevance,
                            "tags": pattern.get("tags", []),
                            "confidence": pattern.get("confidence", 0.8)
                        })
                    else:
                        results.append({
                            "entry_id": f"{domain}-{idx}",
                            "domain": domain,
                            "title": f"{domain} Entry",
                            "content": str(pattern),
                            "relevance": relevance,
                            "tags": [],
                            "confidence": 0.5
                        })
        
        # Sort by relevance descending
        results.sort(key=lambda x: x.get("relevance", 0), reverse=True)
        return results[:max_results]
    
    def _calculate_relevance(self, query_tokens: Set[str], pattern: Dict[str, Any]) -> float:
        """Calculate relevance score between query and pattern."""
        # Handle both dict and string patterns
        if isinstance(pattern, str):
            pattern_tokens = set(pattern.lower().split())
            jaccard_similarity = len(query_tokens & pattern_tokens) / max(len(query_tokens | pattern_tokens), 1)
            return min(jaccard_similarity, 1.0)
        
        if not isinstance(pattern, dict):
            return 0.0
            
        pattern_tokens = set(
            (pattern.get("title", "") + " " + pattern.get("content", "")).lower().split()
        )
        
        if not query_tokens:
            return 0.0
        
        intersection = query_tokens & pattern_tokens
        jaccard_similarity = len(intersection) / len(query_tokens | pattern_tokens)
        
        # Boost score for tag matches
        tag_matches = len([tag for tag in pattern.get("tags", []) if tag in query_tokens])
        tag_boost = min(tag_matches * 0.1, 0.3)
        
        return min(jaccard_similarity + tag_boost, 1.0)
    
    def synthesize(
        self, entries: List[Dict[str, Any]], domains: List[str]
    ) -> Dict[str, Any]:
        """
        Synthesize knowledge from multiple entries across domains.
        
        Implements cross-domain analysis:
        1. Pattern extraction from each entry
        2. Relationship identification
        3. Synthesis generation
        4. Confidence calculation
        
        Args:
            entries: List of knowledge entries to synthesize
            domains: Source domains
            
        Returns:
            Dictionary with synthesis result and metadata
            
        Raises:
            ValueError: If entries list is empty
        """
        if not entries:
            return self._create_empty_synthesis(domains)
        
        source_domains = list(set(entry.get("domain", "") for entry in entries if entry.get("domain")))
        
        # Extract patterns and find relationships
        patterns = self._extract_patterns(entries)
        relationships = self._identify_relationships(entries, source_domains)
        
        # Generate synthesis
        synthesized_text = self._generate_synthesis(entries, patterns, relationships)
        
        # Calculate confidence based on convergence and coverage
        confidence = self._calculate_synthesis_confidence(entries, patterns, relationships)
        
        synthesis_id = f"SYN-{datetime.now().strftime('%Y%m%d%H%M%S')}-{len(entries)}"
        
        result = {
            "synthesis_id": synthesis_id,
            "source_domains": source_domains or domains,
            "synthesized_knowledge": synthesized_text,
            "supporting_entries": entries,
            "relationships": relationships,
            "pattern_matches": patterns,
            "confidence": confidence,
            "created_at": datetime.now().isoformat(),
            "entry_count": len(entries),
            "domain_count": len(set(e.get("domain") for e in entries))
        }
        
        # Cache result
        self._synthesis_cache[synthesis_id] = (result, datetime.now())
        logger.info(f"Synthesis created: {synthesis_id} (confidence: {confidence:.2f})")
        
        return result
    
    def _create_empty_synthesis(self, domains: List[str]) -> Dict[str, Any]:
        """Create empty synthesis for empty input."""
        return {
            "synthesis_id": f"SYN-EMPTY-{datetime.now().isoformat()}",
            "source_domains": domains,
            "synthesized_knowledge": "No knowledge entries provided for synthesis",
            "supporting_entries": [],
            "relationships": [],
            "pattern_matches": [],
            "confidence": 0.0,
            "created_at": datetime.now().isoformat(),
            "entry_count": 0,
            "domain_count": 0
        }
    
    def _extract_patterns(self, entries: List[Dict[str, Any]]) -> List[str]:
        """Extract key patterns from entries."""
        patterns = []
        for entry in entries:
            content = entry.get("content", "").lower()
            tags = entry.get("tags", [])
            
            # Extract keywords
            if tags:
                patterns.extend([f"pattern:{tag}" for tag in tags[:3]])
            
            # Extract common words from content
            words = content.split()
            if words:
                patterns.extend([w for w in words[:5] if len(w) > 4])
        
        return list(set(patterns))[:10]  # Return top 10 unique patterns
    
    def _identify_relationships(
        self, entries: List[Dict[str, Any]], domains: List[str]
    ) -> List[Dict[str, Any]]:
        """Identify relationships between entries and domains."""
        relationships = []
        
        # Find inter-domain relationships
        for i, entry1 in enumerate(entries):
            for entry2 in entries[i+1:]:
                domain1 = entry1.get("domain", "")
                domain2 = entry2.get("domain", "")
                
                if domain1 != domain2:
                    # Check for shared tags
                    tags1 = set(entry1.get("tags", []))
                    tags2 = set(entry2.get("tags", []))
                    shared_tags = tags1 & tags2
                    
                    strength = min(len(shared_tags) * 0.2 + 0.3, 1.0)
                    
                    relationships.append({
                        "from_domain": domain1,
                        "to_domain": domain2,
                        "relationship_type": "cross_domain_synthesis",
                        "strength": strength,
                        "shared_concepts": list(shared_tags)
                    })
        
        return relationships
    
    def _generate_synthesis(
        self, 
        entries: List[Dict[str, Any]], 
        patterns: List[str],
        relationships: List[Dict[str, Any]]
    ) -> str:
        """Generate synthesis text from entries and patterns."""
        if not entries:
            return "No synthesis available"
        
        domains = set(e.get("domain", "unknown") for e in entries)
        concepts = []
        
        for entry in entries:
            if "title" in entry:
                concepts.append(entry["title"])
        
        synthesis = f"Cross-domain synthesis of {len(entries)} knowledge entries from {len(domains)} domains. "
        synthesis += f"Key concepts: {', '.join(concepts[:5])}. "
        synthesis += f"Identified patterns: {', '.join(patterns[:5])}. "
        
        if relationships:
            synthesis += f"Found {len(relationships)} cross-domain relationships with average strength {
                sum(r.get('strength', 0) for r in relationships) / len(relationships):.2f}."
        
        return synthesis
    
    def _calculate_synthesis_confidence(
        self,
        entries: List[Dict[str, Any]],
        patterns: List[str],
        relationships: List[Dict[str, Any]]
    ) -> float:
        """Calculate confidence score for synthesis."""
        if not entries:
            return 0.0
        
        # Base confidence from number of entries
        entry_confidence = min(len(entries) / 10.0, 1.0) * 0.4
        
        # Pattern match confidence
        pattern_confidence = min(len(patterns) / 10.0, 1.0) * 0.3
        
        # Relationship confidence
        rel_confidence = 0.0
        if relationships:
            avg_strength = sum(r.get("strength", 0) for r in relationships) / len(relationships)
            rel_confidence = avg_strength * 0.3
        
        return min(entry_confidence + pattern_confidence + rel_confidence, 1.0)
    
    def track_sources(self, synthesis_id: str) -> Dict[str, Any]:
        """
        Track and retrieve sources for a synthesis result.
        
        Args:
            synthesis_id: ID of synthesis to track
            
        Returns:
            Dictionary with source information
            
        Raises:
            KeyError: If synthesis ID not found
        """
        if synthesis_id not in self._synthesis_cache:
            raise KeyError(f"Synthesis ID not found: {synthesis_id}")
        
        result, created_at = self._synthesis_cache[synthesis_id]
        
        return {
            "synthesis_id": synthesis_id,
            "created_at": result.get("created_at"),
            "source_count": len(result.get("supporting_entries", [])),
            "domain_sources": result.get("source_domains", []),
            "entries": result.get("supporting_entries", [])
        }
    
    def get_domain_relationships(self) -> List[Dict[str, Any]]:
        """
        Get all domain relationships from the configuration.
        
        Returns:
            List of relationship dictionaries with strength information
        """
        relationships = []
        for source, targets in self._domain_relationships.items():
            for target, strength in targets:
                relationships.append({
                    "from_domain": source,
                    "to_domain": target,
                    "strength": strength,
                    "weight": strength
                })
        
        return relationships
    
    def get_related_domains(self, domain: str, min_strength: float = 0.3) -> List[str]:
        """
        Get domains related to given domain above strength threshold.
        
        Args:
            domain: Source domain
            min_strength: Minimum relationship strength
            
        Returns:
            List of related domain names
        """
        if domain not in self._domain_relationships:
            return []
        
        return [
            target for target, strength in self._domain_relationships[domain]
            if strength >= min_strength
        ]
    
    def find_relationships(self, domain1: str, domain2: str) -> List[Dict[str, Any]]:
        """
        Find direct relationships between two specific domains.
        
        Args:
            domain1: First domain
            domain2: Second domain
            
        Returns:
            List of relationships between domains
        """
        relationships = []
        
        if domain1 in self._domain_relationships:
            for target, strength in self._domain_relationships[domain1]:
                if target == domain2:
                    relationships.append({
                        "from_domain": domain1,
                        "to_domain": domain2,
                        "relationship_type": "related",
                        "strength": strength
                    })
        
        return relationships
    
    def get_synthesis(self, synthesis_id: str) -> Optional[Dict[str, Any]]:
        """
        Get cached synthesis result by ID.
        
        Args:
            synthesis_id: ID of synthesis to retrieve
            
        Returns:
            Synthesis result dict or None if not found/expired
        """
        if synthesis_id not in self._synthesis_cache:
            return None
        
        result, created_at = self._synthesis_cache[synthesis_id]
        
        # Check if result has expired
        if datetime.now() - created_at > self._cache_ttl:
            del self._synthesis_cache[synthesis_id]
            logger.info(f"Synthesis cache expired: {synthesis_id}")
            return None
        
        return result
    
    def clear_cache(self) -> None:
        """Clear the synthesis cache."""
        self._synthesis_cache.clear()
        logger.info("Synthesis cache cleared")
    
    def log_synthesis(self, result: SynthesisResult) -> None:
        """Log synthesis result to history for audit trail."""
        self._synthesis_history.append(result)
        logger.info(f"Synthesis result logged: {result.synthesis_id}")
    
    def get_synthesis_history(self) -> List[SynthesisResult]:
        """Get history of all synthesis operations."""
        return self._synthesis_history.copy()
    
    def apply_governance(self, result: SynthesisResult) -> bool:
        """Apply governance rules to synthesis result."""
        # Validate against governance policies
        if self.governance_manager:
            return self.governance_manager.validate(result)
        return True  # Default to allow if no governance manager
    
    def search_indexed_entries(self, query: str, domains: List[str]) -> List[Dict[str, Any]]:
        """Search using indexed entries for performance."""
        if self.indexer:
            return self.indexer.search(query, domains)
        # Fallback to regular query
        return self.query_across_domains(query, domains)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get synthesis engine metrics and statistics."""
        return {
            "total_syntheses": len(self._synthesis_history),
            "cached_results": len(self._synthesis_cache),
            "domains_available": len(self._domain_relationships),
            "patterns_loaded": sum(len(p) for p in self._pattern_db.values()),
            "ac_id": self.ac_id
        }


__all__ = ["SynthesisEngine", "SynthesisResult"]
