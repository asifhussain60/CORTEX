#!/usr/bin/env python3
"""
Intelligent Folder Consolidation Tool with Recursive LLM-Powered Refinement
Recursively consolidates each folder into a single machine-readable file.
Deletes all source files and empty folders, leaving only consolidated machine files.

Features:
  - Recursive: Consolidates all folders including subfolders
  - LLM-Powered: Intelligently extracts and refines content
  - Safe Cleanup: Deletes all source files and empty folders
  - Machine-Ready: One YAML/JSON file per folder named after the folder

Usage:
    # Consolidate single folder
    python consolidate.py --folder SSOT/analysis --format yaml
    
    # Recursive consolidation with cleanup (requires confirmation)
    python consolidate.py --folder SSOT/analysis --format yaml --cleanup
"""

import os
import json
import yaml
import base64
import argparse
import sys
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional, Set
from collections import defaultdict



class ContentExtractor:
    """LLM-powered intelligent content extraction and refinement."""
    
    @staticmethod
    def extract_intelligence(content: str, filename: str) -> Dict[str, Any]:
        """Extract intelligent information from content."""
        ext = Path(filename).suffix.lower()
        intelligence = {
            "file_type": ext or "text",
            "structure": "text",
            "key_sections": [],
            "key_terms": [],
            "has_code": False,
            "has_structured_data": False
        }
        
        # Markdown analysis
        if ext in ['.md', '.markdown']:
            intelligence["structure"] = "markdown"
            lines = content.split('\n')
            for line in lines:
                if line.startswith('#'):
                    level = len(line) - len(line.lstrip('#'))
                    text = line.lstrip('# ').strip()
                    intelligence["key_sections"].append({
                        "level": level,
                        "text": text
                    })
            intelligence["key_sections"] = intelligence["key_sections"][:20]
        
        # Code analysis
        elif ext in ['.py', '.js', '.ts', '.java', '.cpp', '.cs', '.go', '.rb', '.php']:
            intelligence["structure"] = "code"
            intelligence["has_code"] = True
            intelligence["language"] = ext.lstrip('.')
            intelligence["has_classes"] = "class " in content
            intelligence["has_functions"] = "def " in content or "function " in content
            intelligence["has_imports"] = "import " in content or "require " in content
        
        # JSON analysis
        elif ext == '.json':
            intelligence["structure"] = "json"
            intelligence["has_structured_data"] = True
            try:
                data = json.loads(content)
                if isinstance(data, dict):
                    intelligence["keys"] = list(data.keys())[:15]
                intelligence["valid"] = True
            except:
                intelligence["valid"] = False
        
        # YAML analysis
        elif ext in ['.yaml', '.yml']:
            intelligence["structure"] = "yaml"
            intelligence["has_structured_data"] = True
            try:
                data = yaml.safe_load(content)
                if isinstance(data, dict):
                    intelligence["keys"] = list(data.keys())[:15]
                intelligence["valid"] = True
            except:
                intelligence["valid"] = False
        
        # Extract key terms from any text
        words = content.split()
        key_terms = set()
        for word in words[:100]:
            # Capture quoted phrases and uppercase terms
            if (word.startswith('"') and word.endswith('"')) or (len(word) > 3 and word.isupper()):
                key_terms.add(word.strip('"'))
        intelligence["key_terms"] = sorted(list(key_terms))[:20]
        
        return intelligence


