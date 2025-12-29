"""
Generate professional documentation from CORTEX knowledge guidelines (YAML) for Git Pages
"""
import yaml
from pathlib import Path
from typing import Dict, Any, List


def convert_clean_code_to_md(yaml_data: Dict[str, Any]) -> str:
    """Convert clean code YAML to professional markdown"""
    md_lines = []
    
    # Header
    meta = yaml_data.get('metadata', {})
    md_lines.extend([
        f"# {meta.get('title', 'Clean Code Principles')}",
        "",
        f"**Author:** {meta.get('author', 'Unknown')}",
        f"**Source:** {meta.get('source', 'N/A')}",
        f"**Version:** {meta.get('version', '1.0')} | **Updated:** {meta.get('updated', 'N/A')}",
        "",
        "---",
        "",
        "## Overview",
        "",
        "This guide provides authoritative clean code principles for AI-powered code generation, review, and refactoring.",
        "",
        "---",
        ""
    ])
    
    # Naming Conventions
    naming = yaml_data.get('naming_conventions', {})
    if naming:
        md_lines.extend([
            "## 1. Meaningful Names",
            "",
            f"**Principle:** {naming.get('principle', 'N/A')}",
            "",
            f"**Importance:** {naming.get('importance', 'N/A')}",
            "",
            "### Rules",
            ""
        ])
        
        for rule in naming.get('rules', []):
            md_lines.extend([
                f"#### {rule.get('id', 'N/A').upper()}: {rule.get('name', 'Unnamed')}",
                "",
                f"**Description:** {rule.get('description', 'No description')}",
                "",
                f"**Severity:** `{rule.get('severity', 'MEDIUM')}`",
                ""
            ])
            
            # Examples
            examples = rule.get('examples', {})
            if examples.get('good'):
                md_lines.append("✅ **Good Examples:**\n")
                for ex in examples['good']:
                    lang = ex.get('language', 'python')
                    md_lines.extend([
                        f"```{lang}",
                        ex.get('code', '').strip(),
                        "```",
                        f"*{ex.get('explanation', '')}*",
                        ""
                    ])
            
            if examples.get('bad'):
                md_lines.append("❌ **Bad Examples:**\n")
                for ex in examples['bad']:
                    lang = ex.get('language', 'python')
                    md_lines.extend([
                        f"```{lang}",
                        ex.get('code', '').strip(),
                        "```",
                        f"*{ex.get('explanation', '')}*",
                        ""
                    ])
            
            md_lines.append("---\n")
    
    # Functions section
    functions = yaml_data.get('functions', {})
    if functions:
        md_lines.extend([
            "## 2. Functions",
            "",
            f"**Principle:** {functions.get('principle', 'N/A')}",
            "",
            "### Rules",
            ""
        ])
        
        for rule in functions.get('rules', []):
            md_lines.extend([
                f"#### {rule.get('id', 'N/A').upper()}: {rule.get('name', 'Unnamed')}",
                "",
                f"**Description:** {rule.get('description', 'No description')}",
                "",
                f"**Severity:** `{rule.get('severity', 'MEDIUM')}`",
                ""
            ])
            
            if rule.get('rationale'):
                md_lines.extend([
                    f"**Rationale:** {rule['rationale']}",
                    ""
                ])
            
            # Examples
            examples = rule.get('examples', {})
            if examples.get('good'):
                md_lines.append("✅ **Good Examples:**\n")
                for ex in examples['good']:
                    lang = ex.get('language', 'python')
                    md_lines.extend([
                        f"```{lang}",
                        ex.get('code', '').strip(),
                        "```",
                        f"*{ex.get('explanation', '')}*",
                        ""
                    ])
            
            md_lines.append("---\n")
    
    return '\n'.join(md_lines)


