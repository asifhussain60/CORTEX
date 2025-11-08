"""Test suite health validator."""

import os
import subprocess
from pathlib import Path
from typing import Dict, Any
from .base_validator import BaseHealthValidator


class TestValidator(BaseHealthValidator):
    """Validator for CORTEX internal test suite."""
    
    def __init__(self, pass_rate_threshold: float = 0.85):
        """
        Initialize test validator.
        
        Args:
            pass_rate_threshold: Minimum acceptable test pass rate (0.0-1.0)
        """
        self.pass_rate_threshold = pass_rate_threshold
    
    def get_risk_level(self) -> str:
        """Test failures are high risk."""
        return "high"
    
    def check(self) -> Dict[str, Any]:
        """
        Check CORTEX internal test suite pass rate.
        
        ISOLATION: This ONLY tests CORTEX's internal health, never the target
        application's tests. Runs from CORTEX root with isolated environment.
        """
        try:
            # Get CORTEX root directory (3 levels up from validators directory)
            cortex_root = Path(__file__).parent.parent.parent.parent
            
            # Create isolated environment for CORTEX tests
            test_env = os.environ.copy()
            test_env['CORTEX_INTERNAL_TEST'] = 'true'
            test_env['PYTEST_CURRENT_TEST'] = ''  # Clear any target app pytest state
            
            # Run CORTEX tests ONLY - explicit path prevents target app test discovery
            result = subprocess.run(
                ["python3", "-m", "pytest", "tests/", "--tb=no", "-q"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(cortex_root),
                env=test_env
            )
            
            # Parse output for pass/fail counts
            output = result.stdout + result.stderr
            passed = 0
            failed = 0
            
            if "passed" in output:
                parts = output.split("passed")[0].split()
                if parts:
                    try:
                        passed = int(parts[-1])
                    except ValueError:
                        pass
            
            if "failed" in output:
                parts = output.split("failed")[0].split()
                if parts:
                    try:
                        failed = int(parts[-1])
                    except ValueError:
                        pass
            
            total = passed + failed
            pass_rate = passed / total if total > 0 else 0.0
            status = "pass" if pass_rate >= self.pass_rate_threshold else "fail"
            
            result_data = {
                "status": status,
                "passed": passed,
                "failed": failed,
                "total": total,
                "pass_rate": round(pass_rate, 3),
                "threshold": self.pass_rate_threshold,
                "details": [],
                "errors": [],
                "warnings": []
            }
            
            if status == "fail":
                result_data["errors"].append(
                    f"Test pass rate {pass_rate:.1%} below threshold {self.pass_rate_threshold:.1%}"
                )
            
            return result_data
            
        except subprocess.TimeoutExpired:
            return {
                "status": "fail",
                "details": [],
                "errors": ["Test execution timed out (>30s)"],
                "warnings": []
            }
        except Exception as e:
            return {
                "status": "fail",
                "details": [],
                "errors": [f"Test check failed: {str(e)}"],
                "warnings": []
            }
