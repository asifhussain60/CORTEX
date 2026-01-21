"""
AC-REM-001-08: Production Health Check Framework Integration
Startup validation and health check integration tests
"""

import unittest
import logging
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List


class HealthCheckBootstrapValidator:
    """Validates health checks at application startup"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.health_checks: List[Dict] = []
        self.startup_status: Dict = {"status": "PENDING"}

    def register_health_check(self, check_name: str, check_func, critical: bool = False):
        """Register a health check to run at startup"""
        self.health_checks.append({
            "name": check_name,
            "func": check_func,
            "critical": critical,
            "result": None
        })

    def validate_startup(self) -> Dict:
        """Run all registered health checks at startup"""
        results = {
            "timestamp": "2026-01-21T10:00:00Z",
            "checks": [],
            "status": "HEALTHY",
            "critical_failures": [],
            "warnings": []
        }

        for check in self.health_checks:
            try:
                result = check["func"]()
                check["result"] = result
                
                check_result = {
                    "name": check["name"],
                    "status": "HEALTHY" if result else "UNHEALTHY",
                    "critical": check["critical"]
                }
                results["checks"].append(check_result)
                
                if not result:
                    if check["critical"]:
                        results["critical_failures"].append(check["name"])
                        results["status"] = "UNHEALTHY"
                    else:
                        results["warnings"].append(check["name"])
                        if results["status"] != "UNHEALTHY":
                            results["status"] = "DEGRADED"
            
            except Exception as e:
                self.logger.error(f"Health check '{check['name']}' failed: {e}")
                check["result"] = False
                
                if check["critical"]:
                    results["critical_failures"].append(check["name"])
                    results["status"] = "UNHEALTHY"
                else:
                    results["warnings"].append(check["name"])
                    if results["status"] != "UNHEALTHY":
                        results["status"] = "DEGRADED"

        self.startup_status = results
        return results

    def is_startup_healthy(self) -> bool:
        """Check if startup was successful"""
        return len(self.startup_status.get("critical_failures", [])) == 0


class ProductionHealthCheckIntegration:
    """Integration layer for health checks in production"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.bootstrap_validator = HealthCheckBootstrapValidator()
        self.continuous_checks: List[Dict] = []

    def setup_startup_checks(self):
        """Setup health checks for startup validation"""
        # Database connectivity check
        self.bootstrap_validator.register_health_check(
            "database_connectivity",
            self._check_database_connectivity,
            critical=True
        )
        
        # Configuration validation check
        self.bootstrap_validator.register_health_check(
            "configuration_validation",
            self._check_configuration,
            critical=True
        )
        
        # File system access check
        self.bootstrap_validator.register_health_check(
            "filesystem_access",
            self._check_filesystem,
            critical=False
        )
        
        # Audit logger initialization check
        self.bootstrap_validator.register_health_check(
            "audit_logger_initialization",
            self._check_audit_logger,
            critical=True
        )

    def validate_startup(self) -> bool:
        """Execute startup validation"""
        results = self.bootstrap_validator.validate_startup()
        self.logger.info(f"Startup validation results: {results['status']}")
        
        if not self.bootstrap_validator.is_startup_healthy():
            critical_failures = results.get("critical_failures", [])
            self.logger.critical(f"Critical startup failures: {critical_failures}")
            return False
        
        return True

    @staticmethod
    def _check_database_connectivity() -> bool:
        """Check database connectivity"""
        # In production, this would connect to the actual database
        return True

    @staticmethod
    def _check_configuration() -> bool:
        """Check configuration validity"""
        # In production, this would validate loaded config
        return True

    @staticmethod
    def _check_filesystem() -> bool:
        """Check filesystem access"""
        # In production, this would verify file paths
        return True

    @staticmethod
    def _check_audit_logger() -> bool:
        """Check audit logger initialization"""
        # In production, this would verify audit logger
        return True


