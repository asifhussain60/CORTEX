#!/usr/bin/env python3
"""
TDD REFACTOR PHASE: Check for similar ID mismatch issues

Audit all DOM IDs to ensure JavaScript selectors match HTML elements.
"""

import re
from pathlib import Path
from collections import defaultdict


def extract_html_ids(content):
    """Extract all id="..." from HTML"""
    pattern = r'id="([^"]+)"'
    return set(re.findall(pattern, content))


def extract_js_selectors(content):
    """Extract all DOM selectors from JavaScript"""
    selectors = set()
    
    # getElementById patterns
    pattern1 = r"getElementById\(['\"]([^'\"]+)['\"]\)"
    selectors.update(re.findall(pattern1, content))
    
    # querySelector with # patterns
    pattern2 = r"querySelector\(['\"]#([^'\"]+)['\"]\)"
    selectors.update(re.findall(pattern2, content))
    
    # d3.select with # patterns
    pattern3 = r"d3\.select\(['\"]#([^'\"]+)['\"]\)"
    selectors.update(re.findall(pattern3, content))
    
    # document.getElementById
    pattern4 = r"document\.getElementById\(['\"]([^'\"]+)['\"]\)"
    selectors.update(re.findall(pattern4, content))
    
    return selectors


def audit_id_consistency():
    """Audit dashboard for ID consistency"""
    dashboard_path = Path("cortex-brain/documents/onboarded-apps/noor-canvas/dashboard.html")
    
    with open(dashboard_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    html_ids = extract_html_ids(content)
    js_selectors = extract_js_selectors(content)
    
    print(f"📊 Found {len(html_ids)} HTML IDs")
    print(f"📊 Found {len(js_selectors)} JavaScript selectors\n")
    
    # Check for mismatches
    missing_in_html = js_selectors - html_ids
    unused_ids = html_ids - js_selectors
    
    issues = []
    
    if missing_in_html:
        print("⚠️  JavaScript references IDs that don't exist in HTML:")
        for selector_id in sorted(missing_in_html):
            print(f"   - #{selector_id}")
            issues.append(f"Missing HTML element for #{selector_id}")
    
    if unused_ids:
        print("\n📝 HTML IDs not used in JavaScript (may be intentional):")
        for html_id in sorted(unused_ids):
            print(f"   - #{html_id}")
    
    if not missing_in_html:
        print("✅ All JavaScript selectors have matching HTML IDs!")
    
    # Critical IDs check
    critical_ids = [
        'overview-tab', 'techstack-tab', 'architecture-tab', 'security-tab',
        'uml-tab', 'recommendations-tab', 'data-tab',
        'architecture-graph', 'table-body', 'recommendations-container'
    ]
    
    print(f"\n🔍 Checking {len(critical_ids)} critical IDs:")
    for crit_id in critical_ids:
        if crit_id in html_ids:
            print(f"   ✅ #{crit_id}")
        else:
            print(f"   ❌ #{crit_id} MISSING")
            issues.append(f"Critical ID missing: #{crit_id}")
    
    return len(issues) == 0, issues


if __name__ == '__main__':
    print("=" * 70)
    print("TDD REFACTOR PHASE: ID Consistency Audit")
    print("=" * 70)
    print()
    
    success, issues = audit_id_consistency()
    
    print("\n" + "=" * 70)
    if success:
        print("✅ REFACTOR COMPLETE: No ID mismatches found!")
    else:
        print(f"⚠️  Found {len(issues)} potential issues:")
        for issue in issues:
            print(f"   - {issue}")
        print("\nThese may need attention in future iterations.")
