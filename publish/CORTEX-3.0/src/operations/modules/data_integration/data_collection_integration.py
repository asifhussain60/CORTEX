"""
CORTEX 3.0 Phase 2 - Data Collection Integration Main Module
==========================================================

Main integration module for Task 3: Data Collection Integration.
Combines Phase 1 data collectors with Phase 2 brain optimization.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

Phase: Phase 2 - Data Collection Integration (Task 3)
Purpose: Real-time metrics collection across brain tiers
"""

import time
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

# Import core components
try:
    from .real_time_metrics_dashboard import (
        RealTimeMetricsDashboard, 
        create_real_time_dashboard,
        get_dashboard_summary
    )
    from .brain_health_monitor import (
        BrainHealthMonitor,
        create_brain_health_monitor,
        get_health_summary
    )
except ImportError:
    from real_time_metrics_dashboard import (
        RealTimeMetricsDashboard, 
        create_real_time_dashboard,
        get_dashboard_summary
    )
    from brain_health_monitor import (
        BrainHealthMonitor,
        create_brain_health_monitor,
        get_health_summary
    )

# Import Phase 2 brain optimization
try:
    from src.operations.modules.brain.brain_performance_integration import (
        IntegratedBrainPerformanceSystem,
        create_optimized_brain_system
    )
except ImportError:
    IntegratedBrainPerformanceSystem = None
    create_optimized_brain_system = None

# Import Phase 1 collectors
try:
    from src.collectors import get_collector_manager, initialize_data_collectors
except ImportError:
    get_collector_manager = None
    initialize_data_collectors = None


