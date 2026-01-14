#!/usr/bin/env python3
"""
File Consolidation Tool
Recursively scans a folder and consolidates contents into structured JSON/YAML formats.
Can be executed standalone or via CLI with parameters.

Usage:
    python consolidate.py --folder <path> --format json --output-in-source
    python consolidate.py --folder <path> --format yaml
"""

import os
import json
import yaml
import base64
import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional

class FileConsolidator:
    def __init__(self, folder_path: str, output_format: str = "json", 
                 exclude_patterns: List[str] = None, include_patterns: List[str] = None,
                 preserve_tree: bool = True, output_in_source: bool = False):
        """Initialize the consolidator with parameters."""
        self.folder_path = Path(folder_path)
        self.output_format = output_format
        self.exclude_patterns = exclude_patterns or [
            "**/.git/**", "**/__pycache__/**", "**/*.pyc", 
            "**/node_modules/**", "**/.venv/**", "**/*.log"
        ]
        self.include_patterns = include_patterns
        self.preserve_tree = preserve_tree
        self.output_in_source = output_in_source
        self.errors = []
        self.files_data = []
        self.tree_structure = {}
        
    def validate_phase(self) -> bool:
        """Validation Phase: Verify folder exists and is accessible."""
        print("=" * 60)
        print("VALIDATION PHASE")
        print("=" * 60)
        
        if not self.folder_path.exists():
            print(f"❌ Error: Folder does not exist: {self.folder_path}")
            return False
        
        if not self.folder_path.is_dir():
            print(f"❌ Error: Path is not a directory: {self.folder_path}")
            return False
        
        print(f"✓ Folder exists: {self.folder_path}")
        print(f"✓ Output format: {self.output_format}")
        print(f"✓ Preserve tree: {self.preserve_tree}")
        print(f"✓ Exclude patterns: {len(self.exclude_patterns)} patterns")
        
        # Check write permissions
        try:
            output_dir = self.folder_path.parent
            test_file = output_dir / ".test_write"
            test_file.touch()
            test_file.unlink()
            print(f"✓ Write permissions verified")
            return True
        except Exception as e:
            print(f"❌ Error: No write permissions - {e}")
            return False
    
    def should_include_file(self, file_path: Path) -> bool:
        """Check if file should be included based on patterns."""
        relative_path = str(file_path.relative_to(self.folder_path))
        
        # Check exclude patterns
        for pattern in self.exclude_patterns:
            if file_path.match(pattern):
                return False
        
        # Check include patterns if specified
        if self.include_patterns:
            for pattern in self.include_patterns:
                if file_path.match(pattern):
                    return True
            return False
        
        return True
    
    def discovery_phase(self) -> int:
        """Discovery Phase: Walk directory tree and collect file metadata."""
        print("\n" + "=" * 60)
        print("DISCOVERY PHASE")
        print("=" * 60)
        
        file_count = 0
        discovered_files = []
        
        try:
            for file_path in self.folder_path.rglob("*"):
                if file_path.is_file() and self.should_include_file(file_path):
                    discovered_files.append(file_path)
                    file_count += 1
            
            print(f"✓ Discovered {file_count} files")
            
            # Group by extension
            by_extension = {}
            for f in discovered_files:
                ext = f.suffix or "no_extension"
                by_extension[ext] = by_extension.get(ext, 0) + 1
            
            print(f"✓ File type summary:")
            for ext, count in sorted(by_extension.items()):
                print(f"  {ext}: {count} file(s)")
            
            return file_count
        except Exception as e:
            print(f"❌ Error during discovery: {e}")
            self.errors.append({
                "phase": "discovery",
                "error_type": "discovery_error",
                "message": str(e)
            })
            return 0
    
    def read_phase(self) -> None:
        """Read Phase: Read all files with proper encoding handling."""
        print("\n" + "=" * 60)
        print("READ PHASE")
        print("=" * 60)
        
        total_files = 0
        successful_reads = 0
        failed_reads = 0
        total_size = 0
        
        for file_path in sorted(self.folder_path.rglob("*")):
            if not file_path.is_file() or not self.should_include_file(file_path):
                continue
            
            total_files += 1
            relative_path = file_path.relative_to(self.folder_path)
            
            try:
                # Get file metadata
                stat_info = file_path.stat()
                size_bytes = stat_info.st_size
                modified_time = datetime.fromisoformat(
                    datetime.fromtimestamp(stat_info.st_mtime).isoformat()
                ).isoformat()
                
                # Try to read as text
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    is_binary = False
                    encoding = "utf8"
                    successful_reads += 1
                except (UnicodeDecodeError, ValueError):
                    # Fall back to base64 encoding
                    with open(file_path, 'rb') as f:
                        content = base64.b64encode(f.read()).decode('ascii')
                    is_binary = True
                    encoding = "base64"
                    successful_reads += 1
                
                total_size += size_bytes
                
                file_entry = {
                    "path": str(relative_path),
                    "extension": file_path.suffix,
                    "size_bytes": size_bytes,
                    "modified_time": modified_time,
                    "is_binary": is_binary,
                    "content": content,
                    "encoding": encoding
                }
                
                self.files_data.append(file_entry)
                
            except Exception as e:
                failed_reads += 1
                self.errors.append({
                    "file": str(relative_path),
                    "error_type": "read_error",
                    "message": str(e)
                })
                print(f"  ⚠ Failed to read: {relative_path} - {e}")
        
        print(f"✓ Read Phase Complete:")
        print(f"  Total files: {total_files}")
        print(f"  Successful: {successful_reads}")
        print(f"  Failed: {failed_reads}")
        print(f"  Total size: {total_size} bytes")
    
    def consolidation_phase(self) -> None:
        """Consolidation Phase: Structure data with metadata."""
        print("\n" + "=" * 60)
        print("CONSOLIDATION PHASE")
        print("=" * 60)
        
        # Build file type summary
        file_type_summary = {}
        for file_entry in self.files_data:
            ext = file_entry["extension"] or "no_extension"
            file_type_summary[ext] = file_type_summary.get(ext, 0) + 1
        
        # Build tree structure if requested
        if self.preserve_tree:
            self._build_tree_structure()
        
        print(f"✓ Consolidated {len(self.files_data)} files")
        print(f"✓ File type summary prepared")
        print(f"✓ Tree structure {'built' if self.preserve_tree else 'skipped'}")
    
    def _build_tree_structure(self) -> None:
        """Build directory tree structure."""
        tree = {}
        
        for file_entry in self.files_data:
            parts = Path(file_entry["path"]).parts
            current = tree
            
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            # Add file entry
            if parts:
                current[parts[-1]] = {
                    "type": "file",
                    "size": file_entry["size_bytes"],
                    "encoding": file_entry["encoding"]
                }
        
        self.tree_structure = tree
    
    def output_phase(self) -> str:
        """Output Phase: Serialize to specified format."""
        print("\n" + "=" * 60)
        print("OUTPUT PHASE")
        print("=" * 60)
        
        # Prepare metadata
        file_type_summary = {}
        total_size = 0
        for file_entry in self.files_data:
            ext = file_entry["extension"] or "no_extension"
            file_type_summary[ext] = file_type_summary.get(ext, 0) + 1
            total_size += file_entry["size_bytes"]
        
        metadata = {
            "consolidation_timestamp": datetime.now().isoformat(),
            "source_folder": str(self.folder_path),
            "total_files": len(self.files_data),
            "total_size_bytes": total_size,
            "file_type_summary": file_type_summary,
            "errors": self.errors
        }
        
        # Build output object
        output = {
            "metadata": metadata,
            "files": self.files_data
        }
        
        if self.preserve_tree:
            output["tree"] = {
                "directory_structure": self.tree_structure
            }
        
        # Determine output location
        if self.output_in_source:
            output_dir = self.folder_path
        else:
            output_dir = self.folder_path.parent
        
        output_filename = output_dir / f"{self.folder_path.name}_consolidated.{self.output_format}"
        
        try:
            if self.output_format == "json":
                with open(output_filename, 'w', encoding='utf-8') as f:
                    json.dump(output, f, indent=2, ensure_ascii=False)
            elif self.output_format == "yaml":
                with open(output_filename, 'w', encoding='utf-8') as f:
                    yaml.dump(output, f, default_flow_style=False, allow_unicode=True)
            else:
                raise ValueError(f"Unsupported format: {self.output_format}")
            
            print(f"✓ Output written to: {output_filename}")
            print(f"✓ Output size: {output_filename.stat().st_size} bytes")
            
            # Create cross-reference if both formats requested (future enhancement)
            self._maybe_create_cross_reference(output_filename)
            
            return str(output_filename)
        except Exception as e:
            print(f"❌ Error writing output: {e}")
            self.errors.append({
                "phase": "output",
                "error_type": "write_error",
                "message": str(e)
            })
            return ""
    
    def _maybe_create_cross_reference(self, output_file: Path) -> None:
        """Create cross-reference document if needed (placeholder for future)."""
        # Future: If both JSON and YAML exist, create a reference document
        pass
    
    def run(self) -> Tuple[bool, str]:
        """Execute the full consolidation workflow."""
        print("\n" + "🚀 STARTING FILE CONSOLIDATION".center(60))
        
        # Validation Phase
        if not self.validate_phase():
            return False, ""
        
        # Discovery Phase
        if self.discovery_phase() == 0:
            print("⚠ No files to consolidate")
            return False, ""
        
        # Read Phase
        self.read_phase()
        
        # Consolidation Phase
        self.consolidation_phase()
        
        # Output Phase
        output_file = self.output_phase()
        
        print("\n" + "✅ CONSOLIDATION COMPLETE".center(60))
        print("=" * 60)
        
        if self.errors:
            print(f"⚠ {len(self.errors)} error(s) encountered:")
            for error in self.errors[:5]:
                print(f"  - {error}")
            if len(self.errors) > 5:
                print(f"  ... and {len(self.errors) - 5} more")
        
        return bool(output_file), output_file


