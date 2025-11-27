"""
CORTEX Help System

Provides concise, bulletted command reference for easy memorization.
Shows entry point commands, slash commands, and natural language equivalents.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from typing import Dict, List, Optional
from enum import Enum
from src.plugins.command_registry import get_command_registry, CommandCategory


class HelpFormat(Enum):
    """Help display formats"""
    CONCISE = "concise"      # Quick bulletted list
    DETAILED = "detailed"    # Full descriptions with examples
    CATEGORY = "category"    # Grouped by category


def show_help(format: HelpFormat = HelpFormat.CONCISE, 
              category: Optional[CommandCategory] = None) -> str:
    """
    Generate help text for CORTEX commands.
    
    Args:
        format: Display format (concise, detailed, or category)
        category: Optional category filter
    
    Returns:
        Formatted help text
    
    Examples:
        >>> print(show_help())  # Quick bulletted list
        >>> print(show_help(HelpFormat.DETAILED))  # Full details
        >>> print(show_help(category=CommandCategory.PLATFORM))  # Platform commands only
    """
    registry = get_command_registry()
    
    if format == HelpFormat.CONCISE:
        return _generate_concise_help(registry, category)
    elif format == HelpFormat.DETAILED:
        return _generate_detailed_help(registry, category)
    elif format == HelpFormat.CATEGORY:
        return _generate_category_help(registry)
    else:
        return _generate_concise_help(registry, category)


def _generate_concise_help(registry, category: Optional[CommandCategory] = None) -> str:
    """
    Generate concise bulletted help - easy to scan and remember.
    
    Format:
    • /command - Description
    • /command (alias1, alias2) - Description
    """
    commands = (registry.get_commands_by_category(category) 
                if category else registry.get_all_commands())
    
    if not commands:
        return "No commands available."
    
    # Build header
    title = "🧠 CORTEX Quick Command Reference\n\n"
    if category:
        title = f"🧠 CORTEX {category.value.title()} Commands\n\n"
    
    help_text = title
    help_text += "💡 *Tip: Natural language works everywhere! Commands are optional shortcuts.*\n\n"
    
    # Add discovery section only for full help (not category-filtered)
    if not category:
        help_text += "## 🎯 New to CORTEX?\n\n"
        help_text += "**Quick Discovery:**\n"
        help_text += "• `discover cortex` - Interactive guide to explore CORTEX capabilities\n"
        help_text += "• `cortex demo` - See live demonstrations of key features\n"
        help_text += "• `tutorial` - 15-30 min hands-on learning (build real authentication feature)\n\n"
        help_text += "**Try saying:** *\"discover cortex\"* or *\"show me what cortex can do\"*\n\n"
        help_text += "---\n\n"
    
    # Group by category
    by_category: Dict[CommandCategory, List] = {}
    for cmd in commands:
        if cmd.category not in by_category:
            by_category[cmd.category] = []
        by_category[cmd.category].append(cmd)
    
    # Generate bulletted list per category
    for cat in sorted(by_category.keys(), key=lambda x: x.value):
        help_text += f"**{cat.value.upper()}**\n"
        
        for cmd_meta in sorted(by_category[cat], key=lambda x: x.command):
            bullet = f"• `{cmd_meta.command}`"
            
            # Add aliases inline if present
            if cmd_meta.aliases:
                aliases_str = ", ".join(f"`{a}`" for a in cmd_meta.aliases)
                bullet += f" ({aliases_str})"
            
            bullet += f" - {cmd_meta.description}"
            
            # Add natural language hint
            if cmd_meta.natural_language_equivalent:
                bullet += f"\n  *Say: \"{cmd_meta.natural_language_equivalent}\"*"
            
            help_text += bullet + "\n"
        
        help_text += "\n"
    
    # Add footer with stats
    stats = registry.get_stats()
    help_text += f"---\n"
    help_text += f"📊 {stats['unique_commands']} commands • {stats['total_plugins']} plugins\n"
    
    return help_text


def _generate_detailed_help(registry, category: Optional[CommandCategory] = None) -> str:
    """
    Generate detailed help with examples and usage patterns.
    """
    commands = (registry.get_commands_by_category(category) 
                if category else registry.get_all_commands())
    
    if not commands:
        return "No commands available."
    
    # Build header
    title = "# CORTEX Command Reference (Detailed)\n\n"
    if category:
        title = f"# CORTEX {category.value.title()} Commands (Detailed)\n\n"
    
    help_text = title
    help_text += "**Commands are shortcuts. Natural language works everywhere!**\n\n"
    
    # Add discovery section only for full help (not category-filtered)
    if not category:
        help_text += "## 🚀 Getting Started\n\n"
        help_text += "**New to CORTEX?** Start with these interactive guides:\n\n"
        help_text += "• **`discover cortex`** - Explore all capabilities with interactive choices\n"
        help_text += "• **`cortex demo`** - See live demonstrations of features:\n"
        help_text += "  - `demo planning` - Planning System 2.0 with DoR/DoD enforcement\n"
        help_text += "  - `demo tdd` - RED→GREEN→REFACTOR automation\n"
        help_text += "  - `demo view discovery` - Auto-extract UI elements (92% time savings)\n"
        help_text += "  - `demo feedback` - Structured issue reporting\n"
        help_text += "  - `demo upgrade` - Universal upgrade system\n"
        help_text += "• **`tutorial`** - 15-30 minute hands-on learning program\n"
        help_text += "  - Build real authentication feature with tests\n"
        help_text += "  - Learn planning, TDD, validation workflows\n\n"
        help_text += "**Quick paths:**\n"
        help_text += "- *Beginner:* `help` → `tutorial` → `demo planning`\n"
        help_text += "- *Advanced:* `discover cortex` → `system alignment` → `admin help`\n"
        help_text += "- *Developer:* `demo tdd` → `demo view discovery` → `git checkpoint`\n\n"
        help_text += "---\n\n"
    
    # Group by category
    by_category: Dict[CommandCategory, List] = {}
    for cmd in commands:
        if cmd.category not in by_category:
            by_category[cmd.category] = []
        by_category[cmd.category].append(cmd)
    
    # Generate detailed entries per category
    for cat in sorted(by_category.keys(), key=lambda x: x.value):
        help_text += f"## {cat.value.title()}\n\n"
        
        for cmd_meta in sorted(by_category[cat], key=lambda x: x.command):
            help_text += f"### `{cmd_meta.command}`\n\n"
            help_text += f"{cmd_meta.description}\n\n"
            
            # Natural language equivalent
            if cmd_meta.natural_language_equivalent:
                help_text += f"**Natural Language:** \"{cmd_meta.natural_language_equivalent}\"\n\n"
            
            # Aliases
            if cmd_meta.aliases:
                aliases_str = ", ".join(f"`{a}`" for a in cmd_meta.aliases)
                help_text += f"**Aliases:** {aliases_str}\n\n"
            
            # Examples
            if cmd_meta.examples:
                help_text += "**Examples:**\n"
                for example in cmd_meta.examples:
                    help_text += f"- `{example}`\n"
                help_text += "\n"
            
            # Requirements
            if cmd_meta.requires_online:
                help_text += "⚠️ *Requires CORTEX brain connection*\n\n"
            
            help_text += "---\n\n"
    
    return help_text


def _generate_category_help(registry) -> str:
    """
    Generate help organized by category with command counts.
    """
    help_text = "# CORTEX Commands by Category\n\n"
    
    # Get all categories
    all_commands = registry.get_all_commands()
    by_category: Dict[CommandCategory, List] = {}
    
    for cmd in all_commands:
        if cmd.category not in by_category:
            by_category[cmd.category] = []
        by_category[cmd.category].append(cmd)
    
    # Summary table
    help_text += "| Category | Commands | Description |\n"
    help_text += "|----------|----------|-------------|\n"
    
    category_descriptions = {
        CommandCategory.PLATFORM: "Environment and platform management",
        CommandCategory.WORKFLOW: "Task and workflow control",
        CommandCategory.SESSION: "Conversation and session management",
        CommandCategory.DOCUMENTATION: "Help and documentation",
        CommandCategory.TESTING: "Test execution and validation",
        CommandCategory.MAINTENANCE: "Cleanup and optimization",
        CommandCategory.EXTENSION: "VS Code extension features",
        CommandCategory.CUSTOM: "User-defined commands"
    }
    
    for cat in sorted(by_category.keys(), key=lambda x: x.value):
        count = len(by_category[cat])
        desc = category_descriptions.get(cat, "Custom commands")
        help_text += f"| {cat.value.title()} | {count} | {desc} |\n"
    
    help_text += "\n---\n\n"
    
    # List commands per category
    for cat in sorted(by_category.keys(), key=lambda x: x.value):
        help_text += f"## {cat.value.title()}\n\n"
        
        for cmd_meta in sorted(by_category[cat], key=lambda x: x.command):
            help_text += f"- `{cmd_meta.command}` - {cmd_meta.description}\n"
        
        help_text += "\n"
    
    return help_text


def get_quick_reference() -> str:
    """
    Get ultra-concise quick reference - just the essentials.
    
    Perfect for chat responses when user asks "what commands are available?"
    
    Returns:
        Ultra-concise command list
    """
    registry = get_command_registry()
    
    help_text = "**CORTEX Quick Commands:**\n\n"
    
    # Core essentials only
    core_commands = [
        "/help - Show all commands",
        "/setup - Configure environment", 
        "/resume - Continue last conversation",
        "/status - Show progress"
    ]
    
    for cmd in core_commands:
        help_text += f"• {cmd}\n"
    
    help_text += f"\n💡 Or just use natural language - CORTEX understands!\n"
    
    return help_text


def handle_help_request(request: str) -> str:
    """
    Handle help requests intelligently based on what user asks for.
    
    Args:
        request: User's help request
    
    Returns:
        Appropriate help text
    
    Examples:
        "show help" → concise help
        "detailed help" → detailed help
        "platform commands" → platform category help
        "quick reference" → ultra-concise reference
    """
    request_lower = request.lower()
    
    # Detect format preference
    if any(word in request_lower for word in ['detailed', 'full', 'complete', 'explain']):
        return show_help(HelpFormat.DETAILED)
    
    if any(word in request_lower for word in ['quick', 'brief', 'short', 'summary']):
        return get_quick_reference()
    
    # Detect category preference
    category_map = {
        'platform': CommandCategory.PLATFORM,
        'workflow': CommandCategory.WORKFLOW,
        'session': CommandCategory.SESSION,
        'documentation': CommandCategory.DOCUMENTATION,
        'testing': CommandCategory.TESTING,
        'test': CommandCategory.TESTING,
        'maintenance': CommandCategory.MAINTENANCE,
        'extension': CommandCategory.EXTENSION,
        'custom': CommandCategory.CUSTOM
    }
    
    for keyword, category in category_map.items():
        if keyword in request_lower:
            return show_help(HelpFormat.CONCISE, category)
    
    # Check if asking for categories
    if any(word in request_lower for word in ['categories', 'category', 'organize']):
        return show_help(HelpFormat.CATEGORY)
    
    # Default: concise help
    return show_help(HelpFormat.CONCISE)


# Convenience function for quick access
def cortex_help() -> str:
    """Quick access to concise help."""
    return show_help(HelpFormat.CONCISE)


if __name__ == "__main__":
    # Demo the help system
    print("=== CONCISE HELP ===\n")
    print(show_help(HelpFormat.CONCISE))
    
    print("\n\n=== QUICK REFERENCE ===\n")
    print(get_quick_reference())
    
    print("\n\n=== CATEGORY HELP ===\n")
    print(show_help(HelpFormat.CATEGORY))
