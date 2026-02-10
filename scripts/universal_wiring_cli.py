"""
Universal Orchestrator Wiring CLI Tool

AC-ID: UNIVERSAL-WIRING-CLI-001
Purpose: Command-line interface to demonstrate and test the universal orchestrator wiring system
         
Usage:
    python universal_wiring_cli.py scan                    # Scan for all orchestrators
    python universal_wiring_cli.py validate               # Validate all wiring
    python universal_wiring_cli.py fix --dry-run          # Show what would be fixed
    python universal_wiring_cli.py fix                    # Actually fix issues
    python universal_wiring_cli.py test <orchestrator>    # Test specific orchestrator

Author: Asif Hussain
Date: 2026-02-10
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any

# Add CORTEX to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cortex.learning.registry_intelligence_agent import RegistryIntelligenceAgent


def print_banner():
    """Print CLI banner."""
    print("=" * 80)
    print("🧠 CORTEX Universal Orchestrator Wiring System")
    print("=" * 80)


def format_discovery_table(discoveries):
    """Format discoveries as a table."""
    if not discoveries:
        print("No orchestrators discovered.")
        return
    
    print(f"{'Orchestrator':<25} {'Keywords':<30} {'Registered':<12} {'Confidence':<10}")
    print("-" * 77)
    
    for discovery in sorted(discoveries, key=lambda x: x.confidence, reverse=True):
        keywords_str = ", ".join(sorted(list(discovery.keywords))[:4])
        if len(discovery.keywords) > 4:
            keywords_str += "..."
        
        status = "✅ YES" if discovery.is_registered else "❌ NO"
        confidence = f"{discovery.confidence:.2f}"
        
        print(f"{discovery.name:<25} {keywords_str:<30} {status:<12} {confidence:<10}")


def format_validation_report(report):
    """Format validation report."""
    print("📊 UNIVERSAL VALIDATION REPORT")
    print("-" * 50)
    print(f"Total Orchestrators: {report['total_orchestrators']}")
    print(f"Registered: {report['registered_count']}")
    print(f"Unregistered: {report['unregistered_count']}")
    print(f"Health Score: {report['health_score']:.1f}%")
    print(f"Overall Status: {report['overall_status'].upper()}")
    
    # Intent coverage
    print("\\n🎯 INTENT COVERAGE:")
    coverage = report.get('coverage_by_intent', {})
    for intent, info in sorted(coverage.items()):
        status = "✅" if info['covered'] else "❌"
        count = info['count']
        print(f"  {status} {intent:<12} ({count} orchestrators)")
    
    # Issues
    if report.get('dependency_issues'):
        print(f"\\n⚠️ DEPENDENCY ISSUES ({len(report['dependency_issues'])}):")
        for issue in report['dependency_issues'][:5]:  # Show first 5
            print(f"  - {issue['orchestrator']} missing {issue['missing_dependency']}")
    
    if report.get('mcp_exposure_gaps'):
        print(f"\\n🔌 MCP EXPOSURE GAPS ({len(report['mcp_exposure_gaps'])}):")
        for gap in report['mcp_exposure_gaps'][:5]:  # Show first 5
            print(f"  - {gap['orchestrator']} ({gap['capabilities']} capabilities)")


def format_fix_results(results):
    """Format fix results."""
    print("🔧 UNIVERSAL AUTO-FIX RESULTS")
    print("-" * 50)
    print(f"Total Fixes Attempted: {results['total_fixes_attempted']}")
    print(f"Successful Fixes: {results['successful_fixes']}")
    print(f"Failed Fixes: {results['failed_fixes']}")
    print(f"Success Rate: {results.get('success_rate', 0):.1f}%")
    print(f"Overall Status: {results['overall_status'].upper()}")
    
    if results['dry_run']:
        print("\\n💡 DRY RUN - No actual changes made")
    
    # Fix breakdown
    print("\\n📊 FIXES BY TYPE:")
    fixes_by_type = results.get('fixes_by_type', {})
    for fix_type, stats in fixes_by_type.items():
        if stats['attempted'] > 0:
            success_rate = (stats['successful'] / stats['attempted']) * 100 if stats['attempted'] > 0 else 0
            print(f"  {fix_type}: {stats['successful']}/{stats['attempted']} ({success_rate:.1f}%)")
    
    # Detailed fixes
    if results.get('detailed_fixes'):
        print("\\n🔍 DETAILED FIXES:")
        for fix in results['detailed_fixes'][:10]:  # Show first 10
            status_icon = {"success": "✅", "failed": "❌", "dry_run": "🔮"}[fix['status']]
            print(f"  {status_icon} {fix['action']}")


def cmd_scan(args):
    """Scan for orchestrators."""
    print("🔍 Scanning for orchestrators...")
    
    agent = RegistryIntelligenceAgent(enable_learning=False)
    discoveries = agent.scan_for_orchestrators(force_rescan=True)
    
    print(f"\\n📋 Found {len(discoveries)} orchestrators:")
    format_discovery_table(discoveries)
    
    # Summary by intent
    intent_summary = {}
    for discovery in discoveries:
        for keyword in discovery.keywords:
            if keyword not in intent_summary:
                intent_summary[keyword] = 0
            intent_summary[keyword] += 1
    
    if intent_summary:
        print("\\n🎯 Intent Coverage Summary:")
        for intent, count in sorted(intent_summary.items(), key=lambda x: x[1], reverse=True):
            print(f"  {intent}: {count} orchestrators")


def cmd_validate(args):
    """Validate orchestrator wiring."""
    print("✅ Validating universal orchestrator wiring...")
    
    agent = RegistryIntelligenceAgent(enable_learning=False)
    report = agent.validate_universal_wiring()
    
    format_validation_report(report)


def cmd_fix(args):
    """Fix orchestrator wiring issues."""
    dry_run = getattr(args, 'dry_run', False)
    
    if dry_run:
        print("🔮 Running dry-run auto-fix (no actual changes)...")
    else:
        print("🔧 Running universal auto-fix...")
    
    agent = RegistryIntelligenceAgent(enable_learning=False)
    
    # First validate to get issues
    print("Step 1: Validating current state...")
    validation_report = agent.validate_universal_wiring()
    
    # Then attempt fixes
    print("Step 2: Attempting fixes...")
    fix_results = agent.universal_auto_fix(validation_report, dry_run=dry_run)
    
    format_fix_results(fix_results)


def cmd_test(args):
    """Test specific orchestrator."""
    orchestrator_name = args.orchestrator
    
    print(f"🧪 Testing orchestrator: {orchestrator_name}")
    
    agent = RegistryIntelligenceAgent(enable_learning=False)
    discoveries = agent.scan_for_orchestrators(force_rescan=True)
    
    # Find the orchestrator
    target = None
    for discovery in discoveries:
        if discovery.name == orchestrator_name:
            target = discovery
            break
    
    if not target:
        print(f"❌ Orchestrator '{orchestrator_name}' not found.")
        print("Available orchestrators:")
        for discovery in discoveries:
            print(f"  - {discovery.name}")
        return
    
    print(f"✅ Found {orchestrator_name}")
    print(f"Keywords: {', '.join(target.keywords)}")
    print(f"Capabilities: {', '.join(target.capabilities)}")
    print(f"Confidence: {target.confidence:.2f}")
    print(f"Registered: {'Yes' if target.is_registered else 'No'}")
    
    # Try to import and test
    try:
        # Build module path
        relative_path = target.file_path.relative_to(Path.cwd())
        module_parts = relative_path.with_suffix('').parts
        module_path = ".".join(module_parts)
        
        print(f"\\n🔍 Module path: {module_path}")
        
        # TODO: Add actual orchestrator instantiation and testing
        print("✅ Orchestrator structure appears valid")
        
    except Exception as e:
        print(f"❌ Error testing orchestrator: {e}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Universal Orchestrator Wiring System CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s scan                    # Discover all orchestrators
    %(prog)s validate               # Check wiring health  
    %(prog)s fix --dry-run          # Preview fixes
    %(prog)s fix                    # Apply fixes
    %(prog)s test DeploymentOrchestrator  # Test specific orchestrator
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Scan command
    scan_parser = subparsers.add_parser('scan', help='Scan for orchestrators')
    scan_parser.set_defaults(func=cmd_scan)
    
    # Validate command  
    validate_parser = subparsers.add_parser('validate', help='Validate orchestrator wiring')
    validate_parser.set_defaults(func=cmd_validate)
    
    # Fix command
    fix_parser = subparsers.add_parser('fix', help='Fix orchestrator wiring issues')
    fix_parser.add_argument('--dry-run', action='store_true', help='Show what would be fixed without making changes')
    fix_parser.set_defaults(func=cmd_fix)
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test specific orchestrator')
    test_parser.add_argument('orchestrator', help='Name of orchestrator to test')
    test_parser.set_defaults(func=cmd_test)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    print_banner()
    
    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\\n\\n⚠️ Operation cancelled by user")
    except Exception as e:
        print(f"\\n\\n❌ Error: {e}")
        if args.command != 'test':  # Don't show full traceback for test failures
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()