#!/usr/bin/env python3
"""
VS Code MCP Tool Manager
Purpose: Manage VS Code Copilot MCP tool configuration to stay under 128-tool limit
Authority: CORE-051 (Cross-platform MCP compatibility)

This script helps:
1. List all configured MCP servers
2. Disable non-essential MCP servers
3. Keep CORTEX tools enabled (essential)
4. Stay under VS Code's 128-tool performance limit

Usage:
    python .cortex/manage-vscode-mcp-tools.py --list          # List all servers
    python .cortex/manage-vscode-mcp-tools.py --optimize      # Auto-optimize (disable non-essential)
    python .cortex/manage-vscode-mcp-tools.py --disable-server gitkraken  # Disable specific server
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, Any, List
import shutil
from datetime import datetime


# ============================================================================
# CONFIGURATION
# ============================================================================

# Essential MCP servers (DO NOT DISABLE)
ESSENTIAL_SERVERS = {
    "cortex": "CORTEX production tools (24 tools) - REQUIRED for all operations"
}

# Non-essential servers that can be safely disabled
NON_ESSENTIAL_SERVERS = {
    "gitkraken": "GitKraken integration - can use git CLI instead",
    "pylance": "Pylance MCP - redundant with VS Code built-in Pylance",
    "github": "GitHub integration - can use GitHub CLI/web instead",
}

# VS Code tool limit (performance degrades above this)
VSCODE_TOOL_LIMIT = 128


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_settings_path() -> Path:
    """Get VS Code settings.json path."""
    return Path(".vscode/settings.json")


def backup_settings() -> Path:
    """Create backup of settings.json."""
    settings_path = get_settings_path()
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = settings_path.parent / f"settings.json.backup-{timestamp}"
    
    if settings_path.exists():
        shutil.copy2(settings_path, backup_path)
        print(f"✅ Backup created: {backup_path}")
        return backup_path
    return None


def load_settings() -> Dict[str, Any]:
    """Load VS Code settings."""
    settings_path = get_settings_path()
    
    if not settings_path.exists():
        print(f"❌ Settings file not found: {settings_path}")
        sys.exit(1)
    
    with open(settings_path, 'r') as f:
        # Handle JSON with comments (jsonc)
        content = f.read()
        # Remove single-line comments
        lines = [line.split('//')[0] if '//' in line else line 
                 for line in content.split('\n')]
        cleaned_content = '\n'.join(lines)
        return json.loads(cleaned_content)


def save_settings(settings: Dict[str, Any]) -> None:
    """Save VS Code settings."""
    settings_path = get_settings_path()
    
    with open(settings_path, 'w') as f:
        json.dump(settings, f, indent=2)
    
    print(f"✅ Settings saved: {settings_path}")


def get_mcp_servers(settings: Dict[str, Any]) -> Dict[str, Any]:
    """Get MCP server configuration."""
    return settings.get("github.copilot.chat.mcpServers", {})


def estimate_tool_count(server_name: str) -> int:
    """Estimate number of tools for known servers."""
    estimates = {
        "cortex": 24,      # Known exact count
        "gitkraken": 15,   # Estimated
        "pylance": 20,     # Estimated
        "github": 30,      # Estimated
    }
    return estimates.get(server_name.lower(), 10)  # Default estimate


# ============================================================================
# COMMANDS
# ============================================================================

def list_servers(settings: Dict[str, Any], verbose: bool = False) -> None:
    """List all configured MCP servers."""
    mcp_servers = get_mcp_servers(settings)
    
    print("\n" + "="*80)
    print("📋 VS Code MCP Servers Configuration")
    print("="*80 + "\n")
    
    if not mcp_servers:
        print("⚠️  No MCP servers configured")
        return
    
    total_estimated_tools = 0
    
    for server_name, config in mcp_servers.items():
        is_essential = server_name in ESSENTIAL_SERVERS
        tool_count = estimate_tool_count(server_name)
        total_estimated_tools += tool_count
        
        status = "✅ ESSENTIAL" if is_essential else "⚪ OPTIONAL"
        
        print(f"{status} {server_name}")
        print(f"   Estimated Tools: ~{tool_count}")
        
        if verbose:
            print(f"   Command: {config.get('command', 'N/A')}")
            args = config.get('args', [])
            if args:
                print(f"   Args: {' '.join(args)}")
        
        if is_essential:
            print(f"   Note: {ESSENTIAL_SERVERS[server_name]}")
        elif server_name in NON_ESSENTIAL_SERVERS:
            print(f"   Note: {NON_ESSENTIAL_SERVERS[server_name]}")
        
        print()
    
    print("-" * 80)
    print(f"📊 Total Estimated Tools: ~{total_estimated_tools}")
    print(f"📏 VS Code Limit: {VSCODE_TOOL_LIMIT} tools")
    
    if total_estimated_tools > VSCODE_TOOL_LIMIT:
        print(f"⚠️  WARNING: Above limit by ~{total_estimated_tools - VSCODE_TOOL_LIMIT} tools")
        print(f"   Performance may degrade. Consider disabling non-essential servers.")
    else:
        print(f"✅ Within limit (margin: {VSCODE_TOOL_LIMIT - total_estimated_tools} tools)")
    
    print("="*80 + "\n")


def disable_server(settings: Dict[str, Any], server_name: str, dry_run: bool = False) -> Dict[str, Any]:
    """Disable a specific MCP server."""
    mcp_servers = get_mcp_servers(settings)
    
    if server_name not in mcp_servers:
        print(f"❌ Server '{server_name}' not found in configuration")
        return settings
    
    if server_name in ESSENTIAL_SERVERS:
        print(f"❌ Cannot disable essential server: {server_name}")
        print(f"   Reason: {ESSENTIAL_SERVERS[server_name]}")
        return settings
    
    if dry_run:
        print(f"🔍 DRY RUN: Would disable server '{server_name}'")
        return settings
    
    # Remove server from configuration
    del settings["github.copilot.chat.mcpServers"][server_name]
    
    print(f"✅ Disabled MCP server: {server_name}")
    return settings


def optimize_configuration(settings: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
    """Auto-optimize MCP configuration by disabling non-essential servers."""
    mcp_servers = get_mcp_servers(settings)
    
    print("\n" + "="*80)
    print("🔧 Optimizing MCP Configuration")
    print("="*80 + "\n")
    
    # Calculate current tool count
    total_tools = sum(estimate_tool_count(name) for name in mcp_servers)
    
    print(f"Current estimated tools: ~{total_tools}")
    print(f"VS Code limit: {VSCODE_TOOL_LIMIT}")
    print()
    
    if total_tools <= VSCODE_TOOL_LIMIT:
        print("✅ Already within limit. No optimization needed.")
        return settings
    
    # Find non-essential servers to disable
    servers_to_disable = []
    for server_name in mcp_servers:
        if server_name not in ESSENTIAL_SERVERS:
            servers_to_disable.append(server_name)
    
    if not servers_to_disable:
        print("⚠️  All servers are essential. Cannot optimize further.")
        return settings
    
    print(f"Found {len(servers_to_disable)} non-essential server(s) to disable:\n")
    
    for server_name in servers_to_disable:
        tool_count = estimate_tool_count(server_name)
        print(f"  - {server_name} (~{tool_count} tools)")
        if server_name in NON_ESSENTIAL_SERVERS:
            print(f"    Reason: {NON_ESSENTIAL_SERVERS[server_name]}")
    
    print()
    
    if dry_run:
        print("🔍 DRY RUN: No changes made")
        print("\nRun without --dry-run to apply changes")
        return settings
    
    # Disable non-essential servers
    for server_name in servers_to_disable:
        settings = disable_server(settings, server_name, dry_run=False)
    
    # Calculate new tool count
    new_total = sum(estimate_tool_count(name) 
                   for name in settings.get("github.copilot.chat.mcpServers", {}))
    
    print()
    print("-" * 80)
    print(f"📊 Optimization Results:")
    print(f"   Before: ~{total_tools} tools")
    print(f"   After:  ~{new_total} tools")
    print(f"   Saved:  ~{total_tools - new_total} tools")
    
    if new_total <= VSCODE_TOOL_LIMIT:
        print(f"✅ Now within limit!")
    
    print("="*80 + "\n")
    
    return settings


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Manage VS Code MCP tool configuration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all configured servers
  python .cortex/manage-vscode-mcp-tools.py --list
  
  # List with verbose details
  python .cortex/manage-vscode-mcp-tools.py --list --verbose
  
  # Optimize (dry run)
  python .cortex/manage-vscode-mcp-tools.py --optimize --dry-run
  
  # Optimize (apply changes)
  python .cortex/manage-vscode-mcp-tools.py --optimize
  
  # Disable specific server
  python .cortex/manage-vscode-mcp-tools.py --disable-server gitkraken
        """
    )
    
    parser.add_argument("--list", action="store_true",
                       help="List all configured MCP servers")
    parser.add_argument("--verbose", action="store_true",
                       help="Show verbose output")
    parser.add_argument("--optimize", action="store_true",
                       help="Auto-optimize by disabling non-essential servers")
    parser.add_argument("--disable-server", type=str, metavar="NAME",
                       help="Disable specific MCP server")
    parser.add_argument("--dry-run", action="store_true",
                       help="Preview changes without applying")
    parser.add_argument("--no-backup", action="store_true",
                       help="Skip backup creation (not recommended)")
    
    args = parser.parse_args()
    
    # Load settings
    settings = load_settings()
    
    # Execute command
    if args.list:
        list_servers(settings, verbose=args.verbose)
    
    elif args.optimize:
        if not args.no_backup:
            backup_settings()
        
        settings = optimize_configuration(settings, dry_run=args.dry_run)
        
        if not args.dry_run:
            save_settings(settings)
            print("\n⚠️  IMPORTANT: Reload VS Code for changes to take effect")
            print("   Cmd+Shift+P → 'Developer: Reload Window'\n")
    
    elif args.disable_server:
        if not args.no_backup:
            backup_settings()
        
        settings = disable_server(settings, args.disable_server, dry_run=args.dry_run)
        
        if not args.dry_run:
            save_settings(settings)
            print("\n⚠️  IMPORTANT: Reload VS Code for changes to take effect")
            print("   Cmd+Shift+P → 'Developer: Reload Window'\n")
    
    else:
        parser.print_help()
        print("\n💡 Tip: Start with --list to see current configuration")


if __name__ == "__main__":
    main()
