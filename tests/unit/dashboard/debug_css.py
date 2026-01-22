#!/usr/bin/env python3
"""Debug script for CSS parsing."""
import sys
sys.path.insert(0, 'tests/unit/dashboard')
from conftest import get_context, is_accent_color

ctx = get_context()

# Get accent elements
elements = ctx.get_elements('[class*="ai"], [class*="intelligence"], [class*="accent"]')
print(f'Found {len(elements)} elements')
for elem in elements:
    print(f'  Classes: {elem.classes}')
    class_str = ' '.join(elem.classes).lower()
    has_ai_intel_accent = 'ai' in class_str or 'intelligence' in class_str or 'accent' in class_str
    print(f'    has_ai_intel_accent: {has_ai_intel_accent}')
