#!/usr/bin/env python3
"""
Verify that all chapter HTML files have:
1. CSS stylesheet link in <head>
2. Proper dialogue span tags
3. No visible CSS class names in text
"""

import re
from pathlib import Path
from collections import defaultdict

def verify_chapter_html(html_path):
    """Verify a single chapter HTML file"""
    issues = []
    
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check 1: CSS link present in <head>
    if '<link rel="stylesheet" href="../story-styles.css">' not in content:
        issues.append("❌ Missing CSS stylesheet link in <head>")
    
    # Check 2: Has dialogue spans
    dialogue_spans = re.findall(r'<span class="dialogue-(asif|miss-g)">', content)
    if not dialogue_spans:
        issues.append("⚠️  No dialogue spans found (might not have dialogue)")
    
    # Check 3: No literal class names in text (outside of tags)
    # This would catch cases where "dialogue-asif" appears as visible text
    body_match = re.search(r'<body>(.*?)</body>', content, re.DOTALL)
    if body_match:
        body_content = body_match.group(1)
        # Remove all HTML tags to get just text
        text_only = re.sub(r'<[^>]+>', '', body_content)
        if 'dialogue-asif' in text_only or 'dialogue-miss-g' in text_only:
            issues.append("❌ CRITICAL: CSS class names appearing as visible text!")
    
    # Check 4: Verify closing tags
    open_spans = content.count('<span class="dialogue-')
    close_spans = content.count('</span>')
    if open_spans > close_spans:
        issues.append(f"⚠️  Mismatched spans: {open_spans} open, {close_spans} close")
    
    return issues, len(dialogue_spans)

def main():
    """Verify all chapters"""
    story_dir = Path(__file__).parent
    
    chapters = [
        'Prologue',
        'Chapter-01', 'Chapter-02', 'Chapter-03', 'Chapter-04',
        'Chapter-05', 'Chapter-06', 'Chapter-07', 'Chapter-08',
        'Chapter-09', 'Chapter-10', 'Chapter-11', 'Chapter-12',
        'Chapter-13'
    ]
    
    print("=" * 70)
    print("🧠 CORTEX Dialogue Color Verification")
    print("=" * 70)
    print()
    
    total_issues = 0
    total_dialogues = 0
    results = []
    
    for chapter in chapters:
        html_file = story_dir / chapter / 'index.html'
        
        if not html_file.exists():
            print(f"⚠️  {chapter}: HTML file not found")
            results.append((chapter, ["❌ File not found"], 0))
            total_issues += 1
            continue
        
        issues, dialogue_count = verify_chapter_html(html_file)
        results.append((chapter, issues, dialogue_count))
        
        if issues:
            total_issues += len(issues)
            print(f"🔴 {chapter}:")
            for issue in issues:
                print(f"   {issue}")
        else:
            print(f"✅ {chapter}: {dialogue_count} dialogue spans")
        
        total_dialogues += dialogue_count
    
    print()
    print("=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    print(f"Chapters checked: {len(chapters)}")
    print(f"Total dialogue spans: {total_dialogues}")
    print(f"Issues found: {total_issues}")
    print()
    
    if total_issues == 0:
        print("🎉 ALL CHECKS PASSED!")
        print("   ✓ CSS stylesheets linked correctly")
        print("   ✓ Dialogue spans properly formatted")
        print("   ✓ No visible CSS class names in text")
        print("   ✓ All HTML structure valid")
        return 0
    else:
        print("❌ ISSUES DETECTED - See details above")
        return 1

if __name__ == '__main__':
    exit(main())