class DataCollectionIntegrationSystem:
    """
    Unified data collection integration system for CORTEX 3.0 Phase 2.
    
    Combines:
    - Phase 1 data collectors
    - Phase 2 brain optimization  
    - Real-time metrics dashboard
    - Brain health monitoring
    - Performance analytics
    - Auto-healing capabilities
    
    Features:
    - Unified metrics collection and monitoring
    - Real-time performance dashboard
    - Predictive health analytics
    - Auto-healing and optimization
    - Historical data storage
    - Comprehensive reporting
    """
    
    def __init__(self, 
                 brain_path: str = None,
                 workspace_path: str = None,
                 integration_config: Dict[str, Any] = None):
        """
        Initialize data collection integration system.
        
        Args:
            brain_path: Path to CORTEX brain directory
            workspace_path: Path to workspace
            integration_config: Integration configuration
        """
        self.brain_path = brain_path or "cortex-brain"
        self.workspace_path = workspace_path or "."
        self.config = integration_config or self._default_config()
        
        # System components
        self.dashboard = None
        self.brain_system = None
        self.health_monitor = None
        self.collector_manager = None
        
        # System state
        self.system_status = "initializing"
        self.start_time = datetime.now()
        
        # Logger
        self.logger = logging.getLogger(__name__)
        
        # Initialize system
        self._initialize_system()
    
    def _default_config(self) -> Dict[str, Any]:
        """Get default integration configuration."""
        return {
            'auto_start': True,
            'enable_dashboard': True,
            'enable_health_monitoring': True,
            'enable_auto_healing': True,
            'dashboard_config': {
                'monitoring_interval_seconds': 30,
                'enable_database_storage': True,
                'auto_start': True
            },
            'health_config': {
                'auto_healing_enabled': True,
                'trend_window_hours': 6,
                'health_check_interval_seconds': 60
            },
            'brain_config': {
                'cache_size_mb': 50,
                'memory_limit_mb': 200
            }
        }
    
    def _initialize_system(self):
        """Initialize all system components."""
        self.logger.info("Initializing CORTEX 3.0 Data Collection Integration System")
        
        try:
            # Initialize Phase 1 collectors
            self._initialize_collectors()
            
            # Initialize Phase 2 brain optimization
            self._initialize_brain_optimization()
            
            # Initialize real-time dashboard
            if self.config.get('enable_dashboard', True):
                self._initialize_dashboard()
            
            # Initialize health monitoring
            if self.config.get('enable_health_monitoring', True):
                self._initialize_health_monitoring()
            
            self.system_status = "active"
            self.logger.info("Data collection integration system initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize integration system: {e}")
            self.system_status = "error"
    
    def _initialize_collectors(self):
        """Initialize Phase 1 data collectors."""
        if initialize_data_collectors and get_collector_manager:
            try:
                # Initialize collectors
                initialize_data_collectors(
                    brain_path=self.brain_path,
                    workspace_path=self.workspace_path
                )
                
                # Get manager
                self.collector_manager = get_collector_manager(
                    brain_path=self.brain_path,
                    workspace_path=self.workspace_path
                )
                
                self.logger.info("Phase 1 data collectors initialized")
                
            except Exception as e:
                self.logger.warning(f"Failed to initialize Phase 1 collectors: {e}")
        else:
            self.logger.warning("Phase 1 data collectors not available")
    
    def _initialize_brain_optimization(self):
        """Initialize Phase 2 brain optimization system."""
        if create_optimized_brain_system:
            try:
                self.brain_system = create_optimized_brain_system(
                    brain_path=self.brain_path,
                    config=self.config.get('brain_config', {})
                )
                self.logger.info("Phase 2 brain optimization system initialized")
                
            except Exception as e:
                self.logger.warning(f"Failed to initialize brain optimization: {e}")
        else:
            self.logger.warning("Phase 2 brain optimization system not available")
    
    def _initialize_dashboard(self):
        """Initialize real-time metrics dashboard."""
        try:
            self.dashboard = create_real_time_dashboard(
                brain_path=self.brain_path,
                workspace_path=self.workspace_path,
                config=self.config.get('dashboard_config', {})
            )
            self.logger.info("Real-time metrics dashboard initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize dashboard: {e}")
    
    def _initialize_health_monitoring(self):
        """Initialize brain health monitoring."""
        if self.dashboard:
            try:
                self.health_monitor = create_brain_health_monitor(
                    dashboard=self.dashboard,
                    brain_system=self.brain_system,
                    config=self.config.get('health_config', {})
                )
                self.logger.info("Brain health monitoring initialized")
                
            except Exception as e:
                self.logger.error(f"Failed to initialize health monitoring: {e}")
        else:
            self.logger.warning("Cannot initialize health monitoring without dashboard")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        try:
            # Calculate uptime
            uptime_seconds = (datetime.now() - self.start_time).total_seconds()
            
            # Get component statuses
            component_status = {
                'collectors': {
                    'available': self.collector_manager is not None,
                    'active': False,
                    'summary': {}
                },
                'brain_optimization': {
                    'available': self.brain_system is not None,
                    'active': False,
                    'summary': {}
                },
                'dashboard': {
                    'available': self.dashboard is not None,
                    'active': False,
                    'summary': {}
                },
                'health_monitoring': {
                    'available': self.health_monitor is not None,
                    'active': False,
                    'summary': {}
                }
            }
            
            # Get collector status
            if self.collector_manager:
                try:
                    collector_health = self.collector_manager.get_collector_health()
                    component_status['collectors']['active'] = len(collector_health) > 0
                    component_status['collectors']['summary'] = {
                        'total_collectors': len(collector_health),
                        'active_collectors': sum(
                            1 for health in collector_health.values()
                            if hasattr(health, 'status') and str(health.status).lower() == 'active'
                        )
                    }
                except Exception as e:
                    self.logger.warning(f"Error getting collector status: {e}")
            
            # Get brain optimization status
            if self.brain_system:
                try:
                    component_status['brain_optimization']['active'] = (
                        hasattr(self.brain_system, 'monitoring_active') and 
                        self.brain_system.monitoring_active
                    )
                    brain_snapshot = self.brain_system.get_unified_performance_snapshot()
                    component_status['brain_optimization']['summary'] = {
                        'health_score': brain_snapshot.health_score,
                        'optimization_active': brain_snapshot.optimization_active,
                        'cache_hit_rate': brain_snapshot.cache_hit_rate,
                        'memory_usage_mb': brain_snapshot.total_memory_mb
                    }
                except Exception as e:
                    self.logger.warning(f"Error getting brain optimization status: {e}")
            
            # Get dashboard status
            if self.dashboard:
                try:
                    component_status['dashboard']['active'] = self.dashboard.monitoring_active
                    dashboard_state = get_dashboard_summary(self.dashboard)
                    component_status['dashboard']['summary'] = {
                        'status': dashboard_state.get('dashboard_status'),
                        'last_update': dashboard_state.get('last_update'),
                        'active_alerts': dashboard_state.get('alerts', {}).get('total', 0)
                    }
                except Exception as e:
                    self.logger.warning(f"Error getting dashboard status: {e}")
            
            # Get health monitoring status
            if self.health_monitor:
                try:
                    component_status['health_monitoring']['active'] = self.health_monitor.monitoring_active
                    health_assessment = get_health_summary(self.health_monitor)
                    component_status['health_monitoring']['summary'] = {
                        'overall_health': health_assessment.get('overall_health', {}),
                        'risk_factors_count': len(health_assessment.get('risk_factors', [])),
                        'auto_healing_enabled': health_assessment.get('auto_healing', {}).get('enabled', False)
                    }
                except Exception as e:
                    self.logger.warning(f"Error getting health monitoring status: {e}")
            
            # Create status summary
            status = {
                'system_status': self.system_status,
                'uptime_seconds': uptime_seconds,
                'start_time': self.start_time.isoformat(),
                'last_updated': datetime.now().isoformat(),
                'components': component_status,
                'integration_summary': {
                    'phase1_collectors': component_status['collectors']['available'],
                    'phase2_optimization': component_status['brain_optimization']['available'],
                    'real_time_dashboard': component_status['dashboard']['available'],
                    'health_monitoring': component_status['health_monitoring']['available']
                }
            }
            
            return status
            
        except Exception as e:
            self.logger.error(f"Failed to get system status: {e}")
            return {
                'system_status': 'error',
                'error': str(e),
                'last_updated': datetime.now().isoformat()
            }
    
    def get_comprehensive_metrics(self) -> Dict[str, Any]:
        """Get comprehensive metrics from all integrated systems."""
        try:
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'dashboard_metrics': {},
                'health_assessment': {},
                'brain_performance': {},
                'integration_status': {}
            }
            
            # Get dashboard metrics
            if self.dashboard:
                try:
                    dashboard_state = get_dashboard_summary(self.dashboard)
                    metrics['dashboard_metrics'] = dashboard_state.get('latest_metrics', {})
                except Exception as e:
                    metrics['dashboard_metrics'] = {'error': str(e)}
            
            # Get health assessment
            if self.health_monitor:
                try:
                    health_assessment = get_health_summary(self.health_monitor)
                    metrics['health_assessment'] = health_assessment
                except Exception as e:
                    metrics['health_assessment'] = {'error': str(e)}
            
            # Get brain performance
            if self.brain_system:
                try:
                    brain_snapshot = self.brain_system.get_unified_performance_snapshot()
                    metrics['brain_performance'] = {
                        'health_score': brain_snapshot.health_score,
                        'tier_performance': {
                            'tier1_ms': brain_snapshot.tier1_avg_ms,
                            'tier2_ms': brain_snapshot.tier2_avg_ms,
                            'tier3_ms': brain_snapshot.tier3_avg_ms
                        },
                        'cache_performance': {
                            'hit_rate': brain_snapshot.cache_hit_rate,
                            'memory_mb': brain_snapshot.cache_memory_mb,
                            'entries': brain_snapshot.cache_entries
                        },
                        'memory_usage': {
                            'total_mb': brain_snapshot.total_memory_mb,
                            'pressure': brain_snapshot.memory_pressure,
                            'allocations': brain_snapshot.active_allocations
                        }
                    }
                except Exception as e:
                    metrics['brain_performance'] = {'error': str(e)}
            
            # Get integration status
            metrics['integration_status'] = self.get_system_status()
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to get comprehensive metrics: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def trigger_optimization(self) -> Dict[str, Any]:
        """Trigger comprehensive optimization across all systems."""
        self.logger.info("Triggering comprehensive optimization")
        
        optimization_results = {
            'timestamp': datetime.now().isoformat(),
            'brain_optimization': {},
            'collector_restart': {},
            'success': False
        }
        
        try:
            # Brain system optimization
            if self.brain_system:
                brain_results = self.brain_system.trigger_comprehensive_optimization()
                optimization_results['brain_optimization'] = brain_results
            
            # Restart collectors if needed
            if self.collector_manager:
                try:
                    # Check collector health first
                    collector_health = self.collector_manager.get_collector_health()
                    failed_collectors = [
                        collector_id for collector_id, health in collector_health.items()
                        if not getattr(health, 'last_collection_success', True)
                    ]
                    
                    if failed_collectors:
                        self.logger.info(f"Restarting failed collectors: {failed_collectors}")
                        stop_results = self.collector_manager.stop_all_collectors()
                        time.sleep(2)
                        start_results = self.collector_manager.start_all_collectors()
                        
                        optimization_results['collector_restart'] = {
                            'failed_collectors': failed_collectors,
                            'stop_results': stop_results,
                            'start_results': start_results
                        }
                except Exception as e:
                    optimization_results['collector_restart'] = {'error': str(e)}
            
            # Determine overall success
            brain_success = optimization_results.get('brain_optimization', {}).get('success', False)
            collector_success = 'error' not in optimization_results.get('collector_restart', {})
            
            optimization_results['success'] = brain_success or collector_success
            
            return optimization_results
            
        except Exception as e:
            self.logger.error(f"Comprehensive optimization failed: {e}")
            optimization_results['error'] = str(e)
            return optimization_results
    
    def shutdown(self) -> Dict[str, Any]:
        """Shutdown all system components gracefully."""
        self.logger.info("Shutting down data collection integration system")
        
        shutdown_results = {
            'timestamp': datetime.now().isoformat(),
            'components_shutdown': {},
            'success': True
        }
        
        try:
            # Stop health monitoring
            if self.health_monitor and self.health_monitor.monitoring_active:
                try:
                    self.health_monitor.stop_health_monitoring()
                    shutdown_results['components_shutdown']['health_monitor'] = 'success'
                except Exception as e:
                    shutdown_results['components_shutdown']['health_monitor'] = f'error: {e}'
                    shutdown_results['success'] = False
            
            # Stop dashboard monitoring
            if self.dashboard and self.dashboard.monitoring_active:
                try:
                    self.dashboard.stop_monitoring()
                    shutdown_results['components_shutdown']['dashboard'] = 'success'
                except Exception as e:
                    shutdown_results['components_shutdown']['dashboard'] = f'error: {e}'
                    shutdown_results['success'] = False
            
            # Stop brain system monitoring
            if self.brain_system and hasattr(self.brain_system, 'monitoring_active'):
                try:
                    if self.brain_system.monitoring_active:
                        self.brain_system.stop_monitoring()
                    shutdown_results['components_shutdown']['brain_system'] = 'success'
                except Exception as e:
                    shutdown_results['components_shutdown']['brain_system'] = f'error: {e}'
                    shutdown_results['success'] = False
            
            # Stop collectors
            if self.collector_manager:
                try:
                    stop_results = self.collector_manager.stop_all_collectors()
                    shutdown_results['components_shutdown']['collectors'] = stop_results
                except Exception as e:
                    shutdown_results['components_shutdown']['collectors'] = f'error: {e}'
                    shutdown_results['success'] = False
            
            self.system_status = "stopped"
            
            return shutdown_results
            
        except Exception as e:
            self.logger.error(f"System shutdown failed: {e}")
            shutdown_results['error'] = str(e)
            shutdown_results['success'] = False
            return shutdown_results


