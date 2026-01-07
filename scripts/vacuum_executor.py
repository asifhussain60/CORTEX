"""
CORTEX Vacuum Execution Script - Direct File Organization & Cleanup.

This script directly executes vacuum operations using the intelligent
analyzers without requiring the full orchestrator framework.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import sys
import logging
import os
from pathlib import Path
from datetime import datetime
import shutil
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.analyze_untracked_files import OrganizationIntelligence as SimpleIntelligence
from src.orchestrators.vacuum.git_integration import GitStatusAnalyzer
from src.orchestrators.vacuum.organization_intelligence import OrganizationIntelligence
from src.orchestrators.vacuum.gitignore_manager import GitIgnoreManager

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class VacuumExecutor:
    """Direct vacuum executor with intelligent file organization."""
    
    def __init__(self, workspace_root: Path, dry_run: bool = True):
        """
        Initialize vacuum executor.
        
        Args:
            workspace_root: Workspace root path
            dry_run: If True, only analyze without making changes
        """
        self.workspace_root = Path(workspace_root)
        self.dry_run = dry_run
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Initialize analyzers
        self.git_analyzer = GitStatusAnalyzer(workspace_root)
        self.org_intelligence = OrganizationIntelligence(workspace_root)
        self.simple_intelligence = SimpleIntelligence()
        self.gitignore_manager = GitIgnoreManager(workspace_root)
        
        # Statistics
        self.stats = {
            'analyzed': 0,
            'deleted': 0,
            'relocated': 0,
            'preserved': 0,
            'skipped': 0,
            'archived': 0
        }
    
    def analyze(self) -> dict:
        """
        Analyze workspace files.
        
        Returns:
            Analysis results dictionary
        """
        logger.info("🔍 Analyzing workspace...")
        
        # Get git status
        git_status = self.git_analyzer.get_status()
        logger.info(f"  Untracked files: {len(git_status.untracked)}")
        logger.info(f"  Deleted files: {len(git_status.deleted)}")
        logger.info(f"  Modified files: {len(git_status.modified)}")
        
        # Analyze with simple intelligence
        simple_report = self.simple_intelligence.analyze()
        
        # Analyze with advanced intelligence
        advanced_analysis = self.org_intelligence.analyze_files(git_status.untracked)
        
        # Get git recommendations
        git_recommendations = self.git_analyzer.get_cleanup_recommendations()
        
        # Scan gitignored files
        logger.info("  Scanning gitignored files...")
        gitignored_scan = self.gitignore_manager.scan_gitignored_files()
        logger.info(f"  Gitignored to delete: {len(gitignored_scan['delete'])} "
                   f"({gitignored_scan['total_size_delete_mb']} MB)")
        logger.info(f"  Gitignored to archive: {len(gitignored_scan['archive'])} "
                   f"({gitignored_scan['total_size_archive_mb']} MB)")
        
        # Combine results
        combined = {
            'timestamp': datetime.now().isoformat(),
            'git_status': {
                'untracked': git_status.untracked,
                'deleted': git_status.deleted,
                'modified': git_status.modified,
                'ignored': git_status.ignored
            },
            'simple_analysis': simple_report,
            'advanced_analysis': advanced_analysis,
            'git_recommendations': git_recommendations,
            'gitignored_scan': gitignored_scan
        }
        
        self.stats['analyzed'] = len(git_status.untracked)
        
        return combined
    
    def get_root_files_to_relocate(self) -> dict:
        """
        Identify root-level files that should be relocated.
        
        Returns:
            Dictionary mapping files to suggested locations
        """
        allowed_root = {
            '.gitignore', '.gitattributes', '.pre-commit-config.yaml',
            'LICENSE', 'README.md', 'requirements.txt', 'pytest.ini',
            'mypy.ini', '.flake8', '.coverage', '.env',
            '.cortex-initialized', '.cortex-installed', '.cortexignore'
        }
        
        relocations = {}
        
        for item in self.workspace_root.iterdir():
            if not item.is_file():
                continue
            
            if item.name in allowed_root:
                continue
            
            # Determine proper location
            name = item.name
            suffix = item.suffix
            
            if name.startswith('cortex-') and suffix in ['.ps1', '.sh', '.py']:
                relocations[str(item.relative_to(self.workspace_root))] = f'scripts/{name}'
            elif name.endswith('-plan.py'):
                relocations[str(item.relative_to(self.workspace_root))] = f'scripts/{name}'
            elif name == 'deployment-manifest.json':
                relocations[str(item.relative_to(self.workspace_root))] = f'cortex-brain/config/{name}'
            elif suffix == '.json' and 'config' in name.lower():
                relocations[str(item.relative_to(self.workspace_root))] = f'cortex-brain/config/{name}'
            elif suffix in ['.yaml', '.yml'] and name not in allowed_root:
                relocations[str(item.relative_to(self.workspace_root))] = f'cortex-brain/config/{name}'
            elif suffix == '.md' and name not in ['README.md', 'LICENSE']:
                relocations[str(item.relative_to(self.workspace_root))] = f'docs/{name}'
        
        return relocations
    
    def find_backup_files(self) -> list:
        """
        Find all backup files outside archives.
        
        Returns:
            List of backup file paths
        """
        backups = []
        
        for root, dirs, files in os.walk(self.workspace_root):
            # Skip archives and .git
            if 'archives' in root or '.git' in root or '.venv' in root:
                continue
            
            for filename in files:
                if any(x in filename.lower() for x in ['.bak', '.backup', 'backup-']):
                    file_path = Path(root) / filename
                    backups.append(str(file_path.relative_to(self.workspace_root)))
        
        return backups
    
    def find_empty_directories(self) -> list:
        """
        Find empty directories.
        
        Returns:
            List of empty directory paths
        """
        import os
        empty_dirs = []
        
        for root, dirs, files in os.walk(self.workspace_root):
            # Skip .git and .venv
            if '.git' in root or '.venv' in root:
                continue
            
            root_path = Path(root)
            if not any(root_path.iterdir()):
                empty_dirs.append(str(root_path.relative_to(self.workspace_root)))
        
        return empty_dirs
    
    def execute_cleanup(self, analysis: dict, actions: dict = None, include_root: bool = False, 
                       include_backups: bool = False, include_empty: bool = False,
                       include_gitignored: bool = False) -> dict:
        """
        Execute cleanup operations.
        
        Args:
            analysis: Analysis results from analyze()
            actions: Optional dict with 'delete', 'relocate' lists
            include_root: If True, relocate root-level files
            include_backups: If True, move backup files to archives
            include_empty: If True, remove empty directories
            include_gitignored: If True, delete/archive gitignored files
        
        Returns:
            Execution results dictionary
        """
        if actions is None:
            # Use recommendations from simple analysis (safer)
            simple_actions = analysis['simple_analysis']['actions']
            
            # Convert DELETE list to proper format
            delete_list = []
            for filepath in simple_actions.get('DELETE', []):
                delete_list.append({'path': filepath, 'reason': 'temp/cache/obsolete'})
            
            # Add gitignored files if requested
            if include_gitignored:
                gitignored = analysis['gitignored_scan']
                for file_info in gitignored['delete']:
                    delete_list.append({
                        'path': file_info['path'],
                        'reason': f"Gitignored: {file_info['reason']} ({file_info['size_mb']} MB)"
                    })
                logger.info(f"  Added {len(gitignored['delete'])} gitignored files for deletion")
            
            # Use git recommendations for relocations
            relocate_dict = analysis['git_recommendations']['relocate']
            
            # Add root file relocations if requested
            if include_root:
                root_relocations = self.get_root_files_to_relocate()
                relocate_dict.update(root_relocations)
                logger.info(f"  Added {len(root_relocations)} root file relocations")
            
            # Add backup file relocations if requested
            if include_backups:
                backup_files = self.find_backup_files()
                for backup in backup_files:
                    filename = Path(backup).name
                    relocate_dict[backup] = f'cortex-brain/archives/backups/{filename}'
                logger.info(f"  Added {len(backup_files)} backup file relocations")
            
            # Handle gitignored files to archive
            archive_list = []
            if include_gitignored:
                gitignored = analysis['gitignored_scan']
                for file_info in gitignored['archive']:
                    archive_list.append({
                        'path': file_info['path'],
                        'reason': f"Gitignored: {file_info['reason']}"
                    })
                logger.info(f"  Added {len(gitignored['archive'])} gitignored files for archiving")
            
            actions = {
                'delete': delete_list,
                'relocate': relocate_dict,
                'archive': archive_list
            }
        
        results = {
            'deleted': [],
            'relocated': [],
            'archived': [],
            'empty_removed': [],
            'errors': []
        }
        
        # DELETE operations
        logger.info(f"\n🗑️  Processing {len(actions['delete'])} deletions...")
        for item in actions['delete']:
            filepath = item['path'] if isinstance(item, dict) else item
            full_path = self.workspace_root / filepath
            
            try:
                if self.dry_run:
                    logger.info(f"  [DRY-RUN] Would delete: {filepath}")
                    results['deleted'].append({'path': filepath, 'status': 'simulated'})
                else:
                    if full_path.is_file():
                        full_path.unlink()
                        logger.info(f"  ✅ Deleted: {filepath}")
                        results['deleted'].append({'path': filepath, 'status': 'success'})
                    elif full_path.is_dir():
                        shutil.rmtree(full_path)
                        logger.info(f"  ✅ Deleted directory: {filepath}")
                        results['deleted'].append({'path': filepath, 'status': 'success'})
                    else:
                        logger.warning(f"  ⚠️  Not found: {filepath}")
                        results['errors'].append({'path': filepath, 'error': 'not_found'})
                
                self.stats['deleted'] += 1
            
            except Exception as e:
                logger.error(f"  ❌ Failed to delete {filepath}: {e}")
                results['errors'].append({'path': filepath, 'error': str(e)})
        
        # RELOCATE operations
        relocations = actions['relocate']
        logger.info(f"\n📦 Processing {len(relocations)} relocations...")
        for old_path, new_path in relocations.items():
            full_old = self.workspace_root / old_path
            full_new = self.workspace_root / new_path
            
            try:
                if self.dry_run:
                    logger.info(f"  [DRY-RUN] Would move: {old_path} → {new_path}")
                    results['relocated'].append({
                        'from': old_path,
                        'to': new_path,
                        'status': 'simulated'
                    })
                else:
                    # Create destination directory
                    full_new.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Move file
                    shutil.move(str(full_old), str(full_new))
                    logger.info(f"  ✅ Moved: {old_path} → {new_path}")
                    results['relocated'].append({
                        'from': old_path,
                        'to': new_path,
                        'status': 'success'
                    })
                
                self.stats['relocated'] += 1
            
            except Exception as e:
                logger.error(f"  ❌ Failed to relocate {old_path}: {e}")
                results['errors'].append({'path': old_path, 'error': str(e)})
        
        # ARCHIVE operations (for gitignored files we're unsure about)
        if 'archive' in actions and actions['archive']:
            archive_list = actions['archive']
            logger.info(f"\n📦 Processing {len(archive_list)} archive operations...")
            
            archive_base = self.workspace_root / 'cortex-brain' / 'archives' / 'gitignored'
            archive_base.mkdir(parents=True, exist_ok=True)
            
            for item in archive_list:
                filepath = item['path'] if isinstance(item, dict) else item
                full_old = self.workspace_root / filepath
                full_new = archive_base / Path(filepath).name
                
                try:
                    if self.dry_run:
                        logger.info(f"  [DRY-RUN] Would archive: {filepath}")
                        results['archived'].append({'path': filepath, 'status': 'simulated'})
                    else:
                        shutil.move(str(full_old), str(full_new))
                        logger.info(f"  ✅ Archived: {filepath}")
                        results['archived'].append({
                            'from': filepath,
                            'to': str(full_new.relative_to(self.workspace_root)),
                            'status': 'success'
                        })
                    
                    self.stats['archived'] += 1
                
                except Exception as e:
                    logger.error(f"  ❌ Failed to archive {filepath}: {e}")
                    results['errors'].append({'path': filepath, 'error': str(e)})
        
        # REMOVE EMPTY DIRECTORIES
        if include_empty:
            empty_dirs = self.find_empty_directories()
            logger.info(f"\n📭 Processing {len(empty_dirs)} empty directories...")
            
            for dir_path in empty_dirs:
                full_path = self.workspace_root / dir_path
                
                try:
                    if self.dry_run:
                        logger.info(f"  [DRY-RUN] Would remove empty dir: {dir_path}")
                        results['empty_removed'].append({'path': dir_path, 'status': 'simulated'})
                    else:
                        if full_path.is_dir():
                            full_path.rmdir()
                            logger.info(f"  ✅ Removed empty: {dir_path}")
                            results['empty_removed'].append({'path': dir_path, 'status': 'success'})
                
                except Exception as e:
                    logger.error(f"  ❌ Failed to remove {dir_path}: {e}")
                    results['errors'].append({'path': dir_path, 'error': str(e)})
        
        return results
    
    def save_report(self, analysis: dict, execution: dict = None):
        """
        Save comprehensive report.
        
        Args:
            analysis: Analysis results
            execution: Execution results (if operations were performed)
        """
        report_dir = self.workspace_root / 'cortex-brain' / 'cleanup-reports'
        report_dir.mkdir(parents=True, exist_ok=True)
        
        # Save JSON report
        json_report = {
            'timestamp': self.timestamp,
            'dry_run': self.dry_run,
            'statistics': self.stats,
            'analysis': analysis,
            'execution': execution
        }
        
        json_path = report_dir / f'vacuum-execution-{self.timestamp}.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_report, f, indent=2)
        logger.info(f"\n✅ JSON report saved: {json_path}")
        
        # Save markdown report
        md_lines = self._generate_markdown_report(analysis, execution)
        md_path = report_dir / f'vacuum-execution-{self.timestamp}.md'
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(md_lines))
        logger.info(f"✅ Markdown report saved: {md_path}")
    
    def _generate_markdown_report(self, analysis: dict, execution: dict = None) -> list:
        """Generate markdown report lines."""
        lines = []
        
        lines.append("# 🧹 CORTEX Vacuum Execution Report")
        lines.append(f"\n**Timestamp:** {self.timestamp}")
        lines.append(f"**Mode:** {'DRY-RUN' if self.dry_run else 'LIVE EXECUTION'}")
        lines.append("\n---\n")
        
        # Statistics
        lines.append("## 📊 Statistics\n")
        for key, value in self.stats.items():
            lines.append(f"- **{key.title()}:** {value}")
        
        # Analysis summary
        lines.append("\n## 🔍 Analysis Summary\n")
        simple = analysis['simple_analysis']['statistics']
        lines.append(f"- Total Untracked: {simple['total_untracked']}")
        lines.append(f"- To Delete: {simple['by_action'].get('DELETE', 0)}")
        lines.append(f"- To Relocate: {simple['relocations']}")
        lines.append(f"- To Preserve: {simple['by_action'].get('PRESERVE', 0)}")
        
        # Execution results
        if execution:
            lines.append("\n## ✅ Execution Results\n")
            lines.append(f"- Deleted: {len(execution['deleted'])} files")
            lines.append(f"- Relocated: {len(execution['relocated'])} files")
            lines.append(f"- Errors: {len(execution['errors'])}")
            
            if execution['errors']:
                lines.append("\n### ❌ Errors\n")
                for error in execution['errors']:
                    lines.append(f"- `{error['path']}`: {error['error']}")
        
        return lines


def main():
    """Main entry point."""
    import argparse
    
    # Set UTF-8 encoding for Windows console
    if sys.platform == 'win32':
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    
    parser = argparse.ArgumentParser(description='CORTEX Vacuum Executor')
    parser.add_argument('--workspace', type=str, default='.',
                       help='Workspace root path')
    parser.add_argument('--dry-run', action='store_true', default=True,
                       help='Analyze only (default)')
    parser.add_argument('--execute', action='store_true',
                       help='Execute cleanup operations (DANGER!)')
    parser.add_argument('--include-root', action='store_true',
                       help='Include root-level file relocations')
    parser.add_argument('--include-backups', action='store_true',
                       help='Relocate all backup files to archives')
    parser.add_argument('--include-empty', action='store_true',
                       help='Remove empty directories')
    parser.add_argument('--include-gitignored', action='store_true',
                       help='Delete/archive gitignored files (AGGRESSIVE)')
    parser.add_argument('--full-cleanup', action='store_true',
                       help='Enable all cleanup options including gitignored files')
    
    args = parser.parse_args()
    
    # Set dry_run based on --execute flag
    dry_run = not args.execute
    
    # Handle full cleanup flag
    if args.full_cleanup:
        args.include_root = True
        args.include_backups = True
        args.include_empty = True
        args.include_gitignored = True
    
    print("=" * 70)
    print("🧹 CORTEX VACUUM EXECUTOR")
    print("=" * 70)
    print(f"Mode: {'DRY-RUN (Safe)' if dry_run else 'LIVE EXECUTION (DANGER!)'}")
    print(f"Workspace: {Path(args.workspace).absolute()}")
    print(f"Root cleanup: {'Yes' if args.include_root else 'No'}")
    print(f"Backup consolidation: {'Yes' if args.include_backups else 'No'}")
    print(f"Empty dir removal: {'Yes' if args.include_empty else 'No'}")
    print(f"Gitignored files: {'Yes (AGGRESSIVE!)' if args.include_gitignored else 'No'}")
    print("=" * 70)
    
    if not dry_run:
        response = input("\n⚠️  LIVE EXECUTION MODE! Files will be deleted/moved. Continue? (yes/no): ")
        if response.lower() != 'yes':
            print("❌ Aborted.")
            return
    
    # Initialize executor
    executor = VacuumExecutor(Path(args.workspace), dry_run=dry_run)
    
    # Analyze
    analysis = executor.analyze()
    
    # Execute cleanup with options
    execution = executor.execute_cleanup(
        analysis,
        include_root=args.include_root,
        include_backups=args.include_backups,
        include_empty=args.include_empty,
        include_gitignored=args.include_gitignored
    )
    
    # Save report
    executor.save_report(analysis, execution)
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 EXECUTION SUMMARY")
    print("=" * 70)
    for key, value in executor.stats.items():
        print(f"  {key.title()}: {value}")
    print("=" * 70)
    print("\n✅ Vacuum execution complete!")


if __name__ == "__main__":
    main()
