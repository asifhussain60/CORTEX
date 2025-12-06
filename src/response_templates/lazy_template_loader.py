"""
Lazy Template Loader for Distributed Response Templates

This module provides on-demand template loading with caching to support
the distributed template architecture. Templates are loaded only when needed
and cached for performance.

Architecture:
- Registry-based file lookup (O(1) template ID → file path)
- 5-minute cache with TTL to balance performance and memory
- Performance monitoring for load times
- Graceful fallback to monolithic file if distributed files not found

Performance Targets:
- Template load time: <10ms (vs 200-500ms monolithic)
- Cache hit rate: >80%
- Memory overhead: <5MB for 27 templates

Author: Asif Hussain
Phase: 2 - Core Infrastructure
Version: 1.0
Created: December 5, 2025
"""

import yaml
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@dataclass
class CachedTemplate:
    """Represents a cached template with metadata."""
    template_id: str
    content: Dict[str, Any]
    loaded_at: datetime
    file_path: Path
    load_time_ms: float
    
    def is_expired(self, ttl_seconds: int = 300) -> bool:
        """Check if cache entry has expired (default 5 min TTL)."""
        return datetime.now() - self.loaded_at > timedelta(seconds=ttl_seconds)


@dataclass
class LoadMetrics:
    """Performance metrics for template loading."""
    total_loads: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    total_load_time_ms: float = 0.0
    avg_load_time_ms: float = 0.0
    
    @property
    def cache_hit_rate(self) -> float:
        """Calculate cache hit rate percentage."""
        if self.total_loads == 0:
            return 0.0
        return (self.cache_hits / self.total_loads) * 100
    
    def record_load(self, load_time_ms: float, was_cached: bool):
        """Record a template load event."""
        self.total_loads += 1
        if was_cached:
            self.cache_hits += 1
        else:
            self.cache_misses += 1
            self.total_load_time_ms += load_time_ms
            if self.cache_misses > 0:
                self.avg_load_time_ms = self.total_load_time_ms / self.cache_misses


