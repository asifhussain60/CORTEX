"""
Phase 2: Automated Safe Deletion
Deletes archived duplicates and backup files identified as safe.
"""

import json
import shutil
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

print("=" * 80)
print("PHASE 2: AUTOMATED SAFE DELETION")
print("=" * 80)
print()

# Load categorization from Phase 1
categorization_path = Path('cortex-brain/documents/analysis/duplicate-categorization-phase1.json')

print("[*] Loading Phase 1 categorization...")
with open(categorization_path, 'r', encoding='utf-8') as f:
    categorization = json.load(f)

categories = categorization['categories']
consolidation_map = categorization['consolidation_map']

print(f"[+] Loaded categorization:")
print(f"    Auto-safe files: {categories['auto_safe']['count']}")
print(f"    Semi-safe files: {categories['semi_safe']['count']}")
print()

# Create backup directory
backup_root = Path('cortex-brain/backups/phase2-deletion')
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
backup_dir = backup_root / timestamp
backup_dir.mkdir(parents=True, exist_ok=True)

print(f"[*] Backup directory: {backup_dir}")
print()

# Task 2.1: Delete archived duplicates
print("[*] Task 2.1: Deleting archived duplicates...")
print()

deleted_files = []
space_freed_mb = 0.0
errors = []

auto_safe_files = categories['auto_safe']['files']
project_root = Path.cwd()

for item in auto_safe_files:
    file_path_str = item['file']
    
    # Convert to absolute path
    if not Path(file_path_str).is_absolute():
        file_path = project_root / file_path_str
    else:
        file_path = Path(file_path_str)
    
    # Safety check: verify file is in archives
    if 'archives' not in str(file_path).lower():
        errors.append(f"SAFETY: {file_path} not in archives - skipped")
        continue
    
    # Check if file exists
    if not file_path.exists():
        continue  # Skip silently if already deleted
    
    try:
        # Get file size before deletion
        size_mb = file_path.stat().st_size / (1024 * 1024)
        
        # Create backup
        relative_path = file_path.relative_to(project_root)
        backup_path = backup_dir / relative_path
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file_path, backup_path)
        
        # Delete file
        file_path.unlink()
        
        deleted_files.append({
            'file': str(file_path),
            'size_mb': size_mb,
            'backed_up': str(backup_path)
        })
        space_freed_mb += size_mb
        
        if len(deleted_files) % 50 == 0:
            print(f"    [+] Deleted {len(deleted_files)} files ({space_freed_mb:.2f} MB freed)")
        
    except Exception as e:
        errors.append(f"ERROR deleting {file_path}: {e}")

print(f"[+] Task 2.1 complete: {len(deleted_files)} archived files deleted")
print(f"    Space freed: {space_freed_mb:.2f} MB")
print()

# Task 2.2: Remove backup files
print("[*] Task 2.2: Removing backup files...")
print()

backup_deleted = []

# Process consolidation map for backup deletion strategy
for filename, data in consolidation_map.items():
    if data['strategy'] == 'delete_backups':
        for secondary in data['secondaries']:
            # Convert to absolute path
            if not Path(secondary).is_absolute():
                file_path = project_root / secondary
            else:
                file_path = Path(secondary)
            
            # Safety check: verify it's a backup file
            if not (file_path.name.endswith(('.backup', '.old', '.bak')) or 
                    'backup' in str(file_path).lower()):
                continue
            
            if not file_path.exists():
                continue
            
            try:
                size_mb = file_path.stat().st_size / (1024 * 1024)
                
                # Backup before deletion
                relative_path = file_path.relative_to(Path.cwd())
                backup_path = backup_dir / relative_path
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, backup_path)
                
                # Delete
                file_path.unlink()
                
                backup_deleted.append({
                    'file': str(file_path),
                    'size_mb': size_mb
                })
                space_freed_mb += size_mb
                
            except Exception as e:
                errors.append(f"ERROR deleting backup {file_path}: {e}")

print(f"[+] Task 2.2 complete: {len(backup_deleted)} backup files deleted")
print(f"    Additional space freed: {sum(b['size_mb'] for b in backup_deleted):.2f} MB")
print()