def convert_code_review_to_md(yaml_data: Dict[str, Any]) -> str:
    """Convert code review YAML to professional markdown"""
    md_lines = []
    
    # Header
    meta = yaml_data.get('metadata', {})
    md_lines.extend([
        f"# {meta.get('name', 'Code Review Guidelines')}",
        "",
        f"**Version:** {meta.get('version', '1.0')} | **Author:** {meta.get('author', 'Unknown')}",
        f"**Source:** {meta.get('source', 'N/A')}",
        "",
        f"**Description:** {meta.get('description', 'N/A')}",
        "",
        "---",
        "",
        "## Security Review",
        ""
    ])
    
    # Security Review
    for item in yaml_data.get('security_review', []):
        md_lines.extend([
            f"### {item.get('id', 'N/A').upper()}: {item.get('name', 'Unnamed')}",
            "",
            f"**Severity:** `{item.get('severity', 'MEDIUM')}` | **Category:** `{item.get('category', 'N/A')}`",
            "",
            f"**Description:** {item.get('description', 'No description')}",
            "",
            "#### Checklist",
            ""
        ])
        
        for check in item.get('checklist', []):
            md_lines.append(f"- [ ] {check}")
        
        md_lines.append("")
        
        # Detection rules
        if 'detection_rules' in item:
            rules = item['detection_rules']
            md_lines.append("#### Detection Rules\n")
            
            if rules.get('patterns'):
                md_lines.append("**Patterns to detect:**\n")
                for pattern in rules['patterns']:
                    md_lines.append(f"- `{pattern}`")
                md_lines.append("")
            
            if rules.get('tools'):
                md_lines.append("**Recommended tools:**\n")
                for tool in rules['tools']:
                    md_lines.append(f"- **{tool.get('name')}:** `{tool.get('command')}`")
                md_lines.append("")
        
        # Examples
        if item.get('example_bad'):
            md_lines.extend([
                "❌ **Bad Example:**",
                "```python",
                item['example_bad'].strip(),
                "```",
                ""
            ])
        
        if item.get('example_good'):
            md_lines.extend([
                "✅ **Good Example:**",
                "```python",
                item['example_good'].strip(),
                "```",
                ""
            ])
        
        md_lines.append("---\n")
    
    # Code Quality Review
    md_lines.append("## Code Quality Review\n")
    for item in yaml_data.get('code_quality', []):
        md_lines.extend([
            f"### {item.get('id', 'N/A').upper()}: {item.get('name', 'Unnamed')}",
            "",
            f"**Severity:** `{item.get('severity', 'MEDIUM')}` | **Category:** `{item.get('category', 'N/A')}`",
            "",
            f"**Description:** {item.get('description', 'No description')}",
            "",
            "#### Checklist",
            ""
        ])
        
        for check in item.get('checklist', []):
            md_lines.append(f"- [ ] {check}")
        
        md_lines.append("\n---\n")
    
    return '\n'.join(md_lines)


def main():
    """Generate knowledge documentation"""
    print("🎯 Generating Knowledge Guidelines Documentation for Git Pages")
    
    knowledge_dir = Path("cortex-brain/knowledge/engineering")
    output_dir = Path("docs/knowledge/engineering")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    files_processed = 0
    
    # Process each YAML file
    for yaml_file in knowledge_dir.glob("*.yaml"):
        print(f"📄 Processing: {yaml_file.name}")
        
        with open(yaml_file, 'r', encoding='utf-8') as f:
            yaml_data = yaml.safe_load(f)
        
        # Determine conversion function
        if 'clean-code' in yaml_file.name:
            md_content = convert_clean_code_to_md(yaml_data)
            output_file = output_dir / "clean-code.md"
        elif 'code-review' in yaml_file.name:
            md_content = convert_code_review_to_md(yaml_data)
            output_file = output_dir / "code-review.md"
        elif 'refactoring' in yaml_file.name:
            # Placeholder for refactoring guidelines
            output_file = output_dir / "refactoring.md"
            md_content = f"# Refactoring Guidelines\n\n*(Documentation pending)*"
        else:
            print(f"  ⚠️ Skipped: Unknown guideline type")
            continue
        
        # Write markdown file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"  ✅ Generated: {output_file}")
        files_processed += 1
    
    print(f"\n✅ Processed {files_processed} knowledge guidelines")
    print(f"📁 Output directory: {output_dir}")


if __name__ == "__main__":
    main()
