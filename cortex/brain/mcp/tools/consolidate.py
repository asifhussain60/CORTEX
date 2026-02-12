#!/usr/bin/env python3
"""
Intelligent Folder Consolidation Tool - Refactored with SOLID Principles

Architecture:
- Single Responsibility: Each class has one reason to change
- Open/Closed: Open for extension, closed for modification
- Liskov Substitution: Content extractors are interchangeable
- Interface Segregation: Small, focused interfaces
- Dependency Inversion: Depend on abstractions, not implementations

Key improvements:
- File filtering separates source files from consolidation files
- Content extraction is strategy-based
- Cleanup is explicit and safe
- File handling is isolated and testable
"""

import argparse
import base64
import json
import os
import sys
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Set

import yaml

# ============================================================================
# ABSTRACTION: Content Extraction Strategy Pattern
# ============================================================================

class ContentExtractor(ABC):
    """Abstract base for content extraction strategies."""

    @abstractmethod
    def can_extract(self, filename: str) -> bool:
        """Check if this extractor handles this file type."""
        pass

    @abstractmethod
    def extract(self, content: str, filename: str) -> Dict[str, Any]:
        """Extract intelligence from content."""
        pass


class MarkdownExtractor(ContentExtractor):
    """Extracts structure from markdown files."""

    def can_extract(self, filename: str) -> bool:
        return Path(filename).suffix.lower() in ['.md', '.markdown']

    def extract(self, content: str, filename: str) -> Dict[str, Any]:
        intelligence = {
            "structure": "markdown",
            "key_sections": [],
            "key_terms": []
        }
        lines = content.split('\n')
        for line in lines:
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                text = line.lstrip('# ').strip()
                intelligence["key_sections"].append({"level": level, "text": text})
        intelligence["key_sections"] = intelligence["key_sections"][:20]
        return intelligence


class CodeExtractor(ContentExtractor):
    """Extracts structure from code files."""

    CODE_EXTENSIONS = {'.py', '.js', '.ts', '.java', '.cpp', '.cs', '.go', '.rb', '.php'}

    def can_extract(self, filename: str) -> bool:
        return Path(filename).suffix.lower() in self.CODE_EXTENSIONS

    def extract(self, content: str, filename: str) -> Dict[str, Any]:
        ext = Path(filename).suffix.lower()
        return {
            "structure": "code",
            "language": ext.lstrip('.'),
            "has_classes": "class " in content,
            "has_functions": "def " in content or "function " in content,
            "has_imports": "import " in content or "require " in content
        }


class JSONYAMLExtractor(ContentExtractor):
    """Extracts structure from JSON and YAML files."""

    def can_extract(self, filename: str) -> bool:
        ext = Path(filename).suffix.lower()
        return ext in {'.json', '.yaml', '.yml'}

    def extract(self, content: str, filename: str) -> Dict[str, Any]:
        ext = Path(filename).suffix.lower()
        is_json = ext == '.json'
        parser = json.loads if is_json else yaml.safe_load

        try:
            data = parser(content)
            keys = list(data.keys())[:15] if isinstance(data, dict) else []
            return {
                "structure": "json" if is_json else "yaml",
                "format": "json" if is_json else "yaml",
                "keys": keys,
                "valid": True
            }
        except Exception:
            return {"structure": "json" if is_json else "yaml", "valid": False}


class DefaultExtractor(ContentExtractor):
    """Default extractor for any other file type."""

    def can_extract(self, filename: str) -> bool:
        return True  # Matches anything

    def extract(self, content: str, filename: str) -> Dict[str, Any]:
        words = content.split()[:100]
        key_terms = {word.strip('"') for word in words
                    if (word.startswith('"') and word.endswith('"')) or
                       (len(word) > 3 and word.isupper())}
        return {
            "structure": "text",
            "key_terms": sorted(list(key_terms))[:20]
        }


class IntelligenceExtractor:
    """Coordinator for content extraction strategies (Strategy Pattern)."""

    def __init__(self):
        self.extractors: List[ContentExtractor] = [
            MarkdownExtractor(),
            CodeExtractor(),
            JSONYAMLExtractor(),
            DefaultExtractor()
        ]

    def extract(self, content: str, filename: str) -> Dict[str, Any]:
        """Find appropriate extractor and extract intelligence."""
        for extractor in self.extractors:
            if extractor.can_extract(filename):
                return extractor.extract(content, filename)
        return {}


# ============================================================================
# FILE HANDLING: File Discovery and Filtering
# ============================================================================

