#!/usr/bin/env python3
"""
CORTEX Vacuum CLI

User-friendly command-line interface for repository reorganization.

Usage:
    python run-cortex-vacuum.py analyze [--output-dir DIR]
    python run-cortex-vacuum.py execute --plan FILE [--dry-run] [--auto-approve]
    python run-cortex-vacuum.py verify [--fail-on-violations]
    python run-cortex-vacuum.py rollback --snapshot FILE

Author: Asif Hussain
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Optional


def find_repo_root() -> Path:
    """Find CORTEX repository root."""
    current = Path.cwd()
    while current != current.parent:
        if (current / 'cortex_brain').exists() and (current / 'src').exists():
            return current
        current = current.parent
    
    # Try starting from this script's location
    current = Path(__file__).parent.parent
    while current != current.parent:
        if (current / 'cortex_brain').exists() and (current / 'src').exists():
            return current
        current = current.parent
    
    raise RuntimeError("Could not find CORTEX repository root. Please run from within CORTEX project.")


# Add repository root to path for imports
_repo_root = find_repo_root()
sys.path.insert(0, str(_repo_root))

from cortex.brain.mcp.tools.cortex_vacuum_analyzer import CortexVacuumAnalyzer
from cortex.brain.mcp.tools.cortex_vacuum_executor import CortexVacuumExecutor


def cmd_analyze(args) -> int:
    """Execute analysis command."""
    repo_root = Path(args.repo_root) if args.repo_root else find_repo_root()
    output_dir = args.output_dir or (repo_root / 'cortex_brain' / 'vacuum')
    
    print(f"🔍 CORTEX Vacuum Analysis")
    print(f"   Repository: {repo_root}")
    print(f"   Output: {output_dir}")
    
    try:
        analyzer = CortexVacuumAnalyzer(str(repo_root))
        report = analyzer.analyze()
        
        # Save outputs
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        with open(output_path / 'analysis-report.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        with open(output_path / 'migration-plan.json', 'w') as f:
            json.dump({
                'timestamp': report['timestamp'],
                'plans': report['migration_plans']
            }, f, indent=2, default=str)
        
        with open(output_path / 'reference-map.json', 'w') as f:
            json.dump({
                'timestamp': report['timestamp'],
                'references': report['references']
            }, f, indent=2, default=str)
        
        # Print summary
        print(f"\n✓ Analysis Complete")
        print(f"\n📊 Summary:")
        print(f"   Files scanned: {report['summary']['total_files']}")
        print(f"   Issues found: {report['summary']['issues_found']}")
        print(f"   Cross-references: {report['summary']['references_found']}")
        print(f"   Files to delete: {report['summary']['files_to_delete']}")
        print(f"   Files to move: {report['summary']['files_to_move']}")
        print(f"   Files to rename: {report['summary']['files_to_rename']}")
        
        if report['summary']['issues_found'] > 0:
            print(f"\n⚠️  Issues found - review detailed report")
            top_issues = report['issues'][:5]
            for issue in top_issues:
                print(f"   - [{issue['severity']}] {issue['file_path']}: {issue['description']}")
        
        print(f"\n📁 Reports saved to: {output_path}")
        print(f"   - analysis-report.json (detailed)")
        print(f"   - migration-plan.json (for execution)")
        print(f"   - reference-map.json (cross-references)")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ Analysis failed: {e}")
        return 1


def cmd_execute(args) -> int:
    """Execute migration command."""
    repo_root = Path(args.repo_root) if args.repo_root else find_repo_root()
    plan_file = Path(args.plan)
    
    if not plan_file.exists():
        print(f"✗ Migration plan not found: {plan_file}")
        return 1
    
    print(f"🚀 CORTEX Vacuum Execution")
    print(f"   Repository: {repo_root}")
    print(f"   Plan: {plan_file}")
    print(f"   Mode: {'DRY RUN' if args.dry_run else 'LIVE EXECUTION'}")
    
    try:
        with open(plan_file, 'r') as f:
            plan = json.load(f)
        
        executor = CortexVacuumExecutor(str(repo_root), plan, dry_run=args.dry_run)
        report = executor.execute(auto_approve=args.auto_approve)
        
        # Save execution report
        output_dir = plan_file.parent
        report_path = output_dir / 'execution-report.json'
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        # Print results
        if report['success']:
            print(f"\n✓ Execution Successful!")
        else:
            print(f"\n⚠️  Execution Completed with Issues")
        
        verification = report.get('verification', {})
        print(f"\n📊 Results:")
        print(f"   Operations: {verification.get('successful_operations', 0)} successful")
        if verification.get('failed_operations', 0) > 0:
            print(f"              {verification.get('failed_operations', 0)} failed")
        print(f"   References updated: {verification.get('references_updated', 0)}")
        
        print(f"\n📁 Report saved to: {report_path}")
        
        return 0 if report['success'] else 1
        
    except Exception as e:
        print(f"\n✗ Execution failed: {e}")
        return 1


def cmd_verify(args) -> int:
    """Execute verification command."""
    repo_root = Path(args.repo_root) if args.repo_root else find_repo_root()
    
    print(f"🔐 CORTEX Vacuum Verification")
    print(f"   Repository: {repo_root}")
    
    try:
        analyzer = CortexVacuumAnalyzer(str(repo_root))
        analyzer._scan_repository()
        analyzer._identify_file_issues()
        
        issues = analyzer.issues
        print(f"\n✓ Verification Complete")
        
        if not issues:
            print(f"\n✅ Repository is compliant!")
            return 0
        else:
            print(f"\n⚠️  Found {len(issues)} compliance issues:")
            
            # Group by severity
            by_severity = {}
            for issue in issues:
                severity = issue.severity
                if severity not in by_severity:
                    by_severity[severity] = []
                by_severity[severity].append(issue)
            
            for severity in ['error', 'warning', 'info']:
                if severity in by_severity:
                    print(f"\n   [{severity.upper()}] {len(by_severity[severity])} issues")
                    for issue in by_severity[severity][:5]:
                        print(f"      - {issue.file_path}")
                        print(f"        {issue.description}")
                    
                    if len(by_severity[severity]) > 5:
                        print(f"      ... and {len(by_severity[severity]) - 5} more")
            
            if args.fail_on_violations:
                return 1
            return 0
        
    except Exception as e:
        print(f"\n✗ Verification failed: {e}")
        return 1


def cmd_rollback(args) -> int:
    """Execute rollback command."""
    snapshot_file = Path(args.snapshot)
    
    if not snapshot_file.exists():
        print(f"✗ Snapshot not found: {snapshot_file}")
        return 1
    
    print(f"⏮️  CORTEX Vacuum Rollback")
    print(f"   Snapshot: {snapshot_file}")
    print(f"\n⚠️  Rollback not yet implemented in this version")
    print(f"   Please use: git checkout <commit> to restore")
    
    return 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='CORTEX Vacuum - Repository Reorganization Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze repository without making changes
  python run-cortex-vacuum.py analyze --output-dir cortex_brain/vacuum/
  
  # Review the analysis report, then execute
  cat cortex_brain/vacuum/analysis-report.json
  python run-cortex-vacuum.py execute --plan cortex_brain/vacuum/migration-plan.json --dry-run
  
  # Execute after review (no more confirmation prompts with --auto-approve)
  python run-cortex-vacuum.py execute --plan cortex_brain/vacuum/migration-plan.json --auto-approve
  
  # Verify compliance
  python run-cortex-vacuum.py verify --fail-on-violations
"""
    )
    
    parser.add_argument('--repo-root', type=str, help='Repository root (auto-detected if not specified)')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze repository structure')
    analyze_parser.add_argument('--output-dir', type=str, help='Output directory for analysis results')
    analyze_parser.set_defaults(func=cmd_analyze)
    
    # Execute command
    execute_parser = subparsers.add_parser('execute', help='Execute migration plan')
    execute_parser.add_argument('--plan', required=True, help='Path to migration plan JSON file')
    execute_parser.add_argument('--dry-run', action='store_true', help='Simulate without making changes')
    execute_parser.add_argument('--auto-approve', action='store_true', help='Skip confirmation prompt')
    execute_parser.set_defaults(func=cmd_execute)
    
    # Verify command
    verify_parser = subparsers.add_parser('verify', help='Verify repository compliance')
    verify_parser.add_argument('--fail-on-violations', action='store_true', help='Exit with error code if violations found')
    verify_parser.set_defaults(func=cmd_verify)
    
    # Rollback command
    rollback_parser = subparsers.add_parser('rollback', help='Rollback to previous state')
    rollback_parser.add_argument('--snapshot', required=True, help='Path to snapshot file')
    rollback_parser.set_defaults(func=cmd_rollback)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
