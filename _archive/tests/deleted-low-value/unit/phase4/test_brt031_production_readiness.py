"""
BRT-031: Production Readiness & Best Practices

Final validation and best practices for production deployment of the
resilience framework.

Test Infrastructure (RED phase - Tests Before Implementation per CORE-008)
"""

import pytest
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Set, Callable
from threading import Lock
from enum import Enum
import time
import hashlib


class ReadinessStatus(Enum):
    """Readiness status levels."""
    NOT_READY = "not_ready"
    PARTIAL = "partial"
    READY = "ready"
    PRODUCTION = "production"


class BestPractice(Enum):
    """Best practice checks."""
    LOGGING_ENABLED = "logging_enabled"
    MONITORING_ENABLED = "monitoring_enabled"
    ERROR_HANDLING = "error_handling"
    GRACEFUL_SHUTDOWN = "graceful_shutdown"
    CONFIGURATION_VALIDATION = "configuration_validation"
    PERFORMANCE_TUNING = "performance_tuning"
    DOCUMENTATION = "documentation"
    SECURITY = "security"
    TESTING = "testing"
    DEPLOYMENT = "deployment"


@dataclass
class HealthReport:
    """Report on system health."""
    timestamp_ms: float = field(default_factory=lambda: time.time() * 1000)
    service_name: str = ""
    version: str = ""
    status: str = "unknown"
    uptime_ms: int = 0
    response_time_ms: float = 0.0
    error_count: int = 0
    memory_mb: float = 0.0
    cpu_percent: float = 0.0
    dependencies_healthy: bool = True
    checks: Dict[str, bool] = field(default_factory=dict)


