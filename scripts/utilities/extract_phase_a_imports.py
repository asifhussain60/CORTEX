#!/usr/bin/env python3
"""Extract Phase A imports (cortex/ and scripts/)"""
import os
import re
from collections import defaultdict

src_imports = defaultdict(list)

# Search cortex/ and scripts/
for root in ['cortex', 'scripts']:
    if not os.path.exists(root):
        continue
    for dirpath, dirnames, filenames in os.walk(root):
        for filename in filenames:
            if filename.endswith('.py'):
                filepath = os.path.join(dirpath, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        for lineno, line in enumerate(f, 1):
                            if re.match(r'^\s*(from src\.|import src)', line):
                                key = line.strip()
                                src_imports[key].append(f"{filepath}:{lineno}")
                except Exception as e:
                    pass

print("=" * 80)
print("PHASE A IMPORTS (cortex/ and scripts/)")
print("=" * 80)
print()

for imp in sorted(src_imports.keys()):
    print(f"IMPORT: {imp}")
    for loc in src_imports[imp]:
        print(f"  Location: {loc}")
    print()

print(f"\nTotal unique imports: {len(src_imports)}")
print(f"Total import locations: {sum(len(v) for v in src_imports.values())}")
