"""
CORTEX 3.0 Phase 2 - Brain Memory Manager
=========================================

Intelligent memory management for optimal brain performance and resource utilization.
Manages memory allocation, garbage collection, and performance optimization.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

Phase: Phase 2 - Brain Performance Optimization (Task 2)
Integration: Memory Management + Query Cache + Optimization Engine
"""

import gc
import os
import sys
import psutil
import threading
import time
from typing import Dict, List, Any, Optional, Tuple, NamedTuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
import logging
import json
from enum import Enum
import weakref
import tracemalloc
from collections import defaultdict


class MemoryZone(Enum):
    """Memory management zones."""
    TIER1_WORKING = "tier1_working"      # Active conversation memory
    TIER2_KNOWLEDGE = "tier2_knowledge"  # Knowledge graph cache
    TIER3_CONTEXT = "tier3_context"      # Development context
    QUERY_CACHE = "query_cache"          # Query result cache
    SYSTEM_OVERHEAD = "system_overhead"  # System memory overhead


class MemoryPressure(Enum):
    """Memory pressure levels."""
    LOW = "low"        # <100MB usage
    MEDIUM = "medium"  # 100-300MB usage
    HIGH = "high"      # 300-500MB usage
    CRITICAL = "critical"  # >500MB usage


@dataclass
class MemoryAllocation:
    """Memory allocation tracking."""
    zone: MemoryZone
    size_bytes: int
    timestamp: datetime
    allocation_id: str
    description: str
    is_active: bool


@dataclass
class MemoryMetrics:
    """Memory usage metrics."""
    total_memory_mb: float
    zone_allocations: Dict[str, float]
    pressure_level: MemoryPressure
    gc_collections: int
    memory_leaks_detected: int
    optimization_opportunities: List[str]
    last_cleanup: Optional[datetime]


