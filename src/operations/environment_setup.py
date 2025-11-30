"""
CORTEX Environment Setup - Monolithic Script

Single-script implementation for environment setup operation.
Consolidates 11 modules into one cohesive workflow.

Design Philosophy (CORTEX 3.0):
- Monolithic-then-modular: Ship working MVP first
- User value over perfect architecture
- Refactor only when complexity warrants (>500 lines)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0 (CORTEX 3.0 Phase 1.1)
"""

import os
import sys
import platform
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class SetupResult:
    """Result of environment setup operation."""
    success: bool
    profile: str
    steps_completed: List[str] = field(default_factory=list)
    steps_failed: List[str] = field(default_factory=list)
    steps_skipped: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    duration_seconds: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    platform_info: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'success': self.success,
            'profile': self.profile,
            'steps_completed': self.steps_completed,
            'steps_failed': self.steps_failed,
            'steps_skipped': self.steps_skipped,
            'warnings': self.warnings,
            'duration_seconds': self.duration_seconds,
            'timestamp': self.timestamp.isoformat(),
            'platform_info': self.platform_info
        }


class EnvironmentSetup:
    """
    Monolithic environment setup for CORTEX.
    
    Consolidates functionality from 11 modules:
    - project_validation
    - platform_detection
    - git_sync
    - virtual_environment
    - python_dependencies
    - vision_api
    - conversation_tracking
    - brain_initialization
    - brain_tests
    - tooling_verification
    - setup_completion
    """
    
    def __init__(self, project_root: Optional[Path] = None):
        """Initialize setup."""
        self.project_root = project_root or Path.cwd()
        self.result = SetupResult(success=False, profile='unknown')
        self.start_time = datetime.now()
        
    def run(self, profile: str = 'standard') -> SetupResult:
        """
        Execute environment setup.
        
        Args:
            profile: Setup profile (minimal, standard, full)
            
        Returns:
            SetupResult with execution details
        """
        self.result.profile = profile
        
        print("=" * 80)
        print("CORTEX Environment Setup")
        print("=" * 80)
        print(f"Profile: {profile}")
        print(f"Project Root: {self.project_root}")
        print(f"Timestamp: {self.start_time.isoformat()}")
        print()
        
        try:
            # Step 1: Validate project structure
            if not self._validate_project():
                self.result.success = False
                return self.result
            
            # Step 2: Detect platform
            if not self._detect_platform():
                self.result.success = False
                return self.result
            
            # Step 3: Sync git repository (standard/full profiles)
            if profile in ['standard', 'full']:
                if not self._sync_git():
                    self.result.warnings.append("Git sync failed - continuing anyway")
                    self.result.steps_skipped.append('git_sync')
            
            # Step 4: Setup virtual environment
            if not self._setup_virtualenv():
                self.result.success = False
                return self.result
            
            # Step 5: Install Python dependencies
            if not self._install_dependencies():
                self.result.success = False
                return self.result
            
            # Step 6: Configure Vision API (standard/full profiles)
            if profile in ['standard', 'full']:
                if not self._configure_vision_api():
                    self.result.warnings.append("Vision API not configured - optional feature")
                    self.result.steps_skipped.append('vision_api')
            
            # Step 7: Enable conversation tracking (full profile only)
            if profile == 'full':
                if not self._enable_conversation_tracking():
                    self.result.warnings.append("Conversation tracking not enabled - optional feature")
                    self.result.steps_skipped.append('conversation_tracking')
            
            # Step 8: Initialize CORTEX brain
            if not self._initialize_brain():
                self.result.success = False
                return self.result
            
            # Step 9: Run brain tests (standard/full profiles)
            if profile in ['standard', 'full']:
                if not self._run_brain_tests():
                    self.result.warnings.append("Brain tests incomplete - review warnings")
                    self.result.steps_skipped.append('brain_tests')
            
            # Step 10: Verify tooling (full profile only)
            if profile == 'full':
                if not self._verify_tooling():
                    self.result.warnings.append("Some tools not available - optional features")
                    self.result.steps_skipped.append('tooling_verification')
            
            # Step 11: Completion
            self._complete_setup()
            
            self.result.success = True
            
        except Exception as e:
            print(f"\n❌ Setup failed with error: {e}")
            self.result.success = False
            self.result.steps_failed.append(f"exception: {str(e)}")
        
        finally:
            # Calculate duration
            end_time = datetime.now()
            self.result.duration_seconds = (end_time - self.start_time).total_seconds()
            
            # Print summary
            self._print_summary()
        
        return self.result
    
    def _validate_project(self) -> bool:
        """Validate CORTEX project structure."""
        print("📋 Step 1: Validating project structure...")
        
        required_dirs = ['cortex-brain', 'src', 'tests', 'prompts', '.github']
        required_files = ['README.md', 'requirements.txt', 'cortex.config.json']
        
        missing_dirs = []
        missing_files = []
        
        for dir_name in required_dirs:
            dir_path = self.project_root / dir_name
            if not dir_path.exists():
                missing_dirs.append(dir_name)
        
        for file_name in required_files:
            file_path = self.project_root / file_name
            if not file_path.exists():
                missing_files.append(file_name)
        
        if missing_dirs or missing_files:
            print(f"❌ Project validation failed")
            if missing_dirs:
                print(f"   Missing directories: {', '.join(missing_dirs)}")
            if missing_files:
                print(f"   Missing files: {', '.join(missing_files)}")
            self.result.steps_failed.append('project_validation')
            return False
        
        print("✅ Project structure valid")
        self.result.steps_completed.append('project_validation')
        return True
    
    def _detect_platform(self) -> bool:
        """Detect and configure platform."""
        print("\n🖥️  Step 2: Detecting platform...")
        
        system = platform.system()
        machine = platform.machine()
        python_version = platform.python_version()
        
        platform_map = {
            'Darwin': 'mac',
            'Windows': 'windows',
            'Linux': 'linux'
        }
        
        platform_name = platform_map.get(system, 'unknown')
        
        self.result.platform_info = {
            'os': platform_name,
            'system': system,
            'machine': machine,
            'python_version': python_version,
            'python_executable': sys.executable
        }
        
        if platform_name == 'unknown':
            print(f"⚠️  Unknown platform: {system}")
            self.result.warnings.append(f"Unknown platform: {system}")
        else:
            print(f"✅ Platform detected: {platform_name} ({system} {machine})")
            print(f"   Python: {python_version} ({sys.executable})")
        
        self.result.steps_completed.append('platform_detection')
        return True
    
    def _sync_git(self) -> bool:
        """Sync git repository."""
        print("\n📦 Step 3: Syncing git repository...")
        
        try:
            # Check if .git directory exists
            git_dir = self.project_root / '.git'
            if not git_dir.exists():
                print("⚠️  Not a git repository - skipping")
                return False
            
            # Check git status
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                if result.stdout.strip():
                    print(f"⚠️  Uncommitted changes detected - skipping pull")
                    self.result.warnings.append("Uncommitted changes - git pull skipped")
                    return False  # Don't mark as completed if skipped
                else:
                    # Pull latest changes
                    pull_result = subprocess.run(
                        ['git', 'pull'],
                        cwd=self.project_root,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    if pull_result.returncode == 0:
                        print("✅ Git repository synced")
                        self.result.steps_completed.append('git_sync')
                        return True
                    else:
                        print(f"⚠️  Git pull failed: {pull_result.stderr}")
                        return False
            else:
                print(f"⚠️  Git status check failed")
                return False
            
        except subprocess.TimeoutExpired:
            print("⚠️  Git operation timed out")
            return False
        except FileNotFoundError:
            print("⚠️  Git not found - install git first")
            return False
        except Exception as e:
            print(f"⚠️  Git sync error: {e}")
            return False
    
    def _setup_virtualenv(self) -> bool:
        """Setup or verify virtual environment."""
        print("\n🐍 Step 4: Setting up virtual environment...")
        
        # Check if we're already in a virtual environment
        in_venv = hasattr(sys, 'real_prefix') or (
            hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
        )
        
        if in_venv:
            print(f"✅ Already in virtual environment: {sys.prefix}")
            self.result.steps_completed.append('virtual_environment')
            return True
        
        # Check for common virtual environment directories
        venv_dirs = ['.venv', 'venv', 'env']
        existing_venv = None
        
        for venv_name in venv_dirs:
            venv_path = self.project_root / venv_name
            if venv_path.exists():
                existing_venv = venv_path
                break
        
        if existing_venv:
            print(f"✅ Virtual environment found: {existing_venv.name}")
            print(f"   Activate with: source {existing_venv}/bin/activate (Mac/Linux)")
            print(f"   Activate with: {existing_venv}\\Scripts\\activate (Windows)")
            self.result.warnings.append(f"Virtual environment exists but not active - activate manually")
        else:
            print("⚠️  No virtual environment found")
            print("   Create with: python -m venv .venv")
            self.result.warnings.append("No virtual environment - recommended to create one")
        
        self.result.steps_completed.append('virtual_environment')
        return True
    
    def _install_dependencies(self) -> bool:
        """Install Python dependencies."""
        print("\n📦 Step 5: Installing Python dependencies...")
        
        requirements_file = self.project_root / 'requirements.txt'
        
        if not requirements_file.exists():
            print("❌ requirements.txt not found")
            self.result.steps_failed.append('python_dependencies')
            return False
        
        try:
            # Upgrade pip first
            print("   Upgrading pip...")
            pip_upgrade = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if pip_upgrade.returncode != 0:
                print(f"⚠️  Pip upgrade failed (continuing anyway)")
            
            # Install dependencies
            print(f"   Installing from {requirements_file.name}...")
            install_result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if install_result.returncode != 0:
                print(f"❌ Dependency installation failed:")
                print(install_result.stderr)
                self.result.steps_failed.append('python_dependencies')
                return False
            
            print("✅ Dependencies installed successfully")
            self.result.steps_completed.append('python_dependencies')
            return True
            
        except subprocess.TimeoutExpired:
            print("❌ Installation timed out (>5 minutes)")
            self.result.steps_failed.append('python_dependencies')
            return False
        except Exception as e:
            print(f"❌ Installation error: {e}")
            self.result.steps_failed.append('python_dependencies')
            return False
    
    def _configure_vision_api(self) -> bool:
        """Configure Vision API (placeholder)."""
        print("\n👁️  Step 6: Configuring Vision API...")
        print("   Vision API configuration is optional")
        print("   Skipping for MVP (can configure manually later)")
        return False  # Intentionally skip for MVP
    
    def _enable_conversation_tracking(self) -> bool:
        """Enable conversation tracking."""
        print("\n💬 Step 7: Enabling conversation tracking...")
        
        # Check if conversation database exists
        db_path = self.project_root / 'cortex-brain' / 'conversation-history.db'
        
        if db_path.exists():
            print(f"✅ Conversation tracking database exists")
            self.result.steps_completed.append('conversation_tracking')
            return True
        else:
            print("⚠️  Conversation tracking database not initialized")
            print("   Will be created on first use")
            return False
    
    def _initialize_brain(self) -> bool:
        """Initialize CORTEX brain."""
        print("\n🧠 Step 8: Initializing CORTEX brain...")
        
        brain_dir = self.project_root / 'cortex-brain'
        
        if not brain_dir.exists():
            print("❌ cortex-brain directory not found")
            self.result.steps_failed.append('brain_initialization')
            return False
        
        # Check for essential brain files
        essential_files = [
            'brain-protection-rules.yaml',
            'knowledge-graph.yaml',
            'response-templates.yaml'
        ]
        
        missing_files = []
        for file_name in essential_files:
            file_path = brain_dir / file_name
            if not file_path.exists():
                missing_files.append(file_name)
        
        if missing_files:
            print(f"⚠️  Missing brain files: {', '.join(missing_files)}")
            self.result.warnings.append(f"Missing brain files - may need initialization")
        else:
            print("✅ CORTEX brain initialized")
        
        self.result.steps_completed.append('brain_initialization')
        return True
    
    def _run_brain_tests(self) -> bool:
        """Run brain protection tests."""
        print("\n🧪 Step 9: Running brain tests...")
        
        try:
            # Run quick test suite
            test_result = subprocess.run(
                [sys.executable, '-m', 'pytest', 'tests/tier0/', '-v', '--tb=short'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if test_result.returncode == 0:
                print("✅ Brain tests passed")
                self.result.steps_completed.append('brain_tests')
                return True
            else:
                print("⚠️  Some brain tests failed")
                print(test_result.stdout[-500:] if len(test_result.stdout) > 500 else test_result.stdout)
                return False
                
        except subprocess.TimeoutExpired:
            print("⚠️  Tests timed out")
            return False
        except FileNotFoundError:
            print("⚠️  pytest not found - install dependencies first")
            return False
        except Exception as e:
            print(f"⚠️  Test error: {e}")
            return False
    
    def _verify_tooling(self) -> bool:
        """Verify optional tooling."""
        print("\n🔧 Step 10: Verifying tooling...")
        
        tools = {
            'git': ['git', '--version'],
            'pytest': [sys.executable, '-m', 'pytest', '--version'],
            'mkdocs': [sys.executable, '-m', 'mkdocs', '--version']
        }
        
        available = []
        missing = []
        
        for tool_name, cmd in tools.items():
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    available.append(tool_name)
                else:
                    missing.append(tool_name)
            except (subprocess.TimeoutExpired, FileNotFoundError):
                missing.append(tool_name)
        
        if available:
            print(f"✅ Available tools: {', '.join(available)}")
        if missing:
            print(f"⚠️  Missing tools: {', '.join(missing)}")
        
        self.result.steps_completed.append('tooling_verification')
        return len(missing) == 0
    
    def _complete_setup(self) -> None:
        """Complete setup process."""
        print("\n🎉 Step 11: Completing setup...")
        
        # Save setup report
        report_dir = self.project_root / 'cortex-brain' / 'setup-reports'
        report_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = report_dir / f'setup-{timestamp}.json'
        
        try:
            with open(report_file, 'w') as f:
                json.dump(self.result.to_dict(), f, indent=2)
            print(f"✅ Setup report saved: {report_file.name}")
        except Exception as e:
            print(f"⚠️  Could not save report: {e}")
        
        self.result.steps_completed.append('setup_completion')
    
    def _print_summary(self) -> None:
        """Print setup summary."""
        print("\n" + "=" * 80)
        print("SETUP SUMMARY")
        print("=" * 80)
        print(f"Status: {'✅ SUCCESS' if self.result.success else '❌ FAILED'}")
        print(f"Profile: {self.result.profile}")
        print(f"Duration: {self.result.duration_seconds:.2f}s")
        print()
        
        if self.result.steps_completed:
            print(f"Completed ({len(self.result.steps_completed)}):")
            for step in self.result.steps_completed:
                print(f"  ✅ {step}")
        
        if self.result.steps_skipped:
            print(f"\nSkipped ({len(self.result.steps_skipped)}):")
            for step in self.result.steps_skipped:
                print(f"  ⏭️  {step}")
        
        if self.result.steps_failed:
            print(f"\nFailed ({len(self.result.steps_failed)}):")
            for step in self.result.steps_failed:
                print(f"  ❌ {step}")
        
        if self.result.warnings:
            print(f"\nWarnings ({len(self.result.warnings)}):")
            for warning in self.result.warnings:
                print(f"  ⚠️  {warning}")
        
        print("\n" + "=" * 80)


def run_setup(profile: str = 'standard', project_root: Optional[Path] = None) -> SetupResult:
    """
    Run environment setup.
    
    Args:
        profile: Setup profile (minimal, standard, full)
        project_root: Project root directory (default: current directory)
        
    Returns:
        SetupResult with execution details
    """
    setup = EnvironmentSetup(project_root=project_root)
    return setup.run(profile=profile)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='CORTEX Environment Setup')
    parser.add_argument(
        'profile',
        nargs='?',
        default='standard',
        choices=['minimal', 'standard', 'full'],
        help='Setup profile (default: standard)'
    )
    parser.add_argument(
        '--project-root',
        type=Path,
        default=None,
        help='Project root directory (default: current directory)'
    )
    
    args = parser.parse_args()
    
    result = run_setup(profile=args.profile, project_root=args.project_root)
    
    # Exit with appropriate code
    sys.exit(0 if result.success else 1)
