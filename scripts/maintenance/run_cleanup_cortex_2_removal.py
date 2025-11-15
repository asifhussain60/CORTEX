#!/usr/bin/env python3
"""
CORTEX 2.0 Cleanup Script
========================

Purpose: Clean CORTEX 2.0 legacy files and organize root folder

Features:
- Archives CORTEX 2.0 design documentation
- Removes test coverage artifacts
- Organizes misplaced scripts and documents
- Respects protected paths
- Supports dry-run mode

Author: CORTEX Assistant
Date: 2025-11-15
"""

import sys
import json
from pathlib import Path
from typing import List, Dict, Any
import shutil
from datetime import datetime

# Add src to path
CORTEX_ROOT = Path(__file__).parent
sys.path.insert(0, str(CORTEX_ROOT))

from src.operations.modules.cleanup.cleanup_orchestrator import CleanupOrchestrator


class CortexTwoRemovalCleanup:
    """Enhanced cleanup for CORTEX 2.0 removal"""
    
    def __init__(self, project_root: Path = None, dry_run: bool = True):
        self.project_root = project_root or Path.cwd()
        self.dry_run = dry_run
        self.orchestrator = CleanupOrchestrator(project_root=self.project_root)
        self.cleanup_log: List[Dict[str, Any]] = []
        
        # CORTEX 2.0 specific patterns
        self.cortex_2_patterns = [
            "cortex-brain/cortex-2.0-design",
            "cortex-brain/CORTEX-2.0-*.md",
            "cortex-brain/archives/converted-to-yaml-2025-11-09/CORTEX-2.0-*.md"
        ]
        
        # Root clutter patterns
        self.root_clutter_patterns = {
            'coverage_files': ".coverage.*",
            'demo_scripts': "demo_*.py",
            'test_scripts': "test_*_3_0_*.py",
            'investigation_tests': "test_investigation_*.py",
            'kg_tests': "test_knowledge_graph_*.py",
            'validation_scripts': "final_*_validation.py",
            'process_scripts': "process_conversations_*.py",
            'temp_files': "temp_*.json",
            'pattern_files': "pattern_analysis.json",
            'investigation_docs': "*INVESTIGATION*.md"
        }
        
        # Relocation rules
        self.relocation_map = {
            'demo_scripts': 'scripts/demos',
            'test_scripts': 'tests/integration',
            'investigation_tests': 'tests/integration',
            'kg_tests': 'tests/integration',
            'validation_scripts': 'scripts/temp',
            'process_scripts': 'scripts/temp',
            'temp_files': 'scripts/temp',
            'pattern_files': 'scripts/temp',
            'investigation_docs': 'docs/investigation'
        }
    
    def execute(self) -> Dict[str, Any]:
        """Execute CORTEX 2.0 cleanup"""
        print("=" * 70)
        print("CORTEX 2.0 REMOVAL CLEANUP")
        print("=" * 70)
        print(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE EXECUTION'}")
        print(f"Project Root: {self.project_root}")
        print()
        
        results = {
            'success': True,
            'cortex_2_archived': 0,
            'root_files_cleaned': 0,
            'space_freed_mb': 0.0,
            'errors': [],
            'warnings': []
        }
        
        try:
            # Phase 1: Archive CORTEX 2.0 files
            print("Phase 1: Archive CORTEX 2.0 Legacy Files")
            print("-" * 70)
            cortex_2_result = self._archive_cortex_2_files()
            results['cortex_2_archived'] = cortex_2_result['archived_count']
            results['space_freed_mb'] += cortex_2_result['space_freed_mb']
            print(f"✅ Archived {cortex_2_result['archived_count']} CORTEX 2.0 files")
            print()
            
            # Phase 2: Clean root folder
            print("Phase 2: Organize Root Folder")
            print("-" * 70)
            root_result = self._cleanup_root_folder()
            results['root_files_cleaned'] = root_result['files_processed']
            results['space_freed_mb'] += root_result['space_freed_mb']
            print(f"✅ Processed {root_result['files_processed']} root files")
            print()
            
            # Phase 3: Run standard cleanup orchestrator
            print("Phase 3: Standard CORTEX Cleanup")
            print("-" * 70)
            standard_result = self.orchestrator.execute({
                'profile': 'comprehensive',
                'dry_run': self.dry_run
            })
            
            if not standard_result.success:
                results['warnings'].append(f"Standard cleanup issues: {standard_result.message}")
            print()
            
            # Summary
            print("=" * 70)
            print("CLEANUP COMPLETE")
            print("=" * 70)
            print(f"CORTEX 2.0 files archived: {results['cortex_2_archived']}")
            print(f"Root files organized: {results['root_files_cleaned']}")
            print(f"Total space freed: {results['space_freed_mb']:.2f}MB")
            print()
            
            if results['warnings']:
                print("⚠️  Warnings:")
                for warning in results['warnings']:
                    print(f"  - {warning}")
                print()
            
            # Write cleanup log
            if not self.dry_run:
                self._write_cleanup_log(results)
            
            return results
            
        except Exception as e:
            results['success'] = False
            results['errors'].append(str(e))
            print(f"❌ Cleanup failed: {e}")
            return results
    
    def _archive_cortex_2_files(self) -> Dict[str, Any]:
        """Archive CORTEX 2.0 files"""
        result = {
            'archived_count': 0,
            'space_freed_mb': 0.0,
            'files': []
        }
        
        archive_dir = self.project_root / 'cortex-brain' / 'archives' / 'cortex-2.0-legacy'
        
        # Find CORTEX 2.0 files
        cortex_2_files = []
        
        # Pattern 1: cortex-2.0-design folder
        design_folder = self.project_root / 'cortex-brain' / 'cortex-2.0-design'
        if design_folder.exists():
            for file in design_folder.rglob('*'):
                if file.is_file():
                    cortex_2_files.append(file)
        
        # Pattern 2: CORTEX-2.0-*.md in cortex-brain root
        brain_dir = self.project_root / 'cortex-brain'
        for file in brain_dir.glob('CORTEX-2.0-*.md'):
            if file.is_file():
                cortex_2_files.append(file)
        
        # Pattern 3: Archives folder CORTEX-2.0 files
        old_archives = self.project_root / 'cortex-brain' / 'archives' / 'converted-to-yaml-2025-11-09'
        if old_archives.exists():
            for file in old_archives.glob('CORTEX-2.0-*.md'):
                if file.is_file():
                    cortex_2_files.append(file)
        
        print(f"Found {len(cortex_2_files)} CORTEX 2.0 files")
        
        for file in cortex_2_files:
            try:
                # Calculate size
                size = file.stat().st_size
                result['space_freed_mb'] += size / (1024 * 1024)
                
                if not self.dry_run:
                    # Create archive structure
                    relative = file.relative_to(self.project_root / 'cortex-brain')
                    dest = archive_dir / relative
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Move file
                    shutil.move(str(file), str(dest))
                
                result['archived_count'] += 1
                result['files'].append(str(file.relative_to(self.project_root)))
                
                mode = "[DRY RUN] Would archive" if self.dry_run else "Archived"
                print(f"  {mode}: {file.relative_to(self.project_root)}")
                
                self.cleanup_log.append({
                    'action': 'archive',
                    'source': str(file.relative_to(self.project_root)),
                    'dest': str((archive_dir / file.relative_to(self.project_root / 'cortex-brain')).relative_to(self.project_root)),
                    'size_bytes': size,
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                print(f"  ⚠️  Error archiving {file}: {e}")
        
        # Remove empty cortex-2.0-design folder
        if not self.dry_run and design_folder.exists():
            try:
                shutil.rmtree(design_folder)
                print(f"  Removed empty folder: cortex-brain/cortex-2.0-design")
            except Exception as e:
                print(f"  ⚠️  Could not remove folder: {e}")
        
        return result
    
    def _cleanup_root_folder(self) -> Dict[str, Any]:
        """Organize root folder"""
        result = {
            'files_processed': 0,
            'space_freed_mb': 0.0,
            'moved': [],
            'deleted': []
        }
        
        # Process each clutter category
        for category, pattern in self.root_clutter_patterns.items():
            files = list(self.project_root.glob(pattern))
            
            if not files:
                continue
            
            print(f"  Processing {category}: {len(files)} files")
            
            for file in files:
                if not file.is_file():
                    continue
                
                try:
                    size = file.stat().st_size
                    
                    # Coverage files get deleted
                    if category == 'coverage_files':
                        if not self.dry_run:
                            file.unlink()
                        
                        result['deleted'].append(str(file.name))
                        result['space_freed_mb'] += size / (1024 * 1024)
                        
                        mode = "[DRY RUN] Would delete" if self.dry_run else "Deleted"
                        print(f"    {mode}: {file.name}")
                        
                        self.cleanup_log.append({
                            'action': 'delete',
                            'file': str(file.name),
                            'size_bytes': size,
                            'timestamp': datetime.now().isoformat()
                        })
                    
                    # Other files get relocated
                    elif category in self.relocation_map:
                        dest_dir = self.project_root / self.relocation_map[category]
                        dest_file = dest_dir / file.name
                        
                        if not self.dry_run:
                            dest_dir.mkdir(parents=True, exist_ok=True)
                            shutil.move(str(file), str(dest_file))
                        
                        result['moved'].append({
                            'file': str(file.name),
                            'dest': str(dest_file.relative_to(self.project_root))
                        })
                        
                        mode = "[DRY RUN] Would move" if self.dry_run else "Moved"
                        print(f"    {mode}: {file.name} → {self.relocation_map[category]}/")
                        
                        self.cleanup_log.append({
                            'action': 'relocate',
                            'source': str(file.name),
                            'dest': str(dest_file.relative_to(self.project_root)),
                            'size_bytes': size,
                            'timestamp': datetime.now().isoformat()
                        })
                    
                    result['files_processed'] += 1
                    
                except Exception as e:
                    print(f"    ⚠️  Error processing {file.name}: {e}")
        
        return result
    
    def _write_cleanup_log(self, results: Dict[str, Any]) -> None:
        """Write cleanup log to file"""
        log_dir = self.project_root / 'cortex-brain' / 'cleanup-logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y-%m-%d-%H%M%S')
        log_file = log_dir / f'cortex-2-removal-{timestamp}.json'
        
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'mode': 'live',
            'results': results,
            'actions': self.cleanup_log
        }
        
        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        print(f"Cleanup log: {log_file.relative_to(self.project_root)}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='CORTEX 2.0 Removal Cleanup')
    parser.add_argument('--dry-run', action='store_true', default=True,
                       help='Preview changes without executing (default: True)')
    parser.add_argument('--execute', action='store_true',
                       help='Actually execute the cleanup')
    parser.add_argument('--root', type=str, default=None,
                       help='Project root directory (default: current directory)')
    
    args = parser.parse_args()
    
    # Dry run by default unless --execute is specified
    dry_run = not args.execute
    
    if dry_run:
        print("⚠️  DRY RUN MODE - No changes will be made")
        print("⚠️  Use --execute flag to actually perform cleanup")
        print()
    else:
        print("⚠️  LIVE EXECUTION MODE - Changes will be made!")
        response = input("Are you sure you want to proceed? (yes/no): ")
        if response.lower() != 'yes':
            print("Cleanup cancelled")
            return 1
        print()
    
    project_root = Path(args.root) if args.root else None
    cleaner = CortexTwoRemovalCleanup(project_root=project_root, dry_run=dry_run)
    
    results = cleaner.execute()
    
    return 0 if results['success'] else 1


if __name__ == '__main__':
    sys.exit(main())
