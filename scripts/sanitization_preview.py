#!/usr/bin/env python3
"""
Generate markdown-formatted sanitization preview table.
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

# Analyze each
analyzer = FilenameAnalyzer(studio_context="_backlog")
results = []

for video_file in all_files:
    result = analyzer.analyze(video_file.name)
    results.append(result)

# Generate markdown table
print("# _backlog Sanitization Preview")
print()
print(f"**Total Files:** {len(results)} | **Need Sanitization:** {sum(1 for r in results if r.needs_rename)} ({sum(1 for r in results if r.needs_rename)/len(results)*100:.1f}%)")
print()

print("| Before (Current) | After (Sanitized) | Studio | Artists | Tags | ✓ |")
print("|---|---|---|---|---|---|")

for r in results:
    before = r.current_filename[:40] if len(r.current_filename) > 40 else r.current_filename
    after = r.sanitized_filename[:40] if len(r.sanitized_filename) > 40 else r.sanitized_filename
    studio = r.detected_studio or "-"
    artists = ", ".join(r.artists[:2]) if r.artists else "-"
    tags = ", ".join(r.tags[:2]) if r.tags else "-"
    confidence = f"{r.confidence:.0%}"
    
    print(f"| {before} | {after} | {studio} | {artists} | {tags} | {confidence} |")

print()
print("## Summary Statistics")
print()
needs_rename = sum(1 for r in results if r.needs_rename)
studio_detected = sum(1 for r in results if r.detected_studio)
obscenity = sum(1 for r in results if "morphed_obscenity" in r.changes_made)
bloat = sum(1 for r in results if any(c in r.changes_made for c in ["removed_date", "removed_resolution", "removed_studio_suffix"]))

print(f"- **Total files:** {len(results)}")
print(f"- **Need sanitization:** {needs_rename} ({needs_rename/len(results)*100:.1f}%)")
print(f"- **Already clean:** {len(results) - needs_rename}")
print(f"- **Studios detected:** {studio_detected}")
print(f"- **Obscenity morphed:** {obscenity}")
print(f"- **Metadata bloat removed:** {bloat}")
print(f"- **Average confidence:** {sum(r.confidence for r in results)/len(results):.1%}")

print()
print("## Details")
print()

for i, r in enumerate(results, 1):
    if r.needs_rename or r.artists or r.changes_made:
        print(f"**{i}. {r.current_filename}**")
        print(f"   - Sanitized: `{r.sanitized_filename}`")
        if r.detected_studio:
            print(f"   - Studio: {r.detected_studio}")
        if r.artists:
            print(f"   - Artists: {', '.join(r.artists)}")
        if r.tags:
            print(f"   - Tags: {', '.join(r.tags)}")
        if r.changes_made:
            print(f"   - Changes: {', '.join(r.changes_made)}")
        print(f"   - Confidence: {r.confidence:.0%}")
        print()
