"""
Script to fix response template formatting issues
Addresses Gap #7 and #8:
- Gap #7: Title too small (**CORTEX** → # 🧠 CORTEX)
- Gap #8: Confusing Challenge wording

Usage:
    python fix_templates.py
"""

import yaml
from pathlib import Path
import re


def fix_template_formatting(templates_path: Path) -> None:
    """
    Fix formatting issues in response templates.
    
    Changes:
    1. **CORTEX [Operation Type]** → # 🧠 CORTEX [Operation Type]
    2. Challenge: [✓ Accept... OR ⚡ Challenge...] → Challenge: [Specific challenge or "None"]
    """
    print(f"Loading templates from {templates_path}...")
    
    with open(templates_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    templates = data.get('templates', {})
    fixed_count = 0
    
    for template_id, template in templates.items():
        if 'content' not in template:
            continue
        
        content = template['content']
        original_content = content
        
        # Fix #1: Change bold title to H1 heading
        content = re.sub(
            r'🧠 \*\*CORTEX \[Operation Type\]\*\*',
            r'# 🧠 CORTEX [Operation Type]',
            content
        )
        
        # Fix #2: Simplify Challenge field
        # Old: ⚠️ **Challenge:** [✓ Accept with rationale OR ⚡ Challenge with alternatives]
        # New: ⚠️ **Challenge:** [Specific challenge or "None"]
        content = re.sub(
            r'⚠️ \*\*Challenge:\*\* \[✓ Accept with rationale OR ⚡ Challenge with alternatives\]',
            r'⚠️ **Challenge:** [Specific challenge or "None"]',
            content
        )
        
        if content != original_content:
            template['content'] = content
            fixed_count += 1
            print(f"  Fixed template: {template_id}")
    
    # Update last_updated timestamp
    from datetime import datetime
    data['last_updated'] = datetime.now().strftime('%Y-%m-%d')
    
    # Save back to file
    print(f"\nSaving {fixed_count} fixed templates...")
    with open(templates_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print(f"✅ Successfully fixed {fixed_count} templates!")
    print(f"\nChanges made:")
    print(f"  1. Title format: **CORTEX** → # 🧠 CORTEX (H1 heading)")
    print(f"  2. Challenge field: Simplified to [Specific challenge or 'None']")


def main():
    # Determine CORTEX root
    script_dir = Path(__file__).parent
    
    # Try common paths
    possible_paths = [
        script_dir.parent / "cortex-brain" / "response-templates.yaml",
        script_dir / "cortex-brain" / "response-templates.yaml",
        Path(__file__).resolve().parent.parent / "cortex-brain" / "response-templates.yaml",
    ]
    
    templates_path = None
    for path in possible_paths:
        if path.exists():
            templates_path = path
            break
    
    if not templates_path:
        print("❌ Error: Could not find response-templates.yaml")
        print(f"Searched paths:")
        for path in possible_paths:
            print(f"  - {path}")
        return
    
    fix_template_formatting(templates_path)


if __name__ == "__main__":
    main()