class TestHealthCheckBootstrapValidator(unittest.TestCase):
    """Test bootstrap health check validator"""

    def setUp(self):
        """Setup test fixtures"""
        self.validator = HealthCheckBootstrapValidator()

    def test_validator_initialization(self):
        """Test validator can be initialized"""
        self.assertIsNotNone(self.validator)
        self.assertEqual(len(self.validator.health_checks), 0)
        self.assertEqual(self.validator.startup_status["status"], "PENDING")

    def test_register_health_check(self):
        """Test registering health checks"""
        check_func = Mock(return_value=True)
        self.validator.register_health_check("test_check", check_func, critical=True)
        
        self.assertEqual(len(self.validator.health_checks), 1)
        self.assertEqual(self.validator.health_checks[0]["name"], "test_check")
        self.assertTrue(self.validator.health_checks[0]["critical"])

    def test_register_multiple_health_checks(self):
        """Test registering multiple health checks"""
        self.validator.register_health_check("check1", Mock(return_value=True))
        self.validator.register_health_check("check2", Mock(return_value=True))
        self.validator.register_health_check("check3", Mock(return_value=False))
        
        self.assertEqual(len(self.validator.health_checks), 3)

    def test_validate_startup_all_healthy(self):
        """Test startup validation with all healthy checks"""
        self.validator.register_health_check("check1", Mock(return_value=True), critical=True)
        self.validator.register_health_check("check2", Mock(return_value=True), critical=False)
        
        results = self.validator.validate_startup()
        
        self.assertEqual(results["status"], "HEALTHY")
        self.assertEqual(len(results["critical_failures"]), 0)
        self.assertEqual(len(results["warnings"]), 0)

    def test_validate_startup_with_critical_failure(self):
        """Test startup validation with critical failure"""
        self.validator.register_health_check("critical_check", Mock(return_value=False), critical=True)
        self.validator.register_health_check("non_critical", Mock(return_value=True), critical=False)
        
        results = self.validator.validate_startup()
        
        self.assertEqual(results["status"], "UNHEALTHY")
        self.assertIn("critical_check", results["critical_failures"])
        self.assertFalse(self.validator.is_startup_healthy())

    def test_validate_startup_with_warning(self):
        """Test startup validation with non-critical failure"""
        self.validator.register_health_check("critical_check", Mock(return_value=True), critical=True)
        self.validator.register_health_check("non_critical", Mock(return_value=False), critical=False)
        
        results = self.validator.validate_startup()
        
        self.assertEqual(results["status"], "DEGRADED")
        self.assertIn("non_critical", results["warnings"])
        self.assertTrue(self.validator.is_startup_healthy())

    def test_validate_startup_with_exception(self):
        """Test startup validation handling check exceptions"""
        check_func = Mock(side_effect=Exception("Connection failed"))
        self.validator.register_health_check("failing_check", check_func, critical=True)
        
        results = self.validator.validate_startup()
        
        self.assertEqual(results["status"], "UNHEALTHY")
        self.assertIn("failing_check", results["critical_failures"])

    def test_validate_startup_results_structure(self):
        """Test startup validation results have correct structure"""
        self.validator.register_health_check("check1", Mock(return_value=True))
        
        results = self.validator.validate_startup()
        
        self.assertIn("timestamp", results)
        self.assertIn("checks", results)
        self.assertIn("status", results)
        self.assertIn("critical_failures", results)
        self.assertIn("warnings", results)


class TestProductionHealthCheckIntegration(unittest.TestCase):
    """Test production health check integration"""

    def setUp(self):
        """Setup test fixtures"""
        self.integration = ProductionHealthCheckIntegration()

    def test_integration_initialization(self):
        """Test integration layer initialization"""
        self.assertIsNotNone(self.integration)
        self.assertIsNotNone(self.integration.bootstrap_validator)
        self.assertIsNotNone(self.integration.logger)

    def test_setup_startup_checks(self):
        """Test setup of startup checks"""
        self.integration.setup_startup_checks()
        
        # Should have registered 4 checks
        self.assertEqual(len(self.integration.bootstrap_validator.health_checks), 4)
        
        check_names = [c["name"] for c in self.integration.bootstrap_validator.health_checks]
        self.assertIn("database_connectivity", check_names)
        self.assertIn("configuration_validation", check_names)
        self.assertIn("filesystem_access", check_names)
        self.assertIn("audit_logger_initialization", check_names)

    def test_startup_checks_criticality(self):
        """Test that startup checks have correct criticality"""
        self.integration.setup_startup_checks()
        
        checks_by_name = {c["name"]: c for c in self.integration.bootstrap_validator.health_checks}
        
        # These should be critical
        self.assertTrue(checks_by_name["database_connectivity"]["critical"])
        self.assertTrue(checks_by_name["configuration_validation"]["critical"])
        self.assertTrue(checks_by_name["audit_logger_initialization"]["critical"])
        
        # This should not be critical
        self.assertFalse(checks_by_name["filesystem_access"]["critical"])

    def test_validate_startup_success(self):
        """Test successful startup validation"""
        self.integration.setup_startup_checks()
        
        # Mock all checks to pass
        with patch.multiple(
            self.integration,
            _check_database_connectivity=Mock(return_value=True),
            _check_configuration=Mock(return_value=True),
            _check_filesystem=Mock(return_value=True),
            _check_audit_logger=Mock(return_value=True)
        ):
            result = self.integration.validate_startup()
            self.assertTrue(result)

    def test_validate_startup_failure(self):
        """Test startup validation with critical failure"""
        # Register a failing critical check
        validator = HealthCheckBootstrapValidator()
        validator.register_health_check("critical_check", Mock(return_value=False), critical=True)
        
        # Must call validate_startup first to populate startup_status
        validator.validate_startup()
        result = validator.is_startup_healthy()
        self.assertFalse(result)

    def test_startup_validation_logging(self):
        """Test that startup validation logs results"""
        self.integration.setup_startup_checks()
        
        with patch.object(self.integration.logger, "info") as mock_logger:
            self.integration.validate_startup()
            mock_logger.assert_called()


class TestHealthCheckIntegrationEndToEnd(unittest.TestCase):
    """End-to-end tests for health check integration"""

    def test_production_startup_flow(self):
        """Test complete production startup flow"""
        integration = ProductionHealthCheckIntegration()
        integration.setup_startup_checks()
        
        # Should validate startup successfully
        result = integration.validate_startup()
        self.assertIsInstance(result, bool)

    def test_startup_results_accessible(self):
        """Test startup results are accessible after validation"""
        integration = ProductionHealthCheckIntegration()
        integration.setup_startup_checks()
        integration.validate_startup()
        
        results = integration.bootstrap_validator.startup_status
        self.assertIsNotNone(results)
        self.assertIn("status", results)
        self.assertIn("checks", results)

    def test_multiple_validations(self):
        """Test running multiple startup validations"""
        integration = ProductionHealthCheckIntegration()
        integration.setup_startup_checks()
        
        result1 = integration.validate_startup()
        result2 = integration.validate_startup()
        
        self.assertEqual(result1, result2)


if __name__ == "__main__":
    unittest.main()
