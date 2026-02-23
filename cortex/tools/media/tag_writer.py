"""
cortex/tools/media/tag_writer.py

Abstract tag-writer protocol + concrete implementations for each container
format supported by *mutagen*.

Supported writers
-----------------
- :class:`MP4TagWriter`  — ``.mp4`` / ``.m4a`` (iTunes/AAC containers)
- :class:`MP3TagWriter`  — ``.mp3`` (ID3v2 tags via mutagen.id3)
- :class:`FLACTagWriter` — ``.flac`` (Vorbis comments)
- :class:`OggTagWriter`  — ``.ogg`` / ``.opus`` (Vorbis comments)
- :class:`GenericTagWriter` — everything else mutagen can open

Stale-tag clearing
------------------
For MP4 files Plex reads several redundant Apple fields that can shadow
the *real* Title tag.  The ``clear_stale`` flag (default ``True``) removes
them before writing the clean set.

CORE-011: All functions have type hints.
CORE-012: All public APIs have docstrings.
CORE-028: snake_case naming.

AC_START: AC-MEDIA-2026-02-23-003
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Protocol, Tuple

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Tag field container
# ---------------------------------------------------------------------------


@dataclass
class TagFields:
    """
    Canonical set of metadata fields to write.

    All fields except *title* are optional (``None`` means "do not write").

    Attributes:
        title:        Song / video title.
        artist:       Performing artist(s).
        album:        Album / playlist name.
        year:         Release year (4-digit string).
        genre:        Genre label.
        track_number: 1-based track number.
        comment:      Free-form comment; empty string clears existing comment.
    """

    title: str
    artist: Optional[str] = None
    album: Optional[str] = None
    year: Optional[str] = None
    genre: Optional[str] = None
    track_number: Optional[int] = None
    comment: Optional[str] = None


# ---------------------------------------------------------------------------
# Protocol (structural interface — no ABC required)
# ---------------------------------------------------------------------------


class TagWriter(Protocol):
    """
    Interface that every format-specific writer must satisfy.

    Implementations are returned by :class:`TagWriterFactory`.
    """

    def read_tags(self, path: Path) -> TagFields:
        """
        Read existing tags from *path*.

        Args:
            path: Path to the media file.

        Returns:
            :class:`TagFields` reflecting the current embedded metadata.
            Missing tags will be ``None``.
        """
        ...

    def write_tags(
        self,
        path: Path,
        fields: TagFields,
        clear_stale: bool = True,
    ) -> bool:
        """
        Write *fields* to *path*.

        Args:
            path:        Path to the media file.
            fields:      Metadata to embed.
            clear_stale: Remove potentially conflicting legacy tags first.

        Returns:
            ``True`` on success, ``False`` if the file could not be opened
            (e.g. corrupt / unsupported codec inside the container).
        """
        ...


# ---------------------------------------------------------------------------
# MP4 / M4A  (mutagen.mp4)
# ---------------------------------------------------------------------------

# Apple MP4 atom map  (atom → human name)
_MP4_FIELDS: Dict[str, str] = {
    "©nam": "title",
    "©ART": "artist",
    "©alb": "album",
    "©day": "year",
    "©gen": "genre",
    "trkn": "track_number",
    "©cmt": "comment",
}

# Atoms that carry redundant / stale metadata in Plex (Plex prefers ©nam)
_MP4_STALE_ATOMS: List[str] = [
    "tvsh",   # TV show name — bleeds into Plex title
    "tvnn",   # Network
    "tvsn",   # Season
    "tves",   # Episode
    "desc",   # Short description
    "ldes",   # Long description
    "©too",   # Encoding tool string
    "©enc",   # Encoded by
    "purl",   # Podcast feed URL
    "egid",   # Episode GUID
]


class MP4TagWriter:
    """
    Read/write metadata for ``.mp4`` and ``.m4a`` files using *mutagen*.

    Uses the iTunes/Apple atom naming scheme (``©nam``, ``©ART``, etc.).
    """

    def read_tags(self, path: Path) -> TagFields:
        """
        Read existing MP4 tags.

        Args:
            path: Path to an ``.mp4`` or ``.m4a`` file.

        Returns:
            :class:`TagFields` with current tag values.
        """
        from mutagen.mp4 import MP4  # noqa: PLC0415

        try:
            audio = MP4(str(path))
        except Exception:
            return TagFields(title="")

        tags = audio.tags or {}

        def _get(atom: str) -> Optional[str]:
            val = tags.get(atom)
            if val is None:
                return None
            if isinstance(val, list):
                val = val[0]
            if hasattr(val, "text"):  # mutagen FreeForm
                return str(val.text[0]) if val.text else None
            return str(val)

        track_raw = tags.get("trkn")
        track_number: Optional[int] = None
        if track_raw and isinstance(track_raw, list) and track_raw:
            trkn_val = track_raw[0]
            if isinstance(trkn_val, (list, tuple)) and trkn_val:
                track_number = int(trkn_val[0])
            else:
                try:
                    track_number = int(trkn_val)
                except (ValueError, TypeError):
                    pass

        return TagFields(
            title=_get("©nam") or "",
            artist=_get("©ART"),
            album=_get("©alb"),
            year=_get("©day"),
            genre=_get("©gen"),
            track_number=track_number,
            comment=_get("©cmt"),
        )

    def write_tags(
        self,
        path: Path,
        fields: TagFields,
        clear_stale: bool = True,
    ) -> bool:
        """
        Write *fields* to an MP4/M4A file.

        Args:
            path:        Target file.
            fields:      Metadata to embed.
            clear_stale: Remove legacy/redundant atoms before writing.

        Returns:
            ``True`` on success.
        """
        from mutagen.mp4 import MP4  # noqa: PLC0415

        try:
            audio = MP4(str(path))
        except Exception as exc:
            logger.warning("Cannot open %s: %s", path, exc)
            return False

        if audio.tags is None:
            audio.add_tags()

        if clear_stale:
            for atom in _MP4_STALE_ATOMS:
                audio.tags.pop(atom, None)

        # Write clean fields
        audio.tags["©nam"] = [fields.title]

        if fields.artist is not None:
            audio.tags["©ART"] = [fields.artist]
        if fields.album is not None:
            audio.tags["©alb"] = [fields.album]
        if fields.year is not None:
            audio.tags["©day"] = [fields.year]
        if fields.genre is not None:
            audio.tags["©gen"] = [fields.genre]
        if fields.track_number is not None:
            audio.tags["trkn"] = [(fields.track_number, 0)]
        if fields.comment is not None:
            audio.tags["©cmt"] = [fields.comment]

        try:
            audio.save()
            return True
        except Exception as exc:
            logger.error("Failed to save %s: %s", path, exc)
            return False


# ---------------------------------------------------------------------------
# MP3  (mutagen.id3)
# ---------------------------------------------------------------------------

class MP3TagWriter:
    """
    Read/write ID3v2 tags for ``.mp3`` files using *mutagen.id3*.
    """

    def read_tags(self, path: Path) -> TagFields:
        """Read ID3 tags from an MP3 file."""
        from mutagen.id3 import ID3, ID3NoHeaderError  # noqa: PLC0415

        try:
            tags = ID3(str(path))
        except ID3NoHeaderError:
            return TagFields(title="")
        except Exception:
            return TagFields(title="")

        def _text(frame_id: str) -> Optional[str]:
            frame = tags.get(frame_id)
            if frame is None:
                return None
            text = getattr(frame, "text", None)
            if text:
                return str(text[0])
            return None

        track_raw = _text("TRCK")
        track_number: Optional[int] = None
        if track_raw:
            try:
                track_number = int(track_raw.split("/")[0])
            except ValueError:
                pass

        return TagFields(
            title=_text("TIT2") or "",
            artist=_text("TPE1"),
            album=_text("TALB"),
            year=_text("TDRC"),
            genre=_text("TCON"),
            track_number=track_number,
            comment=_text("COMM"),
        )

    def write_tags(
        self,
        path: Path,
        fields: TagFields,
        clear_stale: bool = True,
    ) -> bool:
        """Write ID3 tags to an MP3 file."""
        from mutagen.id3 import (  # noqa: PLC0415
            ID3,
            ID3NoHeaderError,
            TALB,
            TCON,
            TDRC,
            TIT2,
            TPE1,
            TRCK,
        )

        try:
            try:
                tags = ID3(str(path))
            except ID3NoHeaderError:
                tags = ID3()
        except Exception as exc:
            logger.warning("Cannot open ID3 on %s: %s", path, exc)
            return False

        if clear_stale:
            for stale in ("TCOP", "TPUB", "TRSN", "TRSO", "TENC", "TSSE"):
                tags.delall(stale)

        tags.add(TIT2(encoding=3, text=[fields.title]))
        if fields.artist is not None:
            tags.add(TPE1(encoding=3, text=[fields.artist]))
        if fields.album is not None:
            tags.add(TALB(encoding=3, text=[fields.album]))
        if fields.year is not None:
            tags.add(TDRC(encoding=3, text=[fields.year]))
        if fields.genre is not None:
            tags.add(TCON(encoding=3, text=[fields.genre]))
        if fields.track_number is not None:
            tags.add(TRCK(encoding=3, text=[str(fields.track_number)]))

        try:
            tags.save(str(path), v2_version=3)
            return True
        except Exception as exc:
            logger.error("Failed to save ID3 on %s: %s", path, exc)
            return False


# ---------------------------------------------------------------------------
# FLAC  (mutagen.flac)
# ---------------------------------------------------------------------------

class FLACTagWriter:
    """Read/write Vorbis comments for ``.flac`` files."""

    def read_tags(self, path: Path) -> TagFields:
        """Read Vorbis comments from a FLAC file."""
        from mutagen.flac import FLAC  # noqa: PLC0415

        try:
            audio = FLAC(str(path))
        except Exception:
            return TagFields(title="")

        def _get(key: str) -> Optional[str]:
            val = audio.get(key.lower())
            return val[0] if val else None

        track_raw = _get("tracknumber")
        track_number: Optional[int] = None
        if track_raw:
            try:
                track_number = int(track_raw.split("/")[0])
            except ValueError:
                pass

        return TagFields(
            title=_get("title") or "",
            artist=_get("artist"),
            album=_get("album"),
            year=_get("date"),
            genre=_get("genre"),
            track_number=track_number,
            comment=_get("comment"),
        )

    def write_tags(
        self,
        path: Path,
        fields: TagFields,
        clear_stale: bool = True,
    ) -> bool:
        """Write Vorbis comments to a FLAC file."""
        from mutagen.flac import FLAC  # noqa: PLC0415

        try:
            audio = FLAC(str(path))
        except Exception as exc:
            logger.warning("Cannot open FLAC %s: %s", path, exc)
            return False

        audio["title"] = [fields.title]
        if fields.artist is not None:
            audio["artist"] = [fields.artist]
        if fields.album is not None:
            audio["album"] = [fields.album]
        if fields.year is not None:
            audio["date"] = [fields.year]
        if fields.genre is not None:
            audio["genre"] = [fields.genre]
        if fields.track_number is not None:
            audio["tracknumber"] = [str(fields.track_number)]
        if fields.comment is not None:
            audio["comment"] = [fields.comment]

        try:
            audio.save()
            return True
        except Exception as exc:
            logger.error("Failed to save FLAC %s: %s", path, exc)
            return False


# ---------------------------------------------------------------------------
# OGG / OPUS  (mutagen.oggvorbis / mutagen.oggopus)
# ---------------------------------------------------------------------------

class OggTagWriter:
    """Read/write Vorbis comments for ``.ogg`` and ``.opus`` files."""

    def read_tags(self, path: Path) -> TagFields:
        """Read tags from an OGG/Opus file."""
        from mutagen import File as MutagenFile  # noqa: PLC0415

        try:
            audio = MutagenFile(str(path))
            if audio is None:
                return TagFields(title="")
        except Exception:
            return TagFields(title="")

        tags = audio.tags or {}

        def _get(key: str) -> Optional[str]:
            val = tags.get(key.lower())
            return val[0] if val else None

        return TagFields(
            title=_get("title") or "",
            artist=_get("artist"),
            album=_get("album"),
            year=_get("date"),
            genre=_get("genre"),
            comment=_get("comment"),
        )

    def write_tags(
        self,
        path: Path,
        fields: TagFields,
        clear_stale: bool = True,
    ) -> bool:
        """Write tags to an OGG/Opus file."""
        from mutagen import File as MutagenFile  # noqa: PLC0415

        try:
            audio = MutagenFile(str(path))
            if audio is None:
                return False
        except Exception as exc:
            logger.warning("Cannot open OGG %s: %s", path, exc)
            return False

        audio["title"] = [fields.title]
        if fields.artist is not None:
            audio["artist"] = [fields.artist]
        if fields.album is not None:
            audio["album"] = [fields.album]
        if fields.year is not None:
            audio["date"] = [fields.year]
        if fields.genre is not None:
            audio["genre"] = [fields.genre]
        if fields.comment is not None:
            audio["comment"] = [fields.comment]

        try:
            audio.save()
            return True
        except Exception as exc:
            logger.error("Failed to save OGG %s: %s", path, exc)
            return False


# ---------------------------------------------------------------------------
# Generic fallback using mutagen.File()
# ---------------------------------------------------------------------------

class GenericTagWriter:
    """
    Fallback writer for any format mutagen can auto-detect.

    Used for ``.m4a``, ``.aac``, ``.wma``, ``.ape``, ``.aiff``, etc.
    """

    def read_tags(self, path: Path) -> TagFields:
        """Attempt to read tags from any mutagen-supported file."""
        from mutagen import File as MutagenFile  # noqa: PLC0415

        try:
            audio = MutagenFile(str(path), easy=True)
            if audio is None:
                return TagFields(title="")
        except Exception:
            return TagFields(title="")

        tags = audio.tags or {}

        def _get(key: str) -> Optional[str]:
            val = tags.get(key)
            return val[0] if val else None

        return TagFields(
            title=_get("title") or "",
            artist=_get("artist"),
            album=_get("album"),
            year=_get("date"),
            genre=_get("genre"),
        )

    def write_tags(
        self,
        path: Path,
        fields: TagFields,
        clear_stale: bool = True,
    ) -> bool:
        """Write tags to a mutagen-detected file using EasyTags."""
        from mutagen import File as MutagenFile  # noqa: PLC0415

        try:
            audio = MutagenFile(str(path), easy=True)
            if audio is None:
                return False
        except Exception as exc:
            logger.warning("Cannot open %s: %s", path, exc)
            return False

        if audio.tags is None:
            audio.add_tags()

        audio.tags["title"] = [fields.title]
        if fields.artist is not None:
            audio.tags["artist"] = [fields.artist]
        if fields.album is not None:
            audio.tags["album"] = [fields.album]
        if fields.year is not None:
            audio.tags["date"] = [fields.year]
        if fields.genre is not None:
            audio.tags["genre"] = [fields.genre]

        try:
            audio.save()
            return True
        except Exception as exc:
            logger.error("Failed to save %s: %s", path, exc)
            return False


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

_EXT_TO_WRITER: Dict[str, object] = {
    ".mp4": MP4TagWriter(),
    ".m4a": MP4TagWriter(),
    ".mp3": MP3TagWriter(),
    ".flac": FLACTagWriter(),
    ".ogg": OggTagWriter(),
    ".opus": OggTagWriter(),
    ".aac": GenericTagWriter(),
    ".wav": GenericTagWriter(),
    ".wma": GenericTagWriter(),
    ".ape": GenericTagWriter(),
    ".aiff": GenericTagWriter(),
}


class TagWriterFactory:
    """
    Returns the correct :class:`TagWriter` implementation for a given file.

    Examples::

        writer = TagWriterFactory.for_file(Path("song.mp4"))
        fields = writer.read_tags(Path("song.mp4"))
    """

    @staticmethod
    def for_file(path: Path) -> Optional[TagWriter]:
        """
        Return the appropriate writer for *path*'s extension.

        Args:
            path: Path to a media file.

        Returns:
            A :class:`TagWriter` instance, or ``None`` if the extension is
            unsupported.
        """
        ext = path.suffix.lower()
        return _EXT_TO_WRITER.get(ext)  # type: ignore[return-value]


# AC_COMPLETE: AC-MEDIA-2026-02-23-003 ✅
