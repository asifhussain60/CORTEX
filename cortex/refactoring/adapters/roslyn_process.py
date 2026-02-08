"""
RoslynProcessManager - Manages C# Roslyn CLI process lifecycle.

Handles starting, stopping, and communicating with a .NET-based Roslyn
refactoring service via JSON-RPC over stdin/stdout.

AC_START: AC-PHASE24.2.1-002
Description: Roslyn process lifecycle management implementation
Authority: Phase 24.2.1 - Roslyn Process Manager
Author: Asif Hussain
Created: 2026-02-07
"""

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional, Union
from cortex.brain.core.result import Ok, Err


class RoslynProcessManager:
    """
    Manages lifecycle of Roslyn CLI process for C# refactoring.
    
    Provides process management (start/stop), communication (JSON-RPC),
    and availability checking for .NET SDK and Roslyn tools.
    
    Example:
        >>> manager = RoslynProcessManager()
        >>> if manager.is_available():
        ...     result = manager.start()
        ...     if result.is_ok():
        ...         response = manager.send_command({"action": "refactor"})
        ...         manager.stop()
    """

    def __init__(self, dotnet_path: Optional[str] = None):
        """
        Initialize RoslynProcessManager.
        
        Args:
            dotnet_path: Optional path to dotnet executable. If None, searches PATH.
        """
        self.dotnet_path: Optional[str] = dotnet_path or shutil.which("dotnet")
        self._process: Optional[subprocess.Popen] = None
        self._roslyn_cli_path: Optional[Path] = None
        
        # Locate Roslyn CLI tool (to be created)
        self._detect_roslyn_cli()

    def _detect_roslyn_cli(self) -> None:
        """
        Detect Roslyn CLI tool location.
        
        Searches for cortex-roslyn-cli in:
        1. cortex/refactoring/adapters/roslyn-cli/
        2. System PATH
        """
        # Check local tool first
        local_cli = Path(__file__).parent / "roslyn-cli" / "CortexRoslynCli.dll"
        if local_cli.exists():
            self._roslyn_cli_path = local_cli
            return
        
        # Check if built in bin directory
        bin_cli = Path(__file__).parent / "roslyn-cli" / "bin" / "Release" / "net8.0" / "CortexRoslynCli.dll"
        if bin_cli.exists():
            self._roslyn_cli_path = bin_cli
            return
        
        # Not found - will need to build or graceful degradation
        self._roslyn_cli_path = None

    def is_available(self) -> bool:
        """
        Check if Roslyn refactoring is available.
        
        Returns:
            True if .NET SDK is installed, False otherwise.
        """
        return self.dotnet_path is not None

    def is_running(self) -> bool:
        """
        Check if Roslyn process is currently running.
        
        Returns:
            True if process is running, False otherwise.
        """
        if self._process is None:
            return False
        
        # Check if process still alive
        return self._process.poll() is None

    def start(self) -> Union[Ok[None], Err]:
        """
        Start Roslyn CLI process.
        
        Returns:
            Ok(None) if started successfully, Err with error message otherwise.
        """
        if self.is_running():
            return Ok(None)  # Already running
        
        if not self.is_available():
            return Err("dotnet SDK not found. Install .NET 8.0+ SDK to enable C# refactoring.")
        
        if self._roslyn_cli_path is None or not self._roslyn_cli_path.exists():
            return Err(
                "Roslyn CLI tool not found. C# refactoring currently unavailable. "
                "Run 'make build-roslyn-cli' to build the tool."
            )
        
        try:
            # Start Roslyn CLI process
            # Type assertion: dotnet_path guaranteed non-None by is_available() check
            assert self.dotnet_path is not None
            self._process = subprocess.Popen(
                [self.dotnet_path, str(self._roslyn_cli_path)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            # Wait for startup confirmation (with timeout)
            # Note: Handshake protocol is optional - current implementation
            # relies on immediate process availability. Future enhancement
            # could add explicit ready signal from Roslyn CLI.
            
            return Ok(None)
            
        except FileNotFoundError as e:
            return Err(f"Failed to start Roslyn process: {e}")
        except Exception as e:
            return Err(f"Unexpected error starting Roslyn process: {e}")

    def stop(self) -> Union[Ok[None], Err]:
        """
        Stop Roslyn CLI process.
        
        Returns:
            Ok(None) if stopped successfully, Err with error message otherwise.
        """
        if not self.is_running():
            return Ok(None)  # Not running, nothing to stop
        
        # Type assertion: process guaranteed non-None by is_running() check
        assert self._process is not None
        
        try:
            # Send shutdown command
            if self._process.stdin and not self._process.stdin.closed:
                try:
                    self._process.stdin.write(json.dumps({"action": "shutdown"}) + "\n")
                    self._process.stdin.flush()
                except (BrokenPipeError, OSError):
                    pass  # Process may have already terminated
            
            # Terminate process
            self._process.terminate()
            
            # Wait for process to exit (with timeout)
            try:
                self._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Force kill if doesn't terminate
                self._process.kill()
                self._process.wait()
            
            self._process = None
            return Ok(None)
            
        except Exception as e:
            return Err(f"Error stopping Roslyn process: {e}")

    def send_command(self, command: Dict[str, Any]) -> Union[Ok[Dict[str, Any]], Err]:
        """
        Send JSON-RPC command to Roslyn process.
        
        Args:
            command: Dictionary representing JSON-RPC command.
            
        Returns:
            Ok with response dict if successful, Err with error message otherwise.
        """
        if not self.is_running():
            return Err("Roslyn process not running. Call start() first.")
        
        # Type assertion: process guaranteed non-None by is_running() check
        assert self._process is not None
        assert self._process.stdin is not None
        assert self._process.stdout is not None
        
        try:
            # Send command as JSON
            command_json = json.dumps(command) + "\n"
            self._process.stdin.write(command_json)
            self._process.stdin.flush()
            
            # Read response
            response_line = self._process.stdout.readline()
            if not response_line:
                return Err("No response from Roslyn process")
            
            response = json.loads(response_line)
            return Ok(response)
            
        except json.JSONDecodeError as e:
            return Err(f"Invalid JSON response: {e}")
        except BrokenPipeError:
            return Err("Roslyn process terminated unexpectedly")
        except Exception as e:
            return Err(f"Error communicating with Roslyn process: {e}")

    def __del__(self):
        """Cleanup: ensure process is stopped on deletion."""
        if self.is_running():
            self.stop()


# AC_COMPLETE: AC-PHASE24.2.1-002 ✅ RoslynProcessManager implementation