class MemoryPool:
    """Memory pool for specific zones with intelligent allocation."""
    
    def __init__(self, zone: MemoryZone, max_size_mb: int = 50):
        """
        Initialize memory pool.
        
        Args:
            zone: Memory zone type
            max_size_mb: Maximum pool size in MB
        """
        self.zone = zone
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.current_size_bytes = 0
        
        # Allocation tracking
        self.allocations: Dict[str, MemoryAllocation] = {}
        self.allocation_counter = 0
        self.total_allocations = 0
        self.total_deallocations = 0
        
        # Weak references for automatic cleanup
        self.weak_refs: Dict[str, weakref.ref] = {}
        
        # Performance metrics
        self.peak_usage_bytes = 0
        self.fragmentation_level = 0.0
        
        # Lock for thread safety
        self.lock = threading.RLock()
        
        # Logger
        self.logger = logging.getLogger(f"{__name__}.{zone.value}")
    
    def allocate(self, size_bytes: int, description: str = "") -> Optional[str]:
        """
        Allocate memory from pool.
        
        Args:
            size_bytes: Size to allocate
            description: Allocation description
            
        Returns:
            Allocation ID if successful
        """
        with self.lock:
            # Check if allocation would exceed pool limit
            if self.current_size_bytes + size_bytes > self.max_size_bytes:
                # Try to free some memory first
                freed = self.cleanup_inactive_allocations()
                self.logger.info(f"Freed {freed} bytes for new allocation")
                
                # Check again
                if self.current_size_bytes + size_bytes > self.max_size_bytes:
                    self.logger.warning(f"Pool {self.zone.value} at capacity: {self.current_size_bytes}/{self.max_size_bytes}")
                    return None
            
            # Create allocation
            self.allocation_counter += 1
            allocation_id = f"{self.zone.value}_{self.allocation_counter}"
            
            allocation = MemoryAllocation(
                zone=self.zone,
                size_bytes=size_bytes,
                timestamp=datetime.now(),
                allocation_id=allocation_id,
                description=description,
                is_active=True
            )
            
            # Update tracking
            self.allocations[allocation_id] = allocation
            self.current_size_bytes += size_bytes
            self.total_allocations += 1
            
            # Update peak usage
            if self.current_size_bytes > self.peak_usage_bytes:
                self.peak_usage_bytes = self.current_size_bytes
            
            self.logger.debug(f"Allocated {size_bytes} bytes: {allocation_id}")
            return allocation_id
    
    def deallocate(self, allocation_id: str) -> bool:
        """
        Deallocate memory from pool.
        
        Args:
            allocation_id: Allocation to deallocate
            
        Returns:
            True if deallocated successfully
        """
        with self.lock:
            if allocation_id not in self.allocations:
                self.logger.warning(f"Allocation not found: {allocation_id}")
                return False
            
            allocation = self.allocations[allocation_id]
            
            # Update tracking
            self.current_size_bytes -= allocation.size_bytes
            self.total_deallocations += 1
            allocation.is_active = False
            
            # Remove from tracking
            del self.allocations[allocation_id]
            if allocation_id in self.weak_refs:
                del self.weak_refs[allocation_id]
            
            self.logger.debug(f"Deallocated {allocation.size_bytes} bytes: {allocation_id}")
            return True
    
    def cleanup_inactive_allocations(self) -> int:
        """Clean up inactive allocations and return bytes freed."""
        freed_bytes = 0
        
        with self.lock:
            # Find allocations to clean up
            to_cleanup = []
            
            for alloc_id, allocation in self.allocations.items():
                # Check if allocation is old and unused
                age = datetime.now() - allocation.timestamp
                
                if not allocation.is_active or age > timedelta(hours=1):
                    to_cleanup.append(alloc_id)
            
            # Clean up identified allocations
            for alloc_id in to_cleanup:
                allocation = self.allocations.get(alloc_id)
                if allocation:
                    freed_bytes += allocation.size_bytes
                    self.deallocate(alloc_id)
        
        if freed_bytes > 0:
            self.logger.info(f"Cleaned up {len(to_cleanup)} allocations, freed {freed_bytes} bytes")
        
        return freed_bytes
    
    def get_utilization(self) -> float:
        """Get pool utilization percentage."""
        return (self.current_size_bytes / self.max_size_bytes) * 100
    
    def get_fragmentation_level(self) -> float:
        """Calculate memory fragmentation level."""
        if not self.allocations:
            return 0.0
        
        # Simple fragmentation metric based on allocation patterns
        total_allocations = len(self.allocations)
        avg_allocation_size = self.current_size_bytes / max(total_allocations, 1)
        
        # Calculate variance in allocation sizes
        size_variance = 0.0
        for allocation in self.allocations.values():
            size_variance += (allocation.size_bytes - avg_allocation_size) ** 2
        
        size_variance /= max(total_allocations, 1)
        
        # Fragmentation level (0.0 = no fragmentation, 1.0 = high fragmentation)
        self.fragmentation_level = min(size_variance / (avg_allocation_size ** 2), 1.0)
        return self.fragmentation_level


