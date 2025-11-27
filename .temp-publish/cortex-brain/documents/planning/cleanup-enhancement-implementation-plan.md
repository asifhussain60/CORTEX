# Cleanup Enhancement Implementation Plan

**Version:** 2.0  
**Purpose:** Holistic repository cleanup with production-ready validation  
**Status:** ✅ READY FOR IMPLEMENTATION

---

## 🎯 Enhancement Goals

### Current Limitations
1. **Shallow scanning** - Only specific directories checked
2. **Basic patterns** - Simple regex matching for backups
3. **No validation** - Doesn't check production readiness
4. **Limited reporting** - Basic metrics only
5. **No holistic view** - Can't see repository health

### New Capabilities
1. **Holistic scanning** - Recursive analysis of entire repository
2. **Production validation** - Detect non-production naming patterns
3. **Redundancy detection** - Find duplicates, obsolete versions
4. **Comprehensive reporting** - Detailed manifest with categorization
5. **Safe execution** - Dry-run preview, archive, rollback

---

## 📋 Phase 1: Holistic Repository Scanner

### File Categorization Engine

```python
class FileCategorizationEngine:
    """Categorize files by type, purpose, and status"""
    
    CATEGORIES = {
        'production': {
            'patterns': [r'^[a-z_]+\.py$', r'^[A-Z][a-zA-Z]+\.cs$'],
            'description': 'Production-ready files with clean naming'
        },
        'non_production': {
            'patterns': [
                r'.*(clean|modified|updated|fixed|backup|old|temp|test|demo).*',
                r'.*_v\d+.*',
                r'.*-\d{8}.*'
            ],
            'description': 'Files with temporary/versioned naming'
        },
        'redundant': {
            'patterns': [r'.*\.bak$', r'.*\.backup$', r'.*BACKUP.*'],
            'description': 'Backup and redundant files'
        },
        'deprecated': {
            'patterns': [r'.*deprecated.*', r'.*obsolete.*', r'.*old.*'],
            'description': 'Explicitly deprecated files'
        },
        'reports': {
            'patterns': [r'.*REPORT.*\.md$', r'.*SUMMARY.*\.md$', r'.*STATUS.*\.md$'],
            'description': 'Temporary reports and summaries'
        }
    }
    
    def categorize_file(self, file_path: Path) -> Dict[str, Any]:
        """Categorize a single file"""
        categories = []
        
        for category, config in self.CATEGORIES.items():
            for pattern in config['patterns']:
                if re.match(pattern, file_path.name, re.IGNORECASE):
                    categories.append({
                        'category': category,
                        'pattern': pattern,
                        'description': config['description']
                    })
        
        return {
            'path': str(file_path),
            'name': file_path.name,
            'size': file_path.stat().st_size,
            'modified': datetime.fromtimestamp(file_path.stat().st_mtime),
            'categories': categories,
            'production_ready': len(categories) == 0 or 'production' in [c['category'] for c in categories]
        }
```

### Recursive Scanner

```python
class HolisticRepositoryScanner:
    """Recursively scan entire repository"""
    
    def scan_repository(self, root: Path) -> Dict[str, Any]:
        """Perform holistic scan"""
        results = {
            'scanned_at': datetime.now(),
            'root_path': str(root),
            'statistics': {
                'total_files': 0,
                'total_directories': 0,
                'total_size_bytes': 0
            },
            'files_by_category': defaultdict(list),
            'duplicates': [],
            'orphaned_files': [],
            'bloated_files': []
        }
        
        # Scan all files recursively
        for file_path in root.rglob('*'):
            if self._is_protected(file_path):
                continue
            
            if file_path.is_file():
                results['statistics']['total_files'] += 1
                results['statistics']['total_size_bytes'] += file_path.stat().st_size
                
                # Categorize file
                file_info = self.categorization_engine.categorize_file(file_path)
                
                for category_info in file_info['categories']:
                    results['files_by_category'][category_info['category']].append(file_info)
                
                # Check for duplicates
                self._check_duplicates(file_path, results)
                
                # Check if orphaned
                if self._is_orphaned(file_path):
                    results['orphaned_files'].append(file_info)
                
                # Check if bloated
                if self._is_bloated(file_path):
                    results['bloated_files'].append(file_info)
            
            elif file_path.is_dir():
                results['statistics']['total_directories'] += 1
        
        return results
```

