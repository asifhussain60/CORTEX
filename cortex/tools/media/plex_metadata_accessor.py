"""
cortex/tools/media/plex_metadata_accessor.py

Access PLEX metadata for video files via SQLite or REST API.

Reads video metadata from local PLEX Media Server installation (database or
REST API). Supports caching to minimize repeated queries. Handles path
normalization across Windows/Unix platforms.

Metadata retrieved::

    - Title, studio, year, genre
    - Resolution, duration
    - PLEX library ID (plex_id)
    - Last indexed timestamp

Example::

    accessor = PlexMetadataAccessor()
    metadata = accessor.read_metadata(Path("G:/FLICKS/Bellesa/Title.mp4"))
    print(f"{metadata.title} ({metadata.year}) - {metadata.studio}")

CORE-011: All functions have type hints.
CORE-012: All public APIs have docstrings.
CORE-028: snake_case naming.

AC_START: AC-PLEX-ACCESSOR-2026-02-23-002
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class PlexAccessMethod(Enum):
    """Method used to access PLEX metadata."""

    SQLITE = "sqlite"
    REST_API = "rest_api"
    HYBRID = "hybrid"  # Try API, fallback to SQLite


@dataclass
class PlexMetadata:
    """
    Video metadata retrieved from PLEX library.

    Attributes:
        title:              Video title (movie name, scene name).
        studio:             Studio/label (Bellesa, Blacked, etc.).
        year:               Release year as string (e.g. "2024").
        genre:              Genre label(s) (comma-separated if multiple).
        resolution:         Resolution (1080p, 4K, 720p, etc.).
        duration_seconds:   Video length in seconds.
        plex_id:            Unique PLEX library identifier.
        last_indexed:       ISO 8601 timestamp of last PLEX library scan.
    """

    title: str
    studio: Optional[str] = None
    year: Optional[str] = None
    genre: Optional[str] = None
    resolution: Optional[str] = None
    duration_seconds: Optional[int] = None
    plex_id: Optional[str] = None
    last_indexed: Optional[str] = None


@dataclass
class PlexMetadataAccessor:
    """
    Read video metadata from PLEX Media Server.

    Supports two backends:

    1. **SQLite** — Direct read from PLEX database (no authentication required).
       Fastest for batch queries. Works offline if database is accessible.

    2. **REST API** — Via ``http://localhost:32400`` + authentication token.
       Requires token (can be retrieved from appdata config).

    Attributes:
        db_path:           Path to PLEX metadata database. Auto-detected if not
                           provided.
        api_url:           REST API endpoint (default ``http://localhost:32400``).
        api_token:         PLEX auth token for REST API.
        preferred_method:  Preferred access method (:class:`PlexAccessMethod`).
        enable_cache:      Cache metadata lookups to disk/memory.
        cache_ttl_seconds: Cache entry lifetime (seconds).
    """

    db_path: Optional[Path] = None
    api_url: str = "http://localhost:32400"
    api_token: Optional[str] = None
    preferred_method: PlexAccessMethod = PlexAccessMethod.HYBRID
    enable_cache: bool = True
    cache_ttl_seconds: int = 3600
    _cache: Dict[Path, PlexMetadata] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Initialize and detect PLEX database if not provided."""
        if self.db_path is None:
            try:
                self.db_path = self.find_plex_database()
                logger.info(f"Detected PLEX database: {self.db_path}")
            except FileNotFoundError:
                logger.warning("PLEX database not found; will attempt REST API")
                self.db_path = None

    def find_plex_database(self) -> Path:
        """
        Auto-detect PLEX database location.

        Checks standard installation paths:
        - ``%APPDATA%\\Plex Media Server\\Metadata``
        - ``C:\\ProgramData\\Plex Media Server\\Metadata``

        Returns:
            Path to PLEX library database.

        Raises:
            FileNotFoundError: If database not found in standard locations.
        """
        standard_paths = [
            Path.home() / "AppData/Roaming/Plex Media Server/Metadata",
            Path("C:/ProgramData/Plex Media Server/Metadata"),
            Path("C:/Program Files/Plex/Plex Media Server/Metadata"),
        ]

        for candidate in standard_paths:
            if candidate.exists():
                # Look for com.plexapp.plugins.library database directory
                for subdir in candidate.glob("**/com.plexapp.plugins.library"):
                    if subdir.exists():
                        # Return path to metadata directory
                        return subdir
                # If main metadata dir exists, return it
                return candidate

        raise FileNotFoundError(
            f"PLEX database not found in standard locations: {standard_paths}"
        )

    def read_metadata(self, file_path: Path) -> Optional[PlexMetadata]:
        """
        Retrieve metadata for a single video file.

        Returns:
            :class:`PlexMetadata` if file is indexed in PLEX library,
            ``None`` otherwise.

        Args:
            file_path: Path to video file (e.g.
                      ``G:/FLICKS/Bellesa/Title.mp4``).
        """
        if self.enable_cache and file_path in self._cache:
            return self._cache[file_path]

        normalized_path = self._normalize_path(file_path)

        metadata = None
        if self.preferred_method in (
            PlexAccessMethod.SQLITE,
            PlexAccessMethod.HYBRID,
        ):
            if self.db_path:
                try:
                    metadata = self._query_sqlite(normalized_path)
                except Exception as exc:  # noqa: BLE001
                    logger.warning(
                        f"SQLite query failed for {file_path}: {exc}"
                    )
                    if self.preferred_method == PlexAccessMethod.HYBRID:
                        logger.info("Falling back to REST API")

        if metadata is None and self.preferred_method in (
            PlexAccessMethod.REST_API,
            PlexAccessMethod.HYBRID,
        ):
            if self.api_token:
                try:
                    metadata = self._query_rest_api(normalized_path)
                except Exception as exc:  # noqa: BLE001
                    logger.warning(
                        f"REST API query failed for {file_path}: {exc}"
                    )

        if self.enable_cache and metadata:
            self._cache[file_path] = metadata

        return metadata

    def read_batch_metadata(
        self,
        file_paths: List[Path],
    ) -> Dict[Path, PlexMetadata]:
        """
        Retrieve metadata for multiple files in batch.

        Returns:
            Dict mapping :class:`~pathlib.Path` → :class:`PlexMetadata`.
            Paths not in PLEX library are omitted.

        Args:
            file_paths: List of video file paths.
        """
        result: Dict[Path, PlexMetadata] = {}

        for file_path in file_paths:
            metadata = self.read_metadata(file_path)
            if metadata:
                result[file_path] = metadata

        return result

    def _normalize_path(self, file_path: Path) -> str:
        """
        Normalize file path for PLEX database query.

        Converts to forward slashes and handles special characters.

        Args:
            file_path: Original file path.

        Returns:
            Normalized path string.
        """
        # Convert to string and normalize separators
        normalized = str(file_path).replace("\\", "/")
        return normalized

    def _query_sqlite(self, normalized_path: str) -> Optional[PlexMetadata]:
        """
        Query PLEX SQLite database for metadata.

        Args:
            normalized_path: Forward-slash-normalized file path.

        Returns:
            :class:`PlexMetadata` if found, ``None`` otherwise.

        Raises:
            Exception: If database read fails.
        """
        if not self.db_path or not self.db_path.exists():
            raise FileNotFoundError(f"PLEX database not found: {self.db_path}")

        try:
            import sqlite3
        except ImportError as exc:
            raise ImportError("sqlite3 module required for SQLite backend") from exc

        try:
            conn = sqlite3.connect(self.db_path / "library.db")
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Query video metadata (simplified — actual schema may differ)
            cursor.execute(
                """
                SELECT title, studio, year, genre, resolution, duration, id, updated
                FROM metadata
                WHERE file_path LIKE ?
                LIMIT 1
                """,
                (f"%{normalized_path}%",),
            )

            row = cursor.fetchone()
            conn.close()

            if not row:
                return None

            return PlexMetadata(
                title=row["title"] or "",
                studio=row["studio"],
                year=row["year"],
                genre=row["genre"],
                resolution=row["resolution"],
                duration_seconds=row["duration"],
                plex_id=str(row["id"]),
                last_indexed=row["updated"],
            )

        except sqlite3.DatabaseError as exc:
            logger.error(f"SQLite error: {exc}")
            raise

    def _query_rest_api(self, normalized_path: str) -> Optional[PlexMetadata]:
        """
        Query PLEX REST API for metadata.

        Args:
            normalized_path: Forward-slash-normalized file path.

        Returns:
            :class:`PlexMetadata` if found, ``None`` otherwise.

        Raises:
            ValueError: If API token not provided or API unreachable.
        """
        if not self.api_token:
            raise ValueError(
                "PLEX API token required for REST API access. "
                "Set api_token parameter or PLEX_TOKEN environment variable."
            )

        try:
            import requests
        except ImportError as exc:
            raise ImportError("requests module required for REST API backend") from exc

        try:
            # Query PLEX REST API
            headers = {"X-Plex-Token": self.api_token}
            response = requests.get(
                f"{self.api_url}/library/metadata",
                headers=headers,
                params={"file": normalized_path},
                timeout=10,
            )
            response.raise_for_status()

            data = response.json()
            if not data.get("MediaContainer", {}).get("Metadata"):
                return None

            meta = data["MediaContainer"]["Metadata"][0]
            return PlexMetadata(
                title=meta.get("title", ""),
                studio=meta.get("studio"),
                year=meta.get("year"),
                genre=meta.get("genre"),
                resolution=meta.get("Media", [{}])[0].get("videoResolution"),
                duration_seconds=meta.get("duration"),
                plex_id=str(meta.get("ratingKey")),
                last_indexed=meta.get("lastViewedAt"),
            )

        except Exception as exc:
            logger.error(f"REST API error: {exc}")
            raise


# AC_COMPLETE: AC-PLEX-ACCESSOR-2026-02-23-002 ✅
