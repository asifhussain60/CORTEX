#!/usr/bin/env python3
"""
CORTEX 3.0 Legacy Cleanup Script

Systematically removes all 3.0 legacy code that has been superseded by 4.0 implementations.
Part of migration activation enforcement system.

Usage:
    python scripts/cleanup_legacy_3_0.py --scan
    python scripts/cleanup_legacy_3_0.py --delete --confirm
    python scripts/cleanup_legacy_3_0.py --report

Features:
    - Identifies cortex_3_0/ directory and contents
    - Finds legacy template_selector.py references
    - Removes superseded 3.0 orchestrators
    - Cleans up obsolete documents
    - Generates cleanup report
"""

import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# Colors for terminal output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'


class LegacyCleanup:
    """Cleans up CORTEX 3.0 legacy files superseded by 4.0"""
    
    def __init__(self, repo_root: Path, dry_run: bool = True):
        self.repo_root = repo_root
        self.dry_run = dry_run
        self.legacy_items: List[Dict] = []
        self.deleted_items: List[Dict] = []
        self.errors: List[str] = []
        
    def scan(self) -> List[Dict]:
        """Scan for legacy 3.0 files"""
        print(f"\n{Colors.BLUE}{'='*80}{Colors.END}")
        print(f"{Colors.BLUE}🔍 Scanning for CORTEX 3.0 Legacy Files{Colors.END}")
        print(f"{Colors.BLUE}{'='*80}{Colors.END}\n")
        
        # Define legacy items to remove
        legacy_patterns = [
            # Core 3.0 directory - fully superseded by 4.0
            {
                'path': 'src/cortex_3_0/',
                'type': 'directory',
                'reason': 'Superseded by orchestration_4_0 and brain/ architecture',
                'superseded_by': 'src/orchestration_4_0/, src/brain/',
                'size_saved': '~5KB',
                'priority': 'HIGH'
            },
            
            # Legacy template selector with v3.0 compatibility
            {
                'path': 'src/utils/template_selector.py',
                'type': 'file',
                'reason': 'Has legacy_mode() compatibility, v4.0 uses direct loading',
                'superseded_by': 'response-templates-v4.yaml direct loading',
                'size_saved': '~8KB',
                'priority': 'MEDIUM',
                'action': 'REVIEW'  # May have active usage
            },
            
            # Obsolete orchestrators (already archived or deleted)
            {
                'path': 'src/orchestrators/execution/',
                'type': 'directory',
                'reason': 'Migrated to orchestration_4_0',
                'superseded_by': 'src/orchestration_4_0/orchestrators/execution/',
                'size_saved': '~12KB',
                'priority': 'HIGH'
            },
            
            # Legacy document templates
            {
                'path': 'cortex-brain/documents/archived-scripts/',
                'type': 'directory',
                'reason': 'Test scripts for 3.0 foundation - obsolete',
                'superseded_by': 'tests/orchestration_4_0/',
                'size_saved': '~20KB',
                'priority': 'LOW'
            },
            
            # Redundant documentation
            {
                'path': 'cortex-brain/documents/examples/',
                'type': 'directory',
                'reason': 'Outdated examples, duplicates in implementation-guides/',
                'superseded_by': 'cortex-brain/documents/implementation-guides/',
                'size_saved': '~50KB',
                'priority': 'MEDIUM'
            },
            
            {
                'path': 'cortex-brain/documents/narratives/',
                'type': 'directory',
                'reason': 'Story-based docs, mergeable into summaries/',
                'superseded_by': 'cortex-brain/documents/summaries/',
                'size_saved': '~30KB',
                'priority': 'MEDIUM'
            },
            
            {
                'path': 'cortex-brain/documents/scribe/',
                'type': 'directory',
                'reason': 'Auto-generated conversation logs - bloat',
                'superseded_by': 'None (can delete entirely)',
                'size_saved': '~100KB',
                'priority': 'HIGH'
            },
            
            {
                'path': 'cortex-brain/documents/sites/',
                'type': 'directory',
                'reason': 'Website content, should be in docs/ not cortex-brain/',
                'superseded_by': 'docs/',
                'size_saved': '~40KB',
                'priority': 'MEDIUM'
            },
        ]
        
        # Scan each item
        for item in legacy_patterns:
            full_path = self.repo_root / item['path']
            item['exists'] = full_path.exists()
            
            if item['exists']:
                if item['type'] == 'directory':
                    item['file_count'] = sum(1 for _ in full_path.rglob('*') if _.is_file())
                    item['actual_size'] = self._get_dir_size(full_path)
                else:
                    item['file_count'] = 1
                    item['actual_size'] = full_path.stat().st_size if full_path.is_file() else 0
                
                self.legacy_items.append(item)
                
                # Print finding
                status = f"{Colors.RED}❌ EXISTS{Colors.END}"
                print(f"{status} {item['path']}")
                print(f"   Type: {item['type']}")
                print(f"   Reason: {item['reason']}")
                print(f"   Superseded by: {item['superseded_by']}")
                print(f"   Priority: {item['priority']}")
                if item['type'] == 'directory':
                    print(f"   Files: {item['file_count']}")
                print(f"   Size: {self._format_size(item['actual_size'])}")
                print()
        
        print(f"{Colors.BLUE}{'='*80}{Colors.END}")
        print(f"{Colors.BLUE}📊 Scan Complete{Colors.END}")
        print(f"{Colors.BLUE}{'='*80}{Colors.END}")
        print(f"Legacy items found: {len(self.legacy_items)}")
        total_files = sum(item.get('file_count', 0) for item in self.legacy_items)
        total_size = sum(item.get('actual_size', 0) for item in self.legacy_items)
        print(f"Total files: {total_files}")
        print(f"Total size: {self._format_size(total_size)}")
        print()
        
        return self.legacy_items
    
    def delete(self, confirm: bool = False) -> List[Dict]:
        """Delete legacy files"""
        if not self.legacy_items:
            print(f"{Colors.YELLOW}⚠️  No legacy items to delete. Run --scan first.{Colors.END}")
            return []
        
        if not confirm:
            print(f"{Colors.YELLOW}⚠️  DRY RUN MODE - No files will be deleted{Colors.END}")
            print(f"Use --confirm flag to actually delete files\n")
        
        print(f"\n{Colors.BLUE}{'='*80}{Colors.END}")
        print(f"{Colors.BLUE}🗑️  Deleting Legacy Files{Colors.END}")
        print(f"{Colors.BLUE}{'='*80}{Colors.END}\n")
        
        # Group by priority
        high_priority = [item for item in self.legacy_items if item.get('priority') == 'HIGH']
        medium_priority = [item for item in self.legacy_items if item.get('priority') == 'MEDIUM']
        low_priority = [item for item in self.legacy_items if item.get('priority') == 'LOW']
        
        for priority_group, label in [(high_priority, 'HIGH'), (medium_priority, 'MEDIUM'), (low_priority, 'LOW')]:
            if not priority_group:
                continue
            
            print(f"\n{Colors.YELLOW}Priority: {label}{Colors.END}")
            print(f"{'-'*80}")
            
            for item in priority_group:
                # Skip items marked for review
                if item.get('action') == 'REVIEW':
                    print(f"{Colors.YELLOW}⚠️  SKIPPED (needs review): {item['path']}{Colors.END}")
                    continue
                
                full_path = self.repo_root / item['path']
                
                if confirm and full_path.exists():
                    try:
                        if full_path.is_dir():
                            shutil.rmtree(full_path)
                        else:
                            full_path.unlink()
                        
                        print(f"{Colors.GREEN}✅ DELETED: {item['path']}{Colors.END}")
                        self.deleted_items.append(item)
                        
                    except Exception as e:
                        error_msg = f"Failed to delete {item['path']}: {e}"
                        self.errors.append(error_msg)
                        print(f"{Colors.RED}❌ ERROR: {error_msg}{Colors.END}")
                else:
                    print(f"{Colors.BLUE}🔍 Would delete: {item['path']}{Colors.END}")
        
        print(f"\n{Colors.BLUE}{'='*80}{Colors.END}")
        if confirm:
            print(f"{Colors.GREEN}✅ Deletion Complete{Colors.END}")
            print(f"Items deleted: {len(self.deleted_items)}")
        else:
            print(f"{Colors.YELLOW}Dry run complete - use --confirm to delete{Colors.END}")
        print(f"{Colors.BLUE}{'='*80}{Colors.END}\n")
        
        return self.deleted_items
    
    def generate_report(self, output_path: Path = None) -> str:
        """Generate cleanup report"""
        if output_path is None:
            output_path = self.repo_root / "cortex-brain/documents/reports/legacy-cleanup-report.md"
        
        report = []
        report.append("# CORTEX 3.0 Legacy Cleanup Report")
        report.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Mode:** {'DELETE' if not self.dry_run else 'SCAN ONLY'}")
        report.append("\n---\n")
        
        # Summary
        report.append("## 📊 Summary\n")
        report.append(f"- **Legacy Items Found:** {len(self.legacy_items)}")
        report.append(f"- **Items Deleted:** {len(self.deleted_items)}")
        report.append(f"- **Errors:** {len(self.errors)}")
        
        total_files = sum(item.get('file_count', 0) for item in self.legacy_items)
        total_size = sum(item.get('actual_size', 0) for item in self.legacy_items)
        report.append(f"- **Total Files:** {total_files}")
        report.append(f"- **Total Size:** {self._format_size(total_size)}")
        
        # Legacy items table
        report.append("\n## 🗑️  Legacy Items\n")
        report.append("| Path | Type | Priority | Files | Size | Status | Superseded By |")
        report.append("|------|------|----------|-------|------|--------|---------------|")
        
        for item in self.legacy_items:
            status = "✅ Deleted" if item in self.deleted_items else "⏳ Pending"
            files = item.get('file_count', '-')
            size = self._format_size(item.get('actual_size', 0))
            superseded = item.get('superseded_by', '-')
            
            report.append(f"| {item['path']} | {item['type']} | {item['priority']} | {files} | {size} | {status} | {superseded} |")
        
        # Errors
        if self.errors:
            report.append("\n## ❌ Errors\n")
            for error in self.errors:
                report.append(f"- {error}")
        
        # Recommendations
        report.append("\n## 💡 Recommendations\n")
        report.append("1. **High Priority Items:** Delete immediately (src/cortex_3_0/, scribe/)")
        report.append("2. **Medium Priority Items:** Review and consolidate (narratives/ → summaries/)")
        report.append("3. **template_selector.py:** Check for active usage before deletion")
        report.append("4. **Document folders:** Consolidate 2477 files into ~500 essential files (80% reduction target)")
        
        report_text = '\n'.join(report)
        
        # Write to file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report_text, encoding='utf-8')
        print(f"\n📄 Report saved: {output_path}")
        
        return report_text
    
    def _get_dir_size(self, path: Path) -> int:
        """Calculate directory size recursively"""
        return sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
    
    def _format_size(self, size_bytes: int) -> str:
        """Format size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"


def main():
    parser = argparse.ArgumentParser(description='Clean up CORTEX 3.0 legacy files')
    parser.add_argument('--scan', action='store_true', help='Scan for legacy files')
    parser.add_argument('--delete', action='store_true', help='Delete legacy files')
    parser.add_argument('--confirm', action='store_true', help='Confirm deletion (not dry run)')
    parser.add_argument('--report', action='store_true', help='Generate cleanup report')
    
    args = parser.parse_args()
    
    # Find repo root
    repo_root = Path(__file__).parent.parent
    
    # Create cleanup instance
    cleanup = LegacyCleanup(repo_root, dry_run=not args.confirm)
    
    try:
        if args.scan or args.delete:
            # Scan for legacy files
            cleanup.scan()
        
        if args.delete:
            # Delete legacy files
            cleanup.delete(confirm=args.confirm)
        
        if args.report or args.delete:
            # Generate report
            cleanup.generate_report()
        
        if not any([args.scan, args.delete, args.report]):
            parser.print_help()
            return 1
        
        return 0
        
    except Exception as e:
        print(f"{Colors.RED}❌ Error: {e}{Colors.END}", file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
