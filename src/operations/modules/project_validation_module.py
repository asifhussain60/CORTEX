"""
Project Validation Setup Module

Validates CORTEX project structure and required files.

SOLID Principles:
- Single Responsibility: Only handles project structure validation
- Open/Closed: Extends BaseOperationModule without modifying it
- Dependency Inversion: Depends on BaseOperationModule abstraction

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import os
from pathlib import Path
from typing import Dict, Any, Tuple, List
from datetime import datetime

from src.operations.base_operation_module import (
    BaseOperationModule,
    OperationModuleMetadata,
    OperationResult,
    OperationStatus,
    OperationPhase
)


class ProjectValidationModule(BaseOperationModule):
    """
    Setup module for project structure validation.
    
    Responsibilities:
    1. Validate CORTEX project root directory
    2. Check for required directories (cortex-brain/, src/, tests/, prompts/)
    3. Verify essential configuration files
    4. Ensure minimum project structure exists
    """
    
    # Required directories for CORTEX project
    REQUIRED_DIRS = [
        "cortex-brain",
        "src",
        "tests",
        "prompts",
        ".github"
    ]
    
    # Required files (optional check)
    REQUIRED_FILES = [
        "README.md",
        "requirements.txt",
        "cortex.config.json"
    ]
    
    # Critical brain subdirectories
    BRAIN_SUBDIRS = [
        "cortex-brain",  # Main directory must exist
    ]
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Return module metadata."""
        return OperationModuleMetadata(
            module_id="project_validation",
            name="Project Structure Validation",
            description="Validate CORTEX project structure and required directories",
            phase=OperationPhase.PRE_VALIDATION,
            priority=1,  # Highest priority - runs first
            dependencies=[],  # No dependencies - first module to run
            optional=False,
        )
    
    def validate_prerequisites(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate prerequisites for project validation.
        
        Minimal requirements:
        1. Current working directory exists
        2. Can read filesystem
        """
        issues = []
        
        try:
            cwd = Path.cwd()
            if not cwd.exists():
                issues.append("Current working directory does not exist")
                return False, issues
        except Exception as e:
            issues.append(f"Cannot access current working directory: {e}")
            return False, issues
        
        return True, []
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Execute project structure validation.
        
        Steps:
        1. Determine project root (from context or discover)
        2. Validate required directories exist
        3. Check for required files (warnings only)
        4. Verify brain structure
        5. Update context with project paths
        """
        start_time = datetime.now()
        
        try:
            # Determine project root
            project_root = self._determine_project_root(context)
            self.log_info(f"Validating CORTEX project at: {project_root}")
            
            # Track validation results
            validation_results = {
                'project_root': str(project_root),
                'required_dirs_found': [],
                'required_dirs_missing': [],
                'required_files_found': [],
                'required_files_missing': [],
                'brain_subdirs_found': [],
                'brain_subdirs_missing': []
            }
            
            # Validate required directories
            dirs_valid, dirs_issues = self._validate_directories(project_root, validation_results)
            
            # Validate required files (warnings only, not blocking)
            self._validate_files(project_root, validation_results)
            
            # Validate brain structure
            brain_valid, brain_issues = self._validate_brain_structure(project_root, validation_results)
            
            # Determine overall success
            if not dirs_valid:
                # Critical directories missing - cannot proceed
                return OperationResult(
                    success=False,
                    status=OperationStatus.FAILED,
                    message="Project validation failed: Required directories missing",
                    data=validation_results,
                    errors=dirs_issues,
                    duration_seconds=(datetime.now() - start_time).total_seconds()
                )
            
            # Success - update context with project paths
            context['project_root'] = str(project_root)
            context['cortex_brain_path'] = str(project_root / "cortex-brain")
            context['src_path'] = str(project_root / "src")
            context['tests_path'] = str(project_root / "tests")
            context['prompts_path'] = str(project_root / "prompts")
            context['validation_results'] = validation_results
            
            # Build status message
            warnings = []
            if validation_results['required_files_missing']:
                warnings.append(f"{len(validation_results['required_files_missing'])} optional files missing")
            if validation_results['brain_subdirs_missing']:
                warnings.append(f"{len(validation_results['brain_subdirs_missing'])} brain subdirectories not found")
            
            status_message = f"Project validated successfully: {project_root}"
            if warnings:
                status_message += f" (Warnings: {', '.join(warnings)})"
            
            duration_seconds = (datetime.now() - start_time).total_seconds()
            
            return OperationResult(
                success=True,
                status=OperationStatus.SUCCESS if not warnings else OperationStatus.WARNING,
                message=status_message,
                data=validation_results,
                warnings=warnings if warnings else None,
                duration_seconds=duration_seconds
            )
            
        except Exception as e:
            self.log_error(f"Project validation failed: {e}")
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Project validation failed: {str(e)}",
                errors=[str(e)],
                duration_seconds=(datetime.now() - start_time).total_seconds()
            )
    
    def _determine_project_root(self, context: Dict[str, Any]) -> Path:
        """
        Determine CORTEX project root directory.
        
        Priority:
        1. Use project_root from context if provided
        2. Check for CORTEX_ROOT environment variable
        3. Search upward from current directory for .github/prompts/CORTEX.prompt.md
        4. Use current working directory as fallback
        
        Args:
            context: Operation context
        
        Returns:
            Path to project root
        """
        # Check context first
        if 'project_root' in context:
            return Path(context['project_root'])
        
        # Check environment variable
        env_root = os.environ.get('CORTEX_ROOT')
        if env_root:
            self.log_info(f"Using CORTEX_ROOT from environment: {env_root}")
            return Path(env_root)
        
        # Search upward from current directory
        current = Path.cwd()
        for parent in [current, *current.parents]:
            # Look for CORTEX marker file
            marker = parent / ".github" / "prompts" / "CORTEX.prompt.md"
            if marker.exists():
                self.log_info(f"Found CORTEX project marker at: {parent}")
                return parent
            
            # Alternative: look for cortex-brain directory
            if (parent / "cortex-brain").is_dir() and (parent / "src").is_dir():
                self.log_info(f"Found CORTEX project structure at: {parent}")
                return parent
        
        # Fallback to current directory
        self.log_warning("Could not find CORTEX project root, using current directory")
        return Path.cwd()
    
    def _validate_directories(self, project_root: Path, results: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate required directories exist.
        
        Args:
            project_root: Project root path
            results: Validation results dictionary (updated in place)
        
        Returns:
            Tuple of (success, issues)
        """
        issues = []
        
        for dir_name in self.REQUIRED_DIRS:
            dir_path = project_root / dir_name
            if dir_path.is_dir():
                results['required_dirs_found'].append(dir_name)
                self.log_info(f"✓ Required directory found: {dir_name}")
            else:
                results['required_dirs_missing'].append(dir_name)
                issue = f"Required directory missing: {dir_name}"
                issues.append(issue)
                self.log_error(f"✗ {issue}")
        
        return len(issues) == 0, issues
    
    def _validate_files(self, project_root: Path, results: Dict[str, Any]) -> None:
        """
        Validate required files exist (warnings only, not blocking).
        
        Args:
            project_root: Project root path
            results: Validation results dictionary (updated in place)
        """
        for file_name in self.REQUIRED_FILES:
            file_path = project_root / file_name
            if file_path.is_file():
                results['required_files_found'].append(file_name)
                self.log_info(f"✓ Optional file found: {file_name}")
            else:
                results['required_files_missing'].append(file_name)
                self.log_warning(f"⚠ Optional file missing: {file_name}")
    
    def _validate_brain_structure(self, project_root: Path, results: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate brain directory structure.
        
        Args:
            project_root: Project root path
            results: Validation results dictionary (updated in place)
        
        Returns:
            Tuple of (success, issues)
        """
        issues = []
        
        brain_root = project_root / "cortex-brain"
        if not brain_root.is_dir():
            # Already caught by required directories check
            return False, ["Brain root directory missing"]
        
        # Check for key brain files (not blocking, but informative)
        brain_files = [
            "knowledge-graph.yaml",
            "brain-protection-rules.yaml",
            "conversation-history.jsonl"
        ]
        
        for file_name in brain_files:
            file_path = brain_root / file_name
            if file_path.is_file():
                results['brain_subdirs_found'].append(file_name)
                self.log_info(f"✓ Brain file found: {file_name}")
            else:
                results['brain_subdirs_missing'].append(file_name)
                self.log_warning(f"⚠ Brain file not initialized: {file_name}")
        
        return True, []
