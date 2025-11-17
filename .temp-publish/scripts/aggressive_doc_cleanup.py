"""
Aggressive Documentation Cleanup for CORTEX

Removes old session summaries, implementation notes, and quick references
that are historical artifacts and not actively used by CORTEX runtime.

PROTECTED (kept because CORTEX needs them):
- Core documentation in docs/ that's referenced by users
- Brain data files that CORTEX reads (knowledge-graph.yaml, etc.)
- Configuration files
- Active implementation plans being worked on

REMOVED (historical breadcrumbs):
- *-SUMMARY.md files (session notes)
- *-IMPLEMENTATION*.md files (old session notes)
- *-QUICK-REFERENCE.md files (redundant guides)
- Old phase completion reports
- Duplicate files in scripts/temp/

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import send2trash
import json

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class AggressiveDocCleanup:
    """Aggressive cleanup of historical documentation artifacts"""
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.files_to_delete = []
        self.protected_files = set()
        self.stats = {
            'scanned': 0,
            'deleted': 0,
            'protected': 0,
            'space_freed_bytes': 0
        }
        
        # Files that CORTEX actively uses (PROTECTED)
        self.essential_patterns = {
            # Core brain data
            'knowledge-graph.yaml',
            'brain-protection-rules.yaml',
            'cleanup-rules.yaml',
            'response-templates.yaml',
            'development-context.yaml',
            'cortex.config.json',
            'cortex.config.template.json',
            
            # Active design docs (being worked on)
            'CORTEX-UNIFIED-ARCHITECTURE.yaml',
            'CORTEX2-STATUS.MD',
            
            # User-facing documentation
            'README.md',
            'CHANGELOG.md',
            'LICENSE',
            
            # Current implementation summary (active)
            'SWEEPER-IMPLEMENTATION-SUMMARY.md',  # Today's work
        }
        
        # Directories that are completely protected
        self.protected_dirs = {
            '.git',
            '.venv',
            'node_modules',
            'src',  # Source code
            'tests',  # Tests
            '.github/prompts',  # Active prompts
            'prompts',  # Active prompts
            'workflows',  # Active workflows
        }
        
        # Patterns to DELETE (historical artifacts)
        self.delete_patterns = [
            '*-SUMMARY.md',
            '*-IMPLEMENTATION-SUMMARY.md',
            '*-IMPLEMENTATION.md',
            '*-QUICK-REFERENCE.md',
            '*-REFERENCE.md',
            '*-REPORT.md',
            '*-REPORT-*.md',
            '*REPORT*.md',
            'PHASE-*-SUMMARY.md',
            'PHASE-*-IMPLEMENTATION*.md',
            'SESSION-*.md',
            '*-COMPLETION-SUMMARY.md',
            '*-PROGRESS-SUMMARY.md',
            '*-SESSION-SUMMARY.md',
        ]
        
    def is_protected_dir(self, path: Path) -> bool:
        """Check if path is in a protected directory"""
        try:
            rel_path = path.relative_to(self.workspace_root)
            for protected in self.protected_dirs:
                if str(rel_path).startswith(protected.replace('/', '\\')):
                    return True
        except ValueError:
            pass
        return False
    
    def is_essential_file(self, path: Path) -> bool:
        """Check if file is essential to CORTEX runtime"""
        return path.name in self.essential_patterns
    
    def should_delete(self, path: Path) -> tuple[bool, str]:
        """
        Determine if file should be deleted.
        
        Returns:
            (should_delete, reason)
        """
        # Skip if in protected directory
        if self.is_protected_dir(path):
            return (False, f"In protected directory")
        
        # Skip if essential file
        if self.is_essential_file(path):
            return (False, f"Essential CORTEX file")
        
        # Check delete patterns
        for pattern in self.delete_patterns:
            if path.match(pattern):
                return (True, f"Matches pattern: {pattern}")
        
        return (False, "Does not match cleanup criteria")
    
    def scan_workspace(self):
        """Scan workspace for files to delete"""
        print("\n" + "=" * 80)
        print("SCANNING WORKSPACE FOR HISTORICAL ARTIFACTS")
        print("=" * 80)
        print()
        
        for file_path in self.workspace_root.rglob('*.md'):
            self.stats['scanned'] += 1
            
            should_del, reason = self.should_delete(file_path)
            
            if should_del:
                size = file_path.stat().st_size if file_path.exists() else 0
                self.files_to_delete.append({
                    'path': file_path,
                    'size': size,
                    'reason': reason
                })
            else:
                self.protected_files.add(file_path)
        
        print(f"✅ Scanned {self.stats['scanned']} markdown files")
        print(f"   Found {len(self.files_to_delete)} files to delete")
        print(f"   Protected {len(self.protected_files)} files")
        print()
    
    def show_preview(self):
        """Show what will be deleted"""
        print("=" * 80)
        print("DELETION PREVIEW")
        print("=" * 80)
        print()
        
        # Group by directory
        by_dir = {}
        for item in self.files_to_delete:
            dir_path = item['path'].parent
            if dir_path not in by_dir:
                by_dir[dir_path] = []
            by_dir[dir_path].append(item)
        
        total_size = 0
        for dir_path in sorted(by_dir.keys()):
            files = by_dir[dir_path]
            dir_size = sum(f['size'] for f in files)
            total_size += dir_size
            
            rel_dir = dir_path.relative_to(self.workspace_root)
            print(f"\n📁 {rel_dir}/ ({len(files)} files, {dir_size/1024:.1f} KB)")
            
            for item in sorted(files, key=lambda x: x['path'].name):
                print(f"   🗑️  {item['path'].name} ({item['size']/1024:.1f} KB)")
        
        print()
        print("=" * 80)
        print(f"TOTAL: {len(self.files_to_delete)} files, {total_size/1024/1024:.2f} MB")
        print("=" * 80)
        print()
        
        return total_size
    
    def execute_cleanup(self):
        """Execute the cleanup (move files to Recycle Bin)"""
        print("\n" + "=" * 80)
        print("EXECUTING CLEANUP")
        print("=" * 80)
        print()
        
        errors = []
        deleted_files = []
        
        for item in self.files_to_delete:
            try:
                if item['path'].exists():
                    # Move to Recycle Bin
                    send2trash.send2trash(str(item['path']))
                    self.stats['deleted'] += 1
                    self.stats['space_freed_bytes'] += item['size']
                    deleted_files.append({
                        'path': str(item['path'].relative_to(self.workspace_root)),
                        'size_bytes': item['size'],
                        'reason': item['reason'],
                        'deleted_at': datetime.now().isoformat()
                    })
                    
                    if self.stats['deleted'] % 10 == 0:
                        print(f"   Deleted {self.stats['deleted']} files...")
                        
            except Exception as e:
                errors.append(f"{item['path'].name}: {e}")
        
        print()
        print(f"✅ Deleted {self.stats['deleted']} files")
        print(f"   Space freed: {self.stats['space_freed_bytes']/1024/1024:.2f} MB")
        
        if errors:
            print(f"\n⚠️  {len(errors)} errors:")
            for error in errors[:10]:  # Show first 10
                print(f"   - {error}")
        
        # Save audit log
        self.save_audit_log(deleted_files)
        
        return len(errors) == 0
    
    def save_audit_log(self, deleted_files):
        """Save audit log of deleted files"""
        log_dir = self.workspace_root / 'cortex-brain' / 'cleanup-logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        log_file = log_dir / f'aggressive-cleanup-{timestamp}.json'
        
        audit_data = {
            'timestamp': datetime.now().isoformat(),
            'operation': 'aggressive_doc_cleanup',
            'mode': 'recycle_bin',
            'recoverable': True,
            'recovery_instructions': 'Files can be restored from OS Recycle Bin',
            'stats': {
                'files_scanned': self.stats['scanned'],
                'files_deleted': self.stats['deleted'],
                'files_protected': self.stats['protected'],
                'space_freed_mb': self.stats['space_freed_bytes'] / (1024 * 1024)
            },
            'deleted_files': deleted_files
        }
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(audit_data, f, indent=2)
        
        print(f"\n📄 Audit log saved: {log_file.relative_to(self.workspace_root)}")


def main():
    """Main execution"""
    print("=" * 80)
    print("CORTEX AGGRESSIVE DOCUMENTATION CLEANUP")
    print("=" * 80)
    print()
    print("Author:     Asif Hussain")
    print("Copyright:  © 2024-2025 Asif Hussain. All rights reserved.")
    print("License:    Proprietary")
    print()
    print("This will remove historical documentation artifacts:")
    print("  - Session summaries (*-SUMMARY.md)")
    print("  - Implementation notes (*-IMPLEMENTATION.md)")
    print("  - Quick references (*-QUICK-REFERENCE.md)")
    print("  - Old phase reports (PHASE-*-*.md)")
    print()
    print("PROTECTED (essential CORTEX files):")
    print("  - Brain data (knowledge-graph.yaml, etc.)")
    print("  - Active configuration files")
    print("  - User-facing documentation")
    print("  - Source code and tests")
    print()
    print("All files moved to Recycle Bin - FULLY RECOVERABLE!")
    print("=" * 80)
    print()
    
    workspace_root = Path(__file__).parent.parent
    
    # Create cleanup instance
    cleanup = AggressiveDocCleanup(workspace_root)
    
    # Scan workspace
    cleanup.scan_workspace()
    
    # Show preview
    total_size = cleanup.show_preview()
    
    if len(cleanup.files_to_delete) == 0:
        print("✅ No files to clean up!")
        return
    
    # Confirm
    print(f"Ready to move {len(cleanup.files_to_delete)} files ({total_size/1024/1024:.2f} MB) to Recycle Bin.")
    print()
    response = input("Continue? (yes/no): ").strip().lower()
    
    if response not in ['yes', 'y']:
        print("\n❌ Cancelled.")
        return
    
    # Execute
    start_time = datetime.now()
    success = cleanup.execute_cleanup()
    duration = (datetime.now() - start_time).total_seconds()
    
    # Summary
    print()
    print("=" * 80)
    if success:
        print("✅ CLEANUP COMPLETED SUCCESSFULLY")
    else:
        print("⚠️  CLEANUP COMPLETED WITH ERRORS")
    print("=" * 80)
    print()
    print(f"Files deleted:     {cleanup.stats['deleted']}")
    print(f"Space freed:       {cleanup.stats['space_freed_bytes']/1024/1024:.2f} MB")
    print(f"Duration:          {duration:.2f}s")
    print()
    print("✅ All files moved to Recycle Bin - You can restore them anytime!")
    print("=" * 80)


if __name__ == "__main__":
    main()
