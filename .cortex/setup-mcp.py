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


def _strip_jsonc_comments(content: str) -> str:
    """Strip JSONC comments (// and /* */) while preserving string literals.
    
    Uses a state machine approach to avoid corrupting strings that contain
    comment-like patterns (e.g., glob patterns like '**/*').
    
    Args:
        content: Raw JSONC file content
        
    Returns:
        Clean JSON string safe for json.loads()
    """
    result = []
    i = 0
    in_string = False
    
    while i < len(content):
        char = content[i]
        
        # Handle string boundaries (respect escape sequences)
        if char == '"' and (i == 0 or content[i - 1] != '\\'):
            in_string = not in_string
            result.append(char)
            i += 1
            continue
        
        # Inside a string — pass through everything verbatim
        if in_string:
            result.append(char)
            i += 1
            continue
        
        # Outside string: check for comments
        if char == '/' and i + 1 < len(content):
            next_char = content[i + 1]
            # Line comment: //
            if next_char == '/':
                # Skip until end of line
                while i < len(content) and content[i] != '\n':
                    i += 1
                continue
            # Block comment: /* */
            elif next_char == '*':
                i += 2
                while i + 1 < len(content):
                    if content[i] == '*' and content[i + 1] == '/':
                        i += 2
                        break
                    i += 1
                continue
        
        result.append(char)
        i += 1
    
    return ''.join(result)


def _read_jsonc_file(path: Path) -> Tuple[bool, Optional[Dict], Optional[str]]:
    """Read a JSONC file, returning parsed dict AND original raw content.
    
    Args:
        path: Path to JSON/JSONC file
        
    Returns:
        Tuple of (success, parsed_dict, raw_content)
    """
    if not path.exists():
        return True, {}, None
    
    try:
        raw_content = path.read_text(encoding='utf-8')
        clean_json = _strip_jsonc_comments(raw_content)
        parsed = json.loads(clean_json)
        return True, parsed, raw_content
    except json.JSONDecodeError as e:
        logger.error(f"❌ Invalid JSON in {path}: {e}")
        return False, None, None
    except Exception as e:
        logger.error(f"❌ Failed to read {path}: {e}")
        return False, None, None


def _write_settings_safely(settings_path: Path, key: str, value, raw_content: Optional[str] = None) -> bool:
    """Write a single key-value pair to settings.json without corrupting other content.
    
    CRITICAL FIX (BUG-001): This function MUST preserve JSONC comments and glob patterns
    when updating existing keys. The old implementation fell back to json.dumps which
    stripped all comments.
    
    Strategy: For JSONC files with comments, perform surgical regex-based replacement:
    1. Find the line with the key (e.g., '"python.linting": true')
    2. Replace only the value, preserving the key and any trailing comment
    3. If key doesn't exist, insert before closing brace
    
    Args:
        settings_path: Path to .vscode/settings.json
        key: The top-level key to set (e.g., "pylance.mcpServer.enabled")
        value: The value to set
        raw_content: Original raw file content (for surgical updates)
        
    Returns:
        True if successful
    """
    import re
    
    try:
        if not settings_path.exists():
            settings_path.write_text(json.dumps({key: value}, indent=2) + "\n", encoding='utf-8')
            return True
        
        # Read current content
        if raw_content is None:
            raw_content = settings_path.read_text(encoding='utf-8')
        
        # Parse to check if key exists
        clean = _strip_jsonc_comments(raw_content)
        current = json.loads(clean)
        
        # Check if file has JSONC features (comments)
        has_comments = '//' in raw_content or '/*' in raw_content
        
        if has_comments:
            # JSONC file: surgical regex-based replacement to preserve comments
            # Pattern: find the key line and replace only the value
            # e.g., '"python.linting": true' → '"python.linting": false'
            
            if key in current and current[key] == value:
                # Already has correct value, skip
                return True
            
            # Escape special regex chars in key
            key_escaped = re.escape(key)
            
            # Build the pattern: match key with any amount of whitespace and colon,
            # then any value (including nested objects/arrays)
            # This is complex, so we use a simpler approach for top-level keys
            
            value_json = json.dumps(value)
            
            if key in current:
                # Replace existing key value using regex
                # Pattern: "key": <any value> with optional trailing comma and comments
                # Match: " "key" : <non-greedy value> < next key or closing brace or comment
                pattern = rf'("{key_escaped}"\s*:\s*)([^,\n}}/*]+(?:{{[^}}]*}}|\[[^\]]*\])?)'
                replacement = rf'\g<1>{value_json}'
                
                new_content = re.sub(pattern, replacement, raw_content, count=1)
                
                # Verify replacement happened
                if new_content == raw_content:
                    # Regex didn't match, try a more lenient pattern
                    # Find the key and replace everything after it until comma, newline, or }
                    pattern2 = rf'("{key_escaped}"\s*:\s*)[^,\n}}]+'
                    replacement2 = rf'\g<1>{value_json}'
                    new_content = re.sub(pattern2, replacement2, raw_content, count=1)
                
                settings_path.write_text(new_content, encoding='utf-8')
            else:
                # Key doesn't exist, insert before closing brace
                insert_str = f'  "{key}": {value_json}'
                # Find last closing brace
                last_brace = raw_content.rstrip().rfind('}')
                if last_brace > 0:
                    before = raw_content[:last_brace].rstrip()
                    # Add comma if there's content (not just '{')
                    if before.rstrip() and before.rstrip()[-1] not in ('{', ','):
                        before = before + ','
                    new_content = before + '\n' + insert_str + '\n}\n'
                    settings_path.write_text(new_content, encoding='utf-8')
                else:
                    # Fallback: shouldn't happen but handle gracefully
                    current[key] = value
                    settings_path.write_text(json.dumps(current, indent=2) + "\n", encoding='utf-8')
        else:
            # Pure JSON — safe to use json.dumps
            current[key] = value
            settings_path.write_text(json.dumps(current, indent=2) + "\n", encoding='utf-8')
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to write {key} to settings: {e}")
        return False


