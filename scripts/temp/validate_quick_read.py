"""Validate Quick Read version"""
from pathlib import Path
import re

file = Path("docs/story/CORTEX-STORY/Awakening Of CORTEX - Quick Read.md")
text = file.read_text(encoding='utf-8')

words = len(re.findall(r'\b\w+\b', text))

print("Quick Read Stats:")
print(f"Total words: {words:,}")
print(f"Estimated reading time: {words // 200}-{words // 150} minutes")
print(f"Original: ~12,500 words (50-60 min)")
print(f"Reduction: {((12500 - words) / 12500 * 100):.1f}%")
print()

essentials = [
    'Tier 1', 'Tier 2', 'Tier 3', 'Tier 0',
    'Rule #22', 
    'Right Brain', 'Left Brain',
    'SQLite', 'token', 'modular', 'plugin',
    'amnesia', 'memory', 'learning'
]

found = [term for term in essentials if term.lower() in text.lower()]

print(f"Essential concepts found: {len(found)}/{len(essentials)}")
for term in found:
    print(f"  ✅ {term}")

if len(found) < len(essentials):
    print()
    missing = [term for term in essentials if term.lower() not in text.lower()]
    print(f"Missing concepts: {len(missing)}")
    for term in missing:
        print(f"  ❌ {term}")

print()
print("Comedy density check:")
humor_markers = ['😂', '🤣', '*[', 'snapped', 'muttered', 'screamed', 'Narrator:']
humor_count = sum(text.count(marker) for marker in humor_markers)
print(f"Humor markers found: {humor_count}")
print(f"Laughs per 100 words: {(humor_count / words * 100):.2f}")
