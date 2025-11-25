"""
CORTEX Health Check Operation Module

Provides system health monitoring and performance diagnostics.
Part of user-facing entry points for deployment.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import logging
import sqlite3
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
import psutil

from .base_operation_module import (
    BaseOperationModule,
    OperationResult,
    OperationStatus,
    OperationPhase,
    OperationModuleMetadata,
)


logger = logging.getLogger(__name__)


class HealthCheckOperation(BaseOperationModule):
    """
    Health check and performance monitoring for CORTEX.
    
    Features:
    - System resource usage (CPU, memory, disk)
    - Database health checks
    - Brain integrity validation
    - Performance metrics
    - Configuration validation
    
    Usage:
        User says: "healthcheck" or "cortex performance" or "system status"
        CORTEX routes to this module
    """
    
    def __init__(self):
        super().__init__()
        self._metadata = OperationModuleMetadata(
            module_id="healthcheck",
            name="healthcheck",
            description="System health and performance monitoring",
            phase=OperationPhase.VALIDATION,
            priority=50,
            version="1.0.0",
            author="Asif Hussain",
            tags=["user-facing", "monitoring", "diagnostics"],
        )
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Return operation metadata."""
        return self._metadata
    
    def validate(self) -> OperationResult:
        """
        Validate health check can run.
        
        Returns:
            OperationResult with validation status
        """
        # Health check should always run (even if CORTEX unhealthy)
        return OperationResult(
            status=OperationStatus.SUCCESS,
            message="✓ Health check ready",
            phase=OperationPhase.VALIDATION,
        )
    
    def execute(self, **kwargs) -> OperationResult:
        """
        Execute health check.
        
        Args:
            detailed: Include detailed diagnostics
            component: Specific component to check (brain/database/system/all)
        
        Returns:
            OperationResult with health report
        """
        detailed = kwargs.get('detailed', False)
        component = kwargs.get('component', 'all')
        
        logger.info(f"Running health check (component={component}, detailed={detailed})")
        
        health_report = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy',
            'checks': {},
            'warnings': [],
            'errors': [],
        }
        
        try:
            # System resource check
            if component in ['system', 'all']:
                system_check = self._check_system_resources()
                health_report['checks']['system'] = system_check
                if system_check['status'] == 'warning':
                    health_report['warnings'].extend(system_check['issues'])
                elif system_check['status'] == 'critical':
                    health_report['errors'].extend(system_check['issues'])
                    health_report['overall_status'] = 'unhealthy'
            
            # Brain integrity check
            if component in ['brain', 'all']:
                brain_check = self._check_brain_integrity()
                health_report['checks']['brain'] = brain_check
                if brain_check['status'] == 'warning':
                    health_report['warnings'].extend(brain_check['issues'])
                elif brain_check['status'] == 'critical':
                    health_report['errors'].extend(brain_check['issues'])
                    health_report['overall_status'] = 'unhealthy'
            
            # Database health check
            if component in ['database', 'all']:
                db_check = self._check_databases()
                health_report['checks']['database'] = db_check
                if db_check['status'] == 'warning':
                    health_report['warnings'].extend(db_check['issues'])
                elif db_check['status'] == 'critical':
                    health_report['errors'].extend(db_check['issues'])
                    health_report['overall_status'] = 'unhealthy'
            
            # Performance metrics
            if component in ['performance', 'all'] or detailed:
                perf_check = self._check_performance()
                health_report['checks']['performance'] = perf_check
            
            # Determine final status
            if health_report['errors']:
                status = OperationStatus.FAILED
                message = f"⚠️ Health check: UNHEALTHY ({len(health_report['errors'])} critical issues)"
            elif health_report['warnings']:
                status = OperationStatus.SUCCESS
                message = f"⚠️ Health check: WARNING ({len(health_report['warnings'])} warnings)"
            else:
                status = OperationStatus.SUCCESS
                message = "✅ Health check: HEALTHY"
            
            return OperationResult(
                status=status,
                message=message,
                phase=OperationPhase.COMPLETE,
                data=health_report,
            )
            
        except Exception as e:
            logger.error(f"Health check failed: {e}", exc_info=True)
            return OperationResult(
                status=OperationStatus.FAILED,
                message=f"Health check failed: {str(e)}",
                phase=OperationPhase.EXECUTION,
                error=e,
            )
    
    def _check_system_resources(self) -> Dict[str, Any]:
        """Check system resource usage."""
        issues = []
        status = 'healthy'
        
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > 90:
                issues.append(f"High CPU usage: {cpu_percent}%")
                status = 'warning'
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            if memory_percent > 90:
                issues.append(f"High memory usage: {memory_percent}%")
                status = 'critical'
            elif memory_percent > 80:
                issues.append(f"Elevated memory usage: {memory_percent}%")
                status = 'warning'
            
            # Disk usage
            disk = psutil.disk_usage(str(Path.cwd()))
            disk_percent = disk.percent
            if disk_percent > 95:
                issues.append(f"Critical disk usage: {disk_percent}%")
                status = 'critical'
            elif disk_percent > 85:
                issues.append(f"High disk usage: {disk_percent}%")
                status = 'warning'
            
            return {
                'status': status,
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'memory_available_mb': memory.available / (1024 * 1024),
                'disk_percent': disk_percent,
                'disk_free_gb': disk.free / (1024 * 1024 * 1024),
                'issues': issues,
            }
            
        except Exception as e:
            logger.error(f"System resource check failed: {e}")
            return {
                'status': 'error',
                'issues': [f"Failed to check system resources: {str(e)}"],
            }
    
    def _check_brain_integrity(self) -> Dict[str, Any]:
        """Check CORTEX brain integrity."""
        issues = []
        status = 'healthy'
        
        brain_path = Path.cwd() / "cortex-brain"
        
        # Check brain directory exists
        if not brain_path.exists():
            return {
                'status': 'critical',
                'issues': ['cortex-brain/ directory not found'],
            }
        
        # Check critical files
        critical_files = [
            'brain-protection-rules.yaml',
            'schema.sql',
            'response-templates.yaml',
        ]
        
        for file_name in critical_files:
            file_path = brain_path / file_name
            if not file_path.exists():
                issues.append(f"Missing critical file: {file_name}")
                status = 'critical'
        
        # Check tier directories
        tiers = ['tier1', 'tier2', 'tier3']
        for tier in tiers:
            tier_path = brain_path / tier
            if not tier_path.exists():
                issues.append(f"Missing {tier}/ directory")
                status = 'warning'
        
        # Check documents organization
        docs_path = brain_path / "documents"
        if not docs_path.exists():
            issues.append("Missing documents/ directory")
            status = 'warning'
        
        return {
            'status': status,
            'brain_path': str(brain_path),
            'brain_exists': brain_path.exists(),
            'issues': issues,
        }
    
    def _check_databases(self) -> Dict[str, Any]:
        """Check database health."""
        issues = []
        status = 'healthy'
        db_stats = {}
        
        brain_path = Path.cwd() / "cortex-brain"
        
        databases = {
            'tier1': brain_path / "tier1" / "working_memory.db",
            'tier2': brain_path / "tier2" / "knowledge-graph.db",
        }
        
        for db_name, db_path in databases.items():
            if not db_path.exists():
                issues.append(f"{db_name} database not found: {db_path.name}")
                status = 'critical'
                continue
            
            try:
                # Get database size
                size_mb = db_path.stat().st_size / (1024 * 1024)
                
                # Try to connect
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
                
                # Check integrity
                cursor.execute("PRAGMA integrity_check")
                integrity_result = cursor.fetchone()[0]
                
                if integrity_result != 'ok':
                    issues.append(f"{db_name} database integrity check failed")
                    status = 'critical'
                
                # Get table count
                cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                table_count = cursor.fetchone()[0]
                
                conn.close()
                
                db_stats[db_name] = {
                    'size_mb': round(size_mb, 2),
                    'integrity': integrity_result,
                    'table_count': table_count,
                }
                
            except Exception as e:
                issues.append(f"{db_name} database check failed: {str(e)}")
                status = 'warning'
        
        return {
            'status': status,
            'databases': db_stats,
            'issues': issues,
        }
    
    def _check_performance(self) -> Dict[str, Any]:
        """Check performance metrics."""
        try:
            from src.utils.yaml_cache import get_cache_stats
            
            cache_stats = get_cache_stats()
            
            return {
                'yaml_cache': {
                    'entries': cache_stats['total_entries'],
                    'hit_rate': f"{cache_stats['hit_rate']*100:.1f}%",
                    'total_hits': cache_stats['total_hits'],
                    'total_misses': cache_stats['total_misses'],
                },
                'suggestions': self._get_performance_suggestions(cache_stats),
            }
            
        except Exception as e:
            logger.warning(f"Performance check failed: {e}")
            return {
                'error': str(e),
            }
    
    def _get_performance_suggestions(self, cache_stats: Dict) -> List[str]:
        """Generate performance improvement suggestions."""
        suggestions = []
        
        # Cache hit rate suggestions
        if cache_stats['hit_rate'] < 0.5:
            suggestions.append("Low cache hit rate - consider preloading frequently used YAML files")
        
        # Memory suggestions
        memory = psutil.virtual_memory()
        if memory.percent > 80:
            suggestions.append("High memory usage - run 'optimize' to clean up temporary files")
        
        # Disk suggestions
        disk = psutil.disk_usage(str(Path.cwd()))
        if disk.percent > 85:
            suggestions.append("High disk usage - run 'optimize' to reclaim space")
        
        return suggestions
    
    def rollback(self) -> OperationResult:
        """
        Rollback health check (not applicable).
        
        Returns:
            OperationResult indicating rollback not supported
        """
        return OperationResult(
            status=OperationStatus.SUCCESS,
            message="Health check rollback not applicable (read-only operation)",
            phase=OperationPhase.ROLLBACK,
        )
