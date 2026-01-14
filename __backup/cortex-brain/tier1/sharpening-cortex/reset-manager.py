"""
CORTEX 6.0 - Sharpening CORTEX Reset Manager

Purpose: Provides reset capability for all sample applications to enable
         multiple test runs with clean baseline state.

AC Coverage:
- AC-TEST-001: Reset infrastructure for repeatable testing
- AC-INV-002: Test environment management
- AC-QUAL-005: Clean state validation

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import os
import subprocess
import json
import logging
from pathlib import Path
from typing import Dict, List, Literal, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger("cortex.sharpening.reset_manager")


class ResetType(Enum):
    """Types of reset mechanisms supported."""
    SQL_SEED = "sql_seed"
    EF_MIGRATION = "ef_migration"
    GIT_CHECKOUT = "git_checkout"
    DOCKER_COMPOSE = "docker_compose"
    TEST_FIXTURES = "test_fixtures"


@dataclass
class ResetResult:
    """Result of a reset operation."""
    application: str
    success: bool
    reset_type: ResetType
    execution_time_seconds: float
    validation_passed: bool
    error_message: Optional[str] = None
    details: Optional[Dict] = None


class ResetManager:
    """
    Manages reset operations for sharpening-cortex sample applications.
    
    Each application has a specific reset mechanism appropriate for its
    technology stack and complexity.
    """
    
    def __init__(self, sharpening_root: Path):
        """
        Initialize reset manager.
        
        Args:
            sharpening_root: Path to sharpening-cortex directory
        """
        self.root = sharpening_root
        self.logger = logger
        
        # Application reset configurations
        self.reset_configs = {
            "BadMonolith": {
                "type": ResetType.SQL_SEED,
                "path": self.root / "BadMonolith",
                "commands": [
                    "curl http://localhost:5000/api/tasks?action=seed"
                ],
                "validation": self._validate_bad_monolith
            },
            "CleanSolidApp": {
                "type": ResetType.EF_MIGRATION,
                "path": self.root / "CleanSolidApp" / "backend",
                "commands": [
                    "dotnet ef database drop --force",
                    "dotnet ef database update",
                    "curl http://localhost:5001/api/tasks/seed"
                ],
                "validation": self._validate_clean_solid_app
            },
            "_Real": {
                "type": ResetType.GIT_CHECKOUT,
                "path": self.root / "_Real",
                "commands": [
                    "git checkout HEAD -- ."
                ],
                "validation": self._validate_git_clean
            },
            "Cortex-Clean": {
                "type": ResetType.DOCKER_COMPOSE,
                "path": self.root / "Cortex-Clean",
                "commands": [
                    "docker-compose down -v",
                    "docker-compose up -d"
                ],
                "validation": self._validate_docker_health
            },
            "Cortex-SDD": {
                "type": ResetType.TEST_FIXTURES,
                "path": self.root / "Cortex-SDD",
                "commands": [
                    "pytest --fixtures-reset"
                ],
                "validation": self._validate_test_fixtures
            }
        }
    
    def reset_application(self, app_name: str) -> ResetResult:
        """
        Reset a specific application to baseline state.
        
        Args:
            app_name: Name of application to reset
            
        Returns:
            ResetResult with success status and details
        """
        import time
        start_time = time.time()
        
        if app_name not in self.reset_configs:
            return ResetResult(
                application=app_name,
                success=False,
                reset_type=ResetType.GIT_CHECKOUT,  # Default
                execution_time_seconds=0,
                validation_passed=False,
                error_message=f"Unknown application: {app_name}"
            )
        
        config = self.reset_configs[app_name]
        reset_type = config["type"]
        
        self.logger.info(f"Resetting {app_name} using {reset_type.value}")
        
        try:
            # Execute reset commands
            for cmd in config["commands"]:
                self._execute_command(cmd, config["path"])
            
            # Validate reset
            validation_passed = config["validation"]()
            
            execution_time = time.time() - start_time
            
            return ResetResult(
                application=app_name,
                success=True,
                reset_type=reset_type,
                execution_time_seconds=execution_time,
                validation_passed=validation_passed,
                details={"commands_executed": len(config["commands"])}
            )
        
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Reset failed for {app_name}: {e}")
            
            return ResetResult(
                application=app_name,
                success=False,
                reset_type=reset_type,
                execution_time_seconds=execution_time,
                validation_passed=False,
                error_message=str(e)
            )
    
    def reset_all(self) -> List[ResetResult]:
        """
        Reset all applications in parallel.
        
        Returns:
            List of ResetResult for each application
        """
        results = []
        
        for app_name in self.reset_configs.keys():
            result = self.reset_application(app_name)
            results.append(result)
        
        # Summary logging
        success_count = sum(1 for r in results if r.success)
        total_time = sum(r.execution_time_seconds for r in results)
        
        self.logger.info(
            f"Reset completed: {success_count}/{len(results)} successful, "
            f"total time: {total_time:.2f}s"
        )
        
        return results
    
    def _execute_command(self, command: str, cwd: Path) -> subprocess.CompletedProcess:
        """Execute a shell command."""
        self.logger.debug(f"Executing: {command} in {cwd}")
        
        # Determine shell based on OS
        shell = True
        if os.name == 'nt':  # Windows
            shell = ["pwsh.exe", "-Command"]
            result = subprocess.run(
                shell + [command],
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=60
            )
        else:  # Unix-like
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=60
            )
        
        if result.returncode != 0:
            raise RuntimeError(
                f"Command failed: {command}\n"
                f"stdout: {result.stdout}\n"
                f"stderr: {result.stderr}"
            )
        
        return result
    
    # -------------------------------------------------------------------------
    # Validation Functions
    # -------------------------------------------------------------------------
    
    def _validate_bad_monolith(self) -> bool:
        """Validate BadMonolith reset by checking task count."""
        try:
            import requests
            response = requests.get("http://localhost:5000/api/tasks")
            tasks = response.json()
            
            # Should have exactly 2 seeded tasks
            return len(tasks) == 2
        except Exception as e:
            self.logger.warning(f"BadMonolith validation failed: {e}")
            return False
    
    def _validate_clean_solid_app(self) -> bool:
        """Validate CleanSolidApp reset via EF migrations."""
        try:
            # Check if migration history is clean
            result = self._execute_command(
                "dotnet ef migrations list",
                self.root / "CleanSolidApp" / "backend"
            )
            
            # Should have base migration only
            return "InitialCreate" in result.stdout
        except Exception as e:
            self.logger.warning(f"CleanSolidApp validation failed: {e}")
            return False
    
    def _validate_git_clean(self) -> bool:
        """Validate git checkout resulted in clean state."""
        try:
            result = self._execute_command(
                "git status --porcelain",
                self.root / "_Real"
            )
            
            # Should have no modified files
            return result.stdout.strip() == ""
        except Exception as e:
            self.logger.warning(f"_Real validation failed: {e}")
            return False
    
    def _validate_docker_health(self) -> bool:
        """Validate Docker containers are healthy."""
        try:
            result = self._execute_command(
                "docker-compose ps --format json",
                self.root / "Cortex-Clean"
            )
            
            containers = json.loads(result.stdout)
            
            # All containers should be healthy
            return all(
                c.get("Health", "").lower() == "healthy"
                for c in containers
            )
        except Exception as e:
            self.logger.warning(f"Cortex-Clean validation failed: {e}")
            return False
    
    def _validate_test_fixtures(self) -> bool:
        """Validate pytest fixtures cleaned up."""
        try:
            # Check if .pytest_cache is clean
            cache_dir = self.root / "Cortex-SDD" / ".pytest_cache"
            
            if not cache_dir.exists():
                return True
            
            # No active test sessions
            return not (cache_dir / ".lock").exists()
        except Exception as e:
            self.logger.warning(f"Cortex-SDD validation failed: {e}")
            return False
    
    # -------------------------------------------------------------------------
    # Reporting
    # -------------------------------------------------------------------------
    
    def generate_reset_report(self, results: List[ResetResult]) -> Dict:
        """
        Generate detailed reset report.
        
        Args:
            results: List of reset results
            
        Returns:
            Report dictionary
        """
        report = {
            "summary": {
                "total_applications": len(results),
                "successful_resets": sum(1 for r in results if r.success),
                "failed_resets": sum(1 for r in results if not r.success),
                "validation_passed": sum(1 for r in results if r.validation_passed),
                "total_execution_time": sum(r.execution_time_seconds for r in results)
            },
            "results": [
                {
                    "application": r.application,
                    "success": r.success,
                    "reset_type": r.reset_type.value,
                    "execution_time": r.execution_time_seconds,
                    "validation_passed": r.validation_passed,
                    "error": r.error_message
                }
                for r in results
            ]
        }
        
        return report


def main():
    """CLI entry point for reset manager."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Reset sharpening-cortex sample applications"
    )
    parser.add_argument(
        "--app",
        help="Specific application to reset (or 'all')",
        default="all"
    )
    parser.add_argument(
        "--root",
        type=Path,
        help="Path to sharpening-cortex root",
        default=Path(__file__).parent.parent.parent.parent / "sharpening-cortex"
    )
    parser.add_argument(
        "--report",
        type=Path,
        help="Output report path",
        default=None
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    )
    
    manager = ResetManager(args.root)
    
    # Execute reset
    if args.app == "all":
        results = manager.reset_all()
    else:
        result = manager.reset_application(args.app)
        results = [result]
    
    # Generate report
    report = manager.generate_reset_report(results)
    
    # Output report
    if args.report:
        with open(args.report, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"Report saved to {args.report}")
    else:
        print(json.dumps(report, indent=2))
    
    # Exit code based on success
    exit_code = 0 if report["summary"]["failed_resets"] == 0 else 1
    return exit_code


if __name__ == "__main__":
    exit(main())
