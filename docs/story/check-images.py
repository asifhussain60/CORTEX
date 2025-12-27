#!/usr/bin/env python3
"""Check all story chapter images for broken paths"""

import os
import re
from pathlib import Path

story_dir = Path("/Users/asifhussain/PROJECTS/CORTEX/docs/story")
os.chdir(story_dir)

print("🔍 Checking Story Images...")
print("=" * 60)

# Check embedded HTML images in markdown files
print("\n📋 Embedded HTML images in markdown files:")
print("-" * 60)

chapters = ["Prologue"] + [f"Chapter-{i:02d}" for i in range(1, 14)]
missing_images = []
found_images = []

for chapter in chapters:
    chapter_file = story_dir / chapter / "index.md"
    if chapter_file.exists():
        content = chapter_file.read_text()
        # Find all img src paths
        img_matches = re.findall(r'<img\s+src="([^"]+)"', content)
        
        if img_matches:
            print(f"\n{chapter} ({len(img_matches)} images):")
            for img_path in img_matches:
                # Convert relative path ../illustrations/... to absolute
                if img_path.startswith("../"):
                    actual_path = story_dir / img_path[3:]
                    if actual_path.exists():
                        print(f"  ✅ {img_path}")
                        found_images.append((chapter, img_path))
                    else:
                        print(f"  ❌ MISSING: {img_path}")
                        print(f"     Looking for: {actual_path}")
                        missing_images.append((chapter, img_path, str(actual_path)))

print("\n" + "=" * 60)
print(f"\n📊 Summary:")
print(f"  ✅ Found: {len(found_images)} images")
print(f"  ❌ Missing: {len(missing_images)} images")

if missing_images:
    print(f"\n⚠️  Missing images that need to be fixed:")
    for chapter, img_path, actual_path in missing_images:
        print(f"  - {chapter}: {img_path}")
else:
    print(f"\n🎉 All embedded images found!")
