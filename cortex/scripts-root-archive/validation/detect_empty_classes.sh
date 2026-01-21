#!/bin/bash
# CORTEX Empty Class Detection Script
# Detects classes with only 'pass' statements
# Exit code 1 if empty classes found, 0 if clean

set -e

echo "🔍 Scanning for empty class implementations..."

# Find empty classes (class definition followed immediately by pass)
# Using Python to parse properly
EMPTY_CLASSES=$(python3 -c "
import re
import os
import sys

empty_classes = []
for root, dirs, files in os.walk('cortex'):
    # Skip pycache
    dirs[:] = [d for d in dirs if d != '__pycache__']
    
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Find class definitions followed only by pass
                pattern = r'class\s+(\w+).*?:\s*\n\s*pass\s*\n'
                matches = re.finditer(pattern, content, re.MULTILINE)
                
                for match in matches:
                    # Check if not explicitly allowed
                    if '# pragma: stub-allowed' not in content[max(0, match.start()-100):match.end()+20]:
                        line_num = content[:match.start()].count('\n') + 1
                        empty_classes.append(f'{filepath}:{line_num}: {match.group(1)}')
            except Exception as e:
                continue

for ec in empty_classes:
    print(ec)
" 2>/dev/null)

if [ ! -z "$EMPTY_CLASSES" ]; then
    echo "❌ EMPTY CLASSES DETECTED:"
    echo ""
    echo "$EMPTY_CLASSES"
    echo ""
    echo "⚠️  Empty classes are not allowed. Add proper implementation or mark with:"
    echo "    # pragma: stub-allowed"
    echo ""
    exit 1
fi

echo "✅ No empty classes detected"
exit 0
