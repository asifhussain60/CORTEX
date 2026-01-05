"""
Health Check System for CORTEX Audit Logger.

Provides HTTP endpoints and programmatic API for monitoring:
- System health status
- Orchestrator health metrics
- Self-healing effectiveness
- Performance statistics
- Log storage metrics

Usage:
    from src.logging.health_check import HealthCheckServer
    
    server = HealthCheckServer(audit_logger, self_healing_engine)
    await server.start(host="0.0.0.0", port=8080)
    
    # Access endpoints:
    # GET /health - Overall system health
    # GET /health/orchestrator/{name} - Specific orchestrator health
    # GET /metrics - Prometheus-style metrics
    # GET /stats - Detailed statistics
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from pathlib import Path
from collections import defaultdict, Counter
import time

from src.logging.audit_logger import AuditLogger
from src.logging.self_healing_engine import SelfHealingEngine


class HealthCheckSystem:
    """
    Comprehensive health check and metrics system.
    
    Monitors:
    - Orchestrator availability and performance
    - Error rates and patterns
    - Self-healing effectiveness
    - Log storage and rotation
    - System resource usage
    """
    
    def __init__(
        self,
        audit_logger: AuditLogger,
        self_healing_engine: Optional[SelfHealingEngine] = None
    ):
        """
        Initialize health check system.
        
        Args:
            audit_logger: AuditLogger instance for metrics
            self_healing_engine: Optional SelfHealingEngine for self-healing metrics
        """
        self.audit_logger = audit_logger
        self.self_healing_engine = self_healing_engine
        self._start_time = time.time()
    
    async def get_system_health(self) -> Dict[str, Any]:
        """
        Get overall system health status.
        
        Returns:
            Dictionary with system health information
        """
        uptime_seconds = time.time() - self._start_time
        
        health_status = {
            "status": "healthy",  # healthy, degraded, unhealthy
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": uptime_seconds,
            "components": {
                "audit_logger": await self._check_audit_logger(),
                "self_healing_engine": await self._check_self_healing(),
                "log_storage": await self._check_log_storage()
            }
        }
        
        # Determine overall status
        component_statuses = [c["status"] for c in health_status["components"].values()]
        if any(s == "unhealthy" for s in component_statuses):
            health_status["status"] = "unhealthy"
        elif any(s == "degraded" for s in component_statuses):
            health_status["status"] = "degraded"
        
        return health_status
    
    async def _check_audit_logger(self) -> Dict[str, Any]:
        """Check audit logger health."""
        try:
            error_count = self.audit_logger.error_count
            
            return {
                "status": "healthy" if error_count == 0 else "degraded",
                "error_count": error_count,
                "buffer_size": self.audit_logger.buffer_size,
                "async_enabled": self.audit_logger.async_enabled
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def _check_self_healing(self) -> Dict[str, Any]:
        """Check self-healing engine health."""
        if not self.self_healing_engine:
            return {
                "status": "disabled",
                "message": "Self-healing engine not configured"
            }
        
        try:
            metrics = await self.self_healing_engine.get_metrics()
            
            return {
                "status": "healthy",
                "enabled": self.self_healing_engine.auto_recovery_enabled,
                "recovery_attempts": metrics.get("total_attempts", 0),
                "success_rate": metrics.get("success_rate", 0.0)
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def _check_log_storage(self) -> Dict[str, Any]:
        """Check log storage health."""
        try:
            log_dir = self.audit_logger.log_dir / "audit"
            
            if not log_dir.exists():
                return {
                    "status": "unhealthy",
                    "error": "Log directory does not exist"
                }
            
            # Calculate storage usage
            total_size = sum(f.stat().st_size for f in log_dir.rglob("*") if f.is_file())
            file_count = sum(1 for f in log_dir.rglob("*") if f.is_file())
            
            return {
                "status": "healthy",
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "file_count": file_count,
                "log_directory": str(log_dir)
            }
        except Exception as e:
            return {
                "status": "degraded",
                "error": str(e)
            }
    
    async def get_orchestrator_health(self, orchestrator_name: str) -> Dict[str, Any]:
        """
        Get health metrics for specific orchestrator.
        
        Args:
            orchestrator_name: Name of orchestrator
        
        Returns:
            Orchestrator health dictionary
        """
        # Analyze recent events from audit logger cache
        events = self.audit_logger._event_cache
        
        # Filter events for this orchestrator
        orch_events = [e for e in events if e.get("orchestrator") == orchestrator_name]
        
        if not orch_events:
            return {
                "orchestrator": orchestrator_name,
                "status": "unknown",
                "message": "No recent activity"
            }
        
        # Calculate metrics
        error_events = [e for e in orch_events if e.get("level") == "ERROR"]
        total_events = len(orch_events)
        error_rate = len(error_events) / total_events if total_events > 0 else 0.0
        
        # Calculate average response time
        completed_events = [
            e for e in orch_events 
            if "completed" in e.get("event", "") and "duration_ms" in e.get("data", {})
        ]
        avg_response_time = 0.0
        if completed_events:
            durations = [e["data"]["duration_ms"] for e in completed_events]
            avg_response_time = sum(durations) / len(durations)
        
        # Determine health status
        if error_rate > 0.5:
            status = "unhealthy"
        elif error_rate > 0.1:
            status = "degraded"
        else:
            status = "healthy"
        
        return {
            "orchestrator": orchestrator_name,
            "status": status,
            "metrics": {
                "total_events": total_events,
                "error_events": len(error_events),
                "error_rate": round(error_rate, 3),
                "avg_response_time_ms": round(avg_response_time, 2),
                "last_activity": orch_events[-1].get("timestamp") if orch_events else None
            }
        }
    
    async def get_metrics(self) -> Dict[str, Any]:
        """
        Get Prometheus-style metrics.
        
        Returns:
            Dictionary of metrics
        """
        events = self.audit_logger._event_cache
        
        # Event counts by orchestrator
        event_counts = Counter(e.get("orchestrator") for e in events)
        
        # Error counts by orchestrator
        error_counts = Counter(
            e.get("orchestrator") for e in events if e.get("level") == "ERROR"
        )
        
        # Performance metrics
        completed_events = [
            e for e in events 
            if "completed" in e.get("event", "") and "duration_ms" in e.get("data", {})
        ]
        
        performance_by_orch = defaultdict(list)
        for event in completed_events:
            orch = event.get("orchestrator")
            duration = event.get("data", {}).get("duration_ms", 0)
            performance_by_orch[orch].append(duration)
        
        # Self-healing metrics
        self_healing_metrics = {}
        if self.self_healing_engine:
            self_healing_metrics = await self.self_healing_engine.get_metrics()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": time.time() - self._start_time,
            "event_counts": dict(event_counts),
            "error_counts": dict(error_counts),
            "performance_metrics": {
                orch: {
                    "avg_duration_ms": round(sum(durations) / len(durations), 2),
                    "min_duration_ms": round(min(durations), 2),
                    "max_duration_ms": round(max(durations), 2),
                    "total_operations": len(durations)
                }
                for orch, durations in performance_by_orch.items()
            },
            "self_healing": self_healing_metrics
        }
    
    async def get_statistics(self) -> Dict[str, Any]:
        """
        Get detailed statistics.
        
        Returns:
            Comprehensive statistics dictionary
        """
        events = self.audit_logger._event_cache
        
        # Time-based analysis
        now = datetime.now()
        last_hour_events = [
            e for e in events
            if (now - datetime.fromisoformat(e.get("timestamp", now.isoformat()))).total_seconds() < 3600
        ]
        last_day_events = [
            e for e in events
            if (now - datetime.fromisoformat(e.get("timestamp", now.isoformat()))).total_seconds() < 86400
        ]
        
        return {
            "timestamp": now.isoformat(),
            "total_events": len(events),
            "last_hour": {
                "total_events": len(last_hour_events),
                "error_events": len([e for e in last_hour_events if e.get("level") == "ERROR"]),
                "unique_orchestrators": len(set(e.get("orchestrator") for e in last_hour_events))
            },
            "last_24_hours": {
                "total_events": len(last_day_events),
                "error_events": len([e for e in last_day_events if e.get("level") == "ERROR"]),
                "unique_orchestrators": len(set(e.get("orchestrator") for e in last_day_events))
            },
            "event_types": dict(Counter(e.get("event") for e in events)),
            "log_levels": dict(Counter(e.get("level") for e in events)),
            "system_info": {
                "uptime_seconds": time.time() - self._start_time,
                "cache_size": len(events),
                "cache_max_size": self.audit_logger._max_cache_size
            }
        }
    
    def to_prometheus_format(self, metrics: Dict[str, Any]) -> str:
        """
        Convert metrics to Prometheus exposition format.
        
        Args:
            metrics: Metrics dictionary
        
        Returns:
            Prometheus-formatted metrics string
        """
        lines = []
        
        # System uptime
        lines.append(f"# HELP cortex_uptime_seconds System uptime in seconds")
        lines.append(f"# TYPE cortex_uptime_seconds gauge")
        lines.append(f'cortex_uptime_seconds {metrics.get("uptime_seconds", 0)}')
        
        # Event counts
        lines.append(f"# HELP cortex_events_total Total events by orchestrator")
        lines.append(f"# TYPE cortex_events_total counter")
        for orch, count in metrics.get("event_counts", {}).items():
            lines.append(f'cortex_events_total{{orchestrator="{orch}"}} {count}')
        
        # Error counts
        lines.append(f"# HELP cortex_errors_total Total errors by orchestrator")
        lines.append(f"# TYPE cortex_errors_total counter")
        for orch, count in metrics.get("error_counts", {}).items():
            lines.append(f'cortex_errors_total{{orchestrator="{orch}"}} {count}')
        
        # Performance metrics
        for orch, perf in metrics.get("performance_metrics", {}).items():
            lines.append(f'cortex_operation_duration_ms{{orchestrator="{orch}",stat="avg"}} {perf["avg_duration_ms"]}')
            lines.append(f'cortex_operation_duration_ms{{orchestrator="{orch}",stat="min"}} {perf["min_duration_ms"]}')
            lines.append(f'cortex_operation_duration_ms{{orchestrator="{orch}",stat="max"}} {perf["max_duration_ms"]}')
        
        # Self-healing metrics
        sh_metrics = metrics.get("self_healing", {})
        if sh_metrics:
            lines.append(f"# HELP cortex_recovery_attempts_total Total recovery attempts")
            lines.append(f"# TYPE cortex_recovery_attempts_total counter")
            lines.append(f'cortex_recovery_attempts_total {sh_metrics.get("total_attempts", 0)}')
            
            lines.append(f"# HELP cortex_recovery_success_rate Recovery success rate")
            lines.append(f"# TYPE cortex_recovery_success_rate gauge")
            lines.append(f'cortex_recovery_success_rate {sh_metrics.get("success_rate", 0)}')
        
        return "\n".join(lines) + "\n"


# Simple HTTP server for health checks (optional, for production)
try:
    from aiohttp import web
    
    class HealthCheckServer:
        """
        HTTP server for health check endpoints.
        
        Provides REST API for health monitoring.
        """
        
        def __init__(
            self,
            health_check_system: HealthCheckSystem
        ):
            """
            Initialize health check server.
            
            Args:
                health_check_system: HealthCheckSystem instance
            """
            self.health_system = health_check_system
            self.app = web.Application()
            self._setup_routes()
        
        def _setup_routes(self):
            """Setup HTTP routes."""
            self.app.router.add_get("/health", self.health_endpoint)
            self.app.router.add_get("/health/orchestrator/{name}", self.orchestrator_health_endpoint)
            self.app.router.add_get("/metrics", self.metrics_endpoint)
            self.app.router.add_get("/metrics/prometheus", self.prometheus_endpoint)
            self.app.router.add_get("/stats", self.stats_endpoint)
        
        async def health_endpoint(self, request):
            """GET /health - System health check."""
            health = await self.health_system.get_system_health()
            return web.json_response(health)
        
        async def orchestrator_health_endpoint(self, request):
            """GET /health/orchestrator/{name} - Orchestrator health."""
            name = request.match_info["name"]
            health = await self.health_system.get_orchestrator_health(name)
            return web.json_response(health)
        
        async def metrics_endpoint(self, request):
            """GET /metrics - System metrics."""
            metrics = await self.health_system.get_metrics()
            return web.json_response(metrics)
        
        async def prometheus_endpoint(self, request):
            """GET /metrics/prometheus - Prometheus format."""
            metrics = await self.health_system.get_metrics()
            prom_format = self.health_system.to_prometheus_format(metrics)
            return web.Response(text=prom_format, content_type="text/plain")
        
        async def stats_endpoint(self, request):
            """GET /stats - Detailed statistics."""
            stats = await self.health_system.get_statistics()
            return web.json_response(stats)
        
        async def start(self, host: str = "0.0.0.0", port: int = 8080):
            """
            Start health check server.
            
            Args:
                host: Host to bind to
                port: Port to listen on
            """
            runner = web.AppRunner(self.app)
            await runner.setup()
            site = web.TCPSite(runner, host, port)
            await site.start()
            print(f"Health check server started on http://{host}:{port}")

except ImportError:
    # aiohttp not available, skip HTTP server
    class HealthCheckServer:
        """Placeholder when aiohttp not installed."""
        def __init__(self, *args, **kwargs):
            raise ImportError("aiohttp required for HealthCheckServer. Install with: pip install aiohttp")
