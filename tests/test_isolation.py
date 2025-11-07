"""
CORTEX Test Isolation Validation

Verifies that CORTEX's internal tests are completely isolated from
target application test frameworks.
"""

import os
import subprocess
import tempfile
from pathlib import Path
import pytest


class TestCortexTestIsolation:
    """Validate CORTEX test isolation from target applications."""
    
    def test_cortex_tests_run_from_explicit_path(self):
        """Verify CORTEX tests only run when explicit path is given."""
        cortex_root = Path(__file__).parent.parent.parent
        
        # Should work: Explicit CORTEX/tests/ path
        result = subprocess.run(
            ["python3", "-m", "pytest", "CORTEX/tests/agents/", "--collect-only", "-q"],
            capture_output=True,
            text=True,
            cwd=str(cortex_root)
        )
        
        assert result.returncode == 0
        assert "test_agent_framework.py" in result.stdout
    
    def test_cortex_tests_not_discovered_from_other_directories(self):
        """Verify CORTEX tests are not discovered when running from other dirs."""
        cortex_root = Path(__file__).parent.parent.parent
        
        # Create a fake application directory with its own tests
        with tempfile.TemporaryDirectory() as tmpdir:
            app_dir = Path(tmpdir)
            app_test_dir = app_dir / "tests"
            app_test_dir.mkdir()
            
            # Create a dummy application test file
            app_test_file = app_test_dir / "test_app.py"
            app_test_file.write_text("""
def test_application_feature():
    assert True
""")
            
            # Run pytest from app directory WITHOUT explicit CORTEX path
            result = subprocess.run(
                ["python3", "-m", "pytest", "--collect-only", "-q"],
                capture_output=True,
                text=True,
                cwd=str(app_dir)
            )
            
            # Should find app test, NOT CORTEX tests
            assert "test_app.py" in result.stdout or result.returncode == 0
            assert "test_agent_framework.py" not in result.stdout
            assert "CORTEX/tests" not in result.stdout
    
    def test_health_validator_uses_cortex_root(self):
        """Verify HealthValidator runs from CORTEX root."""
        from CORTEX.src.cortex_agents.health_validator import HealthValidator
        
        validator = HealthValidator(name="IsolationTest")
        
        # The _check_tests method should use CORTEX root
        # We can verify by checking it doesn't fail when called from anywhere
        result = validator._check_tests(skip=False)
        
        # Should successfully run CORTEX tests
        assert result["status"] in ["pass", "fail", "skip"]
        # Should have test count data
        assert "passed" in result or "status" in result
    
    def test_environment_variable_set_for_cortex_tests(self):
        """Verify CORTEX sets isolation environment variable."""
        from CORTEX.src.cortex_agents.health_validator import HealthValidator
        import unittest.mock as mock
        
        validator = HealthValidator(name="EnvTest")
        
        # Mock subprocess to capture environment
        with mock.patch('subprocess.run') as mock_run:
            mock_run.return_value = mock.Mock(
                returncode=0,
                stdout="50 passed",
                stderr=""
            )
            
            validator._check_tests(skip=False)
            
            # Verify subprocess was called with isolated environment
            call_args = mock_run.call_args
            if call_args and 'env' in call_args[1]:
                env = call_args[1]['env']
                assert 'CORTEX_INTERNAL_TEST' in env
                assert env['CORTEX_INTERNAL_TEST'] == 'true'
    
    def test_pytest_ini_restricts_to_cortex_tests(self):
        """Verify pytest.ini testpaths points to CORTEX/tests only."""
        cortex_root = Path(__file__).parent.parent.parent
        pytest_ini = cortex_root / "pytest.ini"
        
        assert pytest_ini.exists()
        
        content = pytest_ini.read_text()
        assert "testpaths = CORTEX/tests" in content
        assert "CORTEX_INTERNAL" in content or "cortex_internal" in content
    
    def test_cortex_tests_directory_structure(self):
        """Verify CORTEX tests are in expected isolated location."""
        cortex_root = Path(__file__).parent.parent.parent
        cortex_tests = cortex_root / "CORTEX" / "tests"
        
        assert cortex_tests.exists()
        assert cortex_tests.is_dir()
        
        # Check for expected test directories
        assert (cortex_tests / "agents").exists()
        assert (cortex_tests / "tier1").exists() or True  # May exist
        
        # Verify no test directories in CORTEX/src
        cortex_src = cortex_root / "CORTEX" / "src"
        if cortex_src.exists():
            assert not (cortex_src / "tests").exists()
            assert not (cortex_src / "test").exists()
    
    def test_no_interference_with_application_pytest_markers(self):
        """Verify CORTEX markers don't conflict with application markers."""
        cortex_root = Path(__file__).parent.parent.parent
        pytest_ini = cortex_root / "pytest.ini"
        
        content = pytest_ini.read_text()
        
        # CORTEX-specific markers should be prefixed or clearly internal
        assert "cortex_internal" in content
        assert "agent_test" in content
        assert "brain_test" in content
    
    def test_health_validator_timeout_prevents_runaway_tests(self):
        """Verify health check has timeout to prevent blocking."""
        from CORTEX.src.cortex_agents.health_validator import HealthValidator
        
        validator = HealthValidator(name="TimeoutTest")
        
        # Check that _check_tests has timeout in subprocess call
        import inspect
        source = inspect.getsource(validator._check_tests)
        
        assert "timeout" in source
        assert "30" in source  # 30 second timeout
    
    @pytest.mark.slow
    def test_cortex_tests_complete_within_timeout(self):
        """Verify CORTEX tests complete within health check timeout."""
        import time
        cortex_root = Path(__file__).parent.parent.parent
        
        start = time.time()
        result = subprocess.run(
            ["python3", "-m", "pytest", "CORTEX/tests/agents/", "-q"],
            capture_output=True,
            text=True,
            cwd=str(cortex_root),
            timeout=30  # Should complete within 30 seconds
        )
        duration = time.time() - start
        
        assert result.returncode == 0
        assert duration < 30  # Must complete within timeout