# Task 2.3: Clean test duplicates
print("[*] Task 2.3: Cleaning test duplicates...")
print()

test_deleted = []
semi_safe_files = categories['semi_safe']['files']

for item in semi_safe_files:
    file_path_str = item['file']
    
    # Convert to absolute path
    if not Path(file_path_str).is_absolute():
        file_path = project_root / file_path_str
    else:
        file_path = Path(file_path_str)
    
    # Only delete if it's a test file in wrong location (not in tests/ directory)
    if 'test' in file_path.name.lower() and '\\tests\\' not in str(file_path):
        if not file_path.exists():
            continue
        
        try:
            size_mb = file_path.stat().st_size / (1024 * 1024)
            
            # Backup
            relative_path = file_path.relative_to(Path.cwd())
            backup_path = backup_dir / relative_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, backup_path)
            
            # Delete
            file_path.unlink()
            
            test_deleted.append({
                'file': str(file_path),
                'size_mb': size_mb
            })
            space_freed_mb += size_mb
            
        except Exception as e:
            errors.append(f"ERROR deleting test {file_path}: {e}")

print(f"[+] Task 2.3 complete: {len(test_deleted)} test files deleted")
print(f"    Additional space freed: {sum(t['size_mb'] for t in test_deleted):.2f} MB")
print()

# Clean empty directories
print("[*] Cleaning empty directories...")
empty_dirs_removed = []

for dirpath in sorted(Path('cortex-brain/archives').rglob('*'), reverse=True):
    if not dirpath.is_dir():
        continue
    
    try:
        if not any(dirpath.iterdir()):
            dirpath.rmdir()
            empty_dirs_removed.append(str(dirpath))
    except (OSError, PermissionError):
        pass

print(f"[+] Removed {len(empty_dirs_removed)} empty directories")
print()

# Save Phase 2 results
results = {
    'phase': 2,
    'timestamp': datetime.now().isoformat(),
    'deleted_files': {
        'archived': deleted_files,
        'backups': backup_deleted,
        'tests': test_deleted
    },
    'summary': {
        'total_deleted': len(deleted_files) + len(backup_deleted) + len(test_deleted),
        'space_freed_mb': round(space_freed_mb, 2),
        'empty_dirs_removed': len(empty_dirs_removed),
        'errors': len(errors)
    },
    'backup_location': str(backup_dir),
    'errors': errors
}

results_path = Path('cortex-brain/documents/reports/phase2-deletion-results.json')
results_path.parent.mkdir(parents=True, exist_ok=True)

with open(results_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"[+] Results saved: {results_path}")
print()

# Print summary
print("=" * 80)
print("PHASE 2 SUMMARY")
print("=" * 80)
print()

print(f"Task 2.1: ✅ Deleted {len(deleted_files)} archived duplicates")
print(f"Task 2.2: ✅ Removed {len(backup_deleted)} backup files")
print(f"Task 2.3: ✅ Cleaned {len(test_deleted)} test duplicates")
print(f"Task 2.4: ⏳ Validation pending (run align)")
print()

print(f"TOTALS:")
print(f"  Files deleted: {len(deleted_files) + len(backup_deleted) + len(test_deleted)}")
print(f"  Space freed: {space_freed_mb:.2f} MB")
print(f"  Empty directories removed: {len(empty_dirs_removed)}")
print(f"  Errors: {len(errors)}")
print(f"  Backup location: {backup_dir}")
print()

if errors:
    print(f"ERRORS:")
    for error in errors[:10]:  # Show first 10 errors
        print(f"  - {error}")
    if len(errors) > 10:
        print(f"  ... and {len(errors) - 10} more (see {results_path})")
    print()

print(f"NEXT STEPS:")
print(f"  1. Review deletion results: {results_path}")
print(f"  2. Run validation: python -m src.main 'align'")
print(f"  3. If validation passes, execute Phase 3")
print(f"  4. ROLLBACK if needed: restore from {backup_dir}")
print()

print("=" * 80)
print(f"PHASE 2 COMPLETE - Run validation before Phase 3")
print("=" * 80)
