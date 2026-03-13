#!/usr/bin/env python3
"""
CORTEX MCP Setup Script — Cross-Platform Pylance-Style Configuration

Sets up VS Code MCP server configuration for CORTEX's Pylance-style stdio transport.
Auto-detects OS and configures appropriate Python executable path.

Authority: ENH-066 - MCP Setup Validation
Platform: macOS / Linux / Windows (cross-platform)
Phase: 126-a (Check #30 — Windows Boot Wiring Verification)

Usage:
    python setup-mcp.py             # write .vscode/settings.json
    python setup-mcp.py --dry-run   # validate without writing any files (CI safe)
"""

import argparse
import json
import logging
import platform
import subprocess
import sys
from pathlib import Path


def _setup_logging(log_dir: Path) -> logging.Logger:
    """Configure logging to file and stdout."""
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "setup.log"

    logger = logging.getLogger("cortex.mcp.setup")
    logger.setLevel(logging.DEBUG)

    # File handler
    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter("%(asctime)s  %(levelname)-8s  %(message)s"))

    # Console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter("%(levelname)-8s %(message)s"))

    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


def _detect_python_executable() -> str:
    """Detect the appropriate Python executable for the current platform.

    Prefers sys.executable (the interpreter running this script) so that the
    MCP server always uses the same Python that set it up — critical on Windows
    where 'python3' may not exist on PATH and on virtual-env setups where the
    venv interpreter must be used.

    Returns:
        str: Full path or command name for the Python executable.
    """
    # sys.executable is the most reliable source — it is the exact interpreter
    # that is currently running this script, guaranteed to exist on all platforms.
    if sys.executable:
        return sys.executable

    os_name = platform.system()

    if os_name == "Windows":
        # Windows: prefer python over python3 (python3 may not exist)
        for candidate in ("python", "python3", "py"):
            try:
                result = subprocess.run(
                    [candidate, "--version"],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    return candidate
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue
        return "python"  # Fallback
    elif os_name == "Darwin":
        # macOS: prefer python3 (Homebrew/pyenv)
        for candidate in ("python3", "python"):
            try:
                result = subprocess.run(
                    [candidate, "--version"],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    return candidate
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue
        return "python3"
    elif os_name == "Linux":
        # Linux: python3 is canonical
        for candidate in ("python3", "python"):
            try:
                result = subprocess.run(
                    [candidate, "--version"],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    return candidate
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue
        return "python3"
    else:
        # posix fallback
        return "python3"


def _build_vscode_settings(workspace_root: Path, python_cmd: str) -> dict:
    """Build the VS Code settings.json MCP configuration block.

    Args:
        workspace_root: The workspace: root path.
        python_cmd: Python executable command detected for this platform.

    Returns:
        dict: VS Code settings configuration dict.
    """
    return {
        "github.copilot.chat.mcpServers": {
            "cortex": {
                "command": python_cmd,
                "args": ["-m", "cortex.mcp"],
                "transport": "stdio",
                "cwd": "${workspaceFolder}",
            }
        }
    }


def _strip_jsonc_comments(jsonc: str) -> str:
    """Strip // line-comments from a JSONC string, preserving string content.

    Implements BUG-001 fix: only strips // that appear OUTSIDE quoted strings,
    so glob patterns like "**/*-summary.md" are never corrupted.

    Args:
        jsonc: JSONC text (JSON with // comments).

    Returns:
        Valid JSON string with comments removed.
    """
    import re as _re
    result = []
    in_string = False
    i = 0
    while i < len(jsonc):
        ch = jsonc[i]
        if in_string:
            result.append(ch)
            if ch == '\\' and i + 1 < len(jsonc):
                # Escaped character — consume next char too
                i += 1
                result.append(jsonc[i])
            elif ch == '"':
                in_string = False
        else:
            if ch == '"':
                in_string = True
                result.append(ch)
            elif ch == '/' and i + 1 < len(jsonc) and jsonc[i + 1] == '/':
                # Line comment — skip to end of line
                while i < len(jsonc) and jsonc[i] != '\n':
                    i += 1
                continue
            else:
                result.append(ch)
        i += 1
    return ''.join(result)


def _write_settings_safely(path: "Path", key: str, value: object, original_content: str) -> None:
    """Write a key/value into a JSONC settings file, preserving comments.

    Implements BUG-001 fix: always writes back the original JSONC text (with
    comments) rather than a round-tripped JSON parse, updating only the target
    key's value via regex substitution.

    Args:
        path: Path to the .json / .jsonc settings file to update.
        key: Dot-notation key to set (e.g. "python.linting").
        value: New value to write.
        original_content: The original file content (with comments) as a string.
    """
    import json as _json
    import re as _re

    value_json = _json.dumps(value, indent=2)

    # Strategy: find the key in the JSONC source and replace its entire value
    # block (which may span multiple lines for nested objects).
    # We work on the stripped JSON to locate positions, then map back.
    clean = _strip_jsonc_comments(original_content)
    key_pattern = r'"' + _re.escape(key) + r'"\s*:\s*'
    m = _re.search(key_pattern, clean)

    if m:
        # Parse out the entire value from the clean JSON starting at m.end()
        # Use json.JSONDecoder.raw_decode to find where the value ends
        try:
            decoder = _json.JSONDecoder()
            _, end_idx = decoder.raw_decode(clean, m.end())
        except _json.JSONDecodeError:
            end_idx = m.end()

        # Indent the new value to match surrounding context
        indent = "  "
        if isinstance(value, (dict, list)):
            new_val_lines = value_json.splitlines()
            indented_val = ("\n" + indent).join(new_val_lines)
        else:
            indented_val = value_json

        # Build the replacement: key: value
        replacement_segment = f'"{key}": {indented_val}'
        updated = clean[:m.start()] + replacement_segment + clean[end_idx:]

        # Re-inject original comments: prefix the updated JSON with any leading
        # comments from the original JSONC source.
        comment_lines = []
        for line in original_content.splitlines():
            stripped = line.strip()
            if stripped.startswith("//"):
                comment_lines.append(line)
            else:
                break
        prefix = "\n".join(comment_lines) + "\n" if comment_lines else ""

        # Write: leading comments + updated JSON body (which has no comments)
        path.write_text(prefix + updated, encoding="utf-8")
    else:
        # Key not present — inject before closing brace
        clean_stripped = clean.rstrip()
        if clean_stripped.endswith("}"):
            body = clean_stripped[:-1].rstrip()
            if body and not body.endswith(","):
                body += ","
            if isinstance(value, (dict, list)):
                body += f'\n  "{key}": {value_json}'
            else:
                body += f'\n  "{key}": {value_json}'
            updated = body + "\n}"
        else:
            updated = clean + f'\n  "{key}": {value_json}\n'

        # Re-inject leading comments
        comment_lines = []
        for line in original_content.splitlines():
            stripped = line.strip()
            if stripped.startswith("//"):
                comment_lines.append(line)
            else:
                break
        prefix = "\n".join(comment_lines) + "\n" if comment_lines else ""
        path.write_text(prefix + updated, encoding="utf-8")


def _merge_mcp_servers_safely(path: "Path", server_name: str, config: dict) -> None:
    """Merge an MCP server entry into github.copilot.chat.mcpServers in settings.

    Preserves all existing comments (BUG-002 fix).

    Args:
        path: Path to the .json / .jsonc settings file to update.
        server_name: Key name for the MCP server (e.g. "cortex").
        config: Config dict for the server.
    """
    import json as _json

    original = path.read_text(encoding="utf-8")
    clean = _strip_jsonc_comments(original)
    existing: dict = {}
    try:
        existing = _json.loads(clean)
    except _json.JSONDecodeError:
        existing = {}

    servers: dict = existing.get("github.copilot.chat.mcpServers", {})
    servers.setdefault(server_name, {})
    servers[server_name].update(config)

    _write_settings_safely(path, "github.copilot.chat.mcpServers", servers, original)


def disable_pylance_mcp(path: "Path") -> None:
    """Set pylance.mcpServer.enabled to false in a JSONC settings file.

    Preserves all existing comments in the file.

    Args:
        path: Path to the .json / .jsonc settings file to update.
    """
    original = path.read_text(encoding="utf-8")
    _write_settings_safely(path, "pylance.mcpServer.enabled", False, original)


def _write_vscode_settings(workspace_root: Path, settings: dict, logger: logging.Logger) -> bool:
    """Write or merge MCP settings into .vscode/settings.json.

    Args:
        workspace_root: Root of the workspace.
        settings: Settings dict to merge.
        logger: Logger instance.

    Returns:
        bool: True if written successfully.
    """
    vscode_dir = workspace_root / ".vscode"
    vscode_dir.mkdir(exist_ok=True)
    settings_path = vscode_dir / "settings.json"

    existing: dict = {}
    if settings_path.exists():
        try:
            existing = json.loads(settings_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            logger.warning("Existing settings.json is malformed — overwriting")

    # Deep merge: preserve existing keys, update MCP block
    existing.update(settings)
    settings_path.write_text(
        json.dumps(existing, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8"
    )
    logger.info(f"✅ Wrote MCP settings → {settings_path}")
    return True


def main() -> int:
    """Run cross-platform MCP setup.

    Args supported (via argparse):
        --dry-run: Validate configuration without writing any files.
                   Exits 0 on success. Safe to run in CI on any platform.

    Returns:
        int: Exit code (0 = success, 1 = error).
    """
    parser = argparse.ArgumentParser(
        description="CORTEX MCP Setup — Cross-Platform Pylance-Style Configuration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python setup-mcp.py             # write .vscode/settings.json\n"
            "  python setup-mcp.py --dry-run   # validate only (CI safe, no file writes)\n"
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        dest="dry_run",
        help="Validate configuration without writing any files (CI safe).",
    )
    args = parser.parse_args()

    workspace_root = Path(__file__).parent.parent.resolve()
    log_dir = workspace_root / ".cortex-runtime" / "logs"

    logger = _setup_logging(log_dir)
    logger.info(f"CORTEX MCP Setup — platform={platform.system()}, python={sys.version}")
    logger.info(f"Workspace root: {workspace_root}")

    if args.dry_run:
        logger.info("--dry-run mode: validation only, no files will be written")

    # Detect platform
    os_name = platform.system()
    logger.info(f"Operating system: {os_name}")

    if os_name == "Windows":
        logger.info("Windows detected — using sys.executable path")
    elif os_name == "Darwin":
        logger.info("macOS (Darwin) detected — using sys.executable path")
    elif os_name == "Linux":
        logger.info("Linux detected — using sys.executable path")
    else:
        logger.info(f"posix-like OS detected ({os_name}) — using sys.executable path")

    python_cmd = _detect_python_executable()
    logger.info(f"Python executable: {python_cmd}")

    if args.dry_run:
        # Dry-run: validate that we can compute the settings without writing them
        settings = _build_vscode_settings(workspace_root, python_cmd)
        mcp_config = settings.get("github.copilot.chat.mcpServers", {}).get("cortex", {})
        if not mcp_config.get("command") or not mcp_config.get("args"):
            logger.error("❌ Dry-run validation failed: MCP config block is incomplete")
            return 1
        logger.info("✅ Dry-run validation passed — MCP configuration is valid")
        logger.info(f"  command: {mcp_config['command']}")
        logger.info(f"  args: {mcp_config['args']}")
        logger.info(f"  transport: {mcp_config.get('transport', 'stdio')}")
        logger.info("  (no files written)")
        return 0

    # Build and write VS Code settings
    settings = _build_vscode_settings(workspace_root, python_cmd)
    success = _write_vscode_settings(workspace_root, settings, logger)

    if success:
        logger.info("✅ CORTEX MCP setup complete")
        logger.info("  Restart VS Code to activate Pylance-style stdio transport")
        return 0
    else:
        logger.error("❌ CORTEX MCP setup failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
