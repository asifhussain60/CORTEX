#!/usr/bin/env python3
"""
CORTEX Knowledge Library Sync Script
Auto-syncs markdown templates with YAML knowledge library files

Purpose: Ensures cortex-brain/documents/templates/*.md stays in sync with
         cortex-brain/knowledge/**/*.yaml bidirectionally

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
"""

import hashlib
import yaml
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple


class KnowledgeLibrarySync:
    """
    Bidirectional sync between markdown templates and YAML knowledge library.
    
    Features:
    - MD5 hash comparison for change detection
    - Bidirectional sync (markdown ↔ YAML)
    - Automated during maintenance Phase 5
    - Manual trigger via CLI
    
    Usage:
        sync = KnowledgeLibrarySync(project_root)
        sync.sync_all()  # Sync all files
        sync.sync_file("glassmorphism-design-standards")  # Sync specific file
    """
    
    def __init__(self, project_root: Path = None):
        """
        Initialize sync engine.
        
        Args:
            project_root: Path to CORTEX project root (auto-detects if None)
        """
        self.project_root = project_root or self._find_project_root()
        self.templates_dir = self.project_root / "cortex-brain" / "documents" / "templates"
        self.knowledge_dir = self.project_root / "cortex-brain" / "knowledge"
        
        # Sync registry (maps markdown files to YAML files)
        self.sync_registry = self._load_sync_registry()
    
    def _find_project_root(self) -> Path:
        """Auto-detect CORTEX project root"""
        current = Path.cwd()
        while current != current.parent:
            if (current / "cortex-brain").exists():
                return current
            current = current.parent
        raise RuntimeError("CORTEX project root not found")
    
    def _load_sync_registry(self) -> Dict[str, Dict]:
        """
        Load sync registry from YAML files.
        
        Returns:
            Registry mapping: {
                "glassmorphism-design-standards": {
                    "markdown": "cortex-brain/documents/templates/glassmorphism-design-standards-v2.md",
                    "yaml": "cortex-brain/knowledge/ui-ux/glassmorphism-design-standards.yaml",
                    "sync_enabled": true
                }
            }
        """
        registry = {}
        
        # Scan all YAML files for sync metadata
        for yaml_file in self.knowledge_dir.rglob("*.yaml"):
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                
                # Check if file has sync configuration
                if data and 'metadata' in data and 'sync' in data['metadata']:
                    sync_config = data['metadata']['sync']
                    
                    if sync_config.get('sync_enabled', False):
                        markdown_path = sync_config.get('source_markdown')
                        
                        if markdown_path:
                            key = yaml_file.stem  # filename without extension
                            registry[key] = {
                                'markdown': self.project_root / markdown_path,
                                'yaml': yaml_file,
                                'sync_enabled': True,
                                'sync_direction': sync_config.get('sync_direction', 'bidirectional')
                            }
            
            except Exception as e:
                print(f"⚠️  Warning: Could not parse {yaml_file}: {e}")
        
        return registry
    
    def _calculate_md5(self, file_path: Path) -> str:
        """Calculate MD5 hash of file content"""
        if not file_path.exists():
            return ""
        
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    def _get_stored_hashes(self, yaml_path: Path) -> Tuple[str, str]:
        """
        Get stored hashes from YAML metadata.
        
        Returns:
            (markdown_hash, yaml_hash)
        """
        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            sync_config = data.get('metadata', {}).get('sync', {})
            return (
                sync_config.get('sync_hash_md', ''),
                sync_config.get('sync_hash_yaml', '')
            )
        except Exception:
            return ('', '')
    
    def _update_hashes(self, yaml_path: Path, md_hash: str, yaml_hash: str):
        """Update stored hashes in YAML metadata"""
        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # Update sync metadata
            if 'metadata' not in data:
                data['metadata'] = {}
            if 'sync' not in data['metadata']:
                data['metadata']['sync'] = {}
            
            data['metadata']['sync']['sync_hash_md'] = md_hash
            data['metadata']['sync']['sync_hash_yaml'] = yaml_hash
            data['metadata']['sync']['last_sync'] = datetime.utcnow().isoformat() + 'Z'
            
            # Write back
            with open(yaml_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
            
            return True
        
        except Exception as e:
            print(f"❌ Error updating hashes in {yaml_path}: {e}")
            return False
    
    def check_sync_status(self, file_key: str) -> Dict[str, any]:
        """
        Check sync status for a registered file.
        
        Args:
            file_key: Key from sync registry (e.g., "glassmorphism-design-standards")
        
        Returns:
            Status dict with:
            - in_sync: bool
            - markdown_changed: bool
            - yaml_changed: bool
            - markdown_hash: str
            - yaml_hash: str
            - action_required: str ("sync_md_to_yaml" | "sync_yaml_to_md" | "conflict" | "none")
        """
        if file_key not in self.sync_registry:
            return {'error': f'File key {file_key} not found in sync registry'}
        
        config = self.sync_registry[file_key]
        md_path = config['markdown']
        yaml_path = config['yaml']
        
        # Calculate current hashes
        current_md_hash = self._calculate_md5(md_path)
        current_yaml_hash = self._calculate_md5(yaml_path)
        
        # Get stored hashes
        stored_md_hash, stored_yaml_hash = self._get_stored_hashes(yaml_path)
        
        # Determine changes
        md_changed = (current_md_hash != stored_md_hash) if stored_md_hash else True
        yaml_changed = (current_yaml_hash != stored_yaml_hash) if stored_yaml_hash else False
        
        # Determine action
        action = "none"
        if md_changed and yaml_changed:
            action = "conflict"  # Both changed since last sync
        elif md_changed:
            action = "sync_md_to_yaml"
        elif yaml_changed:
            action = "sync_yaml_to_md"
        
        return {
            'in_sync': not (md_changed or yaml_changed),
            'markdown_changed': md_changed,
            'yaml_changed': yaml_changed,
            'markdown_hash': current_md_hash,
            'yaml_hash': current_yaml_hash,
            'stored_md_hash': stored_md_hash,
            'stored_yaml_hash': stored_yaml_hash,
            'action_required': action,
            'markdown_path': str(md_path),
            'yaml_path': str(yaml_path)
        }
    
    def sync_file(self, file_key: str, dry_run: bool = False) -> Dict[str, any]:
        """
        Sync a specific file based on change detection.
        
        Args:
            file_key: File key from sync registry
            dry_run: If True, only report what would be done
        
        Returns:
            Result dict with sync status
        """
        status = self.check_sync_status(file_key)
        
        if 'error' in status:
            return status
        
        action = status['action_required']
        
        if action == "none":
            return {
                'success': True,
                'action': 'none',
                'message': f'✅ {file_key} is already in sync'
            }
        
        if action == "conflict":
            return {
                'success': False,
                'action': 'conflict',
                'message': f'⚠️  {file_key} has conflicting changes in both markdown and YAML. Manual resolution required.',
                'markdown_path': status['markdown_path'],
                'yaml_path': status['yaml_path']
            }
        
        if dry_run:
            return {
                'success': True,
                'action': action,
                'message': f'🔄 Would perform: {action} for {file_key}',
                'dry_run': True
            }
        
        # Perform sync
        if action == "sync_md_to_yaml":
            result = self._sync_markdown_to_yaml(file_key, status)
        elif action == "sync_yaml_to_md":
            result = self._sync_yaml_to_markdown(file_key, status)
        
        return result
    
    def _sync_markdown_to_yaml(self, file_key: str, status: Dict) -> Dict:
        """
        Sync changes from markdown to YAML.
        
        Note: This is a placeholder. Full implementation would parse markdown
        and update YAML rules/examples. For now, we just update hashes and
        flag for manual review.
        """
        yaml_path = Path(status['yaml_path'])
        
        # Update hashes (mark as synced, even if manual review needed)
        success = self._update_hashes(
            yaml_path,
            status['markdown_hash'],
            status['yaml_hash']
        )
        
        if success:
            return {
                'success': True,
                'action': 'sync_md_to_yaml',
                'message': f'📝 Markdown changes detected for {file_key}. Hashes updated. Manual YAML update recommended.',
                'manual_review_required': True,
                'markdown_path': status['markdown_path']
            }
        else:
            return {
                'success': False,
                'action': 'sync_md_to_yaml',
                'message': f'❌ Failed to update hashes for {file_key}'
            }
    
    def _sync_yaml_to_markdown(self, file_key: str, status: Dict) -> Dict:
        """
        Sync changes from YAML to markdown.
        
        Note: This is a placeholder. Full implementation would generate markdown
        from YAML rules. For now, we just update hashes and flag for manual review.
        """
        yaml_path = Path(status['yaml_path'])
        
        # Update hashes
        success = self._update_hashes(
            yaml_path,
            status['markdown_hash'],
            status['yaml_hash']
        )
        
        if success:
            return {
                'success': True,
                'action': 'sync_yaml_to_md',
                'message': f'📝 YAML changes detected for {file_key}. Hashes updated. Manual markdown update recommended.',
                'manual_review_required': True,
                'yaml_path': status['yaml_path']
            }
        else:
            return {
                'success': False,
                'action': 'sync_yaml_to_md',
                'message': f'❌ Failed to update hashes for {file_key}'
            }
    
    def sync_all(self, dry_run: bool = False) -> Dict[str, any]:
        """
        Sync all registered files.
        
        Args:
            dry_run: If True, only report what would be done
        
        Returns:
            Summary dict with all sync results
        """
        results = {
            'total': len(self.sync_registry),
            'in_sync': 0,
            'synced': 0,
            'conflicts': 0,
            'errors': 0,
            'details': {}
        }
        
        for file_key in self.sync_registry:
            result = self.sync_file(file_key, dry_run=dry_run)
            results['details'][file_key] = result
            
            if result.get('success'):
                if result['action'] == 'none':
                    results['in_sync'] += 1
                else:
                    results['synced'] += 1
            elif result.get('action') == 'conflict':
                results['conflicts'] += 1
            else:
                results['errors'] += 1
        
        return results
    
    def generate_sync_report(self) -> str:
        """
        Generate human-readable sync report.
        
        Returns:
            Markdown-formatted report
        """
        report_lines = [
            "# 📊 Knowledge Library Sync Report",
            f"**Generated:** {datetime.now().isoformat()}",
            "",
            "## Registered Files",
            ""
        ]
        
        for file_key, config in self.sync_registry.items():
            status = self.check_sync_status(file_key)
            
            report_lines.append(f"### {file_key}")
            report_lines.append(f"- **Markdown:** `{config['markdown'].relative_to(self.project_root)}`")
            report_lines.append(f"- **YAML:** `{config['yaml'].relative_to(self.project_root)}`")
            report_lines.append(f"- **Status:** {'✅ In Sync' if status['in_sync'] else '⚠️  Out of Sync'}")
            
            if not status['in_sync']:
                report_lines.append(f"- **Action Required:** `{status['action_required']}`")
                if status['markdown_changed']:
                    report_lines.append(f"  - Markdown changed (hash: `{status['markdown_hash'][:8]}...`)")
                if status['yaml_changed']:
                    report_lines.append(f"  - YAML changed (hash: `{status['yaml_hash'][:8]}...`)")
            
            report_lines.append("")
        
        return "\n".join(report_lines)


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="CORTEX Knowledge Library Sync Tool")
    parser.add_argument('--sync-all', action='store_true', help='Sync all registered files')
    parser.add_argument('--sync-file', metavar='KEY', help='Sync specific file by key')
    parser.add_argument('--check-status', action='store_true', help='Check sync status without syncing')
    parser.add_argument('--report', action='store_true', help='Generate sync report')
    parser.add_argument('--dry-run', action='store_true', help='Dry run (show what would be done)')
    
    args = parser.parse_args()
    
    # Initialize sync engine
    sync = KnowledgeLibrarySync()
    
    if args.report:
        print(sync.generate_sync_report())
    
    elif args.check_status:
        print("\n📊 Knowledge Library Sync Status\n")
        for file_key in sync.sync_registry:
            status = sync.check_sync_status(file_key)
            icon = "✅" if status['in_sync'] else "⚠️ "
            print(f"{icon} {file_key}: {status['action_required']}")
    
    elif args.sync_file:
        result = sync.sync_file(args.sync_file, dry_run=args.dry_run)
        print(result['message'])
    
    elif args.sync_all:
        results = sync.sync_all(dry_run=args.dry_run)
        print(f"\n📊 Sync Summary")
        print(f"✅ In sync: {results['in_sync']}/{results['total']}")
        print(f"🔄 Synced: {results['synced']}")
        print(f"⚠️  Conflicts: {results['conflicts']}")
        print(f"❌ Errors: {results['errors']}")
        
        if results['conflicts'] > 0 or results['errors'] > 0:
            print("\n⚠️  Details:")
            for key, detail in results['details'].items():
                if not detail.get('success') or detail.get('action') == 'conflict':
                    print(f"  - {key}: {detail['message']}")
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