class LazyTemplateLoader:
    """
    Lazy-loading template system with registry-based lookup and caching.
    
    Features:
    - On-demand template loading (only load what's needed)
    - Registry-based file mapping (template ID → file path)
    - 5-minute cache with automatic TTL expiration
    - Performance monitoring and metrics
    - Graceful fallback to monolithic file
    
    Usage:
        loader = LazyTemplateLoader(
            template_dir=Path("cortex-brain/response-templates"),
            registry_file=Path("cortex-brain/response-templates/config/template-registry.yaml")
        )
        
        template = loader.load_template("planning")
        print(f"Cache hit rate: {loader.metrics.cache_hit_rate:.1f}%")
    """
    
    def __init__(
        self,
        template_dir: Path,
        registry_file: Optional[Path] = None,
        cache_ttl_seconds: int = 300,
        enable_metrics: bool = True
    ):
        """
        Initialize lazy template loader.
        
        Args:
            template_dir: Base directory for distributed templates
            registry_file: Path to template-registry.yaml (auto-detected if None)
            cache_ttl_seconds: Cache TTL in seconds (default: 300 = 5 minutes)
            enable_metrics: Enable performance metrics tracking
        """
        self.template_dir = template_dir
        self.cache_ttl_seconds = cache_ttl_seconds
        self.enable_metrics = enable_metrics
        
        # Cache storage: template_id → CachedTemplate
        self.cache: Dict[str, CachedTemplate] = {}
        
        # Performance metrics
        self.metrics = LoadMetrics()
        
        # Registry: template_id → relative file path
        self.registry: Dict[str, str] = {}
        
        # Detect registry file
        if registry_file is None:
            registry_file = template_dir / "config" / "template-registry.yaml"
        
        self.registry_file = registry_file
        
        # Fallback to monolithic file
        self.monolithic_file = template_dir.parent / "response-templates.yaml"
        
        # Load registry
        self._load_registry()
        
        logger.info(
            f"LazyTemplateLoader initialized: {len(self.registry)} templates, "
            f"cache TTL: {cache_ttl_seconds}s"
        )
    
    def _load_registry(self):
        """Load template registry from YAML file."""
        if not self.registry_file.exists():
            logger.warning(
                f"Registry file not found: {self.registry_file}. "
                f"Will attempt to use monolithic file as fallback."
            )
            return
        
        try:
            with open(self.registry_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # Extract template ID → file path mapping
            templates = data.get('templates', {})
            for template_id, template_info in templates.items():
                file_path = template_info.get('file')
                if file_path:
                    self.registry[template_id] = file_path
            
            logger.info(f"Registry loaded: {len(self.registry)} template mappings")
        
        except Exception as e:
            logger.error(f"Failed to load registry: {e}")
    
    def load_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """
        Load template by ID with caching.
        
        Args:
            template_id: Template identifier (e.g., 'planning', 'help_table')
        
        Returns:
            Template content dictionary, or None if not found
        
        Performance:
            - Cache hit: <1ms
            - Cache miss: <10ms (distributed file)
            - Fallback: 200-500ms (monolithic file)
        """
        start_time = time.perf_counter()
        
        # Check cache first
        if template_id in self.cache:
            cached = self.cache[template_id]
            
            # Check if cache entry is still valid
            if not cached.is_expired(self.cache_ttl_seconds):
                load_time = (time.perf_counter() - start_time) * 1000
                
                if self.enable_metrics:
                    self.metrics.record_load(load_time, was_cached=True)
                
                logger.debug(f"Cache HIT: {template_id} ({load_time:.2f}ms)")
                return cached.content
            else:
                # Cache expired, remove entry
                logger.debug(f"Cache EXPIRED: {template_id}")
                del self.cache[template_id]
        
        # Cache miss - load from file
        logger.debug(f"Cache MISS: {template_id}")
        
        # Try distributed file first
        content = self._load_from_distributed_file(template_id)
        
        # Fallback to monolithic file
        if content is None:
            content = self._load_from_monolithic_file(template_id)
        
        load_time = (time.perf_counter() - start_time) * 1000
        
        # Cache the loaded template
        if content is not None:
            file_path = self._get_template_file_path(template_id)
            self.cache[template_id] = CachedTemplate(
                template_id=template_id,
                content=content,
                loaded_at=datetime.now(),
                file_path=file_path,
                load_time_ms=load_time
            )
        
        if self.enable_metrics:
            self.metrics.record_load(load_time, was_cached=False)
        
        logger.info(
            f"Template loaded: {template_id} ({load_time:.2f}ms, "
            f"source: {'distributed' if content else 'not found'})"
        )
        
        return content
    
    def _load_from_distributed_file(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Load template from distributed file structure."""
        file_path = self._get_template_file_path(template_id)
        
        if not file_path or not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # Extract template by ID from file
            # File may contain multiple templates or single template
            if isinstance(data, dict):
                # Check for templates wrapper (migration format)
                if 'templates' in data and isinstance(data['templates'], dict):
                    templates = data['templates']
                    if template_id in templates:
                        return templates[template_id]
                
                # If file has template ID as key, extract it
                if template_id in data:
                    return data[template_id]
                
                # Otherwise return entire content
                return data
            
            return None
        
        except Exception as e:
            logger.error(f"Failed to load distributed template {template_id}: {e}")
            return None
    
    def _load_from_monolithic_file(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Fallback: Load template from monolithic response-templates.yaml."""
        if not self.monolithic_file.exists():
            logger.warning(f"Monolithic file not found: {self.monolithic_file}")
            return None
        
        try:
            with open(self.monolithic_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # Extract template from templates section
            templates = data.get('templates', {})
            if template_id in templates:
                logger.debug(f"Loaded {template_id} from monolithic file (fallback)")
                return templates[template_id]
            
            return None
        
        except Exception as e:
            logger.error(f"Failed to load from monolithic file: {e}")
            return None
    
    def _get_template_file_path(self, template_id: str) -> Optional[Path]:
        """Get absolute file path for template ID from registry."""
        relative_path = self.registry.get(template_id)
        if not relative_path:
            return None
        
        return self.template_dir / relative_path
    
    def clear_cache(self, template_id: Optional[str] = None):
        """
        Clear template cache.
        
        Args:
            template_id: If provided, clear only this template. Otherwise clear all.
        """
        if template_id:
            if template_id in self.cache:
                del self.cache[template_id]
                logger.info(f"Cache cleared: {template_id}")
        else:
            count = len(self.cache)
            self.cache.clear()
            logger.info(f"Cache cleared: {count} templates")
    
    def preload_templates(self, template_ids: List[str]):
        """
        Preload multiple templates into cache.
        
        Useful for warming up cache before high-demand operations.
        
        Args:
            template_ids: List of template IDs to preload
        """
        logger.info(f"Preloading {len(template_ids)} templates...")
        
        for template_id in template_ids:
            self.load_template(template_id)
        
        logger.info(f"Preload complete: {len(template_ids)} templates cached")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics as dictionary."""
        return {
            'total_loads': self.metrics.total_loads,
            'cache_hits': self.metrics.cache_hits,
            'cache_misses': self.metrics.cache_misses,
            'cache_hit_rate_pct': round(self.metrics.cache_hit_rate, 1),
            'avg_load_time_ms': round(self.metrics.avg_load_time_ms, 2),
            'cached_templates': len(self.cache),
            'registry_size': len(self.registry),
        }
    
    def get_cached_template_ids(self) -> List[str]:
        """Get list of currently cached template IDs."""
        return list(self.cache.keys())
    
    def reload_registry(self):
        """Reload template registry from file (useful after registry updates)."""
        logger.info("Reloading template registry...")
        self.registry.clear()
        self._load_registry()
        logger.info(f"Registry reloaded: {len(self.registry)} templates")
