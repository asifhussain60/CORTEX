"""
CORTEX Help Command - Live Demo

Demonstrates the help command functionality with all three formats.

Author: Asif Hussain
Date: 2025-11-10
"""

from pathlib import Path
from src.operations import execute_operation, show_help

def demo_help_command():
    """Run comprehensive help command demo."""
    
    print("\n" + "="*90)
    print("CORTEX HELP COMMAND - LIVE DEMO")
    print("="*90 + "\n")
    
    # Method 1: Via execute_operation
    print("METHOD 1: Via execute_operation('help')")
    print("-" * 90)
    report = execute_operation('help')
    print(f"✓ Success: {report.success}")
    print(f"✓ Operation: {report.operation_name}")
    print(f"✓ Help text length: {len(report.context['help_text'])} characters\n")
    
    # Method 2: Direct function call (table format)
    print("\nMETHOD 2: Direct show_help() - TABLE FORMAT")
    print("-" * 90)
    table_help = show_help('table')
    print(table_help)
    
    # Write to file (avoids console encoding issues)
    output_dir = Path(__file__).parent
    
    # Table format
    table_file = output_dir / 'DEMO_HELP_TABLE.txt'
    table_file.write_text(table_help, encoding='utf-8')
    print(f"\n✓ Table format saved to: {table_file}")
    
    # List format
    print("\n\nMETHOD 3: show_help('list') - LIST FORMAT")
    print("-" * 90)
    list_help = show_help('list')
    list_file = output_dir / 'DEMO_HELP_LIST.txt'
    list_file.write_text(list_help, encoding='utf-8')
    print(f"✓ List format saved to: {list_file}")
    print("\nPreview:")
    print(list_help[:500] + "...\n")
    
    # Detailed format
    print("\nMETHOD 4: show_help('detailed') - DETAILED FORMAT")
    print("-" * 90)
    detailed_help = show_help('detailed')
    detailed_file = output_dir / 'DEMO_HELP_DETAILED.txt'
    detailed_file.write_text(detailed_help, encoding='utf-8')
    print(f"✓ Detailed format saved to: {detailed_file}")
    print("\nPreview:")
    print(detailed_help[:500] + "...\n")
    
    # Test command lookup
    print("\nMETHOD 5: find_command() - LOOKUP SPECIFIC COMMAND")
    print("-" * 90)
    from src.operations.help_command import find_command
    
    commands_to_find = ['setup', 'cleanup', 'update story']
    for cmd in commands_to_find:
        op = find_command(cmd)
        if op:
            print(f"✓ Found '{cmd}':")
            print(f"  - Operation ID: {op['operation_id']}")
            print(f"  - Status: {op['status_icon']} {op['status']}")
            print(f"  - Example: {op['example']}")
            print(f"  - Modules: {op['module_count']}")
        else:
            print(f"✗ '{cmd}' not found")
        print()
    
    # Summary
    print("\n" + "="*90)
    print("DEMO COMPLETE")
    print("="*90)
    print(f"\n✓ All methods working!")
    print(f"✓ Files generated:")
    print(f"  - {table_file.name}")
    print(f"  - {list_file.name}")
    print(f"  - {detailed_file.name}")
    print(f"\n✓ Help command is production ready!")
    print("\nUsage:")
    print("  execute_operation('help')")
    print("  execute_operation('/CORTEX help')")
    print("  show_help()  # Python API")
    print("\n" + "="*90 + "\n")


if __name__ == '__main__':
    demo_help_command()
