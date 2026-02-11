#!/usr/bin/env python3
"""
CORTEX MCP Integration Setup Script

Configures VS Code MCP integration for CORTEX development.
Authority: Phase 25 + Phase 48 + Phase 49 + Phase 50 + Phase 53 (Cross-Platform)
Requirement: Zero-exception setup on all user machines (macOS + Windows)

MCP Architecture:
- MCP runs locally within VS Code (like Pylance)
- Auto-started by VS Code when Copilot Chat invokes cortex_* tools
- Uses stdio transport (stdin/stdout JSON-RPC)
- NO manual server startup required

MCP Policy (Phase 50):
- CORTEX MCP must be the ONLY MCP server
- Competing servers (Pylance MCP, GitKraken MCP) are disabled
- Enforced via git hooks (pre-commit, post-checkout)

Run: python .cortex/setup-mcp.py [--cleanup] [--silent]
  --cleanup: Remove competing MCP servers (Pylance, GitKraken, etc.)
  --silent: Suppress output (for use in git hooks)
"""

import json
import os
import sys
import logging
import platform
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Tuple, Optional, List

# Configure logging
LOG_DIR = Path(".cortex")
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "setup.log"

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)

# Cross-platform detection
IS_WINDOWS = platform.system() == "Windows"
IS_MACOS = platform.system() == "Darwin"
IS_LINUX = platform.system() == "Linux"

# MCP servers that should be disabled (Phase 50 policy)
COMPETING_MCP_SERVERS = ["pylance", "gitkraken", "mssql", "other"]


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="CORTEX MCP Integration Setup",
        epilog="Example: python .cortex/setup-mcp.py --cleanup"
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Remove competing MCP servers (Pylance, GitKraken, etc.)"
    )
    parser.add_argument(
        "--silent",
        action="store_true",
        help="Suppress output (for use in git hooks)"
    )
    return parser.parse_args()


def log_header():
    """Log setup start."""
    logger.info("=" * 80)
    logger.info("CORTEX MCP Integration Setup")
    logger.info(f"Workspace: {os.getcwd()}")
    logger.info(f"User: {os.getenv('USER', 'unknown')}")
    logger.info("=" * 80)


def check_python() -> Tuple[bool, str]:
    """Check Python version >= 3.9.0."""
    version_info = sys.version_info
    version_str = f"{version_info.major}.{version_info.minor}.{version_info.micro}"

    if version_info >= (3, 9):
        logger.info(f"✅ Python {version_str} (>= 3.9.0)")
        return True, version_str

    logger.error(f"❌ Python {version_str} (need >= 3.9.0)")
    return False, version_str


def check_venv() -> Tuple[bool, str]:
    """Check if virtual environment exists (cross-platform)."""
    # Cross-platform venv paths
    if IS_WINDOWS:
        venv_python = Path(".venv/Scripts/python.exe")
        venv_alt = Path(".venv/Scripts/python")
    else:
        venv_python = Path(".venv/bin/python")
        venv_alt = Path(".venv/bin/python3")

    # Check primary path
    if venv_python.exists() and venv_python.is_file():
        logger.info(f"✅ Virtual environment: {venv_python.absolute()}")
        return True, str(venv_python.absolute())

    # Check alternate path
    if venv_alt.exists() and venv_alt.is_file():
        logger.info(f"✅ Virtual environment: {venv_alt.absolute()}")
        return True, str(venv_alt.absolute())

    logger.error(f"❌ Virtual environment not found: {venv_python}")
    if IS_WINDOWS:
        logger.error("   Run: python -m venv .venv && .venv\\Scripts\\activate && pip install -r requirements.txt")
    else:
        logger.error("   Run: python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt")
    return False, ""


def check_mcp_module() -> Tuple[bool, str]:
    """Check if cortex/mcp module exists."""
    mcp_init = Path("cortex/mcp/__init__.py")

    if mcp_init.exists():
        logger.info(f"✅ MCP module found: cortex/mcp/__init__.py")
        return True, str(mcp_init.absolute())

    logger.error(f"❌ MCP module not found: {mcp_init}")
    logger.error("   Run: pip install -e . (to reinstall CORTEX package)")
    return False, ""