class ConfigurationValidator:
    """Validates configuration for production readiness."""
    
    def __init__(self):
        self._required_fields: Set[str] = set()
        self._validators: Dict[str, Callable[[Any], bool]] = {}
        self._lock = Lock()
    
    def add_required_field(self, field_name: str) -> bool:
        """Add required configuration field."""
        with self._lock:
            self._required_fields.add(field_name)
            return True
    
    def add_validator(
        self,
        field_name: str,
        validator: Callable[[Any], bool]
    ) -> bool:
        """Add validator for field."""
        with self._lock:
            if field_name in self._validators:
                return False
            
            self._validators[field_name] = validator
            return True
    
    def validate_config(self, config: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate configuration."""
        errors = []
        
        with self._lock:
            # Check required fields
            for field in self._required_fields:
                if field not in config:
                    errors.append(f"Missing required field: {field}")
            
            # Run validators
            for field, validator in self._validators.items():
                if field in config:
                    try:
                        if not validator(config[field]):
                            errors.append(f"Validation failed for field: {field}")
                    except Exception as e:
                        errors.append(f"Validator error for {field}: {str(e)}")
        
        return len(errors) == 0, errors


class ProductionReadinessChecker:
    """Checks system readiness for production."""
    
    def __init__(self):
        self._checks: Dict[BestPractice, Callable[[], bool]] = {}
        self._lock = Lock()
    
    def register_check(self, practice: BestPractice, check_fn: Callable[[], bool]) -> bool:
        """Register readiness check."""
        with self._lock:
            if practice in self._checks:
                return False
            
            self._checks[practice] = check_fn
            return True
    
    def check_readiness(self) -> Dict[BestPractice, bool]:
        """Check readiness for all practices."""
        results = {}
        
        with self._lock:
            checks = self._checks.copy()
        
        for practice, check_fn in checks.items():
            try:
                results[practice] = check_fn()
            except Exception:
                results[practice] = False
        
        return results
    
    def get_readiness_status(self) -> ReadinessStatus:
        """Get overall readiness status."""
        results = self.check_readiness()
        
        if not results:
            return ReadinessStatus.NOT_READY
        
        passed = sum(1 for v in results.values() if v)
        total = len(results)
        
        if passed == total:
            return ReadinessStatus.PRODUCTION
        elif passed >= (total * 0.8):
            return ReadinessStatus.READY
        elif passed >= (total * 0.5):
            return ReadinessStatus.PARTIAL
        else:
            return ReadinessStatus.NOT_READY


class ServiceHealthMonitor:
    """Monitors service health."""
    
    def __init__(self, service_name: str, version: str):
        self.service_name = service_name
        self.version = version
        self._start_time_ms = time.time() * 1000
        self._request_count = 0
        self._error_count = 0
        self._response_times: List[float] = []
        self._lock = Lock()
    
    def record_request(self, response_time_ms: float, success: bool = True) -> None:
        """Record a request."""
        with self._lock:
            self._request_count += 1
            if not success:
                self._error_count += 1
            self._response_times.append(response_time_ms)
    
    def get_health_report(self) -> HealthReport:
        """Get health report."""
        with self._lock:
            now = time.time() * 1000
            uptime_ms = now - self._start_time_ms
            
            avg_response = (sum(self._response_times) / len(self._response_times)
                           if self._response_times else 0.0)
            
            return HealthReport(
                timestamp_ms=now,
                service_name=self.service_name,
                version=self.version,
                status="healthy",
                uptime_ms=int(uptime_ms),
                response_time_ms=avg_response,
                error_count=self._error_count,
                dependencies_healthy=True
            )


class DeploymentValidator:
    """Validates deployment configuration."""
    
    def __init__(self):
        self._deployment_checks: Dict[str, Callable[[], bool]] = {}
        self._lock = Lock()
    
    def add_check(self, check_name: str, check_fn: Callable[[], bool]) -> bool:
        """Add deployment check."""
        with self._lock:
            if check_name in self._deployment_checks:
                return False
            
            self._deployment_checks[check_name] = check_fn
            return True
    
    def validate_deployment(self) -> tuple[bool, Dict[str, bool]]:
        """Validate deployment readiness."""
        results = {}
        
        with self._lock:
            checks = self._deployment_checks.copy()
        
        for check_name, check_fn in checks.items():
            try:
                results[check_name] = check_fn()
            except Exception:
                results[check_name] = False
        
        all_passed = all(results.values())
        return all_passed, results


class DocumentationChecker:
    """Checks for required documentation."""
    
    def __init__(self):
        self._required_docs: Set[str] = set()
        self._available_docs: Set[str] = set()
        self._lock = Lock()
    
    def add_required_doc(self, doc_name: str) -> bool:
        """Add required documentation."""
        with self._lock:
            self._required_docs.add(doc_name)
            return True
    
    def document_available(self, doc_name: str) -> bool:
        """Mark documentation as available."""
        with self._lock:
            self._available_docs.add(doc_name)
            return True
    
    def get_documentation_status(self) -> tuple[bool, Set[str], Set[str]]:
        """Get documentation status."""
        with self._lock:
            missing = self._required_docs - self._available_docs
            complete = len(missing) == 0
            return complete, self._required_docs, missing


class BackupManager:
    """Manages backup and recovery."""
    
    def __init__(self, backup_dir: str):
        self.backup_dir = backup_dir
        self._backups: Dict[str, Dict[str, Any]] = {}
        self._lock = Lock()
    
    def create_backup(self, backup_id: str, data: Dict[str, Any]) -> bool:
        """Create a backup."""
        with self._lock:
            if backup_id in self._backups:
                return False
            
            self._backups[backup_id] = {
                "data": data.copy(),
                "timestamp_ms": time.time() * 1000,
                "checksum": hashlib.sha256(str(data).encode()).hexdigest()
            }
            return True
    
    def restore_backup(self, backup_id: str) -> Optional[Dict[str, Any]]:
        """Restore a backup."""
        with self._lock:
            backup = self._backups.get(backup_id)
            if not backup:
                return None
            
            return backup["data"].copy()
    
    def list_backups(self) -> List[str]:
        """List available backups."""
        with self._lock:
            return list(self._backups.keys())
    
    def verify_backup_integrity(self, backup_id: str) -> bool:
        """Verify backup integrity."""
        with self._lock:
            backup = self._backups.get(backup_id)
            if not backup:
                return False
            
            # Recalculate checksum
            data = backup["data"]
            expected_checksum = backup["checksum"]
            actual_checksum = hashlib.sha256(str(data).encode()).hexdigest()
            
            return expected_checksum == actual_checksum


class RolloutManager:
    """Manages deployment rollout."""
    
    def __init__(self):
        self._rollout_state = "not_started"
        self._canary_percentage = 0
        self._active_version = "0.0.0"
        self._previous_version = None
        self._lock = Lock()
    
    def start_canary_rollout(self, new_version: str, canary_percent: int) -> bool:
        """Start canary rollout."""
        with self._lock:
            if self._rollout_state != "not_started":
                return False
            
            self._rollout_state = "canary"
            self._canary_percentage = canary_percent
            self._previous_version = self._active_version
            return True
    
    def complete_rollout(self, new_version: str) -> bool:
        """Complete rollout to all instances."""
        with self._lock:
            if self._rollout_state != "canary":
                return False
            
            self._rollout_state = "completed"
            self._active_version = new_version
            self._canary_percentage = 100
            return True
    
    def rollback(self) -> bool:
        """Rollback to previous version."""
        with self._lock:
            if not self._previous_version:
                return False
            
            self._active_version = self._previous_version
            self._rollout_state = "rolled_back"
            return True
    
    def get_rollout_status(self) -> Dict[str, Any]:
        """Get rollout status."""
        with self._lock:
            return {
                "state": self._rollout_state,
                "active_version": self._active_version,
                "canary_percentage": self._canary_percentage
            }


# ============================================================================
# TEST SUITE
# ============================================================================

class TestConfigurationValidator:
    """Test ConfigurationValidator functionality."""
    
    def test_add_required_field(self):
        """Test adding required field."""
        validator = ConfigurationValidator()
        assert validator.add_required_field("host")
    
    def test_validate_with_missing_field(self):
        """Test validation with missing required field."""
        validator = ConfigurationValidator()
        validator.add_required_field("host")
        
        valid, errors = validator.validate_config({"port": 8080})
        assert not valid
        assert len(errors) > 0
    
    def test_validate_with_custom_validator(self):
        """Test validation with custom validator."""
        validator = ConfigurationValidator()
        validator.add_validator("port", lambda x: 1 <= x <= 65535)
        
        valid, errors = validator.validate_config({"port": 8080})
        assert valid
    
    def test_validate_fails_custom_validator(self):
        """Test validation fails custom validator."""
        validator = ConfigurationValidator()
        validator.add_validator("port", lambda x: 1 <= x <= 65535)
        
        valid, errors = validator.validate_config({"port": 99999})
        assert not valid


class TestProductionReadinessChecker:
    """Test ProductionReadinessChecker functionality."""
    
    def test_register_check(self):
        """Test registering check."""
        checker = ProductionReadinessChecker()
        assert checker.register_check(BestPractice.LOGGING_ENABLED, lambda: True)
    
    def test_check_readiness(self):
        """Test checking readiness."""
        checker = ProductionReadinessChecker()
        checker.register_check(BestPractice.LOGGING_ENABLED, lambda: True)
        checker.register_check(BestPractice.MONITORING_ENABLED, lambda: True)
        
        results = checker.check_readiness()
        assert results[BestPractice.LOGGING_ENABLED]
    
    def test_get_readiness_status_production(self):
        """Test getting production readiness status."""
        checker = ProductionReadinessChecker()
        checker.register_check(BestPractice.LOGGING_ENABLED, lambda: True)
        checker.register_check(BestPractice.MONITORING_ENABLED, lambda: True)
        
        status = checker.get_readiness_status()
        assert status == ReadinessStatus.PRODUCTION


class TestServiceHealthMonitor:
    """Test ServiceHealthMonitor functionality."""
    
    def test_record_request(self):
        """Test recording request."""
        monitor = ServiceHealthMonitor("api", "1.0.0")
        monitor.record_request(100.0, success=True)
        
        report = monitor.get_health_report()
        assert report.service_name == "api"
    
    def test_health_report_includes_stats(self):
        """Test health report includes statistics."""
        monitor = ServiceHealthMonitor("api", "1.0.0")
        monitor.record_request(100.0, success=True)
        monitor.record_request(150.0, success=False)
        
        report = monitor.get_health_report()
        assert report.error_count == 1


class TestDeploymentValidator:
    """Test DeploymentValidator functionality."""
    
    def test_add_check(self):
        """Test adding deployment check."""
        validator = DeploymentValidator()
        assert validator.add_check("db_connection", lambda: True)
    
    def test_validate_deployment(self):
        """Test deployment validation."""
        validator = DeploymentValidator()
        validator.add_check("db_connection", lambda: True)
        validator.add_check("cache_connection", lambda: True)
        
        all_passed, results = validator.validate_deployment()
        assert all_passed


class TestDocumentationChecker:
    """Test DocumentationChecker functionality."""
    
    def test_add_required_doc(self):
        """Test adding required documentation."""
        checker = DocumentationChecker()
        assert checker.add_required_doc("README.md")
    
    def test_documentation_status_incomplete(self):
        """Test incomplete documentation status."""
        checker = DocumentationChecker()
        checker.add_required_doc("README.md")
        
        complete, required, missing = checker.get_documentation_status()
        assert not complete
        assert len(missing) == 1
    
    def test_documentation_status_complete(self):
        """Test complete documentation status."""
        checker = DocumentationChecker()
        checker.add_required_doc("README.md")
        checker.document_available("README.md")
        
        complete, required, missing = checker.get_documentation_status()
        assert complete
        assert len(missing) == 0


class TestBackupManager:
    """Test BackupManager functionality."""
    
    def test_create_backup(self):
        """Test creating backup."""
        manager = BackupManager("/backups")
        data = {"key": "value"}
        
        assert manager.create_backup("backup1", data)
    
    def test_restore_backup(self):
        """Test restoring backup."""
        manager = BackupManager("/backups")
        data = {"key": "value"}
        manager.create_backup("backup1", data)
        
        restored = manager.restore_backup("backup1")
        assert restored == data
    
    def test_list_backups(self):
        """Test listing backups."""
        manager = BackupManager("/backups")
        manager.create_backup("backup1", {"a": 1})
        manager.create_backup("backup2", {"b": 2})
        
        backups = manager.list_backups()
        assert len(backups) == 2
    
    def test_verify_backup_integrity(self):
        """Test backup integrity verification."""
        manager = BackupManager("/backups")
        manager.create_backup("backup1", {"data": "test"})
        
        assert manager.verify_backup_integrity("backup1")


class TestRolloutManager:
    """Test RolloutManager functionality."""
    
    def test_start_canary_rollout(self):
        """Test starting canary rollout."""
        manager = RolloutManager()
        assert manager.start_canary_rollout("2.0.0", 10)
    
    def test_complete_rollout(self):
        """Test completing rollout."""
        manager = RolloutManager()
        manager.start_canary_rollout("2.0.0", 10)
        
        assert manager.complete_rollout("2.0.0")
    
    def test_rollback(self):
        """Test rollback."""
        manager = RolloutManager()
        manager.start_canary_rollout("2.0.0", 10)
        
        assert manager.rollback()
    
    def test_get_rollout_status(self):
        """Test getting rollout status."""
        manager = RolloutManager()
        manager.start_canary_rollout("2.0.0", 10)
        
        status = manager.get_rollout_status()
        assert status["state"] == "canary"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
