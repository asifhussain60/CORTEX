"""
Validator Engine - Build and test validation for transformed codebase.

Features:
- Multi-build-system detection (pip, npm, maven, dotnet, gradle, etc.)
- Build execution with timeout
- Test execution (optional)
- Result comparison with baseline
- Rollback trigger on validation failure
- Comprehensive logging

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class BuildSystem(str, Enum):
    """Supported build systems."""
    PIP = "pip"
    NPM = "npm"
    MAVEN = "maven"
    DOTNET = "dotnet"
    GRADLE = "gradle"
    UNKNOWN = "unknown"


class ValidationStatus(str, Enum):
    """Validation status."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class BuildResult:
    """Result of build execution."""
    build_system: BuildSystem
    success: bool
    duration_seconds: float
    exit_code: int
    stdout: str
    stderr: str
    error: Optional[str] = None


@dataclass
class TestResult:
    """Result of test execution."""
    success: bool
    tests_run: int
    tests_passed: int
    tests_failed: int
    duration_seconds: float
    exit_code: int
    stdout: str
    stderr: str
    error: Optional[str] = None


@dataclass
class ValidationResult:
    """Complete validation result."""
    validation_status: ValidationStatus
    build_result: Optional[BuildResult] = None
    test_result: Optional[TestResult] = None
    validation_passed: bool = False
    duration_seconds: float = 0.0
    error: Optional[str] = None


