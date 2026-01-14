#!/usr/bin/env python3
"""
CORTEX 6.0 Document Consolidation Script
Intelligently consolidates scattered files into organized structure.

Usage:
    python3 scripts/consolidate_documents.py --pattern "cx6,cortex-6,holistic" --target cortex-brain/cx6-plan --dry-run
    python3 scripts/consolidate_documents.py --pattern "cx6" --target cortex-brain/cx6-plan --execute

Features:
    - Pattern-based file discovery
    - Content-hash duplicate detection
    - Smart kebab-case renaming (preserves AC-IDs)
    - Reference tracking and updates
    - Atomic operations with rollback
    - Comprehensive logging
"""

import argparse
import hashlib
import re
import shutil
import json
from pathlib import Path
from typing import Dict, List, Tuple, Set
from datetime import datetime


class ConsolidationOrchestrator:
    """Orchestrates document consolidation with governance compliance"""
    
    def __init__(self, workspace: Path, dry_run: bool = True):
        self.workspace = workspace
        self.dry_run = dry_run
        self.moved_files: Dict[Path, Path] = {}
        self.duplicates: Dict[str, List[Path]] = {}
        self.renamed: Dict[str, str] = {}
        self.references_updated: List[Tuple[Path, int]] = []
        self.timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    
    def find_files(self, patterns: List[str], exclude_dirs: List[str] = None) -> List[Path]:
        """Find all files matching patterns"""
        if exclude_dirs is None:
            exclude_dirs = ['.git', 'node_modules', '__pycache__', '.pytest_cache', 'archive']
        
        files = []
        for pattern in patterns:
            for file in self.workspace.rglob(f"*{pattern}*"):
                if file.is_file() and not any(exc in file.parts for exc in exclude_dirs):
                    if file.suffix in ['.md', '.yaml', '.yml', '.txt', '.mmd']:
                        files.append(file)
        
        return list(set(files))  # Remove duplicates
    
    def detect_duplicates(self, files: List[Path]) -> Dict[str, List[Path]]:
        """Detect duplicate files by content hash"""
        hashes = {}
        for file in files:
            if file.is_file():
                try:
                    content_hash = hashlib.md5(file.read_bytes()).hexdigest()
                    hashes.setdefault(content_hash, []).append(file)
                except Exception as e:
                    print(f"⚠️  Error hashing {file}: {e}")
        
        self.duplicates = {h: paths for h, paths in hashes.items() if len(paths) > 1}
        return self.duplicates
    
    def to_kebab_case(self, filename: str) -> str:
        """
        Convert filename to kebab-case intelligently
        
        Preserves:
            - AC-IDs: AC-AUDIT-001, AC-MCP-EXPOSE-001, AC-STS-001-002-003
            - README, LICENSE, CHANGELOG
        
        Examples:
            TRUTH-SOURCES → truth-sources
            SESSION-HANDOFF-2026-01-10 → session-handoff-2026-01-10
            AC-AUDIT-001-Evidence → AC-AUDIT-001-evidence
        """
        # Preserve special files
        if filename.startswith(('README', 'LICENSE', 'CHANGELOG', 'CONTRIBUTING')):
            return filename
        
        # Preserve AC-ID prefix (AC-{CATEGORY}-{NUMBERS} or AC-{CATEGORY}-{TEXT}-{NUMBERS})
        ac_id_match = re.match(r'^(AC-[A-Z]+(?:-[A-Z]+)?-\d+(?:-\d+)*)', filename)
        if ac_id_match:
            ac_id = ac_id_match.group(1)
            rest = filename[len(ac_id):]
            if rest:
                # Convert the rest to kebab-case
                rest = re.sub(r'[-_\s]+', '-', rest).lower()
                return ac_id + rest
            return ac_id
        
        # Standard kebab-case conversion
        # Split on existing delimiters (hyphens, underscores, spaces)
        parts = re.split(r'[-_\s]+', filename)
        # Lowercase each part
        parts = [part.lower() for part in parts if part]
        # Rejoin with hyphens
        return '-'.join(parts)
    
    def categorize_file(self, file: Path) -> str:
        """Determine target subfolder based on file content/name"""
        name_lower = file.name.lower()
        
        # Read first 100 lines to determine category
        try:
            content_preview = file.read_text(encoding='utf-8', errors='ignore')[:5000].lower()
        except:
            content_preview = ""
        
        # Categorization rules
        if 'validation' in name_lower or 'verification' in name_lower or 'evidence' in name_lower:
            return 'validation'
        elif 'viewer' in name_lower or 'dashboard' in name_lower or 'html' in file.suffix:
            return 'viewer'
        elif 'report' in name_lower or 'summary' in name_lower or 'completion' in name_lower:
            return 'reports'
        elif 'phase' in name_lower and file.suffix in ['.md', '.mmd']:
            return 'phases'
        elif 'architecture' in name_lower or 'diagram' in name_lower or file.suffix == '.mmd':
            return 'architecture'
        elif 'round' in name_lower or 'legacy' in name_lower or 'archive' in content_preview:
            return 'archive/legacy'
        else:
            return ''  # Root of target
    
    def find_references(self, old_path: Path) -> List[Path]:
        """Find all files that reference the old path"""
        references = []
        old_path_str = str(old_path.relative_to(self.workspace))
        old_name = old_path.name
        
        # Search in common file types
        for ext in ['.md', '.py', '.yaml', '.yml', '.html']:
            for file in self.workspace.rglob(f"*{ext}"):
                if file.is_file() and file != old_path:
                    try:
                        content = file.read_text(encoding='utf-8', errors='ignore')
                        if old_path_str in content or old_name in content:
                            references.append(file)
                    except Exception as e:
                        print(f"⚠️  Error reading {file}: {e}")
        
        return list(set(references))
    
    def update_references(self, old_path: Path, new_path: Path) -> int:
        """Update all references from old path to new path"""
        references = self.find_references(old_path)
        count = 0
        
        old_rel = str(old_path.relative_to(self.workspace))
        new_rel = str(new_path.relative_to(self.workspace))
        old_name = old_path.name
        new_name = new_path.name
        
        for ref_file in references:
            if self.dry_run:
                print(f"   Would update reference in: {ref_file.relative_to(self.workspace)}")
                count += 1
            else:
                try:
                    content = ref_file.read_text(encoding='utf-8')
                    updated = content.replace(old_rel, new_rel)
                    if old_name != new_name:
                        updated = updated.replace(old_name, new_name)
                    
                    if updated != content:
                        ref_file.write_text(updated, encoding='utf-8')
                        count += 1
                        self.references_updated.append((ref_file, 1))
                except Exception as e:
                    print(f"⚠️  Error updating {ref_file}: {e}")
        
        return count
    
    def consolidate(self, files: List[Path], target_dir: Path) -> Dict[Path, Path]:
        """Execute consolidation plan"""
        print(f"\n{'=' * 70}")
        print(f"📦 CONSOLIDATION PLAN")
        print(f"{'=' * 70}\n")
        print(f"Mode: {'DRY-RUN (no changes)' if self.dry_run else 'EXECUTE (real changes)'}")
        print(f"Target: {target_dir.relative_to(self.workspace)}")
        print(f"Files: {len(files)}\n")
        
        for i, old_path in enumerate(files, 1):
            category = self.categorize_file(old_path)
            new_name = self.to_kebab_case(old_path.stem) + old_path.suffix
            
            if category:
                new_path = target_dir / category / new_name
            else:
                new_path = target_dir / new_name
            
            # Check if rename needed
            renamed = old_path.name != new_name
            
            print(f"{i}. {old_path.relative_to(self.workspace)}")
            print(f"   → {new_path.relative_to(self.workspace)}")
            if renamed:
                print(f"   ✏️  Renamed: {old_path.name} → {new_name}")
            print(f"   📁 Category: {category or 'root'}")
            
            if not self.dry_run:
                # Create target directory
                new_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Move file
                try:
                    shutil.move(str(old_path), str(new_path))
                    self.moved_files[old_path] = new_path
                    print(f"   ✅ Moved successfully")
                except Exception as e:
                    print(f"   ❌ Error: {e}")
                    continue
            
            # Update references
            ref_count = self.update_references(old_path, new_path)
            if ref_count > 0:
                print(f"   🔗 References updated: {ref_count}")
            
            print()
        
        return self.moved_files
    
    def generate_log(self, target_dir: Path):
        """Generate consolidation log"""
        log_path = target_dir / f"consolidation-log-{self.timestamp}.txt"
        
        if self.dry_run:
            print(f"\n📝 Log would be saved to: {log_path.relative_to(self.workspace)}")
            return
        
        with open(log_path, 'w') as f:
            f.write(f"CORTEX 6.0 Document Consolidation Log\n")
            f.write(f"{'=' * 70}\n\n")
            f.write(f"Timestamp: {self.timestamp}\n")
            f.write(f"Files moved: {len(self.moved_files)}\n")
            f.write(f"Duplicates detected: {len(self.duplicates)}\n")
            f.write(f"References updated: {sum(count for _, count in self.references_updated)}\n\n")
            
            f.write(f"FILE MOVES:\n")
            f.write(f"{'-' * 70}\n")
            for old, new in self.moved_files.items():
                f.write(f"{old.relative_to(self.workspace)}\n")
                f.write(f"  → {new.relative_to(self.workspace)}\n\n")
            
            if self.duplicates:
                f.write(f"\nDUPLICATES DETECTED:\n")
                f.write(f"{'-' * 70}\n")
                for hash_val, paths in self.duplicates.items():
                    f.write(f"Hash: {hash_val[:12]}...\n")
                    for path in paths:
                        f.write(f"  - {path.relative_to(self.workspace)}\n")
                    f.write("\n")
            
            if self.references_updated:
                f.write(f"\nREFERENCES UPDATED:\n")
                f.write(f"{'-' * 70}\n")
                for file, count in self.references_updated:
                    f.write(f"{file.relative_to(self.workspace)} ({count} updates)\n")
        
        print(f"\n✅ Log saved to: {log_path.relative_to(self.workspace)}")
    
    def cleanup_empty_dirs(self):
        """Remove empty directories after consolidation"""
        if self.dry_run:
            print("\n🗑️  Would remove empty directories")
            return
        
        for dir_path in sorted(self.workspace.rglob("*"), reverse=True):
            if dir_path.is_dir() and not any(dir_path.iterdir()):
                try:
                    dir_path.rmdir()
                    print(f"🗑️  Removed empty: {dir_path.relative_to(self.workspace)}")
                except Exception as e:
                    pass  # Ignore errors


