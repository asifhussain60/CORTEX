"""
Build Validator for Sanitization

Validates that sanitized codebases build successfully and pass tests.

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
"""

import os
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class BuildValidator:
    """Validates sanitized codebases through build and test execution."""

    def __init__(self, manifest: Dict[str, Any]):
        self.manifest = manifest
        self.validation_rules = manifest.get("validation_rules", {})
        self.build_systems = self.validation_rules.get("build_systems", {})

    def detect_build_system(self, directory: str) -> str:
        """
        Detect build system from project files.

        Args:
            directory: Project directory

        Returns:
            Build system name ('dotnet', 'python', 'node', 'unknown')
        """
        dir_path = Path(directory)

        # Check for .NET
        if list(dir_path.glob("*.csproj")) or list(dir_path.glob("*.sln")):
            return "dotnet"

        # Check for Python
        if (dir_path / "setup.py").exists() or (dir_path / "pyproject.toml").exists():
            return "python"

        # Check for Node.js
        if (dir_path / "package.json").exists():
            return "node"

        # Check for Maven/Gradle
        if (dir_path / "pom.xml").exists():
            return "maven"
        if (dir_path / "build.gradle").exists():
            return "gradle"

        logger.warning(f"Could not detect build system in {directory}")
        return "unknown"

    def execute_build(self, directory: str, build_system: str) -> Dict[str, Any]:
        """
        Execute build for the project.

        Args:
            directory: Project directory
            build_system: Detected build system

        Returns:
            Dict with build results
        """
        if build_system not in self.build_systems:
            logger.warning(f"No build configuration for {build_system}")
            return {
                "success": True,  # Optimistic - assume OK if no build needed
                "skipped": True,
                "message": f"No build configuration for {build_system}",
            }

        config = self.build_systems[build_system]
        build_command = config.get("build_command", "")
        success_exit_code = config.get("success_exit_code", 0)

        logger.info(f"Building with command: {build_command}")

        try:
            result = subprocess.run(
                build_command,
                shell=True,
                cwd=directory,
                capture_output=True,
                text=True,
                timeout=300,  # 5-minute timeout
            )

            success = result.returncode == success_exit_code

            return {
                "success": success,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "output": result.stdout + "\n" + result.stderr,
            }

        except subprocess.TimeoutExpired:
            logger.error("Build timeout exceeded")
            return {
                "success": False,
                "error": "Build timeout (300s)",
            }
        except Exception as e:
            logger.error(f"Build failed: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    def run_tests(self, directory: str, build_system: str) -> Dict[str, Any]:
        """
        Run test suite for the project.

        Args:
            directory: Project directory
            build_system: Detected build system

        Returns:
            Dict with test results
        """
        if build_system not in self.build_systems:
            logger.warning(f"No test configuration for {build_system}")
            return {
                "success": True,  # Optimistic
                "skipped": True,
                "message": f"No test configuration for {build_system}",
            }

        config = self.build_systems[build_system]
        test_command = config.get("test_command", "")
        success_exit_code = config.get("success_exit_code", 0)

        logger.info(f"Running tests with command: {test_command}")

        try:
            result = subprocess.run(
                test_command,
                shell=True,
                cwd=directory,
                capture_output=True,
                text=True,
                timeout=600,  # 10-minute timeout for tests
            )

            success = result.returncode == success_exit_code

            # Parse test output (basic implementation)
            test_stats = self._parse_test_output(result.stdout, build_system)

            return {
                "success": success,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "output": result.stdout + "\n" + result.stderr,
                **test_stats,
            }

        except subprocess.TimeoutExpired:
            logger.error("Test timeout exceeded")
            return {
                "success": False,
                "error": "Test timeout (600s)",
            }
        except Exception as e:
            logger.error(f"Tests failed: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    def _parse_test_output(self, output: str, build_system: str) -> Dict[str, int]:
        """
        Parse test output to extract statistics.

        Args:
            output: Test command output
            build_system: Build system name

        Returns:
            Dict with test statistics
        """
        stats = {
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "total": 0,
        }

        try:
            if build_system == "dotnet":
                # Look for patterns like "Passed!  - Failed:     0, Passed:    10, Skipped:     0, Total:    10"
                import re
                match = re.search(r'Passed:\s+(\d+)', output)
                if match:
                    stats["passed"] = int(match.group(1))
                match = re.search(r'Failed:\s+(\d+)', output)
                if match:
                    stats["failed"] = int(match.group(1))
                match = re.search(r'Total:\s+(\d+)', output)
                if match:
                    stats["total"] = int(match.group(1))

            elif build_system == "python":
                # pytest output: "10 passed in 2.5s"
                import re
                match = re.search(r'(\d+) passed', output)
                if match:
                    stats["passed"] = int(match.group(1))
                match = re.search(r'(\d+) failed', output)
                if match:
                    stats["failed"] = int(match.group(1))
                match = re.search(r'(\d+) skipped', output)
                if match:
                    stats["skipped"] = int(match.group(1))
                stats["total"] = stats["passed"] + stats["failed"] + stats["skipped"]

            elif build_system == "node":
                # Jest/Mocha output
                import re
                match = re.search(r'Tests:\s+(\d+) passed', output)
                if match:
                    stats["passed"] = int(match.group(1))
                match = re.search(r'(\d+) failed', output)
                if match:
                    stats["failed"] = int(match.group(1))

        except Exception as e:
            logger.warning(f"Failed to parse test output: {e}")

        return stats
