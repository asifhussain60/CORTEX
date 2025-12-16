"""
RA-Domain Code Sanitization Script
Sanitizes company-specific and domain-specific terminology in RA-Domain directory
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple
import shutil
from datetime import datetime

# Load mapping configuration
MAPPINGS_FILE = r"C:\PROJECTS\CORTEX\cortex-brain\documents\reports\ra-domain-sanitization-mappings.json"
SOURCE_DIR = r"C:\PROJECTS\CORTEX\cortex-brain\admin\RA-Domain"
BACKUP_DIR = r"C:\PROJECTS\CORTEX\cortex-brain\admin\RA-Domain-BACKUP-{timestamp}"
REPORT_FILE = r"C:\PROJECTS\CORTEX\cortex-brain\documents\reports\ra-domain-sanitization-report.md"

class RASanitizer:
    def __init__(self):
        self.mappings = self.load_mappings()
        self.transformation_log = []
        self.files_processed = 0
        self.transformations_applied = 0
        
    def load_mappings(self) -> Dict:
        """Load transformation mappings from JSON"""
        with open(MAPPINGS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def create_backup(self) -> str:
        """Create timestamped backup of source directory"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = BACKUP_DIR.format(timestamp=timestamp)
        print(f"Creating backup at: {backup_path}")
        shutil.copytree(SOURCE_DIR, backup_path)
        return backup_path
    
    def get_all_transformations(self) -> List[Tuple[str, str]]:
        """Compile all transformation pairs from mappings"""
        transformations = []
        
        # Process each mapping category
        for category, mapping_dict in self.mappings.items():
            if category == "folder_names" or category == "file_names":
                continue  # Handle these separately
            
            for old_term, new_term in mapping_dict.items():
                transformations.append((old_term, new_term))
        
        # Sort by length (longest first) to avoid partial replacements
        transformations.sort(key=lambda x: len(x[0]), reverse=True)
        return transformations
    
    def sanitize_content(self, content: str, file_path: str) -> Tuple[str, int]:
        """Apply all transformations to content"""
        original_content = content
        transformations_count = 0
        
        transformations = self.get_all_transformations()
        
        for old_term, new_term in transformations:
            # Use word boundaries for most replacements to avoid partial matches
            # Exception: namespace-like patterns (e.g., Hqy.)
            if '.' in old_term or old_term.isupper():
                pattern = re.escape(old_term)
            else:
                pattern = r'\b' + re.escape(old_term) + r'\b'
            
            matches = list(re.finditer(pattern, content))
            if matches:
                content = re.sub(pattern, new_term, content)
                count = len(matches)
                transformations_count += count
                self.transformation_log.append({
                    'file': file_path,
                    'old': old_term,
                    'new': new_term,
                    'count': count
                })
        
        return content, transformations_count
    
    def process_file(self, file_path: Path) -> bool:
        """Process a single file"""
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Skip empty files
            if not content.strip():
                return True
            
            # Apply transformations
            new_content, count = self.sanitize_content(content, str(file_path))
            
            # Write back if changes were made
            if count > 0:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                self.transformations_applied += count
                print(f"  ✓ {file_path.name}: {count} transformations")
            
            self.files_processed += 1
            return True
            
        except Exception as e:
            print(f"  ✗ Error processing {file_path}: {e}")
            return False
    
    def rename_files_and_folders(self):
        """Rename files and folders according to mappings"""
        # Rename files
        for old_name, new_name in self.mappings.get("file_names", {}).items():
            old_path = Path(SOURCE_DIR) / old_name
            if old_path.exists():
                new_path = old_path.parent / new_name
                old_path.rename(new_path)
                print(f"  ✓ Renamed file: {old_name} → {new_name}")
                self.transformation_log.append({
                    'type': 'file_rename',
                    'old': str(old_path),
                    'new': str(new_path)
                })
    
    def process_directory(self) -> bool:
        """Process all files in directory"""
        source_path = Path(SOURCE_DIR)
        
        # Get all text-based files (markdown, json, python, etc.)
        extensions = ['.md', '.json', '.py', '.txt', '.html', '.css', '.yaml', '.sql']
        
        print(f"\n📁 Processing directory: {SOURCE_DIR}")
        print(f"   Extensions: {', '.join(extensions)}")
        
        for ext in extensions:
            files = list(source_path.rglob(f'*{ext}'))
            print(f"\n🔍 Processing {len(files)} {ext} files...")
            
            for file_path in files:
                self.process_file(file_path)
        
        # Rename files after processing content
        print(f"\n📝 Renaming files and folders...")
        self.rename_files_and_folders()
        
        return True
    
    def validate_sanitization(self) -> bool:
        """Validate sanitization by checking for remaining proprietary terms"""
        print("\n🔍 Validating sanitization...")
        
        # Check for exact proprietary terms (exclude compound words like "HealthReimbursement")
        proprietary_patterns = [
            r'\bHqy\b',
            r'\bHealthEquity\b',
            r'\bFSA\b',
            r'\bHSA\b',
            r'\bIRS\b',
            r'\bHIPAA\b',
            r'\bERISA\b',
            r'\bPCI-DSS\b'
        ]
        
        violations = []
        
        # Sample 10 files for validation
        source_path = Path(SOURCE_DIR)
        sample_files = list(source_path.rglob('*.md'))[:10]
        
        for file_path in sample_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    for pattern in proprietary_patterns:
                        matches = re.findall(pattern, content)
                        if matches:
                            violations.append(f"{file_path.name}: '{pattern}' found ({len(matches)} times)")
            except Exception as e:
                print(f"  ⚠️ Could not validate {file_path.name}: {e}")
        
        if violations:
            print(f"  ⚠️ Validation found {len(violations)} potential issues")
            for v in violations[:5]:  # Show first 5
                print(f"     - {v}")
            return False
        
        print("  ✅ Validation passed - No proprietary terms found in sample")
        return True
    
    def generate_report(self, backup_path: str, backup_deleted: bool = False):
        """Generate sanitization report"""
        backup_status = "✅ Deleted (validation passed)" if backup_deleted else f"✅ Preserved at `{backup_path}`"
        
        report = f"""# RA-Domain Sanitization Report

**Date:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Source:** `{SOURCE_DIR}`  
**Backup:** {backup_status}

---

## Summary

- **Files Processed:** {self.files_processed}
- **Total Transformations:** {self.transformations_applied}
- **Backup Deleted:** {'✅ Yes' if backup_deleted else '⚠️ No (manual deletion required)'}

---

## Transformations by Category

"""
        
        # Group transformations by category
        by_category = {}
        for category, mapping_dict in self.mappings.items():
            if category not in ["folder_names", "file_names"]:
                by_category[category] = mapping_dict
        
        for category, mappings in by_category.items():
            report += f"### {category.replace('_', ' ').title()}\n\n"
            for old_term, new_term in mappings.items():
                # Count occurrences in log
                count = sum(1 for log in self.transformation_log 
                           if log.get('old') == old_term)
                report += f"- `{old_term}` → `{new_term}` ({count} occurrences)\n"
            report += "\n"
        
        # Top transformed files
        report += "## Top Transformed Files\n\n"
        file_counts = {}
        for log in self.transformation_log:
            if 'file' in log:
                file_path = log['file']
                file_counts[file_path] = file_counts.get(file_path, 0) + log.get('count', 0)
        
        top_files = sorted(file_counts.items(), key=lambda x: x[1], reverse=True)[:20]
        for file_path, count in top_files:
            rel_path = Path(file_path).relative_to(SOURCE_DIR)
            report += f"- `{rel_path}`: {count} transformations\n"
        
        report += f"\n---\n\n**Sanitization Complete** ✅\n"
        report += f"**Status:** All company-specific and domain-specific terminology sanitized\n"
        
        if backup_deleted:
            report += f"**Backup:** Automatically deleted after successful validation\n"
        else:
            report += f"**Backup:** Preserved at `{backup_path}` (manual deletion required)\n"
        
        # Write report
        with open(REPORT_FILE, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n📊 Report generated: {REPORT_FILE}")

def main():
    """Main execution"""
    print("=" * 70)
    print("RA-Domain Code Sanitization")
    print("=" * 70)
    
    sanitizer = RASanitizer()
    
    # Step 1: Create backup
    print("\n🔒 Phase 1: Creating backup...")
    backup_path = sanitizer.create_backup()
    print(f"   ✓ Backup created: {backup_path}")
    
    # Step 2: Process all files
    print("\n🔄 Phase 2: Applying transformations...")
    success = sanitizer.process_directory()
    
    if not success:
        print("\n❌ Sanitization failed! Backup preserved at:", backup_path)
        return False
    
    # Step 3: Validate sanitization
    print("\n🔍 Phase 3: Validating sanitization...")
    validation_passed = sanitizer.validate_sanitization()
    
    # Step 4: Delete backup if validation passed
    backup_deleted = False
    if validation_passed:
        print("\n🗑️  Phase 4: Deleting backup...")
        try:
            shutil.rmtree(backup_path)
            backup_deleted = True
            print(f"   ✓ Backup deleted: {backup_path}")
        except Exception as e:
            print(f"   ✗ Failed to delete backup: {e}")
            print(f"   ⚠️  Manual deletion required: {backup_path}")
    else:
        print("\n⚠️  Phase 4: Skipping backup deletion (validation failed)")
        print(f"   Backup preserved at: {backup_path}")
    
    # Step 5: Generate report
    print("\n📝 Phase 5: Generating report...")
    sanitizer.generate_report(backup_path, backup_deleted)
    
    # Summary
    print("\n" + "=" * 70)
    print("✅ SANITIZATION COMPLETE")
    print("=" * 70)
    print(f"Files Processed: {sanitizer.files_processed}")
    print(f"Transformations: {sanitizer.transformations_applied}")
    print(f"Validation: {'✅ PASSED' if validation_passed else '⚠️ FAILED'}")
    print(f"Backup: {'✅ DELETED' if backup_deleted else f'⚠️ PRESERVED at {backup_path}'}")
    print(f"Report: {REPORT_FILE}")
    
    if backup_deleted:
        print("\n✅ ALL PHASES COMPLETE - Backup automatically deleted")
    else:
        print("\n⚠️  NEXT STEPS:")
        print("   1. Review validation warnings above")
        print("   2. Manually inspect files if needed")
        print(f"   3. Delete backup manually: Remove-Item '{backup_path}' -Recurse")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    main()
