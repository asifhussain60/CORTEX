"""
CORTEX 3.0 Status Checker
=========================

Comprehensive status checking system for monitoring service dependencies,
external APIs, and system components with detailed status reporting.
"""

import time
import threading
import asyncio
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
import json
import sqlite3

# Optional imports for web functionality
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
import socket
import subprocess
import psutil


logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """Service status levels."""
    OPERATIONAL = "operational"
    DEGRADED = "degraded"
    PARTIAL_OUTAGE = "partial_outage"
    MAJOR_OUTAGE = "major_outage"
    MAINTENANCE = "maintenance"
    UNKNOWN = "unknown"


class CheckType(Enum):
    """Types of status checks."""
    HTTP_ENDPOINT = "http_endpoint"
    TCP_PORT = "tcp_port"
    DATABASE = "database"
    SERVICE_PROCESS = "service_process"
    DISK_SPACE = "disk_space"
    CUSTOM_COMMAND = "custom_command"
    CUSTOM_FUNCTION = "custom_function"


@dataclass
class StatusCheckConfig:
    """Configuration for a status check."""
    name: str
    check_type: CheckType
    enabled: bool = True
    interval_seconds: float = 60.0
    timeout_seconds: float = 30.0
    retry_count: int = 2
    
    # Check-specific configuration
    config: Dict[str, Any] = field(default_factory=dict)
    
    # Thresholds for status determination
    success_threshold: int = 1  # Consecutive successes needed for operational
    failure_threshold: int = 3  # Consecutive failures for major outage
    
    # Dependencies
    depends_on: List[str] = field(default_factory=list)  # Other check names
    
    # Metadata
    description: str = ""
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class StatusCheckResult:
    """Result of a status check."""
    check_name: str
    status: ServiceStatus
    timestamp: float
    response_time_ms: float
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'check_name': self.check_name,
            'status': self.status.value,
            'timestamp': self.timestamp,
            'response_time_ms': self.response_time_ms,
            'message': self.message,
            'details': self.details,
            'error': self.error
        }


@dataclass
class ServiceStatusSummary:
    """Summary of overall service status."""
    overall_status: ServiceStatus
    timestamp: float
    total_checks: int
    operational_checks: int
    degraded_checks: int
    failed_checks: int
    maintenance_checks: int
    check_results: Dict[str, StatusCheckResult] = field(default_factory=dict)
    dependencies_status: Dict[str, ServiceStatus] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'overall_status': self.overall_status.value,
            'timestamp': self.timestamp,
            'total_checks': self.total_checks,
            'operational_checks': self.operational_checks,
            'degraded_checks': self.degraded_checks,
            'failed_checks': self.failed_checks,
            'maintenance_checks': self.maintenance_checks,
            'check_results': {name: result.to_dict() for name, result in self.check_results.items()},
            'dependencies_status': {name: status.value for name, status in self.dependencies_status.items()},
            'health_percentage': self.health_percentage
        }
    
    @property
    def health_percentage(self) -> float:
        """Calculate overall health percentage."""
        if self.total_checks == 0:
            return 100.0
        
        # Weight different statuses
        score = (
            (self.operational_checks * 100) +
            (self.degraded_checks * 60) +
            (self.failed_checks * 0) +
            (self.maintenance_checks * 80)
        ) / self.total_checks
        
        return min(100.0, max(0.0, score))


