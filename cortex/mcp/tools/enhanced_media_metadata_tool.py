"""
cortex/mcp/tools/enhanced_media_metadata_tool.py

Enhanced MCP tool for comprehensive video metadata extraction and writing.

Exposes enhanced metadata operations:
- `extract_rich_metadata` — Extract studio, genres, performers, tags from filename
- `write_rich_metadata` — Write comprehensive iTunes/MP4 tags to files
- `batch_enrich_metadata` — Bulk metadata extraction and writing with proper case conversion
- `analyze_metadata_patterns` — Analyze metadata patterns in directory

CORTEX Standards:
- CORE-011: Type hints on all functions
- CORE-012: Docstrings on all public APIs
- CORE-028: snake_case naming only
- TDD-first: Tested before use

AC_START: AC-ENHANCED-METADATA-2026-02-23-006
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class MetadataExtraction:
    """Result of metadata extraction from filename."""

    filename: str
    title: str
    studio: Optional[str] = None
    performers: List[str] = None
    genres: List[str] = None
    resolution: Optional[str] = None
    date: Optional[str] = None
    episode_num: Optional[int] = None
    tags: List[str] = None
    confidence: float = 1.0

    def __post_init__(self) -> None:
        """Initialize list defaults."""
        if self.performers is None:
            self.performers = []
        if self.genres is None:
            self.genres = []
        if self.tags is None:
            self.tags = []


def cortex_extract_rich_metadata(
    filename: str,
    studio_context: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Extract comprehensive metadata from a filename.

    Extracts: studio, performers, genres, resolution, date, episode numbers, tags.
    Applies intelligent parsing and proper case conversion.

    Args:
        filename: Video filename (e.g., "AboutAWomanScene6_s06_jessicadrake_DevinnLane_480p_h264").
        studio_context: Known studio name for validation (e.g., "Vixen").

    Returns:
        Dict with keys:
        - `success`: Extraction completed.
        - `title`: Cleaned title (proper case).
        - `studio`: Detected studio name (proper case).
        - `performers`: List of extracted performer names (proper case).
        - `genres`: List of detected genres.
        - `resolution`: Video resolution (720p, 1080p, etc).
        - `date`: Extracted date if present.
        - `episode_num`: Episode number if present.
        - `tags`: All extracted metadata tags.
        - `confidence`: Confidence score (0.0-1.0).

    Example::

        meta = cortex_extract_rich_metadata(
            "AboutAWomanScene6_s06_jessicadrake_DevinnLane_480p_h264",
            studio_context="Vixen"
        )
        print(f"Title: {meta['title']}")
        print(f"Performers: {meta['performers']}")
        print(f"Resolution: {meta['resolution']}")
    """
    try:
        # Remove extension
        base_name = filename.rsplit(".", 1)[0] if "." in filename else filename

        # Initialize extraction result
        result: Dict[str, Any] = {
            "success": True,
            "filename": filename,
            "title": base_name,
            "studio": studio_context,
            "performers": [],
            "genres": [],
            "resolution": None,
            "date": None,
            "episode_num": None,
            "tags": [],
            "confidence": 1.0,
        }

        # Remove video codec info (h264, h265, x264, etc.)
        clean_name = re.sub(r"[_\-]*(x264|x265|h264|h265|hevc|avc)", "", base_name, flags=re.IGNORECASE)
        clean_name = re.sub(r"[_\-]*(mkv|mp4|m4v|avi)$", "", clean_name, flags=re.IGNORECASE)

        # Extract resolution
        resolution_match = re.search(r"(\d{3,4})p", clean_name, re.IGNORECASE)
        if resolution_match:
            result["resolution"] = f"{resolution_match.group(1)}p"
            clean_name = clean_name.replace(resolution_match.group(0), " ").strip()

        # Extract episode number (e.g., "s06", "ep6", "e06", "Scene6")
        episode_match = re.search(r"[_\-]*(s|ep|e|scene|episode)[\-_]?(\d+)", clean_name, re.IGNORECASE)
        if episode_match:
            result["episode_num"] = int(episode_match.group(2))
            clean_name = re.sub(r"[_\-]*(s|ep|e|scene|episode)[\-_]?\d+", "", clean_name, flags=re.IGNORECASE).strip()

        # Extract date (YYYY-MM-DD or YYYYMMDD)
        date_match = re.search(r"(\d{4})[_\-]?(\d{2})[_\-]?(\d{2})", clean_name)
        if date_match:
            result["date"] = f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}"
            clean_name = clean_name.replace(date_match.group(0), " ").strip()

        # Common studio names (case-insensitive)
        studios = {
            "bellesa": "Bellesa",
            "sexart": "SexArt",
            "vixen": "Vixen",
            "tushy": "TUSHY",
            "deeper": "Deeper",
            "holed": "Holed",
            "wicked": "Wicked",
            "brazzers": "Brazzers",
            "bangbros": "BangBros",
            "pureporn": "PurePorn",
            "passionate": "Passionate",
            "lubed": "Lubed",
            "ella hughes": "Ella Hughes",
            "jessica drake": "Jessica Drake",
            "squirt": "Squirt",
        }

        for studio_key, studio_name in studios.items():
            # Use pattern that works with underscores and hyphens (not just word boundaries)
            pattern = r"(?:^|[_\-\s])" + re.escape(studio_key) + r"(?:[_\-\s]|$)"
            if re.search(pattern, clean_name, re.IGNORECASE):
                result["studio"] = studio_name
                clean_name = re.sub(pattern, " ", clean_name, flags=re.IGNORECASE).strip()
                break

        # Extract performer names (typically capitalized words or after underscores)
        # Performers are usually proper names (CamelCase or capitals) appearing after title
        potential_performers = re.split(r"[_\-]+", clean_name)
        
        # Common words that are NOT performer names (common nouns, verbs, articles, etc.)
        common_words = {
            "a", "the", "and", "or", "in", "of", "on", "at", "to", "for", "with",
            "by", "is", "are", "has", "have", "scene", "part", "episode", "vol", "volume",
            "full", "hd", "sd", "480p", "720p", "1080p", "2160p", "uk", "us", "fr", "de",
            "es", "pt", "it", "nl", "4k", "8k", "2d", "3d", "x264", "x265", "h264", "h265",
            # Additional filtering for common words that frequently appear in titles
            "good", "bad", "hot", "wet", "dirty", "deep", "hard", "rough", "soft", "sweet",
            "her", "his", "him", "he", "she", "they", "them", "what", "who", "where",
            "fit", "fit's", "fits", "fitting",  # Common adjective/verb forms
            "fucks", "fuck", "fucking", "fucked", "sucks", "sucking", "licks",
            "kisses", "loves", "wants", "gets", "gives", "takes", "makes", "comes", "goes",
            "friend", "friends", "girl", "girls", "boy", "boys", "man", "men", "woman", "women",
            "mom", "dad", "son", "daughter", "sister", "brother", "aunt", "uncle", "cousin",
            # Studio names that might appear in title context
            "bellesa", "sexart", "vixen", "tushy", "deeper", "holed", "wicked", "brazzers",
            "bangbros", "pureporn", "passionate", "lubed",
        }
        
        # Strategy: performers are usually later in the filename, proper-cased
        # Look for CamelCase words (at least one capital letter in middle)
        for token in potential_performers:
            token_lower = token.lower().strip()
            
            # Filter out noise - must pass multiple checks
            if (len(token) > 2 and 
                token_lower not in common_words and
                not re.match(r"^\d+$", token) and
                not token_lower.startswith(("http", "www", "ftp")) and
                # Performer names usually have capitals (CamelCase) or are all lowercase after processing
                (re.search(r"[A-Z]", token) or len(token) > 4)):  # Either has caps or is long enough
                
                # Handle CamelCase - split on case boundaries
                # Convert "JessicaDrake" -> "Jessica Drake"
                camel_split = re.sub(r"([a-z])([A-Z])", r"\1 \2", token)
                
                # Convert to proper case (Title Case)
                # Handle multiple words separated by camelCase or underscores
                words = camel_split.split()
                proper_name = " ".join(word.capitalize() for word in words if word and word.lower() not in common_words)
                
                # Additional validation: performer names typically have 2+ words (First Last)
                # or are single but CamelCase (indicating compound name)
                if proper_name and proper_name not in result["performers"]:
                    # Only add if it's a credible performer name
                    # (contains at least one uppercase, or multiple words, or matches known patterns)
                    word_count = len(proper_name.split())
                    has_capitals = any(c.isupper() for c in proper_name)
                    if (word_count >= 2 or has_capitals or re.search(r"[A-Z]{2,}", token)):
                        result["performers"].append(proper_name)

        # Convert title to proper case (Title Case with CamelCase handling)
        # Split clean_name by underscores/hyphens and reconstruct
        title_parts = re.split(r"[_\-]+", clean_name)
        
        cleaned_parts = []
        for part in title_parts:
            if part:
                # Handle CamelCase: "SethGamble" -> "Seth Gamble"
                camel_split = re.sub(r"([a-z])([A-Z])", r"\1 \2", part)
                # Title case each word
                title_cased = " ".join(word.capitalize() for word in camel_split.split() if word)
                if title_cased:
                    cleaned_parts.append(title_cased)
        
        proper_title = " ".join(cleaned_parts).strip()
        result["title"] = proper_title or "Untitled"

        # Build comprehensive tags list
        result["tags"] = []
        if result["studio"]:
            result["tags"].append(result["studio"])
        result["tags"].extend(result["performers"])
        if result["resolution"]:
            result["tags"].append(result["resolution"])
        if result["date"]:
            result["tags"].append(result["date"][:4])  # Year

        # Adjust confidence based on extraction quality (stricter scoring)
        confidence = 1.0
        
        # Confidence penalties for missing/poor quality extractions
        if not result["studio"]:
            confidence -= 0.15
        if len(result["performers"]) < 1:
            confidence -= 0.15
        if not result["resolution"]:
            confidence -= 0.10
        
        # Penalty for very short titles (likely incomplete extraction)
        if len(result["title"]) < 4:
            confidence -= 0.20
        
        # Penalty for title with excessive underscores (case conversion failed)
        if "_" in result["title"]:
            confidence -= 0.25
        
        # Penalty for too many performers (over-detection)
        if len(result["performers"]) > 8:
            confidence -= 0.20
        
        # Bonus for high-quality extractions
        if result["studio"] and len(result["performers"]) >= 2 and result["resolution"]:
            confidence += 0.10
        
        result["confidence"] = max(0.0, min(1.0, confidence))

        return result

    except Exception as exc:  # noqa: BLE001
        return {
            "success": False,
            "error": str(exc),
            "filename": filename,
        }


