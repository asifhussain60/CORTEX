"""
Resource Management Orchestrator - Monitor and optimize resource usage across orchestrators.

**Purpose:** Provide centralized resource monitoring, allocation policies, and optimization
**Features:**
- CPU usage monitoring and history tracking
- Memory usage tracking and leak detection
- Disk usage monitoring for multiple paths
- Resource allocation policies (priority-based)
- Performance bottleneck analysis
- Alert generation for threshold breaches
- Auto-scaling recommendations

**Integration:** Works with all orchestrators to optimize resource utilization

**Author:** Asif Hussain
**Feature:** Orchestrator Enhancement Plan v2.0 - Feature 16
"""

import psutil
import time
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from collections import defaultdict
from pathlib import Path

logger = logging.getLogger(__name__)


class ResourceManagementOrchestrator:
    """
    Resource management orchestrator for monitoring and optimizing system resources.
    
    **Responsibilities:**
    1. Monitor CPU, memory, and disk usage
    2. Track resource usage history
    3. Detect resource bottlenecks and leaks
    4. Allocate resources based on priority
    5. Generate alerts for threshold breaches
    6. Provide optimization recommendations
    7. Support monitoring sessions for orchestrators
    """
    
    def __init__(
        self,
        cpu_threshold: float = 80.0,
        memory_threshold: float = 75.0,
        disk_threshold: float = 85.0,
        monitoring_interval: float = 1.0
    ):
        """
        Initialize resource management orchestrator.
        
        Args:
            cpu_threshold: CPU usage threshold percentage (default: 80%)
            memory_threshold: Memory usage threshold percentage (default: 75%)
            disk_threshold: Disk usage threshold percentage (default: 85%)
            monitoring_interval: Monitoring interval in seconds (default: 1.0)
        """
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold
        self.disk_threshold = disk_threshold
        self.monitoring_interval = monitoring_interval
        self.monitoring_enabled = True
        
        # History tracking
        self.cpu_history: List[Dict[str, Any]] = []
        self.memory_history: List[Dict[str, Any]] = []
        self.disk_history: List[Dict[str, Any]] = []
        
        # Resource allocations
        self.allocations: Dict[str, Dict[str, Any]] = {}
        
        # Alert tracking
        self.alerts: List[Dict[str, Any]] = []
        self.active_alert_ids: set = set()
        
        # Monitoring sessions
        self.sessions: Dict[str, Dict[str, Any]] = {}
    
    # ========== CPU Monitoring ==========
    
    def get_cpu_usage(self) -> float:
        """
        Get current CPU usage percentage.
        
        Returns:
            CPU usage as percentage (0.0-100.0)
        """
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            return cpu_percent
        except Exception as e:
            logger.warning(f"Failed to get CPU usage: {e}")
            return 0.0
    
    def record_cpu_usage(self):
        """Record current CPU usage to history."""
        try:
            cpu_percent = self.get_cpu_usage()
            
            record = {
                "timestamp": datetime.now().isoformat(),
                "cpu_percent": cpu_percent
            }
            
            self.cpu_history.append(record)
            
            # Keep only last 1000 records
            if len(self.cpu_history) > 1000:
                self.cpu_history = self.cpu_history[-1000:]
        except Exception as e:
            logger.warning(f"Failed to record CPU usage: {e}")
    
    def get_cpu_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get CPU usage history.
        
        Args:
            limit: Optional limit on number of records (default: all)
        
        Returns:
            List of CPU usage records with timestamp and percent
        """
        if limit is None:
            return self.cpu_history.copy()
        return self.cpu_history[-limit:] if limit > 0 else []
    
    def check_cpu_threshold(self) -> Optional[Dict[str, Any]]:
        """
        Check if CPU usage exceeds threshold.
        
        Returns:
            Alert dictionary if threshold exceeded, None otherwise
        """
        cpu_usage = self.get_cpu_usage()
        
        if cpu_usage > self.cpu_threshold:
            severity = "critical" if cpu_usage > 95.0 else "warning"
            
            return self.create_alert(
                resource="cpu",
                current_value=cpu_usage,
                threshold=self.cpu_threshold,
                severity=severity
            )
        
        return None
    
    # ========== Memory Tracking ==========
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """
        Get current memory usage statistics.
        
        Returns:
            Dictionary with total, available, used, percent
        """
        try:
            mem = psutil.virtual_memory()
            
            return {
                "total": mem.total,
                "available": mem.available,
                "used": mem.used,
                "percent": mem.percent
            }
        except Exception as e:
            logger.warning(f"Failed to get memory usage: {e}")
            return {"total": 0, "available": 0, "used": 0, "percent": 0.0}
    
    def detect_memory_leak(self, readings: List[Dict[str, Any]]) -> bool:
        """
        Detect potential memory leak from readings trend.
        
        Args:
            readings: List of memory readings with 'percent' field
        
        Returns:
            True if leak detected (sustained increase), False otherwise
        """
        if len(readings) < 3:
            return False
        
        try:
            # Check for sustained increase (each reading higher than previous)
            for i in range(1, len(readings)):
                if readings[i]["percent"] <= readings[i-1]["percent"]:
                    return False
            
            # Check if increase is significant (>10% over period)
            first = readings[0]["percent"]
            last = readings[-1]["percent"]
            
            if last - first > 10.0:
                return True
            
            return True  # Sustained increase detected
        except Exception:
            return False
    
    def check_memory_threshold(self) -> Optional[Dict[str, Any]]:
        """
        Check if memory usage exceeds threshold.
        
        Returns:
            Alert dictionary if threshold exceeded, None otherwise
        """
        memory_info = self.get_memory_usage()
        memory_percent = memory_info["percent"]
        
        if memory_percent > self.memory_threshold:
            severity = "critical" if memory_percent > 90.0 else "warning"
            
            return self.create_alert(
                resource="memory",
                current_value=memory_percent,
                threshold=self.memory_threshold,
                severity=severity
            )
        
        return None
    
    # ========== Disk Usage Monitoring ==========
    
    def get_disk_usage(self, path: str = "/") -> Dict[str, Any]:
        """
        Get disk usage for specific path.
        
        Args:
            path: Path to check (default: root)
        
        Returns:
            Dictionary with total, used, free, percent
        """
        try:
            disk = psutil.disk_usage(path)
            
            return {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": disk.percent
            }
        except Exception as e:
            logger.warning(f"Failed to get disk usage for {path}: {e}")
            return {"total": 0, "used": 0, "free": 0, "percent": 0.0}
    
    def get_disk_usage_multiple(self, paths: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Get disk usage for multiple paths.
        
        Args:
            paths: List of paths to check
        
        Returns:
            Dictionary mapping path to disk usage info
        """
        results = {}
        
        for path in paths:
            if Path(path).exists():
                results[path] = self.get_disk_usage(path)
        
        return results
    
    def check_disk_threshold(self, path: str = "/") -> Optional[Dict[str, Any]]:
        """
        Check if disk usage exceeds threshold.
        
        Args:
            path: Path to check
        
        Returns:
            Alert dictionary if threshold exceeded, None otherwise
        """
        disk_info = self.get_disk_usage(path)
        disk_percent = disk_info["percent"]
        
        if disk_percent > self.disk_threshold:
            severity = "critical" if disk_percent > 95.0 else "warning"
            
            alert = self.create_alert(
                resource="disk",
                current_value=disk_percent,
                threshold=self.disk_threshold,
                severity=severity
            )
            alert["path"] = path
            
            return alert
        
        return None
    
    # ========== Resource Allocation ==========
    
    def allocate_resources(
        self,
        orchestrator_name: str,
        cpu_weight: Optional[float] = None,
        memory_weight: Optional[float] = None,
        priority: str = "medium"
    ) -> Dict[str, Any]:
        """
        Allocate resources to orchestrator based on priority.
        
        Args:
            orchestrator_name: Name of orchestrator
            cpu_weight: Optional CPU weight (0.0-1.0)
            memory_weight: Optional memory weight (0.0-1.0)
            priority: Priority level ("low", "medium", "high")
        
        Returns:
            Allocation details
        """
        # Determine weights based on priority
        priority_weights = {
            "low": {"cpu": 0.1, "memory": 0.1},
            "medium": {"cpu": 0.3, "memory": 0.2},
            "high": {"cpu": 0.5, "memory": 0.4}
        }
        
        weights = priority_weights.get(priority, priority_weights["medium"])
        
        if cpu_weight is None:
            cpu_weight = weights["cpu"]
        if memory_weight is None:
            memory_weight = weights["memory"]
        
        allocation = {
            "orchestrator_name": orchestrator_name,
            "cpu_allocation": cpu_weight,
            "memory_allocation": memory_weight,
            "priority": priority,
            "allocated_at": datetime.now().isoformat()
        }
        
        self.allocations[orchestrator_name] = allocation
        
        logger.info(f"Allocated resources to {orchestrator_name}: CPU={cpu_weight}, Memory={memory_weight}, Priority={priority}")
        
        return allocation
    
    def deallocate_resources(self, orchestrator_name: str) -> bool:
        """
        Deallocate resources for orchestrator.
        
        Args:
            orchestrator_name: Name of orchestrator
        
        Returns:
            True if deallocated, False if not found
        """
        if orchestrator_name in self.allocations:
            del self.allocations[orchestrator_name]
            logger.info(f"Deallocated resources for {orchestrator_name}")
            return True
        
        return False
    
    def get_active_allocations(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all active resource allocations.
        
        Returns:
            Dictionary of active allocations
        """
        return self.allocations.copy()
    
    # ========== Performance Optimization ==========
    
    def analyze_bottlenecks(self) -> List[Dict[str, Any]]:
        """
        Analyze system for resource bottlenecks.
        
        Returns:
            List of detected bottlenecks
        """
        bottlenecks = []
        
        # Check CPU
        cpu_usage = self.get_cpu_usage()
        if cpu_usage > self.cpu_threshold:
            bottlenecks.append({
                "resource": "cpu",
                "current_value": cpu_usage,
                "threshold": self.cpu_threshold,
                "severity": "critical" if cpu_usage > 95.0 else "warning"
            })
        
        # Check memory
        memory_info = self.get_memory_usage()
        if memory_info["percent"] > self.memory_threshold:
            bottlenecks.append({
                "resource": "memory",
                "current_value": memory_info["percent"],
                "threshold": self.memory_threshold,
                "severity": "critical" if memory_info["percent"] > 90.0 else "warning"
            })
        
        # Check disk
        disk_info = self.get_disk_usage("/")
        if disk_info["percent"] > self.disk_threshold:
            bottlenecks.append({
                "resource": "disk",
                "current_value": disk_info["percent"],
                "threshold": self.disk_threshold,
                "severity": "critical" if disk_info["percent"] > 95.0 else "warning"
            })
        
        return bottlenecks
    
    def generate_recommendations(self, bottlenecks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate optimization recommendations for bottlenecks.
        
        Args:
            bottlenecks: List of detected bottlenecks
        
        Returns:
            List of recommendations
        """
        recommendations = []
        
        for bottleneck in bottlenecks:
            resource = bottleneck["resource"]
            
            if resource == "cpu":
                recommendations.append({
                    "resource": "cpu",
                    "action": "Reduce concurrent orchestrator executions",
                    "details": "Consider implementing orchestrator queuing or rate limiting"
                })
                recommendations.append({
                    "resource": "cpu",
                    "action": "Optimize CPU-intensive operations",
                    "details": "Profile code to identify CPU hotspots and optimize algorithms"
                })
            
            elif resource == "memory":
                recommendations.append({
                    "resource": "memory",
                    "action": "Investigate memory leaks",
                    "details": "Use memory profilers to detect and fix memory leaks"
                })
                recommendations.append({
                    "resource": "memory",
                    "action": "Implement caching strategies",
                    "details": "Add LRU caching with size limits to prevent unbounded growth"
                })
            
            elif resource == "disk":
                recommendations.append({
                    "resource": "disk",
                    "action": "Clean up old logs and temp files",
                    "details": "Implement log rotation and automated cleanup policies"
                })
                recommendations.append({
                    "resource": "disk",
                    "action": "Archive historical data",
                    "details": "Move old metrics and reports to compressed archives"
                })
        
        return recommendations
    
    def should_auto_scale(self, load_history: List[Dict[str, Any]]) -> bool:
        """
        Determine if auto-scaling is recommended based on load history.
        
        Args:
            load_history: List of load readings with cpu_percent and memory_percent
        
        Returns:
            True if auto-scaling recommended, False otherwise
        """
        if len(load_history) < 3:
            return False
        
        try:
            # Check if sustained high load (all readings above 80%)
            cpu_high = all(reading.get("cpu_percent", 0) > 80.0 for reading in load_history)
            memory_high = all(reading.get("memory_percent", 0) > 75.0 for reading in load_history)
            
            return cpu_high or memory_high
        except Exception:
            return False
    
    # ========== Monitoring Sessions ==========
    
    def start_monitoring_session(
        self,
        orchestrator_name: str,
        interval: float = 1.0
    ) -> str:
        """
        Start a monitoring session for orchestrator.
        
        Args:
            orchestrator_name: Name of orchestrator to monitor
            interval: Monitoring interval in seconds
        
        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())
        
        session = {
            "session_id": session_id,
            "orchestrator_name": orchestrator_name,
            "interval": interval,
            "start_time": datetime.now(),
            "cpu_readings": [],
            "memory_readings": [],
            "disk_readings": []
        }
        
        self.sessions[session_id] = session
        
        logger.info(f"Started monitoring session {session_id} for {orchestrator_name}")
        
        return session_id
    
    def stop_monitoring_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Stop monitoring session and generate report.
        
        Args:
            session_id: Session ID to stop
        
        Returns:
            Session report with statistics
        """
        if session_id not in self.sessions:
            return None
        
        session = self.sessions.pop(session_id)
        end_time = datetime.now()
        
        # Calculate statistics
        cpu_readings = session.get("cpu_readings", [])
        memory_readings = session.get("memory_readings", [])
        
        report = {
            "session_id": session_id,
            "orchestrator_name": session["orchestrator_name"],
            "start_time": session["start_time"].isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": (end_time - session["start_time"]).total_seconds(),
            "cpu_stats": {
                "avg": sum(cpu_readings) / len(cpu_readings) if cpu_readings else 0.0,
                "max": max(cpu_readings) if cpu_readings else 0.0,
                "min": min(cpu_readings) if cpu_readings else 0.0,
                "readings_count": len(cpu_readings)
            },
            "memory_stats": {
                "avg": sum(memory_readings) / len(memory_readings) if memory_readings else 0.0,
                "max": max(memory_readings) if memory_readings else 0.0,
                "min": min(memory_readings) if memory_readings else 0.0,
                "readings_count": len(memory_readings)
            }
        }
        
        logger.info(f"Stopped monitoring session {session_id}")
        
        return report
    
    def get_resource_summary(self) -> Dict[str, Any]:
        """
        Get overall resource summary.
        
        Returns:
            Summary of current resource state
        """
        return {
            "cpu": self.get_cpu_usage(),
            "memory": self.get_memory_usage(),
            "disk": self.get_disk_usage("/"),
            "active_allocations": len(self.allocations),
            "alerts": len(self.get_active_alerts()),
            "timestamp": datetime.now().isoformat()
        }
    
    # ========== Alert Management ==========
    
    def create_alert(
        self,
        resource: str,
        current_value: float,
        threshold: float,
        severity: str
    ) -> Dict[str, Any]:
        """
        Create resource alert.
        
        Args:
            resource: Resource type (cpu, memory, disk)
            current_value: Current resource value
            threshold: Threshold value
            severity: Alert severity (warning, critical)
        
        Returns:
            Alert dictionary
        """
        alert_id = str(uuid.uuid4())
        
        alert = {
            "alert_id": alert_id,
            "resource": resource,
            "current_value": current_value,
            "threshold": threshold,
            "severity": severity,
            "timestamp": datetime.now().isoformat(),
            "message": f"{resource.upper()} usage ({current_value:.1f}%) exceeds threshold ({threshold:.1f}%)"
        }
        
        self.alerts.append(alert)
        self.active_alert_ids.add(alert_id)
        
        logger.warning(f"Alert created: {alert['message']}")
        
        return alert
    
    def get_alert_history(self) -> List[Dict[str, Any]]:
        """
        Get alert history.
        
        Returns:
            List of all alerts
        """
        return self.alerts.copy()
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """
        Get active (uncleared) alerts.
        
        Returns:
            List of active alerts
        """
        return [alert for alert in self.alerts if alert["alert_id"] in self.active_alert_ids]
    
    def clear_alert(self, alert_id: str) -> bool:
        """
        Clear (resolve) an alert.
        
        Args:
            alert_id: Alert ID to clear
        
        Returns:
            True if cleared, False if not found
        """
        if alert_id in self.active_alert_ids:
            self.active_alert_ids.remove(alert_id)
            logger.info(f"Cleared alert {alert_id}")
            return True
        
        return False
    
    # ========== Configuration ==========
    
    def configure_thresholds(
        self,
        cpu_threshold: Optional[float] = None,
        memory_threshold: Optional[float] = None,
        disk_threshold: Optional[float] = None
    ):
        """
        Configure resource thresholds.
        
        Args:
            cpu_threshold: CPU threshold percentage
            memory_threshold: Memory threshold percentage
            disk_threshold: Disk threshold percentage
        """
        if cpu_threshold is not None:
            self.cpu_threshold = cpu_threshold
        if memory_threshold is not None:
            self.memory_threshold = memory_threshold
        if disk_threshold is not None:
            self.disk_threshold = disk_threshold
        
        logger.info(f"Thresholds configured: CPU={self.cpu_threshold}, Memory={self.memory_threshold}, Disk={self.disk_threshold}")
    
    def configure_monitoring(self, interval: float, enabled: bool = True):
        """
        Configure monitoring settings.
        
        Args:
            interval: Monitoring interval in seconds
            enabled: Whether monitoring is enabled
        """
        self.monitoring_interval = interval
        self.monitoring_enabled = enabled
        
        logger.info(f"Monitoring configured: interval={interval}s, enabled={enabled}")
    
    def export_configuration(self) -> Dict[str, Any]:
        """
        Export current configuration.
        
        Returns:
            Configuration dictionary
        """
        return {
            "cpu_threshold": self.cpu_threshold,
            "memory_threshold": self.memory_threshold,
            "disk_threshold": self.disk_threshold,
            "monitoring_interval": self.monitoring_interval,
            "monitoring_enabled": self.monitoring_enabled
        }