---

## 📋 Phase 2: Production-Ready Validation

### Naming Pattern Validator

```python
class ProductionReadinessValidator:
    """Validate files meet production naming standards"""
    
    NON_PRODUCTION_PATTERNS = [
        # Temporary prefixes/suffixes
        (r'^(temp|tmp|test|demo|scratch|draft)_.*', 'temporary_prefix'),
        (r'.*_(temp|tmp|test|demo|scratch|draft)$', 'temporary_suffix'),
        
        # Version indicators
        (r'.*_v\d+(\.\d+)*$', 'version_suffix'),
        (r'.*-v\d+(\.\d+)*\.', 'version_in_name'),
        
        # Date stamps
        (r'.*-\d{8}\.', 'date_stamp'),
        (r'.*_\d{8}\.', 'date_stamp_underscore'),
        
        # Modification indicators
        (r'.*(clean|cleaned|modified|updated|fixed|corrected|revised).*', 'modification_indicator'),
        
        # Status indicators
        (r'.*(backup|old|obsolete|deprecated|legacy|archived).*', 'status_indicator'),
        
        # Copy indicators
        (r'.*[- ](copy|Copy|COPY)(\s*\d+)?\.', 'copy_indicator'),
        
        # Summary/report files
        (r'.*(SUMMARY|STATUS|REPORT|ANALYSIS|UPDATE).*\.md$', 'temporary_report')
    ]
    
    def validate_file(self, file_path: Path) -> Dict[str, Any]:
        """Check if file meets production standards"""
        violations = []
        
        for pattern, violation_type in self.NON_PRODUCTION_PATTERNS:
            if re.match(pattern, file_path.name, re.IGNORECASE):
                violations.append({
                    'type': violation_type,
                    'pattern': pattern,
                    'severity': self._get_severity(violation_type)
                })
        
        return {
            'path': str(file_path),
            'production_ready': len(violations) == 0,
            'violations': violations,
            'recommended_name': self._suggest_production_name(file_path) if violations else None
        }
    
    def _suggest_production_name(self, file_path: Path) -> str:
        """Suggest production-ready name"""
        name = file_path.name
        
        # Remove version suffixes
        name = re.sub(r'_v\d+(\.\d+)*', '', name)
        name = re.sub(r'-v\d+(\.\d+)*', '', name)
        
        # Remove date stamps
        name = re.sub(r'[-_]\d{8}', '', name)
        
        # Remove modification indicators
        name = re.sub(r'_(clean|cleaned|modified|updated|fixed)', '', name, flags=re.IGNORECASE)
        
        # Remove status indicators
        name = re.sub(r'_(backup|old|obsolete)', '', name, flags=re.IGNORECASE)
        
        # Remove copy indicators
        name = re.sub(r'[- ](copy|Copy|COPY)(\s*\d+)?', '', name)
        
        # Clean up multiple underscores/hyphens
        name = re.sub(r'[-_]{2,}', '_', name)
        name = re.sub(r'^[-_]+|[-_]+$', '', name)
        
        return name
```

---

## 📋 Phase 3: Detailed Reporting

### Cleanup Manifest Generator

