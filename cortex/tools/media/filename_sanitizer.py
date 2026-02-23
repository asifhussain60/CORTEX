"""
cortex/tools/media/filename_sanitizer.py

Intelligent filename sanitization with studio detection, obscenity morphing,
and artist preservation. Designed for video library organization (Plex, Jellyfin).

Features:
- Auto-detect studios (SexArt, Bellesa, EroticaX, etc.)
- Extract and preserve artist names
- Morph crude/obscene language → euphemisms
- Enforce <50 character limit (no dates/versions/resolutions)
- Generate metadata tags for Plex
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# ============================================================================
# DATA STRUCTURES
# ============================================================================


@dataclass
class SanitizationResult:
    """Result of filename analysis and sanitization."""

    current_filename: str
    sanitized_filename: str
    detected_studio: Optional[str] = None
    artists: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    confidence: float = 0.85
    changes_made: list[str] = field(default_factory=list)

    @property
    def needs_rename(self) -> bool:
        """True if sanitized differs from current."""
        return self.current_filename != self.sanitized_filename


# ============================================================================
# STUDIO DETECTION
# ============================================================================


class StudioDetector:
    """Detect studio/production company from filename and folder context."""

    # Studio patterns: (pattern, studio_name, priority)
    STUDIO_PATTERNS = [
        (r"(?:^|\s)SexArt(?:\s|-|_)", "SexArt", 100),
        (r"Bellesa\s+Plus", "Bellesa", 100),
        (r"(?:^|\s)Bellesa(?:\s|$)", "Bellesa", 90),
        (r"(?:^|\s)Blacked(?:\s|$)", "Blacked", 90),
        (r"(?:^|\s)EroticaX(?:\s|$)", "EroticaX", 90),
        (r"(?:^|\s)Pure\s+Taboo(?:\s|$)", "Pure Taboo", 90),
        (r"(?:^|\s)Wicked(?:\s|$)", "Wicked", 90),
        (r"(?:^|\s)SexArt(?:\s|$)", "SexArt", 85),
        (r"(?:^|\s)Sweet\s+Sinner(?:\s|$)", "Sweet Sinner", 85),
    ]

    def __init__(self, studio_context: Optional[str] = None):
        """
        Initialize studio detector.

        Args:
            studio_context: Folder name (e.g., "Bellesa") for high-priority signal.
        """
        self.studio_context = studio_context

    def detect(self, filename: str) -> Optional[str]:
        """
        Detect studio from filename (and folder context if provided).

        Args:
            filename: Filename to analyze (with or without extension).

        Returns:
            Studio name if detected, None otherwise.
        """
        # Remove extension for analysis
        name_only = Path(filename).stem

        # Folder context takes priority
        if self.studio_context:
            # Check if folder is a known studio
            for _, studio, _ in self.STUDIO_PATTERNS:
                if studio.lower() == self.studio_context.lower():
                    return self.studio_context
            # Return folder name as-is if not in patterns
            if self.studio_context not in ("_backlog", "Compilations", "Features"):
                return self.studio_context

        # Pattern matching in filename
        matches = []
        for pattern, studio, priority in self.STUDIO_PATTERNS:
            if re.search(pattern, name_only, re.IGNORECASE):
                matches.append((studio, priority))

        # Return highest priority match
        if matches:
            return max(matches, key=lambda x: x[1])[0]

        return None


# ============================================================================
# OBSCENITY MORPHING
# ============================================================================


class ObscenityMorpher:
    """Replace crude/explicit language with euphemisms while preserving meaning."""

    # (pattern, replacement, context_note)
    MORPH_RULES = [
        # Crude sexual expressions
        (r"\bmorning\s+wood\b", "morning encounter", "crude expression"),
        (r"\b(fuck|fucking|fucked|fucks)\b", "action", "profanity"),
        (r"\bhot\s+cock\b", "encounter", "crude expression"),
        (r"\bcocks?\b(?!\s+and)", "companion", "crude slang"),
        (r"\bpussy\b", "pleasure", "crude slang"),
        (r"\bass\s+hole\b", "trouble", "profanity"),
        (r"\bwhore\b", "entertainer", "vulgar slang"),
        (r"\bslut\b", "wild one", "vulgar slang"),
        (r"\bdamn\b", "darn", "profanity"),
        (r"\bhell\b", "heck", "profanity"),
        # Racial/ethnic slurs - CRITICAL: remove entirely, preserve artist
        (r"\bn\s*\*+g+\s*a|\bnigga\b|\bnigger\b", "", "racial slur - REMOVE"),
        # Bodily functions
        (r"\bpiss\b", "bathroom", "crude slang"),
        (r"\bcum\b", "action", "crude slang"),
        # Remove redundant filler
        (r"\bporno\b", "video", "filler"),
    ]

    def morph(self, text: str) -> str:
        """
        Replace crude/explicit language with euphemisms.

        Args:
            text: Text to morph (usually filename without extension).

        Returns:
            Morphed text with explicit content replaced.
        """
        result = text
        changes_made = []

        for pattern, replacement, context in self.MORPH_RULES:
            if re.search(pattern, result, re.IGNORECASE):
                before = result
                result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
                if before != result:
                    changes_made.append(context)

        # Clean up whitespace
        result = re.sub(r"\s+", " ", result).strip()

        return result


# ============================================================================
# ARTIST EXTRACTION
# ============================================================================


class ArtistExtractor:
    """Extract performer/artist names from various filename patterns."""

    # Patterns to identify artist separators and contexts
    SEPARATOR_PATTERNS = [
        (r"(.+?)\s+and\s+(.+?)(?:\s+Bellesa|\s+Plus|$)", "and_separator"),
        (r"Episode\s+\d+\s+(.+?)\s+(.+?)(?:\s+Bellesa|$)", "episode_format"),
        (r"^(.+?)\s+With\s+(.+?)$", "with_separator"),
        (r"^(.+?)\s+&\s+(.+?)$", "ampersand_separator"),
    ]

    def extract(
        self,
        filename: str,
        detected_studio: Optional[str] = None,
    ) -> list[str]:
        """
        Extract artist/performer names from filename.

        Args:
            filename: Filename to analyze (stem only, no extension).
            detected_studio: Detected studio (helps disambiguate).

        Returns:
            List of artist names (empty if none detected).
        """
        name_only = Path(filename).stem
        artists = []

        # Try separator patterns
        for pattern, pattern_type in self.SEPARATOR_PATTERNS:
            match = re.search(pattern, name_only, re.IGNORECASE)
            if match:
                groups = match.groups()
                for group in groups:
                    cleaned = group.strip()
                    # Skip known non-artist terms
                    if cleaned and not any(
                        skip in cleaned.lower()
                        for skip in [
                            "bellesa",
                            "plus",
                            "episode",
                            "sextart",
                            "blacked",
                        ]
                    ):
                        artists.append(cleaned)
                if artists:
                    return artists

        # Single artist heuristic: only extract if has explicit "and", separator, or episode pattern
        # Don't treat generic titles as artists (e.g., "Cross Roads" should not be artist)
        return artists


# ============================================================================
# FILENAME ANALYZER (MAIN)
# ============================================================================


class FilenameAnalyzer:
    """
    Main analyzer: combines studio detection, artist extraction, and morphing.
    """

    MAX_FILENAME_LENGTH = 50  # Without extension

    def __init__(self, studio_context: Optional[str] = None):
        """
        Initialize analyzer.

        Args:
            studio_context: Folder name (e.g., "Bellesa") for studio detection.
        """
        self.studio_detector = StudioDetector(studio_context=studio_context)
        self.morpher = ObscenityMorpher()
        self.artist_extractor = ArtistExtractor()

    def analyze(self, filename: str) -> SanitizationResult:
        """
        Full analysis: studio detection, artist extraction, morphing, tagging.

        Args:
            filename: Full filename with extension (e.g., "SexArt-2025-11-19-Plan-B-1080.mp4").

        Returns:
            SanitizationResult with all extracted metadata.
        """
        extension = Path(filename).suffix
        name_only = Path(filename).stem

        # 1. DETECT STUDIO
        detected_studio = self.studio_detector.detect(filename)

        # 2. EXTRACT ARTISTS (before morphing to preserve names)
        artists = self.artist_extractor.extract(name_only, detected_studio)

        # 3. MORPH OBSCENITY
        morphed = self.morpher.morph(name_only)

        # 4. REMOVE METADATA BLOAT (dates, versions, resolutions)
        cleaned = self._remove_metadata_bloat(morphed)

        # 5. TRUNCATE IF NEEDED
        if len(cleaned) > self.MAX_FILENAME_LENGTH:
            cleaned = self._smart_truncate(cleaned, artists)

        # 6. BUILD FINAL FILENAME
        sanitized = f"{cleaned}{extension}"

        # 7. BUILD TAGS
        tags = self._build_tags(detected_studio, artists, name_only)

        # 8. DETERMINE CHANGES
        changes = self._determine_changes(name_only, cleaned, detected_studio)

        # 9. CALCULATE CONFIDENCE
        confidence = self._calculate_confidence(changes, artists, detected_studio)

        return SanitizationResult(
            current_filename=filename,
            sanitized_filename=sanitized,
            detected_studio=detected_studio,
            artists=artists,
            tags=tags,
            confidence=confidence,
            changes_made=changes,
        )

    def _remove_metadata_bloat(self, text: str) -> str:
        """Remove dates, versions, resolutions, quality markers."""
        # Remove Episode prefix and number FIRST
        text = re.sub(r"Episode\s+\d+\s*", "", text)
        # Remove SexArt prefix (handled by studio detection)
        text = re.sub(r"^SexArt[\s\-]+", "", text)
        # Remove dates (YYYY-MM-DD)
        text = re.sub(r"\b\d{4}-\d{2}-\d{2}\b", "", text)
        # Remove resolutions (1080p, 720p, etc.)
        text = re.sub(r"\b\d{3,4}p?\b", "", text)
        # Remove version numbers (v1, v2, etc.)
        text = re.sub(r"\bv\d+\b", "", text)
        # Remove studio suffixes already detected
        text = re.sub(r"\s+Plus\s*$", "", text, flags=re.IGNORECASE)
        # Clean up multiple spaces and hyphens
        text = re.sub(r"\s+", " ", text).strip()
        text = re.sub(r"^[\s\-]+", "", text).strip()  # Remove leading hyphens
        text = re.sub(r"-+", " ", text).strip()  # Replace hyphens with spaces
        return text

    def _smart_truncate(self, text: str, artists: list[str]) -> str:
        """Truncate to 50 chars while trying to preserve artists."""
        if len(text) <= self.MAX_FILENAME_LENGTH:
            return text

        # If artists exist, prioritize them
        if artists:
            artist_str = " & ".join(artists[:2])
            if len(artist_str) <= self.MAX_FILENAME_LENGTH:
                return artist_str

        # Otherwise, truncate and add ellipsis
        return text[: self.MAX_FILENAME_LENGTH - 3] + "..."

    def _build_tags(
        self,
        studio: Optional[str],
        artists: list[str],
        original: str,
    ) -> list[str]:
        """Build metadata tags for Plex."""
        tags = []

        if studio:
            tags.append(studio)

        tags.extend(artists)

        # Detect quality if present
        if re.search(r"1080", original):
            tags.append("1080p")
        elif re.search(r"720", original):
            tags.append("720p")

        # Detect genres from filename keywords
        if re.search(r"\bfeat|compilation\b", original, re.IGNORECASE):
            tags.append("Compilation")

        return list(set(tags))  # Deduplicate

    def _determine_changes(
        self,
        original: str,
        cleaned: str,
        studio: Optional[str],
    ) -> list[str]:
        """List of changes made during sanitization."""
        changes = []

        if original != cleaned:
            changes.append("filename_modified")

        if re.search(r"\d{4}-\d{2}-\d{2}", original):
            changes.append("removed_date")

        if re.search(r"\d{3,4}p?", original):
            changes.append("removed_resolution")

        if re.search(r"Bellesa\s+Plus|SexArt|Blacked", original, re.IGNORECASE):
            changes.append("removed_studio_suffix")

        if re.search(r"Episode\s+\d+", original, re.IGNORECASE):
            changes.append("removed_episode_number")

        if self.morpher.morph(original) != original:
            changes.append("morphed_obscenity")

        return changes

    def _calculate_confidence(
        self,
        changes: list[str],
        artists: list[str],
        studio: Optional[str],
    ) -> float:
        """Calculate confidence score (0.0-1.0) for sanitization."""
        score = 1.0

        # Penalty: many changes = more risk
        score -= len(changes) * 0.05

        # Boost: detected studio = high confidence
        if studio:
            score += 0.1

        # Boost: artists preserved = high confidence
        if artists:
            score += 0.05 * len(artists)

        # Penalty: morphed obscenity = slight uncertainty
        if "morphed_obscenity" in changes:
            score -= 0.05

        return max(0.0, min(1.0, score))  # Clamp 0.0-1.0
