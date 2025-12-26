#!/usr/bin/env python3
"""
Simple Story Color Attribution Audit
Checks dialogue attribution rates per chapter without hanging
"""

import re
import json
from pathlib import Path

def extract_dialogues(content):
    """Extract all dialogue lines from markdown content"""
    # Match quoted dialogues
    pattern = r'"([^"]+)"'
    matches = re.findall(pattern, content)
    return matches

def check_attribution(content):
    """Check if dialogue has nearby character attribution"""
    # Character names
    characters = ['Asif', 'Alex', 'Maya', 'Dr. Chen', 'Marcus', 'The Council', 'Elena']
    
    # Count dialogues
    dialogues = extract_dialogues(content)
    total = len(dialogues)
    
    if total == 0:
        return {'total': 0, 'attributed': 0, 'rate': 0}
    
    attributed = 0
    
    # Check each dialogue for nearby character names
    for dialogue in dialogues:
        # Create context window (100 chars before and after)
        pattern = re.escape(f'"{dialogue}"')
        matches = list(re.finditer(pattern, content))
        
        for match in matches:
            start = max(0, match.start() - 100)
            end = min(len(content), match.end() + 100)
            context = content[start:end]
            
            # Check if any character name appears in context
            if any(char in context for char in characters):
                attributed += 1
                break
    
    rate = (attributed / total * 100) if total > 0 else 0
    
    return {
        'total': total,
        'attributed': attributed,
        'unattributed': total - attributed,
        'rate': round(rate, 1)
    }

def main():
    story_dir = Path('docs/story')
    
    if not story_dir.exists():
        print(f"❌ Directory not found: {story_dir}")
        return
    
    # Get all chapter files (in subdirectories)
    chapters = sorted(story_dir.glob('Chapter-*/index.md')) + sorted(story_dir.glob('Prologue/index.md'))
    
    if not chapters:
        print(f"❌ No chapter files found in {story_dir}")
        return
    
    print("🔍 Story Color Attribution Audit\n")
    print(f"{'Chapter':<15} {'Total':<8} {'Attributed':<12} {'Unattributed':<14} {'Rate':<8}")
    print("=" * 70)
    
    results = []
    total_dialogues = 0
    total_attributed = 0
    
    for chapter_file in chapters:
        content = chapter_file.read_text(encoding='utf-8')
        stats = check_attribution(content)
        
        chapter_name = chapter_file.parent.name
        
        print(f"{chapter_name:<15} {stats['total']:<8} {stats['attributed']:<12} "
              f"{stats['unattributed']:<14} {stats['rate']:<8}%")
        
        results.append({
            'chapter': chapter_name,
            'stats': stats
        })
        
        total_dialogues += stats['total']
        total_attributed += stats['attributed']
    
    print("=" * 70)
    overall_rate = (total_attributed / total_dialogues * 100) if total_dialogues > 0 else 0
    print(f"{'TOTAL':<15} {total_dialogues:<8} {total_attributed:<12} "
          f"{total_dialogues - total_attributed:<14} {overall_rate:<8.1f}%\n")
    
    # Find chapters needing attention
    print("\n⚠️  Chapters Below 60% Attribution:")
    for result in results:
        if result['stats']['rate'] < 60:
            print(f"  - {result['chapter']}: {result['stats']['rate']}% "
                  f"({result['stats']['unattributed']} unattributed dialogues)")

if __name__ == '__main__':
    main()