def validate_json_file(path: Path) -> Tuple[bool, Optional[Dict]]:
    """Validate JSON file syntax."""
    if not path.exists():
        return True, {}

    try:
        with open(path) as f:
            content = json.load(f)
        logger.info(f"✅ JSON valid: {path}")
        return True, content
    except json.JSONDecodeError as e:
        logger.error(f"❌ Invalid JSON in {path}: {e}")
        return False, None


def ensure_vscode_dir() -> Tuple[bool, Path]:
    """Create .vscode directory if missing."""
    vscode_dir = Path(".vscode")

    try:
        vscode_dir.mkdir(exist_ok=True)
        logger.info(f"✅ .vscode directory exists: {vscode_dir.absolute()}")
        return True, vscode_dir
    except Exception as e:
        logger.error(f"❌ Failed to create .vscode: {e}")
        return False, vscode_dir


def ensure_settings_json(vscode_dir: Path) -> Tuple[bool, Path]:
    """Create .vscode/settings.json if missing."""
    settings_path = vscode_dir / "settings.json"

    try:
        if not settings_path.exists():
            settings_path.write_text("{}\n")
            logger.info(f"✅ Created .vscode/settings.json")
        return True, settings_path
    except Exception as e:
        logger.error(f"❌ Failed to create settings.json: {e}")
        return False, settings_path


def create_mcp_json(vscode_dir: Path) -> Tuple[bool, Path]:
    """Create .vscode/mcp.json with proper MCP server configuration.
    
    MCP Architecture (Phase 53 - Pylance-Style):
    - VS Code reads mcp.json for MCP server definitions
    - VS Code auto-starts MCP server when Copilot invokes cortex_* tools
    - Uses stdio transport (stdin/stdout JSON-RPC 2.0)
    - NO manual 'python -m cortex.mcp.server' required
    - Cross-platform: Uses ${workspaceFolder} for portability
    """
    mcp_json_path = vscode_dir / "mcp.json"

    try:
        # Cross-platform Python path using VS Code variable
        if IS_WINDOWS:
            python_path = "${workspaceFolder}/.venv/Scripts/python.exe"
        else:
            python_path = "${workspaceFolder}/.venv/bin/python"

        # MCP configuration (VS Code mcp.json format)
        mcp_config = {
            "servers": {
                "cortex": {
                    "type": "stdio",
                    "command": python_path,
                    "args": ["-m", "cortex.mcp"],
                    "env": {
                        "CORTEX_ENV": "development",
                        "CORTEX_MCP_ENABLED": "true",
                        "PYTHONPATH": "${workspaceFolder}",
                        "CORTEX_WORKSPACE": "${workspaceFolder}"
                    }
                }
            }
        }

        # Write mcp.json
        mcp_json_path.write_text(json.dumps(mcp_config, indent=2) + "\n")
        logger.info(f"✅ Created .vscode/mcp.json with CORTEX MCP server config")
        return True, mcp_json_path

    except Exception as e:
        logger.error(f"❌ Failed to create mcp.json: {e}")
        return False, mcp_json_path


def inject_mcp_config(settings_path: Path) -> Tuple[bool, Dict]:
    """Inject cross-platform MCP configuration into .vscode/settings.json.
    
    MCP Architecture (Phase 53 - Pylance-Style):
    - VS Code auto-starts MCP server when Copilot invokes cortex_* tools
    - Uses stdio transport (stdin/stdout JSON-RPC 2.0)
    - NO manual 'python -m cortex.mcp.server' required
    - Cross-platform: Uses ${workspaceFolder} for portability
    """
    try:
        # Read current settings
        current = json.loads(settings_path.read_text()) if settings_path.exists() else {}

        # Cross-platform Python path using VS Code variable
        # ${workspaceFolder} is resolved by VS Code at runtime
        if IS_WINDOWS:
            python_path = "${workspaceFolder}/.venv/Scripts/python.exe"
        else:
            python_path = "${workspaceFolder}/.venv/bin/python"

        # MCP configuration (Pylance-style: auto-started by VS Code)
        mcp_config = {
            "cortex": {
                "command": python_path,
                "args": ["-m", "cortex.mcp"],
                "env": {
                    "CORTEX_ENV": "development",
                    "CORTEX_MCP_ENABLED": "true",
                    "PYTHONPATH": "${workspaceFolder}",
                    "CORTEX_WORKSPACE": "${workspaceFolder}"
                },
            }
        }

        # Merge safely
        if "github.copilot.chat.mcpServers" not in current:
            current["github.copilot.chat.mcpServers"] = {}

        current["github.copilot.chat.mcpServers"].update(mcp_config)

        # Write back with nice formatting
        settings_path.write_text(json.dumps(current, indent=2) + "\n")

        logger.info(f"✅ MCP configuration injected into .vscode/settings.json")
        return True, current

    except Exception as e:
        logger.error(f"❌ Failed to inject MCP config: {e}")
        return False, {}