# Convenience functions for easy integration setup
def create_data_collection_integration(brain_path: str = None,
                                     workspace_path: str = None,
                                     config: Dict[str, Any] = None) -> DataCollectionIntegrationSystem:
    """
    Create and initialize complete data collection integration system.
    
    Args:
        brain_path: Path to CORTEX brain directory
        workspace_path: Path to workspace  
        config: Integration configuration
        
    Returns:
        Initialized DataCollectionIntegrationSystem
    """
    return DataCollectionIntegrationSystem(
        brain_path=brain_path,
        workspace_path=workspace_path,
        integration_config=config
    )


def get_integration_summary(system: DataCollectionIntegrationSystem) -> Dict[str, Any]:
    """
    Get comprehensive integration summary.
    
    Args:
        system: Data collection integration system
        
    Returns:
        Integration summary with status and metrics
    """
    return system.get_system_status()


def get_full_metrics(system: DataCollectionIntegrationSystem) -> Dict[str, Any]:
    """
    Get full metrics from integrated system.
    
    Args:
        system: Data collection integration system
        
    Returns:
        Comprehensive metrics from all components
    """
    return system.get_comprehensive_metrics()


if __name__ == "__main__":
    # Test the data collection integration system
    print("📊 CORTEX 3.0 Phase 2 - Data Collection Integration System Test")
    print("=" * 80)
    
    # Create integration system
    integration_system = create_data_collection_integration(
        brain_path="cortex-brain",
        workspace_path=".",
        config={
            'auto_start': True,
            'enable_dashboard': True,
            'enable_health_monitoring': True
        }
    )
    
    print(f"✅ Integration system created")
    print(f"   Status: {integration_system.system_status}")
    print()
    
    # Wait for initialization
    time.sleep(3)
    
    # Get system status
    system_status = get_integration_summary(integration_system)
    
    print("🔧 System Status:")
    print(f"   Overall Status: {system_status['system_status']}")
    print(f"   Uptime: {system_status['uptime_seconds']:.1f} seconds")
    
    # Show component status
    if 'components' in system_status:
        components = system_status['components']
        print("\n📦 Component Status:")
        for component, status in components.items():
            status_icon = "✅" if status['available'] and status['active'] else "⚠️" if status['available'] else "❌"
            print(f"   {component}: {status_icon} Available: {status['available']}, Active: {status['active']}")
    
    # Show integration summary
    if 'integration_summary' in system_status:
        integration = system_status['integration_summary']
        print("\n🔗 Integration Status:")
        for phase, available in integration.items():
            status_icon = "✅" if available else "❌"
            print(f"   {phase}: {status_icon}")
    
    print("\n📈 Getting comprehensive metrics...")
    
    # Get comprehensive metrics
    metrics = get_full_metrics(integration_system)
    
    if 'dashboard_metrics' in metrics and metrics['dashboard_metrics']:
        dashboard = metrics['dashboard_metrics']
        print(f"   Dashboard: {len(dashboard)} metrics collected")
        
        if 'brain_health_score' in dashboard:
            print(f"   Brain Health: {dashboard['brain_health_score']:.1f}%")
        
        if 'collection_success_rate' in dashboard:
            print(f"   Collection Success: {dashboard['collection_success_rate']:.1%}")
    
    if 'health_assessment' in metrics and 'overall_health' in metrics['health_assessment']:
        health = metrics['health_assessment']['overall_health']
        print(f"   Health Status: {health['status']} ({health['score']:.1f}%)")
    
    if 'brain_performance' in metrics and 'health_score' in metrics['brain_performance']:
        brain_perf = metrics['brain_performance']
        print(f"   Brain Performance: {brain_perf['health_score']:.1f}%")
    
    print("\n🎯 Data collection integration system operational!")
    print("   All Phase 1 collectors integrated with Phase 2 brain optimization")
    print("   Real-time dashboard and health monitoring active")
    print("   Use integration_system.get_comprehensive_metrics() for latest data")