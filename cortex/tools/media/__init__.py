"""
cortex/tools/media/__init__.py

Public API surface for the CORTEX media tag cleaner suite.

Usage::

    from cortex.tools.media import MediaTagCleaner
    cleaner = MediaTagCleaner(root=Path("Z:/MUSIC/Bollywood"), dry_run=True)
    results = cleaner.run()

AC_START: AC-MEDIA-2026-02-23-001
"""

from cortex.tools.media.filename_parser import FilenameParser, ParsedMetadata
from cortex.tools.media.filename_sanitizer import (
    FilenameAnalyzer,
    SanitizationResult,
    StudioDetector,
    ObscenityMorpher,
    ArtistExtractor,
)
from cortex.tools.media.media_scanner import MediaFile, MediaScanner
from cortex.tools.media.tag_cleaner import CleanResult, MediaTagCleaner
from cortex.tools.media.tag_writer import TagFields, TagWriterFactory

__all__ = [
    "FilenameParser",
    "ParsedMetadata",
    "MediaFile",
    "MediaScanner",
    "CleanResult",
    "MediaTagCleaner",
    "TagFields",
    "TagWriterFactory",
    "FilenameAnalyzer",
    "SanitizationResult",
    "StudioDetector",
    "ObscenityMorpher",
    "ArtistExtractor",
]