def verify_mcp_startup() -> Tuple[bool, str]:
    """Verify MCP server module exists and is readable."""
    try:
        # Check if MCP server main module exists and is executable
        mcp_main = Path("cortex/mcp/__main__.py")

        if mcp_main.exists() and mcp_main.is_file():
            logger.info("✅ MCP server __main__.py module verified")
            logger.info("   (Server will start when invoked by Copilot)")
            return True, "Server ready"

        logger.error(f"❌ MCP server __main__.py not found: {mcp_main}")
        return False, "Missing __main__.py"

    except Exception as e:
        logger.error(f"❌ MCP verification failed: {e}")
        return False, str(e)


# ============================================================================
# AC_START: AC-PHASE50-MCPCLEANUP-003 - Competing MCP cleanup functions
# ============================================================================

def detect_competing_mcps() -> List[Dict]:
    """
    Detect competing MCP servers in VS Code configuration.
    
    Returns:
        List of detected competing servers with their locations.
    """
    competing = []
    
    # Check .vscode/settings.json
    settings_path = Path(".vscode/settings.json")
    if settings_path.exists():
        try:
            with open(settings_path) as f:
                content = f.read()
                # Handle JSONC (JSON with comments)
                import re
                content_no_comments = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
                content_no_comments = re.sub(r'/\*.*?\*/', '', content_no_comments, flags=re.DOTALL)
                settings = json.loads(content_no_comments)
            
            mcp_servers = settings.get("github.copilot.chat.mcpServers", {})
            for server_name in mcp_servers:
                if server_name.lower() != "cortex":
                    competing.append({
                        "name": server_name,
                        "location": "settings.json",
                        "path": str(settings_path)
                    })
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"Could not parse settings.json: {e}")
    
    # Check .vscode/mcp.json
    mcp_json_path = Path(".vscode/mcp.json")
    if mcp_json_path.exists():
        try:
            with open(mcp_json_path) as f:
                mcp_config = json.load(f)
            
            servers = mcp_config.get("servers", {})
            for server_name in servers:
                if server_name.lower() != "cortex":
                    competing.append({
                        "name": server_name,
                        "location": "mcp.json",
                        "path": str(mcp_json_path)
                    })
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"Could not parse mcp.json: {e}")
    
    return competing


def disable_pylance_mcp(settings_path: Path) -> bool:
    """
    Disable Pylance MCP server in VS Code settings.
    
    Args:
        settings_path: Path to .vscode/settings.json
    
    Returns:
        True if successfully disabled or already disabled.
    """
    try:
        if not settings_path.exists():
            return True
        
        with open(settings_path) as f:
            content = f.read()
        
        # Handle JSONC
        import re
        content_no_comments = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
        content_no_comments = re.sub(r'/\*.*?\*/', '', content_no_comments, flags=re.DOTALL)
        settings = json.loads(content_no_comments)
        
        modified = False
        
        # Disable Pylance MCP server
        if "pylance.mcpServer.enabled" not in settings:
            settings["pylance.mcpServer.enabled"] = False
            modified = True
            logger.info("✅ Disabled Pylance MCP server (pylance.mcpServer.enabled = false)")
        elif settings.get("pylance.mcpServer.enabled") is True:
            settings["pylance.mcpServer.enabled"] = False
            modified = True
            logger.info("✅ Disabled Pylance MCP server (was enabled)")
        
        # Remove Pylance from mcpServers if present
        mcp_servers = settings.get("github.copilot.chat.mcpServers", {})
        if "pylance" in mcp_servers:
            del mcp_servers["pylance"]
            settings["github.copilot.chat.mcpServers"] = mcp_servers
            modified = True
            logger.info("✅ Removed Pylance from mcpServers")
        
        if modified:
            settings_path.write_text(json.dumps(settings, indent=2) + "\n")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to disable Pylance MCP: {e}")
        return False