def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        description="Consolidate folder contents into structured JSON/YAML format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Consolidate to default output location (parent folder)
  python consolidate.py --folder D:\\path\\to\\folder --format json
  
  # Consolidate with output in source folder
  python consolidate.py --folder D:\\path\\to\\folder --format yaml --output-in-source
  
  # Exclude patterns
  python consolidate.py --folder . --exclude "*.log,*.pyc,__pycache__/**"
        """
    )
    
    parser.add_argument(
        "--folder", "-f",
        required=True,
        type=str,
        help="Root directory to scan and consolidate (required)"
    )
    
    parser.add_argument(
        "--format",
        choices=["json", "yaml"],
        default="json",
        help="Output format: json or yaml (default: json)"
    )
    
    parser.add_argument(
        "--output-in-source",
        action="store_true",
        help="Write output files in the source folder instead of parent directory"
    )
    
    parser.add_argument(
        "--exclude",
        type=str,
        default=None,
        help="Comma-separated glob patterns to exclude (e.g., '*.log,__pycache__/**')"
    )
    
    parser.add_argument(
        "--include",
        type=str,
        default=None,
        help="Comma-separated glob patterns to include exclusively"
    )
    
    parser.add_argument(
        "--preserve-tree",
        action="store_true",
        default=True,
        help="Maintain directory structure in output (default: True)"
    )
    
    return parser


def main():
    """Main CLI entry point."""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # Parse exclude/include patterns
    exclude_patterns = None
    if args.exclude:
        exclude_patterns = [p.strip() for p in args.exclude.split(",")]
    
    include_patterns = None
    if args.include:
        include_patterns = [p.strip() for p in args.include.split(",")]
    
    # Create consolidator
    consolidator = FileConsolidator(
        folder_path=args.folder,
        output_format=args.format,
        exclude_patterns=exclude_patterns,
        include_patterns=include_patterns,
        preserve_tree=args.preserve_tree,
        output_in_source=args.output_in_source
    )
    
    success, output_file = consolidator.run()
    
    if success:
        print(f"\n✅ Consolidation successful!")
        print(f"Output file: {output_file}")
        return 0
    else:
        print(f"\n❌ Consolidation failed or incomplete")
        return 1


if __name__ == "__main__":
    sys.exit(main())
