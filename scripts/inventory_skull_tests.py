"""Inventory SKULL-related tests"""
import os
import re
from pathlib import Path
from collections import defaultdict

test_root = Path('tests')
skull_related = []

# Search for files containing SKULL or brain protection references
for test_file in test_root.rglob('*.py'):
    try:
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if re.search(r'skull|SKULL|brain.?protection|BrainProtection', content, re.IGNORECASE):
                # Extract test function names
                test_funcs = re.findall(r'def (test_\w+)', content)
                skull_related.append({
                    'file': str(test_file.relative_to(test_root)),
                    'test_count': len(test_funcs),
                    'tests': test_funcs
                })
    except Exception as e:
        pass

print(f"🧪 SKULL-Related Test Files Found: {len(skull_related)}\n")
print("="*80)

for item in skull_related:
    print(f"\n📁 {item['file']}")
    print(f"   Tests: {item['test_count']}")
    if item['tests']:
        for test in item['tests'][:5]:  # Show first 5
            print(f"      - {test}")
        if len(item['tests']) > 5:
            print(f"      ... and {len(item['tests']) - 5} more")

total_tests = sum(item['test_count'] for item in skull_related)
print(f"\n{'='*80}")
print(f"📊 Total SKULL-related test functions: {total_tests}")