class FileFilter:
    """Determines which files should be consolidated vs preserved."""

    CONSOLIDATION_EXTENSIONS = {'.yaml', '.json'}
    HIDDEN_PREFIX = '.'

    @classmethod
    def is_consolidation_file(cls, path: Path) -> bool:
        """Check if file is a consolidation output file."""
        return path.suffix in cls.CONSOLIDATION_EXTENSIONS

    @classmethod
    def is_source_file(cls, path: Path) -> bool:
        """Check if file should be consolidated (not a consolidation file)."""
        return not cls.is_consolidation_file(path)

    @classmethod
    def is_hidden(cls, path: Path) -> bool:
        """Check if file should be ignored."""
        return path.name.startswith(cls.HIDDEN_PREFIX)


class FileDiscovery:
    """Discovers files in a folder (Single Responsibility)."""

    def __init__(self, folder_path: Path):
        self.folder_path = folder_path
        self.filter = FileFilter()

    def get_source_files(self) -> List[Path]:
        """Get all source files (not consolidation files, not hidden)."""
        files = []
        for item in sorted(self.folder_path.iterdir()):
            if item.is_file() and not self.filter.is_hidden(item) and self.filter.is_source_file(item):
                files.append(item)
        return files

    def get_all_files(self) -> List[Path]:
        """Get all files including consolidation files."""
        files = []
        for item in sorted(self.folder_path.iterdir()):
            if item.is_file() and not self.filter.is_hidden(item):
                files.append(item)
        return files


# ============================================================================
# FILE READING: Content Loading with Error Handling
# ============================================================================

