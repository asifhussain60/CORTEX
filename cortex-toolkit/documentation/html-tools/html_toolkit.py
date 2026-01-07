#!/usr/bin/env python3
"""
CORTEX HTML Toolkit CLI
Command-line interface for HTML validation and generation

Usage:
    python html_toolkit.py validate <file_or_dir> [--strict]
    python html_toolkit.py generate <output_file> --title "Page Title"
    python html_toolkit.py check <directory> --exclude "pattern"

Author: Asif Hussain
Date: December 27, 2025
"""

import argparse
import sys
from pathlib import Path

try:
    from validator import validate_file, validate_directory, print_validation_report
    from generator import HTMLGenerator, h1, h2, p, ul, div
except ImportError:
    # If running from different location
    import os
    sys.path.insert(0, os.path.dirname(__file__))
    from validator import validate_file, validate_directory, print_validation_report
    from generator import HTMLGenerator, h1, h2, p, ul, div


def cmd_validate(args):
    """Validate HTML file(s)"""
    path = Path(args.path)
    
    if not path.exists():
        print(f"❌ Error: Path not found: {path}")
        return 1
    
    if path.is_file():
        print(f"Validating file: {path}\n")
        result = validate_file(path, strict=args.strict)
        success = print_validation_report({path.name: result})
        return 0 if success else 1
    
    elif path.is_dir():
        print(f"Validating directory: {path}\n")
        exclude = args.exclude.split(',') if args.exclude else []
        results = validate_directory(
            path,
            pattern=args.pattern,
            exclude=exclude,
            strict=args.strict
        )
        success = print_validation_report(results)
        return 0 if success else 1
    
    else:
        print(f"❌ Error: Invalid path: {path}")
        return 1


def cmd_generate(args):
    """Generate HTML document"""
    output_path = Path(args.output)
    
    print(f"Generating HTML document: {output_path}")
    
    # Create document
    doc = HTMLGenerator(title=args.title, lang=args.lang)
    
    # Add meta tags
    if args.description:
        doc.add_meta("description", args.description)
    
    doc.add_meta("author", args.author)
    doc.add_meta("generator", "CORTEX HTML Toolkit")
    
    # Add stylesheets
    if args.css:
        for stylesheet in args.css.split(','):
            doc.add_stylesheet(stylesheet.strip())
    
    # Add scripts
    if args.js:
        for script in args.js.split(','):
            doc.add_script(script.strip(), defer=True)
    
    # Add default content
    header = div(class_name="header")
    header.add_child(h1(args.title))
    
    if args.description:
        header.add_child(p(args.description))
    
    doc.add_to_body(header)
    
    # Add template content
    if args.template == "documentation":
        content = div(class_name="content")
        content.add_child(h2("Overview"))
        content.add_child(p("Document overview goes here."))
        
        content.add_child(h2("Features"))
        content.add_child(ul([
            "Feature 1",
            "Feature 2",
            "Feature 3"
        ]))
        
        doc.add_to_body(content)
    
    # Save document
    try:
        doc.save(output_path)
        print(f"✅ Document created successfully: {output_path}")
        
        # Validate generated document
        result = validate_file(output_path, strict=False)
        if result['valid']:
            print("✅ Generated HTML is valid")
        else:
            print("⚠️  Generated HTML has validation issues:")
            for error in result['errors']:
                print(f"    {error}")
        
        return 0
    
    except Exception as e:
        print(f"❌ Error creating document: {e}")
        return 1


def cmd_check(args):
    """Quick validation check with summary"""
    path = Path(args.path)
    
    if not path.exists():
        print(f"❌ Error: Path not found: {path}")
        return 1
    
    if path.is_file():
        result = validate_file(path, strict=args.strict)
        
        print(f"\n{'='*60}")
        print(f"File: {path.name}")
        print(f"{'='*60}")
        
        if result['valid']:
            print("✅ VALID")
        else:
            print("❌ INVALID")
            print(f"\nErrors: {len(result['errors'])}")
            for error in result['errors'][:5]:  # Show first 5
                print(f"  • {error}")
            if len(result['errors']) > 5:
                print(f"  ... and {len(result['errors']) - 5} more")
        
        if result['warnings']:
            print(f"\nWarnings: {len(result['warnings'])}")
            for warning in result['warnings'][:3]:
                print(f"  • {warning}")
        
        return 0 if result['valid'] else 1
    
    elif path.is_dir():
        exclude = args.exclude.split(',') if args.exclude else []
        results = validate_directory(path, exclude=exclude, strict=args.strict)
        
        valid = sum(1 for r in results.values() if r['valid'])
        invalid = len(results) - valid
        
        print(f"\n{'='*60}")
        print(f"Directory: {path}")
        print(f"{'='*60}")
        print(f"Total files: {len(results)}")
        print(f"✅ Valid: {valid}")
        print(f"❌ Invalid: {invalid}")
        
        if invalid > 0:
            print(f"\nInvalid files:")
            for file_path, result in results.items():
                if not result['valid']:
                    print(f"  • {file_path} ({len(result['errors'])} errors)")
        
        return 0 if invalid == 0 else 1


def main():
    parser = argparse.ArgumentParser(
        description="CORTEX HTML Toolkit - Native Python HTML validation and generation",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Validate command
    validate_parser = subparsers.add_parser(
        'validate',
        help='Validate HTML file(s) with detailed report'
    )
    validate_parser.add_argument('path', help='File or directory to validate')
    validate_parser.add_argument(
        '--strict',
        action='store_true',
        help='Enable strict validation (DOCTYPE, required elements)'
    )
    validate_parser.add_argument(
        '--pattern',
        default='**/*.html',
        help='Glob pattern for files (default: **/*.html)'
    )
    validate_parser.add_argument(
        '--exclude',
        help='Comma-separated patterns to exclude'
    )
    
    # Generate command
    generate_parser = subparsers.add_parser(
        'generate',
        help='Generate HTML document'
    )
    generate_parser.add_argument('output', help='Output file path')
    generate_parser.add_argument(
        '--title',
        default='Document',
        help='Document title'
    )
    generate_parser.add_argument(
        '--description',
        help='Meta description'
    )
    generate_parser.add_argument(
        '--author',
        default='CORTEX',
        help='Document author'
    )
    generate_parser.add_argument(
        '--lang',
        default='en',
        help='Document language (default: en)'
    )
    generate_parser.add_argument(
        '--css',
        help='Comma-separated stylesheet paths'
    )
    generate_parser.add_argument(
        '--js',
        help='Comma-separated script paths'
    )
    generate_parser.add_argument(
        '--template',
        choices=['basic', 'documentation'],
        default='basic',
        help='Document template'
    )
    
    # Check command
    check_parser = subparsers.add_parser(
        'check',
        help='Quick validation check with summary'
    )
    check_parser.add_argument('path', help='File or directory to check')
    check_parser.add_argument(
        '--strict',
        action='store_true',
        help='Enable strict validation'
    )
    check_parser.add_argument(
        '--exclude',
        help='Comma-separated patterns to exclude'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Execute command
    if args.command == 'validate':
        return cmd_validate(args)
    elif args.command == 'generate':
        return cmd_generate(args)
    elif args.command == 'check':
        return cmd_check(args)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
