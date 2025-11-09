"""
Platform Detection Setup Module

Detects current platform (Mac/Windows/Linux) and configures environment accordingly.

SOLID Principles:
- Single Responsibility: Only handles platform detection and basic config
- Open/Closed: Extends BaseSetupModule without modifying it
- Dependency Inversion: Depends on BaseSetupModule abstraction

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sys
import platform
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


class PlatformDetectionModule(BaseOperationModule):
    """
    Setup module for platform detection and configuration.
    
    Responsibilities:
    1. Detect current platform (Mac/Windows/Linux)
    2. Determine platform-specific paths and commands
    3. Configure environment variables
    4. Update context with platform information
    """
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Return module metadata."""
        return OperationModuleMetadata(
            module_id="platform_detection",
            name="Platform Detection & Configuration",
            description="Detect current platform (Mac/Windows/Linux) and configure environment",
            phase=OperationPhase.ENVIRONMENT,
            priority=10,
            dependencies=["project_validation"],
            optional=False,
        )
    
    def validate_prerequisites(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate prerequisites for platform detection.
        
        Checks:
        1. Python sys module available
        2. Platform module available
        3. Project root exists
        """
        issues = []
        
        # Check project root
        project_root = context.get('project_root')
        if not project_root:
            issues.append("Project root not found in context")
            return False, issues
        
        project_root = Path(project_root)
        if not project_root.exists():
            issues.append(f"Project root does not exist: {project_root}")
            return False, issues
        
        return True, []
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Execute platform detection.
        
        Steps:
        1. Detect platform using sys.platform
        2. Determine platform-specific settings
        3. Configure paths and commands
        4. Update context
        """
        start_time = datetime.now()
        
        try:
            # Detect platform
            platform_info = self._detect_platform()
            
            self.log_info(f"Detected platform: {platform_info['display_name']}")
            self.log_info(f"  System: {platform_info['system']}")
            self.log_info(f"  Release: {platform_info['release']}")
            self.log_info(f"  Machine: {platform_info['machine']}")
            
            # Configure platform-specific settings
            config = self._configure_platform(platform_info)
            
            # Update context with platform information
            context['platform'] = platform_info['platform']
            context['platform_display'] = platform_info['display_name']
            context['platform_info'] = platform_info
            context['platform_config'] = config
            context['python_command'] = config['python_command']
            context['shell'] = config['shell']
            context['path_separator'] = config['path_separator']
            
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            return OperationResult(
                module_id=self.metadata.module_id,
                status=OperationStatus.SUCCESS,
                message=f"Platform detected: {platform_info['display_name']}",
                details={
                    'platform': platform_info['platform'],
                    'display_name': platform_info['display_name'],
                    'python_command': config['python_command'],
                    'shell': config['shell'],
                    'system': platform_info['system'],
                    'release': platform_info['release']
                },
                duration_ms=duration_ms
            )
            
        except Exception as e:
            self.log_error(f"Platform detection failed: {e}")
            return OperationResult(
                module_id=self.metadata.module_id,
                status=OperationStatus.FAILED,
                message=f"Platform detection failed: {str(e)}",
                errors=[str(e)],
                duration_ms=(datetime.now() - start_time).total_seconds() * 1000
            )
    
    def _detect_platform(self) -> Dict[str, str]:
        """
        Detect current platform and gather system information.
        
        Returns:
            Dictionary with platform details
        """
        sys_platform = sys.platform
        
        # Determine platform
        if sys_platform == "darwin":
            platform_name = "darwin"
            display_name = "macOS"
        elif sys_platform.startswith("win"):
            platform_name = "win32"
            display_name = "Windows"
        elif sys_platform.startswith("linux"):
            platform_name = "linux"
            display_name = "Linux"
        else:
            platform_name = sys_platform
            display_name = sys_platform.title()
        
        return {
            'platform': platform_name,
            'display_name': display_name,
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor() or 'unknown',
            'python_version': platform.python_version()
        }
    
    def _configure_platform(self, platform_info: Dict[str, str]) -> Dict[str, str]:
        """
        Configure platform-specific settings.
        
        Args:
            platform_info: Platform detection results
        
        Returns:
            Dictionary with platform configuration
        """
        platform_name = platform_info['platform']
        
        if platform_name == "darwin":
            # macOS configuration
            return {
                'platform': platform_name,
                'path_separator': '/',
                'python_command': 'python3',
                'shell': 'zsh',
                'line_ending': '\n',
                'home_var': 'HOME',
                'venv_bin': 'bin',
                'venv_activate': 'bin/activate'
            }
        elif platform_name == "win32":
            # Windows configuration
            return {
                'platform': platform_name,
                'path_separator': '\\',
                'python_command': 'python',
                'shell': 'powershell',
                'line_ending': '\r\n',
                'home_var': 'USERPROFILE',
                'venv_bin': 'Scripts',
                'venv_activate': 'Scripts\\activate'
            }
        elif platform_name == "linux":
            # Linux configuration
            return {
                'platform': platform_name,
                'path_separator': '/',
                'python_command': 'python3',
                'shell': 'bash',
                'line_ending': '\n',
                'home_var': 'HOME',
                'venv_bin': 'bin',
                'venv_activate': 'bin/activate'
            }
        else:
            # Default Unix-like configuration
            return {
                'platform': platform_name,
                'path_separator': '/',
                'python_command': 'python3',
                'shell': 'sh',
                'line_ending': '\n',
                'home_var': 'HOME',
                'venv_bin': 'bin',
                'venv_activate': 'bin/activate'
            }
