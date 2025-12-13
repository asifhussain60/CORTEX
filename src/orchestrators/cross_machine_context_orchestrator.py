"""
Cross-Machine Context Orchestrator (Feature 4).

Enables seamless workflow between Windows and Mac by detecting OS, shell,
runtimes, and providing path/command translation.

Evidence-based solution for chat session issue: manual path translation required
when switching between Windows (C:\\PROJECTS\\) and Mac (/Users/asifhussain/PROJECTS/).

Author: Asif Hussain
Created: December 12, 2025
"""

import platform
import os
import subprocess
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
import logging

from src.operations.utilities.path_translator import PathTranslator
from src.operations.utilities.shell_adapter import ShellAdapter

logger = logging.getLogger(__name__)


@dataclass
class MachineContext:
    """Machine context data structure."""
    
    os: str  # "Windows" | "Mac" | "Linux"
    os_version: str
    shell: str  # "PowerShell" | "bash" | "zsh" | "cmd"
    python_version: Optional[str] = None
    dotnet_version: Optional[str] = None
    node_version: Optional[str] = None
    git_version: Optional[str] = None
    home_directory: str = ""
    working_directory: str = ""
    path_separator: str = ""
    line_ending: str = ""
    case_sensitive: bool = True
    last_active_machine: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for brain storage."""
        return asdict(self)


class CrossMachineContextOrchestrator:
    """
    Orchestrator for cross-machine context detection and adaptation.
    
    Provides:
    - OS and shell detection
    - Path translation (Windows <-> Unix)
    - Shell syntax adaptation
    - Runtime detection (.NET, Python, Node.js, Git)
    - Brain Tier 1 integration
    """
    
    def __init__(self):
        """Initialize orchestrator."""
        logger.info("🎭 Orchestrator engaged: CrossMachineContextOrchestrator")
        self.brain_tier1_path = Path("cortex-brain/tier1")
        self.context_file = self.brain_tier1_path / "machine-context.json"
    
    def detect_machine_context(self) -> MachineContext:
        """
        Detect comprehensive machine context.
        
        Returns:
            MachineContext with all detected information
        """
        logger.info("🎭 Phase: Detecting machine context")
        
        # Detect OS
        os_name = self._detect_os()
        os_version = platform.version()
        
        # Detect shell
        shell = self._detect_shell(os_name)
        
        # Detect runtimes
        python_ver = self._detect_python()
        dotnet_ver = self._detect_dotnet()
        node_ver = self._detect_nodejs()
        git_ver = self._detect_git()
        
        # OS-specific settings
        home_dir = str(Path.home())
        work_dir = str(Path.cwd())
        path_sep = "\\" if os_name == "Windows" else "/"
        line_end = "\r\n" if os_name == "Windows" else "\n"
        case_sens = os_name != "Windows"
        
        machine_name = platform.node()
        
        context = MachineContext(
            os=os_name,
            os_version=os_version,
            shell=shell,
            python_version=python_ver,
            dotnet_version=dotnet_ver,
            node_version=node_ver,
            git_version=git_ver,
            home_directory=home_dir,
            working_directory=work_dir,
            path_separator=path_sep,
            line_ending=line_end,
            case_sensitive=case_sens,
            last_active_machine=machine_name,
        )
        
        logger.info(f"✅ Context detected: {os_name} / {shell}")
        return context
    
    def _detect_os(self) -> str:
        """Detect operating system."""
        system = platform.system()
        if system == "Windows":
            return "Windows"
        elif system == "Darwin":
            return "Mac"
        elif system == "Linux":
            return "Linux"
        else:
            return system
    
    def _detect_shell(self, os_name: str) -> str:
        """
        Detect active shell.
        
        Args:
            os_name: Operating system name
            
        Returns:
            Shell name: "PowerShell", "bash", "zsh", "cmd"
        """
        # Check environment variables
        shell_env = os.environ.get("SHELL", "")
        
        if os_name == "Windows":
            # Check for PowerShell
            if "PSModulePath" in os.environ:
                return "PowerShell"
            # Check for cmd
            elif "COMSPEC" in os.environ and "cmd.exe" in os.environ.get("COMSPEC", ""):
                return "cmd"
            else:
                return "PowerShell"  # Default for Windows
        else:
            # Unix-like systems
            if "zsh" in shell_env:
                return "zsh"
            elif "bash" in shell_env:
                return "bash"
            elif shell_env:
                return Path(shell_env).name
            else:
                return "bash"  # Default for Unix
    
    def _detect_python(self) -> Optional[str]:
        """Detect Python runtime version."""
        try:
            return f"{platform.python_version()}"
        except Exception as e:
            logger.debug(f"Python detection failed: {e}")
            return None
    
    def _detect_dotnet(self) -> Optional[str]:
        """Detect .NET SDK version."""
        try:
            result = subprocess.run(
                ["dotnet", "--version"],
                capture_output=True,
                text=True,
                timeout=2,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception as e:
            logger.debug(f".NET detection failed: {e}")
        return None
    
    def _detect_nodejs(self) -> Optional[str]:
        """Detect Node.js version."""
        try:
            result = subprocess.run(
                ["node", "--version"],
                capture_output=True,
                text=True,
                timeout=2,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception as e:
            logger.debug(f"Node.js detection failed: {e}")
        return None
    
    def _detect_git(self) -> Optional[str]:
        """Detect Git version."""
        try:
            result = subprocess.run(
                ["git", "--version"],
                capture_output=True,
                text=True,
                timeout=2,
            )
            if result.returncode == 0:
                return result.stdout.strip().replace("git version ", "")
        except Exception as e:
            logger.debug(f"Git detection failed: {e}")
        return None
    
    def translate_path(self, path: str, target_os: str) -> str:
        """
        Translate path between Windows and Unix formats.
        
        Args:
            path: Path to translate
            target_os: Target OS ("Windows" or "Unix")
            
        Returns:
            Translated path
        """
        return PathTranslator.translate(path, target_os)
    
    def adapt_command(self, command: str, target_shell: str) -> str:
        """
        Adapt command syntax for target shell.
        
        Args:
            command: Original command
            target_shell: Target shell type
            
        Returns:
            Adapted command
        """
        return ShellAdapter.adapt_command(command, target_shell)
    
    def format_env_var(self, var_name: str, shell: str) -> str:
        """
        Format environment variable reference for shell.
        
        Args:
            var_name: Variable name
            shell: Shell type
            
        Returns:
            Formatted variable reference
        """
        return ShellAdapter.format_env_var(var_name, shell)
    
    def get_line_continuation(self, shell: str) -> str:
        """
        Get line continuation character for shell.
        
        Args:
            shell: Shell type
            
        Returns:
            Line continuation character
        """
        return ShellAdapter.get_line_continuation(shell)
    
    def save_to_brain(self, context: MachineContext) -> bool:
        """
        Save machine context to brain Tier 1.
        
        Args:
            context: Machine context to save
            
        Returns:
            True if successful
        """
        try:
            self.brain_tier1_path.mkdir(parents=True, exist_ok=True)
            with open(self.context_file, "w") as f:
                json.dump(context.to_dict(), f, indent=2)
            logger.info(f"✅ Context saved to brain Tier 1: {self.context_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to save context: {e}")
            return False
    
    def load_from_brain(self) -> Optional[MachineContext]:
        """
        Load machine context from brain Tier 1.
        
        Returns:
            Stored machine context or None
        """
        try:
            if not self.context_file.exists():
                return None
            
            with open(self.context_file, "r") as f:
                data = json.load(f)
            
            context = MachineContext(**data)
            logger.info(f"✅ Context loaded from brain Tier 1")
            return context
        except Exception as e:
            logger.error(f"Failed to load context: {e}")
            return None
    
    def has_context_changed(
        self, old_context: Optional[MachineContext], new_context: MachineContext
    ) -> bool:
        """
        Check if machine context has changed.
        
        Args:
            old_context: Previous context
            new_context: Current context
            
        Returns:
            True if context changed
        """
        if old_context is None:
            return True
        
        # Check key fields that indicate machine change
        changed = (
            old_context.os != new_context.os
            or old_context.shell != new_context.shell
            or old_context.last_active_machine != new_context.last_active_machine
        )
        
        return changed