class ValidatorEngine:
    """
    Validator engine for build and test validation.
    
    Validates transformed codebase by:
    1. Detecting build system
    2. Running build
    3. Running tests (optional)
    4. Comparing results with baseline
    """
    
    # Build system detection
    BUILD_SYSTEM_MARKERS = {
        BuildSystem.PIP: ['requirements.txt', 'setup.py', 'pyproject.toml'],
        BuildSystem.NPM: ['package.json'],
        BuildSystem.MAVEN: ['pom.xml'],
        BuildSystem.DOTNET: ['*.csproj', '*.sln'],
        BuildSystem.GRADLE: ['build.gradle', 'build.gradle.kts']
    }
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize validator engine.
        
        Args:
            config: Configuration dictionary from orchestrator
        """
        self.config = config
        self.validation_config = config.get('validation', {})
        
        # Strategy settings
        self.strategy = self.validation_config.get('strategy', {})
        self.build_required = self.strategy.get('build_required', True)
        self.tests_required = self.strategy.get('tests_required', False)
        
        # Timeout settings
        self.timeout_config = self.validation_config.get('timeout', {})
        self.build_timeout = self.timeout_config.get('build_timeout_seconds', 1800)
        self.test_timeout = self.timeout_config.get('test_timeout_seconds', 3600)
        
        logger.info(
            f"Initialized ValidatorEngine "
            f"(build_required={self.build_required}, tests_required={self.tests_required})"
        )
    
    def validate_codebase(
        self,
        codebase_directory: Path,
        dry_run: bool = False
    ) -> ValidationResult:
        """
        Validate transformed codebase.
        
        Args:
            codebase_directory: Root directory of codebase
            dry_run: If True, skip actual validation
        
        Returns:
            ValidationResult
        """
        logger.info(f"Starting codebase validation: {codebase_directory}")
        start_time = datetime.now()
        
        if dry_run:
            logger.info("DRY-RUN MODE: Skipping validation")
            return ValidationResult(
                validation_status=ValidationStatus.SKIPPED,
                validation_passed=True,
                duration_seconds=0.0
            )
        
        try:
            # Detect build system
            build_system = self.detect_build_system(codebase_directory)
            logger.info(f"Detected build system: {build_system.value}")
            
            if build_system == BuildSystem.UNKNOWN:
                logger.warning("Unknown build system - skipping validation")
                return ValidationResult(
                    validation_status=ValidationStatus.SKIPPED,
                    validation_passed=True,
                    duration_seconds=0.0
                )
            
            # Run build
            build_result = None
            if self.build_required:
                build_result = self.run_build(codebase_directory, build_system)
                
                if not build_result.success:
                    logger.error("Build failed - validation failed")
                    duration = (datetime.now() - start_time).total_seconds()
                    return ValidationResult(
                        validation_status=ValidationStatus.FAILED,
                        build_result=build_result,
                        validation_passed=False,
                        duration_seconds=duration,
                        error="Build failed"
                    )
            
            # Run tests
            test_result = None
            if self.tests_required:
                test_result = self.run_tests(codebase_directory, build_system)
                
                if not test_result.success:
                    logger.error("Tests failed - validation failed")
                    duration = (datetime.now() - start_time).total_seconds()
                    return ValidationResult(
                        validation_status=ValidationStatus.FAILED,
                        build_result=build_result,
                        test_result=test_result,
                        validation_passed=False,
                        duration_seconds=duration,
                        error="Tests failed"
                    )
            
            # Validation passed
            duration = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"Validation passed in {duration:.1f}s")
            
            return ValidationResult(
                validation_status=ValidationStatus.PASSED,
                build_result=build_result,
                test_result=test_result,
                validation_passed=True,
                duration_seconds=duration
            )
        
        except Exception as e:
            logger.error(f"Validation error: {e}", exc_info=True)
            duration = (datetime.now() - start_time).total_seconds()
            return ValidationResult(
                validation_status=ValidationStatus.FAILED,
                validation_passed=False,
                duration_seconds=duration,
                error=str(e)
            )
    
    def detect_build_system(self, directory: Path) -> BuildSystem:
        """
        Detect build system from marker files.
        
        Args:
            directory: Directory to check
        
        Returns:
            BuildSystem enum value
        """
        for build_system, markers in self.BUILD_SYSTEM_MARKERS.items():
            for marker in markers:
                # Handle glob patterns (e.g., *.csproj)
                if '*' in marker:
                    if list(directory.glob(marker)):
                        return build_system
                else:
                    if (directory / marker).exists():
                        return build_system
        
        return BuildSystem.UNKNOWN
    
    def run_build(
        self,
        directory: Path,
        build_system: BuildSystem
    ) -> BuildResult:
        """
        Run build for detected build system.
        
        Args:
            directory: Codebase directory
            build_system: Detected build system
        
        Returns:
            BuildResult
        """
        logger.info(f"Running build ({build_system.value})...")
        start_time = datetime.now()
        
        # Get build command for system
        build_command = self._get_build_command(build_system)
        
        if not build_command:
            logger.warning(f"No build command configured for {build_system.value}")
            return BuildResult(
                build_system=build_system,
                success=False,
                duration_seconds=0.0,
                exit_code=-1,
                stdout="",
                stderr="",
                error="No build command configured"
            )
        
        try:
            # Execute build
            result = subprocess.run(
                build_command,
                cwd=directory,
                capture_output=True,
                text=True,
                timeout=self.build_timeout,
                shell=True
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            success = result.returncode == 0
            
            logger.info(f"Build {'succeeded' if success else 'failed'} in {duration:.1f}s")
            
            return BuildResult(
                build_system=build_system,
                success=success,
                duration_seconds=duration,
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr
            )
        
        except subprocess.TimeoutExpired:
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"Build timeout after {duration:.1f}s")
            return BuildResult(
                build_system=build_system,
                success=False,
                duration_seconds=duration,
                exit_code=-1,
                stdout="",
                stderr="",
                error=f"Build timeout after {self.build_timeout}s"
            )
        
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"Build error: {e}")
            return BuildResult(
                build_system=build_system,
                success=False,
                duration_seconds=duration,
                exit_code=-1,
                stdout="",
                stderr="",
                error=str(e)
            )
    
    def run_tests(
        self,
        directory: Path,
        build_system: BuildSystem
    ) -> TestResult:
        """
        Run tests for detected build system.
        
        Args:
            directory: Codebase directory
            build_system: Detected build system
        
        Returns:
            TestResult
        """
        logger.info(f"Running tests ({build_system.value})...")
        start_time = datetime.now()
        
        # Get test command for system
        test_command = self._get_test_command(build_system)
        
        if not test_command:
            logger.warning(f"No test command configured for {build_system.value}")
            return TestResult(
                success=True,  # Consider success if no tests configured
                tests_run=0,
                tests_passed=0,
                tests_failed=0,
                duration_seconds=0.0,
                exit_code=0,
                stdout="",
                stderr="",
                error="No test command configured"
            )
        
        try:
            # Execute tests
            result = subprocess.run(
                test_command,
                cwd=directory,
                capture_output=True,
                text=True,
                timeout=self.test_timeout,
                shell=True
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            success = result.returncode == 0
            
            # Parse test results (simplified - actual parsing would be build-system specific)
            tests_run, tests_passed, tests_failed = self._parse_test_output(
                result.stdout,
                build_system
            )
            
            logger.info(
                f"Tests {'passed' if success else 'failed'} in {duration:.1f}s "
                f"({tests_passed}/{tests_run} passed)"
            )
            
            return TestResult(
                success=success,
                tests_run=tests_run,
                tests_passed=tests_passed,
                tests_failed=tests_failed,
                duration_seconds=duration,
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr
            )
        
        except subprocess.TimeoutExpired:
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"Test timeout after {duration:.1f}s")
            return TestResult(
                success=False,
                tests_run=0,
                tests_passed=0,
                tests_failed=0,
                duration_seconds=duration,
                exit_code=-1,
                stdout="",
                stderr="",
                error=f"Test timeout after {self.test_timeout}s"
            )
        
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"Test error: {e}")
            return TestResult(
                success=False,
                tests_run=0,
                tests_passed=0,
                tests_failed=0,
                duration_seconds=duration,
                exit_code=-1,
                stdout="",
                stderr="",
                error=str(e)
            )
    
    def _get_build_command(self, build_system: BuildSystem) -> Optional[str]:
        """Get build command for build system."""
        build_systems = self.validation_config.get('build_systems', [])
        
        for system_config in build_systems:
            if system_config.get('name') == build_system.value:
                return system_config.get('build_command')
        
        return None
    
    def _get_test_command(self, build_system: BuildSystem) -> Optional[str]:
        """Get test command for build system."""
        build_systems = self.validation_config.get('build_systems', [])
        
        for system_config in build_systems:
            if system_config.get('name') == build_system.value:
                return system_config.get('test_command')
        
        return None
    
    def _parse_test_output(
        self,
        output: str,
        build_system: BuildSystem
    ) -> tuple[int, int, int]:
        """
        Parse test output to extract test counts.
        
        Simplified implementation - real version would parse build-system-specific output.
        
        Returns:
            (tests_run, tests_passed, tests_failed)
        """
        # Default values if parsing fails
        return (0, 0, 0)
