"""
CORTEX 3.0 Phase 2 - Brain Performance Integration
=================================================

Integration layer connecting Brain Optimization Engine with Phase 1 Data Collectors.
Provides unified brain performance monitoring and optimization.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

Phase: Phase 2 - Brain Performance Optimization (Task 2)
Integration: Optimization Engine + Query Cache + Memory Manager + Data Collectors
"""

import time
import threading
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
import logging
from dataclasses import dataclass

# Import brain optimization components
try:
    from .optimization_engine import BrainOptimizationEngine, OptimizationResult
    from .query_cache import SmartQueryCache, CacheMetrics
    from .memory_manager import BrainMemoryManager, MemoryMetrics, MemoryZone, MemoryPressure
except ImportError:
    from optimization_engine import BrainOptimizationEngine, OptimizationResult
    from query_cache import SmartQueryCache, CacheMetrics
    from memory_manager import BrainMemoryManager, MemoryMetrics, MemoryZone, MemoryPressure

# Import Phase 1 data collectors
try:
    from src.collectors.brain_performance_collector import BrainPerformanceCollector
    from src.collectors.base_collector import CollectorMetric, CollectorPriority
except ImportError:
    # Fallback for testing
    CollectorMetric = None
    CollectorPriority = None
    BrainPerformanceCollector = None


@dataclass
class BrainPerformanceSnapshot:
    """Complete brain performance snapshot."""
    timestamp: datetime
    
    # Tier performance
    tier1_avg_ms: float
    tier2_avg_ms: float
    tier3_avg_ms: float
    
    # Cache performance
    cache_hit_rate: float
    cache_memory_mb: float
    cache_entries: int
    
    # Memory usage
    total_memory_mb: float
    memory_pressure: str
    active_allocations: int
    
    # Optimization status
    optimization_active: bool
    last_optimization: Optional[datetime]
    optimizations_completed: int
    
    # Overall health score (0-100)
    health_score: float