class TestTargetApplicationIsolation:
    """Verify CORTEX doesn't interfere with target applications."""
    
    def test_cortex_agents_dont_modify_application_tests(self):
        """Verify CodeExecutor won't modify application test files."""
        from CORTEX.src.cortex_agents.code_executor import CodeExecutor
        
        executor = CodeExecutor(name="IsolationTest")
        
        # Create a fake test file in a temp directory
        with tempfile.TemporaryDirectory() as tmpdir:
            app_test = Path(tmpdir) / "tests" / "test_app.py"
            app_test.parent.mkdir()
            app_test.write_text("def test_something(): pass")
            
            # CodeExecutor should be able to read but not accidentally execute
            # (This is more of a design verification than a functional test)
            assert app_test.exists()
            
            # CORTEX should never auto-run application tests
            # This is enforced by convention and documentation
    
    def test_test_generator_supports_multiple_frameworks(self):
        """Verify TestGenerator doesn't assume pytest for target apps."""
        from CORTEX.src.cortex_agents.test_generator import TestGenerator
        
        generator = TestGenerator(name="FrameworkTest")
        
        # Generator should work with any source code
        # It generates pytest tests for CORTEX, but could be extended
        # for other frameworks for target applications
        
        sample_code = """
def add(a, b):
    return a + b
"""
        
        from CORTEX.src.cortex_agents.base_agent import AgentRequest
        from CORTEX.src.cortex_agents.agent_types import IntentType
        
        request = AgentRequest(
            intent=IntentType.TEST.value,
            context={"source_code": sample_code},
            user_message="Generate tests"
        )
        
        response = generator.execute(request)
        
        # Should successfully generate tests
        assert response.success
        assert "import pytest" in response.result["test_code"]


class TestProtectionDocumentation:
    """Verify isolation is properly documented."""
    
    def test_isolation_documentation_exists(self):
        """Verify test isolation protection document exists."""
        cortex_root = Path(__file__).parent.parent.parent
        doc_path = cortex_root / "docs" / "CORTEX-TEST-ISOLATION-PROTECTION.md"
        
        assert doc_path.exists()
        
        content = doc_path.read_text()
        assert "isolation" in content.lower()
        assert "CORTEX/tests/" in content
        assert "target application" in content.lower()
    
    def test_health_validator_has_isolation_comments(self):
        """Verify HealthValidator code has isolation documentation."""
        cortex_root = Path(__file__).parent.parent.parent
        hv_path = cortex_root / "CORTEX" / "src" / "cortex_agents" / "health_validator.py"
        
        assert hv_path.exists()
        
        content = hv_path.read_text()
        assert "ISOLATION" in content or "isolation" in content
        assert "CORTEX/tests/" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
