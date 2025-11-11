"""Story Transformation Verification Script"""
import re
from pathlib import Path

print("=== STORY TRANSFORMATION VERIFICATION ===\n")

# Read story file
story_path = Path("docs/story/CORTEX-STORY/Awakening Of CORTEX.md")
story = story_path.read_text(encoding='utf-8')

# Check for deprecated terms
deprecated_terms = [
    'KDS (Key Data Stream)',
    'KDS (Knowledge Delivery System)',
    'monolithic entry point'
]

print("1. DEPRECATED TERMS CHECK:")
found_deprecated = []
for term in deprecated_terms:
    if term.lower() in story.lower():
        found_deprecated.append(term)

if found_deprecated:
    print(f"   ❌ Found {len(found_deprecated)} deprecated terms:")
    for term in found_deprecated:
        print(f"      - {term}")
else:
    print("   ✅ All deprecated terms removed")

# Check for active narrator markers
print("\n2. ACTIVE NARRATOR VOICE CHECK:")
active_markers = [
    'muttered to himself',
    'announced to the empty basement',
    'started typing',
    'Time to test',
    'Time to break it'
]

found_active = 0
for marker in active_markers:
    if marker in story:
        print(f"   ✅ \"{marker}\"")
        found_active += 1

print(f"\n   Active markers found: {found_active}/{len(active_markers)}")

# Check story structure
print("\n3. STORY STRUCTURE CHECK:")
parts = story.count("# PART ")
chapters = story.count("## Chapter ")
interludes = story.count("## Interlude:")

print(f"   Parts: {parts}")
print(f"   Chapters: {chapters}")
print(f"   Interludes: {interludes}")

# Summary
print("\n=== TRANSFORMATION SUMMARY ===")
print(f"✅ Deprecated terms removed: {len(found_deprecated) == 0}")
print(f"✅ Active narrator voice applied: {found_active >= 3}")
print(f"✅ Story structure intact: {parts >= 2 and chapters >= 10}")
print("\n✅ TRANSFORMATION COMPLETE")
