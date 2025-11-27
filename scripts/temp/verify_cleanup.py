from pathlib import Path

root = Path('d:/PROJECTS/CORTEX')
categories = {
    'SUMMARY': 0,
    'IMPLEMENTATION': 0, 
    'REFERENCE': 0,
    'REPORT': 0,
    'Total .md': 0
}

protected = {'.git', '.venv', 'node_modules', 'src', 'tests'}

for f in root.rglob('*.md'):
    categories['Total .md'] += 1
    if any(p in str(f) for p in protected):
        continue
    name = f.name
    if 'SUMMARY' in name:
        categories['SUMMARY'] += 1
    if 'IMPLEMENTATION' in name:
        categories['IMPLEMENTATION'] += 1
    if 'REFERENCE' in name:
        categories['REFERENCE'] += 1
    if 'REPORT' in name:
        categories['REPORT'] += 1

print('\nRemaining files after cleanup:')
for k, v in categories.items():
    print(f'  {k}: {v}')
