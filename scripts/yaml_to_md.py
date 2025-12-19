#!/usr/bin/env python3
"""
YAML to Markdown Converter for Knowledge Guidelines
Converts machine-readable YAML guidelines to human-readable Markdown documentation

Usage:
    python scripts/yaml_to_md.py cortex-brain/knowledge/engineering/clean-code.yaml
    python scripts/yaml_to_md.py --all  # Convert all YAML files
"""

import sys
import yaml
from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime


def convert_clean_code_yaml_to_md(yaml_data: Dict[str, Any], output_path: Path) -> None:
    """Convert clean-code.yaml to Markdown"""
    
    md_lines = []
    
    # Header
    metadata = yaml_data.get('metadata', {})
    md_lines.extend([
        f"# {metadata.get('name', 'Clean Code Guidelines')}",
        "",
        f"**Version:** {metadata.get('version', '1.0')} | **Source:** Machine-generated from `clean-code.yaml`",
        f"**Created:** {metadata.get('created', 'N/A')} | **Updated:** {metadata.get('updated', 'N/A')}",
        "",
        f"{metadata.get('description', '')}",
        "",
        "---",
        ""
    ])
    
    # Table of Contents
    md_lines.extend([
        "## Table of Contents",
        "",
        "1. [Naming Conventions](#naming-conventions)",
        "2. [Function Design](#function-design)",
        "3. [Error Handling](#error-handling)",
        "4. [Commenting](#commenting)",
        "5. [Formatting](#formatting)",
        "6. [SOLID Principles](#solid-principles)",
        "7. [Code Smells](#code-smells)",
        "8. [Automation](#automation)",
        "9. [Metrics](#metrics)",
        "10. [CORTEX Integration](#cortex-integration)",
        "",
        "---",
        ""
    ])
    
    # Naming Conventions
    md_lines.append("## Naming Conventions\n")
    for rule in yaml_data.get('naming_conventions', []):
        md_lines.extend([
            f"### {rule['id']}: {rule['name']}",
            "",
            f"**Severity:** {rule['severity']} | **Category:** {rule['category']}",
            "",
            f"{rule['description']}",
            ""
        ])
        
        if 'example_bad' in rule:
            md_lines.extend([
                "**❌ Bad:**",
                "```python",
                rule['example_bad'].strip(),
                "```",
                ""
            ])
        
        if 'example_good' in rule:
            md_lines.extend([
                "**✅ Good:**",
                "```python",
                rule['example_good'].strip(),
                "```",
                ""
            ])
        
        md_lines.append("---\n")
    
    # Function Design
    md_lines.append("## Function Design\n")
    for rule in yaml_data.get('function_design', []):
        md_lines.extend([
            f"### {rule['id']}: {rule['name']}",
            "",
            f"**Severity:** {rule['severity']} | **Category:** {rule['category']}",
            "",
            f"{rule['description']}",
            ""
        ])
        
        if 'rationale' in rule:
            md_lines.extend([
                f"**Rationale:** {rule['rationale']}",
                ""
            ])
        
        if 'example_bad' in rule:
            md_lines.extend([
                "**❌ Bad:**",
                "```python",
                rule['example_bad'].strip(),
                "```",
                ""
            ])
        
        if 'example_good' in rule:
            md_lines.extend([
                "**✅ Good:**",
                "```python",
                rule['example_good'].strip(),
                "```",
                ""
            ])
        
        md_lines.append("---\n")
    
    # Error Handling
    md_lines.append("## Error Handling\n")
    for rule in yaml_data.get('error_handling', []):
        md_lines.extend([
            f"### {rule['id']}: {rule['name']}",
            "",
            f"**Severity:** {rule['severity']} | **Category:** {rule['category']}",
            "",
            f"{rule['description']}",
            ""
        ])
        
        if 'example_bad' in rule:
            md_lines.extend([
                "**❌ Bad:**",
                "```python",
                rule['example_bad'].strip(),
                "```",
                ""
            ])
        
        if 'example_good' in rule:
            md_lines.extend([
                "**✅ Good:**",
                "```python",
                rule['example_good'].strip(),
                "```",
                ""
            ])
        
        md_lines.append("---\n")
    
    # Commenting
    md_lines.append("## Commenting\n")
    for rule in yaml_data.get('commenting', []):
        md_lines.extend([
            f"### {rule['id']}: {rule['name']}",
            "",
            f"**Severity:** {rule['severity']} | **Category:** {rule['category']}",
            "",
            f"{rule['description']}",
            ""
        ])
        
        if 'good_comments' in rule:
            md_lines.extend([
                "**Good Comments:**",
                ""
            ])
            for comment_type in rule['good_comments']:
                md_lines.append(f"- {comment_type}")
            md_lines.append("")
        
        if 'bad_comments' in rule:
            md_lines.extend([
                "**Bad Comments:**",
                ""
            ])
            for comment_type in rule['bad_comments']:
                md_lines.append(f"- {comment_type}")
            md_lines.append("")
        
        md_lines.append("---\n")
    
    # Formatting
    md_lines.append("## Formatting\n")
    for rule in yaml_data.get('formatting', []):
        md_lines.extend([
            f"### {rule['id']}: {rule['name']}",
            "",
            f"**Severity:** {rule['severity']} | **Category:** {rule['category']}",
            "",
            f"{rule['description']}",
            ""
        ])
        
        if 'rules' in rule:
            for sub_rule in rule['rules']:
                md_lines.append(f"- {sub_rule}")
            md_lines.append("")
        
        md_lines.append("---\n")
    
    # SOLID Principles
    md_lines.extend([
        "## SOLID Principles",
        "",
        "Integration examples showing how clean code principles align with SOLID:",
        ""
    ])
    
    for principle in yaml_data.get('solid_principles', []):
        md_lines.extend([
            f"### {principle['principle']}",
            "",
            f"{principle['clean_code_connection']}",
            "",
            f"**Example:** {principle['example']}",
            "",
            "---",
            ""
        ])
    
    # Code Smells
    md_lines.extend([
        "## Code Smells",
        "",
        "Detection mappings for common code smells:",
        ""
    ])
    
    for smell in yaml_data.get('code_smells', []):
        md_lines.extend([
            f"### {smell['smell']}",
            "",
            f"**Clean Code Rules Violated:** {', '.join(smell['violated_rules'])}",
            "",
            f"**Detection Pattern:** `{smell['detection_pattern']}`",
            "",
            "---",
            ""
        ])
    
    # Automation
    md_lines.extend([
        "## Automation",
        "",
        "Automated tools for enforcing clean code guidelines:",
        ""
    ])
    
    automation = yaml_data.get('automation', {})
    for lang, tools in automation.items():
        if isinstance(tools, list):
            md_lines.extend([
                f"### {lang.title()}",
                ""
            ])
            for tool in tools:
                md_lines.extend([
                    f"#### {tool['name']}",
                    "",
                    f"{tool['description']}",
                    "",
                    "**Detects:**"
                ])
                for detect in tool['detects']:
                    md_lines.append(f"- {detect}")
                md_lines.extend(["", "---", ""])
    
    # Metrics
    md_lines.extend([
        "## Metrics",
        "",
        "Recommended thresholds for code quality metrics:",
        ""
    ])
    
    metrics = yaml_data.get('metrics', {})
    for metric_name, thresholds in metrics.items():
        if isinstance(thresholds, dict):
            md_lines.extend([
                f"### {metric_name.replace('_', ' ').title()}",
                ""
            ])
            for level, value in thresholds.items():
                md_lines.append(f"- **{level.title()}:** {value}")
            md_lines.extend(["", "---", ""])
    
    # CORTEX Integration
    md_lines.extend([
        "## CORTEX Integration",
        "",
        "How CORTEX agents use these guidelines:",
        ""
    ])
    
    integration = yaml_data.get('cortex_integration', {})
    for agent, capabilities in integration.items():
        md_lines.extend([
            f"### {agent.replace('_', ' ').title()}",
            "",
            f"{capabilities}",
            "",
            "---",
            ""
        ])
    
    # Footer
    md_lines.extend([
        "",
        "---",
        "",
        f"**Generated:** {datetime.now().strftime('%B %d, %Y at %H:%M')}",
        f"**Source:** `clean-code.yaml`",
        "",
        "*This document is auto-generated from machine-readable YAML. Do not edit manually.*"
    ])
    
    # Write to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text('\n'.join(md_lines), encoding='utf-8')
    print(f"✅ Generated: {output_path}")


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python yaml_to_md.py <yaml_file>")
        sys.exit(1)
    
    yaml_file = Path(sys.argv[1])
    
    if not yaml_file.exists():
        print(f"❌ File not found: {yaml_file}")
        sys.exit(1)
    
    # Load YAML
    with open(yaml_file, 'r', encoding='utf-8') as f:
        yaml_data = yaml.safe_load(f)
    
    # Determine output path
    if 'clean-code' in yaml_file.name:
        output_path = Path("docs/guidelines/engineering/clean-code.md")
        convert_clean_code_yaml_to_md(yaml_data, output_path)
    else:
        print(f"⚠️  Converter not yet implemented for: {yaml_file.name}")
        print("    Only clean-code.yaml is currently supported")


if __name__ == "__main__":
    main()
