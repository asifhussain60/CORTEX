#!/usr/bin/env python3
"""
Remove slash commands from CORTEX architecture.

Decision: Natural language only for cleaner, more maintainable architecture.
Benefits: 
- Simpler mental model (one interaction method)
- Less documentation overhead
- More flexible and intuitive
- Already works perfectly

This script:
1. Removes slash_command fields from cortex-operations.yaml
2. Generates updated operations count report
3. Creates architectural decision record
"""

import yaml
from pathlib import Path
from datetime import datetime

def remove_slash_commands_from_yaml():
    """Remove slash_command fields from cortex-operations.yaml"""
    
    yaml_path = Path("cortex-operations.yaml")
    
    # Load YAML
    with open(yaml_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    # Track changes
    removed_count = 0
    operations_updated = []
    
    # Remove slash_command from each operation
    for op_name, op_data in data['operations'].items():
        if 'slash_command' in op_data:
            removed_slash = op_data.pop('slash_command')
            removed_count += 1
            operations_updated.append(f"  - {op_name}: removed '{removed_slash}'")
    
    # Save updated YAML
    with open(yaml_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    # Generate report
    report = f"""
SLASH COMMAND REMOVAL REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Operations Updated: {removed_count}
{chr(10).join(operations_updated)}

YAML Size Reduction:
- Before: {yaml_path.stat().st_size} bytes (with slash commands)
- Removed: ~{removed_count * 30} bytes (estimated)
- Fields removed: {removed_count}

Natural Language Examples (Still Work):
- "demo" → cortex_tutorial
- "setup environment" → environment_setup  
- "cleanup" → workspace_cleanup
- "generate documentation" → enterprise_documentation

Next Steps:
1. Update CORTEX.prompt.md (remove slash command sections)
2. Update help system (remove slash command column)
3. Simplify command registry (optional)
4. Update documentation to emphasize natural language

Architecture Decision: Natural language only ✅
"""
    
    print(report)
    
    # Save report
    report_path = Path("cortex-brain/cortex-2.0-design/SLASH-COMMAND-REMOVAL-REPORT.md")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✅ Updated {yaml_path}")
    print(f"✅ Report saved to {report_path}")
    
    return removed_count

def create_interaction_design_yaml():
    """Create interaction-design.yaml to replace slash-commands-guide.yaml"""
    
    interaction_design = {
        'interaction_design': {
            'philosophy': 'Natural language only - intuitive, flexible, maintainable',
            'decision_date': '2025-11-10',
            'rationale': [
                'Simpler mental model (one way to interact)',
                'More intuitive for all user levels',
                'Less documentation overhead',
                'Natural language already works perfectly',
                'Eliminates syntax errors',
                'Reduces maintenance burden'
            ],
            
            'natural_language_patterns': {
                'terse': {
                    'description': 'Single word commands (fast for power users)',
                    'examples': [
                        'setup',
                        'cleanup', 
                        'demo',
                        'help'
                    ]
                },
                'clear': {
                    'description': 'Clear intent phrases (recommended)',
                    'examples': [
                        'setup environment',
                        'clean workspace',
                        'show me what cortex can do',
                        'refresh cortex story'
                    ]
                },
                'conversational': {
                    'description': 'Natural conversation (most flexible)',
                    'examples': [
                        'I want to set up my environment',
                        'Can you clean up temporary files?',
                        'Show me how to use CORTEX',
                        'Let\'s plan a new feature'
                    ]
                }
            },
            
            'intent_detection': {
                'method': 'Semantic matching on natural_language field',
                'fallback': 'If no match, show help with suggestions',
                'confidence_threshold': 0.75,
                'fuzzy_matching': True
            },
            
            'command_discovery': {
                'primary': 'help command shows all operations',
                'search': 'Semantic search through operation descriptions',
                'suggestions': 'Context-aware based on project state',
                'examples': 'Every operation lists natural language examples'
            },
            
            'vs_code_extension': {
                'note': 'VS Code extension MAY use slash commands internally',
                'reason': 'UI conventions (e.g., /resume, /history)',
                'scope': 'Extension only, not core CORTEX',
                'documentation': 'Documented separately from main operations'
            },
            
            'migration_notes': {
                'removed': 'All slash_command fields from cortex-operations.yaml',
                'kept': 'All natural_language arrays (primary interaction method)',
                'impact': 'None - natural language already working',
                'documentation_cleanup': [
                    'CORTEX.prompt.md - remove slash command sections',
                    'Help system - remove slash command column',
                    'Technical docs - emphasize natural language only'
                ]
            }
        },
        
        'metadata': {
            'version': '2.0',
            'last_updated': '2025-11-10',
            'author': 'Asif Hussain',
            'replaces': 'slash-commands-guide.yaml (concept abandoned)',
            'architectural_decision': 'Natural language only interaction model'
        }
    }
    
    output_path = Path("cortex-brain/interaction-design.yaml")
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(interaction_design, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print(f"✅ Created {output_path}")

if __name__ == "__main__":
    print("="*70)
    print("CORTEX SLASH COMMAND REMOVAL")
    print("="*70)
    
    # Step 1: Remove slash commands from YAML
    removed = remove_slash_commands_from_yaml()
    
    # Step 2: Create interaction design YAML
    create_interaction_design_yaml()
    
    print("\n" + "="*70)
    print(f"COMPLETE: Removed {removed} slash commands")
    print("="*70)
    print("\nNext: Update CORTEX.prompt.md and help system")