class FileContentLoader:
    """Loads file content with graceful fallback (Single Responsibility)."""

    @staticmethod
    def load(file_path: Path) -> tuple[str, bool]:
        """Load file content. Returns (content, is_binary)."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read(), False
        except Exception:
            try:
                with open(file_path, 'rb') as f:
                    return base64.b64encode(f.read()).decode('ascii'), True
            except Exception:
                return "", True


class FileMetadataExtractor:
    """Extracts file metadata (Single Responsibility)."""

    @staticmethod
    def extract(file_path: Path) -> Dict[str, Any]:
        """Extract file metadata."""
        try:
            stat_info = file_path.stat()
            return {
                "filename": file_path.name,
                "size_bytes": stat_info.st_size,
                "modified_time": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                "extension": file_path.suffix
            }
        except Exception as e:
            return {"filename": file_path.name, "error": str(e)}


# ============================================================================
# CONSOLIDATION: File Processing
# ============================================================================

class FileProcessor:
    """Processes individual files for consolidation."""

    def __init__(self):
        self.intelligence_extractor = IntelligenceExtractor()
        self.content_loader = FileContentLoader()
        self.metadata_extractor = FileMetadataExtractor()

    def process(self, file_path: Path) -> tuple[Optional[Dict[str, Any]], Optional[Exception]]:
        """Process a single file. Returns (file_entry, error)."""
        try:
            # Load metadata
            metadata = self.metadata_extractor.extract(file_path)
            if "error" in metadata:
                return None, Exception(f"Metadata error: {metadata['error']}")

            # Load content
            content, is_binary = self.content_loader.load(file_path)

            # Extract intelligence
            intelligence = self.intelligence_extractor.extract(content, file_path.name)

            file_entry = {
                **metadata,
                "is_binary": is_binary,
                "content": content,
                "intelligence": intelligence
            }

            return file_entry, None

        except Exception as e:
            return None, e


class FolderConsolidator:
    """Consolidates a single folder into a machine-readable file."""

    def __init__(self, folder_path: Path, output_format: str = "yaml"):
        self.folder_path = folder_path
        self.output_format = output_format

        # Dependencies (Dependency Injection)
        self.discovery = FileDiscovery(folder_path)
        self.processor = FileProcessor()

        # State
        self.files_data: List[Dict[str, Any]] = []
        self.errors: List[Dict[str, str]] = []
        self.consolidation_file: Optional[Path] = None

    def consolidate(self) -> bool:
        """Consolidate folder files. Returns success status."""
        # Phase 1: Discover source files
        source_files = self.discovery.get_source_files()
        if not source_files:
            self.errors.append({"phase": "discovery", "error": "No source files found"})
            return False

        print(f"✓ Found {len(source_files)} file(s)")

        # Phase 2: Process files
        for file_path in source_files:
            file_entry, error = self.processor.process(file_path)
            if error:
                self.errors.append({"file": file_path.name, "error": str(error)})
                print(f"  ⚠ Error: {file_path.name}: {error}")
            else:
                self.files_data.append(file_entry)
                size_kb = file_entry["size_bytes"] / 1024
                print(f"  ✓ {file_path.name} ({size_kb:.1f} KB)")

        if not self.files_data:
            self.errors.append({"phase": "processing", "error": "No files successfully processed"})
            return False

        # Phase 3: Write consolidation
        if not self._write_consolidation():
            return False

        return True

    def _write_consolidation(self) -> bool:
        """Write consolidation file. Returns success status."""
        try:
            metadata = {
                "consolidation_timestamp": datetime.now().isoformat(),
                "source_folder": str(self.folder_path),
                "folder_name": self.folder_path.name,
                "total_files": len(self.files_data),
                "total_size_bytes": sum(f["size_bytes"] for f in self.files_data),
                "file_type_summary": self._build_file_type_summary(),
                "errors": self.errors
            }

            output = {"metadata": metadata, "files": self.files_data}

            self.consolidation_file = self.folder_path / f"{self.folder_path.name}.{self.output_format}"

            if self.output_format == "yaml":
                with open(self.consolidation_file, 'w', encoding='utf-8') as f:
                    yaml.dump(output, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            else:
                with open(self.consolidation_file, 'w', encoding='utf-8') as f:
                    json.dump(output, f, indent=2, ensure_ascii=False)

            size_kb = self.consolidation_file.stat().st_size / 1024
            print(f"✓ Consolidation: {self.consolidation_file.name} ({size_kb:.1f} KB)")
            return True

        except Exception as e:
            self.errors.append({"phase": "write", "error": str(e)})
            print(f"❌ Error writing consolidation: {e}")
            return False

    def _build_file_type_summary(self) -> Dict[str, int]:
        """Build summary of file types."""
        summary: Dict[str, int] = {}
        for file_entry in self.files_data:
            ext = file_entry["extension"] or "no_extension"
            summary[ext] = summary.get(ext, 0) + 1
        return summary

    def get_source_files_to_delete(self) -> List[Path]:
        """Get source files that should be deleted during cleanup."""
        return self.discovery.get_source_files()

    def get_consolidation_file(self) -> Optional[Path]:
        """Get path to consolidation file (to protect from deletion)."""
        return self.consolidation_file


# ============================================================================
# CLEANUP: Safe Deletion with Manifest
# ============================================================================

class CleanupManager:
    """Manages safe cleanup of source files and folders."""

    def __init__(self, consolidators: List[FolderConsolidator]):
        self.consolidators = consolidators
        self.deletion_manifest: List[Dict[str, Any]] = []

    def cleanup(self) -> bool:
        """Delete source files and empty folders. Returns success status."""
        # Phase 1: Collect files to delete (excluding consolidation files)
        all_files_to_delete = set()
        consolidation_files = set()

        for consolidator in self.consolidators:
            cons_file = consolidator.get_consolidation_file()
            if cons_file:
                consolidation_files.add(cons_file)

            for file_path in consolidator.get_source_files_to_delete():
                all_files_to_delete.add(file_path)

        # Phase 2: Delete files (excluding consolidation files)
        deleted = 0
        failed = 0

        for file_path in sorted(all_files_to_delete):
            if file_path in consolidation_files:
                print(f"  ⊘ Skipping consolidation file: {file_path.name}")
                continue

            try:
                file_path.unlink()
                deleted += 1
                self.deletion_manifest.append({
                    "file": str(file_path),
                    "status": "deleted",
                    "time": datetime.now().isoformat()
                })
            except Exception as e:
                failed += 1
                self.deletion_manifest.append({
                    "file": str(file_path),
                    "status": "failed",
                    "error": str(e),
                    "time": datetime.now().isoformat()
                })
                print(f"  ⚠ Failed to delete {file_path.name}: {e}")

        if deleted > 0:
            print(f"🗑 Deleted {deleted} source file(s)")
        if failed > 0:
            print(f"⚠ Failed to delete {failed} file(s)")

        # Phase 3: Delete empty folders (bottom-up)
        return self._cleanup_empty_folders()

    def _cleanup_empty_folders(self) -> bool:
        """Delete empty folders recursively."""
        deleted = 0
        failed = 0

        # Collect all folders from all consolidators
        all_folders = set()
        for consolidator in self.consolidators:
            self._collect_folders(consolidator.folder_path, all_folders)

        # Delete from deepest to shallowest
        for folder_path in sorted(all_folders, key=lambda x: len(x.parts), reverse=True):
            try:
                if not any(folder_path.iterdir()):
                    folder_path.rmdir()
                    deleted += 1
            except Exception:
                failed += 1

        if deleted > 0:
            print(f"🗑 Deleted {deleted} empty folder(s)")
        if failed > 0:
            print(f"⚠ Failed to delete {failed} folder(s)")

        return True

    def _collect_folders(self, folder_path: Path, folders: Set[Path]) -> None:
        """Recursively collect all subfolders."""
        try:
            for item in folder_path.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    folders.add(item)
                    self._collect_folders(item, folders)
        except Exception:
            pass


# ============================================================================
# ORCHESTRATION: Main Coordinator
# ============================================================================

class ConsolidationOrchestrator:
    """Orchestrates the entire consolidation process."""

    def __init__(self, root_folder: Path, output_format: str, cleanup: bool = False):
        self.root_folder = root_folder
        self.output_format = output_format
        self.cleanup = cleanup
        self.consolidators: List[FolderConsolidator] = []

    def execute(self) -> bool:
        """Execute full consolidation workflow. Returns success status."""
        print(f"\n{'='*70}")
        print(f"RECURSIVE CONSOLIDATION: {self.root_folder}")
        print(f"{'='*70}")

        # Phase 1: Consolidate root and all subfolders
        if not self._consolidate_recursively(self.root_folder):
            return False

        # Phase 2: Cleanup if requested
        if self.cleanup:
            print(f"\n{'='*70}")
            print("CLEANUP PHASE")
            print(f"{'='*70}")
            cleanup_manager = CleanupManager(self.consolidators)
            if not cleanup_manager.cleanup():
                return False

        return True

    def _consolidate_recursively(self, folder_path: Path) -> bool:
        """Recursively consolidate folder and all subfolders."""
        # Consolidate this folder
        print(f"\n{'='*70}")
        print(f"Consolidating: {folder_path.name}")
        print(f"{'='*70}")

        consolidator = FolderConsolidator(folder_path, self.output_format)
        if not consolidator.consolidate():
            return False

        self.consolidators.append(consolidator)

        # Recursively consolidate subfolders
        try:
            for item in sorted(folder_path.iterdir()):
                if item.is_dir() and not item.name.startswith('.'):
                    if not self._consolidate_recursively(item):
                        return False
        except Exception as e:
            print(f"❌ Error recursing into subfolders: {e}")
            return False

        return True

    def print_summary(self) -> None:
        """Print consolidation summary."""
        print(f"\n{'='*70}")
        print("CONSOLIDATION SUMMARY")
        print(f"{'='*70}")

        successful = len(self.consolidators)
        total_files = sum(len(c.files_data) for c in self.consolidators)
        total_size = sum(sum(f["size_bytes"] for f in c.files_data) for c in self.consolidators)

        print(f"✓ Successfully consolidated {successful} folder(s)")
        print(f"✓ Total files: {total_files}")
        print(f"✓ Total size: {total_size / 1024 / 1024:.1f} MB")

        for consolidator in self.consolidators:
            rel_path = consolidator.folder_path.relative_to(self.root_folder) \
                if consolidator.folder_path != self.root_folder \
                else consolidator.folder_path.name
            print(f"  ✓ {rel_path}/")


# ============================================================================
# CLI: Command Line Interface
# ============================================================================

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Intelligently consolidate folders into machine-readable files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Consolidate preview (no cleanup)
  python consolidate.py --folder <target-folder> --format yaml

  # Full consolidation with cleanup
  python consolidate.py --folder <target-folder> --format yaml --cleanup
        """
    )

    parser.add_argument("--folder", "-f", required=True, help="Root directory to consolidate")
    parser.add_argument("--format", choices=["yaml", "json"], default="yaml", help="Output format")
    parser.add_argument("--cleanup", "-c", action="store_true", help="Delete source files after consolidation")

    args = parser.parse_args()

    folder_path = Path(args.folder).resolve()

    if not folder_path.exists():
        print(f"❌ Folder not found: {folder_path}")
        return 1

    if not folder_path.is_dir():
        print(f"❌ Not a directory: {folder_path}")
        return 1

    # Confirm cleanup if requested
    if args.cleanup:
        print("\n" + "⚠️  WARNING".center(70))
        print("All source files and empty folders will be DELETED".center(70))
        print("This operation is IRREVERSIBLE".center(70))
        print("Consolidation files (.yaml/.json) will be PRESERVED".center(70))
        print("=" * 70)
        response = input("\nContinue? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("Cancelled.")
            return 0
        print()

    # Execute consolidation
    orchestrator = ConsolidationOrchestrator(folder_path, args.format, args.cleanup)
    success = orchestrator.execute()
    orchestrator.print_summary()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
