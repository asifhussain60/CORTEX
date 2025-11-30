"""
Lazy Loading Manager for Dashboard

Implements incremental data loading and lazy rendering for large datasets
to optimize initial page load and improve perceived performance.

Author: Asif Hussain
Created: 2025-11-30
CORTEX Version: 3.3.0

Performance Targets:
- Initial page load: <2s (without visualizations)
- Lazy load trigger: < 100ms after scroll/click
- Incremental render: 50 items per batch, 60 FPS
"""

from typing import List, Dict, Any, TypeVar, Generic, Callable
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class LazyLoadConfig:
    """Configuration for lazy loading behavior."""
    batch_size: int = 50  # Items per batch
    initial_batch_size: int = 25  # Smaller first batch for faster initial render
    trigger_threshold: float = 0.8  # Load more when 80% scrolled
    enable_virtualization: bool = True  # Use virtual scrolling for large lists
    max_items_in_memory: int = 500  # Keep at most 500 items in DOM


class LazyDataLoader(Generic[T]):
    """
    Generic lazy data loader with batch loading and pagination.
    
    Optimizes performance by loading data incrementally:
    1. Initial batch loads quickly (25 items)
    2. Additional batches load on demand (50 items each)
    3. Virtual scrolling removes off-screen items
    
    Example:
        loader = LazyDataLoader(all_components, config)
        initial_batch = loader.get_next_batch()  # First 25 items
        next_batch = loader.get_next_batch()  # Next 50 items
    """
    
    def __init__(
        self,
        data: List[T],
        config: LazyLoadConfig = None
    ):
        """
        Initialize lazy loader with data.
        
        Args:
            data: Complete dataset to load incrementally
            config: Lazy loading configuration
        """
        self.data = data
        self.config = config or LazyLoadConfig()
        self.current_index = 0
        self.batches_loaded = 0
        self.total_batches = self._calculate_total_batches()
        
        logger.info(
            f"LazyDataLoader initialized: {len(data)} items, "
            f"{self.total_batches} batches"
        )
    
    def get_next_batch(self) -> List[T]:
        """
        Get next batch of data.
        
        Returns:
            List of items in next batch (empty if no more data)
        """
        if self.current_index >= len(self.data):
            return []
        
        # First batch is smaller for faster initial render
        batch_size = (
            self.config.initial_batch_size 
            if self.batches_loaded == 0 
            else self.config.batch_size
        )
        
        end_index = min(self.current_index + batch_size, len(self.data))
        batch = self.data[self.current_index:end_index]
        
        self.current_index = end_index
        self.batches_loaded += 1
        
        logger.debug(
            f"Loaded batch {self.batches_loaded}/{self.total_batches}: "
            f"{len(batch)} items (total loaded: {self.current_index}/{len(self.data)})"
        )
        
        return batch
    
    def has_more(self) -> bool:
        """Check if more data is available."""
        return self.current_index < len(self.data)
    
    def get_progress(self) -> float:
        """Get loading progress as percentage (0.0 to 1.0)."""
        if not self.data:
            return 1.0
        return self.current_index / len(self.data)
    
    def reset(self) -> None:
        """Reset loader to beginning."""
        self.current_index = 0
        self.batches_loaded = 0
        logger.debug("LazyDataLoader reset")
    
    def _calculate_total_batches(self) -> int:
        """Calculate total number of batches."""
        if not self.data:
            return 0
        
        # First batch + remaining batches
        remaining = len(self.data) - self.config.initial_batch_size
        if remaining <= 0:
            return 1
        
        return 1 + ((remaining + self.config.batch_size - 1) // self.config.batch_size)


class UMLDiagramLazyLoader:
    """
    Specialized lazy loader for UML diagrams.
    
    Features:
    - Load UML on tab activation (not on page load)
    - Progressive rendering for complex diagrams
    - Cache rendered SVG for instant re-display
    - Fallback to placeholder while loading
    """
    
    def __init__(self):
        """Initialize UML lazy loader."""
        self._loaded_diagrams: Dict[str, str] = {}  # diagram_id -> SVG content
        self._loading_states: Dict[str, bool] = {}  # diagram_id -> is_loading
        
        logger.info("UMLDiagramLazyLoader initialized")
    
    def should_load_diagram(self, diagram_id: str) -> bool:
        """
        Check if diagram should be loaded.
        
        Args:
            diagram_id: Unique diagram identifier
            
        Returns:
            True if diagram needs loading, False if cached
        """
        return diagram_id not in self._loaded_diagrams
    
    def mark_loading(self, diagram_id: str) -> None:
        """
        Mark diagram as currently loading.
        
        Args:
            diagram_id: Unique diagram identifier
        """
        self._loading_states[diagram_id] = True
        logger.debug(f"UML diagram {diagram_id} marked as loading")
    
    def cache_diagram(self, diagram_id: str, svg_content: str) -> None:
        """
        Cache rendered UML diagram.
        
        Args:
            diagram_id: Unique diagram identifier
            svg_content: Rendered SVG content
        """
        self._loaded_diagrams[diagram_id] = svg_content
        self._loading_states[diagram_id] = False
        
        size_kb = len(svg_content) / 1024
        logger.info(
            f"UML diagram {diagram_id} cached ({size_kb:.1f}KB, "
            f"total cached: {len(self._loaded_diagrams)})"
        )
    
    def get_cached_diagram(self, diagram_id: str) -> str | None:
        """
        Get cached diagram if available.
        
        Args:
            diagram_id: Unique diagram identifier
            
        Returns:
            SVG content or None if not cached
        """
        return self._loaded_diagrams.get(diagram_id)
    
    def is_loading(self, diagram_id: str) -> bool:
        """
        Check if diagram is currently loading.
        
        Args:
            diagram_id: Unique diagram identifier
            
        Returns:
            True if loading, False otherwise
        """
        return self._loading_states.get(diagram_id, False)
    
    def clear_cache(self) -> None:
        """Clear all cached diagrams."""
        count = len(self._loaded_diagrams)
        self._loaded_diagrams.clear()
        self._loading_states.clear()
        logger.info(f"UML diagram cache cleared ({count} diagrams)")


class IncrementalRenderer:
    """
    Incremental renderer for large datasets with progress tracking.
    
    Renders data in small chunks to maintain 60 FPS and provide
    visual feedback during rendering.
    """
    
    def __init__(
        self,
        data: List[T],
        chunk_size: int = 10,
        on_progress: Callable[[int, int], None] = None
    ):
        """
        Initialize incremental renderer.
        
        Args:
            data: Data to render
            chunk_size: Items per render chunk (smaller = smoother, slower)
            on_progress: Callback(current, total) for progress updates
        """
        self.data = data
        self.chunk_size = chunk_size
        self.on_progress = on_progress
        self.current_index = 0
        
        logger.info(
            f"IncrementalRenderer initialized: {len(data)} items, "
            f"chunk_size: {chunk_size}"
        )
    
    def render_next_chunk(self, render_fn: Callable[[List[T]], None]) -> bool:
        """
        Render next chunk of data.
        
        Args:
            render_fn: Function to render a chunk of items
            
        Returns:
            True if more chunks remain, False if complete
        """
        if self.current_index >= len(self.data):
            return False
        
        end_index = min(self.current_index + self.chunk_size, len(self.data))
        chunk = self.data[self.current_index:end_index]
        
        # Render chunk
        render_fn(chunk)
        
        self.current_index = end_index
        
        # Report progress
        if self.on_progress:
            self.on_progress(self.current_index, len(self.data))
        
        logger.debug(
            f"Rendered chunk: {len(chunk)} items "
            f"({self.current_index}/{len(self.data)})"
        )
        
        return self.current_index < len(self.data)
    
    def get_progress_percentage(self) -> int:
        """Get rendering progress as percentage (0-100)."""
        if not self.data:
            return 100
        return int((self.current_index / len(self.data)) * 100)


def create_lazy_loader_config(
    total_items: int,
    performance_tier: str = 'standard'
) -> LazyLoadConfig:
    """
    Create optimized lazy load configuration based on dataset size.
    
    Args:
        total_items: Total number of items to load
        performance_tier: 'fast' (aggressive caching), 'standard', or 'memory-efficient'
        
    Returns:
        Optimized LazyLoadConfig
    """
    if total_items < 100:
        # Small dataset: Load all at once
        return LazyLoadConfig(
            batch_size=total_items,
            initial_batch_size=total_items,
            enable_virtualization=False
        )
    elif total_items < 500:
        # Medium dataset: Standard lazy loading
        return LazyLoadConfig(
            batch_size=50,
            initial_batch_size=25,
            enable_virtualization=True,
            max_items_in_memory=500
        )
    else:
        # Large dataset: Aggressive lazy loading
        if performance_tier == 'fast':
            return LazyLoadConfig(
                batch_size=100,
                initial_batch_size=50,
                enable_virtualization=True,
                max_items_in_memory=1000
            )
        elif performance_tier == 'memory-efficient':
            return LazyLoadConfig(
                batch_size=25,
                initial_batch_size=10,
                enable_virtualization=True,
                max_items_in_memory=200
            )
        else:  # standard
            return LazyLoadConfig(
                batch_size=50,
                initial_batch_size=25,
                enable_virtualization=True,
                max_items_in_memory=500
            )


# Global UML diagram lazy loader
_uml_lazy_loader = UMLDiagramLazyLoader()


def get_uml_lazy_loader() -> UMLDiagramLazyLoader:
    """Get global UML lazy loader instance."""
    return _uml_lazy_loader
