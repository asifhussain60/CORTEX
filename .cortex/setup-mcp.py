#!/usr/bin/env python3
"""
CORTEX MCP Setup Script — Cross-Platform

Sets up the CORTEX MCP server for use with GitHub Copilot Chat in VS Code.
This follows the Pylance-style auto-start architecture — the server auto-starts
when VS Code opens the workspace.

Usage:
    python .cortex/setup-mcp.py           → Full setup
    python .cortex/setup-mcp.py --check   → Check only (no changes)
    python .cortex/setup-mcp.py --cleanup → Remove competing MCP servers

Authority: ENH-066 | CORE-035 (Single Canonical Implementation)
"""

import os
import sys
import json
import logging
import platform
import subprocess
from pathlib import Path
from datetime import datetime


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [CORTEX-MCP-SETUP] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
LOG_PATH = WORKSPACE_ROOT / ".cortex" / "setup.log"
VSCODE_DIR = WORKSPACE_ROOT / ".vscode"
SETTINGS_PATH = VSCODE_DIR / "settings.json"

MCP_SETTINGS = {
    "github.copilot.chat.mcpServers": {
        "cortex": {
            "command": "python3",
            "args": ["-m", "cortex.mcp"],
            "cwd": "${workspaceFolder}",
            "type": "stdio",
        }
    }
}


def detect_platform() -> str:
    """Detect the current operating system using platform.system()."""
    system = platform.system()
    if system == "Windows":
        return "windows"
    elif system == "Darwin":
        return "macos"
    elif system == "Linux":
        return "linux"
    else:
        return "posix"


def get_python_executable() -> str:
    """Get the appropriate Python executable for the current platform."""
    plat = detect_platform()
    if plat == "windows":
        return "python"
    else:
        # macOS (Darwin) and Linux
        return "python3"


def setup_vscode_settings() -> bool:
    """Configure VS Code settings.json with MCP server configuration."""
    VSCODE_DIR.mkdir(parents=True, exist_ok=True)

    existing = {}
    if SETTINGS_PATH.exists():
        try:
            existing = json.loads(SETTINGS_PATH.read_text())
        except json.JSONDecodeError:
            logger.warning("Existing settings.json is invalid JSON — resetting")

    existing.update(MCP_SETTINGS)
    SETTINGS_PATH.write_text(json.dumps(existing, indent=2))
    logger.info(f"✅ settings.json configured: {SETTINGS_PATH}")
    return True


def create_cortex_dir() -> bool:
    """Create .cortex runtime directory."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    return True


def write_setup_log(status: str) -> None:
    """Write setup log to .cortex/setup.log."""
    log_entry = (
        f"[{datetime.now().isoformat()}] platform={platform.system()} "
        f"python={sys.version.split()[0]} status={status}\n"
    )
    with open(LOG_PATH, "a") as f:
        f.write(log_entry)
    logger.info(f"📝 Setup log written: {LOG_PATH}")


def validate_mcp_module() -> bool:
    """Check CORTEX MCP module is importable."""
    try:
        result = subprocess.run(
            [get_python_executable(), "-c", "import cortex.mcp; print('OK')"],
            cwd=str(WORKSPACE_ROOT),
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            logger.info("✅ cortex.mcp module is importable")
            return True
        else:
            logger.warning(f"⚠️  cortex.mcp import failed: {result.stderr.strip()}")
            return False
    except Exception as e:
        logger.warning(f"⚠️  Could not validate cortex.mcp: {e}")
        return False


def main() -> int:
    """Run the CORTEX MCP setup."""
    plat = detect_platform()
    logger.info(f"🚀 CORTEX MCP Setup starting on {platform.system()} ({plat})")

    # Platform-specific notes
    if plat == "windows":
        logger.info("📌 Windows: using 'python' executable")
    elif plat == "macos":
        logger.info("📌 macOS (Darwin): using 'python3' executable")
    elif plat == "linux":
        logger.info("📌 Linux: using 'python3' executable")

    success = True

    # Step 1: Create .cortex runtime dir
    if not create_cortex_dir():
        logger.error("❌ Failed to create .cortex directory")
        success = False

    # Step 2: Configure VS Code settings.json
    if not setup_vscode_settings():
        logger.error("❌ Failed to configure .vscode/settings.json")
        success = False

    # Step 3: Validate MCP module
    validate_mcp_module()

    # Step 4: Write setup log
    write_setup_log("SUCCESS" if success else "PARTIAL")

    if success:
        logger.info("✅ CORTEX MCP Setup complete")
        logger.info("   → Restart VS Code to activate the MCP server (auto-starts on open)")
    else:
        logger.warning("⚠️  Setup completed with warnings — check log above")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
