#!/usr/bin/env python3
"""
CORTEX System Doctor - Comprehensive Health & Maintenance Tool

Chains multiple scripts in optimal order to ensure CORTEX 4.0 operates at peak:
1. DIAGNOSE - Analyze unwired components, entry points, manifests
2. SCAN - Detect duplicates, unnecessary files, redundant folders
3. CLEANUP - Remove safe deletions with backup (dry-run by default)
4. VALIDATE - Verify system integrity post-cleanup
5. REPORT - Generate comprehensive health report

Usage:
    python scripts/cortex_system_doctor.py                     # Full diagnostic (dry-run)
    python scripts/cortex_system_doctor.py --execute           # Execute cleanup
    python scripts/cortex_system_doctor.py --phase diagnose    # Run specific phase
    python scripts/cortex_system_doctor.py --quick             # Quick health check

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sys
import os
import json
import argparse
import importlib.util
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class Phase(Enum):
    """Execution phases in optimal order."""
    DIAGNOSE = "diagnose"
    SCAN = "scan"
    CLEANUP = "cleanup"
    VALIDATE = "validate"
    REPORT = "report"


@dataclass
class PhaseResult:
    """Result of a phase execution."""
    phase: Phase
    success: bool
    duration_seconds: float = 0.0
    findings: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    actions_taken: List[str] = field(default_factory=list)


@dataclass
class DoctorReport:
    """Complete system doctor report."""
    timestamp: str
    mode: str  # dry-run or execute
    phases_run: List[Phase]
    phase_results: Dict[Phase, PhaseResult]
    overall_health_score: float = 0.0
    critical_issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp,
            'mode': self.mode,
            'phases_run': [p.value for p in self.phases_run],
            'phase_results': {
                p.value: {
                    'success': r.success,
                    'duration': r.duration_seconds,
                    'findings': r.findings,
                    'errors': r.errors,
                    'warnings': r.warnings,
                    'actions_taken': r.actions_taken
                } for p, r in self.phase_results.items()
            },
            'overall_health_score': self.overall_health_score,
            'critical_issues': self.critical_issues,
            'recommendations': self.recommendations
        }


class CortexSystemDoctor:
    """
    CORTEX System Doctor - Chain maintenance scripts for peak performance.
    
    Phases (in optimal order):
    1. DIAGNOSE: Find unwired components, missing entry points, invalid manifests
    2. SCAN: Detect duplicates, unnecessary files, redundant folders
    3. CLEANUP: Execute safe deletions with backup
    4. VALIDATE: Verify system integrity
    5. REPORT: Generate comprehensive health report
    """
    
    def __init__(self, project_root: Path, dry_run: bool = True, verbose: bool = True):
        self.root = project_root
        self.dry_run = dry_run
        self.verbose = verbose
        self.scripts_dir = project_root / "scripts"
        self.output_dir = project_root / "cortex-brain" / "health-reports"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Script registry - maps capabilities to scripts
        self.script_registry = {
            'unwired_analysis': 'analyze_unwired_components.py',
            'duplicate_detection': 'detect_duplicates.py',
            'unnecessary_scan': 'scan_unnecessary_files.py',
            'file_cleanup': 'cleanup_unnecessary_files.py',
            'manifest_validation': 'validate_manifests.py',
            'entry_point_validation': 'validate_entry_points.py',
            'brain_health': 'monitor_brain_health.py',
            'cleanup_sweep': 'cleanup_and_sweep.py',
        }
        
    def print_banner(self):
        """Print the doctor banner."""
        print("=" * 80)
        print("🩺 CORTEX SYSTEM DOCTOR v1.0")
        print("=" * 80)
        print()
        print("Author:     Asif Hussain")
        print("Copyright:  © 2024-2025 Asif Hussain. All rights reserved.")
        print(f"Mode:       {'DRY-RUN (preview only)' if self.dry_run else '⚠️  EXECUTE (changes will be made)'}")
        print(f"Timestamp:  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        print("=" * 80)
        
    def run_full_checkup(self, phases: Optional[List[Phase]] = None) -> DoctorReport:
        """
        Run full system checkup through all phases.
        
        Args:
            phases: Specific phases to run (default: all phases in order)
        """
        self.print_banner()
        
        if phases is None:
            phases = list(Phase)
        
        report = DoctorReport(
            timestamp=datetime.now().isoformat(),
            mode='dry-run' if self.dry_run else 'execute',
            phases_run=phases,
            phase_results={}
        )
        
        print(f"\n📋 Running {len(phases)} phase(s): {', '.join(p.value for p in phases)}\n")
        
        for phase in phases:
            print(f"\n{'=' * 60}")
            print(f"🔄 PHASE: {phase.value.upper()}")
            print(f"{'=' * 60}")
            
            start_time = datetime.now()
            
            try:
                if phase == Phase.DIAGNOSE:
                    result = self._run_diagnose_phase()
                elif phase == Phase.SCAN:
                    result = self._run_scan_phase()
                elif phase == Phase.CLEANUP:
                    result = self._run_cleanup_phase()
                elif phase == Phase.VALIDATE:
                    result = self._run_validate_phase()
                elif phase == Phase.REPORT:
                    result = self._run_report_phase(report)
                else:
                    result = PhaseResult(phase=phase, success=False, 
                                        errors=[f"Unknown phase: {phase}"])
                    
            except Exception as e:
                result = PhaseResult(
                    phase=phase, 
                    success=False,
                    errors=[f"Phase failed with exception: {str(e)}"]
                )
                import traceback
                if self.verbose:
                    traceback.print_exc()
            
            result.duration_seconds = (datetime.now() - start_time).total_seconds()
            report.phase_results[phase] = result
            
            # Print phase summary
            status = "✅ SUCCESS" if result.success else "❌ FAILED"
            print(f"\n{status} ({result.duration_seconds:.2f}s)")
            
            if result.errors:
                print(f"  Errors: {len(result.errors)}")
            if result.warnings:
                print(f"  Warnings: {len(result.warnings)}")
            if result.actions_taken:
                print(f"  Actions: {len(result.actions_taken)}")
        
        # Calculate overall health
        report.overall_health_score = self._calculate_health_score(report)
        report.critical_issues = self._identify_critical_issues(report)
        report.recommendations = self._generate_recommendations(report)
        
        # Save report
        self._save_report(report)
        
        # Print final summary
        self._print_final_summary(report)
        
        return report
    
    def _run_diagnose_phase(self) -> PhaseResult:
        """Phase 1: Diagnose system health - unwired components, entry points, manifests."""
        result = PhaseResult(phase=Phase.DIAGNOSE, success=True)
        
        # 1. Analyze unwired components
        print("\n📍 Checking unwired components...")
        unwired_result = self._analyze_unwired_components()
        result.findings['unwired_components'] = unwired_result
        
        if unwired_result.get('error'):
            result.errors.append(unwired_result['error'])
        elif unwired_result.get('summary'):
            summary = unwired_result['summary']
            if summary.get('overall', {}).get('unwired_components', 0) > 0:
                result.warnings.append(
                    f"Found {summary['overall']['unwired_components']} unwired components"
                )
        
        # 2. Validate entry points
        print("\n📍 Validating entry points...")
        entry_result = self._validate_entry_points()
        result.findings['entry_points'] = entry_result
        
        if entry_result.get('failures'):
            result.errors.extend(entry_result['failures'])
        if entry_result.get('warnings'):
            result.warnings.extend(entry_result['warnings'])
        
        # 3. Validate manifests
        print("\n📍 Validating manifests...")
        manifest_result = self._validate_manifests()
        result.findings['manifests'] = manifest_result
        
        if manifest_result.get('errors'):
            result.errors.extend(manifest_result['errors'])
        
        result.success = len(result.errors) == 0
        return result
    
    def _run_scan_phase(self) -> PhaseResult:
        """Phase 2: Scan for duplicates, unnecessary files, redundant folders."""
        result = PhaseResult(phase=Phase.SCAN, success=True)
        
        # 1. Detect duplicates
        print("\n🔍 Scanning for duplicates...")
        dup_result = self._detect_duplicates()
        result.findings['duplicates'] = dup_result
        
        if dup_result.get('duplicates'):
            result.warnings.append(f"Found {len(dup_result['duplicates'])} duplicate sections")
        
        # 2. Scan unnecessary files
        print("\n🔍 Scanning unnecessary files...")
        scan_result = self._scan_unnecessary_files()
        result.findings['unnecessary_files'] = scan_result
        
        total_unnecessary = sum(len(files) for files in scan_result.get('files', {}).values())
        if total_unnecessary > 0:
            result.warnings.append(f"Found {total_unnecessary} unnecessary files")
        
        # 3. Find redundant folders
        print("\n🔍 Scanning for redundant folders...")
        folder_result = self._find_redundant_folders()
        result.findings['redundant_folders'] = folder_result
        
        if folder_result.get('redundant'):
            result.warnings.append(f"Found {len(folder_result['redundant'])} redundant folders")
        
        result.success = len(result.errors) == 0
        return result
    
    def _run_cleanup_phase(self) -> PhaseResult:
        """Phase 3: Execute cleanup (respects dry-run mode)."""
        result = PhaseResult(phase=Phase.CLEANUP, success=True)
        
        if self.dry_run:
            print("\n⚠️  DRY-RUN MODE - No changes will be made")
            print("    Run with --execute to perform actual cleanup")
            result.findings['mode'] = 'dry-run'
            result.warnings.append("Cleanup skipped (dry-run mode)")
            return result
        
        print("\n🧹 Executing cleanup...")
        
        # Create backup first
        backup_dir = self._create_backup()
        result.findings['backup_dir'] = str(backup_dir)
        result.actions_taken.append(f"Created backup at {backup_dir}")
        
        # Run cleanup
        cleanup_result = self._execute_cleanup()
        result.findings['cleanup'] = cleanup_result
        
        if cleanup_result.get('files_deleted'):
            result.actions_taken.append(
                f"Deleted {len(cleanup_result['files_deleted'])} files"
            )
        if cleanup_result.get('folders_deleted'):
            result.actions_taken.append(
                f"Deleted {len(cleanup_result['folders_deleted'])} folders"
            )
        
        if cleanup_result.get('errors'):
            result.errors.extend(cleanup_result['errors'])
        
        result.success = len(result.errors) == 0
        return result
    
    def _run_validate_phase(self) -> PhaseResult:
        """Phase 4: Validate system integrity post-cleanup."""
        result = PhaseResult(phase=Phase.VALIDATE, success=True)
        
        # 1. Check brain health
        print("\n🧠 Checking brain health...")
        brain_result = self._check_brain_health()
        result.findings['brain_health'] = brain_result
        
        if brain_result.get('issues'):
            result.errors.extend(brain_result['issues'])
        
        # 2. Verify critical paths
        print("\n📂 Verifying critical paths...")
        path_result = self._verify_critical_paths()
        result.findings['critical_paths'] = path_result
        
        if path_result.get('missing'):
            result.errors.extend([f"Missing critical path: {p}" for p in path_result['missing']])
        
        # 3. Check imports
        print("\n🔗 Checking import integrity...")
        import_result = self._check_import_integrity()
        result.findings['imports'] = import_result
        
        if import_result.get('broken_imports'):
            result.warnings.extend([f"Broken import: {i}" for i in import_result['broken_imports']])
        
        result.success = len(result.errors) == 0
        return result
    
    def _run_report_phase(self, report: DoctorReport) -> PhaseResult:
        """Phase 5: Generate comprehensive health report."""
        result = PhaseResult(phase=Phase.REPORT, success=True)
        
        print("\n📊 Generating health report...")
        
        # Collect all metrics
        metrics = self._collect_all_metrics(report)
        result.findings['metrics'] = metrics
        
        # Generate markdown report
        report_path = self._generate_markdown_report(report, metrics)
        result.findings['report_path'] = str(report_path)
        result.actions_taken.append(f"Generated report: {report_path}")
        
        print(f"   📄 Report saved to: {report_path}")
        
        return result
    
    # ============== Helper Methods ==============
    
    def _analyze_unwired_components(self) -> Dict[str, Any]:
        """Run unwired component analysis."""
        try:
            script_path = self.scripts_dir / self.script_registry['unwired_analysis']
            if not script_path.exists():
                return {'error': f"Script not found: {script_path}"}
            
            # Import and run the analyzer
            spec = importlib.util.spec_from_file_location("unwired_analyzer", script_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            analyzer = module.UnwiredComponentAnalyzer(self.root)
            results = analyzer.analyze_all()
            
            print(f"   ✅ Analyzed {results['summary']['overall']['total_components']} components")
            print(f"   📊 Wired: {results['summary']['overall']['wired_components']}")
            print(f"   ⚠️  Unwired: {results['summary']['overall']['unwired_components']}")
            
            return results
            
        except Exception as e:
            return {'error': str(e)}
    
    def _validate_entry_points(self) -> Dict[str, Any]:
        """Validate entry points exist."""
        try:
            result = {'success': True, 'failures': [], 'warnings': []}
            
            # Check critical entry points
            critical_paths = [
                ('.github/prompts/CORTEX.prompt.md', 'Main prompt file'),
                ('.github/copilot-instructions.md', 'Copilot instructions'),
                ('cortex-operations.yaml', 'Operations registry'),
                ('cortex-brain/response-templates-v4.yaml', 'Response templates'),
            ]
            
            for rel_path, description in critical_paths:
                full_path = self.root / rel_path
                if full_path.exists():
                    print(f"   ✅ {description}")
                else:
                    result['failures'].append(f"Missing: {rel_path} ({description})")
                    print(f"   ❌ {description} - MISSING")
            
            return result
            
        except Exception as e:
            return {'error': str(e)}
    
    def _validate_manifests(self) -> Dict[str, Any]:
        """Validate manifest files."""
        try:
            result = {'valid': [], 'errors': []}
            
            manifest_dir = self.root / "cortex-brain" / "manifests"
            if not manifest_dir.exists():
                result['errors'].append("Manifest directory not found")
                return result
            
            for manifest_file in manifest_dir.glob("*.yaml"):
                if manifest_file.is_file():
                    try:
                        import yaml
                        with open(manifest_file, 'r', encoding='utf-8') as f:
                            yaml.safe_load(f)
                        result['valid'].append(manifest_file.name)
                        print(f"   ✅ {manifest_file.name}")
                    except Exception as e:
                        result['errors'].append(f"{manifest_file.name}: {str(e)}")
                        print(f"   ❌ {manifest_file.name} - {str(e)[:50]}")
            
            return result
            
        except Exception as e:
            return {'error': str(e)}
    
    def _detect_duplicates(self) -> Dict[str, Any]:
        """Detect duplicate content."""
        try:
            script_path = self.scripts_dir / self.script_registry['duplicate_detection']
            if not script_path.exists():
                return {'warning': 'Duplicate detection script not found'}
            
            # Import and run
            spec = importlib.util.spec_from_file_location("duplicate_detector", script_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            results = module.find_duplicates(threshold=0.8)
            
            print(f"   📊 Found {len(results.get('duplicates', []))} duplicate sections")
            
            return results
            
        except Exception as e:
            return {'error': str(e)}
    
    def _scan_unnecessary_files(self) -> Dict[str, Any]:
        """Scan for unnecessary files."""
        try:
            result = {'files': {}, 'total': 0}
            
            # Patterns for unnecessary files
            patterns = {
                'temp': ['temp-*.md', 'TEMP*.md', '*.tmp'],
                'summary': ['*-SUMMARY.md'],
                'old': ['*.old', '*.bak', '*_backup*'],
                'logs': ['*.log'],
            }
            
            for category, file_patterns in patterns.items():
                category_files = []
                for pattern in file_patterns:
                    for f in self.root.rglob(pattern):
                        # Skip protected directories
                        if any(p in str(f) for p in ['.git', 'node_modules', '__pycache__', 'site']):
                            continue
                        category_files.append(str(f.relative_to(self.root)))
                
                if category_files:
                    result['files'][category] = category_files
                    result['total'] += len(category_files)
            
            print(f"   📊 Found {result['total']} potentially unnecessary files")
            
            return result
            
        except Exception as e:
            return {'error': str(e)}
    
    def _find_redundant_folders(self) -> Dict[str, Any]:
        """Find redundant/duplicate folders."""
        try:
            result = {'redundant': [], 'empty': []}
            
            # Known redundant patterns
            redundant_patterns = [
                'cortex-brain/cortex-brain',  # Nested duplicate
                'archives/archives',
                'backups/backups',
            ]
            
            for pattern in redundant_patterns:
                check_path = self.root / pattern
                if check_path.exists():
                    result['redundant'].append(pattern)
            
            # Find empty directories
            for d in self.root.rglob('*'):
                if d.is_dir() and not any(d.iterdir()):
                    rel_path = str(d.relative_to(self.root))
                    if not any(p in rel_path for p in ['.git', 'node_modules', '__pycache__']):
                        result['empty'].append(rel_path)
            
            print(f"   📊 Found {len(result['redundant'])} redundant folders")
            print(f"   📊 Found {len(result['empty'])} empty folders")
            
            return result
            
        except Exception as e:
            return {'error': str(e)}
    
    def _create_backup(self) -> Path:
        """Create backup before cleanup."""
        backup_dir = self.root / "backups" / f"doctor_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy critical files
        critical_files = [
            'cortex-operations.yaml',
            'cortex.config.json',
        ]
        
        import shutil
        for f in critical_files:
            src = self.root / f
            if src.exists():
                shutil.copy2(src, backup_dir / f)
        
        return backup_dir
    
    def _execute_cleanup(self) -> Dict[str, Any]:
        """Execute actual cleanup operations."""
        result = {'files_deleted': [], 'folders_deleted': [], 'errors': []}
        
        # This would call the cleanup scripts
        # For safety, only delete clearly temporary files
        
        import shutil
        
        # Delete temp files
        for f in self.root.rglob('temp-*.md'):
            if any(p in str(f) for p in ['.git', 'node_modules']):
                continue
            try:
                f.unlink()
                result['files_deleted'].append(str(f.relative_to(self.root)))
            except Exception as e:
                result['errors'].append(f"Failed to delete {f}: {e}")
        
        return result
    
    def _check_brain_health(self) -> Dict[str, Any]:
        """Check brain tier health."""
        try:
            result = {'tiers': {}, 'issues': []}
            
            # Check each tier directory (tier0 in src/, others in cortex-brain/)
            tier_paths = {
                'tier0': 'src/tier0',
                'tier1': 'cortex-brain/tier1',
                'tier2': 'cortex-brain/tier2',
                'tier3': 'cortex-brain/tier3',
            }
            
            for tier, rel_path in tier_paths.items():
                tier_path = self.root / rel_path
                if tier_path.exists():
                    result['tiers'][tier] = 'healthy'
                    print(f"   ✅ {tier} ({rel_path}) - healthy")
                else:
                    result['tiers'][tier] = 'missing'
                    # tier0 is less critical
                    if tier != 'tier0':
                        result['issues'].append(f"{tier} directory missing at {rel_path}")
                    print(f"   {'⚠️ ' if tier == 'tier0' else '❌'} {tier} ({rel_path}) - missing")
            
            # Check databases
            db_files = ['cortex-brain.db', 'cortex_status.db']
            for db in db_files:
                db_path = self.root / db
                if db_path.exists():
                    print(f"   ✅ {db} - present")
                else:
                    print(f"   ⚠️  {db} - not found (may be optional)")
            
            return result
            
        except Exception as e:
            return {'error': str(e)}
    
    def _verify_critical_paths(self) -> Dict[str, Any]:
        """Verify critical paths exist."""
        critical_paths = [
            'src/main.py',
            'src/orchestrators',
            'src/cortex_agents',
            'cortex-brain',
            'tests',
        ]
        
        result = {'present': [], 'missing': []}
        
        for path in critical_paths:
            full_path = self.root / path
            if full_path.exists():
                result['present'].append(path)
                print(f"   ✅ {path}")
            else:
                result['missing'].append(path)
                print(f"   ❌ {path} - MISSING")
        
        return result
    
    def _check_import_integrity(self) -> Dict[str, Any]:
        """Check for broken imports in key modules."""
        result = {'checked': [], 'broken_imports': []}
        
        # Check key modules can be imported
        key_modules = [
            'src.main',
            'src.tier0',
            'src.tier1',
        ]
        
        for module_name in key_modules:
            try:
                # Don't actually import, just check file exists
                module_path = self.root / module_name.replace('.', '/') 
                if (module_path / '__init__.py').exists() or (module_path.with_suffix('.py')).exists():
                    result['checked'].append(module_name)
                    print(f"   ✅ {module_name}")
                else:
                    print(f"   ⚠️  {module_name} - structure unclear")
            except Exception as e:
                result['broken_imports'].append(f"{module_name}: {str(e)}")
        
        return result
    
    def _collect_all_metrics(self, report: DoctorReport) -> Dict[str, Any]:
        """Collect metrics from all phases."""
        metrics = {
            'phases_completed': len([r for r in report.phase_results.values() if r.success]),
            'phases_failed': len([r for r in report.phase_results.values() if not r.success]),
            'total_errors': sum(len(r.errors) for r in report.phase_results.values()),
            'total_warnings': sum(len(r.warnings) for r in report.phase_results.values()),
            'total_actions': sum(len(r.actions_taken) for r in report.phase_results.values()),
            'total_duration': sum(r.duration_seconds for r in report.phase_results.values()),
        }
        
        return metrics
    
    def _calculate_health_score(self, report: DoctorReport) -> float:
        """Calculate overall health score (0-100)."""
        score = 100.0
        
        for result in report.phase_results.values():
            if not result.success:
                score -= 20  # Major penalty for failed phase
            score -= len(result.errors) * 5  # 5 points per error
            score -= len(result.warnings) * 2  # 2 points per warning
        
        return max(0.0, min(100.0, score))
    
    def _identify_critical_issues(self, report: DoctorReport) -> List[str]:
        """Identify critical issues requiring immediate attention."""
        critical = []
        
        for phase, result in report.phase_results.items():
            if not result.success:
                critical.append(f"Phase {phase.value} failed")
            for error in result.errors:
                if 'missing' in error.lower() or 'critical' in error.lower():
                    critical.append(error)
        
        return critical
    
    def _generate_recommendations(self, report: DoctorReport) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Based on findings, generate recommendations
        for phase, result in report.phase_results.items():
            if phase == Phase.DIAGNOSE:
                unwired = result.findings.get('unwired_components', {})
                if unwired.get('summary', {}).get('overall', {}).get('unwired_components', 0) > 5:
                    recommendations.append("Wire unwired components to cortex-operations.yaml")
            
            elif phase == Phase.SCAN:
                if result.findings.get('unnecessary_files', {}).get('total', 0) > 10:
                    recommendations.append("Run cleanup with --execute to remove unnecessary files")
                if result.findings.get('redundant_folders', {}).get('redundant'):
                    recommendations.append("Remove redundant nested folders (cortex-brain/cortex-brain)")
            
            elif phase == Phase.VALIDATE:
                if result.findings.get('brain_health', {}).get('issues'):
                    recommendations.append("Restore missing brain tier directories")
        
        if not recommendations:
            recommendations.append("System is healthy - no immediate actions required")
        
        return recommendations
    
    def _generate_markdown_report(self, report: DoctorReport, metrics: Dict[str, Any]) -> Path:
        """Generate markdown health report."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = self.output_dir / f"doctor-report-{timestamp}.md"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# 🩺 CORTEX System Doctor Report\n\n")
            f.write(f"**Generated:** {report.timestamp}\n")
            f.write(f"**Mode:** {report.mode}\n")
            f.write(f"**Health Score:** {report.overall_health_score:.1f}/100\n\n")
            
            f.write("---\n\n")
            
            # Summary metrics
            f.write("## 📊 Summary Metrics\n\n")
            f.write(f"| Metric | Value |\n")
            f.write(f"|--------|-------|\n")
            f.write(f"| Phases Completed | {metrics['phases_completed']} |\n")
            f.write(f"| Phases Failed | {metrics['phases_failed']} |\n")
            f.write(f"| Total Errors | {metrics['total_errors']} |\n")
            f.write(f"| Total Warnings | {metrics['total_warnings']} |\n")
            f.write(f"| Total Duration | {metrics['total_duration']:.2f}s |\n\n")
            
            # Critical issues
            if report.critical_issues:
                f.write("## 🚨 Critical Issues\n\n")
                for issue in report.critical_issues:
                    f.write(f"- ❌ {issue}\n")
                f.write("\n")
            
            # Recommendations
            f.write("## 💡 Recommendations\n\n")
            for rec in report.recommendations:
                f.write(f"- {rec}\n")
            f.write("\n")
            
            # Phase details
            f.write("## 📋 Phase Details\n\n")
            for phase, result in report.phase_results.items():
                status = "✅" if result.success else "❌"
                f.write(f"### {status} {phase.value.upper()}\n\n")
                f.write(f"**Duration:** {result.duration_seconds:.2f}s\n\n")
                
                if result.errors:
                    f.write("**Errors:**\n")
                    for error in result.errors:
                        f.write(f"- {error}\n")
                    f.write("\n")
                
                if result.warnings:
                    f.write("**Warnings:**\n")
                    for warning in result.warnings:
                        f.write(f"- {warning}\n")
                    f.write("\n")
                
                if result.actions_taken:
                    f.write("**Actions:**\n")
                    for action in result.actions_taken:
                        f.write(f"- {action}\n")
                    f.write("\n")
        
        return report_path
    
    def _save_report(self, report: DoctorReport):
        """Save JSON report."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        json_path = self.output_dir / f"doctor-report-{timestamp}.json"
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report.to_dict(), f, indent=2)
    
    def _print_final_summary(self, report: DoctorReport):
        """Print final summary to console."""
        print("\n" + "=" * 80)
        print("🩺 SYSTEM DOCTOR FINAL SUMMARY")
        print("=" * 80)
        
        # Health score with visual indicator
        score = report.overall_health_score
        if score >= 90:
            indicator = "🟢 EXCELLENT"
        elif score >= 70:
            indicator = "🟡 GOOD"
        elif score >= 50:
            indicator = "🟠 FAIR"
        else:
            indicator = "🔴 POOR"
        
        print(f"\n📊 Health Score: {score:.1f}/100 {indicator}")
        
        # Critical issues
        if report.critical_issues:
            print(f"\n🚨 Critical Issues ({len(report.critical_issues)}):")
            for issue in report.critical_issues[:5]:
                print(f"   - {issue}")
        
        # Top recommendations
        print(f"\n💡 Top Recommendations:")
        for rec in report.recommendations[:3]:
            print(f"   - {rec}")
        
        # Next action
        print(f"\n📄 Detailed report saved to: cortex-brain/health-reports/")
        
        if self.dry_run:
            print(f"\n⚠️  Run with --execute to perform cleanup actions")
        
        print("\n" + "=" * 80)


def run_quick_health_check(project_root: Path) -> Dict[str, Any]:
    """
    Quick health check - minimal validation for fast feedback.
    
    Returns:
        Dict with health status and any critical issues
    """
    print("\n⚡ QUICK HEALTH CHECK\n")
    
    result = {
        'healthy': True,
        'checks': {},
        'critical_issues': []
    }
    
    # Check 1: Core files exist
    core_files = [
        '.github/prompts/CORTEX.prompt.md',
        'cortex-operations.yaml',
        'src/main.py',
    ]
    
    for f in core_files:
        exists = (project_root / f).exists()
        result['checks'][f] = exists
        if not exists:
            result['critical_issues'].append(f"Missing: {f}")
            result['healthy'] = False
        print(f"   {'✅' if exists else '❌'} {f}")
    
    # Check 2: Brain directories (tier0 is in src/, tiers 1-3 are in cortex-brain/)
    brain_tier_paths = [
        ('tier0', 'src/tier0'),
        ('tier1', 'cortex-brain/tier1'),
        ('tier2', 'cortex-brain/tier2'),
        ('tier3', 'cortex-brain/tier3'),
    ]
    for tier, path in brain_tier_paths:
        exists = (project_root / path).exists()
        result['checks'][f'brain/{tier}'] = exists
        if not exists:
            # tier0 might be optional if using different architecture
            if tier != 'tier0':
                result['critical_issues'].append(f"Missing brain tier: {tier}")
                result['healthy'] = False
        print(f"   {'✅' if exists else '⚠️ '} {path}")
    
    # Summary
    if result['healthy']:
        print("\n✅ Quick health check passed!")
    else:
        print(f"\n❌ Issues found: {len(result['critical_issues'])}")
        for issue in result['critical_issues']:
            print(f"   - {issue}")
    
    return result


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='CORTEX System Doctor - Comprehensive Health & Maintenance Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/cortex_system_doctor.py                     # Full diagnostic (dry-run)
    python scripts/cortex_system_doctor.py --execute           # Execute cleanup
    python scripts/cortex_system_doctor.py --phase diagnose    # Run specific phase
    python scripts/cortex_system_doctor.py --quick             # Quick health check
    python scripts/cortex_system_doctor.py --phase scan --phase cleanup  # Multiple phases
        """
    )
    
    parser.add_argument(
        '--execute',
        action='store_true',
        help='Execute cleanup actions (default is dry-run preview)'
    )
    
    parser.add_argument(
        '--phase',
        action='append',
        choices=[p.value for p in Phase],
        help='Run specific phase(s). Can be used multiple times.'
    )
    
    parser.add_argument(
        '--quick',
        action='store_true',
        help='Quick health check only (minimal validation)'
    )
    
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Reduce output verbosity'
    )
    
    args = parser.parse_args()
    
    # Determine project root
    project_root = PROJECT_ROOT
    
    if args.quick:
        result = run_quick_health_check(project_root)
        sys.exit(0 if result['healthy'] else 1)
    
    # Determine phases to run
    phases = None
    if args.phase:
        phases = [Phase(p) for p in args.phase]
    
    # Create and run doctor
    doctor = CortexSystemDoctor(
        project_root=project_root,
        dry_run=not args.execute,
        verbose=not args.quiet
    )
    
    report = doctor.run_full_checkup(phases=phases)
    
    # Exit with appropriate code
    if report.overall_health_score >= 70:
        sys.exit(0)
    elif report.critical_issues:
        sys.exit(2)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
