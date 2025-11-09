"""
Python Dependencies Setup Module

Installs required Python packages from requirements.txt.

SOLID Principles:
- Single Responsibility: Only handles Python package installation
- Open/Closed: Extends BaseOperationModule without modifying it
- Dependency Inversion: Depends on BaseOperationModule abstraction

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import subprocess
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


class PythonDependenciesModule(BaseOperationModule):
    """
    Setup module for installing Python dependencies.
    
    Responsibilities:
    1. Verify requirements.txt exists
    2. Upgrade pip to latest version
    3. Install packages from requirements.txt
    4. Verify installations
    5. Update context with installed packages
    """
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Return module metadata."""
        return OperationModuleMetadata(
            module_id="python_dependencies",
            name="Python Dependencies Installation",
            description="Install required Python packages from requirements.txt",
            phase=OperationPhase.DEPENDENCIES,
            priority=10,
            dependencies=["virtual_environment"],
            optional=False,
        )
    
    def validate_prerequisites(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate prerequisites for dependency installation.
        
        Checks:
        1. Project root exists
        2. requirements.txt exists
        3. Python command available
        """
        issues = []
        
        # Check project root
        project_root = context.get('project_root')
        if not project_root:
            issues.append("Project root not found in context")
            return False, issues
        
        project_root = Path(project_root)
        
        # Check requirements.txt
        requirements_file = project_root / "requirements.txt"
        if not requirements_file.exists():
            issues.append(f"requirements.txt not found: {requirements_file}")
            return False, issues
        
        # Check Python command
        python_cmd = context.get('python_command', 'python3')
        try:
            result = subprocess.run(
                [python_cmd, "--version"],
                capture_output=True,
                timeout=5
            )
            if result.returncode != 0:
                issues.append(f"Python command '{python_cmd}' failed")
        except Exception as e:
            issues.append(f"Python command '{python_cmd}' not available: {e}")
        
        return len(issues) == 0, issues
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Execute Python dependency installation.
        
        Steps:
        1. Upgrade pip
        2. Install from requirements.txt
        3. Verify installations
        4. Update context
        """
        start_time = datetime.now()
        warnings = []
        
        try:
            project_root = Path(context['project_root'])
            requirements_file = project_root / "requirements.txt"
            python_cmd = self._get_python_command(context)
            
            self.log_info(f"Installing dependencies from: {requirements_file}")
            
            # Step 1: Upgrade pip
            self.log_info("Upgrading pip...")
            pip_result = subprocess.run(
                [python_cmd, "-m", "pip", "install", "--upgrade", "pip"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if pip_result.returncode != 0:
                warnings.append("Failed to upgrade pip (continuing anyway)")
                self.log_warning(warnings[0])
            else:
                self.log_info("✓ Pip upgraded")
            
            # Step 2: Install dependencies
            self.log_info(f"Installing packages from requirements.txt...")
            install_result = subprocess.run(
                [python_cmd, "-m", "pip", "install", "-r", str(requirements_file)],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if install_result.returncode != 0:
                return OperationResult(
                    module_id=self.metadata.module_id,
                    status=OperationStatus.FAILED,
                    message="Failed to install dependencies",
                    errors=[install_result.stderr],
                    duration_ms=(datetime.now() - start_time).total_seconds() * 1000
                )
            
            # Parse installation output
            packages_installed = self._parse_install_output(install_result.stdout)
            self.log_info(f"✓ Installed {packages_installed} packages")
            
            # Step 3: Verify critical packages
            critical_packages = ['pytest', 'pyyaml', 'numpy', 'scikit-learn']
            missing = self._verify_packages(python_cmd, critical_packages)
            
            if missing:
                warnings.append(f"Some critical packages may not be installed: {', '.join(missing)}")
                self.log_warning(warnings[-1])
            
            # Update context
            context['dependencies_installed'] = True
            context['packages_installed'] = packages_installed
            
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            status = OperationStatus.WARNING if warnings else OperationStatus.SUCCESS
            
            return OperationResult(
                module_id=self.metadata.module_id,
                status=status,
                message=f"Installed {packages_installed} Python packages",
                details={
                    'requirements_file': str(requirements_file),
                    'packages_installed': packages_installed,
                    'python_command': python_cmd
                },
                warnings=warnings,
                duration_ms=duration_ms
            )
            
        except subprocess.TimeoutExpired:
            return OperationResult(
                module_id=self.metadata.module_id,
                status=OperationStatus.FAILED,
                message="Installation timeout (exceeded 5 minutes)",
                errors=["Timeout"],
                duration_ms=(datetime.now() - start_time).total_seconds() * 1000
            )
        except Exception as e:
            self.log_error(f"Dependency installation failed: {e}")
            return OperationResult(
                module_id=self.metadata.module_id,
                status=OperationStatus.FAILED,
                message=f"Installation failed: {str(e)}",
                errors=[str(e)],
                duration_ms=(datetime.now() - start_time).total_seconds() * 1000
            )
    
    def _get_python_command(self, context: Dict[str, Any]) -> str:
        """Get Python command from context or determine from venv."""
        # Check if venv path in context
        venv_path = context.get('venv_path')
        if venv_path:
            venv_path = Path(venv_path)
            platform_config = context.get('platform_config', {})
            venv_bin = platform_config.get('venv_bin', 'bin')
            
            python_exe = venv_path / venv_bin / 'python'
            if platform_config.get('platform') == 'win32':
                python_exe = python_exe.with_suffix('.exe')
            
            if python_exe.exists():
                return str(python_exe)
        
        # Fallback to context python_command
        return context.get('python_command', 'python3')
    
    def _parse_install_output(self, output: str) -> int:
        """Parse pip install output to count packages."""
        # Count lines with "Successfully installed"
        if "Successfully installed" in output:
            # Extract package names from the line
            for line in output.split('\n'):
                if "Successfully installed" in line:
                    # Count packages after "Successfully installed"
                    packages = line.split("Successfully installed")[1].strip().split()
                    return len(packages)
        return 0
    
    def _verify_packages(self, python_cmd: str, packages: List[str]) -> List[str]:
        """
        Verify that packages are installed.
        
        Args:
            python_cmd: Python command
            packages: List of package names to verify
        
        Returns:
            List of missing packages
        """
        missing = []
        
        for package in packages:
            try:
                result = subprocess.run(
                    [python_cmd, "-c", f"import {package}"],
                    capture_output=True,
                    timeout=5
                )
                if result.returncode != 0:
                    missing.append(package)
            except:
                missing.append(package)
        
        return missing