def cortex_write_rich_metadata(
    file_path: str,
    metadata: Dict[str, Any],
    dry_run: bool = True,
) -> Dict[str, Any]:
    """
    Write comprehensive metadata to an MP4/M4V video file.

    Writes iTunes-compatible tags including title, artist, album, genre, comments.

    Args:
        file_path: Path to video file.
        metadata: Metadata dict from cortex_extract_rich_metadata.
        dry_run: Preview mode (don't write if True).

    Returns:
        Dict with keys:
        - `success`: Write completed.
        - `file`: Filename.
        - `tags_written`: Dict of tag_name -> value written.
        - `dry_run`: Whether this was a dry run.

    Example::

        meta = cortex_extract_rich_metadata("video.mp4")
        result = cortex_write_rich_metadata("video.mp4", meta, dry_run=False)
        print(f"Tags written: {result['tags_written']}")
    """
    try:
        from mutagen.mp4 import MP4

        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            return {
                "success": False,
                "error": f"File not found: {file_path}",
            }

        # Map metadata to iTunes atoms
        tags_to_write = {}

        if metadata.get("title"):
            tags_to_write["\xa9nam"] = [metadata["title"]]  # Title

        if metadata.get("studio"):
            tags_to_write["\xa9alb"] = [metadata["studio"]]  # Album -> Studio

        if metadata.get("performers"):
            # Join performers as artist
            tags_to_write["\xa9ART"] = [", ".join(metadata["performers"])]

        # Genre tag
        genres = metadata.get("genres", [])
        if genres:
            tags_to_write["\xa9gen"] = [", ".join(genres)]
        elif metadata.get("studio"):
            # Default genre based on studio
            tags_to_write["\xa9gen"] = ["Adult"]

        # Comments with metadata summary
        comments_parts = []
        if metadata.get("resolution"):
            comments_parts.append(f"Resolution: {metadata['resolution']}")
        if metadata.get("episode_num"):
            comments_parts.append(f"Episode: {metadata['episode_num']}")
        if metadata.get("date"):
            comments_parts.append(f"Date: {metadata['date']}")

        if comments_parts:
            tags_to_write["\xa9cmt"] = [" | ".join(comments_parts)]

        # Keywords/tags
        if metadata.get("tags"):
            tags_to_write["keyw"] = metadata["tags"]

        if dry_run:
            return {
                "success": True,
                "file": file_path_obj.name,
                "tags_to_write": tags_to_write,
                "dry_run": True,
            }

        # Write tags to file
        audio = MP4(str(file_path))
        audio.tags.clear()
        for tag_key, tag_value in tags_to_write.items():
            audio.tags[tag_key] = tag_value
        audio.save()

        return {
            "success": True,
            "file": file_path_obj.name,
            "tags_written": {k: v for k, v in tags_to_write.items()},
            "dry_run": False,
        }

    except ImportError:
        return {
            "success": False,
            "error": "mutagen library required. Install: pip install mutagen",
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "success": False,
            "error": str(exc),
            "file": file_path,
        }


