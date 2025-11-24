"""
Tooling Verification Setup Module

Verifies development tools are installed and configured.

SOLID Principles:
- Single Responsibility: Only handles tooling verification
- Open/Closed: Extends BaseOperationModule without modifying it
- Dependency Inversion: Depends on BaseOperationModule abstraction

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import subprocess
import sys
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


class ToolingVerificationModule(BaseOperationModule):
    """
    Setup module for development tooling verification.
    
    Responsibilities:
    1. Verify git installation and version
    2. Verify Python installation and version
    3. Verify pytest installation (optional)
    4. Verify other common dev tools
    5. Report tool status summary
    """
    
    REQUIRED_TOOLS = {
        'git': {
            'command': ['git', '--version'],
            'min_version': None,
            'optional': False
        },
        'python': {
            'command': [sys.executable, '--version'],
            'min_version': '3.8',
            'optional': False
        }
    }
    
    OPTIONAL_TOOLS = {
        'pytest': {
            'command': [sys.executable, '-m', 'pytest', '--version'],
            'min_version': None,
            'optional': True
        },
        'pip': {
            'command': [sys.executable, '-m', 'pip', '--version'],
            'min_version': None,
            'optional': True
        }
    }
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Return module metadata."""
        return OperationModuleMetadata(
            module_id="tooling_verification",
            name="Development Tooling Verification",
            description="Verify development tools (git, python, etc.) are installed",
            phase=OperationPhase.VALIDATION,
            priority=20,
            dependencies=[],
            optional=True,  # Optional validation
        )
    
    def validate_prerequisites(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate prerequisites for tooling verification.
        
        Minimal requirements - can always run.
        """
        return True, []
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Execute tooling verification.
        
        Steps:
        1. Check required tools (git, python)
        2. Check optional tools (pytest, pip)
        3. Verify versions where applicable
        4. Generate tool status report
        """
        start_time = datetime.now()
        
        try:
            tool_results = {
                'required_tools': {},
                'optional_tools': {},
                'all_required_present': True,
                'warnings': []
            }
            
            # Check required tools
            for tool_name, tool_spec in self.REQUIRED_TOOLS.items():
                result = self._check_tool(tool_name, tool_spec)
                tool_results['required_tools'][tool_name] = result
                
                if result['status'] == 'installed':
                    self.log_info(f"✓ {tool_name}: {result['version']}")
                else:
                    self.log_error(f"✗ {tool_name}: {result['message']}")
                    tool_results['all_required_present'] = False
            
            # Check optional tools
            for tool_name, tool_spec in self.OPTIONAL_TOOLS.items():
                result = self._check_tool(tool_name, tool_spec)
                tool_results['optional_tools'][tool_name] = result
                
                if result['status'] == 'installed':
                    self.log_info(f"✓ {tool_name}: {result['version']}")
                elif result['status'] == 'not_found':
                    self.log_warning(f"⚠ {tool_name}: not installed (optional)")
                    tool_results['warnings'].append(f"{tool_name} not installed (optional)")
            
            # Determine overall status
            if not tool_results['all_required_present']:
                return OperationResult(
                    success=False,
                    status=OperationStatus.FAILED,
                    message="Required development tools missing",
                    data=tool_results,
                    errors=["One or more required tools not found"],
                    duration_seconds=(datetime.now() - start_time).total_seconds()
                )
            
            # Success
            context['tooling_verified'] = True
            context['tool_results'] = tool_results
            
            status = OperationStatus.SUCCESS if not tool_results['warnings'] else OperationStatus.WARNING
            message = "All required development tools verified"
            
            duration_seconds = (datetime.now() - start_time).total_seconds()
            
            return OperationResult(
                success=True,
                status=status,
                message=message,
                data=tool_results,
                warnings=tool_results['warnings'] if tool_results['warnings'] else None,
                duration_seconds=duration_seconds
            )
            
        except Exception as e:
            self.log_error(f"Tooling verification failed: {e}")
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Tooling verification failed: {str(e)}",
                errors=[str(e)],
                duration_seconds=(datetime.now() - start_time).total_seconds()
            )
    
    def _check_tool(self, tool_name: str, tool_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if a tool is installed and get version.
        
        Args:
            tool_name: Name of tool (e.g., 'git', 'python')
            tool_spec: Tool specification with command and version requirements
        
        Returns:
            Dictionary with tool status
        """
        try:
            result = subprocess.run(
                tool_spec['command'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                version = result.stdout.strip() or result.stderr.strip()
                
                # Check minimum version if specified
                min_version = tool_spec.get('min_version')
                if min_version:
                    version_ok = self._check_version(version, min_version)
                    if not version_ok:
                        return {
                            'status': 'version_too_old',
                            'version': version,
                            'min_version': min_version,
                            'message': f'Version {version} below minimum {min_version}'
                        }
                
                return {
                    'status': 'installed',
                    'version': version,
                    'message': 'Tool available'
                }
            else:
                return {
                    'status': 'error',
                    'message': f'Tool returned error code {result.returncode}',
                    'output': result.stderr
                }
                
        except FileNotFoundError:
            return {
                'status': 'not_found',
                'message': 'Tool not found in PATH'
            }
        except subprocess.TimeoutExpired:
            return {
                'status': 'timeout',
                'message': 'Tool command timed out'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error checking tool: {str(e)}'
            }
    
    def _check_version(self, version_str: str, min_version: str) -> bool:
        """
        Compare version strings (basic implementation).
        
        Args:
            version_str: Actual version string
            min_version: Minimum required version
        
        Returns:
            True if version meets minimum, False otherwise
        """
        try:
            # Extract version numbers (e.g., "Python 3.10.0" -> "3.10.0")
            import re
            actual_match = re.search(r'(\d+\.\d+(?:\.\d+)?)', version_str)
            if not actual_match:
                return True  # Can't parse, assume OK
            
            actual = actual_match.group(1)
            
            # Compare version parts
            actual_parts = [int(x) for x in actual.split('.')]
            min_parts = [int(x) for x in min_version.split('.')]
            
            # Pad shorter version
            while len(actual_parts) < len(min_parts):
                actual_parts.append(0)
            while len(min_parts) < len(actual_parts):
                min_parts.append(0)
            
            return actual_parts >= min_parts
            
        except (ValueError, AttributeError):
            return True  # Can't compare, assume OK
