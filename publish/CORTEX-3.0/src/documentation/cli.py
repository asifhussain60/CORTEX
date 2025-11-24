"""CLI entry point for CORTEX documentation generation"""

import argparse
import sys
import json
from pathlib import Path
from datetime import datetime

from src.documentation import DocumentationOrchestrator, CapabilityScanner


def cmd_generate(args):
    """Generate documentation"""
    print(f"🧠 CORTEX Documentation Generator")
    print(f"{'='*60}")
    print(f"Workspace: {args.workspace}")
    print(f"Output: {args.output}")
    print(f"Parallel: {'Yes' if args.parallel else 'No'}")
    print(f"{'='*60}\n")
    
    # Initialize orchestrator
    orchestrator = DocumentationOrchestrator(
        workspace_root=args.workspace,
        output_dir=args.output
    )
    
    # Generate all documentation
    print("📝 Starting documentation generation...\n")
    start_time = datetime.now()
    
    try:
        report = orchestrator.generate_all(parallel=args.parallel)
        
        duration = datetime.now() - start_time
        
        # Display summary
        print(f"\n{'='*60}")
        print(f"✅ Generation Complete!")
        print(f"{'='*60}")
        print(f"Duration: {duration.total_seconds():.2f} seconds")
        print(f"Components: {len(report['results'])}")
        
        # Count successes/failures
        successes = sum(1 for r in report['results'].values() if r['status'] == 'success')
        failures = sum(1 for r in report['results'].values() if r['status'] == 'failed')
        
        print(f"✅ Successful: {successes}")
        if failures > 0:
            print(f"❌ Failed: {failures}")
        
        # Save report
        report_path = Path(args.output) / 'generation-report.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n📊 Report saved: {report_path}")
        
        # Show failures
        if failures > 0:
            print(f"\n❌ Failed Components:")
            for name, result in report['results'].items():
                if result['status'] == 'failed':
                    print(f"  • {name}: {result.get('error', 'Unknown error')}")
            return 1
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Generation failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


def cmd_scan(args):
    """Scan workspace for capabilities"""
    print(f"🔍 Scanning workspace: {args.workspace}")
    
    scanner = CapabilityScanner(args.workspace)
    capabilities = scanner.scan_all()
    
    print(f"\n✅ Found {len(capabilities)} capabilities:")
    
    # Group by type
    by_type = {}
    for cap_id, cap in scanner.capabilities.items():
        cap_type = cap.type
        if cap_type not in by_type:
            by_type[cap_type] = []
        by_type[cap_type].append(cap)
    
    for cap_type, caps in sorted(by_type.items()):
        print(f"\n{cap_type.upper()} ({len(caps)}):")
        for cap in caps[:10]:  # Show first 10
            status_emoji = '✅' if cap.status in ['active', 'implemented'] else '⏳'
            print(f"  {status_emoji} {cap.name} - {cap.description}")
        
        if len(caps) > 10:
            print(f"  ... and {len(caps) - 10} more")
    
    # Export registry
    if args.output:
        output_path = Path(args.output)
        scanner.export_registry(str(output_path))
        print(f"\n📊 Registry exported: {output_path}")
    
    return 0


def cmd_validate(args):
    """Validate generated documentation"""
    print(f"✅ Validating documentation: {args.docs_dir}")
    
    docs_dir = Path(args.docs_dir)
    if not docs_dir.exists():
        print(f"❌ Documentation directory not found: {docs_dir}")
        return 1
    
    # Check required files
    required_files = [
        'index.md',
        'EXECUTIVE-SUMMARY.md',
        'CAPABILITIES-MATRIX.md',
        'THE-AWAKENING-OF-CORTEX.md'
    ]
    
    missing = []
    found = []
    
    for file in required_files:
        file_path = docs_dir / file
        if file_path.exists():
            found.append(file)
            size = file_path.stat().st_size
            print(f"  ✅ {file} ({size:,} bytes)")
        else:
            missing.append(file)
            print(f"  ❌ {file} (missing)")
    
    # Check ChatGPT prompts
    prompts_dir = docs_dir / 'chatgpt-prompts'
    if prompts_dir.exists():
        prompt_count = len(list(prompts_dir.glob('*.md')))
        print(f"\n  ✅ ChatGPT prompts: {prompt_count} files")
    
    # Check Mermaid diagrams
    diagrams_dir = docs_dir / 'mermaid'
    if diagrams_dir.exists():
        diagram_count = len(list(diagrams_dir.rglob('*.mmd')))
        print(f"  ✅ Mermaid diagrams: {diagram_count} files")
    
    print(f"\n{'='*60}")
    if not missing:
        print(f"✅ All required files present ({len(found)}/{len(required_files)})")
        return 0
    else:
        print(f"❌ Missing {len(missing)} required files")
        return 1


