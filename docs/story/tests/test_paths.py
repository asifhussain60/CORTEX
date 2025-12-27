#!/usr/bin/env python3
"""
Story Viewer Path Validation Tests
Validates all chapter files and image paths exist before Git Pages deployment.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Tuple

# Base paths
STORY_DIR = Path(__file__).parent.parent
DOCS_DIR = STORY_DIR.parent

# Chapter configuration (mirrors story-viewer.js)
CHAPTERS = {
    'prologue': {
        'file': 'Prologue/PROLOGUE.txt',
        'images': [
            'illustrations/images/essentials/cortex-awakening-prologue-01.jpeg',
            'illustrations/images/essentials/cortex-awakening-prologue-02.jpeg'
        ]
    },
    'chapter-01': {
        'file': 'Chapter-01/CHAPTER-01.txt',
        'images': [
            'illustrations/images/essentials/cortex-awakening-ch01-01.jpeg',
            'illustrations/images/valuable/cortex-awakening-ch01-02.jpeg',
            'illustrations/images/essentials/cortex-awakening-ch01-03.jpeg'
        ]
    },
    'chapter-02': {
        'file': 'Chapter-02/CHAPTER-02.txt',
        'images': [
            'illustrations/images/essentials/cortex-awakening-ch02-01.jpeg',
            'illustrations/images/essentials/cortex-awakening-ch02-02.jpeg'
        ]
    },
    'chapter-03': {
        'file': 'Chapter-03/CHAPTER-03.txt',
        'images': [
            'illustrations/images/essentials/cortex-awakening-ch03-01.jpeg'
        ]
    },
    'chapter-04': {
        'file': 'Chapter-04/CHAPTER-04.txt',
        'images': []
    },
    'chapter-05': {
        'file': 'Chapter-05/CHAPTER-05.txt',
        'images': [
            'illustrations/images/valuable/cortex-awakening-ch05-01.jpeg'
        ]
    },
    'chapter-06': {
        'file': 'Chapter-06/CHAPTER-06.txt',
        'images': [
            'illustrations/images/valuable/cortex-awakening-ch06-01.jpeg'
        ]
    },
    'chapter-07': {
        'file': 'Chapter-07/CHAPTER-07.txt',
        'images': [
            'illustrations/images/essentials/cortex-awakening-ch07-01.jpeg',
            'illustrations/images/valuable/cortex-awakening-ch07-02.jpeg'
        ]
    },
    'chapter-08': {
        'file': 'Chapter-08/CHAPTER-08.txt',
        'images': [
            'illustrations/images/essentials/cortex-awakening-ch08-01.jpeg'
        ]
    },
    'chapter-09': {
        'file': 'Chapter-09/CHAPTER-09.txt',
        'images': [
            'illustrations/images/essentials/cortex-awakening-ch09-01.jpeg',
            'illustrations/images/valuable/cortex-awakening-ch09-02.jpeg'
        ]
    },
    'chapter-10': {
        'file': 'Chapter-10/CHAPTER-10.txt',
        'images': [
            'illustrations/images/essentials/cortex-awakening-ch10-01.jpeg'
        ]
    },
    'chapter-11': {
        'file': 'Chapter-11/CHAPTER-11.txt',
        'images': [
            'illustrations/images/valuable/cortex-awakening-ch11-01.jpeg',
            'illustrations/images/valuable/cortex-awakening-ch11-02.jpeg'
        ]
    },
    'chapter-12': {
        'file': 'Chapter-12/CHAPTER-12.txt',
        'images': [
            'illustrations/images/essentials/cortex-awakening-epilogue-01.jpeg'
        ]
    }
}


def test_chapter_files() -> Tuple[int, int, List[str]]:
    """Test all chapter files exist and are readable"""
    print("\n📖 Testing Chapter Files...")
    passed = 0
    failed = 0
    errors = []
    
    for chapter_id, config in CHAPTERS.items():
        file_path = STORY_DIR / config['file']
        
        if not file_path.exists():
            failed += 1
            error = f"  ❌ {chapter_id}: File not found - {config['file']}"
            errors.append(error)
            print(error)
        elif not file_path.is_file():
            failed += 1
            error = f"  ❌ {chapter_id}: Not a file - {config['file']}"
            errors.append(error)
            print(error)
        elif os.path.getsize(file_path) == 0:
            failed += 1
            error = f"  ❌ {chapter_id}: Empty file - {config['file']}"
            errors.append(error)
            print(error)
        else:
            passed += 1
            # Verify file is readable
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read(100)  # Read first 100 chars
                    if not content:
                        failed += 1
                        error = f"  ❌ {chapter_id}: File is empty - {config['file']}"
                        errors.append(error)
                        print(error)
                        passed -= 1
                    else:
                        print(f"  ✅ {chapter_id}: {config['file']}")
            except Exception as e:
                failed += 1
                error = f"  ❌ {chapter_id}: Read error - {config['file']} ({e})"
                errors.append(error)
                print(error)
                passed -= 1
    
    return passed, failed, errors


def test_image_files() -> Tuple[int, int, List[str]]:
    """Test all image files exist"""
    print("\n🖼️  Testing Image Files...")
    passed = 0
    failed = 0
    errors = []
    
    for chapter_id, config in CHAPTERS.items():
        for image_path in config['images']:
            full_path = STORY_DIR / image_path
            
            if not full_path.exists():
                failed += 1
                error = f"  ❌ {chapter_id}: Image not found - {image_path}"
                errors.append(error)
                print(error)
            elif not full_path.is_file():
                failed += 1
                error = f"  ❌ {chapter_id}: Not a file - {image_path}"
                errors.append(error)
                print(error)
            elif os.path.getsize(full_path) == 0:
                failed += 1
                error = f"  ❌ {chapter_id}: Empty image - {image_path}"
                errors.append(error)
                print(error)
            else:
                passed += 1
                print(f"  ✅ {chapter_id}: {Path(image_path).name}")
    
    return passed, failed, errors


def test_viewer_file() -> bool:
    """Test viewer.html exists"""
    print("\n📄 Testing Viewer Files...")
    
    viewer_path = STORY_DIR / "viewer.html"
    js_path = STORY_DIR / "story-viewer.js"
    
    viewer_ok = viewer_path.exists() and viewer_path.is_file()
    js_ok = js_path.exists() and js_path.is_file()
    
    if viewer_ok:
        print(f"  ✅ viewer.html")
    else:
        print(f"  ❌ viewer.html not found")
    
    if js_ok:
        print(f"  ✅ story-viewer.js")
    else:
        print(f"  ❌ story-viewer.js not found")
    
    return viewer_ok and js_ok


def test_assets() -> bool:
    """Test required assets exist"""
    print("\n🎨 Testing Assets...")
    
    logo_path = DOCS_DIR / "assets" / "images" / "CORTEX-logo.png"
    css_path = DOCS_DIR / "assets" / "css" / "main.css"
    
    logo_ok = logo_path.exists() and logo_path.is_file()
    css_ok = css_path.exists() and css_path.is_file()
    
    if logo_ok:
        print(f"  ✅ CORTEX-logo.png")
    else:
        print(f"  ❌ CORTEX-logo.png not found")
    
    if css_ok:
        print(f"  ✅ main.css")
    else:
        print(f"  ❌ main.css not found")
    
    return logo_ok and css_ok


def generate_report(results: Dict) -> None:
    """Generate test report"""
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    
    total_tests = sum(r['passed'] + r['failed'] for r in results.values())
    total_passed = sum(r['passed'] for r in results.values())
    total_failed = sum(r['failed'] for r in results.values())
    
    for category, result in results.items():
        status = "✅" if result['failed'] == 0 else "❌"
        print(f"{status} {category}: {result['passed']} passed, {result['failed']} failed")
    
    print("=" * 70)
    print(f"TOTAL: {total_passed}/{total_tests} tests passed")
    
    if total_failed > 0:
        print(f"\n⚠️  {total_failed} test(s) FAILED")
        print("\n🔍 Failed Tests:")
        for category, result in results.items():
            if result['errors']:
                print(f"\n{category}:")
                for error in result['errors']:
                    print(error)
        return False
    else:
        print("\n🎉 All tests PASSED!")
        print("✅ Story viewer is ready for Git Pages deployment")
        return True


def main():
    """Run all tests"""
    print("=" * 70)
    print("🧠 CORTEX Story Viewer - Path Validation Tests")
    print("=" * 70)
    print(f"📁 Story Directory: {STORY_DIR}")
    print(f"📁 Docs Directory: {DOCS_DIR}")
    
    results = {}
    
    # Test chapter files
    passed, failed, errors = test_chapter_files()
    results['Chapter Files'] = {'passed': passed, 'failed': failed, 'errors': errors}
    
    # Test image files
    passed, failed, errors = test_image_files()
    results['Image Files'] = {'passed': passed, 'failed': failed, 'errors': errors}
    
    # Test viewer files
    viewer_ok = test_viewer_file()
    results['Viewer Files'] = {'passed': 2 if viewer_ok else 0, 'failed': 0 if viewer_ok else 2, 'errors': []}
    
    # Test assets
    assets_ok = test_assets()
    results['Asset Files'] = {'passed': 2 if assets_ok else 0, 'failed': 0 if assets_ok else 2, 'errors': []}
    
    # Generate report
    success = generate_report(results)
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
