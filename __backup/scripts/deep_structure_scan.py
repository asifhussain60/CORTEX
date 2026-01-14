"""
Deep Structure Scan for CORTEX Repository.

Performs comprehensive recursive scan to identify:
- Root-level files that should be organized
- Misplaced files in wrong directories
- Empty directories
- Duplicate files across different locations
- Files with improper naming conventions

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Tuple, Set
from collections import defaultdict
from datetime import datetime
import hashlib


class DeepStructureScanner:
    """Comprehensive repository structure scanner."""
    
    # Proper CORTEX structure rules
    ALLOWED_ROOT_FILES = {
        '.gitignore', '.gitattributes', '.pre-commit-config.yaml',
        'LICENSE', 'README.md', 'requirements.txt', 'pytest.ini',
        'mypy.ini', '.flake8', '.coverage', '.env',
        '.cortex-initialized', '.cortex-installed', '.cortexignore'
    }
    
    ALLOWED_ROOT_DIRS = {
        '.git', '.github', '.venv', '.vscode', '.pytest_cache',
        'src', 'tests', 'scripts', 'docs', 'templates',
        'cortex-brain', 'cortex-sample-apps', 'cortex-toolkit',
        'build', 'logs', 'htmlcov', 'extensions', '.asif'
    }
    
    # Files that should be relocated
    RELOCATE_PATTERNS = {
        '.ps1': 'scripts/',
        '.sh': 'scripts/',
        '.py': 'scripts/',  # Root-level Python scripts only
        '.md': 'docs/',  # Root-level docs only
        'cortex-*.ps1': 'scripts/',
        'cortex-*.sh': 'scripts/',
        '*-plan.py': 'scripts/',
        '*.config.json': 'cortex-brain/config/',
        '*.yaml': 'cortex-brain/config/',  # Root-level config only
        'deployment-manifest.json': 'cortex-brain/config/',
    }
    
    def __init__(self, root_path: Path):
        """Initialize scanner."""
        self.root = Path(root_path)
        self.issues = defaultdict(list)
        self.stats = {
            'total_files': 0,
            'total_dirs': 0,
            'root_files': 0,
            'misplaced': 0,
            'empty_dirs': 0,
            'duplicates': 0
        }
    
    def scan(self) -> Dict:
        """Perform comprehensive scan."""
        print("🔍 Starting deep structure scan...")
        
        # Scan root directory
        self._scan_root()
        
        # Recursive scan
        self._scan_recursive()
        
        # Find empty directories
        self._find_empty_dirs()
        
        # Find duplicates (by content hash)
        self._find_duplicates()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'statistics': self.stats,
            'issues': dict(self.issues)
        }
    
    def _scan_root(self):
        """Scan root directory for misplaced files."""
        print("  📁 Scanning root directory...")
        
        for item in self.root.iterdir():
            if item.is_file():
                self.stats['root_files'] += 1
                
                # Check if file should be at root
                if item.name not in self.ALLOWED_ROOT_FILES:
                    # Check for patterns that should be relocated
                    suggested = self._suggest_location(item)
                    if suggested:
                        self.issues['root_misplaced'].append({
                            'file': str(item.relative_to(self.root)),
                            'suggested': suggested,
                            'reason': 'Root-level file should be organized'
                        })
                        self.stats['misplaced'] += 1
    
    def _suggest_location(self, filepath: Path) -> str:
        """Suggest proper location for file."""
        name = filepath.name
        suffix = filepath.suffix
        
        # Check specific patterns
        if name.startswith('cortex-') and suffix in ['.ps1', '.sh']:
            return f'scripts/{name}'
        
        if name.startswith('cortex-') and suffix == '.py':
            return f'scripts/{name}'
        
        if name.endswith('-plan.py'):
            return f'scripts/{name}'
        
        if name == 'deployment-manifest.json':
            return f'cortex-brain/config/{name}'
        
        if suffix in ['.md'] and name not in ['README.md', 'LICENSE']:
            return f'docs/{name}'
        
        if suffix == '.json' and 'config' in name.lower():
            return f'cortex-brain/config/{name}'
        
        if suffix == '.yaml' and name not in self.ALLOWED_ROOT_FILES:
            return f'cortex-brain/config/{name}'
        
        return None
    
    def _scan_recursive(self, max_depth: int = 10):
        """Recursive scan of directory structure."""
        print("  🔄 Scanning directory tree...")
        
        # Track directories by depth
        dirs_by_depth = defaultdict(list)
        
        for root, dirs, files in os.walk(self.root):
            root_path = Path(root)
            depth = len(root_path.relative_to(self.root).parts)
            
            # Skip excluded directories
            dirs[:] = [d for d in dirs if not self._should_skip(root_path / d)]
            
            if depth > max_depth:
                continue
            
            # Count files and directories
            self.stats['total_files'] += len(files)
            self.stats['total_dirs'] += len(dirs)
            
            # Check for suspicious directory names
            for dir_name in dirs:
                dir_path = root_path / dir_name
                rel_path = dir_path.relative_to(self.root)
                
                # Check for directories that shouldn't exist
                if dir_name in ['.backups', 'backup', 'backups'] and 'archives' not in str(rel_path):
                    self.issues['misplaced_dirs'].append({
                        'directory': str(rel_path),
                        'suggested': f'cortex-brain/archives/backups/{dir_name}',
                        'reason': 'Backup directory outside archives'
                    })
                
                # Check for temp directories
                if dir_name in ['temp', 'tmp', '.cache'] and depth < 3:
                    self.issues['temp_dirs'].append({
                        'directory': str(rel_path),
                        'reason': 'Temporary directory at shallow depth'
                    })
            
            # Check files in this directory
            for filename in files:
                file_path = root_path / filename
                rel_path = file_path.relative_to(self.root)
                
                # Check for backup files outside archives
                if any(x in filename.lower() for x in ['.bak', '.backup', 'backup-']):
                    if 'archives' not in str(rel_path):
                        self.issues['misplaced_backups'].append({
                            'file': str(rel_path),
                            'suggested': f'cortex-brain/archives/backups/{filename}',
                            'reason': 'Backup file outside archives'
                        })
                        self.stats['misplaced'] += 1
                
                # Check for reports outside reports directory
                if 'report' in filename.lower() and filename.endswith('.md'):
                    if 'cortex-brain/documents/reports' not in str(rel_path):
                        self.issues['misplaced_reports'].append({
                            'file': str(rel_path),
                            'suggested': f'cortex-brain/documents/reports/{filename}',
                            'reason': 'Report file outside reports directory'
                        })
    
    def _should_skip(self, path: Path) -> bool:
        """Check if directory should be skipped."""
        skip_patterns = [
            '.git', '.venv', '__pycache__', 'node_modules',
            '.pytest_cache', '.mypy_cache', 'htmlcov',
            '.eggs', '.tox', 'build', 'dist'
        ]
        
        return any(pattern in str(path) for pattern in skip_patterns)
    
    def _find_empty_dirs(self):
        """Find empty directories."""
        print("  📭 Finding empty directories...")
        
        for root, dirs, files in os.walk(self.root):
            root_path = Path(root)
            
            if self._should_skip(root_path):
                continue
            
            if not dirs and not files:
                rel_path = root_path.relative_to(self.root)
                self.issues['empty_dirs'].append({
                    'directory': str(rel_path),
                    'reason': 'Empty directory'
                })
                self.stats['empty_dirs'] += 1
    
    def _find_duplicates(self):
        """Find duplicate files by content hash."""
        print("  🔍 Finding duplicate files...")
        
        hashes = defaultdict(list)
        
        for root, dirs, files in os.walk(self.root):
            root_path = Path(root)
            
            if self._should_skip(root_path):
                continue
            
            for filename in files:
                file_path = root_path / filename
                
                # Skip large files
                if file_path.stat().st_size > 10 * 1024 * 1024:  # 10MB
                    continue
                
                try:
                    # Calculate hash
                    with open(file_path, 'rb') as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()
                    
                    hashes[file_hash].append(str(file_path.relative_to(self.root)))
                
                except Exception:
                    continue
        
        # Report duplicates
        for file_hash, paths in hashes.items():
            if len(paths) > 1:
                self.issues['duplicates'].append({
                    'hash': file_hash,
                    'files': paths,
                    'count': len(paths)
                })
                self.stats['duplicates'] += len(paths) - 1
    
    def generate_report(self, results: Dict) -> str:
        """Generate markdown report."""
        lines = []
        
        lines.append("# 🔍 CORTEX Deep Structure Scan Report")
        lines.append(f"\n**Generated:** {results['timestamp']}")
        lines.append(f"**Scanner:** Deep Structure Scanner v1.0")
        lines.append("\n---\n")
        
        # Statistics
        lines.append("## 📊 Statistics\n")
        for key, value in results['statistics'].items():
            lines.append(f"- **{key.replace('_', ' ').title()}:** {value}")
        
        # Issues by category
        issues = results['issues']
        
        # Root misplaced files
        if 'root_misplaced' in issues and issues['root_misplaced']:
            lines.append(f"\n## 🚨 Root-Level Files to Relocate ({len(issues['root_misplaced'])})\n")
            for item in issues['root_misplaced']:
                lines.append(f"- `{item['file']}`")
                lines.append(f"  → `{item['suggested']}`")
                lines.append(f"  *{item['reason']}*\n")
        
        # Misplaced directories
        if 'misplaced_dirs' in issues and issues['misplaced_dirs']:
            lines.append(f"\n## 📁 Misplaced Directories ({len(issues['misplaced_dirs'])})\n")
            for item in issues['misplaced_dirs']:
                lines.append(f"- `{item['directory']}`")
                lines.append(f"  → `{item['suggested']}`")
                lines.append(f"  *{item['reason']}*\n")
        
        # Misplaced backups
        if 'misplaced_backups' in issues and issues['misplaced_backups']:
            lines.append(f"\n## 💾 Misplaced Backup Files ({len(issues['misplaced_backups'])})\n")
            for item in issues['misplaced_backups'][:20]:  # Limit display
                lines.append(f"- `{item['file']}` → `{item['suggested']}`")
            if len(issues['misplaced_backups']) > 20:
                lines.append(f"\n... and {len(issues['misplaced_backups']) - 20} more")
        
        # Empty directories
        if 'empty_dirs' in issues and issues['empty_dirs']:
            lines.append(f"\n## 📭 Empty Directories ({len(issues['empty_dirs'])})\n")
            for item in issues['empty_dirs'][:30]:
                lines.append(f"- `{item['directory']}`")
            if len(issues['empty_dirs']) > 30:
                lines.append(f"\n... and {len(issues['empty_dirs']) - 30} more")
        
        # Duplicates
        if 'duplicates' in issues and issues['duplicates']:
            lines.append(f"\n## 🔄 Duplicate Files ({len(issues['duplicates'])} sets)\n")
            for dup in issues['duplicates'][:10]:
                lines.append(f"\n### Duplicate Set ({dup['count']} files)")
                for filepath in dup['files']:
                    lines.append(f"- `{filepath}`")
            if len(issues['duplicates']) > 10:
                lines.append(f"\n... and {len(issues['duplicates']) - 10} more duplicate sets")
        
        return '\n'.join(lines)


def main():
    """Main entry point."""
    print("=" * 70)
    print("🔍 CORTEX DEEP STRUCTURE SCAN")
    print("=" * 70)
    
    # Initialize scanner
    scanner = DeepStructureScanner(Path('.'))
    
    # Perform scan
    results = scanner.scan()
    
    # Generate report
    report_md = scanner.generate_report(results)
    
    # Save reports
    report_dir = Path('cortex-brain/cleanup-reports')
    report_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save JSON
    json_path = report_dir / f'deep-structure-scan-{timestamp}.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print(f"\n✅ JSON report: {json_path}")
    
    # Save Markdown
    md_path = report_dir / f'deep-structure-scan-{timestamp}.md'
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(report_md)
    print(f"✅ Markdown report: {md_path}")
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 SCAN SUMMARY")
    print("=" * 70)
    for key, value in results['statistics'].items():
        print(f"  {key.replace('_', ' ').title()}: {value}")
    print("=" * 70)


if __name__ == "__main__":
    main()
