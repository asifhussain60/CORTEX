"""
CORTEX 3.0 Performance Optimization System
==========================================

Production-grade performance monitoring, caching, and optimization
for enterprise-scale documentation generation.

Features:
- Intelligent caching with TTL and invalidation
- Async processing for large documentation sets
- Resource optimization and memory management
- Performance monitoring and metrics collection
- Load balancing and request queuing
"""

from .cache_manager import CacheManager
from .async_processor import AsyncDocumentProcessor
from .performance_monitor import PerformanceMonitor
from .resource_optimizer import ResourceOptimizer
from .load_balancer import LoadBalancer

__version__ = "3.0.0"
__all__ = [
    'CacheManager',
    'AsyncDocumentProcessor', 
    'PerformanceMonitor',
    'ResourceOptimizer',
    'LoadBalancer'
]