"""
Plex Library Refresh Utility

Triggers Plex Media Server to scan and refresh metadata for a specific library section.
Works with Plex REST API (requires authentication token).
"""

import logging
import sys
from pathlib import Path
from typing import Optional
import urllib.request
import urllib.parse
import json
import configparser

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


class PlexLibraryRefresher:
    """Triggers Plex library scan/refresh operations via REST API."""
    
    def __init__(self, plex_url: str = "http://localhost:32400", token: Optional[str] = None):
        """
        Initialize Plex refresher.
        
        Args:
            plex_url: Plex server URL (default: http://localhost:32400)
            token: Plex authentication token (auto-detected if None)
        """
        self.plex_url = plex_url.rstrip("/")
        self.token = token or self._detect_token()
        
        if not self.token:
            raise ValueError(
                "Plex token not found. Set PLEX_TOKEN environment variable or "
                "provide via --token argument"
            )
    
    def _detect_token(self) -> Optional[str]:
        """Auto-detect Plex token from standard config location."""
        config_paths = [
            Path.home() / "AppData/Local/Plex Media Server/Preferences.xml",
            Path("C:/Program Files/Plex/Plex Media Server/Preferences.xml"),
            Path.home() / "Library/Application Support/Plex Media Server/Preferences.xml",
        ]
        
        for config_path in config_paths:
            if config_path.exists():
                try:
                    content = config_path.read_text(encoding="utf-8")
                    # Extract PlexOnlineToken from Preferences.xml
                    import re
                    match = re.search(r'PlexOnlineToken="([^"]+)"', content)
                    if match:
                        logger.info(f"Detected Plex token from {config_path}")
                        return match.group(1)
                except Exception as e:
                    logger.debug(f"Failed to read token from {config_path}: {e}")
        
        return None
    
    def get_library_sections(self) -> dict:
        """
        Get all library sections from Plex.
        
        Returns:
            Dict mapping section name → section ID
        """
        url = f"{self.plex_url}/library/sections?X-Plex-Token={self.token}"
        
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode())
                
                sections = {}
                for section in data.get("MediaContainer", {}).get("Directory", []):
                    sections[section["title"]] = section["key"]
                
                return sections
        
        except Exception as e:
            logger.error(f"Failed to get library sections: {e}")
            return {}
    
    def scan_library(self, section_id: str) -> bool:
        """
        Trigger a library scan for a specific section.
        
        Args:
            section_id: Plex library section ID
            
        Returns:
            True if scan triggered successfully
        """
        url = f"{self.plex_url}/library/sections/{section_id}/refresh?X-Plex-Token={self.token}"
        
        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    logger.info(f"✅ Library scan triggered for section {section_id}")
                    return True
                else:
                    logger.error(f"Unexpected response: {response.status}")
                    return False
        
        except Exception as e:
            logger.error(f"Failed to trigger scan: {e}")
            return False
    
    def refresh_library_by_name(self, library_name: str) -> bool:
        """
        Refresh a library by name.
        
        Args:
            library_name: Name of the Plex library (e.g., "Music", "Movies")
            
        Returns:
            True if refresh triggered successfully
        """
        sections = self.get_library_sections()
        
        if not sections:
            logger.error("No library sections found")
            return False
        
        logger.info(f"Available libraries: {', '.join(sections.keys())}")
        
        # Try exact match first
        if library_name in sections:
            section_id = sections[library_name]
            logger.info(f"Found library '{library_name}' with ID {section_id}")
            return self.scan_library(section_id)
        
        # Try partial match (case-insensitive)
        for name, section_id in sections.items():
            if library_name.lower() in name.lower():
                logger.info(f"Found library '{name}' (partial match) with ID {section_id}")
                return self.scan_library(section_id)
        
        logger.error(f"Library '{library_name}' not found")
        return False
    
    def refresh_all_libraries(self) -> int:
        """
        Refresh all Plex libraries.
        
        Returns:
            Number of libraries successfully refreshed
        """
        sections = self.get_library_sections()
        
        if not sections:
            logger.error("No library sections found")
            return 0
        
        success_count = 0
        for name, section_id in sections.items():
            logger.info(f"Refreshing library: {name}")
            if self.scan_library(section_id):
                success_count += 1
        
        return success_count


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Trigger Plex library scan/refresh")
    parser.add_argument("--library", "-l", help="Library name to refresh (default: all)", default=None)
    parser.add_argument("--url", default="http://localhost:32400", help="Plex server URL")
    parser.add_argument("--token", help="Plex authentication token (auto-detected if omitted)")
    parser.add_argument("--list", action="store_true", help="List all libraries and exit")
    
    args = parser.parse_args()
    
    try:
        refresher = PlexLibraryRefresher(plex_url=args.url, token=args.token)
        
        if args.list:
            sections = refresher.get_library_sections()
            print("\nAvailable Plex Libraries:")
            print("=" * 50)
            for name, section_id in sections.items():
                print(f"  {name} (ID: {section_id})")
            return 0
        
        if args.library:
            success = refresher.refresh_library_by_name(args.library)
            return 0 if success else 1
        else:
            count = refresher.refresh_all_libraries()
            logger.info(f"Refreshed {count} libraries")
            return 0 if count > 0 else 1
    
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
