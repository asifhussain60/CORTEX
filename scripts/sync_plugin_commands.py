#!/usr/bin/env python3
"""
Plugin Command Discovery and Documentation Sync

Automatically discovers all plugin commands from the command registry
and updates the GitHub Copilot entry point files with current plugin list.

This ensures that when you add a new plugin with commands, the `/CORTEX`
entry point automatically reflects the new commands without manual updates.

Usage:
    python scripts/sync_plugin_commands.py
    
    # Or with auto-update on plugin changes
    python scripts/sync_plugin_commands.py --watch

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sys
from pathlib import Path
from typing import Dict, List, Set
import importlib
import inspect

# Add src to path
CORTEX_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(CORTEX_ROOT / "src"))

from plugins.command_registry import PluginCommandRegistry, CommandMetadata, CommandCategory


def discover_all_plugins() -> List[str]:
    """Discover all plugin modules in src/plugins/"""
    plugins_dir = CORTEX_ROOT / "src" / "plugins"
    plugin_files = []
    
    for file in plugins_dir.glob("*_plugin.py"):
        plugin_name = file.stem
        plugin_files.append(plugin_name)
    
    return sorted(plugin_files)


def load_plugin_commands() -> Dict[str, List[CommandMetadata]]:
    """Load all commands from all plugins."""
    registry = PluginCommandRegistry()
    plugin_commands: Dict[str, List[CommandMetadata]] = {}
    
    plugins = discover_all_plugins()
    
    for plugin_name in plugins:
        try:
            # Import plugin module
            module = importlib.import_module(f"plugins.{plugin_name}")
            
            # Find and instantiate plugin
            if hasattr(module, 'register'):
                plugin = module.register()
                
                # Get commands if plugin has them
                if hasattr(plugin, 'register_commands'):
                    commands = plugin.register_commands()
                    if commands:
                        plugin_id = plugin.metadata.plugin_id
                        plugin_commands[plugin_id] = commands
                        
                        print(f"✅ {plugin_id}: {len(commands)} command(s)")
        except Exception as e:
            print(f"⚠️  {plugin_name}: {e}")
    
    return plugin_commands


def generate_plugin_list_markdown(plugin_commands: Dict[str, List[CommandMetadata]]) -> str:
    """Generate markdown list of plugins and their commands."""
    lines = []
    
    # Group by category
    by_category: Dict[CommandCategory, List[tuple]] = {}
    
    for plugin_id, commands in plugin_commands.items():
        for cmd in commands:
            category = cmd.category
            if category not in by_category:
                by_category[category] = []
            by_category[category].append((plugin_id, cmd))
    
    # Generate markdown
    lines.append("**Current plugins with commands:**")
    lines.append("")
    
    category_names = {
        CommandCategory.PLATFORM: "🖥️  Platform & Environment",
        CommandCategory.WORKFLOW: "🔄 Workflow & Tasks",
        CommandCategory.SESSION: "💬 Session Management",
        CommandCategory.DOCUMENTATION: "📚 Documentation",
        CommandCategory.TESTING: "🧪 Testing",
        CommandCategory.MAINTENANCE: "🧹 Maintenance",
        CommandCategory.EXTENSION: "🔌 Extensions",
        CommandCategory.CUSTOM: "⚙️  Custom"
    }
    
    for category in CommandCategory:
        if category not in by_category:
            continue
        
        lines.append(f"### {category_names.get(category, category.value.title())}")
        lines.append("")
        
        for plugin_id, cmd in by_category[category]:
            # Format: - **Plugin Name:** `/command` - Description
            aliases = f" (aliases: {', '.join(cmd.aliases)})" if cmd.aliases else ""
            lines.append(f"- **{plugin_id}:** `{cmd.command}`{aliases} - {cmd.description}")
        
        lines.append("")
    
    return "\n".join(lines)


def update_copilot_instructions(plugin_list: str):
    """Update .github/copilot-instructions.md with current plugin list."""
    file_path = CORTEX_ROOT / ".github" / "copilot-instructions.md"
    
    if not file_path.exists():
        print(f"⚠️  {file_path} not found")
        return
    
    content = file_path.read_text()
    
    # Find the plugin section
    start_marker = "**Current Plugins:**"
    end_marker = "---\n\n## 🚀 Quick Commands"
    
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker)
    
    if start_idx == -1 or end_idx == -1:
        print("⚠️  Plugin section markers not found in copilot-instructions.md")
        return
    
    # Replace plugin section
    new_content = (
        content[:start_idx] +
        start_marker + "\n" +
        plugin_list + "\n" +
        content[end_idx:]
    )
    
    file_path.write_text(new_content)
    print(f"✅ Updated {file_path}")


def update_prompt_file(plugin_list: str):
    """Update .github/prompts/CORTEX.prompt.md with current plugin list."""
    file_path = CORTEX_ROOT / ".github" / "prompts" / "CORTEX.prompt.md"
    
    if not file_path.exists():
        print(f"⚠️  {file_path} not found")
        return
    
    content = file_path.read_text()
    
    # Find the plugin section
    start_marker = "**Current plugins with commands:**"
    end_marker = "**How it works:**"
    
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker)
    
    if start_idx == -1 or end_idx == -1:
        print("⚠️  Plugin section markers not found in CORTEX.prompt.md")
        return
    
    # Replace plugin section
    new_content = (
        content[:start_idx] +
        plugin_list + "\n\n" +
        content[end_idx:]
    )
    
    file_path.write_text(new_content)
    print(f"✅ Updated {file_path}")


def main():
    """Main execution."""
    print("🔍 Discovering plugin commands...")
    print()
    
    # Load all plugin commands
    plugin_commands = load_plugin_commands()
    
    if not plugin_commands:
        print("⚠️  No plugin commands found")
        return
    
    print()
    print(f"📊 Found {len(plugin_commands)} plugin(s) with commands")
    print()
    
    # Generate markdown
    plugin_list = generate_plugin_list_markdown(plugin_commands)
    
    print("📝 Generated plugin list:")
    print()
    print(plugin_list)
    print()
    
    # Update files
    print("📄 Updating entry point files...")
    update_copilot_instructions(plugin_list)
    update_prompt_file(plugin_list)
    
    print()
    print("✅ Plugin command sync complete!")
    print()
    print("💡 New plugins with commands are now available in:")
    print("   - .github/copilot-instructions.md (auto-loaded)")
    print("   - .github/prompts/CORTEX.prompt.md (/CORTEX command)")


if __name__ == "__main__":
    main()
