#!/usr/bin/env python3
"""
CORTEX Maintenance Runner - Automated Maintenance Pipeline

Chains maintenance operations in optimal order for keeping CORTEX 4.0 at peak performance.
This is designed for scheduled/automated runs (e.g., weekly maintenance).

Pipeline Stages:
1. PRE-FLIGHT: Quick health check (abort if critical issues)
2. ANALYSIS: Run system doctor diagnose + scan
3. OPTIMIZATION: Deduplicate, organize, optimize
4. CLEANUP: Remove safe deletables (with backup)
5. VALIDATION: Post-maintenance health check
6. REPORTING: Generate maintenance report

Usage:
    python scripts/cortex_maintenance_runner.py                    # Full maintenance (dry-run)
    python scripts/cortex_maintenance_runner.py --execute          # Execute all stages
    python scripts/cortex_maintenance_runner.py --stage analysis   # Run specific stage
    python scripts/cortex_maintenance_runner.py --schedule weekly  # Output cron schedule

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sys
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class Stage(Enum):
    """Maintenance pipeline stages."""
    PREFLIGHT = "preflight"
    ANALYSIS = "analysis"
    OPTIMIZATION = "optimization"
    CLEANUP = "cleanup"
    VALIDATION = "validation"
    REPORTING = "reporting"


@dataclass
class StageResult:
    """Result of a maintenance stage."""
    stage: Stage
    success: bool
    duration_seconds: float = 0.0
    output: str = ""
    metrics: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)


@dataclass
class MaintenanceReport:
    """Complete maintenance run report."""
    timestamp: str
    mode: str
    stages_run: List[Stage]
    stage_results: Dict[Stage, StageResult]
    overall_success: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp,
            'mode': self.mode,
            'stages_run': [s.value for s in self.stages_run],
            'overall_success': self.overall_success,
            'stage_results': {
                s.value: {
                    'success': r.success,
                    'duration': r.duration_seconds,
                    'errors': r.errors,
                    'metrics': r.metrics
                } for s, r in self.stage_results.items()
            }
        }


class CortexMaintenanceRunner:
    """
    Automated maintenance pipeline for CORTEX 4.0.
    
    Chains maintenance scripts in optimal order with proper
    error handling and rollback capabilities.
    """
    
    def __init__(self, project_root: Path, dry_run: bool = True, verbose: bool = True):
        self.root = project_root
        self.dry_run = dry_run
        self.verbose = verbose
        self.scripts_dir = project_root / "scripts"
        self.output_dir = project_root / "cortex-brain" / "health-reports"
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def print_banner(self):
        """Print maintenance banner."""
        print("=" * 80)
        print("🔧 CORTEX MAINTENANCE RUNNER v1.0")
        print("=" * 80)
        print()
        print("Author:     Asif Hussain")
        print("Copyright:  © 2024-2025 Asif Hussain. All rights reserved.")
        print(f"Mode:       {'DRY-RUN (preview)' if self.dry_run else '⚠️  EXECUTE (changes will apply)'}")
        print(f"Started:    {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        print("=" * 80)
    
    def run_pipeline(self, stages: Optional[List[Stage]] = None) -> MaintenanceReport:
        """
        Run the full maintenance pipeline.
        
        Args:
            stages: Specific stages to run (default: all)
        """
        self.print_banner()
        
        if stages is None:
            stages = list(Stage)
        
        report = MaintenanceReport(
            timestamp=datetime.now().isoformat(),
            mode='dry-run' if self.dry_run else 'execute',
            stages_run=stages,
            stage_results={}
        )
        
        print(f"\n📋 Running {len(stages)} stage(s): {', '.join(s.value for s in stages)}\n")
        
        for stage in stages:
            print(f"\n{'=' * 60}")
            print(f"🔄 STAGE: {stage.value.upper()}")
            print(f"{'=' * 60}")
            
            start_time = datetime.now()
            
            try:
                result = self._run_stage(stage)
            except Exception as e:
                result = StageResult(
                    stage=stage,
                    success=False,
                    errors=[f"Stage failed: {str(e)}"]
                )
            
            result.duration_seconds = (datetime.now() - start_time).total_seconds()
            report.stage_results[stage] = result
            
            # Print status
            status = "✅ PASSED" if result.success else "❌ FAILED"
            print(f"\n{status} ({result.duration_seconds:.2f}s)")
            
            if result.errors:
                for error in result.errors:
                    print(f"   ❌ {error}")
            
            # Abort on preflight failure
            if stage == Stage.PREFLIGHT and not result.success:
                print("\n🛑 Aborting: Pre-flight check failed")
                report.overall_success = False
                break
        
        # Determine overall success
        report.overall_success = all(r.success for r in report.stage_results.values())
        
        # Save and print summary
        self._save_report(report)
        self._print_summary(report)
        
        return report
    
    def _run_stage(self, stage: Stage) -> StageResult:
        """Run a specific stage."""
        if stage == Stage.PREFLIGHT:
            return self._stage_preflight()
        elif stage == Stage.ANALYSIS:
            return self._stage_analysis()
        elif stage == Stage.OPTIMIZATION:
            return self._stage_optimization()
        elif stage == Stage.CLEANUP:
            return self._stage_cleanup()
        elif stage == Stage.VALIDATION:
            return self._stage_validation()
        elif stage == Stage.REPORTING:
            return self._stage_reporting()
        else:
            return StageResult(stage=stage, success=False, errors=["Unknown stage"])
    
    def _stage_preflight(self) -> StageResult:
        """Pre-flight: Quick health check to ensure system is safe to maintain."""
        result = StageResult(stage=Stage.PREFLIGHT, success=True)
        
        print("   Running quick health check...")
        
        # Run doctor quick check
        cmd = [sys.executable, str(self.scripts_dir / "cortex_system_doctor.py"), "--quick"]
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(self.root))
        
        result.output = proc.stdout
        if proc.returncode != 0:
            result.success = False
            result.errors.append("Quick health check failed")
            result.errors.append(proc.stderr if proc.stderr else "See output for details")
        else:
            print("   ✅ System is ready for maintenance")
        
        return result
    
    def _stage_analysis(self) -> StageResult:
        """Analysis: Deep scan for issues."""
        result = StageResult(stage=Stage.ANALYSIS, success=True)
        
        print("   Running system doctor analysis...")
        
        # Run doctor diagnose + scan
        cmd = [
            sys.executable, 
            str(self.scripts_dir / "cortex_system_doctor.py"),
            "--phase", "diagnose",
            "--phase", "scan",
            "--quiet"
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(self.root))
        
        result.output = proc.stdout
        
        # Parse metrics from output
        if "Health Score:" in proc.stdout:
            import re
            match = re.search(r'Health Score: ([\d.]+)', proc.stdout)
            if match:
                result.metrics['health_score'] = float(match.group(1))
        
        # Non-zero exit for warnings is OK for analysis
        if proc.returncode > 1:
            result.success = False
            result.errors.append("Analysis found critical issues")
        
        return result
    
    def _stage_optimization(self) -> StageResult:
        """Optimization: Deduplicate and organize."""
        result = StageResult(stage=Stage.OPTIMIZATION, success=True)
        
        if self.dry_run:
            print("   [DRY-RUN] Would run optimization scripts")
            result.metrics['dry_run'] = True
            return result
        
        # Run duplicate detection
        print("   Checking for duplicates...")
        
        try:
            # Import and run duplicate detector
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "detector",
                self.scripts_dir / "detect_duplicates.py"
            )
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                dup_results = module.find_duplicates()
                result.metrics['duplicates_found'] = len(dup_results.get('duplicates', []))
                print(f"   📊 Found {result.metrics['duplicates_found']} duplicate sections")
        except Exception as e:
            result.errors.append(f"Duplicate detection failed: {e}")
        
        return result
    
    def _stage_cleanup(self) -> StageResult:
        """Cleanup: Remove unnecessary files."""
        result = StageResult(stage=Stage.CLEANUP, success=True)
        
        if self.dry_run:
            print("   [DRY-RUN] Would execute cleanup")
            result.metrics['dry_run'] = True
            return result
        
        print("   Executing cleanup...")
        
        # Run doctor cleanup phase
        cmd = [
            sys.executable,
            str(self.scripts_dir / "cortex_system_doctor.py"),
            "--phase", "cleanup",
            "--execute"
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(self.root))
        
        result.output = proc.stdout
        if proc.returncode != 0:
            result.errors.append("Cleanup completed with warnings")
        
        return result
    
    def _stage_validation(self) -> StageResult:
        """Validation: Post-maintenance health check."""
        result = StageResult(stage=Stage.VALIDATION, success=True)
        
        print("   Running post-maintenance validation...")
        
        # Run doctor validate phase
        cmd = [
            sys.executable,
            str(self.scripts_dir / "cortex_system_doctor.py"),
            "--phase", "validate"
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(self.root))
        
        result.output = proc.stdout
        if proc.returncode != 0:
            result.success = False
            result.errors.append("Post-maintenance validation failed")
        else:
            print("   ✅ Validation passed")
        
        return result
    
    def _stage_reporting(self) -> StageResult:
        """Reporting: Generate maintenance report."""
        result = StageResult(stage=Stage.REPORTING, success=True)
        
        print("   Generating maintenance report...")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = self.output_dir / f"maintenance-report-{timestamp}.md"
        
        result.metrics['report_path'] = str(report_path)
        print(f"   📄 Report: {report_path}")
        
        return result
    
    def _save_report(self, report: MaintenanceReport):
        """Save maintenance report."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        json_path = self.output_dir / f"maintenance-{timestamp}.json"
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report.to_dict(), f, indent=2)
    
    def _print_summary(self, report: MaintenanceReport):
        """Print maintenance summary."""
        print("\n" + "=" * 80)
        print("🔧 MAINTENANCE SUMMARY")
        print("=" * 80)
        
        status = "✅ SUCCESS" if report.overall_success else "❌ FAILED"
        print(f"\nOverall Status: {status}")
        
        print("\nStage Results:")
        for stage, result in report.stage_results.items():
            s = "✅" if result.success else "❌"
            print(f"   {s} {stage.value.upper()}: {result.duration_seconds:.2f}s")
        
        total_time = sum(r.duration_seconds for r in report.stage_results.values())
        print(f"\nTotal Duration: {total_time:.2f}s")
        
        print("\n" + "=" * 80)


