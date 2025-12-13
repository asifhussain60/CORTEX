"""
CORTEX Lens Command-Line Interface

Entry point for CLI usage of CORTEX Lens.
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import List, Optional

from . import CortexLens, __version__


def setup_logging(verbose: bool = False):
    """Configure logging"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(message)s',
        handlers=[logging.StreamHandler()]
    )


def cmd_analyze(args):
    """Handle 'analyze' command"""
    lens = CortexLens()
    
    result = lens.analyze(
        repo_path=args.repo_path,
        output_dir=args.output,
        template=args.template,
        export_formats=args.format
    )
    
    print(f"\n✅ Analysis Complete!")
    print(f"📊 Dashboard: {result['dashboard_path']}")
    print(f"📦 Package: {result['package_path']}")
    
    if result.get('export_paths'):
        print(f"\n📄 Exports:")
        for format_type, path in result['export_paths'].items():
            print(f"  - {format_type.upper()}: {path}")
    
    metrics = result.get('metrics', {})
    print(f"\n📈 Metrics:")
    print(f"  - Duration: {metrics.get('duration_seconds', 0):.2f}s")
    print(f"  - Files: {metrics.get('total_files', 0)}")
    print(f"  - LOC: {metrics.get('total_loc', 0)}")
    
    return 0


def cmd_scan(args):
    """Handle 'scan' command"""
    lens = CortexLens()
    
    classification = lens.scan(args.repo_path)
    
    print(f"\n🔍 Repository Classification")
    print(f"Primary Type: {classification['primary_type']}")
    print(f"Confidence: {classification['confidence_scores'][classification['primary_type']]:.1%}")
    
    if classification['secondary_types']:
        print(f"\nSecondary Types:")
        for repo_type in classification['secondary_types']:
            print(f"  - {repo_type} ({classification['confidence_scores'][repo_type]:.1%})")
    
    print(f"\nDetected Patterns:")
    for pattern, detected in classification['detected_patterns'].items():
        status = "✓" if detected else "✗"
        print(f"  {status} {pattern}")
    
    print(f"\nDashboard Template: {classification['dashboard_template']}")
    
    return 0


def cmd_compare(args):
    """Handle 'compare' command"""
    lens = CortexLens()
    
    result = lens.compare(
        repo_paths=args.repos,
        output_dir=args.output
    )
    
    print(f"\n✅ Comparison Complete!")
    print(f"📊 Comparison Dashboard: {result['comparison_path']}")
    print(f"Repositories Compared: {len(args.repos)}")
    
    return 0


def cmd_templates(args):
    """Handle 'templates' command"""
    templates = [
        ("fullstack_web", "Full-Stack Web Application", "Frontend + Backend + Database"),
        ("api_service", "API Service", "REST/GraphQL endpoints"),
        ("database_project", "Database Project", "Schema, migrations, procedures"),
        ("console_app", "Console Application", "CLI commands, workflows"),
        ("microservices", "Microservices", "Distributed services, messaging"),
        ("library_package", "Library/Package", "Exported APIs, documentation")
    ]
    
    print("\n📋 Available Dashboard Templates\n")
    for template_id, name, description in templates:
        print(f"  {template_id:20s} - {name}")
        print(f"  {' ' * 20}   {description}")
        print()
    
    return 0


def cmd_version(args):
    """Handle 'version' command"""
    print(f"CORTEX Lens v{__version__}")
    print("Universal Repository Intelligence Platform")
    print("Author: Asif Hussain")
    print("Copyright © 2025 Asif Hussain. All rights reserved.")
    return 0


def main(argv: Optional[List[str]] = None):
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog='cortex-lens',
        description='Universal Repository Intelligence Platform',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Analyze command
    analyze_parser = subparsers.add_parser(
        'analyze',
        help='Analyze repository and generate dashboard'
    )
    analyze_parser.add_argument(
        'repo_path',
        help='Path to repository'
    )
    analyze_parser.add_argument(
        '-o', '--output',
        help='Output directory (default: cortex-lens-output/{repo_name})'
    )
    analyze_parser.add_argument(
        '-t', '--template',
        help='Force specific template (default: auto-detect)'
    )
    analyze_parser.add_argument(
        '-f', '--format',
        nargs='+',
        choices=['html', 'json', 'yaml', 'csv', 'all'],
        default=['html'],
        help='Export formats (default: html)'
    )
    analyze_parser.set_defaults(func=cmd_analyze)
    
    # Scan command
    scan_parser = subparsers.add_parser(
        'scan',
        help='Quick scan - classification only'
    )
    scan_parser.add_argument(
        'repo_path',
        help='Path to repository'
    )
    scan_parser.set_defaults(func=cmd_scan)
    
    # Compare command
    compare_parser = subparsers.add_parser(
        'compare',
        help='Compare multiple repositories'
    )
    compare_parser.add_argument(
        'repos',
        nargs='+',
        help='Paths to repositories'
    )
    compare_parser.add_argument(
        '-o', '--output',
        help='Output directory (default: cortex-lens-output/comparison)'
    )
    compare_parser.set_defaults(func=cmd_compare)
    
    # Templates command
    templates_parser = subparsers.add_parser(
        'templates',
        help='List available dashboard templates'
    )
    templates_parser.set_defaults(func=cmd_templates)
    
    # Version command
    version_parser = subparsers.add_parser(
        'version',
        help='Show version information'
    )
    version_parser.set_defaults(func=cmd_version)
    
    # Parse arguments
    args = parser.parse_args(argv)
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Execute command
    if hasattr(args, 'func'):
        try:
            return args.func(args)
        except KeyboardInterrupt:
            print("\n\n⚠️  Operation cancelled by user")
            return 1
        except Exception as e:
            logging.error(f"❌ Error: {e}")
            if args.verbose:
                logging.exception("Full traceback:")
            return 1
    else:
        parser.print_help()
        return 0


if __name__ == '__main__':
    sys.exit(main())
