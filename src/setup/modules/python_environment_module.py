"""
Python Environment Setup Module

Intelligently detects and manages Python environments for CORTEX.

Strategy:
- Reuse existing environments when dependencies are satisfied
- Create isolated environment when conflicts detected
- Preserve user's global Python installation
- Validate brain database compatibility

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sys
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from ..base_setup_module import (
    BaseSetupModule,
    SetupModuleMetadata,
    SetupResult,
    SetupStatus,
    SetupPhase
)


@dataclass
class EnvironmentAnalysis:
    """Results of Python environment analysis."""
    is_virtual_env: bool
    environment_path: Path
    python_version: Tuple[int, int, int]
    is_global: bool
    parent_project: Optional[str]
    dependencies_satisfied: bool
    conflicts: List[str]
    missing_packages: List[str]
    action_recommendation: str
    reason: str


class PythonEnvironmentModule(BaseSetupModule):
    """
    Analyzes and configures Python environment for CORTEX.
    
    Decision Logic:
    1. Global Python → Always create isolated venv
    2. Existing venv + satisfied deps → Reuse environment
    3. Existing venv + conflicts → Create CORTEX venv
    4. Embedded installation + compatible → Reuse parent
    5. Embedded installation + conflicts → Isolate CORTEX
    """
    
    # CORTEX required packages with version constraints
    REQUIRED_PACKAGES = {
        'pytest': '>=8.4.0',
        'PyYAML': '>=6.0.2',
        'watchdog': '>=6.0.0',
        'psutil': '>=6.1.1',
        'scikit-learn': '>=1.5.2',
        'PyGithub': '>=2.5.0',
        'tree-sitter': '>=0.20.1',
        'python-docx': '>=1.1.0',
        'PyPDF2': '>=3.0.0'
    }
    
    def __init__(self):
        """Initialize Python environment module."""
        super().__init__()
        self.logger = logging.getLogger(__name__)
    
    def get_metadata(self) -> SetupModuleMetadata:
        """Module metadata."""
        return SetupModuleMetadata(
            module_id="python_environment",
            name="Python Environment Setup",
            description="Detect and configure Python environment with intelligent reuse",
            phase=SetupPhase.ENVIRONMENT,
            priority=10,  # Early phase - needed by all other modules
            dependencies=[],
            optional=False
        )
    
    def validate_prerequisites(self, context: Dict) -> Tuple[bool, str]:
        """Validate Python is available."""
        try:
            # Check Python version
            version_info = sys.version_info
            if version_info < (3, 8):
                # Handle both named tuple and regular tuple
                major = version_info[0] if isinstance(version_info, tuple) else version_info.major
                minor = version_info[1] if isinstance(version_info, tuple) else version_info.minor
                return False, f"Python 3.8+ required, found {major}.{minor}"
            
            return True, "Python 3.8+ detected"
        except Exception as e:
            return False, f"Failed to validate Python: {e}"
    
    def execute(self, context: Dict) -> SetupResult:
        """
        Analyze and configure Python environment.
        
        Args:
            context: Setup context with project_root
        
        Returns:
            SetupResult with environment configuration
        """
        try:
            self.logger.info("🔍 Analyzing Python environment...")
            
            # Analyze current environment
            analysis = self._analyze_environment(context)
            
            # Log analysis
            self._log_analysis(analysis)
            
            # Execute recommended action
            if analysis.action_recommendation == "reuse_environment":
                result = self._configure_reuse(analysis, context)
            elif analysis.action_recommendation == "create_venv":
                result = self._create_venv(analysis, context)
            else:
                raise ValueError(f"Unknown action: {analysis.action_recommendation}")
            
            # Store analysis in context for other modules
            context['environment_analysis'] = analysis
            context['environment_path'] = result.details.get('environment_path')
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Environment setup failed: {e}")
            return SetupResult(
                module_id=self.metadata.module_id,
                status=SetupStatus.FAILED,
                message=f"Environment setup failed: {e}",
                details={'error': str(e)}
            )
    
    def rollback(self, context: Dict) -> bool:
        """Rollback environment changes if needed."""
        try:
            # Check if we created a new venv
            venv_path = context.get('cortex_venv_path')
            if venv_path and Path(venv_path).exists():
                self.logger.info(f"🗑️ Removing created venv: {venv_path}")
                import shutil
                shutil.rmtree(venv_path)
                return True
            return True
        except Exception as e:
            self.logger.error(f"❌ Rollback failed: {e}")
            return False
    
    def _analyze_environment(self, context: Dict) -> EnvironmentAnalysis:
        """Analyze current Python environment."""
        
        # Detect environment type
        is_virtual_env = hasattr(sys, 'real_prefix') or (
            hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
        )
        
        environment_path = Path(sys.prefix)
        python_version = sys.version_info[:3]
        is_global = not is_virtual_env
        
        # Detect parent project (for embedded installations)
        parent_project = self._detect_parent_project(context)
        
        # Check dependencies
        missing_packages, conflicts = self._check_dependencies()
        dependencies_satisfied = not missing_packages and not conflicts
        
        # Determine action
        if is_global:
            action = "create_venv"
            reason = "Global Python environment - isolation required for safety"
        elif dependencies_satisfied:
            action = "reuse_environment"
            reason = f"Existing environment compatible - all dependencies satisfied"
        elif parent_project and not conflicts:
            action = "reuse_environment"
            reason = f"Parent project environment compatible - missing packages will be installed"
        else:
            action = "create_venv"
            reason = f"Conflicts detected - isolated environment required"
            if conflicts:
                reason += f" ({len(conflicts)} conflicts)"
        
        return EnvironmentAnalysis(
            is_virtual_env=is_virtual_env,
            environment_path=environment_path,
            python_version=python_version,
            is_global=is_global,
            parent_project=parent_project,
            dependencies_satisfied=dependencies_satisfied,
            conflicts=conflicts,
            missing_packages=missing_packages,
            action_recommendation=action,
            reason=reason
        )
    
    def _detect_parent_project(self, context: Dict) -> Optional[str]:
        """Detect if CORTEX is embedded in a parent project."""
        project_root = context.get('project_root', Path.cwd())
        
        # Check if CORTEX is in a subdirectory
        if project_root.name == 'CORTEX':
            parent = project_root.parent
            
            # Look for common project indicators in parent
            indicators = [
                'package.json',
                'requirements.txt',
                'pyproject.toml',
                'setup.py',
                '.git'
            ]
            
            for indicator in indicators:
                if (parent / indicator).exists():
                    return parent.name
        
        return None
    
    def _check_dependencies(self) -> Tuple[List[str], List[str]]:
        """
        Check if required packages are installed and compatible.
        
        Returns:
            (missing_packages, conflicts)
        """
        missing = []
        conflicts = []
        
        for package, constraint in self.REQUIRED_PACKAGES.items():
            try:
                # Try to import package
                if package == 'PyYAML':
                    import yaml
                    installed_version = yaml.__version__
                elif package == 'PyGithub':
                    import github
                    installed_version = github.__version__
                elif package == 'python-docx':
                    import docx
                    installed_version = docx.__version__ if hasattr(docx, '__version__') else 'unknown'
                else:
                    # Dynamic import
                    module = __import__(package.lower().replace('-', '_'))
                    installed_version = getattr(module, '__version__', 'unknown')
                
                # Parse constraint
                if constraint.startswith('>='):
                    min_version = constraint[2:]
                    if installed_version != 'unknown' and installed_version < min_version:
                        conflicts.append(f"{package} {installed_version} (need {constraint})")
                
            except ImportError:
                missing.append(package)
            except Exception as e:
                self.logger.debug(f"Error checking {package}: {e}")
                missing.append(package)
        
        return missing, conflicts
    
    def _configure_reuse(self, analysis: EnvironmentAnalysis, context: Dict) -> SetupResult:
        """Configure CORTEX to reuse existing environment."""
        
        # Install missing packages if any
        if analysis.missing_packages:
            self.logger.info(f"📦 Installing {len(analysis.missing_packages)} missing packages...")
            success = self._install_packages(analysis.missing_packages)
            if not success:
                return SetupResult(
                    module_id=self.metadata.module_id,
                    status=SetupStatus.FAILED,
                    message="Failed to install missing dependencies",
                    details={'missing': analysis.missing_packages}
                )
        
        return SetupResult(
            module_id=self.metadata.module_id,
            status=SetupStatus.SUCCESS,
            message=f"✅ Reusing existing environment: {analysis.reason}",
            details={
                'action': 'reuse',
                'environment_path': str(analysis.environment_path),
                'python_version': '.'.join(map(str, analysis.python_version)),
                'parent_project': analysis.parent_project,
                'packages_installed': analysis.missing_packages
            }
        )
    
    def _create_venv(self, analysis: EnvironmentAnalysis, context: Dict) -> SetupResult:
        """Create isolated CORTEX virtual environment."""
        
        project_root = context.get('project_root', Path.cwd())
        venv_path = project_root / '.venv'
        
        self.logger.info(f"🔨 Creating isolated virtual environment: {venv_path}")
        
        try:
            # Create venv
            subprocess.run(
                [sys.executable, '-m', 'venv', str(venv_path)],
                check=True,
                capture_output=True,
                text=True
            )
            
            # Determine pip executable path
            if sys.platform == 'win32':
                pip_executable = venv_path / 'Scripts' / 'pip.exe'
            else:
                pip_executable = venv_path / 'bin' / 'pip'
            
            # Install requirements
            requirements_file = project_root / 'requirements.txt'
            if requirements_file.exists():
                self.logger.info("📦 Installing CORTEX dependencies...")
                subprocess.run(
                    [str(pip_executable), 'install', '-r', str(requirements_file)],
                    check=True,
                    capture_output=True,
                    text=True
                )
            
            # Store venv path for potential rollback
            context['cortex_venv_path'] = str(venv_path)
            
            return SetupResult(
                module_id=self.metadata.module_id,
                status=SetupStatus.SUCCESS,
                message=f"✅ Created isolated environment: {analysis.reason}",
                details={
                    'action': 'create',
                    'environment_path': str(venv_path),
                    'python_version': '.'.join(map(str, analysis.python_version)),
                    'conflicts_resolved': analysis.conflicts
                }
            )
            
        except (subprocess.CalledProcessError, Exception) as e:
            error_msg = getattr(e, 'stderr', str(e))
            return SetupResult(
                module_id=self.metadata.module_id,
                status=SetupStatus.FAILED,
                message=f"Failed to create virtual environment: {error_msg}",
                details={'error': str(e)}
            )
    
    def _install_packages(self, packages: List[str]) -> bool:
        """Install missing packages in current environment."""
        try:
            subprocess.run(
                [sys.executable, '-m', 'pip', 'install'] + packages,
                check=True,
                capture_output=True,
                text=True
            )
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to install packages: {e.stderr}")
            return False
    
    def _log_analysis(self, analysis: EnvironmentAnalysis):
        """Log environment analysis results."""
        self.logger.info("\n" + "="*60)
        self.logger.info("🔍 Python Environment Analysis")
        self.logger.info("="*60)
        self.logger.info(f"Environment Type: {'Virtual Environment' if analysis.is_virtual_env else 'Global Python'}")
        self.logger.info(f"Python Version: {'.'.join(map(str, analysis.python_version))}")
        self.logger.info(f"Environment Path: {analysis.environment_path}")
        
        if analysis.parent_project:
            self.logger.info(f"Parent Project: {analysis.parent_project} (embedded installation)")
        
        if analysis.missing_packages:
            self.logger.info(f"Missing Packages: {', '.join(analysis.missing_packages)}")
        
        if analysis.conflicts:
            self.logger.warning(f"⚠️ Conflicts Detected:")
            for conflict in analysis.conflicts:
                self.logger.warning(f"  • {conflict}")
        
        self.logger.info(f"\n💡 Recommendation: {analysis.action_recommendation}")
        self.logger.info(f"📝 Reason: {analysis.reason}")
        self.logger.info("="*60 + "\n")