def cmd_report(args):
    """Show generation report"""
    report_path = Path(args.report)
    
    if not report_path.exists():
        print(f"❌ Report not found: {report_path}")
        return 1
    
    with open(report_path, 'r', encoding='utf-8') as f:
        report = json.load(f)
    
    print(f"📊 Documentation Generation Report")
    print(f"{'='*60}")
    print(f"Started: {report.get('started_at', 'Unknown')}")
    print(f"Completed: {report.get('completed_at', 'Unknown')}")
    print(f"Duration: {report.get('duration_seconds', 0):.2f} seconds")
    print(f"{'='*60}\n")
    
    results = report.get('results', {})
    successes = [k for k, v in results.items() if v['status'] == 'success']
    failures = [k for k, v in results.items() if v['status'] == 'failed']
    
    print(f"✅ Successful: {len(successes)}")
    print(f"❌ Failed: {len(failures)}")
    
    if failures:
        print(f"\n❌ Failed Components:")
        for name in failures:
            error = results[name].get('error', 'Unknown')
            print(f"  • {name}: {error}")
    
    if args.verbose:
        print(f"\n✅ Successful Components:")
        for name in successes[:20]:  # Show first 20
            output = results[name].get('output', '')
            print(f"  • {name}")
            if output:
                print(f"    Output: {output}")
        
        if len(successes) > 20:
            print(f"  ... and {len(successes) - 20} more")
    
    return 0


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='CORTEX Documentation Generation System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate all documentation
  python -m src.documentation.cli generate
  
  # Generate with custom output directory
  python -m src.documentation.cli generate --output docs/generated
  
  # Scan workspace for capabilities
  python -m src.documentation.cli scan
  
  # Validate generated documentation
  python -m src.documentation.cli validate --docs-dir docs
  
  # Show generation report
  python -m src.documentation.cli report --report docs/generation-report.json
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Generate command
    generate_parser = subparsers.add_parser('generate', help='Generate all documentation')
    generate_parser.add_argument(
        '--workspace',
        default='.',
        help='Workspace root directory (default: current directory)'
    )
    generate_parser.add_argument(
        '--output',
        default='docs',
        help='Output directory (default: docs)'
    )
    generate_parser.add_argument(
        '--parallel',
        action='store_true',
        help='Enable parallel generation'
    )
    generate_parser.set_defaults(func=cmd_generate)
    
    # Scan command
    scan_parser = subparsers.add_parser('scan', help='Scan workspace for capabilities')
    scan_parser.add_argument(
        '--workspace',
        default='.',
        help='Workspace root directory (default: current directory)'
    )
    scan_parser.add_argument(
        '--output',
        help='Export registry to file (optional)'
    )
    scan_parser.set_defaults(func=cmd_scan)
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate generated documentation')
    validate_parser.add_argument(
        '--docs-dir',
        default='docs',
        help='Documentation directory (default: docs)'
    )
    validate_parser.set_defaults(func=cmd_validate)
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Show generation report')
    report_parser.add_argument(
        '--report',
        default='docs/generation-report.json',
        help='Report file path (default: docs/generation-report.json)'
    )
    report_parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed information'
    )
    report_parser.set_defaults(func=cmd_report)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Execute command
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
