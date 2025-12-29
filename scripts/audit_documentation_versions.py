#!/usr/bin/env python3
"""
Phase 14 Task 14.5: Documentation Version Reference Audit

Scans all documentation for v2/v3 references and generates migration report.

Author: Asif Hussain
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple
import json


def scan_file_for_version_refs(file_path: Path) -> List[Tuple[int, str, str]]:
    """
    Scan a file for version references.
    
    Returns: List of (line_number, line_content, version_found)
    """
    matches = []
    version_patterns = [
        (r'v2\.\d+', 'v2.x'),
        (r'v3\.\d+', 'v3.x'),
        (r'version\s+2', 'version 2'),
        (r'version\s+3', 'version 3'),
        (r'CORTEX\s+2', 'CORTEX 2'),
        (r'CORTEX\s+3', 'CORTEX 3'),
        (r'_v2[_\.]', '_v2'),
        (r'_v3[_\.]', '_v3'),
        (r'-v2[_\-\.]', '-v2'),
        (r'-v3[_\-\.]', '-v3'),
        (r'V2\.\d+', 'V2.x'),
        (r'V3\.\d+', 'V3.x'),
    ]
    
    try:
        content = file_path.read_text(encoding='utf-8')
        lines = content.splitlines()
        
        for line_num, line in enumerate(lines, 1):
            for pattern, version_type in version_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    matches.append((line_num, line.strip(), version_type))
                    break  # Only count once per line
    except Exception as e:
        print(f"  ⚠️  Error reading {file_path}: {e}")
    
    return matches


def audit_documentation():
    """Audit all documentation for version references"""
    
    print("\n" + "=" * 80)
    print("PHASE 14 - TASK 14.5: DOCUMENTATION VERSION AUDIT")
    print("=" * 80 + "\n")
    
    # Directories to scan
    scan_dirs = [
        "cortex-brain/documents",
        "docs",
        ".github/prompts",
        "README.md",
        "CHANGELOG.md"
    ]
    
    # Patterns to include/exclude
    include_patterns = ["*.md", "*.yaml", "*.yml", "*.txt"]
    exclude_dirs = ["archive", "backup", "node_modules", ".git", "htmlcov"]
    
    results = {
        "files_scanned": 0,
        "files_with_refs": 0,
        "total_refs": 0,
        "by_version": {"v2.x": 0, "v3.x": 0, "other": 0},
        "by_directory": {},
        "detailed_findings": []
    }
    
    print("🔍 Scanning documentation...")
    print("-" * 80)
    
    for scan_path in scan_dirs:
        path = Path(scan_path)
        if not path.exists():
            continue
        
        if path.is_file():
            files = [path]
        else:
            files = []
            for pattern in include_patterns:
                files.extend(path.rglob(pattern))
        
        for file_path in files:
            # Skip excluded directories
            if any(excluded in file_path.parts for excluded in exclude_dirs):
                continue
            
            results["files_scanned"] += 1
            
            matches = scan_file_for_version_refs(file_path)
            if matches:
                results["files_with_refs"] += 1
                results["total_refs"] += len(matches)
                
                # Categorize by version
                for _, _, version_type in matches:
                    if 'v2' in version_type.lower() or '2' in version_type:
                        results["by_version"]["v2.x"] += 1
                    elif 'v3' in version_type.lower() or '3' in version_type:
                        results["by_version"]["v3.x"] += 1
                    else:
                        results["by_version"]["other"] += 1
                
                # Categorize by directory
                dir_name = str(file_path.parent)
                if dir_name not in results["by_directory"]:
                    results["by_directory"][dir_name] = 0
                results["by_directory"][dir_name] += len(matches)
                
                # Store detailed finding
                results["detailed_findings"].append({
                    "file": str(file_path),
                    "refs_count": len(matches),
                    "lines": [{"line_num": ln, "content": content, "version": ver} 
                             for ln, content, ver in matches]
                })
                
                print(f"  📄 {file_path} - {len(matches)} refs")
    
    # Summary
    print("\n" + "=" * 80)
    print("AUDIT SUMMARY")
    print("=" * 80)
    
    print(f"\n📊 Statistics:")
    print(f"  • Files Scanned:      {results['files_scanned']:,}")
    print(f"  • Files with Refs:    {results['files_with_refs']:,}")
    print(f"  • Total References:   {results['total_refs']:,}")
    
    print(f"\n🔢 By Version:")
    print(f"  • v2.x references:    {results['by_version']['v2.x']:,}")
    print(f"  • v3.x references:    {results['by_version']['v3.x']:,}")
    print(f"  • Other references:   {results['by_version']['other']:,}")
    
    if results["by_directory"]:
        print(f"\n📁 Top Directories with References:")
        sorted_dirs = sorted(results["by_directory"].items(), 
                           key=lambda x: x[1], reverse=True)[:10]
        for dir_name, count in sorted_dirs:
            print(f"  • {dir_name:70} {count:3} refs")
    
    # Recommendations
    print("\n💡 Recommendations:")
    if results["total_refs"] == 0:
        print("  ✅ No version references found - documentation is clean!")
    else:
        print(f"  ⚠️  Found {results['total_refs']} version references")
        print("  📝 Review detailed_findings in JSON report for specific lines")
        print("  🔄 Consider updating references to v4.0 or removing version specifics")
    
    # Determine status
    if results["total_refs"] == 0:
        status = "CLEAN"
        print("\n🎉 STATUS: DOCUMENTATION IS VERSION-CLEAN")
    elif results["total_refs"] < 50:
        status = "MINOR_CLEANUP_NEEDED"
        print("\n✅ STATUS: MINOR CLEANUP NEEDED (< 50 references)")
    else:
        status = "MAJOR_CLEANUP_NEEDED"
        print("\n⚠️  STATUS: MAJOR CLEANUP NEEDED (≥ 50 references)")
    
    # Save report
    report_path = Path("cortex-brain/dashboards/phase-14-task-14.5-audit.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    results["status"] = status
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Detailed report saved: {report_path}")
    print("=" * 80 + "\n")
    
    return status == "CLEAN"


if __name__ == "__main__":
    import sys
    success = audit_documentation()
    sys.exit(0 if success else 1)