class StatusChecker:
    """
    Comprehensive status checking system that monitors service dependencies,
    external APIs, and system components with intelligent status aggregation.
    """
    
    def __init__(
        self,
        storage_path: Optional[str] = None,
        enable_persistence: bool = True,
        default_check_interval: float = 60.0
    ):
        self.storage_path = storage_path or "cortex_status.db"
        self.enable_persistence = enable_persistence
        self.default_check_interval = default_check_interval
        
        # Status checks registry
        self._checks: Dict[str, StatusCheckConfig] = {}
        self._checks_lock = threading.RLock()
        
        # Status tracking
        self._check_results: Dict[str, List[StatusCheckResult]] = {}
        self._current_status: Dict[str, ServiceStatus] = {}
        self._consecutive_results: Dict[str, List[bool]] = {}  # Track success/failure streaks
        
        # Monitoring state
        self._monitoring_active = False
        self._monitor_thread: Optional[threading.Thread] = None
        
        # Status change callbacks
        self._status_callbacks: List[Callable[[str, ServiceStatus, StatusCheckResult], None]] = []
        
        # Dependency tracking
        self._dependency_graph: Dict[str, List[str]] = {}  # check_name -> depends_on
        
        # Initialize storage
        if self.enable_persistence:
            self._init_storage()
        
        # Register default system checks
        self._register_default_checks()
    
    def start_monitoring(self) -> None:
        """Start automatic status monitoring."""
        if self._monitoring_active:
            return
        
        self._monitoring_active = True
        self._monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self._monitor_thread.start()
        
        logger.info("Status monitoring started")
    
    def stop_monitoring(self) -> None:
        """Stop status monitoring."""
        self._monitoring_active = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5.0)
        
        logger.info("Status monitoring stopped")
    
    def register_check(self, check_config: StatusCheckConfig) -> None:
        """
        Register a new status check.
        
        Args:
            check_config: Status check configuration
        """
        with self._checks_lock:
            self._checks[check_config.name] = check_config
            self._check_results[check_config.name] = []
            self._current_status[check_config.name] = ServiceStatus.UNKNOWN
            self._consecutive_results[check_config.name] = []
            
            # Update dependency graph
            if check_config.depends_on:
                self._dependency_graph[check_config.name] = check_config.depends_on.copy()
        
        logger.info(f"Registered status check: {check_config.name}")
    
    def run_check(self, check_name: str) -> StatusCheckResult:
        """
        Run a specific status check manually.
        
        Args:
            check_name: Name of check to run
            
        Returns:
            Check result
        """
        with self._checks_lock:
            config = self._checks.get(check_name)
            if not config:
                return StatusCheckResult(
                    check_name=check_name,
                    status=ServiceStatus.UNKNOWN,
                    timestamp=time.time(),
                    response_time_ms=0.0,
                    message=f"Check {check_name} not found"
                )
            
            return self._execute_check(config)
    
    def run_all_checks(self) -> Dict[str, StatusCheckResult]:
        """
        Run all registered status checks.
        
        Returns:
            Dictionary of check results
        """
        results = {}
        
        with self._checks_lock:
            # Sort checks by dependencies (topological sort)
            sorted_checks = self._topological_sort_checks()
            
            for check_name in sorted_checks:
                config = self._checks[check_name]
                if config.enabled:
                    results[check_name] = self._execute_check(config)
        
        return results
    
    def get_status_summary(self) -> ServiceStatusSummary:
        """
        Get comprehensive status summary.
        
        Returns:
            Status summary with aggregated information
        """
        # Run all checks
        check_results = self.run_all_checks()
        
        # Count statuses
        status_counts = {status: 0 for status in ServiceStatus}
        for result in check_results.values():
            status_counts[result.status] += 1
        
        # Determine overall status
        overall_status = self._calculate_overall_status(check_results)
        
        # Get dependencies status
        dependencies_status = self._get_dependencies_status(check_results)
        
        return ServiceStatusSummary(
            overall_status=overall_status,
            timestamp=time.time(),
            total_checks=len(check_results),
            operational_checks=status_counts[ServiceStatus.OPERATIONAL],
            degraded_checks=status_counts[ServiceStatus.DEGRADED] + status_counts[ServiceStatus.PARTIAL_OUTAGE],
            failed_checks=status_counts[ServiceStatus.MAJOR_OUTAGE],
            maintenance_checks=status_counts[ServiceStatus.MAINTENANCE],
            check_results=check_results,
            dependencies_status=dependencies_status
        )
    
    def get_check_history(
        self,
        check_name: str,
        hours: int = 24
    ) -> List[StatusCheckResult]:
        """
        Get check history for a specific check.
        
        Args:
            check_name: Name of check
            hours: Number of hours of history
            
        Returns:
            List of check results
        """
        cutoff_time = time.time() - (hours * 3600)
        
        with self._checks_lock:
            results = self._check_results.get(check_name, [])
            return [r for r in results if r.timestamp > cutoff_time]
    
    def get_status_trends(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get status trends over time.
        
        Args:
            hours: Number of hours to analyze
            
        Returns:
            Trend analysis
        """
        cutoff_time = time.time() - (hours * 3600)
        trends = {}
        
        with self._checks_lock:
            for check_name, results in self._check_results.items():
                recent_results = [r for r in results if r.timestamp > cutoff_time]
                
                if recent_results:
                    # Calculate uptime percentage
                    operational_count = sum(
                        1 for r in recent_results 
                        if r.status == ServiceStatus.OPERATIONAL
                    )
                    uptime_percentage = (operational_count / len(recent_results)) * 100
                    
                    # Calculate average response time
                    avg_response_time = sum(r.response_time_ms for r in recent_results) / len(recent_results)
                    
                    # Detect trend direction
                    if len(recent_results) >= 10:
                        recent_half = recent_results[len(recent_results)//2:]
                        earlier_half = recent_results[:len(recent_results)//2]
                        
                        recent_uptime = sum(1 for r in recent_half if r.status == ServiceStatus.OPERATIONAL) / len(recent_half)
                        earlier_uptime = sum(1 for r in earlier_half if r.status == ServiceStatus.OPERATIONAL) / len(earlier_half)
                        
                        if recent_uptime > earlier_uptime + 0.1:
                            trend_direction = "improving"
                        elif recent_uptime < earlier_uptime - 0.1:
                            trend_direction = "degrading"
                        else:
                            trend_direction = "stable"
                    else:
                        trend_direction = "stable"
                    
                    trends[check_name] = {
                        'uptime_percentage': uptime_percentage,
                        'avg_response_time_ms': avg_response_time,
                        'trend_direction': trend_direction,
                        'total_checks': len(recent_results),
                        'current_status': self._current_status.get(check_name, ServiceStatus.UNKNOWN).value
                    }
        
        return trends
    
    def add_status_callback(
        self,
        callback: Callable[[str, ServiceStatus, StatusCheckResult], None]
    ) -> None:
        """Add callback for status changes."""
        self._status_callbacks.append(callback)
    
    def _register_default_checks(self) -> None:
        """Register default system status checks."""
        # System disk space check
        self.register_check(StatusCheckConfig(
            name="system_disk_space",
            check_type=CheckType.DISK_SPACE,
            config={
                'path': '/',
                'warning_threshold_percent': 80,
                'critical_threshold_percent': 90
            },
            interval_seconds=120.0,
            description="System disk space availability"
        ))
        
        # System process check (if we can identify key processes)
        self.register_check(StatusCheckConfig(
            name="system_processes",
            check_type=CheckType.CUSTOM_FUNCTION,
            config={
                'function': self._check_system_processes
            },
            interval_seconds=60.0,
            description="Critical system processes health"
        ))
        
        # Network connectivity check
        self.register_check(StatusCheckConfig(
            name="network_connectivity",
            check_type=CheckType.HTTP_ENDPOINT,
            config={
                'url': 'https://httpbin.org/status/200',
                'expected_status_codes': [200],
                'timeout_seconds': 10
            },
            interval_seconds=120.0,
            description="External network connectivity"
        ))
    
    def register_http_check(
        self,
        name: str,
        url: str,
        expected_status_codes: List[int] = None,
        expected_response_contains: Optional[str] = None,
        timeout_seconds: float = 30.0,
        interval_seconds: float = 60.0,
        headers: Optional[Dict[str, str]] = None
    ) -> None:
        """Register an HTTP endpoint check."""
        if expected_status_codes is None:
            expected_status_codes = [200]
        
        config = StatusCheckConfig(
            name=name,
            check_type=CheckType.HTTP_ENDPOINT,
            config={
                'url': url,
                'expected_status_codes': expected_status_codes,
                'expected_response_contains': expected_response_contains,
                'timeout_seconds': timeout_seconds,
                'headers': headers or {}
            },
            interval_seconds=interval_seconds,
            timeout_seconds=timeout_seconds
        )
        
        self.register_check(config)
    
    def register_tcp_check(
        self,
        name: str,
        host: str,
        port: int,
        timeout_seconds: float = 10.0,
        interval_seconds: float = 60.0
    ) -> None:
        """Register a TCP port check."""
        config = StatusCheckConfig(
            name=name,
            check_type=CheckType.TCP_PORT,
            config={
                'host': host,
                'port': port,
                'timeout_seconds': timeout_seconds
            },
            interval_seconds=interval_seconds,
            timeout_seconds=timeout_seconds
        )
        
        self.register_check(config)
    
    def register_database_check(
        self,
        name: str,
        connection_string: str,
        query: str = "SELECT 1",
        timeout_seconds: float = 30.0,
        interval_seconds: float = 120.0
    ) -> None:
        """Register a database connectivity check."""
        config = StatusCheckConfig(
            name=name,
            check_type=CheckType.DATABASE,
            config={
                'connection_string': connection_string,
                'query': query,
                'timeout_seconds': timeout_seconds
            },
            interval_seconds=interval_seconds,
            timeout_seconds=timeout_seconds
        )
        
        self.register_check(config)
    
    def _execute_check(self, config: StatusCheckConfig) -> StatusCheckResult:
        """Execute a status check with error handling and timing."""
        start_time = time.time()
        
        try:
            # Check dependencies first
            if config.depends_on:
                for dep_name in config.depends_on:
                    dep_status = self._current_status.get(dep_name, ServiceStatus.UNKNOWN)
                    if dep_status in [ServiceStatus.MAJOR_OUTAGE, ServiceStatus.UNKNOWN]:
                        return StatusCheckResult(
                            check_name=config.name,
                            status=ServiceStatus.DEGRADED,
                            timestamp=time.time(),
                            response_time_ms=(time.time() - start_time) * 1000,
                            message=f"Dependency {dep_name} is not operational",
                            details={'dependency_status': dep_status.value}
                        )
            
            # Execute check based on type
            if config.check_type == CheckType.HTTP_ENDPOINT:
                result = self._check_http_endpoint(config)
            elif config.check_type == CheckType.TCP_PORT:
                result = self._check_tcp_port(config)
            elif config.check_type == CheckType.DISK_SPACE:
                result = self._check_disk_space(config)
            elif config.check_type == CheckType.CUSTOM_FUNCTION:
                result = self._check_custom_function(config)
            elif config.check_type == CheckType.CUSTOM_COMMAND:
                result = self._check_custom_command(config)
            else:
                raise ValueError(f"Unsupported check type: {config.check_type}")
            
            # Update timing
            result.response_time_ms = (time.time() - start_time) * 1000
            result.timestamp = time.time()
            
            # Store result and update status
            self._store_check_result(config.name, result)
            
            return result
        
        except Exception as e:
            error_result = StatusCheckResult(
                check_name=config.name,
                status=ServiceStatus.MAJOR_OUTAGE,
                timestamp=time.time(),
                response_time_ms=(time.time() - start_time) * 1000,
                message=f"Check execution failed: {str(e)}",
                error=str(e)
            )
            
            self._store_check_result(config.name, error_result)
            return error_result
    
    def _check_http_endpoint(self, config: StatusCheckConfig) -> StatusCheckResult:
        """Check HTTP endpoint status."""
        if not REQUESTS_AVAILABLE:
            return StatusCheckResult(
                check_name=config.name,
                status=ServiceStatus.MAJOR_OUTAGE,
                timestamp=0,
                response_time_ms=0,
                message="Requests library not available for HTTP checks",
                error="requests module not installed"
            )
        
        check_config = config.config
        
        response = requests.get(
            check_config['url'],
            timeout=check_config.get('timeout_seconds', config.timeout_seconds),
            headers=check_config.get('headers', {}),
            allow_redirects=True
        )
        
        # Check status code
        expected_codes = check_config.get('expected_status_codes', [200])
        if response.status_code not in expected_codes:
            return StatusCheckResult(
                check_name=config.name,
                status=ServiceStatus.MAJOR_OUTAGE,
                timestamp=0,  # Will be set by caller
                response_time_ms=0,  # Will be set by caller
                message=f"Unexpected status code: {response.status_code}",
                details={
                    'status_code': response.status_code,
                    'expected_codes': expected_codes,
                    'response_size': len(response.content)
                }
            )
        
        # Check response content if specified
        expected_content = check_config.get('expected_response_contains')
        if expected_content and expected_content not in response.text:
            return StatusCheckResult(
                check_name=config.name,
                status=ServiceStatus.DEGRADED,
                timestamp=0,
                response_time_ms=0,
                message=f"Expected content not found: {expected_content}",
                details={
                    'status_code': response.status_code,
                    'response_size': len(response.content)
                }
            )
        
        return StatusCheckResult(
            check_name=config.name,
            status=ServiceStatus.OPERATIONAL,
            timestamp=0,
            response_time_ms=0,
            message="HTTP endpoint responding normally",
            details={
                'status_code': response.status_code,
                'response_size': len(response.content)
            }
        )
    
    def _check_tcp_port(self, config: StatusCheckConfig) -> StatusCheckResult:
        """Check TCP port connectivity."""
        check_config = config.config
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(check_config.get('timeout_seconds', config.timeout_seconds))
        
        try:
            result = sock.connect_ex((check_config['host'], check_config['port']))
            
            if result == 0:
                status = ServiceStatus.OPERATIONAL
                message = f"TCP port {check_config['port']} is open"
            else:
                status = ServiceStatus.MAJOR_OUTAGE
                message = f"TCP port {check_config['port']} is closed or unreachable"
            
            return StatusCheckResult(
                check_name=config.name,
                status=status,
                timestamp=0,
                response_time_ms=0,
                message=message,
                details={
                    'host': check_config['host'],
                    'port': check_config['port'],
                    'connection_result': result
                }
            )
        
        finally:
            sock.close()
    
    def _check_disk_space(self, config: StatusCheckConfig) -> StatusCheckResult:
        """Check disk space availability."""
        check_config = config.config
        
        disk_usage = psutil.disk_usage(check_config['path'])
        used_percent = (disk_usage.used / disk_usage.total) * 100
        
        warning_threshold = check_config.get('warning_threshold_percent', 80)
        critical_threshold = check_config.get('critical_threshold_percent', 90)
        
        if used_percent >= critical_threshold:
            status = ServiceStatus.MAJOR_OUTAGE
            message = f"Critical disk usage: {used_percent:.1f}%"
        elif used_percent >= warning_threshold:
            status = ServiceStatus.DEGRADED
            message = f"High disk usage: {used_percent:.1f}%"
        else:
            status = ServiceStatus.OPERATIONAL
            message = f"Disk usage normal: {used_percent:.1f}%"
        
        return StatusCheckResult(
            check_name=config.name,
            status=status,
            timestamp=0,
            response_time_ms=0,
            message=message,
            details={
                'path': check_config['path'],
                'used_percent': used_percent,
                'total_gb': disk_usage.total / (1024**3),
                'free_gb': disk_usage.free / (1024**3),
                'warning_threshold': warning_threshold,
                'critical_threshold': critical_threshold
            }
        )
    
    def _check_custom_function(self, config: StatusCheckConfig) -> StatusCheckResult:
        """Execute custom function check."""
        check_config = config.config
        check_function = check_config['function']
        
        # Execute custom function
        result = check_function()
        
        # Validate result format
        if not isinstance(result, dict):
            raise ValueError("Custom function must return dictionary")
        
        required_fields = ['status', 'message']
        for field in required_fields:
            if field not in result:
                raise ValueError(f"Custom function result must include '{field}' field")
        
        # Convert status string to enum if needed
        if isinstance(result['status'], str):
            status = ServiceStatus(result['status'])
        else:
            status = result['status']
        
        return StatusCheckResult(
            check_name=config.name,
            status=status,
            timestamp=0,
            response_time_ms=0,
            message=result['message'],
            details=result.get('details', {})
        )
    
    def _check_custom_command(self, config: StatusCheckConfig) -> StatusCheckResult:
        """Execute custom command check."""
        check_config = config.config
        
        result = subprocess.run(
            check_config['command'],
            shell=True,
            capture_output=True,
            text=True,
            timeout=config.timeout_seconds
        )
        
        # Determine status based on exit code and output
        if result.returncode == 0:
            status = ServiceStatus.OPERATIONAL
            message = "Command executed successfully"
        else:
            status = ServiceStatus.MAJOR_OUTAGE
            message = f"Command failed with exit code {result.returncode}"
        
        return StatusCheckResult(
            check_name=config.name,
            status=status,
            timestamp=0,
            response_time_ms=0,
            message=message,
            details={
                'exit_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'command': check_config['command']
            }
        )
    
    def _check_system_processes(self) -> Dict[str, Any]:
        """Custom function to check system processes."""
        try:
            # Get basic system info
            cpu_percent = psutil.cpu_percent(interval=1.0)
            memory = psutil.virtual_memory()
            process_count = len(psutil.pids())
            
            # Determine status based on system load
            if cpu_percent > 90 or memory.percent > 95:
                status = ServiceStatus.DEGRADED
                message = f"High system load (CPU: {cpu_percent:.1f}%, Memory: {memory.percent:.1f}%)"
            elif cpu_percent > 95 or memory.percent > 98:
                status = ServiceStatus.MAJOR_OUTAGE
                message = f"Critical system load (CPU: {cpu_percent:.1f}%, Memory: {memory.percent:.1f}%)"
            else:
                status = ServiceStatus.OPERATIONAL
                message = f"System processes healthy (CPU: {cpu_percent:.1f}%, Memory: {memory.percent:.1f}%)"
            
            return {
                'status': status.value,
                'message': message,
                'details': {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'process_count': process_count,
                    'load_average': psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0
                }
            }
        
        except Exception as e:
            return {
                'status': ServiceStatus.MAJOR_OUTAGE.value,
                'message': f"System process check failed: {e}",
                'details': {'error': str(e)}
            }
    
    def _store_check_result(self, check_name: str, result: StatusCheckResult) -> None:
        """Store check result and update status tracking."""
        with self._checks_lock:
            # Store result
            if check_name not in self._check_results:
                self._check_results[check_name] = []
            
            self._check_results[check_name].append(result)
            
            # Limit history size
            if len(self._check_results[check_name]) > 1000:
                self._check_results[check_name] = self._check_results[check_name][-500:]
            
            # Update consecutive results tracking
            is_success = result.status == ServiceStatus.OPERATIONAL
            if check_name not in self._consecutive_results:
                self._consecutive_results[check_name] = []
            
            self._consecutive_results[check_name].append(is_success)
            if len(self._consecutive_results[check_name]) > 10:
                self._consecutive_results[check_name] = self._consecutive_results[check_name][-10:]
            
            # Determine new status based on consecutive results and thresholds
            config = self._checks.get(check_name)
            if config:
                new_status = self._calculate_check_status(check_name, result.status, config)
                old_status = self._current_status.get(check_name, ServiceStatus.UNKNOWN)
                self._current_status[check_name] = new_status
                
                # Notify callbacks if status changed
                if new_status != old_status:
                    for callback in self._status_callbacks:
                        try:
                            callback(check_name, new_status, result)
                        except Exception as e:
                            logger.warning(f"Status callback error: {e}")
    
    def _calculate_check_status(
        self,
        check_name: str,
        current_result_status: ServiceStatus,
        config: StatusCheckConfig
    ) -> ServiceStatus:
        """Calculate check status based on consecutive results and thresholds."""
        consecutive_results = self._consecutive_results.get(check_name, [])
        
        if not consecutive_results:
            return current_result_status
        
        # Count consecutive successes and failures
        consecutive_successes = 0
        consecutive_failures = 0
        
        # Count from the end (most recent)
        for success in reversed(consecutive_results):
            if success:
                consecutive_successes += 1
                break
            else:
                consecutive_failures += 1
        
        # Apply thresholds
        if consecutive_successes >= config.success_threshold:
            return ServiceStatus.OPERATIONAL
        elif consecutive_failures >= config.failure_threshold:
            return ServiceStatus.MAJOR_OUTAGE
        elif consecutive_failures > 0:
            return ServiceStatus.DEGRADED
        else:
            return current_result_status
    
    def _calculate_overall_status(self, check_results: Dict[str, StatusCheckResult]) -> ServiceStatus:
        """Calculate overall system status from individual check results."""
        if not check_results:
            return ServiceStatus.UNKNOWN
        
        status_priority = {
            ServiceStatus.MAJOR_OUTAGE: 5,
            ServiceStatus.PARTIAL_OUTAGE: 4,
            ServiceStatus.DEGRADED: 3,
            ServiceStatus.MAINTENANCE: 2,
            ServiceStatus.OPERATIONAL: 1,
            ServiceStatus.UNKNOWN: 0
        }
        
        highest_priority = 0
        for result in check_results.values():
            priority = status_priority.get(result.status, 0)
            highest_priority = max(highest_priority, priority)
        
        # Find status with highest priority
        for status, priority in status_priority.items():
            if priority == highest_priority:
                return status
        
        return ServiceStatus.UNKNOWN
    
    def _get_dependencies_status(self, check_results: Dict[str, StatusCheckResult]) -> Dict[str, ServiceStatus]:
        """Get status of check dependencies."""
        dependencies = {}
        
        for check_name, result in check_results.items():
            config = self._checks.get(check_name)
            if config and config.depends_on:
                for dep_name in config.depends_on:
                    if dep_name in check_results:
                        dependencies[dep_name] = check_results[dep_name].status
        
        return dependencies
    
    def _topological_sort_checks(self) -> List[str]:
        """Sort checks by dependencies using topological sort."""
        # Simple topological sort implementation
        visited = set()
        result = []
        
        def visit(check_name: str):
            if check_name in visited:
                return
            
            visited.add(check_name)
            
            # Visit dependencies first
            config = self._checks.get(check_name)
            if config and config.depends_on:
                for dep_name in config.depends_on:
                    if dep_name in self._checks:
                        visit(dep_name)
            
            result.append(check_name)
        
        # Visit all checks
        for check_name in self._checks:
            visit(check_name)
        
        return result
    
    def _init_storage(self) -> None:
        """Initialize SQLite storage for status persistence."""
        try:
            conn = sqlite3.connect(self.storage_path)
            cursor = conn.cursor()
            
            # Create status_results table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS status_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    check_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    response_time_ms REAL NOT NULL,
                    message TEXT NOT NULL,
                    details TEXT,
                    error TEXT
                )
            """)
            
            # Create index for efficient queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_status_check_timestamp 
                ON status_results(check_name, timestamp)
            """)
            
            conn.commit()
            conn.close()
            
            logger.info(f"Initialized status storage: {self.storage_path}")
        
        except Exception as e:
            logger.error(f"Failed to initialize status storage: {e}")
    
    def _monitoring_loop(self) -> None:
        """Main status monitoring loop."""
        logger.info("Status monitoring loop started")
        
        last_check_times = {}
        
        while self._monitoring_active:
            try:
                current_time = time.time()
                
                with self._checks_lock:
                    for check_name, config in self._checks.items():
                        if not config.enabled:
                            continue
                        
                        # Check if it's time to run this check
                        last_check = last_check_times.get(check_name, 0)
                        if current_time - last_check >= config.interval_seconds:
                            try:
                                self._execute_check(config)
                                last_check_times[check_name] = current_time
                            except Exception as e:
                                logger.error(f"Check execution error for {check_name}: {e}")
                
                # Wait before next iteration
                time.sleep(10)  # Check every 10 seconds for due checks
            
            except Exception as e:
                logger.error(f"Status monitoring loop error: {e}")
                time.sleep(60)
        
        logger.info("Status monitoring loop stopped")


# Global status checker instance
default_status_checker = StatusChecker()