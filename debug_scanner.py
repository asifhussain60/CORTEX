#!/usr/bin/env python3
"""Debug: Check if VideoLibraryScanner finds files in Wicked."""

from pathlib import Path
from cortex.tools.media.video_library_scanner import VideoLibraryScanner

scanner = VideoLibraryScanner(root=Path(r"G:\FLICKS\Wicked"))
files = scanner.scan()

print(f"Scanner found {len(files)} files")
for f in files[:5]:
    print(f"  - {f.filename_stem}{f.extension} (studio: {f.studio})")
