#!/usr/bin/env python3
"""
CORTEX Legacy Reference Remover - Remove deprecated 5-part template references

Removes all references to deprecated 5-part response templates:
- inherits_from: core/base-templates/5-part-standard.yaml
- 5-part-standard references
- Updates to use adaptive-base.yaml

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0.0
"""

import os
import sys
import re
import shutil
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime
import argparse


# Patterns to remove/replace
LEGACY_PATTERNS = [
    {
        "pattern": r"^\s*inherits_from:\s*core/base-templates/5-part-standard\.yaml\s*\n?",
        "replacement": "",
        "description": "inherits_from: 5-part-standard.yaml"
    },
    {
        "pattern": r"inherits_from:\s*['\"]?core/base-templates/5-part-standard\.yaml['\"]?",
        "replacement": "inherits_from: core/base-templates/adaptive-base.yaml",
        "description": "5-part-standard reference"
    },
]

# Files/directories to skip
SKIP_PATTERNS = [
    "user-response-template-cleanup",  # Planning docs about the cleanup
    "cortex-cleanup.prompt.md",         # This cleanup prompt
    ".git",
    "__pycache__",
    "node_modules",
    ".backup",
]


def should_skip(path: Path) -> bool:
    """Check if path should be skipped."""
    path_str = str(path)
    return any(skip in path_str for skip in SKIP_PATTERNS)


def find_legacy_files(workspace: Path) -> List[Dict]:
    """Find files containing legacy 5-part references."""
    findings = []
    
    search_dirs = [
        workspace / "cortex-brain",
        workspace / ".github",
        workspace / "src",
    ]
    
    extensions = [".yaml", ".yml", ".md"]
    
    combined_pattern = r"5-part-standard|five-part-standard|5_part_standard"
    
    for search_dir in search_dirs:
        if not search_dir.exists():
            continue
        
        for ext in extensions:
            for file in search_dir.rglob(f"*{ext}"):
                if should_skip(file):
                    continue
                
                try:
                    content = file.read_text()
                    matches = re.findall(combined_pattern, content, re.IGNORECASE)
                    
                    if matches:
                        findings.append({
                            "file": file,
                            "matches": matches,
                            "count": len(matches)
                        })
                except Exception as e:
                    print(f"   ⚠️  Error reading {file}: {e}")
    
    return findings


def create_backup(file: Path, backup_dir: Path) -> Path:
    """Create backup of file before modification."""
    relative = file.relative_to(file.parent.parent.parent)
    backup_path = backup_dir / relative
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(file, backup_path)
    return backup_path


def remove_legacy_references(
    workspace: Path,
    dry_run: bool = True,
    verbose: bool = False
) -> Tuple[int, int, List[str]]:
    """
    Remove legacy 5-part template references.
    
    Returns:
        Tuple of (files_modified, references_removed, errors)
    """
    files_modified = 0
    references_removed = 0
    errors = []
    
    print(f"\n{'=' * 60}")
    print("🗑️  CORTEX Legacy Reference Remover")
    print(f"{'=' * 60}")
    print(f"\n📂 Workspace: {workspace}")
    print(f"🔍 Mode: {'DRY RUN' if dry_run else 'EXECUTE'}")
    
    # Find files with legacy references
    print("\n📋 Scanning for legacy 5-part references...")
    findings = find_legacy_files(workspace)
    
    if not findings:
        print("\n✅ No legacy references found!")
        return 0, 0, []
    
    print(f"\n⚠️  Found {len(findings)} file(s) with legacy references:")
    
    for finding in findings:
        print(f"   📄 {finding['file'].relative_to(workspace)} ({finding['count']} match(es))")
    
    # Create backup directory
    if not dry_run:
        backup_dir = workspace / ".cleanup-backup" / datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir.mkdir(parents=True, exist_ok=True)
        print(f"\n📦 Backup directory: {backup_dir}")
    
    # Process files
    print(f"\n{'🔍 Would modify' if dry_run else '🔧 Modifying'} files...")
    
    for finding in findings:
        file = finding["file"]
        
        try:
            content = file.read_text()
            original_content = content
            
            # Apply all replacement patterns
            for pattern_config in LEGACY_PATTERNS:
                matches_before = len(re.findall(pattern_config["pattern"], content, re.MULTILINE))
                content = re.sub(
                    pattern_config["pattern"],
                    pattern_config["replacement"],
                    content,
                    flags=re.MULTILINE
                )
                matches_after = len(re.findall(pattern_config["pattern"], content, re.MULTILINE))
                references_removed += (matches_before - matches_after)
            
            if content != original_content:
                if not dry_run:
                    # Create backup
                    create_backup(file, backup_dir)
                    # Write modified content
                    file.write_text(content)
                
                files_modified += 1
                
                if verbose:
                    print(f"   ✅ {file.relative_to(workspace)}")
                    
        except Exception as e:
            errors.append(f"Error processing {file}: {e}")
    
    # Summary
    print(f"\n{'=' * 60}")
    print("📊 Summary")
    print(f"{'=' * 60}")
    
    if dry_run:
        print(f"\n   Would modify: {files_modified} file(s)")
        print(f"   Would remove: {references_removed} reference(s)")
        print("\n💡 Run with --execute to apply changes")
    else:
        print(f"\n   ✅ Modified: {files_modified} file(s)")
        print(f"   ✅ Removed: {references_removed} reference(s)")
        print(f"   📦 Backups in: {backup_dir}")
    
    if errors:
        print(f"\n   ⚠️  Errors: {len(errors)}")
        for err in errors:
            print(f"      - {err}")
    
    print(f"\n{'=' * 60}\n")
    
    return files_modified, references_removed, errors


def check_5part_file(workspace: Path) -> bool:
    """Check if 5-part-standard.yaml file exists and should be deleted."""
    file = workspace / "cortex-brain" / "response-templates" / "core" / "base-templates" / "5-part-standard.yaml"
    
    if file.exists():
        print(f"\n⚠️  Found deprecated file: {file.relative_to(workspace)}")
        
        # Check content - if it's just a stub/redirect, safe to delete
        content = file.read_text()
        if "adaptive" in content.lower() or "deprecated" in content.lower():
            print("   📝 File appears to be a redirect/stub")
        
        return True
    
    return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="CORTEX Legacy Reference Remover - Remove deprecated 5-part template references"
    )
    parser.add_argument(
        "--workspace",
        type=str,
        default=".",
        help="Workspace root directory (default: current)"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually make changes (default is dry-run)"
    )
    parser.add_argument(
        "--delete-file",
        action="store_true",
        help="Also delete the 5-part-standard.yaml file if it exists"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    workspace = Path(args.workspace).resolve()
    
    if not workspace.exists():
        print(f"❌ Workspace not found: {workspace}")
        sys.exit(1)
    
    # Remove references
    files_modified, refs_removed, errors = remove_legacy_references(
        workspace,
        dry_run=not args.execute,
        verbose=args.verbose
    )
    
    # Optionally delete the 5-part file
    if args.delete_file:
        file_exists = check_5part_file(workspace)
        if file_exists and args.execute:
            file = workspace / "cortex-brain" / "response-templates" / "core" / "base-templates" / "5-part-standard.yaml"
            file.unlink()
            print(f"   ✅ Deleted: {file.relative_to(workspace)}")
    
    sys.exit(0 if not errors else 1)


if __name__ == "__main__":
    main()