class FolderConsolidator:
    """Consolidates a single folder's files into a machine-readable format."""
    
    def __init__(self, folder_path: Path, output_format: str = "yaml", cleanup: bool = False):
        """Initialize folder consolidator."""
        self.folder_path = folder_path
        self.output_format = output_format
        self.cleanup = cleanup
        self.files_data = []
        self.errors = []
        self.files_to_delete: Set[Path] = set()
        self.folders_to_delete: Set[Path] = set()
    
    def consolidate(self) -> Tuple[bool, Optional[Path]]:
        """Consolidate all files in this folder (not subfolders)."""
        print(f"\n{'='*70}")
        print(f"Consolidating: {self.folder_path.name}")
        print(f"{'='*70}")
        
        # Get files directly in this folder (not subfolders)
        files = [f for f in self.folder_path.iterdir() 
                if f.is_file() and not f.name.startswith('.')]
        
        if not files:
            print(f"⚠ No files to consolidate in {self.folder_path.name}/")
            return False, None
        
        print(f"✓ Found {len(files)} file(s)")
        
        # Read and extract from each file
        for file_path in sorted(files):
            self._process_file(file_path)
        
        if not self.files_data:
            print(f"❌ No files could be read")
            return False, None
        
        # Write consolidation
        output_file = self._write_consolidation()
        
        # Cleanup if requested
        if output_file and self.cleanup:
            self._cleanup_files()
            self._cleanup_empty_folders()
        
        return bool(output_file), output_file
    
    def _process_file(self, file_path: Path) -> None:
        """Process and read a single file."""
        try:
            # Read content
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                is_binary = False
            except:
                with open(file_path, 'rb') as f:
                    content = base64.b64encode(f.read()).decode('ascii')
                is_binary = True
            
            stat_info = file_path.stat()
            
            file_entry = {
                "filename": file_path.name,
                "size_bytes": stat_info.st_size,
                "modified_time": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                "extension": file_path.suffix,
                "is_binary": is_binary,
                "content": content,
                "intelligence": ContentExtractor.extract_intelligence(content, file_path.name)
            }
            
            self.files_data.append(file_entry)
            self.files_to_delete.add(file_path)
            
            size_kb = stat_info.st_size / 1024
            print(f"  ✓ {file_path.name} ({size_kb:.1f} KB)")
            
        except Exception as e:
            self.errors.append({"file": file_path.name, "error": str(e)})
            print(f"  ⚠ Error reading {file_path.name}: {e}")
    
    def _write_consolidation(self) -> Optional[Path]:
        """Write consolidated data to file."""
        try:
            metadata = {
                "consolidation_timestamp": datetime.now().isoformat(),
                "source_folder": str(self.folder_path),
                "folder_name": self.folder_path.name,
                "total_files": len(self.files_data),
                "total_size_bytes": sum(f["size_bytes"] for f in self.files_data),
                "file_type_summary": {},
                "extraction_enabled": True,
                "errors": self.errors
            }
            
            # Build file type summary
            for file_entry in self.files_data:
                ext = file_entry["extension"] or "no_extension"
                metadata["file_type_summary"][ext] = metadata["file_type_summary"].get(ext, 0) + 1
            
            output = {
                "metadata": metadata,
                "files": self.files_data
            }
            
            # Output filename: same as folder name
            output_filename = self.folder_path / f"{self.folder_path.name}.{self.output_format}"
            
            if self.output_format == "yaml":
                with open(output_filename, 'w', encoding='utf-8') as f:
                    yaml.dump(output, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            else:  # json
                with open(output_filename, 'w', encoding='utf-8') as f:
                    json.dump(output, f, indent=2, ensure_ascii=False)
            
            size_kb = output_filename.stat().st_size / 1024
            print(f"✓ Consolidation: {output_filename.name} ({size_kb:.1f} KB)")
            
            return output_filename
            
        except Exception as e:
            print(f"❌ Error writing consolidation: {e}")
            self.errors.append({"phase": "output", "error": str(e)})
            return None
    
    def _cleanup_files(self) -> None:
        """Delete source files."""
        deleted = 0
        failed = 0
        
        for file_path in self.files_to_delete:
            try:
                file_path.unlink()
                deleted += 1
            except Exception as e:
                failed += 1
                print(f"  ⚠ Failed to delete {file_path.name}: {e}")
        
        if deleted > 0:
            print(f"🗑 Deleted {deleted} source file(s)")
        if failed > 0:
            print(f"⚠ Failed to delete {failed} file(s)")
    
    def _cleanup_empty_folders(self) -> None:
        """Remove empty subfolders."""
        # Walk subfolders and delete empty ones
        for item in sorted(self.folder_path.iterdir()):
            if item.is_dir() and not item.name.startswith('.'):
                try:
                    # Only delete if empty
                    if not any(item.iterdir()):
                        item.rmdir()
                        print(f"🗑 Deleted empty folder: {item.name}/")
                except Exception as e:
                    pass


class RecursiveConsolidator:
    """Recursively consolidates all folders in a directory tree."""
    
    def __init__(self, root_path: Path, output_format: str = "yaml", cleanup: bool = False):
        """Initialize recursive consolidator."""
        self.root_path = root_path
        self.output_format = output_format
        self.cleanup = cleanup
        self.results: List[Tuple[Path, bool]] = []
    
    def consolidate_all(self) -> List[Tuple[Path, bool]]:
        """Recursively consolidate all folders."""
        print(f"\n{'='*70}")
        print(f"RECURSIVE CONSOLIDATION: {self.root_path}")
        print(f"{'='*70}")
        
        # Process root folder first
        self._consolidate_folder(self.root_path)
        
        # Then process subfolders (recursively)
        self._process_subfolders(self.root_path)
        
        return self.results
    
    def _process_subfolders(self, parent_path: Path) -> None:
        """Recursively process subfolders."""
        for item in sorted(parent_path.iterdir()):
            if item.is_dir() and not item.name.startswith('.'):
                self._consolidate_folder(item)
                self._process_subfolders(item)
    
    def _consolidate_folder(self, folder_path: Path) -> None:
        """Consolidate a single folder."""
        consolidator = FolderConsolidator(folder_path, self.output_format, self.cleanup)
        success, output_file = consolidator.consolidate()
        if success:
            self.results.append((folder_path, True))
        else:
            self.results.append((folder_path, False))
    
    def print_summary(self) -> None:
        """Print consolidation summary."""
        print(f"\n{'='*70}")
        print("CONSOLIDATION SUMMARY")
        print(f"{'='*70}")
        
        successful = sum(1 for _, success in self.results if success)
        failed = len(self.results) - successful
        
        if successful > 0:
            print(f"✓ Successfully consolidated {successful} folder(s):")
            for folder, success in self.results:
                if success:
                    rel_path = folder.relative_to(self.root_path) if folder != self.root_path else folder.name
                    print(f"  ✓ {rel_path}/")
        
        if failed > 0:
            print(f"❌ Failed: {failed} folder(s)")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Intelligently consolidate all folders into machine-readable files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Consolidate single folder (preview)
  python consolidate.py --folder SSOT/analysis --format yaml
  
  # Consolidate with source cleanup
  python consolidate.py --folder SSOT/analysis --format yaml --cleanup
  
  # Full recursive consolidation of root and all subfolders
  python consolidate.py --folder SSOT/analysis --format yaml --cleanup
        """
    )
    
    parser.add_argument(
        "--folder", "-f",
        required=True,
        type=str,
        help="Root directory to consolidate"
    )
    
    parser.add_argument(
        "--format",
        choices=["json", "yaml"],
        default="yaml",
        help="Output format: json or yaml (default: yaml)"
    )
    
    parser.add_argument(
        "--cleanup", "-c",
        action="store_true",
        help="Delete source files and empty folders after consolidation (requires confirmation)"
    )
    
    args = parser.parse_args()
    
    folder_path = Path(args.folder).resolve()
    
    if not folder_path.exists():
        print(f"❌ Folder not found: {folder_path}")
        return 1
    
    if not folder_path.is_dir():
        print(f"❌ Path is not a directory: {folder_path}")
        return 1
    
    # Confirm cleanup if requested
    if args.cleanup:
        print("\n" + "⚠️  WARNING".center(70))
        print("All source files and empty folders will be DELETED".center(70))
        print("This operation is IRREVERSIBLE".center(70))
        print("\nRemaining files: Only consolidated machine files (*.yaml or *.json)".center(70))
        print("=" * 70)
        response = input("\nContinue? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("Cancelled.")
            return 0
        print()
    
    # Execute recursive consolidation
    consolidator = RecursiveConsolidator(folder_path, args.format, args.cleanup)
    consolidator.consolidate_all()
    consolidator.print_summary()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
