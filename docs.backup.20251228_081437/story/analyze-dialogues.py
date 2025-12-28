#!/usr/bin/env python3
"""
Analyze character dialogue patterns across all story chapters
Identifies which dialogues have clear character attribution
"""

import re
from pathlib import Path
from collections import defaultdict

# Character patterns to detect
CHARACTERS = {
    'Asif': ['Asif', 'I ', 'my ', 'he ', 'He ', 'his ', 'His '],
    'Miss G': ['Miss G', 'she ', 'She ', 'her ', 'Her ', "Miss G's", 'Mrs. G'],
    'Copilot': ['Copilot', 'AI ', 'assistant'],
    'CORTEX': ['CORTEX', 'system', 'voice'],
    'Mom': ['Mom', 'mother'],
    'Client': ['client', 'business']
}

def analyze_chapter(file_path):
    """Analyze dialogues in a single chapter"""
    content = file_path.read_text()
    
    # Find all quoted dialogues
    dialogue_pattern = r'"([^"]+)"'
    dialogues = []
    
    for match in re.finditer(dialogue_pattern, content):
        dialogue_text = match.group(1)
        dialogue_pos = match.start()
        
        # Skip meta-content
        if any(skip in dialogue_text for skip in ['://', '.css', '.jpeg', '.png', 'Chapter', 'float:', 'margin:']):
            continue
            
        # Get context (150 chars before and after)
        context_start = max(0, dialogue_pos - 150)
        context_end = min(len(content), dialogue_pos + len(match.group(0)) + 150)
        context = content[context_start:context_end]
        
        # Detect character
        detected = None
        for char_name, patterns in CHARACTERS.items():
            if any(pattern.lower() in context.lower() for pattern in patterns):
                detected = char_name
                break
        
        dialogues.append({
            'text': dialogue_text[:50] + ('...' if len(dialogue_text) > 50 else ''),
            'character': detected or 'UNKNOWN',
            'context': context[:100].replace('\n', ' ')
        })
    
    return dialogues

def main():
    story_dir = Path('/Users/asifhussain/PROJECTS/CORTEX/docs/story')
    
    # Collect all chapters
    chapters = []
    chapters.append(('Prologue', story_dir / 'Prologue' / 'index.md'))
    
    for i in range(1, 14):
        chapter_path = story_dir / f'Chapter-{i:02d}' / 'index.md'
        if chapter_path.exists():
            chapters.append((f'Chapter {i}', chapter_path))
    
    # Analyze each chapter
    stats = defaultdict(lambda: defaultdict(int))
    all_unknown = []
    
    print("=" * 80)
    print("CHARACTER DIALOGUE ANALYSIS")
    print("=" * 80)
    
    for chapter_name, chapter_path in chapters:
        dialogues = analyze_chapter(chapter_path)
        
        char_counts = defaultdict(int)
        for d in dialogues:
            char_counts[d['character']] += 1
            if d['character'] == 'UNKNOWN':
                all_unknown.append({
                    'chapter': chapter_name,
                    'text': d['text'],
                    'context': d['context']
                })
        
        print(f"\n{chapter_name}:")
        print(f"  Total dialogues: {len(dialogues)}")
        for char in sorted(char_counts.keys()):
            print(f"  - {char}: {char_counts[char]}")
            stats[chapter_name][char] = char_counts[char]
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    total_dialogues = sum(sum(chars.values()) for chars in stats.values())
    total_unknown = sum(1 for chars in stats.values() for char, count in chars.items() if char == 'UNKNOWN' for _ in range(count))
    
    print(f"\nTotal dialogues across all chapters: {total_dialogues}")
    print(f"Attributed: {total_dialogues - total_unknown} ({100*(total_dialogues-total_unknown)/total_dialogues:.1f}%)")
    print(f"Unattributed (UNKNOWN): {total_unknown} ({100*total_unknown/total_dialogues:.1f}%)")
    
    # Show character totals
    print("\nCharacter totals:")
    char_totals = defaultdict(int)
    for chapter_stats in stats.values():
        for char, count in chapter_stats.items():
            char_totals[char] += count
    
    for char in sorted(char_totals.keys(), key=lambda x: char_totals[x], reverse=True):
        print(f"  - {char}: {char_totals[char]}")
    
    # Sample unknown dialogues
    if all_unknown:
        print("\n" + "=" * 80)
        print("SAMPLE UNATTRIBUTED DIALOGUES (first 10)")
        print("=" * 80)
        for item in all_unknown[:10]:
            print(f"\n{item['chapter']}:")
            print(f"  Dialogue: \"{item['text']}\"")
            print(f"  Context: ...{item['context']}...")

if __name__ == '__main__':
    main()
