#!/usr/bin/env python3
"""
Fix MkDocs UTF-8 Encoding Issues

This script ensures MkDocs builds with proper UTF-8 encoding on Windows
where the default locale encoding (cp1252) can cause garbled text.

Root Cause:
- Python locale encoding: cp1252 (Windows-1252)
- Source files: UTF-8 with characters like —, ✓, 🎯
- Result: Double-encoding artifacts (ΓÇö, Γ£à, ≡ƒôï)

Solution:
1. Force PYTHONUTF8=1 environment variable
2. Verify all template files use UTF-8
3. Clean and rebuild with correct encoding
"""

import os
import sys
import subprocess
from pathlib import Path


def set_utf8_environment():
    """Set environment variables to force UTF-8 encoding."""
    os.environ['PYTHONUTF8'] = '1'
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    print("✓ Set PYTHONUTF8=1 and PYTHONIOENCODING=utf-8")


def verify_encoding():
    """Verify Python encoding settings."""
    import locale
    
    print("\n📊 Encoding Check:")
    print(f"  Default encoding: {sys.getdefaultencoding()}")
    print(f"  Locale encoding: {locale.getpreferredencoding()}")
    print(f"  PYTHONUTF8: {os.environ.get('PYTHONUTF8', 'not set')}")
    print(f"  PYTHONIOENCODING: {os.environ.get('PYTHONIOENCODING', 'not set')}")


def clean_build():
    """Clean previous MkDocs builds."""
    site_dir = Path('site')
    if site_dir.exists():
        print(f"\n🧹 Cleaning {site_dir}...")
        import shutil
        shutil.rmtree(site_dir)
        print("  ✓ Removed old build")


def build_mkdocs():
    """Build MkDocs with proper UTF-8 encoding."""
    print("\n🔨 Building MkDocs site...")
    
    # Run mkdocs build with UTF-8 environment
    result = subprocess.run(
        ['mkdocs', 'build', '--clean', '--strict'],
        env=os.environ.copy(),
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    
    if result.returncode == 0:
        print("  ✓ Build successful")
        return True
    else:
        print("  ✗ Build failed:")
        print(result.stderr)
        return False


def verify_output():
    """Verify that output HTML has correct UTF-8 characters."""
    print("\n🔍 Verifying output encoding...")
    
    test_file = Path('site/diagrams/story/The-CORTEX-Story/index.html')
    
    if not test_file.exists():
        print(f"  ⚠ Test file not found: {test_file}")
        return False
    
    # Read file and check for garbled characters
    content = test_file.read_text(encoding='utf-8')
    
    # Check for correct UTF-8 characters
    correct_chars = ['—', '✓', '✅', '🎯', '…', '"', '"']
    # Check for garbled patterns (double-encoded UTF-8)
    garbled_patterns = ['ΓÇö', 'Γ£à', '≡ƒôï', 'ΓÇÖ', 'ΓÇô', 'Γäó']
    
    found_correct = sum(1 for char in correct_chars if char in content)
    found_garbled = sum(1 for pattern in garbled_patterns if pattern in content)
    
    print(f"  Correct UTF-8 chars found: {found_correct}/{len(correct_chars)}")
    print(f"  Garbled patterns found: {found_garbled}/{len(garbled_patterns)}")
    
    if found_garbled > 0:
        print("  ✗ ENCODING ISSUES DETECTED")
        print("\n  Garbled patterns found:")
        for pattern in garbled_patterns:
            if pattern in content:
                # Find context around garbled text
                idx = content.index(pattern)
                context = content[max(0, idx-30):min(len(content), idx+30)]
                print(f"    '{pattern}' in: ...{context}...")
        return False
    elif found_correct > 0:
        print("  ✓ UTF-8 encoding correct")
        return True
    else:
        print("  ⚠ No test characters found (file might not contain them)")
        return True


def main():
    """Main execution."""
    print("🚀 MkDocs UTF-8 Encoding Fix\n")
    print("=" * 60)
    
    # Step 1: Set UTF-8 environment
    set_utf8_environment()
    
    # Step 2: Verify encoding
    verify_encoding()
    
    # Step 3: Clean previous builds
    clean_build()
    
    # Step 4: Build MkDocs
    if not build_mkdocs():
        print("\n❌ Build failed. Please check errors above.")
        sys.exit(1)
    
    # Step 5: Verify output
    if not verify_output():
        print("\n❌ Output verification failed. Encoding issues detected.")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ MkDocs build completed with correct UTF-8 encoding!")
    print("\nNext steps:")
    print("  1. Test the site: mkdocs serve")
    print("  2. Check for garbled text in browser")
    print("  3. Run automated tests: python tests/test_mkdocs_encoding.py")


if __name__ == '__main__':
    main()
