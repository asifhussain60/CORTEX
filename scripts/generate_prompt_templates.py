"""
Generate CORTEX.prompt.md template selection section from response-templates.yaml

This script bridges the gap between Python template system and GitHub Copilot AI.
It reads structured templates from YAML and generates AI-readable instructions
that Copilot can understand and follow.

Architecture:
    YAML Templates (single source of truth)
        ↓
    This Generator Script
        ↓
    AI-Readable Instructions in CORTEX.prompt.md
        ↓
    GitHub Copilot Execution

Usage:
    python scripts/generate_prompt_templates.py
    
Output:
    Updates CORTEX.prompt.md with embedded template selection logic

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import yaml
from pathlib import Path
import sys
from datetime import datetime


def load_templates():
    """Load templates from response-templates.yaml"""
    template_file = Path("cortex-brain/templates/response-templates.yaml")
    
    if not template_file.exists():
        print(f"❌ Error: {template_file} not found")
        sys.exit(1)
    
    try:
        with open(template_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            return data
    except Exception as e:
        print(f"❌ Error loading templates: {e}")
        sys.exit(1)


def format_template_content(content, max_lines=20):
    """Format template content for display in prompt file"""
    lines = content.split('\n')
    
    # Keep first max_lines lines
    if len(lines) > max_lines:
        preview_lines = lines[:max_lines]
        preview_lines.append("   ...")
        preview_lines.append("   [Additional sections follow same structure]")
        return '\n'.join(preview_lines)
    
    return content


def generate_template_section(templates_data):
    """Generate markdown section for CORTEX.prompt.md"""
    
    lines = [
        "# 🎯 CRITICAL: Template Trigger Detection & Selection",
        "",
        "**AUTO-GENERATED FROM response-templates.yaml**",
        f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "**BEFORE responding to ANY user request:**",
        "",
        "1. **Check user message for template triggers** (exact match or fuzzy match)",
        "2. **Select appropriate template** based on trigger match",
        "3. **Apply template format** with context substitution",
        "4. **If no trigger matches:** Use fallback template",
        "",
        "---",
        "",
        "## 📋 Template Trigger Mappings",
        ""
    ]
    
    templates = templates_data.get('templates', {})
    
    # Sort templates: specific triggers first, fallback last
    sorted_templates = sorted(
        templates.items(),
        key=lambda x: (x[0] == 'fallback', x[0])  # fallback last, rest alphabetical
    )
    
    for template_id, config in sorted_templates:
        triggers = config.get('trigger', [])
        
        # Skip fallback for now (handle at end)
        if template_id == 'fallback':
            continue
        
        # Skip templates with no triggers (confidence indicators, etc.)
        if not triggers:
            continue
        
        name = config.get('name', template_id.replace('_', ' ').title())
        response_type = config.get('response_type', 'structured')
        content = config.get('content', '')
        
        lines.append(f"### {name}")
        lines.append("")
        lines.append(f"**Template ID:** `{template_id}`  ")
        lines.append(f"**Response Type:** `{response_type}`  ")
        
        # Format triggers
        if len(triggers) == 1:
            lines.append(f"**Trigger:** `{triggers[0]}`")
        else:
            lines.append("**Triggers:**")
            for trigger in triggers:
                lines.append(f"- `{trigger}`")
        
        lines.append("")
        lines.append("**Format to use:**")
        lines.append("```markdown")
        lines.append(format_template_content(content))
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")
    
    # Add fallback template last
    if 'fallback' in templates:
        fallback = templates['fallback']
        lines.append("### Fallback Response (No Trigger Match)")
        lines.append("")
        lines.append("**Template ID:** `fallback`  ")
        lines.append("**When to use:** No specific trigger detected  ")
        lines.append("")
        lines.append("**Format to use:**")
        lines.append("```markdown")
        lines.append(format_template_content(fallback.get('content', '')))
        lines.append("```")
        lines.append("")
    
    # Add routing instructions
    lines.extend([
        "---",
        "",
        "## 🎯 Template Selection Algorithm (For AI)",
        "",
        "```",
        "1. Extract key phrases from user message",
        "2. Check each template's triggers (case-insensitive)",
        "3. If exact match found → Use that template",
        "4. If fuzzy match found (70%+ similarity) → Use that template",
        "5. If TDD keywords (implement/add/create) → Check if critical feature → Use TDD template",
        "6. If planning keywords (plan/let's plan) → Use planning template",
        "7. If no match → Use fallback template",
        "```",
        "",
        "**Priority Order:**",
        "1. Exact trigger match (highest priority)",
        "2. TDD workflow detection (critical features)",
        "3. Planning workflow detection",
        "4. Documentation generation",
        "5. Fuzzy trigger match (70%+ similarity)",
        "6. Fallback (lowest priority)",
        "",
    ])
    
    return '\n'.join(lines)


def update_cortex_prompt():
    """Update CORTEX.prompt.md with generated template section"""
    
    print("📖 Loading templates from response-templates.yaml...")
    templates = load_templates()
    
    template_count = len([t for t in templates.get('templates', {}).keys() if t != 'fallback'])
    print(f"✅ Loaded {template_count} templates (+ 1 fallback)")
    
    print("🔄 Generating AI-readable template section...")
    template_section = generate_template_section(templates)
    
    # Read current prompt file
    prompt_file = Path(".github/prompts/CORTEX.prompt.md")
    
    if not prompt_file.exists():
        print(f"❌ Error: {prompt_file} not found")
        sys.exit(1)
    
    print(f"📄 Reading {prompt_file}...")
    content = prompt_file.read_text(encoding='utf-8')
    
    # Find section markers
    marker_start = "# 🎯 CRITICAL: Template Trigger Detection"
    marker_end = "## 🧠 Contextual Intelligence (Architecture Utilization)"
    
    if marker_start not in content:
        print(f"⚠️ Warning: Start marker not found. Adding template section at beginning...")
        new_content = template_section + "\n\n" + content
    elif marker_end not in content:
        print(f"⚠️ Warning: End marker not found. Appending template section...")
        new_content = content + "\n\n" + template_section
    else:
        # Replace section between markers
        before = content.split(marker_start)[0]
        after_parts = content.split(marker_end)
        after = marker_end + after_parts[1] if len(after_parts) > 1 else ""
        
        new_content = before + template_section + "\n\n" + after
    
    # Write updated content
    print(f"💾 Writing updated prompt file...")
    prompt_file.write_text(new_content, encoding='utf-8')
    
    print(f"✅ Successfully updated {prompt_file}")
    print(f"📊 Generated {len(template_section.split('###')) - 1} template mappings")
    print(f"📏 Added {len(template_section.split(chr(10)))} lines to prompt file")
    print("")
    print("🎯 Next Steps:")
    print("   1. Review the updated CORTEX.prompt.md")
    print("   2. Test with GitHub Copilot: 'help', 'plan feature', 'export brain'")
    print("   3. Verify template selection works correctly")


def main():
    """Main entry point"""
    print("=" * 70)
    print("🧠 CORTEX Template-to-Prompt Generator")
    print("=" * 70)
    print("")
    
    try:
        update_cortex_prompt()
        print("")
        print("=" * 70)
        print("✅ SUCCESS - Template system now integrated with GitHub Copilot")
        print("=" * 70)
        return 0
    except Exception as e:
        print("")
        print("=" * 70)
        print(f"❌ ERROR: {e}")
        print("=" * 70)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
