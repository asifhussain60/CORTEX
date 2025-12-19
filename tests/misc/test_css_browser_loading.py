"""
Test to verify CSS can be loaded in a browser and renders correctly.

This helps debug browser caching and CSS application issues.
"""

import pytest
from pathlib import Path
import hashlib


class TestCSSCacheBusting:
    """Test CSS file integrity and cache-busting."""
    
    def test_css_file_hash(self):
        """Generate hash of CSS file to detect changes."""
        css_path = Path("d:/PROJECTS/CORTEX/site/stylesheets/custom.css")
        
        if not css_path.exists():
            pytest.skip("Run 'mkdocs build' first")
        
        content = css_path.read_bytes()
        file_hash = hashlib.md5(content).hexdigest()
        
        print(f"\n✅ CSS File Hash: {file_hash}")
        print(f"✅ CSS File Size: {len(content)} bytes")
        print("\nIf you're not seeing styles, try:")
        print("1. Hard refresh browser (Ctrl+Shift+R or Cmd+Shift+R)")
        print("2. Clear browser cache")
        print(f"3. Verify CSS loaded: http://127.0.0.1:8000/stylesheets/custom.css")
        
        # File should be substantial
        assert len(content) > 10000, \
            f"CSS file seems too small ({len(content)} bytes). Expected > 10KB"
    
    def test_css_specificity_check(self):
        """Check that our selectors are specific enough."""
        css_path = Path("d:/PROJECTS/CORTEX/site/stylesheets/custom.css")
        
        if not css_path.exists():
            pytest.skip("Run 'mkdocs build' first")
        
        content = css_path.read_text(encoding='utf-8')
        
        # Count !important flags (we need them to override Material theme)
        important_count = content.count('!important')
        
        print(f"\n✅ !important flags: {important_count}")
        print("These override Material theme's default styles")
        
        assert important_count >= 20, \
            f"Expected at least 20 !important flags, found {important_count}. " \
            "Need more to override Material theme."
    
    def test_css_load_order(self):
        """Verify custom.css loads after Material theme CSS."""
        html_path = Path(__file__).resolve().parent.parent / "site" / "index.html"
        
        if not html_path.exists():
            pytest.skip("Run 'mkdocs build' first")
        
        html = html_path.read_text(encoding='utf-8')
        
        # Find positions of CSS links
        material_pos = html.find('assets/stylesheets/main')
        custom_pos = html.find('stylesheets/custom.css')
        
        print(f"\n✅ Material CSS position: {material_pos}")
        print(f"✅ Custom CSS position: {custom_pos}")
        
        assert material_pos < custom_pos, \
            "custom.css should load AFTER Material theme CSS to override styles"
        
        print("✅ CSS load order is correct!")


class TestVisualDebugging:
    """Generate debugging info for visual inspection."""
    
    def test_generate_css_snippet(self):
        """Generate a CSS snippet to test in browser DevTools."""
        css_path = Path("d:/PROJECTS/CORTEX/site/stylesheets/custom.css")
        
        if not css_path.exists():
            pytest.skip("Run 'mkdocs build' first")
        
        content = css_path.read_text(encoding='utf-8')
        
        # Extract navigation styles
        import re
        nav_match = re.search(
            r'/\*.*NAVIGATION.*?\*/.*?(?=/\*|$)',
            content,
            re.DOTALL
        )
        
        if nav_match:
            nav_styles = nav_match.group(0)
            print("\n" + "="*80)
            print("Copy this to browser DevTools to test styles manually:")
            print("="*80)
            print(nav_styles[:500])  # First 500 chars
            print("\n... (truncated)")
            print("="*80)
        
        assert True  # Always pass, this is for info only


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])  # -s shows print statements