def remove_competing_from_mcp_json(mcp_json_path: Path) -> bool:
    """
    Remove competing MCP servers from mcp.json, keeping only CORTEX.
    
    Args:
        mcp_json_path: Path to .vscode/mcp.json
    
    Returns:
        True if successfully cleaned or already clean.
    """
    try:
        if not mcp_json_path.exists():
            return True
        
        with open(mcp_json_path) as f:
            mcp_config = json.load(f)
        
        servers = mcp_config.get("servers", {})
        original_count = len(servers)
        
        # Keep only CORTEX server
        if "cortex" in servers:
            cortex_config = servers["cortex"]
            mcp_config["servers"] = {"cortex": cortex_config}
        
        removed_count = original_count - len(mcp_config.get("servers", {}))
        
        if removed_count > 0:
            mcp_json_path.write_text(json.dumps(mcp_config, indent=2) + "\n")
            logger.info(f"✅ Removed {removed_count} competing MCP server(s) from mcp.json")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to clean mcp.json: {e}")
        return False


def enforce_cortex_only() -> Tuple[bool, str]:
    """
    Enforce CORTEX-only MCP policy by removing all competing servers.
    
    Returns:
        Tuple of (success, message)
    """
    logger.info("=" * 80)
    logger.info("🔌 MCP Cleanup: Enforcing CORTEX-only policy")
    logger.info("=" * 80)
    
    # Detect competing servers
    competing = detect_competing_mcps()
    
    if not competing:
        logger.info("✅ No competing MCP servers detected")
        return True, "Already CORTEX-only"
    
    logger.info(f"⚠️  Found {len(competing)} competing MCP server(s):")
    for server in competing:
        logger.info(f"   - {server['name']} in {server['location']}")
    
    # Disable Pylance MCP
    settings_path = Path(".vscode/settings.json")
    disable_pylance_mcp(settings_path)
    
    # Clean mcp.json
    mcp_json_path = Path(".vscode/mcp.json")
    remove_competing_from_mcp_json(mcp_json_path)
    
    # Verify cleanup
    remaining = detect_competing_mcps()
    if remaining:
        logger.warning(f"⚠️  {len(remaining)} server(s) could not be removed automatically")
        return False, f"Manual cleanup needed for: {[s['name'] for s in remaining]}"
    
    logger.info("✅ MCP cleanup complete: CORTEX is now the only MCP server")
    return True, "Cleanup successful"


# AC_COMPLETE: AC-PHASE50-MCPCLEANUP-003 ✅


def display_completion_message(cleanup_mode: bool = False):
    """Display completion message with next steps."""
    print("\n" + "=" * 80)
    if cleanup_mode:
        print("🧹 CORTEX MCP CLEANUP COMPLETE")
    else:
        print("🔌 CORTEX MCP INTEGRATION SETUP COMPLETE")
    print("=" * 80)
    print("\n✅ Configuration Status: SUCCESS\n")
    print("MCP Architecture (Pylance-Style):")
    print("  • MCP runs locally within VS Code (like Pylance)")
    print("  • Auto-started when Copilot Chat invokes cortex_* tools")
    print("  • Uses stdio transport (stdin/stdout JSON-RPC)")
    print("  • NO manual server startup required\n")
    
    if cleanup_mode:
        print("MCP Policy Enforcement (Phase 50):")
        print("  ✅ Competing MCP servers removed")
        print("  ✅ Pylance MCP disabled")
        print("  ✅ CORTEX is the ONLY MCP server")
        print("  ✅ Policy enforced via git hooks\n")
    else:
        print("What was configured:")
        print("  ✅ .vscode/mcp.json created (PRIMARY - VS Code reads this)")
        print("  ✅ .vscode/settings.json updated (SECONDARY - fallback)")
        if IS_WINDOWS:
            print("  ✅ Python: ${workspaceFolder}/.venv/Scripts/python.exe")
        else:
            print("  ✅ Python: ${workspaceFolder}/.venv/bin/python")
        print("  ✅ MCP module: cortex.mcp (stdio transport)")
        print("  ✅ Environment variables configured")
        print("  ✅ Cross-platform: Works on macOS/Windows/Linux\n")
    
    print("NEXT STEPS:")
    print("⚡ **Restart VS Code for changes to take effect**\n")
    print("In VS Code:")
    print("  1. Command Palette (Cmd+Shift+P / Ctrl+Shift+P)")
    print("  2. Type: Developer: Reload Window")
    print("  3. Press Enter\n")
    print("  4. Run: MCP: List Servers (to verify CORTEX is listed)")
    print("  5. Start the server from the MCP servers list\n")
    print("Available Tools After Setup:")
    print("  • cortex_process_request (TDD implementation)")
    print("  • cortex_lens_analyze (Code intelligence)")
    print("  • cortex_challenge (Challenge gate)")
    print("  • cortex_plan_execute_autonomous (Phase execution)")
    print("  • cortex_detect_duplicates (CORE-035 detection)")
    print("  • cortex_total_recall (Feature discovery)")
    print("  • cortex_git_history (24h git context)")
    print("  • cortex_plan_setup (Pre-execution hook)")
    print("  • cortex_plan_teardown (Post-execution hook)")
    print("  • cortex_plan_sync (Dashboard sync)\n")
    print("NOTE: NO 'python -m cortex.mcp.server' needed!")
    print("      VS Code auto-starts MCP when Copilot invokes tools.\n")
    print("Configuration files:")
    print("  • .vscode/mcp.json (MCP server definition)")
    print("  • .cortex/setup.log (setup log)")
    print("=" * 80 + "\n")


