"""
HealthValidator Agent

Validates system health before executing risky operations.
Checks database integrity, test pass rates, git status, and performance metrics.

The HealthValidator is the safety net that prevents operations from starting
when the system is in an unhealthy state.
"""

import os
import sqlite3
import subprocess
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
from CORTEX.src.cortex_agents.base_agent import BaseAgent, AgentRequest, AgentResponse
from CORTEX.src.cortex_agents.agent_types import IntentType


class HealthValidator(BaseAgent):
    """
    Validates system health before risky operations.
    
    The HealthValidator performs comprehensive health checks including:
    - Database integrity verification
    - Test suite pass rate validation
    - Git repository status
    - Disk space availability
    - Performance metric thresholds
    
    Features:
    - Multi-tier database checks
    - Test execution and validation
    - Git status monitoring
    - Resource availability checks
    - Risk level assessment
    
    Example:
        validator = HealthValidator(name="Validator", tier1_api, tier2_kg, tier3_context)
        
        request = AgentRequest(
            intent="health_check",
            context={},
            user_message="Check if system is ready for deployment"
        )
        
        response = validator.execute(request)
        # Returns: {
        #   "status": "healthy",
        #   "checks": {
        #     "databases": "pass",
        #     "tests": "pass",
        #     "git": "pass"
        #   },
        #   "warnings": [],
        #   "errors": []
        # }
    """
    
    def __init__(self, name: str, tier1_api=None, tier2_kg=None, tier3_context=None):
        """Initialize HealthValidator with tier APIs."""
        super().__init__(name, tier1_api, tier2_kg, tier3_context)
        
        # Health check thresholds
        self.THRESHOLDS = {
            "test_pass_rate": 0.95,  # 95% tests must pass
            "disk_space_gb": 1.0,     # 1GB minimum free space
            "db_size_mb": 500,        # 500MB max database size
            "max_uncommitted": 50     # 50 uncommitted changes is concerning
        }
        
        # Risk levels for different check failures
        self.RISK_LEVELS = {
            "databases": "critical",
            "tests": "high",
            "git": "medium",
            "disk_space": "high",
            "performance": "medium"
        }
    
    def can_handle(self, request: AgentRequest) -> bool:
        """
        Check if this agent can handle the request.
        
        Args:
            request: The agent request
        
        Returns:
            True if intent is health_check or validate
        """
        valid_intents = [
            IntentType.HEALTH_CHECK.value,
            IntentType.VALIDATE.value,
            "health",
            "check",
            "validate"
        ]
        return request.intent.lower() in valid_intents
    
    def execute(self, request: AgentRequest) -> AgentResponse:
        """
        Perform system health validation.
        
        Args:
            request: The agent request
        
        Returns:
            AgentResponse with health status and check results
        """
        try:
            self.log_request(request)
            self.logger.info("Starting health validation")
            
            # Perform all health checks
            check_results = {
                "databases": self._check_databases(),
                "tests": self._check_tests(request.context.get("skip_tests", False)),
                "git": self._check_git_status(),
                "disk_space": self._check_disk_space(),
                "performance": self._check_performance()
            }
            
            # Analyze results
            status, warnings, errors = self._analyze_results(check_results)
            
            # Calculate overall risk
            risk_level = self._calculate_risk(check_results, errors)
            
            # Log to Tier 1 if available
            if self.tier1 and request.conversation_id:
                self.tier1.process_message(
                    request.conversation_id,
                    "agent",
                    f"HealthValidator: System {status}, {len(errors)} errors, {len(warnings)} warnings"
                )
            
            response = AgentResponse(
                success=(status == "healthy"),
                result={
                    "status": status,
                    "checks": check_results,
                    "warnings": warnings,
                    "errors": errors,
                    "risk_level": risk_level,
                    "timestamp": datetime.now().isoformat()
                },
                message=self._format_message(status, check_results, warnings, errors),
                agent_name=self.name,
                metadata={
                    "total_checks": len(check_results),
                    "passed_checks": sum(1 for r in check_results.values() if r.get("status") == "pass"),
                    "risk_level": risk_level
                },
                next_actions=self._suggest_actions(status, errors, warnings)
            )
            
            self.log_response(response)
            return response
            
        except Exception as e:
            self.logger.error(f"Health validation failed: {str(e)}")
            return AgentResponse(
                success=False,
                result=None,
                message=f"Health validation failed: {str(e)}",
                agent_name=self.name
            )
    
    def _check_databases(self) -> Dict[str, Any]:
        """
        Check all tier databases for integrity.
        
        Returns:
            Database health check results
        """
        results = {
            "status": "pass",
            "details": [],
            "errors": []
        }
        
        try:
            # Check Tier 1 database
            if self.tier1:
                tier1_check = self._check_single_database(
                    getattr(self.tier1, 'db_path', None),
                    "Tier 1"
                )
                results["details"].append(tier1_check)
                if tier1_check["status"] == "fail":
                    results["status"] = "fail"
                    results["errors"].append(tier1_check.get("error", "Tier 1 check failed"))
            
            # Check Tier 2 database
            if self.tier2:
                tier2_check = self._check_single_database(
                    getattr(self.tier2, 'db_path', None),
                    "Tier 2"
                )
                results["details"].append(tier2_check)
                if tier2_check["status"] == "fail":
                    results["status"] = "fail"
                    results["errors"].append(tier2_check.get("error", "Tier 2 check failed"))
            
            # Check Tier 3 database
            if self.tier3:
                tier3_check = self._check_single_database(
                    getattr(self.tier3, 'db_path', None),
                    "Tier 3"
                )
                results["details"].append(tier3_check)
                if tier3_check["status"] == "fail":
                    results["status"] = "fail"
                    results["errors"].append(tier3_check.get("error", "Tier 3 check failed"))
            
        except Exception as e:
            results["status"] = "fail"
            results["errors"].append(f"Database check failed: {str(e)}")
        
        return results
    
    def _check_single_database(self, db_path: Optional[str], name: str) -> Dict[str, Any]:
        """
        Check a single database file.
        
        Args:
            db_path: Path to database file
            name: Database name for reporting
        
        Returns:
            Check results for this database
        """
        if not db_path:
            return {
                "name": name,
                "status": "skip",
                "message": f"{name} database path not available"
            }
        
        try:
            # Check file exists
            if not os.path.exists(db_path):
                return {
                    "name": name,
                    "status": "fail",
                    "error": f"{name} database file not found: {db_path}"
                }
            
            # Check file size
            size_mb = os.path.getsize(db_path) / (1024 * 1024)
            if size_mb > self.THRESHOLDS["db_size_mb"]:
                return {
                    "name": name,
                    "status": "warn",
                    "size_mb": round(size_mb, 2),
                    "error": f"{name} database size ({size_mb:.1f}MB) exceeds threshold"
                }
            
            # Check database integrity
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check")
            integrity = cursor.fetchone()[0]
            conn.close()
            
            if integrity != "ok":
                return {
                    "name": name,
                    "status": "fail",
                    "error": f"{name} database integrity check failed: {integrity}"
                }
            
            return {
                "name": name,
                "status": "pass",
                "size_mb": round(size_mb, 2)
            }
            
        except Exception as e:
            return {
                "name": name,
                "status": "fail",
                "error": f"{name} database check error: {str(e)}"
            }
    
    def _check_tests(self, skip: bool = False) -> Dict[str, Any]:
        """
        Check CORTEX internal test suite pass rate.
        
        ISOLATION: This ONLY tests CORTEX's internal health, never the target
        application's tests. Runs from CORTEX root with isolated environment.
        
        Args:
            skip: Whether to skip test execution
        
        Returns:
            Test health check results
        """
        if skip:
            return {
                "status": "skip",
                "message": "Test check skipped by request"
            }
        
        try:
            # Get CORTEX root directory (3 levels up from this file)
            # This ensures we always run from CORTEX root, not target app
            cortex_root = Path(__file__).parent.parent.parent
            
            # Create isolated environment for CORTEX tests
            test_env = os.environ.copy()
            test_env['CORTEX_INTERNAL_TEST'] = 'true'
            test_env['PYTEST_CURRENT_TEST'] = ''  # Clear any target app pytest state
            
            # Run CORTEX tests ONLY - explicit path prevents target app test discovery
            result = subprocess.run(
                ["python3", "-m", "pytest", "CORTEX/tests/", "--tb=no", "-q"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(cortex_root),  # Always CORTEX root, never target app
                env=test_env  # Isolated environment
            )
            
            # Parse output for pass/fail counts
            output = result.stdout + result.stderr
            
            # Simple parsing - look for "passed" and "failed"
            passed = 0
            failed = 0
            
            if "passed" in output:
                # Extract number before "passed"
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
            
            status = "pass" if pass_rate >= self.THRESHOLDS["test_pass_rate"] else "fail"
            
            return {
                "status": status,
                "passed": passed,
                "failed": failed,
                "total": total,
                "pass_rate": round(pass_rate, 3),
                "threshold": self.THRESHOLDS["test_pass_rate"]
            }
            
        except subprocess.TimeoutExpired:
            return {
                "status": "fail",
                "error": "Test execution timed out (>30s)"
            }
        except Exception as e:
            return {
                "status": "fail",
                "error": f"Test check failed: {str(e)}"
            }
    
    def _check_git_status(self) -> Dict[str, Any]:
        """
        Check git repository status.
        
        Returns:
            Git health check results
        """
        try:
            # Check if we're in a git repo
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                return {
                    "status": "skip",
                    "message": "Not a git repository"
                }
            
            # Get uncommitted changes count
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            uncommitted_lines = result.stdout.strip().split("\n") if result.stdout.strip() else []
            uncommitted_count = len(uncommitted_lines)
            
            # Determine status
            if uncommitted_count == 0:
                status = "pass"
                message = "No uncommitted changes"
            elif uncommitted_count < self.THRESHOLDS["max_uncommitted"]:
                status = "pass"
                message = f"{uncommitted_count} uncommitted changes (acceptable)"
            else:
                status = "warn"
                message = f"{uncommitted_count} uncommitted changes (high)"
            
            return {
                "status": status,
                "uncommitted_count": uncommitted_count,
                "message": message
            }
            
        except Exception as e:
            return {
                "status": "fail",
                "error": f"Git status check failed: {str(e)}"
            }
    
    def _check_disk_space(self) -> Dict[str, Any]:
        """
        Check available disk space.
        
        Returns:
            Disk space check results
        """
        try:
            # Get current working directory disk usage
            cwd = Path.cwd()
            stat = os.statvfs(cwd)
            
            # Calculate free space in GB
            free_gb = (stat.f_bavail * stat.f_frsize) / (1024 ** 3)
            total_gb = (stat.f_blocks * stat.f_frsize) / (1024 ** 3)
            used_percent = ((total_gb - free_gb) / total_gb) * 100
            
            status = "pass" if free_gb >= self.THRESHOLDS["disk_space_gb"] else "fail"
            
            return {
                "status": status,
                "free_gb": round(free_gb, 2),
                "total_gb": round(total_gb, 2),
                "used_percent": round(used_percent, 1),
                "threshold_gb": self.THRESHOLDS["disk_space_gb"]
            }
            
        except Exception as e:
            return {
                "status": "fail",
                "error": f"Disk space check failed: {str(e)}"
            }
    
    def _check_performance(self) -> Dict[str, Any]:
        """
        Check performance metrics from Tier 3.
        
        Returns:
            Performance check results
        """
        if not self.tier3:
            return {
                "status": "skip",
                "message": "Tier 3 not available"
            }
        
        try:
            # Get performance metrics from Tier 3
            summary = self.tier3.get_context_summary()
            
            # Check if metrics are within acceptable ranges
            # (This is a simple example - real implementation would be more sophisticated)
            metrics = {
                "status": "pass",
                "metrics": {}
            }
            
            if "average_velocity" in summary:
                velocity = summary["average_velocity"]
                metrics["metrics"]["velocity"] = velocity
                # Velocity below 5 is concerning
                if velocity is not None and velocity < 5:
                    metrics["status"] = "warn"
                    metrics["warning"] = f"Low velocity: {velocity}"
            
            return metrics
            
        except Exception as e:
            return {
                "status": "fail",
                "error": f"Performance check failed: {str(e)}"
            }
    
    def _analyze_results(
        self,
        check_results: Dict[str, Dict[str, Any]]
    ) -> tuple[str, List[str], List[str]]:
        """
        Analyze check results to determine overall status.
        
        Args:
            check_results: Results from all checks
        
        Returns:
            Tuple of (status, warnings, errors)
        """
        warnings = []
        errors = []
        
        for check_name, result in check_results.items():
            status = result.get("status", "unknown")
            
            if status == "fail":
                error_msg = result.get("error", f"{check_name} check failed")
                errors.append(f"{check_name}: {error_msg}")
            elif status == "warn":
                warning_msg = result.get("message", result.get("error", f"{check_name} warning"))
                warnings.append(f"{check_name}: {warning_msg}")
            
            # Check for specific error fields in details
            if "errors" in result and result["errors"]:
                for err in result["errors"]:
                    if err:  # Skip None/empty errors
                        errors.append(f"{check_name}: {err}")
        
        # Determine overall status
        if errors:
            overall_status = "unhealthy"
        elif warnings:
            overall_status = "degraded"
        else:
            overall_status = "healthy"
        
        return overall_status, warnings, errors
    
    def _calculate_risk(
        self,
        check_results: Dict[str, Dict[str, Any]],
        errors: List[str]
    ) -> str:
        """
        Calculate overall risk level.
        
        Args:
            check_results: Results from all checks
            errors: List of error messages
        
        Returns:
            Risk level: "low", "medium", "high", or "critical"
        """
        if not errors:
            return "low"
        
        # Check for critical failures
        for check_name, result in check_results.items():
            if result.get("status") == "fail":
                risk = self.RISK_LEVELS.get(check_name, "medium")
                if risk == "critical":
                    return "critical"
        
        # Count high-risk failures
        high_risk_count = sum(
            1 for check_name, result in check_results.items()
            if result.get("status") == "fail" and self.RISK_LEVELS.get(check_name) == "high"
        )
        
        if high_risk_count >= 2:
            return "high"
        elif high_risk_count == 1:
            return "medium"
        else:
            return "low"
    
    def _format_message(
        self,
        status: str,
        check_results: Dict[str, Dict[str, Any]],
        warnings: List[str],
        errors: List[str]
    ) -> str:
        """
        Format a human-readable status message.
        
        Args:
            status: Overall status
            check_results: Results from all checks
            warnings: Warning messages
            errors: Error messages
        
        Returns:
            Formatted message string
        """
        passed = sum(1 for r in check_results.values() if r.get("status") == "pass")
        total = len(check_results)
        
        if status == "healthy":
            return f"System healthy: {passed}/{total} checks passed"
        elif status == "degraded":
            return f"System degraded: {passed}/{total} checks passed, {len(warnings)} warnings"
        else:
            return f"System unhealthy: {passed}/{total} checks passed, {len(errors)} errors"
    
    def _suggest_actions(
        self,
        status: str,
        errors: List[str],
        warnings: List[str]
    ) -> List[str]:
        """
        Suggest remediation actions.
        
        Args:
            status: Overall system status
            errors: Error messages
            warnings: Warning messages
        
        Returns:
            List of suggested actions
        """
        actions = []
        
        if status == "healthy":
            actions.append("System ready for operations")
            return actions
        
        # Database-related actions
        if any("database" in e.lower() for e in errors):
            actions.append("Run database integrity repair")
            actions.append("Check database file permissions")
        
        # Test-related actions
        if any("test" in e.lower() for e in errors):
            actions.append("Fix failing tests before proceeding")
            actions.append("Review recent code changes")
        
        # Git-related actions
        if any("git" in w.lower() for w in warnings):
            actions.append("Consider committing changes")
        
        # Disk space actions
        if any("disk" in e.lower() for e in errors):
            actions.append("Free up disk space")
            actions.append("Clean temporary files")
        
        if not actions:
            actions.append("Review errors and warnings")
            actions.append("Address issues before continuing")
        
        return actions
