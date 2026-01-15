"""
Knowledge Retrieval Optimization System
========================================

AC-ID: KN-002-02
Purpose: Semantic search, intelligent ranking, and performance optimization

Provides:
- Semantic search capabilities
- Result ranking with multiple factors
- Caching mechanisms
- Query optimization
- Performance monitoring
"""

import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import time
import hashlib


@dataclass
class SearchResult:
    """Result from semantic search."""
    entry_id: str
    domain: str
    relevance_score: float
    quality_score: float
    rank: int
    excerpt: str = ""


class RetrievalOptimizer:
    """Knowledge retrieval optimization system."""
    
    VALID_DOMAINS = [
        "GOVERNANCE", "INTENT-ROUTING", "HALLUCINATION-PREVENTION",
        "EXECUTION-ORCHESTRATION", "DATA-MANAGEMENT", "OBSERVABILITY",
        "SECURITY", "API-DESIGN", "ML-MODELS", "KNOWLEDGE-CURATION",
        "TESTING-VALIDATION", "DEPLOYMENT", "DOCUMENTATION",
        "PERFORMANCE", "ARCHITECTURE", "ERROR-HANDLING"
    ]
    
    def __init__(self):
        """Initialize retrieval optimizer."""
        self.ac_id = "KN-002-02"
        self.config_path = Path("/Users/asifhussain/PROJECTS/CORTEX/cortex_brain/tier3/knowledge/retrieval-config.yaml")
        self.db_path = Path("/Users/asifhussain/PROJECTS/CORTEX/cortex_brain/state/governance.db")
        
        self.config = {}
        self.ranking_rules = []
        self.search_profiles = {}
        self.cache = {}
        self.metrics = {
            "searches": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "avg_search_time": 0.0
        }
        
        # Import dependencies
        try:
            from cortex_brain.tier3.knowledge.knowledge_indexer import KnowledgeIndexer
            from cortex_brain.tier3.knowledge.ai_curator import AICurator
            from cortex_brain.tier3.knowledge.synthesis_engine import SynthesisEngine
            
            self.indexer = KnowledgeIndexer()
            self.curator = AICurator()
            self.synthesizer = SynthesisEngine()
        except ImportError:
            self.indexer = None
            self.curator = None
            self.synthesizer = None
        
        self._load_config()
    
    def _load_config(self) -> None:
        """Load retrieval config from YAML."""
        if not self.config_path.exists():
            return
        
        with open(self.config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.ranking_rules = self.config.get("ranking_rules", [])
        self.search_profiles = self.config.get("search_profiles", {})
        self.stop_words = self.config.get("query_optimization", {}).get("stop_words", [])
    
    def semantic_search(self, query: str, domain: str = None, 
                       limit: int = 10, profile: str = "balanced") -> List[Dict[str, Any]]:
        """Perform semantic search."""
        if not query:
            return []
        
        # Check cache first
        cache_key = self._get_cache_key(query, domain, profile)
        if cache_key in self.cache:
            self.metrics["cache_hits"] += 1
            return self.cache[cache_key]
        
        self.metrics["cache_misses"] += 1
        self.metrics["searches"] += 1
        
        start_time = time.time()
        
        # Optimize query
        optimized_query = self.optimize_query(query)
        
        # Search results (mock implementation)
        results = []
        
        # If domain specified, filter
        if domain and domain not in self.VALID_DOMAINS:
            return results
        
        search_profile = self.search_profiles.get(profile, {})
        threshold = search_profile.get("similarity_threshold", 0.65)
        max_results = min(limit, search_profile.get("max_results", 100))
        
        # In real implementation, would search semantic index
        # For now, return empty list or mock results
        if self.indexer:
            try:
                if domain:
                    entries = self.indexer.get_entries_by_domain(domain) if hasattr(self.indexer, 'get_entries_by_domain') else []
                else:
                    entries = []
                
                for entry in entries[:max_results]:
                    results.append({
                        "entry_id": entry.get("entry_id", ""),
                        "domain": entry.get("domain", ""),
                        "relevance_score": 0.75,
                        "content": entry.get("content", "")
                    })
            except:
                pass
        
        # Rank results
        results = self.rank_results(results, preferred_domain=domain)
        
        # Cache if enabled
        if self.config.get("caching", {}).get("enabled", True):
            self.cache[cache_key] = results
        
        elapsed = time.time() - start_time
        self.metrics["avg_search_time"] = (self.metrics["avg_search_time"] + elapsed) / 2
        
        return results[:limit]
    
    def rank_results(self, entries: List[Dict[str, Any]], 
                    preferred_domain: str = None) -> List[Dict[str, Any]]:
        """Rank search results using multiple factors."""
        if not entries:
            return []
        
        # Calculate scores for each entry
        scored_entries = []
        
        for entry in entries:
            score = 0.0
            
            # Quality score
            quality = entry.get("quality", 0.5)
            score += quality * 0.35
            
            # Relevance score
            relevance = entry.get("relevance_score", 0.5)
            score += relevance * 0.30
            
            # Domain preference
            if preferred_domain and entry.get("domain") == preferred_domain:
                score += 0.15
            
            # Recency boost
            if "timestamp" in entry:
                score += 0.05
            
            entry["final_score"] = score
            scored_entries.append(entry)
        
        # Sort by score
        ranked = sorted(scored_entries, key=lambda x: x.get("final_score", 0), reverse=True)
        
        # Add rank field
        for i, entry in enumerate(ranked):
            entry["rank"] = i + 1
        
        return ranked
    
    def optimize_query(self, query: str) -> str:
        """Optimize query for better search."""
        if not query:
            return ""
        
        # Normalize whitespace
        optimized = " ".join(query.split())
        
        # Remove stop words
        words = optimized.split()
        filtered_words = [w for w in words if w.lower() not in self.stop_words]
        
        if filtered_words:
            optimized = " ".join(filtered_words)
        
        return optimized.lower()
    
    def clear_cache(self) -> None:
        """Clear search cache."""
        self.cache.clear()
        self.metrics["cache_hits"] = 0
        self.metrics["cache_misses"] = 0
    
    def _get_cache_key(self, query: str, domain: str, profile: str) -> str:
        """Generate cache key for search parameters."""
        key_str = f"{query}:{domain}:{profile}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get knowledge index statistics."""
        stats = {
            "total_entries": 0,
            "by_domain": {},
            "avg_quality": 0.0,
            "last_updated": datetime.now().isoformat()
        }
        
        if self.indexer:
            try:
                # Get stats from indexer
                for domain in self.VALID_DOMAINS:
                    if hasattr(self.indexer, 'get_entries_by_domain'):
                        entries = self.indexer.get_entries_by_domain(domain)
                        stats["by_domain"][domain] = len(entries) if entries else 0
                        stats["total_entries"] += len(entries) if entries else 0
            except:
                pass
        
        return stats
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get retrieval performance metrics."""
        cache_config = self.config.get("caching", {})
        
        total_searches = self.metrics["searches"]
        if total_searches > 0:
            cache_hit_rate = self.metrics["cache_hits"] / total_searches
        else:
            cache_hit_rate = 0.0
        
        return {
            "total_searches": self.metrics["searches"],
            "cache_hits": self.metrics["cache_hits"],
            "cache_misses": self.metrics["cache_misses"],
            "cache_hit_rate": cache_hit_rate,
            "avg_search_time_ms": self.metrics["avg_search_time"] * 1000,
            "cache_entries": len(self.cache),
            "cache_enabled": cache_config.get("enabled", True),
            "cache_ttl_seconds": cache_config.get("ttl_seconds", 3600)
        }


# Convenience instance
_optimizer_instance = None

def get_retrieval_optimizer() -> RetrievalOptimizer:
    """Get singleton retrieval optimizer instance."""
    global _optimizer_instance
    if _optimizer_instance is None:
        _optimizer_instance = RetrievalOptimizer()
    return _optimizer_instance