class BrainMemoryManager:
    """
    Central brain memory manager.
    
    Features:
    - Zone-based memory allocation
    - Automatic garbage collection
    - Memory pressure monitoring
    - Intelligent cleanup strategies
    - Performance optimization
    """
    
    def __init__(self, total_memory_limit_mb: int = 200):
        """
        Initialize brain memory manager.
        
        Args:
            total_memory_limit_mb: Total memory limit in MB
        """
        self.total_memory_limit_bytes = total_memory_limit_mb * 1024 * 1024
        
        # Memory pools for different zones
        self.memory_pools = {
            MemoryZone.TIER1_WORKING: MemoryPool(MemoryZone.TIER1_WORKING, 40),
            MemoryZone.TIER2_KNOWLEDGE: MemoryPool(MemoryZone.TIER2_KNOWLEDGE, 60), 
            MemoryZone.TIER3_CONTEXT: MemoryPool(MemoryZone.TIER3_CONTEXT, 40),
            MemoryZone.QUERY_CACHE: MemoryPool(MemoryZone.QUERY_CACHE, 50),
            MemoryZone.SYSTEM_OVERHEAD: MemoryPool(MemoryZone.SYSTEM_OVERHEAD, 10)
        }
        
        # Memory monitoring
        self.memory_monitor = None
        self.monitoring_active = False
        self.monitoring_thread = None
        self.stop_monitoring = False
        
        # Metrics tracking
        self.gc_collections = 0
        self.last_cleanup = None
        self.memory_alerts = []
        self.optimization_history = []
        
        # Memory pressure thresholds
        self.pressure_thresholds = {
            MemoryPressure.LOW: 100 * 1024 * 1024,      # 100MB
            MemoryPressure.MEDIUM: 300 * 1024 * 1024,   # 300MB
            MemoryPressure.HIGH: 500 * 1024 * 1024,     # 500MB
            MemoryPressure.CRITICAL: 700 * 1024 * 1024  # 700MB
        }
        
        # Logger
        self.logger = logging.getLogger(__name__)
        
        # Initialize memory tracking
        if not tracemalloc.is_tracing():
            tracemalloc.start()
        
        self.logger.info(f"Brain memory manager initialized: {total_memory_limit_mb}MB limit")
    
    def start_monitoring(self):
        """Start memory monitoring."""
        if self.monitoring_active:
            return
        
        self.stop_monitoring = False
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self.monitoring_thread.start()
        self.monitoring_active = True
        
        self.logger.info("Memory monitoring started")
    
    def stop_monitoring(self):
        """Stop memory monitoring."""
        self.stop_monitoring = True
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        self.monitoring_active = False
        
        self.logger.info("Memory monitoring stopped")
    
    def allocate_memory(self, zone: MemoryZone, size_bytes: int, description: str = "") -> Optional[str]:
        """
        Allocate memory in specified zone.
        
        Args:
            zone: Memory zone for allocation
            size_bytes: Size to allocate
            description: Allocation description
            
        Returns:
            Allocation ID if successful
        """
        # Check memory pressure
        pressure = self.get_memory_pressure()
        
        if pressure == MemoryPressure.CRITICAL:
            self.logger.warning("Critical memory pressure, triggering emergency cleanup")
            self.emergency_cleanup()
        elif pressure == MemoryPressure.HIGH:
            self.logger.info("High memory pressure, optimizing memory usage")
            self.optimize_memory_usage()
        
        # Allocate from appropriate pool
        pool = self.memory_pools.get(zone)
        if not pool:
            self.logger.error(f"Unknown memory zone: {zone}")
            return None
        
        allocation_id = pool.allocate(size_bytes, description)
        
        if allocation_id:
            self.logger.debug(f"Allocated {size_bytes} bytes in {zone.value}: {allocation_id}")
        else:
            self.logger.warning(f"Failed to allocate {size_bytes} bytes in {zone.value}")
        
        return allocation_id
    
    def deallocate_memory(self, allocation_id: str) -> bool:
        """
        Deallocate memory by allocation ID.
        
        Args:
            allocation_id: Allocation to deallocate
            
        Returns:
            True if deallocated successfully
        """
        # Find the pool containing this allocation
        for pool in self.memory_pools.values():
            if allocation_id in pool.allocations:
                return pool.deallocate(allocation_id)
        
        self.logger.warning(f"Allocation not found: {allocation_id}")
        return False
    
    def get_memory_pressure(self) -> MemoryPressure:
        """Get current memory pressure level."""
        try:
            process = psutil.Process()
            memory_usage = process.memory_info().rss
            
            if memory_usage >= self.pressure_thresholds[MemoryPressure.CRITICAL]:
                return MemoryPressure.CRITICAL
            elif memory_usage >= self.pressure_thresholds[MemoryPressure.HIGH]:
                return MemoryPressure.HIGH
            elif memory_usage >= self.pressure_thresholds[MemoryPressure.MEDIUM]:
                return MemoryPressure.MEDIUM
            else:
                return MemoryPressure.LOW
        
        except Exception as e:
            self.logger.warning(f"Failed to get memory pressure: {e}")
            return MemoryPressure.MEDIUM
    
    def get_memory_metrics(self) -> MemoryMetrics:
        """Get comprehensive memory metrics."""
        try:
            process = psutil.Process()
            total_memory_mb = process.memory_info().rss / (1024 * 1024)
            
            # Zone allocations
            zone_allocations = {}
            for zone, pool in self.memory_pools.items():
                zone_allocations[zone.value] = pool.current_size_bytes / (1024 * 1024)
            
            # Optimization opportunities
            optimization_opportunities = []
            
            for zone, pool in self.memory_pools.items():
                utilization = pool.get_utilization()
                fragmentation = pool.get_fragmentation_level()
                
                if utilization > 90:
                    optimization_opportunities.append(f"{zone.value} pool near capacity ({utilization:.1f}%)")
                
                if fragmentation > 0.7:
                    optimization_opportunities.append(f"{zone.value} pool highly fragmented ({fragmentation:.1f})")
            
            # Memory leaks detection
            memory_leaks_detected = self._detect_memory_leaks()
            
            return MemoryMetrics(
                total_memory_mb=total_memory_mb,
                zone_allocations=zone_allocations,
                pressure_level=self.get_memory_pressure(),
                gc_collections=self.gc_collections,
                memory_leaks_detected=memory_leaks_detected,
                optimization_opportunities=optimization_opportunities,
                last_cleanup=self.last_cleanup
            )
        
        except Exception as e:
            self.logger.error(f"Failed to get memory metrics: {e}")
            return MemoryMetrics(
                total_memory_mb=0.0,
                zone_allocations={},
                pressure_level=MemoryPressure.MEDIUM,
                gc_collections=0,
                memory_leaks_detected=0,
                optimization_opportunities=["Failed to get metrics"],
                last_cleanup=None
            )
    
    def optimize_memory_usage(self) -> Dict[str, Any]:
        """Optimize memory usage across all pools."""
        optimization_results = {
            'pools_optimized': [],
            'total_bytes_freed': 0,
            'gc_collections_triggered': 0,
            'optimizations_applied': []
        }
        
        # Optimize each memory pool
        for zone, pool in self.memory_pools.items():
            utilization = pool.get_utilization()
            
            if utilization > 70:  # Pool under pressure
                freed_bytes = pool.cleanup_inactive_allocations()
                
                if freed_bytes > 0:
                    optimization_results['pools_optimized'].append(zone.value)
                    optimization_results['total_bytes_freed'] += freed_bytes
                    optimization_results['optimizations_applied'].append(
                        f"Cleaned {zone.value} pool: {freed_bytes} bytes freed"
                    )
        
        # Trigger garbage collection
        initial_gc = gc.get_count()
        gc.collect()
        final_gc = gc.get_count()
        gc_triggered = sum(initial_gc) - sum(final_gc)
        
        if gc_triggered > 0:
            self.gc_collections += 1
            optimization_results['gc_collections_triggered'] = gc_triggered
            optimization_results['optimizations_applied'].append(
                f"Garbage collection freed {gc_triggered} objects"
            )
        
        # Update timestamp
        self.last_cleanup = datetime.now()
        
        # Log optimization results
        if optimization_results['total_bytes_freed'] > 0:
            self.logger.info(
                f"Memory optimization: {optimization_results['total_bytes_freed']} bytes freed, "
                f"{len(optimization_results['pools_optimized'])} pools optimized"
            )
        
        # Store in history
        self.optimization_history.append({
            'timestamp': self.last_cleanup,
            'results': optimization_results
        })
        
        # Keep only last 20 optimization records
        if len(self.optimization_history) > 20:
            self.optimization_history = self.optimization_history[-20:]
        
        return optimization_results
    
    def emergency_cleanup(self) -> Dict[str, Any]:
        """Emergency memory cleanup for critical situations."""
        self.logger.warning("Performing emergency memory cleanup")
        
        cleanup_results = {
            'pools_cleaned': [],
            'allocations_freed': 0,
            'bytes_freed': 0,
            'actions_taken': []
        }
        
        # Aggressive cleanup for all pools
        for zone, pool in self.memory_pools.items():
            initial_allocations = len(pool.allocations)
            initial_size = pool.current_size_bytes
            
            # Clean all inactive allocations
            freed_bytes = pool.cleanup_inactive_allocations()
            
            # If still under pressure, clean old allocations too
            if pool.get_utilization() > 80:
                cutoff_time = datetime.now() - timedelta(minutes=30)
                old_allocations = [
                    alloc_id for alloc_id, alloc in pool.allocations.items()
                    if alloc.timestamp < cutoff_time
                ]
                
                for alloc_id in old_allocations:
                    if pool.deallocate(alloc_id):
                        freed_bytes += pool.allocations.get(alloc_id, 
                                                           MemoryAllocation(zone, 0, datetime.now(), "", "", True)).size_bytes
            
            if freed_bytes > 0:
                cleanup_results['pools_cleaned'].append(zone.value)
                cleanup_results['allocations_freed'] += initial_allocations - len(pool.allocations)
                cleanup_results['bytes_freed'] += freed_bytes
                cleanup_results['actions_taken'].append(
                    f"Emergency cleanup {zone.value}: {freed_bytes} bytes freed"
                )
        
        # Force garbage collection multiple times
        for i in range(3):
            gc.collect()
        
        cleanup_results['actions_taken'].append("Multiple garbage collections performed")
        
        self.logger.warning(f"Emergency cleanup complete: {cleanup_results['bytes_freed']} bytes freed")
        return cleanup_results
    
    def _detect_memory_leaks(self) -> int:
        """Detect potential memory leaks."""
        leaks_detected = 0
        
        try:
            # Check for pools with consistently high utilization
            for zone, pool in self.memory_pools.items():
                utilization = pool.get_utilization()
                active_allocations = sum(1 for alloc in pool.allocations.values() if alloc.is_active)
                
                # High utilization with many old allocations suggests potential leaks
                if utilization > 85 and active_allocations > 50:
                    old_allocations = sum(
                        1 for alloc in pool.allocations.values()
                        if (datetime.now() - alloc.timestamp) > timedelta(hours=2)
                    )
                    
                    if old_allocations > active_allocations * 0.5:
                        leaks_detected += 1
                        self.logger.warning(f"Potential memory leak detected in {zone.value} pool")
        
        except Exception as e:
            self.logger.error(f"Memory leak detection failed: {e}")
        
        return leaks_detected
    
    def _monitoring_loop(self):
        """Background memory monitoring loop."""
        while not self.stop_monitoring:
            try:
                pressure = self.get_memory_pressure()
                
                # Auto-optimize on high pressure
                if pressure == MemoryPressure.HIGH:
                    self.optimize_memory_usage()
                elif pressure == MemoryPressure.CRITICAL:
                    self.emergency_cleanup()
                
                # Sleep for monitoring interval
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Memory monitoring error: {e}")
                time.sleep(10)  # Wait before retrying
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """Get comprehensive memory management summary."""
        metrics = self.get_memory_metrics()
        
        return {
            'memory_metrics': {
                'total_memory_mb': metrics.total_memory_mb,
                'zone_allocations': metrics.zone_allocations,
                'pressure_level': metrics.pressure_level.value,
                'gc_collections': metrics.gc_collections,
                'memory_leaks_detected': metrics.memory_leaks_detected,
                'optimization_opportunities': metrics.optimization_opportunities,
                'last_cleanup': metrics.last_cleanup.isoformat() if metrics.last_cleanup else None
            },
            'pool_statistics': {
                zone.value: {
                    'utilization_percent': pool.get_utilization(),
                    'fragmentation_level': pool.get_fragmentation_level(),
                    'active_allocations': len(pool.allocations),
                    'peak_usage_mb': pool.peak_usage_bytes / (1024 * 1024),
                    'total_allocations': pool.total_allocations,
                    'total_deallocations': pool.total_deallocations
                }
                for zone, pool in self.memory_pools.items()
            },
            'optimization_history': self.optimization_history[-5:],  # Last 5 optimizations
            'monitoring_status': 'active' if self.monitoring_active else 'inactive'
        }


