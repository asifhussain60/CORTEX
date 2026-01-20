#!/usr/bin/env python3
"""Extract Phase B imports (tests/)"""
import os
import re
from collections import defaultdict

src_imports = defaultdict(list)

# Search tests/ only
if os.path.exists('tests'):
    for dirpath, dirnames, filenames in os.walk('tests'):
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
print("PHASE B IMPORTS (tests/)")
print("=" * 80)
print()

# Get unique modules
unique_modules = set()
for imp in src_imports.keys():
    match = re.search(r'from (src\.[a-z_]+(\.[a-z_]+)*)', imp)
    if match:
        unique_modules.add(match.group(1))

print(f"Unique src.* modules found: {len(unique_modules)}")
print()

for module in sorted(unique_modules):
    print(f"Module: {module}")

print()
print(f"Total unique imports: {len(src_imports)}")
print(f"Total import locations: {sum(len(v) for v in src_imports.values())}")
print()

# Count by file
files_with_imports = defaultdict(int)
for locations in src_imports.values():
    for loc in locations:
        file_path = loc.split(':')[0]
        files_with_imports[file_path] += 1

print(f"Files with imports: {len(files_with_imports)}")
print()

# Show top 20 files
for filepath, count in sorted(files_with_imports.items(), key=lambda x: -x[1])[:20]:
    print(f"  {count:3d} → {filepath}")

if len(files_with_imports) > 20:
    print(f"  ... and {len(files_with_imports) - 20} more files")
