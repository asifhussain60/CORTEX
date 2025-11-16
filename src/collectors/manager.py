"""
CORTEX 3.0 - Data Collectors Manager
===================================

Central management system for all CORTEX data collectors.
Provides unified interface for starting, stopping, and monitoring collectors.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

Feature: Quick Win #3 (Week 1)
Effort: 2 hours (collector management system)
Target: Unified collector management with automatic initialization
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import logging
import threading
import time
from pathlib import Path

from .base_collector import BaseCollector, CollectorMetric, CollectorHealth, collector_registry
from .response_template_collector import ResponseTemplateMetricsCollector
from .brain_performance_collector import BrainPerformanceCollector
from .token_usage_collector import TokenUsageCollector
from .workspace_health_collector import WorkspaceHealthCollector
from .conversation_collector import ConversationCollector


class CollectorManager:
    """
    Manages all CORTEX data collectors.
    
    Responsibilities:
    - Initialize and register all collectors
    - Start/stop collection processes
    - Coordinate data collection
    - Provide unified metrics API
    - Handle collector health monitoring
    """
    
    def __init__(self, 
                 brain_path: Optional[str] = None,
                 workspace_path: Optional[str] = None,
                 auto_start: bool = True):
        self.brain_path = brain_path
        self.workspace_path = workspace_path
        self.auto_start = auto_start
        
        # State management
        self.initialized = False
        self.collection_active = False
        self.collection_thread = None
        self.shutdown_event = threading.Event()
        
        # Configuration
        self.collection_interval = 60.0  # Default collection interval in seconds
        self.enable_background_collection = True
        
        # Setup logging
        self.logger = logging.getLogger("cortex.collector.manager")
        
        # Initialize collectors
        self.collectors: Dict[str, BaseCollector] = {}
        
        if auto_start:
            self.initialize()
    
    def initialize(self) -> bool:
        """Initialize all collectors and prepare for data collection"""
        try:
            if self.initialized:
                self.logger.info("Collector manager already initialized")
                return True
            
            self.logger.info("Initializing CORTEX data collectors...")
            
            # Create and register core collectors
            self._create_core_collectors()
            
            # Start collectors if auto-start is enabled
            if self.auto_start:
                self.start_all_collectors()
            
            self.initialized = True
            self.logger.info("Collector manager initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize collector manager: {e}")
            return False
    
    def _create_core_collectors(self) -> None:
        """Create and register the 5 core collectors"""
        
        # 1. Response Template Metrics Collector
        template_collector = ResponseTemplateMetricsCollector(
            brain_path=self.brain_path
        )
        self.collectors[template_collector.collector_id] = template_collector
        collector_registry.register(template_collector)
        
        # 2. Brain Performance Collector
        brain_collector = BrainPerformanceCollector(
            brain_path=self.brain_path
        )
        self.collectors[brain_collector.collector_id] = brain_collector
        collector_registry.register(brain_collector)
        
        # 3. Token Usage Collector
        token_collector = TokenUsageCollector(
            brain_path=self.brain_path
        )
        self.collectors[token_collector.collector_id] = token_collector
        collector_registry.register(token_collector)
        
        # 4. Workspace Health Collector
        workspace_collector = WorkspaceHealthCollector(
            workspace_path=self.workspace_path,
            brain_path=self.brain_path
        )
        self.collectors[workspace_collector.collector_id] = workspace_collector
        collector_registry.register(workspace_collector)
        
        # 5. Conversation Pipeline Collector (NEW)
        conversation_collector = ConversationCollector(
            brain_path=self.brain_path
        )
        self.collectors[conversation_collector.collector_id] = conversation_collector
        collector_registry.register(conversation_collector)
        
        self.logger.info(f"Created {len(self.collectors)} core collectors")
    
    def start_all_collectors(self) -> Dict[str, bool]:
        """Start all registered collectors"""
        results = {}
        
        for collector_id, collector in self.collectors.items():
            try:
                success = collector.start()
                results[collector_id] = success
                
                if success:
                    self.logger.info(f"Started collector: {collector.name}")
                else:
                    self.logger.warning(f"Failed to start collector: {collector.name}")
                    
            except Exception as e:
                self.logger.error(f"Error starting collector {collector_id}: {e}")
                results[collector_id] = False
        
        # Start background collection if enabled
        if self.enable_background_collection and any(results.values()):
            self.start_background_collection()
        
        return results
    
    def stop_all_collectors(self) -> Dict[str, bool]:
        """Stop all registered collectors"""
        results = {}
        
        # Stop background collection
        self.stop_background_collection()
        
        for collector_id, collector in self.collectors.items():
            try:
                success = collector.stop()
                results[collector_id] = success
                
                if success:
                    self.logger.info(f"Stopped collector: {collector.name}")
                else:
                    self.logger.warning(f"Failed to stop collector: {collector.name}")
                    
            except Exception as e:
                self.logger.error(f"Error stopping collector {collector_id}: {e}")
                results[collector_id] = False
        
        return results
    
    def collect_all_metrics(self) -> Dict[str, List[CollectorMetric]]:
        """Collect metrics from all active collectors"""
        all_metrics = {}
        
        for collector_id, collector in self.collectors.items():
            try:
                metrics = collector.collect()
                all_metrics[collector_id] = metrics
                
                if metrics:
                    self.logger.debug(f"Collected {len(metrics)} metrics from {collector.name}")
                    
            except Exception as e:
                self.logger.warning(f"Error collecting from {collector_id}: {e}")
                all_metrics[collector_id] = []
        
        return all_metrics
    
    def get_collector_health(self) -> Dict[str, CollectorHealth]:
        """Get health status of all collectors"""
        health_status = {}
        
        for collector_id, collector in self.collectors.items():
            try:
                health = collector.get_health()
                health_status[collector_id] = health
            except Exception as e:
                self.logger.warning(f"Error getting health for {collector_id}: {e}")
        
        return health_status
    
    def start_background_collection(self) -> bool:
        """Start background collection thread"""
        if self.collection_active:
            self.logger.info("Background collection already active")
            return True
        
        try:
            self.shutdown_event.clear()
            self.collection_thread = threading.Thread(
                target=self._background_collection_loop,
                name="CORTEX-DataCollection",
                daemon=True
            )
            self.collection_thread.start()
            self.collection_active = True
            
            self.logger.info("Started background data collection")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start background collection: {e}")
            return False
    
    def stop_background_collection(self) -> bool:
        """Stop background collection thread"""
        if not self.collection_active:
            return True
        
        try:
            self.shutdown_event.set()
            
            if self.collection_thread and self.collection_thread.is_alive():
                self.collection_thread.join(timeout=10.0)
                
            self.collection_active = False
            self.collection_thread = None
            
            self.logger.info("Stopped background data collection")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop background collection: {e}")
            return False
    
    def _background_collection_loop(self) -> None:
        """Background thread loop for automatic data collection"""
        self.logger.info("Background collection loop started")
        
        while not self.shutdown_event.is_set():
            try:
                # Collect metrics from all collectors
                metrics = self.collect_all_metrics()
                
                # Log collection summary
                total_metrics = sum(len(m) for m in metrics.values())
                if total_metrics > 0:
                    self.logger.debug(f"Background collection: {total_metrics} total metrics")
                
            except Exception as e:
                self.logger.warning(f"Error in background collection: {e}")
            
            # Wait for next collection cycle or shutdown
            if self.shutdown_event.wait(self.collection_interval):
                break  # Shutdown requested
        
        self.logger.info("Background collection loop ended")
    
    # Convenience methods for specific collectors
    
    def track_template_usage(self, template_name: str, response_time_ms: float) -> None:
        """Track response template usage"""
        collector = self.collectors.get("response_templates")
        if collector and hasattr(collector, 'track_template_usage'):
            collector.track_template_usage(template_name, response_time_ms)
    
    def track_token_usage(self, operation_name: str, input_tokens: int, output_tokens: int) -> None:
        """Track token usage for an operation"""
        collector = self.collectors.get("token_usage")
        if collector and hasattr(collector, 'track_operation'):
            collector.track_operation(operation_name, input_tokens, output_tokens)
    
    def track_optimization(self, optimization_name: str, before_tokens: tuple, after_tokens: tuple) -> float:
        """Track token optimization impact"""
        collector = self.collectors.get("token_usage")
        if collector and hasattr(collector, 'track_optimization'):
            return collector.track_optimization(optimization_name, before_tokens, after_tokens)
        return 0.0
    
    # Reporting and summary methods
    
    def get_summary_report(self) -> Dict[str, Any]:
        """Get comprehensive summary of all collectors"""
        summary = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "collectors": {},
            "overall_health": self._calculate_overall_health(),
            "collection_status": {
                "initialized": self.initialized,
                "background_active": self.collection_active,
                "total_collectors": len(self.collectors)
            }
        }
        
        # Get summary from each collector
        for collector_id, collector in self.collectors.items():
            try:
                health = collector.get_health()
                
                collector_summary = {
                    "name": collector.name,
                    "status": health.status.value,
                    "priority": collector.priority.value,
                    "metrics_collected": health.metrics_collected,
                    "last_collection": health.last_collection.isoformat() if health.last_collection else None,
                    "error_count": health.error_count,
                    "collection_rate_per_minute": health.collection_rate_per_minute
                }
                
                # Add collector-specific summary if available
                if hasattr(collector, 'get_brain_summary'):
                    collector_summary["brain_summary"] = collector.get_brain_summary()
                elif hasattr(collector, 'get_template_summary'):
                    collector_summary["template_summary"] = collector.get_template_summary()
                elif hasattr(collector, 'get_usage_summary'):
                    collector_summary["usage_summary"] = collector.get_usage_summary()
                elif hasattr(collector, 'get_workspace_summary'):
                    collector_summary["workspace_summary"] = collector.get_workspace_summary()
                
                summary["collectors"][collector_id] = collector_summary
                
            except Exception as e:
                self.logger.warning(f"Error getting summary for {collector_id}: {e}")
                summary["collectors"][collector_id] = {"error": str(e)}
        
        return summary
    
    def _calculate_overall_health(self) -> Dict[str, Any]:
        """Calculate overall system health based on all collectors"""
        health_data = self.get_collector_health()
        
        if not health_data:
            return {"score": 0, "status": "no_collectors"}
        
        # Calculate health score (0-100)
        active_collectors = sum(1 for h in health_data.values() if h.status.value == "active")
        error_collectors = sum(1 for h in health_data.values() if h.status.value == "error")
        total_collectors = len(health_data)
        
        if total_collectors == 0:
            health_score = 0
        else:
            health_score = (active_collectors / total_collectors) * 100
            # Penalize for errors
            if error_collectors > 0:
                health_score *= (1 - (error_collectors / total_collectors) * 0.5)
        
        # Determine overall status
        if health_score >= 80:
            overall_status = "healthy"
        elif health_score >= 60:
            overall_status = "warning"
        elif health_score >= 40:
            overall_status = "degraded"
        else:
            overall_status = "critical"
        
        return {
            "score": round(health_score, 1),
            "status": overall_status,
            "active_collectors": active_collectors,
            "total_collectors": total_collectors,
            "error_collectors": error_collectors
        }
    
    def shutdown(self) -> bool:
        """Shutdown all collectors and cleanup resources"""
        try:
            self.logger.info("Shutting down collector manager...")
            
            # Stop background collection
            self.stop_background_collection()
            
            # Stop all collectors
            self.stop_all_collectors()
            
            # Clear registry
            for collector_id in list(self.collectors.keys()):
                collector_registry.unregister(collector_id)
            
            self.collectors.clear()
            self.initialized = False
            
            self.logger.info("Collector manager shutdown complete")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
            return False


# Global collector manager instance
_collector_manager: Optional[CollectorManager] = None


def get_collector_manager(brain_path: Optional[str] = None, 
                         workspace_path: Optional[str] = None) -> CollectorManager:
    """Get or create the global collector manager instance"""
    global _collector_manager
    
    if _collector_manager is None:
        _collector_manager = CollectorManager(
            brain_path=brain_path,
            workspace_path=workspace_path,
            auto_start=True
        )
    
    return _collector_manager


def initialize_data_collectors(brain_path: Optional[str] = None, 
                              workspace_path: Optional[str] = None) -> bool:
    """Initialize the CORTEX data collection system"""
    try:
        manager = get_collector_manager(brain_path, workspace_path)
        return manager.initialize()
    except Exception as e:
        logging.getLogger("cortex.collectors").error(f"Failed to initialize data collectors: {e}")
        return False