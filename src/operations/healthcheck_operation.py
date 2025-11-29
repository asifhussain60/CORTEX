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
from .modules.healthcheck.brain_analytics_collector import BrainAnalyticsCollector
from .modules.healthcheck.strategic_feature_validator import StrategicFeatureValidator

# Enhancement Catalog imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.enhancement_catalog import EnhancementCatalog
from discovery.enhancement_discovery import EnhancementDiscoveryEngine


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
            detailed: Include detailed diagnostics (default: False)
            component: Specific component to check (brain/database/system/all)
            quick: Skip expensive operations for fast validation (default: False)
        
        Returns:
            OperationResult with health report
        """
        detailed = kwargs.get('detailed', False)
        component = kwargs.get('component', 'all')
        quick = kwargs.get('quick', False)
        
        logger.info(f"Running health check (component={component}, detailed={detailed}, quick={quick})")
        
        health_report = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy',
            'checks': {},
            'warnings': [],
            'errors': [],
        }
        
        # Safe default for downstream references
        brain_analytics: Dict[str, Any] = {}

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
            
            # Brain analytics (comprehensive brain tier analysis)
            if component in ['brain', 'all'] and not quick:
                logger.info("Collecting brain analytics...")
                brain_analytics = self._check_brain_analytics()
                health_report['checks']['brain_analytics'] = brain_analytics
            
            # Strategic feature health (Architecture/Rollback/Swagger/UX/ADO)
            if component in ['strategic', 'all']:
                strategic = self._check_strategic_features()
                health_report['checks']['strategic_features'] = strategic
                # Aggregate issues
                for k, v in strategic.items():
                    status = v.get('status')
                    issues = v.get('issues', [])
                    if status == 'warning':
                        health_report['warnings'].extend(issues)
                    elif status == 'critical':
                        health_report['errors'].extend(issues)
                        health_report['overall_status'] = 'unhealthy'
            
            # Enhancement Catalog health check
            if component in ['catalog', 'all']:
                catalog_check = self._check_catalog_health()
                health_report['checks']['catalog'] = catalog_check
                if catalog_check['status'] == 'warning':
                    health_report['warnings'].extend(catalog_check['issues'])
                elif catalog_check['status'] == 'critical':
                    health_report['errors'].extend(catalog_check['issues'])
                    if health_report['overall_status'] == 'healthy':
                        health_report['overall_status'] = 'warning'
                
                # Add brain recommendations
                if brain_analytics.get('recommendations'):
                    health_report['warnings'].extend(brain_analytics['recommendations'])
            
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
                success=status == OperationStatus.SUCCESS,
                status=status,
                message=message,
                data=health_report,
            )
            
        except Exception as e:
            logger.error(f"Health check failed: {e}", exc_info=True)
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Health check failed: {str(e)}",
                errors=[str(e)],
            )

    def _check_strategic_features(self) -> Dict[str, Any]:
        """Run strategic feature validators and return a structured dict."""
        try:
            validator = StrategicFeatureValidator()
            results = {
                'architecture_intelligence': validator.validate_architecture_intelligence(),
                'rollback_system': validator.validate_rollback_system(),
                'swagger_dor': validator.validate_swagger_dor(),
                'ux_enhancement': validator.validate_ux_enhancement(),
                'ado_agent': validator.validate_ado_agent(),
            }
            return results
        except Exception as e:
            logger.warning(f"Strategic feature validation failed: {e}")
            return {
                'error': str(e)
            }
    
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
            'tier2': brain_path / "tier2" / "knowledge_graph.db",
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
                    'entries': cache_stats.get('total_files', 0),
                    'hit_rate': f"{cache_stats.get('overall_hit_rate', 0):.1f}%",
                    'total_hits': cache_stats.get('total_hits', 0),
                    'total_misses': cache_stats.get('total_misses', 0),
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
        hit_rate = cache_stats.get('overall_hit_rate', 0)
        if hit_rate < 50:
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
    
    def _check_brain_analytics(self) -> Dict[str, Any]:
        """
        Check comprehensive brain analytics across all tiers.
        
        Returns:
            Dict with brain analytics from all tiers
        """
        try:
            collector = BrainAnalyticsCollector()
            analytics = collector.collect_all_analytics()
            
            logger.info(
                f"Brain health score: {analytics.get('health_score')}% "
                f"(Tier1: {analytics.get('tier1', {}).get('status')}, "
                f"Tier2: {analytics.get('tier2', {}).get('status')}, "
                f"Tier3: {analytics.get('tier3', {}).get('status')})"
            )
            
            return analytics
            
        except Exception as e:
            logger.error(f"Brain analytics collection failed: {e}", exc_info=True)
            return {
                'status': 'error',
                'error': str(e),
                'health_score': 0
            }
    
    def _check_catalog_health(self) -> Dict[str, Any]:
        """
        Check Enhancement Catalog health and freshness.
        
        Returns:
            Dict with catalog health metrics
        """
        issues = []
        status = 'healthy'
        
        try:
            catalog = EnhancementCatalog()
            
            # Get catalog statistics
            stats = catalog.get_catalog_stats()
            
            # Check for staleness (> 7 days since any review)
            last_reviews = {}
            for review_type in ['documentation', 'epm_setup', 'alignment', 'upgrade', 'admin_help', 'healthcheck']:
                last_review = catalog.get_last_review_timestamp(review_type)
                if last_review:
                    days_since = (datetime.now() - last_review).days
                    last_reviews[review_type] = days_since
                    
                    if days_since > 7:
                        issues.append(f"{review_type} catalog review stale (>{days_since} days old)")
                        if status == 'healthy':
                            status = 'warning'
            
            # Check for catalog integrity
            if stats['total_features'] == 0:
                issues.append("Enhancement catalog is empty - run discovery")
                status = 'warning'
            
            # Check for discovery engine availability
            try:
                engine = EnhancementDiscoveryEngine()
                engine_status = 'available'
            except Exception as e:
                engine_status = f'unavailable: {e}'
                issues.append(f"Discovery engine not available: {e}")
                status = 'warning'
            
            return {
                'status': status,
                'total_features': stats['total_features'],
                'by_type': stats['by_type'],
                'by_status': stats['by_status'],
                'last_reviews': last_reviews,
                'discovery_engine': engine_status,
                'issues': issues,
            }
        
        except Exception as e:
            logger.error(f"Catalog health check failed: {e}")
            return {
                'status': 'critical',
                'error': str(e),
                'issues': [f"Catalog health check failed: {e}"],
            }
    
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
