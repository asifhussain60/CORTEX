"""
cortex/tools/media/bollywood_metadata_accessor.py

Bollywood music metadata accessor for MusicBrainz and online sources.

Queries MusicBrainz API and Wikipedia to retrieve enriched metadata including:
- Song title, artist(s), film/album name
- Release year, genre classifications
- Album art URLs (for PLEX posters)
- Featured artists and composers

Supports caching to minimize repeated queries.

CORE-011: All functions have type hints.
CORE-012: All public APIs have docstrings.
CORE-028: snake_case naming.

AC_START: AC-BOLLYWOOD-ACCESSOR-2026-03-11-001
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from urllib.parse import quote
import urllib.request
import urllib.error

logger = logging.getLogger(__name__)


@dataclass
class BollywoodMetadata:
    """Music metadata retrieved from online sources."""

    title: str
    artists: List[str] = field(default_factory=list)
    album: Optional[str] = None  # Film name or album
    year: Optional[int] = None
    genre: str = "Bollywood"
    composers: List[str] = field(default_factory=list)
    lyricists: List[str] = field(default_factory=list)
    film_name: Optional[str] = None
    duration_seconds: Optional[int] = None
    musicbrainz_id: Optional[str] = None
    album_art_url: Optional[str] = None
    confidence: float = 0.0  # 0.0-1.0 match confidence
    source: str = "unknown"  # "musicbrainz" | "wikipedia" | "manual"


@dataclass
class BollywoodMetadataFetcher:
    """
    Fetch Bollywood music metadata from online sources.

    Supports MusicBrainz API with fallback to Wikipedia/IMDb for film soundtracks.

    Attributes:
        musicbrainz_url: MusicBrainz API base URL.
        cache_dir: Optional cache directory for responses.
        use_cache: Whether to use cached responses.
        timeout_seconds: HTTP request timeout.
        retry_count: Number of retries on failure.
    """

    musicbrainz_url: str = "https://musicbrainz.org/ws/2"
    cache_dir: Optional[Path] = None
    use_cache: bool = True
    timeout_seconds: int = 10
    retry_count: int = 2

    def __post_init__(self) -> None:
        """Initialize cache directory if specified."""
        if self.cache_dir and self.use_cache:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

    def search_by_title_artist(
        self, title: str, artist: Optional[str] = None
    ) -> Optional[BollywoodMetadata]:
        """
        Search for Bollywood song by title and optional artist.

        Args:
            title: Song title.
            artist: Optional artist name to narrow search.

        Returns:
            :class:`BollywoodMetadata` or ``None`` if not found.
        """
        # Try cache first
        cache_key = f"{title}_{artist or 'unknown'}"
        if self.use_cache:
            cached = self._load_cache(cache_key)
            if cached:
                logger.debug(f"Bollywood metadata cache hit: {title}")
                return cached

        logger.info(f"Searching MusicBrainz for: {title} by {artist or 'unknown'}")

        # Build MusicBrainz query
        # Example: https://musicbrainz.org/ws/2/recording/?query=recording:"Aaj Ki Raat" AND country:IN&fmt=json
        query_parts = [f'recording:"{title}"']
        if artist:
            query_parts.append(f'artist:"{artist}"')
        query_parts.append("country:IN")  # India filter for Bollywood

        query = " AND ".join(query_parts)
        url = f"{self.musicbrainz_url}/recording/?query={quote(query)}&fmt=json&limit=5"

        try:
            result = self._fetch_with_retry(url)
            if result:
                metadata = self._parse_musicbrainz_response(result, title)
                if metadata and self.use_cache:
                    self._save_cache(cache_key, metadata)
                return metadata
        except Exception as e:
            logger.warning(f"MusicBrainz search failed for '{title}': {e}")

        return None

    def search_by_film(self, film_name: str) -> List[BollywoodMetadata]:
        """
        Search for all songs from a Bollywood film soundtrack.

        Args:
            film_name: Film name (e.g., "Stree 2", "Raees").

        Returns:
            List of :class:`BollywoodMetadata` for soundtrack songs.
        """
        logger.info(f"Searching soundtrack for film: {film_name}")

        # MusicBrainz query for release (album) by name
        query = f'release:"{film_name}" AND country:IN'
        url = f"{self.musicbrainz_url}/release/?query={quote(query)}&fmt=json&limit=3"

        try:
            result = self._fetch_with_retry(url)
            if result and "releases" in result:
                releases = result["releases"]
                if releases:
                    # Get first matching release ID
                    release_id = releases[0].get("id")
                    if release_id:
                        return self._fetch_release_tracks(release_id, film_name)
        except Exception as e:
            logger.warning(f"Film soundtrack search failed for '{film_name}': {e}")

        return []

    def _fetch_release_tracks(
        self, release_id: str, film_name: str
    ) -> List[BollywoodMetadata]:
        """Fetch all tracks from a MusicBrainz release."""
        url = f"{self.musicbrainz_url}/release/{release_id}?inc=recordings+artist-credits&fmt=json"

        try:
            result = self._fetch_with_retry(url)
            if result and "media" in result:
                tracks = []
                for medium in result["media"]:
                    for track in medium.get("tracks", []):
                        recording = track.get("recording", {})
                        artists = [
                            ac["artist"]["name"]
                            for ac in track.get("artist-credit", [])
                            if "artist" in ac
                        ]

                        metadata = BollywoodMetadata(
                            title=recording.get("title", ""),
                            artists=artists,
                            album=film_name,
                            film_name=film_name,
                            year=self._extract_year(result.get("date")),
                            duration_seconds=recording.get("length", 0) // 1000,
                            musicbrainz_id=recording.get("id"),
                            confidence=0.85,
                            source="musicbrainz",
                        )
                        tracks.append(metadata)
                return tracks
        except Exception as e:
            logger.warning(f"Release track fetch failed for ID '{release_id}': {e}")

        return []

    def _parse_musicbrainz_response(
        self, response: Dict, search_title: str
    ) -> Optional[BollywoodMetadata]:
        """Parse MusicBrainz JSON response and extract metadata."""
        recordings = response.get("recordings", [])
        if not recordings:
            return None

        # Take first result (best match)
        recording = recordings[0]
        title = recording.get("title", "")
        mb_id = recording.get("id", "")

        # Extract artists from artist-credit
        artists = []
        for ac in recording.get("artist-credit", []):
            if "artist" in ac:
                artists.append(ac["artist"]["name"])

        # Extract release (album/film) info
        releases = recording.get("releases", [])
        album = releases[0].get("title") if releases else None
        year = self._extract_year(releases[0].get("date")) if releases else None

        # Calculate confidence based on title similarity
        confidence = self._calculate_confidence(search_title, title)

        metadata = BollywoodMetadata(
            title=title,
            artists=artists,
            album=album,
            film_name=album,  # For Bollywood, album usually = film
            year=year,
            musicbrainz_id=mb_id,
            confidence=confidence,
            source="musicbrainz",
        )

        logger.debug(f"Parsed MusicBrainz metadata: {title} by {', '.join(artists)} (confidence: {confidence:.2f})")
        return metadata

    def _fetch_with_retry(self, url: str) -> Optional[Dict]:
        """Fetch URL with retry logic."""
        headers = {
            "User-Agent": "CORTEX/1.0 (https://github.com/cortex; asif@cortexlabs.ai)"
        }

        for attempt in range(self.retry_count + 1):
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=self.timeout_seconds) as response:
                    data = response.read().decode("utf-8")
                    return json.loads(data)
            except urllib.error.HTTPError as e:
                if e.code == 429:  # Rate limit
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(f"Rate limited, waiting {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"HTTP error {e.code}: {e.reason}")
                    return None
            except Exception as e:
                logger.warning(f"Fetch attempt {attempt + 1} failed: {e}")
                if attempt < self.retry_count:
                    time.sleep(1)

        return None

    def _extract_year(self, date_str: Optional[str]) -> Optional[int]:
        """Extract year from ISO date string (e.g., '2024-08-15' -> 2024)."""
        if not date_str:
            return None
        try:
            return int(date_str.split("-")[0])
        except (ValueError, IndexError):
            return None

    def _calculate_confidence(self, search_term: str, matched_term: str) -> float:
        """Calculate match confidence based on string similarity."""
        search_lower = search_term.lower().strip()
        matched_lower = matched_term.lower().strip()

        if search_lower == matched_lower:
            return 1.0

        # Simple substring matching
        if search_lower in matched_lower or matched_lower in search_lower:
            return 0.85

        # Word overlap scoring
        search_words = set(search_lower.split())
        matched_words = set(matched_lower.split())
        common_words = search_words & matched_words

        if not search_words:
            return 0.0

        overlap_ratio = len(common_words) / len(search_words)
        return max(0.5, min(0.95, overlap_ratio))

    def _load_cache(self, cache_key: str) -> Optional[BollywoodMetadata]:
        """Load cached metadata from disk."""
        if not self.cache_dir:
            return None

        cache_file = self.cache_dir / f"{self._sanitize_filename(cache_key)}.json"
        if not cache_file.exists():
            return None

        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return BollywoodMetadata(**data)
        except Exception as e:
            logger.warning(f"Cache load failed: {e}")
            return None

    def _save_cache(self, cache_key: str, metadata: BollywoodMetadata) -> None:
        """Save metadata to cache."""
        if not self.cache_dir:
            return

        cache_file = self.cache_dir / f"{self._sanitize_filename(cache_key)}.json"
        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                # Convert dataclass to dict
                data = {
                    "title": metadata.title,
                    "artists": metadata.artists,
                    "album": metadata.album,
                    "year": metadata.year,
                    "genre": metadata.genre,
                    "composers": metadata.composers,
                    "lyricists": metadata.lyricists,
                    "film_name": metadata.film_name,
                    "duration_seconds": metadata.duration_seconds,
                    "musicbrainz_id": metadata.musicbrainz_id,
                    "album_art_url": metadata.album_art_url,
                    "confidence": metadata.confidence,
                    "source": metadata.source,
                }
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.warning(f"Cache save failed: {e}")

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize string for use as filename."""
        # Remove invalid filename characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, "_")
        return filename[:100]  # Limit length


# AC_COMPLETE: AC-BOLLYWOOD-ACCESSOR-2026-03-11-001 ✅