def main():
    """Main setup flow."""
    args = parse_args()
    
    # Configure logging for silent mode
    if args.silent:
        logging.getLogger().setLevel(logging.WARNING)
    
    log_header()
    
    # If cleanup mode, just do cleanup and exit
    if args.cleanup:
        success, message = enforce_cortex_only()
        if success:
            if not args.silent:
                display_completion_message(cleanup_mode=True)
            return 0
        else:
            logger.error(f"Cleanup failed: {message}")
            return 1

    # Step 1: Check Python
    python_ok, python_version = check_python()
    if not python_ok:
        logger.error("Setup failed: Python version check")
        return 1

    # Step 2: Check Virtual Environment
    venv_ok, venv_path = check_venv()
    if not venv_ok:
        logger.error("Setup failed: Virtual environment check")
        return 1

    # Step 3: Check MCP Module
    mcp_ok, mcp_path = check_mcp_module()
    if not mcp_ok:
        logger.error("Setup failed: MCP module check")
        return 1

    # Step 4: Create .vscode directory
    vscode_ok, vscode_dir = ensure_vscode_dir()
    if not vscode_ok:
        logger.error("Setup failed: .vscode directory creation")
        return 1

    # Step 5: Create/validate settings.json
    settings_ok, settings_path = ensure_settings_json(vscode_dir)
    if not settings_ok:
        logger.error("Setup failed: settings.json creation")
        return 1

    # Step 6: Validate JSON
    json_ok, json_content = validate_json_file(settings_path)
    if not json_ok:
        logger.error("Setup failed: JSON validation")
        return 1

    # Step 7: Create mcp.json (PRIMARY - VS Code reads this for MCP servers)
    mcp_json_ok, mcp_json_path = create_mcp_json(vscode_dir)
    if not mcp_json_ok:
        logger.error("Setup failed: mcp.json creation")
        return 1

    # Step 8: Inject MCP configuration into settings.json (SECONDARY - fallback)
    inject_ok, settings_content = inject_mcp_config(settings_path)
    if not inject_ok:
        logger.error("Setup failed: MCP configuration injection")
        return 1
    
    # Step 8.5: Disable Pylance MCP (Phase 50 policy)
    disable_pylance_mcp(settings_path)

    # Step 9: Verify MCP startup
    verify_ok, verify_msg = verify_mcp_startup()
    if not verify_ok:
        logger.error("Setup failed: MCP startup verification")
        logger.error(f"Details: {verify_msg}")
        logger.error(
            "Recommendation: Check that all dependencies are installed (pip install -r requirements.txt)"
        )
        return 1

    # Success!
    logger.info("=" * 80)
    logger.info("✅ SETUP COMPLETE - MCP integration configured successfully")
    logger.info("⚡ Next: Restart VS Code for changes to take effect")
    logger.info("=" * 80)

    if not args.silent:
        display_completion_message()

    return 0


if __name__ == "__main__":
    sys.exit(main())