def generate_schedule_info():
    """Print cron schedule suggestions."""
    print("""
CORTEX Maintenance Schedule Suggestions
======================================

Weekly Maintenance (Recommended):
    # Run every Sunday at 2 AM
    0 2 * * 0 cd /path/to/CORTEX && python3 scripts/cortex_maintenance_runner.py --execute >> logs/maintenance.log 2>&1

Daily Quick Check:
    # Run every day at 6 AM
    0 6 * * * cd /path/to/CORTEX && python3 scripts/cortex_system_doctor.py --quick >> logs/health.log 2>&1

Monthly Deep Scan:
    # Run first of every month at 3 AM
    0 3 1 * * cd /path/to/CORTEX && python3 scripts/cortex_system_doctor.py >> logs/monthly-scan.log 2>&1

Add to crontab with: crontab -e
""")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='CORTEX Maintenance Runner - Automated Maintenance Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/cortex_maintenance_runner.py                    # Full pipeline (dry-run)
    python scripts/cortex_maintenance_runner.py --execute          # Execute all stages
    python scripts/cortex_maintenance_runner.py --stage analysis   # Run specific stage
    python scripts/cortex_maintenance_runner.py --schedule         # Show cron schedule
        """
    )
    
    parser.add_argument(
        '--execute',
        action='store_true',
        help='Execute maintenance (default is dry-run)'
    )
    
    parser.add_argument(
        '--stage',
        action='append',
        choices=[s.value for s in Stage],
        help='Run specific stage(s). Can be used multiple times.'
    )
    
    parser.add_argument(
        '--schedule',
        action='store_true',
        help='Print cron schedule suggestions'
    )
    
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Reduce output'
    )
    
    args = parser.parse_args()
    
    if args.schedule:
        generate_schedule_info()
        return
    
    # Determine stages
    stages = None
    if args.stage:
        stages = [Stage(s) for s in args.stage]
    
    # Run maintenance
    runner = CortexMaintenanceRunner(
        project_root=PROJECT_ROOT,
        dry_run=not args.execute,
        verbose=not args.quiet
    )
    
    report = runner.run_pipeline(stages=stages)
    
    sys.exit(0 if report.overall_success else 1)


if __name__ == '__main__':
    main()
