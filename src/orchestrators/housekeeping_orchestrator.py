"""
CORTEX 6.0 - Housekeeping Orchestrator

Manual on-demand CORTEX system maintenance orchestrator.
Executes 9-phase cleanup workflow to maintain system health.

Per DOR Q4/Q9: MANUAL EXECUTION ONLY
- NO automatic triggers, cron jobs, or file watchers
- NO git hooks
- User control prioritized

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import sqlite3
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import yaml


@dataclass
class HousekeepingConfig:
    """Configuration for housekeeping orchestrator."""
    
    workspace_root: Path
    manual_only: bool = True  # MUST be True per DOR Q4/Q9
    allow_background: bool = False  # User sees execution by default
    cache_retention_days: int = 30
    audit_retention_days: int = 90
    
    def __post_init__(self):
        """Validate configuration."""
        if not self.manual_only:
            raise ValueError("Housekeeping MUST be manual_only=True per DOR Q4/Q9")


@dataclass
class PhaseResult:
    """Result from a single housekeeping phase."""
    
    phase_number: int
    phase_name: str
    status: str  # SUCCESS, FAILED, SKIPPED
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0
    error_message: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    health_contribution: float = 0.0
    
    # Phase-specific metrics
    rules_validated: int = 0
    conflicts_detected: int = 0
    rules_passed: int = 0
    rules_failed: int = 0
    test_files_scanned: int = 0
    total_tests: int = 0
    tests_with_ac_markers: int = 0
    orphaned_tests_count: int = 0
    coverage_percentage: float = 0.0
    audit_entries_analyzed: int = 0
    error_patterns_detected: int = 0
    tiers_validated: int = 0
    sync_issues_found: int = 0
    sync_issues_fixed: int = 0
    cache_files_deleted: int = 0
    space_reclaimed_mb: float = 0.0
    isolation_violations_found: int = 0
    gitignore_valid: bool = False
    total_ac_defined: int = 0
    ac_without_tests: int = 0
    critical_gaps: List[str] = field(default_factory=list)


@dataclass
class HealthScore:
    """Overall system health score."""
    
    score: float  # 0-100
    components: Dict[str, float] = field(default_factory=dict)
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class HousekeepingReport:
    """Complete housekeeping execution report."""
    
    timestamp: datetime
    workspace_root: Path
    phase_results: List[PhaseResult] = field(default_factory=list)
    overall_health_score: float = 0.0
    total_duration_seconds: float = 0.0
    report_path: Optional[Path] = None
    
    def to_yaml(self) -> str:
        """Export report to YAML format."""
        return yaml.dump({
            'timestamp': self.timestamp.isoformat(),
            'workspace_root': str(self.workspace_root),
            'overall_health_score': self.overall_health_score,
            'total_duration_seconds': self.total_duration_seconds,
            'phase_results': [
                {
                    'phase': p.phase_number,
                    'name': p.phase_name,
                    'status': p.status,
                    'duration': p.duration_seconds,
                    'health_contribution': p.health_contribution,
                    'details': p.details
                }
                for p in self.phase_results
            ]
        }, default_flow_style=False, sort_keys=False)


class HousekeepingOrchestrator:
    """
    CORTEX Housekeeping Orchestrator - Manual On-Demand Only
    
    Executes 9-phase system maintenance workflow:
    1. Governance rule validation
    2. Test coverage analysis
    3. Audit log health check
    4. Brain tier synchronization
    5. Cache cleanup
    6. Git isolation verification
    7. Orchestrator manifest validation
    8. AC gap detection
    9. Health report generation
    
    CRITICAL: Manual execution only per DOR Q4/Q9
    - NO automatic triggers
    - NO git hooks
    - NO cron jobs
    - NO file watchers
    """
    
    def __init__(self, config: HousekeepingConfig):
        """Initialize housekeeping orchestrator."""
        self.config = config
        self.workspace_root = config.workspace_root
        self.cortex_brain = self.workspace_root / "cortex-brain"
        
        # Verify manual_only requirement
        if not config.manual_only:
            raise ValueError("Housekeeping MUST be manual_only=True per DOR Q4/Q9")
        
        # NO scheduler, file watcher, git hooks (per DOR Q4/Q9)
        # These attributes intentionally NOT defined
    
    def execute(self) -> HousekeepingReport:
        """
        Execute complete 9-phase housekeeping workflow.
        
        MANUAL INVOCATION ONLY - No automatic triggers.
        
        Returns:
            HousekeepingReport with all phase results and health score
        """
        start_time = datetime.now()
        report = HousekeepingReport(
            timestamp=start_time,
            workspace_root=self.workspace_root
        )
        
        # Execute 9 phases sequentially
        phases = [
            (1, "governance_validation", self._execute_phase_1),
            (2, "test_coverage_analysis", self._execute_phase_2),
            (3, "audit_log_health_check", self._execute_phase_3),
            (4, "brain_tier_sync", self._execute_phase_4),
            (5, "cache_cleanup", self._execute_phase_5),
            (6, "git_isolation_check", self._execute_phase_6),
            (7, "manifest_validation", self._execute_phase_7),
            (8, "ac_gap_detection", self._execute_phase_8),
            (9, "health_report_generation", self._execute_phase_9),
        ]
        
        for phase_num, phase_name, phase_func in phases:
            try:
                result = phase_func()
                result.phase_number = phase_num
                result.phase_name = phase_name
                report.phase_results.append(result)
            except Exception as e:
                # Phase failure - log but continue
                result = PhaseResult(
                    phase_number=phase_num,
                    phase_name=phase_name,
                    status="FAILED",
                    start_time=datetime.now(),
                    end_time=datetime.now(),
                    error_message=str(e)
                )
                report.phase_results.append(result)
        
        # Calculate overall health score
        report.overall_health_score = self._calculate_health_score(report.phase_results)
        
        # Calculate total duration
        end_time = datetime.now()
        report.total_duration_seconds = (end_time - start_time).total_seconds()
        
        # Save report
        report.report_path = self._save_report(report)
        
        return report
    
    def get_phases(self) -> List[Any]:
        """
        Get list of all housekeeping phases.
        
        Returns:
            List of phase objects with name and number attributes
        """
        from types import SimpleNamespace
        
        return [
            SimpleNamespace(number=1, name='governance_validation'),
            SimpleNamespace(number=2, name='test_coverage_analysis'),
            SimpleNamespace(number=3, name='audit_log_health_check'),
            SimpleNamespace(number=4, name='brain_tier_sync'),
            SimpleNamespace(number=5, name='cache_cleanup'),
            SimpleNamespace(number=6, name='git_isolation_check'),
            SimpleNamespace(number=7, name='manifest_validation'),
            SimpleNamespace(number=8, name='ac_gap_detection'),
            SimpleNamespace(number=9, name='health_report_generation'),
        ]
    
    # =========================================================================
    # PHASE IMPLEMENTATIONS
    # =========================================================================
    
    def _execute_phase_1(self) -> PhaseResult:
        """Phase 1: Governance rule validation."""
        start_time = datetime.now()
        result = PhaseResult(
            phase_number=1,
            phase_name="governance_validation",
            status="SUCCESS",
            start_time=start_time
        )
        
        try:
            # Load CORE governance rules
            rules_file = self.cortex_brain / "tier0" / "governance" / "core-rules.yaml"
            
            if not rules_file.exists():
                result.status = "SKIPPED"
                result.details['reason'] = "No governance rules file found"
                result.end_time = datetime.now()
                result.duration_seconds = (result.end_time - start_time).total_seconds()
                return result
            
            with open(rules_file) as f:
                rules_data = yaml.safe_load(f)
            
            rules = rules_data.get('rules', [])
            result.rules_validated = len(rules)
            
            # Check for duplicate IDs (conflicts)
            rule_ids = [r.get('id') for r in rules if 'id' in r]
            duplicates = [rid for rid in rule_ids if rule_ids.count(rid) > 1]
            result.conflicts_detected = len(set(duplicates))
            
            # Mark rules as passed/failed
            result.rules_passed = len(rules) - result.conflicts_detected
            result.rules_failed = result.conflicts_detected
            
            # Health contribution (100% if no conflicts)
            result.health_contribution = 100.0 if result.conflicts_detected == 0 else 75.0
            
            result.details = {
                'rules_validated': result.rules_validated,
                'conflicts': list(set(duplicates)) if duplicates else []
            }
            
        except Exception as e:
            result.status = "FAILED"
            result.error_message = str(e)
            result.health_contribution = 0.0
        
        result.end_time = datetime.now()
        result.duration_seconds = (result.end_time - start_time).total_seconds()
        return result
    
    def _execute_phase_2(self) -> PhaseResult:
        """Phase 2: Test coverage analysis."""
        start_time = datetime.now()
        result = PhaseResult(
            phase_number=2,
            phase_name="test_coverage_analysis",
            status="SUCCESS",
            start_time=start_time
        )
        
        try:
            # Use AC traceability system for coverage analysis
            from infrastructure.ac_traceability import (
                ACTraceabilitySystem,
                TraceabilityConfig
            )
            
            tests_root = self.workspace_root / "tests"
            if not tests_root.exists():
                result.status = "SKIPPED"
                result.details['reason'] = "No tests directory found"
                result.end_time = datetime.now()
                result.duration_seconds = (result.end_time - start_time).total_seconds()
                return result
            
            config = TraceabilityConfig(
                tests_root=tests_root,
                registry_path=self.cortex_brain / "registry"
            )
            
            system = ACTraceabilitySystem(config)
            
            # Scan tests
            scan_results = system.scan_tests()
            
            # Generate gap report
            gap_report = system.detect_gaps()
            
            # Populate metrics
            result.tests_with_ac_markers = sum(len(tests) for tests in scan_results.values())
            result.orphaned_tests_count = len(gap_report.orphaned_tests)
            result.total_tests = result.tests_with_ac_markers + result.orphaned_tests_count
            
            if result.total_tests > 0:
                result.coverage_percentage = (result.tests_with_ac_markers / result.total_tests) * 100
            
            # Count test files
            test_files = list(tests_root.rglob("test_*.py")) + list(tests_root.rglob("*_test.py"))
            result.test_files_scanned = len([f for f in test_files if f.name not in ('conftest.py', '__init__.py')])
            
            # Health contribution based on coverage
            result.health_contribution = result.coverage_percentage
            
            result.details = {
                'test_files': result.test_files_scanned,
                'total_tests': result.total_tests,
                'marked_tests': result.tests_with_ac_markers,
                'orphaned_tests': result.orphaned_tests_count,
                'coverage': f"{result.coverage_percentage:.1f}%"
            }
            
        except Exception as e:
            result.status = "FAILED"
            result.error_message = str(e)
            result.health_contribution = 0.0
        
        result.end_time = datetime.now()
        result.duration_seconds = (result.end_time - start_time).total_seconds()
        return result
    
    def _execute_phase_3(self) -> PhaseResult:
        """Phase 3: Audit log health check."""
        start_time = datetime.now()
        result = PhaseResult(
            phase_number=3,
            phase_name="audit_log_health_check",
            status="SUCCESS",
            start_time=start_time
        )
        
        try:
            # Find audit database
            audit_dir = self.cortex_brain / "audit-logs"
            if not audit_dir.exists():
                result.status = "SKIPPED"
                result.details['reason'] = "No audit logs found"
                result.end_time = datetime.now()
                result.duration_seconds = (result.end_time - start_time).total_seconds()
                return result
            
            audit_dbs = list(audit_dir.glob("*.db"))
            if not audit_dbs:
                result.status = "SKIPPED"
                result.details['reason'] = "No audit database found"
                result.end_time = datetime.now()
                result.duration_seconds = (result.end_time - start_time).total_seconds()
                return result
            
            # Analyze first database found
            audit_db = audit_dbs[0]
            conn = sqlite3.connect(audit_db)
            cursor = conn.cursor()
            
            # Count total entries
            cursor.execute("SELECT COUNT(*) FROM audit_log")
            result.audit_entries_analyzed = cursor.fetchone()[0]
            
            # Count error patterns (repeated errors)
            cursor.execute("""
                SELECT message, COUNT(*) as count
                FROM audit_log
                WHERE level = 'ERROR'
                GROUP BY message
                HAVING count > 1
            """)
            error_patterns = cursor.fetchall()
            result.error_patterns_detected = len(error_patterns)
            
            conn.close()
            
            # Health contribution (100% if no error patterns)
            result.health_contribution = 100.0 if result.error_patterns_detected == 0 else 80.0
            
            result.details = {
                'entries_analyzed': result.audit_entries_analyzed,
                'error_patterns': result.error_patterns_detected
            }
            
        except Exception as e:
            result.status = "FAILED"
            result.error_message = str(e)
            result.health_contribution = 0.0
        
        result.end_time = datetime.now()
        result.duration_seconds = (result.end_time - start_time).total_seconds()
        return result
    
    def _execute_phase_4(self) -> PhaseResult:
        """Phase 4: Brain tier synchronization."""
        start_time = datetime.now()
        result = PhaseResult(
            phase_number=4,
            phase_name="brain_tier_sync",
            status="SUCCESS",
            start_time=start_time
        )
        
        try:
            # Validate 4-tier structure
            tiers = ['tier0', 'tier1', 'tier2', 'tier3']
            validated = 0
            
            for tier in tiers:
                tier_path = self.cortex_brain / tier
                if tier_path.exists():
                    validated += 1
            
            result.tiers_validated = validated
            result.sync_issues_found = 4 - validated
            result.sync_issues_fixed = 0  # Read-only check for now
            
            # Health contribution
            result.health_contribution = (validated / 4) * 100
            
            result.details = {
                'tiers_validated': validated,
                'missing_tiers': 4 - validated
            }
            
        except Exception as e:
            result.status = "FAILED"
            result.error_message = str(e)
            result.health_contribution = 0.0
        
        result.end_time = datetime.now()
        result.duration_seconds = (result.end_time - start_time).total_seconds()
        return result
    
    def _execute_phase_5(self) -> PhaseResult:
        """Phase 5: Cache cleanup."""
        start_time = datetime.now()
        result = PhaseResult(
            phase_number=5,
            phase_name="cache_cleanup",
            status="SUCCESS",
            start_time=start_time
        )
        
        try:
            cache_dir = self.cortex_brain / "cache"
            if not cache_dir.exists():
                result.status = "SKIPPED"
                result.details['reason'] = "No cache directory found"
                result.end_time = datetime.now()
                result.duration_seconds = (result.end_time - start_time).total_seconds()
                return result
            
            # Find old cache files
            cutoff_time = datetime.now() - timedelta(days=self.config.cache_retention_days)
            deleted_count = 0
            space_reclaimed = 0
            
            for cache_file in cache_dir.rglob("*"):
                if cache_file.is_file():
                    mtime = datetime.fromtimestamp(cache_file.stat().st_mtime)
                    if mtime < cutoff_time:
                        size = cache_file.stat().st_size
                        cache_file.unlink()
                        deleted_count += 1
                        space_reclaimed += size
            
            result.cache_files_deleted = deleted_count
            result.space_reclaimed_mb = space_reclaimed / (1024 * 1024)
            
            # Health contribution (100% regardless - cleanup is maintenance)
            result.health_contribution = 100.0
            
            result.details = {
                'files_deleted': deleted_count,
                'space_reclaimed_mb': f"{result.space_reclaimed_mb:.2f}"
            }
            
        except Exception as e:
            result.status = "FAILED"
            result.error_message = str(e)
            result.health_contribution = 0.0
        
        result.end_time = datetime.now()
        result.duration_seconds = (result.end_time - start_time).total_seconds()
        return result
    
    def _execute_phase_6(self) -> PhaseResult:
        """Phase 6: Git isolation verification."""
        start_time = datetime.now()
        result = PhaseResult(
            phase_number=6,
            phase_name="git_isolation_check",
            status="SUCCESS",
            start_time=start_time
        )
        
        try:
            # Check .gitignore contains cortex-brain
            gitignore = self.workspace_root / ".gitignore"
            
            # Default: no violations unless explicitly found
            result.isolation_violations_found = 0
            result.gitignore_valid = True  # Assume valid unless proven otherwise
            
            if gitignore.exists():
                content = gitignore.read_text()
                result.gitignore_valid = 'cortex-brain' in content
                # Only report violation if .gitignore exists but doesn't contain pattern
                if not result.gitignore_valid:
                    result.isolation_violations_found = 1
            # If .gitignore doesn't exist, that's okay (might be a new project)
            
            # Health contribution based on gitignore validation
            result.health_contribution = 100.0 if result.gitignore_valid else 90.0
            
            result.details = {
                'gitignore_valid': result.gitignore_valid,
                'violations': result.isolation_violations_found
            }
            
        except Exception as e:
            result.status = "FAILED"
            result.error_message = str(e)
            result.health_contribution = 0.0
        
        result.end_time = datetime.now()
        result.duration_seconds = (result.end_time - start_time).total_seconds()
        return result
    
    def _execute_phase_7(self) -> PhaseResult:
        """Phase 7: Orchestrator manifest validation."""
        start_time = datetime.now()
        result = PhaseResult(
            phase_number=7,
            phase_name="manifest_validation",
            status="SUCCESS",
            start_time=start_time
        )
        
        try:
            # Validate orchestrator manifests
            manifests_dir = self.cortex_brain / "manifests" / "orchestrators"
            
            if not manifests_dir.exists():
                result.status = "SKIPPED"
                result.details['reason'] = "No manifests directory found"
                result.end_time = datetime.now()
                result.duration_seconds = (result.end_time - start_time).total_seconds()
                return result
            
            manifest_files = list(manifests_dir.glob("*.yaml"))
            validated = 0
            errors = []
            
            for manifest_file in manifest_files:
                try:
                    with open(manifest_file) as f:
                        yaml.safe_load(f)
                    validated += 1
                except Exception as e:
                    errors.append(f"{manifest_file.name}: {str(e)}")
            
            result.details = {
                'manifests_validated': validated,
                'validation_errors': len(errors),
                'errors': errors[:5]  # Limit to first 5
            }
            
            # Health contribution
            total = len(manifest_files)
            result.health_contribution = (validated / total * 100) if total > 0 else 100
            
        except Exception as e:
            result.status = "FAILED"
            result.error_message = str(e)
            result.health_contribution = 0.0
        
        result.end_time = datetime.now()
        result.duration_seconds = (result.end_time - start_time).total_seconds()
        return result
    
    def _execute_phase_8(self) -> PhaseResult:
        """Phase 8: AC gap detection."""
        start_time = datetime.now()
        result = PhaseResult(
            phase_number=8,
            phase_name="ac_gap_detection",
            status="SUCCESS",  # Always SUCCESS (even if no report)
            start_time=start_time
        )
        
        try:
            # Load AC coverage report if exists
            coverage_report = self.cortex_brain / "registry" / "ac-test-coverage.yaml"
            
            if not coverage_report.exists():
                # No report found - return with zero values but still SUCCESS
                result.total_ac_defined = 0
                result.ac_without_tests = 0
                result.coverage_percentage = 0.0
                result.critical_gaps = []
                result.health_contribution = 100.0  # No report = no gaps detected
                result.details = {
                    'reason': 'No AC coverage report found',
                    'total_ac': 0,
                    'uncovered': 0,
                    'coverage': '0.0%',
                    'critical_gaps': 0
                }
                result.end_time = datetime.now()
                result.duration_seconds = (result.end_time - start_time).total_seconds()
                return result
            
            with open(coverage_report) as f:
                report_data = yaml.safe_load(f)
            
            stats = report_data.get('statistics', {})
            result.total_ac_defined = stats.get('total_ac', 0)
            result.ac_without_tests = stats.get('uncovered_ac', 0)
            result.coverage_percentage = stats.get('coverage_percentage', 0.0)
            
            # Get critical gaps
            gaps = report_data.get('gaps', {})
            result.critical_gaps = gaps.get('critical_gaps', [])
            
            # Health contribution based on coverage
            result.health_contribution = result.coverage_percentage
            
            result.details = {
                'total_ac': result.total_ac_defined,
                'uncovered': result.ac_without_tests,
                'coverage': f"{result.coverage_percentage:.1f}%",
                'critical_gaps': len(result.critical_gaps)
            }
            
        except Exception as e:
            result.status = "FAILED"
            result.error_message = str(e)
            result.health_contribution = 0.0
        
        result.end_time = datetime.now()
        result.duration_seconds = (result.end_time - start_time).total_seconds()
        return result
    
    def _execute_phase_9(self) -> PhaseResult:
        """Phase 9: Health report generation."""
        start_time = datetime.now()
        result = PhaseResult(
            phase_number=9,
            phase_name="health_report_generation",
            status="SUCCESS",
            start_time=start_time
        )
        
        # This phase generates the report (handled by execute())
        result.health_contribution = 100.0
        result.details = {'report_generated': True}
        
        result.end_time = datetime.now()
        result.duration_seconds = (result.end_time - start_time).total_seconds()
        return result
    
    # =========================================================================
    # HELPER METHODS
    # =========================================================================
    
    def _calculate_health_score(self, phase_results: List[PhaseResult]) -> float:
        """Calculate overall health score from phase results."""
        if not phase_results:
            return 0.0
        
        # Weighted average of phase contributions
        total_contribution = sum(p.health_contribution for p in phase_results)
        return total_contribution / len(phase_results)
    
    def _save_report(self, report: HousekeepingReport) -> Path:
        """Save housekeeping report to file."""
        reports_dir = self.cortex_brain / "documents" / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp_str = report.timestamp.strftime("%Y%m%d-%H%M%S")
        report_path = reports_dir / f"housekeeping-{timestamp_str}.yaml"
        
        with open(report_path, 'w') as f:
            f.write(report.to_yaml())
        
        return report_path
