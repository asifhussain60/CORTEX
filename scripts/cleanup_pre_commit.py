#!/usr/bin/env python3
"""
Pre-Commit Cleanup Script for CORTEX 4.0

Runs BEFORE commit to:
1. Delete temp files, test artifacts, orphaned reports
2. Reorganize misplaced files to correct locations
3. Auto-stage reorganized files for commit

Usage:
    python scripts/cleanup_pre_commit.py [--dry-run]
    
Exit Codes:
    0 - Cleanup successful
    1 - Cleanup failed (blocks commit)
"""

import argparse
import shutil
import sys
from pathlib import Path
from typing import List, Tuple
import subprocess


class PreCommitCleanup:
    """Pre-commit cleanup orchestrator"""
    
    def __init__(self, repo_root: Path, dry_run: bool = False):
        self.repo_root = repo_root
        self.dry_run = dry_run
        self.deleted_files = []
        self.moved_files = []
        self.errors = []
        
        # Temp file patterns to delete
        self.temp_patterns = [
            '*.tmp',
            '*.temp',
            '*.bak',
            '*.old',
            '*.cache',
            '*~',
            '*.swp',
            '*.swo',
            '.DS_Store',
            'Thumbs.db',
        ]
        
        # Folders to clean recursively
        self.temp_folders = [
            '__pycache__',
            '.pytest_cache',
            '.mypy_cache',
            '.ruff_cache',
            'htmlcov',
            '.coverage',
            '.tox',
            '*.egg-info',
        ]
        
        # Protected paths (never delete)
        self.protected_paths = [
            '.git',
            '.github',
            '.venv',
            'venv',
            'node_modules',
            'cortex-brain/tier0',
            'cortex-brain/tier1',
            'cortex-brain/tier2',
            'cortex-brain/tier3',
        ]
        
        # Orphaned report patterns (old/stale reports not in correct locations)
        self.orphaned_report_patterns = [
            'coverage.json',  # Should be in reports/
            'TEST-*.xml',     # Should be in reports/
            'test-results.json',
            'validation-*.md',  # Should be in reports/ if not current
            '*-report-*.md',    # Should be in reports/
        ]
    
    def is_protected(self, path: Path) -> bool:
        """Check if path is protected from deletion"""
        try:
            relative = path.relative_to(self.repo_root)
            return any(str(relative).startswith(p) for p in self.protected_paths)
        except ValueError:
            return False
    
    def delete_temp_files(self) -> int:
        """Delete temporary files matching patterns"""
        print("\n[>] Cleaning temporary files...")
        deleted_count = 0
        
        for pattern in self.temp_patterns:
            for file_path in self.repo_root.rglob(pattern):
                if file_path.is_file() and not self.is_protected(file_path):
                    try:
                        relative = file_path.relative_to(self.repo_root)
                        if self.dry_run:
                            print(f"  [DRY-RUN] Would delete: {relative}")
                        else:
                            file_path.unlink()
                            print(f"  [OK] Deleted: {relative}")
                        self.deleted_files.append(str(relative))
                        deleted_count += 1
                    except Exception as e:
                        self.errors.append(f"Failed to delete {relative}: {e}")
        
        return deleted_count
    
    def delete_temp_folders(self) -> int:
        """Delete temporary folders recursively"""
        print("\n[>] Cleaning temporary folders...")
        deleted_count = 0
        
        for pattern in self.temp_folders:
            for folder_path in self.repo_root.rglob(pattern):
                if folder_path.is_dir() and not self.is_protected(folder_path):
                    try:
                        relative = folder_path.relative_to(self.repo_root)
                        if self.dry_run:
                            print(f"  [DRY-RUN] Would delete: {relative}/")
                        else:
                            shutil.rmtree(folder_path)
                            print(f"  [OK] Deleted: {relative}/")
                        self.deleted_files.append(str(relative) + "/")
                        deleted_count += 1
                    except Exception as e:
                        self.errors.append(f"Failed to delete {relative}: {e}")
        
        return deleted_count
    
    def delete_orphaned_reports(self) -> int:
        """Delete orphaned reports from root/stray locations"""
        print("\n[>] Cleaning orphaned reports...")
        deleted_count = 0
        
        # Only check root and immediate subdirectories (not deep in brain)
        for pattern in self.orphaned_report_patterns:
            for file_path in self.repo_root.glob(pattern):
                if file_path.is_file() and not self.is_protected(file_path):
                    try:
                        relative = file_path.relative_to(self.repo_root)
                        if self.dry_run:
                            print(f"  [DRY-RUN] Would delete: {relative}")
                        else:
                            file_path.unlink()
                            print(f"  [OK] Deleted: {relative}")
                        self.deleted_files.append(str(relative))
                        deleted_count += 1
                    except Exception as e:
                        self.errors.append(f"Failed to delete {relative}: {e}")
        
        return deleted_count
    
    def reorganize_stray_tests(self) -> int:
        """Move stray test files to tests/ folder"""
        print("\n[>] Reorganizing stray test files...")
        moved_count = 0
        
        # Find test files outside tests/ folder
        for test_file in self.repo_root.rglob('test_*.py'):
            if 'tests/' not in str(test_file) and not self.is_protected(test_file):
                try:
                    relative = test_file.relative_to(self.repo_root)
                    
                    # Determine target location based on path
                    if 'src/' in str(relative):
                        # Mirror src/ structure in tests/
                        target_path = self.repo_root / 'tests' / relative.relative_to('src')
                    else:
                        # Move to tests/misc/
                        target_path = self.repo_root / 'tests' / 'misc' / test_file.name
                    
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    if self.dry_run:
                        print(f"  [DRY-RUN] Would move: {relative} -> {target_path.relative_to(self.repo_root)}")
                    else:
                        shutil.move(str(test_file), str(target_path))
                        print(f"  [OK] Moved: {relative} -> {target_path.relative_to(self.repo_root)}")
                        self._git_add(target_path)
                    
                    self.moved_files.append((str(relative), str(target_path.relative_to(self.repo_root))))
                    moved_count += 1
                except Exception as e:
                    self.errors.append(f"Failed to move {relative}: {e}")
        
        return moved_count
    
    def reorganize_stray_docs(self) -> int:
        """Move stray docs to cortex-brain/documents/{category}/"""
        print("\n[>] Reorganizing stray documentation...")
        moved_count = 0
        
        # Find markdown files in root (excluding README, CHANGELOG, LICENSE)
        excluded_root_docs = ['README.md', 'CHANGELOG.md', 'LICENSE', 'LICENSE.md']
        
        for doc_file in self.repo_root.glob('*.md'):
            if doc_file.name not in excluded_root_docs:
                try:
                    relative = doc_file.relative_to(self.repo_root)
                    
                    # Determine category from filename
                    name_lower = doc_file.name.lower()
                    if 'report' in name_lower or 'status' in name_lower:
                        category = 'reports'
                    elif 'analysis' in name_lower or 'review' in name_lower:
                        category = 'analysis'
                    elif 'guide' in name_lower or 'how-to' in name_lower:
                        category = 'implementation-guides'
                    elif 'plan' in name_lower or 'roadmap' in name_lower:
                        category = 'planning'
                    else:
                        category = 'summaries'
                    
                    target_path = self.repo_root / 'cortex-brain' / 'documents' / category / doc_file.name
                    
                    # Skip if already in correct location
                    if target_path.exists():
                        print(f"  [SKIP] Already exists: {target_path.relative_to(self.repo_root)}")
                        continue
                    
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    if self.dry_run:
                        print(f"  [DRY-RUN] Would move: {relative} -> {target_path.relative_to(self.repo_root)}")
                    else:
                        shutil.move(str(doc_file), str(target_path))
                        print(f"  [OK] Moved: {relative} -> {target_path.relative_to(self.repo_root)}")
                        self._git_add(target_path)
                    
                    self.moved_files.append((str(relative), str(target_path.relative_to(self.repo_root))))
                    moved_count += 1
                except Exception as e:
                    self.errors.append(f"Failed to move {relative}: {e}")
        
        return moved_count
    
    def _git_add(self, file_path: Path):
        """Stage reorganized file in git"""
        try:
            subprocess.run(
                ['git', 'add', str(file_path)],
                cwd=self.repo_root,
                check=True,
                capture_output=True
            )
        except subprocess.CalledProcessError as e:
            self.errors.append(f"Failed to stage {file_path}: {e}")
    
    def run(self) -> Tuple[bool, dict]:
        """Execute all cleanup operations"""
        print("\n" + "="*80)
        print("[>] CORTEX 4.0 Pre-Commit Cleanup")
        if self.dry_run:
            print("[!] DRY-RUN MODE - No changes will be made")
        print("="*80)
        
        # Execute cleanup phases
        deleted_files = self.delete_temp_files()
        deleted_folders = self.delete_temp_folders()
        deleted_reports = self.delete_orphaned_reports()
        moved_tests = self.reorganize_stray_tests()
        moved_docs = self.reorganize_stray_docs()
        
        # Summary
        print("\n" + "="*80)
        print("[#] CLEANUP SUMMARY")
        print("="*80)
        print(f"Temp files deleted:    {deleted_files}")
        print(f"Temp folders deleted:  {deleted_folders}")
        print(f"Orphaned reports:      {deleted_reports}")
        print(f"Tests reorganized:     {moved_tests}")
        print(f"Docs reorganized:      {moved_docs}")
        
        if self.errors:
            print(f"\n[X] ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  {error}")
            return False, self._build_summary()
        
        total_changes = deleted_files + deleted_folders + deleted_reports + moved_tests + moved_docs
        
        if total_changes > 0:
            print(f"\n[OK] Cleanup complete: {total_changes} changes")
            if not self.dry_run:
                self._auto_commit_cleanup(total_changes)
        else:
            print("\n[OK] No cleanup needed")
        
        print("="*80 + "\n")
        
        return True, self._build_summary()
    
    def _auto_commit_cleanup(self, change_count: int):
        """Auto-commit cleanup changes (additions + deletions)"""
        try:
            print("\n[>] Auto-committing cleanup changes...")
            
            # Stage ALL changes: additions, modifications, AND deletions
            # -A flag captures everything including deletions
            result = subprocess.run(
                ['git', 'add', '-A'],
                cwd=self.repo_root,
                check=True,
                capture_output=True,
                text=True
            )
            
            # Verify we have staged changes
            status = subprocess.run(
                ['git', 'diff', '--cached', '--name-only'],
                cwd=self.repo_root,
                capture_output=True,
                text=True
            )
            
            staged_files = status.stdout.strip().split('\n') if status.stdout.strip() else []
            
            if not staged_files:
                print("[!] No changes to commit (already clean)")
                return
            
            # Build detailed commit message
            commit_msg = f"chore: Auto-cleanup by pre-commit hook ({len(staged_files)} files)\n\n"
            commit_msg += f"Deletions: {len([f for f in self.deleted_files])}\n"
            commit_msg += f"Reorganizations: {len([f for f in self.moved_files])}\n\n"
            commit_msg += "Changes:\n"
            for f in staged_files[:10]:  # Show first 10 files
                commit_msg += f"  - {f}\n"
            if len(staged_files) > 10:
                commit_msg += f"  ... and {len(staged_files) - 10} more files\n"
            
            # Commit with --no-verify to avoid recursion
            result = subprocess.run(
                ['git', 'commit', '--no-verify', '-m', commit_msg],
                cwd=self.repo_root,
                check=True,
                capture_output=True,
                text=True
            )
            
            print(f"[OK] Cleanup auto-committed: {len(staged_files)} files")
            print("[>] Your original commit will now proceed\n")
            
        except subprocess.CalledProcessError as e:
            print(f"[X] Auto-commit failed: {e}")
            if e.stderr:
                print(f"    Error: {e.stderr}")
            # Don't exit - let user's commit proceed
    
    def _build_summary(self) -> dict:
        """Build summary of cleanup operations"""
        return {
            'deleted_files': self.deleted_files,
            'moved_files': self.moved_files,
            'errors': self.errors,
            'total_changes': len(self.deleted_files) + len(self.moved_files)
        }


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description='CORTEX 4.0 Pre-Commit Cleanup')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    args = parser.parse_args()
    
    repo_root = Path(__file__).parent.parent
    cleanup = PreCommitCleanup(repo_root, dry_run=args.dry_run)
    success, summary = cleanup.run()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