```python
class CleanupManifestGenerator:
    """Generate comprehensive cleanup manifest"""
    
    def generate_manifest(self, scan_results: Dict[str, Any]) -> Dict[str, Any]:
        """Create detailed cleanup manifest"""
        manifest = {
            'generated_at': datetime.now().isoformat(),
            'repository': scan_results['root_path'],
            
            'overview': {
                'total_files': scan_results['statistics']['total_files'],
                'total_size_mb': scan_results['statistics']['total_size_bytes'] / (1024 * 1024),
                'production_ready': len([f for f in scan_results.get('all_files', []) if f['production_ready']]),
                'requires_attention': len([f for f in scan_results.get('all_files', []) if not f['production_ready']])
            },
            
            'categories': {
                category: {
                    'count': len(files),
                    'total_size_mb': sum(f['size'] for f in files) / (1024 * 1024),
                    'files': files
                }
                for category, files in scan_results['files_by_category'].items()
            },
            
            'recommendations': self._generate_recommendations(scan_results),
            
            'proposed_actions': self._generate_proposed_actions(scan_results)
        }
        
        return manifest
    
    def _generate_recommendations(self, scan_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate cleanup recommendations"""
        recommendations = []
        
        # Check for non-production files
        non_prod_count = len(scan_results['files_by_category'].get('non_production', []))
        if non_prod_count > 0:
            recommendations.append({
                'priority': 'high',
                'category': 'naming',
                'title': f'{non_prod_count} files with non-production naming',
                'description': 'Rename or remove files with temporary/versioned naming patterns',
                'files': scan_results['files_by_category']['non_production'][:10]  # Top 10
            })
        
        # Check for redundant files
        redundant_count = len(scan_results['files_by_category'].get('redundant', []))
        if redundant_count > 0:
            recommendations.append({
                'priority': 'high',
                'category': 'redundancy',
                'title': f'{redundant_count} redundant/backup files',
                'description': 'Archive or delete backup files to free space',
                'files': scan_results['files_by_category']['redundant'][:10]
            })
        
        # Check for deprecated files
        deprecated_count = len(scan_results['files_by_category'].get('deprecated', []))
        if deprecated_count > 0:
            recommendations.append({
                'priority': 'medium',
                'category': 'deprecated',
                'title': f'{deprecated_count} deprecated files',
                'description': 'Remove explicitly deprecated files',
                'files': scan_results['files_by_category']['deprecated'][:10]
            })
        
        # Check for orphaned files
        orphaned_count = len(scan_results.get('orphaned_files', []))
        if orphaned_count > 0:
            recommendations.append({
                'priority': 'medium',
                'category': 'orphaned',
                'title': f'{orphaned_count} orphaned files',
                'description': 'No references found - consider removal',
                'files': scan_results['orphaned_files'][:10]
            })
        
        return recommendations
    
    def _generate_proposed_actions(self, scan_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate specific actions to take"""
        actions = []
        
        for category, files in scan_results['files_by_category'].items():
            if category in ['redundant', 'deprecated', 'reports']:
                for file_info in files:
                    actions.append({
                        'action': 'delete',
                        'file': file_info['path'],
                        'reason': f"Categorized as {category}",
                        'size_freed_mb': file_info['size'] / (1024 * 1024),
                        'safe_to_delete': True
                    })
            
            elif category == 'non_production':
                for file_info in files:
                    validation = self.validator.validate_file(Path(file_info['path']))
                    if validation['recommended_name']:
                        actions.append({
                            'action': 'rename',
                            'file': file_info['path'],
                            'new_name': validation['recommended_name'],
                            'reason': 'Non-production naming pattern',
                            'safe_to_rename': True
                        })
        
        return actions
```

### Report Formatter

