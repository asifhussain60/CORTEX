"""
cortex/tools/media/filename_parser.py

Parse media filenames into structured metadata for tag writing.

Supports common Bollywood / general music naming conventions:
  • ``Artist - Title``
  • ``Track. Artist - Title``   e.g. ``01. Badshah - Paani Paani``
  • ``Artist, Artist2 - Title`` (multiple artists)
  • ``Title only``              (no dash separator)

CORE-011: All functions have type hints.
CORE-012: All public APIs have docstrings.
CORE-028: snake_case naming.

AC_START: AC-MEDIA-2026-02-23-001
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Noise-word suffixes that pollute titles when absent an artist separator
# ---------------------------------------------------------------------------
_NOISE_SUFFIXES: tuple[str, ...] = (
    r"\bSong\b",
    r"\bHD\b",
    r"\b1080p\b",
    r"\b720p\b",
    r"\b4K\b",
    r"\bOfficial\b",
    r"\bVideo\b",
    r"\bLyrics\b",
    r"\bFull\s+Song\b",
    r"\bAudio\b",
    r"\bMV\b",
)

_NOISE_RE = re.compile(
    r"(?:" + "|".join(_NOISE_SUFFIXES) + r")\s*$",
    re.IGNORECASE,
)

# Pattern: optional ``01. `` prefix, then ``Artist - Title``
# The title-half must contain at least one non-digit character so that
# ``"Guru Randhawa Song - 1"`` is NOT split into artist/track but treated as
# a title-only string (preventing "1" from becoming the song title).
_TRACK_ARTIST_TITLE_RE = re.compile(
    r"^(?:(\d+)\.\s+)?(.+?)\s+-\s+(\S.*[^\d\s].*)$"
)


@dataclass
class ParsedMetadata:
    """
    Structured metadata derived from a media filename stem.

    Attributes:
        title:        Song / video title (always populated).
        artist:       Performing artist(s) or ``None`` when not detected.
        track_number: Integer track number or ``None``.
        album:        Album name — populated externally (e.g. folder name).
        year:         Release year string or ``None``.
        genre:        Genre string or ``None``.
        comment:      Free-form comment or ``None``.
    """

    title: str
    artist: Optional[str] = None
    track_number: Optional[int] = None
    album: Optional[str] = None
    year: Optional[str] = None
    genre: Optional[str] = None
    comment: Optional[str] = None

    # -----------------------------------------------------------------------
    def to_tag_fields(self, album: Optional[str] = None) -> "TagFields":
        """
        Convert to :class:`~cortex.tools.media.tag_writer.TagFields`.

        Args:
            album: Override album name; falls back to ``self.album``.

        Returns:
            :class:`~cortex.tools.media.tag_writer.TagFields` instance.
        """
        # Avoid circular import — import lazily
        from cortex.tools.media.tag_writer import TagFields  # noqa: PLC0415

        return TagFields(
            title=self.title,
            artist=self.artist,
            album=album or self.album,
            year=self.year,
            genre=self.genre,
            track_number=self.track_number,
            comment=self.comment,
        )


class FilenameParser:
    """
    Stateless parser that converts a filename stem into :class:`ParsedMetadata`.

    All methods are class-level; no instance is required.

    Examples::

        meta = FilenameParser.parse("Badshah - Paani Paani")
        # → ParsedMetadata(title="Paani Paani", artist="Badshah")

        meta = FilenameParser.from_path(Path("song.mp4"))
        # → parses the stem "song"
    """

    @classmethod
    def parse(cls, stem: str) -> ParsedMetadata:
        """
        Parse a filename stem (no extension) into structured metadata.

        Detection order:

        1. Strip leading/trailing whitespace from *stem*.
        2. Try ``[track. ]Artist - Title`` regex.
        3. Fall back to title-only (full stem, noise-stripped).

        Args:
            stem: The filename without its extension.

        Returns:
            :class:`ParsedMetadata` with at least ``title`` populated.
        """
        stem = stem.strip()
        match = _TRACK_ARTIST_TITLE_RE.match(stem)
        if match:
            raw_track, raw_artist, raw_title = match.groups()
            track_number: Optional[int] = int(raw_track) if raw_track else None
            artist = raw_artist.strip() or None
            title = raw_title.strip()
            return ParsedMetadata(
                title=title,
                artist=artist,
                track_number=track_number,
            )

        # Title-only fallback: strip trailing noise words
        clean_title = _NOISE_RE.sub("", stem).strip()
        if not clean_title:
            clean_title = stem  # guard against over-stripping

        return ParsedMetadata(title=clean_title, artist=None)

    @classmethod
    def from_path(cls, path: Path) -> ParsedMetadata:
        """
        Parse the stem of a file path.

        Args:
            path: File path — the ``stem`` attribute is used (no extension).

        Returns:
            :class:`ParsedMetadata` derived from the filename stem.
        """
        return cls.parse(path.stem)


# Avoid circular import at module level — TagFields imported inside to_tag_fields
try:
    from cortex.tools.media.tag_writer import TagFields  # noqa: F401 (re-export hint)
except ImportError:
    pass


# AC_COMPLETE: AC-MEDIA-2026-02-23-001 ✅
