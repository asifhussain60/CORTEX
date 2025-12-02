#!/usr/bin/env python3
"""
Code Review CLI

User-friendly command-line interface for code review operations.

Version: 3.0.0 (Utility Migration)
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import sys
import json
from pathlib import Path
from typing import Optional

# Import review utility
try:
    from src.operations.modules.review.review_utility import (
        create_review,
        load_review,
        analyze_file,
        generate_report,
        list_reviews,
        ReviewDepth,
        ReviewStatus
    )
except ImportError:
    # Handle direct execution
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    from src.operations.modules.review.review_utility import (
        create_review,
        load_review,
        analyze_file,
        generate_report,
        list_reviews,
        ReviewDepth,
        ReviewStatus
    )


def format_output(result, json_output: bool = False):
    """Format operation result for display."""
    if json_output:
        output = {
            "success": result.success,
            "message": result.message,
            "review_id": result.review_id,
            "errors": result.errors
        }
        print(json.dumps(output, indent=2))
        return
    
    # Text output
    icon = "✅" if result.success else "❌"
    print(f"\n{icon} {result.message}")
    
    if result.review_id:
        print(f"📝 Review ID: {result.review_id}")
    
    if result.session:
        session = result.session
        print(f"📊 Status: {session.status.value.upper()}")
        print(f"🔍 Depth: {session.depth.value.upper()}")
        if session.metrics:
            print(f"⚠️  Risk Score: {session.metrics.risk_score}/100")
            print(f"📁 Files Analyzed: {session.metrics.files_analyzed}")
            print(f"🐛 Total Issues: {len(session.issues)}")
    
    if result.report_path:
        print(f"📄 Report: {result.report_path}")
    
    if result.errors:
        print(f"\n❗ Errors: {', '.join(result.errors)}")


def cmd_create(args):
    """Create new code review."""
    depth = ReviewDepth.STANDARD
    if args.depth:
        depth = ReviewDepth(args.depth.lower())
    
    result = create_review(
        title=args.title,
        description=args.description,
        depth=depth,
        reviewer=args.reviewer or "CORTEX"
    )
    
    format_output(result, args.json)
    return 0 if result.success else 1


def cmd_load(args):
    """Load existing review."""
    result = load_review(args.review_id)
    format_output(result, args.json)
    
    if result.success and not args.json:
        session = result.session
        print(f"\n📋 Review Details:")
        print(f"   Title: {session.title}")
        print(f"   Description: {session.description}")
        print(f"   Reviewer: {session.reviewer}")
        print(f"   Created: {session.created_at}")
        if session.files_reviewed:
            print(f"\n📁 Files Reviewed ({len(session.files_reviewed)}):")
            for file in session.files_reviewed:
                print(f"   - {file}")
    
    return 0 if result.success else 1


def cmd_analyze(args):
    """Analyze file for issues."""
    file_path = Path(args.file)
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return 1
    
    result = analyze_file(args.review_id, file_path)
    format_output(result, args.json)
    
    if result.success and not args.json and result.session:
        # Show issues summary
        issues = result.session.issues
        if issues:
            print(f"\n🐛 Issues Found ({len(issues)}):")
            
            by_severity = {"critical": [], "high": [], "medium": [], "low": []}
            for issue in issues:
                severity = issue.severity.lower()
                if severity in by_severity:
                    by_severity[severity].append(issue)
            
            for severity, icon in [("critical", "🔴"), ("high", "🟠"), ("medium", "🟡"), ("low", "🟢")]:
                if by_severity[severity]:
                    print(f"   {icon} {severity.upper()}: {len(by_severity[severity])}")
    
    return 0 if result.success else 1


def cmd_report(args):
    """Generate review report."""
    result = generate_report(args.review_id)
    format_output(result, args.json)
    
    if result.success and not args.json and result.report_path:
        print(f"\n📖 Report generated at:")
        print(f"   {result.report_path}")
        
        if result.session and result.session.metrics:
            metrics = result.session.metrics
            print(f"\n📊 Report Summary:")
            print(f"   Risk Score: {metrics.risk_score}/100")
            print(f"   🔴 Critical: {metrics.issues_count.get('critical', 0)}")
            print(f"   🟠 High: {metrics.issues_count.get('high', 0)}")
            print(f"   🟡 Medium: {metrics.issues_count.get('medium', 0)}")
            print(f"   🟢 Low: {metrics.issues_count.get('low', 0)}")
    
    return 0 if result.success else 1


def cmd_list(args):
    """List code reviews."""
    status = None
    if args.status:
        status = ReviewStatus(args.status.lower())
    
    result = list_reviews(status)
    format_output(result, args.json)
    
    if result.success and not args.json:
        # Load and display all reviews
        from src.operations.modules.review.review_utility import _get_review_dirs
        
        dirs = _get_review_dirs()
        search_dirs = {}
        
        if status:
            from src.operations.modules.review.review_utility import _get_status_dir
            search_dirs = {status.value: _get_status_dir(status)}
        else:
            search_dirs = {
                "draft": dirs["draft"],
                "in_progress": dirs["in_progress"],
                "completed": dirs["completed"],
                "approved": dirs["approved"]
            }
        
        import yaml
        reviews = []
        for status_name, dir_path in search_dirs.items():
            for yaml_path in dir_path.glob("*.yaml"):
                try:
                    with open(yaml_path, 'r', encoding='utf-8') as f:
                        data = yaml.safe_load(f)
                    reviews.append(data)
                except Exception:
                    pass
        
        if reviews:
            print(f"\n📋 Reviews ({len(reviews)}):\n")
            for data in sorted(reviews, key=lambda x: x.get('updated_at', ''), reverse=True):
                status_icons = {
                    "draft": "📝",
                    "in_progress": "⏳",
                    "completed": "✅",
                    "approved": "🎯"
                }
                icon = status_icons.get(data.get('status', ''), '📄')
                
                print(f"{icon} {data.get('title', 'Untitled')}")
                print(f"   ID: {data.get('review_id', 'unknown')}")
                print(f"   Status: {data.get('status', 'unknown').upper()}")
                print(f"   Updated: {data.get('updated_at', 'unknown')}")
                print()
        else:
            print("\n📋 No reviews found")
    
    return 0 if result.success else 1


def main():
    """Main CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Code Review CLI - Fast, lightweight code review operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s create "Feature Review" "Review new authentication feature" --depth standard
  %(prog)s analyze review-20240101 src/main.py
  %(prog)s report review-20240101
  %(prog)s list --status draft
        """
    )
    
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Create command
    parser_create = subparsers.add_parser('create', help='Create new code review')
    parser_create.add_argument('title', help='Review title')
    parser_create.add_argument('description', help='Review description')
    parser_create.add_argument('--depth', choices=['quick', 'standard', 'deep'],
                               help='Analysis depth (default: standard)')
    parser_create.add_argument('--reviewer', help='Reviewer name (default: CORTEX)')
    
    # Load command
    parser_load = subparsers.add_parser('load', help='Load existing review')
    parser_load.add_argument('review_id', help='Review ID')
    
    # Analyze command
    parser_analyze = subparsers.add_parser('analyze', help='Analyze file')
    parser_analyze.add_argument('review_id', help='Review ID')
    parser_analyze.add_argument('file', help='File to analyze')
    
    # Report command
    parser_report = subparsers.add_parser('report', help='Generate review report')
    parser_report.add_argument('review_id', help='Review ID')
    
    # List command
    parser_list = subparsers.add_parser('list', help='List code reviews')
    parser_list.add_argument('--status', choices=['draft', 'in_progress', 'completed', 'approved'],
                             help='Filter by status')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Execute command
    commands = {
        'create': cmd_create,
        'load': cmd_load,
        'analyze': cmd_analyze,
        'report': cmd_report,
        'list': cmd_list
    }
    
    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
