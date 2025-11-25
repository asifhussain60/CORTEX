"""
Async Pattern Retrieval

Asynchronous pattern retrieval from Tier 2 store with parallel query support.

Copyright (c) 2024-2025 Asif Hussain. All rights reserved.
"""

import asyncio
import sqlite3
from typing import List, Optional, Dict, Any
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from .tier2_pattern_store import Tier2PatternStore, BusinessPattern


@dataclass
class RetrievalRequest:
    """Pattern retrieval request"""
    query: str
    domain: Optional[str] = None
    min_confidence: float = 0.5
    limit: int = 10


@dataclass
class RetrievalResult:
    """Pattern retrieval result"""
    request: RetrievalRequest
    patterns: List[BusinessPattern]
    duration_ms: float
    source: str  # 'cache' or 'database'


class AsyncPatternRetriever:
    """
    Asynchronous pattern retrieval with parallel query support.
    
    Phase 2 Milestone 2.3 - Performance Optimization
    Target: Enable parallel pattern retrieval for multiple domains
    
    Note: Creates per-thread connections to avoid SQLite threading issues.
    """
    
    def __init__(
        self,
        db_path: str,
        max_workers: int = 4
    ):
        """
        Initialize async retriever.
        
        Args:
            db_path: Path to pattern store database
            max_workers: Maximum concurrent workers
        """
        self.db_path = db_path
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
        # Simple in-memory cache for recent queries
        self.query_cache: Dict[str, List[BusinessPattern]] = {}
        self.cache_max_size = 100
    
    def _cache_key(self, request: RetrievalRequest) -> str:
        """Generate cache key from request"""
        return f"{request.query}:{request.domain}:{request.min_confidence}:{request.limit}"
    
    async def retrieve_patterns(
        self,
        request: RetrievalRequest
    ) -> RetrievalResult:
        """
        Retrieve patterns asynchronously.
        
        Args:
            request: Retrieval request
            
        Returns:
            RetrievalResult with patterns and metadata
        """
        import time
        start_time = time.time()
        
        # Check cache first
        cache_key = self._cache_key(request)
        if cache_key in self.query_cache:
            duration_ms = (time.time() - start_time) * 1000
            return RetrievalResult(
                request=request,
                patterns=self.query_cache[cache_key],
                duration_ms=duration_ms,
                source='cache'
            )
        
        # Run database query in thread pool
        loop = asyncio.get_event_loop()
        patterns = await loop.run_in_executor(
            self.executor,
            self._sync_retrieve,
            request
        )
        
        # Cache result
        if len(self.query_cache) >= self.cache_max_size:
            # Remove oldest entry (simple FIFO)
            first_key = next(iter(self.query_cache))
            del self.query_cache[first_key]
        
        self.query_cache[cache_key] = patterns
        
        duration_ms = (time.time() - start_time) * 1000
        
        return RetrievalResult(
            request=request,
            patterns=patterns,
            duration_ms=duration_ms,
            source='database'
        )
    
    def _sync_retrieve(self, request: RetrievalRequest) -> List[BusinessPattern]:
        """Synchronous pattern retrieval (runs in executor) - creates own connection"""
        # Create thread-local connection
        store = Tier2PatternStore(self.db_path)
        
        try:
            if request.domain:
                return store.get_patterns_by_domain(
                    domain=request.domain,
                    min_confidence=request.min_confidence,
                    limit=request.limit
                )
            else:
                return store.search_patterns(
                    query=request.query,
                    domain=None,
                    min_confidence=request.min_confidence,
                    limit=request.limit
                )
        finally:
            store.close()
    
    async def retrieve_batch(
        self,
        requests: List[RetrievalRequest]
    ) -> List[RetrievalResult]:
        """
        Retrieve multiple pattern sets in parallel.
        
        Args:
            requests: List of retrieval requests
            
        Returns:
            List of retrieval results
        """
        tasks = [
            self.retrieve_patterns(request)
            for request in requests
        ]
        
        results = await asyncio.gather(*tasks)
        return list(results)
    
    async def retrieve_multi_domain(
        self,
        query: str,
        domains: List[str],
        min_confidence: float = 0.5,
        limit_per_domain: int = 10
    ) -> Dict[str, RetrievalResult]:
        """
        Retrieve patterns from multiple domains in parallel.
        
        Args:
            query: Search query
            domains: List of domains to search
            min_confidence: Minimum confidence threshold
            limit_per_domain: Limit per domain
            
        Returns:
            Dictionary mapping domain to retrieval results
        """
        requests = [
            RetrievalRequest(
                query=query,
                domain=domain,
                min_confidence=min_confidence,
                limit=limit_per_domain
            )
            for domain in domains
        ]
        
        results = await self.retrieve_batch(requests)
        
        return {
            result.request.domain: result
            for result in results
            if result.request.domain is not None
        }
    
    def clear_cache(self) -> None:
        """Clear query cache"""
        self.query_cache.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        return {
            'cache_size': len(self.query_cache),
            'cache_max_size': self.cache_max_size,
            'max_workers': self.max_workers
        }
    
    def shutdown(self) -> None:
        """Shutdown executor"""
        self.executor.shutdown(wait=True)
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.shutdown()


# Helper functions for common async patterns

async def retrieve_for_function(
    retriever: AsyncPatternRetriever,
    function_name: str,
    domains: List[str],
    min_confidence: float = 0.5
) -> Dict[str, List[BusinessPattern]]:
    """
    Retrieve patterns for a function across multiple domains.
    
    Args:
        retriever: AsyncPatternRetriever instance
        function_name: Function name to search for
        domains: List of domains to search
        min_confidence: Minimum confidence threshold
        
    Returns:
        Dictionary mapping domain to pattern lists
    """
    results = await retriever.retrieve_multi_domain(
        query=function_name,
        domains=domains,
        min_confidence=min_confidence
    )
    
    return {
        domain: result.patterns
        for domain, result in results.items()
    }


async def retrieve_with_fallback(
    retriever: AsyncPatternRetriever,
    primary_request: RetrievalRequest,
    fallback_request: RetrievalRequest
) -> RetrievalResult:
    """
    Retrieve patterns with fallback if primary returns empty.
    
    Args:
        retriever: AsyncPatternRetriever instance
        primary_request: Primary retrieval request
        fallback_request: Fallback request if primary is empty
        
    Returns:
        RetrievalResult from primary or fallback
    """
    result = await retriever.retrieve_patterns(primary_request)
    
    if not result.patterns:
        result = await retriever.retrieve_patterns(fallback_request)
    
    return result