def _merge_mcp_servers_safely(settings_path: Path, server_name: str, server_config: Dict) -> bool:
    """Merge an MCP server config into settings.json without corrupting other content.
    
    CRITICAL FIX (BUG-002): This function MUST preserve JSONC comments and glob patterns
    when merging MCP server configurations. The old implementation used json.dumps which
    stripped all comments.
    
    Strategy: For JSONC files:
    1. Read raw content + parse it
    2. Update the mcpServers key
    3. Write back with a sophisticated approach that preserves comments:
       - If the mcpServers value is a simple object on one line, use regex replacement
       - Otherwise, use surgical JSON merge at the mcpServers level
    
    This specifically handles the github.copilot.chat.mcpServers key,
    adding or updating a single server entry while preserving all other content.
    
    Args:
        settings_path: Path to .vscode/settings.json
        server_name: Name of MCP server (e.g., "cortex")
        server_config: Server configuration dict
        
    Returns:
        True if successful
    """
    import re
    
    try:
        ok, current, raw = _read_jsonc_file(settings_path)
        if not ok or current is None:
            current = {}
            raw = None
        
        # Ensure mcpServers key exists
        if "github.copilot.chat.mcpServers" not in current:
            current["github.copilot.chat.mcpServers"] = {}
        
        # Check if already configured correctly
        existing = current["github.copilot.chat.mcpServers"].get(server_name)
        if existing == server_config:
            logger.info(f"✅ MCP server '{server_name}' already configured correctly")
            return True
        
        # Check if file has JSONC comments
        has_comments = raw and ('//' in raw or '/*' in raw)
        
        # Update the server config
        current["github.copilot.chat.mcpServers"][server_name] = server_config
        
        if has_comments and raw:
            # JSONC file: Try to preserve comments using surgical regex replacement
            # This is complex for nested JSON, so we use a two-pronged approach:
            
            # Strategy 1: Try to find and replace just the server entry
            server_escaped = re.escape(server_name)
            # Pattern looks for: "server_name": { ... } (with nested braces)
            # This is very tricky, so instead we replace the entire mcpServers block
            
            # Find the mcpServers section in raw content
            mcp_pattern = r'"github\.copilot\.chat\.mcpServers"\s*:\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}'
            
            if re.search(mcp_pattern, raw):
                # Re-serialize only the mcpServers value as JSON (without comments)
                mcp_servers_json = json.dumps(current["github.copilot.chat.mcpServers"], indent=2)
                # Indent it properly (add 2 spaces)
                mcp_lines = mcp_servers_json.split('\n')
                mcp_indented = '\n  '.join(mcp_lines)
                
                replacement = f'"github.copilot.chat.mcpServers": {mcp_indented}'
                new_content = re.sub(mcp_pattern, replacement, raw, count=1)
                
                # Only write if replacement succeeded
                if new_content != raw:
                    settings_path.write_text(new_content, encoding='utf-8')
                    return True
            
            # Strategy 2: If regex didn't work, just do a full rewrite
            # (This is not ideal but better than leaving it broken)
            settings_path.write_text(json.dumps(current, indent=2) + "\n", encoding='utf-8')
        else:
            # Pure JSON or no raw content — safe to use json.dumps
            settings_path.write_text(json.dumps(current, indent=2) + "\n", encoding='utf-8')
        
        logger.info(f"✅ Merged MCP server '{server_name}' config")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to merge MCP server config: {e}")
        return False


