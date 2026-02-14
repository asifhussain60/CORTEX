#!/usr/bin/env python3
"""
Dashboard Loading Test
Tests that the dashboard loads JSON data correctly via HTTP
"""

import json
import subprocess
import time
from urllib.request import urlopen
from urllib.error import URLError

def test_dashboard_json():
    """Test that plan-summary.json is accessible and valid"""
    url = 'http://localhost:8893/data/plan-summary.json'
    
    try:
        with urlopen(url, timeout=5) as response:
            data = json.loads(response.read())
            
        # Verify structure
        assert 'statistics' in data, "Missing 'statistics' key"
        assert 'active_phases' in data, "Missing 'active_phases' key"
        
        stats = data['statistics']
        print("✅ JSON loads successfully")
        print(f"📊 Total phases: {stats['total_phases']}")
        print(f"📊 Active phases: {stats['active_phases']}")
        print(f"📊 Completed 2026: {stats['completed_2026']}")
        print(f"📊 Completed 2025: {stats['completed_2025']}")
        print(f"📊 Total completed: {stats['completed_2025'] + stats['completed_2026']}")
        print(f"📊 Completion rate: {stats['completion_rate']}%")
        print(f"📊 Status: {stats['overall_status']}")
        
        # Verify expected values
        assert stats['total_phases'] == 20, f"Expected 20 total phases, got {stats['total_phases']}"
        assert stats['active_phases'] == 1, f"Expected 1 active phase, got {stats['active_phases']}"
        assert stats['completion_rate'] == 95, f"Expected 95% completion, got {stats['completion_rate']}%"
        
        print("\n✅ All assertions passed")
        return True
        
    except URLError as e:
        print(f"❌ Failed to load JSON: {e}")
        print("⚠️  Is the HTTP server running on port 8893?")
        print("   Run: cd cortex-registry/_cortex-master/dashboard && python3 -m http.server 8893")
        return False
    except AssertionError as e:
        print(f"❌ Assertion failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_dashboard_html():
    """Test that index.html loads correctly"""
    url = 'http://localhost:8893/index.html'
    
    try:
        with urlopen(url, timeout=5) as response:
            html = response.read().decode('utf-8')
            
        # Verify dynamic loading code is present
        assert 'loadDashboardData' in html, "Missing loadDashboardData function"
        assert 'transformDashboardData' in html, "Missing transformDashboardData function"
        assert "fetch('data/plan-summary.json')" in html, "Missing fetch call"
        
        print("\n✅ HTML loads successfully")
        print("✅ Dynamic JSON loading code present")
        print("✅ Transform function present")
        
        return True
        
    except URLError as e:
        print(f"\n❌ Failed to load HTML: {e}")
        return False
    except AssertionError as e:
        print(f"\n❌ Assertion failed: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("CORTEX Dashboard Loading Test")
    print("=" * 60)
    print()
    
    # Run tests
    json_ok = test_dashboard_json()
    html_ok = test_dashboard_html()
    
    print()
    print("=" * 60)
    if json_ok and html_ok:
        print("✅ ALL TESTS PASSED")
        print()
        print("🌐 Dashboard URL: http://localhost:8893/index.html")
        print("📊 JSON URL: http://localhost:8893/data/plan-summary.json")
        print()
        print("Open the dashboard in your browser and check:")
        print("  1. Progress ring shows 95% (not 0%)")
        print("  2. Active phases shows 1 (not 0)")
        print("  3. Completed shows 19 (not 0)")
        print("  4. Browser console shows: '✅ Dashboard data loaded from plan-summary.json'")
    else:
        print("❌ TESTS FAILED")
        print()
        print("Troubleshooting:")
        print("  1. Ensure HTTP server is running: python3 -m http.server 8893")
        print("  2. Server must be in: cortex-registry/_cortex-master/dashboard/")
        print("  3. Do NOT open via file:// protocol")
    print("=" * 60)
