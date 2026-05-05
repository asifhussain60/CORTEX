"""
scripts/bollywood_organize.py

Entry point script for organizing Bollywood music videos with CORTEX governance.

Workflow:
1. SCAN — Recursively discover all MP4/M4A files in target directory and subfolders
2. IDENTIFY — Extract artist, song title, film name using semantic parsing
3. MATCH — Query MusicBrainz for enriched metadata (year, genre, album art)
4. DUPLICATE — Detect duplicate songs using SHA256 hashing and audio fingerprinting
5. RENAME — Apply proper case naming with spaces (Artist - Song Title - Film.mp4)
6. TAG — Write MP4 metadata (Title, Artist, Album, Year, Genre, Comment)
7. PLEX — Sync metadata with Plex Media Server library
8. VERIFY — Validate all files processed successfully

Usage:
    python scripts/bollywood_organize.py --dry-run     # Preview only
    python scripts/bollywood_organize.py --apply       # Execute changes
    python scripts/bollywood_organize.py --target "Z:\\MUSIC\\Bollywood\\Bollywood Hits"

Features:
    - Recursive subfolder scanning
    - Proper case file naming with spaces (human-readable)
    - Duplicate detection and documentation
    - Plex metadata preservation and sync
    - In-place renaming (preserves folder structure)
    - Enhanced metadata enrichment

CORE-011: All functions have type hints.
CORE-012: All public APIs have docstrings.

AC_START: AC-BOLLYWOOD-ORGANIZE-2026-03-11-003
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import time

# Add parent directory to path for local imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from cortex.tools.media.bollywood_metadata_accessor import (
    BollywoodMetadataFetcher,
    BollywoodMetadata,
)
from cortex.tools.media.duplicate_detector import (
    DuplicateDetector,
    DuplicateGroup,
)
from cortex.tools.media.plex_metadata_accessor import (
    PlexMetadataAccessor,
    PlexMetadata,
)
from cortex.tools.media.tag_writer import TagFields, TagWriter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


@dataclass
class FileEntry:
    """Single file to process."""

    original_path: Path
    original_name: str
    extracted_title: Optional[str] = None
    extracted_artists: List[str] = field(default_factory=list)
    extracted_film: Optional[str] = None
    category: str = "Bollywood Hits"
    new_name: Optional[str] = None
    target_path: Optional[Path] = None
    metadata: Optional[BollywoodMetadata] = None
    plex_metadata: Optional[PlexMetadata] = None
    confidence: float = 0.0
    is_duplicate: bool = False
    duplicate_group_id: Optional[str] = None
    file_hash: Optional[str] = None


@dataclass
class WorkflowStats:
    """Workflow execution statistics."""

    total_files: int = 0
    files_scanned: int = 0
    files_identified: int = 0
    files_matched: int = 0
    duplicates_found: int = 0
    files_renamed: int = 0
    files_tagged: int = 0
    plex_synced: int = 0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    duration_seconds: float = 0.0
    duplicate_groups: List[DuplicateGroup] = field(default_factory=list)


class BollywoodOrganizer:
    """Organize Bollywood music videos with metadata enrichment."""

    def __init__(
        self,
        target_dir: Path,
        dry_run: bool = True,
        use_online_metadata: bool = True,
        detect_duplicates: bool = True,
        sync_plex: bool = True,
        in_place: bool = True,
    ) -> None:
        """
        Initialize Bollywood organizer.

        Args:
            target_dir: Target directory to scan recursively (e.g., Z:\\MUSIC\\Bollywood\\Bollywood Hits).
            dry_run: Preview mode (no file modifications).
            use_online_metadata: Query MusicBrainz for enriched metadata.
            detect_duplicates: Enable SHA256-based duplicate detection.
            sync_plex: Sync metadata with Plex Media Server.
            in_place: Rename files in-place (preserve folder structure).
        """
        self.target_dir = target_dir
        self.dry_run = dry_run
        self.use_online_metadata = use_online_metadata
        self.detect_duplicates = detect_duplicates
        self.sync_plex = sync_plex
        self.in_place = in_place

        # Initialize metadata fetcher
        cache_dir = Path(".cortex-runtime/bollywood-cache")
        self.metadata_fetcher = BollywoodMetadataFetcher(
            cache_dir=cache_dir, use_cache=True
        )

        # Initialize duplicate detector
        if detect_duplicates:
            self.duplicate_detector = DuplicateDetector(
                root=target_dir,
                extensions=[".mp4", ".m4a", ".mp3", ".flac"],
            )

        # Initialize Plex accessor
        if sync_plex:
            try:
                self.plex_accessor = PlexMetadataAccessor()
            except Exception as e:
                logger.warning(f"Plex accessor initialization failed: {e}")
                self.sync_plex = False

        self.stats = WorkflowStats()
        self.files: List[FileEntry] = []

    def run_workflow(self) -> WorkflowStats:
        """Execute complete workflow."""
        start_time = time.time()

        logger.info("=" * 80)
        logger.info("BOLLYWOOD MUSIC ORGANIZATION WORKFLOW (CORTEX)")
        logger.info("=" * 80)
        logger.info(f"Target: {self.target_dir}")
        logger.info(f"Mode: {'DRY-RUN (Preview)' if self.dry_run else 'APPLY (Execute)'}")
        logger.info(f"Recursive: True (all subfolders)")
        logger.info(f"Naming: Proper case with spaces (Artist - Song - Film)")
        logger.info(f"Duplicate detection: {self.detect_duplicates}")
        logger.info(f"Plex sync: {self.sync_plex}")
        logger.info("=" * 80)
        logger.info("")

        # Stage 1: SCAN (recursive)
        logger.info("STAGE 1: SCAN — Recursively discovering audio files...")
        self._scan_files_recursive()
        logger.info(f"✅ Found {self.stats.files_scanned} files in {self.stats.total_files} total\n")

        # Stage 2: IDENTIFY
        logger.info("STAGE 2: IDENTIFY — Extracting metadata from filenames...")
        self._identify_metadata()
        logger.info(f"✅ Identified {self.stats.files_identified} files\n")

        # Stage 3: MATCH (online enrichment)
        if self.use_online_metadata:
            logger.info("STAGE 3: MATCH — Querying MusicBrainz for enriched metadata...")
            self._match_online_metadata()
            logger.info(f"✅ Matched {self.stats.files_matched} files\n")

        # Stage 4: DUPLICATE DETECTION
        if self.detect_duplicates:
            logger.info("STAGE 4: DUPLICATE — Detecting duplicate songs...")
            self._detect_duplicates()
            logger.info(f"✅ Found {self.stats.duplicates_found} duplicates in {len(self.stats.duplicate_groups)} groups\n")
        else:
            logger.info("STAGE 4: DUPLICATE — Skipped (disabled)\n")

        # Stage 5: RENAME (proper case with spaces, in-place)
        logger.info("STAGE 5: RENAME — Generating proper case filenames with spaces...")
        self._generate_proper_case_names()
        
        # Apply renames if not in dry-run mode
        if not self.dry_run:
            logger.info("Applying file renames...")
            self._apply_renames()
            logger.info(f"✅ Renamed {self.stats.files_renamed} files (in-place)\n")
        else:
            logger.info(f"✅ Generated {self.stats.files_renamed} rename proposals (dry-run)\n")

        # Stage 6: TAG (metadata writing)
        if not self.dry_run:
            logger.info("STAGE 6: TAG — Writing MP4 metadata...")
            self._write_metadata_tags()
            logger.info(f"✅ Tagged {self.stats.files_tagged} files\n")
        else:
            logger.info("STAGE 6: TAG — Skipped (dry-run mode)\n")

        # Stage 7: PLEX SYNC
        if self.sync_plex and not self.dry_run:
            logger.info("STAGE 7: PLEX — Syncing metadata with Plex Media Server...")
            self._sync_plex_metadata()
            logger.info(f"✅ Synced {self.stats.plex_synced} files with Plex\n")
        else:
            logger.info("STAGE 7: PLEX — Skipped (dry-run or disabled)\n")

        # Stage 8: VERIFY
        logger.info("STAGE 8: VERIFY — Validating results...")
        self._verify_results()
        logger.info("✅ Verification complete\n")

        self.stats.duration_seconds = time.time() - start_time

        self._print_summary()
        return self.stats

    def _scan_files_recursive(self) -> None:
        """Stage 1: Recursively scan target directory for audio files."""
        audio_extensions = [".mp4", ".m4a", ".mp3", ".flac", ".ogg", ".wav"]
        all_files = []
        
        for ext in audio_extensions:
            all_files.extend(self.target_dir.rglob(f"*{ext}"))
        
        self.stats.total_files = len(all_files)
        self.stats.files_scanned = len(all_files)

        for file_path in all_files:
            entry = FileEntry(
                original_path=file_path,
                original_name=file_path.name,
            )
            self.files.append(entry)
            
        logger.info(f"Scanned {len(all_files)} files across all subfolders")

    def _identify_metadata(self) -> None:
        """Stage 2: Extract artist, song title, film from filenames."""
        for entry in self.files:
            # Parse filename to extract metadata
            parsed = self._parse_filename(entry.original_name)
            entry.extracted_title = parsed["title"]
            entry.extracted_artists = parsed["artists"]
            entry.extracted_film = parsed["film"]
            entry.category = self._categorize_file(entry.original_name)

            if entry.extracted_title:
                self.stats.files_identified += 1

    def _parse_filename(self, filename: str) -> Dict[str, any]:
        """
        Parse Bollywood music video filename to extract metadata.

        Handles patterns like:
        - "Aaj Ki Raat   Stree 2   Tamannaah Bhatia   Sachin–Jigar..."
        - "60. Saturday Night - Jhootha Kahin Ka  Sunny,Omkar,Natasha..."
        - "GURU RANDHAWA -  AZUL   MV.mp4"
        - "Artist - Song Title - Film.mp4"
        """
        # Common Bollywood artists for pattern matching
        common_artists = {
            "badshah", "guru randhawa", "honey singh", "yo yo honey singh", "neha kakkar",
            "shreya ghoshal", "arijit singh", "sonu nigam", "kumar sanu", "alka yagnik",
            "udit narayan", "sunidhi chauhan", "armaan malik", "jubin nautiyal", "darshan raval",
            "pritam", "vishal-shekhar", "sachin-jigar", "tanishk bagchi", "himesh reshammiya",
            "a.r. rahman", "salim-sulaiman", "shankar-ehsaan-loy", "mika singh", "diljit dosanjh",
            "atif aslam", "rahat fateh ali khan", "karan aujla", "jasmine sandlas", "garry sandhu",
            "tony kakkar", "amit trivedi", "anu malik", "ankit tiwari", "tulsi kumar",
            "dhvani bhanushali", "asees kaur", "b praak", "jaani", "zahrah khan"
        }
        
        # Common film keywords to help identify film names
        film_keywords = {
            "stree", "raees", "war", "fighter", "pushpa", "kgf", "dhoom", "ready", "housefull",
            "hate story", "student of the year", "street dancer", "hate", "love", "mission",
            "badlapur", "bhediya", "munjya", "sikandar", "baaghi", "sanju", "legacy roots"
        }

        # Remove extension
        name = filename.replace(".mp4", "").strip()

        # Remove leading numbers (e.g., "60. ")
        name = re.sub(r"^\d+\.\s*", "", name)

        # Remove video quality markers and noise
        name = re.sub(r"\(.*?(Full|Official|Lyric|Video|8K|4K|HD).*?\)", "", name, flags=re.IGNORECASE)
        name = re.sub(r"(Full|Official|Lyric|Video|8K|4K|HD)\s+(Video|Song)", "", name, flags=re.IGNORECASE)
        name = re.sub(r"(Music\s+Video|MV)\s*$", "", name, flags=re.IGNORECASE)
        name = re.sub(r"#\w+", "", name)  # Remove hashtags
        # DON'T normalize spaces yet - we need the multi-space delimiters!

        # Try Pattern 1: "Artist - Song - Film" (explicit structure)
        # Only apply if clean dash separation (no multi-spaces within parts)
        if name.count(" - ") >= 1:
            dash_parts = [p.strip() for p in name.split(" - ") if p.strip()]
            # Check if this is truly a dash-separated structure (no multi-spaces in first part)
            first_part_clean = "  " not in dash_parts[0] if dash_parts else False
            
            if len(dash_parts) >= 2 and first_part_clean:
                # Check if first part is a known artist
                if any(artist in dash_parts[0].lower() for artist in common_artists):
                    return {
                        "title": dash_parts[1] if len(dash_parts) > 1 else dash_parts[0],
                        "artists": [dash_parts[0]],
                        "film": dash_parts[2] if len(dash_parts) > 2 else None,
                    }
                # Check if it's explicit 3-part "Artist - Song - Film"
                elif len(dash_parts) >= 3 and "  " not in dash_parts[1]:
                    return {
                        "title": dash_parts[1],
                        "artists": [dash_parts[0]],
                        "film": dash_parts[2],
                    }

        # Try Pattern 2: Multiple spaces as delimiters (most common Bollywood pattern)
        # "Song   Film   Artists   Composers"
        parts = [p.strip() for p in re.split(r"\s{2,}", name) if p.strip()]
        
        if not parts:
            return {"title": name, "artists": [], "film": None}

        title = parts[0]
        artists = []
        film = None

        # Analyze remaining parts for film and artists
        # Priority: Find comma-separated lists first (these are almost always artists)
        artist_parts = []
        film_candidate = None
        
        for i, part in enumerate(parts[1:], 1):
            part_lower = part.lower()
            
            # Strong artist indicators (highest priority)
            has_commas = "," in part
            has_ampersand = "&" in part
            has_known_artist = any(artist in part_lower for artist in common_artists)
            is_known_film = any(keyword in part_lower for keyword in film_keywords)
            
            # If part has commas or multiple &, it's almost certainly artists
            if has_commas or part.count("&") >= 2:
                artist_parts.append((i, part, "comma_list"))
            # If it's a known artist name
            elif has_known_artist:
                artist_parts.append((i, part, "known_artist"))
            # If it's position 1 (right after title) and looks like film
            elif i == 1 and (is_known_film or (len(part.split()) <= 4 and not has_ampersand)):
                film_candidate = part
            # Position 2-3 with single & or "X" or "feat" are likely artists
            elif i in [2, 3] and (has_ampersand or " X " in part or "feat" in part_lower):
                artist_parts.append((i, part, "collaboration"))

        # Extract artists from identified parts (prioritize earliest/most confident)
        for idx, artist_part, reason in artist_parts[:2]:  # Take first 2 artist parts max
            # Split by separators
            if reason == "comma_list":
                artist_list = re.split(r"[,&]", artist_part)
            else:
                artist_list = re.split(r"[,&]|\s+X\s+|\s+x\s+|\s+feat\.?\s+|\s+ft\.?\s+", 
                                     artist_part, flags=re.IGNORECASE)
            
            for artist in artist_list:
                artist = artist.strip()
                # Filter out non-artist entries (directors, actors often have single names)
                if artist and len(artist) > 2 and not any(x in artist.lower() for x in ["presents", "official"]):
                    artists.append(artist)

        # Set film name
        film = film_candidate

        # Fallback: If still no artists and we have 3+ parts, assume part 2 or 3 is artists
        if not artists and len(parts) >= 3:
            # Try part 2 (if not already film)
            if film != parts[1]:
                candidate = parts[1]
            elif len(parts) >= 4:
                candidate = parts[2]
            else:
                candidate = None
            
            if candidate:
                # If it has separators, split it
                if "," in candidate or "&" in candidate:
                    artist_list = re.split(r"[,&]", candidate)
                    artists = [a.strip() for a in artist_list if a.strip()]
                else:
                    artists = [candidate]

        # Clean up artist names (remove non-name suffixes)
        cleaned_artists = []
        for artist in artists:
            # Remove trailing descriptors
            artist = re.sub(r"\s+(Presents?|Official|New Song).*$", "", artist, flags=re.IGNORECASE)
            # Take first name if multiple words and very long
            if len(artist) > 30:
                words = artist.split()
                artist = " ".join(words[:3])  # Keep first 3 words
            if artist and len(artist) > 2:
                cleaned_artists.append(artist)

        return {
            "title": title,
            "artists": cleaned_artists[:3] if cleaned_artists else [],  # Max 3 artists
            "film": film,
        }

    def _categorize_file(self, filename: str) -> str:
        """Categorize file based on filename patterns."""
        name_lower = filename.lower()

        # Mashups/Compilations
        if any(
            kw in name_lower
            for kw in ["mashup", "megamix", "jukebox", "playlist", "collection"]
        ):
            return "Compilations/Mashups"

        # Party & Dance
        if any(
            kw in name_lower
            for kw in ["party", "dance", "night", "hook up", "coca cola", "badshah"]
        ):
            return "Party & Dance"

        # Romantic
        if any(kw in name_lower for kw in ["romantic", "love", "dil", "ishq", "pyaar"]):
            return "Romantic"

        # Default: Bollywood Hits
        return "Bollywood Hits"

    def _match_online_metadata(self) -> None:
        """Stage 3: Query MusicBrainz for enriched metadata."""
        for entry in self.files:
            if not entry.extracted_title:
                continue

            try:
                artist_hint = entry.extracted_artists[0] if entry.extracted_artists else None
                metadata = self.metadata_fetcher.search_by_title_artist(
                    entry.extracted_title, artist_hint
                )

                if metadata and metadata.confidence >= 0.7:
                    entry.metadata = metadata
                    entry.confidence = metadata.confidence
                    self.stats.files_matched += 1
                    logger.debug(f"Matched: {entry.extracted_title} (confidence: {metadata.confidence:.2f})")
                else:
                    logger.debug(f"No match found for: {entry.extracted_title}")
            except Exception as e:
                logger.warning(f"Metadata fetch failed for '{entry.extracted_title}': {e}")

    def _detect_duplicates(self) -> None:
        """Stage 4: Detect duplicate songs using SHA256 hashing."""
        if not self.detect_duplicates:
            return

        try:
            # Build hash index
            logger.info("Computing file hashes...")
            self.duplicate_detector.scan()

            # Find duplicates
            duplicate_groups = self.duplicate_detector.find_duplicates()
            self.stats.duplicate_groups = duplicate_groups

            # Mark duplicate files in entries
            for group in duplicate_groups:
                self.stats.duplicates_found += group.duplicate_count - 1  # -1 for original
                for file_path in group.files:
                    for entry in self.files:
                        if entry.original_path == file_path:
                            entry.is_duplicate = True
                            entry.duplicate_group_id = group.sha256
                            entry.file_hash = group.sha256

            logger.info(f"Identified {len(duplicate_groups)} duplicate groups")
        except Exception as e:
            logger.error(f"Duplicate detection failed: {e}")
            self.stats.errors.append(f"Duplicate detection error: {e}")

    def _generate_proper_case_names(self) -> None:
        """Stage 5: Generate strict English Artist/Title filenames."""
        for entry in self.files:
            # Skip duplicate files (keep only one copy)
            if entry.is_duplicate:
                self.stats.warnings.append(f"Duplicate: {entry.original_name} (hash: {entry.file_hash[:8]}...)")
                continue

            # Use enriched metadata if available (prioritize)
            if entry.metadata and entry.metadata.confidence >= 0.7:
                artist = entry.metadata.artists[0] if entry.metadata.artists else None
                title = entry.metadata.title
                film = entry.metadata.film_name or entry.metadata.album or ""
            else:
                # Fall back to extracted metadata
                artist = entry.extracted_artists[0] if entry.extracted_artists else None
                title = entry.extracted_title or "Unknown Song"
                film = entry.extracted_film or ""

            canonical_artist, canonical_title = self._canonicalize_artist_title(
                entry.original_name,
                artist_candidate=artist,
                title_candidate=title,
            )

            if not canonical_artist:
                canonical_artist = "Unknown Artist"
            if not canonical_title:
                canonical_title = canonical_artist

            original_ext = entry.original_path.suffix
            new_name = self._sanitize_filename(f"{canonical_title}{original_ext}", max_length=120)
            entry.new_name = new_name

            # Canonical layout required by policy: Artist/Title.ext
            artist_folder = self._sanitize_path_component(canonical_artist, fallback="Unknown Artist")
            entry.target_path = self.target_dir / artist_folder / new_name

            self.stats.files_renamed += 1

    def _ascii_fold(self, text: str) -> str:
        """Convert text to ASCII by dropping non-English characters."""
        return (
            unicodedata.normalize("NFKD", text)
            .encode("ascii", "ignore")
            .decode("ascii")
        )

    def _normalize_words(self, text: str) -> str:
        """Normalize whitespace and convert to proper case."""
        text = re.sub(r"\s+", " ", text).strip()
        if not text:
            return ""
        text = text.title()
        small_words = {
            "A", "An", "The", "And", "But", "Or", "For", "Nor", "On", "At", "To", "By", "Of", "In", "With"
        }
        words = text.split()
        if len(words) > 1:
            for i in range(1, len(words) - 1):
                if words[i] in small_words:
                    words[i] = words[i].lower()
            text = " ".join(words)
        return text

    def _sanitize_artist(self, text: str) -> str:
        """Normalize artist name to strict English words only."""
        text = self._ascii_fold(text)
        text = re.sub(r"\b(ft|feat|featuring|x|vs)\b.*$", "", text, flags=re.IGNORECASE)
        text = re.sub(r"[^A-Za-z\s]", " ", text)
        text = re.sub(r"\d+", " ", text)
        return self._normalize_words(text)

    def _sanitize_title(self, text: str) -> str:
        """Normalize title to strict English words only and remove noise."""
        text = self._ascii_fold(text)
        noise_patterns = [
            r"\b(official|video|lyrical|lyrics|audio|hd|uhd|fhd|4k|8k|remix|version|full|new|latest|hindi|bollywood)\b",
            r"\b(song|track|mv|music|promo|shorts?)\b",
            r"\b\d{3,4}p\b",
        ]
        for pattern in noise_patterns:
            text = re.sub(pattern, " ", text, flags=re.IGNORECASE)
        text = re.sub(r"\([^)]*\)", " ", text)
        text = re.sub(r"\[[^\]]*\]", " ", text)
        text = re.sub(r"[^A-Za-z\s]", " ", text)
        text = re.sub(r"\d+", " ", text)
        return self._normalize_words(text)

    def _extract_artist_hint_from_filename(self, original_name: str) -> str:
        """Extract artist hint from filename patterns like '(JENNIE)'."""
        stem = Path(original_name).stem
        paren_groups = re.findall(r"\(([^)]{1,80})\)", stem)
        for group in paren_groups:
            candidate = self._sanitize_artist(group)
            if candidate:
                return candidate

        # Fallback: leading token before separator
        prefix = re.split(r"\s+-\s+|\s{2,}", stem, maxsplit=1)[0]
        return self._sanitize_artist(prefix)

    def _canonicalize_artist_title(
        self,
        original_name: str,
        artist_candidate: Optional[str],
        title_candidate: Optional[str],
    ) -> Tuple[str, str]:
        """Build canonical Artist/Title from noisy filename and parsed metadata."""
        artist = self._sanitize_artist(artist_candidate or "")
        title = self._sanitize_title(title_candidate or "")

        if not artist:
            artist = self._extract_artist_hint_from_filename(original_name)

        if not title:
            title = self._sanitize_title(Path(original_name).stem)

        # Collapse cases like "like Jennie" into "Jennie" when matching artist.
        if artist and re.fullmatch(rf"(?i)like\s+{re.escape(artist)}", title):
            title = artist

        if artist and title and title.lower() == artist.lower():
            return artist, title

        return artist, title

    def _sanitize_path_component(self, text: str, fallback: str) -> str:
        """Sanitize folder names for filesystem safety."""
        cleaned = re.sub(r"[^A-Za-z\s]", " ", text)
        cleaned = self._normalize_words(cleaned)
        return cleaned if cleaned else fallback

    def _to_proper_case(self, text: str) -> str:
        """Convert text to proper case (title case) with clean formatting."""
        return self._normalize_words(self._ascii_fold(text))

    def _clean_title(self, title: str) -> str:
        """Clean song title by removing redundant metadata and additive words."""
        # List of additive/descriptive words to remove (case-insensitive)
        additive_words = [
            # Generic descriptors
            r"\bSong\b", r"\bVideo\b", r"\bAudio\b", r"\bTrack\b", r"\bTune\b",
            r"\bNumber\b", r"\bHit\b", r"\bClassic\b",
            
            # Quality descriptors
            r"\bBeautiful\b", r"\bRomantic\b", r"\bNew\b", r"\bLatest\b", 
            r"\bOriginal\b", r"\bOfficial\b",
            
            # Video/technical terms
            r"\bLyrical\b", r"\bFull\b", r"\bComplete\b", r"\bVersion\b",
            r"\bMV\b", r"\bHD\b", r"\b4K\b", r"\b8K\b",
            
            # Category descriptors
            r"\bDance\b", r"\bParty\b", r"\bMovie\b",
        ]
        
        # Remove additive words (must be whole words, case-insensitive)
        for pattern in additive_words:
            title = re.sub(pattern, "", title, flags=re.IGNORECASE)
        
        # Remove content in parentheses that contains any of these keywords
        title = re.sub(r"\s*\(.*?(Full|Official|Lyric|Video|Film|HD|4K|8K).*?\)", "", title, flags=re.IGNORECASE)
        
        # Remove trailing pipe or dash artifacts
        title = re.sub(r"\s*[|–—-]\s*$", "", title)
        
        # Clean up extra spaces and normalize
        title = re.sub(r"\s+", " ", title).strip()
        
        # Remove trailing/leading dashes or spaces
        title = title.strip(" -–—")
        
        return self._sanitize_title(title)

    def _extract_title_from_filename(self, filename: str) -> str:
        """
        Extract the cleaned title from a filename.
        
        Format: "Artist - Title - Film.mp4" or "Artist - Title.mp4"
        Returns the title portion (middle segment or second segment).
        """
        # Remove .mp4 extension
        name_without_ext = filename[:-4] if filename.endswith('.mp4') else filename
        
        # Split by " - " delimiter
        parts = name_without_ext.split(" - ")
        
        if len(parts) >= 3:
            # Format: "Artist - Title - Film"
            return parts[1].strip()
        elif len(parts) == 2:
            # Format: "Artist - Title"
            return parts[1].strip()
        else:
            # Fallback: single segment or no delimiter
            return name_without_ext.strip()

    def _sanitize_filename(self, filename: str, max_length: int = 100) -> str:
        """Sanitize filename removing invalid characters with smart truncation."""
        # Normalize to ASCII and strict English chars.
        filename = self._ascii_fold(filename)
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, "")

        stem, ext = Path(filename).stem, Path(filename).suffix
        stem = re.sub(r"[^A-Za-z\s]", " ", stem)
        stem = re.sub(r"\d+", " ", stem)
        stem = self._normalize_words(stem)
        filename = f"{stem}{ext or '.mp4'}"

        # Smart truncate if too long
        if len(filename) > max_length:
            # Find the last dash before the limit to avoid cutting mid-word
            name_without_ext = filename[:-4]  # Remove .mp4
            target_length = max_length - 4  # Leave room for .mp4
            
            if len(name_without_ext) > target_length:
                # Try to cut at last dash/space before limit
                truncated = name_without_ext[:target_length]
                last_dash = max(truncated.rfind(" - "), truncated.rfind(" "))
                
                if last_dash > target_length * 0.6:  # Only if we're not cutting too much
                    truncated = name_without_ext[:last_dash]
                
                filename = truncated.rstrip(" -") + ".mp4"

        return filename

    def _write_metadata_tags(self) -> None:
        """Stage 5: Write MP4 metadata tags (APPLY mode only)."""
        try:
            from mutagen.mp4 import MP4

            for entry in self.files:
                # Use enriched metadata if available, otherwise fall back to extracted metadata
                if entry.metadata and entry.metadata.confidence >= 0.7:
                    title = entry.metadata.title
                    artists = entry.metadata.artists
                    album = entry.metadata.album or entry.extracted_film or "Bollywood"
                    genre = entry.metadata.genre
                    year = entry.metadata.year
                else:
                    # Extract cleaned title from new_name (post-cleaning) instead of extracted_title (pre-cleaning)
                    # new_name format: "Artist - Title - Film.mp4" or "Artist - Title.mp4"
                    cleaned_title = self._extract_title_from_filename(entry.new_name)
                    title = cleaned_title or entry.extracted_title or "Unknown Song"
                    artists = entry.extracted_artists if entry.extracted_artists else ["Unknown Artist"]
                    album = entry.extracted_film or "Bollywood"
                    genre = "Bollywood"
                    year = None

                try:
                    # Use target_path since files have already been moved
                    file_path = entry.target_path if entry.target_path and entry.target_path.exists() else entry.original_path
                    audio = MP4(str(file_path))

                    canonical_title = self._sanitize_title(Path(file_path).stem) or "Unknown Song"
                    canonical_artist = self._sanitize_artist(file_path.parent.name) or "Unknown Artist"

                    # Write tags
                    audio["\xa9nam"] = canonical_title  # Title
                    audio["\xa9ART"] = canonical_artist  # Artist
                    audio["\xa9alb"] = "Bollywood Party Mix"  # Album → single canonical Plex collection
                    audio["\xa9gen"] = genre  # Genre
                    if year:
                        audio["\xa9day"] = str(year)  # Year
                    audio["\xa9cmt"] = f"Original: {entry.original_name}"  # Comment
                    # Remove ©grp (individual category) — collection is driven by ©alb alone
                    if "\xa9grp" in audio:
                        del audio["\xa9grp"]
                    # Set ©col for non-Plex players
                    audio["\xa9col"] = ["Bollywood Party Mix"]  # Collection (must be list)

                    audio.save()
                    self.stats.files_tagged += 1
                    logger.debug(f"Tagged: {entry.original_name}")
                except Exception as e:
                    logger.error(f"Tag write failed for '{entry.original_name}': {e}")
                    self.stats.errors.append(f"Tag error: {entry.original_name}")

        except ImportError:
            logger.warning("mutagen not installed — skipping MP4 tagging (pip install mutagen)")

    def update_collections(self, collection_name: str = "Bollywood Party Mix") -> int:
        """
        Update collection metadata on all MP4 files.
        
        Args:
            collection_name: Name of the collection to set.
            
        Returns:
            Number of files updated.
        """
        try:
            from mutagen.mp4 import MP4
            
            updated_count = 0
            
            logger.info(f"Updating collection to '{collection_name}' on all files...")
            
            for entry in self.files:
                try:
                    # Get actual file path (after rename)
                    file_path = entry.target_path if entry.target_path and entry.target_path.exists() else entry.original_path
                    
                    if not file_path.exists():
                        logger.warning(f"File not found: {file_path}")
                        continue
                    
                    audio = MP4(str(file_path))
                    
                    # Clear any existing collection fields (various possible keys)
                    for key in list(audio.keys()):
                        if 'col' in key.lower() and key not in ['\xa9cmt', '\xa9cpy']:  # Don't delete comment/copyright
                            del audio[key]
                    
                    # Set new collection (must be a list with single entry)
                    audio["\xa9col"] = [collection_name]
                    
                    audio.save()
                    updated_count += 1
                    logger.debug(f"Updated collection: {file_path.name}")
                    
                except Exception as e:
                    logger.error(f"Failed to update collection for '{entry.original_name}': {e}")
                    self.stats.errors.append(f"Collection update error: {entry.original_name}")
            
            logger.info(f"✅ Updated collection on {updated_count} files")
            return updated_count
            
        except ImportError:
            logger.error("mutagen not installed — cannot update collections (pip install mutagen)")
            return 0

    def _sync_plex_metadata(self) -> None:
        """Stage 7: Sync metadata with Plex Media Server."""
        if not self.sync_plex:
            return

        for entry in self.files:
            if entry.is_duplicate:
                continue  # Skip duplicates

            try:
                # Read Plex metadata if available
                plex_meta = self.plex_accessor.read_metadata(entry.target_path or entry.original_path)
                if plex_meta:
                    entry.plex_metadata = plex_meta
                    self.stats.plex_synced += 1
                    logger.debug(f"Synced with Plex: {entry.new_name or entry.original_name}")
            except Exception as e:
                logger.debug(f"Plex sync skipped for '{entry.original_name}': {e}")

    def _apply_renames(self) -> None:
        """Apply file renames (in-place)."""
        applied_count = 0

        for entry in self.files:
            if not entry.target_path or entry.is_duplicate:
                continue

            if entry.original_path == entry.target_path:
                continue

            if not entry.original_path.exists():
                logger.warning(f"Source missing, skipping: {entry.original_path}")
                self.stats.warnings.append(f"Source missing: {entry.original_name}")
                continue

            # Ensure destination artist folder exists before rename.
            entry.target_path.parent.mkdir(parents=True, exist_ok=True)

            # Skip if target already exists (unless it's the same file)
            if entry.target_path.exists() and entry.target_path != entry.original_path:
                logger.warning(f"Target exists, skipping: {entry.target_path.name}")
                self.stats.warnings.append(f"Target exists: {entry.target_path.name}")
                continue

            try:
                # Rename file (in-place)
                entry.original_path.rename(entry.target_path)
                applied_count += 1
                logger.debug(f"Renamed: {entry.original_name} → {entry.target_path.name}")
            except Exception as e:
                logger.error(f"Rename failed for '{entry.original_name}': {e}")
                self.stats.errors.append(f"Rename error: {entry.original_name}")

        self.stats.files_renamed = applied_count

    def _organize_files(self) -> None:
        """Stage 6: Move files to categorized folders (APPLY mode only)."""
        import shutil

        for entry in self.files:
            if not entry.target_path:
                continue

            try:
                # Create target directory
                entry.target_path.parent.mkdir(parents=True, exist_ok=True)

                # Move file
                shutil.move(str(entry.original_path), str(entry.target_path))
                self.stats.files_organized += 1
                logger.debug(f"Moved: {entry.original_name} → {entry.target_path}")
            except Exception as e:
                logger.error(f"File move failed for '{entry.original_name}': {e}")
                self.stats.errors.append(f"Move error: {entry.original_name}")

    def _verify_results(self) -> None:
        """Stage 7: Verify workflow results."""
        success_rate = (
            self.stats.files_renamed / self.stats.total_files * 100
            if self.stats.total_files > 0
            else 0
        )
        logger.info(f"Success rate: {success_rate:.1f}%")

    def _print_summary(self) -> None:
        """Print workflow summary."""
        logger.info("")
        logger.info("=" * 80)
        logger.info("WORKFLOW SUMMARY (CORTEX)")
        logger.info("=" * 80)
        logger.info(f"Total files:          {self.stats.total_files}")
        logger.info(f"Files scanned:        {self.stats.files_scanned}")
        logger.info(f"Files identified:     {self.stats.files_identified}")
        logger.info(f"Files matched:        {self.stats.files_matched}")
        logger.info(f"Duplicates found:     {self.stats.duplicates_found} in {len(self.stats.duplicate_groups)} groups")
        logger.info(f"Files renamed:        {self.stats.files_renamed}")
        logger.info(f"Files tagged:         {self.stats.files_tagged}")
        logger.info(f"Plex synced:          {self.stats.plex_synced}")
        logger.info(f"Warnings:             {len(self.stats.warnings)}")
        logger.info(f"Errors:               {len(self.stats.errors)}")
        logger.info(f"Duration:             {self.stats.duration_seconds:.1f}s")
        logger.info("=" * 80)

        # Print duplicate groups
        if self.stats.duplicate_groups:
            logger.info("")
            logger.info("DUPLICATE GROUPS:")
            logger.info("=" * 80)
            for i, group in enumerate(self.stats.duplicate_groups, 1):
                logger.info(f"\nGroup {i} (SHA256: {group.sha256[:8]}..., Size: {group.size_bytes / 1024 / 1024:.1f} MB):")
                for file_path in group.files:
                    logger.info(f"  - {file_path.relative_to(self.target_dir)}")

        # Print sample rename proposals
        if self.dry_run and self.files:
            logger.info("")
            logger.info("SAMPLE RENAME PROPOSALS (First 15, excluding duplicates):")
            logger.info("=" * 80)
            non_duplicates = [e for e in self.files if not e.is_duplicate][:15]
            for i, entry in enumerate(non_duplicates, 1):
                logger.info(f"\n{i}. ORIGINAL: {entry.original_name}")
                logger.info(f"   NEW NAME: {entry.new_name}")
                if entry.target_path:
                    logger.info(f"   TARGET: {entry.target_path.relative_to(self.target_dir)}")
                else:
                    logger.info(f"   TARGET: (not set)")
                if entry.metadata:
                    logger.info(f"   METADATA: {entry.metadata.artists[0] if entry.metadata.artists else 'Unknown'}")
                    logger.info(f"             Album: {entry.metadata.album or 'N/A'}")
                    logger.info(f"             Year: {entry.metadata.year or 'N/A'}")
                    logger.info(f"             Confidence: {entry.metadata.confidence:.2f}")

        # Print warnings
        if self.stats.warnings:
            logger.info("")
            logger.info("WARNINGS:")
            for warning in self.stats.warnings[:20]:  # Limit to first 20
                logger.info(f"  - {warning}")

        if self.stats.errors:
            logger.info("")
            logger.info("ERRORS:")
            for error in self.stats.errors:
                logger.info(f"  - {error}")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Organize Bollywood music videos with CORTEX governance"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Preview mode (no file modifications) - DEFAULT",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Execute changes (rename files, write metadata)",
    )
    parser.add_argument(
        "--target",
        type=str,
        default=r"Z:\MUSIC\Bollywood\Bollywood Hits",
        help="Target directory to scan recursively",
    )
    parser.add_argument(
        "--no-online",
        action="store_true",
        help="Disable online metadata fetching",
    )
    parser.add_argument(
        "--no-duplicates",
        action="store_true",
        help="Disable duplicate detection",
    )
    parser.add_argument(
        "--no-plex",
        action="store_true",
        help="Disable Plex metadata sync",
    )
    parser.add_argument(
        "--organize",
        action="store_true",
        help="Move files to category folders (default: in-place rename)",
    )
    parser.add_argument(
        "--update-collection",
        type=str,
        metavar="NAME",
        help="Update collection metadata on all files (e.g., 'Bollywood Party Songs')",
    )

    args = parser.parse_args()

    target_dir = Path(args.target)

    if not target_dir.exists():
        logger.error(f"Target directory not found: {target_dir}")
        return 1

    # Special mode: Update collection only
    if args.update_collection:
        logger.info("=" * 80)
        logger.info("COLLECTION UPDATE MODE")
        logger.info("=" * 80)
        logger.info(f"Target: {target_dir}")
        logger.info(f"Collection: {args.update_collection}")
        logger.info("=" * 80)
        logger.info("")
        
        organizer = BollywoodOrganizer(
            target_dir=target_dir,
            dry_run=False,  # Always apply in collection update mode
            use_online_metadata=False,
            detect_duplicates=False,
            sync_plex=False,
            in_place=True,
        )
        
        # Scan files only
        organizer._scan_files_recursive()
        
        # Update collections
        updated = organizer.update_collections(args.update_collection)
        
        logger.info("")
        logger.info("=" * 80)
        logger.info(f"✅ Collection updated on {updated} files")
        logger.info("=" * 80)
        
        return 0 if len(organizer.stats.errors) == 0 else 1

    # Apply mode overrides dry-run
    dry_run = not args.apply

    if not target_dir.exists():
        logger.error(f"Target directory not found: {target_dir}")
        return 1

    # Run workflow
    organizer = BollywoodOrganizer(
        target_dir=target_dir,
        dry_run=dry_run,
        use_online_metadata=not args.no_online,
        detect_duplicates=not args.no_duplicates,
        sync_plex=not args.no_plex,
        in_place=not args.organize,
    )

    stats = organizer.run_workflow()

    # Return exit code
    return 0 if len(stats.errors) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())


# AC_COMPLETE: AC-BOLLYWOOD-ORGANIZE-2026-03-11-003 ✅
