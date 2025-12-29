#!/usr/bin/env python3
"""
Find specific unattributed dialogues in a chapter for analysis
"""

import re
from pathlib import Path

def check_attribution(text, dialogue_match, offset, character):
    """Check if dialogue matches a specific character"""
    context_before = text[max(0, offset - 200):offset]
    context_after = text[offset + len(dialogue_match):min(len(text), offset + len(dialogue_match) + 100)]
    
    patterns_before = [
        rf'{character}[^.]*?$',
        rf"{character}'s[^.]*?$",
        rf'{character} (?:asked|said|responded|replied|explained|muttered|whispered|shouted)',
        rf'{character} (?:turned|looked|smiled|frowned|winced|blinked|sighed|nodded)',
        rf'{character} (?:could|would|should|might|must|had to)',
        rf'{character}[^.]{{0,30}}(?:thoughts|mind|voice)',
    ]
    
    patterns_after = [
        rf'^[,.]?\\s*{character}\\s+(?:asked|said|muttered|thought)',
        rf'^[,.]?\\s*{character}\\s+(?:blinked|sighed|nodded|turned)',
    ]
    
    for pattern_str in patterns_before:
        if re.search(pattern_str, context_before, re.IGNORECASE):
            return True
    
    for pattern_str in patterns_after:
        if re.search(pattern_str, context_after, re.IGNORECASE):
            return True
    
    return False

def find_unattributed(filepath, limit=20):
    """Find unattributed dialogues in chapter"""
    content = filepath.read_text(encoding='utf-8')
    
    characters = ['Asif', 'Miss G', 'Copilot', 'CORTEX', 'he', 'He', 'she', 'She']
    
    dialogue_pattern = r'"([^"]+)"'
    matches = list(re.finditer(dialogue_pattern, content))
    
    unattributed = []
    
    for match in matches:
        # Check all characters
        attributed = False
        for char in characters:
            if check_attribution(content, match.group(0), match.start(), char):
                attributed = True
                break
        
        if not attributed:
            start = max(0, match.start() - 150)
            end = min(len(content), match.end() + 150)
            context = content[start:end].replace('\n', ' ').strip()
            
            unattributed.append({
                'dialogue': match.group(1),
                'context': context
            })
            
            if len(unattributed) >= limit:
                break
    
    return unattributed

def main():
    chapter_path = Path('docs/story/Chapter-11/index.md')
    
    if not chapter_path.exists():
        print(f"❌ File not found: {chapter_path}")
        return
    
    print("🔍 Unattributed Dialogues in Chapter-11\n")
    
    unattributed = find_unattributed(chapter_path, limit=20)
    
    for i, item in enumerate(unattributed, 1):
        print(f"\n{i}. \"{item['dialogue']}\"")
        print(f"   Context: ...{item['context'][:200]}...")
        print()

if __name__ == '__main__':
    main()
