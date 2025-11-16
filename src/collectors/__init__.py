"""
CORTEX 3.0 - Data Collectors Package
===================================

Real-time data collection system for CORTEX metrics and monitoring.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

Feature: Quick Win #3 (Week 1)
Components:
- BaseCollector: Foundation class for all collectors
- ResponseTemplateMetricsCollector: Template usage and performance
- BrainPerformanceCollector: Brain health and optimization
- TokenUsageCollector: Token consumption and cost monitoring
- WorkspaceHealthCollector: Development environment health
- CollectorManager: Unified management and coordination

Usage:
    from src.collectors import initialize_data_collectors, get_collector_manager
    
    # Initialize the collection system
    initialize_data_collectors(
        brain_path="/path/to/cortex-brain",
        workspace_path="/path/to/workspace"
    )
    
    # Get manager for manual control
    manager = get_collector_manager()
    summary = manager.get_summary_report()
"""

from .base_collector import (
    BaseCollector, 
    CollectorMetric, 
    CollectorHealth, 
    CollectorStatus, 
    CollectorPriority,
    ICollector,
    CollectorRegistry,
    collector_registry
)

from .response_template_collector import ResponseTemplateMetricsCollector
from .brain_performance_collector import BrainPerformanceCollector
from .token_usage_collector import TokenUsageCollector
from .workspace_health_collector import WorkspaceHealthCollector
from .conversation_collector import ConversationCollector

from .manager import (
    CollectorManager,
    get_collector_manager,
    initialize_data_collectors
)

# Package metadata
__version__ = "1.0.0"
__author__ = "Asif Hussain"
__license__ = "Proprietary"

# Core collectors available
CORE_COLLECTORS = [
    "response_templates",
    "brain_performance", 
    "token_usage",
    "workspace_health"
]

# Quick initialization function
def quick_start(brain_path: str = None, workspace_path: str = None) -> CollectorManager:
    """
    Quick start the CORTEX data collection system.
    
    Args:
        brain_path: Path to CORTEX brain directory
        workspace_path: Path to workspace directory
        
    Returns:
        CollectorManager: Initialized manager instance
    """
    initialize_data_collectors(brain_path, workspace_path)
    return get_collector_manager()


# Convenience functions for common operations
def track_template_usage(template_name: str, response_time_ms: float) -> None:
    """Track response template usage"""
    manager = get_collector_manager()
    manager.track_template_usage(template_name, response_time_ms)


def track_token_usage(operation_name: str, input_tokens: int, output_tokens: int) -> None:
    """Track token usage for an operation"""
    manager = get_collector_manager()
    manager.track_token_usage(operation_name, input_tokens, output_tokens)


def track_optimization(optimization_name: str, before_tokens: tuple, after_tokens: tuple) -> float:
    """Track optimization impact and return cost savings"""
    manager = get_collector_manager()
    return manager.track_optimization(optimization_name, before_tokens, after_tokens)


def get_system_health() -> dict:
    """Get overall system health summary"""
    manager = get_collector_manager()
    return manager.get_summary_report()


# Export all public symbols
__all__ = [
    # Core classes
    "BaseCollector",
    "CollectorMetric", 
    "CollectorHealth",
    "CollectorStatus",
    "CollectorPriority", 
    "ICollector",
    "CollectorRegistry",
    "collector_registry",
    
    # Collector implementations
    "ResponseTemplateMetricsCollector",
    "BrainPerformanceCollector",
    "TokenUsageCollector", 
    "WorkspaceHealthCollector",
    "ConversationCollector",
    
    # Management
    "CollectorManager",
    "get_collector_manager",
    "initialize_data_collectors",
    
    # Convenience functions
    "quick_start",
    "track_template_usage",
    "track_token_usage", 
    "track_optimization",
    "get_system_health",
    
    # Constants
    "CORE_COLLECTORS"
]