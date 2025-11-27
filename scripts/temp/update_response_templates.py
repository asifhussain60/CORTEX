"""
Update Response Templates to New Standard Format

Converts all templates from old format to new unified format:
- Changes header from "🧠 **CORTEX [Operation Type]**" to "# CORTEX [Title]"
- Updates author line to "**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX"
- Adds horizontal rule separator
- Converts section emojis to ## markdown headers
- Removes copyright since site is public

Author: Asif Hussain
"""

import yaml
import re
from pathlib import Path

def convert_old_to_new_format(content: str, title: str = "Operation") -> str:
    """
    Convert old template format to new standard format.
    
    Args:
        content: Old template content
        title: Title for the template (extracted from template name)
    
    Returns:
        New format template content
    """
    # Remove unicode emoji encoding and convert to markdown
    content = content.replace("\\U0001F9E0", "")  # Remove brain emoji code
    content = content.replace("\\U0001F3AF", "")  # Remove dart emoji code
    content = content.replace("\\U0001F4AC", "")  # Remove speech emoji code
    content = content.replace("\\U0001F4DD", "")  # Remove pencil emoji code
    content = content.replace("\\U0001F50D", "")  # Remove magnifying glass emoji code
    content = content.replace("⚠️", "")  # Remove warning emoji
    
    # Convert old header format
    content = re.sub(
        r'\*\*CORTEX.*?\*\*\nAuthor: Asif Hussain \| © 2024-2025 \| github\.com/asifhussain60/CORTEX',
        f'# CORTEX {title}\n**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX\n\n---',
        content
    )
    
    # Convert section headers from emoji + bold to ## headers
    content = re.sub(r'\*\*My Understanding Of Your Request:\*\*', '## My Understanding Of Your Request', content)
    content = re.sub(r'\*\*Challenge:\*\*', '## Challenge', content)
    content = re.sub(r'\*\*Response:\*\*', '## Response', content)
    content = re.sub(r'\*\*Your Request:\*\*', '## Your Request', content)
    content = re.sub(r'\*\*Next Steps:\*\*', '## Next Steps', content)
    
    # Clean up extra whitespace
    content = re.sub(r'\n\s+\n', '\n\n', content)
    content = re.sub(r'\n\s+([^\s])', r'\n\1', content)
    
    return content.strip()

def update_templates_file():
    """Update response-templates.yaml with new format."""
    templates_path = Path(__file__).parent / 'cortex-brain' / 'response-templates.yaml'
    
    # Read current templates
    with open(templates_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    # Update schema version
    data['schema_version'] = '3.0'
    data['last_updated'] = '2025-11-26'
    
    # Update shared header
    data['shared'] = {
        'standard_header': (
            "# CORTEX {title}\n"
            "**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX\n"
            "\n"
            "---\n"
        )
    }
    
    # Update each template
    for template_key, template_data in data.get('templates', {}).items():
        if 'content' in template_data and isinstance(template_data['content'], str):
            # Get title from template name
            title = template_data.get('name', template_key.replace('_', ' ').title())
            
            # Convert content
            old_content = template_data['content']
            new_content = convert_old_to_new_format(old_content, title)
            
            # Make it a proper multi-line YAML string
            if '\n' in new_content:
                template_data['content'] = new_content
            
            print(f"Updated template: {template_key}")
    
    # Write updated templates
    with open(templates_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=120)
    
    print(f"\n✅ Updated {len(data.get('templates', {}))} templates")
    print(f"📁 File: {templates_path}")

if __name__ == '__main__':
    update_templates_file()