```python
class CleanupReportFormatter:
    """Format cleanup reports for user review"""
    
    def format_manifest(self, manifest: Dict[str, Any]) -> str:
        """Format manifest as readable markdown"""
        report = []
        
        # Header
        report.append("# CORTEX Repository Cleanup Manifest")
        report.append(f"\n**Generated:** {manifest['generated_at']}")
        report.append(f"**Repository:** {manifest['repository']}")
        report.append("\n---\n")
        
        # Overview
        report.append("## 📊 Overview")
        overview = manifest['overview']
        report.append(f"\n- **Total Files:** {overview['total_files']}")
        report.append(f"- **Total Size:** {overview['total_size_mb']:.2f} MB")
        report.append(f"- **Production Ready:** {overview['production_ready']} files")
        report.append(f"- **Requires Attention:** {overview['requires_attention']} files")
        
        # Categories
        report.append("\n## 📁 File Categories")
        for category, info in manifest['categories'].items():
            report.append(f"\n### {category.replace('_', ' ').title()}")
            report.append(f"- Count: {info['count']}")
            report.append(f"- Size: {info['total_size_mb']:.2f} MB")
            report.append(f"\n<details>")
            report.append(f"<summary>Show files</summary>\n")
            for file_info in info['files'][:20]:  # Top 20
                report.append(f"- `{file_info['name']}`")
            if len(info['files']) > 20:
                report.append(f"- ... and {len(info['files']) - 20} more")
            report.append(f"</details>")
        
        # Recommendations
        report.append("\n## 💡 Recommendations")
        for rec in manifest['recommendations']:
            priority_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}[rec['priority']]
            report.append(f"\n### {priority_emoji} {rec['title']}")
            report.append(f"\n{rec['description']}")
            report.append(f"\n**Affected files:** {len(rec['files'])}")
        
        # Proposed Actions
        report.append("\n## 🎯 Proposed Actions")
        delete_actions = [a for a in manifest['proposed_actions'] if a['action'] == 'delete']
        rename_actions = [a for a in manifest['proposed_actions'] if a['action'] == 'rename']
        
        if delete_actions:
            total_freed = sum(a.get('size_freed_mb', 0) for a in delete_actions)
            report.append(f"\n### Delete ({len(delete_actions)} files, {total_freed:.2f} MB freed)")
            for action in delete_actions[:10]:
                report.append(f"- `{Path(action['file']).name}` - {action['reason']}")
            if len(delete_actions) > 10:
                report.append(f"- ... and {len(delete_actions) - 10} more")
        
        if rename_actions:
            report.append(f"\n### Rename ({len(rename_actions)} files)")
            for action in rename_actions[:10]:
                old_name = Path(action['file']).name
                new_name = action['new_name']
                report.append(f"- `{old_name}` → `{new_name}`")
            if len(rename_actions) > 10:
                report.append(f"- ... and {len(rename_actions) - 10} more")
        
        # Footer
        report.append("\n---")
        report.append("\n**⚠️ Review Carefully:** This manifest shows proposed changes.")
        report.append("Run cleanup with `--dry-run` to preview without executing.")
        
        return "\n".join(report)
```

---

## 📋 Phase 4: Safe Execution

### Safe Cleanup Executor

```python
class SafeCleanupExecutor:
    """Execute cleanup with safety checks and rollback"""
    
    def execute_cleanup(
        self, 
        manifest: Dict[str, Any], 
        dry_run: bool = True,
        require_approval: bool = True
    ) -> Dict[str, Any]:
        """Execute cleanup actions safely"""
        
        if dry_run:
            logger.info("🔍 DRY RUN MODE - No changes will be made")
            return self._preview_actions(manifest)
        
        if require_approval:
            approval = self._request_approval(manifest)
            if not approval:
                return {'aborted': True, 'reason': 'User declined approval'}
        
        # Create backup point
        backup_result = self._create_backup_point()
        
        try:
            # Execute actions
            results = {
                'started_at': datetime.now().isoformat(),
                'backup_commit': backup_result['commit_sha'],
                'actions_executed': [],
                'actions_failed': [],
                'space_freed_bytes': 0
            }
            
            # Execute delete actions
            for action in manifest['proposed_actions']:
                if action['action'] == 'delete':
                    result = self._execute_delete(action)
                    if result['success']:
                        results['actions_executed'].append(result)
                        results['space_freed_bytes'] += action.get('size_freed_mb', 0) * 1024 * 1024
                    else:
                        results['actions_failed'].append(result)
                
                elif action['action'] == 'rename':
                    result = self._execute_rename(action)
                    if result['success']:
                        results['actions_executed'].append(result)
                    else:
                        results['actions_failed'].append(result)
            
            # Commit changes
            commit_result = self._commit_cleanup(results)
            results['cleanup_commit'] = commit_result['commit_sha']
            
            results['completed_at'] = datetime.now().isoformat()
            results['success'] = len(results['actions_failed']) == 0
            
            return results
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            self._rollback_to_backup(backup_result['commit_sha'])
            raise
    
    def _create_backup_point(self) -> Dict[str, Any]:
        """Create git backup point before cleanup"""
        try:
            # Commit current state
            subprocess.run(['git', 'add', '-A'], cwd=str(self.project_root), check=True)
            
            timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
            commit_msg = f"[BACKUP] Pre-cleanup backup - {timestamp}"
            
            subprocess.run(
                ['git', 'commit', '-m', commit_msg],
                cwd=str(self.project_root),
                check=True
            )
            
            # Get commit SHA
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                check=True
            )
            
            commit_sha = result.stdout.strip()
            
            logger.info(f"✅ Backup point created: {commit_sha[:8]}")
            
            return {
                'success': True,
                'commit_sha': commit_sha,
                'timestamp': timestamp
            }
            
        except Exception as e:
            logger.error(f"Failed to create backup point: {e}")
            raise
    
    def _rollback_to_backup(self, commit_sha: str) -> None:
        """Rollback to backup point if cleanup fails"""
        try:
            logger.warning(f"⚠️ Rolling back to backup: {commit_sha[:8]}")
            
            subprocess.run(
                ['git', 'reset', '--hard', commit_sha],
                cwd=str(self.project_root),
                check=True
            )
            
            logger.info("✅ Rollback successful")
            
        except Exception as e:
            logger.error(f"❌ Rollback failed: {e}")
            raise
```

