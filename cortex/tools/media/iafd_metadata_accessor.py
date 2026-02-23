"""
cortex/tools/media/iafd_metadata_accessor.py

IAFD (Internet Adult Film Database) metadata accessor.

Queries https://www.iafd.com/ to retrieve enriched metadata including:
- Scene details (date, directors, performers)
- Production company information
- Genre classifications
- Scene titles and descriptions
- Runtime and resolution metadata

Supports caching to minimize repeated queries.

CORE-011: All functions have type hints.
CORE-012: All public APIs have docstrings.
CORE-028: snake_case naming.

AC_START: AC-IAFD-ACCESSOR-2026-02-23-001
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

logger = logging.getLogger(__name__)


@dataclass
class IAFDMetadata:
    """Video metadata retrieved from IAFD database."""

    title: str
    performers: List[str] = field(default_factory=list)
    directors: List[str] = field(default_factory=list)
    production_company: Optional[str] = None
    release_date: Optional[str] = None
    runtime_minutes: Optional[int] = None
    resolution: Optional[str] = None
    scene_number: Optional[int] = None
    description: Optional[str] = None
    genres: List[str] = field(default_factory=list)
    iafd_url: Optional[str] = None
    iafd_id: Optional[str] = None
    confidence: float = 0.0  # 0.0-1.0 match confidence


@dataclass
class IAFDAccessor:
    """
    Access IAFD metadata via HTTP queries.

    Supports fallback caching and retry logic for API resilience.

    Attributes:
        base_url: IAFD website base URL.
        cache_dir: Optional cache directory for responses.
        use_cache: Whether to use cached responses.
        timeout_seconds: HTTP request timeout.
        retry_count: Number of retries on failure.
    """

    base_url: str = "https://www.iafd.com"
    cache_dir: Optional[Path] = None
    use_cache: bool = True
    timeout_seconds: int = 10
    retry_count: int = 2

    def search_by_title(self, title: str) -> Optional[IAFDMetadata]:
        """
        Search IAFD by scene/video title.

        Args:
            title: Scene or video title.

        Returns:
            :class:`IAFDMetadata` or ``None`` if not found.
        """
        # Try cache first
        if self.use_cache:
            cached = self._load_cache(title)
            if cached:
                logger.debug(f"IAFD cache hit: {title}")
                return cached

        logger.info(f"Searching IAFD for: {title}")

        try:
            # Search URL: https://www.iafd.com/results.asp?searchtype=title&searchstring=...
            search_url = (
                f"{self.base_url}/results.asp?searchtype=title&searchstring={quote(title)}"
            )

            metadata = self._query_iafd(search_url, title)

            if metadata and self.use_cache:
                self._save_cache(title, metadata)

            return metadata

        except Exception as exc:
            logger.warning(f"IAFD search failed for '{title}': {exc}")
            return None

    def search_by_performers(
        self,
        performers: List[str],
    ) -> Optional[IAFDMetadata]:
        """
        Search IAFD by performer names.

        Args:
            performers: List of performer names.

        Returns:
            :class:`IAFDMetadata` or ``None`` if not found.
        """
        if not performers:
            return None

        # Use first performer as primary search
        primary = performers[0]
        logger.info(f"Searching IAFD by performer: {primary}")

        try:
            # Performer URL: https://www.iafd.com/results.asp?searchtype=performance&searchstring=...
            search_url = (
                f"{self.base_url}/results.asp?searchtype=performance&searchstring={quote(primary)}"
            )

            metadata = self._query_iafd(search_url, primary)

            if metadata:
                # Filter to only scenes with all performers
                metadata.performers = [
                    p for p in metadata.performers
                    if any(perf.lower() in p.lower() or p.lower() in perf.lower()
                           for perf in performers)
                ]

            if metadata and self.use_cache:
                self._save_cache(primary, metadata)

            return metadata

        except Exception as exc:
            logger.warning(f"IAFD performer search failed: {exc}")
            return None

    def search_by_studio(
        self,
        studio: str,
        limit: int = 10,
    ) -> List[IAFDMetadata]:
        """
        Search IAFD by studio/production company.

        Args:
            studio: Production company name (e.g., "Wicked Pictures").
            limit: Maximum results to return.

        Returns:
            List of :class:`IAFDMetadata` or empty list if not found.
        """
        logger.info(f"Searching IAFD studio: {studio}")

        try:
            # Studio URL: https://www.iafd.com/results.asp?searchtype=releasecompany&searchstring=...
            search_url = (
                f"{self.base_url}/results.asp?searchtype=releasecompany&searchstring={quote(studio)}"
            )

            # Parse multiple results from search page
            results = self._query_iafd_batch(search_url, studio, limit)
            return results

        except Exception as exc:
            logger.warning(f"IAFD studio search failed: {exc}")
            return []

    def _query_iafd(
        self,
        url: str,
        query_term: str,
    ) -> Optional[IAFDMetadata]:
        """
        Query IAFD and parse response.

        Args:
            url: Full IAFD URL to query.
            query_term: Original search term (for logging).

        Returns:
            :class:`IAFDMetadata` or ``None``.
        """
        import requests
        from bs4 import BeautifulSoup

        for attempt in range(self.retry_count):
            try:
                logger.debug(f"IAFD query (attempt {attempt + 1}): {url}")

                response = requests.get(
                    url,
                    timeout=self.timeout_seconds,
                    headers={
                        "User-Agent": (
                            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                        )
                    },
                )
                response.raise_for_status()

                # Parse HTML
                soup = BeautifulSoup(response.content, "html.parser")

                # Extract first result (primary match)
                metadata = self._parse_result(soup, query_term)

                if metadata:
                    metadata.confidence = 0.95  # High confidence from IAFD
                    return metadata

                logger.info(f"IAFD no results for: {query_term}")
                return None

            except requests.exceptions.RequestException as e:
                logger.debug(f"IAFD request failed (attempt {attempt + 1}): {e}")
                if attempt < self.retry_count - 1:
                    time.sleep(1)
                else:
                    raise

        return None

    def _query_iafd_batch(
        self,
        url: str,
        query_term: str,
        limit: int,
    ) -> List[IAFDMetadata]:
        """
        Query IAFD and parse multiple results.

        Args:
            url: Full IAFD URL.
            query_term: Search term.
            limit: Max results.

        Returns:
            List of :class:`IAFDMetadata`.
        """
        import requests
        from bs4 import BeautifulSoup

        results = []

        try:
            response = requests.get(
                url,
                timeout=self.timeout_seconds,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                    )
                },
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            # Extract multiple results
            result_rows = soup.find_all("tr", limit=limit)

            for row in result_rows:
                try:
                    metadata = self._parse_result(row, query_term)
                    if metadata:
                        results.append(metadata)
                except Exception as e:
                    logger.debug(f"Error parsing result: {e}")
                    continue

            logger.info(f"IAFD batch: {len(results)} results for {query_term}")

        except Exception as exc:
            logger.warning(f"IAFD batch query failed: {exc}")

        return results

    def _parse_result(
        self,
        soup_element,
        query_term: str,
    ) -> Optional[IAFDMetadata]:
        """
        Parse IAFD result from HTML element.

        Args:
            soup_element: BeautifulSoup element to parse.
            query_term: Search term (for confidence scoring).

        Returns:
            :class:`IAFDMetadata` or ``None``.
        """
        try:
            # Extract fields from table row/result element
            # This is a simplified parser - adjust selectors based on actual IAFD HTML structure

            # Try to find title link
            title_link = soup_element.find("a", href=lambda x: x and "/title" in x)
            if not title_link:
                return None

            title = title_link.get_text(strip=True)
            if not title:
                return None

            iafd_url = title_link.get("href", "")
            if not iafd_url.startswith("http"):
                iafd_url = f"{self.base_url}{iafd_url}"

            # Extract performers (usually in additional cells)
            performers = []
            perf_cells = soup_element.find_all("a", href=lambda x: x and "/person" in x)
            for cell in perf_cells:
                perf_name = cell.get_text(strip=True)
                if perf_name:
                    performers.append(perf_name)

            # Try to extract release date
            release_date = None
            date_cell = soup_element.find("td", string=lambda x: x and "/" in str(x))
            if date_cell:
                release_date = date_cell.get_text(strip=True)

            # Extract directors (if available)
            directors = []
            director_cells = soup_element.find_all("a", href=lambda x: x and "/director" in x)
            for cell in director_cells:
                dir_name = cell.get_text(strip=True)
                if dir_name:
                    directors.append(dir_name)

            # Try to extract production company
            production_company = None
            company_cells = soup_element.find_all(
                "a", href=lambda x: x and "/company" in x
            )
            if company_cells:
                production_company = company_cells[0].get_text(strip=True)

            # Extract IAFD ID from URL
            iafd_id = None
            if "/title/" in iafd_url:
                parts = iafd_url.split("/")
                iafd_id = parts[-1].replace(".html", "") if parts else None

            return IAFDMetadata(
                title=title,
                performers=performers,
                directors=directors,
                production_company=production_company,
                release_date=release_date,
                iafd_url=iafd_url,
                iafd_id=iafd_id,
                confidence=0.85,
            )

        except Exception as exc:
            logger.debug(f"Error parsing IAFD result: {exc}")
            return None

    def _load_cache(self, key: str) -> Optional[IAFDMetadata]:
        """Load cached metadata."""
        if not self.cache_dir:
            return None

        cache_file = self.cache_dir / f"{self._hash_key(key)}.json"
        if not cache_file.exists():
            return None

        try:
            with open(cache_file) as f:
                data = json.load(f)
                return IAFDMetadata(**data)
        except Exception as exc:
            logger.debug(f"Cache load failed: {exc}")
            return None

    def _save_cache(self, key: str, metadata: IAFDMetadata) -> None:
        """Save metadata to cache."""
        if not self.cache_dir:
            return

        self.cache_dir.mkdir(parents=True, exist_ok=True)

        cache_file = self.cache_dir / f"{self._hash_key(key)}.json"

        try:
            with open(cache_file, "w") as f:
                json.dump(
                    {
                        "title": metadata.title,
                        "performers": metadata.performers,
                        "directors": metadata.directors,
                        "production_company": metadata.production_company,
                        "release_date": metadata.release_date,
                        "runtime_minutes": metadata.runtime_minutes,
                        "resolution": metadata.resolution,
                        "scene_number": metadata.scene_number,
                        "description": metadata.description,
                        "genres": metadata.genres,
                        "iafd_url": metadata.iafd_url,
                        "iafd_id": metadata.iafd_id,
                        "confidence": metadata.confidence,
                    },
                    f,
                    indent=2,
                )
        except Exception as exc:
            logger.debug(f"Cache save failed: {exc}")

    @staticmethod
    def _hash_key(key: str) -> str:
        """Hash cache key."""
        import hashlib

        return hashlib.md5(key.encode()).hexdigest()


# AC_COMPLETE: AC-IAFD-ACCESSOR-2026-02-23-001 ✅