def cortex_batch_enrich_metadata(
    root_path: str = "G:\\FLICKS\\_backlog",
    dry_run: bool = True,
    max_files: int = 100,
) -> Dict[str, Any]:
    """
    Batch extract and write rich metadata to all video files.

    Args:
        root_path: Root directory to scan.
        dry_run: Preview mode (don't write if True).
        max_files: Max files to process (default: 100).

    Returns:
        Dict with keys:
        - `success`: Operation completed.
        - `files_processed`: Total files analyzed.
        - `metadata_extractions`: List of extraction results.
        - `tags_written`: Total tags written (or would write in dry_run).
        - `avg_confidence`: Average confidence score.

    Example::

        result = cortex_batch_enrich_metadata(
            root_path="G:\\\\FLICKS\\\\_backlog",
            dry_run=True
        )
        print(f"Would write {result['tags_written']} tags to {result['files_processed']} files")
    """
    try:
        root = Path(root_path)
        if not root.exists():
            return {
                "success": False,
                "error": f"Path not found: {root_path}",
            }

        # Get all video files
        video_extensions = {".mp4", ".mkv", ".m4v", ".avi", ".webm", ".mov"}
        all_files = sorted(
            [f for f in root.iterdir() if f.is_file() and f.suffix.lower() in video_extensions]
        )[:max_files]

        extractions = []
        total_confidence = 0
        tags_written_count = 0

        for video_file in all_files:
            # Extract metadata
            extraction = cortex_extract_rich_metadata(video_file.name)

            if extraction.get("success"):
                extractions.append(extraction)
                total_confidence += extraction.get("confidence", 0)

                # Write metadata
                write_result = cortex_write_rich_metadata(
                    str(video_file),
                    extraction,
                    dry_run=dry_run,
                )

                if write_result.get("success"):
                    tags_written_count += len(
                        write_result.get("tags_written", write_result.get("tags_to_write", {}))
                    )

        avg_confidence = total_confidence / len(extractions) if extractions else 0

        return {
            "success": True,
            "files_processed": len(all_files),
            "metadata_extractions": extractions[:20],  # Limit output
            "total_extractions": len(extractions),
            "tags_written": tags_written_count,
            "avg_confidence": round(avg_confidence, 2),
            "dry_run": dry_run,
        }

    except Exception as exc:  # noqa: BLE001
        return {
            "success": False,
            "error": str(exc),
            "files_processed": 0,
        }


