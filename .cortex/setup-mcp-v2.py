#!/usr/bin/env python3
"""
CORTEX MCP v2 Setup Script

Cross-platform setup for macOS, Windows, and Linux.
Generates VS Code configuration with platform-specific Python paths.

Usage:
    python .cortex/setup-mcp-v2.py
    
AC_START: AC-WAVE100-S3-001
"""

import json
import os
import platform
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional


def get_python_executable() -> str:
    """
    Get the Python executable path based on platform.
    
    Returns:
        Full path to Python executable
    """
    # Check if in virtual environment
    venv_path = os.environ.get("VIRTUAL_ENV")
    
    if venv_path:
        venv = Path(venv_path)
        system = platform.system().lower()
        
        if system == "windows":
            python_path = venv / "Scripts" / "python.exe"
        else:  # macOS, Linux
            python_path = venv / "bin" / "python"
        
        if python_path.exists():
            return str(python_path)
    
    # Fall back to current Python
    return sys.executable


def get_workspace_root() -> Path:
    """
    Find the workspace root by looking for .cortex marker.
    
    Returns:
        Path to workspace root
    """
    current = Path.cwd()
    
    # Walk up looking for .cortex
    while current != current.parent:
        if (current / ".cortex").exists():
            return current
        if (current / "cortex").exists() and (current / "cortex" / "mcp").exists():
            return current
        current = current.parent
    
    # Fall back to cwd
    return Path.cwd()


def generate_mcp_config(python_path: str, workspace_root: Path) -> Dict[str, Any]:
    """
    Generate MCP server configuration.
    
    Args:
        python_path: Path to Python executable
        workspace_root: Workspace root path
        
    Returns:
        MCP configuration dict
    """
    return {
        "cortex": {
            "type": "stdio",
            "command": python_path,
            "args": ["-m", "cortex.mcp.v2"],
            "cwd": str(workspace_root),
            "env": {
                "PYTHONPATH": str(workspace_root),
                "CORTEX_MCP_ENABLED": "true",
                "CORTEX_MCP_VERSION": "2.0.0",
            }
        }
    }


def update_vscode_settings(workspace_root: Path, mcp_config: Dict[str, Any]) -> bool:
    """
    Update VS Code settings with MCP configuration.
    
    Args:
        workspace_root: Workspace root path
        mcp_config: MCP server configuration
        
    Returns:
        True if successful
    """
    vscode_dir = workspace_root / ".vscode"
    vscode_dir.mkdir(exist_ok=True)
    
    settings_file = vscode_dir / "settings.json"
    
    # Load existing settings or create new
    settings: Dict[str, Any] = {}
    if settings_file.exists():
        try:
            with open(settings_file, "r") as f:
                content = f.read().strip()
                if content:
                    settings = json.loads(content)
        except json.JSONDecodeError:
            print(f"⚠️ Warning: Invalid JSON in {settings_file}, will recreate")
    
    # Update MCP configuration
    settings["github.copilot.chat.mcpServers"] = mcp_config
    
    # Also set Python path if not set
    if "python.defaultInterpreterPath" not in settings:
        settings["python.defaultInterpreterPath"] = get_python_executable()
    
    # Write settings
    with open(settings_file, "w") as f:
        json.dump(settings, f, indent=4)
    
    return True


def verify_python_version() -> bool:
    """
    Verify Python version is 3.9+.
    
    Returns:
        True if version is compatible
    """
    version = sys.version_info
    if version < (3, 9):
        print(f"❌ Python 3.9+ required, found {version.major}.{version.minor}.{version.micro}")
        return False
    return True


def verify_dependencies() -> bool:
    """
    Verify required dependencies are installed.
    
    Returns:
        True if all dependencies available
    """
    required = ["cortex"]
    missing = []
    
    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    
    if missing:
        print(f"⚠️ Warning: Missing packages: {', '.join(missing)}")
        print("   Run: pip install -e .")
        return False
    
    return True


def write_setup_log(workspace_root: Path, status: str, details: Dict[str, Any]) -> None:
    """
    Write setup log for verification.
    
    Args:
        workspace_root: Workspace root path
        status: Setup status
        details: Setup details
    """
    cortex_dir = workspace_root / ".cortex"
    cortex_dir.mkdir(exist_ok=True)
    
    log_file = cortex_dir / "setup.log"
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "status": status,
        "platform": platform.system(),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "mcp_version": "2.0.0",
        **details,
    }
    
    with open(log_file, "w") as f:
        for key, value in log_entry.items():
            f.write(f"{key}: {value}\n")
        f.write("\n✅ SETUP COMPLETE\n")


def main() -> int:
    """
    Main setup function.
    
    Returns:
        Exit code (0 for success)
    """
    print("=" * 60)
    print("🧠 CORTEX MCP v2 Setup")
    print("=" * 60)
    print()
    
    # Check Python version
    print("📋 Checking Python version...")
    if not verify_python_version():
        return 1
    print(f"   ✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    
    # Find workspace root
    print("📋 Finding workspace root...")
    workspace_root = get_workspace_root()
    print(f"   ✅ {workspace_root}")
    
    # Get Python executable
    print("📋 Getting Python executable...")
    python_path = get_python_executable()
    print(f"   ✅ {python_path}")
    
    # Check platform
    print(f"📋 Platform: {platform.system()}")
    
    # Generate MCP config
    print("📋 Generating MCP configuration...")
    mcp_config = generate_mcp_config(python_path, workspace_root)
    print("   ✅ Configuration generated")
    
    # Update VS Code settings
    print("📋 Updating VS Code settings...")
    if update_vscode_settings(workspace_root, mcp_config):
        print("   ✅ .vscode/settings.json updated")
    else:
        print("   ❌ Failed to update settings")
        return 1
    
    # Verify dependencies
    print("📋 Checking dependencies...")
    verify_dependencies()
    
    # Write setup log
    print("📋 Writing setup log...")
    write_setup_log(workspace_root, "SUCCESS", {
        "python_path": python_path,
        "workspace_root": str(workspace_root),
    })
    print("   ✅ .cortex/setup.log written")
    
    print()
    print("=" * 60)
    print("✅ SETUP COMPLETE")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  1. Reload VS Code: Cmd+Shift+P → Developer: Reload Window")
    print("  2. Open Copilot Chat and use @cortex commands")
    print()
    print("MCP Server:")
    print(f"  - Transport: stdio")
    print(f"  - Command: {python_path} -m cortex.mcp.v2")
    print(f"  - Tools: 24 production tools")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

# AC_COMPLETE: AC-WAVE100-S3-001 ✅ Cross-platform setup script
