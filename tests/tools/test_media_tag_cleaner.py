"""
Tests for media tag cleaner suite.

AC_START: AC-MEDIA-2026-02-23-001
Tests: MediaTagCleaner, FilenameParser, TagWriter, MediaScanner
CORE-008: TDD mandatory — tests written before implementation.
"""

from __future__ import annotations

import re
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# FilenameParser
# ---------------------------------------------------------------------------
from cortex.tools.media.filename_parser import FilenameParser, ParsedMetadata


class TestFilenameParserArtistDashTitle:
    """'Artist - Title' pattern — most common Bollywood naming."""

    def test_simple_artist_dash_title(self) -> None:
        meta = FilenameParser.parse("Badshah - Paani Paani")
        assert meta.title == "Paani Paani"
        assert meta.artist == "Badshah"

    def test_multi_word_artist_and_title(self) -> None:
        meta = FilenameParser.parse("Arijit Singh - Tum Hi Ho")
        assert meta.title == "Tum Hi Ho"
        assert meta.artist == "Arijit Singh"

    def test_multiple_artists_comma_separated(self) -> None:
        meta = FilenameParser.parse("Badshah, Payal Dev - Song Name")
        assert meta.title == "Song Name"
        assert meta.artist == "Badshah, Payal Dev"


class TestFilenameParserTrackPrefix:
    """'01. Artist - Title' pattern — numbered tracks."""

    def test_track_number_extracted(self) -> None:
        meta = FilenameParser.parse("01. Badshah - Paani Paani")
        assert meta.track_number == 1
        assert meta.artist == "Badshah"
        assert meta.title == "Paani Paani"

    def test_two_digit_track(self) -> None:
        meta = FilenameParser.parse("12. Arijit Singh - Tum Hi Ho")
        assert meta.track_number == 12
        assert meta.title == "Tum Hi Ho"


class TestFilenameParserTitleOnly:
    """Filename has no dash — full filename becomes title."""

    def test_plain_title(self) -> None:
        meta = FilenameParser.parse("Aadat Bollywood Classic")
        assert meta.title == "Aadat Bollywood Classic"
        assert meta.artist is None

    def test_single_word(self) -> None:
        meta = FilenameParser.parse("Kaho")
        assert meta.title == "Kaho"

    def test_suffix_noise_stripped(self) -> None:
        """Trailing noise words like 'Song', 'HD', '1080p' are stripped from title."""
        meta = FilenameParser.parse("Aaj Ki Raat Song")
        assert "Song" not in meta.title

    def test_extension_not_included(self) -> None:
        """Passing a stem (no extension) is fine; extension handled outside."""
        meta = FilenameParser.parse("Akhiyaan Gulaab")
        assert ".mp4" not in meta.title


class TestFilenameParserEdgeCases:
    """Edge cases and robustness."""

    def test_leading_trailing_spaces_stripped(self) -> None:
        meta = FilenameParser.parse("  Badshah  -  Paani Paani  ")
        assert meta.title == "Paani Paani"
        assert meta.artist == "Badshah"

    def test_dash_in_title_not_split_again(self) -> None:
        meta = FilenameParser.parse("Badshah - Paani-Paani")
        assert meta.title == "Paani-Paani"
        assert meta.artist == "Badshah"

    def test_parsed_metadata_is_dataclass(self) -> None:
        meta = FilenameParser.parse("Test - Title")
        assert isinstance(meta, ParsedMetadata)

    def test_from_path_uses_stem(self) -> None:
        p = Path("Z:/MUSIC/Bollywood Hits/Badshah - Paani Paani.mp4")
        meta = FilenameParser.from_path(p)
        assert meta.title == "Paani Paani"
        assert meta.artist == "Badshah"


# ---------------------------------------------------------------------------
# MediaScanner
# ---------------------------------------------------------------------------
from cortex.tools.media.media_scanner import MediaFile, MediaScanner


class TestMediaScanner:
    """MediaScanner — recursive file discovery."""

    def _make_tmp_tree(self, tmp_path: Path) -> None:
        (tmp_path / "subA").mkdir()
        (tmp_path / "subB").mkdir()
        (tmp_path / "subA" / "song1.mp4").write_bytes(b"")
        (tmp_path / "subA" / "song2.mp3").write_bytes(b"")
        (tmp_path / "subB" / "song3.mp4").write_bytes(b"")
        (tmp_path / "readme.txt").write_bytes(b"")  # should be excluded

    def test_scans_all_supported_extensions(self, tmp_path: Path) -> None:
        self._make_tmp_tree(tmp_path)
        scanner = MediaScanner(tmp_path)
        files = scanner.scan()
        names = {f.path.name for f in files}
        assert "song1.mp4" in names
        assert "song2.mp3" in names
        assert "song3.mp4" in names

    def test_excludes_unsupported_extension(self, tmp_path: Path) -> None:
        self._make_tmp_tree(tmp_path)
        scanner = MediaScanner(tmp_path)
        files = scanner.scan()
        names = {f.path.name for f in files}
        assert "readme.txt" not in names

    def test_custom_extensions(self, tmp_path: Path) -> None:
        self._make_tmp_tree(tmp_path)
        scanner = MediaScanner(tmp_path, extensions={".mp4"})
        files = scanner.scan()
        names = {f.path.name for f in files}
        assert "song1.mp4" in names
        assert "song2.mp3" not in names  # excluded by custom filter

    def test_media_file_has_folder_name(self, tmp_path: Path) -> None:
        self._make_tmp_tree(tmp_path)
        scanner = MediaScanner(tmp_path)
        files = scanner.scan()
        sub_a_files = [f for f in files if f.path.name == "song1.mp4"]
        assert sub_a_files[0].folder_name == "subA"

    def test_returns_media_file_instances(self, tmp_path: Path) -> None:
        self._make_tmp_tree(tmp_path)
        scanner = MediaScanner(tmp_path)
        files = scanner.scan()
        for mf in files:
            assert isinstance(mf, MediaFile)

    def test_empty_directory_returns_empty(self, tmp_path: Path) -> None:
        scanner = MediaScanner(tmp_path)
        assert scanner.scan() == []


