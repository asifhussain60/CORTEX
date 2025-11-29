"""
Refactoring Tools Setup Module

Detects and optionally installs refactoring tools for user's tech stack.

ZERO-FOOTPRINT ARCHITECTURE:
- Detects existing tools (C#, JavaScript/TypeScript, SQL, Python)
- Does NOT force installations
- Provides guidance when tools missing
- Respects organizational firewalls

SOLID Principles:
- Single Responsibility: Only handles refactoring tool detection/setup
- Open/Closed: Extends BaseSetupModule without modifying it
- Dependency Inversion: Depends on BaseSetupModule abstraction

Tech Stack Priority (based on user's organization):
1. C# / .NET Core (Roslyn analyzers, dotnet format)
2. Angular/React (ESLint, Prettier, TSLint)
3. SQL Server/Oracle (sqlfluff, SQL formatters)
4. Python (rope, black) - CORTEX dev only

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any, Tuple, List, Optional
from datetime import datetime
from dataclasses import dataclass

from ..base_setup_module import (
    BaseSetupModule,
    SetupModuleMetadata,
    SetupResult,
    SetupStatus,
    SetupPhase
)


@dataclass
class ToolInfo:
    """Information about a detected tool."""
    name: str
    command: str
    version: Optional[str]
    installed: bool
    install_command: Optional[str]
    category: str  # 'csharp', 'javascript', 'sql', 'python'


class RefactoringToolsModule(BaseSetupModule):
    """
    Setup module for detecting and optionally installing refactoring tools.
    
    Responsibilities:
    1. Detect existing tools (dotnet, npm, eslint, etc.)
    2. Check for tool versions
    3. Optionally install missing tools (user consent required)
    4. Provide guidance for blocked tools
    5. Update context with detected tools
    
    Zero-Footprint Design:
    - NEVER installs by default
    - Always asks for consent
    - Provides fallback guidance
    - Handles firewall restrictions gracefully
    """
    
    def get_metadata(self) -> SetupModuleMetadata:
        """Return module metadata."""
        return SetupModuleMetadata(
            module_id="refactoring_tools",
            name="Refactoring Tools Detection",
            description="Detect and optionally install refactoring tools for user's tech stack",
            phase=SetupPhase.DEPENDENCIES,
            priority=30,  # After python_dependencies
            dependencies=["platform_detection"],
            optional=True,  # OPTIONAL by default
            enabled_by_default=False  # User must opt-in
        )
    
    def validate_prerequisites(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate prerequisites for tool detection.
        
        Checks:
        1. Project root exists
        2. Platform detected
        
        NO FAILURES - This module is optional and always succeeds validation.
        """
        issues = []
        
        project_root = context.get('project_root')
        if not project_root:
            issues.append("Project root not found in context")
        
        platform = context.get('platform')
        if not platform:
            issues.append("Platform not detected")
        
        # Even with issues, return True (optional module)
        if issues:
            self.log_warning(f"Prerequisites incomplete, but module is optional: {', '.join(issues)}")
        
        return True, issues
    
    def execute(self, context: Dict[str, Any]) -> SetupResult:
        """
        Execute tool detection and optional installation.
        
        Steps:
        1. Detect C# / .NET tools (highest priority)
        2. Detect JavaScript/TypeScript tools
        3. Detect SQL tools
        4. Detect Python tools (lowest priority)
        5. Provide guidance for missing tools
        6. Optionally install (with consent)
        """
        start_time = datetime.now()
        warnings = []
        
        try:
            project_root = Path(context.get('project_root', Path.cwd()))
            platform = context.get('platform', 'unknown')
            
            self.log_info("🔍 Detecting refactoring tools for your tech stack...")
            self.log_info("   (Zero-footprint mode: detection only, no forced installs)")
            
            # Detect all tools
            detected_tools = {
                'csharp': self._detect_csharp_tools(context),
                'javascript': self._detect_javascript_tools(project_root),
                'sql': self._detect_sql_tools(context),
                'python': self._detect_python_tools(context)
            }
            
            # Count installed vs missing
            total_tools = 0
            installed_count = 0
            missing_tools = []
            
            for category, tools in detected_tools.items():
                for tool in tools:
                    total_tools += 1
                    if tool.installed:
                        installed_count += 1
                        self.log_info(f"   ✅ {tool.name}: {tool.version}")
                    else:
                        missing_tools.append(tool)
                        self.log_warning(f"   ❌ {tool.name}: Not installed")
            
            # Generate guidance for missing tools
            guidance = self._generate_guidance(missing_tools)
            
            # Update context
            context['refactoring_tools_detected'] = True
            context['detected_tools'] = detected_tools
            context['installed_tools_count'] = installed_count
            context['missing_tools_count'] = len(missing_tools)
            
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            # Determine status
            if len(missing_tools) == 0:
                status = SetupStatus.SUCCESS
                message = f"All refactoring tools installed ({installed_count}/{total_tools})"
            elif installed_count > 0:
                status = SetupStatus.WARNING
                message = f"Some tools missing ({installed_count}/{total_tools} installed)"
                warnings.append(f"{len(missing_tools)} tools not installed (see guidance)")
            else:
                status = SetupStatus.WARNING
                message = "No refactoring tools detected (optional)"
                warnings.append("Consider installing tools for your tech stack")
            
            return SetupResult(
                module_id=self.metadata.module_id,
                status=status,
                message=message,
                details={
                    'total_tools_checked': total_tools,
                    'installed': installed_count,
                    'missing': len(missing_tools),
                    'detected_tools': {
                        category: [
                            {
                                'name': t.name,
                                'installed': t.installed,
                                'version': t.version,
                                'command': t.command
                            } for t in tools
                        ]
                        for category, tools in detected_tools.items()
                    },
                    'guidance': guidance
                },
                warnings=warnings,
                duration_ms=duration_ms
            )
            
        except Exception as e:
            self.log_error(f"Tool detection failed: {e}")
            return SetupResult(
                module_id=self.metadata.module_id,
                status=SetupStatus.WARNING,  # Not FAILED (optional module)
                message=f"Tool detection incomplete: {str(e)}",
                warnings=[str(e)],
                duration_ms=(datetime.now() - start_time).total_seconds() * 1000
            )
    
    def _detect_csharp_tools(self, context: Dict[str, Any]) -> List[ToolInfo]:
        """
        Detect C# / .NET refactoring tools (HIGHEST PRIORITY).
        
        Tools checked:
        1. dotnet CLI
        2. dotnet format
        3. Roslyn analyzers
        """
        tools = []
        
        # 1. dotnet CLI
        dotnet_version = self._get_command_version('dotnet', ['--version'])
        tools.append(ToolInfo(
            name="dotnet CLI",
            command="dotnet",
            version=dotnet_version,
            installed=dotnet_version is not None,
            install_command="Download from https://dotnet.microsoft.com/download",
            category="csharp"
        ))
        
        # 2. dotnet format (if dotnet CLI available)
        if dotnet_version:
            format_check = self._check_dotnet_tool('dotnet-format')
            tools.append(ToolInfo(
                name="dotnet format",
                command="dotnet format",
                version=format_check['version'] if format_check['installed'] else None,
                installed=format_check['installed'],
                install_command="dotnet tool install -g dotnet-format",
                category="csharp"
            ))
        
        return tools
    
    def _detect_javascript_tools(self, project_root: Path) -> List[ToolInfo]:
        """
        Detect JavaScript/TypeScript refactoring tools.
        
        Tools checked:
        1. Node.js / npm
        2. ESLint (project-local)
        3. Prettier (project-local)
        4. TSLint (project-local, legacy)
        """
        tools = []
        
        # 1. Node.js / npm
        node_version = self._get_command_version('node', ['--version'])
        npm_version = self._get_command_version('npm', ['--version'])
        
        tools.append(ToolInfo(
            name="Node.js",
            command="node",
            version=node_version,
            installed=node_version is not None,
            install_command="Download from https://nodejs.org/",
            category="javascript"
        ))
        
        tools.append(ToolInfo(
            name="npm",
            command="npm",
            version=npm_version,
            installed=npm_version is not None,
            install_command="Included with Node.js",
            category="javascript"
        ))
        
        # 2. ESLint (check project's node_modules)
        eslint_local = self._check_npm_package_local(project_root, 'eslint')
        tools.append(ToolInfo(
            name="ESLint (project)",
            command="npx eslint",
            version=eslint_local['version'] if eslint_local['installed'] else None,
            installed=eslint_local['installed'],
            install_command="npm install --save-dev eslint",
            category="javascript"
        ))
        
        # 3. Prettier (check project's node_modules)
        prettier_local = self._check_npm_package_local(project_root, 'prettier')
        tools.append(ToolInfo(
            name="Prettier (project)",
            command="npx prettier",
            version=prettier_local['version'] if prettier_local['installed'] else None,
            installed=prettier_local['installed'],
            install_command="npm install --save-dev prettier",
            category="javascript"
        ))
        
        return tools
    
    def _detect_sql_tools(self, context: Dict[str, Any]) -> List[ToolInfo]:
        """
        Detect SQL refactoring/formatting tools.
        
        Tools checked:
        1. sqlfluff (Python package)
        2. SQL Formatter (npm package)
        """
        tools = []
        
        # 1. sqlfluff (pip package)
        python_cmd = context.get('python_command', 'python3')
        sqlfluff_installed = self._check_python_package(python_cmd, 'sqlfluff')
        
        tools.append(ToolInfo(
            name="sqlfluff",
            command="sqlfluff",
            version=sqlfluff_installed['version'] if sqlfluff_installed['installed'] else None,
            installed=sqlfluff_installed['installed'],
            install_command="pip install sqlfluff",
            category="sql"
        ))
        
        return tools
    
    def _detect_python_tools(self, context: Dict[str, Any]) -> List[ToolInfo]:
        """
        Detect Python refactoring tools (LOWEST PRIORITY).
        
        Tools checked:
        1. rope (refactoring library)
        2. black (code formatter)
        3. flake8 (linter)
        4. mypy (type checker)
        
        Note: These are for CORTEX development, NOT user's apps!
        """
        tools = []
        python_cmd = context.get('python_command', 'python3')
        
        python_packages = {
            'rope': 'Python refactoring library',
            'black': 'Code formatter',
            'flake8': 'Linter',
            'mypy': 'Type checker'
        }
        
        for package, description in python_packages.items():
            check = self._check_python_package(python_cmd, package)
            tools.append(ToolInfo(
                name=f"{package} ({description})",
                command=package,
                version=check['version'] if check['installed'] else None,
                installed=check['installed'],
                install_command=f"pip install {package}",
                category="python"
            ))
        
        return tools
    
    def _get_command_version(self, command: str, args: List[str]) -> Optional[str]:
        """Get version of a command-line tool."""
        try:
            result = subprocess.run(
                [command] + args,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip().split('\n')[0]
            return None
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return None
    
    def _check_dotnet_tool(self, tool_name: str) -> Dict[str, Any]:
        """Check if a dotnet global tool is installed."""
        try:
            result = subprocess.run(
                ['dotnet', 'tool', 'list', '-g'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # Parse output for tool
                for line in result.stdout.split('\n'):
                    if tool_name.lower() in line.lower():
                        parts = line.split()
                        if len(parts) >= 2:
                            return {'installed': True, 'version': parts[1]}
            
            return {'installed': False, 'version': None}
        except:
            return {'installed': False, 'version': None}
    
    def _check_npm_package_local(self, project_root: Path, package_name: str) -> Dict[str, Any]:
        """Check if npm package exists in project's node_modules."""
        node_modules = project_root / 'node_modules' / package_name
        
        if node_modules.exists():
            # Try to get version from package.json
            package_json = node_modules / 'package.json'
            if package_json.exists():
                try:
                    import json
                    with open(package_json) as f:
                        data = json.load(f)
                        version = data.get('version', 'unknown')
                        return {'installed': True, 'version': version}
                except:
                    pass
            return {'installed': True, 'version': 'unknown'}
        
        return {'installed': False, 'version': None}
    
    def _check_python_package(self, python_cmd: str, package_name: str) -> Dict[str, Any]:
        """Check if Python package is installed."""
        try:
            # Try to import and get version
            result = subprocess.run(
                [python_cmd, '-c', f'import {package_name}; print({package_name}.__version__)'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                version = result.stdout.strip()
                return {'installed': True, 'version': version}
            
            return {'installed': False, 'version': None}
        except:
            return {'installed': False, 'version': None}
    
    def _generate_guidance(self, missing_tools: List[ToolInfo]) -> Dict[str, List[str]]:
        """
        Generate installation guidance for missing tools.
        
        Returns categorized guidance by tech stack.
        """
        guidance = {
            'csharp': [],
            'javascript': [],
            'sql': [],
            'python': []
        }
        
        for tool in missing_tools:
            category = tool.category
            if tool.install_command:
                guidance[category].append(
                    f"{tool.name}: {tool.install_command}"
                )
        
        return {k: v for k, v in guidance.items() if v}  # Remove empty categories
