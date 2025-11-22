"""
Scan CORTEX repository for unnecessary documentation, summary, review files.
Outputs categorized list for cleanup.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import os
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import json

# File patterns to scan for
PATTERNS = {
    'summary': ['*-SUMMARY.md', '*SUMMARY*.md'],
    'status': ['*-STATUS.md', '*STATUS*.md'],
    'report': ['*-REPORT.md', '*REPORT*.md'],
    'analysis': ['*-ANALYSIS.md', '*ANALYSIS*.md'],
    'review': ['*-REVIEW.md', '*REVIEW*.md'],
    'complete': ['*-COMPLETE.md', '*COMPLETE*.md', '*COMPLETION*.md'],
    'investigation': ['*INVESTIGATION*.md'],
    'progress': ['*-PROGRESS*.md', '*PROGRESS*.md'],
    'notes': ['*-NOTES.md', '*NOTES*.md'],
    'guide': ['*-GUIDE.md', '*GUIDE*.md'],
    'temp': ['temp-*.md', 'temp_*.md', 'TEMP*.md'],
    'direct': ['DIRECT-*.md'],
    'fix': ['*-FIX-*.md', '*FIX*.md'],
    'restoration': ['*RESTORATION*.md'],
    'enhancement': ['*ENHANCEMENT*.md'],
    'integration': ['*-INTEGRATION-GUIDE.md', '*INTEGRATION*.md'],
    'ambient': ['*AMBIENT*.md'],
    'resolution': ['*RESOLUTION*.md'],
    'quick': ['QUICK-*.md'],
    'session': ['*-SESSION*.md', '*SESSION*.md'],
}

# Directories to exclude
EXCLUDE_DIRS = {
    'node_modules', '.git', '.venv', 'site', 'archives',
    '.backup-archive', 'dist', 'build', '__pycache__'
}

# Protected files (never delete)
PROTECTED_FILES = {
    'README.md', 'CHANGELOG.md', 'LICENSE.md', 'LICENSE',
    'PHASE-3-COMMIT-GUIDE.md', 'PHASE-3-SUMMARY.md',
    'PHASE-3-VISUAL-SUMMARY.md', 'PHASE-4-PRODUCTION-READY.md',
    'GIT-SYNC-COMPLETE.md'
}


def should_exclude(path: Path, project_root: Path) -> bool:
    """Check if path should be excluded from scan."""
    # Check if in excluded directory
    try:
        rel_path = path.relative_to(project_root)
        for part in rel_path.parts:
            if part in EXCLUDE_DIRS:
                return True
    except ValueError:
        return True
    
    # Check if protected
    if path.name in PROTECTED_FILES:
        return True
    
    # Keep cortex-brain/documents/* (organized structure)
    if 'cortex-brain\\documents\\' in str(path):
        return True
    
    return False


def scan_repository(project_root: Path) -> dict:
    """Scan repository for unnecessary files."""
    results = defaultdict(list)
    
    for category, patterns in PATTERNS.items():
        for pattern in patterns:
            for file_path in project_root.rglob(pattern):
                if file_path.is_file() and not should_exclude(file_path, project_root):
                    try:
                        size = file_path.stat().st_size
                        mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                        rel_path = file_path.relative_to(project_root)
                        
                        results[category].append({
                            'path': str(rel_path),
                            'full_path': str(file_path),
                            'size': size,
                            'size_kb': round(size / 1024, 2),
                            'modified': mtime.isoformat(),
                            'name': file_path.name
                        })
                    except Exception as e:
                        print(f"Error scanning {file_path}: {e}")
    
    return dict(results)


def generate_report(results: dict, project_root: Path):
    """Generate detailed report."""
    print("\n" + "="*80)
    print("🧠 CORTEX UNNECESSARY FILES SCAN")
    print("="*80)
    
    total_files = sum(len(files) for files in results.values())
    total_size = sum(f['size'] for files in results.values() for f in files)
    total_mb = total_size / (1024 * 1024)
    
    print(f"\n📊 Summary:")
    print(f"   Total files found: {total_files}")
    print(f"   Total size: {total_mb:.2f} MB")
    print(f"   Categories: {len(results)}")
    
    print("\n📁 By Category:")
    for category, files in sorted(results.items(), key=lambda x: len(x[1]), reverse=True):
        if files:
            cat_size = sum(f['size'] for f in files)
            cat_mb = cat_size / (1024 * 1024)
            print(f"\n   {category.upper()}: {len(files)} files ({cat_mb:.2f} MB)")
            
            # Show first 5 files in each category
            for f in files[:5]:
                print(f"     • {f['path']} ({f['size_kb']} KB)")
            
            if len(files) > 5:
                print(f"     ... and {len(files) - 5} more")
    
    # Save detailed JSON report
    report_path = project_root / 'cortex-brain' / 'cleanup-reports' / f'unnecessary-files-{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    report_data = {
        'timestamp': datetime.now().isoformat(),
        'total_files': total_files,
        'total_size_bytes': total_size,
        'total_size_mb': round(total_mb, 2),
        'categories': {cat: len(files) for cat, files in results.items()},
        'files': results
    }
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2)
    
    print(f"\n💾 Detailed report saved: {report_path.relative_to(project_root)}")
    
    return report_path


def main():
    """Main entry point."""
    project_root = Path(__file__).parent.parent
    
    print(f"🔍 Scanning: {project_root}")
    print(f"⏳ This may take a moment...\n")
    
    results = scan_repository(project_root)
    report_path = generate_report(results, project_root)
    
    print("\n" + "="*80)
    print("✅ Scan complete!")
    print("="*80)
    
    return results, report_path


if __name__ == '__main__':
    main()
