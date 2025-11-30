"""
Virtual Environment Setup Module

Creates or activates Python virtual environment for CORTEX.

SOLID Principles:
- Single Responsibility: Only handles virtual environment management
- Open/Closed: Extends BaseOperationModule without modifying it
- Dependency Inversion: Depends on BaseOperationModule abstraction

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import subprocess
import sys
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


class VirtualEnvironmentModule(BaseOperationModule):
    """
    Setup module for Python virtual environment management.
    
    Responsibilities:
    1. Check if already running in venv
    2. Detect existing venv in project
    3. Create new venv if needed
    4. Provide activation instructions
    5. Validate venv is usable
    """
    
    VENV_DIRS = [".venv", "venv", ".env"]  # Common venv directory names
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Return module metadata."""
        return OperationModuleMetadata(
            module_id="virtual_environment",
            name="Python Virtual Environment",
            description="Create or activate Python virtual environment",
            phase=OperationPhase.DEPENDENCIES,
            priority=10,  # Before python dependencies
            dependencies=["platform_detection"],
            optional=False,
        )
    
    def validate_prerequisites(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate prerequisites for virtual environment setup.
        
        Checks:
        1. Project root exists
        2. Python command available
        3. Platform information available
        """
        issues = []
        
        # Check project root
        project_root = context.get('project_root')
        if not project_root:
            issues.append("Project root not found in context")
            return False, issues
        
        # Check platform info
        if 'platform_config' not in context:
            issues.append("Platform configuration not found in context")
            return False, issues
        
        return True, []
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Execute virtual environment setup.
        
        Steps:
        1. Check if running in venv already
        2. Look for existing venv
        3. Create venv if needed
        4. Validate venv
        5. Provide activation instructions
        """
        start_time = datetime.now()
        project_root = Path(context['project_root'])
        platform_config = context['platform_config']
        python_cmd = platform_config['python_command']
        
        try:
            # Check if already in venv
            in_venv = self._is_in_virtualenv()
            if in_venv:
                venv_path = self._get_current_venv_path()
                self.log_info(f"Already running in virtual environment: {venv_path}")
                
                context['venv_active'] = True
                context['venv_path'] = str(venv_path)
                context['venv_python'] = sys.executable
                
                return OperationResult(
                    success=True,
                    status=OperationStatus.SUCCESS,
                    message="Already running in virtual environment",
                    data={
                        'in_venv': True,
                        'venv_path': str(venv_path),
                        'python_executable': sys.executable,
                        'created_new': False
                    },
                    duration_seconds=(datetime.now() - start_time).total_seconds()
                )
            
            # Look for existing venv
            existing_venv = self._find_existing_venv(project_root)
            if existing_venv:
                self.log_info(f"Found existing virtual environment: {existing_venv}")
                
                # Validate it's usable
                if self._validate_venv(existing_venv, python_cmd):
                    activation_cmd = self._get_activation_command(existing_venv, platform_config)
                    
                    context['venv_active'] = False
                    context['venv_path'] = str(existing_venv)
                    context['activation_command'] = activation_cmd
                    
                    return OperationResult(
                        success=True,
                        status=OperationStatus.WARNING,
                        message="Virtual environment exists but not activated",
                        data={
                            'in_venv': False,
                            'venv_path': str(existing_venv),
                            'venv_exists': True,
                            'activation_command': activation_cmd,
                            'created_new': False
                        },
                        warnings=[f"Please activate virtual environment: {activation_cmd}"],
                        duration_seconds=(datetime.now() - start_time).total_seconds()
                    )
            
            # Create new venv
            self.log_info("Creating new virtual environment...")
            venv_path = project_root / ".venv"
            
            create_success, create_output = self._create_venv(venv_path, python_cmd)
            if not create_success:
                return OperationResult(
                    success=False,
                    status=OperationStatus.FAILED,
                    message="Failed to create virtual environment",
                    errors=[f"venv creation failed: {create_output}"],
                    duration_seconds=(datetime.now() - start_time).total_seconds()
                )
            
            self.log_info(f"Created virtual environment at: {venv_path}")
            
            # Validate new venv
            if not self._validate_venv(venv_path, python_cmd):
                return OperationResult(
                    success=False,
                    status=OperationStatus.FAILED,
                    message="Virtual environment validation failed",
                    errors=["Created venv is not functional"],
                    duration_seconds=(datetime.now() - start_time).total_seconds()
                )
            
            activation_cmd = self._get_activation_command(venv_path, platform_config)
            
            context['venv_active'] = False
            context['venv_path'] = str(venv_path)
            context['activation_command'] = activation_cmd
            
            duration_seconds = (datetime.now() - start_time).total_seconds()
            
            return OperationResult(
                success=True,
                status=OperationStatus.WARNING,
                message="Virtual environment created successfully",
                data={
                    'in_venv': False,
                    'venv_path': str(venv_path),
                    'venv_exists': True,
                    'activation_command': activation_cmd,
                    'created_new': True
                },
                warnings=[f"Please activate virtual environment: {activation_cmd}"],
                duration_seconds=duration_seconds
            )
            
        except Exception as e:
            self.log_error(f"Virtual environment setup failed: {e}")
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Virtual environment setup failed: {str(e)}",
                errors=[str(e)],
                duration_seconds=(datetime.now() - start_time).total_seconds()
            )
    
    def _is_in_virtualenv(self) -> bool:
        """Check if currently running in a virtual environment."""
        return (
            hasattr(sys, 'real_prefix') or
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
        )
    
    def _get_current_venv_path(self) -> Path:
        """Get path to current virtual environment."""
        if hasattr(sys, 'real_prefix'):
            return Path(sys.prefix)
        elif hasattr(sys, 'base_prefix'):
            return Path(sys.prefix)
        return Path(sys.prefix)
    
    def _find_existing_venv(self, project_root: Path) -> Path:
        """Find existing virtual environment in project."""
        for venv_dir in self.VENV_DIRS:
            venv_path = project_root / venv_dir
            if venv_path.is_dir():
                # Check if it looks like a venv (has pyvenv.cfg or Scripts/bin)
                if (venv_path / "pyvenv.cfg").exists():
                    return venv_path
                if (venv_path / "Scripts").is_dir() or (venv_path / "bin").is_dir():
                    return venv_path
        return None
    
    def _validate_venv(self, venv_path: Path, python_cmd: str) -> bool:
        """Validate virtual environment is functional."""
        # Check for python executable
        if (venv_path / "Scripts" / "python.exe").exists():
            python_exe = venv_path / "Scripts" / "python.exe"
        elif (venv_path / "bin" / "python").exists():
            python_exe = venv_path / "bin" / "python"
        else:
            return False
        
        # Try to run python --version
        try:
            result = subprocess.run(
                [str(python_exe), "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except subprocess.SubprocessError:
            return False
    
    def _create_venv(self, venv_path: Path, python_cmd: str) -> Tuple[bool, str]:
        """Create new virtual environment."""
        try:
            result = subprocess.run(
                [python_cmd, "-m", "venv", str(venv_path)],
                capture_output=True,
                text=True,
                timeout=60
            )
            output = result.stdout + result.stderr
            return result.returncode == 0, output
        except subprocess.SubprocessError as e:
            return False, str(e)
    
    def _get_activation_command(self, venv_path: Path, platform_config: Dict[str, str]) -> str:
        """Get platform-specific activation command."""
        platform = platform_config['platform']
        
        if platform == "win32":
            # Windows
            return f"{venv_path}\\Scripts\\activate"
        else:
            # Unix-like (macOS, Linux)
            return f"source {venv_path}/bin/activate"
