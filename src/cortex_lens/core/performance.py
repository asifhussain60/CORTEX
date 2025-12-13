"""
Performance Configuration & System Detection

Auto-detects optimal performance settings based on system resources.
Provides configuration for multi-threaded processing and memory management.

Author: Asif Hussain
"""

import os
import logging
import psutil
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class PerformanceConfig:
    """
    Auto-detected performance configuration.
    
    Detects system resources and provides optimal settings for:
    - Multi-threaded processing
    - Memory management
    - Cache sizing
    - Worker pool sizing
    """
    
    cpu_count: int
    physical_cores: int
    memory_total_gb: float
    memory_available_gb: float
    optimal_workers: int
    max_workers: int
    cache_size_mb: int
    memory_limit_gb: float
    
    @classmethod
    def detect(cls, user_workers: Optional[int] = None) -> 'PerformanceConfig':
        """
        Detect system capabilities and create optimal config.
        
        Args:
            user_workers: Optional user-specified worker count (overrides auto-detection)
        
        Returns:
            PerformanceConfig with optimal settings
        """
        # CPU Detection
        cpu_count = os.cpu_count() or 4
        physical_cores = psutil.cpu_count(logical=False) or cpu_count
        
        # Memory Detection
        memory = psutil.virtual_memory()
        memory_total_gb = memory.total / (1024 ** 3)
        memory_available_gb = memory.available / (1024 ** 3)
        
        # Worker Pool Sizing
        # Strategy: Use physical cores - 1 (leave one for system)
        # But cap at available memory (assume 500MB per worker)
        memory_based_workers = int(memory_available_gb / 0.5)
        optimal_workers = min(physical_cores - 1, memory_based_workers)
        optimal_workers = max(1, optimal_workers)  # At least 1
        
        # Override if user specified
        if user_workers:
            optimal_workers = user_workers
        
        # Max workers (for burst capacity)
        max_workers = min(cpu_count, int(memory_available_gb / 0.3))
        max_workers = max(optimal_workers, max_workers)
        
        # Cache sizing (10% of available memory, capped at 500MB)
        cache_size_mb = int(min(memory_available_gb * 0.1 * 1024, 500))
        
        # Memory limit per worker (90% of available / workers)
        memory_limit_gb = (memory_available_gb * 0.9) / optimal_workers
        
        config = cls(
            cpu_count=cpu_count,
            physical_cores=physical_cores,
            memory_total_gb=round(memory_total_gb, 2),
            memory_available_gb=round(memory_available_gb, 2),
            optimal_workers=optimal_workers,
            max_workers=max_workers,
            cache_size_mb=cache_size_mb,
            memory_limit_gb=round(memory_limit_gb, 2)
        )
        
        logger.info(f"🔧 Performance Config Detected:")
        logger.info(f"   CPU: {cpu_count} logical, {physical_cores} physical cores")
        logger.info(f"   Memory: {memory_total_gb:.1f} GB total, {memory_available_gb:.1f} GB available")
        logger.info(f"   Workers: {optimal_workers} optimal, {max_workers} max")
        logger.info(f"   Cache: {cache_size_mb} MB, Memory Limit: {memory_limit_gb:.1f} GB/worker")
        
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'cpu_count': self.cpu_count,
            'physical_cores': self.physical_cores,
            'memory_total_gb': self.memory_total_gb,
            'memory_available_gb': self.memory_available_gb,
            'optimal_workers': self.optimal_workers,
            'max_workers': self.max_workers,
            'cache_size_mb': self.cache_size_mb,
            'memory_limit_gb': self.memory_limit_gb
        }
    
    def validate_memory_usage(self, current_usage_gb: float) -> bool:
        """
        Check if current memory usage is within safe limits.
        
        Args:
            current_usage_gb: Current memory usage in GB
        
        Returns:
            True if within limits, False if approaching limit
        """
        threshold = self.memory_limit_gb * 0.9  # 90% of limit
        return current_usage_gb < threshold
    
    def should_scale_down(self) -> bool:
        """
        Check if system should scale down workers (low memory).
        
        Returns:
            True if memory pressure detected
        """
        memory = psutil.virtual_memory()
        return memory.percent > 85  # >85% memory usage
    
    def get_chunk_size(self, total_items: int) -> int:
        """
        Calculate optimal chunk size for parallel processing.
        
        Args:
            total_items: Total number of items to process
        
        Returns:
            Optimal chunk size
        """
        # Strategy: At least 10 items per worker, but not too small
        min_chunk = 10
        max_chunk = 100
        
        chunk = total_items // (self.optimal_workers * 4)
        chunk = max(min_chunk, min(chunk, max_chunk))
        
        return chunk