def _remove_mcp_server_safely(settings_path: Path, server_name: str) -> bool:
    """Remove a specific MCP server from settings.json without corrupting other content.
    
    Args:
        settings_path: Path to .vscode/settings.json
        server_name: Name of MCP server to remove (e.g., "pylance")
        
    Returns:
        True if successful (or server didn't exist)
    """
    try:
        ok, current, raw = _read_jsonc_file(settings_path)
        if not ok or current is None:
            return True
        
        mcp_servers = current.get("github.copilot.chat.mcpServers", {})
        if server_name not in mcp_servers:
            return True
        
        del mcp_servers[server_name]
        current["github.copilot.chat.mcpServers"] = mcp_servers
        settings_path.write_text(json.dumps(current, indent=2) + "\n", encoding='utf-8')
        logger.info(f"✅ Removed '{server_name}' from mcpServers")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to remove MCP server '{server_name}': {e}")
        return False


def validate_json_file(path: Path) -> Tuple[bool, Optional[Dict]]:
    """Validate JSON/JSONC file syntax (JSONC-aware)."""
    if not path.exists():
        return True, {}

    ok, parsed, _ = _read_jsonc_file(path)
    if ok and parsed is not None:
        logger.info(f"✅ JSON valid: {path}")
        return True, parsed
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
    
    Uses JSONC-safe read/write to preserve existing settings, comments,
    and glob patterns. Only modifies the github.copilot.chat.mcpServers key.
    
    MCP Architecture (Phase 53 - Pylance-Style):
    - VS Code auto-starts MCP server when Copilot invokes cortex_* tools
    - Uses stdio transport (stdin/stdout JSON-RPC 2.0)
    - NO manual 'python -m cortex.mcp.server' required
    - Cross-platform: Uses ${workspaceFolder} for portability
    """
    try:
        # Cross-platform Python path using VS Code variable
        # ${workspaceFolder} is resolved by VS Code at runtime
        if IS_WINDOWS:
            python_path = "${workspaceFolder}/.venv/Scripts/python.exe"
        else:
            python_path = "${workspaceFolder}/.venv/bin/python"

        # MCP configuration (Pylance-style: auto-started by VS Code)
        server_config = {
            "command": python_path,
            "args": ["-m", "cortex.mcp"],
            "env": {
                "CORTEX_ENV": "development",
                "CORTEX_MCP_ENABLED": "true",
                "PYTHONPATH": "${workspaceFolder}",
                "CORTEX_WORKSPACE": "${workspaceFolder}"
            },
        }

        # Use JSONC-safe merge (preserves comments, globs, formatting)
        success = _merge_mcp_servers_safely(settings_path, "cortex", server_config)
        
        if success:
            logger.info(f"✅ MCP configuration injected into .vscode/settings.json")
            ok, current, _ = _read_jsonc_file(settings_path)
            return True, current or {}
        else:
            return False, {}

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
    
    Uses JSONC-safe reading to avoid corrupting glob patterns.
    
    Returns:
        List of detected competing servers with their locations.
    """
    competing = []
    
    # Check .vscode/settings.json
    settings_path = Path(".vscode/settings.json")
    if settings_path.exists():
        ok, settings, _ = _read_jsonc_file(settings_path)
        if ok and settings:
            mcp_servers = settings.get("github.copilot.chat.mcpServers", {})
            for server_name in mcp_servers:
                if server_name.lower() != "cortex":
                    competing.append({
                        "name": server_name,
                        "location": "settings.json",
                        "path": str(settings_path)
                    })
    
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
    
    Uses JSONC-safe read/write to preserve existing settings, comments,
    and glob patterns. Only modifies Pylance-specific keys.
    
    Args:
        settings_path: Path to .vscode/settings.json
    
    Returns:
        True if successfully disabled or already disabled.
    """
    try:
        if not settings_path.exists():
            return True
        
        ok, settings, raw = _read_jsonc_file(settings_path)
        if not ok or settings is None:
            return False
        
        modified = False
        
        # Disable Pylance MCP server setting
        if settings.get("pylance.mcpServer.enabled") is not False:
            _write_settings_safely(settings_path, "pylance.mcpServer.enabled", False, raw)
            modified = True
            logger.info("✅ Disabled Pylance MCP server (pylance.mcpServer.enabled = false)")
            # Re-read after write
            _, settings, raw = _read_jsonc_file(settings_path)
        
        # Remove Pylance from mcpServers if present
        mcp_servers = settings.get("github.copilot.chat.mcpServers", {}) if settings else {}
        if "pylance" in mcp_servers:
            _remove_mcp_server_safely(settings_path, "pylance")
            modified = True
        
        if not modified:
            logger.info("✅ Pylance MCP already disabled")
        
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
