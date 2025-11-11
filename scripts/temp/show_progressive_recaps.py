"""Display full progressive recap content"""

from src.plugins.doc_refresh_plugin import Plugin
from pathlib import Path

# Initialize plugin
plugin = Plugin()
plugin.initialize()

# Load story
story_path = Path('docs/story/CORTEX-STORY/Awakening Of CORTEX.md')
story_text = story_path.read_text(encoding='utf-8')

# Generate progressive recaps
recaps = plugin._generate_progressive_recaps(story_text)

print("=" * 80)
print("PROGRESSIVE RECAPS FOR CORTEX STORY")
print("=" * 80)
print(f"\nParts Found: {', '.join(recaps['found_parts'])}")
print()

if recaps.get('part_2_recap'):
    print("=" * 80)
    print("PART 2 RECAP (Start of Part 2 - Summarizes Part 1)")
    print("=" * 80)
    p2 = recaps['part_2_recap']
    print(f"Location: {p2['location']}")
    print(f"Style: {p2['style']}")
    print(f"Compression: {p2['compression_level']}")
    print(f"Token Estimate: {p2['token_estimate']}")
    print()
    print("CONTENT:")
    print(p2['content'])
    print()

if recaps.get('part_3_recap'):
    print("=" * 80)
    print("PART 3 RECAP (Start of Part 3 - Summarizes Part 2 + Part 1)")
    print("=" * 80)
    p3 = recaps['part_3_recap']
    print(f"Location: {p3['location']}")
    print(f"Style: {p3['style']}")
    print(f"Compression: {p3['compression_level']}")
    print(f"Token Estimate: {p3['token_estimate']}")
    print()
    print("CONTENT:")
    print(p3['content'])
    print()

print("=" * 80)
print("USAGE INSTRUCTIONS")
print("=" * 80)
print("""
These recaps should be inserted at the START of each PART section:

PART 2 RECAP:
  - Insert RIGHT AFTER '# PART 2: THE EVOLUTION TO 2.0' heading
  - BEFORE '## Interlude: The Whiteboard Archaeology'
  - Creates seamless transition from Part 1 to Part 2

PART 3 RECAP:
  - Insert RIGHT AFTER '# PART 3: THE EXTENSION ERA' heading  
  - BEFORE '## Interlude: The Invoice That Haunts Him'
  - Provides compressed summary of entire journey

COMPRESSION STRATEGY:
  - Part 2 recap: Medium compression of Part 1 (~150 tokens)
  - Part 3 recap: High compression of Part 1 (~80 tokens) + Medium of Part 2 (~120 tokens)
  - Gets progressively more high-level as you go back in time
  - Maintains humor and key milestones throughout
""")
