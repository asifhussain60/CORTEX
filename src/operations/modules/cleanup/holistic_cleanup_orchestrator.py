"""
Holistic Cleanup Orchestrator for CORTEX 3.2

Performs comprehensive repository analysis and cleanup with:
- Recursive directory scanning
- Production-ready file naming validation
- Redundancy detection and elimination
- Detailed reporting before execution
- Safe execution with backup/rollback

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions) - See LICENSE
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Set, Tuple, Optional
from dataclasses import dataclass, asdict, field
import json
import shutil
import subprocess
import logging
import re
import hashlib
from collections import defaultdict

from src.operations.base_operation_module import (
    BaseOperationModule, OperationPhase, OperationResult, 
    OperationModuleMetadata, OperationStatus
)

try:
    from .cleanup_validator import CleanupValidator
    from .cleanup_verifier import CleanupVerifier
    VALIDATION_AVAILABLE = True
except ImportError:
    VALIDATION_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Cleanup validation modules not available - validation will be skipped")

try:
    from .cleanup_test_harness import CleanupTestHarness
    TEST_HARNESS_AVAILABLE = True
except ImportError:
    TEST_HARNESS_AVAILABLE = False
    logger.warning("Cleanup test harness not available - test validation will be skipped")

try:
    from .markdown_consolidation_engine import MarkdownConsolidationEngine
    MARKDOWN_CONSOLIDATION_AVAILABLE = True
except ImportError:
    MARKDOWN_CONSOLIDATION_AVAILABLE = False
    logger.warning("Markdown consolidation engine not available - consolidation will be skipped")

logger = logging.getLogger(__name__)


@dataclass
class FileInfo:
    """Information about a file"""
    path: str
    name: str
    size: int
    modified: datetime
    categories: List[str] = field(default_factory=list)
    production_ready: bool = True
    violations: List[Dict[str, str]] = field(default_factory=list)
    recommended_name: Optional[str] = None


@dataclass
class CleanupManifest:
    """Comprehensive cleanup manifest"""
    generated_at: datetime
    repository: str
    overview: Dict[str, Any]
    categories: Dict[str, Any]
    recommendations: List[Dict[str, Any]]
    proposed_actions: List[Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['generated_at'] = self.generated_at.isoformat()
        return data


class FileCategorizationEngine:
    """Categorize files by type, purpose, and status"""
    
    CATEGORIES = {
        'production': {
            'patterns': [r'^[a-z_]+\.py$', r'^[A-Z][a-zA-Z]+\.cs$', r'^[a-z_]+\.ts$'],
            'description': 'Production-ready files with clean naming'
        },
        'non_production': {
            'patterns': [
                r'.*(clean|cleaned|modified|updated|fixed|backup|old|temp|test|demo).*',
                r'.*_v\d+.*',
                r'.*-\d{8}.*',
                r'.*-COPY.*'
            ],
            'description': 'Files with temporary/versioned naming'
        },
        'redundant': {
            'patterns': [
                r'.*\.bak$', r'.*\.backup$', r'.*BACKUP.*',
                r'.*\.old$', r'.*_old_.*'
            ],
            'description': 'Backup and redundant files'
        },
        'deprecated': {
            'patterns': [r'.*deprecated.*', r'.*obsolete.*', r'.*legacy.*'],
            'description': 'Explicitly deprecated files'
        },
        'reports': {
            'patterns': [
                r'.*REPORT.*\.md$', r'.*SUMMARY.*\.md$', 
                r'.*STATUS.*\.md$', r'.*ANALYSIS.*\.md$'
            ],
            'description': 'Temporary reports and summaries'
        }
    }
    
    def categorize_file(self, file_path: Path) -> FileInfo:
        """Categorize a single file"""
        categories = []
        
        for category, config in self.CATEGORIES.items():
            for pattern in config['patterns']:
                if re.match(pattern, file_path.name, re.IGNORECASE):
                    categories.append(category)
                    break
        
        return FileInfo(
            path=str(file_path),
            name=file_path.name,
            size=file_path.stat().st_size,
            modified=datetime.fromtimestamp(file_path.stat().st_mtime),
            categories=categories,
            production_ready=len(categories) == 0 or 'production' in categories
        )


class ProductionReadinessValidator:
    """Validate files meet production naming standards"""
    
    NON_PRODUCTION_PATTERNS = [
        # Temporary prefixes/suffixes
        (r'^(temp|tmp|test|demo|scratch|draft)_.*', 'temporary_prefix', 'high'),
        (r'.*_(temp|tmp|test|demo|scratch|draft)$', 'temporary_suffix', 'high'),
        
        # Version indicators
        (r'.*_v\d+(\.\d+)*$', 'version_suffix', 'medium'),
        (r'.*-v\d+(\.\d+)*\.', 'version_in_name', 'medium'),
        
        # Date stamps
        (r'.*-\d{8}\.', 'date_stamp', 'medium'),
        (r'.*_\d{8}\.', 'date_stamp_underscore', 'medium'),
        
        # Modification indicators
        (r'.*(clean|cleaned|modified|updated|fixed|corrected|revised).*', 'modification_indicator', 'high'),
        
        # Status indicators
        (r'.*(backup|old|obsolete|deprecated|legacy|archived).*', 'status_indicator', 'high'),
        
        # Copy indicators
        (r'.*[- ](copy|Copy|COPY)(\s*\d+)?\.', 'copy_indicator', 'high'),
        
        # Summary/report files
        (r'.*(SUMMARY|STATUS|REPORT|ANALYSIS|UPDATE).*\.md$', 'temporary_report', 'medium')
    ]
    
    def validate_file(self, file_path: Path) -> FileInfo:
        """Check if file meets production standards"""
        violations = []
        
        for pattern, violation_type, severity in self.NON_PRODUCTION_PATTERNS:
            if re.match(pattern, file_path.name, re.IGNORECASE):
                violations.append({
                    'type': violation_type,
                    'pattern': pattern,
                    'severity': severity
                })
        
        file_info = FileInfo(
            path=str(file_path),
            name=file_path.name,
            size=file_path.stat().st_size,
            modified=datetime.fromtimestamp(file_path.stat().st_mtime),
            production_ready=len(violations) == 0,
            violations=violations
        )
        
        if violations:
            file_info.recommended_name = self._suggest_production_name(file_path)
        
        return file_info
    
    def _suggest_production_name(self, file_path: Path) -> str:
        """Suggest production-ready name"""
        name = file_path.stem
        ext = file_path.suffix
        
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
        
        return name + ext


class HolisticRepositoryScanner:
    """Recursively scan entire repository"""
    
    def __init__(self, project_root: Path, protected_paths: Set[str]):
        self.project_root = Path(project_root) if isinstance(project_root, str) else project_root
        self.protected_paths = protected_paths
        self.categorization_engine = FileCategorizationEngine()
        self.validator = ProductionReadinessValidator()
    
    def scan_repository(self) -> Dict[str, Any]:
        """Perform holistic scan"""
        logger.info("Starting holistic repository scan...")
        
        results = {
            'scanned_at': datetime.now(),
            'root_path': str(self.project_root),
            'statistics': {
                'total_files': 0,
                'total_directories': 0,
                'total_size_bytes': 0
            },
            'files_by_category': defaultdict(list),
            'all_files': [],
            'duplicates': [],
            'orphaned_files': [],
            'bloated_files': []
        }
        
        # Scan all files recursively
        for file_path in self.project_root.rglob('*'):
            if self._is_protected(file_path):
                continue
            
            if file_path.is_file():
                results['statistics']['total_files'] += 1
                results['statistics']['total_size_bytes'] += file_path.stat().st_size
                
                # Categorize file
                file_info = self.categorization_engine.categorize_file(file_path)
                
                # Validate production readiness
                if not file_info.production_ready:
                    validation_info = self.validator.validate_file(file_path)
                    file_info.violations = validation_info.violations
                    file_info.recommended_name = validation_info.recommended_name
                
                results['all_files'].append(file_info)
                
                for category in file_info.categories:
                    results['files_by_category'][category].append(file_info)
                
                # Check for duplicates
                self._check_duplicates(file_path, results)
                
                # Check if bloated
                if self._is_bloated(file_path):
                    results['bloated_files'].append(file_info)
            
            elif file_path.is_dir():
                results['statistics']['total_directories'] += 1
        
        logger.info(f"Scan complete: {results['statistics']['total_files']} files, "
                   f"{results['statistics']['total_directories']} directories")
        
        return results
    
    def _is_protected(self, path: Path) -> bool:
        """Check if path is protected"""
        try:
            relative_path = path.relative_to(self.project_root)
            path_str = str(relative_path).replace('\\', '/')
            
            for protected in self.protected_paths:
                if path_str == protected.rstrip('/'):
                    return True
                if path_str.startswith(protected):
                    return True
            
            return False
            
        except ValueError:
            return True
    
    def _check_duplicates(self, file_path: Path, results: Dict[str, Any]) -> None:
        """Check for duplicate files"""
        # Simple name-based duplicate detection
        name_base = re.sub(r'[-_]?(v\d+|copy|\d{8})', '', file_path.stem.lower())
        
        for existing in results['all_files']:
            existing_base = re.sub(r'[-_]?(v\d+|copy|\d{8})', '', Path(existing.path).stem.lower())
            
            if name_base == existing_base and file_path.suffix == Path(existing.path).suffix:
                if file_path.name != Path(existing.path).name:
                    results['duplicates'].append({
                        'original': existing.path,
                        'duplicate': str(file_path),
                        'size': file_path.stat().st_size
                    })
    
    def _is_bloated(self, file_path: Path) -> bool:
        """Check if file is bloated"""
        if file_path.suffix not in ['.py', '.md', '.cs', '.ts']:
            return False
        
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            token_count = len(content) // 4  # Rough estimate
            
            # Thresholds by file type
            thresholds = {
                '.py': 5000,
                '.md': 3000,
                '.cs': 5000,
                '.ts': 4000
            }
            
            threshold = thresholds.get(file_path.suffix, 3000)
            return token_count > threshold
            
        except Exception:
            return False


class CleanupManifestGenerator:
    """Generate comprehensive cleanup manifest"""
    
    def generate_manifest(self, scan_results: Dict[str, Any]) -> CleanupManifest:
        """Create detailed cleanup manifest"""
        
        all_files = scan_results['all_files']
        production_ready = [f for f in all_files if f.production_ready]
        requires_attention = [f for f in all_files if not f.production_ready]
        
        overview = {
            'total_files': scan_results['statistics']['total_files'],
            'total_size_mb': scan_results['statistics']['total_size_bytes'] / (1024 * 1024),
            'production_ready': len(production_ready),
            'requires_attention': len(requires_attention),
            'production_ready_percent': (len(production_ready) / len(all_files) * 100) if all_files else 0
        }
        
        categories = {}
        for category, files in scan_results['files_by_category'].items():
            categories[category] = {
                'count': len(files),
                'total_size_mb': sum(f.size for f in files) / (1024 * 1024),
                'files': [asdict(f) for f in files]
            }
        
        recommendations = self._generate_recommendations(scan_results)
        proposed_actions = self._generate_proposed_actions(scan_results)
        
        return CleanupManifest(
            generated_at=datetime.now(),
            repository=scan_results['root_path'],
            overview=overview,
            categories=categories,
            recommendations=recommendations,
            proposed_actions=proposed_actions
        )
    
    def _generate_recommendations(self, scan_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate cleanup recommendations"""
        recommendations = []
        
        # Check for non-production files
        non_prod_files = scan_results['files_by_category'].get('non_production', [])
        if non_prod_files:
            recommendations.append({
                'priority': 'high',
                'category': 'naming',
                'title': f'{len(non_prod_files)} files with non-production naming',
                'description': 'Rename or remove files with temporary/versioned naming patterns',
                'affected_count': len(non_prod_files),
                'sample_files': [f.name for f in non_prod_files[:10]]
            })
        
        # Check for redundant files
        redundant_files = scan_results['files_by_category'].get('redundant', [])
        if redundant_files:
            space_freed = sum(f.size for f in redundant_files) / (1024 * 1024)
            recommendations.append({
                'priority': 'high',
                'category': 'redundancy',
                'title': f'{len(redundant_files)} redundant/backup files',
                'description': f'Archive or delete backup files to free {space_freed:.2f}MB',
                'affected_count': len(redundant_files),
                'sample_files': [f.name for f in redundant_files[:10]]
            })
        
        # Check for deprecated files
        deprecated_files = scan_results['files_by_category'].get('deprecated', [])
        if deprecated_files:
            recommendations.append({
                'priority': 'medium',
                'category': 'deprecated',
                'title': f'{len(deprecated_files)} deprecated files',
                'description': 'Remove explicitly deprecated files',
                'affected_count': len(deprecated_files),
                'sample_files': [f.name for f in deprecated_files[:10]]
            })
        
        # Check for duplicates
        if scan_results['duplicates']:
            recommendations.append({
                'priority': 'medium',
                'category': 'duplicates',
                'title': f'{len(scan_results["duplicates"])} duplicate files detected',
                'description': 'Multiple versions of same file found',
                'affected_count': len(scan_results['duplicates']),
                'sample_files': [d['duplicate'] for d in scan_results['duplicates'][:10]]
            })
        
        return recommendations
    
    def _generate_proposed_actions(self, scan_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate specific actions to take"""
        actions = []
        
        # Delete redundant, deprecated, report files
        for category in ['redundant', 'deprecated', 'reports']:
            files = scan_results['files_by_category'].get(category, [])
            for file_info in files:
                actions.append({
                    'action': 'delete',
                    'file': file_info.path,
                    'reason': f"Categorized as {category}",
                    'size_freed_mb': file_info.size / (1024 * 1024),
                    'safe_to_delete': True
                })
        
        # Rename non-production files
        non_prod_files = scan_results['files_by_category'].get('non_production', [])
        for file_info in non_prod_files:
            if file_info.recommended_name:
                actions.append({
                    'action': 'rename',
                    'file': file_info.path,
                    'new_name': file_info.recommended_name,
                    'reason': 'Non-production naming pattern',
                    'violations': file_info.violations,
                    'safe_to_rename': True
                })
        
        return actions


class HolisticCleanupOrchestrator(BaseOperationModule):
    """
    Holistic cleanup orchestrator with:
    - Recursive repository scanning
    - Production-ready validation
    - Detailed manifest generation
    - Safe execution with backup/rollback
    """
    
    def __init__(self, project_root: Path = None):
        super().__init__()
        self.project_root = Path(project_root) if project_root and isinstance(project_root, str) else (project_root or Path.cwd())
        
        # Protected paths - NEVER touch these
        self.protected_paths = {
            'src/', 'tests/', 'cortex-brain/tier1/', 'cortex-brain/tier2/',
            'cortex-brain/tier3/', 'docs/', '.git/', '.github/',
            '.vscode/', 'node_modules/', 'package.json', 'LICENSE',
            'README.md', 'requirements.txt', 'cortex.config.json'
        }
        
        # Test harness (optional)
        self.test_harness: Optional['CleanupTestHarness'] = None
        self.enable_test_validation = True  # Can be disabled via context
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Module metadata"""
        return OperationModuleMetadata(
            module_id="holistic_cleanup_orchestrator",
            name="Holistic Cleanup Orchestrator",
            description="Comprehensive repository cleanup with production validation",
            version="2.0.0",
            author="Asif Hussain",
            phase=OperationPhase.PROCESSING,
            priority=100,
            dependencies=[],
            optional=False,
            tags=['cleanup', 'maintenance', 'holistic', 'validation']
        )
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """Execute holistic cleanup"""
        dry_run = context.get('dry_run', True)
        manifest_data = context.get('manifest')
        
        try:
            logger.info("=" * 70)
            logger.info("CORTEX HOLISTIC CLEANUP ORCHESTRATOR")
            logger.info("=" * 70)
            logger.info(f"Mode: {'DRY RUN' if dry_run else 'LIVE EXECUTION'}")
            logger.info(f"Project Root: {self.project_root}")
            logger.info("")
            
            # If manifest provided, execute actions directly
            if manifest_data and not dry_run:
                return self._execute_cleanup_actions(manifest_data)
            
            # Phase 1: Holistic scan
            logger.info("Phase 1: Holistic Repository Scan")
            logger.info("-" * 70)
            
            scanner = HolisticRepositoryScanner(self.project_root, self.protected_paths)
            scan_results = scanner.scan_repository()
            
            logger.info(f"✅ Scanned {scan_results['statistics']['total_files']} files")
            logger.info("")
            
            # Phase 2: Generate manifest
            logger.info("Phase 2: Manifest Generation")
            logger.info("-" * 70)
            
            manifest_gen = CleanupManifestGenerator()
            manifest = manifest_gen.generate_manifest(scan_results)
            
            # Save manifest to file
            manifest_path = self.project_root / 'cortex-brain' / 'documents' / 'reports' / f'cleanup-manifest-{datetime.now().strftime("%Y%m%d-%H%M%S")}.json'
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest.to_dict(), f, indent=2, default=str)
            
            logger.info(f"✅ Manifest saved: {manifest_path.relative_to(self.project_root)}")
            logger.info("")
            
            # Phase 3: Generate report
            logger.info("Phase 3: Report Generation")
            logger.info("-" * 70)
            
            report = self._generate_markdown_report(manifest)
            
            report_path = self.project_root / 'cortex-brain' / 'documents' / 'reports' / f'cleanup-report-{datetime.now().strftime("%Y%m%d-%H%M%S")}.md'
            report_path.write_text(report, encoding='utf-8')
            
            logger.info(f"✅ Report saved: {report_path.relative_to(self.project_root)}")
            logger.info("")
            
            # NEW: Phase 4: Dry-Run Validation
            if VALIDATION_AVAILABLE and dry_run and len(manifest.proposed_actions) > 0:
                logger.info("Phase 4: Dry-Run Validation")
                logger.info("-" * 70)
                
                validator = CleanupValidator(self.project_root)
                validation_result = validator.validate_proposed_cleanup(manifest.to_dict())
                
                if validation_result.has_critical_errors:
                    logger.error("❌ VALIDATION FAILED - Proposed cleanup would break CORTEX")
                    logger.error("")
                    logger.error("Critical Issues:")
                    for error in validation_result.critical_errors:
                        logger.error(f"  • {error.message}")
                        logger.error(f"    File: {error.file.relative_to(self.project_root)}")
                        if error.details:
                            for key, value in error.details.items():
                                logger.error(f"    {key}: {value}")
                        logger.error("")
                    
                    # Save validation report
                    validation_report = self._generate_validation_report(validation_result)
                    validation_report_path = self.project_root / 'cortex-brain' / 'documents' / 'reports' / f'cleanup-validation-{datetime.now().strftime("%Y%m%d-%H%M%S")}.md'
                    validation_report_path.parent.mkdir(parents=True, exist_ok=True)
                    validation_report_path.write_text(validation_report, encoding='utf-8')
                    
                    logger.error(f"📄 Validation report: {validation_report_path.relative_to(self.project_root)}")
                    logger.error("")
                    logger.error("⚠️  Cleanup BLOCKED to protect CORTEX functionality")
                    logger.error("    Fix critical issues before proceeding")
                    
                    return OperationResult(
                        success=False,
                        status=OperationStatus.FAILED,
                        message=f"Cleanup validation failed: {len(validation_result.critical_errors)} critical issues",
                        data={
                            'validation_errors': [
                                {
                                    'severity': e.severity,
                                    'category': e.category,
                                    'message': e.message,
                                    'file': str(e.file),
                                    'details': e.details
                                }
                                for e in validation_result.errors
                            ],
                            'validation_report': str(validation_report_path)
                        },
                        errors=[f"{e.severity}: {e.message}" for e in validation_result.critical_errors]
                    )
                
                logger.info(f"✅ Validation passed in {validation_result.validation_time:.2f}s")
                logger.info("   Cleanup is safe to execute")
                logger.info("")
            
            # NEW: Phase 4.5: Test Harness Baseline (if enabled)
            test_baseline_captured = False
            if TEST_HARNESS_AVAILABLE and context.get('enable_test_validation', self.enable_test_validation):
                logger.info("Phase 4.5: Test Harness Baseline")
                logger.info("-" * 70)
                
                try:
                    self.test_harness = CleanupTestHarness(
                        workspace_root=self.project_root,
                        test_command=context.get('test_command', 'pytest tests/ -v --tb=short'),
                        coverage_command=context.get('coverage_command')
                    )
                    
                    baseline = self.test_harness.capture_baseline()
                    test_baseline_captured = True
                    
                    logger.info(f"✅ Test baseline captured: {baseline.passed_tests}/{baseline.total_tests} passing")
                    logger.info(f"   Coverage: {baseline.coverage_percent:.1f}%")
                    
                    if baseline.failed_tests > 0:
                        logger.warning(f"⚠️  Baseline has {baseline.failed_tests} failing tests")
                        logger.warning("   Cleanup may introduce additional failures")
                    
                    logger.info("")
                    
                except Exception as e:
                    logger.warning(f"⚠️  Could not capture test baseline: {e}")
                    logger.warning("   Proceeding without test validation")
                    self.test_harness = None
                    logger.info("")
            
            # Phase 5: Summary
            logger.info("=" * 70)
            logger.info("CLEANUP MANIFEST SUMMARY")
            logger.info("=" * 70)
            logger.info(f"Total Files: {manifest.overview['total_files']}")
            logger.info(f"Total Size: {manifest.overview['total_size_mb']:.2f} MB")
            logger.info(f"Production Ready: {manifest.overview['production_ready']} ({manifest.overview['production_ready_percent']:.1f}%)")
            logger.info(f"Requires Attention: {manifest.overview['requires_attention']}")
            logger.info(f"\nProposed Actions: {len(manifest.proposed_actions)}")
            logger.info(f"  - Delete: {sum(1 for a in manifest.proposed_actions if a['action'] == 'delete')}")
            logger.info(f"  - Rename: {sum(1 for a in manifest.proposed_actions if a['action'] == 'rename')}")
            logger.info("")
            
            if dry_run:
                logger.info("🔍 DRY RUN COMPLETE - No changes made")
                logger.info(f"📄 Review manifest: {report_path.relative_to(self.project_root)}")
                logger.info("To execute cleanup, say: 'approve cleanup' or run with dry_run=False")
            
            return OperationResult(
                success=True,
                status=OperationStatus.SUCCESS,
                message=f"Holistic cleanup manifest generated: {manifest.overview['requires_attention']} files require attention",
                data={
                    'manifest': manifest.to_dict(),
                    'manifest_path': str(manifest_path),
                    'report_path': str(report_path),
                    'dry_run': dry_run,
                    'statistics': scan_results['statistics']
                }
            )
            
        except Exception as e:
            logger.error(f"Holistic cleanup failed: {e}", exc_info=True)
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Cleanup failed: {str(e)}",
                data={'error': str(e)}
            )
    
    def _execute_cleanup_actions(self, manifest_data: Dict[str, Any]) -> OperationResult:
        """Execute actual cleanup actions from manifest with category-level validation"""
        try:
            logger.info("Phase 4: Executing Cleanup Actions")
            logger.info("-" * 70)
            
            proposed_actions = manifest_data.get('proposed_actions', [])
            
            # Group actions by category for batch validation
            actions_by_category = defaultdict(list)
            for action in proposed_actions:
                category = action.get('category', 'other')
                actions_by_category[category].append(action)
            
            files_deleted = 0
            files_renamed = 0
            space_freed = 0.0
            errors = []
            rollback_occurred = False
            
            # Process each category with test validation
            for category, category_actions in actions_by_category.items():
                logger.info(f"\n📦 Processing category: {category} ({len(category_actions)} actions)")
                logger.info("-" * 50)
                
                # Backup files before deletion
                if self.test_harness:
                    files_to_backup = [Path(a['file']) for a in category_actions if Path(a['file']).exists()]
                    backup_path = self.test_harness.backup_files(files_to_backup)
                else:
                    backup_path = None
                
                # Execute actions for this category
                category_deleted = 0
                category_renamed = 0
                category_space_freed = 0.0
                
                for action in category_actions:
                    try:
                        file_path = Path(action['file'])
                        
                        if not file_path.exists():
                            logger.warning(f"File not found, skipping: {file_path}")
                            continue
                        
                        if action['action'] == 'delete':
                            # Delete file
                            file_size_mb = file_path.stat().st_size / (1024 * 1024)
                            file_path.unlink()
                            category_deleted += 1
                            category_space_freed += file_size_mb
                            logger.info(f"  ✅ Deleted: {file_path.name} ({file_size_mb:.2f} MB)")
                            
                        elif action['action'] == 'rename':
                            # Rename file
                            new_name = action.get('new_name')
                            if new_name:
                                new_path = file_path.parent / new_name
                                if not new_path.exists():
                                    file_path.rename(new_path)
                                    category_renamed += 1
                                    logger.info(f"  ✅ Renamed: {file_path.name} → {new_name}")
                                else:
                                    logger.warning(f"Target exists, skipping rename: {new_name}")
                            
                    except Exception as e:
                        error_msg = f"Failed to process {action['file']}: {str(e)}"
                        errors.append(error_msg)
                        logger.error(f"  ❌ {error_msg}")
                
                # Validate with test harness after category cleanup
                if self.test_harness and (category_deleted > 0 or category_renamed > 0):
                    logger.info(f"\n🧪 Validating category: {category}")
                    
                    validation_result = self.test_harness.validate_category(category)
                    
                    if validation_result.has_failures():
                        # Rollback this category
                        logger.error(f"❌ Test validation failed for category: {category}")
                        logger.error("   Rolling back changes...")
                        
                        if backup_path and self.test_harness.rollback_category(backup_path):
                            logger.warning(f"✅ Rollback successful for {category}")
                            rollback_occurred = True
                            
                            # Don't count these as successful actions
                            errors.append(f"Category {category} rolled back due to test failures")
                        else:
                            logger.error(f"❌ Rollback failed for {category}")
                            errors.append(f"Failed to rollback category {category}")
                            
                            # Still count the actions since we can't undo them
                            files_deleted += category_deleted
                            files_renamed += category_renamed
                            space_freed += category_space_freed
                        
                        # Stop processing remaining categories
                        logger.error("\n⚠️  Cleanup aborted due to test failures")
                        logger.error("   Remaining categories will not be processed")
                        break
                    else:
                        # Validation passed, keep the changes
                        files_deleted += category_deleted
                        files_renamed += category_renamed
                        space_freed += category_space_freed
                        logger.info(f"✅ Validation passed for {category}")
                else:
                    # No test harness, just count the actions
                    files_deleted += category_deleted
                    files_renamed += category_renamed
                    space_freed += category_space_freed
            
            logger.info("")
            logger.info("=" * 70)
            logger.info("CLEANUP EXECUTION COMPLETE")
            logger.info("=" * 70)
            logger.info(f"Files Deleted: {files_deleted}")
            logger.info(f"Files Renamed: {files_renamed}")
            logger.info(f"Space Freed: {space_freed:.2f} MB")
            if errors:
                logger.warning(f"Errors: {len(errors)}")
            if rollback_occurred:
                logger.warning("⚠️  Some categories were rolled back due to test failures")
            logger.info("")
            
            # Generate test validation report if harness was used
            if self.test_harness:
                validation_report = self.test_harness.generate_validation_report()
                validation_report_path = self.project_root / 'cortex-brain' / 'documents' / 'reports' / f'cleanup-test-validation-{datetime.now().strftime("%Y%m%d-%H%M%S")}.md'
                validation_report_path.parent.mkdir(parents=True, exist_ok=True)
                validation_report_path.write_text(validation_report, encoding='utf-8')
                logger.info(f"📄 Test validation report: {validation_report_path.relative_to(self.project_root)}")
                logger.info("")
            
            # NEW: Post-Cleanup Verification
            if VALIDATION_AVAILABLE:
                logger.info("")
                verifier = CleanupVerifier(self.project_root)
                verification_result = verifier.verify_cleanup(use_health_validator=True)
                
                if not verification_result.passed:
                    logger.error("❌ POST-CLEANUP VERIFICATION FAILED")
                    logger.error("   Some CORTEX functionality may be compromised")
                    logger.warning("   Manual review recommended")
                    
                    return OperationResult(
                        success=False,
                        status=OperationStatus.WARNING,
                        message="Cleanup completed but verification detected issues",
                        data={
                            'execution_summary': {
                                'files_deleted': files_deleted,
                                'files_renamed': files_renamed,
                                'space_freed_mb': space_freed,
                                'errors_count': len(errors)
                            },
                            'verification_checks': verification_result.checks,
                            'verification_passed': False
                        },
                        errors=errors if errors else [],
                        warnings=["Post-cleanup verification failed - manual review recommended"]
                    )
            
            return OperationResult(
                success=True,
                status=OperationStatus.SUCCESS,
                message=f"Cleanup executed: {files_deleted} deleted, {files_renamed} renamed, {space_freed:.2f} MB freed",
                data={
                    'execution_summary': {
                        'files_deleted': files_deleted,
                        'files_renamed': files_renamed,
                        'space_freed_mb': space_freed,
                        'errors_count': len(errors)
                    }
                },
                errors=errors if errors else []
            )
            
        except Exception as e:
            logger.error(f"Cleanup execution failed: {e}", exc_info=True)
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Cleanup execution failed: {str(e)}",
                data={'error': str(e)}
            )
    
    def execute_markdown_consolidation(
        self,
        documents_root: Optional[Path] = None,
        dry_run: bool = True
    ) -> OperationResult:
        """
        Execute markdown file consolidation.
        
        Args:
            documents_root: Root directory for documents (default: cortex-brain/documents)
            dry_run: If True, only preview changes
            
        Returns:
            OperationResult with consolidation report
        """
        if not MARKDOWN_CONSOLIDATION_AVAILABLE:
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message="Markdown consolidation engine not available",
                data={'error': 'Module not imported'}
            )
        
        try:
            logger.info("=" * 70)
            logger.info("MARKDOWN CONSOLIDATION")
            logger.info("=" * 70)
            logger.info(f"Mode: {'DRY RUN' if dry_run else 'LIVE EXECUTION'}")
            logger.info("")
            
            documents_root = documents_root or (self.project_root / 'cortex-brain' / 'documents')
            
            if not documents_root.exists():
                return OperationResult(
                    success=False,
                    status=OperationStatus.FAILED,
                    message=f"Documents directory not found: {documents_root}",
                    data={'error': 'Directory not found'}
                )
            
            # Initialize engine
            engine = MarkdownConsolidationEngine(
                documents_root=documents_root,
                archive_retention_days=30
            )
            
            # Phase 1: Discovery
            logger.info("Phase 1: File Discovery")
            logger.info("-" * 70)
            discovered = engine.discover_files()
            logger.info("")
            
            # Phase 2: Analysis
            logger.info("Phase 2: Consolidation Analysis")
            logger.info("-" * 70)
            rules = engine.analyze_consolidation_opportunities()
            logger.info("")
            
            # Phase 3: Execution
            logger.info("Phase 3: Consolidation Execution")
            logger.info("-" * 70)
            report = engine.execute_consolidation(rules=rules, dry_run=dry_run)
            logger.info("")
            
            # Save report
            report_path = self.project_root / 'cortex-brain' / 'documents' / 'reports' / f'markdown-consolidation-{datetime.now().strftime("%Y%m%d-%H%M%S")}.md'
            report_path.parent.mkdir(parents=True, exist_ok=True)
            
            report_content = self._generate_consolidation_report(report)
            report_path.write_text(report_content, encoding='utf-8')
            
            logger.info("=" * 70)
            logger.info("CONSOLIDATION SUMMARY")
            logger.info("=" * 70)
            logger.info(f"Files: {report.files_before} → {report.files_after} ({report.files_before - report.files_after} reduced)")
            logger.info(f"Size: {report.size_before_mb:.2f} MB → {report.size_after_mb:.2f} MB")
            logger.info(f"Reduction: {((report.files_before - report.files_after) / report.files_before * 100) if report.files_before > 0 else 0:.1f}%")
            logger.info(f"Archived: {len(report.archived_files)} files")
            logger.info(f"Execution Time: {report.execution_time:.2f}s")
            logger.info("")
            
            if dry_run:
                logger.info("🔍 DRY RUN COMPLETE - No changes made")
                logger.info(f"📄 Review report: {report_path.relative_to(self.project_root)}")
                logger.info("To execute, run with dry_run=False or say 'approve consolidation'")
            
            return OperationResult(
                success=True,
                status=OperationStatus.SUCCESS,
                message=f"Markdown consolidation {'preview' if dry_run else 'complete'}: {report.files_before - report.files_after} files reduced",
                data={
                    'report': report.to_dict(),
                    'report_path': str(report_path),
                    'dry_run': dry_run
                }
            )
            
        except Exception as e:
            logger.error(f"Markdown consolidation failed: {e}", exc_info=True)
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Consolidation failed: {str(e)}",
                data={'error': str(e)}
            )
    
    def _generate_markdown_report(self, manifest: CleanupManifest) -> str:
        """Generate markdown report"""
        lines = []
        
        # Header
        lines.append("# CORTEX Holistic Cleanup Manifest")
        lines.append(f"\n**Generated:** {manifest.generated_at.isoformat()}")
        lines.append(f"**Repository:** {manifest.repository}")
        lines.append("\n---\n")
        
        # Overview
        lines.append("## 📊 Overview")
        lines.append(f"\n- **Total Files:** {manifest.overview['total_files']}")
        lines.append(f"- **Total Size:** {manifest.overview['total_size_mb']:.2f} MB")
        lines.append(f"- **Production Ready:** {manifest.overview['production_ready']} files ({manifest.overview['production_ready_percent']:.1f}%)")
        lines.append(f"- **Requires Attention:** {manifest.overview['requires_attention']} files")
        
        # Categories
        lines.append("\n## 📁 File Categories\n")
        for category, info in manifest.categories.items():
            lines.append(f"### {category.replace('_', ' ').title()}")
            lines.append(f"- **Count:** {info['count']}")
            lines.append(f"- **Size:** {info['total_size_mb']:.2f} MB")
            lines.append(f"\n<details>")
            lines.append(f"<summary>Show files ({min(20, len(info['files']))} of {len(info['files'])})</summary>\n")
            for file_info in info['files'][:20]:
                lines.append(f"- `{file_info['name']}` ({file_info['size'] / 1024:.1f} KB)")
            if len(info['files']) > 20:
                lines.append(f"\n... and {len(info['files']) - 20} more")
            lines.append("</details>\n")
        
        # Recommendations
        lines.append("\n## 💡 Recommendations\n")
        for rec in manifest.recommendations:
            priority_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}[rec['priority']]
            lines.append(f"### {priority_emoji} {rec['title']}")
            lines.append(f"\n{rec['description']}")
            lines.append(f"\n**Affected files:** {rec['affected_count']}")
            if 'sample_files' in rec:
                lines.append("\n**Sample files:**")
                for fname in rec['sample_files'][:5]:
                    lines.append(f"- `{fname}`")
            lines.append("")
        
        # Proposed Actions
        lines.append("\n## 🎯 Proposed Actions\n")
        
        delete_actions = [a for a in manifest.proposed_actions if a['action'] == 'delete']
        rename_actions = [a for a in manifest.proposed_actions if a['action'] == 'rename']
        
        if delete_actions:
            total_freed = sum(a.get('size_freed_mb', 0) for a in delete_actions)
            lines.append(f"### Delete ({len(delete_actions)} files, {total_freed:.2f} MB freed)\n")
            for action in delete_actions[:15]:
                fname = Path(action['file']).name
                size_mb = action.get('size_freed_mb', 0)
                lines.append(f"- `{fname}` ({size_mb:.2f} MB) - {action['reason']}")
            if len(delete_actions) > 15:
                lines.append(f"\n... and {len(delete_actions) - 15} more")
            lines.append("")
        
        if rename_actions:
            lines.append(f"### Rename ({len(rename_actions)} files)\n")
            for action in rename_actions[:15]:
                old_name = Path(action['file']).name
                new_name = action['new_name']
                lines.append(f"- `{old_name}` → `{new_name}`")
            if len(rename_actions) > 15:
                lines.append(f"\n... and {len(rename_actions) - 15} more")
            lines.append("")
        
        # Footer
        lines.append("\n---")
        lines.append("\n**⚠️ Review Carefully:** This manifest shows proposed changes.")
        lines.append("To execute cleanup, say: **'approve cleanup'** or run with `dry_run=False`")
        
        return "\n".join(lines)
    
    def _generate_validation_report(self, validation_result) -> str:
        """Generate markdown validation report"""
        lines = []
        
        lines.append("# CORTEX Cleanup Validation Report")
        lines.append("")
        lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Validation Type:** Pre-Cleanup Dry-Run")
        lines.append(f"**Result:** {'✅ PASSED' if validation_result.passed else '❌ FAILED'}")
        lines.append(f"**Validation Time:** {validation_result.validation_time:.2f} seconds")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        if validation_result.critical_errors:
            lines.append("## ⚠️ Critical Issues (MUST FIX)")
            lines.append("")
            
            for i, error in enumerate(validation_result.critical_errors, 1):
                lines.append(f"### Issue {i}: {error.category}")
                lines.append(f"**File:** `{error.file.relative_to(self.project_root)}`")
                lines.append(f"**Problem:** {error.message}")
                lines.append("")
                
                if error.details:
                    lines.append("**Details:**")
                    for key, value in error.details.items():
                        if isinstance(value, list):
                            lines.append(f"- **{key}:**")
                            for item in value[:10]:  # Limit to first 10
                                lines.append(f"  - {item}")
                            if len(value) > 10:
                                lines.append(f"  - ... and {len(value) - 10} more")
                        else:
                            lines.append(f"- **{key}:** {value}")
                    lines.append("")
                
                lines.append(f"**Impact:** {error.severity}")
                lines.append("")
        
        if validation_result.errors and not validation_result.critical_errors:
            lines.append("## ⚠️ Issues Detected")
            lines.append("")
            for error in validation_result.errors:
                lines.append(f"- **{error.severity}**: {error.message} (`{error.file.name}`)")
            lines.append("")
        
        if validation_result.passed:
            lines.append("## ✅ Validation Passed")
            lines.append("")
            lines.append("All validation checks passed successfully. Cleanup is safe to execute.")
            lines.append("")
        else:
            lines.append("## 🚫 Cleanup Blocked")
            lines.append("")
            lines.append("Cleanup has been blocked to protect CORTEX functionality.")
            lines.append("Please review and fix the critical issues listed above before proceeding.")
            lines.append("")
        
        return "\n".join(lines)

    def _generate_consolidation_report(self, report) -> str:
        """Generate markdown consolidation report"""
        from .markdown_consolidation_engine import ConsolidationReport
        
        lines = []
        
        # Header
        lines.append("# Markdown Consolidation Report")
        lines.append("")
        lines.append(f"**Generated:** {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Execution Time:** {report.execution_time:.2f}s")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # Summary
        lines.append("## 📊 Summary")
        lines.append("")
        lines.append(f"- **Files Before:** {report.files_before}")
        lines.append(f"- **Files After:** {report.files_after}")
        lines.append(f"- **Reduction:** {report.files_before - report.files_after} files ({((report.files_before - report.files_after) / report.files_before * 100) if report.files_before > 0 else 0:.1f}%)")
        lines.append(f"- **Size Before:** {report.size_before_mb:.2f} MB")
        lines.append(f"- **Size After:** {report.size_after_mb:.2f} MB")
        lines.append(f"- **Archived Files:** {len(report.archived_files)}")
        lines.append("")
        
        # Rules Applied
        lines.append("## 📋 Rules Applied")
        lines.append("")
        
        if not report.rules_applied:
            lines.append("No consolidation rules were applied.")
        else:
            for i, rule in enumerate(report.rules_applied, 1):
                lines.append(f"### Rule {i}: {rule.name}")
                lines.append("")
                lines.append(f"- **Action:** {rule.action.replace('_', ' ').title()}")
                lines.append(f"- **Pattern:** `{rule.pattern}`")
                lines.append(f"- **Files Affected:** {len(rule.file_paths)}")
                if rule.target_filename:
                    lines.append(f"- **Target File:** `{rule.target_filename}`")
                lines.append(f"- **Estimated Reduction:** {rule.estimated_reduction} files")
                lines.append("")
                
                if rule.file_paths and len(rule.file_paths) <= 10:
                    lines.append("**Files:**")
                    for file_path in rule.file_paths:
                        lines.append(f"- `{file_path.name}`")
                    lines.append("")
                elif rule.file_paths:
                    lines.append(f"**Files:** {len(rule.file_paths)} files (first 5 shown)")
                    for file_path in rule.file_paths[:5]:
                        lines.append(f"- `{file_path.name}`")
                    lines.append(f"- ... and {len(rule.file_paths) - 5} more")
                    lines.append("")
        
        # Errors
        if report.errors:
            lines.append("## ❌ Errors")
            lines.append("")
            for error in report.errors:
                lines.append(f"- {error}")
            lines.append("")
        
        # Footer
        lines.append("---")
        lines.append("")
        lines.append("**Archive Location:** `.archive/` in documents root")
        lines.append(f"**Retention Policy:** {30} days")
        lines.append("")
        
        return "\n".join(lines)