# ---------------------------------------------------------------------------
# TagWriter (unit tests using stubs — no real files touched)
# ---------------------------------------------------------------------------
from cortex.tools.media.tag_writer import TagFields, TagWriterFactory


class TestTagWriterFactory:
    """TagWriterFactory returns correct writer per extension."""

    def test_mp4_extension(self, tmp_path: Path) -> None:
        f = tmp_path / "test.mp4"
        f.write_bytes(b"")
        writer = TagWriterFactory.for_file(f)
        assert writer is not None

    def test_mp3_extension(self, tmp_path: Path) -> None:
        f = tmp_path / "test.mp3"
        f.write_bytes(b"")
        writer = TagWriterFactory.for_file(f)
        assert writer is not None

    def test_unknown_extension_returns_none(self, tmp_path: Path) -> None:
        f = tmp_path / "test.xyz"
        f.write_bytes(b"")
        writer = TagWriterFactory.for_file(f)
        assert writer is None


class TestTagFields:
    """TagFields dataclass construction."""

    def test_defaults_are_none(self) -> None:
        tf = TagFields(title="Test")
        assert tf.artist is None
        assert tf.album is None
        assert tf.year is None
        assert tf.genre is None
        assert tf.track_number is None
        assert tf.comment is None

    def test_fully_populated(self) -> None:
        tf = TagFields(
            title="Paani Paani",
            artist="Badshah",
            album="Bollywood Hits",
            year="2021",
            genre="Bollywood",
            track_number=3,
            comment="",
        )
        assert tf.title == "Paani Paani"
        assert tf.track_number == 3


# ---------------------------------------------------------------------------
# MediaTagCleaner (integration — uses real mutagen on temp MP4 stubs)
# ---------------------------------------------------------------------------
from cortex.tools.media.tag_cleaner import CleanResult, MediaTagCleaner


class TestMediaTagCleanerDryRun:
    """Dry-run mode — no files mutated."""

    def test_dry_run_returns_results(self, tmp_path: Path) -> None:
        """Dry-run must return CleanResult list without raising."""
        cleaner = MediaTagCleaner(tmp_path, dry_run=True)
        results = cleaner.run()
        assert isinstance(results, list)

    def test_dry_run_produces_no_side_effects(self, tmp_path: Path) -> None:
        """No actual tag writes in dry-run."""
        (tmp_path / "song.mp4").write_bytes(b"")  # zero-byte stub
        cleaner = MediaTagCleaner(tmp_path, dry_run=True)
        with patch("cortex.tools.media.tag_cleaner.TagWriterFactory") as mock_factory:
            mock_writer = MagicMock()
            mock_factory.for_file.return_value = mock_writer
            cleaner.run()
            mock_writer.write_tags.assert_not_called()


class TestMediaTagCleanerResults:
    """CleanResult contract."""

    def test_clean_result_is_dataclass(self) -> None:
        r = CleanResult(
            path=Path("test.mp4"),
            success=True,
            old_title="old",
            new_title="new",
            changes={"title": ("old", "new")},
        )
        assert r.success is True
        assert r.error is None

    def test_clean_result_failure_carries_error(self) -> None:
        r = CleanResult(
            path=Path("bad.mp4"),
            success=False,
            old_title=None,
            new_title="",
            changes={},
            error="mutagen parse failed",
        )
        assert r.success is False
        assert "mutagen" in (r.error or "")


class TestMediaTagCleanerConfig:
    """Configuration surface of MediaTagCleaner."""

    def test_default_uses_folder_as_album(self, tmp_path: Path) -> None:
        cleaner = MediaTagCleaner(tmp_path)
        assert cleaner.use_folder_as_album is True

    def test_can_disable_folder_as_album(self, tmp_path: Path) -> None:
        cleaner = MediaTagCleaner(tmp_path, use_folder_as_album=False)
        assert cleaner.use_folder_as_album is False

    def test_dry_run_default_false(self, tmp_path: Path) -> None:
        cleaner = MediaTagCleaner(tmp_path)
        assert cleaner.dry_run is False

    def test_clear_stale_default_true(self, tmp_path: Path) -> None:
        cleaner = MediaTagCleaner(tmp_path)
        assert cleaner.clear_stale_tags is True


# ---------------------------------------------------------------------------
# ParsedMetadata <-> TagFields bridge
# ---------------------------------------------------------------------------
class TestParsedMetadataToTagFields:
    """ParsedMetadata.to_tag_fields() produces correct TagFields."""

    def test_artist_title_mapped(self) -> None:
        meta = FilenameParser.parse("Badshah - Paani Paani")
        tf = meta.to_tag_fields(album="Bollywood Hits")
        assert tf.title == "Paani Paani"
        assert tf.artist == "Badshah"
        assert tf.album == "Bollywood Hits"

    def test_no_artist_filename_as_artist(self) -> None:
        meta = FilenameParser.parse("Aadat Bollywood Classic")
        tf = meta.to_tag_fields()
        assert tf.title == "Aadat Bollywood Classic"
        # artist may be None when not parseable
        assert tf.artist is None

    def test_track_number_propagated(self) -> None:
        meta = FilenameParser.parse("03. Arijit Singh - Tum Hi Ho")
        tf = meta.to_tag_fields()
        assert tf.track_number == 3
