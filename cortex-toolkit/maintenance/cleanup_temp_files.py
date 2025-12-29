"""
CORTEX Temporary File Cleanup Tool
Interactive deletion with preview, confirmation, and rollback capability.
"""

import json
import os
import yaml
import shutil
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import re
import subprocess

class TempFileCleanup:
    """Safe temporary file cleanup with interactive controls."""
    
    def __init__(self, config_file='cortex-brain/cleanup-detection-patterns.yaml'):
        """Initialize cleanup tool with configuration."""
        self.config_file = config_file
        self.config = self._load_config()
        self.workspace_root = Path.cwd()
        self.candidates = defaultdict(list)
        self.git_tracked = set()
        self.deletion_log = []
        
    def _load_config(self):
        """Load detection patterns from YAML configuration."""
        with open(self.config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _get_git_tracked_files(self):
        """Get list of git-tracked files."""
        try:
            result = subprocess.run(
                ['git', 'ls-files'],
                capture_output=True,
                text=True,
                check=True
            )
            # Convert to absolute paths and normalize
            tracked = set()
            for line in result.stdout.strip().split('\n'):
                if line:
                    abs_path = (self.workspace_root / line).resolve()
                    tracked.add(str(abs_path))
            return tracked
        except subprocess.CalledProcessError:
            print("⚠️  Warning: Could not get git tracked files. Proceeding with caution.")
            return set()
    
    def _is_protected(self, file_path):
        """Check if file is protected from cleanup."""
        path_str = str(file_path)
        name = os.path.basename(path_str)
        
        # Check protected directories
        for protected_dir in self.config['protected_directories']:
            if protected_dir in path_str:
                return True
        
        # Check protected files
        if name in self.config['protected_files']:
            return True
        
        # Check custom exclusions
        custom_exclusions = self.config.get('custom_exclusions') or []
        for pattern in custom_exclusions:
            if pattern and re.search(pattern, name):
                return True
        
        # Never delete tracked files (if git integration enabled)
        if self.config['git_filters']['exclude_tracked']:
            if str(file_path.resolve()) in self.git_tracked:
                return True
        
        return False
    
    def _matches_pattern(self, file_path, name_lower):
        """Check if file matches cleanup patterns."""
        matches = []
        name = os.path.basename(str(file_path))
        
        # Check temporal keywords
        for keyword in self.config['temporal_keywords']:
            if keyword.lower() in name_lower:
                matches.append(f'keyword:{keyword}')
        
        # Check temporary extensions
        for ext in self.config['temporary_extensions']:
            if name_lower.endswith(ext.lower()):
                matches.append(f'extension:{ext}')
        
        # Check regex patterns
        for pattern_name, pattern in self.config['regex_patterns'].items():
            if re.search(pattern, name):
                matches.append(f'pattern:{pattern_name}')
        
        return matches
    
    def scan_workspace(self):
        """Scan workspace for cleanup candidates."""
        print("🔍 Scanning workspace for temporary files...")
        print(f"📂 Root: {self.workspace_root}")
        
        # Get git tracked files if enabled
        if self.config['git_filters']['exclude_tracked']:
            print("📊 Loading git tracked files...")
            self.git_tracked = self._get_git_tracked_files()
            print(f"   Found {len(self.git_tracked)} tracked files")
        
        excluded_dirs = set(self.config['protected_directories'])
        scanned_count = 0
        
        for root, dirs, files in os.walk(self.workspace_root):
            # Filter out protected directories
            dirs[:] = [d for d in dirs if d not in excluded_dirs]
            
            for filename in files:
                file_path = Path(root) / filename
                scanned_count += 1
                
                if scanned_count % 500 == 0:
                    print(f"   Scanned {scanned_count} files...", end='\r')
                
                # Skip protected files
                if self._is_protected(file_path):
                    continue
                
                # Check for pattern matches
                name_lower = filename.lower()
                matches = self._matches_pattern(file_path, name_lower)
                
                if matches:
                    # Categorize by risk level
                    category = self._categorize_file(file_path, matches)
                    self.candidates[category].append({
                        'path': file_path,
                        'size': file_path.stat().st_size,
                        'modified': datetime.fromtimestamp(file_path.stat().st_mtime),
                        'matches': matches
                    })
        
        print(f"\n✅ Scanned {scanned_count} files")
        print(f"📋 Found {sum(len(files) for files in self.candidates.values())} cleanup candidates")
    
    def _categorize_file(self, file_path, matches):
        """Categorize file by cleanup risk level."""
        name = os.path.basename(str(file_path))
        ext = file_path.suffix.lower()
        
        # HIGH CONFIDENCE: Backup extensions
        if any('extension:' in m for m in matches):
            if ext in ['.bak', '.backup', '.old', '.orig']:
                return 'high_confidence'
        
        # MEDIUM CONFIDENCE: Temporal keywords + age check
        if any('keyword:' in m for m in matches):
            # Check if old enough based on type
            age_days = (datetime.now() - datetime.fromtimestamp(file_path.stat().st_mtime)).days
            
            if 'summary' in name.lower() and age_days > self.config['age_thresholds']['session_summaries']:
                return 'medium_confidence'
            if 'report' in name.lower() and age_days > self.config['age_thresholds']['reports']:
                return 'medium_confidence'
        
        # LOW CONFIDENCE: Pattern matches but review needed
        return 'review_required'
    
    def show_preview(self):
        """Display interactive preview of cleanup candidates."""
        if not self.candidates:
            print("\n✅ No temporary files found for cleanup!")
            return False
        
        print("\n" + "="*80)
        print("📋 CLEANUP PREVIEW")
        print("="*80)
        
        categories = [
            ('high_confidence', '🔴 HIGH CONFIDENCE (Safe to delete)', 'Backup files, obvious temps'),
            ('medium_confidence', '🟡 MEDIUM CONFIDENCE (Review recommended)', 'Old reports/summaries'),
            ('review_required', '⚪ REVIEW REQUIRED (Manual check needed)', 'Pattern matches, needs verification')
        ]
        
        total_size = 0
        total_count = 0
        
        for category, label, description in categories:
            files = self.candidates.get(category, [])
            if not files:
                continue
            
            category_size = sum(f['size'] for f in files)
            total_size += category_size
            total_count += len(files)
            
            print(f"\n{label}")
            print(f"Description: {description}")
            print(f"Files: {len(files)} | Size: {self._format_size(category_size)}")
            print("-" * 80)
            
            # Show first 5 files
            for i, file_info in enumerate(files[:5]):
                rel_path = file_info['path'].relative_to(self.workspace_root)
                age_days = (datetime.now() - file_info['modified']).days
                print(f"  {i+1}. {rel_path}")
                print(f"     Size: {self._format_size(file_info['size'])} | "
                      f"Age: {age_days} days | "
                      f"Matches: {', '.join(file_info['matches'][:2])}")
            
            if len(files) > 5:
                print(f"  ... and {len(files) - 5} more files")
        
        print("\n" + "="*80)
        print(f"📊 TOTAL: {total_count} files | {self._format_size(total_size)}")
        print("="*80)
        
        return True
    
    def _format_size(self, size_bytes):
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def interactive_cleanup(self, dry_run=None):
        """Interactive cleanup with confirmation."""
        if dry_run is None:
            dry_run = self.config['safety']['dry_run_default']
        
        if not self.show_preview():
            return
        
        print("\n" + "="*80)
        print("🎯 CLEANUP OPTIONS")
        print("="*80)
        print("1. Delete HIGH CONFIDENCE only (safest)")
        print("2. Delete HIGH + MEDIUM CONFIDENCE (recommended)")
        print("3. Delete ALL candidates (includes review required)")
        print("4. Custom selection (choose specific files)")
        print("5. Cancel (no changes)")
        print("="*80)
        
        choice = input("\nYour choice (1-5): ").strip()
        
        if choice == '5':
            print("❌ Cleanup cancelled.")
            return
        
        # Determine files to delete
        files_to_delete = []
        if choice == '1':
            files_to_delete = self.candidates.get('high_confidence', [])
        elif choice == '2':
            files_to_delete = self.candidates.get('high_confidence', []) + \
                            self.candidates.get('medium_confidence', [])
        elif choice == '3':
            for category in self.candidates.values():
                files_to_delete.extend(category)
        elif choice == '4':
            files_to_delete = self._custom_selection()
        else:
            print("❌ Invalid choice. Cleanup cancelled.")
            return
        
        if not files_to_delete:
            print("❌ No files selected for cleanup.")
            return
        
        # Final confirmation
        total_size = sum(f['size'] for f in files_to_delete)
        print(f"\n⚠️  About to delete {len(files_to_delete)} files ({self._format_size(total_size)})")
        
        if dry_run:
            print("🔍 DRY RUN MODE: Files will NOT be actually deleted")
        
        confirm = input("\nConfirm deletion? (yes/no): ").strip().lower()
        if confirm != 'yes':
            print("❌ Cleanup cancelled.")
            return
        
        # Perform deletion
        self._delete_files(files_to_delete, dry_run)
    
    def _custom_selection(self):
        """Allow user to select specific files for deletion."""
        print("\n📋 CUSTOM FILE SELECTION")
        print("Enter file numbers to delete (comma-separated), or 'all' for all files")
        print("Example: 1,3,5-10,15")
        
        # Create flat list with indices
        all_files = []
        for category in ['high_confidence', 'medium_confidence', 'review_required']:
            all_files.extend(self.candidates.get(category, []))
        
        # Show all files with numbers
        for i, file_info in enumerate(all_files, 1):
            rel_path = file_info['path'].relative_to(self.workspace_root)
            print(f"{i:3d}. {rel_path}")
        
        selection = input("\nYour selection: ").strip()
        
        if selection.lower() == 'all':
            return all_files
        
        # Parse selection
        selected_indices = set()
        for part in selection.split(','):
            part = part.strip()
            if '-' in part:
                start, end = map(int, part.split('-'))
                selected_indices.update(range(start, end + 1))
            else:
                selected_indices.add(int(part))
        
        return [all_files[i-1] for i in selected_indices if 1 <= i <= len(all_files)]
    
    def _delete_files(self, files, dry_run):
        """Delete files and create deletion log."""
        print("\n" + "="*80)
        if dry_run:
            print("🔍 DRY RUN - Simulating deletion")
        else:
            print("🗑️  DELETING FILES")
        print("="*80)
        
        deleted_count = 0
        failed_count = 0
        
        for file_info in files:
            file_path = file_info['path']
            rel_path = file_path.relative_to(self.workspace_root)
            
            try:
                if not dry_run:
                    file_path.unlink()
                
                deleted_count += 1
                print(f"✅ {'[DRY RUN] ' if dry_run else ''}Deleted: {rel_path}")
                
                # Log deletion
                self.deletion_log.append({
                    'path': str(rel_path),
                    'size': file_info['size'],
                    'deleted_at': datetime.now().isoformat(),
                    'matches': file_info['matches'],
                    'dry_run': dry_run
                })
                
            except Exception as e:
                failed_count += 1
                print(f"❌ Failed: {rel_path} - {str(e)}")
        
        # Save deletion log
        if self.config['safety']['create_deletion_log']:
            self._save_deletion_log(dry_run)
        
        print("\n" + "="*80)
        print(f"📊 CLEANUP {'SIMULATION ' if dry_run else ''}COMPLETE")
        print(f"✅ {'Would delete' if dry_run else 'Deleted'}: {deleted_count} files")
        if failed_count > 0:
            print(f"❌ Failed: {failed_count} files")
        print("="*80)
    
    def _save_deletion_log(self, dry_run):
        """Save deletion log for rollback capability."""
        log_dir = Path(self.config['safety']['deletion_log_path'])
        log_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = log_dir / f"deletion-log-{timestamp}{'_DRYRUN' if dry_run else ''}.json"
        
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'dry_run': dry_run,
            'total_files': len(self.deletion_log),
            'total_size': sum(f['size'] for f in self.deletion_log),
            'files': self.deletion_log
        }
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2)
        
        print(f"\n📝 Deletion log saved: {log_file.relative_to(self.workspace_root)}")


def main():
    """Main entry point."""
    print("="*80)
    print("🧠 CORTEX Temporary File Cleanup Tool")
    print("="*80)
    print("Version: 1.0")
    print("Safe cleanup with preview, confirmation, and rollback capability")
    print("="*80)
    
    cleanup = TempFileCleanup()
    cleanup.scan_workspace()
    cleanup.interactive_cleanup()


if __name__ == '__main__':
    main()