if __name__ == "__main__":
    # Test the memory manager
    print("🧠 CORTEX 3.0 Phase 2 - Memory Manager Test")
    print("=" * 55)
    
    # Initialize memory manager
    memory_manager = BrainMemoryManager(total_memory_limit_mb=100)
    
    # Test memory allocation
    print("\n1. Testing Memory Allocation:")
    allocations = []
    
    # Allocate memory in different zones
    zones_to_test = [
        (MemoryZone.TIER1_WORKING, 5 * 1024 * 1024, "Conversation cache"),
        (MemoryZone.TIER2_KNOWLEDGE, 10 * 1024 * 1024, "Knowledge graph cache"),
        (MemoryZone.TIER3_CONTEXT, 3 * 1024 * 1024, "Development context"),
        (MemoryZone.QUERY_CACHE, 8 * 1024 * 1024, "Query result cache")
    ]
    
    for zone, size, description in zones_to_test:
        alloc_id = memory_manager.allocate_memory(zone, size, description)
        if alloc_id:
            allocations.append(alloc_id)
            print(f"   ✅ Allocated {size/(1024*1024):.1f}MB in {zone.value}")
        else:
            print(f"   ❌ Failed to allocate {size/(1024*1024):.1f}MB in {zone.value}")
    
    # Get memory metrics
    print("\n2. Memory Usage Analysis:")
    metrics = memory_manager.get_memory_metrics()
    
    print(f"   Total Memory: {metrics.total_memory_mb:.1f}MB")
    print(f"   Memory Pressure: {metrics.pressure_level.value}")
    print(f"   Active Zones: {len(metrics.zone_allocations)}")
    
    for zone, usage_mb in metrics.zone_allocations.items():
        if usage_mb > 0:
            print(f"   {zone}: {usage_mb:.1f}MB")
    
    # Test optimization
    print("\n3. Testing Memory Optimization:")
    optimization_results = memory_manager.optimize_memory_usage()
    
    print(f"   Pools Optimized: {len(optimization_results['pools_optimized'])}")
    print(f"   Bytes Freed: {optimization_results['total_bytes_freed']}")
    print(f"   GC Collections: {optimization_results['gc_collections_triggered']}")
    
    for optimization in optimization_results['optimizations_applied']:
        print(f"   - {optimization}")
    
    # Test deallocation
    print("\n4. Testing Memory Deallocation:")
    deallocated = 0
    for alloc_id in allocations:
        if memory_manager.deallocate_memory(alloc_id):
            deallocated += 1
    
    print(f"   Deallocated: {deallocated}/{len(allocations)} allocations")
    
    # Final memory summary
    print("\n5. Final Memory Summary:")
    summary = memory_manager.get_memory_summary()
    
    print(f"   Memory Manager Status: {summary['monitoring_status']}")
    print(f"   Total Optimizations: {len(summary['optimization_history'])}")
    
    pool_stats = summary['pool_statistics']
    for zone, stats in pool_stats.items():
        if stats['active_allocations'] > 0 or stats['peak_usage_mb'] > 0:
            print(f"   {zone}: {stats['utilization_percent']:.1f}% utilized, "
                  f"{stats['active_allocations']} active allocations")
    
    print("\n✅ Memory Manager Test Complete!")
    print("🎯 Ready for integration with Brain Optimization Engine")