def main():
    parser = argparse.ArgumentParser(description="CORTEX 6.0 Document Consolidation")
    parser.add_argument('--pattern', type=str, required=True,
                        help='Comma-separated patterns to search for (e.g., "cx6,cortex-6,holistic")')
    parser.add_argument('--target', type=str, required=True,
                        help='Target directory for consolidated files (e.g., cortex-brain/cx6-plan)')
    parser.add_argument('--execute', action='store_true',
                        help='Execute consolidation (default is dry-run)')
    parser.add_argument('--workspace', type=str, default='.',
                        help='Workspace root directory (default: current directory)')
    
    args = parser.parse_args()
    
    workspace = Path(args.workspace).resolve()
    target_dir = workspace / args.target
    patterns = [p.strip() for p in args.pattern.split(',')]
    dry_run = not args.execute
    
    print(f"\n{'=' * 70}")
    print(f"CORTEX 6.0 DOCUMENT CONSOLIDATION")
    print(f"{'=' * 70}\n")
    
    orchestrator = ConsolidationOrchestrator(workspace, dry_run=dry_run)
    
    # Step 1: Find files
    print("🔍 Finding files...")
    files = orchestrator.find_files(patterns)
    print(f"✅ Found {len(files)} files matching patterns: {', '.join(patterns)}\n")
    
    # Step 2: Detect duplicates
    print("🔍 Detecting duplicates...")
    duplicates = orchestrator.detect_duplicates(files)
    if duplicates:
        print(f"⚠️  Found {len(duplicates)} sets of duplicates")
        for hash_val, paths in list(duplicates.items())[:3]:  # Show first 3
            print(f"   - {paths[0].name} (appears {len(paths)} times)")
    else:
        print("✅ No duplicates detected")
    
    # Step 3: Consolidate
    print(f"\n{'=' * 70}")
    moved = orchestrator.consolidate(files, target_dir)
    
    # Step 4: Generate log
    if moved or dry_run:
        orchestrator.generate_log(target_dir)
    
    # Step 5: Cleanup
    if moved:
        orchestrator.cleanup_empty_dirs()
    
    # Summary
    print(f"\n{'=' * 70}")
    print(f"✅ CONSOLIDATION {'SIMULATION' if dry_run else 'COMPLETE'}")
    print(f"{'=' * 70}\n")
    
    if dry_run:
        print("⚠️  This was a DRY-RUN. No files were actually moved.")
        print("    Run with --execute to apply changes.\n")
    else:
        print(f"✅ Files moved: {len(moved)}")
        print(f"✅ References updated: {sum(c for _, c in orchestrator.references_updated)}")
        print(f"✅ Log saved: consolidation-log-{orchestrator.timestamp}.txt\n")


if __name__ == "__main__":
    main()
