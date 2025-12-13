"""Tests for Integration Testing Orchestrator."""
import pytest
from src.operations.utilities.integration_testing_orchestrator import (
    IntegrationTestingOrchestrator, TestEnvironment, TestResult
)

@pytest.fixture
def orchestrator():
    return IntegrationTestingOrchestrator()

class TestIntegrationTesting:
    def test_setup_environment(self, orchestrator):
        env = orchestrator.setup_environment("test-env")
        assert isinstance(env, TestEnvironment)
        assert env.name == "test-env"

    def test_execute_tests(self, orchestrator):
        env = TestEnvironment(name="test")
        result = orchestrator.execute_tests(env, ["test1", "test2"])
        assert isinstance(result, TestResult)
        assert result.total_tests >= 0

    def test_teardown_environment(self, orchestrator):
        env = TestEnvironment(name="test")
        success = orchestrator.teardown_environment(env)
        assert isinstance(success, bool)

    def test_aggregate_results(self, orchestrator):
        results = [
            TestResult(total_tests=5, passed=5, failed=0),
            TestResult(total_tests=3, passed=2, failed=1)
        ]
        summary = orchestrator.aggregate_results(results)
        assert summary['total'] == 8
        assert summary['passed'] == 7
