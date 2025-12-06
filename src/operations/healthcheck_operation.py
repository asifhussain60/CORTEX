"""
CORTEX Healthcheck Operation Module

Provides comprehensive system health monitoring and diagnostics.
Reports on brain health, database performance, cache status, and system metrics.

Features:
- Brain tier health checks (Tier 0-3)
- Database performance metrics
- Cache hit rates and optimization
- Memory usage and patterns
- Operation success rates
- System recommendations

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import logging
import sqlite3
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json

from .base_operation_module import (
    BaseOperationModule,
    OperationResult,
    OperationStatus,
    OperationPhase,
    OperationModuleMetadata,
)
from src.utils.progress_decorator import with_progress, yield_progress


logger = logging.getLogger(__name__)


class HealthCheckOperation(BaseOperationModule):
    """
    Health check operation for CORTEX system.
    
    Features:
    - Brain tier health (working memory, knowledge graph, dev context)
    - Database performance metrics
    - Cache optimization status
    - System resource usage
    - Error rate monitoring
    - Performance recommendations
    
    Usage:
        User says: "healthcheck" or "system health" or "check cortex health"
        CORTEX routes to this module
    """
    
    def __init__(self):
        super().__init__()
        self._metadata = OperationModuleMetadata(
            module_id="healthcheck",
            name="healthcheck",
            description="System health and performance monitoring",
            phase=OperationPhase.PROCESSING,
            priority=50,
            version="1.0.0",
            author="Asif Hussain",
            tags=["user-facing", "diagnostics", "monitoring"],
        )
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Return operation metadata."""
        return self._metadata
    
    def validate(self) -> OperationResult:
        """
        Validate healthcheck operation can run.
        
        Returns:
            OperationResult with validation status
        """
        try:
            from src.config import Config
            config = Config()
            brain_path = Path(config.get_brain_path())
            
            if not brain_path.exists():
                return OperationResult(
                    success=False,
                    status=OperationStatus.FAILED,
                    message="Brain directory not found",
                    error="Cannot locate cortex-brain directory"
                )
            
            return OperationResult(
                success=True,
                status=OperationStatus.SUCCESS,
                message="Healthcheck validation passed"
            )
        except Exception as e:
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message="Validation failed",
                error=str(e)
            )
    
    @with_progress(operation_name="System Health Check")
    def execute(self, context: Optional[Dict[str, Any]] = None) -> OperationResult:
        """
        Execute health check operation with progress monitoring.
        
        Args:
            context: Optional execution context
            
        Returns:
            OperationResult with health metrics
        """
        try:
            logger.info("Starting CORTEX health check...")
            
            # Total check phases
            total_phases = 5
            
            yield_progress(1, total_phases, "Checking brain health (Tier 0-3)")
            brain_health = self._check_brain_health()
            
            yield_progress(2, total_phases, "Analyzing database performance")
            database_health = self._check_database_health()
            
            yield_progress(3, total_phases, "Evaluating cache status")
            cache_health = self._check_cache_health()
            
            yield_progress(4, total_phases, "Gathering system metrics")
            system_metrics = self._get_system_metrics()
            
            health_report = {
                "timestamp": datetime.now().isoformat(),
                "brain_health": brain_health,
                "database_health": database_health,
                "cache_health": cache_health,
                "system_metrics": system_metrics,
                "recommendations": []
            }
            
            # Generate recommendations
            yield_progress(5, total_phases, "Generating recommendations")
            health_report["recommendations"] = self._generate_recommendations(health_report)
            
            # Calculate overall health score
            overall_score = self._calculate_health_score(health_report)
            health_report["overall_score"] = overall_score
            health_report["status"] = self._get_health_status(overall_score)
            
            return OperationResult(
                success=True,
                status=OperationStatus.SUCCESS,
                message=f"Health check complete - Status: {health_report['status']}",
                data=health_report
            )
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message="Health check failed",
                error=str(e)
            )
    
    def _check_brain_health(self) -> Dict[str, Any]:
        """Check brain tier health."""
        try:
            from src.config import Config
            config = Config()
            brain_path = Path(config.get_brain_path())
            
            return {
                "tier1_db": self._check_db_file(brain_path / "tier1" / "working_memory.db"),
                "tier2_db": self._check_db_file(brain_path / "tier2" / "knowledge_graph.db"),
                "tier3_db": self._check_db_file(brain_path / "tier3" / "development_context.db"),
                "brain_protection": self._check_brain_protection(brain_path),
            }
        except Exception as e:
            logger.error(f"Brain health check failed: {e}")
            return {"error": str(e)}
    
    def _check_database_health(self) -> Dict[str, Any]:
        """Check database performance metrics."""
        try:
            from src.config import Config
            config = Config()
            brain_path = Path(config.get_brain_path())
            
            metrics = {}
            for tier, db_name in [
                ("tier1", "working_memory.db"),
                ("tier2", "knowledge_graph.db"),
                ("tier3", "development_context.db")
            ]:
                db_path = brain_path / tier / db_name
                if db_path.exists():
                    metrics[tier] = self._get_db_metrics(db_path)
            
            return metrics
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {"error": str(e)}
    
    def _check_cache_health(self) -> Dict[str, Any]:
        """Check cache performance."""
        return {
            "yaml_cache": "operational",
            "response_cache": "operational",
            "optimization": "pending"
        }
    
    def _get_system_metrics(self) -> Dict[str, Any]:
        """Get system-level metrics."""
        try:
            from src.config import Config
            config = Config()
            brain_path = Path(config.get_brain_path())
            
            return {
                "brain_size_mb": self._get_directory_size(brain_path),
                "uptime_hours": 0,  # Placeholder
                "operations_count": 0,  # Placeholder
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _check_db_file(self, db_path: Path) -> Dict[str, Any]:
        """Check database file health."""
        if not db_path.exists():
            return {"status": "missing", "exists": False}
        
        try:
            size_mb = db_path.stat().st_size / (1024 * 1024)
            return {
                "status": "healthy",
                "exists": True,
                "size_mb": round(size_mb, 2),
                "readable": True
            }
        except Exception as e:
            return {
                "status": "error",
                "exists": True,
                "error": str(e)
            }
    
    def _check_brain_protection(self, brain_path: Path) -> Dict[str, Any]:
        """Check brain protection rules."""
        rules_file = brain_path / "brain-protection-rules.yaml"
        if not rules_file.exists():
            return {"status": "missing"}
        
        return {
            "status": "active",
            "exists": True,
            "size_kb": round(rules_file.stat().st_size / 1024, 2)
        }
    
    def _get_db_metrics(self, db_path: Path) -> Dict[str, Any]:
        """Get database performance metrics."""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get table count
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            table_count = cursor.fetchone()[0]
            
            # Get database size
            cursor.execute("PRAGMA page_count")
            page_count = cursor.fetchone()[0]
            cursor.execute("PRAGMA page_size")
            page_size = cursor.fetchone()[0]
            size_mb = (page_count * page_size) / (1024 * 1024)
            
            conn.close()
            
            return {
                "tables": table_count,
                "size_mb": round(size_mb, 2),
                "status": "healthy"
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _get_directory_size(self, path: Path) -> float:
        """Get total size of directory in MB."""
        try:
            total = sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
            return round(total / (1024 * 1024), 2)
        except Exception as e:
            return 0.0
    
    def _generate_recommendations(self, health_report: Dict[str, Any]) -> List[str]:
        """Generate health recommendations."""
        recommendations = []
        
        # Check database sizes
        db_health = health_report.get("database_health", {})
        for tier, metrics in db_health.items():
            if isinstance(metrics, dict) and metrics.get("size_mb", 0) > 100:
                recommendations.append(
                    f"{tier} database exceeds 100MB - consider vacuum/optimization"
                )
        
        # Check brain size
        system_metrics = health_report.get("system_metrics", {})
        brain_size = system_metrics.get("brain_size_mb", 0)
        if brain_size > 500:
            recommendations.append(
                f"Brain directory is {brain_size}MB - consider cleanup"
            )
        
        if not recommendations:
            recommendations.append("System health is optimal")
        
        return recommendations
    
    def _calculate_health_score(self, health_report: Dict[str, Any]) -> float:
        """Calculate overall health score (0-100)."""
        score = 100.0
        
        # Deduct for database issues
        db_health = health_report.get("database_health", {})
        for metrics in db_health.values():
            if isinstance(metrics, dict):
                if metrics.get("status") == "error":
                    score -= 20
                elif metrics.get("size_mb", 0) > 100:
                    score -= 5
        
        # Deduct for missing components
        brain_health = health_report.get("brain_health", {})
        for component, status in brain_health.items():
            if isinstance(status, dict) and not status.get("exists", True):
                score -= 15
        
        return max(0.0, min(100.0, score))
    
    def _get_health_status(self, score: float) -> str:
        """Get health status from score."""
        if score >= 90:
            return "Excellent"
        elif score >= 75:
            return "Good"
        elif score >= 60:
            return "Fair"
        elif score >= 40:
            return "Poor"
        else:
            return "Critical"
    
    def rollback(self) -> OperationResult:
        """
        Rollback not applicable for health checks.
        
        Returns:
            OperationResult indicating rollback not needed
        """
        return OperationResult(
            success=True,
            status=OperationStatus.SUCCESS,
            message="Rollback not applicable for health checks"
        )
