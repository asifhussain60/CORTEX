#!/usr/bin/env python3
"""Fix response template headers - remove decorative lines, keep simple prominent headers."""

import re

# Read the file
with open('d:\\PROJECTS\\CORTEX\\cortex-brain\\response-templates.yaml', 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern 1: Full header with three lines of decorative characters
pattern1 = (
    r'━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n'
    r'      🎯 CORTEX ([^\n]+)\n'
    r'      ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n'
    r'      Author: Asif Hussain \| © 2024-2025 \| github\.com/asifhussain60/CORTEX\n'
    r'      ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
)

replacement1 = (
    r'🎯 **CORTEX \1**\n'
    r'      Author: Asif Hussain | © 2024-2025 | github.com/asifhussain60/CORTEX'
)

# Apply replacement
new_content = re.sub(pattern1, replacement1, content)

# Pattern 2: Also remove standalone decorative line separators in content
pattern2 = r'      ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n      \n'
replacement2 = '\n'

new_content = re.sub(pattern2, replacement2, new_content)

# Write back
with open('d:\\PROJECTS\\CORTEX\\cortex-brain\\response-templates.yaml', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ Fixed all response template headers!")
print(f"   Removed decorative lines, keeping simple prominent headers")
