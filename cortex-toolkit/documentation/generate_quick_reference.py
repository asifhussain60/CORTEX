"""
Extract Quick Reference Commands

Extracts the most useful CORTEX commands from cortex-operations.yaml
and creates a quick reference table.

Author: Asif Hussain
"""

import yaml
from pathlib import Path
from typing import List, Dict, Tuple

CORTEX_ROOT = Path(__file__).resolve().parents[1]
OPERATIONS_FILE = CORTEX_ROOT / "cortex-operations.yaml"

# Priority commands with manual triggers (ordered by importance/frequency of use)
PRIORITY_COMMANDS = [
    ("help", "help", "Show available commands and CORTEX capabilities"),
    ("plan", "plan [feature]", "Create implementation plan with DoR/DoD validation"),
    ("start_tdd", "start tdd", "Begin TDD workflow (RED → GREEN → REFACTOR)"),
    ("commit", "commit", "Stage, commit, push changes with brain protection"),
    ("align", "align", "Run system alignment checks and integration scoring"),
    ("optimize", "optimize", "Optimize CORTEX with SKULL tests and validation"),
    ("tutorial", "tutorial", "Interactive 15-30 min CORTEX learning program"),
    ("load_dashboard", "load dashboard", "Launch dashboard with HTTP server"),
    ("upgrade_cortex", "upgrade cortex", "Upgrade CORTEX to latest version safely"),
    ("resume_conversation", "resume [topic]", "Resume previous conversation with full context"),
    ("feedback", "feedback", "Submit bug report or feature request"),
    ("discover_views", "discover views", "Extract element IDs from Razor/Blazor files"),
    ("run_tests", "run tests", "Execute tests with auto-debug on failures"),
    ("deploy_cortex_production", "deploy cortex", "Build and publish production package (admin)"),
    ("review_architecture", "review architecture", "Analyze health trends and forecast debt")
]


def load_operations() -> Dict:
    """Load operations from YAML file."""
    with open(OPERATIONS_FILE, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    return data.get('operations', {})


def extract_command_info(operation_name: str, operation_data: Dict) -> Tuple[str, str, str]:
    """Extract command name, triggers, and description."""
    name = operation_data.get('name', operation_name)
    description = operation_data.get('description', 'No description')
    
    # Get first natural language trigger
    triggers = operation_data.get('natural_language', [])
    if triggers:
        # Clean up trigger (remove {variables})
        trigger = triggers[0].replace('{', '').replace('}', '').strip()
    else:
        trigger = operation_name.replace('_', ' ')
    
    # Shorten description if too long
    if len(description) > 70:
        description = description[:67] + "..."
    
    return (trigger, name, description)


def create_quick_reference_table(limit: int = 15) -> str:
    """Create markdown table of quick reference commands."""
    
    # Use priority commands with manual triggers
    commands = PRIORITY_COMMANDS[:limit]
    
    # Build table
    table = "| Command | Description |\n"
    table += "|---------|-------------|\n"
    
    for _, trigger, description in commands:
        # Escape pipe characters in description
        description = description.replace('|', '\\|')
        table += f"| `{trigger}` | {description} |\n"
    
    return table


def main():
    """Generate quick reference table."""
    print("=" * 80)
    print("CORTEX Quick Reference Generator")
    print("=" * 80)
    print()
    
    operations = load_operations()
    print(f"[*] Loaded {len(operations)} operations")
    
    # Count ready operations
    ready = sum(1 for op in operations.values() 
                if op.get('implementation_status', {}).get('status') == 'ready')
    print(f"[OK] {ready} operations ready")
    print()
    
    # Generate table
    table = create_quick_reference_table(limit=15)
    
    print("Quick Reference Table (Top 15 Commands):")
    print()
    print(table)
    
    # Save to include file
    output_file = CORTEX_ROOT / ".github" / "prompts" / "includes" / "quick-reference-table.md"
    
    content = f"""# Quick Reference - Top 15 Commands

{table}

**Full Command List:** See `cortex-operations.yaml` for all {len(operations)} available operations
"""
    
    output_file.write_text(content, encoding='utf-8')
    print()
    print(f"[OK] Saved to: {output_file.relative_to(CORTEX_ROOT)}")
    
    return 0


if __name__ == "__main__":
    exit(main())
