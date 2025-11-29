"""
Simple visual verification test for CORTEX MkDocs site
Checks if the Tales design is correctly applied
"""

import requests
from bs4 import BeautifulSoup

def test_tales_design_applied():
    """Test that Tales design CSS is loaded and elements are present"""
    url = "http://127.0.0.1:8000/"
    
    print("🧪 Testing CORTEX Tales Design Implementation")
    print("=" * 60)
    
    try:
        # Fetch the page
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Test 1: Check if tales-design.css is loaded
        print("\n✓ Test 1: Checking CSS link...")
        css_links = soup.find_all('link', rel='stylesheet')
        tales_css_found = any('tales-design.css' in link.get('href', '') for link in css_links)
        
        if tales_css_found:
            print("  ✅ tales-design.css is linked")
        else:
            print("  ❌ tales-design.css NOT found")
            return False
        
        # Test 2: Check if Material theme is NOT present
        print("\n✓ Test 2: Checking for Material theme removal...")
        material_css = any('material' in link.get('href', '').lower() 
                          for link in css_links 
                          if 'tales' not in link.get('href', ''))
        
        if not material_css:
            print("  ✅ Material theme CSS removed")
        else:
            print("  ⚠️  Material theme CSS still present (but might be overridden)")
        
        # Test 3: Check for Tales design header
        print("\n✓ Test 3: Checking header structure...")
        header = soup.find('header', class_='header')
        if header:
            print("  ✅ Header with class 'header' found")
            
            # Check for subtitle
            subtitle = header.find('p', class_='subtitle')
            if subtitle:
                print("  ✅ Subtitle with word styling found")
            else:
                print("  ❌ Subtitle not found")
                return False
        else:
            print("  ❌ Header not found")
            return False
        
        # Test 4: Check for navigation
        print("\n✓ Test 4: Checking navigation...")
        nav = soup.find('nav', class_='nav')
        if nav:
            nav_items = nav.find_all('a', class_='nav-item')
            print(f"  ✅ Navigation found with {len(nav_items)} items")
        else:
            print("  ❌ Navigation not found")
            return False
        
        # Test 5: Check for stats grid
        print("\n✓ Test 5: Checking stats grid...")
        stats_grid = soup.find('div', class_='stats-grid')
        if stats_grid:
            stat_cards = stats_grid.find_all('div', class_='stat-card')
            print(f"  ✅ Stats grid found with {len(stat_cards)} cards")
        else:
            print("  ❌ Stats grid not found")
            return False
        
        # Test 6: Check for capability cards
        print("\n✓ Test 6: Checking capability cards...")
        capability_grid = soup.find('div', class_='capability-grid')
        if capability_grid:
            capability_cards = capability_grid.find_all('div', class_='capability-card')
            print(f"  ✅ Capability grid found with {len(capability_cards)} cards")
        else:
            print("  ❌ Capability grid not found")
            return False
        
        # Test 7: Check for badges
        print("\n✓ Test 7: Checking badges...")
        badges = soup.find_all('span', class_='badge')
        if badges:
            badge_types = set(badge.get('class', [])[-1] for badge in badges if 'badge' in badge.get('class', []))
            print(f"  ✅ Found {len(badges)} badges with types: {badge_types}")
        else:
            print("  ❌ No badges found")
            return False
        
        # Test 8: Check for footer
        print("\n✓ Test 8: Checking footer...")
        footer = soup.find('footer', class_='footer-branding')
        if footer:
            print("  ✅ Footer with class 'footer-branding' found")
        else:
            print("  ❌ Footer not found")
            return False
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED - Tales design is correctly applied!")
        print("=" * 60)
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to http://127.0.0.1:8000/")
        print("   Make sure MkDocs server is running with 'mkdocs serve'")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    import sys
    success = test_tales_design_applied()
    sys.exit(0 if success else 1)