---

## 🔗 Integration Points

### Response Template Update

```yaml
cleanup_operation:
  name: Cleanup Operation (Enhanced)
  triggers:
  - cleanup
  - clean up
  - cleanup cortex
  - clean cortex
  - holistic cleanup
  - repository cleanup
  response_type: detailed
  content: |
    # 🧠 CORTEX Holistic Cleanup
    **Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX
    
    ---
    
    ## 🎯 My Understanding Of Your Request
    You want to perform a holistic cleanup of the CORTEX repository, identifying and removing:
    - Non-production files (temporary naming patterns)
    - Redundant/backup files
    - Deprecated/obsolete content
    - Orphaned files with no references
    
    ## ⚠️ Challenge
    No Challenge - Holistic cleanup will scan entire repository, categorize all files, validate production readiness, and generate detailed manifest for review before execution.
    
    ## 💬 Response
    Starting holistic repository cleanup...
    
    **Phase 1: Repository Scan** (30-60s)
    - Recursively scan all directories
    - Categorize files by type and purpose
    - Detect naming pattern violations
    - Identify redundancies and orphaned files
    
    **Phase 2: Production Validation** (10-20s)
    - Check file naming standards
    - Detect temporary/versioned patterns
    - Suggest production-ready names
    - Flag files requiring attention
    
    **Phase 3: Report Generation** (5s)
    - Comprehensive cleanup manifest
    - Categorized file listings
    - Recommended actions
    - Space savings projection
    
    **Phase 4: Safe Execution** (with approval)
    - DRY RUN: Preview all changes
    - USER APPROVAL: Review manifest
    - BACKUP: Create git backup point
    - EXECUTE: Perform cleanup
    - COMMIT: Document changes
    - ROLLBACK: Available if needed
    
    ## 📝 Your Request
    Perform holistic cleanup with production-ready validation
    
    ## 🔍 Next Steps
    
    1. **Review Manifest** - Cleanup manifest will be generated and opened in VS Code
    2. **Approve Changes** - Say "approve cleanup" to execute or "cancel cleanup" to abort
    3. **Monitor Progress** - Real-time progress shown during execution
    4. **Review Results** - Cleanup summary with space freed and actions taken
    
    **Safety Features:**
    - ✅ Dry-run preview before execution
    - ✅ Git backup before changes
    - ✅ Rollback capability if issues
    - ✅ Protected paths never touched
    - ✅ Detailed action logging
```

---

## 📊 Expected Results

### Before Cleanup
```
Total Files: 2,847
Total Size: 1.2 GB
Production Ready: 1,924 (67%)
Requires Attention: 923 (33%)

Non-Production Files: 456
Redundant/Backup: 287
Deprecated: 94
Reports/Summaries: 86
```

### After Cleanup
```
Total Files: 1,924
Total Size: 850 MB
Production Ready: 1,924 (100%)
Requires Attention: 0 (0%)

Space Freed: 350 MB
Files Removed: 467
Files Renamed: 456
```

---

## ✅ Success Criteria

1. **Complete Scan** - All directories recursively analyzed
2. **Accurate Categorization** - Files correctly categorized by type/purpose
3. **Production Validation** - All non-production naming patterns detected
4. **Detailed Manifest** - Comprehensive report with all findings
5. **Safe Execution** - Backup/rollback working correctly
6. **User Approval** - Changes require explicit approval
7. **Space Reclaimed** - Significant disk space freed (>200 MB)
8. **No Data Loss** - All important files preserved

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions)
