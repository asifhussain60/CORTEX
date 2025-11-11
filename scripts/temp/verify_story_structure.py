"""Verify story structure after refresh"""

with open('docs/awakening-of-cortex.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract headings
headings = [line for line in content.split('\n') if line.startswith('#')]

print("=" * 60)
print("STORY STRUCTURE VERIFICATION")
print("=" * 60)
print(f"\nTotal headings: {len(headings)}")
print(f"Total lines: {len(content.split(chr(10)))}")
print(f"Total words: {len(content.split())}")
print(f"Total characters: {len(content)}")

print("\n--- Heading Structure ---")
for i, heading in enumerate(headings, 1):
    level = len(heading) - len(heading.lstrip('#'))
    indent = "  " * (level - 1)
    title = heading.lstrip('#').strip()
    print(f"{i:2d}. {indent}{title}")

print("\n--- Content Validation ---")
required_sections = [
    "The Intern with Amnesia",
    "Dual-Hemisphere Brain Architecture",
    "LEFT HEMISPHERE",
    "RIGHT HEMISPHERE", 
    "CORPUS CALLOSUM",
    "Four-Tier Memory System",
    "TIER 0",
    "TIER 1",
    "TIER 2",
    "TIER 3",
    "Before vs After CORTEX"
]

for section in required_sections:
    if section.lower() in content.lower():
        print(f"✅ {section}")
    else:
        print(f"❌ MISSING: {section}")

print("\n" + "=" * 60)
print("✅ Story structure verification complete")
print("=" * 60)
