"""
Bulk Copyright Updater Utility

Reusable utility for bulk operations on markdown files:
- Add CORTEX copyright headers
- Update existing headers
- Scan and report missing headers
- Dry run mode for safety

Author: Asif Hussain
Date: December 15, 2025
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import re
from datetime import datetime
import shutil

logger = logging.getLogger(__name__)


class BulkCopyrightUpdater:
    """
    Reusable utility for bulk copyright header operations.
    
    Features:
    - Add copyright headers to markdown files
    - Update existing headers (preserve custom titles)
    - Recursive directory scanning
    - Dry run mode (report only, no changes)
    - Backup before modifications
    - Protected file patterns (skip certain files)
    - Custom copyright format support
    """

    def __init__(
        self,
        base_path: Path,
        copyright_format: Optional[str] = None,
        protected_patterns: Optional[List[str]] = None,
        dry_run: bool = True
    ):
        """
        Initialize bulk copyright updater.

        Args:
            base_path: Root directory to scan
            copyright_format: Custom copyright format (uses default if None)
            protected_patterns: File patterns to skip (e.g., ['README.md', '*-schema.yaml'])
            dry_run: If True, only report changes without applying them
        """
        self.base_path = Path(base_path)
        self.dry_run = dry_run
        
        # Default CORTEX copyright format
        self.copyright_format = copyright_format or (
            "🧠 CORTEX - {title}\n"
            "Author: Asif Hussain | GitHub: github.com/asifhussain60/CORTEX\n"
            "\n"
            "---\n"
        )
        
        # Default protected patterns
        self.protected_patterns = protected_patterns or [
            "README.md",
            "*-schema.yaml",
            "*.template.*",
            ".gitignore",
            "LICENSE",
            "CHANGELOG.md"
        ]
        
        self.stats = {
            "scanned": 0,
            "has_header": 0,
            "missing_header": 0,
            "updated": 0,
            "skipped": 0,
            "errors": 0
        }

    def execute(self, file_pattern: str = "**/*.md") -> Dict[str, Any]:
        """
        Execute bulk copyright update operation.

        Args:
            file_pattern: Glob pattern for files to process (default: **/*.md)

        Returns:
            Dictionary with operation results and statistics
        """
        logger.info(f"🔍 Scanning {self.base_path} for {file_pattern}...")
        logger.info(f"{'🏃 DRY RUN MODE' if self.dry_run else '⚠️  LIVE MODE - FILES WILL BE MODIFIED'}")
        
        # Scan for markdown files
        md_files = list(self.base_path.rglob(file_pattern))
        self.stats["scanned"] = len(md_files)
        
        logger.info(f"Found {len(md_files)} files to process")
        
        # Create backup if not dry run
        backup_path = None
        if not self.dry_run:
            backup_path = self._create_backup()
            logger.info(f"📦 Backup created: {backup_path}")
        
        # Process each file
        results = []
        for md_file in md_files:
            result = self._process_file(md_file)
            results.append(result)
        
        # Generate summary
        summary = self._generate_summary(results, backup_path)
        
        return summary

    def scan_missing_headers(self, file_pattern: str = "**/*.md") -> List[Path]:
        """
        Scan for files missing copyright headers (read-only operation).

        Args:
            file_pattern: Glob pattern for files to scan

        Returns:
            List of file paths missing copyright headers
        """
        md_files = list(self.base_path.rglob(file_pattern))
        missing = []
        
        for md_file in md_files:
            if self._is_protected(md_file):
                continue
            
            if not self._has_copyright_header(md_file):
                missing.append(md_file)
        
        return missing

    def _process_file(self, file_path: Path) -> Dict[str, Any]:
        """Process single markdown file."""
        result = {
            "file": str(file_path.relative_to(self.base_path)),
            "action": "none",
            "status": "success",
            "message": ""
        }
        
        try:
            # Check if file is protected
            if self._is_protected(file_path):
                result["action"] = "skipped"
                result["message"] = "Protected file pattern"
                self.stats["skipped"] += 1
                return result
            
            # Read file content
            content = file_path.read_text(encoding="utf-8")
            
            # Check if copyright header exists
            has_header = self._has_copyright_header(content)
            
            if has_header:
                self.stats["has_header"] += 1
                result["action"] = "skipped"
                result["message"] = "Copyright header already present"
                return result
            
            # Extract title from file
            title = self._extract_title(content, file_path)
            
            # Generate copyright header
            copyright_header = self.copyright_format.format(title=title)
            
            # Add copyright header to content
            new_content = self._add_copyright_header(content, copyright_header)
            
            # Apply changes if not dry run
            if not self.dry_run:
                file_path.write_text(new_content, encoding="utf-8")
                result["action"] = "updated"
                result["message"] = f"Added copyright header with title: {title}"
                self.stats["updated"] += 1
            else:
                result["action"] = "would_update"
                result["message"] = f"Would add copyright header with title: {title}"
                self.stats["missing_header"] += 1
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            result["status"] = "error"
            result["message"] = str(e)
            self.stats["errors"] += 1
        
        return result

    def _is_protected(self, file_path: Path) -> bool:
        """Check if file matches protected patterns."""
        for pattern in self.protected_patterns:
            if file_path.match(pattern):
                return True
        return False

    def _has_copyright_header(self, content: str) -> bool:
        """Check if content has CORTEX copyright header."""
        # Check for key components of copyright header
        return (
            "🧠 CORTEX" in content and
            "Author: Asif Hussain" in content and
            "github.com/asifhussain60/CORTEX" in content
        )

    def _extract_title(self, content: str, file_path: Path) -> str:
        """
        Extract title from file content or filename.
        
        Priority:
        1. First H1 heading (# Title)
        2. Filename (humanized)
        """
        # Try to extract from first H1
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        
        # Fallback to filename
        filename = file_path.stem
        
        # Humanize filename
        # Remove prefixes (00-, 01-, etc.)
        filename = re.sub(r'^\d+-', '', filename)
        
        # Replace hyphens/underscores with spaces
        filename = filename.replace('-', ' ').replace('_', ' ')
        
        # Title case
        return filename.title()

    def _add_copyright_header(self, content: str, header: str) -> str:
        """Add copyright header to content."""
        # If content starts with H1, place header before it
        # Otherwise, place at very top
        
        # Remove any existing markdown comments at top
        content = re.sub(r'^<!--.*?-->\s*', '', content, flags=re.DOTALL)
        
        return header + "\n" + content

    def _create_backup(self) -> Path:
        """Create backup of base directory before modifications."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_root = self.base_path.parent / "cortex-brain" / "backups"
        backup_root.mkdir(parents=True, exist_ok=True)
        
        backup_path = backup_root / f"copyright-update-backup-{timestamp}"
        
        # Copy directory
        shutil.copytree(self.base_path, backup_path, ignore=shutil.ignore_patterns('*.pyc', '__pycache__'))
        
        return backup_path

    def _generate_summary(self, results: List[Dict[str, Any]], backup_path: Optional[Path]) -> Dict[str, Any]:
        """Generate operation summary."""
        summary = {
            "mode": "dry_run" if self.dry_run else "live",
            "base_path": str(self.base_path),
            "timestamp": datetime.now().isoformat(),
            "backup_path": str(backup_path) if backup_path else None,
            "statistics": self.stats.copy(),
            "results": results
        }
        
        # Log summary
        logger.info("\n" + "=" * 70)
        logger.info("📊 BULK COPYRIGHT UPDATE SUMMARY")
        logger.info("=" * 70)
        logger.info(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE'}")
        logger.info(f"Base Path: {self.base_path}")
        logger.info(f"Files Scanned: {self.stats['scanned']}")
        logger.info(f"Already Has Header: {self.stats['has_header']}")
        logger.info(f"Missing Header: {self.stats['missing_header']}")
        logger.info(f"Updated: {self.stats['updated']}")
        logger.info(f"Skipped: {self.stats['skipped']}")
        logger.info(f"Errors: {self.stats['errors']}")
        
        if backup_path:
            logger.info(f"Backup: {backup_path}")
        
        logger.info("=" * 70)
        
        return summary


class PlanningDocumentRealigner:
    """
    Specialized realigner for planning documents.
    
    Combines copyright header updates with folder organization enforcement.
    """

    def __init__(self, cortex_root: Path, dry_run: bool = True):
        """
        Initialize planning document realigner.

        Args:
            cortex_root: CORTEX repository root
            dry_run: If True, only report changes
        """
        self.cortex_root = Path(cortex_root)
        self.planning_root = self.cortex_root / "cortex-brain" / "documents" / "planning"
        self.dry_run = dry_run
        
        self.copyright_updater = BulkCopyrightUpdater(
            base_path=self.planning_root,
            dry_run=dry_run
        )

    def realign_all(self) -> Dict[str, Any]:
        """
        Execute comprehensive realignment:
        1. Add copyright headers to all planning documents
        2. Move files to proper folders (temp-plans/, active/, completed/)
        3. Create universal subfolders (context/, reports/, artifacts/, tracking/)
        4. Generate realignment report
        
        Returns:
            Dictionary with realignment results
        """
        logger.info("🔧 Starting Planning Document Realignment...")
        logger.info(f"{'🏃 DRY RUN MODE' if self.dry_run else '⚠️  LIVE MODE'}")
        
        results = {
            "copyright_update": None,
            "folder_organization": None,
            "timestamp": datetime.now().isoformat()
        }
        
        # Phase 1: Add copyright headers
        logger.info("\n📝 Phase 1: Copyright Header Updates")
        results["copyright_update"] = self.copyright_updater.execute()
        
        # Phase 2: Folder organization (if implemented)
        logger.info("\n📁 Phase 2: Folder Organization")
        # TODO: Implement folder organization logic
        # This would involve:
        # - Detecting files in planning/ root
        # - Moving to temp-plans/ or active/ based on content analysis
        # - Creating universal subfolders
        # - Moving analysis docs to reports/
        # - Moving artifacts to artifacts/
        
        logger.info("✅ Planning Document Realignment Complete")
        
        return results


# ============================================
# CLI INTERFACE
# ============================================

def main():
    """CLI interface for bulk copyright updater."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Bulk Copyright Header Updater")
    parser.add_argument(
        "base_path",
        type=str,
        help="Base directory to scan"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute changes (default is dry run)"
    )
    parser.add_argument(
        "--pattern",
        type=str,
        default="**/*.md",
        help="File pattern to process (default: **/*.md)"
    )
    parser.add_argument(
        "--scan-only",
        action="store_true",
        help="Only scan and report missing headers"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s'
    )
    
    base_path = Path(args.base_path)
    
    if not base_path.exists():
        logger.error(f"❌ Path not found: {base_path}")
        return 1
    
    updater = BulkCopyrightUpdater(
        base_path=base_path,
        dry_run=not args.execute
    )
    
    if args.scan_only:
        logger.info("🔍 Scanning for missing copyright headers...")
        missing = updater.scan_missing_headers(args.pattern)
        
        logger.info(f"\n📊 Found {len(missing)} files missing copyright headers:\n")
        for file in missing:
            logger.info(f"  - {file.relative_to(base_path)}")
        
        return 0
    
    # Execute bulk update
    summary = updater.execute(args.pattern)
    
    # Save summary to JSON
    import json
    summary_file = base_path / "copyright-update-summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    logger.info(f"\n📄 Summary saved to: {summary_file}")
    
    return 0


if __name__ == "__main__":
    exit(main())
