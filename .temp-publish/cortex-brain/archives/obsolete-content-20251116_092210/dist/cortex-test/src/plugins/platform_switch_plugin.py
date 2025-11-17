"""
CORTEX Platform Switch Plugin

Handles automatic platform detection and configuration when switching between
development environments (Mac/Windows/Linux).

Features:
- Automatic platform detection on startup
- Stores last known platform to detect changes
- Auto-configures environment when platform changes
- Manual /setup command for forced reconfiguration

Usage:
    - Automatic: Opens CORTEX on different platform → auto-detects and configures
    - Manual: "setup environment" or /setup → forces reconfiguration
"""

import os
import sys
import platform
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

from .base_plugin import (
    BasePlugin,
    PluginMetadata,
    PluginCategory,
    PluginPriority,
    HookPoint
)


class Platform(Enum):
    """Supported development platforms."""
    MAC = "darwin"
    WINDOWS = "win32"
    LINUX = "linux"
    
    @staticmethod
    def current() -> 'Platform':
        """Detect current platform."""
        sys_platform = sys.platform
        if sys_platform == "darwin":
            return Platform.MAC
        elif sys_platform.startswith("win"):
            return Platform.WINDOWS
        elif sys_platform.startswith("linux"):
            return Platform.LINUX
        else:
            raise ValueError(f"Unsupported platform: {sys_platform}")
    
    @property
    def display_name(self) -> str:
        """Human-readable platform name."""
        return {
            Platform.MAC: "macOS",
            Platform.WINDOWS: "Windows",
            Platform.LINUX: "Linux"
        }[self]


@dataclass
class PlatformConfig:
    """Platform-specific configuration."""
    platform: Platform
    path_separator: str
    python_command: str
    shell: str
    line_ending: str
    home_var: str
    
    @staticmethod
    def for_platform(plat: Platform) -> 'PlatformConfig':
        """Get configuration for a specific platform."""
        if plat == Platform.MAC:
            return PlatformConfig(
                platform=plat,
                path_separator="/",
                python_command="python3",
                shell="zsh",
                line_ending="\n",
                home_var="HOME"
            )
        elif plat == Platform.WINDOWS:
            return PlatformConfig(
                platform=plat,
                path_separator="\\",
                python_command="python",
                shell="powershell",
                line_ending="\r\n",
                home_var="USERPROFILE"
            )
        elif plat == Platform.LINUX:
            return PlatformConfig(
                platform=plat,
                path_separator="/",
                python_command="python3",
                shell="bash",
                line_ending="\n",
                home_var="HOME"
            )
        else:
            raise ValueError(f"Unsupported platform: {plat}")


