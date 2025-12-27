#!/usr/bin/env python3
import re
from pathlib import Path

files = [
    'docs/features/orchestrators.html',
    'docs/technical/orchestrators/index.html'
]

for file_path in files:
    path = Path(file_path)
    content = path.read_text(encoding='utf-8')
    original = content
    
    # Remove style attributes except those in D3.js template literals
    # Look for style=" outside of ${...} contexts
    lines = content.split('\n')
    new_lines = []
    
    for line in lines:
        # Skip lines with D3.js template literal variables
        if '${d.' in line or '${orchestrator.' in line:
            new_lines.append(line)
        else:
            # Remove style attributes from this line
            line = re.sub(r'\s+style="[^"]*"', '', line)
            new_lines.append(line)
    
    content = '\n'.join(new_lines)
    
    if content != original:
        changes = original.count('style="') - content.count('style="')
        path.write_text(content, encoding='utf-8')
        print(f'✅ {path.name}: {changes} inline styles removed')
    else:
        print(f'ℹ️  {path.name}: No changes needed')
