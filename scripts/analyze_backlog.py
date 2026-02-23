#!/usr/bin/env python3
"""
Analyze _backlog folder and generate comprehensive before/after table.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cortex.tools.media.filename_sanitizer import FilenameAnalyzer

# Scan _backlog
backlog = Path("G:\\FLICKS\\_backlog")
video_extensions = {".mp4", ".mkv", ".m4v", ".avi", ".webm", ".mov"}

all_files = sorted([
    f for f in backlog.iterdir()
    if f.is_file() and f.suffix.lower() in video_extensions
])

print(f"Total files found: {len(all_files)}\n")

# Analyze each
analyzer = FilenameAnalyzer(studio_context="_backlog")
results = []

for video_file in all_files:
    result = analyzer.analyze(video_file.name)
    results.append(result)

# Show comprehensive table
print("=" * 140)
print(f"{'BEFORE (Current)':<50} | {'AFTER (Sanitized)':<40} | {'Studio':<12} | {'Conf':<5} | {'Changes':<20}")
print("=" * 140)

for r in results:
    changes_str = ", ".join(r.changes_made[:2]) if r.changes_made else "none"
    if len(changes_str) > 18:
        changes_str = changes_str[:15] + "..."
    
    studio_str = r.detected_studio if r.detected_studio else "-"
    conf_str = f"{r.confidence:.0%}"
    
    print(f"{r.current_filename:<50} | {r.sanitized_filename:<40} | {studio_str:<12} | {conf_str:<5} | {changes_str:<20}")

print("=" * 140)

# Summary stats
needs_rename = sum(1 for r in results if r.needs_rename)
studio_detected = sum(1 for r in results if r.detected_studio)
obscenity = sum(1 for r in results if "morphed_obscenity" in r.changes_made)
bloat = sum(1 for r in results if any(c in r.changes_made for c in ["removed_date", "removed_resolution", "removed_studio_suffix"]))

print(f"\n📊 SUMMARY:")
print(f"  • Total files: {len(results)}")
print(f"  • Need sanitization: {needs_rename} ({needs_rename/len(results)*100:.1f}%)")
print(f"  • Studios detected: {studio_detected}")
print(f"  • Obscenity morphed: {obscenity}")
print(f"  • Metadata bloat removed: {bloat}")
print(f"  • Average confidence: {sum(r.confidence for r in results)/len(results):.2%}")

# Show detailed examples
print("\n\n" + "=" * 140)
print("DETAILED EXAMPLES (with tags & artists)")
print("=" * 140)
print(f"{'File':<50} | {'Artists':<20} | {'Tags':<40}")
print("=" * 140)

for r in results[:15]:
    artists_str = ", ".join(r.artists) if r.artists else "-"
    if len(artists_str) > 18:
        artists_str = artists_str[:15] + "..."
    
    tags_str = ", ".join(r.tags[:2]) if r.tags else "-"
    if len(tags_str) > 38:
        tags_str = tags_str[:35] + "..."
    
    print(f"{r.sanitized_filename:<50} | {artists_str:<20} | {tags_str:<40}")