def cortex_analyze_metadata_patterns(
    root_path: str = "G:\\__Backlog",
    sample_size: int = 100,
) -> Dict[str, Any]:
    """
    Analyze metadata patterns across a directory to guide extraction.

    Args:
        root_path: Root directory to scan.
        sample_size: Number of files to sample (default: 100).

    Returns:
        Dict with keys:
        - `success`: Analysis completed.
        - `total_files`: Total video files in directory.
        - `studios_detected`: Dict of studio -> count.
        - `resolutions`: Dict of resolution -> count.
        - `common_performers`: List of top performers.
        - `date_usage`: % of files with dates.
        - `episode_usage`: % of files with episode numbers.
        - `naming_pattern_samples`: Example filenames.

    Example::

        patterns = cortex_analyze_metadata_patterns("G:\\\\__Backlog")
        print(f"Most common studio: {patterns['studios_detected']}")
    """
    try:
        root = Path(root_path)
        if not root.exists():
            return {
                "success": False,
                "error": f"Path not found: {root_path}",
            }

        # Get all video files
        video_extensions = {".mp4", ".mkv", ".m4v", ".avi", ".webm", ".mov"}
        all_files = sorted(
            [f for f in root.rglob("*") if f.is_file() and f.suffix.lower() in video_extensions]
        )

        pattern_stats = {
            "studios": {},
            "resolutions": {},
            "performers": {},
            "has_dates": 0,
            "has_episodes": 0,
            "samples": [],
        }

        sample_files = all_files[:sample_size]

        for video_file in sample_files:
            extraction = cortex_extract_rich_metadata(video_file.name)

            if extraction.get("success"):
                # Track studios
                if extraction.get("studio"):
                    studio = extraction["studio"]
                    pattern_stats["studios"][studio] = pattern_stats["studios"].get(studio, 0) + 1

                # Track resolutions
                if extraction.get("resolution"):
                    res = extraction["resolution"]
                    pattern_stats["resolutions"][res] = pattern_stats["resolutions"].get(res, 0) + 1

                # Track performers
                for performer in extraction.get("performers", []):
                    pattern_stats["performers"][performer] = (
                        pattern_stats["performers"].get(performer, 0) + 1
                    )

                # Track dates and episodes
                if extraction.get("date"):
                    pattern_stats["has_dates"] += 1
                if extraction.get("episode_num"):
                    pattern_stats["has_episodes"] += 1

                # Collect samples
                pattern_stats["samples"].append(
                    {
                        "filename": video_file.name,
                        "title": extraction.get("title"),
                        "studio": extraction.get("studio"),
                    }
                )

        return {
            "success": True,
            "total_files": len(all_files),
            "sampled_files": len(sample_files),
            "studios_detected": dict(
                sorted(pattern_stats["studios"].items(), key=lambda x: -x[1])[:10]
            ),
            "resolutions": dict(
                sorted(pattern_stats["resolutions"].items(), key=lambda x: -x[1])
            ),
            "top_performers": dict(
                sorted(pattern_stats["performers"].items(), key=lambda x: -x[1])[:15]
            ),
            "date_usage_percent": round((pattern_stats["has_dates"] / len(sample_files) * 100), 1)
            if sample_files
            else 0,
            "episode_usage_percent": round(
                (pattern_stats["has_episodes"] / len(sample_files) * 100), 1
            )
            if sample_files
            else 0,
            "naming_pattern_samples": pattern_stats["samples"][:5],
        }

    except Exception as exc:  # noqa: BLE001
        return {
            "success": False,
            "error": str(exc),
        }


# AC_COMPLETE: AC-ENHANCED-METADATA-2026-02-23-006 ✅
