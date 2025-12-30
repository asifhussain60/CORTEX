#!/usr/bin/env python3
"""Quick wiring status check - no Unicode issues."""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
reports_dir = PROJECT_ROOT / "cortex-brain" / "health-reports"

# Find latest report
reports = list(reports_dir.glob("wiring-report-*.json"))
if not reports:
    print("No wiring report found")
    exit(1)

latest = max(reports, key=lambda p: p.stat().st_mtime)

# Load and display
with open(latest, 'r', encoding='utf-8') as f:
    data = json.load(f)

total = data.get('total', 0)
wired = data.get('wired', 0)
unwired = data.get('unwired', 0)
coverage = data.get('coverage', 0)

print("=" * 60)
print("CORTEX WIRING STATUS")
print("=" * 60)
print(f"Total Components: {total}")
print(f"Wired:            {wired}")
print(f"Unwired:          {unwired}")
print(f"Coverage:         {coverage:.1f}%")
print("=" * 60)

# Show first 10 unwired
components = data.get('components', [])
unwired_list = [c for c in components if not c.get('wired', False)]

if unwired_list:
    print(f"\nFirst 10 unwired components:")
    for i, comp in enumerate(unwired_list[:10], 1):
        print(f"  {i}. [{comp['type']}] {comp['name']}")
    
    if len(unwired_list) > 10:
        print(f"  ... and {len(unwired_list) - 10} more")