class PlatformSwitchPlugin(BasePlugin):
    """
    Handles platform switching for CORTEX development.
    
    Automates:
    1. Git pull latest code
    2. Environment setup for platform
    3. Brain tests validation
    4. Tooling and dependencies verification
    """
    
    def __init__(self):
        self.metadata = PluginMetadata(
            plugin_id="platform_switch",
            name="Platform Switch Plugin",
            version="1.0.0",
            category=PluginCategory.INFRASTRUCTURE,
            priority=PluginPriority.HIGH,
            description="Automated platform switching and environment setup",
            author="CORTEX Team",
            dependencies=[],
            hooks=[HookPoint.ON_STARTUP.value],
            config_schema={}
        )
        self.triggers = [
            "setup environment", "configure platform", "switch platform",
            "setup", "configure environment"
        ]
        self.project_root = self._find_project_root()
        self.current_platform = Platform.current()
        self.config = PlatformConfig.for_platform(self.current_platform)
        self._logs = []
        self._platform_state_file = self.project_root / "cortex-brain" / ".platform_state.json"
    
    def log(self, message: str):
        """Log a message (stores for retrieval)."""
        print(message)
        self._logs.append(message)
    
    def get_logs(self) -> List[str]:
        """Get all logged messages."""
        return self._logs.copy()
    
    def _get_metadata(self) -> PluginMetadata:
        """Return plugin metadata (required by BasePlugin)."""
        return self.metadata
    
    def register_commands(self) -> List[Any]:
        """
        Register platform commands.
        
        Only /setup is exposed - platform detection is automatic.
        
        Returns:
            List of CommandMetadata objects
        """
        from .command_registry import CommandMetadata, CommandCategory
        
        return [
            # Manual setup/reconfiguration command
            CommandMetadata(
                command="/setup",
                natural_language_equivalent="setup environment",
                plugin_id=self.metadata.plugin_id,
                description="Setup/reconfigure development environment",
                category=CommandCategory.PLATFORM,
                aliases=["/env", "/environment", "/configure"],
                examples=["@cortex /setup", "setup environment"],
                requires_online=False
            ),
        ]
    
    def initialize(self) -> bool:
        """Initialize the plugin and check for platform changes."""
        try:
            # Verify project structure
            if not self.project_root.exists():
                self.log(f"⚠️  Project root not found: {self.project_root}")
                return False
            
            # Verify cortex-brain exists
            if not (self.project_root / "cortex-brain").exists():
                self.log("⚠️  cortex-brain directory not found")
                return False
            
            # Check for platform changes and auto-configure if needed
            self._check_and_handle_platform_change()
            
            self.log(f"✅ Plugin initialized for {self.current_platform.display_name}")
            return True
        except Exception as e:
            self.log(f"❌ Plugin initialization failed: {e}")
            return False
    
    def _check_and_handle_platform_change(self):
        """Check if platform has changed and auto-configure if needed."""
        last_platform = self._get_last_platform()
        current_platform = self.current_platform
        
        if last_platform is None:
            # First time setup
            self.log(f"🆕 First-time setup detected for {current_platform.display_name}")
            self._save_platform_state(current_platform)
            # Don't auto-configure on first run - wait for explicit command
            return
        
        if last_platform != current_platform:
            # Platform changed! Auto-configure
            self.log(f"🔄 Platform change detected: {last_platform.display_name} → {current_platform.display_name}")
            self.log(f"🤖 Auto-configuring environment...")
            
            # Execute auto-configuration
            result = self._auto_configure_platform(current_platform)
            
            if result['success']:
                self.log(f"✅ Auto-configuration complete!")
                self._save_platform_state(current_platform)
            else:
                self.log(f"⚠️  Auto-configuration had issues. Run '/setup' to retry.")
        else:
            # Same platform, no action needed
            self.log(f"✓ Running on {current_platform.display_name} (no change)")
    
    def _get_last_platform(self) -> Optional[Platform]:
        """Get the last known platform from state file."""
        if not self._platform_state_file.exists():
            return None
        
        try:
            with open(self._platform_state_file, 'r') as f:
                state = json.load(f)
                platform_str = state.get('last_platform')
                
                if platform_str:
                    # Convert string back to Platform enum
                    for plat in Platform:
                        if plat.value == platform_str:
                            return plat
        except Exception as e:
            self.log(f"Warning: Could not read platform state: {e}")
        
        return None
    
    def _save_platform_state(self, platform: Platform):
        """Save current platform to state file."""
        try:
            self._platform_state_file.parent.mkdir(parents=True, exist_ok=True)
            
            state = {
                'last_platform': platform.value,
                'last_update': str(Path.cwd()),
                'timestamp': platform.display_name  # For human readability
            }
            
            with open(self._platform_state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            self.log(f"Warning: Could not save platform state: {e}")
    
    def _auto_configure_platform(self, target_platform: Platform) -> Dict[str, Any]:
        """Auto-configure environment for platform (lightweight version)."""
        target_config = PlatformConfig.for_platform(target_platform)
        
        results = {
            "platform": target_platform.display_name,
            "steps": [],
            "success": True,
            "errors": [],
            "auto_mode": True
        }
        
        # Step 1: Git pull latest code
        step1 = self._git_pull_latest()
        results["steps"].append(step1)
        if not step1["success"]:
            results["success"] = False
        
        # Step 2: Configure environment (lightweight - just detection)
        step2 = {
            "name": "Environment Detection",
            "success": True,
            "message": f"Detected {target_platform.display_name} environment"
        }
        results["steps"].append(step2)
        
        # Step 3: Quick dependency check (don't install)
        step3 = self._check_dependencies_exist(target_config)
        results["steps"].append(step3)
        if not step3["success"]:
            self.log("⚠️  Some dependencies missing. Run '/setup' for full configuration.")
        
        return results
    
    def _check_dependencies_exist(self, config: PlatformConfig) -> Dict[str, Any]:
        """Quick check if dependencies exist (don't install)."""
        try:
            # Check Python
            result = subprocess.run(
                [config.python_command, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            python_ok = result.returncode == 0
            
            # Check Git
            git_result = subprocess.run(
                ["git", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            git_ok = git_result.returncode == 0
            
            return {
                "name": "Dependency Check",
                "success": python_ok and git_ok,
                "message": f"Python: {'✅' if python_ok else '❌'}, Git: {'✅' if git_ok else '❌'}"
            }
        except Exception as e:
            return {
                "name": "Dependency Check",
                "success": False,
                "message": f"Check failed: {e}"
            }
    
    def cleanup(self) -> bool:
        """Cleanup plugin resources (required by BasePlugin)."""
        self._logs.clear()
        return True
    
    def _find_project_root(self) -> Path:
        """Find CORTEX project root directory."""
        current = Path.cwd()
        while current != current.parent:
            if (current / "cortex-brain").exists() and (current / "src").exists():
                return current
            current = current.parent
        return Path.cwd()
    
    def can_handle(self, request: str) -> bool:
        """Check if this plugin should handle the request."""
        request_lower = request.lower()
        return any(trigger in request_lower for trigger in self.triggers)
    
    def execute(self, request: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute manual platform setup/configuration.
        
        Now delegates to the modular setup orchestrator system.
        
        Note: Platform detection is automatic. This method only runs
        when user explicitly requests setup/configuration.
        """
        from src.setup import run_setup
        
        # Always configure current platform (auto-detected)
        target_platform = self.current_platform
        
        self.log(f"🔧 CORTEX Setup: Configuring {target_platform.display_name}")
        self.log(f"📦 Using modular setup system with SOLID architecture")
        
        # Determine setup profile based on user request
        request_lower = request.lower()
        if 'full' in request_lower or 'complete' in request_lower:
            profile = 'full'
        elif 'minimal' in request_lower or 'quick' in request_lower:
            profile = 'minimal'
        else:
            profile = 'standard'
        
        self.log(f"   Profile: {profile}")
        
        # Build setup context
        setup_context = {
            'project_root': self.project_root,
            'platform': target_platform.value,
            'platform_display': target_platform.display_name,
            'user_request': request,
            'setup_profile': profile
        }
        
        # Add plugin context if provided
        if context:
            setup_context.update(context)
        
        # Execute setup via orchestrator
        try:
            report = run_setup(
                profile=profile,
                project_root=self.project_root,
                context=setup_context
            )
            
            # Convert report to plugin-compatible format
            results = {
                "platform": target_platform.display_name,
                "profile": profile,
                "success": report.overall_success,
                "summary": report.summary,
                "duration_ms": report.duration_ms,
                "modules_executed": len(report.results),
                "failed_modules": report.failed_modules,
                "steps": []
            }
            
            # Convert module results to plugin steps format
            for module_result in report.results:
                step = {
                    "step": module_result.module_id,
                    "success": module_result.success,
                    "message": module_result.message,
                    "details": module_result.details,
                    "duration_ms": module_result.duration_ms
                }
                results["steps"].append(step)
                
                # Log each step
                if module_result.success:
                    self.log(f"   ✅ {module_result.module_id}: {module_result.message}")
                else:
                    self.log(f"   ❌ {module_result.module_id}: {module_result.message}")
            
            # Save platform state on success
            if report.overall_success:
                self._save_platform_state(target_platform)
            
            # Generate and add summary
            results["summary"] = report.summary
            
            return results
            
        except Exception as e:
            self.log(f"❌ Setup failed with error: {e}")
            return {
                "platform": target_platform.display_name,
                "profile": profile,
                "success": False,
                "summary": f"Setup failed: {str(e)}",
                "error": str(e),
                "steps": []
            }
    
    def _git_pull_latest(self) -> Dict[str, Any]:
        """Step 1: Pull latest code from Git."""
        self.log("\n📥 Step 1: Pulling latest code from Git...")
        
        try:
            # Get current branch
            branch_result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if branch_result.returncode != 0:
                return {
                    "step": "Git Pull",
                    "success": False,
                    "error": "Failed to get current branch",
                    "details": branch_result.stderr
                }
            
            branch = branch_result.stdout.strip()
            self.log(f"   Branch: {branch}")
            
            # Pull latest changes
            pull_result = subprocess.run(
                ["git", "pull", "origin", branch],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if pull_result.returncode != 0:
                return {
                    "step": "Git Pull",
                    "success": False,
                    "error": "Git pull failed",
                    "details": pull_result.stderr
                }
            
            # Parse output for changes
            output = pull_result.stdout
            files_changed = self._count_git_changes(output)
            
            self.log(f"   ✅ Git pull successful")
            self.log(f"   Files changed: {files_changed}")
            
            return {
                "step": "Git Pull",
                "success": True,
                "branch": branch,
                "files_changed": files_changed,
                "output": output[:500]  # First 500 chars
            }
            
        except subprocess.TimeoutExpired:
            return {
                "step": "Git Pull",
                "success": False,
                "error": "Git pull timeout"
            }
        except Exception as e:
            return {
                "step": "Git Pull",
                "success": False,
                "error": str(e)
            }
    
    def _count_git_changes(self, git_output: str) -> int:
        """Count number of files changed from git output."""
        try:
            # Look for "N files changed"
            for line in git_output.split("\n"):
                if "files changed" in line or "file changed" in line:
                    parts = line.split()
                    if parts and parts[0].isdigit():
                        return int(parts[0])
            return 0
        except:
            return 0
    
    def _configure_environment(self, config: PlatformConfig) -> Dict[str, Any]:
        """Step 2: Configure environment for target platform."""
        self.log(f"\n⚙️  Step 2: Configuring {config.platform.display_name} environment...")
        
        try:
            env_details = {
                "platform": config.platform.display_name,
                "python_version": None,
                "venv_path": None,
                "venv_exists": False,
                "path_separator": config.path_separator,
                "shell": config.shell
            }
            
            # Check Python version
            python_cmd = self._find_python_command(config)
            if python_cmd:
                try:
                    version_result = subprocess.run(
                        [python_cmd, "--version"],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    env_details["python_version"] = version_result.stdout.strip()
                    self.log(f"   Python: {env_details['python_version']}")
                except:
                    pass
            
            # Check virtual environment
            venv_path = self.project_root / ".venv"
            env_details["venv_exists"] = venv_path.exists()
            env_details["venv_path"] = str(venv_path)
            
            if env_details["venv_exists"]:
                self.log(f"   ✅ Virtual environment found: {venv_path}")
            else:
                self.log(f"   ⚠️  Virtual environment not found at: {venv_path}")
                self.log(f"   Creating virtual environment...")
                
                # Create venv
                create_result = subprocess.run(
                    [python_cmd, "-m", "venv", str(venv_path)],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if create_result.returncode == 0:
                    env_details["venv_exists"] = True
                    self.log(f"   ✅ Virtual environment created")
                else:
                    self.log(f"   ❌ Failed to create virtual environment")
                    return {
                        "step": "Environment Configuration",
                        "success": False,
                        "error": "Failed to create virtual environment",
                        "details": create_result.stderr
                    }
            
            # Detect platform-specific paths
            env_details["project_root"] = str(self.project_root)
            env_details["cortex_brain"] = str(self.project_root / "cortex-brain")
            env_details["src_path"] = str(self.project_root / "src")
            env_details["tests_path"] = str(self.project_root / "tests")
            
            self.log(f"   ✅ Environment configured for {config.platform.display_name}")
            
            return {
                "step": "Environment Configuration",
                "success": True,
                "details": env_details
            }
            
        except Exception as e:
            return {
                "step": "Environment Configuration",
                "success": False,
                "error": str(e)
            }
    
    def _find_python_command(self, config: PlatformConfig) -> Optional[str]:
        """Find the appropriate Python command for the platform."""
        candidates = [
            config.python_command,
            "python3",
            "python",
            "py"  # Windows py launcher
        ]
        
        for cmd in candidates:
            try:
                result = subprocess.run(
                    [cmd, "--version"],
                    capture_output=True,
                    timeout=5
                )
                if result.returncode == 0:
                    return cmd
            except:
                continue
        
        return None
    
    def _verify_dependencies(self, config: PlatformConfig) -> Dict[str, Any]:
        """Step 3: Verify and install required dependencies."""
        self.log(f"\n📦 Step 3: Verifying dependencies...")
        
        try:
            # Required packages from requirements.txt
            required_packages = {
                "pytest": "pytest>=7.4.0",
                "pytest-cov": "pytest-cov>=4.1.0",
                "PyYAML": "PyYAML>=6.0.1",
                "numpy": "numpy>=1.24.0",
                "scikit-learn": "scikit-learn>=1.3.0",
                "watchdog": "watchdog>=3.0.0",
                "mkdocs": "mkdocs>=1.5.0",
                "mkdocs-material": "mkdocs-material>=9.4.0",
                "black": "black>=23.0.0",
                "flake8": "flake8>=6.0.0",
                "mypy": "mypy>=1.0.0"
            }
            
            python_cmd = self._get_venv_python(config)
            
            # Check installed packages
            pip_result = subprocess.run(
                [python_cmd, "-m", "pip", "list", "--format=json"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if pip_result.returncode != 0:
                return {
                    "step": "Dependency Verification",
                    "success": False,
                    "error": "Failed to list installed packages"
                }
            
            installed = {pkg["name"].lower(): pkg["version"] 
                        for pkg in json.loads(pip_result.stdout)}
            
            missing = []
            installed_list = []
            
            for pkg_name, pkg_spec in required_packages.items():
                pkg_lower = pkg_name.lower()
                if pkg_lower in installed:
                    installed_list.append(f"{pkg_name} ({installed[pkg_lower]})")
                    self.log(f"   ✅ {pkg_name}: {installed[pkg_lower]}")
                else:
                    missing.append(pkg_spec)
                    self.log(f"   ❌ {pkg_name}: Not installed")
            
            # Install missing packages
            if missing:
                self.log(f"\n   Installing {len(missing)} missing packages...")
                
                install_result = subprocess.run(
                    [python_cmd, "-m", "pip", "install"] + missing,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if install_result.returncode != 0:
                    return {
                        "step": "Dependency Verification",
                        "success": False,
                        "error": "Failed to install missing packages",
                        "missing": missing,
                        "details": install_result.stderr
                    }
                
                self.log(f"   ✅ Successfully installed {len(missing)} packages")
            
            return {
                "step": "Dependency Verification",
                "success": True,
                "installed": installed_list,
                "missing_installed": missing
            }
            
        except Exception as e:
            return {
                "step": "Dependency Verification",
                "success": False,
                "error": str(e)
            }
    
    def _get_venv_python(self, config: PlatformConfig) -> str:
        """Get path to Python in virtual environment."""
        venv_path = self.project_root / ".venv"
        
        if config.platform == Platform.WINDOWS:
            return str(venv_path / "Scripts" / "python.exe")
        else:
            return str(venv_path / "bin" / "python")
    
    def _run_brain_tests(self, config: PlatformConfig) -> Dict[str, Any]:
        """Step 4: Run brain tests to validate platform compatibility."""
        self.log(f"\n🧪 Step 4: Running brain tests...")
        
        try:
            python_cmd = self._get_venv_python(config)
            
            # Define test paths
            test_paths = [
                "tests/tier0/test_brain_protector.py",
                "tests/tier1/test_working_memory.py",
                "tests/tier2/test_knowledge_graph.py",
                "tests/tier3/test_context_intelligence.py"
            ]
            
            # Run pytest
            pytest_cmd = [
                python_cmd, "-m", "pytest"
            ] + test_paths + [
                "-v",
                "--tb=short",
                "--maxfail=5"
            ]
            
            self.log(f"   Running: pytest {' '.join(test_paths)}")
            
            test_result = subprocess.run(
                pytest_cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            output = test_result.stdout + test_result.stderr
            
            # Parse results
            passed = output.count(" PASSED")
            failed = output.count(" FAILED")
            errors = output.count(" ERROR")
            
            success = test_result.returncode == 0
            
            if success:
                self.log(f"   ✅ All tests passed!")
                self.log(f"   Tests: {passed} passed")
            else:
                self.log(f"   ❌ Some tests failed")
                self.log(f"   Tests: {passed} passed, {failed} failed, {errors} errors")
            
            return {
                "step": "Brain Tests",
                "success": success,
                "passed": passed,
                "failed": failed,
                "errors": errors,
                "output": output[-2000:]  # Last 2000 chars
            }
            
        except subprocess.TimeoutExpired:
            return {
                "step": "Brain Tests",
                "success": False,
                "error": "Tests timeout (exceeded 5 minutes)"
            }
        except Exception as e:
            return {
                "step": "Brain Tests",
                "success": False,
                "error": str(e)
            }
    
    def _verify_tooling(self, config: PlatformConfig) -> Dict[str, Any]:
        """Step 5: Verify required tooling is installed."""
        self.log(f"\n🔧 Step 5: Verifying tooling...")
        
        tools = {
            "git": ["git", "--version"],
            "python": [self._find_python_command(config), "--version"],
        }
        
        # Platform-specific tools
        if config.platform == Platform.MAC:
            tools["brew"] = ["brew", "--version"]
        elif config.platform == Platform.WINDOWS:
            tools["powershell"] = ["powershell", "-Command", "$PSVersionTable.PSVersion"]
        
        results = {}
        all_success = True
        
        for tool_name, cmd in tools.items():
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    version = result.stdout.strip().split("\n")[0]
                    results[tool_name] = {
                        "installed": True,
                        "version": version
                    }
                    self.log(f"   ✅ {tool_name}: {version}")
                else:
                    results[tool_name] = {
                        "installed": False,
                        "error": "Command failed"
                    }
                    self.log(f"   ⚠️  {tool_name}: Not found or failed")
                    all_success = False
                    
            except FileNotFoundError:
                results[tool_name] = {
                    "installed": False,
                    "error": "Not found"
                }
                self.log(f"   ❌ {tool_name}: Not installed")
                all_success = False
            except Exception as e:
                results[tool_name] = {
                    "installed": False,
                    "error": str(e)
                }
                all_success = False
        
        return {
            "step": "Tooling Verification",
            "success": all_success,
            "tools": results
        }
    
    def _generate_summary(self, results: Dict[str, Any]) -> str:
        """Generate human-readable summary."""
        platform = results["platform"]
        success = results["success"]
        
        summary = [
            f"\n{'='*60}",
            f"🔄 Platform Switch Summary: {platform}",
            f"{'='*60}\n"
        ]
        
        for step_result in results["steps"]:
            step_name = step_result["step"]
            step_success = step_result.get("success", False)
            icon = "✅" if step_success else "❌"
            
            summary.append(f"{icon} {step_name}: {'SUCCESS' if step_success else 'FAILED'}")
            
            # Add specific details
            if step_name == "Git Pull" and step_success:
                files = step_result.get("files_changed", 0)
                summary.append(f"   Files changed: {files}")
            
            elif step_name == "Brain Tests" and "passed" in step_result:
                summary.append(f"   Passed: {step_result['passed']}, Failed: {step_result['failed']}")
            
            elif step_name == "Dependency Verification":
                missing = step_result.get("missing_installed", [])
                if missing:
                    summary.append(f"   Installed: {len(missing)} missing packages")
        
        summary.append(f"\n{'='*60}")
        
        if success:
            summary.append(f"✅ {platform} environment is ready!")
            summary.append(f"   All systems operational for CORTEX 2.0")
        else:
            summary.append(f"⚠️  {platform} setup completed with issues")
            summary.append(f"   Please review errors above")
        
        summary.append(f"{'='*60}\n")
        
        return "\n".join(summary)
    
    def validate(self) -> Tuple[bool, List[str]]:
        """Validate plugin configuration."""
        issues = []
        
        if not self.project_root.exists():
            issues.append(f"Project root not found: {self.project_root}")
        
        if not (self.project_root / "cortex-brain").exists():
            issues.append("cortex-brain directory not found")
        
        if not (self.project_root / "src").exists():
            issues.append("src directory not found")
        
        return len(issues) == 0, issues


# Plugin registration
def register() -> BasePlugin:
    """Register the platform switch plugin."""
    return PlatformSwitchPlugin()
