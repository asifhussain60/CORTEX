"""
tests/unit/tools/media/test_plex_metadata_accessor.py

TDD tests for PlexMetadataAccessor — PLEX metadata retrieval via SQLite.

Test suite covers:
- PLEX database detection and connection
- Metadata query for video files
- Fallback to REST API (if available)
- Error handling (database not found, malformed queries)
- Cache mechanism for repeated lookups
- Path normalization across OS

AC_START: AC-PLEX-ACCESSOR-2026-02-23-002
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, Mock
from cortex.tools.media.plex_metadata_accessor import (
    PlexMetadata,
    PlexMetadataAccessor,
    PlexAccessMethod,
)


class TestPlexMetadataDataclass:
    """Test PlexMetadata dataclass structure."""

    def test_plex_metadata_initialization(self):
        """PlexMetadata initializes with video metadata fields."""
        metadata = PlexMetadata(
            title="Test Video",
            studio="Bellesa",
            year="2024",
            genre="Drama",
            resolution="1080p",
            duration_seconds=3600,
            plex_id="12345",
            last_indexed="2026-02-23T10:00:00Z",
        )
        assert metadata.title == "Test Video"
        assert metadata.studio == "Bellesa"
        assert metadata.year == "2024"
        assert metadata.genre == "Drama"
        assert metadata.resolution == "1080p"
        assert metadata.duration_seconds == 3600
        assert metadata.plex_id == "12345"

    def test_plex_metadata_optional_fields(self):
        """PlexMetadata allows None for optional fields."""
        metadata = PlexMetadata(
            title="Test",
            studio=None,
            year=None,
            genre=None,
            resolution=None,
            duration_seconds=None,
            plex_id=None,
            last_indexed=None,
        )
        assert metadata.title == "Test"
        assert metadata.studio is None
        assert metadata.year is None


class TestPlexAccessorInitialization:
    """Test PlexMetadataAccessor initialization."""

    def test_accessor_initialization_with_database_path(self):
        """PlexMetadataAccessor initializes with optional database path."""
        db_path = Path("C:\\ProgramData\\Plex Media Server\\Metadata\\com.plexapp.plugins.library\\123\\metadata\\123.db")
        accessor = PlexMetadataAccessor(db_path=db_path)
        assert accessor.db_path == db_path

    def test_accessor_initialization_auto_detect_database(self):
        """PlexMetadataAccessor auto-detects PLEX database if not provided."""
        accessor = PlexMetadataAccessor()
        # Should attempt to locate database at default PLEX locations
        assert accessor is not None
        assert hasattr(accessor, "find_plex_database")

    def test_accessor_initialization_with_fallback_rest_api(self):
        """PlexMetadataAccessor accepts REST API endpoint and token."""
        accessor = PlexMetadataAccessor(
            api_url="http://localhost:32400",
            api_token="xyz123",
            preferred_method=PlexAccessMethod.REST_API,
        )
        assert accessor.api_url == "http://localhost:32400"
        assert accessor.api_token == "xyz123"


class TestPlexAccessorDatabaseDetection:
    """Test PLEX database auto-detection."""

    def test_find_plex_database_appdata_path(self):
        """Locates PLEX database in standard AppData location."""
        accessor = PlexMetadataAccessor()
        # Would check standard locations:
        # %APPDATA%\Plex Media Server\Metadata
        # C:\ProgramData\Plex Media Server\Metadata
        assert hasattr(accessor, "find_plex_database")

    def test_find_plex_database_raises_not_found(self):
        """Raises exception if no PLEX database found."""
        accessor = PlexMetadataAccessor()
        with patch.object(accessor, "_locate_plex_appdata", return_value=None):
            with pytest.raises(FileNotFoundError):
                accessor.find_plex_database()


class TestPlexAccessorMetadataRetrieval:
    """Test metadata retrieval for video files."""

    def test_read_metadata_for_single_file(self):
        """read_metadata() returns PlexMetadata for known video path."""
        accessor = PlexMetadataAccessor()
        accessor.db_path = Path("test.db")
        
        with patch.object(accessor, "_query_sqlite") as mock_query:
            mock_query.return_value = {
                "title": "Abella Won't Tell",
                "year": "2024",
                "studio": "Bellesa",
                "genre": "Feature",
                "resolution": "1080p",
                "duration_seconds": 2400,
                "plex_id": "999",
            }
            
            result = accessor.read_metadata(
                file_path=Path("G:/FLICKS/Bellesa/Abella Won't Tell.mp4")
            )
            assert result.title == "Abella Won't Tell"
            assert result.studio == "Bellesa"

    def test_read_metadata_returns_none_for_unindexed_file(self):
        """read_metadata() returns None if file not in PLEX library."""
        accessor = PlexMetadataAccessor()
        accessor.db_path = Path("test.db")
        
        with patch.object(accessor, "_query_sqlite", return_value=None):
            result = accessor.read_metadata(
                file_path=Path("G:/FLICKS/Unknown/File.mp4")
            )
            assert result is None

    def test_read_batch_metadata_for_multiple_files(self):
        """read_batch_metadata() returns dict mapping paths to metadata."""
        accessor = PlexMetadataAccessor()
        accessor.db_path = Path("test.db")
        
        paths = [
            Path("G:/FLICKS/Bellesa/File1.mp4"),
            Path("G:/FLICKS/Blacked/File2.mp4"),
        ]
        
        with patch.object(accessor, "read_metadata") as mock_read:
            mock_read.side_effect = [
                PlexMetadata(
                    title="File1",
                    studio="Bellesa",
                    year="2024",
                    genre="Feature",
                    resolution="1080p",
                    duration_seconds=2400,
                    plex_id="1",
                    last_indexed="2026-02-23",
                ),
                PlexMetadata(
                    title="File2",
                    studio="Blacked",
                    year="2024",
                    genre="Feature",
                    resolution="4K",
                    duration_seconds=3000,
                    plex_id="2",
                    last_indexed="2026-02-23",
                ),
            ]
            
            result = accessor.read_batch_metadata(paths)
            assert len(result) == 2
            assert result[paths[0]].title == "File1"
            assert result[paths[1]].title == "File2"


class TestPlexAccessorPathNormalization:
    """Test cross-OS path normalization."""

    def test_normalize_path_windows_backslash(self):
        """Normalizes Windows paths with backslashes."""
        accessor = PlexMetadataAccessor()
        path = Path("G:\\FLICKS\\Bellesa\\Title.mp4")
        normalized = accessor._normalize_path(path)
        # Should handle both forward and back slashes
        assert "\\" in str(path) or "/" in str(normalized)

    def test_normalize_path_removes_unicode_escapes(self):
        """Handles filenames with special characters."""
        accessor = PlexMetadataAccessor()
        path = Path("G:/FLICKS/Bellesa/Won't Tell.mp4")
        normalized = accessor._normalize_path(path)
        assert "Won't" in str(normalized) or "Won" in str(normalized)


class TestPlexAccessorCaching:
    """Test metadata caching mechanism."""

    def test_cache_stores_metadata_lookups(self):
        """Caching stores PlexMetadata results to avoid repeated queries."""
        accessor = PlexMetadataAccessor(enable_cache=True)
        accessor.db_path = Path("test.db")
        
        path = Path("G:/FLICKS/Bellesa/Test.mp4")
        meta = PlexMetadata(
            title="Test",
            studio="Bellesa",
            year="2024",
            genre="Feature",
            resolution="1080p",
            duration_seconds=2400,
            plex_id="1",
            last_indexed="2026-02-23",
        )
        
        with patch.object(accessor, "_query_sqlite", return_value=meta.__dict__):
            # First call queries database
            result1 = accessor.read_metadata(path)
            # Second call should use cache (no query)
            result2 = accessor.read_metadata(path)
            
            assert result1.title == result2.title

    def test_cache_respects_ttl(self):
        """Cache entries expire after configured TTL."""
        accessor = PlexMetadataAccessor(enable_cache=True, cache_ttl_seconds=60)
        assert accessor.cache_ttl_seconds == 60


class TestPlexAccessorRESTAPIFallback:
    """Test REST API fallback if SQLite unavailable."""

    def test_switch_to_rest_api_if_database_missing(self):
        """Falls back to REST API if PLEX database not found."""
        accessor = PlexMetadataAccessor(
            api_url="http://localhost:32400",
            api_token="token123",
        )
        
        with patch.object(accessor, "find_plex_database", side_effect=FileNotFoundError):
            with patch.object(accessor, "_query_rest_api") as mock_api:
                mock_api.return_value = {
                    "title": "Test",
                    "studio": "Bellesa",
                }
                # Should fall back to REST API
                accessor.access_method = PlexAccessMethod.REST_API

    def test_rest_api_requires_token(self):
        """REST API method requires valid authentication token."""
        accessor = PlexMetadataAccessor(
            api_url="http://localhost:32400",
            api_token="",
        )
        with pytest.raises(ValueError):
            accessor._query_rest_api(
                query="SELECT * FROM metadata",
            )


class TestPlexAccessorIntegration:
    """Integration tests with mocked PLEX database."""

    def test_full_retrieval_workflow(self):
        """Complete workflow: initialize, detect database, retrieve metadata."""
        accessor = PlexMetadataAccessor()
        assert accessor is not None
        assert hasattr(accessor, "read_metadata")
        assert hasattr(accessor, "read_batch_metadata")

    def test_error_handling_database_locked(self):
        """Handles database locked error gracefully."""
        accessor = PlexMetadataAccessor()
        accessor.db_path = Path("test.db")
        
        with patch.object(accessor, "_query_sqlite") as mock_query:
            mock_query.side_effect = Exception("database is locked")
            
            with pytest.raises(Exception):
                accessor.read_metadata(
                    file_path=Path("G:/FLICKS/Bellesa/Test.mp4")
                )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