class IntegratedBrainPerformanceSystem:
    """
    Integrated brain performance system.
    
    Combines:
    - Brain Optimization Engine
    - Intelligent Query Cache
    - Memory Manager
    - Data Collectors
    
    Features:
    - Unified performance monitoring
    - Automatic optimization triggers
    - Real-time health scoring
    - Performance trend analysis
    """
    
    def __init__(self, brain_path: str = None, config: Dict[str, Any] = None):
        """
        Initialize integrated brain performance system.
        
        Args:
            brain_path: Path to CORTEX brain directory
            config: Configuration parameters
        """
        self.brain_path = brain_path
        self.config = config or {}
        
        # Initialize core components
        self.optimization_engine = BrainOptimizationEngine(brain_path)
        self.query_cache = SmartQueryCache(
            cache_size_mb=self.config.get('cache_size_mb', 50)
        )
        self.memory_manager = BrainMemoryManager(
            total_memory_limit_mb=self.config.get('memory_limit_mb', 200)
        )
        
        # Initialize data collector (Phase 1 integration)
        self.performance_collector = None
        if BrainPerformanceCollector:
            try:
                self.performance_collector = BrainPerformanceCollector(brain_path)
                self.performance_collector._initialize()
            except Exception as e:
                logging.warning(f"Failed to initialize performance collector: {e}")
        
        # Performance monitoring
        self.performance_snapshots: List[BrainPerformanceSnapshot] = []
        self.monitoring_active = False
        self.monitoring_thread = None
        self.stop_monitoring = False
        
        # Optimization triggers
        self.optimization_thresholds = {
            'tier1_slow_threshold_ms': 40,   # Trigger if tier1 > 40ms (80% of target)
            'tier2_slow_threshold_ms': 120,  # Trigger if tier2 > 120ms (80% of target)
            'tier3_slow_threshold_ms': 160,  # Trigger if tier3 > 160ms (80% of target)
            'cache_hit_rate_min': 0.7,      # Trigger if cache hit rate < 70%
            'memory_pressure_threshold': MemoryPressure.HIGH,  # Trigger on high memory pressure
            'auto_optimization_enabled': True
        }
        
        # Performance trends
        self.performance_trends = {
            'tier1_trend': [],
            'tier2_trend': [],
            'tier3_trend': [],
            'cache_trend': [],
            'memory_trend': []
        }
        
        # Logger
        self.logger = logging.getLogger(__name__)
        
        self.logger.info("Integrated brain performance system initialized")
    
    def start_monitoring(self):
        """Start unified performance monitoring."""
        if self.monitoring_active:
            return
        
        # Start component monitoring
        self.optimization_engine.start_optimization_monitoring()
        self.memory_manager.start_monitoring()
        
        # Start unified monitoring
        self.stop_monitoring = False
        self.monitoring_thread = threading.Thread(
            target=self._unified_monitoring_loop,
            daemon=True
        )
        self.monitoring_thread.start()
        self.monitoring_active = True
        
        self.logger.info("Unified brain performance monitoring started")
    
    def stop_monitoring(self):
        """Stop unified performance monitoring."""
        # Stop component monitoring
        self.optimization_engine.stop_optimization_monitoring()
        self.memory_manager.stop_monitoring()
        
        # Stop unified monitoring
        self.stop_monitoring = True
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        self.monitoring_active = False
        
        self.logger.info("Unified brain performance monitoring stopped")
    
    def execute_optimized_query(self, query: str, tier: str, execute_func, *args, **kwargs) -> Any:
        """
        Execute query with full optimization pipeline.
        
        Args:
            query: Query string
            tier: Target tier (tier1, tier2, tier3)
            execute_func: Function to execute query
            *args, **kwargs: Arguments for execute_func
            
        Returns:
            Query result with performance tracking
        """
        # Start performance tracking
        start_time = time.time()
        
        # Try cache first
        result = self.query_cache.cached_query(query, execute_func, *args, **kwargs)
        
        # Calculate performance
        execution_time_ms = (time.time() - start_time) * 1000
        
        # Record tier operation
        self.optimization_engine.record_tier_operation(
            tier, "query", execution_time_ms, len(str(query)), 
            len(str(result)) if result else 0
        )
        
        # Collect metrics if available
        if self.performance_collector:
            try:
                metrics = self.performance_collector._collect_metrics()
                # Additional metric processing could go here
            except Exception as e:
                self.logger.warning(f"Failed to collect metrics: {e}")
        
        # Check if optimization is needed
        self._check_optimization_triggers(tier, execution_time_ms)
        
        return result
    
    def allocate_optimized_memory(self, zone: MemoryZone, size_bytes: int, description: str = "") -> Optional[str]:
        """
        Allocate memory with optimization integration.
        
        Args:
            zone: Memory zone
            size_bytes: Size to allocate
            description: Allocation description
            
        Returns:
            Allocation ID if successful
        """
        allocation_id = self.memory_manager.allocate_memory(zone, size_bytes, description)
        
        if allocation_id:
            # Record successful allocation
            self.logger.debug(f"Allocated {size_bytes} bytes in {zone.value}: {allocation_id}")
        else:
            # Trigger optimization if allocation failed
            self.logger.warning(f"Memory allocation failed, triggering optimization")
            self.trigger_comprehensive_optimization()
            
            # Retry allocation
            allocation_id = self.memory_manager.allocate_memory(zone, size_bytes, description)
        
        return allocation_id
    
    def get_unified_performance_snapshot(self) -> BrainPerformanceSnapshot:
        """Get comprehensive performance snapshot."""
        # Get component metrics
        optimization_summary = self.optimization_engine.get_performance_summary()
        cache_stats = self.query_cache.get_cache_stats()
        memory_metrics = self.memory_manager.get_memory_metrics()
        
        # Calculate tier averages
        tier_performance = optimization_summary['tier_performance']
        tier1_avg = tier_performance['tier1']['average_ms']
        tier2_avg = tier_performance['tier2']['average_ms']
        tier3_avg = tier_performance['tier3']['average_ms']
        
        # Cache metrics
        cache_perf = cache_stats['performance_metrics']
        cache_hit_rate = cache_perf['hit_rate']
        cache_memory_mb = cache_perf['memory_usage_mb']
        cache_entries = cache_perf['entries_count']
        
        # Memory metrics
        total_memory_mb = memory_metrics.total_memory_mb
        memory_pressure = memory_metrics.pressure_level.value
        active_allocations = sum(
            len(pool.allocations) for pool in self.memory_manager.memory_pools.values()
        )
        
        # Optimization status
        optimization_active = optimization_summary['optimization_engine_status'] == 'active'
        last_optimization = None
        if optimization_summary['last_optimization']:
            last_optimization = datetime.fromisoformat(optimization_summary['last_optimization'])
        
        optimizations_completed = len(optimization_summary['optimization_results'])
        
        # Calculate health score
        health_score = self._calculate_health_score(
            tier1_avg, tier2_avg, tier3_avg, cache_hit_rate, memory_pressure
        )
        
        snapshot = BrainPerformanceSnapshot(
            timestamp=datetime.now(),
            tier1_avg_ms=tier1_avg,
            tier2_avg_ms=tier2_avg,
            tier3_avg_ms=tier3_avg,
            cache_hit_rate=cache_hit_rate,
            cache_memory_mb=cache_memory_mb,
            cache_entries=cache_entries,
            total_memory_mb=total_memory_mb,
            memory_pressure=memory_pressure,
            active_allocations=active_allocations,
            optimization_active=optimization_active,
            last_optimization=last_optimization,
            optimizations_completed=optimizations_completed,
            health_score=health_score
        )
        
        # Store snapshot
        self.performance_snapshots.append(snapshot)
        if len(self.performance_snapshots) > 100:
            self.performance_snapshots = self.performance_snapshots[-100:]
        
        # Update trends
        self._update_performance_trends(snapshot)
        
        return snapshot
    
    def trigger_comprehensive_optimization(self) -> Dict[str, Any]:
        """Trigger comprehensive optimization across all components."""
        self.logger.info("Starting comprehensive brain optimization")
        
        optimization_results = {
            'timestamp': datetime.now(),
            'optimization_engine_results': {},
            'cache_optimization_results': {},
            'memory_optimization_results': {},
            'overall_improvement': 0.0,
            'success': True
        }
        
        try:
            # Optimization engine
            engine_results = self.optimization_engine.run_comprehensive_optimization()
            optimization_results['optimization_engine_results'] = {
                tier: {
                    'improvement': result.performance_improvement,
                    'memory_saved': result.memory_savings,
                    'success': result.success
                }
                for tier, result in engine_results.items()
            }
            
            # Query cache optimization
            cache_results = self.query_cache.cache_engine.optimize_cache()
            optimization_results['cache_optimization_results'] = cache_results
            
            # Memory optimization
            memory_results = self.memory_manager.optimize_memory_usage()
            optimization_results['memory_optimization_results'] = memory_results
            
            # Calculate overall improvement
            total_improvement = sum(
                result.performance_improvement for result in engine_results.values()
            )
            optimization_results['overall_improvement'] = total_improvement / len(engine_results)
            
            self.logger.info(f"Comprehensive optimization complete: {optimization_results['overall_improvement']:.1f}% improvement")
            
        except Exception as e:
            self.logger.error(f"Comprehensive optimization failed: {e}")
            optimization_results['success'] = False
            optimization_results['error'] = str(e)
        
        return optimization_results
    
    def get_performance_trends(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance trends over specified time period."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Filter recent snapshots
        recent_snapshots = [
            snapshot for snapshot in self.performance_snapshots
            if snapshot.timestamp >= cutoff_time
        ]
        
        if not recent_snapshots:
            return {'error': 'No recent performance data available'}
        
        # Calculate trends
        trends = {
            'period_hours': hours,
            'snapshots_analyzed': len(recent_snapshots),
            'tier_performance': {
                'tier1': {
                    'current_ms': recent_snapshots[-1].tier1_avg_ms,
                    'average_ms': sum(s.tier1_avg_ms for s in recent_snapshots) / len(recent_snapshots),
                    'min_ms': min(s.tier1_avg_ms for s in recent_snapshots),
                    'max_ms': max(s.tier1_avg_ms for s in recent_snapshots)
                },
                'tier2': {
                    'current_ms': recent_snapshots[-1].tier2_avg_ms,
                    'average_ms': sum(s.tier2_avg_ms for s in recent_snapshots) / len(recent_snapshots),
                    'min_ms': min(s.tier2_avg_ms for s in recent_snapshots),
                    'max_ms': max(s.tier2_avg_ms for s in recent_snapshots)
                },
                'tier3': {
                    'current_ms': recent_snapshots[-1].tier3_avg_ms,
                    'average_ms': sum(s.tier3_avg_ms for s in recent_snapshots) / len(recent_snapshots),
                    'min_ms': min(s.tier3_avg_ms for s in recent_snapshots),
                    'max_ms': max(s.tier3_avg_ms for s in recent_snapshots)
                }
            },
            'cache_performance': {
                'current_hit_rate': recent_snapshots[-1].cache_hit_rate,
                'average_hit_rate': sum(s.cache_hit_rate for s in recent_snapshots) / len(recent_snapshots),
                'current_memory_mb': recent_snapshots[-1].cache_memory_mb,
                'average_entries': sum(s.cache_entries for s in recent_snapshots) / len(recent_snapshots)
            },
            'memory_usage': {
                'current_mb': recent_snapshots[-1].total_memory_mb,
                'average_mb': sum(s.total_memory_mb for s in recent_snapshots) / len(recent_snapshots),
                'peak_mb': max(s.total_memory_mb for s in recent_snapshots),
                'current_pressure': recent_snapshots[-1].memory_pressure
            },
            'health_scores': {
                'current': recent_snapshots[-1].health_score,
                'average': sum(s.health_score for s in recent_snapshots) / len(recent_snapshots),
                'min': min(s.health_score for s in recent_snapshots),
                'max': max(s.health_score for s in recent_snapshots)
            }
        }
        
        return trends
    
    def _unified_monitoring_loop(self):
        """Unified monitoring loop."""
        while not self.stop_monitoring:
            try:
                # Take performance snapshot
                snapshot = self.get_unified_performance_snapshot()
                
                # Check for optimization triggers
                if self.optimization_thresholds['auto_optimization_enabled']:
                    self._check_comprehensive_optimization_triggers(snapshot)
                
                # Sleep for monitoring interval
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Unified monitoring error: {e}")
                time.sleep(10)  # Wait before retrying
    
    def _check_optimization_triggers(self, tier: str, execution_time_ms: float):
        """Check if optimization should be triggered."""
        thresholds = self.optimization_thresholds
        
        if tier == 'tier1' and execution_time_ms > thresholds['tier1_slow_threshold_ms']:
            self.logger.info(f"Tier 1 performance degraded: {execution_time_ms}ms")
            self.optimization_engine.optimize_tier_performance('tier1')
        
        elif tier == 'tier2' and execution_time_ms > thresholds['tier2_slow_threshold_ms']:
            self.logger.info(f"Tier 2 performance degraded: {execution_time_ms}ms")
            self.optimization_engine.optimize_tier_performance('tier2')
        
        elif tier == 'tier3' and execution_time_ms > thresholds['tier3_slow_threshold_ms']:
            self.logger.info(f"Tier 3 performance degraded: {execution_time_ms}ms")
            self.optimization_engine.optimize_tier_performance('tier3')
    
    def _check_comprehensive_optimization_triggers(self, snapshot: BrainPerformanceSnapshot):
        """Check if comprehensive optimization should be triggered."""
        triggers = []
        
        # Cache performance trigger
        if snapshot.cache_hit_rate < self.optimization_thresholds['cache_hit_rate_min']:
            triggers.append(f"Low cache hit rate: {snapshot.cache_hit_rate:.2f}")
        
        # Memory pressure trigger
        if snapshot.memory_pressure in ['high', 'critical']:
            triggers.append(f"Memory pressure: {snapshot.memory_pressure}")
        
        # Health score trigger
        if snapshot.health_score < 70:
            triggers.append(f"Low health score: {snapshot.health_score:.1f}")
        
        # Multiple slow tiers
        slow_tiers = []
        if snapshot.tier1_avg_ms > self.optimization_thresholds['tier1_slow_threshold_ms']:
            slow_tiers.append('tier1')
        if snapshot.tier2_avg_ms > self.optimization_thresholds['tier2_slow_threshold_ms']:
            slow_tiers.append('tier2')
        if snapshot.tier3_avg_ms > self.optimization_thresholds['tier3_slow_threshold_ms']:
            slow_tiers.append('tier3')
        
        if len(slow_tiers) >= 2:
            triggers.append(f"Multiple slow tiers: {slow_tiers}")
        
        # Trigger optimization if needed
        if triggers:
            self.logger.warning(f"Triggering comprehensive optimization: {triggers}")
            self.trigger_comprehensive_optimization()
    
    def _calculate_health_score(self, tier1_ms: float, tier2_ms: float, tier3_ms: float,
                              cache_hit_rate: float, memory_pressure: str) -> float:
        """Calculate overall brain health score (0-100)."""
        score = 100.0
        
        # Tier performance (40 points total)
        if tier1_ms > 50:  # Target: <50ms
            score -= min(20, (tier1_ms - 50) / 10)  # Penalty increases with delay
        if tier2_ms > 150:  # Target: <150ms
            score -= min(15, (tier2_ms - 150) / 20)
        if tier3_ms > 200:  # Target: <200ms
            score -= min(5, (tier3_ms - 200) / 30)
        
        # Cache performance (30 points)
        if cache_hit_rate < 0.8:  # Target: >80%
            score -= (0.8 - cache_hit_rate) * 30
        
        # Memory pressure (20 points)
        memory_penalties = {
            'low': 0,
            'medium': 5,
            'high': 15,
            'critical': 20
        }
        score -= memory_penalties.get(memory_pressure, 10)
        
        # Optimization activity bonus (10 points)
        # This could be enhanced to consider recent optimizations
        
        return max(0.0, min(100.0, score))
    
    def _update_performance_trends(self, snapshot: BrainPerformanceSnapshot):
        """Update performance trend tracking."""
        self.performance_trends['tier1_trend'].append(snapshot.tier1_avg_ms)
        self.performance_trends['tier2_trend'].append(snapshot.tier2_avg_ms)
        self.performance_trends['tier3_trend'].append(snapshot.tier3_avg_ms)
        self.performance_trends['cache_trend'].append(snapshot.cache_hit_rate)
        self.performance_trends['memory_trend'].append(snapshot.total_memory_mb)
        
        # Keep only recent trends (last 100 data points)
        for trend_key in self.performance_trends:
            if len(self.performance_trends[trend_key]) > 100:
                self.performance_trends[trend_key] = self.performance_trends[trend_key][-100:]


# Convenience function for easy integration
def create_optimized_brain_system(brain_path: str = "cortex-brain", config: Dict[str, Any] = None) -> IntegratedBrainPerformanceSystem:
    """
    Create and initialize optimized brain system.
    
    Args:
        brain_path: Path to CORTEX brain directory
        config: System configuration
        
    Returns:
        Initialized IntegratedBrainPerformanceSystem
    """
    system = IntegratedBrainPerformanceSystem(brain_path, config)
    system.start_monitoring()
    return system


if __name__ == "__main__":
    # Test integrated brain performance system
    print("🧠 CORTEX 3.0 Phase 2 - Integrated Brain Performance System Test")
    print("=" * 75)
    
    # Create optimized brain system
    system = create_optimized_brain_system("cortex-brain", {
        'cache_size_mb': 20,
        'memory_limit_mb': 100
    })
    
    # Test optimized query execution
    print("\n1. Testing Optimized Query Execution:")
    
    def mock_tier_query(query: str, tier: str):
        import time
        time.sleep(0.02)  # 20ms mock execution
        return f"Results for {query} from {tier}"
    
    queries = [
        ("CORTEX brain status", "tier1"),
        ("pattern search", "tier2"),
        ("development context", "tier3"),
        ("CORTEX brain status", "tier1")  # Duplicate for cache test
    ]
    
    for query, tier in queries:
        result = system.execute_optimized_query(query, tier, mock_tier_query, query, tier)
        print(f"   Query: {query[:20]}... -> Tier: {tier}, Result: {len(result)} chars")
    
    # Test memory allocation
    print("\n2. Testing Optimized Memory Allocation:")
    
    allocations = [
        (MemoryZone.TIER1_WORKING, 1024*1024, "Working memory test"),
        (MemoryZone.QUERY_CACHE, 2*1024*1024, "Cache memory test"),
        (MemoryZone.TIER2_KNOWLEDGE, 512*1024, "Knowledge graph test")
    ]
    
    alloc_ids = []
    for zone, size, description in allocations:
        alloc_id = system.allocate_optimized_memory(zone, size, description)
        if alloc_id:
            alloc_ids.append(alloc_id)
            print(f"   ✅ Allocated {size/(1024*1024):.1f}MB in {zone.value}")
        else:
            print(f"   ❌ Failed to allocate {size/(1024*1024):.1f}MB in {zone.value}")
    
    # Get performance snapshot
    print("\n3. Performance Snapshot:")
    snapshot = system.get_unified_performance_snapshot()
    
    print(f"   Health Score: {snapshot.health_score:.1f}/100")
    print(f"   Tier Performance: T1={snapshot.tier1_avg_ms:.1f}ms, T2={snapshot.tier2_avg_ms:.1f}ms, T3={snapshot.tier3_avg_ms:.1f}ms")
    print(f"   Cache Hit Rate: {snapshot.cache_hit_rate*100:.1f}%")
    print(f"   Memory Usage: {snapshot.total_memory_mb:.1f}MB ({snapshot.memory_pressure})")
    print(f"   Active Allocations: {snapshot.active_allocations}")
    
    # Test comprehensive optimization
    print("\n4. Testing Comprehensive Optimization:")
    optimization_results = system.trigger_comprehensive_optimization()
    
    if optimization_results['success']:
        print(f"   ✅ Overall Improvement: {optimization_results['overall_improvement']:.1f}%")
        print(f"   Engine Optimizations: {len(optimization_results['optimization_engine_results'])}")
        print(f"   Cache Optimizations: {len(optimization_results['cache_optimization_results']['optimizations_applied'])}")
        print(f"   Memory Optimizations: {len(optimization_results['memory_optimization_results']['optimizations_applied'])}")
    else:
        print(f"   ❌ Optimization failed: {optimization_results.get('error', 'Unknown error')}")
    
    # Cleanup
    for alloc_id in alloc_ids:
        system.memory_manager.deallocate_memory(alloc_id)
    
    system.stop_monitoring()
    
    print("\n✅ Integrated Brain Performance System Test Complete!")
    print("🎯 Task 2 (Brain Performance Optimization) Ready for Production!")