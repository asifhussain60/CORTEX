"""
Tag existing Bollywood music files with MP4 metadata for PLEX.

This script updates MP4 metadata tags for files that have already been organized
into the Bollywood directory structure.

Usage:
    python scripts/tag_bollywood_files.py

AC_START: AC-TAG-BOLLYWOOD-2026-03-11-001
"""

import logging
import sys
from pathlib import Path
from typing import Dict, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def parse_filename(filename: str) -> Dict[str, any]:
    """Parse organized filename to extract metadata."""
    # Format: "Artist - Title - Film.mp4" or "Artist - Title.mp4"
    name = filename.replace(".mp4", "").strip()
    
    parts = [p.strip() for p in name.split(" - ")]
    
    if len(parts) >= 3:
        return {
            "artist": parts[0],
            "title": parts[1],
            "film": parts[2],
        }
    elif len(parts) == 2:
        return {
            "artist": parts[0],
            "title": parts[1],
            "film": None,
        }
    else:
        # Compilation or single-word title
        return {
            "artist": None,
            "title": parts[0] if parts else name,
            "film": None,
        }


def tag_file(file_path: Path, category: str) -> bool:
    """Write MP4 metadata tags to a single file."""
    try:
        from mutagen.mp4 import MP4
    except ImportError:
        logger.error("mutagen library not installed. Run: pip install mutagen")
        return False

    # Parse filename
    parsed = parse_filename(file_path.name)
    
    try:
        audio = MP4(str(file_path))
        
        # Write tags
        audio["\xa9nam"] = parsed["title"]  # Title
        if parsed["artist"]:
            audio["\xa9ART"] = parsed["artist"]  # Artist
        else:
            audio["\xa9ART"] = "Various Artists"
        
        audio["\xa9alb"] = parsed["film"] or "Bollywood"  # Album (Film name)
        audio["\xa9gen"] = "Bollywood"  # Genre
        audio["\xa9grp"] = category  # Grouping (Category)
        audio["\xa9cmt"] = f"Organized by CORTEX"  # Comment
        
        audio.save()
        logger.debug(f"Tagged: {file_path.name}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to tag {file_path.name}: {e}")
        return False


def main() -> int:
    """Tag all MP4 files in Bollywood directory."""
    bollywood_dir = Path(r"Z:\MUSIC\Bollywood")
    
    if not bollywood_dir.exists():
        logger.error(f"Bollywood directory not found: {bollywood_dir}")
        return 1
    
    logger.info("=" * 80)
    logger.info("BOLLYWOOD MUSIC METADATA TAGGING")
    logger.info("=" * 80)
    logger.info(f"Directory: {bollywood_dir}")
    logger.info("=" * 80)
    logger.info("")
    
    # Get all categories
    categories = {
        "Bollywood Hits": bollywood_dir / "Bollywood Hits",
        "Compilations/Mashups": bollywood_dir / "Compilations" / "Mashups",
        "Compilations": bollywood_dir / "Compilations",
        "Party & Dance": bollywood_dir / "Party & Dance",
        "Romantic": bollywood_dir / "Romantic",
    }
    
    total_files = 0
    tagged_files = 0
    errors = 0
    
    for category_name, category_path in categories.items():
        if not category_path.exists():
            continue
        
        mp4_files = list(category_path.glob("*.mp4"))
        logger.info(f"Processing {len(mp4_files)} files in {category_name}...")
        
        for file_path in mp4_files:
            total_files += 1
            if tag_file(file_path, category_name):
                tagged_files += 1
            else:
                errors += 1
    
    logger.info("")
    logger.info("=" * 80)
    logger.info("TAGGING SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Total files:     {total_files}")
    logger.info(f"Files tagged:    {tagged_files}")
    logger.info(f"Errors:          {errors}")
    logger.info("=" * 80)
    
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())


# AC_COMPLETE: AC-TAG-BOLLYWOOD-2026-03-11-001 ✅
