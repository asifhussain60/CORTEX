#!/usr/bin/env python3
"""
CORTEX Regeneration Tracker

Intelligent change detection system for document/image/diagram regeneration.
Only regenerates files when source content or dependencies actually change.

Features:
- SHA256 content hashing for accurate change detection
- Dependency tracking (templates, configs affect outputs)
- Manifest persistence (survives git operations)
- Statistics tracking (time saved, files skipped)
- Force regeneration override

Usage:
    tracker = RegenerationTracker()
    
    # Check if file needs regeneration
    if tracker.should_regenerate("output.md", ["source.yaml", "template.j2"]):
        regenerate_file()
        tracker.mark_regenerated("output.md", ["source.yaml", "template.j2"])
    
    # Force regeneration
    tracker.force_regenerate_all()

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
Version: 1.0.0
"""

import hashlib
import yaml
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import time


class RegenerationTracker:
    """Tracks content changes to enable intelligent incremental regeneration."""
    
    def __init__(self, cortex_root: Optional[Path] = None):
        """
        Initialize regeneration tracker.
        
        Args:
            cortex_root: Path to CORTEX root directory. Auto-detects if None.
        """
        if cortex_root is None:
            # Auto-detect CORTEX root (go up from this file)
            cortex_root = Path(__file__).parent.parent.parent.parent
        
        self.cortex_root = Path(cortex_root)
        self.manifest_path = self.cortex_root / "cortex-brain" / "metadata" / "regeneration-manifest.yaml"
        self.manifest = self._load_manifest()
        self._start_time = time.time()
        self._files_processed = 0
        self._files_skipped = 0
    
    def _load_manifest(self) -> Dict:
        """Load regeneration manifest from disk."""
        if not self.manifest_path.exists():
            return self._get_empty_manifest()
        
        try:
            with open(self.manifest_path, 'r', encoding='utf-8') as f:
                manifest = yaml.safe_load(f)
                if not manifest:
                    return self._get_empty_manifest()
                return manifest
        except Exception as e:
            print(f"⚠️  Warning: Could not load manifest: {e}")
            return self._get_empty_manifest()
    
    def _get_empty_manifest(self) -> Dict:
        """Get empty manifest structure."""
        return {
            'version': '1.0.0',
            'last_updated': None,
            'documents': {},
            'images': {},
            'diagrams': {},
            'global_dependencies': [
                'cortex-brain/response-templates.yaml',
                'cortex-brain/brain-protection-rules.yaml',
                'cortex-operations.yaml',
                'cortex.config.json'
            ],
            'statistics': {
                'total_regenerations': 0,
                'last_full_regeneration': None,
                'last_incremental_regeneration': None,
                'files_skipped_last_run': 0,
                'time_saved_seconds': 0.0
            }
        }
    
    def _save_manifest(self):
        """Save manifest to disk."""
        self.manifest['last_updated'] = datetime.now().isoformat()
        
        # Ensure directory exists
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(self.manifest_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.manifest, f, default_flow_style=False, sort_keys=False)
        except Exception as e:
            print(f"⚠️  Warning: Could not save manifest: {e}")
    
    def compute_file_hash(self, file_path: Path) -> str:
        """
        Compute SHA256 hash of file content.
        
        Args:
            file_path: Path to file (relative to CORTEX root or absolute)
        
        Returns:
            SHA256 hash as hex string
        """
        # Convert to absolute path
        if not file_path.is_absolute():
            file_path = self.cortex_root / file_path
        
        if not file_path.exists():
            return ""
        
        try:
            sha256 = hashlib.sha256()
            with open(file_path, 'rb') as f:
                # Read in chunks for memory efficiency
                for chunk in iter(lambda: f.read(8192), b''):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except Exception as e:
            print(f"⚠️  Warning: Could not hash {file_path}: {e}")
            return ""
    
    def compute_combined_hash(self, file_paths: List[Path]) -> str:
        """
        Compute combined hash of multiple files (for dependencies).
        
        Args:
            file_paths: List of file paths
        
        Returns:
            SHA256 hash of concatenated file hashes
        """
        combined = ""
        for file_path in file_paths:
            combined += self.compute_file_hash(file_path)
        
        if not combined:
            return ""
        
        return hashlib.sha256(combined.encode()).hexdigest()
    
    def _check_global_dependencies_changed(self) -> bool:
        """Check if any global dependencies have changed."""
        global_deps = self.manifest.get('global_dependencies', [])
        
        for dep in global_deps:
            dep_path = self.cortex_root / dep
            if not dep_path.exists():
                continue
            
            current_hash = self.compute_file_hash(dep_path)
            
            # Check if any tracked file depends on this and hash changed
            for category in ['documents', 'images', 'diagrams']:
                for output_file, data in self.manifest.get(category, {}).items():
                    deps = data.get('dependencies', [])
                    if dep in deps:
                        # Global dependency affects this file, check if it changed
                        for tracked_dep in deps:
                            if tracked_dep == dep:
                                tracked_path = self.cortex_root / tracked_dep
                                if tracked_path.exists():
                                    old_hash = data.get('source_hash', '')
                                    # If hash computation included this dep and it changed
                                    # we'd need to regenerate
                                    # For now, be conservative and mark changed
                                    return True
        
        return False
    
    def should_regenerate(
        self, 
        output_file: str, 
        source_dependencies: List[str],
        category: str = 'documents'
    ) -> Tuple[bool, str]:
        """
        Check if output file needs regeneration.
        
        Args:
            output_file: Path to output file (relative to CORTEX root)
            source_dependencies: List of source files that generate this output
            category: Type of file ('documents', 'images', 'diagrams')
        
        Returns:
            Tuple of (should_regenerate: bool, reason: str)
        """
        output_path = self.cortex_root / output_file
        
        # If output doesn't exist, must regenerate
        if not output_path.exists():
            return (True, "Output file does not exist")
        
        # Get tracked data
        category_data = self.manifest.get(category, {})
        if category_data is None:
            category_data = {}
        tracked_data = category_data.get(output_file)
        
        # If never tracked, must regenerate
        if not tracked_data:
            return (True, "File not in manifest (first run)")
        
        # Compute current source hash
        source_paths = [self.cortex_root / dep for dep in source_dependencies]
        current_source_hash = self.compute_combined_hash(source_paths)
        
        # Compare with tracked hash
        tracked_source_hash = tracked_data.get('source_hash', '')
        
        if current_source_hash != tracked_source_hash:
            return (True, f"Source dependencies changed")
        
        # Verify output file still matches
        current_output_hash = self.compute_file_hash(output_path)
        tracked_output_hash = tracked_data.get('generated_hash', '')
        
        if current_output_hash != tracked_output_hash:
            return (True, "Output file was manually modified")
        
        # Everything matches - skip regeneration
        self._files_skipped += 1
        return (False, "No changes detected")
    
    def mark_regenerated(
        self,
        output_file: str,
        source_dependencies: List[str],
        category: str = 'documents',
        additional_metadata: Optional[Dict] = None
    ):
        """
        Mark file as regenerated and update manifest.
        
        Args:
            output_file: Path to output file (relative to CORTEX root)
            source_dependencies: List of source files used to generate output
            category: Type of file ('documents', 'images', 'diagrams')
            additional_metadata: Optional extra data to store (e.g., generation params)
        """
        output_path = self.cortex_root / output_file
        
        if not output_path.exists():
            print(f"⚠️  Warning: Cannot mark non-existent file: {output_file}")
            return
        
        # Compute hashes
        source_paths = [self.cortex_root / dep for dep in source_dependencies]
        source_hash = self.compute_combined_hash(source_paths)
        output_hash = self.compute_file_hash(output_path)
        
        # Ensure category exists and is not None
        if category not in self.manifest or self.manifest[category] is None:
            self.manifest[category] = {}
        
        # Store tracking data
        tracking_data = {
            'source_hash': source_hash,
            'generated_hash': output_hash,
            'last_regenerated': datetime.now().isoformat(),
            'dependencies': source_dependencies
        }
        
        # Add any additional metadata
        if additional_metadata:
            tracking_data.update(additional_metadata)
        
        self.manifest[category][output_file] = tracking_data
        
        # Update statistics
        if self.manifest.get('statistics') is None:
            self.manifest['statistics'] = {
                'total_regenerations': 0,
                'last_full_regeneration': None,
                'last_incremental_regeneration': None,
                'files_skipped_last_run': 0,
                'time_saved_seconds': 0.0
            }
        
        self.manifest['statistics']['total_regenerations'] += 1
        self.manifest['statistics']['last_incremental_regeneration'] = datetime.now().isoformat()
        
        self._files_processed += 1
    
    def mark_full_regeneration(self):
        """Mark that a full regeneration occurred."""
        self.manifest['statistics']['last_full_regeneration'] = datetime.now().isoformat()
        self._save_manifest()
    
    def finalize(self) -> Dict:
        """
        Finalize tracking session and save manifest.
        
        Returns:
            Summary statistics
        """
        elapsed_time = time.time() - self._start_time
        
        # Update statistics
        self.manifest['statistics']['files_skipped_last_run'] = self._files_skipped
        
        # Estimate time saved (assume 2 seconds per skipped file)
        time_saved = self._files_skipped * 2.0
        self.manifest['statistics']['time_saved_seconds'] = (
            self.manifest['statistics'].get('time_saved_seconds', 0.0) + time_saved
        )
        
        self._save_manifest()
        
        return {
            'files_processed': self._files_processed,
            'files_skipped': self._files_skipped,
            'elapsed_time': elapsed_time,
            'time_saved': time_saved
        }
    
    def get_statistics(self) -> Dict:
        """Get regeneration statistics."""
        return self.manifest.get('statistics', {})
    
    def clear_manifest(self):
        """Clear all tracking data (for force regeneration)."""
        self.manifest = self._get_empty_manifest()
        self._save_manifest()
    
    def get_tracked_files(self, category: Optional[str] = None) -> List[str]:
        """
        Get list of tracked files.
        
        Args:
            category: Optional category filter ('documents', 'images', 'diagrams')
        
        Returns:
            List of tracked file paths
        """
        if category:
            return list(self.manifest.get(category, {}).keys())
        
        all_files = []
        for cat in ['documents', 'images', 'diagrams']:
            all_files.extend(self.manifest.get(cat, {}).keys())
        return all_files
    
    def print_summary(self):
        """Print tracking summary."""
        stats = self.get_statistics()
        
        print("\n📊 Regeneration Tracker Summary")
        print("=" * 60)
        print(f"  Total regenerations: {stats.get('total_regenerations', 0)}")
        print(f"  Files skipped (last run): {stats.get('files_skipped_last_run', 0)}")
        print(f"  Time saved (cumulative): {stats.get('time_saved_seconds', 0.0):.1f}s")
        
        if stats.get('last_full_regeneration'):
            print(f"  Last full regeneration: {stats['last_full_regeneration']}")
        if stats.get('last_incremental_regeneration'):
            print(f"  Last incremental: {stats['last_incremental_regeneration']}")
        
        print("\n  Tracked files by category:")
        for category in ['documents', 'images', 'diagrams']:
            category_data = self.manifest.get(category, {})
            if category_data is None:
                category_data = {}
            count = len(category_data)
            if count > 0:
                print(f"    {category.capitalize()}: {count} files")


if __name__ == "__main__":
    # Demo usage
    tracker = RegenerationTracker()
    tracker.print_summary()
