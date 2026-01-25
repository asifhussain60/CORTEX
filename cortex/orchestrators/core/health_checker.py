"""
Health Checker for Database-Backed Orchestrator Registry

Provides continuous validation that wiring stays intact:
- Background validation every 60 seconds
- Automatic detection of unwiring
- Recovery attempts with escalation
- Full audit trail in database

AC-ID: AC-DB-SSOT-002

Author: Asif Hussain
Date: 2026-01-25
"""

from __future__ import annotations

import json
import logging
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

from cortex.brain.core.result import Err, Ok, Result
from cortex.infrastructure.database import DatabaseManager

logger = logging.getLogger(__name__)


@dataclass
class HealthCheckResult:
    """Result of a health check."""
    
    check_time: datetime
    orchestrators_ok: int
    orchestrators_failed: int
    unwiring_detected: bool
    recovery_attempted: bool
    recovery_success: bool
    details: Dict[str, Any]
    
    @property
    def is_healthy(self) -> bool:
        """Check if system is healthy."""
        return self.orchestrators_failed == 0 and not self.unwiring_detected


class OrchestratorHealthChecker:
    """
    Continuous health monitoring for orchestrator registry.
    
    Features:
    - Background validation every N seconds
    - Automatic detection of unwiring
    - Recovery attempts with configurable policy
    - Escalation for persistent failures
    - Full audit trail in database
    
    Usage:
        from cortex.orchestrators.core.database_registry import get_database_registry
        
        registry = get_database_registry()
        health_checker = OrchestratorHealthChecker(registry)
        health_checker.start_background_checks(interval_seconds=60)
        
        # Later...
        health_checker.stop_background_checks()
    """
    
    DEFAULT_INTERVAL = 60  # seconds
    MAX_RECOVERY_ATTEMPTS = 3
    ESCALATION_THRESHOLD = 3  # Consecutive failures before escalation
    
    def __init__(
        self,
        registry: Any,  # DatabaseBackedRegistry - avoid circular import
        db: Optional[DatabaseManager] = None,
        alert_callback: Optional[Callable[[str, Dict], None]] = None
    ):
        """
        Initialize health checker.
        
        Args:
            registry: DatabaseBackedRegistry instance to monitor
            db: Optional DatabaseManager for logging (defaults to registry's DB)
            alert_callback: Optional callback for alerts (message, details)
        """
        self._registry = registry
        self._db = db or registry._db
        self._alert_callback = alert_callback
        
        self._running = False
        self._check_thread: Optional[threading.Thread] = None
        self._interval = self.DEFAULT_INTERVAL
        
        self._consecutive_failures = 0
        self._last_check: Optional[HealthCheckResult] = None
        self._recovery_attempts = 0
        self._unwiring_first_detected: Optional[datetime] = None
        
        self._check_history: List[HealthCheckResult] = []
        self._max_history = 100
    
    # =========================================================================
    # Background Check Management
    # =========================================================================
    
    def start_background_checks(self, interval_seconds: int = DEFAULT_INTERVAL) -> None:
        """
        Start background health checks.
        
        Args:
            interval_seconds: Seconds between checks (default: 60)
        """
        if self._running:
            logger.warning("Health checks already running")
            return
        
        self._interval = interval_seconds
        self._running = True
        self._check_thread = threading.Thread(
            target=self._background_check_loop,
            name="OrchestratorHealthChecker",
            daemon=True
        )
        self._check_thread.start()
        logger.info(f"Started background health checks (every {interval_seconds}s)")
    
    def stop_background_checks(self) -> None:
        """Stop background health checks."""
        self._running = False
        if self._check_thread:
            self._check_thread.join(timeout=5.0)
            self._check_thread = None
        logger.info("Stopped background health checks")
    
    def _background_check_loop(self) -> None:
        """Main loop for background checks."""
        while self._running:
            try:
                self.run_health_check()
            except Exception as e:
                logger.error(f"Health check failed: {e}")
            
            # Wait for next interval
            time.sleep(self._interval)
    
    # =========================================================================
    # Health Check Logic
    # =========================================================================
    
    def run_health_check(self) -> HealthCheckResult:
        """
        Run a single health check.
        
        Checks:
        1. All registered orchestrators are wired
        2. All wired orchestrators are callable
        3. Current state matches last snapshot
        
        Returns:
            HealthCheckResult with check details
        """
        check_time = datetime.now(timezone.utc)
        details: Dict[str, Any] = {}
        
        # Step 1: Validate wiring
        validation = self._registry.validate_wiring()
        orchestrators_ok = validation.passed_count
        orchestrators_failed = validation.checked_count - validation.passed_count
        
        details['validation'] = {
            'checked': validation.checked_count,
            'passed': validation.passed_count,
            'failures': validation.failures
        }
        
        # Step 2: Compare with snapshot
        snapshot_result = self._registry.compare_with_snapshot()
        if snapshot_result.is_ok():
            comparison = snapshot_result.unwrap()
            details['snapshot_comparison'] = comparison
            drift_detected = comparison.get('drift_detected', False)
        else:
            drift_detected = False
            details['snapshot_comparison'] = {'error': snapshot_result.error}
        
        # Determine if unwiring occurred
        unwiring_detected = orchestrators_failed > 0 or drift_detected
        
        # Step 3: Attempt recovery if needed
        recovery_attempted = False
        recovery_success = False
        
        if unwiring_detected:
            if self._unwiring_first_detected is None:
                self._unwiring_first_detected = check_time
                logger.warning(f"Unwiring first detected at {check_time}")
            
            self._consecutive_failures += 1
            
            # Attempt recovery if under threshold
            if self._recovery_attempts < self.MAX_RECOVERY_ATTEMPTS:
                recovery_attempted = True
                recovery_success = self._attempt_recovery(details)
                self._recovery_attempts += 1
            else:
                logger.error("Max recovery attempts exceeded")
                details['recovery'] = {'message': 'Max attempts exceeded'}
            
            # Escalate if consecutive failures exceed threshold
            if self._consecutive_failures >= self.ESCALATION_THRESHOLD:
                self._escalate(details)
        else:
            # Reset counters on success
            self._consecutive_failures = 0
            self._recovery_attempts = 0
            self._unwiring_first_detected = None
        
        # Create result
        result = HealthCheckResult(
            check_time=check_time,
            orchestrators_ok=orchestrators_ok,
            orchestrators_failed=orchestrators_failed,
            unwiring_detected=unwiring_detected,
            recovery_attempted=recovery_attempted,
            recovery_success=recovery_success,
            details=details
        )
        
        # Log to database
        self._log_health_check(result)
        
        # Store in history
        self._check_history.append(result)
        if len(self._check_history) > self._max_history:
            self._check_history.pop(0)
        
        self._last_check = result
        
        # Log summary
        if result.is_healthy:
            logger.debug(f"Health check passed ({orchestrators_ok} orchestrators OK)")
        else:
            logger.warning(
                f"Health check detected issues: {orchestrators_failed} failed, "
                f"unwiring={unwiring_detected}"
            )
        
        return result
    
    def _attempt_recovery(self, details: Dict[str, Any]) -> bool:
        """
        Attempt to recover from unwiring.
        
        Strategies:
        1. Re-wire missing orchestrators
        2. Reload from database configuration
        
        Args:
            details: Dictionary to populate with recovery details
            
        Returns:
            True if recovery succeeded
        """
        logger.info(f"Attempting recovery (attempt {self._recovery_attempts + 1})")
        
        try:
            # Strategy 1: Try to re-wire
            wire_result = self._registry.wire_all(fail_fast=False)
            
            if wire_result.is_ok():
                validation = wire_result.unwrap()
                if validation.passed:
                    details['recovery'] = {
                        'strategy': 'rewire',
                        'success': True,
                        'message': 'Re-wiring succeeded'
                    }
                    logger.info("Recovery succeeded via re-wiring")
                    return True
                else:
                    details['recovery'] = {
                        'strategy': 'rewire',
                        'success': False,
                        'failures': validation.failures
                    }
                    logger.warning(f"Re-wiring partial: {len(validation.failures)} failures")
            else:
                details['recovery'] = {
                    'strategy': 'rewire',
                    'success': False,
                    'error': wire_result.error
                }
            
            return False
            
        except Exception as e:
            details['recovery'] = {
                'strategy': 'rewire',
                'success': False,
                'error': str(e)
            }
            logger.error(f"Recovery failed: {e}")
            return False
    
    def _escalate(self, details: Dict[str, Any]) -> None:
        """
        Escalate persistent failure.
        
        Sends alert and logs critical error.
        """
        message = (
            f"CORTEX Orchestrator Wiring Failure - Manual Intervention Required\n"
            f"Consecutive failures: {self._consecutive_failures}\n"
            f"First detected: {self._unwiring_first_detected}\n"
            f"Recovery attempts: {self._recovery_attempts}"
        )
        
        logger.critical(message)
        
        if self._alert_callback:
            try:
                self._alert_callback(message, details)
            except Exception as e:
                logger.error(f"Alert callback failed: {e}")
        
        details['escalation'] = {
            'triggered': True,
            'consecutive_failures': self._consecutive_failures,
            'recovery_attempts': self._recovery_attempts
        }
    
    def _log_health_check(self, result: HealthCheckResult) -> None:
        """Log health check result to database."""
        try:
            with self._db.get_connection() as conn:
                conn.execute("""
                    INSERT INTO health_check_log (
                        check_time, orchestrators_ok, orchestrators_failed,
                        unwiring_detected, recovery_attempted, recovery_success,
                        details
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    result.check_time.isoformat(),
                    result.orchestrators_ok,
                    result.orchestrators_failed,
                    1 if result.unwiring_detected else 0,
                    1 if result.recovery_attempted else 0,
                    1 if result.recovery_success else 0,
                    json.dumps(result.details)
                ))
                conn.commit()
        except Exception as e:
            logger.warning(f"Failed to log health check: {e}")
    
    # =========================================================================
    # Public API
    # =========================================================================
    
    def get_last_check(self) -> Optional[HealthCheckResult]:
        """Get the most recent health check result."""
        return self._last_check
    
    def get_check_history(self, limit: int = 10) -> List[HealthCheckResult]:
        """Get recent health check history."""
        return self._check_history[-limit:]
    
    def get_status(self) -> Dict[str, Any]:
        """Get current health checker status."""
        return {
            'running': self._running,
            'interval_seconds': self._interval,
            'consecutive_failures': self._consecutive_failures,
            'recovery_attempts': self._recovery_attempts,
            'unwiring_first_detected': (
                self._unwiring_first_detected.isoformat()
                if self._unwiring_first_detected else None
            ),
            'last_check': {
                'time': self._last_check.check_time.isoformat() if self._last_check else None,
                'healthy': self._last_check.is_healthy if self._last_check else None
            },
            'history_count': len(self._check_history)
        }
    
    def force_check(self) -> HealthCheckResult:
        """Force an immediate health check."""
        return self.run_health_check()
    
    def reset_recovery_counter(self) -> None:
        """Reset recovery attempt counter (e.g., after manual intervention)."""
        self._recovery_attempts = 0
        self._consecutive_failures = 0
        self._unwiring_first_detected = None
        logger.info("Recovery counters reset")


# Convenience function
def create_health_checker(
    registry: Any,
    start_immediately: bool = True,
    interval_seconds: int = 60,
    alert_callback: Optional[Callable[[str, Dict], None]] = None
) -> OrchestratorHealthChecker:
    """
    Create and optionally start a health checker.
    
    Args:
        registry: DatabaseBackedRegistry instance
        start_immediately: Whether to start background checks immediately
        interval_seconds: Check interval (default: 60)
        alert_callback: Optional alert callback
        
    Returns:
        Configured OrchestratorHealthChecker
    """
    checker = OrchestratorHealthChecker(
        registry=registry,
        alert_callback=alert_callback
    )
    
    if start_immediately:
        checker.start_background_checks(interval_seconds)
    
    return checker
