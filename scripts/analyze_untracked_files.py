"""
Intelligent Untracked Files Analyzer for CORTEX Vacuum Orchestrator.

This script analyzes all untracked files and categorizes them into:
- DELETE: Temporary, cache, obsolete files
- RELOCATE: Misplaced files that should be in proper folders
- PRESERVE: Active code, documentation, configuration

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import subprocess
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict
from datetime import datetime


class GitStatusParser:
    """Parse git status output and extract file information."""
    
    @staticmethod
    def parse() -> Tuple[List[str], List[str], List[str]]:
        """
        Parse git status and return categorized files.
        
        Returns:
            Tuple of (deleted_files, modified_files, untracked_files)
        """
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True
        )
        
        deleted = []
        modified = []
        untracked = []
        
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
            
            status = line[:2]
            filepath = line[3:]
            
            if status.strip() == 'D':
                deleted.append(filepath)
            elif status.strip() == 'M':
                modified.append(filepath)
            elif status.strip() == '??':
                untracked.append(filepath)
        
        return deleted, modified, untracked


class FileTypeClassifier:
    """Classify files by type and purpose."""
    
    # File categories with patterns
    CATEGORIES = {
        'temp_cache': {
            'patterns': [
                '.pyc', '.pyo', '__pycache__', '.cache', 
                '.tmp', '.temp', '.swp', '.swo', '.DS_Store',
                'thumbs.db', '.backup', '.bak', '~'
            ],
            'action': 'DELETE'
        },
        'build_artifacts': {
            'patterns': [
                'dist/', 'build/', 'bin/', 'obj/', 'out/',
                '*.egg-info/', '.eggs/', '.tox/',
                'htmlcov/', '.coverage', 'coverage.json',
                '.pytest_cache/', '.mypy_cache/'
            ],
            'action': 'DELETE'
        },
        'logs': {
            'patterns': [
                '.log', 'logs/', '*.jsonl'
            ],
            'action': 'DELETE'  # Old logs, preserve recent if needed
        },
        'backups': {
            'patterns': [
                'backups/', '.backups/', 'backup-', '-backup',
                '.backup-', 'auto-backup-'
            ],
            'action': 'RELOCATE'  # Move to cortex-brain/archives/backups/
        },
        'config': {
            'patterns': [
                '.yaml', '.yml', '.json', '.toml', '.ini',
                '.config', '.conf', '.env', '.template'
            ],
            'action': 'PRESERVE'
        },
        'documentation': {
            'patterns': [
                '.md', '.txt', '.rst', '.pdf',
                'README', 'CHANGELOG', 'LICENSE',
                'docs/', 'documentation/'
            ],
            'action': 'PRESERVE'
        },
        'source_code': {
            'patterns': [
                '.py', '.js', '.ts', '.jsx', '.tsx',
                '.java', '.cpp', '.c', '.h', '.cs',
                '.go', '.rs', '.rb', '.php'
            ],
            'action': 'PRESERVE'
        },
        'web_assets': {
            'patterns': [
                '.html', '.css', '.scss', '.sass',
                '.jpg', '.jpeg', '.png', '.gif', '.svg',
                '.woff', '.woff2', '.ttf', '.eot'
            ],
            'action': 'PRESERVE'
        },
        'data_files': {
            'patterns': [
                '.csv', '.xml', '.sql', '.db', '.sqlite',
                '.parquet', '.arrow'
            ],
            'action': 'PRESERVE'
        },
        'scripts': {
            'patterns': [
                '.sh', '.bash', '.ps1', '.bat', '.cmd'
            ],
            'action': 'PRESERVE'
        }
    }
    
    @staticmethod
    def classify(filepath: str) -> Tuple[str, str]:
        """
        Classify file by type and recommended action.
        
        Returns:
            Tuple of (category, action)
        """
        filepath_lower = filepath.lower()
        path = Path(filepath)
        
        for category, info in FileTypeClassifier.CATEGORIES.items():
            for pattern in info['patterns']:
                if pattern in filepath_lower or filepath_lower.endswith(pattern):
                    return category, info['action']
        
        return 'unknown', 'REVIEW'


class FolderStructureAnalyzer:
    """Analyze folder structure and suggest reorganization."""
    
    # Proper CORTEX folder structure
    PROPER_STRUCTURE = {
        'cortex-brain/documents/': [
            'reports/', 'analysis/', 'summaries/', 'investigations/',
            'planning/', 'implementation-guides/', 'architecture/',
            'governance/', 'reviews/', 'standards/', 'updates/'
        ],
        'cortex-brain/config/': [
            'schemas/', 'templates/'
        ],
        'cortex-brain/archives/': [
            'backups/', 'deprecated/', 'obsolete/'
        ],
        'cortex-brain/tier0/': ['governance/', 'policies/'],
        'cortex-brain/tier1/': ['conversation-context/', 'session-state/'],
        'cortex-brain/tier2/': ['knowledge-graph/', 'schemas/'],
        'cortex-brain/tier3/': ['development/', 'testing/']
    }
    
    @staticmethod
    def suggest_relocation(filepath: str) -> str:
        """
        Suggest proper location for misplaced file.
        
        Returns:
            Suggested destination path
        """
        path = Path(filepath)
        
        # Check if file is in root (should be relocated)
        if len(path.parts) == 1:
            if path.suffix in ['.md', '.txt']:
                return f'cortex-brain/documents/summaries/{path.name}'
            elif path.suffix in ['.yaml', '.yml', '.json']:
                return f'cortex-brain/config/{path.name}'
            elif path.suffix in ['.py']:
                return f'src/{path.name}'
            elif path.suffix in ['.sh', '.ps1']:
                return f'scripts/{path.name}'
        
        # Check if backup files are in wrong location
        if 'backup' in filepath.lower() and not filepath.startswith('cortex-brain/archives/'):
            return f'cortex-brain/archives/backups/{path.name}'
        
        # Check if reports are in wrong subfolder
        if 'report' in filepath.lower() and path.suffix == '.md':
            if not filepath.startswith('cortex-brain/documents/reports/'):
                return f'cortex-brain/documents/reports/{path.name}'
        
        return filepath  # No relocation needed


class DependencyDetector:
    """Detect file dependencies and relationships."""
    
    @staticmethod
    def is_referenced(filepath: str, all_files: List[str]) -> bool:
        """
        Check if file is referenced in other files.
        
        Returns:
            True if file is referenced elsewhere
        """
        # For now, simple check - can be enhanced with AST parsing
        filename = Path(filepath).name
        
        # Check if Python module is imported
        if filepath.endswith('.py'):
            module_name = filename[:-3]
            # Search for imports in other Python files
            # This is simplified - full implementation would use grep/ag
            return True  # Assume referenced for safety
        
        return False
    
    @staticmethod
    def find_orphans(untracked_files: List[str]) -> List[str]:
        """
        Find orphaned files (no references, not used).
        
        Returns:
            List of orphaned file paths
        """
        orphans = []
        
        for filepath in untracked_files:
            # Skip directories
            if filepath.endswith('/'):
                continue
            
            # Check if file is truly orphaned
            path = Path(filepath)
            
            # Temp files are always orphans
            if any(x in filepath for x in ['.pyc', '.cache', '.tmp', '.swp']):
                orphans.append(filepath)
            
            # Old backups (check timestamp in name)
            if 'backup' in filepath.lower():
                # Extract date from filename if present
                # Simplified check
                orphans.append(filepath)
        
        return orphans


class OrganizationIntelligence:
    """Main intelligence engine for file organization."""
    
    def __init__(self):
        self.parser = GitStatusParser()
        self.classifier = FileTypeClassifier()
        self.folder_analyzer = FolderStructureAnalyzer()
        self.dependency_detector = DependencyDetector()
    
    def analyze(self) -> Dict[str, any]:
        """
        Perform comprehensive analysis of untracked files.
        
        Returns:
            Analysis report dictionary
        """
        # Parse git status
        deleted, modified, untracked = self.parser.parse()
        
        # Categorize untracked files
        categorized = defaultdict(list)
        actions = defaultdict(list)
        
        for filepath in untracked:
            category, action = self.classifier.classify(filepath)
            categorized[category].append(filepath)
            actions[action].append(filepath)
        
        # Find orphaned files
        orphans = self.dependency_detector.find_orphans(untracked)
        
        # Suggest relocations
        relocations = {}
        for filepath in actions.get('RELOCATE', []):
            new_location = self.folder_analyzer.suggest_relocation(filepath)
            if new_location != filepath:
                relocations[filepath] = new_location
        
        # Generate statistics
        stats = {
            'total_untracked': len(untracked),
            'total_deleted': len(deleted),
            'total_modified': len(modified),
            'by_category': {k: len(v) for k, v in categorized.items()},
            'by_action': {k: len(v) for k, v in actions.items()},
            'orphans': len(orphans),
            'relocations': len(relocations)
        }
        
        # Build report
        report = {
            'timestamp': datetime.now().isoformat(),
            'statistics': stats,
            'deleted_files': deleted,
            'modified_files': modified,
            'untracked_files': untracked,
            'categorized': dict(categorized),
            'actions': dict(actions),
            'orphans': orphans,
            'relocations': relocations
        }
        
        return report
    
    def generate_markdown_report(self, report: Dict) -> str:
        """Generate human-readable markdown report."""
        md = []
        
        md.append("# 🧹 CORTEX Untracked Files Analysis Report")
        md.append(f"\n**Generated:** {report['timestamp']}")
        md.append(f"\n**Analyzer:** Organization Intelligence v1.0")
        md.append("\n---\n")
        
        # Statistics
        md.append("## 📊 Statistics\n")
        stats = report['statistics']
        md.append(f"- **Total Untracked:** {stats['total_untracked']}")
        md.append(f"- **Total Deleted:** {stats['total_deleted']}")
        md.append(f"- **Total Modified:** {stats['total_modified']}")
        md.append(f"- **Orphaned Files:** {stats['orphans']}")
        md.append(f"- **Relocations Needed:** {stats['relocations']}\n")
        
        # By Category
        md.append("## 📁 Files by Category\n")
        for category, count in stats['by_category'].items():
            md.append(f"- **{category}:** {count} files")
        
        # By Action
        md.append("\n## 🎯 Recommended Actions\n")
        for action, count in stats['by_action'].items():
            md.append(f"- **{action}:** {count} files")
        
        # DELETE recommendations
        if 'DELETE' in report['actions']:
            md.append("\n## 🗑️ Files to DELETE\n")
            md.append(f"**Total:** {len(report['actions']['DELETE'])} files\n")
            for filepath in sorted(report['actions']['DELETE'])[:50]:  # Limit display
                md.append(f"- `{filepath}`")
            if len(report['actions']['DELETE']) > 50:
                md.append(f"\n... and {len(report['actions']['DELETE']) - 50} more files")
        
        # RELOCATE recommendations
        if report['relocations']:
            md.append("\n## 📦 Files to RELOCATE\n")
            md.append(f"**Total:** {len(report['relocations'])} files\n")
            for old_path, new_path in list(report['relocations'].items())[:30]:
                md.append(f"- `{old_path}` → `{new_path}`")
            if len(report['relocations']) > 30:
                md.append(f"\n... and {len(report['relocations']) - 30} more relocations")
        
        # PRESERVE (important files)
        if 'PRESERVE' in report['actions']:
            md.append("\n## ✅ Files to PRESERVE\n")
            md.append(f"**Total:** {len(report['actions']['PRESERVE'])} files\n")
            preserve_by_type = defaultdict(list)
            for filepath in report['actions']['PRESERVE']:
                ext = Path(filepath).suffix or 'no_ext'
                preserve_by_type[ext].append(filepath)
            
            for ext, files in sorted(preserve_by_type.items()):
                md.append(f"\n### {ext} ({len(files)} files)")
                for filepath in sorted(files)[:10]:
                    md.append(f"- `{filepath}`")
                if len(files) > 10:
                    md.append(f"  ... and {len(files) - 10} more")
        
        # Orphaned files
        if report['orphans']:
            md.append("\n## 🔍 Orphaned Files (No References)\n")
            md.append(f"**Total:** {len(report['orphans'])} files\n")
            for filepath in sorted(report['orphans'])[:30]:
                md.append(f"- `{filepath}`")
            if len(report['orphans']) > 30:
                md.append(f"\n... and {len(report['orphans']) - 30} more orphans")
        
        md.append("\n---\n")
        md.append("## 🎯 Next Steps\n")
        md.append("1. Review DELETE recommendations (automated cleanup safe)")
        md.append("2. Verify RELOCATE suggestions (folder structure optimization)")
        md.append("3. Confirm PRESERVE files are in correct locations")
        md.append("4. Execute vacuum orchestrator with approved actions")
        
        return '\n'.join(md)


def main():
    """Main entry point."""
    print("🧹 CORTEX Untracked Files Analysis")
    print("=" * 60)
    
    # Initialize intelligence engine
    intelligence = OrganizationIntelligence()
    
    # Perform analysis
    print("📊 Analyzing files...")
    report = intelligence.analyze()
    
    # Generate reports
    markdown_report = intelligence.generate_markdown_report(report)
    
    # Save JSON report
    json_path = Path("cortex-brain/cleanup-reports/untracked-files-analysis.json")
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(json_path, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"✅ JSON report saved: {json_path}")
    
    # Save markdown report
    md_path = Path("cortex-brain/cleanup-reports/untracked-files-analysis.md")
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(markdown_report)
    print(f"✅ Markdown report saved: {md_path}")
    
    # Display summary
    print("\n📊 Analysis Summary:")
    print(f"  Total Untracked: {report['statistics']['total_untracked']}")
    print(f"  To Delete: {report['statistics']['by_action'].get('DELETE', 0)}")
    print(f"  To Relocate: {report['statistics']['relocations']}")
    print(f"  To Preserve: {report['statistics']['by_action'].get('PRESERVE', 0)}")
    print(f"  Orphaned: {report['statistics']['orphans']}")
    
    print(f"\n✅ Analysis complete! Review reports in cortex-brain/cleanup-reports/")


if __name__ == "__main__":
    main()
