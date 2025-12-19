#!/usr/bin/env python3
"""
TDD Test: JavaScript Initialization

RED PHASE: Test that initialization functions are being called.
"""

import re
from pathlib import Path


def test_javascript_initialization_code():
    """Test that DOMContentLoaded and init functions are properly connected"""
    dashboard_path = Path("cortex-brain/documents/onboarded-apps/noor-canvas/dashboard.html")
    
    with open(dashboard_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Test 1: DOMContentLoaded listener exists
    assert 'DOMContentLoaded' in content, "Missing DOMContentLoaded event listener"
    
    # Test 2: Check what's called in DOMContentLoaded
    dom_pattern = r"addEventListener\('DOMContentLoaded'.*?\{([^}]+)\}"
    dom_match = re.search(dom_pattern, content, re.DOTALL)
    
    if dom_match:
        init_code = dom_match.group(1)
        print(f"DOMContentLoaded code:\n{init_code[:500]}")
    else:
        # Try alternate pattern
        dom_pattern2 = r"window\.addEventListener\('DOMContentLoaded',\s*\(\)\s*=>\s*\{([^\}]+)\}"
        dom_match = re.search(dom_pattern2, content, re.DOTALL)
        if dom_match:
            init_code = dom_match.group(1)
            print(f"DOMContentLoaded code:\n{init_code[:500]}")
    
    # Test 3: Check if initializeOverview is called
    if 'initializeOverview()' in content:
        print("✅ initializeOverview() is called")
    else:
        print("❌ initializeOverview() NOT called")
        raise AssertionError("initializeOverview() not called in initialization")
    
    # Test 4: Check if there's code to render architecture graph
    if 'architecture-graph' in content and 'd3.select' in content:
        print("✅ D3 graph rendering code present")
    else:
        print("❌ D3 graph rendering code missing or not connected")
        raise AssertionError("D3 graph rendering not properly set up")
    
    return True


def test_tab_initialization():
    """Test that tabs are initialized and first tab is active"""
    dashboard_path = Path("cortex-brain/documents/onboarded-apps/noor-canvas/dashboard.html")
    
    with open(dashboard_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Test 1: Overview tab has active class by default
    overview_active_patterns = [
        r'id="overview-tab"[^>]*class="[^"]*active[^"]*"',
        r'id="overview-tab".*?active',
        r'class="[^"]*active[^"]*"[^>]*id="overview-tab"'
    ]
    
    found_active = any(re.search(pattern, content, re.DOTALL) for pattern in overview_active_patterns)
    
    if not found_active:
        print("❌ Overview tab doesn't have 'active' class by default")
        # Check what class it has
        overview_match = re.search(r'id="overview-tab"[^>]*class="([^"]*)"', content)
        if overview_match:
            print(f"   Overview tab class: '{overview_match.group(1)}'")
        raise AssertionError("Overview tab not set as active by default")
    
    print("✅ Overview tab is active by default")
    return True


if __name__ == '__main__':
    print("=" * 70)
    print("TDD RED PHASE: JavaScript Initialization Tests")
    print("=" * 70)
    
    tests = [
        ("JavaScript Initialization", test_javascript_initialization_code),
        ("Tab Active State", test_tab_initialization)
    ]
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            test_func()
            print(f"✅ {test_name}: PASS")
        except AssertionError as e:
            print(f"❌ {test_name}: FAIL - {e}")
        except Exception as e:
            print(f"💥 {test_name}: ERROR - {e}")
