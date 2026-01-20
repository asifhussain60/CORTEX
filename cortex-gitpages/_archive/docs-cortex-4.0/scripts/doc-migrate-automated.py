#!/usr/bin/env python3
"""
PHASE-30: Automated Documentation Reorganization Orchestrator

This script provides fully automated, idempotent documentation reorganization:
1. Audit: Categorize all docs/ files using deterministic rules
2. Migrate: Move files to GitHub Pages structure
3. Verify: Validate GitHub Pages readiness

No manual review required. Safe to execute repeatedly.
"""

import os
import json
import shutil
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import re
import yaml


class DocumentationMigrator:
    """Orchestrator for automated documentation reorganization."""
    
    def __init__(self, docs_root: str = "docs", dry_run: bool = False):
        """
        Initialize migration orchestrator.
        
        Args:
            docs_root: Root directory for documentation (default: docs/)
            dry_run: If True, show what WOULD happen without making changes
        """
        self.docs_root = Path(docs_root)
        self.dry_run = dry_run
        self.timestamp = datetime.now().isoformat()
        self.audit_log = {
            'timestamp': self.timestamp,
            'mode': 'DRY_RUN' if dry_run else 'EXECUTE',
            'stats': {
                'total_files': 0,
                'ignored_files': 0,
                'moved_files': 0,
                'merged_files': 0,
                'deleted_files': 0,
                'errors': 0,
            },
            'actions': [],
            'deletions': [],
            'moves': [],
            'merges': [],
            'errors': [],
        }
        self.ignore_patterns = {}
        self.categorization_rules = {}
        
    def load_ignore_list(self, ignore_list_path: str) -> None:
        """Load ignore patterns from YAML."""
        with open(ignore_list_path, 'r') as f:
            config = yaml.safe_load(f)
            self.ignore_patterns = config.get('executable_prompts', {})
            self.ignore_patterns.update(config.get('agent_definitions', {}))
            self.ignore_patterns.update(config.get('specifications', {}))
            self.ignore_patterns.update(config.get('temporary_artifacts', {}))
            self.ignore_patterns.update(config.get('executable_scripts', {}))
            self.ignore_patterns.update(config.get('metadata_and_indexes', {}))
    
    def load_categorization_rules(self, rules_path: str) -> None:
        """Load categorization rules from YAML."""
        with open(rules_path, 'r') as f:
            config = yaml.safe_load(f)
            self.categorization_rules = config.get('categorization_rules', [])
    
    def should_ignore(self, filename: str) -> Tuple[bool, Optional[str]]:
        """
        Check if file matches any ignore pattern.
        
        Returns:
            Tuple of (is_ignored, reason)
        """
        ignore_patterns = []
        
        # Flatten ignore patterns from config
        for pattern_group in self.ignore_patterns.values():
            if isinstance(pattern_group, dict) and 'patterns' in pattern_group:
                ignore_patterns.extend(pattern_group['patterns'])
        
        # Check each pattern
        for pattern in ignore_patterns:
            if self._pattern_matches(filename, pattern):
                return True, f"Matches ignore pattern: {pattern}"
        
        return False, None
    
    def _pattern_matches(self, filename: str, pattern: str) -> bool:
        """Check if filename matches glob pattern."""
        # Convert glob pattern to regex
        if pattern == "*":
            return True
        
        # Handle wildcard patterns
        regex_pattern = pattern.replace(".", r"\.").replace("*", ".*")
        regex_pattern = f"^{regex_pattern}$"
        
        return bool(re.match(regex_pattern, filename, re.IGNORECASE))
    
    def categorize_file(self, filename: str) -> Tuple[str, str]:
        """
        Apply categorization rules to determine target folder.
        
        Returns:
            Tuple of (category_folder, normalized_filename)
        """
        best_rule = None
        
        # Evaluate each rule in priority order
        for rule in self.categorization_rules:
            patterns = rule.get('patterns', [])
            
            for pattern in patterns:
                if self._pattern_matches(filename, pattern):
                    best_rule = rule
                    break
            
            if best_rule:
                break
        
        # Use default if no rule matched
        if not best_rule:
            best_rule = {
                'category': 'concepts/',
                'id': 'rule_default'
            }
        
        category = best_rule.get('category', 'concepts/')
        normalized = self._normalize_filename(filename)
        
        return category, normalized
    
    def _normalize_filename(self, filename: str) -> str:
        """
        Convert filename to kebab-case and truncate.
        
        Examples:
            "CORTEX-HOLISTIC-REVIEW-20260118.md" → "cortex-holistic-review.md"
            "cortex-builder-issue-remediation-pattern.md" → "cortex-builder-remediation-pattern.md"
        """
        # Remove .md extension
        name = filename.replace('.md', '')
        
        # Convert to lowercase
        name = name.lower()
        
        # Replace underscores with hyphens
        name = name.replace('_', '-')
        
        # Remove date stamps (e.g., -20260118)
        name = re.sub(r'-\d{8}$', '', name)
        name = re.sub(r'-\d{8}t\d{6}', '', name)
        
        # Remove duplicates of the same words
        parts = name.split('-')
        seen = set()
        unique_parts = []
        for part in parts:
            if part not in seen and part:
                unique_parts.append(part)
                seen.add(part)
        
        name = '-'.join(unique_parts)
        
        # Truncate to 50 chars
        if len(name) > 50:
            name = name[:47] + '...'
        
        # Add .md back
        return f"{name}.md"
    
    def collect_all_files(self) -> List[Path]:
        """Recursively collect all .md files from docs/."""
        files = []
        for md_file in self.docs_root.rglob('*.md'):
            # Skip system files
            if any(part.startswith('.') for part in md_file.parts):
                continue
            files.append(md_file)
        
        # Sort alphabetically for deterministic ordering
        return sorted(files)
    
    def plan_migration(self) -> Dict:
        """Generate migration plan without executing."""
        files = self.collect_all_files()
        self.audit_log['stats']['total_files'] = len(files)
        
        migration_plan = {
            'deletions': [],    # Files to delete (ignored)
            'moves': {},        # filename -> (old_path, new_path)
            'merges': {},       # target_path -> [source_files]
        }
        
        for file_path in files:
            relative_path = file_path.relative_to(self.docs_root)
            filename = relative_path.name
            
            # Check ignore list
            should_ignore, reason = self.should_ignore(filename)
            if should_ignore:
                migration_plan['deletions'].append({
                    'file': str(relative_path),
                    'reason': reason,
                })
                self.audit_log['stats']['ignored_files'] += 1
                continue
            
            # Categorize file
            category, normalized_filename = self.categorize_file(filename)
            
            # Build target path
            target_path = f"{category}{normalized_filename}"
            
            # Check for collision
            if target_path in migration_plan['merges']:
                migration_plan['merges'][target_path].append(str(relative_path))
                self.audit_log['stats']['merged_files'] += 1
            else:
                migration_plan['merges'][target_path] = [str(relative_path)]
                if str(relative_path) != target_path:
                    migration_plan['moves'][filename] = (
                        str(relative_path),
                        target_path
                    )
                    self.audit_log['stats']['moved_files'] += 1
        
        self.audit_log['stats']['deleted_files'] = len(migration_plan['deletions'])
        
        return migration_plan
    
    def execute_migration(self, migration_plan: Dict) -> bool:
        """Execute migration plan (respects dry_run mode)."""
        try:
            # Phase 1: Delete ignored files
            for deletion in migration_plan['deletions']:
                file_path = self.docs_root / deletion['file']
                action = {
                    'type': 'DELETE',
                    'file': deletion['file'],
                    'reason': deletion['reason'],
                    'timestamp': datetime.now().isoformat(),
                }
                
                if self.dry_run:
                    action['status'] = 'DRY_RUN'
                else:
                    if file_path.exists():
                        file_path.unlink()
                    action['status'] = 'DELETED'
                
                self.audit_log['deletions'].append(action)
            
            # Phase 2: Create target directories
            target_dirs = set()
            for target_path in migration_plan['merges'].keys():
                target_dir = str(Path(target_path).parent)
                if target_dir:
                    target_dirs.add(target_dir)
            
            for target_dir in sorted(target_dirs):
                target_dir_path = self.docs_root / target_dir
                if not self.dry_run:
                    target_dir_path.mkdir(parents=True, exist_ok=True)
            
            # Phase 3: Move/merge files
            for target_path, source_files in migration_plan['merges'].items():
                if len(source_files) == 1:
                    # Single file - just move it
                    old_path = self.docs_root / source_files[0]
                    new_path = self.docs_root / target_path
                    
                    action = {
                        'type': 'MOVE',
                        'from': source_files[0],
                        'to': target_path,
                        'timestamp': datetime.now().isoformat(),
                    }
                    
                    if self.dry_run:
                        action['status'] = 'DRY_RUN'
                    else:
                        if old_path != new_path and old_path.exists():
                            new_path.parent.mkdir(parents=True, exist_ok=True)
                            shutil.move(str(old_path), str(new_path))
                        action['status'] = 'MOVED'
                    
                    self.audit_log['moves'].append(action)
                
                else:
                    # Multiple files - merge them
                    merged_content = []
                    
                    for source_file in sorted(source_files):
                        source_path = self.docs_root / source_file
                        if source_path.exists():
                            with open(source_path, 'r') as f:
                                content = f.read()
                            
                            # Add source header
                            merged_content.append(f"\n## Source: {source_file}\n")
                            merged_content.append(content)
                    
                    action = {
                        'type': 'MERGE',
                        'sources': source_files,
                        'target': target_path,
                        'timestamp': datetime.now().isoformat(),
                    }
                    
                    if self.dry_run:
                        action['status'] = 'DRY_RUN'
                    else:
                        target_file = self.docs_root / target_path
                        target_file.parent.mkdir(parents=True, exist_ok=True)
                        with open(target_file, 'w') as f:
                            f.write('\n'.join(merged_content))
                        
                        # Delete source files
                        for source_file in source_files:
                            source_path = self.docs_root / source_file
                            if source_path.exists():
                                source_path.unlink()
                        
                        action['status'] = 'MERGED'
                    
                    self.audit_log['merges'].append(action)
            
            return True
        
        except Exception as e:
            self.audit_log['errors'].append({
                'type': 'MIGRATION_ERROR',
                'message': str(e),
                'timestamp': datetime.now().isoformat(),
            })
            self.audit_log['stats']['errors'] += 1
            return False
    
    def generate_github_pages_structure(self) -> bool:
        """Generate GitHub Pages structure files."""
        try:
            # Create _config.yml
            config_yml = {
                'title': 'CORTEX Documentation',
                'description': 'AI-Powered Development Orchestration System',
                'theme': 'jekyll-theme-slate',
                'show_downloads': False,
                'github': {
                    'repository_url': 'https://github.com/asifhussain60/CORTEX',
                    'pages': {
                        'url': 'https://asifhussain60.github.io/CORTEX/'
                    }
                }
            }
            
            if not self.dry_run:
                config_path = self.docs_root / '_config.yml'
                with open(config_path, 'w') as f:
                    yaml.dump(config_yml, f, default_flow_style=False)
            
            # Create index.md
            index_content = """# CORTEX Documentation

Welcome to CORTEX - AI-Powered Development Orchestration System.

## Navigation

- **[Guides](guides/)** - How-to guides and quick starts
- **[Concepts](concepts/)** - Architecture and design concepts
- **[Reference](reference/)** - API reference and specifications
- **[Architecture](architecture/)** - System design and patterns
- **[Processes](processes/)** - Operational procedures
- **[Research](research/)** - Analysis and research findings
- **[Reports](reports/)** - Phase completion and verification reports

## Quick Start

New to CORTEX? Start with the [Quick Start Guide](guides/quick-start.md).

## About

CORTEX is a comprehensive AI-powered development orchestration system designed to streamline software development workflows with intelligent automation, governance, and decision support.

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**
"""
            
            if not self.dry_run:
                index_path = self.docs_root / 'index.md'
                with open(index_path, 'w') as f:
                    f.write(index_content)
            
            return True
        
        except Exception as e:
            self.audit_log['errors'].append({
                'type': 'GITHUB_PAGES_ERROR',
                'message': str(e),
                'timestamp': datetime.now().isoformat(),
            })
            return False
    
    def save_audit_log(self, output_path: str = None) -> str:
        """Save audit log to JSON file."""
        if output_path is None:
            output_path = f"_workspaces/roadmap/reports/doc-migration-{self.timestamp}.json"
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(self.audit_log, f, indent=2)
        
        return output_path
    
    def print_summary(self) -> None:
        """Print migration summary."""
        stats = self.audit_log['stats']
        mode = "DRY RUN - NO CHANGES MADE" if self.dry_run else "EXECUTED"
        
        print("\n" + "=" * 70)
        print(f"PHASE-30 Documentation Reorganization - {mode}")
        print("=" * 70)
        print(f"Total files scanned:  {stats['total_files']}")
        print(f"Ignored files:        {stats['ignored_files']}")
        print(f"Moved files:          {stats['moved_files']}")
        print(f"Merged files:         {stats['merged_files']}")
        print(f"Deleted files:        {stats['deleted_files']}")
        print(f"Errors:               {stats['errors']}")
        print("=" * 70)
    
    def run(self, ignore_list: str, rules_list: str) -> bool:
        """Execute full migration orchestration."""
        print("Loading configuration...")
        self.load_ignore_list(ignore_list)
        self.load_categorization_rules(rules_list)
        
        print("Planning migration...")
        migration_plan = self.plan_migration()
        
        print(f"Found {self.audit_log['stats']['total_files']} files")
        print(f"  - Ignored: {self.audit_log['stats']['ignored_files']}")
        print(f"  - To migrate: {self.audit_log['stats']['moved_files']}")
        
        if self.dry_run:
            print("\n(DRY RUN MODE - No changes will be made)\n")
        
        print("Executing migration...")
        success = self.execute_migration(migration_plan)
        
        if success:
            print("Generating GitHub Pages structure...")
            self.generate_github_pages_structure()
        
        audit_log_path = self.save_audit_log()
        
        self.print_summary()
        print(f"\nAudit log: {audit_log_path}")
        
        return success


if __name__ == '__main__':
    import sys
    
    dry_run = '--dry-run' in sys.argv
    
    migrator = DocumentationMigrator(dry_run=dry_run)
    success = migrator.run(
        ignore_list='scripts/doc-ignore-list.yaml',
        rules_list='scripts/doc-categorization-rules.yaml'
    )
    
    sys.exit(0 if success else 1)
